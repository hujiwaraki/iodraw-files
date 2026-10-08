"""终章 · 此心安处 —— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。

她回到房间，照片越拍越多，心情却留不住了；唯有创造才能永恒。笔尖落在空白的书页上，
镜头钻进纸里：高原（垒石头、建立秩序）→ 平原（踏脚石、身边的一小撮人）→ 海洋（出海、心安、永不回头）
→ 一张地图缩影、月光下的海 → 退出纸外，一页页往回翻，原来就是每一章开头那本墨绿色的书。
画面里不写字（封面书名除外）。
"""
import math
import os
import random
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("series", "chapter01", "chapter02", "chapter03", "chapter04", "chapter05", "chapter06", "chapter07"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
from draw import *  # noqa: F401,F403,E402
from engine import BOOK_H, BOOK_W, PAGE, book_intro, book_outro, cover_face, page_paper, table_bg  # noqa: E402
from scenes_v2 import local  # noqa: E402

WARM = hexc("ffd98a")
COOL = hexc("cfe4ff")
STONE = hexc("9a948a")
SEA_A, SEA_B = hexc("4f86b8"), hexc("2f5f90")


# ================================================================ 小物件
def pebble_illus(c, cx, cy):
    """章节页小插画：一座有棱有角的小山，一条河弯弯地流下来，流到一条小帆船旁边。"""
    with keep():
        line(c, [(cx - 90, cy + 20), (cx - 55, cy - 40), (cx - 20, cy + 20)], "illm", 3.4, INK)
        line(c, [(cx - 55, cy + 24), (cx - 30, cy + 40), (cx, cy + 32), (cx + 30, cy + 46)], "illr", 3, hexc("5a8ab8"))
        line(c, [(cx + 40, cy + 30), (cx + 92, cy + 30)], "illb", 3, INK)
        line(c, [(cx + 64, cy + 30), (cx + 64, cy - 22), (cx + 88, cy + 22)], "ills", 2.6, INK)


def intro(c, t):
    book_intro(c, t, "终章", "此心安处", pebble_illus)


def rock(c, x, y, w, h, key, col=STONE, sharp=True, rot=0.0):
    """一块石头：sharp=有棱有角，否则是被磨圆的鹅卵石。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    with keep():
        if sharp:
            r = random.Random(key)
            pts = [(-w / 2, 0), (-w / 2 + r.uniform(0, w * 0.2), -h * r.uniform(0.6, 1.0)),
                   (r.uniform(-w * 0.2, w * 0.2), -h), (w / 2 - r.uniform(0, w * 0.2), -h * r.uniform(0.5, 0.9)), (w / 2, 0)]
            shape(c, pts, col, key, lw=2.2, amp=0.6)
        else:
            shape(c, ell(0, -h / 2, w / 2, h / 2, 22), col, key, lw=2, amp=0.4)
            shape(c, ell(-w * 0.15, -h * 0.68, w * 0.12, h * 0.1, 10), (1, 1, 1), key + "h", lw=0, edge=False, alpha=0.4)
    c.restore()


def breath(c, x, y, t, key, period=0.75):
    ph = (t / period) % 1
    with keep():
        shape(c, ell(x + ph * 30, y - ph * 30, 10 + ph * 18, 8 + ph * 10, 10), (1, 1, 1), key, lw=0.8, alpha=0.75 * (1 - ph))


def sailboat(c, x, y, s, key, sail=1.0, rock_=0.0, rider=None, oar=False, wake=0.0, t=0.0):
    """一条够大的帆船：木头船身、主帆和前帆。rider 是站在船尾的她（girl 的参数），oar 让她握着一支插进水里的船桨。"""
    c.save()
    c.translate(x, y)
    c.rotate(rock_)
    c.scale(s, s)
    wood = hexc("b8683e")
    with keep():
        if wake > 0:                                               # 船尾翻起的白色泡沫
            for j in range(6):
                ph = (t * 1.2 * wake + j / 6) % 1
                ex = -330 - ph * 420
                circle(c, ex, 30 + 14 * math.sin(j * 2.1), 26 * (1 - ph) + 8, (1, 1, 1), a=0.8 * (1 - ph))
                circle(c, ex - 30, 46 + 10 * math.cos(j), 16 * (1 - ph) + 6, (1, 1, 1), a=0.6 * (1 - ph))
            for j in range(4):
                ph = (t * 2.0 + j / 4) % 1
                circle(c, 330 + ph * 60, -20 - ph * 50 + ph * ph * 80, 10 * (1 - ph) + 3, (1, 1, 1), a=1 - ph)
        if sail > 0:
            line(c, [(40, -40), (40, -640)], key + "m", 7, hexc("6a4a32"))
            shape(c, [(52, -620), (52, -90), (52 + 260 * sail, -100)], (0.98, 0.97, 0.94), key + "s", lw=2.6)
            shape(c, [(30, -580), (30 - 0 * sail, -110), (30 - 200 * sail, -110)], (0.95, 0.93, 0.88), key + "j", lw=2.4)
            line(c, [(40, -640), (330, -70)], key + "fs", 1.6, hexc("6a4a32"))
    if rider is not None:
        rk = dict(rider)
        gs = rk.pop("scale", 0.8)
        if oar:                                                    # 两只手一上一下握着桨
            rk.setdefault("arms", [(-30, -70), (10, -100)])
        girl(c, -200, -40, gs, **rk)
    shape(c, [(-330, -46), (300, -54), (350, -90), (300, 30), (-270, 44)], wood, key + "h", lw=3)
    with keep():
        for j, yy in enumerate((-20, 6)):                          # 船板
            line(c, [(-310, yy - 2), (310, yy - 8)], key + f"pl{j}", 2, hexc("7a4426"), alpha=0.8)
        line(c, [(-326, -44), (304, -52)], key + "rl", 5, hexc("f4e6d0"))
    if rider is not None and oar:                                  # 船桨：握在手里，桨叶插进水里
        h2 = (-200 + 10 * gs, -40 - 100 * gs)
        dx, dy = -40.0, 30.0                                       # 沿着两只手的方向
        k_ = (70 - h2[1]) / dy
        bx, by = h2[0] + dx * k_, h2[1] + dy * k_
        with keep():
            line(c, [(h2[0] - dx * 0.9 * gs, h2[1] - dy * 0.9 * gs), (bx, by)], key + "oar", 7, hexc("8a5a32"))
            c.save()
            c.translate(bx, by)
            c.rotate(math.atan2(dy, dx) - math.pi / 2)
            shape(c, ell(0, 30, 18, 44, 14), hexc("8a5a32"), key + "blade", lw=2)
            c.restore()
    c.restore()


def ship_rider(look=0.5, eyes=False, mouth="smile", tilt=0.0, scale=0.8, key="rd"):
    return dict(scale=scale, outfit="sea_white", pack=False, look=look, eyes_closed=eyes, mouth=mouth, tilt=tilt, key=key)


def seabird(c, x, y, s, t, key):
    fl = math.sin(t * 10) * 10 * s
    with keep():
        line(c, [(x - 22 * s, y - fl), (x - 6 * s, y), (x, y + 2 * s), (x + 6 * s, y), (x + 22 * s, y - fl)], key, 2.6,
             hexc("3a3a48"))


def waves(c, t, y0, y1, key, n=5, col=(1, 1, 1), a=0.5, speed=2.0):
    with keep():
        for j in range(n):
            y = y0 + (y1 - y0) * j / max(1, n - 1)
            line(c, [(x, y + 8 * math.sin(x * 0.02 + t * speed + j)) for x in range(-40, W + 80, 40)], f"{key}{j}", 2.4, col,
                 alpha=a)


# ================================================================ 1 唯有创造
def phone_screen(c, t, zoom=0.0, fade=0.0):
    """手机屏幕：一格一格的照片往上滚；zoom → 1 时一张海的照片放大，fade 让它褪成灰白。"""
    fill_all(c, hexc("1e2030"))
    with keep():
        glow(c, 540, 760, 560, COOL, 0.22)
        shape(c, rrect(220, 160, 640, 1100, 60), hexc("2a2e3a"), "ph", lw=3)
    c.save()
    c.rectangle(250, 220, 580, 980)
    c.clip()
    with keep():
        fill_all(c, hexc("f2f4f6"))
        r = random.Random(3)
        scroll = t * 520 * (1 - zoom)
        palettes = [("8fc4ea", "f4e6c8"), ("4f86b8", "f2c890"), ("e8a090", "6a5a7a"), ("9ac08a", "e8e0c0"), ("c8d4e4", "7a8aa8"),
                    ("f2b88a", "4a6a9a"), ("b8a888", "6a8a5a")]
        for k in range(60):
            col_i, row = k % 3, k // 3
            x, y = 262 + col_i * 188, 232 + row * 188 - scroll % (188 * 6)
            if -200 < y < 1260:
                a_, b_ = r.choice(palettes)
                shape(c, rect(x, y, 178, 178), hexc(a_), f"tb{k}", lw=0, edge=False, amp=0.2)
                shape(c, rect(x, y + 100, 178, 78), hexc(b_), f"tc{k}", lw=0, edge=False, amp=0.2)
                kind = k % 4
                if kind == 0:
                    shape(c, [(x + 30, y + 100), (x + 90, y + 40), (x + 150, y + 100)], hexc("e8eef4"), f"tm{k}", lw=1.4, amp=0.3)
                elif kind == 1:
                    circle(c, x + 120, y + 60, 18, hexc("ffe8b0"))
                elif kind == 2:
                    for j in range(2):
                        line(c, [(x + 20, y + 120 + j * 20), (x + 160, y + 116 + j * 20)], f"tw{k}{j}", 2, (1, 1, 1), alpha=0.7)
                else:
                    shape(c, rect(x + 60, y + 60, 50, 40), hexc("c96f4a"), f"th{k}", lw=1.2, amp=0.3)
    if zoom > 0:                                                   # 那张海的照片
        x0, y0 = lerp(450, 250, zoom), lerp(600, 220, zoom)
        w_, h_ = lerp(178, 580, zoom), lerp(178, 980, zoom)
        with grade(sat=1 - 0.95 * fade):
            with nokeep():
                vgrad(c, y0, y0 + h_, [(0, hexc("f2b88a")), (0.5, hexc("f8d8b0")), (0.52, hexc("4f86b8")), (1, hexc("2a4a78"))],
                      x0, x0 + w_)
                circle(c, x0 + w_ / 2, y0 + h_ * 0.47, w_ * 0.12, hexc("ffe8b0"))
                for j in range(6):
                    yy = y0 + h_ * (0.6 + j * 0.06)
                    line(c, [(x0 + 20 + i * w_ / 8, yy + 4 * math.sin(i + j)) for i in range(9)], f"pw{j}", 2, (1, 1, 1),
                         alpha=0.6)
        if fade > 0:
            veil(c, (0.92, 0.92, 0.93), 0.45 * fade)
    c.restore()


def desk_book(c, t, draw_u=0.0, pen=True, open_=1.0):
    """从上往下看的书桌：摊开的空白墨绿色本子，笔尖画出第一道山脊线。"""
    table_bg(c, t)
    bw, bh = BOOK_W, BOOK_H
    sx, by = W / 2, H * 0.42 - bh / 2
    with keep():
        c.rectangle(sx - bw + 16, by + 22, 2 * bw, bh)
        c.set_source_rgba(0, 0, 0, 0.3)
        c.fill()
        shape(c, rect(sx - bw - 14, by - 14, 2 * bw + 28, bh + 28), hexc("2f4a3c") + (1.0,), "dbk", lw=3)
        page_paper(c, sx - bw, by, bw, bh, "dpL")
        page_paper(c, sx, by, bw, bh, "dpR")
        line(c, [(sx, by), (sx, by + bh)], "dspine", 2, hexc("b7a888"))
        ridge = [(sx + 40 + k * 20, by + 420 - 120 * math.sin(k / 19 * math.pi) * (1 if k < 12 else 0.8) - (k % 3) * 6)
                 for k in range(20)]
        n = int(draw_u * 20)
        if n >= 2:
            line(c, ridge[:n], "dridge", 3, INK)
        if pen:
            px, py = ridge[min(max(n - 1, 0), 19)]
            c.save()
            c.translate(px, py)
            c.rotate(-0.7)
            shape(c, rrect(-8, -240, 16, 240, 6), hexc("3a3a48"), "pen", lw=2)
            shape(c, [(-8, 0), (8, 0), (0, 22)], hexc("d8c8a8"), "nib", lw=1.6)
            c.restore()
    return sx, by


def k01(c, t):
    if t < 3.3:
        phone_screen(c, t)
    elif t < 6.6:
        lt = t - 3.3
        phone_screen(c, 3.3, zoom=ease_io(prog(lt, 0.0, 1.0)), fade=ease_io(prog(lt, 1.2, 1.8)))
    else:
        lt = t - 6.6
        z = ease_in(prog(lt, 2.0, 1.4))                            # 笔尖落下，镜头跟着钻进纸里
        sx, by = W / 2, H * 0.42 - BOOK_H / 2
        with cam(c, lerp(540, sx + 230, z), lerp(960, by + 360, z), 1 + 4 * z):
            desk_book(c, t, draw_u=prog(lt, 0.6, 1.8), pen=z < 0.6)
        if z > 0.6:
            veil(c, PAGE, (z - 0.6) / 0.4)


# ================================================================ 2–4 高原
def plateau_sky(c, warm=0.0):
    vgrad(c, -300, 1300, [(0, hexc("1e4a8c")), (0.7, hexc("7aaee0")), (1, mix(hexc("cfe4f4"), hexc("ffd8b0"), warm))],
          -300, W + 300)


def k02(c, t):
    """纸上展开一片很大的高原，云在脚下，她小小一个站在山口。"""
    draw_in = ease_io(prog(t, 0.0, 1.2))
    plateau_sky(c)
    with group_alpha(c, draw_in):
        for k in range(6):
            cloud(c, (k * 220 + t * 10) % 1400 - 200, 1060 + (k % 2) * 30, 1.6, f"c2{k}", a=0.95)
        mountain(c, 200, 1000, 700, 520, hexc("c8d4e4"), "pm1")
        mountain(c, 880, 1000, 640, 460, hexc("b8c6da"), "pm2")
        shape(c, [(-40, 2000), (-40, 1230), (320, 1170), (540, 1150), (760, 1170), (1120, 1230), (1120, 2000)],
              hexc("a89a88"), "pass", lw=3)
        girl(c, 540, 1160, 0.9, outfit="snow", pack=True, look=0.0, key="p2")
    ridge = [(-40, 1230), (320, 1170), (540, 1150), (760, 1170), (1120, 1230)]
    if draw_in < 1:
        with keep():
            line(c, ridge, "pridge", 3, INK, alpha=1 - draw_in)


def k03(c, t):
    """她在大风里喘着白气，仰望一座被朝阳照亮的雪峰；第三屏镜头推向雪峰锋利的山脊——高原是有棱有角的。"""
    push = ease_io(prog(t, 6.3, 3.0))
    with cam(c, lerp(540, 790, push), lerp(960, 560, push), lerp(1.0, 1.6, push)):
        _k03(c, t)


def _k03(c, t):
    plateau_sky(c, warm=0.4)
    with keep():
        glow(c, 820, 420, 360, hexc("ffd8a0"), 0.45)
    mountain(c, 800, 1000, 760, 760, hexc("d8e0ec"), "bigpk")
    with keep():
        shape(c, [(800, 240), (740, 380), (780, 360), (860, 400), (830, 330)], hexc("ffe6b8"), "goldtip", lw=0, edge=False,
              alpha=0.7)
    shape(c, rect(-40, 990, W + 80, 1000), hexc("a89a88"), "pl3", lw=3)
    with keep():                                                   # 风
        for j in range(4):
            xx = (t * 700 + j * 300) % 1400 - 200
            line(c, [(xx, 700 + j * 90), (xx + 160, 690 + j * 90), (xx + 240, 704 + j * 90)], f"wd{j}", 2, (1, 1, 1), alpha=0.5)
    girl(c, 320, 1240, 1.6, outfit="snow", pack=True, look=0.5, look_up=0.9, mouth="o", key="p3")
    breath(c, 320 + 30, 1240 - 150 * 1.6, t, "br3")


def cairn(c, n, key="cn"):
    """垒起来的石堆：n 块有棱有角的石头。"""
    spec = [(0, 150, 60), (-6, 130, 54), (8, 110, 50), (-4, 92, 44), (6, 74, 40), (0, 56, 34), (-3, 40, 28)]
    y = 1250
    for k in range(min(n, len(spec))):
        dx, w_, h_ = spec[k]
        rock(c, 680 + dx, y, w_, h_, f"{key}{k}", col=mix(STONE, hexc("8a8478"), (k % 2) * 0.5))
        y -= h_ * 0.86


def _flood_edge(x, t, base, amp):
    return base + amp * math.sin(x * 0.012 - t * 3.0) + amp * 0.5 * math.sin(x * 0.031 - t * 5.0)


def k04(c, t):
    """把有棱有角的石头一块块垒起来，垒完她走出画面；山上的雪水汇成一股洪流，翻着白浪从左边冲过来，
    撞在石堆上溅起水花，从两边分开流走了。石堆一动不动。"""
    flood = ease_io(prog(t, 6.3, 1.2))
    plateau_sky(c, warm=0.2)
    if flood > 0:
        with keep():
            for k in range(4):
                cloud(c, 120 + k * 200, 300 + (k % 2) * 40, 2.0, f"fc4{k}", col=hexc("8a96a8"), a=0.7 * flood)
    mountain(c, 260, 1000, 700, 600, hexc("c8d4e4"), "pk4")
    shape(c, rect(-40, 990, W + 80, 1000), hexc("a89a88"), "pl4", lw=3)
    if flood > 0:
        xs = list(range(-60, W + 80, 40))
        top = [(x, _flood_edge(x, t, lerp(1250, 1090, flood), 22 * flood)) for x in xs]
        bot = [(x, _flood_edge(x, t + 1.3, lerp(1260, 1520, flood), 26 * flood)) for x in reversed(xs)]
        shape(c, top + bot, hexc("5a8ab8"), "flood", lw=2.4, alpha=0.95)
        with keep():
            for j in range(10):                                    # 深色的水流
                ph = (t * 0.9 + j * 0.13) % 1
                y = lerp(1120, 1480, (j * 0.37) % 1)
                x = lerp(-200, W + 200, ph)
                line(c, [(x - 160, y + 8), (x, y), (x + 160, y + 10)], f"dk{j}", 5, hexc("3e6a98"), alpha=0.6 * flood)
            dry = [(612, 1240), (748, 1240), (1000, 1300), (980, 1340), (700, 1330)]  # 石堆挡出来的一小块干地
            shape(c, dry, hexc("a89a88"), "dry4", lw=2, alpha=flood)
            for j in range(14):                                    # 翻滚的白浪
                ph = (t * 0.55 + j / 14) % 1
                y = lerp(1110, 1470, (j * 0.61) % 1)
                x = lerp(-150, W + 150, ph)
                if 560 < x < 1000 and 1230 < y < 1345:
                    continue
                r_ = 34 + 14 * ((j * 7) % 3)
                c.set_source_rgba(1, 1, 1, 0.85 * flood)
                c.set_line_width(4)
                c.arc(x, y, r_, math.pi * 1.05, math.pi * 1.9)
                c.stroke()
                c.arc(x + r_ * 0.55, y - r_ * 0.5, r_ * 0.35, math.pi * 1.3, math.pi * 2.6)
                c.stroke()
            rs = random.Random(4)
            for j in range(5):                                     # 被冲走的石块
                ph = (t * 0.45 + j / 5) % 1
                x = lerp(-120, W + 120, ph)
                y = lerp(1150, 1450, rs.random()) + 10 * math.sin(t * 4 + j)
                if 560 < x < 1000 and 1220 < y < 1350:
                    continue
                rock(c, x, y, 40, 26, f"fr{j}", col=hexc("8a8478"), sharp=True, rot=t * 2 + j)
    n = 1 + int(prog(t, 0.2, 5.2) * 7)
    cairn(c, n)
    if flood > 0:                                                  # 撞在石堆上溅起来的水花
        with keep():
            for j in range(16):
                ph = (t * 1.6 + j / 16) % 1
                a_ = math.pi * (0.55 + 0.6 * (j / 16))
                d = ph * 170
                circle(c, 600 + math.cos(a_) * d, 1210 - math.sin(a_) * d * 1.2 + ph * ph * 120, 7 * (1 - ph) + 2,
                       (1, 1, 1), a=(1 - ph) * flood)
    if t < 5.6:
        girl(c, 470, 1220, 1.5, outfit="snow", pack=True, sit=True, crouch=True, look=0.7, head_down=6, mouth="flat",
             key="p4")
    elif t < 6.6:                                                  # 垒完了，她走出画面，只留下石堆
        go = prog(t, 5.6, 1.0)
        girl(c, lerp(470, 1220, go), lerp(1250, 1290, go), 1.5, outfit="snow", pack=True, look=0.9, mouth="flat",
             walk=t * 6, key="p4")


# ================================================================ 5–7 平原
def plain_bg(c, t, dusk=0.0):
    vgrad(c, 0, 1000, [(0, mix(hexc("8fc4ea"), hexc("e8a090"), dusk)), (1, mix(hexc("f4ecd0"), hexc("ffd8a8"), dusk))])
    shape(c, hill_pts(860, 20, 0.003, 0.4), mix(hexc("a8b890"), hexc("9a8a78"), dusk), "ph", lw=2)
    shape(c, rect(-40, 900, W + 80, 1100), mix(hexc("e8c860"), hexc("c8a060"), dusk), "field", lw=2.4)
    with keep():
        for row in range(5):
            for k in range(14):
                x = k * 82 + (row % 2) * 40
                y = 930 + row * 40
                line(c, [(x, y + 26), (x + 4 * math.sin(t * 2 + k), y)], f"wh{row}{k}", 2, hexc("c8a040"), alpha=0.7)


def river(c, t, y0=1060, y1=1170, col=hexc("6aa0c8")):
    shape(c, [(-40, y0), (W + 40, y0 - 20), (W + 40, y1 - 10), (-40, y1)], col, "rv", lw=2.4)
    waves(c, t, y0 + 20, y1 - 20, "rvw", n=3, a=0.45, speed=2.5)


def sheaf(c, x, y, s, key):
    """一捆麦子：麦秆、捆绳、上面一簇麦穗。"""
    with keep():
        for k in range(9):
            dx = (k - 4) * 5 * s
            line(c, [(x + dx * 0.6, y), (x + dx * 1.6, y - 110 * s)], f"{key}s{k}", 2, hexc("c8a040"))
            shape(c, ell(x + dx * 1.7, y - 118 * s, 5 * s, 14 * s, 10), hexc("e8c058"), f"{key}e{k}", lw=1, amp=0.3)
        line(c, [(x - 16 * s, y - 50 * s), (x + 16 * s, y - 50 * s)], key + "t", 4, hexc("a8783a"))


def k05(c, t):
    if t < 3.17:                                                   # 从山上走下来
        plateau_sky(c, warm=0.5)
        mountain(c, 760, 1000, 900, 600, hexc("c8d4e4"), "pk5")
        shape(c, [(-40, 2000), (-40, 1050), (500, 1150), (1120, 1300), (1120, 2000)], hexc("a8a088"), "down", lw=3)
        x = lerp(200, 760, prog(t, 0, 3.17))
        y = 1050 + (x + 40) / 1160 * 250 - 10
        girl(c, x, min(y, 1250), 1.4, outfit="snow", pack=True, look=0.8, walk=t * 6, key="p5")
        return
    lt = t - 3.17                                                  # 金色的田、大河，一起收割
    plain_bg(c, t)
    river(c, t, 1000, 1080)
    workers = [(170, 1150, "7a5a4a", "short"), (360, 1210, "4f7a5a", "bun"), (880, 1170, "8a6a9a", "short")]
    for i, (x, y, col, st) in enumerate(workers):
        bend = 0.5 + 0.5 * math.sin(lt * 2 + i)
        sheaf(c, x + 50, y, 0.9, f"sh{i}")
        local(c, x, y, 1.25, f"wk{i}", hexc(col), hexc("2f2a28"), st, head_down=12 * bend, tilt=0.25 * bend,
              mouth="laugh" if i == 1 else "smile", arms=[(30, -70 + 20 * bend), (40, -60 + 20 * bend)])
    fix = ease_io(prog(lt, 2.4, 0.8))
    girl(c, 600, 1240, 1.45, outfit="folk", hat=True, pack=True, look=0.4, mouth="laugh", key="p5b", tilt=0.06 * (1 - fix))
    local(c, 700, 1240, 1.4, "uncle", hexc("8a5a3a"), hexc("2f2a28"), "short", look=-0.7, mouth="smile",
          arms=[(-24, -78), (lerp(-24, -60, fix), lerp(-78, -220, fix))])



def _channel(y, base, ph):
    return base + 90 * math.sin(y * 0.004 + ph) + 36 * math.sin(y * 0.011 + ph * 2.3)


CHANNELS = [(170, 0.0, 30), (540, 2.2, 38), (900, 4.4, 24), (360, 5.9, 12)]


def k05m(c, t):
    """俯瞰河口的冲积平原：泥色的土地上，水道弯弯绕绕、分了又合，乱得没有章法；
    第二屏，水道之间一块块整整齐齐的田慢慢长出来，小房子沿着直直的田埂排开。"""
    rise = ease_io(prog(t, 0.0, 6.0))
    with cam(c, 540, 960, lerp(1.12, 1.0, rise)):
        shape(c, rect(-200, -200, W + 400, H + 400), hexc("c8b08a"), "mud", lw=0, edge=False)
        r = random.Random(55)
        with keep():
            for k in range(26):                                    # 深深浅浅的淤泥
                shape(c, ell(r.uniform(-100, W + 100), r.uniform(-100, H + 100), r.uniform(60, 160), r.uniform(30, 80), 12),
                      hexc(r.choice(["bfa47c", "d2bc96", "b89c74"])), f"md{k}", lw=0, edge=False, alpha=0.6)
        grow = prog(t, 2.8, 2.6)                                   # 田一块块长出来
        cells = []
        for gy in range(-3, 22):
            for gx in range(-2, 13):
                x0, y0 = gx * 92 + 4, gy * 92 + 10
                cx, cy = x0 + 42, y0 + 42
                if any(min(abs(cx - _channel(yy, b, p)) for yy in (y0, cy, y0 + 84)) < w + 46 for b, p, w in CHANNELS):
                    continue
                cells.append((x0, y0, gx, gy))
        cells.sort(key=lambda q: (q[1] - 960) ** 2 + (q[0] - 540) ** 2)
        n = len(cells)
        for i, (x0, y0, gx, gy) in enumerate(cells):
            a = clamp(grow * (n + 6) / 1.0 - i * (n + 6) / n)       # 从中间往外，一块接一块
            if a <= 0:
                continue
            col = hexc(["9ab86a", "c8b45a", "7aa860", "b8c070"][(gx * 3 + gy) % 4])
            shape(c, rect(x0, y0, 84, 84), col, f"fd{gx}_{gy}", lw=1.8, alpha=a, amp=0.6)
            with keep():
                for j in range(3):                                 # 整齐的垄
                    yy = y0 + 20 + j * 22
                    line(c, [(x0 + 10, yy), (x0 + 74, yy)], f"fr{gx}_{gy}_{j}", 1.6, hexc("5a7a40"), alpha=0.5 * a)
            if (gx * 5 + gy * 3) % 11 == 0 and a > 0.5:            # 田埂边的小房子
                hx, hy = x0 + 70, y0 + 74
                shape(c, rect(hx - 14, hy - 12, 28, 22), hexc("f2e6d0"), f"hs{gx}_{gy}", lw=1.6)
                shape(c, [(hx - 18, hy - 12), (hx, hy - 28), (hx + 18, hy - 12)], hexc("b8584a"), f"hr{gx}_{gy}", lw=1.6)
        for k, (b, p, w) in enumerate(CHANNELS):                   # 弯弯绕绕的水道
            ys = [y for y in range(-300, H + 320, 40)]
            left = [(_channel(y, b, p) - w, y) for y in ys]
            right = [(_channel(y, b, p) + w, y) for y in reversed(ys)]
            shape(c, left + right, hexc("7aaac8"), f"ch{k}", lw=2.2)
            with keep():
                for j in range(6):                                 # 水在流
                    y = (t * 90 + j * 260 + k * 70) % (H + 400) - 200
                    x = _channel(y, b, p)
                    line(c, [(x - w * 0.4, y), (x + w * 0.2, y + 24)], f"fl{k}{j}", 2, (1, 1, 1), alpha=0.5)


def k05h(c, t):
    k05(c, t + 3.17)

def k06(c, t):
    """河上一排村里人铺下的踏脚石，一个孩子先踩过去，回头伸手拉她，她踩着别人铺好的石头过了河。"""
    plain_bg(c, t)
    shape(c, rect(-40, 1000, W + 80, 1000), hexc("6aa0c8"), "rv6", lw=2.4)
    waves(c, t, 1040, 1400, "rw6", n=6, a=0.4)
    stones = [(80 + k * 130, 1250 - (k % 2) * 8) for k in range(8)]
    for k, (x, y) in enumerate(stones):
        rock(c, x, y + 14, 110, 36, f"ss{k}", col=hexc("a8a49a"), sharp=False)
    cross = prog(t, 0.6, 3.6)
    kx = lerp(560, 860, prog(t, 0.0, 1.2))
    local(c, kx, 1250, 1.0, "kid", hexc("9fc5e8"), hexc("2f2a28"), "short", look=-0.8, mouth="laugh",
          arms=[(-34, -110), (20, -70)] if cross < 0.8 else None)
    gx = lerp(80, 730, cross)
    hop = abs(math.sin(cross * math.pi * 5)) * 20
    girl(c, gx, 1250 - hop, 1.4, outfit="folk", hat=True, pack=True, look=0.8, mouth="smile",
         walk=t * 6 if cross < 1 else None, arms=[(-24, -78), (40, -120)] if 0.5 < cross < 1 else None, key="p6")


def k07(c, t):
    """黄昏，河边一张小木桌，拉她过河的孩子、老奶奶、帮她扣正草帽的大叔，中间一锅冒着热气的饭，每人一只碗。"""
    plain_bg(c, t, dusk=1.0)
    river(c, t, 1000, 1080, col=hexc("c88a7a"))
    with keep():                                                   # 落到河那边的太阳
        glow(c, 760, 880, 360, WARM, 0.5)
        c.save()
        c.rectangle(-100, 0, W + 200, 870)
        c.clip()
        circle(c, 760, 880, 60, hexc("ffcf80"))
        c.restore()
    shape(c, rect(250, 1150, 580, 18), hexc("8c5a3c"), "tbl", lw=2.4)
    for x in (280, 800):
        line(c, [(x, 1168), (x, 1250)], f"tl{x}", 6, hexc("6a4a32"))
    local(c, 300, 1150, 1.3, "kid7", hexc("9fc5e8"), hexc("2f2a28"), "short", sit=True, legs=False, look=0.6, mouth="laugh")
    local(c, 430, 1150, 1.4, "gma", hexc("6a5a7a"), hexc("2f2a28"), "bun", sit=True, legs=False, age=1.0, look=0.4,
          mouth="smile")
    girl(c, 640, 1150, 1.45, outfit="folk", hat=False, pack=False, sit=True, legs=False, look=-0.3, mouth="laugh", key="p7")
    local(c, 780, 1150, 1.4, "uncle7", hexc("8a5a3a"), hexc("2f2a28"), "short", sit=True, legs=False, look=-0.5, mouth="smile")
    with keep():                                                   # 桌子中间一锅热饭，每人面前一只碗
        shape(c, [(492, 1150), (588, 1150), (600, 1098), (480, 1098)], hexc("5a4a40"), "pot", lw=2.4)
        shape(c, ell(540, 1098, 62, 12, 18), hexc("7a6a5a"), "potl", lw=2)
        for j in range(3):                                         # 热气
            ph = (t * 0.5 + j / 3) % 1
            x0 = 515 + j * 25
            line(c, [(x0, 1080 - ph * 120), (x0 + 10 * math.sin(ph * 6 + j), 1050 - ph * 120),
                     (x0 - 6, 1020 - ph * 120)], f"stm{j}", 3, (1, 1, 1), alpha=0.6 * (1 - ph))
        for k, x in enumerate((330, 440, 650, 770)):
            shape(c, ell(x, 1146, 28, 10, 14, 0, math.pi), (0.97, 0.96, 0.93), f"bs{k}", lw=1.6)


# ================================================================ 8–12 海洋
def sea_bg(c, t, dusk=0.0, storm=0.0, horizon=900):
    top = mix(mix(hexc("8fc4ea"), hexc("e8907a"), dusk), hexc("5a6070"), storm)
    bot = mix(mix(hexc("f2f0e4"), hexc("ffd0a0"), dusk), hexc("9aa0a8"), storm)
    vgrad(c, -200, horizon, [(0, top), (1, bot)], -300, W + 300)
    shape(c, rect(-300, horizon, W + 600, 1400), mix(mix(SEA_A, hexc("c87a6a"), dusk * 0.6), hexc("3a4a5a"), storm),
          "sea", lw=2)
    waves(c, t, horizon + 60, horizon + 600, "sw", n=6, a=0.45 - 0.2 * storm)


def k08(c, t):
    k = min(int(t / 3.1), 4)
    u = t - k * 3.1
    if k == 0:                                                     # 走到海边
        vgrad(c, 0, 900, [(0, hexc("8fc4ea")), (1, hexc("f2f0e4"))])
        shape(c, rect(-40, 880, W + 80, 1100), SEA_A, "sea8", lw=2)
        shape(c, [(-40, 1700), (-40, 1150), (300, 1080), (700, 1040), (1120, 1000), (1120, 1700)], hexc("e8d8b0"), "sand8",
              lw=2.4)
        wash = 0.5 + 0.5 * math.sin(u * 1.4)                        # 浪一下一下漫上沙滩
        with keep():
            shape(c, [(-40, 1150), (300, 1080), (700, 1040), (1120, 1000), (1120, 1000 + 40 * wash), (700, 1060 + 50 * wash),
                      (300, 1100 + 50 * wash), (-40, 1170 + 50 * wash)], (0.96, 0.97, 0.98), "foam8", lw=1.4, alpha=0.7)
        waves(c, u, 920, 1020, "w8", n=3)
        girl(c, lerp(760, 880, prog(u, 0, 3.1)), 1240, 1.4, outfit="sea_white", pack=True, look=0.6, walk=u * 6, key="p8")
    elif k == 1:                                                   # 小岛：岛民把不多的鱼和水果分着搬上岸
        sea_bg(c, u)
        shape(c, [(-40, 1700), (-40, 1100), (200, 1020), (520, 1000), (720, 1060), (900, 1180), (1120, 1220), (1120, 1700)],
              hexc("e8d8b0"), "isl", lw=2.4)
        sailboat(c, 830, 1170, 0.4, "fb", sail=0.0)
        for i, (x, col) in enumerate(((300, "4f8a8a"), (480, "c98d72"))):
            local(c, x, 1200, 1.3, f"isl{i}", hexc(col), hexc("2f2a28"), "short", look=0.6 - i, walk=u * 4 + i,
                  arms=[(-26, -150), (26, -150)])
            with keep():
                shape(c, ell(x, 1200 - 160 * 1.3, 40, 14, 14, 0, math.pi), hexc("c8a060"), f"bsk{i}", lw=2)
                circle(c, x - 10, 1200 - 166 * 1.3, 9, hexc(["7fb8d8", "e8743a"][i]))
        girl(c, 640, 1240, 1.4, outfit="sea_white", pack=True, look=-0.4, mouth="smile", key="p8")
    elif k == 2:                                                   # 解开缆绳
        sea_bg(c, u)
        shape(c, rect(-40, 1180, 600, 60), hexc("8c6a4a"), "pier8", lw=2.4)
        for x in (60, 300, 520):
            line(c, [(x, 1240), (x, 1400)], f"pp{x}", 8, hexc("6a4a32"))
        sail = ease_io(prog(u, 1.2, 1.4))
        untie = ease_io(prog(u, 0.2, 0.8))
        sailboat(c, 800, 1290, 0.85, "sb", sail=sail, rock_=0.02 * math.sin(u * 2),
                 rider=ship_rider(look=-0.6, scale=0.85, key="p8r"))
        with keep():                                               # 缆绳解开，落进水里
            line(c, [(520, 1190), (lerp(530, 560, untie), lerp(1270, 1330, untie)), (lerp(530, 600, untie), lerp(1260, 1360, untie))],
                 "rope", 3, hexc("c8b088"))
    elif k == 3:                                                   # 扬帆出海
        sea_bg(c, u)
        go = ease_in(prog(u, 0.0, 3.1))
        x = lerp(560, 760, go)
        y = lerp(1300, 1040, go)
        s = lerp(0.95, 0.5, go)
        sailboat(c, x, y, s, "sb", rock_=0.03 * math.sin(u * 2), rider=ship_rider(look=0.5, scale=0.85, key="p8s"),
                 oar=True, wake=0.6, t=u)
    else:                                                          # 一场未知而远大的冒险：一望无际的海，远处的云
        sea_bg(c, u, horizon=980)
        for j in range(4):
            cloud(c, 120 + j * 280 + u * 20, 760 + (j % 2) * 60, 2.0, f"fc{j}", a=0.9)
        with keep():
            glow(c, 900, 900, 380, hexc("fff0c8"), 0.4)
        go = prog(u, 0.0, 3.1)
        x, y = lerp(420, 640, go), lerp(1180, 1060, go)
        sailboat(c, x, y, lerp(0.42, 0.28, go), "sbfar", rock_=0.03 * math.sin(u * 2), rider=ship_rider(scale=0.85, key="pfar"))


def boat_close(c, t, dusk=0.0, storm=0.0, look=0.5, eyes=False, mouth="smile", speed=0.0, lean=0.0, balance=0.0):
    """近一点看那条大船：她小小地站在船尾，握着船桨。"""
    sea_bg(c, t, dusk=dusk, storm=storm, horizon=860)
    rock_ = 0.04 * math.sin(t * 1.6) * (1 + 3 * storm)
    tilt = (0.1 if eyes else 0.0) - rock_ * balance
    sailboat(c, 620, 1190, 1.15, "bc", sail=1.0, rock_=rock_,
             rider=ship_rider(look=look, eyes=eyes, mouth=mouth, tilt=tilt, scale=0.85, key="bcg"),
             oar=True, wake=speed, t=t)


def k09(c, t):
    """心安或许并不是一种生存状态（平静的海上，闭着眼）；而是在不断的动荡和摇摆中，保持自我的平衡（风雨里，船摇得很厉害，她稳稳地坐正）。"""
    if t < 3.17:
        with keep():
            glow(c, 540, 400, 600, hexc("ffe8b0"), 0.3)
        boat_close(c, t, eyes=True, mouth="smile", lean=-10)
        return
    lt = t - 3.17
    storm = ease_io(prog(lt, 0.0, 0.8))
    boat_close(c, t, storm=storm, look=0.7, mouth="flat", balance=1.0)
    with keep():
        for k in range(5):
            cloud(c, 300 + k * 160, 320 + (k % 2) * 40, 2.2, f"st{k}", col=hexc("4a4e5a"), a=0.9 * storm)
        if 1.2 < lt % 3.2 < 1.3:
            line(c, [(560, 420), (520, 560), (580, 600), (530, 760)], "bolt", 4, hexc("fff6c8"))
            veil(c, (1, 1, 1), 0.25)
        rs = random.Random(9)
        for k in range(50):                                        # 斜斜的雨
            x = (rs.uniform(0, W + 300) - lt * 500) % (W + 300)
            y = (rs.uniform(0, 1700) + lt * 1300) % 1700
            line(c, [(x, y), (x - 12, y + 34)], f"rn{k}", 1.6, hexc("c8d4e0"), alpha=0.5 * storm)
        ph = (lt * 1.33) % 1                                       # 拍在船头的浪
        if ph < 0.4:
            for k in range(8):
                a = k / 8 * math.pi
                circle(c, 1010 + math.cos(a) * ph * 200, 1110 - math.sin(a) * ph * 160, 7, (1, 1, 1), a=1 - ph / 0.4)


def k12(c, t):
    """风雨过去，她把帆拉紧，船往前冲，船尾的白浪很快被海抹平。"""
    boat_close(c, t, look=0.8, mouth="laugh", speed=1.0)


def k13(c, t):
    """太阳落进海里，她把帆一点点放下来；天黑了，月亮升起来，海面平得像一面镜子，小船停在月光里。"""
    if t < 6.25:
        sea_bg(c, t, dusk=1.0, horizon=900)
        sun_y = lerp(820, 905, ease_io(prog(t, 0.0, 6.25)))
        with keep():
            glow(c, 540, sun_y, 420, hexc("ffb070"), 0.6)
            c.save()
            c.rectangle(-100, -300, W + 200, 1200)
            c.clip()
            circle(c, 540, sun_y, 90, hexc("ffcf80"))
            c.restore()
            for j in range(5):                                     # 海面上的光
                line(c, [(540 - 80 + j * 10, 930 + j * 40), (540 + 80 - j * 10, 930 + j * 40)], f"sg{j}", 4,
                     hexc("ffd8a0"), alpha=0.6 * (1 - prog(t, 4.0, 2.25)))
        for k in range(3):
            x = (t * 120 + k * 90) % 1500 - 300
            seabird(c, x, 560 + (k % 2) * 50 + 20 * math.sin(t + k), 0.9, t + k, f"sb{k}")
        sail = lerp(1.0, 0.2, ease_io(prog(t, 1.5, 3.5)))       # 帆一点点放下来
        rk = 0.02 * math.sin(t * 1.5) * (1 - 0.6 * prog(t, 1.5, 3.5))
        sailboat(c, 760, 1240, 1.2, "sb13", sail=sail, rock_=rk)
        girl(c, 700, 1222, 1.3, outfit="sea_white", pack=False, sit=True, legs=False, look=-0.7, mouth="smile",
             eyes_closed=t > 4.2, key="p13")
        return
    u = t - 6.25
    night = ease_io(prog(u, 0.0, 2.5))
    top = mix(hexc("e8907a"), hexc("1c2448"), night)
    bot = mix(hexc("ffd0a0"), hexc("4a5a8a"), night)
    vgrad(c, -200, 900, [(0, top), (1, bot)], -300, W + 300)
    r = random.Random(31)
    with keep():
        for k in range(30):
            star(c, r.uniform(0, W), r.uniform(60, 760), r.uniform(1.5, 2.6), night * (0.4 + 0.3 * math.sin(u * 2 + k)))
    shape(c, rect(-300, 900, W + 600, 1400), mix(hexc("b07a7a"), hexc("26345a"), night), "sea13", lw=2)
    my = lerp(860, 520, ease_io(prog(u, 0.4, 5.0)))               # 月亮慢慢升起来
    with keep():
        glow(c, 380, my, 300, hexc("fff4d8"), 0.35 * night)
        c.save()
        c.rectangle(-100, -300, W + 200, 1200)
        c.clip()
        circle(c, 380, my, 54, mix(hexc("ffd8a0"), hexc("fff6e0"), night))
        c.restore()
        for j in range(7):                                         # 平静的海面上一片柔柔的月光
            y = 960 + j * 50
            glow(c, 380 + 8 * math.sin(u * 1.2 + j), y, 70 + j * 14, hexc("fff0c8"), 0.22 * night * (1 - j / 9))
    sailboat(c, 640, 1200, 0.42, "sb13n", sail=0.6, rock_=0.01 * math.sin(u),
             rider=ship_rider(look=-0.6, eyes=True, scale=0.85, key="p13n"))



# ================================================================ 13a 一张缩影：从高原到海洋的地图
KRAFT = hexc("e2ad66")


def _river_x(y):
    return 470 + 150 * math.sin((y - 560) * 0.0065) + 40 * math.sin(y * 0.017)


def _coast_y(x):
    return 1350 + 46 * math.sin(x * 0.011) + 20 * math.sin(x * 0.031 + 1)


def _journey():
    """她走过的路：从山口出发，绕着湖、在村子里来回、在田里打转，最后到海边上船。乱七八糟的。"""
    way = [(250, 330), (330, 420), (240, 520), (300, 640), (420, 600), (470, 700), (700, 760), (820, 690),
           (760, 860), (600, 900), (380, 860), (300, 980), (520, 1060), (760, 1040), (700, 1150), (420, 1120),
           (330, 1230), (520, 1290), (600, 1240), (560, 1350), (640, 1450), (720, 1540)]
    pts = []
    for i in range(len(way) - 1):
        (x0, y0), (x1, y1) = way[i], way[i + 1]
        for k in range(12):
            u = k / 12
            w = math.sin((i * 12 + k) * 0.9) * 10 + math.sin((i * 12 + k) * 0.37) * 14
            pts.append((lerp(x0, x1, u) + w, lerp(y0, y1, u) - w * 0.6))
    pts.append(way[-1])
    return pts


JOURNEY = _journey()


def map_card(c, t, draw=1.0, path=1.0):
    """竖着的牛皮纸卡片：上面是有棱有角的山和湖，一条河弯弯地流过平原，一边挤满小房子、一边是纵横的田，最下面是海和小帆船。"""
    table_bg(c, t)
    x0, y0, w, h = 70, 90, W - 140, H - 300
    with keep():
        shape(c, rect(x0 + 10, y0 + 14, w, h), (0, 0, 0), "mshadow", lw=0, edge=False, alpha=0.25)
    shape(c, rect(x0, y0, w, h), KRAFT, "mcard", lw=2.4, amp=0.6)
    with keep():
        for k in range(6):                                         # 活页孔
            circle(c, x0 + 40, y0 + 160 + k * 260, 16, hexc("6a4a32"))
    c.save()
    c.rectangle(x0 + 70, y0 + 20, w - 90, h - 40)
    c.clip()
    r = random.Random(81)
    ink = hexc("2e2420")
    pencil = hexc("7a5a3a")
    a_m, a_r, a_p, a_o = [clamp((draw - d) / 0.3) for d in (0.0, 0.2, 0.4, 0.6)]
    with keep():
        if a_m > 0:                                                # 有棱有角的山
            for k in range(16):
                mx, my = 150 + (k % 6) * 140 + r.uniform(-30, 30), 210 + (k // 6) * 130 + r.uniform(-20, 20)
                if abs(mx - 300) < 90 and abs(my - 520) < 70:
                    continue
                s_ = r.uniform(0.8, 1.2)
                line(c, [(mx - 60 * s_, my + 50 * s_), (mx, my - 50 * s_), (mx + 60 * s_, my + 50 * s_)], f"mt{k}", 4, ink,
                     alpha=a_m)
                line(c, [(mx, my - 50 * s_), (mx - 8, my + 30 * s_)], f"mtr{k}", 2.4, ink, alpha=a_m)
            shape(c, ell(300, 525, 95, 62, 20), hexc("e8bc78"), "lake", lw=3.4, alpha=a_m)
            for j in range(3):
                line(c, [(270, 505 + j * 18), (330, 505 + j * 18)], f"lk{j}", 2.4, ink, alpha=a_m)
        if a_r > 0:                                                # 河
            ys = list(range(560, 1390, 30))
            for side in (-1, 1):
                line(c, [(_river_x(y) + side * (8 + (y - 560) * 0.02), y) for y in ys], f"rv{side}", 3.4, ink, alpha=a_r)
        if a_p > 0:                                                # 河一边挤满了小房子
            for k in range(70):
                hy = r.uniform(640, 1000)
                hx = _river_x(hy) + r.uniform(50, 360)
                if hx > W - 110:
                    continue
                aa = a_p * clamp((a_p * 70 - k) / 4 + 1)
                c.set_source_rgba(*pencil[:3], 0.9 * aa)
                c.set_line_width(1.8)
                c.rectangle(hx - 12, hy - 8, 24, 18)
                c.move_to(hx - 14, hy - 8)
                c.line_to(hx, hy - 22)
                c.line_to(hx + 14, hy - 8)
                c.stroke()
            for k in range(26):                                    # 另一边纵横的田和小路
                fy = r.uniform(1000, 1300)
                fx = r.uniform(120, _river_x(fy) - 30)
                ang = r.uniform(-0.9, 0.9)
                ln = r.uniform(80, 220)
                c.set_source_rgba(*pencil[:3], 0.7 * a_p)
                c.set_line_width(1.6)
                c.move_to(fx, fy)
                c.line_to(fx + ln * math.cos(ang), fy + ln * math.sin(ang))
                c.stroke()
        if a_o > 0:                                                # 海岸线、海浪、小帆船
            xs = list(range(60, W - 40, 30))
            line(c, [(x, _coast_y(x)) for x in xs], "coast", 4.4, ink, alpha=a_o)
            for k in range(9):
                wx, wy = r.uniform(140, W - 160), r.uniform(1440, 1640)
                line(c, [(wx, wy), (wx + 30, wy - 14), (wx + 60, wy), (wx + 90, wy - 12)], f"ow{k}", 3, ink, alpha=0.8 * a_o)
            for k, (bx, by, bs) in enumerate(((300, 1470, 1.0), (520, 1600, 0.8), (860, 1460, 0.9), (720, 1540, 1.4),
                                              (920, 1620, 0.7))):
                c.set_source_rgba(*ink[:3], a_o)
                c.set_line_width(2.4)
                c.move_to(bx - 16 * bs, by)
                c.line_to(bx + 16 * bs, by)
                c.line_to(bx + 10 * bs, by + 10 * bs)
                c.line_to(bx - 10 * bs, by + 10 * bs)
                c.close_path()
                c.move_to(bx, by)
                c.line_to(bx, by - 34 * bs)
                c.line_to(bx + 18 * bs, by - 8 * bs)
                c.stroke()
    if path > 0:                                                   # 她走过的那条乱七八糟的路
        n = max(2, int(len(JOURNEY) * path))
        c.set_source_rgba(*hexc("c0443a")[:3], 0.9)
        c.set_line_width(5)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_dash([14, 12])
        c.move_to(*JOURNEY[0])
        for p in JOURNEY[1:n]:
            c.line_to(*p)
        c.stroke()
        c.set_dash([])
        hx, hy = JOURNEY[n - 1]
        with keep():
            glow(c, hx, hy, 40, hexc("ffe08a"), 0.6)
            circle(c, hx, hy, 11, hexc("f2c230"))
    c.restore()


def k13a(c, t):
    """一张缩影：牛皮纸上的地图画出来，一条红色虚线是她走过的路，兜兜转转，最后到了海边。"""
    with cam(c, 540, 960, lerp(1.08, 1.0, ease_io(prog(t, 0.0, 9.4)))):
        map_card(c, t, draw=prog(t, 0.2, 2.2), path=ease_io(prog(t, 2.2, 6.6)))


def k13n(c, t):
    k13(c, t + 8.0)


# ================================================================ 13c 成长是重锤凿出来的；下一座山前，又回到新手村
CLIMB = [(0.0, 0.0), (1.6, 0.32), (2.3, 0.14), (3.9, 0.46), (4.6, 0.28), (6.2, 0.42), (8.0, 0.78), (8.6, 0.6),
         (9.5, 0.6), (11.2, 1.0), (16.0, 1.0)]


def _climb(t):
    for (t0, u0), (t1, u1) in zip(CLIMB, CLIMB[1:]):
        if t <= t1:
            k = ease_io(prog(t, t0, t1 - t0))
            return lerp(u0, u1, k), u1 < u0
    return 1.0, False


def _slope_pt(u):
    return lerp(160, 700, u), lerp(1470, 910, u)


def k13g(c, t):
    """黄昏，她爬一段陡坡：滑下来，再爬，摔一跤，再爬，终于翻上坡顶，喘着气笑了。
    最后一屏镜头拉远：坡顶后面是一整排更高、更远的山。她扶了扶草帽，又是新手。"""
    out = ease_io(prog(t, 12.2, 2.4))
    u, slip = _climb(t)
    x, y = _slope_pt(u)
    with cam(c, lerp(x + 60, 540, out), lerp(y - 160, 960, out), lerp(1.35, 1.0, out)):
        vgrad(c, -400, 2400, [(0, hexc("e8a090")), (0.35, hexc("f6c8a0")), (1, hexc("fbe6c4"))], -500, W + 500)
        with keep():
            glow(c, 220, 820, 420, hexc("ffd8a0"), 0.5)
        with group_alpha(c, out):                                  # 坡顶后面，一整排更高、更远的山
            for k, (mx, mh, mw) in enumerate(((-120, 520, 520), (300, 600, 560), (700, 700, 600), (1080, 640, 560),
                                              (1420, 560, 520))):
                mountain(c, mx, 1000, mw, mh, mix(hexc("c8b4c4"), hexc("f6d4b4"), 0.3 + 0.2 * (k % 2)), f"far{k}")
        shape(c, [(-400, 2400), (-400, 1520), (160, 1470), (700, 910), (760, 920), (1500, 1150), (1500, 2400)],
              hexc("a88a70"), "slope", lw=3)
        with keep():                                               # 坡上的碎石和草
            for k in range(9):
                px, py = _slope_pt(k / 9 + 0.04)
                line(c, [(px - 14, py + 30), (px - 6, py + 12)], f"gr{k}", 2, hexc("6a7a50"), alpha=0.7)
        if slip and u < 0.65 and t > 8.0:                          # 摔了一跤，坐在坡上
            girl(c, x, y + 10, 1.2, hat=True, pack=True, sit=True, crouch=True, look=-0.4, mouth="flat", key="p13g")
        else:
            moving = 0.0 < t < 11.2
            lean = 0.18 if moving and not slip else (-0.12 if slip else 0.0)
            arms = None
            if t > 13.0 and t < 14.4:                              # 扶了扶草帽
                arms = [(-24, -78), (14, -168)]
            girl(c, x, y, 1.2, hat=True, pack=True, look=0.6 if t < 11.2 else 0.2, tilt=lean,
                 mouth="flat" if t < 11.2 else "laugh", walk=t * 6 if moving and not slip else 0, arms=arms,
                 key="p13g")
            if 11.0 < t < 13.5:
                breath(c, x + 30, y - 190, t, "br13g")

# ================================================================ 14 退出纸外，一页页往回翻
_STILLS = {}


def _still(name):
    if name in _STILLS:
        return _STILLS[name]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cc = cairo.Context(surf)
    fn, tt = STILL_SPECS[name]
    try:
        with grade(sat=1.0, dark=0.0, warm=0.0):
            fn()(cc, tt)
    except Exception:
        cc.set_source_rgb(*PAGE)
        cc.paint()
    _STILLS[name] = surf
    return surf


def _imp(mod, fn):
    def get():
        m = __import__(mod)
        return getattr(m, fn)
    return get


STILL_SPECS = {
    "sea": (lambda: k13g, 15.4), "plain": (lambda: k07, 2.0), "plateau": (lambda: k04, 8.0),
    "ch7": (_imp("scenes07", "h03"), 1.0), "ch6": (_imp("scenes06", "g09"), 6.0), "ch5": (_imp("scenes05", "f06"), 6.0),
    "ch4": (_imp("scenes04", "e02"), 3.0), "ch3": (_imp("scenes03w", "kitchen_wide"), 2.0),
    "ch2": (_imp("scenes02", "c11_platform"), 2.0), "ch1": (_imp("scenes_v2", "s14_door"), 3.0),
}
FLIP_ORDER = ["sea", "plain", "plateau", "ch7", "ch6", "ch5", "ch4", "ch3", "ch2", "ch1"]


def _page_img(c, surf, x, y, w, h):
    c.save()
    c.rectangle(x, y, w, h)
    c.clip()
    c.translate(x, y)
    c.scale(w / W, h / H)
    c.set_source_surface(surf, 0, 0)
    c.paint()
    c.restore()


def k14(c, t):
    bw, bh = BOOK_W, BOOK_H
    sx, by = W / 2, H * 0.42 - bh / 2
    pr = (sx + 30, by + 40, bw - 60, bh - 80)
    table_bg(c, t)
    close = ease_io(prog(t, 9.6, 1.6))
    with keep():
        if close < 1:
            c.rectangle(sx - bw + 16, by + 22, 2 * bw, bh)
            c.set_source_rgba(0, 0, 0, 0.3)
            c.fill()
            shape(c, rect(sx - bw - 14, by - 14, 2 * bw + 28, bh + 28), hexc("2f4a3c") + (1.0,), "kbk", lw=3)
            page_paper(c, sx - bw, by, bw, bh, "kpL")
            page_paper(c, sx, by, bw, bh, "kpR")
    nsp = len(FLIP_ORDER) // 2                                     # 每一张对开：右页 P[2s]、左页 P[2s+1]，每个画面只出现一次
    flips = prog(t, 3.1, 6.2) * (nsp - 1)
    sp = min(int(flips), nsp - 1)
    frac = flips - sp if sp < nsp - 1 else 0.0
    z = ease_io(prog(t, 0.0, 2.4))                                 # 镜头从纸里退出来
    pl = (sx - bw + 30, by + 40, bw - 60, bh - 80)

    def img(i):
        return _still(FLIP_ORDER[min(i, len(FLIP_ORDER) - 1)])
    if close <= 0:
        if t < 3.1:
            x, y, w_, h_ = (lerp(0, pr[0], z), lerp(0, pr[1], z), lerp(W, pr[2], z), lerp(H, pr[3], z))
            if z > 0.5:
                _page_img(c, img(1), *pl)
            _page_img(c, _still("sea"), x, y, w_, h_)
        else:                                                      # 往回翻：左页那一张纸翻起来，落到右边，露出它背面的画
            front, back = 2 * sp + 1, 2 * sp + 2
            _page_img(c, img(2 * sp + 3) if frac > 0 else img(front), *pl)
            _page_img(c, img(2 * sp), *pr)
            if frac > 0:
                wv = math.cos(frac * math.pi)
                with keep():
                    if wv > 0:
                        page_paper(c, sx - bw * wv, by, bw * wv, bh, "leafL")
                        _page_img(c, img(front), sx - (bw - 30) * wv, by + 40, (bw - 60) * wv, bh - 80)
                    else:
                        page_paper(c, sx, by, -bw * wv, bh, "leafR")
                        _page_img(c, img(back), sx + 30 * -wv, by + 40, (bw - 60) * -wv, bh - 80)
        with keep():
            line(c, [(sx, by), (sx, by + bh)], "kspine", 2, hexc("b7a888"))
    else:                                                          # 合上：正是每一章开头的那本墨绿色的书
        wv = math.cos(close * math.pi / 2)
        with keep():
            if close < 1:
                shape(c, rect(sx - bw - 14 + (bw + 14) * (1 - wv), by - 14, (bw + 14) * wv + bw + 14, bh + 28),
                      hexc("2f4a3c") + (1.0,), "kbk2", lw=3)
            if wv > 0.05:
                page_paper(c, sx, by, bw, bh, "kpR2")
                page_paper(c, sx - bw * wv, by, bw * wv, bh, "kpL2")
        if close >= 1:                                             # 合好的书挪到桌子中间，和每章开头一样
            slide = ease_io(prog(t, 11.2, 0.9))
            cx0 = lerp(sx, W / 2 - (bw + 14) / 2, slide)
            with keep():
                c.rectangle(cx0 + 16, by + 8, bw + 14, bh + 28)
                c.set_source_rgba(0, 0, 0, 0.3)
                c.fill()
            cover_face(c, cx0, by - 14, bw + 14, bh + 28, key="kcv")


# ================================================================ 15 合上书，推门出去
def room15(c, t):
    fill_all(c, hexc("e8dcc4"))
    with keep():                                                   # 晨光从窗户照进来
        shape(c, rect(120, 300, 300, 420), hexc("cfe6f2"), "rwin", lw=4)
        glow(c, 270, 520, 520, hexc("fff0c8"), 0.5)
        line(c, [(270, 300), (270, 720)], "rwm", 4, hexc("b8a488"))
        shape(c, [(120, 720), (420, 720), (700, 1240), (300, 1240)], hexc("fff0c8"), "beam", lw=0, edge=False, alpha=0.3)
    shape(c, rect(-40, 1240, W + 80, 800), hexc("c8b090"), "rfl", lw=3)
    shape(c, rect(380, 1050, 380, 20), hexc("8c5a3c"), "rdesk", lw=2.4)
    for x in (400, 740):
        line(c, [(x, 1070), (x, 1240)], f"rdl{x}", 6, hexc("6a4a32"))


def closed_book(c, x, y, s, key):
    with keep():
        shape(c, [(x - 110 * s, y), (x + 110 * s, y), (x + 100 * s, y - 26 * s), (x - 100 * s, y - 26 * s)],
              hexc("2f4a3c") + (1.0,), key, lw=2.4)
        line(c, [(x - 96 * s, y - 13 * s), (x + 96 * s, y - 13 * s)], key + "g", 1.6, hexc("c8a860"))


def k15(c, t):
    k = min(int(t / 3.125), 3)
    u = t - k * 3.125
    if k < 3:
        room15(c, t)
        closed_book(c, 570, 1050, 1.0, "cb")
        place = ease_io(prog(t, 0.3, 1.0))
        with keep():                                               # 门
            shape(c, rect(820, 520, 220, 720), hexc("8c6a4a"), "door", lw=3)
            op = ease_io(prog(t, 4.0, 1.2))
            if op > 0:
                shape(c, rect(820, 520, 220 * op, 720), hexc("fff3d0"), "dlight", lw=1)
                glow(c, 930, 900, 400, hexc("fff0c8"), 0.5 * op)
        if k == 0:
            hat = u > 1.8
            girl(c, 480, 1240, 1.6, hat=hat, pack=u > 2.4, look=0.6, mouth="smile",
                 arms=[(-24, -78), (lerp(50, 24, place), lerp(-110, -78, place))] if u < 1.4 else None, key="p15")
            if not hat:
                hat_item(c, 520, 1040, 0.8, "h15")
        elif k == 1:
            x = lerp(480, 880, ease_io(prog(u, 0.3, 2.6)))
            girl(c, x, 1240, 1.6, hat=True, pack=True, look=0.8, mouth="smile", walk=u * 6, key="p15")
        else:
            a = 1 - ease_io(prog(u, 0.2, 1.6))
            with group_alpha(c, a):
                girl(c, 930, 1240, 1.5, view="back", hat=True, pack=True, walk=u * 6, key="p15")
        return
    push = ease_io(prog(u, 0.0, 3.1))                              # 镜头留在桌上那本书上
    with cam(c, lerp(560, 575, push), lerp(980, 1030, push), lerp(1.0, 2.6, push)):
        room15(c, t)
        closed_book(c, 570, 1050, 1.0, "cb")
        with keep():
            px = lerp(420, 700, push)
            shape(c, [(px, 1000), (px + 120, 1000), (px + 160, 1050), (px + 40, 1050)], hexc("fff0c8"), "sunp", lw=0,
                  edge=False, alpha=0.35)


# ================================================================ 片尾
_END = {}


def end_still():
    if "s" not in _END:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(135.0)
        with grade(sat=1.0, dark=0.0, warm=0.05):
            k15(cc, 12.4)
        _END["s"] = surf
    return _END["s"]


def outro(c, t):
    book_outro(c, t, end_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="终章 · 完")

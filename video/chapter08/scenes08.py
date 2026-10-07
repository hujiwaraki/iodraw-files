"""终章 · 此心安处 —— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。

她回到房间，照片越拍越多，心情却留不住了；唯有创造才能永恒。笔尖落在空白的书页上，
镜头钻进纸里：高原（垒石头、建立秩序）→ 平原（踏脚石、身边的一小撮人）→ 海洋（出海、心安、永不回头）
→ 被浪磨圆的鹅卵石 → 退出纸外，一页页往回翻，原来就是每一章开头那本墨绿色的书。
贯穿的小线索是石头：有棱有角 → 别人铺好的踏脚石 → 被浪磨圆的鹅卵石。画面里不写字（封面书名除外）。
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
    """章节页小插画：一颗圆圆的鹅卵石。"""
    with keep():
        shape(c, ell(cx, cy + 30, 52, 34, 26), hexc("b8b0a4"), "ill", lw=3, amp=0.5)
        shape(c, ell(cx - 14, cy + 20, 14, 7, 12), (1, 1, 1), "illh", lw=0, edge=False, alpha=0.5)


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


def sailboat(c, x, y, s, key, sail=1.0, rock_=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rock_)
    c.scale(s, s)
    with keep():
        if sail > 0:
            line(c, [(0, -10), (0, -260)], key + "m", 4, hexc("6a4a32"))
            shape(c, [(4, -250), (4, -20), (4 + 150 * sail, -30)], (0.98, 0.97, 0.94), key + "s", lw=2.4)
        shape(c, [(-130, -12), (140, -12), (100, 34), (-100, 34)], hexc("c96f4a"), key + "h", lw=2.6)
        line(c, [(-124, 0), (134, 0)], key + "st", 2, hexc("f4e6d0"))
    c.restore()


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
    """她在大风里喘着白气，仰望一座被朝阳照亮的雪峰。"""
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


def k04(c, t):
    """把有棱有角的石头一块块垒起来；雪水冲下来，绕过石堆流走了，石堆一动不动。"""
    plateau_sky(c, warm=0.2)
    mountain(c, 260, 1000, 700, 600, hexc("c8d4e4"), "pk4")
    shape(c, rect(-40, 990, W + 80, 1000), hexc("a89a88"), "pl4", lw=3)
    flood = ease_io(prog(t, 6.3, 1.4))
    if flood > 0:                                                  # 雪水汇成急流
        with keep():
            pts_l = [(lerp(-40, 380, k / 10), lerp(1000, 1500, k / 10)) for k in range(11)]
            band = [(x - 120 * flood, y) for x, y in pts_l] + [(x + 140 * flood, y) for x, y in reversed(pts_l)]
            shape(c, band, hexc("8ab8d8"), "flood", lw=2, alpha=0.9)
            for j in range(7):
                ph = (t * 1.6 + j / 7) % 1
                x, y = lerp(-40, 380, ph), lerp(1000, 1500, ph)
                line(c, [(x - 40, y), (x, y + 10), (x + 40, y)], f"fl{j}", 2.4, (1, 1, 1), alpha=0.7 * flood)
            for j in range(5):                                     # 水从石堆两边分开流过去
                ph = (t * 1.3 + j / 5) % 1
                line(c, [(560, 1180 + ph * 60), (600, 1240 + ph * 40)], f"sp{j}", 2, (1, 1, 1), alpha=0.6 * flood)
    n = 1 + int(prog(t, 0.2, 5.2) * 7)
    cairn(c, n)
    if t < 5.8:
        girl(c, 470, 1220, 1.5, outfit="snow", pack=True, sit=True, crouch=True, look=0.7, head_down=6, mouth="flat",
             key="p4")
    else:
        girl(c, 440, 1250, 1.5, outfit="snow", pack=True, look=0.6, mouth="flat", key="p4")


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
    """黄昏，河边一张小木桌，拉她过河的孩子、递碗的老奶奶、帮她扣正草帽的大叔，碗一只只传过来。"""
    plain_bg(c, t, dusk=1.0)
    river(c, t, 1000, 1080, col=hexc("c88a7a"))
    with keep():
        glow(c, 540, 1000, 360, WARM, 0.45)
        line(c, [(540, 760), (540, 900)], "lmp", 3, hexc("3a3a3a"))
        circle(c, 540, 905, 12, hexc("fff0b8"))
    shape(c, rect(250, 1150, 580, 18), hexc("8c5a3c"), "tbl", lw=2.4)
    for x in (280, 800):
        line(c, [(x, 1168), (x, 1250)], f"tl{x}", 6, hexc("6a4a32"))
    local(c, 300, 1150, 1.3, "kid7", hexc("9fc5e8"), hexc("2f2a28"), "short", sit=True, legs=False, look=0.6, mouth="laugh")
    local(c, 430, 1150, 1.4, "gma", hexc("6a5a7a"), hexc("2f2a28"), "bun", sit=True, legs=False, age=1.0, look=0.4,
          mouth="smile")
    girl(c, 640, 1150, 1.45, outfit="folk", hat=False, pack=False, sit=True, legs=False, look=-0.3, mouth="laugh", key="p7")
    local(c, 780, 1150, 1.4, "uncle7", hexc("8a5a3a"), hexc("2f2a28"), "short", sit=True, legs=False, look=-0.5, mouth="smile")
    with keep():                                                   # 碗一只只传过去
        for j in range(2):
            u = ((t * 0.5 + j * 0.5) % 1)
            bx = lerp(330, 760, u)
            shape(c, ell(bx, 1146, 30, 10, 14, 0, math.pi), (0.97, 0.96, 0.93), f"bw{j}", lw=2)
        for k, x in enumerate((360, 480, 600, 720)):
            shape(c, ell(x, 1146, 26, 8, 14, 0, math.pi), (0.97, 0.96, 0.93), f"bs{k}", lw=1.6)


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
    if k == 0:                                                     # 大河流进海里
        vgrad(c, 0, 900, [(0, hexc("8fc4ea")), (1, hexc("f2f0e4"))])
        shape(c, rect(-40, 880, W + 80, 1100), SEA_A, "sea8", lw=2)
        shape(c, [(-40, 1700), (-40, 1150), (300, 1080), (700, 1040), (1120, 1000), (1120, 1700)], hexc("e8d8b0"), "sand8",
              lw=2.4)
        shape(c, [(-40, 1500), (-40, 1380), (400, 1180), (600, 1060), (720, 1050), (560, 1200), (200, 1500)],
              hexc("6aa0c8"), "riv8", lw=2)
        waves(c, u, 920, 1020, "w8", n=3)
        girl(c, lerp(760, 880, prog(u, 0, 3.1)), 1240, 1.4, outfit="sea_white", pack=True, look=0.6, walk=u * 6, key="p8")
    elif k == 1:                                                   # 小岛：岛民把不多的鱼和水果分着搬上岸
        sea_bg(c, u)
        shape(c, [(-40, 1700), (-40, 1100), (200, 1020), (520, 1000), (720, 1060), (900, 1180), (1120, 1220), (1120, 1700)],
              hexc("e8d8b0"), "isl", lw=2.4)
        sailboat(c, 860, 1180, 0.8, "fb", sail=0.0)
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
        sailboat(c, 780, 1260, 1.0, "sb", sail=sail, rock_=0.03 * math.sin(u * 2))
        untie = ease_io(prog(u, 0.2, 0.8))
        with keep():
            line(c, [(520, 1190), (lerp(660, 600, untie), lerp(1250, 1300, untie))], "rope", 3, hexc("c8b088"))
        girl(c, 700, 1240, 1.4, outfit="sea_white", pack=True, look=-0.6, arms=[(-40, -60), (24, -78)], key="p8")
    elif k == 3:                                                   # 扬帆出海
        sea_bg(c, u)
        go = ease_in(prog(u, 0.0, 3.1))
        x = lerp(560, 760, go)
        y = lerp(1240, 1000, go)
        s = lerp(1.0, 0.5, go)
        sailboat(c, x, y, s, "sb", rock_=0.03 * math.sin(u * 2))
        girl(c, x - 40 * s, y - 14 * s, 1.3 * s, outfit="sea_white", pack=False, sit=True, legs=False, look=0.5, key="p8s")
    else:                                                          # 一场未知而远大的冒险：一望无际的海，远处的云
        sea_bg(c, u, horizon=980)
        for j in range(4):
            cloud(c, 120 + j * 280 + u * 20, 760 + (j % 2) * 60, 2.0, f"fc{j}", a=0.9)
        with keep():
            glow(c, 900, 900, 380, hexc("fff0c8"), 0.4)
        go = prog(u, 0.0, 3.1)
        x, y = lerp(420, 640, go), lerp(1180, 1060, go)
        sailboat(c, x, y, lerp(0.55, 0.35, go), "sbfar", rock_=0.03 * math.sin(u * 2))


def boat_close(c, t, dusk=0.0, storm=0.0, look=0.5, eyes=False, mouth="smile", speed=0.0, lean=0.0, balance=0.0):
    sea_bg(c, t, dusk=dusk, storm=storm, horizon=860)
    rock_ = 0.04 * math.sin(t * 1.6) * (1 + 3 * storm)
    bx = 540
    sailboat(c, bx, 1240, 1.6, "bc", sail=1.0, rock_=rock_)
    c.save()
    c.translate(bx, 1240)
    c.rotate(rock_)
    girl(c, -90 + lean, -20, 1.5, outfit="sea_white", pack=False, sit=True, legs=False, look=look, eyes_closed=eyes,
         mouth=mouth, tilt=(0.12 if eyes else 0.0) - rock_ * balance, key="bcg")
    c.restore()
    if speed > 0:                                                  # 船尾拖出的白浪
        with keep():
            for j in range(4):
                xx = bx - 260 - j * 120 - (t * 400 * speed) % 120
                line(c, [(xx, 1270 + j * 6), (xx - 120, 1262 + j * 10)], f"wk{j}", 4 - j * 0.6, (1, 1, 1),
                     alpha=0.7 * (1 - j / 4))


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
                circle(c, 760 + math.cos(a) * ph * 200, 1220 - math.sin(a) * ph * 160, 6, (1, 1, 1), a=1 - ph / 0.4)


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
        for j in range(9):                                         # 平静的海面上一条月光
            y = 930 + j * 34
            hw = 30 + j * 12 + 6 * math.sin(u * 1.4 + j)
            line(c, [(380 - hw, y), (380 + hw, y)], f"mp{j}", 3, hexc("fff0c8"), alpha=0.55 * night * (1 - j / 12))
        for j in range(3):                                         # 几乎不动的浪
            yy = 1120 + j * 160
            line(c, [(-40, yy), (W + 40, yy + 4)], f"cw{j}", 1.6, (1, 1, 1), alpha=0.18)
    sailboat(c, 640, 1200, 0.5, "sb13n", sail=0.2, rock_=0.01 * math.sin(u))
    girl(c, 615, 1193, 0.54, outfit="sea_white", pack=False, sit=True, legs=False, look=-0.6, eyes_closed=True,
         mouth="smile", key="p13n")


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
    "sea": (lambda: k13, 2.0), "plain": (lambda: k07, 2.0), "plateau": (lambda: k04, 8.0),
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
    flips = prog(t, 3.1, 6.2) * (len(FLIP_ORDER) - 1)
    idx = min(int(flips), len(FLIP_ORDER) - 1)
    frac = flips - idx if idx < len(FLIP_ORDER) - 1 else 0.0
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
        else:                                                      # 一页一页往回翻：左页翻起来，落到右页上
            _page_img(c, img(idx + 2) if frac > 0 else img(idx + 1), *pl)
            _page_img(c, img(idx), *pr)
            if frac > 0:
                wv = math.cos(frac * math.pi)
                with keep():
                    if wv > 0:
                        page_paper(c, sx - bw * wv, by, bw * wv, bh, "leafL")
                        _page_img(c, img(idx + 1), sx - (bw - 30) * wv, by + 40, (bw - 60) * wv, bh - 80)
                    else:
                        page_paper(c, sx, by, -bw * wv, bh, "leafR")
                        _page_img(c, img(idx + 1), sx + 30 * -wv, by + 40, (bw - 60) * -wv, bh - 80)
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
        rock(c, lerp(560, 590, place), lerp(1080, 1024, place), 44, 28, "mypb15", col=hexc("c8c0b4"), sharp=False)
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
    push = ease_io(prog(u, 0.0, 3.1))                              # 镜头留在书和石头上
    with cam(c, lerp(560, 575, push), lerp(980, 1030, push), lerp(1.0, 2.6, push)):
        room15(c, t)
        closed_book(c, 570, 1050, 1.0, "cb")
        rock(c, 590, 1024, 44, 28, "mypb15", col=hexc("c8c0b4"), sharp=False)
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

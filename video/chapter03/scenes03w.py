"""第三章 · 从游客到旅人（第六稿：一路走下去）—— 镜头一直跟着她走；“以前 / 后来”同一个机位拍两遍。"""
import math
import random

import cairo

from scenes03 import (GRAN, SKIN_L, RED, cobbles, d05_tourist, d06_checkin, d08_wider, d10_town, d11_costume,
                      d14_shoot, guidebook, landmark, local, old_town, phone_at, postcard, produce, pull,
                      street_lamp, town_bg)
from scenes03j import courtyard
from draw import *  # noqa: F401,F403
from engine import book_intro, book_outro

TAN = hexc("ecc3a0")          # 后来晒黑了一点


# ================================================================ 通用
def pan(c, t, fa, fb, tb, d=0.8):
    """镜头横移：她走出左边的画面，下一幕从右边接上。fb 的本地时间从 tb 开始算。"""
    if t < tb:
        fa(c, t)
        return
    if t >= tb + d:
        fb(c, t - tb)
        return
    e = ease_io((t - tb) / d)
    for fn, ox, lt in ((fa, -W * e, t), (fb, W * (1 - e), t - tb)):
        c.save()
        c.translate(ox, 0)
        c.rectangle(0 if ox <= 0 else 0, -200, W, H + 400)
        c.clip()
        fn(c, lt)
        c.restore()


def xfade(c, t, fa, fb, tb, d=0.5):
    """同一个机位：前后两个时间叠化。"""
    if t < tb:
        fa(c, t)
        return
    if t >= tb + d:
        fb(c, t - tb)
        return
    fa(c, t)
    with group_alpha(c, ease_io((t - tb) / d)):
        fb(c, t - tb)


def bubble(c, x, y, s, a=1.0, key="bb", w=None, size=40):
    """对白气泡。"""
    if a <= 0.01:
        return
    w = w or (len(s) * size * 0.95 + 60)
    with keep():
        shape(c, rrect(x - w / 2, y - 50, w, 84, 30) + [], (1, 1, 1), key, lw=2.2, alpha=a)
        shape(c, [(x - 20, y + 32), (x + 6, y + 32), (x - 26, y + 66)], (1, 1, 1), key + "t", lw=2, alpha=a)
        text(c, s, x, y + 6, size, INK, a=a)


def hat_on_pack(c, x, y, s, key):
    """背影：草帽挂在背包侧边。"""
    c.save()
    c.translate(x + 30 * s, y - 72 * s)
    c.rotate(0.35)
    hat_item(c, 0, 0, s * 0.5, key)
    c.restore()


def sneakers_illus(c, cx, cy):
    """章节页小插画：一双走旧了的帆布鞋。"""
    with keep():
        for i, dx in enumerate((-40, 40)):
            x = cx + dx
            shape(c, [(x - 34, cy + 20), (x - 30, cy - 10), (x - 6, cy - 22), (x + 14, cy - 6), (x + 40, cy + 2),
                      (x + 42, cy + 20)], hexc("e8e0cf"), f"sn{i}", lw=2.4)
            shape(c, rect(x - 36, cy + 16, 80, 10), hexc("b9a587"), f"sns{i}", lw=1.8)
            for k in range(3):
                line(c, [(x - 16 + k * 8, cy - 14 + k * 4), (x - 4 + k * 8, cy - 18 + k * 4)], f"snl{i}{k}", 1.6, RED)
            circle(c, x + 24, cy + 4, 3, hexc("a8a090"))


def intro(c, t):
    book_intro(c, t, "第三章", "从游客到旅人", sneakers_illus)


# ================================================================ 1 车站
def w01(c, t):
    """车站的自动门打开，她拉着箱子走出来，深吸一口气，帽檐压得很低。"""
    vgrad(c, 0, 760, [(0, hexc("c9d4dc")), (1, hexc("e6e8e4"))])
    shape(c, rect(-20, 220, W + 40, 560), hexc("cfcac0"), "stw", lw=3)       # 站房
    shape(c, rect(-20, 200, W + 40, 40), hexc("9aa0a8"), "stroof", lw=2.4)
    for i in range(6):
        shape(c, rect(40 + i * 175, 300, 120, 160), hexc("b7c6d2"), f"stwin{i}", lw=2)
    with keep():
        shape(c, rect(330, 250, 420, 70), hexc("2f6a4a"), "exit", lw=2.4)
        text(c, "出 站 口", 540, 300, 44, (1, 1, 1))
    op = ease_io(prog(t, 0.2, 0.8)) * (1 - ease_io(prog(t, 2.6, 0.8)))
    shape(c, rect(340, 500, 400, 280), hexc("4a4f58"), "door_in", lw=2.4)
    with keep():                                                   # 两扇玻璃门向两边滑开
        for sg in (-1, 1):
            x0 = 540 + sg * (100 + 200 * op) - 100
            shape(c, rect(x0, 500, 200, 280), hexc("cfe4f2") + (0.75,), f"gd{sg}", lw=2.4)
    shape(c, rect(-20, 780, W + 40, 1200), hexc("cfc6b4"), "square", lw=3)
    for i in range(10):
        line(c, [(-20, 800 + i * i * 9), (W + 20, 800 + i * i * 9)], f"sq{i}", 1.4, hexc("bdb39f"), alpha=0.6)
    for i in range(8):
        line(c, [(540 + (i - 3.5) * 60, 780), (540 + (i - 3.5) * 300, 1900)], f"sqv{i}", 1.4, hexc("bdb39f"), alpha=0.5)
    r = random.Random(11)
    for i in range(6):                                             # 匆匆走过的路人
        x = (r.uniform(0, 1200) + t * (90 if i % 2 else -110)) % 1300 - 100
        silhouette(c, x, 880 + r.uniform(0, 80), 1.0 + r.uniform(0, 0.2), f"sp{i}", walk=t * 7 + i, a=0.55)
    for i in range(4):                                             # 鸽子
        bx = 160 + i * 230 + math.sin(t * 2 + i) * 8
        shape(c, ell(bx, 1180, 18, 10, 10), hexc("9aa0a8"), f"pg{i}", lw=1.6)
        shape(c, ell(bx + 14, 1168, 7, 7, 8), hexc("9aa0a8"), f"pgh{i}", lw=1.4)
    # 走出来 → 站住深吸一口气 → 往右走出画面
    out = ease_out(prog(t, 0.6, 2.4))
    breath = math.sin(prog(t, 3.2, 2.0) * math.pi)
    go = ease_in(prog(t, 5.6, 2.4))
    x = 540 + go * 700
    y = lerp(800, 1220, out)
    s = lerp(0.9, 1.6, out)
    walking = out < 1 or go > 0
    pull(c, x, y, s, "g01", walk=t * 7 if walking else None, mouth="o" if breath > 0.5 else "flat",
         head_down=6 * (1 - breath), look_up=0.4 * breath, eyes_closed=breath > 0.6, look=0.9 if go > 0 else 0.2)


# ================================================================ 2 台阶 / 夜路
def stairs(c, t):
    """长台阶：箱子的一个轮子卡坏了，她抱起箱子一级一级往上拖，停下来擦汗。"""
    vgrad(c, 0, 900, [(0, hexc("c9d1d8")), (1, hexc("e4e5e1"))])
    old_town(c, t, 760, "sto", hs=0.9)
    cobbles(c, 1340, 1500, "stc")
    run_, rise, n = 100, 62, 10
    x0, y0 = 360, 1340
    pts = [(-40, y0), (x0, y0)]
    for k in range(n):
        pts += [(x0 + k * run_, y0 - (k + 1) * rise), (x0 + (k + 1) * run_, y0 - (k + 1) * rise)]
    pts += [(W + 40, y0 - n * rise), (W + 40, 1900), (-40, 1900)]
    shape(c, pts, hexc("bdb4a4"), "stair", lw=3)
    for k in range(n):
        line(c, [(x0 + k * run_, y0 - (k + 1) * rise), (x0 + (k + 1) * run_, y0 - (k + 1) * rise)], f"stl{k}", 4,
             hexc("8f877a"))
    line(c, [(x0 - 20, y0 - 160), (x0 + n * run_, y0 - n * rise - 160)], "rail", 4, hexc("6a6560"))
    for k in range(0, n + 1, 3):
        line(c, [(x0 + k * run_, y0 - k * rise), (x0 + k * run_, y0 - k * rise - 160)], f"railp{k}", 3, hexc("6a6560"))
    # 0–1.1：拉到台阶前，轮子“啪”地掉了
    if t < 1.6:
        x = lerp(60, 300, ease_out(prog(t, 0.0, 1.1)))
        pull(c, x, y0, 1.5, "g02", walk=t * 7 if t < 1.1 else None, mouth="o" if t > 1.1 else "flat",
             head_down=8 if t > 1.1 else 4, look=-0.6 if t > 1.1 else 0.9, bump=t)
        u = prog(t, 1.1, 0.5)
        if u > 0:
            with keep():
                wx = 300 - 58 * 1.5 + 120 * u
                circle(c, wx, y0 - 4 - 30 * math.sin(u * math.pi), 9, hexc("3a3a3a"))
        return
    # 1.6–：抱起箱子往上走，中途停下擦汗
    rest = 3.5 < t < 4.6
    climb = ease_io(prog(t, 1.6, 1.9)) * 2.0 + ease_io(prog(t, 4.6, 1.4)) * 1.6
    x = x0 + 30 + climb * run_
    y = y0 - max(1, math.ceil(climb + 0.4)) * rise
    with keep():                                                   # 掉了轮子的箱子
        circle(c, 300 - 58 * 1.5 + 120, y0 - 4, 9, hexc("3a3a3a"))
    if rest:
        suitcase(c, x - 70, y, 0.85, "su02", handle=0.0)
        girl(c, x, y, 1.5, hat=True, mouth="o", look=-0.3, arms=[(-24, -78), (-6, -196)], key="g02b")
        with keep():
            for j in range(3):
                ph = (t * 2 + j / 3) % 1
                shape(c, ell(x + 34 + j * 14, y - 250 + ph * 40, 5, 8, 8), hexc("9fc5e8"), f"sw{j}", lw=1, alpha=1 - ph)
    else:
        lift = 6 * abs(math.sin(t * 6))
        girl(c, x, y - lift * 0.3, 1.5, hat=True, mouth="sad", look=0.6, head_down=6, walk=t * 6,
             arms=[(-10, -100), (40, -100)], key="g02b")
        suitcase(c, x + 26, y - 40 - lift, 0.62, "su02", handle=0.0, tilt=-0.2)


def night(c, t):
    """天黑了：路灯一盏亮一盏灭，身后有脚步声；进旅馆，锁门，背靠着门松一口气。"""
    if t < 3.4:
        fill_all(c, hexc("1d2235"))
        old_town(c, t, 980, "ngt", dark=True, hs=1.1)
        shape(c, rect(-20, 980, W + 40, 900), hexc("2e3242"), "ngg", lw=3)
        for i, x in enumerate((120, 480, 840)):
            flick = 1.0 if i != 1 else (0.15 + 0.85 * (math.sin(t * 13) > -0.2) * (math.sin(t * 3.1) > -0.6))
            street_lamp(c, x, 1000, f"nl{i}", on=flick)
        with keep():                                               # 旅馆的门和小招牌
            shape(c, rect(880, 780, 160, 220), hexc("6b4a32"), "inn", lw=3)
            glow(c, 960, 740, 120, hexc("ffd98a"), 0.6)
            shape(c, rect(880, 710, 160, 50), hexc("f2d98a"), "innsign", lw=2)
            text(c, "旅 馆", 960, 746, 30, INK)
        x = lerp(80, 900, ease_io(prog(t, 0.0, 3.3)))
        sx = lerp(-260, 420, ease_io(prog(t, 0.0, 3.3)))          # 身后的影子
        with grade(dark=0.2):
            c.save()
            c.translate(sx, 1240)
            c.scale(1.2, 1.7)
            silhouette(c, 0, 0, 1.0, "follow", col=hexc("0d0f18"), walk=t * 7, a=0.55)
            c.restore()
        back = math.sin(t * 2.6) > 0.4
        girl(c, x, 1240, 1.5, hat=True, walk=t * 11, run=t > 1.6, look=-1.0 if back else 0.8, mouth="flat",
             arms=[(-24, -78), (22, -100)], key="g02n")
        phone_at(c, x + 22 * 1.5, 1240 - 104 * 1.5, 1.1, "nph", glow_a=0.5)
        return
    # 房间里：背靠着门
    lt = t - 3.4
    fill_all(c, hexc("3a3550"))
    with keep():
        glow(c, 300, 500, 300, hexc("ffd98a"), 0.35)
    shape(c, rect(380, 420, 320, 820), hexc("6b4a32"), "rdoor", lw=3)
    with keep():
        line(c, [(600, 640), (650, 600)], "chain", 4, hexc("c9c4b8"))
        circle(c, 650, 600, 6, hexc("c9c4b8"))
    shape(c, rect(-20, 1240, W + 40, 700), hexc("4a4458"), "rfl", lw=3)
    ex = math.sin(prog(lt, 0.4, 1.2) * math.pi)
    girl(c, 540, 1240, 1.7, hat=True, mouth="o" if ex > 0.4 else "flat", eyes_closed=ex > 0.3, look_up=0.3 * ex,
         arms=[(-30, -80), (30, -80)], key="g02r")
    if ex > 0.2:
        with keep():
            for j in range(3):
                line(c, [(600 + j * 20, 1240 - 230 * 1.7 + j * 6), (640 + j * 24, 1240 - 240 * 1.7 + j * 8)], f"ex{j}", 3,
                     (1, 1, 1), alpha=ex * 0.6)


def w02(c, t):
    pan(c, t, stairs, night, 5.4)


# ================================================================ 3 一个人吃饭 / 看风景 / 陌生的城市
def noodle(c, t):
    """小面馆的窗外看进去：她一个人低头吃面，邻桌的人看了她一眼。"""
    fill_all(c, hexc("cfc6b4"))
    shape(c, rect(-20, 140, W + 40, 1120), hexc("d9c4a8"), "nw", lw=3)
    with keep():
        shape(c, rect(260, 180, 560, 90), hexc("8c5a3c"), "nsign", lw=2.4)
        shape(c, ell(540, 236, 40, 22, 16, 0, math.pi), (1, 1, 1), "nbowl", lw=2)
        for k in range(3):
            line(c, [(520 + k * 20, 214), (516 + k * 20, 196)], f"nst{k}", 2, (1, 1, 1))
    shape(c, rect(110, 330, 860, 760), hexc("f3dfb8"), "nwin", lw=4)                 # 暖黄的窗
    with keep():
        glow(c, 540, 600, 420, hexc("ffe2a0"), 0.5)
    line(c, [(540, 330), (540, 400)], "nlampw", 2)
    shape(c, [(500, 400), (580, 400), (600, 440), (480, 440)], hexc("c98d4a"), "nlamp", lw=2)
    # 邻桌：两个人
    shape(c, rect(620, 860, 300, 18), hexc("8c5a3c"), "ntab2", lw=2)
    look = prog(t, 1.2, 0.4) * (1 - prog(t, 2.4, 0.4))
    for i, (x, col) in enumerate(((680, "8fb39a"), (860, "c98d72"))):
        local(c, x, 860, 1.05, f"nb{i}", hexc(col), hexc("2f2a28"), "short", sit=True, legs=False,
              look=-0.9 * look if i == 0 else -0.6 * look, mouth="smile")
    # 她
    shape(c, rect(170, 900, 340, 18), hexc("8c5a3c"), "ntab", lw=2)
    eat = math.sin(t * 5)
    girl(c, 300, 900, 1.1, sit=True, legs=False, hat=True, head_down=8, look=0.2, mouth="o" if eat > 0.3 else "flat",
         arms=[(-20, -70), (26, -96 + 14 * eat)], key="g03n")
    with keep():
        shape(c, ell(330, 890, 50, 16, 16, 0, math.pi), hexc("f8f6f0"), "nb", lw=2)
        line(c, [(330, 1000 - 104 * 1.1 + 14 * eat), (346, 880)], "chop", 2.4, hexc("8c5a3c"))
        for k in range(3):
            ph = (t * 0.7 + k / 3) % 1
            line(c, [(310 + k * 18, 870 - ph * 60), (306 + k * 18, 850 - ph * 60)], f"nsm{k}", 2, (1, 1, 1), alpha=0.6 * (1 - ph))
    for k in range(1, 3):                                          # 窗框
        line(c, [(110 + k * 287, 330), (110 + k * 287, 1090)], f"nwm{k}", 5, hexc("8c5a3c"))
    shape(c, rect(-20, 1260, W + 40, 700), hexc("b7ae9c"), "nside", lw=3)


def breakwater(c, t):
    """海边防波堤上，一个人坐着看浪。"""
    vgrad(c, 0, 800, [(0, hexc("b9cbd8")), (1, hexc("e6edf0"))])
    shape(c, rect(-20, 700, W + 40, 700), hexc("6f95b0"), "sea", lw=3)
    for k in range(5):
        y = 760 + k * 60
        off = math.sin(t * 1.5 + k) * 30
        line(c, [(-20, y), (300 + off, y + 8), (700 + off, y), (W + 20, y + 8)], f"wv{k}", 2, (1, 1, 1), alpha=0.45)
    for i in range(8):
        x = -20 + i * 150
        shape(c, [(x, 1240), (x + 140, 1240), (x + 120, 1110), (x + 20, 1110)], hexc("b7b2a7"), f"bw{i}", lw=2.4)
    sp = max(0.0, math.sin(t * 2.0 - 0.5))
    with keep():
        for k in range(6):
            shape(c, ell(760 + k * 34, 1080 - sp * 120 - k * 8, 18, 12, 10), (1, 1, 1), f"spl{k}", lw=1, alpha=sp * 0.8)
    for i in range(2):
        bx = (300 + i * 260 + t * 30) % 1200 - 60
        line(c, [(bx - 16, 380 - 6), (bx, 380), (bx + 16, 380 - 6)], f"gull{i}", 2.4, hexc("4a4f58"))
    girl(c, 480, 1110, 1.6, view="back", sit=True, hat=True, key="g03b")


def subway(c, t):
    """地铁换乘通道：看不懂的线路图前，她站在中间转圈。"""
    fill_all(c, hexc("e4e5e1"))
    for i in range(14):
        for j in range(12):
            shape(c, rect(i * 80 - 20, j * 80 + 40, 76, 76), hexc("eef0ee"), f"tl{i}_{j}", lw=0.8, amp=0.2)
    with keep():
        shape(c, rect(110, 180, 860, 520), (1, 1, 1), "smap", lw=3)
        cols = ["c9473b", "3f6fb5", "4f9a5c", "e8c040", "8d6a9f", "e8743a"]
        r = random.Random(4)
        for i, col in enumerate(cols):
            pts = []
            y = 220 + i * 70
            x = 140
            while x < 950:
                pts.append((x, y))
                x += r.uniform(60, 130)
                y = clamp(y + r.uniform(-90, 90), 210, 670)
            line(c, pts, f"ml{i}", 7, hexc(col))
            for p in pts:
                circle(c, p[0], p[1], 8, (1, 1, 1))
        for k, (x, d) in enumerate(((200, 1), (520, -1), (860, 1))):          # 方向互相矛盾的指示牌
            shape(c, rect(x - 90, 760, 180, 60), hexc("2f4a6a"), f"dir{k}", lw=2)
            text(c, "→" if d > 0 else "←", x + d * 50, 802, 34, (1, 1, 1))
            for j in range(3):
                line(c, [(x - 70 + j * 24, 790), (x - 56 + j * 24, 790)], f"dirt{k}{j}", 3, (1, 1, 1))
    shape(c, rect(-20, 1100, W + 40, 900), hexc("c9c6bc"), "sfl", lw=3)
    r = random.Random(9)
    for i in range(7):
        x = (r.uniform(0, 1200) + t * (260 if i % 2 else -240)) % 1300 - 100
        silhouette(c, x, 1150 + r.uniform(0, 60), 1.3, f"rush{i}", walk=t * 10 + i, a=0.5)
    spin = math.cos(t * 3.0)
    girl(c, 540, 1240, 1.6, hat=True, look=spin, mouth="o", sx=1.0 if spin > -0.3 else -1.0,
         arms=[(-24, -78), (30, -120)], key="g03s")
    phone_at(c, 540 + 30 * 1.6, 1240 - 124 * 1.6, 1.1, "sph")


def w03(c, t):
    pan(c, t, noodle, lambda cc, tt: pan(cc, tt, breakwater, subway, 3.3), 3.3)


# ================================================================ 4 / 9 同一家餐厅
def restaurant_bg(c, t, look=0.0, empty_window=False):
    fill_all(c, hexc("e6d6b8"))
    glow(c, 540, 300, 700, hexc("ffe2a0"), 0.5)
    shape(c, rect(560, 220, 400, 300), hexc("bfd9e8"), "rwin", lw=3)                 # 窗
    line(c, [(760, 220), (760, 520)], "rwinm", 4, hexc("8c5a3c"))
    for i in range(4):
        line(c, [(160 + i * 260, 0), (160 + i * 260, 120)], f"rl{i}", 2)
        shape(c, [(120 + i * 260, 120), (200 + i * 260, 120), (220 + i * 260, 160), (100 + i * 260, 160)],
              hexc("c98d4a"), f"rlamp{i}", lw=2)
    # 后面的桌子：两人桌、四人桌
    tables = [(250, 800, [(170, "8fb39a"), (330, "c98d72")]),
              (720, 820, [(580, "7d6a8f"), (680, "e8c040"), (780, "6b7a8a"), (880, "f2a6a0")])]
    for ti, (tx, ty, people) in enumerate(tables):
        for pi, (px, col) in enumerate(people):
            local(c, px, ty, 1.1, f"rp{ti}{pi}", hexc(col), hexc("2f2a28"), "short", sit=True, legs=False,
                  look=look * (-1 if px > 540 else 1) * 0.9 + (1 - look) * (0.6 if pi % 2 == 0 else -0.6),
                  mouth="smile")
        w_ = 260 if ti == 0 else 400
        shape(c, rect(tx - w_ / 2, ty, w_, 18), hexc("8c5a3c"), f"rt{ti}", lw=2)
        for k in range(len(people)):
            shape(c, ell(tx - w_ / 2 + 50 + k * (w_ - 100) / max(1, len(people) - 1), ty - 6, 24, 8, 12), hexc("f8f6f0"),
                  f"rd{ti}{k}", lw=1.4)
    shape(c, rect(-20, 1000, W + 40, 900), hexc("c9b59a"), "rfl", lw=3)
    for i in range(8):
        line(c, [(-20, 1030 + i * i * 9), (W + 20, 1030 + i * i * 9)], f"rfb{i}", 1.4, hexc("b39f86"), alpha=0.6)


def waiter(c, t, x=800, one=True):
    local(c, x, 1240, 1.6, "waiter", hexc("f4f2ec"), hexc("3a3a3a"), "short", look=-0.8, mouth="smile",
          arms=[(-40, -170), (24, -78)] if one else [(-24, -78), (24, -78)])
    with keep():
        shape(c, [(x - 36, 1240 - 130 * 1.6), (x + 36, 1240 - 130 * 1.6), (x + 40, 1240 - 40 * 1.6), (x - 40, 1240 - 40 * 1.6)],
              hexc("2f4a6a"), "wapron", lw=2)
        if one:                                                    # 竖起一根手指
            line(c, [(x - 40 * 1.6, 1240 - 170 * 1.6), (x - 40 * 1.6, 1240 - 190 * 1.6)], "wfinger", 5, SKIN_L)


def steps_outside(c, t):
    """打包带走，坐在门口台阶上吃。"""
    vgrad(c, 0, 900, [(0, hexc("c9d1d8")), (1, hexc("e4e5e1"))])
    shape(c, rect(-20, 200, W + 40, 900), hexc("d9c4a8"), "sow", lw=3)
    with keep():
        shape(c, rect(560, 340, 400, 660), hexc("f3dfb8"), "sod", lw=3)
        glow(c, 760, 600, 260, hexc("ffe2a0"), 0.4)
    for k in range(3):
        shape(c, rect(-20 + k * 30, 1000 + k * 60, W + 40, 60), hexc("bdb4a4"), f"sost{k}", lw=2.4)
    shape(c, rect(-20, 1180, W + 40, 800), hexc("a39a8c"), "sog", lw=3)
    eat = math.sin(t * 4)
    girl(c, 360, 1060, 1.6, sit=True, crouch=True, hat=True, head_down=10, look=0.2, mouth="o" if eat > 0.3 else "flat",
         arms=[(-20, -60), (24, -90 + 12 * eat)], key="g04s")
    with keep():
        shape(c, rect(330, 1060 - 70 * 1.6 + 52 * 1.6 - 20, 70, 44), hexc("f8f6f0"), "box", lw=2)
        line(c, [(360 + 24 * 1.6, 1060 - 90 * 1.6 + 52 * 1.6 + 12 * eat), (370, 1060 - 30)], "chop4", 2.4, hexc("8c5a3c"))
    for i in range(3):
        silhouette(c, (200 + i * 400 + t * 80) % 1200 - 60, 1300, 1.2, f"sop{i}", walk=t * 6 + i, a=0.4)


def w04(c, t):
    if t < 4.4:
        look = ease_io(prog(t, 1.6, 0.6))
        restaurant_bg(c, t, look=look)
        waiter(c, t, one=t > 0.4)
        bubble(c, 760, 600, "一位？", a=clamp((t - 0.5) * 3) * (1 - prog(t, 3.0, 0.4)), key="b04")
        down = ease_io(prog(t, 2.4, 0.8))
        girl(c, 280, 1240, 1.7, hat=True, mouth="flat", look=0.5, head_down=lerp(2, 12, down),
             arms=[(-24, -78), (lerp(24, 10, down), lerp(-78, -236, down))] if down < 1 else [(-24, -78), (24, -78)],
             key="g04")
        return
    steps_outside(c, t - 4.4)


def w09(c, t):
    """同一家餐厅、同一个机位：她笑着比“1”，坐到窗边，点了一桌菜，和老板聊天。"""
    if t < 2.6:
        restaurant_bg(c, t, look=0.0)
        waiter(c, t, one=True)
        bubble(c, 760, 600, "一位？", a=clamp((t - 0.3) * 3) * (1 - prog(t, 1.4, 0.4)), key="b09")
        girl(c, 280, 1240, 1.7, hat=True, mouth="laugh", look=0.5, look_up=0.2,
             arms=[(-24, -78), (40, -190)] if t > 0.9 else [(-24, -78), (24, -78)], key="g09")
        if t > 0.9:
            with keep():
                line(c, [(280 + 40 * 1.7, 1240 - 190 * 1.7), (280 + 40 * 1.7, 1240 - 212 * 1.7)], "one", 5, SKIN)
        return
    lt = t - 2.6
    restaurant_bg(c, t, look=0.0)
    # 窗边最好的位置，一桌菜
    TY = 1080
    cheers = lt > 2.6
    girl(c, 380, TY, 1.7, sit=True, legs=False, hat=False, mouth="laugh", look=0.6,
         arms=[(-20, -70), (40, -150)] if cheers else [(-20, -70), (30 + 8 * math.sin(lt * 7), -86)], key="g09t")
    shape(c, rect(130, TY, 520, 24), hexc("8c5a3c"), "wtab", lw=3)
    for x in (150, 620):
        shape(c, rect(x, TY + 24, 16, 150), hexc("7a4d33"), f"wtl{x}", lw=2)
    hat_item(c, 230, TY, 0.9, "g09hat")
    cols = ["d9653a", "6fa860", "e8c040", "b5533a"]
    for i in range(4):
        x = 300 + i * 100
        shape(c, ell(x, TY - 8, 44, 14, 14), hexc("f8f6f0"), f"wd{i}", lw=2, amp=0.4)
        shape(c, ell(x, TY - 12, 32, 8, 12), hexc(cols[i]), f"wf{i}", lw=1.4, amp=0.3)
        line(c, [(x - 6, TY - 24), (x - 12 + math.sin(lt * 2 + i) * 6, TY - 56), (x - 2, TY - 86)], f"ws{i}", 2,
             (1, 1, 1), alpha=0.6)
    local(c, 820, 1240, 1.6, "boss", hexc("f4f2ec"), hexc("3a3a3a"), "short", look=-0.8, mouth="laugh",
          arms=[(-40, -130 + 10 * math.sin(lt * 6)), (24, -78)])
    with keep():
        shape(c, [(820 - 36, 1240 - 130 * 1.6), (820 + 36, 1240 - 130 * 1.6), (820 + 40, 1240 - 40 * 1.6),
                  (820 - 40, 1240 - 40 * 1.6)], hexc("c9473b"), "bapron", lw=2)
    for k in range(3):                                             # 聊天
        a = math.sin(prog(lt, 0.4 + k * 0.9, 1.0) * math.pi)
        if a > 0:
            x, y = (520, 720) if k % 2 == 0 else (760, 780)
            with keep():
                for j in range(3):
                    circle(c, x - 20 + j * 20, y, 6, INK, a=a * 0.7)
    if cheers:
        with keep():
            shape(c, [(380 + 56, TY - 214), (380 + 84, TY - 214), (380 + 80, TY - 180), (380 + 60, TY - 180)],
                  hexc("f2d98a"), "cup", lw=1.8)


# ================================================================ 5–7 游客
def w05(c, t):
    """景区门口排长队：她把攻略本举在头顶挡太阳。"""
    vgrad(c, 0, 900, [(0, hexc("8fc3e3")), (1, hexc("e9f2f6"))])
    with keep():
        glow(c, 860, 160, 300, hexc("fff3b0"), 0.8)
        circle(c, 860, 160, 60, hexc("fff0b0"))
    landmark(c, 540, 860, 1.4, "gate", "lmg")
    shape(c, rect(-20, 860, W + 40, 900), hexc("d6cbb2"), "plaza", lw=3)
    for i in range(8):
        line(c, [(-10, 890 + i * i * 9), (W + 10, 890 + i * i * 9)], f"pz{i}", 1.6, hexc("c0b59b"), alpha=0.6)
    r = random.Random(5)
    for i in range(16):
        x = 120 + (i % 8) * 110 + r.uniform(-20, 20) + math.sin(t + i) * 4
        y = 960 + (i // 8) * 60
        silhouette(c, x, y, 1.0, f"q{i}", a=0.7, col=[hexc("8d95a3"), hexc("a3958d"), hexc("8da395")][i % 3])
        if i % 5 == 0:
            line(c, [(x + 20, y - 130), (x + 20, y - 200)], f"qf{i}", 2.4, hexc("6b4a32"))
            with keep():
                shape(c, [(x + 20, y - 200), (x + 50, y - 192), (x + 20, y - 184)], hexc("e8c040"), f"qff{i}", lw=1.4)
    up = ease_out(prog(t, 0.6, 0.8))
    girl(c, 540, 1240, 1.6, hat=True, mouth="sad", look=-0.2, look_up=0.3 * up,
         arms=[(-24, -78), (24, -78)] if up < 0.3 else [(-30, lerp(-78, -250, up)), (30, lerp(-78, -250, up))], key="g05")
    suitcase(c, 540 - 90, 1244, 0.9, "su05", handle=0.4)
    if up > 0.3:
        c.save()
        c.translate(540, 1240 - 268 * 1.6 * up)
        c.rotate(math.pi / 2)
        guidebook(c, 0, 0, 1.6, "gb5")
        c.restore()
    with keep():                                                   # 晒得冒热气
        for k in range(4):
            ph = (t * 0.8 + k / 4) % 1
            line(c, [(470 + k * 40, 760 - ph * 60), (464 + k * 40, 730 - ph * 60), (470 + k * 40, 700 - ph * 60)],
                 f"ht{k}", 2.4, hexc("e8743a"), alpha=0.8 * (1 - ph))


def w06(c, t):
    d06_checkin(c, t)


def w07(c, t):
    """夜里在旅馆床上翻相册：一格一格几乎一样的剪刀手；手指停在一张上，想不起来这是哪里。"""
    fill_all(c, hexc("2b3048"))
    with keep():
        glow(c, 540, 1100, 500, hexc("bcd2ff"), 0.25)
    shape(c, rect(60, 1080, 960, 220), hexc("5a5f7a"), "bed", lw=3)
    shape(c, rect(60, 980, 140, 160), hexc("6a6f8a"), "headb", lw=3)
    shape(c, rrect(150, 1010, 240, 90, 30), hexc("dfe2ee"), "pillow", lw=2)
    girl(c, 560, 1080, 1.5, sit=True, legs=False, hat=False, head_down=8, look=0.0, mouth="flat",
         arms=[(-14, -96), (14, -96)], key="g07")
    phone_at(c, 560, 1080 - 96 * 1.5 + 52 * 1.5 - 10, 1.0, "ph07", glow_a=0.6)
    # 放大的手机屏幕
    px, py, pw, ph = 240, 110, 600, 760
    scroll = ease_io(prog(t, 0.2, 2.6)) * 640
    with keep():
        shape(c, rrect(px - 16, py - 16, pw + 32, ph + 32, 44), hexc("3a3f4a"), "alb", lw=3)
        shape(c, rect(px, py, pw, ph), hexc("f6f6f6"), "als", lw=0, edge=False)
        text(c, "相册", px + pw / 2, py + 50, 30, INK)
        c.save()
        c.rectangle(px, py + 80, pw, ph - 80)
        c.clip()
        skies = ["9fc5e8", "f2c79a", "b9c3e8", "a9c48b", "f2a6a0", "c9d1d8"]
        kinds = ["bridge", "gate", "tower"]
        stop = 13
        for i in range(30):
            cx = px + 12 + (i % 3) * 196
            cy = py + 92 + (i // 3) * 196 - scroll
            if cy < py - 200 or cy > py + ph:
                continue
            c.save()
            c.rectangle(cx, cy, 186, 186)
            c.clip()
            vgrad(c, cy, cy + 186, [(0, hexc(skies[i % 6])), (1, (0.97, 0.96, 0.93))], cx, cx + 186)
            landmark(c, cx + 93, cy + 160, 0.26, kinds[i % 3], f"al{i}")
            girl(c, cx + 93, cy + 186, 0.66, look=0.2, mouth="laugh", arms=[(-24, -80), (44, -168)], key=f"ag{i}")
            c.restore()
            hl = i == stop and t > 3.0
            shape(c, rect(cx, cy, 186, 186), None, f"alf{i}", lw=4 if hl else 1.6, amp=0.2)
            if hl:                                                 # 手指停住
                circle(c, cx + 120, cy + 120, 22, SKIN, a=0.9)
        c.restore()
    q = ease_back(prog(t, 3.6, 0.5))
    if q > 0:
        with keep():
            text(c, "？", 690, 1080 - 250 * 1.5 + 30, 70 * q, (1, 1, 1))


# ================================================================ 8 走过更大的世界
TERRAINS = [("f2d29a", "e8b46a", "沙漠"), ("9fd0ec", "6fa8c8", "海岸"), ("eef2f8", "c9d6e3", "雪地"),
            ("bfe0b0", "5f9a5a", "雨林")]


def terrain(c, i, x0, w):
    sky, ground, kind = TERRAINS[i % 4]
    c.save()
    c.rectangle(x0, -200, w + 1, H + 400)
    c.clip()
    vgrad(c, 0, 1000, [(0, hexc(sky)), (1, (0.98, 0.97, 0.94))], x0, x0 + w)
    if kind == "沙漠":
        shape(c, hill_pts(980, 60, 0.008, i, x0, x0 + w, 1900), hexc(ground), f"tr{i}", lw=2.4)
        with keep():
            circle(c, x0 + w * 0.7, 300, 70, hexc("fff0b0"))
    elif kind == "海岸":
        shape(c, rect(x0, 820, w, 200), hexc("4f8fb8"), f"tsea{i}", lw=2)
        shape(c, hill_pts(1000, 20, 0.01, i, x0, x0 + w, 1900), hexc("efdcb0"), f"tr{i}", lw=2.4)
    elif kind == "雪地":
        for k in range(3):
            mountain(c, x0 + 150 + k * 300, 960, 360, 320, hexc("b9c6d6"), f"tm{i}{k}")
        shape(c, hill_pts(990, 30, 0.006, i, x0, x0 + w, 1900), hexc("f6f8fb"), f"tr{i}", lw=2.4)
    else:
        for k in range(5):
            tree(c, x0 + 80 + k * 220, 1000, 1.6, f"tt{i}{k}", col=hexc("4f8a4a"))
        shape(c, hill_pts(1000, 20, 0.01, i, x0, x0 + w, 1900), hexc(ground), f"tr{i}", lw=2.4)
    c.restore()


def world_walk(c, t):
    if True:
        dist = t * 600 + t * t * 160                              # 越走越快
        i0 = int(dist // W)
        off = dist % W
        terrain(c, i0, -off, W)
        terrain(c, i0 + 1, W - off, W)
        stride = clamp(t / 3.0)
        girl(c, 520, 1240, 1.6 + 0.1 * stride, hat=True, walk=t * (7 + 5 * stride), run=stride > 0.7, look=0.8,
             head_down=lerp(8, 0, stride), mouth="smile" if stride > 0.5 else "flat", key="g08")


def w08(c, t):
    pan(c, t, world_walk, lambda cc, tt: d08_wider(cc, 1.4 + tt), 3.6, 0.6)


# ================================================================ 10–13 以前 / 后来：同一个机位
def room_bg(c, warm):
    """民宿房间：窗、床、门。"""
    fill_all(c, hexc("e8dcc4") if warm else hexc("dcd8cf"))
    shape(c, rect(380, 220, 320, 360), hexc("bfe0f2") if warm else hexc("cfd6dc"), "rwin", lw=3)
    line(c, [(540, 220), (540, 580)], "rwm", 4, hexc("8c5a3c"))
    line(c, [(380, 400), (700, 400)], "rwh", 4, hexc("8c5a3c"))
    shape(c, rect(360, 580, 360, 22), hexc("b9a587"), "sill", lw=2)
    shape(c, rect(820, 420, 200, 640), hexc("8c6a4a"), "rdoor", lw=3)
    circle(c, 845, 760, 8, hexc("d9b778"))
    shape(c, rect(-20, 1060, W + 40, 900), hexc("c9b59a"), "rfl", lw=3)
    shape(c, rect(40, 880, 360, 180), hexc("f4f0e6"), "bed", lw=3)
    shape(c, rect(40, 780, 40, 280), hexc("8c5a3c"), "bedh", lw=2.4)
    shape(c, rrect(90, 850, 120, 50, 20), (1, 1, 1), "bpill", lw=2)


def days_before(c, t):
    room_bg(c, False)
    suitcase(c, 760, 1110, 1.1, "suD", handle=1.0)
    girl(c, 260, 880, 1.5, sit=True, hat=True, head_down=8, look=0.3, mouth="flat", arms=[(-20, -70), (14, -100)],
         key="gDb")
    phone_at(c, 260 + 14 * 1.5, 880 - 100 * 1.5 + 52 * 1.5, 1.0, "phD", glow_a=0.3)
    a = clamp((t - 0.6) * 2)
    with keep():
        shape(c, rrect(150, 520, 300, 120, 24), (1, 1, 1), "retb", lw=2, alpha=a)
        text(c, "返程", 300, 566, 30, INK, a=a)
        text(c, "第 3 天 10:00", 300, 614, 30, RED, a=a)


def days_after(c, t):
    room_bg(c, True)
    with keep():
        shape(c, [(420, 580), (480, 580), (470, 540), (430, 540)], hexc("c98d4a"), "pot", lw=2)       # 小盆栽
        for k in range(3):
            shape(c, ell(450 + (k - 1) * 22, 520 - (k % 2) * 16, 16, 24, 10), hexc("6fa860"), f"leaf{k}", lw=1.4)
        for k in range(3):                                         # 墙上的速写
            x = 100 + k * 90
            c.save()
            c.translate(x, 330)
            c.rotate(0.08 * (k - 1))
            shape(c, rect(-36, -46, 72, 92), (1, 1, 1), f"sk{k}", lw=1.6, amp=0.3)
            line(c, [(-24, 20), (-6, -10), (8, 6), (24, -20)], f"skl{k}", 2, hexc("6a6560"))
            c.restore()
            circle(c, x, 288, 4, RED)
        for k, col in enumerate(("f2a6a0", "9fc5e8", "f7e27a")):     # 摊开的衣服
            shape(c, [(560 + k * 60, 1040), (620 + k * 60, 1030), (630 + k * 60, 1060), (556 + k * 60, 1064)],
                  hexc(col), f"clo{k}", lw=1.6, amp=0.5)
        shape(c, ell(300, 868, 50, 22, 16), hexc("e8a050"), "cat", lw=2)                 # 睡在床上的猫
        shape(c, ell(342, 856, 18, 16, 12), hexc("e8a050"), "cath", lw=2)
        for sg in (-1, 1):
            shape(c, [(342 + sg * 12, 846), (342 + sg * 6, 834), (342, 846)], hexc("e8a050"), f"cate{sg}", lw=1.4)
        line(c, [(334, 858), (340, 860)], "catz", 1.6)
        z = (t * 0.6) % 1
        text(c, "z", 380 + z * 30, 820 - z * 40, 26, INK, a=1 - z)
    water = math.sin(t * 3) * 6
    girl(c, 600, 1240, 1.6, hat=False, mouth="laugh", look=-0.6, skin=TAN, arms=[(-40, -150 + water), (24, -78)],
         key="gDa")
    with keep():                                                   # 给盆栽浇水的小水壶
        shape(c, [(600 - 64, 1240 - 154 * 1.6 + water), (600 - 30, 1240 - 154 * 1.6 + water),
                  (600 - 34, 1240 - 130 * 1.6 + water), (600 - 60, 1240 - 130 * 1.6 + water)], hexc("9fc5e8"), "can",
              lw=1.8)


def gate_bg(c, t, clock):
    vgrad(c, 0, 1000, [(0, hexc("f6e6c8")), (1, hexc("fbf3e2"))])
    shape(c, rect(80, 200, 920, 560), hexc("cfe0ea"), "gwin", lw=3)
    for k in range(1, 4):
        line(c, [(80 + k * 230, 200), (80 + k * 230, 760)], f"gwm{k}", 4, hexc("6f7d8a"))
    shape(c, rect(80, 620, 920, 140), hexc("b9c0c4"), "apron", lw=2)
    plane(c, 560, 600, 3.0, "gpl")
    with keep():
        shape(c, rect(640, 90, 340, 80), hexc("2e3449"), "gsign", lw=2)
        text(c, "14:00 登机", 810, 144, 38, hexc("f6e08a"))
        shape(c, rect(100, 90, 200, 80), hexc("e8c040"), "gate", lw=2)
        text(c, "登机口", 200, 144, 36, INK)
        shape(c, ell(420, 130, 46, 46, 20), (1, 1, 1), "gclk", lw=2.4)
        h, m = clock
        a_m, a_h = m / 60 * 2 * math.pi, (h % 12 + m / 60) / 12 * 2 * math.pi
        line(c, [(420, 130), (420 + math.sin(a_m) * 36, 130 - math.cos(a_m) * 36)], "gmm", 3)
        line(c, [(420, 130), (420 + math.sin(a_h) * 24, 130 - math.cos(a_h) * 24)], "ghh", 4)
    shape(c, rect(-20, 1000, W + 40, 900), hexc("c9c2b4"), "gfl", lw=3)
    for k in range(4):                                             # 一排候机椅
        shape(c, rrect(120 + k * 120, 1000, 100, 70, 14), hexc("6f8aa0"), f"seat{k}", lw=2)
        line(c, [(170 + k * 120, 1070), (170 + k * 120, 1130)], f"seatl{k}", 4, hexc("6a6560"))


def plan_before(c, t):
    gate_bg(c, t, (11, 0))
    girl(c, 300, 1000, 1.5, sit=True, hat=True, head_down=10, look=0.2, mouth="flat", arms=[(-30, -96), (30, -96)],
         key="gPb")
    with keep():                                                   # 贴满便利贴的厚攻略
        bx, by = 300, 1000 - 96 * 1.5 + 52 * 1.5 - 20
        shape(c, rect(bx - 70, by - 50, 140, 90), hexc("3f6fb5"), "pbk", lw=2)
        shape(c, rect(bx - 66, by - 64, 132, 16), (1, 1, 1), "pbk2", lw=1.4)
        for k, col in enumerate(("f7e27a", "f2a6a0", "a8e07a", "9fc5e8", "f7e27a", "f2a6a0")):
            shape(c, rect(bx - 60 + k * 22, by - 80 - (k % 2) * 8, 16, 22), hexc(col), f"pnote{k}", lw=1, amp=0.2)
    suitcase(c, 470, 1004, 0.9, "suPb", handle=0.4)


def plan_after(c, t):
    gate_bg(c, t, (13, 55))
    a = clamp(t * 3) * (0.6 + 0.4 * (math.sin(t * 8) > 0))
    with keep():                                                   # 广播：最后登机
        shape(c, rrect(300, 360, 480, 100, 30), (1, 1, 1), "ann", lw=2, alpha=a)
        text(c, "📢 最后登机", 540, 424, 40, RED, a=a)
    x = lerp(-80, 620, ease_out(prog(t, 0.0, 2.6)))
    pull(c, x, 1240, 1.6, "gPa", walk=t * 13, run=True, mouth="laugh")
    p = ease_back(prog(t, 1.2, 0.5))
    if p > 0:
        with keep():
            c.save()
            c.translate(800, 860)
            c.scale(p, p)
            shape(c, rrect(-110, -170, 220, 340, 26), hexc("3a3f4a"), "bigph", lw=2.4)
            shape(c, rect(-96, -150, 192, 300), hexc("eef4ff"), "bigphs", lw=1)
            text(c, "08:00", 0, -96, 34, INK)
            text(c, "已出票", 0, -50, 30, hexc("4f9a5c"))
            line(c, [(-70, -20), (70, -20)], "bpl", 1.6, hexc("9aa0a8"))
            text(c, "14:00", 0, 30, 34, INK)
            text(c, "登机", 0, 76, 30, RED)
            c.restore()


def pack_room(c, warm):
    fill_all(c, hexc("eaf2e2") if warm else hexc("dcd8cf"))
    shape(c, rect(820, 420, 200, 640), hexc("8c6a4a"), "pdoor", lw=3)
    shape(c, rect(-20, 1060, W + 40, 900), hexc("d9c4a8"), "pfl", lw=3)
    for k in range(9):
        line(c, [(k * 130 - 20, 1060), (k * 160 - 120, 1900)], f"pkb{k}", 1.4, hexc("c4ae90"), alpha=0.6)


def wall_clock(c, x, y, mins, key):
    with keep():
        shape(c, ell(x, y, 80, 80, 24), (1, 1, 1), key, lw=3)
        a = mins / 60 * 2 * math.pi
        line(c, [(x, y), (x + math.sin(a) * 60, y - math.cos(a) * 60)], key + "m", 4)
        line(c, [(x, y), (x + 34, y - 20)], key + "h", 5)


def pack_before(c, t):
    pack_room(c, False)
    wall_clock(c, 300, 300, 0, "pclk")
    sq = 10 * abs(math.sin(t * 5))
    with keep():                                                   # 塞得满满当当的箱子
        shape(c, rrect(330, 980 + sq, 420, 230 - sq, 24), hexc("8b6f9a"), "bigsu", lw=3)
        line(c, [(330, 1040 + sq), (750, 1040 + sq)], "zip", 3, hexc("5a4a6a"))
        pop = ease_back(prog(t, 2.2, 0.4))
        if pop > 0:                                                # 拉链崩开一角，袖子掉出来
            shape(c, [(720, 1040), (790, 1000 - 30 * pop), (810, 1030 - 30 * pop), (740, 1060)], hexc("f2a6a0"), "slv",
                  lw=1.6)
            text(c, "啪！", 820, 960, 40, RED, a=pop)
    girl(c, 540, 980 + sq, 1.5, sit=True, hat=False, mouth="sad", look=0.0, arms=[(-60, -40), (60, -40)], key="gKb")


def pack_after(c, t):
    pack_room(c, True)
    wall_clock(c, 300, 300, 10 * clamp(t / 2.4), "pclk")
    with keep():
        text(c, "10 分钟", 300, 430, 36, INK)
    if t < 2.6:
        with keep():
            shape(c, rrect(250, 1000, 220, 250, 44), PACK, "bpk", lw=3)
            shape(c, rrect(280, 1130, 160, 90, 16), darker(PACK, 0.85), "bpkp", lw=2)
            u = prog(t, 0.1, 2.0)
            for k in range(3):                                     # 卷起来的衣服，一件件塞进去
                uu = ease_io(clamp(u * 3 - k))
                if uu < 1:
                    shape(c, rrect(lerp(600, 330, uu), lerp(1100, 1010, uu) - math.sin(uu * math.pi) * 160, 80, 34, 16),
                          hexc(["9fc5e8", "f7e27a", "f2a6a0"][k]), f"pc{k}", lw=1.6, amp=0.4)
        girl(c, 640, 1240, 1.6, hat=True, look=-0.7, mouth="smile",
             arms=[(-50, -100 + 20 * math.sin(t * 10)), (24, -78)], key="gKa")
    else:
        x = lerp(560, 1250, ease_in(prog(t, 2.8, 1.2)))
        girl(c, x, 1240, 1.6, hat=True, look=0.9, mouth="laugh", walk=t * 9, run=True, pack=True, key="gKa2")


def fork_bg(c, warm):
    vgrad(c, 0, 900, [(0, hexc("9fd0ec") if warm else hexc("c9d1d8")), (1, hexc("f4efe4"))])
    shape(c, hill_pts(860, 30, 0.008, 2.0), hexc("a9c48b"), "fkh", lw=3)
    for i, x1 in enumerate((140, 540, 940)):
        shape(c, [(500, 1300), (580, 1300), (x1 + 40, 880), (x1 - 40, 880)], hexc("d9c39a"), f"fk{i}", lw=2.4)
    shape(c, rect(-20, 1280, W + 40, 600), hexc("cfc19c"), "fkg", lw=3)
    if warm:
        for k in range(3):
            cloud(c, 160 + k * 340, 260 + k * 40, 1.1, f"fkc{k}")


def route_before(c, t):
    fork_bg(c, False)
    spin = math.cos(t * 3.2)
    girl(c, 540, 1260, 1.7, hat=True, pack=True, look=spin, mouth="o", sx=1.0 if spin > -0.3 else -1.0,
         arms=[(-24, -78), (30, -130)], key="gRb")
    with keep():                                                   # 不停转的导航箭头
        c.save()
        c.translate(540, 560)
        c.rotate(t * 4)
        shape(c, [(0, -60), (36, 40), (0, 20), (-36, 40)], hexc("3f6fb5"), "navarr", lw=2)
        c.restore()
        shape(c, ell(540, 560, 90, 90, 24), None, "navc", lw=2)
    phone_at(c, 540 + 30 * 1.7 * (1 if spin > -0.3 else -1), 1260 - 130 * 1.7, 1.2, "phR", glow_a=0.3)


def route_after(c, t):
    fork_bg(c, True)
    unfold = ease_io(prog(t, 0.0, 0.6)) * (1 - ease_io(prog(t, 1.4, 0.4)))
    point = t > 1.9
    walk = t > 2.6
    x = 540 + ease_in(prog(t, 2.6, 1.4)) * 360
    y = 1260 - ease_in(prog(t, 2.6, 1.4)) * 300
    s = 1.7 - ease_in(prog(t, 2.6, 1.4)) * 0.8
    girl(c, x, y, s, hat=True, pack=True, view="back" if walk else "front", mouth="laugh", look=0.3,
         arms=[(-24, -78), (70, -190)] if point and not walk else ([(-40, -110), (40, -110)] if unfold > 0.05 else None),
         walk=t * 6 if walk else None, key="gRa")
    if unfold > 0.05:
        with keep():                                               # 摊开的纸地图
            w_ = 220 * unfold
            shape(c, rect(540 - w_ / 2, 1260 - 210 * 1.7, w_, 130), hexc("f4e7c8"), "pmap", lw=2)
            line(c, [(540 - w_ / 2 + 20, 1260 - 160 * 1.7), (540, 1260 - 190 * 1.7), (540 + w_ / 2 - 20, 1260 - 150 * 1.7)],
                 "pmapl", 2, RED)


PAIRS = [(days_before, days_after), (plan_before, plan_after), (pack_before, pack_after), (route_before, route_after)]


def w10(c, t):
    k = min(int(t / 8.0), 3)
    lt = t - k * 8.0
    before, after = PAIRS[k]

    def bf(cc, tt):
        with grade(sat=0.3):
            before(cc, tt)
    xfade(c, lt, bf, after, 4.0, 0.6)


# ================================================================ 14–19 走进当地人的生活
def w14(c, t):
    d10_town(c, t)


def w15(c, t):
    d11_costume(c, t)


def w16(c, t):
    """穿着这身衣服，提着菜篮跟在房东后面，比划着讲价，篮子越装越满。"""
    fill_all(c, hexc("f2e6cf"))
    for i in range(3):
        x = 40 + i * 340
        shape(c, [(x, 520), (x + 320, 520), (x + 290, 440), (x + 30, 440)], hexc(["d9653a", "4f8a7a", "e8c040"][i]),
              f"aw{i}", lw=2.4)
        for k in range(6):
            line(c, [(x + 30 + k * 46, 440), (x + 20 + k * 50, 520)], f"aws{i}{k}", 2, (1, 1, 1), alpha=0.5)
        shape(c, rect(x + 10, 760, 300, 140), hexc("a8865f"), f"stl{i}", lw=2.4)
        for j in range(3):
            produce(c, x + 70 + j * 90, 760, (i + j) % 4, f"pr{i}{j}")
        local(c, x + 160, 760, 1.1, f"ven{i}", hexc(["8fb39a", "c98d72", "7d6a8f"][i]), hexc("2f2a28"), "short",
              look=0.0, mouth="laugh", legs=False)
    shape(c, rect(-20, 900, W + 40, 900), hexc("d9c8a8"), "mg", lw=3)
    r = random.Random(7)
    for i in range(6):
        x = (r.uniform(0, 1100) + t * 50 * (1 if i % 2 else -1)) % 1200 - 60
        silhouette(c, x, 1000 + r.uniform(-20, 20), 1.1, f"mp{i}", walk=t * 6 + i, a=0.45)
    walk = ease_io(prog(t, 0.0, 2.0))
    gx = lerp(160, 480, walk)
    local(c, gx + 180, 1230, 1.6, "landlady", hexc("8d6a9f"), GRAN, "granny", look=0.4, mouth="laugh",
          walk=t * 6 if walk < 1 else None)
    haggle = 2.4 < t < 5.0
    girl(c, gx, 1230, 1.6, hat=True, outfit="folk", look=0.6 if not haggle else -0.6, mouth="laugh" if haggle else "smile",
         walk=t * 6 if walk < 1 else None, arms=[(-30, -60), (30 + 10 * math.sin(t * 9) * haggle, -110 if haggle else -76)],
         key="g16")
    with keep():
        bx, by = gx - 30 * 1.6, 1230 - 60 * 1.6
        shape(c, [(bx - 34, by - 10), (bx + 34, by - 10), (bx + 26, by + 34), (bx - 26, by + 34)], hexc("d9b778"), "bsk",
              lw=2)
        n = int(clamp(t / 1.1, 0, 5))
        for k in range(n):
            shape(c, ell(bx - 22 + (k % 3) * 22, by - 14 - (k // 3) * 14, 12, 10, 10),
                  hexc(["d9433a", "6fa860", "e8c040", "c98d4a", "d9433a"][k]), f"bk{k}", lw=1.2, amp=0.2)
        if haggle:
            for k, (txt, xx) in enumerate((("3 ?", 300), ("2 !", 620))):
                a = math.sin(prog(t, 2.4 + k * 0.9, 1.4) * math.pi)
                if a > 0:
                    shape(c, rrect(xx - 50, 460, 100, 70, 20), (1, 1, 1), f"hb{k}", lw=2, alpha=a)
                    text(c, txt, xx, 508, 36, INK, a=a)


# ---------------------------------------------------------------- 17 做饭：切菜的手
GRAN_SLEEVE = hexc("8d6a9f")


def sleeve(c, p0, p1, w, col, key):
    """从画面边上伸进来的袖子：有墨线的长条，末端一圈袖口。"""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    with keep():
        shape(c, [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)],
              col, key, lw=2.6, amp=0.5)
        shape(c, [(p1[0] + nx * 1.05, p1[1] + ny * 1.05), (p1[0] - nx * 1.05, p1[1] - ny * 1.05),
                  (p1[0] - nx * 1.05 - dx / L * 18, p1[1] - ny * 1.05 - dy / L * 18),
                  (p1[0] + nx * 1.05 - dx / L * 18, p1[1] + ny * 1.05 - dy / L * 18)], darker(col, 0.85), key + "c",
              lw=2.2, amp=0.4)


def fist(c, x, y, s, skin, key):
    with keep():
        shape(c, ell(x, y, 38 * s, 32 * s, 14), skin, key, lw=2.4)
        for k in range(3):
            line(c, [(x - 20 * s + k * 16 * s, y - 14 * s), (x - 20 * s + k * 16 * s, y + 4 * s)], f"{key}k{k}", 1.6)


def knife(c, x, y, ang, key):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    with keep():
        shape(c, [(0, 0), (150, -10), (190, 30), (0, 40)], hexc("dfe3e6"), key + "b", lw=2.4)
        shape(c, rrect(-110, 4, 116, 32, 10), hexc("6b4a32"), key + "h", lw=2.4)
    c.restore()


def hand_shape(c, x, y, s, skin, key, curl=0.0, rot=0.0):
    """手背 + 四根手指；curl=1 时手指弯起来，指节朝前。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    with keep():
        for k in range(4):
            fx = -30 + k * 20
            if curl > 0.5:
                shape(c, ell(fx, 30, 11, 12, 10), skin, f"{key}f{k}", lw=2)
            else:
                shape(c, rrect(fx - 9, 10, 18, 56 - k * 4, 9), skin, f"{key}f{k}", lw=2)
        shape(c, ell(0, 0, 50, 34, 16), skin, key + "p", lw=2.4)
        shape(c, ell(46, 10, 12, 20, 10), skin, key + "th", lw=2)
    c.restore()


def chop_close(c, t):
    """特写：案板、土豆、刀。①她自己切，大小不一，一块滚出案板 ②奶奶握住她的手，示范手指弯起来 ③她自己切整齐了，奶奶竖大拇指。"""
    fill_all(c, hexc("e8dcc4"))
    for i in range(6):
        shape(c, rect(60 + i * 170, 120, 150, 110), hexc("dfe9ea"), f"tile{i}", lw=1.6, amp=0.4)
    shape(c, rect(-20, 420, W + 40, 1500), hexc("b9a587"), "counter", lw=3)
    shape(c, rrect(100, 560, 880, 560, 30), hexc("efdcb4"), "board", lw=3)
    for k in range(5):
        line(c, [(140, 640 + k * 100), (940, 650 + k * 100)], f"bgr{k}", 1.4, hexc("d9c196"), alpha=0.6)
    phase = 0 if t < 1.7 else (1 if t < 3.3 else 2)
    with keep():                                                   # 土豆
        shape(c, ell(560, 820, 120, 80, 24), hexc("b88a52"), "pot", lw=2.4)
        for k in range(4):
            circle(c, 520 + k * 28, 800 + (k % 2) * 20, 4, hexc("7a5a30"))
    # 切下来的块
    with keep():
        r = random.Random(3)
        n_rough = int(clamp(t / 0.32, 0, 5))
        for k in range(n_rough):                                   # 第一次：大小不一
            sz = r.uniform(18, 46)
            shape(c, rect(380 - k * 52 - sz / 2, 840 - sz / 2, sz, sz * 0.8), hexc("f6ecc8"), f"rk{k}", lw=1.6, amp=0.4)
        roll = prog(t, 1.0, 0.8)
        if roll > 0:                                               # 一块滚到了案板外
            rx = 260 - roll * 260
            circle(c, rx, 860 + roll * 380 * roll, 22, hexc("f6ecc8"))
            shape(c, ell(rx, 860 + roll * 380 * roll, 22, 22, 12), None, "rollk", lw=1.6)
        if phase >= 1:                                             # 奶奶示范 / 她自己：整齐的薄片
            n_neat = int(clamp((t - 1.9) / 0.14, 0, 10)) if phase == 1 else 10
            for k in range(n_neat):
                shape(c, ell(700 + k * 18, 900, 6, 34, 10), hexc("f6ecc8"), f"nk{k}", lw=1.4, amp=0.2)
        if phase == 2:
            n2 = int(clamp((t - 3.4) / 0.3, 0, 4))
            for k in range(n2):
                shape(c, ell(700 + k * 18, 980, 6, 34, 10), hexc("f6ecc8"), f"nk2{k}", lw=1.4, amp=0.2)
    # 刀和手
    if phase == 0:
        up = abs(math.sin(t * 7))
        hand_shape(c, 620, 780, 1.4, SKIN, "lhand", curl=0.0, rot=0.2)            # 手指伸直按着
        sleeve(c, (1120, 520), (720, 700), 70, COAT, "lsl")
        knife(c, 470, 740 - up * 90, -0.25 - up * 0.3, "kn")
        sleeve(c, (-40, 1080), (330, 800 - up * 90), 70, COAT, "rsl")
        fist(c, 380, 780 - up * 90, 1.2, SKIN, "rfist")
    elif phase == 1:
        up = abs(math.sin(t * 12)) * 0.5
        hand_shape(c, 640, 800, 1.4, SKIN, "lhand", curl=1.0, rot=0.2)            # 手指弯起来，指节贴着刀
        hand_shape(c, 650, 760, 1.5, SKIN_L, "ghand", curl=1.0, rot=0.25)          # 奶奶的手盖在上面
        sleeve(c, (1120, 420), (740, 680), 76, GRAN_SLEEVE, "gsl")
        knife(c, 610, 760 - up * 60, -0.15 - up * 0.2, "kn")
        sleeve(c, (-40, 1080), (470, 810 - up * 60), 70, COAT, "rsl")
        fist(c, 520, 790 - up * 60, 1.2, SKIN, "rfist")
        hand_shape(c, 540, 770 - up * 60, 1.3, SKIN_L, "ghand2", curl=1.0, rot=-0.3)
        sleeve(c, (160, 380), (470, 720 - up * 60), 76, GRAN_SLEEVE, "gsl2")
        a = clamp((t - 1.8) * 3) * (1 - prog(t, 3.0, 0.3))
        with keep():
            shape(c, rrect(560, 380, 380, 90, 30), (1, 1, 1), "tip", lw=2, alpha=a)
            text(c, "手指弯起来～", 750, 438, 38, INK, a=a)
    else:
        up = abs(math.sin(t * 6)) * 0.6
        hand_shape(c, 660, 860, 1.4, SKIN, "lhand", curl=1.0, rot=0.2)
        sleeve(c, (1120, 600), (740, 780), 70, COAT, "lsl")
        knife(c, 630, 820 - up * 60, -0.15 - up * 0.2, "kn")
        sleeve(c, (-40, 1140), (490, 870 - up * 60), 70, COAT, "rsl")
        fist(c, 540, 850 - up * 60, 1.2, SKIN, "rfist")
        th = ease_back(prog(t, 3.8, 0.4))                          # 奶奶竖大拇指
        if th > 0:
            c.save()
            c.translate(820, 340 + 200 * (1 - th))
            sleeve(c, (300, 120), (40, 60), 90, GRAN_SLEEVE, "thsl")
            with keep():
                shape(c, rrect(-60, -10, 110, 100, 30), SKIN_L, "thumbf", lw=2.6)
                for k in range(3):
                    line(c, [(-56, 20 + k * 24), (-20, 20 + k * 24)], f"thk{k}", 1.8)
                shape(c, rrect(-30, -100, 40, 104, 20), SKIN_L, "thumb", lw=2.6)
            c.restore()


def wok(c, t):
    """她把菜倒进锅里，“滋啦”一声冒起白烟，奶奶颠锅。"""
    fill_all(c, hexc("e8dcc4"))
    for i in range(6):
        shape(c, rect(80 + i * 160, 160, 120, 90), hexc("dfe9ea"), f"wtile{i}", lw=1.6, amp=0.4)
    pour = ease_io(prog(t, 0.0, 0.4)) * (1 - ease_io(prog(t, 0.5, 0.3)))
    toss0 = max(0.0, math.sin(prog(t, 0.8, 0.7) * math.pi)) if t > 0.8 else 0.0
    girl(c, 300, 950, 2.0, hat=False, look=0.6, mouth="laugh",
         arms=[(-24, -78), (lerp(30, 86, pour), lerp(-80, -96, pour))], key="g17w")
    local(c, 860, 950, 2.0, "cookgran", GRAN_SLEEVE, GRAN, "granny", look=-0.8, mouth="laugh",
          arms=[(-24, -78), (30, -95 - 20 * toss0)])
    shape(c, rect(40, 860, 1000, 900), hexc("8c7a62") + (1.0,), "wcounter", lw=3)
    shape(c, rect(40, 840, 1000, 30), hexc("b9a587") + (1.0,), "wctop", lw=2.4)
    toss = max(0.0, math.sin(prog(t, 0.8, 0.7) * math.pi)) if t > 0.8 else 0.0
    wy = 800 - toss * 40
    with keep():
        glow(c, 620, 820, 160, hexc("ff9a50"), 0.6 + 0.2 * math.sin(t * 9))
        shape(c, ell(620, wy, 150, 40, 20, 0, math.pi), hexc("3a3a3a"), "wok", lw=3)
        line(c, [(770, wy), (920, wy - 40)], "wokh", 10, hexc("3a3a3a"))
        for k in range(6):                                         # 颠起来的菜
            fy = wy - 10 - toss * (120 + k * 20) * (0.4 + 0.6 * abs(math.sin(k + 1)))
            shape(c, ell(560 + k * 24, fy, 12, 8, 8), hexc(["efe0b0", "6fa860", "d9433a"][k % 3]), f"wf{k}", lw=1)
        sm = clamp(t * 2)
        for k in range(7):
            ph = (t * 0.9 + k / 7) % 1
            shape(c, ell(540 + k * 26 + math.sin(t + k) * 10, 740 - ph * 360, 34 + ph * 50, 20 + ph * 24, 12),
                  (1, 1, 1), f"wsmk{k}", lw=0.8, amp=0.4, alpha=0.6 * (1 - ph) * sm)
        a = math.sin(prog(t, 0.05, 1.0) * math.pi)
        if a > 0:
            text(c, "滋啦！", 360, 560, 60, RED, a=a)


def w17(c, t):
    if t < 4.4:
        chop_close(c, t)
    elif t < 6.2:
        wok(c, t - 4.4)
    else:
        courtyard(c, t - 6.2 + 1.0)


def w18(c, t):
    d14_shoot(c, t + 0.4)


# ---------------------------------------------------------------- 19 / 20 / 21 清晨的小巷
def alley(c, t, crowd=0.0):
    vgrad(c, 0, 900, [(0, hexc("f6c99a")), (1, hexc("fbecd0"))])
    with keep():
        glow(c, 540, 300, 600, hexc("fff0c0"), 0.6)
    shape(c, [(0, 0), (300, 200), (300, 1000), (0, 1300)], hexc("e2c49c"), "lw", lw=3)
    shape(c, [(W, 0), (W - 300, 200), (W - 300, 1000), (W, 1300)], hexc("d6b48c"), "rw", lw=3)
    shape(c, [(300, 1000), (W - 300, 1000), (W + 40, 1300), (W + 40, 1900), (-40, 1900), (-40, 1300)], hexc("c9b59a"),
          "lf", lw=3)
    for k in range(6):                                             # 石板路
        y = 1000 + k * k * 18
        line(c, [(300 - k * k * 6, y), (W - 300 + k * k * 6, y)], f"lfs{k}", 1.4, hexc("b39f86"), alpha=0.6)
    for sg, x0 in ((1, 0), (-1, W)):                               # 墙上的窗和花盆
        for k in range(2):
            wx = x0 + sg * (120 + k * 110)
            wy = 330 + k * 60
            shape(c, rect(wx - 40, wy, 80, 110 - k * 20), hexc("8fb3c4"), f"aw{sg}{k}", lw=2)
            with keep():
                shape(c, rect(wx - 44, wy + 110 - k * 20, 88, 22), hexc("b5533a"), f"ap{sg}{k}", lw=1.6)
                for j in range(3):
                    circle(c, wx - 24 + j * 24, wy + 104 - k * 20, 9, hexc(["e8743a", "f2a6a0", "f7e27a"][j]))
    line(c, [(300, 260), (W - 300, 240)], "laundry", 2, hexc("6a6560"))
    with keep():                                                   # 晾着的衣服
        for k, col in enumerate(("9fc5e8", "f2a6a0", "f7e27a", "a8e07a")):
            x = 380 + k * 90
            sw = math.sin(t * 2 + k) * 4
            shape(c, [(x - 26, 252 - k * 2), (x + 26, 252 - k * 2), (x + 22 + sw, 320), (x - 22 + sw, 320)], hexc(col),
                  f"cl{k}", lw=1.6)
    shape(c, rect(40, 860, 220, 160), hexc("8c5a3c"), "stall", lw=2.4)
    lift = ease_io(prog(t, 0.6, 0.8))
    with keep():
        for k in range(3):
            shape(c, ell(150, 860 - k * 34, 80, 22, 16), hexc("d9b778"), f"stm{k}", lw=2)
        shape(c, ell(150, 860 - 3 * 34 - lift * 60, 80, 22, 16), hexc("c9a46a"), "lid", lw=2)
        for k in range(4):
            ph = (t * 0.6 + k / 4) % 1
            if lift > 0.3:
                shape(c, ell(120 + k * 22, 720 - ph * 260, 26 + ph * 30, 16 + ph * 16, 12), (1, 1, 1), f"st{k}", lw=0.8,
                      amp=0.4, alpha=0.6 * (1 - ph))
    local(c, 150, 1010, 1.3, "vendor", hexc("f4f2ec"), hexc("3a3a3a"), "short", look=0.6, mouth="laugh",
          arms=[(-24, -78), (40, -150)])


def kids(c, t, n=2, y=1260):
    for i in range(n):
        x = lerp(-100, 1200, ((t * 0.25 + i * 0.4) % 1))
        local(c, x, y + i * 30, 1.0, f"kid{i}", hexc(["f2a6a0", "9fc5e8", "a8e07a"][i % 3]), hexc("2f2a28"), "short",
              walk=t * 12 + i, run=True, pack=True, look=1.0, mouth="laugh")


def w19(c, t):
    """清晨的小巷：卖早点的掀开蒸笼，孩子跑过，有人点头打招呼，她也点头。"""
    alley(c, t)
    kids(c, t)
    nod = 6 * max(0.0, math.sin(prog(t, 2.6, 1.0) * math.pi))
    local(c, 860, 1180, 1.4, "oldman", hexc("6b7a8a"), GRAN, "short", look=-0.7, head_down=nod, mouth="smile")
    x = lerp(400, 560, ease_out(prog(t, 0.0, 2.4)))
    girl(c, x, 1220, 1.6, hat=False, pack=True, look=0.6 if t > 2.4 else 0.0, head_down=nod, mouth="smile",
         walk=t * 6 if t < 2.4 else None, key="g19")


def hen(c, x, y, t, key, flap=0.0):
    with keep():
        shape(c, ell(x, y, 36, 26, 14), (1, 1, 1), key, lw=2)
        shape(c, ell(x + 30, y - 24, 14, 14, 10), (1, 1, 1), key + "h", lw=2)
        shape(c, [(x + 30, y - 40), (x + 36, y - 48), (x + 40, y - 38)], RED, key + "c", lw=1.4)
        shape(c, [(x + 42, y - 24), (x + 54, y - 20), (x + 42, y - 16)], hexc("e8c040"), key + "b", lw=1.2)
        wa = flap * math.sin(t * 30)
        shape(c, [(x - 10, y - 10), (x - 50, y - 40 - 30 * wa), (x - 20, y + 6)], (1, 1, 1), key + "w", lw=1.6)
        for sg in (-1, 1):
            line(c, [(x + sg * 8, y + 24), (x + sg * 8, y + 44)], f"{key}l{sg}", 2.4, hexc("e8a040"))


def w20(c, t):
    """安静的梦一样的气泡，被孩子、鸡、蒸笼、吆喝撞破，满画面热闹，她笑了。"""
    busy = ease_io(prog(t, 2.8, 0.8))
    alley(c, t + 1.4)
    kids(c, t, n=2 + int(busy), y=1250)
    hx = lerp(1100, 700, ease_out(prog(t, 2.2, 1.0))) - busy * t * 30
    hen(c, hx, 1150, t, "hen1", flap=1.0 if t > 2.4 else 0.2)
    hen(c, hx + 140, 1190, t + 0.3, "hen2", flap=busy)
    laugh = t > 3.6
    girl(c, 540, 1230, 1.6, hat=False, pack=True, look=0.0, mouth="laugh" if laugh else "smile", look_up=0.4,
         arms=[(-24, -78), (24, -78)] if not laugh else [(-40, -150), (40, -150)], key="g20")
    if busy > 0:                                                   # 吆喝声
        with keep():
            for k, (x, y, s) in enumerate(((180, 560, "包子～"), (840, 700, "早！"), (700, 420, "豆浆！"))):
                a = busy * (0.6 + 0.4 * math.sin(t * 5 + k))
                shape(c, rrect(x - 80, y - 46, 160, 76, 26), (1, 1, 1), f"yell{k}", lw=2, alpha=a)
                text(c, s, x, y + 6, 34, INK, a=a)
    grow = ease_back(prog(t, 0.2, 0.8))
    pop = prog(t, 2.8, 0.5)
    cx, cy = 540, 520
    if pop <= 0 and grow > 0.01:
        with keep():
            c.save()
            c.translate(cx, cy)
            c.scale(grow, grow)
            pts = []
            for i in range(80):
                a = i / 80 * 2 * math.pi
                rr = 1 + 0.04 * math.cos(a * 11)
                pts.append((math.cos(a) * 340 * rr, math.sin(a) * 230 * rr))
            c.save()
            spath(c, pts, True)
            c.clip()
            vgrad(c, -240, 240, [(0, hexc("3b3a6e")), (0.7, hexc("c8708a")), (1, hexc("f2b27a"))], -360, 360)
            for k in range(14):
                star(c, -300 + (k * 53) % 600, -190 + (k * 37) % 180, 3, 0.8)
            shape(c, ell(0, 190, 280, 36, 24), hexc("e8b0a0"), "dground", lw=1.6, alpha=0.7)
            girl(c, 0, 190, 1.6, outfit="folk", hat=True, mouth="smile", key="gdream")
            c.restore()
            spath(c, pts, True)
            c.set_source_rgba(1, 1, 1, 0.5)
            c.set_line_width(6)
            c.stroke()
            c.restore()
            for k, (x, y, r) in enumerate(((560, 860, 14), (580, 800, 20))):
                shape(c, ell(x, y, r * grow, r * grow, 12), (1, 1, 1), f"tb{k}", lw=2, alpha=0.8)
    if 0 < pop < 1:
        r = random.Random(5)
        with keep():
            text(c, "啵！", cx, cy, 90 * (0.6 + pop), RED, a=1 - pop)
            for k in range(30):
                a = r.uniform(0, 2 * math.pi)
                d = 200 + pop * 260
                star(c, cx + math.cos(a) * d * 1.3, cy + math.sin(a) * d * 0.8, 5 * (1 - pop) + 1, 1 - pop,
                     hexc("fff3d0"))


def rack(c, x, y, key, held=False):
    """旋转的明信片架。"""
    line(c, [(x, y), (x, y - 520)], key + "p", 6, hexc("6a6560"))
    shape(c, ell(x, y, 60, 14, 14), hexc("6a6560"), key + "b", lw=2)
    cols = ["f2a6a0", "a8e07a", "f7e27a", "c9a0dc", "f2c79a", "9fd0ec"]
    with keep():
        for row in range(4):
            for k in range(3):
                if held and row == 1 and k == 2:
                    continue
                xx = x - 120 + k * 80
                yy = y - 500 + row * 120
                shape(c, rect(xx, yy, 70, 96), (1, 1, 1), f"{key}c{row}{k}", lw=1.6, amp=0.3)
                if row == 1 and k == 2:
                    vgrad(c, yy + 6, yy + 90, [(0, hexc("5fa8d8")), (1, hexc("dff0fa"))], xx + 6, xx + 64)
                    for j in range(3):
                        shape(c, rect(xx + 14 + j * 16, yy + 60, 12, 14), (1, 1, 1), f"{key}hs{j}", lw=1)
                else:
                    shape(c, rect(xx + 6, yy + 6, 58, 60), hexc(cols[(row * 3 + k) % 6]), f"{key}i{row}{k}", lw=1,
                          amp=0.3)


def w21(c, t):
    """巷子尽头的明信片架：拿起蓝白色海岛那张，看了很久，放回去；走两步回头看一眼，走进阳光里。镜头升高。"""
    rise = ease_io(prog(t, 6.6, 3.0))
    with cam(c, 540, H / 2 + 60 * rise, 1.0 - 0.38 * rise, ty=-260 * rise):
        alley(c, t + 3.0)
        with keep():                                               # 巷子尽头的阳光
            glow(c, 540, 820, 380, hexc("fff6d8"), 0.7 + 0.2 * rise)
        shape(c, rect(660, 700, 260, 300), hexc("e8d6b8"), "shop", lw=2.4)
        with keep():
            shape(c, rect(660, 660, 260, 50), hexc("4f8a7a"), "shopsign", lw=2)
            text(c, "明信片", 790, 696, 30, (1, 1, 1))
        held = 1.0 < t < 4.4
        rack(c, 820, 1150, "rk", held=held)
        r = random.Random(8)
        for i in range(int(8 * rise)):                             # 清晨的人群
            x = (r.uniform(0, 1200) + t * (60 if i % 2 else -50)) % 1300 - 100
            local(c, x, 1300 + r.uniform(0, 140), 1.2, f"crowd{i}", hexc(["8fb39a", "c98d72", "7d6a8f", "e8c040"][i % 4]),
                  hexc("2f2a28"), "short", walk=t * 6 + i, look=0.8 if i % 2 else -0.8, mouth="smile")
        if t < 4.6:
            look_card = held
            girl(c, 620, 1220, 1.6, hat=False, pack=True, look=0.6, head_down=-4 if look_card else 0,
                 mouth="o" if 1.4 < t < 3.6 else "smile",
                 arms=[(-24, -78), (34, -150)] if held else ([(-24, -78), (70, -190)] if t < 1.0 or t > 4.0 else None),
                 key="g21")
            if held:
                postcard(c, 620 + 34 * 1.6, 1220 - 168 * 1.6, 0.42, "pc21")
        else:
            walk = prog(t, 4.6, 5.4)
            back = 5.8 < t < 6.6                                   # 走了两步，回头看一眼
            x = lerp(620, 520, ease_io(walk))
            y = lerp(1220, 1020, ease_io(prog(t, 6.6, 3.0)))
            s = lerp(1.6, 0.9, ease_io(prog(t, 6.6, 3.0)))
            girl(c, x, y, s, hat=False, pack=True, view="front" if back else "back", look=0.9 if back else 0.0,
                 mouth="smile", walk=None if back else t * 6, key="g21w")
            if not back:
                hat_on_pack(c, x, y, s, "g21wh")
    if 1.4 < t < 3.6:                                              # 看了很久：明信片放大
        a = math.sin(prog(t, 1.4, 2.2) * math.pi)
        with group_alpha(c, a):
            postcard(c, 540, 520, 1.5, "pc21big")


# ================================================================ 片尾
_STILL = {}


def end_still():
    if "s" not in _STILL:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(158.0)
        with grade(sat=1.0, dark=0.0, warm=0.15):
            w21(cc, 9.8)
        _STILL["s"] = surf
    return _STILL["s"]


def outro(c, t):
    book_outro(c, t, end_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第三章 · 完")

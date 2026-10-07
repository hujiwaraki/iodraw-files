"""第六章 · 模糊地带 —— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。

天气一路变过去：大雨 → 雨停起雾 → 雾散后的夜晚（没画完的圆变成月亮）→ 第二天的日常 → 傍晚的云 → 回家路上的月亮。
画面里不写字。
"""
import math
import os
import random
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("series", "chapter01", "chapter02", "chapter03", "chapter04", "chapter05"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
from draw import *  # noqa: F401,F403,E402
from engine import book_intro, book_outro  # noqa: E402
from scenes_v2 import local  # noqa: E402
from scenes02 import phone_at  # noqa: E402
from scenes05 import mate  # noqa: E402

SKIN_L = hexc("e8c09a")
WOOD = hexc("8c5a3c")
WARM = hexc("ffd98a")
CHALK = hexc("f4f2ec")
NIGHT_A, NIGHT_B = hexc("141c36"), hexc("2c3c66")


# ================================================================ 小物件
def umbrella(c, x, y, s, key, flip=0.0, col=hexc("4f7aa8")):
    """伞：flip → 1 时被风吹翻。(x, y) 是伞柄顶端。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with keep():
        line(c, [(0, 0), (0, 110)], key + "h", 4, hexc("3a3a3a"))
        line(c, [(0, 110), (10, 122), (20, 112)], key + "hk", 4, hexc("3a3a3a"))
        bend = lerp(1.0, -0.8, flip)
        pts = [(math.cos(a) * 110, -abs(math.sin(a)) * 70 * bend - 10 * flip) for a in
               [math.pi * (1 - i / 20) for i in range(21)]]
        pts += [(110, 0)] + [(110 - i * 220 / 6, 10 * math.sin(i * math.pi) * (1 - flip)) for i in range(7)]
        shape(c, pts, col, key + "c", lw=2.4)
        for k in range(1, 6):
            a = math.pi * (1 - k / 6)
            line(c, [(0, -70 * bend if bend > 0 else 0), (math.cos(a) * 110, -abs(math.sin(a)) * 70 * bend)], f"{key}r{k}", 1.4,
                 darker(col, 0.7))
    c.restore()


def rainfall(c, t, n=90, a=0.45, slant=6, y0=-100, y1=2000, seed=1, speed=1400):
    r = random.Random(seed)
    with keep():
        for k in range(n):
            x = r.uniform(-100, W + 100)
            y = (r.uniform(y0, y1) + t * speed * r.uniform(0.8, 1.2)) % (y1 - y0) + y0
            line(c, [(x, y), (x - slant, y + 36)], f"rf{k}", 1.6, hexc("b8c8dc"), alpha=a)


def fog(c, t, amount, y0=0, y1=1920, col=(0.93, 0.94, 0.95)):
    """一层层慢慢飘动的雾。"""
    if amount <= 0:
        return
    with keep():
        for k in range(7):
            y = y0 + (y1 - y0) * (k + 0.5) / 7
            x = (t * (20 + k * 6) + k * 270) % 1600 - 300
            for j in range(3):
                shape(c, ell(x + j * 520 - 300, y + math.sin(t * 0.4 + k) * 20, 420, 120, 18), col, f"fog{k}{j}", lw=0,
                      edge=False, alpha=0.32 * amount)
        c.save()
        c.rectangle(-400, y0, W + 800, y1 - y0)
        c.set_source_rgba(*col, 0.35 * amount)
        c.fill()
        c.restore()


def crescent(c, x, y, r, a=1.0, glow_a=0.35):
    """一弯月亮：缺了一口的圆。"""
    with keep():
        glow(c, x, y, r * 4, hexc("fff3c8"), glow_a * a)
    c.push_group()
    c.arc(x, y, r, 0, 2 * math.pi)
    c.set_source_rgba(0.99, 0.95, 0.84, 1)
    c.fill()
    c.set_operator(cairo.OPERATOR_CLEAR)
    c.arc(x + r * 0.45, y - r * 0.3, r * 0.92, 0, 2 * math.pi)
    c.fill()
    c.set_operator(cairo.OPERATOR_OVER)
    c.pop_group_to_source()
    c.paint_with_alpha(a)


def open_circle(c, x, y, r, u, key, lw=6, col=CHALK, a=1.0, gap=0.28):
    """粉笔画的圆：u 从 0 画到 1，最后总差一口。"""
    end = (2 * math.pi - gap) * clamp(u)
    if end <= 0.02:
        return
    pts = [(x + math.cos(-math.pi / 2 + k / 60 * end) * r, y + math.sin(-math.pi / 2 + k / 60 * end) * r * 0.42)
           for k in range(61)]
    with keep():
        line(c, pts, key, lw, col, alpha=a)


def open_circle_from(c, x, y, r, u, key, lw=6, col=CHALK, a=1.0, gap=0.28, a0=math.pi / 2):
    """从 a0 开始画的粉笔圆，最后差一口。"""
    end = (2 * math.pi - gap) * clamp(u)
    if end <= 0.02:
        return
    pts = [(x + math.cos(a0 + k / 60 * end) * r, y + math.sin(a0 + k / 60 * end) * r * 0.42) for k in range(61)]
    with keep():
        line(c, pts, key, lw, col, alpha=a)


def crane(c, x, y, s, key, half=True, rot=0.0):
    """纸鹤（half：只折了一半）。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    with keep():
        shape(c, [(-40, 0), (40, 0), (0, -26)], hexc("f6efe0"), key + "b", lw=1.8)
        shape(c, [(0, -26), (-6, -70), (20, -20)], hexc("efe6d2"), key + "w", lw=1.6)
        if not half:
            shape(c, [(0, -26), (6, -70), (-20, -20)], hexc("efe6d2"), key + "w2", lw=1.6)
        else:
            shape(c, [(0, 0), (30, 20), (50, 6), (40, 0)], hexc("f6efe0"), key + "flap", lw=1.4)    # 还没折的一角
        line(c, [(-40, 0), (-62, -30), (-70, -26)], key + "neck", 2, hexc("b8b0a0"))
    c.restore()


def chipped_cup(c, x, y, s, key, steam=True, t=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with keep():
        shape(c, [(-40, -90), (40, -90), (32, 0), (-32, 0)], hexc("e8eef4"), key, lw=2.4)
        shape(c, ell(46, -48, 16, 24, 12), None, key + "hd", lw=3)
        shape(c, [(8, -92), (18, -92), (14, -80)], hexc("6a6f7d"), key + "chip", lw=1.4)   # 杯沿的小缺口
        line(c, [(-36, -60), (36, -60)], key + "bd", 3, hexc("c96f6f"))
        if steam:
            for k in range(3):
                ph = (t * 0.6 + k / 3) % 1
                line(c, [(-14 + k * 14, -100 - ph * 60), (-8 + k * 14, -120 - ph * 60)], f"{key}st{k}", 2, (1, 1, 1),
                     alpha=0.7 * (1 - ph))
    c.restore()


def paper_ball(c, x, y, s, key):
    with keep():
        shape(c, ell(x, y, 22 * s, 20 * s, 9), hexc("f4f0e4"), key, lw=1.8, amp=1.6)
        for k in range(3):
            line(c, [(x - 12 * s + k * 8 * s, y - 10 * s), (x - 4 * s + k * 8 * s, y + 8 * s)], f"{key}c{k}", 1.2,
                 hexc("b8b0a0"))


def chalk_stick(c, x, y, s, key):
    with keep():
        shape(c, rrect(x - 30 * s, y - 7 * s, 60 * s, 14 * s, 6), CHALK, key, lw=1.6)


def seesaw(c, x, y, tilt, key, kids=0.0, t=0.0):
    with keep():
        shape(c, [(x - 30, y), (x + 30, y), (x, y - 60)], hexc("8c5a3c"), key + "piv", lw=2)
        c.save()
        c.translate(x, y - 60)
        c.rotate(tilt)
        shape(c, rect(-260, -10, 520, 20), hexc("e8743a"), key + "bd", lw=2.4)
        for sg in (-1, 1):
            line(c, [(sg * 230, -10), (sg * 230, -40)], f"{key}hd{sg}", 4, hexc("3a3a3a"))
        c.restore()
    if kids > 0:
        for i, sg in enumerate((-1, 1)):
            px = x + sg * 220 * math.cos(tilt)
            py = y - 60 + sg * 220 * math.sin(tilt) - 6
            local(c, px, py, 0.9, f"{key}k{i}", hexc(["f2a6a0", "9fc5e8"][i]), hexc("2f2a28"), "short", sit=True,
                  legs=False, mouth="laugh", look=-sg * 0.6, arms=[(-20, -80), (20, -80)])


def chair(c, x, seat, floor, key, col=WOOD, back=-1):
    """侧面看的椅子：座面在 seat，椅背在 back 一侧。"""
    with keep():
        line(c, [(x + back * 50, seat), (x + back * 50, seat - 150)], key + "b", 8, darker(col, 0.85))
        shape(c, rect(x - 60, seat, 120, 16), col, key + "s", lw=2)
        for sg in (-1, 1):
            line(c, [(x + sg * 50, seat + 16), (x + sg * 50, floor)], f"{key}l{sg}", 6, darker(col, 0.85))


def table(c, x0, x1, top, floor, key, col=WOOD):
    with keep():
        shape(c, rect(x0, top, x1 - x0, 18), col, key + "t", lw=2.4)
        for x in (x0 + 30, x1 - 30):
            line(c, [(x, top + 18), (x, floor)], f"{key}l{x}", 7, darker(col, 0.85))


def open_circle_illus(c, cx, cy):
    """章节页小插画：一个缺了一口、没有画完的圆。"""
    with keep():
        end = 2 * math.pi - 0.5
        pts = [(cx + math.cos(-math.pi / 2 + k / 50 * end) * 60, cy + 20 + math.sin(-math.pi / 2 + k / 50 * end) * 60)
               for k in range(51)]
        line(c, pts, "ill", 4, INK)


def intro(c, t):
    book_intro(c, t, "第六章", "模糊地带", open_circle_illus)


# ================================================================ 1 大雨的路口
def rain_city(c, t, dark=0.0):
    vgrad(c, 0, 1000, [(0, mix(hexc("8a93a0"), hexc("2a2f3a"), dark)), (1, mix(hexc("b8bec6"), hexc("4a505a"), dark))])
    r = random.Random(3)
    x = -40
    i = 0
    while x < W + 40:
        w_, h_ = r.uniform(140, 220), r.uniform(380, 700)
        shape(c, rect(x, 1000 - h_, w_, h_), mix(hexc(r.choice(["9aa0aa", "8a909a", "a8acb2"])), hexc("3a3e48"), dark),
              f"rc{i}", lw=2)
        with keep():
            for j in range(int(h_ / 90)):
                if r.random() < 0.45:
                    shape(c, rect(x + 20, 1000 - h_ + 30 + j * 90, 30, 40), hexc("ffe8b0"), f"rcw{i}{j}", lw=1,
                          alpha=0.6)
        x += w_ + 8
        i += 1
    shape(c, rect(-20, 1000, W + 40, 900), mix(hexc("6a6e76"), hexc("2a2c34"), dark), "road", lw=3)
    with keep():
        for k in range(7):                                         # 斑马线
            shape(c, [(80 + k * 140, 1100), (160 + k * 140, 1100), (190 + k * 140, 1180), (100 + k * 140, 1180)],
                  hexc("d8dade"), f"zb{k}", lw=1, alpha=0.6)
        for k in range(6):                                         # 地上的水洼反光
            shape(c, ell(140 + k * 180, 1300 + (k % 2) * 60, 70, 10, 14), hexc("b8c8dc"), f"pd{k}", lw=0, edge=False,
                  alpha=0.4)


def g01(c, t):
    """一阵风把她的伞吹翻了，一辆车开过，溅了她一身水。她站在雨里愣了一下。"""
    rain_city(c, t)
    flip = ease_out(prog(t, 1.4, 0.4))
    car = prog(t, 3.0, 1.2)
    splash = prog(t, 3.5, 0.8)
    wet = splash > 0
    girl(c, 520, 1250, 1.6, hat=False, mouth="o" if wet else ("o" if flip > 0.5 else "flat"), look=0.4 if car > 0 else 0.0,
         arms=[(-24, -78), (30, -150)], key="g1")
    umbrella(c, 520 + 30 * 1.6, 1250 - 150 * 1.6 - 120 * 1.6 + 30, 1.5, "um1", flip=flip)
    if 0 < car < 1:                                                # 开过去的车
        cx = lerp(1500, -500, car)
        with keep():
            shape(c, rrect(cx - 260, 1180, 520, 160, 40), hexc("3a5a7a"), "car", lw=3)
            shape(c, rrect(cx - 160, 1110, 300, 90, 30), hexc("4a6a8a"), "carroof", lw=2.4)
            for wx in (-160, 160):
                shape(c, ell(cx + wx, 1340, 46, 46, 16), hexc("2a2a2a"), f"cw{wx}", lw=2)
            glow(c, cx - 250, 1260, 120, hexc("fff0b8"), 0.5)
    if 0 < splash < 1:                                             # 溅起来的水
        r = random.Random(5)
        with keep():
            for k in range(30):
                a = r.uniform(math.pi * 1.1, math.pi * 1.6)
                d = splash * r.uniform(150, 420)
                circle(c, 640 + math.cos(a) * d * 0.5, 1240 + math.sin(a) * d * 0.8 + splash * splash * 260, r.uniform(5, 11),
                       hexc("b8c8dc"), a=1 - splash)
    if wet:                                                        # 一身水
        with keep():
            for k in range(6):
                ph = (t * 1.2 + k / 6) % 1
                circle(c, 480 + k * 16, 1250 - 120 * 1.6 + ph * 140, 4, hexc("b8c8dc"), a=0.8 * (1 - ph))
    rainfall(c, t)


# ================================================================ 2 失望、失去、被辜负、离别、孤独
def cafe_clock(c, t):
    fill_all(c, hexc("8a7a72"))
    shape(c, rect(560, 160, 420, 520), hexc("6a7a8a"), "cwin", lw=3)
    with keep():
        c.save()
        c.rectangle(560, 160, 420, 520)
        c.clip()
        rainfall(c, t, n=30, a=0.6, y0=160, y1=680, seed=2)
        c.restore()
    with keep():                                                   # 钟走了一圈又一圈
        shape(c, ell(300, 360, 130, 130, 30), (0.98, 0.97, 0.94), "clk", lw=3)
        for k in range(12):
            a = k / 12 * 2 * math.pi
            line(c, [(300 + math.sin(a) * 110, 360 - math.cos(a) * 110), (300 + math.sin(a) * 122, 360 - math.cos(a) * 122)],
                 f"tk{k}", 3)
        am = t * 4.0
        line(c, [(300, 360), (300 + math.sin(am) * 100, 360 - math.cos(am) * 100)], "mh", 4)
        line(c, [(300, 360), (300 + math.sin(am / 12) * 64, 360 - math.cos(am / 12) * 64)], "hh", 6)
    shape(c, rect(-20, 1240, W + 40, 700), hexc("6a5a52"), "cfl", lw=3)
    shape(c, ell(540, 1040, 200, 40, 20), hexc("c9b8a0"), "ctab", lw=2.4)
    line(c, [(540, 1040), (540, 1240)], "ctl", 6, hexc("5a4a42"))
    for k, x in enumerate((300, 780)):
        shape(c, rect(x - 60, 1060, 120, 20), WOOD, f"ch{k}", lw=2)
        line(c, [(x - 50, 1080), (x - 50, 1240)], f"chl{k}", 4, WOOD)
        line(c, [(x + 50, 1080), (x + 50, 1240)], f"chr{k}", 4, WOOD)
        shape(c, rect(x - 60 + (40 if k else 0), 880, 20, 190), WOOD, f"chb{k}", lw=2)
    girl(c, 310, 1060, 1.45, sit=True, legs=False, hat=False, look=0.7, mouth="flat", head_down=4,
         arms=[(-20, -70), (40, -90)], key="g2a")
    chipped_cup(c, 470, 1030, 0.5, "cup2", t=t)


def wilting(c, t):
    fill_all(c, hexc("8a909a"))
    shape(c, rect(140, 160, 800, 760), hexc("5a6a7a"), "wwin", lw=4)
    with keep():
        c.save()
        c.rectangle(140, 160, 800, 760)
        c.clip()
        rainfall(c, t, n=50, a=0.6, y0=160, y1=920, seed=3)
        c.restore()
    line(c, [(140, 540), (940, 540)], "wwm", 6, hexc("e8e4dc"))
    shape(c, rect(100, 920, 880, 40), hexc("e8e4dc"), "sill", lw=2.4)
    shape(c, [(440, 920), (640, 920), (610, 760), (470, 760)], hexc("b8704a"), "pot", lw=2.4)
    droop = ease_io(prog(t, 0.3, 2.6))
    with keep():
        for k in range(6):
            a = -math.pi / 2 + (k - 2.5) * 0.35
            a2 = a + droop * (1.4 if k < 3 else -1.4) * 0.8
            bx, by = 540, 760
            mx, my = bx + math.cos(a) * 80, by + math.sin(a) * 80
            ex, ey = mx + math.cos(a2) * 90, my + math.sin(a2) * 90 + droop * 60
            line(c, [(bx, by), (mx, my), (ex, ey)], f"stem{k}", 3, mix(hexc("6fa860"), hexc("a8905a"), droop))
            shape(c, ell(ex, ey, 26, 12, 12), mix(hexc("6fa860"), hexc("b89a5a"), droop), f"lf{k}", lw=1.4)
        if droop > 0.7:                                            # 掉下来的叶子
            u = prog(t, 2.2, 0.8)
            shape(c, ell(640 + u * 60, 820 + u * 100, 22, 10, 12), hexc("b89a5a"), "fall", lw=1.2)


def umbrella_give(c, t):
    rain_city(c, t, dark=0.2)
    give = ease_io(prog(t, 0.2, 0.8))
    walk = ease_in(prog(t, 1.1, 2.0))
    girl(c, 420, 1250, 1.55, hat=False, look=0.7 if walk < 0.3 else 0.8, mouth="flat" if walk > 0.2 else "smile",
         arms=[(-24, -78), (lerp(30, 70, give), lerp(-150, -130, give))] if walk <= 0 else None, key="g2c")
    px = 620 + walk * 600
    local(c, px, 1250, 1.55, "taker", hexc("6b7a8a"), hexc("2f2a28"), "short", view="back" if walk > 0 else "front",
          look=-0.6, walk=t * 7 if walk > 0 else None, arms=[(-30, -150), (24, -78)])
    ux = lerp(420 + 30 * 1.55, px - 30 * 1.55, give) if walk <= 0 else px - 30 * 1.55
    umbrella(c, ux, 1250 - 150 * 1.55 - 120 * 1.5 + 30, 1.5, "um2")
    rainfall(c, t)


def fireworks(c, t):
    vgrad(c, 0, 1100, [(0, hexc("0f1630")), (1, hexc("2a3050"))])
    shape(c, rect(-20, 1000, W + 40, 200), hexc("1a2440"), "river", lw=2)
    shape(c, rect(-20, 1160, W + 40, 800), hexc("2a2a3a"), "bank", lw=3)
    bursts = [(300, 380, 0.0, "ff8a6a"), (720, 300, 0.7, "8ad8ff"), (520, 460, 1.4, "ffd96a")]
    with keep():
        for k, (bx, by, t0, col) in enumerate(bursts):
            u = prog(t, t0, 1.4)
            if 0 < u < 1:
                for j in range(24):
                    a = j / 24 * 2 * math.pi
                    d = ease_out(u) * 180
                    circle(c, bx + math.cos(a) * d, by + math.sin(a) * d + u * u * 60, 5, hexc(col), a=1 - u)
                glow(c, bx, by, 300, hexc(col), 0.3 * (1 - u))
        last = prog(t, 2.0, 1.2)                                   # 最后一朵慢慢落下来
        if last > 0:
            for j in range(30):
                a = j / 30 * 2 * math.pi
                d = 160 + last * 40
                circle(c, 540 + math.cos(a) * d, 360 + math.sin(a) * d + last * 260, 4, hexc("ffe0a0"), a=0.9 * (1 - last))
    fade = ease_io(prog(t, 2.2, 0.8))
    for k, (x, who) in enumerate(((330, 0), (450, "me"), (590, 1), (720, 2))):
        if who == "me":
            girl(c, x, 1240, 1.4, view="front", hat=False, look=0.0, look_up=lerp(0.6, 0.2, fade),
                 mouth="laugh" if fade < 0.5 else "flat", key="g2d")
        else:
            mate(c, who, x, 1240, 1.35, look_up=0.6, mouth="laugh", k="fw")
    with keep():
        veil(c, (0.05, 0.05, 0.12), 0.15)


def kitchen_3am(c, t):
    fill_all(c, hexc("12141e"))
    with keep():                                                   # 冰箱的光
        glow(c, 860, 900, 600, hexc("cfe4ff"), 0.35)
        shape(c, rect(760, 500, 240, 740), hexc("dfe8f0"), "fridge", lw=2.4, alpha=0.9)
        line(c, [(780, 860), (980, 860)], "frl", 2)
    shape(c, rect(-20, 1240, W + 40, 700), hexc("1a1c28"), "kfl", lw=3)
    table(c, 420, 700, 1070, 1240, "ktab", hexc("3a3040"))
    chair(c, 320, 1150, 1240, "kch", hexc("3a3040"))
    down = ease_io(prog(t, 2.0, 0.6))
    with nokeep():
        with grade(sat=0.7, dark=0.25):
            girl(c, 320, 1150, 1.7, sit=True, hat=False, look=0.0 if down < 1 else 0.3, head_down=10, mouth="flat",
                 arms=[(-14, -90), (14, -90)] if down < 1 else [(-24, -70), (56, -96)], key="g2e")
    if down < 1:
        phone_at(c, lerp(320, 430, down), lerp(1150 - 90 * 1.7 + 52 * 1.7 - 14, 1062, down), 1.4, "ph2",
                 glow_a=0.6 * (1 - down) * (0.8 + 0.2 * math.sin(t * 9)))
    else:
        with keep():
            shape(c, rrect(420, 1058, 60, 12, 4), hexc("3a3f4a"), "phdown", lw=1.6)


SAD = [(cafe_clock, 3.0), (wilting, 3.0), (umbrella_give, 3.2), (fireworks, 3.4), (kitchen_3am, 5.4)]


def g02(c, t):
    t0 = 0.0
    for fn, d in SAD:
        if t < t0 + d or fn is kitchen_3am:
            return fn(c, t - t0)
        t0 += d


# ================================================================ 3–6 雾
def fog_lake(c, t, clear=0.0):
    vgrad(c, -200, 1000, [(0, hexc("c8ccd0")), (1, hexc("e4e6e6"))], -400, W + 400)
    shape(c, hill_pts(860, 30, 0.004, 1.0, -400, W + 400), hexc("b8bcc0"), "far", lw=1.4, alpha=0.6 + 0.4 * clear)
    vgrad(c, 880, 1150, [(0, hexc("c4ccd2")), (1, hexc("aeb8c0"))], -400, W + 400)
    shape(c, rect(-400, 1150, W + 800, 900), hexc("b8b2a6"), "shore", lw=3)


def g03(c, t):
    """雨停了，湖边起了大雾。她沿着岸边走，雾里隐约有几个人影；小路的尽头消失在雾里，她慢慢走了进去。"""
    fog_lake(c, t)
    with keep():
        for k in range(3):                                         # 雾里的人影，走近了又散开
            a = math.sin(prog(t, 0.5 + k * 1.0, 2.4) * math.pi)
            silhouette(c, 300 + k * 260, 1150, 1.0, f"fs{k}", col=hexc("9aa0a8"), a=0.5 * a)
    fog(c, t, 0.9, 500, 1200)
    walk = lerp(80, 760, ease_io(prog(t, 0.0, 6.5)))
    fade = ease_io(prog(t, 5.6, 2.0))
    with group_alpha(c, 1 - 0.85 * fade):
        girl(c, walk, 1260, 1.5, hat=True, walk=t * 6 if 0.2 < t < 6.5 else None, look=0.8, mouth="flat", key="g3")
    fog(c, t + 3, 0.5 + 0.4 * fade, 0, 1920)


def g04(c, t):
    k = min(int(t / 3.33), 2)
    u = t - k * 3.33
    fog_lake(c, t)
    if k == 0:                                                     # 雾墙上，她的影子旁边多了一个影子
        fog(c, t, 0.8)
        x = 300 + u * 80
        with keep():
            for j, (dx, col) in enumerate(((0, (0.35, 0.38, 0.42)), (220 + 30 * math.sin(u), (0.45, 0.48, 0.52)))):
                c.save()
                c.translate(x + dx + 120, 1000)
                c.scale(1.4, 1.9)
                silhouette(c, 0, 0, 1.0, f"sh{j}", col=hexc("6a7078"), walk=u * 5 + j, a=0.35 if j == 0 else 0.28 * math.sin(clamp(u / 3.3) * math.pi))
                c.restore()
        girl(c, x, 1260, 1.5, hat=True, walk=u * 6, look=0.8, mouth="flat", key="g4a")
    elif k == 1:                                                   # 湿沙滩上一串脚印，走着走着就没有了
        fog(c, t, 0.6)
        with keep():
            for j in range(9):
                y = 1680 - j * 90 + j * j * 3
                x = 540 + (34 if j % 2 else -34) * (1 - j * 0.06) + math.sin(j * 0.5) * 40
                s = 1.9 - j * 0.15
                shape(c, ell(x, y, 14 * s, 26 * s, 12), hexc("6a6458"), f"fp{j}", lw=0, edge=False,
                      alpha=0.75 * (1 - j / 10) * (1 - 0.3 * u / 3.3))
        fog(c, t + 2, 0.6, 600, 1500)
    else:                                                          # 栈桥尽头有个人挥手，转身走进雾里
        fog(c, t, 0.5)
        shape(c, [(560, 1920), (940, 1920), (742, 1000), (702, 1000)], WOOD, "pier", lw=2.4)
        for j in range(12):
            y = 1010 + j * j * 6.5
            v = (y - 1000) / 920
            line(c, [(lerp(702, 560, v), y), (lerp(742, 940, v), y)], f"pl{j}", 1.4, hexc("6a4a32"), alpha=0.6)
        turn = u > 1.8
        a = 0.6 * (1 - ease_io(prog(u, 2.0, 1.2)))
        with group_alpha(c, a):
            local(c, 722, 1010, 0.7, "far", hexc("6b7a8a"), hexc("2f2a28"), "short", view="back" if turn else "front",
                  arms=[(-24, -78), (40, -170 + 12 * math.sin(u * 9))] if not turn else None, walk=u * 5 if turn else None)
        fog(c, t + 1, 0.5, 700, 1200)
        girl(c, 360, 1240, 1.5, view="back", hat=True, arms=[(-24, -78), (40, -180 + 14 * math.sin(u * 9))] if u < 2.0 else None,
             key="g4c")


def g05(c, t):
    if t < 3.5:                                                    # 一滴水落进湖面，涟漪荡开又平了
        vgrad(c, 0, 1920, [(0, hexc("c4ccd2")), (1, hexc("9aa8b2"))])
        fog(c, t, 0.4)
        drop = prog(t, 0.0, 0.6)
        with keep():
            if drop < 1:
                shape(c, ell(540, lerp(200, 900, ease_in(drop)), 8, 12, 10), hexc("e4ecf2"), "drop", lw=1.4)
            for k in range(5):
                u = prog(t, 0.6 + k * 0.25, 2.4)
                if 0 < u < 1:
                    shape(c, ell(540, 900, 30 + u * 380, 10 + u * 120, 30), None, f"rip{k}", lw=2.4, alpha=0.8 * (1 - u))
        return
    lt = t - 3.5                                                   # 长椅：身边留着一小片没干的水印
    fog_lake(c, t)
    shape(c, rect(260, 1120, 560, 26), WOOD, "bench", lw=2.4)
    shape(c, rect(260, 1000, 560, 22), WOOD, "benchb", lw=2.4)
    for x in (290, 790):
        line(c, [(x, 1146), (x, 1250)], f"bl{x}", 5, hexc("5a3a2a"))
    with keep():
        shape(c, ell(650, 1124, 80, 11, 16), hexc("4a3020"), "wet", lw=0, edge=False, alpha=0.85)
        for k in range(3):                                         # 椅面边上还在往下滴
            ph = (lt * 0.7 + k / 3) % 1
            circle(c, 600 + k * 45, 1150 + ph * 90, 4, hexc("9aa8b2"), a=0.8 * (1 - ph))
    girl(c, 420, 1120, 1.5, sit=True, hat=True, look=0.6, mouth="flat", arms=[(-20, -70), (20, -70)], key="g5")
    fog(c, t, 0.5)


def g06(c, t):
    """她拿出一张纸折纸鹤，折到一半停了手，放在长椅上，起身走了。雾慢慢散开。"""
    clear = ease_io(prog(t, 2.6, 2.4))
    fog_lake(c, t, clear)
    shape(c, rect(260, 1120, 560, 26), WOOD, "bench", lw=2.4)
    shape(c, rect(260, 1000, 560, 22), WOOD, "benchb", lw=2.4)
    for x in (290, 790):
        line(c, [(x, 1146), (x, 1250)], f"bl{x}", 5, hexc("5a3a2a"))
    if t < 2.2:
        fold = math.sin(t * 5) * 6
        girl(c, 420, 1120, 1.5, sit=True, hat=True, look=0.2, head_down=8, mouth="flat",
             arms=[(-16, -76 + fold), (16, -76 - fold)], key="g6")
        crane(c, 420, 1120 - 76 * 1.5 + 52 * 1.5 + 4, 0.7, "cr6", rot=0.1 * math.sin(t * 3))
    else:
        walk = ease_in(prog(t, 2.4, 2.4))
        gx = 420 + walk * 600
        girl(c, gx, 1250 if walk > 0 else 1120, 1.5, sit=walk <= 0, hat=True, look=0.8, mouth="flat",
             walk=t * 6 if walk > 0 else None, key="g6")
        crane(c, 620, 1112, 0.8, "cr6b", rot=0.08 * math.sin(t * 2))
    fog(c, t, 0.6 * (1 - clear))


# ================================================================ 7–9 粉笔圆 → 月亮
def night_ground(c, t, moon=None, stars=1.0):
    vgrad(c, -200, 1000, [(0, NIGHT_A), (1, NIGHT_B)], -400, W + 400)
    r = random.Random(4)
    with keep():
        for k in range(50):
            star(c, r.uniform(0, W), r.uniform(0, 800), r.uniform(1.5, 3.2), stars * (0.5 + 0.5 * math.sin(t * 2 + k)))
    vgrad(c, 820, 960, [(0, hexc("2a3a5a")), (1, hexc("1e2a44"))], -400, W + 400)
    shape(c, rect(-400, 960, W + 800, 1000), hexc("3a3a48"), "ground", lw=3)
    if moon:
        crescent(c, *moon)


def g07(c, t):
    """她蹲着用粉笔画圆，画到最后差一点，接不上。皱着眉擦掉，重新画；又擦掉，又画。"""
    night_ground(c, t)
    cyc = t % 2.3
    u = ease_io(clamp(cyc / 1.7))
    erase = prog(cyc, 1.9, 0.4)
    with keep():                                                   # 擦过的地方留下淡淡的粉笔灰
        shape(c, ell(540, 1150, 190, 80, 30), CHALK, "dust7", lw=0, edge=False, alpha=0.06 * min(t / 2.3, 2))
    a0 = -0.15                                                     # 从右边开始画，缺口留在右边
    ang = a0 + (2 * math.pi - 0.32) * u
    hx, hy = 540 + math.cos(ang) * 210, 1110 + math.sin(ang) * 210 * 0.42
    open_circle_from(c, 540, 1110, 210, u, "oc7", a=1 - erase, gap=0.32, a0=a0)
    if u < 1 and erase <= 0:                                       # 粉笔头
        with keep():
            glow(c, hx, hy, 26, CHALK, 0.5)
            circle(c, hx, hy, 6, CHALK)
    lean = math.cos(ang) * 0.12                                    # 背对镜头蹲着，身子跟着粉笔转
    shake = math.sin(t * 20) * 0.06 * (erase > 0 and erase < 1)
    girl(c, 540 + math.cos(ang) * 30 * (u < 1), 1225, 1.6, view="back", sit=True, crouch=True, hat=False,
         tilt=lean + shake, key="g7")


def g08(c, t):
    """在旅行里报复性地找答案：半夜爬山赶日出、摇签筒、对着海大喊；最后在回程的车上累得睡着了。"""
    k = min(int(t / 2.1), 3)
    u = t - k * 2.1
    if k == 0:                                                     # 半夜往山顶爬，赶上日出，四处张望
        dawn = ease_io(prog(u, 0.6, 1.4))
        vgrad(c, -100, 1950, [(0, mix(NIGHT_A, hexc("f08a5a"), dawn)), (1, mix(NIGHT_B, hexc("ffd9a8"), dawn))])
        with keep():
            if dawn > 0:
                glow(c, 800, 1060, 420, hexc("ffb060"), 0.6 * dawn)
                circle(c, 800, 1160 - 160 * dawn, 70, hexc("ffcf70"))
            shape(c, [(-20, 1300), (300, 1120), (560, 1180), (900, 1080), (1100, 1150), (1100, 1300)],
                  mix(hexc("1e2030"), hexc("8a6a7a"), dawn), "far8", lw=2)
        shape(c, [(-20, 1950), (-20, 1500), (420, 1150), (560, 1160), (1100, 1560), (1100, 1950)],
              mix(hexc("2a2a3a"), hexc("6a5a5a"), dawn), "peak", lw=3)
        climb = ease_out(prog(u, 0.0, 1.0))
        look = math.sin(u * 6) if u > 1.0 else 0.6
        girl(c, lerp(200, 490, climb), lerp(1650, 1158, climb), 1.4, hat=True, pack=True, look=look, mouth="o",
             walk=u * 9 if climb < 1 else None, run=True, key="g8a")
    elif k == 1:                                                   # 寺庙里用力摇签筒，签一根根掉出来
        fill_all(c, hexc("6a3a2a"))
        for x in (140, 940):
            shape(c, rect(x - 40, 0, 80, 1300), hexc("b8302a"), f"pil{x}", lw=3)
        with keep():
            glow(c, 540, 500, 400, WARM, 0.4)
        shape(c, rect(-20, 1250, W + 40, 700), hexc("4a2a20"), "tfl", lw=3)
        shake = math.sin(u * 30) * 10
        girl(c, 480, 1180, 1.5, sit=True, crouch=True, hat=False, look=0.6, head_down=-2, mouth="o",
             arms=[(50, -66 + shake / 1.5), (62, -60 + shake / 1.5)], key="g8b")
        with keep():
            cx, cy = 480 + 74 * 1.5, 1180 - 66 * 1.5 + 52 * 1.5 - 40
            c.save()
            c.translate(cx, cy + shake)
            c.rotate(-0.4)
            shape(c, rect(-30, -50, 60, 100), hexc("c98d4a"), "tube", lw=2)
            for j in range(6):
                line(c, [(-20 + j * 8, -50), (-22 + j * 8, -90)], f"stk{j}", 3, hexc("e8d0a0"))
            c.restore()
            for j in range(3):                                     # 掉出来的签
                fu = prog(u, 0.4 + j * 0.45, 0.5)
                if fu > 0:
                    sx = cx - 40 - j * 50 - fu * 40
                    sy = lerp(cy - 60, 1240, ease_in(fu))
                    c.save()
                    c.translate(sx, sy)
                    c.rotate(fu * 2 + j)
                    line(c, [(0, -40), (0, 40)], f"fs{j}", 4, hexc("e8d0a0"))
                    c.restore()
    elif k == 2:                                                   # 深夜的海边，对着浪大喊，声音被浪吞掉
        vgrad(c, 0, 900, [(0, NIGHT_A), (1, NIGHT_B)])
        shape(c, rect(-20, 820, W + 40, 500), hexc("1e2a48"), "nsea", lw=2)
        wave = 0.5 + 0.5 * math.sin(u * 3)
        with keep():
            for j in range(4):
                y = 1060 + j * 40 - wave * 30
                line(c, [(x, y + 18 * math.sin(x * 0.02 + u * 4 + j)) for x in range(-20, W + 60, 40)], f"wv{j}", 4,
                     (0.9, 0.95, 1), alpha=0.5)
            for j in range(4):                                     # 喊出去的声音，被浪吞掉
                ph = (u * 1.2 + j / 4) % 1
                r_ = 40 + ph * 260
                c.save()
                c.arc(540, 1000, r_, math.pi * 1.2, math.pi * 1.8)
                c.set_source_rgba(1, 1, 1, 0.5 * (1 - ph))
                c.set_line_width(3)
                c.stroke()
                c.restore()
        shape(c, rect(-20, 1200, W + 40, 800), hexc("3a3a48"), "nsand", lw=3)
        girl(c, 540, 1260, 1.6, view="front", hat=True, look=0.0, look_up=0.3, mouth="o",
             arms=[(-30, -150), (30, -150)], key="g8c")
    else:                                                          # 回程的车上，累得睡着了
        fill_all(c, hexc("3a4050"))
        shape(c, rect(120, 300, 840, 520), hexc("1e2438"), "bwin", lw=4)
        with keep():
            c.save()
            c.rectangle(120, 300, 840, 520)
            c.clip()
            for j in range(6):
                x = (j * 220 - u * 700) % 1100 + 60
                glow(c, x, 560, 60, WARM, 0.5)
                circle(c, x, 560, 8, hexc("fff0b8"))
            c.restore()
        shape(c, rect(-20, 1240, W + 40, 900), hexc("2a2e3a"), "bfl", lw=3)
        shape(c, rrect(320, 870, 460, 290, 30), hexc("5a6a8a"), "seat", lw=3)
        shape(c, rect(360, 1189, 380, 51), hexc("3a4050"), "seatb", lw=2)
        girl(c, 560, 1165, 1.6, sit=True, hat=True, pack=True, look=-0.3, eyes_closed=True, mouth="flat",
             tilt=-0.18, arms=[(-20, -70), (20, -70)], key="g8d")
        shape(c, rrect(300, 1150, 500, 40, 16), hexc("6a7a9a") + (1.0,), "seatc", lw=3)


def g09(c, t):
    """她不再擦了，坐在缺口的圆旁边。粉笔圆亮起来，飘离地面，升上夜空，变成一弯月亮。她仰头看着，笑了。"""
    night_ground(c, t)
    rise = ease_io(prog(t, 1.2, 3.6))
    cx, cy = lerp(620, 760, rise), lerp(1150, 300, rise)
    r = lerp(180, 70, rise)
    morph = ease_io(prog(t, 3.4, 1.4))
    glow_a = ease_io(prog(t, 0.4, 1.0))
    with keep():
        glow(c, cx, cy, r * 2, hexc("fff3c8"), 0.35 * glow_a)
    c.save()
    c.translate(cx, cy)
    c.scale(1.0, lerp(0.42, 1.0, rise) / 0.42)
    open_circle(c, 0, 0, r, 1.0, "oc9", lw=lerp(6, 10, rise), col=mix(CHALK, hexc("fff3c8"), glow_a), a=1 - morph)
    c.restore()
    if morph > 0:
        crescent(c, cx, cy, r, a=morph)
    look = 0.5 * rise
    girl(c, 330, 1150, 1.6, sit=True, crouch=True, hat=False, look=0.5, look_up=lerp(0, 1.0, rise),
         head_down=lerp(6, -6, rise), mouth="smile" if rise > 0.6 else "flat", key="g9")


# ================================================================ 10–11 悬在那里
def regret_cup(c, t):
    fill_all(c, hexc("2a3048"))
    shape(c, rect(620, 160, 360, 420), hexc("141c36"), "cwin10", lw=4)
    c.save()
    c.rectangle(620, 160, 360, 420)
    c.clip()
    crescent(c, 820, 330, 50)
    c.restore()
    line(c, [(800, 160), (800, 580)], "cwm10", 5, hexc("4a5068"))
    with keep():
        glow(c, 800, 900, 600, hexc("cfe0ff"), 0.12)
    shape(c, rect(-20, 1240, W + 40, 900), hexc("3a3448"), "dfl", lw=3)
    table(c, 450, 900, 1070, 1240, "dtab", hexc("6a5040"))
    chair(c, 340, 1150, 1240, "dch", hexc("6a5040"))
    lift = ease_io(clamp(prog(t, 0.6, 0.8))) - ease_io(clamp(prog(t, 2.4, 0.8)))
    cup_x, cup_y = lerp(510, 440, lift), lerp(1070, 1040, lift)     # 杯子从桌上举到嘴边，再放回去
    girl(c, 340, 1150, 1.6, sit=True, hat=False, look=0.5, head_down=lerp(4, -4, lift), mouth="flat",
         eyes_closed=lift > 0.8, arms=[(-20, -70), ((cup_x - 20 - 340) / 1.6, (cup_y - 40 - 1150) / 1.6 - 52)], key="g10a")
    chipped_cup(c, cup_x, cup_y, 0.75, "cup10", steam=lift < 0.2, t=t)


def regret_balloon(c, t):
    """夜里，一只气球挂在光秃秃的树枝上：风一吹，它扯了扯，像要飞走，又停回原来的位置。飞不走，也落不下来。"""
    vgrad(c, -100, 1300, [(0, hexc("141c36")), (0.7, hexc("2c3c66")), (1, hexc("4a4e78"))], -400, W + 400)
    r = random.Random(9)
    with keep():
        for k in range(45):
            star(c, r.uniform(0, W), r.uniform(0, 1000), r.uniform(1.4, 3.0), 0.4 + 0.5 * math.sin(t * 2 + k))
    crescent(c, 250, 230, 54)
    shape(c, hill_pts(1150, 40, 0.004, 1.2, -400, W + 400, bottom=2400), hexc("1c2236"), "bhill", lw=2)
    TREE = hexc("1c2236")
    with keep():                                                   # 光秃秃的树，枝丫伸向夜空
        line(c, [(230, 1160), (250, 960), (300, 800), (380, 660)], "trunk", 26, TREE)
        for k, pts in enumerate((
                [(380, 660), (500, 560), (640, 520)],
                [(380, 660), (420, 520), (470, 400)],
                [(300, 800), (180, 680), (120, 560)],
                [(500, 560), (560, 440), (600, 380)],
                [(250, 960), (130, 900), (60, 860)],
                [(640, 520), (700, 470)],
                [(420, 520), (360, 430)])):
            line(c, pts, f"br{k}", max(4, 16 - k * 1.6), TREE)
    wind = math.sin(clamp(prog(t, 0.9, 1.8)) * math.pi)            # 一阵风
    sway = 0.12 * math.sin(t * 1.6) + 0.5 * wind * (0.7 + 0.3 * math.sin(t * 7))
    ax, ay = 690, 474                                              # 绳子缠在枝头
    L = 190
    ang = 0.35 + sway                                              # 气球往右上飘，被绳子拽着
    bx, by = ax + math.sin(ang) * L, ay - math.cos(ang) * L - 70
    with keep():
        line(c, [(ax - 4, ay + 16), (ax + 6, ay + 10), (ax, ay), ((ax + bx) / 2 - 8, (ay + by + 70) / 2 + 6), (bx, by + 72)],
             "bstr", 1.6, hexc("c8c4d8"))
        line(c, [(ax - 4, ay + 16), (ax - 10, ay + 70), (ax - 2, ay + 110)], "btail", 1.4, hexc("c8c4d8"))   # 垂下来的一截
        glow(c, bx, by, 150, hexc("f6b8c8"), 0.25)
        c.save()
        c.translate(bx, by)
        c.rotate(sway * 0.5)
        shape(c, ell(0, 0, 54, 64, 26), hexc("f2a6b4") + (1.0,), "balloon", lw=2.4)
        shape(c, [(-8, 62), (8, 62), (0, 74)], hexc("e08a9a"), "bknot", lw=1.6)
        shape(c, ell(-18, -24, 10, 18, 12), (1, 1, 1), "bhl", lw=0, edge=False, alpha=0.5)
        c.restore()
    with keep():                                                   # 风吹过的几道线
        for j in range(3):
            u = prog(t, 0.9 + j * 0.25, 1.2)
            if 0 < u < 1:
                xx = lerp(-200, 1200, u)
                line(c, [(xx, 700 + j * 70), (xx + 160, 690 + j * 70), (xx + 240, 704 + j * 70)], f"bw{j}", 2,
                     (1, 1, 1), alpha=0.4 * math.sin(u * math.pi))


def letter_and_message(c, t):
    if t < 1.8:                                                    # 写满的信，叠好又揉成一团，丢进纸篓
        fill_all(c, hexc("3a3040"))
        with keep():
            glow(c, 700, 600, 500, WARM, 0.4)
        shape(c, rect(-20, 1000, W + 40, 900), hexc("6a5040"), "desk", lw=3)
        crumple = ease_io(prog(t, 0.5, 0.5))
        toss = ease_in(prog(t, 1.1, 0.6))
        with keep():
            shape(c, [(780, 1240), (940, 1240), (920, 1440), (800, 1440)], hexc("8a8a92"), "bin", lw=2.4)
        if crumple < 1:
            with keep():
                w_, h_ = 300 * (1 - crumple * 0.85), 380 * (1 - crumple * 0.85)
                shape(c, rect(400 - w_ / 2, 820 - h_ / 2, w_, h_), hexc("f6f0e2"), "letter", lw=2)
                for k in range(8):
                    if crumple < 0.3:
                        y = 820 - h_ / 2 + 40 + k * 40
                        line(c, [(400 - w_ / 2 + 30, y), (400 + w_ / 2 - 30 - (k * 37) % 60, y)], f"lt{k}", 2,
                             hexc("6a6560"), alpha=0.7)
        else:
            bx = lerp(400, 860, toss)
            by = lerp(820, 1260, toss) - math.sin(toss * math.pi) * 260
            paper_ball(c, bx, by, 1.6, "ball")
        return
    lt = t - 1.8                                                   # 输入框里的字，一个一个删掉
    fill_all(c, hexc("1e2030"))
    with keep():
        glow(c, 540, 640, 520, hexc("cfe0ff"), 0.18)
        shape(c, rrect(220, 120, 640, 1020, 60), hexc("2a2e3a"), "phone", lw=3)
        shape(c, rect(250, 180, 580, 900), hexc("eef2f6"), "scr", lw=1)
        for k, (bx, by, bw, mine) in enumerate(((280, 240, 300, False), (500, 340, 300, True), (280, 440, 240, False))):
            shape(c, rrect(bx, by, bw, 70, 26), hexc("cfe6c8") if mine else (1, 1, 1), f"bub{k}", lw=1.6)
            for j in range(int(bw / 34) - 1):
                xx = bx + 24 + j * 30
                line(c, [(xx, by + 40), (xx + 8, by + 30), (xx + 16, by + 42), (xx + 22, by + 32)], f"bw{k}{j}", 2,
                     hexc("8a8a8a"))
        shape(c, rrect(270, 980, 450, 70, 30), (1, 1, 1), "input", lw=2)
        shape(c, ell(770, 1015, 34, 34, 16), hexc("9aa6b5"), "send", lw=2)
        line(c, [(756, 1026), (770, 1002), (784, 1026)], "senda", 3, (1, 1, 1))
        n = int(lerp(14, 0, clamp(lt / 1.4)))                       # 用波浪线代表字，看不出写了什么
        for k in range(n):
            x = 296 + k * 28
            line(c, [(x, 1022), (x + 8, 1010), (x + 16, 1024), (x + 22, 1012)], f"ch{k}", 2.4, hexc("3a3a3a"))
        if math.sin(lt * 9) > 0:
            line(c, [(300 + n * 28, 998), (300 + n * 28, 1034)], "cur", 3, hexc("3f6fb5"))


REGRETS = [regret_cup, regret_balloon, letter_and_message]


def g10(c, t):
    k = min(int(t / 3.67), 2)
    REGRETS[k](c, t - k * 3.67)


def mobile(c, t, x=540, y=150):
    """天花板上垂下来的一串挂饰：折了一半的纸鹤、缺口的杯子、一截粉笔、一团揉皱的信纸。"""
    with keep():
        line(c, [(x, 0), (x, y)], "mstr", 2, hexc("b8b0a0"))
        a = math.sin(t * 0.8) * 0.25
        c.save()
        c.translate(x, y)
        c.rotate(a)
        line(c, [(-320, 0), (320, 0)], "mbar", 5, WOOD)
        items = [(-280, 200, "crane"), (-95, 300, "cup"), (95, 170, "chalk"), (280, 250, "ball")]
        for k, (ix, ln, kind) in enumerate(items):
            sw = math.sin(t * 1.3 + k) * 8
            line(c, [(ix, 0), (ix + sw, ln)], f"mi{k}", 1.6, hexc("b8b0a0"))
            px, py = ix + sw, ln + 30
            sx = math.cos(t * 1.1 + k * 1.7)
            c.save()
            c.translate(px, py)
            c.scale(max(0.2, abs(sx)) * (1 if sx >= 0 else -1) * 1.7, 1.7)
            if kind == "crane":
                crane(c, 0, 20, 1.0, "mcr")
            elif kind == "cup":
                chipped_cup(c, 0, 80, 0.8, "mcup", steam=False)
            elif kind == "chalk":
                chalk_stick(c, 0, 0, 1.2, "mck")
            else:
                paper_ball(c, 0, 10, 1.4, "mball")
            c.restore()
        c.restore()


def g11(c, t):
    morning = ease_io(prog(t, 3.4, 1.0))
    fill_all(c, mix(hexc("2a3048"), hexc("e8dcc8"), morning))
    shape(c, rect(700, 380, 300, 380), mix(hexc("1e2a44"), hexc("cfe6f2"), morning), "rwin", lw=4)
    if morning < 1:
        c.save()
        c.rectangle(700, 380, 300, 380)
        c.clip()
        crescent(c, 860, 520, 50, a=1 - morning)
        c.restore()
    shape(c, rect(80, 520, 220, 720), mix(hexc("4a3a3a"), hexc("8c6a4a"), morning), "rdoor", lw=3)
    shape(c, rect(-20, 1240, W + 40, 700), mix(hexc("2a2830"), hexc("b89a78"), morning), "rfl", lw=3)
    mobile(c, t)
    if t < 3.4:
        shape(c, rrect(380, 920, 300, 120, 40), hexc("4a4a6a"), "pillow", lw=2.4)
        girl(c, 560, 1100, 1.5, sit=True, legs=False, hat=False, look=0.0, look_up=0.6, mouth="smile",
             arms=[(-20, -66), (20, -66)], key="g11")
        shape(c, [(330, 1240), (330, 1090), (450, 1060), (700, 1070), (810, 1100), (810, 1240)], hexc("3a3a5a"), "rbed",
              lw=3)
        if t > 2.6:
            veil(c, (0.02, 0.02, 0.06), 0.5 * prog(t, 2.6, 0.6))
    else:
        shape(c, rrect(380, 920, 300, 120, 40), mix(hexc("4a4a6a"), hexc("f4f0f8"), morning), "pillow", lw=2.4)
        shape(c, [(330, 1240), (330, 1090), (450, 1080), (700, 1085), (810, 1100), (810, 1240)],
              mix(hexc("3a3a5a"), hexc("e8e0f0"), morning), "rbed", lw=3)
        walk = ease_in(prog(t, 4.2, 2.4))
        girl(c, lerp(520, 190, walk), 1240, 1.55, hat=True, look=-0.8, mouth="smile", walk=t * 7 if walk > 0 else None,
             key="g11b")


# ================================================================ 12–14 还是会
def g12(c, t):
    k = min(int(t / 1.25), 3)
    u = t - k * 1.25
    if k == 0:                                                     # 一碗面
        fill_all(c, hexc("e8d8c0"))
        with keep():
            shape(c, ell(540, 960, 300, 300, 30), hexc("f8f6f0"), "bowl", lw=3)
            shape(c, ell(540, 960, 250, 250, 30), hexc("e8b060"), "soup", lw=2)
            for j in range(10):
                line(c, [(380 + j * 34, 900), (400 + j * 30, 1020)], f"nd{j}", 4, hexc("f4e2a8"))
            lift = math.sin(u * 8) * 40
            line(c, [(520, 960 - lift), (700, 400)], "chop1", 6, WOOD)
            line(c, [(560, 960 - lift), (760, 420)], "chop2", 6, WOOD)
            for j in range(3):
                ph = (u * 0.8 + j / 3) % 1
                shape(c, ell(480 + j * 60, 700 - ph * 200, 30, 18, 10), (1, 1, 1), f"st{j}", lw=0.8, alpha=0.6 * (1 - ph))
    elif k == 1:                                                   # 闹钟响，把被子拉过头顶
        fill_all(c, hexc("c8d0e0"))
        shape(c, rect(660, 920, 340, 1000), WOOD, "nstand", lw=3)
        with keep():
            shake = math.sin(u * 40) * 6
            for sg in (-1, 1):
                shape(c, ell(810 + shake + sg * 52, 760, 24, 16, 12), hexc("e8743a"), f"bell{sg}", lw=2)
            shape(c, ell(810 + shake, 840, 80, 80, 24), hexc("e8743a"), "alarm", lw=3)
            shape(c, ell(810 + shake, 840, 62, 62, 20), (1, 1, 1), "alarmf", lw=2)
            line(c, [(810 + shake, 840), (810 + shake, 800)], "alh", 3)
            line(c, [(810 + shake, 840), (838 + shake, 852)], "alm", 3)
            for j in range(3):                                     # 铃声
                ph = (u * 2.5 + j / 3) % 1
                c.save()
                c.arc(810, 820, 100 + ph * 90, -math.pi * 0.45, -math.pi * 0.05)
                c.set_source_rgba(0.9, 0.45, 0.23, 0.6 * (1 - ph))
                c.set_line_width(3)
                c.stroke()
                c.restore()
        shape(c, rrect(120, 900, 340, 110, 40), hexc("f4f0f8"), "pil12", lw=2.4)
        girl(c, 300, 1080, 1.5, sit=True, legs=False, hat=False, look=0.3, eyes_closed=True, mouth="flat",
             tilt=-0.25, key="g12b")
        hide = ease_io(prog(u, 0.45, 0.35))
        qy = lerp(1010, 860, hide)
        shape(c, [(-20, 1940), (-20, qy + 40), (180, qy), (460, qy + 10), (600, 1010), (640, 1040), (640, 1940)],
              hexc("e8b8a8") + (1.0,), "quilt2", lw=3)
    elif k == 2:                                                   # 电脑前敲键盘
        fill_all(c, hexc("dcdcd4"))
        shape(c, rect(-20, 1080, W + 40, 900), hexc("b8a888"), "wdesk", lw=3)
        with keep():
            glow(c, 760, 960, 180, hexc("cfe4ff"), 0.3)
            shape(c, rrect(650, 890, 220, 150, 10), hexc("3a3f4a"), "lap", lw=2.4)
            shape(c, rect(664, 902, 192, 126), hexc("cfe4ff"), "laps", lw=1)
            for j in range(4):
                line(c, [(678, 924 + j * 26), (840 - (j * 37) % 70, 924 + j * 26)], f"lpl{j}", 2, hexc("6a7a8a"))
            shape(c, [(620, 1080), (900, 1080), (880, 1040), (640, 1040)], hexc("8a909a"), "kb", lw=2)
        tap = math.sin(u * 30) * 8
        girl(c, 520, 1080, 1.6, sit=True, legs=False, hat=False, look=0.8, mouth="flat",
             arms=[(52, -40 + tap), (66, -40 - tap)], key="g12c")
    else:                                                          # 追着公交车跑，挤了上去
        rain_city(c, u, dark=-0.3)
        with keep():
            shape(c, rrect(560, 900, 600, 330, 30), hexc("3f8fb0"), "bus", lw=3)
            for j in range(4):
                shape(c, rect(600 + j * 130, 940, 100, 110), hexc("dfeef4"), f"bw{j}", lw=2)
            door = ease_io(prog(u, 0.7, 0.4))
            shape(c, rect(560, 960, 70 * door + 4, 250), hexc("2f6f90"), "door", lw=2)
        x = lerp(100, 560, ease_in(clamp(u / 0.9)))
        girl(c, x, 1240, 1.6, hat=True, walk=u * 14, run=True, look=0.9, mouth="o", key="g12d")


def dusk_street(c, t, crowd=True, cloud_glow=1.0):
    vgrad(c, -900, 1000, [(0, hexc("6a8ac8")), (0.55, hexc("f2a6a0")), (1, hexc("ffd9a8"))], -400, W + 400)
    with keep():                                                   # 天边一大朵被夕阳染色的云
        for k, (dx, dy, rx, ry) in enumerate(((0, 0, 260, 140), (-200, 40, 200, 120), (210, 50, 220, 110),
                                              (-80, -90, 200, 120), (120, -70, 180, 110), (-330, 90, 140, 80),
                                              (340, 100, 150, 80))):
            shape(c, ell(560 + dx, 300 + dy, rx, ry, 24), mix(hexc("ffc8b0"), hexc("ffe0a0"), (k % 3) / 2), f"bc{k}",
                  lw=0, edge=False, alpha=0.9 * cloud_glow)
        glow(c, 560, 320, 520, hexc("ffd0a0"), 0.35 * cloud_glow)
    r = random.Random(3)
    x = -40
    i = 0
    while x < W + 40:
        w_, h_ = r.uniform(140, 220), r.uniform(240, 420)
        shape(c, rect(x, 1000 - h_, w_, h_), hexc(r.choice(["8a7a8a", "9a8a8a", "7a6a7a"])), f"db{i}", lw=2)
        x += w_ + 8
        i += 1
    shape(c, rect(-20, 1000, W + 40, 900), hexc("b8a898"), "dsw", lw=3)
    if crowd:
        for k in range(8):
            sp = 90 + (k % 3) * 30
            xx = (k * 157 + t * sp * (1 if k % 2 else -1)) % 1300 - 100
            silhouette(c, xx, 1110 + (k % 4) * 25, 1.2, f"dcw{k}", col=hexc("7a6a7a"), walk=t * 6 + k, a=0.6)


def g13(c, t):
    """下班的人行道，人来人往。她忽然停住抬头：天边一大朵云被夕阳染成粉色和金色。"""
    up = ease_io(prog(t, 1.4, 2.6))
    with cam(c, 540, 1150, lerp(1.7, 1.0, up)):
        dusk_street(c, t)
        stop = t > 1.2
        x = lerp(380, 540, ease_out(prog(t, 0.0, 1.4)))
        girl(c, x, 1250, 1.55, hat=True, walk=t * 7 if not stop else None, look=0.8 if not stop else 0.0,
             look_up=min(1.0, 0.4 + up), mouth="smile" if up > 0.5 else "flat", key="g13")


def g14(c, t):
    if t < 4.6:
        k = min(int(t / 1.53), 2)
        u = t - k * 1.53
        if k == 0:                                                 # 热腾腾的一碗，吃了第一口，闭上眼睛
            fill_all(c, hexc("e8c8a0"))
            with keep():
                glow(c, 540, 700, 500, WARM, 0.5)
            shape(c, rect(-20, 1080, W + 40, 900), hexc("8c5a3c"), "ntab", lw=3)
            girl(c, 540, 1080, 1.6, sit=True, legs=False, hat=False, look=0.0, eyes_closed=u > 0.3, mouth="smile",
                 head_down=-4 if u > 0.3 else 6, arms=[(-24, -60), (24, -60)], key="g14a")
            with keep():
                shape(c, ell(540, 1050, 170, 26, 22), hexc("e8a050"), "nsoup", lw=2)
                shape(c, ell(540, 1050, 170, 110, 26, 0, math.pi), hexc("f8f6f0"), "nb", lw=2.4)
                line(c, [(400, 1100), (680, 1100)], "nbd", 3, hexc("c96f6f"))
                for j in range(4):
                    ph = (u * 0.9 + j / 4) % 1
                    shape(c, ell(470 + j * 45, 1010 - ph * 200, 26, 14, 10), (1, 1, 1), f"ns{j}", lw=0.8, alpha=0.6 * (1 - ph))
        elif k == 1:                                               # 桥上一阵风
            vgrad(c, 0, 1000, [(0, hexc("8fc4ea")), (1, hexc("f4e6d0"))])
            shape(c, rect(-20, 1000, W + 40, 900), hexc("6f9ac0"), "river", lw=2)
            line(c, [(-20, 1110), (W + 20, 1110)], "brail", 6, hexc("8c7a62"))
            for j in range(12):
                line(c, [(j * 95, 1110), (j * 95, 1190)], f"brp{j}", 3, hexc("8c7a62"))
            shape(c, rect(-20, 1190, W + 40, 900), hexc("b8a488"), "bdeck", lw=3)
            with keep():
                for j in range(5):
                    yy = 700 + j * 90
                    xx = (u * 1200 + j * 240) % 1400 - 200
                    line(c, [(xx, yy), (xx + 180, yy - 10), (xx + 260, yy + 6)], f"wd{j}", 2.4, (1, 1, 1), alpha=0.6)
            girl(c, 540, 1250, 1.6, hat=True, look=0.3, look_up=0.3, eyes_closed=True, mouth="smile", key="g14b")
            with keep():                                           # 帽带被风吹起来
                for j in range(2):
                    line(c, [(540 + 26 * 1.6, 1250 - 168 * 1.6), (540 + 60 * 1.6, 1250 - (172 - j * 8) * 1.6 + 6 * math.sin(u * 12 + j)),
                             (540 + 95 * 1.6, 1250 - (166 - j * 12) * 1.6 + 10 * math.sin(u * 12 + j + 1))], f"rib{j}", 4,
                         hexc("bf4a3c"))
        else:                                                      # 公园长椅，和老人一起笑；跷跷板上两个孩子
            vgrad(c, 0, 1000, [(0, hexc("9fd0ec")), (1, hexc("f4efe4"))])
            shape(c, rect(-20, 1000, W + 40, 900), hexc("a8c48b"), "pkg", lw=3)
            kx, ky = 820 + 30 * math.sin(u * 2), 420 + 20 * math.sin(u * 3)   # 远处一个孩子在放风筝
            with keep():
                line(c, [(850, 1060 - 150 * 0.9), (kx, ky + 60)], "kstr", 1.4, hexc("6a6a6a"))
                shape(c, [(kx, ky - 50), (kx + 36, ky), (kx, ky + 60), (kx - 36, ky)], hexc("e8743a"), "kite", lw=2)
                line(c, [(kx, ky + 60), (kx - 10 + 10 * math.sin(u * 6), ky + 120), (kx + 6, ky + 170)], "ktail", 2,
                     hexc("d9433a"))
            local(c, 830, 1060, 0.9, "kid", hexc("9fc5e8"), hexc("2f2a28"), "short", look=0.5, look_up=0.8,
                  mouth="laugh", arms=[(-20, -80), (22, -150)])
            shape(c, rect(160, 1150, 520, 24), WOOD, "pb", lw=2.4)
            shape(c, rect(160, 1040, 520, 20), WOOD, "pbb", lw=2.4)
            laugh = math.sin(u * 10) * 3
            girl(c, 300, 1150, 1.5, sit=True, hat=True, look=0.6, mouth="laugh", tilt=laugh * 0.01, key="g14c")
            local(c, 520, 1150, 1.5, "oldman", hexc("6b7a8a"), hexc("e3ddd5"), "short", sit=True, look=-0.6, mouth="laugh",
                  arms=[(-24, -70), (40, -100)])
        return
    lt = t - 4.6                                                   # 黄昏回家，路灯一盏盏亮起来，天上又挂着那弯月亮
    vgrad(c, 0, 1000, [(0, hexc("3a4a7a")), (1, hexc("e8a090"))])
    crescent(c, 820, 260, 56, a=0.9)
    shape(c, rect(-20, 1000, W + 40, 900), hexc("8a7a7a"), "hst", lw=3)
    for k in range(4):
        x = 120 + k * 280
        on = clamp((lt - 0.65 - k * 0.75) * 3)
        line(c, [(x, 1000), (x, 640)], f"lp{k}", 6, hexc("3a3a3a"))
        with keep():
            if on > 0:
                glow(c, x, 640, 200, WARM, 0.55 * on)
            circle(c, x, 640, 12, mix(hexc("9a9a9a"), hexc("fff0b8"), on))
    walk = lerp(160, 700, lt / 4.8)
    bob = abs(math.sin(lt * 7)) * 6
    girl(c, walk, 1250 - bob, 1.55, hat=True, walk=lt * 7, look=0.8, mouth="smile", arms=[(-24, -78), (40, -86)], key="g14d")
    with keep():                                                   # 一袋菜
        bx, by = walk + 40 * 1.55, 1250 - bob - 86 * 1.55
        shape(c, [(bx - 30, by), (bx + 30, by), (bx + 38, by + 70), (bx - 38, by + 70)], hexc("e8e0d0"), "bag", lw=2)
        for j, col in enumerate(("6fa860", "d9433a", "e8c040")):
            shape(c, ell(bx - 16 + j * 16, by - 4, 12, 10, 10), hexc(col), f"veg{j}", lw=1)


# ================================================================ 15 很多答案，都是走了很久很久才明白的
def long_road(c, t, lamps_on):
    """从她身后看出去的一条长路，路灯一盏接一盏亮到远处。"""
    vgrad(c, -500, 900, [(0, hexc("1a2244")), (0.6, hexc("3a4a7a")), (1, hexc("d89a8c"))], -400, W + 400)
    r = random.Random(6)
    with keep():
        for k in range(40):
            star(c, r.uniform(-100, W + 100), r.uniform(-480, 500), r.uniform(1.5, 3.0), 0.4 + 0.4 * math.sin(t * 2 + k))
    crescent(c, 800, 180, 56)
    shape(c, hill_pts(860, 26, 0.006, 0.4, -400, W + 400, bottom=2400), hexc("4a4458"), "rfar", lw=2)
    VY = 900
    shape(c, [(-600, 2400), (530, VY), (550, VY), (1700, 2400)], hexc("7a6a72"), "road15", lw=3)
    with keep():
        for k in range(14):                                        # 路中间的虚线
            z0, z1 = 1.4 + k * 0.9, 1.4 + k * 0.9 + 0.4
            line(c, [(540, VY + 1100 / z0), (540, VY + 1100 / z1)], f"dash{k}", max(1.0, 9 / z0), hexc("d8c8b0"),
                 alpha=0.6)
    for k, z in enumerate((1.6, 2.3, 3.2, 4.4, 6.0, 8.2, 11.0, 15.0)):
        for sg in (-1, 1):
            x, y, h = 540 + sg * 820 / z, VY + 1100 / z, 620 / z
            on = clamp((lamps_on - k * 0.45) * 3)
            line(c, [(x, y), (x, y - h)], f"lp15{k}{sg}", max(1.2, 9 / z), hexc("2e2e3a"))
            with keep():
                if on > 0:
                    glow(c, x, y - h, 260 / z, WARM, 0.6 * on)
                circle(c, x, y - h, max(2.0, 16 / z), mix(hexc("8a8a8a"), hexc("fff0b8"), on))
    return VY


def g15(c, t):
    """接着回家的路，镜头慢慢升高拉远：路变得很长，她变成路上一个小小的身影，不紧不慢地往前走。
    后来她停下来，一颗流星从头顶划过——就是这一个瞬间。"""
    rise = ease_io(prog(t, 1.2, 5.6))
    with cam(c, 540, 960, 1.0, ty=rise * 150):
        VY = long_road(c, t, t * 2.2)
        z = lerp(3.0, 7.0, prog(t, 0.0, 7.0))
        x, y, sc = 540 + 70 / z, VY + 1100 / z, 3.6 / z
        girl(c, x, y, sc, view="back", hat=True, walk=min(t, 7.6) * 6, key="g15")
        mt = prog(t, 8.6, 1.1)                                     # 她停下来的那一刻，一颗流星划过
        if 0 < mt < 1:
            with keep():
                hx, hy = lerp(1000, 360, mt), lerp(-120, 200, mt)
                fade = math.sin(mt * math.pi)
                for j in range(12):                                # 越往后越淡的尾巴
                    f0, f1 = j / 12, (j + 1) / 12
                    line(c, [(hx + 260 * f0, hy - 130 * f0), (hx + 260 * f1, hy - 130 * f1)], f"mt{j}",
                         max(1.0, 7 * (1 - f0)), hexc("fff6d8"), alpha=(1 - f0) * fade)
                circle(c, hx, hy, 6, hexc("fffaf0"), a=fade)
                glow(c, hx, hy, 70, hexc("fff6d8"), 0.5 * math.sin(mt * math.pi))
        with keep():                                               # 一袋菜
            bx, by = x + 36 * sc, y - 72 * sc
            shape(c, [(bx - 16 * sc, by), (bx + 16 * sc, by), (bx + 20 * sc, by + 38 * sc), (bx - 20 * sc, by + 38 * sc)],
                  hexc("e8e0d0"), "bag15", lw=1.6)


# ================================================================ 片尾
_STILL = {}


def end_still():
    if "s" not in _STILL:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(120.0)
        with grade(sat=1.0, dark=0.0, warm=0.1):
            g15(cc, 6.9)
        _STILL["s"] = surf
    return _STILL["s"]


def outro(c, t):
    book_outro(c, t, end_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第六章 · 完")

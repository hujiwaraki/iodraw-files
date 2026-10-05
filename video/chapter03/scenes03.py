"""第三章 · 从游客到旅人 —— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。"""
import math
import os
import random
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter01"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter02"))
from draw import *  # noqa: F401,F403,E402
from engine import book_intro, book_outro  # noqa: E402
from scenes import GROUND, panel, street_bg  # noqa: E402
from scenes_v2 import local  # noqa: E402
from scenes02 import (COUPLE_COLS, RED, DESK, c09_alone, c10_eyes, eye, gaze, heart, phone_at, tinbox,  # noqa: E402
                      travel_ticket, TICKET_KINDS, _STILL)

SKIN_L = hexc("e8c09a")
GRAN = hexc("e3ddd5")


# ================================================================ 通用
def pull(c, x, y, s, key, walk=None, d=1, bump=0.0, **kw):
    """她拉着行李箱：d=1 向右（箱子在左后方）。bump：石子路上的颠簸。"""
    kw.setdefault("hat", True)
    kw.setdefault("look", 0.9 * d)
    arms = [(-26, -76), (-40, -70)] if d > 0 else [(-26, -76), (40, -70)]
    girl(c, x, y, s, walk=walk, arms=arms, key=key, **kw)
    jig = math.sin(bump * 37) * 4 * (bump > 0)
    suitcase(c, x - d * 58 * s, y + 2 * s + jig, 0.6 * s, key + "su",
             tilt=(0.15 * d + math.sin(bump * 23) * 0.06 * (bump > 0)) if walk is not None else 0.0)


def cobbles(c, y0, y1, key, seed=3):
    shape(c, rect(-20, y0, W + 40, y1 - y0 + 400), hexc("a39a8c"), key + "g", lw=3)
    r = random.Random(seed)
    yy = y0 + 12
    row = 0
    while yy < y1 + 300:
        sz = 14 + (yy - y0) * 0.05
        xx = -20 + (row % 2) * sz
        while xx < W + 20:
            shape(c, ell(xx + r.uniform(-3, 3), yy, sz * 0.9, sz * 0.5, 10), hexc("8f877a"), f"{key}{row}_{int(xx)}",
                  lw=1.2, amp=0.6)
            xx += sz * 2
        yy += sz * 0.95
        row += 1


def old_town(c, t, base, key, lit=False, dark=False, hs=1.0):
    """石子路边的老房子。"""
    cols = [("e8d6b8", "8c5a3c"), ("d9c4a8", "6b4a32"), ("efe2c8", "a8613f"), ("cfc2ae", "5a5d66")]
    x = -40
    i = 0
    while x < W + 40:
        w_ = (160 + (i * 37) % 60) * max(hs, 0.6)
        h_ = (300 + (i * 53) % 160) * hs
        wall, roof = cols[i % 4]
        house(c, x, base, w_, h_, hexc(wall), hexc(roof), f"{key}{i}", "tri" if i % 2 else "flat",
              win=hexc("cfd8e0"), lit=3 if lit else None)
        x += w_ + 4
        i += 1
    if dark:
        veil(c, (0.06, 0.07, 0.14), 0.55)


def street_lamp(c, x, base, key, on=1.0):
    line(c, [(x, base), (x, base - 300)], key + "p", 6, hexc("3a3a3a"))
    shape(c, [(x - 22, base - 300), (x + 22, base - 300), (x + 14, base - 330), (x - 14, base - 330)], hexc("3a3a3a"),
          key + "h", lw=2)
    if on > 0:
        with keep():
            glow(c, x, base - 290, 220, hexc("ffd98a"), 0.55 * on)
            shape(c, ell(x, base - 296, 14, 6, 10), hexc("fff0b8"), key + "b", lw=1, amp=0.2, alpha=on)


# ================================================================ 片头
def bag_illus(c, cx, cy):
    """章节页小插画：一只行李箱旁边放着一个背包。"""
    with keep():
        suitcase(c, cx - 50, cy + 70, 0.55, "bi_su", handle=0.5)
        shape(c, rrect(cx + 10, cy - 10, 80, 84, 18), PACK, "bi_pk", lw=2.4)
        shape(c, rrect(cx + 18, cy + 30, 64, 30, 8), darker(PACK, 0.85), "bi_pkp", lw=1.8)
        line(c, [(cx + 30, cy - 10), (cx + 40, cy - 28), (cx + 60, cy - 28), (cx + 70, cy - 10)], "bi_h", 3)


def intro(c, t):
    book_intro(c, t, "第三章", "从游客到旅人", bag_illus)


# ================================================================ 一、第二张票
def desk_scene(c, t, lamp_glow=0.6):
    fill_all(c, hexc("4a4038"))
    glow(c, 320, 520, 760, hexc("ffd8a0"), lamp_glow)
    line(c, [(320, 0), (320, 380)], "lcord", 3, hexc("2e2824"))
    shape(c, [(250, 380), (390, 380), (430, 470), (210, 470)], hexc("d9a65a"), "lshade", lw=3)


def d01_ticket(c, t):
    desk_scene(c, t)
    girl(c, 540, 1010, 2.1, sit=True, legs=False, hat=False, look=0.0, head_down=6, look_up=-0.8, mouth="smile",
         arms=[(-30, -60), (30, -60)] if t < 1.6 else [(-12, -96), (12, -96)], key="g1")
    shape(c, rect(-40, 1010, W + 80, 600), DESK, "desk", lw=3)
    tinbox(c, 540, 1170, 0.9, "b1", n=8)
    up = ease_io(prog(t, 1.2, 1.4))
    zoom = ease_io(prog(t, 2.8, 1.8))
    if up > 0:
        x = lerp(540, 540, zoom)
        y = lerp(1050, 760, up) if zoom <= 0 else lerp(760, 820, zoom)
        s = lerp(0.5, 0.9, up) * lerp(1.0, 2.4, zoom)
        travel_ticket(c, x, y, s, "train", "tk2", age=0.7, rot=lerp(-0.2, 0.0, up), seed=5)
    melt = ease_io(prog(t, 5.2, 2.4))
    if melt > 0:
        with group_alpha(c, melt), grade(sat=0.15, warm=0.0):
            vgrad(c, 0, 780, [(0, hexc("c9d1d8")), (1, hexc("e4e5e1"))])
            old_town(c, t, 780, "mt")
            cobbles(c, 780, 1500, "mc")


# ================================================================ 二、并不浪漫
def p_cobble(c, t, w, h):
    vgrad(c, 0, h, [(0, hexc("c9d1d8")), (1, hexc("e4e5e1"))], 0, w)
    old_town(c, t, 210, "pc", hs=0.55)
    cobbles(c, 210, h, "pcs")
    x = lerp(200, 700, ease_io(t / 5.0))
    pull(c, x, 410, 1.35, "gpc", walk=t * 5, bump=t, mouth="sad", head_down=8, look_up=-0.4)
    with keep():
        for k in range(2):                                         # 汗珠
            ph = (t * 1.2 + k * 0.5) % 1
            shape(c, ell(x + 34 + k * 12, 410 - 160 * 1.35 + ph * 30, 5, 7, 8), hexc("9fc5e8"), f"sw{k}", lw=1,
                  amp=0.2, alpha=1 - ph)
        for k in range(3):                                         # 轮子的颠簸
            line(c, [(x - 110 + k * 8, 420 + k * 4), (x - 136 + k * 8, 416 + k * 4)], f"bp{k}", 2, hexc("6a6f7d"),
                 alpha=0.6 * abs(math.sin(t * 9 + k)))


def p_night(c, t, w, h):
    fill_all(c, hexc("1d2235"))
    old_town(c, t, 300, "pn", lit=False, dark=True, hs=0.6)
    shape(c, rect(-20, 330, w + 40, h), hexc("2e3242"), "png", lw=2.4)
    for i, x in enumerate((160, 520, 880)):
        flick = 1.0 if i != 1 else (0.2 + 0.8 * (math.sin(t * 13) > -0.2) * (math.sin(t * 3.1) > -0.6))
        street_lamp(c, x, 340, f"nl{i}", on=flick)
    with grade(dark=0.2):                                          # 拉长的影子
        for i, x in enumerate((60, 760)):
            c.save()
            c.translate(x, 500)
            c.scale(1.0, 1.9)
            silhouette(c, 0, 0, 1.0, f"nsh{i}", col=hexc("0d0f18"), a=0.5)
            c.restore()
    x = lerp(220, 640, ease_io(t / 5.0))
    lookback = math.sin(t * 2.2) > 0.3
    girl(c, x, 500, 1.4, hat=True, walk=t * 10, look=-1.0 if lookback else 0.8, mouth="flat",
         arms=[(-24, -78), (22, -100)], key="gpn")
    phone_at(c, x + 22 * 1.4, 500 - 104 * 1.4, 1.0, "nph", glow_a=0.5)


def d02_hard(c, t):
    fill_all(c, hexc("e8e2d6"))
    panel(c, 60, 150, 960, 440, ease_back(prog(t, 0.15, 0.5)), "hp1", p_cobble, t, rot=-0.008)
    panel(c, 60, 640, 960, 560, ease_back(prog(t, 5.0, 0.5)), "hp2", p_night, t - 5.0, rot=0.006)


def d03_alone(c, t):
    c09_alone(c, t)


def d04_eyes(c, t):
    c10_eyes(c, t)


# ================================================================ 三、路过的游客
def landmark(c, x, base, s, kind, key):
    """几种不写名字的“网红景点”：塔、城门、桥。"""
    c.save()
    c.translate(x, base)
    c.scale(s, s)
    if kind == "tower":
        for k in range(4):
            w_ = 150 - k * 28
            shape(c, rect(-w_ / 2, -120 - k * 110, w_, 110), hexc("c9a46a"), f"{key}b{k}", lw=2.4)
            shape(c, [(-w_ / 2 - 26, -120 - k * 110), (w_ / 2 + 26, -120 - k * 110), (0, -160 - k * 110)],
                  hexc("8c5a3c"), f"{key}r{k}", lw=2.4)
        shape(c, rect(-60, -120, 120, 120), hexc("b48a4f"), key + "base", lw=2.4)
    elif kind == "gate":
        shape(c, rect(-260, -260, 520, 260), hexc("b9a587"), key + "w", lw=3)
        shape(c, ell(0, -90, 80, 110, 20, math.pi, 2 * math.pi) + [(80, 0), (-80, 0)], hexc("4a4038"), key + "door", lw=2.4)
        shape(c, [(-300, -260), (300, -260), (240, -340), (-240, -340)], hexc("6b4a32"), key + "roof", lw=3)
        with keep():
            shape(c, rect(-90, -230, 180, 50), hexc("c9473b"), key + "sign", lw=2)
            text(c, "景 区", 0, -194, 34, hexc("f4e2b0"))
    else:
        shape(c, ell(0, 0, 320, 150, 30, math.pi, 2 * math.pi), hexc("b7b2a7"), key + "arch", lw=3)
        shape(c, ell(0, 0, 230, 90, 30, math.pi, 2 * math.pi), hexc("9fc5e8"), key + "hole", lw=2.4)
        line(c, [(-320, -150), (320, -150)], key + "rail", 5, hexc("6b5a4a"))
    c.restore()


def guidebook(c, x, y, s, key, open_=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with keep():
        shape(c, rect(-30, -40, 60, 80), hexc("3f6fb5"), key, lw=2)
        for k, col in enumerate(("f7e27a", "f2a6a0", "a8e07a", "9fc5e8", "f7e27a")):
            shape(c, rect(30, -36 + k * 15, 12, 10), hexc(col), f"{key}t{k}", lw=1, amp=0.2)
        text(c, "攻略", 0, 8, 18, (1, 1, 1))
    c.restore()


def d05_tourist(c, t):
    vgrad(c, 0, 900, [(0, hexc("8fc3e3")), (1, hexc("e9f2f6"))])
    glow(c, 860, 160, 260, hexc("fff3b0"), 0.7)
    landmark(c, 540, 860, 1.4, "gate", "lmg")
    shape(c, rect(-20, 860, W + 40, 900), hexc("d6cbb2"), "plaza", lw=3)
    for i in range(8):
        line(c, [(-10, 890 + i * i * 9), (W + 10, 890 + i * i * 9)], f"pz{i}", 1.6, hexc("c0b59b"), alpha=0.6)
    r = random.Random(5)
    for i in range(16):                                            # 人山人海的队伍
        x = 120 + (i % 8) * 110 + r.uniform(-20, 20) + math.sin(t + i) * 4
        y = 960 + (i // 8) * 60
        silhouette(c, x, y, 1.0, f"q{i}", a=0.7, col=[hexc("8d95a3"), hexc("a3958d"), hexc("8da395")][i % 3])
        if i % 5 == 0:
            line(c, [(x + 20, y - 130), (x + 20, y - 200)], f"qf{i}", 2.4, hexc("6b4a32"))
            with keep():
                shape(c, [(x + 20, y - 200), (x + 50, y - 192), (x + 20, y - 184)], hexc("e8c040"), f"qff{i}", lw=1.4)
    pull(c, 540, 1250, 1.5, "g5", mouth="flat", look=-0.2)
    guidebook(c, 540 + 30 * 1.5, 1250 - 100 * 1.5, 1.2, "gb5")
    with keep():                                                   # 好热
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1
            line(c, [(520 + k * 20, 1250 - 260 * 1.5 - ph * 40), (514 + k * 20, 1250 - 280 * 1.5 - ph * 40)], f"ht{k}", 2,
                 hexc("e8743a"), alpha=1 - ph)


CHECK_ITEMS = ["网红桥", "古城门", "观景塔", "必吃小吃", "日落机位", "纪念品店"]


def checklist(c, x, y, n_done, key, scale=1.0):
    c.save()
    c.translate(x, y)
    c.scale(scale, scale)
    with keep():
        shape(c, rect(0, 0, 260, 60 + 48 * len(CHECK_ITEMS)), hexc("fbf6e8"), key, lw=2.4)
        text(c, "必去清单", 130, 42, 28, INK)
        for i, it in enumerate(CHECK_ITEMS):
            yy = 70 + i * 48
            shape(c, rect(20, yy, 28, 28), (1, 1, 1), f"{key}b{i}", lw=1.8, amp=0.2)
            text(c, it, 62, yy + 24, 24, INK, a=0.5 if i < n_done else 1.0, anchor="l")
            if i < n_done:
                line(c, [(22, yy + 14), (32, yy + 26), (52, yy - 6)], f"{key}c{i}", 4, RED)
    c.restore()


def d06_checkin(c, t):
    k = min(int(t / 2.3), 2)
    lt = t - k * 2.3
    kinds = ["bridge", "gate", "tower"]
    skies = [("9fc5e8", "e9f2f6"), ("f2c79a", "fbe6c4"), ("b9c3e8", "eef0f6")]
    vgrad(c, 0, 900, [(0, hexc(skies[k][0])), (1, hexc(skies[k][1]))])
    landmark(c, 540, 860, 1.3, kinds[k], f"lm{k}")
    shape(c, rect(-20, 860, W + 40, 900), hexc("d6cbb2"), "plz6", lw=3)
    for i in range(5):
        x = (i * 230 + 80) % 1100
        silhouette(c, x, 960 + (i % 2) * 40, 1.0, f"cq{i}", a=0.55, walk=t * 6 + i)
    girl(c, 480, 1240, 1.5, look=0.3, mouth="laugh", arms=[(-24, -80), (44, -168)], key=f"g6{k}")
    with keep():                                                   # 比剪刀手
        hx, hy = 480 - 24 * 1.5, 1240 - 80 * 1.5
        line(c, [(hx, hy), (hx - 6, hy - 26)], "v1", 4, SKIN)
        line(c, [(hx, hy), (hx + 8, hy - 26)], "v2", 4, SKIN)
    phone_at(c, 480 + 44 * 1.5, 1240 - 180 * 1.5, 1.1, "p6", glow_a=0.3)
    f = 1 - ease_out(prog(lt, 0.9, 0.3))
    if 0 < f < 1:
        veil(c, (1, 1, 1), 0.4 * f)
    suitcase(c, 620, 1244, 0.9, "su6", handle=0.4)
    n = k * 2 + (1 if lt > 1.2 else 0) + (1 if lt > 1.8 else 0)
    checklist(c, 700, 120, n, "cl6", 1.0)
    for j in range(6):                                             # 赶路的速度线
        yy = 1060 + j * 30
        line(c, [(-20 + (t * 900 + j * 170) % 1200, yy), (60 + (t * 900 + j * 170) % 1200, yy)], f"spd{j}", 2,
             hexc("b7b2a7"), alpha=0.5)


def d07_album(c, t):
    fill_all(c, hexc("d9d6ce"))
    px, py, pw, ph = 220, 120, 640, 1100
    with keep():
        glow(c, 540, 650, 600, hexc("dfeaff"), 0.4)
        shape(c, rrect(px - 18, py - 18, pw + 36, ph + 36, 48), hexc("3a3f4a"), "alb", lw=3)
        shape(c, rect(px, py, pw, ph), hexc("f6f6f6"), "als", lw=0, edge=False)
        text(c, "相册", px + pw / 2, py + 60, 32, INK)
        scroll = ease_io(prog(t, 0.4, 3.0)) * 520
        c.save()
        c.rectangle(px, py + 90, pw, ph - 90)
        c.clip()
        skies = ["9fc5e8", "f2c79a", "b9c3e8", "a9c48b", "f2a6a0", "c9d1d8"]
        kinds = ["bridge", "gate", "tower"]
        for i in range(24):
            cx = px + 16 + (i % 3) * 206
            cy = py + 110 + (i // 3) * 206 - scroll
            if cy < py - 220 or cy > py + ph:
                continue
            c.save()
            c.rectangle(cx, cy, 196, 196)
            c.clip()
            vgrad(c, cy, cy + 196, [(0, hexc(skies[i % 6])), (1, (0.97, 0.96, 0.93))], cx, cx + 196)
            landmark(c, cx + 98, cy + 170, 0.28, kinds[i % 3], f"al{i}")
            girl(c, cx + 98, cy + 196, 0.7, look=0.2, mouth="laugh", arms=[(-24, -80), (44, -168)], key=f"ag{i}")
            c.restore()
            shape(c, rect(cx, cy, 196, 196), None, f"alf{i}", lw=1.6, amp=0.2)
        c.restore()
    dz = ease_io(prog(t, 3.6, 1.0))
    if dz > 0:
        with group_alpha(c, dz):
            veil(c, (0.95, 0.94, 0.9), 0.5)
            girl(c, 540, 1260, 1.9, look=0.0, mouth="o", head_down=4, look_up=-0.6,
                 arms=[(-14, -96), (14, -96)], key="g7")


# ================================================================ 四、慢慢变了
def d08_wider(c, t):
    k = 1.25 - 0.25 * ease_io(prog(t, 0.0, 3.0))
    with cam(c, 540, 1000, k):
        vgrad(c, 0, 1000, [(0, hexc("7fb2d8")), (0.7, hexc("cfe6f2")), (1, hexc("f4efe4"))])
        glow(c, 760, 520, 500, hexc("fff3c8"), 0.6)
        for i, (base, amp, col) in enumerate(((760, 60, "a9b8cc"), (820, 50, "8fa8a0"), (880, 40, "7f9a7a"))):
            shape(c, hill_pts(base, amp, 0.006 + i * 0.002, i * 1.3), hexc(col), f"wh{i}", lw=2.4)
        shape(c, rect(560, 800, 600, 60), hexc("6fa8c8"), "sea", lw=2)            # 远处的海
        x = 120
        r = random.Random(4)
        while x < 520:                                                           # 远处的城市
            hh = r.uniform(40, 110)
            shape(c, rect(x, 840 - hh, 30, hh), hexc("9aa6b5"), f"cty{int(x)}", lw=1.4, amp=0.3)
            x += 36
        for i in range(4):
            cloud(c, (i * 300 + t * 25) % 1300 - 120, 300 + i * 60, 1.1, f"wc{i}", a=0.8)
        shape(c, [(-40, 1900), (-40, 1180), (360, 1060), (700, 1090), (1120, 1220), (1120, 1900)], hexc("6f7a6a"), "cliff",
              lw=3)
    push = ease_io(prog(t, 2.8, 0.8))
    walk = t > 4.4
    x = 540 + (ease_in(prog(t, 4.4, 1.6)) * 260)
    girl(c, x, 1100, 1.7, view="back" if not (2.4 < t < 4.4) else "front", hat=True, mouth="laugh",
         head_down=lerp(6, 0, push), look_up=lerp(-0.6, 0.4, push), walk=t * 7 if walk else None,
         arms=[(-24, -78), (lerp(24, 18, push) if push < 0.99 else 24, lerp(-78, -190, push * (1 - prog(t, 3.8, 0.4))))],
         key="g8")


def split_frame(c, t, top_fn, bot_fn, reveal):
    """上下分屏：上半格“以前”（灰），下半格“后来”（彩色）。"""
    fill_all(c, hexc("e8e2d6"))
    for (y0, h, fn, k, lab, sat) in ((120, 540, top_fn, 1.0, "以前", 0.25), (700, 540, bot_fn, reveal, "后来", 1.0)):
        if k <= 0.01:
            continue
        c.save()
        c.rectangle(60, y0, 960, h)
        c.clip()
        c.translate(60, y0)
        with grade(sat=sat):
            fn(c, t, 960, h)
        c.restore()
        shape(c, rect(60, y0, 960, h), None, f"sf{y0}", lw=5, amp=1.0)
        with keep():
            shape(c, rrect(80, y0 + 18, 110, 50, 12), hexc("fbf6e8"), f"sl{y0}", lw=2)
            text(c, lab, 135, y0 + 54, 30, INK)
    if reveal < 1:
        veil(c, (0.91, 0.89, 0.84), 0)


def s_plan(c, t, w, h):
    fill_all(c, hexc("e9e2d4"))
    shape(c, rect(60, 60, 340, 360), hexc("f4efe6"), "cal", lw=2.4)
    shape(c, rect(60, 60, 340, 60), hexc("c0503c"), "calh", lw=2)
    for i in range(5):
        for j in range(6):
            text(c, str(1 + i * 6 + j), 90 + j * 52, 160 + i * 56, 22, INK, a=0.7)
    with keep():
        shape(c, ell(90 + 4 * 52 + 6, 160 + 3 * 56 - 8, 26, 22, 14), None, "calc", lw=3)
    shape(c, rect(470, 40, 400, 440), hexc("fbf6e8"), "list", lw=2.4)
    n = int(clamp(t / 0.3, 0, 12))
    for i in range(n):
        line(c, [(500, 80 + i * 32), (500 + 80 + (i * 53) % 220, 80 + i * 32)], f"li{i}", 2.4, hexc("6a6f7d"))
    girl(c, 900, 520, 0.9, hat=False, look=-0.8, mouth="flat", arms=[(-36, -100), (24, -78)], key="gpl")


def s_book(c, t, w, h):
    vgrad(c, 0, h, [(0, hexc("f6e6c8")), (1, hexc("fbf3e2"))], 0, w)
    with keep():
        shape(c, rrect(120, 80, 220, 380, 26), hexc("3a3f4a"), "bph", lw=2.4)
        shape(c, rect(134, 100, 192, 340), hexc("eef4ff"), "bps", lw=1)
        text(c, "08:00", 230, 150, 34, INK)
        shape(c, rrect(150, 330, 160, 60, 20), hexc("4f9a5c") if t > 1.2 else hexc("e8743a"), "bbtn", lw=1.6)
        text(c, "已出票" if t > 1.2 else "订票", 230, 370, 26, (1, 1, 1))
    shape(c, rect(420, 60, 500, 400), hexc("cfe0ea"), "gwin", lw=3)
    plane(c, 640 + t * 30, 300, 1.4, "gpl")
    with keep():
        shape(c, rect(470, 70, 180, 60), hexc("2e3449"), "gsign", lw=1.6)
        text(c, "14:00 登机", 560, 112, 26, hexc("f6e08a"))
    girl(c, 820, 520, 0.95, hat=True, look=-0.5, mouth="laugh", pack=True, key="gbk")


def s_stuff(c, t, w, h):
    fill_all(c, hexc("e2dccd"))
    sq = math.sin(t * 6) * 6
    with keep():
        shape(c, rrect(300, 230 + sq, 380, 240 - sq, 20), hexc("8b6f9a"), "bigsu", lw=3)
        for k in range(5):                                         # 塞不下的衣服
            shape(c, ell(330 + k * 70, 230 + sq, 34, 16, 12), hexc(["f2a6a0", "9fc5e8", "f7e27a", "a8e07a", "f2d0c8"][k]),
                  f"cl{k}", lw=1.6, amp=0.4)
    girl(c, 490, 230 + sq, 1.0, sit=True, hat=False, mouth="flat", look=0.0, arms=[(-60, -40), (60, -40)], key="gsit")
    with keep():
        for k in range(3):
            line(c, [(260 - k * 10, 300 + k * 30), (230 - k * 10, 296 + k * 30)], f"st{k}", 2.4, hexc("8a8f99"))


def s_pack(c, t, w, h):
    vgrad(c, 0, h, [(0, hexc("eaf2e2")), (1, hexc("fbf6ec"))], 0, w)
    with keep():
        shape(c, ell(780, 120, 70, 70, 24), (1, 1, 1), "clk", lw=2.4)
        a = t * 2.4
        line(c, [(780, 120), (780 + math.sin(a) * 50, 120 - math.cos(a) * 50)], "clkh", 3)
        text(c, "10 分钟", 780, 230, 28, INK)
    if t < 2.2:
        with keep():
            shape(c, rrect(300, 300, 150, 170, 30), PACK, "bpk", lw=3)
            u = prog(t, 0.2, 1.6)
            for k in range(3):
                uu = clamp(u * 3 - k)
                shape(c, ell(lerp(560, 375, uu), lerp(240, 330, uu), 30, 14, 12),
                      hexc(["9fc5e8", "f7e27a", "f2a6a0"][k]), f"pc{k}", lw=1.4, amp=0.3, alpha=1 - uu * 0.8)
        girl(c, 600, 500, 1.0, hat=True, look=-0.7, mouth="smile", arms=[(-50, -90), (24, -78)], key="gpk")
    else:
        x = lerp(420, 1100, ease_in(prog(t, 2.4, 1.6)))
        girl(c, x, 500, 1.0, hat=True, look=0.9, mouth="laugh", walk=t * 9, run=True, pack=True, key="gpk2")


def s_flag(c, t, w, h):
    vgrad(c, 0, h, [(0, hexc("c9d1d8")), (1, hexc("e4e5e1"))], 0, w)
    landmark(c, 700, 380, 0.9, "tower", "sfl")
    shape(c, rect(-20, 380, w + 40, 200), hexc("d6cbb2"), "sfg", lw=2.4)
    local(c, 140, 500, 1.0, "sguide", hexc("c9473b"), hexc("2f2a28"), "short", look=0.6, arms=[(-24, -78), (20, -150)],
          walk=t * 5)
    line(c, [(160, 350), (160, 260)], "sfp", 3, hexc("6b4a32"))
    with keep():
        shape(c, [(160, 260), (200, 270), (160, 280)], hexc("e8c040"), "sff", lw=1.6)
    for i in range(5):
        silhouette(c, 260 + i * 70, 500, 0.95, f"sq{i}", walk=t * 5 + i, a=0.6)
    girl(c, 640, 500, 0.95, hat=True, look=-0.6, mouth="flat", walk=t * 5, key="gfl")
    checklist(c, 760, 30, int(clamp(t / 0.8, 0, 6)), "cl11", 0.7)


def s_alley(c, t, w, h):
    vgrad(c, 0, h, [(0, hexc("fbe6c4")), (1, hexc("f6efe0"))], 0, w)
    shape(c, [(0, 0), (330, 120), (330, h - 60), (0, h)], hexc("e8c9a0"), "awl", lw=2.4)
    shape(c, [(w, 0), (w - 330, 120), (w - 330, h - 60), (w, h)], hexc("d9b48a"), "awr", lw=2.4)
    shape(c, [(330, h - 60), (w - 330, h - 60), (w, h), (0, h)], hexc("c9b59a"), "afl", lw=2.4)
    with keep():
        for i in range(4):                                         # 晾着的衣服、花盆
            x = 360 + i * 60
            shape(c, rect(x, 150 + (i % 2) * 10, 40, 50), hexc(["f2a6a0", "9fc5e8", "f7e27a", "a8e07a"][i]), f"lau{i}",
                  lw=1.4)
        for i, (x, y) in enumerate(((120, 300), (920, 280))):
            shape(c, rect(x - 20, y, 40, 30), hexc("c97a4a"), f"pot{i}", lw=1.6)
            shape(c, ell(x, y - 6, 28, 18, 12), hexc("6fa860"), f"plt{i}", lw=1.4)
    walk = t > 1.6
    x = lerp(300, 540, ease_io(prog(t, 1.6, 2.2)))
    s = lerp(1.0, 0.75, ease_io(prog(t, 1.6, 2.2)))
    girl(c, x, 520 - 40 * ease_io(prog(t, 1.6, 2.2)), s, hat=True, pack=True, look=0.3, mouth="smile",
         walk=t * 6 if walk else None, arms=[(-30, -110), (24, -78)] if not walk else None, key="gal")
    if not walk:
        with keep():                                               # 手绘地图
            shape(c, rect(300 - 30 * 1.0 - 50, 520 - 150, 80, 60), hexc("f4e7c8"), "amap", lw=1.6)
            line(c, [(260, 400), (280, 385), (300, 400)], "amr", 1.6, RED)


PAIRS = [(s_plan, s_book), (s_stuff, s_pack), (s_flag, s_alley)]


def d09_split(c, t):
    k = min(int(t / 8.0), 2)
    lt = t - k * 8.0
    top, bot = PAIRS[k]
    reveal = ease_io(prog(lt, 3.6, 0.6))

    def topf(cc, tt, w, h):
        top(cc, lt, w, h)

    def botf(cc, tt, w, h):
        bot(cc, max(0.0, lt - 3.8), w, h)

    split_frame(c, t, topf, botf, reveal)


# ================================================================ 五、走进当地人的生活
def town_bg(c, t, base=900, morning=False):
    vgrad(c, 0, base, [(0, hexc("f3c79a") if morning else hexc("9fd0ec")), (1, hexc("fbecd0") if morning else hexc("eef6f2"))])
    cols = [("f1c27d", "b4533f"), ("8fc0b5", "3f6f73"), ("f3e3c3", "3c6ea5"), ("e98f6f", "8b4a3a"), ("c9d98a", "6b7a3a")]
    x = -30
    i = 0
    while x < W + 30:
        w_ = 150 + (i * 41) % 70
        h_ = 260 + (i * 67) % 180
        wall, roof = cols[i % 5]
        house(c, x, base, w_, h_, hexc(wall), hexc(roof), f"tw{i}", "tri" if i % 2 == 0 else "flat")
        x += w_ + 6
        i += 1
    shape(c, rect(-20, base, W + 40, 1000), hexc("e2d2b2"), "tg", lw=3)


def d10_town(c, t):
    town_bg(c, t)
    line(c, [(780, 1100), (780, 880)], "spost", 6, hexc("6b4a32"))
    with keep():
        for i, (dy, d) in enumerate(((880, 1), (930, -1), (980, 1))):
            pts = [(780, dy), (780 + d * 130, dy), (780 + d * 152, dy + 18), (780 + d * 130, dy + 36), (780, dy + 36)]
            shape(c, pts, hexc(["f4e2b0", "f2d0c8", "dfe9f5"][i]), f"arr{i}", lw=2)
    for i in range(4):
        bx = (200 + i * 160 + t * 40) % 1200 - 60
        by = 260 + i * 30 + math.sin(t * 2 + i) * 10
        line(c, [(bx - 14, by - 6), (bx, by), (bx + 14, by - 6)], f"tb{i}", 2.2, hexc("3a3f4a"))
    breath = math.sin(prog(t, 0.6, 2.4) * math.pi)
    girl(c, 480, 1180, 1.7 * (1 + 0.02 * breath), hat=True, pack=True, look=0.3, mouth="o" if breath > 0.5 else "smile",
         eyes_closed=breath > 0.5, look_up=0.5 * breath, key="g10")


def d11_costume(c, t):
    town_bg(c, t, base=760)
    shape(c, rect(80, 640, 920, 30), hexc("8c5a3c"), "rack", lw=3)
    with keep():                                                   # 挂着的衣服
        r = random.Random(3)
        for i in range(8):
            x = 120 + i * 110
            col = [hexc("2f7f8a"), hexc("c9473b"), hexc("e8c040"), hexc("8d6a9f")][i % 4]
            shape(c, [(x - 34, 670), (x + 34, 670), (x + 46, 840), (x - 46, 840)], col, f"dr{i}", lw=2)
            line(c, [(x - 40, 800), (x + 40, 800)], f"drz{i}", 3, hexc("f0c040"))
    shape(c, rect(-20, 1000, W + 40, 900), hexc("d9c39a"), "cg", lw=3)
    changed = t > 1.6
    curtain = math.sin(prog(t, 1.1, 1.0) * math.pi)
    tie = ease_io(prog(t, 2.0, 1.2))
    spin = t > 3.6
    sx = math.cos(prog(t, 3.6, 1.2) * 2 * math.pi) if spin else 1.0
    girl(c, 480, 1230, 1.7, hat=True, outfit="folk" if changed else None, look=0.6 if not spin else 0.0,
         mouth="laugh" if spin else "smile", sx=max(abs(sx), 0.1) * (1 if sx >= 0 else -1), key="g11")
    local(c, 720, 1230, 1.6, "auntie", hexc("c98d72"), GRAN, "granny", look=-0.9, mouth="laugh",
          arms=[(-60 - 10 * math.sin(t * 8) * (2.0 < t < 3.2), -96), (-48, -90)] if t < 3.4 else [(-24, -78), (24, -78)])
    with keep():                                                   # 小镜子
        shape(c, rrect(880, 900, 110, 200, 40), hexc("8c5a3c"), "mirf", lw=3)
        shape(c, rrect(892, 912, 86, 176, 34), hexc("dfeefa"), "mir", lw=1.6)
    if curtain > 0.01:
        with keep():
            shape(c, [(330, 800), (630, 800), (620, 1260), (340, 1260)], hexc("c9473b"), "curt", lw=3, alpha=curtain)


def produce(c, x, y, kind, key, s=1.0):
    with keep():
        if kind == 0:
            for k in range(5):
                shape(c, ell(x - 40 + (k % 3) * 34, y - (k // 3) * 22, 18 * s, 16 * s, 12), hexc("d9433a"), f"{key}{k}",
                      lw=1.4, amp=0.3)
        elif kind == 1:
            for k in range(4):
                shape(c, [(x - 40 + k * 22, y), (x - 34 + k * 22, y - 50), (x - 24 + k * 22, y)], hexc("6fa860"),
                      f"{key}{k}", lw=1.4, amp=0.3)
        elif kind == 2:
            for k in range(4):
                shape(c, ell(x - 30 + k * 20, y - 6, 10, 26, 10), hexc("e8c040"), f"{key}{k}", lw=1.4, amp=0.3)
        else:
            for k in range(5):
                shape(c, ell(x - 40 + k * 20, y - 4, 12, 9, 10), hexc("c98d4a"), f"{key}{k}", lw=1.4, amp=0.3)


def d12_market(c, t):
    fill_all(c, hexc("f2e6cf"))
    for i in range(3):                                             # 摊位的棚子
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
    gx = lerp(200, 520, walk)
    local(c, gx + 160, 1230, 1.6, "landlady", hexc("8d6a9f"), GRAN, "granny", look=0.4, mouth="laugh",
          walk=t * 6 if walk < 1 else None)
    haggle = 2.4 < t < 5.0
    girl(c, gx, 1230, 1.6, hat=True, pack=True, look=0.6 if not haggle else -0.6, mouth="laugh" if haggle else "smile",
         walk=t * 6 if walk < 1 else None, arms=[(-30, -60), (30 + 10 * math.sin(t * 9) * haggle, -110 if haggle else -76)],
         key="g12")
    with keep():                                                   # 越装越满的菜篮
        bx, by = gx - 30 * 1.6, 1230 - 60 * 1.6
        shape(c, [(bx - 34, by - 10), (bx + 34, by - 10), (bx + 26, by + 34), (bx - 26, by + 34)], hexc("d9b778"), "bsk",
              lw=2)
        n = int(clamp(t / 1.2, 0, 5))
        for k in range(n):
            shape(c, ell(bx - 22 + (k % 3) * 22, by - 14 - (k // 3) * 14, 12, 10, 10),
                  hexc(["d9433a", "6fa860", "e8c040", "c98d4a", "d9433a"][k]), f"bk{k}", lw=1.2, amp=0.2)
        if haggle:                                                 # 比划着讲价
            for k, (txt, xx) in enumerate((("3 ?", 300), ("2 !", 620))):
                a = math.sin(prog(t, 2.4 + k * 0.9, 1.4) * math.pi)
                if a > 0:
                    shape(c, rrect(xx - 50, 520 - 60, 100, 70, 20), (1, 1, 1), f"hb{k}", lw=2, alpha=a)
                    text(c, txt, xx, 520 - 12, 36, INK, a=a)


def d13_cook(c, t):
    if t < 4.6:
        fill_all(c, hexc("e8dcc4"))
        for i in range(6):
            shape(c, rect(80 + i * 160, 160, 120, 90), hexc("dfe9ea"), f"tile{i}", lw=1.6, amp=0.4)
        shape(c, rect(60, 820, 960, 380), hexc("8c7a62"), "counter", lw=3)
        shape(c, rect(60, 800, 960, 30), hexc("b9a587"), "ctop", lw=2.4)
        with keep():                                               # 灶台和锅
            glow(c, 760, 760, 140, hexc("ff9a50"), 0.5 + 0.2 * math.sin(t * 9))
            shape(c, ell(760, 780, 120, 34, 20, 0, math.pi), hexc("3a3a3a"), "wok", lw=3)
            for k in range(6):
                ph = (t * 0.7 + k / 6) % 1
                shape(c, ell(700 + k * 22 + math.sin(t + k) * 10, 720 - ph * 300, 30 + ph * 40, 18 + ph * 20, 12),
                      (1, 1, 1), f"smk{k}", lw=0.8, amp=0.4, alpha=0.5 * (1 - ph))
            shape(c, rect(260, 770, 220, 30), hexc("d9b778"), "board", lw=2)
            r = random.Random(4)
            for k in range(int(clamp(t / 0.3, 0, 10))):
                sz = r.uniform(6, 18)
                shape(c, rect(290 + k * 18, 760 - sz, sz, sz), hexc("6fa860"), f"veg{k}", lw=1, amp=0.3)
        local(c, 860, 1200, 1.6, "cookgran", hexc("8d6a9f"), GRAN, "granny", look=-0.8, mouth="laugh",
              arms=[(-50, -96), (24, -78)] if t > 2.2 else [(-24, -78), (40, -110)])
        girl(c, 380, 1200, 1.6, hat=False, look=0.3, mouth="laugh" if t > 2.4 else "flat",
             arms=[(-20, -110 + 10 * math.sin(t * 14)), (40, -112)], key="g13")
    else:
        lt = t - 4.6
        fill_all(c, hexc("f2e2c4"))
        glow(c, 540, 400, 700, hexc("ffe2a8"), 0.6)
        line(c, [(540, 0), (540, 200)], "kl", 3)
        shape(c, [(480, 200), (600, 200), (630, 260), (450, 260)], hexc("d9a65a"), "klamp", lw=2.4)
        seats = [(200, "8d6a9f", GRAN, "granny"), (340, "6b7a5a", hexc("3a3a3a"), "short"),
                 (740, "c98d72", hexc("2f2a28"), "bang_short"), (880, "5d7a9a", hexc("2f2a28"), "short")]
        for i, (x, col, hr, st) in enumerate(seats):
            local(c, x, 980, 1.4, f"fam{i}", hexc(col), hr, st, sit=True, legs=False, mouth="laugh",
                  look=0.5 if x < 540 else -0.5, arms=[(-20, -70), (30 + 10 * math.sin(lt * 6 + i), -80)])
        girl(c, 540, 980, 1.4, sit=True, legs=False, hat=False, mouth="laugh", look=0.0, arms=[(-30, -80), (30, -80)],
             key="g13b")
        shape(c, ell(540, 1040, 470, 110, 40), hexc("eee7d8"), "ftab", lw=3)
        shape(c, [(70, 1040), (1010, 1040), (990, 1250), (90, 1250)], hexc("c9473b"), "fcloth", lw=3)
        cols = ["d9653a", "6fa860", "e8c040", "b5533a", "8a6a4a", "f2a6a0"]
        for i in range(6):
            a = i * math.pi / 3
            x, y = 540 + math.cos(a) * 260, 1030 + math.sin(a) * 50
            shape(c, ell(x, y, 56, 18, 16), hexc("f8f6f0"), f"fd{i}", lw=2, amp=0.4)
            shape(c, ell(x, y - 4, 38, 10, 14), hexc(cols[i]), f"ff{i}", lw=1.6, amp=0.3)
            line(c, [(x - 6, y - 16), (x - 12 + math.sin(lt * 2 + i) * 6, y - 50), (x - 2, y - 80)], f"fs{i}", 2, (1, 1, 1),
                 alpha=0.6)


def gun_shape(c, x, y, s, key):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with keep():
        shape(c, [(-10, -10), (50, -10), (50, 2), (6, 2), (2, 26), (-12, 26), (-6, 2), (-10, 2)], hexc("3a3f4a"), key,
              lw=1.6, amp=0.2)
    c.restore()


def target(c, x, y, r, key, holes):
    with keep():
        for k, col in enumerate(("f4f2ec", "3a3f4a", "f4f2ec", "3a3f4a", "c9473b")):
            rr = r * (1 - k * 0.2)
            shape(c, ell(x, y, rr, rr, 30), hexc(col), f"{key}{k}", lw=1.6, amp=0.2)
        for i, (dx, dy) in enumerate(holes):
            circle(c, x + dx * r, y + dy * r, 6, hexc("1d1d1d"))


def d14_shoot(c, t):
    fill_all(c, hexc("c9c4b8"))
    for i in range(4):                                             # 一条条靶道
        x = 120 + i * 260
        shape(c, [(x, 1100), (x + 220, 1100), (x + 170, 520), (x + 50, 520)], hexc("b9b2a4"), f"lane{i}", lw=2)
    target(c, 540, 600, 110, "tg", [(0.55, -0.4)] if t < 3.6 else [(0.55, -0.4), (0.16, 0.1)])
    shape(c, rect(-20, 1060, W + 40, 60), hexc("8c7a62"), "bench", lw=3)
    local(c, 800, 1230, 1.6, "coach", hexc("6b7a5a"), hexc("2f2a28"), "short", look=-0.8, mouth="laugh",
          arms=[(-90, -130), (-70, -110)] if t < 1.6 else ([(-60, -170), (24, -78)] if t > 4.4 else [(-24, -78), (24, -78)]))
    with keep():
        line(c, [(800 - 42, 1230 - 156 * 1.6), (800, 1230 - 196 * 1.6), (800 + 42, 1230 - 156 * 1.6)], "cmuff", 5, hexc("3f6fb5"))
        for sg in (-1, 1):
            shape(c, ell(800 + sg * 42, 1230 - 150 * 1.6, 12, 18, 12), hexc("3f6fb5"), f"cmf{sg}", lw=2)
    aim = 0.8 < t < 4.4
    five = t > 4.4
    gx, gy, gs = 520, 1230, 1.6
    if aim:                                                        # 背对镜头，对着靶子举枪
        girl(c, gx, gy, gs, view="back", hat=False, key="g14")
        with keep():                                               # 双手向前举起
            for sg in (-1, 1):
                line(c, [(gx + sg * 17 * gs, gy - 118 * gs), (gx + sg * 6 + 40, gy - 150 * gs)], f"aim{sg}", 7, COAT)
        gun_shape(c, gx + 40, gy - 162 * gs, 1.2, "gun")
        for tf in (2.0, 3.6):
            f = 1 - ease_out(prog(t, tf, 0.25))
            if 0 < f < 1:
                with keep():
                    glow(c, gx + 60, gy - 180 * gs, 60, hexc("ffe08a"), 0.8 * f)
    else:
        girl(c, gx, gy, gs, hat=False, look=0.6, mouth="laugh",
             arms=[(-24, -78), (60, -170)] if five else None, key="g14")
    with keep():                                                   # 耳罩
        hx, hy = gx, gy - 150 * gs
        line(c, [(hx - 46, hy - 6), (hx, hy - 52), (hx + 46, hy - 6)], "muff", 6, hexc("c9473b"))
        for sg in (-1, 1):
            shape(c, ell(hx + sg * 46, hy, 14, 20, 12), hexc("c9473b"), f"mf{sg}", lw=2)
    if five:
        with keep():
            star(c, 700, gy - 175 * gs, 12, ease_out(prog(t, 4.6, 0.3)), hexc("fff3b0"))


def d15_alley(c, t):
    vgrad(c, 0, 900, [(0, hexc("f6c99a")), (1, hexc("fbecd0"))])
    glow(c, 540, 300, 600, hexc("fff0c0"), 0.6)
    shape(c, [(0, 0), (300, 200), (300, 1000), (0, 1300)], hexc("e2c49c"), "lw", lw=3)
    shape(c, [(W, 0), (W - 300, 200), (W - 300, 1000), (W, 1300)], hexc("d6b48c"), "rw", lw=3)
    shape(c, [(300, 1000), (W - 300, 1000), (W + 40, 1900), (-40, 1900)], hexc("c9b59a"), "lf", lw=3)
    # 早点铺：掀开蒸笼
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
    # 背着书包跑过的孩子
    for i in range(2):
        x = lerp(-100, 1200, ((t * 0.25 + i * 0.4) % 1))
        local(c, x, 1260 + i * 30, 1.0, f"kid{i}", hexc(["f2a6a0", "9fc5e8"][i]), hexc("2f2a28"), "short", walk=t * 12 + i,
              run=True, pack=True, look=1.0, mouth="laugh")
    # 点头打招呼的老人
    nod = 6 * max(0.0, math.sin(prog(t, 2.6, 1.0) * math.pi))
    local(c, 860, 1180, 1.4, "oldman", hexc("6b7a8a"), GRAN, "short", look=-0.7, head_down=nod, mouth="smile")
    girl(c, 560, 1220, 1.6, hat=True, pack=True, look=0.6 if t > 2.4 else 0.0, head_down=nod, mouth="smile",
         walk=t * 6 if t < 2.4 else None, key="g15")


def d16_bubble(c, t):
    d12_market(c, 4.5 + t * 0.5)
    grow = ease_back(prog(t, 0.4, 0.8))
    pop = prog(t, 3.4, 0.5)
    cx, cy = 540, 430
    if pop <= 0 and grow > 0.01:
        with keep():
            c.save()
            c.translate(cx, cy)
            c.scale(grow, grow)
            pts = []
            for i in range(80):
                a = i / 80 * 2 * math.pi
                rr = 1 + 0.04 * math.cos(a * 11)
                pts.append((math.cos(a) * 360 * rr, math.sin(a) * 250 * rr))
            c.save()
            spath(c, pts, True)
            c.clip()
            vgrad(c, -260, 260, [(0, hexc("3b3a6e")), (0.7, hexc("c8708a")), (1, hexc("f2b27a"))], -380, 380)
            for k in range(14):
                star(c, -300 + (k * 53) % 600, -200 + (k * 37) % 200, 3, 0.8)
            shape(c, ell(0, 210, 300, 40, 24), hexc("e8b0a0"), "dground", lw=1.6, alpha=0.7)
            for k in range(5):
                with keep():
                    glow(c, -260 + k * 130, -120 + (k % 2) * 40, 40, hexc("ffb070"), 0.6)
                    shape(c, ell(-260 + k * 130, -120 + (k % 2) * 40, 16, 20, 12), hexc("d9433a"), f"dl{k}", lw=1.4)
            girl(c, 0, 210, 1.9, outfit="folk", hat=True, mouth="laugh", sx=max(0.2, abs(math.cos(t * 2.5))), key="gdream")
            c.restore()
            spath(c, pts, True)
            c.set_source_rgba(1, 1, 1, 0.5)
            c.set_line_width(6)
            c.stroke()
            c.restore()
            for k, (x, y, r) in enumerate(((470, 760, 14), (500, 700, 20))):
                shape(c, ell(x, y, r * grow, r * grow, 12), (1, 1, 1), f"tb{k}", lw=2, alpha=0.8)
    if 0 < pop < 1:
        r = random.Random(5)
        with keep():
            for k in range(30):
                a = r.uniform(0, 2 * math.pi)
                d = 200 + pop * 260
                star(c, cx + math.cos(a) * d * 1.3, cy + math.sin(a) * d * 0.8, 5 * (1 - pop) + 1, 1 - pop,
                     hexc("fff3d0"))


def d17_table(c, t):
    fill_all(c, hexc("e6d6b8"))
    glow(c, 540, 300, 700, hexc("ffe2a0"), 0.6)
    line(c, [(540, 0), (540, 160)], "tl", 3)
    shape(c, [(480, 160), (600, 160), (630, 220), (450, 220)], hexc("c98d4a"), "tlamp", lw=2.4)
    with keep():                                                   # 墙上的菜单
        shape(c, rect(700, 260, 280, 300), hexc("3a3f4a"), "menu", lw=2.4)
        for k in range(5):
            line(c, [(730, 310 + k * 48), (930 - (k * 37) % 80, 310 + k * 48)], f"mn{k}", 3, hexc("f6e08a"), alpha=0.8)
    local(c, 820, 1060, 1.5, "boss", hexc("f4f2ec"), hexc("3a3a3a"), "short", look=-0.8, mouth="laugh",
          arms=[(-40, -110), (24, -78)] if t > 1.0 else [(-24, -78), (24, -78)])
    with keep():
        shape(c, [(820 - 36, 1060 - 130), (820 + 36, 1060 - 130), (820 + 40, 1060 - 40), (820 - 40, 1060 - 40)],
              hexc("c9473b"), "apron", lw=2)
    cheers = t > 4.2
    girl(c, 380, 1000, 1.5, sit=True, legs=False, hat=False, mouth="laugh", look=0.7,
         arms=[(-20, -70), (40, -150)] if cheers else [(-20, -70), (30 + 8 * math.sin(t * 7), -86)], key="g17")
    if cheers:
        with keep():
            shape(c, [(380 + 32, 1000 - 170 + 52), (380 + 56, 1000 - 170 + 52), (380 + 52, 1000 - 140 + 52),
                      (380 + 36, 1000 - 140 + 52)], hexc("f2d98a"), "cup", lw=1.8)
    shape(c, rect(120, 1000, 840, 26), hexc("8c5a3c"), "tab", lw=3)
    for x in (150, 920):
        shape(c, rect(x, 1026, 16, 160), hexc("7a4d33"), f"tl{x}", lw=2.4)
    cols = ["d9653a", "6fa860", "e8c040", "b5533a", "8a6a4a"]
    for i in range(5):                                              # 一桌菜
        x = 220 + i * 140
        shape(c, ell(x, 990, 60, 18, 16), hexc("f8f6f0"), f"td{i}", lw=2, amp=0.4)
        shape(c, ell(x, 986, 42, 10, 14), hexc(cols[i]), f"tf{i}", lw=1.6, amp=0.3)
        line(c, [(x - 6, 972), (x - 12 + math.sin(t * 2 + i) * 6, 940), (x - 2, 910)], f"ts{i}", 2, (1, 1, 1), alpha=0.6)
    # 邻桌的视线：一根根变淡
    for i, x in enumerate((90, 150)):
        silhouette(c, x, 1180, 1.0, f"nb{i}", a=0.6)
    fade = 1 - ease_io(prog(t, 1.4, 4.0))
    if fade > 0.01:
        gaze(c, 90, 1180 - 150, 360, 820, 1.0, "nz1", a=0.7 * fade, show_eye=False)
        gaze(c, 150, 1180 - 150, 380, 830, 1.0, "nz2", a=0.7 * fade, show_eye=False)


# ================================================================ 七、回到现在
def postcard(c, x, y, s, key):
    """盒底一张没用过的明信片：蓝白色的海岛。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with keep():
        shape(c, rect(-150, -100, 300, 200), hexc("fbfaf6"), key, lw=2.4, amp=0.3)
        c.save()
        c.rectangle(-138, -88, 276, 176)
        c.clip()
        vgrad(c, -88, 88, [(0, hexc("5fa8e0")), (0.55, hexc("bfe0f2")), (0.56, hexc("2f6fb8")), (1, hexc("3f8fd0"))], -140, 140)
        shape(c, [(-140, 20), (-60, -10), (40, 0), (140, 30), (140, 90), (-140, 90)], hexc("f4f2ec"), key + "isl", lw=1.6)
        for k, (hx, hy) in enumerate(((-90, 10), (-40, 0), (10, 6), (60, 14))):
            shape(c, rect(hx, hy, 34, 26), (1, 1, 1), f"{key}h{k}", lw=1.2, amp=0.2)
            if k % 2 == 0:
                shape(c, ell(hx + 17, hy, 14, 12, 12, math.pi, 2 * math.pi), hexc("2f6fb8"), f"{key}d{k}", lw=1.2,
                      amp=0.2)
        shape(c, ell(90, -50, 18, 18, 14), hexc("fff3b0"), key + "sun", lw=1.2)
        c.restore()
    c.restore()


def d18_desk(c, t):
    if t < 5.0:
        fill_all(c, DESK)
        for i in range(9):
            line(c, [(-20, 120 + i * 150), (W + 20, 140 + i * 150)], f"grain{i}", 2, hexc("7a4d33"), alpha=0.6)
        glow(c, 360, 300, 900, hexc("ffd8a0"), 0.35)
        r = random.Random(9)
        for i in range(18):                                        # 早期是景点门票，后来是汽车票、早班机
            x, y = 180 + (i % 4) * 220 + r.uniform(-30, 30), 220 + (i // 4) * 210 + r.uniform(-20, 20)
            k = ease_back(prog(t, 0.2 + i * 0.12, 0.3))
            if k <= 0:
                continue
            kind = "scenic" if i < 6 else ("bus" if i % 2 else "boarding")
            travel_ticket(c, x, y, 0.42 * k, kind, f"dk{i}", age=max(0.0, 0.5 - i * 0.03), rot=r.uniform(-0.3, 0.3),
                          seed=i + 40)
            if i >= 6 and k > 0.9:                                 # 背面写满了小字
                with keep():
                    for j in range(3):
                        line(c, [(x - 50, y + 46 + j * 10), (x + 30 - j * 14, y + 46 + j * 10)], f"wr{i}{j}", 1.4,
                             hexc("2f4a6a"), alpha=0.8)
    else:
        lt = t - 5.0
        desk_scene(c, t)
        girl(c, 540, 1010, 2.1, sit=True, legs=False, hat=False, look=0.0, head_down=8, look_up=-0.9, mouth="smile",
             arms=[(-30, -60), (lerp(40, 10, ease_io(prog(lt, 0.4, 1.2))), lerp(-110, -50, ease_io(prog(lt, 0.4, 1.2))))],
             key="g18")
        shape(c, rect(-40, 1010, W + 80, 600), DESK, "desk", lw=3)
        tinbox(c, 540, 1170, 0.9, "b18", n=6)
        u = ease_io(prog(lt, 0.4, 1.2))
        travel_ticket(c, lerp(600, 540, u), lerp(860, 1050, u), lerp(0.5, 0.36, u), "train", "tk18", age=0.7,
                      rot=lerp(0.2, 0.0, u), seed=5)
        pc = ease_io(prog(lt, 2.4, 1.6))
        if pc > 0:                                                 # 盒底露出的明信片
            postcard(c, 540, lerp(1120, 1010, pc), lerp(0.4, 0.95, pc), "post")
            with keep():
                glow(c, 540, lerp(1120, 1010, pc), 220 * pc, hexc("bfe0f2"), 0.35 * pc)


_STILL3 = {}


def desk_still():
    if "d" not in _STILL3:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(150.0)
        with grade(sat=1.0, dark=0.0, warm=0.2):
            d18_desk(cc, 4.9)
        _STILL3["d"] = surf
    return _STILL3["d"]


def outro(c, t):
    book_outro(c, t, desk_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第三章 · 完")

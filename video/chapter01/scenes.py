"""第一章 · 出逃 —— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。"""
import math
import os
import random
import sys

import cairo

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "series"))
from draw import *  # noqa: F401,F403
from engine import book_intro, book_outro, door_illus

GROUND = hexc("b9b6ae")
WATER = hexc("5d6f86")


# ================================================================ 通用：灰色城市、房间
def city_row(c, base, seed, h0=300, h1=560, light=False, lit=None):
    r = random.Random(seed)
    x = -40
    i = 0
    cols = ["d9cbb5", "c9b8a6", "b9c2c9", "d6c3ae", "c5ccd0", "d8d0c2"]
    while x < W + 40:
        w = r.choice((150, 170, 190, 210))
        h = r.uniform(h0, h1)
        wc = hexc(cols[i % len(cols)])
        if light:
            wc = mix(wc, (0.95, 0.95, 0.95), 0.4)
        house(c, x, base, w, h, wc, darker(wc, 0.8), f"cr{seed}{i}", "flat", door=False, lit=lit)
        x += w + r.uniform(4, 16)
        i += 1


def street_bg(c, t, base=760, rain_a=0.35, seed=1):
    vgrad(c, 0, base, [(0, hexc("c9d1d8")), (1, hexc("e4e5e1"))])
    city_row(c, base - 40, seed + 10, 380, 640, light=True)
    city_row(c, base, seed, 260, 480)
    shape(c, rect(-20, base, W + 40, H - base + 20), GROUND, f"gr{seed}", lw=3)
    for i in range(9):
        y = base + 40 + i * i * 14
        line(c, [(-10, y), (W + 10, y)], f"pv{seed}{i}", 1.6, darker(GROUND, 0.85), alpha=0.7)
    for i in range(-6, 7):
        line(c, [(540 + i * 60, base), (540 + i * 330, H)], f"pz{seed}{i}", 1.4, darker(GROUND, 0.85), alpha=0.5)
    if rain_a > 0:
        rain(c, t, 80, rain_a, seed=seed)


def room(c, t, sky="grey", curtain=0.0, hat_hook=True, hat_dust=0.0, map_age=0.0, cal=0.0,
         web=0.0, pack_corner=True, map_glow=0.0, dim=0.0, door=0.0, chair=True):
    fill_all(c, hexc("e8d4b4"))
    c.save()
    for i in range(22):
        x = i * 80 + 20
        line(c, [(x, 0), (x, 1100)], f"wp{i}", 2.0, hexc("dcc39c"), alpha=0.6, amp=1.0)
        for j in range(14):
            circle(c, x + 40, 40 + j * 84 + (i % 2) * 42, 3.2, hexc("d8a98a"), 0.55)
    c.restore()
    # 窗
    wx0, wy0, wx1, wy1 = 470, 230, 950, 770
    c.save()
    c.rectangle(wx0, wy0, wx1 - wx0, wy1 - wy0)
    c.clip()
    if sky == "night":
        vgrad(c, wy0, wy1, [(0, hexc("1d2647")), (0.7, hexc("34477a")), (1, hexc("5b6a9a"))])
        r = random.Random(4)
        for i in range(16):
            star(c, r.uniform(wx0, wx1), r.uniform(wy0, wy0 + 300), r.uniform(2, 4),
                 0.55 + 0.45 * math.sin(t * 3 + i))
        glow(c, 860, 330, 130, hexc("fff3cf"), 0.35)
        shape(c, ell(860, 330, 34, 34, 16), hexc("fbf0cf"), "moon", lw=2.4)
        city_row(c, wy1 + 10, 77, 120, 260, lit=3)
        r = random.Random(9)
        for i in range(30):
            x, y = r.uniform(wx0, wx1), r.uniform(wy1 - 220, wy1 - 20)
            on = 0.6 + 0.4 * math.sin(t * 1.3 + i * 2)
            circle(c, x, y, 3, hexc("f8d77a"), 0.8 * on)
    elif sky == "warm":
        vgrad(c, wy0, wy1, [(0, hexc("f3c79a")), (1, hexc("fbe6c4"))])
        glow(c, 760, 600, 300, hexc("fff0c0"), 0.7)
        city_row(c, wy1 + 10, 77, 120, 260, light=True)
    else:
        vgrad(c, wy0, wy1, [(0, hexc("aab4bf")), (1, hexc("d5d8da"))])
        city_row(c, wy1 + 10, 77, 120, 260, light=True)
        rain(c, t, 30, 0.3, seed=3, x0=wx0, x1=wx1, y0=wy0, y1=wy1)
    c.restore()
    for (x, y, w, h) in ((440, 200, 540, 30), (440, 770, 540, 30), (440, 200, 30, 600), (950, 200, 30, 600), (695, 230, 30, 540)):
        shape(c, rect(x, y, w, h), hexc("8c5a3c"), f"wf{x}{y}", lw=3)
    # 窗帘
    sway = math.sin(t * 1.1) * 5
    lc = lerp(530, 710, curtain)
    rc = lerp(890, 710, curtain)
    shape(c, [(400, 170), (lc, 170), (lc - 20 + sway, 500), (lc + sway, 830), (410, 830), (420, 500)], hexc("c98d72"), "curL", lw=3)
    shape(c, [(rc, 170), (1020, 170), (1010, 500), (1020, 830), (rc - sway, 830), (rc + 20 - sway, 500)], hexc("c98d72"), "curR", lw=3)
    line(c, [(380, 168), (1040, 168)], "rod", 6, hexc("6b4430"))
    # 日历
    shape(c, rect(110, 230, 220, 230), hexc("f4efe6"), "cal", lw=3)
    shape(c, rect(110, 230, 220, 50), hexc("c0503c"), "calh", lw=3)
    text(c, str(1 + int(cal) % 28), 220, 400, 92, INK, a=0.8)
    if cal > 0:
        u = cal % 1.0
        c.save()
        c.translate(110 + 220 * u * 1.4, 280 - 260 * u)
        c.rotate(u * 3)
        shape(c, rect(0, 0, 220, 180), hexc("f4efe6"), "calp", lw=2.5, alpha=1 - u * 0.6)
        c.restore()
    # 地图
    mc = mix(hexc("efe2c2"), hexc("c9a46a"), map_age)
    shape(c, [(90, 510), (400, 500), (408, 728), (96, 736)], mc, "map", lw=3)
    line(c, [(120, 620), (170, 580), (230, 640), (300, 560), (370, 610)], "mapr", 2.4, hexc("c0503c"))
    for i, (x, y) in enumerate(((150, 560), (240, 690), (330, 640), (360, 540), (200, 620))):
        if map_glow > 0:
            g = clamp(map_glow * 6 - i)
            if g > 0:
                with grade(sat=1.0):
                    glow(c, x, y, 60, hexc("ffd27a"), 0.8 * g)
                    circle(c, x, y, 8, hexc("ffb347"), g)
        circle(c, x, y, 4, hexc("8c5a3c"), 0.8)
    if map_age > 0:
        shape(c, [(372, 728), (408, 728), (404, 690)], darker(mc, 0.8), "mapc", lw=2, alpha=map_age)
    # 挂钩与帽子
    line(c, [(250, 800), (250, 782)], "hook", 4)
    if hat_hook:
        hat_item(c, 250, 812, 1.0, dust=hat_dust)
        if hat_dust > 0:
            r = random.Random(5)
            for i in range(int(30 * hat_dust)):
                circle(c, 250 + r.uniform(-50, 50), 790 + r.uniform(-14, 10), 1.6, hexc("8b857a"), 0.8)
    # 地板
    shape(c, rect(-20, 1100, 1700, 900), hexc("bb8c63"), "floor", lw=3)
    for i in range(8):
        line(c, [(-10, 1140 + i * i * 12), (1700, 1140 + i * i * 12)], f"fl{i}", 1.8, hexc("9c714d"), alpha=0.7)
    # 门（向右延伸的墙上）
    shape(c, rect(1130, 540, 290, 560), hexc("7a4d33"), "dframe", lw=3)
    if door > 0:
        c.save()
        c.rectangle(1150, 560, 250, 540)
        c.clip()
        vgrad(c, 560, 900, [(0, hexc("8fc3e3")), (1, hexc("fbf0d6"))], 1150, 1400)
        glow(c, 1300, 760, 200, hexc("fff3c0"), 0.9)
        shape(c, hill_pts(880, 26, 0.02, 1.0, 1140, 1410, 1110), hexc("a9c48b"), "dhill", lw=2.4)
        r = random.Random(3)
        for i in range(24):
            circle(c, r.uniform(1150, 1400), r.uniform(900, 1100), r.uniform(4, 8),
                   [hexc("f2a6a0"), hexc("fbe29a"), hexc("ffffff"), hexc("c9a0dc")][i % 4])
        c.restore()
    fx = 1150 + door * 220
    shape(c, [(fx, 560 - door * 30), (1400, 560), (1400, 1100), (fx, 1100 + door * 30)], hexc("9b6b4a"), "door", lw=3)
    if door < 0.5:
        circle(c, fx + 26, 830, 9, hexc("e1b44f"))
    # 墙角背包与蛛网
    if pack_corner:
        shape(c, rrect(70, 1010, 110, 100, 18), PACK, "cpack", lw=3)
        shape(c, rrect(70, 1010, 110, 36, 12), darker(PACK, 0.88), "cpackf", lw=2.4)
    if web > 0:
        for k in range(6):
            a = math.pi * (0.02 + 0.09 * k)
            line(c, [(0, 1100), (math.cos(a) * 230 * web, 1100 - math.sin(a) * 230 * web)], f"web{k}", 1.4, hexc("efefef"), alpha=0.8)
        for rr in (60, 120, 180):
            if rr < 230 * web:
                pts = [(math.cos(math.pi * (0.02 + 0.09 * k)) * rr, 1100 - math.sin(math.pi * (0.02 + 0.09 * k)) * rr) for k in range(6)]
                line(c, pts, f"webr{rr}", 1.2, hexc("efefef"), alpha=0.7)
    if chair:
        shape(c, rect(630, 1000, 170, 22), hexc("8c5a3c"), "chs", lw=3)
        for x in (645, 770):
            shape(c, rect(x, 1022, 14, 90), hexc("7a4d33"), f"chl{x}", lw=2.4)
    if dim > 0:
        veil(c, (0.08, 0.1, 0.2), dim)


def water(c, t, level, key="wt", a=0.72, col=WATER):
    with grade(sat=max(GRADE["sat"], 0.55)):
        _water(c, t, level, key, a, col)


def _water(c, t, level, key, a, col):
    pts = [(-40, H + 40)] + [(x, level + 9 * math.sin(x * 0.012 + t * 2.2)) for x in range(-40, W + 120, 40)] + [(W + 80, H + 40)]
    shape(c, pts, col + (a,), key, lw=2.6, amp=1)
    line(c, [(x, level + 9 * math.sin(x * 0.012 + t * 2.2) + 4) for x in range(-40, W + 120, 40)], key + "hl", 2.4,
         (0.85, 0.9, 0.95), alpha=0.6)
    r = random.Random(11)
    for i in range(14):
        ph = (t * r.uniform(0.3, 0.6) + r.random()) % 1.0
        x = r.uniform(30, W - 30)
        y = lerp(H, level + 20, ph)
        if y > level + 10:
            c.arc(x, y, r.uniform(3, 7), 0, 2 * math.pi)
            c.set_source_rgba(0.85, 0.9, 0.95, 0.5)
            c.set_line_width(1.6)
            c.stroke()


# ================================================================ 片头
def intro(c, t):
    book_intro(c, t, "第一章", "出 逃", door_illus)


# ================================================================ 一、这片土地
def s01_loop(c, t):
    with cam(c, 540, 960, 1.04 - 0.04 * ease_io(t / 4.5)):
        street_bg(c, t, base=740)
        cx, cy, rx, ry = 540, 1010, 380, 150
        shape(c, ell(cx, cy, rx + 14, ry + 8, 40), None, "loopo", lw=2, alpha=0.4)
        shape(c, ell(cx, cy, rx - 14, ry - 8, 40), None, "loopi", lw=2, alpha=0.4)
        a_now = -math.pi / 2 + 0.6 + t * 0.85
        for k in range(70):
            a = a_now - 0.12 - k * 0.11
            side = 1 if k % 2 else -1
            fx = cx + (rx + side * 8) * math.cos(a)
            fy = cy + (ry + side * 4) * math.sin(a)
            fade = 0.75 if k < 18 else 0.3
            c.save()
            c.translate(fx, fy)
            c.rotate(a + math.pi / 2)
            c.scale(1, 0.6)
            c.arc(0, 0, 7, 0, 2 * math.pi)
            c.restore()
            c.set_source_rgba(*G(hexc("6e6a63"))[:3], fade)
            c.fill()
        x = cx + rx * math.cos(a_now)
        y = cy + ry * math.sin(a_now)
        s = 1.05 + 0.25 * math.sin(a_now)
        dx = -math.sin(a_now)
        girl(c, x, y, s, look=clamp(dx * 1.4, -1, 1), walk=t * 8, pack=False, hat=False, mouth="flat")


def s02_three(c, t):
    stops = [0, 1080, 2160]
    p1 = ease_io(prog(t, 2.6, 0.8))
    p2 = ease_io(prog(t, 5.6, 0.8))
    tx = -(1080 * p1 + 1080 * p2)
    c.save()
    c.translate(tx, 0)
    # --- ① 雨中的咖啡馆
    x0 = 0
    vgrad(c, 0, 1160, [(0, hexc("b7b0a6")), (1, hexc("cfc6b8"))], x0 - 100, x0 + 1080)
    shape(c, rect(x0 - 20, 0, 1100, 1160), hexc("a98a74"), "cafe", lw=3)
    for i in range(10):
        line(c, [(x0 - 20, 60 + i * 110), (x0 + 1080, 60 + i * 110)], f"brk{i}", 1.6, hexc("8f7360"), alpha=0.6)
    shape(c, rect(x0 + 110, 300, 860, 560), hexc("6b4430"), "cwf", lw=3.4)
    vgrad(c, 320, 840, [(0, hexc("efe2c8")), (1, hexc("dccaa9"))], x0 + 130, x0 + 950)
    glow(c, x0 + 640, 520, 360, hexc("ffe2a8"), 0.5)
    shape(c, rect(x0 + 130, 700, 820, 26), hexc("8c5a3c"), "ctab", lw=3)
    mug(c, x0 + 650, 660, 2.1, "mgL", col=hexc("f2efe8"), heart="L")
    mug(c, x0 + 742, 660, 2.1, "mgR", col=hexc("f2efe8"), heart="R", crack=True)
    for k in range(2):
        sx = x0 + 650 + k * 92
        line(c, [(sx, 610), (sx - 8 + math.sin(t * 2 + k) * 6, 570), (sx + 4, 530)], f"stm{k}", 2, hexc("ffffff"), alpha=0.5)
    r = random.Random(3)
    for i in range(26):
        rx, ry = r.uniform(x0 + 140, x0 + 940), r.uniform(330, 820)
        yy = ry + ((t * 40 * r.uniform(0.5, 1.5)) % 60)
        line(c, [(rx, yy), (rx + 1, yy + 14)], f"gd{i}", 2, hexc("c5ced8"), alpha=0.7)
    line(c, [(x0 + 540, 300), (x0 + 540, 860)], "cwm", 6, hexc("6b4430"))
    for i in range(8):
        shape(c, [(x0 + 90 + i * 112, 220), (x0 + 202 + i * 112, 220), (x0 + 202 + i * 112, 280), (x0 + 90 + i * 112, 300)],
              hexc("c9553f") if i % 2 == 0 else hexc("f3ead8"), f"awn{i}", lw=2.4)
    shape(c, rect(x0 - 20, 1160, 1100, 800), hexc("8f949a"), "wet", lw=3)
    for i in range(6):
        line(c, [(x0 + 100 + i * 170, 1200), (x0 + 160 + i * 170, 1200)], f"refl{i}", 3, hexc("c9cdd2"), alpha=0.5)
    girl(c, x0 + 300, 1180, 1.45, view="back", pack=False, hat=False, arms=[(-26, -80), (8, -110)])
    gx, gy = x0 + 300 + 8 * 1.45, 1180 - 110 * 1.45
    line(c, [(gx, gy), (gx + 10, gy - 190)], "umh", 4)
    ux, uy = gx + 90, gy - 190
    shape(c, ell(ux, uy, 230, 90, 24, math.pi, 2 * math.pi), hexc("7f3f3f"), "umb", lw=3)
    for k in range(-2, 3):
        line(c, [(ux, uy - 90), (ux + k * 92, uy)], f"umr{k}", 1.6, darker(hexc("7f3f3f"), 0.7))
    rain(c, t, 70, 0.4, seed=5, x0=x0 - 100, x1=x0 + 1080)
    # --- ② 灰云下的工位
    x0 = 1080
    shape(c, rect(x0, 0, 1080, 1100), hexc("cfd2cf"), "office", lw=3)
    shape(c, rect(x0, 1100, 1080, 900), hexc("9a9a94"), "ofloor", lw=3)
    for i, (sx_, s_, wh) in enumerate(((x0 + 160, 1.7, 0.0), (x0 + 900, 1.8, 1.3), (x0 + 1000, 1.6, 2.1))):
        silhouette(c, sx_ + math.sin(t * 1.3 + i) * 6, 1100, s_, f"wh{i}", col=hexc("9ea3ab"))
        for k in range(3):
            ph = (t * 1.5 + k * 0.33 + wh) % 1
            bx = sx_ + (40 if sx_ < x0 + 540 else -60) + ph * 50 * (1 if sx_ < x0 + 540 else -1)
            line(c, [(bx, 760 - ph * 40), (bx + 12, 750 - ph * 40), (bx + 24, 762 - ph * 40), (bx + 36, 752 - ph * 40)],
                 f"wsp{i}{k}", 2.4, hexc("7d838c"), alpha=1 - ph)
    girl(c, x0 + 540, 930, 1.35, sit=True, legs=False, pack=False, hat=False, badge=True, head_down=5,
         mouth="flat", arms=[(-34, -60), (34, -60)], look_up=-0.6)
    shape(c, rect(x0 + 200, 900, 680, 36), hexc("a69a8a"), "desk", lw=3)
    shape(c, rect(x0 + 230, 936, 30, 180), hexc("8a7f72"), "dl1", lw=2.4)
    shape(c, rect(x0 + 820, 936, 30, 180), hexc("8a7f72"), "dl2", lw=2.4)
    shape(c, rect(x0 + 640, 760, 190, 130), hexc("6f747c"), "mon", lw=3)
    shape(c, rect(x0 + 655, 775, 160, 100), hexc("dfe6ec"), "scr", lw=2)
    for k in range(5):
        shape(c, rect(x0 + 260, 880 - k * 14, 150, 14), hexc("f2f0ea"), f"ppr{k}", lw=1.6, amp=0.6)
    cy_ = lerp(560, 640, ease_io(t / 9))
    rain_cloud(c, x0 + 540, cy_, 2.1, "ocld", col=hexc("858a93"), t=t)
    # --- ③ 不敢接的电话
    x0 = 2160
    with grade(dark=0.35):
        shape(c, rect(x0, 0, 1080, 1100), hexc("8d8a98"), "broom", lw=3)
        shape(c, rect(x0 + 640, 240, 300, 380), hexc("2a3150"), "bwin", lw=3)
        r = random.Random(14)
        for i in range(9):
            star(c, r.uniform(x0 + 660, x0 + 920), r.uniform(260, 600), 2.6, 0.6 + 0.4 * math.sin(t * 3 + i))
        shape(c, ell(x0 + 860, 320, 28, 28, 14), hexc("f4ecd0"), "bmoon", lw=2)
        line(c, [(x0 + 790, 240), (x0 + 790, 620)], "bwm", 5, hexc("4a4458"))
        shape(c, rect(x0, 1100, 1080, 900), hexc("6b6170"), "bfloor", lw=3)
        shape(c, rect(x0 + 150, 960, 780, 140), hexc("b5a9b8"), "bed", lw=3)
        shape(c, rect(x0 + 150, 930, 780, 40), hexc("e0d8e2"), "bedtop", lw=3)
    ring = t - 6.0
    girl(c, x0 + 540, 960, 1.45, sit=True, pack=False, hat=False, head_down=6, mouth="flat", look_up=-0.8,
         arms=[(-16, -50), (14 + 3 * math.sin(t * 3), -80 + 4 * math.sin(t * 2.3))])
    phone(c, x0 + 540, 960 - 118 * 1.45 + 52 * 1.45 + 52, 0.9, "ph", ring=ring if ring > 0 else 0)
    c.restore()
    # 分隔的书页折痕
    for k in (1, 2):
        xx = 1080 * k + tx
        if -20 < xx < W + 20:
            line(c, [(xx, 0), (xx, H)], f"sep{k}", 4)


def s03_tide(c, t):
    street_bg(c, t, base=820, rain_a=0.4, seed=2)
    r = random.Random(4)
    for i in range(8):
        x0 = r.uniform(60, W - 60)
        y0 = r.uniform(1150, 1500)
        line(c, [(x0, y0), (x0 + r.uniform(-60, 60), y0 + 30), (x0 + r.uniform(-90, 90), y0 + 70)], f"crk{i}", 2.4)
    girl(c, 540, 1160, 1.65, pack=False, hat=False, mouth="flat", look_up=-0.8, head_down=4)
    lvl = lerp(1240, 1120, ease_io(prog(t, 0.6, 3.6)))
    a = 0.25 + 0.45 * ease_io(prog(t, 0.2, 1.5))
    water(c, t, lvl, "tide3", a=a, col=hexc("4f6584"))
    for i in range(10):
        ph = (t * 0.7 + i * 0.1) % 1
        x = (i * 113) % W
        y = lvl + 30 + (i * 67) % 400
        c.save()
        c.translate(x, y)
        c.scale(1, 0.35)
        c.arc(0, 0, 10 + ph * 40, 0, 2 * math.pi)
        c.restore()
        c.set_source_rgba(0.85, 0.9, 0.95, 0.5 * (1 - ph))
        c.set_line_width(1.8)
        c.stroke()


def roots_at(c, fx, fy, t, key, tension=0.0, shrink=None, n=6, spread=1.0):
    r = random.Random(zlib_key(key))
    for i in range(n):
        if shrink is not None and shrink[i] >= 1:
            continue
        L = 1.0 if shrink is None else 1 - shrink[i]
        x0 = fx + r.uniform(-26, 26)
        pts = [(x0, fy)]
        x, y = x0, fy
        segs = 7
        dx = r.uniform(-1, 1) * 80 * spread
        for k in range(1, segs + 1):
            if k / segs > L:
                break
            y = fy + k * (r.uniform(70, 110) * spread) * (1 - 0.4 * tension)
            x = x0 + dx * k / segs + math.sin(k * 1.3 + i + t * 0.8) * 26 * spread
            pts.append((x, y))
        if len(pts) >= 2:
            line(c, pts, f"{key}r{i}", 13 - i, hexc("3f3a35"), amp=1.5)
            line(c, pts, f"{key}ri{i}", 7 - i * 0.6, hexc("d6d0c3"), amp=1.5)


def floor_roots(c, fx, fy, t, shrink):
    """沿地板向四周蔓延、缠住脚踝的灰色根；shrink[i]→1 时收回。"""
    for i in range(6):
        L = 1 - shrink[i]
        if L <= 0.02:
            continue
        sg = -1 if i % 2 else 1
        ang = (0.15 + 0.28 * (i // 2)) * sg
        pts = []
        for k in range(9):
            u = k / 8 * L
            d = 40 + 520 * u
            x = fx + sg * d * math.cos(ang) + math.sin(u * 9 + i + t) * 14
            y = fy + 10 + d * abs(math.sin(ang)) * 0.35 + math.cos(u * 7 + i) * 8
            pts.append((x, y))
        line(c, pts, f"fr{i}", 14, hexc("3f3a35"), amp=1.5)
        line(c, pts, f"fri{i}", 7, hexc("d6d0c3"), amp=1.5)


def zlib_key(s):
    import zlib
    return zlib.crc32(s.encode())


def s04_roots(c, t):
    ty = -480 * ease_io(prog(t, 0.2, 1.6))
    jump = 0.0
    if 2.4 < t < 3.6:
        u = (t - 2.4) / 1.2
        jump = -math.sin(min(u * 2, 1) * math.pi / 2) * 30 * (1 - ease_in(clamp((u - 0.5) * 2)))
    shake = 0
    if 3.2 < t < 3.7:
        shake = math.sin(t * 80) * 5 * (3.7 - t)
    c.save()
    c.translate(shake, ty)
    vgrad(c, -200, 900, [(0, hexc("c9d1d8")), (1, hexc("e4e5e1"))])
    city_row(c, 840, 31, 300, 520, light=True)
    city_row(c, 900, 32, 200, 420)
    shape(c, rect(-20, 900, W + 40, 1600), hexc("6a5f50"), "soil", lw=3)
    r = random.Random(7)
    for i in range(30):
        shape(c, ell(r.uniform(0, W), r.uniform(980, 2300), r.uniform(10, 30), r.uniform(8, 18), 10),
              hexc("5a5044"), f"stone{i}", lw=1.8)
    for i in range(4):
        line(c, [(-10, 1040 + i * 260), (W + 10, 1060 + i * 260)], f"strata{i}", 2, hexc("766d60"), alpha=0.6)
    shape(c, rect(-20, 880, W + 40, 30), GROUND, "crust", lw=3)
    roots_at(c, 540, 900, t, "rt4", tension=clamp(-jump / 30), n=7, spread=1.6)
    girl(c, 540, 900 + jump, 1.6, pack=False, hat=False, mouth="flat" if t < 2.4 else "o",
         look_up=-0.8 if t < 2.2 else 0.3, head_down=3)
    for k, sg in enumerate((-1, 1)):
        line(c, [(540 + sg * 14, 900 + jump), (540 + sg * 24, 905)], f"tie{k}", 6, hexc("76736d"))
    water(c, t, 870, "tide4", a=0.55)
    c.restore()
    rain(c, t, 40, 0.3, seed=9)


def s05_station(c, t):
    street_bg(c, t, base=860, rain_a=0.0, seed=3)
    shape(c, rect(140, 300, 800, 560), hexc("cfc5b4"), "stn", lw=3.2)
    shape(c, [(110, 300), (540, 170), (970, 300)], hexc("9a7c66"), "stnr", lw=3.2)
    shape(c, rect(300, 330, 480, 90), hexc("4f5a52"), "sign", lw=3)
    text(c, "车  站", 540, 395, 58, hexc("f2ead8"))
    shape(c, [(400, 860), (400, 600), (540, 520), (680, 600), (680, 860)], hexc("3e3a3a"), "arch", lw=3)
    shape(c, ell(540, 245, 46, 46, 18), hexc("f4efe6"), "sclk", lw=2.6)
    line(c, [(540, 245), (540, 215)], "sch", 3)
    line(c, [(540, 245), (562, 252)], "scm", 3)
    if t < 1.9:
        x = lerp(120, 470, ease_io(prog(t, 0.0, 1.9)))
        girl(c, x, 1170, 1.55, look=1.0, walk=t * 8, mouth="flat")
    elif t < 2.6:
        girl(c, 470, 1170, 1.55, look=0.4, head_down=7, look_up=-0.9, mouth="flat")
    elif t < 3.0:
        sp = prog(t, 2.6, 0.4)
        girl(c, 470, 1170, 1.55, look=-0.4, head_down=5, sx=max(abs(math.cos(sp * math.pi)), 0.05), mouth="flat")
    else:
        x = lerp(470, 150, ease_io(prog(t, 3.0, 1.5)))
        girl(c, x, 1170, 1.55, look=-1.0, walk=t * 7, head_down=4, mouth="flat", look_up=-0.5)
    rain(c, t, 70, 0.38, seed=4)


# ================================================================ 二、为什么不走
def s06_window(c, t):
    with cam(c, 700, 760, 1.0 + 0.05 * ease_io(t / 4)):
        room(c, t, sky="night", hat_hook=True, dim=0.28)
        glow(c, 710, 600, 500, hexc("c8d4ff"), 0.15)
        girl(c, 712, 1000, 1.6, view="back", sit=True, pack=False, hat=False, walk=t * 1.2,
             head_down=-2 + 2 * math.sin(t * 0.8))


def panel(c, x, y, w, h, k, key, draw_fn, t, rot=0.0):
    if k <= 0.01:
        return
    c.save()
    c.translate(x + w / 2, y + h / 2)
    c.rotate(rot)
    c.scale(0.85 + 0.15 * k, 0.85 + 0.15 * k)
    c.translate(-(x + w / 2), -(y + h / 2))
    with group_alpha(c, clamp(k * 1.4)):
        c.rectangle(x + 10, y + 14, w, h)
        c.set_source_rgba(0, 0, 0, 0.2)
        c.fill()
        c.save()
        c.rectangle(x, y, w, h)
        c.clip()
        c.translate(x, y)
        draw_fn(c, t, w, h)
        c.restore()
        shape(c, rect(x, y, w, h), None, key + "fr", lw=5, amp=1.0)
    c.restore()


def p_suitcase(c, t, w, h):
    with grade(dark=0.3):
        fill_all(c, hexc("6d7486"))
        city_row(c, 200, 51, 80, 180, lit=2)
        shape(c, rect(-10, 200, w + 20, 200), hexc("8e8f93"), "pst", lw=2.6)
    glow(c, 820, 110, 200, hexc("ffe6a8"), 0.6)
    line(c, [(820, 330), (820, 90)], "lamp", 6, hexc("4a4a4a"))
    shape(c, [(790, 80), (850, 80), (840, 105), (800, 105)], hexc("4a4a4a"), "lamph", lw=2.4)
    c.save()
    c.translate(560, 300)
    c.rotate(0.12)
    shape(c, rrect(-90, -170, 180, 170, 14), hexc("8b6f9a"), "suit", lw=3.4)
    line(c, [(-40, -170), (-40, -230), (40, -230), (40, -170)], "suith", 5)
    line(c, [(-90, -90), (90, -90)], "suitb", 3)
    circle(c, -70, 8, 11, INK)
    c.restore()
    wx = 660 + ease_out(prog(t, 0.4, 1.6)) * 160
    c.save()
    c.translate(wx, 316)
    c.rotate(wx * 0.05)
    shape(c, ell(0, 0, 13, 13, 12), hexc("3a3a3a"), "wheel", lw=2)
    line(c, [(0, 0), (8, 0)], "wsp", 1.6, hexc("dddddd"))
    c.restore()
    girl(c, 400, 266, 1.15, sit=True, crouch=True, pack=False, hat=False, mouth="flat", look=0.8,
         arms=[(48, -30), (60, -10)], head_down=4)
    rain(c, t, 50, 0.5, seed=12, x1=w, y1=h)


def p_noodle(c, t, w, h):
    fill_all(c, hexc("d7c9b4"))
    glow(c, 470, 40, 260, hexc("ffe2a0"), 0.5)
    line(c, [(470, 0), (470, 40)], "lmpw", 2)
    shape(c, [(430, 40), (510, 40), (530, 80), (410, 80)], hexc("c98d4a"), "lmps", lw=2.4)
    girl(c, 300, 230, 1.15, sit=True, legs=False, pack=False, hat=False, mouth="flat", look=0.5,
         arms=[(40, -40), (50, -50)], head_down=6, look_up=-0.7)
    shape(c, rect(160, 230, 600, 22), hexc("8c5a3c"), "ntab", lw=3)
    shape(c, ell(420, 220, 46, 16, 16, 0, math.pi), hexc("e8e2d6"), "bowl", lw=2.4)
    shape(c, ell(420, 220, 46, 10, 16), hexc("f3d9a0"), "noodle", lw=2)
    for k in range(3):
        sx = 400 + k * 20
        line(c, [(sx, 205), (sx - 6 + math.sin(t * 2 + k) * 5, 175), (sx + 3, 150)], f"nst{k}", 2, hexc("ffffff"), alpha=0.6)
    shape(c, rect(600, 120, 14, 112), hexc("7a4d33"), "chb", lw=2.4)
    shape(c, rect(600, 200, 110, 14), hexc("8c5a3c"), "chs2", lw=2.4)
    shape(c, rect(696, 214, 14, 100), hexc("7a4d33"), "chl2", lw=2.4)
    shape(c, rect(600, 214, 14, 100), hexc("7a4d33"), "chl3", lw=2.4)


def p_tall(c, t, w, h):
    vgrad(c, 0, h, [(0, hexc("b9c3cc")), (1, hexc("e1e2dc"))], 0, w)
    r = random.Random(8)
    x = -20
    i = 0
    while x < w + 20:
        bw = r.uniform(110, 170)
        bh = r.uniform(h * 0.9, h * 1.6)
        house(c, x, h - 40, bw, bh, hexc(["c9c3b6", "b8bfc6", "d2cabd"][i % 3]), hexc("8f8a82"), f"tb{i}", "flat", door=False)
        x += bw + 6
        i += 1
    shape(c, rect(-10, h - 40, w + 20, 60), GROUND, "tg", lw=2.4)
    girl(c, w / 2, h - 44, 0.55, look=0.0, look_up=1.0, pack=True)


def s07_comic(c, t):
    fill_all(c, hexc("e8e2d6"))
    panel(c, 60, 130, 960, 300, ease_back(prog(t, 0.15, 0.5)), "pn1", p_suitcase, t, rot=-0.008)
    panel(c, 60, 470, 960, 300, ease_back(prog(t, 4.5, 0.5)), "pn2", p_noodle, t - 4.5, rot=0.006)
    panel(c, 60, 810, 960, 340, ease_back(prog(t, 7.0, 0.5)), "pn3", p_tall, t - 7.0, rot=-0.004)


# ---------------------------------------------------------------- 月台
def platform_bg(c, t, clock_speed=6.0, clock_stop=None):
    fill_all(c, hexc("d7d4cb"))
    for i in range(14):
        line(c, [(i * 80, 0), (i * 80, 900)], f"tile{i}", 1.6, hexc("c5c1b7"), alpha=0.6)
    for j in range(11):
        line(c, [(0, j * 80), (W, j * 80)], f"tilh{j}", 1.6, hexc("c5c1b7"), alpha=0.6)
    line(c, [(540, 0), (540, 170)], "clkrod", 5)
    shape(c, ell(540, 290, 120, 120, 30), hexc("f6f1e6"), "clk", lw=4)
    for k in range(12):
        a = k * math.pi / 6
        line(c, [(540 + math.cos(a) * 100, 290 + math.sin(a) * 100), (540 + math.cos(a) * 112, 290 + math.sin(a) * 112)], f"tk{k}", 3)
    tt = t if clock_stop is None else min(t, clock_stop)
    jit = 0.0
    if clock_stop is not None and clock_stop < t < clock_stop + 0.5:
        jit = math.sin(t * 60) * 0.08 * (clock_stop + 0.5 - t) * 2
    am = tt * clock_speed + jit
    ah = tt * clock_speed / 12
    line(c, [(540, 290), (540 + math.sin(am) * 92, 290 - math.cos(am) * 92)], "mh", 4)
    line(c, [(540, 290), (540 + math.sin(ah) * 60, 290 - math.cos(ah) * 60)], "hh", 6)
    circle(c, 540, 290, 7, INK)
    shape(c, rect(-420, 900, W + 840, 150), hexc("54555a"), "track", lw=3)
    for y in (950, 1010):
        line(c, [(-410, y), (W + 410, y)], f"rail{y}", 5, hexc("8d8f94"))
    for i in range(-6, 22):
        shape(c, rect(i * 72 - 10, 940, 30, 80), hexc("6b5a4a"), f"slp{i}", lw=1.4, amp=0.5)
    shape(c, rect(-420, 1050, W + 840, 1100), hexc("b7b2a7"), "plat", lw=3)
    shape(c, rect(-420, 1062, W + 840, 16), hexc("d9c26a"), "safe", lw=2)


def train_pass(c, t, t0, dur, y0=600, y1=900, col=hexc("8c99a6")):
    u = prog(t, t0, dur)
    if 0 < u < 1:
        x = lerp(W + 100, -2600, u)
        for k in range(4):
            cx = x + k * 640
            shape(c, rrect(cx, y0, 620, y1 - y0, 20), col, f"tr{k}", lw=3)
            for j in range(5):
                shape(c, rect(cx + 40 + j * 115, y0 + 50, 80, 90), hexc("d8e0e8"), f"trw{k}{j}", lw=2)
            line(c, [(cx + 10, y1 - 60), (cx + 610, y1 - 60)], f"trs{k}", 6, hexc("c9553f"))
        for j in range(8):
            yy = y0 + 20 + j * 36
            line(c, [(x + 2560, yy), (x + 2560 + 300, yy)], f"spd{j}", 2, hexc("ffffff"), alpha=0.6)


def s09_platform(c, t):
    platform_bg(c, t, clock_speed=8.0)
    train_pass(c, t, 1.0, 2.0)
    r = random.Random(21)
    walkers = [(r.choice((-1, 1)), r.uniform(1100, 1340), r.uniform(1.25, 1.65), r.uniform(220, 380), r.uniform(0, 1)) for _ in range(9)]
    walkers.sort(key=lambda w: w[1])
    drawn_girl = False
    for i, (d, y, s, sp, ph) in enumerate(walkers):
        if y > 1190 and not drawn_girl:
            girl(c, 540, 1190, 1.55, mouth="flat", look=0.0)
            drawn_girl = True
        span = W + 400
        x = ((ph * span + d * t * sp) % span) - 200
        if abs(x - 540) < 60 and abs(y - 1190) < 40:
            continue
        silhouette(c, x, y, s, f"sw{i}", walk=t * 7 + i, a=0.75)
    if not drawn_girl:
        girl(c, 540, 1190, 1.55, mouth="flat")


def s10_bench(c, t):
    k = 1 - 0.16 * ease_io(prog(t, 5.0, 4.0))
    with cam(c, 540, 860, k):
        platform_bg(c, t, clock_speed=14.0, clock_stop=5.0)
        season = t / 4.6
        green = hexc("74a160")
        yellow = hexc("e0b34a")
        col = mix(green, yellow, clamp(season * 2)) if season < 0.66 else yellow
        bare = clamp((season - 0.55) * 3)
        shape(c, rect(740, 1000, 160, 70), hexc("8f8a82"), "planter", lw=3)
        with grade(sat=0.5):
            tree(c, 820, 1000, 2.6, "btree", col, bare=bare)
            r = random.Random(4)
            for i in range(26):
                st = r.uniform(1.2, 4.4)
                u = prog(t, st, 1.4)
                if u <= 0:
                    continue
                lx = 820 + r.uniform(-140, 140) + math.sin(u * 6 + i) * 30
                ly = lerp(720, 1130 + r.uniform(0, 60), ease_in(u) * 0.6 + u * 0.4)
                if t > 5.2:
                    w = ease_in(prog(t, 5.2 + r.uniform(0, 0.5), 1.8))
                    lx += w * 1400
                    ly -= w * 160 * math.sin(i)
                c.save()
                c.translate(lx, ly)
                c.rotate(u * 8 + i)
                shape(c, ell(0, 0, 14, 7, 10), mix(yellow, hexc("c9553f"), (i % 3) / 3), f"lf{i}", lw=1.6, amp=0.5)
                c.restore()
        shape(c, rect(260, 1080, 560, 26), hexc("8c5a3c"), "bseat", lw=3)
        shape(c, rect(260, 1010, 560, 22), hexc("8c5a3c"), "bback", lw=3)
        for x in (290, 770):
            shape(c, rect(x, 1106, 18, 80), hexc("6b4430"), f"bl{x}", lw=2.4)
        girl(c, 430, 1080, 1.5, sit=True, mouth="flat", head_down=2 + 4 * clamp(t / 6), look=0.3,
             look_up=-0.4 if t > 5 else 0.0, arms=[(-20, -70), (20, -70)])
        if t > 5.0:
            for i in range(5):
                ph = (t * 1.2 + i * 0.2) % 1
                y = 900 + i * 60
                x = -200 + ph * 1500
                line(c, [(x, y), (x + 60, y - 6), (x + 120, y)], f"wnd{i}", 2.4, hexc("9aa3ad"), alpha=0.6)


# ================================================================ 三、两种恐惧
def s12_scale(c, t):
    fill_all(c, hexc("d6d1c5"))
    glow(c, 540, 500, 800, hexc("f4efe4"), 0.4)
    tip = ease_back(prog(t, 4.0, 0.7), 1.2)
    wob_a = 0.04 * math.sin(t * 2.2) * (1 - clamp(t / 4))
    th = 0.27 * tip + wob_a
    shake = 0
    if 4.4 < t < 5.0:
        shake = math.sin(t * 90) * 7 * (5.0 - t)
    c.save()
    c.translate(shake, 0)
    shape(c, [(430, 1100), (650, 1100), (600, 1030), (480, 1030)], hexc("8c6f4a"), "base", lw=3)
    shape(c, rect(526, 450, 28, 590), hexc("a9875a"), "pole", lw=3)
    px, py = 540, 450
    L = 360
    ends = [(px - L * math.cos(th), py - L * math.sin(th)), (px + L * math.cos(th), py + L * math.sin(th))]
    line(c, [ends[0], ends[1]], "beam", 14, hexc("8c6f4a"))
    line(c, [ends[0], ends[1]], "beam2", 8, hexc("c9a46a"))
    circle(c, px, py, 16, hexc("c9a050"))
    for i, (ex, ey) in enumerate(ends):
        pan_y = ey + 300
        for sg in (-1, 1):
            line(c, [(ex, ey), (ex + sg * 120, pan_y)], f"ch{i}{sg}", 2.4)
        shape(c, ell(ex, pan_y, 140, 34, 22, 0, math.pi), hexc("c9a46a"), f"pan{i}", lw=3)
        line(c, [(ex - 140, pan_y), (ex + 140, pan_y)], f"panl{i}", 3)
        if i == 0:
            rain_cloud(c, ex, pan_y - 70, 1.25, "lcl", col=hexc("8d929b"), t=t)
        else:
            hx, hy = ex, pan_y - 110
            shape(c, rect(hx - 70, hy - 110, 140, 16), hexc("8c6f4a"), "hgt", lw=2.6)
            shape(c, rect(hx - 70, hy + 94, 140, 16), hexc("8c6f4a"), "hgb", lw=2.6)
            shape(c, [(hx - 56, hy - 94), (hx + 56, hy - 94), (hx + 6, hy), (hx + 56, hy + 94), (hx - 56, hy + 94), (hx - 6, hy)],
                  hexc("eef3f6"), "glass", lw=2.6)
            sand = clamp(0.3 + t / 6)
            top_h = 80 * (1 - sand)
            if top_h > 2:
                shape(c, [(hx - 56 * top_h / 94, hy - top_h), (hx + 56 * top_h / 94, hy - top_h), (hx + 4, hy - 4), (hx - 4, hy - 4)],
                      hexc("d9b56a"), "sandt", lw=1.6, amp=0.4)
            bh = 86 * sand
            shape(c, [(hx - 56, hy + 94), (hx + 56, hy + 94), (hx + 56 - bh * 0.4, hy + 94 - bh), (hx - 56 + bh * 0.4, hy + 94 - bh)],
                  hexc("d9b56a"), "sandb", lw=1.6, amp=0.4)
            line(c, [(hx, hy), (hx, hy + 94 - bh)], "stream", 2.4, hexc("d9b56a"))
            if 4.4 < t < 5.4:
                u = prog(t, 4.4, 1.0)
                r = random.Random(3)
                for k in range(10):
                    a = r.uniform(math.pi, 2 * math.pi)
                    d = 40 + 120 * ease_out(u)
                    circle(c, ex + math.cos(a) * d, pan_y + 20 + math.sin(a) * d * 0.4, 8 * (1 - u) + 2, hexc("b9b2a4"), 0.7 * (1 - u))
    c.restore()
    girl(c, 170, 1160, 1.1, look=0.6, look_up=1.0, mouth="o" if t > 4.3 else "flat", pack=False, hat=False)


def s14_aging(c, t):
    age = ease_io(prog(t, 0.3, 5.0))
    cal = t * 3.2 if t < 5.5 else 5.5 * 3.2
    curtain = ease_io(prog(t, 6.5, 3.0))
    look = lerp(1.0, -0.3, ease_io(prog(t, 5.6, 1.2)))
    comp_a = ease_io(prog(t, 5.0, 1.2)) * (1 - ease_io(prog(t, 10.0, 1.5)))
    with cam(c, 620, 820, 1.0 + 0.04 * ease_io(t / 15)):
        room(c, t, sky="grey", curtain=curtain, hat_dust=age, map_age=age, cal=cal, web=age, chair=True)
        if comp_a > 0.01:
            shape(c, rect(840, 1010, 150, 20), hexc("8c5a3c"), "ch2", lw=3, alpha=comp_a)
            person(c, 915, 1010, 1.5, sit=True, coat=hexc("8fa0b3"), hair=hexc("6b5a4a"), hair_style="short",
                   hat=False, pack=False, look=-0.8, alpha=comp_a, key="mate", age=0.6)
        girl(c, 712, 1000, 1.6, sit=True, pack=False, hat=False, age=age, look=look, look_up=0.4 * (1 - curtain),
             head_down=3 * age, mouth="flat" if t < 5 else "sad", walk=None)
        lvl = lerp(H + 40, 850, ease_io(prog(t, 10.2, 4.6)))
        if lvl < H:
            water(c, t, lvl, "tide14", a=0.78, col=hexc("3f4a5e"))


def s17_wake(c, t):
    flash = 1 - ease_out(prog(t, 0, 0.5))
    unfold = ease_io(prog(t, 5.0, 1.4))
    stand = t > 4.9
    with cam(c, 560, 820, 1.0):
        room(c, t, sky="warm", hat_hook=t < 10.0, map_glow=prog(t, 0.6, 2.4), chair=True, pack_corner=t < 10.5)
        # 散开的灰尘
        r = random.Random(6)
        for i in range(40):
            u = prog(t, r.uniform(0, 0.8), 2.0)
            if 0 < u < 1:
                x = r.uniform(80, 1000) + u * r.uniform(-60, 60)
                y = r.uniform(300, 1100) - u * 200
                star(c, x, y, 2.5, (1 - u) * 0.8, hexc("fff2c0"))
        # 地图展开成立体书
        if unfold > 0:
            mx0, my0, mx1, my1 = 90, 500, 400, 730
            tx0, ty0, tx1, ty1 = 40, 150, 1040, 760
            x0, y0 = lerp(mx0, tx0, unfold), lerp(my0, ty0, unfold)
            x1, y1 = lerp(mx1, tx1, unfold), lerp(my1, ty1, unfold)
            with grade(sat=0.85, warm=0.15):
                shape(c, rect(x0, y0, x1 - x0, y1 - y0), hexc("f3e6c6") + (1.0,), "bigmap", lw=3.2)
                pops = [(0.2, lambda: mountain(c, 230, 560, 300, 260, hexc("a7b4d0"), "pm1")),
                        (0.35, lambda: mountain(c, 420, 560, 220, 180, hexc("b5c1d8"), "pm2")),
                        (0.5, lambda: tree(c, 600, 560, 1.0, "pt1", hexc("74a160"))),
                        (0.6, lambda: tree(c, 680, 560, 0.8, "pt2", hexc("8fb46a"))),
                        (0.7, lambda: house(c, 760, 560, 90, 120, hexc("f1c27d"), hexc("b4533f"), "ph1")),
                        (0.8, lambda: house(c, 870, 560, 80, 160, hexc("8fc0b5"), hexc("3f6f73"), "ph2", "dome")),
                        (0.9, lambda: (shape(c, [(960, 560), (968, 420), (990, 420), (998, 560)], hexc("f4efe6"), "lh", lw=2.6),
                                       shape(c, rect(964, 396, 30, 26), hexc("d1553f"), "lht", lw=2.4)))]
                if unfold > 0.98:
                    for k, (t0, fn) in enumerate(pops):
                        kk = ease_back(prog(t, 6.4 + t0 * 1.2, 0.45))
                        if kk > 0.01:
                            with popup(c, 540, 560, kk):
                                fn()
                    shape(c, [(60, 560), (1020, 560), (1020, 740), (60, 740)], hexc("cfe0a8"), "mapgr", lw=2.6)
                    for k in range(5):
                        u = ease_io(prog(t, 7.2 + k * 0.25, 0.9))
                        if u > 0:
                            ex, ey = [(230, 600), (420, 610), (620, 590), (800, 600), (980, 600)][k]
                            pts = [(620, 1100), (lerp(620, ex, 0.5) + (k - 2) * 40, lerp(1100, ey, 0.5)), (ex, ey)]
                            n = max(2, int(10 * u))
                            seg = [(lerp(pts[0][0], pts[1][0], i / 9) if i < 5 else lerp(pts[1][0], pts[2][0], (i - 5) / 4),
                                    lerp(pts[0][1], pts[1][1], i / 9) if i < 5 else lerp(pts[1][1], pts[2][1], (i - 5) / 4))
                                   for i in range(10)][:n]
                            with ink_style(hexc("b0613f"), [10, 10]):
                                line(c, seg, f"path{k}", 3.2)
        # 帽子飞到头上
        hu = ease_io(prog(t, 10.0, 0.8))
        if not stand:
            girl(c, 712, 1000, 1.6, sit=True, pack=False, hat=False, look=-1.0 if t > 0.5 else 0.6, look_up=0.5,
                 mouth="o" if t < 2.0 else "smile", tilt=0.0)
        else:
            tilt = 0.22 * ease_io(prog(t, 8.4, 0.5)) * (1 - ease_io(prog(t, 9.8, 0.4)))
            pk = t > 10.5
            girl(c, 620, 1100, 1.6, pack=pk, hat=hu >= 1, look=-0.2, look_up=0.6 if t < 10 else 0.0, tilt=tilt,
                 mouth="smile", arms=[(-26, -76), (30 + 10 * hu, -150 + 70 * hu)] if 9.9 < t < 10.9 else None)
            if 8.6 < t < 9.9:
                q = ease_back(prog(t, 8.6, 0.4))
                text(c, "?", 700, 1100 - 260 * 1.6 / 1.6 - 70, 70 * q, INK)
        if 0 < hu < 1:
            hx = lerp(250, 620, hu)
            hy = lerp(812, 1100 - 172 * 1.6, hu) - math.sin(hu * math.pi) * 160
            c.save()
            c.translate(hx, hy)
            c.rotate((1 - hu) * 6)
            c.translate(-hx, -hy)
            hat_item(c, hx, hy, 1.4)
            c.restore()
        if 10.8 < t < 12.0:
            u = prog(t, 10.8, 1.2)
            r = random.Random(2)
            for k in range(10):
                a = r.uniform(0, 2 * math.pi)
                star(c, 620 + math.cos(a) * (80 + 120 * u), 1100 - 290 + math.sin(a) * (80 + 120 * u), 5, 1 - u)
    if flash > 0:
        c.set_source_rgba(1, 0.98, 0.92, flash)
        c.paint()


# ================================================================ 五、出逃
def s20_roots(c, t):
    shrink = [ease_io(prog(t, 0.4 + i * 0.45, 0.5)) for i in range(6)]
    stand = t > 3.1
    with cam(c, 540, 900, 1.12):
        room(c, t, sky="warm", hat_hook=False, chair=False, pack_corner=False)
        puddle = 1 - ease_io(prog(t, 0.6, 2.6))
        if puddle > 0:
            shape(c, ell(540, 1130, 420 * puddle + 40, 40 * puddle + 6, 26), WATER + (0.6,), "pud", lw=2)
        floor_roots(c, 540, 1112, t, shrink)
        if not stand:
            girl(c, 540, 1060, 1.6, sit=True, crouch=True, pack=True, hat=True, look=0.0, look_up=-1.0, head_down=10,
                 arms=[(-24 + 6 * math.sin(t * 6), -14), (26, -12 + 5 * math.sin(t * 5))], mouth="flat")
            for i in range(6):
                if shrink[i] < 1:
                    sg = -1 if i % 2 else 1
                    pts = [(540 + sg * 22, 1112), (540 + sg * 6, 1098 - i * 2), (540 - sg * 18, 1104), (540 + sg * 4 * (1 - shrink[i]), 1116)]
                    line(c, pts, f"tie20{i}", 5, hexc("76736d"), alpha=1 - shrink[i])
        else:
            u = ease_back(prog(t, 3.1, 0.5))
            girl(c, 540, 1110, 1.6, pack=True, hat=True, look=0.3, mouth="smile",
                 arms=[(-12, -112 + 8 * math.sin(t * 6)), (12, -112 + 8 * math.sin(t * 6))] if t < 4.2 else None)


def s20_door(c, t):
    tx = -480 * ease_io(prog(t, 0.0, 1.0))
    door = ease_io(prog(t, 0.5, 0.8))
    rad = 2400 * ease_io(prog(t, 0.9, 2.3))

    def scene(cc):
        cc.save()
        cc.translate(tx, 0)
        room(cc, t, sky="warm", hat_hook=False, chair=False, pack_corner=False, door=door)
        if door > 0:
            glow(cc, 1275, 830, 600 * door, hexc("fff0c0"), 0.6)
        x = lerp(820, 1200, ease_io(prog(t, 0.4, 2.2)))
        girl(cc, x, 1110, 1.6, view="back" if t > 1.4 else "front", look=1.0, walk=t * 8 if t < 2.6 else None)
        cc.restore()

    flood(c, scene, 1275 + tx, 830, rad, soft=420, from_sat=0.12, to_sat=1.0)
    if t > 1.0:
        GRADE["keep"] += 1
        r = random.Random(12)
        for i in range(40):
            st = r.uniform(1.0, 2.8)
            u = prog(t, st, 1.6)
            if 0 < u < 1:
                x = 1275 + tx - u * r.uniform(500, 1300)
                y = 830 + r.uniform(-260, 260) + math.sin(u * 8 + i) * 40 - u * r.uniform(-200, 300)
                c.save()
                c.translate(x, y)
                c.rotate(u * 10 + i)
                shape(c, ell(0, 0, 11, 6, 10), [hexc("f2a6a0"), hexc("fbe29a"), hexc("8fc3e3"), hexc("c9a0dc"), hexc("a9d28b")][i % 5],
                      f"dp{i}", lw=1.4, amp=0.4)
                c.restore()
        GRADE["keep"] -= 1


# ================================================================ 六、重活一遍
def s21_train(c, t):
    if t < 2.4:
        vgrad(c, 0, 900, [(0, hexc("8fc3e3")), (1, hexc("f3ecd2"))])
        for i, (x, y, s) in enumerate(((200, 200, 1.2), (760, 140, 0.9), (520, 330, 0.7))):
            cloud(c, x + t * 20, y, s, f"tcl{i}")
        shape(c, hill_pts(700, 50, 0.006, 1.0), hexc("a9c48b"), "th1", lw=3)
        shape(c, hill_pts(860, 30, 0.004, 2.0), hexc("bcd38f"), "th2", lw=3)
        r = random.Random(5)
        for i in range(60):
            circle(c, r.uniform(0, W), r.uniform(900, 1900), r.uniform(4, 8),
                   [hexc("f2a6a0"), hexc("fbe29a"), hexc("ffffff"), hexc("c9a0dc")][i % 4])
        line(c, [(-10, 905), (W + 10, 905)], "rl1", 5, hexc("8a5a3a"))
        x = lerp(-1200, 900, ease_out(prog(t, 0, 2.4)))
        for k in range(3):
            cx = x - k * 420
            col = hexc("c9553f") if k == 0 else hexc("e7d3a8")
            shape(c, rrect(cx - 400, 720, 400, 170, 18), col, f"tc{k}", lw=3)
            for j in range(3):
                shape(c, rect(cx - 370 + j * 120, 750, 90, 70), hexc("dff0f6"), f"tw{k}{j}", lw=2)
            for wx in (cx - 330, cx - 80):
                shape(c, ell(wx, 895, 22, 22, 12), hexc("4a3a33"), f"twh{k}{wx}", lw=2)
        hx = x - 420 - 370 + 120 + 45
        person(c, hx, 840, 0.62, legs=False, look=1.0, key="trg", keep_color=True, pack=False)
        for k in range(5):
            ph = (t * 1.3 + k * 0.2) % 1
            cloud(c, x - 60 - ph * 300, 680 - ph * 220, 0.3 + ph * 0.5, f"smk{k}", a=0.8 * (1 - ph))
    else:
        lt = t - 2.4
        vgrad(c, 0, 900, [(0, hexc("a9d2e6")), (1, hexc("fbf0d6"))])
        shape(c, hill_pts(760, 40, 0.005, 3.0), hexc("a9c48b"), "sh1", lw=3)
        shape(c, rect(-20, 900, W + 40, 1100), hexc("e9d5ad"), "splat", lw=3)
        shape(c, rect(80, 520, 360, 380), hexc("f4e2c2"), "shut", lw=3)
        shape(c, [(50, 520), (260, 400), (470, 520)], hexc("c9553f"), "shutr", lw=3)
        shape(c, rect(150, 600, 220, 70), hexc("4f7a5a"), "ssign", lw=2.6)
        for k in range(6):
            circle(c, 120 + k * 60, 905, 14, [hexc("f2a6a0"), hexc("fbe29a"), hexc("e07a5f")][k % 3])
        shape(c, rrect(620, 640, 520, 260, 20), hexc("c9553f"), "strain", lw=3)
        shape(c, rect(680, 700, 120, 200), hexc("8c3a2e"), "sdoor", lw=3)
        x = lerp(740, 520, ease_io(prog(lt, 0.0, 1.4)))
        girl(c, x, 1150, 1.5, look=-0.6, walk=lt * 8 if lt < 1.4 else None, mouth="smile", look_up=0.4)
        fl = 1 - ease_out(prog(lt, 0, 0.3))
        c.set_source_rgba(1, 1, 1, fl * 0.8)
        c.paint()


def q_market(c, t, w, h):
    fill_all(c, hexc("f6e3c4"))
    for i in range(7):
        shape(c, [(i * 76 - 10, 0), (i * 76 + 66, 0), (i * 76 + 66, 70), (i * 76 - 10, 82)],
              hexc("d1553f") if i % 2 == 0 else hexc("f8ecd7"), f"qa{i}", lw=2.2)
    line(c, [(20, 130), (w - 20, 130)], "rack", 4)
    for i, col in enumerate(("4f8a8b", "f0b84a", "8d6a9f", "e07a5f", "6f9a58")):
        x = 50 + i * 90
        sw = math.sin(t * 2 + i) * 4
        shape(c, [(x, 130), (x + 50, 130), (x + 64 + sw, 250), (x - 14 + sw, 250)], hexc(col), f"qd{i}", lw=2.2)
    sp = prog(t, 0.2, 0.8)
    sx = math.cos(sp * 2 * math.pi) if 0 < sp < 1 else 1
    girl(c, w / 2, h - 30, 1.2, outfit="dress" if sp > 0.5 else None, sx=max(abs(sx), 0.05), pack=False,
         hat=True, mouth="laugh" if sp >= 1 else "smile")
    shape(c, rect(-10, h - 30, w + 20, 40), hexc("d9b98f"), "qg", lw=2)


def q_dinner(c, t, w, h):
    fill_all(c, hexc("e9c79a"))
    glow(c, w / 2, 60, 280, hexc("ffd27a"), 0.7)
    line(c, [(w / 2, 0), (w / 2, 50)], "lan0", 2)
    shape(c, ell(w / 2, 80, 36, 42, 16), hexc("d1553f"), "lan", lw=2.4)
    person(c, 110, 330, 1.05, sit=True, legs=False, coat=hexc("4f8a8b"), hair=hexc("2f2a28"), hair_style="short",
           hat=False, pack=False, look=0.6, mouth="laugh", key="lo1", skin=hexc("e8bf9a"))
    person(c, w - 110, 330, 1.05, sit=True, legs=False, coat=hexc("8d6a9f"), hair=hexc("e3ddd5"), hair_style="granny",
           hat=False, pack=False, look=-0.6, mouth="laugh", key="lo2", skin=hexc("e8bf9a"))
    girl(c, w / 2, 340, 1.05, sit=True, legs=False, outfit="dress", pack=False, hat=False, mouth="laugh", eyes_closed=(t % 2) > 1.4)
    shape(c, ell(w / 2, 360, 230, 50, 24), hexc("a8744f"), "rtab", lw=3)
    for k, x in enumerate((w / 2 - 110, w / 2, w / 2 + 110)):
        shape(c, ell(x, 350, 34, 12, 14), hexc("f3efe6"), f"dish{k}", lw=2)
        circle(c, x, 346, 14, [hexc("e8823f"), hexc("7aa557"), hexc("d6463c")][k])
        line(c, [(x, 330), (x - 5 + math.sin(t * 2 + k) * 4, 300), (x + 2, 276)], f"dst{k}", 2, hexc("ffffff"), alpha=0.6)


def q_pottery(c, t, w, h):
    fill_all(c, hexc("e4d2b8"))
    shape(c, rect(-10, 330, w + 20, 200), hexc("c4a07a"), "pfl", lw=2.4)
    person(c, 130, 380, 1.15, sit=True, legs=False, coat=hexc("7f6a8f"), hair=hexc("e3ddd5"), hair_style="granny",
           hat=False, pack=False, look=0.8, mouth="smile", key="gran", skin=hexc("e8c4a2"), arms=[(50, -40), (60, -30)])
    shape(c, ell(250, 340, 90, 20, 20), hexc("8c6f4a"), "wheel", lw=2.6)
    pot = [(210, 336), (200, 300), (215, 270), (230, 255), (270, 255), (285, 270), (300, 300), (290, 336)]
    shape(c, pot, hexc("c47a4a"), "pot", lw=2.6)
    for k in range(3):
        y = 270 + k * 20
        off = (t * 60 + k * 15) % 60 - 30
        line(c, [(230 + off * 0.3, y), (270 + off * 0.3, y)], f"pr{k}", 1.6, hexc("9a5a3a"), alpha=0.7)
    girl(c, 380, 390, 1.15, sit=True, legs=False, outfit="dress", pack=False, hat=False, look=-0.8, look_up=-0.3,
         arms=[(-60, -46), (-40, -40)], mouth="o" if (t % 3) < 1 else "smile")


def q_alley(c, t, w, h):
    vgrad(c, 0, h, [(0, hexc("f7c79a")), (1, hexc("fbe6c4"))], 0, w)
    glow(c, w / 2, 170, 200, hexc("fff0b0"), 0.8)
    shape(c, [(-10, 0), (170, 120), (170, 330), (-10, h + 10)], hexc("d9b48f"), "alw", lw=2.6)
    shape(c, [(w + 10, 0), (w - 170, 120), (w - 170, 330), (w + 10, h + 10)], hexc("e4c39f"), "alr", lw=2.6)
    shape(c, [(170, 330), (w - 170, 330), (w + 10, h + 10), (-10, h + 10)], hexc("cdb48e"), "alg", lw=2.6)
    for i in range(6):
        y = 340 + i * i * 6
        line(c, [(150 - i * 30, y), (w - 150 + i * 30, y)], f"alc{i}", 1.4, hexc("b39a74"), alpha=0.6)
    for k, (x0, s) in enumerate(((200, 0.55), (300, 0.6))):
        x = x0 + math.sin(t + k) * 4
        person(c, x, 360 - k * 6, s, view="back", coat=[hexc("4f8a8b"), hexc("8d6a9f")][k], hair=hexc("2f2a28"),
               hair_style="short", hat=False, pack=False, walk=t * 6 + k, key=f"al{k}")
        shape(c, ell(x + 18 * s, 360 - k * 6 - 80 * s, 16 * s, 10 * s, 10), hexc("c49a6c"), f"bask{k}", lw=2)
    girl(c, w / 2 + 30, 430, 0.8, view="back", outfit="dress", pack=True, hat=True, walk=t * 6)


def s22_panels(c, t):
    fill_all(c, hexc("f3e7d2"))
    panel(c, 40, 130, 490, 480, ease_back(prog(t, 0.1, 0.5)), "q1", q_market, t, rot=-0.01)
    panel(c, 550, 130, 490, 480, ease_back(prog(t, 1.7, 0.5)), "q2", q_dinner, t - 1.7, rot=0.008)
    panel(c, 40, 650, 490, 480, ease_back(prog(t, 4.6, 0.5)), "q3", q_pottery, t - 4.6, rot=0.006)
    panel(c, 550, 650, 490, 480, ease_back(prog(t, 6.2, 0.5)), "q4", q_alley, t - 6.2, rot=-0.008)


def s24_badge(c, t):
    fill_all(c, hexc("e7c9a0"))
    for i in range(10):
        line(c, [(i * 120, 0), (i * 120, H)], f"wood{i}", 2, hexc("cfa77c"), alpha=0.7)
    shape(c, rect(560, 160, 420, 520), hexc("f7e6c4"), "iwin", lw=3)
    glow(c, 770, 420, 420, hexc("fff0c0"), 0.7)
    shape(c, rect(740, 160, 20, 520), hexc("8c5a3c"), "iwm", lw=2.6)
    shape(c, rect(600, 900, 460, 30), hexc("8c5a3c"), "shelf", lw=3)
    bx, by = 820, 900
    lid = ease_io(prog(t, 2.5, 0.6))
    shape(c, rect(bx - 110, by - 110, 220, 110), hexc("b37a4c"), "box", lw=3)
    gx, gy, s = 380, 1360, 3.2
    take = ease_io(prog(t, 0.8, 1.0))
    drop = ease_io(prog(t, 1.8, 0.7))
    chest = (gx, gy + (-100 + 14) * s)
    held = (gx + 42 * s, gy - 112 * s)
    into = (bx, by - 60)
    if drop > 0:
        bp = (lerp(held[0], into[0], drop), lerp(held[1], into[1], drop))
    else:
        bp = (lerp(chest[0], held[0], take), lerp(chest[1], held[1], take))
    if drop > 0:
        hand = (lerp(42, 28, drop), lerp(-112, -72, drop))
    else:
        hand = ((bp[0] - gx) / s, (bp[1] - gy) / s)
    girl(c, gx, gy, s, outfit="dress", pack=False, hat=True, look=0.5, look_up=0.3 if t < 2.4 else 0.0,
         arms=[(-26, -76), hand], mouth="smile", eyes_closed=t > 3.0)
    if t < 2.5 or lid < 0.3:
        c.save()
        c.translate(*bp)
        c.scale(2.6, 2.6)
        if t < 0.8:
            line(c, [(-9, -24), (0, 0), (9, -24)], "lan24", 2.2, hexc("3f6fb5"))
        shape(c, rect(-11, 0, 22, 28), hexc("f8f6f0"), "bdg24", lw=1.4, amp=0.3)
        circle(c, -3, 9, 4, hexc("9fb7d4"))
        line(c, [(-6, 20), (7, 20)], "bdl", 1.2)
        c.restore()
    c.save()
    c.translate(bx - 110, by - 110)
    c.rotate(-(1 - lid) * 1.6)
    shape(c, rect(0, -22, 220, 22), hexc("c98c5a"), "lid", lw=3)
    c.restore()


def s25_redraw(c, t):
    vgrad(c, 0, 1000, [(0, hexc("f2b9a0")), (0.6, hexc("f8d7a8")), (1, hexc("fbecc8"))])
    sun_y = lerp(820, 640, ease_io(t / 6))
    glow(c, 540, sun_y, 520, hexc("fff0b8"), 0.75)
    circle(c, 540, sun_y, 90, hexc("fff3cf"))
    if t > 3.6:
        a = ease_io(prog(t, 3.6, 1.0))
        for k in range(12):
            ang = k * math.pi / 6 + t * 0.1
            c.move_to(540, sun_y)
            c.line_to(540 + math.cos(ang - 0.06) * 1400, sun_y + math.sin(ang - 0.06) * 1400)
            c.line_to(540 + math.cos(ang + 0.06) * 1400, sun_y + math.sin(ang + 0.06) * 1400)
            c.close_path()
            c.set_source_rgba(1, 0.96, 0.82, 0.12 * a)
            c.fill()
    shape(c, hill_pts(860, 40, 0.006, 0.5), hexc("a9c48b"), "rh1", lw=3)
    for i, (x, w_, h_, wc, rc) in enumerate(((60, 120, 140, "f1c27d", "b4533f"), (200, 100, 180, "8fc0b5", "3f6f73"),
                                              (800, 110, 150, "f3e3c3", "3c6ea5"), (930, 100, 120, "e98f6f", "8b4a3a"))):
        house(c, x, 900, w_, h_, hexc(wc), hexc(rc), f"rv{i}", "tri" if i % 2 == 0 else "flat")
    shape(c, rect(-20, 900, W + 40, 1100), hexc("cfe0a8"), "rgr", lw=3)
    gx, gy, s = 540, 1150, 2.1
    # 旧的她：颜色褪去 → 线条被擦掉
    fade_fill = 1 - ease_io(prog(t, 0.3, 0.8))
    erase = ease_io(prog(t, 1.1, 1.0))
    draw_new = ease_io(prog(t, 2.2, 1.4))
    bloom = ease_io(prog(t, 3.6, 0.8))
    top, bot = gy - 210 * s, gy + 20
    kw_old = dict(look=0.0, mouth="flat")
    kw_new = dict(outfit="dress", look=0.0, mouth="laugh" if t > 4.4 else "smile", eyes_closed=t > 4.6)
    if t < 2.2:
        if fade_fill > 0:
            with fill_only(), group_alpha(c, fade_fill):
                girl(c, gx, gy, s, **kw_old)
        ey = lerp(top, bot, erase)
        c.save()
        c.rectangle(0, ey, W, H)
        c.clip()
        with outline_only():
            girl(c, gx, gy, s, **kw_old)
        c.restore()
        if 0 < erase < 1:
            r = random.Random(int(t * 20))
            for k in range(10):
                star(c, gx + r.uniform(-110, 110), ey + r.uniform(-10, 10), 4, 0.9, hexc("fff6d0"))
    else:
        dy = lerp(top, bot, draw_new)
        if bloom > 0:
            with fill_only(), group_alpha(c, bloom):
                girl(c, gx, gy, s, **kw_new)
        c.save()
        c.rectangle(0, 0, W, dy)
        c.clip()
        with outline_only():
            girl(c, gx, gy, s, **kw_new)
        c.restore()
        if 0 < draw_new < 1:
            px = gx + math.sin(t * 40) * 90
            c.save()
            c.translate(px, dy)
            c.rotate(-0.6)
            shape(c, [(0, 0), (10, -24), (18, -20), (8, 4)], hexc("f0c04a"), "pen1", lw=2)
            shape(c, [(10, -24), (40, -110), (48, -106), (18, -20)], hexc("e8b94a"), "pen2", lw=2.2)
            c.restore()
    if t > 3.8:
        r = random.Random(9)
        for i in range(22):
            sp = r.uniform(40, 90)
            x = (r.uniform(0, W) + (t - 3.8) * sp) % W
            y = (r.uniform(0, 1100) + (t - 3.8) * sp * 1.5) % 1200
            c.save()
            c.translate(x, y)
            c.rotate(t * 2 + i)
            shape(c, ell(0, 0, 9, 5, 10), hexc("f2a6a0"), f"pt{i}", lw=1.4, amp=0.4)
            c.restore()


_STILL = {}


def redraw_still():
    if "s" not in _STILL:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(129.4)
        with grade(sat=1.0, dark=0.0, warm=0.0):
            s25_redraw(cc, 5.95)
        _STILL["s"] = surf
    return _STILL["s"]


def outro(c, t):
    book_outro(c, t, redraw_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第一章 · 完")

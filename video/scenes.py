"""12 个分镜。每个函数 fn(c, t) 中 t 为该镜头内的本地时间（秒）。"""
import math
import random

import cairo

from draw import *  # noqa: F401,F403

BAR = 2.5
BEAT = BAR / 4


def sky_stars(c, t, n, x0, y0, x1, y1, seed=1, a=1.0):
    r = random.Random(seed)
    for i in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        tw = 0.55 + 0.45 * math.sin(t * r.uniform(2, 4) + i)
        star(c, x, y, r.uniform(2, 4.5), tw * a)


# ================================================================ 房间
def room(c, t, mode="s1", door_open=0.0, dim=0.0):
    # 墙
    c.set_source_rgb(*hexc("ead7b8"))
    c.paint()
    for i in range(34):
        x = i * 80 + 20
        line(c, [(x, 0), (x, 830)], f"wp{i}", 2.0, hexc("dcc39c"), alpha=0.6, amp=1.0)
        for j in range(10):
            circle(c, x + 40, 40 + j * 84 + (i % 2) * 42, 3.2, hexc("d8a98a"), 0.55)
    # 窗外夜空
    gx0, gy0, gx1, gy1 = 670, 180, 1250, 630
    c.save()
    c.rectangle(gx0, gy0, gx1 - gx0, gy1 - gy0)
    c.clip()
    vgrad(c, gy0, gy1, [(0, hexc("1d2647")), (0.7, hexc("34477a")), (1, hexc("5b6a9a"))])
    sky_stars(c, t, 22, gx0 + 10, gy0 + 10, gx1 - 10, gy0 + 300, seed=4)
    glow(c, 1120, 270, 150, hexc("fff3cf"), 0.35)
    shape(c, ell(1120, 270, 40, 40, 18), hexc("fbf0cf"), "moon", lw=2.5)
    roofs = [(660, 560), (740, 520), (820, 545), (900, 500), (990, 535), (1060, 490), (1150, 530), (1260, 510)]
    pts = [(660, 640)]
    for i, (x, y) in enumerate(roofs):
        pts += [(x, y), (x + 40, y - 30 if i % 2 else y), (x + 80, y)]
    pts += [(1270, 640)]
    shape(c, pts, hexc("26304f"), "roofs", ink=False)
    r = random.Random(9)
    for i in range(14):
        wx, wy = r.uniform(680, 1230), r.uniform(560, 615)
        on = 0.6 + 0.4 * math.sin(t * 1.3 + i * 2)
        c.rectangle(wx, wy, 9, 11)
        c.set_source_rgba(*hexc("f8d77a"), 0.8 * on)
        c.fill()
    c.restore()
    # 窗框
    shape(c, rect(640, 150, 640, 510), None, "wframe", lw=4)
    for (x, y, w, h) in ((640, 150, 640, 30), (640, 630, 640, 30), (640, 150, 30, 510), (1250, 150, 30, 510),
                         (945, 180, 30, 450)):
        shape(c, rect(x, y, w, h), hexc("8c5a3c"), f"wf{x}{y}", lw=3)
    # 窗帘
    sway = math.sin(t * 1.2) * 6
    shape(c, [(560, 120), (690, 120), (660 + sway, 400), (690 + sway, 700), (575, 700), (590, 400)], hexc("d4876a"), "curL", lw=3)
    shape(c, [(1230, 120), (1360, 120), (1330 - sway, 400), (1345 - sway, 700), (1230 - sway, 700), (1260, 400)], hexc("d4876a"), "curR", lw=3)
    line(c, [(540, 118), (1380, 118)], "rod", 6, hexc("6b4430"))
    # 窗下长凳
    shape(c, rect(650, 704, 620, 22), hexc("cbd8a5"), "cush", lw=3)
    shape(c, rect(660, 726, 600, 104), hexc("a0694a"), "bench", lw=3)
    shape(c, rect(690, 748, 250, 64), hexc("94603f"), "bp1", lw=2.4)
    shape(c, rect(980, 748, 250, 64), hexc("94603f"), "bp2", lw=2.4)
    # 地板
    shape(c, rect(-20, 830, W + 700, 300), hexc("bb8c63"), "floor", lw=3)
    for i in range(6):
        line(c, [(-10, 870 + i * 45), (W + 680, 870 + i * 45)], f"fl{i}", 1.8, hexc("9c714d"), alpha=0.7)
    shape(c, ell(960, 940, 400, 62, 26), hexc("c96f53"), "rug", lw=3)
    shape(c, ell(960, 940, 330, 46, 26), None, "rug2", lw=2)
    # 书桌与台灯
    shape(c, rect(170, 640, 360, 26), hexc("8c5a3c"), "desk", lw=3)
    for x in (190, 490):
        shape(c, rect(x, 666, 20, 164), hexc("7a4d33"), f"dl{x}", lw=2.6)
    shape(c, rect(330, 616, 170, 26), hexc("efe2c2"), "map", lw=2.4)
    line(c, [(345, 632), (380, 624), (420, 634), (460, 622), (485, 628)], "route", 2, hexc("c0503c"))
    for i in range(3):
        shape(c, rect(195, 612 - i * 16, 110, 16), [hexc("6b8fb3"), hexc("d6a34a"), hexc("9b5b4a")][i], f"book{i}", lw=2.2)
    shape(c, rect(244, 520, 10, 76), hexc("5b4a3a"), "lampst", lw=2)
    shape(c, [(205, 470), (295, 470), (318, 528), (182, 528)], hexc("ebb75b"), "shade", lw=3)
    # 门
    shape(c, rect(1450, 312, 300, 528), hexc("7a4d33"), "doorframe", lw=3)
    if door_open > 0:
        g = cairo.LinearGradient(1470, 0, 1730, 0)
        g.add_color_stop_rgb(0, *hexc("fff6dc"))
        g.add_color_stop_rgb(1, *hexc("ffe6a8"))
        c.set_source(g)
        c.rectangle(1470, 330, 260, 500)
        c.fill()
        glow(c, 1600, 580, 420 * door_open, hexc("fff0c0"), 0.55 * door_open)
    fx = 1470 + door_open * 230
    dpts = [(fx, 330 - door_open * 30), (1730, 330), (1730, 830), (fx, 830 + door_open * 30)]
    shape(c, dpts, hexc("9b6b4a"), "door", lw=3)
    if door_open < 0.6:
        dw = 1730 - fx
        for j in range(2):
            shape(c, rect(fx + dw * 0.14, 370 + j * 220, dw * 0.72, 180), hexc("8c5d3f"), f"dpan{j}", lw=2.2)
        circle(c, fx + dw * 0.12, 590, 9, hexc("e1b44f"))
    # 挂钩上的帽子和背包
    if mode == "s1":
        line(c, [(1350, 420), (1350, 404)], "hook", 4)
        shape(c, rrect(1318, 430, 64, 74, 12), PACK, "hpack", lw=3)
        shape(c, ell(1350, 425, 54, 12, 20), STRAW, "hhat", lw=3)
        shape(c, [(1328, 424), (1330, 400), (1370, 400), (1372, 424)], STRAW, "hhat2", lw=3)
        shape(c, rect(1328, 412, 44, 8), RIBBON, "hrib", lw=2)
    # 盆栽
    shape(c, [(1300, 830), (1290, 770), (1370, 770), (1360, 830)], hexc("c66b4a"), "pot", lw=3)
    for i in range(5):
        a = -math.pi / 2 + (i - 2) * 0.45 + math.sin(t * 1.5 + i) * 0.05
        shape(c, ell(1330 + math.cos(a) * 40, 770 + math.sin(a) * 50, 14, 28, 12), hexc("6f9a58"), f"leaf{i}", lw=2.4)
    # 台灯光
    glow(c, 250, 540, 330, hexc("ffd98a"), 0.42 * (1 - dim))
    if dim > 0:
        c.set_source_rgba(*hexc("141a3c"), dim)
        c.paint()


def s1(c, t):
    k = 1 + 0.07 * ease_io(t / 5)
    c.save()
    c.translate(960, 520)
    c.scale(k, k)
    c.translate(-960, -520)
    room(c, t, "s1")
    girl(c, 960, 706, 1.25, view="back", sit=True, hat=False, pack=False, walk=t * 1.5,
         head_down=-2 + 2 * math.sin(t * 0.8))
    c.restore()


def s2(c, t):
    if t < 2.4:
        cam = ease_io(t / 0.9)
        door = ease_io(prog(t, 0.5, 0.9))
        z = 1 + 6 * ease_in(prog(t, 1.4, 1.0))
        tx = lerp(960, 1450, cam)
        c.save()
        c.translate(960, 540)
        c.scale(z, z)
        cx = lerp(tx, 1600, ease_io(prog(t, 1.3, 0.8)))
        c.translate(-cx, -lerp(540, 580, ease_io(prog(t, 1.3, 0.8))))
        room(c, t, "s2", door_open=door)
        wx = lerp(1300, 1560, ease_io(prog(t, 1.2, 1.2)))
        walking = 1.2 < t
        girl(c, wx, 840, 1.25, look=1.0, walk=(t * 9 if walking else None))
        c.restore()
        fl = ease_in(prog(t, 2.0, 0.4))
        c.set_source_rgba(*hexc("fff6e0"), fl)
        c.paint()
        return
    lt = t - 2.4
    vgrad(c, 0, H, [(0, hexc("a9cfe2")), (0.74, hexc("f6ead2")), (1, hexc("f6ead2"))])
    k = ease_back(prog(lt, 0.05, 0.5))
    with popup(c, 1550, 300, k):
        glow(c, 1550, 220, 200, hexc("fff2b8"), 0.6)
        shape(c, ell(1550, 220, 64, 64, 20), hexc("fbe39a"), "sun2", lw=3)
    for i, (x, y, s) in enumerate(((380, 180, 1.0), (980, 140, 0.8), (1300, 300, 0.7))):
        kk = ease_back(prog(lt, 0.2 + i * 0.12, 0.5))
        if kk > 0.01:
            cloud(c, x + lt * 14, y, s * kk, f"cl2{i}")
    k = ease_back(prog(lt, 0.15, 0.55))
    with popup(c, 960, 700, k):
        for i, (x, w, h) in enumerate(((300, 700, 330), (800, 600, 260), (1350, 800, 380), (1800, 600, 280))):
            mountain(c, x, 700, w, h, hexc("a7b4d0"), f"mt2{i}", snow=i % 2 == 0)
    k = ease_back(prog(lt, 0.35, 0.55))
    with popup(c, 960, 800, k):
        shape(c, hill_pts(700, 30, 0.004, 1.0), hexc("a9c48b"), "hill2", lw=3)
    k = ease_back(prog(lt, 0.25, 0.5))
    with popup(c, 960, 1080, k):
        shape(c, hill_pts(800, 12, 0.003, 2.0), hexc("c7d89c"), "gr2", lw=3)
        shape(c, [(-40, 880), (500, 840), (1000, 820), (1500, 790), (1960, 770), (1960, 800), (1500, 830),
                  (1000, 870), (500, 900), (-40, 940)], hexc("e8d0a2"), "path2", lw=3)
    for i, (x, s) in enumerate(((1120, 0.9), (1280, 1.1), (1480, 0.85), (1700, 1.2), (180, 1.0))):
        kk = ease_back(prog(lt, 0.6 + i * 0.12, 0.45))
        if kk > 0.01:
            with popup(c, x, 800, kk):
                tree(c, x, 800, s, f"tr2{i}", hexc("74a160") if i % 2 else hexc("8fb46a"))
    kk = ease_back(prog(lt, 1.3, 0.45))
    if kk > 0.01:
        with popup(c, 1020, 850, kk):
            shape(c, rect(1014, 740, 12, 110), hexc("8a5a3a"), "post", lw=2.6)
            shape(c, [(980, 750), (1080, 750), (1100, 770), (1080, 790), (980, 790)], hexc("efd9a8"), "sign", lw=2.6)
    for i in range(3):
        bx = 600 + i * 70 + lt * 40
        by = 260 + i * 18 + math.sin(lt * 3 + i) * 6
        fl = math.sin(lt * 10 + i)
        line(c, [(bx - 14, by - 6 * fl), (bx, by), (bx + 14, by - 6 * fl)], f"bird2{i}", 2.4)
    x = lerp(240, 760, ease_io(prog(lt, 0.2, 2.4)))
    girl(c, x, 905, 1.15, look=1.0, walk=lt * 9 if lt < 2.6 else None)
    fl = 1 - ease_out(prog(lt, 0, 0.5))
    c.set_source_rgba(*hexc("fff6e0"), fl)
    c.paint()


# ================================================================ 城市
CITY_BACK = [(60, 150, 300, "e9c9a6", "c98a6a"), (240, 130, 360, "dfd5c0", "8aa0b5"), (400, 170, 260, "efd8b0", "b9705a"),
             (600, 140, 340, "e5cdb6", "a3816a"), (780, 160, 280, "f0e0c4", "7f9a8d"), (980, 150, 380, "e2c9a9", "c08060"),
             (1160, 140, 300, "ecd9bb", "8b93b0"), (1330, 170, 340, "e7d0b2", "b8735b"), (1530, 150, 280, "efe0c8", "86a28f"),
             (1710, 170, 330, "e3cbaa", "a77d65")]
CITY_FRONT = [(-20, 210, 330, "f1c27d", "b4533f", "tri"), (200, 170, 270, "8fc0b5", "3f6f73", "flat"),
              (380, 220, 360, "f3e3c3", "3c6ea5", "dome"), (620, 190, 290, "e98f6f", "8b4a3a", "tri"),
              (1240, 200, 320, "a7c38a", "5d7a45", "tri"), (1460, 180, 260, "f3d58b", "a8613f", "flat"),
              (1660, 260, 370, "c9b3d9", "6e5a8c", "tri")]


def s3(c, t):
    vgrad(c, 0, 840, [(0, hexc("f4cba5")), (1, hexc("f8ead0"))])
    glow(c, 1500, 250, 260, hexc("fff0b0"), 0.6)
    k = ease_back(prog(t, 0.0, 0.5))
    with popup(c, 1500, 330, k):
        shape(c, ell(1500, 250, 80, 80, 22), hexc("fbe29a"), "sun3", lw=3)
    drift = t * 6
    for i, (x, w, h, wc, rc) in enumerate(CITY_BACK):
        kk = ease_back(prog(t, 0.05 + i * 0.04, 0.5))
        if kk > 0.01:
            with popup(c, x, 640, kk):
                c.save()
                c.translate(-drift * 0.4, 0)
                house(c, x, 640, w, h, mix(hexc(wc), hexc("f6e6cf"), 0.35), mix(hexc(rc), hexc("f6e6cf"), 0.35), f"cb{i}", door=False)
                c.restore()
    # 彩旗
    kk = ease_out(prog(t, 0.6, 0.6))
    if kk > 0:
        pts = [(x, 250 + 90 * math.sin(math.pi * (x / W))) for x in range(0, W + 1, 60)]
        line(c, [(x, y) for x, y in pts[:max(2, int(len(pts) * kk))]], "string", 2.2)
        cols = [hexc(h) for h in ("d1553f", "f0b84a", "4f8a8b", "8d6a9f", "6f9a58")]
        for i, (x, y) in enumerate(pts[:int(len(pts) * kk) - 1]):
            fl = math.sin(t * 6 + i) * 5
            shape(c, [(x + 6, y + 2), (x + 46, y + 4), (x + 26 + fl, y + 44)], cols[i % 5], f"flag{i}", lw=2, amp=0.6)
    for i, (x, w, h, wc, rc, rt) in enumerate(CITY_FRONT):
        kk = ease_back(prog(t, 0.2 + i * 0.07, 0.5))
        if kk > 0.01:
            with popup(c, x, 830, kk):
                house(c, x, 830, w, h, hexc(wc), hexc(rc), f"cf{i}", rt)
    # 屋顶上的猫
    kk = ease_back(prog(t, 1.1, 0.4))
    if kk > 0.01:
        with popup(c, 1590, 650, kk):
            cx, cy = 1590, 650
            shape(c, ell(cx, cy - 18, 20, 18, 14), hexc("4a3a33"), "cat", lw=2.4)
            shape(c, ell(cx + 6, cy - 44, 14, 13, 12), hexc("4a3a33"), "cath", lw=2.4)
            shape(c, [(cx - 4, cy - 52), (cx - 2, cy - 64), (cx + 6, cy - 55)], hexc("4a3a33"), "cate1", lw=2)
            shape(c, [(cx + 8, cy - 55), (cx + 16, cy - 64), (cx + 18, cy - 50)], hexc("4a3a33"), "cate2", lw=2)
            tail = math.sin(t * 3) * 10
            line(c, [(cx - 18, cy - 8), (cx - 36, cy - 20), (cx - 40 + tail, cy - 44)], "catt", 5, hexc("4a3a33"))
    # 市集摊位
    kk = ease_back(prog(t, 0.7, 0.5))
    if kk > 0.01:
        with popup(c, 1050, 840, kk):
            shape(c, rect(930, 720, 240, 110), hexc("c49a6c"), "stall", lw=3)
            for i in range(6):
                shape(c, [(910 + i * 47, 640), (957 + i * 47, 640), (957 + i * 47, 690), (910 + i * 47, 700)],
                      hexc("d1553f") if i % 2 == 0 else hexc("f8ecd7"), f"awn{i}", lw=2.4)
            for i in range(8):
                circle(c, 950 + i * 27, 712, 13, [hexc("e8823f"), hexc("d6463c"), hexc("f2c14e"), hexc("7aa557")][i % 4])
    shape(c, rect(-20, 830, W + 40, 260), hexc("dcc196"), "street", lw=3)
    r = random.Random(3)
    for i in range(40):
        x, y = r.uniform(0, W), r.uniform(850, 1060)
        shape(c, ell(x, y, 22, 8, 10), None, f"cob{i}", lw=1.6, amp=0.8)
    # 女孩：走入 → 转圈换装 → 跳一下
    x = lerp(220, 860, ease_io(prog(t, 0.2, 2.1)))
    sp = prog(t, 2.35, 0.7)
    outfit = "dress" if sp >= 0.5 else None
    sx = math.cos(sp * 2 * math.pi) if 0 < sp < 1 else 1.0
    hop = -math.sin(math.pi * prog(t, 3.2, 0.45)) * 40
    walking = t < 2.3
    girl(c, x, 930 + hop, 1.2, look=1.0 if walking else 0.2, walk=t * 9 if walking else None,
         outfit=outfit, sx=sx if abs(sx) > 0.05 else 0.05, pack=True)
    if 0.3 < sp < 1.0 or 3.2 < t < 3.9:
        r = random.Random(int(t * 12))
        for i in range(8):
            a = r.uniform(0, 2 * math.pi)
            d = r.uniform(70, 150)
            star(c, x + math.cos(a) * d, 930 - 120 + math.sin(a) * d, r.uniform(3, 6), 0.9, hexc("fff3b0"))


# ================================================================ 圣托里尼
def santorini(c, t, x0, y0, w, h):
    c.save()
    c.rectangle(x0, y0, w, h)
    c.clip()
    hz = y0 + h * 0.6
    vgrad(c, y0, hz, [(0, hexc("8fb9da")), (0.6, hexc("f2c6a4")), (1, hexc("f7d39b"))], x0, x0 + w)
    sy = hz - 20 + t * 7
    glow(c, x0 + w * 0.72, sy, 180, hexc("ffd08a"), 0.7)
    circle(c, x0 + w * 0.72, sy, 46, hexc("f6a25b"))
    vgrad(c, hz, y0 + h, [(0, hexc("4176a8")), (1, hexc("234d7a"))], x0, x0 + w)
    r = random.Random(5)
    for i in range(40):
        yy = hz + 8 + r.uniform(0, h * 0.35)
        xx = x0 + w * 0.72 + r.uniform(-60, 60) * (1 + (yy - hz) / 120)
        ln = r.uniform(10, 34)
        a = 0.4 + 0.4 * math.sin(t * 4 + i)
        c.move_to(xx - ln / 2 + math.sin(t * 2 + i) * 6, yy)
        c.rel_line_to(ln, 0)
        c.set_source_rgba(*hexc("ffd9a0"), a)
        c.set_line_width(2.4)
        c.stroke()
    # 远处小帆船
    bx = x0 + w * 0.45 + t * 10
    shape(c, [(bx - 20, hz + 30), (bx + 20, hz + 30), (bx + 14, hz + 38), (bx - 14, hz + 38)], hexc("f6f1e7"), "boat", lw=2)
    shape(c, [(bx, hz - 10), (bx, hz + 28), (bx + 18, hz + 28)], hexc("fbf8f0"), "sail", lw=2)
    # 悬崖与白房子
    cliff = [(x0 - 10, y0 + h + 10), (x0 - 10, hz - 120), (x0 + w * 0.12, hz - 150), (x0 + w * 0.3, hz - 80),
             (x0 + w * 0.42, hz + 40), (x0 + w * 0.5, y0 + h + 10)]
    shape(c, cliff, hexc("b98e6b"), "cliff", lw=3)
    houses = [(0.02, -150, 80, 60, None), (0.1, -160, 70, 50, "dome"), (0.18, -120, 90, 54, None),
              (0.05, -90, 100, 56, None), (0.16, -60, 80, 50, "dome"), (0.26, -70, 90, 50, None),
              (0.1, -30, 90, 52, None), (0.22, -10, 80, 50, None), (0.32, 10, 70, 46, None)]
    for i, (fx, oy, ww, hh, kind) in enumerate(houses):
        hx = x0 + w * fx
        hb = hz + oy
        shape(c, rect(hx, hb - hh, ww, hh), hexc("f8f5ee"), f"sw{i}", lw=2.4)
        shape(c, rect(hx + ww * 0.4, hb - 26, 16, 26), hexc("3a6ea5"), f"sd{i}", lw=2)
        if kind == "dome":
            shape(c, ell(hx + ww / 2, hb - hh, ww * 0.36, ww * 0.36, 14, math.pi, 2 * math.pi), hexc("2f63a8"), f"sdm{i}", lw=2.4)
            line(c, [(hx + ww / 2, hb - hh - ww * 0.36), (hx + ww / 2, hb - hh - ww * 0.36 - 16)], f"sx{i}", 2)
    c.restore()


def s4(c, t):
    k = 1 + 0.04 * ease_io(t / 5)
    c.save()
    c.translate(960, 540)
    c.scale(k, k)
    c.translate(-960, -540)
    c.set_source_rgb(*hexc("f1e6d2"))
    c.paint()
    glow(c, 1230, 420, 800, hexc("f9d9b0"), 0.45)
    shape(c, ell(700, 840, 760, 70, 30), hexc("c9d6a2"), "lawn", lw=3)
    fx, fy, fw, fh = 790, 120, 900, 580
    shape(c, rect(fx - 30, fy - 30, fw + 60, fh + 60), hexc("c9a050"), "frame", lw=3.5)
    shape(c, rect(fx - 12, fy - 12, fw + 24, fh + 24), hexc("a87f3a"), "frame2", lw=2.5)
    santorini(c, t, fx, fy, fw, fh)
    shape(c, rect(fx, fy, fw, fh), None, "fin", lw=3)
    # 长椅
    shape(c, rect(330, 676, 520, 20), hexc("a0694a"), "bb1", lw=3)
    shape(c, rect(330, 706, 520, 20), hexc("a0694a"), "bb2", lw=3)
    for x in (360, 800):
        shape(c, rect(x, 696, 16, 120), hexc("7a4d33"), f"bl{x}", lw=2.6)
    shape(c, rect(320, 770, 540, 24), hexc("b37a55"), "bseat", lw=3)
    girl(c, 450, 790, 1.15, sit=True, look=1.0, look_up=0.6, walk=t * 1.2)
    with ink_style(hexc("8d7a6a"), [8, 9], 0.55):
        person(c, 720, 790, 1.2, sit=True, look=-0.6, coat=hexc("efe4d2"), hair=hexc("e8dcc8"), skin=hexc("f4ece0"),
               leg=hexc("d8cbb8"), shoe=hexc("d8cbb8"), hat=False, pack=False, hair_style="short", key="empty", alpha=0.55)
    r = random.Random(11)
    for i in range(14):
        sp = r.uniform(30, 60)
        x = (r.uniform(-200, W) + t * sp * 3) % (W + 200) - 100
        y = (r.uniform(0, H) + t * sp) % H
        a = t * 2 + i
        c.save()
        c.translate(x, y)
        c.rotate(a)
        shape(c, ell(0, 0, 7, 4, 10), hexc("f2a6a0"), f"pet{i}", lw=1.4, amp=0.4)
        c.restore()
    c.restore()


# ================================================================ 同路人蒙太奇
def mont_bike(c, t):
    vgrad(c, 0, 840, [(0, hexc("bfe0ec")), (1, hexc("fdf3dc"))])
    for i, (x, y, s) in enumerate(((300, 160, 1.0), (900, 120, 0.8), (1500, 200, 0.9), (2100, 150, 1))):
        cloud(c, (x - t * 40) % 2200 - 140, y, s, f"cb{i}")
    for layer, (sp, base, amp, col) in enumerate(((60, 620, 50, "aac1d4"), (180, 720, 40, "9fc285"))):
        off = t * sp
        shape(c, hill_pts(base, amp, 0.004, off * 0.004 + layer), hexc(col), f"mh{layer}", lw=3)
    shape(c, rect(-20, 780, W + 40, 320), hexc("bcd38f"), "mgr", lw=3)
    shape(c, rect(-20, 830, W + 40, 90), hexc("dcc7a1"), "road", lw=3)
    off = (t * 700) % 160
    for i in range(14):
        x = i * 160 - off
        line(c, [(x, 875), (x + 70, 875)], f"rd{i}", 4, hexc("f7f0de"))
    for i in range(9):
        x = (i * 260 - t * 520) % (W + 260) - 130
        shape(c, rect(x, 740, 10, 50), hexc("a77d55"), f"fp{i}", lw=2)
        circle(c, x + 60, 800, 7, hexc("f2a6a0"))
        circle(c, x + 140, 795, 6, hexc("fbe29a"))
    line(c, [(-10, 755), (W + 10, 755)], "fence", 2.4, hexc("a77d55"))
    riders = [(560, 1, COMPANIONS[0]), (930, 0, None), (1300, 2, COMPANIONS[1])]
    cols = [hexc("4f8a8b"), hexc("d1553f"), hexc("e07a5f")]
    for i, (x, ci, comp) in enumerate(riders):
        by = 900 + math.sin(t * 9 + i) * 3
        bicycle(c, x, by, 1.05, -t * 14, cols[i], f"bk{i}")
        if comp is None:
            girl(c, x - 12, by - 86, 0.95, sit=True, look=1.0, legs=False, arms=[(22, -88), (28, -86)])
        else:
            companion(c, [0, 1][i // 2], x - 12, by - 86, 1.0, sit=True, look=1.0, legs=False, arms=[(22, -88), (28, -86)])
        for k in range(2):
            ang = t * 14 + k * math.pi
            px, py = x + 6 + math.cos(ang) * 12, by - 34 + math.sin(ang) * 12
            line(c, [(x - 12, by - 86), (lerp(x - 12, px, 0.5) + 8, lerp(by - 86, py, 0.5)), (px, py)], f"pl{i}{k}", 6, LEG, amp=0.4)
    for i in range(6):
        y = 640 + i * 40
        x = (i * 330 - t * 1400) % (W + 400) - 200
        line(c, [(x, y), (x + 120, y - 4)], f"wind{i}", 2.4, (1, 1, 1), alpha=0.7)


def mont_bar(c, t):
    c.set_source_rgb(*hexc("6e4535"))
    c.paint()
    for i in range(12):
        line(c, [(i * 170, 0), (i * 170, 700)], f"pan{i}", 2, hexc("5c3a2c"), alpha=0.8)
    shape(c, rect(-20, 380, W + 40, 18), hexc("4f3024"), "shelf", lw=2.5)
    r = random.Random(2)
    for i in range(22):
        x = 60 + i * 84
        h = r.uniform(50, 90)
        col = [hexc("4f8a6b"), hexc("b5553f"), hexc("d9a441"), hexc("6a7fb0")][i % 4]
        shape(c, [(x, 380), (x, 380 - h * 0.6), (x + 8, 380 - h * 0.7), (x + 8, 380 - h), (x + 18, 380 - h),
                  (x + 18, 380 - h * 0.7), (x + 26, 380 - h * 0.6), (x + 26, 380)], col, f"btl{i}", lw=2.2)
    pts = [(x, 120 + 130 * math.sin(math.pi * x / W)) for x in range(-40, W + 80, 40)]
    line(c, pts, "lights", 2.4, hexc("2f1f18"))
    for i, (x, y) in enumerate(pts[1::2]):
        tw = 0.7 + 0.3 * math.sin(t * 8 + i * 1.7)
        glow(c, x, y + 14, 70, hexc("ffd27a"), 0.55 * tw)
        circle(c, x, y + 14, 9, hexc("fff0b8"), 0.95)
    shape(c, rect(-20, 820, W + 40, 300), hexc("5b382b"), "barfloor", lw=3)
    clink = ease_io(prog(t, 0.05, 0.55))
    seats = [(600, 0), (790, None), (1130, 1), (1320, 2)]
    tx, ty = 960, 560
    for i, (x, ci) in enumerate(seats):
        sway = math.sin(t * 6 + i) * 4
        side = -1 if x < 960 else 1
        far_hand = (side * -40, -72)
        mx = lerp(x - side * 50, tx + side * (24 + i % 2 * 18), clink)
        my = lerp(690, ty + (i % 2) * 16, clink)
        lx, ly = (mx - x - sway) / 1.4, (my - 750) / 1.4 - 52
        if ci is None:
            girl(c, x + sway, 750, 1.4, sit=True, look=-side * 0.5, legs=False, arms=[far_hand, (lx, ly)], pack=False)
        else:
            companion(c, ci, x + sway, 750, 1.4, sit=True, look=-side * 0.5, legs=False, arms=[far_hand, (lx, ly)])
    shape(c, ell(960, 760, 420, 70, 28), hexc("a8744f"), "table", lw=3.2)
    shape(c, rect(940, 820, 40, 120), hexc("7a4d33"), "tleg", lw=3)
    for i, (x, ci) in enumerate(seats):
        side = -1 if x < 960 else 1
        mx = lerp(x - side * 50, tx + side * (24 + i % 2 * 18), clink)
        my = lerp(690, ty + (i % 2) * 16, clink)
        mug(c, mx, my, 1.2, f"mug{i}", tilt=side * -0.25 * clink)
    if t > 0.55:
        u = prog(t, 0.55, 0.9)
        r = random.Random(7)
        for i in range(14):
            a = r.uniform(0, 2 * math.pi)
            d = 30 + 170 * ease_out(u)
            star(c, tx + math.cos(a) * d, ty - 20 + math.sin(a) * d * 0.7, 5 * (1 - u) + 1, 1 - u)
        glow(c, tx, ty - 20, 200, hexc("fff2c0"), 0.6 * (1 - u))


def mont_plateau(c, t):
    vgrad(c, 0, 760, [(0, hexc("5f9cd3")), (1, hexc("e2eff3"))])
    for i, (x, w, h) in enumerate(((250, 900, 520), (820, 760, 420), (1350, 1000, 600), (1880, 800, 480))):
        mountain(c, x - t * 12, 760, w, h, hexc("9fb3cb"), f"pm{i}")
    for i, (x, y, s) in enumerate(((300, 470, 1.4), (1100, 520, 1.2), (1700, 430, 1.1))):
        cloud(c, x + t * 30, y, s, f"pc{i}", a=0.85)
    shape(c, hill_pts(700, 30, 0.003, 0.5), hexc("a3b37a"), "pmid", lw=3)
    slope = [(-40, 1100), (-40, 1000), (600, 900), (1200, 760), (1960, 600), (1960, 1100)]
    shape(c, slope, hexc("c3c98b"), "slope", lw=3.2)

    def sy(x):
        if x < 600:
            return 1000 - 100 * (x + 40) / 640
        if x < 1200:
            return 900 - 140 * (x - 600) / 600
        return 760 - 160 * (x - 1200) / 760

    # 风马旗
    pts = [(x, 140 + 50 * math.sin(math.pi * x / W) + x * 0.12) for x in range(-20, W + 60, 60)]
    line(c, pts, "pfstr", 2.2)
    fcols = [hexc(h) for h in ("3f6fb5", "f3f1ea", "c9473b", "4f9a5c", "f0c04a")]
    for i, (x, y) in enumerate(pts[:-1]):
        fl = math.sin(t * 9 + i * 0.7) * 6
        shape(c, [(x + 4, y + 2), (x + 50, y + 4 + fl * 0.3), (x + 48 + fl, y + 56), (x + 2 + fl * 0.5, y + 52)],
              fcols[i % 5], f"pf{i}", lw=1.8, amp=0.6)
    climbers = [(1, 380), (2, 620), (0, 860)]
    for j, (ci, x0) in enumerate(climbers):
        x = x0 + t * 70
        companion(c, ci, x, sy(x) + 4, 1.0, look=1.0, walk=t * 7 + j)
    gx = 1420 + ease_out(prog(t, 0, 1.0)) * 120
    up = ease_back(prog(t, 0.9, 0.4))
    arms = None if up < 0.05 else [(-26 - 10 * up, -80 - 70 * up), (26 + 10 * up, -80 - 70 * up)]
    jump = -math.sin(math.pi * prog(t, 0.95, 0.4)) * 30
    girl(c, gx, sy(gx) + 4 + jump, 1.05, look=0.3 if up > 0.05 else 1.0, walk=t * 7 if up < 0.05 else None,
         arms=arms, look_up=0.5 * up)


def mont_sea(c, t, run=True, sun_y=470, dusk=0.0):
    sky = [(0, mix(hexc("f5a96c"), hexc("4e3f73"), dusk)), (0.55, mix(hexc("f7b27a"), hexc("b0698a"), dusk)),
           (1, mix(hexc("fcd892"), hexc("f0a284"), dusk))]
    vgrad(c, 0, 560, sky)
    if dusk > 0.4:
        sky_stars(c, t, 26, 40, 30, W - 40, 330, seed=8, a=(dusk - 0.4) / 0.6)
    if sun_y < 620:
        glow(c, 1450, sun_y, 330, hexc("fff0b8"), 0.7 * (1 - dusk * 0.7))
        circle(c, 1450, sun_y, 110, mix(hexc("fff2c4"), hexc("f7a35c"), dusk))
    for i, (x, y, w) in enumerate(((300, 240, 420), (900, 330, 360), (1700, 200, 300))):
        shape(c, ell(x + t * 10, y, w / 2, 14, 18), mix(hexc("fbd0b0"), hexc("c98aa0"), dusk), f"sk{i}", ink=False)
    vgrad(c, 560, 790, [(0, mix(hexc("e6907a"), hexc("7d6295"), dusk)), (1, mix(hexc("b8708a"), hexc("4a3d6a"), dusk))])
    r = random.Random(4)
    for i in range(50):
        yy = 570 + r.uniform(0, 210)
        xx = 1450 + r.uniform(-90, 90) * (1 + (yy - 560) / 90)
        ln = r.uniform(14, 44)
        a = (0.4 + 0.4 * math.sin(t * 5 + i)) * (1 - dusk * 0.6)
        c.move_to(xx - ln / 2 + math.sin(t * 2 + i) * 8, yy)
        c.rel_line_to(ln, 0)
        c.set_source_rgba(*hexc("ffe3b0"), a)
        c.set_line_width(2.6)
        c.stroke()
    shape(c, rect(-20, 780, W + 40, 320), mix(hexc("f2d3a8"), hexc("c9a59a"), dusk), "sand", lw=3)
    shape(c, rect(-20, 780, W + 40, 60), mix(hexc("d9b48f"), hexc("ae8b8e"), dusk), "wet", lw=2, ink=False)


def mont_sea_run(c, t):
    mont_sea(c, t)
    foam_y = 815 + 22 * math.sin(t * 3.2)
    pts = [(-20, 790)] + [(x, foam_y + 10 * math.sin(x * 0.01 + t * 4)) for x in range(-20, W + 60, 60)] + [(W + 20, 790)]
    shape(c, pts, (1, 1, 1, 0.5), "foam", lw=2.4, amp=1)
    xs = [300, 520, 760, 980]
    who = [1, None, 0, 2]
    for i, (x0, ci) in enumerate(zip(xs, who)):
        x = x0 + t * 300
        if ci is None:
            girl(c, x, 905, 1.0, look=1.0, walk=t * 15 + i, run=True)
        else:
            companion(c, ci, x, 905, 1.02, look=1.0, walk=t * 15 + i * 1.3, run=True)
        r = random.Random(int(t * 10) * 7 + i)
        for k in range(4):
            circle(c, x - 20 + r.uniform(-30, 10), 900 - r.uniform(0, 40), r.uniform(3, 6), (1, 1, 1), 0.85)


MONT = [mont_bike, mont_bar, mont_plateau, mont_sea_run]
MONT_LEN = 7.5 / 4


def s5(c, t):
    i = min(3, int(t / MONT_LEN))
    lt = t - i * MONT_LEN
    k = 1 + 0.05 * (1 - ease_out(prog(lt, 0, 0.35)))
    c.save()
    c.translate(960, 540)
    c.scale(k, k)
    c.translate(-960, -540)
    MONT[i](c, lt)
    c.restore()
    fl = 1 - ease_out(prog(lt, 0, 0.25))
    if i > 0 and fl > 0:
        c.set_source_rgba(1, 0.98, 0.9, 0.55 * fl)
        c.paint()


# ================================================================ 纸鸟飞走
BIRD_T = [0.4, 1.0, 1.6]
BIRD_DIR = [(-700, -620), (520, -700), (1100, -380)]


def s6(c, t):
    mont_sea(c, t, sun_y=560 + t * 14, dusk=0.55 + 0.35 * ease_io(t / 5))
    xs = [700, 1180, 1400]
    for i in range(3):
        t0 = BIRD_T[i]
        shrink = ease_in(prog(t, t0, 0.35))
        if shrink < 1:
            with popup(c, xs[i], 905 - 100, 1 - shrink, sx=1 - shrink * 0.6):
                companion(c, i, xs[i], 905, 1.05, look=-0.4 if xs[i] > 960 else 0.4, alpha=1 - shrink * 0.5)
        u = prog(t, t0 + 0.2, 2.6)
        if 0 < u < 1:
            dx, dy = BIRD_DIR[i]
            e = ease_in(u) * 0.7 + u * 0.3
            bx = xs[i] + dx * e + math.sin(u * 5) * 30
            by = 800 + dy * e - math.sin(u * math.pi) * 60
            ang = math.atan2(dy, dx) * 0.25
            sgn = 1 if dx > 0 else -1
            c.save()
            c.translate(bx, by)
            c.scale(sgn, 1)
            paper_bird(c, 0, 0, 1.4 * (1 - 0.6 * u), t * 13 + i, COMPANIONS[i]["coat"], ang * sgn, f"pb{i}")
            c.restore()
    look_up = ease_io(prog(t, 1.0, 1.0))
    girl(c, 960, 905, 1.1, look=-0.2, look_up=look_up)


# ================================================================ 回忆
def mini_scene(c, kind, w, h, t):
    if kind == 0:
        vgrad(c, 0, h, [(0, hexc("bfe0ec")), (1, hexc("fdf3dc"))], 0, w)
        c.rectangle(0, h * 0.7, w, h * 0.3)
        c.set_source_rgb(*hexc("bcd38f"))
        c.fill()
        for k, x in enumerate((40, 105)):
            c.arc(x - 16, h * 0.72, 12, 0, 2 * math.pi)
            c.arc(x + 16, h * 0.72, 12, 0, 2 * math.pi)
            c.set_source_rgba(*INK, 0.8)
            c.set_line_width(2)
            c.stroke()
            circle(c, x, h * 0.48, 9, [hexc("d1553f"), hexc("4f8a8b")][k])
    elif kind == 1:
        c.rectangle(0, 0, w, h)
        c.set_source_rgb(*hexc("6e4535"))
        c.fill()
        for k in range(5):
            glow(c, 15 + k * 30, 20 + 8 * math.sin(k), 18, hexc("ffd27a"), 0.8)
        for k, x in enumerate((50, 95)):
            c.rectangle(x - 10, h * 0.5, 20, 28)
            c.set_source_rgb(*hexc("f0b64a"))
            c.fill()
        star(c, 72, h * 0.45, 5, 1)
    elif kind == 2:
        vgrad(c, 0, h, [(0, hexc("5f9cd3")), (1, hexc("e2eff3"))], 0, w)
        c.move_to(0, h)
        c.line_to(50, h * 0.3)
        c.line_to(90, h * 0.6)
        c.line_to(120, h * 0.25)
        c.line_to(w, h)
        c.set_source_rgb(*hexc("9fb3cb"))
        c.fill()
        for k in range(6):
            c.rectangle(10 + k * 24, 18 + k * 3, 14, 14)
            c.set_source_rgb(*[hexc("3f6fb5"), hexc("f3f1ea"), hexc("c9473b"), hexc("4f9a5c"), hexc("f0c04a")][k % 5])
            c.fill()
    else:
        vgrad(c, 0, h * 0.6, [(0, hexc("f5a96c")), (1, hexc("fcd892"))], 0, w)
        circle(c, w * 0.68, h * 0.58, 24, hexc("fff2c4"))
        c.rectangle(0, h * 0.6, w, h * 0.4)
        c.set_source_rgb(*hexc("b8708a"))
        c.fill()
        for k in range(3):
            circle(c, 30 + k * 26, h * 0.62, 6, INK, 0.8)


def s7(c, t):
    room(c, t + 40, "s7", dim=0.5)
    glow(c, 960, 520, 700, hexc("ffd98a"), 0.18)
    sky_stars(c, t, 18, 100, 60, 1800, 500, seed=21, a=0.5)
    girl(c, 960, 880, 1.25, sit=True, pack=False, hat=False, look=0.0, look_up=0.7 + 0.2 * math.sin(t),
         walk=t * 1.3)
    r = random.Random(13)
    for i in range(30):
        x = (r.uniform(0, W) + math.sin(t * 0.7 + i) * 60) % W
        y = r.uniform(150, 950) + math.cos(t * 0.9 + i * 2) * 40
        tw = 0.5 + 0.5 * math.sin(t * 3 + i)
        glow(c, x, y, 18, hexc("fff0a0"), 0.6 * tw)
        circle(c, x, y, 2.5, hexc("fffbe0"), tw)
    cards = []
    for i in range(4):
        a = t * 0.32 + i * math.pi / 2 + 0.4
        x = 960 + math.cos(a) * 520
        y = 520 + math.sin(a) * 170
        depth = math.sin(a)
        cards.append((depth, i, x, y))
    for depth, i, x, y in sorted(cards):
        k = ease_back(prog(t, 0.2 + i * 0.25, 0.5))
        if k < 0.01:
            continue
        s = (0.85 + 0.2 * depth) * k
        glow(c, x, y, 190 * s, hexc("ffd98a"), 0.55)
        c.save()
        c.translate(x, y)
        c.rotate(math.sin(t * 0.8 + i) * 0.12)
        c.scale(s, s)
        shape(c, rect(-85, -100, 170, 200), hexc("fbf5e8"), f"card{i}", lw=2.6)
        c.save()
        c.translate(-75, -90)
        c.rectangle(0, 0, 150, 140)
        c.clip()
        mini_scene(c, i, 150, 140, t)
        c.restore()
        shape(c, rect(-75, -90, 150, 140), None, f"cardin{i}", lw=2)
        c.restore()


# ================================================================ 博物馆
def starry(c, x0, y0, w, h, t):
    c.save()
    c.rectangle(x0, y0, w, h)
    c.clip()
    vgrad(c, y0, y0 + h, [(0, hexc("2c4a86")), (1, hexc("4d6fae"))], x0, x0 + w)
    for k in range(7):
        cx = x0 + w * (0.15 + 0.13 * k)
        cy = y0 + h * (0.25 + 0.12 * math.sin(k * 1.7))
        pts = []
        for j in range(40):
            a = j * 0.4 + t * 0.6
            rr = 6 + j * 1.4
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.7))
        line(c, pts, f"sw{k}", 3.0, hexc("a8c4ea"), alpha=0.8)
    for k in range(9):
        sx = x0 + w * (0.08 + 0.11 * k)
        sy = y0 + h * (0.12 + 0.2 * ((k * 37) % 5) / 5)
        glow(c, sx, sy, 40, hexc("fbe08a"), 0.7)
        circle(c, sx, sy, 9, hexc("fbe08a"))
    shape(c, hill_pts(y0 + h * 0.78, 30, 0.01, 1, x0 - 10, x0 + w + 10, y0 + h + 10), hexc("2d3f5c"), "shill", lw=2.5)
    shape(c, [(x0 + w * 0.2, y0 + h + 10), (x0 + w * 0.2 - 30, y0 + h * 0.3), (x0 + w * 0.2 + 10, y0 + h * 0.15),
              (x0 + w * 0.2 + 34, y0 + h + 10)], hexc("1f2b3a"), "cypress", lw=2.5)
    c.restore()


def museum(c, t, cam_x=0.0, him_alpha=0.65, show_girl=True):
    c.save()
    c.translate(-cam_x, 0)
    c.set_source_rgb(*hexc("e6e1d1"))
    c.rectangle(-40, -40, 2600, 1200)
    c.fill()
    for i in range(16):
        line(c, [(i * 170, 0), (i * 170, 820)], f"mwl{i}", 1.6, hexc("d6d0bd"), alpha=0.6)
    for i, x in enumerate((1150, 2250)):
        shape(c, [(x - 90, 520), (x - 90, 180), (x, 110), (x + 90, 180), (x + 90, 520)], hexc("f6f1e0"), f"arch{i}", lw=3)
        c.move_to(x - 90, 180)
        c.line_to(x + 90, 180)
        c.line_to(x + 330, 1080)
        c.line_to(x - 60, 1080)
        c.close_path()
        c.set_source_rgba(1, 0.98, 0.9, 0.22)
        c.fill()
    shape(c, rect(150, 110, 800, 540), hexc("6a4a33"), "pframe", lw=3.4)
    starry(c, 180, 140, 740, 480, t)
    shape(c, rect(180, 140, 740, 480), None, "pin", lw=2.5)
    shape(c, rect(1700, 210, 520, 330), hexc("b48a4f"), "p2f", lw=3)
    c.save()
    c.rectangle(1722, 232, 476, 286)
    c.clip()
    vgrad(c, 232, 518, [(0, hexc("f2d7a6")), (1, hexc("e7b98a"))], 1722, 2198)
    shape(c, hill_pts(440, 30, 0.01, 2, 1700, 2220, 540), hexc("9fb07a"), "p2h", lw=2.5)
    c.restore()
    shape(c, rect(-40, 820, 2640, 300), hexc("cdb894"), "mfloor", lw=3)
    for i in range(30):
        line(c, [(i * 100 - 300, 1080), (i * 100 - 300 + 300, 820)], f"tile{i}", 1.5, hexc("b8a27c"), alpha=0.6)
    for x in (1000, 1300):
        shape(c, rect(x - 6, 720, 12, 110), hexc("8c6f4a"), f"rp{x}", lw=2.4)
        circle(c, x, 716, 10, hexc("c9a050"))
    line(c, [(1000, 740), (1150, 790), (1300, 740)], "rope", 5, hexc("a8423a"))
    shape(c, rect(1090, 560, 120, 270), hexc("efe9da"), "ped", lw=3)
    vase = [(1120, 560), (1110, 500), (1090, 460), (1100, 410), (1125, 390), (1118, 370), (1182, 370), (1175, 390),
            (1200, 410), (1210, 460), (1190, 500), (1180, 560)]
    shape(c, vase, hexc("c47a4a"), "vase", lw=3)
    line(c, [(1095, 440), (1205, 440)], "vb1", 3, INK, alpha=0.6)
    line(c, [(1100, 470), (1200, 470)], "vb2", 3, INK, alpha=0.6)
    if show_girl:
        girl(c, 560, 900, 1.15, view="back", head_down=-3)
    shape(c, rect(1760, 760, 460, 22), hexc("8c5a3c"), "mbench", lw=3)
    for x in (1790, 2170):
        shape(c, rect(x, 782, 16, 70), hexc("6b4430"), f"mbl{x}", lw=2.4)
    if him_alpha > 0.01:
        ghost_person(c, 1990, 772, 1.2, alpha=him_alpha, sit=True, look=0.4, head_down=8,
                     arms=[(-8, -86), (8, -86)])
        glow(c, 1990, 772 - 52 * 1.2 - 34 * 1.2 + 52 * 1.2 - 30, 60, hexc("cfe3ff"), 0.6 * him_alpha)
        shape(c, rrect(1980, 772 - 54, 22, 14, 3), hexc("dfeaff"), "phone", lw=2, alpha=him_alpha)
    c.restore()


def s8(c, t):
    cam = 600 * ease_io(prog(t, 0.6, 3.6))
    museum(c, t, cam_x=cam)


def s9(c, t):
    c.set_source_rgb(*hexc("d3d8db"))
    c.paint()
    shape(c, rect(170, 140, 420, 420), hexc("eef0ee"), "win9", lw=3.5)
    c.save()
    c.rectangle(185, 155, 390, 390)
    c.clip()
    vgrad(c, 155, 545, [(0, hexc("b9c3cc")), (1, hexc("e1e2dc"))])
    for k, (x0, y0, x1, y1) in enumerate(((240, 545, 320, 300), (320, 300, 260, 200), (320, 300, 420, 230),
                                          (420, 230, 500, 180), (300, 400, 200, 340))):
        line(c, [(x0, y0), (x1, y1)], f"br{k}", 7 - k * 0.8, hexc("5b4a42"))
    c.restore()
    line(c, [(380, 140), (380, 560)], "wm", 6, hexc("cfd2cf"))
    shape(c, rect(-20, 820, W + 40, 300), hexc("b8ad9c"), "f9", lw=3)
    bx0, bx1 = 640, 1500
    shape(c, rect(bx0, 560, bx1 - bx0, 30), hexc("8c5a3c"), "b9b1", lw=3.2)
    shape(c, rect(bx0, 610, bx1 - bx0, 30), hexc("8c5a3c"), "b9b2", lw=3.2)
    shape(c, rect(bx0 - 20, 700, bx1 - bx0 + 40, 34), hexc("9b6646"), "b9s", lw=3.2)
    for x in (bx0 + 20, bx1 - 40):
        shape(c, rect(x, 590, 22, 120), hexc("6b4430"), f"b9u{x}", lw=2.6)
        shape(c, rect(x, 734, 22, 120), hexc("6b4430"), f"b9l{x}", lw=2.6)
    fade = 1 - ease_io(prog(t, 0.2, 1.4))
    if fade > 0:
        ghost_person(c, 1180, 704, 1.7, alpha=0.6 * fade, sit=True, look=0.4, head_down=10, arms=[(-8, -86), (8, -86)])
        r = random.Random(5)
        for i in range(40):
            u = prog(t, 0.2 + r.uniform(0, 0.8), 1.6)
            if 0 < u < 1:
                x = 1180 + r.uniform(-60, 60) + u * r.uniform(40, 160)
                y = 704 - r.uniform(0, 300) - u * 120
                circle(c, x, y, 3, hexc("a9b2c2"), 0.6 * (1 - u))
    wind = prog(t, 1.4, 3.3)
    if wind > 0:
        for i in range(7):
            ph = (t * 1.3 + i * 0.37) % 1.0
            x = -300 + ph * 2500
            y = 300 + i * 80 + math.sin(i) * 30
            pts = [(x + k * 40, y + math.sin(k * 0.6 + t * 3 + i) * 14) for k in range(8)]
            line(c, pts, f"w9{i}", 2.4, hexc("8f99a6"), alpha=0.55 * math.sin(math.pi * clamp(wind * 1.4)))
        r = random.Random(8)
        for i in range(10):
            u = (t * 0.35 + r.uniform(0, 1)) % 1.0
            x = -100 + u * 2200
            y = r.uniform(250, 800) + math.sin(u * 12 + i) * 40
            c.save()
            c.translate(x, y)
            c.rotate(u * 14 + i)
            shape(c, ell(0, 0, 13, 6, 10), [hexc("d9893f"), hexc("c9553f"), hexc("e8b94a")][i % 3], f"lf{i}", lw=1.6, amp=0.5)
            c.restore()
    u = ease_in(prog(t, 1.9, 2.9)) * 0.8 + prog(t, 1.9, 2.9) * 0.2
    nx = 960 + u * 1300
    ny = 690 - math.sin(clamp(u * 1.4) * math.pi * 0.9) * 330 - u * 120
    rot = u * 7 if u > 0 else -0.05
    unfold = math.sin(math.pi * clamp((u - 0.05) / 0.45)) if 0.05 < u < 0.5 else 0.0
    sc = 1 + 1.4 * unfold
    c.save()
    c.translate(nx, ny)
    c.rotate(rot * (1 - unfold))
    c.scale(sc, sc * (0.55 + 0.45 * math.cos(u * 18) if unfold < 0.3 else 1))
    nw, nh = 70 + 50 * unfold, 44 + 4 * unfold
    shape(c, rect(-nw / 2, -nh / 2, nw, nh), hexc("fbf6e9"), "note", lw=2.2 / sc, amp=0.6)
    if unfold > 0.35:
        text(c, "万事向前看", 0, 6, 15, INK, a=clamp((unfold - 0.35) * 3))
    else:
        for k in range(3):
            line(c, [(-nw / 2 + 10, -8 + k * 8), (nw / 2 - 12 - k * 8, -8 + k * 8)], f"nl{k}", 1.4, INK, alpha=0.5, amp=0.4)
    c.restore()


# ================================================================ 吾乡
def s10(c, t):
    hz = 560
    vgrad(c, 0, hz, [(0, hexc("2d3463")), (0.35, hexc("7b4673")), (0.62, hexc("e06b78")), (0.85, hexc("f7a45c")),
                     (1, hexc("fdd48a"))])
    sky_stars(c, t, 16, 60, 20, W - 60, 200, seed=31, a=0.7)
    for i, (x, y, w) in enumerate(((260, 330, 520), (1000, 380, 460), (1650, 300, 420), (600, 450, 380))):
        shape(c, ell(x + t * 8, y, w / 2, 12, 20), hexc("f5a98d"), f"st{i}", ink=False, alpha=0.8)
    sy = hz + 8 + t * 9
    glow(c, 960, sy, 520, hexc("ffdd99"), 0.75)
    circle(c, 960, sy, 150, hexc("fff0c8"))
    vgrad(c, hz, 800, [(0, hexc("e7837a")), (0.5, hexc("a35e86")), (1, hexc("4c3f6e"))])
    r = random.Random(2)
    for i in range(80):
        yy = hz + 6 + r.uniform(0, 240) ** 1.0
        spread = 140 * (1 + (yy - hz) / 80)
        xx = 960 + r.gauss(0, spread * 0.4)
        ln = r.uniform(16, 60)
        a = 0.35 + 0.45 * math.sin(t * 4 + i * 1.3)
        c.move_to(xx - ln / 2 + math.sin(t * 1.5 + i) * 10, yy)
        c.rel_line_to(ln, 0)
        c.set_source_rgba(*hexc("ffe6b5"), a)
        c.set_line_width(2.6)
        c.stroke()
    for i in range(3):
        bx = 500 + i * 60 + t * 25
        by = 250 + i * 22 + math.sin(t * 2 + i) * 5
        fl = math.sin(t * 8 + i)
        line(c, [(bx - 12, by - 5 * fl), (bx, by), (bx + 12, by - 5 * fl)], f"bd{i}", 2.2, hexc("3a2c48"))
    shape(c, rect(-20, 790, W + 40, 320), hexc("cf9f8a"), "s10sand", lw=3)
    shape(c, rect(-20, 790, W + 40, 70), hexc("b98584"), "s10wet", ink=False)
    girl(c, 960, 905, 1.1, view="back")
    fy = 880 + 26 * math.sin(t * 1.5 - 0.5)
    pts = [(-20, 790)] + [(x, fy + 8 * math.sin(x * 0.012 + t * 2)) for x in range(-20, W + 60, 50)] + [(W + 20, 790)]
    shape(c, pts, (0.96, 0.85, 0.85, 0.45), "foam10", lw=2.4)
    line(c, pts[1:-1], "foam10b", 3, (1, 0.97, 0.94), alpha=0.85)


# ================================================================ 继续走
def s11(c, t):
    hz = 560
    vgrad(c, 0, hz, [(0, hexc("98c3e2")), (0.7, hexc("f6dcb4")), (1, hexc("fbe6c0"))])
    glow(c, 960, hz, 520, hexc("fff2c6"), 0.7)
    for i, (x, y, s) in enumerate(((330, 170, 1.0), (1500, 130, 0.9), (1000, 260, 0.6))):
        cloud(c, x + t * 12, y, s, f"c11{i}")
    pops = [
        (0.5, lambda: [mountain(c, x, hz, w, h, hexc("a9b4d0"), f"m11{i}") for i, (x, w, h) in
                       enumerate(((260, 520, 260), (560, 440, 190)))]),
        (1.1, lambda: [house(c, x, hz, w, h, hexc(wc), hexc(rc), f"h11{i}", rt, door=False) for i, (x, w, h, wc, rc, rt) in
                       enumerate(((1250, 70, 120, "e9d3b5", "b4533f", "tri"), (1330, 60, 170, "dcd2c2", "6e7a9a", "flat"),
                                  (1400, 80, 100, "f0dcb8", "3c6ea5", "dome"), (1490, 60, 140, "e3c5aa", "8b4a3a", "tri")))]),
        (1.8, lambda: (shape(c, [(1740, hz), (1752, hz - 170), (1778, hz - 170), (1790, hz)], hexc("f4efe6"), "lh", lw=3),
                       shape(c, rect(1748, hz - 200, 34, 30), hexc("d1553f"), "lhtop", lw=3),
                       glow(c, 1765, hz - 186, 90, hexc("fff0b0"), 0.6 + 0.3 * math.sin(t * 5)))),
        (2.6, lambda: (shape(c, rect(760, hz - 120, 10, 120), hexc("8a5a3a"), "wm1", lw=2.4),
                       [shape(c, [(765, hz - 120), (765 + math.cos(t * 2 + k * 1.57) * 60, hz - 120 + math.sin(t * 2 + k * 1.57) * 60),
                                  (765 + math.cos(t * 2 + k * 1.57 + 0.25) * 60, hz - 120 + math.sin(t * 2 + k * 1.57 + 0.25) * 60)],
                              hexc("f5efe2"), f"wb{k}", lw=2) for k in range(4)])),
    ]
    for t0, fn in pops:
        k = ease_back(prog(t, t0, 0.5))
        if k > 0.01:
            with popup(c, 960, hz, k):
                fn()
    bu = prog(t, 2.0, 3.0)
    if bu > 0:
        bx, by = 620 + bu * 40, hz - 40 - ease_out(bu) * 300
        c.save()
        c.rectangle(0, 0, W, hz)
        c.clip()
        shape(c, ell(bx, by - 60, 50, 58, 18), hexc("e07a5f"), "bal", lw=2.6)
        shape(c, [(bx - 30, by - 30), (bx + 30, by - 30), (bx, by + 4)], hexc("f0b84a"), "bal2", ink=False, alpha=0.8)
        line(c, [(bx - 20, by - 10), (bx - 10, by + 14)], "rope1", 1.6)
        line(c, [(bx + 20, by - 10), (bx + 10, by + 14)], "rope2", 1.6)
        shape(c, rect(bx - 12, by + 14, 24, 16), hexc("8a5a3a"), "bask", lw=2)
        c.restore()
    shape(c, [(-20, hz), (W + 20, hz), (W + 20, 1100), (-20, 1100)], hexc("b9cc8e"), "field", lw=3)
    for i in range(-12, 13):
        line(c, [(960 + i * 8, hz + 2), (960 + i * 260, 1100)], f"crop{i}", 2, hexc("9db574"), alpha=0.7)
    shape(c, [(940, hz), (980, hz), (1260, 1100), (660, 1100)], hexc("ead6a8"), "road11", lw=3)
    for k in range(10):
        z0 = (k + (t * 0.9) % 1) / 10
        z1 = z0 + 0.04
        y0 = hz + (1100 - hz) * z0 ** 2
        y1 = hz + (1100 - hz) * z1 ** 2
        c.move_to(960, y0)
        c.line_to(960, y1)
        c.set_source_rgba(1, 0.98, 0.92, 0.85)
        c.set_line_width(1 + 10 * z0)
        c.stroke()
    r = random.Random(17)
    for i in range(60):
        side = 1 if i % 2 else -1
        z = r.uniform(0.05, 1.0)
        y = hz + (1100 - hz) * z ** 2
        x = 960 + side * (40 + (300 + r.uniform(0, 600)) * z)
        circle(c, x, y, 2 + 6 * z, [hexc("f2a6a0"), hexc("fbe29a"), hexc("ffffff"), hexc("c9a0dc")][i % 4], 0.95)
    u = ease_io(prog(t, 0.0, 5.2))
    gy = lerp(1010, 680, u)
    s = 1.25 * (gy - hz) / (1010 - hz)
    girl(c, 960, gy, s, view="back", walk=t * 7.5)


# ================================================================ 合书 + 印章
_S11_END = {}


def s11_still():
    if "surf" not in _S11_END:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(52.5 + 5.0)
        s11(cc, 5.0)
        _S11_END["surf"] = surf
    return _S11_END["surf"]


def cover(c, x, y, w, h, key="cv"):
    shape(c, rect(x, y, w, h), hexc("2c3b5e") + (1.0,), key, lw=3)
    gold = hexc("d9b46a")
    shape(c, rect(x + 22, y + 22, w - 44, h - 44), None, key + "b1", lw=2)
    with ink_style(gold):
        shape(c, rect(x + 22, y + 22, w - 44, h - 44), None, key + "b2", lw=2.4)
        shape(c, rect(x + 32, y + 32, w - 64, h - 64), None, key + "b3", lw=1.4)
    text(c, "此心安处", x + w / 2, y + h * 0.36, 62, gold)
    cx, cy = x + w / 2, y + h * 0.62
    c.new_path()
    c.arc(cx + 70, cy - 40, 26, 0, 2 * math.pi)
    c.set_source_rgba(*gold, 0.9)
    c.set_line_width(2.4)
    c.stroke()
    with ink_style(gold):
        line(c, [(cx - 160, cy + 40), (cx - 100, cy + 30), (cx - 40, cy + 42), (cx + 20, cy + 32), (cx + 80, cy + 42),
                 (cx + 160, cy + 34)], key + "wave", 2.4, gold)
    c.push_group()
    person(c, cx - 40, cy + 36, 0.42, view="back", key="cvg")
    pat = c.pop_group()
    c.set_source_rgba(*gold, 1)
    c.mask(pat)


def seal(c, x, y, s, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    red = hexc("b8322a")
    spath(c, wob(rect(-55, -55, 110, 110), "seal", 2.2, 20, static=True), True)
    c.set_source_rgba(*red, 0.94 * a)
    c.fill()
    c.select_font_face(FONT_FACE)
    c.set_source_rgba(*hexc("f6ead6"), a)
    c.set_font_size(46)
    for ch, (tx, ty) in (("藤", (6, -6)), ("原", (6, 44))):
        c.move_to(tx, ty)
        c.show_text(ch)
    c.save()
    c.translate(-48, -6)
    c.scale(1.0, 2.1)
    c.set_font_size(46)
    c.move_to(0, 22)
    c.show_text("樹")
    c.restore()
    c.rectangle(-45, -47, 92, 94)
    c.set_line_width(2.5)
    c.stroke()
    r = random.Random(42)
    for i in range(60):
        circle(c, r.uniform(-55, 55), r.uniform(-55, 55), r.uniform(0.8, 2.6), hexc("f2e6d0"), 0.7 * a)
    c.restore()


def s12(c, t):
    c.set_source_rgb(*hexc("7e5236"))
    c.paint()
    for i in range(30):
        y = i * 38
        pts = [(x, y + 8 * math.sin(x * 0.004 + i)) for x in range(-40, W + 80, 80)]
        line(c, pts, f"grain{i}", 2, hexc("6a442c"), alpha=0.6, amp=2)
    glow(c, 960, 520, 1100, hexc("ffd8a0"), 0.3)
    pw, ph = 680, 382.5
    bx, by = 960, 540 - ph / 2
    zoom = ease_io(prog(t, 0.0, 1.3))
    close = ease_io(prog(t, 1.5, 1.1))
    pan = ease_io(prog(t, 2.6, 0.8))
    shake = 0.0
    if t > 3.3:
        shake = 6 * math.exp(-(t - 3.3) * 12) * math.sin((t - 3.3) * 60)
    c.save()
    k = 1 + 0.12 * pan
    c.translate(960, 540)
    c.scale(k, k)
    c.translate(-960 - pan * 340, -540 + shake)
    # 书影与书页
    lw_sh = (pw + 18) * max(0.0, math.cos(close * math.pi))
    c.rectangle(bx - lw_sh + 14, by - 18 + 22, lw_sh + pw + 18, ph + 36)
    c.set_source_rgba(0, 0, 0, 0.3)
    c.fill()
    left_vis = close < 0.5
    if close < 0.5:
        lwid = (pw + 18) * math.cos(close * math.pi)
        shape(c, rect(bx - lwid, by - 18, lwid, ph + 36), hexc("2c3b5e"), "bcl", lw=3)
    shape(c, rect(bx, by - 18, pw + 18, ph + 36), hexc("2c3b5e"), "bcr", lw=3)
    for k2 in range(3):
        line(c, [(bx + 4, by + ph + 4 + k2 * 4), (bx + pw - 4, by + ph + 4 + k2 * 4)], f"pg{k2}", 1.2, hexc("cdbfa5"))
    # 右页：最后一幕画面
    c.save()
    c.rectangle(bx, by, pw, ph)
    c.clip()
    c.translate(bx, by)
    c.scale(pw / W, ph / H)
    c.set_source_surface(s11_still(), 0, 0)
    c.paint()
    c.restore()
    shade = cairo.LinearGradient(bx, 0, bx + 60, 0)
    shade.add_color_stop_rgba(0, 0, 0, 0, 0.25)
    shade.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(shade)
    c.rectangle(bx, by, 60, ph)
    c.fill()

    def left_page_content():
        c.set_source_rgb(*hexc("f6eedd"))
        c.rectangle(bx - pw, by, pw, ph)
        c.fill()
        lines = ["一直知道，一个人旅行并不浪漫。", "世界太大了，", "人生也不一定只有一种活法。", "",
                 "此心安处是吾乡。", "", "继续一个人，看这个世界。"]
        for i, s in enumerate(lines):
            text(c, s, bx - pw + 70, by + 70 + i * 44, 26, INK, a=0.85, anchor="l")

    if left_vis:
        th = close * math.pi
        wv = math.cos(th)
        c.save()
        c.translate(bx, 0)
        c.scale(max(wv, 0.001), 1)
        c.translate(-bx, 0)
        left_page_content()
        c.restore()
        c.set_source_rgba(0, 0, 0, 0.25 * close * 2)
        c.rectangle(bx - pw * wv, by, pw * wv, ph)
        c.fill()
    else:
        th = close * math.pi
        wv = -math.cos(th)
        c.set_source_rgba(0, 0, 0, 0.3 * (1 - close))
        c.rectangle(bx, by, pw, ph)
        c.fill()
        c.save()
        c.translate(bx, 0)
        c.scale(max(wv, 0.001), 1)
        c.translate(-bx, 0)
        cover(c, bx - 18, by - 18, pw + 36, ph + 36)
        c.restore()
    # 印章
    st = prog(t, 3.0, 0.3)
    if st > 0:
        sc = lerp(2.2, 1.0, ease_in(st))
        cx, cy = bx + pw - 80, by + ph - 70
        if st >= 1:
            ring = prog(t, 3.3, 0.5)
            c.arc(cx, cy, 70 + 60 * ring, 0, 2 * math.pi)
            c.set_source_rgba(*hexc("b8322a"), 0.35 * (1 - ring))
            c.set_line_width(3)
            c.stroke()
        seal(c, cx, cy, 0.95 * sc, a=ease_io(st * 1.5))
    c.restore()
    na = ease_io(prog(t, 3.6, 0.8))
    if na > 0:
        text(c, "— 藤原樹 —", 960, 985, 44, hexc("f4e6cc"), a=na)


SCENES = [(0, 5, s1), (5, 10, s2), (10, 15, s3), (15, 20, s4), (20, 27.5, s5), (27.5, 32.5, s6),
          (32.5, 37.5, s7), (37.5, 42.5, s8), (42.5, 47.5, s9), (47.5, 52.5, s10), (52.5, 57.5, s11),
          (57.5, 62.5, s12)]
# (时间, 类型)：page = 翻页，fade = 叠化
TRANSITIONS = [(5, "page"), (10, "page"), (15, "page"), (20, "page"), (32.5, "page"),
               (37.5, "page"), (42.5, "page"), (47.5, "page"), (52.5, "page")]

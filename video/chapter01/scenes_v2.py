"""第一章 · 出逃（第二版）—— 新增与重做的镜头。"""
import math
import random

import cairo

from scenes import (WATER, GROUND, city_row, floor_roots, platform_bg, rain_cloud, room, s24_badge, s25_redraw,
                    silhouette, street_bg, water, intro, s01_loop, s03_tide, s04_roots)
from draw import *  # noqa: F401,F403
from engine import book_outro

RED = hexc("d9534a")


# ================================================================ 锚点地图
MAP_X, MAP_Y, MAP_W, MAP_H = 60, 470, 400, 300
# (x, y, 类型, 颜色) —— 相对地图的 0..1 坐标
PINS = [
    (0.22, 0.30, "snow", "3f6fb5"), (0.78, 0.36, "wave", "2f7f8a"), (0.30, 0.74, "sun", "e0a33a"),
    (0.70, 0.72, "leaf", "4f9a5c"), (0.50, 0.52, "anchor", "c9473b"), (0.12, 0.55, "pin", "e8b94a"),
    (0.40, 0.20, "flag", "c9473b"), (0.62, 0.18, "pin", "c9473b"), (0.88, 0.58, "flag", "3f6fb5"),
    (0.52, 0.86, "circle", "c9473b"), (0.08, 0.86, "pin", "c9473b"),
]
STRINGS = [(5, 0), (0, 6), (6, 7), (7, 1), (1, 8), (8, 3), (3, 9), (9, 2), (2, 10)]
ORDER = [4, 0, 1, 2, 3, 6, 7, 8, 9, 5, 10]          # 亮起顺序：船锚先


def _pin_xy(i):
    fx, fy = PINS[i][0], PINS[i][1]
    return MAP_X + 18 + fx * (MAP_W - 36), MAP_Y + 18 + fy * (MAP_H - 36)


def _icon(c, kind, x, y, s=1.0):
    if kind == "snow":
        for k in range(3):
            a = k * math.pi / 3
            line(c, [(x - math.cos(a) * 9 * s, y - math.sin(a) * 9 * s), (x + math.cos(a) * 9 * s, y + math.sin(a) * 9 * s)],
                 f"ic_s{k}", 2.0, hexc("3f6fb5"))
    elif kind == "wave":
        line(c, [(x - 12 * s, y), (x - 6 * s, y - 5 * s), (x, y), (x + 6 * s, y - 5 * s), (x + 12 * s, y)], "ic_w", 2.2, hexc("2f7f8a"))
    elif kind == "sun":
        circle(c, x, y, 6 * s, hexc("e0a33a"))
        for k in range(8):
            a = k * math.pi / 4
            line(c, [(x + math.cos(a) * 9 * s, y + math.sin(a) * 9 * s), (x + math.cos(a) * 13 * s, y + math.sin(a) * 13 * s)],
                 f"ic_r{k}", 1.6, hexc("e0a33a"))
    elif kind == "leaf":
        shape(c, ell(x, y, 11 * s, 6 * s, 10), hexc("4f9a5c"), "ic_l", lw=1.4, amp=0.3)
        line(c, [(x - 10 * s, y), (x + 10 * s, y)], "ic_lm", 1.2, hexc("2f6a3c"))


def anchor_pin(c, x, y, s=1.0, col=hexc("c9473b")):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    line(c, [(0, -14), (0, 12)], "anc1", 3, col)
    line(c, [(-7, -8), (7, -8)], "anc2", 2.6, col)
    c.new_path()
    c.arc(0, -17, 4, 0, 2 * math.pi)
    c.set_source_rgba(*G(col)[:3], 1)
    c.set_line_width(2.4)
    c.stroke()
    line(c, [(-12, 4), (-9, 11), (0, 13), (9, 11), (12, 4)], "anc3", 2.8, col)
    c.restore()


def anchor_map(c, t, dust=0.0, anchor_glow=0.0, lit=0.0, taut=0.0):
    """dust：灰尘与松垂；anchor_glow：船锚亮起；lit：0..1 其余锚点依次亮起；taut：红线绷紧。"""
    x0, y0, w, h = MAP_X, MAP_Y, MAP_W, MAP_H
    paper = mix(hexc("efe2c2"), hexc("cdbf9f"), dust * 0.6)
    shape(c, [(x0, y0 + 6), (x0 + w, y0), (x0 + w + 6, y0 + h), (x0 + 4, y0 + h + 4)], paper, "amap", lw=3)
    for k in (0, 1):
        c.save()
        c.translate(x0 + (8 if k == 0 else w - 4), y0 + 4)
        c.rotate(-0.6 if k == 0 else 0.6)
        shape(c, rect(-22, -9, 44, 18), (0.96, 0.94, 0.86, 0.75), f"tape{k}", ink=False)
        c.restore()
    c.save()
    c.rectangle(x0 + 6, y0 + 8, w - 10, h - 10)
    c.clip()
    for k in range(1, 5):
        line(c, [(x0, y0 + k * h / 5), (x0 + w, y0 + k * h / 5)], f"lat{k}", 1.0, hexc("b8a882"), alpha=0.5)
        line(c, [(x0 + k * w / 5, y0), (x0 + k * w / 5, y0 + h)], f"lon{k}", 1.0, hexc("b8a882"), alpha=0.5)
    land = hexc("c9d1a0")
    for k, (cx, cy, rx, ry) in enumerate(((0.22, 0.32, 0.16, 0.16), (0.55, 0.28, 0.2, 0.13), (0.3, 0.72, 0.12, 0.17),
                                          (0.72, 0.68, 0.14, 0.14), (0.88, 0.3, 0.07, 0.1))):
        r = random.Random(k)
        pts = []
        for j in range(12):
            a = j * math.pi / 6
            rr = 1 + r.uniform(-0.3, 0.3)
            pts.append((x0 + cx * w + math.cos(a) * rx * w * rr, y0 + cy * h + math.sin(a) * ry * h * rr))
        shape(c, pts, land, f"land{k}", lw=1.8, amp=0.8)
    for k in range(7):
        r = random.Random(30 + k)
        wx, wy = x0 + r.uniform(0.05, 0.95) * w, y0 + r.uniform(0.1, 0.95) * h
        line(c, [(wx, wy), (wx + 5, wy - 3), (wx + 10, wy)], f"mw{k}", 1.2, hexc("8fa9b8"), alpha=0.8)
    c.restore()
    # 指南针
    cx, cy = x0 + w - 40, y0 + h - 38
    shape(c, ell(cx, cy, 22, 22, 14), None, "cmp", lw=1.6)
    shape(c, [(cx, cy - 20), (cx + 5, cy), (cx, cy + 20), (cx - 5, cy)], hexc("c9473b"), "cmpn", lw=1.2, amp=0.3)
    # 红线
    for k, (i, j) in enumerate(STRINGS):
        ax, ay = _pin_xy(i)
        bx, by = _pin_xy(j)
        sag = 26 * (1 - taut) * (0.5 + dust * 0.5)
        mx, my = (ax + bx) / 2, (ay + by) / 2 + sag
        on = clamp(lit * len(ORDER) - ORDER.index(j)) if lit > 0 else 0
        col = mix(hexc("b5473c"), hexc("ff6a4a"), on)
        if on > 0:
            with grade(sat=1.0):
                line(c, [(ax, ay), (mx, my), (bx, by)], f"str{k}g", 5, hexc("ffb38a"), alpha=0.35 * on)
        with grade(sat=lerp(GRADE["sat"], 1.0, on)):
            line(c, [(ax, ay), (mx, my), (bx, by)], f"str{k}", 1.8, col, alpha=0.9)
    # 便利贴、拍立得、车票
    note_rot = lerp(0.5, 0.05, taut) if dust > 0 or taut > 0 else 0.05
    for k, (nx, ny, rot, col, doodle) in enumerate(((x0 + 300, y0 + 210, note_rot, "f6e27a", "mtn"),
                                                    (x0 + 40, y0 + 120, -0.12, "f2b8c6", "camel"))):
        c.save()
        c.translate(nx, ny)
        c.rotate(rot)
        shape(c, rect(-30, -26, 60, 52), hexc(col), f"note{k}", lw=1.8, amp=0.5)
        if doodle == "mtn":
            line(c, [(-20, 12), (-6, -10), (4, 4), (12, -6), (22, 12)], "nd1", 1.6)
        else:
            line(c, [(-18, 10), (-12, -2), (-4, -6), (4, 2), (10, -8), (18, 10)], "nd2", 1.6)
        c.restore()
    pc = clamp(lit * 1.5)
    c.save()
    c.translate(x0 + w - 20, y0 + 60)
    c.rotate(0.15)
    shape(c, rect(-34, -40, 68, 80), hexc("fbf7ee"), "pol", lw=1.8)
    with grade(sat=lerp(GRADE["sat"], 1.0, pc)):
        vgrad(c, -32, 18, [(0, hexc("8fc3e3")), (1, hexc("f5d9a8"))], -28, 28)
        circle(c, 8, 0, 8, hexc("ffd27a"))
    line(c, [(-6, -44), (-6, -30)], "clip", 2.6, hexc("a0a0a0"))
    c.restore()
    c.save()
    c.translate(x0 + 70, y0 + h - 6)
    c.rotate(-0.08)
    shape(c, rect(-40, -16, 80, 32), hexc("e9c79a"), "tkt", lw=1.6, amp=0.4)
    line(c, [(10, -16), (10, 16)], "tktp", 1.2, INK, alpha=0.5)
    c.restore()
    # 锚点
    for idx, (fx, fy, kind, col) in enumerate(PINS):
        px, py = _pin_xy(idx)
        order = ORDER.index(idx)
        on = clamp(lit * len(ORDER) - order) if lit > 0 else 0
        if kind == "anchor":
            on = max(on, anchor_glow)
        if on > 0:
            with grade(sat=1.0):
                glow(c, px, py, 60 + 20 * on, hexc("ffd27a"), 0.85 * on)
        with grade(sat=lerp(GRADE["sat"], 1.0, on)):
            cc = hexc(col)
            if kind == "anchor":
                anchor_pin(c, px, py, 1.1, cc)
            elif kind == "flag":
                line(c, [(px, py + 4), (px, py - 22)], f"fl{idx}", 2)
                shape(c, [(px, py - 22), (px + 18, py - 16), (px, py - 10)], cc, f"flg{idx}", lw=1.4, amp=0.3)
            elif kind == "circle":
                shape(c, ell(px, py, 18, 12, 14), None, f"cir{idx}", lw=2)
                text(c, "?", px + 22, py - 8, 18, INK)
            else:
                circle(c, px, py, 7, cc)
                circle(c, px - 2, py - 2, 2.4, (1, 1, 1), 0.8)
                if kind in ("snow", "wave", "sun", "leaf"):
                    _icon(c, kind, px + 20, py - 14, 0.9)
    if dust > 0:
        r = random.Random(77)
        for k in range(int(70 * dust)):
            circle(c, r.uniform(x0, x0 + w), r.uniform(y0, y0 + h), 1.5, hexc("8b857a"), 0.6)


def map_state(c, **kw):
    return lambda cc: anchor_map(cc, STATE["t"], **kw)


# ================================================================ 三种难过（独立镜头，镜头推近）
def p1_cafe(c, t):
    zoom = 1 + 1.3 * ease_io(prog(t, 1.6, 1.6))
    with cam(c, 525, 900, zoom, ty=lerp(0, 120, ease_io(prog(t, 1.6, 1.6)))):
        fill_all(c, hexc("c9b8a3"))
        shape(c, rect(120, 260, 840, 560), hexc("6b4430"), "cfw", lw=3.4)
        vgrad(c, 280, 800, [(0, hexc("b7c0c8")), (1, hexc("d4d6d4"))], 140, 940)
        city_row(c, 800, 41, 200, 420, light=True)
        rain(c, t, 40, 0.4, seed=8, x0=140, x1=940, y0=280, y1=800)
        line(c, [(540, 260), (540, 820)], "cfm", 6, hexc("6b4430"))
        # 对面的人起身离开
        u = ease_io(prog(t, 0.3, 1.6))
        if u < 1:
            ox = lerp(800, 1250, ease_in(prog(t, 0.9, 1.0)))
            stand = ease_io(prog(t, 0.3, 0.6))
            if stand < 0.5:
                person(c, ox, 960, 1.4, sit=True, legs=False, coat=hexc("8a94a3"), hair=hexc("4a4a4a"),
                       hair_style="short", hat=False, pack=False, look=-0.6, key="ex", mouth="flat")
            else:
                person(c, ox, 1130, 1.4, view="back", coat=hexc("8a94a3"), hair=hexc("4a4a4a"), hair_style="short",
                       hat=False, pack=False, walk=t * 8 if t > 0.9 else None, key="ex")
        shape(c, rect(740, 860, 130, 20), hexc("8c5a3c"), "och", lw=3)
        shape(c, rect(850, 720, 18, 150), hexc("7a4d33"), "ochb", lw=2.4)
        girl(c, 260, 960, 1.4, sit=True, legs=False, pack=False, hat=False, look=0.8, look_up=-0.6, mouth="flat",
             arms=[(30, -60), (40, -55)], head_down=3)
        shape(c, rect(120, 950, 840, 34), hexc("8c5a3c"), "ctab2", lw=3)
        shape(c, rect(150, 984, 30, 200), hexc("7a4d33"), "ctl1", lw=2.4)
        shape(c, rect(900, 984, 30, 200), hexc("7a4d33"), "ctl2", lw=2.4)
        crack = ease_out(prog(t, 3.1, 0.35))
        with keep():
            pass
        mug(c, 480, 948, 2.0, "pmL", col=hexc("f2efe8"), heart="L")
        mug(c, 568, 948, 2.0, "pmR", col=hexc("f2efe8"), heart="R", crack=crack > 0, crack_u=crack)
        if t > 3.1:
            uu = prog(t, 3.1, 0.6)
            r = random.Random(3)
            for k in range(6):
                circle(c, 548 + r.uniform(-20, 20) + uu * r.uniform(-40, 40), 900 + uu * r.uniform(-30, 30), 2.2, INK, 1 - uu)


def p2_office(c, t):
    zoom = 1 + 0.35 * ease_io(t / 5)
    with cam(c, 540, 880, zoom):
        fill_all(c, hexc("cfd2cf"))
        shape(c, rect(-200, 1100, 1500, 900), hexc("9a9a94"), "of2", lw=3)
        lean = ease_io(t / 5)
        for i, (sx_, s_, d) in enumerate(((150, 1.8, 1), (930, 1.9, -1), (1010, 1.7, -1), (60, 1.6, 1))):
            silhouette(c, sx_ + d * lean * 50 + math.sin(t * 1.3 + i) * 5, 1100, s_, f"wh2{i}", col=hexc("9ea3ab"))
        n = 2 + int(t * 2.2)
        r = random.Random(4)
        for k in range(min(n, 14)):
            side = 1 if k % 2 else -1
            bx = 540 + side * r.uniform(150, 360)
            by = r.uniform(600, 900)
            ph = (t * 1.2 + k * 0.17) % 1
            spike = clamp(t / 4)
            pts = [(bx + side * (-ph * 40 + j * 12), by + ((-8 if j % 2 else 8) * (0.5 + spike))) for j in range(5)]
            line(c, pts, f"spk{k}", 2.6, hexc("6d737c"), alpha=0.9 * (1 - ph * 0.5))
        girl(c, 540, 930, 1.45, sit=True, legs=False, pack=False, hat=False, badge=True, head_down=5 + 3 * lean,
             mouth="flat", arms=[(-34, -60), (34, -60)], look_up=-0.6)
        shape(c, rect(200, 900, 680, 36), hexc("a69a8a"), "desk2", lw=3)
        shape(c, rect(230, 936, 30, 180), hexc("8a7f72"), "d2l1", lw=2.4)
        shape(c, rect(820, 936, 30, 180), hexc("8a7f72"), "d2l2", lw=2.4)
        shape(c, rect(640, 760, 190, 130), hexc("6f747c"), "mon2", lw=3)
        shape(c, rect(655, 775, 160, 100), hexc("dfe6ec"), "scr2", lw=2)
        for k in range(5 + int(t * 1.5)):
            shape(c, rect(250 + (k % 2) * 6, 880 - k * 13, 150, 13), hexc("f2f0ea"), f"pp2{k}", lw=1.6, amp=0.6)
        cy_ = lerp(520, 690, ease_io(t / 5))
        rain_cloud(c, 540, cy_, 2.0 + 0.3 * lean, "ocl2", col=hexc("7d828b"), t=t)


def p3_phone(c, t):
    zoom = 1 + 1.0 * ease_io(prog(t, 0.0, 1.6))
    flip = ease_io(prog(t, 2.6, 0.6))
    with grade(dark=0.35):
        with cam(c, 600, 1000, zoom, ty=lerp(0, 160, ease_io(prog(t, 0, 1.6)))):
            fill_all(c, hexc("8d8a98"))
            shape(c, rect(620, 220, 320, 400), hexc("2a3150"), "pwin", lw=3)
            r = random.Random(14)
            for i in range(9):
                star(c, r.uniform(640, 920), r.uniform(240, 600), 2.6, 0.6 + 0.4 * math.sin(t * 3 + i))
            shape(c, rect(-200, 1100, 1500, 900), hexc("6b6170"), "pfl", lw=3)
            hand = (lerp(40, 80, flip), lerp(-60, -40, flip)) if t > 2.2 else (20, -55)
            girl(c, 330, 1000, 1.5, sit=True, legs=False, pack=False, hat=False, look=0.9, look_up=-0.8,
                 mouth="flat", head_down=4, arms=[(-20, -60), hand])
            shape(c, rect(180, 990, 700, 30), hexc("8f8494"), "ptab", lw=3)
            # 平放的手机
            px, py = 600, 975
            c.save()
            c.translate(px, py)
            sy = math.cos(flip * math.pi)
            jit = math.sin(t * 50) * 3 if t < 2.6 and (t % 1.0) < 0.5 else 0
            c.translate(jit, 0)
            c.scale(1, 0.42 * max(abs(sy), 0.05))
            if sy > 0:
                with keep():
                    glow(c, 0, 0, 220 * (1 - flip), hexc("dfeaff"), 0.6)
                shape(c, rrect(-70, -120, 140, 240, 14), hexc("3a3f4a"), "pph", lw=3)
                with keep():
                    shape(c, rrect(-58, -104, 116, 208, 8), hexc("e8f0ff"), "ppsc", lw=1.6, edge=False)
                    c.save()
                    c.scale(1, 1 / 0.42)
                    text(c, "家", 0, -10, 46, INK)
                    c.restore()
                    circle(c, -28, 70, 14, hexc("6fbf73"))
                    circle(c, 28, 70, 14, hexc("e0604f"))
            else:
                shape(c, rrect(-70, -120, 140, 240, 14), hexc("2c2f36"), "ppb", lw=3)
                circle(c, -40, -90, 10, hexc("1c1e22"))
            c.restore()


# ================================================================ 填不满的日子
STROBE = [hexc("ff4f8b"), hexc("4fd1ff"), hexc("ffd34f"), hexc("9b6bff"), hexc("58f0a0")]


def beams(c, t, cx, cy, n=6, a=0.35, spin=1.0):
    with keep():
        for k in range(n):
            ang = math.pi / 2 + math.sin(t * spin * (1.3 + k * 0.2) + k) * 0.9
            col = STROBE[(k + int(t * 4)) % len(STROBE)]
            c.move_to(cx, cy)
            c.line_to(cx + math.cos(ang - 0.08) * 2400, cy + math.sin(ang - 0.08) * 2400)
            c.line_to(cx + math.cos(ang + 0.08) * 2400, cy + math.sin(ang + 0.08) * 2400)
            c.close_path()
            c.set_source_rgba(*col, a)
            c.fill()


def party_dance(c, t):
    fill_all(c, hexc("d6d2c8"))
    shape(c, rect(60, 200, 960, 840), hexc("dfe6ea"), "mirror", lw=4)
    line(c, [(60, 860), (1020, 860)], "barre", 8, hexc("8c5a3c"))
    shape(c, rect(-200, 1080, 1500, 900), hexc("b49a7a"), "dfl", lw=3)
    with keep():
        for k in range(4):
            col = STROBE[(k + int(t * 3)) % 5]
            glow(c, 200 + k * 230, 220, 260, col, 0.25)
    arm = math.sin(t * 9)
    arms = [(-30, -120 - 40 * arm), (30, -120 + 40 * arm)]
    with group_alpha(c, 0.45):
        girl(c, 640, 1040, 1.5, pack=False, hat=False, arms=arms, walk=t * 6, sx=-1, mouth="laugh", key="mir")
    girl(c, 420, 1100, 1.7, pack=False, hat=False, arms=arms, walk=t * 6, mouth="laugh")


def party_club(c, t, fade=0.0, still=False):
    fill_all(c, hexc("2b2a33"))
    if fade < 1:
        beams(c, t, 540, 120, n=7, a=0.3 * (1 - fade))
        with keep():
            glow(c, 540, 140, 120, (1, 1, 1), 0.5 * (1 - fade))
    shape(c, ell(540, 140, 46, 46, 18), hexc("c8c8d0"), "ball", lw=2.4)
    for k in range(6):
        line(c, [(500 + k * 16, 100), (500 + k * 16, 180)], f"bl{k}", 1, hexc("8a8a94"))
    line(c, [(540, 0), (540, 94)], "ballr", 3)
    shape(c, rect(-200, 1100, 1500, 900), hexc("3a3844"), "cfl", lw=3)
    r = random.Random(9)
    for i in range(16):
        x = r.uniform(-40, W + 40)
        y = r.uniform(1050, 1250)
        a = 1 - clamp(fade * 2.2 - r.uniform(0, 1.2))
        if a <= 0.02:
            continue
        hop = 0 if still else -abs(math.sin(t * 8 + i)) * 25
        silhouette(c, x, y + hop, r.uniform(1.4, 1.9), f"cr{i}", col=hexc("5a5866"), a=0.9 * a)
    hop = 0 if still else -abs(math.sin(t * 8)) * 40
    arms = [(-30, -150), (30, -150)] if not still else None
    if fade > 0.8:
        with keep():
            g = cairo.RadialGradient(540, 1180, 0, 540, 1180, 360)
            g.add_color_stop_rgba(0, 1, 1, 0.95, 0.25 * (1 - (fade - 0.8) * 2))
            g.add_color_stop_rgba(1, 1, 1, 0.95, 0)
            c.set_source(g)
            c.paint()
    girl(c, 540, 1180 + hop, 1.7, pack=False, hat=False, arms=arms, mouth="laugh" if not still else "flat",
         look_up=0.4 if not still else -0.6, head_down=0 if not still else 4)
    if fade > 0:
        veil(c, (0.05, 0.05, 0.08), 0.55 * fade)
        if fade > 0.6:
            with keep():
                g = cairo.RadialGradient(540, 1050, 0, 540, 1050, 300)
                g.add_color_stop_rgba(0, 1, 0.97, 0.9, 0.22)
                g.add_color_stop_rgba(1, 1, 0.97, 0.9, 0)
                c.set_source(g)
                c.paint()


def party_bar(c, t):
    fill_all(c, hexc("3b3036"))
    beams(c, t, 980, 0, n=4, a=0.18, spin=1.6)
    shape(c, rect(-20, 380, 1120, 20), hexc("4f3024"), "shelf2", lw=2.5)
    r = random.Random(2)
    for i in range(13):
        x = 30 + i * 82
        h = r.uniform(60, 100)
        shape(c, [(x, 380), (x, 380 - h * 0.6), (x + 9, 380 - h * 0.7), (x + 9, 380 - h), (x + 20, 380 - h),
                  (x + 20, 380 - h * 0.7), (x + 29, 380 - h * 0.6), (x + 29, 380)],
              [hexc("4f8a6b"), hexc("b5553f"), hexc("d9a441"), hexc("6a7fb0")][i % 4], f"bt2{i}", lw=2)
    girl(c, 400, 1000, 1.7, sit=True, legs=False, pack=False, hat=False, mouth="laugh",
         arms=[(-30, -70), (50, -110 + 30 * math.sin(t * 6))], look=0.5)
    person(c, 760, 1000, 1.7, sit=True, legs=False, coat=hexc("7d7a86"), hair=hexc("3a3a3a"), hair_style="short",
           hat=False, pack=False, mouth="laugh", look=-0.5, key="bm", arms=[(-50, -110 + 30 * math.sin(t * 6 + 1)), (30, -70)])
    shape(c, rect(-20, 980, 1120, 60), hexc("6b4430"), "bar2", lw=3)
    shape(c, rect(-20, 1040, 1120, 900), hexc("4a3a33"), "bar3", lw=3)
    for k in range(6):
        gx = 250 + k * 110
        shape(c, [(gx - 16, 940), (gx + 16, 940), (gx + 12, 980), (gx - 12, 980)], hexc("e8d9a8"), f"gl{k}", lw=2)
    clink = (t * 3) % 1 < 0.2
    gx1 = 400 + 50 * 1.7
    gy1 = 1000 + (-110 + 52 + 30 * math.sin(t * 6)) * 1.7
    mug(c, gx1, gy1, 1.2, "bmg1", col=hexc("f0b64a"))
    mug(c, 760 - 50 * 1.7, 1000 + (-110 + 52 + 30 * math.sin(t * 6 + 1)) * 1.7, 1.2, "bmg2", col=hexc("f0b64a"))
    if clink:
        with keep():
            for k in range(6):
                a = k * math.pi / 3 + t
                star(c, 580 + math.cos(a) * 60, 860 + math.sin(a) * 40, 5, 0.9, hexc("fff3b0"))


def s05_party(c, t):
    cuts = [0.0, 2.2, 4.2, 6.0]
    i = 0 if t < cuts[1] else 1 if t < cuts[2] else 2
    lt = t - cuts[i]
    k = 1 + 0.06 * (1 - ease_out(prog(lt, 0, 0.3)))
    with cam(c, 540, 960, k):
        [party_dance, party_club, party_bar][i](c, lt + i)
    fl = 1 - ease_out(prog(lt, 0, 0.18))
    if i > 0 and fl > 0:
        with keep():
            c.set_source_rgba(1, 1, 1, 0.5 * fl)
            c.paint()


def s06_empty(c, t):
    fade = ease_io(prog(t, 0.2, 2.6))
    party_club(c, 6.0 + (t if t < 0.3 else 0.3), fade=fade, still=t > 0.3)
    r = random.Random(4)
    for k in range(30):
        x, y = r.uniform(0, W), r.uniform(1110, 1500)
        with keep():
            circle(c, x, y, 4, STROBE[k % 5], 0.5 * (1 - fade * 0.7))
    cupx = lerp(820, 690, ease_out(prog(t, 1.0, 2.5)))
    c.save()
    c.translate(cupx, 1230)
    c.rotate(cupx * 0.03)
    shape(c, [(-14, -18), (14, -18), (10, 18), (-10, 18)], hexc("c9c4b8"), "cup", lw=2)
    c.restore()


# ================================================================ 两次没走成
def d_station(c, t, w, h):
    fill_all(c, hexc("d7d4cb"))
    shape(c, rect(-10, 260, w + 20, 80), hexc("54555a"), "dtr", lw=2.6)
    line(c, [(-10, 290), (w + 10, 290)], "drl1", 4, hexc("8d8f94"))
    line(c, [(-10, 320), (w + 10, 320)], "drl2", 4, hexc("8d8f94"))
    shape(c, rect(-10, 340, w + 20, 200), hexc("b7b2a7"), "dpl", lw=2.6)
    arrive = ease_out(prog(t, 0.2, 1.3))
    leave = ease_in(prog(t, 2.6, 1.4))
    tx = lerp(w + 50, 40, arrive) - leave * 1600
    for k in range(3):
        cx = tx + k * 330
        shape(c, rrect(cx, 120, 320, 170, 16), hexc("8c99a6"), f"dtc{k}", lw=2.6)
        for j in range(3):
            shape(c, rect(cx + 30 + j * 95, 150, 70, 60), hexc("d8e0e8"), f"dtw{k}{j}", lw=1.8)
    shape(c, rect(580, 330, 20, 120), hexc("8f8a82"), "gate1", lw=2)
    shape(c, rect(680, 330, 20, 120), hexc("8f8a82"), "gate2", lw=2)
    if t < 2.1:
        x = lerp(140, 470, ease_io(prog(t, 0, 2.0)))
        girl(c, x, 450, 1.0, look=1.0, walk=t * 8 if t < 2.0 else None, pack=False, mouth="flat",
             arms=[(-26, -76), (-40, -70)])
        suitcase(c, x - 58, 452, 0.6, "dsu1", tilt=0.15)
    elif t < 2.6:
        girl(c, 470, 450, 1.0, look=0.3, head_down=6, look_up=-0.9, pack=False, mouth="flat", arms=[(-26, -76), (-40, -70)])
        suitcase(c, 412, 452, 0.6, "dsu1", tilt=0.15)
    else:
        x = lerp(470, 120, ease_io(prog(t, 2.6, 1.6)))
        girl(c, x, 450, 1.0, look=-1.0, walk=t * 7, head_down=4, look_up=-0.5, pack=False, mouth="flat",
             arms=[(-26, -76), (40, -70)])
        suitcase(c, x + 58, 452, 0.6, "dsu2", tilt=-0.15)


def d_airport(c, t, w, h):
    fill_all(c, hexc("dcdad4"))
    shape(c, rect(30, 30, w - 60, 280), hexc("b8c4cc"), "awin", lw=3)
    for k in range(1, 5):
        line(c, [(30 + k * (w - 60) / 5, 30), (30 + k * (w - 60) / 5, 310)], f"awm{k}", 4, hexc("8a8f96"))
    c.save()
    c.rectangle(30, 30, w - 60, 280)
    c.clip()
    vgrad(c, 30, 310, [(0, hexc("b7c3cc")), (1, hexc("dfe3e2"))], 30, w - 30)
    shape(c, rect(20, 250, w, 60), hexc("8f9195"), "tarm", lw=2)
    u = prog(t, 2.0, 2.2)
    px = lerp(260, 1200, ease_in(u))
    py = 240 - ease_in(prog(t, 2.8, 1.4)) * 200
    sc = 0.9 * (1 - 0.6 * ease_in(prog(t, 2.8, 1.4)))
    c.save()
    c.translate(px, py)
    c.rotate(-0.25 * ease_in(prog(t, 2.8, 0.8)))
    plane(c, 0, 0, sc, "apl")
    c.restore()
    c.restore()
    shape(c, rect(-10, 380, w + 20, 200), hexc("b9b4aa"), "afl", lw=2.6)
    for k in range(4):
        shape(c, rect(120 + k * 130, 360, 110, 20), hexc("7d8a96"), f"seat{k}", lw=2)
    r = random.Random(3)
    for i in range(6):
        qx = lerp(700 + i * 40, 980 + i * 40, ease_in(prog(t, 0.6 + i * 0.15, 2.0)))
        silhouette(c, qx, 470, 0.85, f"aq{i}", walk=t * 6 + i, a=0.7)
    shape(c, rect(880, 300, 70, 140), hexc("6d7a86"), "agate", lw=2.4)
    droop = ease_io(prog(t, 3.0, 1.0))
    girl(c, 300, 380, 1.0, sit=True, legs=True, pack=False, look=1.0, look_up=0.2 - droop * 1.0, mouth="flat",
         head_down=droop * 5, arms=[(-20, -60), (34, -76 + 30 * droop)])
    with keep():
        bx, by = 300 + 34, 380 + (-76 + 52 + 30 * droop)
        c.save()
        c.translate(bx, by)
        c.rotate(0.4 + droop * 0.9)
        shape(c, rect(-4, -8, 34, 18), hexc("f6f1e6"), "bpass", lw=1.4, amp=0.3)
        line(c, [(18, -8), (18, 10)], "bpl", 1, INK, alpha=0.5)
        c.restore()
    suitcase(c, 220, 430, 0.6, "asu", handle=0.4)


def panel2(c, x, y, w, h, k, key, fn, t, rot=0.0):
    from scenes import panel
    panel(c, x, y, w, h, k, key, fn, t, rot)


def s07_depart(c, t):
    fill_all(c, hexc("e8e2d6"))
    panel2(c, 60, 120, 960, 520, ease_back(prog(t, 0.1, 0.5)), "dp1", d_station, min(t, 4.2), rot=-0.006)
    panel2(c, 60, 680, 960, 520, ease_back(prog(t, 3.9, 0.5)), "dp2", d_airport, t - 3.9, rot=0.005)


# ================================================================ 被吞没 · 停顿 · 惊醒
def s08_drown(c, t):
    with cam(c, 560, 880, 1.0 + 0.05 * ease_io(t / 5.5)):
        room(c, t, sky="grey", hat_hook=True, hat_dust=0.6, pack_corner=False, suit_corner=True,
             amap=map_state(c, dust=1.0))
        girl(c, 712, 1000, 1.6, sit=True, pack=False, hat=False, mouth="flat", head_down=4, look_up=-0.5,
             eyes_closed=t > 3.6)
        lvl = lerp(H + 40, 860, ease_io(prog(t, 0.0, 4.6)))
        water(c, t, lvl, "tide8", a=0.8, col=hexc("3f4a5e"))


def s08b_pause(c, t):
    glow_u = ease_io(prog(t, 1.4, 0.8))
    with cam(c, 400, 760, 1.05 + 0.2 * ease_io(prog(t, 1.2, 1.8))):
        room(c, 5.5, sky="grey", hat_hook=True, hat_dust=0.6, pack_corner=False, suit_corner=True,
             amap=map_state(c, dust=1.0, anchor_glow=glow_u))
        girl(c, 712, 1000, 1.6, sit=True, pack=False, hat=False, mouth="flat", head_down=4 - 4 * glow_u,
             look=-1.0 * glow_u, look_up=0.3 * glow_u - 0.5 * (1 - glow_u), eyes_closed=t < 1.9)
        water(c, 0.0, 860, "tide8", a=0.8, col=hexc("3f4a5e"))
        bu = prog(t, 0.2, 1.6)
        if 0 < bu < 1:
            c.arc(700, lerp(990, 870, bu), 7, 0, 2 * math.pi)
            c.set_source_rgba(0.85, 0.9, 0.95, 0.8 * (1 - bu * 0.5))
            c.set_line_width(2)
            c.stroke()


def s09_wake(c, t):
    flash = 1 - ease_out(prog(t, 0, 0.45))
    drain = ease_in(prog(t, 0, 0.5))
    lit = ease_io(prog(t, 0.5, 3.2))
    with cam(c, 420, 780, 1.25 - 0.15 * ease_io(prog(t, 0.2, 3.0))):
        room(c, t, sky="warm", hat_hook=True, pack_corner=False, suit_corner=True,
             amap=map_state(c, dust=1.0 - lit, anchor_glow=1.0, lit=lit, taut=ease_back(prog(t, 0.8, 1.2))))
        if drain < 1:
            water(c, t, lerp(860, H + 60, drain), "tide9", a=0.8 * (1 - drain), col=hexc("3f4a5e"))
        else:
            shape(c, ell(700, 1140, 260, 26, 20), WATER + (0.45,), "pud9", lw=1.6)
        girl(c, 712, 1000, 1.6, sit=True, pack=False, hat=False, look=-1.0, look_up=0.6,
             mouth="o" if t < 1.6 else "smile")
        r = random.Random(6)
        for i in range(30):
            u = prog(t, r.uniform(0, 0.6), 1.8)
            if 0 < u < 1:
                star(c, r.uniform(60, 980) + u * r.uniform(-60, 60), r.uniform(400, 1100) - u * 200, 2.5,
                     (1 - u) * 0.8, hexc("fff2c0"))
    if flash > 0:
        with keep():
            c.set_source_rgba(1, 0.98, 0.92, flash)
            c.paint()


# ================================================================ 立体书：雪山 · 大海 · 沙漠 · 雨林
def q_snow(c, x, y, w, h, t):
    vgrad(c, y, y + h, [(0, hexc("27365e")), (1, hexc("8fa9cf"))], x, x + w)
    for k in range(3):
        pts = [(x + w * i / 20, y + h * (0.18 + 0.05 * k) + math.sin(i * 0.7 + t * 1.5 + k) * 14) for i in range(21)]
        line(c, pts, f"aur{k}", 14 - k * 3, [hexc("6ff0b0"), hexc("8fd6ff"), hexc("c49bff")][k], alpha=0.45)
    mountain(c, x + w * 0.3, y + h, w * 0.7, h * 0.7, hexc("b5c3dd"), "qs1")
    mountain(c, x + w * 0.72, y + h, w * 0.6, h * 0.55, hexc("9fb1cf"), "qs2")
    r = random.Random(1)
    for k in range(18):
        sx = x + r.uniform(0, w)
        sy = y + (r.uniform(0, h) + t * 40) % h
        circle(c, sx, sy, 2.4, (1, 1, 1), 0.9)


def q_sea(c, x, y, w, h, t):
    vgrad(c, y, y + h * 0.45, [(0, hexc("9fd2ee")), (1, hexc("dff1f6"))], x, x + w)
    vgrad(c, y + h * 0.45, y + h, [(0, hexc("3f8fbf")), (1, hexc("23628f"))], x, x + w)
    shape(c, [(x + w * 0.78, y + h * 0.46), (x + w * 0.8, y + h * 0.18), (x + w * 0.86, y + h * 0.18), (x + w * 0.88, y + h * 0.46)],
          hexc("f4efe6"), "qlh", lw=2)
    shape(c, rect(x + w * 0.79, y + h * 0.12, w * 0.08, h * 0.07), hexc("d1553f"), "qlht", lw=2)
    ty_ = y + h * 0.5 - abs(math.sin(t * 1.6)) * 30
    tx_ = x + w * 0.35
    shape(c, [(tx_, ty_ + 40), (tx_ - 6, ty_ + 10), (tx_ - 40, ty_ - 10), (tx_ - 10, ty_ - 4), (tx_, ty_ - 20),
              (tx_ + 10, ty_ - 4), (tx_ + 40, ty_ - 10), (tx_ + 6, ty_ + 10), (tx_ + 6, ty_ + 40)], hexc("2c3f5a"), "whale", lw=2)
    for k in range(4):
        yy = y + h * (0.6 + k * 0.1)
        pts = [(x + w * i / 12, yy + math.sin(i * 1.3 + t * 3 + k) * 6) for i in range(13)]
        line(c, pts, f"qwv{k}", 2.4, (1, 1, 1), alpha=0.7)


def q_desert(c, x, y, w, h, t):
    vgrad(c, y, y + h * 0.6, [(0, hexc("f6b26b")), (1, hexc("fbe2b0"))], x, x + w)
    circle(c, x + w * 0.65, y + h * 0.42, h * 0.18, hexc("fff0c0"))
    shape(c, hill_pts(y + h * 0.62, 18, 0.02, 1, x - 10, x + w + 10, y + h + 10, n=20), hexc("e8b56a"), "qd1", lw=2)
    shape(c, hill_pts(y + h * 0.78, 14, 0.03, 3, x - 10, x + w + 10, y + h + 10, n=20), hexc("d99a4f"), "qd2", lw=2)
    for k in range(3):
        cx = x + w * 0.2 + k * w * 0.14 + (t * 10) % 20
        cy = y + h * 0.6 - 4
        shape(c, [(cx - 14, cy), (cx - 12, cy - 14), (cx - 4, cy - 20), (cx + 4, cy - 14), (cx + 10, cy - 22), (cx + 16, cy - 16),
                  (cx + 14, cy)], hexc("6b4a35"), f"cam{k}", lw=1.4, amp=0.4)


def q_forest(c, x, y, w, h, t):
    vgrad(c, y, y + h, [(0, hexc("7fc48a")), (1, hexc("3f8a5a"))], x, x + w)
    shape(c, rect(x + w * 0.62, y, w * 0.12, h), hexc("dff4f6"), "fall", lw=2)
    for k in range(5):
        yy = y + ((t * 120 + k * h / 5) % h)
        line(c, [(x + w * 0.64, yy), (x + w * 0.72, yy)], f"fw{k}", 2, hexc("9fd3e6"))
    for k, (lx, ly, rot) in enumerate(((0.15, 0.3, -0.6), (0.3, 0.75, 0.5), (0.85, 0.35, 0.7), (0.5, 0.9, -0.3), (0.05, 0.85, 0.3))):
        c.save()
        c.translate(x + w * lx, y + h * ly)
        c.rotate(rot + math.sin(t * 1.2 + k) * 0.05)
        shape(c, ell(0, 0, w * 0.2, h * 0.09, 16), hexc("2f7a4a"), f"lf{k}", lw=2)
        line(c, [(-w * 0.19, 0), (w * 0.19, 0)], f"lfm{k}", 1.4, hexc("1f5a35"))
        c.restore()
    for k in range(3):
        line(c, [(x + w * (0.2 + k * 0.25), y), (x + w * (0.22 + k * 0.25) + math.sin(t + k) * 8, y + h * 0.5)],
             f"vine{k}", 3, hexc("4f7a3a"))
    px = x + w * (0.1 + 0.8 * ((t * 0.25) % 1))
    py = y + h * 0.25 + math.sin(t * 4) * 10
    paper_bird_ = [(px - 14, py), (px + 14, py - 4), (px + 4, py + 6)]
    shape(c, paper_bird_, hexc("e0403a"), "parrot", lw=1.6, amp=0.3)
    shape(c, [(px - 4, py), (px + 6, py - 14 * math.sin(t * 12)), (px + 8, py)], hexc("3f6fd5"), "parw", lw=1.4, amp=0.3)


QUADS = [(q_snow, 0, "snow"), (q_sea, 1, "wave"), (q_desert, 2, "sun"), (q_forest, 3, "leaf")]


def popup_book(c, t, unfold, quad_t):
    bx0, by0, bx1, by1 = 50, 130, 1030, 900
    x0, y0 = lerp(MAP_X, bx0, unfold), lerp(MAP_Y, by0, unfold)
    x1, y1 = lerp(MAP_X + MAP_W, bx1, unfold), lerp(MAP_Y + MAP_H, by1, unfold)
    if unfold <= 0.001:
        return
    with grade(sat=1.0, warm=0.0):
        shape(c, rect(x0 - 10, y0 - 10, x1 - x0 + 20, y1 - y0 + 20), hexc("8c5a3c") + (1.0,), "bookb", lw=3)
        shape(c, rect(x0, y0, x1 - x0, y1 - y0), hexc("f3e6c6") + (1.0,), "bookp", lw=2.4)
        if unfold > 0.98:
            line(c, [(540, by0), (540, by1)], "gut", 2, hexc("c9b48f"))
        qw, qh = (bx1 - bx0 - 60) / 2, (by1 - by0 - 60) / 2
        cells = [(bx0 + 20, by0 + 20), (540 + 10, by0 + 20), (bx0 + 20, by0 + 40 + qh), (540 + 10, by0 + 40 + qh)]
        sx = (x1 - x0) / (bx1 - bx0)
        sy = (y1 - y0) / (by1 - by0)
        c.save()
        c.translate(x0, y0)
        c.scale(sx, sy)
        c.translate(-bx0, -by0)
        for k, (fn, idx, icon) in enumerate(QUADS):
            kk = ease_back(prog(quad_t, 0.9 + k * 0.55, 0.5))
            if kk <= 0.01:
                continue
            qx, qy = cells[k]
            with popup(c, qx + qw / 2, qy + qh, kk):
                c.save()
                c.rectangle(qx, qy, qw, qh)
                c.clip()
                fn(c, qx, qy, qw, qh, t)
                c.restore()
                shape(c, rect(qx, qy, qw, qh), None, f"qf{k}", lw=2.6)
            with keep():
                _icon(c, icon, qx + 26, qy + 26, 1.3)
        c.restore()


def s10_popup(c, t):
    unfold = ease_io(prog(t, 0.0, 1.0))
    e = ease_io(prog(t, 0.0, 0.9))
    with cam(c, lerp(420, 540, e), lerp(780, 900, e), lerp(1.1, 1.0, e)):
        room(c, t + 5, sky="warm", hat_hook=True, pack_corner=False, suit_corner=True,
             amap=map_state(c, lit=1.0, anchor_glow=1.0, taut=1.0))
        popup_book(c, t, unfold, t)
        gx = lerp(712, 540, ease_io(prog(t, 0.1, 1.1)))
        gy = 1160
        for k in range(4):
            u = ease_io(prog(t, 3.2 + k * 0.2, 0.9))
            if u > 0:
                qx, qy = [(290, 620), (790, 620), (290, 860), (790, 860)][k]
                pts = [(540 + (k - 1.5) * 20, gy - 10), (lerp(540, qx, 0.5) + (k - 1.5) * 60, lerp(gy, qy, 0.55)), (qx, qy)]
                seg = []
                for i in range(12):
                    v = i / 11 * u
                    if v < 0.5:
                        p = (lerp(pts[0][0], pts[1][0], v * 2), lerp(pts[0][1], pts[1][1], v * 2))
                    else:
                        p = (lerp(pts[1][0], pts[2][0], v * 2 - 1), lerp(pts[1][1], pts[2][1], v * 2 - 1))
                    seg.append(p)
                with ink_style(hexc("b0613f"), [12, 10]):
                    line(c, seg, f"path{k}", 3.4)
        tilt = 0.22 * ease_io(prog(t, 4.6, 0.4)) * (1 - ease_io(prog(t, 5.7, 0.3)))
        look = math.sin(prog(t, 3.6, 1.0) * math.pi * 2) * 0.8 if 3.6 < t < 4.6 else (-0.8 if t < 1.2 else 0.0)
        girl(c, gx, gy, 1.6, pack=False, hat=False, look=look, look_up=0.6, tilt=tilt, mouth="smile",
             walk=t * 7 if 0.1 < t < 1.2 else None)
        if 4.6 < t < 5.9:
            q = ease_back(prog(t, 4.6, 0.4))
            text(c, "?", gx + 95, gy - 330, 110 * q, INK)


def s11_hat(c, t):
    hu = ease_io(prog(t, 0.2, 0.9))
    fold = 1 - ease_io(prog(t, 0.9, 1.0))
    with cam(c, 540, 900, 1.0):
        room(c, t + 11, sky="warm", hat_hook=hu <= 0, pack_corner=False, suit_corner=True,
             amap=map_state(c, lit=1.0, anchor_glow=1.0, taut=1.0))
        popup_book(c, t + 6, fold, 99)
        gx, gy = 540, 1160
        girl(c, gx, gy, 1.6, pack=False, hat=hu >= 1, look=-0.3, look_up=0.5 if hu < 1 else 0.0, mouth="smile",
             arms=[(-26, -76), (30 + 10 * hu, -150 + 70 * hu)] if 0.1 < t < 1.3 else None)
        if 0 < hu < 1:
            hx = lerp(250, gx, hu)
            hy = lerp(812, gy - 172 * 1.6, hu) - math.sin(hu * math.pi) * 180
            c.save()
            c.translate(hx, hy)
            c.rotate((1 - hu) * 6)
            c.translate(-hx, -hy)
            hat_item(c, hx, hy, 1.4)
            c.restore()
        if 1.0 < t < 2.4:
            u = prog(t, 1.0, 1.4)
            r = random.Random(2)
            for k in range(10):
                a = r.uniform(0, 2 * math.pi)
                star(c, gx + math.cos(a) * (80 + 120 * u), gy - 290 + math.sin(a) * (80 + 120 * u), 5, 1 - u)


def s12_untie(c, t):
    shrink = [ease_io(prog(t, 0.3 + i * 0.36, 0.45)) for i in range(6)]
    stand = t > 2.6
    sux = lerp(140, 700, ease_io(prog(t, 3.0, 0.9)))
    with cam(c, 540, 900, 1.1):
        room(c, t + 14, sky="warm", hat_hook=False, chair=False, pack_corner=False, suit_corner=False,
             amap=map_state(c, lit=1.0, anchor_glow=1.0, taut=1.0))
        puddle = 1 - ease_io(prog(t, 0.3, 2.3))
        if puddle > 0:
            shape(c, ell(540, 1130, 420 * puddle + 40, 40 * puddle + 6, 26), WATER + (0.6,), "pud12", lw=2)
        floor_roots(c, 540, 1112, t, shrink)
        dust = 1 - ease_io(prog(t, 3.9, 0.5))
        suitcase(c, sux, 1110, 0.9, "su12", handle=ease_io(prog(t, 3.5, 0.4)), dust=dust)
        if dust < 1 and dust > 0:
            r = random.Random(int(t * 10))
            for k in range(8):
                circle(c, sux + r.uniform(-60, 60), 1000 + r.uniform(-60, 40), 4, hexc("c9c2b4"), dust * 0.7)
        if not stand:
            girl(c, 540, 1060, 1.6, sit=True, crouch=True, pack=False, hat=True, look=0.0, look_up=-1.0, head_down=10,
                 arms=[(-24 + 6 * math.sin(t * 6), -14), (26, -12 + 5 * math.sin(t * 5))], mouth="flat")
        else:
            reach = ease_io(prog(t, 3.0, 0.9))
            girl(c, 540, 1110, 1.6, pack=False, hat=True, look=0.6, mouth="smile",
                 arms=[(-26, -76), (lerp(30, (sux - 540) / 1.6 - 10, reach), lerp(-76, -150 * 0.9 / 1.6 - 20, reach))])


# ================================================================ 书里的想象
PAGE = (70, 150, 940, 760)


def img_plane(c, w, h, t):
    vgrad(c, 0, h, [(0, hexc("7fb9e6")), (1, hexc("e9f4fb"))], 0, w)
    for k in range(6):
        cloud(c, (k * 260 - t * 120) % (w + 400) - 200, 120 + (k * 97) % 400, 1.2 + 0.3 * (k % 2), f"ic{k}")
    plane(c, w * 0.5 + math.sin(t) * 10, h * 0.48 + math.sin(t * 1.3) * 8, 2.0, "ipl", face=4)
    for k in range(4):
        cloud(c, (k * 330 - t * 260) % (w + 500) - 250, h - 90 + (k % 2) * 30, 1.6, f"icf{k}", a=0.95)


def img_train(c, w, h, t):
    vgrad(c, 0, h * 0.6, [(0, hexc("a9d6ef")), (1, hexc("fbf0d6"))], 0, w)
    shape(c, hill_pts(h * 0.55, 30, 0.01, 1.0, -20, w + 20, h + 20), hexc("a9c48b"), "it1", lw=2.6)
    shape(c, hill_pts(h * 0.7, 20, 0.008, 2.0, -20, w + 20, h + 20), hexc("c8dc98"), "it2", lw=2.6)
    r = random.Random(5)
    for i in range(50):
        circle(c, r.uniform(0, w), r.uniform(h * 0.7, h), r.uniform(4, 7),
               [hexc("f2a6a0"), hexc("fbe29a"), hexc("ffffff"), hexc("c9a0dc")][i % 4])
    line(c, [(-10, h * 0.66), (w + 10, h * 0.66)], "irl", 4, hexc("8a5a3a"))
    x = lerp(-700, w + 200, t / 2.6)
    for k in range(3):
        cx = x - k * 300
        shape(c, rrect(cx - 280, h * 0.66 - 130, 280, 120, 14), hexc("c9553f") if k == 0 else hexc("e7d3a8"), f"itc{k}", lw=2.6)
        for j in range(3):
            shape(c, rect(cx - 260 + j * 86, h * 0.66 - 110, 64, 50), hexc("dff0f6"), f"itw{k}{j}", lw=1.8)
    for k in range(4):
        ph = (t * 1.3 + k * 0.25) % 1
        cloud(c, x - 40 - ph * 260, h * 0.66 - 160 - ph * 160, 0.3 + ph * 0.5, f"ism{k}", a=0.8 * (1 - ph))


def img_costume(c, w, h, t):
    vgrad(c, 0, h, [(0, hexc("3b3a6e")), (0.7, hexc("c8708a")), (1, hexc("f2b27a"))], 0, w)
    r = random.Random(3)
    for k in range(22):
        lx = r.uniform(0, w)
        ly = (r.uniform(0, h) - t * r.uniform(30, 60)) % (h + 60) - 30
        glow(c, lx, ly, 40, hexc("ffc070"), 0.6)
        shape(c, rrect(lx - 9, ly - 12, 18, 24, 6), hexc("ff9a4a"), f"lan{k}", lw=1.4, amp=0.3)
    shape(c, rect(-10, h * 0.8, w + 20, h * 0.2 + 10), hexc("6a4a5a"), "ifl", lw=2.4)
    sp = (t * 0.9) % 1.0
    sx = math.cos(sp * 2 * math.pi)
    girl(c, w / 2, h * 0.86, 1.5, outfit="folk", pack=True, hat=True, sx=max(abs(sx), 0.08), mouth="laugh",
         arms=[(-44, -110), (44, -110)], eyes_closed=True, key="ig1")
    for k in range(8):
        a = t * 2 + k * math.pi / 4
        star(c, w / 2 + math.cos(a) * 160, h * 0.6 + math.sin(a) * 60, 4, 0.8, hexc("fff3b0"))


def img_table(c, w, h, t):
    vgrad(c, 0, h, [(0, hexc("f4d3a0")), (1, hexc("fbecc8"))], 0, w)
    tree(c, w * 0.5, h * 0.62, 3.0, "itree", hexc("6f9a58"))
    shape(c, rect(60, h * 0.7, w - 120, 22), hexc("a8744f"), "ltab", lw=2.6)
    for k in range(6):
        sx_ = 120 + k * (w - 240) / 5
        with group_alpha(c, 0.55):
            silhouette(c, sx_, h * 0.7 + 4, 1.0, f"its{k}", col=hexc("c7a98a"))
    girl(c, w * 0.5, h * 0.7 + 4, 1.1, sit=True, legs=False, pack=False, hat=True, mouth="laugh", key="ig2",
         arms=[(-40, -70), (40, -70)])
    shape(c, rect(60, h * 0.7, w - 120, 22), hexc("a8744f"), "ltab2", lw=2.6)
    for k in range(5):
        dx = 140 + k * (w - 280) / 4
        shape(c, ell(dx, h * 0.7 - 6, 34, 10, 12), hexc("f3efe6"), f"pl{k}", lw=1.6)
        circle(c, dx, h * 0.7 - 12, 12, [hexc("e8823f"), hexc("7aa557"), hexc("d6463c")][k % 3])
        ph = (t * 0.6 + k * 0.2) % 1
        by = h * 0.7 - 30 - ph * 300
        bx = dx + math.sin(ph * 6 + k) * 30
        if ph < 0.35:
            line(c, [(dx, h * 0.7 - 30), (bx, by)], f"stm{k}", 2, (1, 1, 1), alpha=0.6)
        else:
            fl = math.sin(t * 12 + k)
            line(c, [(bx - 10, by - 5 * fl), (bx, by), (bx + 10, by - 5 * fl)], f"sbd{k}", 2.2, (1, 1, 1), alpha=1 - ph)


def img_boat(c, w, h, t):
    vgrad(c, 0, h * 0.5, [(0, hexc("2f3a6e")), (1, hexc("f2b9a0"))], 0, w)
    vgrad(c, h * 0.5, h, [(0, hexc("5a6a9a")), (1, hexc("2a3460"))], 0, w)
    r = random.Random(9)
    for k in range(16):
        star(c, r.uniform(0, w), r.uniform(0, h * 0.35), 2.4, 0.6 + 0.4 * math.sin(t * 3 + k))
        star(c, r.uniform(0, w), r.uniform(h * 0.55, h), 2.0, 0.4 + 0.3 * math.sin(t * 2 + k))
    bx = w * 0.5
    by = h * 0.62 + math.sin(t * 1.5) * 6
    with group_alpha(c, 0.6):
        person(c, bx + 90, by - 20, 1.0, sit=True, legs=False, coat=hexc("c7a98a"), hair=hexc("8a7a6a"), hair_style="short",
               hat=False, pack=False, key="fish", mouth="smile")
    girl(c, bx - 60, by - 20, 1.0, sit=True, legs=False, pack=True, hat=True, mouth="smile", key="ig3",
         arms=[(-40, -40 + 20 * math.sin(t * 3)), (-20, -30 + 20 * math.sin(t * 3))])
    shape(c, [(bx - 200, by - 20), (bx + 200, by - 20), (bx + 150, by + 30), (bx - 150, by + 30)], hexc("8c5a3c"), "boat", lw=2.6)
    ox = bx - 130
    line(c, [(ox, by - 60), (ox - 90, by + 60 + 10 * math.sin(t * 3))], "oar", 4, hexc("6b4430"))
    for k in range(3):
        ph = (t * 0.8 + k / 3) % 1
        c.save()
        c.translate(ox - 90, by + 66)
        c.scale(1, 0.3)
        c.arc(0, 0, 20 + ph * 140, 0, 2 * math.pi)
        c.restore()
        c.set_source_rgba(1, 0.95, 0.8, 0.6 * (1 - ph))
        c.set_line_width(2)
        c.stroke()


def img_path(c, w, h, t):
    vgrad(c, 0, h * 0.4, [(0, hexc("bfe0f0")), (1, hexc("fbe6c4"))], 0, w)
    shape(c, rect(-10, h * 0.4, w + 20, h * 0.6 + 10), hexc("bcd38f"), "ipg", lw=2.4)
    unroll = ease_io(prog(t, 0.0, 1.6))
    top = lerp(h, h * 0.4, unroll)
    shape(c, [(w * 0.5 - 18, top), (w * 0.5 + 18, top), (w * 0.5 + 220, h + 10), (w * 0.5 - 220, h + 10)], hexc("f1dfb8"), "scroll", lw=2.4)
    shape(c, ell(w * 0.5, top, 40, 10, 14), hexc("e6cfa0"), "roll", lw=2)
    for k in range(12):
        z = k / 12
        y = lerp(h - 20, h * 0.42, z)
        if y < top:
            continue
        side = 1 if k % 2 else -1
        x = w * 0.5 + side * lerp(30, 6, z)
        c.save()
        c.translate(x, y)
        c.scale(lerp(1.0, 0.3, z), lerp(0.55, 0.18, z))
        c.arc(0, 0, 12, 0, 2 * math.pi)
        c.restore()
        c.set_source_rgba(*G(hexc("8c6f4a"))[:3], 0.7)
        c.fill()
    u = ease_io(prog(t, 0.8, 2.0))
    gy = lerp(h - 30, h * 0.6, u)
    s = lerp(1.2, 0.6, u)
    girl(c, w * 0.5, gy, s, view="back", pack=True, hat=True, walk=t * 6, key="ig4")


def img_badge(c, w, h, t):
    c.save()
    k = w / 1080
    c.scale(k, k)
    c.translate(0, -560)
    s24_badge(c, t, outfit="folk")
    c.restore()


def img_redraw(c, w, h, t):
    c.save()
    k = w / 1080
    c.scale(k, k)
    c.translate(0, -560)
    s25_redraw(c, t, outfit="folk")
    c.restore()


IMG_PAGES = [(0.0, 2.4, img_plane), (2.4, 5.0, img_train), (5.0, 7.2, img_costume), (7.2, 9.2, img_table),
             (9.2, 11.6, img_boat), (11.6, 14.0, img_path), (14.0, 18.0, img_badge), (18.0, 24.0, img_redraw)]


def s13_imagine(c, t):
    bx, by, bw, bh = PAGE
    with cam(c, 540, 900, 1.0):
        room(c, t + 18, sky="warm", hat_hook=False, chair=False, pack_corner=False, suit_corner=False,
             amap=map_state(c, lit=1.0, anchor_glow=1.0, taut=1.0))
        rise = ease_out(prog(t, 0.0, 0.9))
        float_y = math.sin(t * 1.2) * 6
        oy = lerp(300, 0, rise) + float_y
        spill = ease_io(prog(t, 19.0, 3.0))
        with keep():
            glow(c, 540, by + bh / 2 + oy, 700, hexc("fff0c8"), 0.35 + 0.3 * spill)
        with grade(sat=1.0, warm=0.0, dark=0.0):
            c.save()
            c.translate(0, oy)
            with group_alpha(c, rise):
                shape(c, rect(bx - 16, by - 16, bw + 32, bh + 32), hexc("2f4a3c") + (1.0,), "ibk", lw=3)
                shape(c, rect(bx, by, bw, bh), hexc("f6eedd") + (1.0,), "ipg0", lw=2)
                idx = 0
                for i, (a, b, fn) in enumerate(IMG_PAGES):
                    if a <= t < b or (i == len(IMG_PAGES) - 1 and t >= b):
                        idx = i
                a, b, fn = IMG_PAGES[idx]
                c.save()
                c.rectangle(bx + 14, by + 14, bw - 28, bh - 28)
                c.clip()
                c.translate(bx + 14, by + 14)
                fn(c, bw - 28, bh - 28, t - a)
                c.restore()
                # 梦一样的柔光边缘
                g = cairo.RadialGradient(540, by + bh / 2, bh * 0.35, 540, by + bh / 2, bh * 0.75)
                g.add_color_stop_rgba(0, 1, 0.98, 0.92, 0)
                g.add_color_stop_rgba(1, 1, 0.98, 0.92, 0.55)
                c.set_source(g)
                c.rectangle(bx + 14, by + 14, bw - 28, bh - 28)
                c.fill()
                # 翻页
                lt = t - a
                if idx > 0 and lt < 0.35:
                    p = ease_io(lt / 0.35)
                    ex = bx + bw * (1 - p)
                    c.rectangle(bx + 14, by + 14, max(0, ex - bx - 14), bh - 28)
                    c.set_source_rgba(0.97, 0.94, 0.86, 1)
                    c.fill()
                    line(c, [(ex, by + 14), (ex, by + bh - 14)], "pgfl", 2)
                r = random.Random(int(t * 4))
                for k in range(6):
                    star(c, bx + r.uniform(20, bw - 20), by + r.uniform(20, bh - 20), 3, 0.6, hexc("fff6d0"))
            c.restore()
        if spill > 0:
            with keep():
                aim = math.atan2(960 - (by + bh + oy), 330 - 540)
                for k in range(7):
                    a0 = aim + (k - 3) * 0.1
                    c.move_to(540, by + bh + oy - 20)
                    c.line_to(540 + math.cos(a0 - 0.04) * 700, by + bh + oy + math.sin(a0 - 0.04) * 700)
                    c.line_to(540 + math.cos(a0 + 0.04) * 700, by + bh + oy + math.sin(a0 + 0.04) * 700)
                    c.close_path()
                    c.set_source_rgba(1, 0.95, 0.78, 0.13 * spill)
                    c.fill()
        # 现实中的她：行李箱，工牌
        gx, gy = 330, 1180
        took = ease_io(prog(t, 15.4, 1.0))
        smile = t > 2.5
        has_badge = t < 15.3
        tx, ty = 820, 1080
        shape(c, rect(740, 1080, 180, 18), hexc("8c5a3c"), "stab", lw=2.6)
        shape(c, rect(755, 1098, 14, 80), hexc("7a4d33"), "stl1", lw=2)
        shape(c, rect(892, 1098, 14, 80), hexc("7a4d33"), "stl2", lw=2)
        toss = prog(t, 16.0, 0.6)
        if 0 < toss < 1:
            bxp = lerp(gx + 40 * 1.4, 817, toss)
            byp = lerp(gy - 95 * 1.4, 1068, toss) - math.sin(toss * math.pi) * 160
            c.save()
            c.translate(bxp, byp)
            c.rotate(toss * 8)
            shape(c, rect(-11, -10, 22, 20), hexc("f8f6f0"), "fbadge", lw=1.6, amp=0.3)
            c.restore()
        if toss >= 1:
            shape(c, rect(806, 1060, 22, 20), hexc("f8f6f0"), "rbadge", lw=1.6, amp=0.3)
        with keep():
            if spill > 0:
                glow(c, gx, gy - 260, 220, hexc("fff0c0"), 0.5 * spill)
        if 15.0 < t < 16.0:
            arms = [(-26, -76), (lerp(10, 40, took), lerp(-110, -95, took))]
        elif 16.0 <= t < 16.5:
            arms = [(-26, -76), (46, -130)]
        else:
            arms = [(-26, -76), (44, -84)]
        girl(c, gx, gy, 1.4, pack=False, hat=True, badge=has_badge, look=0.6 if t < 14.6 else 0.2,
             look_up=0.8 if t < 14.6 or t > 16.6 else -0.9, mouth="smile" if smile else "o",
             head_down=4 if 14.6 < t < 16.6 else 0, arms=arms, eyes_closed=t > 21.5)
        suitcase(c, gx + 44 * 1.4 + 50, gy + 2, 0.9, "su13", handle=1.0)


def s14_door(c, t):
    tx = -480 * ease_io(prog(t, 0.6, 1.2))
    door = ease_io(prog(t, 1.4, 0.7))
    rad = 2400 * ease_io(prog(t, 1.8, 2.2))
    orb = prog(t, 0.0, 1.2)

    def outside(cc):
        vgrad(cc, 560, 900, [(0, hexc("8fc3e3")), (1, hexc("fbf0d6"))], 1150, 1400)
        glow(cc, 1300, 760, 200, hexc("fff3c0"), 0.9)
        shape(cc, hill_pts(880, 26, 0.02, 1.0, 1140, 1410, 1110), hexc("a9c48b"), "dh14", lw=2.4)
        r = random.Random(3)
        for i in range(24):
            circle(cc, r.uniform(1150, 1400), r.uniform(900, 1100), r.uniform(4, 8),
                   [hexc("f2a6a0"), hexc("fbe29a"), hexc("ffffff"), hexc("c9a0dc")][i % 4])

    def scene(cc):
        cc.save()
        cc.translate(tx, 0)
        room(cc, t + 42, sky="warm", hat_hook=False, chair=False, pack_corner=False, suit_corner=False, door=door,
             door_world=outside, amap=map_state(cc, lit=1.0, anchor_glow=1.0, taut=1.0))
        shape(cc, rect(740, 1080, 180, 18), hexc("8c5a3c"), "stab", lw=2.6)
        shape(cc, rect(806, 1060, 22, 20), hexc("f8f6f0"), "rbadge", lw=1.6, amp=0.3)
        if door > 0:
            glow(cc, 1275, 830, 600 * door, hexc("fff0c0"), 0.6)
        x = lerp(330, 1210, ease_io(prog(t, 0.6, 3.0)))
        walking = 0.6 < t < 3.6
        back = t > 2.2
        girl(cc, x, 1180 - 70 * ease_io(prog(t, 2.6, 1.0)), 1.4 - 0.15 * ease_io(prog(t, 2.6, 1.0)),
             view="back" if back else "front", pack=False, hat=True, look=1.0, walk=t * 8 if walking else None,
             arms=[(-30 if back else 30, -76), (44, -84)])
        sx = x - 100 if back else x + 110
        suitcase(cc, sx, 1180 - 70 * ease_io(prog(t, 2.6, 1.0)), 0.9, "su14", handle=1.0, tilt=0.15 if walking else 0)
        cc.restore()

    flood(c, scene, 1275 + tx, 830, rad, soft=420, from_sat=0.3, to_sat=1.0)
    if orb < 1:
        with keep():
            ox = lerp(540, 1275 + tx, ease_io(orb))
            oy_ = lerp(530, 830, ease_io(orb))
            glow(c, ox, oy_, 160 * (1 - orb * 0.5), hexc("fff0c0"), 0.9)
            circle(c, ox, oy_, 18 * (1 - orb * 0.6), hexc("fffbe8"))
    if t > 1.8:
        GRADE["keep"] += 1
        r = random.Random(12)
        for i in range(40):
            st = r.uniform(1.8, 3.4)
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


_STILL2 = {}


def door_still():
    if "s" not in _STILL2:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(105.9)
        with grade(sat=1.0, dark=0.0, warm=0.0):
            s14_door(cc, 4.95)
        _STILL2["s"] = surf
    return _STILL2["s"]


def outro2(c, t):
    book_outro(c, t, door_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第一章 · 完")

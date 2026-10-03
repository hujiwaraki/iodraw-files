"""第一章 · 出逃（第二版）—— 新增与重做的镜头。"""
import math
import random

import cairo
from contextlib import contextmanager

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
    zoom = 1 + 0.45 * ease_io(prog(t, 0.0, 1.6))
    flip = ease_io(prog(t, 2.6, 0.6))
    with grade(dark=0.35):
        with cam(c, 520, 960, zoom, ty=lerp(0, 60, ease_io(prog(t, 0, 1.6)))):
            fill_all(c, hexc("8d8a98"))
            shape(c, rect(620, 220, 320, 400), hexc("2a3150"), "pwin", lw=3)
            r = random.Random(14)
            for i in range(9):
                star(c, r.uniform(640, 920), r.uniform(240, 600), 2.6, 0.6 + 0.4 * math.sin(t * 3 + i))
            shape(c, rect(-200, 1100, 1500, 900), hexc("6b6170"), "pfl", lw=3)
            hand = (lerp(40, 70, flip), lerp(-60, -46, flip)) if t > 2.2 else (20, -55)
            girl(c, 330, 1000, 1.5, sit=True, legs=False, pack=False, hat=False, look=0.9, look_up=-0.8,
                 mouth="flat", head_down=4, arms=[(-20, -60), hand])
            shape(c, rect(180, 990, 700, 30), hexc("8f8494"), "ptab", lw=3)
            # 平放的手机
            px, py = 560, 982
            c.save()
            c.translate(px, py)
            sy = math.cos(flip * math.pi)
            jit = math.sin(t * 50) * 3 if t < 2.6 and (t % 1.0) < 0.5 else 0
            c.translate(jit, 0)
            c.scale(0.62, 0.62 * 0.42 * max(abs(sy), 0.05))
            if sy > 0:
                with keep():
                    glow(c, 0, 0, 260 * (1 - flip), hexc("dfeaff"), 0.55)
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


NEON = "今晚不醉不归"


def neon_sign(c, t, on=6, cx=540, cy=360, size=88):
    """霓虹灯字：on = 还亮着的字数（从右往左熄灭）。"""
    n = len(NEON)
    x0 = cx - size * n / 2 + size / 2
    with keep():
        shape(c, rrect(cx - size * n / 2 - 30, cy - size * 0.75, size * n + 60, size * 1.4, 18), hexc("1c1b22"), "nbox", lw=3)
        for i, ch in enumerate(NEON):
            x = x0 + i * size
            lit = i < on
            flick = 1.0
            if lit and i == on - 1 and on < n:
                flick = 0.55 + 0.45 * math.sin(t * 60)
            col = hexc("ff4f8b") if i % 2 == 0 else hexc("ffd34f")
            if lit:
                glow(c, x, cy, size * 0.95, col, 0.55 * flick)
                text(c, ch, x, cy + size * 0.36, size, mix(col, (1, 1, 1), 0.45), a=flick)
            else:
                text(c, ch, x, cy + size * 0.36, size, hexc("4a4852"), a=0.9)


def party_schedule(c, t):
    fill_all(c, hexc("e9e3d6"))
    shape(c, rect(110, 140, 860, 1080), hexc("f6f1e4"), "nb", lw=3)
    for k in range(18):
        line(c, [(140, 260 + k * 52), (940, 260 + k * 52)], f"nbl{k}", 1.2, hexc("c9c0ac"), alpha=0.7)
    line(c, [(250, 160), (250, 1200)], "nbm", 1.6, hexc("d9a49a"))
    text(c, "这一周", 540, 225, 54, INK)
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    plans = ["舞蹈课", "健身", "喝酒", "聚餐", "蹦迪", "看演出", "再约"]
    for i, (d, pl) in enumerate(zip(days, plans)):
        y = 330 + i * 120
        text(c, d, 190, y, 40, INK, a=0.85)
        a = clamp((t - 0.05 - i * 0.14) / 0.12)
        if a > 0:
            text(c, pl, 290, y, 48, INK, a=a, anchor="l")
    extras = [("+ 加班后再喝一杯", 560, 455, -0.06), ("+ 通宵！", 640, 695, 0.08), ("+ 续摊", 600, 935, -0.1),
              ("满了", 760, 1160, -0.15)]
    for k, (tx_, x, y, rot) in enumerate(extras):
        a = clamp((t - 1.05 - k * 0.1) / 0.1)
        if a > 0:
            c.save()
            c.translate(x, y)
            c.rotate(rot)
            text(c, tx_, 0, 0, 38 if k < 3 else 60, hexc("b5473c"), a=a, anchor="l")
            c.restore()


def party_club(c, t, fade=0.0, still=False, neon_on=6):
    fill_all(c, hexc("2b2a33"))
    if fade < 1:
        beams(c, t, 540, 120, n=7, a=0.3 * (1 - fade))
        with keep():
            glow(c, 540, 140, 120, (1, 1, 1), 0.5 * (1 - fade))
    shape(c, ell(540, 140, 46, 46, 18), hexc("c8c8d0"), "ball", lw=2.4)
    for k in range(6):
        line(c, [(500 + k * 16, 100), (500 + k * 16, 180)], f"bl{k}", 1, hexc("8a8a94"))
    line(c, [(540, 0), (540, 94)], "ballr", 3)
    neon_sign(c, t, on=neon_on)
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


PARTY_CUTS = [0.0, 1.6, 3.2, 4.7, 6.0]


def s05_party(c, t):
    i = max(j for j in range(4) if t >= PARTY_CUTS[j])
    lt = t - PARTY_CUTS[i]
    k = 1 + 0.06 * (1 - ease_out(prog(lt, 0, 0.3)))
    with cam(c, 540, 960, k):
        [party_schedule, party_dance, party_club, party_bar][i](c, lt + (0 if i == 0 else i))
    fl = 1 - ease_out(prog(lt, 0, 0.18))
    if i > 0 and fl > 0:
        with keep():
            c.set_source_rgba(1, 1, 1, 0.5 * fl)
            c.paint()


NEON_OFF = [0.4 + i * 0.4 for i in range(6)]       # 从右往左，一个字一个字熄灭


def s06_empty(c, t):
    fade = ease_io(prog(t, 0.2, 2.6))
    on = 6 - sum(1 for i in range(6) if t >= NEON_OFF[i])
    party_club(c, 6.0 + (t if t < 0.3 else 0.3), fade=fade, still=t > 0.3, neon_on=on)
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
    x = lerp(150, w + 700, t / 2.6)
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


BUB = (548, 470, 440, 350)          # 想象气泡：中心与半径


def s14_door(c, t):
    tx = -480 * ease_io(prog(t, 0.6, 1.2))
    door = ease_io(prog(t, 1.4, 0.7))
    rad = 2400 * ease_io(prog(t, 1.8, 2.2))

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
    pop_ = ease_out(prog(t, 0.0, 0.3))
    with keep():
        if pop_ < 1:
            glow(c, BUB[0], BUB[1], 560 * (1 + pop_ * 0.3), hexc("fff3d0"), 0.85 * (1 - pop_))
        r = random.Random(21)
        for k in range(40):
            d = r.uniform(0, 0.4)
            u = ease_io(prog(t, 0.05 + d * 0.5, 1.1))
            if u >= 1:
                continue
            sx_ = BUB[0] + r.uniform(-0.85, 0.85) * BUB[2]
            sy_ = BUB[1] + r.uniform(-0.85, 0.85) * BUB[3]
            ex, ey = 1275 + tx + r.uniform(-60, 60), 830 + r.uniform(-120, 120)
            x = lerp(sx_, ex, u) + math.sin(u * 6 + k) * 30
            y = lerp(sy_, ey, u) - math.sin(u * math.pi) * 80
            glow(c, x, y, 26, hexc("fff0c0"), 0.8 * (1 - u * 0.6))
            circle(c, x, y, 4, hexc("fffbe8"), 1 - u * 0.5)
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


# ================================================================ 想象的气泡（第三版）：和当地人一起
SKIN_L = hexc("e8c09a")
TRAIL = [(318, 884, 9), (346, 852, 14)]


def local(c, x, y, s, key, coat, hair=hexc("2f2a28"), style="short", **kw):
    kw.setdefault("hat", False)
    kw.setdefault("pack", False)
    person(c, x, y, s, coat=coat, hair=hair, hair_style=style, skin=SKIN_L, key=key, **kw)


def thought_path(c, k=1.0, ox=0.0, oy=0.0):
    cx, cy, rx, ry = BUB
    pts = []
    for i in range(96):
        a = i / 96 * 2 * math.pi
        r = 1 + 0.035 * math.cos(a * 11) + 0.012 * math.sin(a * 5 + STATE["t"])
        pts.append((cx + ox + math.cos(a) * rx * r * k, cy + oy + math.sin(a) * ry * r * k))
    spath(c, pts, True)


def img_train_in(c, w, h, t):
    fill_all(c, hexc("f1e2c4"))
    c.save()
    c.rectangle(60, 70, w - 120, h * 0.48)
    c.clip()
    vgrad(c, 70, 70 + h * 0.48, [(0, hexc("a9d6ef")), (1, hexc("fbf0d6"))], 60, w - 60)
    shape(c, hill_pts(70 + h * 0.36, 26, 0.012, t * 2.2, 40, w - 40, 70 + h * 0.5, n=20), hexc("a9c48b"), "tw1", lw=2)
    for k in range(6):
        x = (k * 200 - t * 380) % (w + 200) - 100
        tree(c, x, 70 + h * 0.44, 0.5, f"twt{k}", hexc("74a160"))
    c.restore()
    shape(c, rect(60, 70, w - 120, h * 0.48), None, "twin", lw=4)
    shape(c, rect(-10, h * 0.62, w + 20, h * 0.4), hexc("b37a55"), "tseat", lw=2.6)
    girl(c, w * 0.3, h * 0.66, 1.25, sit=True, legs=False, outfit="folk", pack=False, hat=True, look=0.8,
         mouth="laugh" if t > 1.8 else "smile", key="itg", arms=[(-30, -70), (lerp(30, 60, ease_io(prog(t, 1.4, 0.5))), -80)])
    give = ease_io(prog(t, 0.6, 1.0))
    local(c, w * 0.72, h * 0.66, 1.25, "gran1", hexc("8d6a9f"), hexc("e3ddd5"), "granny", sit=True, legs=False,
          look=-0.8, mouth="laugh", arms=[(lerp(-30, -110, give), -80), (30, -70)])
    ox = w * 0.72 + lerp(-30, -110, give) * 1.25
    if t > 1.8:
        ox = lerp(ox, w * 0.3 + 60 * 1.25, ease_io(prog(t, 1.8, 0.4)))
    circle(c, ox, h * 0.66 + (-80 + 52) * 1.25 - 8, 16, hexc("f08a2a"))
    line(c, [(ox, h * 0.66 + (-80 + 52) * 1.25 - 24), (ox + 6, h * 0.66 + (-80 + 52) * 1.25 - 32)], "leafo", 2.4, hexc("4f9a5c"))


def img_dance(c, w, h, t):
    vgrad(c, 0, h, [(0, hexc("3b3a6e")), (0.7, hexc("c8708a")), (1, hexc("f2b27a"))], 0, w)
    r = random.Random(3)
    for k in range(20):
        lx = r.uniform(0, w)
        ly = (r.uniform(0, h) - t * r.uniform(30, 60)) % (h + 60) - 30
        glow(c, lx, ly, 40, hexc("ffc070"), 0.6)
        shape(c, rrect(lx - 9, ly - 12, 18, 24, 6), hexc("ff9a4a"), f"lan{k}", lw=1.4, amp=0.3)
    shape(c, ell(w / 2, h * 0.86, w * 0.42, 50, 30), hexc("8a5a6a"), "dfloor", lw=2)
    cols = [hexc("d1553f"), hexc("e8b94a"), hexc("4f8a8b"), hexc("8d6a9f"), hexc("e07a5f")]
    styles = ["short", "bun", "granny", "short", "bob"]
    dancers = []
    for i in range(6):
        a = t * 1.1 + i * 2 * math.pi / 6
        x = w / 2 + math.cos(a) * w * 0.3
        y = h * 0.86 + math.sin(a) * 42
        dancers.append((y, i, x))
    for y, i, x in sorted(dancers):
        s = 0.95 + (y - h * 0.86) / 42 * 0.12
        arms = [(-40, -92), (40, -92)]
        if i == 0:
            girl(c, x, y, s * 1.1, outfit="folk", pack=False, hat=True, walk=t * 7, arms=arms, mouth="laugh", key="idg")
        else:
            local(c, x, y, s, f"dl{i}", cols[i - 1], hexc("e3ddd5") if styles[i - 1] == "granny" else hexc("2f2a28"),
                  styles[i - 1], walk=t * 7 + i, arms=arms, mouth="laugh")


def img_feast(c, w, h, t):
    vgrad(c, 0, h, [(0, hexc("f4d3a0")), (1, hexc("fbecc8"))], 0, w)
    tree(c, w * 0.5, h * 0.6, 3.0, "itree", hexc("6f9a58"))
    seats = [(0.16, hexc("4f8a8b"), "short"), (0.32, hexc("d1553f"), "bun"), (0.68, hexc("8d6a9f"), "granny"),
             (0.84, hexc("e8b94a"), "short")]
    for k, (fx, col, st) in enumerate(seats):
        local(c, w * fx, h * 0.72, 1.05, f"fs{k}", col, hexc("e3ddd5") if st == "granny" else hexc("2f2a28"), st,
              sit=True, legs=False, mouth="laugh", look=0.6 if fx < 0.5 else -0.6)
    girl(c, w * 0.5, h * 0.72, 1.1, sit=True, legs=False, outfit="folk", pack=False, hat=True, mouth="laugh", key="ifg",
         arms=[(-40, -60), (40, -60)])
    shape(c, rect(40, h * 0.72, w - 80, 24), hexc("a8744f"), "ftab", lw=2.6)
    for k in range(5):
        dx = 120 + k * (w - 240) / 4
        if k == 3:
            dx = lerp(w * 0.74, w * 0.56, ease_io(prog(t, 0.3, 1.0)))
        shape(c, ell(dx, h * 0.72 - 6, 34, 10, 12), hexc("f3efe6"), f"fpl{k}", lw=1.6)
        circle(c, dx, h * 0.72 - 12, 12, [hexc("e8823f"), hexc("7aa557"), hexc("d6463c")][k % 3])
        ph = (t * 0.6 + k * 0.2) % 1
        by = h * 0.72 - 30 - ph * 300
        bx = dx + math.sin(ph * 6 + k) * 30
        if ph < 0.35:
            line(c, [(dx, h * 0.72 - 30), (bx, by)], f"fstm{k}", 2, (1, 1, 1), alpha=0.6)
        else:
            fl = math.sin(t * 12 + k)
            line(c, [(bx - 10, by - 5 * fl), (bx, by), (bx + 10, by - 5 * fl)], f"fsb{k}", 2.2, (1, 1, 1), alpha=1 - ph)


def img_row(c, w, h, t):
    vgrad(c, 0, h * 0.5, [(0, hexc("2f3a6e")), (1, hexc("f2b9a0"))], 0, w)
    vgrad(c, h * 0.5, h, [(0, hexc("5a6a9a")), (1, hexc("2a3460"))], 0, w)
    r = random.Random(9)
    for k in range(16):
        star(c, r.uniform(0, w), r.uniform(0, h * 0.35), 2.4, 0.6 + 0.4 * math.sin(t * 3 + k))
        star(c, r.uniform(0, w), r.uniform(h * 0.55, h), 2.0, 0.4 + 0.3 * math.sin(t * 2 + k))
    bx, by = w * 0.5, h * 0.64 + math.sin(t * 1.5) * 6
    stroke = math.sin(t * 3)
    girl(c, bx - 40, by - 20, 1.1, sit=True, legs=False, outfit="folk", pack=False, hat=True, mouth="laugh", key="irg",
         arms=[(-50, -40 + 20 * stroke), (-30, -34 + 20 * stroke)])
    local(c, bx + 40, by - 20, 1.1, "fisher", hexc("7a8a6a"), hexc("8a7a6a"), "short", sit=True, legs=False,
          mouth="laugh", look=-0.8, arms=[(-70, -44 + 20 * stroke), (-50, -30 + 20 * stroke)])
    shape(c, [(bx - 220, by - 20), (bx + 200, by - 20), (bx + 150, by + 30), (bx - 170, by + 30)], hexc("8c5a3c"), "rboat", lw=2.6)
    ox = bx - 100
    line(c, [(ox, by - 70), (ox - 110, by + 60 + 10 * stroke)], "roar", 4.5, hexc("6b4430"))
    for k in range(3):
        ph = (t * 0.8 + k / 3) % 1
        c.save()
        c.translate(ox - 110, by + 66)
        c.scale(1, 0.3)
        c.arc(0, 0, 20 + ph * 160, 0, 2 * math.pi)
        c.restore()
        c.set_source_rgba(1, 0.95, 0.8, 0.6 * (1 - ph))
        c.set_line_width(2)
        c.stroke()


def img_walk(c, w, h, t):
    vgrad(c, 0, h * 0.4, [(0, hexc("bfe0f0")), (1, hexc("fbe6c4"))], 0, w)
    shape(c, rect(-10, h * 0.4, w + 20, h * 0.6 + 10), hexc("bcd38f"), "iwg", lw=2.4)
    shape(c, [(w * 0.5 - 18, h * 0.4), (w * 0.5 + 18, h * 0.4), (w * 0.5 + 240, h + 10), (w * 0.5 - 240, h + 10)],
          hexc("d8c9b0"), "stone", lw=2.4)
    for k in range(14):
        z = k / 14
        y = lerp(h - 10, h * 0.42, z)
        line(c, [(w * 0.5 - lerp(230, 16, z), y), (w * 0.5 + lerp(230, 16, z), y)], f"st{k}", 1.4, hexc("b9a988"), alpha=0.7)
    u = ease_io(prog(t, 0.0, 2.4))
    for k, (dx, col, st) in enumerate(((-90, hexc("4f8a8b"), "short"), (90, hexc("d1553f"), "granny"))):
        gy = lerp(h - 40, h * 0.62, u) - k * 20
        s = lerp(1.15, 0.65, u)
        x = w * 0.5 + dx * s
        local(c, x, gy, s, f"wl{k}", col, hexc("e3ddd5") if st == "granny" else hexc("2f2a28"), st, view="back", walk=t * 6 + k)
        shape(c, ell(x + 22 * s, gy - 80 * s, 18 * s, 12 * s, 10), hexc("c49a6c"), f"wbk{k}", lw=1.8)
    gy = lerp(h - 20, h * 0.64, u)
    girl(c, w * 0.5, gy, lerp(1.2, 0.68, u), view="back", outfit="folk", pack=True, hat=True, walk=t * 6, key="iwgl")


def img_badge2(c, w, h, t):
    vgrad(c, 0, h * 0.55, [(0, hexc("f6d7a6")), (1, hexc("fbeccc"))], 0, w)
    for i, (x, w_, h_, wc, rc) in enumerate(((40, 150, 200, "f1c27d", "b4533f"), (220, 120, 260, "8fc0b5", "3f6f73"),
                                              (w - 330, 140, 220, "e98f6f", "8b4a3a"), (w - 170, 140, 180, "f3e3c3", "3c6ea5"))):
        house(c, x, h * 0.6, w_, h_, hexc(wc), hexc(rc), f"ibh{i}")
    shape(c, rect(-10, h * 0.6, w + 20, h * 0.4 + 10), hexc("e6d2a8"), "isq", lw=2.4)
    bx, by = w * 0.72, h * 0.86
    shape(c, rect(bx - 60, by - 60, 120, 60), hexc("b37a4c"), "ibox", lw=2.6)
    toss = prog(t, 0.8, 0.8)
    gx, gy = w * 0.38, h * 0.88
    girl(c, gx, gy, 1.5, outfit="folk", pack=False, hat=True, badge=t < 0.8, mouth="laugh",
         arms=[(-26, -76), (40, -130)] if 0.6 < t < 1.4 else None, key="ibg")
    if 0.8 <= t < 1.6:
        x = lerp(gx + 40 * 1.5, bx, toss)
        y = lerp(gy - 130 * 1.5, by - 50, toss) - math.sin(toss * math.pi) * 150
        c.save()
        c.translate(x, y)
        c.rotate(toss * 9)
        shape(c, rect(-12, -10, 24, 20), hexc("f8f6f0"), "ibdg", lw=1.6, amp=0.3)
        c.restore()
    clap = 0.5 + 0.5 * math.sin(t * 14) if t > 1.6 else 0.0
    for k, (x, col, st) in enumerate(((w * 0.12, hexc("4f8a8b"), "short"), (w * 0.9, hexc("8d6a9f"), "granny"))):
        d = 1 if x < w / 2 else -1
        local(c, x, gy, 1.3, f"cl{k}", col, hexc("e3ddd5") if st == "granny" else hexc("2f2a28"), st,
              mouth="laugh", look=0.6 * d, arms=[(-6 - 14 * clap, -96), (6 + 14 * clap, -96)])
    if t > 1.6:
        r = random.Random(int(t * 6))
        for k in range(8):
            star(c, bx + r.uniform(-80, 80), by - 80 + r.uniform(-60, 20), 4, 0.8, hexc("fff3b0"))


def img_redraw2(c, w, h, t):
    c.save()
    k = w / 1080
    c.scale(k, k)
    c.translate(0, -560)
    s25_redraw(c, t, outfit="folk")
    if t > 3.8:
        a = ease_io(prog(t, 3.8, 0.8))
        clap = 0.5 + 0.5 * math.sin(t * 14)
        with group_alpha(c, a):
            for j, (x, col, st) in enumerate(((240, hexc("4f8a8b"), "short"), (840, hexc("8d6a9f"), "granny"))):
                d = 1 if x < 540 else -1
                local(c, x, 1150, 1.8, f"rl{j}", col, hexc("e3ddd5") if st == "granny" else hexc("2f2a28"), st,
                      mouth="laugh", look=0.6 * d, arms=[(-6 - 14 * clap, -96), (6 + 14 * clap, -96)])
    c.restore()


IMG_PAGES = [(0.0, 2.4, img_plane), (2.4, 5.0, img_train_in), (5.0, 7.2, img_dance), (7.2, 9.2, img_feast),
             (9.2, 11.6, img_row), (11.6, 14.0, img_walk), (14.0, 18.0, img_badge2), (18.0, 24.0, img_redraw2)]


def _page_at(t):
    idx = 0
    for i, (a, b, fn) in enumerate(IMG_PAGES):
        if t >= a:
            idx = i
    return idx


def s13_imagine(c, t):
    cx, cy, rx, ry = BUB
    with cam(c, 540, 900, 1.0):
        room(c, t + 18, sky="warm", hat_hook=False, chair=False, pack_corner=False, suit_corner=False,
             amap=map_state(c, lit=1.0, anchor_glow=1.0, taut=1.0))
        pop = ease_back(prog(t, 0.2, 0.8))
        trail_a = [ease_out(prog(t, 0.0, 0.25)), ease_out(prog(t, 0.1, 0.25))]
        spill = ease_io(prog(t, 19.0, 3.0))
        fy = math.sin(t * 1.2) * 6
        with keep():
            glow(c, cx, cy + fy, 700, hexc("fff0c8"), (0.3 + 0.3 * spill) * pop)
        with grade(sat=1.0, warm=0.0, dark=0.0):
            for (x, y, r_), a in zip(TRAIL, trail_a):
                if a > 0:
                    shape(c, ell(x, y + fy * 0.3, r_ * a, r_ * a, 12), (1, 0.99, 0.95), f"tr{x}", lw=2.4, amp=0.6)
            if pop > 0.01:
                c.save()
                ax, ay = 360, 840
                c.translate(ax, ay)
                c.scale(pop, pop)
                c.translate(-ax, -ay + fy)
                c.save()
                thought_path(c)
                c.clip()
                idx = _page_at(t)
                a, b, fn = IMG_PAGES[idx]
                lt = t - a
                bx0, by0 = cx - rx, cy - ry
                if idx > 0 and lt < 0.45:
                    pa, pb, pfn = IMG_PAGES[idx - 1]
                    c.save()
                    c.translate(bx0, by0)
                    pfn(c, rx * 2, ry * 2, pb - pa - 0.01)
                    c.restore()
                    with group_alpha(c, ease_io(lt / 0.45)):
                        c.save()
                        c.translate(bx0, by0)
                        fn(c, rx * 2, ry * 2, lt)
                        c.restore()
                else:
                    c.save()
                    c.translate(bx0, by0)
                    fn(c, rx * 2, ry * 2, lt)
                    c.restore()
                g = cairo.RadialGradient(cx, cy, ry * 0.55, cx, cy, rx * 1.05)
                g.add_color_stop_rgba(0, 1, 0.98, 0.94, 0)
                g.add_color_stop_rgba(1, 1, 0.98, 0.94, 0.75)
                c.set_source(g)
                c.paint()
                r = random.Random(int(t * 4))
                for k in range(8):
                    star(c, cx + r.uniform(-rx * 0.8, rx * 0.8), cy + r.uniform(-ry * 0.8, ry * 0.8), 3, 0.6, hexc("fff6d0"))
                c.restore()
                thought_path(c)
                c.set_source_rgba(1, 1, 1, 0.5)
                c.set_line_width(14)
                c.stroke()
                spath(c, wob([(cx + math.cos(i / 48 * 2 * math.pi) * rx * (1 + 0.035 * math.cos(i / 48 * 2 * math.pi * 11)),
                               cy + math.sin(i / 48 * 2 * math.pi) * ry * (1 + 0.035 * math.cos(i / 48 * 2 * math.pi * 11)))
                              for i in range(48)], "bubink", 1.2, 40), True)
                c.set_source_rgba(*INK, 0.85)
                c.set_line_width(3)
                c.stroke()
                c.restore()
        if spill > 0:
            with keep():
                aim = math.atan2(960 - (cy + ry), 300 - cx)
                for k in range(7):
                    a0 = aim + (k - 3) * 0.1
                    c.move_to(cx - 120, cy + ry - 30)
                    c.line_to(cx - 120 + math.cos(a0 - 0.04) * 600, cy + ry - 30 + math.sin(a0 - 0.04) * 600)
                    c.line_to(cx - 120 + math.cos(a0 + 0.04) * 600, cy + ry - 30 + math.sin(a0 + 0.04) * 600)
                    c.close_path()
                    c.set_source_rgba(1, 0.95, 0.78, 0.13 * spill)
                    c.fill()
        # 现实中的她：行李箱，工牌
        gx, gy = 300, 1180
        took = ease_io(prog(t, 15.4, 1.0))
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
        girl(c, gx, gy, 1.4, pack=False, hat=True, badge=t < 15.3, look=0.6 if t < 14.6 else 0.2,
             look_up=0.8 if t < 14.6 or t > 16.6 else -0.9, mouth="smile" if t > 2.5 else "o",
             head_down=4 if 14.6 < t < 16.6 else 0, arms=arms, eyes_closed=t > 21.5)
        suitcase(c, gx + 44 * 1.4 + 50, gy + 2, 0.9, "su13", handle=1.0)


# ================================================================ 第四版：拥抱 → 分开 → 红心碎裂
def heart_pts(cx, cy, s, n=40):
    pts = []
    for i in range(n):
        a = i / n * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * s, cy + y * s))
    return pts


ZIG = [(0, -12), (-3, -6), (3, -1), (-2, 5), (2, 10), (0, 16)]


def heart_half(c, cx, cy, s, side, key):
    """沿锯齿裂缝切开的半颗心。side=-1 左半，1 右半。"""
    c.save()
    c.new_path()
    far = -30 if side < 0 else 30
    zz = [(cx + zx * s, cy + zy * s) for zx, zy in ZIG]
    c.move_to(cx + far * s, cy - 30 * s)
    for p in zz:
        c.line_to(*p)
    c.line_to(cx + far * s, cy + 30 * s)
    c.close_path()
    c.clip()
    with keep():
        shape(c, heart_pts(cx, cy, s), RED, key, lw=2.4, amp=0.5)
    c.restore()
    line(c, [(cx + zx * s, cy + zy * s) for zx, zy in ZIG], key + "z", 2.2)


def p1_breakup(c, t):
    with cam(c, 540, 900, 1.05):
        street_bg(c, t, base=760, rain_a=0.3, seed=6)
        apart = ease_io(prog(t, 1.1, 1.5))
        hx, px = lerp(492, 330, apart), lerp(588, 760, apart)
        leave = ease_in(prog(t, 3.4, 1.6))
        px += leave * 600
        y = 1180
        hug = 1 - apart
        her_arms = [(lerp(-26, 30, hug), lerp(-76, -112, hug)), (lerp(26, 46, hug), lerp(-76, -92, hug))]
        his_arms = [(lerp(-26, -46, hug), lerp(-76, -92, hug)), (lerp(26, -30, hug), lerp(-76, -112, hug))]
        if t < 3.4:
            person(c, px, y, 1.7, coat=hexc("8a94a3"), hair=hexc("4a4a4a"), hair_style="short", hat=False, pack=False,
                   look=-0.7, arms=his_arms, key="ex2", mouth="flat", eyes_closed=hug > 0.5)
        else:
            person(c, px, y, 1.7, view="back", coat=hexc("8a94a3"), hair=hexc("4a4a4a"), hair_style="short",
                   hat=False, pack=False, walk=t * 7, key="ex2")
        girl(c, hx, y, 1.6, pack=False, hat=False, look=0.7 if t < 3.6 else 0.2, arms=her_arms,
             mouth="smile" if hug > 0.5 else "flat", eyes_closed=hug > 0.5, head_down=0 if t < 3.0 else 5,
             look_up=0 if t < 3.0 else -0.8)
        # 红心：拥抱时浮在头顶，分开时被拉长成红线，然后裂开
        hcx = (hx + min(px, 760)) / 2
        hcy = 760 + math.sin(t * 2.4) * 8
        crack = prog(t, 2.55, 0.3)
        fall = ease_in(prog(t, 2.9, 1.0))
        beat = 1 + 0.06 * math.sin(t * 7) * (1 - apart)
        with keep():
            if t < 2.9:
                stretch = apart
                if stretch > 0:
                    for k, ax in enumerate((hx + 20, min(px, 760) - 20)):
                        line(c, [(ax, 1000), (lerp(ax, hcx, 0.5), lerp(1000, hcy, 0.5) + 30 * (1 - stretch)), (hcx, hcy)],
                             f"thr{k}", 3 + 2 * stretch, RED)
                glow(c, hcx, hcy, 160, hexc("ff8a80"), 0.35)
                c.save()
                c.translate(hcx, hcy)
                c.scale(beat * (1 + 0.25 * stretch), beat * (1 - 0.15 * stretch))
                c.translate(-hcx, -hcy)
                shape(c, heart_pts(hcx, hcy, 4.2), RED, "bheart", lw=2.6, amp=0.5)
                if crack > 0:
                    zz = [(hcx + zx * 4.2, hcy + zy * 4.2) for zx, zy in ZIG]
                    n = max(2, int(round(1 + crack * (len(zz) - 1))))
                    line(c, zz[:n], "bcrack", 3)
                c.restore()
            else:
                for side in (-1, 1):
                    c.save()
                    ox = hcx + side * (20 + 80 * fall)
                    oy = lerp(hcy, 1170, fall)
                    c.translate(ox, oy)
                    c.rotate(side * fall * 1.4)
                    c.translate(-hcx, -hcy)
                    heart_half(c, hcx, hcy, 4.2, side, f"hh{side}")
                    c.restore()
                if fall < 1:
                    r = random.Random(5)
                    for k in range(8):
                        sx_ = hcx + r.uniform(-40, 40) + fall * r.uniform(-120, 120)
                        sy_ = lerp(hcy, 1160, fall * r.uniform(0.7, 1.0))
                        shape(c, [(sx_, sy_), (sx_ + 8, sy_ + 3), (sx_ + 2, sy_ + 9)], RED, f"shd{k}", lw=1.2, amp=0.3)


# ================================================================ 第四版：日程表停 5 秒
def party_schedule(c, t):
    fill_all(c, hexc("e9e3d6"))
    shape(c, rect(110, 140, 860, 1080), hexc("f6f1e4"), "nb", lw=3)
    for k in range(18):
        line(c, [(140, 260 + k * 52), (940, 260 + k * 52)], f"nbl{k}", 1.2, hexc("c9c0ac"), alpha=0.7)
    line(c, [(250, 160), (250, 1200)], "nbm", 1.6, hexc("d9a49a"))
    text(c, "这一周", 540, 225, 54, INK)
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    plans = ["舞蹈课", "健身", "喝酒", "聚餐", "蹦迪", "看演出", "再约"]
    for i, (d, pl) in enumerate(zip(days, plans)):
        y = 330 + i * 120
        text(c, d, 190, y, 40, INK, a=0.85)
        a = clamp((t - 0.1 - i * 0.26) / 0.2)
        if a > 0:
            text(c, pl, 290, y, 48, INK, a=a, anchor="l")
    extras = [("+ 加班后再喝一杯", 560, 455, -0.06), ("+ 通宵！", 640, 695, 0.08), ("+ 续摊", 600, 935, -0.1),
              ("满了", 760, 1160, -0.15)]
    for k, (tx_, x, y, rot) in enumerate(extras):
        a = clamp((t - 2.1 - k * 0.38) / 0.18)
        if a > 0:
            c.save()
            c.translate(x, y)
            c.rotate(rot)
            text(c, tx_, 0, 0, 38 if k < 3 else 64, hexc("b5473c"), a=a, anchor="l")
            c.restore()
    if t > 3.4:
        a = ease_io(prog(t, 3.4, 0.4))
        c.save()
        c.translate(760, 1160)
        c.rotate(-0.15)
        shape(c, ell(60, -20, 90, 46, 20), None, "mancir", lw=3.4, alpha=a)
        c.restore()


PARTY_CUTS = [0.0, 5.0, 6.35, 7.7, 9.0]


def s05_party(c, t):
    i = max(j for j in range(4) if t >= PARTY_CUTS[j])
    lt = t - PARTY_CUTS[i]
    k = 1 + 0.06 * (1 - ease_out(prog(lt, 0, 0.3)))
    if i == 0:
        k = 1 + 0.05 * ease_io(lt / 5.0)
    with cam(c, 540, 960, k):
        [party_schedule, party_dance, party_club, party_bar][i](c, lt + (0 if i == 0 else i))
    fl = 1 - ease_out(prog(lt, 0, 0.18))
    if i > 0 and fl > 0:
        with keep():
            c.set_source_rgba(1, 1, 1, 0.5 * fl)
            c.paint()


# ================================================================ 第四版：更丰富的立体书四景
@contextmanager
def layer(c, x, y, w, h, lt, d):
    k = ease_back(prog(lt, 0.15 + d, 0.45))
    c.save()
    c.translate(x + w / 2, y + h)
    c.scale(1, max(k, 0.001))
    c.translate(-(x + w / 2), -(y + h))
    yield k > 0.01
    c.restore()


def pine(c, x, base, s, key, col=hexc("2f5a4a")):
    shape(c, rect(x - 3 * s, base - 14 * s, 6 * s, 14 * s), hexc("6b4a35"), key + "t", lw=1.4, amp=0.3)
    for j in range(3):
        yy = base - 12 * s - j * 16 * s
        ww = (26 - j * 6) * s
        shape(c, [(x - ww, yy), (x, yy - 26 * s), (x + ww, yy)], col, f"{key}{j}", lw=1.4, amp=0.4)
        shape(c, [(x - ww * 0.35, yy - 17 * s), (x, yy - 26 * s), (x + ww * 0.35, yy - 17 * s)], (0.97, 0.97, 0.98),
              f"{key}s{j}", ink=False)


def q_snow(c, x, y, w, h, t, lt=9):
    vgrad(c, y, y + h, [(0, hexc("16204a")), (0.6, hexc("2f4680")), (1, hexc("5d78ad"))], x, x + w)
    r = random.Random(11)
    for k in range(34):
        star(c, x + r.uniform(0, w), y + r.uniform(0, h * 0.5), r.uniform(1.4, 2.6), 0.5 + 0.5 * math.sin(t * 3 + k))
    for k, col in enumerate((hexc("6ff0b0"), hexc("8fd6ff"), hexc("c49bff"))):
        for i in range(70):
            xx = x + w * i / 70
            top = y + h * (0.08 + 0.07 * k) + math.sin(i * 0.18 + t * 1.3 + k * 1.7) * 16
            ln = 40 + 30 * math.sin(i * 0.4 + t * 2 + k)
            c.move_to(xx, top)
            c.line_to(xx, top + ln)
            c.set_source_rgba(*G(col)[:3], 0.22)
            c.set_line_width(w / 70 + 1)
            c.stroke()
    with layer(c, x, y, w, h, lt, 0.0) as on:
        if on:
            for k, (fx, fw, fh) in enumerate(((0.18, 0.5, 0.62), (0.55, 0.6, 0.72), (0.9, 0.45, 0.55))):
                mountain(c, x + w * fx, y + h * 0.78, w * fw, h * fh, hexc("8fa6cf"), f"sm{k}")
    with layer(c, x, y, w, h, lt, 0.12) as on:
        if on:
            for k, (fx, fw, fh) in enumerate(((0.32, 0.55, 0.5), (0.75, 0.5, 0.42))):
                mx, base, mw, mh = x + w * fx, y + h * 0.82, w * fw, h * fh
                mountain(c, mx, base, mw, mh, hexc("c6d3ea"), f"sn{k}")
                shape(c, [(mx, base - mh), (mx + mw * 0.16, base - mh * 0.78), (mx + mw / 2, base), (mx + mw * 0.05, base)],
                      (0.4, 0.48, 0.66, 0.35), f"snsh{k}", ink=False)
    with layer(c, x, y, w, h, lt, 0.24) as on:
        if on:
            for k in range(11):
                px = x + 14 + k * (w - 28) / 10
                pine(c, px, y + h * 0.86 + (k % 2) * 6, 0.9 + 0.25 * ((k * 7) % 3) / 2, f"pn{k}")
    with layer(c, x, y, w, h, lt, 0.32) as on:
        if on:
            cx_, cy_ = x + w * 0.62, y + h * 0.86
            shape(c, rect(cx_ - 34, cy_ - 40, 68, 40), hexc("8a5a3a"), "cab", lw=1.8)
            shape(c, [(cx_ - 42, cy_ - 40), (cx_, cy_ - 68), (cx_ + 42, cy_ - 40)], (0.97, 0.97, 0.98), "cabr", lw=1.8)
            with keep():
                glow(c, cx_ - 10, cy_ - 22, 40, hexc("ffd27a"), 0.9)
                shape(c, rect(cx_ - 20, cy_ - 30, 20, 16), hexc("ffd98a"), "cabw", lw=1.4, amp=0.3)
            shape(c, rect(cx_ + 14, cy_ - 74, 10, 20), hexc("6b4a35"), "chim", lw=1.4, amp=0.3)
            for k in range(4):
                ph = (t * 0.5 + k * 0.25) % 1
                cloud(c, cx_ + 19 + ph * 30, cy_ - 80 - ph * 60, 0.12 + ph * 0.15, f"smk{k}", a=0.7 * (1 - ph))
    with layer(c, x, y, w, h, lt, 0.4) as on:
        if on:
            shape(c, ell(x + w * 0.3, y + h * 0.95, w * 0.34, h * 0.07, 22), hexc("b5cbe3"), "lake", lw=1.8)
            for k, col in enumerate((hexc("6ff0b0"), hexc("8fd6ff"))):
                line(c, [(x + w * (0.12 + k * 0.1), y + h * 0.94), (x + w * (0.4 + k * 0.1), y + h * 0.95)], f"lr{k}", 3, col,
                     alpha=0.6)
    for layer_k, (sp, sz) in enumerate(((30, 1.6), (60, 2.6))):
        rr = random.Random(20 + layer_k)
        for k in range(16):
            sx_ = x + rr.uniform(0, w) + math.sin(t + k) * 8
            sy_ = y + (rr.uniform(0, h) + t * sp) % h
            circle(c, sx_, sy_, sz, (1, 1, 1), 0.85)


def q_sea(c, x, y, w, h, t, lt=9):
    vgrad(c, y, y + h * 0.45, [(0, hexc("7cc6ee")), (1, hexc("e6f6fb"))], x, x + w)
    glow(c, x + w * 0.82, y + h * 0.14, 70, hexc("fff6c8"), 0.9)
    circle(c, x + w * 0.82, y + h * 0.14, 20, hexc("fff3c0"))
    for k in range(2):
        cloud(c, x + w * (0.2 + 0.35 * k) + t * 8, y + h * (0.12 + 0.06 * k), 0.45, f"sc{k}")
    for k in range(3):
        gx = x + ((k * 130 + t * 50) % (w + 60)) - 30
        gy = y + h * 0.22 + k * 14 + math.sin(t * 2 + k) * 4
        f = math.sin(t * 9 + k)
        line(c, [(gx - 9, gy - 4 * f), (gx, gy), (gx + 9, gy - 4 * f)], f"gull{k}", 2)
    vgrad(c, y + h * 0.42, y + h, [(0, hexc("5aa6cf")), (1, hexc("1f5f8f"))], x, x + w)
    with layer(c, x, y, w, h, lt, 0.0) as on:
        if on:
            bx = x + w * 0.25 + math.sin(t * 0.4) * 10
            shape(c, [(bx - 18, y + h * 0.46), (bx + 18, y + h * 0.46), (bx + 12, y + h * 0.5), (bx - 12, y + h * 0.5)],
                  hexc("f4efe6"), "sbt", lw=1.4, amp=0.3)
            shape(c, [(bx, y + h * 0.36), (bx, y + h * 0.455), (bx + 16, y + h * 0.455)], (1, 1, 1), "ssl", lw=1.4, amp=0.3)
    with layer(c, x, y, w, h, lt, 0.12) as on:
        if on:
            rx_ = x + w * 0.8
            shape(c, [(rx_ - 70, y + h * 0.66), (rx_ - 50, y + h * 0.52), (rx_ + 10, y + h * 0.48), (rx_ + 70, y + h * 0.56),
                      (rx_ + 90, y + h * 0.66)], hexc("6d6a6a"), "rock", lw=2)
            lx, lb = rx_ + 10, y + h * 0.5
            for j in range(4):
                shape(c, [(lx - 14 + j * 1.5, lb - j * 22), (lx + 14 - j * 1.5, lb - j * 22),
                          (lx + 12.5 - j * 1.5, lb - (j + 1) * 22), (lx - 12.5 + j * 1.5, lb - (j + 1) * 22)],
                      hexc("d1553f") if j % 2 == 0 else (0.98, 0.97, 0.94), f"lhb{j}", lw=1.6, amp=0.3)
            shape(c, rect(lx - 10, lb - 108, 20, 20), hexc("fff3c0"), "lhl", lw=1.6, amp=0.3)
            shape(c, [(lx - 13, lb - 108), (lx, lb - 122), (lx + 13, lb - 108)], hexc("3a3a3a"), "lhr", lw=1.4, amp=0.3)
            with keep():
                ang = t * 1.6
                c.move_to(lx, lb - 98)
                c.line_to(lx + math.cos(ang - 0.12) * 260, lb - 98 + math.sin(ang - 0.12) * 40)
                c.line_to(lx + math.cos(ang + 0.12) * 260, lb - 98 + math.sin(ang + 0.12) * 40)
                c.close_path()
                c.set_source_rgba(1, 0.97, 0.75, 0.35)
                c.fill()
    with layer(c, x, y, w, h, lt, 0.2) as on:
        if on:
            for k in range(4):
                yy = y + h * (0.56 + k * 0.06)
                pts = [(x + w * i / 14, yy + math.sin(i * 1.3 + t * 2.5 + k) * 4) for i in range(15)]
                line(c, pts, f"mw{k}", 2, (1, 1, 1), alpha=0.6)
    with layer(c, x, y, w, h, lt, 0.28) as on:
        if on:
            wx, wy = x + w * 0.38, y + h * 0.72
            ph = (t * 0.45) % 1
            rise = math.sin(ph * math.pi)
            ty_ = wy - rise * 70
            shape(c, [(wx - 8, wy), (wx - 6, ty_ + 20), (wx - 48, ty_ - 6), (wx - 12, ty_ + 2), (wx, ty_ - 16),
                      (wx + 12, ty_ + 2), (wx + 48, ty_ - 6), (wx + 6, ty_ + 20), (wx + 8, wy)], hexc("2c3f5a"), "wtail", lw=2)
            if rise > 0.3:
                rr = random.Random(int(t * 10))
                for k in range(10):
                    circle(c, wx + rr.uniform(-40, 40), wy - rr.uniform(0, 30) * rise, rr.uniform(2, 4), (1, 1, 1), 0.9)
            sp = (t * 0.7) % 1
            for k in range(7):
                a = -math.pi / 2 + (k - 3) * 0.25
                circle(c, x + w * 0.62 + math.cos(a) * 40 * sp, y + h * 0.66 + math.sin(a) * 60 * sp + 40 * sp * sp,
                       3, (0.92, 0.97, 1), 1 - sp)
    with layer(c, x, y, w, h, lt, 0.38) as on:
        if on:
            for row in range(2):
                yy = y + h * (0.86 + row * 0.08)
                for k in range(6):
                    cx_ = x + (k + 0.5 * row) * w / 5 + math.sin(t * 2 + k) * 6
                    shape(c, [(cx_ - 46, yy + 14), (cx_ - 30, yy - 10), (cx_, yy - 22), (cx_ + 24, yy - 14), (cx_ + 14, yy - 4),
                              (cx_ + 46, yy + 14)], hexc("2f78a8"), f"cw{row}{k}", lw=1.8, amp=0.5)
                    for j in range(4):
                        circle(c, cx_ - 4 + j * 7, yy - 18 + j * 3, 4, (1, 1, 1), 0.95)
            rr = random.Random(4)
            for k in range(20):
                gx = x + rr.uniform(0, w)
                gy = y + h * rr.uniform(0.6, 0.8)
                line(c, [(gx, gy), (gx + 10, gy)], f"gl{k}", 2, hexc("fff3c0"), alpha=0.5 + 0.5 * math.sin(t * 5 + k))


def camel(c, x, base, s, t, key, rider=False):
    col = hexc("5a3a2a")
    c.save()
    c.translate(x, base)
    c.scale(s, s)
    shape(c, ell(0, -24, 24, 10, 16), col, key + "b", lw=1.4, amp=0.3)
    shape(c, ell(-4, -34, 9, 8, 10), col, key + "h1", lw=1.2, amp=0.3)
    shape(c, ell(8, -33, 8, 7, 10), col, key + "h2", lw=1.2, amp=0.3)
    line(c, [(20, -26), (30, -42), (36, -42)], key + "n", 4, col)
    for k, lx in enumerate((-16, -8, 10, 18)):
        sw = math.sin(t * 6 + k * 1.6) * 4
        line(c, [(lx, -18), (lx + sw, 0)], f"{key}l{k}", 2.4, col)
    if rider:
        shape(c, ell(-2, -46, 6, 9, 10), hexc("8c4a3a"), key + "r", lw=1.2, amp=0.3)
        circle(c, -2, -58, 5, hexc("e8c09a"))
    c.restore()


def palm(c, x, base, s, key):
    c.save()
    c.translate(x, base)
    c.scale(s, s)
    line(c, [(0, 0), (4, -30), (2, -60)], key + "t", 5, hexc("8a5a3a"))
    for k in range(6):
        a = math.pi + k * math.pi / 5
        line(c, [(2, -60), (2 + math.cos(a) * 20, -60 + math.sin(a) * 12 - 6), (2 + math.cos(a) * 36, -60 + math.sin(a) * 4 + 10)],
             f"{key}f{k}", 4, hexc("3f7a3a"))
    c.restore()


def q_desert(c, x, y, w, h, t, lt=9):
    vgrad(c, y, y + h * 0.62, [(0, hexc("e8706a")), (0.45, hexc("f6a96a")), (1, hexc("fde2b0"))], x, x + w)
    sx_, sy_ = x + w * 0.6, y + h * 0.42
    with keep():
        for k in range(14):
            a = k * math.pi / 7 + t * 0.05
            c.move_to(sx_, sy_)
            c.line_to(sx_ + math.cos(a - 0.05) * w, sy_ + math.sin(a - 0.05) * w)
            c.line_to(sx_ + math.cos(a + 0.05) * w, sy_ + math.sin(a + 0.05) * w)
            c.close_path()
            c.set_source_rgba(1, 0.92, 0.7, 0.12)
            c.fill()
    glow(c, sx_, sy_, h * 0.42, hexc("fff0c0"), 0.8)
    circle(c, sx_, sy_, h * 0.17, hexc("fff2c8"))

    def dune(key, base, amp, phase, light, dark):
        pts = [(x - 10, y + h + 10)]
        ridge = []
        for i in range(25):
            xx = x - 10 + (w + 20) * i / 24
            yy = base - amp * (0.5 + 0.5 * math.sin(xx * 0.018 + phase))
            pts.append((xx, yy))
            ridge.append((xx, yy))
        pts.append((x + w + 10, y + h + 10))
        shape(c, pts, light, key, lw=1.8, amp=0.6)
        lee = [(xx + 6, yy + 6) for xx, yy in ridge]
        lee_pts = [(x - 10, y + h + 10)] + [(xx, yy + 18) for xx, yy in lee] + [(x + w + 10, y + h + 10)]
        g = cairo.LinearGradient(0, base - amp, 0, base + 40)
        dk = G(dark)[:3]
        g.add_color_stop_rgba(0, *dk, 0.0)
        g.add_color_stop_rgba(0.5, *dk, 0.28)
        g.add_color_stop_rgba(1, *dk, 0.0)
        spath(c, lee_pts, True)
        c.set_source(g)
        c.fill()
        for j in range(3):
            pts2 = [(xx, yy + 14 + j * 10 + math.sin(xx * 0.05 + j) * 2) for xx, yy in ridge[1:-1]]
            line(c, pts2, f"{key}rp{j}", 1.1, dark, alpha=0.35)
        return ridge

    with layer(c, x, y, w, h, lt, 0.0) as on:
        if on:
            dune("d0", y + h * 0.6, 26, 0.5, hexc("efb879"), hexc("c98a4a"))
    with layer(c, x, y, w, h, lt, 0.12) as on:
        if on:
            ridge = dune("d1", y + h * 0.72, 40, 2.1, hexc("f2c27e"), hexc("b97a3e"))
    with layer(c, x, y, w, h, lt, 0.24) as on:
        if on:
            for k in range(4):
                u = ((t * 0.03 + k * 0.12) % 1.0)
                cxp = x + w * (0.15 + k * 0.13) + t * 6 % 30
                base = y + h * 0.72 - 40 * (0.5 + 0.5 * math.sin(cxp * 0.018 + 2.1))
                shape(c, ell(cxp + 30, base + 2, 34, 4, 12), (0.45, 0.25, 0.15, 0.35), f"csh{k}", ink=False)
                camel(c, cxp, base, 0.9, t + k, f"cm{k}", rider=k == 0)
    with layer(c, x, y, w, h, lt, 0.32) as on:
        if on:
            shape(c, ell(x + w * 0.16, y + h * 0.9, w * 0.13, h * 0.05, 16), hexc("4fa3b8"), "oasis", lw=1.8)
            for k, (fx, s) in enumerate(((0.08, 1.0), (0.2, 0.85), (0.28, 0.7))):
                palm(c, x + w * fx, y + h * 0.9, s, f"palm{k}")
    with layer(c, x, y, w, h, lt, 0.4) as on:
        if on:
            dune("d2", y + h * 0.94, 20, 4.0, hexc("f5d095"), hexc("c98a4a"))
            for k in range(5):
                yy = y + h * (0.95 + k * 0.012)
                line(c, [(x + w * (0.4 + 0.03 * k), yy), (x + w * 0.6, yy - 4), (x + w * (0.9 - 0.02 * k), yy)], f"rip{k}", 1.2,
                     hexc("c98a4a"), alpha=0.6)


def monstera(c, x, y, s, rot, key, col=hexc("2f7a4a")):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    shape(c, ell(0, 0, 50, 40, 22), col, key, lw=2, amp=0.6)
    for k in range(-2, 3):
        a = k * 0.45
        line(c, [(math.cos(a) * 22, math.sin(a) * 17), (math.cos(a) * 50, math.sin(a) * 40)], f"{key}c{k}", 3.2, hexc("7fbf8a"),
             alpha=0.9)
    line(c, [(-50, 0), (50, 0)], key + "m", 1.6, hexc("1f5a35"))
    c.restore()


def hibiscus(c, x, y, s, key):
    for k in range(5):
        a = k * 2 * math.pi / 5
        shape(c, ell(x + math.cos(a) * 9 * s, y + math.sin(a) * 9 * s, 9 * s, 6 * s, 10), hexc("e0403a"), f"{key}{k}", lw=1.2, amp=0.3)
    circle(c, x, y, 3 * s, hexc("ffd34f"))


def q_forest(c, x, y, w, h, t, lt=9):
    vgrad(c, y, y + h, [(0, hexc("d8eecc")), (1, hexc("8fca94"))], x, x + w)
    with keep():
        for k in range(4):
            x0 = x + w * (0.1 + 0.22 * k)
            c.move_to(x0, y)
            c.line_to(x0 + 40, y)
            c.line_to(x0 + 140, y + h)
            c.line_to(x0 + 70, y + h)
            c.close_path()
            c.set_source_rgba(1, 1, 0.92, 0.16)
            c.fill()
    with layer(c, x, y, w, h, lt, 0.0) as on:
        if on:
            for k in range(9):
                shape(c, ell(x + k * w / 8, y + h * 0.42, 50, 60, 16), hexc("2f6a4a"), f"fc0{k}", lw=1.6, amp=1)
    with layer(c, x, y, w, h, lt, 0.1) as on:
        if on:
            for k in range(8):
                shape(c, ell(x + 30 + k * w / 7, y + h * 0.56, 46, 50, 16), hexc("4f8a5a"), f"fc1{k}", lw=1.6, amp=1)
    with layer(c, x, y, w, h, lt, 0.18) as on:
        if on:
            fx0 = x + w * 0.56
            shape(c, [(fx0 - 40, y + h * 0.2), (fx0 + 120, y + h * 0.18), (fx0 + 130, y + h * 0.8), (fx0 - 50, y + h * 0.8)],
                  hexc("6f8a6a"), "cliff", lw=2)
            shape(c, rect(fx0 + 10, y + h * 0.2, 60, h * 0.62), hexc("e6f6fb"), "wfall", lw=1.6, amp=0.4)
            for k in range(7):
                yy = y + h * 0.2 + ((t * 140 + k * h * 0.09) % (h * 0.62))
                line(c, [(fx0 + 16 + (k % 3) * 18, yy), (fx0 + 16 + (k % 3) * 18, yy + 22)], f"wf{k}", 2.4, hexc("9fd3e6"))
            with keep():
                glow(c, fx0 + 40, y + h * 0.8, 90, (1, 1, 1), 0.7)
                for j, col in enumerate((hexc("ff6b6b"), hexc("ffd34f"), hexc("6fd38a"), hexc("6fb7ff"), hexc("b08bff"))):
                    c.new_path()
                    c.arc(fx0 + 40, y + h * 0.84, 70 - j * 5, math.pi * 1.1, math.pi * 1.9)
                    c.set_source_rgba(*col, 0.45)
                    c.set_line_width(4)
                    c.stroke()
    with layer(c, x, y, w, h, lt, 0.26) as on:
        if on:
            pts = [(x - 10, y + h + 10), (x - 10, y + h * 0.88)]
            pts += [(x + w * i / 10, y + h * 0.86 + math.sin(i * 0.9) * 8) for i in range(11)]
            pts += [(x + w + 10, y + h + 10)]
            shape(c, pts, hexc("5fa8c8"), "river", lw=1.8)
            for k in range(3):
                line(c, [(x + w * (0.1 + 0.3 * k) + (t * 30) % 40, y + h * 0.93), (x + w * (0.18 + 0.3 * k) + (t * 30) % 40, y + h * 0.93)],
                     f"rv{k}", 2, (1, 1, 1), alpha=0.7)
    with layer(c, x, y, w, h, lt, 0.32) as on:
        if on:
            for k in range(5):
                vx = x + w * (0.08 + 0.2 * k)
                vl = h * (0.3 + 0.12 * (k % 3))
                pts = [(vx + math.sin(j * 0.8 + t + k) * 6, y + vl * j / 6) for j in range(7)]
                line(c, pts, f"vn{k}", 2.4, hexc("3f6a2a"))
                for j in range(1, 6, 2):
                    shape(c, ell(pts[j][0] + 6, pts[j][1], 6, 3.5, 8), hexc("5f9a4a"), f"vl{k}{j}", lw=1, amp=0.3)
            monstera(c, x + w * 0.1, y + h * 0.8, 1.1, -0.5 + math.sin(t) * 0.04, "ms1")
            monstera(c, x + w * 0.92, y + h * 0.78, 1.0, 0.6 + math.sin(t + 1) * 0.04, "ms2", hexc("3f8a4f"))
            for k, (fx, fy, rot) in enumerate(((0.3, 0.95, -0.3), (0.75, 0.97, 0.4))):
                c.save()
                c.translate(x + w * fx, y + h * fy)
                c.rotate(rot)
                shape(c, ell(0, 0, 80, 18, 18), hexc("4f9a4a"), f"bn{k}", lw=1.8)
                line(c, [(-78, 0), (78, 0)], f"bnm{k}", 1.4, hexc("2f6a2a"))
                c.restore()
    with layer(c, x, y, w, h, lt, 0.4) as on:
        if on:
            for k, (fx, fy) in enumerate(((0.22, 0.86), (0.4, 0.92), (0.84, 0.9))):
                hibiscus(c, x + w * fx, y + h * fy, 1.2, f"hb{k}")
    px = x + w * (0.05 + 0.9 * ((t * 0.18) % 1))
    py = y + h * 0.3 + math.sin(t * 3) * 10
    flap = math.sin(t * 12)
    shape(c, ell(px, py, 18, 9, 12), hexc("1f1f24"), "tcb", lw=1.2, amp=0.3)
    shape(c, [(px + 14, py - 4), (px + 40, py), (px + 14, py + 4)], hexc("f08a2a"), "tbk", lw=1.2, amp=0.3)
    shape(c, [(px - 6, py), (px + 4, py - 20 * flap), (px + 10, py)], hexc("1f1f24"), "tw", lw=1, amp=0.3)
    for k in range(3):
        bx = x + w * (0.2 + 0.25 * k) + math.sin(t * 1.3 + k * 2) * 30
        by = y + h * (0.6 + 0.08 * k) + math.cos(t * 1.7 + k) * 20
        f = abs(math.sin(t * 14 + k))
        col = [hexc("ffd34f"), hexc("6fb7ff"), hexc("ff8ab5")][k]
        shape(c, [(bx, by), (bx - 10, by - 10 * f - 2), (bx - 12, by + 4)], col, f"bf{k}a", lw=1, amp=0.2)
        shape(c, [(bx, by), (bx + 10, by - 10 * f - 2), (bx + 12, by + 4)], col, f"bf{k}b", lw=1, amp=0.2)


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
            t0 = 0.9 + k * 0.55
            kk = ease_back(prog(quad_t, t0, 0.5))
            if kk <= 0.01:
                continue
            qx, qy = cells[k]
            c.rectangle(qx + 8, qy + 10, qw, qh)
            c.set_source_rgba(0, 0, 0, 0.18 * min(kk, 1))
            c.fill()
            with popup(c, qx + qw / 2, qy + qh, kk):
                c.save()
                c.rectangle(qx, qy, qw, qh)
                c.clip()
                fn(c, qx, qy, qw, qh, t, quad_t - t0)
                c.restore()
                shape(c, rect(qx, qy, qw, qh), None, f"qf{k}", lw=2.6)
            line(c, [(qx, qy + qh), (qx + qw, qy + qh)], f"fold{k}", 1.6, hexc("8c6f4a"), alpha=0.7)
            with keep():
                _icon(c, icon, qx + 26, qy + 26, 1.3)
        c.restore()


# ================================================================ 第五版：周五 吃饭 → 喝酒 → 唱 K 通宵
FRIENDS = [dict(coat=hexc("8a94a3"), hair=hexc("3a3a3a"), hair_style="short"),
           dict(coat=hexc("b59a8a"), hair=hexc("5a3a2a"), hair_style="bun"),
           dict(coat=hexc("9aa48a"), hair=hexc("2f2a28"), hair_style="sweep"),
           dict(coat=hexc("a08aa8"), hair=hexc("4a3a33"), hair_style="short")]


def friend(c, i, x, y, s, **kw):
    d = dict(FRIENDS[i % len(FRIENDS)])
    d.update(hat=False, pack=False, key=f"fr{i}")
    d.update(kw)
    person(c, x, y, s, **d)


def party_schedule(c, t):
    fill_all(c, hexc("e9e3d6"))
    shape(c, rect(110, 140, 860, 1080), hexc("f6f1e4"), "nb", lw=3)
    for k in range(18):
        line(c, [(140, 260 + k * 52), (940, 260 + k * 52)], f"nbl{k}", 1.2, hexc("c9c0ac"), alpha=0.7)
    line(c, [(250, 160), (250, 1200)], "nbm", 1.6, hexc("d9a49a"))
    text(c, "这一周", 540, 225, 54, INK)
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    plans = ["舞蹈课", "健身", "蹦迪", "Live", "吃饭 → 喝酒 → 唱K通宵", "补觉", "再约"]
    for i, (d, pl) in enumerate(zip(days, plans)):
        y = 330 + i * 120
        text(c, d, 190, y, 40, INK, a=0.85)
        a = clamp((t - 0.1 - i * 0.26) / 0.2)
        if a > 0:
            text(c, pl, 290, y, 48 if i != 4 else 44, INK, a=a, anchor="l")
    extras = [("+ 加班后再喝一杯", 560, 455, -0.06), ("通宵！", 820, 760, 0.12), ("+ 续摊", 560, 1055, -0.1),
              ("满了", 760, 1160, -0.15)]
    for k, (tx_, x, y, rot) in enumerate(extras):
        a = clamp((t - 2.1 - k * 0.38) / 0.18)
        if a > 0:
            c.save()
            c.translate(x, y)
            c.rotate(rot)
            text(c, tx_, 0, 0, 38 if k < 3 else 64, hexc("b5473c"), a=a, anchor="l")
            c.restore()
    if t > 2.0:
        a = ease_io(prog(t, 2.0, 0.4))
        c.save()
        c.translate(560, 800)
        shape(c, ell(0, 0, 330, 44, 24), None, "fricir", lw=3.2, alpha=a)
        c.restore()
    if t > 3.4:
        a = ease_io(prog(t, 3.4, 0.4))
        c.save()
        c.translate(760, 1160)
        c.rotate(-0.15)
        shape(c, ell(60, -20, 90, 46, 20), None, "mancir", lw=3.4, alpha=a)
        c.restore()


def party_club(c, t, fade=0.0, still=False, neon_on=6):
    fill_all(c, hexc("2b2a33"))
    beams(c, t, 540, 120, n=7, a=0.3)
    with keep():
        glow(c, 540, 140, 120, (1, 1, 1), 0.5)
    shape(c, ell(540, 140, 46, 46, 18), hexc("c8c8d0"), "ball", lw=2.4)
    line(c, [(540, 0), (540, 94)], "ballr", 3)
    shape(c, rect(-200, 1100, 1500, 900), hexc("3a3844"), "cfl", lw=3)
    r = random.Random(9)
    for i in range(16):
        x = r.uniform(-40, W + 40)
        y = r.uniform(1050, 1250)
        hop = -abs(math.sin(t * 8 + i)) * 25
        silhouette(c, x, y + hop, r.uniform(1.4, 1.9), f"cr{i}", col=hexc("5a5866"), a=0.9)
    hop = -abs(math.sin(t * 8)) * 40
    girl(c, 540, 1180 + hop, 1.7, pack=False, hat=False, arms=[(-30, -150), (30, -150)], mouth="laugh", look_up=0.4)


def party_hotpot(c, t):
    fill_all(c, hexc("d8c9b0"))
    for k in range(6):
        with keep():
            glow(c, 160 + k * 160, 140, 90, hexc("ffcf7a"), 0.5)
        line(c, [(160 + k * 160, 0), (160 + k * 160, 110)], f"lan{k}", 2)
        shape(c, ell(160 + k * 160, 140, 26, 32, 14), hexc("c9473b"), f"lanb{k}", lw=2)
    seats = [(200, 0), (380, None), (700, 1), (880, 2)]
    for x, fi in seats:
        if fi is None:
            girl(c, x, 1000, 1.6, sit=True, legs=False, pack=False, hat=False, mouth="laugh", look=0.6,
                 arms=[(-20, -60), (46, -96 + 10 * math.sin(t * 8))])
        else:
            friend(c, fi, x, 1000, 1.6, sit=True, legs=False, mouth="laugh", look=0.6 if x < 540 else -0.6,
                   arms=[(-30 if x > 540 else 30, -60), (-46 if x > 540 else 46, -96 + 10 * math.sin(t * 8 + fi))])
    shape(c, ell(540, 1010, 460, 70, 30), hexc("8c5a3c"), "htab", lw=3)
    shape(c, ell(540, 980, 150, 40, 24), hexc("7a7a80"), "pot", lw=3)
    with keep():
        shape(c, ell(540, 972, 132, 30, 24), hexc("d9452f"), "broth", lw=2, amp=0.6)
        for k in range(10):
            ph = (t * 1.6 + k * 0.1) % 1
            circle(c, 460 + k * 17, 972 + math.sin(k) * 10, 3 + 5 * ph, hexc("f07a4a"), 1 - ph)
    for k in range(5):
        ph = (t * 0.8 + k * 0.2) % 1
        sx_ = 450 + k * 45 + math.sin(ph * 6 + k) * 12
        line(c, [(sx_, 940), (sx_ - 10, 880 - ph * 120), (sx_ + 6, 800 - ph * 160)], f"hst{k}", 3, (1, 1, 1), alpha=0.6 * (1 - ph))
    for k in range(4):
        cx_ = [300, 450, 640, 780][k]
        line(c, [(cx_, 860), (540 + (k - 1.5) * 40, 960)], f"chop{k}", 3, hexc("c9a46a"))


def party_ktv(c, t, dawn=0.0, fade=0.0, neon_on=6, leave=0.0):
    fill_all(c, hexc("2e2638"))
    with keep():
        beams(c, t, 540, 60, n=5, a=0.18 * (1 - dawn * 0.6) * (1 - fade))
    shape(c, rect(170, 120, 740, 420), hexc("1a1a22"), "screen", lw=4)
    with keep():
        g = cairo.LinearGradient(0, 130, 0, 530)
        g.add_color_stop_rgb(0, *hexc("3a4f9a"))
        g.add_color_stop_rgb(1, *hexc("8a4f9a"))
        c.set_source(g)
        c.rectangle(185, 135, 710, 390)
        c.fill()
        if fade < 0.5:
            for k in range(2):
                y_ = 400 + k * 60
                text(c, ["啦 啦 啦 ～ 再唱一首", "我们 一直 唱到 天亮"][(k + int(t * 0.8)) % 2], 540, y_, 40, (1, 1, 1), a=0.9)
            px = 300 + ((t * 160) % 480)
            circle(c, px, 360 - abs(math.sin(t * 6)) * 20, 9, hexc("ffd34f"))
        else:
            text(c, "下一首……", 540, 350, 52, (1, 1, 1), a=0.8)
    neon_sign(c, t, on=neon_on, cx=540, cy=640, size=70)
    shape(c, rect(-200, 1080, 1500, 900), hexc("3a3040"), "kfl", lw=3)
    shape(c, rrect(60, 930, 960, 120, 20), hexc("6a3a5a"), "sofa", lw=3)
    if dawn > 0:
        with keep():
            shape(c, rect(930, 120, 130, 760), hexc("2a2230"), "kwin", lw=3)
            g = cairo.LinearGradient(0, 120, 0, 880)
            g.add_color_stop_rgba(0, *hexc("9fc3e3"), dawn)
            g.add_color_stop_rgba(1, *hexc("f8d7a8"), dawn)
            c.set_source(g)
            c.rectangle(985, 125, 20, 750)
            c.fill()
            c.move_to(985, 125)
            c.line_to(1005, 125)
            c.line_to(700, 1100)
            c.line_to(560, 1100)
            c.close_path()
            c.set_source_rgba(1, 0.92, 0.75, 0.18 * dawn)
            c.fill()
        shape(c, ell(140, 870, 40, 40, 16), hexc("f4efe6"), "kclk", lw=2.4)
        line(c, [(140, 870), (140, 842)], "kclm", 2.4)
        line(c, [(140, 870), (122, 878)], "kclh", 3)
        text(c, "5:47", 140, 940, 32, (1, 1, 1), a=dawn)
    sing = 1 - fade
    sway = math.sin(t * (2.2 if dawn > 0 else 6)) * (6 if dawn > 0 else 0)
    # 朋友们
    for i, x in enumerate((260, 420, 700, 860)):
        if leave > 0:
            u = clamp(leave * 4 - i * 0.8)
            if u >= 1:
                continue
            x = x + u * (1300 if x > 540 else -900)
        hop = 0 if dawn > 0 or fade > 0 else -abs(math.sin(t * 7 + i)) * 26
        arms = [(-30, -150), (30, -140)] if dawn == 0 and fade == 0 else [(-40, -120), (40, -120)]
        if leave > 0:
            arms = [(-26, -76), (34, -160)]
        friend(c, i, x + sway, 1000 + hop, 1.6, sit=False, mouth="o" if sing > 0.5 else "smile", look=0.2,
               eyes_closed=dawn > 0.5 and leave == 0, arms=arms, walk=t * 7 if leave > 0 else None)
        if i == 1 and dawn == 0 and fade == 0:
            with keep():
                shape(c, ell(x + 30 * 1.6, 1000 - 140 * 1.6 + hop, 14, 14, 12), hexc("e8b94a"), "tamb", lw=2)
    gy = 1000 if dawn > 0 or fade > 0 else 930 - abs(math.sin(t * 7)) * 30
    girl(c, 560 + sway, gy, 1.7, pack=False, hat=False, mouth="o" if sing > 0.5 else "flat", look=0.0,
         eyes_closed=dawn > 0.5 and fade == 0, look_up=0.3 if fade == 0 else -0.6,
         arms=[(-30, -150), (20, -110)] if fade == 0 else [(-26, -76), (20, -96)])
    mx, my = 560 + sway + 20 * 1.7, gy + (-110 if fade == 0 else -96) * 1.7
    line(c, [(mx, my), (mx + 6, my - 30)], "mic", 6, hexc("3a3a3a"))
    circle(c, mx + 7, my - 34, 9, hexc("8a8a94"))
    if fade > 0:
        veil(c, (0.04, 0.04, 0.07), 0.55 * fade)
        if fade > 0.6:
            with keep():
                g = cairo.RadialGradient(560, 900, 0, 560, 900, 320)
                g.add_color_stop_rgba(0, 1, 0.97, 0.9, 0.22)
                g.add_color_stop_rgba(1, 1, 0.97, 0.9, 0)
                c.set_source(g)
                c.paint()


PARTY_CUTS = [0.0, 5.0, 6.2, 7.4, 8.6, 9.8, 11.8, 14.0]


def s05_party(c, t):
    i = max(j for j in range(7) if t >= PARTY_CUTS[j])
    lt = t - PARTY_CUTS[i]
    k = 1 + 0.06 * (1 - ease_out(prog(lt, 0, 0.3)))
    if i == 0:
        k = 1 + 0.05 * ease_io(lt / 5.0)
    with cam(c, 540, 960, k):
        if i == 0:
            party_schedule(c, lt)
        elif i == 1:
            party_dance(c, lt + 1)
        elif i == 2:
            party_club(c, lt + 2)
        elif i == 3:
            party_hotpot(c, lt)
        elif i == 4:
            party_bar(c, lt + 3)
        elif i == 5:
            party_ktv(c, lt)
        else:
            party_ktv(c, lt + 2, dawn=ease_io(prog(lt, 0.0, 0.8)))
    fl = 1 - ease_out(prog(lt, 0, 0.18))
    if 0 < i < 6 and fl > 0:
        with keep():
            c.set_source_rgba(1, 1, 1, 0.5 * fl)
            c.paint()


def s06_empty(c, t):
    fade = ease_io(prog(t, 1.0, 2.4))
    on = 6 - sum(1 for i in range(6) if t >= NEON_OFF[i])
    party_ktv(c, 4.0 + min(t, 0.5), dawn=1.0, fade=fade, neon_on=on, leave=ease_io(prog(t, 0.0, 1.4)))

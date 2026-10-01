"""绘本风绘图工具：手抖线条、水彩填充、人物、常用物件。"""
import math
import random
import zlib
from contextlib import contextmanager

import cairo

W, H = 1920, 1080
FONT_FACE = "LXGW WenKai"


def hexc(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def darker(c, k=0.8):
    return tuple(v * k for v in c)


def clamp(u, a=0.0, b=1.0):
    return a if u < a else b if u > b else u


def lerp(a, b, u):
    return a + (b - a) * u


def prog(t, t0, dur):
    return clamp((t - t0) / dur)


def ease_io(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def ease_in(u):
    u = clamp(u)
    return u ** 3


def ease_back(u, s=1.9):
    u = clamp(u)
    v = u - 1
    return 1 + (s + 1) * v ** 3 + s * v ** 2


INK = hexc("3d2f28")
PAPER = hexc("f4ead8")
SKIN = hexc("f7d6bd")
HAIR = hexc("5a3a2a")
COAT = hexc("e2a93f")
PACK = hexc("6f8f5c")
STRAW = hexc("ecc879")
RIBBON = hexc("bf4a3c")
LEG = hexc("4b3a33")
SHOE = hexc("7a4630")
BLUSH = hexc("ef9a8a")

# ---------------------------------------------------------------- 线条“沸腾”
STATE = {"boil": 0, "ink": INK, "dash": None, "ink_a": 0.9}


def set_time(t):
    # 每秒 8 次的线条抖动，模拟手绘动画的“boil”
    STATE["boil"] = int(t * 8)


@contextmanager
def ink_style(col=None, dash=None, alpha=None):
    old = dict(STATE)
    if col is not None:
        STATE["ink"] = col
    STATE["dash"] = dash
    if alpha is not None:
        STATE["ink_a"] = alpha
    yield
    STATE.update({k: old[k] for k in ("ink", "dash", "ink_a")})


def rng(key, static=False):
    b = 0 if static else STATE["boil"]
    return random.Random(zlib.crc32(f"{key}|{b}".encode()))


def wob(pts, key, amp=1.4, seg=26, closed=True, static=False):
    r = rng(key, static)
    out = []
    n = len(pts)
    m = n if closed else n - 1
    for i in range(m):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        k = max(1, int(math.hypot(x1 - x0, y1 - y0) / seg))
        for j in range(k):
            u = j / k
            out.append((x0 + (x1 - x0) * u + r.uniform(-amp, amp),
                        y0 + (y1 - y0) * u + r.uniform(-amp, amp)))
    if not closed:
        out.append((pts[-1][0] + r.uniform(-amp, amp), pts[-1][1] + r.uniform(-amp, amp)))
    return out


def spath(c, pts, closed=True):
    n = len(pts)
    c.move_to(*pts[0])
    if n < 3:
        for p in pts[1:]:
            c.line_to(*p)
        if closed:
            c.close_path()
        return
    rngi = range(n) if closed else range(n - 1)
    for i in rngi:
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[0]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else pts[-1]
        c.curve_to(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6,
                   p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6,
                   p2[0], p2[1])
    if closed:
        c.close_path()


def shape(c, pts, fill=None, key="s", ink=True, amp=1.3, lw=3.0, closed=True,
          alpha=1.0, edge=True, seg=26):
    """水彩填充 + 错位的墨线。"""
    if fill is not None and closed:
        spath(c, wob(pts, key + "f", amp, seg), True)
        c.set_source_rgba(*fill[:3], (fill[3] if len(fill) > 3 else 0.95) * alpha)
        if edge:
            c.fill_preserve()
            c.set_source_rgba(*darker(fill[:3], 0.78), 0.33 * alpha)
            c.set_line_width(lw * 2.2)
            c.stroke()
        else:
            c.fill()
    if ink:
        spath(c, wob(pts, key + "i", amp, seg, closed), closed)
        c.set_source_rgba(*STATE["ink"], STATE["ink_a"] * alpha)
        c.set_line_width(lw)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        if STATE["dash"]:
            c.set_dash(STATE["dash"])
        c.stroke()
        c.set_dash([])


def line(c, pts, key="l", lw=3.0, col=None, alpha=1.0, amp=1.2):
    spath(c, wob(pts, key, amp, 26, closed=False), closed=False)
    c.set_source_rgba(*(col or STATE["ink"]), alpha * (STATE["ink_a"] if col is None else 1))
    c.set_line_width(lw)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    if STATE["dash"] and col is None:
        c.set_dash(STATE["dash"])
    c.stroke()
    c.set_dash([])


def ell(cx, cy, rx, ry, n=22, a0=0.0, a1=2 * math.pi):
    full = abs(a1 - a0 - 2 * math.pi) < 1e-6
    k = n if full else n + 1
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n),
             cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(k)]


def rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def rrect(x, y, w, h, r, n=4):
    pts = []
    for cx, cy, a in ((x + w - r, y + r, -math.pi / 2), (x + w - r, y + h - r, 0),
                      (x + r, y + h - r, math.pi / 2), (x + r, y + r, math.pi)):
        for i in range(n + 1):
            aa = a + (math.pi / 2) * i / n
            pts.append((cx + r * math.cos(aa), cy + r * math.sin(aa)))
    return pts


def circle(c, x, y, r, col, a=1.0):
    c.arc(x, y, r, 0, 2 * math.pi)
    c.set_source_rgba(*col[:3], a)
    c.fill()


def glow(c, x, y, r, col, a=0.5):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *col, a)
    g.add_color_stop_rgba(0.4, *col, a * 0.45)
    g.add_color_stop_rgba(1, *col, 0)
    c.set_source(g)
    c.arc(x, y, r, 0, 2 * math.pi)
    c.fill()


def vgrad(c, y0, y1, stops, x0=0, x1=W):
    g = cairo.LinearGradient(0, y0, 0, y1)
    for o, col in stops:
        g.add_color_stop_rgb(o, *col)
    c.set_source(g)
    c.rectangle(x0, y0, x1 - x0, y1 - y0)
    c.fill()


@contextmanager
def popup(c, ax, ay, k, sx=None):
    """立体书弹起：以底边为轴纵向展开。"""
    c.save()
    c.translate(ax, ay)
    c.scale(1 if sx is None else sx, max(k, 0.001))
    c.translate(-ax, -ay)
    yield
    c.restore()


@contextmanager
def group_alpha(c, a):
    if a >= 0.999:
        yield
        return
    c.push_group()
    yield
    c.pop_group_to_source()
    c.paint_with_alpha(max(a, 0))


def text(c, s, x, y, size, col, a=1.0, anchor="c"):
    c.select_font_face(FONT_FACE)
    c.set_font_size(size)
    ext = c.text_extents(s)
    if anchor == "c":
        x -= ext.x_advance / 2
    c.move_to(x, y)
    c.set_source_rgba(*col, a)
    c.show_text(s)


# ---------------------------------------------------------------- 风景元件
def hill_pts(base, amp, freq, phase, x0=-60, x1=W + 60, bottom=H + 60, n=40, freq2=None):
    pts = [(x0, bottom)]
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = base - amp * (0.6 * math.sin(x * freq + phase) +
                          0.4 * math.sin(x * (freq2 or freq * 2.3) + phase * 1.7))
        pts.append((x, y))
    pts.append((x1, bottom))
    return pts


def cloud(c, x, y, s, key, col=(1, 0.99, 0.96), a=0.92):
    puffs = [(-60, 6, 34), (-25, -14, 42), (18, -20, 46), (58, 0, 34), (0, 10, 40)]
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for i, (px, py, r) in enumerate(puffs):
        spath(c, wob(ell(px, py, r, r * 0.86, 14), f"{key}{i}", 1.2), True)
    c.set_source_rgba(*col, a)
    c.fill()
    for i, (px, py, r) in enumerate(puffs):
        if py >= 0:
            spath(c, wob(ell(px, py, r, r * 0.86, 14, 0.15 * math.pi, 0.85 * math.pi), f"{key}b{i}", 1.0), False)
    c.set_source_rgba(*darker(col, 0.8), 0.35)
    c.set_line_width(2.4 / s)
    c.stroke()
    c.restore()


def star(c, x, y, r, a, col=(1, 0.95, 0.75)):
    glow(c, x, y, r * 4, col, 0.35 * a)
    c.move_to(x, y - r * 1.6)
    c.curve_to(x, y, x, y, x + r * 1.6, y)
    c.curve_to(x, y, x, y, x, y + r * 1.6)
    c.curve_to(x, y, x, y, x - r * 1.6, y)
    c.curve_to(x, y, x, y, x, y - r * 1.6)
    c.set_source_rgba(*col, a)
    c.fill()


def tree(c, x, base, s, key, col=hexc("74a160")):
    c.save()
    c.translate(x, base)
    c.scale(s, s)
    shape(c, [(-8, 0), (-6, -70), (6, -70), (8, 0)], hexc("8a5a3a"), key + "t", lw=3 / s)
    shape(c, ell(0, -105, 52, 58, 18), col, key + "c", lw=3 / s, amp=2)
    shape(c, ell(-18, -118, 14, 12, 10), mix(col, (1, 1, 0.8), 0.35), key + "h", ink=False)
    c.restore()


def house(c, x, base, w, h, wall, roof, key, roof_type="tri", win=hexc("fbe7b0"), door=True):
    lw = 3
    shape(c, rect(x, base - h, w, h), wall, key + "w", lw=lw)
    if roof_type == "tri":
        shape(c, [(x - 12, base - h), (x + w / 2, base - h - w * 0.55), (x + w + 12, base - h)], roof, key + "r", lw=lw)
    elif roof_type == "flat":
        shape(c, rect(x - 6, base - h - 12, w + 12, 12), roof, key + "r", lw=lw)
    elif roof_type == "dome":
        shape(c, ell(x + w / 2, base - h, w * 0.42, w * 0.42, 16, math.pi, 2 * math.pi), roof, key + "r", lw=lw)
        line(c, [(x + w / 2, base - h - w * 0.42), (x + w / 2, base - h - w * 0.42 - 18)], key + "x", 2.5)
        line(c, [(x + w / 2 - 6, base - h - w * 0.42 - 12), (x + w / 2 + 6, base - h - w * 0.42 - 12)], key + "y", 2.5)
    cols = max(1, int(w // 46))
    rows = max(1, int((h - 40) // 52))
    for i in range(cols):
        for j in range(rows):
            wx = x + (i + 0.5) * w / cols - 10
            wy = base - h + 18 + j * 52
            if door and j == rows - 1 and i == cols // 2:
                continue
            shape(c, rect(wx, wy, 20, 24), win, f"{key}w{i}{j}", lw=2.2, amp=0.8)
    if door:
        dx = x + (cols // 2 + 0.5) * w / cols - 13
        shape(c, rect(dx, base - 40, 26, 40), darker(roof, 0.85), key + "d", lw=2.5)


def mountain(c, x, base, w, h, col, key, snow=True):
    pts = [(x - w / 2, base), (x - w * 0.12, base - h * 0.82), (x, base - h),
           (x + w * 0.16, base - h * 0.78), (x + w / 2, base)]
    shape(c, pts, col, key, lw=3, amp=2)
    if snow:
        sp = [(x - w * 0.12 * 0.62, base - h * 0.82 * 0.62 - h * 0.38 * 0.62 + h * 0.25),
              (x, base - h), (x + w * 0.1, base - h * 0.84), (x + w * 0.05, base - h * 0.74),
              (x - 0.02 * w, base - h * 0.8), (x - w * 0.07, base - h * 0.72)]
        shape(c, sp, (0.98, 0.97, 0.95), key + "s", lw=2.4, amp=1.2)


def paper_bird(c, x, y, s, flap, col, ang=0.0, key="b"):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    f = math.sin(flap)
    lw = 2.4 / s
    shape(c, [(-34, 4), (30, -2), (44, -12), (36, 4), (-10, 12)], col, key + "b", lw=lw, amp=0.7)
    shape(c, [(-8, 2), (16, 0), (4, -40 * f - 6)], mix(col, (1, 1, 1), 0.35), key + "w1", lw=lw, amp=0.7)
    shape(c, [(-2, 4), (20, 2), (12, 30 * f + 8)], darker(col, 0.85), key + "w2", lw=lw, amp=0.7)
    c.restore()


# ---------------------------------------------------------------- 人物
def person(c, x, y, s=1.0, view="front", look=0.0, walk=None, run=False, sit=False,
           coat=COAT, hair=HAIR, hat=True, pack=True, outfit=None, alpha=1.0, key="p",
           head_down=0.0, look_up=0.0, arms=None, legs=True, hair_style="bob",
           skin=SKIN, leg=LEG, shoe=SHOE, sx=1.0):
    """绘本小人，脚底在 (x, y)。sit=True 时 (x, y) 是座面。"""
    c.save()
    c.translate(x, y)
    c.scale(s * sx, s)
    lw = 3.0 / max(s, 0.25) ** 0.6
    with group_alpha(c, alpha):
        ph = walk if walk is not None else 0.0
        amp_leg = (0.85 if run else 0.42) if walk is not None else 0.0
        a = amp_leg * math.sin(ph)
        bob = -abs(math.sin(ph)) * (7 if run else 3) if walk is not None else 0.0
        dy = 52 if sit else 0
        oy = dy + bob

        def body_pts():
            if outfit == "dress":
                return [(-18, -126 + oy), (18, -126 + oy), (38, -48 + oy), (-38, -48 + oy)]
            return [(-19, -126 + oy), (19, -126 + oy), (32, -50 + oy), (-32, -50 + oy)]

        if pack and view == "front":
            shape(c, rrect(-31, -128 + oy, 62, 58, 10), PACK, key + "pk", lw=lw)
        # legs
        if legs:
            for i, sg in enumerate((-1, 1)):
                if sit:
                    sw = 0.18 * math.sin(ph * 0.5 + i * 1.3) if walk is not None else 0
                    hx, hy = sg * 9, 0
                    fx, fy = hx + math.sin(sw) * 46, 46
                else:
                    ang = a * sg
                    hx, hy = sg * 9, -56 + bob * 0.4
                    fx, fy = hx + math.sin(ang) * 56, hy + math.cos(ang) * 56 - (bob * 0.4)
                line(c, [(hx, hy), (fx, fy)], f"{key}lg{i}", lw * 2.2, leg, amp=0.6)
                fwd = 4 if view == "front" else 0
                shape(c, ell(fx + look * fwd, fy, 9, 5, 10), shoe, f"{key}sh{i}", lw=lw * 0.7, amp=0.6)
        # body
        col = coat if outfit != "dress" else hexc("c9553f")
        shape(c, body_pts(), col, key + "bd", lw=lw)
        if outfit == "dress":
            r = random.Random(3)
            for i in range(9):
                px, py = r.uniform(-24, 24), r.uniform(-112, -56)
                if abs(px) < 18 + (py + 126) * 0.25:
                    circle(c, px, py + oy, 3.2, (1, 0.97, 0.9), 0.9)
        else:
            # 纽扣与口袋
            if view == "front":
                for j in range(3):
                    circle(c, 0, -110 + j * 18 + oy, 2.6, darker(col, 0.55), 0.8)
        # arms
        sh = [(-17, -118 + oy), (17, -118 + oy)]
        if arms is None:
            sw = -a * 18
            hands = [(-27 - sw * 0.2, -76 + oy + abs(sw) * 0.1 - sw), (27 + sw * 0.2, -76 + oy + abs(sw) * 0.1 + sw)]
            if run:
                hands = [(-30, -84 + oy - a * 22), (30, -84 + oy + a * 22)]
        else:
            hands = [(hx, hy + (dy if sit else 0)) for hx, hy in arms]
        arm_col = col if outfit != "dress" else SKIN
        for i in range(2):
            line(c, [sh[i], hands[i]], f"{key}ao{i}", lw * 3.4, STATE["ink"], alpha=STATE["ink_a"], amp=0.5)
            line(c, [sh[i], hands[i]], f"{key}ai{i}", lw * 2.0, arm_col, amp=0.5)
            circle(c, hands[i][0], hands[i][1], 5.5, skin)
        if outfit == "dress":
            shape(c, [(-20, -128 + oy), (20, -128 + oy), (14, -118 + oy), (-14, -118 + oy)], hexc("3f8f8a"), key + "sc", lw=lw)
            shape(c, [(10, -122 + oy), (22, -96 + oy), (14, -94 + oy), (6, -118 + oy)], hexc("3f8f8a"), key + "st", lw=lw * 0.8)
        if pack:
            if view == "back":
                shape(c, rrect(-25, -130 + oy, 50, 60, 9), PACK, key + "pb", lw=lw)
                shape(c, rrect(-25, -130 + oy, 50, 20, 6), darker(PACK, 0.88), key + "pf", lw=lw * 0.8)
                shape(c, rrect(-14, -96 + oy, 28, 20, 5), mix(PACK, (1, 1, 1), 0.2), key + "pp", lw=lw * 0.8)
                shape(c, ell(0, -134 + oy, 27, 7, 14), hexc("c79a6a"), key + "roll", lw=lw * 0.8)
            else:
                for i, sg in enumerate((-1, 1)):
                    line(c, [(sg * 11, -124 + oy), (sg * 13, -90 + oy)], f"{key}strap{i}", lw * 1.8, darker(PACK, 0.8), amp=0.4)
        # head
        hy = -150 + oy + head_down
        hdx = look * 2.5 if view == "front" else 0
        if view == "front":
            if hair_style in ("bob", "bun"):
                shape(c, ell(hdx, hy - 1, 30, 28, 18), hair, key + "hb", lw=lw)
            shape(c, ell(hdx, hy, 25, 25, 18), skin, key + "hd", lw=lw)
            if hair_style in ("bob", "bun"):
                bangs = ell(hdx, hy - 2, 30, 28, 10, math.pi * 1.05, math.pi * 1.95)
                bangs += [(hdx + 22, hy - 8), (hdx + 8, hy - 12), (hdx - 6, hy - 9), (hdx - 22, hy - 10)]
                shape(c, bangs, hair, key + "bg", lw=lw * 0.9)
            elif hair_style == "short":
                cap = ell(hdx, hy - 3, 27, 26, 10, math.pi * 1.0, math.pi * 2.0) + [(hdx + 20, hy - 12), (hdx - 20, hy - 12)]
                shape(c, cap, hair, key + "cp", lw=lw * 0.9)
            elif hair_style == "beanie":
                bn = ell(hdx, hy - 5, 28, 28, 10, math.pi * 1.0, math.pi * 2.0) + [(hdx + 28, hy - 3), (hdx - 28, hy - 3)]
                shape(c, bn, hair, key + "bn", lw=lw * 0.9)
                circle(c, hdx, hy - 34, 7, mix(hair, (1, 1, 1), 0.4))
            if hair_style == "bun":
                shape(c, ell(hdx, hy - 34, 12, 11, 10), hair, key + "bun", lw=lw * 0.8)
            ex = look * 6
            ey = hy + 1 - look_up * 4
            for sg in (-1, 1):
                circle(c, hdx + sg * 8.5 + ex, ey, 2.7, STATE["ink"], STATE["ink_a"])
                c.save()
                c.translate(hdx + sg * 15 + ex * 0.6, hy + 9 - look_up * 2)
                c.scale(1, 0.6)
                c.arc(0, 0, 5.5, 0, 2 * math.pi)
                c.restore()
                c.set_source_rgba(*BLUSH, 0.55)
                c.fill()
            if look_up < 0.5:
                c.arc(hdx + ex * 0.8, hy + 8, 4, 0.2 * math.pi, 0.8 * math.pi)
                c.set_source_rgba(*STATE["ink"], STATE["ink_a"] * 0.9)
                c.set_line_width(1.8)
                c.stroke()
        else:
            shape(c, ell(0, hy, 25, 25, 18), skin, key + "hd", lw=lw)
            if hair_style in ("bob", "bun"):
                shape(c, ell(0, hy + 2, 30, 29, 18), hair, key + "hb", lw=lw)
                for i in (-1, 0, 1):
                    line(c, [(i * 9, hy - 20), (i * 11, hy + 22)], f"{key}hs{i}", 1.6, darker(hair, 0.7), alpha=0.6)
            elif hair_style == "short":
                shape(c, ell(0, hy - 1, 26, 25, 18), hair, key + "hb", lw=lw)
            elif hair_style == "beanie":
                shape(c, ell(0, hy, 27, 26, 18), hair, key + "hb", lw=lw)
            if hair_style == "bun":
                shape(c, ell(0, hy - 34, 12, 11, 10), hair, key + "bun", lw=lw * 0.8)
        if hat:
            by = hy - 20
            shape(c, ell(hdx * 0.6, by, 50, 11, 20), STRAW, key + "br", lw=lw)
            crown = [(hdx * 0.6 - 24, by - 1), (hdx * 0.6 - 22, by - 22), (hdx * 0.6 - 12, by - 29),
                     (hdx * 0.6 + 12, by - 29), (hdx * 0.6 + 22, by - 22), (hdx * 0.6 + 24, by - 1)]
            shape(c, crown, STRAW, key + "cr", lw=lw)
            shape(c, rect(hdx * 0.6 - 23, by - 9, 46, 8), RIBBON, key + "rb", lw=lw * 0.7, amp=0.6)
            shape(c, [(hdx * 0.6 + 20, by - 6), (hdx * 0.6 + 36, by + 10), (hdx * 0.6 + 28, by + 12)], RIBBON, key + "rt", lw=lw * 0.7, amp=0.6)
    c.restore()


def girl(c, x, y, s=1.0, **kw):
    kw.setdefault("key", "girl")
    person(c, x, y, s, **kw)


GHOST = dict(coat=hexc("c9d0dc"), hair=hexc("a3abb9"), skin=hexc("e3e6ec"), leg=hexc("aab1be"),
             shoe=hexc("aab1be"), hat=False, pack=False, hair_style="short")


def ghost_person(c, x, y, s, alpha=0.6, **kw):
    with ink_style(hexc("7d879a"), [9, 7], 0.75):
        person(c, x, y, s, alpha=alpha, key="him", **{**GHOST, **kw})


COMPANIONS = [
    dict(coat=hexc("4f8a8b"), hair=hexc("2f2a28"), hair_style="short", key="c1"),
    dict(coat=hexc("e07a5f"), hair=hexc("8b5a3c"), hair_style="bun", key="c2"),
    dict(coat=hexc("8d6a9f"), hair=hexc("3e3a5a"), hair_style="beanie", key="c3"),
]


def companion(c, i, x, y, s=1.05, **kw):
    d = dict(COMPANIONS[i])
    d.update(hat=False, pack=False)
    d.update(kw)
    person(c, x, y, s, **d)


def bicycle(c, x, y, s, rot, col, key):
    """y 为地面。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lw = 3.0 / s ** 0.6
    for i, wx in enumerate((-46, 46)):
        shape(c, ell(wx, -32, 30, 30, 18), None, f"{key}wh{i}", lw=lw * 1.3)
        for k in range(4):
            a = rot + k * math.pi / 4
            line(c, [(wx - 28 * math.cos(a), -32 - 28 * math.sin(a)), (wx + 28 * math.cos(a), -32 + 28 * math.sin(a))],
                 f"{key}sp{i}{k}", 1.4, STATE["ink"], alpha=0.5, amp=0.3)
    frame = [(-46, -32), (-8, -32), (22, -74), (-14, -74), (-8, -32)]
    line(c, frame, key + "fr", lw * 1.8, col, amp=0.5)
    line(c, [(-14, -74), (-46, -32)], key + "fr2", lw * 1.8, col, amp=0.5)
    line(c, [(22, -74), (46, -32)], key + "fork", lw * 1.8, col, amp=0.5)
    line(c, [(22, -74), (26, -92), (14, -96)], key + "bar", lw * 1.4, STATE["ink"], amp=0.4)
    line(c, [(-20, -82), (-6, -82)], key + "seat", lw * 2, STATE["ink"], amp=0.4)
    c.restore()


def mug(c, x, y, s, key, tilt=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s, s)
    shape(c, rrect(-13, -16, 26, 34, 4), hexc("f0b64a"), key + "m", lw=2.4)
    shape(c, ell(0, -18, 15, 7, 12), (1, 0.98, 0.93), key + "f", lw=2)
    line(c, [(13, -8), (21, -6), (21, 8), (13, 10)], key + "h", 2.4)
    c.restore()

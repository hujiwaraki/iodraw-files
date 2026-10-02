"""《此心安处》系列 · 竖屏绘本绘图工具。

手抖线条、水彩填充、全局调色（灰调 / 回彩）、人物、常用物件。
"""
import math
import random
import zlib
from contextlib import contextmanager

import cairo

W, H = 1080, 1920
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
SKIN = hexc("f7d6bd")
HAIR = hexc("5a3a2a")
COAT = hexc("e2a93f")
PACK = hexc("6f8f5c")
STRAW = hexc("ecc879")
RIBBON = hexc("bf4a3c")
LEG = hexc("4b3a33")
SHOE = hexc("7a4630")
BLUSH = hexc("ef9a8a")
WHITE_HAIR = hexc("e9e6e0")

# ---------------------------------------------------------------- 全局状态
STATE = {"boil": 0, "t": 0.0, "ink": INK, "dash": None, "ink_a": 0.9, "no_fill": 0, "no_ink": 0}
GRADE = {"sat": 1.0, "dark": 0.0, "warm": 0.0, "keep": 0}


def set_time(t):
    STATE["t"] = t
    STATE["boil"] = int(t * 8)


def set_grade(sat=1.0, dark=0.0, warm=0.0):
    GRADE.update(sat=sat, dark=dark, warm=warm)


@contextmanager
def grade(sat=None, dark=None, warm=None):
    old = dict(GRADE)
    if sat is not None:
        GRADE["sat"] = sat
    if dark is not None:
        GRADE["dark"] = dark
    if warm is not None:
        GRADE["warm"] = warm
    yield
    GRADE.update(old)


@contextmanager
def keep():
    """在灰色世界里保留原色（女孩的草帽、外套）。"""
    GRADE["keep"] += 1
    yield
    GRADE["keep"] -= 1


def G(col):
    """把颜色按当前调色处理：去饱和偏灰蓝、压暗、暖光。"""
    if GRADE["keep"] > 0 or col is None:
        return col
    a = col[3:] if len(col) > 3 else ()
    r, g, b = col[:3]
    s = GRADE["sat"]
    if s < 1:
        lum = 0.3 * r + 0.59 * g + 0.11 * b
        grey = (lum * 0.93, lum * 0.98, min(1, lum * 1.07))
        r, g, b = mix(grey, (r, g, b), s)
    w = GRADE["warm"]
    if w > 0:
        r, g, b = mix((r, g, b), (min(1, r * 1.1 + 0.03), g * 1.0, b * 0.84), w)
    d = GRADE["dark"]
    if d > 0:
        r, g, b = mix((r, g, b), (0.11, 0.13, 0.2), d)
    return (r, g, b) + a


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


@contextmanager
def outline_only():
    STATE["no_fill"] += 1
    yield
    STATE["no_fill"] -= 1


@contextmanager
def fill_only():
    STATE["no_ink"] += 1
    yield
    STATE["no_ink"] -= 1


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
    """水彩填充 + 错位墨线。"""
    if fill is not None and closed and not STATE["no_fill"]:
        f = G(fill)
        spath(c, wob(pts, key + "f", amp, seg), True)
        c.set_source_rgba(*f[:3], (f[3] if len(f) > 3 else 0.95) * alpha)
        if edge:
            c.fill_preserve()
            c.set_source_rgba(*darker(f[:3], 0.78), 0.33 * alpha)
            c.set_line_width(lw * 2.2)
            c.stroke()
        else:
            c.fill()
    if ink and not STATE["no_ink"]:
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
    if col is None and STATE["no_ink"]:
        return
    if col is not None and STATE["no_fill"] and col != STATE["ink"]:
        return
    spath(c, wob(pts, key, amp, 26, closed=False), closed=False)
    cc = STATE["ink"] if col is None else G(col)
    c.set_source_rgba(*cc[:3], alpha * (STATE["ink_a"] if col is None else 1))
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
    if STATE["no_fill"]:
        return
    c.arc(x, y, r, 0, 2 * math.pi)
    cc = G(col)
    c.set_source_rgba(*cc[:3], a)
    c.fill()


def glow(c, x, y, r, col, a=0.5):
    if r <= 0:
        return
    cc = G(col)[:3]
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *cc, a)
    g.add_color_stop_rgba(0.4, *cc, a * 0.45)
    g.add_color_stop_rgba(1, *cc, 0)
    c.set_source(g)
    c.arc(x, y, r, 0, 2 * math.pi)
    c.fill()


def vgrad(c, y0, y1, stops, x0=-200, x1=W + 200):
    g = cairo.LinearGradient(0, y0, 0, y1)
    for o, col in stops:
        g.add_color_stop_rgb(o, *G(col)[:3])
    c.set_source(g)
    c.rectangle(x0, y0, x1 - x0, y1 - y0)
    c.fill()


def fill_all(c, col):
    c.set_source_rgb(*G(col)[:3])
    c.paint()


def veil(c, col, a):
    if a <= 0:
        return
    c.set_source_rgba(*col, a)
    c.paint()


@contextmanager
def popup(c, ax, ay, k, sx=None):
    """立体书弹起：以底边为轴展开。"""
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


@contextmanager
def cam(c, cx, cy, k=1.0, tx=0.0, ty=0.0, rot=0.0):
    """以 (cx, cy) 为中心缩放，并整体平移。"""
    c.save()
    c.translate(W / 2 + tx, H / 2 + ty)
    c.rotate(rot)
    c.scale(k, k)
    c.translate(-cx, -cy)
    yield
    c.restore()


def text(c, s, x, y, size, col, a=1.0, anchor="c"):
    c.select_font_face(FONT_FACE)
    c.set_font_size(size)
    ext = c.text_extents(s)
    if anchor == "c":
        x -= ext.x_advance / 2
    elif anchor == "r":
        x -= ext.x_advance
    c.move_to(x, y)
    cc = G(col)
    c.set_source_rgba(*cc[:3], a)
    c.show_text(s)
    c.new_path()


def flood(c, draw_fn, cx, cy, r, soft=260, from_sat=0.12, to_sat=1.0):
    """颜色从 (cx, cy) 涌出：圈内彩色，圈外灰色。"""
    with grade(sat=from_sat):
        c.push_group()
        draw_fn(c)
        grey = c.pop_group()
    with grade(sat=to_sat, dark=0.0, warm=0.0):
        c.push_group()
        draw_fn(c)
        col = c.pop_group()
    c.set_source(grey)
    c.paint()
    if r > 0:
        m = cairo.RadialGradient(cx, cy, max(r - soft, 0), cx, cy, r)
        m.add_color_stop_rgba(0, 0, 0, 0, 1)
        m.add_color_stop_rgba(1, 0, 0, 0, 0)
        c.set_source(col)
        c.mask(m)


# ---------------------------------------------------------------- 风景元件
def hill_pts(base, amp, freq, phase, x0=-80, x1=W + 80, bottom=H + 80, n=40):
    pts = [(x0, bottom)]
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = base - amp * (0.6 * math.sin(x * freq + phase) + 0.4 * math.sin(x * freq * 2.3 + phase * 1.7))
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
    cc = G(col)
    c.set_source_rgba(*cc[:3], a)
    c.fill()
    for i, (px, py, r) in enumerate(puffs):
        if py >= 0:
            spath(c, wob(ell(px, py, r, r * 0.86, 14, 0.15 * math.pi, 0.85 * math.pi), f"{key}b{i}", 1.0), False)
    c.set_source_rgba(*darker(cc[:3], 0.8), 0.35)
    c.set_line_width(2.4 / s)
    c.stroke()
    c.restore()


def rain_cloud(c, x, y, s, key, col=hexc("8a8f99"), t=0.0, drops=True):
    cloud(c, x, y, s, key, col, 0.95)
    if drops:
        r = random.Random(zlib.crc32(key.encode()))
        for i in range(int(10 * s)):
            dx = r.uniform(-70, 70) * s
            ph = (t * 1.6 + r.random()) % 1.0
            dy = 30 * s + ph * 110 * s
            line(c, [(x + dx, y + dy), (x + dx - 3, y + dy + 12 * s)], f"{key}d{i}", 2.2, hexc("7f8ea3"), alpha=1 - ph)


def rain(c, t, n=70, a=0.35, col=hexc("9aa6b5"), seed=1, x0=0, x1=W, y0=0, y1=H):
    r = random.Random(seed)
    cc = G(col)
    c.set_source_rgba(*cc[:3], a)
    c.set_line_width(2)
    for i in range(n):
        x = r.uniform(x0, x1 + 200)
        sp = r.uniform(900, 1400)
        y = (r.uniform(0, y1 - y0) + t * sp) % (y1 - y0) + y0
        x -= (t * sp * 0.15) % 200
        c.move_to(x, y)
        c.rel_line_to(-6, 26)
    c.stroke()


def star(c, x, y, r, a, col=(1, 0.95, 0.75)):
    glow(c, x, y, r * 4, col, 0.35 * a)
    cc = G(col)
    c.move_to(x, y - r * 1.6)
    c.curve_to(x, y, x, y, x + r * 1.6, y)
    c.curve_to(x, y, x, y, x, y + r * 1.6)
    c.curve_to(x, y, x, y, x - r * 1.6, y)
    c.curve_to(x, y, x, y, x, y - r * 1.6)
    c.set_source_rgba(*cc[:3], a)
    c.fill()


def tree(c, x, base, s, key, col=hexc("74a160"), bare=0.0):
    c.save()
    c.translate(x, base)
    c.scale(s, s)
    shape(c, [(-8, 0), (-6, -70), (6, -70), (8, 0)], hexc("8a5a3a"), key + "t", lw=3 / s)
    if bare > 0:
        for k, (bx, by) in enumerate(((-40, -120), (36, -130), (0, -160), (-20, -100), (30, -95))):
            line(c, [(0, -60), (bx * 0.5, (by - 60) * 0.5), (bx, by)], f"{key}br{k}", 4 / s, hexc("6b4a35"))
    if bare < 1:
        with group_alpha(c, 1 - bare):
            shape(c, ell(0, -105, 52, 58, 18), col, key + "c", lw=3 / s, amp=2)
            shape(c, ell(-18, -118, 14, 12, 10), mix(col, (1, 1, 0.8), 0.35), key + "h", ink=False)
    c.restore()


def house(c, x, base, w, h, wall, roof, key, roof_type="tri", win=hexc("fbe7b0"), door=True, lit=None):
    lw = 3
    shape(c, rect(x, base - h, w, h), wall, key + "w", lw=lw)
    if roof_type == "tri":
        shape(c, [(x - 12, base - h), (x + w / 2, base - h - w * 0.55), (x + w + 12, base - h)], roof, key + "r", lw=lw)
    elif roof_type == "flat":
        shape(c, rect(x - 6, base - h - 12, w + 12, 12), roof, key + "r", lw=lw)
    elif roof_type == "dome":
        shape(c, ell(x + w / 2, base - h, w * 0.42, w * 0.42, 16, math.pi, 2 * math.pi), roof, key + "r", lw=lw)
    cols = max(1, int(w // 46))
    rows = max(1, int((h - 40) // 52))
    for i in range(cols):
        for j in range(rows):
            wx = x + (i + 0.5) * w / cols - 10
            wy = base - h + 18 + j * 52
            if door and j == rows - 1 and i == cols // 2:
                continue
            wc = win if lit is None else (hexc("f6d27a") if (i * 7 + j * 3 + lit) % 5 == 0 else win)
            shape(c, rect(wx, wy, 20, 24), wc, f"{key}w{i}{j}", lw=2.2, amp=0.8)
    if door:
        dx = x + (cols // 2 + 0.5) * w / cols - 13
        shape(c, rect(dx, base - 40, 26, 40), darker(roof, 0.85), key + "d", lw=2.5)


def mountain(c, x, base, w, h, col, key, snow=True):
    pts = [(x - w / 2, base), (x - w * 0.12, base - h * 0.82), (x, base - h),
           (x + w * 0.16, base - h * 0.78), (x + w / 2, base)]
    shape(c, pts, col, key, lw=3, amp=2)
    if snow:
        sp = [(x - w * 0.07, base - h * 0.72), (x, base - h), (x + w * 0.1, base - h * 0.84),
              (x + w * 0.05, base - h * 0.74), (x - 0.02 * w, base - h * 0.8)]
        shape(c, sp, (0.98, 0.97, 0.95), key + "s", lw=2.4, amp=1.2)


def silhouette(c, x, y, s, key, col=hexc("8d95a3"), walk=None, a=0.85):
    """没有脸的路人剪影。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    ph = walk or 0.0
    sw = 0.4 * math.sin(ph) if walk is not None else 0
    with group_alpha(c, a):
        for sg in (-1, 1):
            line(c, [(sg * 8, -60), (sg * 8 + math.sin(sw * sg) * 60, 0)], f"{key}l{sg}", 9, col, amp=0.5)
        shape(c, [(-22, -140), (22, -140), (30, -56), (-30, -56)], col, key + "b", ink=False, edge=False)
        shape(c, ell(0, -165, 24, 26, 14), col, key + "h", ink=False, edge=False)
    c.restore()


# ---------------------------------------------------------------- 人物
def person(c, x, y, s=1.0, view="front", look=0.0, walk=None, run=False, sit=False, crouch=False,
           coat=COAT, hair=HAIR, hat=True, pack=True, outfit=None, alpha=1.0, key="p",
           head_down=0.0, look_up=0.0, arms=None, legs=True, hair_style="bob",
           skin=SKIN, leg=LEG, shoe=SHOE, sx=1.0, keep_color=False, age=0.0, mouth="smile",
           tilt=0.0, badge=False, blink=True, eyes_closed=False):
    """绘本小人，脚底在 (x, y)；sit/crouch 时 (x, y) 是座面/臀部。"""
    c.save()
    c.translate(x, y)
    c.scale(s * sx, s)
    lw = 3.0 / max(s, 0.25) ** 0.6
    hair = mix(hair, WHITE_HAIR, age)

    def kc():
        return keep() if keep_color else _null()

    with group_alpha(c, alpha):
        ph = walk if walk is not None else 0.0
        amp_leg = (0.85 if run else 0.42) if walk is not None else 0.0
        a = amp_leg * math.sin(ph)
        bob = -abs(math.sin(ph)) * (7 if run else 3) if walk is not None else 0.0
        dy = 52 if sit else 0
        oy = dy + bob + age * 4

        if pack and view == "front":
            with kc():
                shape(c, rrect(-31, -128 + oy, 62, 58, 10), PACK, key + "pk", lw=lw)
        if legs:
            for i, sg in enumerate((-1, 1)):
                if sit and crouch:
                    hx, hy = sg * 10, 0
                    fx, fy = sg * 12, 32
                elif sit:
                    sw = 0.18 * math.sin(ph * 0.5 + i * 1.3) if walk is not None else 0
                    hx, hy = sg * 9, 0
                    fx, fy = hx + math.sin(sw) * 46, 46
                else:
                    ang = a * sg
                    hx, hy = sg * 9, -56 + bob * 0.4
                    fx, fy = hx + math.sin(ang) * 56, hy + math.cos(ang) * 56 - (bob * 0.4)
                if sit and crouch:
                    line(c, [(hx, hy), (sg * 34, -30), (fx, fy)], f"{key}lg{i}", lw * 2.2, leg, amp=0.6)
                else:
                    line(c, [(hx, hy), (fx, fy)], f"{key}lg{i}", lw * 2.2, leg, amp=0.6)
                fwd = 4 if view == "front" else 0
                shape(c, ell(fx + look * fwd, fy, 9, 5, 10), shoe, f"{key}sh{i}", lw=lw * 0.7, amp=0.6)
        col = coat if outfit != "dress" else hexc("c9553f")
        with kc():
            if outfit == "dress":
                shape(c, [(-18, -126 + oy), (18, -126 + oy), (38, -48 + oy), (-38, -48 + oy)], col, key + "bd", lw=lw)
                r = random.Random(3)
                for i in range(9):
                    px, py = r.uniform(-24, 24), r.uniform(-112, -56)
                    if abs(px) < 18 + (py + 126) * 0.25:
                        circle(c, px, py + oy, 3.2, (1, 0.97, 0.9), 0.9)
            else:
                shape(c, [(-19, -126 + oy), (19, -126 + oy), (32, -50 + oy), (-32, -50 + oy)], col, key + "bd", lw=lw)
                if view == "front":
                    for j in range(3):
                        circle(c, 0, -110 + j * 18 + oy, 2.6, darker(col, 0.55), 0.8)
        if badge and view == "front":
            line(c, [(-9, -124 + oy), (0, -100 + oy), (9, -124 + oy)], key + "lan", 2.2, hexc("3f6fb5"))
            shape(c, rect(-11, -100 + oy, 22, 28), hexc("f8f6f0"), key + "bdg", lw=1.8, amp=0.4)
            circle(c, -3, -91 + oy, 4, hexc("9fb7d4"))
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
            line(c, [sh[i], hands[i]], f"{key}ao{i}", lw * 3.4, None, amp=0.5) if not STATE["no_ink"] else None
            with kc():
                line(c, [sh[i], hands[i]], f"{key}ai{i}", lw * 2.0, arm_col, amp=0.5)
            circle(c, hands[i][0], hands[i][1], 5.5, skin)
        if outfit == "dress":
            with kc():
                shape(c, [(-20, -128 + oy), (20, -128 + oy), (14, -118 + oy), (-14, -118 + oy)], hexc("3f8f8a"), key + "sc", lw=lw)
                shape(c, [(10, -122 + oy), (22, -96 + oy), (14, -94 + oy), (6, -118 + oy)], hexc("3f8f8a"), key + "st", lw=lw * 0.8)
        if pack:
            with kc():
                if view == "back":
                    shape(c, rrect(-25, -130 + oy, 50, 60, 9), PACK, key + "pb", lw=lw)
                    shape(c, rrect(-25, -130 + oy, 50, 20, 6), darker(PACK, 0.88), key + "pf", lw=lw * 0.8)
                    shape(c, rrect(-14, -96 + oy, 28, 20, 5), mix(PACK, (1, 1, 1), 0.2), key + "pp", lw=lw * 0.8)
                    shape(c, ell(0, -134 + oy, 27, 7, 14), hexc("c79a6a"), key + "roll", lw=lw * 0.8)
                else:
                    for i, sg in enumerate((-1, 1)):
                        line(c, [(sg * 11, -124 + oy), (sg * 13, -90 + oy)], f"{key}strap{i}", lw * 1.8, darker(PACK, 0.8), amp=0.4)
        # 头部（可倾斜）
        hy = -150 + oy + head_down
        c.save()
        c.translate(0, hy + 24)
        c.rotate(tilt)
        c.translate(0, -(hy + 24))
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
                cap = ell(hdx, hy - 3, 27, 26, 10, math.pi, math.pi * 2.0) + [(hdx + 20, hy - 12), (hdx - 20, hy - 12)]
                shape(c, cap, hair, key + "cp", lw=lw * 0.9)
            elif hair_style == "granny":
                cap = ell(hdx, hy - 3, 28, 26, 10, math.pi, math.pi * 2.0) + [(hdx + 22, hy - 8), (hdx - 22, hy - 8)]
                shape(c, cap, hair, key + "cp", lw=lw * 0.9)
                shape(c, ell(hdx, hy - 30, 13, 11, 10), hair, key + "bun", lw=lw * 0.8)
            if hair_style == "bun":
                shape(c, ell(hdx, hy - 34, 12, 11, 10), hair, key + "bun", lw=lw * 0.8)
            if not STATE["no_fill"] or not STATE["no_ink"]:
                ex = look * 6
                ey = hy + 1 - look_up * 4
                tt = STATE["t"] + (zlib.crc32(key.encode()) % 100) / 37
                closed = eyes_closed or (blink and (tt % 3.3) < 0.13)
                for sg in (-1, 1):
                    if closed:
                        line(c, [(hdx + sg * 8.5 + ex - 3.5, ey), (hdx + sg * 8.5 + ex + 3.5, ey)], f"{key}bl{sg}", 2.0)
                    elif not STATE["no_ink"]:
                        c.arc(hdx + sg * 8.5 + ex, ey, 2.8 if mouth == "o" else 2.6, 0, 2 * math.pi)
                        c.set_source_rgba(*STATE["ink"], STATE["ink_a"])
                        c.fill()
                    if not STATE["no_fill"]:
                        c.save()
                        c.translate(hdx + sg * 15 + ex * 0.6, hy + 9 - look_up * 2)
                        c.scale(1, 0.6)
                        c.arc(0, 0, 5.5, 0, 2 * math.pi)
                        c.restore()
                        c.set_source_rgba(*G(BLUSH)[:3], 0.55)
                        c.fill()
                if not STATE["no_ink"]:
                    mx = hdx + ex * 0.8
                    if mouth == "o":
                        c.arc(mx, hy + 10, 3.6, 0, 2 * math.pi)
                        c.set_source_rgba(*STATE["ink"], STATE["ink_a"])
                        c.set_line_width(1.8)
                        c.stroke()
                    elif mouth == "flat":
                        c.move_to(mx - 4, hy + 10)
                        c.line_to(mx + 4, hy + 10)
                        c.set_source_rgba(*STATE["ink"], STATE["ink_a"] * 0.9)
                        c.set_line_width(1.8)
                        c.stroke()
                    elif mouth == "sad":
                        c.arc(mx, hy + 14, 4, 1.2 * math.pi, 1.8 * math.pi)
                        c.set_source_rgba(*STATE["ink"], STATE["ink_a"] * 0.9)
                        c.set_line_width(1.8)
                        c.stroke()
                    elif mouth == "laugh":
                        c.arc(mx, hy + 7, 5, 0, math.pi)
                        c.close_path()
                        c.set_source_rgba(*hexc("b5503f"), 0.9)
                        c.fill()
                    else:
                        c.arc(mx, hy + 8, 4, 0.2 * math.pi, 0.8 * math.pi)
                        c.set_source_rgba(*STATE["ink"], STATE["ink_a"] * 0.9)
                        c.set_line_width(1.8)
                        c.stroke()
        else:
            shape(c, ell(0, hy, 25, 25, 18), skin, key + "hd", lw=lw)
            if hair_style in ("bob", "bun"):
                shape(c, ell(0, hy + 2, 30, 29, 18), hair, key + "hb", lw=lw)
                for i in (-1, 0, 1):
                    line(c, [(i * 9, hy - 20), (i * 11, hy + 22)], f"{key}hs{i}", 1.6, darker(hair, 0.7), alpha=0.6)
            elif hair_style in ("short", "granny"):
                shape(c, ell(0, hy - 1, 26, 25, 18), hair, key + "hb", lw=lw)
            if hair_style == "bun":
                shape(c, ell(0, hy - 34, 12, 11, 10), hair, key + "bun", lw=lw * 0.8)
        if hat:
            with kc():
                hat_c = mix(STRAW, hexc("b9b3a8"), clamp(age * 1.2))
                by = hy - 20
                shape(c, ell(hdx * 0.6, by, 50, 11, 20), hat_c, key + "br", lw=lw)
                crown = [(hdx * 0.6 - 24, by - 1), (hdx * 0.6 - 22, by - 22), (hdx * 0.6 - 12, by - 29),
                         (hdx * 0.6 + 12, by - 29), (hdx * 0.6 + 22, by - 22), (hdx * 0.6 + 24, by - 1)]
                shape(c, crown, hat_c, key + "cr", lw=lw)
                shape(c, rect(hdx * 0.6 - 23, by - 9, 46, 8), RIBBON, key + "rb", lw=lw * 0.7, amp=0.6)
                shape(c, [(hdx * 0.6 + 20, by - 6), (hdx * 0.6 + 36, by + 10), (hdx * 0.6 + 28, by + 12)], RIBBON, key + "rt", lw=lw * 0.7, amp=0.6)
        c.restore()
    c.restore()


@contextmanager
def _null():
    yield


def girl(c, x, y, s=1.0, **kw):
    kw.setdefault("key", "girl")
    kw.setdefault("keep_color", True)
    person(c, x, y, s, **kw)


def hat_item(c, x, y, s, key="hhat", dust=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with keep():
        hc = mix(STRAW, hexc("a9a49a"), dust)
        shape(c, ell(0, 0, 54, 12, 20), hc, key + "b", lw=3)
        shape(c, [(-22, -1), (-20, -24), (-10, -31), (10, -31), (20, -24), (22, -1)], hc, key + "c", lw=3)
        shape(c, rect(-21, -10, 42, 8), mix(RIBBON, hexc("8a8580"), dust), key + "r", lw=2)
    c.restore()


def mug(c, x, y, s, key, col=hexc("f0b64a"), heart=None, crack=False):
    """heart: 'L' / 'R' 半颗心。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shape(c, rrect(-22, -30, 44, 56, 6), col, key + "m", lw=2.6)
    side = -1 if heart == "R" else 1
    line(c, [(side * 22, -16), (side * 34, -14), (side * 34, 6), (side * 22, 8)], key + "h", 2.6)
    if heart:
        sg = 1 if heart == "L" else -1
        cx = 22 * sg
        pts = [(cx, -14)]
        for i in range(9):
            a = math.pi * i / 8
            pts.append((cx - sg * (8 + 8 * math.sin(a)), -18 + i * 3.4 - 6 * math.sin(a)))
        pts.append((cx, 14))
        shape(c, pts, hexc("d9534a"), key + "ht", lw=1.6, amp=0.4)
    if crack:
        line(c, [(-8, -30), (-2, -16), (-10, -4), (-3, 8), (-7, 18)], key + "ck", 2.4, INK)
    c.restore()


def phone(c, x, y, s, key, label="家", ring=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(math.sin(ring * 40) * 0.06 * (ring > 0))
    c.scale(s, s)
    glow(c, 0, 0, 120, hexc("dfeaff"), 0.55)
    shape(c, rrect(-28, -52, 56, 104, 9), hexc("3a3f4a"), key + "b", lw=2.4)
    with keep():
        shape(c, rrect(-23, -44, 46, 84, 5), hexc("e8f0ff"), key + "s", lw=1.6, edge=False)
        text(c, label, 0, -10, 22, INK)
        circle(c, -10, 24, 7, hexc("6fbf73"))
        circle(c, 10, 24, 7, hexc("e0604f"))
    c.restore()

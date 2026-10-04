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
STATE = {"still": 0, "boil": 0, "t": 0.0, "ink": INK, "dash": None, "ink_a": 0.9, "no_fill": 0, "no_ink": 0}
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
def nokeep():
    """临时让 keep() 失效：整个人物（包括草帽、外套）都跟着调色走。"""
    old = GRADE["keep"]
    GRADE["keep"] = -1000
    yield
    GRADE["keep"] = old


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
    b = 0 if static or STATE["still"] else STATE["boil"]
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
           tilt=0.0, badge=False, blink=True, eyes_closed=False, round_face=False):
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

        if hair_style in LONG_HAIR and view == "front":
            _long_hair_behind(c, hair_style, look * 2.5, -150 + oy + head_down, mix(hair, WHITE_HAIR, 0), key, lw)
        if pack and view == "front":
            with kc():
                shape(c, rrect(-31, -128 + oy, 62, 58, 10), PACK, key + "pk", lw=lw)
        feet = []
        if outfit in COSTUMES and COSTUMES[outfit].get("bare_legs"):
            leg, shoe = skin, hexc("8a5a3a")
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
                feet.append((hx, hy, fx, fy))
        if outfit in COSTUMES and feet and not sit:
            with kc():
                _costume_legs(c, outfit, feet, oy, key, lw)
        col = {"dress": hexc("c9553f"), "folk": hexc("2f7f8a")}.get(outfit, coat)
        if outfit in COSTUMES:
            col = COSTUMES[outfit]["sleeve"]
        with kc():
            if outfit in COSTUMES:
                _costume_body(c, outfit, oy, key, lw, view)
            elif outfit == "folk":
                shape(c, [(-18, -126 + oy), (18, -126 + oy), (42, -44 + oy), (-42, -44 + oy)], col, key + "bd", lw=lw)
                for j, (yy, bc) in enumerate(((-58, "e8b94a"), (-70, "c9473b"), (-112, "e8b94a"))):
                    half = 18 + (yy + 126) * 0.29
                    pts = [(-half + k * half / 4, yy + oy + (3 if k % 2 else -3)) for k in range(9)]
                    line(c, pts, f"{key}band{j}", 2.6, hexc(bc), amp=0.3)
                for k in range(5):
                    circle(c, -16 + k * 8, -92 + oy, 2.2, hexc("f3e6c6"), 0.9)
            elif outfit == "dress":
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
        if outfit in COSTUMES:
            with kc():
                _costume_neck(c, outfit, oy, key, lw, view)
                if view == "front":
                    _costume_hands(c, outfit, hands, key, lw)
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
        STATE["still"] += 1                # 头部（脸、五官、头发、帽子）线条不抖动
        c.translate(0, hy + 24)
        c.rotate(tilt)
        c.translate(0, -(hy + 24))
        hdx = look * 2.5 if view == "front" else 0
        if view == "front":
            if hair_style in ("bob", "bun"):
                shape(c, ell(hdx, hy - 1, 30, 28, 18), hair, key + "hb", lw=lw)
            if hair_style in GIRL_HAIR:
                _hair_behind(c, hair_style, hdx, hy, hair, key, lw)
            fw, fh, fdy = (27.5, 24.5, 1.5) if round_face else (25, 25, 0)      # 主角：更圆一点的脸
            shape(c, ell(hdx, hy + fdy, fw, fh, 18), skin, key + "hd", lw=lw)
            if hair_style in GIRL_HAIR:
                _hair_front(c, hair_style, hdx, hy, hair, key, lw)
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
                        c.translate(hdx + sg * (16.5 if round_face else 15) + ex * 0.6, hy + (10 if round_face else 9) - look_up * 2)
                        c.scale(1, 0.6)
                        c.arc(0, 0, 6.5 if round_face else 5.5, 0, 2 * math.pi)
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
            fw, fh, fdy = (27.5, 24.5, 1.5) if round_face else (25, 25, 0)
            shape(c, ell(0, hy + fdy, fw, fh, 18), skin, key + "hd", lw=lw)
            if hair_style in GIRL_HAIR:
                _hair_back_view(c, hair_style, hy, hair, key, lw)
            if hair_style in ("bob", "bun"):
                shape(c, ell(0, hy + 2, 30, 29, 18), hair, key + "hb", lw=lw)
                for i in (-1, 0, 1):
                    line(c, [(i * 9, hy - 20), (i * 11, hy + 22)], f"{key}hs{i}", 1.6, darker(hair, 0.7), alpha=0.6)
            elif hair_style in ("short", "granny"):
                shape(c, ell(0, hy - 1, 26, 25, 18), hair, key + "hb", lw=lw)
            if hair_style == "bun":
                shape(c, ell(0, hy - 34, 12, 11, 10), hair, key + "bun", lw=lw * 0.8)
        if outfit in COSTUMES:
            with kc():
                _costume_head(c, outfit, hdx, hy, key, lw, view, hat)
        if hat and (outfit not in COSTUMES or COSTUMES[outfit].get("straw")):
            with kc():
                hat_c = mix(STRAW, hexc("b9b3a8"), clamp(age * 1.2))
                by = hy - 20
                shape(c, ell(hdx * 0.6, by, 50, 11, 20), hat_c, key + "br", lw=lw)
                crown = [(hdx * 0.6 - 24, by - 1), (hdx * 0.6 - 22, by - 22), (hdx * 0.6 - 12, by - 29),
                         (hdx * 0.6 + 12, by - 29), (hdx * 0.6 + 22, by - 22), (hdx * 0.6 + 24, by - 1)]
                shape(c, crown, hat_c, key + "cr", lw=lw)
                shape(c, rect(hdx * 0.6 - 23, by - 9, 46, 8), RIBBON, key + "rb", lw=lw * 0.7, amp=0.6)
                shape(c, [(hdx * 0.6 + 20, by - 6), (hdx * 0.6 + 36, by + 10), (hdx * 0.6 + 28, by + 12)], RIBBON, key + "rt", lw=lw * 0.7, amp=0.6)
        STATE["still"] -= 1
        c.restore()
    c.restore()


@contextmanager
def _null():
    yield


GIRL_HAIR = ("sweep", "flick", "hat_braids", "pony", "braids", "bang_short", "bang_long", "curtain_long")
LONG_HAIR = ("bang_long", "curtain_long")
HAIR_TIE = hexc("c9473b")


def _sway(key, k=1.0):
    return math.sin(STATE["t"] * 2.2 + (zlib.crc32(key.encode()) % 7)) * 3 * k


def _hair_behind(c, style, x, y, hair, key, lw):
    """脸后面的头发：只露出两侧和脑后，不在下巴处合成一圈。"""
    if style in ("sweep", "pony"):
        for sg in (-1, 1):                     # A 侧分短发：两侧发尾外翘（戴帽子时用）
            pts = [(x + sg * 23, y - 12), (x + sg * 31, y), (x + sg * 29, y + 12), (x + sg * 34, y + 22), (x + sg * 38, y + 30),
                   (x + sg * 31, y + 31), (x + sg * 26, y + 25), (x + sg * 23, y + 14), (x + sg * 20, y + 4)]
            shape(c, pts, hair, f"{key}lk{sg}", lw=lw * 0.9, amp=0.5)
            line(c, [(x + sg * 26, y), (x + sg * 28, y + 14), (x + sg * 33, y + 25)], f"{key}wv{sg}", 1.1, darker(hair, 0.6),
                 alpha=0.5)
    if style == "flick":
        for sg in (-1, 1):                     # 不戴帽：齐平的下摆，发尾微微往外翘
            pts = [(x + sg * 23, y - 12), (x + sg * 30, y - 2), (x + sg * 31, y + 10), (x + sg * 32, y + 18),
                   (x + sg * 37, y + 22), (x + sg * 30, y + 24), (x + sg * 20, y + 22), (x + sg * 20, y + 4)]
            shape(c, pts, hair, f"{key}lk{sg}", lw=lw * 0.9, amp=0.35)
            line(c, [(x + sg * 25, y), (x + sg * 27, y + 19)], f"{key}wv{sg}", 1.1, darker(hair, 0.6), alpha=0.45)
    if style == "hat_braids":
        for sg in (-1, 1):                     # 戴帽：头发收到耳后，只露两侧一小片
            pts = [(x + sg * 23, y - 12), (x + sg * 29, y - 2), (x + sg * 29, y + 8), (x + sg * 21, y + 8), (x + sg * 20, y)]
            shape(c, pts, hair, f"{key}lk{sg}", lw=lw * 0.9, amp=0.3)
    if style == "bang_short":
        for sg in (-1, 1):
            pts = [(x + sg * 22, y - 14), (x + sg * 30, y - 2), (x + sg * 31, y + 20), (x + sg * 20, y + 21), (x + sg * 20, y + 4)]
            shape(c, pts, hair, f"{key}bl{sg}", lw=lw * 0.9, amp=0.4)
    if style == "pony":
        sw = _sway(key)
        pts = [(x + 18, y + 2), (x + 30, y + 10), (x + 38 + sw, y + 30), (x + 36 + sw * 1.5, y + 50),
               (x + 28 + sw, y + 42), (x + 24, y + 22), (x + 14, y + 10)]
        shape(c, pts, hair, key + "pony", lw=lw * 0.9, amp=0.5)
        line(c, [(x + 27, y + 18), (x + 31 + sw * 0.6, y + 36)], key + "pst", 1.2, darker(hair, 0.65), alpha=0.6)
        with keep():
            shape(c, ell(x + 26, y + 9, 5, 4, 10), HAIR_TIE, key + "tie", lw=lw * 0.6, amp=0.3)


def _braid(c, x0, y0, sg, hair, key, lw):
    sw = _sway(key, 0.6)
    for j in range(4):
        bx = x0 + sg * (2 + j * 1.5) + sw * j / 3
        by = y0 + 6 + j * 10
        r = 7 - j * 0.7
        shape(c, ell(bx, by, r, r * 0.85, 10), hair, f"{key}{j}", lw=lw * 0.7, amp=0.3)
        line(c, [(bx - r * 0.6, by - 1), (bx + r * 0.6, by + 2)], f"{key}w{j}", 1.0, darker(hair, 0.6), alpha=0.6)
    ex, ey = x0 + sg * 8 + sw, y0 + 46
    with keep():
        shape(c, ell(ex, ey - 2, 4, 3, 8), HAIR_TIE, key + "t", lw=lw * 0.5, amp=0.2)
    shape(c, [(ex - 4, ey), (ex + 4, ey), (ex + 3 + sg * 2, ey + 9), (ex - 3 + sg * 2, ey + 8)], hair, key + "tf", lw=lw * 0.6, amp=0.3)


def _small_braid(c, x0, y0, sg, hair, key, lw):
    """戴帽子时耳下的两个小辫子：三节短麻花 + 红头绳 + 小发梢。"""
    sw = _sway(key, 0.5)
    for j in range(3):
        bx = x0 + sg * j * 1.2 + sw * j / 3
        by = y0 + 4 + j * 7.5
        r = 5.2 - j * 0.6
        shape(c, ell(bx, by, r, r * 0.85, 10), hair, f"{key}{j}", lw=lw * 0.65, amp=0.25)
        line(c, [(bx - r * 0.6, by - 1), (bx + r * 0.6, by + 1.5)], f"{key}w{j}", 0.9, darker(hair, 0.6), alpha=0.6)
    ex, ey = x0 + sg * 4 + sw, y0 + 27
    with keep():
        shape(c, ell(ex, ey - 2, 3.2, 2.4, 8), HAIR_TIE, key + "t", lw=lw * 0.45, amp=0.2)
    shape(c, [(ex - 3, ey), (ex + 3, ey), (ex + 2 + sg * 2.5, ey + 7), (ex - 2 + sg * 2.5, ey + 6)], hair, key + "tf",
          lw=lw * 0.5, amp=0.25)


def _long_hair_behind(c, style, x, y, hair, key, lw):
    """长发：在身体后面的一整片，从头顶垂到背中间。"""
    sw = _sway(key, 0.5)
    pts = ell(x, y - 1, 30, 29, 14, math.pi * 0.95, math.pi * 2.05)
    pts += [(x + 33, y + 20), (x + 37 + sw, y + 55), (x + 38 + sw, y + 84), (x + 26 + sw, y + 90), (x + 14 + sw, y + 86),
            (x - 14 + sw, y + 86), (x - 26 + sw, y + 90), (x - 38 + sw, y + 84), (x - 37 + sw, y + 55), (x - 33, y + 20)]
    shape(c, pts, hair, key + "long", lw=lw * 0.9, amp=0.6)


def _front_locks(c, x, y, hair, key, lw):
    sw = _sway(key, 0.4)
    for sg in (-1, 1):
        pts = [(x + sg * 21, y - 10), (x + sg * 28, y + 6), (x + sg * 30 + sw, y + 40), (x + sg * 27 + sw, y + 66),
               (x + sg * 21 + sw, y + 62), (x + sg * 21, y + 30), (x + sg * 18, y + 4)]
        shape(c, pts, hair, f"{key}fl{sg}", lw=lw * 0.8, amp=0.4)
        line(c, [(x + sg * 24, y + 10), (x + sg * 26 + sw, y + 50)], f"{key}fs{sg}", 1.1, darker(hair, 0.6), alpha=0.5)


def _hair_front(c, style, x, y, hair, key, lw):
    """头顶与刘海。"""
    hl = mix(hair, (1, 1, 1), 0.35)
    if style in ("bang_short", "bang_long"):
        cap = ell(x, y - 1, 28.5, 28, 14, math.pi * 1.04, math.pi * 1.96)
        cap += [(x + 26, y - 4)] + [(x + 24 - k * 4, y - 3 + (1.5 if k % 2 else -1)) for k in range(13)] + [(x - 26, y - 4)]
        shape(c, cap, hair, key + "cap", lw=lw * 0.9, amp=0.4)
        for k in range(-2, 3):
            line(c, [(x + k * 8, y - 22), (x + k * 9, y - 6)], f"{key}bs{k}", 1.1, darker(hair, 0.6), alpha=0.45)
        line(c, [(x - 14, y - 22), (x - 6, y - 25)], key + "shine", 2.2, hl, alpha=0.7)
        if style == "bang_long":
            _front_locks(c, x, y, hair, key, lw)
        return
    if style == "curtain_long":
        cap = ell(x, y - 1, 28.5, 28, 14, math.pi * 1.04, math.pi * 1.96)
        cap += [(x + 26, y + 6), (x + 20, y - 2), (x + 12, y - 12), (x + 3, y - 20), (x, y - 21), (x - 3, y - 20),
                (x - 12, y - 12), (x - 20, y - 2), (x - 26, y + 6)]
        shape(c, cap, hair, key + "cap", lw=lw * 0.9, amp=0.4)
        line(c, [(x, y - 28), (x, y - 20)], key + "part", 1.4, darker(hair, 0.6), alpha=0.6)
        for sg in (-1, 1):
            line(c, [(x + sg * 4, y - 22), (x + sg * 14, y - 12), (x + sg * 22, y + 2)], f"{key}cs{sg}", 1.2, darker(hair, 0.6),
                 alpha=0.5)
        line(c, [(x - 16, y - 22), (x - 8, y - 25)], key + "shine", 2.2, hl, alpha=0.7)
        _front_locks(c, x, y, hair, key, lw)
        return
    cap = ell(x, y - 1, 28.5, 28, 14, math.pi * 1.04, math.pi * 1.96)
    cap += [(x + 26, y - 5), (x + 20, y - 4), (x + 13, y - 9), (x + 5, y - 16), (x - 1, y - 9), (x - 9, y - 4),
            (x - 17, y - 2), (x - 25, y - 4)]
    shape(c, cap, hair, key + "cap", lw=lw * 0.9, amp=0.6)
    line(c, [(x + 5, y - 27), (x + 1, y - 18), (x - 6, y - 10)], key + "str1", 1.3, darker(hair, 0.6), alpha=0.55)
    line(c, [(x + 9, y - 25), (x + 14, y - 15), (x + 19, y - 8)], key + "str2", 1.3, darker(hair, 0.6), alpha=0.55)
    hl = mix(hair, (1, 1, 1), 0.35)
    line(c, [(x - 14, y - 22), (x - 6, y - 25)], key + "shine", 2.2, hl, alpha=0.7)
    if style == "braids":
        for sg in (-1, 1):
            _braid(c, x + sg * 22, y + 4, sg, hair, f"{key}br{sg}", lw)
    if style == "hat_braids":
        for sg in (-1, 1):
            _small_braid(c, x + sg * 25, y + 6, sg, hair, f"{key}sb{sg}", lw)


def _hair_back_view(c, style, y, hair, key, lw):
    if style in LONG_HAIR:
        sw = _sway(key, 0.5)
        pts = ell(0, y - 1, 29, 28, 14, math.pi * 0.95, math.pi * 2.05)
        pts += [(32, y + 20), (35 + sw, y + 55), (36 + sw, y + 84), (22 + sw, y + 90), (0 + sw, y + 86), (-22 + sw, y + 90),
                (-36 + sw, y + 84), (-35 + sw, y + 55), (-32, y + 20)]
        shape(c, pts, hair, key + "blong", lw=lw * 0.9, amp=0.6)
        for i in (-2, -1, 0, 1, 2):
            line(c, [(i * 7, y - 22), (i * 10 + sw, y + 80)], f"{key}bls{i}", 1.2, darker(hair, 0.65), alpha=0.45)
        return
    if style == "bang_short":
        pts = ell(0, y - 1, 28, 27, 14, math.pi * 0.98, math.pi * 2.02) + [(31, y + 20), (0, y + 22), (-31, y + 20)]
        shape(c, pts, hair, key + "bk", lw=lw * 0.9, amp=0.5)
        for i in (-1, 0, 1):
            line(c, [(i * 8, y - 24), (i * 10, y + 18)], f"{key}bs{i}", 1.3, darker(hair, 0.65), alpha=0.5)
        return
    pts = ell(0, y - 1, 28, 27, 14, math.pi * 0.98, math.pi * 2.02)
    if style == "flick":
        pts += [(31, y + 10), (32, y + 18), (37, y + 22), (30, y + 24), (-30, y + 24), (-37, y + 22), (-32, y + 18),
                (-31, y + 10)]
    elif style == "hat_braids":
        pts += [(29, y + 8), (18, y + 12), (-18, y + 12), (-29, y + 8)]
    elif style in ("sweep", "pony"):
        pts += [(31, y + 12), (37, y + 28), (26, y + 26), (16, y + 30), (5, y + 26), (-5, y + 30), (-16, y + 26),
                (-26, y + 30), (-37, y + 28), (-31, y + 12)]
    else:
        pts += [(26, y + 12), (0, y + 16), (-26, y + 12)]
    shape(c, pts, hair, key + "bk", lw=lw * 0.9, amp=0.6)
    for i in (-1, 0, 1):
        line(c, [(i * 8, y - 24), (i * 11, y + 12)], f"{key}bs{i}", 1.3, darker(hair, 0.65), alpha=0.5)
    if style == "pony":
        sw = _sway(key)
        shape(c, [(-8, y + 6), (8, y + 6), (10 + sw, y + 30), (4 + sw * 1.5, y + 52), (-4 + sw, y + 44), (-10, y + 22)],
              hair, key + "bpony", lw=lw * 0.9, amp=0.5)
        with keep():
            shape(c, ell(0, y + 7, 7, 4, 10), HAIR_TIE, key + "btie", lw=lw * 0.6, amp=0.3)
    if style == "braids":
        for sg in (-1, 1):
            _braid(c, sg * 18, y + 8, sg, hair, f"{key}bb{sg}", lw)
    if style == "hat_braids":
        for sg in (-1, 1):
            _small_braid(c, sg * 20, y + 8, sg, hair, f"{key}bsb{sg}", lw)


def girl(c, x, y, s=1.0, **kw):
    kw.setdefault("key", "girl")
    if "hair_style" not in kw:                 # 系列定稿：戴帽子 → A 侧分短发；不戴帽子 → 齐平短发、发尾微翘
        hatted = kw.get("hat", True) and kw.get("outfit") not in ("desert", "sea_pink", "sea_white")
        kw["hair_style"] = "sweep" if hatted else "flick"
    kw.setdefault("keep_color", True)
    kw.setdefault("round_face", True)
    kw.setdefault("pack", False)               # 第一章还没有背包，背包从后面章节开始
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


def mug(c, x, y, s, key, col=hexc("f0b64a"), heart=None, crack=False, crack_u=1.0):
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
        with keep():
            shape(c, pts, hexc("d9534a"), key + "ht", lw=1.6, amp=0.4)
    if crack and crack_u > 0:
        pts = [(-8, -30), (-2, -16), (-10, -4), (-3, 8), (-7, 18), (-4, 26)]
        n = max(2, int(round(1 + crack_u * (len(pts) - 1))))
        line(c, pts[:n], key + "ck", 2.6, INK)
        if crack_u >= 1:
            line(c, [(-10, -4), (-18, 2)], key + "ck2", 1.8, INK)
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


def suitcase(c, x, y, s, key="suit", col=hexc("8b6f9a"), handle=1.0, tilt=0.0, dust=0.0):
    """立着的行李箱，(x, y) 是轮子着地点的中心。"""
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s, s)
    lw = 3.0 / max(s, 0.3) ** 0.6
    hh = 90 * handle
    if hh > 4:
        line(c, [(-22, -150), (-22, -150 - hh), (22, -150 - hh), (22, -150)], key + "h", lw * 1.6)
    shape(c, rrect(-55, -150, 110, 140, 14), col, key + "b", lw=lw)
    for k in (-1, 1):
        line(c, [(k * 25, -146), (k * 25, -14)], f"{key}r{k}", lw * 0.8, darker(col, 0.75))
    for k in (-1, 1):
        shape(c, ell(k * 38, -5, 8, 8, 10), INK, f"{key}w{k}", lw=lw * 0.6)
    if dust > 0:
        r = random.Random(7)
        for i in range(int(40 * dust)):
            circle(c, r.uniform(-50, 50), r.uniform(-145, -20), 1.8, hexc("9c968c"), 0.8)
    c.restore()


def plane(c, x, y, s, key="pl", col=hexc("f4f2ec"), tail=hexc("c9553f"), face=None):
    """侧面的小飞机，机头朝右。face：在某个舷窗里画她的脸。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lw = 3.0 / max(s, 0.3) ** 0.6
    shape(c, [(-60, 10), (-120, -60), (-96, -60), (-40, -10)], tail, key + "t", lw=lw)
    shape(c, [(-150, -12), (140, -16), (190, 0), (140, 18), (-150, 14)], col, key + "b", lw=lw)
    shape(c, [(-20, 6), (40, 6), (-30, 70), (-60, 70)], darker(col, 0.92), key + "w", lw=lw)
    for k in range(7):
        circle(c, -100 + k * 34, -2, 6, hexc("9fc3dd"))
    if face is not None:
        fx = -100 + face * 34
        circle(c, fx, -2, 11, hexc("dff0f6"))
        with keep():
            circle(c, fx, 0, 7, SKIN)
            c.arc(fx, -6, 9, math.pi, 2 * math.pi)
            c.set_source_rgba(*STRAW, 1)
            c.fill()
    c.restore()


# ---------------------------------------------------------------- 旅途服装（按 2026-10 参考图定稿，原创绘制）
COSTUMES = {
    "folk": dict(name="想象 · 民族服饰", sleeve=(0.98, 0.97, 0.94), straw=True),
    "snow": dict(name="雪原 · 护耳毛线帽 + 刺绣斗篷", sleeve=hexc("6f93c4")),
    "desert": dict(name="沙漠 · 轻纱 + 珠宝头饰", sleeve=SKIN, bare_legs=True),
    "sea_pink": dict(name="海岛 · 度假长裙（粉色）", sleeve=SKIN, bare_legs=True),
    "sea_white": dict(name="海岛 · 针织镂空上下分离（白色）", sleeve=SKIN, bare_legs=True),
    "jungle": dict(name="雨林 · 探险帽 + 多袋夹克", sleeve=hexc("7d7a4a")),
}
FUR = (0.98, 0.97, 0.95)
GOLD = hexc("d8b04a")
RED = hexc("c9473b")
LEATHER = hexc("8a5a3a")
CREAM = (0.99, 0.97, 0.93)


def _flower(c, x, y, s, key, col=hexc("f6b8c8"), center=hexc("f7d34f")):
    for k in range(5):
        a = k * 2 * math.pi / 5 - math.pi / 2
        shape(c, ell(x + math.cos(a) * 5 * s, y + math.sin(a) * 5 * s, 5 * s, 4 * s, 8), col, f"{key}{k}", lw=1, amp=0.2)
    circle(c, x, y, 2 * s, center)


def _crossbody(c, oy, key, lw, side=1):
    line(c, [(-side * 14, -124 + oy), (side * 22, -70 + oy)], key + "strap", 2.2, darker(LEATHER, 0.8))
    shape(c, rrect(side * 16 - 12, -76 + oy, 24, 20, 4), LEATHER, key + "bag", lw=lw * 0.7, amp=0.3)
    line(c, [(side * 16 - 12, -70 + oy), (side * 16 + 12, -70 + oy)], key + "flap", 1.4, darker(LEATHER, 0.7))


def _basket(c, x, y, key, lw, flower=False):
    shape(c, [(x - 16, y), (x + 16, y), (x + 13, y + 24), (x - 13, y + 24)], hexc("d9b778"), key + "bk", lw=lw * 0.7, amp=0.4)
    for k in range(3):
        line(c, [(x - 15 + k, y + 6 + k * 6), (x + 15 - k, y + 6 + k * 6)], f"{key}w{k}", 1.0, hexc("a8843a"), alpha=0.8)
    c.new_path()
    c.arc(x, y, 11, math.pi, 2 * math.pi)
    c.set_source_rgba(*G(hexc("a8843a"))[:3], 1)
    c.set_line_width(2)
    c.stroke()
    if flower:
        _flower(c, x, y + 12, 0.7, key + "fl", (1, 1, 1))


def _boots(c, feet, key, lw, sock=None):
    for i, (hx, hy, fx, fy) in enumerate(feet):
        if sock:
            shape(c, rect(fx - 7, fy - 26, 14, 7), sock, f"{key}sk{i}", lw=lw * 0.5, amp=0.2)
        shape(c, [(fx - 6, fy - 20), (fx + 6, fy - 20), (fx + 7, fy - 2), (fx + 11, fy + 1), (fx - 8, fy + 1)], LEATHER,
              f"{key}bt{i}", lw=lw * 0.7, amp=0.3)
        for k in range(2):
            line(c, [(fx - 4, fy - 16 + k * 6), (fx + 4, fy - 14 + k * 6)], f"{key}lc{i}{k}", 1, CREAM)


def _costume_legs(c, outfit, feet, oy, key, lw):
    if outfit == "snow":
        _boots(c, feet, key, lw)
    elif outfit == "jungle":
        _boots(c, feet, key, lw, sock=hexc("efe6d0"))


def _costume_body(c, outfit, oy, key, lw, view):
    if outfit == "folk":
        teal, orange = hexc("2f6f7a"), hexc("e0703a")
        shape(c, [(-20, -126 + oy), (20, -126 + oy), (24, -84 + oy), (-24, -84 + oy)], CREAM, key + "blouse", lw=lw)
        shape(c, [(-20, -126 + oy), (-6, -126 + oy), (-4, -84 + oy), (-24, -84 + oy)], teal, key + "vL", lw=lw * 0.8)
        shape(c, [(20, -126 + oy), (6, -126 + oy), (4, -84 + oy), (24, -84 + oy)], teal, key + "vR", lw=lw * 0.8)
        shape(c, [(-24, -86 + oy), (24, -86 + oy), (40, -40 + oy), (-40, -40 + oy)], teal, key + "skirt", lw=lw)
        pts = [(-38 + k * 9.5, -48 + oy + (4 if k % 2 else -3)) for k in range(9)]
        line(c, pts, key + "zig", 2.6, hexc("f0c040"))
        line(c, [(-38, -42 + oy), (38, -42 + oy)], key + "hem", 3.4, orange)
        shape(c, rect(-25, -92 + oy, 50, 9), orange, key + "sash", lw=lw * 0.7, amp=0.4)
        shape(c, rect(-5, -93 + oy, 10, 11), GOLD, key + "buckle", lw=lw * 0.5, amp=0.2)
        for k in range(3):
            circle(c, -14 + k * 2, -112 + k * 8 + oy, 1.8, orange)
            circle(c, 14 - k * 2, -112 + k * 8 + oy, 1.8, orange)
    elif outfit == "snow":
        shape(c, [(-22, -84 + oy), (22, -84 + oy), (28, -38 + oy), (-28, -38 + oy)], CREAM, key + "skirt", lw=lw)
        line(c, [(-27, -44 + oy), (27, -44 + oy)], key + "sst", 2.6, RED)
        blue = hexc("6f93c4")
        shape(c, [(-20, -128 + oy), (20, -128 + oy), (40, -62 + oy), (-40, -62 + oy)], blue, key + "cape", lw=lw)
        for k in range(8):
            circle(c, -38 + k * 10.8, -63 + oy, 6, FUR)
        for k, (px, py) in enumerate(((-24, -86), (24, -86), (-12, -100), (12, -100))):
            line(c, [(px - 4, py + oy), (px + 4, py + oy)], f"{key}emb{k}a", 1.6, CREAM)
            line(c, [(px, py - 4 + oy), (px, py + 4 + oy)], f"{key}emb{k}b", 1.6, CREAM)
        if view == "front":
            _crossbody(c, oy, key, lw, side=1)
    elif outfit == "desert":
        shape(c, [(-15, -126 + oy), (15, -126 + oy), (17, -90 + oy), (-17, -90 + oy)], SKIN, key + "skin", lw=lw * 0.8)
        shape(c, [(-17, -116 + oy), (17, -116 + oy), (18, -98 + oy), (-18, -98 + oy)], CREAM, key + "top", lw=lw * 0.9)
        line(c, [(-17, -98 + oy), (17, -98 + oy)], key + "tg", 2.2, GOLD)
        for sg in (-1, 1):
            line(c, [(sg * 9, -116 + oy), (sg * 7, -128 + oy)], f"{key}st{sg}", 1.6, GOLD)
        shape(c, rect(-19, -94 + oy, 38, 6), GOLD, key + "belt", lw=lw * 0.6, amp=0.3)
        shape(c, [(-19, -90 + oy), (19, -90 + oy), (40, -20 + oy), (-40, -20 + oy)], CREAM + (0.92,), key + "sk1", lw=lw)
        shape(c, [(-10, -88 + oy), (30, -88 + oy), (48, -26 + oy), (6, -18 + oy)], hexc("a9d3cf") + (0.55,), key + "sk2", lw=lw * 0.6)
        for k in range(4):
            line(c, [(-16 + k * 10, -88 + oy), (-26 + k * 16, -22 + oy)], f"{key}fold{k}", 1, hexc("c9b48f"), alpha=0.6)
        if view == "front":
            _crossbody(c, oy, key, lw, side=-1)
    elif outfit == "sea_pink":
        pink = hexc("f2a6c4")
        shape(c, [(-15, -126 + oy), (15, -126 + oy), (17, -100 + oy), (-17, -100 + oy)], SKIN, key + "skin", lw=lw * 0.8)
        shape(c, [(-12, -126 + oy), (-3, -126 + oy), (0, -108 + oy), (3, -126 + oy), (12, -126 + oy), (18, -90 + oy), (-18, -90 + oy)],
              pink, key + "bodice", lw=lw)
        shape(c, [(-18, -92 + oy), (18, -92 + oy), (40, -12 + oy), (-34, -12 + oy)], pink, key + "skirt", lw=lw)
        shape(c, [(6, -90 + oy), (18, -90 + oy), (40, -12 + oy), (18, -12 + oy)], darker(pink, 0.92), key + "wrap", lw=lw * 0.6)
        r = random.Random(5)
        for k in range(14):
            px, py = r.uniform(-26, 30), r.uniform(-84, -18)
            if abs(px) < 18 + (py + 92) * 0.28:
                circle(c, px, py + oy, 2.2, (1, 0.96, 0.98), 0.9)
        line(c, [(-18, -92 + oy), (18, -92 + oy)], key + "waist", 2.2, darker(pink, 0.75))
        line(c, [(10, -60 + oy), (22, -14 + oy)], key + "slit", 1.4, darker(pink, 0.7))
        sw = _sway(key, 1.5)
        shape(c, [(-30, -40 + oy), (-34, -12 + oy), (-62 + sw * 2, -6 + oy), (-76 + sw * 3, -18 + oy), (-50 + sw, -30 + oy)],
              pink + (0.85,), key + "train", lw=lw * 0.6, amp=0.6)
        if view == "front":
            for sg in (-1, 1):
                shape(c, [(14, -92 + oy), (14 + sg * 10, -98 + oy), (14 + sg * 10, -86 + oy)], darker(pink, 0.85),
                      f"{key}bow{sg}", lw=lw * 0.5, amp=0.3)
            line(c, [(14, -91 + oy), (18 + sw, -66 + oy)], key + "tail1", 2.4, darker(pink, 0.85))
            line(c, [(14, -91 + oy), (22 + sw, -70 + oy)], key + "tail2", 2.4, darker(pink, 0.85))
    elif outfit == "sea_white":
        shape(c, [(-15, -126 + oy), (15, -126 + oy), (17, -92 + oy), (-17, -92 + oy)], SKIN, key + "skin", lw=lw * 0.8)
        shape(c, [(-18, -118 + oy), (18, -118 + oy), (19, -100 + oy), (-19, -100 + oy)], CREAM, key + "crop", lw=lw * 0.9)
        for k in range(6):
            c.new_path()
            c.arc(-14 + k * 5.6, -109 + oy, 1.8, 0, 2 * math.pi)
            c.set_source_rgba(*G(hexc("c9b48f"))[:3], 0.9)
            c.set_line_width(1)
            c.stroke()
        for sg in (-1, 1):
            line(c, [(sg * 9, -118 + oy), (sg * 7, -128 + oy)], f"{key}st{sg}", 1.4, CREAM)
        shape(c, [(-18, -90 + oy), (18, -90 + oy), (36, -12 + oy), (-36, -12 + oy)], CREAM, key + "skirt", lw=lw)
        r = random.Random(9)
        for k in range(22):
            px, py = r.uniform(-30, 30), r.uniform(-84, -18)
            if abs(px) < 16 + (py + 90) * 0.26 and not (8 < px < 18 and py > -56):
                c.new_path()
                c.arc(px, py + oy, 2.2, 0, 2 * math.pi)
                c.set_source_rgba(*G(hexc("c9b48f"))[:3], 0.8)
                c.set_line_width(1)
                c.stroke()
        line(c, [(12, -56 + oy), (22, -14 + oy)], key + "slit", 1.4, hexc("c9b48f"))
        line(c, [(-18, -90 + oy), (18, -90 + oy)], key + "waist", 2.2, hexc("e3d4b4"))
    elif outfit == "jungle":
        olive = hexc("7d7a4a")
        shape(c, [(-20, -126 + oy), (20, -126 + oy), (28, -64 + oy), (-28, -64 + oy)], olive, key + "bd", lw=lw)
        if view == "front":
            for sg in (-1, 1):
                shape(c, rect(sg * 13 - 7, -110 + oy, 14, 12), darker(olive, 0.85), f"{key}pk{sg}", lw=1.4, amp=0.3)
                shape(c, rect(sg * 16 - 8, -86 + oy, 16, 14), darker(olive, 0.85), f"{key}pl{sg}", lw=1.4, amp=0.3)
            shape(c, [(-10, -127 + oy), (0, -116 + oy), (10, -127 + oy)], darker(olive, 0.8), key + "collar", lw=1.4, amp=0.3)
            line(c, [(0, -116 + oy), (0, -66 + oy)], key + "zip", 1.4, darker(olive, 0.6))
            _crossbody(c, oy, key, lw, side=1)
        shape(c, [(-28, -66 + oy), (28, -66 + oy), (30, -46 + oy), (-30, -46 + oy)], darker(olive, 0.9), key + "shorts", lw=lw)
        shape(c, rect(-29, -69 + oy, 58, 6), LEATHER, key + "belt", lw=lw * 0.6, amp=0.3)


def _costume_neck(c, outfit, oy, key, lw, view):
    if outfit == "snow":
        shape(c, [(-22, -130 + oy), (22, -130 + oy), (20, -118 + oy), (-20, -118 + oy)], FUR, key + "fcol", lw=lw * 0.8)
        for sg in (-1, 1):
            line(c, [(sg * 6, -120 + oy), (sg * 8, -108 + oy)], f"{key}tie{sg}", 1.4, CREAM)
            circle(c, sg * 8, -106 + oy, 3, FUR)


def _costume_hands(c, outfit, hands, key, lw):
    if outfit in ("sea_pink", "sea_white"):
        hx, hy = hands[0]
        _basket(c, hx - 2, hy + 2, key + "bsk", lw, flower=outfit == "sea_white")


def _costume_head(c, outfit, x, y, key, lw, view, hat):
    if outfit == "snow":
        sw = _sway(key, 0.5)
        knit, blue = (0.98, 0.97, 0.95), hexc("4f6fa8")
        for sg in (-1, 1):
            shape(c, [(x + sg * 23, y - 8), (x + sg * 29, y - 4), (x + sg * 28, y + 4), (x + sg * 23, y + 3)], blue,
                  f"{key}flap{sg}", lw=lw * 0.8, amp=0.3)
            line(c, [(x + sg * 26, y + 4), (x + sg * 27 + sw, y + 30)], f"{key}cord{sg}", 1.8, CREAM)
            shape(c, ell(x + sg * 27 + sw, y + 34, 7, 7, 12), FUR, f"{key}ep{sg}", lw=lw * 0.5, amp=0.4)
        dome = ell(x, y - 4, 30, 28, 14, math.pi, 2 * math.pi) + [(x + 30, y - 2), (x - 30, y - 2)]
        shape(c, dome, knit, key + "dome", lw=lw)
        shape(c, rect(x - 30, y - 22, 60, 10), blue, key + "band1", lw=lw * 0.6, amp=0.3)
        for k in range(6):
            shape(c, [(x - 26 + k * 10, y - 13), (x - 21 + k * 10, y - 21), (x - 16 + k * 10, y - 13)], knit, f"{key}tri{k}",
                  ink=False)
        shape(c, rect(x - 30, y - 10, 60, 7), blue, key + "band2", lw=lw * 0.6, amp=0.3)
        shape(c, ell(x, y - 35, 11, 11, 12), FUR, key + "pom", lw=lw * 0.6, amp=0.5)
    elif outfit == "desert":
        sw = _sway(key, 1.2)
        veil = CREAM + (0.38,)
        if view == "back":
            shape(c, [(x - 26, y - 20), (x + 26, y - 20), (x + 46 + sw * 2, y + 90), (x - 40 + sw * 2, y + 96)], veil,
                  key + "veilB", lw=lw * 0.4, amp=0.8)
        else:
            for layer, (spread, a_) in enumerate(((1.0, 0.32), (0.7, 0.3))):
                for sg in (-1, 1):
                    w_ = 1 + 0.08 * math.sin(STATE["t"] * 2 + sg + layer)
                    pts = [(x + sg * 26, y - 22), (x + sg * (60 * spread) * w_ + sw * 3, y + 20),
                           (x + sg * (95 * spread) * w_ + sw * 5, y + 70), (x + sg * (88 * spread) + sw * 5, y + 96),
                           (x + sg * (62 * spread) + sw * 3, y + 104), (x + sg * (40 * spread) + sw * 2, y + 92),
                           (x + sg * 30, y + 20)]
                    shape(c, pts, CREAM + (a_,), f"{key}veil{sg}{layer}", lw=lw * 0.35, amp=0.8)
                    for k in range(3):
                        u = (k + 1) / 4
                        circle(c, lerp(x + sg * 30, x + sg * 95 * spread * w_ + sw * 5, u), y + 20 + u * 60, 1.4, GOLD, 0.7)
        pts = [(x - 26 + k * 52 / 12, y - 14 - 8 * math.sin(math.pi * k / 12)) for k in range(13)]
        line(c, pts, key + "chain", 1.8, GOLD)
        for k in range(1, 12, 2):
            px, py = pts[k]
            line(c, [(px, py), (px, py + 5)], f"{key}dr{k}", 1.2, GOLD)
            circle(c, px, py + 6, 1.8, GOLD)
        circle(c, x, y - 16, 3.6, hexc("2f8f8a"))
        line(c, [(x - 28, y - 18), (x - 10, y - 30), (x + 10, y - 30), (x + 28, y - 18)], key + "crown", 1.6, GOLD)
    elif outfit in ("sea_pink", "sea_white"):
        col = hexc("f6b8c8") if outfit == "sea_pink" else (1, 1, 1)
        if view != "back":
            _flower(c, x + 22, y - 12, 1.0, key + "hf", col)
        else:
            _flower(c, x - 20, y - 12, 0.9, key + "hfb", col)
    elif outfit == "jungle":
        helm = hexc("c9a46a")
        shape(c, ell(x, y - 20, 48, 11, 18), helm, key + "brim", lw=lw)
        shape(c, ell(x, y - 24, 26, 20, 16, math.pi, 2 * math.pi) + [(x + 26, y - 21), (x - 26, y - 21)], helm, key + "crown",
              lw=lw)
        shape(c, rect(x - 26, y - 28, 52, 7), RED, key + "hband", lw=lw * 0.6, amp=0.3)
        for k, rot in enumerate((0.5, 0.9)):
            c.save()
            c.translate(x + 22 + k * 4, y - 34 - k * 2)
            c.rotate(rot)
            shape(c, ell(0, 0, 10, 4, 10), hexc("4f9a4a"), f"{key}hl{k}", lw=1, amp=0.2)
            c.restore()

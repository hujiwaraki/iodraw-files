"""Drawing engine: helpers, character rig, props, subtitles, post effects (skia-python)."""
import math, os, random
import numpy as np
import skia

W, H = 1920, 1080
MODELS = os.environ.get("MODELS_DIR", "/tmp/claude-0/-home-user-iodraw-files/f68f4a23-b1f2-5f8c-b6cc-97aac70db429/scratchpad/models")

# ---------------------------------------------------------------- fonts
def _wght(tf, w):
    tag = (ord('w') << 24) | (ord('g') << 16) | (ord('h') << 8) | ord('t')
    VP = skia.FontArguments.VariationPosition
    vp = VP(VP.Coordinates([VP.Coordinate(tag, float(w))]))
    fa = skia.FontArguments(); fa.setVariationDesignPosition(vp)
    return tf.makeClone(fa)

TF = {
    "en": skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"),
    "en_b": skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-Bold.otf"),
    "en_xb": skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf") or skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-Bold.otf"),
    "en_r": skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-Regular.otf"),
    "zh": skia.Typeface.MakeFromFile(os.path.join(MODELS, "NotoSansSC-600.ttf")),
    "zh_b": skia.Typeface.MakeFromFile(os.path.join(MODELS, "NotoSansSC-800.ttf")),
    "zh_r": skia.Typeface.MakeFromFile(os.path.join(MODELS, "NotoSansSC-400.ttf")),
}
def font(kind, size):
    f = skia.Font(TF[kind], size); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias); return f

# ---------------------------------------------------------------- utils
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, t): return a + (b - a) * t
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_in(t): t = clamp(t); return t ** 3
def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else (1.0 if t >= b else 0.0)
def hexc(h, a=255):
    h = h.lstrip('#'); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(a))
def mix(h1, h2, t, a=255):
    h1 = h1.lstrip('#'); h2 = h2.lstrip('#')
    c = [int(lerp(int(h1[i:i+2], 16), int(h2[i:i+2], 16), clamp(t))) for i in (0, 2, 4)]
    return skia.Color(c[0], c[1], c[2], int(a))
def mixhex(h1, h2, t):
    h1 = h1.lstrip('#'); h2 = h2.lstrip('#')
    return '#' + ''.join('%02x' % int(lerp(int(h1[i:i+2], 16), int(h2[i:i+2], 16), clamp(t))) for i in (0, 2, 4))

def P(color, a=None, stroke=None, cap=True, blur=None):
    if isinstance(color, str): color = hexc(color, 255 if a is None else a)
    p = skia.Paint(AntiAlias=True, Color=color)
    if a is not None and not isinstance(color, int): pass
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        if cap: p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p

def lin(x0, y0, x1, y1, cols, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], [hexc(c) if isinstance(c, str) else c for c in cols], pos))
    return p
def rad(x, y, r, cols, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(x, y), r, [hexc(c) if isinstance(c, str) else c for c in cols], pos))
    return p

def rect(c, x, y, w, h, p): c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), p)
def rrect(c, x, y, w, h, r, p): c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), p)
def circle(c, x, y, r, p): c.drawCircle(x, y, r, p)
def line(c, x0, y0, x1, y1, p): c.drawLine(x0, y0, x1, y1, p)
def poly(c, pts, p, close=True):
    path = skia.Path(); path.moveTo(*pts[0])
    for q in pts[1:]: path.lineTo(*q)
    if close: path.close()
    c.drawPath(path, p)
def text(c, s, x, y, f, p, align="left"):
    w = f.measureText(s)
    if align == "center": x -= w / 2
    elif align == "right": x -= w
    c.drawString(s, x, y, f, p); return w

def shadow_ellipse(c, x, y, w, h, a=70):
    c.drawOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), P(skia.Color(0, 0, 0, a), blur=h * 0.35))

# ---------------------------------------------------------------- character rig
MING = dict(skin="#f2c9a0", skin_sh="#dca27a", hair="#1d1a22", top="#e8743b", top_sh="#c65a28",
            pants="#2d3b55", shoes="#f4f1ea", sole="#3a3a3a", hairstyle="ming", kid=True, hood=True)
WORKER = dict(skin="#c98e62", skin_sh="#a87048", hair="#2b2119", top="#3b4a5c", top_sh="#2c3846", pants="#3a3f47",
              shoes="#4a3424", sole="#222222", hairstyle="short", kid=False, vest=True, hardhat=True, beard=True)
STAFF = dict(skin="#f0c4a3", skin_sh="#d49c7c", hair="#5a3522", top="#2f5d8a", top_sh="#244a70", pants="#2a2f3a",
             shoes="#222222", sole="#111111", hairstyle="bob", kid=False, lanyard=True, blouse="#f4f1ea")
TEACHER = dict(skin="#f3cba8", skin_sh="#d8a483", hair="#1f1b1d", top="#7a5c8e", top_sh="#634a75", pants="#30303a",
               shoes="#2a2a2a", sole="#111111", hairstyle="bun", kid=False, glasses=True)

def rig_dims(p, s):
    if p.get("kid"):
        return dict(leg=118 * s, torso=118 * s, head=64 * s, sw=46 * s, hw=36 * s, limb=27 * s, arm=58 * s)
    return dict(leg=190 * s, torso=165 * s, head=56 * s, sw=58 * s, hw=44 * s, limb=30 * s, arm=82 * s)

def _limb(c, x0, y0, a1, a2, L, w, col, col_end=None, end_r=None):
    """two-segment limb from (x0,y0); angles in degrees measured from straight down, positive = toward +x."""
    x1 = x0 + math.sin(math.radians(a1)) * L; y1 = y0 + math.cos(math.radians(a1)) * L
    x2 = x1 + math.sin(math.radians(a1 + a2)) * L; y2 = y1 + math.cos(math.radians(a1 + a2)) * L
    path = skia.Path(); path.moveTo(x0, y0); path.lineTo(x1, y1); path.lineTo(x2, y2)
    c.drawPath(path, P(col, stroke=w))
    if col_end: circle(c, x2, y2, end_r or w * 0.55, P(col_end))
    return x2, y2

def draw_person(c, x, y, s, p, pose=None, t=0.0):
    """x,y = point between feet on floor. pose keys:
    face (-1..1), walk (phase or None), run(bool), sit(bool), legs_hidden(bool), arms (la1,la2,ra1,ra2),
    eyes ('open','wide','closed','happy','down'), brow ('neutral','worried','sad','raised','determined'),
    mouth ('smile','flat','frown','o','grin','small'), talk (0..1), blush (0..1), tilt (deg), lean (deg),
    backpack, look (dx,dy) pupils, sweat(0..1), earbuds(bool)"""
    q = dict(face=0.0, walk=None, run=False, sit=False, legs_hidden=False, arms=(8, 10, -8, -10), eyes="open",
             brow="neutral", mouth="smile", talk=0.0, blush=0.0, tilt=0.0, lean=0.0, backpack=False, look=(0, 0),
             sweat=0.0, earbuds=False, blink=True, scale_x=1.0)
    if pose: q.update(pose)
    d = rig_dims(p, s)
    c.save(); c.translate(x, y)
    if q["scale_x"] != 1.0: c.scale(q["scale_x"], 1.0)
    face = q["face"]
    bob = 0.0; lphase = 0.0
    if q["walk"] is not None:
        ph = q["walk"]; amp = 34 if q["run"] else 22
        lphase = math.sin(ph) * amp; bob = -abs(math.sin(ph)) * (9 if q["run"] else 5) * s
    hip_y = -d["leg"] * 2 * 0.97 + bob
    if q["sit"]: hip_y = -d["leg"] * 1.05
    # floor shadow
    if not q["legs_hidden"]:
        shadow_ellipse(c, 0, 0, d["sw"] * 3.2, 22 * s, 60)
    # legs
    if not q["legs_hidden"]:
        lw = d["limb"] * 1.12
        dirx_ = 1 if face >= 0 else -1
        for side, off in ((-1, 0.0), (1, math.pi)):
            hx = side * d["hw"] * 0.45
            if q["sit"]:
                a1 = 85 * dirx_; a2 = -85 * dirx_
            elif q["walk"] is not None:
                ph = q["walk"] + off; amp = 34 if q["run"] else 22; bend = 55 if q["run"] else 30
                a1 = math.sin(ph) * amp * dirx_
                a2 = -dirx_ * (0.5 + 0.5 * math.cos(ph + 0.9)) * bend
            else:
                a1, a2 = side * -3, 0
            L = d["leg"] * 0.97
            fx, fy = _limb(c, hx, hip_y, a1, a2, L, lw, p["pants"])
            # shoe
            dirx = 1 if face >= 0 else -1
            if abs(face) < 0.3 and q["walk"] is None and not q["sit"]: dirx = side * 0.4
            rrect(c, fx - 18 * s + dirx * 10 * s, fy - 10 * s, 40 * s, 22 * s, 10 * s, P(p["shoes"]))
            rect(c, fx - 18 * s + dirx * 10 * s, fy + 7 * s, 40 * s, 5 * s, P(p["sole"]))
    c.translate(0, hip_y)
    c.rotate(q["lean"])
    sh_y = -d["torso"]
    # backpack (behind)
    if q["backpack"]:
        bx = -face * d["sw"] * 0.9
        rrect(c, bx - d["sw"] * 0.85, sh_y + 10 * s, d["sw"] * 1.7, d["torso"] * 0.85, 22 * s, P("#3e7c6b"))
        rrect(c, bx - d["sw"] * 0.6, sh_y + d["torso"] * 0.45, d["sw"] * 1.2, d["torso"] * 0.3, 12 * s, P("#346a5b"))
    # arms behind torso (far arm)
    la1, la2, ra1, ra2 = q["arms"]
    arm_col = p["top_sh"]
    sx = d["sw"] * 0.92
    def arm(side, a1, a2, col):
        return _limb(c, side * sx, sh_y + 16 * s, a1, a2, d["arm"], d["limb"], col, p["skin"], d["limb"] * 0.62)
    far_side = 1 if face < 0 else -1
    far = (la1, la2) if far_side == -1 else (ra1, ra2)
    near = (ra1, ra2) if far_side == -1 else (la1, la2)
    near_side = -far_side
    if q["walk"] is not None:
        sw_ = math.sin(q["walk"]) * (40 if q["run"] else 24)
        far = (far[0] - sw_, far[1] - (40 if q["run"] else 12)) if not pose.get("arms_fixed") else far
        near = (near[0] + sw_, near[1] - (40 if q["run"] else 12)) if not pose.get("arms_fixed") else near
    hand_far = arm(far_side, far[0], far[1], arm_col)
    hand_far = (hand_far[0], hand_far[1] + hip_y)
    # torso
    tw = d["sw"]; path = skia.Path()
    path.moveTo(-tw, sh_y + 14 * s); path.quadTo(-tw, sh_y, -tw + 18 * s, sh_y)
    path.lineTo(tw - 18 * s, sh_y); path.quadTo(tw, sh_y, tw, sh_y + 14 * s)
    path.lineTo(d["hw"] * 1.02, 8 * s); path.lineTo(-d["hw"] * 1.02, 8 * s); path.close()
    tp = lin(0, sh_y, 0, 10 * s, [p["top"], p["top_sh"]])
    c.drawPath(path, tp)
    if p.get("hood"):
        # hoodie pocket & strings & hood rim
        rrect(c, -tw * 0.62 + face * 8 * s, -d["torso"] * 0.42, tw * 1.24, d["torso"] * 0.3, 10 * s, P(p["top_sh"]))
        poly(c, [(-tw * 0.75 + face * 10 * s, sh_y + 2 * s), (tw * 0.75 + face * 10 * s, sh_y + 2 * s), (face * 10 * s, sh_y + 26 * s)], P(p["top_sh"]))
        line(c, -8 * s + face * 12 * s, sh_y + 16 * s, -10 * s + face * 12 * s, sh_y + 52 * s, P("#f4f1ea", stroke=4 * s))
        line(c, 8 * s + face * 12 * s, sh_y + 16 * s, 10 * s + face * 12 * s, sh_y + 52 * s, P("#f4f1ea", stroke=4 * s))
    if p.get("blouse"):
        poly(c, [(-20 * s + face * 10 * s, sh_y), (20 * s + face * 10 * s, sh_y), (face * 10 * s, sh_y + 55 * s)], P(p["blouse"]))
    if p.get("vest"):
        vp = skia.Path(); vp.moveTo(-tw * 0.95, sh_y + 10 * s); vp.lineTo(-tw * 0.25 + face * 8 * s, sh_y)
        vp.lineTo(-tw * 0.2 + face * 8 * s, 6 * s); vp.lineTo(-d["hw"], 6 * s); vp.close()
        c.drawPath(vp, P("#f2c230"))
        vp2 = skia.Path(); vp2.moveTo(tw * 0.95, sh_y + 10 * s); vp2.lineTo(tw * 0.25 + face * 8 * s, sh_y)
        vp2.lineTo(tw * 0.2 + face * 8 * s, 6 * s); vp2.lineTo(d["hw"], 6 * s); vp2.close()
        c.drawPath(vp2, P("#f2c230"))
        for yy in (-d["torso"] * 0.42, -d["torso"] * 0.2):
            rect(c, -tw * 0.98, yy, tw * 0.75, 9 * s, P("#e6e9ee"))
            rect(c, tw * 0.23, yy, tw * 0.75, 9 * s, P("#e6e9ee"))
    if p.get("lanyard") or q.get("lanyard"):
        line(c, -16 * s + face * 10 * s, sh_y + 4 * s, face * 10 * s, sh_y + 70 * s, P("#d64545", stroke=4 * s))
        line(c, 16 * s + face * 10 * s, sh_y + 4 * s, face * 10 * s, sh_y + 70 * s, P("#d64545", stroke=4 * s))
        rrect(c, -15 * s + face * 10 * s, sh_y + 68 * s, 30 * s, 38 * s, 4 * s, P("#ffffff"))
        rect(c, -10 * s + face * 10 * s, sh_y + 76 * s, 20 * s, 8 * s, P("#3a7bd5"))
    if q["backpack"]:
        line(c, -tw * 0.55 + face * 6 * s, sh_y + 4 * s, -tw * 0.62 + face * 6 * s, -d["torso"] * 0.35, P("#2f6153", stroke=8 * s))
        line(c, tw * 0.55 + face * 6 * s, sh_y + 4 * s, tw * 0.62 + face * 6 * s, -d["torso"] * 0.35, P("#2f6153", stroke=8 * s))
    # head
    c.save(); c.translate(face * 4 * s, sh_y - 6 * s); c.rotate(q["tilt"])
    hr = d["head"]
    neck_h = 16 * s
    rect(c, -11 * s, -neck_h - 4 * s, 22 * s, neck_h + 8 * s, P(p["skin_sh"]))
    hc_y = -neck_h - hr * 0.92
    draw_head(c, 0, hc_y, hr, p, q, t, s)
    c.restore()
    hand_near = arm(near_side, near[0], near[1], p["top"])
    hand_near = (hand_near[0], hand_near[1] + hip_y)
    c.restore()
    return dict(hand_far=hand_far, hand_near=hand_near)

def draw_head(c, x, y, r, p, q, t, s):
    face = q["face"]; fx = face * r * 0.36
    # back hair / bun
    hs = p["hairstyle"]
    if hs == "bob":
        rrect(c, x - r * 1.12, y - r * 0.95, r * 2.24, r * 1.85, r * 0.6, P(p["hair"]))
    if hs == "bun":
        circle(c, x - face * r * 0.5, y - r * 1.0, r * 0.42, P(p["hair"]))
    # ears
    circle(c, x - r * 0.95 + fx * 0.4, y + r * 0.08, r * 0.2, P(p["skin_sh"]))
    circle(c, x + r * 0.95 + fx * 0.4, y + r * 0.08, r * 0.2, P(p["skin_sh"]))
    # face
    c.drawOval(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r * 1.04), rad(x + fx - r * 0.2, y - r * 0.3, r * 1.6, [mixhex(p["skin"], "#ffffff", 0.08), p["skin"], p["skin_sh"]], [0, 0.6, 1]))
    # hair front
    hp = skia.Path()
    if hs == "ming":
        hp.moveTo(x - r * 1.02, y + r * 0.05)
        hp.cubicTo(x - r * 1.15, y - r * 1.25, x + r * 1.15, y - r * 1.3, x + r * 1.02, y + r * 0.0)
        hp.lineTo(x + r * 0.85, y - r * 0.35)
        # fringe zigzag shifted with face
        pts = [(0.75, -0.32), (0.5, -0.22), (0.35, -0.42), (0.1, -0.2), (-0.05, -0.45), (-0.3, -0.25), (-0.45, -0.48), (-0.7, -0.3), (-0.88, -0.35)]
        for px, py in pts: hp.lineTo(x + (px + face * 0.25) * r, y + py * r)
        hp.close(); c.drawPath(hp, P(p["hair"]))
        # highlight
        hl = skia.Path(); hl.moveTo(x - r * 0.4 + fx * 0.3, y - r * 0.85); hl.quadTo(x + fx * 0.3, y - r * 1.02, x + r * 0.45 + fx * 0.3, y - r * 0.86)
        c.drawPath(hl, P(skia.Color(110, 105, 130, 110), stroke=r * 0.06))
    elif hs == "short":
        hp.moveTo(x - r * 1.0, y - r * 0.1); hp.cubicTo(x - r * 1.0, y - r * 1.2, x + r * 1.0, y - r * 1.2, x + r * 1.0, y - r * 0.1)
        hp.lineTo(x + r * 0.8, y - r * 0.5); hp.lineTo(x - r * 0.8 + fx * 0.3, y - r * 0.55); hp.close(); c.drawPath(hp, P(p["hair"]))
    elif hs == "bob":
        hp.moveTo(x - r * 1.05, y + r * 0.6); hp.cubicTo(x - r * 1.25, y - r * 1.3, x + r * 1.25, y - r * 1.3, x + r * 1.05, y + r * 0.6)
        hp.lineTo(x + r * 0.85, y + r * 0.1); hp.quadTo(x + r * 0.7 + fx, y - r * 0.6, x - r * 0.2 + fx, y - r * 0.55)
        hp.quadTo(x - r * 0.75, y - r * 0.45, x - r * 0.85, y + r * 0.1); hp.close(); c.drawPath(hp, P(p["hair"]))
    elif hs == "bun":
        hp.moveTo(x - r * 1.02, y - r * 0.0); hp.cubicTo(x - r * 1.1, y - r * 1.25, x + r * 1.1, y - r * 1.25, x + r * 1.02, y - r * 0.0)
        hp.quadTo(x + r * 0.6 + fx, y - r * 0.7, x + fx * 0.5, y - r * 0.62); hp.quadTo(x - r * 0.6, y - r * 0.6, x - r * 1.02, y); hp.close()
        c.drawPath(hp, P(p["hair"]))
    if p.get("hardhat"):
        hh = skia.Path(); hh.moveTo(x - r * 1.05, y - r * 0.35); hh.cubicTo(x - r * 1.05, y - r * 1.45, x + r * 1.05, y - r * 1.45, x + r * 1.05, y - r * 0.35); hh.close()
        c.drawPath(hh, lin(x, y - r * 1.4, x, y - r * 0.3, ["#ffd447", "#e8a91c"]))
        rrect(c, x - r * 1.25 + fx * 0.3, y - r * 0.42, r * 2.5, r * 0.16, r * 0.08, P("#e0a018"))
    # eyes
    ex = r * 0.38; ey = y + r * 0.05
    blink = False
    if q["blink"]:
        bt = (t * 1.0 + (hash(p["hair"]) % 7) * 0.37) % 3.7
        blink = bt < 0.12
    lx, ly = q["look"]
    for side in (-1, 1):
        cx = x + side * ex + fx
        sc = 1.0 - max(0, side * -face) * 0.18 if face != 0 else 1.0
        e = q["eyes"]
        if blink and e in ("open", "wide", "down"): e = "closed"
        if e == "closed":
            pth = skia.Path(); pth.moveTo(cx - r * 0.14, ey); pth.quadTo(cx, ey + r * 0.1, cx + r * 0.14, ey)
            c.drawPath(pth, P("#2a1f1f", stroke=r * 0.06))
        elif e == "happy":
            pth = skia.Path(); pth.moveTo(cx - r * 0.14, ey + r * 0.04); pth.quadTo(cx, ey - r * 0.12, cx + r * 0.14, ey + r * 0.04)
            c.drawPath(pth, P("#2a1f1f", stroke=r * 0.06))
        else:
            rr = r * (0.165 if e == "wide" else 0.13) * sc
            c.drawOval(skia.Rect.MakeXYWH(cx - rr, ey - rr * 1.2, rr * 2, rr * 2.4), P("#ffffff"))
            pr = rr * (0.62 if e == "wide" else 0.78)
            py = ey + (rr * 0.35 if e == "down" else 0) + ly * rr * 0.4
            circle(c, cx + lx * rr * 0.4 + face * rr * 0.2, py, pr, P("#2a1f1f"))
            circle(c, cx + lx * rr * 0.4 + face * rr * 0.2 - pr * 0.35, py - pr * 0.4, pr * 0.3, P("#ffffff"))
            if e == "down":
                c.drawOval(skia.Rect.MakeXYWH(cx - rr * 1.1, ey - rr * 1.4, rr * 2.2, rr * 1.2), P(p["skin"]))
                line(c, cx - rr, ey - rr * 0.25, cx + rr, ey - rr * 0.25, P("#2a1f1f", stroke=r * 0.04))
        # brows
        b = q["brow"]; by = ey - r * 0.3
        if b == "raised": by -= r * 0.1
        idy = {"neutral": 0, "worried": -0.08, "sad": -0.11, "raised": -0.02, "determined": 0.08}[b] * r
        line(c, cx + side * r * 0.16, by, cx - side * r * 0.13, by + idy, P(p["hair"], stroke=r * 0.07))
    if p.get("glasses"):
        for side in (-1, 1):
            circle(c, x + side * ex + fx, ey, r * 0.22, P("#2a2a2a", stroke=r * 0.05))
        line(c, x - ex + fx + r * 0.22, ey, x + ex + fx - r * 0.22, ey, P("#2a2a2a", stroke=r * 0.04))
    # nose
    pth = skia.Path(); pth.moveTo(x + fx * 1.15, y + r * 0.22); pth.quadTo(x + fx * 1.15 + face * r * 0.08 + r * 0.04, y + r * 0.32, x + fx * 1.1, y + r * 0.36)
    c.drawPath(pth, P(p["skin_sh"], stroke=r * 0.05))
    # blush
    if q["blush"] > 0:
        for side in (-1, 1):
            c.drawOval(skia.Rect.MakeXYWH(x + side * r * 0.58 + fx - r * 0.18, y + r * 0.3, r * 0.36, r * 0.18), P(skia.Color(232, 92, 92, int(150 * q["blush"])), blur=r * 0.06))
    # mouth
    mx = x + fx * 1.05; my = y + r * 0.56
    talk = q["talk"]; m = q["mouth"]
    if talk > 0.05:
        h = r * (0.05 + 0.2 * talk); w = r * (0.2 + 0.05 * talk)
        c.drawOval(skia.Rect.MakeXYWH(mx - w, my - h * 0.5, 2 * w, h * 1.3), P("#7a2e2e"))
        c.drawOval(skia.Rect.MakeXYWH(mx - w * 0.6, my + h * 0.2, 1.2 * w, h * 0.5), P("#d46a6a"))
    elif m == "smile":
        pth = skia.Path(); pth.moveTo(mx - r * 0.2, my - r * 0.02); pth.quadTo(mx, my + r * 0.14, mx + r * 0.2, my - r * 0.02)
        c.drawPath(pth, P("#7a2e2e", stroke=r * 0.06))
    elif m == "grin":
        pth = skia.Path(); pth.moveTo(mx - r * 0.24, my - r * 0.04); pth.quadTo(mx, my + r * 0.28, mx + r * 0.24, my - r * 0.04); pth.close()
        c.drawPath(pth, P("#7a2e2e"))
    elif m == "flat":
        line(c, mx - r * 0.14, my + r * 0.02, mx + r * 0.14, my + r * 0.02, P("#7a2e2e", stroke=r * 0.055))
    elif m == "small":
        line(c, mx - r * 0.07, my + r * 0.02, mx + r * 0.07, my + r * 0.02, P("#7a2e2e", stroke=r * 0.055))
    elif m == "frown":
        pth = skia.Path(); pth.moveTo(mx - r * 0.17, my + r * 0.08); pth.quadTo(mx, my - r * 0.06, mx + r * 0.17, my + r * 0.08)
        c.drawPath(pth, P("#7a2e2e", stroke=r * 0.06))
    elif m == "o":
        c.drawOval(skia.Rect.MakeXYWH(mx - r * 0.09, my - r * 0.06, r * 0.18, r * 0.2), P("#7a2e2e"))
    if p.get("beard"):
        pth = skia.Path(); pth.moveTo(x - r * 0.75 + fx, y + r * 0.35); pth.quadTo(x + fx, y + r * 1.25, x + r * 0.75 + fx, y + r * 0.35)
        pth.quadTo(x + fx, y + r * 0.9, x - r * 0.75 + fx, y + r * 0.35); c.drawPath(pth, P(p["hair"], a=200))
    if q["sweat"] > 0:
        sx_ = x + r * 0.95 + fx * 0.3; sy_ = y - r * 0.35 + (t * 30 % 20) * 0.5
        pth = skia.Path(); pth.moveTo(sx_, sy_ - r * 0.18); pth.quadTo(sx_ + r * 0.12, sy_, sx_, sy_ + r * 0.08); pth.quadTo(sx_ - r * 0.12, sy_, sx_, sy_ - r * 0.18)
        c.drawPath(pth, P(skia.Color(140, 200, 255, int(220 * q["sweat"]))))
    if q["earbuds"]:
        circle(c, x - r * 0.97 + fx * 0.4, y + r * 0.1, r * 0.1, P("#ffffff"))
        circle(c, x + r * 0.97 + fx * 0.4, y + r * 0.1, r * 0.1, P("#ffffff"))

# ---------------------------------------------------------------- props
def draw_robot(c, x, y, s, built=1.0, glow=0.0, t=0.0):
    """Small handmade solar robot standing on a surface at (x,y). built 0..1 reveals parts."""
    parts = 6; b = built * parts
    def show(i): return clamp(b - i)
    c.save(); c.translate(x, y)
    shadow_ellipse(c, 0, 0, 150 * s, 16 * s, 70)
    a = show(0)
    if a > 0:  # wheels / base
        for wx in (-45, 45):
            circle(c, wx * s, -18 * s, 18 * s, P("#2b2b33", a=int(255 * a)))
            circle(c, wx * s, -18 * s, 7 * s, P("#9aa3ad", a=int(255 * a)))
        rrect(c, -62 * s, -42 * s, 124 * s, 22 * s, 6 * s, P("#5b6573", a=int(255 * a)))
    a = show(1)
    if a > 0:  # body
        rrect(c, -48 * s, -120 * s, 96 * s, 80 * s, 12 * s, lin(0, -120 * s, 0, -40 * s, ["#d9dde3", "#a9b0ba"]))
        circle(c, -20 * s, -80 * s, 7 * s, P("#e8743b")); circle(c, 0, -80 * s, 7 * s, P("#3aa0d8")); circle(c, 20 * s, -80 * s, 7 * s, P("#62c26a"))
    a = show(2)
    if a > 0:  # head
        rrect(c, -36 * s, -178 * s, 72 * s, 52 * s, 14 * s, lin(0, -178 * s, 0, -126 * s, ["#e9ecef", "#b9c0c9"]))
        g = 0.6 + 0.4 * math.sin(t * 3) if glow > 0 else 0.4
        for ex in (-14, 14):
            circle(c, ex * s, -152 * s, 8 * s, P(mix("#1d5d7d", "#7fe3ff", g * max(glow, 0.3))))
    a = show(3)
    if a > 0:  # arms
        line(c, -48 * s, -105 * s, -78 * s, -70 * s, P("#7b8591", stroke=10 * s)); line(c, 48 * s, -105 * s, 78 * s, -130 * s, P("#7b8591", stroke=10 * s))
        circle(c, -80 * s, -66 * s, 9 * s, P("#e8743b")); circle(c, 80 * s, -134 * s, 9 * s, P("#e8743b"))
    a = show(4)
    if a > 0:  # antenna
        line(c, 0, -178 * s, 0, -205 * s, P("#7b8591", stroke=5 * s)); circle(c, 0, -210 * s, 8 * s, P("#e8743b"))
    a = show(5)
    if a > 0:  # solar panel on back
        c.save(); c.translate(-62 * s, -150 * s); c.rotate(-25)
        rect(c, -40 * s, -12 * s, 80 * s, 24 * s, P("#1f3d73"))
        for i in range(1, 4): line(c, -40 * s + i * 20 * s, -12 * s, -40 * s + i * 20 * s, 12 * s, P("#4d77b8", stroke=1.5 * s))
        c.restore()
    if glow > 0:
        c.drawCircle(0, -100 * s, 140 * s, P(skia.Color(127, 227, 255, int(40 * glow)), blur=50 * s))
    c.restore()

def draw_laptop(c, x, y, s, screen_fn=None, open_=1.0, glow=1.0):
    """laptop base centered at x, bottom y. screen_fn(c, sx, sy, sw, sh) draws screen content."""
    bw, bh = 520 * s, 26 * s
    rrect(c, x - bw / 2, y - bh, bw, bh, 8 * s, lin(0, y - bh, 0, y, ["#c9ced6", "#8f97a3"]))
    sw_, sh_ = 470 * s, 300 * s
    hh = sh_ * open_
    sx, sy = x - sw_ / 2, y - bh - hh
    rrect(c, sx - 12 * s, sy - 12 * s, sw_ + 24 * s, hh + 12 * s, 14 * s, P("#3b4049"))
    if open_ > 0.9:
        rect(c, sx, sy, sw_, hh - 2 * s, P("#f7f8fa"))
        if screen_fn:
            c.save(); c.clipRect(skia.Rect.MakeXYWH(sx, sy, sw_, hh - 2 * s)); screen_fn(c, sx, sy, sw_, hh - 2 * s); c.restore()
        if glow > 0:
            c.drawRect(skia.Rect.MakeXYWH(sx - 60 * s, sy - 60 * s, sw_ + 120 * s, hh + 120 * s), P(skia.Color(200, 225, 255, int(28 * glow)), blur=40 * s))
    return sx, sy, sw_, hh

def draw_window_night(c, x, y, w, h, t, day=0.0, rain=0.0):
    sky = lin(x, y, x, y + h, [mixhex("#0e1a33", "#8fc4ef", day), mixhex("#2a3560", "#d6ecfa", day)])
    rect(c, x, y, w, h, sky)
    # city silhouette
    rnd = random.Random(7)
    bx = x
    while bx < x + w:
        bw_ = rnd.uniform(40, 90); bh_ = rnd.uniform(h * 0.15, h * 0.5)
        rect(c, bx, y + h - bh_, bw_ - 6, bh_, P(mixhex("#141d36", "#9fb4c8", day)))
        for wy in range(int(y + h - bh_ + 12), int(y + h - 8), 22):
            for wx in range(int(bx + 8), int(bx + bw_ - 16), 18):
                if rnd.random() < 0.4 * (1 - day):
                    rect(c, wx, wy, 8, 10, P("#ffd98a", a=200))
        bx += bw_
    if day < 0.5:
        circle(c, x + w * 0.8, y + h * 0.2, 22, P("#f4ecd0", a=int(255 * (1 - day * 2))))
    if rain > 0:
        rr = random.Random(int(t * 24))
        for i in range(int(60 * rain)):
            rx = x + rr.random() * w; ry = y + rr.random() * h
            line(c, rx, ry, rx - 6, ry + 26, P(skia.Color(200, 220, 255, 90), stroke=2))
    # frame
    rect(c, x - 14, y - 14, w + 28, 14, P("#e7dccb")); rect(c, x - 14, y + h, w + 28, 22, P("#e7dccb"))
    rect(c, x - 14, y, 14, h, P("#e7dccb")); rect(c, x + w, y, 14, h, P("#e7dccb")); rect(c, x + w / 2 - 6, y, 12, h, P("#e7dccb"))

def draw_lamp(c, x, y, s, on=1.0):
    if on > 0:
        c.drawCircle(x + 60 * s, y - 120 * s, 420 * s, rad(x + 60 * s, y - 120 * s, 420 * s, [skia.Color(255, 214, 140, int(110 * on)), skia.Color(255, 214, 140, 0)]))
    rrect(c, x - 40 * s, y - 10 * s, 80 * s, 12 * s, 6 * s, P("#3a3f4a"))
    line(c, x, y - 8 * s, x + 20 * s, y - 140 * s, P("#3a3f4a", stroke=8 * s))
    line(c, x + 20 * s, y - 140 * s, x + 90 * s, y - 175 * s, P("#3a3f4a", stroke=8 * s))
    pth = skia.Path(); pth.moveTo(x + 60 * s, y - 200 * s); pth.lineTo(x + 140 * s, y - 175 * s); pth.lineTo(x + 115 * s, y - 130 * s); pth.close()
    c.drawPath(pth, P("#2f6f8f"))

def draw_book(c, x, y, w, h, col, open_=False, title=None):
    if open_:
        rrect(c, x, y, w, h, 6, P("#f6f1e4")); line(c, x + w / 2, y, x + w / 2, y + h, P("#d8cfb8", stroke=3))
        for i in range(6):
            line(c, x + 16, y + 18 + i * h / 8, x + w / 2 - 16, y + 18 + i * h / 8, P("#b9b2a2", stroke=3))
            line(c, x + w / 2 + 16, y + 18 + i * h / 8, x + w - 16, y + 18 + i * h / 8, P("#b9b2a2", stroke=3))
    else:
        rrect(c, x, y, w, h, 5, P(col)); rect(c, x + 6, y + h - 10, w - 12, 6, P("#f6f1e4"))
        if title: text(c, title, x + w / 2, y + h * 0.45, font("en_b", h * 0.22), P("#ffffff"), "center")

def draw_calendar(c, x, y, w, h, day_label, num, mon="JUNE", flip=0.0, red=False):
    rrect(c, x, y, w, h, 10, P("#fbfaf6")); rrect(c, x, y, w, h * 0.28, 10, P("#d64545")); rect(c, x, y + h * 0.18, w, h * 0.1, P("#d64545"))
    text(c, mon, x + w / 2, y + h * 0.19, font("en_b", h * 0.13), P("#ffffff"), "center")
    text(c, str(num), x + w / 2, y + h * 0.7, font("en_xb", h * 0.42), P("#d64545" if red else "#2c3340"), "center")
    text(c, day_label, x + w / 2, y + h * 0.9, font("en_b", h * 0.12), P("#5c6370"), "center")
    for i in range(2): circle(c, x + w * (0.3 + 0.4 * i), y + 6, 7, P("#555b66"))
    if flip > 0:
        # page flipping up
        c.save(); hh = h * 0.72 * (1 - flip)
        rect(c, x, y + h * 0.28, w, hh * 0.98, P(skia.Color(240, 236, 228, int(255 * (1 - flip * 0.5)))))
        c.restore()

def draw_clock(c, x, y, r, tmin):
    circle(c, x, y, r + 10, P("#3b4049")); circle(c, x, y, r, P("#fbfaf6"))
    for i in range(12):
        a = math.radians(i * 30); line(c, x + math.sin(a) * r * 0.82, y - math.cos(a) * r * 0.82, x + math.sin(a) * r * 0.93, y - math.cos(a) * r * 0.93, P("#3b4049", stroke=r * 0.05))
    am = math.radians(tmin * 6); ah = math.radians(tmin * 0.5)
    line(c, x, y, x + math.sin(ah) * r * 0.5, y - math.cos(ah) * r * 0.5, P("#2c3340", stroke=r * 0.07))
    line(c, x, y, x + math.sin(am) * r * 0.75, y - math.cos(am) * r * 0.75, P("#2c3340", stroke=r * 0.045))
    circle(c, x, y, r * 0.06, P("#d64545"))

# ---------------------------------------------------------------- post / overlays
_rng = np.random.default_rng(3)
_GRAIN = []
for i in range(6):
    g = (_rng.normal(0, 1, (H // 2, W // 2)) * 9 + 128).clip(0, 255).astype(np.uint8)
    rgba = np.dstack([g, g, g, np.full_like(g, 20)])
    _GRAIN.append(skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType))

def vignette(c, strength=1.0):
    c.drawRect(skia.Rect.MakeWH(W, H), rad(W / 2, H / 2, W * 0.72, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, int(150 * strength))], [0, 0.55, 1]))

def grain(c, fi):
    img = _GRAIN[fi % len(_GRAIN)]
    p = skia.Paint(); p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImageRect(img, skia.Rect.MakeWH(W, H), skia.SamplingOptions(), p)

def letterbox_fade(c, a):
    if a > 0: c.drawRect(skia.Rect.MakeWH(W, H), P(skia.Color(0, 0, 0, int(255 * clamp(a)))))

# ---------------------------------------------------------------- subtitles
EN_SIZE, ZH_SIZE = 50, 44
SUB_MAXW = 1560

def wrap_en(s, f, maxw=SUB_MAXW):
    if f.measureText(s) <= maxw: return [s]
    words = s.split(' '); best = None
    for i in range(1, len(words)):
        a = ' '.join(words[:i]); b = ' '.join(words[i:])
        wa, wb = f.measureText(a), f.measureText(b)
        if max(wa, wb) > maxw: continue
        score = max(wa, wb)
        if words[i - 1][-1] in '.?!:': score -= 600
        elif words[i - 1][-1] in ',;': score -= 200
        if len(words) - i < 3 or i < 3: score += 500  # avoid orphans
        if best is None or score < best[0]: best = (score, [a, b])
    return best[1] if best else [s]

def draw_subtitle(c, en, zh, alpha=1.0):
    if alpha <= 0: return
    fe = font("en", EN_SIZE); fz = font("zh", ZH_SIZE)
    en_lines = wrap_en(en, fe); zh_lines = [zh]
    gap_e = EN_SIZE * 1.22; gap_z = ZH_SIZE * 1.35
    total_h = len(en_lines) * gap_e + len(zh_lines) * gap_z + 8
    wmax = max([fe.measureText(l) for l in en_lines] + [fz.measureText(l) for l in zh_lines])
    bottom = H - 44
    top = bottom - total_h - 30
    a = int(255 * alpha)
    rrect(c, W / 2 - wmax / 2 - 36, top, wmax + 72, total_h + 30, 18, P(skia.Color(8, 10, 16, int(168 * alpha))))
    y = top + 18 + EN_SIZE * 0.95
    sh = P(skia.Color(0, 0, 0, int(160 * alpha)), blur=3)
    for l in en_lines:
        text(c, l, W / 2 + 2, y + 2, fe, sh, "center"); text(c, l, W / 2, y, fe, P(skia.Color(255, 255, 255, a)), "center"); y += gap_e
    y += 6 + ZH_SIZE * 0.15
    for l in zh_lines:
        text(c, l, W / 2 + 2, y + 2, fz, sh, "center"); text(c, l, W / 2, y, fz, P(skia.Color(255, 226, 140, a)), "center"); y += gap_z

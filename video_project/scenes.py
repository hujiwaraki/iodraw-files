"""All shots of the film. Each scene fn(c, t) draws a full 1920x1080 frame for global time t."""
import math, random
import skia
from engine import *
from timeline import T, END, TITLE_S, TITLE_E, COLD_AT, env

def S(l): return T[l][0]
def E(l): return T[l][1]
def lp(t, l, a=0.0, b=1.0):
    """progress through line l (0..1), optionally a sub-range"""
    s, e = T[l]; d = e - s
    return prog(t, s + a * d, s + b * d)

def camera(c, zoom=1.0, cx=W / 2, cy=H / 2, rot=0.0, shake=0.0, t=0.0):
    c.translate(W / 2, H / 2)
    if shake > 0:
        c.translate(math.sin(t * 71) * 14 * shake, math.cos(t * 53) * 10 * shake)
    if rot: c.rotate(rot)
    c.scale(zoom, zoom); c.translate(-cx, -cy)

# ------------------------------------------------------------------ extra cast (classmates)
KID2 = dict(MING, top="#3a7bd5", top_sh="#2c5fa6", hair="#2a2220", hairstyle="bob", hood=False, pants="#3b3b48")
KID3 = dict(MING, top="#62a86b", top_sh="#4b8a55", hair="#141414", hairstyle="short", hood=False, pants="#2d3b55")
KID4 = dict(MING, top="#d9b13b", top_sh="#b8932a", hair="#3a2a1e", hairstyle="bun", hood=False, pants="#4a3f5a", skin="#e9b892", skin_sh="#cf9670")
CROWD = [dict(STAFF, top=c_, top_sh=c_, hairstyle=h, lanyard=False, blouse=None) for c_, h in
         (("#6b7c8f", "short"), ("#8a6f6a", "bob"), ("#5f7a6a", "short"), ("#7c6f8f", "bun"), ("#8c8170", "short"))]

# ------------------------------------------------------------------ BEDROOM set
def bedroom_bg(c, t, mood=0.0, day=0.0, rain=0.0, notes=0, notes_fall=0.0):
    """mood: 0 warm evening, 1 cold blue sad. day: window daylight."""
    wall_top = mixhex(mixhex("#4a4063", "#2b3550", mood), "#cfd9e6", day * 0.8)
    wall_bot = mixhex(mixhex("#6e5a74", "#36415c", mood), "#e8e1d5", day * 0.8)
    rect(c, 0, 0, W, H, lin(0, 0, 0, H, [wall_top, wall_bot]))
    draw_window_night(c, 150, 120, 480, 360, t, day=day, rain=rain)
    # poster
    rrect(c, 1450, 110, 260, 340, 8, P(mixhex("#1f2a48", "#2a3a62", day)))
    circle(c, 1580, 250, 70, P("#e8743b")); c.drawOval(skia.Rect.MakeXYWH(1480, 235, 200, 30), P("#f2c230", stroke=6))
    circle(c, 1650, 170, 6, P("#ffffff")); circle(c, 1500, 380, 4, P("#ffffff")); circle(c, 1680, 400, 5, P("#ffffff"))
    text(c, "SPACE", 1580, 425, font("en_b", 30), P("#f4f1ea"), "center")
    # shelf
    rect(c, 760, 300, 420, 16, P("#8a6a4f"))
    cols = ["#d64545", "#3a7bd5", "#62a86b", "#d9b13b", "#7a5c8e", "#e8743b", "#5b6573"]
    xx = 775
    for i, col in enumerate(cols):
        hgt = 90 + (i * 37 % 40); rect(c, xx, 300 - hgt, 38, hgt, P(col)); xx += 44
    draw_sticky_notes(c, t, notes, notes_fall)
    # floor
    rect(c, 0, 900, W, 180, lin(0, 900, 0, H, [mixhex("#6b5446", "#3a3a48", mood), mixhex("#4d3b31", "#2a2a36", mood)]))

NOTE_POS = []
_r = random.Random(11)
for i in range(60):
    NOTE_POS.append((_r.uniform(700, 1420), _r.uniform(340, 640), _r.uniform(-12, 12), _r.choice(["#ffe27a", "#ffd0a8", "#c9f0a8", "#a8dcff"])))
NOTE_POS.sort(key=lambda p: abs(p[0] - 1060) + abs(p[1] - 470) * 1.5)
def draw_sticky_notes(c, t, n, fall=0.0):
    f = font("en_xb", 46)
    for i in range(int(min(n, len(NOTE_POS)))):
        x, y, a, col = NOTE_POS[i]
        drop = 0.0
        if fall > 0:
            k = clamp(fall * len(NOTE_POS) * 1.0 - (len(NOTE_POS) - 1 - i) * 0.6)
            k = clamp(fall * 3 - (i / len(NOTE_POS)) * 2)
            if k >= 1: continue
            drop = ease_in(k)
        c.save(); c.translate(x, y + drop * 500); c.rotate(a + drop * 80)
        pa = int(255 * (1 - drop))
        rect(c, -34 + 4, -34 + 6, 68, 68, P(skia.Color(0, 0, 0, int(60 * (1 - drop))), blur=4))
        rect(c, -34, -34, 68, 68, P(col, a=pa))
        text(c, "?", 0, 16, f, P(skia.Color(70, 60, 80, pa)), "center")
        c.restore()

def desk_front(c, y=760, x0=260, x1=1660, mood=0.0):
    rect(c, x0, y, x1 - x0, 26, P(mixhex("#a77b55", "#5a5a6a", mood * 0.6)))
    rect(c, x0 + 20, y + 26, x1 - x0 - 40, 300, lin(0, y, 0, y + 300, [mixhex("#8a6345", "#4a4a58", mood * 0.6), mixhex("#6b4a33", "#34343f", mood * 0.6)]))
    rect(c, x0 + 60, y + 60, 420, 120, P(mixhex("#7a5840", "#40404c", mood * 0.6))); circle(c, x0 + 270, y + 120, 10, P("#d9c2a0"))

# ------------------------------------------------------------------ title & cold open
def scene_cold(c, t):
    # Ming walking toward a closed repair area; shout; freeze
    lt = t
    c.save()
    k = ease(prog(lt, 0, 2.2))
    shake = 0.9 if 0.5 < lt < 0.9 or 1.15 < lt < 1.5 else 0.0
    camera(c, 1.5 + 0.1 * k, 1250 + 60 * k, 600, shake=shake, t=t)
    corridor_bg(c, t, panel_swing=1.0)
    corridor_fg(c, t)
    stopped = lt > 1.3
    mx = 1260 + min(lt, 1.3) * 110
    draw_person(c, mx, 900, 1.15, MING, dict(face=0.75, walk=None if stopped else lt * 7.5, backpack=True, lanyard=True,
                eyes="wide" if stopped else "open", look=(0.4, -0.6) if not stopped else (-0.8, 0), brow="raised" if stopped else "neutral",
                mouth="o" if stopped else "smile"), t)
    c.restore()
    if lt > 2.25: letterbox_fade(c, (lt - 2.25) / 0.3)

def scene_title(c, t):
    lt = t - TITLE_S; d = TITLE_E - TITLE_S
    rect(c, 0, 0, W, H, lin(0, 0, 0, H, ["#0d1220", "#1a1f33"]))
    a = clamp(lt / 0.5) * clamp((d - lt) / 0.5)
    sc = 1.0 + 0.04 * lt / d
    c.save(); c.translate(W / 2, H / 2 - 30); c.scale(sc, sc)
    text(c, "LATER", 0, 40, font("en_xb", 190), P(skia.Color(244, 241, 234, int(255 * a))), "center")
    text(c, "以后再说", 0, 150, font("zh_b", 74), P(skia.Color(232, 116, 59, int(255 * a))), "center")
    c.restore()
    rect(c, W / 2 - 160 * a, H / 2 + 175, 320 * a, 4, P(skia.Color(232, 116, 59, int(200 * a))))

# ------------------------------------------------------------------ BEDROOM scenes
def scene_bedroom(c, t):
    # L1-L3: English book -> "later" -> sticky "?" notes pile up while he plays with robot parts
    z = 1.0 + 0.06 * prog(t, S("L1") - 0.2, S("L4"))
    c.save(); camera(c, z, 960, 560)
    notes = 0
    if t > S("L3"): notes = 1 + 11 * lp(t, "L3")
    bedroom_bg(c, t, notes=notes)
    closed = t > S("L2") + 0.25
    # Ming
    arms = (18, 30, -18, -30)
    pose = dict(face=0.0, legs_hidden=True, eyes="down", brow="neutral", mouth="flat", tilt=-6)
    if t < S("L2"):
        pose.update(tilt=-8 + 3 * math.sin(t * 2), mouth="flat", eyes="down", arms=(35, 55, -35, -55))
    elif t < S("L3"):
        k = lp(t, "L2")
        pose.update(eyes="happy" if k > 0.3 else "open", mouth="grin", tilt=4, brow="raised", arms=(-40 + 60 * k, 20, -30, -40))
    else:
        k = lp(t, "L3")
        pose.update(eyes="open", mouth="smile", face=0.35, look=(0.8, 0.5), tilt=2, arms=(30, 50, -30 - 20 * math.sin(t * 6), -70))
        if k > 0.55: pose.update(look=(-0.3, -0.8), brow="raised", mouth="small", face=0.1)  # glances at the notes...
        if k > 0.8: pose.update(look=(0.8, 0.5), mouth="smile", face=0.35)   # ...and looks away again
    draw_person(c, 960, 1000, 1.25, MING, pose, t)
    desk_front(c)
    draw_lamp(c, 1420, 760, 1.0, on=1.0)
    # book: open -> closes and slides away
    if not closed:
        draw_book(c, 820, 700, 260, 70, "#3a7bd5", open_=True)
        text(c, "ENGLISH", 880, 690, font("en_b", 22), P("#ffffff", a=0), "center")
    else:
        k = ease_out(prog(t, S("L2") + 0.25, S("L2") + 0.9))
        draw_book(c, 840 - 420 * k, 700, 200, 56, "#3a7bd5", title="ENGLISH")
    # robot parts on the desk
    if t > S("L2") + 0.4:
        draw_robot(c, 1180, 760, 0.55, built=0.35, t=t)
    c.restore()
    vignette(c, 0.9)

def scene_build(c, t):
    k = lp(t, "L4")
    c.save(); camera(c, 1.25 + 0.08 * k, 1060, 520)
    day = 0.5 + 0.5 * math.sin(k * math.pi * 6 - math.pi / 2)
    bedroom_bg(c, t, day=day * 0.85, notes=12 + 8 * k)
    # calendar on wall flips through days
    draw_calendar(c, 1250, 330, 150, 170, ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"][int(k * 20) % 7], 1 + int(k * 21), mon="MAY")
    draw_person(c, 900, 1000, 1.25, MING, dict(face=0.55, legs_hidden=True, eyes="open", look=(0.9, 0.7), brow="determined", mouth="small",
                arms=(25, 40, -60 - 25 * math.sin(t * 9), -60 + 20 * math.sin(t * 9))), t)
    desk_front(c)
    draw_lamp(c, 1480, 760, 1.0, on=1 - day * 0.6)
    draw_robot(c, 1180, 760, 0.75, built=0.3 + 0.7 * k, glow=0.0, t=t)
    c.restore(); vignette(c, 0.8)

EMAIL_LINES = [("From:", "Young Makers Science Camp"), ("Subject:", "Your robot project")]
def email_screen(c, x, y, w, h, highlight=0.0, closed_msg=0.0, scroll=0.0):
    rect(c, x, y, w, h, P("#ffffff"))
    rect(c, x, y, w, 34, P("#e9edf2"))
    for i, col in enumerate(["#ff5f57", "#febc2e", "#28c840"]): circle(c, x + 22 + i * 22, y + 17, 7, P(col))
    fy = y + 76
    fb = font("en_b", 21); fr = font("en_r", 21)
    for k_, v in EMAIL_LINES:
        text(c, k_, x + 26, fy, fb, P("#5c6370")); text(c, v, x + 130, fy, fr, P("#2c3340")); fy += 32
    line(c, x + 20, fy - 12, x + w - 20, fy - 12, P("#dde2e8", stroke=2))
    fy += 18
    body = ["Hi Ming,", "Thank you for your interest in our camp!", "Sign up by Friday, June 14.", "Upload one photo of your project.", "Late sign-ups cannot be accepted."]
    for i, b in enumerate(body):
        if i == 2 and highlight > 0:
            rect(c, x + 20, fy - 26, (fr.measureText(b) + 16) * highlight, 36, P("#ffe27a"))
        text(c, b, x + 26, fy, font("en_b", 22) if i == 2 else fr, P("#2c3340")); fy += 38
    if closed_msg > 0:
        a = int(255 * closed_msg)
        rrect(c, x + 20, y + h - 96 + (1 - closed_msg) * 30, w - 40, 76, 10, P(skia.Color(253, 236, 236, a)))
        rect(c, x + 20, y + h - 96 + (1 - closed_msg) * 30, 8, 76, P(skia.Color(214, 69, 69, a)))
        text(c, "Registration is now closed.", x + 44, y + h - 50 + (1 - closed_msg) * 30, font("en_b", 24), P(skia.Color(160, 40, 40, a)))

def scene_email(c, t):
    if t < S("L6") - 0.25:
        # close-up of laptop screen, email slides in with a ding
        k = ease_out(prog(t, S("L5") - 0.2, S("L5") + 0.6))
        c.save(); camera(c, 1.0 + 0.05 * lp(t, "L5", 0, 1.3), 960, 540)
        rect(c, 0, 0, W, H, lin(0, 0, 0, H, ["#262b3d", "#151827"]))
        sx, sy, sw_, sh_ = 360, 110, 1200, 760
        rrect(c, sx - 30, sy - 30, sw_ + 60, sh_ + 60, 26, P("#30353f"))
        rect(c, sx, sy, sw_, sh_, P("#f3f5f8"))
        c.save(); c.clipRect(skia.Rect.MakeXYWH(sx, sy, sw_, sh_))
        c.translate(0, (1 - k) * 80)
        c.save(); c.translate(sx + 120, sy + 60); c.scale(1.45, 1.45)
        email_screen(c, 0, 0, 660, 420)
        c.restore(); c.restore()
        c.drawRect(skia.Rect.MakeXYWH(sx, sy, sw_, sh_), P(skia.Color(255, 255, 255, int(120 * (1 - k)))))
        c.restore(); vignette(c, 1.0)
    else:
        # Ming lit by the screen, confused; shrugs and closes the laptop: "Later."
        k = lp(t, "L6")
        c.save(); camera(c, 1.35, 960, 560)
        bedroom_bg(c, t, mood=0.25, notes=20)
        frown = k < 0.55
        pose = dict(face=0.0, legs_hidden=True, eyes="open", look=(0, 0.6), brow="worried" if frown else "neutral",
                    mouth="frown" if frown else "flat", tilt=-6 if frown else 3, arms=(30, 60, -30, -60))
        if 0.3 < k < 0.55: pose.update(look=(0.6, 0.2), brow="worried", tilt=-10)
        if k >= 0.55: pose.update(eyes="happy", mouth="smile", arms=(20, 40, -50, -70))
        draw_person(c, 960, 1000, 1.25, MING, pose, t)
        # screen glow on face
        c.drawCircle(960, 520, 260, P(skia.Color(160, 200, 255, int(70 * (1 - prog(k, 0.6, 0.75)))), blur=80))
        desk_front(c, mood=0.25)
        lid = 1 - ease(prog(k, 0.62, 0.78))
        # back of laptop (facing camera)
        lh = 120 * lid
        rrect(c, 960 - 200, 760 - 18 - lh, 400, lh + 6, 14, lin(0, 760 - lh, 0, 760, ["#b9c0c9", "#8e96a2"]))
        rrect(c, 960 - 250, 760 - 22, 500, 24, 8, P("#8f97a3"))
        draw_lamp(c, 1420, 760, 1.0, on=0.8)
        c.restore(); vignette(c, 1.0)

def scene_monday(c, t):
    k = lp(t, "L7")
    if k < 0.42:
        kk = k / 0.42
        days = [("WED", 12), ("THU", 13), ("FRI", 14), ("SAT", 15), ("SUN", 16), ("MON", 17)]
        i = min(int(kk * 6.5), 5); f = (kk * 6.5) % 1 if i < 5 else 0
        c.save(); camera(c, 1.0 + 0.08 * kk, 960, 520)
        rect(c, 0, 0, W, H, lin(0, 0, 0, H, ["#5a6276", "#3a4052"]))
        d, n = days[i]
        draw_calendar(c, 960 - 220, 260, 440, 500, d, n, mon="JUNE", red=(d == "FRI"))
        if f > 0.7 and i < 5:
            ff = (f - 0.7) / 0.3
            c.save(); c.translate(0, -ff * 300); c.rotate(-ff * 8)
            rect(c, 960 - 220, 260 + 140, 440, 360 * (1 - ff), P(skia.Color(250, 250, 246, int(255 * (1 - ff)))))
            c.restore()
        c.restore(); vignette(c, 1.0)
    else:
        kk = (k - 0.42) / 0.58
        c.save(); camera(c, 1.08 + 0.1 * kk, 960, 470)
        rect(c, 0, 0, W, H, lin(0, 0, 0, H, ["#262b3d", "#151827"]))
        sx, sy, sw_, sh_ = 360, 110, 1200, 760
        rrect(c, sx - 30, sy - 30, sw_ + 60, sh_ + 60, 26, P("#30353f"))
        c.save(); c.clipRect(skia.Rect.MakeXYWH(sx, sy, sw_, sh_))
        rect(c, sx, sy, sw_, sh_, P("#f3f5f8"))
        c.translate(sx + 120, sy + 60); c.scale(1.45, 1.45)
        email_screen(c, 0, 0, 660, 420, highlight=ease(prog(kk, 0.25, 0.65)), closed_msg=ease_out(prog(t, E("L7") + 0.1, E("L7") + 0.5)))
        c.restore(); c.restore(); vignette(c, 1.0)

def scene_loss(c, t):
    k = prog(t, S("L8"), S("L9") - 0.3)
    c.save(); camera(c, 1.0 + 0.18 * ease(k), 1150 - 80 * k, 600)
    bedroom_bg(c, t, mood=1.0, rain=1.0, notes=20)
    # bed on left
    rrect(c, 140, 760, 620, 150, 20, P("#3f4a6a")); rrect(c, 140, 720, 620, 70, 20, P("#56638a")); rrect(c, 160, 690, 160, 60, 18, P("#c9d0e0"))
    draw_person(c, 470, 905, 1.2, MING, dict(face=0.4, sit=True, eyes="down", brow="sad", mouth="frown", tilt=-12, arms=(55, -40, 10, -20)), t)
    desk_front(c, x0=980, x1=1800, mood=1.0)
    draw_lamp(c, 1650, 760, 1.0, on=0.7)
    draw_robot(c, 1300, 760, 0.85, built=1.0, glow=0.35, t=t)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), P(skia.Color(20, 30, 70, 50)))
    vignette(c, 1.3)
    if t > S("L9") - 0.6: letterbox_fade(c, (t - (S("L9") - 0.6)) / 0.6)

# ------------------------------------------------------------------ MUSEUM sets
def museum_bg(c, t, cool=0.0):
    rect(c, 0, 0, W, H, lin(0, 0, 0, 760, [mixhex("#dfe9f2", "#9aa7b8", cool), mixhex("#f3efe6", "#b5b7bf", cool)]))
    # tall windows
    for i in range(6):
        x = 120 + i * 300
        rect(c, x, 80, 160, 520, lin(0, 80, 0, 600, [mixhex("#bfe0ff", "#8aa0b8", cool), mixhex("#e8f4ff", "#a8b4c4", cool)]))
        line(c, x + 80, 80, x + 80, 600, P("#ffffff", stroke=6))
        c.drawRect(skia.Rect.MakeXYWH(x - 40, 80, 240, 700), P(skia.Color(255, 255, 255, int(28 * (1 - cool))), blur=40))
    # floor
    rect(c, 0, 760, W, 320, lin(0, 760, 0, H, [mixhex("#cbbfae", "#8f8a86", cool), mixhex("#a99a86", "#6f6b6a", cool)]))
    for i in range(-10, 30):
        line(c, i * 120, 760, i * 120 - 500, H, P(skia.Color(255, 255, 255, 30), stroke=2))

def scene_trip(c, t):
    k = prog(t, S("L9") - 0.4, S("L10"))
    c.save(); camera(c, 1.0, 960 + 120 * k, 540)
    museum_bg(c, t)
    # banner
    rrect(c, 640, 140, 760, 120, 12, P("#1f3d73"))
    text(c, "SCIENCE MUSEUM", 1020, 222, font("en_xb", 68), P("#ffffff"), "center")
    # hanging planets
    for i, (px, py, pr, col) in enumerate([(300, 330, 60, "#e8743b"), (1600, 300, 80, "#3a7bd5"), (1850, 420, 40, "#d9b13b")]):
        line(c, px, 0, px, py - pr, P("#888888", stroke=2)); circle(c, px + math.sin(t + i) * 4, py, pr, P(col))
    # class group walking right
    base = 300 + k * 700
    group = [(TEACHER, 1.0, 0.85, 0), (KID2, 1.0, 1.0, 1.1), (KID3, 1.0, 1.0, 2.3), (MING, 1.0, 1.0, 0.6), (KID4, 1.0, 1.0, 1.7)]
    xs = [330, 120, -60, -250, -430]
    for (p, _, s, ph), dx in zip(group, xs):
        extra = dict(backpack=True, lanyard=True) if p is MING else dict(backpack=p.get("kid", False))
        pose = dict(face=0.7, walk=t * 7 + ph, eyes="open", mouth="smile", **extra)
        if p is MING: pose.update(look=(0.5, -0.8), mouth="o", eyes="wide", brow="raised")
        if p is TEACHER: pose.update(arms=(10, 10, 160, 0), arms_fixed=True)
        hands = draw_person(c, base + dx, 940, s * (0.95 if p is TEACHER else 1.05), p, pose, t)
        if p is TEACHER:
            hx, hy = hands["hand_near"]; hx += base + dx; hy += 940
            line(c, hx, hy + 20, hx, hy - 120, P("#555b66", stroke=5))
            poly(c, [(hx, hy - 120), (hx + 70, hy - 100), (hx, hy - 80)], P("#e8743b"))
    # teacher's flag
    c.restore(); vignette(c, 0.6)
    if t < S("L9") - 0.3: letterbox_fade(c, 1 - (t - (S("L9") - 0.6)) / 0.3)

def corridor_bg(c, t, panel_swing=1.0, panel_fall=0.0, dust=0.0, cool=0.0):
    rect(c, -600, -300, W * 2 + 1200, H + 300, lin(0, 0, 0, 760, [mixhex("#d7dde4", "#9aa3ae", cool), mixhex("#eeeae2", "#b5b3b0", cool)]))
    # exhibits on left wall
    for i, x in enumerate([120, 470, 820]):
        rrect(c, x, 260, 260, 200, 10, P("#2c3340")); rrect(c, x + 12, 272, 236, 176, 6, P(["#3a7bd5", "#62a86b", "#7a5c8e"][i]))
        circle(c, x + 130, 360, 50 + 6 * math.sin(t * 2 + i), P("#ffffff", a=110))
    # repair area to the right (x 1250..2000)
    rect(c, 1250, 0, 900, 120, P("#4a4f58"))   # opened ceiling
    for i in range(5):
        cx_ = 1300 + i * 140
        pth = skia.Path(); pth.moveTo(cx_, 110); pth.quadTo(cx_ + 30, 230 + 30 * math.sin(t * 2 + i), cx_ + 60, 150)
        c.drawPath(pth, P(["#d64545", "#2c3340", "#f2c230", "#2c3340", "#3a7bd5"][i], stroke=6))
    # spark
    if int(t * 10) % 7 in (0, 1):
        sx_, sy_ = 1580, 240
        for a in range(0, 360, 40):
            line(c, sx_, sy_, sx_ + math.cos(math.radians(a + t * 300)) * 26, sy_ + math.sin(math.radians(a + t * 300)) * 26, P("#ffe27a", stroke=3))
        circle(c, sx_, sy_, 10, P("#fff6c0"))
    # ladder
    line(c, 1820, 300, 1760, 900, P("#9aa3ad", stroke=12)); line(c, 1900, 300, 1960, 900, P("#9aa3ad", stroke=12))
    for i in range(7):
        yy = 340 + i * 80; line(c, 1820 - (yy - 300) * 0.1, yy, 1900 + (yy - 300) * 0.1, yy, P("#9aa3ad", stroke=9))
    # floor
    rect(c, -600, 760, W * 2 + 1200, 900, lin(0, 760, 0, H, [mixhex("#bdb3a6", "#8a8580", cool), mixhex("#a39888", "#6f6b6a", cool)]))
    # hanging loose panel
    px, py = 1440, 120
    if panel_fall <= 0:
        ang = 28 + 6 * math.sin(t * 3.5) * panel_swing
        c.save(); c.translate(px - 120, py); c.rotate(ang)
        rect(c, 0, 0, 330, 40, P("#5d6672")); rect(c, 0, 0, 330, 8, P("#9aa3ad")); rect(c, 0, 32, 330, 8, P("#3e454e")); rrect(c, 110, 40, 110, 24, 6, P("#fff6c0"))
        c.restore()
        line(c, px + 110, py, px + 60, py + 60, P("#2c3340", stroke=4))
    else:
        fy = py + ease_in(min(panel_fall, 1.0)) * 750
        c.save(); c.translate(px - 120, fy); c.rotate(28 + 60 * min(panel_fall, 1.0))
        if panel_fall >= 1.0:
            c.restore(); c.save(); c.translate(px - 170, 872); c.rotate(-4)
        rect(c, 0, 0, 330, 40, P("#5d6672")); rect(c, 0, 0, 330, 8, P("#9aa3ad")); rect(c, 0, 32, 330, 8, P("#3e454e")); rrect(c, 110, 40, 110, 24, 6, P("#fff6c0"))
        c.restore()
    if dust > 0:
        for i in range(14):
            a = i / 14 * math.pi
            r_ = 40 + dust * 260
            circle(c, px + math.cos(a) * r_ * 1.4 - 10, 890 - math.sin(a) * r_ * 0.35, 30 + dust * 50, P(skia.Color(220, 214, 204, int(150 * (1 - dust))), blur=20))

def corridor_fg(c, t):
    # barrier stands with stripes + sign
    for bx in (1200, 1560):
        line(c, bx, 760, bx, 900, P("#2c3340", stroke=10)); line(c, bx + 260, 760, bx + 260, 900, P("#2c3340", stroke=10))
        c.save(); c.clipRect(skia.Rect.MakeXYWH(bx - 10, 760, 280, 44))
        rect(c, bx - 10, 760, 280, 44, P("#f2c230"))
        for i in range(-2, 12):
            poly(c, [(bx + i * 40, 760), (bx + i * 40 + 20, 760), (bx + i * 40 - 24, 804), (bx + i * 40 - 44, 804)], P("#1f1f1f"))
        c.restore()
    # sign on stand
    sx, sy = 1170, 470
    line(c, sx + 110, sy + 220, sx + 110, 900, P("#2c3340", stroke=10))
    rrect(c, sx, sy, 220, 230, 10, P("#f2c230")); rrect(c, sx + 10, sy + 10, 200, 210, 6, P("#f2c230", stroke=6))
    poly(c, [(sx + 110, sy + 26), (sx + 150, sy + 90), (sx + 70, sy + 90)], P("#1f1f1f")); text(c, "!", sx + 110, sy + 84, font("en_xb", 50), P("#f2c230"), "center")
    for i, s_ in enumerate(["CLOSED FOR", "REPAIRS", "DO NOT ENTER"]):
        text(c, s_, sx + 110, sy + 132 + i * 34, font("en_xb", 28 if i < 2 else 23), P("#1f1f1f"), "center")

def scene_danger(c, t):
    s10, s11, s12 = S("L10"), S("L11"), S("L12")
    fall_t = s12 + 1.25
    panel_fall = prog(t, fall_t, fall_t + 0.45) if t > fall_t else 0.0
    if t > fall_t + 0.45: panel_fall = 1.0
    dust = prog(t, fall_t + 0.45, fall_t + 1.6) if t > fall_t + 0.45 else 0.0
    shake = 1.0 * (1 - prog(t, fall_t + 0.45, fall_t + 1.0)) if fall_t + 0.45 < t < fall_t + 1.0 else 0.0
    if t < s11:
        zoom, cx = 1.0, 960
    elif t < s12:
        zoom, cx = 1.0 + 0.25 * ease(prog(t, s11, s12)), 960 + 220 * ease(prog(t, s11, s12))
    else:
        kz = ease(prog(t, s12, s12 + 1.1))
        zoom, cx = 1.25 - 0.4 * kz, 1180 - 30 * kz
    cy = 560 + 110 * (ease(prog(t, s12, s12 + 1.1)) if t > s12 else 0)
    c.save(); camera(c, zoom, cx, cy, shake=shake, t=t)
    corridor_bg(c, t, panel_fall=panel_fall, dust=0)
    corridor_fg(c, t)
    # Ming path: walks right toward the gap between barriers (x~1500) and under the panel
    grab = s12 + 1.0
    if t < grab:
        mx = 640 + (t - s10) * ((1450 - 640) / (grab - s10))
        walking = True
    else:
        k = ease_out(prog(t, grab, grab + 0.5)); mx = 1450 - 330 * k; walking = False
    mpose = dict(face=0.75, walk=t * 7 if walking else None, backpack=True, lanyard=True, look=(0.5, -0.9), eyes="open", mouth="smile")
    if t < s11 and t > s10 + 0.2: mpose.update(look=(-0.4, 0), brow="raised", mouth="small")  # hears something, doesn't get it
    if s11 < t < s11 + 1.6: mpose.update(face=0.3, look=(-0.9, 0), brow="worried", mouth="flat")  # glances back, confused
    if t >= grab: mpose.update(face=-0.3, eyes="wide", brow="raised", mouth="o", look=(0.9, 0), lean=-8 * (1 - prog(t, grab + 0.7, grab + 1.4)))
    # Worker: at left shouting during L10, then running at L12
    if t < s12:
        wx = 260 + 140 * prog(t, s10, s11 + 3); wpose = dict(face=0.7, walk=(t * 5) if t > s10 + 2.5 else None,
                 arms=(20, 20, 100, 10) if t < s11 + 0.3 else (15, 20, -40, -20), talk=env("L10", t), brow="worried", mouth="flat", arms_fixed=True)
    else:
        k = prog(t, s12, grab)
        if t < grab:
            wx = lerp(470, mx - 160, ease_in(k) * 0.4 + k * 0.6); wpose = dict(face=0.8, walk=t * 11, run=True, brow="worried", mouth="o", arms=(20, 30, -20, -30))
        else:
            wx = mx - 200; wpose = dict(face=0.7, arms=(20, 20, 85, 5), brow="worried", mouth="flat", arms_fixed=True)
    draw_person(c, wx, 920, 0.95, WORKER, wpose, t)
    draw_person(c, mx, 930, 1.05, MING, mpose, t)
    corridor_dust(c, dust)
    c.restore(); vignette(c, 0.9)
    if fall_t + 0.4 < t < fall_t + 0.6:
        c.drawRect(skia.Rect.MakeWH(W, H), P(skia.Color(255, 255, 255, int(90 * (1 - abs(t - fall_t - 0.5) / 0.1)))))

def corridor_dust(c, dust):
    if dust <= 0: return
    px = 1440
    for i in range(16):
        a = i / 15 * math.pi; r_ = 40 + dust * 280
        circle(c, px + math.cos(a) * r_ * 1.3, 885 - math.sin(a) * r_ * 0.3, 28 + dust * 46, P(skia.Color(225, 218, 205, int(170 * (1 - dust))), blur=18))

def scene_lesson(c, t):
    k = prog(t, S("L13"), S("L14") - 0.2)
    c.save(); camera(c, 1.45 + 0.08 * k, 1230, 600)
    corridor_bg(c, t, panel_fall=1.0, panel_swing=0)
    corridor_fg(c, t)
    draw_person(c, 1080, 960, 0.95, WORKER, dict(face=0.5, brow="neutral", mouth="smile", arms=(20, 20, 70, 30), arms_fixed=True, tilt=6, lean=6), t)
    draw_person(c, 1330, 960, 1.05, MING, dict(face=-0.4, backpack=True, lanyard=True, eyes="open", brow="worried", mouth="flat",
                look=(-0.8, -0.3), tilt=-3 + 4 * math.sin(t * 2) * (k > 0.5)), t)
    c.restore(); vignette(c, 1.0)

def scene_lost(c, t):
    k = lp(t, "L14"); turned = k > 0.48
    c.save()
    rot = 0.0 if not turned else 2.0 * math.sin((t - S("L14")) * 2)
    camera(c, 1.1 + 0.25 * ease(prog(k, 0.48, 1.0)), 960, 600, rot=rot)
    museum_bg(c, t, cool=0.25 + 0.5 * ease(prog(k, 0.48, 1.0)))
    # robot arm exhibit
    rrect(c, 1180, 620, 360, 160, 10, P("#3b4049"))
    a1 = -30 + 25 * math.sin(t * 1.6); a2 = 40 * math.sin(t * 2.3)
    x0, y0 = 1360, 620
    x1 = x0 + math.sin(math.radians(180 + a1)) * -200; y1 = y0 + math.cos(math.radians(180 + a1)) * 200
    x2 = x1 + math.sin(math.radians(120 + a1 + a2)) * 150; y2 = y1 + math.cos(math.radians(120 + a1 + a2)) * 150
    line(c, x0, y0, x1, y1, P("#e8743b", stroke=40)); line(c, x1, y1, x2, y2, P("#e8743b", stroke=30))
    circle(c, x0, y0, 30, P("#2c3340")); circle(c, x1, y1, 24, P("#2c3340")); circle(c, x2, y2, 18, P("#2c3340"))
    # passers-by (strangers), blurred & cool when he turns
    blur = 6 if turned else 0
    lay = skia.Paint(); lay.setImageFilter(skia.ImageFilters.Blur(blur, blur)) if blur else None
    if blur: c.saveLayer(None, lay)
    for i, p in enumerate(CROWD):
        sp = 120 + i * 30; dirn = 1 if i % 2 == 0 else -1
        x = ((i * 430 + dirn * (t - S("L14")) * sp) % 2400) - 240
        draw_person(c, x, 900 + (i % 2) * 70, 0.85, p, dict(face=0.7 * dirn, walk=t * 6 + i, eyes="open", mouth="flat"), t)
    if blur: c.restore()
    if not turned:
        draw_person(c, 900, 960, 1.15, MING, dict(face=0.8, backpack=True, lanyard=True, look=(0.8, -0.5), eyes="open", mouth="grin", brow="raised"), t)
    else:
        kk = prog(k, 0.48, 0.6)
        draw_person(c, 900, 960, 1.15, MING, dict(face=0.8 - 0.8 * ease(kk), backpack=True, lanyard=True, look=(math.sin(t * 5) * 0.9, 0), eyes="wide",
                    mouth="o", brow="worried", sweat=prog(k, 0.7, 0.9)), t)
    c.restore(); vignette(c, 1.0 + 0.6 * turned)

# ------------------------------------------------------------------ information desk
def desk_bg(c, t, cool=0.0):
    museum_bg(c, t, cool=cool)
    rrect(c, 1080, 230, 560, 110, 12, P("#1f3d73"))
    circle(c, 1150, 285, 36, P("#ffffff")); text(c, "i", 1150, 302, font("en_xb", 50), P("#1f3d73"), "center")
    text(c, "INFORMATION", 1410, 307, font("en_xb", 56), P("#ffffff"), "center")

def info_desk(c, x=1060, y=700, w=640):
    rrect(c, x, y, w, 40, 8, P("#e9e4da")); rect(c, x + 10, y + 40, w - 20, 300, lin(0, y, 0, y + 300, ["#3f5f8f", "#2e4a72"]))
    rect(c, x + 10, y + 90, w - 20, 10, P("#e8743b"))

def scene_desk(c, t):
    s15, s16, s17, s18, s19, s20, s21 = [S("L%d" % i) for i in range(15, 22)]
    if t < s16:
        # wide: Ming walks to the desk
        k = prog(t, s15, s15 + 2.4)
        c.save(); camera(c, 1.0, 960, 540)
        desk_bg(c, t, cool=0.4)
        draw_person(c, 1380, 1060, 0.95, STAFF, dict(face=-0.4, legs_hidden=True, mouth="smile", arms=(15, 20, -15, -20)), t)
        info_desk(c)
        mx = lerp(300, 900, ease(k))
        draw_person(c, mx, 960, 1.05, MING, dict(face=0.7, walk=t * 7 if k < 1 else None, backpack=True, lanyard=True, brow="worried", mouth="flat",
                    look=(0.8, -0.3)), t)
        c.restore(); vignette(c, 1.1)
    elif t < s17:
        # staff speaks to him (two-shot)
        c.save(); camera(c, 1.45, 1100, 560)
        desk_bg(c, t, cool=0.3)
        draw_person(c, 1380, 1060, 0.95, STAFF, dict(face=-0.5, legs_hidden=True, mouth="smile", talk=env("L16", t), arms=(15, 20, -60, -40), lean=-4), t)
        info_desk(c)
        draw_person(c, 900, 960, 1.05, MING, dict(face=0.6, backpack=True, lanyard=True, brow="worried", mouth="flat", look=(0.8, -0.6)), t)
        c.restore(); vignette(c, 1.1)
    elif t < s18:
        # close-up: panic, clock ticks fast, light closes in
        k = prog(t, s17, s18)
        c.save(); camera(c, 2.4 + 0.25 * k, 880, 560)
        desk_bg(c, t, cool=0.5 + 0.4 * k)
        draw_clock(c, 660, 380, 70, 600 + k * 300)
        draw_person(c, 900, 960, 1.05, MING, dict(face=0.3, backpack=True, lanyard=True, brow="worried", mouth="frown" if k < 0.6 else "small",
                    eyes="down" if 0.3 < k < 0.7 else "open", look=(math.sin(t * 6) * 0.7, 0.2), blush=ease(prog(k, 0.0, 0.3)), sweat=ease(prog(k, 0.5, 0.8)), tilt=-5), t)
        c.restore()
        vignette(c, 1.4 + 0.5 * math.sin(t * 7.5) ** 2)
    elif t < s19:
        # breath -> remembers
        k = prog(t, s18, s19)
        c.save(); camera(c, 2.5 - 0.6 * ease(k), 900, 560)
        desk_bg(c, t, cool=0.8 - 0.6 * ease(k))
        draw_person(c, 900, 960, 1.05, MING, dict(face=0.3, backpack=True, lanyard=True, eyes="closed" if k < 0.45 else "open",
                    brow="neutral" if k < 0.45 else "determined", mouth="flat", blush=0.4 * (1 - k), tilt=0), t)
        c.restore()
        c.drawCircle(900, 380, 500, P(skia.Color(255, 220, 150, int(60 * ease(k))), blur=120))
        vignette(c, 1.2 - 0.4 * k)
    elif t < s20:
        # Ming says the sentence
        c.save(); camera(c, 1.6, 1080, 560)
        desk_bg(c, t, cool=0.1)
        draw_person(c, 1380, 1060, 0.95, STAFF, dict(face=-0.5, legs_hidden=True, mouth="smile", eyes="open", brow="raised", arms=(15, 20, -15, -20), lean=-6), t)
        info_desk(c)
        draw_person(c, 920, 960, 1.05, MING, dict(face=0.6, backpack=True, lanyard=True, brow="determined", mouth="flat", talk=env("L19", t),
                    look=(0.8, -0.6), arms=(10, 10, -40, -50)), t)
        c.restore(); vignette(c, 0.9)
    else:
        # staff helps: calls the teacher, Ming stays at the desk
        k = prog(t, s20, s21)
        c.save(); camera(c, 1.3, 1080, 540)
        desk_bg(c, t, cool=0.0)
        phone = k > 0.55
        hands = draw_person(c, 1380, 1060, 0.95, STAFF, dict(face=-0.4, legs_hidden=True, mouth="smile", talk=env("L20", t), eyes="open",
                    arms=(15, 20, -150, -100) if phone else (15, 20, -70, -60), arms_fixed=True), t)
        if phone:
            hx, hy = hands["hand_far"]; hx += 1380; hy += 1060
            rrect(c, hx - 12, hy - 40, 24, 50, 5, P("#2c3340"))
        info_desk(c)
        draw_person(c, 920, 960, 1.05, MING, dict(face=0.6, backpack=True, lanyard=True, brow="neutral", mouth="smile", look=(0.8, -0.6)), t)
        c.restore(); vignette(c, 0.8)

def scene_reunite(c, t):
    k = prog(t, S("L21") - 0.8, S("L21") + 1.6)
    c.save(); camera(c, 1.2, 960, 540)
    desk_bg(c, t)
    draw_person(c, 1380, 1060, 0.95, STAFF, dict(face=-0.4, legs_hidden=True, mouth="smile", arms=(15, 20, -150, 20), arms_fixed=True), t)
    info_desk(c)
    tx = lerp(-150, 640, ease_out(k))
    draw_person(c, tx, 960, 0.92, TEACHER, dict(face=0.6, walk=t * 7 if k < 1 else None, mouth="smile", brow="worried" if k < 1 else "neutral",
                arms=(15, 20, -15, -20) if k < 1 else (15, 20, 75, 20), arms_fixed=k >= 1), t)
    draw_person(c, 900, 960, 1.05, MING, dict(face=-0.6 * ease(prog(k, 0.3, 0.6)), backpack=True, lanyard=True, eyes="happy" if k > 0.8 else "open",
                mouth="grin" if k > 0.8 else "smile", brow="raised"), t)
    c.restore(); vignette(c, 0.8)
    if t > S("L22") - 0.6: letterbox_fade(c, (t - (S("L22") - 0.6)) / 0.6)

# ------------------------------------------------------------------ home: realization, practice
def scene_home(c, t):
    s22, s23 = S("L22"), S("L23")
    fall = prog(t, s23 + 0.3, s23 + 2.6) if t > s23 + 0.3 else 0.0
    n = 20 + 40 * ease(prog(t, s22, E("L22")))
    zoom = 1.0 + 0.1 * ease(prog(t, s22, E("L22")))
    c.save(); camera(c, zoom, 1000, 520)
    bedroom_bg(c, t, mood=0.4 * (1 - prog(t, s23, E("L23"))), notes=n, notes_fall=fall)
    stand = t > s23
    if not stand:
        draw_person(c, 960, 1000, 1.25, MING, dict(face=0.0, legs_hidden=True, eyes="open", look=(0, -0.8), brow="worried", mouth="flat"), t)
    else:
        k = prog(t, s23, s23 + 1.0)
        arm = 150 + 20 * math.sin(t * 8) if t > s23 + 0.3 else 40
        draw_person(c, 900, 1000 - 60 * ease(k), 1.25, MING, dict(face=0.4, legs_hidden=True, eyes="open", look=(0.5, -0.8), brow="determined",
                    mouth="smile", arms=(20, 20, arm, -20), arms_fixed=True), t)
    desk_front(c, mood=0.4 * (1 - prog(t, s23, E("L23"))))
    draw_lamp(c, 1420, 760, 1.0, on=0.6 + 0.4 * prog(t, s23, E("L23")))
    draw_robot(c, 1200, 760, 0.6, built=1.0, glow=0.3, t=t)
    c.restore(); vignette(c, 1.0)
    if t < s22: letterbox_fade(c, 1 - (t - (s22 - 0.6)) / 0.6)

def notebook(c, x, y, w, h, written=1.0):
    rrect(c, x, y, w, h, 10, P("#fbfaf6")); rect(c, x + w / 2 - 2, y, 4, h, P("#d8cfb8"))
    for i in range(4): line(c, x + 20, y + 52 + i * 40, x + w - 20, y + 52 + i * 40, P("#c9d8ea", stroke=2))
    items = [("I don't understand.", x + 22, y + 46, "en_b"), ("Can you help me?", x + 22, y + 86, "en_b"),
             ("我不明白，", x + w / 2 + 22, y + 46, "zh"), ("你能帮帮我吗？", x + w / 2 + 22, y + 86, "zh")]
    for i, (s_, tx, ty, fk) in enumerate(items):
        kk = clamp(written * 4 - i)
        if kk <= 0: continue
        c.save(); c.clipRect(skia.Rect.MakeXYWH(tx - 4, y, (w / 2 - 20) * kk, h))
        text(c, s_, tx, ty, font(fk, 29), P("#2c3e70"))
        c.restore()

def kitchen_timer(c, x, y, secs):
    circle(c, x, y, 60, P("#e8743b")); circle(c, x, y, 46, P("#fbfaf6"))
    m, s_ = int(secs // 60), int(secs % 60)
    text(c, "%d:%02d" % (m, s_), x, y + 11, font("en_b", 30), P("#2c3340"), "center")

def scene_practice(c, t):
    k = lp(t, "L24")
    c.save(); camera(c, 1.2, 960, 560)
    bedroom_bg(c, t, day=1.0)
    beat = 0 if k < 0.38 else (1 if k < 0.7 else 2)   # hear / repeat / say it yourself
    talk = 0.0
    if beat == 1: talk = 0.5 + 0.5 * abs(math.sin(t * 9))
    if beat == 2 and k > 0.78: talk = 0.6 * abs(math.sin(t * 8)) + 0.2
    draw_person(c, 960, 1000, 1.25, MING, dict(face=0.0 if beat < 2 else 0.2, legs_hidden=True, earbuds=beat < 2, eyes="down" if beat == 0 else "open",
                look=(0, 0.6) if beat < 2 else (0.3, -0.3), brow="neutral" if beat < 2 else "determined", mouth="smile", talk=talk,
                arms=(30, 60, -30, -60)), t)
    if beat < 2:
        line(c, 960 - 76, 470, 960 - 64, 560, P("#ffffff", stroke=3))
    if beat == 0:
        for i in range(3):
            r_ = 30 + ((t * 60 + i * 25) % 75)
            c.drawArc(skia.Rect.MakeXYWH(960 - 90 - r_, 450 - r_, 2 * r_, 2 * r_), 150, 60, False, P(skia.Color(255, 255, 255, int(200 * (1 - (r_ - 30) / 75))), stroke=5))
    if beat == 1:
        for i in range(3):
            on = (k - 0.38) / 0.32 * 3 > i
            circle(c, 1200 + i * 40, 420, 12, P("#62c26a" if on else "#ffffff", a=230))
    desk_front(c)
    notebook(c, 660, 600, 600, 160, written=clamp(k * 1.6))
    kitchen_timer(c, 1380, 690, 600 - k * 40)
    c.restore(); vignette(c, 0.6)

def scene_ask(c, t):
    k = lp(t, "L25")
    c.save(); camera(c, 1.0, 960, 540)
    rect(c, 0, 0, W, H, lin(0, 0, 0, H, ["#e9e2d0", "#d8cfb8"]))
    # whiteboard
    rrect(c, 820, 140, 760, 380, 10, P("#8a8f99")); rect(c, 835, 155, 730, 350, P("#fbfbf8"))
    for i, s_ in enumerate(["Today:", "Can you say that again?", "What does this word mean?"]):
        text(c, s_, 870, 220 + i * 70, font("en_b", 36 if i else 40), P("#2c3e70" if i else "#d64545"))
    rect(c, 0, 760, W, 320, lin(0, 760, 0, H, ["#b59a78", "#8e7558"]))
    draw_person(c, 1720, 960, 0.92, TEACHER, dict(face=-0.6, mouth="smile", eyes="open", arms=(15 + 75 * prog(k, 0.3, 0.6), 0, -15, -20), arms_fixed=True, brow="raised"), t)
    # classmates seated (back rows)
    draw_person(c, 300, 1135, 1.0, KID2, dict(face=0.6, legs_hidden=True, mouth="smile"), t)
    draw_person(c, 1150, 1135, 1.0, KID3, dict(face=0.4, legs_hidden=True, mouth="smile"), t)
    raise_ = ease(prog(k, 0.0, 0.25))
    draw_person(c, 700, 1165, 1.15, MING, dict(face=0.6, legs_hidden=True, mouth="smile" if k < 0.5 else "small", talk=0.5 * abs(math.sin(t * 8)) if k > 0.5 else 0,
                brow="determined", arms=(30, 40, -30 + 195 * raise_, -40 + 30 * raise_), arms_fixed=True), t)
    for x0 in (120, 560, 1000):
        rect(c, x0, 900, 400, 24, P("#a77b55")); rect(c, x0 + 20, 924, 360, 160, P("#8a6345"))
    c.restore(); vignette(c, 0.6)

def scene_end(c, t):
    s = S("L26")
    k = prog(t, s - 0.2, END)
    # morning street, Ming walks to school
    rect(c, 0, 0, W, H, lin(0, 0, 0, H, ["#ffd9a8", "#fbe9d0"]))
    circle(c, 1500, 700, 200, P("#fff2cf"))
    c.drawCircle(1500, 700, 380, P(skia.Color(255, 230, 170, 120), blur=80))
    rnd = random.Random(4); bx = -40
    while bx < W:
        bw_ = rnd.uniform(120, 220); bh_ = rnd.uniform(160, 340)
        rect(c, bx, 800 - bh_, bw_ - 10, bh_, P("#e7b98e")); bx += bw_
    rect(c, 0, 800, W, 280, lin(0, 800, 0, H, ["#c99a74", "#a77b55"]))
    mx = 300 + (t - s + 0.2) * 110
    draw_person(c, mx, 960, 0.95, MING, dict(face=0.75, walk=t * 6.5, backpack=True, mouth="smile", eyes="open", brow="determined"), t)
    a = clamp((t - s - 0.8) / 0.6)
    if a > 0:
        rrect(c, W / 2 - 560, 120, 1120, 300, 26, P(skia.Color(20, 22, 34, int(170 * a))))
        text(c, "I don't understand. Can you help me?", W / 2, 228, font("en_xb", 62), P(skia.Color(255, 255, 255, int(255 * a))), "center")
        text(c, "我不明白，你能帮帮我吗？", W / 2, 312, font("zh_b", 52), P(skia.Color(255, 226, 140, int(255 * a))), "center")
        text(c, "10 minutes today  ·  今天先学十分钟", W / 2, 384, font("zh", 36), P(skia.Color(255, 255, 255, int(220 * a))), "center")
    vignette(c, 0.5)
    if t > END - 0.8: letterbox_fade(c, (t - (END - 0.8)) / 0.8)

# ------------------------------------------------------------------ dispatcher
SCHEDULE = [
    (0.0, scene_cold), (TITLE_S, scene_title), (S("L1") - 0.2, scene_bedroom), (S("L4") - 0.05, scene_build),
    (S("L5") - 0.2, scene_email), (S("L7") - 0.05, scene_monday), (S("L8") - 0.1, scene_loss), (S("L9") - 0.6, scene_trip),
    (S("L10") - 0.15, scene_danger), (S("L13") - 0.3, scene_lesson), (S("L14") - 0.2, scene_lost), (S("L15") - 0.25, scene_desk),
    (S("L21") - 0.8, scene_reunite), (S("L22") - 0.6, scene_home), (S("L24") - 0.3, scene_practice), (S("L25") - 0.2, scene_ask),
    (S("L26") - 0.2, scene_end),
]
def scene_for(t):
    fn = SCHEDULE[0][1]
    for st, f in SCHEDULE:
        if t >= st: fn = f
    return fn

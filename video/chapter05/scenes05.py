"""第五章 · 同路人 —— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。

两条线：蒲公英种子（一起飞一段，又被风吹散）；深夜说心里话时飞出来的小光点（章尾回来陪着她）。
画面里不写字；路人是灰色剪影，同路人是彩色的，分开以后在人群里慢慢变回灰色。
"""
import math
import os
import random
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("series", "chapter01", "chapter02", "chapter03", "chapter04"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
from draw import *  # noqa: F401,F403,E402
from engine import book_intro, book_outro  # noqa: E402
from scenes_v2 import local  # noqa: E402
from scenes02 import phone_at  # noqa: E402
from scenes04 import seed  # noqa: E402

SKIN_L = hexc("e8c09a")
WOOD = hexc("8c5a3c")
WARM = hexc("ffd98a")
# 三个同路人：颜色和发型固定，前后能认出来
MATES = [("4f8a8a", "short", "m1"), ("c98d72", "bang_long", "m2"), ("7d6a8f", "pony", "m3")]


def mate(c, i, x, y, s, **kw):
    col, st, key = MATES[i % 3]
    kw.setdefault("hair", hexc("2f2a28"))
    hair = kw.pop("hair")
    local(c, x, y, s, key + kw.pop("k", ""), hexc(col), hair, st, **kw)


def firefly(c, x, y, r, a, key=""):
    with keep():
        glow(c, x, y, r * 6, WARM, 0.5 * a)
        circle(c, x, y, r, hexc("fff3c0"), a=a)


def footprints_illus(c, cx, cy):
    """章节页小插画：沙地上几行大小不一的脚印，并排走了一段。"""
    with keep():
        for row, (dx, s) in enumerate(((-36, 1.0), (0, 0.8), (36, 1.1))):
            for k in range(4):
                x = cx + dx + (6 if k % 2 else -6)
                y = cy + 60 - k * 34
                shape(c, ell(x, y, 6 * s, 10 * s, 10), hexc("b8a68a"), f"fp{row}{k}", lw=1.2, amp=0.3)


def intro(c, t):
    book_intro(c, t, "第五章", "同路人", footprints_illus)


# ================================================================ 1 几颗种子一起飞
def morning_sky(c, warm=0.0):
    vgrad(c, -200, 2200, [(0, mix(hexc("9fc8ea"), hexc("f2b88a"), warm)), (0.6, mix(hexc("f6e2cc"), hexc("ffd9a8"), warm)),
                          (1, hexc("fbf2e6"))], -400, W + 400)


def seeds_flock(c, t, n_join, cx, cy, scatter=0.0, key="sf"):
    """几颗种子绕着彼此转圈一起飞；scatter → 1 时被风吹散，各自飞走。"""
    entries = [(-200, 500), (1300, 300), (1200, 1500), (-150, 1300)]
    dirs = [(0.2, -1.0), (1.0, -0.4), (0.9, 0.6), (-1.0, -0.2)]
    for i in range(4):
        if i == 0:
            j = 1.0
        else:
            j = ease_io(clamp(n_join - (i - 1)))
            if j <= 0:
                continue
        a = i * math.pi / 2 + t * 0.9
        ox, oy = cx + math.cos(a) * 170, cy + math.sin(a) * 110
        if i > 0:
            ox, oy = lerp(entries[i][0], ox, j), lerp(entries[i][1], oy, j)
        if scatter > 0 and i != 0:
            d = ease_in(scatter) * 1400
            ox += dirs[i][0] * d
            oy += dirs[i][1] * d
        seed(c, ox, oy, 2.2, f"{key}{i}", open_=1.0, glow_a=0.2, rot=math.sin(t * 2 + i) * 0.25)


def f01(c, t):
    morning_sky(c)
    for k in range(3):
        cloud(c, (k * 420 + t * 20) % 1500 - 200, 300 + k * 260, 1.4, f"cl{k}", a=0.7)
    seeds_flock(c, t, n_join=prog(t, 1.0, 3.0) * 3, cx=420 + t * 30, cy=760 - t * 15)


# ================================================================ 2 山路上一个个遇见
def trail_bg(c, t, ox=0.0):
    vgrad(c, 0, 900, [(0, hexc("a8d0ec")), (1, hexc("eef4ee"))])
    for i, (base, amp, col) in enumerate(((700, 70, "a8bcc8"), (820, 60, "9ab88f"), (930, 50, "86a878"))):
        shape(c, hill_pts(base, amp, 0.005 + i * 0.002, i * 1.7 + ox * 0.001 * (i + 1)), hexc(col), f"th{i}", lw=2.4)
    shape(c, rect(-20, 1000, W + 40, 900), hexc("a8c48b"), "tg", lw=3)
    shape(c, [(-20, 1180), (W + 20, 1120), (W + 20, 1250), (-20, 1300)], hexc("e2d2b2"), "tpath", lw=2.4)  # 小路
    shape(c, [(700, 1135), (1000, 1000), (1060, 1000), (820, 1132)], hexc("e2d2b2"), "tfork", lw=2)          # 岔路
    for k in range(5):
        tree(c, 80 + k * 240 + (k % 2) * 40, 1000 + (k % 2) * 10, 1.1, f"tt{k}", col=hexc("6f9a5a"))


def walker_shadow(c, x, y, s):
    with keep():
        shape(c, ell(x + 30 * s, y + 4, 46 * s, 9 * s, 14), (0.25, 0.3, 0.2, 0.25), f"shd{int(x)}", lw=0, edge=False)


def f02(c, t):
    """她一个人背着包走；身后有人追上来问路，看同一张地图，笑了，一起走；岔路上又并进来两个人。影子从一个变成四个。"""
    trail_bg(c, t)
    gx = lerp(160, 520, ease_io(prog(t, 0.0, 2.2))) + max(0.0, t - 4.2) * 70
    walking = t < 2.2 or t > 4.2
    gy = 1240
    # 追上来的人
    mx = lerp(-150, gx - 150, ease_out(prog(t, 0.6, 1.6))) if t < 4.2 else gx - 150
    mapping = 2.2 < t < 4.2
    people = []
    if t > 0.6:
        people.append((mx, gy, 0, t < 2.2 or t > 4.2))
    for i, t0 in ((1, 4.4), (2, 4.8)):                             # 岔路上走来的两个人
        if t > t0:
            u = ease_out(prog(t, t0, 1.6))
            px = lerp(1060, gx + 140 + (i - 1) * 130, u)
            py = lerp(1010, gy - 10 * (i - 1), u)
            ps = lerp(0.8, 1.45, u)
            people.append((px, py, i, True, ps))
    for p in people:
        walker_shadow(c, p[0], p[1], p[4] if len(p) > 4 else 1.5)
    walker_shadow(c, gx, gy, 1.6)
    for p in people:
        if len(p) > 4:
            mate(c, p[2], p[0], p[1], p[4], pack=True, walk=t * 7 if p[3] else None, look=-0.6, mouth="laugh",
                 arms=[(-24, -78), (40, -170)] if t < p[1] * 0 + 5.6 and t > 4.4 + (p[2] - 1) * 0.4 else None)
    if t > 0.6:
        mate(c, 0, mx, gy, 1.55, pack=True, walk=t * 9 if t < 2.2 or t > 4.2 else None, look=0.6,
             mouth="laugh" if mapping else "o", arms=[(-24, -78), (40, -110)] if mapping else None)
    girl(c, gx, gy, 1.6, hat=True, pack=True, look=-0.6 if mapping else 0.8, mouth="laugh" if mapping else "smile",
         walk=t * 7 if walking else None, arms=[(-40, -110), (24, -78)] if mapping else None, key="g2")
    if mapping:                                                    # 两个人一起看的地图
        with keep():
            mx2 = (gx + mx) / 2
            shape(c, [(mx2 - 70, gy - 190), (mx2 + 70, gy - 196), (mx2 + 74, gy - 110), (mx2 - 66, gy - 104)],
                  hexc("f4e7c8"), "map", lw=2)
            line(c, [(mx2 - 50, gy - 170), (mx2 - 10, gy - 140), (mx2 + 40, gy - 160)], "mapl", 2, hexc("c9473b"))


# ================================================================ 3 从天上看：小路汇进大路
MAIN = [(540, 2100), (500, 1700), (620, 1400), (480, 1100), (560, 800), (520, 500), (600, 200), (560, -200)]
SIDES = [([(-100, 1550), (200, 1520), (490, 1600)], 0.28), ([(1180, 1300), (900, 1250), (580, 1330)], 0.42),
         ([(-120, 950), (220, 980), (510, 1010)], 0.58), ([(1200, 700), (880, 760), (550, 760)], 0.72)]


def along(pts, u):
    seg = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    L = sum(seg)
    d = clamp(u) * L
    for i, s in enumerate(seg):
        if d <= s:
            f = d / s if s else 0
            return lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f)
        d -= s
    return pts[-1]


def top_field(c):
    fill_all(c, hexc("b8d49a"))
    r = random.Random(3)
    with keep():
        for k in range(60):
            x, y = r.uniform(-100, 1180), r.uniform(-100, 2100)
            shape(c, ell(x, y, r.uniform(30, 60), r.uniform(20, 40), 14), hexc(r.choice(["9cc27a", "a8cc88", "8fb870"])),
                  f"tf{k}", lw=0, edge=False)


def dot_person(c, x, y, col, key, hat=False):
    with keep():
        shape(c, ell(x + 4, y + 6, 26, 12, 10), (0, 0, 0, 0.2), key + "sh", lw=0, edge=False)
        shape(c, ell(x, y, 24, 24, 12), col, key, lw=2)
        if hat:
            shape(c, ell(x, y, 34, 34, 14), hexc("ecc879"), key + "h", lw=2)
            shape(c, ell(x, y, 16, 16, 10), hexc("bf4a3c"), key + "r", lw=1.4)
        else:
            shape(c, ell(x, y, 14, 14, 10), hexc("2f2a28"), key + "hd", lw=1.4)


def f03(c, t):
    """从天上往下看：一条弯弯的大路，两边的小路上各走来一个人，一个个汇进大路，像小溪流进河。"""
    k = lerp(1.5, 1.0, ease_io(prog(t, 0.0, 3.0)))
    with cam(c, 540, 1100, k):
        top_field(c)
        line(c, MAIN, "main", 70, hexc("e8d8b4"))
        for i, (pts, _) in enumerate(SIDES):
            line(c, pts, f"side{i}", 34, hexc("e8d8b4"))
        u_me = 0.05 + t / 8.0 * 0.85
        mx, my = along(MAIN, u_me)
        dot_person(c, mx, my, hexc("e2a93f"), "me", hat=True)
        cols = [hexc(MATES[i % 3][0]) for i in range(4)]
        for i, (pts, junction) in enumerate(SIDES):
            arrive = junction / 0.85 * 8.0 - 0.6                    # 她走到这个路口的时间
            if t < arrive:
                u = clamp(t / max(arrive, 0.1))
                x, y = along(pts, u)
            else:
                u2 = u_me - 0.03 * (i + 1)
                x, y = along(MAIN, u2)
                x += (14 if i % 2 else -14)
            dot_person(c, x, y, cols[i], f"p{i}")


# ================================================================ 4 一起骑车、喝酒、桌游、爬高原、追落日
def bike(c, x, y, s, key, t, rider=None, look=0.8, wave=False):
    """自行车（侧面），骑车的人坐在上面。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with keep():
        for k, wx in enumerate((-48, 48)):
            shape(c, ell(wx, 0, 32, 32, 18), None, f"{key}w{k}", lw=3)
            a = t * 9
            line(c, [(wx + math.cos(a) * 30, math.sin(a) * 30), (wx - math.cos(a) * 30, -math.sin(a) * 30)], f"{key}sp{k}",
                 1.2, hexc("6a6560"))
        line(c, [(-48, 0), (-10, -40), (30, -40), (48, 0)], f"{key}fr", 3.4, hexc("3a6a8a"))
        line(c, [(-10, -40), (0, 0), (30, -40)], f"{key}fr2", 3.4, hexc("3a6a8a"))
        line(c, [(30, -40), (36, -60), (52, -62)], f"{key}hb", 3, hexc("3a3a3a"))
    c.restore()
    arms = [(30, -96), (40, -92)] if not wave else [(30, -96), (-20, -180)]
    if rider == "me":
        girl(c, x - 6 * s, y - 34 * s, s * 0.95, sit=True, legs=False, hat=True, look=look, mouth="laugh", arms=arms, key=key + "r")
    elif rider is not None:
        mate(c, rider, x - 6 * s, y - 34 * s, s * 0.95, sit=True, legs=False, look=look, mouth="laugh", arms=arms,
             k=key)


def road_scene(c, t, riders=True):
    vgrad(c, 0, 820, [(0, hexc("8fd0ec")), (1, hexc("f0f6f4"))])
    shape(c, rect(-20, 700, W + 40, 300), hexc("3f9fc8"), "rsea", lw=2)
    for k in range(4):
        y = 730 + k * 50
        line(c, [(-20, y), (W + 20, y + 4)], f"rsw{k}", 2, (1, 1, 1), alpha=0.4)
    shape(c, rect(-20, 960, W + 40, 300), hexc("8c8a86"), "road", lw=3)
    off = (t * 600) % 200 if riders else 0
    with keep():
        for k in range(8):
            x = k * 200 - off
            line(c, [(x, 1110), (x + 100, 1110)], f"rl{k}", 6, (1, 1, 1))
    shape(c, rect(-20, 1260, W + 40, 700), hexc("d9c8a8"), "rside", lw=3)
    if riders:
        with keep():
            for k in range(6):                                     # 风
                yy = 300 + k * 90
                xx = (-t * 900 + k * 230) % 1400 - 200
                line(c, [(xx, yy), (xx + 160, yy)], f"wd{k}", 2, (1, 1, 1), alpha=0.6)
        for i, (x, who) in enumerate(((820, 0), (600, 1), (380, 2), (170, "me"))):
            bob = math.sin(t * 9 + i) * 3
            bike(c, x, 1180 + bob, 1.25, f"bk{i}", t, rider=who, look=-0.8 if i == 0 else 0.8, wave=(i == 0 and t > 1.0))
    else:                                                          # 空镜：车辙被风吹淡
        a = 1 - ease_io(prog(t, 0.0, 2.6))
        with keep():
            for k in range(3):
                line(c, [(-20, 1150 + k * 22), (W + 20, 1140 + k * 22)], f"trk{k}", 2, hexc("5a5854"), alpha=0.5 * a)
            for k in range(4):
                yy = 400 + k * 110
                xx = (t * 300 + k * 260) % 1400 - 200
                line(c, [(xx, yy), (xx + 120, yy)], f"wde{k}", 2, (1, 1, 1), alpha=0.5)


GLASSES = [("mug", (-1, -0.2), "f6e08a"), ("wine", (1, -0.2), "c9506a"), ("tall", (-0.2, -1), "f2c070"),
           ("short", (0.2, 1), "e8a050")]


def glass_shape(c, kind, x, y, col, key, empty=False):
    with keep():
        if kind == "mug":
            shape(c, rrect(x - 40, y - 110, 80, 110, 8), (1, 1, 1, 0.6), key, lw=2.4)
            if not empty:
                shape(c, rect(x - 36, y - 90, 72, 86), hexc(col), key + "l", lw=0, edge=False)
                shape(c, ell(x, y - 96, 40, 14, 12), (1, 1, 1), key + "f", lw=1.6)
            shape(c, ell(x + 52, y - 56, 18, 28, 12), None, key + "hd", lw=3)
        elif kind == "wine":
            shape(c, ell(x, y - 120, 38, 44, 16, 0, math.pi), (1, 1, 1, 0.5), key, lw=2.4)
            if not empty:
                shape(c, ell(x, y - 112, 32, 30, 14, 0, math.pi), hexc(col), key + "l", lw=0, edge=False)
            line(c, [(x, y - 76), (x, y - 10)], key + "st", 3)
            shape(c, ell(x, y - 6, 28, 7, 10), (1, 1, 1, 0.5), key + "b", lw=2)
        elif kind == "tall":
            shape(c, [(x - 30, y - 160), (x + 30, y - 160), (x + 24, y), (x - 24, y)], (1, 1, 1, 0.5), key, lw=2.4)
            if not empty:
                shape(c, [(x - 27, y - 130), (x + 27, y - 130), (x + 23, y - 4), (x - 23, y - 4)], hexc(col), key + "l",
                      lw=0, edge=False)
        else:
            shape(c, rect(x - 40, y - 80, 80, 80), (1, 1, 1, 0.5), key, lw=2.4)
            if not empty:
                shape(c, rect(x - 36, y - 56, 72, 52), hexc(col), key + "l", lw=0, edge=False)
                shape(c, rrect(x - 14, y - 50, 28, 26, 6), (0.9, 0.95, 1, 0.8), key + "ice", lw=1)


def bar_bg(c, t):
    fill_all(c, hexc("3a2a2a"))
    line(c, [(-20, 260), (W + 20, 320)], "barl", 2, hexc("6a5a50"))
    with keep():
        for k in range(10):
            x = k * 120 + 20
            y = 270 + k * 5 + math.sin(t * 1.5 + k) * 4
            glow(c, x, y + 14, 80, WARM, 0.45)
            circle(c, x, y + 14, 8, hexc("fff0b8"))
    shape(c, rect(-20, 700, W + 40, 300), hexc("4a3530"), "barwall", lw=2)
    for k in range(6):
        shape(c, rect(60 + k * 170, 560, 30, 130), hexc(["5a8a6a", "8a5a4a", "c9a04a", "4a5a8a", "8a4a6a", "6a8a4a"][k]),
              f"bot{k}", lw=1.6)
    shape(c, ell(540, 1180, 420, 120, 30), hexc("8c5a3c"), "bartab", lw=3)


def bar_scene(c, t, empty=False):
    bar_bg(c, t)
    if empty:
        with keep():
            for k, (kind, d, col) in enumerate(GLASSES):
                x, y = 540 + d[0] * 170, 1180 + d[1] * 70 + 40
                shape(c, ell(x, y + 8, 44, 12, 14), None, f"ring{k}", lw=2, alpha=0.5)
                shape(c, ell(x + 30, y + 30, 40, 10, 14), None, f"ring2{k}", lw=1.6, alpha=0.35)
                glass_shape(c, kind, x, y, col, f"eg{k}", empty=True)
        return
    meet = ease_in(prog(t, 0.0, 1.0))
    bounce = math.sin(prog(t, 1.0, 0.4) * math.pi) * 20
    for k, (kind, d, col) in enumerate(GLASSES):
        dist = lerp(520, 60, meet) + bounce
        x = 540 + d[0] * dist
        y = 1120 + d[1] * dist * 0.4
        glass_shape(c, kind, x, y, col, f"g{k}")
    if t > 1.0:                                                    # 泡沫溅出来
        u = prog(t, 1.0, 1.2)
        r = random.Random(4)
        with keep():
            for k in range(18):
                a = r.uniform(math.pi * 1.1, math.pi * 1.9)
                d = u * r.uniform(80, 220)
                circle(c, 540 + math.cos(a) * d, 960 + math.sin(a) * d + u * u * 160, r.uniform(5, 10), (1, 1, 1),
                       a=1 - u)


def game_table(c, t, empty=False, laugh=0.0):
    """从正上方往下看的桌子。"""
    fill_all(c, hexc("6a4a3a"))
    shape(c, rrect(250, 560, 580, 720, 30), hexc("2f6a5a"), "felt", lw=3)
    r = random.Random(6)
    with keep():
        if empty:
            for k in range(8):
                shape(c, rrect(460 + k * 2, 820 - k * 3, 120, 170, 10), hexc("fbfaf6"), f"stk{k}", lw=1.6)
            die(c, 680, 980, 0.0, 6, "d0")
        else:
            for k in range(12):
                x, y = r.uniform(330, 750), r.uniform(650, 1180)
                c.save()
                c.translate(x, y)
                c.rotate(r.uniform(-0.8, 0.8))
                shape(c, rrect(-50, -70, 100, 140, 10), hexc("fbfaf6"), f"cd{k}", lw=1.6)
                shape(c, ell(0, 0, 16, 16, 12), hexc(["c9473b", "3a3a3a"][k % 2]), f"cds{k}", lw=1)
                c.restore()
            for k in range(2):
                roll = max(0.0, 1.2 - t)
                die(c, 520 + k * 120 + roll * 60, 900 + roll * 40 * (1 if k else -1), roll * 9 + k, 1 + int(t * 7 + k * 3) % 6
                    if roll > 0 else (3 + k * 2), f"d{k}")
    if not empty:                                                  # 一圈脑袋（从上面看）
        heads = [(540, 500), (890, 720), (890, 1100), (540, 1340), (190, 1100), (190, 720)]
        for k, (x, y) in enumerate(heads):
            lean = 24 * math.sin(t * 2 + k) + laugh * 30 * math.sin(t * 14 + k)
            cx, cy = x, y
            dx, dy = (540 - cx) / max(1, math.hypot(540 - cx, 900 - cy)), (900 - cy) / max(1, math.hypot(540 - cx, 900 - cy))
            hx, hy = cx + dx * lean, cy + dy * lean
            with keep():
                col = hexc(["e2a93f", "4f8a8a", "c98d72", "7d6a8f", "6b7a8a", "8fb39a"][k])
                shape(c, ell(hx - dx * 40, hy - dy * 40, 70, 60, 16), col, f"sh{k}", lw=2)
                if k == 0:                                         # 她：草帽
                    shape(c, ell(hx, hy, 72, 72, 20), hexc("ecc879"), "hat", lw=2.4)
                    shape(c, ell(hx, hy, 40, 40, 16), hexc("bf4a3c"), "hatr", lw=1.6)
                    shape(c, ell(hx, hy, 32, 32, 14), hexc("ecc879"), "hatt", lw=1.6)
                else:
                    shape(c, ell(hx, hy, 46, 46, 16), hexc("2f2a28"), f"hd{k}", lw=2)


def die(c, x, y, rot, n, key):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    with keep():
        shape(c, rrect(-34, -34, 68, 68, 12), (1, 1, 1), key, lw=2.4)
        pips = {1: [(0, 0)], 2: [(-14, -14), (14, 14)], 3: [(-14, -14), (0, 0), (14, 14)],
                4: [(-14, -14), (14, -14), (-14, 14), (14, 14)], 5: [(-14, -14), (14, -14), (0, 0), (-14, 14), (14, 14)],
                6: [(-14, -16), (14, -16), (-14, 0), (14, 0), (-14, 16), (14, 16)]}
        for px, py in pips[n]:
            circle(c, px, py, 5, INK)
    c.restore()


def plateau(c, t, empty=False):
    vgrad(c, 0, 1000, [(0, hexc("2f5fa8")), (1, hexc("a8c8e8"))])
    for k in range(3):
        mountain(c, 200 + k * 360, 760, 520, 360, hexc("c8d4e4"), f"pm{k}")
    shape(c, [(-20, 1500), (-20, 900), (300, 1000), (700, 760), (1100, 600), (1100, 1500)], hexc("9a8a78"), "slope", lw=3)
    r = random.Random(8)
    with keep():
        for k in range(26):
            x = r.uniform(0, 1080)
            y = 1500 - (1500 - (900 - x * 0.28)) * r.uniform(0.05, 0.95)
            shape(c, ell(x, y, r.uniform(8, 20), r.uniform(5, 12), 10), hexc("7a6a5a"), f"rk{k}", lw=1, amp=0.4)
    if empty:
        a = 1 - ease_io(prog(t, 0.0, 2.6))
        with keep():
            for k in range(6):
                x = 300 + k * 90
                y = 1000 - (x - 300) * 0.5 + 40
                shape(c, ell(x, y, 12, 6, 10), hexc("5a4a3a"), f"fpr{k}", lw=0, edge=False, alpha=0.6 * a)
            for k in range(5):
                yy = 700 + k * 90
                xx = (t * 500 + k * 260) % 1400 - 200
                line(c, [(xx, yy), (xx + 140, yy - 10)], f"pwd{k}", 2, (1, 1, 1), alpha=0.5)
        return
    pull = ease_io(prog(t, 0.8, 1.2))
    mate(c, 0, 760, 760 + 40, 1.3, pack=True, look=-0.8, mouth="laugh", arms=[(-60, -110), (24, -78)])
    gx, gy = lerp(470, 600, pull), lerp(1010, 900, pull)
    girl(c, gx, gy, 1.3, hat=True, pack=True, look=0.8, mouth="laugh" if pull > 0.6 else "o",
         arms=[(-24, -78), (60, -140)] if pull < 0.9 else None, key="g4p")
    mate(c, 1, 300, 1080, 1.35, pack=True, look=0.7, mouth="laugh", walk=t * 4)
    with keep():                                                   # 喘着的白气
        for k, (x, y) in enumerate(((gx + 30, gy - 260), (760 - 20, 800 - 260), (330, 1080 - 270))):
            ph = (t * 0.8 + k * 0.3) % 1
            shape(c, ell(x + ph * 30, y - ph * 30, 14 + ph * 20, 10 + ph * 12, 10), (1, 1, 1), f"br{k}", lw=0.8,
                  alpha=0.7 * (1 - ph))


def sunset_beach(c, t, sun_y=760, dusk=0.0, runners=True, sun_r=200):
    sky_a = mix(hexc("f08a5a"), hexc("1f2a4a"), dusk)
    sky_b = mix(hexc("ffd08a"), hexc("6a4a6a"), dusk)
    vgrad(c, -200, 900, [(0, sky_a), (1, sky_b)], -400, W + 400)
    if dusk > 0.5:
        r = random.Random(3)
        with keep():
            for k in range(40):
                star(c, r.uniform(0, W), r.uniform(0, 600), r.uniform(1.5, 3), (dusk - 0.5) * 2)
    c.save()
    c.rectangle(-400, -400, W + 800, 900 + 400)
    c.clip()
    with keep():
        glow(c, 540, sun_y, sun_r * 3, hexc("ffb060"), 0.6 * (1 - dusk))
        circle(c, 540, sun_y, sun_r, hexc("ffcf70"))
    c.restore()
    vgrad(c, 900, 1200, [(0, mix(hexc("e8805a"), hexc("2a3050"), dusk)), (1, mix(hexc("b8605a"), hexc("1a2038"), dusk))],
          -400, W + 400)
    with keep():
        for k in range(10):
            y = 920 + k * k * 3
            w_ = 60 + k * 30
            line(c, [(540 - w_ / 2, y), (540 + w_ / 2, y)], f"sb{k}", 3, hexc("ffe0a0"), alpha=(0.7 - k * 0.06) * (1 - dusk))
    vgrad(c, 1180, 2000, [(0, mix(hexc("8a5a4a"), hexc("2a2a3a"), dusk)), (1, mix(hexc("5a3a3a"), hexc("1a1a28"), dusk))],
          -400, W + 400)
    if runners:
        for k in range(4):
            x = (900 - t * 260 + k * 180) % 1300 - 100
            phase = t * 11 + k
            c.save()
            c.push_group()
            if k == 3:
                girl(c, x, 1260 + k * 4, 1.5, hat=True, walk=phase, run=True, look=-0.9, key=f"rn{k}")
            else:
                mate(c, k, x, 1260 + k * 4, 1.5 - 0.05 * k, walk=phase, run=True, look=-0.9)
            c.pop_group_to_source()
            c.paint_with_alpha(1.0)
            c.restore()
            with keep():                                           # 剪影：盖一层深色
                pass
            with keep():                                           # 金色的水花
                for j in range(4):
                    ph = (t * 2 + j / 4 + k * 0.3) % 1
                    circle(c, x + 20 - ph * 40 + j * 6, 1250 - math.sin(ph * math.pi) * 60, 5, hexc("ffd98a"), a=1 - ph)


def silhouette_layer(c, fn, alpha=0.88, col=(0.18, 0.12, 0.16)):
    """把人物画成逆光的剪影。"""
    c.push_group()
    fn()
    c.pop_group_to_source()
    pat = c.get_source()
    c.save()
    c.set_source_rgba(*col, alpha)
    c.mask(pat)
    c.restore()


def f04(c, t):
    k = min(int(t / 3.0), 4)
    u = t - k * 3.0
    if k == 0:
        road_scene(c, u)
    elif k == 1:
        bar_scene(c, u)
    elif k == 2:
        game_table(c, u)
    elif k == 3:
        plateau(c, u)
    else:
        beach_run(c, u)


def beach_run(c, t):
    sunset_beach(c, t, runners=False)
    for k in range(4):
        x = (900 - t * 240 + k * 200) % 1300 - 100
        phase = t * 11 + k

        def draw(k=k, x=x, phase=phase):
            if k == 3:
                girl(c, x, 1300, 1.5, hat=True, walk=phase, run=True, look=-0.9, key=f"rn{k}")
            else:
                mate(c, k, x, 1300, 1.5 - 0.05 * k, walk=phase, run=True, look=-0.9)
        silhouette_layer(c, draw)
        with keep():                                               # 金色的水花
            for j in range(5):
                ph = (t * 2 + j / 5 + k * 0.3) % 1
                circle(c, x + 30 - ph * 60 + j * 6, 1290 - math.sin(ph * math.pi) * 70, 6, hexc("ffd98a"), a=1 - ph)


# ================================================================ 5 托住落日
def f05(c, t):
    """太阳一点点往海里沉。她跑到最前面，假装要把太阳托住；大家一起伸手去托，笑成一团；太阳还是沉下去了，大家坐到天黑。"""
    sink = ease_io(prog(t, 3.0, 4.5))
    sun_y = lerp(760, 1020, sink)
    dusk = ease_io(prog(t, 5.5, 4.0))
    sunset_beach(c, t, sun_y=sun_y, dusk=dusk, runners=False, sun_r=190)
    sit = t > 7.0
    hold = 0.5 < t < 7.0
    for k in range(4):
        join = ease_out(prog(t, 0.0 if k == 3 else 1.2 + k * 0.3, 0.9))
        if k == 3:
            x = 540
        else:
            x = [300, 780, 160][k]
        x0 = [-100, 1180, -200, 540][k]
        xx = lerp(x0, x, join)

        def draw(k=k, xx=xx):
            laugh = math.sin(t * 10 + k) * 4
            if sit:
                if k == 3:
                    girl(c, xx, 1250, 1.4, sit=True, hat=True, view="back", key="g5s")
                else:
                    mate(c, k, xx, 1250, 1.35, sit=True, view="back", k="s")
            elif k == 3:
                girl(c, xx, 1320, 1.6, hat=True, view="back",
                     arms=[(-40, -230 + laugh), (40, -230 - laugh)] if hold else None, key="g5")
            else:
                mate(c, k, xx, 1320, 1.5, view="back", arms=[(-40, -220 + laugh), (40, -220 - laugh)] if hold and join > 0.9 else None,
                     walk=t * 8 if join < 1 else None, run=join < 1)
        silhouette_layer(c, draw, alpha=0.9 - 0.2 * dusk)


# ================================================================ 6 屋顶夜聊，话变成小光点
def rooftop(c, t, sky=1.0, lamp=1.0, people=True, talk=0.0, cushions=False, sun_phase=None):
    """sky：0 白天 → 1 深夜。"""
    top = mix(hexc("8fc4ea"), hexc("141c36"), sky)
    low = mix(hexc("f4e6d0"), hexc("2c3c66"), sky)
    vgrad(c, -200, 1000, [(0, top), (1, low)], -400, W + 400)
    if sky > 0.6:
        r = random.Random(5)
        with keep():
            for k in range(50):
                star(c, r.uniform(0, W), r.uniform(0, 800), r.uniform(1.5, 3.2), (sky - 0.6) * 2.5 * (0.6 + 0.4 * math.sin(t * 2 + k)))
    if sun_phase is not None:                                      # 太阳、月亮划过天空
        a = sun_phase * math.pi
        bx, by = 540 - math.cos(a) * 600, 900 - math.sin(a) * 600
        with keep():
            if sky < 0.5:
                glow(c, bx, by, 200, hexc("fff0b0"), 0.6)
                circle(c, bx, by, 60, hexc("fff0b0"))
            else:
                circle(c, bx, by, 46, hexc("fdf3d6"))
    # 远处的屋顶和小镇
    r = random.Random(2)
    x = -40
    i = 0
    while x < W + 40:
        w_, h_ = r.uniform(120, 200), r.uniform(80, 200)
        shape(c, rect(x, 1000 - h_, w_, h_ + 40), mix(hexc("c9b8a0"), hexc("2a2840"), sky), f"tw{i}", lw=2)
        with keep():
            if sky > 0.5 and r.random() < 0.7:
                shape(c, rect(x + w_ * 0.4, 1000 - h_ * 0.6, 22, 26), WARM, f"twl{i}", lw=1, alpha=sky)
        x += w_ + 8
        i += 1
    shape(c, rect(-40, 1040, W + 80, 900), mix(hexc("b8a088"), hexc("3a3550"), sky), "roof", lw=3)
    line(c, [(-40, 1040), (W + 40, 1040)], "roofedge", 5, mix(hexc("8c7a62"), hexc("2a2538"), sky))
    # 毯子、垫子
    with keep():
        for k, (bx, col) in enumerate(((260, "c96f6f"), (540, "6f8fb8"), (820, "8fb39a"))):
            shape(c, ell(bx, 1250, 150, 40, 18), mix(hexc(col), hexc("2a2840"), 0.3 * sky), f"blk{k}", lw=2)
            if cushions:
                shape(c, ell(bx, 1240, 70, 16, 14), darker(mix(hexc(col), hexc("2a2840"), 0.3 * sky), 0.8), f"dent{k}",
                      lw=1, edge=False)
    # 小灯
    with keep():
        shape(c, rect(520, 1180, 40, 60 * lamp + 4), hexc("f4ead0"), "candle", lw=1.6)
        if lamp > 0.05:
            glow(c, 540, 1180 - 10, 260 * (0.6 + 0.4 * lamp), WARM, 0.6)
            shape(c, ell(540, 1170 - 4 * math.sin(t * 9), 8, 16, 10), hexc("ffb040"), "flame", lw=1)
        else:                                                      # 烧完了，最后一缕细烟
            for k in range(6):
                ph = (t * 0.4 + k / 6) % 1
                line(c, [(540 + math.sin(ph * 6 + t) * 10, 1170 - ph * 200), (540 + math.sin(ph * 6 + t + 0.5) * 10,
                                                                               1160 - ph * 200)],
                     f"smoke{k}", 2, (0.8, 0.8, 0.85), alpha=0.5 * (1 - ph))
        shape(c, rrect(510, 1236, 60, 14, 4), hexc("8c7a62"), "candleb", lw=1.4)
    if not people:
        return
    sway = math.sin(t * 2.4)
    mate(c, 2, 820, 1250, 1.3, sit=True, legs=False, look=-0.2, eyes_closed=True, mouth="smile", tilt=-0.18, k="r")
    mate(c, 1, 700, 1250, 1.3, sit=True, legs=False, look=-0.4, mouth="laugh", tilt=0.15 + 0.05 * sway,
         arms=[(-24, -70), (30, -90)], k="r")
    girl(c, 300, 1250, 1.35, sit=True, legs=False, hat=False, look=0.6, mouth="smile" if talk > 0 else "laugh", key="g6")
    mate(c, 0, 420, 1250, 1.3, sit=True, legs=False, look=-0.6, mouth="smile" if talk > 0 else "laugh", k="r")


def f06(c, t):
    talk = prog(t, 6.0, 0.5)
    with cam(c, 540, 1100, 1.35):
        f06_inner(c, t, talk)


def f06_inner(c, t, talk):
    rooftop(c, t, sky=1.0, lamp=1.0, talk=talk)
    if talk > 0:                                                   # 话变成小光点
        r = random.Random(11)
        for k in range(int((t - 6.0) * 4)):
            born = 6.0 + k * 0.25
            age = t - born
            x0 = 360 + r.uniform(-20, 20)
            y0 = 1250 - 150 * 1.35
            x = x0 + math.sin(age * 1.5 + k) * 40 + r.uniform(-60, 60) * age * 0.3
            y = y0 - age * 120
            firefly(c, x, y, 4, clamp(age * 2) * clamp(1.5 - (y0 - y) / 900))


# ================================================================ 7 一天、两天、三天
def f07(c, t):
    cyc = t / 2.0                                                  # 每 2 秒一天
    ph = cyc % 1
    sky = 0.5 + 0.5 * math.cos(ph * 2 * math.pi)                  # 夜 → 昼 → 夜
    rooftop(c, t, sky=sky, lamp=1 - 0.85 * clamp(t / 6.0), people=False, sun_phase=(ph * 2) % 1)


# ================================================================ 8 路口拥抱，各自走散
def crossroad(c, t, people=True, prints=False):
    vgrad(c, 0, 900, [(0, hexc("bcd8ee")), (1, hexc("f6eee2"))])
    for i, (base, col) in enumerate(((760, "b8c4cc"), (860, "a8b89a"))):
        shape(c, hill_pts(base, 40, 0.006, i * 2.0), hexc(col), f"ch{i}", lw=2.4)
    shape(c, rect(-20, 900, W + 40, 1000), hexc("a8c48b"), "cg", lw=3)
    for pts in ([(540, 1000), (-200, 1400)], [(540, 1000), (1300, 1400)], [(540, 1000), (540, 760)], [(540, 1000), (540, 1900)]):
        line(c, pts, f"cr{pts[1][0]}", 90 if pts[1][1] > 1000 else 40, hexc("e2d2b2"))
    line(c, [(560, 1000), (560, 850)], "post", 6, WOOD)
    with keep():
        for k, (dy, d) in enumerate(((860, 1), (900, -1), (940, 1))):
            shape(c, [(560, dy), (560 + d * 90, dy), (560 + d * 104, dy + 14), (560 + d * 90, dy + 28), (560, dy + 28)],
                  hexc(["f4e2b0", "f2d0c8", "dfe9f5"][k]), f"arr{k}", lw=1.6)
    if prints:
        with keep():
            for k, (dx, dy) in enumerate(((-1, 0.5), (1, 0.5), (0, -1), (-0.3, 1))):
                for j in range(5):
                    x = 540 + dx * (60 + j * 70)
                    y = 1060 + dy * (30 + j * 50)
                    shape(c, ell(x + (6 if j % 2 else -6), y, 8, 12, 10), hexc("8a7a5a"), f"pr{k}{j}", lw=0, edge=False,
                          alpha=0.55 - j * 0.07)
        with keep():
            for k in range(4):
                yy = 500 + k * 120
                xx = (t * 400 + k * 300) % 1400 - 200
                line(c, [(xx, yy), (xx + 140, yy - 6)], f"cwd{k}", 2, (1, 1, 1), alpha=0.5)
            for k in range(3):                                     # 被风吹过的叶子
                lx = (t * 260 + k * 400) % 1300 - 100
                shape(c, ell(lx, 1100 + k * 60 + math.sin(t * 3 + k) * 20, 10, 5, 8), hexc("c9a04a"), f"leaf{k}", lw=1)
    if not people:
        return
    hug = 0.5 + 0.5 * math.sin(t * 2.0)
    girl(c, 400, 1240, 1.55, hat=True, pack=True, look=0.6, mouth="smile", eyes_closed=t > 1.2,
         arms=[(-24, -78), (60, -120)] if t > 0.8 else None, key="g8")
    mate(c, 0, 400 + 120, 1240, 1.5, pack=True, look=-0.6, mouth="smile", arms=[(-60, -120), (24, -78)] if t > 0.8 else None)
    mate(c, 1, 760, 1240, 1.45, pack=True, look=-0.6, mouth="smile", arms=[(-50, -110), (24, -78)])
    mate(c, 2, 880, 1240, 1.4, pack=True, look=-0.8, mouth="smile", arms=[(-40, -110), (24, -78)])


def f08(c, t):
    if t < 3.4:
        crossroad(c, t)
        return
    lt = t - 3.4                                                   # 从天上看：像花瓣往外散开
    k = lerp(1.6, 1.0, ease_io(prog(lt, 0.0, 1.6)))
    with cam(c, 540, 1000, k):
        top_field(c)
        dirs = [(-1, -0.6), (1, -0.5), (-0.7, 1), (0.8, 1)]
        for i, (dx, dy) in enumerate(dirs):
            line(c, [(540, 1000), (540 + dx * 1400, 1000 + dy * 1400)], f"rd{i}", 40, hexc("e8d8b4"))
        for i, (dx, dy) in enumerate(dirs):
            d = ease_in(prog(lt, 0.4 + i * 0.2, 4.0)) * 900
            col = hexc("e2a93f") if i == 0 else hexc(MATES[(i - 1) % 3][0])
            dot_person(c, 540 + dx * d / math.hypot(dx, dy), 1000 + dy * d / math.hypot(dx, dy), col, f"q{i}", hat=i == 0)


# ================================================================ 9 种子被风吹散
def f09(c, t):
    morning_sky(c, warm=0.3)
    with keep():
        for k in range(6):
            yy = 400 + k * 200
            xx = (t * 900 + k * 260) % 1600 - 300
            line(c, [(xx, yy), (xx + 200, yy - 10), (xx + 320, yy + 6)], f"gust{k}", 2.4, (1, 1, 1), alpha=0.5 * clamp(t * 2))
    seeds_flock(c, t + 6.0, n_join=3, cx=540, cy=900, scatter=prog(t, 0.6, 3.2), key="s9")


# ================================================================ 10 另一间青旅：笑着点点头，继续看书
def f10(c, t):
    fill_all(c, hexc("e8dcc8"))
    shape(c, rect(560, 220, 420, 560), hexc("cfe6f2"), "hwin", lw=4)
    line(c, [(770, 220), (770, 780)], "hwinm", 5, WOOD)
    with keep():                                                   # 窗外的光落在书页上
        c.save()
        g = cairo.LinearGradient(560, 780, 360, 1300)
        g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.45)
        g.add_color_stop_rgba(1, 1, 0.95, 0.8, 0.0)
        c.set_source(g)
        c.move_to(560, 780)
        c.line_to(980, 780)
        c.line_to(760, 1400)
        c.line_to(260, 1400)
        c.close_path()
        c.fill()
        c.restore()
    shape(c, rect(-20, 1240, W + 40, 700), hexc("b89a78"), "hfl", lw=3)
    shape(c, rect(60, 300, 200, 940), hexc("8c6a4a"), "hdoor", lw=3)
    wave = 0.8 < t < 3.0
    mate(c, 1, 170, 1240, 1.5, pack=True, look=0.8, mouth="laugh",
         arms=[(-24, -78), (40, -180 + 15 * math.sin(t * 12))] if wave else None, k="h")
    nod = 6 * max(0.0, math.sin(prog(t, 1.8, 0.9) * math.pi))
    look = -0.7 if 1.4 < t < 3.2 else 0.3
    shape(c, rect(600, 1100, 160, 20), WOOD, "chair", lw=2)
    for x in (610, 740):
        line(c, [(x, 1120), (x, 1240)], f"chl{x}", 4, WOOD)
    girl(c, 680, 1100, 1.5, sit=True, hat=False, look=look, head_down=4 + nod if look < 0 else 8, mouth="smile",
         arms=[(-14, -96), (24, -96)], key="g10")
    with keep():
        shape(c, [(680 - 40, 1100 - 96 * 1.5 + 52 * 1.5 - 30), (680 + 50, 1100 - 96 * 1.5 + 52 * 1.5 - 34),
                  (680 + 46, 1100 - 96 * 1.5 + 52 * 1.5 + 4), (680 - 36, 1100 - 96 * 1.5 + 52 * 1.5 + 8)],
              hexc("fbfaf6"), "book", lw=1.8)
        line(c, [(680 + 5, 1100 - 96 * 1.5 + 52 * 1.5 - 32), (680 + 5, 1100 - 96 * 1.5 + 52 * 1.5 + 6)], "bookm", 1.4)


# ================================================================ 11 公交站：分一副耳机，拥抱，上车
def bus(c, x, y, key, door=0.0, face=None):
    with keep():
        shape(c, rrect(x - 380, y - 360, 760, 330, 30), hexc("3f8fb0"), key, lw=3)
        for k in range(5):
            shape(c, rect(x - 340 + k * 130, y - 320, 100, 110), hexc("dfeef4"), f"{key}w{k}", lw=2)
        shape(c, rect(x - 340, y - 190, 680, 20), hexc("f4f0e6"), key + "st", lw=1.6)
        for wx in (-250, 250):
            shape(c, ell(x + wx, y - 30, 46, 46, 16), hexc("3a3a3a"), f"{key}wh{wx}", lw=2)
        shape(c, rect(x - 360, y - 300, 60 * (1 - door) + 4, 250), hexc("2f6f90"), key + "door", lw=2)


def f11(c, t):
    vgrad(c, 0, 1100, [(0, hexc("141c36")), (1, hexc("34406a"))])
    with keep():
        line(c, [(160, 1250), (160, 700)], "lamp", 8, hexc("3a3a3a"))
        glow(c, 190, 720, 320, WARM, 0.55)
        circle(c, 190, 720, 16, hexc("fff0b8"))
    shape(c, rect(-20, 1250, W + 40, 700), hexc("3a3a48"), "street", lw=3)
    shape(c, rect(-20, 1250, W + 40, 40), hexc("6a6a78"), "curb", lw=2)
    # 车站的棚子
    shape(c, rect(380, 760, 560, 26), hexc("7a8a9a"), "shroof", lw=2.4)
    for x in (400, 920):
        line(c, [(x, 786), (x, 1250)], f"shp{x}", 6, hexc("7a8a9a"))
    shape(c, rect(470, 1110, 380, 20), hexc("8c7a62"), "bench", lw=2)
    arrive = ease_out(prog(t, 3.6, 1.2))
    leave = ease_in(prog(t, 7.4, 2.0))
    hug = 5.6 < t < 6.6
    board = t > 6.8
    if arrive > 0:                                                 # 车停在站台后面
        bx = lerp(1500, 560, arrive) - leave * 1500
        bus(c, bx, 1200, "bus", door=1.0 if 4.8 < t < 7.2 else 0.0)
        if board:                                                  # 车窗里朝彼此挥手
            with keep():
                c.save()
                c.rectangle(bx - 210, 880, 100, 110)
                c.clip()
                girl(c, bx - 160, 1040, 0.9, hat=True, look=0.6, mouth="laugh",
                     arms=[(-24, -78), (40, -170 + 14 * math.sin(t * 10))], key="g11w")
                c.restore()
    nod = math.sin(t * 6) * 3 if t < 3.8 else 0
    if not board:
        if hug:                                                    # 张开手臂抱一下
            girl(c, 600, 1250, 1.5, hat=True, pack=True, look=0.5, mouth="laugh", eyes_closed=True,
                 arms=[(-24, -110), (60, -130)], key="g11")
            mate(c, 0, 690, 1250, 1.5, look=-0.6, mouth="laugh", eyes_closed=True, arms=[(-60, -130), (24, -110)], k="b")
        else:
            girl(c, 580, 1250, 1.5, hat=True, pack=True, look=0.5, head_down=nod, mouth="smile",
                 arms=[(-24, -78), (40, -150)] if 4.6 < t < 5.6 else None, key="g11")
            phone = 4.6 < t < 5.6
            mate(c, 0, 720, 1250, 1.5, look=-0.6, head_down=nod, mouth="smile",
                 arms=[(-40, -150), (24, -78)] if phone else None, k="b")
            if phone:
                phone_at(c, 720 - 40 * 1.5, 1250 - 150 * 1.5 - 20, 1.2, "ph11", glow_a=0.4)
            if t < 4.2:                                            # 一副耳机分着听
                with keep():
                    hx1, hy1 = 580 + 22, 1250 - 165 * 1.5
                    hx2, hy2 = 720 - 22, 1250 - 165 * 1.5
                    line(c, [(hx1, hy1), ((hx1 + hx2) / 2, 1250 - 110 * 1.5), (hx2, hy2)], "ear", 2, (1, 1, 1))
                    circle(c, hx1, hy1, 5, (1, 1, 1))
                    circle(c, hx2, hy2, 5, (1, 1, 1))
                    for k in range(3):                             # 音符一样的小点
                        ph = (t * 0.8 + k / 3) % 1
                        circle(c, 650 + math.sin(ph * 6 + k) * 30, 1250 - 200 * 1.5 - ph * 120, 4, WARM, a=1 - ph)
    else:
        mate(c, 0, 720, 1250, 1.5, look=-0.8, mouth="smile", arms=[(-40, -180 + 14 * math.sin(t * 10)), (24, -78)], k="b")


# ================================================================ 12 吹散一朵蒲公英
def f12(c, t):
    vgrad(c, 0, 1000, [(0, hexc("9fd0ec")), (1, hexc("f4f2e8"))])
    for k in range(3):
        cloud(c, (k * 400 + t * 25) % 1400 - 150, 260 + k * 120, 1.2, f"c12{k}", a=0.8)
    shape(c, hill_pts(1040, 60, 0.004, 1.2), hexc("9ec27a"), "hill12", lw=3)
    with keep():
        for k in range(20):                                        # 草
            x = k * 56
            line(c, [(x, 1240), (x + 6 + math.sin(t * 2 + k) * 6, 1200)], f"gr{k}", 2.4, hexc("6f9a50"))
    blow = t > 1.0
    walk = ease_in(prog(t, 2.6, 2.4))
    gx = 520 + walk * 500
    girl(c, gx, 1240, 1.6, hat=True, pack=True, look=0.6 if not walk else 0.9, mouth="o" if 0.9 < t < 1.6 else "smile",
         arms=[(-24, -78), (40, -150)] if t < 2.4 else None, walk=t * 7 if walk > 0 else None, key="g12")
    hx, hy = 520 + 40 * 1.6, 1240 - 150 * 1.6
    if t < 2.4:
        with keep():
            line(c, [(hx, hy), (hx + 10, hy - 60)], "stalk", 2.4, hexc("6f9a50"))
            if not blow:
                for k in range(26):
                    a = k / 26 * 2 * math.pi
                    line(c, [(hx + 10, hy - 60), (hx + 10 + math.cos(a) * 34, hy - 60 + math.sin(a) * 34)], f"puf{k}", 1,
                         (1, 1, 1))
                    circle(c, hx + 10 + math.cos(a) * 34, hy - 60 + math.sin(a) * 34, 2.4, (1, 1, 1))
    if blow:                                                       # 种子一下子散开，飞得很高、很轻
        r = random.Random(7)
        for k in range(26):
            u = ease_out(prog(t, 1.0 + r.uniform(0, 0.3), 4.0))
            ang = r.uniform(-1.2, 0.3)
            d = u * r.uniform(300, 900)
            x = hx + 10 + math.cos(ang) * d + math.sin(t * 2 + k) * 20 * u
            y = hy - 60 + math.sin(ang) * d - u * 200
            seed(c, x, y, 0.55, f"bl{k}", open_=1.0, glow_a=0.0, rot=math.sin(t * 2 + k) * 0.3)


# ================================================================ 13 小站：一步跨上车，回头看一眼
def f13(c, t):
    vgrad(c, 0, 1000, [(0, hexc("e8885a")), (1, hexc("ffd9a8"))])
    for k in range(5):                                             # 山坡上亮着暖灯的小镇
        house(c, 120 + k * 170, 760 - (k % 2) * 40, 140, 120 + (k % 3) * 20, hexc("e8d0b0"), hexc("a85a3a"), f"tn{k}",
              "tri", lit=2)
    shape(c, rect(-20, 780, W + 40, 300), hexc("a8805a"), "tnh", lw=2.4)
    shape(c, rect(-20, 1060, W + 40, 900), hexc("8c8a86"), "plat", lw=3)
    line(c, [(-20, 1060), (W + 20, 1060)], "pedge", 6, hexc("e8c040"))
    move = ease_in(prog(t, 5.6, 1.6))
    tx = -move * 1400
    # 火车
    with keep():
        shape(c, rrect(tx - 200, 620, 1500, 440, 24), hexc("4f7a6a"), "train", lw=3)
        for k in range(4):
            shape(c, rect(tx - 140 + k * 300, 680, 200, 150), hexc("ffe0a8"), f"tw{k}", lw=2)
    door_x = tx + 480
    closing = ease_io(prog(t, 4.8, 0.6))
    with keep():
        shape(c, rect(door_x, 700, 160, 360), hexc("2a3a34"), "door", lw=2)
    step = ease_io(prog(t, 2.6, 0.6))
    if t < 2.6:
        girl(c, lerp(200, 520, ease_io(prog(t, 0.0, 2.4))), 1240, 1.6, hat=True, pack=True, look=0.8, mouth="smile",
             walk=t * 7 if t < 2.4 else None, key="g13")
    else:
        lookback = 3.2 < t < 4.8
        c.save()
        c.rectangle(door_x, 700, 160, 360)
        c.clip()
        girl(c, door_x + 80 - 20 * (1 - step), lerp(1240, 1050, step), lerp(1.6, 1.2, step), view="front" if lookback else "back",
             hat=True, pack=True, look=-0.9 if lookback else 0.0, mouth="smile",
             arms=[(-50, -120), (24, -78)] if lookback else None, key="g13d")
        c.restore()
    with keep():                                                   # 车门滑上
        shape(c, rect(door_x, 700, 80 * closing, 360), hexc("6f9a8a"), "dl", lw=2)
        shape(c, rect(door_x + 160 - 80 * closing, 700, 80 * closing, 360), hexc("6f9a8a"), "dr", lw=2)


# ================================================================ 14–15 空镜
def f14(c, t):
    crossroad(c, t, people=False, prints=True)


def f15(c, t):
    k = min(int(t / 3.0), 4)
    u = t - k * 3.0
    if k == 0:
        road_scene(c, u, riders=False)
    elif k == 1:
        bar_scene(c, u, empty=True)
    elif k == 2:
        game_table(c, u, empty=True)
    elif k == 3:
        plateau(c, u, empty=True)
    else:
        rooftop(c, u, sky=1.0, lamp=0.0, people=False, cushions=True)


# ================================================================ 16 人群里擦肩，变回灰色
def f16(c, t):
    vgrad(c, 0, 1000, [(0, hexc("c9d1d8")), (1, hexc("e4e5e1"))])
    r = random.Random(4)
    x = -40
    i = 0
    while x < W + 40:
        w_, h_ = r.uniform(140, 220), r.uniform(400, 700)
        shape(c, rect(x, 1000 - h_, w_, h_), hexc(r.choice(["b8bcc4", "a8aeb8", "c4c0b8"])), f"cb{i}", lw=2)
        x += w_ + 6
        i += 1
    shape(c, rect(-20, 1000, W + 40, 900), hexc("c9c6bc"), "sw", lw=3)
    for k in range(10):                                            # 灰色的人群
        sp = 90 + (k % 3) * 30
        xx = (k * 157 + t * sp * (1 if k % 2 else -1)) % 1300 - 100
        silhouette(c, xx, 1120 + (k % 4) * 40, 1.25 + (k % 3) * 0.05, f"crw{k}", walk=t * 6 + k, a=0.75)
    gx = lerp(120, 920, t / 7.0)
    ox = lerp(1000, 80, t / 7.0)
    passed = t > 2.6
    glance = 2.8 < t < 3.8
    fade = ease_io(prog(t, 3.6, 3.0))
    if fade < 1:
        with nokeep():
            with grade(sat=1 - fade):
                with group_alpha(c, 1 - fade):
                    mate(c, 0, ox, 1240, 1.5, pack=True, walk=t * 7, look=0.9 if glance else -0.8, mouth="flat", k="x")
    if fade > 0:
        silhouette(c, ox, 1240, 1.25 * 1.2, "oxs", walk=t * 7, a=0.75 * fade)
    girl(c, gx, 1250, 1.55, hat=True, pack=True, walk=t * 7, look=-0.9 if glance else 0.8, mouth="flat", key="g16")


# ================================================================ 17–22 阁楼，光点回来了
def attic(c, t, dark=0.0, rain=True):
    fill_all(c, mix(hexc("6a5a6a"), hexc("1a1a2a"), dark))
    shape(c, [(-40, 0), (1120, 0), (1120, 260), (-40, 900)], mix(hexc("8a7a7a"), hexc("22223a"), dark), "slope", lw=3)
    with keep():                                                   # 斜屋顶上的天窗
        c.save()
        sk = [(560, 160), (860, 80), (900, 300), (600, 380)]
        spath(c, sk, True)
        c.clip()
        vgrad(c, 60, 400, [(0, hexc("1f2a4a")), (1, hexc("2c3c66"))], 540, 920)
        if rain:
            r = random.Random(5)
            for k in range(30):
                x = r.uniform(560, 900)
                y = (r.uniform(0, 400) + t * 500) % 420 + 60
                line(c, [(x, y), (x - 6, y + 24)], f"rn{k}", 1.6, hexc("9ab8e0"), alpha=0.6)
        c.restore()
        shape(c, sk, None, "skf", lw=4)
    shape(c, rect(-20, 1240, W + 40, 700), mix(hexc("8a6a5a"), hexc("1e1a26"), dark), "afl", lw=3)
    shape(c, rect(200, 1080, 620, 160), mix(hexc("e8e0f0"), hexc("3a3a5a"), dark), "abed", lw=3)
    shape(c, rect(170, 980, 50, 260), mix(WOOD, hexc("2a2030"), dark), "abedh", lw=2.4)
    shape(c, rect(860, 1090, 140, 150), mix(WOOD, hexc("2a2030"), dark), "nstand", lw=2.4)


def table_lamp(c, on):
    with keep():
        line(c, [(930, 1090), (930, 990)], "lpole", 4, hexc("3a3a3a"))
        shape(c, [(880, 990), (980, 990), (960, 930), (900, 930)], hexc("e8c8a0"), "lshade", lw=2)
        if on > 0:
            glow(c, 930, 990, 500, WARM, 0.55 * on)


def sitting_girl(c, t, look_up=0.0, smile=False, arms=None):
    girl(c, 500, 1086, 1.6, sit=True, hat=False, look=0.2, look_up=look_up,
         mouth="smile" if smile else "flat", arms=arms or [(-20, -66), (20, -66)], key="g17")


def f17(c, t):
    attic(c, t, dark=0.35)
    table_lamp(c, 1.0)
    sitting_girl(c, t)


def f18(c, t):
    off = ease_io(prog(t, 1.4, 0.4))
    attic(c, t, dark=0.35 + 0.55 * off)
    table_lamp(c, 1 - off)
    reach = math.sin(clamp(prog(t, 0.4, 1.6)) * math.pi)
    sitting_girl(c, t, arms=[(-20, -66), (lerp(20, 120, reach), lerp(-66, -100, reach))])


FLY = [(random.Random(k).uniform(120, 980), random.Random(k + 50).uniform(120, 760)) for k in range(26)]


def fireflies_in(c, t, n, settle=1.0, out=0.0):
    for k in range(n):
        born = k * 0.28
        u = ease_out(clamp((t - born) / 2.0))
        if u <= 0:
            continue
        tx, ty = FLY[k]
        x = lerp(730, tx, u) + math.sin(t * 1.3 + k) * 10
        y = lerp(120, ty, u) + math.cos(t * 1.1 + k) * 8
        if out > 0:
            o = ease_in(clamp(out * 1.6 - k * 0.03))
            x, y = lerp(x, 730, o), lerp(y, -80, o)
        firefly(c, x, y, 4 + 1.5 * math.sin(t * 3 + k), 0.9)


def f19(c, t):
    attic(c, t, dark=0.9)
    sitting_girl(c, t, look_up=0.5 * ease_io(prog(t, 0.6, 1.0)))
    fireflies_in(c, t, int(clamp(t / 0.28 + 1, 0, 26)))


def memory_bubble(c, fn, u, t, cx=540, cy=500, R=300):
    """一只光点放大成一小团暖光，里面浮着一个画面。"""
    grow = ease_io(clamp(u / 0.5)) * (1 - ease_io(clamp((u - 2.8) / 0.5)))
    if grow <= 0.01:
        return
    r = R * grow
    with keep():
        glow(c, cx, cy, r * 1.5, WARM, 0.5 * grow)
    c.save()
    c.arc(cx, cy, r, 0, 2 * math.pi)
    c.clip()
    c.translate(cx, cy)
    c.scale(r / 540 * 1.0, r / 540 * 1.0)
    c.translate(-540, -960)
    with grade(sat=0.9, warm=0.35):
        fn(c, t)
    c.restore()
    with keep():
        c.save()
        c.arc(cx, cy, r, 0, 2 * math.pi)
        c.set_source_rgba(1, 0.9, 0.7, 0.35 * grow)
        c.set_line_width(10)
        c.stroke()
        c.restore()


def mem_feet(c, t):
    """脚踝边的浪花漫上来，又退下去。"""
    vgrad(c, 0, 1920, [(0, hexc("f2b88a")), (1, hexc("e8c8a0"))])
    w = 0.5 + 0.5 * math.sin(t * 1.6)
    for k, (x, col, skin) in enumerate(((330, "4f8a8a", SKIN_L), (470, "e2a93f", SKIN), (630, "c98d72", SKIN_L),
                                        (760, "7d6a8f", SKIN_L))):
        for sg in (-1, 1):
            lx = x + sg * 26
            shape(c, rect(lx - 18, 560, 36, 120), hexc(col), f"pant{k}{sg}", lw=2)        # 卷起来的裤腿
            shape(c, rect(lx - 14, 680, 28, 320), skin, f"leg{k}{sg}", lw=2)
            shape(c, ell(lx + 14, 1010, 34, 16, 12), skin, f"ft{k}{sg}", lw=2)
    pts = [(-40, 1920)] + [(x, 1050 - w * 120 + 16 * math.sin(x * 0.02 + t * 3)) for x in range(-40, W + 80, 40)] + [(W + 40, 1920)]
    shape(c, pts, hexc("e8f4f8") + (0.8,), "foam", lw=2)
    for k in range(3):
        line(c, [(x, 1050 - w * 120 - 14 - k * 22 + 8 * math.sin(x * 0.03 + t * 2 + k)) for x in range(-40, W + 80, 60)],
             f"fm{k}", 2, (1, 1, 1), alpha=0.7)


def f20(c, t):
    attic(c, t, dark=0.9)
    seg = 3.3
    k = min(int(t / seg), 5)
    u = t - k * seg
    glow_face = 0.4 if k >= 1 else 0.2
    with keep():
        glow(c, 500, 700, 500, WARM, glow_face)
    sitting_girl(c, t, look_up=0.5, smile=k >= 1)
    fireflies_in(c, 30.0, 26)
    fns = [None, lambda cc, tt: road_scene(cc, tt), lambda cc, tt: bar_scene(cc, 0.9 + (tt % 1.2)),
           lambda cc, tt: game_table(cc, 3.0, laugh=1.0), lambda cc, tt: mem_feet(cc, tt), lambda cc, tt: beach_run(cc, tt)]
    if k >= 1:
        memory_bubble(c, fns[k], u, t)


def f21(c, t):
    attic(c, t, dark=0.9)
    with keep():
        glow(c, 500, 700, 500, WARM, 0.3 * (1 - prog(t, 0, 4)))
    sitting_girl(c, t, look_up=0.5 * (1 - prog(t, 2.0, 2.0)), smile=True)
    fireflies_in(c, 30.0, 26, out=prog(t, 0.2, 4.0))


def f22(c, t):
    attic(c, t, dark=0.9)
    land = ease_io(prog(t, 0.2, 2.0))
    close = ease_io(prog(t, 2.8, 0.8))
    hx, hy = 500 + 60 * 1.6, 1090 - 120 * 1.6 + 52 * 1.6
    sitting_girl(c, t, look_up=0.0, smile=True, arms=[(-20, -66), (60, -120)])
    fx, fy = lerp(700, hx, land), lerp(300, hy - 14, land)
    with keep():
        if close < 1:
            firefly(c, fx, fy, 6, 1.0)
        glow(c, hx, hy, 160 + 40 * math.sin(t * 2), WARM, 0.35 + 0.3 * close)
        if close > 0:                                              # 合上手，光从指缝里透出来
            shape(c, ell(hx, hy - 6, 30 * close, 22 * close, 14), SKIN, "fist", lw=2)
            for k in range(3):
                line(c, [(hx - 12 + k * 12, hy - 20), (hx - 12 + k * 12, hy + 4)], f"slit{k}", 3, hexc("fff3c0"),
                     alpha=0.8 * close)


# ================================================================ 片尾
_STILL = {}


def end_still():
    if "s" not in _STILL:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(185.0)
        with grade(sat=1.0, dark=0.0, warm=0.1):
            f22(cc, 5.5)
        _STILL["s"] = surf
    return _STILL["s"]


def outro(c, t):
    book_outro(c, t, end_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第五章 · 完")

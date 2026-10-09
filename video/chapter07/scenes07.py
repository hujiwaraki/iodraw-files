"""第七章 · 那个人 —— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。

ta 只用虚线勾出轮廓，没有脸、没有颜色。贯穿全章的是纸飞机：隔着一片屋顶的两扇窗，纸飞机飞来飞去；
后来再没有纸飞机飞来，远处那扇窗灭了；最后一只纸飞机打开是一张空白的纸，被风吹走。
画面里不写字。
"""
import math
import os
import random
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("series", "chapter01", "chapter02", "chapter03", "chapter04", "chapter05", "chapter06"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
from draw import *  # noqa: F401,F403,E402
from engine import book_intro, book_outro  # noqa: E402
from scenes_v2 import local  # noqa: E402
from scenes05 import bar_scene, mate, plateau  # noqa: E402

GH = hexc("8a909c")                       # ta 的虚线颜色
WARM = hexc("ffd98a")
COOL = hexc("cfe4ff")
PAPER = (0.98, 0.97, 0.94)
NIGHT_A, NIGHT_B = hexc("141c36"), hexc("2c3c66")
WOOD = hexc("8c5a3c")
F_WIN = (760, 830)                        # 远处 ta 的窗（窗口机位里）


# ================================================================ 小物件
def ghost(c, x, y, s, key, sit=False, walk=None, a=0.9, phone=0.0, arms=None, head_down=0.0, legs=True, col=None):
    """ta：只有虚线轮廓，没有脸、没有颜色。"""
    if a <= 0.01:
        return
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    dy = 52 if sit else 0
    ph = walk or 0.0
    sw = 0.4 * math.sin(ph) if walk is not None else 0.0
    bob = -abs(math.sin(ph)) * 3 if walk is not None else 0.0
    hd = head_down + (6 if phone > 0 else 0)
    head = ell(0, -165 + dy + hd + bob, 24, 26, 16)
    body = [(-22, -140 + dy + bob), (22, -140 + dy + bob), (30, -56 + dy + bob), (-30, -56 + dy + bob)]
    with keep(), group_alpha(c, a):
        shape(c, head, (0.93, 0.94, 0.97), key + "hf", ink=False, alpha=0.22, edge=False)
        shape(c, body, (0.93, 0.94, 0.97), key + "bf", ink=False, alpha=0.22, edge=False)
        with ink_style(col=col or GH, dash=[9, 7], alpha=0.95):
            shape(c, head, None, key + "h", lw=2.6 / max(s, 0.3) ** 0.4)
            shape(c, body, None, key + "b", lw=2.6 / max(s, 0.3) ** 0.4)
            lw = 2.6 / max(s, 0.3) ** 0.4
            if legs:
                for sg in (-1, 1):
                    if sit:
                        line(c, [(sg * 10, -4), (sg * 12, 44)], f"{key}l{sg}", lw)
                    else:
                        line(c, [(sg * 9, -56 + bob), (sg * 9 + math.sin(sw * sg) * 56, 0)], f"{key}l{sg}", lw)
            if phone > 0:
                for sg in (-1, 1):
                    line(c, [(sg * 22, -130 + dy), (sg * 26, -98 + dy), (sg * 8, -108 + dy)], f"{key}a{sg}", lw)
            else:
                hands = arms or [(-30, -70), (30, -70)]
                for i, sg in enumerate((-1, 1)):
                    hx, hy = hands[i]
                    line(c, [(sg * 22, -130 + dy + bob), (hx, hy + dy + bob)], f"{key}a{sg}", lw)
        if phone > 0:
            glow(c, 0, -110 + dy, 110, COOL, 0.55 * phone)
            shape(c, rrect(-10, -126 + dy, 20, 30, 4), hexc("eaf4ff"), key + "ph", lw=1.6, alpha=phone)
    c.restore()


def pplane(c, x, y, s, key, rot=0.0, col=PAPER):
    """纸飞机，机头朝右。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    with keep():
        shape(c, [(-40, -2), (42, 0), (-40, 14)], col, key + "a", lw=2.2)
        shape(c, [(-40, -2), (42, 0), (-30, -18)], darker(col, 0.92), key + "b", lw=2.2)
        line(c, [(-40, 2), (42, 0)], key + "c", 1.4, darker(col, 0.7))
    c.restore()


def backpack(c, x, y, s, key):
    """一只放下来的背包（底部在 y）。"""
    with keep():
        shape(c, rrect(x - 50 * s, y - 120 * s, 100 * s, 120 * s, 24 * s), PACK, key, lw=2.4)
        shape(c, rrect(x - 40 * s, y - 120 * s, 80 * s, 46 * s, 18 * s), darker(PACK, 0.9), key + "f", lw=2)
        shape(c, rrect(x - 28 * s, y - 60 * s, 56 * s, 40 * s, 10 * s), darker(PACK, 0.92), key + "p", lw=1.6)


def lines_illus(c, cx, cy):
    """章节页小插画：一条实线和一条虚线并排走了一段，然后分开。"""
    a = [(cx - 90 + k * 9, cy + 10 + (0 if k < 10 else -(k - 10) ** 1.6 * 2.2)) for k in range(21)]
    b = [(cx - 90 + k * 9, cy + 26 + (0 if k < 10 else (k - 10) ** 1.6 * 2.2)) for k in range(21)]
    with keep():
        line(c, a, "ilA", 4, INK)
        with ink_style(col=GH, dash=[8, 6]):
            line(c, b, "ilB", 4)


def intro(c, t):
    book_intro(c, t, "第七章", "那个人", lines_illus)


# ================================================================ 窗口机位：从她身后往外看
def window_scene(c, t, mode="night", sag=20.0, wob=0.0, broken=None, leaves=0.0, snow_on=0.0, snowfall=0.0,
                 lights=1.0, star_a=0.0, panes=None, gale=0.0, string=False, girl=None, far_ghost=0.0, cup_in_hand=False,
                 far_on=1.0):
    """她坐在窗台上（背影），窗外一片屋顶，远处一扇亮着的窗是 ta 的。"""
    X0, Y0, X1, Y1 = 160, 360, 920, 1240
    night = mode in ("night", "snow")
    wall = {"night": hexc("3a3040"), "snow": hexc("2e2a38"), "morning": hexc("e8dcc8")}[mode]
    fill_all(c, wall)
    c.save()
    c.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    c.clip()
    if mode == "morning":
        vgrad(c, Y0, Y1, [(0, hexc("9fd0ec")), (1, hexc("f4efe0"))], X0 - 50, X1 + 50)
    else:
        vgrad(c, Y0, Y1, [(0, NIGHT_A), (1, NIGHT_B if mode == "night" else hexc("3a4058"))], X0 - 50, X1 + 50)
        r = random.Random(2)
        with keep():
            for k in range(30):
                star(c, r.uniform(X0, X1), r.uniform(Y0, 860), r.uniform(1.4, 2.8), (0.4 + 0.4 * math.sin(t * 2 + k)) *
                     (0.3 if mode == "snow" else 1))
    if star_a > 0:
        with keep():
            glow(c, 770, 520, 120, hexc("fff3c8"), 0.6 * star_a)
            circle(c, 770, 520, 6, hexc("fffbe8"), a=star_a)
    # 一层层屋顶
    r = random.Random(5)
    roof_back = hexc("232a44") if night else hexc("9aa6b8")
    roof_front = hexc("1c2236") if night else hexc("7c879a")
    x = X0 - 40
    k = 0
    while x < X1 + 40:
        w_, h_ = r.uniform(90, 160), r.uniform(60, 180)
        shape(c, [(x, 1000), (x, 1000 - h_), (x + w_ / 2, 1000 - h_ - 30), (x + w_, 1000 - h_), (x + w_, 1000)], roof_back,
              f"rb{k}", lw=1.4, amp=0.3)
        x += w_ + 6
        k += 1
    shape(c, rect(700, 780, 130, 230), roof_back, "fbld", lw=1.0, amp=0.15)            # ta 那栋楼
    shape(c, rect(X0 - 40, 1000, X1 - X0 + 80, 300), roof_front, "rf", lw=1.6)
    x = X0 - 20
    k = 0
    while x < X1 + 40:
        w_ = r.uniform(120, 200)
        h_ = r.uniform(40, 120)
        shape(c, [(x, 1060), (x + w_ * 0.5, 1060 - h_), (x + w_, 1060)], roof_front, f"rfr{k}", lw=1.4)
        x += w_ - 20
        k += 1
    with keep():                                                   # 远处零星的窗光
        rr = random.Random(7)
        wins = [(rr.uniform(X0 + 20, X1 - 20), rr.uniform(900, 1180)) for _ in range(16)]
        for j, (wx, wy) in enumerate(wins):
            if night and j / 16 < lights:
                shape(c, rect(wx, wy, 14, 18), WARM, f"fw{j}", lw=0, edge=False, alpha=0.7, amp=0.2)
        on = far_on if (night and lights > 0.02) else 0.0
        shape(c, rect(F_WIN[0] - 22, F_WIN[1] - 28, 44, 52), mix(hexc("2a3048") if night else hexc("a8b4c4"), WARM, on),
              "fwin", lw=0.8, amp=0.12)
        if on > 0:
            glow(c, F_WIN[0], F_WIN[1], 60, WARM, 0.4 * on)
    if far_ghost > 0:
        ghost(c, F_WIN[0], F_WIN[1] + 18, 0.17, "fg", sit=True, a=far_ghost * far_on, legs=False)
    if snowfall > 0:
        rs = random.Random(11)
        with keep():
            for j in range(int(70 * snowfall)):
                sx = (rs.uniform(X0 - 300, X1) + t * (40 + gale * 500)) % (X1 - X0 + 300) + X0 - 150
                sy = (rs.uniform(Y0, Y1) + t * rs.uniform(60, 120)) % (Y1 - Y0) + Y0
                circle(c, sx, sy, rs.uniform(2, 5), (1, 1, 1), a=0.8)
    c.restore()
    # 窗框
    with keep():
        col = hexc("5a4a40") if night else hexc("b8a488")
        shape(c, rect(X0 - 14, Y0 - 14, X1 - X0 + 28, 14), col, "wft", lw=2)
        shape(c, rect(X0 - 14, Y0 - 14, 14, Y1 - Y0 + 14), col, "wfl", lw=2)
        shape(c, rect(X1, Y0 - 14, 14, Y1 - Y0 + 14), col, "wfr", lw=2)
        if panes is not None:                                      # 两扇窗：0 关上，1 全开
            for sg, hx in ((-1, X0), (1, X1)):
                w_ = (X1 - X0) / 2 * (1 - 0.85 * panes)
                px0 = hx if sg < 0 else hx - w_
                shape(c, rect(px0, Y0, w_, Y1 - Y0), (0.85, 0.92, 0.96), f"pane{sg}", lw=2.4, alpha=0.35)
                shape(c, rect(px0, Y0, w_, Y1 - Y0), None, f"panef{sg}", lw=3)
    if girl:
        girl()
    with keep():                                                   # 窗台上慢慢落了叶子，又积了雪
        if leaves > 0:
            for j in range(int(7 * leaves)):
                shape(c, ell(200 + j * 97 % 700, 1236, 12, 6, 10), hexc(["c9763a", "d9a04a", "a8603a"][j % 3]), f"lf{j}", lw=1)
        shape(c, rect(X0 - 40, Y1, X1 - X0 + 80, 40), hexc("6a5040") if night else hexc("c8b090"), "sill", lw=2.4)
        if snow_on > 0:
            shape(c, [(X0 - 36, Y1 + 2), (X0 - 36, Y1 - 6 * snow_on), (X1 + 36, Y1 - 10 * snow_on), (X1 + 36, Y1 + 2)],
                  (0.98, 0.98, 1.0), "snowsill", lw=1.4, alpha=snow_on)


def _her_back(c, plane=False, arm_up=0.0, x=430, hat=False, tilt=0.0):
    """窗台上的她（背影）。plane：手里拿着一只纸飞机。"""
    if arm_up > 0:
        arms = [(-24, -78), (lerp(60, 70, arm_up), lerp(-110, -230, arm_up))]
    elif plane:
        arms = [(-24, -78), (60, -110)]
    else:
        arms = [(-24, -78), (24, -78)]
    girl(c, x, 1240, 1.7, view="back", sit=True, legs=False, hat=hat, arms=arms, tilt=tilt, key="hb")
    if plane:
        hx = x + arms[1][0] * 1.7
        hy = 1240 + (arms[1][1] + 52) * 1.7
        pplane(c, hx + 20, hy - 10, 0.75, "hand_pl", rot=-0.25 * arm_up)


HAND = (562, 1076)                        # 她手里纸飞机的位置（窗口机位里）


def fly_pt(u, a=HAND, b=F_WIN, lift=200):
    """纸飞机从她的窗飞向远处 ta 的窗：一段弧线，越飞越小。"""
    x = lerp(a[0], b[0], u)
    y = lerp(a[1], b[1], u) - lift * math.sin(u * math.pi)
    sc = lerp(0.75, 0.1, u)
    dx = b[0] - a[0]
    dy = (b[1] - a[1]) - lift * math.pi * math.cos(u * math.pi)
    return x, y, sc, math.atan2(dy, dx)


# ================================================================ 1 纸飞机
def side_talk(c, t):
    """侧面：她坐在窗台上，对着纸杯雀跃地说话，细线从纸杯后面伸出窗外。"""
    fill_all(c, hexc("4a3a40"))
    with keep():
        glow(c, 300, 700, 600, WARM, 0.35)
    c.save()
    c.rectangle(640, 300, 600, 900)
    c.clip()
    vgrad(c, 300, 1200, [(0, NIGHT_A), (1, NIGHT_B)], 600, 1200)
    r = random.Random(3)
    with keep():
        for k in range(18):
            star(c, r.uniform(640, 1080), r.uniform(320, 800), r.uniform(1.4, 2.8), 0.5 + 0.4 * math.sin(t * 2 + k))
    x = 620
    k = 0
    while x < 1100:
        w_, h_ = r.uniform(80, 140), r.uniform(80, 200)
        shape(c, [(x, 1200), (x, 1000 - h_ + 200), (x + w_ / 2, 970 - h_ + 200), (x + w_, 1000 - h_ + 200), (x + w_, 1200)],
              hexc("1c2236"), f"sr{k}", lw=1.4)
        x += w_ + 4
        k += 1
    c.restore()
    with keep():
        shape(c, rect(620, 286, 24, 920), hexc("5a4a40"), "sfr", lw=2)
        shape(c, rect(100, 1180, 980, 40), hexc("6a5040"), "ssill", lw=2.4)
    throw = ease_out(prog(t, 2.0, 1.4))
    fold = math.sin(t * 5) * 4 if t < 1.9 else 0
    reach = min(1, throw * 4)
    girl(c, 420, 1180, 1.9, sit=True, crouch=True, hat=False, look=0.9, head_down=8 if t < 1.9 else -2,
         mouth="smile" if t < 1.9 else "laugh",
         arms=[(-10, -96 + fold), (lerp(28, 70, reach), lerp(-96 - fold, -170, reach))], key="st")
    if throw <= 0:
        pplane(c, 420 + 30 * 1.9, 1180 + (-96 + 52) * 1.9 - 14, 0.9, "stpl", rot=0.1 * math.sin(t * 4))
    elif throw < 1:
        pplane(c, lerp(560, 1150, throw), lerp(1060, 700, throw) - math.sin(throw * math.pi) * 120, lerp(0.9, 0.5, throw),
               "stpl", rot=-0.35)


def h01(c, t):
    if t < 3.5:
        side_talk(c, t)
        return
    u = ease_io(prog(t, 3.6, 3.0))                                # 镜头跟着纸飞机，飞向远处那扇亮着的窗
    k = lerp(1.0, 4.0, u)
    cx, cy = lerp(540, F_WIN[0], u), lerp(960, F_WIN[1] + 10, u)
    with cam(c, cx, cy, k):
        window_scene(c, t, far_ghost=1.0, girl=lambda: _her_back(c, arm_up=1 - ease_out(prog(t, 3.5, 0.8))))
        fu = ease_io(prog(t, 3.5, 3.2))
        if fu < 1:
            x, y, sc, rot = fly_pt(fu)
            pplane(c, x, y, sc, "fly1", rot=rot)


def h02(c, t):
    """远处的窗里，一只纸飞机飞了回来，镜头跟着退回她的窗台。"""
    k = lerp(4.0, 1.0, ease_io(prog(t, 0.4, 3.2)))
    v = (k - 1) / 3.0
    cx, cy = lerp(540, F_WIN[0], v), lerp(960, F_WIN[1] + 10, v)
    with cam(c, cx, cy, k):
        window_scene(c, t, far_ghost=1.0, girl=lambda: _her_back(c))
        fu = 1 - ease_io(prog(t, 0.5, 3.0))
        if t < 3.5:
            x, y, sc, rot = fly_pt(fu, lift=160)
            pplane(c, x, y, sc, "pl1", rot=rot + math.pi)
        else:
            land = ease_out(prog(t, 3.5, 0.4))
            pplane(c, lerp(HAND[0], 720, land), lerp(HAND[1], 1222, land), 0.7, "pl1", rot=lerp(0.3, 0.0, land))


def h03(c, t):
    """她拿起纸飞机翻看，又望向远处那扇窗。"""
    def her():
        look = 0.0 if t < 3.0 else 0.6
        girl(c, 430, 1240, 1.7, view="back", sit=True, legs=False, hat=False, look=look,
             arms=[(-24, -78), (60, -110)], key="hb")
    window_scene(c, t, far_ghost=1.0, girl=her)
    turn = math.sin(t * 2.2) * 0.5 if t < 3.0 else 0.2
    pplane(c, 590, 1100, 0.75, "pl1", rot=turn)


def h04(c, t):
    """她也折了一只飞回去；另一只从远处飞来，两只在半空擦身而过。"""
    send = ease_io(prog(t, 0.6, 2.8))
    back = ease_io(prog(t, 0.9, 2.8))
    raise_ = math.sin(clamp(prog(t, 0.2, 0.8)) * math.pi)
    window_scene(c, t, far_ghost=1.0, girl=lambda: _her_back(c, plane=send <= 0, arm_up=raise_))
    pplane(c, 720, 1222, 0.7, "pl1")                               # ta 的那只留在窗台上
    if 0 < send < 1:
        x, y, sc, rot = fly_pt(send)
        pplane(c, x, y, sc, "pl2", rot=rot, col=hexc("dfe8f2"))
    if 0 < back < 1:
        x, y, sc, rot = fly_pt(1 - back, lift=120)
        pplane(c, x, y + 30, sc, "pl3", rot=rot + math.pi)


# ================================================================ 2 陪伴不一定是同行
def cabin(c, t, her_look=-0.9, ghost_a=1.0, ghost_x=730, ghost_walk=None, sky="day", lean=0.0, mouth="smile"):
    """飞机上两个座位（正面）：她靠窗，旁边的座位。"""
    fill_all(c, hexc("e4ded2"))
    shape(c, rect(-20, 0, W + 40, 300), hexc("d6cfc2"), "bins", lw=2.4)
    for k in range(3):
        line(c, [(k * 380 + 40, 300), (k * 380 + 300, 300)], f"bl{k}", 2, hexc("b8b0a0"))
    c.save()
    c.rectangle(-20, 520, 290, 420)
    c.clip()
    sky_c = [hexc("8fc4ea"), hexc("e6f2fa")] if sky == "day" else [hexc("8a7a9a"), hexc("f0b8a0")]
    vgrad(c, 520, 940, [(0, sky_c[0]), (1, sky_c[1])], -100, 300)
    for k in range(4):
        x = (k * 180 - t * 160) % 520 - 140
        cloud(c, x, 620 + (k % 2) * 160, 0.9, f"cc{k}", a=0.9)
    c.restore()
    with keep():
        shape(c, rrect(50, 540, 210, 380, 100), None, "port", lw=6)
        shape(c, rrect(30, 520, 250, 420, 116), None, "port2", lw=3)
    shape(c, rect(-20, 1240, W + 40, 700), hexc("8a8478"), "cfl", lw=3)
    seat = hexc("5a6a8a")
    for k, x in enumerate((390, 730)):
        shape(c, rrect(x - 150, 700, 300, 520, 40), seat, f"sb{k}", lw=3)
        shape(c, rrect(x - 110, 700, 220, 90, 20), (0.95, 0.95, 0.93), f"hr{k}", lw=2)
    girl(c, 390 + lean, 1165, 1.6, sit=True, legs=False, hat=False, look=her_look, mouth=mouth, key="cab")
    hat_item(c, 400, 1150, 0.8, "cabhat")
    if ghost_a > 0:
        if ghost_walk is None:
            ghost(c, ghost_x, 1165, 1.6, "cg", sit=True, legs=False, a=ghost_a, col=hexc("e4e8ef"))
        else:
            ghost(c, ghost_x, 1250, 1.6, "cg", walk=ghost_walk, a=ghost_a, col=hexc("e4e8ef"))
    for k, x in enumerate((390, 730)):
        shape(c, rrect(x - 160, 1150, 320, 50, 18), darker(seat, 0.92) + (1.0,), f"sc{k}", lw=3)
    shape(c, rrect(552, 1080, 16, 140, 6), hexc("4a5670"), "arm", lw=2)


def h05(c, t):
    cabin(c, t, lean=-10 * ease_io(prog(t, 0.5, 1.0)), mouth="smile")


def path_scene(c, t):
    """山路：她总停下来看花看山；ta 低头看手机一直往前走。"""
    vgrad(c, 0, 1100, [(0, hexc("8fbfe0")), (1, hexc("eef4f0"))])
    for k, (x, h_, col) in enumerate(((220, 420, "b8c8d8"), (620, 520, "a8bcd0"), (960, 400, "b8c8d8"))):
        mountain(c, x, 1000, 560, h_, hexc(col), f"pm{k}")
    shape(c, hill_pts(1000, 30, 0.005, 0.6), hexc("9cc08a"), "ph1", lw=2.4)
    shape(c, [(-20, 1300), (-20, 1190), (W + 20, 1150), (W + 20, 1300)], hexc("d8c8a8"), "path", lw=2.4)
    shape(c, rect(-20, 1300, W + 40, 700), hexc("8fb07a"), "pg", lw=2.4)
    with keep():
        line(c, [(330, 1250), (332, 1214)], "fst", 2.4, hexc("5a8a4a"))
        for j in range(5):
            a = j / 5 * 2 * math.pi
            circle(c, 332 + math.cos(a) * 9, 1206 + math.sin(a) * 9, 7, hexc("f2a6c0"))
        circle(c, 332, 1206, 5, hexc("f7d34f"))
    crouch = t > 3.0
    if crouch:
        girl(c, 280, 1210, 1.4, sit=True, crouch=True, hat=True, pack=True, look=0.6, head_down=6, mouth="smile", key="pw")
    else:
        girl(c, 250, 1240, 1.4, hat=True, pack=True, look=-0.3, look_up=0.6, mouth="o", key="pw")
    gx = lerp(470, 900, ease_out(prog(t, 0.0, 3.6)))
    ghost(c, gx, 1222, 1.35, "pgh", walk=t * 5 if t < 3.6 else None, phone=1.0)


def h06(c, t):
    path_scene(c, t)


def whale_bones(c, x, y, s, key, sway=0.0):
    """吊在展厅半空的一副鲸鱼骨架：宽宽的头骨和下颌、一节节的脊椎、弯弯的肋骨、胸鳍的骨头、尾巴。"""
    bone = hexc("f2ead8")
    edge = hexc("8a7f6a")
    c.save()
    c.translate(x, y + sway)
    c.scale(s, s)

    def bone_line(pts, k, w):
        line(c, pts, f"{key}{k}o", w + 3, edge)
        line(c, pts, f"{key}{k}i", w, bone)
    with keep():
        for k, hx in enumerate((-300, 60, 360)):                   # 吊着它的细线
            line(c, [(hx, -400), (hx, -20)], f"{key}w{k}", 1.4, hexc("8a8a8a"), alpha=0.6)
        n = 22
        spine = []
        for i in range(n):
            u = i / (n - 1)
            spine.append((lerp(-240, 520, u), -14 * math.sin(u * math.pi) + 40 * u * u))
        for i in range(2, 14):                                     # 肋骨
            px, py = spine[i]
            ln = 150 * math.sin(lerp(0.5, 2.9, (i - 2) / 11))
            bone_line([(px, py + 10), (px - 18, py + ln * 0.6), (px - 6, py + ln)], f"r{i}", 4)
        bone_line([(-170, 30), (-130, 120), (-60, 150), (-20, 140)], "fin", 7)       # 胸鳍
        for i, (px, py) in enumerate(spine):                       # 脊椎
            w_ = lerp(26, 10, i / n)
            shape(c, rect(px - w_ / 2, py - w_ * 0.6, w_, w_ * 1.2), bone, f"{key}v{i}", lw=1.6, amp=0.3)
        shape(c, [(-520, -10), (-380, -50), (-250, -40), (-230, 20), (-360, 40), (-520, 20)], bone, key + "sk",
              lw=2.6)                                              # 宽宽的头骨
        bone_line([(-520, 30), (-380, 70), (-250, 40)], "jaw", 9)  # 下颌
        shape(c, [(520, 40), (620, -40), (590, 40), (620, 120)], bone, key + "tl", lw=2.4)
    c.restore()


def hall(c, t, beam=1.0, patch=None):
    """海洋博物馆高高的展厅：半空吊着一副鲸鱼骨架，正面是一整面蓝色的大水槽，
    水里有慢慢游过的鱼和一只蝠鲼；水光一圈圈晃在墙上和地上。世界坐标，长椅在 x≈1400。"""
    shape(c, rect(-600, -200, 2800, 1500), hexc("d8e4e8"), "hw", lw=0, edge=False)
    for k in range(6):
        line(c, [(-200 + k * 420, 0), (-200 + k * 420, 1250)], f"hcol{k}", 2, hexc("bccdd4"))
    shape(c, rect(-600, 1250, 2800, 900), hexc("9fb4bc"), "hf", lw=3)
    for k in range(10):
        line(c, [(-600, 1290 + k * k * 8), (2200, 1290 + k * k * 8)], f"hfl{k}", 1.2, hexc("8ea2aa"), alpha=0.5)
    tx0, ty0, tw, th = 110, 330, 860, 900                          # 一整面大水槽
    shape(c, rect(tx0 - 26, ty0 - 26, tw + 52, th + 26), hexc("5a6a74"), "tfr", lw=3)
    c.save()
    c.rectangle(tx0, ty0, tw, th)
    c.clip()
    vgrad(c, ty0, ty0 + th, [(0, hexc("5fb0d8")), (0.5, hexc("2f78b0")), (1, hexc("163e70"))], tx0, tx0 + tw)
    with keep():
        for j in range(5):                                         # 从水面照下来的光
            x = tx0 + 120 + j * 170 + 30 * math.sin(t * 0.6 + j)
            shape(c, [(x - 30, ty0), (x + 30, ty0), (x + 120, ty0 + th), (x - 20, ty0 + th)], hexc("dff4ff"),
                  f"tray{j}", lw=0, edge=False, alpha=0.12)
        mx = tx0 + 260 + ((t * 45) % (tw + 400)) - 200             # 一只蝠鲼慢慢滑过去
        my = ty0 + 380 + 40 * math.sin(t * 0.5)
        flap = 30 * math.sin(t * 1.6)
        shape(c, [(mx - 150, my + flap), (mx, my - 50), (mx + 60, my - 10), (mx, my + 40), (mx - 150, my - flap)],
              hexc("1d3a5c"), "manta", lw=0, edge=False, alpha=0.85)
        line(c, [(mx - 20, my), (mx - 200, my + 30)], "mtail", 3, hexc("1d3a5c"), alpha=0.85)
        r = random.Random(7)
        for k in range(14):                                        # 一群小鱼
            fx = tx0 + ((r.uniform(0, tw) - t * r.uniform(30, 70)) % (tw + 100)) - 50
            fy = ty0 + r.uniform(120, th - 120) + 8 * math.sin(t * 2 + k)
            shape(c, [(fx - 18, fy), (fx, fy - 7), (fx + 14, fy), (fx, fy + 7)], hexc("e8f2f8"), f"fs{k}", lw=0,
                  edge=False, alpha=0.7)
            shape(c, [(fx + 14, fy), (fx + 24, fy - 7), (fx + 24, fy + 7)], hexc("e8f2f8"), f"ft{k}", lw=0, edge=False,
                  alpha=0.7)
        for k in range(12):                                        # 气泡
            bx = tx0 + 60 + (k * 73) % (tw - 120)
            by = ty0 + th - ((t * 90 + k * 140) % th)
            circle(c, bx + 6 * math.sin(t * 3 + k), by, 4 + (k % 3) * 2, hexc("e8f6ff"), a=0.5)
        for k in range(9):                                         # 水底轻轻摆的海草
            bx = tx0 + 50 + k * 100
            pts = [(bx + 18 * math.sin(t * 1.2 + k + j * 0.6) * j / 6, ty0 + th - j * 34) for j in range(7)]
            line(c, pts, f"sea{k}", 6, hexc("4f9a7a"), alpha=0.8)
        for k in range(4):                                         # 分叉的珊瑚
            bx = tx0 + 120 + k * 220
            by = ty0 + th
            col = hexc(["f08a7a", "f2b07a", "e88ab0", "f08a7a"][k])
            line(c, [(bx, by), (bx, by - 90)], f"cr{k}", 9, col)
            line(c, [(bx, by - 50), (bx - 40, by - 110)], f"cra{k}", 7, col)
            line(c, [(bx, by - 70), (bx + 36, by - 130)], f"crb{k}", 7, col)
            line(c, [(bx - 40, by - 110), (bx - 50, by - 140)], f"crc{k}", 5, col)
    c.restore()
    with keep():                                                   # 水光一圈圈晃在墙上和地上
        for k in range(10):
            wx = 60 + k * 110 + 30 * math.sin(t * 0.9 + k * 1.7)
            wy = 1300 + (k % 3) * 60 + 10 * math.cos(t * 1.1 + k)
            shape(c, ell(wx, wy, 70, 14, 16), hexc("dff4ff"), f"cau{k}", lw=0, edge=False, alpha=0.35)
    whale_bones(c, 680, 150, 1.1, "wb", sway=4 * math.sin(t * 0.4))
    if beam > 0:
        with keep():
            shape(c, [(400, -200), (680, -200), (900, 1260), (180, 1260)], hexc("fff6dc"), "beam", lw=0, edge=False,
                  alpha=0.18 * beam)
    if patch is not None:                                          # 地上的光斑慢慢移过去
        with keep():
            px = lerp(-200, 900, patch)
            shape(c, [(px, 940), (px + 200, 940), (px + 260, 1240), (px + 60, 1240)], hexc("dff4ff"), "patch", lw=0,
                  edge=False, alpha=0.4)
    shape(c, rect(1240, 1150, 320, 26), WOOD, "bench", lw=2.4)
    for x in (1270, 1530):
        line(c, [(x, 1176), (x, 1250)], f"bnl{x}", 5, hexc("5a3a2a"))


def h07(c, t):
    if t < 3.2:                                                    # 她看得入了神
        hall(c, t)
        girl(c, 540, 1240, 1.35, view="back", hat=True, pack=True, key="mu")
        return
    if t < 6.4:                                                    # 回头：长椅上 ta 低头对着发亮的手机
        lt = t - 3.2
        pan = ease_io(prog(lt, 0.6, 2.0))
        with cam(c, lerp(540, 1300, pan), 960, 1.0):
            hall(c, t)
            girl(c, 540, 1240, 1.35, view="front" if lt > 0.2 else "back", hat=True, pack=True, look=0.9, mouth="flat",
                 key="mu")
            ghost(c, 1400, 1150, 1.4, "mgh", sit=True, phone=1.0)
        return
    lt = t - 6.4                                                   # 手机屏幕：一格一格的表格，一个小护照图案，没有字
    fill_all(c, hexc("1e2030"))
    with keep():
        glow(c, 540, 760, 560, COOL, 0.25)
        shape(c, rrect(260, 180, 560, 1060, 56), hexc("2a2e3a"), "mph", lw=3)
        shape(c, rect(288, 240, 504, 940), hexc("f2f6fa"), "mps", lw=1)
        shape(c, rrect(470, 280, 140, 190, 14), hexc("3a4a6a"), "pass", lw=2)
        shape(c, ell(540, 360, 34, 34, 18), None, "pemb", lw=2.4)
        line(c, [(506, 360), (574, 360)], "pemb2", 1.6)
        line(c, [(540, 326), (540, 394)], "pemb3", 1.6)
        for j in range(5):
            y = 530 + j * 110
            shape(c, rrect(320, y, 440, 64, 12), (1, 1, 1), f"fld{j}", lw=2)
            fill = clamp((lt * 2.2 - j) / 1.0)
            if fill > 0:
                line(c, [(344, y + 32), (344 + 300 * fill, y + 32)], f"fill{j}", 6, hexc("c8d2e0"))
        shape(c, rrect(380, 1090, 320, 60, 24), hexc("3f6fb5"), "pbtn", lw=2)


def h08(c, t):
    """展厅暗下来，只剩两团光。"""
    dark = ease_io(prog(t, 0.3, 1.6))
    with cam(c, 980, 960, 0.72):
        hall(c, t, beam=1.0 - 0.3 * dark)
        veil(c, (0.06, 0.06, 0.1), 0.0)
    veil(c, (0.05, 0.05, 0.09), 0.72 * dark)
    with cam(c, 980, 960, 0.72):
        with keep():
            shape(c, [(400, -200), (680, -200), (860, 1260), (220, 1260)], hexc("fff6dc"), "beam2", lw=0, edge=False,
                  alpha=0.25 * dark)
            shape(c, ell(540, 1262, 250, 46, 30), hexc("fff3d0"), "pool", lw=0, edge=False, alpha=0.35 * dark)
            glow(c, 1400, 1080, 260, COOL, 0.45 * dark)
        girl(c, 540, 1240, 1.35, view="back", hat=True, pack=True, key="mu")
        ghost(c, 1400, 1150, 1.4, "mgh", sit=True, phone=1.0)


# ================================================================ 3 一场很私人的对话
def lookout(c, t, crowd=True):
    vgrad(c, 0, 1100, [(0, hexc("8ab8e0")), (1, hexc("f0eee6"))])
    for k in range(5):
        cloud(c, (k * 260 + t * 12) % 1300 - 100, 900 + (k % 2) * 40, 1.6, f"lc{k}", a=0.95)
    shape(c, rect(-20, 1000, W + 40, 120), (0.98, 0.98, 0.97), "csea", lw=0, edge=False)
    shape(c, rect(-20, 1110, W + 40, 900), hexc("9a8a78"), "lrock", lw=3)
    line(c, [(-20, 1060), (W + 20, 1060)], "rail", 5, hexc("6a5a4a"))
    for k in range(10):
        line(c, [(k * 120, 1060), (k * 120, 1140)], f"rp{k}", 4, hexc("6a5a4a"))
    if crowd:
        leave = max(0.0, t - 2.4)
        for k in range(5):
            x = 330 + k * 130 + leave * (300 + k * 40)
            if x > 1300:
                continue
            silhouette(c, x, 1230, 1.3, f"lcw{k}", walk=leave * 7 + k if leave > 0 else None)
            with keep():
                shape(c, rrect(x + 14, 1230 - 250, 22, 34, 4), hexc("3a3f4a"), f"lph{k}", lw=1.4, alpha=0.9)
                fl = (t * 1.7 + k * 0.37) % 1
                if leave == 0 and fl < 0.12:
                    glow(c, x + 25, 1230 - 240, 90, (1, 1, 1), 0.8)
    girl(c, 190, 1232, 1.4, view="back", hat=True, pack=True, key="lk")


def h09(c, t):
    lookout(c, t)


def old_street(c, t):
    sun = prog(t, 0.0, 3.2)
    vgrad(c, 0, 900, [(0, mix(hexc("9fd0ec"), hexc("f2b88a"), sun)), (1, mix(hexc("f4efe0"), hexc("ffd9a8"), sun))])
    shape(c, rect(-20, 300, 480, 900), hexc("d8c4a8"), "ow1", lw=3)
    shape(c, rect(620, 260, 480, 940), hexc("c8b498"), "ow2", lw=3)
    for k, (x, y) in enumerate(((80, 420), (300, 420), (720, 380), (920, 380))):
        shape(c, rect(x, y, 90, 120), hexc("6a5040"), f"own{k}", lw=2)
    shape(c, rect(-20, 1200, W + 40, 800), hexc("b8a890"), "ost", lw=3)
    shape(c, rect(80, 1150, 400, 60), hexc("c8b8a0"), "step0", lw=2)
    shape(c, rect(120, 1100, 340, 50), hexc("d4c4ac"), "step1", lw=2)
    shape(c, rect(735, 1150, 90, 60), hexc("8a6a4a"), "stool", lw=2)
    sl = lerp(40, 280, sun)                                        # 影子从短变长
    with keep():
        shape(c, ell(300 + sl * 0.6, 1214, sl, 14, 16), hexc("6a5a4a"), "shA", lw=0, edge=False, alpha=0.35)
        shape(c, ell(780 + sl * 0.6, 1214, sl, 14, 16), hexc("6a5a4a"), "shB", lw=0, edge=False, alpha=0.35)
    girl(c, 300, 1150, 1.5, sit=True, hat=True, pack=True, look=0.8, mouth="smile", arms=[(-20, -70), (22, -126)], key="os")
    local(c, 780, 1150, 1.5, "old", hexc("7a6a5a"), hexc("2f2a28"), "short", sit=True, age=1.0, look=0.2, head_down=8,
          arms=[(-20, -60), (20, -60)])
    with keep():                                                   # 越编越高的竹篮
        hgt = lerp(20, 60, prog(t, 0.0, 3.2))
        bx, by = 780, 1150 - 20
        shape(c, [(bx - 50, by - hgt), (bx + 50, by - hgt), (bx + 36, by), (bx - 36, by)], hexc("c8a060"), "bask", lw=2)
        for j in range(int(hgt / 10)):
            line(c, [(bx - 46 + j * 1.5, by - j * 10 - 5), (bx + 46 - j * 1.5, by - j * 10 - 5)], f"bw{j}", 1.4, hexc("8a6a3a"))


def moor(c, t, girl_on=True, tiny=False):
    vgrad(c, 0, 1050, [(0, hexc("7a9ab8")), (1, hexc("dfe4e0"))])
    for k in range(4):
        cloud(c, (k * 340 - t * 260) % 1500 - 200, 300 + k * 110, 1.5, f"mc{k}", a=0.85)
    shape(c, hill_pts(1000, 40, 0.004, 1.0), hexc("a8b088"), "mh", lw=2.4)
    shape(c, rect(-20, 1080, W + 40, 900), hexc("8a9a68"), "mg", lw=2.4)
    with keep():
        for row in range(7):
            y = 1060 + row * 40
            for k in range(14):
                x = k * 82 + (row % 2) * 40
                bend = 18 * math.sin(t * 3 - k * 0.5 + row)
                line(c, [(x, y + 30), (x + bend * 0.5, y + 10), (x + bend, y - 10)], f"gr{row}{k}", 2, hexc("c8cf9a"),
                     alpha=0.7)
    if girl_on:
        if tiny:
            girl(c, 540, 1150, 0.45, hat=True, pack=True, key="mt")
        else:
            shape(c, ell(560, 1205, 110, 36, 18), hexc("8a8478"), "mrock", lw=2.4)
            girl(c, 560, 1180, 1.5, sit=True, crouch=True, hat=True, pack=True, look=0.5, mouth="flat", key="mo")


def old_tree(c, t):
    """一棵很老很大的树：她坐在树下的石头上，仰头看了很久；叶影在她身上慢慢移过去，几片叶子落下来。"""
    sun = prog(t, 0.0, 3.2)
    vgrad(c, 0, 1100, [(0, hexc("a8d0e8")), (1, hexc("f2f0dc"))])
    with keep():
        glow(c, lerp(200, 900, sun), 260, 300, hexc("fff0c0"), 0.5)
    shape(c, hill_pts(1080, 20, 0.004, 0.7), hexc("b8c890"), "th", lw=2.4)
    shape(c, rect(-20, 1160, W + 40, 900), hexc("a8b878"), "tg", lw=2.4)
    shape(c, [(470, 1180), (500, 700), (460, 560), (560, 640), (640, 520), (620, 720), (660, 1180)], hexc("7a5a3e"),
          "trunk", lw=3)                                           # 粗粗的树干
    for k, (dx, dy, r_) in enumerate(((-260, -40, 210), (-60, -150, 260), (200, -60, 230), (330, 80, 170),
                                      (-330, 110, 160), (40, 40, 220))):
        shape(c, ell(560 + dx, 470 + dy, r_, r_ * 0.8, 24), mix(hexc("5f8a4a"), hexc("7aa860"), (k % 3) / 2),
              f"crown{k}", lw=2.4, amp=0.8)
    with keep():                                                   # 叶影慢慢移过去
        r = random.Random(12)
        for k in range(14):
            x = r.uniform(-100, W + 100) + lerp(-160, 160, sun)
            y = r.uniform(1170, 1600)
            shape(c, ell(x, y, r.uniform(30, 70), r.uniform(10, 18), 14), hexc("4a6a3a"), f"lsh{k}", lw=0, edge=False,
                  alpha=0.25)
        for k in range(4):                                         # 落下来的叶子
            ph = (t * 0.35 + k * 0.27) % 1
            lx = 300 + k * 160 + 40 * math.sin(ph * 6 + k)
            ly = lerp(560, 1180, ph)
            shape(c, ell(lx, ly, 12, 6, 10), hexc("c8a040"), f"leaf{k}", lw=1.2, alpha=1 - ph * 0.5)
    shape(c, ell(300, 1196, 90, 26, 16), hexc("9a948a"), "tstone", lw=2.4)
    girl(c, 300, 1180, 1.45, sit=True, hat=True, pack=True, look=0.6, look_up=0.8, mouth="o", key="tree")


def museum_out(c, t):
    """海洋博物馆的外面：一整面波浪形的屋顶，她在台阶下面，只是小小的一点。"""
    vgrad(c, 0, 1200, [(0, hexc("8fc4ea")), (1, hexc("f0f2ea"))])
    pts = [(60, 640)] + [(60 + i * 32, 600 - 60 * math.sin(i * 0.35)) for i in range(31)] + [(1020, 640)]
    shape(c, pts + [(1020, 700), (60, 700)], hexc("e8eef0"), "mroof", lw=3)
    shape(c, rect(100, 700, 880, 440), hexc("dfe6e8"), "mbody", lw=3)
    for k in range(7):
        shape(c, rect(150 + k * 120, 760, 60, 380), hexc("bcd8e4"), f"mwin{k}", lw=2)
    shape(c, rect(-20, 1140, W + 40, 40), hexc("c8c8c0"), "mstep1", lw=2)
    shape(c, rect(-20, 1180, W + 40, 900), hexc("d8d4c8"), "mplaza", lw=2.4)
    girl(c, 540, 1240, 0.5, view="back", hat=True, pack=True, key="mo2")


def h10(c, t):
    k = min(int(t / 3.17), 2)
    u = t - k * 3.17
    if k == 0:
        old_tree(c, u)
    elif k == 1:
        old_street(c, u)
    else:
        moor(c, u)


def seaside(c, t, tiny=False, city=0.0):
    vgrad(c, 0, 900, [(0, hexc("9fcbe8")), (1, hexc("f2f0e4"))])
    if city > 0:                                                   # 身后远处城市的轮廓，像铅笔印一样被擦淡
        r = random.Random(4)
        x = 80
        pts = [(60, 900)]
        while x < 1020:
            h_ = r.uniform(60, 220)
            pts += [(x, 900 - h_), (x + 60, 900 - h_)]
            x += 70
        pts += [(1020, 900)]
        with keep():
            line(c, pts, "city", 2, hexc("8a8a92"), alpha=0.6 * city)
    shape(c, rect(-20, 900, W + 40, 300), hexc("6aa0c8"), "sea2", lw=2.4)
    with keep():
        for j in range(4):
            y = 960 + j * 60
            line(c, [(x, y + 8 * math.sin(x * 0.02 + t * 2 + j)) for x in range(-20, W + 40, 40)], f"sw{j}", 2.4,
                 (1, 1, 1), alpha=0.5)
    shape(c, rect(-20, 1180, W + 40, 800), hexc("e8d8b0"), "sand2", lw=3)
    if tiny:
        girl(c, 540, 1200, 0.45, hat=True, pack=True, key="st2")
    else:
        girl(c, 540, 1250, 1.7, view="back", hat=True, pack=True, key="st3")
        with keep():                                               # 帽带被风吹起来
            for j in range(2):
                line(c, [(540 + 24 * 1.7, 1250 - 168 * 1.7),
                         (540 + 60 * 1.7, 1250 - (172 - j * 8) * 1.7 + 6 * math.sin(t * 9 + j)),
                         (540 + 95 * 1.7, 1250 - (166 - j * 12) * 1.7 + 10 * math.sin(t * 9 + j + 1))], f"rb{j}", 4,
                     hexc("bf4a3c"))


def h11(c, t):
    if t < 3.2:                                                    # 四个大风景，她都只是一个小点
        k = min(int(t / 0.8), 3)
        if k == 0:
            vgrad(c, 0, 1300, [(0, hexc("7aa8d8")), (1, hexc("e8f0f4"))])
            mountain(c, 540, 1200, 1300, 980, hexc("a8b8cc"), "bigm")
            shape(c, rect(-20, 1200, W + 40, 800), hexc("9a9a88"), "bmg", lw=2)
            girl(c, 540, 1200, 0.42, hat=True, pack=True, key="tm")
        elif k == 1:
            moor(c, t, tiny=True)
        elif k == 2:
            museum_out(c, t)
        else:
            seaside(c, t, tiny=True)
        return
    lt = t - 3.2
    seaside(c, lt, city=1.0 - ease_io(prog(lt, 0.3, 2.8)))


def h12(c, t):
    """一个人在雪山脚下往上爬，听见自己的心跳。"""
    beat = 0.0
    for b0 in (math.floor(t / 0.75) * 0.75, math.floor(t / 0.75) * 0.75 - 0.75):
        dt = t - b0
        if dt >= 0:
            beat = max(beat, math.exp(-dt * 9) + 0.6 * math.exp(-max(0, dt - 0.2) * 9) * (dt > 0.2))
    pulse = beat if t > 3.0 else 0.0
    with cam(c, 540, 1100, 1.0 + 0.012 * pulse):
        vgrad(c, -200, 1000, [(0, hexc("1e4a8c")), (1, hexc("8ab8e0"))], -300, W + 300)
        mountain(c, 300, 1000, 900, 760, hexc("c8d4e4"), "hm1")
        mountain(c, 820, 1000, 800, 640, hexc("b8c6da"), "hm2")
        shape(c, rect(-300, 990, 1700, 800), hexc("c8bca8"), "hplain", lw=2)
        shape(c, [(-300, 1700), (-300, 1300), (300, 1240), (1400, 980), (1400, 1700)], hexc("a89a88"), "hslope", lw=3)
        shape(c, rect(-300, 1500, 1700, 500), hexc("a89a88"), "hslope2", lw=0, edge=False)
        r = random.Random(8)
        with keep():
            for k in range(20):
                x = r.uniform(0, 1080)
                y = 1250 - (x - 300) * 0.24 + r.uniform(20, 300)
                shape(c, ell(x, y, r.uniform(8, 18), r.uniform(5, 10), 10), hexc("7a6a5a"), f"hr{k}", lw=1, amp=0.4)
        climb = ease_io(prog(t, 0.0, 3.0))
        gx = lerp(320, 520, climb)
        gy = 1240 - (gx - 300) * 0.24
        if t < 3.0:
            girl(c, gx, gy, 1.5, hat=True, pack=True, look=0.7, mouth="o", walk=t * 3.5, key="hp")
        elif t < 6.0:
            girl(c, gx, gy, 1.5, hat=True, pack=True, look=0.4, head_down=12, mouth="o", tilt=0.12,
                 arms=[(-20, -60), (20, -60)], key="hp")
        else:
            girl(c, gx, gy, 1.5, hat=True, pack=True, look=0.2, look_up=1.0, mouth="smile", key="hp")
        with keep():                                               # 呼出的白气
            ph = (t * 1.33) % 1
            shape(c, ell(gx + 36 + ph * 30, gy - 230 - ph * 30, 10 + ph * 18, 8 + ph * 10, 10), (1, 1, 1), "brth",
                  lw=0.8, alpha=0.75 * (1 - ph))
        if t > 6.0:                                                # 每一下心跳，都从她身上荡开一圈光
            with keep():
                for j in range(4):
                    b0 = math.floor(t / 0.75) * 0.75 - j * 0.75
                    u = (t - b0) / 3.0
                    if b0 >= 6.0 and 0 <= u < 1:
                        shape(c, ell(gx, gy - 120, 60 + u * 900, 30 + u * 420, 40), None, f"ring{j}", lw=3,
                              alpha=0.5 * (1 - u))
                        with ink_style(col=hexc("fff6dc")):
                            shape(c, ell(gx, gy - 120, 60 + u * 900, 30 + u * 420, 40), None, f"ringw{j}", lw=2,
                                  alpha=0.6 * (1 - u))


def h13(c, t):
    """夜里躺在荒原上，满天星星转出一圈圈星轨。"""
    vgrad(c, -100, 1200, [(0, hexc("0c1028")), (1, hexc("2a3060"))])
    r = random.Random(13)
    pole = (540, 380)
    with keep():
        for k in range(110):
            rad = r.uniform(30, 900)
            a0 = r.uniform(0, 2 * math.pi)
            sweep = 0.12 + t * 0.1
            n = 10
            pts = [(pole[0] + math.cos(a0 + sweep * i / n) * rad, pole[1] + math.sin(a0 + sweep * i / n) * rad * 0.9)
                   for i in range(n + 1)]
            if all(p[1] < 1100 for p in pts):
                line(c, pts, f"trl{k}", r.uniform(1.4, 2.6), hexc(r.choice(["fff6dc", "dfe8ff", "ffe8c8"])),
                     alpha=r.uniform(0.4, 0.8), amp=0.2)
    shape(c, hill_pts(1080, 26, 0.005, 0.3), hexc("141a30"), "nh", lw=2)
    c.save()
    c.translate(560, 1150)
    c.rotate(-math.pi / 2 + 0.05)
    girl(c, 0, 0, 1.2, hat=False, look=0.0, look_up=0.4, mouth="smile", key="ly")
    c.restore()
    hat_item(c, 700, 1160, 0.8, "lyhat")


# ================================================================ 4 交集很小
def hillside(c, t, drain=0.0):
    with grade(sat=1.0 - 0.95 * drain):
        with nokeep():
            vgrad(c, 0, 1100, [(0, hexc("6aa8e0")), (1, hexc("f4e6c8"))])
            shape(c, hill_pts(980, 40, 0.004, 0.8), hexc("8ab070"), "hs1", lw=2.4)
            shape(c, [(-20, 1300), (-20, 1150), (500, 1100), (W + 20, 1180), (W + 20, 1300)], hexc("7aa060"), "hs2", lw=2.4)
            shape(c, rect(-20, 1290, W + 40, 700), hexc("6a9050"), "hs3", lw=2.4)
            for k in range(8):
                cx, cy = 200 + k * 110, 1200 + (k % 3) * 20
                circle(c, cx, cy, 6, hexc(["f2a6c0", "f7d34f", "ffffff"][k % 3]))


def birds(c, t, cx=600, cy=420):
    with keep():
        for k in range(14):
            a = t * 0.9 + k * 0.12
            x = cx + math.cos(a) * 320 - 100
            y = cy + math.sin(a) * 120 + (k % 3) * 18
            fl = math.sin(t * 12 + k) * 8
            line(c, [(x - 14, y - fl), (x, y), (x + 14, y - fl)], f"bd{k}", 2.4, hexc("3a3a4a"))


def h14(c, t):
    if t < 3.2:
        hillside(c, t)
        birds(c, t)
        girl(c, 380, 1240, 1.5, hat=True, pack=True, look=0.6, look_up=0.8, mouth="o", key="hl")
        mate(c, 0, 660, 1240, 1.45, pack=True, look=0.2, look_up=0.7, mouth="laugh", arms=[(-24, -78), (40, -210)])
        return
    lt = t - 3.2
    drain = ease_io(prog(lt, 0.3, 2.4))
    hillside(c, t, drain)
    girl(c, 380, 1240, 1.5, hat=True, pack=True, look=0.4, mouth="flat", key="hl")
    ghost(c, 660, 1240, 1.45, "hgh", phone=1.0)


def h15(c, t):
    """旅途最后一晚，两盏路灯，两圈光只重叠了窄窄一小条。"""
    vgrad(c, 0, 1100, [(0, hexc("0e1226")), (1, hexc("232a48"))])
    shape(c, rect(-20, 1100, W + 40, 900), hexc("2a2c38"), "nst", lw=3)
    for k, x in enumerate((280, 800)):
        line(c, [(x, 1210), (x, 560)], f"lpp{k}", 7, hexc("3a3a48"))
        line(c, [(x, 560), (x + (40 if k == 0 else -40), 540)], f"lpa{k}", 6, hexc("3a3a48"))
        lx = x + (40 if k == 0 else -40)
        with keep():
            glow(c, lx, 560, 160, WARM, 0.5)
            shape(c, [(lx - 14, 560), (lx + 14, 560), (lx + 250, 1210), (lx - 250, 1210)], WARM, f"cone{k}", lw=0,
                  edge=False, alpha=0.12)
            shape(c, ell(lx, 1210, 252, 54, 30), WARM, f"pool{k}", lw=0, edge=False, alpha=0.3)
            circle(c, lx, 560, 12, hexc("fff0b8"))
    girl(c, 260, 1215, 1.5, hat=True, pack=True, look=0.3, mouth="flat", key="sl")
    ghost(c, 820, 1215, 1.45, "sgh", a=0.9)


# 第 16 句：那四个月
def room(c, t, lamp=1.0):
    fill_all(c, hexc("4a4048"))
    with keep():
        glow(c, 760, 760, 560, WARM, 0.35 * lamp)
    shape(c, rect(-20, 1240, W + 40, 700), hexc("5a4a42"), "rfl", lw=3)


def h16(c, t):
    k = min(int(t / 3.0), 7)
    u = t - k * 3.0
    if k == 0:                                                     # 线松了；拿起纸杯，最后没出声
        lift = 0.55 * math.sin(clamp(prog(u, 0.3, 2.4)) * math.pi)
        window_scene(c, u, girl=lambda: _her_back(c, plane=True, arm_up=lift))
    elif k == 1:                                                   # 什么都只有一份
        room(c, u)
        shape(c, rect(80, 1000, 380, 240), hexc("8a8098"), "bed1", lw=3)
        shape(c, rrect(100, 960, 140, 60, 20), hexc("e8e4f0"), "pil1", lw=2)
        shape(c, rect(640, 1060, 300, 18), WOOD, "tb1", lw=2.4)
        for x in (660, 920):
            line(c, [(x, 1078), (x, 1240)], f"tbl{x}", 6, darker(WOOD, 0.85))
        with keep():
            shape(c, [(770, 1060), (800, 1060), (796, 1020), (774, 1020)], hexc("e8eef4"), "cup1", lw=2)
            line(c, [(1000, 1078), (1000, 1240)], "ch1l", 6, darker(WOOD, 0.85))
            shape(c, rect(950, 1140, 90, 14), WOOD, "ch1", lw=2)
            line(c, [(1032, 1140), (1032, 1000)], "ch1b", 6, darker(WOOD, 0.85))
        girl(c, 520, 1240, 1.55, hat=False, look=math.sin(u * 1.6) * 0.9, mouth="flat", key="rm")
    elif k == 2:                                                   # 多出来的椅子上，放上了背包
        room(c, u)
        shape(c, rect(330, 1050, 420, 18), WOOD, "tb2", lw=2.4)
        for x in (350, 730):
            line(c, [(x, 1068), (x, 1240)], f"t2l{x}", 6, darker(WOOD, 0.85))
        for cx, k2 in ((230, "A"), (850, "B")):
            shape(c, rect(cx - 60, 1140, 120, 16), WOOD, f"c2{k2}", lw=2)
            for sg in (-1, 1):
                line(c, [(cx + sg * 50, 1156), (cx + sg * 50, 1240)], f"c2l{k2}{sg}", 6, darker(WOOD, 0.85))
            bx = cx - 50 if k2 == "A" else cx + 50
            line(c, [(bx, 1140), (bx, 990)], f"c2b{k2}", 7, darker(WOOD, 0.85))
        with keep():
            shape(c, ell(420, 1042, 60, 16, 16, 0, math.pi), (0.97, 0.96, 0.93), "bowl2", lw=2)
        girl(c, 230, 1140, 1.6, sit=True, hat=False, look=0.6, mouth="flat", arms=[(-20, -70), (52, -80)], key="ea")
        drop = ease_out(prog(u, 0.6, 0.6))
        backpack(c, lerp(980, 850, drop), lerp(1240, 1140, drop) - math.sin(drop * math.pi) * 60, 1.0, "bp2")
    elif k == 3:                                                   # 窗外，灰色的人影两个两个地走过
        vgrad(c, 0, 1920, [(0, hexc("2a3048")), (1, hexc("3a4058"))])
        shape(c, rect(-20, 700, W + 40, 1300), hexc("4a4e5a"), "road", lw=2)
        with keep():
            for j in range(8):
                line(c, [(j * 150, 1060), (j * 150 + 80, 1060)], f"lane{j}", 4, hexc("8a8e98"), alpha=0.6)
        for j in range(3):
            x = (j * 420 + u * 120 * (1 if j % 2 else -1)) % 1400 - 160
            y = 920 + j * 140
            for i in range(2):
                silhouette(c, x + i * 46, y, 1.0, f"pr{j}{i}", walk=u * 6 + i + j, a=0.85)
            with keep():
                shape(c, ell(x + 23, y - 190, 90, 40, 20, math.pi, 2 * math.pi), hexc("5a6a7a"), f"umb{j}", lw=2)
                line(c, [(x + 23, y - 190), (x + 23, y - 120)], f"umbh{j}", 2.4, hexc("3a3a3a"))
        rs = random.Random(3)
        with keep():
            for j in range(60):
                y = (rs.uniform(0, 1700) + u * 900) % 1700
                x = rs.uniform(0, W)
                line(c, [(x, y), (x - 4, y + 24)], f"rr{j}", 1.4, hexc("b8c8dc"), alpha=0.45)
    elif k == 4:                                                   # 回忆：很冷的夜里，ta 递过来一杯热饮
        with grade(warm=0.35):
            vgrad(c, 0, 1250, [(0, hexc("1a1e34")), (1, hexc("3a3a58"))])
            shape(c, rect(-20, 1240, W + 40, 700), hexc("3a3440"), "mfl", lw=3)
            shape(c, rect(260, 380, 560, 860), hexc("6a6070"), "mdoorw", lw=3)
            with keep():
                shape(c, rect(380, 640, 320, 600), WARM, "mdoor", lw=2, alpha=0.8)
                glow(c, 540, 900, 420, WARM, 0.4)
            for x in (300, 780):
                shape(c, rect(x - 24, 380, 48, 860), hexc("8a8090"), f"mcol{x}", lw=2)
            give = ease_io(prog(u, 0.4, 1.0))
            girl(c, 340, 1240, 1.6, hat=True, pack=True, look=0.6, mouth="smile",
                 arms=[(-24, -78), (lerp(24, 50, give), lerp(-78, -120, give))], key="mem")
            ghost(c, 740, 1240, 1.6, "mgh2", arms=[(-30, -70), (lerp(-20, -70, give), -120)])
            cxp = lerp(740 - 30 * 1.6, 340 + 60 * 1.6, give)
            with keep():
                shape(c, [(cxp - 18, 1240 - 132 * 1.6), (cxp + 18, 1240 - 132 * 1.6), (cxp + 14, 1240 - 100 * 1.6),
                          (cxp - 14, 1240 - 100 * 1.6)], hexc("f2e8d8"), "hcup2", lw=2)
                glow(c, cxp, 1240 - 120 * 1.6, 70, WARM, 0.5)
                for j in range(3):
                    ph = (u * 0.8 + j / 3) % 1
                    line(c, [(cxp - 8 + j * 8, 1240 - 140 * 1.6 - ph * 60), (cxp - 4 + j * 8, 1240 - 156 * 1.6 - ph * 60)],
                         f"hst{j}", 2, (1, 1, 1), alpha=0.7 * (1 - ph))
    elif k == 5:                                                   # 她停下来仰头看星空；ta 转身朝酒店的灯走去
        with grade(warm=0.25):
            vgrad(c, -100, 1250, [(0, hexc("0e1430")), (1, hexc("2a3060"))])
            r = random.Random(21)
            with keep():
                for j in range(60):
                    star(c, r.uniform(0, W), r.uniform(0, 900), r.uniform(1.6, 3.6), 0.5 + 0.5 * math.sin(u * 3 + j))
            shape(c, rect(-20, 1240, W + 40, 700), hexc("2a2a38"), "sfl", lw=3)
            with keep():
                shape(c, rect(900, 700, 220, 540), WARM, "hotel", lw=2, alpha=0.85)
                glow(c, 1000, 980, 380, WARM, 0.45)
            up = ease_io(prog(u, 0.2, 0.8))                        # 她停下来，仰头看满天的星星
            girl(c, 360, 1240, 1.6, hat=True, pack=True, look=-0.3, look_up=0.9 * up, mouth="laugh" if up > 0.5 else "o",
                 key="pt")
            walk = ease_in(prog(u, 0.4, 2.6))
            ghost(c, lerp(620, 860, walk), 1240, 1.6, "pgh2", walk=u * 5 if walk > 0 else None, a=0.9 - 0.3 * walk)
    elif k == 6:                                                   # 对面楼：每扇窗里两个人各自低头看手机
        fill_all(c, hexc("1e2234"))
        shape(c, rect(100, 160, 880, 1100), hexc("2e3448"), "obld", lw=3)
        for row in range(4):
            for col in range(3):
                wx, wy = 160 + col * 280, 220 + row * 250
                with keep():
                    shape(c, rect(wx, wy, 220, 180), hexc("e8c88a"), f"ow{row}{col}", lw=2, alpha=0.75)
                for i in range(2):
                    hx = wx + 75 + i * 70
                    silhouette(c, hx, wy + 210, 0.75, f"op{row}{col}{i}", col=hexc("5a5a6a"), a=0.9)
                    with keep():
                        glow(c, hx + 6, wy + 120, 40, COOL, 0.6)
    else:                                                          # 天边一颗很亮的星；看了很久，低下头，把窗帘拉上一半
        pull_ = ease_io(prog(u, 1.4, 1.3))

        def her():
            with keep():
                cw = 380 * pull_
                shape(c, rect(920 - cw, 360, cw, 880), hexc("8a7a9a"), "curt", lw=2.4)
                for j in range(4):
                    fx = 920 - cw + (j + 0.5) * cw / 4
                    line(c, [(fx, 380), (fx + 6, 1220)], f"cf{j}", 1.6, hexc("6a5a7a"), alpha=0.6 * pull_)
            girl(c, 430, 1240, 1.7, view="back", sit=True, legs=False, hat=False,
                 head_down=14 * ease_io(prog(u, 1.0, 0.8)), key="hb")
        window_scene(c, u, star_a=1.0, girl=her)


# ================================================================ 第 17–19 句
def h17(c, t):
    if t < 3.3:                                                    # 时间过去，窗台上落了叶子、积了雪；远处那扇窗灭了
        season = prog(t, 0.0, 2.2)
        off = 1 - ease_io(prog(t, 2.3, 0.5))
        window_scene(c, t, leaves=clamp(season * 2), snow_on=clamp(season * 2 - 1), snowfall=clamp(season * 2 - 1),
                     girl=lambda: _her_back(c), far_on=off, mode="night" if season < 0.5 else "snow")
        return
    if t < 6.4:                                                    # 最后一只纸飞机从黑暗里飞来，落在窗台上
        lt = t - 3.3
        window_scene(c, t, snow_on=1.0, snowfall=1.0, girl=lambda: _her_back(c, plane=lt > 2.2), far_on=0.0, mode="snow")
        fu = 1 - ease_out(prog(lt, 0.2, 1.8))
        if lt < 2.0:
            x, y, sc, rot = fly_pt(fu, lift=120)
            pplane(c, x, y + 20, sc, "last", rot=rot + math.pi)
        elif lt <= 2.2:
            pplane(c, 720, 1222, 0.7, "last")
        return
    lt = t - 6.4                                                   # 打开来，是一张空白的纸；一阵风，纸被吹走了
    window_scene(c, t, snow_on=1.0, snowfall=1.0, gale=0.6, girl=lambda: _her_back(c), far_on=0.0, mode="snow")
    fly = ease_in(prog(lt, 0.9, 2.2))
    x = lerp(560, 980, fly) + math.sin(lt * 5) * 30 * (1 - fly)
    y = lerp(1080, 520, fly) - math.sin(fly * math.pi) * 160
    sc = lerp(1.0, 0.35, fly)
    c.save()
    c.translate(x, y)
    c.rotate(lt * 3 * fly)
    c.scale(sc, sc)
    with keep():
        shape(c, rect(-60, -44, 120, 88), PAPER, "slip", lw=2)
        for j in range(3):
            line(c, [(-60 + j * 40, -44), (-60 + j * 40, 44)], f"crease{j}", 1, hexc("d8d0c0"), alpha=0.6)
    c.restore()


def h18(c, t):
    """风雪大起来，把远处屋顶的灯一盏盏吞掉，只剩她窗口一小块光。"""
    gone = ease_io(prog(t, 0.3, 3.4))
    window_scene(c, t, snow_on=1.0, snowfall=1.0 + gone, gale=0.4 + gone, lights=1.0 - gone, far_on=0.0,
                 girl=lambda: _her_back(c, tilt=0.06), mode="snow")
    veil(c, (0.04, 0.04, 0.08), 0.35 * gone)


def h19(c, t):
    if t < 3.2:
        cabin(c, t, ghost_a=0.0, sky="dusk", mouth="flat")
    elif t < 6.4:
        cabin(c, t, ghost_a=0.7 * ease_io(prog(t, 3.4, 1.6)), sky="dusk", mouth="flat")
    else:
        lt = t - 6.4
        walk = ease_in(prog(lt, 0.4, 2.6))
        cabin(c, t, ghost_a=0.7 * (1 - walk), ghost_x=lerp(730, 1150, walk), ghost_walk=lt * 5, sky="dusk", mouth="flat")


# ================================================================ 5 接受
def spring_branch(c, t):
    with keep():
        line(c, [(940, 380), (860, 430), (780, 470)], "sbr", 4, hexc("6a5040"))
        for j in range(6):
            u = j / 5
            bx, by = lerp(930, 790, u), lerp(386, 466, u)
            sg = 1 if j % 2 else -1
            sway = math.sin(t * 2 + j) * 3
            shape(c, ell(bx + 4, by + sg * 18 + sway, 16, 9, 12), hexc("8fc070"), f"nl{j}", lw=1.2)


def h20(c, t):
    """春天的清晨，她推开窗，拿起 ta 那只纸飞机看了一会儿。"""
    panes = ease_io(prog(t, 0.2, 1.4))
    pick = ease_io(prog(t, 2.6, 1.2))

    def her():
        girl(c, 430, 1240, 1.7, view="back", sit=True, legs=False, hat=True, arms=[(-24, -78), (60, -110)], key="hb")
    window_scene(c, t, mode="morning", panes=panes, girl=her)
    spring_branch(c, t)
    pplane(c, lerp(760, 590, pick), lerp(1222, 1100, pick), 0.7, "pl1", rot=0.15 * math.sin(t * 1.5) * pick)


def h21(c, t):
    """春天的窗口：几只淡淡颜色的纸飞机轻轻飞进来，绕着她转一圈，又飞走了；最后她把 ta 那只举起来对着天。"""
    k = min(int(t / 3.0), 2)
    u = t - k * 3.0
    hold = k == 2
    lift = ease_io(prog(u, 0.2, 0.9)) if hold else 0.0

    def her():
        if hold:
            _her_back(c, plane=True, arm_up=lift, hat=True)
        else:
            girl(c, 430, 1240, 1.7, view="back", sit=True, legs=False, hat=True, look=0.6 * math.sin(u * 1.4),
                 key="hb")
    window_scene(c, t, mode="morning", panes=1.0, girl=her)
    spring_branch(c, t)
    if not hold:
        f = prog(u, 0.1, 2.8)
        if 0 < f < 1:
            a = f * 2 * math.pi
            if k == 0:                                             # 从左边飞进来，绕一圈，往右飞走
                x = lerp(120, 1000, f) + math.sin(a) * 140
                y = 820 - math.sin(f * math.pi) * 120 + math.cos(a) * 90
                col = hexc("8cc4c4")
            else:                                                  # 从右边飞进来，绕一圈，往上飞走
                x = lerp(980, 420, f) - math.sin(a) * 140
                y = lerp(1000, 380, f) + math.cos(a) * 80
                col = hexc("e8a890")
            dx = (lerp(120, 1000, f + 0.01) if k == 0 else lerp(980, 420, f + 0.01)) - (lerp(120, 1000, f) if k == 0 else lerp(980, 420, f))
            rot = 0.0 if k == 0 else math.pi + 0.3
            pplane(c, x, y, 1.0, f"vis{k}", rot=rot + 0.4 * math.sin(a), col=col)


def h22(c, t):
    """她把纸飞机朝春风一送，看它飞远，笑了一下，关上窗。"""
    close = ease_io(prog(t, 4.0, 1.2))
    throw = ease_out(prog(t, 0.6, 3.2))

    def her():
        girl(c, 430, 1240, 1.7, view="back", sit=True, legs=False, hat=True,
             arms=[(-24, -78), (lerp(34, 60, min(1, throw * 3)), lerp(-110, -200, min(1, throw * 3)))], key="hb")
    window_scene(c, t, mode="morning", panes=1 - close, girl=her)
    spring_branch(c, t)
    if t < 0.6:
        pplane(c, 590, 1100, 0.75, "pl1")
    elif throw < 1:
        x = lerp(590, 880, throw)
        y = lerp(1100, 480, throw) - math.sin(throw * math.pi) * 120
        pplane(c, x, y, lerp(0.75, 0.12, throw), "pl1", rot=-0.4 + throw * 0.3)


# ================================================================ 片尾
_STILL = {}


def end_still():
    if "s" not in _STILL:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(170.0)
        with grade(sat=1.0, dark=0.0, warm=0.05):
            h22(cc, 3.6)
        _STILL["s"] = surf
    return _STILL["s"]


def outro(c, t):
    book_outro(c, t, end_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第七章 · 完")

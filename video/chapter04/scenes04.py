"""第四章 · 不敢抵达的地方（第三稿）—— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。

贯穿全章的是一颗她随身带着的种子：想找个地方把它种下，却总种不下去；最后发现它是一颗蒲公英的种子。
画面里不写字，用光、影子和玻璃上的倒影说话。
"""
import math
import os
import random
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("series", "chapter01", "chapter02", "chapter03"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
from draw import *  # noqa: F401,F403,E402
from engine import book_intro, book_outro  # noqa: E402
from scenes_v2 import local  # noqa: E402
from scenes02 import RED  # noqa: E402

SKIN_L = hexc("e8c09a")
WOOD = hexc("8c5a3c")
TURQ = hexc("4fd0d0")
DOME = hexc("2f6fc8")

def boat(c, x, y, s, key, rock=0.0):
    """小木船（船身盖住她的腿）。"""
    c.save()
    c.translate(x, y)
    c.rotate(rock)
    c.scale(s, s)
    with keep():
        shape(c, [(-160, -10), (160, -10), (128, 50), (-128, 50)], hexc("a8754a"), key + "h", lw=3)
        line(c, [(-160, -10), (160, -10)], key + "rim", 8, hexc("6b4a32"))
        for k in range(3):
            line(c, [(-140 + k * 6, 8 + k * 14), (140 - k * 6, 8 + k * 14)], f"{key}pl{k}", 1.6, hexc("7a5236"), alpha=0.6)
    c.restore()


def night_sea(c, t, horizon=820, moon=(780, 300)):
    vgrad(c, 0, horizon, [(0, hexc("141c36")), (1, hexc("2c3c66"))])
    r = random.Random(4)
    with keep():
        for k in range(40):
            star(c, r.uniform(0, W), r.uniform(0, horizon * 0.8), r.uniform(1.5, 3.5), 0.5 + 0.5 * math.sin(t * 2 + k))
        glow(c, moon[0], moon[1], 260, hexc("fff3c8"), 0.35)
        circle(c, moon[0], moon[1], 70, hexc("fdf3d6"))
    vgrad(c, horizon, 1920, [(0, hexc("2b4470")), (1, hexc("16223e"))])
    with keep():                                                   # 月光铺在海上
        rr = random.Random(6)
        for k in range(22):
            y = horizon + 14 + k * k * 2.6
            spread = 20 + k * 9
            for j in range(2):
                cx = moon[0] + rr.uniform(-spread, spread) + math.sin(t * 1.6 + k * 1.7 + j) * 14
                w_ = rr.uniform(12, 30) + k * 2
                line(c, [(cx - w_ / 2, y), (cx + w_ / 2, y)], f"mp{k}{j}", 2.6, hexc("fdf3d6"), alpha=0.5 - k * 0.018)


def view_snow(c, x, y, w, h, t):
    vgrad(c, y, y + h, [(0, hexc("b9cde0")), (1, hexc("eef2f6"))], x, x + w)
    for k in range(3):
        mountain(c, x + 60 + k * 120, y + h, 200, 160 + k * 20, hexc("9fb0c4"), f"vs{k}")


def view_sea(c, x, y, w, h, t):
    vgrad(c, y, y + h * 0.55, [(0, hexc("9fd0ec")), (1, hexc("e6f3f8"))], x, x + w)
    shape(c, rect(x, y + h * 0.55, w, h * 0.45), hexc("4f8fb8"), "vsea", lw=1.6)
    with keep():
        circle(c, x + w * 0.7, y + h * 0.3, 26, hexc("fff0b0"))


def view_city(c, x, y, w, h, t):
    fill_all_rect(c, x, y, w, h, hexc("2a2c4a"))
    r = random.Random(5)
    xx = x
    while xx < x + w:
        bw, bh = r.uniform(40, 70), r.uniform(80, h * 0.85)
        shape(c, rect(xx, y + h - bh, bw, bh), hexc("3d4066"), f"vc{int(xx)}", lw=1.4)
        with keep():
            for j in range(int(bh / 26)):
                if r.random() < 0.5:
                    shape(c, rect(xx + 8, y + h - bh + 10 + j * 26, 10, 12), hexc(r.choice(["ff7aa8", "7ae0ff", "ffd96a"])),
                          f"vcw{int(xx)}{j}", lw=0.6, amp=0.2)
        xx += bw + 6


def view_desert(c, x, y, w, h, t):
    vgrad(c, y, y + h, [(0, hexc("f2c79a")), (1, hexc("fbe6c4"))], x, x + w)
    shape(c, hill_pts(y + h * 0.7, 30, 0.02, 1.0, x, x + w, y + h), hexc("e8b46a"), "vd", lw=1.6)
    with keep():
        circle(c, x + w * 0.3, y + h * 0.35, 30, hexc("fff0b0"))


def fill_all_rect(c, x, y, w, h, col):
    c.save()
    c.rectangle(x, y, w, h)
    c.set_source_rgb(*G(col)[:3])
    c.fill()
    c.restore()


ROOMS = [(view_snow, "d9cfc0", "c9d6e3"), (view_sea, "cfe0d8", "f2d0c8"), (view_city, "b9b2c8", "8fa0c4"),
         (view_desert, "ecd8b8", "e8c08a")]


def lying_girl(c, x, y, s, key, **kw):
    """躺着：把站着的小人转 90°，头朝左。"""
    c.save()
    c.translate(x, y)
    c.rotate(-math.pi / 2)
    girl(c, 0, 0, s, key=key, arms=[(-24, -78), (24, -78)], **kw)
    c.restore()


def room(c, t, i):
    view, wall, sheet = ROOMS[i % 4]
    fill_all(c, hexc(wall))
    for k in range(12):                                            # 墙纸的竖条纹
        line(c, [(k * 100, 0), (k * 100, 1000)], f"wp{i}{k}", 1.4, darker(hexc(wall), 0.9), alpha=0.5)
    wx, wy, ww, wh = 330, 200, 420, 360
    c.save()
    c.rectangle(wx, wy, ww, wh)
    c.clip()
    view(c, wx, wy, ww, wh, t)
    c.restore()
    shape(c, rect(wx, wy, ww, wh), None, f"win{i}", lw=5)
    line(c, [(wx + ww / 2, wy), (wx + ww / 2, wy + wh)], f"winm{i}", 5, WOOD)
    shape(c, rect(-20, 1000, W + 40, 900), darker(hexc(wall), 0.75), f"fl{i}", lw=3)
    # 床
    shape(c, rect(150, 860, 60, 300), WOOD, f"bh{i}", lw=3)
    shape(c, rect(180, 960, 760, 120), hexc("f4f0e6"), f"bed{i}", lw=3)
    shape(c, rrect(200, 900, 160, 70, 26), (1, 1, 1), f"pil{i}", lw=2)
    lying_girl(c, 560, 950, 1.5, key="g1", hat=False, mouth="flat", look=0.0, look_up=0.0)
    shape(c, [(360, 950), (900, 950), (930, 1040), (330, 1040)], hexc(sheet), f"blk{i}", lw=2.4)   # 被子
    shape(c, rect(180, 1080, 760, 40), darker(hexc(sheet), 0.85), f"bskirt{i}", lw=2)


def e01(c, t):
    """同一个机位：她躺在不同旅馆的床上，窗外和墙纸一次次换掉，只有她的姿势没变；最后床变成一只小船。"""
    if t < 9.2:
        k = int(t / 2.3)
        room(c, t, k)
        f = prog(t - k * 2.3, 2.1, 0.2)                            # 换房间时一闪
        if f > 0:
            veil(c, hexc("fbf6e8"), 0.6 * math.sin(f * math.pi))
        return
    lt = t - 9.2                                                   # 床 → 小船；她坐起来（和下一幕同一个构图）
    night_sea(c, t)
    rock = math.sin(t * 1.4) * 0.03
    boat(c, 540, 1080, 1.3, "b2", rock)
    sit = ease_io(prog(lt, 0.9, 0.7))
    if sit < 1:
        with group_alpha(c, 1 - sit):
            lying_girl(c, 600, 1050, 1.3, key="g1b", hat=False, mouth="flat")
    if sit > 0:
        with group_alpha(c, sit):
            girl(c, 520, 1060, 1.3, sit=True, legs=False, hat=True, look=0.0, head_down=8, mouth="flat",
                 arms=[(-24, -78), (24, -78)], key="g2")
    boat_front(c, 540, 1080, 1.3, "b2", rock)
    a = 1 - ease_io(prog(lt, 0.0, 1.0))
    if a > 0:
        with group_alpha(c, a):
            room(c, t, 3)


def boat_front(c, x, y, s, key, rock=0.0):
    """船舷（画在人前面，挡住下半身）。"""
    c.save()
    c.translate(x, y)
    c.rotate(rock)
    c.scale(s, s)
    with keep():
        shape(c, [(-160, -24), (160, -24), (128, 50), (-128, 50)], hexc("a8754a"), key + "hf", lw=3)
        line(c, [(-160, -24), (160, -24)], key + "rimf", 8, hexc("6b4a32"))
    c.restore()


def isle_city(c, x, base, t):
    shape(c, ell(x, base, 260, 40, 24), hexc("3d4a3a"), "ic_g", lw=2.4)
    r = random.Random(7)
    for k in range(7):
        bw, bh = 50, r.uniform(120, 300)
        bx = x - 190 + k * 56
        shape(c, rect(bx, base - bh, bw, bh), hexc("3d4066"), f"ic{k}", lw=2)
        with keep():
            for j in range(int(bh / 30)):
                for i in range(2):
                    if r.random() < 0.7:
                        shape(c, rect(bx + 8 + i * 20, base - bh + 12 + j * 30, 12, 14), hexc("ffd96a"), f"icw{k}{j}{i}",
                              lw=0.6, amp=0.2)
    with keep():
        glow(c, x, base - 150, 300, hexc("ffd98a"), 0.3)


def isle_cabin(c, x, base, t):
    shape(c, ell(x, base, 240, 40, 24), hexc("4f6a3a"), "icb_g", lw=2.4)
    house(c, x - 80, base, 170, 140, hexc("c9a46a"), hexc("8b4a3a"), "cab", "tri", lit=2)
    for k in range(5):                                             # 冒炊烟
        ph = (t * 0.5 + k / 5) % 1
        shape(c, ell(x - 10 + math.sin(t + k) * 10, base - 260 - ph * 160, 18 + ph * 26, 12 + ph * 14, 12), (1, 1, 1),
              f"cbs{k}", lw=0.8, alpha=0.6 * (1 - ph))
    line(c, [(x + 100, base - 120), (x + 220, base - 110)], "cbl", 2, hexc("6a6560"))
    with keep():
        for k, col in enumerate(("f2a6a0", "9fc5e8", "f7e27a")):
            shape(c, rect(x + 110 + k * 36, base - 118, 26, 34), hexc(col), f"cbc{k}", lw=1.2)
        for k in range(4):                                         # 菜地
            line(c, [(x - 200 + k * 30, base - 6), (x - 190 + k * 30, base - 30)], f"veg{k}", 3, hexc("6fa860"))


def isle_pier(c, x, base, t, fog):
    shape(c, ell(x + 60, base, 200, 36, 24), hexc("4f6a3a"), "ip_g", lw=2.4)
    shape(c, rect(x - 260, base - 20, 280, 20), WOOD, "pier", lw=2.4)
    for k in range(5):
        line(c, [(x - 250 + k * 64, base), (x - 250 + k * 64, base + 50)], f"pp{k}", 4, WOOD)
    wave = math.sin(t * 6) * 30
    local(c, x - 30, base - 20, 1.1, "pierman", hexc("6b7a8a"), hexc("2f2a28"), "short", view="back",
          arms=[(-24, -78), (40 + wave * 0.3, -200 + wave)])
    if fog > 0:
        with keep():
            for k in range(6):
                shape(c, ell(x - 120 + k * 60, base - 120 - (k % 2) * 40, 160, 70, 16), (0.92, 0.94, 0.97), f"fog{k}",
                      lw=0, edge=False, alpha=0.75 * fog)


def dawn_sea(c, t, u):
    """月夜 → 天亮。"""
    sky_top = mix(hexc("141c36"), hexc("8fb8e0"), u)
    sky_low = mix(hexc("2c3c66"), hexc("f6c9a0"), u)
    vgrad(c, 0, 820, [(0, sky_top), (1, sky_low)])
    with keep():
        if u > 0:
            glow(c, 300, 820, 420, hexc("ffd9a0"), 0.6 * u)
            circle(c, 300, 820 - 60 * u, 60, hexc("fff0c8"))
    vgrad(c, 820, 1920, [(0, mix(hexc("2b4470"), hexc("6f9ac0"), u)), (1, mix(hexc("16223e"), hexc("3f6890"), u))])


def poster_snow(c, x, y, w, h, t):
    vgrad(c, y, y + h, [(0, hexc("9fc0e0")), (1, hexc("eef2f8"))], x, x + w)
    for k in range(3):
        mountain(c, x + w * (0.2 + 0.3 * k), y + h * 0.85, w * 0.5, h * (0.45 + 0.1 * (k % 2)), hexc("8fa6c0"), f"ps{k}")
    shape(c, rect(x, y + h * 0.85, w, h * 0.15), (0.97, 0.98, 1), "psg", lw=1.4)


def poster_desert(c, x, y, w, h, t):
    vgrad(c, y, y + h, [(0, hexc("f2b27a")), (1, hexc("fbe6c4"))], x, x + w)
    with keep():
        circle(c, x + w * 0.65, y + h * 0.3, w * 0.12, hexc("fff0b0"))
    shape(c, hill_pts(y + h * 0.7, h * 0.06, 0.02, 2.0, x, x + w, y + h), hexc("e8a050"), "pd", lw=1.6)


def poster_town(c, x, y, w, h, t):
    vgrad(c, y, y + h, [(0, hexc("bfe0f2")), (1, hexc("f6efe0"))], x, x + w)
    for k in range(4):
        house(c, x + 10 + k * w / 4, y + h * 0.85, w / 4 - 8, h * (0.3 + 0.08 * (k % 2)),
              hexc(["e98f6f", "f3e3c3", "8fc0b5", "f1c27d"][k]), hexc(["8b4a3a", "3c6ea5", "3f6f73", "b4533f"][k]), f"pt{k}",
              "tri" if k % 2 else "flat")
    shape(c, rect(x, y + h * 0.85, w, h * 0.15), hexc("d9c8a8"), "ptg", lw=1.4)


def poster_jungle(c, x, y, w, h, t):
    vgrad(c, y, y + h, [(0, hexc("bfe0b0")), (1, hexc("e8f2d8"))], x, x + w)
    for k in range(4):
        tree(c, x + 20 + k * w / 3.5, y + h * 0.9, 1.0, f"pj{k}", col=hexc("4f8a4a"))
    shape(c, rect(x, y + h * 0.88, w, h * 0.12), hexc("6f9a50"), "pjg", lw=1.4)


X0, X1, Y0, Y1 = -500, W + 500, -600, 2800                    # 画得比画面大，镜头拉远时不露边


def zoom_into(c, t, rect_, fn, t0, d, reverse=False):
    """镜头穿过玻璃，从海报的框推进到满屏（reverse：从满屏退回框里）。"""
    x, y, w, h = rect_
    e = ease_io(prog(t, t0, d))
    if reverse:
        e = 1 - e
    sf = w / W
    z = lerp(1.0, 1.0 / sf, e)
    ox, oy = lerp(0, x, e), lerp(0, y, e)
    c.save()
    c.scale(z, z)
    c.translate(-ox, -oy)
    fn(c)
    c.restore()


# ================================================================ 种子
def seed(c, x, y, s, key, open_=0.0, glow_a=0.6, rot=0.0):
    """一颗小种子；open_ → 1 时张开一圈白色的蒲公英绒毛。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    with keep():
        if glow_a > 0:
            glow(c, 0, -10 - 30 * open_, 70 + 40 * open_, hexc("fff3c8"), glow_a)
        shape(c, ell(0, 0, 7, 12, 12), hexc("a8754a"), key + "b", lw=1.6, amp=0.3)
        if open_ > 0:
            stalk = 40 * open_
            line(c, [(0, -10), (0, -10 - stalk)], key + "st", 1.6, hexc("efe8d8"))
            n = 18
            for k in range(n):
                a = math.pi * (1.1 + 0.8 * k / (n - 1))
                ln = 34 * open_
                ex, ey = math.cos(a) * ln, -10 - stalk + math.sin(a) * ln
                line(c, [(0, -10 - stalk), (ex, ey)], f"{key}f{k}", 1.2, (1, 1, 1), alpha=0.9)
                circle(c, ex, ey, 2.2, (1, 1, 1), a=0.9)
    c.restore()


def seed_illus(c, cx, cy):
    seed(c, cx, cy + 40, 1.4, "ill", open_=1.0, glow_a=0.0)


def intro(c, t):
    book_intro(c, t, "第四章", "不敢抵达的地方", seed_illus)


# ================================================================ 2 手心里的种子
def e02(c, t):
    """小船漂在月光的海上。她摊开手心，一颗小小的种子微微发亮；四周全是水，没有一处可以把它放下。"""
    k = lerp(1.0, 1.6, ease_io(prog(t, 0.0, 8.0)))
    with cam(c, 540, 960, k):
        night_sea(c, t)
        rock = math.sin(t * 1.4) * 0.03
        boat(c, 540, 1080, 1.3, "b2", rock)
        openh = ease_io(prog(t, 0.6, 1.0))
        look = 0.0 if t < 2.6 else math.sin((t - 2.6) * 1.3) * 0.9
        girl(c, 520, 1060, 1.3, sit=True, legs=False, hat=True, look=look, head_down=8 if t < 2.6 else 2, mouth="flat",
             arms=[(-24, -78), (lerp(24, 54, openh), lerp(-78, -112, openh))], key="g2")
        boat_front(c, 540, 1080, 1.3, "b2", rock)
        if openh > 0:
            seed(c, 520 + 54 * 1.3, 1060 - 112 * 1.3 - 14, 1.1, "s2", glow_a=0.8 * openh)


# ================================================================ 3 三座小岛
def e03(c, t):
    """小船漂过三座小岛：每一座她都捧着种子往前伸一伸，又收回来。"""
    night_sea(c, t, moon=(860, 220))
    i = min(int(t / 3.33), 2)
    u = t - i * 3.33
    x = 540 + (1.665 - u) * 420
    base = 820
    if i == 0:
        isle_city(c, x, base, t)
    elif i == 1:
        isle_cabin(c, x, base, t)
    else:
        isle_pier(c, x, base, t, fog=ease_io(prog(u, 1.8, 1.2)))
    reach = math.sin(clamp((u - 0.6) / 2.0) * math.pi)
    rock = math.sin(t * 1.4) * 0.03
    boat(c, 520, 1150, 1.3, "b3", rock)
    hx, hy = lerp(50, 70, reach), lerp(-110, -190, reach)
    girl(c, 500, 1130, 1.3, sit=True, legs=False, hat=True, look=0.6, look_up=0.3 * reach, mouth="flat",
         arms=[(-24, -78), (hx, hy)], key="g3")
    boat_front(c, 520, 1150, 1.3, "b3", rock)
    seed(c, 500 + hx * 1.3, 1130 + hy * 1.3 - 14, 1.0, "s3", glow_a=0.7)


# ================================================================ 4 埋进沙里
def beach(c, t, wave_in=0.0, dawn=0.0):
    sky_a = mix(hexc("1e2a4c"), hexc("8fb8e0"), dawn)
    sky_b = mix(hexc("44587e"), hexc("f6c9a0"), dawn)
    vgrad(c, 0, 560, [(0, sky_a), (1, sky_b)])
    with keep():
        if dawn < 0.8:
            circle(c, 820, 200, 56, hexc("fdf3d6"))
            glow(c, 820, 200, 220, hexc("fff3c8"), 0.3 * (1 - dawn))
        if dawn > 0:
            glow(c, 300, 560, 380, hexc("ffd9a0"), 0.6 * dawn)
    shape(c, rect(-20, 560, W + 40, 300), mix(hexc("2b4470"), hexc("6f9ac0"), dawn), "bsea", lw=2)
    vgrad(c, 760, 1920, [(0, mix(hexc("cdbb98"), hexc("e8d4b0"), dawn)), (1, mix(hexc("a8977a"), hexc("cdb898"), dawn))])
    boat(c, 150, 840, 0.9, "b4", -0.08)
    boat_front(c, 150, 840, 0.9, "b4", -0.08)
    edge = 760 + wave_in * 440
    pts = [(-20, 740)] + [(x, edge + 14 * math.sin(x * 0.02 + t * 3)) for x in range(-20, W + 60, 60)] + [(W + 40, 740)]
    return pts, edge


def draw_wave(c, t, pts, edge):
    shape(c, pts, hexc("e8f2f6") + (0.85,), "wave", lw=2.4)
    for k in range(3):
        line(c, [(x, edge - 20 - k * 30 + 8 * math.sin(x * 0.03 + t * 2 + k)) for x in range(-20, W + 60, 60)],
             f"foam{k}", 2, (1, 1, 1), alpha=0.6)


def e04(c, t):
    """她跪下来把种子埋进沙里，轻轻拍平，抱着膝盖坐在旁边笑了；一个浪漫上来又退下去，沙子被抹得平平的。"""
    w_in = ease_io(prog(t, 3.6, 0.8)) * (1 - ease_io(prog(t, 4.6, 1.2)))
    pts, edge = beach(c, t, w_in)
    mound = 1.0 - ease_io(prog(t, 3.9, 0.5))
    if mound > 0 and t > 0.6:                                      # 小沙包
        with keep():
            shape(c, ell(420, 1160, 80 * mound, 30 * mound, 16, math.pi, 2 * math.pi), hexc("bca888"), "mound", lw=1.8)
            glow(c, 420, 1150, 60, hexc("fff3c8"), 0.25 * mound)
    if t < 0.8:
        seed(c, 430, 1110, 1.1, "s4", glow_a=0.7)
    pat = t < 1.8
    if pat:                                                        # 跪着拍
        ph = abs(math.sin(t * 8))
        girl(c, 520, 1180, 1.6, sit=True, crouch=True, hat=True, look=-0.6, head_down=12, mouth="smile",
             arms=[(-60, -40 - 20 * ph), (-30, -50)], key="g4")
    else:                                                          # 抱着膝盖坐着
        girl(c, 540, 1180, 1.6, sit=True, crouch=True, hat=True, look=-0.4, mouth="laugh" if t < 3.6 else "o",
             arms=[(-16, -30), (16, -30)], key="g4")
    draw_wave(c, t, pts, edge)


# ================================================================ 5 原来是一颗蒲公英
def e05(c, t):
    if t < 3.4:                                                    # 退下去的浪花里，种子浮出来
        w_in = 0.35 * (1 - ease_io(prog(t, 0.0, 1.6)))
        pts, edge = beach(c, t, w_in)
        sx = lerp(420, 470, ease_io(prog(t, 1.6, 1.2)))
        sy = lerp(1140, 1060, ease_io(prog(t, 1.6, 1.2)))
        bob = math.sin(t * 3) * 6 * (t < 1.6)
        draw_wave(c, t, pts, edge)
        reach = ease_io(prog(t, 1.0, 0.8))
        girl(c, 560, 1180, 1.6, sit=True, crouch=True, hat=True, look=-0.6, head_down=10, mouth="o",
             arms=[(-24, -30), (lerp(-16, -60, reach), lerp(-30, -70, reach))], key="g5")
        seed(c, sx, sy + bob, 0.8, "s5", glow_a=0.6)
        return
    lt = t - 3.4                                                   # 手心里张开绒毛 → 风把它带走，飞进晨光
    dawn = ease_io(prog(lt, 1.0, 5.0))
    beach(c, t, 0.0, dawn)
    fly = ease_in(prog(lt, 3.8, 3.6))
    up = 0.5 * ease_io(prog(lt, 3.6, 1.2))
    girl(c, 560, 1200, 1.9, sit=True, crouch=True, hat=True, look=0.0, look_up=up, mouth="o" if lt < 3.6 else "smile",
         arms=[(-24, -40), (50, -110)] if fly < 0.05 else [(-16, -30), (16, -30)], key="g5b")
    opn = ease_io(prog(lt, 0.6, 2.2))
    sx = 560 + 50 * 1.9 + fly * 260 + math.sin(lt * 2.4) * 40 * fly
    sy = 1200 + (-110 + 52) * 1.9 - 20 - fly * 1000
    seed(c, sx, sy, 1.3 - 0.4 * fly, "s5b", open_=opn, glow_a=0.5, rot=math.sin(lt * 2) * 0.25 * fly)
    if fly > 0:
        with keep():
            for k in range(4):                                     # 风
                yy = 420 + k * 130
                xx = (lt * 600 + k * 260) % 1400 - 200
                line(c, [(xx, yy), (xx + 120, yy - 10), (xx + 200, yy + 6)], f"wind{k}", 2.4, (1, 1, 1), alpha=0.5)


# ================================================================ 海岛：一笔一笔画出来的白房子
BOUG = hexc("e0559a")                                              # 三角梅


def bougainvillea(c, x, y, r, key, warm=0.0):
    rr = random.Random(hash(key) & 0xffff)
    with keep():
        for k in range(22):
            a = rr.uniform(0, 2 * math.pi)
            d = rr.uniform(0, r)
            shape(c, ell(x + math.cos(a) * d, y + math.sin(a) * d * 0.7, rr.uniform(8, 14), rr.uniform(7, 11), 8),
                  mix(BOUG, hexc("f08a5a"), warm * 0.4), f"{key}{k}", lw=0.8, amp=0.3)
        for k in range(5):
            a = rr.uniform(0, 2 * math.pi)
            shape(c, ell(x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.5, 9, 5, 8), hexc("4f8a4a"), f"{key}l{k}",
                  lw=0.8, amp=0.3)


def cyc_house(c, x, base, w, h, key, warm=0.0, door=None, win=1, dome=False, balcony=False, flowers=None,
              arch=False, chimney=False):
    """一间基克拉泽斯式的白房子：圆角的白墙、右侧一点阴影、蓝色的门和百叶窗。"""
    white = mix(hexc("fbfaf6"), hexc("ffe2c0"), warm)
    shade = mix(hexc("dde4ec"), hexc("e8b48a"), warm)
    blue = mix(DOME, hexc("3a5aa8"), warm * 0.3)
    shape(c, rrect(x, base - h, w, h, 10), white, key + "w", lw=2.2, amp=0.6)
    shape(c, rrect(x + w - 16, base - h + 4, 14, h - 6, 6), shade, key + "sh", lw=0, edge=False, amp=0.4)
    line(c, [(x - 4, base - h), (x + w + 4, base - h)], key + "roof", 4, white)
    if chimney:
        shape(c, rrect(x + w * 0.7, base - h - 26, 22, 30, 6), white, key + "ch", lw=1.8)
    with keep():
        if door is not None:                                       # 蓝门 + 门框
            dx = x + w * door
            if arch:
                shape(c, rect(dx - 18, base - 56, 36, 56) + [], blue, key + "d", lw=1.8)
                shape(c, ell(dx, base - 56, 18, 16, 12, math.pi, 2 * math.pi), blue, key + "da", lw=1.8)
            else:
                shape(c, rect(dx - 17, base - 66, 34, 66), blue, key + "d", lw=1.8)
            line(c, [(dx - 21, base - 70), (dx + 21, base - 70)], key + "dl", 2.4, shade)
            circle(c, dx + 9, base - 34, 2.4, hexc("e8c040"))
        for k in range(win):                                       # 窗 + 两扇蓝色百叶
            wx = x + w * (0.22 + 0.5 * k) if win > 1 else x + w * (0.3 if door and door > 0.5 else 0.7)
            wy = base - h * 0.62
            shape(c, rect(wx - 12, wy - 16, 24, 30), hexc("2a3a5a"), f"{key}win{k}", lw=1.4)
            shape(c, rect(wx - 22, wy - 16, 10, 30), blue, f"{key}shl{k}", lw=1.2)
            shape(c, rect(wx + 12, wy - 16, 10, 30), blue, f"{key}shr{k}", lw=1.2)
    if balcony:                                                    # 屋顶的小露台栏杆
        for k in range(int(w / 18)):
            line(c, [(x + 6 + k * 18, base - h), (x + 6 + k * 18, base - h - 20)], f"{key}bal{k}", 2, white)
        line(c, [(x + 4, base - h - 20), (x + w - 4, base - h - 20)], key + "balt", 3, white)
    if dome:                                                       # 蓝圆顶 + 白色小十字
        cx = x + w / 2
        shape(c, rect(cx - w * 0.32, base - h - 18, w * 0.64, 20), white, key + "drum", lw=1.8)
        shape(c, ell(cx, base - h - 18, w * 0.34, w * 0.34, 20, math.pi, 2 * math.pi), blue, key + "dome", lw=2)
        line(c, [(cx, base - h - 18 - w * 0.34), (cx, base - h - 18 - w * 0.34 - 26)], key + "cr", 3, white)
        line(c, [(cx - 9, base - h - 18 - w * 0.34 - 16), (cx + 9, base - h - 18 - w * 0.34 - 16)], key + "crh", 3, white)
    if flowers:
        fx, fy, fr = flowers
        bougainvillea(c, x + w * fx, base - h * fy, fr, key + "bg", warm)


def bell_tower(c, x, base, key, warm=0.0):
    """白色的小钟楼：两层拱，挂着一口钟。"""
    white = mix(hexc("fbfaf6"), hexc("ffe2c0"), warm)
    shape(c, rrect(x - 50, base - 150, 100, 150, 8), white, key + "t", lw=2.2)
    with keep():
        for k, (cx, cy) in enumerate(((x - 22, base - 110), (x + 22, base - 110))):
            shape(c, rect(cx - 12, cy, 24, 44), hexc("2a3a5a"), f"{key}ar{k}", lw=1.4)
            shape(c, ell(cx, cy, 12, 12, 12, math.pi, 2 * math.pi), hexc("2a3a5a"), f"{key}arr{k}", lw=1.4)
            shape(c, ell(cx, cy + 22, 7, 9, 10), hexc("c9a04a"), f"{key}bell{k}", lw=1.2)
    shape(c, [(x - 34, base - 150), (x + 34, base - 150), (x + 34, base - 186), (x, base - 210), (x - 34, base - 186)],
          white, key + "top", lw=2)
    line(c, [(x, base - 210), (x, base - 236)], key + "cr", 3, white)
    line(c, [(x - 9, base - 226), (x + 9, base - 226)], key + "crh", 3, white)


CLIFF = [  # x, base, w, h, door, win, dome, balcony, flowers, arch, chimney
    (-60, 420, 170, 110, 0.7, 1, False, True, None, False, True),
    (120, 440, 130, 130, None, 2, True, False, None, False, False),
    (260, 470, 150, 100, 0.3, 1, False, True, (0.9, 0.3, 40), False, False),
    (-90, 560, 210, 120, 0.5, 2, False, False, None, True, False),
    (130, 590, 160, 130, 0.65, 1, False, True, (0.1, 0.4, 46), False, True),
    (300, 620, 140, 110, None, 1, True, False, None, False, False),
    (-40, 730, 180, 120, 0.3, 1, False, True, (0.95, 0.5, 50), True, False),
    (150, 760, 220, 140, 0.8, 2, False, False, None, False, True),
    (380, 790, 140, 100, 0.5, 0, False, True, None, True, False),
]


def caldera(c, t, sun=0.0, warm=0.0, night=0.0, tower=True):
    """悬崖上一层层的白房子，右边是大海；天空占了大半个画面。"""
    sky_a = mix(mix(hexc("5fb0f0"), hexc("e8885a"), warm), hexc("0f1630"), night)
    sky_b = mix(mix(hexc("cfeafc"), hexc("ffd9a0"), warm), hexc("2a3a6a"), night)
    vgrad(c, Y0, 860, [(0, sky_a), (1, sky_b)], X0, X1)
    if night > 0.5:
        r = random.Random(12)
        with keep():
            for k in range(80):
                star(c, r.uniform(X0, X1), r.uniform(Y0, 800), r.uniform(1.5, 3.2), 0.6 + 0.4 * math.sin(t * 1.5 + k))
    if sun > 0:
        with keep():
            glow(c, 760, 800, 560 * sun, hexc("ffb060"), 0.55 * min(1.0, warm + 0.3))
            circle(c, 760, 800, 110 * sun, mix(hexc("fff3c0"), hexc("ffc060"), warm))
    vgrad(c, 860, 1400, [(0, mix(mix(hexc("2f8fd8"), hexc("d8805a"), warm), hexc("10203a"), night)),
                         (1, mix(mix(hexc("1f6fb0"), hexc("9a5a5a"), warm), hexc("0a1428"), night))], X0, X1)
    with keep():
        for k in range(9):                                         # 海面上的光
            y = 880 + k * k * 6
            w_ = 40 + k * 24
            off = math.sin(t * 1.5 + k * 1.3) * 16
            line(c, [(760 - w_ / 2 + off, y), (760 + w_ / 2 + off, y)], f"cal{k}", 3,
                 mix(hexc("e6f4fc"), hexc("ffe0a0"), warm), alpha=(0.6 - k * 0.05) * (1 - night))
    rock = mix(mix(hexc("b89a78"), hexc("b8805a"), warm), hexc("3a3046"), night)
    shape(c, [(X0, 300), (-80, 330), (200, 400), (420, 560), (560, 780), (600, 900), (640, 1000), (X0, 1000)], rock,
          "cliff", lw=3)
    with group_alpha(c, 1 - 0.5 * night):
        for i, (x, base, w, h, door, win, dome, bal, fl, arch, ch) in enumerate(CLIFF):
            cyc_house(c, x, base, w, h, f"cy{i}", warm, door, win, dome, bal, fl, arch, ch)
        if tower:
            bell_tower(c, 480, 660, "bt", warm)
        for k in range(5):                                         # 弯下去的白台阶
            line(c, [(420 + k * 30, 830 + k * 34), (500 + k * 30, 830 + k * 34)], f"stp{k}", 5,
                 mix(hexc("fbfaf6"), hexc("ffe2c0"), warm))


def chapel(c, t, veil_t=None, warm=0.0):
    """悬崖边一座白墙蓝顶的小教堂，大片的天空；一条白纱被风吹过来，飘过蓝顶，飘向海。"""
    vgrad(c, Y0, 1100, [(0, mix(hexc("4f9fe0"), hexc("e8885a"), warm)), (1, mix(hexc("d6eefc"), hexc("ffd9a0"), warm))],
          X0, X1)
    vgrad(c, 1100, 1500, [(0, hexc("2f8fd8")), (1, hexc("1f6fb0"))], X0, X1)
    shape(c, [(X0, 1060), (300, 1040), (760, 1080), (840, 1200), (X0, 1300)], hexc("b89a78"), "chcliff", lw=3)
    white = hexc("fbfaf6")
    shape(c, rrect(260, 760, 420, 300, 12), white, "chw", lw=2.6)
    shape(c, rrect(640, 772, 34, 286, 8), hexc("dde4ec"), "chsh", lw=0, edge=False)
    shape(c, rect(320, 690, 300, 80), white, "chdrum", lw=2.4)
    shape(c, ell(470, 690, 160, 160, 28, math.pi, 2 * math.pi), DOME, "chdome", lw=2.6)
    line(c, [(470, 530), (470, 470)], "chcr", 5, white)
    line(c, [(448, 494), (492, 494)], "chcrh", 5, white)
    with keep():
        shape(c, rect(440, 940, 60, 120), DOME, "chdoor", lw=2)
        shape(c, ell(470, 940, 30, 26, 14, math.pi, 2 * math.pi), DOME, "chdoora", lw=2)
        for k, x in enumerate((340, 580)):
            shape(c, rect(x - 14, 840, 28, 50), hexc("2a3a5a"), f"chwn{k}", lw=1.4)
            shape(c, ell(x, 840, 14, 14, 12, math.pi, 2 * math.pi), hexc("2a3a5a"), f"chwna{k}", lw=1.4)
    bell_tower(c, 760, 1080, "chbt")
    bougainvillea(c, 250, 1000, 70, "chbg")
    if veil_t is not None:                                         # 白纱
        u = veil_t
        x0 = lerp(-300, 1400, u)
        y0 = lerp(900, 380, u) + math.sin(u * 9) * 40
        pts = []
        for k in range(12):
            a = k / 11
            pts.append((x0 - 380 * a, y0 + 70 * math.sin(a * 5 + u * 12) + a * 60))
        for k in range(11, -1, -1):
            a = k / 11
            pts.append((x0 - 380 * a + 10, y0 + 70 * math.sin(a * 5 + u * 12) + a * 60 + 50 - 30 * a))
        with keep():
            shape(c, pts, (1, 1, 1, 0.7), "veil", lw=1.6, amp=0.8)


def villa_dusk(c, t, night=0.0):
    """黄昏，碧绿的浅海上一间水上小木屋，水面漂着一路玫瑰花瓣，一直通到木屋门口。"""
    vgrad(c, Y0, 700, [(0, mix(hexc("e89a6a"), hexc("0f1630"), night)), (1, mix(hexc("ffd9a8"), hexc("2a3a6a"), night))],
          X0, X1)
    if night > 0.5:
        r = random.Random(12)
        with keep():
            for k in range(90):
                star(c, r.uniform(X0, X1), r.uniform(Y0, 660), r.uniform(1.5, 3.2), 0.6 + 0.4 * math.sin(t * 1.5 + k))
    vgrad(c, 700, Y1, [(0, mix(hexc("6fc8c0"), hexc("10203a"), night)), (1, mix(hexc("2fa0a8"), hexc("0a1428"), night))],
          X0, X1)
    # 木屋
    for sg in (-1, 1):
        for k in range(3):
            line(c, [(540 + sg * (60 + k * 40), 760), (540 + sg * (60 + k * 40), 860)], f"vst{sg}{k}", 6, hexc("6b4a32"))
    shape(c, rect(380, 740, 320, 30), WOOD, "vdeck", lw=2.4)
    shape(c, rect(420, 560, 240, 180), hexc("d9b778"), "vwall", lw=2.6)
    shape(c, [(380, 570), (700, 570), (600, 450), (480, 450)], hexc("a8754a"), "vroof", lw=2.6)
    for k in range(9):
        line(c, [(400 + k * 35, 570), (490 + k * 15, 456)], f"vth{k}", 1.4, hexc("8c5a3c"), alpha=0.6)
    lit = 0.6 + 0.4 * night
    with keep():
        shape(c, rect(510, 620, 60, 120), hexc("ffd98a"), "vdoor", lw=2)
        glow(c, 540, 680, 160, hexc("ffd98a"), 0.4 * lit)
        if night > 0.5:                                            # 水里的倒影
            for j in range(6):
                line(c, [(520 + j * 2, 900 + j * 26), (560 - j * 2, 900 + j * 26)], f"vrf{j}", 4, hexc("ffd98a"),
                     alpha=0.5 - j * 0.07)
    # 一路玫瑰花瓣
    r = random.Random(3)
    with keep():
        for k in range(46):
            a = k / 45
            px = lerp(540, 300, a) + math.sin(a * 6) * 60 + r.uniform(-20, 20)
            py = lerp(780, 1500, a) + r.uniform(-14, 14) + math.sin(t * 1.2 + k) * 3
            s = lerp(0.6, 1.4, a)
            shape(c, ell(px, py, 9 * s, 5 * s, 8), hexc("e8506a"), f"vp{k}", lw=0.8, amp=0.3, alpha=1 - night * 0.5)
    with keep():
        for k in range(10):                                        # 水面的波纹
            y = 900 + k * 70
            line(c, [(X0, y), (X1, y + 8)], f"vw{k}", 1.6, (1, 1, 1), alpha=0.2)


# ================================================================ 6–7 橱窗
def poster_art(c, x, y, w, h, t, warm=0.0, couple=True, sun=0.0):
    """最后一张海报：白房子和台阶上，两个人牵着手的背影。"""
    c.save()
    c.rectangle(x, y, w, h)
    c.clip()
    c.translate(x, y)
    sc = w / W
    c.scale(sc, sc)
    c.translate(0, -100)
    caldera(c, t, sun=sun, warm=warm)
    if couple:
        local(c, 250, 1160, 1.6, "pc1", hexc("2f3a4a"), hexc("2f2a28"), "short", view="back",
              arms=[(-24, -78), (30, -84)])
        local(c, 340, 1160, 1.6, "pc2", hexc("fbfaf6"), hexc("5a3a2a"), "bang_long", view="back",
              arms=[(-30, -84), (24, -78)])
        line(c, [(250 + 30 * 1.6, 1160 - 84 * 1.6), (340 - 30 * 1.6, 1160 - 84 * 1.6)], "pchand", 4, SKIN_L)
    c.restore()


def window(c, t, ox, posters=True):
    vgrad(c, 0, 1000, [(0, hexc("cfe4ef")), (1, hexc("f6efe0"))])
    c.save()
    c.translate(-ox, 0)
    shape(c, rect(-200, 120, 2900, 960), hexc("e8d6b8"), "shopw", lw=3)
    with keep():
        shape(c, rect(-100, 150, 2700, 90), hexc("2f6a6a"), "shopsign", lw=2.4)
    shape(c, rect(-60, 280, 2620, 720), hexc("dfeef4"), "glass", lw=4)
    if posters:
        for k, fn in enumerate((poster_snow, poster_desert, poster_town, poster_jungle)):
            px = 60 + k * 480
            with keep():
                shape(c, rect(px - 10, 350, 360, 480), (1, 1, 1), f"pf{k}", lw=2.4)
            c.save()
            c.rectangle(px, 360, 340, 460)
            c.clip()
            fn(c, px, 360, 340, 460, t)
            c.restore()
            shape(c, rect(px, 360, 340, 460), None, f"pb{k}", lw=2)
        with keep():
            shape(c, rect(1988, 318, 444, 584), (1, 1, 1), "ipf", lw=3)
        poster_art(c, 2000, 330, 420, 560, t)
        shape(c, rect(2000, 330, 420, 560), None, "ipb", lw=2.4)
    with keep():
        for k in range(8):
            x = k * 340
            line(c, [(x, 300), (x + 120, 980)], f"refl{k}", 6, (1, 1, 1), alpha=0.3)
    shape(c, rect(-200, 1000, 2900, 900), hexc("c9c2b4"), "walk", lw=3)
    for k in range(20):
        line(c, [(k * 150 - 200, 1000), (k * 150 - 260, 1900)], f"wk{k}", 1.4, hexc("b3ab9c"), alpha=0.5)
    c.restore()


def e06(c, t):
    """蒲公英种子飘过来，停在橱窗上。她走过一张张海报，只轻轻看一眼；走到最后一张前停住了。"""
    walk = ease_io(prog(t, 1.2, 6.0))
    gx = lerp(200, 2210, walk)
    ox = clamp(gx - 540, 0, 1700)
    window(c, t, ox)
    fall = ease_out(prog(t, 0.0, 2.0))
    sx = lerp(980, 2380, fall) - ox if t < 2.0 else 2380 - ox
    sy = lerp(160, 300, fall)
    seed(c, sx + math.sin(t * 3) * 20 * (1 - fall), sy, 0.9, "s6", open_=1.0, glow_a=0.2)
    moving = 0 < walk < 1
    glance = max(0.0, max(1 - abs(gx - (230 + k * 480)) / 140 for k in range(4)))
    girl(c, gx - ox, 1240, 1.6, hat=True, pack=True, look=0.7 - 0.9 * glance if moving else 0.0, look_up=0.3,
         mouth="smile" if walk < 1 else "flat", walk=t * 7 if moving else None, key="g6")


def reflection(c, x, y, s, a, key, others=0.0):
    """玻璃上的倒影：她自己（正面、淡淡的），以及慢慢多出来的模糊身影。"""
    with group_alpha(c, a):
        with grade(sat=0.5):
            if others > 0:
                with group_alpha(c, clamp(others * 2)):
                    local(c, x + 130 * s / 1.6, y, s * 1.05, key + "o1", hexc("6b7a8a"), hexc("3a3a3a"), "short",
                          mouth="smile", look=-0.3)
                if others > 0.5:
                    with group_alpha(c, clamp((others - 0.5) * 2)):
                        for k, (dx, ss, col) in enumerate(((-180, 0.95, "c98d72"), (-90, 0.85, "8fb39a"), (220, 0.9, "7d6a8f"),
                                                           (300, 0.8, "4f8a8a"))):
                            local(c, x + dx * s / 1.6, y - 40, s * ss, f"{key}o{k + 2}", hexc(col), hexc("3a3a3a"), "short",
                                  mouth="laugh", look=0.3 if dx < 0 else -0.3)
            girl(c, x, y, s, hat=True, pack=True, mouth="smile", look=0.0, keep_color=False, key=key + "me")


def glass_scene(c, t, poster_warm=0.0, sun=0.0, refl_a=0.35, others=0.0, me=True):
    """正对着橱窗：海报占满玻璃，她背对着我们站在玻璃前。"""
    vgrad(c, 0, 1920, [(0, hexc("dfeef4")), (1, hexc("cfe4ef"))])
    with keep():
        shape(c, rect(96, 126, 888, 1068), (1, 1, 1), "bigpf", lw=3)
    poster_art(c, 110, 140, 860, 1040, t, warm=poster_warm, sun=sun)
    shape(c, rect(110, 140, 860, 1040), None, "bigpb", lw=2.4)
    c.save()                                                       # 玻璃上的倒影
    c.rectangle(110, 140, 860, 1040)
    c.clip()
    reflection(c, 760, 1150, 1.9, refl_a, "rf", others)
    with keep():
        for k in range(4):
            line(c, [(k * 320 - 60, 100), (k * 320 + 120, 1300)], f"gl{k}", 8, (1, 1, 1), alpha=0.25)
    c.restore()


def e07(c, t):
    """海报：两个人牵手的背影。她伸手想去碰，停在玻璃前；玻璃上映出她自己——只有她一个人；她把手收回来。"""
    glass_scene(c, t, refl_a=lerp(0.0, 0.4, ease_io(prog(t, 1.6, 1.2))))
    reach = math.sin(clamp(prog(t, 0.6, 4.2)) * math.pi)
    girl(c, 820, 1900, 2.8, view="back", hat=True, pack=True,
         arms=[(-24, -78), (lerp(24, 60, reach), lerp(-78, -260, reach))], key="g7")


# ================================================================ 8–11 走进海报
def e08(c, t):
    if t < 1.2:                                                    # 穿过玻璃
        zoom_into(c, t, (110, 140, 860, 1040), lambda cc: e07(cc, 6.0), 0.0, 1.2)
        return
    if t < 5.2:
        chapel(c, t, veil_t=prog(t, 1.4, 3.6))
        return
    villa_dusk(c, t)


def terrace(c, t, sun=0.0, warm=0.0, shadows=False):
    """海岛的露台：面朝大海和落日，两把椅子，桌上两只杯子。"""
    caldera(c, t, sun=sun, warm=warm, tower=False)
    tf = mix(hexc("fbfaf6"), hexc("ffe2c0"), warm)
    rail = mix(hexc("d9d4c8"), hexc("e8b080"), warm)
    shape(c, [(X0, 1060), (X1, 1060), (X1, Y1), (X0, Y1)], tf, "terr", lw=3)
    shape(c, [(X0, 1000), (X1, 1000), (X1, 1060), (X0, 1060)], tf, "parapet", lw=2.4)
    for k, x in enumerate((300, 780)):                             # 两把椅子
        with keep():
            shape(c, rrect(x - 50, 1080, 100, 90, 10), hexc("2f6fc8"), f"chb{k}", lw=2.4)
            shape(c, rect(x - 56, 1160, 112, 18), hexc("f4f0e6"), f"chs{k}", lw=2.4)
            for sg in (-1, 1):
                line(c, [(x + sg * 46, 1178), (x + sg * 46, 1240)], f"chl{k}{sg}", 4, hexc("8c7a62"))


def e09(c, t):
    """露台上两把椅子的影子并排拉得很长；小桌上两只杯子，杯沿碰在一起；海里两只海龟并排游过去。"""
    k = min(int(t / 2.33), 2)
    u = t - k * 2.33
    if k == 0:                                                     # 长长的影子
        with cam(c, 540, 1200, 1.15, ty=-u * 30):
            terrace(c, t, sun=1.0, warm=0.7)
            with keep():
                for j, x in enumerate((300, 780)):
                    shape(c, [(x - 50, 1240), (x + 50, 1240), (x - 140, 1800), (x - 300, 1800)], (0.35, 0.25, 0.3, 0.35),
                          f"shd{j}", lw=0, edge=False)
    elif k == 1:                                                   # 两只杯子，杯沿碰在一起
        vgrad(c, 0, 1920, [(0, hexc("f6c99a")), (1, hexc("fbe6c4"))])
        with keep():
            glow(c, 760, 500, 500, hexc("ffd08a"), 0.6)
            shape(c, ell(540, 1180, 360, 60, 30), hexc("fbfaf6"), "tabtop", lw=3)
            tilt = 0.12 * ease_out(prog(u, 0.3, 0.6))
            for j, sg in enumerate((-1, 1)):
                c.save()
                c.translate(540 + sg * 70, 1170)
                c.rotate(-sg * tilt)
                shape(c, [(-46, -300), (46, -300), (16, -170), (-16, -170)], hexc("f6e08a") + (0.85,), f"cup{j}", lw=2.4)
                line(c, [(0, -170), (0, -40)], f"cupst{j}", 5)
                shape(c, ell(0, -30, 46, 12, 16), (1, 1, 1, 0.6), f"cupb{j}", lw=2)
                for b in range(4):
                    circle(c, -10 + b * 7, -220 - ((u * 40 + b * 13) % 70), 3, (1, 1, 1), a=0.8)
                c.restore()
            if tilt > 0.1:
                star(c, 540, 870, 14, 1 - prog(u, 0.9, 0.6), hexc("fff3b0"))
    else:                                                          # 两只海龟
        vgrad(c, 0, 1920, [(0, hexc("5fd0d0")), (1, hexc("2fa0a8"))])
        with keep():
            for j in range(14):
                ph = math.sin(t * 2 + j)
                shape(c, ell((j * 173) % W, (j * 131) % 1700, 70 + ph * 10, 16, 16), None, f"caus{j}", lw=1.6, alpha=0.35)
            for j in range(2):
                tx = lerp(-120, 1200, u / 2.33) + j * 40
                ty = 760 + j * 170 + math.sin(u * 3 + j) * 10
                fl = math.sin(u * 6 + j) * 0.4
                for sg in (-1, 1):
                    shape(c, ell(tx + 30, ty + sg * 60, 46, 16, 12), hexc("7fa06a"), f"tfl{j}{sg}", lw=1.6)
                shape(c, ell(tx, ty, 90, 64, 18), hexc("6f8a4a"), f"tsh{j}", lw=2.4)
                for q in range(5):
                    shape(c, ell(tx - 40 + q * 20, ty + (q % 2) * 14 - 7, 16, 14, 8), hexc("8aa05a"), f"tsc{j}{q}", lw=1)
                shape(c, ell(tx + 100, ty, 26, 20, 12), hexc("8fb07a"), f"th{j}", lw=1.8)


def e10(c, t):
    """海太蓝 / 落日太盛大 / 夜晚又太安静。"""
    k = min(int(t / 3.33), 2)
    u = t - k * 3.33
    if k == 0:
        vgrad(c, 0, 1920, [(0, hexc("7fe0e0")), (1, hexc("2fb0c0"))])
        with keep():
            for j in range(26):
                ph = (u * 0.3 + j / 26) % 1
                cx, cy = (j * 211) % W, (j * 137) % 1700
                shape(c, ell(cx, cy, 30 + ph * 90, 10 + ph * 26, 18), None, f"ring{j}", lw=2.2, alpha=0.6 * (1 - ph))
                circle(c, cx, cy, 4, (1, 1, 1), a=0.6 * (1 - ph))
    elif k == 1:
        caldera(c, t, sun=1.7 + 0.3 * u / 3.33, warm=0.9)
    else:
        villa_dusk(c, t, night=1.0)


def gold_press(c, amount, t):
    """金色的光像一床厚厚的被子，一层一层压下来。"""
    with keep():
        for k in range(7):
            u = clamp(amount * 7 - k)
            if u <= 0:
                continue
            y = lerp(-400, 200 + k * 120, ease_io(u))
            c.save()
            g = cairo.LinearGradient(0, y - 400, 0, y + 60)
            g.add_color_stop_rgba(0, 1.0, 0.72, 0.38, 0.0)
            g.add_color_stop_rgba(1, 1.0, 0.72, 0.38, 0.22)
            c.set_source(g)
            c.rectangle(-600, y - 400, W + 1200, 460)
            c.fill()
            c.restore()


def e11(c, t):
    """她一个人站在露台上看落日。落日越来越大，天越来越低，金色的光一层层压下来，她越来越小，只剩一个剪影。"""
    grow = ease_io(prog(t, 0.0, 9.5))
    k = lerp(1.0, 0.6, grow)
    with cam(c, 540, 1150, k, ty=lerp(0, -180, grow)):
        terrace(c, t, sun=1.0 + 1.5 * grow, warm=0.8)
        dark = ease_io(prog(t, 5.0, 4.0))
        if dark > 0.02:                                            # 慢慢只剩一个剪影
            with nokeep():
                with grade(sat=lerp(1.0, 0.2, dark), dark=0.75 * dark, warm=0.0):
                    girl(c, 540, 1240, 1.5, view="back", hat=True, pack=True, key="g11")
        else:
            girl(c, 540, 1240, 1.5, view="back", hat=True, pack=True, key="g11")
    gold_press(c, ease_io(prog(t, 5.6, 5.0)), t)


def e12(c, t):
    """她往后退了一步。镜头退出海报，回到街上：玻璃上映着她一个人。"""
    if t < 1.0:
        terrace(c, 4.0, sun=1.6, warm=0.8)
        back = ease_io(prog(t, 0.0, 0.8))
        girl(c, 540, lerp(1240, 1270, back), lerp(1.5, 1.6, back), view="back", hat=True, pack=True, key="g12")
        return

    def street_glass(cc):
        glass_scene(cc, t, poster_warm=0.8, sun=1.6, refl_a=0.4)
        girl(cc, 820, 1900, 2.8, view="back", hat=True, pack=True, key="g12b")
    e = ease_io(prog(t, 1.0, 1.4))
    if e < 1:
        x, y, w, h = 110, 140, 860, 1040
        sf = w / W
        z = lerp(1.0 / sf, 1.0, e)
        c.save()
        c.scale(z, z)
        c.translate(-lerp(x, 0, e), -lerp(y, 0, e))
        street_glass(c)
        c.restore()
        return
    street_glass(c)


# ================================================================ 13–14 留给一些人
def e13(c, t):
    """倒影里只有她；然后她身边慢慢多出一个模糊的身影，身后又多出好几个。她没有回头，只是对着玻璃笑了一下。"""
    others = ease_io(prog(t, 3.8, 3.2))
    glass_scene(c, t, poster_warm=0.6, sun=1.2, refl_a=0.42, others=others)
    girl(c, 820, 1900, 2.8, view="back", hat=True, pack=True, key="g13")


def two_shadows(c, t):
    terrace(c, t, sun=1.3, warm=0.8)
    with keep():                                                   # 两个人的影子并排坐着，落日在他们之间
        for j, x in enumerate((360, 720)):
            c.save()
            c.push_group()
            local(c, x, 1150, 1.7, f"sh{j}", hexc("3a2a3a"), hexc("3a2a3a"), "short" if j else "bang_short",
                  sit=True, legs=False, view="back")
            c.pop_group_to_source()
            c.paint_with_alpha(0.85)
            c.restore()


def shallow_walk(c, t):
    vgrad(c, Y0, 700, [(0, hexc("7fc0f0")), (1, hexc("e6f6fc"))], X0, X1)
    vgrad(c, 700, Y1, [(0, hexc("7fe0d8")), (1, hexc("3fb8c0"))], X0, X1)
    with keep():
        for j in range(16):
            ph = math.sin(t * 2 + j)
            shape(c, ell((j * 173) % W, 800 + (j * 97) % 700, 60 + ph * 10, 12, 16), None, f"sc{j}", lw=1.6, alpha=0.35)
    people = [(250, 1.6, "c98d72", "bang_long"), (430, 1.3, "8fb39a", "short"), (600, 1.0, "f2a6a0", "pony"),
              (800, 1.5, "7d6a8f", "short")]
    for k, (x, s, col, st) in enumerate(people):
        xx = x + t * 25
        wave = k % 2 == 1
        local(c, xx, 1180 - (1.6 - s) * 120, s, f"sw{k}", hexc(col), hexc("3a3a3a"), st, walk=t * 4 + k,
              look=-0.8, mouth="laugh", arms=[(-24, -78), (44, -176 + 14 * math.sin(t * 8))] if wave else None,
              leg=SKIN_L)
        fy = 1180 - (1.6 - s) * 120
        with keep():                                               # 浅浅的海水没过脚踝
            shape(c, ell(xx, fy - 6, 46 * s / 1.6, 14 * s / 1.6, 16), hexc("6fd8d0") + (0.75,), f"ank{k}", lw=1.4, amp=0.4)
            for q in range(3):
                line(c, [(xx - 40 + q * 10, 1180 - (1.6 - s) * 120 - 10 + q * 8),
                         (xx + 40 - q * 10, 1180 - (1.6 - s) * 120 - 6 + q * 8)], f"rip{k}{q}", 2, (1, 1, 1), alpha=0.6)


def night_table(c, t):
    caldera(c, t, night=1.0, tower=False)
    shape(c, [(X0, 1060), (X1, 1060), (X1, Y1), (X0, Y1)], hexc("3a3550"), "nterr", lw=3)
    line(c, [(-40, 760), (1120, 800)], "lights", 2, hexc("6a6560"))
    with keep():
        for k in range(10):                                        # 晃来晃去的灯
            x = k * 120
            y = 770 + k * 3 + math.sin(t * 2 + k) * 8
            glow(c, x, y + 14, 70, hexc("ffd98a"), 0.5)
            circle(c, x, y + 14, 9, hexc("fff0b8"))
    for k in range(6):
        x = 130 + k * 165
        sway = math.sin(t * 3 + k) * 0.04
        local(c, x, 1130, 1.25, f"nt{k}", hexc(["c98d72", "8fb39a", "4f8a8a", "7d6a8f", "6b7a8a", "f2a6a0"][k]),
              hexc("2f2a28"), ["short", "bang_long", "short", "pony", "short", "bang_short"][k], sit=True, legs=False,
              mouth="laugh", look=0.3 * (1 if k % 2 else -1), tilt=sway, arms=[(-24, -70), (30, -176)])
        with keep():
            shape(c, [(x + 30 * 1.25 - 10, 1130 - 176 * 1.25 + 52 * 1.25 - 30), (x + 30 * 1.25 + 10, 1130 - 176 * 1.25 + 52 * 1.25 - 30),
                      (x + 30 * 1.25 + 6, 1130 - 176 * 1.25 + 52 * 1.25), (x + 30 * 1.25 - 6, 1130 - 176 * 1.25 + 52 * 1.25)],
                  hexc("f6e08a"), f"ntg{k}", lw=1.4)
    shape(c, rect(60, 1140, 960, 26), hexc("8c5a3c"), "ntab", lw=2.4)
    with keep():
        for k in range(5):
            glow(c, 160 + k * 190, 1130, 50, hexc("ffd98a"), 0.5)
            shape(c, rect(150 + k * 190, 1108, 20, 30), hexc("fff0b8"), f"cand{k}", lw=1.2)


def street_end(c, lt):
    """玻璃里又只剩她一个人，可她在笑。她转身往前走，橱窗上的蒲公英种子也被风带起来，跟着她飘走。"""
    vgrad(c, 0, 1000, [(0, hexc("f2c79a")), (1, hexc("fbecd0"))])
    shape(c, rect(-20, 120, W + 40, 960), hexc("e8d6b8"), "shopw3", lw=3)
    shape(c, rect(40, 280, 1000, 720), hexc("dfeef4"), "glass3", lw=4)
    with keep():
        shape(c, rect(288, 318, 444, 584), (1, 1, 1), "ipf3", lw=3)
    poster_art(c, 300, 330, 420, 560, lt, warm=0.6, sun=1.2)
    shape(c, rect(300, 330, 420, 560), None, "ipb3", lw=2.4)
    shape(c, rect(-20, 1000, W + 40, 900), hexc("c9c2b4"), "walk3", lw=3)
    r = random.Random(9)
    crowd = ease_io(prog(lt, 1.2, 1.0))
    for k in range(int(6 * crowd)):
        px = (r.uniform(0, 1200) + lt * (70 if k % 2 else -60)) % 1300 - 100
        local(c, px, 1160 + r.uniform(0, 100), 1.25, f"cr{k}", hexc(["8fb39a", "c98d72", "7d6a8f", "4f8a8a"][k % 4]),
              hexc("2f2a28"), "short", walk=lt * 6 + k, look=0.8 if k % 2 else -0.8, mouth="smile")
    turn = lt > 0.8
    walk = ease_in(prog(lt, 1.2, 2.4))
    gx, gy, gs = 540 + walk * 420, 1240 - walk * 60, 1.6 - walk * 0.4
    girl(c, gx, gy, gs, view="front" if turn else "back", hat=True, pack=True, look=0.9 if turn else 0.0, mouth="smile",
         walk=lt * 6 if walk > 0 else None, key="g14")
    lift = ease_in(prog(lt, 1.6, 2.4))                             # 蒲公英种子跟着她飘走
    seed(c, lerp(760, gx + 80, lift), lerp(300, gy - 300 * gs, lift) + math.sin(lt * 3) * 16, 0.8, "s14", open_=1.0,
         glow_a=0.2)


def e14(c, t):
    if t < 4.2:
        two_shadows(c, t)
    elif t < 8.4:
        shallow_walk(c, t - 4.2)
    elif t < 12.4:
        night_table(c, t)
    else:
        lt = t - 12.4
        street_end(c, lt)
        a = 1 - ease_io(prog(lt, 0.0, 0.8))
        if a > 0:
            with group_alpha(c, a):
                night_table(c, t)


# ================================================================ 片尾
_STILL = {}


def end_still():
    if "s" not in _STILL:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(130.0)
        with grade(sat=1.0, dark=0.0, warm=0.1):
            street_end(cc, 0.5)
        _STILL["s"] = surf
    return _STILL["s"]


def outro(c, t):
    book_outro(c, t, end_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第四章 · 完")

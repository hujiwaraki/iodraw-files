"""第四章 · 不敢抵达的地方 —— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。"""
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
NIGHT = hexc("1f2a4a")
SEA_N = hexc("2b4470")
TURQ = hexc("4fd0d0")
DOME = hexc("2f6fc8")


# ================================================================ 通用小物件
def anchor(c, x, y, s, key, paper=0.0, rot=0.0, col=hexc("5d6470")):
    """船锚。paper=1 时是一只纸折的锚：白色、带折痕。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    fill = mix(col, hexc("f8f6ee"), paper)
    with keep():
        shape(c, ell(0, -92, 16, 16, 14), None, key + "ring", lw=6)
        shape(c, rect(-7, -76, 14, 120), fill, key + "sh", lw=2.4)
        shape(c, rrect(-44, -70, 88, 14, 6), fill, key + "st", lw=2.4)
        arc = [(math.cos(a) * 58, 6 + math.sin(a) * 40) for a in [math.pi * (0.05 + 0.9 * i / 16) for i in range(17)]]
        line(c, arc, key + "arc", 13, darker(fill, 0.95))
        line(c, arc, key + "arci", 2.4)
        for sg in (-1, 1):
            shape(c, [(sg * 56, 14), (sg * 72, -10), (sg * 46, 0)], fill, f"{key}fl{sg}", lw=2.4)
        if paper > 0.3:                                            # 纸的折痕
            for k, (a, b) in enumerate((((-7, -76), (7, -20)), ((-7, 0), (7, 44)), ((-44, -70), (0, -56)))):
                line(c, [a, b], f"{key}fold{k}", 1.4, hexc("b8b2a4"), alpha=paper)
    c.restore()


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


def ghost(c, a=0.75):
    """虚线、半透明的想象画面。"""
    class _G:
        def __enter__(self):
            self.g = group_alpha(c, a)
            self.g.__enter__()
            self.i = ink_style(hexc("6f8fb8"), dash=[10, 7])
            self.i.__enter__()
            self.gr = grade(sat=0.35, warm=0.2)
            self.gr.__enter__()

        def __exit__(self, *e):
            self.gr.__exit__(*e)
            self.i.__exit__(*e)
            self.g.__exit__(*e)
    return _G()


def bubble_text(c, s, x, y, size, col=INK, a=1.0):
    with keep():
        text(c, s, x, y, size, col, a=a)


def anchor_illus(c, cx, cy):
    """章节页小插画：一只小小的船锚。"""
    anchor(c, cx, cy + 20, 0.75, "ill")


def intro(c, t):
    book_intro(c, t, "第四章", "不敢抵达的地方", anchor_illus)


# ================================================================ 1 去哪都不对：同一个机位，换了很多房间
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
    lt = t - 9.2                                                   # 床 → 小船
    night_sea(c, t)
    boat(c, 560, 1020, 1.3, "b1")
    lying_girl(c, 560, 990, 1.3, key="g1b", hat=False, mouth="flat")
    boat_front(c, 560, 1020, 1.3, "b1")
    a = 1 - ease_io(prog(lt, 0.0, 1.4))
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


# ================================================================ 2 抛不下的锚
def e02(c, t):
    """小船漂在月光的海上，她把锚抛下去；镜头跟着锚往下沉：绳子放到了头，锚还悬在水里，碰不到底。"""
    throw = prog(t, 1.2, 0.5)
    fall = clamp((t - 1.7) / 4.0)
    ay = 900 + ease_out(fall) * 1700 if t > 1.7 else 0
    jerk = math.sin(max(0.0, t - 5.7) * 9) * math.exp(-max(0.0, t - 5.7) * 2) * 30 if t > 5.7 else 0.0
    cam_y = clamp(ay - 1000, 0, 1500) if t > 1.7 else 0
    c.save()
    c.translate(0, -cam_y)
    night_sea(c, t)
    vgrad(c, 1100, 3400, [(0, hexc("1f3560")), (0.6, hexc("0f1a33")), (1, hexc("05080f"))])
    r = random.Random(3)
    with keep():
        for k in range(30):                                        # 水里的小光点
            bx, by = r.uniform(0, W), r.uniform(1000, 3300)
            circle(c, bx + math.sin(t + k) * 6, by - (t * 20) % 60, 3, hexc("8fb8e0"), a=0.4)
    rock = math.sin(t * 1.4) * 0.03
    sitting = True
    arm = [(-24, -78), (60, -180)] if t < 1.2 else [(-24, -78), (lerp(60, 70, throw), lerp(-180, -100, throw))]
    if t > 1.7:
        arm = [(-24, -78), (40, -110 + 6 * math.sin(t * 10) * (fall < 1))]
    boat(c, 540, 900, 1.2, "b2", rock)
    girl(c, 500, 880, 1.2, sit=sitting, legs=False, hat=True, look=0.6, mouth="flat", head_down=6, arms=arm, key="g2")
    boat_front(c, 540, 900, 1.2, "b2", rock)
    if t < 1.7:                                                    # 举起锚
        hx, hy = 500 + arm[1][0] * 1.2, 880 + arm[1][1] * 1.2
        anchor(c, hx + 30 * throw * 3, hy + 40 + throw * 120, 0.55, "a2")
    else:
        line(c, [(560, 880), (620, 905), (620 + jerk * 0.2, ay - 70)], "rope", 2.4, hexc("d9c39a"))
        anchor(c, 620 + jerk * 0.2, ay, 0.8, "a2", rot=jerk * 0.004)
        if fall < 0.15:                                            # 水花
            with keep():
                for k in range(6):
                    shape(c, ell(600 + k * 10, 900 - 30 * math.sin(fall / 0.15 * math.pi) - k * 4, 8, 6, 8), (1, 1, 1),
                          f"spl{k}", lw=1, alpha=1 - fall / 0.15)
    c.restore()


# ================================================================ 3 三座小岛
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


def e03(c, t):
    """小船漂过三座小岛：每一座她都举起锚，又放下。"""
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
    lift = math.sin(clamp((u - 0.7) / 1.8) * math.pi)
    rock = math.sin(t * 1.4) * 0.03
    boat(c, 520, 1150, 1.3, "b3", rock)
    girl(c, 480, 1130, 1.3, sit=True, legs=False, hat=True, look=0.8, mouth="flat",
         arms=[(-24, -78), (40, lerp(-90, -200, lift))], key="g3")
    anchor(c, 480 + 40 * 1.3, 1130 + lerp(-90, -200, lift) * 1.3 + 50, 0.5, "a3")
    boat_front(c, 520, 1150, 1.3, "b3", rock)


# ================================================================ 4 就是这里了
def e04(c, t):
    """小船靠上沙滩，她用树枝在沙子上写“就是这里了”，退后一步看看；一个浪打过来，字被抹平了。"""
    vgrad(c, 0, 560, [(0, hexc("1e2a4c")), (1, hexc("44587e"))])
    with keep():
        circle(c, 820, 200, 56, hexc("fdf3d6"))
        glow(c, 820, 200, 220, hexc("fff3c8"), 0.3)
    shape(c, rect(-20, 560, W + 40, 300), hexc("2b4470"), "e4sea", lw=2)
    vgrad(c, 760, 1920, [(0, hexc("cdbb98")), (1, hexc("a8977a"))])
    # 浪：盖过来，再退回去
    w_in = ease_io(prog(t, 3.5, 0.8)) * (1 - ease_io(prog(t, 4.5, 1.0)))
    edge = 760 + w_in * 420
    pts = [(-20, 740)] + [(x, edge + 14 * math.sin(x * 0.02 + t * 3)) for x in range(-20, W + 60, 60)] + [(W + 40, 740)]
    # 字
    written = 1.0 if t > 2.4 else t / 2.4
    erased = ease_io(prog(t, 3.8, 0.6))
    s = "就是这里了"
    n = int(len(s) * written)
    if n > 0:
        with keep():
            text(c, s[:n], 380, 1030, 80, hexc("6b5a40"), a=0.85 * (1 - erased))
    shape(c, pts, hexc("e8f2f6") + (0.85,), "wave", lw=2.4)
    for k in range(3):
        line(c, [(x, edge - 20 - k * 30 + 8 * math.sin(x * 0.03 + t * 2 + k)) for x in range(-20, W + 60, 60)],
             f"foam{k}", 2, (1, 1, 1), alpha=0.6)
    boat(c, 150, 840, 0.9, "b4", -0.08)
    boat_front(c, 150, 840, 0.9, "b4", -0.08)
    back = ease_io(prog(t, 2.6, 0.7))
    gx = lerp(700, 860, back)
    gy = lerp(1180, 1150, back)
    write = t < 2.4
    wob = math.sin(t * 9) * 20 if write else 0
    girl(c, gx, gy, 1.6, hat=True, mouth="smile" if t < 4.0 else "o", look=-0.5 if write else -0.2, head_down=10 if write else 0,
         arms=[(-24, -78), (-40 + wob * 0.4, -60)] if write else [(-24, -78), (24, -78)], key="g4")
    if write or t < 2.6:
        line(c, [(gx - 40 * 1.6 + wob * 0.6, gy - 60 * 1.6), (gx - 120 + wob, gy - 20)], "stick", 4, WOOD)


# ================================================================ 5 很难被锚住的人
def underwater(c, t, depth=0.0):
    vgrad(c, 0, 1920, [(0, mix(hexc("1f3560"), hexc("0b1222"), depth)), (1, hexc("04070d"))])
    r = random.Random(8)
    with keep():
        for k in range(40):
            bx, by = r.uniform(0, W), r.uniform(0, 1900)
            circle(c, bx + math.sin(t + k) * 6, (by - t * 30) % 1900, r.uniform(2, 4), hexc("8fb8e0"), a=0.35)
        for k in range(5):                                         # 光柱
            x = 200 + k * 180
            c.save()
            g = cairo.LinearGradient(x, 0, x, 1200)
            g.add_color_stop_rgba(0, 0.7, 0.85, 1, 0.12 * (1 - depth))
            g.add_color_stop_rgba(1, 0.7, 0.85, 1, 0)
            c.set_source(g)
            c.move_to(x - 30, 0)
            c.line_to(x + 30, 0)
            c.line_to(x + 140, 1200)
            c.line_to(x + 60, 1200)
            c.close_path()
            c.fill()
            c.restore()


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


def e05(c, t):
    if t < 3.3:                                                    # 水下：锚悬着，下面看不到底
        underwater(c, t, depth=prog(t, 0, 3.3) * 0.6)
        sw = math.sin(t * 1.2) * 0.06
        line(c, [(540, -20), (540 + sw * 200, 760)], "rope5", 2.4, hexc("d9c39a"))
        anchor(c, 540 + sw * 200, 840, 1.1, "a5", rot=sw)
        return
    lt = t - 3.3
    u = ease_io(prog(lt, 2.5, 4.5))
    dawn_sea(c, t, u)
    rock = math.sin(t * 1.4) * 0.03
    boat(c, 540, 1160, 1.5, "b5", rock)
    pull = lt < 1.8
    if pull:                                                       # 一把一把拉上来
        ph = math.sin(lt * 6)
        girl(c, 520, 1140, 1.5, sit=True, legs=False, hat=True, look=0.5, mouth="flat",
             arms=[(-30, -110 + 30 * ph), (30, -110 - 30 * ph)], key="g5")
        line(c, [(520 + 30 * 1.5, 1140 - 100 * 1.5), (700, 1220)], "rope5b", 2.4, hexc("d9c39a"))
    else:
        fly = ease_in(prog(lt, 3.9, 3.6))
        hold = fly <= 0
        look_up = 0.6 * ease_io(prog(lt, 3.9, 1.0))
        girl(c, 520, 1140, 1.5, sit=True, legs=False, hat=True, look=0.0, look_up=look_up,
             mouth="o" if lt < 3.6 else "smile", arms=[(-34, -150), (34, -150)] if hold else [(-24, -78), (40, -130)],
             key="g5")
        ax = 520 + fly * 260 + math.sin(lt * 3) * 30 * fly
        ay = 1140 - 150 * 1.5 - 40 - fly * 900
        paper = ease_io(prog(lt, 1.8, 1.0))
        if fly > 0:                                                # 像风筝：线还拖在下面
            line(c, [(520 + 40 * 1.5, 1140 - 130 * 1.5), ((520 + ax) / 2 + 60, (1140 - 195 + ay) / 2 + 80), (ax, ay + 40)],
                 "kite", 2, hexc("d9c39a"), alpha=1 - fly)
            with keep():
                for k in range(4):                                 # 风
                    yy = 500 + k * 120
                    xx = (lt * 700 + k * 260) % 1400 - 200
                    line(c, [(xx, yy), (xx + 120, yy - 10), (xx + 200, yy + 6)], f"wind{k}", 2.4, (1, 1, 1), alpha=0.6)
        anchor(c, ax, ay, 0.9 - 0.3 * fly, "a5p", paper=paper, rot=math.sin(lt * 2) * 0.2 * fly)
    boat_front(c, 540, 1160, 1.5, "b5", rock)


# ================================================================ 6–7 旅行社的橱窗
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


POSTERS = [(poster_snow, "雪山"), (poster_desert, "沙漠"), (poster_town, "古城"), (poster_jungle, "雨林")]


def poster_frame(c, x, y, w, h, fn, label, t, key):
    with keep():
        shape(c, rect(x - 10, y - 10, w + 20, h + 70), (1, 1, 1), key + "pf", lw=2.4)
    c.save()
    c.rectangle(x, y, w, h)
    c.clip()
    fn(c, x, y, w, h, t)
    c.restore()
    shape(c, rect(x, y, w, h), None, key + "pb", lw=2)
    with keep():
        text(c, label, x + w / 2, y + h + 44, 30, INK)


X0, X1, Y0, Y1 = -500, W + 500, -600, 2800                    # 画得比画面大，镜头拉远时不露边


def island_scene(c, t, couple=True, sun=0.0, warm=0.0):
    """蓝白色的海岛：左边的山坡上层层叠叠的白房子、蓝圆顶，右边是海和落日，一段台阶通向海边。"""
    sky_a = mix(hexc("5fb0f0"), hexc("e8885a"), warm)
    sky_b = mix(hexc("cfeafc"), hexc("ffd9a0"), warm)
    vgrad(c, Y0, 820, [(0, sky_a), (1, sky_b)], X0, X1)
    if sun > 0:
        with keep():
            glow(c, 720, 760, 520 * sun, hexc("ffb060"), 0.55 * min(1.0, warm + 0.3))
            circle(c, 720, 760, 110 * sun, mix(hexc("fff3c0"), hexc("ffc060"), warm))
    vgrad(c, 820, 1300, [(0, mix(hexc("2f8fd8"), hexc("d8805a"), warm)), (1, mix(hexc("1f6fb0"), hexc("9a5a5a"), warm))],
          X0, X1)
    with keep():
        for k in range(8):                                         # 海面的光
            y = 840 + k * k * 6
            w_ = 40 + k * 22
            off = math.sin(t * 1.5 + k * 1.3) * 16
            line(c, [(720 - w_ / 2 + off, y), (720 + w_ / 2 + off, y)], f"isl{k}", 3,
                 mix(hexc("e6f4fc"), hexc("ffe0a0"), warm), alpha=0.6 - k * 0.05)
    white = mix(hexc("fbfaf6"), hexc("ffe2c0"), warm)
    shade = mix(hexc("dfe6ee"), hexc("e8b890"), warm)
    # 左边的山坡
    shape(c, [(X0, 300), (80, 340), (360, 560), (560, 820), (640, 1000), (X0, 1000)], mix(hexc("cdbb98"), hexc("c8946a"), warm),
          "hill", lw=3)
    rows = [(430, [-60, 60, 180]), (560, [-80, 50, 180, 300]), (700, [-40, 90, 220, 350, 470]),
            (850, [-60, 70, 200, 330, 460])]
    for ri, (base, xs) in enumerate(rows):
        for k, x in enumerate(xs):
            if x > 80 + (base - 300) * 1.05:
                continue
            sz = 100 + ri * 8
            shape(c, rect(x, base - sz, sz * 1.1, sz), white, f"ih{ri}{k}", lw=2)
            shape(c, rect(x + sz * 1.1 - 14, base - sz, 14, sz), shade, f"ihs{ri}{k}", lw=1, edge=False)
            with keep():
                shape(c, ell(x + sz * 0.4, base - sz * 0.45, sz * 0.12, sz * 0.18, 12, math.pi, 2 * math.pi) +
                      [(x + sz * 0.52, base - sz * 0.25), (x + sz * 0.28, base - sz * 0.25)], DOME, f"ihw{ri}{k}", lw=1.4)
            if (k + ri) % 2 == 0:
                shape(c, ell(x + sz * 0.55, base - sz, sz * 0.36, sz * 0.36, 18, math.pi, 2 * math.pi), DOME,
                      f"id{ri}{k}", lw=2)
                line(c, [(x + sz * 0.55, base - sz * 1.36), (x + sz * 0.55, base - sz * 1.58)], f"ix{ri}{k}", 3, white)
                line(c, [(x + sz * 0.47, base - sz * 1.5), (x + sz * 0.63, base - sz * 1.5)], f"ixh{ri}{k}", 3, white)
    # 一段白台阶通向海边
    for k in range(6):
        shape(c, rect(380 + k * 40, 900 + k * 50, 260, 50), white, f"ist{k}", lw=1.8)
    shape(c, [(X0, 1200), (X1, 1200), (X1, Y1), (X0, Y1)], mix(hexc("f4f0e6"), hexc("ffd9a8"), warm), "iground", lw=3)
    if couple:                                                     # 台阶下拍婚纱照的新人
        veil = math.sin(t * 2.2)
        local(c, 680, 1190, 1.5, "groom", hexc("2f3a4a"), hexc("2f2a28"), "short", look=-0.4, mouth="smile",
              arms=[(-30, -100), (24, -78)])
        with keep():
            pts = [(560 - 10, 1190 - 230), (560 + 20, 1190 - 236), (560 - 80 - 50 * veil, 1190 - 120),
                   (560 - 240 - 70 * veil, 1190 - 170 + 50 * veil), (560 - 190, 1190 - 260 - 30 * veil)]
            shape(c, pts, (1, 1, 1, 0.7), "veil", lw=1.8)
        local(c, 560, 1190, 1.5, "bride", hexc("fbfaf6"), hexc("5a3a2a"), "bang_long", look=0.4, mouth="laugh",
              arms=[(-24, -78), (30, -100)])
        with keep():
            shape(c, [(560 - 36, 1190 - 70), (560 + 36, 1190 - 70), (560 + 66, 1190), (560 - 66, 1190)], (1, 1, 1),
                  "skirt", lw=2)


def villas_scene(c, t, sign=True, night=0.0):
    """碧绿的浅海上，木栈道连着一间间水上小木屋。"""
    vgrad(c, 0, 600, [(0, mix(hexc("6fc8f0"), hexc("0f1630"), night)), (1, mix(hexc("e6f6fc"), hexc("2a3a6a"), night))])
    vgrad(c, 600, 1920, [(0, mix(TURQ, hexc("10203a"), night)), (1, mix(hexc("2fb0b8"), hexc("0a1428"), night))])
    if night > 0.5:
        r = random.Random(12)
        with keep():
            for k in range(70):
                star(c, r.uniform(0, W), r.uniform(0, 560), r.uniform(1.5, 3.2), 0.6 + 0.4 * math.sin(t * 1.5 + k))
    with keep():                                                   # 浅海里的光斑
        for k in range(14):
            cx = (k * 173) % W
            cy = 700 + (k * 97) % 500
            ph = math.sin(t * 2 + k)
            shape(c, ell(cx, cy, 60 + ph * 10, 14, 16), None, f"caus{k}", lw=1.6, amp=0.6, alpha=0.3 * (1 - night))
    # 栈道
    shape(c, [(80, 720), (1000, 720), (1000, 744), (80, 744)], WOOD, "board", lw=2.4)
    for k in range(5):                                             # 水上小木屋
        x = 120 + k * 200
        for sg in (-1, 1):
            line(c, [(x + sg * 50, 690), (x + sg * 50, 780)], f"stilt{k}{sg}", 5, hexc("6b4a32"))
        shape(c, rect(x - 70, 600, 140, 100), hexc("d9b778"), f"vil{k}", lw=2.4)
        shape(c, [(x - 90, 604), (x + 90, 604), (x, 530)], hexc("b88a52"), f"vr{k}", lw=2.4)
        lit = night > 0.5 and k == 3
        with keep():
            shape(c, rect(x - 20, 640, 40, 50), hexc("ffd98a") if lit else hexc("6b4a32"), f"vd{k}", lw=1.6)
            if lit:
                glow(c, x, 660, 120, hexc("ffd98a"), 0.7)
                for j in range(5):                                 # 水里的倒影
                    line(c, [(x - 16 + j * 2, 800 + j * 20), (x + 16 - j * 2, 800 + j * 20)], f"refl{j}", 3,
                         hexc("ffd98a"), alpha=0.5 - j * 0.08)
    if sign:
        with keep():
            shape(c, rect(640, 520, 180, 50), (1, 1, 1), "vsign", lw=2)
            text(c, "蜜月套房", 730, 556, 30, RED)
    # 近处的小木屋：门开着，床上用花瓣摆成一颗心
    if sign:
        shape(c, rect(80, 900, 920, 360), hexc("e8d0a8"), "bigvil", lw=3)
        shape(c, rect(80, 880, 920, 30), hexc("b88a52"), "bigvr", lw=2.4)
        with keep():
            shape(c, rect(260, 960, 560, 260), hexc("fbf6ec"), "bed8", lw=2.4)
            shape(c, rect(260, 960, 560, 40), hexc("e8e0d0"), "bed8h", lw=2)
            for k in range(40):                                    # 花瓣摆成的心
                a = k / 40 * 2 * math.pi
                hx = 16 * math.sin(a) ** 3
                hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
                shape(c, ell(540 + hx * 7, 1100 + hy * 7, 9, 6, 8), hexc("e8506a"), f"pet{k}", lw=0.8, amp=0.3)


def street(c, t, ox=0.0, n_post=5, island_poster=True):
    """旅行社的橱窗（世界坐标比画面宽，ox 是镜头横移）。"""
    vgrad(c, 0, 1000, [(0, hexc("cfe4ef")), (1, hexc("f6efe0"))])
    c.save()
    c.translate(-ox, 0)
    shape(c, rect(-200, 120, 2900, 960), hexc("e8d6b8"), "shopw", lw=3)
    with keep():
        shape(c, rect(-100, 150, 2700, 90), hexc("2f6a6a"), "shopsign", lw=2.4)
        for k in range(3):
            text(c, "旅 行 社", 300 + k * 900, 212, 46, (1, 1, 1))
    shape(c, rect(-60, 280, 2620, 720), hexc("dfeef4"), "glass", lw=4)
    for k, (fn, label) in enumerate(POSTERS):
        poster_frame(c, 60 + k * 480, 360, 340, 460, fn, label, t, f"pp{k}")
    if island_poster:
        island_poster_at(c, 2000, 330, 420, 560, t)
    with keep():                                                   # 玻璃反光
        for k in range(8):
            x = k * 340
            line(c, [(x, 300), (x + 120, 980)], f"refl{k}", 6, (1, 1, 1), alpha=0.35)
    shape(c, rect(-200, 1000, 2900, 900), hexc("c9c2b4"), "walk", lw=3)
    for k in range(20):
        line(c, [(k * 150 - 200, 1000), (k * 150 - 260, 1900)], f"wk{k}", 1.4, hexc("b3ab9c"), alpha=0.5)
    c.restore()


def island_poster_at(c, x, y, w, h, t):
    """最后一张海报：蓝白色的海岛。“蜜月之选 · 双人成行”。"""
    with keep():
        shape(c, rect(x - 12, y - 12, w + 24, h + 120), (1, 1, 1), "ipf", lw=3)
    c.save()
    c.rectangle(x, y, w, h)
    c.clip()
    c.translate(x, y)
    c.scale(w / W, w / W)
    island_scene(c, t, couple=True)
    c.restore()
    shape(c, rect(x, y, w, h), None, "ipb", lw=2.4)
    with keep():
        text(c, "蜜月之选 · 双人成行", x + w / 2, y + h + 70, 34, RED)


def e06(c, t):
    """纸锚飘过一条街，落在旅行社的橱窗前；她背着包一张张看过去，走到最后一张前停住了。"""
    walk = ease_io(prog(t, 1.2, 6.0))
    gx = lerp(200, 2210, walk)
    ox = clamp(gx - 540, 0, 1700)
    street(c, t, ox)
    # 飘下来的纸锚
    fall = ease_out(prog(t, 0.0, 1.6))
    anchor(c, lerp(900, 640, fall) - ox * 0 + math.sin(t * 3) * 20 * (1 - fall), lerp(200, 960, fall), 0.4, "a6", paper=1.0,
           rot=math.sin(t * 2) * 0.3 * (1 - fall))
    # 她：每张海报前轻松地点点头
    nod = 0.0
    for k in range(4):
        px = 60 + k * 480 + 170
        nod = max(nod, 1 - abs(gx - px) / 120)
    moving = 0 < walk < 1
    girl(c, gx - ox, 1240, 1.6, hat=True, pack=True, look=-0.0 if not moving else 0.7, head_down=6 * nod, look_up=0.3,
         mouth="smile", walk=t * 7 if moving else None, key="g6")


def e07(c, t):
    """海报特写：她伸手想碰，手停在玻璃前，又收了回来。"""
    vgrad(c, 0, 1920, [(0, hexc("dfeef4")), (1, hexc("cfe4ef"))])
    island_poster_at(c, 110, 140, 860, 1040, t)
    with keep():
        for k in range(4):
            line(c, [(k * 320 - 60, 100), (k * 320 + 120, 1300)], f"refl7{k}", 8, (1, 1, 1), alpha=0.3)
    reach = math.sin(clamp(prog(t, 0.8, 3.6)) * math.pi)
    girl(c, 560, 1900, 2.8, view="back", hat=True, pack=True,
         arms=[(-24, -78), (lerp(24, 60, reach), lerp(-78, -260, reach))], key="g7")


# ================================================================ 8–12 走进海报
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


def e08(c, t):
    if t < 1.2:                                                    # 穿过玻璃
        zoom_into(c, t, (110, 140, 860, 1040), lambda cc: e07(cc, 6.0), 0.0, 1.2)
        return
    if t < 5.2:
        island_scene(c, t, couple=True)
        return
    villas_scene(c, t, sign=True)


def terrace(c, t, sun=0.0, warm=0.0, chairs=2, table=False):
    """海岛的露台：面朝大海和落日，两把躺椅，桌上两只香槟杯。"""
    island_scene(c, t, couple=False, sun=sun, warm=warm)
    tf = mix(hexc("fbfaf6"), hexc("ffe2c0"), warm)
    rail = mix(hexc("d9d4c8"), hexc("e8b080"), warm)
    shape(c, [(X0, 1060), (X1, 1060), (X1, Y1), (X0, Y1)], tf, "terr", lw=3)
    line(c, [(X0, 980), (X1, 980)], "rail", 6, rail)
    for k in range(-6, 18):
        line(c, [(k * 95, 980), (k * 95, 1060)], f"railp{k}", 3, rail)
    for k, x in enumerate((230, 850)):                             # 两把躺椅
        with keep():
            shape(c, [(x - 110, 1200), (x + 90, 1200), (x + 110, 1150), (x - 70, 1150)], hexc("f4f0e6"), f"lou{k}", lw=2.4)
            shape(c, [(x + 60, 1150), (x + 110, 1150), (x + 140, 1060), (x + 100, 1060)], hexc("f4f0e6"), f"loub{k}", lw=2.4)
            for sg in (-1, 1):
                line(c, [(x + sg * 80, 1200), (x + sg * 80, 1240)], f"loul{k}{sg}", 4, hexc("8c7a62"))
    with keep():                                                   # 小桌和两只香槟杯
        shape(c, ell(540, 1150, 70, 18, 16), hexc("f4f0e6"), "ctab", lw=2.4)
        line(c, [(540, 1150), (540, 1240)], "ctabl", 5, hexc("8c7a62"))
        for k, dx in enumerate((-24, 24)):
            shape(c, [(540 + dx - 12, 1080), (540 + dx + 12, 1080), (540 + dx + 4, 1110), (540 + dx - 4, 1110)],
                  hexc("f6e08a"), f"gl{k}", lw=1.6)
            line(c, [(540 + dx, 1110), (540 + dx, 1140)], f"gls{k}", 2)
            line(c, [(540 + dx - 10, 1142), (540 + dx + 10, 1142)], f"glb{k}", 2)


def e09(c, t):
    """那里的一切都是成双的：两把躺椅、两只香槟杯、一架双人秋千、两只一起游过的海龟。"""
    z = 1.0 + 0.06 * t
    with cam(c, 540, 1000, z):
        terrace(c, t)
        with keep():                                               # 远处栈道尽头的双人秋千
            shape(c, rect(760, 900, 300, 14), WOOD, "spier", lw=2)       # 小栈道尽头的双人秋千
            line(c, [(900, 780), (900, 900)], "swpL", 4, WOOD)
            line(c, [(1020, 780), (1020, 900)], "swpR", 4, WOOD)
            line(c, [(890, 780), (1030, 780)], "swpT", 5, WOOD)
            sw = math.sin(t * 1.6) * 10
            line(c, [(920, 780), (920 + sw, 860)], "swr1", 2)
            line(c, [(1000, 780), (1000 + sw, 860)], "swr2", 2)
            shape(c, rect(910 + sw, 860, 100, 12), hexc("f4f0e6"), "swseat", lw=1.6)
            for k in range(2):                                     # 两只海龟
                tx = 640 + (t * 30 + k * 70) % 300
                ty = 940 - k * 30
                shape(c, ell(tx, ty, 26, 18, 14), hexc("6f9a5a"), f"tur{k}", lw=1.6)
                shape(c, ell(tx + 28, ty - 4, 10, 8, 10), hexc("8fb07a"), f"turh{k}", lw=1.4)


def e10(c, t):
    """海太蓝 / 落日太盛大 / 夜晚又太安静。"""
    k = min(int(t / 3.33), 2)
    u = t - k * 3.33
    if k == 0:
        villas_scene(c, t, sign=False)
        with keep():
            for j in range(20):
                ph = (u * 0.4 + j / 20) % 1
                shape(c, ell((j * 211) % W, 780 + (j * 131) % 900, 40 + ph * 80, 10 + ph * 20, 16), None, f"ring{j}",
                      lw=2, alpha=0.5 * (1 - ph))
    elif k == 1:
        island_scene(c, t, couple=False, sun=1.6 + 0.4 * u / 3.33, warm=0.9)
    else:
        villas_scene(c, t, sign=False, night=1.0)


def gray_snow(c, t, amount):
    r = random.Random(21)
    n = int(1400 * amount)
    with keep():
        for k in range(n):
            x = r.uniform(0, W)
            sp = r.uniform(60, 160)
            y = (r.uniform(0, 1900) + t * sp) % 1900
            circle(c, x + math.sin(t + k) * 8, y, r.uniform(2, 5), hexc("8a8f99"), a=0.55)
        veil(c, hexc("3a3f4a"), 0.35 * amount)


def e11(c, t):
    """她一个人站在露台上，落日越来越大，她越来越小；成千上万个灰色小光点像雪一样压下来。"""
    grow = ease_io(prog(t, 0.0, 9.0))
    k = lerp(1.0, 0.62, grow)
    with cam(c, 540, 1100, k, ty=lerp(0, -200, grow)):
        terrace(c, t, sun=1.0 + 1.4 * grow, warm=0.8)
        girl(c, 540, 1230, 1.5, view="back", hat=True, pack=True, key="g11")
    gray_snow(c, t, ease_io(prog(t, 6.6, 3.0)))


def e12(c, t):
    """她往后退了一步；镜头退出海报，回到街上的橱窗前，海报上的落日安安静静。"""
    def big(cc):
        terrace(cc, 4.0, sun=1.6, warm=0.8)
        back = ease_io(prog(t, 0.0, 0.8))
        girl(cc, 540, lerp(1230, 1260, back), lerp(1.5, 1.6, back), view="back", hat=True, pack=True, key="g12")

    if t < 1.0:
        big(c)
        return
    e = ease_io(prog(t, 1.0, 1.4))
    if e < 1:
        x, y, w, h = 300, 330, 420, 560
        sf = w / W
        z = lerp(1.0 / sf, 1.0, e)
        c.save()
        ox, oy = lerp(x, 0, e), lerp(y, 0, e)
        c.scale(z, z)
        c.translate(-ox, -oy)
        street_sunset(c, t, girl_on=e > 0.6)
        c.restore()
        return
    street_sunset(c, t)


def street_sunset(c, t, girl_on=True):
    """街上：橱窗里的海报换成了落日的那一页。"""
    vgrad(c, 0, 1000, [(0, hexc("cfe4ef")), (1, hexc("f6efe0"))])
    shape(c, rect(-20, 120, W + 40, 960), hexc("e8d6b8"), "shopw2", lw=3)
    shape(c, rect(40, 280, 1000, 720), hexc("dfeef4"), "glass2", lw=4)
    with keep():
        shape(c, rect(288, 318, 444, 584 + 100), (1, 1, 1), "ipf2", lw=3)
    c.save()
    c.rectangle(300, 330, 420, 560)
    c.clip()
    c.translate(300, 330)
    c.scale(420 / W, 420 / W)
    terrace(c, 4.0, sun=1.6, warm=0.8)
    c.restore()
    shape(c, rect(300, 330, 420, 560), None, "ipb2", lw=2.4)
    with keep():
        text(c, "蜜月之选 · 双人成行", 510, 960, 30, RED)
        for k in range(3):
            line(c, [(k * 380 + 20, 300), (k * 380 + 140, 980)], f"refl2{k}", 6, (1, 1, 1), alpha=0.3)
    shape(c, rect(-20, 1000, W + 40, 900), hexc("c9c2b4"), "walk2", lw=3)
    if girl_on:
        girl(c, 540, 1240, 1.6, view="back", hat=True, pack=True, key="g12s")


# ================================================================ 13–14 留给一些人
CARDS = ["TA", "在乎的人", "老朋友们"]


def long_table(c, grow, cards):
    """露台上多出来的长桌和椅子；卡片一张张放上去。"""
    with keep():
        y = 1150
        for k in range(5):
            x = 180 + k * 180
            pop = ease_back(clamp(grow * 5 - k))
            if pop <= 0:
                continue
            c.save()
            c.translate(x, y + 60)
            c.scale(1, pop)
            shape(c, rect(-40, -120, 80, 120), hexc("f4f0e6"), f"chb{k}", lw=2.4)
            shape(c, rect(-50, -10, 100, 14), hexc("f4f0e6"), f"chs{k}", lw=2.4)
            c.restore()
        if grow > 0.3:
            shape(c, rect(120, 1160, 840, 22), hexc("e8e0d0"), "ltab", lw=2.4)
            for x in (150, 930):
                line(c, [(x, 1182), (x, 1250)], f"ltl{x}", 5, hexc("8c7a62"))
        for k, lab in enumerate(CARDS):
            a = cards[k]
            if a <= 0:
                continue
            x = 260 + k * 280
            c.save()
            c.translate(x, 1160 - 40 * (1 - a))
            shape(c, [(-60, 0), (60, 0), (50, -50), (-50, -50)], (1, 1, 1), f"card{k}", lw=2, alpha=a)
            text(c, lab, 0, -16, 26, RED, a=a)
            c.restore()


def e13(c, t):
    terrace(c, t, sun=1.2, warm=0.6)
    grow = ease_io(prog(t, 0.2, 1.4))
    cards = [ease_out(prog(t, 2.0 + k * 1.6, 0.5)) for k in range(3)]
    long_table(c, grow, cards)
    gx = 260 + min(2, int(max(0.0, t - 1.6) / 1.6)) * 280 + 40
    gx = lerp(180, gx, ease_io(prog(t, 1.4, 0.6)))
    girl(c, gx, 1240, 1.5, hat=True, pack=True, look=-0.6, head_down=6, mouth="smile",
         arms=[(-40, -110), (24, -78)], key="g13")


def ghost_sunset(c, u):
    with ghost(c, 0.85 * math.sin(clamp(u) * math.pi) ** 0.5):
        girl(c, 450, 1000, 1.5, sit=True, legs=False, hat=False, keep_color=False, view="back", key="gh1")
        local(c, 630, 1000, 1.6, "gh1b", hexc("9aa6b5"), hexc("6a6f7d"), "short", sit=True, legs=False, view="back")


def ghost_sea(c, u, t):
    with ghost(c, 0.85 * math.sin(clamp(u) * math.pi) ** 0.5):
        for k, (x, s) in enumerate(((620, 1.2), (740, 1.0), (850, 0.8), (950, 1.15))):
            local(c, x, 930, s, f"gh2{k}", hexc(["c98d72", "8fb39a", "f2a6a0", "7d6a8f"][k]), hexc("6a6f7d"), "short",
                  walk=t * 4 + k, look=-0.7, mouth="smile", arms=[(-24, -78), (40, -170)] if k % 2 else None)
        for k in range(4):
            line(c, [(600 + k * 110, 936), (680 + k * 110, 940)], f"gh2w{k}", 2, (1, 1, 1))


def ghost_friends(c, u, t):
    with ghost(c, 0.85 * math.sin(clamp(u) * math.pi) ** 0.5):
        for k in range(5):
            x = 180 + k * 180
            sway = math.sin(t * 3 + k) * 6
            local(c, x, 1120, 1.2, f"gh3{k}", hexc(["c98d72", "8fb39a", "e8c040", "7d6a8f", "6b7a8a"][k]), hexc("6a6f7d"),
                  "short", sit=True, legs=False, mouth="laugh", look=0.3 * (1 if k % 2 else -1), tilt=sway * 0.01,
                  arms=[(-24, -70), (30, -170)])


def e14(c, t):
    """三个虚线的、半透明的画面一个个浮现，又淡去；只剩放着卡片的空椅子。镜头拉远回到街上，她转身走进人群。"""
    if t < 12.4:
        terrace(c, t, sun=1.2, warm=0.6)
        long_table(c, 1.0, [1, 1, 1])
        if t < 4.2:
            ghost_sunset(c, t / 4.2)
        elif t < 8.4:
            ghost_sea(c, (t - 4.2) / 4.2, t)
        else:
            ghost_friends(c, (t - 8.4) / 4.0, t)
        return
    lt = t - 12.4                                                  # 拉远：回到街上，她转身走进人群
    e = ease_io(prog(lt, 0.0, 1.4))
    x, y, w, h = 300, 330, 420, 560
    sf = w / W
    if e < 1:
        z = lerp(1.0 / sf, 1.0, e)
        c.save()
        ox, oy = lerp(x, 0, e), lerp(y, 0, e)
        c.scale(z, z)
        c.translate(-ox, -oy)
        street_end(c, lt, girl_on=e > 0.5)
        c.restore()
        return
    street_end(c, lt)


def street_end(c, lt, girl_on=True):
    vgrad(c, 0, 1000, [(0, hexc("f2c79a")), (1, hexc("fbecd0"))])
    shape(c, rect(-20, 120, W + 40, 960), hexc("e8d6b8"), "shopw3", lw=3)
    shape(c, rect(40, 280, 1000, 720), hexc("dfeef4"), "glass3", lw=4)
    with keep():
        shape(c, rect(288, 318, 444, 684), (1, 1, 1), "ipf3", lw=3)
    c.save()
    c.rectangle(300, 330, 420, 560)
    c.clip()
    c.translate(300, 330)
    c.scale(420 / W, 420 / W)
    terrace(c, 4.0, sun=1.2, warm=0.6)
    long_table(c, 1.0, [1, 1, 1])
    c.restore()
    shape(c, rect(300, 330, 420, 560), None, "ipb3", lw=2.4)
    with keep():
        text(c, "蜜月之选 · 双人成行", 510, 960, 30, RED)
    shape(c, rect(-20, 1000, W + 40, 900), hexc("c9c2b4"), "walk3", lw=3)
    r = random.Random(9)
    crowd = ease_io(prog(lt, 1.0, 1.0))
    for k in range(int(7 * crowd)):
        px = (r.uniform(0, 1200) + lt * (70 if k % 2 else -60)) % 1300 - 100
        local(c, px, 1180 + r.uniform(0, 100), 1.3, f"cr{k}", hexc(["8fb39a", "c98d72", "7d6a8f", "e8c040"][k % 4]),
              hexc("2f2a28"), "short", walk=lt * 6 + k, look=0.8 if k % 2 else -0.8, mouth="smile")
    if girl_on:
        turn = lt > 1.6
        walk = ease_in(prog(lt, 2.0, 2.4))
        girl(c, 540 + walk * 420, 1240 - walk * 60, 1.6 - walk * 0.4, view="front" if turn else "back", hat=True, pack=True,
             look=0.9 if turn else 0.0, mouth="smile", walk=lt * 6 if walk > 0 else None, key="g14")


# ================================================================ 片尾
_STILL = {}


def end_still():
    if "s" not in _STILL:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(130.0)
        with grade(sat=1.0, dark=0.0, warm=0.1):
            e14(cc, 15.0)
        _STILL["s"] = surf
    return _STILL["s"]


def outro(c, t):
    book_outro(c, t, end_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第四章 · 完")

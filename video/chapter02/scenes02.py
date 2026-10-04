"""第二章 · 一个人 —— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。"""
import math
import os
import random
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter01"))
from draw import *  # noqa: F401,F403,E402
from engine import book_intro, book_outro  # noqa: E402
from scenes import (GROUND, panel, p_noodle, p_suitcase, p_tall, platform_bg, room, s10_bench, s12_scale,  # noqa: E402
                    s14_aging, street_bg)
from scenes_v2 import local  # noqa: E402

RED = hexc("d9534a")
SKY_HI = hexc("2f6fb8")
SKY_LO = hexc("bfe0f2")
SNOW = hexc("f4f7fa")
ROCK = hexc("8d8a9a")
LAKE = hexc("4fc3c0")
FLAGS = [hexc("3f6fb5"), hexc("f4f2ec"), hexc("c9473b"), hexc("4f9a5c"), hexc("e8c040")]
COUPLE_COLS = [(hexc("c98d72"), hexc("5d7a9a")), (hexc("8fb39a"), hexc("7d6a8f")), (hexc("d9a65a"), hexc("6b7a5a"))]


# ================================================================ 通用
def pull(c, x, y, s, key, walk=None, d=1, **kw):
    """她拉着行李箱：d=1 向右（箱子在左后方），d=-1 向左。"""
    kw.setdefault("hat", True)
    kw.setdefault("look", 0.9 * d)
    arms = [(-26, -76), (-40, -70)] if d > 0 else [(-26, -76), (40, -70)]
    girl(c, x, y, s, walk=walk, arms=arms, key=key, **kw)
    suitcase(c, x - d * 58 * s, y + 2 * s, 0.6 * s, key + "su", tilt=(0.15 * d) if walk is not None else 0.0)


def gaze(c, x0, y0, x1, y1, k, key, a=0.8, show_eye=True):
    """别人投来的视线：一串越来越密的小短线 + 起点的一只小眼睛。"""
    if k <= 0:
        return
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - 60
    n = 9
    with keep():
        for i in range(n):
            u0 = i / n
            if u0 > k:
                break
            u1 = min(u0 + 0.5 / n, k)
            pts = []
            for u in (u0, (u0 + u1) / 2, u1):
                bx = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * x1
                by = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1
                pts.append((bx, by))
            line(c, pts, f"{key}g{i}", 3.2, hexc("4a4f5d"), alpha=a * (0.5 + 0.5 * u0))
        if show_eye:
            eye(c, x0, y0, 1.0, key + "e", a)


def eye(c, x, y, s, key, a=1.0, look=(0.0, 0.0)):
    with keep(), group_alpha(c, a):
        pts = [(x - 16 * s, y), (x, y - 9 * s), (x + 16 * s, y), (x, y + 9 * s)]
        shape(c, pts, hexc("f6f3ec"), key + "w", lw=2, amp=0.3)
        circle(c, x + look[0] * 5 * s, y + look[1] * 3 * s, 5 * s, hexc("3a3f4a"))


def couple(c, x, y, s, i, key, gap=62, look=(0.3, -0.3), hearts=0.0, t=0.0, hold=True, **kw):
    """一对牵手的情侣（不同颜色的外套）。"""
    ca, cb = COUPLE_COLS[i % len(COUPLE_COLS)]
    ha = [(-24, -78), (24 * gap / 62 + 6, -70)] if hold else None
    hb = [(-24 * gap / 62 - 6, -70), (24, -78)] if hold else None
    local(c, x - gap / 2 * s, y, s, key + "a", ca, hexc("2f2a28"), "bang_short", look=look[0], arms=ha, **kw)
    local(c, x + gap / 2 * s, y, s, key + "b", cb, hexc("3a3a3a"), "short", look=look[1], arms=hb, **kw)
    if hearts > 0:
        for k in range(3):
            ph = (t * 0.6 + k / 3) % 1
            hx = x + math.sin(ph * 6 + k) * 14 * s
            hy = y - 200 * s - ph * 90 * s
            heart(c, hx, hy, 9 * s * (1 - ph * 0.3), hearts * math.sin(math.pi * ph))


def heart(c, x, y, r, a=1.0, col=RED):
    if a <= 0:
        return
    with keep(), group_alpha(c, a):
        pts = []
        for i in range(24):
            th = i / 24 * 2 * math.pi
            hx = 16 * math.sin(th) ** 3
            hy = -(13 * math.cos(th) - 5 * math.cos(2 * th) - 2 * math.cos(3 * th) - math.cos(4 * th))
            pts.append((x + hx * r / 16, y + hy * r / 16))
        shape(c, pts, col, f"ht{int(x)}{int(y)}", lw=1.6, amp=0.2)


def o2can(c, x, y, s, key):
    """便携氧气瓶。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with keep():
        shape(c, rrect(-13, -40, 26, 58, 8), hexc("f2f0ea"), key + "b", lw=2.2, amp=0.3)
        shape(c, rect(-13, -22, 26, 18), hexc("4f8fd0"), key + "l", lw=1.6, amp=0.2)
        shape(c, rrect(-8, -52, 16, 14, 4), hexc("e07a3a"), key + "c", lw=2, amp=0.2)
    c.restore()


def plateau_bg(c, t, base=900, dusk=0.0, lake=True, flags=True, yaks=True):
    """稻城亚丁：三座雪山 + 牛奶海 + 经幡 + 远处的牦牛。"""
    top = mix(SKY_HI, hexc("e9a58a"), dusk)
    low = mix(SKY_LO, hexc("f6d6b0"), dusk)
    vgrad(c, 0, base, [(0, top), (1, low)])
    for i, (x, y, s) in enumerate(((220, 260, 1.1), (860, 200, 0.9))):
        cloud(c, x + math.sin(t * 0.2 + i) * 20, y, s, f"pc{i}")
    peaks = [(240, 330, 520, ROCK), (560, 470, 640, hexc("7f7c90")), (880, 330, 500, ROCK)]
    for i, (x, h, w, col) in enumerate(peaks):
        b = base - 60
        pts = [(x - w / 2, b), (x - w * 0.1, b - h * 0.86), (x, b - h), (x + w * 0.12, b - h * 0.84), (x + w / 2, b)]
        shape(c, pts, col, f"pk{i}", lw=3, amp=1.6)
        cap = [(x - w * 0.22, b - h * 0.55), (x - w * 0.1, b - h * 0.86), (x, b - h), (x + w * 0.12, b - h * 0.84),
               (x + w * 0.24, b - h * 0.52), (x + w * 0.12, b - h * 0.6), (x + w * 0.04, b - h * 0.5),
               (x - w * 0.06, b - h * 0.62)]
        shape(c, cap, SNOW, f"pks{i}", lw=2.4, amp=1.0)
    shape(c, hill_pts(base - 40, 26, 0.008, 0.6, bottom=base + 200), hexc("8fae7a"), "phl", lw=3)
    if lake:
        shape(c, ell(560, base - 10, 300, 46, 30), LAKE, "lake", lw=2.6)
        for k in range(3):
            line(c, [(420 + k * 90, base - 14 + k * 6), (470 + k * 90, base - 14 + k * 6)], f"lk{k}", 1.6,
                 hexc("e8fbfa"), alpha=0.7)
    if yaks:
        for i, (x, y) in enumerate(((880, base - 40), (950, base - 30))):
            x += math.sin(t * 0.3 + i) * 6
            shape(c, ell(x, y - 14, 26, 15, 14), hexc("3d342e"), f"yk{i}", lw=2, amp=0.4)
            shape(c, ell(x + 24, y - 20, 9, 8, 10), hexc("3d342e"), f"ykh{i}", lw=1.8, amp=0.3)
            for lx in (-14, -4, 8, 16):
                line(c, [(x + lx, y - 2), (x + lx, y + 8)], f"ykl{i}{lx}", 2.6, hexc("3d342e"))
            line(c, [(x + 28, y - 28), (x + 34, y - 34)], f"ykc{i}", 2, hexc("efe6d6"))
    if flags:
        prayer_flags(c, t, -40, 120, W + 40, 220, "pf1")


def prayer_flags(c, t, x0, y0, x1, y1, key):
    pts = []
    n = 16
    for i in range(n + 1):
        u = i / n
        pts.append((lerp(x0, x1, u), lerp(y0, y1, u) + math.sin(math.pi * u) * 70))
    line(c, pts, key + "rope", 2, hexc("6b5a4a"))
    with keep():
        for i in range(n):
            u = (i + 0.5) / n
            x = lerp(x0, x1, u)
            y = lerp(y0, y1, u) + math.sin(math.pi * u) * 70
            sw = math.sin(t * 4 + i) * 5
            col = FLAGS[i % 5]
            shape(c, [(x - 20, y), (x + 20, y), (x + 22 + sw, y + 42), (x - 18 + sw, y + 42)], mix(col, hexc("c9c6bd"), 0.25),
                  f"{key}{i}", lw=1.6, amp=0.4)


# ================================================================ 片头
def foot_illus(c, cx, cy):
    """章节页小插画：雪地上一行孤零零的脚印。"""
    with keep():
        shape(c, ell(cx, cy + 20, 150, 56, 24), hexc("eef3f6"), "fi_s", lw=2)
        for k in range(7):
            x = cx - 110 + k * 36
            y = cy + 52 - k * 13
            sg = 1 if k % 2 else -1
            c.save()
            c.translate(x, y + sg * 7)
            c.rotate(-0.35)
            shape(c, ell(0, 0, 6, 10, 10), hexc("aab6c2"), f"fi{k}", lw=1.2, amp=0.3)
            c.restore()


def intro(c, t):
    book_intro(c, t, "第二章", "一 个 人", foot_illus)


# ================================================================ 一、只想逃离
def c01_rush(c, t):
    with cam(c, 540, 960, 1.0, tx=-ease_io(t / 5) * 60):
        street_bg(c, t, base=760, rain_a=0.2, seed=3)
        r = random.Random(2)
        for i in range(6):
            x = (r.uniform(-200, 1300) - t * 140 * r.choice((-1, 1))) % 1500 - 200
            silhouette(c, x, 1000 + r.uniform(0, 80), 1.2, f"rs{i}", walk=t * 6 + i, a=0.55)
        x = lerp(160, 960, ease_io(t / 5))
        pull(c, x, 1150, 1.5, "g1", walk=t * 11, mouth="flat", head_down=3)
        for k in range(3):                                    # 匆忙的速度线
            yy = 980 + k * 50
            line(c, [(x - 230 - k * 30, yy), (x - 150 - k * 30, yy)], f"spd{k}", 2.4, hexc("8a8f99"), alpha=0.5)


# ================================================================ 二、问了几个朋友
CHAT = [(0.3, "me", "周末想出去走走，\n有人一起吗？"), (1.1, "a", "最近太忙了……"), (1.8, "b", "下次吧"),
        (2.5, "c", "去不了诶"), (3.0, "read", "已读")]


def bubble(c, x, y, w, h, col, key, me):
    shape(c, rrect(x, y, w, h, 18), col, key, lw=2, amp=0.4)
    tx = x + w - 6 if me else x + 6
    shape(c, [(tx, y + h - 22), (tx + (18 if me else -18), y + h - 6), (tx + (-4 if me else 4), y + h - 8)], col, key + "t",
          lw=2, amp=0.3)


def c02_ask(c, t):
    fill_all(c, hexc("d9d6ce"))
    px, py, pw, ph = 250, 140, 580, 1060
    slide = ease_io(prog(t, 3.6, 0.6))
    with keep():
        glow(c, 540, 650, 600, hexc("dfeaff"), 0.4)
        shape(c, rrect(px - 18, py - 18, pw + 36, ph + 36, 48), hexc("3a3f4a"), "phb", lw=3)
        c.save()
        c.rectangle(px, py, pw, ph)
        c.clip()
        c.translate(-slide * pw, 0)
        # 群聊
        fill_rect = rect(px, py, pw, ph)
        shape(c, fill_rect, hexc("eef0f2"), "scr", lw=0, edge=False)
        shape(c, rect(px, py, pw, 90), hexc("f8f8f8"), "hdr", lw=1.6)
        text(c, "好朋友们（5）", px + pw / 2, py + 58, 32, INK)
        y = py + 140
        for t0, who, msg in CHAT:
            k = ease_back(prog(t, t0, 0.35))
            if k <= 0:
                if who != "read":
                    y += 150
                continue
            if who == "read":
                text(c, msg, px + pw - 50, py + 330, 22, hexc("8a8f99"), a=k)
                continue
            lines = msg.split("\n")
            bw = max(len(s) for s in lines) * 34 + 50
            bh = len(lines) * 44 + 34
            me = who == "me"
            bx = px + pw - bw - 40 if me else px + 110
            c.save()
            c.translate(bx + bw / 2, y + bh / 2)
            c.scale(k, k)
            c.translate(-(bx + bw / 2), -(y + bh / 2))
            bubble(c, bx, y, bw, bh, hexc("a8e07a") if me else hexc("ffffff"), f"bb{who}", me)
            for j, s in enumerate(lines):
                text(c, s, bx + bw / 2, y + 50 + j * 44, 30, INK)
            if not me:
                circle(c, px + 60, y + bh - 24, 26, [hexc("c9a0dc"), hexc("9fc5e8"), hexc("f2b49a")]["abc".index(who)])
            c.restore()
            y += bh + 40
        # 旅行 App
        ax = px + pw
        shape(c, rect(ax, py, pw, ph), hexc("f7f3ea"), "app", lw=0, edge=False)
        text(c, "出发吧 · 拼团", ax + pw / 2, py + 70, 34, INK)
        c.save()
        c.rectangle(ax + 40, py + 130, pw - 80, 420)
        c.clip()
        vgrad(c, py + 130, py + 550, [(0, hexc("3f7fc4")), (1, hexc("cfe8f5"))], ax, ax + pw)
        for i, (x, h_) in enumerate(((ax + 150, 200), (ax + 290, 280), (ax + 430, 190))):
            b = py + 520
            shape(c, [(x - 140, b), (x, b - h_), (x + 140, b)], hexc("8d8a9a"), f"apk{i}", lw=2)
            shape(c, [(x - 50, b - h_ * 0.64), (x, b - h_), (x + 50, b - h_ * 0.64), (x, b - h_ * 0.72)], SNOW, f"aps{i}", lw=1.6)
        shape(c, ell(ax + 290, py + 530, 160, 24, 20), LAKE, "alk", lw=1.6)
        c.restore()
        shape(c, rect(ax + 40, py + 130, pw - 80, 420), None, "apfr", lw=2)
        text(c, "稻城亚丁 · 七日游", ax + pw / 2, py + 620, 40, INK)
        text(c, "海拔 4000m+ · 全程跟团", ax + pw / 2, py + 680, 26, hexc("6a6f7d"))
        text(c, "拼团中 · 还差 1 人", ax + pw / 2, py + 740, 28, RED)
        press = ease_io(prog(t, 5.0, 0.15)) * (1 - ease_io(prog(t, 5.2, 0.2)))
        done = t > 5.3
        bw2 = 360 * (1 - 0.05 * press)
        shape(c, rrect(ax + pw / 2 - bw2 / 2, py + 820, bw2, 100, 50), hexc("4f9a5c") if done else hexc("e8743a"), "btn",
              lw=2.4)
        text(c, "已报名 ✓" if done else "立即报名", ax + pw / 2, py + 884, 38, (1, 1, 1))
        c.restore()
        if 4.4 < t < 5.6:                                  # 手指点下去
            fy = py + 870 + 60 * (1 - ease_io(prog(t, 4.4, 0.6)))
            shape(c, ell(px + pw / 2 + 20, fy + 60, 40, 60, 20), SKIN, "finger", lw=2.4)


# ================================================================ 三、海拔四千米
ROAD = [(90, 1060), (930, 990), (180, 920), (900, 860), (260, 810), (820, 765), (360, 735)]


def _road_at(u):
    seg = len(ROAD) - 1
    f = clamp(u) * seg
    i = min(int(f), seg - 1)
    v = f - i
    (x0, y0), (x1, y1) = ROAD[i], ROAD[i + 1]
    return x0 + (x1 - x0) * v, y0 + (y1 - y0) * v, (1 if x1 > x0 else -1)


def bus(c, x, y, s, d, key):
    c.save()
    c.translate(x, y)
    c.scale(s * d, s)
    with keep():
        shape(c, rrect(-70, -60, 140, 56, 12), hexc("f2f0ea"), key + "b", lw=2.4)
        shape(c, rect(-70, -26, 140, 10), hexc("e07a3a"), key + "s", lw=1.6, amp=0.3)
        for j in range(4):
            shape(c, rect(-58 + j * 30, -52, 22, 18), hexc("9fc5e8"), f"{key}w{j}", lw=1.4, amp=0.3)
        for wx in (-40, 40):
            circle(c, wx, -4, 10, INK)
    c.restore()


def c03_bus(c, t):
    with cam(c, 540, 960, 1.0 + 0.05 * ease_io(t / 6)):
        plateau_bg(c, t, base=760, lake=False, flags=False, yaks=False)
        shape(c, [(-60, 1900), (-60, 760), (300, 700), (700, 690), (1140, 740), (1140, 1900)], hexc("a9b98a"), "slope",
              lw=3)
        line(c, ROAD, "road", 26, hexc("8a8478"))
        line(c, ROAD, "roadc", 2, hexc("f2f0ea"), alpha=0.8)
        u = ease_io(prog(t, 0.2, 5.4))
        x, y, d = _road_at(u)
        bus(c, x, y - 4, 0.9 - 0.35 * u, d, "bus")
        for i in range(3):                                         # 很低的云
            cloud(c, (i * 420 + t * 30) % 1400 - 200, 640 + i * 40, 1.3, f"lc{i}", a=0.7)
        # 路牌
        line(c, [(860, 1240), (860, 1110)], "spost", 8, hexc("6b5a4a"))
        with keep():
            shape(c, rrect(730, 1010, 260, 110, 10), hexc("2f6fb8"), "sign", lw=3)
            text(c, "海拔 4000m", 860, 1080, 40, (1, 1, 1))


# ================================================================ 团里的人都成双成对
def c04_couples(c, t):
    plateau_bg(c, t, base=900)
    shape(c, rect(-20, 1100, W + 40, 600), hexc("a8865f"), "deck", lw=3)
    for i in range(8):
        line(c, [(-10, 1130 + i * i * 10), (W + 10, 1130 + i * i * 10)], f"dk{i}", 1.6, hexc("8c6a48"), alpha=0.6)
    line(c, [(-10, 1060), (W + 10, 1060)], "rail", 5, hexc("6b4a32"))
    for x in range(20, W, 120):
        line(c, [(x, 1060), (x, 1105)], f"rp{x}", 4, hexc("6b4a32"))
    give = ease_io(prog(t, 1.4, 0.7)) * (1 - ease_io(prog(t, 4.0, 0.6)))
    selfie = 4.6 < t < 6.4
    stare = ease_io(prog(t, 5.8, 1.0))
    couple(c, 230, 1180, 1.25, 0, "ca", hearts=1.0, t=t, look=(0.5, -0.4) if stare <= 0 else (1.0, 1.0),
           mouth="laugh")
    couple(c, 860, 1200, 1.25, 1, "cb", hearts=1.0, t=t + 0.5, look=(0.3, -0.5) if stare <= 0 else (-1.0, -1.0),
           mouth="smile")
    gx, gy = 540, 1210
    if 1.8 < t < 4.2:                                           # 帮别人拍照
        arms = [(-34, -150), (-14, -150)]
        girl(c, gx, gy, 1.45, look=-0.8, arms=arms, key="g4", mouth="smile")
        with keep():
            shape(c, rrect(gx - 48 * 1.45, gy - 196 * 1.45, 34, 56, 6), hexc("3a3f4a"), "ophone", lw=2)
    elif selfie:
        girl(c, gx, gy, 1.45, look=0.2, arms=[(-24, -80), (44, -168)], key="g4", mouth="smile")
        with keep():
            shape(c, rrect(gx + 34 * 1.45, gy - 196 * 1.45, 34, 56, 6), hexc("3a3f4a"), "sphone", lw=2)
    else:
        down = ease_io(prog(t, 6.4, 0.6))
        girl(c, gx, gy, 1.45, look=0.0, head_down=8 * down, look_up=-0.8 * down, mouth="flat" if down > 0 else "smile",
             arms=[(-24, -78), (lerp(26, 22, down), lerp(-76, -196, down))], key="g4")
    if give > 0:                                                # 对方递来的手机
        px = lerp(300, gx - 40, give)
        with keep():
            shape(c, rrect(px - 17, 1000 - give * 30, 34, 56, 6), hexc("3a3f4a"), "gphone", lw=2, alpha=1 - (1.8 < t < 4.2))
    for tf in (3.4, 5.9):                                       # 快门闪光
        f = 1 - ease_out(prog(t, tf, 0.35))
        if 0 < f < 1:
            veil(c, (1, 1, 1), 0.35 * f)
    if stare > 0:
        hy = gy - 150 * 1.45
        gaze(c, 230 - 30, 1180 - 152 * 1.25, gx - 30, hy, stare, "z1", show_eye=False)
        gaze(c, 230 + 50, 1180 - 152 * 1.25, gx - 20, hy + 10, stare * 0.9, "z2", show_eye=False)
        gaze(c, 860 - 40, 1200 - 152 * 1.25, gx + 30, hy, stare, "z3", show_eye=False)
        gaze(c, 860 + 40, 1200 - 152 * 1.25, gx + 20, hy + 10, stare * 0.8, "z4", show_eye=False)


# ================================================================ 高原反应
def c05_altitude(c, t):
    fill_all(c, hexc("39415a"))
    # 窗外：夜里的雪山
    c.save()
    c.rectangle(140, 220, 420, 420)
    c.clip()
    vgrad(c, 220, 640, [(0, hexc("141b33")), (1, hexc("3b4b7a"))])
    r = random.Random(6)
    for i in range(14):
        star(c, r.uniform(140, 560), r.uniform(230, 460), r.uniform(2, 3.5), 0.6 + 0.4 * math.sin(t * 3 + i))
    shape(c, [(120, 640), (300, 430), (420, 540), (480, 470), (600, 640)], hexc("6e7590"), "nmt", lw=2.4)
    shape(c, [(255, 482), (300, 430), (340, 470), (300, 466)], hexc("dfe6f0"), "nmts", lw=1.8)
    c.restore()
    shape(c, rect(140, 220, 420, 420), None, "nwin", lw=6)
    line(c, [(350, 220), (350, 640)], "nwm", 5)
    # 墙：隔壁的笑声
    shape(c, rect(800, 120, 40, 1100), hexc("2e3449"), "wall", lw=3)
    glow(c, 960, 700, 260, hexc("ffd59a"), 0.35 + 0.1 * math.sin(t * 3))
    with keep():
        for k in range(4):
            ph = (t * 0.5 + k / 4) % 1
            a = math.sin(math.pi * ph)
            text(c, ["哈哈", "♡", "慢点喝水", "哈哈哈"][k], 920 + math.sin(ph * 5 + k) * 30, 900 - ph * 500, 34,
                 hexc("f6d6a8"), a=0.8 * a)
    # 床
    shape(c, rect(80, 1040, 660, 60), hexc("e6e0d4"), "bed", lw=3)
    shape(c, rect(80, 1100, 660, 140), hexc("7f8aa8"), "bedb", lw=3)
    shape(c, rrect(100, 960, 170, 80, 26), hexc("f2efe8"), "pillow", lw=2.4)
    breath = math.sin(t * 2.2)
    gx, gy = 430, 1040
    girl(c, gx, gy, 1.55, sit=True, crouch=True, hat=False, mouth="sad", head_down=6 + breath * 2, look=0.2,
         arms=[(-14, -92), (14, -92)], eyes_closed=(t % 2.4) < 1.2, key="g5")
    o2can(c, gx + 2, gy + (-86 + 52) * 1.55 - 2, 1.5, "can5")
    # 晕眩的圈
    hy = gy + (52 - 150) * 1.55 - 70
    with keep():
        pts = []
        for i in range(60):
            a = i / 60 * 4 * math.pi + t * 3
            rr = 8 + i * 0.9
            pts.append((gx + math.cos(a) * rr * 1.6, hy + math.sin(a) * rr * 0.5))
        line(c, pts, "dizzy", 2.2, hexc("c8cde0"), alpha=0.8)
        for k in range(3):
            a = t * 2.5 + k * 2.1
            star(c, gx + math.cos(a) * 70, hy + math.sin(a) * 18, 5, 0.9, hexc("f6e08a"))


# ================================================================ 说不清的事
def c06_thread(c, t):
    plateau_bg(c, t, base=860, dusk=0.6, flags=True, yaks=False)
    shape(c, rect(-20, 1080, W + 40, 700), hexc("9fb08a"), "pgr", lw=3)
    lean = ease_io(prog(t, 1.6, 1.0)) * (1 - ease_io(prog(t, 3.8, 0.9)))
    back = ease_io(prog(t, 3.0, 0.6))
    turn = t > 5.0
    wx, mx = 260, lerp(390, 520, lean)
    gx = lerp(800, 850, back)
    if turn:
        gx = lerp(850, 1260, ease_in(prog(t, 5.2, 1.8)))
    s = 1.4
    local(c, wx, 1200, s, "tw", COUPLE_COLS[2][0], hexc("2f2a28"), "bang_short", look=0.6, arms=[(-24, -78), (40, -72)],
          mouth="smile")
    local(c, mx, 1200, s, "tm", COUPLE_COLS[2][1], hexc("3a3a3a"), "short", look=1.0 if t > 0.8 else -0.6,
          arms=[(-40, -72), (lerp(24, 78, lean), lerp(-78, -110, lean))], mouth="smile")
    # 红线：连着两人牵着的手
    ax, ay = wx + 40 * s, 1200 - 72 * s
    bx, by = mx - 40 * s, 1200 - 72 * s
    taut = lean
    sag = 40 * (1 - taut) + 4
    trem = math.sin(t * 50) * 4 * taut
    with keep():
        pts = [(ax, ay), ((ax + bx) / 2, (ay + by) / 2 + sag + trem), (bx, by)]
        line(c, pts, "rthread", 4 - 1.6 * taut, mix(RED, hexc("ff3b3b"), taut))
    if lean > 0.05:                                              # 递来的氧气
        cx_ = lerp(mx + 24 * s, mx + 78 * s, lean)
        o2can(c, cx_, 1200 - 104 * s, 1.1, "can6")
    if not turn:
        push = back * (1 - ease_io(prog(t, 4.4, 0.5)))
        girl(c, gx, 1200, s, look=-0.8, mouth="flat", key="g6",
             arms=[(lerp(-24, -66, push), lerp(-78, -110, push)), (24, -78)])
    else:
        girl(c, gx, 1200, s, view="back", walk=t * 8, mouth="flat", key="g6")
    if t > 4.6:                                                   # 红线重新绷好
        heart(c, (ax + bx) / 2, ay + sag - 30, 12, ease_out(prog(t, 4.6, 0.6)))


# ================================================================ 三、并不浪漫（漫画页）
def p_alley(c, t, w, h):
    fill_all(c, hexc("3a3d4a"))
    shape(c, [(0, 0), (300, 120), (300, h - 120), (0, h)], hexc("4d5160"), "awl", lw=2.6)
    shape(c, [(w, 0), (w - 300, 120), (w - 300, h - 120), (w, h)], hexc("4d5160"), "awr", lw=2.6)
    shape(c, rect(300, 120, w - 600, h - 240), hexc("2a2d38"), "aend", lw=2.4)
    shape(c, [(300, h - 120), (w - 300, h - 120), (w, h), (0, h)], hexc("5a5d68"), "aflr", lw=2.4)
    glow(c, 480, 150, 220, hexc("ffd59a"), 0.45)
    line(c, [(480, 120), (480, 160)], "alamp", 3)
    with grade(dark=0.2):
        for i, (x, sc) in enumerate(((150, 1.6), (820, 1.9))):        # 墙上被拉长的影子
            c.save()
            c.translate(x, h - 80)
            c.scale(1.0, 2.2)
            silhouette(c, 0, 0, sc, f"ash{i}", col=hexc("15161c"), a=0.55, walk=t * 2 + i)
            c.restore()
    girl(c, 500, h - 110, 1.15, hat=True, mouth="flat", look=-0.3, look_up=-0.6, head_down=4,
         arms=[(-26, -76), (18, -104)], key="ga")
    suitcase(c, 430, h - 108, 0.7, "asu")
    # 电量 3%
    blink = 0.5 + 0.5 * math.sin(t * 8)
    with keep():
        shape(c, rrect(700, 40, 200, 90, 14), hexc("f2f0ea"), "batb", lw=3)
        shape(c, rect(900, 66, 14, 38), hexc("f2f0ea"), "batn", lw=2)
        shape(c, rect(712, 52, 14, 66), RED, "batl", lw=1.4, amp=0.2, alpha=0.4 + 0.6 * blink)
        text(c, "3%", 812, 106, 44, RED)


def c07_hard(c, t):
    fill_all(c, hexc("e8e2d6"))
    panel(c, 60, 150, 960, 300, ease_back(prog(t, 0.15, 0.5)), "hp1", p_suitcase, t, rot=-0.008)
    panel(c, 60, 500, 960, 600, ease_back(prog(t, 5.0, 0.5)), "hp2", p_alley, t - 5.0, rot=0.006)


def p_noodle_eyes(c, t, w, h):
    p_noodle(c, t, w, h)
    for i, x in enumerate((780, 870)):
        silhouette(c, x, 300, 1.0, f"nd{i}", a=0.7)
    k = ease_io(prog(t, 0.8, 1.2))
    gaze(c, 770, 140, 340, 130, k, "nz1", a=0.7, show_eye=False)
    gaze(c, 860, 140, 350, 150, k * 0.8, "nz2", a=0.7, show_eye=False)


def p_sunset(c, t, w, h):
    vgrad(c, 0, h, [(0, hexc("e9a58a")), (0.6, hexc("f6d6b0")), (1, hexc("f2e6cf"))], 0, w)
    sy = 170 + t * 6
    glow(c, w / 2, sy, 200, hexc("ffe2a0"), 0.7)
    shape(c, ell(w / 2, sy, 60, 60, 20), hexc("f8c27a"), "sun", lw=2)
    shape(c, rect(-10, 190, w + 20, 200), hexc("7f9cb3"), "sea", lw=2.4)
    for k in range(4):
        line(c, [(w / 2 - 80 + k * 10, 205 + k * 14), (w / 2 + 80 - k * 10, 205 + k * 14)], f"sr{k}", 2,
             hexc("f8d29a"), alpha=0.8)
    shape(c, rect(-10, 250, w + 20, 100), hexc("d9c7a3"), "sand", lw=2.4)
    shape(c, rect(380, 238, 200, 14), hexc("8c5a3c"), "sbench", lw=2.4)
    girl(c, 480, 238, 0.9, view="back", sit=True, hat=True, key="gss")
    for i, x in enumerate((150, 820)):                       # 远处一对对的人
        local(c, x, 280, 0.55, f"ssa{i}", hexc("6b5a5a"), view="back", alpha=0.6)
        local(c, x + 34, 280, 0.55, f"ssb{i}", hexc("5a5a6b"), view="back", alpha=0.6)


GLYPHS = 6


def p_city_signs(c, t, w, h):
    p_tall(c, t, w, h)
    r = random.Random(13)
    with keep():
        for i in range(9):
            x = r.uniform(40, w - 160)
            y = r.uniform(30, h - 140)
            col = [hexc("c9473b"), hexc("3f6fb5"), hexc("e8c040"), hexc("4f9a5c")][i % 4]
            shape(c, rect(x, y, 110, 46), col, f"sg{i}", lw=2, amp=0.4)
            for j in range(3):                                  # 看不懂的字
                gx = x + 22 + j * 32
                kind = (i + j) % 3
                if kind == 0:
                    shape(c, ell(gx, y + 22, 7, 7, 10), None, f"sgg{i}{j}", lw=2, amp=0.3)
                    line(c, [(gx + 9, y + 12), (gx + 9, y + 34)], f"sgh{i}{j}", 2, (1, 1, 1))
                elif kind == 1:
                    line(c, [(gx - 8, y + 30), (gx - 2, y + 14), (gx + 4, y + 30), (gx + 10, y + 14)], f"sgg{i}{j}", 2,
                         (1, 1, 1))
                else:
                    line(c, [(gx - 6, y + 16), (gx + 8, y + 16), (gx - 6, y + 32), (gx + 8, y + 32)], f"sgg{i}{j}", 2,
                         (1, 1, 1))


def c09_alone(c, t):
    fill_all(c, hexc("e8e2d6"))
    panel(c, 60, 130, 960, 330, ease_back(prog(t, 0.15, 0.5)), "ap1", p_noodle_eyes, t, rot=-0.006)
    panel(c, 60, 500, 960, 330, ease_back(prog(t, 3.2, 0.5)), "ap2", p_sunset, t - 3.2, rot=0.006)
    panel(c, 60, 870, 960, 360, ease_back(prog(t, 6.2, 0.5)), "ap3", p_city_signs, t - 6.2, rot=-0.004)


# ================================================================ 那些眼神
def c10_eyes(c, t):
    fill_all(c, hexc("cfd2d6"))
    glow(c, 540, 900, 600, hexc("eef0f2"), 0.5)
    shrink = ease_io(prog(t, 0.6, 3.0))
    gx, gy = 540, 1150
    s = lerp(1.9, 1.5, shrink)
    r = random.Random(30)
    n = 14
    for i in range(n):
        a = i / n * 2 * math.pi + r.uniform(-0.15, 0.15)
        d = r.uniform(380, 470)
        ex, ey = gx + math.cos(a) * d, gy - 190 + math.sin(a) * d * 0.9
        k = ease_out(prog(t, 0.2 + i * 0.16, 0.8))
        if k <= 0:
            continue
        lk = (-math.cos(a), -math.sin(a))
        eye(c, ex, ey, 1.4 * k, f"ey{i}", a=k, look=lk)
        gaze(c, ex, ey, gx, gy - 160 * s, ease_io(prog(t, 0.6 + i * 0.16, 1.2)), f"eg{i}", a=0.6)
    girl(c, gx, gy, s, mouth="flat", head_down=4 + 8 * shrink, look_up=-0.9 * shrink,
         arms=[(-14, -96), (lerp(14, 22, shrink), lerp(-96, -196, shrink))], key="g10")


# ================================================================ 四、等
def train_at(c, x, key, y0=600, y1=900, col=hexc("8c99a6")):
    for k in range(3):
        cx = x + k * 640
        shape(c, rrect(cx, y0, 620, y1 - y0, 20), col, f"{key}{k}", lw=3)
        for j in range(5):
            shape(c, rect(cx + 40 + j * 115, y0 + 50, 80, 90), hexc("d8e0e8"), f"{key}w{k}{j}", lw=2)
        line(c, [(cx + 10, y1 - 60), (cx + 610, y1 - 60)], f"{key}s{k}", 6, hexc("c9553f"))


def c11_platform(c, t):
    platform_bg(c, t, clock_speed=8.0)
    arrive = ease_out(prog(t, 0.0, 1.3))
    leave = ease_in(prog(t, 4.3, 1.5))
    tx = lerp(W + 100, -700, arrive) - leave * 2400
    train_at(c, tx, "pt")
    # 下车的人，都是一对一对
    for i in range(3):
        u = prog(t, 1.4 + i * 0.6, 2.6)
        if 0 < u < 1:
            x = lerp([140, 820, 260][i], [-300, 1380, -300][i], ease_in(u))
            d = -1 if i % 2 else 1
            for j in range(2):
                silhouette(c, x + j * 52, 1150 + i * 30, 1.4, f"pp{i}{j}", walk=t * 7 + j, a=0.8)
            heart(c, x + 26, 1150 + i * 30 - 230, 8, 0.8 * math.sin(math.pi * u))
            _ = d
    pull(c, 540, 1200, 1.5, "g11", mouth="flat", look=0.0)


def c12_wait(c, t):
    s10_bench(c, t * 1.0)
    r = random.Random(17)
    with keep():
        if t < 1.6:                                              # 春：花瓣
            for i in range(18):
                x = (r.uniform(0, W) + t * 120) % W
                y = (r.uniform(0, 900) + t * 160) % 1300
                shape(c, ell(x, y, 8, 5, 8), hexc("f6c2cc"), f"pt{i}", lw=1.2, amp=0.3, alpha=1 - prog(t, 1.0, 0.6))
        if t > 4.0:                                              # 冬：雪
            a = ease_io(prog(t, 4.0, 0.8))
            for i in range(50):
                x = (r.uniform(0, W) + math.sin(t + i) * 30) % W
                y = (r.uniform(0, 1300) + t * 90) % 1300
                circle(c, x, y, r.uniform(3, 6), (1, 1, 1), 0.85 * a)
            shape(c, rrect(250, 1066, 580, 18, 8), (1, 1, 1), "bsnow", lw=1.4, amp=0.4, alpha=a)
    for i, mo in enumerate(("3月", "6月", "9月", "12月")):       # 日历一页页飞走
        u = prog(t, 0.4 + i * 1.3, 1.6)
        if 0 < u < 1:
            c.save()
            c.translate(lerp(980, -150, u), 260 + math.sin(u * 6 + i) * 60)
            c.rotate(u * 4)
            with keep():
                shape(c, rect(-50, -40, 100, 80), hexc("f4efe6"), f"cp{i}", lw=2)
                shape(c, rect(-50, -40, 100, 20), hexc("c0503c"), f"cph{i}", lw=2)
                text(c, mo, 0, 26, 30, INK)
            c.restore()


def c12b_notes(c, t):
    with cam(c, 260, 640, 1.55):
        room(c, t, sky="grey", hat_hook=True, hat_dust=lerp(0.4, 1.0, ease_io(t / 4)), map_age=0.4, chair=False)
        r = random.Random(23)
        with keep():
            for i in range(9):
                k = ease_back(prog(t, 0.2 + i * 0.32, 0.35))
                if k <= 0:
                    continue
                x, y = 120 + (i % 3) * 95 + r.uniform(-10, 10), 530 + (i // 3) * 68 + r.uniform(-6, 6)
                c.save()
                c.translate(x, y)
                c.rotate(r.uniform(-0.2, 0.2))
                c.scale(k, k)
                shape(c, rect(-40, -26, 80, 52), hexc("f7e27a"), f"sn{i}", lw=1.6, amp=0.4)
                text(c, "明年再去", 0, 6, 17, INK)
                c.restore()


# ================================================================ 五、怕
def c13_aging(c, t):
    s14_aging(c, min(t * 0.85, 4.9))


def c14_scale(c, t):
    s12_scale(c, t)


def c15_old(c, t):
    if t < 6.8:
        with cam(c, 620, 820, 1.0 + 0.03 * ease_io(t / 6.8)):
            room(c, t, sky="grey", curtain=0.2, hat_hook=False, map_age=1.0, web=0.6, chair=True)
            shape(c, rect(900, 1010, 150, 20), hexc("8c5a3c"), "ch2", lw=3)
            person(c, 975, 1010, 1.5, sit=True, coat=hexc("8fa0b3"), hair=hexc("6b5a4a"), hair_style="short", hat=False,
                   pack=False, look=-0.8, key="mate", age=0.9, mouth="smile")
            # 桌上两张机票
            shape(c, rect(800, 930, 90, 16), hexc("8c5a3c"), "otab", lw=2.6)
            line(c, [(845, 946), (845, 1100)], "otabl", 5, hexc("7a4d33"))
            for k in range(2):
                c.save()
                c.translate(830 + k * 30, 922 - k * 6)
                c.rotate(-0.15 + k * 0.25)
                with keep():
                    shape(c, rect(-34, -16, 68, 30), hexc("f4f2ec"), f"tk{k}", lw=1.6, amp=0.3)
                    line(c, [(-10, -2), (14, -2)], f"tkp{k}", 2, hexc("3f6fb5"))
                c.restore()
            girl(c, 712, 1000, 1.6, sit=True, hat=False, age=1.0, look=-0.6, look_up=0.3, head_down=4, mouth="flat",
                 arms=[(-14, -40), (14, -40)], key="gold")
            with nokeep(), grade(sat=0.0):                        # 膝上褪色的草帽
                hat_item(c, 712, 1020, 0.9, "oldhat")
    else:
        f = ease_io(prog(t, 6.8, 0.4))
        fill_all(c, hexc("efe4cc"))
        beat = (t * 1.25) % 1
        pulse = math.exp(-beat * 7)
        with keep():
            for k in range(3):
                rr = 220 + k * 140 + beat * 120
                shape(c, ell(540, 820, rr, rr, 40), None, f"hb{k}", lw=3, alpha=(1 - beat) * 0.5 * f)
        s = 2.4 * (1 + 0.025 * pulse)
        girl(c, 540, 1240, s, hat=False, look=0.0, mouth="flat", arms=[(-16, -100), (16, -100)], key="gy", look_up=0.2)
        with keep():
            hat_item(c, 540, 1240 - 112 * s, 1.6 * (1 + 0.025 * pulse), "yhat")
        veil(c, (1, 1, 1), 1 - f)


# ================================================================ 六、一个人出发
def c16_go(c, t):
    street_bg(c, t, base=760, rain_a=0.0, seed=5)
    glow(c, 900, 300, 700, hexc("fff0c0"), 0.5)
    gx = 420
    if t < 2.6:
        blow = ease_out(prog(t, 0.6, 1.0))
        on = ease_io(prog(t, 1.7, 0.8))
        hy = lerp(1150 - 120 * 1.6, 1150 - 160 * 1.6, on)
        girl(c, gx, 1150, 1.6, hat=on > 0.98, look=0.3, mouth="o" if 0.6 < t < 1.4 else "smile",
             arms=[(-14, -110 - 50 * on), (40 - 30 * on, -120 - 40 * on)], key="g16")
        suitcase(c, gx + 130, 1152, 0.95, "su16", handle=0.3)
        if on < 0.98:
            hat_item(c, gx + lerp(60, 0, on) * 1.6 / 1.6, hy, 1.5, "h16", dust=1 - blow)
        r = random.Random(3)
        for i in range(24):                                    # 吹掉的灰
            u = prog(t, 0.6 + r.uniform(0, 0.3), 1.2)
            if 0 < u < 1:
                circle(c, gx + 60 + u * r.uniform(80, 260), hy + r.uniform(-30, 30) - u * r.uniform(0, 80),
                       2.4 * (1 - u) + 1, hexc("9c968c"), 0.8 * (1 - u))
    else:
        x = lerp(gx, 1300, ease_in(prog(t, 2.8, 2.2)))
        pull(c, x, 1150, 1.6, "g16w", walk=t * 9, mouth="smile")


# ================================================================ 不知不觉，去了很多地方
MAP_BOX = (170, 200, 920, 1060)
LON0, LON1, LAT0, LAT1 = 98.0, 130.0, 22.0, 48.0
PLACES = [("稻城亚丁", 100.3, 29.0, "peak", 1), ("苏州", 120.6, 31.3, "bridge", -1), ("哈尔滨", 126.6, 45.8, "snow", -1),
          ("东北", 123.4, 41.8, "pine", -1), ("厦门", 118.1, 24.5, "palm", 1), ("上海", 122.4, 31.0, "tower", 1),
          ("西安", 108.9, 34.3, "gate", 1)]
EXTRA = [(113.3, 23.1), (104.1, 30.6), (116.4, 39.9), (120.4, 36.1), (110.3, 25.3), (102.7, 25.0)]


def geo(lon, lat):
    x0, y0, x1, y1 = MAP_BOX
    return x0 + (lon - LON0) / (LON1 - LON0) * (x1 - x0), y0 + (LAT1 - lat) / (LAT1 - LAT0) * (y1 - y0)


def place_icon(c, kind, x, y, key):
    with keep():
        if kind == "peak":
            shape(c, [(x - 26, y), (x, y - 36), (x + 26, y)], ROCK, key, lw=2)
            shape(c, [(x - 10, y - 22), (x, y - 36), (x + 10, y - 22)], SNOW, key + "s", lw=1.4)
            line(c, [(x + 22, y), (x + 22, y - 44)], key + "fp", 2)
            shape(c, [(x + 22, y - 44), (x + 44, y - 38), (x + 22, y - 32)], RED, key + "ff", lw=1.4)
        elif kind == "bridge":
            line(c, [(x - 26, y), (x - 14, y - 16), (x + 14, y - 16), (x + 26, y)], key, 3, hexc("8c8a86"))
            shape(c, ell(x, y, 12, 10, 12, math.pi, 2 * math.pi), hexc("9fc5e8"), key + "w", lw=1.4)
        elif kind == "snow":
            for k in range(3):
                a = k * math.pi / 3
                line(c, [(x - math.cos(a) * 18, y - 18 - math.sin(a) * 18), (x + math.cos(a) * 18, y - 18 + math.sin(a) * 18)],
                     f"{key}{k}", 2.4, hexc("6fa8dc"))
        elif kind == "pine":
            shape(c, [(x - 18, y - 4), (x, y - 40), (x + 18, y - 4)], hexc("4f7a5c"), key, lw=1.8)
            shape(c, [(x - 10, y - 26), (x, y - 40), (x + 10, y - 26)], SNOW, key + "s", lw=1.2)
        elif kind == "palm":
            line(c, [(x, y), (x + 4, y - 36)], key, 3, hexc("8c6a48"))
            for k in range(4):
                a = math.pi * (1.1 + k * 0.27)
                line(c, [(x + 4, y - 36), (x + 4 + math.cos(a) * 22, y - 36 + math.sin(a) * 10 + 8)], f"{key}{k}", 2.6,
                     hexc("4f9a5c"))
        elif kind == "tower":
            line(c, [(x, y), (x, y - 48)], key, 2.4)
            for yy, rr in ((-12, 8), (-30, 6)):
                shape(c, ell(x, y + yy, rr, rr, 10), hexc("d97aa0"), f"{key}{yy}", lw=1.4)
        elif kind == "gate":
            shape(c, rect(x - 24, y - 20, 48, 20), hexc("a8865f"), key, lw=1.8)
            shape(c, [(x - 30, y - 20), (x, y - 38), (x + 30, y - 20)], hexc("6b4a32"), key + "r", lw=1.8)


def map_scene(c, t):
    fill_all(c, hexc("e9dcc0"))
    unroll = ease_io(prog(t, 0.0, 0.7))
    x0, y0, x1, y1 = MAP_BOX
    c.save()
    c.rectangle(0, 0, W, y0 - 40 + (y1 - y0 + 120) * unroll)
    c.clip()
    shape(c, rect(x0 - 50, y0 - 40, x1 - x0 + 100, y1 - y0 + 120), hexc("f4e7c8"), "mapb", lw=3)
    for k in range(5):                                            # 东边的海
        yy = 560 + k * 110
        line(c, [(x1 - 90 + (k % 2) * 20, yy), (x1 - 60, yy - 8), (x1 - 30, yy), (x1, yy - 8)], f"wv{k}", 2, hexc("9fc5e8"))
    for k in range(4):                                            # 西边的山
        mx, my = x0 + 40 + (k % 2) * 70, 400 + k * 140
        line(c, [(mx - 24, my), (mx, my - 26), (mx + 24, my)], f"mm{k}", 2, hexc("b7a888"))
    cx, cy = x1 - 40, y0 + 40                                     # 指南针
    line(c, [(cx, cy - 34), (cx, cy + 34)], "cmp1", 2, hexc("b48a4f"))
    line(c, [(cx - 34, cy), (cx + 34, cy)], "cmp2", 2, hexc("b48a4f"))
    text(c, "N", cx, cy - 44, 24, hexc("b48a4f"))
    # 行程虚线
    pts = [geo(lon, lat) for _, lon, lat, _, _ in PLACES]
    step = 0.85
    T0 = 0.9
    for i in range(len(pts) - 1):
        u = prog(t, T0 + i * step + 0.25, step - 0.25)
        if u <= 0:
            continue
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        mx, my = (ax + bx) / 2, (ay + by) / 2 - 80
        n = 18
        for j in range(n):
            v0, v1 = j / n, (j + 0.55) / n
            if v0 > u:
                break
            v1 = min(v1, u)
            seg = []
            for v in (v0, v1):
                seg.append(((1 - v) ** 2 * ax + 2 * (1 - v) * v * mx + v * v * bx,
                            (1 - v) ** 2 * ay + 2 * (1 - v) * v * my + v * v * by))
            with keep():
                line(c, seg, f"dash{i}{j}", 3, hexc("c9473b"), alpha=0.8, amp=0.4)
    for i, (name, lon, lat, kind, side) in enumerate(PLACES):
        k = ease_back(prog(t, T0 + i * step, 0.4))
        if k <= 0:
            continue
        x, y = pts[i]
        with keep():
            glow(c, x, y, 90 * k, hexc("ffd27a"), 0.7)
            circle(c, x, y, 10 * k, hexc("e07a3a"))
            c.save()
            c.translate(x + side * 62, y - 4)
            c.scale(1.5 * min(k, 1.0), 1.5 * min(k, 1.0))
            place_icon(c, kind, 0, 0, f"pi{i}")
            c.restore()
            text(c, name, x + side * 14, y + 48, 36 * k, INK, anchor="r" if side < 0 else "l")
    for i, (lon, lat) in enumerate(EXTRA):                           # 还有很多地方……
        k = ease_back(prog(t, T0 + len(PLACES) * step + i * 0.18, 0.3))
        if k > 0:
            x, y = geo(lon, lat)
            with keep():
                glow(c, x, y, 50 * k, hexc("ffd27a"), 0.6)
                circle(c, x, y, 7 * k, hexc("e8a050"))
    c.restore()
    # 越叠越高的车票
    with keep():
        n = int(clamp((t - T0) / step + 1, 0, len(PLACES))) + int(clamp((t - T0 - len(PLACES) * step) / 0.18, 0, 6))
        for k in range(n):
            c.save()
            c.translate(170 + math.sin(k * 1.7) * 8, 1200 - k * 14)
            c.rotate(math.sin(k * 2.3) * 0.12)
            shape(c, rect(-70, -22, 140, 40), hexc("f4f2ec") if k % 2 else hexc("dfe9f5"), f"tick{k}", lw=1.6, amp=0.3)
            line(c, [(-36, -2), (36, -2)], f"tickl{k}", 2, hexc("3f6fb5") if k % 2 else hexc("c9473b"))
            c.restore()


def road_scene(c, t):
    vgrad(c, 0, 900, [(0, hexc("f3c79a")), (1, hexc("fbe6c4"))])
    glow(c, 540, 760, 500, hexc("fff0c0"), 0.8)
    shape(c, ell(540, 820, 90, 90, 24), hexc("fbe2a0"), "rsun", lw=2)
    shape(c, hill_pts(860, 30, 0.006, 1.2), hexc("b5c98f"), "rh", lw=3)
    shape(c, [(470, 870), (610, 870), (1000, 1800), (80, 1800)], hexc("d9c39a"), "rroad", lw=3)
    with keep():
        for k in range(8):
            v = ((k / 8) + t * 0.08) % 1
            y = lerp(880, 1700, v ** 1.6)
            w_ = lerp(4, 40, v ** 1.6)
            line(c, [(540, y), (540, y + w_ * 1.4)], f"rl{k}", lerp(2, 8, v), hexc("f4efe4"))
    u = ease_out(prog(t, 0.0, 6.0))
    y = lerp(1300, 980, u)
    s = lerp(1.3, 0.55, u)
    girl(c, 540, y, s, view="back", walk=t * 8, hat=True, key="groad")
    suitcase(c, 540 + 70 * s, y + 2 * s, 0.6 * s, "rsu", tilt=-0.12)


def c17_map(c, t):
    swap = ease_io(prog(t, 8.2, 1.2))
    if swap < 1:
        map_scene(c, t)
    if swap > 0:
        with group_alpha(c, swap):
            road_scene(c, t - 8.2)


_STILL = {}


def map_still():
    if "s" not in _STILL:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(120.0)
        with grade(sat=1.0, dark=0.0, warm=0.0):
            map_scene(cc, 7.9)
        _STILL["s"] = surf
    return _STILL["s"]


def outro(c, t):
    book_outro(c, t, map_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第二章 · 完")

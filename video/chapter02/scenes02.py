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
    """高原：三座雪山（可选：湖、经幡、牦牛；第二章不展示具体地点，默认只用雪山）。"""
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
CHAT = [(0.3, "me", "周末想出去走走，\n有人一起吗？"), (1.4, "a", "最近太忙了……"), (2.4, "b", "下次吧"),
        (3.3, "c", "去不了诶"), (4.0, "read", "已读")]


def bubble(c, x, y, w, h, col, key, me):
    shape(c, rrect(x, y, w, h, 18), col, key, lw=2, amp=0.4)
    tx = x + w - 6 if me else x + 6
    shape(c, [(tx, y + h - 22), (tx + (18 if me else -18), y + h - 6), (tx + (-4 if me else 4), y + h - 8)], col, key + "t",
          lw=2, amp=0.3)


def c02_ask(c, t):
    fill_all(c, hexc("d9d6ce"))
    px, py, pw, ph = 250, 140, 580, 1060
    slide = ease_io(prog(t, 5.2, 0.6))
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
        c.restore()
        shape(c, rect(ax + 40, py + 130, pw - 80, 420), None, "apfr", lw=2)
        text(c, "高原七日游", ax + pw / 2, py + 620, 44, INK)
        text(c, "海拔 4000m+ · 全程跟团", ax + pw / 2, py + 680, 26, hexc("6a6f7d"))
        text(c, "拼团中 · 还差 1 人", ax + pw / 2, py + 740, 28, RED)
        press = ease_io(prog(t, 7.6, 0.15)) * (1 - ease_io(prog(t, 7.8, 0.2)))
        done = t > 7.9
        bw2 = 360 * (1 - 0.05 * press)
        shape(c, rrect(ax + pw / 2 - bw2 / 2, py + 820, bw2, 100, 50), hexc("4f9a5c") if done else hexc("e8743a"), "btn",
              lw=2.4)
        text(c, "已报名 ✓" if done else "立即报名", ax + pw / 2, py + 884, 38, (1, 1, 1))
        c.restore()
        if 7.0 < t < 8.2:                                  # 手指点下去
            fy = py + 870 + 60 * (1 - ease_io(prog(t, 7.0, 0.6)))
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
def phone_at(c, x, y, s, key, glow_a=0.0):
    with keep():
        if glow_a > 0:
            glow(c, x, y, 40 * s, hexc("dfeaff"), glow_a)
        shape(c, rrect(x - 11 * s, y - 18 * s, 22 * s, 36 * s, 4 * s), hexc("3a3f4a"), key, lw=2, amp=0.2)
        shape(c, rect(x - 8 * s, y - 14 * s, 16 * s, 26 * s), hexc("bfe0ff"), key + "s", lw=0, edge=False, alpha=0.9)


def viewpoint_bg(c, t):
    """观景台：雪山、远处的步道和小小的游客、停着的大巴、飞鸟、导游的小旗子、望远镜。"""
    plateau_bg(c, t, base=900, lake=False, flags=False, yaks=False)
    # 远处的步道和游客
    path = [(-40, 860), (200, 835), (420, 850), (640, 828), (860, 842), (1120, 820)]
    line(c, path, "trail", 6, hexc("c9bfa8"))
    r = random.Random(12)
    for i in range(9):
        u = (r.uniform(0, 1) + t * 0.02 * (1 if i % 2 else -1)) % 1
        x = lerp(-20, 1100, u)
        silhouette(c, x, 842 + math.sin(u * 9) * 8, 0.42, f"ft{i}", walk=t * 5 + i, a=0.6)
    # 停着的大巴
    bus(c, 140, 900, 0.75, 1, "pbus")
    # 飞鸟
    for i in range(4):
        bx = (300 + i * 140 + t * 40) % 1200 - 60
        by = 300 + i * 30 + math.sin(t * 2 + i) * 10
        w_ = 12 + 4 * math.sin(t * 8 + i)
        line(c, [(bx - 14, by - w_ * 0.5), (bx, by), (bx + 14, by - w_ * 0.5)], f"bird{i}", 2.2, hexc("3a3f4a"))
    # 导游举着小旗子，带着另一队人走过
    gx_, gy_ = 640 + t * 16, 1040
    for i in range(3):
        silhouette(c, gx_ - 50 - i * 40, gy_, 0.65, f"tour{i}", walk=t * 6 + i, a=0.5)
    local(c, gx_, gy_, 0.7, "guide", hexc("c9473b"), hexc("2f2a28"), "short", hat=False, look=0.6, mouth="laugh",
          walk=t * 6, arms=[(-24, -78), (20, -150)])
    line(c, [(gx_ + 14, gy_ - 105), (gx_ + 14, gy_ - 175)], "gpole", 3, hexc("6b4a32"))
    with keep():
        sw = math.sin(t * 5) * 5
        shape(c, [(gx_ + 14, gy_ - 175), (gx_ + 48 + sw, gy_ - 166), (gx_ + 14, gy_ - 156)], hexc("e8c040"), "gflag", lw=2)
    # 观景台
    shape(c, rect(-20, 1100, W + 40, 700), hexc("a8865f"), "deck", lw=3)
    for i in range(9):
        line(c, [(-10, 1125 + i * i * 9), (W + 10, 1125 + i * i * 9)], f"dk{i}", 1.6, hexc("8c6a48"), alpha=0.6)
    line(c, [(-10, 1050), (W + 10, 1050)], "rail", 6, hexc("6b4a32"))
    line(c, [(-10, 1080), (W + 10, 1080)], "rail2", 3, hexc("6b4a32"))
    for x in range(20, W, 110):
        line(c, [(x, 1045), (x, 1104)], f"rp{x}", 5, hexc("6b4a32"))
    # 望远镜
    line(c, [(990, 1104), (990, 1010)], "tsp", 6, hexc("5a5d66"))
    shape(c, rrect(940, 975, 64, 40, 10), hexc("6f7a8a"), "tsc", lw=2.4)
    shape(c, ell(940, 995, 8, 16, 10), hexc("3a3f4a"), "tse", lw=1.6)
def c04_couples(c, t):
    viewpoint_bg(c, t)
    s = 1.5
    gy = 1215
    gx = 560
    # 情侣 A：男生过来递手机、回去摆姿势、再过来拿回手机
    ax, bx0 = 200, 290
    walk1 = ease_io(prog(t, 0.8, 0.8)) * (1 - ease_io(prog(t, 1.9, 0.7)))
    walk2 = ease_io(prog(t, 3.9, 0.5)) * (1 - ease_io(prog(t, 4.5, 0.6)))
    bx = lerp(bx0, 400, max(walk1, walk2))
    moving = (0.8 < t < 2.6) or (3.9 < t < 5.1)
    stare = ease_io(prog(t, 6.2, 1.0))
    together = bx < bx0 + 8
    look_b = 1.0 if moving else (0.4 if stare <= 0 else 1.0)
    local(c, ax, gy, s, "ca_a", COUPLE_COLS[0][0], hexc("2f2a28"), "bang_short",
          look=0.5 if stare <= 0 else 1.0, mouth="laugh", arms=[(-24, -78), (30, -70)] if together else None)
    b_arms = [(-30, -70), (24, -78)] if together else [(-24, -78), (48, -100)]
    local(c, bx, gy, s, "ca_b", COUPLE_COLS[0][1], hexc("3a3a3a"), "short", look=look_b, mouth="smile",
          walk=t * 8 if moving else None, arms=b_arms)
    if together and stare <= 0:
        for k in range(3):                                         # 头顶的小爱心
            ph = (t * 0.6 + k / 3) % 1
            heart(c, (ax + bx) / 2 + math.sin(ph * 6 + k) * 14, gy - 230 * s - ph * 80, 10, math.sin(math.pi * ph))
    couple(c, 880, gy + 10, s, 1, "cb", hearts=1.0 if stare <= 0 else 0.0, t=t + 0.5,
           look=(0.3, -0.5) if stare <= 0 else (-1.0, -1.0), mouth="smile")
    # 她
    photo = 2.0 < t < 3.9
    selfie = 5.1 < t < 6.6
    down = ease_io(prog(t, 6.8, 0.6))
    if 1.4 < t < 2.0 or 3.9 < t < 4.6:
        g_arms = [(-50, -100), (24, -78)]                          # 伸手接 / 递回去
        look_g = -1.0
    elif photo:
        g_arms = [(-24, -150), (-44, -150)]
        look_g = -1.0
    elif selfie:
        g_arms = [(-24, -80), (44, -168)]
        look_g = 0.2
    else:
        g_arms = [(-24, -78), (lerp(26, 22, down), lerp(-76, -196, down))]
        look_g = 0.0 if t > 5 else -0.4
    girl(c, gx, gy, s, look=look_g, arms=g_arms, key="g4", mouth="flat" if down > 0 else "smile",
         head_down=8 * down, look_up=-0.8 * down)
    # 手机：始终拿在某个人手里
    b_hand = (bx + 48 * s, gy - 100 * s)
    g_take = (gx - 50 * s, gy - 100 * s)
    if t < 1.6:
        if t > 0.8:
            phone_at(c, *b_hand, 1.1, "aphone")
    elif t < 1.9:
        u = ease_io(prog(t, 1.6, 0.3))
        phone_at(c, lerp(b_hand[0], g_take[0], u), lerp(b_hand[1], g_take[1], u), 1.1, "aphone")
    elif t < 3.9:
        phone_at(c, gx - 34 * s, gy - 162 * s, 1.1, "aphone", glow_a=0.3)
    elif t < 4.4:
        phone_at(c, *g_take, 1.1, "aphone")
    elif t < 4.7:
        u = ease_io(prog(t, 4.4, 0.3))
        phone_at(c, lerp(g_take[0], b_hand[0], u), lerp(g_take[1], b_hand[1], u), 1.1, "aphone")
    elif t < 5.1:
        phone_at(c, *b_hand, 1.1, "aphone")
    if selfie:
        phone_at(c, gx + 44 * s, gy - 180 * s, 1.1, "sphone", glow_a=0.3)
    for tf in (3.4, 5.9):                                        # 快门闪光
        f = 1 - ease_out(prog(t, tf, 0.35))
        if 0 < f < 1:
            veil(c, (1, 1, 1), 0.35 * f)
    if stare > 0:
        hy = gy - 150 * s
        gaze(c, ax, gy - 152 * s, gx - 30, hy, stare, "z1", show_eye=False)
        gaze(c, bx, gy - 152 * s, gx - 20, hy + 10, stare * 0.9, "z2", show_eye=False)
        gaze(c, 880 - 46, gy - 152 * s, gx + 30, hy, stare, "z3", show_eye=False)
        gaze(c, 880 + 46, gy - 152 * s, gx + 20, hy + 10, stare * 0.8, "z4", show_eye=False)


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
    # 床头柜、水壶、台灯，打开的行李箱
    shape(c, rect(600, 900, 150, 140), hexc("6b5a4a"), "ntable", lw=3)
    with keep():
        glow(c, 650, 820, 160, hexc("ffd59a"), 0.4)
    shape(c, [(620, 840), (690, 840), (700, 880), (610, 880)], hexc("d9a65a"), "nlamp", lw=2)
    line(c, [(655, 880), (655, 900)], "nlampp", 3)
    shape(c, rrect(700, 860, 40, 40, 8), hexc("c9c4b8"), "kettle", lw=2)
    suitcase(c, 900, 1235, 1.0, "alsu", handle=0.0)
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
        silhouette(c, ex, ey + 150 * 0.95, 0.95, f"es{i}", a=0.3 * k)
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


def _route():
    r = random.Random(11)
    pts = [geo(lon, lat) for _, lon, lat, _, _ in PLACES] + [geo(lon, lat) for lon, lat in EXTRA]
    x0, y0, x1, y1 = MAP_BOX
    rest = [(r.uniform(x0 + 60, x1 - 120), r.uniform(y0 + 80, y1 - 60)) for _ in range(14)]
    rest += pts[7:]
    pts = pts[:7]
    while rest:                                                   # 就近连下一站，线不那么乱
        lx, ly = pts[-1]
        j = min(range(len(rest)), key=lambda i: (rest[i][0] - lx) ** 2 + (rest[i][1] - ly) ** 2)
        pts.append(rest.pop(j))
    times = []
    tt, step = 0.9, 0.75
    for _ in pts:
        times.append(tt)
        tt += step
        step = max(0.16, step * 0.84)
    return pts, times


ROUTE, ROUTE_T = _route()


def map_scene(c, t):
    fill_all(c, hexc("e9dcc0"))
    unroll = ease_io(prog(t, 0.0, 0.7))
    x0, y0, x1, y1 = MAP_BOX
    c.save()
    c.rectangle(0, 0, W, y0 - 40 + (y1 - y0 + 120) * unroll)
    c.clip()
    shape(c, rect(x0 - 50, y0 - 40, x1 - x0 + 100, y1 - y0 + 120), hexc("f4e7c8"), "mapb", lw=3)
    for k in range(5):                                            # 海
        yy = 560 + k * 110
        line(c, [(x1 - 90 + (k % 2) * 20, yy), (x1 - 60, yy - 8), (x1 - 30, yy), (x1, yy - 8)], f"wv{k}", 2, hexc("9fc5e8"))
    for k in range(4):                                            # 山
        mx, my = x0 + 40 + (k % 2) * 70, 400 + k * 140
        line(c, [(mx - 24, my), (mx, my - 26), (mx + 24, my)], f"mm{k}", 2, hexc("b7a888"))
    cx, cy = x1 - 40, y0 + 40                                     # 指南针
    line(c, [(cx, cy - 34), (cx, cy + 34)], "cmp1", 2, hexc("b48a4f"))
    line(c, [(cx - 34, cy), (cx + 34, cy)], "cmp2", 2, hexc("b48a4f"))
    text(c, "N", cx, cy - 44, 24, hexc("b48a4f"))
    pts, times = ROUTE, ROUTE_T
    for i in range(len(pts) - 1):                                 # 行程虚线
        dur = times[i + 1] - times[i]
        u = prog(t, times[i] + dur * 0.2, dur * 0.8)
        if u <= 0:
            continue
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        mx, my = (ax + bx) / 2, (ay + by) / 2 - 60
        n = 16
        for j in range(n):
            v0, v1 = j / n, (j + 0.55) / n
            if v0 > u:
                break
            v1 = min(v1, u)
            seg = [((1 - v) ** 2 * ax + 2 * (1 - v) * v * mx + v * v * bx,
                    (1 - v) ** 2 * ay + 2 * (1 - v) * v * my + v * v * by) for v in (v0, v1)]
            with keep():
                line(c, seg, f"dash{i}{j}", 3, hexc("c9473b"), alpha=0.75, amp=0.4)
    for i, (x, y) in enumerate(pts):                              # 一个个亮起的光点
        k = ease_back(prog(t, times[i], 0.35))
        if k <= 0:
            continue
        with keep():
            glow(c, x, y, (90 if i < 7 else 60) * k, hexc("ffd27a"), 0.7)
            circle(c, x, y, (11 if i < 7 else 8) * k, hexc("e07a3a") if i < 7 else hexc("e8a050"))
            if i == 0:                                            # 第一次：插着小红旗
                line(c, [(x, y), (x, y - 56 * k)], "flagp", 2.4)
                shape(c, [(x, y - 56 * k), (x + 30 * k, y - 48 * k), (x, y - 40 * k)], RED, "flag", lw=1.6)
    c.restore()
    with keep():                                                  # 越叠越高的车票
        n = sum(1 for tt in times if t >= tt)
        for k in range(n):
            c.save()
            c.translate(170 + math.sin(k * 1.7) * 8, 1210 - k * 11)
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


# ================================================================ 第二版新增：开头的旧铁盒
def ticket(c, x, y, s, key, age=1.0, rot=0.0):
    """泛黄、卷边的旧车票。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    paper = mix(hexc("f4f0e6"), hexc("e2c98f"), age)
    with keep():
        shape(c, [(-170, -80), (170, -80), (176, 60), (150, 82), (-170, 80)], paper, key, lw=3, amp=1.0)
        shape(c, rect(-170, -80, 340, 34), mix(hexc("9fc5e8"), hexc("c9b07a"), age), key + "h", lw=2, amp=0.6)
        for j in range(3):
            line(c, [(-140, -16 + j * 30), (40 - j * 40, -16 + j * 30)], f"{key}l{j}", 4, mix(INK, paper, 0.45 + 0.2 * age))
        line(c, [(-140, 62), (60, 62)], key + "arr", 3, mix(RED, paper, 0.4))
        shape(c, [(60, 52), (78, 62), (60, 72)], mix(RED, paper, 0.4), key + "arh", lw=1.6)
        shape(c, ell(120, 6, 34, 34, 20), None, key + "st", lw=2.4, alpha=0.5)
        circle(c, 150, 60, 10, hexc("6b5a4a"), 0.5)
    c.restore()


def c00_box(c, t):
    fill_all(c, hexc("4a4038"))
    glow(c, 320, 520, 760, hexc("ffd8a0"), 0.55)
    line(c, [(320, 0), (320, 380)], "lcord", 3, hexc("2e2824"))
    shape(c, [(250, 380), (390, 380), (430, 470), (210, 470)], hexc("d9a65a"), "lshade", lw=3)
    girl(c, 540, 1010, 2.1, sit=True, legs=False, hat=False, look=0.0, head_down=8, look_up=-0.9,
         arms=[(-30, -60), (30, -60)] if t < 2.8 else [(-12, -96), (12, -96)], mouth="smile", key="g0")
    shape(c, rect(-40, 1010, W + 80, 600), hexc("8c5a3c"), "desk", lw=3)
    for i in range(3):
        line(c, [(-20, 1060 + i * 60), (W + 20, 1060 + i * 60)], f"dg{i}", 1.6, hexc("74492f"), alpha=0.6)
    # 旧铁盒
    bx, by = 540, 1170
    lid = ease_io(prog(t, 0.3, 0.9))
    with keep():
        shape(c, [(bx - 160, by - 110 - 90 * lid), (bx + 160, by - 110 - 90 * lid), (bx + 160, by - 110), (bx - 160, by - 110)],
              hexc("7f9cb3"), "lid", lw=3)
        r = random.Random(4)
        for k in range(8):                                     # 盒子里的一沓车票和登机牌
            jig = math.sin(t * 9 + k) * 5 * (1.4 < t < 2.8)
            col = [hexc("f4f2ec"), hexc("dfe9f5"), hexc("f7e3b0"), hexc("f2d0c8")][k % 4]
            shape(c, rect(bx - 135 + r.uniform(-8, 8), by - 128 + k * 3 + jig, 270, 30), col, f"bt{k}", lw=1.6, amp=0.4)
        shape(c, rrect(bx - 165, by - 110, 330, 120, 12), hexc("6f8aa0"), "box", lw=3)
        shape(c, rect(bx - 165, by - 88, 330, 12), hexc("5d7489"), "boxs", lw=2)
    # 抽出最底下那张泛黄的车票，越变越大
    up = ease_io(prog(t, 2.6, 1.4))
    zoom = ease_io(prog(t, 4.2, 1.8))
    if up > 0:
        x = lerp(bx, 540, zoom)
        y = lerp(by - 120, 760, up) if zoom <= 0 else lerp(760, 820, zoom)
        s = lerp(0.6, 1.0, up) * lerp(1.0, 2.6, zoom)
        ticket(c, x, y, s, "tk0", age=1.0, rot=lerp(-0.15, 0.0, up))
    # 车票褪色、晕开，变成回忆里灰色的街
    melt = ease_io(prog(t, 6.2, 2.4))
    if melt > 0:
        with group_alpha(c, melt), grade(sat=0.12, warm=0.0):
            street_bg(c, 5.0 + t, base=760, rain_a=0.2, seed=3)
        veil(c, (0.85, 0.75, 0.55), 0.25 * melt * (1 - melt) * 4)


# ================================================================ 团餐：各自低头玩手机
DINERS = [(135, 0, 0), (230, 0, 1), (365, 1, 0), (460, 1, 1), (595, 2, 0), (690, 2, 1)]
GIRL_SEAT = 885
SEAT_Y = 900
DS = 1.7


def c06_dinner(c, t):
    if t < 10.0:
        k, cx = 1.0, 540
    elif t < 13.0:
        u = ease_io(prog(t, 10.0, 1.2))
        k, cx = lerp(1.0, 1.55, u), lerp(540, 860, u)
    elif t < 17.5:
        u = ease_io(prog(t, 13.0, 4.3))
        k, cx = 1.45, lerp(860, 170, u)
    else:
        u = ease_io(prog(t, 17.5, 1.2))
        k, cx = lerp(1.45, 1.0, u), lerp(170, 540, u)
    cy = lerp(960, 880, (k - 1.0) / 0.55)
    phones = ease_io(prog(t, 3.0, 0.8))
    dim = ease_io(prog(t, 17.6, 1.4))
    with cam(c, cx, cy, k):
        fill_all(c, hexc("c9b59a"))
        for i in range(12):
            line(c, [(i * 100 - 20, 0), (i * 100 - 20, 900)], f"dw{i}", 1.6, hexc("b9a587"), alpha=0.6)
        line(c, [(540, 0), (540, 220)], "dlc", 3, hexc("4a4038"))
        shape(c, [(470, 220), (610, 220), (650, 300), (430, 300)], hexc("d9a65a"), "dlamp", lw=3)
        glow(c, 540, 420, 700, hexc("ffe2a8"), 0.55 * (1 - dim))
        # 坐着的人
        for x, ci, j in DINERS:
            col = COUPLE_COLS[ci][j]
            look = (0.6 if j == 0 else -0.6) if phones < 0.5 else 0.0
            local(c, x, SEAT_Y, DS, f"dn{x}", col, hexc("2f2a28") if j == 0 else hexc("3a3a3a"),
                  "bang_short" if j == 0 else "short", sit=True, legs=False, look=look,
                  head_down=8 * phones, look_up=-0.9 * phones, mouth="flat" if phones > 0.5 else "smile",
                  arms=[(-12, -86), (12, -86)] if phones > 0.3 else [(-28, -58), (28, -58)])
        bowl_y = SEAT_Y + (-84 + 52) * DS
        gl = -1.0 if 10.0 <= t < 17.5 else 0.0
        girl(c, GIRL_SEAT, SEAT_Y, DS, sit=True, legs=False, hat=False, look=gl, mouth="flat",
             head_down=10 * dim, look_up=-1.0 * dim, arms=[(-16, -84), (16, -84)], key="gd")
        with keep():
            shape(c, ell(GIRL_SEAT, bowl_y, 40, 14, 14, 0, math.pi), hexc("f2efe8"), "gbowl", lw=2)
        # 手机的蓝光
        if phones > 0:
            for x, ci, j in DINERS:
                py_ = SEAT_Y + (-86 + 52) * DS
                with keep():
                    shape(c, rrect(x - 15, py_ - 34, 30, 46, 5), hexc("2e3449"), f"ph{x}", lw=1.6, amp=0.2)
                    shape(c, rect(x - 11, py_ - 29, 22, 35, ), hexc("bfe0ff"), f"phs{x}", lw=0, edge=False, alpha=phones)
                    glow(c, x, SEAT_Y - 150, 60, hexc("8fb8ff"), 0.28 * phones * (1 + dim))
        # 小爱心变灰、掉在桌上
        if t > 6.8:
            for i in range(3):
                hx = (DINERS[i * 2][0] + DINERS[i * 2 + 1][0]) / 2
                fall = ease_in(prog(t, 7.6 + i * 0.35, 1.0))
                grey = ease_io(prog(t, 6.8 + i * 0.3, 0.8))
                hy = lerp(SEAT_Y - 300, 840, fall)
                col = mix(RED, hexc("9a9a9a"), grey)
                r_ = lerp(24, 18, grey)
                c.save()
                c.translate(hx, hy)
                c.rotate(fall * (1.2 if i % 2 else -1.2))
                heart(c, 0, 0, r_, 1.0, col)
                c.restore()
        # 圆桌与转盘
        shape(c, ell(540, 960, 520, 140, 40), hexc("eee7d8"), "table", lw=3)
        shape(c, [(20, 960), (1060, 960), (1040, 1210), (40, 1210)], hexc("e2d9c6"), "tskirt", lw=3)
        rot = t * 0.22
        shape(c, ell(540, 950, 280, 66, 30), hexc("dfe7ea"), "susan", lw=2.4)
        dishes = []
        for i in range(5):
            a = rot + i * 2 * math.pi / 5
            dishes.append((540 + math.cos(a) * 200, 950 + math.sin(a) * 40, i))
        dishes.sort(key=lambda d: d[1])
        cols = [hexc("d9653a"), hexc("6fa860"), hexc("e8c040"), hexc("b5533a"), hexc("8a6a4a")]
        for x, y, i in dishes:
            shape(c, ell(x, y, 52, 16, 16), hexc("f8f6f0"), f"pl{i}", lw=2, amp=0.4)
            shape(c, ell(x, y - 4, 34, 9, 14), cols[i], f"fd{i}", lw=1.6, amp=0.3)
            steam = 1 - ease_io(prog(t, 8.0, 4.0))
            if steam > 0:
                for kk in range(2):
                    sx = x - 8 + kk * 16
                    line(c, [(sx, y - 16), (sx - 6 + math.sin(t * 2 + kk + i) * 6, y - 46), (sx + 4, y - 74)], f"st{i}{kk}", 2,
                         (1, 1, 1), alpha=0.6 * steam)
        if dim > 0:
            veil(c, (0.1, 0.12, 0.22), 0.5 * dim)
            with keep():
                for x, ci, j in DINERS:
                    glow(c, x, SEAT_Y - 150, 70, hexc("8fb8ff"), 0.4 * dim)


# ================================================================ 两个人的寂寞 / 一个人的孤独
def c07_split(c, t):
    wipe = ease_io(prog(t, 0.8, 1.0))
    # 左：灰色雨云下背对背的两个人
    c.save()
    c.rectangle(0, 0, 540 + 540 * (1 - wipe), H)
    c.clip()
    with grade(sat=0.1):
        fill_all(c, hexc("8a8f99"))
        shape(c, rect(-20, 1100, 600, 800), hexc("6f747d"), "lgr", lw=3)
        rain_cloud(c, 300, 560, 1.7, "lcl2", col=hexc("6a6f79"), t=t)
        rain(c, t, 40, 0.4, seed=8, x0=0, x1=540, y0=600, y1=1200)
        shape(c, rect(160, 1090, 280, 20), hexc("5a5d66"), "lbench", lw=2.4)
    for j, (x, lk) in enumerate(((250, -1.0), (350, 1.0))):
        local(c, x, 1090, 1.3, f"bb{j}", COUPLE_COLS[0][j], hexc("2f2a28"), "short" if j else "bang_short", sit=True,
              look=lk, head_down=8, look_up=-0.9, mouth="flat", arms=[(-12, -86), (12, -86)])
        with keep():
            glow(c, x, 1090 - 110, 60, hexc("8fb8ff"), 0.5)
            shape(c, rrect(x - 10, 1090 - 70, 20, 30, 4), hexc("2e3449"), f"bph{j}", lw=1.4, amp=0.2)
    c.restore()
    # 右：星空下一个人
    if wipe > 0:
        c.save()
        c.rectangle(540 + 540 * (1 - wipe), 0, 540, H)
        c.clip()
        with grade(sat=0.9):
            vgrad(c, 0, 1100, [(0, hexc("141b3a")), (0.7, hexc("34477a")), (1, hexc("6b7bb0"))], 540, W)
            r = random.Random(5)
            for i in range(40):
                star(c, r.uniform(560, W), r.uniform(60, 820), r.uniform(1.5, 3.5), 0.6 + 0.4 * math.sin(t * 3 + i))
            shape(c, [(520, 1110), (620, 900), (720, 980), (860, 820), (1100, 1110)], hexc("3d4766"), "rmt", lw=2.6)
            shape(c, rect(520, 1110, 600, 800), hexc("2e3550"), "rgr", lw=2.6)
            glow(c, 820, 900, 420, hexc("dfe6ff"), 0.35)
        girl(c, 820, 1110, 1.5, view="back", hat=True, key="gst")
        with keep():                                            # 风吹起的红丝带
            sw = math.sin(t * 5) * 10
            hy = 1110 - 168 * 1.5
            line(c, [(820 + 26, hy), (820 + 70 + sw, hy - 10), (820 + 110 + sw * 1.5, hy + 4)], "rib", 5, RED)
        c.restore()
        line(c, [(540 + 540 * (1 - wipe), 0), (540 + 540 * (1 - wipe), H)], "split", 4)


# ================================================================ 又一次高原反应：有人敲门
def c08_door(c, t):
    dawn = ease_io(prog(t, 7.0, 2.4))
    fill_all(c, mix(hexc("39415a"), hexc("8a8fa6"), dawn * 0.6))
    # 窗
    c.save()
    c.rectangle(110, 220, 380, 420)
    c.clip()
    vgrad(c, 220, 640, [(0, mix(hexc("141b33"), hexc("f3c79a"), dawn)), (1, mix(hexc("3b4b7a"), hexc("fbe6c4"), dawn))])
    shape(c, [(90, 640), (250, 430), (350, 540), (420, 470), (520, 640)], mix(hexc("2a3048"), hexc("9aa0b8"), dawn), "dmt",
          lw=2.4)
    shape(c, [(210, 482), (250, 430), (290, 470), (250, 466)], hexc("eef2f8"), "dmts", lw=1.8, alpha=0.3 + 0.7 * dawn)
    c.restore()
    shape(c, rect(110, 220, 380, 420), None, "dwin", lw=6)
    # 门：开着时能看到走廊，尽头一扇半掩的门透出灯光
    dx0, dx1, dy0, dy1 = 680, 930, 500, 1180
    open_ = ease_io(prog(t, 2.4, 0.5)) * (1 - ease_io(prog(t, 4.8, 0.5)))
    shape(c, rect(dx0 - 20, dy0 - 20, dx1 - dx0 + 40, dy1 - dy0 + 20), hexc("2e3449"), "dfr", lw=3)
    if open_ > 0:
        c.save()
        c.rectangle(dx0, dy0, dx1 - dx0, dy1 - dy0)
        c.clip()
        fill_all(c, hexc("d9c8a8"))
        shape(c, [(dx0, dy0), (770, 760), (840, 760), (dx1, dy0)], hexc("e8dcc4"), "corc", lw=1.6)
        shape(c, [(dx0, dy1), (770, 860), (840, 860), (dx1, dy1)], hexc("b9a587"), "corf", lw=1.6)
        shape(c, rect(770, 760, 70, 100), hexc("8c7a62"), "cend", lw=1.6)
        with keep():                                            # 尽头半掩的门
            shape(c, rect(790, 775, 16, 85), hexc("ffd59a"), "cgap", lw=1.2, amp=0.2)
            glow(c, 800, 820, 70, hexc("ffd59a"), 0.6)
        glow(c, 800, 600, 260, hexc("fff0c8"), 0.4)
        if 2.6 < t < 4.9:
            local(c, 805, 1170, 1.45, "doorman", COUPLE_COLS[1][1], hexc("3a3a3a"), "short", look=-0.6, mouth="smile",
                  arms=[(-24, -78), (-60, -96) if t < 4.0 else (-24, -78)])
        c.restore()
    door_w = (dx1 - dx0) * (1 - open_ * 0.85)
    shape(c, rect(dx0, dy0, door_w, dy1 - dy0), hexc("6b5a4a"), "dpanel", lw=3)
    circle(c, dx0 + door_w - 24, 860, 8, hexc("d9b56a"))
    # 床
    shape(c, rect(60, 1040, 500, 60), hexc("e6e0d4"), "dbed", lw=3)
    shape(c, rect(60, 1100, 500, 140), hexc("7f8aa8"), "dbedb", lw=3)
    # 药盒：从他手里到她手里
    def medbox(x, y, key):
        with keep():
            shape(c, rect(x - 26, y - 18, 52, 36), hexc("f4f2ec"), key, lw=2, amp=0.3)
            shape(c, rect(x - 26, y - 18, 52, 10), hexc("4f8fd0"), key + "s", lw=1.4, amp=0.2)
            shape(c, ell(x, y + 6, 10, 5, 10), hexc("e8a050"), key + "p", lw=1.2, amp=0.2)
    if t < 1.6:                                                 # 床上晕眩，听见敲门
        girl(c, 330, 1040, 1.5, sit=True, crouch=True, hat=False, mouth="sad", head_down=6, look=0.6 if t > 0.8 else 0.2,
             arms=[(-14, -92), (14, -92)], key="g8")
        hy = 1040 + (52 - 150) * 1.5 - 70
        with keep():
            pts = [(330 + math.cos(i / 50 * 4 * math.pi + t * 3) * (8 + i) * 1.4,
                    hy + math.sin(i / 50 * 4 * math.pi + t * 3) * (8 + i) * 0.45) for i in range(50)]
            line(c, pts, "dz8", 2.2, hexc("c8cde0"), alpha=0.8)
        for kk, tk in enumerate((0.8, 1.15)):
            a = 1 - prog(t, tk, 0.4)
            if 0 < a < 1:
                with keep():
                    for j in range(3):
                        line(c, [(dx0 - 30 - j * 14, 760 + j * 18), (dx0 - 50 - j * 14, 750 + j * 18)], f"kn{kk}{j}", 3,
                             hexc("f6d6a8"), alpha=a)
    elif t < 6.8:
        x = lerp(330, 600, ease_io(prog(t, 1.6, 0.8)))
        lean = t > 5.2
        girl(c, x, 1180, 1.5, hat=False, look=1.0 if not lean else 0.0, mouth="flat" if lean else "smile",
             walk=t * 8 if t < 2.4 else None, head_down=6 if lean else 0, eyes_closed=lean and t > 5.6,
             arms=[(-24, -78), (40, -96)] if 3.6 < t < 5.0 else [(-24, -78), (24, -78)], key="g8w")
        if 2.6 < t < 4.0:
            medbox(805 - 60 * 1.45, 1170 - 96 * 1.45, "med")
        elif 3.6 <= t < 6.8:
            medbox(x + 40 * 1.5, 1180 - 96 * 1.5, "med")
    else:                                                       # 停顿：坐回床边，天一点点亮
        girl(c, 330, 1040, 1.5, sit=True, hat=False, look=-0.7, look_up=0.5, mouth="flat",
             arms=[(-12, -70), (12, -70)], key="g8s")
        medbox(330, 1040 + (-70 + 52) * 1.5 - 6, "med")


# ================================================================ 越来越习惯一个人
def m_train(c, t):
    fill_all(c, hexc("c9bfae"))
    c.save()
    c.rectangle(160, 300, 760, 520)
    c.clip()
    vgrad(c, 300, 820, [(0, hexc("9fc5e8")), (1, hexc("e9f2f6"))])
    shape(c, hill_pts(700, 40, 0.01, t * 4, 100, 1000, 900), hexc("8fb07a"), "mth", lw=2.4)
    for k in range(4):
        x = (k * 300 - t * 700) % 1200 - 100
        line(c, [(x, 520), (x, 820)], f"mpole{k}", 6, hexc("6b5a4a"))
    c.restore()
    shape(c, rect(160, 300, 760, 520), None, "mtw", lw=8)
    line(c, [(120, 230), (960, 230)], "rack", 6, hexc("6b5a4a"))
    for i, (x, w_, col) in enumerate(((200, 150, "8b6f9a"), (420, 110, "c98d72"), (700, 170, "7f9cb3"))):
        shape(c, rrect(x, 150, w_, 78, 10), hexc(col), f"bag{i}", lw=2.4)
    shape(c, rect(100, 1000, 880, 40), hexc("8a6a4a"), "mtsill", lw=3)
    with keep():
        shape(c, [(300, 960), (340, 960), (334, 1000), (306, 1000)], hexc("f2efe8"), "mcup", lw=2)
        for k in range(2):
            line(c, [(312 + k * 14, 952), (306 + k * 14 + math.sin(t * 3 + k) * 5, 926), (314 + k * 14, 900)], f"mst{k}", 2,
                 (1, 1, 1), alpha=0.7)
    shape(c, rrect(840, 980, 170, 420, 30), hexc("4f7a8c"), "mseat", lw=3)
    girl(c, 760, 1180, 1.6, sit=True, hat=True, look=-0.9, mouth="flat", key="gm1")


def m_peak(c, t):
    vgrad(c, 0, 1100, [(0, hexc("f2a07a")), (0.6, hexc("f8d29a")), (1, hexc("fbecc8"))])
    glow(c, 540, 860, 520, hexc("fff0b8"), 0.8)
    shape(c, ell(540, 860, 80, 80, 24), hexc("fbd78a"), "msun", lw=2)
    for i in range(5):
        cloud(c, (i * 260 + t * 20) % 1300 - 120, 1000 + (i % 2) * 40, 1.6, f"mcl{i}", a=0.85)
    shape(c, [(-40, 1900), (-40, 1300), (300, 1050), (540, 1120), (760, 1000), (1120, 1300), (1120, 1900)], hexc("6f6a80"),
          "mpk", lw=3)
    for k, (rx, ry, rr) in enumerate(((760, 1040, 26), (765, 1012, 20), (762, 990, 14))):
        shape(c, ell(rx, ry, rr, rr * 0.7, 12), hexc("9a96a8"), f"cairn{k}", lw=2)
    girl(c, 560, 1130, 1.6, view="back", hat=True, key="gm2")


def m_market(c, t):
    vgrad(c, 0, 1300, [(0, hexc("1d2647")), (1, hexc("4a3a5a"))])
    pts = [(-40, 420), (540, 520), (1120, 420)]
    line(c, pts, "mrope", 2, hexc("2e2824"))
    with keep():
        for k in range(9):
            u = (k + 0.5) / 9
            x = lerp(-40, 1120, u)
            y = 420 + math.sin(math.pi * u) * 100 + 30
            glow(c, x, y, 90, hexc("ffb070"), 0.5)
            shape(c, ell(x, y, 26, 32, 16), hexc("d9433a"), f"lan{k}", lw=2)
    for i, (x, col) in enumerate(((160, "8a5a3a"), (880, "6a5a7a"))):
        shape(c, rect(x - 110, 900, 220, 220), hexc(col), f"stall{i}", lw=3)
        shape(c, [(x - 130, 900), (x + 130, 900), (x + 100, 840), (x - 100, 840)], hexc("e8c040"), f"aw{i}", lw=2.4)
    for i, (x, col) in enumerate(((400, "5a6a4a"), (680, "7a4a4a"))):
        shape(c, rect(x - 80, 940, 160, 180), hexc(col), f"stb{i}", lw=2.4)
        shape(c, [(x - 96, 940), (x + 96, 940), (x + 76, 896), (x - 76, 896)], hexc("d9653a"), f"awb{i}", lw=2)
    with keep():
        for i, x in enumerate((160, 400, 680, 880)):
            glow(c, x, 1000, 90, hexc("ffc070"), 0.35)
            for k in range(2):
                line(c, [(x - 10 + k * 20, 930), (x - 16 + k * 20 + math.sin(t * 3 + i + k) * 6, 880),
                         (x - 6 + k * 20, 830)], f"mkst{i}{k}", 2.2, (1, 1, 1), alpha=0.5)
    shape(c, rect(-20, 1120, W + 40, 600), hexc("3a3440"), "mgr", lw=3)
    r = random.Random(14)
    for i in range(7):
        x = (r.uniform(0, 1100) - t * 60 * (1 if i % 2 else -1)) % 1200 - 60
        if abs(x - 540) > 90:
            silhouette(c, x, 1180 + r.uniform(-20, 20), 1.2, f"mkp{i}", walk=t * 6 + i, a=0.5, col=hexc("6a6070"))
    girl(c, 540, 1200, 1.6, hat=True, walk=t * 7, look=0.3, mouth="laugh", key="gm3")


def c09_montage(c, t):
    if t < 1.8:
        m_train(c, t)
    elif t < 3.6:
        m_peak(c, t)
    else:
        m_market(c, t)


def c14_wait(c, t):
    if t < 5.5:
        c12_wait(c, t)
    else:
        c12b_notes(c, t - 5.5)


# ================================================================ 第十稿：回到家放进铁盒 / 回到台灯下
def tinbox(c, bx, by, lid, key, n=8, jig=0.0, empty=False):
    with keep():
        shape(c, [(bx - 160, by - 110 - 90 * lid), (bx + 160, by - 110 - 90 * lid), (bx + 160, by - 110), (bx - 160, by - 110)],
              hexc("7f9cb3"), key + "lid", lw=3)
        if not empty:
            r = random.Random(4)
            for k in range(n):
                col = [hexc("f4f2ec"), hexc("dfe9f5"), hexc("f7e3b0"), hexc("f2d0c8")][k % 4]
                shape(c, rect(bx - 135 + r.uniform(-8, 8), by - 128 + k * 3 + math.sin(k) * jig, 270, 30), col, f"{key}t{k}",
                      lw=1.6, amp=0.4)
        shape(c, rrect(bx - 165, by - 110, 330, 120, 12), hexc("6f8aa0"), key + "b", lw=3)
        shape(c, rect(bx - 165, by - 88, 330, 12), hexc("5d7489"), key + "s", lw=2)


def c08b_home(c, t):
    """回到家：把第一张车票放进一个空铁盒（就是开头那个铁盒）。"""
    room(c, t, sky="grey", hat_hook=False, chair=False)
    shape(c, rect(520, 1000, 440, 22), hexc("8c5a3c"), "htab", lw=3)
    for x in (540, 930):
        shape(c, rect(x, 1022, 14, 90), hexc("7a4d33"), f"htl{x}", lw=2.4)
    girl(c, 400, 1110, 1.6, hat=True, look=0.8, mouth="smile", key="g8b",
         arms=[(-24, -78), (lerp(60, 40, ease_io(prog(t, 0.6, 1.0))), lerp(-120, -96, ease_io(prog(t, 0.6, 1.0))))])
    suitcase(c, 250, 1112, 0.9, "h8su", handle=0.0)
    c.save()
    c.translate(740, 1000)
    c.scale(0.55, 0.55)
    tinbox(c, 0, 0, 0.8 * (1 - ease_io(prog(t, 2.0, 0.6))), "hb", empty=True)
    c.restore()
    u = ease_io(prog(t, 0.4, 1.4))
    if t < 2.0:
        ticket(c, lerp(470, 740, u), lerp(900, 950, u), 0.32, "htk", age=0.0, rot=lerp(-0.3, 0.0, u))


DESK = hexc("8c5a3c")


def desk_tickets(c, t):
    """俯视的书桌：车票一张张铺开，红色虚线把它们连成地图。"""
    fill_all(c, DESK)
    for i in range(9):
        line(c, [(-20, 120 + i * 150), (W + 20, 120 + i * 150 + 20)], f"grain{i}", 2, hexc("7a4d33"), alpha=0.6)
    glow(c, 360, 300, 900, hexc("ffd8a0"), 0.35)
    pts, times = ROUTE, ROUTE_T
    for i in range(len(pts) - 1):                                 # 红色虚线
        dur = times[i + 1] - times[i]
        u = prog(t, times[i] + dur * 0.2, dur * 0.8)
        if u <= 0:
            continue
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        mx, my = (ax + bx) / 2, (ay + by) / 2 - 60
        n = 16
        for j in range(n):
            v0, v1 = j / n, (j + 0.55) / n
            if v0 > u:
                break
            v1 = min(v1, u)
            seg = [((1 - v) ** 2 * ax + 2 * (1 - v) * v * mx + v * v * bx,
                    (1 - v) ** 2 * ay + 2 * (1 - v) * v * my + v * v * by) for v in (v0, v1)]
            with keep():
                line(c, seg, f"ddash{i}{j}", 3.4, hexc("e0533f"), alpha=0.85, amp=0.4)
    r = random.Random(31)
    for i, (x, y) in enumerate(pts):                              # 一张张车票
        k = ease_back(prog(t, times[i], 0.35))
        rot = r.uniform(-0.4, 0.4)
        if k <= 0:
            continue
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.scale(k, k)
        if i == 0:
            ticket(c, 0, 0, 0.36, "dt0", age=1.0)
        else:
            col = [hexc("f4f2ec"), hexc("dfe9f5"), hexc("f7e3b0"), hexc("f2d0c8")][i % 4]
            with keep():
                shape(c, rect(-46, -20, 92, 40), col, f"dt{i}", lw=1.8, amp=0.4)
                line(c, [(-30, -4), (24, -4)], f"dtl{i}", 2.4, hexc("3f6fb5") if i % 2 else RED)
                line(c, [(-30, 8), (8, 8)], f"dtm{i}", 2, hexc("8a8f99"))
        c.restore()
        with keep():
            glow(c, x, y, 60 * k, hexc("ffd27a"), 0.35)


def desk_front(c, t):
    """回到台灯下：满桌车票，她把最早那张放回最上面，笑了。"""
    fill_all(c, hexc("4a4038"))
    glow(c, 320, 520, 760, hexc("ffd8a0"), 0.6)
    line(c, [(320, 0), (320, 380)], "lcord2", 3, hexc("2e2824"))
    shape(c, [(250, 380), (390, 380), (430, 470), (210, 470)], hexc("d9a65a"), "lshade2", lw=3)
    girl(c, 540, 1010, 2.1, sit=True, legs=False, hat=False, look=0.0, head_down=4, look_up=-0.4, mouth="smile",
         arms=[(-30, -60), (lerp(40, 14, ease_io(prog(t, 0.6, 1.2))), lerp(-110, -70, ease_io(prog(t, 0.6, 1.2))))], key="gend")
    shape(c, rect(-40, 1010, W + 80, 600), DESK, "desk2", lw=3)
    r = random.Random(8)
    with keep():                                                  # 铺满桌面的车票
        for k in range(16):
            x, y = r.uniform(60, 1020), r.uniform(1060, 1300)
            c.save()
            c.translate(x, y)
            c.rotate(r.uniform(-0.5, 0.5))
            col = [hexc("f4f2ec"), hexc("dfe9f5"), hexc("f7e3b0"), hexc("f2d0c8")][k % 4]
            shape(c, rect(-50, -18, 100, 36), col, f"ft{k}", lw=1.6, amp=0.4)
            c.restore()
    tinbox(c, 540, 1170, 0.9, "eb", n=3)
    u = ease_io(prog(t, 0.6, 1.2))
    ticket(c, lerp(600, 540, u), lerp(860, 1050, u), lerp(0.55, 0.42, u), "etk", age=1.0, rot=lerp(0.2, 0.05, u))


def c17_desk(c, t):
    swap = ease_io(prog(t, 8.2, 1.2))
    if swap < 1:
        desk_tickets(c, t)
    if swap > 0:
        with group_alpha(c, swap):
            desk_front(c, t - 8.2)


def desk_still():
    if "d" not in _STILL:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(170.0)
        with grade(sat=1.0, dark=0.0, warm=0.2):
            desk_tickets(cc, 7.9)
        _STILL["d"] = surf
    return _STILL["d"]


def outro2(c, t):
    book_outro(c, t, desk_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第二章 · 完")

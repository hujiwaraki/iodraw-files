"""第八章 · 同路人 —— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。

一向喜新厌旧，风景一张张翻过去不回头 → 停在一座长在山上的城，去了三次 → 前两次：一大桌人、两顿火锅（偏灰）
→ 这次跟她一起去：梯坎上她回头等 → 一路讲小时候 → 小摊、小凳子 → 能吃辣，肠子不服气 → 夜里挤在一张床上，
凌晨了她还在说 → 心和心的距离 → 玩累了在长椅上睡着，她静静等 → 醒来，一起走下梯坎，轻轨开远。
画面里不写字、不写真实地名；不用雾。好朋友：青绿色外套、马尾，有脸有颜色。
"""
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
from scenes_v2 import local  # noqa: E402

FRIEND = hexc("3f9a8a")                   # 好朋友的青绿色外套
FHAIR = hexc("2a2220")
CHILI = hexc("c8402e")
WARM = hexc("ffd08a")
WOOD = hexc("9a6a44")


def friend(c, x, y, s, key="fr", **kw):
    kw.setdefault("look", -0.4)
    local(c, x, y, s, key, FRIEND, FHAIR, "pony", **kw)


def slippers_illus(c, cx, cy):
    """章节页小插画：两双并排放着的拖鞋。"""
    with keep():
        for k, col in enumerate((hexc("f2c04a"), FRIEND)):
            for j in range(2):
                x = cx - 70 + k * 84 + j * 34
                shape(c, rrect(x - 14, cy - 40, 28, 84, 13), col, f"ill{k}{j}", lw=2.6, amp=0.5)
                shape(c, rrect(x - 15, cy - 26, 30, 22, 8), mix(col, (1, 1, 1), 0.45), f"ills{k}{j}", lw=2, amp=0.4)


def intro(c, t):
    book_intro(c, t, "第八章", "同路人", slippers_illus)


# ================================================================ 山城
def building(c, x, base, w, h, col, key, lit=0.0, night=0.0, seed=0):
    shape(c, rect(x, base - h, w, h + 30), mix(col, hexc("2a2e48"), night * 0.7), key, lw=2.4)
    r = random.Random(seed)
    with keep():
        for row in range(int(h // 70)):
            for colm in range(max(1, int(w // 60))):
                wx, wy = x + 16 + colm * 60, base - h + 24 + row * 70
                if wx + 30 > x + w:
                    continue
                on = r.random() < (0.35 + 0.5 * lit)
                if night > 0 and on:
                    shape(c, rect(wx, wy, 30, 36), hexc("ffd98a"), f"{key}w{row}{colm}", lw=0, edge=False,
                          alpha=0.85 * night)
                elif night <= 0:
                    shape(c, rect(wx, wy, 30, 36), mix(col, (1, 1, 1), 0.45), f"{key}w{row}{colm}", lw=1.2)


def hill_y(x, base, amp, ph):
    return base - amp * (0.5 + 0.5 * math.sin(x * 0.0045 + ph)) - 0.18 * (x - W / 2)


def city(c, t, night=0.0, rail=None, warm=0.0, lit=0.3):
    """一座长在山上的城：几层山坡，楼顺着坡一层叠一层往上长。rail：一列轻轨从一栋楼中间穿过去（0→1）。"""
    top = mix(mix(hexc("9fc0dc"), hexc("f2c8a0"), warm), hexc("141a34"), night)
    bot = mix(mix(hexc("e6ebe8"), hexc("fbe6c8"), warm), hexc("2e3458"), night)
    vgrad(c, -200, 1300, [(0, top), (1, bot)], -300, W + 300)
    if night > 0:
        r = random.Random(5)
        with keep():
            for k in range(30):
                star(c, r.uniform(0, W), r.uniform(40, 420), r.uniform(1.5, 2.6), night * 0.6)
    layers = ((760, 260, 0.3, (90, 220), "b8c4cc", "a8b4a8"), (1000, 300, 1.9, (110, 260), "c8b8a8", "a89a80"),
              (1260, 320, 3.4, (120, 300), "d8c8b0", "9a8a70"))
    for li, (base, amp, ph, (hmin, hmax), col, hcol) in enumerate(layers):
        pts = [(x, hill_y(x, base, amp, ph)) for x in range(-200, W + 240, 40)]
        r = random.Random(10 + li)
        x = -60
        k = 0
        while x < W + 60:                                          # 楼顺着山坡长上去，底部埋在坡里
            w_ = r.uniform(90, 150)
            h_ = r.uniform(hmin, hmax)
            yb = hill_y(x + w_ / 2, base, amp, ph) + 40
            building(c, x, yb, w_, h_, hexc(col), f"b{li}_{k}", lit=lit, night=night, seed=li * 50 + k)
            x += w_ + r.uniform(-20, 10)
            k += 1
        shape(c, pts + [(W + 240, 2400), (-200, 2400)], mix(hexc(hcol), hexc("1a1e30"), night * 0.8), f"hl{li}", lw=2.4)
    if rail is not None:                                           # 一栋楼中间开了一个洞，轻轨从里面穿过去
        bx, bw, bh = 420, 260, 620
        bb = hill_y(bx + bw / 2, 1260, 320, 3.4) + 60
        ty = bb - 330                                              # 轨道的高度
        line(c, [(-200, ty + 92), (W + 200, ty + 92)], "track", 10, hexc("7a7a8a"))
        for xx in (100, 860):
            line(c, [(xx, ty + 92), (xx, hill_y(xx, 1260, 320, 3.4) + 20)], f"pier{xx}", 16, hexc("8a8a98"))
        tx = lerp(-900, W + 300, rail)
        shape(c, rect(bx, ty - 14, bw, 112), mix(hexc("4a4a5a"), hexc("12142a"), night), "holebg", lw=0, edge=False)

        def train():
            with keep():
                shape(c, rrect(tx, ty, 820, 84, 26), hexc("e8eef0"), "train", lw=2.4)
                line(c, [(tx + 10, ty + 60), (tx + 810, ty + 60)], "trs", 6, hexc("3f8ab8"))
                for k in range(8):
                    shape(c, rect(tx + 40 + k * 96, ty + 14, 64, 34), mix(hexc("bcd8e8"), hexc("ffd98a"), night),
                          f"trw{k}", lw=1.4)
        train()
        c.save()                                                   # 楼盖在轻轨上面，只在洞那里露出车厢
        c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        c.rectangle(bx - 20, bb - bh - 20, bw + 40, bh + 60)
        c.rectangle(bx, ty - 14, bw, 112)
        c.clip()
        building(c, bx, bb, bw, bh, hexc("e0d4c4"), "railb", night=night, seed=99)
        c.restore()
        shape(c, rect(bx, ty - 14, bw, 112), None, "hole", lw=2.4)



def stairs_bg(c, t, rain=0.0, crayon=False):
    """长长的梯坎：从左下一直爬到右上，两边是老房子的墙和花盆。"""
    sky = mix(hexc("c8d8e4"), hexc("a8b0bc"), rain)
    vgrad(c, -200, 1200, [(0, sky), (1, hexc("efe8dc"))], -300, W + 300)
    shape(c, [(-40, 0), (360, 0), (360, 2000), (-40, 2000)], hexc("d8c8b0") if not crayon else hexc("e8c8a0"), "wallL",
          lw=3)
    shape(c, [(760, 0), (1120, 0), (1120, 2000), (760, 2000)], hexc("cbb89c") if not crayon else hexc("e0b890"), "wallR",
          lw=3)
    for k in range(3):
        shape(c, rect(60, 300 + k * 420, 160, 200), hexc("8a6a4a"), f"wwL{k}", lw=2)
        shape(c, rect(860, 200 + k * 420, 160, 200), hexc("8a6a4a"), f"wwR{k}", lw=2)
    for k in range(22):                                            # 一级一级往上的台阶
        y = 1900 - k * 72
        shape(c, rect(360, y, 400, 72), mix(hexc("b8b0a0"), hexc("d8d0c0"), (k % 2) * 0.4), f"st{k}", lw=1.8, amp=0.5)
    with keep():
        for k in range(4):                                         # 墙边的花盆
            y = 1700 - k * 380
            shape(c, [(330, y), (370, y), (364, y + 34), (336, y + 34)], hexc("c8784a"), f"pot{k}", lw=1.6)
            for j in range(3):
                shape(c, ell(342 + j * 10, y - 12, 10, 16, 10), hexc("6fa860"), f"lf{k}{j}", lw=1.2)



def old_street(c, t):
    vgrad(c, -200, 1100, [(0, hexc("b8d0e0")), (1, hexc("f2ece0"))], -300, W + 300)
    for k, (x0, w_, h_, col) in enumerate(((-40, 300, 700, "d8c0a0"), (260, 280, 820, "c8b8a8"),
                                            (540, 260, 760, "dcc8a8"), (800, 320, 700, "cbb898"))):
        shape(c, rect(x0, 1240 - h_, w_, h_ + 20), hexc(col), f"os{k}", lw=3)
        for j in range(3):
            shape(c, rect(x0 + 30, 1240 - h_ + 60 + j * 200, w_ - 60, 26), hexc("8a6a4a"), f"bal{k}{j}", lw=1.8)
            for i in range(4):                                     # 晾着的衣服
                shape(c, rect(x0 + 40 + i * (w_ - 80) / 4, 1240 - h_ + 86 + j * 200, 30, 44),
                      hexc(["e88a7a", "9fc5e8", "f2d27a", "a8d0a0"][(i + j + k) % 4]), f"cl{k}{j}{i}", lw=1.2)
    shape(c, rect(-20, 1240, W + 40, 700), hexc("b8ac98"), "osg", lw=3)


def memory(c, a, fn):
    """蜡笔画的回忆：暖暖的颜色、柔一点的光，叠在现实里。"""
    if a <= 0:
        return
    with group_alpha(c, a), grade(sat=0.8, warm=0.45):
        with keep():
            glow(c, 300, 1100, 360, hexc("ffe0b0"), 0.5)
        fn()



def bedroom(c, t, dark=0.0, off=0.0):
    fill_all(c, mix(hexc("3a3a58"), hexc("141628"), dark))
    with keep():                                                   # 床头上方的窗：山城的灯一层一层亮到天边
        shape(c, rect(250, 220, 580, 420), hexc("141a34"), "win8", lw=4)
        c.save()
        c.rectangle(254, 224, 572, 412)
        c.clip()
        r = random.Random(8)
        for layer in range(4):
            yb = 520 + layer * 40
            for k in range(30):
                x = 250 + k * 20 + r.uniform(-4, 4)
                y = yb - r.uniform(0, 120 - layer * 20)
                on = r.random() < 0.7
                gone = r.random() < off                            # 窗外的灯一格一格熄掉
                if on and not gone:
                    circle(c, x, y, 3, hexc("ffd98a"), a=0.5 + 0.4 * math.sin(t * 2 + k + layer))
        c.restore()
        line(c, [(540, 220), (540, 640)], "win8m", 4, hexc("6a5a50"))
    shape(c, rect(-20, 1380, W + 40, 700), mix(hexc("4a4458"), hexc("1e1e2e"), dark), "fl8", lw=3)
    shape(c, rect(150, 760, 780, 200), hexc("8a6a4a"), "headb", lw=3)       # 床头
    shape(c, rect(130, 960, 820, 420), hexc("8a6a4a"), "bedf", lw=3)
    for x, k in ((380, "A"), (700, "B")):
        shape(c, rrect(x - 130, 900, 260, 90, 30), hexc("f2eee6"), f"pil{k}", lw=2.4)


def quilt(c, dark=0.0):
    shape(c, [(130, 1060), (950, 1060), (960, 1380), (120, 1380)], mix(hexc("e8a8a0"), hexc("8a6a78"), dark * 0.5),
          "quilt", lw=3)
    with keep():
        for k in range(6):
            circle(c, 220 + k * 130, 1180 + (k % 2) * 60, 14, hexc("f6e0c8"), a=0.7)




# ================================================================ 1 一向喜新厌旧：风景一张张翻过去
def far_view(c, k, off):
    """很淡的远方：0 雪山 / 1 海 / 2 草原。"""
    pale = 0.42
    if k == 0:
        vgrad(c, -200, 1300, [(0, mix(hexc("9fc0dc"), (1, 1, 1), pale)), (1, hexc("f2f2ee"))], -300, W + 300)
        for j, (mx, mh, mw) in enumerate(((120, 760, 640), (560, 980, 760), (980, 820, 680))):
            mountain(c, mx + off, 1300, mw, mh, mix(hexc("a8b8cc"), (1, 1, 1), pale), f"fm{j}")
    elif k == 1:
        vgrad(c, -200, 1000, [(0, mix(hexc("8ec4e4"), (1, 1, 1), pale)), (1, hexc("f4f6f2"))], -300, W + 300)
        shape(c, rect(-200, 960, W + 400, 400), mix(hexc("6aa8cc"), (1, 1, 1), pale), "fsea", lw=2.4)
        with keep():
            for j in range(5):
                y = 1010 + j * 60
                line(c, [(xx, y + 8 * math.sin(xx * 0.015 + j + off * 0.01)) for xx in range(-200, W + 200, 40)],
                     f"fw{j}", 2, (1, 1, 1), alpha=0.6)
    else:
        vgrad(c, -200, 1100, [(0, mix(hexc("a8d0e8"), (1, 1, 1), pale)), (1, hexc("f6f4e8"))], -300, W + 300)
        shape(c, hill_pts(1080, 60, 0.004, 1.0 + off * 0.002), mix(hexc("a8c88a"), (1, 1, 1), pale), "fg1", lw=2.4)
        shape(c, hill_pts(1180, 40, 0.006, 2.4 + off * 0.003), mix(hexc("9cc07c"), (1, 1, 1), pale), "fg2", lw=2.4)
        for j in range(4):
            tree(c, 160 + j * 260 + off * 0.6, 1150, 0.7, f"ft{j}", mix(hexc("74a160"), (1, 1, 1), pale))


def m01(c, t):
    """远方的风景像书页一样一张张从她身边翻过去，她拉着箱子一直往前走，没回头。"""
    flips = (2.0, 4.3)
    k = sum(1 for f in flips if t >= f + 0.6)
    off = -t * 40
    far_view(c, k, off)
    for f in flips:                                                # 新的一页从右边翻进来
        u = prog(t, f, 0.6)
        if 0 < u < 1:
            edge = lerp(W + 40, -40, ease_io(u))
            c.save()
            c.rectangle(edge, -200, W + 400, H + 400)
            c.clip()
            far_view(c, k + 1, off)
            c.restore()
            with keep():
                line(c, [(edge, -100), (edge, H + 100)], "pgedge", 6, hexc("c8c0b0"), alpha=0.8)
                shape(c, rect(edge - 60, -100, 60, H + 200), hexc("8a8478"), "pgsh", lw=0, edge=False,
                      alpha=0.12 * math.sin(math.pi * u))
    shape(c, rect(-200, 1300, W + 400, 700), hexc("d8ccb4"), "path1", lw=3)
    with keep():
        for j in range(6):                                         # 路面往后退
            x = (j * 260 - t * 220) % (W + 260) - 130
            line(c, [(x, 1420), (x + 90, 1420)], f"pd{j}", 4, hexc("b8ac94"))
    x = 470
    girl(c, x, 1300, 1.35, hat=True, pack=True, look=0.6, mouth="smile", walk=t * 6, arms=[(-26, -76), (-40, -70)],
         key="g1")
    suitcase(c, x - 58 * 1.35, 1302, 0.6 * 1.35, "su1", tilt=0.15)


# ================================================================ 2 可这座城，去了三次
def m02(c, t):
    """风景停在一座山城：楼一层叠一层，轻轨从楼中间穿过去。她停下来，仰头看。"""
    city(c, t, rail=prog(t, 0.3, 3.0))
    shape(c, rect(-20, 1400, W + 40, 600), hexc("c8bca8"), "plaza", lw=3)
    go = 1 - ease_out(prog(t, 0.0, 1.0))
    x = lerp(560, 480, go)
    girl(c, x, 1620, 1.25, hat=True, pack=True, look=0.3, look_up=0.6 * ease_io(prog(t, 0.8, 1.0)), mouth="o",
         walk=t * 6 if go > 0.05 else None, arms=[(-26, -76), (-40, -70)], key="g2")
    suitcase(c, x - 58 * 1.25, 1622, 0.6 * 1.25, "su2", tilt=0.15 if go > 0.05 else 0.0)


# ================================================================ 3 前两次：一大桌人，两顿火锅
def hotpot(c, t, var):
    wall = (hexc("c8b8a8"), hexc("b8bcc0"))[var]
    fill_all(c, wall)
    with keep():
        for j in range(3):                                         # 店里挂着的灯
            lx = (300, 540, 780)[j] + var * 60
            line(c, [(lx, 0), (lx, 300 + 40 * (j % 2))], f"hl{var}{j}", 3, hexc("5a4a40"))
            shape(c, ell(lx, 330 + 40 * (j % 2), 46, 50, 16), hexc("d86a4a"), f"hla{var}{j}", lw=2)
            glow(c, lx, 340, 140, WARM, 0.25)
    shape(c, rect(-20, 1330, W + 40, 700), darker(wall, 0.8), "hfl", lw=3)
    seats = ((200, 420, 700, 880), (180, 380, 600, 800, 940))[var]
    me = (700, 380)[var]
    for k, x in enumerate(seats):                                  # 围坐在桌子后面的一大桌人
        if x == me:
            girl(c, x, 1150, 1.25, sit=True, legs=False, hat=False, pack=False, look=lerp(0.5, -0.5, x / W),
                 mouth="smile" if math.sin(t * 2 + k) > 0 else "o", key=f"g3{var}")
        else:
            silhouette(c, x, 1262, 1.3, f"hs{var}{k}", a=0.8)
    shape(c, [(100, 1230), (980, 1230), (960, 1400), (120, 1400)], hexc("e8e0d4"), "hcloth", lw=3)  # 大圆桌
    shape(c, ell(540, 1230, 440, 90, 30), hexc("8a5a3a"), "htop", lw=3)
    shape(c, ell(540, 1215, 150, 42, 24), hexc("4a4040"), "hpot", lw=3)
    shape(c, ell(540, 1206, 128, 28, 22), CHILI, "hsoup", lw=1.6)
    with keep():
        for j in range(10):                                        # 咕嘟冒泡
            ph = (t * 1.8 + j / 10) % 1
            circle(c, 440 + j * 22, 1204 - ph * 10, 7 * (1 - ph) + 2, hexc("f2805a"), a=1 - ph)
        for j in range(5):                                         # 热气往上冒
            ph = (t * 0.6 + j / 5) % 1
            line(c, [(470 + j * 34 + 10 * math.sin(ph * 6), 1170 - ph * 300),
                     (480 + j * 34 + 10 * math.sin(ph * 6 + 1), 1130 - ph * 300)], f"hst{j}", 3.4, (1, 1, 1),
                 alpha=0.55 * (1 - ph))
        for k, x in enumerate(seats):                              # 筷子伸进锅里涮
            dip = 0.5 + 0.5 * math.sin(t * 2.6 + k * 1.7)
            ex = lerp(x, 540 + (x - 540) * 0.2, 0.6 + 0.4 * dip)
            line(c, [(x + (20 if x < 540 else -20), 1100), (lerp(x, ex, 0.5), lerp(1130, 1190, dip))], f"hcp{k}", 3.4, hexc("c8a070"))


def m03(c, t):
    """偏灰一点：一大桌人围着一锅红汤涮，她坐在里面；画面一闪，换了一桌、换了一群人，还是一锅火锅。"""
    var = 0 if t < 3.4 else 1
    with grade(sat=0.62, warm=0.0):
        hotpot(c, t, var)
    flash = 1 - prog(t, 3.4, 0.35) if t >= 3.4 else 0
    if flash > 0:
        veil(c, (1, 1, 1), 0.7 * flash)


# ================================================================ 4 这次不一样，是跟她一起去的
def m04(c, t):
    """颜色暖起来。长长的梯坎，她爬得直喘气；好朋友一步两级往上跳，停下来回头，笑着等她。"""
    stairs_bg(c, t)
    with keep():
        glow(c, 700, 300, 520, WARM, 0.3)
    cy = lerp(1840, 1560, ease_io(prog(t, 0.0, 6.8)))
    girl(c, 520, cy, 1.4, hat=True, pack=True, look=0.3, look_up=0.5, mouth="o", walk=t * 4, key="me2",
         head_down=6)
    breath_ph = (t / 0.6) % 1
    with keep():                                                   # 喘气
        shape(c, ell(560 + breath_ph * 30, cy - 260 - breath_ph * 30, 10 + breath_ph * 14, 8 + breath_ph * 8, 10),
              (1, 1, 1), "pant", lw=0.8, alpha=0.6 * (1 - breath_ph))
    hop = abs(math.sin(t * 3.2)) * 30
    fy = lerp(1300, 1000, ease_io(prog(t, 0.0, 3.0))) - hop
    wait = t > 3.0                                                 # 停下来回头，笑着等她
    friend(c, 620, fy + (hop if wait else 0), 1.25, key="fr2", look=-0.8, mouth="laugh", walk=None if wait else t * 7)


# ================================================================ 5 一路上，她都在讲小时候的事
def m05(c, t):
    """老街上两人并排走，好朋友边走边讲；身边叠出暖色的回忆：小时候的她蹦蹦跳跳跑过同一个路口。"""
    old_street(c, t)
    walk = t * 5
    girl(c, 760, 1260, 1.45, hat=True, pack=True, look=-0.7, mouth="smile", walk=walk, key="me3")
    talk = math.sin(t * 8) > 0
    friend(c, 560, 1260, 1.45, key="fr3", look=0.6, mouth="laugh" if talk else "o", walk=walk)

    def kid():
        hop = abs(math.sin(t * 6)) * 22
        kx = lerp(60, 400, prog(t, 1.2, 3.4))
        local(c, kx, 1250 - hop, 0.85, "kid5", hexc("f29a8a"), FHAIR, "pony", look=0.6, mouth="laugh", walk=t * 9,
              run=True)
    memory(c, ease_io(prog(t, 1.0, 1.0)), kid)


# ================================================================ 6–7 她从小吃到大的小摊
def snack_stall(c, t):
    vgrad(c, -200, 1100, [(0, hexc("f2c8a0")), (1, hexc("fbeede"))], -300, W + 300)
    shape(c, rect(-20, 300, W + 40, 120), hexc("c8584a"), "awn", lw=2.4)
    for k in range(9):
        shape(c, [(k * 130, 420), (k * 130 + 65, 470), (k * 130 + 130, 420)], hexc("f2e2d0"), f"awt{k}", lw=1.6)
    with keep():
        for k in range(3):                                         # 檐下的红灯笼
            lx = 220 + k * 320
            line(c, [(lx, 470), (lx, 520)], f"lnw{k}", 2.4, INK)
            shape(c, ell(lx, 570, 44, 52, 16), hexc("d8483a"), f"ln{k}", lw=2)
            glow(c, lx, 570, 110, WARM, 0.3)
    shape(c, rect(80, 820, 920, 40), hexc("8c6a4a"), "stall", lw=2.6)      # 后面的摊子
    for x in (110, 960):
        line(c, [(x, 860), (x, 1000)], f"sl{x}", 8, hexc("6a4a32"))
    with keep():
        for j in range(4):
            ph = (t * 0.5 + j / 4) % 1
            line(c, [(300 + j * 160, 800 - ph * 160), (310 + j * 160, 760 - ph * 160)], f"sts{j}", 3, (1, 1, 1),
                 alpha=0.5 * (1 - ph))
    shape(c, rect(-20, 1000, W + 40, 1000), hexc("b8a888"), "sfg", lw=3)
    # 中间一张矮桌，两张小凳子
    shape(c, rect(370, 1140, 340, 26), WOOD, "lt", lw=2.6)
    for x in (390, 690):
        line(c, [(x, 1166), (x, 1252)], f"ltl{x}", 7, darker(WOOD, 0.85))
    for sx_, k in ((260, "L"), (820, "R")):
        shape(c, rect(sx_ - 56, 1180, 112, 18), WOOD, f"stool{k}", lw=2)
        for sg in (-1, 1):
            line(c, [(sx_ + sg * 42, 1198), (sx_ + sg * 42, 1250)], f"stl{k}{sg}", 6, darker(WOOD, 0.85))
    # 一碗红红的小面、一碗抄手、一碗冰冰凉凉的甜点
    for k, x in enumerate((440, 540, 640)):
        shape(c, ell(x, 1132, 46, 16, 16), hexc("f6f2ea"), f"bw{k}", lw=2.2)
        shape(c, ell(x, 1124, 38, 10, 14), (CHILI, hexc("d8583a"), hexc("ece4cc"))[k], f"bs{k}", lw=1.4)
    with keep():
        for j in range(4):
            line(c, [(416 + j * 14, 1124), (420 + j * 14, 1108)], f"nd{j}", 2.2, hexc("f2d27a"))
        for j in range(3):
            shape(c, ell(522 + j * 18, 1120, 9, 6, 10), hexc("f8f2e8"), f"ws{j}", lw=1.2)
        for j in range(4):
            circle(c, 622 + j * 12, 1122, 3.4, hexc("8a5a3a"))
        for k, x in enumerate((440, 540)):
            ph = (t * 0.7 + k * 0.5) % 1
            line(c, [(x - 6, 1100 - ph * 80), (x + 2, 1070 - ph * 80)], f"bst{k}", 2.4, (1, 1, 1), alpha=0.6 * (1 - ph))


def m06(c, t):
    """小摊前的小凳子上，两个人围着一张矮桌，吃她从小吃到大的东西。"""
    snack_stall(c, t)
    chew = math.sin(t * 5)
    friend(c, 260, 1180, 1.4, key="fr6", sit=True, look=0.6, mouth="laugh" if chew > 0 else "smile")
    girl(c, 820, 1180, 1.4, sit=True, hat=True, pack=False, look=-0.6, mouth="laugh" if chew < 0 else "smile",
         key="me6")


def m07(c, t):
    """她吃得很香，一点不怕辣；下一刻捂着肚子皱起脸，好朋友在旁边笑出声。"""
    snack_stall(c, t + 4.0)
    if t < 3.4:
        friend(c, 260, 1180, 1.4, key="fr7", sit=True, look=0.7, mouth="smile")
        girl(c, 820, 1180, 1.4, sit=True, hat=True, pack=False, look=-0.6, mouth="laugh", key="me7",
             head_down=4 * abs(math.sin(t * 4)))
        with keep():                                               # 吃得香：头顶冒两朵小热气
            for j in range(2):
                ph = (t * 1.1 + j / 2) % 1
                shape(c, ell(800 + j * 50, 1180 - 260 * 1.4 + 52 * 1.4 - ph * 50, 8 * (1 - ph) + 3, 6, 8),
                      hexc("f2805a"), f"hot{j}", lw=0, edge=False, alpha=0.8 * (1 - ph))
        return
    u = t - 3.4
    laugh = abs(math.sin(u * 7)) * 6
    friend(c, 260, 1180 - laugh, 1.4, key="fr7b", sit=True, look=0.8, mouth="laugh")
    girl(c, 820, 1180, 1.4, sit=True, hat=True, pack=False, look=-0.3, mouth="o", head_down=10, key="me7b",
         eyes_closed=True, arms=[(-4, -96), (12, -92)])
    with keep():                                                   # 肚子里咕噜咕噜
        for j in range(3):
            ph = (u * 1.4 + j / 3) % 1
            r = 10 + ph * 22
            pts = [(820 + r * math.cos(a), 1180 - 30 + r * 0.6 * math.sin(a))
                   for a in [i / 10 * 2 * math.pi * 0.8 + j for i in range(11)]]
            line(c, pts, f"gr{j}", 2.4, hexc("8a7a6a"), alpha=0.8 * (1 - ph))


# ================================================================ 8–9 夜里挤在一张床上
def bubble_icon(c, k, x, y, a):
    with group_alpha(c, a), keep():
        shape(c, ell(x, y, 64, 56, 20), (1, 1, 1), f"bb{k}", lw=2.2)
        kind = k % 4
        if kind == 0:                                              # 一碗面
            shape(c, ell(x, y + 8, 30, 12, 14), hexc("f6f2ea"), f"bi{k}", lw=1.8)
            shape(c, ell(x, y + 4, 24, 7, 12), CHILI, f"bis{k}", lw=1.2)
            line(c, [(x - 6, y + 2), (x + 6, y - 26)], f"bic{k}", 2.4, hexc("c8a070"))
        elif kind == 1:                                            # 一串灯笼
            for j in range(3):
                shape(c, ell(x - 26 + j * 26, y + (j % 2) * 6, 11, 13, 12), hexc("d8483a"), f"bil{k}{j}", lw=1.4)
        elif kind == 2:                                            # 一段梯坎
            pts = [(x - 34, y + 24)]
            for j in range(4):
                pts += [(x - 34 + j * 17, y + 24 - (j + 1) * 12), (x - 17 + j * 17, y + 24 - (j + 1) * 12)]
            line(c, pts, f"bis{k}", 2.6, hexc("8a7a6a"))
        else:                                                      # 一条江
            for j in range(2):
                line(c, [(x - 34 + i * 8, y - 4 + j * 14 + 4 * math.sin(i * 0.9)) for i in range(9)], f"biw{k}{j}",
                     2.4, hexc("6aa8cc"))


def m08(c, t):
    """灯关了，两人并排躺着。好朋友说个不停，头顶冒出一个个小气泡；窗外的灯一格一格熄掉，她还在说。"""
    dark = ease_io(prog(t, 0.8, 1.2))
    bedroom(c, t, dark, off=prog(t, 2.6, 4.8) * 0.85)
    talk = math.sin(t * 9) > 0
    friend(c, 380, 1180, 1.3, key="fr8", look=0.8, mouth="laugh" if talk else "o")
    girl(c, 700, 1180, 1.3, hat=False, pack=False, look=-0.8, mouth="laugh" if math.sin(t * 1.3) > 0.6 else "smile",
         key="me8")
    quilt(c, dark)
    if dark > 0:
        veil(c, (0.02, 0.02, 0.06), 0.3 * dark)
    for k in range(6):                                             # 说个不停：一个个小气泡往上飘
        u = prog(t, 0.4 + k * 1.15, 2.6)
        if 0 < u < 1:
            a = 0.9 * math.sin(math.pi * u)
            bubble_icon(c, k, 400 + 90 * math.sin(k * 2.1) + u * 60, lerp(860, 520, u), a)


def m09(c, t):
    """两人都睡着了，脸朝着对方；镜头退到窗外，一大片暗下来的山城里，只有这一扇小窗还亮着。"""
    if t < 3.4:
        bedroom(c, t, 1.0, off=0.85)
        friend(c, 380, 1180, 1.3, key="fr9", look=0.8, eyes_closed=True, mouth="smile", tilt=0.12)
        girl(c, 700, 1180, 1.3, hat=False, pack=False, look=-0.8, eyes_closed=True, mouth="smile", tilt=-0.12, key="me9")
        quilt(c, 1.0)
        veil(c, (0.02, 0.02, 0.06), 0.3)
        return
    u = t - 3.4
    z = lerp(1.6, 1.0, ease_io(prog(u, 0.0, 4.0)))
    with cam(c, 540, 1000, z):
        city(c, t, night=1.0, lit=-0.62)
        with keep():                                               # 那一扇亮着的小窗
            glow(c, 560, 1010, 160, WARM, 0.8)
            shape(c, rect(530, 980, 60, 64), hexc("ffd98a"), "ourwin", lw=2)


# ================================================================ 10–11 玩累了，在长椅上睡着
def bench_street(c, t):
    vgrad(c, -200, 1150, [(0, hexc("f2d8b0")), (1, hexc("fbf0e0"))], -300, W + 300)
    shape(c, rect(560, 300, 560, 900), hexc("d8c4a4"), "bwall", lw=3)      # 后面的老墙和往上走的梯坎
    for k in range(9):
        y = 1150 - k * 64
        shape(c, rect(-20 + k * 50, y, 600 - k * 50, 64), mix(hexc("c8bca8"), hexc("d8d0c0"), (k % 2) * 0.4),
              f"bst{k}", lw=1.8, amp=0.5)
    with keep():
        for k in range(2):                                         # 楼梯上慢慢走过的路人
            p = ((t * 0.08 + k * 0.5) % 1)
            sx = lerp(520, 40, p)
            silhouette(c, sx, 1150 - p * 520 + 12, 0.7, f"bp{k}", walk=t * 4 + k, a=0.55)
    shape(c, rect(-20, 1150, W + 40, 900), hexc("c8b898"), "bgr", lw=3)
    line(c, [(980, 1150), (980, 200)], "btr", 26, hexc("8a6a4a"))         # 一棵树
    with keep():
        for k, (x, y, r) in enumerate(((900, 200, 170), (1040, 300, 150), (820, 360, 130))):
            shape(c, ell(x, y, r, r * 0.8, 20), hexc("8ab070"), f"bl{k}", lw=2.4)
    # 长椅
    shape(c, rect(200, 1020, 680, 24), WOOD, "bback", lw=2.4)
    shape(c, rect(200, 1070, 680, 24), WOOD, "bback2", lw=2.4)
    for x in (230, 850):
        line(c, [(x, 1020), (x, 1290)], f"bpost{x}", 9, darker(WOOD, 0.8))
    shape(c, rect(190, 1196, 700, 28), WOOD, "bseat", lw=2.6)


def bench_light(c, t):
    with keep():                                                   # 树影一点点移过去
        r = random.Random(12)
        for k in range(10):
            x = (r.uniform(0, W) + t * 18) % (W + 200) - 100
            y = r.uniform(1240, 1700)
            shape(c, ell(x, y, r.uniform(30, 60), 12, 14), hexc("fff6dc"), f"dap{k}", lw=0, edge=False, alpha=0.45)


def m10(c, t):
    """出去玩的路上，她玩累了，靠在长椅上睡着了；好朋友坐在旁边，没叫醒她，静静地等着。"""
    bench_street(c, t)
    breathe = math.sin(t * 1.6) * 2
    glance = 0.6 if 2.6 < t < 4.4 else -0.5                      # 看看街上，又转头看看她
    friend(c, 400, 1196, 1.45, key="fr10", sit=True, look=glance, mouth="smile")
    girl(c, 680, 1196 + breathe, 1.45, sit=True, hat=False, pack=False, look=-0.2, eyes_closed=True, tilt=0.2,
         head_down=8, mouth="smile", key="me10")
    hat_item(c, 696, 1196 + 30, 0.8, "lap10")                     # 帽子滑到膝盖上
    bench_light(c, t)


def m11(c, t):
    """她醒过来，两人相视一笑；起身并肩走下那段梯坎。轻轨开过山城，楼一层层退远。"""
    if t < 3.4:
        bench_street(c, t + 6.8)
        wake = ease_io(prog(t, 0.4, 0.8))
        friend(c, 400, 1196, 1.45, key="fr11", sit=True, look=0.6, mouth="laugh" if t > 1.4 else "smile")
        girl(c, 680, 1196, 1.45, sit=True, hat=False, pack=False, look=lerp(-0.2, -0.6, wake), eyes_closed=t < 0.6,
             tilt=0.2 * (1 - wake), head_down=8 * (1 - wake), mouth="laugh" if t > 1.4 else "o", key="me11")
        hat_item(c, 696, 1196 + 30, 0.8, "lap11")
        bench_light(c, t + 6.8)
        return
    if t < 6.8:
        u = t - 3.4
        stairs_bg(c, u)
        with keep():
            glow(c, 540, 500, 520, WARM, 0.35)
        down = ease_io(prog(u, 0.0, 3.4))
        y = lerp(1100, 1760, down)
        s = lerp(0.95, 1.35, down)
        friend(c, 480, y, s, key="fr11b", look=0.4, mouth="laugh", walk=u * 6)
        girl(c, 640, y, s, hat=True, pack=True, look=-0.4, mouth="smile", walk=u * 6, key="me11b")
        return
    u = t - 6.8
    z = lerp(1.0, 0.85, ease_io(prog(u, 0.0, 3.4)))
    with cam(c, 540, 960, z):
        city(c, t, rail=prog(u, 0.0, 3.4), warm=0.6)


# ================================================================ 片尾
_END = {}


def end_still():
    if "s" not in _END:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(80.0)
        with grade(sat=1.0, dark=0.0, warm=0.05):
            m09(cc, 8.4)
        _END["s"] = surf
    return _END["s"]


def outro(c, t):
    book_outro(c, t, end_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第八章 · 完")

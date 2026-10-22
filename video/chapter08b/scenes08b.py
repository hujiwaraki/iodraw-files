"""第八章 · 她的小时候 —— 分镜实现（竖屏 1080×1920）。每个函数 fn(c, t)，t 为镜头内本地时间。

这一次不是一个人：好朋友带她回自己长大的山城。楼一层叠一层、梯坎上上下下、轻轨从楼中间穿过去。
一路听她讲小时候，讲得最多的是外婆（蜡笔画的回忆叠在现实里）→ 见到外婆，一大桌菜、街上的小吃
→ 晚上挤在一张床上聊到很晚 → 江边的台阶上各自发呆 → 离开时外婆塞了一大袋吃的。
画面里不写字、不写真实地名；不用雾。好朋友：青绿色外套、马尾，有脸有颜色。外婆：白头发、碎花围裙。
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
GRAN = hexc("8a6a8a")                     # 外婆的衣服
APRON = hexc("f2e2d8")
WHITE_H = hexc("e8e4dc")
CHILI = hexc("c8402e")
WARM = hexc("ffd08a")
WOOD = hexc("9a6a44")


def friend(c, x, y, s, key="fr", **kw):
    kw.setdefault("look", -0.4)
    local(c, x, y, s, key, FRIEND, FHAIR, "pony", **kw)


def gran(c, x, y, s, key="gm", **kw):
    kw.setdefault("look", 0.2)
    kw.setdefault("mouth", "laugh")
    local(c, x, y, s, key, GRAN, WHITE_H, "granny", age=1.0, **kw)
    with keep():                                                   # 碎花围裙
        sx = s
        shape(c, [(x - 26 * sx, y - 120 * sx), (x + 26 * sx, y - 120 * sx), (x + 32 * sx, y - 40 * sx),
                  (x - 32 * sx, y - 40 * sx)], APRON, key + "ap", lw=1.8)
        r = random.Random(len(key))
        for k in range(6):
            circle(c, x + r.uniform(-20, 20) * sx, y - r.uniform(50, 110) * sx, 3 * sx, hexc("d88a8a"))


def umbrella_illus(c, cx, cy):
    """章节页小插画：一把歪向一边的伞。"""
    with keep():
        c.save()
        c.translate(cx, cy + 20)
        c.rotate(-0.35)
        pts = [(math.cos(a) * 70, -abs(math.sin(a)) * 46) for a in [math.pi * (1 - i / 16) for i in range(17)]]
        shape(c, pts + [(70, 0), (-70, 0)], hexc("d86a5a"), "ill", lw=3, amp=0.5)
        line(c, [(0, -40), (0, 60), (10, 70), (20, 62)], "illh", 3, INK)
        c.restore()


def intro(c, t):
    book_intro(c, t, "第八章", "她的小时候", umbrella_illus)


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


def city(c, t, night=0.0, rail=None, warm=0.0):
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
            building(c, x, yb, w_, h_, hexc(col), f"b{li}_{k}", lit=0.3, night=night, seed=li * 50 + k)
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


def n01(c, t):
    """山城：楼一层叠一层，一列轻轨从两栋楼中间穿过去；她和好朋友拖着行李走出车站。"""
    city(c, t, rail=prog(t, 0.4, 4.4))
    shape(c, rect(-20, 1400, W + 40, 600), hexc("c8bca8"), "plaza", lw=3)
    go = ease_io(prog(t, 3.2, 3.0))
    x = lerp(300, 620, go)
    friend(c, x + 150, 1560, 1.25, key="fr1", walk=t * 6 if go > 0 else None, look=-0.6, mouth="laugh")
    girl(c, x, 1560, 1.25, hat=True, pack=True, look=0.6, look_up=0.4 * (1 - go), mouth="o" if go < 0.3 else "smile",
         walk=t * 6 if go > 0 else None, key="me1")


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


def n02(c, t):
    """长长的梯坎，她爬得直喘气；好朋友一步两级往上跳，回头笑着朝她招手。"""
    stairs_bg(c, t)
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


# ================================================================ 她的小时候（蜡笔画的回忆叠在现实里）
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


def n03(c, t):
    """老街上两人并排走；好朋友讲话时，她身边叠出一个蜡笔画的小女孩，被外婆牵着手，蹦蹦跳跳。"""
    old_street(c, t)
    walk = t * 5
    girl(c, 760, 1260, 1.45, hat=True, pack=True, look=-0.7, mouth="smile", walk=walk, key="me3")
    talk = math.sin(t * 8) > 0
    friend(c, 560, 1260, 1.45, key="fr3", look=0.6, mouth="laugh" if talk else "o", walk=walk)

    def kid():
        hop = abs(math.sin(t * 5)) * 16
        local(c, 210, 1250 - hop, 0.85, "kid3", hexc("f29a8a"), FHAIR, "pony", look=0.5, mouth="laugh",
              arms=[(-24, -78), (30, -96)], walk=walk)
        gran(c, 120, 1250, 1.25, key="gm3", look=0.5, arms=[(-24, -78), (40, -80)], walk=walk)
    memory(c, ease_io(prog(t, 2.6, 1.4)), kid)


def n04(c, t):
    """蜡笔回忆：下雨的梯坎，外婆的伞歪向小女孩；路过的邻居小孩，外婆顺手递过去一块糖。"""
    with grade(sat=0.8, warm=0.45):
        stairs_bg(c, t, rain=0.4, crayon=True)
        with keep():
            glow(c, 540, 1300, 500, hexc("ffe0b0"), 0.35)
        if t < 3.4:
            y = 1700
            local(c, 600, y, 1.0, "kid4", hexc("f29a8a"), FHAIR, "pony", look=-0.3, mouth="smile", walk=t * 4)
            gran(c, 470, y, 1.4, key="gm4", look=0.5, arms=[(-24, -78), (36, -200)], walk=t * 4)
            with keep():                                           # 伞歪向小女孩
                c.save()
                c.translate(540, y - 300)
                c.rotate(0.35)
                pts = [(math.cos(a) * 170, -abs(math.sin(a)) * 90) for a in [math.pi * (1 - i / 18) for i in range(19)]]
                shape(c, pts + [(170, 0), (-170, 0)], hexc("d86a5a"), "umb4", lw=2.6)
                c.restore()
                line(c, [(470 + 36 * 1.4, y - 200 * 1.4), (540, y - 300)], "umbh", 4, INK)
            rs = random.Random(4)
            with keep():
                for k in range(40):
                    x = rs.uniform(0, W)
                    yy = (rs.uniform(0, 1900) + t * 1100) % 1900
                    if 330 < x < 760 and yy < y and yy > y - 320 and x > 420:
                        continue                                   # 伞下面没有雨
                    line(c, [(x, yy), (x - 6, yy + 26)], f"r4{k}", 1.6, hexc("9ab0c8"), alpha=0.5)
        else:
            u = t - 3.4
            gran(c, 470, 1600, 1.4, key="gm4b", look=0.6, arms=[(-24, -78), (lerp(30, 70, ease_io(prog(u, 0.3, 0.8))), -110)])
            silhouette(c, 700, 1600, 0.9, "nb4", a=0.6)            # 路过的邻居小孩
            give = ease_io(prog(u, 0.3, 0.8))
            with keep():
                circle(c, lerp(470 + 30 * 1.4, 640, give), 1600 - 110 * 1.4, 10, hexc("f2c04a"))


def n05(c, t):
    """老房子门口，外婆笑着迎出来，一手拉一个，把两人拉进屋。"""
    vgrad(c, -200, 1100, [(0, hexc("bcd4e4")), (1, hexc("f4eee2"))], -300, W + 300)
    shape(c, rect(80, 420, 920, 840), hexc("d8c4a4"), "house", lw=3)
    shape(c, [(40, 440), (540, 200), (1040, 440)], hexc("6a5a50"), "roof", lw=3)
    shape(c, rect(420, 760, 240, 480), hexc("8a5a3a"), "door5", lw=3)
    with keep():
        shape(c, rect(436, 776, 208, 464), hexc("ffe8b8"), "doorl", lw=0, edge=False, alpha=0.6)
        glow(c, 540, 1000, 260, WARM, 0.4)
    for x in (180, 760):
        shape(c, rect(x, 560, 140, 160), hexc("9fc5e8"), f"hw{x}", lw=2)
    shape(c, rect(-20, 1240, W + 40, 700), hexc("b8ac98"), "yard", lw=3)
    out = ease_io(prog(t, 0.3, 1.4))
    hold = ease_io(prog(t, 1.8, 0.8))
    gx = lerp(540, 540, out)
    gran(c, gx, 1250, 1.5, key="gm5", look=0.0, arms=[(lerp(-24, -70, hold), -80), (lerp(24, 70, hold), -80)])
    girl(c, 760, 1260, 1.5, hat=True, pack=True, look=-0.7, mouth="smile", key="me5",
         arms=[(lerp(-24, -50, hold), -80), (24, -78)])
    friend(c, 320, 1260, 1.5, key="fr5", look=0.7, mouth="laugh", arms=[(-24, -78), (lerp(24, 50, hold), -80)])


# ================================================================ 家乡的味道
def table_feast(c, t):
    fill_all(c, hexc("e8d8c0"))
    with keep():
        glow(c, 540, 600, 520, WARM, 0.45)
        line(c, [(540, 0), (540, 420)], "lampw", 3, hexc("3a3a3a"))
        shape(c, ell(540, 440, 90, 40, 18, math.pi, 2 * math.pi), hexc("e8a050"), "lamp", lw=2)
    shape(c, rect(-20, 1240, W + 40, 700), hexc("b8a080"), "fl6", lw=3)
    serve = math.sin(t * 2.4)
    gran(c, 540, 1240, 1.7, key="gm6", look=0.3 * serve, arms=[(-24, -78), (40 + 16 * serve, -96)])
    shape(c, rect(300, 1130, 480, 26), WOOD, "tb6b", lw=2.6)       # 外婆站在桌子后面，桌子挡住她的下半身
    shape(c, rect(310, 1156, 460, 84), darker(WOOD, 0.9), "tb6f", lw=2.4)
    for k, (x, col) in enumerate(((370, "c8402e"), (455, "6fa860"), (540, "d89a4a"), (625, "c8402e"), (710, "e8c860"))):
        shape(c, ell(x, 1122, 42, 14, 16), hexc("f6f2ea"), f"pl{k}", lw=2)
        shape(c, ell(x, 1116, 36, 10, 14), hexc(col), f"fd{k}", lw=1.4)
        with keep():
            for j in range(2):
                ph = (t * 0.6 + j / 2 + k * 0.2) % 1
                line(c, [(x - 8 + j * 14, 1100 - ph * 90), (x - 2 + j * 14, 1070 - ph * 90)], f"st6{k}{j}", 2.4,
                     (1, 1, 1), alpha=0.6 * (1 - ph))
    for sx_, k in ((210, "L"), (870, "R")):                         # 两张小凳子
        shape(c, rect(sx_ - 60, 1150, 120, 18), WOOD, f"stool{k}", lw=2)
        for sg in (-1, 1):
            line(c, [(sx_ + sg * 46, 1168), (sx_ + sg * 46, 1240)], f"stl{k}{sg}", 6, darker(WOOD, 0.85))
    friend(c, 210, 1150, 1.3, key="fr6", sit=True, look=0.6, mouth="laugh")
    girl(c, 870, 1150, 1.3, sit=True, hat=False, pack=False, look=-0.6, mouth="laugh", key="me6")


def street_food(c, t):
    vgrad(c, -200, 1100, [(0, hexc("f2c8a0")), (1, hexc("fbeede"))], -300, W + 300)
    shape(c, rect(-20, 300, W + 40, 120), hexc("c8584a"), "awn", lw=2.4)
    for k in range(9):
        shape(c, [(k * 130, 420), (k * 130 + 65, 470), (k * 130 + 130, 420)], hexc("f2e2d0"), f"awt{k}", lw=1.6)
    shape(c, rect(-20, 1100, W + 40, 900), hexc("b8a888"), "sfg", lw=3)
    shape(c, rect(80, 900, 920, 40), hexc("8c6a4a"), "stall", lw=2.6)
    for x in (110, 960):
        line(c, [(x, 940), (x, 1100)], f"sl{x}", 8, hexc("6a4a32"))
    # 一碗红红的小面、一锅咕嘟冒泡的红汤、一碗冰冰凉凉的甜点
    shape(c, ell(260, 880, 90, 30, 18), hexc("f6f2ea"), "b1", lw=2.4)
    shape(c, ell(260, 870, 72, 20, 16), CHILI, "b1s", lw=1.6)
    with keep():
        for j in range(5):
            line(c, [(214 + j * 22, 870), (220 + j * 22, 850)], f"nd{j}", 2.4, hexc("f2d27a"))
    shape(c, ell(540, 880, 140, 40, 22), hexc("5a4a40"), "pot", lw=2.6)
    shape(c, ell(540, 864, 120, 26, 20), CHILI, "pots", lw=1.6)
    with keep():
        for j in range(8):
            ph = (t * 1.6 + j / 8) % 1
            circle(c, 440 + j * 28, 860 - ph * 14, 6 * (1 - ph) + 2, hexc("f2805a"), a=1 - ph)
        for j in range(4):
            ph = (t * 0.7 + j / 4) % 1
            line(c, [(480 + j * 40, 820 - ph * 140), (490 + j * 40, 780 - ph * 140)], f"st7{j}", 3, (1, 1, 1),
                 alpha=0.6 * (1 - ph))
    shape(c, ell(820, 880, 80, 28, 18), hexc("f6f2ea"), "b3", lw=2.4)
    shape(c, ell(820, 870, 62, 18, 14), hexc("e8e0c8"), "b3s", lw=1.4)
    with keep():
        for j in range(5):
            circle(c, 790 + j * 14, 866, 5, hexc("c88a5a"))
    friend(c, 360, 1260, 1.5, key="fr7", look=0.6, mouth="laugh", arms=[(-24, -78), (56, -96)])
    girl(c, 700, 1260, 1.5, hat=True, pack=True, look=-0.4, mouth="o", key="me7")


def n06(c, t):
    """外婆家的方桌上热气腾腾，外婆不停往碗里夹菜；接着是街边的小摊。"""
    if t < 3.4:
        table_feast(c, t)
    else:
        street_food(c, t - 3.4)


def n07(c, t):
    """她被辣得直扇舌头，好朋友笑得前仰后合，递过来一碗甜的。"""
    street_food(c, t + 3.0)
    with keep():                                                   # 冒汗
        for j in range(3):
            ph = (t * 1.2 + j / 3) % 1
            shape(c, ell(700 + (j - 1) * 40, 1260 - 250 * 1.5 + ph * 40, 6, 9, 10), hexc("bcd8f0"), f"sw{j}", lw=1,
                  alpha=1 - ph)
        for j in range(3):                                         # 辣得冒火
            ph = (t * 2 + j / 3) % 1
            shape(c, ell(700 + (j - 1) * 12, 1260 - 190 * 1.5 - ph * 30, 8 * (1 - ph) + 3, 5, 8), hexc("f2805a"),
                  f"hot{j}", lw=0, edge=False, alpha=1 - ph)


# ================================================================ 聊到很晚
def bedroom(c, t, dark=0.0):
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
                if r.random() < 0.7:
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


def n08(c, t):
    """夜里的小房间，两人并排躺在一张床上，盖着同一床被子。灯关了，两个人还在小声说话，偶尔一起笑出声。"""
    dark = ease_io(prog(t, 3.6, 1.2))
    bedroom(c, t, dark)
    with keep():
        if dark < 1:
            glow(c, 900, 700, 300, WARM, 0.45 * (1 - dark))
    talk_me = math.sin(t * 2.2) > 0
    friend(c, 380, 1180, 1.3, key="fr8", look=0.8, mouth="laugh" if (not talk_me and t > 6) else ("o" if not talk_me else "smile"))
    girl(c, 700, 1180, 1.3, hat=False, pack=False, look=-0.8, mouth="laugh" if t > 6 else ("o" if talk_me else "smile"),
         key="me8")
    quilt(c, dark)
    with keep():                                                   # 小声说话：一串轻轻的点
        a = 0.8
        x0 = 540 if talk_me else 520
        for j in range(3):
            ph = (t * 1.5 + j * 0.3) % 1
            circle(c, x0 - 30 + j * 30, 880 - ph * 40, 6, (1, 1, 1), a=a * (1 - ph))
    if dark > 0:
        veil(c, (0.02, 0.02, 0.06), 0.35 * dark)


def n09(c, t):
    """两人都睡着了，脸朝着对方；镜头退到窗外，一大片山城的灯火里，只有这一扇小窗还亮着暖暖的光。"""
    if t < 2.8:
        bedroom(c, t, 1.0)
        friend(c, 380, 1180, 1.3, key="fr9", look=0.8, eyes_closed=True, mouth="smile", tilt=0.12)
        girl(c, 700, 1180, 1.3, hat=False, pack=False, look=-0.8, eyes_closed=True, mouth="smile", tilt=-0.12, key="me9")
        quilt(c, 1.0)
        veil(c, (0.02, 0.02, 0.06), 0.35)
        return
    u = t - 2.8
    z = lerp(1.6, 1.0, ease_io(prog(u, 0.0, 3.6)))
    with cam(c, 540, 1000, z):
        city(c, t, night=1.0)
        with keep():                                               # 那一扇亮着的小窗
            glow(c, 560, 1010, 160, WARM, 0.8)
            shape(c, rect(530, 980, 60, 64), hexc("ffd98a"), "ourwin", lw=2)


# ================================================================ 江边 / 离开
def riverside(c, t):
    vgrad(c, -200, 1000, [(0, hexc("9fc8e8")), (1, hexc("eef0ea"))], -300, W + 300)
    r = random.Random(3)
    x = -40
    k = 0
    while x < W + 40:                                              # 对岸的楼
        w_, h_ = r.uniform(80, 140), r.uniform(160, 380)
        building(c, x, 820, w_, h_, hexc("c8c4bc"), f"ob{k}", seed=k)
        x += w_ + 10
        k += 1
    shape(c, rect(-20, 820, W + 40, 300), hexc("8aa8b8"), "river", lw=2.4)
    with keep():
        for j in range(4):
            y = 860 + j * 60
            line(c, [(xx, y + 6 * math.sin(xx * 0.02 + t * 1.5 + j)) for xx in range(-20, W + 40, 40)], f"rw{j}", 2,
                 (1, 1, 1), alpha=0.4)
        bx = (t * 40) % (W + 400) - 200                            # 江上慢慢开过去的船
        shape(c, [(bx - 90, 940), (bx + 90, 940), (bx + 70, 970), (bx - 70, 970)], hexc("e8e0d0"), "boat", lw=2)
        shape(c, rect(bx - 40, 900, 80, 40), hexc("f2f2f0"), "cabin", lw=2)
    for k in range(6):                                             # 一级一级的台阶
        shape(c, rect(-20, 1120 + k * 130, W + 40, 130), mix(hexc("c8bca8"), hexc("b8ac98"), (k % 2) * 0.5), f"rs{k}",
              lw=2)


def n10(c, t):
    """从背后看：两人并排坐在江边的台阶上，各自发呆，偶尔转头说一两句，看江上的船慢慢开过去。"""
    riverside(c, t)
    shape(c, rect(-20, 1180, W + 40, 800), hexc("b8ac98"), "ledge", lw=2.4)      # 她们坐着的那一级台阶
    turn = math.sin(t * 0.9)
    local(c, 420, 1180, 1.5, "fr10", FRIEND, FHAIR, "pony", view="back", sit=True, legs=False,
          look=0.4 if turn > 0.6 else 0.0)
    girl(c, 660, 1180, 1.5, view="back", hat=True, pack=False, sit=True, legs=False,
         look=-0.4 if turn < -0.6 else 0.0, key="me10")


def n11(c, t):
    """离开那天，外婆在门口往她们包里塞了一大袋吃的，一直挥手。轻轨开过江上的桥，楼一层层退远。"""
    if t < 3.4:
        vgrad(c, -200, 1100, [(0, hexc("bcd4e4")), (1, hexc("f4eee2"))], -300, W + 300)
        shape(c, rect(80, 420, 920, 840), hexc("d8c4a4"), "house", lw=3)
        shape(c, [(40, 440), (540, 200), (1040, 440)], hexc("6a5a50"), "roof", lw=3)
        shape(c, rect(420, 760, 240, 480), hexc("8a5a3a"), "door11", lw=3)
        shape(c, rect(-20, 1240, W + 40, 700), hexc("b8ac98"), "yard", lw=3)
        stuff = ease_io(prog(t, 0.2, 1.4))
        wave = math.sin(t * 8) * 30 if t > 1.8 else 0
        gran(c, 540, 1250, 1.5, key="gm11", look=0.5,
             arms=[(-24, -78), (40, -200 + wave)] if t > 1.8 else [(-24, -78), (lerp(30, 70, stuff), -110)])
        girl(c, 790, 1260, 1.5, hat=True, pack=True, look=-0.6, mouth="smile", key="me11")
        friend(c, 300, 1260, 1.5, key="fr11", look=0.6, mouth="laugh")
        with keep():                                               # 一大袋吃的
            bx = lerp(600, 880, stuff)
            by_ = lerp(1080, 1120, stuff)
            shape(c, [(bx - 40, by_), (bx + 40, by_), (bx + 50, by_ + 90), (bx - 50, by_ + 90)], hexc("f2e8d8"), "bag",
                  lw=2)
            for j in range(3):
                circle(c, bx - 20 + j * 20, by_ - 6, 12, hexc(["e88a5a", "f2c04a", "c8402e"][j]))
        return
    u = t - 3.4
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
            n09(cc, 6.6)
        _END["s"] = surf
    return _END["s"]


def outro(c, t):
    book_outro(c, t, end_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第八章 · 完")

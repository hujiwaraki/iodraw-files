"""第三章 · 第七稿新加的“重锤”一节：出租车上一路哭 → 坐在路边，头顶一大朵乌云 → （缓冲）乌云散开，天亮了
→ 一路走：头顶那朵小乌云跟着她，摔跤、踩进水坑、跳过一道沟，乌云才散 → 倒霉事照来，她撑开伞接着走
→ 前面是一整排更高的山：又回到了新手村。"""
import math
import random

from scenes03 import pull
from draw import *  # noqa: F401,F403

NIGHT = hexc("1f2540")
TAXI = hexc("3f8a84")


# ================================================================ 小道具
def umbrella(c, x, y, s, key, open_=1.0, col=hexc("e07a6a")):
    """伞：(x, y) 是伞柄顶端；open_ 从 0 到 1 撑开。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with keep():
        line(c, [(0, 0), (0, 110)], key + "h", 4, hexc("3a3a3a"))
        line(c, [(0, 110), (10, 122), (20, 112)], key + "hk", 4, hexc("3a3a3a"))
        w = lerp(18, 110, open_)
        h = lerp(90, 70, open_)
        pts = [(math.cos(a) * w, -abs(math.sin(a)) * h - (1 - open_) * 30) for a in
               [math.pi * (1 - i / 20) for i in range(21)]]
        pts += [(w - i * 2 * w / 6, 10 * math.sin(i * math.pi) * open_) for i in range(7)]
        shape(c, pts, col, key + "c", lw=2.4)
    c.restore()


def taxi(c, x, y, key, t=0.0, girl_in=True, sob=True):
    """侧面的出租车，车头朝右。(x, y) 是车底中点。后窗里，她小小地缩在后座。"""
    bob = math.sin(t * 9) * 2
    with keep():
        glow(c, x + 330, y - 60, 260, hexc("fff0b8"), 0.35)       # 车灯
    body = [(x - 300, y - 30 + bob), (x + 300, y - 30 + bob), (x + 310, y - 110 + bob), (x + 170, y - 120 + bob),
            (x + 100, y - 210 + bob), (x - 160, y - 210 + bob), (x - 240, y - 120 + bob), (x - 300, y - 110 + bob)]
    shape(c, body, TAXI, key + "b", lw=3)
    shape(c, rect(x - 40, y - 240 + bob, 80, 30), hexc("f2e6c0"), key + "sign", lw=2)    # 车顶灯（不写字）
    win_r = [(x + 10, y - 120 + bob), (x + 150, y - 120 + bob), (x + 92, y - 196 + bob), (x + 10, y - 196 + bob)]
    win_b = [(x - 150, y - 120 + bob), (x - 10, y - 120 + bob), (x - 10, y - 196 + bob), (x - 150, y - 196 + bob)]
    shape(c, win_r, hexc("2a3350"), key + "wr", lw=2)
    shape(c, win_b, hexc("3a3a52"), key + "wb", lw=2)
    if girl_in:                                                    # 后座上的她：低着头，肩膀一抖一抖
        c.save()
        spath(c, win_b, True)
        c.clip()
        with keep():
            glow(c, x - 80, y - 150 + bob, 120, hexc("ffd8a0"), 0.25)
        shake = math.sin(t * 15) * 3 if sob else 0.0
        girl(c, x - 80, y - 40 + bob + shake, 0.95, sit=True, legs=False, hat=False, head_down=16, look=0.3,
             mouth="flat", arms=[(-14, -60), (14, -60)], key=key + "g")
        c.restore()
        with keep():
            shape(c, win_b, hexc("9fb7d8"), key + "wg", lw=0, edge=False, alpha=0.18)
    for wx in (x - 190, x + 200):
        circle(c, wx, y - 20 + bob, 48, hexc("2a2a2a"))
        circle(c, wx, y - 20 + bob, 20, hexc("8a8a8a"))


def city_night(c, t, scroll=0.0, lamps=None, sky=0.0):
    """夜里的街：远处一排楼的剪影、路灯、马路。sky 从 0 到 1 慢慢变成天亮前的颜色。"""
    top = mix(NIGHT, hexc("6a7aa8"), sky)
    bot = mix(hexc("3a3f5c"), hexc("f2c8a8"), sky)
    vgrad(c, -200, 1300, [(0, top), (1, bot)], -300, W + 300)
    r = random.Random(3)
    x = -200 - (scroll * 0.25) % 260
    k = 0
    while x < W + 200:                                             # 远处的楼
        w_, h_ = 200 + r.uniform(-40, 60), r.uniform(240, 520)
        shape(c, rect(x, 1000 - h_, w_, h_ + 40), mix(hexc("2a3050"), hexc("8a8aa8"), sky), f"bd{k % 12}", lw=2)
        with keep():
            for j in range(int(h_ // 90)):
                if r.random() < 0.4 * (1 - sky):
                    shape(c, rect(x + 30 + (j % 2) * 80, 1000 - h_ + 40 + j * 80, 30, 36), hexc("f6d890"), f"bw{k}{j}",
                          lw=0, edge=False, alpha=0.7)
        x += w_ + 60
        k += 1
    shape(c, rect(-40, 1000, W + 80, 260), mix(hexc("4a4a5e"), hexc("a8a0a0"), sky), "walk3", lw=2.4)   # 人行道
    shape(c, rect(-40, 1260, W + 80, 700), mix(hexc("2e2e3a"), hexc("8a8488"), sky), "road3", lw=3)
    with keep():
        for j in range(8):                                         # 车道线
            lx = (j * 300 - scroll) % (W + 300) - 150
            line(c, [(lx, 1500), (lx + 140, 1500)], f"ln{j}", 6, hexc("d8d0b0"), alpha=0.6)
    if lamps is not None:
        for j, on in enumerate(lamps):
            lx = 140 + j * 400
            line(c, [(lx, 1010), (lx, 640)], f"lp{j}", 7, hexc("2a2a2a"))
            with keep():
                if on > 0:
                    glow(c, lx, 650, 240, hexc("ffd98a"), 0.5 * on)
                circle(c, lx, 646, 14, mix(hexc("8a8a8a"), hexc("fff0b8"), on))


# ================================================================ 8 出租车上一路哭；路边，头顶一大朵乌云
def x08(c, t):
    if t < 9.0:                                                    # 夜里下着雨，出租车开在长长的路上
        scroll = t * 700
        city_night(c, t, scroll=scroll)
        with keep():
            for j in range(4):                                     # 一盏盏往后退的路灯
                lx = W + 200 - (scroll * 1.0 + j * 420) % (W + 600)
                line(c, [(lx, 1010), (lx, 640)], f"lpm{j}", 7, hexc("2a2a2a"))
                glow(c, lx, 650, 240, hexc("ffd98a"), 0.45)
                circle(c, lx, 646, 14, hexc("fff0b8"))
        taxi(c, 540, 1420, "tx", t=t)
        rain(c, t, n=110, a=0.5, col=hexc("aab8d0"), seed=5)
        return
    u = t - 9.0                                                    # 出租车开走；她坐在路边，头顶压着一大朵乌云
    lamps = [1.0 - clamp((u - 3.0 - j * 1.6) * 3) for j in range(3)]
    city_night(c, u, lamps=lamps)
    tx = 540 + ease_in(prog(u, 0.0, 1.4)) * 1200
    if tx < W + 400:
        taxi(c, tx, 1420, "tx2", t=u, girl_in=False)
    suitcase(c, 700, 1160, 0.9, "su8")
    girl(c, 540, 1200, 1.45, sit=True, crouch=True, hat=True, head_down=16, look=0.2, mouth="flat",
         arms=[(-10, -36), (10, -36)], key="g8c")
    breathe = 1 + 0.03 * math.sin(u * 1.2)
    with keep():
        for k, (dx, dy, r_) in enumerate(((-300, 20, 190), (-110, -60, 240), (120, -50, 250), (320, 30, 190),
                                          (0, 60, 230), (-200, 90, 160), (220, 100, 170))):
            shape(c, ell(540 + dx * breathe, 560 + dy * breathe, r_ * breathe, r_ * 0.8 * breathe, 26),
                  hexc("3a3e52"), f"bigc{k}", lw=2.4, amp=0.8)
    rain(c, u, n=70, a=0.6, col=hexc("aab8d0"), seed=8, x0=240, x1=700, y0=700, y1=1260)


# ================================================================ 缓冲：乌云慢慢散开，天亮了，她抬起头，站起来
def x08b(c, t):
    k = ease_io(prog(t, 0.0, 3.4))
    city_night(c, t, lamps=[0, 0, 0], sky=k)
    with keep():
        glow(c, 900, 1000, 500, hexc("ffd8a0"), 0.4 * k)
    suitcase(c, 700, 1160, 0.9, "su8")
    if t < 2.6:
        girl(c, 540, 1200, 1.45, sit=True, crouch=True, hat=True, head_down=lerp(16, 0, ease_io(prog(t, 0.8, 1.6))),
             look_up=0.6 * ease_io(prog(t, 1.2, 1.2)), look=0.4, mouth="flat", arms=[(-10, -36), (10, -36)], key="g8c")
    else:
        girl(c, 540, 1250, 1.45, hat=True, look=0.6, mouth="smile", key="g8c")
    s = lerp(1.0, 0.25, k)                                         # 乌云缩小、变淡、飘走
    with keep():
        for j, (dx, dy, r_) in enumerate(((-300, 20, 190), (-110, -60, 240), (120, -50, 250), (320, 30, 190),
                                          (0, 60, 230))):
            shape(c, ell(540 + dx * s + k * 300, 560 - k * 200 + dy * s, r_ * s, r_ * 0.8 * s, 26),
                  mix(hexc("3a3e52"), hexc("d8d4dc"), k), f"bigc{j}", lw=2.4, amp=0.8, alpha=1 - 0.7 * k)
    if t < 1.2:
        rain(c, t, n=40, a=0.5 * (1 - t / 1.2), col=hexc("aab8d0"), seed=8, x0=240, x1=700, y0=700, y1=1260)


# ================================================================ 9 一路走：小乌云跟着她，摔跤、水坑、跳过一道沟；倒霉事照来，她撑开伞
def _speed(t):
    if t < 4.0:
        return 180.0
    if t < 5.4:
        return 0.0
    if t < 9.8:
        return 220.0
    if t < 10.4:
        return 0.0
    if t < 11.0:
        return 420.0
    return 260.0


_DIST = []


def _dist(t):
    if not _DIST:
        d = 0.0
        for i in range(0, 1801):
            _DIST.append(d)
            d += _speed(i * 0.01) * 0.01
    return _DIST[max(0, min(1800, int(t * 100)))]


HERX = 480


def _obstacles():
    return dict(stone=_dist(4.0) + HERX + 34, puddle=_dist(7.2) + HERX, ditch=_dist(10.4) + HERX + 30,
                ditch_w=_dist(11.0) - _dist(10.4) - 70, puddle2=_dist(13.2) + HERX)


def road_day(c, t, d, warm):
    vgrad(c, -200, 1240, [(0, mix(hexc("b8c4d4"), hexc("9fc8ea"), warm)), (1, mix(hexc("e8e4dc"), hexc("fbf0d8"), warm))],
          -300, W + 300)
    with keep():
        if warm > 0:
            glow(c, 860, 360, 360, hexc("fff0b0"), 0.5 * warm)
            circle(c, 860, 360, 70 * warm, hexc("fff0b0"))
    shape(c, hill_pts(1000, 40, 0.004, 1.3 + d * 0.0, -400, W + 400, 1900), mix(hexc("b8c0a8"), hexc("a8c890"), warm),
          "rhill", lw=2.4)
    r = random.Random(9)
    for k in range(10):                                            # 路边的树，往后退
        tx = (k * 380 + r.uniform(0, 200) - d * 0.6) % (W + 800) - 300
        tree(c, tx, 1240, 1.3, f"rt{k}", col=mix(hexc("8aa080"), hexc("74a160"), warm))
    ob = _obstacles()
    dl, dw = ob["ditch"] - d, ob["ditch_w"]
    ground = [(-40, 1240), (dl, 1240), (dl, 2000), (-40, 2000)]
    ground2 = [(dl + dw, 1240), (W + 40, 1240), (W + 40, 2000), (dl + dw, 2000)]
    shape(c, ground, mix(hexc("b8a888"), hexc("d8c098"), warm), "rg1", lw=3)
    if dl + dw < W + 40:
        shape(c, ground2, mix(hexc("b8a888"), hexc("d8c098"), warm), "rg2", lw=3)
        if dl > -dw - 40:                                          # 沟里的水
            shape(c, rect(dl, 1300, dw, 700), hexc("6aa0c8"), "ditchw", lw=2)
            with keep():
                for j in range(3):
                    yy = 1340 + j * 60
                    line(c, [(dl + 20, yy), (dl + dw - 20, yy + 4)], f"dw{j}", 2, (1, 1, 1), alpha=0.6)
    for key, wx in (("pd1", ob["puddle"]), ("pd2", ob["puddle2"])):  # 水坑
        sx = wx - d
        if -200 < sx < W + 200:
            shape(c, ell(sx, 1262, 90, 18, 20), hexc("8ab0d0"), key, lw=2)
    sx = ob["stone"] - d                                           # 绊脚的石头
    if -200 < sx < W + 200:
        rock_ = [(sx - 30, 1244), (sx - 18, 1214), (sx + 14, 1208), (sx + 32, 1244)]
        shape(c, rock_, hexc("8a8478"), "trip", lw=2.4)


def splash(c, x, y, ph, key):
    if 0 <= ph < 1:
        with keep():
            for j in range(8):
                a = math.pi * (0.15 + 0.7 * j / 7)
                d = ph * 90
                circle(c, x + math.cos(a) * d, y - math.sin(a) * d * 1.3 + ph * ph * 60, 7 * (1 - ph) + 2,
                       hexc("bcd6ea"), a=1 - ph)


def x09(c, t):
    d = _dist(t)
    warm = ease_io(prog(t, 10.8, 1.6))
    road_day(c, t, d, warm)
    s = 1.45
    walking = _speed(t) > 0
    y = 1240
    jump = prog(t, 10.4, 0.6)
    if 0 < jump < 1:
        y -= math.sin(jump * math.pi) * 150
    fallen = 4.15 < t < 5.0
    # 头顶那朵跟着她的小乌云：越来越小，跳过沟以后“噗”地散掉
    cs = lerp(1.9, 1.1, prog(t, 0.0, 10.0))
    pop = prog(t, 11.0, 0.5)
    if pop < 1:
        with keep():
            if pop <= 0:
                rain_cloud(c, HERX, 700 + 20 * math.sin(t * 2), cs, "mycl", col=hexc("6a6e80"), t=t)
            else:
                for j in range(6):
                    a = j / 6 * 2 * math.pi
                    circle(c, HERX + math.cos(a) * 140 * pop, 700 + math.sin(a) * 90 * pop, 30 * (1 - pop),
                           hexc("8a8e9a"), a=1 - pop)
    # 准时飘来的一小朵雨云，她撑开伞
    late = prog(t, 15.0, 1.0)
    if late > 0:
        with keep():
            rain_cloud(c, lerp(W + 200, HERX, ease_io(late)), 640, 1.0, "lcl", col=hexc("9a9eaa"), t=t)
    if fallen:                                                     # 被石头绊倒，坐在地上
        girl(c, HERX + 30, 1250, s, sit=True, crouch=True, hat=True, look=0.6, head_down=10, mouth="flat", key="g9")
        suitcase(c, HERX - 90, 1242, 0.6 * s, "su9", tilt=-0.6)
    elif t > 15.6:                                                 # 一手拉箱子，一手撑伞
        op = ease_out(prog(t, 15.6, 0.6))
        girl(c, HERX, y, s, hat=True, look=0.9, mouth="laugh", walk=d / 40, arms=[(-26, -76), (16, -150)], key="g9")
        suitcase(c, HERX - 58 * s, y + 2 * s, 0.6 * s, "su9", tilt=0.15)
        umbrella(c, HERX + 16 * s, y - 150 * s - 112 * 0.9 * op, 0.9 * s, "umb", open_=op)
    else:
        mood = "laugh" if t > 12.0 else ("smile" if t > 11.0 else "flat")
        tilt = -0.15 if 7.1 < t < 7.6 else 0.0
        if 9.8 < t < 10.4:
            look = -0.2
        else:
            look = 0.9
        pull(c, HERX, y, s, "g9", walk=d / 40 if walking else None, d=1, look=look, mouth=mood, tilt=tilt,
             head_down=lerp(10, 0, prog(t, 9.0, 3.0)))
    splash(c, HERX + 20, 1252, prog(t, 7.15, 0.6), "sp1")
    splash(c, HERX + 20, 1252, prog(t, 13.15, 0.6), "sp2")
    if 0 < prog(t, 4.0, 0.3) < 1:                                  # 摔倒时扬起的一点灰
        with keep():
            for j in range(5):
                ph = prog(t, 4.0, 0.3)
                circle(c, HERX - 20 + j * 24, 1240 - ph * 30, 10 * (1 - ph) + 3, hexc("c8b898"), a=1 - ph)


# ================================================================ 10 前面是一整排更高、更远的山：又回到了新手村
def x10(c, t):
    vgrad(c, -200, 1240, [(0, hexc("9fc8ea")), (1, hexc("fbf0d8"))], -300, W + 300)
    look = ease_io(prog(t, 0.0, 1.0))
    with cam(c, 540, 960, lerp(1.25, 1.0, look)):
        for k, (mx, mh, mw) in enumerate(((-60, 760, 640), (380, 980, 760), (820, 860, 700), (1180, 700, 600))):
            mountain(c, mx, 1240, mw, mh, mix(hexc("b9c6d6"), hexc("d6dee8"), 0.3 * (k % 2)), f"nm{k}")
        shape(c, rect(-200, 1230, W + 400, 800), hexc("d8c098"), "nmg", lw=3)
        go = ease_in(prog(t, 2.8, 1.2))
        x = 300 + go * 160
        girl(c, x, 1250, 1.3, hat=True, look=0.5, look_up=0.8 * (1 - go), mouth="laugh" if t > 1.6 else "o",
             walk=t * 6 if go > 0 else None, arms=[(-26, -76), (-40, -70)], key="g10")
        suitcase(c, x - 58 * 1.3, 1252, 0.6 * 1.3, "su10", tilt=0.15 if go > 0 else 0.0)

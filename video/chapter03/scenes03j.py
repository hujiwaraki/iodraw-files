"""第三章 · 从游客到旅人（第五稿：旅行手账）—— 每一段都从手账的一页开始，画面“活”过来。"""
import math
import random

from scenes03 import (GRAN, SKIN_L, COUPLE_COLS, RED, c10_eyes, checklist, cobbles, d05_tourist, d06_checkin,
                      d10_town, d11_costume, d12_market, d14_shoot, d15_alley, d17_table, gaze, landmark, local,
                      old_town, p_night, phone_at, pull, s_book, s_pack, street_lamp, tinbox, travel_ticket)
from scenes02 import p_noodle_eyes
from draw import *  # noqa: F401,F403
from engine import book_intro, book_outro
import cairo

PAPER = hexc("fbf6e8")
LINE = hexc("c9d6e3")
PENCIL = hexc("6a6560")
CLOTH = hexc("b9a58c")
PX, PY, PW, PH = 70, 90, 940, 1250            # 手账页面


# ================================================================ 手账的基础画法
def page_bg(c, t, key="pg", lines=True, paper=PAPER, curl=0.0):
    fill_all(c, CLOTH)
    for i in range(12):                                            # 桌布的格纹
        line(c, [(i * 100, 0), (i * 100, 1920)], f"cl{i}", 1.4, darker(CLOTH, 0.9), alpha=0.4)
        line(c, [(0, i * 160), (1080, i * 160)], f"ch{i}", 1.4, darker(CLOTH, 0.9), alpha=0.4)
    with keep():
        c.rectangle(PX + 14, PY + 18, PW, PH)
        c.set_source_rgba(0, 0, 0, 0.18)
        c.fill()
        shape(c, rect(PX, PY, PW, PH), paper, key, lw=2.4, amp=0.5)
        if lines:
            for k in range(1, int(PH / 52)):
                line(c, [(PX + 20, PY + k * 52), (PX + PW - 20, PY + k * 52)], f"{key}l{k}", 1.2, LINE, alpha=0.7, amp=0.3)
            line(c, [(PX + 110, PY + 10), (PX + 110, PY + PH - 10)], key + "mg", 1.4, hexc("e8a0a0"), alpha=0.7)
        for k in range(11):                                        # 线圈
            y = PY + 60 + k * 112
            shape(c, ell(PX - 6, y, 16, 10, 12), None, f"{key}r{k}", lw=3, amp=0.3)


def tape(c, x, y, w, h, rot, key, col=hexc("f2d98a")):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    with keep():
        shape(c, rect(-w / 2, -h / 2, w, h), col + (0.75,), key, lw=1, amp=0.2, edge=False)
    c.restore()


def hand(c, s, x, y, size, col=PENCIL, rot=0.0, a=1.0, anchor="c"):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    with keep():
        text(c, s, 0, 0, size, col, a=a, anchor=anchor)
    c.restore()


def scribble_reveal(c, s, x, y, size, u, col=PENCIL, rot=0.0):
    """一个字一个字写出来。"""
    n = int(len(s) * clamp(u))
    if n > 0:
        hand(c, s[:n], x, y, size, col, rot, anchor="l")


FRAME_W = 600
FRAME_SF = FRAME_W / W
FRAME_H = H * FRAME_SF


def sketch(c, fn, t, fx, fy, sat=0.0, pencil=1.0, sf=FRAME_SF):
    """把一个场景缩小画进手账里的一个小框：铅笔素描（灰）→ 彩色。"""
    fw, fh = W * sf, H * sf
    c.save()
    c.rectangle(fx, fy, fw, min(fh, 1340 * sf))
    c.clip()
    c.translate(fx, fy)
    c.scale(sf, sf)
    with grade(sat=sat):
        fn(c, t)
    c.restore()
    if pencil > 0:
        with keep():
            c.rectangle(fx, fy, fw, min(fh, 1340 * sf))
            c.set_source_rgba(0.98, 0.96, 0.9, 0.45 * pencil)
            c.fill()
    with keep():
        shape(c, rect(fx, fy, fw, min(fh, 1340 * sf)), None, f"sk{int(fx)}{int(fy)}", lw=2, amp=0.6)


def come_alive(c, t, page_fn, fn, fx, fy, t0, d=1.0, sat_to=None, sf=FRAME_SF):
    """手账页 → 镜头推进小框 → 画面活过来，变成真实场景。"""
    if sat_to is None:
        sat_to = GRADE["sat"]
    if t < t0:
        page_fn(c, t)
        sketch(c, fn, t, fx, fy, sat=0.0, pencil=1.0, sf=sf)
        return
    e = ease_io(prog(t, t0, d))
    if e >= 1:
        fn(c, t)
        return
    z = lerp(1.0, 1.0 / sf, e)
    ox, oy = lerp(0, fx, e), lerp(0, fy, e)
    c.save()
    c.scale(z, z)
    c.translate(-ox, -oy)
    page_fn(c, t)
    sketch(c, fn, t, fx, fy, sat=sat_to * e, pencil=1 - e, sf=sf)
    c.restore()


def back_to_page(c, t, page_fn, fn, fx, fy, t0, d=0.7, sf=FRAME_SF):
    """真实场景 → 镜头拉远，落回手账上的小框。"""
    e = 1 - ease_io(prog(t, t0, d))
    if t < t0:
        fn(c, t)
        return
    z = lerp(1.0, 1.0 / sf, e)
    ox, oy = lerp(0, fx, e), lerp(0, fy, e)
    c.save()
    c.scale(z, z)
    c.translate(-ox, -oy)
    page_fn(c, t)
    sketch(c, fn, t, fx, fy, sat=GRADE["sat"] * e, pencil=1 - e, sf=sf)
    c.restore()


# ================================================================ 片头
def journal_illus(c, cx, cy):
    """章节页小插画：一本贴着票根的旅行手账。"""
    with keep():
        shape(c, rrect(cx - 70, cy - 40, 140, 110, 8), hexc("8c5a3c"), "ji_c", lw=2.4)
        shape(c, rect(cx - 60, cy - 30, 120, 90), PAPER, "ji_p", lw=1.6)
        for k in range(3):
            line(c, [(cx - 50, cy - 10 + k * 22), (cx + 50, cy - 10 + k * 22)], f"ji_l{k}", 1.2, LINE)
        c.save()
        c.translate(cx + 20, cy - 34)
        c.rotate(0.2)
        shape(c, rect(-34, -12, 68, 24), hexc("cfe4f2"), "ji_t", lw=1.4)
        c.restore()
        line(c, [(cx - 80, cy + 20), (cx + 80, cy + 20)], "ji_band", 3, RED)


def intro(c, t):
    book_intro(c, t, "第三章", "从游客到旅人", journal_illus)


# ================================================================ 一、手账的第一页
def s_station(c, t):
    """车站出口：她拉着行李箱走出来。"""
    fill_all(c, hexc("d7d4cb"))
    for i in range(14):
        line(c, [(i * 80, 0), (i * 80, 900)], f"st{i}", 1.4, hexc("c5c1b7"), alpha=0.6)
    with keep():
        shape(c, rect(300, 180, 480, 100), hexc("2f6a4a"), "exit", lw=2.4)
        text(c, "出 站 口  →", 540, 248, 52, (1, 1, 1))
    for i in range(5):                                             # 闸机
        x = 160 + i * 190
        shape(c, rect(x, 900, 40, 190), hexc("9aa0a8"), f"gate{i}", lw=2.4)
        shape(c, rect(x + 40, 960, 110, 14), hexc("c9473b"), f"gbar{i}", lw=1.6, alpha=0.7)
    glow(c, 980, 700, 400, hexc("fff3d0"), 0.6)
    shape(c, rect(-20, 1090, W + 40, 800), hexc("b7b2a7"), "sfl", lw=3)
    r = random.Random(3)
    for i in range(5):
        x = (r.uniform(0, 1100) + t * 120) % 1200 - 60
        silhouette(c, x, 1150 + r.uniform(0, 40), 1.2, f"sp{i}", walk=t * 7 + i, a=0.6)
    x = lerp(260, 640, ease_io(prog(t, 0.8, 5.0)))
    pull(c, x, 1220, 1.6, "g1", walk=t * 7, mouth="flat")


def page1(c, t):
    page_bg(c, t, "p1")
    travel_ticket(c, 300, 260, 0.75, "train", "p1tk", age=0.0, rot=-0.08, seed=5)
    tape(c, 190, 200, 90, 30, -0.5, "p1ta")
    tape(c, 420, 320, 90, 30, 0.5, "p1tb")
    scribble_reveal(c, "第一次，一个人", 560, 260, 46, prog(t, 0.2, 1.4), rot=-0.03)
    hand(c, "（有点怕）", 640, 320, 30, a=clamp((t - 1.4) * 2))


def j01(c, t):
    come_alive(c, t, page1, s_station, 380, 380, 2.4, 1.2)


# ================================================================ 二、并不浪漫
def s_stairs(c, t):
    """石子路尽头的长台阶：她抱着行李箱一级一级往上拖，停下来擦汗。"""
    vgrad(c, 0, 900, [(0, hexc("c9d1d8")), (1, hexc("e4e5e1"))])
    old_town(c, t, 760, "sto", hs=0.9)
    cobbles(c, 1360, 1500, "stc")
    run_, rise, n = 100, 62, 10
    x0, y0 = 120, 1380                                             # 第一级台阶的左下角
    pts = [(-40, y0), (x0, y0)]
    for k in range(n):
        pts += [(x0 + k * run_, y0 - (k + 1) * rise), (x0 + (k + 1) * run_, y0 - (k + 1) * rise)]
    pts += [(W + 40, y0 - n * rise), (W + 40, 1900), (-40, 1900)]
    shape(c, pts, hexc("bdb4a4"), "stair", lw=3)
    for k in range(n):                                             # 每一级的边
        line(c, [(x0 + k * run_, y0 - (k + 1) * rise), (x0 + (k + 1) * run_, y0 - (k + 1) * rise)], f"stl{k}", 4,
             hexc("8f877a"))
    line(c, [(x0 - 20, y0 - 150), (x0 + n * run_, y0 - n * rise - 150)], "rail", 4, hexc("6a6560"))
    for k in range(0, n + 1, 3):
        line(c, [(x0 + k * run_, y0 - k * rise), (x0 + k * run_, y0 - k * rise - 150)], f"railp{k}", 3, hexc("6a6560"))
    rest = 2.3 < t < 3.4
    climb = ease_io(prog(t, 0.0, 2.3)) * 3 + ease_io(prog(t, 3.4, 1.0)) * 1.5
    x = x0 + 50 + climb * run_
    y = y0 - (math.ceil(climb - 0.01) if climb > 0 else 0) * rise - (0 if climb > 0 else 0)
    y = y0 - max(1, math.ceil(climb + 0.5)) * rise
    girl(c, x, y, 1.5, hat=True, mouth="sad", look=-0.8, head_down=0 if rest else 6,
         arms=[(-24, -78), (-40, -150)] if rest else [(-30, -90), (-50, -80)], key="g2s")
    with keep():
        suitcase(c, x - 90, y + rise * 0.6 + (0 if rest else 6 * abs(math.sin(t * 7))), 0.8, "su2s", handle=0.0,
                 tilt=0.0 if rest else -0.25)
        if rest:
            for j in range(3):
                ph = (t * 2 + j / 3) % 1
                shape(c, ell(x + 40 + j * 14, y - 250 + ph * 40, 5, 8, 8), hexc("9fc5e8"), f"sw{j}", lw=1, alpha=1 - ph)


def s_night(c, t):
    p_night(c, t, W, 1340)


SF2 = 0.4


def page2(c, t):
    page_bg(c, t, "p2")
    with keep():                                                   # 被汗打湿的页角
        shape(c, ell(150, 1250, 140, 100, 20), hexc("e8e0c8"), "wet", lw=0, edge=False, alpha=0.7)
    hand(c, "台阶好多……", 600, 260, 40, rot=-0.04)
    hand(c, "晚上不敢出门", 330, 1180, 36, rot=0.05, a=clamp((t - 4.6) * 2))
    if t > 4.3:                                                    # 台阶那一格已经画好了
        sketch(c, s_stairs, 4.3, 120, 330, sat=0.0, pencil=1.0, sf=SF2)


def j02(c, t):
    if t < 4.3:
        come_alive(c, t, page2, s_stairs, 120, 330, 0.6, 0.9, sf=SF2)
    elif t < 5.0:
        back_to_page(c, t, page2, s_stairs, 120, 330, 4.3, 0.7, sf=SF2)
    else:
        come_alive(c, t, page2, lambda cc, tt: s_night(cc, tt - 5.0), 540, 560, 5.6, 0.9, sf=SF2)


def p_breakwater(c, t, w, h):
    vgrad(c, 0, h, [(0, hexc("9fc5e8")), (1, hexc("e9f2f6"))], 0, w)
    shape(c, rect(-10, h * 0.45, w + 20, h), hexc("4f8fb8"), "sea", lw=2)
    for k in range(4):
        y = h * 0.5 + k * 30
        line(c, [(-10, y), (w * 0.3, y + 6), (w * 0.6, y), (w + 10, y + 6)], f"wv{k}", 2, (1, 1, 1), alpha=0.5)
    for i in range(7):                                             # 防波堤
        x = 60 + i * 130
        shape(c, [(x, h * 0.75), (x + 120, h * 0.75), (x + 100, h * 0.62), (x + 20, h * 0.62)], hexc("b7b2a7"),
              f"bw{i}", lw=2)
    sp = max(0.0, math.sin(t * 2.0))
    with keep():
        for k in range(5):
            shape(c, ell(700 + k * 30, h * 0.6 - sp * 60 - k * 6, 14, 10, 10), (1, 1, 1), f"spl{k}", lw=1, alpha=sp * 0.8)
    girl(c, 480, h * 0.62, 1.0, view="back", sit=True, hat=True, key="gbw")


def p_subway(c, t, w, h):
    fill_all(c, hexc("e4e5e1"))
    with keep():
        shape(c, rect(80, 30, w - 160, h - 80), (1, 1, 1), "map", lw=2.4)
        cols = ["c9473b", "3f6fb5", "4f9a5c", "e8c040", "8d6a9f"]
        r = random.Random(4)
        for i, col in enumerate(cols):
            pts = []
            y = 60 + i * 40
            x = 100
            while x < w - 120:
                pts.append((x, y))
                x += r.uniform(60, 140)
                y = clamp(y + r.uniform(-50, 50), 50, h - 70)
            line(c, pts, f"ml{i}", 6, hexc(col))
            for j, p in enumerate(pts):
                circle(c, p[0], p[1], 7, (1, 1, 1))
                line(c, [(p[0] + 10, p[1] - 10), (p[0] + 20, p[1] - 4), (p[0] + 14, p[1] - 16)], f"mg{i}{j}", 1.4,
                     hexc("6a6f7d"))
    lk = math.sin(t * 4)
    girl(c, w / 2, h - 30, 0.8, hat=True, look=lk, mouth="o", key="gsw")


def page3(c, t):
    page_bg(c, t, "p3")
    hand(c, "一个人", 160, 210, 44, rot=-0.03, anchor="l")


THREE = [(p_noodle_eyes, "吃饭"), (p_breakwater, "看风景"), (p_subway, "陌生的城市")]


def j03(c, t):
    page3(c, t)
    active = min(int(t / 3.3), 2)
    for i, (fn, lab) in enumerate(THREE):
        fx, fy, fw, fh = 130, 270 + i * 340, 820, 290
        on = i == active and t >= i * 3.3
        shown = t >= i * 3.3 - 0.2
        if not shown:
            continue
        k = 1.06 if on else 1.0
        c.save()
        c.translate(fx + fw / 2, fy + fh / 2)
        c.scale(k, k)
        c.translate(-(fx + fw / 2), -(fy + fh / 2))
        c.save()
        c.rectangle(fx, fy, fw, fh)
        c.clip()
        c.translate(fx, fy)
        c.scale(fw / 960, fh / 330)
        with grade(sat=1.0 if on else 0.0):
            fn(c, t - i * 3.3 if on else 1.0, 960, 330)
        c.restore()
        if not on:
            with keep():
                c.rectangle(fx, fy, fw, fh)
                c.set_source_rgba(0.98, 0.96, 0.9, 0.45)
                c.fill()
        with keep():
            shape(c, rect(fx, fy, fw, fh), None, f"f3{i}", lw=2.4, amp=0.6)
        tape(c, fx + 40, fy, 80, 26, -0.3, f"t3{i}")
        c.restore()


def page4(c, t):
    page_bg(c, t, "p4")
    r = random.Random(9)
    n = int(clamp(t / 0.08, 0, 40))
    for i in range(n):                                             # 页边画满的小眼睛
        x = r.choice((r.uniform(PX + 20, PX + 100), r.uniform(PX + PW - 120, PX + PW - 30)))
        y = r.uniform(PY + 40, PY + PH - 40)
        with keep():
            shape(c, [(x - 14, y), (x, y - 8), (x + 14, y), (x, y + 8)], None, f"pe{i}", lw=1.6, amp=0.3)
            circle(c, x, y, 3.5, PENCIL)


def j04(c, t):
    if t < 1.2:
        page4(c, t)
    else:
        f = ease_io(prog(t, 1.2, 0.6))
        c10_eyes(c, t - 1.2 + 0.2)
        if f < 1:
            with group_alpha(c, 1 - f):
                page4(c, t)


# ================================================================ 三、路过的游客
def page5(c, t):
    page_bg(c, t, "p5", lines=False, paper=hexc("f6f6f2"))
    with keep():                                                   # 打印出来的行程表
        text(c, "行 程 表", 540, 200, 48, INK)
        for i in range(9):
            y = 250 + i * 110
            line(c, [(120, y), (960, y)], f"tr{i}", 1.6, hexc("9aa0a8"), amp=0.1)
            if i < 8:
                text(c, f"{8 + i}:00", 150, y + 66, 28, hexc("6a6f7d"), anchor="l")
                text(c, ["景区A", "景区B", "网红桥", "古城门", "午饭（必吃）", "观景塔", "日落机位", "纪念品店"][i], 330,
                     y + 66, 30, INK, anchor="l")
        line(c, [(290, 250), (290, 1130)], "trv", 1.6, hexc("9aa0a8"), amp=0.1)


def j05(c, t):
    come_alive(c, t, page5, d05_tourist, 420, 260, 1.6, 1.0, sf=0.45)


def page6(c, t, n):
    page_bg(c, t, "p6", lines=False)
    hand(c, "打卡！", 560, 200, 44, rot=-0.05)
    for i in range(n):
        x = 220 + (i % 3) * 300
        y = 380 + (i // 3) * 360
        with keep():
            shape(c, rect(x - 110, y - 130, 220, 260), (1, 1, 1), f"ph{i}", lw=2, amp=0.3)
            vgrad(c, y - 115, y + 70, [(0, hexc(["9fc5e8", "f2c79a", "b9c3e8"][i % 3])), (1, (0.97, 0.96, 0.93))],
                  x - 96, x + 96)
            landmark(c, x, y + 60, 0.22, ["bridge", "gate", "tower"][i % 3], f"phl{i}")
            girl(c, x, y + 80, 0.55, look=0.2, mouth="laugh", arms=[(-24, -80), (44, -168)], key=f"phg{i}")
            line(c, [(x + 70, y + 110), (x + 82, y + 124), (x + 104, y + 92)], f"phc{i}", 4, RED)
        tape(c, x, y - 130, 70, 22, 0.1 * (i % 2 * 2 - 1), f"pht{i}")


def j06(c, t):
    k = min(int(t / 2.3), 2)
    lt = t - k * 2.3
    if lt < 1.3:
        d06_checkin(c, k * 2.3 + lt)
    else:
        u = ease_back(prog(lt, 1.3, 0.3))
        page6(c, t, k * 2 + 1)
        if u < 1:
            veil(c, (1, 1, 1), 0.3 * (1 - u))


def j07(c, t):
    page_bg(c, t, "p7", lines=False)
    for i in range(12):                                            # 贴满几乎一样的照片
        x = 200 + (i % 4) * 230
        y = 260 + (i // 4) * 300
        with keep():
            shape(c, rect(x - 90, y - 110, 180, 210), (1, 1, 1), f"q{i}", lw=1.6, amp=0.2)
            vgrad(c, y - 98, y + 50, [(0, hexc(["9fc5e8", "f2c79a", "b9c3e8", "a9c48b"][i % 4])), (1, (0.97, 0.96, 0.93))],
                  x - 78, x + 78)
            girl(c, x, y + 66, 0.45, look=0.2, mouth="laugh", arms=[(-24, -80), (44, -168)], key=f"qg{i}")
    with keep():                                                   # 写不出字的空白
        shape(c, rect(170, 1150, 740, 150), PAPER, "blank", lw=1.6, amp=0.3)
        px_ = 300 + math.sin(t * 1.3) * 30
        py_ = 1220
        shape(c, [(px_, py_), (px_ + 14, py_ - 10), (px_ + 120, py_ - 140), (px_ + 106, py_ - 150), (px_ - 4, py_ - 20)],
              hexc("e8c040"), "pen", lw=2)
        circle(c, px_ + 2, py_ - 2, 3, INK)
        if t > 2.0:
            for j in range(3):
                circle(c, px_ + 30 + j * 18, py_ + 10, 3, PENCIL, a=0.6 * (0.5 + 0.5 * math.sin(t * 3 + j)))


# ================================================================ 四、变得自信
TERRAINS = [("f2d29a", "e8b46a"), ("9fd0ec", "6fa8c8"), ("eef2f8", "c9d6e3"), ("a9c48b", "6fa860"),
            ("f2c79a", "c98d72"), ("cfe0a8", "8fae7a")]


def flip_page(c, t, i, stride):
    page_bg(c, t, f"fl{i % 2}", lines=False)
    sky, ground = TERRAINS[i % len(TERRAINS)]
    with keep():
        shape(c, rect(150, 300, 780, 700), hexc(sky), f"fls{i}", lw=1.6, amp=0.3)
        shape(c, hill_pts(820, 40, 0.01, i, 150, 930, 1000), hexc(ground), f"flg{i}", lw=1.6)
    girl(c, 540, 900, 1.1 + 0.08 * stride, hat=True, walk=i * 1.3, look=0.8, head_down=max(0, 6 - stride * 2),
         mouth="smile" if stride > 2 else "flat", key=f"flgirl{i % 2}")


def s_road(c, t):
    vgrad(c, 0, 900, [(0, hexc("9fd0ec")), (1, hexc("f4efe4"))])
    shape(c, hill_pts(860, 40, 0.006, 1.0), hexc("a9c48b"), "rdh", lw=3)
    shape(c, [(470, 870), (610, 870), (1100, 1800), (-20, 1800)], hexc("d9c39a"), "rd", lw=3)
    for k in range(4):
        cloud(c, (k * 300 + t * 20) % 1300 - 120, 300 + k * 50, 1.2, f"rdc{k}")
    push = ease_io(prog(t, 0.6, 0.8))
    girl(c, 540, 1240, 1.8, hat=True, look=0.0, mouth="laugh", head_down=lerp(6, 0, push),
         look_up=lerp(-0.6, 0.4, push), arms=[(-24, -78), (lerp(24, 18, push), lerp(-78, -190, push * (1 - prog(t, 1.8, 0.4))))],
         key="g8r")


def j08(c, t):
    if t < 4.6:
        i = int(t * (3 + t * 1.2))                                  # 越翻越快
        flip_page(c, t, i, min(5, t * 1.4))
        ph = (t * (3 + t * 1.2)) % 1                               # 翻页的纸边
        with keep():
            xx = PX + PW * (1 - ph)
            shape(c, [(xx, PY), (xx + 40, PY + 20), (xx + 30, PY + PH - 20), (xx, PY + PH)], PAPER, "flp", lw=1.6)
    else:
        come_alive(c, t, lambda cc, tt: flip_page(cc, tt, 30, 5), lambda cc, tt: s_road(cc, tt - 4.6), 240, 200, 4.6, 0.8)


def j09(c, t):
    if t < 5.6:
        d17_table(c, t)
    else:
        lt = t - 5.6
        page4(c, 4.0)
        with keep():                                                # 橡皮擦掉眼睛
            ex = PX + 60 + math.sin(lt * 9) * 30
            ey = PY + 120 + lt * 420
            c.rectangle(PX + 10, PY + 20, 120, ey - PY - 20)
            c.set_source_rgba(*PAPER, 1.0)
            c.fill()
            c.rectangle(PX + PW - 140, PY + 20, 130, ey - PY - 20)
            c.fill()
            shape(c, rrect(ex - 40, ey - 24, 80, 48, 8), hexc("f2a6a0"), "eraser", lw=2)
            shape(c, rrect(PX + PW - 120 - math.sin(lt * 9) * 30, ey - 24, 80, 48, 8), hexc("f2a6a0"), "eraser2", lw=2)


# ================================================================ 五、以前 / 后来（翻页）
def before_days(c, t):
    for i in range(3):
        x = 180 + i * 250
        with keep():
            shape(c, rect(x, 340, 210, 260), (1, 1, 1), f"bd{i}", lw=1.6, amp=0.2)
            text(c, f"第 {i + 1} 天", x + 105, 390, 32, INK)
    with keep():
        shape(c, rrect(720, 480, 120, 60, 10), hexc("9aa0a8"), "bdbus", lw=1.6)
        text(c, "返程", 780, 520, 26, (1, 1, 1))
    girl(c, 300, 900, 1.4, hat=True, look=0.0, mouth="flat", arms=[(-24, -78), (20, -110)], key="gbd")
    with keep():
        shape(c, ell(300 + 20 * 1.4, 900 - 114 * 1.4, 14, 14, 12), (1, 1, 1), "watch", lw=1.6)


def after_days(c, t):
    unfold = ease_out(prog(t, 0.2, 2.2))
    n = int(15 * unfold)
    cols = ["f2a6a0", "9fc5e8", "f7e27a", "a8e07a", "c9a0dc", "f2c79a"]
    for i in range(n):
        x = 160 + (i % 5) * 156
        y = 240 + (i // 5) * 200
        with keep():
            c.save()
            c.translate(x + 70, y + 90)
            c.rotate(0.05 * math.sin(i * 2.3))
            shape(c, rect(-70, -90, 140, 180), (1, 1, 1), f"ad{i}", lw=1.6, amp=0.3)
            shape(c, rect(-60, -80, 120, 110), hexc(cols[i % 6]), f"adp{i}", lw=1, amp=0.3)
            text(c, f"第{i + 1}天", 0, 64, 24, INK)
            c.restore()
    girl(c, 540, 1060, 1.4, hat=True, look=0.3, mouth="laugh", key="gad")


def before_plan(c, t):
    for i in range(4):
        with keep():
            shape(c, rect(170 + i * 18, 280 + i * 14, 560, 700), (1, 1, 1), f"bp{i}", lw=1.6, amp=0.2)
    for j in range(14):
        line(c, [(220, 340 + j * 44), (660 - (j * 37) % 200, 340 + j * 44)], f"bpl{j}", 2, hexc("9aa0a8"), amp=0.1)
    for j, col in enumerate(("f7e27a", "f2a6a0", "a8e07a")):
        with keep():
            shape(c, rect(700, 320 + j * 120, 120, 100), hexc(col), f"bps{j}", lw=1.4, amp=0.3)
    line(c, [(170, 1010), (760, 1010)], "ruler", 10, hexc("e8c040"))


def after_plan(c, t):
    travel_ticket(c, 540, 330, 0.9, "boarding", "apbp", rot=-0.18, seed=12)
    tape(c, 440, 250, 90, 28, -0.6, "apt")
    scribble_reveal(c, "早上 8 点订，下午 2 点飞！", 170, 560, 44, prog(t, 0.2, 1.6), col=hexc("2f4a6a"), rot=-0.05)


def before_pack(c, t):
    hand(c, "行李清单", 540, 220, 44)
    items = ["衣服×8", "鞋×3", "吹风机", "卷发棒", "化妆包", "雨伞", "拖鞋", "转换插头", "零食", "药", "相机", "三脚架",
             "充电宝", "帽子×2", "外套", "睡衣", "书", "水杯"]
    for i, it in enumerate(items):
        x = 170 + (i % 2) * 400
        y = 300 + (i // 2) * 88
        hand(c, "□ " + it, x, y, 30, anchor="l")


def after_pack(c, t):
    hand(c, "行李清单", 540, 220, 44)
    for i, it in enumerate(["几件衣服", "证件", "手机", "充电宝", "草帽"]):
        hand(c, "✓ " + it, 200, 310 + i * 64, 32, col=hexc("2f4a6a"), anchor="l")
    with keep():
        shape(c, rrect(660, 300, 200, 240, 40), PACK, "apk", lw=2.4)
        shape(c, rrect(688, 430, 144, 80, 16), darker(PACK, 0.85), "apkp", lw=2)


def before_route(c, t):
    hand(c, "路线", 540, 220, 44)
    pts = [(200, 360), (800, 360), (800, 560), (200, 560), (200, 760), (800, 760), (800, 960)]
    line(c, pts, "brt", 3, INK)
    for i, p in enumerate(pts):
        circle(c, p[0], p[1], 10, INK)
        hand(c, f"{i + 1}", p[0], p[1] - 22, 26)
    line(c, [(160, 1040), (840, 1040)], "ruler2", 10, hexc("e8c040"))


def after_route(c, t):
    hand(c, "随便走走", 540, 220, 48, col=hexc("2f4a6a"), rot=-0.06)
    r = random.Random(5)
    pts = [(180, 420)]
    for i in range(10):
        pts.append((clamp(pts[-1][0] + r.uniform(-60, 150), 160, 920), clamp(pts[-1][1] + r.uniform(-90, 90), 300, 600)))
    with keep():
        line(c, pts, "art", 3, hexc("2f4a6a"))
        for i, p in enumerate(pts[1:]):
            hand(c, "?" if i % 3 == 0 else ("→" if i % 3 == 1 else "♡"), p[0] + 20, p[1] - 10, 30, col=RED)


def s_fork(c, t):
    vgrad(c, 0, 900, [(0, hexc("9fd0ec")), (1, hexc("f4efe4"))])
    shape(c, hill_pts(860, 30, 0.008, 2.0), hexc("a9c48b"), "fkh", lw=3)
    for i, (x1, col) in enumerate(((140, "d9c39a"), (540, "d9c39a"), (940, "d9c39a"))):
        shape(c, [(500, 1300), (580, 1300), (x1 + 40, 880), (x1 - 40, 880)], hexc(col), f"fk{i}", lw=2.4)
    shape(c, rect(-20, 1280, W + 40, 600), hexc("cfc19c"), "fkg", lw=3)
    girl(c, 540, 1300, 1.7, hat=True, pack=True, view="back" if t > 1.4 else "front", mouth="laugh", look=0.2,
         arms=[(-24, -78), (60, -170)] if t > 0.8 else [(-30, -110), (30, -110)], walk=t * 6 if t > 1.4 else None,
         key="gfk")


def s_gate(c, t):
    """早上订的票，下午就站在登机口：她拉着小箱子一路小跑。"""
    vgrad(c, 0, 1000, [(0, hexc("f6e6c8")), (1, hexc("fbf3e2"))])
    shape(c, rect(90, 180, 900, 620), hexc("cfe0ea"), "gwin", lw=3)
    for k in range(1, 4):
        line(c, [(90 + k * 225, 180), (90 + k * 225, 800)], f"gwm{k}", 4, hexc("6f7d8a"))
    shape(c, rect(90, 640, 900, 160), hexc("b9c0c4"), "apron", lw=2)
    plane(c, 300 + t * 60, 600, 3.2, "gpl")
    with keep():
        shape(c, rect(640, 90, 330, 76), hexc("2e3449"), "gsign", lw=2)
        text(c, "14:00 登机", 805, 142, 38, hexc("f6e08a"))
        shape(c, rect(110, 90, 250, 76), hexc("e8c040"), "gate", lw=2)
        text(c, "登机口 →", 235, 142, 36, INK)
    shape(c, rect(-20, 1000, W + 40, 900), hexc("c9c2b4"), "gfl", lw=3)
    for k in range(8):
        line(c, [(-20, 1040 + k * k * 8), (W + 20, 1040 + k * k * 8)], f"gfl{k}", 1.4, hexc("b3ab9c"), alpha=0.6)
    x = lerp(160, 860, ease_io(prog(t, 0.0, 3.6)))
    pull(c, x, 1260, 1.6, "ggate", walk=t * 12, mouth="laugh", run=True)


def s_packing(c, t):
    """十分钟收好一个背包：几件衣服塞进去，背上就走。"""
    vgrad(c, 0, 1000, [(0, hexc("eaf2e2")), (1, hexc("fbf6ec"))])
    shape(c, rect(-20, 1000, W + 40, 900), hexc("d9c4a8"), "pkf", lw=3)
    for k in range(9):
        line(c, [(k * 130 - 20, 1000), (k * 160 - 120, 1900)], f"pkb{k}", 1.4, hexc("c4ae90"), alpha=0.6)
    with keep():
        shape(c, ell(840, 300, 110, 110, 24), (1, 1, 1), "clk", lw=3)
        a = t * 1.6
        line(c, [(840, 300), (840 + math.sin(a) * 80, 300 - math.cos(a) * 80)], "clkh", 4)
        text(c, "10 分钟", 840, 470, 40, INK)
    if t < 2.4:
        with keep():
            shape(c, rrect(250, 1000, 220, 250, 44), PACK, "bpk", lw=3)
            shape(c, rrect(280, 1130, 160, 90, 16), darker(PACK, 0.85), "bpkp", lw=2)
            u = prog(t, 0.1, 1.8)
            for k in range(3):
                uu = ease_io(clamp(u * 3 - k))
                if uu < 1:
                    shape(c, ell(lerp(620, 360, uu), lerp(880, 1020, uu) - math.sin(uu * math.pi) * 160, 50, 24, 12),
                          hexc(["9fc5e8", "f7e27a", "f2a6a0"][k]), f"pc{k}", lw=1.6, amp=0.4)
        girl(c, 680, 1260, 1.6, hat=True, look=-0.7, mouth="smile", arms=[(-50, -100 + 20 * math.sin(t * 10)), (24, -78)],
             key="gpk")
    else:
        x = lerp(560, 1250, ease_in(prog(t, 2.6, 1.8)))
        girl(c, x, 1260, 1.6, hat=True, look=0.9, mouth="laugh", walk=t * 9, run=True, pack=True, key="gpk2")


PAIRS = [(before_days, after_days, None), (before_plan, after_plan, s_gate), (before_pack, after_pack, s_packing),
         (before_route, after_route, s_fork)]


def page_turn(c, t, u, before_fn, after_fn):
    """手账翻页：下面是后来的页，上面一页翻过去。"""
    page_bg(c, t, "pt_a")
    with grade(sat=1.0):
        after_fn(c, 0.0)
    w_ = PW * math.cos(u * math.pi / 2)
    c.save()
    c.rectangle(PX, PY, max(1, w_), PH)
    c.clip()
    with grade(sat=0.3):
        page_bg(c, t, "pt_b", paper=hexc("f2f0ea"))
        before_fn(c, 4.0)
    c.restore()
    with keep():
        c.rectangle(PX + w_ - 30, PY, 30, PH)
        c.set_source_rgba(0, 0, 0, 0.12 * math.sin(u * math.pi))
        c.fill()


def j10(c, t):
    k = min(int(t / 8.0), 3)
    lt = t - k * 8.0
    before_fn, after_fn, live_fn = PAIRS[k]
    if lt < 3.6:
        with grade(sat=0.3):
            page_bg(c, t, "pb", paper=hexc("f2f0ea"))
            before_fn(c, lt)
    elif lt < 4.3:
        page_turn(c, t, ease_io(prog(lt, 3.6, 0.7)), before_fn, after_fn)
    else:
        at = lt - 4.3
        if live_fn is None:
            page_bg(c, t, "pa")
            after_fn(c, at)
        else:
            def pg(cc, tt):
                page_bg(cc, tt, "pa")
                after_fn(cc, at)
            come_alive(c, at, pg, lambda cc, tt: live_fn(cc, tt - 1.8), 330, 660, 1.8, 0.9, sf=0.4)


# ================================================================ 六、走进当地人的生活
def courtyard(c, t):
    """院子里的小板凳和矮桌。"""
    vgrad(c, 0, 900, [(0, hexc("f3c79a")), (1, hexc("fbecd0"))])
    shape(c, rect(-20, 500, W + 40, 420), hexc("d9c4a8"), "cyw", lw=3)
    for i in range(6):
        shape(c, rect(i * 200 - 20, 470, 180, 40), hexc("8c5a3c"), f"cyr{i}", lw=2)
    with keep():
        for i in range(7):
            x = 80 + i * 150
            glow(c, x, 560, 60, hexc("ffd98a"), 0.4)
            circle(c, x, 560, 10, hexc("fff0b8"))
        line(c, [(0, 550), (W, 570)], "cyl", 2, hexc("6b4a32"))
    shape(c, rect(-20, 900, W + 40, 900), hexc("c9b59a"), "cyg", lw=3)
    for i in range(12):
        line(c, [(-10, 940 + i * i * 6), (W + 10, 940 + i * i * 6)], f"cyb{i}", 1.4, hexc("b39f86"), alpha=0.6)
    people = [(200, "8d6a9f", GRAN, "granny"), (360, "6b7a5a", hexc("3a3a3a"), "short"),
              (720, "c98d72", hexc("2f2a28"), "bang_short"), (880, "5d7a9a", hexc("2f2a28"), "short")]
    for i, (x, col, hr, st) in enumerate(people):
        shape(c, rect(x - 40, 1160, 80, 20), hexc("8c5a3c"), f"stool{i}", lw=2)
        local(c, x, 1160, 1.3, f"cyp{i}", hexc(col), hr, st, sit=True, mouth="laugh", look=0.5 if x < 540 else -0.5,
              arms=[(-20, -70), (30 + 10 * math.sin(t * 6 + i), -80)])
    shape(c, rect(500, 1160, 80, 20), hexc("8c5a3c"), "stoolg", lw=2)
    girl(c, 540, 1160, 1.3, sit=True, hat=False, mouth="laugh", look=0.0, arms=[(-30, -80), (30, -80)], key="gcy")
    shape(c, rect(260, 1180, 560, 30), hexc("8c5a3c"), "lowtab", lw=3)
    for x in (290, 770):
        shape(c, rect(x, 1210, 16, 70), hexc("7a4d33"), f"ltl{x}", lw=2)
    cols = ["d9653a", "6fa860", "e8c040", "b5533a"]
    for i in range(4):
        x = 330 + i * 140
        shape(c, ell(x, 1176, 46, 14, 14), hexc("f8f6f0"), f"cyd{i}", lw=2, amp=0.3)
        shape(c, ell(x, 1172, 32, 8, 12), hexc(cols[i]), f"cyf{i}", lw=1.4, amp=0.3)
        line(c, [(x - 4, 1160), (x - 10 + math.sin(t * 2 + i) * 6, 1130), (x, 1100)], f"cys{i}", 2, (1, 1, 1), alpha=0.6)


def kitchen(c, t):
    fill_all(c, hexc("e8dcc4"))
    for i in range(6):
        shape(c, rect(80 + i * 160, 160, 120, 90), hexc("dfe9ea"), f"tile{i}", lw=1.6, amp=0.4)
    shape(c, rect(60, 820, 960, 380), hexc("8c7a62"), "counter", lw=3)
    shape(c, rect(60, 800, 960, 30), hexc("b9a587"), "ctop", lw=2.4)
    with keep():
        glow(c, 760, 760, 140, hexc("ff9a50"), 0.5 + 0.2 * math.sin(t * 9))
        shape(c, ell(760, 780, 120, 34, 20, 0, math.pi), hexc("3a3a3a"), "wok", lw=3)
        for k in range(6):
            ph = (t * 0.7 + k / 6) % 1
            shape(c, ell(700 + k * 22 + math.sin(t + k) * 10, 720 - ph * 300, 30 + ph * 40, 18 + ph * 20, 12),
                  (1, 1, 1), f"smk{k}", lw=0.8, amp=0.4, alpha=0.5 * (1 - ph))
        shape(c, rect(260, 770, 220, 30), hexc("d9b778"), "board", lw=2)
        r = random.Random(4)
        for k in range(int(clamp(t / 0.3, 0, 10))):
            sz = r.uniform(6, 18)
            shape(c, rect(290 + k * 18, 760 - sz, sz, sz), hexc("6fa860"), f"veg{k}", lw=1, amp=0.3)
    local(c, 860, 1200, 1.6, "cookgran", hexc("8d6a9f"), GRAN, "granny", look=-0.8, mouth="laugh",
          arms=[(-50, -96), (24, -78)] if t > 2.2 else [(-24, -78), (40, -110)])
    girl(c, 380, 1200, 1.6, hat=False, look=0.3, mouth="laugh" if t > 2.4 else "flat",
         arms=[(-20, -110 + 10 * math.sin(t * 14)), (40, -112)], key="g13")


def cook_seq(c, t):
    if t < 3.6:
        kitchen(c, t)
    else:
        courtyard(c, t - 3.6)


def item_cloth(c, t):
    with keep():
        shape(c, [(380, 360), (700, 330), (720, 600), (370, 620)], hexc("2f7f8a"), "cloth", lw=2.4)
        for k in range(4):
            line(c, [(390, 400 + k * 60), (705, 370 + k * 60)], f"clz{k}", 4, hexc("f0c040"))
    tape(c, 380, 360, 80, 26, -0.6, "clt")
    hand(c, "阿姨送的布头", 540, 700, 34)


def item_receipt(c, t):
    with keep():
        shape(c, rect(400, 300, 280, 420), (1, 1, 1), "rc", lw=2, amp=0.3)
        for i, it in enumerate(["番茄 2斤", "青菜 1把", "辣椒 少许", "土豆 3个", "砍价成功！"]):
            text(c, it, 430, 360 + i * 64, 28, INK if i < 4 else RED, anchor="l")
    tape(c, 540, 300, 90, 26, 0.1, "rct")


def item_recipe(c, t):
    hand(c, "奶奶的菜谱", 540, 300, 44, rot=-0.04)
    for i, it in enumerate(["1. 油要烧热", "2. 菜别切太大（被笑了）", "3. 盐少放，最后放", "4. 大家一起吃！"]):
        hand(c, it, 200, 400 + i * 80, 32, rot=0.02 * (i % 2 * 2 - 1), anchor="l")


def item_target(c, t):
    with keep():
        for k, col in enumerate(("f4f2ec", "3a3f4a", "f4f2ec", "3a3f4a", "c9473b")):
            rr = 180 * (1 - k * 0.2)
            shape(c, ell(540, 520, rr, rr, 30), hexc(col), f"it{k}", lw=1.6, amp=0.2)
        circle(c, 540 + 0.55 * 180, 520 - 0.4 * 180, 8, hexc("1d1d1d"))
        circle(c, 540 + 0.16 * 180, 520 + 0.1 * 180, 8, hexc("1d1d1d"))
    tape(c, 400, 350, 90, 26, -0.5, "itt")
    hand(c, "第二枪近一点了！", 540, 740, 34, col=RED)


def item_sketch(c, t):
    with keep():
        shape(c, rect(250, 300, 580, 420), PAPER, "skb", lw=1.6)
        line(c, [(260, 700), (450, 420), (450, 320)], "sk1", 2, PENCIL)
        line(c, [(820, 700), (630, 420), (630, 320)], "sk2", 2, PENCIL)
        for k in range(3):
            shape(c, ell(330, 640 - k * 26, 50, 14, 12), None, f"sk3{k}", lw=1.6)
    hand(c, "清晨的小巷", 230, 750, 34, anchor="l")


def page_item(item_fn, title):
    def f(c, t):
        page_bg(c, t, "pi" + title)
        hand(c, title, 160, 210, 34, anchor="l", rot=-0.02)
        item_fn(c, t)
    return f


def j_local(item_fn, title, scene_fn, t0=1.4):
    pf = page_item(item_fn, title)

    def f(c, t):
        come_alive(c, t, pf, lambda cc, tt: scene_fn(cc, tt - t0 + 0.2), 420, 760, t0, 0.9, sf=0.4)
    return f


def page14(c, t):
    page_bg(c, t, "p14")
    scribble_reveal(c, "这一次，慢慢来", 300, 500, 54, prog(t, 0.2, 1.2), col=hexc("2f4a6a"))


j14 = None
j15 = j_local(item_cloth, "集市", d11_costume)
j16 = j_local(item_receipt, "菜市场", d12_market)
j17 = j_local(item_recipe, "做饭", cook_seq)
j18 = j_local(item_target, "射击", d14_shoot)
j19 = j_local(item_sketch, "清晨", d15_alley)


def j14(c, t):  # noqa: F811
    come_alive(c, t, page14, lambda cc, tt: d10_town(cc, tt - 1.6), 400, 640, 1.6, 0.9, sf=0.4)


def j20(c, t):
    page_bg(c, t, "p20", lines=False)
    with keep():                                                   # 左：第一章那个梦一样的气泡画
        pts = []
        for i in range(60):
            a = i / 60 * 2 * math.pi
            rr = 1 + 0.05 * math.cos(a * 9)
            pts.append((330 + math.cos(a) * 200 * rr, 520 + math.sin(a) * 160 * rr))
        c.save()
        spath(c, pts, True)
        c.clip()
        vgrad(c, 360, 680, [(0, hexc("3b3a6e")), (0.7, hexc("c8708a")), (1, hexc("f2b27a"))], 120, 540)
        c.restore()
        spath(c, pts, True)
        c.set_source_rgba(0.3, 0.3, 0.3, 0.8)
        c.set_line_width(2)
        c.stroke()
    girl(c, 330, 620, 0.8, outfit="folk", hat=True, mouth="laugh", key="g20d")
    hand(c, "想象", 330, 740, 30)
    r = random.Random(2)                                           # 右：一路贴满的小东西
    cols = ["2f7f8a", "f2a6a0", "f7e27a", "a8e07a", "9fc5e8", "c9a0dc"]
    for i in range(10):
        x, y = 640 + r.uniform(-30, 260), 340 + r.uniform(0, 420)
        with keep():
            c.save()
            c.translate(x, y)
            c.rotate(r.uniform(-0.4, 0.4))
            shape(c, rect(-50, -36, 100, 72), hexc(cols[i % 6]), f"col{i}", lw=1.4, amp=0.3)
            c.restore()
    hand(c, "真实", 760, 820, 30)
    u = prog(t, 1.4, 1.2)                                          # 画圈 + 写“更热闹”
    if u > 0:
        pts2 = [(760 + math.cos(a) * 220, 560 + math.sin(a) * 280) for a in [i / 40 * 2 * math.pi * u for i in range(41)]]
        with keep():
            line(c, pts2, "circle20", 4, RED)
    scribble_reveal(c, "更热闹！", 650, 960, 56, prog(t, 2.8, 1.0), col=RED, rot=-0.08)
    if u < 1:                                                      # 红笔：先画圈，再写字
        a = 2 * math.pi * u
        px_, py_ = 760 + math.cos(a) * 220, 560 + math.sin(a) * 280
    else:
        w_ = prog(t, 2.8, 1.0)
        px_, py_ = 650 + 240 * w_, 950 + 10 * math.sin(t * 20) * (w_ < 1)
    if t > 1.0:
        with keep():
            shape(c, [(px_, py_), (px_ + 12, py_ - 14), (px_ + 130, py_ + 120), (px_ + 116, py_ + 134), (px_ - 2, py_ + 18)],
                  RED, "rpen", lw=2)
            circle(c, px_ + 2, py_ + 2, 4, INK)


# ================================================================ 七、合上手账
def journal_closed(c, band):
    """鼓鼓的、合不上的手账，封面贴满票根和贴纸。"""
    with keep():
        shape(c, rrect(-300, -380, 600, 760, 20), hexc("8c5a3c"), "jc", lw=3)
        for k in range(6):                                          # 塞得鼓鼓的纸页
            shape(c, rect(-290 + k * 3, -390 - k * 4, 590, 20), [PAPER, hexc("f7e27a"), hexc("cfe4f2")][k % 3], f"jpg{k}",
                  lw=1.2, amp=0.4)
        r = random.Random(6)
        for k in range(9):                                          # 封面上的票根和贴纸
            x, y = r.uniform(-240, 200), r.uniform(-320, 300)
            c.save()
            c.translate(x, y)
            c.rotate(r.uniform(-0.5, 0.5))
            shape(c, rect(-50, -24, 100, 48), [hexc("cfe4f2"), hexc("f7e3b0"), hexc("f2d98a"), hexc("fbfaf6")][k % 4],
                  f"jcs{k}", lw=1.4, amp=0.3)
            c.restore()
        if band > 0:
            line(c, [(-310, lerp(-380, 60, band)), (310, lerp(-380, 60, band))], "jband", 8, RED)


def j21(c, t):
    """橡皮筋绑好 → 一张明信片滑出来 → 手账放进铁盒，盖上。"""
    fill_all(c, CLOTH)
    for i in range(12):
        line(c, [(i * 100, 0), (i * 100, 1920)], f"cl{i}", 1.4, darker(CLOTH, 0.9), alpha=0.4)
        line(c, [(0, i * 160), (1080, i * 160)], f"ch{i}", 1.4, darker(CLOTH, 0.9), alpha=0.4)
    band = ease_io(prog(t, 0.5, 1.0))
    slide = ease_io(prog(t, 1.8, 1.4))
    go = ease_io(prog(t, 3.8, 1.6))
    lid = 1.0 - ease_io(prog(t, 5.8, 0.7))
    bx, by, bs = 420, 1080, 1.6                                     # 铁盒
    if go > 0:
        c.save()
        c.translate(bx, by)
        c.scale(bs, bs)
        tinbox(c, 0, 0, lid * 1.2, "j21b", n=10)
        c.restore()
    if lid > 0.05:
        c.save()
        c.translate(lerp(540, bx, go), lerp(640, by - 230 * bs * 0.55, go))
        c.rotate(lerp(-0.04, 0.0, go))
        sc = lerp(1.0, 0.42, go)
        c.scale(sc, sc)
        journal_closed(c, band)
        c.restore()
    if go > 0:                                                      # 铁盒正面挡住手账下半截
        c.save()
        c.translate(bx, by)
        c.scale(bs, bs)
        with keep():
            shape(c, rrect(-165, -110, 330, 120, 12), hexc("6f8aa0"), "j21bb", lw=3)
            shape(c, rect(-165, -88, 330, 12), hexc("5d7489"), "j21bs", lw=2)
        c.restore()
    if slide > 0:                                                   # 明信片：一座蓝白色的海岛
        px_, py_ = lerp(600, 800, slide), lerp(800, 1130, slide)
        with keep():
            glow(c, px_, py_, 260 * slide, hexc("bfe0f2"), 0.35 * slide * (0.6 + 0.4 * prog(t, 6.6, 2.0)))
        from scenes03 import postcard
        c.save()
        c.translate(px_, py_)
        c.rotate(lerp(-0.1, 0.12, slide))
        c.translate(-px_, -py_)
        postcard(c, px_, py_, 0.9, "pc21")
        c.restore()


_STILL = {}


def journal_still():
    if "j" not in _STILL:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(surf)
        set_time(160.0)
        with grade(sat=1.0, dark=0.0, warm=0.1):
            j21(cc, 6.0)
        _STILL["j"] = surf
    return _STILL["j"]


def outro(c, t):
    book_outro(c, t, journal_still(), "© 2026 藤原樹\n未经授权请勿转载", end_mark="第三章 · 完")

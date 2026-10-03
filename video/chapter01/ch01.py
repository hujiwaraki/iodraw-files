"""第一章 · 出逃（第二版）—— 时间轴、字幕、调色。"""
from scenes import intro, s01_loop, s03_tide, s04_roots
from scenes_v2 import (outro2, p1_breakup, p2_office, p3_phone, s05_party, s06_empty, s07_depart, s08_drown, s08b_pause,
                       s09_wake, s10_popup, s11_hat, s12_untie, s13_imagine, s14_door)
from draw import ease_io, lerp, prog

NAME = "chapter01_出逃"
DUR = 121.0

SCENES = [
    (0.0, 6.0, intro),
    (6.0, 10.0, s01_loop),
    (10.0, 15.0, p1_breakup),
    (15.0, 20.0, p2_office),
    (20.0, 24.0, p3_phone),
    (24.0, 29.0, s03_tide),
    (29.0, 33.0, s04_roots),
    (33.0, 47.0, s05_party),
    (47.0, 52.0, s06_empty),
    (52.0, 60.0, s07_depart),
    (60.0, 65.0, s08_drown),
    (65.0, 68.0, s08b_pause),
    (68.0, 73.0, s09_wake),
    (73.0, 79.0, s10_popup),
    (79.0, 82.0, s11_hat),
    (82.0, 86.0, s12_untie),
    (86.0, 110.0, s13_imagine),
    (110.0, 115.0, s14_door),
    (115.0, 121.0, outro2),
]

TRANSITIONS = [(6.0, "fade"), (10.0, "page"), (15.0, "page"), (20.0, "page"), (24.0, "page"), (33.0, "page"),
               (52.0, "page"), (60.0, "page"), (86.0, "page")]

SUBS = [
    (6.3, 9.8, "在一个地方待了太久。", "dark"),
    (10.3, 23.8, "久到每一条街，\n都记得某一次难过。", "dark"),
    (24.3, 28.8, "恐惧、压力，和说不清的焦虑，\n像潮水一样，一点点漫上来。", "dark"),
    (29.3, 32.8, "不知道该怎么，\n和这片土地和平共处。", "light"),
    (33.3, 46.8, "也试过用很多事情，\n把日子填满。", "dark"),
    (47.3, 51.8, "可热闹散场以后，\n剩下的还是迷茫和空洞。", "light"),
    (52.3, 59.8, "也想过很多次离开，\n却总是迈不出那一步。", "dark"),
    (60.3, 64.8, "就这样一天天待着，\n那种感觉越来越重，快要把人吞没了。", "light"),
    (68.4, 72.8, "如果那些地方迟早要去，\n为什么不是现在？", "dark"),
    (73.3, 78.8, "世界太大了，\n人生也不一定只有一种活法。对吗？", "dark"),
    (79.3, 81.8, "想自己去验证一下。", "dark"),
    (82.3, 85.8, "于是开始想出逃。", "dark"),
    (86.4, 90.8, "去一个谁也不认识的地方，", "dark"),
    (91.0, 94.8, "穿当地人的衣服，\n吃他们吃的东西，", "dark"),
    (95.2, 99.8, "学他们生活的方式，\n走他们每天走过的路。", "dark"),
    (100.2, 103.8, "暂时放下原来的身份。", "dark"),
    (104.2, 109.6, "像重新出生一次，\n小小地重活一遍。", "dark"),
]


def grade_at(t):
    """色彩暗线：这片土地是灰蓝的；颜色先出现在想象里，再随门打开涌进现实。"""
    if t < 6.0 or t >= 115.0:
        return dict(sat=1.0, dark=0.0, warm=0.0)
    if t < 60.0:
        return dict(sat=0.12, dark=0.0, warm=0.0)
    if t < 68.0:
        return dict(sat=0.08, dark=lerp(0.0, 0.3, ease_io(prog(t, 60.0, 5.0))), warm=0.0)
    return dict(sat=0.3, dark=0.0, warm=0.3)

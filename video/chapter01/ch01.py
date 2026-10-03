"""第一章 · 出逃（第二版）—— 时间轴、字幕、调色。"""
from scenes import intro, s01_loop, s03_tide, s04_roots
from scenes_v2 import (outro2, p1_cafe, p2_office, p3_phone, s05_party, s06_empty, s07_depart, s08_drown, s08b_pause,
                       s09_wake, s10_popup, s11_hat, s12_untie, s13_imagine, s14_door)
from draw import ease_io, lerp, prog

NAME = "chapter01_出逃"
DUR = 112.0

SCENES = [
    (0.0, 6.0, intro),
    (6.0, 10.0, s01_loop),
    (10.0, 14.0, p1_cafe),
    (14.0, 19.0, p2_office),
    (19.0, 23.0, p3_phone),
    (23.0, 28.0, s03_tide),
    (28.0, 32.0, s04_roots),
    (32.0, 38.0, s05_party),
    (38.0, 43.0, s06_empty),
    (43.0, 51.0, s07_depart),
    (51.0, 56.0, s08_drown),
    (56.0, 59.0, s08b_pause),
    (59.0, 64.0, s09_wake),
    (64.0, 70.0, s10_popup),
    (70.0, 73.0, s11_hat),
    (73.0, 77.0, s12_untie),
    (77.0, 101.0, s13_imagine),
    (101.0, 106.0, s14_door),
    (106.0, 112.0, outro2),
]

TRANSITIONS = [(6.0, "fade"), (10.0, "page"), (14.0, "page"), (19.0, "page"), (23.0, "page"), (32.0, "page"),
               (43.0, "page"), (51.0, "page"), (77.0, "page")]

SUBS = [
    (6.3, 9.8, "在一个地方待了太久。", "dark"),
    (10.3, 22.8, "久到每一条街，\n都记得某一次难过。", "dark"),
    (23.3, 27.8, "恐惧、压力，和说不清的焦虑，\n像潮水一样，一点点漫上来。", "dark"),
    (28.3, 31.8, "不知道该怎么，\n和这片土地和平共处。", "light"),
    (32.3, 37.8, "也试过用很多事情，\n把日子填满。", "dark"),
    (38.3, 42.8, "可热闹散场以后，\n剩下的还是迷茫和空洞。", "light"),
    (43.3, 50.8, "也想过很多次离开，\n却总是迈不出那一步。", "dark"),
    (51.3, 55.8, "就这样一天天待着，\n那种感觉越来越重，快要把人吞没了。", "light"),
    (59.4, 63.8, "如果那些地方迟早要去，\n为什么不是现在？", "dark"),
    (64.3, 69.8, "世界太大了，\n人生也不一定只有一种活法。对吗？", "dark"),
    (70.3, 72.8, "想自己去验证一下。", "dark"),
    (73.3, 76.8, "于是开始想出逃。", "dark"),
    (77.4, 81.8, "去一个谁也不认识的地方，", "dark"),
    (82.0, 85.8, "穿当地人的衣服，\n吃他们吃的东西，", "dark"),
    (86.2, 90.8, "学他们生活的方式，\n走他们每天走过的路。", "dark"),
    (91.2, 94.8, "暂时放下原来的身份。", "dark"),
    (95.2, 100.6, "像重新出生一次，\n小小地重活一遍。", "dark"),
]


def grade_at(t):
    """色彩暗线：这片土地是灰蓝的；颜色先出现在想象里，再随门打开涌进现实。"""
    if t < 6.0 or t >= 106.0:
        return dict(sat=1.0, dark=0.0, warm=0.0)
    if t < 51.0:
        return dict(sat=0.12, dark=0.0, warm=0.0)
    if t < 59.0:
        return dict(sat=0.08, dark=lerp(0.0, 0.3, ease_io(prog(t, 51.0, 5.0))), warm=0.0)
    return dict(sat=0.3, dark=0.0, warm=0.3)

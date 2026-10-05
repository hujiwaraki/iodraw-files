"""第二章 · 一个人（第二版）—— 时间轴、字幕、调色。字幕每屏最多两行、每行不超过 15 字。"""
from scenes02 import (c00_box, c01_rush, c02_ask, c03_bus, c04_couples, c05_altitude, c06_dinner, c07_hard, c07_split,
                      c08_door, c09_alone, c09_montage, c10_eyes, c11_platform, c13_aging, c14_scale, c14_wait, c15_old,
                      c16_go, c17_map, intro, outro, c08b_home, c17_desk, outro2)
from draw import ease_io, lerp, prog

NAME = "chapter02_一个人"
DUR = 149.5

SCENES = [
    (0.0, 6.0, intro),
    (6.0, 15.0, c00_box),
    (15.0, 20.0, c01_rush),
    (20.0, 29.0, c02_ask),
    (29.0, 34.5, c03_bus),
    (34.5, 42.5, c04_couples),
    (42.5, 48.5, c05_altitude),
    (48.5, 70.5, c06_dinner),
    (70.5, 76.0, c07_split),
    (76.0, 85.5, c08_door),
    (85.5, 88.5, c08b_home),
    (88.5, 95.5, c11_platform),
    (95.5, 104.5, c14_wait),
    (104.5, 110.5, c13_aging),
    (110.5, 116.5, c14_scale),
    (116.5, 126.5, c15_old),
    (126.5, 131.5, c16_go),
    (131.5, 143.5, c17_desk),
    (143.5, 149.5, outro2),
]

TRANSITIONS = [(6.0, "fade"), (20.0, "page"), (29.0, "fade"), (48.5, "page"), (70.5, "page"), (76.0, "fade"),
               (85.5, "fade"), (88.5, "page"), (104.5, "page"), (126.5, "page"), (131.5, "page")]

SUBS = [
    (6.4, 10.4, "第一次一个人出门旅行，\n是什么时候呢？", "light"),
    (10.7, 14.8, "好像，\n已经是很久很久以前的事了。", "light"),
    (15.3, 19.8, "那时候其实没想过要一个人，\n只是想快点逃走。", "dark"),
    (20.3, 25.2, "随口问了几个朋友要不要一起，\n大家都说最近没空。", "dark"),
    (25.6, 28.8, "那就报个团吧。", "dark"),
    (29.3, 34.3, "就这样，\n去了海拔四千米的高原。", "dark"),
    (34.8, 42.3, "团里的人，\n都是成双成对的。", "dark"),
    (42.8, 48.3, "高原反应来的时候，\n也只能自己扛着。", "light"),
    (48.8, 51.6, "可一桌人围坐吃饭的时候，", "dark"),
    (51.9, 55.6, "一对对情侣却各自低头玩着手机，\n一句话也没有。", "dark"),
    (55.9, 58.6, "看起来，\n也没有很开心。", "dark"),
    (58.9, 61.6, "那时候很不理解：", "dark"),
    (61.9, 66.3, "不那么有共鸣的两个人，\n为什么可以一起去那么远的地方。", "dark"),
    (66.6, 70.3, "突然觉得有点悲哀。", "light"),
    (70.8, 75.8, "两个人的寂寞，\n似乎还不如一个人的孤独。", "light"),
    (76.3, 82.8, "还遇到了一些\n说不清的事。", "light"),
    (88.8, 92.3, "回来以后，也想过等一等，\n等一个真正合适的同行者。", "dark"),
    (92.5, 95.2, "可不知道那个人\n什么时候会出现，", "dark"),
    (95.8, 104.2, "也等不来\n一个更好的时机。", "dark"),
    (104.8, 110.3, "害怕孤独，\n也害怕衰老。", "dark"),
    (110.8, 116.3, "而最终，对衰老的恐惧，\n压过了对一切风险的恐惧。", "dark"),
    (116.8, 122.3, "害怕有一天，终于有了时间，\n也终于遇到了对的人，", "dark"),
    (122.5, 126.3, "却已经没有了现在这样强烈的，\n想出发、想看世界的心情。", "dark"),
    (126.8, 131.3, "于是不再等了，\n一个人出发。", "dark"),
    (134.5, 142.8, "不知不觉，\n一个人去了很多地方。", "light"),
]


def grade_at(t):
    """色彩：灯下的现在 → 灰色的回忆 → 高原的蓝 → 团餐 → 灰色的等待与害怕 → 上路 → 回到灯下。"""
    if t < 6.0 or t >= 143.5:
        return dict(sat=1.0, dark=0.0, warm=0.0)
    if t < 15.0:
        return dict(sat=0.55, dark=0.0, warm=0.3)
    if t < 29.0:
        return dict(sat=0.12, dark=0.0, warm=0.0)
    if t < 48.5:
        return dict(sat=0.6, dark=0.0, warm=0.0)
    if t < 70.5:
        return dict(sat=0.45, dark=0.0, warm=0.0)
    if t < 85.5:
        return dict(sat=0.6, dark=0.0, warm=0.0)
    if t < 88.5:
        return dict(sat=0.3, dark=0.0, warm=0.1)
    if t < 116.5:
        return dict(sat=0.15, dark=0.0, warm=0.0)
    if t < 123.3:
        return dict(sat=0.1, dark=0.1, warm=0.0)
    if t < 131.5:
        return dict(sat=0.45, dark=0.0, warm=0.25)
    return dict(sat=lerp(0.6, 0.95, ease_io(prog(t, 131.5, 3.0))), dark=0.0, warm=0.25)

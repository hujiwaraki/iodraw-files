"""第八章 · 她的小时候 —— 时间轴、字幕、调色。字幕每屏最多两行、每行不超过 15 字。"""
from scenes08b import intro, n01, n02, n03, n04, n05, n06, n07, n08, n09, n10, n11, outro

NAME = "chapter08_她的小时候"
S = 3.4                                   # 一屏字幕的长度

_seq = [(intro, 6.0), (n01, 2 * S), (n02, 2 * S), (n03, 2 * S), (n04, 2 * S), (n05, 2 * S), (n06, 2 * S), (n07, S),
        (n08, 3 * S), (n09, 2 * S), (n10, 2 * S), (n11, 2 * S), (outro, 6.0)]
SCENES = []
_t = 0.0
for _fn, _d in _seq:
    SCENES.append((round(_t, 2), round(_t + _d, 2), _fn))
    _t += _d
DUR = round(_t, 2)
START = {fn.__name__: a for a, b, fn in SCENES}

TRANSITIONS = [(a, "fade") for a, b, fn in SCENES[1:]]


def _screens(t0, items, gap=0.3):
    out = []
    t = t0
    for s, st in items:
        out.append((t + 0.3, t + S - gap, s, st))
        t += S
    return out


SUBS = (
    _screens(START["n01"], [("这一次，不是一个人出发。", "dark"), ("她说：\n带你去看看我长大的地方。", "dark")]) +
    _screens(START["n02"], [("那是一座长在山上的城，", "dark"), ("路总是一会儿上坡，\n一会儿下坡。", "dark")]) +
    _screens(START["n03"], [("一路上，她都在讲小时候。", "dark"), ("讲得最多的，是外婆。", "dark")]) +
    _screens(START["n04"], [("她说，外婆是个很善良的人。", "dark"), ("对她好，\n对身边每一个人都好。", "dark")]) +
    _screens(START["n05"], [("后来见到了外婆。", "dark"), ("外婆拉着我的手，\n像早就认识我一样。", "dark")]) +
    _screens(START["n06"], [("外婆做了一大桌菜，", "dark"), ("她又拉着我，\n把街上的小吃一家家吃过去。", "dark")]) +
    _screens(START["n07"], [("辣得直冒汗，\n还是一口接一口。", "dark")]) +
    _screens(START["n08"], [("晚上挤在一张床上，", "light"), ("聊她，聊我，\n聊小时候，也聊以后，", "light"),
                            ("不知不觉，\n就聊到了很晚很晚。", "light")]) +
    _screens(START["n09"], [("原来人和人之间，", "light"), ("心和心的距离，\n居然可以这么近。", "light")]) +
    _screens(START["n10"], [("两个人一起，也可以很轻松。", "dark"), ("不用迁就，\n也不用刻意找话题。", "dark")]) +
    _screens(START["n11"], [("那是她的家乡，不是我的。", "dark"), ("可从那以后，那座山城，\n也有一小块，是我的了。", "dark")])
)


def grade_at(t):
    if t < 6.0 or t >= START["outro"]:
        return dict(sat=1.0, dark=0.0, warm=0.0)
    return dict(sat=1.0, dark=0.0, warm=0.06)

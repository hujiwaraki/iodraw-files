"""番外 · 同路人 —— 时间轴、字幕、调色。字幕每屏最多两行、每行不超过 15 字。"""
from scenes08b import intro, m01, m02, m03, m04, m05, m05b, m06, m07, m08, m09, m10, m11, outro

NAME = "番外_同路人"
S = 3.4                                   # 一屏字幕的长度

_seq = [(intro, 6.0), (m01, 2 * S), (m02, S), (m03, 2 * S), (m04, 2 * S), (m05, 1.4 * S), (m05b, 3 * S), (m06, 1.3 * S),
        (m07, 2 * S), (m08, 2.3 * S), (m09, 3 * S), (m10, 2 * S), (m11, 8.5 * S), (outro, 6.0)]
SCENES = []
_t = 0.0
for _fn, _d in _seq:
    SCENES.append((round(_t, 2), round(_t + _d, 2), _fn))
    _t += _d
DUR = round(_t, 2)
START = {fn.__name__: a for a, b, fn in SCENES}
LEN = {fn.__name__: b - a for a, b, fn in SCENES}

TRANSITIONS = [(a, "fade") for a, b, fn in SCENES[1:]]


def _screens(name, items, gap=0.3):
    """一个镜头里的几屏字幕，平分这个镜头的时长。"""
    step = LEN[name] / len(items)
    t = START[name]
    out = []
    for s, st in items:
        out.append((t + 0.3, t + step - gap, s, st))
        t += step
    return out


SUBS = (
    _screens("m01", [("一向喜新厌旧，", "dark"), ("去过的地方，\n基本不会想再去第二次。", "dark")]) +
    _screens("m02", [("可这座城，去了三次。", "dark")]) +
    _screens("m03", [("前两次去，也没怎么玩，", "light"), ("就吃了两顿火锅。", "light")]) +
    _screens("m04", [("这次不一样，是跟她一起去的。", "dark"), ("她说：\n你想去，我可以和你一起回去。", "dark")]) +
    _screens("m05", [("一路上，她都在讲小时候的事。", "dark")]) +
    _screens("m05b", [("走过老城的一砖一瓦，", "dark"), ("这座城有过沉甸甸的过去，\n如今的日子却过得很巴适。", "light"),
                      ("跟着她走这一趟，\n好像也慢慢更懂她了。", "light")]) +
    _screens("m06", [("吃了好多她从小吃到大的东西。", "dark")]) +
    _screens("m07", [("明明挺能吃辣，", "dark"), ("吃完，肠子还是不太服气。", "dark")]) +
    _screens("m08", [("晚上两个人挤在一张床上，", "light"), ("都凌晨了，\n还在说哪家好吃、哪里好玩。", "light")]) +
    _screens("m09", [("那时候突然觉得，", "light"), ("人和人之间，心和心的距离，", "light"), ("居然可以这么近。", "light")]) +
    _screens("m10", [("两个人待在一起很舒服，", "dark"), ("不用迁就谁，\n也不用硬找话题。", "dark")]) +
    _screens("m11", [("说不清为什么，\n好像变得包容了许多。", "dark"), ("可和她在一起，\n其实也没什么需要包容的。", "dark"),
                     ("人和人之间的和谐，\n或许就在于匹配吧。", "dark"),
                     ("那没那么匹配的大多数人呢？", "dark"), ("是不是，就只剩下包容了？", "dark"),
                     ("大概率是的吧。", "dark"), ("看人，多看优点。", "dark"),
                     ("遇到合拍的人，是运气。", "dark"), ("和不合拍的人好好相处，\n也是门学问。", "dark"),
                     ("或许，人生的新篇章，", "dark"), ("就从这里悄悄开始了。", "dark")])
)


def grade_at(t):
    if t < 6.0 or t >= START["outro"]:
        return dict(sat=1.0, dark=0.0, warm=0.0)
    if START["m01"] <= t < START["m04"]:                          # 前两次：偏灰、偏冷一点
        return dict(sat=0.8, dark=0.0, warm=0.0)
    return dict(sat=1.0, dark=0.0, warm=0.06)

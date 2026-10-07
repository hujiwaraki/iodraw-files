"""第七章 · 那个人 —— 配乐（纯代码合成）。

极简钢琴，大量留白。全章一个速度：每拍 0.75 秒，一小节 4 拍 = 3 秒；快一点的声音落在 0.375 的细分上。
线出现时总有一声轻轻的拨弦；高原那一句只剩心跳和风；动摇那一段回忆时稍微暖一点；
线断的那一下，所有声音都停住；春天的清晨，钢琴回到大调。
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
from synth import (SR, Mix, cello, heartbeat, knock, music_box, pad, piano, pluck, rumble, scratch, snap, swell,  # noqa: E402
                   swish, thump, tick, _t)

DUR = 174.0
M = Mix(DUR)
B = 0.75
BAR = 3.0


def P(sig, t, vol=1.0, pan=0.0):
    M.place(sig, t, vol, pan)


THEME_MAJ = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 79, 2)]
THEME_MIN = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 74, 2)]
CH = {"F": [53, 57, 60], "C": [48, 55, 64], "Dm": [50, 57, 62], "Bb": [46, 53, 58], "Am": [45, 52, 57], "Gm": [43, 50, 58]}
ROOT = {"F": 41, "C": 36, "Dm": 38, "Bb": 34, "Am": 45, "Gm": 43}


def melody(t0, notes, beat, inst="piano", vol=1.0, shift=0, pan=0.0):
    for b, m, d in notes:
        t = t0 + b * beat
        if inst == "box":
            P(music_box(m + shift), t, vol, pan)
        else:
            P(piano(m + shift, d * beat * 0.95), t, vol, pan)


def bar(t0, ch, vol=0.2, pattern=(0, 1, 2, 1)):
    """左手：根音 + 每拍一个分解和弦音。"""
    P(piano(ROOT[ch] + 12, BAR * 0.9), t0, vol * 1.1, -0.2)
    for j, k in enumerate(pattern):
        P(piano(CH[ch][k] + 12, B * 0.9), t0 + j * B, vol * 0.7, 0.1)


def noise(length, lo, hi, vol, fade=0.3):
    from scipy.signal import butter, sosfilt
    n, t = _t(length)
    s = sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), np.random.randn(n))
    env = np.clip(t / fade, 0, 1) * np.clip((length - t) / fade, 0, 1)
    return s * env * vol


def wind(length, vol=0.1, gust=0.4):
    n, t = _t(length)
    return noise(length, 250, 1500, 1.0, 1.0) * (0.6 + gust * np.sin(2 * np.pi * 0.35 * t)) * vol


def string_ting(t0, vol=0.22, m=88):                                 # 线：一声轻轻的拨弦
    P(pluck(m, length=2.2, bright=0.14), t0, vol, 0.3)
    P(pluck(m + 7, length=1.6, bright=0.12), t0 + 0.02, vol * 0.4, 0.3)


def hum(length, vol=0.05):                                           # 机舱的低鸣
    return noise(length, 60, 260, 1.0, 1.0) * vol


# ================================================================ 片头 0–6
melody(0.4, THEME_MAJ, 0.7, "box", 0.3, pan=0.1)
P(pad(CH["F"], 4.5, att=1.5), 0.6, 0.3)
for t0 in (2.1, 2.55, 3.0):
    P(swish(), t0, 0.5)

# ================================================================ 一根线 6–27
for i, ch in enumerate(["F", "C", "Dm", "Bb", "F", "C", "Bb"]):
    bar(6.0 + i * BAR, ch, 0.16)
string_ting(6.75)
for k, m in enumerate((84, 88, 86, 84, 81, 84)):                    # 她雀跃地说话
    P(music_box(m, 0.8), 7.125 + k * 0.375, 0.07, -0.2)
string_ting(9.75, 0.18, 93)                                          # 镜头顺着线往外走
P(swell(3.0, 300, 3000), 9.8, 0.1)
string_ting(13.5, 0.26, 86)                                          # 线一颤
P(swish(1.2), 14.0, 0.25)                                            # 纸飞机顺着线滑过来
P(snap(), 16.875, 0.12)                                              # 落在窗台上
melody(18.0, THEME_MIN[:5], B, "piano", 0.24, shift=-12)             # 不知道是好奇，还是只是想陪着去
string_ting(23.625, 0.2, 91)
P(swish(1.0), 23.7, 0.2)
P(swish(1.0), 24.1, 0.15)

# ================================================================ 陪伴不一定是同行 27–53
P(hum(6.5), 27.0, 1.0)
for i, ch in enumerate(["F", "C"]):
    bar(27.0 + i * BAR, ch, 0.18)
melody(27.0, THEME_MAJ, B, "piano", 0.3, shift=-12)                  # 也许这一次，可以走得远一点
for i, ch in enumerate(["Dm", "Bb"]):
    bar(33.0 + i * BAR, ch, 0.15)
for k in range(5):
    P(knock(), 33.375 + k * 0.75, 0.05, 0.4)                        # ta 的脚步
for i, ch in enumerate(["F", "Am", "Bb"]):                           # 展厅：高高的、空空的
    P(piano(CH[ch][2] + 24, 2.6), 39.75 + i * BAR, 0.14, 0.2)
    P(piano(ROOT[ch] + 12, 2.8), 39.75 + i * BAR, 0.12, -0.2)
for k in range(8):                                                   # 手机上一格一格地填
    P(tick(k % 2 == 1), 46.5 + k * 0.375, 0.06, 0.3)
P(pad([45, 52, 60], 4.0, att=1.5, rel=2.0, bright=0.7), 49.0, 0.14)  # 两团光
P(piano(72, 3.0), 49.5, 0.14, -0.4)
P(piano(66, 3.0), 50.25, 0.1, 0.4)

# ================================================================ 一场很私人的对话 53–88.5
for k in range(6):                                                   # 拍完就走
    P(tick(), 53.375 + k * 0.375, 0.08, 0.2)
P(wind(6.0, 0.06), 53.0, 1.0)
P(piano(65, 3.0), 56.0, 0.14)
for i, ch in enumerate(["F", "Dm", "Bb", "C", "F", "Dm", "Bb", "C"]):
    bar(59.25 + i * BAR, ch, 0.15)
melody(59.25, THEME_MAJ, B * 1.5, "piano", 0.26, shift=-12)
melody(68.25, THEME_MAJ, B, "piano", 0.24, shift=-12)
P(wind(3.0, 0.08), 65.5, 1.0)                                        # 荒原上的风
P(noise(3.5, 150, 2000, 0.12, 1.0), 71.7, 1.0)                       # 海浪
# 高原：只剩呼吸、心跳和风
P(wind(9.0, 0.1, 0.5), 75.0, 1.0)
for k in range(4):
    P(noise(0.35, 400, 2500, 0.08, 0.1), 75.0 + k * 0.75, 1.0)       # 喘气
for k in range(8):
    P(heartbeat(), 78.0 + k * 0.75, 0.38)
P(pad([41, 48, 53], 3.5, att=1.0, rel=2.0, bright=0.6), 81.0, 0.12)
P(swell(2.4, 300, 4000), 81.0, 0.08)
P(pad(CH["F"] + [72], 4.5, att=1.5, rel=2.5, bright=1.2), 84.0, 0.18)  # 星轨
for k, m in enumerate((96, 93, 89, 91, 96)):
    P(music_box(m, 2.0), 84.75 + k * 0.75, 0.07, -0.4 + k * 0.2)

# ================================================================ 交集很小 88.5–99.5
bar(88.5, "F", 0.16)
for k, m in enumerate((84, 88, 91, 96)):                             # 一群鸟转了个大弯
    P(music_box(m, 1.2), 89.25 + k * 0.375, 0.08, -0.3 + k * 0.2)
P(pad([45, 52, 57], 3.5, att=0.8, rel=2.0, bright=0.5), 91.7, 0.14)  # 颜色被抽走
P(piano(57, 3.0), 91.875, 0.12)
P(piano(72, 3.5), 95.25, 0.14, -0.5)                                 # 两盏路灯：两个隔得很远的音
P(piano(78, 3.5), 96.75, 0.1, 0.5)

# ================================================================ 动摇的四个月 99.5–123.5
for i, ch in enumerate(["Dm", "Bb", "F", "C"]):
    P(piano(ROOT[ch] + 12, 2.8), 99.75 + i * BAR, 0.12, -0.2)
    P(piano(CH[ch][1] + 24, 2.4), 99.75 + i * BAR + 1.5, 0.08, 0.2)
P(noise(3.0, 300, 3000, 0.04, 1.0), 108.5, 1.0)                      # 窗外的雨
melody(111.75, THEME_MAJ, B, "piano", 0.24, shift=-12)               # 回忆：暖一点
P(pad(CH["F"], 6.0, att=1.5, rel=2.0, bright=1.0), 111.5, 0.14)
for i, ch in enumerate(["Dm", "Bb"]):
    P(piano(ROOT[ch] + 12, 2.8), 117.75 + i * BAR, 0.11, -0.2)
P(piano(84, 2.5), 121.5, 0.1, 0.4)                                   # 远处那颗很亮的星
P(music_box(96, 2.0), 122.25, 0.06, 0.4)

# ================================================================ 线断了 123.5–137.5
P(piano(65, 3.0), 123.75, 0.12)
P(piano(62, 3.0), 125.25, 0.1)
P(wind(4.2, 0.08, 0.6) * np.linspace(0.4, 1.6, int(4.2 * SR)), 123.5, 1.0)   # 风越来越大
string_ting(127.65, 0.3, 81)                                         # 啪——然后什么声音都没有
for i, m in enumerate((84, 81, 77)):                                 # 纸条被风吹走
    P(music_box(m, 2.2), 130.5 + i * 0.75, 0.08, 0.2 + i * 0.2)
P(wind(4.5, 0.14, 0.7), 133.0, 1.0)                                  # 风雪吞掉远处的灯
P(cello(38, 4.2, att=1.2), 133.2, 0.4)
P(cello(45, 3.0, att=1.0), 134.6, 0.25)

# ================================================================ 有人来过，又离开 137.5–147
P(hum(9.5, 0.05), 137.5, 1.0)
melody(138.0, THEME_MIN, B * 1.25, "piano", 0.22, shift=-12)
for i, ch in enumerate(["Dm", "Bb", "Gm"]):
    P(piano(ROOT[ch] + 12, 2.8), 138.0 + i * BAR, 0.11, -0.2)

# ================================================================ 春天的清晨 147–174
for k in range(6):                                                   # 鸟叫
    P(music_box(100 + (k % 3) * 2, 0.4), 147.375 + k * 0.375 + (k // 3) * 1.5, 0.05, 0.5)
P(knock(), 147.4, 0.08)                                              # 推开窗
for i, ch in enumerate(["F", "C"]):
    bar(147.75 + i * BAR, ch, 0.15)
P(pad(CH["F"] + [72], 6.0, att=2.0, rel=2.0, bright=1.2), 147.5, 0.14)
P(snap(), 154.5, 0.1)                                                # 碰杯
P(music_box(103, 0.8), 154.5, 0.12)
P(thump(), 158.25, 0.15)                                             # 拉上去
P(hum(3.0, 0.05), 159.5, 1.0)
for i, ch in enumerate(["F", "Dm", "Bb"]):
    bar(153.75 + i * BAR, ch, 0.14)
melody(162.75, THEME_MAJ, B * 0.75, "piano", 0.3, shift=-12)         # 送走纸飞机
P(swish(1.4), 163.1, 0.3)
P(knock(), 166.8, 0.1)                                               # 关上窗
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.0), 166.5 + i * 0.07, 0.2, -0.3 + i * 0.2)

# ================================================================ 片尾 168–174
P(swish(), 169.6, 0.4)
melody(168.4, THEME_MAJ, 0.6, "box", 0.24, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.0), 168.4, 0.35)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 171.8 + i * 0.07, 0.24, pan=-0.3 + i * 0.2)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.9), (6, 1.2), (39, 1.2), (44, 1.5), (52, 1.6), (56, 1.3), (75, 1.2), (84, 1.3), (99.5, 1.5), (123.5, 1.4), (127.6, 1.4), (127.7, 0.0),
        (129.4, 0.0), (130.3, 1.4), (137.5, 1.4), (147, 1.2), (168, 0.75), (DUR + 1, 0.75)])
duck = [(0, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 174, 4)))

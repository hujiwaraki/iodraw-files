"""第四章 · 不敢抵达的地方 —— 配乐（纯代码合成）。

钢琴 + 弦乐铺底，偏慢，带一点惆怅。全章一个速度：每拍 0.75 秒，一小节 4 拍 = 3 秒。
换房间的钢琴 → 月夜的海（弦乐、慢半拍的主旋律）→ 抛锚、碰不到底 → 天亮 → 橱窗前轻一点
→ 蜜月圣地：音色变亮变满 → 落日、夜里只剩一个长音 → 孤独压下来：只剩低音弦乐 → 留给一些人：慢慢暖起来
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
from synth import (SR, Mix, bass, cello, knock, music_box, pad, piano, pluck, scratch, snap, swell, swish, thump,  # noqa: E402
                   tick, _t)

DUR = 140.0
M = Mix(DUR)
B = 0.75                                  # 一拍
BAR = 3.0                                 # 一小节


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
        elif inst == "pluck":
            P(pluck(m + shift, length=max(0.8, d * beat * 1.6), bright=0.2), t, vol, pan)
        else:
            P(piano(m + shift, d * beat * 0.95), t, vol, pan)


def piano_bar(t0, ch, vol=0.25, pattern=(0, 1, 2, 1)):
    """左手：根音 + 慢慢的分解和弦（每拍一个音）。"""
    P(piano(ROOT[ch], BAR * 0.9), t0, vol * 1.1, -0.2)
    for j, k in enumerate(pattern):
        P(piano(CH[ch][k] + 12, B * 0.9), t0 + j * B, vol * 0.7, 0.1)


def strings(t0, ch, bars, vol=0.3, bright=1.2):
    P(pad(CH[ch] + [CH[ch][0] + 12], bars * BAR, att=1.2, rel=1.6, bright=bright), t0, vol)
    P(cello(ROOT[ch] + 12, bars * BAR, att=1.0), t0, vol * 0.9)


def noise(length, lo, hi, vol, fade=0.3):
    from scipy.signal import butter, sosfilt
    n, t = _t(length)
    s = sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), np.random.randn(n))
    env = np.clip(t / fade, 0, 1) * np.clip((length - t) / fade, 0, 1)
    return s * env * vol


def waves(length, vol=0.12):
    n, t = _t(length)
    return noise(length, 150, 2000, 1.0, 1.0) * (0.4 + 0.6 * np.sin(2 * np.pi * 0.12 * t) ** 2) * vol


def wind(length, vol=0.1):
    n, t = _t(length)
    return noise(length, 300, 1600, 1.0, 0.8) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * t)) * vol


# ================================================================ 片头 0–6
melody(0.4, THEME_MAJ, 0.7, "box", 0.32, pan=0.1)
P(pad(CH["F"], 4.5, att=1.5), 0.6, 0.3)
for t0 in (2.1, 2.55, 3.0):
    P(swish(), t0, 0.5)

# ================================================================ 一、去哪都不对 6–17：换房间的钢琴
for i, ch in enumerate(["Dm", "Bb", "F", "C"]):
    piano_bar(6.0 + i * BAR, ch, vol=0.22)
for tk in (8.1, 10.4, 12.7):                                       # 换房间时一闪
    P(swish(0.35), tk, 0.18)
P(pad(CH["Dm"], 8.0, att=2.0, rel=2.0, bright=1.0), 9.0, 0.15)
P(swell(1.6, 200, 2000), 15.2, 0.25)                               # 床变成小船
P(waves(3.0, 0.1), 15.4, 1.0)

# ================================================================ 月夜的海 17–52：弦乐 + 慢半拍的主旋律
P(waves(35.0, 0.09), 17.0, 1.0)
for i, ch in enumerate(["Dm", "Bb", "F", "C", "Dm", "Bb", "Gm", "C", "Dm", "Bb", "F", "C"]):
    strings(17.0 + i * BAR, ch, 1, vol=0.22, bright=1.4)
melody(17.0, THEME_MIN, B * 2, "piano", 0.32, shift=-12, pan=0.1)  # 慢半拍
P(swish(0.4), 18.2, 0.3)                                           # 抛锚
P(thump(), 18.7, 0.25)                                             # 落水
for k in range(14):                                                 # 绳子一圈圈往下放
    P(tick(k % 2 == 1), 18.9 + k * 0.28, 0.07)
P(thump(), 22.7, 0.35)                                             # 绳子放到了头
P(cello(33, 3.0, att=0.3), 22.7, 0.35)
for i, tk in enumerate((25.8, 29.1, 32.4)):                         # 三座小岛：举起锚，又放下
    P(piano([62, 65, 69][i], 2.0), tk, 0.2, 0.2)
    P(piano([57, 60, 64][i], 2.0), tk + 1.5, 0.15, -0.2)
P(swell(1.6, 300, 3000), 33.8, 0.2)                                # 起雾
melody(29.0, THEME_MIN[4:], B * 2, "piano", 0.24, shift=-12, pan=-0.1)
# 沙滩
for k in range(10):
    P(scratch(0.2), 35.1 + k * 0.24, 0.12, pan=-0.3)               # 写字
P(noise(2.4, 200, 4000, 0.25, 0.6), 38.4, 1.0)                     # 浪打过来
P(piano(64, 2.0), 39.2, 0.18)
# 水下 → 纸锚 → 风筝 → 天亮
P(cello(31, 3.6, att=1.0), 41.0, 0.3)
for k in range(5):
    P(knock(), 44.3 + k * B / 2, 0.08)                              # 拉绳子
for i, m in enumerate((84, 88, 91)):
    P(music_box(m, 1.6), 46.4 + i * 0.1, 0.25)                    # 原来是纸折的
P(wind(4.4, 0.12), 47.6, 1.0)
P(swell(3.0, 300, 6000), 48.4, 0.3)
for i, ch in enumerate(["F", "C"]):                                 # 天亮：大调
    strings(46.0 + i * BAR, ch, 1, vol=0.24, bright=1.8)
melody(49.0, THEME_MAJ[:5], B, "pluck", 0.3, shift=-12, pan=0.2)

# ================================================================ 二、橱窗 52–66：轻一点
for i, ch in enumerate(["F", "C", "Dm", "Bb"]):
    piano_bar(52.0 + i * BAR, ch, vol=0.2)
melody(52.0, THEME_MAJ, B, "piano", 0.28, pan=0.1)
for k in range(int(6.0 / B * 2)):
    P(knock(), 53.2 + k * B / 2, 0.035, pan=0.2)                    # 脚步
P(pad(CH["Dm"], 5.4, att=1.0, rel=1.6, bright=1.0), 60.0, 0.22)   # 停在最后一张前
P(piano(76, 3.0), 61.5, 0.18)                                      # 伸手
P(piano(74, 3.0), 63.6, 0.14)                                      # 收回来

# ================================================================ 蜜月圣地 66–93：音色变亮、变满
P(swell(1.2, 400, 8000), 66.0, 0.3)                                # 穿过玻璃
for i, ch in enumerate(["F", "C", "Dm", "Bb", "F", "C", "Bb", "C", "F"]):
    t0 = 66.0 + i * BAR
    strings(t0, ch, 1, vol=0.24, bright=2.0)
    for j in range(8):                                              # 竖琴一样的分解和弦
        P(pluck(CH[ch][j % 3] + 24 + (12 if j >= 6 else 0), length=1.4, bright=0.18), t0 + j * B / 2, 0.11, 0.3)
melody(67.5, THEME_MAJ, B, "piano", 0.3, pan=0.1)
melody(76.5, THEME_MAJ, B, "piano", 0.28, pan=0.1)
for k in range(6):                                                  # 光斑
    P(music_box(96 + (k % 3) * 2, 0.8), 83.4 + k * B / 2, 0.06, -0.4 + k * 0.15)
P(swell(2.6, 200, 3000), 86.6, 0.25)                                # 落日
P(cello(41, 3.0, att=0.8), 86.6, 0.3)
P(pad(CH["F"] + [72], 3.2, att=0.4, rel=2.0, bright=1.0), 89.9, 0.12)   # 夜里：只剩一个长音

# ================================================================ 孤独压下来 93–104：只剩低音弦乐
for i, ch in enumerate(["Dm", "Bb", "Gm"]):
    P(cello(ROOT[ch] + 12, BAR + 0.6, att=0.8), 93.0 + i * BAR, 0.4)
    P(cello(ROOT[ch], BAR + 0.6, att=0.8), 93.0 + i * BAR, 0.3)
P(pad([38, 45, 50], 11.0, att=3.0, rel=2.0, bright=0.6), 93.0, 0.25)
for i, m in enumerate((74, 72, 69, 67, 65, 62)):                    # 灰色的光点落下来
    P(piano(m, 1.6), 99.0 + i * B, 0.12, -0.3 + i * 0.12)
P(noise(4.0, 2000, 7000, 0.04, 1.5), 99.6, 1.0)

# ================================================================ 退出海报 104–110
P(swish(0.6), 104.9, 0.25)
P(piano(62, 4.0), 105.5, 0.28)
P(piano(57, 4.0), 107.0, 0.22)

# ================================================================ 三、留给一些人 110–134：慢慢暖起来
for i, ch in enumerate(["F", "C", "Dm", "Bb", "F", "C", "Bb", "C"]):
    piano_bar(110.0 + i * BAR, ch, vol=0.2)
    if i >= 2:
        strings(110.0 + i * BAR, ch, 1, vol=0.16 + 0.02 * i, bright=1.6)
for k in range(3):                                                  # 放卡片
    P(tick(), 112.0 + k * 1.6, 0.12)
melody(116.0, THEME_MAJ, B, "piano", 0.3, pan=0.1)
for i, tk in enumerate((118.3, 122.5, 126.8)):                      # 三个想象的画面
    for j, m in enumerate((84, 88, 91)):
        P(music_box(m + i * 2, 1.6), tk + j * 0.12, 0.16)
melody(124.0, THEME_MAJ, B, "piano", 0.28, pan=-0.1)
P(pad(CH["F"] + [72], 5.0, att=1.5, rel=2.0), 130.0, 0.22)
P(noise(4.0, 300, 2500, 0.03, 1.0), 130.5, 1.0)                    # 街上的人声

# ================================================================ 片尾 134–140
P(swish(), 135.6, 0.4)
melody(134.4, THEME_MAJ, 0.6, "box", 0.42, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.0), 134.4, 0.4)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 137.8 + i * 0.07, 0.4, pan=-0.3 + i * 0.2)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.85), (6, 1.0), (134, 0.55), (DUR + 1, 0.55)])
M.muffle([(0, 0), (19.0, 0), (19.4, 1), (24.5, 1), (25.0, 0), (41.0, 1), (44.0, 1), (44.4, 0), (DUR + 1, 0)])
duck = [(0, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 140, 4)))

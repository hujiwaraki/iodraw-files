"""终章 · 此心安处 —— 配乐（纯代码合成）。

全章一个速度：每拍 0.75 秒，一小节 3 秒；快一点的声音落在 0.375 的细分上。
台灯下：很淡的钢琴，翻照片的轻响 → 笔尖落纸 → 高原：风声、低沉的长音、像心跳的低鼓，垒石头的轻响
→ 平原：木吉他，像走路一样的节奏 → 黄昏的小桌：暖一点 → 海洋：弦乐铺底和潮水，海鸟，雷雨，冲出去时旋律完整出现
→ 鹅卵石滩：安静的浪 → 翻书：一页一页的翻页声，八音盒完整奏一遍全系列的主旋律 → 推门走进晨光
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
from synth import (SR, Mix, bass, cello, kick, knock, music_box, pad, piano, pluck, rumble, scratch, shaker, snap,  # noqa: E402
                   swell, swish, thump, tick, _t)

DUR = 141.5
M = Mix(DUR)
B = 0.75
BAR = 3.0


def P(sig, t, vol=1.0, pan=0.0):
    M.place(sig, t, vol, pan)


THEME_MAJ = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 79, 2)]
THEME_END = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 74, .5), (6, 77, 3)]
CH = {"F": [53, 57, 60], "C": [48, 55, 64], "Dm": [50, 57, 62], "Bb": [46, 53, 58], "Am": [45, 52, 57]}
ROOT = {"F": 41, "C": 36, "Dm": 38, "Bb": 34, "Am": 45}
ARP = {"F": [53, 57, 60, 65], "C": [48, 55, 60, 64], "Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62], "Am": [45, 52, 57, 60]}


def melody(t0, notes, beat, inst="piano", vol=1.0, shift=0, pan=0.0):
    for b, m, d in notes:
        t = t0 + b * beat
        if inst == "box":
            P(music_box(m + shift), t, vol, pan)
        elif inst == "pluck":
            P(pluck(m + shift, length=max(0.8, d * beat * 1.6), bright=0.22), t, vol, pan)
        elif inst == "cello":
            P(cello(m + shift, d * beat * 0.95, att=0.2), t, vol, pan)
        else:
            P(piano(m + shift, d * beat * 0.95), t, vol, pan)


def noise(length, lo, hi, vol, fade=0.3):
    from scipy.signal import butter, sosfilt
    n, t = _t(length)
    s = sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), np.random.randn(n))
    env = np.clip(t / fade, 0, 1) * np.clip((length - t) / fade, 0, 1)
    return s * env * vol


def wind(length, vol=0.1, gust=0.4):
    n, t = _t(length)
    return noise(length, 250, 1500, 1.0, 1.0) * (0.6 + gust * np.sin(2 * np.pi * 0.3 * t)) * vol


def waves_snd(length, vol=0.1):
    n, t = _t(length)
    return noise(length, 150, 2200, 1.0, 1.0) * (0.4 + 0.6 * np.sin(2 * np.pi * 0.19 * t) ** 2) * vol


def strings(t0, ch, dur, vol=0.25, bright=1.3):
    P(pad(CH[ch] + [CH[ch][0] + 12], dur, att=1.0, rel=1.6, bright=bright), t0, vol)
    P(cello(ROOT[ch] + 12, dur, att=0.8), t0, vol * 0.8)


def guitar_bar(t0, ch, vol=0.12):
    for j, k in enumerate((0, 1, 2, 3, 2, 1, 2, 3)):
        P(pluck(ARP[ch][k] + 12, length=1.0, bright=0.24), t0 + j * 0.375, vol, 0.15)
    P(bass(ROOT[ch] + 12, BAR * 0.9), t0, vol * 1.4)


# ================================================================ 片头 0–6
melody(0.4, THEME_MAJ, 0.7, "box", 0.3, pan=0.1)
P(pad(CH["F"], 4.5, att=1.5), 0.6, 0.3)
for t0 in (2.1, 2.55, 3.0):
    P(swish(), t0, 0.5)

# ================================================================ 台灯下 6–16
for i, (m, d) in enumerate(((69, 2.5), (65, 2.5), (67, 2.0), (64, 3.0))):
    P(piano(m, d), 6.0 + i * 2.25, 0.16, 0.1)
for k in range(8):                                                   # 照片一格格往上滚
    P(tick(), 6.375 + k * 0.375, 0.035, 0.3)
P(pad([45, 52, 57], 3.5, att=1.0, rel=1.5, bright=0.6), 9.3, 0.12)    # 照片褪色
P(knock(), 12.6, 0.08)                                               # 手机扣下
P(scratch(1.6), 13.2, 0.12)                                          # 笔尖落纸
P(swell(1.8, 300, 6000), 14.4, 0.16)

# ================================================================ 高原 16–41：风、低沉的长音、像心跳的低鼓
P(wind(25.0, 0.1, 0.5), 16.0, 1.0)
for i, (m, d) in enumerate(((38, 6.0), (41, 6.0), (36, 6.0), (38, 7.0))):
    P(cello(m + 12, d, att=1.5), 16.0 + i * 6.0, 0.4)
    P(pad([m + 12, m + 19], d, att=2.0, rel=2.0, bright=0.7), 16.0 + i * 6.0, 0.1)
for k in range(int(25 / BAR)):                                       # 低鼓，像心跳
    P(kick(0.5), 16.0 + k * BAR, 0.14)
    P(kick(0.5), 16.0 + k * BAR + 0.375, 0.07)
for k, m in enumerate((69, 72, 74, 76)):                             # 雪峰上的金光
    P(music_box(m + 12, 2.0), 22.75 + k * 0.75, 0.07, 0.4)
for k in range(7):                                                   # 一块块垒石头
    P(knock(), 28.7 + k * 0.743, 0.12, -0.2)
P(noise(6.0, 200, 3000, 0.18, 0.8), 34.8, 1.0, -0.3)                 # 雪水冲下来

# ================================================================ 平原 41–61.5：木吉他，像走路
for i, ch in enumerate(["F", "C", "Dm", "Bb", "F"]):
    guitar_bar(41.25 + i * BAR, ch, 0.11)
for k in range(int(13.5 / 0.75)):
    P(shaker(), 41.625 + k * 0.75, 0.04, 0.3)
melody(44.25, THEME_MAJ, B, "pluck", 0.26, shift=-12)
for k in range(5):                                                   # 踩着踏脚石过河
    P(knock(), 51.0 + k * 0.75, 0.06)
for i, ch in enumerate(["F", "Bb"]):                                 # 黄昏的小桌，暖一点
    P(pad(CH[ch] + [CH[ch][0] + 12], BAR, att=1.0, rel=1.5, bright=1.1), 55.0 + i * BAR, 0.16)
    for j, k in enumerate((0, 1, 2, 1)):
        P(pluck(ARP[ch][k] + 12, length=1.4, bright=0.2), 55.0 + i * BAR + j * B, 0.1, 0.15)
P(snap(), 56.5, 0.06)

# ================================================================ 海洋 61.5–98：弦乐和潮水
P(waves_snd(49.0, 0.1), 61.5, 1.0)
for i, ch in enumerate(["F", "C", "Dm", "Bb", "F"]):
    strings(61.5 + i * 3.1, ch, 3.1, 0.2, bright=1.3 + 0.1 * i)
P(swish(1.0), 70.8, 0.15)                                            # 扬帆
P(swell(2.6, 300, 5000), 73.9, 0.1)                                  # 一场未知而远大的冒险
for i, ch in enumerate(["F", "Am"]):                                 # 风平浪静，闭着眼
    P(pad(CH[ch] + [CH[ch][0] + 12], 1.6, att=0.8, rel=1.2, bright=1.2), 77.0 + i * 1.6, 0.16)
P(rumble(6.3) * 0.6, 80.2, 1.0)                                      # 动荡和摇摆
for t0 in (81.5, 84.7):
    P(thump(), t0, 0.3)
    P(noise(1.4, 100, 900, 0.2, 0.2), t0 + 0.05, 1.0)
for i, ch in enumerate(["Dm", "Bb"]):
    P(cello(ROOT[ch] + 12, 3.0, att=0.6), 80.2 + i * 3.15, 0.4)
P(pad(CH["F"], 6.3, att=2.0, rel=1.5, bright=0.8), 80.2, 0.1)        # 保持平衡：底下一直有一个稳的音
for k in range(5):                                                   # 海鸟
    P(music_box(100 + (k % 2) * 3, 0.4), 87.0 + k * 0.75, 0.04, 0.5)
melody(87.0, THEME_MAJ, B * 0.75, "piano", 0.24, shift=-12)          # 每个活在当下的瞬间
P(pad(CH["F"] + [72], 6.0, att=1.5, rel=2.0, bright=1.4), 86.5, 0.16)
for i, ch in enumerate(["F", "C"]):                                  # 永不回头：旋律完整地冲出来
    strings(93.0 + i * 2.5, ch, 2.5, 0.24, bright=1.6)
melody(93.0, THEME_MAJ, 0.5625, "cello", 0.5, shift=-12)
for k in range(6):
    P(kick(0.5), 93.0 + k * 0.75, 0.1)
for i, ch in enumerate(["F", "Dm", "Bb", "F"]):                      # 鹅卵石滩：安静下来
    P(pad(CH[ch], 3.2, att=1.2, rel=1.6, bright=1.0), 98.0 + i * 3.125, 0.14)
for k in range(14):
    P(tick(k % 2 == 1), 98.7 + k * 0.75 + 0.1 * (k % 3), 0.03, -0.4 + (k % 5) * 0.2)
P(music_box(84, 2.0), 103.0, 0.1)                                    # 捡起一颗

# ================================================================ 翻书 110.5–123：八音盒完整奏一遍主旋律
melody(111.0, THEME_MAJ, B, "box", 0.28, pan=0.1)
melody(117.0, THEME_END, B, "box", 0.28, pan=-0.1)
P(pad(CH["F"] + [72], 12.0, att=2.0, rel=2.0, bright=1.3), 110.5, 0.16)
for k in range(9):                                                   # 一页一页往回翻
    P(swish(0.35), 113.6 + k * 0.689, 0.1, 0.2)
P(thump(), 121.5, 0.12)                                              # 合上

# ================================================================ 推门走进晨光 123–135.5
for i, ch in enumerate(["F", "C", "Bb", "F"]):
    P(piano(ROOT[ch] + 12, BAR * 0.9), 123.0 + i * BAR, 0.12, -0.2)
    for j, k in enumerate((0, 1, 2, 1)):
        P(piano(CH[ch][k] + 12, B * 0.9), 123.0 + i * BAR + j * B, 0.08, 0.1)
P(knock(), 123.5, 0.08)                                              # 鹅卵石放在书上
P(swell(2.4, 400, 7000), 127.1, 0.14)                                # 推开门
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 132.5 + i * 0.07, 0.2, -0.3 + i * 0.2)

# ================================================================ 片尾 135.5–141.5
P(swish(), 137.1, 0.4)
melody(135.9, THEME_MAJ, 0.6, "box", 0.24, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.0), 135.9, 0.35)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 139.3 + i * 0.07, 0.24, pan=-0.3 + i * 0.2)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.9), (6, 1.4), (9, 1.7), (15.5, 1.6), (16, 1.1), (41, 1.1), (50, 1.2), (54, 1.6), (61, 1.5), (62, 1.0), (110.5, 1.1), (122.5, 1.1), (124.5, 1.6), (135, 1.4), (135.5, 0.75), (DUR + 1, 0.75)])
duck = [(0, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 140, 4)))

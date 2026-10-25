"""第八章 · 同路人 —— 配乐（纯代码合成）。

开头往前赶的拨弦（一路向前、不回头）→ 停在山城：停一拍 → 前两次的火锅：单薄一点 → 跟她一起去：拨弦和轻轻的手鼓
→ 小时候：八音盒 → 小摊：热闹一点 → 夜里聊天：只剩很轻的钢琴 → 心和心的距离：一个长长的和弦
→ 长椅上睡着：慢下来 → 一起走下梯坎：旋律慢慢收回系列的主题。
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "series"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter01"))
from synth import SR, Mix, bass, cello, kick, knock, music_box, pad, piano, pluck, shaker, swish, tick  # noqa: E402
import ch08b  # noqa: E402

DUR = ch08b.DUR
T = ch08b.START
LEN = ch08b.LEN
M = Mix(DUR)
B = 0.6
BAR = 2.4


def P(sig, t, vol=1.0, pan=0.0):
    if 0 <= t < DUR:
        M.place(sig, t, vol, pan)


THEME = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 79, 2)]
THEME_END = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 74, .5), (6, 77, 3)]
CH = {"F": [53, 57, 60], "C": [48, 55, 64], "Dm": [50, 57, 62], "Bb": [46, 53, 58], "Am": [45, 52, 57]}
ROOT = {"F": 41, "C": 36, "Dm": 38, "Bb": 34, "Am": 45}
ARP = {"F": [53, 57, 60, 65], "C": [48, 55, 60, 64], "Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62], "Am": [45, 52, 57, 60]}
PROG = ["F", "C", "Dm", "Bb"]


def melody(t0, notes, beat, inst="box", vol=1.0, shift=0, pan=0.0):
    for b, m, d in notes:
        t = t0 + b * beat
        if inst == "box":
            P(music_box(m + shift), t, vol, pan)
        elif inst == "pluck":
            P(pluck(m + shift, length=max(0.8, d * beat * 1.6), bright=0.24), t, vol, pan)
        else:
            P(piano(m + shift, d * beat * 0.95), t, vol, pan)


def guitar(t0, ch, vol=0.1, pan=0.15):
    for j, k in enumerate((0, 1, 2, 3, 2, 1, 2, 3)):
        P(pluck(ARP[ch][k] + 12, length=1.0, bright=0.26), t0 + j * B / 2, vol, pan)
    P(bass(ROOT[ch] + 12, BAR * 0.9), t0, vol * 1.3)


# ================================================================ 片头
melody(0.4, THEME, 0.7, "box", 0.3, pan=0.1)
P(pad(CH["F"], 4.5, att=1.5), 0.6, 0.3)
for t0 in (2.1, 2.55, 3.0):
    P(swish(), t0, 0.5)

# ================================================================ 一向喜新厌旧：往前赶的拨弦
t0 = T["m01"]
for i in range(int(LEN["m01"] / (BAR * 0.75))):
    guitar(t0 + i * BAR * 0.75, PROG[i % 4], 0.08)
    for j in range(4):
        P(shaker(), t0 + i * BAR * 0.75 + j * B * 0.75 + B * 0.375, 0.035, 0.3)
for f in (2.0, 4.3):                                                 # 翻页
    P(swish(), t0 + f, 0.3)
# 停在山城：停一拍，一个长音
P(pad(CH["F"] + [72], LEN["m02"], att=0.6, rel=1.6, bright=1.0), T["m02"] + 0.2, 0.18)
melody(T["m02"] + 0.6, THEME[:4], 0.6, "box", 0.18)

# ================================================================ 前两次的火锅：单薄一点
t0 = T["m03"]
for i, ch in enumerate(["Dm", "Bb", "Dm", "C"]):
    P(pluck(ARP[ch][0] + 12, length=1.8, bright=0.18), t0 + i * 1.7, 0.14)
    P(pad(CH[ch], 1.7, att=0.5, rel=1.0, bright=0.8), t0 + i * 1.7, 0.08)
    P(pluck(ARP[ch][2] + 12, length=1.2, bright=0.18), t0 + i * 1.7 + 0.85, 0.09)
P(swish(), T["m03"] + 3.4, 0.25)                                    # 画面一闪

# ================================================================ 跟她一起去 → 小时候：拨弦、轻轻的手鼓、八音盒
t0 = T["m04"]
for i in range(int((T["m06"] - t0) / BAR) + 1):
    guitar(t0 + i * BAR, PROG[i % 4], 0.09)
    for j in range(4):
        P(shaker(), t0 + i * BAR + j * B + B / 2, 0.035, 0.3)
        P(kick(0.4), t0 + i * BAR + j * B, 0.05 if j % 2 else 0.08)
melody(T["m04"] + 0.6, THEME, B, "pluck", 0.18, shift=-12)
for k in range(10):                                                  # 梯坎：一级一级的脚步
    P(tick(k % 2 == 1), T["m04"] + 0.3 + k * 0.62, 0.04, -0.2)
melody(T["m05"] + 1.0, THEME, 0.5, "box", 0.2, pan=-0.1)

# ================================================================ 小摊：热闹一点
t0 = T["m06"]
for i in range(int((T["m08"] - t0) / BAR) + 1):
    guitar(t0 + i * BAR, PROG[i % 4], 0.11)
    for j in range(4):
        P(shaker(), t0 + i * BAR + j * B + B / 2, 0.045, 0.3)
        P(knock(), t0 + i * BAR + j * B, 0.025, -0.3)
melody(T["m06"] + 0.3, THEME, B, "pluck", 0.22)
for i, m in enumerate((72, 69, 65, 60)):                             # 肠子不太服气：咕噜往下掉
    P(pluck(m, length=0.5, bright=0.3), T["m07"] + 3.6 + i * 0.16, 0.12, 0.2)

# ================================================================ 夜里聊天：只剩很轻的钢琴
t0 = T["m08"]
for i, ch in enumerate(["F", "Dm", "Bb", "C"]):
    P(piano(ROOT[ch] + 24, BAR * 0.9), t0 + i * 1.95, 0.1, -0.2)
    for j, k in enumerate((0, 1, 2, 1)):
        P(piano(CH[ch][k] + 12, B * 0.9), t0 + i * 1.95 + j * 0.49, 0.06, 0.1)
for k in range(6):                                                   # 窗外的灯一格一格熄掉
    P(music_box(84 - (k % 3) * 3, 1.2), t0 + 2.8 + k * 0.8, 0.06, 0.3)

# ================================================================ 心和心的距离：一个长长的和弦
P(pad(CH["F"] + [65, 69, 72], LEN["m09"], att=2.0, rel=2.5, bright=1.2), T["m09"], 0.2)
melody(T["m09"] + 3.6, THEME, 0.7, "piano", 0.12)

# ================================================================ 长椅上睡着：慢下来
for i, ch in enumerate(["F", "C", "Bb"]):
    P(pad(CH[ch], 2.4, att=0.8, rel=1.4, bright=0.9), T["m10"] + i * 2.27, 0.22)
    P(pluck(ARP[ch][0] + 12, length=1.6, bright=0.2), T["m10"] + i * 2.27, 0.13)

# ================================================================ 一起走下梯坎：旋律慢慢收回系列的主题
P(music_box(77, 2.0), T["m11"] + 0.6, 0.12)                          # 醒过来
for i in range(3):
    guitar(T["m11"] + 3.4 + i * BAR, PROG[i % 4], 0.07)
melody(T["m11"] + 3.6, THEME_END, 0.8, "box", 0.24, pan=0.1)
P(pad(CH["F"] + [72], 6.8, att=1.5, rel=2.0, bright=1.2), T["m11"] + 3.4, 0.16)

# ================================================================ 片尾
t0 = T["outro"]
P(swish(), t0 + 1.6, 0.4)
melody(t0 + 0.4, THEME, 0.6, "box", 0.24, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.0), t0 + 0.4, 0.35)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), t0 + 3.8 + i * 0.07, 0.24, pan=-0.3 + i * 0.2)

M.gain([(0, 0.9), (6, 1.3), (T["m08"], 1.3), (T["m08"] + 0.5, 1.6), (T["outro"], 1.2), (T["outro"] + 0.4, 0.8),
        (DUR + 1, 0.8)])

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"))
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, int(DUR) - 3, 4)))

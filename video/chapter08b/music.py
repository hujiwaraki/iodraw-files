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

# 每一段只留一两样乐器，换段时上一段先收掉，再进下一段（不叠在一起）。
def strum(t0, t1, vol=0.09, beat=1.0, shake=0.0):
    """t0–t1 之间的分解和弦（可选轻轻的沙锤），最后一小节自动收轻。"""
    bar = BAR * beat
    n = max(1, int((t1 - t0) / bar))
    for i in range(n):
        v = vol * (0.6 if i == n - 1 else 1.0)
        ch = PROG[i % 4]
        for j, k in enumerate((0, 1, 2, 3, 2, 1, 2, 3)):
            P(pluck(ARP[ch][k] + 12, length=1.0, bright=0.26), t0 + i * bar + j * bar / 8, v, 0.15)
        P(bass(ROOT[ch] + 12, bar * 0.9), t0 + i * bar, v * 1.2)
        if shake:
            for j in range(4):
                P(shaker(), t0 + i * bar + j * bar / 4 + bar / 8, shake * (0.6 if i == n - 1 else 1.0), 0.3)


# ================================================================ 一向喜新厌旧：往前赶的拨弦
strum(T["m01"], T["m02"], 0.12, beat=0.75, shake=0.03)
for f in (2.0, 4.3):                                                 # 翻页
    P(swish(), T["m01"] + f, 0.25)
# 停在山城：停一拍，一个长音
P(pad(CH["F"] + [72], LEN["m02"], att=0.6, rel=1.6, bright=1.0), T["m02"] + 0.2, 0.16)
melody(T["m02"] + 0.6, THEME[:4], 0.6, "box", 0.16)

# ================================================================ 前两次的火锅：单薄一点
t0 = T["m03"]
for i, ch in enumerate(["Dm", "Bb", "Dm", "C"]):
    P(pluck(ARP[ch][0] + 12, length=1.8, bright=0.18), t0 + i * 1.7, 0.2)
    P(pluck(ARP[ch][2] + 12, length=1.2, bright=0.18), t0 + i * 1.7 + 0.85, 0.12)
P(swish(), T["m03"] + 3.4, 0.2)                                     # 画面一闪

# ================================================================ 跟她一起去：拨弦 + 梯坎上的脚步；小时候：八音盒（拨弦让出来）
strum(T["m04"], T["m05"], 0.13, shake=0.025)
for k in range(8):
    P(tick(k % 2 == 1), T["m04"] + 0.4 + k * 0.7, 0.03, -0.2)
P(pad(CH["F"] + [CH["F"][0] + 12], LEN["m05"], att=0.6, rel=1.4, bright=1.0), T["m05"], 0.12)
melody(T["m05"] + 0.6, THEME, 0.5, "box", 0.2, pan=-0.1)

# ================================================================ 老城：低低的大提琴 → 防空洞里的火锅：拨弦一点点回来
t0 = T["m05b"]
for i, m in enumerate((38, 41)):
    P(cello(m, 1.7), t0 + 0.1 + i * 1.7, 0.24, -0.1)
P(pad(CH["Dm"], 3.2, att=1.0, rel=1.0, bright=0.8), t0, 0.08)
strum(t0 + 3.4, T["m06"], 0.09, shake=0.015)
melody(t0 + 5.0, THEME[:6], B, "pluck", 0.12)

# ================================================================ 小摊：热闹一点，只用拨弦 + 沙锤
strum(T["m06"], T["m08"], 0.1, shake=0.04)

# ================================================================ 夜里聊天：只剩很轻的钢琴
t0 = T["m08"]
for i, ch in enumerate(["F", "Dm", "Bb", "C"]):
    P(piano(ROOT[ch] + 24, BAR * 0.9), t0 + i * 1.95, 0.1, -0.2)
    for j, k in enumerate((0, 1, 2, 1)):
        P(piano(CH[ch][k] + 12, B * 0.9), t0 + i * 1.95 + j * 0.49, 0.06, 0.1)
for k in range(6):                                                   # 窗外的灯一格一格熄掉
    P(music_box(84 - (k % 3) * 3, 1.2), t0 + 2.8 + k * 0.8, 0.05, 0.3)

# ================================================================ 心和心的距离：一个长长的和弦
P(pad(CH["F"] + [65, 69, 72], LEN["m09"], att=2.0, rel=2.5, bright=1.2), T["m09"], 0.18)
melody(T["m09"] + 3.6, THEME, 0.7, "piano", 0.12)

# ================================================================ 长椅上睡着：慢下来
for i, ch in enumerate(["F", "C", "Bb"]):
    P(pad(CH[ch], 2.4, att=0.8, rel=1.4, bright=0.9), T["m10"] + i * 2.27, 0.2)
    P(pluck(ARP[ch][0] + 12, length=1.6, bright=0.2), T["m10"] + i * 2.27, 0.12)

# ================================================================ 一起走下梯坎：旋律慢慢收回系列的主题
P(music_box(77, 2.0), T["m11"] + 0.6, 0.12)                          # 醒过来
melody(T["m11"] + 4.2, THEME, 0.8, "box", 0.2, pan=0.1)
P(pad(CH["F"] + [72], 6.0, att=1.5, rel=2.0, bright=1.2), T["m11"] + 4.0, 0.14)
P(pad(CH["Dm"] + [69], 5.4, att=1.5, rel=2.0, bright=1.0), T["m11"] + 8.0, 0.14)   # 问题：停在小调上
melody(T["m11"] + 13.4, THEME_END, 0.8, "box", 0.22, pan=-0.1)                     # 自己的回答：回到主题
P(pad(CH["F"] + [72], 5.0, att=1.2, rel=2.0, bright=1.2), T["m11"] + 13.4, 0.16)
P(pad(CH["Bb"] + [70], 2.6, att=1.0, rel=1.4, bright=1.0), T["m11"] + 18.5, 0.13)   # 合拍是运气
P(pad(CH["F"] + [72, 77], 3.6, att=1.0, rel=2.4, bright=1.2), T["m11"] + 21.1, 0.16)  # 也是门学问
for i, m_ in enumerate((65, 69, 72, 77)):
    P(music_box(m_, 3.0), T["m11"] + 21.4 + i * 0.12, 0.1, -0.3 + i * 0.2)

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

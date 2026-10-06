"""第六章 · 模糊地带 —— 配乐（纯代码合成）。

慢速：每拍 0.75 秒，一小节 4 拍 = 3 秒；快的段落在本段内部用 0.375 / 0.1875 的细分，节奏音都落在格子上。
大雨：只有雨声和低低的大提琴 → 起雾：钢琴一个音一个音地进来 → 粉笔圆：不解决的和弦
→ 报复性地找答案：又急又快，睡着时戛然而止 → 月亮升起：第一次有旋律 → 悬在那里：八音盒
→ 日常快切：轻快的节拍 → 看到云：旋律完整出现，吉他加进来 → 回家路上
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
from synth import (SR, Mix, bass, cello, jingle, kick, knock, music_box, pad, piano, pluck, rain, rumble, scratch,  # noqa: E402
                   shaker, snap, swell, swish, thump, tick, _t)

DUR = 130.0
M = Mix(DUR)
B = 0.75
BAR = 3.0


def P(sig, t, vol=1.0, pan=0.0):
    M.place(sig, t, vol, pan)


THEME_MAJ = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 79, 2)]
THEME_MIN = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 74, 2)]
CH = {"F": [53, 57, 60], "C": [48, 55, 64], "Dm": [50, 57, 62], "Bb": [46, 53, 58], "Am": [45, 52, 57], "Gm": [43, 50, 58]}
ROOT = {"F": 41, "C": 36, "Dm": 38, "Bb": 34, "Am": 45, "Gm": 43}
ARP = {"F": [53, 57, 60, 65], "C": [48, 55, 60, 64], "Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62], "Am": [45, 52, 57, 60]}


def melody(t0, notes, beat, inst="piano", vol=1.0, shift=0, pan=0.0):
    for b, m, d in notes:
        t = t0 + b * beat
        if inst == "box":
            P(music_box(m + shift), t, vol, pan)
        elif inst == "pluck":
            P(pluck(m + shift, length=max(0.8, d * beat * 1.6), bright=0.22), t, vol, pan)
        else:
            P(piano(m + shift, d * beat * 0.95), t, vol, pan)


def noise(length, lo, hi, vol, fade=0.3):
    from scipy.signal import butter, sosfilt
    n, t = _t(length)
    s = sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), np.random.randn(n))
    env = np.clip(t / fade, 0, 1) * np.clip((length - t) / fade, 0, 1)
    return s * env * vol


def arp(t0, ch, vol, step, pattern=(0, 1, 2, 3, 2, 1, 2, 3), pan=0.15, shift=12):
    for j, k in enumerate(pattern):
        P(pluck(ARP[ch][k] + shift, length=1.0, bright=0.24), t0 + j * step, vol, pan)


def strings(t0, ch, dur, vol=0.3, bright=1.2):
    P(pad(CH[ch] + [CH[ch][0] + 12], dur, att=1.2, rel=1.6, bright=bright), t0, vol)
    P(cello(ROOT[ch] + 12, dur, att=1.0), t0, vol * 0.9)


# ================================================================ 片头 0–6
melody(0.4, THEME_MIN, 0.7, "box", 0.3, pan=0.1)
P(pad(CH["Dm"], 4.5, att=1.5), 0.6, 0.3)
for t0 in (2.1, 2.55, 3.0):
    P(swish(), t0, 0.5)

# ================================================================ 很烂的时候 6–31：只有雨声和低低的大提琴
P(rain(25.5) * 0.32, 5.5, 1.0)
for i, (m, d) in enumerate(((38, 6.0), (34, 6.0), (36, 6.0), (33, 7.0))):   # D – Bb – C – A，很低
    P(cello(m + 12, d, att=1.6), 6.0 + i * 6.0, 0.55)
P(noise(0.9, 300, 2400, 0.35, 0.25), 7.3, 1.0, 0.3)                # 一阵风，伞翻了
P(swish(0.5), 7.5, 0.4)
P(rumble(1.6), 8.6, 0.35)                                           # 车开过来
P(noise(0.8, 800, 6000, 0.4, 0.08), 9.5, 1.0, 0.2)                 # 哗——溅了一身水
for k in range(8):                                                  # 咖啡馆的钟
    P(tick(k % 2 == 1), 13.0 + k * B, 0.12)
P(piano(57, 2.0), 16.0, 0.12)                                       # 叶子垂下去
P(piano(53, 2.4), 17.5, 0.1)
P(piano(50, 2.4), 19.4, 0.1)                                        # 伞递了出去
for t0, m in ((22.2, 89), (22.9, 93), (23.6, 86)):                  # 远处的烟花
    P(thump(), t0, 0.12)
    P(music_box(m, 1.4), t0 + 0.05, 0.07)
P(noise(5.0, 60, 220, 0.12, 1.0), 25.6, 1.0)                        # 冰箱的嗡嗡声
P(knock(), 28.2, 0.18)                                              # 手机扣在桌上
P(pad([38, 45, 50], 6.0, att=2.0, rel=2.5, bright=0.6), 25.6, 0.14)

# ================================================================ 起雾 31–61：钢琴一个音一个音地进来
P(rain(3.0) * 0.18 * np.linspace(1, 0, int(3.0 * SR)), 31.0, 1.0)   # 雨停了
P(pad(CH["Dm"] + [62], 30.0, att=4.0, rel=3.0, bright=0.9), 31.0, 0.14)
notes = [(31.75, 69), (34.0, 72), (36.25, 74), (38.5, 72),
         (40.0, 69), (41.5, 65), (43.0, 67), (44.5, 69), (46.0, 72), (47.5, 70),
         (49.75, 69), (51.25, 65), (52.75, 67), (53.5, 69), (55.0, 64),
         (56.5, 65), (57.25, 69), (58.0, 72), (58.75, 74), (59.5, 72), (60.25, 77)]
for t0, m in notes:
    P(piano(m, 1.8), t0, 0.2, 0.1)
for i, ch in enumerate(["Dm", "Bb", "F", "C", "Dm", "Bb", "F", "C", "Dm", "Bb"]):
    if i >= 3:                                                      # 第三屏开始才有左手
        P(piano(ROOT[ch] + 12, BAR * 0.9), 31.0 + i * BAR, 0.12, -0.2)
P(music_box(96, 2.0), 49.6, 0.18)                                   # 一滴水
P(swell(2.0, 200, 1600), 49.7, 0.12)
P(scratch(0.5), 56.4, 0.1)                                          # 折纸
P(scratch(0.4), 57.2, 0.08)

# ================================================================ 粉笔圆 61–68：不解决的和弦
for k in range(3):
    t0 = 61.0 + k * 2.3
    P(scratch(1.6), t0, 0.12, 0.1)                                  # 粉笔画圈
    P(noise(0.35, 1500, 6000, 0.1, 0.1), t0 + 1.9, 1.0)             # 擦掉
for i, ch in enumerate(("Bb", "C")):                                # 停在 C 上，回不到 F
    P(piano(ROOT[ch] + 12, 3.2), 61.0 + i * 3.0, 0.16, -0.2)
    for j, m in enumerate(CH[ch]):
        P(piano(m + 12, 3.0), 61.0 + i * 3.0 + j * B, 0.1, 0.15)
P(pad([48, 55, 58, 62], 4.5, att=1.5, rel=1.5, bright=0.8), 64.0, 0.12)

# ================================================================ 报复性地找答案 68–74.3：又急又快
F0 = 68.0
S = 0.1875
for i in range(int(6.3 / S)):
    t0 = F0 + i * S
    ch = ["Dm", "Bb", "C", "Am"][int(i * S / 1.5) % 4]
    P(pluck(ARP[ch][i % 4] + 12, length=0.5, bright=0.3), t0, 0.12, 0.2 if i % 2 else -0.2)
    if i % 2 == 0:
        P(kick(0.6), t0, 0.16 if i % 4 == 0 else 0.08)
    else:
        P(shaker(), t0, 0.07, 0.3)
    if i % 8 == 0:
        P(bass(ROOT[ch] + 12, 1.4), t0, 0.22)
P(swell(1.5, 400, 6000), F0 + 0.75, 0.15)                           # 日出
for k in range(3):                                                  # 签掉出来
    P(tick(k % 2 == 1), F0 + 2.1 + 0.375 + k * 0.375, 0.2)
P(noise(2.0, 150, 2000, 0.25, 0.4), F0 + 4.2, 1.0)                  # 浪把喊声吞掉
P(rumble(2.8) * 0.5, 74.3, 1.0)                                     # 戛然而止：车上睡着了
P(pad([38, 45], 2.6, att=0.6, rel=1.0, bright=0.6), 74.3, 0.1)

# ================================================================ 月亮升起 77–84：第一次有旋律
P(pad(CH["F"] + [65], 7.0, att=2.0, rel=3.0, bright=1.1), 77.0, 0.2)
P(swell(3.0, 300, 5000), 78.2, 0.14)
melody(78.5, THEME_MAJ, B, "piano", 0.32, shift=-12)
for i, ch in enumerate(("F", "C")):
    P(piano(ROOT[ch] + 12, BAR * 0.9), 78.5 + i * BAR, 0.14, -0.2)
for i, m in enumerate((84, 88, 91, 96)):                            # 变成月亮
    P(music_box(m, 2.0), 80.75 + i * 0.375, 0.12, -0.3 + i * 0.2)

# ================================================================ 遗憾、奇怪的位置、说不清的话 84–95
for i, ch in enumerate(["Dm", "Bb", "F", "C"]):
    t0 = 84.5 + i * BAR
    P(piano(ROOT[ch] + 12, BAR * 0.9), t0, 0.14, -0.2)
    for j, k in enumerate((0, 1, 2, 1)):
        P(piano(CH[ch][k] + 12, B * 0.9), t0 + j * B, 0.09, 0.1)
melody(84.5, THEME_MIN, B * 1.25, "piano", 0.2, shift=-12)
P(knock(), 85.4, 0.1)                                               # 杯子放回桌上
P(scratch(0.5), 92.0, 0.15)                                         # 揉成一团
P(knock(), 92.7, 0.08)                                              # 丢进纸篓
for k in range(7):                                                  # 一个一个删掉
    P(tick(), 93.35 + k * 0.1875, 0.05)

# ================================================================ 悬在那里 95–102：八音盒
for i, m in enumerate((77, 81, 84, 81, 79, 76, 77, 72)):
    P(music_box(m + 12, 2.0), 95.3 + i * B, 0.12, -0.3 + (i % 4) * 0.2)
P(pad(CH["F"], 7.0, att=2.0, rel=2.0, bright=1.2), 95.0, 0.16)
P(tick(), 97.6, 0.25)                                               # 关灯
P(swell(1.2, 600, 7000), 98.4, 0.12)                                # 天亮了
P(knock(), 100.2, 0.1)                                              # 推门出去

# ================================================================ 还是得吃饭，睡觉，工作，赶车 102–107：轻快的节拍
D0 = 102.0
E = 0.3125                                                          # 本段一拍 = 0.625 秒，八分音符 = 0.3125
for i in range(16):
    t0 = D0 + i * E
    if i % 2 == 0:
        P(kick(0.6), t0, 0.2)
    P(shaker(), t0 + E / 2, 0.07, 0.3)
for i, ch in enumerate(["F", "C", "Dm", "Bb"]):
    arp(D0 + i * 1.25, ch, 0.12, E, pattern=(0, 1, 2, 3))
    P(bass(ROOT[ch] + 12, 1.1), D0 + i * 1.25, 0.2)
for k in range(8):                                                  # 闹钟
    P(jingle(), D0 + 1.25 + k * E / 2, 0.08, 0.4)
for k in range(6):                                                  # 敲键盘
    P(tick(k % 2 == 1), D0 + 2.5 + k * E / 2, 0.08, -0.3)
P(swish(0.5), D0 + 4.375, 0.3)                                      # 车门

# ================================================================ 好看的云 107–114：旋律完整出现，吉他加进来
for i, ch in enumerate(["F", "C", "Dm", "Bb"]):
    t0 = 107.0 + i * 1.75
    arp(t0, ch, 0.12, 0.21875)
    P(bass(ROOT[ch] + 12, 1.6), t0, 0.18)
P(swell(3.0, 300, 6000), 108.4, 0.16)
P(pad(CH["F"] + [72], 8.0, att=2.0, rel=2.0, bright=1.4), 108.4, 0.2)
melody(108.75, THEME_MAJ, 0.4375, "piano", 0.34, shift=-12)

# ================================================================ 一顿饭、一阵风、一次谈话 114–124
for i, ch in enumerate(["F", "C", "Dm", "Bb", "F", "C"]):
    t0 = 114.0 + i * 1.75
    arp(t0, ch, 0.12, 0.21875)
    P(bass(ROOT[ch] + 12, 1.6), t0, 0.18)
    P(kick(0.5), t0, 0.1)
    P(kick(0.5), t0 + 0.875, 0.06)
melody(114.0, THEME_MAJ, 0.4375, "pluck", 0.3, shift=-12)
P(noise(1.4, 300, 1800, 0.25, 0.4), 115.6, 1.0, -0.3)               # 一阵风
P(snap(), 117.2, 0.15)                                              # 一起笑起来
melody(118.0, THEME_MAJ, 0.5, "piano", 0.3, shift=-12)
for k in range(4):                                                  # 路灯一盏盏亮起来
    P(music_box([84, 88, 91, 96][k], 1.6), 119.25 + k * B, 0.12, -0.4 + k * 0.25)
P(pad(CH["F"] + [72], 6.0, att=2.0, rel=3.0, bright=1.3), 118.6, 0.2)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.0), 122.4 + i * 0.07, 0.2, -0.3 + i * 0.2)

# ================================================================ 片尾 124–130
P(swish(), 125.6, 0.4)
melody(124.4, THEME_MAJ, 0.6, "box", 0.24, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.0), 124.4, 0.35)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 127.8 + i * 0.07, 0.24, pan=-0.3 + i * 0.2)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.9), (6, 1.0), (30, 1.0), (32, 1.6), (61, 1.5), (67.5, 1.4), (68, 1.0), (74.3, 1.1), (77, 1.15), (84, 1.3),
        (91, 1.5), (102, 1.15), (104, 1.25), (108, 1.0), (124, 0.7), (DUR + 1, 0.7)])
duck = [(0, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 130, 4)))

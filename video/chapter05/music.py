"""第五章 · 同路人 —— 配乐（纯代码合成）。

全章一个速度：每拍 0.5 秒，一小节 4 拍 = 2 秒。
种子相遇（吉他 + 八音盒）→ 一路遇见（轻轻的扫弦、沙锤）→ 一起骑车喝酒桌游爬山追落日（手鼓 + 吉他 + 簧片旋律，最热闹）
→ 托住落日（慢下来）→ 屋顶夜聊（只剩吉他，光点是八音盒）→ 一天天过去 → 分别（吉他独奏）→ 空镜（长音、风）
→ 阁楼的雨 → 光点回来（八音盒慢慢进来，回忆里的声音一个个响起）→ 合上手
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
from synth import (SR, Mix, bass, jingle, kick, knock, music_box, pad, pluck, rain, reed, rumble, scratch, shaker,  # noqa: E402
                   snap, swell, swish, thump, tick, _t)

DUR = 192.0
M = Mix(DUR)
B = 0.5
BAR = 2.0


def P(sig, t, vol=1.0, pan=0.0):
    M.place(sig, t, vol, pan)


THEME_MAJ = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 79, 2)]
CH = {"F": [53, 57, 60], "C": [48, 55, 64], "Dm": [50, 57, 62], "Bb": [46, 53, 58], "Am": [45, 52, 57]}
ROOT = {"F": 41, "C": 36, "Dm": 38, "Bb": 34, "Am": 45}
ARP = {"F": [53, 57, 60, 65], "C": [48, 55, 60, 64], "Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62], "Am": [45, 52, 57, 60]}
PROG = ["F", "C", "Dm", "Bb"]


def melody(t0, notes, beat, inst="pluck", vol=1.0, shift=0, pan=0.0):
    for b, m, d in notes:
        t = t0 + b * beat
        if inst == "box":
            P(music_box(m + shift), t, vol, pan)
        elif inst == "reed":
            P(reed(m + shift, d * beat * 0.95), t, vol, pan)
        else:
            P(pluck(m + shift, length=max(0.7, d * beat * 1.6), bright=0.22), t, vol, pan)


def arp(t0, ch, vol, pan=0.1, pattern=(0, 1, 2, 3, 2, 1, 2, 3)):
    step = BAR / len(pattern)
    for j, k in enumerate(pattern):
        P(pluck(ARP[ch][k] + 12, length=1.0, bright=0.24), t0 + j * step, vol, pan)


def strum(t0, ch, vol, down=True):
    notes = ARP[ch] + [ARP[ch][1] + 12]
    for j, m in enumerate(notes if down else notes[::-1]):
        P(pluck(m + 12, length=1.2, bright=0.28), t0 + j * 0.018, vol, -0.2 + j * 0.1)


def noise(length, lo, hi, vol, fade=0.3):
    from scipy.signal import butter, sosfilt
    n, t = _t(length)
    s = sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), np.random.randn(n))
    env = np.clip(t / fade, 0, 1) * np.clip((length - t) / fade, 0, 1)
    return s * env * vol


def bell(t0, vol=0.2):                                             # 自行车铃
    for k in range(2):
        P(music_box(100, 0.6), t0 + k * 0.14, vol)
        P(music_box(104, 0.6), t0 + k * 0.14 + 0.02, vol * 0.6)


def clink(t0, vol=0.3):
    P(music_box(103, 0.8), t0, vol)
    P(music_box(108, 0.6), t0 + 0.03, vol * 0.7)
    P(snap(), t0, vol * 0.4)


def waves(length, vol=0.12):
    n, t = _t(length)
    return noise(length, 150, 2500, 1.0, 1.0) * (0.4 + 0.6 * np.sin(2 * np.pi * 0.2 * t) ** 2) * vol


def murmur(length, vol=0.05):
    n, t = _t(length)
    return noise(length, 300, 2500, 1.0, 0.6) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 3.1 * t))) * vol


# ================================================================ 片头 0–6
melody(0.4, THEME_MAJ, 0.7, "box", 0.2, pan=0.1)
P(pad(CH["F"], 4.5, att=1.5), 0.6, 0.3)
for t0 in (2.1, 2.55, 3.0):
    P(swish(), t0, 0.5)

# ================================================================ 种子相遇 6–12
for i, ch in enumerate(["F", "C", "Dm"]):
    arp(6.0 + i * BAR, ch, 0.13)
for i, m in enumerate((84, 88, 91)):                                # 一颗、两颗、三颗
    P(music_box(m, 1.6), 7.1 + i * 1.0, 0.2, -0.4 + i * 0.4)
P(pad(CH["F"] + [72], 6.0, att=2.0, rel=2.0, bright=1.4), 6.0, 0.18)

# ================================================================ 一路遇见 12–27
for i in range(7):
    ch = PROG[i % 4]
    t0 = 12.0 + i * BAR
    strum(t0, ch, 0.12)
    strum(t0 + 1.0, ch, 0.08, down=False)
    P(bass(ROOT[ch] + 12, BAR * 0.9), t0, 0.18)
    for j in range(4):
        P(shaker(), t0 + j * B + B / 2, 0.08, pan=0.3)
for k in range(10):
    P(knock(), 12.2 + k * B, 0.035, pan=-0.2)                       # 脚步
P(scratch(0.4), 14.6, 0.15)                                         # 摊开地图
for i, m in enumerate((79, 84)):
    P(music_box(m, 1.4), 16.4 + i * 0.4, 0.18)                      # 岔路上走来的两个人
melody(19.0, THEME_MAJ, B, "pluck", 0.3, shift=-12, pan=0.1)
for i, tk in enumerate((20.6, 21.9, 23.2, 24.5)):                   # 小路一条条汇进大路
    P(music_box([77, 81, 84, 89][i], 1.4), tk, 0.14, -0.3 + i * 0.2)

# ================================================================ 一起骑车、喝酒、桌游、爬山、追落日 27–42：最热闹
for i in range(int(15 / B)):
    t0 = 27.0 + i * B
    if i % 2 == 0:
        P(kick(0.7), t0, 0.24)
    P(jingle(), t0 + B / 2, 0.08 if i % 4 else 0.13, pan=0.4)
for i in range(8):
    ch = PROG[i % 4]
    t0 = 27.0 + i * BAR
    if t0 >= 42.0:
        break
    arp(t0, ch, 0.13)
    P(bass(ROOT[ch] + 12, BAR * 0.9), t0, 0.24)
melody(27.0, THEME_MAJ, B, "reed", 0.42, shift=-12)
melody(31.0, THEME_MAJ, B, "reed", 0.38, shift=-12)
melody(35.0, THEME_MAJ, B, "pluck", 0.35, shift=-12)
bell(28.0)
clink(31.0)
for k in range(8):
    P(tick(k % 2 == 1), 33.1 + k * 0.14, 0.12)                     # 骰子
P(thump(), 37.0, 0.25)                                              # 拉上来
P(waves(3.2, 0.1), 39.0, 1.0)
for k in range(6):
    P(noise(0.25, 1500, 6000, 0.12, 0.05), 39.4 + k * B, 1.0, 0.3)   # 踩着浪花

# ================================================================ 托住落日 42–52：慢下来
for i, ch in enumerate(["F", "C", "Dm", "Bb", "F"]):
    t0 = 42.0 + i * BAR
    arp(t0, ch, 0.12 - 0.012 * i)
    P(bass(ROOT[ch] + 12, BAR * 0.9), t0, 0.18)
for i in range(int(5 / B)):
    if i % 2 == 0:
        P(kick(0.6), 42.0 + i * B, 0.14 * (1 - i / 10))
melody(42.0, THEME_MAJ, B * 1.5, "pluck", 0.3, shift=-12)
P(pad(CH["F"] + [72], 8.0, att=2.0, rel=3.0, bright=1.2), 44.0, 0.22)
P(waves(10.0, 0.08), 42.0, 1.0)

# ================================================================ 屋顶夜聊 52–64：只剩吉他，光点是八音盒
for i, ch in enumerate(["F", "Am", "Bb", "C", "F", "Dm"]):
    arp(52.0 + i * BAR, ch, 0.11, pattern=(0, 1, 2, 1))
P(pad([53, 60, 65], 12.0, att=2.0, rel=2.0, bright=1.0), 52.0, 0.14)
for k in range(12):                                                 # 话变成的小光点
    P(music_box([84, 88, 91, 96, 93, 89][k % 6], 1.2), 58.0 + k * B, 0.07, -0.5 + (k % 5) * 0.25)

# ================================================================ 一天、两天、三天 64–70
for k in range(3):
    P(swell(1.6, 300, 4000), 64.0 + k * 2.0, 0.2)
    P(pluck(72 + k * 2, length=1.6), 64.6 + k * 2.0, 0.18)
for i, ch in enumerate(["F", "C", "Dm"]):
    arp(64.0 + i * BAR, ch, 0.1)

# ================================================================ 分别 70–111：吉他独奏
for i, ch in enumerate(["F", "C", "Dm", "Bb", "F", "C", "Bb", "C", "F", "Am", "Dm", "C", "Bb", "F", "C", "F", "Dm",
                        "Bb", "C", "F"]):
    t0 = 70.0 + i * BAR
    arp(t0, ch, 0.15, pattern=(0, 1, 2, 3))
melody(72.0, THEME_MAJ, B * 2, "pluck", 0.26, shift=-12)
P(noise(5.0, 300, 1600, 0.12, 1.0), 78.0, 1.0)                      # 风把种子吹散
for i, m in enumerate((96, 93, 89, 84)):
    P(music_box(m, 1.6), 78.6 + i * 0.6, 0.14, -0.6 + i * 0.4)
P(music_box(91, 1.6), 85.0, 0.14)                                   # 笑着点点头
for k in range(16):                                                 # 耳机里的歌
    P(pluck([77, 81, 84, 81][k % 4], length=0.4, bright=0.3), 89.2 + k * B / 2, 0.16, 0.5)
P(rumble(2.4), 92.4, 0.2)                                           # 公交车进站
P(swish(0.6), 93.8, 0.25)                                           # 开门
P(rumble(2.0), 96.4, 0.15)
P(noise(1.0, 400, 2500, 0.2, 0.3), 100.0, 1.0)                      # 一吹
P(swell(2.4, 400, 7000), 100.2, 0.25)
for i, m in enumerate((84, 88, 91, 96)):
    P(music_box(m, 1.6), 100.4 + i * 0.25, 0.14, -0.3 + i * 0.2)
for k in range(5):
    P(knock(), 104.2 + k * B, 0.05)                                 # 上车
P(thump(), 108.9, 0.3)                                              # 车门关上
P(rumble(2.4), 109.6, 0.25)                                         # 火车开走

# ================================================================ 空镜 111–131：长音、风
P(pad([41, 48, 57], 20.0, att=3.0, rel=3.0, bright=0.8), 111.0, 0.2)
P(noise(20.0, 300, 1500, 0.08, 2.0), 111.0, 1.0)
for i, m in enumerate((65, 64, 62, 60, 57, 60)):
    P(pluck(m, length=2.6, bright=0.16), 111.4 + i * 3.0, 0.22)
P(music_box(91, 2.0), 129.0, 0.1)

# ================================================================ 变回陌生人 131–138
P(murmur(7.0, 0.07), 131.0, 1.0)
for k in range(14):
    P(knock(), 131.2 + k * B, 0.03, pan=(-0.4 if k % 2 else 0.4))
P(pluck(69, length=3.0, bright=0.16), 133.8, 0.22)                  # 擦肩、回头
P(pluck(64, length=3.0, bright=0.16), 135.0, 0.18)

# ================================================================ 阁楼的雨 138–147.5
P(rain(9.5) * 0.25, 138.0, 1.0)
P(pad([45, 52, 57], 9.0, att=2.0, rel=2.0, bright=0.6), 138.0, 0.16)
P(tick(), 145.4, 0.3)                                               # 关灯

# ================================================================ 光点回来 147.5–186
P(rain(38.0) * 0.18, 147.5, 1.0)
for k in range(14):
    P(music_box([84, 88, 91, 96, 93, 89, 86][k % 7], 1.6), 148.0 + k * 0.5, 0.08, -0.6 + (k % 7) * 0.2)
for i, ch in enumerate(["F", "C", "Dm", "Bb"] * 4):
    t0 = 155.0 + i * BAR
    if t0 > 175:
        break
    arp(t0, ch, 0.09, pattern=(0, 1, 2, 1))
melody(155.0, THEME_MAJ, B * 1.5, "box", 0.22, pan=0.1)
melody(165.0, THEME_MAJ, B * 1.5, "box", 0.2, pan=-0.1)
P(pad(CH["F"] + [72], 20.0, att=3.0, rel=3.0, bright=1.4), 155.0, 0.16)
bell(158.6, 0.12)                                                   # 回忆里的声音
P(murmur(2.0, 0.04), 161.7, 1.0)
clink(162.4, 0.15)
for k in range(6):
    P(tick(), 165.0 + k * 0.16, 0.06)
P(waves(3.0, 0.08), 168.2, 1.0)
for k in range(5):
    P(noise(0.25, 1500, 6000, 0.08, 0.05), 171.6 + k * B, 1.0, 0.3)
for i, m in enumerate((96, 93, 89, 86, 84)):                        # 光点飞出天窗
    P(music_box(m, 1.6), 175.4 + i * 0.6, 0.1)
melody(180.0, THEME_MAJ, 0.7, "box", 0.28)
P(pad(CH["F"] + [72], 6.0, att=1.5, rel=3.0, bright=1.2), 180.0, 0.2)
for i, m in enumerate((65, 69, 72, 77)):                            # 合上手
    P(music_box(m, 3.0), 183.0 + i * 0.07, 0.25, pan=-0.3 + i * 0.2)

# ================================================================ 片尾 186–192
P(swish(), 187.6, 0.4)
melody(186.4, THEME_MAJ, 0.6, "box", 0.24, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.0), 186.4, 0.35)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 189.8 + i * 0.07, 0.24, pan=-0.3 + i * 0.2)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.85), (6, 1.0), (52, 1.15), (70, 1.15), (84, 1.5), (100, 1.2), (104, 1.5), (111, 1.35), (131, 1.4), (150, 1.25), (156, 1.0), (172, 1.3), (180, 0.9), (186, 0.6), (DUR + 1, 0.6)])
M.muffle([(0, 0), (89.0, 0), (89.2, 0.7), (93.6, 0.7), (93.9, 0), (DUR + 1, 0)])
duck = [(0, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 192, 4)))

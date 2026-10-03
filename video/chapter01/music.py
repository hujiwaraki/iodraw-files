"""第一章 · 出逃（第二版）—— 配乐（纯代码合成）。

八音盒主题 → 灰色小调与雨 → 杯裂、低语、震动 → 潮水 → 蹦迪鼓点骤停、耳鸣 → 火车与飞机远去
→ 滴答、水下、心跳 → 停顿里的一声八音盒 → “叮”地惊醒、锚点一个个响起 → 风、浪、驼铃、鸟鸣
→ 解开根的拨弦 → 书里梦一样的远方 → 开门，主题绽放 → 八音盒收尾
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
from synth import (SR, Mix, bandnoise, bass, buzz, cello, chug, heartbeat, jingle, kick, knock, music_box, pad,  # noqa: E402
                   piano, pluck, rain, reed, rumble, scratch, shaker, snap, swell, swish, thump, tick, whistle, _t)

DUR = 112.0
M = Mix(DUR)
P = M.place

THEME_MAJ = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 79, 2)]
THEME_MIN = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 74, 2)]
CH = {"F": [57, 60, 65], "C": [55, 60, 64], "Dm": [57, 62, 65], "Bb": [58, 62, 65], "Gm": [55, 58, 62], "A": [57, 61, 64]}
ROOT = {"F": 41, "C": 36, "Dm": 38, "Bb": 34, "Gm": 43, "A": 45}
ARP = {"F": [53, 57, 60, 65], "C": [48, 55, 60, 64], "Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62],
       "Gm": [43, 50, 55, 58], "A": [45, 52, 57, 61]}


def melody(t0, notes, beat, inst="box", vol=1.0, shift=0, pan=0.0):
    for b, m, d in notes:
        t = t0 + b * beat
        if inst == "box":
            P(music_box(m + shift), t, vol, pan)
        elif inst == "piano":
            P(piano(m + shift, d * beat), t, vol, pan)
        elif inst == "reed":
            P(reed(m + shift, d * beat * 0.95), t, vol, pan)
        elif inst == "pluck":
            P(pluck(m + shift), t, vol, pan)


def whisper(length):
    n, t = _t(length)
    from scipy.signal import butter, sosfilt
    s = sosfilt(butter(2, [1500, 6000], btype="band", fs=SR, output="sos"), np.random.randn(n))
    am = np.clip(np.sin(2 * np.pi * 7 * t + 3 * np.sin(2 * np.pi * 1.7 * t)), 0, 1) ** 2
    return s * am * 0.05


def tinnitus(length):
    n, t = _t(length)
    return np.sin(2 * np.pi * 5800 * t) * 0.012 * np.clip(t / 0.05, 0, 1) * np.exp(-t / (length / 2.5))


def roar(length):
    n, t = _t(length)
    from scipy.signal import butter, sosfilt
    s = sosfilt(butter(2, [80, 2000], btype="band", fs=SR, output="sos"), np.random.randn(n))
    return s * np.sin(np.pi * t / length) ** 1.5 * 0.25


def wind(length):
    n, t = _t(length)
    from scipy.signal import butter, sosfilt
    s = sosfilt(butter(2, [300, 1600], btype="band", fs=SR, output="sos"), np.random.randn(n))
    return s * np.sin(np.pi * t / length) ** 2 * (1 + 0.4 * np.sin(2 * np.pi * 0.8 * t)) * 0.12


def wave_sound(length):
    n, t = _t(length)
    from scipy.signal import butter, sosfilt
    s = sosfilt(butter(2, [200, 3000], btype="band", fs=SR, output="sos"), np.random.randn(n))
    return s * (np.sin(np.pi * t / length) ** 3) * 0.2


def bird(t0):
    for k in range(3):
        n, t = _t(0.12)
        f = 3200 + 1200 * np.sin(np.pi * t / 0.12)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.12) * 0.12
        P(s, t0 + k * 0.16, 0.8, pan=0.5)


def camel_bell(t0):
    for k in range(3):
        n, t = _t(0.8)
        s = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((620, 1), (1580, 0.5), (2710, 0.3))) * np.exp(-t / 0.25) * 0.12
        P(s, t0 + k * 0.32, 0.8, pan=-0.3)


def chime(t0, vol=0.5):
    P(music_box(76, 2.0), t0, vol * 0.8)
    P(music_box(72, 2.0), t0 + 0.4, vol * 0.8)


# ================================================================ 片头 0–6
melody(0.4, THEME_MAJ, 0.7, "box", 0.8, pan=0.1)
P(pad(CH["F"], 4.5, att=1.5), 0.6, 0.35)
for t0 in (2.1, 2.55, 3.0):
    P(swish(), t0, 0.5)

# ================================================================ 这片土地 6–32
P(rain(26.5), 5.5, 1.0)
P(pad([50, 57, 62], 25.0, att=3.0, rel=2.0, bright=2.2), 6.0, 0.55)
P(cello(38, 8.0, att=1.5), 6.2, 0.55)
melody(6.6, THEME_MIN, 0.9, "piano", 0.45, shift=-12, pan=-0.1)
P(knock(), 10.4, 0.25)                                   # 椅子
for k in range(4):                                        # 离开的脚步
    P(knock(), 10.9 + k * 0.38, 0.12, pan=0.4 + k * 0.1)
P(snap(), 13.1, 0.5)                                      # 杯子裂开
P(music_box(98, 1.0), 13.1, 0.4)
P(piano(62, 2.0), 13.3, 0.3)
for k in range(10):                                       # 越来越密的低语
    P(whisper(1.6), 14.2 + k * 0.45, 0.6 + 0.08 * k, pan=-0.6 + (k % 3) * 0.6)
P(rumble(4.0), 15.0, 0.4)
for k in range(3):                                        # 手机震动
    P(buzz(), 19.3 + k * 0.9, 0.9, pan=0.2)
P(knock(), 22.0, 0.4)                                     # 扣下手机
P(rumble(6.0), 22.8, 0.8)                                 # 潮水
P(cello(38, 4.5, att=1.2), 23.1, 0.65)
P(cello(45, 4.5, att=1.2), 23.1, 0.35)
melody(23.4, THEME_MIN[:5], 0.9, "piano", 0.4, shift=-12)
P(rumble(4.5), 27.8, 1.0)
P(cello(33, 4.5, att=1.0), 28.0, 0.75)
P(thump(), 31.1, 0.5)                                     # 被根拉回去

# ================================================================ 填不满的日子 32–43（蹦迪 → 断电）
beat = 60 / 124
t = 32.0
STOP = 38.25
while t < STOP - 0.01:
    k = int(round((t - 32.0) / beat))
    P(kick(1.0), t, 0.85)
    P(shaker(), t + beat / 2, 0.45, pan=0.3)
    if k % 2 == 1:
        P(snap(), t, 0.55, pan=-0.1)
    chn = ["Dm", "Dm", "Bb", "C"][(k // 4) % 4]
    P(bass(ROOT[chn] + 12, beat * 0.45), t + beat / 2, 0.7)
    if k % 4 == 0:
        P(pad(CH[chn], beat * 3.5, att=0.02, rel=0.1, bright=1.0), t, 0.55)
    t += beat
for tc in (34.2, 36.2):
    P(swell(0.4), tc - 0.4, 0.8)
for k in range(6):                                        # 碰杯
    P(music_box(100, 0.5), 36.3 + k * 0.333, 0.25, pan=0.2)
P(thump(), STOP, 0.5)
P(tinnitus(4.5), 38.3, 1.0)
P(cello(38, 4.5, att=1.5), 38.6, 0.35)

# ================================================================ 想走却没走 43–51
for i, chn in enumerate(["Dm", "Bb", "F", "A"]):
    t0 = 43.0 + i * 2.0
    P(piano(ROOT[chn] + 12, 1.9), t0, 0.4)
    for j, m in enumerate(ARP[chn]):
        P(piano(m + 12, 0.45), t0 + j * 0.5, 0.2, pan=-0.25)
melody(43.0, THEME_MIN, 0.95, "piano", 0.38, shift=-12, pan=0.1)
P(rumble(1.4), 43.2, 0.9)
for k in range(8):
    P(chug(), 43.3 + k * 0.16, 0.2, pan=0.5 - k * 0.1)
P(rumble(1.6), 45.6, 0.9)
for k in range(8):
    P(chug(), 45.6 + k * 0.2, 0.18, pan=-0.5 - k * 0.05)
chime(47.2, 0.45)                                         # 机场广播
P(roar(3.2), 48.6, 0.9)                                   # 飞机起飞远去

# ================================================================ 被吞没 51–59
for k in range(int((56.0 - 51.0) / 0.5)):
    P(tick(k % 2 == 1), 51.0 + k * 0.5, 0.4, pan=0.25)
P(cello(34, 5.5, att=1.5), 51.0, 0.55)
P(pad([50, 57, 62], 5.0, att=2.0), 51.0, 0.45)
P(rumble(5.0), 51.0, 0.5)
for k, t0 in enumerate((53.0, 53.9, 54.8, 55.7, 56.7, 57.8)):    # 心跳越来越慢
    P(heartbeat(), t0, 0.32 + 0.03 * k)
P(music_box(81, 2.5), 57.6, 0.18, pan=-0.5)               # 远处的一声八音盒

# ================================================================ 为什么不是现在 59–73
P(snap(), 58.95, 0.5)
for m in (89, 96):
    P(music_box(m, 3.0), 59.0, 0.75)
P(pad(CH["F"] + [72], 11.5, att=1.5, rel=2.0), 59.2, 0.55)
melody(59.8, THEME_MAJ, 0.7, "box", 0.45, pan=0.15)
for i in range(11):                                       # 锚点一个个亮起
    P(music_box([77, 79, 81, 84, 86, 89, 91, 93, 96, 98, 101][i], 1.2), 59.6 + i * 0.29, 0.28, pan=-0.6 + i * 0.12)
for t0, chn in ((59.2, "F"), (61.6, "C"), (64.0, "Dm"), (66.4, "Bb"), (68.8, "C")):
    P(piano(ROOT[chn] + 12, 2.3), t0, 0.35)
P(wind(1.6), 64.8, 1.0, pan=-0.4)                         # 雪山
P(wave_sound(1.6), 65.35, 1.0, pan=0.4)                   # 大海
camel_bell(65.9)                                          # 沙漠
bird(66.45)                                               # 雨林
for i, m in enumerate((65, 69, 72, 77)):
    P(pluck(m + 12), 64.9 + i * 0.55, 0.4, pan=-0.5 + i * 0.33)
P(pluck(84), 68.6, 0.45)                                  # 对吗？
P(pluck(79), 68.9, 0.45)
for i, m in enumerate((77, 81, 84, 89, 93)):              # 帽子飞到头上
    P(music_box(m, 1.6), 70.2 + i * 0.13, 0.45, pan=0.5 - i * 0.2)

# ================================================================ 出逃 73–77
b2 = 0.6
for k in range(int((77.0 - 73.0) / (b2 / 2))):
    t0 = 73.0 + k * b2 / 2
    chn = ["F", "C", "Dm", "Bb"][int((t0 - 73.0) / 2.4) % 4]
    P(pluck(ARP[chn][k % 4] + 12), t0, 0.3 + 0.1 * (t0 - 73.0) / 4, pan=-0.35)
for i, m in enumerate((72, 74, 77, 79, 81, 84)):          # 每解开一根
    P(music_box(m, 1.6), 73.3 + i * 0.36, 0.45, pan=-0.3 + i * 0.12)
P(rumble(0.8), 76.0, 0.4)                                 # 拉出行李箱

# ================================================================ 书里的想象 77–101（梦一样，隔着一层纱）
P(pad(CH["F"] + [72], 23.0, att=2.0, rel=3.0, bright=2.0), 77.0, 0.5)
P(swish(1.2), 77.0, 0.6)
for k, (t0, m) in enumerate(((77.0, 84), (77.18, 88), (77.36, 91), (77.6, 96))):   # 气泡一个个冒出来
    P(pluck(m, length=0.4, bright=0.1), t0, 0.35, pan=-0.3 + k * 0.2)
P(wind(2.2), 77.2, 0.5)
P(whistle(1.0), 79.6, 0.35, pan=-0.5)
for k in range(8):
    P(chug(), 79.6 + k * 0.17, 0.08)
dream = 0.75
for i, chn in enumerate(["F", "C", "Dm", "Bb", "F", "C", "Bb", "C"]):
    t0 = 77.0 + i * 2.4
    for j, m in enumerate(ARP[chn]):
        P(pluck(m + 12, bright=0.2), t0 + j * 0.6, 0.18, pan=-0.3)
        P(pluck(m + 24, bright=0.15), t0 + j * 0.6 + 0.3, 0.1, pan=0.3)
    P(bass(ROOT[chn] + 12, 2.2), t0, 0.3)
for k in range(9):                                        # 灯笼下转圈：轻手鼓
    P(jingle(), 82.0 + k * 0.6, 0.25, pan=0.3)
melody(82.0, THEME_MAJ, dream, "reed", 0.4, shift=-12, pan=0.1)
P(wave_sound(2.0), 86.4, 0.4)                             # 划船的水声
melody(88.6, THEME_MAJ[:5], dream, "box", 0.4, pan=-0.1)
P(knock(), 93.6, 0.35)                                    # 工牌落在桌上
P(scratch(1.2), 96.2, 0.5)
P(scratch(1.2), 97.4, 0.55)
P(swell(1.6, 400, 8000), 98.6, 0.9)
P(pad(CH["F"] + [72, 77], 4.0, att=1.0, rel=2.0), 99.0, 0.8)
melody(99.0, THEME_MAJ[:5], 0.4, "box", 0.5, pan=0.1)

# ================================================================ 推门 101–106
P(swish(0.9), 101.0, 0.7)
P(pluck(96, length=0.4, bright=0.1), 101.0, 0.4)
P(swell(1.8), 101.2, 1.1)
P(pad(CH["F"] + [72, 77], 3.8, att=0.4, rel=3.0), 102.9, 1.4)
melody(103.0, THEME_MAJ, 0.38, "box", 0.85, pan=0.1)
melody(103.0, THEME_MAJ, 0.38, "piano", 0.5, shift=-12)
P(bass(41, 2.4), 103.0, 0.6)
P(kick(0.8), 103.0, 0.7)
for k in range(10):                                       # 行李箱轮子
    P(chug(0.1), 103.8 + k * 0.2, 0.12)

# ================================================================ 片尾 106–112
P(swish(), 107.6, 0.7)
melody(106.4, THEME_MAJ, 0.6, "box", 0.7, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.0), 106.4, 0.55)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 110.2 + i * 0.07, 0.5, pan=-0.3 + i * 0.2)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.8), (6, 0.8), (6.5, 0.95), (13.5, 0.95), (14.5, 1.25), (22.5, 1.2), (23.5, 0.95), (31.8, 0.95), (32.0, 1.25), (38.2, 1.25), (38.3, 0.9), (51, 1.0),
        (58.9, 1.1), (59.0, 1.0), (76.5, 1.0), (77.5, 1.3), (98.5, 1.3), (100, 1.0), (102.8, 1.25), (106, 1.0), (DUR + 1, 1.0)])
M.muffle([(0, 0), (52.0, 0), (55.5, 0.9), (58.9, 0.9), (58.95, 0), (DUR + 1, 0)])
duck = [(0, 1), (38.2, 1), (38.3, 0.15), (38.8, 1), (58.85, 1), (58.95, 0.15), (59.1, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 112, 4)))

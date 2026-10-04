"""第二章 · 一个人 —— 配乐（纯代码合成）。

一把吉他（拨弦）独奏：匆忙的分解和弦 → 消息提示音 → 高原的风与经幡 → 快门 → 高原反应的呼吸与晕眩
→ 绷紧的红线 → 雨夜、小巷、电量提示 → 一个人的饭、海浪、城市 → 视线 → 月台 → 季节与钟
→ 沙漏与天平 → 老去的八音盒 → 心跳 → 出发 → 地图上一个个亮起的地方 → 八音盒收尾
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
from synth import (SR, Mix, bandnoise, bass, cello, chug, heartbeat, jingle, kick, knock, music_box, pad,  # noqa: E402
                   piano, pluck, rain, reed, rumble, scratch, shaker, snap, swell, swish, thump, tick, whistle, _t)

DUR = 130.5
M = Mix(DUR)
P = M.place

THEME_MAJ = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 79, 2)]
THEME_MIN = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 74, 2)]
CH = {"F": [57, 60, 65], "C": [55, 60, 64], "Dm": [57, 62, 65], "Bb": [58, 62, 65], "Gm": [55, 58, 62], "A": [57, 61, 64],
      "Am": [57, 60, 64]}
ROOT = {"F": 41, "C": 36, "Dm": 38, "Bb": 34, "Gm": 43, "A": 45, "Am": 45}
ARP = {"F": [53, 57, 60, 65], "C": [48, 55, 60, 64], "Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62],
       "Gm": [43, 50, 55, 58], "A": [45, 52, 57, 61], "Am": [45, 52, 57, 60]}


def melody(t0, notes, beat, inst="pluck", vol=1.0, shift=0, pan=0.0):
    for b, m, d in notes:
        t = t0 + b * beat
        if inst == "box":
            P(music_box(m + shift), t, vol, pan)
        elif inst == "piano":
            P(piano(m + shift, d * beat), t, vol, pan)
        elif inst == "reed":
            P(reed(m + shift, d * beat * 0.95), t, vol, pan)
        else:
            P(pluck(m + shift, length=max(0.6, d * beat * 1.4), bright=0.22), t, vol, pan)


def guitar(t0, chords, bar, vol=0.3, up=12, pattern=(0, 1, 2, 3, 2, 1), pan=-0.2):
    """吉他分解和弦：每小节一个和弦。"""
    step = bar / len(pattern)
    for i, ch in enumerate(chords):
        tb = t0 + i * bar
        P(pluck(ROOT[ch] + 12, length=bar * 1.2, bright=0.2), tb, vol * 1.1, pan)
        for j, k in enumerate(pattern):
            P(pluck(ARP[ch][k] + up, length=1.2, bright=0.24), tb + j * step, vol, pan + 0.3)


def soft_rain(t0, t1, vol=0.3):
    from scipy.signal import butter, sosfilt
    n, tt = _t(t1 - t0)
    sig = sosfilt(butter(2, 3200, btype="low", fs=SR, output="sos"), rain(t1 - t0))
    env = np.clip(tt / 0.8, 0, 1) * np.clip((t1 - t0 - tt) / 0.8, 0, 1)
    P(sig * env, t0, vol)


def wind(length, vol=0.12):
    n, t = _t(length)
    from scipy.signal import butter, sosfilt
    s = sosfilt(butter(2, [250, 1400], btype="band", fs=SR, output="sos"), np.random.randn(n))
    return s * np.sin(np.pi * t / length) ** 1.5 * (1 + 0.4 * np.sin(2 * np.pi * 0.5 * t)) * vol


def breath(length):
    """高原上又短又浅的呼吸。"""
    n, t = _t(length)
    from scipy.signal import butter, sosfilt
    s = sosfilt(butter(2, [400, 2500], btype="band", fs=SR, output="sos"), np.random.randn(n))
    env = np.clip(np.sin(2 * np.pi * 0.9 * t), 0, 1) ** 2
    return s * env * 0.07


def whisper(length):
    n, t = _t(length)
    from scipy.signal import butter, sosfilt
    s = sosfilt(butter(2, [1500, 6000], btype="band", fs=SR, output="sos"), np.random.randn(n))
    am = np.clip(np.sin(2 * np.pi * 7 * t + 3 * np.sin(2 * np.pi * 1.7 * t)), 0, 1) ** 2
    return s * am * 0.05


def wave_sound(length):
    n, t = _t(length)
    from scipy.signal import butter, sosfilt
    s = sosfilt(butter(2, [200, 3000], btype="band", fs=SR, output="sos"), np.random.randn(n))
    return s * (np.sin(np.pi * t / length) ** 3) * 0.2


def beep(f=1800, length=0.12):
    n, t = _t(length)
    return np.sin(2 * np.pi * f * t) * np.sin(np.pi * t / length) * 0.08


def sand(length):
    n, t = _t(length)
    from scipy.signal import butter, sosfilt
    s = sosfilt(butter(2, [3000, 9000], btype="band", fs=SR, output="sos"), np.random.randn(n))
    return s * np.clip(t / 0.3, 0, 1) * np.clip((length - t) / 0.3, 0, 1) * 0.03


# ================================================================ 片头 0–6：主题换成吉他
melody(0.4, THEME_MAJ, 0.7, "pluck", 0.55, shift=-12, pan=0.1)
P(pad(CH["F"], 4.5, att=1.5), 0.6, 0.3)
for t0 in (2.1, 2.55, 3.0):
    P(swish(), t0, 0.5)

# ================================================================ 只想逃离 6–11：匆忙的分解和弦 + 脚步
soft_rain(5.8, 11.2, 0.22)
guitar(6.0, ["Dm", "Bb", "C", "Dm"], 1.25, vol=0.26, pattern=(0, 1, 2, 3))
P(cello(38, 5.0, att=0.6), 6.0, 0.35)
for k in range(14):
    P(knock(), 6.2 + k * 0.34, 0.05, pan=-0.4 + k * 0.06)
for k in range(16):
    P(chug(0.08), 6.2 + k * 0.3, 0.05)

# ================================================================ 问了几个朋友 11–17.5
P(pad([50, 57, 62], 6.5, att=1.0, rel=1.0, bright=1.4), 11.0, 0.3)
for t0, m in ((11.3, 96), (12.1, 89), (12.8, 86), (13.5, 84)):     # 消息一条条冒出来
    P(music_box(m, 0.6), t0, 0.35, pan=0.2)
P(tick(), 14.0, 0.2)                                              # 已读
P(swish(0.5), 14.6, 0.5)                                          # 划到 App
P(knock(), 16.0, 0.3)                                             # 点下报名
for i, m in enumerate((84, 88, 91)):
    P(music_box(m, 1.2), 16.3 + i * 0.09, 0.35)
P(pluck(62, length=1.4), 15.4, 0.25)
P(pluck(57, length=1.4), 16.4, 0.25)

# ================================================================ 稻城亚丁 17.5–31.5：风、经幡、大巴
P(wind(14.0, 0.14), 17.4, 1.0, pan=-0.3)
P(rumble(5.5), 17.8, 0.35)                                        # 大巴爬坡
guitar(17.6, ["Am", "F", "C", "Am", "F", "C", "Am", "F", "C", "Am", "F"], 1.25, vol=0.22, pattern=(0, 2, 1, 3, 2, 1))
P(pad([57, 64, 69], 13.5, att=2.5, rel=2.0, bright=2.2), 17.6, 0.32)
for k in range(10):                                               # 经幡哗啦啦
    P(bandnoise(0.5, 1500, 6000, 0.12) * 0.25, 23.6 + k * 0.8, 0.5, pan=-0.6 + k * 0.12)
for k in range(6):                                                # 情侣头顶的小爱心
    P(music_box([93, 96, 98][k % 3], 0.6), 24.0 + k * 0.6, 0.12, pan=-0.5 + (k % 2))
P(snap(), 26.9, 0.5)                                              # 快门
P(snap(), 29.4, 0.45)
P(cello(36, 3.0, att=1.0), 29.3, 0.4)                             # 视线落下来
P(whisper(2.2), 29.4, 0.6, pan=-0.4)
P(whisper(2.2), 29.6, 0.6, pan=0.4)

# ================================================================ 高原反应 31.5–37.5
for k in range(6):
    P(breath(1.2), 31.6 + k * 1.0, 0.9)
P(swell(2.0, 300, 3000), 31.8, 0.4)
P(pad([45, 52, 57], 6.0, att=1.5, rel=1.0, bright=1.0), 31.5, 0.35)
for t0, m in ((32.2, 69), (33.8, 65), (35.4, 64)):
    P(pluck(m, length=1.6, bright=0.18), t0, 0.28, pan=-0.2)
for k in range(5):                                                # 隔壁闷闷的笑声
    P(reed(72 + (k % 3) * 2, 0.18), 32.4 + k * 0.9, 0.08, pan=0.7)

# ================================================================ 说不清的事 37.5–44.5：绷紧的红线
P(wind(7.0, 0.1), 37.5, 1.0)
P(cello(41, 3.0, att=0.6), 39.0, 0.4)
for k in range(10):                                               # 越绷越紧
    P(pluck(76 + k % 2, length=0.3, bright=0.35), 39.1 + k * 0.17, 0.12 + 0.02 * k, pan=0.2)
P(knock(), 40.6, 0.35)                                            # 推回去
for i, m in enumerate((72, 69, 65)):                              # 松开、重新绷好
    P(pluck(m, length=1.6, bright=0.2), 41.6 + i * 0.4, 0.3)
P(music_box(89, 1.2), 42.2, 0.3)
for k in range(6):
    P(knock(), 42.8 + k * 0.28, 0.06, pan=0.5)

# ================================================================ 并不浪漫 44.5–54.5：雨夜、小巷
soft_rain(44.4, 50.0, 0.3)
for k in range(5):
    P(chug(0.1), 44.9 + k * 0.22, 0.12)                           # 轮子滚走
P(cello(38, 9.5, att=1.5), 44.6, 0.4)
melody(45.0, THEME_MIN[:5], 0.9, "pluck", 0.32, shift=-12)
for k in range(8):                                                # 小巷里的回声脚步
    P(knock(), 49.8 + k * 0.55, 0.12 * (0.6 + 0.4 * (k % 2)), pan=(-0.6 if k % 2 else 0.6))
for k in range(5):
    P(beep(1700), 50.4 + k * 0.8, 0.5)                            # 电量 3%
P(rumble(4.0), 50.0, 0.3)

# ================================================================ 一个人 54.5–64.5
guitar(54.5, ["Dm", "Bb", "F", "C", "Dm", "Bb", "F", "A"], 1.25, vol=0.2)
melody(54.6, THEME_MIN, 1.2, "pluck", 0.36, shift=-12, pan=0.1)
P(music_box(100, 0.4), 55.0, 0.12)                                # 勺子碰碗
P(whisper(1.6), 55.6, 0.5, pan=0.6)
P(wave_sound(3.0), 57.8, 0.6)
P(wave_sound(2.6), 59.8, 0.5)
P(rumble(3.4), 60.8, 0.35)                                        # 陌生城市的嘈杂
for k in range(6):
    P(knock(), 61.0 + k * 0.4, 0.05, pan=-0.6 + k * 0.24)

# ================================================================ 那些眼神 64.5–69.5
for k in range(14):
    P(tick(), 64.7 + k * 0.16, 0.08, pan=-0.7 + (k % 5) * 0.35)
for k in range(8):
    P(whisper(1.4), 64.8 + k * 0.45, 0.55 + 0.05 * k, pan=-0.6 + (k % 3) * 0.6)
P(swell(3.6, 200, 4000), 65.4, 0.6)
P(cello(36, 4.5, att=1.5), 64.6, 0.5)

# ================================================================ 月台 69.5–75.5
P(rumble(1.6), 69.5, 0.8)
for k in range(8):
    P(chug(), 69.6 + k * 0.16, 0.18, pan=0.5 - k * 0.1)
P(whistle(0.8), 70.4, 0.3, pan=0.4)
P(rumble(1.8), 73.8, 0.8)
for k in range(8):
    P(chug(), 73.9 + k * 0.2, 0.16, pan=-0.5 - k * 0.05)
guitar(69.6, ["Dm", "Bb", "F", "A"], 1.4, vol=0.2)

# ================================================================ 等 75.5–85.5
for k in range(int(10.0 / 0.5)):
    P(tick(k % 2 == 1), 75.5 + k * 0.5, 0.25, pan=0.25)
guitar(75.5, ["F", "C", "Dm", "Bb", "F", "C", "Bb"], 1.4, vol=0.2, pattern=(0, 2, 1, 3))
P(wind(5.0, 0.08), 79.5, 1.0)
for i in range(9):                                                # 便利贴一张张贴上去
    P(knock(), 81.7 + i * 0.32, 0.08, pan=-0.4 + i * 0.1)

# ================================================================ 怕 85.5–97.5
P(pad([50, 57, 62], 12.0, att=2.0, rel=1.5, bright=1.6), 85.5, 0.4)
for i, chn in enumerate(["Dm", "Bb", "Gm", "A"]):
    t0 = 85.6 + i * 3.0
    P(piano(ROOT[chn] + 12, 2.8), t0, 0.35)
    for j, m in enumerate(ARP[chn]):
        P(piano(m + 12, 0.6), t0 + j * 0.7, 0.16, pan=-0.25)
P(sand(5.0), 91.5, 1.0)                                           # 沙漏
P(thump(), 95.5, 0.6)                                             # 天平沉下去
P(rumble(1.0), 95.5, 0.5)

# ================================================================ 老去的那一天 97.5–104.3
for i, (b, m, d) in enumerate(THEME_MIN):
    P(music_box(m - 0.3, 2.4), 97.8 + b * 0.85, 0.3, pan=-0.2)
P(pad([45, 52, 57], 6.8, att=2.0, rel=1.0, bright=0.8), 97.5, 0.35)
for k in range(int(6.5 / 1.0)):
    P(tick(k % 2 == 1), 97.6 + k * 1.0, 0.15)

# ================================================================ 心跳 104.3–107.5
P(swell(0.5, 800, 9000), 103.9, 0.6)
for k in range(4):
    P(heartbeat(), 104.4 + k * 0.8, 0.45 + 0.05 * k)
P(cello(41, 3.2, att=0.8), 104.3, 0.4)

# ================================================================ 一个人出发 107.5–112.5
P(swish(0.8), 108.1, 0.5)                                         # 吹掉灰
for i, m in enumerate((65, 69, 72, 77)):                          # 戴上草帽
    P(pluck(m, length=1.5), 109.2 + i * 0.06, 0.35)
guitar(109.8, ["F", "C"], 1.2, vol=0.26, pattern=(0, 1, 2, 3))
for k in range(10):
    P(chug(0.1), 110.3 + k * 0.2, 0.1)

# ================================================================ 很多地方 112.5–124.5
b = 0.5
for k in range(int(12.0 / b)):
    t0 = 112.5 + k * b
    P(kick(0.7), t0, 0.35 if k % 2 == 0 else 0.0)
    P(shaker(), t0 + b / 2, 0.2, pan=0.3)
guitar(112.5, ["F", "C", "Dm", "Bb", "F", "C", "Bb", "C", "F"], 1.33, vol=0.24, pattern=(0, 1, 2, 3, 2, 1))
for i, chn in enumerate(["F", "C", "Dm", "Bb", "F", "C", "Bb", "C", "F"]):
    P(bass(ROOT[chn] + 12, 1.2), 112.5 + i * 1.33, 0.35)
for i in range(7):                                                # 地点一个个亮起
    P(music_box([77, 79, 81, 84, 86, 89, 93][i], 1.4), 113.4 + i * 0.85, 0.4, pan=-0.5 + i * 0.16)
for i in range(6):
    P(music_box([96, 98, 101, 103, 105, 108][i], 0.6), 113.4 + 7 * 0.85 + i * 0.18, 0.2, pan=0.4 - i * 0.15)
melody(119.4, THEME_MAJ, 0.62, "pluck", 0.5, shift=-12, pan=0.1)
P(pad(CH["F"] + [72], 5.0, att=1.0, rel=2.0), 119.4, 0.45)
P(swell(1.2, 400, 8000), 120.2, 0.5)

# ================================================================ 片尾 124.5–130.5
P(swish(), 126.1, 0.7)
melody(124.9, THEME_MAJ, 0.6, "box", 0.6, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.0), 124.9, 0.5)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 128.7 + i * 0.07, 0.45, pan=-0.3 + i * 0.2)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.85), (6, 0.9), (17.5, 1.0), (44.5, 1.0), (64.5, 1.15), (69.5, 1.0), (97.5, 0.95), (104.3, 1.15),
        (107.5, 1.0), (112.5, 0.75), (124.5, 0.8), (DUR + 1, 1.0)])
M.muffle([(0, 0), (97.4, 0), (97.6, 0.8), (104.2, 0.8), (104.35, 0), (DUR + 1, 0)])
duck = [(0, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 130, 4)))

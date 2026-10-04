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

DUR = 177.0
M = Mix(DUR)

# 第九稿调整了段落顺序：配乐仍按旧时间轴书写，放置时整段搬到新位置
MOVES = [(85.5, 91.0, 153.5), (91.0, 116.0, 101.5), (116.0, 132.0, 85.5), (132.0, 159.0, 126.5)]


def remap(t):
    for a, b, new in MOVES:
        if a <= t + 0.3 < b:
            return t - a + new
    return t


def P(sig, t, vol=1.0, pan=0.0):
    M.place(sig, remap(t), vol, pan)

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

# ================================================================ 很久以前 6–15：台灯下的旧铁盒
P(pad(CH["F"] + [72], 9.0, att=2.0, rel=2.0, bright=1.2), 6.0, 0.3)
P(knock(), 6.4, 0.25)                                             # 打开铁盒
for k in range(6):                                                # 翻车票
    P(scratch(0.25), 7.5 + k * 0.22, 0.12)
melody(8.6, THEME_MAJ[:5], 0.9, "box", 0.32, pan=-0.1)
P(swell(2.4, 300, 5000), 12.4, 0.5)                               # 褪色、晕开
soft_rain(13.0, 20.2, 0.22)

# ================================================================ 只想逃走 15–20
guitar(15.0, ["Dm", "Bb", "C", "Dm"], 1.25, vol=0.26, pattern=(0, 1, 2, 3))
P(cello(38, 5.0, att=0.6), 15.0, 0.35)
for k in range(14):
    P(knock(), 15.2 + k * 0.34, 0.05, pan=-0.4 + k * 0.06)

# ================================================================ 问朋友、报团 20–29
P(pad([50, 57, 62], 9.0, att=1.0, rel=1.0, bright=1.4), 20.0, 0.3)
for t0, m in ((20.3, 96), (21.4, 89), (22.4, 86), (23.3, 84)):
    P(music_box(m, 0.6), t0, 0.35, pan=0.2)
P(tick(), 24.0, 0.2)                                              # 已读
P(swish(0.5), 25.2, 0.5)                                          # 划到 App
P(knock(), 27.6, 0.3)                                             # 点下报名
for i, m in enumerate((84, 88, 91)):
    P(music_box(m, 1.2), 27.9 + i * 0.09, 0.35)

# ================================================================ 高原 29–48.5
P(wind(19.5, 0.14), 28.8, 1.0, pan=-0.3)
P(rumble(5.5), 29.3, 0.35)                                        # 大巴爬坡
guitar(29.0, ["Am", "F", "C", "Am", "F", "C", "Am", "F", "C", "Am", "F"], 1.25, vol=0.22, pattern=(0, 2, 1, 3, 2, 1))
P(pad([57, 64, 69], 13.5, att=2.5, rel=2.0, bright=2.2), 29.0, 0.32)
for k in range(6):                                                # 情侣头顶的小爱心
    P(music_box([93, 96, 98][k % 3], 0.6), 35.0 + k * 0.6, 0.12, pan=-0.5 + (k % 2))
P(snap(), 37.9, 0.5)                                              # 快门
P(snap(), 40.4, 0.45)
P(cello(36, 3.0, att=1.0), 40.3, 0.4)                             # 视线落下来
P(whisper(2.2), 40.4, 0.6, pan=-0.4)
P(whisper(2.2), 40.6, 0.6, pan=0.4)
for k in range(6):                                                # 高原反应
    P(breath(1.2), 42.6 + k * 1.0, 0.9)
P(swell(2.0, 300, 3000), 42.8, 0.4)
P(pad([45, 52, 57], 6.0, att=1.5, rel=1.0, bright=1.0), 42.5, 0.35)
for t0, m in ((43.2, 69), (44.8, 65), (46.4, 64)):
    P(pluck(m, length=1.6, bright=0.18), t0, 0.28, pan=-0.2)
for k in range(5):                                                # 隔壁闷闷的笑声
    P(reed(72 + (k % 3) * 2, 0.18), 43.4 + k * 0.9, 0.08, pan=0.7)

# ================================================================ 团餐 48.5–70.5：几乎无声，只有碗筷与转盘
for k in range(5):
    P(music_box(100 + (k % 2) * 3, 0.3), 48.8 + k * 0.55, 0.1, pan=-0.5 + k * 0.25)   # 碗筷
for k in range(int(22 / 1.1)):
    P(chug(0.06), 48.6 + k * 1.1, 0.04, pan=0.2)                  # 转盘轻轻转
for k in range(10):                                               # 手机的提示音、划屏
    P(beep(2400 + (k % 3) * 300, 0.06), 51.9 + k * 0.42, 0.25, pan=-0.6 + (k % 5) * 0.3)
for i in range(3):                                                # 爱心掉在桌上
    P(knock(), 57.0 + i * 0.35, 0.12)
P(pad([45, 52, 57], 8.0, att=3.0, rel=2.0, bright=0.8), 58.9, 0.3)
P(pad([50, 57, 62], 10.5, att=2.0, rel=1.5, bright=0.7), 48.6, 0.2)       # 很轻的底色，冷场但不是死寂
P(wind(10.0, 0.04), 49.0, 1.0)
for t0, m in ((59.2, 64), (61.9, 62), (64.0, 60)):
    P(pluck(m, length=2.0, bright=0.16), t0, 0.22)
P(cello(33, 4.0, att=1.5), 66.6, 0.4)                             # 有点悲哀

# ================================================================ 两个人的寂寞 70.5–76
soft_rain(70.4, 73.5, 0.25)
P(swish(0.8), 71.2, 0.4)
for i, m in enumerate((77, 81, 84, 89)):                          # 星空那半边亮起来
    P(music_box(m, 2.0), 71.4 + i * 0.25, 0.3, pan=0.4)
P(pad(CH["F"] + [72], 4.5, att=1.0, rel=1.5, bright=1.8), 71.3, 0.35)

# ================================================================ 敲门 76–85.5
P(breath(1.2), 76.1, 0.7)
P(knock(), 76.8, 0.45, pan=0.5)
P(knock(), 77.15, 0.45, pan=0.5)
P(swish(0.4), 78.4, 0.3, pan=0.5)                                 # 开门
P(pluck(65, length=1.6, bright=0.18), 79.6, 0.25)
P(knock(), 80.8, 0.3, pan=0.5)                                    # 关门
P(cello(41, 3.5, att=1.0), 81.2, 0.3)
P(wind(3.0, 0.08), 82.6, 1.0)                                     # 停顿：只有风
P(swell(2.2, 300, 4000), 83.4, 0.3)

# ================================================================ 越来越习惯一个人 85.5–91
guitar(85.5, ["F", "C", "Dm", "Bb"], 1.35, vol=0.24, pattern=(0, 1, 2, 3, 2, 1))
for k in range(6):
    P(chug(0.08), 85.6 + k * 0.28, 0.08)                          # 火车
P(jingle(), 89.2, 0.25)                                           # 夜市

# ================================================================ 并不浪漫 91–101：雨夜、小巷
soft_rain(90.9, 96.5, 0.3)
for k in range(5):
    P(chug(0.1), 91.4 + k * 0.22, 0.12)
P(cello(38, 9.5, att=1.5), 91.1, 0.4)
melody(91.5, THEME_MIN[:5], 0.9, "pluck", 0.32, shift=-12)
for k in range(8):
    P(knock(), 96.3 + k * 0.55, 0.12 * (0.6 + 0.4 * (k % 2)), pan=(-0.6 if k % 2 else 0.6))
for k in range(5):
    P(beep(1700), 96.9 + k * 0.8, 0.5)
P(rumble(4.0), 96.5, 0.3)

# ================================================================ 一个人 101–111
guitar(101.0, ["Dm", "Bb", "F", "C", "Dm", "Bb", "F", "A"], 1.25, vol=0.2)
melody(101.1, THEME_MIN, 1.2, "pluck", 0.36, shift=-12, pan=0.1)
P(music_box(100, 0.4), 101.5, 0.12)
P(whisper(1.6), 102.1, 0.5, pan=0.6)
P(wave_sound(3.0), 104.3, 0.6)
P(rumble(3.4), 107.3, 0.35)

# ================================================================ 那些眼神 111–116
for k in range(14):
    P(tick(), 111.2 + k * 0.16, 0.08, pan=-0.7 + (k % 5) * 0.35)
for k in range(8):
    P(whisper(1.4), 111.3 + k * 0.45, 0.55 + 0.05 * k, pan=-0.6 + (k % 3) * 0.6)
P(swell(3.6, 200, 4000), 111.9, 0.6)
P(cello(36, 4.5, att=1.5), 111.1, 0.5)

# ================================================================ 月台 116–123
P(rumble(1.6), 116.0, 0.8)
for k in range(8):
    P(chug(), 116.1 + k * 0.16, 0.18, pan=0.5 - k * 0.1)
P(whistle(0.8), 116.9, 0.3, pan=0.4)
P(rumble(1.8), 120.3, 0.8)
for k in range(8):
    P(chug(), 120.4 + k * 0.2, 0.16, pan=-0.5 - k * 0.05)
guitar(116.1, ["Dm", "Bb", "F", "A", "Dm"], 1.4, vol=0.2)

# ================================================================ 等 123–132
for k in range(int(9.0 / 0.5)):
    P(tick(k % 2 == 1), 123.0 + k * 0.5, 0.25, pan=0.25)
guitar(123.0, ["F", "C", "Dm", "Bb", "F", "C"], 1.5, vol=0.2, pattern=(0, 2, 1, 3))
P(wind(4.0, 0.08), 126.5, 1.0)
for i in range(9):                                                # 便利贴一张张贴上去
    P(knock(), 128.7 + i * 0.32, 0.08, pan=-0.4 + i * 0.1)

# ================================================================ 怕 132–144
P(pad([50, 57, 62], 12.0, att=2.0, rel=1.5, bright=1.6), 132.0, 0.4)
for i, chn in enumerate(["Dm", "Bb", "Gm", "A"]):
    t0 = 132.1 + i * 3.0
    P(piano(ROOT[chn] + 12, 2.8), t0, 0.35)
    for j, m in enumerate(ARP[chn]):
        P(piano(m + 12, 0.6), t0 + j * 0.7, 0.16, pan=-0.25)
P(sand(5.0), 138.0, 1.0)                                          # 沙漏
P(thump(), 142.0, 0.6)                                            # 天平沉下去
P(rumble(1.0), 142.0, 0.5)

# ================================================================ 老去的那一天 144–150.8
for b_, m, d in THEME_MIN:
    P(music_box(m - 0.3, 2.4), 144.3 + b_ * 0.85, 0.3, pan=-0.2)
P(pad([45, 52, 57], 6.8, att=2.0, rel=1.0, bright=0.8), 144.0, 0.35)
for k in range(6):
    P(tick(k % 2 == 1), 144.1 + k * 1.0, 0.15)

# ================================================================ 心跳 150.8–154
P(swell(0.5, 800, 9000), 150.4, 0.6)
for k in range(4):
    P(heartbeat(), 150.9 + k * 0.8, 0.45 + 0.05 * k)
P(cello(41, 3.2, att=0.8), 150.8, 0.4)

# ================================================================ 一个人出发 154–159
P(swish(0.8), 154.6, 0.5)
for i, m in enumerate((65, 69, 72, 77)):
    P(pluck(m, length=1.5), 155.7 + i * 0.06, 0.35)
guitar(156.3, ["F", "C"], 1.2, vol=0.26, pattern=(0, 1, 2, 3))
for k in range(10):
    P(chug(0.1), 156.8 + k * 0.2, 0.1)

# ================================================================ 很多地方 159–171
b = 0.5
for k in range(int(12.0 / b)):
    t0 = 159.0 + k * b
    P(kick(0.7), t0, 0.35 if k % 2 == 0 else 0.0)
    P(shaker(), t0 + b / 2, 0.2, pan=0.3)
guitar(159.0, ["F", "C", "Dm", "Bb", "F", "C", "Bb", "C", "F"], 1.33, vol=0.24, pattern=(0, 1, 2, 3, 2, 1))
for i, chn in enumerate(["F", "C", "Dm", "Bb", "F", "C", "Bb", "C", "F"]):
    P(bass(ROOT[chn] + 12, 1.2), 159.0 + i * 1.33, 0.35)
tt, step = 0.9, 0.75                                              # 光点一个个亮起（与画面同一节奏）
for i in range(27):
    P(music_box([77, 79, 81, 84, 86, 89, 91, 93, 96, 98][i % 10] + 12 * (i >= 10) * 0, 1.0), 159.0 + tt,
      0.32 if i < 7 else 0.16, pan=-0.6 + (i % 7) * 0.2)
    tt += step
    step = max(0.16, step * 0.84)
melody(165.9, THEME_MAJ, 0.62, "pluck", 0.5, shift=-12, pan=0.1)
P(pad(CH["F"] + [72], 5.0, att=1.0, rel=2.0), 165.9, 0.45)
P(swell(1.2, 400, 8000), 166.7, 0.5)

# ================================================================ 片尾 171–177
P(swish(), 172.6, 0.7)
melody(171.4, THEME_MAJ, 0.6, "box", 0.6, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.0), 171.4, 0.5)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 175.2 + i * 0.07, 0.45, pan=-0.3 + i * 0.2)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.85), (6, 0.9), (29, 1.0), (48.5, 1.1), (70.5, 1.0), (121.5, 1.15), (126.5, 1.0), (138.5, 0.95),
        (145.3, 1.15), (148.5, 1.0), (159, 0.75), (171, 0.62), (DUR + 1, 0.62)])
M.muffle([(0, 0), (138.4, 0), (138.6, 0.8), (145.2, 0.8), (145.35, 0), (DUR + 1, 0)])
duck = [(0, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 177, 4)))

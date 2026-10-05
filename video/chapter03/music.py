"""第三章 · 从游客到旅人 —— 配乐（纯代码合成）。

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

DUR = 165.0
M = Mix(DUR)

def remap(t):
    """第二稿：配乐按第一稿时间书写，放置时搬到新位置（四人桌提前、分屏多一组）。"""
    if 133.0 <= t + 0.3 < 141.0:
        return t - 67.0
    if 90.0 <= t + 0.3 < 133.0:
        return t + 16.0
    if t + 0.3 >= 141.0:
        return t + 8.0
    return t


def remap_j(T):
    """第五稿（手账）：清晨、气泡两段各提前 1 秒；结尾另写，直接放置。"""
    if T >= 148.0:
        return None
    if T >= 136.5:
        return T - 1.0
    return T


DIRECT = [False]                                                   # True：按新时间直接放置


def P(sig, t, vol=1.0, pan=0.0):
    T = t if DIRECT[0] else remap_j(remap(t))
    if T is not None:
        M.place(sig, T, vol, pan)


def PA(sig, t, vol=1.0, pan=0.0):
    M.place(sig, t, vol, pan)


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


# ================================================================ 片头 0–6
melody(0.4, THEME_MAJ, 0.7, "pluck", 0.55, shift=-12, pan=0.1)
P(pad(CH["F"], 4.5, att=1.5), 0.6, 0.3)
for t0 in (2.1, 2.55, 3.0):
    P(swish(), t0, 0.5)

# ================================================================ 第二张票 6–14
P(pad(CH["F"] + [72], 8.0, att=2.0, rel=2.0, bright=1.2), 6.0, 0.3)
for k in range(5):
    P(scratch(0.25), 6.8 + k * 0.22, 0.12)
melody(7.6, THEME_MAJ[:5], 0.9, "box", 0.3, pan=-0.1)
P(swell(2.4, 300, 5000), 11.4, 0.5)

# ================================================================ 并不浪漫 14–39
P(cello(38, 10.0, att=1.5), 14.0, 0.35)
for k in range(24):                                               # 石子路上的轮子
    P(chug(0.06), 14.2 + k * 0.2, 0.12 + 0.04 * (k % 2), pan=-0.3)
melody(14.5, THEME_MIN[:5], 0.9, "pluck", 0.3, shift=-12)
for k in range(10):                                               # 夜路：脚步越来越快
    P(knock(), 19.2 + k * 0.42 - k * k * 0.01, 0.12, pan=(-0.5 if k % 2 else 0.5))
P(rumble(4.0), 19.0, 0.3)
guitar(24.0, ["Dm", "Bb", "F", "C", "Dm", "Bb", "F", "A"], 1.25, vol=0.2)
melody(24.1, THEME_MIN, 1.2, "pluck", 0.34, shift=-12, pan=0.1)
P(music_box(100, 0.4), 24.5, 0.12)
P(wave_sound(3.0), 27.4, 0.5)
P(rumble(3.4), 30.4, 0.35)
for k in range(14):                                               # 那些眼神
    P(tick(), 34.2 + k * 0.16, 0.08, pan=-0.7 + (k % 5) * 0.35)
for k in range(8):
    P(whisper(1.4), 34.3 + k * 0.45, 0.55, pan=-0.6 + (k % 3) * 0.6)
P(cello(36, 4.5, att=1.5), 34.1, 0.45)

# ================================================================ 路过的游客 39–59：赶场一样的节拍
b = 60 / 132
t = 39.0
while t < 52.8:
    P(kick(0.8), t, 0.3)
    P(shaker(), t + b / 2, 0.22, pan=0.3)
    t += b
guitar(39.0, ["C", "G" if False else "C", "F", "C", "F", "C", "F", "C", "F", "C", "F"], 1.25, vol=0.2, pattern=(0, 1, 2, 3))
for k in range(30):                                               # 人群的嘈杂
    P(whisper(0.8), 39.2 + k * 0.45, 0.25, pan=-0.8 + (k % 5) * 0.4)
for tf in (46.9, 49.2, 51.5):                                     # 快门 + 打勾
    P(snap(), tf, 0.4)
    P(scratch(0.2), tf + 0.4, 0.3, pan=0.5)
P(swish(0.6), 48.6, 0.3)
P(swish(0.6), 50.9, 0.3)
for k in range(8):                                                # 翻相册
    P(tick(), 53.5 + k * 0.4, 0.08)
P(pad([45, 52, 57], 5.5, att=1.0, rel=1.0, bright=0.8), 53.2, 0.3)
P(pluck(64, length=2.0, bright=0.16), 57.0, 0.25)

# ================================================================ 世界展开 59–66
P(swell(2.6, 300, 6000), 59.0, 0.6)
P(wind(6.0, 0.1), 59.2, 1.0)
P(pad(CH["F"] + [72, 77], 6.5, att=2.0, rel=2.0, bright=2.0), 59.4, 0.45)
melody(60.4, THEME_MAJ, 0.62, "pluck", 0.45, shift=-12, pan=0.1)
for i, m in enumerate((77, 81, 84, 89)):                          # 推起帽檐
    P(music_box(m, 1.6), 62.0 + i * 0.08, 0.3)

# ================================================================ 以前 / 后来 74–106（四组，按新时间直接放置）
for k4 in range(4):
    t0 = 74.0 + k4 * 8.0
    PA(pad([50, 57, 62], 3.8, att=0.6, rel=0.6, bright=0.8), t0, 0.25)   # 以前：灰灰的
    for k in range(7):
        PA(tick(k % 2 == 1), t0 + 0.2 + k * 0.5, 0.12)
    tb = t0 + 4.0                                                 # 后来：明亮的吉他
    PA(swish(0.4), tb - 0.2, 0.4)
    for i, chn in enumerate(["F", "C", "Dm"]):
        PA(pluck(ROOT[chn] + 12, length=1.6, bright=0.2), tb + i * 1.3, 0.3, -0.2)
        for j, kk in enumerate((0, 1, 2, 3, 2, 1)):
            PA(pluck(ARP[chn][kk] + 12, length=1.2, bright=0.24), tb + i * 1.3 + j * 1.3 / 6, 0.28, 0.1)
    PA(bass(41, 3.6), tb, 0.3)
    PA(kick(0.7), tb, 0.3)
PA(swish(0.5), 93.8, 0.3)                                         # 背包甩上肩
for k in range(6):
    PA(knock(), 102.3 + k * 0.4, 0.06, pan=0.4)

# ================================================================ 走进当地人的生活 90–133：热闹的拨弦 + 手鼓
b2 = 0.5
for k in range(int((133.0 - 90.0) / b2)):
    t0 = 90.0 + k * b2
    if k % 2 == 0:
        P(kick(0.6), t0, 0.22)
    P(jingle(), t0 + b2 / 2, 0.08 if k % 4 else 0.14, pan=0.4)
for i, chn in enumerate(["F", "C", "Dm", "Bb"] * 8):
    t0 = 90.0 + i * 1.33
    if t0 > 132.5:
        break
    P(bass(ROOT[chn] + 12, 1.2), t0, 0.28)
    for j, m in enumerate(ARP[chn]):
        P(pluck(m + 12, length=0.9, bright=0.25), t0 + j * 0.33, 0.18, pan=-0.3 + j * 0.2)
P(wind(3.0, 0.06), 90.2, 1.0)
for k in range(3):                                                # 深呼吸
    P(breath(1.2), 91.0 + k * 0.9, 0.5)
P(swish(0.6), 96.2, 0.4)                                          # 换衣服的帘子
for i, m in enumerate((84, 88, 91)):
    P(music_box(m, 1.2), 98.7 + i * 0.1, 0.3)
for k in range(20):                                               # 菜市场的吆喝
    P(whisper(0.9), 101.2 + k * 0.28, 0.35, pan=-0.7 + (k % 6) * 0.28)
for k in range(5):
    P(knock(), 103.5 + k * 0.5, 0.1)
for k in range(14):                                               # 切菜
    P(knock(), 107.4 + k * 0.22, 0.12, pan=-0.3)
P(rain(3.0) * 0.12, 108.0, 0.8)                                   # 油锅滋滋
for k in range(6):
    P(music_box(98 + (k % 2) * 3, 0.3), 111.8 + k * 0.3, 0.1)    # 碗筷
P(thump(), 116.0, 0.35)                                           # 射击（闷闷的）
P(thump(), 117.6, 0.35)
P(snap(), 118.5, 0.4)                                             # 击掌
for i, m in enumerate((84, 88, 91, 96)):
    P(music_box(m, 1.0), 118.6 + i * 0.07, 0.25)
for k in range(4):                                                # 清晨：鸟叫、蒸笼
    n, tt = _t(0.12)
    f = 3200 + 1200 * np.sin(np.pi * tt / 0.12)
    P(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.12) * 0.1, 121.4 + k * 0.9, 0.6, pan=0.5)
P(swell(1.0, 400, 3000), 121.6, 0.3)
P(swell(0.8, 800, 9000), 127.4, 0.4)                              # 梦的气泡
for i, m in enumerate((96, 93, 89, 86, 84)):
    P(music_box(m, 1.0), 130.4 + i * 0.07, 0.3)                   # 气泡破掉

# ================================================================ 视线消失 133–141
melody(133.3, THEME_MAJ, 0.62, "pluck", 0.5, shift=-12, pan=0.1)
P(pad(CH["F"] + [72], 7.5, att=1.5, rel=2.0, bright=1.6), 133.2, 0.4)
P(music_box(100, 0.5), 137.3, 0.3)                                # 碰杯
P(music_box(103, 0.5), 137.45, 0.25)

DIRECT[0] = True

# ================================================================ 手账翻页动画 59–63.6
tf = 59.2
while tf < 63.6:
    PA(tick(), tf, 0.07, pan=0.3)
    tf += 1.0 / (3 + (tf - 59.0) * 1.2)

# ================================================================ 合上手账 148–159 / 片尾 159–165
PA(pad(CH["F"] + [72], 11.0, att=2.0, rel=3.0, bright=1.2), 148.0, 0.32)
PA(snap(), 149.4, 0.25)                                            # 橡皮筋
melody(149.6, THEME_MAJ[:5], 0.8, "box", 0.3)
PA(swell(1.6, 300, 4000), 149.8, 0.3)                              # 明信片滑出来
PA(music_box(91, 2.4), 151.0, 0.28)
PA(swish(0.6), 151.8, 0.35)                                        # 放进铁盒
PA(knock(), 154.4, 0.25)                                           # 盖上盖子
PA(music_box(84, 2.0), 155.2, 0.2)
PA(swish(), 160.6, 0.45)
melody(159.4, THEME_MAJ, 0.6, "box", 0.45, pan=0.1)
PA(pad(CH["F"], 4.0, att=1.0, rel=2.0), 159.4, 0.5)
for i, m in enumerate((65, 69, 72, 77)):
    PA(music_box(m, 3.5), 162.8 + i * 0.07, 0.45, pan=-0.3 + i * 0.2)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.85), (6, 0.9), (14, 1.0), (39, 0.9), (59, 1.0), (66, 0.9), (74, 1.0), (106, 0.8), (148, 0.95), (159, 0.62),
        (DUR + 1, 0.62)])
M.muffle([(0, 0), (DUR + 1, 0)])
duck = [(0, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 165, 4)))

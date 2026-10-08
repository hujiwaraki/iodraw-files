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

DUR = 165.0
M = Mix(DUR)
B = 0.75
BAR = 3.0


WARP = [True]


def warp(t):
    """第十三稿在高原后面加了 3 秒、平原中间加了 6 秒：旧时间轴上的声音整体往后挪。"""
    if t < 28.5:
        return t
    if t < 44.17:
        return t + 3.0
    return t + 9.0


def warp2(t):
    """第十六稿洪流那段多了 3 屏字幕，44 秒以后整体再往后挪 2.5 秒。"""
    return t if t < 44.0 else t + 2.5


def warp3(t):
    """第十九稿：平原加一屏（+3 秒），月光后面加“成长”那一段（再 +15.5 秒）。"""
    if t < 73.0:
        return t
    if t < 115.5:
        return t + 3.0
    return t + 18.5


def P(sig, t, vol=1.0, pan=0.0):
    M.place(sig, warp3(warp2(warp(t) if WARP[0] else t)), vol, pan)


def Q(sig, t, vol=1.0, pan=0.0):
    """直接按最终时间轴放。"""
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
WARP[0] = False                                                      # 这一段直接按新时间轴写：16–44
P(wind(30.5, 0.1, 0.5), 16.0, 1.0)
for i, (m, d) in enumerate(((38, 7.0), (41, 7.0), (36, 7.0), (38, 9.5))):
    P(cello(m + 12, d, att=1.5), 16.0 + i * 7.0, 0.4)
    P(pad([m + 12, m + 19], d, att=2.0, rel=2.0, bright=0.7), 16.0 + i * 7.0, 0.1)
for k in range(10):                                                  # 低鼓，像心跳
    P(kick(0.5), 16.0 + k * BAR, 0.14)
    P(kick(0.5), 16.0 + k * BAR + 0.375, 0.07)
P(thump(), 28.6, 0.12)                                               # 有棱有角
WARP[0] = True
for k, m in enumerate((69, 72, 74, 76)):                             # 雪峰上的金光
    P(music_box(m + 12, 2.0), 22.75 + k * 0.75, 0.07, 0.4)
for k in range(7):                                                   # 一块块垒石头
    P(knock(), 28.7 + k * 0.743, 0.12, -0.2)
P(noise(8.5, 200, 3000, 0.18, 0.8), 34.8, 1.0, -0.3)                 # 雪水冲下来

# ================================================================ 冲积平原 47.17–53.17（新时间轴）：水声乱乱的，然后吉他稳稳地走起来
WARP[0] = False
P(noise(6.0, 120, 1400, 0.14, 1.2), 47.17, 1.0, 0.2)                 # 弯弯绕绕的水
P(pad(CH["Dm"] + [62], 3.2, att=1.2, rel=1.5, bright=0.8), 47.2, 0.14)
for k, mm in enumerate((62, 65, 60, 64, 57, 62)):                    # 乱一点的音
    P(pluck(mm + 12, length=1.2, bright=0.2), 47.5 + k * 0.45 + 0.12 * (k % 2), 0.06, -0.3 + (k % 3) * 0.3)
guitar_bar(50.17, "F", 0.1)                                          # 秩序：吉他的节奏稳稳地进来
for k in range(4):
    P(shaker(), 50.545 + k * 0.75, 0.035, 0.3)
WARP[0] = True

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
P(waves_snd(42.5, 0.1), 61.5, 1.0)
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
for i, ch in enumerate(["F", "C"]):                                  # 永不回头：旋律完整地冲出来
    strings(86.5 + i * 2.5, ch, 2.5, 0.24, bright=1.6)
melody(86.5, THEME_MAJ, 0.5625, "cello", 0.5, shift=-12)
for k in range(6):
    P(kick(0.5), 86.5 + k * 0.75, 0.1)
for i, ch in enumerate(["F", "Dm", "Bb", "F"]):                      # 地图、月亮升起来：安静下来
    P(pad(CH[ch], 3.2, att=1.2, rel=1.6, bright=1.0), 91.5 + i * 3.125, 0.14)
WARP[0] = False                                                      # 一张缩影（新时间轴 100.5–109.9）
P(scratch(1.8), 100.7, 0.1)                                          # 铅笔画出地图
for k in range(18):                                                  # 红线一步步走过去
    P(tick(k % 2 == 1), 102.7 + k * 0.375, 0.025, -0.4 + (k % 5) * 0.2)
for k, mm in enumerate((72, 76, 79, 84)):                            # 月亮升起来
    P(music_box(mm, 2.0), 110.2 + k * 0.6, 0.07, -0.3 + k * 0.2)
WARP[0] = True

# ================================================================ 翻书 104–116.5：八音盒完整奏一遍主旋律
melody(104.5, THEME_MAJ, B, "box", 0.28, pan=0.1)
melody(110.5, THEME_END, B, "box", 0.28, pan=-0.1)
P(pad(CH["F"] + [72], 12.0, att=2.0, rel=2.0, bright=1.3), 104, 0.16)
WARP[0] = False
for k in range(4):                                                   # 一页一页往回翻（四次）
    P(swish(0.6), 113.0 + 3.2 + k * 1.55, 0.12, 0.2)
WARP[0] = True
P(thump(), 115, 0.12)                                              # 合上

# ================================================================ 推门走进晨光 116.5–129
for i, ch in enumerate(["F", "C", "Bb", "F"]):
    P(piano(ROOT[ch] + 12, BAR * 0.9), 116.5 + i * BAR, 0.12, -0.2)
    for j, k in enumerate((0, 1, 2, 1)):
        P(piano(CH[ch][k] + 12, B * 0.9), 116.5 + i * BAR + j * B, 0.08, 0.1)
P(knock(), 117, 0.08)                                              # 鹅卵石放在书上
P(swell(2.4, 400, 7000), 120.6, 0.14)                                # 推开门
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 126 + i * 0.07, 0.2, -0.3 + i * 0.2)

# ================================================================ 片尾 129–135
P(swish(), 130.6, 0.4)
melody(129.4, THEME_MAJ, 0.6, "box", 0.24, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.0), 129.4, 0.35)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 132.8 + i * 0.07, 0.24, pan=-0.3 + i * 0.2)

# ================================================================ 第十九稿新加的两段（最终时间轴）
Q(pad(CH["F"] + [CH["F"][0] + 12], 3.0, att=1.0, rel=1.5, bright=1.1), 73.0, 0.16)   # 所谓人间，就是在人之间
for j, k in enumerate((0, 1, 2, 1)):
    Q(pluck(ARP["F"][k] + 12, length=1.4, bright=0.2), 73.0 + j * B, 0.1, 0.15)

for i, ch in enumerate(["Dm", "Bb", "Dm", "C"]):                    # 爬坡：低沉、一下一下的
    Q(cello(ROOT[ch] + 12, 3.0, att=0.6), 118.5 + i * 3.1, 0.3)
    Q(pad(CH[ch], 3.1, att=1.0, rel=1.4, bright=0.8), 118.5 + i * 3.1, 0.1)
for k in range(16):                                                  # 重锤：一下一下凿
    Q(kick(0.5), 118.5 + k * 0.775, 0.1 if k % 2 == 0 else 0.05)
for t0 in (120.8, 123.1, 127.1):                                     # 滑下来、摔一跤
    Q(noise(0.8, 300, 2400, 0.12, 0.1), t0, 1.0, 0.2)
Q(swell(2.0, 300, 6000), 129.3, 0.12)                                # 翻上坡顶
for i, m in enumerate((65, 69, 72)):                                 # 又回到新手村：轻一点、带点笑
    Q(music_box(m + 12, 1.6), 130.9 + i * 0.4, 0.1, -0.2 + i * 0.2)
Q(pad(CH["F"] + [72], 3.4, att=1.2, rel=1.6, bright=1.2), 130.6, 0.14)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.9), (6, 1.4), (9, 1.7), (15.5, 1.6), (16, 1.1), (46.5, 1.1), (61.5, 1.2), (65.5, 1.6), (72.5, 1.5), (76.5, 1.0), (134, 1.1), (146, 1.1), (148, 1.6), (158.5, 1.4), (159, 0.75), (DUR + 1, 0.75)])
duck = [(0, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 160, 4)))

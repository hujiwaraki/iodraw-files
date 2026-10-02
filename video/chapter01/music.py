"""第一章 · 出逃 —— 配乐（纯代码合成）。

情绪线：八音盒主题 → 灰色小调（雨声、潮水）→ 钢琴等待 → 钟表滴答、水下心跳 → “叮”地惊醒
        → 解开根的拨弦 → 开门时主题绽放 → 异乡民谣 → 重活一遍的高潮 → 八音盒收尾
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
from synth import (Mix, bass, bandnoise, buzz, cello, chug, heartbeat, jingle, kick, knock, music_box, pad, piano,  # noqa: E402
                   pluck, rain, reed, rumble, scratch, shaker, snap, swell, swish, thump, tick, whistle)

DUR = 136.0
M = Mix(DUR)
P = M.place

# 主旋律动机（整个系列共用）：大调与小调两个版本，(拍, 音高, 时值拍)
THEME_MAJ = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 79, 2)]
THEME_MIN = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 74, 2)]
CH = {"F": [57, 60, 65], "C": [55, 60, 64], "Dm": [57, 62, 65], "Bb": [58, 62, 65], "Gm": [55, 58, 62],
      "A": [57, 61, 64], "Am": [57, 60, 64]}
ROOT = {"F": 41, "C": 36, "Dm": 38, "Bb": 34, "Gm": 43, "A": 45, "Am": 45}
ARP = {"F": [53, 57, 60, 65], "C": [48, 55, 60, 64], "Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62],
       "Gm": [43, 50, 55, 58], "A": [45, 52, 57, 61], "Am": [45, 52, 57, 60]}


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


# ================================================================ 片头 0–6
melody(0.4, THEME_MAJ, 0.7, "box", 0.8, pan=0.1)
P(pad(CH["F"], 4.5, att=1.5), 0.6, 0.35)
P(swish(), 2.1, 0.6)
P(swish(), 2.55, 0.5)
P(swish(), 3.0, 0.5)

# ================================================================ 一、这片土地 6–33.5（D 小调，雨）
P(rain(30.0), 5.5, 1.0)
P(pad([50, 57, 62], 27.0, att=3.0, rel=2.0, bright=2.2), 6.0, 0.6)
P(cello(38, 9.0, att=1.5), 6.2, 0.6)
melody(7.0, THEME_MIN, 1.0, "piano", 0.5, shift=-12, pan=-0.1)
for t0, m in ((11.0, 62), (13.0, 65), (15.0, 69), (17.0, 67)):
    P(piano(m, 1.5), t0, 0.3, pan=0.25)
for k in range(3):                                   # 手机震动
    P(buzz(), 16.6 + k * 1.0, 0.8, pan=0.2)
P(rumble(6.0), 19.3, 0.8)                            # 潮水漫上来
P(cello(38, 4.5, att=1.2), 19.6, 0.7)
P(cello(45, 4.5, att=1.2), 19.6, 0.4)
melody(20.0, THEME_MIN[:5], 1.0, "piano", 0.45, shift=-12)
P(rumble(5.0), 24.3, 1.0)                            # 镜头沉到水下
P(cello(33, 5.0, att=1.0), 24.5, 0.8)
P(thump(), 27.2, 0.5)                                # 被根拉回去
P(piano(50, 3.0), 29.2, 0.4)
P(piano(57, 2.0), 30.4, 0.3)
P(piano(53, 2.0), 31.6, 0.3)

# ================================================================ 二、为什么不走 33.5–61（钢琴，等待）
prog2 = ["Dm", "Bb", "F", "C", "Dm", "Bb", "Gm", "A"]
bar = 3.3
for i, chn in enumerate(prog2):
    t0 = 33.6 + i * bar
    P(piano(ROOT[chn] + 12, bar * 0.95), t0, 0.45)
    a = ARP[chn]
    for k, m in enumerate([a[0], a[1], a[2], a[3], a[2], a[1]]):
        P(piano(m + 12, 0.5), t0 + k * bar / 6, 0.22, pan=-0.25)
for t0, notes in ((33.6, THEME_MIN[:5]), (40.2, THEME_MIN[5:]), (46.8, THEME_MIN[:5])):
    melody(t0, notes, 0.83, "piano", 0.42, shift=-12, pan=0.1)
P(rain(6.0) * 0.6, 37.5, 0.8)                        # 漫画格①：雨夜
P(knock(), 38.4, 0.4)                                # 轮子掉了
P(rumble(2.4), 48.4, 1.2)                            # 列车驶过
for k in range(14):
    P(chug(), 48.6 + k * 0.15, 0.25, pan=-0.6 + k * 0.09)
for k in range(int((57.0 - 47.5) / 0.5)):            # 站台的钟
    P(tick(k % 2 == 1), 47.5 + k * 0.5, 0.35, pan=0.3)
P(tick(), 57.05, 0.45)
P(tick(True), 57.25, 0.25)
P(cello(38, 3.5, att=0.6), 57.3, 0.45)                # 永远也等不来
P(music_box(74, 3.0), 58.6, 0.35)

# ================================================================ 三、两种恐惧 61–85.5（滴答、压抑、水下）
for k in range(int((85.4 - 61.0) / 0.5)):
    t0 = 61.0 + k * 0.5
    P(tick(k % 2 == 1), t0, 0.45 if t0 < 80 else 0.35, pan=0.25)
prog3 = ["Dm", "Dm", "Bb", "A", "Dm", "Gm", "Bb", "A", "Dm", "Bb", "Gm", "A"]
for i, chn in enumerate(prog3):
    t0 = 61.0 + i * 2.0
    for m in CH[chn]:
        P(piano(m - 12, 1.8), t0, 0.22)
    P(piano(ROOT[chn] + 12, 1.9), t0, 0.4)
P(snap(), 65.3, 0.6)
P(thump(), 65.4, 1.0)                                # 天平“咚”地倒下
P(cello(38, 8.0, att=2.0), 70.0, 0.55)
for i, m in enumerate((77, 76, 74, 72, 70, 69, 67, 65)):   # 日历一页页飞走：下行
    P(music_box(m, 1.4), 70.3 + i * 0.6, 0.22, pan=-0.4)
P(pad([50, 57, 62, 65], 10.0, att=3.0), 75.0, 0.5)
P(cello(34, 5.5, att=1.5), 80.0, 0.6)
P(rumble(5.5), 80.0, 0.55)
for k in range(6):                                   # 心跳
    P(heartbeat(), 80.2 + k * 0.9, 0.3 + 0.06 * k)

# ================================================================ 四、为什么不是现在 85.5–98.5（叮——暖光）
P(snap(), 85.45, 0.5)
for m in (89, 96):
    P(music_box(m, 3.0), 85.5, 0.75)
P(pad(CH["F"] + [72], 12.5, att=1.5, rel=2.0), 85.7, 0.6)
melody(86.6, THEME_MAJ, 0.75, "box", 0.6, pan=0.15)
P(piano(41 + 12, 4.0), 86.6, 0.35)
P(piano(36 + 12, 4.0), 89.6, 0.35)
for i, m in enumerate((65, 69, 72, 74, 77, 81, 84)):       # 立体书一样一个个弹起
    P(pluck(m + 12), 91.9 + i * 0.17, 0.4, pan=-0.6 + i * 0.2)
P(piano(38 + 12, 3.0), 92.6, 0.35)
P(pluck(84), 94.2, 0.45)                              # 对吗？
P(pluck(79), 94.5, 0.45)
P(piano(34 + 12, 3.0), 95.5, 0.35)
for i, m in enumerate((77, 81, 84, 89, 93)):          # 帽子飞到头上
    P(music_box(m, 1.6), 95.5 + i * 0.13, 0.45, pan=0.5 - i * 0.2)

# ================================================================ 五、出逃 98.5–106.5
beat = 0.6
for k in range(int((103.4 - 98.6) / (beat / 2))):     # 拨弦节奏进来
    t0 = 98.6 + k * beat / 2
    chn = ["F", "C", "Dm", "Bb"][int((t0 - 98.6) / 2.4) % 4]
    P(pluck(ARP[chn][k % 4] + 12), t0, 0.32 + 0.1 * ((t0 - 98.6) / 4.8), pan=-0.35)
    if t0 > 100.0:
        P(shaker(), t0, 0.25, pan=0.4)
for i, m in enumerate((72, 74, 77, 79, 81, 84)):      # 每解开一根
    P(music_box(m, 1.6), 98.9 + i * 0.45, 0.5, pan=-0.3 + i * 0.12)
P(swell(1.6), 102.6, 1.2)
P(pad(CH["F"] + [72, 77], 3.6, att=0.6, rel=2.5), 103.9, 1.4)   # 开门：主题绽放
melody(104.0, THEME_MAJ[:5], 0.5, "box", 0.85, pan=0.1)
melody(104.0, THEME_MAJ[:5], 0.5, "piano", 0.5, shift=-12)
P(bass(41, 2.4), 104.0, 0.6)
P(kick(0.8), 104.0, 0.7)

# ================================================================ 六、重活一遍 106.5–129.5（异乡民谣，100 BPM）
P(whistle(1.2), 106.7, 0.7, pan=-0.4)
for k in range(16):
    P(chug(), 106.6 + k * 0.15, 0.22, pan=-0.3 + k * 0.04)
folk_prog = ["F", "C", "Dm", "Bb"]
t_start, t_end = 106.5, 123.5
nb = int((t_end - t_start) / beat)
for k in range(nb):
    t0 = t_start + k * beat
    chn = folk_prog[(k // 4) % 4]
    soft = 119.5 <= t0 < 123.5                       # 摘下工牌：收一点
    for j, m in enumerate(ARP[chn]):                 # 扫弦
        P(pluck(m + 12, bright=0.33), t0 + j * 0.012, 0.18 if not soft else 0.12, pan=-0.3)
    if not soft:
        if k % 4 == 0:
            P(kick(0.7), t0, 0.6)
            P(bass(ROOT[chn] + 12, beat * 1.8), t0, 0.55)
        if k % 4 == 2:
            P(bass(ROOT[chn] + 19, beat * 1.8), t0, 0.45)
        if k % 2 == 1:
            P(jingle(), t0, 0.5, pan=0.35)
        P(shaker(), t0 + beat / 2, 0.25, pan=0.45)
    else:
        if k % 4 == 0:
            P(bass(ROOT[chn] + 12, beat * 3.5), t0, 0.4)
melody(110.3, THEME_MAJ, beat, "reed", 0.75, shift=-12, pan=0.15)
melody(115.1, [(0, 81, 1), (1, 79, 1), (2, 77, 1), (3, 79, 1), (4, 81, 2), (6, 84, 2)], beat, "reed", 0.7, shift=-12, pan=0.15)
melody(119.9, THEME_MAJ[:5], beat * 1.2, "box", 0.5, pan=0.2)
P(knock(), 122.3, 0.5)                                # 盒子合上
# 重新被画出来
P(scratch(1.2), 124.6, 0.6, pan=0.1)
P(scratch(1.4), 125.7, 0.7, pan=-0.1)
P(swell(1.2, 400, 8000), 126.0, 1.4)
P(pad(CH["F"] + [72, 77], 6.0, att=0.4, rel=3.0), 127.1, 1.5)
for k in range(int((129.5 - 127.1) / beat)):
    t0 = 127.1 + k * beat
    chn = ["F", "C", "Bb", "F"][(k // 2) % 4]
    for j, m in enumerate(ARP[chn]):
        P(pluck(m + 12, bright=0.33), t0 + j * 0.012, 0.2, pan=-0.3)
    if k % 2 == 0:
        P(kick(0.8), t0, 0.6)
    P(bass(ROOT[chn] + 12, beat * 0.9), t0, 0.5)
melody(127.1, THEME_MAJ, beat * 0.5, "box", 0.7, pan=0.1)
melody(127.1, THEME_MAJ, beat * 0.5, "reed", 0.55, shift=-12)
P(snap(), 127.1, 0.4)

# ================================================================ 片尾 129.5–136（八音盒收尾）
P(swish(), 131.2, 0.7)
melody(130.0, THEME_MAJ, 0.62, "box", 0.7, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.5), 130.0, 0.6)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 134.2 + i * 0.07, 0.5, pan=-0.3 + i * 0.2)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.8), (6, 0.8), (6.5, 0.9), (33, 0.9), (61, 1.0), (85.3, 1.1), (85.5, 1.0), (98.5, 0.95),
        (104, 1.15), (106.4, 1.15), (106.6, 1.45), (119.3, 1.45), (119.6, 1.0), (123.5, 1.05), (127, 1.25), (129.5, 1.0), (DUR + 1, 1.0)])
M.muffle([(0, 0), (79.5, 0), (84.5, 0.9), (85.4, 0.95), (85.45, 0), (DUR + 1, 0)])
duck = [(0, 1), (85.3, 1), (85.4, 0.15), (85.5, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    import numpy as np
    sr = 44100
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * sr):int((t + 4) * sr)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 136, 4)))

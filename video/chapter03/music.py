"""第三章 · 从游客到旅人（第六稿）—— 配乐（纯代码合成）。

整章同一条旋律、同一个速度，只换乐器和编配，像一条旋律慢慢“长出来”：
零散的单音（并不浪漫）→ 机械的节拍（游客）→ 转成大调、第一次完整弹出（变自信）
→ 以前 / 后来：一层一层往上加（低音 → 分解和弦 → 轻打击乐 → 旋律），以前时只是收轻
→ 手鼓和拨弦（当地生活，最热闹）→ 退回一把吉他（结尾）
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
from synth import (SR, Mix, bass, cello, chug, jingle, kick, knock, music_box, pad, pluck, rain, rumble,  # noqa: E402
                   scratch, shaker, snap, swell, swish, thump, tick, _t)

DUR = 166.0
M = Mix(DUR)
B = 0.6                                   # 一拍（全章同一个速度）


def P(sig, t, vol=1.0, pan=0.0):
    M.place(sig, t, vol, pan)


THEME_MAJ = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 79, 2)]
THEME_MIN = [(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1), (4, 76, 1.5), (5.5, 77, .5), (6, 74, 2)]
CH = {"F": [57, 60, 65], "C": [55, 60, 64], "Dm": [57, 62, 65], "Bb": [58, 62, 65], "Am": [57, 60, 64]}
ROOT = {"F": 41, "C": 36, "Dm": 38, "Bb": 34, "Am": 45}
ARP = {"F": [53, 57, 60, 65], "C": [48, 55, 60, 64], "Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62],
       "Am": [45, 52, 57, 60]}
PROG = ["F", "C", "Dm", "Bb"]


def melody(t0, notes, beat, inst="pluck", vol=1.0, shift=0, pan=0.0, every=1):
    for i, (b, m, d) in enumerate(notes):
        if i % every:
            continue
        t = t0 + b * beat
        if inst == "box":
            P(music_box(m + shift), t, vol, pan)
        else:
            P(pluck(m + shift, length=max(0.6, d * beat * 1.6), bright=0.22), t, vol, pan)


def arp(t0, ch, bar, vol, pan=0.1, pattern=(0, 1, 2, 3, 2, 1)):
    step = bar / len(pattern)
    for j, k in enumerate(pattern):
        P(pluck(ARP[ch][k] + 12, length=1.2, bright=0.24), t0 + j * step, vol, pan)


def noise(length, lo, hi, vol, fade=0.3):
    from scipy.signal import butter, sosfilt
    n, t = _t(length)
    s = sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), np.random.randn(n))
    env = np.clip(t / fade, 0, 1) * np.clip((length - t) / fade, 0, 1)
    return s * env * vol


def murmur(length, vol=0.05):
    """人声嘈杂。"""
    n, t = _t(length)
    s = noise(length, 300, 2500, 1.0, 0.6)
    am = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 3.1 * t) * np.sin(2 * np.pi * 1.3 * t + 1))
    return s * am * vol


def waves(length):
    n, t = _t(length)
    return noise(length, 200, 3000, 0.2, 0.8) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t) ** 2)


def breath(length=1.0):
    n, t = _t(length)
    return noise(length, 400, 2500, 0.08, 0.2) * np.sin(np.pi * t / length) ** 2


def bird(t0, vol=0.6, pan=0.5):
    n, tt = _t(0.12)
    f = 3200 + 1200 * np.sin(np.pi * tt / 0.12)
    P(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.12) * 0.1, t0, vol, pan)


def ding_dong(t0, vol=0.3):
    P(music_box(84, 1.6), t0, vol)
    P(music_box(79, 2.0), t0 + 0.5, vol)


# ================================================================ 片头 0–6
melody(0.4, THEME_MAJ, 0.7, "pluck", 0.55, shift=-12, pan=0.1)
P(pad(CH["F"], 4.5, att=1.5), 0.6, 0.3)
for t0 in (2.1, 2.55, 3.0):
    P(swish(), t0, 0.5)

# ================================================================ 一、并不浪漫 6–41：零散的单音，中间留很多空白
P(cello(38, 9.0, att=2.0), 6.0, 0.25)
P(swish(0.6), 6.3, 0.35)                                           # 自动门
P(murmur(7.0, 0.05), 6.5, 1.0, -0.3)
for k in range(5):
    P(knock(), 6.8 + k * 0.45, 0.04, pan=0.3)                      # 拖箱子的轮子
melody(7.2, THEME_MIN[:5], 1.2, "pluck", 0.32, shift=-12, every=2)  # 单音，一个一个
P(pluck(69, length=2.4, bright=0.18), 10.4, 0.22)                  # 深吸一口气
P(breath(1.4), 9.4, 0.8)
# 台阶 14–19.4
P(swish(0.7), 13.8, 0.4)                                           # 镜头跟着她走
for k in range(6):
    P(chug(0.06), 14.1 + k * 0.18, 0.1, pan=-0.2)
P(knock(), 15.1, 0.25)                                             # 轮子“啪”地掉了
P(tick(), 15.25, 0.2)
for k in range(5):
    P(thump(), 15.8 + k * 0.4, 0.12)                               # 一级一级往上拖
for k in range(3):
    P(thump(), 18.6 + k * 0.45, 0.12)
P(breath(1.0), 17.6, 0.9)
P(pluck(62, length=2.4, bright=0.16), 16.0, 0.22)
P(pluck(65, length=2.4, bright=0.16), 18.4, 0.2)
# 夜路 19.4–24
P(swish(0.7), 19.2, 0.35)
P(cello(36, 5.0, att=1.0), 19.4, 0.35)
P(rumble(3.4), 19.4, 0.25)
for k in range(12):                                                 # 她的脚步越来越快，身后还有一串
    tk = 19.5 + k * (0.34 - k * 0.012)
    P(knock(), tk, 0.11, pan=0.3)
    P(knock(), tk + 0.17, 0.05, pan=-0.6)
P(thump(), 22.8, 0.4)                                              # 关门
P(tick(), 23.05, 0.3)                                              # 锁上
P(breath(1.4), 23.2, 1.0)
# 一个人吃饭 / 看风景 / 陌生的城市 24–34
P(swish(0.7), 23.9, 0.3)
melody(24.3, THEME_MIN, 1.2, "pluck", 0.3, shift=-12, every=2, pan=0.1)
P(pad([45, 52, 57], 9.5, att=2.0, rel=2.0, bright=0.6), 24.0, 0.16)
P(murmur(3.2, 0.04), 24.1, 1.0)
for k in range(4):
    P(music_box(100, 0.3), 24.8 + k * 0.6, 0.05)                   # 碗筷
P(waves(3.6), 27.2, 0.6)
P(rumble(3.6), 30.5, 0.35)                                         # 地铁
for k in range(6):
    P(tick(k % 2 == 1), 30.8 + k * 0.5, 0.1, pan=-0.5 + k * 0.2)
# 餐厅门口 34–41
P(swish(0.7), 33.8, 0.3)
P(murmur(4.4, 0.07), 34.0, 1.0)
P(music_box(91, 0.6), 34.6, 0.18)                                  # “一位？”
P(cello(37, 3.0, att=0.6), 35.8, 0.3)                              # 几个人抬头看过来
P(pluck(57, length=2.6, bright=0.14), 37.0, 0.25)                  # 压低帽檐
P(pluck(60, length=3.0, bright=0.14), 38.6, 0.2)
P(pluck(65, length=3.0, bright=0.14), 39.8, 0.18)

# ================================================================ 二、游客 41–60：机械的节拍
t = 41.0
while t < 53.9:
    P(kick(0.7), t, 0.22)
    P(shaker(), t + 0.25, 0.14, pan=0.3)
    t += 0.5
for i in range(13):                                                 # 呆板的四分音符和弦
    ch = ["C", "F"][i % 2]
    for j in range(4):
        P(pluck(ARP[ch][j % 4] + 12, length=0.5, bright=0.2), 41.0 + i * 1.0 + j * 0.25, 0.1, -0.2)
P(murmur(6.0, 0.06), 41.0, 1.0)
for k in range(3):                                                  # 快门 + 打勾
    tk = 47.0 + k * 2.3
    P(snap(), tk + 0.9, 0.35)
    P(scratch(0.2), tk + 1.2, 0.25, pan=0.5)
    P(scratch(0.2), tk + 1.8, 0.25, pan=0.5)
P(pad([45, 52, 57], 6.0, att=1.2, rel=1.2, bright=0.8), 54.0, 0.28)  # 夜里翻相册
for k in range(10):
    P(tick(), 54.3 + k * 0.28, 0.06)
P(pluck(64, length=2.4, bright=0.16), 57.6, 0.25)                  # 想不起来是哪里
P(pluck(62, length=2.4, bright=0.16), 58.6, 0.2)

# ================================================================ 三、变自信 60–74：同一段旋律，转成大调
P(swell(2.4, 300, 6000), 59.6, 0.45)
P(pad(CH["F"] + [72], 7.5, att=2.0, rel=2.0, bright=1.6), 60.0, 0.32)
for i, ch in enumerate(PROG):
    arp(60.0 + i * 2.4, ch, 2.4, 0.13 + 0.03 * i)
melody(60.6, THEME_MAJ, B, "pluck", 0.36, shift=-12, pan=0.1)      # 第一次完整地弹出来
P(swish(0.6), 63.5, 0.3)
P(noise(3.0, 250, 1400, 0.12, 1.0), 63.8, 1.0)                     # 山坡上的风
for i, m in enumerate((77, 81, 84, 89)):                            # 推起帽檐
    P(music_box(m, 1.6), 65.0 + i * 0.08, 0.28)
# 同一家餐厅：这一次很暖
P(murmur(7.0, 0.05), 67.0, 1.0)
P(music_box(91, 0.6), 67.4, 0.2)
for i, ch in enumerate(["F", "C", "Dm", "C"]):
    P(pluck(ROOT[ch] + 12, length=2.0, bright=0.2), 67.0 + i * 1.8, 0.22, -0.2)
    arp(67.0 + i * 1.8, ch, 1.8, 0.16)
P(music_box(100, 0.5), 72.2, 0.3)                                  # 碰杯
P(music_box(103, 0.5), 72.35, 0.25)

# ================================================================ 四、以前 / 后来 74–106：一层一层往上加
BAR = 2.0
for i in range(16):
    t0 = 74.0 + i * BAR
    k4 = i // 4                                                     # 第几组
    after = (i % 4) >= 2                                            # 每组后半段是“后来”
    ch = PROG[i % 4]
    lvl = (0.55 if not after else 1.0)
    arp(t0, ch, BAR, 0.1 + 0.05 * lvl + 0.01 * k4)                  # 分解和弦一直在，以前只是收轻
    if k4 >= 1 or (k4 == 0 and after):                              # 第一组“后来”起：低音
        P(bass(ROOT[ch] + 12, BAR * 0.95), t0, 0.22 * lvl)
    if k4 >= 2 and (after or k4 == 3):                              # 第三组“后来”起：轻打击乐
        for j in range(4):
            P(kick(0.6), t0 + j * 0.5, 0.14 * lvl)
            P(jingle(), t0 + j * 0.5 + 0.25, 0.06 * lvl, pan=0.4)
    if not after and i % 4 == 0:
        P(pad(CH[ch], 4.0, att=0.8, rel=0.8, bright=0.6), t0, 0.12)
melody(98.2, THEME_MAJ, B, "pluck", 0.42, shift=-12, pan=0.15)     # 第四组“后来”：旋律回来了
for k4 in range(4):
    P(swish(0.4), 74.0 + k4 * 8 + 3.9, 0.25)                        # 叠化到“后来”
for k in range(4):
    P(tick(k % 2 == 1), 74.6 + k * 0.6, 0.06)                       # 看着返程时间
ding_dong(86.1, 0.25)                                               # 最后登机
for k in range(8):
    P(knock(), 86.2 + k * 0.28, 0.07, pan=-0.3 + k * 0.08)          # 一路跑来
P(snap(), 92.2, 0.35)                                               # 拉链崩开
P(swish(0.5), 96.6, 0.35)                                           # 背包甩上肩
P(scratch(0.4), 102.0, 0.2)                                         # 展开纸地图

# ================================================================ 五、走进当地人的生活 106–143：手鼓、拨弦
b2 = 0.5
for k in range(int((143.0 - 106.0) / b2)):
    t0 = 106.0 + k * b2
    g = 0.8 if t0 < 111 else 1.0
    if k % 2 == 0:
        P(kick(0.6), t0, 0.2 * g)
    P(jingle(), t0 + b2 / 2, (0.07 if k % 4 else 0.12) * g, pan=0.4)
for i in range(18):
    ch = PROG[i % 4]
    t0 = 106.0 + i * 2.0
    P(bass(ROOT[ch] + 12, 1.9), t0, 0.24)
    arp(t0, ch, 2.0, 0.15, pattern=(0, 1, 2, 3, 2, 1, 2, 3))
melody(106.4, THEME_MAJ, B, "pluck", 0.3, shift=-12, every=2)
for k in range(3):
    P(breath(1.0), 107.0 + k * 0.9, 0.5)                           # 深吸一口气
P(swish(0.6), 112.1, 0.4)                                          # 换衣服的帘子
for i, m in enumerate((84, 88, 91)):
    P(music_box(m, 1.2), 114.6 + i * 0.1, 0.28)                    # 转一圈
P(murmur(6.0, 0.08), 117.0, 1.0)                                   # 菜市场
for k in range(5):
    P(knock(), 119.4 + k * 0.5, 0.08)
# 切菜：大小不一 → 奶奶示范，又快又匀 → 她自己，慢但整齐
for tk in (0.1, 0.55, 0.95, 1.4):
    P(knock(), 123.0 + tk, 0.18, pan=-0.2)
P(thump(), 124.0, 0.12)                                            # 一块滚到案板外
tk = 1.85
while tk < 3.3:
    P(knock(), 123.0 + tk, 0.14, pan=-0.1)
    tk += 0.13
for tk in (3.5, 4.0, 4.5):
    P(knock(), 123.0 + tk, 0.16, pan=-0.1)
for i, m in enumerate((84, 88, 91)):
    P(music_box(m, 1.0), 127.0 + i * 0.07, 0.22)                   # 竖大拇指
P(rain(1.8) * 0.2, 127.4, 0.8)                                      # 滋啦
P(swish(0.4), 128.2, 0.3)                                          # 颠锅
for k in range(5):
    P(music_box(98 + (k % 2) * 3, 0.3), 129.4 + k * 0.32, 0.08)    # 院子里的碗筷
P(thump(), 132.6, 0.4)                                             # 射击
P(thump(), 134.2, 0.4)
P(snap(), 135.0, 0.4)                                              # 击掌
for i, m in enumerate((84, 88, 91, 96)):
    P(music_box(m, 1.0), 135.1 + i * 0.07, 0.22)
for k in range(5):
    bird(137.4 + k * 0.9)
P(swell(1.0, 400, 3000), 137.6, 0.25)                              # 掀开蒸笼

# ================================================================ 六、旅人 143–160
P(swell(0.8, 800, 9000), 143.2, 0.35)                              # 梦一样的气泡
P(pad(CH["F"] + [72, 77], 2.8, att=0.8, rel=0.6, bright=2.2), 143.2, 0.22)
P(snap(), 145.8, 0.45)                                             # 啵！
for i, m in enumerate((96, 93, 89, 86, 84)):
    P(music_box(m, 1.0), 145.85 + i * 0.07, 0.25)
b3 = 0.5
for k in range(int((150.0 - 146.0) / b3)):                         # 热闹起来
    t0 = 146.0 + k * b3
    P(kick(0.7), t0, 0.24)
    P(jingle(), t0 + b3 / 2, 0.12, pan=0.4)
for i, ch in enumerate(["F", "C"]):
    P(bass(ROOT[ch] + 12, 1.9), 146.0 + i * 2.0, 0.26)
    arp(146.0 + i * 2.0, ch, 2.0, 0.17, pattern=(0, 1, 2, 3, 2, 1, 2, 3))
P(murmur(4.0, 0.08), 146.0, 1.0)
for k in range(3):
    P(scratch(0.15), 146.4 + k * 0.9, 0.12, pan=0.6)                # 鸡扑腾
# 热闹退去，只剩一把吉他
P(pad(CH["F"] + [72], 10.0, att=2.0, rel=3.0, bright=1.2), 150.0, 0.26)
melody(150.6, THEME_MAJ, 0.75, "pluck", 0.42, shift=-12, pan=0.1)
P(swell(1.4, 300, 5000), 151.3, 0.25)                              # 那张明信片
P(music_box(91, 2.4), 151.6, 0.22)
for k in range(4):
    bird(155.0 + k * 1.1, 0.4, -0.4)
P(swell(3.0, 200, 3000), 156.6, 0.25)                              # 镜头升高
P(pluck(77, length=3.0, bright=0.18), 156.8, 0.25)

# ================================================================ 片尾 160–166
P(swish(), 161.6, 0.45)
melody(160.4, THEME_MAJ, 0.6, "box", 0.42, pan=0.1)
P(pad(CH["F"], 4.0, att=1.0, rel=2.0), 160.4, 0.45)
for i, m in enumerate((65, 69, 72, 77)):
    P(music_box(m, 3.5), 163.8 + i * 0.07, 0.42, pan=-0.3 + i * 0.2)

# ---------------------------------------------------------------- 混音
M.gain([(0, 0.85), (6, 1.0), (41, 0.95), (60, 0.88), (67, 1.0), (106, 0.85), (150, 1.0), (160, 0.5), (DUR + 1, 0.5)])
M.muffle([(0, 0), (DUR + 1, 0)])
duck = [(0, 1), (DUR + 1, 1)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = M.render(os.path.join(HERE, "out", "music.wav"), duck=duck)
    print(" ".join(f"{int(t)}:{20 * np.log10(np.sqrt((out[int(t * SR):int((t + 4) * SR)] ** 2).mean()) + 1e-9):.0f}"
                   for t in range(0, 166, 4)))

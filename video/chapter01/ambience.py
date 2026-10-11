"""第一章 · 出逃 —— 环境音（和画面对应的声音），叠在配乐下面。纯代码合成，时间对齐 ch01.py 的最终时间轴。

灰色城市的脚步 → 咖啡馆 / 办公室 / 手机震动 → 地缝渗水、根被拉住 → 派对、KTV → 散场、霓虹灯一个个熄灭
→ 车站和机场 → 被淹没（水下）→ 猛地吸一口气、水退去 → 立体书里的风、浪、鸟 → 解开根、拉箱子
→ 书里的旅途：机舱、小火车、灯笼下的人声、长桌、湖上的桨声、晨鸟 → 推开门，外面的世界涌进来
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "series"))
from synth import SR, Mix, _t, knock, swish, thump, tick  # noqa: E402
from scipy.signal import butter, sosfilt  # noqa: E402

DUR = 121.0
A = Mix(DUR)
R = np.random.RandomState(11)


def P(sig, t, vol=1.0, pan=0.0):
    A.place(sig, t, vol, pan)


def bed(length, lo, hi, vol, fade=0.6, am=0.0, am_f=0.3):
    """一段滤过的噪声底：城市、人声、空调、水……am 让它有一点起伏。"""
    n, t = _t(length)
    s = sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), R.randn(n))
    s /= np.max(np.abs(s)) + 1e-9
    env = np.clip(t / fade, 0, 1) * np.clip((length - t) / fade, 0, 1)
    if am:
        env *= 1 - am + am * (0.5 + 0.5 * np.sin(2 * np.pi * am_f * t + R.uniform(0, 6)))
    return s * env * vol


def step(vol=1.0, bright=1.0):
    """一声脚步：低低的一下 + 一点鞋底摩擦。"""
    n, t = _t(0.18)
    s = np.sin(2 * np.pi * 90 * t) * np.exp(-t / 0.03)
    s += sosfilt(butter(2, [800, 3000 * bright], btype="band", fs=SR, output="sos"), R.randn(n)) * np.exp(-t / 0.02) * 0.4
    return s * vol


def clink(f=2400, vol=1.0):
    """杯子、碗碟轻轻一碰。"""
    n, t = _t(0.6)
    s = sum(np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) for r, d in ((1, 0.18), (2.7, 0.08), (4.1, 0.05)))
    return s * vol * 0.4


def key_click(vol=1.0):
    n, t = _t(0.05)
    return sosfilt(butter(2, [1500, 6000], btype="band", fs=SR, output="sos"), R.randn(n)) * np.exp(-t / 0.008) * vol


def buzz_phone(length=0.6, vol=1.0):
    """手机震动：低低的嗡嗡声，一顿一顿的。"""
    n, t = _t(length)
    s = np.sign(np.sin(2 * np.pi * 160 * t)) * 0.3 + np.sin(2 * np.pi * 160 * t)
    gate = (np.sin(2 * np.pi * 5 * t) > -0.2).astype(float)
    return sosfilt(butter(2, 900, btype="low", fs=SR, output="sos"), s) * gate * np.exp(-t / 2) * vol * 0.5


def chirp(f0, f1, length=0.12, vol=1.0):
    """一声鸟叫。"""
    n, t = _t(length)
    f = np.linspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.sin(np.pi * t / length) ** 2 * vol * 0.35


def birds(t0, length, density=1.2, vol=0.06, pan=0.3):
    t = t0
    while t < t0 + length:
        base = R.uniform(2600, 4200)
        for j in range(R.randint(1, 4)):
            P(chirp(base, base * R.uniform(1.1, 1.5), R.uniform(0.06, 0.14)), t + j * 0.13, vol, pan + R.uniform(-0.4, 0.4))
        t += R.uniform(0.6, 1.6) / density


def bubbles(t0, length, vol=0.05):
    t = t0
    while t < t0 + length:
        n, tt = _t(0.08)
        f = R.uniform(400, 900)
        s = np.sin(2 * np.pi * (f + 3000 * tt) * tt) * np.exp(-tt / 0.03)
        P(s, t, vol, R.uniform(-0.5, 0.5))
        t += R.uniform(0.15, 0.6)


def creak(length=1.2, vol=1.0):
    """门轴吱呀一声。"""
    n, t = _t(length)
    f = 180 + 120 * np.sin(np.pi * t / length)
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    s = sosfilt(butter(2, [300, 2500], btype="band", fs=SR, output="sos"), saw)
    return s * np.sin(np.pi * t / length) * vol * 0.3


def wheels(length, vol=1.0):
    """行李箱轮子在地上滚。"""
    n, t = _t(length)
    s = sosfilt(butter(2, [80, 600], btype="band", fs=SR, output="sos"), R.randn(n))
    s /= np.max(np.abs(s)) + 1e-9
    s *= 0.7 + 0.3 * (np.sin(2 * np.pi * 9 * t) > 0)
    return s * np.clip(t / 0.2, 0, 1) * np.clip((length - t) / 0.3, 0, 1) * vol


def train_clack(t0, length, vol=0.12):
    t = t0
    while t < t0 + length:
        P(step(1.0, 0.6), t, vol, -0.2)
        P(step(0.8, 0.6), t + 0.12, vol, -0.2)
        t += 0.8


# ================================================================ 1 灰色的城市，每天走同一条路 6–10
P(bed(4.2, 120, 900, 1.0, am=0.3), 6.0, 0.05)                     # 远处的车流
for k in range(8):
    P(step(), 6.2 + k * 0.48, 0.07, -0.2 + 0.05 * (k % 2))
# ================================================================ 2 每一条街都记得某一次难过 10–24
P(bed(5.0, 300, 2000, 1.0, am=0.5, am_f=0.7), 10.0, 0.05)          # ① 咖啡馆里低低的人声
P(clink(2600), 11.0, 0.12, 0.3)
P(bed(0.5, 200, 1200, 1.0, fade=0.1), 11.6, 0.1, -0.3)            # 对面的人推开椅子
P(clink(2200), 13.2, 0.08, 0.2)
P(bed(5.0, 60, 400, 1.0, am=0.1), 15.0, 0.05)                      # ② 办公室：空调的嗡嗡声
for k in range(26):
    P(key_click(), 15.3 + k * 0.17 + R.uniform(0, 0.06), 0.025, 0.2)
P(bed(4.0, 80, 600, 1.0), 20.0, 0.03)                              # ③ 安静的房间
P(buzz_phone(0.6), 20.6, 0.1)
P(buzz_phone(0.6), 21.3, 0.08)
# ================================================================ 3–4 潮水漫上来；根把她拉回去 24–33
P(bed(5.0, 1500, 6000, 1.0, am=0.6, am_f=2.2), 24.0, 0.05, 0.1)   # 地缝里渗出来的水
bubbles(25.0, 4.0, 0.04)
P(bed(4.0, 40, 300, 1.0, am=0.4), 29.0, 0.07)                      # 土里低低的声音
P(bed(0.8, 100, 500, 1.0, fade=0.2), 30.4, 0.12)                   # 根缠紧
# ================================================================ 5 把日子填满 33–47
for k in range(4):                                                 # 日程本一页页翻
    P(swish(0.3), 33.6 + k * 1.1, 0.05, 0.3)
P(bed(8.5, 200, 2500, 1.0, am=0.4, am_f=1.1), 38.5, 0.07)          # 包厢里的人声和笑
for k in range(6):
    P(clink(R.uniform(2000, 2800)), 39.0 + k * 1.3 + R.uniform(0, 0.4), 0.08, R.uniform(-0.5, 0.5))
P(bed(1.2, 300, 3000, 1.0, fade=0.3), 44.6, 0.1)                   # 一阵欢呼
# ================================================================ 6 散场以后 47–52
P(bed(5.0, 60, 300, 1.0), 47.0, 0.03)                              # 一下子空下来的房间
for k in range(6):                                                 # 霓虹灯一个字一个字熄灭
    P(tick(k % 2 == 1), 47.6 + k * 0.45, 0.08, 0.3)
# ================================================================ 7 迈不出那一步 52–60
P(bed(8.0, 250, 1800, 1.0, am=0.4, am_f=0.5), 52.0, 0.05)          # 车站 / 机场的人声
for f0, t0 in ((660, 52.4), (520, 52.9)):                          # 车站广播前的提示音
    n, tt = _t(0.9)
    P(np.sin(2 * np.pi * f0 * tt) * np.exp(-tt / 0.4) * 0.3, t0, 0.12)
for k in range(6):                                                 # 转身往回走
    P(step(), 54.6 + k * 0.42, 0.06, 0.2)
train_clack(55.2, 2.4, 0.08)                                       # 火车开走
# ================================================================ 8 被吞没：像在水下 60–68
P(bed(8.0, 40, 350, 1.0, am=0.3, am_f=0.2), 60.0, 0.06)             # 水下闷闷的声音
bubbles(60.4, 6.0, 0.05)
# ================================================================ 9 “啪”：水退去，猛地吸一口气 68–73
P(bed(1.0, 400, 5000, 1.0, fade=0.15), 68.0, 0.14)                 # 水哗地退下去
P(bed(0.5, 800, 4000, 1.0, fade=0.1), 68.35, 0.1)                  # 吸一口气
for k in range(5):                                                 # 便利贴被风吹正
    P(swish(0.25), 69.4 + k * 0.5, 0.03, -0.4 + k * 0.2)
# ================================================================ 10 立体书里的世界 73–79
birds(73.5, 5.0, 1.0, 0.05)
P(bed(5.0, 300, 3000, 1.0, am=0.5, am_f=0.25), 73.5, 0.03)
# ================================================================ 11–12 草帽；解开根，拉出行李箱 79–86
P(swish(0.5), 79.2, 0.08)
for k in range(4):
    P(bed(0.25, 100, 700, 1.0, fade=0.05), 82.4 + k * 0.5, 0.08)   # 一根根解开
P(wheels(1.2), 84.4, 0.06)
# ================================================================ 13–17 书里的旅途 86–110（隔着一层纱，轻一点）
P(bed(4.5, 60, 500, 1.0), 86.2, 0.05)                              # 机舱的嗡嗡声
train_clack(88.6, 2.2, 0.05)                                       # 换乘小火车
P(bed(4.5, 300, 2200, 1.0, am=0.5, am_f=0.9), 91.0, 0.04)          # 灯笼下的人声
for k in range(4):
    P(clink(R.uniform(1800, 2600)), 92.2 + k * 0.7, 0.06, R.uniform(-0.5, 0.5))
birds(93.6, 1.4, 2.0, 0.05, pan=0.5)                                # 热气变成小鸟飞走
for k in range(3):                                                 # 湖上划桨
    P(bed(0.6, 300, 2500, 1.0, fade=0.15), 95.4 + k * 1.3, 0.06, -0.2)
for k in range(5):                                                 # 踩着当地人的脚印走
    P(step(0.8), 98.2 + k * 0.5, 0.04)
birds(103.0, 7.0, 0.8, 0.04)                                       # 晨光
# ================================================================ 推开门，颜色涌进来 110–115
P(creak(1.2), 110.6, 0.08, 0.3)
P(bed(4.0, 300, 4000, 1.0, am=0.3), 111.2, 0.05)                   # 外面的世界涌进来
birds(111.4, 3.6, 1.6, 0.06)
P(wheels(2.2), 112.2, 0.07)

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    A.render(os.path.join(HERE, "out", "ambience.wav"), wet=0.25)
    print("ok")

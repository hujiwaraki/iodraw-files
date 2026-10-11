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


# 第二版：太吵了 —— 去掉持续的人声、车流、空调、包厢这些底噪，只留几个和画面动作对得上的轻轻的点。
# ================================================================ 1 灰色的城市，每天走同一条路 6–10
for k in range(6):
    P(step(), 6.3 + k * 0.6, 0.04, -0.2 + 0.05 * (k % 2))
# ================================================================ 2 每一条街都记得某一次难过 10–24
P(clink(2600), 11.0, 0.06, 0.3)                                    # 咖啡杯轻轻一碰
P(buzz_phone(0.6), 20.6, 0.06)                                     # 手机震了一下
# ================================================================ 3 潮水漫上来 24–29
P(bed(4.6, 1500, 6000, 1.0, am=0.6, am_f=2.2), 24.2, 0.025, 0.1)  # 细细的渗水声
# ================================================================ 6 散场以后 47–52
for k in range(6):                                                 # 霓虹灯一个字一个字熄灭
    P(tick(k % 2 == 1), 47.6 + k * 0.45, 0.04, 0.3)
# ================================================================ 7 迈不出那一步 52–60
for k in range(5):                                                 # 转身往回走
    P(step(), 54.6 + k * 0.5, 0.035, 0.2)
# ================================================================ 8 被吞没：像在水下 60–68
bubbles(60.6, 4.5, 0.025)
# ================================================================ 9 “啪”：水退去 68–73
P(bed(1.0, 400, 5000, 1.0, fade=0.15), 68.0, 0.06)
# ================================================================ 10 立体书里的世界 73–79
birds(74.0, 4.5, 0.6, 0.03)
# ================================================================ 12 拉出行李箱 82–86
P(wheels(1.2), 84.4, 0.03)
# ================================================================ 书里的旅途 86–110（隔着一层纱）
for k in range(3):                                                 # 湖上划桨
    P(bed(0.6, 300, 2500, 1.0, fade=0.15), 95.6 + k * 1.4, 0.03, -0.2)
birds(104.0, 5.0, 0.5, 0.025)                                      # 晨光
# ================================================================ 推开门 110–115
P(creak(1.2), 110.6, 0.05, 0.3)
birds(111.6, 3.2, 0.9, 0.035)
P(wheels(2.0), 112.4, 0.035)

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    A.render(os.path.join(HERE, "out", "ambience.wav"), wet=0.25)
    print("ok")

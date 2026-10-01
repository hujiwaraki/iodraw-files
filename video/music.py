"""纯代码合成配乐：八音盒 / 钢琴 / 拨弦 / 铺底 / 轻打击乐。96 BPM，F 大调，62.5 秒。"""
import os
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
DUR = 62.5
BAR = 2.5
BEAT = BAR / 4
N = int(SR * (DUR + 0.01))
L = np.zeros(N)
R = np.zeros(N)
rs = np.random.RandomState(1)


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(sig, t, vol=1.0, pan=0.0, gate=None):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[:N - i] * vol
    if gate is not None:
        g = int((gate - t) * SR)
        if 0 < g < len(sig):
            fade = min(int(0.02 * SR), len(sig) - g)
            sig = sig.copy()
            sig[g:g + fade] *= np.linspace(1, 0, fade)
            sig[g + fade:] = 0
    gl = np.cos((pan + 1) * np.pi / 4)
    gr = np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(sig)] += sig * gl
    R[i:i + len(sig)] += sig * gr


def env_tt(n, att=0.004):
    a = max(1, int(att * SR))
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a)
    return e


def music_box(m, length=2.2):
    f = mtof(m)
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for ratio, amp, tau in ((1, 1.0, 1.1), (2.0, 0.18, 0.5), (3.0, 0.08, 0.3), (5.4, 0.12, 0.12), (8.9, 0.05, 0.05)):
        s += amp * np.sin(2 * np.pi * f * ratio * t + rs.uniform(0, 6)) * np.exp(-t / tau)
    return s * env_tt(n, 0.002) * 0.35


def piano(m, dur, length=None):
    f = mtof(m)
    length = length or dur + 1.2
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    B = 0.00035
    for k in range(1, 10):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > SR / 2.2:
            break
        tau = 2.4 / (1 + 0.5 * k) * (220 / max(f, 110)) ** 0.3
        s += (1 / k ** 1.4) * np.sin(2 * np.pi * fk * t + rs.uniform(0, 6)) * np.exp(-t / tau)
    rel = np.ones(n)
    d = int(dur * SR)
    if d < n:
        rel[d:] = np.exp(-(np.arange(n - d) / SR) / 0.25)
    ham = rs.randn(n) * np.exp(-t / 0.006) * 0.08
    return (s * rel + ham) * env_tt(n, 0.003) * 0.3


def pluck(m, length=0.9):
    f = mtof(m)
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k in range(1, 12):
        if f * k > SR / 2.2:
            break
        s += (1 / k) * np.sin(np.pi * k * 0.27) * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (3 + 2.2 * k))
    return s * env_tt(n, 0.002) * 0.4


def pad(ms, dur, att=1.0, rel=1.2):
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for m in ms:
        f = mtof(m)
        for det in (-0.08, 0.0, 0.08):
            fd = f * 2 ** (det / 12)
            for k in range(1, 8):
                s += (1 / k ** 1.6) * np.sin(2 * np.pi * fd * k * t + rs.uniform(0, 6))
    e = np.clip(t / att, 0, 1) ** 2
    e *= np.where(t > dur, np.exp(-(t - dur) / (rel / 3)), 1)
    lfo = 1 + 0.08 * np.sin(2 * np.pi * 0.3 * t)
    return s * e * lfo * 0.03


def bass(m, dur):
    f = mtof(m)
    n = int((dur + 0.15) * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.1 * np.sin(6 * np.pi * f * t)
    e = np.exp(-t / (dur * 0.9)) * np.clip((dur + 0.15 - t) / 0.15, 0, 1)
    return s * e * env_tt(n, 0.006) * 0.35


def kick(vol=1.0):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 90 * np.exp(-t / 0.04)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.12) * 0.8 * vol


def bandnoise(length, lo, hi, tau):
    n = int(length * SR)
    t = np.arange(n) / SR
    sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, rs.randn(n)) * np.exp(-t / tau)


def snap():
    return bandnoise(0.25, 1200, 5000, 0.05) * 0.5


def shaker():
    return bandnoise(0.08, 6000, 14000, 0.018) * 0.3


def swell(length=0.6):
    n = int(length * SR)
    t = np.arange(n) / SR
    sos = butter(2, [800, 9000], btype="band", fs=SR, output="sos")
    return sosfilt(sos, rs.randn(n)) * (t / length) ** 3 * 0.25


def wind(length):
    n = int(length * SR)
    t = np.arange(n) / SR
    sos = butter(2, [250, 1400], btype="band", fs=SR, output="sos")
    e = np.sin(np.pi * t / length) ** 2 * (1 + 0.5 * np.sin(2 * np.pi * 0.7 * t))
    return sosfilt(sos, rs.randn(n)) * e * 0.12


def thump():
    n = int(0.8 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.12) * 0.7 +
            bandnoise(0.8, 200, 1500, 0.03) * 0.5)


CH = {"F": [57, 60, 65], "C": [55, 60, 64], "Dm": [57, 62, 65], "Bb": [58, 62, 65], "Gm": [55, 58, 62]}
ROOT = {"F": 41, "C": 36, "Dm": 38, "Bb": 46, "Gm": 43}
ARP = {"F": [53, 57, 60, 65], "C": [48, 55, 60, 64], "Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62], "Gm": [43, 50, 55, 58]}
PROG = ["F", "C", "Dm", "Bb", "F", "C", "Dm", "Bb", "F", "C", "Bb", "Dm", "Bb", "Dm", "Bb", "Gm", "C", "Dm", "Bb",
        "Bb", "C", "F", "Dm", "Bb", "F"]

THEME_A = [[(0, 81, 1), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3, 77, 1)], [(0, 76, 1.5), (1.5, 77, .5), (2, 79, 2)]]
THEME_B = [[(0, 77, 1), (1, 81, .5), (1.5, 79, .5), (2, 77, 1), (3, 74, 1)], [(0, 74, 1.5), (1.5, 72, .5), (2, 74, 2)]]


def mel(bar, notes, inst="box", vol=1.0, shift=0, pan=0.0, gate=None):
    for b, m, d in notes:
        t = at(bar, b)
        if inst == "box":
            place(music_box(m + shift), t, vol, pan, gate)
        elif inst == "piano":
            place(piano(m + shift, d * BEAT), t, vol, pan, gate)
        elif inst == "pluck":
            place(pluck(m + shift), t, vol, pan, gate)


def compose():
    # ---- 第一乐章 出发 (bars 0-5)
    mel(0, THEME_A[0], "box", 0.9, pan=0.1)
    mel(1, THEME_A[1], "box", 0.9, pan=0.1)
    mel(2, THEME_B[0], "box", 0.9, pan=0.1)
    mel(3, THEME_B[1], "box", 0.9, pan=0.1)
    for bar in range(0, 4):
        for k in range(4):
            place(music_box(ARP[PROG[bar]][k] + 12), at(bar, k), 0.35, pan=-0.3)
    for bar in (3,):
        place(piano(ROOT[PROG[bar]] + 12, BAR), at(bar), 0.5)
    for i, m in enumerate([65, 69, 72, 77, 81, 84, 89]):           # 开门 → 弹出的世界
        place(music_box(m), 7.05 + i * 0.05, 0.55, pan=-0.6 + i * 0.2)
    for bar in (4, 5):
        mel(bar, THEME_A[bar - 4], "box", 0.85, pan=0.1)
        place(piano(ROOT[PROG[bar]] + 12, BAR), at(bar), 0.55)
        for k in range(8):
            place(pluck(ARP[PROG[bar]][k % 4] + 12), at(bar, k * 0.5), 0.45, pan=-0.35)
        for k in range(8):
            place(shaker(), at(bar, k * 0.5), 0.25 + 0.15 * (k % 2), pan=0.4)
    for i, m in enumerate([77, 81, 84, 89, 93]):                     # 转圈换装
        place(music_box(m), 12.35 + i * 0.09, 0.5, pan=0.5 - i * 0.25)
    # ---- 第二乐章 不敢抵达的地方 (bars 6-7)
    for bar in (6, 7):
        mel(bar, THEME_B[bar - 6], "piano", 0.75, shift=-12)
        place(pad(CH[PROG[bar]], BAR, att=0.8), at(bar), 0.9)
        place(piano(ROOT[PROG[bar]] + 12, BAR), at(bar), 0.5)
        for k in range(4):
            place(piano(ARP[PROG[bar]][k] + 12, BEAT * 0.9), at(bar, k + 0.5 * (k % 2)), 0.25, pan=-0.3)
    place(swell(0.6), 19.4, 1.0)
    # ---- 第三乐章 同路人 (bars 8-10)，27.5 秒骤停
    G = 27.5
    upbeat = [[(0, 81, .5), (.5, 81, .5), (1, 84, .5), (1.5, 81, .5), (2, 79, .5), (2.5, 77, .5), (3, 79, 1)],
              [(0, 76, .5), (.5, 76, .5), (1, 79, .5), (1.5, 76, .5), (2, 74, .5), (2.5, 72, .5), (3, 74, 1)],
              [(0, 74, .5), (.5, 77, .5), (1, 81, .5), (1.5, 84, .5), (2, 82, .5), (2.5, 81, .5), (3, 79, .5), (3.5, 84, .5)]]
    for j, bar in enumerate((8, 9, 10)):
        mel(bar, upbeat[j], "box", 0.8, pan=0.15, gate=G)
        mel(bar, upbeat[j], "pluck", 0.6, shift=-12, pan=-0.15, gate=G)
        chords = [PROG[bar]] * 2 if bar != 10 else ["Bb", "C"]
        for half, chn in enumerate(chords):
            for k in range(4):
                place(bass(ROOT[chn] + (12 if k % 2 else 0), BEAT * 0.45), at(bar, half * 2 + k * 0.5), 0.75, gate=G)
            for k in range(4):
                place(pluck(ARP[chn][k % 4] + 12), at(bar, half * 2 + k * 0.5), 0.38, pan=-0.45, gate=G)
            place(pad(CH[chn], BAR / 2 - 0.1, att=0.05, rel=0.2), at(bar, half * 2), 0.6, gate=G)
        for k in range(4):
            if k in (0, 2):
                place(kick(), at(bar, k), 0.9, gate=G)
            else:
                place(snap(), at(bar, k), 0.75, pan=0.1, gate=G)
        place(kick(0.6), at(bar, 2.5), 0.7, gate=G)
        for k in range(8):
            place(shaker(), at(bar, k * 0.5), 0.3 + 0.2 * (k % 2), pan=0.45, gate=G)
    for tc in (21.875, 23.75, 25.625):                                # 镜头切换
        place(swell(0.35), tc - 0.35, 0.8)
    for m in (100, 103):                                              # 碰杯
        place(music_box(m, 1.0), 22.475, 0.5, pan=0.2)
    # ---- 纸鸟 (bars 11-12)
    for tb, m, pn in ((28.1, 84, -0.5), (28.7, 81, 0.5), (29.3, 77, 0.7)):
        place(music_box(m, 3.5), tb, 0.85, pan=pn)
        place(music_box(m - 12, 3.5), tb, 0.3, pan=pn)
    place(pad(CH["Dm"], 3.2, att=1.5, rel=1.5), 28.6, 0.6)
    place(music_box(74, 3.0), 30.6, 0.5)
    # ---- 第四乐章 回忆 / 那个人 (bars 13-18)
    for bar in (13, 14):
        a = ARP[PROG[bar]]
        seq = [a[0], a[1], a[2], a[3], a[3] + 4 if PROG[bar] == "Dm" else a[3] + 3, a[3], a[2], a[1]]
        for k, m in enumerate(seq):
            place(piano(m, BEAT * 0.5), at(bar, k * 0.5), 0.35, pan=-0.25)
        mel(bar, THEME_B[bar - 13], "piano", 0.55)
        mel(bar, THEME_B[bar - 13], "box", 0.18, shift=12, pan=0.5)
    m15 = [[(0, 70, 1.5), (1.5, 69, .5), (2, 67, 2)], [(0, 67, 1), (1, 72, 1), (2, 70, 1), (3, 69, 1)]]
    for j, bar in enumerate((15, 16)):
        for m in CH[PROG[bar]]:
            place(piano(m - 12, BAR * 0.9), at(bar), 0.3)
        place(piano(ROOT[PROG[bar]] + 12, BAR), at(bar), 0.45)
        mel(bar, m15[j], "piano", 0.5)
    m17 = [[(0, 62, 2), (2, 65, 1), (3, 69, 1)], [(0, 70, 2), (2, 69, 1), (3, 65, 1)]]
    for j, bar in enumerate((17, 18)):
        mel(bar, m17[j], "piano", 0.45)
        place(piano(ROOT[PROG[bar]] + 12, BAR), at(bar), 0.35)
    place(piano(26, 3.0), 44.4, 0.5)
    place(wind(3.0), 43.9, 1.0, pan=0.3)
    place(swell(1.2), 46.3, 1.2)
    # ---- 第五乐章 吾乡 (bars 19-24)
    m19 = [[(0, 77, 1), (1, 81, 1), (2, 84, 2)], [(0, 84, 1), (1, 86, 1), (2, 88, 1.5), (3.5, 86, .5)],
           [(0, 89, 3), (3, 88, 1)], [(0, 86, 1.5), (1.5, 84, .5), (2, 81, 2)]]
    for j, bar in enumerate((19, 20, 21, 22)):
        chn = PROG[bar]
        mel(bar, m19[j], "piano", 0.7, shift=-12)
        mel(bar, m19[j], "box", 0.35, pan=0.3)
        place(pad(CH[chn] + [CH[chn][0] + 12], BAR, att=0.6 if j else 1.6, rel=1.0), at(bar), 1.4 if j < 2 else 1.1)
        place(piano(ROOT[chn] + 12, BAR), at(bar), 0.55)
        place(bass(ROOT[chn], BAR * 0.9), at(bar), 0.5)
        for k in range(8):
            place(pluck(ARP[chn][k % 4] + 12), at(bar, k * 0.5), 0.3 if j < 2 else 0.25, pan=-0.4)
        if j >= 2:
            for k in (0, 2):
                place(kick(0.6), at(bar, k), 0.55)
    place(kick(1.0), at(19), 0.8)
    place(kick(1.0), at(20), 0.8)
    m23 = [(0, 74, 1), (1, 77, 1), (2, 81, 2)]
    mel(23, m23, "box", 0.85, pan=0.1)
    place(pad(CH["Bb"], BAR, att=0.3, rel=2.0), at(23), 0.5)
    place(music_box(72, 2.5), at(24), 0.6, pan=0.1)
    tseal = 60.8
    place(thump(), tseal, 0.9)
    for i, m in enumerate([65, 69, 72, 77, 81]):
        place(music_box(m, 3.0), tseal + 0.03 + i * 0.06, 0.6, pan=-0.4 + i * 0.2)
    place(pad(CH["F"], 1.2, att=0.05, rel=1.5), tseal, 0.6)


def reverb(x, seconds=2.4, seed=3):
    r = np.random.RandomState(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = r.randn(n) * np.exp(-t / (seconds / 6.5))
    sos = butter(1, 5000, btype="low", fs=SR, output="sos")
    ir = sosfilt(sos, ir)
    ir[: int(0.012 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    return fftconvolve(x, ir)[: len(x)]


def main():
    compose()
    t = np.arange(N) / SR
    # 段落力度：开场轻、高潮最亮
    pts = [(0, 0.5), (9.5, 0.55), (10.5, 0.68), (15, 0.8), (20, 1.0), (27.5, 1.0), (47.0, 1.0), (48.5, 1.45),
           (57.0, 1.3), (58.5, 1.0), (DUR + 1, 1.0)]
    g = np.interp(t, [a for a, _ in pts], [b for _, b in pts])
    L[:] *= g
    R[:] *= g
    wl, wr = reverb(L, seed=3), reverb(R, seed=4)
    duck = np.interp(t, [0, 27.5, 27.56, 27.95, 28.05, DUR + 1], [1, 1, 0.12, 0.12, 1, 1])
    wl *= duck
    wr *= duck
    out = np.stack([L * 0.85 + wl * 0.42, R * 0.85 + wr * 0.42], axis=1)
    sos = butter(1, 30, btype="high", fs=SR, output="sos")
    out = sosfilt(sos, out, axis=0)
    out /= np.max(np.abs(out)) + 1e-9
    out = np.tanh(out * 1.3) / np.tanh(1.3)
    out[:, 0] *= np.clip((DUR - t) / 1.0, 0, 1)
    out[:, 1] *= np.clip((DUR - t) / 1.0, 0, 1)
    out *= 0.89
    pcm = (out * 32767).astype(np.int16)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "music.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", path, len(pcm) / SR, "s")


if __name__ == "__main__":
    main()

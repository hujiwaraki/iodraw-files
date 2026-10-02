"""《此心安处》系列 · 纯代码合成器：乐器、音效、混音。"""
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
rs = np.random.RandomState(1)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _att(n, att=0.004):
    a = max(1, int(att * SR))
    e = np.ones(n)
    e[:min(a, n)] = np.linspace(0, 1, min(a, n))
    return e


def _t(length):
    n = int(length * SR)
    return n, np.arange(n) / SR


# ---------------------------------------------------------------- 乐器
def music_box(m, length=2.4):
    f = mtof(m)
    n, t = _t(length)
    s = np.zeros(n)
    for ratio, amp, tau in ((1, 1.0, 1.2), (2.0, 0.18, 0.5), (3.0, 0.08, 0.3), (5.4, 0.12, 0.12), (8.9, 0.05, 0.05)):
        s += amp * np.sin(2 * np.pi * f * ratio * t + rs.uniform(0, 6)) * np.exp(-t / tau)
    return s * _att(n, 0.002) * 0.35


def piano(m, dur, length=None):
    f = mtof(m)
    length = length or dur + 1.3
    n, t = _t(length)
    s = np.zeros(n)
    B = 0.00035
    for k in range(1, 10):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > SR / 2.2:
            break
        tau = 2.6 / (1 + 0.5 * k) * (220 / max(f, 110)) ** 0.3
        s += (1 / k ** 1.4) * np.sin(2 * np.pi * fk * t + rs.uniform(0, 6)) * np.exp(-t / tau)
    rel = np.ones(n)
    d = int(dur * SR)
    if d < n:
        rel[d:] = np.exp(-(np.arange(n - d) / SR) / 0.3)
    ham = rs.randn(n) * np.exp(-t / 0.006) * 0.06
    return (s * rel + ham) * _att(n, 0.003) * 0.3


def pluck(m, length=1.0, bright=0.27):
    f = mtof(m)
    n, t = _t(length)
    s = np.zeros(n)
    for k in range(1, 14):
        if f * k > SR / 2.2:
            break
        s += (1 / k) * np.sin(np.pi * k * bright) * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (2.5 + 2.0 * k))
    return s * _att(n, 0.002) * 0.42


def reed(m, dur, vib=0.006):
    """簧风琴 / 手风琴感。"""
    f = mtof(m)
    n, t = _t(dur + 0.15)
    ph = 2 * np.pi * f * (t + vib / (2 * np.pi * 5.5) * np.sin(2 * np.pi * 5.5 * t) * f / f)
    s = np.zeros(n)
    for k in range(1, 9):
        s += (0.9 / k ** 1.1) * np.sin(k * ph + 0.3 * k) * (1 if k % 2 else 0.6)
    e = np.clip(t / 0.05, 0, 1) * np.clip((dur + 0.15 - t) / 0.15, 0, 1)
    sos = butter(1, 3200, btype="low", fs=SR, output="sos")
    return sosfilt(sos, s * e) * 0.1


def cello(m, dur, att=0.35):
    f = mtof(m)
    n, t = _t(dur + 0.6)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * t) * np.clip(t / 0.8, 0, 1)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    s = np.zeros(n)
    for k in range(1, 12):
        s += ((-1) ** k) / k * np.sin(k * ph)
    e = np.clip(t / att, 0, 1) ** 1.5 * np.where(t > dur, np.exp(-(t - dur) / 0.25), 1)
    sos = butter(2, 1800, btype="low", fs=SR, output="sos")
    return sosfilt(sos, s * e) * 0.12


def pad(ms, dur, att=1.0, rel=1.4, bright=1.6):
    n, t = _t(dur + rel)
    s = np.zeros(n)
    for m in ms:
        f = mtof(m)
        for det in (-0.08, 0.0, 0.08):
            fd = f * 2 ** (det / 12)
            for k in range(1, 8):
                s += (1 / k ** bright) * np.sin(2 * np.pi * fd * k * t + rs.uniform(0, 6))
    e = np.clip(t / att, 0, 1) ** 2 * np.where(t > dur, np.exp(-(t - dur) / (rel / 3)), 1)
    return s * e * (1 + 0.08 * np.sin(2 * np.pi * 0.3 * t)) * 0.03


def bass(m, dur):
    f = mtof(m)
    n, t = _t(dur + 0.15)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.1 * np.sin(6 * np.pi * f * t)
    e = np.exp(-t / (dur * 0.9)) * np.clip((dur + 0.15 - t) / 0.15, 0, 1)
    return s * e * _att(n, 0.006) * 0.35


# ---------------------------------------------------------------- 打击与音效
def bandnoise(length, lo, hi, tau, order=2):
    n, t = _t(length)
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, rs.randn(n)) * np.exp(-t / tau)


def kick(vol=1.0):
    n, t = _t(0.35)
    f = 45 + 90 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12) * 0.8 * vol


def shaker():
    return bandnoise(0.08, 6000, 14000, 0.018) * 0.3


def jingle():
    s = bandnoise(0.25, 5000, 12000, 0.06) * 0.25
    n, t = _t(0.25)
    for f in (6200, 7400, 8900):
        s += np.sin(2 * np.pi * f * t) * np.exp(-t / 0.05) * 0.03
    return s


def tick(tock=False):
    n, t = _t(0.06)
    f = 1400 if tock else 2100
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.008) * 0.5 + bandnoise(0.06, 2500, 8000, 0.004) * 0.4)


def heartbeat():
    n, t = _t(0.7)
    s = np.zeros(n)
    for t0, a in ((0.0, 1.0), (0.22, 0.7)):
        tt = np.clip(t - t0, 0, None)
        s += np.where(t >= t0, np.sin(2 * np.pi * 52 * tt) * np.exp(-tt / 0.07) * a, 0)
    return s * 0.9


def thump():
    n, t = _t(0.9)
    return np.sin(2 * np.pi * 58 * t) * np.exp(-t / 0.15) * 0.8 + bandnoise(0.9, 150, 1200, 0.03) * 0.5


def rain(length):
    n, t = _t(length)
    sos = butter(2, [900, 7000], btype="band", fs=SR, output="sos")
    s = sosfilt(sos, rs.randn(n)) * 0.05
    drops = (rs.rand(n) < 0.0009) * rs.rand(n)
    sos2 = butter(2, [2500, 6000], btype="band", fs=SR, output="sos")
    return s + sosfilt(sos2, drops) * 0.6


def rumble(length):
    n, t = _t(length)
    sos = butter(2, [40, 220], btype="band", fs=SR, output="sos")
    return sosfilt(sos, rs.randn(n)) * np.sin(np.pi * t / length) ** 2 * 0.5


def swell(length=0.8, lo=600, hi=9000):
    n, t = _t(length)
    sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, rs.randn(n)) * (t / length) ** 3 * 0.25


def swish(length=0.45):
    n, t = _t(length)
    sos = butter(2, [1200, 6000], btype="band", fs=SR, output="sos")
    return sosfilt(sos, rs.randn(n)) * np.sin(np.pi * t / length) ** 2 * 0.15


def buzz(length=0.45):
    n, t = _t(length)
    s = np.sign(np.sin(2 * np.pi * 170 * t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 28 * t))
    sos = butter(2, [150, 900], btype="band", fs=SR, output="sos")
    return sosfilt(sos, s) * np.clip(t / 0.02, 0, 1) * np.clip((length - t) / 0.05, 0, 1) * 0.12


def whistle(length=1.1):
    n, t = _t(length)
    vib = 1 + 0.01 * np.sin(2 * np.pi * 6 * t)
    s = np.zeros(n)
    for f in (mtof(81), mtof(85), mtof(88)):
        s += np.sin(2 * np.pi * f * np.cumsum(vib) / SR)
    e = np.clip(t / 0.08, 0, 1) * np.clip((length - t) / 0.25, 0, 1)
    return (s * 0.12 + bandnoise(length, 1500, 4000, 10) * 0.05) * e


def chug(length=0.18):
    return bandnoise(length, 200, 1600, 0.05) * 0.4


def scratch(length):
    n, t = _t(length)
    sos = butter(2, [2000, 7000], btype="band", fs=SR, output="sos")
    am = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * t + 3 * np.sin(2 * np.pi * 2.3 * t)))
    return sosfilt(sos, rs.randn(n)) * am * 0.07


def knock():
    n, t = _t(0.2)
    return np.sin(2 * np.pi * 620 * t) * np.exp(-t / 0.02) * 0.5 + bandnoise(0.2, 400, 2500, 0.01) * 0.4


def snap():
    return bandnoise(0.25, 1200, 5000, 0.05) * 0.5


# ---------------------------------------------------------------- 混音
class Mix:
    def __init__(self, dur):
        self.dur = dur
        self.N = int(SR * (dur + 0.01))
        self.L = np.zeros(self.N)
        self.R = np.zeros(self.N)

    def place(self, sig, t, vol=1.0, pan=0.0):
        i = int(t * SR)
        if i >= self.N or i < 0:
            return
        sig = sig[:self.N - i] * vol
        gl = np.cos((pan + 1) * np.pi / 4)
        gr = np.sin((pan + 1) * np.pi / 4)
        self.L[i:i + len(sig)] += sig * gl
        self.R[i:i + len(sig)] += sig * gr

    def time(self):
        return np.arange(self.N) / SR

    def gain(self, pts):
        g = np.interp(self.time(), [a for a, _ in pts], [b for _, b in pts])
        self.L *= g
        self.R *= g

    def muffle(self, pts, cutoff=380):
        """按包络在原声与“水下”低通之间混合。"""
        sos = butter(2, cutoff, btype="low", fs=SR, output="sos")
        u = np.interp(self.time(), [a for a, _ in pts], [b for _, b in pts])
        self.L = self.L * (1 - u) + sosfilt(sos, self.L) * u * 1.15
        self.R = self.R * (1 - u) + sosfilt(sos, self.R) * u * 1.15

    def render(self, path, wet=0.42, duck=None):
        def reverb(x, seconds=2.6, seed=3):
            r = np.random.RandomState(seed)
            n = int(seconds * SR)
            t = np.arange(n) / SR
            ir = r.randn(n) * np.exp(-t / (seconds / 6.5))
            ir = sosfilt(butter(1, 5000, btype="low", fs=SR, output="sos"), ir)
            ir[:int(0.012 * SR)] = 0
            ir /= np.sqrt(np.sum(ir ** 2))
            return fftconvolve(x, ir)[:len(x)]

        wl, wr = reverb(self.L, seed=3), reverb(self.R, seed=4)
        if duck is not None:
            d = np.interp(self.time(), [a for a, _ in duck], [b for _, b in duck])
            wl *= d
            wr *= d
        out = np.stack([self.L * 0.85 + wl * wet, self.R * 0.85 + wr * wet], axis=1)
        out = sosfilt(butter(1, 30, btype="high", fs=SR, output="sos"), out, axis=0)
        out /= np.max(np.abs(out)) + 1e-9
        out = np.tanh(out * 1.3) / np.tanh(1.3)
        t = self.time()
        fade = np.clip((self.dur - t) / 1.2, 0, 1)
        out *= fade[:, None] * 0.89
        pcm = (out * 32767).astype(np.int16)
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        return out

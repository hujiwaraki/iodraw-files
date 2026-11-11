"""Build the final soundtrack: narration + light synthesized score (ducked under speech) + SFX. Writes mix.wav (48 kHz stereo)."""
import numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
from timeline import T, AUD, END, COLD_CLIP, COLD_AT, TITLE_S, SR
SRO = 48000
N = int(END * SRO) + SRO
rng = np.random.default_rng(1)
def S(l): return T[l][0]
def E(l): return T[l][1]

def up(a): return resample_poly(a, 2, 1).astype(np.float64)  # 24k -> 48k
def place(buf, a, t, g=1.0):
    i = int(t * SRO); j = min(len(buf), i + len(a)); buf[i:j] += a[: j - i] * g
def lp(x, f, order=2): return sosfilt(butter(order, f, 'low', fs=SRO, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'high', fs=SRO, output='sos'), x)
def bp(x, f1, f2): return sosfilt(butter(2, [f1, f2], 'band', fs=SRO, output='sos'), x)
def tt(d): return np.arange(int(d * SRO)) / SRO
def note_hz(n): return 440.0 * 2 ** ((n - 69) / 12)

# ---------------- narration
voice = np.zeros(N)
a = AUD["L10"][int(COLD_CLIP[0] * SR): int(COLD_CLIP[1] * SR)].copy()
fade = int(0.02 * SR); a[-fade:] *= np.linspace(1, 0, fade)
place(voice, up(a), COLD_AT)
for lid, (s, e) in T.items():
    place(voice, up(AUD[lid]), s)
voice *= 0.89 / np.max(np.abs(voice))

# ---------------- score
def epiano(n, d=2.2, v=0.25):
    x = tt(d); f = note_hz(n)
    env = np.exp(-x * 2.2) * (1 - np.exp(-x * 300))
    sig = np.sin(2 * np.pi * f * x) + 0.35 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 4) + 0.08 * np.sin(2 * np.pi * 3.01 * f * x) * np.exp(-x * 7)
    return sig * env * v
def pad(notes, d, v=0.08):
    x = tt(d); env = np.minimum(1, x / 0.9) * np.minimum(1, (d - x) / 0.9)
    sig = sum(np.sin(2 * np.pi * note_hz(n) * x + i) + 0.5 * np.sin(2 * np.pi * note_hz(n) * 1.003 * x) for i, n in enumerate(notes))
    return lp(sig, 1800) * env * v / len(notes)

music = np.zeros(N)
# chord sets (MIDI)
CH = {"C": [48, 55, 60, 64, 67], "Am": [45, 52, 57, 60, 64], "F": [41, 48, 53, 57, 60], "G": [43, 50, 55, 59, 62],
      "Dm": [38, 50, 53, 57, 62], "Em": [40, 52, 55, 59, 64], "Fm": [41, 48, 53, 56, 60]}
def section(t0, t1, prog_, bar=2.4, arp=True, v=1.0, arp_v=0.16, octave=0):
    t = t0; i = 0
    while t < t1 - 0.3:
        ch = CH[prog_[i % len(prog_)]]; d = min(bar, t1 - t)
        place(music, pad([n + octave for n in ch[1:4]], d + 0.8, 0.07 * v), t)
        place(music, pad([ch[0] - 12 + octave], d + 0.8, 0.09 * v), t)
        if arp:
            pat = [ch[2], ch[3], ch[4], ch[3]]
            for k in range(4):
                if t + k * bar / 4 < t1 - 0.2:
                    place(music, epiano(pat[k] + 12 + octave, v=arp_v * v), t + k * bar / 4)
        t += bar; i += 1

# cold open: low tense drone + pulse
x = tt(2.6); place(music, (np.sin(2 * np.pi * 55 * x) + 0.5 * np.sin(2 * np.pi * 82.4 * x)) * np.minimum(1, x / 0.5) * 0.10, 0.0)
# title hit
x = tt(3.0); place(music, np.sin(2 * np.pi * 45 * x) * np.exp(-x * 2.5) * 0.35, TITLE_S)
place(music, epiano(76, 3.0, 0.22) + epiano(69, 3.0, 0.15), TITLE_S + 0.05)
section(S("L1") - 0.3, S("L7"), ["C", "Am", "F", "G"])                 # light, everyday
section(S("L7"), S("L9") - 0.4, ["Am", "F", "Dm", "Em"], bar=2.8, arp_v=0.12)  # it sinks in
section(S("L9") - 0.4, S("L10"), ["F", "G", "C", "C"], bar=1.6, v=1.0)        # bright trip
# danger: pulse
t = S("L10")
while t < S("L13"):
    x = tt(0.3); place(music, np.sin(2 * np.pi * 73.4 * x) * np.exp(-x * 9) * 0.32, t); t += 0.42
section(S("L10"), S("L13"), ["Dm"], bar=3.0, arp=False, v=1.2)
section(S("L13"), S("L14"), ["F", "C"], bar=1.6, arp_v=0.10)
# lost / desk anxiety
t = S("L14") + 2.0
while t < S("L18"):
    x = tt(0.3); place(music, np.sin(2 * np.pi * 61.7 * x) * np.exp(-x * 9) * 0.26, t); t += 0.55
section(S("L14"), S("L18"), ["Am", "Fm" if False else "F", "Dm", "Em"], bar=2.4, arp=False, v=1.1)
# hope build
section(S("L18"), S("L22") - 0.5, ["F", "G", "Am", "C"], bar=2.0, arp_v=0.13)
section(S("L22") - 0.5, END - 0.2, ["F", "G", "Em", "Am", "F", "G", "C", "C"], bar=2.2, arp_v=0.15)
music[int((END - 2.0) * SRO):int(END * SRO)] *= np.linspace(1, 0, int(2.0 * SRO))[: len(music[int((END - 2.0) * SRO):int(END * SRO)])]
music[int(END * SRO):] = 0

# ---------------- sfx
sfx = np.zeros(N)
def ding(t0, g=0.22):
    x = tt(1.2); place(sfx, (np.sin(2 * np.pi * 1318.5 * x) * np.exp(-x * 5) + 0.6 * np.sin(2 * np.pi * 1975.5 * (x)) * np.exp(-x * 6) * (x > 0.12)) * g, t0)
def swish(t0, g=0.10):
    x = tt(0.25); n = rng.normal(0, 1, len(x)); place(sfx, bp(n, 1500, 6000) * np.sin(np.pi * x / 0.25) * g, t0)
def thud(t0, g=0.5):
    x = tt(0.6); place(sfx, (np.sin(2 * np.pi * 60 * x) * np.exp(-x * 8) + lp(rng.normal(0, 1, len(x)), 400) * np.exp(-x * 12) * 0.5) * g, t0)
def tick(t0, g=0.10):
    x = tt(0.04); place(sfx, hp(rng.normal(0, 1, len(x)), 2500) * np.exp(-x * 150) * g, t0)
def heartbeat(t0, g=0.35):
    for o in (0, 0.22):
        x = tt(0.25); place(sfx, np.sin(2 * np.pi * 50 * x) * np.exp(-x * 18) * g * (1 if o == 0 else 0.7), t0 + o)
def steps(t0, t1, rate=0.42, g=0.05):
    t = t0
    while t < t1:
        x = tt(0.08); place(sfx, bp(rng.normal(0, 1, len(x)), 200, 1500) * np.exp(-x * 60) * g, t); t += rate
def ambience(t0, t1, lo, hi, g):
    d = t1 - t0; x = tt(d); n = bp(rng.normal(0, 1, len(x)), lo, hi)
    env = np.minimum(1, x / 0.8) * np.minimum(1, (d - x) / 0.8)
    place(sfx, n * env * g, t0)

# cold open
steps(0.0, 1.3, 0.38, 0.06)
ambience(0.0, 2.5, 150, 900, 0.025)
# email
ding(S("L5") - 0.15)
ding(S("L5") - 0.15 + 0.0, 0.0)
# laptop closes
thud(S("L6") + 0.7 * (E("L6") - S("L6")), 0.18)
# calendar flips
for i in range(6): swish(S("L7") + i * (0.42 * (E("L7") - S("L7"))) / 6.5, 0.12)
thud(E("L7") + 0.12, 0.40)
# rain
ambience(S("L8") - 0.1, S("L9") - 0.2, 1500, 7000, 0.035)
# museum crowd murmur
ambience(S("L9") - 0.5, S("L13"), 200, 1100, 0.03)
ambience(S("L14") - 0.2, S("L21") + 2.0, 200, 1100, 0.03)
steps(S("L10"), S("L12") + 1.0, 0.42, 0.05)
steps(S("L12"), S("L12") + 1.0, 0.2, 0.06)
# crash: panel hits floor
fall_land = S("L12") + 1.25 + 0.45
x = tt(1.6)
crash = lp(rng.normal(0, 1, len(x)), 3000) * np.exp(-x * 5) * 0.55 + np.sin(2 * np.pi * 48 * x) * np.exp(-x * 4) * 0.6
for f in (523, 811, 1233, 1709): crash += np.sin(2 * np.pi * f * x) * np.exp(-x * 3.5) * 0.06
place(sfx, crash, fall_land)
# spark crackles
for k in range(int(S("L10") * 10), int(S("L13") * 10)):
    if k % 7 == 0: place(sfx, hp(rng.normal(0, 1, int(0.08 * SRO)), 3000) * 0.04, k / 10)
# clock + heartbeat while panicking
t = S("L17")
while t < S("L18"): tick(t, 0.12); t += 0.5
t = S("L17") + 0.2
while t < S("L18") + 0.3: heartbeat(t, 0.32); t += 0.85
# soft breath-swell on remembering
x = tt(1.6); place(sfx, bp(rng.normal(0, 1, len(x)), 300, 1200) * np.sin(np.pi * x / 1.6) * 0.05, S("L18") + 0.1)
# sticky notes falling
for i in range(10): swish(S("L23") + 0.4 + i * 0.22, 0.05)
# end chime
place(sfx, epiano(84, 3, 0.16) + epiano(79, 3, 0.12), S("L26") - 0.1)

# ---------------- duck music under voice
venv = np.abs(voice)
k = int(0.05 * SRO); venv = np.convolve(venv, np.ones(k) / k, mode="same")
active = (venv > 0.01).astype(float)
k2 = int(0.35 * SRO); active = np.convolve(active, np.ones(k2) / k2, mode="same")
duck = 1.0 - 0.65 * np.clip(active * 1.5, 0, 1)
mus = music * duck * 0.45
fx = sfx * (1.0 - 0.35 * np.clip(active * 1.5, 0, 1))

mixL = voice + mus * 1.00 + fx
mixR = voice + mus * 0.96 + fx
st = np.stack([mixL, mixR], 1)[: int(END * SRO)]
peak = np.max(np.abs(st)); st *= 0.95 / peak if peak > 0.95 else 1.0
sf.write("mix.wav", st.astype(np.float32), SRO, subtype="PCM_24")
# report levels (speech-active vs music)
def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
mask = (active[: len(st)] > 0.5)
print("voice RMS (speech)", round(rms_db(voice[: len(st)][mask]), 1), "dBFS | music under speech", round(rms_db(mus[: len(st)][mask]), 1),
      "dBFS | music in gaps", round(rms_db(mus[: len(st)][~mask]), 1), "dBFS | peak", round(20 * np.log10(np.max(np.abs(st))), 2))

"""Audio-driven timeline: every visual and subtitle time comes from the real TTS durations."""
import soundfile as sf, numpy as np, os
from script_lines import LINES
HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
SR = 24000
COLD_FILE = "COLD.wav"       # "Hey! Stop!" generated as its own line (am_michael)
COLD_AT = 0.45
TITLE_S, TITLE_E = 2.6, 5.6
EXTRA_GAP = {"L9": 0.6, "L14": 0.3, "L21": 0.2, "L22": 0.6, "L24": 0.2}
T = {}; AUD = {}; ENV = {}
t = TITLE_E + 0.2
for lid, sp, en, zh, pause in LINES:
    a, sr = sf.read(os.path.join(HERE, "tts", lid + ".wav"), dtype="float32"); assert sr == SR
    t += EXTRA_GAP.get(lid, 0.0)
    T[lid] = (round(t, 3), round(t + len(a) / sr, 3)); AUD[lid] = a
    hop = sr // FPS
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) if i < len(a) else 0 for i in range(0, len(a) + hop, hop)])
    ENV[lid] = np.clip(rms / (rms.max() + 1e-9) * 1.4, 0, 1)
    t += len(a) / sr + pause
END = round(T["L26"][1] + 5.0, 3)
NFRAMES = int(round(END * FPS))

def env(lid, tt):
    s, e = T[lid]
    if tt < s or tt > e: return 0.0
    i = int((tt - s) * FPS); return float(ENV[lid][min(i, len(ENV[lid]) - 1)])

# subtitle cues
CUES = [(COLD_AT, COLD_AT + 1.75, "Hey! Stop!", "嘿！停下！")]
ids = [l[0] for l in LINES]
for i, (lid, sp, en, zh, pause) in enumerate(LINES):
    s, e = T[lid]
    nxt = T[ids[i + 1]][0] if i + 1 < len(ids) else END - 0.5
    end = min(max(e + 0.35, s + 1.6), nxt - 0.06)
    CUES.append((s, end, en, zh))

def cue_at(tt):
    for s, e, en, zh in CUES:
        if s - 0.001 <= tt < e: 
            a = min(1.0, (tt - s) / 0.12, (e - tt) / 0.12)
            return en, zh, max(0.0, a)
    return None

if __name__ == "__main__":
    for k, v in T.items(): print(k, v)
    print("END", END, "frames", NFRAMES)

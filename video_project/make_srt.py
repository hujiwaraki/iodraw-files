from timeline import CUES
from engine import wrap_en, font, EN_SIZE
def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)
fe = font("en", EN_SIZE); out = []
for i, (s, e, en, zh) in enumerate(CUES, 1):
    out.append(f"{i}\n{ts(s)} --> {ts(e)}\n" + "\n".join(wrap_en(en, fe)) + f"\n{zh}\n")
open("build/later_bilingual.srt", "w", encoding="utf-8").write("\n".join(out))
print(len(CUES), "cues")

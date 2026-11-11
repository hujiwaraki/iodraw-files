import json, numpy as np, soundfile as sf, sys, os
from kokoro_onnx import Kokoro
from script_lines import LINES, VOICE
M=sys.argv[1]
k=Kokoro(M+"/kokoro-v1.0.onnx", M+"/voices-v1.0.bin")
os.makedirs("tts",exist_ok=True); meta=[]
SPEED={"N":0.94,"W":1.0,"S":0.95}
for lid,sp,en,zh,p in LINES:
    txt=en.replace("“",'"').replace("”",'"')
    a,sr=k.create(txt, voice=VOICE[sp], speed=SPEED[sp], lang="en-us")
    # trim silence (keep 60ms pad so word ends are never cut)
    thr=10**(-45/20); idx=np.where(np.abs(a)>thr)[0]
    s=max(0,idx[0]-int(.06*sr)); e=min(len(a),idx[-1]+int(.12*sr)); a=a[s:e]
    sf.write(f"tts/{lid}.wav",a,sr); meta.append((lid,len(a)/sr)); print(lid,round(len(a)/sr,2))
print("total speech",sum(d for _,d in meta), "pauses", sum(l[4] for l in LINES))

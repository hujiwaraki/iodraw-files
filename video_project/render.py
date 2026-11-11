"""Render frames: python3 render.py preview outdir t1 t2 ...  |  python3 render.py segment f0 f1 out.mp4"""
import sys, subprocess, numpy as np, skia
from engine import W, H, draw_subtitle, grain
from scenes import scene_for
from timeline import FPS, cue_at

def frame(t, fi):
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.ColorBLACK)
    scene_for(t)(c, t)
    grain(c, fi)
    cue = cue_at(t)
    if cue: draw_subtitle(c, cue[0], cue[1], cue[2])
    return surf

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "preview":
        for ts in sys.argv[3:]:
            t = float(ts); frame(t, int(t * FPS)).makeImageSnapshot().save(f"{sys.argv[2]}/f_{t:07.2f}.png")
    else:
        f0, f1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high", "-g", "60", out], stdin=subprocess.PIPE)
        for fi in range(f0, f1):
            img = frame(fi / FPS, fi).makeImageSnapshot()
            p.stdin.write(img.toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
        p.stdin.close(); p.wait(); assert p.returncode == 0

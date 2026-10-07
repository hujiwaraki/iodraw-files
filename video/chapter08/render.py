"""终章渲染入口。

  python render.py keyframes 8 30 66 92 125   # 关键帧
  python render.py video                        # 完整视频（无声）
  python render.py mux                          # 合成音乐 → out/chapter08_终章_此心安处.mp4
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "series"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter01"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter02"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter03"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter04"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter05"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter06"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter07"))

import ch08  # noqa: E402
from engine import render_keyframes, render_video  # noqa: E402

OUT = os.path.join(HERE, "out")

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "keyframes":
        for p in render_keyframes(ch08, [float(x) for x in sys.argv[2:]], OUT):
            print(p)
    elif mode == "video":
        print(render_video("ch08", ch08, OUT))
    elif mode == "mux":
        final = os.path.join(OUT, f"{ch08.NAME}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(OUT, "video_silent.mp4"),
                        "-i", os.path.join(OUT, "music.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                        "-shortest", "-movflags", "+faststart", final], check=True)
        share = os.path.join(OUT, f"{ch08.NAME}_分享版.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(OUT, "video_silent.mp4"),
                        "-i", os.path.join(OUT, "music.wav"), "-c:v", "libx264", "-preset", "slow", "-b:v", "1000k",
                        "-maxrate", "1800k", "-bufsize", "3000k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                        "-shortest", "-movflags", "+faststart", share], check=True)
        print(final, share)

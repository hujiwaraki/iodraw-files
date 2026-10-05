"""第三章渲染入口。

  python render.py keyframes 8 30 66 92 125   # 关键帧
  python render.py video                        # 完整视频（无声）
  python render.py mux                          # 合成音乐 → out/chapter03_从游客到旅人.mp4
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "series"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter01"))
sys.path.insert(0, os.path.join(HERE, "..", "chapter02"))

import ch03  # noqa: E402
from engine import render_keyframes, render_video  # noqa: E402

OUT = os.path.join(HERE, "out")

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "keyframes":
        for p in render_keyframes(ch03, [float(x) for x in sys.argv[2:]], OUT):
            print(p)
    elif mode == "video":
        print(render_video("ch03", ch03, OUT))
    elif mode == "mux":
        final = os.path.join(OUT, f"{ch03.NAME}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(OUT, "video_silent.mp4"),
                        "-i", os.path.join(OUT, "music.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                        "-shortest", "-movflags", "+faststart", final], check=True)
        share = os.path.join(OUT, f"{ch03.NAME}_分享版.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(OUT, "video_silent.mp4"),
                        "-i", os.path.join(OUT, "music.wav"), "-c:v", "libx264", "-preset", "slow", "-b:v", "1000k",
                        "-maxrate", "1800k", "-bufsize", "3000k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                        "-shortest", "-movflags", "+faststart", share], check=True)
        print(final, share)

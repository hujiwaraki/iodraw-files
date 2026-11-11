#!/bin/bash
# concat rendered segments, mux narration/music mix, H.264 + AAC, yuv420p, faststart
set -e
cd "$(dirname "$0")"
printf "file 'seg0.mp4'\nfile 'seg1.mp4'\nfile 'seg2.mp4'\nfile 'seg3.mp4'\n" > build/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i build/list.txt -c copy build/video_only.mp4
ffmpeg -y -loglevel error -i build/video_only.mp4 -i mix.wav -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart \
  -metadata title="Later / 以后再说" build/later_bilingual_1080p.mp4
ls -la build/later_bilingual_1080p.mp4

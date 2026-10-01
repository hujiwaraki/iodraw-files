# 此心安处 · 绘本风动画短片

全部由代码生成：画面用 pycairo 逐帧绘制，配乐用 numpy 合成，没有任何外部素材。

- `draw.py`：手抖线条、水彩填充、人物与物件
- `scenes.py`：12 个分镜
- `render.py`：转场、纸张纹理、字幕、并行渲染
- `music.py`：八音盒 / 钢琴 / 拨弦 / 铺底 / 打击乐合成

```bash
pip install numpy pillow pycairo scipy
mkdir -p fonts && curl -L -o fonts/LXGWWenKai-Regular.ttf \
  https://github.com/lxgw/LxgwWenKai/releases/download/v1.330/LXGWWenKai-Regular.ttf
cp fonts/LXGWWenKai-Regular.ttf ~/.fonts/ && fc-cache -f
python render.py video && python music.py
ffmpeg -i out/video_silent.mp4 -i out/music.wav -c:v copy -c:a aac -b:a 256k -shortest out/此心安处.mp4
```

文字：藤原樹

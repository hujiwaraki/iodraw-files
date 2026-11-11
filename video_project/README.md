# LATER / 以后再说 — 中英双语教育短片

面向中国小学五年级（10–11 岁）的叙事短片，约 106 秒，1920×1080，16:9。

## 成片

| 文件 | 说明 |
| --- | --- |
| `deliverables/later_bilingual_1080p.mp4` | 成片：H.264 High（yuv420p，30fps）+ AAC 48 kHz 立体声，已加 `+faststart`；双语字幕已烧录在画面中 |
| `deliverables/later_bilingual.srt` | 与成片时间轴一致的双语 SRT（英文在上、中文在下） |

## 故事

主角阿明（Ming）总说“英语以后再学”，于是发生了三件后果逐步加重的事：

1. **错过机会**：他花了三周做机器人，却没看懂报名邮件（“Sign up by Friday” = 最迟星期五完成报名），也没有去问。到星期一才弄明白，报名已经截止。
2. **安全风险**：研学时在科学馆里，他没听懂工作人员喊的 “Stop! That area is closed for repairs.”，继续往前走。工作人员冲过去把他拉了回来，下一秒天花板板块就砸了下来。
3. **求助困难**：他和同学走散后，选择去服务台求助，这是对的做法。但他说不清自己的情况，急得脑子一片空白。最后他想起课上学过的一句话 “I don't understand. Can you help me?”，工作人员帮他联系上了老师。

转折：拖得越久，不懂的地方就越多，但今天就可以开始补。
结尾行动：今天先学十分钟，听懂一句、跟读几遍、自己说出来；遇到不懂的，马上问。

## 制作方式（全部在本地离线完成）

- **配音**：Kokoro-82M 神经网络 TTS（ONNX 版），使用 American English（`lang="en-us"`）音色：
  旁白 `af_heart`（美式女声），工作人员 `am_michael`（美式男声），服务台工作人员 `af_bella`（美式女声）。
  语速用模型参数控制在 0.94–1.0，没有对音频做时间拉伸。
- **语音核查**：用 Whisper small.en（sherpa-onnx）逐句转写，并对最终混音整轨再转写一次，所有句子均与台词一致。
- **画面**：skia-python 矢量绘制。人物有骨骼绑定（手臂、腿、行走和奔跑循环、表情、口型）；口型由各句配音的音量包络驱动。
- **配乐与音效**：用 numpy/scipy 程序合成；旁白出现时自动压低配乐（旁白下方约 −15.6 dB）。
- **字幕**：Inter（英文）+ Noto Sans SC（中文）。长句按语义断行，避免最后一个词单独成行。

## 重新生成

```bash
export MODELS_DIR=/path/to/models   # kokoro-v1.0.onnx, voices-v1.0.bin, NotoSansSC-{400,600,800}.ttf
python3 gen_tts.py "$MODELS_DIR"     # 逐句生成配音 -> tts/
python3 mix.py                       # 混音 -> mix.wav
python3 make_srt.py                  # 字幕 -> build/later_bilingual.srt
python3 render.py segment 0 3188 build/seg0.mp4   # 或拆成 4 段并行渲染
./finalize.sh                        # 拼接 + 混入音频 + faststart
node playtest.js build/later_bilingual_1080p.mp4 <截图目录>   # 浏览器实际播放检查
```

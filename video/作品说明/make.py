"""《此心安处》作品说明 PDF：封面、简介与目录、每集一页（梗概 + 三张关键画面）。"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
V = "/home/user/iodraw-files/video/成品"
FONT = "/home/user/iodraw-files/video/fonts/LXGWWenKai-Regular.ttf"
PW, PH = 1240, 1754
BG, INK, SUB, ACC = (246, 240, 228), (60, 52, 46), (128, 116, 104), (63, 90, 72)

EPS = [
    ("第一章", "出逃", "chapter01/chapter01_出逃.mp4", "2 分 01 秒", (1, 5, 6),
     "在一个地方待了太久，久到每一条街都记得某一次难过。焦虑像潮水一样漫上来，热闹散场后只剩空洞。"
     "直到在一本书里看见另一个世界——她终于推开门，从灰蓝色的日子里出逃，颜色一点点回到了世界。"),
    ("第二章", "一个人", "chapter02/chapter02_一个人.mp4", "2 分 30 秒", (2, 3, 5),
     "第一次只想逃，没人陪，只好跟团；在团里才看清，两个人也可能很寂寞。也想等一个真正合适的人，可总等不来。"
     "怕孤独，也怕衰老，后来衰老压过了一切——于是不再等，一个人出发。"),
    ("第三章", "从游客到旅人", "chapter03/chapter03_从游客到旅人.mp4", "3 分 38 秒", (1, 5, 6),
     "第一次一个人上路，订错机票，在出租车上哭了一路，才明白一个人旅行并不浪漫。成长是生活的重锤一下一下凿出来的，"
     "跨过一道坎，下一个困难又回到新手村。跌跌撞撞地，她从打卡的游客，慢慢变成了走进当地生活的旅人。"),
    ("第四章", "不敢抵达的地方", "chapter04/chapter04_不敢抵达的地方.mp4", "2 分 20 秒", (1, 3, 6),
     "漂泊了很久，想找个地方把自己“种”下来，却总种不下去。习惯了一个人走，却仍有不敢一个人抵达的地方："
     "那些风景太盛大、太适合两个人。她把它们留着——留给某一个人，也留给一群人。"),
    ("第五章", "同路人", "chapter05/chapter05_同路人.mp4", "3 分 12 秒", (2, 5, 6),
     "一个人出发，却并不总是一个人。同路人不用在出发前苦等，是在路上遇见的：一起骑车、喝酒、追落日，很快熟悉，"
     "又在旅程结束时各自散开。那些相遇没有失去意义——愉快的夜晚，后来陪伴了很多孤寂的夜晚。"),
    ("第六章", "模糊地带", "chapter06/chapter06_模糊地带.mp4", "2 分 22 秒", (1, 4, 6),
     "人间不完美：失望、失去、被辜负。也正是在一次次相遇和分离里，她学会了接受模糊地带——关系不一定有定义，"
     "故事不一定有结尾。人生本来就不会闭环；很多答案，都在每一个活在当下的瞬间里。"),
    ("第七章", "那个人", "chapter07/chapter07_那个人.mp4", "3 分 13 秒", (1, 3, 6),
     "以为短暂的旅伴这次能走远一点，一起上路才发现，陪伴不等于同行。ta 很好，可就是不合拍。四个月后，ta 离开了，"
     "只留下一句“万事向前看”。后来 ta 又回来了，她却很平静——当时觉得天大的事，回头再看，也不是什么大事。"),
    ("终章", "此心安处", "chapter08/chapter08_终章_此心安处.mp4", "2 分 30 秒", (2, 4, 5),
     "从高原到平原，再到海洋：曾经用规矩把自己垒得坚硬，后来在混沌的人间里明白，所谓人间，就是在人之间；"
     "心安不是一种固定的状态，而是在动荡与摇摆中保持自我的平衡。原来每一章翻开的那本书，是她自己写的。"),
    ("番外", "例外", "chapter08b/番外_例外.mp4", "1 分 56 秒", (1, 3, 5),
     "一向喜新厌旧的人，却把同一座山城去了三次——这一次，是好朋友带她回自己长大的地方。走过老城的一砖一瓦，"
     "吃遍她从小吃到大的味道，夜里聊到凌晨。原来人和人之间，心和心的距离，可以这么近。"),
]

INTRO = ("《此心安处》是一部绘本风格的竖屏系列动画，共九集（第一章至终章，外加一篇番外），总时长约 24 分钟。"
         "作品根据作者本人的旅行随笔改编，讲述一个人从逃离日常、独自上路，到慢慢学会与自己、与他人、与世界相处的过程："
         "一路向外行走，也一路向内寻找，最终找到内心的安宁。")
NOTES = [
    "画幅：9:16 竖屏，1080×1920，30 帧。",
    "形象：主角以“黄色外套、草帽”为固定形象；路人为灰色无脸的剪影，“那个人”只有虚线轮廓。",
    "表达：全片不出现真实地名，不用直白的解说，多用光线、天气与季节变化来表达情绪。",
    "结构：每一集都从一本翻开的书开始，在书页合上时结束；终章揭晓，这本书是她自己写的。",
    "制作：画面、字幕与配乐均为作者原创，并全部以代码生成。",
]


def font(size):
    return ImageFont.truetype(FONT, size)


def wrap(d, text, f, width):
    toks, i = [], 0                                                # 英文字母连在一起，不拆开（ta）
    while i < len(text):
        j = i
        while j < len(text) and text[j].isascii() and text[j].isalpha():
            j += 1
        toks.append(text[i:j] if j > i else text[i])
        i = max(j, i + 1)
    lines, cur = [], ""
    for tk in toks:
        if d.textlength(cur + tk, font=f) > width and cur:
            lines.append(cur)
            cur = tk
        else:
            cur += tk
    if cur:
        lines.append(cur)
    for k in range(1, len(lines)):                                 # 标点不放行首
        while lines[k] and lines[k][0] in "，。、；：！？”）":
            lines[k - 1] += lines[k][0]
            lines[k] = lines[k][1:]
    return [ln for ln in lines if ln]


def para(d, text, x, y, width, size, col=INK, gap=1.75):
    f = font(size)
    for ln in wrap(d, text, f, width):
        d.text((x, y), ln, font=f, fill=col)
        y += int(size * gap)
    return y


def frame(path, t, w):
    out = os.path.join(HERE, "frames", f"{os.path.basename(path)}_{t:.2f}.jpg")
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1",
                        "-vf", "scale=720:1280", out], check=True)
    im = Image.open(out).convert("RGB")
    return im.resize((w, int(w * 16 / 9)), Image.LANCZOS)


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)


def page():
    im = Image.new("RGB", (PW, PH), BG)
    return im, ImageDraw.Draw(im)


def footer(d, n):
    f = font(22)
    s = f"《此心安处》作品说明 · {n}"
    d.text(((PW - d.textlength(s, font=f)) / 2, PH - 70), s, font=f, fill=SUB)


pages = []
# 封面
im, d = page()
cover = frame(os.path.join(V, EPS[7][2]), 6 + (duration(os.path.join(V, EPS[7][2])) - 12) * 4.5 / 6, 520)
im.paste(cover, ((PW - 520) // 2, 470))
d.rectangle(((PW - 520) // 2 - 2, 468, (PW + 520) // 2 + 1, 470 + cover.height + 1), outline=(200, 190, 175), width=2)
for s, size, y, col in (("此心安处", 120, 170, INK), ("绘本风格竖屏系列动画 · 共九集 · 约 24 分钟", 34, 340, SUB),
                        ("藤原樹", 44, 1440, INK), ("作品说明", 34, 1510, SUB)):
    f = font(size)
    d.text(((PW - d.textlength(s, font=f)) / 2, y), s, font=f, fill=col)
pages.append(im)

# 简介、创作说明、目录
im, d = page()
d.text((110, 110), "作品简介", font=font(52), fill=ACC)
y = para(d, INTRO, 110, 200, PW - 220, 31, gap=1.65)
d.text((110, y + 40), "创作说明", font=font(52), fill=ACC)
y += 130
for s in NOTES:
    y = para(d, "· " + s, 110, y, PW - 220, 29, gap=1.6) + 8
d.text((110, y + 30), "目录", font=font(52), fill=ACC)
y += 120
for no, title, _, dur, _, _ in EPS:
    d.text((150, y), f"{no}　{title}", font=font(32), fill=INK)
    f = font(30)
    d.text((PW - 150 - d.textlength(dur, font=f), y + 2), dur, font=f, fill=SUB)
    y += 50
d.text((150, y + 6), "合计　约 23 分 40 秒", font=font(32), fill=ACC)
pages.append(im)

# 每集一页
for i, (no, title, path, dur, picks, text) in enumerate(EPS):
    im, d = page()
    full = os.path.join(V, path)
    D = duration(full)
    d.text((110, 110), no, font=font(40), fill=SUB)
    d.text((110, 170), title, font=font(84), fill=INK)
    f = font(30)
    d.text((PW - 110 - d.textlength(dur, font=f), 210), dur, font=f, fill=SUB)
    d.line((110, 300, PW - 110, 300), fill=(210, 200, 185), width=2)
    y = para(d, text, 110, 340, PW - 220, 32)
    w, gap = 340, 30
    x0 = (PW - 3 * w - 2 * gap) // 2
    top = max(y + 70, 640)
    for j, k in enumerate(picks):
        im.paste(frame(full, 6 + (D - 12) * (k - 0.5) / 6, w), (x0 + j * (w + gap), top))
    footer(d, i + 3)
    pages.append(im)

out = os.path.join(HERE, "此心安处_作品说明.pdf")
pages[0].save(out, save_all=True, append_images=pages[1:], resolution=150, quality=88)
print(out, os.path.getsize(out) // 1024, "KB")

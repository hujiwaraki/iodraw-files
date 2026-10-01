"""逐帧渲染：场景 → 转场 → 纸张纹理 → 字幕 → ffmpeg。

用法：
  python render.py keyframes 3 13.5 26.5 50      # 输出关键帧 PNG
  python render.py video                         # 渲染完整视频（无声）
"""
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from draw import H, W, clamp, ease_io, set_time
from scenes import SCENES, TRANSITIONS

FPS = 30
DUR = 62.5
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FONT_PATH = os.path.join(HERE, "fonts", "LXGWWenKai-Regular.ttf")

# (开始, 结束, 文本, 样式) 样式: dark=墨色字, light=浅色字, title=大标题
SUBS = [
    (0.5, 4.7, "一直知道，一个人旅行并不浪漫。", "dark"),
    (5.4, 9.7, "如果那些地方迟早要去，为什么不是现在？", "dark"),
    (10.4, 14.7, "去一个谁也不认识的地方，小小地重活一遍。", "dark"),
    (15.4, 19.7, "有些地方，还是想留给某一个人。", "dark"),
    (20.3, 27.2, "一起骑车，一起喝酒，一起追着落日跑。", "dark"),
    (28.0, 32.2, "然后，各自去了不同的城市。", "light"),
    (33.0, 37.2, "那些人早已不在生活里，可那些时刻还在。", "light"),
    (37.9, 42.2, "一回头，他坐在长椅上，申请下一段行程的签证。", "dark"),
    (42.9, 47.2, "四个月后，只留下一句：“万事向前看。”", "dark"),
    (48.0, 52.2, "此心安处是吾乡。", "title"),
    (49.6, 52.2, "—— 苏轼", "title_small"),
    (53.0, 57.2, "继续一个人，看这个世界。", "dark"),
]


# ---------------------------------------------------------------- 纸张纹理
def make_paper():
    rs = np.random.RandomState(7)

    def noise(scale):
        small = (rs.rand(H // scale + 2, W // scale + 2) * 255).astype(np.uint8)
        im = Image.fromarray(small).resize((W, H), Image.BICUBIC)
        return np.asarray(im, np.float32) / 255

    n = 0.5 * noise(240) + 0.3 * noise(60) + 0.2 * noise(10)
    grain = rs.rand(H, W).astype(np.float32)
    fib = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(fib)
    for _ in range(900):
        x, y = rs.uniform(0, W), rs.uniform(0, H)
        a = rs.uniform(0, math.pi)
        ln = rs.uniform(8, 40)
        d.line([(x, y), (x + math.cos(a) * ln, y + math.sin(a) * ln)], fill=int(rs.uniform(40, 110)), width=1)
    fib = np.asarray(fib.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
    tex = 0.985 + 0.07 * (n - 0.5) + 0.05 * (grain - 0.5) - 0.06 * fib
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dd = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
    vig = 1 - 0.16 * np.clip(dd - 0.35, 0, None)
    return (tex * vig)[..., None].astype(np.float32)


PAPER_TEX = None


# ---------------------------------------------------------------- 字幕
class Sub:
    def __init__(self, t0, t1, s, style):
        self.t0, self.t1, self.s, self.style = t0, t1, s, style
        size = {"title": 110, "title_small": 42}.get(style, 56)
        font = ImageFont.truetype(FONT_PATH, size)
        pad = 40
        widths = [font.getlength(ch) for ch in s]
        tw = int(sum(widths)) + 2 * pad
        th = int(size * 1.35) + 2 * pad
        img = Image.new("L", (tw, th), 0)
        d = ImageDraw.Draw(img)
        x = pad
        centers = []
        for ch, w in zip(s, widths):
            d.text((x, pad), ch, font=font, fill=255)
            centers.append(x + w / 2)
            x += w
        self.text_a = np.asarray(img, np.float32) / 255
        halo = img.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(14))
        ha = np.asarray(halo, np.float32) / 255
        self.halo_a = np.clip(ha * 2.2, 0, 1)
        cols = np.arange(tw)
        self.col_idx = np.argmin(np.abs(cols[:, None] - np.array(centers)[None, :]), axis=1)
        self.n = len(s)
        self.w, self.h = tw, th
        if style == "title":
            self.cy = 250
        elif style == "title_small":
            self.cy = 375
        else:
            self.cy = 990
        self.x = (W - tw) // 2 if style != "title_small" else W // 2 + 180
        self.y = self.cy - th // 2
        light = style in ("light", "title", "title_small")
        self.tcol = np.array((250, 243, 230) if light else (58, 44, 37), np.float32) / 255
        self.hcol = np.array((40, 28, 48) if light else (246, 238, 222), np.float32) / 255
        self.hmax = 0.45 if light else 0.75
        self.step = 0.22 if style == "title" else 0.06
        self.fade_in = 0.6 if style.startswith("title") else 0.35

    def alpha_cols(self, t):
        i = np.arange(self.n)
        a = np.clip((t - self.t0 - i * self.step) / self.fade_in, 0, 1)
        a = a * a * (3 - 2 * a)
        out = clamp((self.t1 - t) / 0.45)
        return (a * out)[self.col_idx]

    def composite(self, img, t):
        if not (self.t0 <= t <= self.t1):
            return
        ac = self.alpha_cols(t)[None, :]
        rise = 0.0
        y = self.y + int(rise)
        region = img[y:y + self.h, self.x:self.x + self.w]
        ha = (self.halo_a * ac * self.hmax)[..., None]
        region[:] = region * (1 - ha) + self.hcol * ha
        ta = (self.text_a * ac)[..., None]
        region[:] = region * (1 - ta) + self.tcol * ta


SUB_OBJS = None


# ---------------------------------------------------------------- 合成
def scene_at(t):
    for i, (a, b, fn) in enumerate(SCENES):
        if a <= t < b or i == len(SCENES) - 1:
            return i, a, b, fn


def draw_scene(t, idx=None):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    c.set_source_rgb(0.957, 0.918, 0.847)
    c.paint()
    if idx is None:
        idx, a, b, fn = scene_at(t)
    else:
        a, b, fn = SCENES[idx]
    lt = clamp(t - a, 0, b - a - 1e-3)
    set_time(t)
    fn(c, lt)
    return surf


def render_surface(t):
    for tb, kind in TRANSITIONS:
        half = 0.35 if kind == "page" else 0.3
        if tb - half <= t < tb + half:
            ia = scene_at(tb - 0.01)[0]
            ib = ia + 1
            A = draw_scene(min(t, tb - 0.001), ia)
            B = draw_scene(max(t, tb), ib)
            p = ease_io((t - (tb - half)) / (2 * half))
            out = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
            c = cairo.Context(out)
            c.set_source_surface(A, 0, 0)
            c.paint()
            if kind == "fade":
                c.set_source_surface(B, 0, 0)
                c.paint_with_alpha(p)
                return out
            edge = W * (1 - p)
            c.save()
            c.rectangle(edge, 0, W - edge, H)
            c.clip()
            c.set_source_surface(B, 0, 0)
            c.paint()
            g = cairo.LinearGradient(edge, 0, edge + 120, 0)
            g.add_color_stop_rgba(0, 0, 0, 0, 0.35)
            g.add_color_stop_rgba(1, 0, 0, 0, 0)
            c.set_source(g)
            c.paint()
            c.restore()
            fw = min(180, (W - edge) * 0.35) * math.sin(math.pi * p)
            if fw > 1:
                g = cairo.LinearGradient(edge - fw, 0, edge, 0)
                g.add_color_stop_rgb(0, 0.86, 0.81, 0.72)
                g.add_color_stop_rgb(0.7, 0.98, 0.95, 0.89)
                g.add_color_stop_rgb(1, 0.93, 0.89, 0.82)
                c.set_source(g)
                c.move_to(edge, 0)
                c.curve_to(edge - fw * 0.6, H * 0.3, edge - fw, H * 0.7, edge - fw * 0.9, H)
                c.line_to(edge, H)
                c.close_path()
                c.fill_preserve()
                c.set_source_rgba(0.24, 0.18, 0.16, 0.6)
                c.set_line_width(2)
                c.stroke()
            return out
    return draw_scene(t)


def render_frame(t):
    global PAPER_TEX, SUB_OBJS
    if PAPER_TEX is None:
        PAPER_TEX = make_paper()
    if SUB_OBJS is None:
        SUB_OBJS = [Sub(*s) for s in SUBS]
    surf = render_surface(t)
    surf.flush()
    arr = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    img = arr[..., [2, 1, 0]].astype(np.float32) / 255
    img *= PAPER_TEX
    for s in SUB_OBJS:
        s.composite(img, t)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def render_chunk(args):
    wid, f0, f1 = args
    path = os.path.join(OUT, f"part{wid}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(render_frame(f / FPS).tobytes())
        if (f - f0) % 60 == 0:
            print(f"[w{wid}] {f - f0}/{f1 - f0}", flush=True)
    p.stdin.close()
    p.wait()
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    mode = sys.argv[1]
    if mode == "keyframes":
        for ts in sys.argv[2:]:
            t = float(ts)
            Image.fromarray(render_frame(t)).save(os.path.join(OUT, f"key_{t:05.1f}.png"))
            print("saved", t)
    elif mode == "video":
        nf = int(round(DUR * FPS))
        nw = int(os.environ.get("WORKERS", os.cpu_count() or 4))
        step = math.ceil(nf / nw)
        jobs = [(i, i * step, min(nf, (i + 1) * step)) for i in range(nw)]
        with Pool(nw) as pool:
            parts = pool.map(render_chunk, jobs)
        lst = os.path.join(OUT, "parts.txt")
        with open(lst, "w") as f:
            for p in parts:
                f.write(f"file '{p}'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", os.path.join(OUT, "video_silent.mp4")], check=True)
        print("done")


if __name__ == "__main__":
    main()

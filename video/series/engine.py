"""《此心安处》系列 · 竖屏渲染引擎。

每一章提供一个 config 模块：
  NAME, DUR, SCENES=[(t0, t1, fn)], TRANSITIONS=[(t, kind)], SUBS=[(t0, t1, text, style)], grade_at(t)
"""
import math
import os
import subprocess
from multiprocessing import Pool

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from draw import (FONT_FACE, H, INK, W, clamp, ease_io, ease_in, ease_out, ell, glow, hexc, keep, line,
                  mix, prog, rect, set_grade, set_time, shape, text, wob, spath)

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "..", "fonts", "LXGWWenKai-Regular.ttf")

COVER = hexc("2f4a3c")       # 墨绿布面
COVER_DARK = hexc("243a2f")
GOLD = hexc("d8b46a")
PAGE = hexc("f6eedd")
TABLE = hexc("7e5236")


# ---------------------------------------------------------------- 纸张纹理
def make_paper():
    rs = np.random.RandomState(7)

    def noise(scale):
        small = (rs.rand(H // scale + 2, W // scale + 2) * 255).astype(np.uint8)
        return np.asarray(Image.fromarray(small).resize((W, H), Image.BICUBIC), np.float32) / 255

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
    vig = 1 - 0.14 * np.clip(dd - 0.4, 0, None)
    return (tex * vig)[..., None].astype(np.float32)


# ---------------------------------------------------------------- 字幕（可多行，逐字浮现）
SUB_Y = 1290          # 约 67% 高度，避开底部互动区


class Sub:
    def __init__(self, t0, t1, s, style="dark", size=52, cy=SUB_Y):
        self.t0, self.t1, self.style = t0, t1, style
        font = ImageFont.truetype(FONT_PATH, size)
        lines = s.split("\n")
        lh = int(size * 1.5)
        pad = 44
        widths = [sum(font.getlength(ch) for ch in ln) for ln in lines]
        tw = int(max(widths)) + 2 * pad
        th = lh * len(lines) + 2 * pad
        img = Image.new("L", (tw, th), 0)
        d = ImageDraw.Draw(img)
        idx_map = np.zeros((th, tw), np.int32)
        xs = np.arange(tw)
        k = 0
        for li, (ln, wl) in enumerate(zip(lines, widths)):
            x = (tw - wl) / 2
            y = pad + li * lh
            cs, ks = [], []
            for ch in ln:
                w = font.getlength(ch)
                d.text((x, y), ch, font=font, fill=255)
                cs.append(x + w / 2)
                ks.append(k)
                x += w
                k += 1
            near = np.array(ks)[np.argmin(np.abs(xs[:, None] - np.array(cs)[None, :]), axis=1)]
            r0 = 0 if li == 0 else pad + li * lh
            r1 = th if li == len(lines) - 1 else pad + (li + 1) * lh
            idx_map[r0:r1, :] = near[None, :]
        self.n = k
        self.idx = idx_map
        self.text_a = np.asarray(img, np.float32) / 255
        halo = img.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(14))
        self.halo_a = np.clip(np.asarray(halo, np.float32) / 255 * 2.2, 0, 1)
        self.w, self.h = tw, th
        self.x = (W - tw) // 2
        self.y = int(cy - th / 2)
        light = style == "light"
        self.tcol = np.array((250, 243, 230) if light else (58, 44, 37), np.float32) / 255
        self.hcol = np.array((30, 30, 44) if light else (246, 238, 222), np.float32) / 255
        self.hmax = 0.5 if light else 0.78
        self.step = 0.055
        self.fade_in = 0.35

    def composite(self, img, t):
        if not (self.t0 <= t <= self.t1):
            return
        i = np.arange(self.n)
        a = np.clip((t - self.t0 - i * self.step) / self.fade_in, 0, 1)
        a = a * a * (3 - 2 * a) * clamp((self.t1 - t) / 0.4)
        am = a[self.idx]
        region = img[self.y:self.y + self.h, self.x:self.x + self.w]
        ha = (self.halo_a * am * self.hmax)[..., None]
        region[:] = region * (1 - ha) + self.hcol * ha
        ta = (self.text_a * am)[..., None]
        region[:] = region * (1 - ta) + self.tcol * ta


# ---------------------------------------------------------------- 书：片头 / 片尾
def table_bg(c, t):
    with keep():
        c.set_source_rgb(*TABLE)
        c.paint()
        for i in range(52):
            y = i * 38
            pts = [(x, y + 8 * math.sin(x * 0.005 + i)) for x in range(-40, W + 80, 80)]
            line(c, pts, f"grain{i}", 2, hexc("6a442c"), alpha=0.6, amp=2)
        glow(c, W / 2, H * 0.42, 1300, hexc("ffd8a0"), 0.3)


def cover_face(c, x, y, w, h, title="此心安处", key="cv"):
    with keep():
        shape(c, rect(x, y, w, h), COVER + (1.0,), key, lw=3)
        from draw import ink_style
        with ink_style(GOLD):
            shape(c, rect(x + 24, y + 24, w - 48, h - 48), None, key + "b2", lw=2.4)
            shape(c, rect(x + 34, y + 34, w - 68, h - 68), None, key + "b3", lw=1.4)
        text(c, title, x + w / 2, y + h * 0.3, 64, GOLD)
        cx, cy = x + w / 2, y + h * 0.6
        c.new_path()
        c.arc(cx + 80, cy - 70, 28, 0, 2 * math.pi)
        c.set_source_rgba(*GOLD, 0.95)
        c.set_line_width(2.4)
        c.stroke()
        with ink_style(GOLD):
            line(c, [(cx - 170, cy + 40), (cx - 100, cy + 30), (cx - 40, cy + 42), (cx + 20, cy + 32),
                     (cx + 90, cy + 42), (cx + 170, cy + 34)], key + "wave", 2.4, GOLD)
        from draw import person
        c.push_group()
        person(c, cx - 40, cy + 36, 0.5, view="back", key="cvg", blink=False)
        pat = c.pop_group()
        c.set_source_rgba(*GOLD, 1)
        c.mask(pat)


def page_paper(c, x, y, w, h, key):
    with keep():
        shape(c, rect(x, y, w, h), PAGE + (1.0,), key, lw=1.5, amp=0.6)


def chapter_page(c, x, y, w, h, no, title, illus=None):
    page_paper(c, x, y, w, h, "chp")
    with keep():
        text(c, no, x + w / 2, y + h * 0.36, 40, INK, a=0.85)
        text(c, title, x + w / 2, y + h * 0.52, 104, INK)
        line(c, [(x + w * 0.3, y + h * 0.6), (x + w * 0.7, y + h * 0.6)], "chl", 2, hexc("b48a4f"))
        if illus:
            illus(c, x + w / 2, y + h * 0.78)


def door_illus(c, cx, cy):
    """章节页小插画：门缝里透出的光。"""
    with keep():
        shape(c, rect(cx - 45, cy - 90, 90, 150), hexc("8c5a3c"), "di_f", lw=2.4)
        glow(c, cx + 20, cy - 10, 120, hexc("ffe9b0"), 0.7)
        shape(c, [(cx - 34, cy - 80), (cx + 4, cy - 80), (cx + 4, cy + 54), (cx - 34, cy + 54)], hexc("a8744f"), "di_d", lw=2.2)
        c.move_to(cx + 4, cy - 80)
        c.line_to(cx + 34, cy - 80)
        c.line_to(cx + 34, cy + 54)
        c.line_to(cx + 4, cy + 54)
        c.close_path()
        c.set_source_rgba(1, 0.95, 0.78, 1)
        c.fill()
        c.move_to(cx + 4, cy + 54)
        c.line_to(cx + 34, cy + 54)
        c.line_to(cx + 120, cy + 110)
        c.line_to(cx - 10, cy + 110)
        c.close_path()
        c.set_source_rgba(1, 0.92, 0.7, 0.55)
        c.fill()


BOOK_W, BOOK_H = 470, 680


def book_intro(c, t, no, title, illus=None, dur=6.0):
    """封面 → 翻开 → 翻几页 → 停在章节页 → 推进。"""
    table_bg(c, t)
    bw, bh = BOOK_W, BOOK_H
    spine_x0 = W / 2 - bw / 2
    by = H * 0.42 - bh / 2
    open_u = ease_io(prog(t, 0.9, 1.0))
    shift = (bw / 2) * open_u            # 书脊从左移到中间
    sx = spine_x0 + shift
    zoom = ease_in(prog(t, 4.6, 1.4))
    k = 1 + 2.6 * zoom
    with keep():
        c.save()
        c.translate(sx + bw / 2, by + bh / 2)
        c.scale(k, k)
        c.translate(-(sx + bw / 2), -(by + bh / 2))
        c.rectangle(sx - bw * open_u + 16, by + 22, bw * (1 + open_u), bh)
        c.set_source_rgba(0, 0, 0, 0.3)
        c.fill()
        if open_u > 0:
            shape(c, rect(sx - bw - 14, by - 14, bw + 14, bh + 28), COVER + (1.0,), "bkL", lw=3)
            page_paper(c, sx - bw, by, bw, bh, "pgL")
            for i in range(6):
                line(c, [(sx - bw + 60, by + 120 + i * 50), (sx - 70 - (i % 3) * 40, by + 120 + i * 50)],
                     f"pl{i}", 2, hexc("cbbd9f"), alpha=0.7)
        shape(c, rect(sx, by - 14, bw + 14, bh + 28), COVER + (1.0,), "bkR", lw=3)
        chapter_page(c, sx, by, bw, bh, no, title, illus)
        # 快速翻页
        for j, t0 in enumerate((2.2, 2.65, 3.1)):
            u = ease_io(prog(t, t0, 0.5))
            if 0 < u < 1:
                th = u * math.pi
                wv = math.cos(th)
                if wv > 0:
                    page_paper(c, sx, by, bw * wv, bh, f"fp{j}")
                else:
                    page_paper(c, sx + bw * wv, by, -bw * wv, bh, f"fpb{j}")
                c.rectangle(sx, by, bw, bh)
                c.set_source_rgba(0, 0, 0, 0.12 * math.sin(th))
                c.fill()
            elif t < t0:
                page_paper(c, sx, by, bw, bh, f"fpw{j}")
        # 封面翻开
        if open_u < 1:
            th = open_u * math.pi
            wv = math.cos(th)
            if wv > 0:
                c.save()
                c.translate(sx, 0)
                c.scale(max(wv, 0.001), 1)
                c.translate(-sx, 0)
                cover_face(c, sx, by - 14, bw + 14, bh + 28)
                c.restore()
            else:
                shape(c, rect(sx + (bw + 14) * wv, by - 14, -(bw + 14) * wv, bh + 28), COVER_DARK + (1.0,), "cvin", lw=3)
        c.restore()
    fl = ease_in(prog(t, 5.5, 0.5))
    if fl > 0:
        c.set_source_rgba(*PAGE, fl)
        c.paint()


def book_outro(c, t, still, last_line, end_mark=""):
    """画面缩回书页 → 翻到最后一页 → 版权信息。"""
    table_bg(c, t)
    bw, bh = BOOK_W, BOOK_H
    sx = W / 2
    by = H * 0.42 - bh / 2
    z = ease_io(prog(t, 0.0, 1.4))
    with keep():
        c.rectangle(sx - bw + 16, by + 22, 2 * bw, bh)
        c.set_source_rgba(0, 0, 0, 0.3)
        c.fill()
        shape(c, rect(sx - bw - 14, by - 14, 2 * bw + 28, bh + 28), COVER + (1.0,), "obk", lw=3)
        page_paper(c, sx - bw, by, bw, bh, "opL")
        page_paper(c, sx, by, bw, bh, "opR")
        # 最后一幕画面贴在右页，翻过去
        u = ease_io(prog(t, 1.7, 0.9))
        th = u * math.pi
        wv = math.cos(th)
        rx0, ry0, rw, rh = lerp_rect((0, 0, W, H), (sx + 30, by + 40, bw - 60, bh - 80), z)
        if wv > 0:
            c.save()
            c.translate(sx, 0)
            c.scale(max(wv, 0.001), 1)
            c.translate(-sx, 0)
            if u > 0:
                page_paper(c, sx, by, bw, bh, "opR2")
            c.save()
            c.rectangle(rx0, ry0, rw, rh)
            c.clip()
            c.translate(rx0, ry0)
            c.scale(rw / W, rh / H)
            c.set_source_surface(still, 0, 0)
            c.paint()
            c.restore()
            c.restore()
        else:
            page_paper(c, sx + bw * wv, by, -bw * wv, bh, "opB")
        line(c, [(sx, by), (sx, by + bh)], "spine", 2, hexc("b7a888"))
        a = ease_io(prog(t, 2.5, 0.9))
        if a > 0:
            cx = sx + bw / 2
            text(c, end_mark, cx, by + bh * 0.42, 40, INK, a=a * 0.85)
            line(c, [(cx - 70, by + bh * 0.47), (cx + 70, by + bh * 0.47)], "endl", 2, hexc("b48a4f"), alpha=a)
            for k, ln in enumerate(last_line.split("\n")):
                text(c, ln, cx, by + bh * 0.72 + k * 46, 30, INK, a=a * 0.85)


def lerp_rect(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


# ---------------------------------------------------------------- 合成
class Renderer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.paper = None
        self.subs = None

    def scene_at(self, t):
        sc = self.cfg.SCENES
        for i, (a, b, fn) in enumerate(sc):
            if a <= t < b or i == len(sc) - 1:
                return i

    def draw_scene(self, t, idx):
        a, b, fn = self.cfg.SCENES[idx]
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(surf)
        c.set_source_rgb(0.957, 0.918, 0.847)
        c.paint()
        set_time(t)
        set_grade(**self.cfg.grade_at(t))
        fn(c, clamp(t - a, 0, b - a - 1e-3))
        return surf

    def surface(self, t):
        for tb, kind in self.cfg.TRANSITIONS:
            half = 0.35
            if tb - half <= t < tb + half:
                ia = self.scene_at(tb - 0.01)
                A = self.draw_scene(min(t, tb - 0.001), ia)
                B = self.draw_scene(max(t, tb), ia + 1)
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
                g = cairo.LinearGradient(edge, 0, edge + 110, 0)
                g.add_color_stop_rgba(0, 0, 0, 0, 0.35)
                g.add_color_stop_rgba(1, 0, 0, 0, 0)
                c.set_source(g)
                c.paint()
                c.restore()
                fw = min(150, (W - edge) * 0.35) * math.sin(math.pi * p)
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
        return self.draw_scene(t, self.scene_at(t))

    def frame(self, t):
        if self.paper is None:
            self.paper = make_paper()
            self.subs = [Sub(*s) for s in self.cfg.SUBS]
        surf = self.surface(t)
        surf.flush()
        arr = np.ndarray((H, W, 4), np.uint8, surf.get_data())
        img = arr[..., [2, 1, 0]].astype(np.float32) / 255
        img *= self.paper
        for s in self.subs:
            s.composite(img, t)
        return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


_R = None


def _chunk(args):
    cfg_name, wid, f0, f1, out_dir = args
    import importlib
    cfg = importlib.import_module(cfg_name)
    r = Renderer(cfg)
    path = os.path.join(out_dir, f"part{wid}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(r.frame(f / FPS).tobytes())
        if (f - f0) % 90 == 0:
            print(f"[w{wid}] {f - f0}/{f1 - f0}", flush=True)
    p.stdin.close()
    p.wait()
    return path


def render_video(cfg_name, cfg, out_dir, workers=None):
    os.makedirs(out_dir, exist_ok=True)
    nf = int(round(cfg.DUR * FPS))
    nw = workers or os.cpu_count() or 4
    step = math.ceil(nf / nw)
    jobs = [(cfg_name, i, i * step, min(nf, (i + 1) * step), out_dir) for i in range(nw)]
    with Pool(nw) as pool:
        parts = pool.map(_chunk, jobs)
    lst = os.path.join(out_dir, "parts.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    out = os.path.join(out_dir, "video_silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
    return out


def render_keyframes(cfg, ts, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    r = Renderer(cfg)
    paths = []
    for t in ts:
        p = os.path.join(out_dir, f"key_{t:06.2f}.png")
        Image.fromarray(r.frame(t)).save(p)
        paths.append(p)
    return paths

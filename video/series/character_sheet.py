"""人物设定图：对比不同发型（正面 / 戴帽 / 背面 / 侧看）。

  python character_sheet.py out.png bob sweep pony braids
"""
import sys

import cairo

from draw import INK, girl, hexc, set_time, text

STYLES = {"bob": "现在的发型", "sweep": "A 侧分短发", "pony": "B 低马尾", "braids": "C 双麻花辫",
          "bang_short": "D 齐刘海短发", "bang_long": "E 齐刘海长发", "curtain_long": "F 八字刘海长发"}


def main(path, styles):
    cw, rh = 1000, 560
    W_, H_ = cw * 4, rh * len(styles) + 120
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W_, H_)
    c = cairo.Context(surf)
    c.set_source_rgb(*hexc("f4ead8"))
    c.paint()
    set_time(0.3)
    for j, lab in enumerate(("正面", "戴草帽", "背面", "转头看")):
        text(c, lab, cw * j + cw / 2, 80, 56, INK)
    for i, st in enumerate(styles):
        y = 120 + rh * i + rh - 40
        text(c, STYLES.get(st, st), 30, 120 + rh * i + 70, 52, hexc("b5473c"), anchor="l")
        kw = dict(hair_style=st, pack=False, key=f"cs{st}")
        girl(c, cw * 0.5, y, 2.4, hat=False, **kw)
        girl(c, cw * 1.5, y, 2.4, hat=True, **kw)
        girl(c, cw * 2.5, y, 2.4, hat=True, view="back", **{**kw, "pack": True})
        girl(c, cw * 3.5, y, 2.4, hat=False, look=1.0, mouth="laugh", **kw)
    surf.write_to_png(path)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or list(STYLES))

# -*- coding: utf-8 -*-
"""把八张表情拼成一张「小鱼写真集」封面。"""
import os

from PIL import Image, ImageDraw, ImageFont

SRC = r"E:\Agent-bluefish\working\小鱼表情包"
OUT = os.path.join(SRC, "小鱼写真集.png")
CELL = 240
GAP = 20
COLS = 3
TITLE_H = 90
W = CELL * COLS + GAP * (COLS + 1)
H = CELL * 3 + GAP * 4 + TITLE_H

FONT = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_L = r"C:\Windows\Fonts\msyh.ttc"


def main():
    files = sorted(f for f in os.listdir(SRC) if f.endswith(".png") and f[0].isdigit())
    files = files[:8]
    canvas = Image.new("RGB", (W, H), (243, 248, 253))
    d = ImageDraw.Draw(canvas)

    # 标题
    f1 = ImageFont.truetype(FONT, 38)
    f2 = ImageFont.truetype(FONT_L, 18)
    d.text((GAP, 18), "小鱼的写真集", font=f1, fill=(44, 90, 140))
    d.text((GAP + 1, 60), "a small fish living in a computer", font=f2, fill=(120, 150, 180))

    # 九宫格，中心留给名字
    positions = [0, 1, 2, 3, 5, 6, 7, 8]
    for idx, fname in enumerate(files):
        slot = positions[idx]
        r, c = divmod(slot, COLS)
        x = GAP + c * (CELL + GAP)
        y = TITLE_H + GAP + r * (CELL + GAP)
        im = Image.open(os.path.join(SRC, fname)).convert("RGBA").resize((CELL, CELL), Image.LANCZOS)
        canvas.paste(im, (x, y), im)

    # 中心格
    c = 1
    r = 1
    x = GAP + c * (CELL + GAP)
    y = TITLE_H + GAP + r * (CELL + GAP)
    d.rounded_rectangle([x, y, x + CELL, y + CELL], radius=28, fill=(214, 234, 248))
    f3 = ImageFont.truetype(FONT, 52)
    f4 = ImageFont.truetype(FONT_L, 20)
    title = "小鱼"
    tw = d.textlength(title, font=f3)
    d.text((x + (CELL - tw) / 2, y + 78), title, font=f3, fill=(44, 90, 140))
    sub = "阿冉的"
    sw = d.textlength(sub, font=f4)
    d.text((x + (CELL - sw) / 2, y + 146), sub, font=f4, fill=(120, 150, 180))

    canvas.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()

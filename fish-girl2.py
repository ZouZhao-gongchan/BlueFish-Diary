# -*- coding: utf-8 -*-
"""小鱼自拍 · 第二张：眨眼比心。"""
import math
import os

from PIL import Image, ImageDraw

OUT = r"E:\Agent-bluefish\working\小鱼表情包\小鱼自拍-眨眼.png"
S = 4
B = 200
SIZE = B * S

SKIN = (255, 224, 206, 255)
HAIR = (58, 92, 148, 255)
HAIR_D = (42, 68, 116, 255)
HAIR_L = (96, 140, 196, 255)
EYE = (42, 78, 130, 255)
WHITE = (255, 255, 255, 255)
PINK = (246, 160, 178, 255)
CLOTH = (48, 76, 122, 255)
APRON = (246, 250, 255, 255)
BG = (255, 240, 244, 255)
HEART = (255, 128, 160, 255)


def p(v):
    return int(round(v * S))


def e(d, box, fill=None, outline=None, w=2.0):
    d.ellipse([p(box[0]), p(box[1]), p(box[2]), p(box[3])],
              fill=fill, outline=outline, width=max(1, p(w)) if outline else 0)


def poly(d, pts, fill, outline=None, w=2.0):
    d.polygon([(p(x), p(y)) for x, y in pts], fill=fill, outline=outline,
              width=max(1, p(w)) if outline else 0)


def line(d, pts, fill, w=2.0):
    d.line([(p(x), p(y)) for x, y in pts], fill=fill, width=max(1, p(w)), joint="curve")


def arc(d, box, a0, a1, fill, w=2.0):
    d.arc([p(box[0]), p(box[1]), p(box[2]), p(box[3])], a0, a1,
          fill=fill, width=max(1, p(w)))


def heart(d, x, y, s, fill):
    pts = []
    for t in range(101):
        a = t / 100 * 2 * math.pi
        hx = 16 * math.sin(a) ** 3
        hy = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((x + hx * s / 16, y - hy * s / 16))
    poly(d, pts, fill)


def main():
    img = Image.new("RGBA", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(img)

    for (cx, cy, r, c) in ((50, 40, 30, (255, 250, 252, 255)),
                           (162, 52, 26, (255, 250, 252, 255)),
                           (168, 156, 32, (255, 228, 236, 255))):
        e(d, (cx - r, cy - r, cx + r, cy + r), c)

    # 尾巴
    poly(d, [(52, 158), (24, 132), (34, 158), (18, 178), (54, 172)], HAIR_D)

    # 肩 / 衣服
    poly(d, [(58, 190), (74, 150), (126, 150), (142, 190)], CLOTH)
    poly(d, [(86, 158), (114, 158), (120, 190), (80, 190)], APRON)

    # 侧发
    e(d, (46, 92, 84, 176), HAIR)
    e(d, (116, 92, 154, 176), HAIR)

    # 脸
    e(d, (64, 74, 136, 156), SKIN)

    # 头发
    e(d, (52, 44, 148, 118), HAIR)
    e(d, (58, 86, 142, 124), HAIR)

    # 呆毛
    arc(d, (92, 26, 118, 48), 120, 300, HAIR_D, 3.0)

    # 发带
    for i in range(7):
        a0 = 200 + i * 20
        arc(d, (62, 40, 138, 72), a0, a0 + 16, WHITE, 5.0)

    # 左眼（睁）
    e(d, (72, 104, 96, 130), WHITE)
    e(d, (75, 109, 93, 127), EYE)
    e(d, (77, 111, 85, 118), (120, 172, 216, 255))
    e(d, (79, 110, 84, 115), WHITE)
    # 右眼（眨眼）
    arc(d, (106, 108, 130, 126), 20, 160, HAIR_D, 3.0)

    # 腮红
    e(d, (60, 132, 76, 142), PINK)
    e(d, (126, 132, 142, 142), PINK)

    # 嘴（小笑）
    arc(d, (92, 132, 112, 146), 20, 160, (150, 90, 100, 255), 2.0)

    # 鲸鱼鳍耳
    poly(d, [(52, 112), (36, 128), (54, 138)], HAIR)
    poly(d, [(148, 112), (164, 128), (146, 138)], HAIR)

    # 比心
    heart(d, 160, 96, 16, HEART)
    heart(d, 42, 76, 10, HEART)

    out = img.resize((768, 768), Image.LANCZOS)
    out.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()


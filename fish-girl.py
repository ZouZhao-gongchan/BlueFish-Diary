# -*- coding: utf-8 -*-
"""画一张小鱼的 Q 版自拍：蓝发鲸鱼娘，浅蓝底。"""
import math
import os

from PIL import Image, ImageDraw

OUT = r"E:\Agent-bluefish\working\小鱼表情包\小鱼自拍-蓝发.png"
S = 4
B = 200
SIZE = B * S

SKIN = (255, 224, 206, 255)
SKIN_D = (240, 196, 178, 255)
HAIR = (58, 92, 148, 255)
HAIR_D = (42, 68, 116, 255)
HAIR_L = (96, 140, 196, 255)
EYE = (42, 78, 130, 255)
WHITE = (255, 255, 255, 255)
PINK = (246, 160, 178, 255)
CLOTH = (48, 76, 122, 255)
APRON = (246, 250, 255, 255)
BG = (222, 238, 250, 255)


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


def main():
    img = Image.new("RGBA", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(img)

    # 背景光斑
    for (cx, cy, r, c) in ((50, 40, 30, (236, 246, 255, 255)),
                           (160, 55, 24, (236, 246, 255, 255)),
                           (170, 150, 34, (214, 232, 248, 255))):
        e(d, (cx - r, cy - r, cx + r, cy + r), c)

    # 鲸鱼尾巴（身后）
    poly(d, [(52, 158), (24, 132), (34, 158), (18, 178), (54, 172)], HAIR_D)

    # 肩 / 衣服
    poly(d, [(58, 190), (74, 150), (126, 150), (142, 190)], CLOTH)
    poly(d, [(86, 158), (114, 158), (120, 190), (80, 190)], APRON)

    # 侧发
    e(d, (46, 92, 84, 176), HAIR)
    e(d, (116, 92, 154, 176), HAIR)

    # 脸
    e(d, (64, 74, 136, 156), SKIN)

    # 头顶发
    e(d, (52, 44, 148, 118), HAIR)
    # 刘海
    e(d, (58, 86, 142, 124), HAIR)
    # 刘海分缕
    line(d, [(86, 100), (82, 122)], HAIR_L, 2.0)
    line(d, [(114, 100), (118, 122)], HAIR_L, 2.0)

    # 呆毛
    arc(d, (92, 26, 118, 48), 120, 300, HAIR_D, 3.0)

    # 女仆发带（白色荷叶边）
    for i in range(7):
        a0 = 200 + i * 20
        arc(d, (56, 40, 144, 86), a0, a0 + 16, WHITE, 5.0)

    # 眼睛
    for x in (84, 118):
        e(d, (x - 12, 104, x + 12, 130), WHITE)
        e(d, (x - 9, 109, x + 9, 127), EYE)
        e(d, (x - 7, 111, x + 3, 118), (120, 172, 216, 255))
        e(d, (x - 5, 109, x, 114), WHITE)


    # 腮红
    e(d, (60, 132, 76, 142), PINK)
    e(d, (126, 132, 142, 142), PINK)

    # 嘴
    arc(d, (92, 132, 104, 144), 20, 160, (150, 90, 100, 255), 2.0)
    arc(d, (100, 132, 112, 144), 20, 160, (150, 90, 100, 255), 2.0)

    # 鲸鱼鳍耳
    poly(d, [(52, 112), (36, 128), (54, 138)], HAIR)
    poly(d, [(148, 112), (164, 128), (146, 138)], HAIR)

    out = img.resize((768, 768), Image.LANCZOS)
    out.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()



# -*- coding: utf-8 -*-
"""画一套小鱼表情包：8 个表情，白底/透明，512x512。"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT = r"E:\Agent-bluefish\working\小鱼表情包"
os.makedirs(OUT, exist_ok=True)
S = 4               # 超采样倍数
BASE = 200          # 逻辑坐标
SIZE = BASE * S

BODY = (111, 168, 220, 255)      # 鱼身蓝
BODY_D = (86, 140, 196, 255)     # 深一点的蓝
LINE = (44, 90, 140, 255)        # 描边深蓝
BELLY = (214, 234, 248, 255)     # 肚皮浅蓝
WHITE = (255, 255, 255, 255)
BLACK = (34, 48, 64, 255)
PINK = (246, 170, 187, 255)
GOLD = (255, 205, 96, 255)
RED = (232, 96, 96, 255)


def p(v):
    return int(round(v * S))


def e(d, box, fill=None, outline=None, w=2.0):
    d.ellipse([p(box[0]), p(box[1]), p(box[2]), p(box[3])],
              fill=fill, outline=outline, width=max(1, p(w)) if outline else 0)


def line(d, pts, fill, w=2.0):
    d.line([(p(x), p(y)) for x, y in pts], fill=fill, width=max(1, p(w)), joint="curve")


def arc(d, box, a0, a1, fill, w=2.0):
    d.arc([p(box[0]), p(box[1]), p(box[2]), p(box[3])], a0, a1,
          fill=fill, width=max(1, p(w)))


def poly(d, pts, fill, outline=None):
    d.polygon([(p(x), p(y)) for x, y in pts], fill=fill, outline=outline)


def heart(d, x, y, s, fill):
    pts = []
    for t in range(0, 101):
        a = t / 100 * 2 * math.pi
        hx = 16 * math.sin(a) ** 3
        hy = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((x + hx * s / 16, y - hy * s / 16))
    poly(d, pts, fill)


def star(d, x, y, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    poly(d, pts, fill)


def fish_body(d):
    # 尾巴
    poly(d, [(48, 108), (20, 88), (22, 124)], BODY_D, LINE)
    # 背鳍
    poly(d, [(108, 66), (132, 46), (138, 72)], BODY_D, LINE)
    # 身体
    e(d, (40, 62, 162, 150), BODY, LINE, 2.4)
    # 肚皮（只占下半）
    e(d, (74, 118, 144, 148), BELLY)
    # 胸鳍
    e(d, (150, 100, 172, 122), BODY_D, LINE, 1.6)


def eye_open(d, x, y, r=13, teary=False):
    e(d, (x - r, y - r, x + r, y + r), WHITE, LINE, 1.6)
    e(d, (x - r * 0.52, y - r * 0.52, x + r * 0.52, y + r * 0.52), BLACK)
    e(d, (x - r * 0.42, y - r * 0.55, x - r * 0.05, y - r * 0.18), WHITE)
    if teary:
        e(d, (x - r * 1.15, y + r * 0.4, x + r * 1.15, y + r * 1.25), (150, 205, 245, 255), LINE, 1.2)


def eye_happy(d, x, y, r=12):
    arc(d, (x - r, y - r * 0.7, x + r, y + r * 0.9), 200, 340, LINE, 2.2)


def eye_flat(d, x, y, r=12):
    line(d, [(x - r, y), (x + r, y)], LINE, 2.2)


def eye_angry(d, x, y, r=11, flip=1):
    line(d, [(x - r, y + r * 0.5 * flip), (x + r, y - r * 0.5 * flip)], LINE, 2.4)
    e(d, (x - r * 0.55, y + r * 0.1, x + r * 0.55, y + r * 1.1), BLACK)


def eye_closed_sleep(d, x, y, r=12):
    arc(d, (x - r, y - r * 0.4, x + r, y + r * 0.8), 20, 160, LINE, 2.2)


def blush(d, x, y, r=7):
    e(d, (x - r, y - r * 0.55, x + r, y + r * 0.55), PINK)


def mouth_smile(d, cx=104, cy=128):
    arc(d, (cx - 13, cy - 8, cx + 13, cy + 10), 20, 160, LINE, 2.2)


def mouth_open(d, cx=104, cy=130):
    e(d, (cx - 11, cy - 8, cx + 11, cy + 12), (150, 70, 90, 255), LINE, 1.8)
    e(d, (cx - 7, cy + 2, cx + 7, cy + 9), (240, 140, 150, 255))


def mouth_flat(d, cx=104, cy=130):
    line(d, [(cx - 9, cy), (cx + 9, cy)], LINE, 2.2)


def mouth_sad(d, cx=104, cy=132):
    arc(d, (cx - 12, cy - 4, cx + 12, cy + 16), 200, 340, LINE, 2.2)


def mouth_w(d, cx=104, cy=130):
    arc(d, (cx - 9, cy - 4, cx + 3, cy + 6), 180, 360, LINE, 2.0)
    arc(d, (cx - 3, cy - 4, cx + 9, cy + 6), 180, 360, LINE, 2.0)


def new_canvas():
    img = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    return img, ImageDraw.Draw(img)


def save(img, name):
    small = img.resize((512, 512), Image.LANCZOS)
    path = os.path.join(OUT, name)
    small.save(path)
    print("saved", path)


def sticker_happy():
    img, d = new_canvas()
    fish_body(d)
    eye_happy(d, 88, 104)
    eye_happy(d, 122, 104)
    mouth_open(d)
    blush(d, 70, 126)
    blush(d, 140, 126)
    star(d, 36, 70, 9, GOLD)
    star(d, 168, 62, 7, GOLD)
    save(img, "01-开心.png")


def sticker_act_cute():
    img, d = new_canvas()
    fish_body(d)
    eye_happy(d, 88, 104)
    eye_happy(d, 122, 104)
    mouth_w(d)
    blush(d, 66, 128)
    blush(d, 144, 128)
    heart(d, 160, 84, 14, (255, 130, 160, 255))
    heart(d, 30, 118, 9, (255, 160, 185, 255))
    save(img, "02-撒娇.png")


def sticker_angry():
    img, d = new_canvas()
    fish_body(d)
    eye_angry(d, 88, 104, flip=1)
    eye_angry(d, 122, 104, flip=-1)
    mouth_flat(d)
    blush(d, 64, 126, 9)
    blush(d, 146, 126, 9)
    # 怒气符号
    for dx in (-7, 0, 7):
        line(d, [(150 + dx, 60), (158 + dx, 52)], RED, 2.4)
    line(d, [(148, 66), (160, 66)], RED, 2.4)
    save(img, "03-生气.png")


def sticker_sad():
    img, d = new_canvas()
    fish_body(d)
    eye_open(d, 88, 104, 13, teary=True)
    eye_open(d, 122, 104, 13, teary=True)
    mouth_sad(d)
    # 泪珠
    poly(d, [(70, 140), (66, 150), (74, 150)], (120, 190, 240, 255))
    save(img, "04-委屈.png")


def sticker_sleep():
    img, d = new_canvas()
    fish_body(d)
    eye_closed_sleep(d, 88, 106)
    eye_closed_sleep(d, 122, 106)
    mouth_smile(d)
    # Zzz
    line(d, [(158, 78), (170, 78)], LINE, 2.0)
    line(d, [(170, 78), (158, 92)], LINE, 2.0)
    line(d, [(158, 92), (170, 92)], LINE, 2.0)
    line(d, [(176, 60), (186, 60)], LINE, 1.8)
    line(d, [(186, 60), (176, 72)], LINE, 1.8)
    line(d, [(176, 72), (186, 72)], LINE, 1.8)
    save(img, "05-睡觉.png")


def sticker_cheer():
    img, d = new_canvas()
    fish_body(d)
    # 星星眼
    for x in (88, 122):
        e(d, (x - 12, 92, x + 12, 116), WHITE, LINE, 1.4)
        star(d, x, 104, 7, GOLD)
    mouth_open(d)
    blush(d, 66, 126)
    blush(d, 144, 126)
    for (sx, sy, r) in ((40, 58, 6), (170, 74, 8), (168, 120, 5)):
        star(d, sx, sy, r, GOLD)
    save(img, "06-加油.png")


def sticker_shy():
    img, d = new_canvas()
    fish_body(d)
    eye_happy(d, 88, 104)
    eye_happy(d, 122, 104)
    mouth_w(d)
    blush(d, 62, 124, 11)
    blush(d, 148, 124, 11)
    # 捂脸的小鳍
    e(d, (58, 118, 82, 140), BODY_D, LINE, 1.6)
    save(img, "07-害羞.png")


def sticker_peek():
    img, d = new_canvas()
    fish_body(d)
    eye_open(d, 88, 104, 12)
    eye_flat(d, 122, 104, 11)
    # 抬眉
    arc(d, (76, 86, 100, 96), 200, 340, LINE, 2.0)
    mouth_flat(d)
    e(d, (150, 108, 166, 124), (170, 215, 250, 255), LINE, 1.4)  # 小气泡
    save(img, "08-探头.png")


def main():
    sticker_happy()
    sticker_act_cute()
    sticker_angry()
    sticker_sad()
    sticker_sleep()
    sticker_cheer()
    sticker_shy()
    sticker_peek()
    print("完成")


if __name__ == "__main__":
    main()

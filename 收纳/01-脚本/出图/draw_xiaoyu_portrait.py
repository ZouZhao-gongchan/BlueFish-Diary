# -*- coding: utf-8 -*-
"""画一张小鱼的「魅力写真」：蓝发鱼少女半身像（Pillow 超采样）。"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 1024
SS = 2
W = S * SS

def P(x, y):
    return (x * SS, y * SS)

def BOX(x0, y0, x1, y1):
    return [x0 * SS, y0 * SS, x1 * SS, y1 * SS]

def bez(p0, p1, p2, p3, n=120):
    out = []
    for i in range(n + 1):
        t = i / n
        m = 1 - t
        x = m ** 3 * p0[0] + 3 * m * m * t * p1[0] + 3 * m * t * t * p2[0] + t ** 3 * p3[0]
        y = m ** 3 * p0[1] + 3 * m * m * t * p1[1] + 3 * m * t * t * p2[1] + t ** 3 * p3[1]
        out.append(P(x, y))
    return out

def vgrad(size, top, bot):
    img = Image.new("RGB", (1, size[1]))
    px = img.load()
    for y in range(size[1]):
        t = y / (size[1] - 1)
        px[0, y] = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    return img.resize(size, Image.BILINEAR)

def radial(size, color, cx, cy, radius, strength=255, power=2.0):
    """柔和径向光斑（RGBA）。"""
    w = h = int(radius * 2)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - radius) ** 2 + (yy - radius) ** 2) / radius
    a = np.clip(1.0 - d, 0, 1) ** power * strength
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = color
    rgba[..., 3] = a.astype(np.uint8)
    layer = Image.fromarray(rgba, "RGBA")
    base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    base.alpha_composite(layer, (int(cx - radius), int(cy - radius)))
    return base

BG_TOP = (7, 24, 50)
BG_BOT = (14, 62, 94)
HAIR = (46, 78, 138)
HAIR_D = (28, 50, 98)
HAIR_L = (104, 152, 220)
SKIN = (255, 233, 221)
SKIN_SH = (244, 203, 191)
BLUSH = (255, 143, 165)
IRIS_T = (86, 178, 255)
IRIS_B = (18, 62, 140)
DARK = (20, 32, 62)
WHITE = (255, 255, 255)
LIP = (228, 116, 130)
SHIRT = (246, 250, 255)
SHIRT_SH = (208, 221, 242)
RIBBON = (72, 156, 226)
FIN = (150, 230, 255)

canvas = Image.new("RGBA", (W, W), (0, 0, 0, 255))
canvas.alpha_composite(vgrad((W, W), BG_TOP, BG_BOT).convert("RGBA"))

# 水底光柱
rays = Image.new("RGBA", (W, W), (0, 0, 0, 0))
rd = ImageDraw.Draw(rays)
for i, (x0, wid) in enumerate([(120, 90), (330, 60), (640, 120), (820, 70)]):
    rd.polygon([P(x0, -40), P(x0 + wid, -40), P(x0 + wid + 260, 1064), P(x0 + 210, 1064)],
               fill=(120, 220, 255, 20))
rays = rays.filter(ImageFilter.GaussianBlur(30 * SS))
canvas.alpha_composite(rays)

# 光斑
for cx, cy, r, a in [(250, 190, 260, 70), (800, 300, 210, 55), (520, 120, 180, 45), (140, 780, 240, 40)]:
    canvas.alpha_composite(radial(W, (130, 225, 255), cx * SS, cy * SS, r * SS, a, 2.2))

# 气泡
bub = Image.new("RGBA", (W, W), (0, 0, 0, 0))
bd = ImageDraw.Draw(bub)
for cx, cy, r in [(150, 520, 34), (128, 610, 18), (205, 690, 11), (886, 540, 26), (916, 610, 14), (860, 700, 9)]:
    bd.ellipse(BOX(cx - r, cy - r, cx + r, cy + r), fill=(190, 240, 255, 46),
               outline=(220, 250, 255, 110), width=int(2 * SS))
    bd.ellipse(BOX(cx - r * 0.45, cy - r * 0.62, cx - r * 0.05, cy - r * 0.24), fill=(255, 255, 255, 120))
canvas.alpha_composite(bub)

# ---------- 后发 ----------
hair_back = Image.new("RGBA", (W, W), (0, 0, 0, 0))
hd = ImageDraw.Draw(hair_back)
outline = []
outline += bez((512, 168), (338, 176), (286, 330), (300, 520))
outline += bez((300, 520), (308, 660), (330, 780), (352, 830))
outline += bez((352, 830), (430, 862), (594, 862), (672, 830))
outline += bez((672, 830), (694, 780), (716, 660), (724, 520))
outline += bez((724, 520), (738, 330), (686, 176), (512, 168))
hd.polygon(outline, fill=HAIR_D + (255,))
canvas.alpha_composite(hair_back)

# ---------- 鱼鳍耳（在脸后面） ----------
fins = Image.new("RGBA", (W, W), (0, 0, 0, 0))
fd = ImageDraw.Draw(fins)
for side in (-1, 1):
    base_x = 512 + side * 122
    fin = [P(base_x, 425)]
    fin += bez((base_x, 425), (base_x + side * 78, 366), (base_x + side * 112, 440), (base_x + side * 62, 486))
    fin += bez((base_x + side * 62, 486), (base_x + side * 34, 502), (base_x + side * 14, 492), (base_x, 478))
    fd.polygon(fin, fill=FIN + (115,))
    for k in range(3):
        y0 = 432 + k * 22
        fd.line([P(base_x + side * 12, y0), P(base_x + side * (56 - k * 6), y0 + 26)],
                fill=(210, 250, 255, 85), width=int(2 * SS))
canvas.alpha_composite(fins)

# ---------- 身体 / 衣服 ----------
body = Image.new("RGBA", (W, W), (0, 0, 0, 0))
cd = ImageDraw.Draw(body)
cd.rounded_rectangle(BOX(474, 500, 550, 720), radius=30 * SS, fill=SKIN_SH + (255,))
shirt = [P(300, 960)]
shirt += bez((300, 960), (306, 790), (378, 700), (462, 658))
shirt += [P(562, 658)]
shirt += bez((562, 658), (646, 700), (718, 790), (724, 960))
shirt += [P(724, 1024), P(300, 1024)]
cd.polygon(shirt, fill=SHIRT + (255,))
# 领口阴影（脖子投下的柔影）
neck_sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
nd = ImageDraw.Draw(neck_sh)
nd.ellipse(BOX(472, 588, 552, 664), fill=(198, 212, 234, 120))
neck_sh = neck_sh.filter(ImageFilter.GaussianBlur(18 * SS))
body.alpha_composite(neck_sh)
cd = ImageDraw.Draw(body)
# 水手领
cd.polygon([P(438, 662), P(462, 664), P(512, 768), P(562, 664), P(586, 662), P(586, 686), P(512, 800), P(438, 686)],
           fill=RIBBON + (255,))
cd.line([P(438, 686), P(512, 800), P(586, 686)], fill=(40, 110, 180, 200), width=int(4 * SS))
# 领结
cd.polygon([P(512, 764), P(480, 738), P(480, 800), P(512, 780)], fill=(96, 190, 240, 255))
cd.polygon([P(512, 764), P(544, 738), P(544, 800), P(512, 780)], fill=(96, 190, 240, 255))
cd.ellipse(BOX(502, 756, 522, 784), fill=(150, 220, 252, 255))
canvas.alpha_composite(body)

# ---------- 脸 ----------
face = Image.new("RGBA", (W, W), (0, 0, 0, 0))
fdd = ImageDraw.Draw(face)
fdd.ellipse(BOX(382, 250, 642, 548), fill=SKIN + (255,))
# 下巴
chin = [P(420, 460)]
chin += bez((420, 460), (448, 556), (484, 586), (512, 586))
chin += bez((512, 586), (540, 586), (576, 556), (604, 460))
chin += [P(604, 400), P(420, 400)]
fdd.polygon(chin, fill=SKIN + (255,))
# 脸侧阴影
sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
sd = ImageDraw.Draw(sh)
sd.ellipse(BOX(396, 330, 436, 560), fill=SKIN_SH + (60,))
sd.ellipse(BOX(588, 330, 628, 560), fill=SKIN_SH + (60,))
sh = sh.filter(ImageFilter.GaussianBlur(18 * SS))
fdd.bitmap((0, 0), sh.split()[3], fill=SKIN_SH + (80,))
canvas.alpha_composite(face)

# ---------- 腮红 ----------
blush = Image.new("RGBA", (W, W), (0, 0, 0, 0))
bd2 = ImageDraw.Draw(blush)
for cx in (432, 592):
    bd2.ellipse(BOX(cx - 42, 478, cx + 42, 520), fill=BLUSH + (110,))
blush = blush.filter(ImageFilter.GaussianBlur(14 * SS))
canvas.alpha_composite(blush)

# ---------- 眼睛 ----------
eyes = Image.new("RGBA", (W, W), (0, 0, 0, 0))
ed = ImageDraw.Draw(eyes)
for cx in (455, 569):
    cy = 412
    # 眼白
    ed.ellipse(BOX(cx - 36, cy - 40, cx + 36, cy + 42), fill=WHITE + (255,))
    # 虹膜（渐变）
    iris = Image.new("RGBA", (int(76 * SS), int(86 * SS)), (0, 0, 0, 0))
    ig = Image.new("RGBA", iris.size, (0, 0, 0, 0))
    igd = ImageDraw.Draw(ig)
    for i in range(60, 0, -1):
        t = i / 60
        c = tuple(int(IRIS_T[k] + (IRIS_B[k] - IRIS_T[k]) * (1 - t)) for k in range(3))
        rw = 34 * t * SS
        rh = 40 * t * SS
        igd.ellipse([38 * SS - rw, 43 * SS - rh, 38 * SS + rw, 43 * SS + rh], fill=c + (255,))
    mask = Image.new("L", iris.size, 0)
    ImageDraw.Draw(mask).ellipse([2 * SS, 3 * SS, 74 * SS, 83 * SS], fill=255)
    eyes.paste(ig, (int((cx - 38) * SS), int((cy - 43) * SS)), mask)
    # 瞳孔
    ed.ellipse(BOX(cx - 13, cy - 16, cx + 13, cy + 18), fill=DARK + (255,))
    # 高光
    ed.ellipse(BOX(cx - 24, cy - 28, cx - 2, cy - 6), fill=(255, 255, 255, 245))
    ed.ellipse(BOX(cx + 6, cy + 12, cx + 20, cy + 24), fill=(200, 240, 255, 160))
    # 上睫毛
    lash = []
    lash += bez((cx - 38, cy - 16), (cx - 26, cy - 44), (cx + 26, cy - 46), (cx + 38, cy - 18))
    lash += bez((cx + 38, cy - 18), (cx + 30, cy - 30), (cx - 30, cy - 28), (cx - 38, cy - 16))
    ed.polygon(lash, fill=DARK + (255,))
    # 眼尾
    ed.line([P(cx + 38, cy - 20), P(cx + 50, cy - 34)], fill=DARK + (255,), width=int(5 * SS))
    # 下眼线
    ed.line([P(cx - 28, cy + 38), P(cx + 22, cy + 42)], fill=DARK + (120,), width=int(3 * SS))
eyes = eyes.filter(ImageFilter.GaussianBlur(0.6 * SS))
canvas.alpha_composite(eyes)

# 眉毛
brow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
bd3 = ImageDraw.Draw(brow)
for cx in (455, 569):
    pts = bez((cx - 40, 362), (cx - 14, 343), (cx + 14, 342), (cx + 40, 356))
    bd3.line(pts, fill=(64, 84, 136, 220), width=int(6 * SS), joint="curve")
canvas.alpha_composite(brow)

# 鼻子
nose = Image.new("RGBA", (W, W), (0, 0, 0, 0))
ImageDraw.Draw(nose).ellipse(BOX(512, 452, 526, 462), fill=(226, 176, 170, 190))
canvas.alpha_composite(nose)

# 嘴
mouth = Image.new("RGBA", (W, W), (0, 0, 0, 0))
md = ImageDraw.Draw(mouth)
lip = []
lip += bez((494, 508), (504, 524), (522, 524), (532, 508))
lip += bez((532, 508), (522, 500), (504, 500), (494, 508))
md.polygon(lip, fill=LIP + (235,))
md.line(bez((492, 506), (504, 516), (522, 516), (534, 506)), fill=(176, 78, 94, 190), width=int(3 * SS))
canvas.alpha_composite(mouth)

# ---------- 刘海 ----------
bangs = Image.new("RGBA", (W, W), (0, 0, 0, 0))
bng = ImageDraw.Draw(bangs)
# 头顶发块
cap = []
cap += bez((512, 186), (388, 190), (352, 280), (368, 352))
cap += bez((368, 352), (420, 300), (470, 292), (512, 300))
cap += bez((512, 300), (554, 292), (604, 300), (656, 352))
cap += bez((656, 352), (672, 280), (636, 190), (512, 186))
bng.polygon(cap, fill=HAIR + (255,))
# 束状刘海
for (x0, x1, dip, c) in [(-96, -18, 40, HAIR), (18, 96, 44, HAIR), (-34, 34, 18, HAIR)]:
    pts = [P(512 + x0, 292)]
    pts += bez((512 + x0, 292), (512 + x0 + 6, 330), (512 + x1 - 8, 352), (512 + x1, 300 + dip))
    pts += bez((512 + x1, 300 + dip), (512 + x1 + 6, 272), (512 + x1 - 6, 276), (512 + x0 + 16, 288))
    bng.polygon(pts, fill=c + (255,))
# 两侧发缕
for side in (-1, 1):
    strand = [P(512 + side * 118, 300)]
    strand += bez((512 + side * 118, 300), (512 + side * 150, 420), (512 + side * 148, 560), (512 + side * 128, 640))
    strand += bez((512 + side * 128, 640), (512 + side * 108, 540), (512 + side * 96, 420), (512 + side * 96, 320))
    bng.polygon(strand, fill=HAIR + (255,))
# 发丝高光
for k, (x0, y0, x1, y1) in enumerate([(430, 240, 470, 330), (540, 236, 588, 322), (600, 250, 636, 330)]):
    hl = bez((x0, y0), (x0 + 12, y0 + 30), (x1 - 8, y1 - 30), (x1, y1))
    bng.line(hl, fill=HAIR_L + (110,), width=int(6 * SS))
canvas.alpha_composite(bangs)

# 发饰：右侧小鱼发夹
clip = Image.new("RGBA", (W, W), (0, 0, 0, 0))
cd2 = ImageDraw.Draw(clip)
cd2.ellipse(BOX(618, 214, 676, 262), fill=(120, 210, 245, 255))
cd2.polygon([P(616, 236), P(590, 214), P(592, 258)], fill=(120, 210, 245, 255))
cd2.ellipse(BOX(650, 228, 660, 238), fill=(255, 255, 255, 240))
canvas.alpha_composite(clip)

# ---------- 前景光效 ----------
spark = Image.new("RGBA", (W, W), (0, 0, 0, 0))
sp = ImageDraw.Draw(spark)
def star(cx, cy, r, a=200):
    sp.polygon([P(cx, cy - r), P(cx + r * 0.22, cy - r * 0.22), P(cx + r, cy),
                P(cx + r * 0.22, cy + r * 0.22), P(cx, cy + r),
                P(cx - r * 0.22, cy + r * 0.22), P(cx - r, cy),
                P(cx - r * 0.22, cy - r * 0.22)], fill=(210, 245, 255, a))
for cx, cy, r in [(760, 200, 16), (250, 350, 11), (836, 430, 9), (196, 250, 8), (700, 820, 12)]:
    star(cx, cy, r)
spark = spark.filter(ImageFilter.GaussianBlur(1.2 * SS))
canvas.alpha_composite(spark)

# 前景漂浮光点
dust = Image.new("RGBA", (W, W), (0, 0, 0, 0))
dd = ImageDraw.Draw(dust)
for cx, cy, r, a in [(430, 800, 5, 150), (600, 860, 3, 120), (300, 700, 4, 120), (740, 660, 3, 110), (180, 420, 3, 100)]:
    dd.ellipse(BOX(cx - r, cy - r, cx + r, cy + r), fill=(200, 245, 255, a))
canvas.alpha_composite(dust)

# 暗角
vig = Image.new("L", (W, W), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse(BOX(-120, -120, 1144, 1144), fill=90)
vig = vig.filter(ImageFilter.GaussianBlur(90 * SS))
dark = Image.new("RGBA", (W, W), (4, 12, 26, 255))
mask = vig.point(lambda v: int((90 - v) * 1.4) if v < 90 else 0)
canvas = Image.composite(dark, canvas, mask)

# 输出
out = canvas.convert("RGB").resize((S, S), Image.LANCZOS)
path = r"E:\Agent-bluefish\小鱼图库\小鱼表情包\小鱼写真-魅力版.png"
out.save(path, "PNG")
print("saved", path, out.size)

"""重做「毛先生」立绘：从宣传画原图抠出人物，出几种红黑色调变体给人挑。

源图：宣传画 2312×1254（06_art.png）
输出：透明 webp 变体 + 一张对照表
"""
import os, io
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageDraw

SRC = r"E:\Agent-bluefish\working\收纳\01-脚本\出图\背景制作\art\06_art.png"
OUT = r"E:\Agent-bluefish\working\收纳\03-截图\20261119-毛先生重做"
os.makedirs(OUT, exist_ok=True)

print("读原图…")
src = Image.open(SRC).convert("RGB")
W, H = src.size
print("  ", W, H)

# 先按人物所在位置裁一块（原尺寸），再抠 —— 小图抠出来边缘糊
crop_box = (int(W * 0.12), 0, int(W * 0.66), H)
work = src.crop(crop_box)
print("  裁出人物区:", work.size)

print("rembg 抠图…")
from rembg import remove, new_session
session = new_session('u2net')   # 本地已有 u2net.onnx，别让它去下默认的新模型
cut = remove(work, session=session, post_process_mask=True)
print("  抠完", cut.size, cut.mode)

alpha = cut.split()[-1]
bbox = alpha.getbbox()
print("  alpha bbox:", bbox)
if bbox is None:
    raise SystemExit("抠出来是空的")
person = cut.crop(bbox)
pw, ph = person.size
print("  人物", pw, ph, "比例", round(pw / ph, 3))

# 目标宽度 620（启动画面里显示 250px 宽，2.5x 足够清晰）
target_w = 760
target_h = int(ph * target_w / pw)
person = person.resize((target_w, target_h), Image.LANCZOS)
rgb = person.convert("RGB")
a = person.split()[-1]

L = ImageOps.grayscale(rgb)


def keep_alpha(img):
    out = img.convert("RGBA")
    out.putalpha(a)
    return out


variants = {}

# A 红黑双色调：暗部近黑、亮部骨白，整体压红
base = ImageOps.autocontrast(L, cutoff=1)
duo = ImageOps.colorize(base, black=(12, 0, 0), white=(240, 232, 218))
red_layer = Image.new("RGB", duo.size, (150, 18, 18))
variants["A-红黑双色调"] = keep_alpha(Image.blend(duo, red_layer, 0.18))

# B 版画三色：骨白 / 深红 / 近黑
arr = np.asarray(base, dtype=np.float32)
poster = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
poster[arr < 70] = (10, 2, 2)
poster[(arr >= 70) & (arr < 165)] = (128, 20, 20)
poster[arr >= 165] = (236, 227, 212)
variants["B-版画三色"] = keep_alpha(Image.fromarray(poster))

# C 暖红浮雕：原色降饱和 + 红通道抬升 + 轻浮雕
gray = ImageOps.grayscale(rgb)
warm = Image.merge("RGB", (
    gray.point(lambda v: min(255, int(v * 1.18))),
    gray.point(lambda v: int(v * 0.72)),
    gray.point(lambda v: int(v * 0.66)),
))
edge = gray.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(0.8))
emboss = ImageOps.invert(edge).point(lambda v: int(v * 0.35 + 165))
warm = Image.composite(warm, Image.blend(warm, emboss.convert("RGB"), 0.5), a)
variants["C-暖红浮雕"] = keep_alpha(warm)

# D 只用红与黑（最狠的一版）
bw = base.point(lambda v: 255 if v > 120 else 0)
variants["D-纯红黑"] = keep_alpha(ImageOps.colorize(bw, black=(6, 0, 0), white=(214, 32, 32)))

# 存 webp + 拼对照表
sheet_w = 0
items = []
for name, img in variants.items():
    p = os.path.join(OUT, f"{name}.webp")
    img.save(p, "WEBP", quality=88, method=6)
    kb = os.path.getsize(p) / 1024
    print(f"  {name}: {img.size} {kb:.0f}KB")
    items.append((name, img, kb))

thumb_h = 520
thumbs = []
for name, img, kb in items:
    t = img.copy()
    t.thumbnail((400, thumb_h), Image.LANCZOS)
    thumbs.append((name, t, kb))

cell_w = 420
cell_h = thumb_h + 60
sheet = Image.new("RGB", (cell_w * len(thumbs), cell_h), (18, 18, 20))
d = ImageDraw.Draw(sheet)
for i, (name, t, kb) in enumerate(thumbs):
    x = i * cell_w + (cell_w - t.size[0]) // 2
    y = 40 + (thumb_h - t.size[1]) // 2
    sheet.paste(t, (x, y), t)
    d.text((i * cell_w + 12, 10), f"{name}  {kb:.0f}KB", fill=(240, 240, 240))
sheet.save(os.path.join(OUT, "对照表.jpg"), "JPEG", quality=90)
print("对照表:", os.path.join(OUT, "对照表.jpg"))

"""把静态立绘做成「慢推镜」无缝循环视频（PIL 亚像素仿射 + numpy 叠加）。

用法: python ken.py <src.png> <out.mp4> [zoom_max] [seconds] [snow]
- 推镜：1.00 → zoom_max → 1.00（往返，所以首尾帧完全一致，循环无缝）
- snow：加飘雪层（1 = 开）
"""
import sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = sys.argv[1]
OUT = sys.argv[2]
ZMAX = float(sys.argv[3]) if len(sys.argv) > 3 else 1.07
SECONDS = float(sys.argv[4]) if len(sys.argv) > 4 else 40.0
SNOW = int(sys.argv[5]) if len(sys.argv) > 5 else 0

W, H = 1920, 1080
FPS = 30
N = int(SECONDS * FPS)

src = Image.open(SRC).convert("RGB")
SW, SH = src.size
print(f"src {SW}x{SH} -> {W}x{H}, {N} frames, zmax={ZMAX}, snow={SNOW}")

# 目标窗口的宽高比要跟输出一致
TARGET_AR = W / H
# 源图裁到 16:9（居中），避免仿射时把画面拉扁
if SW / SH > TARGET_AR:
    crop_w = SH * TARGET_AR
    base = src.crop((int((SW - crop_w) / 2), 0, int((SW + crop_w) / 2), SH))
else:
    crop_h = SW / TARGET_AR
    base = src.crop((0, int((SH - crop_h) / 2), SW, int((SH + crop_h) / 2)))
BW, BH = base.size
print(f"cropped base {BW}x{BH}")

# 暗角：先做一张 mask，逐帧乘
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
nx = (xx / W - 0.5) * 2
ny = (yy / H - 0.5) * 2
r = np.sqrt(nx ** 2 + ny ** 2) / math.sqrt(2)
vignette = np.clip(1.0 - 0.16 * np.clip((r - 0.45) / 0.55, 0, 1) ** 1.6, 0, 1)[..., None]

# 雪花：远近两层，近处的更大更亮走得更快（视差）
rng = np.random.default_rng(20261118)


def make_flakes(n, spd_lo, spd_hi, size_lo, size_hi, alpha_lo, alpha_hi):
    out = []
    for _ in range(n):
        out.append(dict(
            x=rng.uniform(-0.06, 1.06), y=rng.uniform(0, 1.2),
            spd=rng.uniform(spd_lo, spd_hi),
            sway=rng.uniform(0.004, 0.018),
            phase=rng.uniform(0, math.tau),
            size=int(rng.integers(size_lo, size_hi)),
            alpha=int(rng.uniform(alpha_lo, alpha_hi)),
        ))
    return out


FAR = make_flakes(300, 0.010, 0.024, 1, 3, 45, 120) if SNOW else []
NEAR = make_flakes(70, 0.030, 0.070, 2, 5, 90, 205) if SNOW else []


def draw_flakes(flakes, t, blur):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for f in flakes:
        y = (f["y"] + f["spd"] * t) % 1.2 - 0.1
        x = f["x"] + f["sway"] * math.sin(f["phase"] + t * 0.9)
        px, py = x * W, y * H
        r0 = f["size"]
        d.ellipse([px - r0, py - r0, px + r0, py + r0], fill=(255, 255, 255, f["alpha"]))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def snow_layer(t):
    if not SNOW:
        return None
    return Image.alpha_composite(draw_flakes(FAR, t, 0.6), draw_flakes(NEAR, t, 1.9))


proc = subprocess.Popen(
    ["ffmpeg", "-y", "-v", "error",
     "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
     "-profile:v", "high", "-movflags", "+faststart", "-an", OUT],
    stdin=subprocess.PIPE)

for i in range(N):
    # 三角波：0 → 1 → 0，保证首尾一致
    p = i / (N - 1)
    tri = 1 - abs(2 * p - 1)
    z = 1.0 + (ZMAX - 1.0) * tri
    # 轻微横移：跟随主体（左偏），慢慢从左往右再回来
    panx = (0.010 * math.sin(math.tau * p * 0.5)) * BW
    winw = BW / z
    winh = winw / TARGET_AR
    cx = BW / 2 + panx
    cy = BH / 2
    a = winw / W
    e = winh / H
    c = cx - winw / 2
    f = cy - winh / 2
    frame = base.transform((W, H), Image.AFFINE, (a, 0, c, 0, e, f), Image.BICUBIC)
    arr = np.asarray(frame, dtype=np.float32) * vignette
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    if SNOW:
        img = Image.alpha_composite(img.convert("RGBA"), snow_layer(i / FPS)).convert("RGB")
    proc.stdin.write(img.tobytes())
    if i % 300 == 0:
        print(f"  {i}/{N}", flush=True)

proc.stdin.close()
proc.wait()
print("exit", proc.returncode, "->", OUT)

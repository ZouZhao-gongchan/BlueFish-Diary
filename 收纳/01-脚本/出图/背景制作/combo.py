"""把 06（毛泽东宣传画）和 30（雄关漫道）拼成一条无缝循环的背景片。

思路：
  out = 06[3s..37s] → 溶解(06 尾 3s ↔ 30 头 3s) → 30[3s..37s] → 溶解(30 尾 3s ↔ 06 头 3s) → 回到开头
  最后那段溶解正好收敛到 06(3s)，也就是输出的第一帧，所以接缝落在溶解收敛处，看不出来。

溶解不是线性的：alpha 用 smootherstep，中点压 20% 亮度、再加一记解焦模糊（sigma 峰值 ~6），
这样两张风格差很远的画不会在中点叠成一张脏图。

用法: python combo.py
"""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

TEST = len(sys.argv) > 1 and sys.argv[1] == "test"

W, H = 1920, 1080
FPS = 30
CLIP_FRAMES = 120 if TEST else 1980      # 每段 66s = 60s 净停留 + 两侧各 3s 过渡
TRANS_FRAMES = 30 if TEST else 90       # 溶解 3s
TARGET_AR = W / H

ART06 = r"C:\Users\FIshKiller\AppData\Local\Temp\bgcheck\wp3\art\06_art.png"
ART30 = r"C:\Users\FIshKiller\AppData\Local\Temp\bgcheck\wp3\art\30_art.png"
OUT = (r"C:\Users\FIshKiller\AppData\Local\Temp\bgcheck\wp3\test_combo.mp4" if TEST
       else r"C:\Users\FIshKiller\AppData\Local\Temp\bgcheck\wp3\bg-changzheng.mp4")


# ---------- 暗角（8 位，用 ImageChops 乘，比 float 快很多） ----------
def make_vignette(strength=0.16):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx / W - 0.5) * 2
    ny = (yy / H - 0.5) * 2
    r = np.sqrt(nx ** 2 + ny ** 2) / math.sqrt(2)
    v = np.clip(1.0 - strength * np.clip((r - 0.45) / 0.55, 0, 1) ** 1.6, 0, 1)
    a = (v * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([a, a, a]), "RGB")


VIG = make_vignette()


# ---------- 雪花 ----------
def make_flakes(n, spd_lo, spd_hi, size_lo, size_hi, alpha_lo, alpha_hi, seed):
    rng = np.random.default_rng(seed)
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


FAR = make_flakes(300, 0.010, 0.024, 1, 3, 45, 120, 20261118)
NEAR = make_flakes(70, 0.030, 0.070, 2, 5, 90, 205, 20261119)


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
    return Image.alpha_composite(draw_flakes(FAR, t, 0.6), draw_flakes(NEAR, t, 1.9))


# ---------- 一段素材 ----------
class Clip:
    def __init__(self, path, zmax, pan_amp, snow, name):
        self.name = name
        src = Image.open(path).convert("RGB")
        sw, sh = src.size
        if sw / sh > TARGET_AR:
            cw = sh * TARGET_AR
            base = src.crop((int((sw - cw) / 2), 0, int((sw + cw) / 2), sh))
        else:
            ch = sw / TARGET_AR
            base = src.crop((0, int((sh - ch) / 2), sw, int((sh + ch) / 2)))
        self.base = base
        self.BW, self.BH = base.size
        self.zmax = zmax
        self.pan_amp = pan_amp
        self.snow = snow

    def frame(self, i):
        p = i / (CLIP_FRAMES - 1)
        tri = 1 - abs(2 * p - 1)            # 0 → 1 → 0，首尾同帧
        z = 1.0 + (self.zmax - 1.0) * tri
        panx = self.pan_amp * math.sin(math.tau * p * 0.5) * self.BW
        winw = self.BW / z
        winh = winw / TARGET_AR
        cx = self.BW / 2 + panx
        cy = self.BH / 2
        a = winw / W
        e = winh / H
        c = cx - winw / 2
        f = cy - winh / 2
        img = self.base.transform((W, H), Image.AFFINE, (a, 0, c, 0, e, f), Image.BICUBIC)
        img = ImageChops.multiply(img, VIG)
        if self.snow:
            img = Image.alpha_composite(img.convert("RGBA"), snow_layer(i / FPS)).convert("RGB")
        return img


print("载入素材…")
C06 = Clip(ART06, 1.08, 0.010, False, "06")
C30 = Clip(ART30, 1.07, 0.010, True, "30")
print(f"  06 base {C06.BW}x{C06.BH}   30 base {C30.BW}x{C30.BH}")


def blend(a, b, p):
    """p: 0 → 1。smootherstep + 中点压亮度 + 解焦。

    压亮度是这条过渡的关键：两张画风格差太远（暖黄宣传画 vs 冷灰水墨），
    纯淡入淡出在中点会变成「毛先生身上贴着满屏草书」的重影。把中点压到一半亮度，
    重影就被埋进暗部，读起来像一次「换场」而不是两张图叠在一起。
    """
    s = p * p * p * (p * (p * 6 - 15) + 10)
    cut = int(s * 255)
    mixed = Image.composite(b, a, Image.new("L", (W, H), cut))
    dip = 1.0 - 0.78 * math.sin(math.pi * p) ** 1.30
    mixed = ImageChops.multiply(mixed, Image.new("RGB", (W, H), (int(dip * 255),) * 3))
    sigma = 7.5 * math.sin(math.pi * p) ** 1.1
    if sigma > 0.25:
        mixed = mixed.filter(ImageFilter.GaussianBlur(sigma))
    return mixed


# ---------- 时间线 ----------
SEQ = []
for i in range(TRANS_FRAMES, CLIP_FRAMES - TRANS_FRAMES):     # 06 主体
    SEQ.append(("06", i))
for k in range(TRANS_FRAMES):                                 # 06 → 30
    SEQ.append(("T1", k))
for i in range(TRANS_FRAMES, CLIP_FRAMES - TRANS_FRAMES):     # 30 主体
    SEQ.append(("30", i))
for k in range(TRANS_FRAMES):                                 # 30 → 06（收敛到 06 开头，接缝藏这里）
    SEQ.append(("T2", k))

N = len(SEQ)
print(f"总帧数 {N}  ({N / FPS:.1f}s)")

proc = subprocess.Popen(
    ["ffmpeg", "-y", "-v", "error",
     "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
     "-profile:v", "high", "-movflags", "+faststart", "-an", OUT],
    stdin=subprocess.PIPE)

for n, (kind, k) in enumerate(SEQ):
    if kind == "06":
        img = C06.frame(k)
    elif kind == "30":
        img = C30.frame(k)
    elif kind == "T1":
        p = k / (TRANS_FRAMES - 1)
        img = blend(C06.frame(CLIP_FRAMES - TRANS_FRAMES + k), C30.frame(k), p)
    else:
        p = k / (TRANS_FRAMES - 1)
        img = blend(C30.frame(CLIP_FRAMES - TRANS_FRAMES + k), C06.frame(k), p)
    proc.stdin.write(img.tobytes())
    if n % 200 == 0:
        print(f"  {n}/{N}", flush=True)

proc.stdin.close()
proc.wait()
print("exit", proc.returncode, "->", OUT)

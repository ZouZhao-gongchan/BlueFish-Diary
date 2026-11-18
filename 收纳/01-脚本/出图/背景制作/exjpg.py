import glob, os, sys

OUT = r"C:\Users\FIshKiller\AppData\Local\Temp\bgcheck\wp3\texjpgs"
os.makedirs(OUT, exist_ok=True)

SRC = r"C:\Users\FIshKiller\AppData\Local\Temp\bgcheck\wp3\unpacked"

for p in glob.glob(os.path.join(SRC, "*", "*.tex")):
    key = os.path.basename(os.path.dirname(p))
    d = open(p, "rb").read()
    # 找所有 JPEG 段：SOI ... EOI
    segs = []
    i = 0
    while True:
        s = d.find(b"\xff\xd8\xff", i)
        if s < 0:
            break
        e = d.find(b"\xff\xd9", s + 3)
        if e < 0:
            break
        segs.append((s, e + 2))
        i = e + 2
    if not segs:
        print(f"{key} {os.path.basename(p)[:30]}: no jpeg, {len(d)} bytes")
        continue
    sizes = [e - s for s, e in segs]
    print(f"{key} {os.path.basename(p)[:30]}: {len(segs)} jpeg(s), file={len(d)}, sizes {sizes[:6]}{'...' if len(sizes) > 6 else ''}")
    for n, (s, e) in enumerate(segs[:3]):
        dst = os.path.join(OUT, f"{key}_{n:03d}.jpg")
        open(dst, "wb").write(d[s:e])
    if len(segs) > 3:
        dst = os.path.join(OUT, f"{key}_last.jpg")
        s, e = segs[-1]
        open(dst, "wb").write(d[s:e])

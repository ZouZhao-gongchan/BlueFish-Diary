import glob, os, struct, io
from PIL import Image

SRC = r"C:\Users\FIshKiller\AppData\Local\Temp\bgcheck\wp3\unpacked"
OUT = r"C:\Users\FIshKiller\AppData\Local\Temp\bgcheck\wp3\art"
os.makedirs(OUT, exist_ok=True)


def candidates(d):
    out = []
    i = 0
    while True:
        s = d.find(b"\xff\xd8\xff", i)
        if s < 0:
            break
        i = s + 3
        if s < 4:
            continue
        size = struct.unpack_from('<I', d, s - 4)[0]
        if not (100 < size <= len(d) - s + 64):
            continue
        window = d[s:s + size + 64]
        e = window.rfind(b"\xff\xd9")
        if e < 0:
            continue
        blob = window[:e + 2]
        try:
            im = Image.open(io.BytesIO(blob))
            im.load()
        except Exception:
            continue
        out.append((im.size[0] * im.size[1], s, len(blob), im.size, blob))
    return out


for p in glob.glob(os.path.join(SRC, "*", "*.tex")):
    key = os.path.basename(os.path.dirname(p))
    d = open(p, "rb").read()
    cands = candidates(d)
    if not cands:
        continue
    cands.sort(key=lambda t: -t[0])
    for pxs, s, ln, dim, _ in cands:
        print(f"{key}: {dim[0]}x{dim[1]}  {ln} bytes @ {s}")
    pxs, s, ln, dim, blob = cands[0]
    dst = os.path.join(OUT, f"{key}_art.png")
    Image.open(io.BytesIO(blob)).save(dst)
    print(f"   -> best {dim} saved as {os.path.basename(dst)}")

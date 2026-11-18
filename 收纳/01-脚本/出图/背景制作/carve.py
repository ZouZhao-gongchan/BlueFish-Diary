import glob, os, struct

SRC = r"C:\Users\FIshKiller\AppData\Local\Temp\bgcheck\wp3\unpacked"
OUT = r"C:\Users\FIshKiller\AppData\Local\Temp\bgcheck\wp3\media"
os.makedirs(OUT, exist_ok=True)


def carve_mp4(d, start):
    """从 start 开始按 mp4 box 结构走，返回有效长度。"""
    pos = start
    n = len(d)
    while pos + 8 <= n:
        size = struct.unpack_from('>I', d, pos)[0]
        typ = d[pos + 4:pos + 8]
        if size == 1:  # 64-bit size
            if pos + 16 > n:
                break
            size = struct.unpack_from('>Q', d, pos + 8)[0]
        if size == 0:  # box 到文件尾
            return n - start
        if size < 8 or pos + size > n:
            break
        pos += size
    return pos - start


for p in glob.glob(os.path.join(SRC, "*", "*.tex")):
    key = os.path.basename(os.path.dirname(p))
    d = open(p, "rb").read()
    i = d.find(b'ftyp')
    if i < 0:
        continue
    start = i - 4
    size = carve_mp4(d, start)
    blob = d[start:start + size]
    dst = os.path.join(OUT, f"{key}.mp4")
    open(dst, "wb").write(blob)
    print(f"{key}: tex={len(d)} mp4@ {start} size={size} -> {dst}")

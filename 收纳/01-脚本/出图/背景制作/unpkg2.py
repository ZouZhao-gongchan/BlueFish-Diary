import struct, os, json

targets = {
    "06": r"E:\SteamLibrary\steamapps\workshop\content\431960\2316528446\scene.pkg",
    "30": r"E:\SteamLibrary\steamapps\workshop\content\431960\3346760756\scene.pkg",
    "45": r"E:\SteamLibrary\steamapps\workshop\content\431960\3785101203\scene.pkg",
}
OUT = r"C:\Users\FIshKiller\AppData\Local\Temp\bgcheck\wp3\unpacked"


def guess(b):
    if b[:4] == b'RIFF': return 'riff'
    if b[:8] == b'\x89PNG\r\n\x1a\n': return 'png'
    if b[:2] == b'\xff\xd8': return 'jpg'
    if b[:3] == b'GIF': return 'gif'
    if b[4:8] == b'ftyp': return 'mp4'
    if b[:4] == b'TEXV': return 'tex'
    if b[:1] in (b'{', b'['): return 'json'
    return '?'


def parse(path):
    data = open(path, 'rb').read()
    magic_len = struct.unpack_from('<i', data, 0)[0]
    magic = data[4:4 + magic_len].decode('latin-1')
    ver = int(magic[4:])
    pos = 4 + magic_len
    count = struct.unpack_from('<i', data, pos)[0]; pos += 4
    entries = []
    for _ in range(count):
        ln = struct.unpack_from('<i', data, pos)[0]; pos += 4
        name = data[pos:pos + ln].decode('utf-8', 'replace'); pos += ln
        offset = struct.unpack_from('<i', data, pos)[0]; pos += 4
        length = struct.unpack_from('<i', data, pos)[0]; pos += 4
        entries.append((name, offset, length))
    return magic, ver, entries, data, pos


for key, path in targets.items():
    print("=" * 60)
    print(key, f"{os.path.getsize(path)/1048576:.2f} MB")
    magic, ver, entries, data, table_end = parse(path)
    print("magic", magic, "count", len(entries), "table_end", table_end)
    # 校验：每个 entry 的魔数
    bad = 0
    for name, offset, length in entries:
        o = table_end + offset
        m = guess(data[o:o + 8])
        if m == '?':
            bad += 1
    print("unknown-magic entries:", bad, "/", len(entries))
    dst = os.path.join(OUT, key)
    os.makedirs(dst, exist_ok=True)
    for name, offset, length in entries:
        o = table_end + offset
        blob = data[o:o + length]
        m = guess(blob[:8])
        print(f"  {m:5s} {length:>9d}  {name}")
        safe = name.replace('/', '__').replace('\\', '__')
        if m in ('png', 'jpg', 'mp4', 'riff', 'gif', 'tex'):
            open(os.path.join(dst, safe), 'wb').write(blob)
        elif m == 'json':
            open(os.path.join(dst, safe + '.txt'), 'wb').write(blob)

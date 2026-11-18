import re, os, sys, struct

targets = {
    "06_mao": r"E:\SteamLibrary\steamapps\workshop\content\431960\2316528446\scene.pkg",
    "30_xiongguan": r"E:\SteamLibrary\steamapps\workshop\content\431960\3346760756\scene.pkg",
    "45_chuangkou": r"E:\SteamLibrary\steamapps\workshop\content\431960\3785101203\scene.pkg",
}

for key, p in targets.items():
    if not os.path.isfile(p):
        print(f"{key}: 文件不存在 {p}")
        continue
    size = os.path.getsize(p)
    with open(p, "rb") as f:
        head = f.read(16)
        f.seek(0)
        raw = f.read()
    # 找文件扩展名
    exts = {}
    for m in re.finditer(rb"\.(mp4|webm|mov|m4v|png|jpg|jpeg|gif|tex|json|scene)\b", raw, re.I):
        e = m.group(1).lower().decode()
        exts[e] = exts.get(e, 0) + 1
    print(f"== {key}  {size/1024/1024:.2f} MB  头部={head[:8]!r}")
    print("   扩展名出现次数:", exts)
    # 抓几个看起来像路径的字符串
    names = set()
    for m in re.finditer(rb"[A-Za-z0-9_\-/\\\. ]{4,80}\.(?:mp4|webm|png|jpg|tex)", raw, re.I):
        s = m.group(0).decode("latin-1", "ignore")
        if len(names) < 8:
            names.add(s)
    for n in list(names)[:8]:
        print("   ", n)

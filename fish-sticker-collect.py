# -*- coding: utf-8 -*-
"""小鱼收表情包：把阿冉在 QQ 私聊里发的图片拉下来，存进收藏夹。

用法：
  python fish-sticker-collect.py          # 拉最近 20 条，收新图
  python fish-sticker-collect.py 50       # 拉最近 50 条
"""
import hashlib
import json
import os
import sys
import urllib.request

ONEBOT = "http://127.0.0.1:3000"
QQ = 3587074357
DEST = r"E:\Agent-bluefish\working\小鱼表情包"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "Chrome/120 Safari/537.36")


def post(path, body):
    req = urllib.request.Request(
        ONEBOT + path,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    os.makedirs(DEST, exist_ok=True)
    data = post("/get_friend_msg_history", {"user_id": QQ, "count": count})
    msgs = (data.get("data") or {}).get("messages") or []
    saved = 0
    for m in msgs:
        for seg in m.get("message") or []:
            if seg.get("type") != "image":
                continue
            url = (seg.get("data") or {}).get("url") or ""
            if not url:
                continue
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                blob = urllib.request.urlopen(req, timeout=30).read()
            except Exception as e:
                print(f"下载失败: {e}")
                continue
            digest = hashlib.md5(blob).hexdigest()[:10]
            name = f"sticker-{digest}.jpg"
            path = os.path.join(DEST, name)
            if os.path.exists(path):
                continue
            with open(path, "wb") as f:
                f.write(blob)
            saved += 1
            print(f"收下 {name}  ({len(blob)//1024}KB)")
    print(f"这次新收 {saved} 张，收藏夹共 {len(os.listdir(DEST))} 个文件")


if __name__ == "__main__":
    main()

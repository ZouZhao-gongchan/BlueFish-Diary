# -*- coding: utf-8 -*-
"""小鱼刷 B 站：抓热门榜，可按分区筛选，打印候选清单。

用法：
  python fish-bilibili.py popular 12
  python fish-bilibili.py digital 8   # 从热门里筛数码/科技类
"""
import json
import sys
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "Chrome/120 Safari/537.36")
HEADERS = {"User-Agent": UA, "Referer": "https://www.bilibili.com"}

POPULAR = "https://api.bilibili.com/x/web-interface/popular?ps={n}&pn=1"

TECH_ZONES = {"数码", "科技", "科学科普", "计算机技术", "手机平板", "机械",
              "人工智能", "科工机械", "科技数码"}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("code") != 0:
        return []
    return (data.get("data") or {}).get("list") or []


def fmt_play(n):
    n = int(n or 0)
    return f"{n/10000:.1f}w" if n >= 10000 else str(n)


def main():
    zone = sys.argv[1] if len(sys.argv) > 1 else "popular"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    pool = fetch(POPULAR.format(n=50))
    if zone in ("digital", "tech"):
        pool = [it for it in pool if it.get("tname") in TECH_ZONES]
    items = pool[:count]
    for it in items:
        dur = int(it.get("duration") or 0)
        print(f"[{it.get('tname','')}] {it.get('title','')}")
        print(f"  UP: {it.get('owner',{}).get('name','')} | 播放 {fmt_play(it.get('stat',{}).get('view'))} "
              f"| {dur//60}:{dur%60:02d}")
        print(f"  https://www.bilibili.com/video/{it.get('bvid','')}")
    if not items:
        print("（没抓到内容）")


if __name__ == "__main__":
    main()

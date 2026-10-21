"""从 fisharchive（同人表情墙）按标签挑表情，下载到小鱼的贴纸池。

用法：
    python fisharchive-fetch.py --max 12 --tags 卖萌,开心,比心
    python fisharchive-fetch.py --max 5 --dry-run

说明：
- 站点 robots.txt 明确允许收录 media/ 与 large/；这里只取它公开的 index.json；
- 只下原图（png/jpg 优先），过大或非这两类时退回 480px 的 large.webp；
- 去重、记来源与许可，图只作个人表情包用。
"""

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

INDEX_URL = "https://fisharchive.cc/stickers/index.json"
DEFAULT_OUT = Path(r"E:\Agent-bluefish\大肥鱼可爱图片")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FishStickerBot/0.1 (personal use)"
MAX_BYTES = 4 * 1024 * 1024

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def fetch(url: str, limit: int = MAX_BYTES) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        content_type = response.headers.get("Content-Type", "")
        payload = response.read(limit + 1)
    if len(payload) > limit:
        raise ValueError(f"超过 {limit // 1024} KB")
    return payload, content_type


def ext_of(url: str, content_type: str) -> str:
    suffix = Path(url.split("?")[0]).suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return suffix
    mapping = {"image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif", "image/webp": ".webp"}
    return mapping.get(content_type.split(";")[0].strip(), ".img")


def existing_hashes(out: Path) -> set[str]:
    found = set()
    for file in out.iterdir():
        if file.is_file() and file.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            found.add(hashlib.sha1(file.read_bytes()).hexdigest())
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=12)
    parser.add_argument("--tags", default="卖萌,开心,比心,打招呼", help="逗号分隔的标签")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--prefix", default="fa")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    raw, _ = fetch(INDEX_URL)
    index = json.loads(raw.decode("utf-8"))
    print(f"站点：{index.get('name')}｜共 {index.get('count')} 张｜许可：{index.get('license')}")

    stickers = index.get("stickers") or []
    wanted = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    pool = [item for item in stickers if any(tag in (item.get("tags") or []) for tag in wanted)]
    if not pool:
        print("没有匹配标签，退回全部。")
        pool = stickers

    hashes = existing_hashes(out)
    attribution_file = out / "crawl-attribution.json"
    attribution = []
    if attribution_file.exists():
        try:
            attribution = json.loads(attribution_file.read_text(encoding="utf-8"))
        except Exception:
            attribution = []

    saved = 0
    for item in pool:
        if saved >= args.max:
            break
        original = item.get("original") or ""
        large = item.get("large") or ""
        url = original if Path(original.split("?")[0]).suffix.lower() in {".png", ".jpg", ".jpeg"} else (large or original)
        if not url:
            continue
        try:
            payload, content_type = fetch(url)
        except Exception as error:
            print(f"  跳过（下载失败）：{url} -> {error}")
            continue
        if len(payload) < 6 * 1024:
            print(f"  跳过（太小）：{url}")
            continue
        digest = hashlib.sha1(payload).hexdigest()
        if digest in hashes:
            print(f"  跳过（已有）：{item.get('alt', '')[:20]}")
            continue
        suffix = ext_of(url, content_type)
        if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            print(f"  跳过（格式 {content_type}）：{url}")
            continue
        target = out / f"{args.prefix}-{digest[:8]}{suffix}"
        alt = (item.get("alt") or "").strip()
        print(f"  {'[dry-run] ' if args.dry_run else ''}{target.name}｜{alt[:34]}｜{len(payload) // 1024}KB")
        if not args.dry_run:
            target.write_bytes(payload)
            hashes.add(digest)
            attribution.append({
                "file": target.name,
                "alt": alt,
                "tags": item.get("tags") or [],
                "source_page": "https://fisharchive.cc/#wall",
                "source_url": url,
                "license": index.get("license"),
                "fetched_at": datetime.now().isoformat(timespec="seconds"),
            })
        saved += 1

    if not args.dry_run and saved:
        attribution_file.write_text(json.dumps(attribution, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"完成：{saved} 张 -> {out}")
    elif not saved:
        print("没有新图。")


if __name__ == "__main__":
    main()

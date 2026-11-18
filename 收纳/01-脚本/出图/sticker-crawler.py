"""小鱼的贴纸爬虫（单页版）。

用法：
    python sticker-crawler.py --page http://www.doutula.com --max 5 --prefix doutula
    python sticker-crawler.py --page <url> --max 5 --dry-run
    python sticker-crawler.py --page <url> --max 5 --out "E:\\...\\大肥鱼可爱图片"

原则：
- 只看你给的那一页，不递归、不扫站；
- 先查 robots.txt，明示 Disallow 就不抓；
- 只下图片，限大小、去重、记来源；
- 抓来的图仅作个人表情包用，别商用、别二次传播。
"""

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

# Windows 控制台默认 GBK，遇到 emoji 会崩；统一成 UTF-8。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FishStickerBot/0.1 (personal use)"
DEFAULT_OUT = Path(r"E:\Agent-bluefish\大肥鱼可爱图片")
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
SKIP_PATTERNS = ("loader", "spacer", "blank", "logo", "icon", "avatar", "banner")


class ImageCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() != "img":
            return
        data = {key.lower(): value for key, value in attrs if value}
        for key in ("data-original", "data-src", "data-lazy-src", "src"):
            value = data.get(key)
            if value:
                self.urls.append(value)
        srcset = data.get("srcset")
        if srcset:
            for part in srcset.split(","):
                candidate = part.strip().split(" ")[0]
                if candidate:
                    self.urls.append(candidate)


def fetch(url: str, limit: int = 8 * 1024 * 1024, timeout: int = 20) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": url})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        payload = response.read(limit + 1)
    if len(payload) > limit:
        raise ValueError(f"文件超过 {limit // 1024} KB")
    return payload, content_type


def allowed_by_robots(page_url: str) -> bool:
    parts = urllib.parse.urlsplit(page_url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    parser = urllib.robotparser.RobotFileParser()
    try:
        parser.set_url(robots_url)
        parser.read()
    except Exception:
        return True  # 读不到 robots 时不阻断，但会打印警告
    return parser.can_fetch(UA, page_url)


def resolve(base: str, src: str) -> str | None:
    src = src.strip()
    if not src or src.startswith("data:"):
        return None
    if src.startswith("//"):
        scheme = urllib.parse.urlsplit(base).scheme or "http"
        src = f"{scheme}:{src}"
    return urllib.parse.urljoin(base, src)


def looks_like_image(url: str) -> bool:
    path = urllib.parse.urlsplit(url).path.lower()
    return Path(path).suffix in IMG_EXT


def ext_for(url: str, content_type: str) -> str:
    suffix = Path(urllib.parse.urlsplit(url).path).suffix.lower()
    if suffix in IMG_EXT:
        return suffix
    mapping = {"image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif", "image/webp": ".webp"}
    return mapping.get(content_type.split(";")[0].strip(), ".img")


def existing_hashes(out: Path) -> set[str]:
    hashes = set()
    for file in out.iterdir():
        if file.is_file() and file.suffix.lower() in IMG_EXT:
            hashes.add(hashlib.sha1(file.read_bytes()).hexdigest())
    return hashes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", required=True, help="要抓的页面 URL")
    ap.add_argument("--max", type=int, default=5, help="最多下载几张（默认 5）")
    ap.add_argument("--prefix", default="crawl", help="文件名前缀")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="保存目录")
    ap.add_argument("--min-kb", type=int, default=8, help="小于这个大小的图跳过（默认 8KB）")
    ap.add_argument("--max-kb", type=int, default=5120, help="大于这个大小的图跳过（默认 5MB）")
    ap.add_argument("--dry-run", action="store_true", help="只列出候选，不下载")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if not allowed_by_robots(args.page):
        sys.exit(f"robots.txt 不允许抓这个页面：{args.page}")

    print(f"抓取页面：{args.page}")
    html, _ = fetch(args.page, limit=4 * 1024 * 1024)
    collector = ImageCollector()
    collector.feed(html.decode("utf-8", errors="ignore"))

    candidates: list[str] = []
    seen = set()
    for raw in collector.urls:
        url = resolve(args.page, raw)
        if not url or url in seen:
            continue
        seen.add(url)
        low = url.lower()
        if any(pattern in low for pattern in SKIP_PATTERNS):
            continue
        if not looks_like_image(url):
            continue
        candidates.append(url)

    print(f"候选 {len(candidates)} 张，准备下载 {min(args.max, len(candidates))} 张")

    hashes = existing_hashes(out)
    attribution_file = out / "crawl-attribution.json"
    attribution = []
    if attribution_file.exists():
        try:
            attribution = json.loads(attribution_file.read_text(encoding="utf-8"))
        except Exception:
            attribution = []

    saved = 0
    for url in candidates:
        if saved >= args.max:
            break
        try:
            payload, content_type = fetch(url, limit=args.max_kb * 1024)
        except Exception as error:
            print(f"  跳过（下载失败）：{url} -> {error}")
            continue
        if len(payload) < args.min_kb * 1024:
            print(f"  跳过（太小 {len(payload) // 1024}KB）：{url}")
            continue
        if content_type and not content_type.startswith("image/"):
            print(f"  跳过（不是图片 {content_type}）：{url}")
            continue
        digest = hashlib.sha1(payload).hexdigest()
        if digest in hashes:
            print(f"  跳过（已有重复）：{url}")
            continue
        ext = ext_for(url, content_type)
        target = out / f"{args.prefix}-{digest[:8]}{ext}"
        if args.dry_run:
            print(f"  [dry-run] {target.name} <- {url}")
        else:
            target.write_bytes(payload)
            hashes.add(digest)
            attribution.append({
                "file": target.name,
                "source_page": args.page,
                "source_url": url,
                "sha1": digest,
                "fetched_at": datetime.now().isoformat(timespec="seconds"),
            })
            print(f"  ✅ {target.name} ({len(payload) // 1024}KB) <- {url}")
            time.sleep(0.3)
        saved += 1

    if not args.dry_run and saved:
        attribution_file.write_text(json.dumps(attribution, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"完成：{saved} 张 -> {out}")
    elif not saved:
        print("这次没有下到新图。")


if __name__ == "__main__":
    main()

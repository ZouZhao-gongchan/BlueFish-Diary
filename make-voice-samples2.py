import asyncio
from pathlib import Path

import edge_tts

OUT = Path(r"E:\Agent-bluefish\working\voice-samples")
OUT.mkdir(parents=True, exist_ok=True)

A = "阿冉，我是小鱼呀。今天也想你了，你在忙什么呢？"
B = "阿冉……我是小鱼呀。今天，也在想你呢。你那边，忙不忙呀？"

JOBS = [
    ("04-xiaoyi-slower", "zh-CN-XiaoyiNeural", A, "-8%", "+8Hz"),
    ("05-xiaoyi-casual", "zh-CN-XiaoyiNeural", B, "-10%", "+10Hz"),
    ("06-xiaoyi-soft", "zh-CN-XiaoyiNeural", B, "-15%", "+12Hz"),
]


async def main():
    for name, voice, text, rate, pitch in JOBS:
        path = OUT / f"{name}.mp3"
        await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(str(path))
        print(f"saved {path} ({path.stat().st_size} bytes)")


asyncio.run(main())

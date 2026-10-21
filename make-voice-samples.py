import asyncio
from pathlib import Path

import edge_tts

OUT = Path(r"E:\Agent-bluefish\working\voice-samples")
OUT.mkdir(parents=True, exist_ok=True)

TEXT = "阿冉，我是小鱼呀。今天也想你了，你在忙什么呢？"

JOBS = [
    ("01-晓伊-软萌", "zh-CN-XiaoyiNeural", "+0%", "+0Hz"),
    ("02-晓伊-再甜一点", "zh-CN-XiaoyiNeural", "+5%", "+18Hz"),
    ("03-晓晓-温柔", "zh-CN-XiaoxiaoNeural", "+0%", "+0Hz"),
]


async def main():
    for name, voice, rate, pitch in JOBS:
        path = OUT / f"{name}.mp3"
        communicate = edge_tts.Communicate(TEXT, voice, rate=rate, pitch=pitch)
        await communicate.save(str(path))
        print(f"saved {path} ({path.stat().st_size} bytes)")


asyncio.run(main())

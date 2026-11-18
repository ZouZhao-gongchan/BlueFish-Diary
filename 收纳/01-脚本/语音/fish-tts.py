"""小鱼的声音：用 edge-tts 合成一句中文语音。

用法：
    python fish-tts.py "要说的话" "输出.mp3" [voice] [rate] [pitch]

默认就是阿冉选定的 04：晓伊 + 慢 8% + 高 8Hz。
"""

import asyncio
import sys

import edge_tts


async def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit('usage: fish-tts.py "text" "out.mp3" [voice] [rate] [pitch]')

    text = sys.argv[1]
    out = sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) > 3 else "zh-CN-XiaoyiNeural"
    rate = sys.argv[4] if len(sys.argv) > 4 else "-8%"
    pitch = sys.argv[5] if len(sys.argv) > 5 else "+8Hz"

    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(out)


asyncio.run(main())

"""生成 B 站扫码登录二维码，登录成功后把 SESSDATA 写进本地凭据文件。

只写本地文件，不打印、不提交、不进对话。
轮询对网络抖动做重试；二维码约 170 秒后过期。
"""

import asyncio
import json
import shutil
import tempfile
import time
from pathlib import Path

from bilibili_api import login_v2
from bilibili_api.login_v2 import QrCodeLoginEvents

QR = Path(r"E:\Agent-bluefish\working\bili-qr.png")
CRED = Path(r"E:\Agent-bluefish\bili-credential.json")


async def main() -> None:
    qr = login_v2.QrCodeLogin()
    await qr.generate_qrcode()

    temp_qr = Path(tempfile.gettempdir()) / "qrcode.png"
    shutil.copy(temp_qr, QR)
    print(f"QR_SAVED {QR}", flush=True)

    deadline = time.time() + 170
    while time.time() < deadline:
        try:
            state = await qr.check_state()
        except Exception as error:  # 网络抖动/超时：别死，继续等
            print(f"RETRY {type(error).__name__}", flush=True)
            await asyncio.sleep(3)
            continue

        print(f"STATE {state}", flush=True)
        if state == QrCodeLoginEvents.DONE:
            credential = qr.get_credential()
            data = {
                "sessdata": credential.sessdata,
                "bili_jct": credential.bili_jct,
                "buvid3": credential.buvid3,
                "dedeuserid": credential.dedeuserid,
            }
            CRED.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"CRED_SAVED {CRED}", flush=True)
            return
        if state == QrCodeLoginEvents.TIMEOUT:
            print("TIMEOUT", flush=True)
            return
        await asyncio.sleep(2)

    print("EXPIRED", flush=True)


asyncio.run(main())

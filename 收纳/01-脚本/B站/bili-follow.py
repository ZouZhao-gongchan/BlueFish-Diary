"""关注阿冉的 B 站账号，并打印昵称（用于评论里的 @）。"""

import asyncio
import json
from pathlib import Path

import requests
from bilibili_api import Credential, user

CRED = Path(r"E:\Agent-bluefish\bili-credential.json")
TARGET_UID = 552164191
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def get_buvid3() -> str:
    try:
        response = requests.get(
            "https://api.bilibili.com/x/frontend/finger/spi",
            headers={"User-Agent": UA, "Referer": "https://www.bilibili.com/"},
            timeout=20,
        ).json()
        if response.get("code") == 0:
            return str(response["data"]["b_3"])
    except Exception as error:
        print(f"buvid3 获取失败：{type(error).__name__}")
    return ""


async def main() -> None:
    data = json.loads(CRED.read_text(encoding="utf-8"))
    if not data.get("buvid3"):
        data["buvid3"] = get_buvid3()
        CRED.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    credential = Credential(
        sessdata=data.get("sessdata", ""),
        bili_jct=data.get("bili_jct", ""),
        buvid3=data.get("buvid3", ""),
        dedeuserid=data.get("dedeuserid", ""),
    )
    target = user.User(TARGET_UID, credential=credential)

    info = await target.get_user_info()
    print("nickname=" + str(info.get("name", "")))
    print("uid=" + str(info.get("mid", "")))

    result = await target.modify_relation(user.RelationType.SUBSCRIBE)
    print("code=" + str(result.get("code")))
    print("message=" + str(result.get("message", "")))


asyncio.run(main())

"""B 站扫码登录（自抓 Cookie 版）。

生成二维码 → 轮询 → 成功后从 session.cookies 与返回 URL 里取 SESSDATA。
只写本地凭据文件，不打印令牌值。
"""

import json
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import qrcode
import requests

QR = Path(r"E:\Agent-bluefish\working\bili-qr.png")
CRED = Path(r"E:\Agent-bluefish\bili-credential.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def main() -> None:
    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Referer": "https://www.bilibili.com/"})

    generated = session.get(
        "https://passport.bilibili.com/x/passport-login/web/qrcode/generate", timeout=20
    ).json()
    data = generated["data"]
    qr_url = data["url"]
    qr_key = data["qrcode_key"]

    qrcode.make(qr_url).save(QR)
    print(f"QR_SAVED {QR}", flush=True)

    deadline = time.time() + 170
    while time.time() < deadline:
        try:
            polled = session.get(
                "https://passport.bilibili.com/x/passport-login/web/qrcode/poll",
                params={"qrcode_key": qr_key, "source": "main-fe-header"},
                timeout=20,
            ).json()
        except Exception as error:
            print(f"RETRY {type(error).__name__}", flush=True)
            time.sleep(3)
            continue

        code = (polled.get("data") or {}).get("code")
        print(f"CODE {code}", flush=True)

        if code == 0:
            cookies = {key: value for key, value in session.cookies.get_dict().items()}
            returned = (polled.get("data") or {}).get("url") or ""
            for key, values in parse_qs(urlparse(returned).query).items():
                cookies.setdefault(key, values[0])

            def pick(*names: str) -> str:
                for name in names:
                    if cookies.get(name):
                        return str(cookies[name])
                return ""

            credential = {
                "sessdata": pick("SESSDATA", "sessdata"),
                "bili_jct": pick("bili_jct", "biliJct"),
                "buvid3": pick("buvid3", "buvid_3"),
                "dedeuserid": pick("DedeUserID", "dedeuserid"),
            }
            if not credential["sessdata"]:
                print("EMPTY_SESSDATA cookies=" + ",".join(cookies.keys()), flush=True)
                return
            CRED.write_text(json.dumps(credential, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"CRED_SAVED {CRED}", flush=True)
            return

        if code == 86038:
            print("EXPIRED", flush=True)
            return
        time.sleep(2)

    print("EXPIRED", flush=True)


main()

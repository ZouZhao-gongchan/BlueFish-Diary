# -*- coding: utf-8 -*-
"""用 CDP 打开绝区零官网下载页，抓页面里的下载链接。"""
import json
import subprocess
import time
import urllib.request

from websocket import create_connection

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PROFILE = r"C:\Users\FIshKiller\AppData\Local\Temp\edge-cdp-profile"

proc = subprocess.Popen(
    [EDGE, "--headless=new", "--disable-gpu", "--remote-debugging-port=9222",
     "--remote-allow-origins=*", f"--user-data-dir={PROFILE}", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)

ws = None
try:
    for _ in range(30):
        try:
            targets = json.load(urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=2))
            pages = [t for t in targets if t.get("type") == "page"]
            if pages:
                ws = create_connection(pages[0]["webSocketDebuggerUrl"], timeout=30)
                break
        except Exception:
            pass
        time.sleep(1)
    if ws is None:
        raise RuntimeError("cdp not ready")

    counter = [0]

    def send(method, params=None):
        counter[0] += 1
        mid = counter[0]
        ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == mid:
                return msg

    send("Page.enable")
    send("Runtime.enable")
    send("Page.navigate", {"url": "https://zzz.mihoyo.com/download"})
    time.sleep(15)

    expr = """
    (() => {
      const links = [...document.querySelectorAll('a')].map(a => a.href).filter(Boolean);
      const res = performance.getEntriesByType('resource').map(e => e.name)
        .filter(n => /exe|installer|download|launcher|setup/i.test(n));
      const btns = [...document.querySelectorAll('a,button,div,span')]
        .filter(el => (el.textContent || '').trim().match(/^(PC端下载|下载游戏|立即下载|下载|PC下载)$/))
        .slice(0, 8)
        .map(el => ({tag: el.tagName, text: (el.textContent || '').trim(), href: el.href || ''}));
      return JSON.stringify({links: links.slice(0, 40), res: res.slice(0, 20), btns});
    })()
    """
    r = send("Runtime.evaluate", {"expression": expr, "returnByValue": True})
    print(r.get("result", {}).get("result", {}).get("value", "NO VALUE"))
finally:
    try:
        if ws:
            ws.close()
    except Exception:
        pass
    proc.terminate()

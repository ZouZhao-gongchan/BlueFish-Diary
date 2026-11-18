# -*- coding: utf-8 -*-
"""画一套 Q 版小鱼跳舞帧，拼成 GIF。"""
import json
import os
import urllib.parse
import urllib.request
import uuid

from PIL import Image

HOST = "http://127.0.0.1:8188"
CID = str(uuid.uuid4())
CKPT = "NoobAI-XL-v1.1.safetensors"
OUT_DIR = r"E:\Agent-bluefish\小鱼图库\小鱼表情包"
FRAME_DIR = r"E:\Agent-bluefish\小鱼图库\小鱼跳舞帧"

HEAD = (
    "masterpiece, best quality, very aesthetic, absurdres, chibi, "
    "1girl, solo, blue hair, long hair, blue eyes, fluffy fin ears with white fur trim, whale tail, "
    "white knit sweater with whale pattern, blue plaid skirt, cute, full body, simple background, "
    "pastel blue background, "
)
NEG = (
    "worst quality, low quality, bad anatomy, bad hands, extra fingers, fewer fingers, "
    "watermark, text, signature, username, elf ears, cat ears, animal ears, multiple views, "
    "jpeg artifacts, blurry, deformed"
)

POSES = [
    ("pose-1", "dancing, arms up, one leg raised, happy smile, motion lines"),
    ("pose-2", "dancing, spinning, skirt flaring, arms out, closed eyes, smile"),
    ("pose-3", "dancing, hands on hips, wink, one eye closed, confident smile"),
    ("pose-4", "jumping, arms up, excited, open mouth smile, sparkles"),
    ("pose-5", "dancing, one hand waving, other hand on hip, gentle smile"),
    ("pose-6", "posing, peace sign, tilted head, cute smile, sparkles"),
]


def graph(pos, seed, w=640, h=800):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": HEAD + pos, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": 30, "cfg": 5.5,
            "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1.0,
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0],
        }},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "xiaoyu_dance"}},
    }


def submit(g):
    body = json.dumps({"prompt": g, "client_id": CID}).encode("utf-8")
    req = urllib.request.Request(HOST + "/prompt", data=body, headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["prompt_id"]


def wait(pid, timeout=900):
    import time
    t0 = time.time()
    while time.time() - t0 < timeout:
        with urllib.request.urlopen(f"{HOST}/history/{pid}") as r:
            hist = json.load(r)
        if pid in hist:
            return hist[pid]
        time.sleep(2)
    raise TimeoutError(pid)


def download(entry, path):
    imgs = entry["outputs"]["7"]["images"]
    data = b""
    for im in imgs:
        q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im.get("subfolder", ""), "type": "output"})
        with urllib.request.urlopen(f"{HOST}/view?{q}") as r:
            data = r.read()
    with open(path, "wb") as f:
        f.write(data)
    return path


if __name__ == "__main__":
    os.makedirs(FRAME_DIR, exist_ok=True)
    frames = []
    for i, (tag, pose) in enumerate(POSES):
        pid = submit(graph(pose, 1000 + i * 77))
        entry = wait(pid)
        p = download(entry, os.path.join(FRAME_DIR, f"{tag}.png"))
        frames.append(p)
        print("ok", p, flush=True)

    # 拼 GIF
    imgs = [Image.open(p).convert("RGB").resize((512, 640), Image.LANCZOS) for p in frames]
    gif_path = os.path.join(OUT_DIR, "小鱼跳舞.gif")
    imgs[0].save(gif_path, save_all=True, append_images=imgs[1:], duration=320, loop=0, disposal=2)
    print("GIF", gif_path, os.path.getsize(gif_path))

# -*- coding: utf-8 -*-
"""用本地 ComfyUI + NoobAI-XL 给小鱼画写真。"""
import json
import os
import random
import time
import urllib.parse
import urllib.request
import uuid

HOST = "http://127.0.0.1:8188"
CID = str(uuid.uuid4())
CKPT = "NoobAI-XL-v1.1.safetensors"
OUT_DIR = r"E:\Agent-bluefish\小鱼图库\小鱼表情包"

POS = (
    "masterpiece, best quality, amazing quality, very aesthetic, absurdres, newest, "
    "1girl, solo, blue hair, long hair, blue eyes, fin ears, whale tail, "
    "blue sailor dress, white frills, hair ribbon, upper body, "
    "looking at viewer, gentle smile, blush, "
    "soft lighting, cinematic lighting, depth of field, night, window, starry sky, "
    "water droplets, bubbles, blue theme"
)
NEG = (
    "worst quality, low quality, bad anatomy, bad hands, extra fingers, fewer fingers, "
    "watermark, text, signature, username, jpeg artifacts, blurry, sketch, comic, "
    "multiple views, deformed, mutated"
)


def graph(seed, width, height, steps=28, cfg=5.0):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": POS, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": steps, "cfg": cfg,
            "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1.0,
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0],
        }},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "xiaoyu_meili"}},
    }


def submit(g):
    body = json.dumps({"prompt": g, "client_id": CID}).encode("utf-8")
    req = urllib.request.Request(HOST + "/prompt", data=body, headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["prompt_id"]


def wait(pid, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        with urllib.request.urlopen(f"{HOST}/history/{pid}") as r:
            hist = json.load(r)
        if pid in hist:
            return hist[pid]
        time.sleep(2)
    raise TimeoutError(pid)


def download(entry, name):
    imgs = entry["outputs"]["7"]["images"]
    for im in imgs:
        q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im.get("subfolder", ""), "type": "output"})
        with urllib.request.urlopen(f"{HOST}/view?{q}") as r:
            data = r.read()
    path = os.path.join(OUT_DIR, name + ".png")
    with open(path, "wb") as f:
        f.write(data)
    return path


if __name__ == "__main__":
    jobs = [
        ("meili-1", 832, 1216, 1234567),
        ("meili-2", 832, 1216, 7654321),
        ("meili-3", 832, 1216, 20261024),
        ("meili-4", 832, 1216, 998877),
    ]
    saved = []
    for name, w, h, seed in jobs:
        pid = submit(graph(seed, w, h))
        entry = wait(pid)
        p = download(entry, f"小鱼写真-{name}")
        saved.append(p)
        print("ok", p, flush=True)
    print("ALL DONE", len(saved))

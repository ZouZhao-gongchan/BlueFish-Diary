# -*- coding: utf-8 -*-
"""在基准图基础上，把鱼鳍耳做成毛茸茸的（艺术化，允许蓬松绒毛感）。"""
import json
import os
import urllib.parse
import urllib.request
import uuid

from PIL import Image

HOST = "http://127.0.0.1:8188"
CID = str(uuid.uuid4())
CKPT = "NoobAI-XL-v1.1.safetensors"
COMFY_INPUT = r"E:\ComfyUI\ComfyUI_windows_portable\ComfyUI\input"
OUT_DIR = r"E:\Agent-bluefish\小鱼图库\小鱼表情包"
BASE = r"E:\Agent-bluefish\小鱼图库\小鱼表情包\小鱼-形象基准-1.png"

POS = (
    "masterpiece, best quality, very aesthetic, absurdres, newest, "
    "1girl, solo, blue hair, long hair, blue eyes, "
    "blue fin ears, fluffy fuzzy fin ears, soft fur trim on ears, detailed ear fins with fine hairs, "
    "fluffy ears, fuzzy ear edges, whale tail, "
    "blue maid dress, white frills, hair ribbon, smile, looking at viewer, "
    "soft lighting, white background, bubbles, blue theme"
)
NEG = (
    "worst quality, low quality, bad anatomy, bad hands, extra fingers, fewer fingers, "
    "watermark, text, signature, username, elf ears, pointy human ears, cat ears, animal ears, "
    "jpeg artifacts, blurry, multiple views, deformed, bald"
)


def prepare(size):
    img = Image.open(BASE).convert("RGB")
    tw, th = size
    ar = tw / th
    w, h = img.size
    if w / h > ar:
        nw = int(h * ar)
        img = img.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w / ar)
        img = img.crop((0, (h - nh) // 2, w, (h + nh) // 2))
    img = img.resize(size, Image.LANCZOS)
    name = "ref_xiaoyu_base1.png"
    img.save(os.path.join(COMFY_INPUT, name), "PNG")
    return name


def graph(ref_name, seed, denoise, w, h):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": POS, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
        "8": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
        "9": {"class_type": "VAEEncode", "inputs": {"pixels": ["8", 0], "vae": ["1", 2]}},
        "5": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": 32, "cfg": 5.5,
            "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": denoise,
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["9", 0],
        }},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "xiaoyu_fluffy"}},
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


def download(entry, name):
    imgs = entry["outputs"]["7"]["images"]
    data = b""
    for im in imgs:
        q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im.get("subfolder", ""), "type": "output"})
        with urllib.request.urlopen(f"{HOST}/view?{q}") as r:
            data = r.read()
    path = os.path.join(OUT_DIR, name + ".png")
    with open(path, "wb") as f:
        f.write(data)
    return path


if __name__ == "__main__":
    size = (832, 1248)
    ref = prepare(size)
    jobs = [
        ("毛茸-1", 24680, 0.45),
        ("毛茸-2", 13579, 0.55),
        ("毛茸-3", 97531, 0.62),
    ]
    for tag, seed, dn in jobs:
        pid = submit(graph(ref, seed, dn, size[0], size[1]))
        entry = wait(pid)
        print("ok", download(entry, f"小鱼-耳朵{tag}"), flush=True)
    print("DONE")

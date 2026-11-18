# 背景制作

把 Wallpaper Engine 的壁纸做成 dsh-video-skin 聊天背景用的脚本和素材。

- `unpkg2.py` / `extract_art4.py` / `carve.py` —— 解 `scene.pkg`：静态图是内嵌 JPEG，视频壁纸是内嵌 mp4。
- `ken.py` —— 静态立绘 → 慢推镜无缝循环视频（PIL 亚像素仿射 + numpy 暗角 + 飘雪层）。
- `combo.py` —— 把两段拼成一条，中间用「smootherstep + 中点压暗 + 解焦」的溶解；改 `CLIP_FRAMES` 调每段停留时间。
- `art\06_art.png`（2312×1254）、`art\30_art.png`（1920×1080）—— 从 pkg 里抠出来的原画，重渲染要用。

跑法：`python ken.py art\30_art.png out.mp4 1.07 40 1`（1.07=最大推近倍率，40=秒，1=开飘雪）。
需要装了 Pillow + numpy 的 Python（我用的是 ComfyUI 自带的那个）和 PATH 里的 ffmpeg。
"""从插件原始 skin.js 重新打「活换背景」补丁（之前那版换片失败会把整个背景拆掉）。

锚点：buildBackdrop 里 `var delayTimer = global.setTimeout(load, delayMs)` 之后插轮询。
"""
import os, shutil, sys

PLUGIN = r"E:\Agent-bluefish\Save\dsh-home\profiles\desktop\node_modules\dsh-video-skin"
VANILLA = r"E:\Agent-bluefish\Backups\video-skin-live-20261119\skin.js.bak"
TARGET = os.path.join(PLUGIN, "runtime", "skin.js")
SNAP = r"E:\Agent-bluefish\Backups\video-skin-live-20261119\skin.js.patched"

shutil.copyfile(VANILLA, TARGET)
src = open(TARGET, "r", encoding="utf-8").read()
print("原始 skin.js:", len(src), "字符")
if "watchTimer" in src:
    print("原文件里已经有补丁，停下"); sys.exit(1)

anchor = "    // 延后加载：开机阶段把带宽和 CPU 留给界面本身。\n    var delayTimer = global.setTimeout(load, delayMs)\n"
if anchor not in src:
    print("找不到锚点"); sys.exit(1)

block = '''    // ── 换素材不必刷新页面 ──────────────────────────────────────
    // 页面按 `background.src`（带 ?v= 内容指纹）判断要不要换片。
    // 关键：**先让新元素加载成功，再顶替旧元素**。换片失败一律保住旧画面 ——
    // 2026-11-19 踩过：换片瞬间文件正被别的进程改写 → 新视频 error → 旧实现顺手
    // teardownBackdrop() → 整个背景消失，还要重启才能回来。
    var swapBackdrop = function (nextSrc, rate) {
      if (backdrop === null) return
      var layer = backdrop.layer
      var old = backdrop.video
      if (!layer || !old || !doc.createElement) return
      var fresh = doc.createElement('video')
      fresh.id = 'dsvs-backdrop-video'
      fresh.muted = true
      fresh.defaultMuted = true
      fresh.loop = true
      fresh.playsInline = true
      fresh.autoplay = false
      fresh.preload = 'auto'
      fresh.setAttribute('playsinline', '')
      fresh.setAttribute('muted', '')
      fresh.setAttribute('aria-hidden', 'true')
      try {
        fresh.playbackRate = rate
      } catch (error) {
        /* 忽略 */
      }
      var settled = false
      var dropFresh = function () {
        try {
          fresh.pause()
        } catch (error) {
          /* 忽略 */
        }
        if (fresh.parentNode) fresh.parentNode.removeChild(fresh)
      }
      fresh.addEventListener('loadeddata', function () {
        if (settled) return
        settled = true
        fresh.setAttribute('data-shown', '1')
        if (backdrop === null) {
          dropFresh()
          return
        }
        backdrop.video = fresh
        try {
          old.pause()
        } catch (error) {
          /* 忽略 */
        }
        if (old.parentNode) old.parentNode.removeChild(old)
      })
      fresh.addEventListener('error', function () {
        if (settled) return
        settled = true
        api.state.failures.push('backdrop-swap-error:' + (fresh.error ? fresh.error.code : 0))
        dropFresh()
        old.setAttribute('data-shown', '1')
      })
      layer.insertBefore(fresh, old)
      fresh.src = nextSrc
      var played = fresh.play()
      if (played && typeof played.catch === 'function') played.catch(noop)
    }

''' + anchor

src = src.replace(anchor, block, 1)

poll = '''
    // 每 4 秒回读一次运行期配置：素材地址变了就换片。
    if (typeof global.fetch === 'function' && configUrl !== '') {
      var pickedSrc = src
      var watchTimer = global.setInterval(function () {
        if (backdrop === null) return
        global.fetch(configUrl, { cache: 'no-store' })
          .then(function (res) { return res.json() })
          .then(function (next) {
            if (backdrop === null) return
            var nb = isObject(next) && isObject(next.background) ? next.background : null
            if (nb === null) return
            var nextSrc = typeof nb.src === 'string' ? nb.src : ''
            if (nextSrc === '' || nextSrc === pickedSrc) return
            pickedSrc = nextSrc
            liveCfg = mergeConfig(liveCfg, { background: nb })
            api.config = liveCfg
            applyVisuals(liveCfg)
            swapBackdrop(nextSrc, num(nb.playbackRate, 1, 0.25, 4))
          })
          .catch(noop)
      }, 4000)
      backdrop.watchTimer = watchTimer
    }
'''

# 插在 delayTimer 那行之后
idx = src.index(anchor) + len(anchor)
src = src[:idx] + poll + src[idx:]

# teardown 里清掉定时器
tear = "  function teardownBackdrop() {\n    if (backdrop === null) return\n"
if tear not in src:
    print("找不到 teardown 锚点"); sys.exit(1)
src = src.replace(tear, """  function teardownBackdrop() {
    if (backdrop === null) return
    try {
      if (backdrop.watchTimer) global.clearInterval(backdrop.watchTimer)
      backdrop.watchTimer = null
    } catch (error) {
      /* 尽力而为 */
    }
""", 1)

open(TARGET, "w", encoding="utf-8", newline="\n").write(src)
shutil.copyfile(TARGET, SNAP)
print("打好了:", len(src), "字符；快照:", SNAP)

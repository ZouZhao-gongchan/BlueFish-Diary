"""把「毛先生」写回 dsh-startup-secret 的 splash.js：加第 6 款立绘 + 左群像右毛先生。

会被 npm 重装冲掉 —— 打完之后会把成品存一份到 Backups，附还原命令。
"""
import base64, os, re, shutil, sys

SPLASH = r"E:\Agent-bluefish\Save\dsh-home\profiles\desktop\node_modules\dsh-startup-secret\lib\splash.js"
IMG = r"E:\Agent-bluefish\working\收纳\03-截图\20261119-毛先生重做\B-版画三色.webp"
BK = r"E:\Agent-bluefish\Backups\startup-secret-lib-20261118"

src = open(SPLASH, "r", encoding="utf-8").read()
print("原文件", len(src), "字符")

if "MASCOT_SRC_5" in src:
    print("已经打过补丁（含 MASCOT_SRC_5），先退出，避免重复插")
    sys.exit(0)

b64 = base64.b64encode(open(IMG, "rb").read()).decode("ascii")
print("立绘 base64", len(b64), "字符")

# 1) 在 MASCOT_SRC_4 那一行后面插入 MASCOT_SRC_5
m = re.search(r"var MASCOT_SRC_4 = '[^']*'\n", src)
if not m:
    print("找不到 MASCOT_SRC_4 定义")
    sys.exit(1)
insert = "var MASCOT_SRC_5 = 'data:image/webp;base64,%s'\n" % b64
src = src[: m.end()] + insert + src[m.end():]

# 2) MASCOTS 数组加第 6 项
old_arr = "var MASCOTS = [MASCOT_SRC, MASCOT_SRC_1, MASCOT_SRC_2, MASCOT_SRC_3, MASCOT_SRC_4]"
new_arr = "var MASCOTS = [MASCOT_SRC, MASCOT_SRC_1, MASCOT_SRC_2, MASCOT_SRC_3, MASCOT_SRC_4, MASCOT_SRC_5]"
if old_arr not in src:
    print("找不到 MASCOTS 数组原定义")
    sys.exit(1)
src = src.replace(old_arr, new_arr, 1)

# 3) 立绘渲染：右边写死第 6 款（index 5），左边常驻第 5 款（index 4）
start = src.index("  ui.mascot = q('.dsu-mascot')")
end_marker = "  ui.event = q('.dsu-event')"
end = src.index(end_marker)
old_block = src[start:end]

new_block = """  ui.mascot = q('.dsu-mascot')
  /* 左右双立绘，编号写死、不看配置 —— 配置会被插件回写的快照盖掉。
     定位一律走内联样式：splash.css 可能被旧缓存顶着，right:0 不生效会跑到左边重叠。 */
  var RIGHT_IDX = 5
  var LEFT_IDX = 4
  var mascotStyle = function (box, side) {
    box.hidden = false
    box.removeAttribute('hidden')
    box.style.position = 'fixed'
    box.style.bottom = '84px'
    box.style.width = '250px'
    box.style.zIndex = '22'
    box.style.opacity = '1'
    box.style.transform = 'none'
    box.style.pointerEvents = 'none'
    if (side === 'left') { box.style.left = '0'; box.style.right = 'auto' }
    else { box.style.right = '0'; box.style.left = 'auto' }
  }
  if (C.showMascot !== false) {
    if (RIGHT_IDX < MASCOTS.length) {
      ui.mascot.setAttribute('data-mascot', String(RIGHT_IDX))
      var rightImg = document.createElement('img')
      rightImg.className = 'dsu-mascot-img'
      rightImg.alt = ''
      rightImg.draggable = false
      rightImg.setAttribute('src', MASCOTS[RIGHT_IDX])
      ui.mascot.appendChild(rightImg)
      mascotStyle(ui.mascot, 'right')
    } else {
      ui.mascot.hidden = true
    }
    if (LEFT_IDX < MASCOTS.length) {
      var leftBox = document.createElement('div')
      leftBox.className = 'dsu-mascot'
      leftBox.setAttribute('data-mascot', String(LEFT_IDX))
      var leftImg = document.createElement('img')
      leftImg.className = 'dsu-mascot-img'
      leftImg.alt = ''
      leftImg.draggable = false
      leftImg.setAttribute('src', MASCOTS[LEFT_IDX])
      leftBox.appendChild(leftImg)
      mascotStyle(leftBox, 'left')
      root.appendChild(leftBox)
    }
  } else {
    ui.mascot.hidden = true
  }
"""
src = src[:start] + new_block + src[end:]

open(SPLASH, "w", encoding="utf-8", newline="\n").write(src)
print("写回完成，新长度", len(src), "字符")

# 4) 存一份打完补丁的成品，方便被冲掉后还原
os.makedirs(BK, exist_ok=True)
snap = os.path.join(BK, "splash.js.patched")
shutil.copyfile(SPLASH, snap)
print("已存快照:", snap, round(os.path.getsize(snap) / 1024, 1), "KB")

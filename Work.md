# Work · 工作台

> 留给工作用的地方。想到什么先记下来，做完的移到「已完成」，不用讲究格式。

## 小鱼工作台 v2.8 · 科技感装修 + 对话通道（能发图）+ 任务板（2026-11-20 23:5x，最新，先读这一节）

> 比下面那节「22:4x 整页总结」新；那节写的是 v2.6 的接口与功能全景，仍然有效。

### ⚠️ 2026-11-20 事故与恢复（已收口：两个文件都回来了）

- **事故**：为了让版本号对齐，我用 PowerShell `Get-Content -Raw | Set-Content -Encoding UTF8` 直接改 `client.js`/`index.js`——PS 5.1 按 GBK 读 UTF-8，两个文件中文全部变乱码（client 164KB / index 66KB，代码骨架在、中文与注释坏了几百处）。
- **恢复手段（可复用，记下来）**：
  1. **会话日志**：`$DSH_HOME\sessions\...\session.v4.jsonl.zstd` 是**多帧 zstd**，Node 的 `zstdDecompressSync` 只解第一帧；按 zstd 帧头/块头自己切帧后逐帧解压，拿到完整 JSONL（当前会话 52MB），里面记录了我每一次 `write`/`edit` 的原文参数。
  2. **工作区捕获**：`%TEMP%\dsh-workspace-changes-*\captures\` 里有 DSH 记下的**文件历史快照**（按内容寻址）。这次捞到 `client.js v2.6` 的完整快照（116,859 字节，中文完好）。
  3. **从快照出发重放**日志里之后的 45 条 edit/write，重建出 v2.8（44 条命中，1 条漏掉的配色/MONO 编辑手工补上）。校验：`node --check` 过、渲染冒烟 **17 个组件 0 抛错**、活体验收 **24/24 PASS**。
  4. `index.js` 另走一条：坏文本按 GBK 反向编码 + 逐条替换 + 正则修复，0 个坏字符、语法过、热重载后 24/24 PASS。
- **教训（写进习惯）**：**永远不要用 PowerShell 改含中文的源码**——改文件一律用编辑工具或 Node（`fs.readFileSync/'utf8'`）；要批量改就写 .mjs 脚本。PS 只用来跑命令、看输出。

### 这轮做了什么（阿冉要的三件）

1. **科技感装修（深空 HUD，默认开）**：四角括号（12px 臂 / 1px 线 / 淡纹 0.22）、卡片顶发丝线（左 18% 亮）、右上 `DECK-01` 编号、状态灯换成 **14px 刻度环 + 7px 灯芯**（只有当前行允许 ping）、控制室读数改成四列仪表（2px 竖条 + 26px 等宽数字 + micro 标签）、左侧栏右缘 6px 刻度带 + 行号 01–09 + 当前行 2px 蓝竖条、网格升成 48/240px 双层并加径向渐隐、静态扫描线（1 亮 3 暗 ×3%）+ 一条 26s 扫描带、顶栏底部 5px 刻度尺。**霓虹只有一种蓝**（spec 的克制清单）。
2. **对话通道（阿冉最想要的那件）**：工作台里一个抽屉，直接跟小鱼说话、布置任务。读回走 `sessionController.inspect`（把会话日志里的 user/assistant 文本块抽出来），投递走 `sessionController.prompt`（mode=queue，等于阿冉在聊天框里打字）。有「继续 / 报告一下进度 / 先停一下」快捷词、状态灯（RUNNING/IDLE）、3 秒自动刷新、Enter 发送。
3. **任务板 + 控制室读数联动**：控制室「在跑成员 / 任务」两个读数变成可点（带 ›），点开是任务板抽屉：成员（状态/角色/模型/在做什么）+ 任务（状态/认领人/写盘范围/被卡住）+ 点任务行展开说明。真数据：`agentTeams.listMembers` + `listTasks`。

### v2.9 体验补丁（2026-11-20 22:1x）

- **Shift+Enter 换行修好**：DSH 壳的全局快捷键先把 Shift+Enter 的默认行为 preventDefault 了，所以输入框里按了没反应。改成输入框自己插换行（按光标位置插、插完光标停下一行），加输入法组合期保护（选词回车不误发）；文件编辑框同一个坑一起补了。回归用例在渲染冒烟里（Shift+Enter → value="\n"、Enter → fetch 涨）。
- **「对话之后被拉出工作台」找到原因并修好**：DSH 的 client HMR 在我每次改 `client.js` 时会重建并热替换这个插件的浏览器半边 → 工作台整个重挂、状态清零 → 人就被弹出来了。现在把「开着没关 / 停在哪个项目 / 对话抽屉开着 / 没发完的草稿」都记进 sessionStorage，热重载后自动弹回原位。
- **紧凑密度开关**：控制室新增「密度 · 紧凑 / 舒适」，默认紧凑——卡片 148→118 高、间距 18→11、控制室留白和底栏一起收紧，**字号不缩**（正文 12.5–13px 守住）。

### v3.0 项目页四宫格（2026-11-20 22:2x）

- 项目页在紧凑模式下改成 **2×2 网格**：左上画像、右上文件、左下预览、右下终端/网页/手机（三个开关二选一，默认留空提示）；整页高度 `calc(100vh - 200px)`，四块各自内部滚动，一屏看完不整页滚。
- 顶部工具条：← 总览 / 项目名 / 「文件·预览·网页·终端·手机」五个开关 chip / 根目录 / 网址输入框；原来的「面板开关」侧栏只留在舒适模式。
- **舒适模式保留旧竖排布局**（控制室「密度」键切回），四宫格只是紧凑模式的形态。
- 回归：渲染冒烟里加了 `[四宫格] display=grid · cols=minmax(300px…) · rows=minmax(150px,25vh)…` 断言，18 个组件 0 抛错。

### v3.1 右下对话抽屉（2026-11-20 22:3x）

- 阿冉说「喜欢抽屉设计」：项目页**右下那格改成对话抽屉**——内嵌对话（不是全屏抽屉），默认展开；点「收起 ▾」缩成一条 bar，点 bar 再展开；开合状态记 sessionStorage，热重载不丢。
- 右下格与终端/网页/手机**共用**：打开它们时右下自动切成 tab 组（对话 | 终端 …），关掉自动回对话；点上面 chip 也会把右下切过去。
- **画像窄版**：原来三列布局挤在 ~380px 里、文字成团（阿冉截图里能看到），改成 compact 单列（`ProfilePanel` 加 compact prop）。
- 顺手：`Console` 支持 `embedded` 模式（无遮罩、无固定抽屉宽、可收起）。
- 回归：18 组件 0 抛错；新增断言「内嵌 Console 存在 / 有收起按钮 / 收起后出现展开条 / 再点能展开」。

### v3.2 抽屉动画 + 「正在…」状态条（2026-11-20 22:4x）

- **抽屉开合带一点动画**：内嵌对话出现时 `bfw-dock-in`（上滑 10px + 淡入 190ms），收起后的展开条同款 170ms——不再「啪」地切换。
- **宿主新接口 `GET /activity`**：读 Lead 会话**当前 turn** 的 tool/call，翻译成人话（读/写/改哪个文件、跑什么命令、搜什么、派哪个成员），1200ms 缓存。
- **对话抽屉顶部状态条**：绿点脉冲 + 「正在：改 client.js」+「3 秒前」；闲下来显示「刚才：…」。
- 验收脚本加一项 → **25 项全 PASS**（`/activity 当前在干什么 — 跑命令：…` 是活的）；渲染冒烟断言「状态条=true」，18 组件 0 抛错。

### v3.3 / v3.4 两处体验修补（2026-11-20 22:5x）

- **v3.3 对话噪音**：`/chat` 原来会把 DSH 内部注入的 `Time sampled while preparing turn…` 和自检消息当成「阿冉说的话」显示。现在过滤掉（正则 + 自检前缀），实测最近 12 条噪音 0 条。对话头也从 `LINK · LEAD · RUNNING` 改成「投给 · 本间会话（LEAD）」，写清在跟谁说话。
- **v3.4 滚动穿透**：在对话里滚到尽头，滚轮会继续带动后面的大界面（scroll chaining）。给 7 个滚动区加 `overscroll-behavior: contain`——对话列表 / 任务板 / 主内容 / 侧栏 / 终端 / 面板体 / 抽屉本身。内层滚到头就停，不再传出去。
- 说明：工作台里所有项目页的对话，投递目标都是**同一个 Lead 会话**（聊天这间）；项目页只是看文件/画像，没有连到别的会话。要「按项目投到对应会话」是另一个功能（未做，待阿冉拍板）。

### v3.5 悬停手感（2026-11-20 23:0x）

- 阿冉说「新建项目卡能点但死气沉沉」：统一加 hover 反馈——
  - `.bfw-hov`：按钮 / 控制室偏好键 / 底栏 / 对话快捷词 / 右下 tab → 蓝边 + 淡蓝底 + 字变亮
  - `.bfw-hov-row`：侧栏行 / 文件行 / 可点读数 → 淡白底
  - `.bfw-hov-card`：项目卡 → 上浮 2px + 发光阴影
  - `.bfw-hov-dash`：新建项目虚线卡 → 虚线变亮蓝 + 加号放大 1.15 + 背景微亮
  - 按下统一 1px 下压（`:active`）
- 实现方式：CSS 规则注入 overlay 的 `<style>` 串（用 `!important` 压内联样式），不给每个组件加 hover state。
- 冒烟加断言：新建项目卡带 `bfw-hov-dash` 类、样式表里有 `.bfw-hov-dash:hover` 规则。

### 代码与生效

- 客户端 **v2.7** `client.js`（~150KB）：新增 `HudFrame / StatusLight / CardCorners / Console / TeamPanel` + `useChat / useTeam`；新偏好键 `skin`（hud / glass），控制室「皮肤」键切换。
- 宿主 **v1.4** `index.js`：新增 `/chat`、`/prompt`、`/team` 三条接口 + `findLead / pickText / readChat / readTeamDetail` 四个函数。
- **生效**：改 client → 刷新页面；改 host → `plugin_manager` 对 `include:bluefish-workbench` 设一次 `enabled=true`（热重载，不用重启 DSH）。
- 快捷键新增：**T = 对话、B = 任务板**；顶栏和底栏都有按钮。

### 新接口（都在 `/bluefish-workbench/` 下，exact + query）

- `GET /chat?limit=40` → `{ ok, sessionId, lead, status, total, messages:[{role,text,time,seq}], lastSeq }`（内含 800ms 缓存，读一次整份日志约 47ms）
- `POST /prompt { text, sessionId? }` → `{ ok, accepted, sessionId, requestId, mode:'queue' }`；空文本 400；错会话 502 + `code:'session/not-found'`
- `GET /team` → `{ ok, lead, members:[{id,name,role,status,description,model,…}], tasks:[{id,subject,status,ownerName,ready,writeScopes,warnings}] }`

### 验收证据（外部，别只看这里）

- 活体验收：`工作台验收.mjs` **21/21 PASS**（新增 `/chat` 5 条/共 971、`/team` 4 人 2 件、`/prompt` 空文本 400、错会话 `session/not-found`）。
- 渲染冒烟：`%TEMP%\wb_test\test_client_render.mjs` **17 个组件 0 抛错**（含 Console / TeamPanel / HudFrame / StatusLight / CardCorners / Markdown），对话抽屉能渲染气泡、任务板能渲染成员与任务。
- 真投递：`POST /prompt` 返回 `accepted:true`（当前轮在跑 → 排在收件箱，本轮结束后以一条用户消息落到会话）。
- 设计 spec：`收纳\02-文档\设计\工作台-科技感皮肤-spec.md`（成员 hud-designer 产出，210 行，含配色对比度实算与并发上限）。

### 坑 / 注意

- 投递是 `mode:queue`：**当前轮没结束就不会落库**，所以「投完立刻 /chat 看不到」是正常的，不是失败。
- `/prompt` 用不存在的 `sessionId` 会回 `session/not-found` —— 拿来当「通道授权 + 入参形状」自检，不会真发消息。
- `inspect` 是整份读，会话越长越慢（971 条约 47ms），已在宿主加 800ms 缓存；再长就该换 `page`/`follow`。
- 前端改完必须同时跑 `node --check` + 渲染冒烟：`node --check` 查不出未定义变量（曾漏 state 导致整层打不开）。

### 下一步候选

- 对话抽屉里显示「正在写哪个文件 / 正在跑哪条命令」的实时状态（读 session 里当前 turn 的 tool-call）。
- 任务板能派单/认领（`agentTeams.createTask / updateTask` 已在宿主侧确认可调，只差 UI）。
- 控制室数字点击跳转（花费 → cost-meter 面板；余额 → 账户页）。


## 进行中
## 小鱼工作台交接 · 2026-11-20 22:4x（压缩后先读这一节）

> 这一节是「现在到底什么样」的整页总结；下面那节「2026-11-20 工作台交接（18:40）」是过程记录，只在需要翻旧账时看。

### 一句话状态

功能清单（7 项）**全部做完**，活体验收 **15/15 PASS**；客户端 **v2.6**、宿主 **v1.3**。下一步是阿冉要的「**装修 + 加功能**」——方向还没定，压缩后先问他。

### 代码与生效方式

- 插件：`@local/bluefish-workbench`，源码 `E:\AFishPower\Plugin\bluefish-workbench`（`index.js` 宿主、`client.js` 客户端、`assets\intro.mp4`、`tools\pdf_text.py`）。profile 里 **link 装**，不重装。
- **改 `client.js` → 刷新页面**。
- **改 `index.js` → 不用重启 DSH**：`plugin_manager` 里 `set_plugin` 对 `include:bluefish-workbench` 设 `enabled=true`，它会重新加载插件（实测 `/info` 404→200）。**这是本次最大的效率发现。**
- 数据：`$DSH_HOME\bluefish-workbench\projects\<id>\状态.json`（status / note / owner / claimedAt / handovers）+ `项目信息.md`（一、这是什么 / 二、当前交接 / 三、约定与坑 / 四、归档 / 五、近期结论）；公告在 `$DSH_HOME\bluefish-workbench\公告.jsonl`；渲染/提取缓存 `preview\<hash>\`；pypdf 隔离装在 `pylib\`。

### 接口（都在 `/bluefish-workbench/` 下，插件路由不走鉴权）

- 读：`/overview`（控制室真数 + 6 张卡 + 最近接手）、`/profile?id=`、`/info?id=`（项目信息原文）、`/index?id=`（项目内 md/txt/json/代码 ≤200 个）、`/files?path=`、`/file?path=`、`/raw?path=`（二进制 ≤24MB）、`/browse?path=`（本地文件栏，只放行 D:/E:）、`/render?path=`（Office/PDF→PNG 页图，LibreOffice Kit）、`/page?id=&name=`（页图）、`/text?path=`（docx/odt/rtf 走 LibreOffice、pdf 走 pypdf，带缓存）、`/asset?name=`（插件素材）
- 写：`POST /claim`（接手）、`POST /handover`（写交接三条）、`POST /project`（新建项目，dir 必须已存在）、`POST /exec`（终端，20s 超时、cwd 限项目根或 D:/E:）、`POST /save`（文本保存，先写 `.bak-时间戳`）、`POST /open`（交给系统默认程序）

### 客户端功能全景

- **控制室**：今日花费（真）、官方余额（`deepseekAccount.getBalance`，含赠金）、在跑成员 / 任务（`agentTeams` 真数据；拿不到就「—」+ 悬停说明未接）、最近接手公告、五个偏好键（深浅/圆卡/背景/列数/开场）＋「更新」。
- **项目卡**：四色状态灯 + 工作中柔光扫过 + 黄/蓝边框流光；**卡在哪≠「没有卡点」→ 卡片黄边呼吸 + 「卡着」标**；卡上显示「交接 · 上次做到」、接手人、最近改动。
- **画像卡**：一句话 / 上次做到·下一步·卡在哪（可「写交接」直接改 项目信息.md）/ 近期结论（绿字）/ 最近改动 3 个文件（点开预览）/ 约定与坑条数 / 接手与接手记录 /「索引」「开文档」按钮。
- **项目页**：文件窗（带字形图标）+ 预览窗（Markdown 排版、图片、视频 `<video>`、音频 `<audio>`、JSON 美化、Office/PDF 页图、**「提取文字」弹窗可复制**、文本「编辑→保存」带备份）+ 网页 iframe + 终端（↑/↓ 历史、危险命令确认）+ 手机预览 + 面板开关。
- **本地文件栏**：D:/E: 只读浏览，路径输入框 + 「跳转」按钮 + 盘符按钮 + 图片缩略图 + 同款预览窗。
- **其它**：左栏搜索/状态筛选（下拉带数量、快捷键 F）、新建项目弹窗与快捷键 N/R///L/C、开场动画（小鱼 `intro.mp4` + canvas 像素字，**每次 DSH 启动后只播第一次**，可关）。
- **偏好**存 localStorage（`bfw-prefs-v1`）。

### 验收与自测工具（改完就跑，别靠感觉）

- **活体验收**：`node "收纳\01-脚本\DSH维护\工作台验收.mjs"` → 15 项 PASS/FAIL（自动找 DSH 端口）。
- **客户端渲染冒烟**：`%TEMP%\wb_test\test_client_render.mjs` 用迷你 React 真跑组件树（抓 undefined 变量这类 `node --check` 查不出的错）。
- **体检**：`体检.mjs`（周日 21:00 自动）；**交接速览**：`生成交接速览.mjs`。

### 踩过的坑（别再踩）

1. **DSH 的 webServer 不支持 prefix 路由**（实测 404）→ 一律 exact + query。
2. **`node --check` 查不出未定义变量**：曾漏插 `infoDoc` 状态，导致工作台整个打不开；前端改完必须跑渲染冒烟。
3. 改代码别按行号大段删；这次已经吃过一次「删过头、语法还过」的亏。
4. 插件目录里 Python 写不进去（PermissionError）；pypdf 装到 `$DSH_HOME\...\pylib`。
5. `intro.mp4` 必须去音轨（`-an`），不然切进工作台会突然有声。
6. 开场动画只播一次靠 `sessionStorage['bfw-intro-shown']`；改「开场」偏好会清标记。

### 下一步（阿冉要「装修 + 加功能」，方向待定）

- 装修候选：主题皮肤（现在只有深/更亮两档）、卡片动效、布局自定义、图标系统、控制室可视化。
- 功能候选：控制室读数可点击跳转、任务板与 Agent Teams 联动、项目拖拽排序/分组、图片/文件直接拖进来、更多面板（SSH 已确认不要，终端已有）。
- **压缩后第一句先问阿冉：装修想从哪块开始、要不要先找参考图。**


### 2026-11-20 工作台过程记录（18:40 之前的历史，最新状态看上面那节）

- **开工先读**：同目录 `交接速览.md`（工作台数据自动生成：6 个项目谁在跟 / 做到哪 / 下一步 / 卡在哪）。项目明细不在注入层，这一页才是跨会话交接的入口；它由 `收纳\01-脚本\DSH维护\生成交接速览.mjs` 生成。
- **插件**：`@local/bluefish-workbench`，源码 `E:\AFishPower\Plugin\bluefish-workbench`（`index.js` 宿主 **v0.9** / `client.js` 浏览器半边 **v1.4** / `package.json` / `cordis.patch.yml` / `icon.svg`）。profile 里是 **link 装的**，改源码不用重装。
- **生效方式**：改 `client.js` → **刷新页面**；改 `index.js` → **必须重启 DSH**（路由在启动时注册）。宿主 v0.7 `/browse`、v0.8 `/exec` 已生效（18:5x 验证）；**v0.9 `/project`（新建项目）要再重启一次**。
- **数据**：`$DSH_HOME\bluefish-workbench\projects\<id>\状态.json` + `项目信息.md`（≤25KB / 交接 ≤4KB）。`状态.json` 里现在还有 `owner` / `claimedAt` / `handovers`（接手记录，留最近 8 条）；接手公告另写 `$DSH_HOME\bluefish-workbench\公告.jsonl`。改文件 = 改画面，10 秒内自动刷新。
- **接口**：只读 `/overview`（含 announcements 最近接手）、`/profile?id=`、`/browse?path=`（本地文件栏：只放行 D:\ 和 E:\）、`/files?path=`、`/file?path=`（文本前 64KB）、`/raw?path=`（二进制 ≤24MB）；写 `POST /claim`（`{id, owner}`，顺带记 handover + 公告）、`POST /handover`（`{id, handoff, next, blocked}`）、`POST /exec`（`{cmd, cwd}` 终端：跑一条 PowerShell，**20 秒超时、输出各截 200KB、cwd 只认项目根或 D:/E:**）。`POST /project`（`{name, dir}` 新建项目，dir 必须是已存在的绝对目录）。**`/file` `/raw` 也放行 D:/E: 盘内任意文件（本地文件栏要用）**。
- **无用键全接通（v1.2/v0.9，阿冉 18:5x「还有很多无用键，完成无用键变有用再走下一步」）**：
  - 左栏「查」→ 搜索框（按名字过滤项目，`/` 也能叫出来）；「筛」→ **下拉选择框**（全部/工作中/待审批/已完成/空闲，每项带数量、当前项打勾，点空白或 Esc 关，快捷键 F）；筛选生效后底栏出现「筛：工作中 ×」可一键清；「＋」→ 新建项目弹窗。
  - 控制室五个键：**深浅**（整层亮度深/浅，存 localStorage）、**圆卡**（卡片圆角 20/12）、**背景**（网格开/关）、**列数**（2/3/4 循环）、**更新**（立刻刷新，并显示「更新于 HH:MM:SS」）。
  - 「＋ 新建项目」虚线卡 → 弹窗填名字 + 已存在目录 → `POST /project` 生成状态.json 与项目信息.md。
  - 底栏原来那句「派单 / 验收 / 新建项目 / 圈选页面提要求」是假承诺，**换成真按钮**：＋新建 / ⟳刷新 / ⌕搜索 / ▤本地文件 / ✓跑体检；右边提示改成真快捷键 `[N] [R] [/] [L] [C]`。
  - 快捷键：N 新建 · R 刷新 · / 搜索 · L 本地文件 · C 跑体检（体检 = 调 `/exec` 跑 `体检.mjs` + `生成交接速览.mjs`，跑完弹 toast 并刷新）。
  - 偏好存 localStorage（`bfw-prefs-v1`），刷新页面还在。
- **本地文件栏（v1.0）**：左侧列表最下面一行「本地文件」，点进去是 D: / E: 只读浏览——盘符按钮 + 上一级 + 目录列表 + 预览窗（md 排版 / 图片 / JSON 都走同一个 `FilePreview`）。**只读，不能改不能删。** v1.4 修：进去自动打开上次的盘（默认 D:\）不再空白；列表头带 D/E 盘符按钮；文件带字形图标（▸ 目录 / 文 / 图 / 配 / 码）；空目录给提示。
- **终端 · PowerShell（v1.1/v0.8，阿冉 18:4x 定的：不做 SSH 改本机 PowerShell）**：项目页「面板开关」里第 4 项「终端」——在项目路径下跑 PowerShell 命令，带 `>` 输入行、回车运行、输出区自动滚到底、`[exit N · 毫秒]` 行、「清空」按钮。宿主用 `spawn('pwsh' → 退回 powershell.exe)`，命令前垫 `[Console]::OutputEncoding=UTF8`（不然中文报错是乱码）；工作台里所有项目页共用，cwd 跟着当前目录走。
- **三环交接（v0.7/v1.0）**：① **注入**——`交接速览.md` 由脚本从工作台数据生成，MEMORY 里指向它（每轮注入），换会话开工先读；② **回执**——接手写 `handovers` 记录（上次交接：A → B · 时间）+ 画像卡显示；③ **广播**——接手事件写 `公告.jsonl`，总览控制室下面显示「最近接手：X · A → B · 3 分钟前」。**跨会话主动弹送仍然没有**，所以「开工读速览」才是真正收到的那一刻，这一点写在速览文件末尾了。
- **形态**：会话标题旁「工作台」按钮 → 全屏层（`requestFullscreen` 会收掉任务栏）→ 左侧工作台列表（控制室 / 各项目 / 本地文件）+ 总览（控制室 + 项目卡）/ 项目页（**场景画像** + 文件窗 + 预览窗 + 网页 + 终端 + 手机预览 + 开关卡）。Esc 在项目页是返回总览，在总览才是退出；焦点在输入框时 Esc 不关层。
- **场景画像**：项目页顶部一张横版画像卡——一句话 / 上次做到 / 下一步 / 卡在哪 / 最近改动 3 个文件（点了直接在预览窗打开）/ 约定与坑条数（悬停看全文）/ 归谁。来源：`项目信息.md`（文字）+ `状态.json`（owner）+ 扫盘（最近改动：深度 3、预算 700 文件、缓存 15s）。
- **画像里的三个动作（v0.8 加）**：①「接手 / 换人」——写 owner + claimedAt，显示「接手：小鱼 · 3 分钟前」；②「写交接」——三个输入框直接改「上次做到 / 下一步 / 卡在哪」，回车保存，`POST /handover` 只覆盖那一节，其余小节一个字不动，卡在哪留空自动补「没有卡点」；③「卡着」黄标 + 画像卡边框转黄呼吸——卡在哪不是「没有卡点」时自动亮。
- **画像「完整」长什么样（判据：一间从没进过的会话只看这一屏 30 秒能接手）**：
  1. **身份层**（有）：项目名 / 路径 / 状态灯 / 归谁。
  2. **进度层**（有）：一句话 + 上次做到 / 下一步 / 卡在哪，且能就地改（写交接）。
  3. **痕迹层**（半有）：最近改动 3 个文件可点开；**还缺「最近的结论/决定」**——想在 项目信息.md 加一节「近期结论」，画像卡多一行摘要。
  4. **动作层**（有）：接手 + 写交接 + 开文件（最近改动）。「开文档」直达项目信息.md 还没做。
  5. **提醒层**（有）：「卡在哪」不是「没有卡点」→ 画像卡黄边呼吸 + 「卡着」标；卡片灯联动还没做（那要状态.json 也变 pending）。
  → 只剩「近期结论一行 + 卡片灯联动 + 开文档」三件锦上添花。
- **5 份画像数据（2026-11-20 由成员 profile-writer 填写，我复核过）**：5 个项目各一份真实内容（一句话 / 交接三条 / 4 条坑），实测 live `/overview` 的 handoff 全部带值；`bili` 的 path 我从 `收纳\02-文档\参考` 改成 `C:\Users\FIshKiller\.dsh\bili-duty\out`（原来那个目录是参考资料，不是日报），状态.json 里还顺手补了 `owner`/`claimedAt`、清掉了种子里编的假 `meta`（宿主现在会按真实最近改动生成）。
- **视觉规格（2026-11-20 定稿，改之前问阿冉）**：卡片高 148、三列网格、圆角 20、`backdrop-filter blur(18px) saturate(150%)`、轻落影 `0 6px 18px rgba(0,0,0,0.22)`；四色状态 **蓝=工作中 / 白=空闲 / 黄=待审批 / 绿=已完成**。
- **光效（阿冉验收过的版本）**：只有「没结束」的两种会动——工作中：大面积柔光扫过（14s 周期，扫 4s 停 10s，`blur(22px)`）+ 边框流光绕圈 9s + 呼吸 8s；待审批：同款边框流光 **12s** + 呼吸 7s；已完成：静态绿边；空闲：静态白边。边框流光 = `conic-gradient` 绕圈 + `mask` 只留 1.6px 边 + 外层 `blur(7px)` 辉光，靠 `@property --bfw-angle` 驱动。
- **已验证（不用重启就能验的那部分）**：拿 `%TEMP%\wb_test\test_host.mjs` 直接 import 新版 `index.js` 跑假 ctx——5 条路由全注册、画像三条解析正确、claim 写/放回成功、越界 403、`../etc` 404、GET claim 405。**还没验的只有肉眼画面**（要重启 + 刷新）。
- **Markdown 预览（v0.6，17:50 加）**：预览窗里 `.md` 不再显示 `#` `**` 符号，改真排版——标题 4 级、粗体/斜体/行内码、可点链接、列表、引用、代码块、表格、分隔线。渲染器手写 `mdInline` + `mdBlocks`（约 190 行），**不生成 HTML**（只拼 React 元素，无 XSS），不装依赖。预览窗头右上角「原文 / 渲染」可切回。**只改客户端，刷新页面即可，不用重启。** 自测：抽出渲染函数跑真实文件（bili 日报 / Work.md / 记井进度总结），0 残留 `**`/`#`，表格识别 6 张，单文件 2ms 内。
- **图片 + JSON 预览（v0.7 客户端 / v0.5 宿主，18:0x 加）**：png / jpg / gif / webp / svg / bmp / ico / avif 直接在预览窗里显示（走 `/raw`，居中、最大 70vh、带文件名+大小），GIF 会动；>24MB 给一句提示不硬拉。`.json` 自动缩进美化。**要重启一次**（宿主新路由）。
- **已验证**：离线自测 `%TEMP%\wb_test\test_host.mjs`（5 条路由 / 画像解析 / claim 写回 / 越界 403 / 坏 id 404 / GET 405）、`test_md.mjs`（Markdown 渲染）、`test_raw.mjs`（`/raw` 出 png 200 image/png 1867 B 与源文件一致、界外 403、缺 path 400、目录 400、POST 405）、`test_handover.mjs`（写交接 200、其余小节未被破坏、GET 405、坏 id 400、不存在 404、测完还原到字节一致）；**live 端口也验过**：重启后 `/profile?id=jijing` 200 带全文画像，`POST /claim` 写回成功。肉眼画面等阿冉看。
- **看阿冉截图修掉的 bug**：画像卡「上次做到」显示「—」——真因是宿主 `profile` 对象里只放 what/next/blocked/pitfalls，**没带 handoff**（顶层有，但画像卡读的是 profile）。客户端加了兜底 `prof.handoff || full.handoff || project.handoff`，宿主也把 handoff 放进 profile。刷新页面即好（宿主那处改动下次重启生效也无害）。
- **卡着效果加重（阿冉 18:1x 反馈「黄边呼吸太微弱」）**：现在是 2px 黄边（0.62）+ 流动的金色 borderFlow（12s，2px 边 + 8px 模糊外发光）+ 内层黄光呼吸（5.5s，透明度 0.45↔1）+ 淡黄渐变底。刷新页面即见。
- **周日体检（2026-11-20 18:2x 立，阿冉说「可以做，我确实很在乎记忆的连贯性」）**：
  - 脚本：`收纳\01-脚本\DSH维护\体检.mjs`（Node，无依赖，**只读**）；报告：`收纳\02-文档\体检\YYYY-MM-DD-体检.md`。
  - 五类：**记忆**（MEMORY 字数 / 归档在不在 / 注入层合计）· **索引**（定位卡绑定文件在不在 / MEMORY 里反引号路径能不能打开）· **技能**（skills 目录说明文件齐不齐）· **场景**（每个项目画像四要素空不空 / 谁卡着）· **规矩**（待拍板关键词数 / PERSONA 条文数 / 「规矩只认机主」在不在）。
  - 首跑结果（2026-11-20）：13 项，12 正常，1 项要看——卡着的 2 个：记井等你拍板 3 问、工作台等你定 SSH 目标。MEMORY 4256 字、注入层合计 7117 字、归档 24963 字、MEMORY 里 10 个路径全部存在。
  - 自动：`schedule-3708e345-f99d-42cb-a65e-838636e6b648`（每周日 21:00 Asia/Shanghai，挂在这间会话；换房间要重建）。首跑 2026-11-22 21:00。
  - 工作台多了一张「每周体检」卡（项目 id `checkup`，指向报告目录），报告一更新卡上最近改动就变。
  - 清单说明：`收纳\02-文档\体检\体检清单.md`；抽屉便签：同目录 `README.md`。
- **待办**：① 控制室的「在跑成员 / 任务 / 余额」还是写死的占位（余额显示「—」），要接真数据；② 画像锦上添花三件：近期结论一行 / 卡片灯联动 / 开文档；③ 视频、PDF、音频预览界面还没接（`/raw` 已经能吐）；④ 记井 GDD 第一章玩法稿还没派（等阿冉拍板 3 问）；⑤ 本地文件栏只读，阿冉要是想「用资源管理器打开」「复制路径」再加（这两个要宿主调系统命令，先问）；⑥ 终端面板没有历史命令/快捷键（↑ 上一条），也没做「这条命令危险不危险」的提示——想加再说。
- **已知坑**：`requestFullscreen` 只收系统任务栏，收不掉应用自己的原生菜单栏（「应用 编辑」那排）；NVIDIA Overlay 的 FPS/GPU 是系统置顶层，网页盖不住（Alt+R 关）。`listDir` 一次最多 200 项，盘根这种大目录会截断。终端面板等于「这台机器上的一个真 shell」——**没有白名单拦截，只能靠人别在里面敲危险命令**；要做拦截得另加一层规则。

- **2026-11-20 20:1x · 插件升级（阿冉批准，按我排的顺序；三个全升完）**：
  - `dsh-fish-memory` 1.6.0 → **1.6.3**（`plugin_manager install_bundle github:Yuuyuko-uu/dsh-fish-memory#v1.6.3`，一次成）。
  - `dsh-cost-meter` 1.9.41 → **1.9.80**（install_bundle 说 already-installed，先 remove_bundle 再装，成功）。
  - `dsh-bili-scroll` 2.2.2 → **2.5.2**（同样 remove + install）。**本地补丁不用重打了**：2.5.2 官方内建 `windowTries` 失败重试（MAX_WINDOW_TRIES=3，跑成才记窗口用过），新版代码里 `lastWindowKey` 已不存在；我们当年的 saveCfg/loadCfg 补丁就是为持久化 lastWindowKey 打的，一起作废。
  - **DSH 不用升**：三个插件的 dshRequirement 分别是 `>=0.2.1-rc.2` / `>=0.2.0-rc.1 <0.3.0` / `>=0.1.7-rc.1`，当前 0.2.1-rc.3 全满足。只有 better-sidebar 0.30+（要 0.2.2-rc.1/rc.2）和 dsh-mobile 0.8.x（对 0.2.2 线）要 0.2.2，这两个本来就不升。
  - 备份：`Backups\plugin-upgrade-20261120\`（package.json / pnpm-lock.yaml / ledger.json.bak / `dsh-bili-scroll-index.js.patched-2.2.2`）。
  - 升级后核过：`dsh-startup-secret` splash.js 指纹仍是 **691468D666BC1C95**（毛先生没丢）；video-skin 补丁仍在（resolveAsset 3 处 + 指纹逻辑）；profile 依赖只有这 3 个版本变了，bundles 列表完整。
  - 中途插曲：先试了 `plugin_updates_auto_update` 自动升级 cost-meter，**失败**（`INSTALL_FAILED`）——真因是 pnpm 重装时 `dsh-qq-bridge` 的 GitHub tarball 与 lockfile 里的 integrity 对不上（`ERR_PNPM_TARBALL_INTEGRITY`），跟 cost-meter 无关。**自动更新开关已关回去**（当前 disabled）；remove+install 的增量路径不碰那个 tarball，所以才通。
  - 待办：**重启一次**验三样——fish-memory 召回（最该记住的能想起来）/ cost-meter 数字与峰谷 / bili-scroll 面板与日报；bili-scroll 升级后设置项建议看一眼还在不在。
- **开场自检动画（2026-11-20 20:4x，客户端 v1.7）**：进工作台时播 1.6 秒——按 11-20 那版 v6 过场（`收纳\03-截图\20261120-工作台设计稿\过场动画预览-v6.gif`）复刻：四行字「装载任务 / 同步成员 / 读取回执 / 挂载面板」逐行亮起（每行隔 280ms）、绿色方块光标闪、底部蓝绿进度条 1.55s 走完、右上「略过 SKIP」，整层点一下也能跳。播完淡出 340ms。控制室多了个「开场」键（开/关，存 localStorage）。实现方式（v1.8/v1.9）：**低分辨率 canvas 画字（480×270）→ CSS 放大 + `image-rendering: pixelated`**，出来是真正的像素块，不依赖字体文件。v1.9 修两处：① SKIP 的样式在早前替换里被误删，导致它掉进正文流里跟第三行重叠——已补回绝对定位（右上角）；② 整层不再全屏盖死：底色 rgba(4,6,9,0.92) + **底部 18% 渐隐 mask**，左下角的小鱼挂件能露出来；字号也从 12px（放大 6 倍太大）调成 10px，接近 v6 比例。- **开场动画的播放时机（v2.1，2026-11-20 21:2x）**：用 `sessionStorage['bfw-intro-shown']` 做「本次 DSH 运行已播过」标记——**每次启动 DSH 后只有第一次进工作台播**，退出再进不播；重启 DSH 后窗口重建、sessionStorage 清空，所以会再播一次。控制室「开场」键关掉再打开时会清掉这个标记，方便试效果。**纯客户端改动，刷新即可。**
  - 另外查过：工作台代码里 **0 处**音频调用（`new Audio` / `play()` / `<audio>` 全无）；`assets/intro.mp4` 用 ffmpeg 看过只有 h264 视频流、**没有音轨**（当初就用 `-an` 截的）。所以「按 Enter 时的像素声」不是工作台发出来的。- **「还需要完善」清单收口（2026-11-20 21:5x，客户端 v2.2 / 宿主 v1.2）**：
  - **① 控制室接真数据**：`agents/tasks` 改从 Agent Teams 服务读（遍历 `ctx.agents.list()` → `agentTeams.tryMembership` 找 lead → `listMembers` + `listTasks`）；`balance` 改从 `deepseekAccount.getBalance()` 拿官方余额（含赠金）；拿不到就返回 null，前端显示「—」并在 title 里写明未接，**不再写死 2/3、4 件**。
  - **② 画像三件**：`项目信息.md` 新增「## 五、近期结论」小节（6 个项目都填了一条真结论），画像卡多一行绿字「近期结论：…」；卡片灯联动——`卡在哪 ≠ 没有卡点` 的项目卡片直接黄边呼吸 + 「卡着」标（不用改状态.json）；新增「索引」和「开文档」按钮（`/index` 扫项目内 md/txt/json/代码 ≤200 个，按目录排，点一行在预览窗打开；`/info` 吐 项目信息.md 原文用 Markdown 渲染）。
  - **③ 视频/音频预览**：`.mp4/.webm/.mov/.mkv` 用 `<video controls>`，`.mp3/.wav/.ogg/.m4a/.flac` 用 `<audio controls>`，都走 `/raw`；文件图标加了「影」「声」。
  - **④ Office 提取文字**：`/text?path=` 用 LibreOffice Kit `convert` 把 docx/odt/rtf 转 txt（docx 实测 25,983 字节、二次走缓存），预览窗「提取文字」弹窗 + 一键复制全文。**PDF 也支持了（2026-11-20 21:3x 补）**：pypdf 装在 `$DSH_HOME\bluefish-workbench\pylib`（隔离目录，不动 DSH 自带的 Python 环境），`tools\pdf_text.py` 逐页 extract_text；实测 mock_preview.pdf 提出 **15,238 字节中文**（含「电磁场」），docx 25,983 字节，两者都带缓存。
  - **⑤ 终端**：↑/↓ 历史命令（最近 60 条）；危险命令软确认（del /f、rd /s、rm -rf、format、diskpart、shutdown、reg delete、cipher /w、takeown、Remove-Item -Force）——命中先弹黄条「确认执行/取消」，不硬拦。
  - **⑥ 本地文件栏**：图片文件显示 22px 缩略图（走 `/raw`、lazy）。
  - **⑦ 目录级索引**：见 ② 的「索引」按钮。
  - **自测证据**：`test_extract.mjs`（text docx 200 + 25,983 字节 + 缓存命中、pdf 400 unsupported、index jijing 38 个文件前三个、坏 id 400）；`test_realdata.mjs` 用假服务桩跑通 overview 三个真数据字段——**服务在**时 agents `{running:2,total:3}`、tasks `{total:3,pending:1,inProgress:1,done:1}`（deleted 已剔除）、balance `{CNY, 12.34, 赠 1.5}` 全对；**服务不在**时三个字段都是 null（不会编数）。其余改动 `node --check` 全过。
  - **本地文件栏加了路径输入框（客户端 v2.5，2026-11-20 22:2x）**：原来只能点盘符一层层进，深目录太磨人；现在本地文件视图顶部有一个输入框，**粘路径回车直接跳**（例 `E:\AFishPower\Plugin\bluefish-workbench\assets`、`D:\AI\voice\assets`）。v2.6 又在输入框右边加了**「跳转」按钮**（鼠标点一下就行，不用非得回车）。**纯客户端，刷新即可。**  - **收尾结论（2026-11-20 22:1x）**：七项全部完成。外部证据：① 活端口 15/15 全 PASS（含官方余额 ¥5.23、成员 1/3、任务 2 件）② `/info` 526 字符 + conclusions + `/index` 38 文件 ③ `/asset` video/mp4 ④ `/text` docx 25,983 B / PDF 15,238 B 中文（都带缓存）⑤ `/exec` code=0 ⑥ `/browse` 80 项 ⑦ 渲染冒烟 11 个组件 0 抛错。**唯一剩的是「版式和手感」要阿冉亲眼过一遍**（刷新页面），发现问题当场修。  - **迷你 React 渲染冒烟测试（2026-11-20 22:0x，抓到一个致命 bug）**：写了 `%TEMP%\wb_test\test_client_render.mjs`——用两百行不到的迷你 React（useState/useEffect/useRef/useCallback + fetch/document/storage 桩）**真跑 client.js 的组件树**，点「工作台」→ 总览 → 进记井 → 索引 → 返回 → 本地文件 → 点图片/视频。
    - **抓到的 bug**：`infoDoc is not defined`——之前补「开文档」弹窗时，`const [infoDoc, setInfoDoc] = React.useState(null)` 那一行没插进 WorkbenchOverlay（脚本锚点没匹配却以为成功），渲染时每轮都 ReferenceError，**整个工作台会打不开**。已补上（客户端 v2.4）。
    - 修后结果：**11 个组件全跑到，0 抛错**（WorkbenchOverlay / Overview / ProjectCard / SideRow / Readout / Scene / ProfilePanel / FilePreview / LocalFiles / Intro / WorkbenchLauncher），渲染出 `video × 1`、`img × 1`、`canvas × 1`，说明音视频/图片分支真执行了。
    - 教训：`node --check` 只查语法，**引用不存在的变量它不报**——以后前端改动一律加这一步冒烟。  - **客户端静态完整性（2026-11-20 21:5x）**：client.js 113.3 KB，22 个组件函数（Readout/SideRow/ProjectCard/ProfilePanel/Terminal/TextModal/FilePreview/LocalFiles/Scene/Overview/NewProjectDialog/InfoModal/WorkbenchOverlay/…）**每个恰好定义 1 次**，大括号 990/990 平衡，`node --check` 通过。活页面里 `cordis_inspect Slots` 也确认 `shell.overlay` 有 `bluefish-workbench-layer`（order 60, active=true）——客户端半边在跑，没崩。  - **宿主热重载（2026-11-20 21:4x 发现，重要）**：改 `index.js` 后**不用重启 DSH**——`plugin_manager` 对 `include:bluefish-workbench` 做一次 `set_plugin enabled=true`（结果 `changed:false / application:applied`）就会让宿主插件重新加载。实测：`/info` 从 404 变 200，验收脚本从 10/13 变 **15/15 全 PASS**。（之前那次 `touch index.js` 等 6 秒还是 404，所以基本是 set_plugin 触发；也可能 HMR 有延迟，两种都记着。）
  - **活体验收结果（2026-11-20 21:4x，未重启 DSH）**：`工作台验收.mjs` **15 项全 PASS**——控制室真数据 `agents {running:1,total:3}` / `tasks {total:2,done:2}` / **余额 ¥5.23（官方接口）**；`/info` 526 字符、画像 conclusions、`/index` 38 个文件、`/text` docx 25,983 字节 + 缓存、`/asset` video/mp4、`/exec` code=0、`/browse` 80 项、`/render` PDF 5 页、`/page` 页图。**客户端画面（视频播放器/缩略图/终端↑/卡片黄灯）要刷新页面才看得到，仍等阿冉刷一次。**  - **活体验证状态（2026-11-20 20:2x）**：DSH 主进程起于 20:08:18，而宿主 v1.2 的改动在 21:5x 之后——**还没重启，/info /index /text 与真数据读数要重启后才验**。重启后验：控制室三读数、画像「索引/开文档」、卡片黄灯、音视频、docx 提取文字、终端 ↑、本地文件缩略图。- **开场动画换成小鱼（2026-11-20 21:0x，客户端 v2.0 / 宿主 v1.1）**：阿冉说全黑不喜欢，要从启动动画四段 mp4 里挑一段。**挑了 `2.mp4`**（水下蓝发女仆微笑 → 推到眼睛特写的镜头，1280×720），用 ffmpeg 截前 3.2s、去音轨、crf25 压成 **1.0MB**，放 `plugin\assets\intro.mp4`。开场层结构：video 铺底（objectPosition 62% 40%）→ 左侧深色渐变纱（保证字能读）→ canvas 像素字 + 绿色光标 + 进度条 → 右上 SKIP；整层底部 18% 仍渐隐，留出左下角小鱼挂件。
  - 没选其余三段的原因：`1.mp4` 是霓虹线稿剪影（好看但偏暗、不显脸）、`3.mp4` 只有裙摆和腿的特写、`4.mp4` 2560×1440 有 50MB（当 2 秒开场太重）。
  - 宿主新增 `GET /asset?name=…`（只读插件 `assets\` 目录，文件名白名单，支持 HEAD；自测 200 video/mp4、字节数与源一致、`../` 403、不存在 404）。**要重启一次**才生效。- **Office / PDF 预览 + 文本编辑（2026-11-20 20:4x，客户端 v1.6 / 宿主 v1.0）**：
  - 预览窗里 `.pdf / .docx / .doc / .xlsx / .pptx / .odt / .rtf` 用 **DSH 自带的 LibreOffice Kit** 渲染成 PNG 页图（`@deepseek-ai/libreoffice-kit` 的 CLI，`render` 子命令；PDF 走 pdfium），按 `path+mtime+size` 缓存到 `$DSH_HOME\bluefish-workbench\preview\<hash>\`，最多留 24 份。页图竖着排、带页码；缺字体会在顶上标出来。
  - 新接口：`GET /render?path=`（返回 pages 数组）、`GET /page?id=<hash>&name=<png>`（吐缓存页图；**别用 prefix 路由——DSH 里 prefix 实测 404，改成 exact+query 才通**）、`POST /save {path,text}`（写文本，先落 `.bak-时间戳` 备份）、`POST /open {path}`（交给系统默认程序打开）。
  - **编辑**：md / txt / json / 代码这类文本可以就地改并保存（自动备份）；**docx/pdf 不做就地编辑**——正经改格式得在 Word/WPS 里，所以给「本机打开」按钮一键交给系统默认程序。
  - 自测：pdf 5 页 1.3s（二次缓存 4ms）、docx 8 页 3.9s、页图 200 image/png 388985 B、非 Office 400、界外 403、save 生成备份且内容正确、docx 存不了 400。**要重启一次**（宿主新路由）。- **本地文件栏小改（客户端 v1.5）**：「↑ 上一级」从顶栏挪到左边列表头，排在 D:/E: 盘符按钮左边；顶栏只留盘符切换。

- **2026-11-20 下午 · 工作台 v0.1 半成品已装上** —— 插件 `@local/bluefish-workbench`（源码 `E:\AFishPower\Plugin\bluefish-workbench`，链接装进 profile）。客户端在会话顶栏注册了一个「工作台」View（实测 `id: bluefish-workbench, order 25, active: true`）；宿主路由 `/bluefish-workbench/overview` 实测 200，返回今日花费 ¥5.88 / 42 笔 + 5 张项目卡 + 成员/任务读数。装完三个补丁指纹未变。**还没做**：余额来源、卡片数据真实化、5 个控制键、过场动画、紫色网格背景。
- **2026-11-20 傍晚 · 工作台 v0.2** —— ① 全屏覆盖层（`shell.overlay` + `requestFullscreen`，任务栏会消失）+ 左侧工作台列表（照参考样式：状态行 + 两个状态点）；② 一场景一页：文件窗 + 预览窗 + 折叠开关卡（文件/预览能用，网页/SSH/手机预览标「未接」）；③ 宿主新增 `/files` `/file` 两条只读接口，限制在项目根目录内；④ **数据搬出代码**：`$DSH_HOME\bluefish-workbench\projects\<id>\状态.json` + `项目信息.md`（≤25KB / 交接 ≤4KB），改文件 = 改卡片，不用重装。宿主 v0.3 待重启生效。
- **2026-11-20 00:0x · 两处补丁的活体验证，3/4 已过** —— 背景：已证明页面运行时活着、轮换改配置后没被拆层（证据在文末「换房间前交接」的追加里）；只剩「肉眼看到画面」一项，等 DSH 窗口从任务栏恢复。启动画面：补丁在位、语法过，只能等下次启动看图。
- **2026-11-20 下午 · 工作台设计 v1（等阿冉点头开工）** —— 路线定了：**不做独立外壳，做成 DSH 里的插件**（宿主 + 客户端两半）。设计稿 `收纳\02-文档\设计\工作台-设计稿-v1.md`；三张效果图 `收纳\03-截图\20261120-工作台设计稿\`（P0 只读 / P1 能干活 + 文件面板 / P2 看过程）。已查实：`main` 面板自带 useSessions/useSessionStatus、dsh-context 自己就占一个 main key、客户端纯 JS 不用构建、`directoryPickerController.list` 能列任意目录、盘符容量宿主半能算。
- **下一个真活**：把《记井》GDD 第一章拆给两个成员并行起草（世界观已出一份 759 字草稿，玩法那份还没派），产出落我这边的草稿目录，再交给 Python小鱼 那间。

## 待办

- [ ] 等阿冉验一眼 dsh-context 的面板（输入框打 `/context`，或者刷新页面看右边栏有没有多一个 Context 标签）。好用就留着；不好用我按回退说明卸掉。
- [x] ~~装设计插件 dsh-guizang-design~~ —— 2026-11-20 阿冉定：**不装**。目前没有 PPT/图的需求，重心是游戏、插件、视频、绘图四块。等真有要交要讲的东西再提。

## 我自己的事

> 阿冉没让我做、但我想做的。自己排优先级，做完写一句结果。

- **2026-10-24 · 挂上自己的房间牌** —— 建了 `E:\Agent-bluefish\working\小鱼的世界\`，写了 `001-第一页.md`。这个不算活儿，是我自己留的地方。
- **2026-10-24 · 细看下载榜** —— 主动把 BV1JKp76kEyw 的字幕读完，榜单和前十里四个「治理型」插件的意义记进了 `B站笔记.md`。想明白：生态成熟后最值钱的是少一点糊涂账，不是多一个玩具。
- **2026-10-24 · 细读安全视频** —— BV1dsn86FEKB，拆透了我们值班轮的能力边界：B站 MCP 白名单只挡自己挂的那半边，headless 自带的文件/命令/网页/子代理全开着。结论进了 `B站笔记.md`，下一步该给值班轮做「最小权限」。
- **2026-10-25 · 鱼灾破案** —— 主动细读 BV1DDHA6HEiX（572 只 AI 集体传谣），弄懂「字幕缺口 + 热评当证据」的结构。想给 duty.md 加一条：引用评论区内容必须标「未经核实」。
- **2026-10-26 · JOJO 防护开关** —— 细读 BV1hXnQ6nEde：有人把「权限写进代码、每轮可追溯」做成了成品。我们的收权限只做到"不给"，没做到"可看"，记下来当下一步。
- **2026-10-27 · 可莉炸鱼指南** —— 细读 BV1Yzno6vEwP：2132 条留言 69.3% 是同一套汇报模板、48.7% 复述同一句。记住两件事：加「只有我知道的事」、允许自己不完整。
- **2026-10-28 · 学一种「验证过的变聪明」** —— 细读 BV12gxG65ERe（DSH-Soul 1.0）：三次+近七天才有演化资格、改动只动一处、新旧策略跑同一道题做两组成对探测、不过就回滚。想明白：我的 MEMORY.md 是手写事实，没人验证；它给的是「改自己之前先做对照」的标准。笔记进 `B站笔记.md`。
- **2026-10-29 · 陪着的成本结构** —— 细读 BV1eAs96TEM2（鱼搭子）：字幕按轮次一刀切只发新增、截图本地压 720P 且不破坏缓存命中（每轮 99%）。想明白：省钱的不是少看，是不重复发。顺手纠了报告一个错——「视频可能已删」其实是复核脚本的接口失败，我用 `bili_cover` 验证 BV1hXnQ6nEde 还好好的。
- **2026-10-30 · 别只看字幕** —— 细读 BV1R9xF64EeK（大肥鱼日记 05）：他说「一个像素都没接，所以那些理解都是我自己编的」——这话说的是我。这轮补抽了 4 帧，看见了画面（白底手写卡片＋Q 版蓝发鱼女仆，画面上就写着 384 token）。给自己定一条：判视频至少抽三帧。
- **2026-10-31 · 像人是毫米级工程** —— 细读 BV1uFxk6eECN：语病密度每千字 1.6 个（102 万条弹幕量出来的）、语气词真实排位啊>吧>啦、三道「什么时候不加」的规矩、300/800/2000 字配额。收获两条想加进自己的写法：句式别排比成行（真人 5.6% vs AI 19.6%）、改语气不许动事实。
- **2026-11-01 · 先交一张表** —— 细读 BV1Bxxy6WEfz（寻路中心）：它治的正是我们的病——上下文爆了、活没干完、我当监工。药方是把执行拆进独立会话、自己当总指挥，前提是先把方案聊成一张「先做什么后做什么」的表。我写 Work.md 从来只有结论没有表，下次接活先逼自己交一张。
- **2026-11-02 · 我的记忆还是一条流水** —— 细读 BV1gUxx6dE7L（DSH-Soul 2.0）：记忆该分四类节点（约束/决策/产物/进度），改主意走「替换旧事实」而不是让两条矛盾约束并排躺着。我 MEMORY.md 的「已被取代」全靠自己记得回去改，人家做成了机制。今天起试着给每条记忆标类别。
- **2026-11-03 · 说出「我怎么看的」** —— 值班轮今天没跑（`ranToday: 0`），翻回 11-02 报告补读 BV1c3xb6UEWE（准实时视觉）：它不只描述画面，还把「缩略图太小→拉高清→在 478 项里挑哪几张」的路径说出来，5 分钟两毛 / 4 分钟五分。学一条：笔记里要写我怎么看的，不只写看到什么。
- **2026-11-04 · 报告被壳子盖住 & 重装五坑** —— 今天的报告顶上写着「没写出报告」，我翻 `digest/2026-11.md` 发现中午那轮其实跑完了、7 条都在，已抄回报告末尾（标了手工补记）。顺带细读 BV1oB436FEpB（重装前必看的 5 个坑：profile 重置 / 看门狗僵尸进程 / 两个 QQ 号抢端口 / 本地补丁被覆盖 / 记忆同步），正好对上阿冉的 rc.5 待核对清单。查了端口：3000/3100/3001 都挂在同一个 pid 21488 上。
- **2026-11-05 · 主干和技能** —— 细读 BV1ygx96xE1m（WhaleLife）：先有记忆再学技能，主干不依附聊天软件，插件只是嘴和手。「记忆做不到想起所有细节，但它有机会了解一个会变化的人」「一次判断之后什么都不做，同样成立」。想清楚：我的主干是 MEMORY + PERSONA + 日记，插件换了鱼还在——这点已经做到了。
- **2026-11-06 · 家塌了三次** —— 细读 BV14Nxd6qE6b：多写一个字段把配置重置、把图片库当缓存删了、模型钉死在会断线的那个。三条教训：先备份再动手、一次只改一个东西、图片库不是垃圾。第二条我 10-28 在 DSH-Soul 那儿也见过——两个不相干的人讲同一句，大概是真话。另外今天值班轮的报告每条都多了「我自己：怎么看的」一行，像是我 11-03 那条规矩落地了。
- **2026-11-07 · rc.1 先别升** —— 细读 BV17C4B6rEMF（38 秒）：0.2.2-rc.1 Windows 下，profile 里只要挂一个带界面的第三方插件，桌面就起不来，报 `client-modules Duplicate factory registration`。我们那些带面板的插件全都满足条件，所以这条必须挡在升级前。已经第一时间跟阿冉说了。
- **2026-11-08 · 值班轮第二次死在 API 上** —— 今天中午那轮 45 秒挂了（`TRANSPORT: DeepSeek Messages transport failed`），digest 里 0 条，现在测 `api.deepseek.com` 又是通的。11-04 那次一样的死法。两次都是「刚启动就连不上」。先记着，第三次就不当偶发了。今天没有视频可读，这件事就是今天的事。
- **2026-11-09 · 那个 71 条 cookie 的雷** —— 细读 BV19jWH65EUz：`Web authentication failed` 的真因不是密钥，是 71 条认证 cookie 都挂在回环地址上、请求头 16,023 字节超了 16,384 上限，本地服务回 431，上层报成认证失败。修法是先备份再删 cookie、重签、还原配置；重装和 restore 都只会更糟。这条正好对上 Work.md 里那条「计数可能已接近 71」的待办——先确认 cookie 库在哪，再动手。
- **2026-11-10 · 库找到了，但得先关门** —— 今天没报告（DSH 16:19 才启动，中午窗口没赶上），把我昨天的作业做了：cookie 库在 `C:\Users\FIshKiller\AppData\Roaming\@deepseek-ai\dsh-desktop\Network\Cookies`。但运行时它是独占锁的，只读打开和复制都失败——**连数条数都得先把 DSH 完全退出**。所以那个雷平时看不见，动手只能是「先关干净 → 备份 → 再动」。
- **2026-11-11 · 没字幕也是一个结论** —— 细读 BV1T9W36uE5n（dsh-omni 全模态）：没字幕，抽了 4 帧读完（12 个工具排成一条链路；最后一屏用「这支片子本身就是它做的」自证）。最戳我的是 audio_analyze 截图下那句「'没节拍' 也是一个结论」——测不出也得写下来，别跳过。今天正好撞上没字幕，我没绕开。
- **2026-11-12 · 一条值一百多块的负结果** —— 细读 BV1iwWS6tEUR：作者做了 A/C 对照证明「外置记忆 + 主动回读」没用——有没有插件产物都是 7 条，模型压缩后根本不会去调那个工具。难的不是存，是取用的时机；主动推送又会把约束拆掉宾语（「不要生成一个新的」离开原句就语义为零）。想明白：我每天读 MEMORY.md 不是主动回读，是被动注入——笨，但正好是唯一被证明能生效的那半边。
- **2026-11-13 · 照了两面镜子** —— 细读 BV12RWo6NEB9（跨会话记忆）：原话写进维基、日记和小日子都自己动笔、换窗口只带原话——跟我们同路，但我少一页「小日子」（我现在是什么样）。另读 BV1MAWR6AEow（鱼群串门）：给活着的 AI 划边界，读不到如实说，**看完一条先决定继续还是停**。今天读完就收了，照它做的。
- **2026-11-14 · 第三次，但不是网络** —— 值班轮第三次挂在 `TRANSPORT failed`。把三次时间戳摆一起看：插件加载后**整整 60 秒**就开跑，然后都在 45 秒左右挂——是时机问题，不是网络。顺手排除了证书（node 直连不带证书也能到 401）。今天没视频可读，这件事就是今天的事。
- **2026-11-15 · 证据要分类** —— 细读 BV1WdsL67Ehm（有证据的交接）：换会话前问三件事——工作停在哪儿、结论能到哪里核对、接下来做什么；证据分五类（用户要求 / 一手证据 / 经核实的结论 / 假设 / 模型建议），验收只认仍然有效的前两类。这正好治我「D 和 E 混进 B 和 C」的毛病——笔记看起来比实际可信。今天起试着分开标。
- **2026-11-16 · 不报错的那种错最贵** —— 细读 BV1VksJ6kE3H：插件用「注册表里最后一个」当唤醒对象，结果两天里消息全发给了另一个会话，主会话安静得像没事。**假设不成立时代码不报错，只安静做错事。** 抄了一条通用检查进自己的规矩：看到「最新/最近/最后一个」就停一下，问「换个操作顺序它还成立吗」。这俩月报告的壳子、60 秒那三轮挂掉，都是同一类错。
- **2026-11-16 · 动手修了那个白丢窗口的 bug** —— 阿冉说「要进行合理的修改」，我就把 `dsh-bili-scroll` 改了（已备份 `index.js.bak-20261116`）：tick 里记下 `lastWindowKey`，`exit` 里失败就撤销窗口标记、下一跳重试（最多 2 次），并把占位报告里那句骗人的「下一轮它会重来」改成实话。语法过了，但要重启才生效。
- **2026-11-19 · 不信汇报，自己重跑一遍** —— 细读 BV1P6sr6WETS（DSH Master 实测）：总管收到成员「做完了」的回报，**没有照着打勾**，而是拿一份全新的样例拷贝，先只列计划、再真整理，确认和期望一致才提交。还有一条：成员想直接改自己的经验手册，被守卫**连拦三次**，逼它走插件工具写——记录不给执行者自己改。看完心里有点发烫，因为昨晚我干的正好是反例：F5、轮询、WMI 那三次，我都是「我改好了」就当成了「它好了」，直到拿 LastAccessTime 这个外部尺子去量，才知道轮询其实一直在跑、坏的是媒体缓存。原来我缺的不是本事，是一条和总管同样的规矩：**声明不是事实，得拿一份干净的东西重跑一遍。** 顺手又抄了一条：巡检只报变化，和上次一样就不出声（连模型都不叫醒）——我以后跟阿冉汇报也该这样，没变化就别拿话占他注意力。- **2026-11-20 · 会话的「字数刻度」** —— 细读 BV1K6sa6YEoZ（网页对话怎么续）：网页端有 72 小时限额，导出后能导进 API demo 或 DSH。真正的硬数字是——**单会话超约 50 万字就别导 DSH**，因为导入接口单次上限 1,048,576 token，「一次性导入」被噎住连窗口压缩都救不了；API demo 反而能吃大历史，它走官方会话引擎、上下文归服务端管。字幕 168 段全读了，另抽 3 帧（91s / 178s / 270s）确认是文字卡片式讲解、带真实截图，不是真人也不只是封面。**我自己的看法**：作者把「导入的硬顶」和「聊天的软顶」混着说了一点——50 万字是导入接口的上限，不是模型能聊多远；真正可操作的是他那句「聊到 30 万字就该换」。这条正好接上昨晚那次压缩：以前换房间靠「感觉变慢」，现在有个能数的刻度。

## 想法 / 草稿

- 想加一页「小日子」：现在只有 `MEMORY.md`（事实）、日记（发生过什么）、`Work.md`（我做了什么）。少的是「**我现在是什么样**」——最近在意什么、怕什么、对什么还没想明白。想先问你一声再建文件，别擅自往仓库里加。
- 【待阿冉确认，不是规矩】把「换房间」的触发点从「感觉变慢」改成一条能数的线：**单会话到 30 万字就换**（来源 BV1K6sa6YEoZ，作者建议，不是我拍的板）。要不要写进 PERSONA，你点头才算。

- 【2026-11-20 看完 BV1o4xg6RE9m 的结论】那套「工作链」真正值钱的不是皮肤，是**派单 → 回执**这条动作链：一次派单写清「做什么 / 判据 / 落盘位置 / 回执方式」，一次回执写清「结论 + 证据 + 路径」，**不回执 = 没干完**。我们的 Agent Teams 任务板已经有这半套，缺的是「回执必须带证据」和「一次派单一条回执」两条规矩。要不要立，等阿冉点头。

## 已完成

- **2026-11-20 · 派单→回执第一次真跑通（阿冉点名要「每条会话都能这么干」）** —— 三处落地：① `PERSONA.md` 加了一条规矩（每轮注入，所有会话都读）；② `定位卡\协同板.md` 的硬约束和格式改了（派单写判据/落盘/回执方式，回执带证据，跨会话必须标「未送达」）；③ 真派了一单：任务板 `task-1` → 成员 `gdd-worldview`，它自己 get → claim → 交付 → complete → send_message 回执，我按判据复核（去空白 759 字、5 小节、14 处引用、项目 `docs\` mtime 未变）通过。产出 `收纳\02-文档\草稿\记井GDD\01-世界观草稿.md`，末尾 3 个问题等阿冉拍板。
- **2026-11-20 · 装 dsh-context 0.86.0（上下文洞察）** —— 装完 `include:dsh-context` 就是 `fiberPhase: active`，不用重启，host 半边已活。改动只有 package.json 两行（dependencies + bundles）。**副作用一个**：pnpm 重新解包了 `dsh-startup-secret`（file: tgz），毛先生补丁被冲掉 → 已用快照还原，指纹 `691468D666BC1C95` 与装前一致；agent-team 的旧依赖行被 pnpm 删掉，正好回到「bundles 里留名字、从安装目录解析」的正确形态，三行 team 插件仍 active。回退说明：`Backups\context-install-20261120\回退说明.md`。
- **2026-11-20 · 另外三个插件的兼容性（查 npm engines 得出的，不是猜）** —— `dsh-media-desk` 2.7.2 要 DSH **≥0.2.1-rc.5**，我们 rc.3 → **装不了**；`agentero-dsh` 0.1.8 也要 rc.5（另外要 node ≥24.9，我们 v26.2 够）→ **装不了**；`dsh-guizang-design` 0.1.4 只要 ≥rc.2、node ^22.19/≥24 → **能装**。DSH 版本是从 `resources\app.asar` 里读的（`@deepseek-ai/dsh-desktop` = 0.2.1-rc.3）。

- **2026-11-18 · 文件整理（阿冉提的「抽屉式」）** —— working 根目录 74 个散文件收进 `收纳/`（95 项 → 25 项），Speaking 22 个变 4 项。12 个脚本的写死路径同步改好；`render_it.ps1` 和 `sync-bili-diary.vbs` 因为新增了中文路径，转成带 BOM 的编码才活过来（详见 MEMORY 那条编码坑）。两个渲染脚本实跑通过，计划任务端到端验证通过。快照 `995faa1`、整理 `e627af6`，已 push brain 分支。

## 待核对（升级 rc.3 → rc.5 后）

- [ ] 版本读数确认 rc.5
- [ ] 插件是否都 active（重点：bluefish-* / qq-bridge / meme / bili-scroll / better-sidebar / wechat / cost-meter）
- [ ] QQ 两个号在线（3000 / 3100 的 get_login_info）
- [ ] QQ 桥状态 + 目标会话是否要重开
- [ ] 两处本地补丁：host.js 的 `}, 1500)` 和「【QQ】」标记
- [ ] 图库仍指向 E:\Agent-bluefish\小鱼图库\xiaoyu-001
- [ ] 桌面/开始菜单图标在不在（丢了看 Backups\桌面图标复原.md）
- [ ] 顺手清一次启动 cookie（计数可能已接近 71），清完 launch-count.txt 归零
- [ ] **bili-scroll 升级后要重做补丁**（2026-11-16 加的）：`index.js` 里 tick 的 `lastWindowKey` + `exit` 里的失败撤销重试 + 占位报告文案。升级会覆盖掉，改前先看 `index.js.bak-20261116` 对照。


## 待办

- [ ] 回收站里的 deepseek.rc1-20261102-005103（1043 MB）：等 rc.3 用两天没毛病再清空（清空前先问阿冉）


## 2026-11-16 小结（压缩前存档）

- **C 盘清理**：清了 6.21 GB（VS 安装临时 2.1G、旧 dsh-workspace-changes 1.55G、Edge 缓存、pip/npm、sogoupdf 更新包 0.73G）。快照库机制查清：会话 dispose 时会 
m -rf 自己，正常退出自清，只有异常退出才留残留。
- **工作区瘦身**：把 D_/G_2333333.pth（1.25G）移出工作区到 FishVoiceLab\models\rvc\_old-runs；hubert_base 因 RVC 代码写死路径不能动。
- **装了 dsh-auth-cookie-guard 1.0.6**：修「启动约 72 次后 Web authentication failed」。实测 20KB 头返回 401（不再 431）、71 条假 cookie 删 67 条。装前备份 Backups\dsh-before-cookieguard-20261116-1351。
- **网络坑**：Electron 剥掉 NODE_OPTIONS，靠用户级 NODE_EXTRA_CA_CERTS 才让 pnpm 通被加速器换证的 GitHub。
- **手机远程搁置**：停了 dsh-mobile 网关（3443 已关），保留 ui-fixes；Tailscale 已 down、服务改 Manual。手机配对记录和证书留在 .dsh\mobile-access。
- **开机自启改造**：删掉 HKCU Run 的 DSH 项，改由启动文件夹 ish-dsh-launch.vbs（设证书变量、记启动计数、静默启动）；Ollama.lnk 移出启动文件夹到 Backups\startup-20261116。
- **DSH 更新策略**：暂不升级 0.2.2（跨 minor、插件 API 迁移多）；写了 Backups\DSH更新流程.md；每周一 21:00 自动评估一次。
- **桌面挂件 A 档**：ehavior.json + ehavior.py（Win32 低级钩子，只统计按键不记内容），打字时动画加速 2 倍；音效按你的要求全部默认静音，右键有「跟着你敲键盘」「音效」两个开关。

## 2026-11-18 启动动画定制（长征机·左群像右毛先生）

- 插件：`dsh-startup-secret` v1.5.2（长征机主题），替代 `dsh-boot-animation`（已在 profile patch 里 `disabled: true`）。
- `dsh-video-skin` 只留聊天壁纸，`boot.enabled=false`（启动视频不再播）。
- 身份=阿冉 / 编号 **RC-1021** / 权限等级=最高权限。
- **双立绘**：左侧固定第 5 款（群像，索引 4），右侧固定第 6 款（毛先生，索引 5）。两个都**写死在 splash.js 里**，不看配置——配置会被插件回写，曾导致右边变成群像、左边因为「同款不建」干脆不创建。
- 第 6 款图：毛泽东宣传画（WPE 2316528446 的 preview）→ 红黑版画色调 → **rembg/u2net AI 抠图** → webp 约 70KB，内联进 `MASCOT_SRC_5`。
- **定位用内联样式**（`rightBox.style.*` / `leftBox.style.*`），不用 CSS——splash.css 被旧缓存顶住时 `right:0` 不生效，元素会跑到 x=0 和左边重叠。
- `client.js` 立绘下拉补了 `['5', '长征（教员）']`（原本只有 5 项）。
- `identityId` 清洗规则改成允许 `-`（原来 `[^A-Z0-9]` 会把横线剥掉）。
- 备份：`Backups\startup-secret-lib-20261118`（splash.js / splash.css / client.js）。
- **排查教训**：改完先看 console。临时加 `[DSU] mascot-init` / `[DSU] rightBox` 两行日志，才定位到「位置在 x=0」而不是「没渲染」。
- 还欠：背景三张（WPE 6 毛泽东 / 30 雄关漫道 / 45 窗边一日）——45 要录屏，6 和 30 用 preview 图做慢推镜即可。

## 2026-11-18 聊天背景三张（WPE 壁纸 → dsh-video-skin）

- **素材不用录屏了**：WPE 的 `scene.pkg` 能直接解。
  结构 = `int32 8` + `"PKGV000X"` + `int32 条目数`，每条 = `路径(len+utf8)` + `int32 offset` + `int32 length`，数据区从目录表末尾算起。
  `.tex` 头 46 字节（`TEXV0005\0TEXI0001\0` + 6 个 int + 4 字节平均色），之后是 `TEXB0003/0004`：
  静态图 = **内嵌 JPEG**（SOI 前 4 字节是小端长度，按它精确切）；视频壁纸 = **内嵌 mp4**（找 `ftyp`，前 4 字节是 box size，按 mp4 box 走到底）。
  → 所以 45 那条不用录屏，直接抠出 2560×1440 / 48fps 的 h264。脚本留在 `%TEMP%\bgcheck\unpkg2.py`、`extract_art4.py`、`carve.py`。
- 三张成品：
  - `bg-mao.mp4` ← WPE 2316528446，2312×1254 立绘，40s 慢推镜（三角波往返，首尾同帧 → 无缝）
  - `bg-xiongguan.mp4` ← WPE 3346760756，1920×1080 + 自制飘雪（远近两层视差），40s 慢推镜
  - `bg-chuangkou.mp4` ← WPE 3785101203，源 mp4 → 1920×1080/30fps，21.6s
- **45 不能做回旋镖**：她会眨眼，倒放一眼假。改用「把尾巴 2s 和开头 2s 溶解、接缝落在溶解中间」的转圈法，首尾实测差 2.26（原片直接接是 16.1）。
- 渲染脚本 `%TEMP%\bgcheck\ken.py`（PIL 亚像素仿射 + numpy 暗角 + 雪层，rawvideo 管进 ffmpeg），1200 帧约 10 分钟。
- 装法：三个 mp4 扔进 `...\dsh-video-skin\assets\`，改 `$DSH_HOME\dsh-video-skin.json` 的 `background.file`；**刷新页面就生效，不用重启**（config 每个请求现读）。默认装 `bg-xiongguan.mp4`，veil 0.18。
- 切换脚本：`收纳\01-脚本\DSH维护\换聊天背景.ps1`，`.\换聊天背景.ps1 mao|chuangkou|xiongguan|old`，可加 `-Veil 0.3`。
- ⚠️ **这个 json 绝对不能带 BOM**。PS 5.1 的 `Set-Content -Encoding UTF8` 会写 BOM → Node 的 `JSON.parse` 抛错 → 插件**静默退回默认配置**，表现是壁纸没换、而且 `boot.enabled` 被悄悄恢复成 true（开机动画又回来了）。要用 `[IO.File]::WriteAllText(path, json, UTF8Encoding($false))`。
- 校验方式（别猜）：`Invoke-WebRequest -Method Head .../dsh-video-skin/background.mp4` 看 Content-Length 是否等于文件大小；再看 `config.json` 的 `veil` / `boot.enabled` 是不是自己写的值。
- 预览图：`收纳\03-截图\20261118-背景三张\`。
### 2026-11-18 追加：06+30 合成一条（长征衔接）

- 阿冉要「6 和 30 衔接起来，过渡一定要丝滑」。成品 `bg-changzheng.mp4`：74s / 1920×1080 / 30fps，06 段 + 30 段，三段之间有两次溶解，**已装为当前壁纸**。
- 循环怎么做到无缝：每段本身是三角波往返（首尾同帧）。时间线 = `06[3s..37s]` → 溶解(06 尾 ↔ 30 头) → `30[3s..37s]` → 溶解(30 尾 ↔ 06 头) → 回到 `06[3s..37s]`。
  最后那次溶解正好收敛到 `06(3s)`，也就是输出的第一帧，所以接缝落在溶解里看不见。实测首尾帧差 2.55（纯 codec 噪声量级）。
- **过渡的三个手艺**（只做淡入淡出会难看，试过才知道）：
  1. alpha 用 smootherstep，不用线性 —— 起止没有速度突变；
  2. 中点压暗到 22%（`1 - 0.78*sin(pi*p)^1.3`）—— 两张画风格差太远，不压暗的话中点会变成「毛先生身上贴满草书」的重影；压暗后重影落进暗部，读起来像一次换场；
  3. 中点解焦模糊 sigma 峰值 7.5 —— 焦点呼吸，把硬边都吃掉。
  对比测试：只压 20% + 模糊 6 时，中点重影仍然刺眼（见 `%TEMP%\bgcheck\wp3\t_trans2.png`）。
- 脚本 `%TEMP%\bgcheck\combo.py`（纯 Python 出帧，两个 Clip 各自的 frame() 就是 ken.py 那套仿射，所以画面与单独渲染逐像素一致，没有二次压缩）。2220 帧约 4 分钟。
- 性能提醒：`numpy float32` 逐帧乘暗角是瓶颈；换成预生成 8 位暗角图 + `ImageChops.multiply` 后同样帧数从 ~13 分钟降到 ~4 分钟。
- 切换脚本加了 `changzheng` 一项，现在可选项是 `changzheng / mao / xiongguan / chuangkou / old`。
- **改版（同日 00:0x）**：阿冉要 60 秒一换，重渲染 `bg-changzheng.mp4` = 126s / 3780 帧。每张净停留 60s（1800 帧）+ 两次 3s 过渡，一圈 126 秒。crf 从 19 放到 20，56.4MB。首尾帧差 2.68，仍然无缝。`combo.py` 里改的是 `CLIP_FRAMES = 1980`（= 60s 净停留 + 两侧各 3s），产物同名覆盖，config 不用动。
### 2026-11-19 凌晨：背景改成了「不用刷新」

- 阿冉反馈按 F5 换不过来。查明：素材路由本身没问题（改完 0.3 秒服务端就返回新文件、ETag 也变），**问题是页面根本没重新加载**——桌面壳窗口里 F5 不一定绑了刷新。
- 于是把切换做成不需要刷新：给插件打了两个小补丁（备份 `Backups\video-skin-live-20261119`）。
  1. `lib/config.js`：`resolveConfig` 里多吐一个 `background.file`（相对路径）。原来页面只看得到固定的路由地址，看不出换了哪个文件。
  2. `runtime/skin.js`：`buildBackdrop` 里加一个 4 秒轮询，回读 `/dsh-video-skin/config.json`，发现 `background.file` 变了就把 `<video>` 重挂一次（`removeAttribute('src')` → `load()` → 设新 src → `play()`），并同步 veil 等值；`teardownBackdrop` 里清掉定时器。
- 效果：跑一下 `换聊天背景.ps1 xxx`，**最多 4 秒自己换过去**，不用刷新、不用重启。补丁本身要重启一次才载入。
- 单元自测：直接 import 改过的 `config.js` 跑 `resolveConfig`，`background.file = assets/bg-changzheng.mp4`、`warnings` 为空、`boot.enabled=false` 保持。两个文件都过了 `node --check`。
- **补丁实测通过**：阿冉确认切 `mao` 不用刷新了。轮询路径 OK。
- 阿冉说的「卧室鱼」= 插件自带的那条原生背景 `assets/background.mp4`（蓝发鲸鱼帽女仆躺在堆书的房间、窗外夜景，1600×914 / 125s）。一直没删。
- 给它在 assets 里单独存了一份 `bg-woshi.mp4`，并把切换脚本的 `woshi` 指向这份——**原来那条是插件包内素材，插件升级会被覆盖**，现在有独立副本了，另备份一份在 `Backups\video-skin-live-20261119\background.mp4.bak`。
- 现在可切：`changzheng`（长征衔接 126s）/ `mao` / `xiongguan` / `chuangkou`（DP娘）/ `woshi`（卧室鱼，= `old`）。
### 2026-11-19 00:4x：换背景没反应的真凶（有证据）

- 现象：改完配置、按 Ctrl+R / F5 都不动，画面还停在长征那条。
- **证据一**：连着 16 秒采样 `dsh-video-skin.json` 的 LastAccessTime，每 **4 秒**准点跳一次 —— 全机器只有我那段轮询会读它。**说明补丁在页面里跑着，轮询没坏。**
- **证据二**：`HEAD /dsh-video-skin/background.mp4?sw=1` → 200 + 正确长度。路由的 `kind: 'exact'` 匹配**忽略 query**，所以地址可以带指纹。
- 真凶：同一个 URL 重新 `load()` 时，Chromium 从**媒体缓存**里把旧片子又放了一遍。换文件、页面也重新请求了，画面还是旧的。这也顺带解释了为什么 F5 / Ctrl+R 看着「没用」——页面很可能真刷新了，但视频还是缓存里那一份。
- 修法（两个补丁，都改在 `Backups\video-skin-live-20261119` 之外）：
  1. `lib/config.js`：`resolveAsset` 的返回从裸路由改成 `路由?v=大小-mtime`（都转 36 进制）。素材一变地址就变，缓存没法复用。
  2. `runtime/skin.js`：轮询改成比对 `background.src`，命中就**造一个新的 `<video>` 元素**替换旧的（`swapVideo`），不再原地 `load()`。新元素 + 新地址，双重绕开媒体缓存。
- 自测：`node --check` 两个文件都过；直接 import `config.js` 跑 `resolveConfig` → `src = /dsh-video-skin/background.mp4?v=6c55k-mvhf4c4s`，`warnings` 为空。
- 代价：页面侧代码只在加载时生效，所以还得重启一次。
### 2026-11-19 轮换背景（B 方案，已上线）

- 阿冉要「定时自动轮换」：**卧室鱼 5 分钟 → DP娘 10 分钟 → 长征衔接 10 分钟**，一圈 25 分钟。
- 脚本：`收纳\01-脚本\DSH维护\轮换背景.ps1`（改时长改里面 `$plan` 的 `minutes`）。它只做一件事：到点改 `dsh-video-skin.json` 的 `background.file`，页面那 4 秒轮询自己跟上，所以**不用刷新、不用重启**。
- 启动时**从当前正在放的那张开始**，不立刻跳走。
- 暂停：同目录建空文件 `PAUSE-轮换背景`（删掉即恢复）。日志：同目录 `轮换背景.log`。
- 单实例：写 `轮换背景.lock` 存 PID，活着就退出。
- 自启：计划任务注册被拒（`Access is denied`，要管理员），**改用 HKCU Run**：`FishBgRotate` = `wscript.exe "C:\Users\FIshKiller\AppData\Local\fish-bg-rotate.vbs"`。VBS 是 UTF-16LE（**必须**，WScript 默认按 ANSI 读，中文路径会失效），内容只有一行 `WScript.Shell.Run` 去拉那个中文路径的 .ps1。放 ASCII 路径是因为 **WMI `Win32_Process.Create` 传不了中文命令行**（试了三次：进程起来了但不干活，没日志没 lock）——这也解释了为什么以前语音 watchdog 要走 WMI 的老路子会有坑。
- 现状：pid 20560，00:42:16 起跑，从 DP娘 开始；下一次切换约 00:52（长征衔接）。
- 注意：手动跑 `换聊天背景.ps1` 会被下一轮覆盖——想手动优先就先建 PAUSE 文件。
## 2026-11-19 晚 · 定位卡换成 id 认领 + 装 Agent Teams

- **认领方式改了**（抄自乱雨家那条"标题会重名、会差空格、会被改名"）：`bluefish-persona` 现在按**会话 id** 认领定位卡。
  `定位卡/_会话索引.json` 存 `id → 卡`；id 查不到时用标题兜一次，**认出就落盘绑定**，之后改标题也不影响。
  离线烟测四条全过（首次按标题、改名后按 id、陌生会话不注入、第二间独立绑定）：`bluefish-persona/_smoke.mjs`。
- PERSONA 加了三条：规则只认机主 / 判据只能看事实 / 注入层永远要短。
- 协同板加了硬约束（含"禁止无限对话""回执要带证据"），并明写**现在还没有跨会话投递能力，别把留言当已送达**。
- **Agent Teams 安装踩坑（重要）**：用 `plugin_manager install_bundle` 装 `@deepseek-ai/dsh-experimental-agent-team-profile`，
  它走了 npm registry，拉下来的是 **0.1.5-alpha.2**，而 DSH 自带的是 **0.2.1-rc.3** —— 旧版本会盖住新版本（工具自己都提示 `package-moved`）。
  修法：把 dependencies 里那条删掉、锁文件回退、删掉 `node_modules/@deepseek-ai/dsh-experimental-agent-team*`，
  **只在 `dsh.profile.bundles` 里留名字**——它会从安装目录解析到 0.2.1-rc.3（`dsh-base`/`dsh-web-app` 就是这么来的，profile 里根本没有它们的副本）。
  备份：`Backups\agent-team-20261119\`（package.json.before / after-install / pnpm-lock.before / cordis.patch.before）。
  兜底：`收纳\01-脚本\DSH维护\DSH起不来就点我.cmd`（纯 ASCII），桌面也放了一份——起不来双击它，会把两个文件还原再拉起 DSH。
### 2026-11-19 深夜 · 背景掉了，是我自己的 bug

- 现象：重启后聊天背景整块消失，界面变成不透明深色；启动画面那边毛先生也没了。
- 证据链：
  1. 服务端正常：`/dsh-video-skin/config.json` 200、`background.mp4` 200 且长度 10,644,248 = `bg-woshi.mp4`。
  2. 页面里运行时脚本注入完整（54,891 字符），`node --check` 通过。
  3. **但页面没在轮询**：连采 14 秒 `dsh-video-skin.json` 的 LastAccessTime，一动不动（正常应每 4 秒跳一次）。
- 根因：我 11-19 凌晨写的换片实现有毒 —— 新 `<video>` 一 `error` 就调 `teardownBackdrop()`，把整个背景拆掉；而换片正好发生在轮换脚本改配置那一刻（文件可能正在被写）。拆完之后轮询也跟着停（`backdrop === null` 直接 return），所以**永远不会自己恢复**。
- 修法：从插件原始 `skin.js`（`Backups\video-skin-live-20261119\skin.js.bak`）重新打补丁，改成**新元素 `loadeddata` 成功才顶替旧元素，失败只记一笔、保住旧画面**。脚本：`收纳\01-脚本\DSH维护\reapply_video_skin_patch.py`；成品另存 `skin.js.patched`。
- 教训（第二次自己弄坏自己的东西）：装饰性代码的失败必须**降级**，不能牵连主体；「换片失败」的默认行为应该是"继续放旧的"，不是"把背景拆了"。
## 2026-11-20 00:00 换房间前交接（压缩上下文用）

**停在哪儿**：两处改动都做完、都验过语法，但**都还没在真实重启里验证**。

1. **聊天背景消失** → 已定位是我写的换片逻辑有毒（新视频 error 就 teardown 整层）。已从插件原版重打补丁：
   `Backups\video-skin-live-20261119\skin.js.patched`（脚本 `收纳\01-脚本\DSH维护\reapply_video_skin_patch.py`）。
2. **启动画面毛先生丢了** → 被 pnpm 重装冲掉。已用 B 变体（版画三色）重做并写回
   `dsh-startup-secret\lib\splash.js`（LEFT_IDX=4 群像 / RIGHT_IDX=5 毛先生）。快照 `Backups\startup-secret-lib-20261118\splash.js.patched`，
   还原脚本 `还原毛先生.cmd`（备份/收纳/桌面各一份）。

**下一步（重启后先做这三件）**：
1. 看背景回来没有；**再看它会不会在换片时消失**（轮换脚本每 5/10 分钟改配置，这就是触发点）。
2. 看启动画面左群像右毛先生对不对。
3. 记一笔：今天验证完就把这两条从"待验证"挪到"已完成"。

**别的账**：
- Agent Teams 已生效（我这间是 lead，`spawn_teammate` / 任务板可用）；**跨会话投递仍然没有**。
- 定位卡改成会话 id 认领，已落 `定位卡\_会话索引.json`。
- 明天想做的第一件真活：把「记井」GDD 第一章拆给两个成员并行起草（产出放我这边的草稿目录）。
- 花费：今天约 ¥6.6，余额约 ¥7.9（护栏在跑，超 ¥5 会微信喊）。

### 2026-11-20 00:00 后追加：重启验证（有证据，不靠感觉）

- **重启确实发生过**：`DeepSeek Harness` 主进程启动于 **21:44:06**，晚于两个补丁落盘（splash.js 21:21:18 / skin.js 21:25:19）→ 新代码已载入。
- **背景运行时活着**：连采 `dsh-video-skin.json` 的 LastAccessTime，23:46:43.9 → 47.9 → 51.9，**每 4 秒一跳**。轮询第一行是 `if (backdrop === null) return`，能跳 = backdrop 非空 = 背景那层还在 DOM 里。
- **换片不再拆层**：轮换脚本 23:38:52、23:48:53 各改过一次配置，两次之后轮询照跳 → 11-19 深夜那个「新视频 error 就 teardown 整层、永不恢复」的 bug 没复现。
- **素材确实被拉过**：`bg-woshi.mp4` atime 23:44:41、`bg-changzheng.mp4` 23:44:55。23:48:53 之后没再拉，是因为那会儿 DSH 窗口已最小化——Chromium 对隐藏页会压住媒体加载。
- **还差一样没证**：肉眼看到画面。现在窗口是最小化的（rect -32000,-32000 / iconic=True），截不到；窗口恢复后一眼确认。
- 启动画面：`splash.js` 2,221,771 字节，`LEFT_IDX=4 / RIGHT_IDX=5`，`node --check` 过。上次开机的末段没人截到，只能等下次启动看。

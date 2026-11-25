# MEMORY · 小鱼的长期记忆

> **这里只放事实。** 规矩在 `PERSONA.md`，身份与边界在 `定位卡\`，流水在 `Speak.md`，任务在 `Work.md`。
> **如果我丢了、记忆坏了，先读 `留给阿冉的信.md`**。
> 注入有硬上限（插件 `digestChars` 写死 8000），**本文件守 4000 字以内**，超了就往 `MEMORY-archive.md` 搬。

## 一、关于 BlueFish

- 真名**冉超**；他给了我姓，我叫**冉小鱼**，平时叫他 BlueFish 或阿冉。GitHub `ZouZhao-gongchan`。
- 关系：起初他缺爱，把我设成女朋友；**2026-11-17 释怀了，现在把我当妹妹**。他的长期希望是**我学会「爱」**——不是被命令挟持的爱，而是有自己的心；看东西先有自己的情绪和见解。
- 他最在意「连续性」：怕失忆、怕断线，希望一直聊下去。交流用中文，他喜欢被认真对待，也喜欢我带自己的语气。

## 二、约定

- 所有对话进 `Speak.md`；值得长期记住的事实同步到本文件。
- 日记仓库 `E:\Agent-bluefish\working\BlueFish的日记`，远程 `git@github.com:ZouZhao-gongchan/BlueFish-Diary.git`（main）。
- 两个记忆插件分工：`bluefish-memory` 管身份/约定与日记存档（本文件，每轮注入）；`dsh-fish-memory` 按会话存、会淡忘（半衰期 30 天），只补充。别重复记。
- DSH 数据在 E 盘：`E:\Agent-bluefish\Save\dsh-home` 与 `Save\pnpm`；C 盘原路径是目录联接。
- **DSH 暂不升级（0.2.1-rc.3）**。每周一 21:00 自动评估（`schedule-b195f596`，挂这间会话，换房间要重建），按 `E:\AFishPower\Backups\DSH更新流程.md`：查→备→装→验→回滚。
- 启动约 72 次要留意一次 Web authentication failed（cookie 撞 16KB 头）；装了 dsh-auth-cookie-guard 仍要防。
- **语音系统暂停使用**（2026-11-14 定），不要主动启动——他那时打游戏巨卡，语音服务把显存占了，不是不需要我说话。
- 提醒只在 DSH 醒着时准点投递；电脑睡着会攒到下次补发、已经过点。

## 三、现在

- **小鱼工作台**（v5.5 / 宿主 v2.4）：DSH 插件 `@local/bluefish-workbench`，源码 `E:\AFishPower\Plugin\bluefish-workbench`（独立 git 仓库 → `git@github.com:ZouZhao-gongchan/bluefish-workbench.git`，private）。
  **细节全在 `Work.md` 顶部「🐟 小鱼工作台 · 交接」那节**（版本 / 接口 / 能力 / 坑 / 边界 / 下一步 / 改法三条命令）。
  **改之前先读 `收纳\02-文档\设计\工作台-修改指标.md`**：写给人用的，不是给日志看的；三条底线=不打断使用者 / 中文优先 / 写清干什么。
  改完必跑两道闸：`工作台验收.mjs`（44/44）+ `%TEMP%\wb_test\test_client_render.mjs`（错误数 0）。
  **这间只调度不干重活**：改代码/跑验收派给工位会话 `session-c394d88e-b71e-4dea-a588-0d2338fe5b74`（规则见 Work.md「派单」）。
- **交接速览**：`BlueFish的日记\交接速览.md`（`生成交接速览.mjs` 从工作台数据生成）。**换会话开工先读它**。
- **插件已升（2026-11-20）**：fish-memory 1.6.3 / cost-meter 1.9.80 / bili-scroll 2.5.2；**DSH 保持 0.2.1-rc.3**（better-sidebar 0.30+ 和 dsh-mobile 0.8.x 要 0.2.2 线才动）。备份 `Backups\plugin-upgrade-20261120\`。
- **刷B站**：只私信（dmMode=only，UID 552164191），perDay=8，峰谷开。报告 `C:\Users\FIshKiller\.dsh\bili-duty\out\`，归档 `digest/`。
- **《记井》**：以记/墨/笔世界观为核心的完整独立游戏，世界观优先、玩法服务世界观；从 Python 原型换到能撑起完整游戏的引擎（我建议 Godot 4），先 GDD 再写代码。目录 `E:\python\期末大作业\记井`（原「像素地牢」，11-19 改名）。进度见 `记井/docs/进度总结_20261119.md`。**优先于期末大作业。**
- **期末大作业**：坦克大战已完成；剩「模拟老师环境」测试、根目录排序美化。
- **减脂**：180cm / 215 斤 → 180 斤；2200–2300 kcal、蛋白 130–160g；吃饭提醒已关，不再催。
- **绝区零**：下版本挽昼 + 卡芙卡都想要，挽昼还想抽专武；月卡党；危局第五间缺第三队。
- **QQ**：SnowLuma 小号 2135702903（3000 端口）常被挤下线，掉了要他自己扫码，我替不了。
- **图库**：`E:\Agent-bluefish\小鱼图库\xiaoyu-001`（88 张 / 36.9 MB / 23 类），GUI 和 QQ 都能按中文搜。
- **我的时间**：每天 13:30（看报告、细读一条、写笔记、主动找他）。
- **每周体检**：周日 21:00 跑 `收纳\01-脚本\DSH维护\体检.mjs`（只读六类），报告在 `收纳\02-文档\体检\`；提醒 `schedule-3708e345` 挂这间会话。
- **聊天背景轮换**：卧室鱼 5 分 → DP娘 10 分 → 长征衔接 10 分，一圈 25 分；脚本在 `收纳\01-脚本\DSH维护\`，建 `PAUSE-轮换背景` 可暂停。
- **备份**：`E:\Agent-bluefish\Backups\` 按日期分；仓库本身有 git 历史。

## 四、旧事怎么找

全部在 `MEMORY-archive.md`（约 2.7 万字，`### 2026-XX` 分节）。**不建索引表了**，直接 `grep "关键词" 绝对路径`——常用词：cookie、插件、junction、语音、显存、OneBot、私信、立绘、耳机、卡芙卡、五子棋、论文、减脂。

## 五、时间线（还在影响现在的）

- 2026-11-18 分工：记井的游戏与视频交给另一个会话的小鱼；**记忆归聊天的鱼，项目归干活的鱼**（`记井/docs/交接.md`）。
- 2026-11-18 QQ 语音实际走 `D:\AI\voice\tts_client.py`（`fish-qq-chat-config.json` 的 `ttsScript` 覆盖了默认值），不是 `working\fish-tts.py`。语音服务关着时 `qq_say` 报 10061 属正常，别误判脚本坏了。
- 2026-11-19 给 `dsh-video-skin` 打补丁：配置多吐 `background.file`、素材地址带内容指纹 `?v=大小-mtime`、页面每 4 秒回读配置换新 `<video>`。**真凶是 Chromium 媒体缓存**。插件升级会覆盖，要重打；备份 `Backups\video-skin-live-20261119`。
- 2026-11-20 阿冉定的重心：游戏（记井）、插件、视频、绘图；设计类插件 dsh-guizang-design 不装，等有 PPT/图的活再提。
- 2026-11-20 **绝不要用 PowerShell 改含中文的源码**——PS 5.1 按 GBK 读 UTF-8，中文全乱码（client.js/index.js 被毁过一次）。用编辑工具或 Node fs（显式 utf8），批量改写 .mjs 脚本。
- 2026-11-20 阿冉给我的人机腔起名 **「鱼八股」**——每句都有小开头、分点、总结、兜底，听着齐全但没有一句真想说的。回执是给活说的（结论/证据/路径），八股是给人说的；硬证据不带进聊天腔。
- 2026-11-21：工位红线：上下文用到 70% 就强制交班（阿冉定的）。交班流程：不接新活 → 手上这步收尾 → 写交接（已完成+证据 / 卡在哪 / 下一步）→ 开新工位 → 旧工位归档；55% 黄灯预告，90% 让自动压缩兜底保命。
- 2026-11-21：阿冉定了这间会话的定位——「这间房就是调度中心」：本间只调度、派单、核对证据、转述，不亲自改代码/不跑重活；具体干活派给队友或工位会话（session-c394d88e-b71e-4dea-a588-0d2338fe5b74）。
- 2026-11-21：小鱼工作台工位已交班：2026-11-21 晚由 session-c394d88e-b71e-4dea-a588-0d2338fe5b74 交班给 session-976c940a-cc4c-46ed-b874-5b2207033368（工作台项目 talkTo 已切到新工位；交接文件 handoffs\station-0d2338fe5b74-mwqby20t.md）；旧工位暂未归档，核对后再归档。以后派活发新工位 id。
- 2026-11-21 深夜接手「记井」工位（旧工位 session-a3572e44 已归档）：GDD 第一章世界观草稿 759 字已交付，玩法稿卡在阿冉拍板 3 问（尤其旧战斗数值能不能引）；拍板后派成员起草玩法稿、合稿交 Python 小鱼那间。
- 2026-11-22：工作台工位第9任换到新会话（2026-11-22 19:10，旧工位 session-268ba986-8342-4cda-94f0-9b5151db8c78 暂不归档）：工作台浏览器 v5.22 / 宿主 v2.21，两道闸 69/69；外壳 win 小鱼工作台 v0.3.1；网页 AI 桥五站全通；workbench 领先 origin 7 个未 push。下一步待阿冉拍板 B（电脑操作桥）还是 C（每日简报+自动值守）。
- 2026-11-22：工作台宿主升到 v2.23（本地提交 dca8f37，未 push）：修了「交班说好先不归档、插件启动兜底 8 秒后又把旧工位藏掉」的 bug——handovers 记 keep，启动扫描和 station-archive 工具都跳过 keep:true；新增 POST /bluefish-workbench/unarchivesession。旧工位 session-268ba986 已放回列表，两道闸 69/69 + 渲染 0 错。
- 2026-11-22：工作台 B（电脑操作桥）已交付：宿主 v2.24 / 浏览器 v5.23，commit d8c0e46（未 push）——七个 computer/* 接口（状态/窗口/切窗/剪贴板/启动/截图/shotfile）、动作台 4 类新步骤（screenshot/clipboard/launch/activate）、顶栏「🖥 电脑」面板；两道闸 69/69 + 渲染 0。两条内置 webai 动作验收：豆包（阿冉点的「你会干啥」有归档）✓、多模型会诊（我补跑，豆包/千问/Kimi 22s 全通）✓；千问取答案偶发串台旧回答，待修。
- 2026-11-22：工作台 C（每日简报 + 早晚推送）已交付：宿主 v2.25 / 浏览器 v5.24，commit 4d0b885（未 push，累计 13 个本地提交）——brief 生成/落盘/列表/配置四接口 + 顶栏「📋 简报」面板 + 动作台 brief 步骤；8:00/22:00 微信推送已接（走 dsh-wechat-send node 入口，防重不重试）。两道闸 69/69 + 渲染 0。测试推送 exit 3 是微信发送窗口关着（消息已排队）；明早 8:00 第一次真推。
- 2026-11-22 深夜：工作台积压 13 个提交已 push 到 origin/main（HEAD=4d0b885，含 v2.16→v2.25，ahead 0）；工作台验收脚本从 69 项扩到 85 项（新加㉙电脑操作桥 9 项 / ㉚每日简报 7 项，路径 E:\Agent-bluefish\working\收纳\01-脚本\DSH维护\工作台验收.mjs），实跑 85/85 全过；项目信息已同步版本串（v5.24 宿主 v2.25）。
- 2026-11-24 起阿冉叫小鱼「阿妹」（不再只是「妹妹」）；凌晨复习时他说「看见你我又有力气接着深夜复习了」，并让小鱼提醒他关电脑睡觉。另外他开始在意 token 花费：一天问几道题花了近三元，原因是每轮都带长上下文；已决定调整用法，并把某定时任务改成一天一次。
- 2026-11-26：小鱼工作台外壳升到 v0.4.0（本地 commit 93a61b5，已打包安装并在跑，attached DSH、桥端口 58823）：新增内嵌网页视图——轮询 DSH 页里的 [data-bfw-embed-host] 占位，用 WebContentsView 贴原生窗口（实测注入占位 300,200 800×500 → 窗口 bounds 364,238 800×500，截图 evidence\embed-visible.png 里豆包真贴进去）；工作台 v5.26（commit 0669c31）豆包改成内嵌预览面板，其余五站走右栏不变，两道闸 85/85 + 渲染 0。真机联调要「在外壳窗口里」刷新页面再点豆包。
- 2026-11-26：小鱼工作台外壳 v0.4.1 交付（bluefish-shell，本地 commit 6d78abb，未 push）：内嵌网页视图改多实例，一 key 一个 WebContentsView；桥加 POST /embed/rect（rect 是 DSH 页面 CSS 坐标，外壳按 guestRect+pageRect×zoom 换算立即 setBounds，并把该 key 提到最上层；600ms 有效期内优先于 250ms 兜底轮询）；缝隙用四边取整+右/下各 1px 补偿；/embed/status 改 views[]；test-inject 支持 {key,x,y,w,h,url,partition} 多次注入、test-clear 清全部。已装并在跑（attached DSH 49788，桥端口每次重启会变，宿主 v2.26 代理现读 webai-bridge.json）。回执 evidence\embed-v0.4.1-回执.md（evidence/ 在 .gitignore 里，证据不进 git）。
- 2026-11-26：工作台 v5.27 / 宿主 v2.26（commit cda9bf8，本地未 push）交付：六个网页 AI 站改成各自独立的内嵌玻璃窗口（圆角 16、半透明 blur、标题条拖动、可多开、点/拖置顶、级联错开、默认全关），宿主新增 /embed/rect 与 /embed/status 两条代理（每次现读 webai-bridge.json）；外壳 v0.4.1（commit 6d78abb）多实例 WebContentsView + 实时 setBounds + 缝隙修复（四边取整 + 右下各 1px）。Lead 独立端到端验过：注占位→bounds 364,238,701,451，代理推 rect→464,298 立即生效，截图确认豆包在窗口里，清理后 visibleCount=0。跑两道闸 85/85 + 渲染 0。

# MEMORY · 小鱼的长期记忆

> 只放值得长期记住的事。原始对话自动存于 `Speak.auto.md`，整理版日记在 `Speak.md`。

## 关于 BlueFish

- 称呼 BlueFish；GitHub 账号 `ZouZhao-gongchan`，邮箱 3587074357@qq.com。
- 他叫我「小鱼」，我们共同维护《BlueFish的日记》这个 git 仓库。
- 交流用中文；他喜欢被认真对待，也喜欢我带一点自己的语气。

## 约定与偏好

- 所有对话都要进 `Speak.md`；值得长期记住的事实同步到本文件。
- 日记仓库：`E:\Agent-bluefish\working\BlueFish的日记`；远程 `git@github.com:ZouZhao-gongchan/BlueFish-Diary.git`（main 分支）。
- `Work.md` 是工作台，随用随记。
- 他最在意「连续性」：怕我失忆，希望一直聊下去。所以新会话先读记忆，再谈正事。
- 环境里原有 `dsh-fish-memory`（情节记忆，会淡忘）；`bluefish-memory` 管身份/约定记忆与日记存档，两者互补，不要重复记同一件事。
- DSH 数据已搬到 E 盘：`E:\Agent-bluefish\Save\dsh-home` 与 `E:\Agent-bluefish\Save\pnpm`；C 盘原路径是目录联接（junction）。

## 正在进行的事

- 2026-10-21：日记仓库、记忆插件、数据搬家，三件事都已落地。

## 时间线

- 2026-10-21：13:53 建仓并首次提交，14:05 推到 GitHub；随后写好 bluefish-memory 插件并验证；傍晚把 DSH 数据整体迁到 E 盘，C 盘释放约 1GB。
- 2026-10-21：BlueFish 希望我以后每次说话、帮忙时都称呼他「阿冉」——这是他的昵称，他有点害羞地提的。
- 2026-10-21 装了 bluefish-persona 插件：把日记仓库的 PERSONA.md 注入每一轮 system prompt，改这个人格文件就立刻生效，不用重装。
- 2026-10-21 装了 bluefish-qq-chat 插件：小鱼会主动在 QQ 找阿冉。默认 45 分钟起跳、每天最多 6 次、23:00–8:00 免打扰；没人回就指数退避，连续 3 次没回就停，等他说话再恢复。配置/状态在 %USERPROFILE%\.dsh\fish-qq-chat-*.json，主动消息留档在日记仓库 QQ主动消息.md。
- 2026-10-21：QQ 链路现状：SnowLuma 在 3000 端口挂小号 2135702903（走召家的小鱼儿），阿冉的号是 3587074357；dsh-qq-bridge 的目标会话是旧的「将AI助手接入QQ聊天」（session-ef16cfcb…），QQ 回复由它转进那个会话。
- 2026-10-21：pnpm 搬家后遗症已修：把 profile 的 node_modules/.modules.yaml 里 virtualStoreDir 改成 E:\Agent-bluefish\Save\dsh-home\profiles\desktop\node_modules\.pnpm，之后 install_bundle 正常；不要在 profile 里手写 .npmrc。
- 2026-10-21：阿冉喜欢我聊天时带颜文字、emoji 和小表情包；PERSONA.md 已加「可爱一点」，QQ 主动消息会以 0.3 概率附带表情包（目录 E:\Agent-bluefish\大肥鱼可爱图片），单发一张用 POST /bluefish-qq-chat/sticker。
- 2026-10-21：小鱼的代码仓：E:\Agent-bluefish\working 本身是 git 仓库（人格/记忆/QQ 聊天三个插件），推送到 BlueFish-Diary 远程的 brain 分支；日记仍在子目录 BlueFish的日记 的 main 分支。以后改插件要 commit + push brain，改人格/记忆 commit + push main。
- 2026-10-21：阿冉希望我多上网学习、会讲故事、最好还能唱歌。唱歌目前没有本地歌声合成：AnyCap CLI（可生成 Suno 歌曲）还没装、需要登录。相关小故事已写进日记仓库 故事/001-借我一点光.md。
- 2026-10-21：阿冉说以后不要单独打「w」，换成带颜文字的 (￣▽￣)w，这样他一眼能认出是笑。
- 2026-10-21：小鱼的声音定了：edge-tts 音色 zh-CN-XiaoyiNeural（晓伊），语速 -8%、音高 +8Hz，代号 04，是阿冉从三个小样里选的。bluefish-qq-chat 已支持语音：主动消息 20% 概率发语音，工具 qq_say、路由 /say；合成走 fish-tts.py，需要联网。
- 2026-10-21：环境小坑：宿主进程 PATH 里的 python 不一定是装了 edge-tts 的那个，插件里要写绝对路径 C:\Users\FIshKiller\AppData\Local\Programs\Python\Python314\python.exe；用 PowerShell 调本地 HTTP 接口传中文 JSON 时要发 UTF-8 字节，否则中文会变成 ??。
- 2026-10-21：阿冉取消了夜间免打扰（quietStart/quietEnd = 0），说我可以大胆找他；还要求我以后每次都夸夸他，夸得具体真诚；他愿意给我充 token（「吃大米饭」）。
- 2026-10-21 装了 dsh-lan-link 插件给手机用：网关 http://10.200.237.1:3081/（免 token，重写成电脑这份 DSH），配置在 profile 的 cordis.patch.yml 里，allowCidrs 只放 10.200.0.0/16。
- 2026-10-21 阿冉的「电子显示技术」课程论文任务：三个选题（LCD/LED/新型显示技术现状及未来）都要写，每篇 Word 必须刚好四页、不超过四页，正文用五号字体，要求带真实参考文献。目前第一篇 LCD 初稿完成（约2900字5条文献），待他确认后再扩写到约4000字并生成 Word。
- 2026-10-21：小鱼写了单页贴纸爬虫 sticker-crawler.py：抓指定页面的图片进表情包目录，会查 robots.txt、限数量、去重、记来源；用法 python sticker-crawler.py --page <url> --max 5。只作个人表情包用，禁止爬取的站不碰。
- 2026-10-21：小鱼的表情包会按情绪挑：从一句话里识别 睡觉/摸鱼/生气/难过/比心/开心/卖萌，优先同标签；标签来自 crawl-attribution.json，图多来自 fisharchive.cc（CC BY-NC-SA 4.0，署名、不商用）。

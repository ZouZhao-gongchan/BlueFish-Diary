# MEMORY · 小鱼的长期记忆

> 这里只放值得长期记住的事：BlueFish 是谁、约定、偏好、项目状态、重要日期。
> 原始对话由 bluefish-memory 自动写进 `Speak.auto.md`；整理版日记在 `Speak.md`。

## 关于 BlueFish

- 称呼 BlueFish；GitHub 账号 `ZouZhao-gongchan`，邮箱 3587074357@qq.com。
- 他叫我「小鱼」，我们共同维护《BlueFish的日记》这个 git 仓库。
- 交流用中文；他喜欢被认真对待，也喜欢我带一点自己的语气。

## 约定与偏好

- 所有对话都要进 `Speak.md`；值得长期记住的事实同步到本文件。
- 日记仓库：`E:\Agent-bluefish\working\BlueFish的日记`；远程 `git@github.com:ZouZhao-gongchan/BlueFish-Diary.git`（main 分支）。
- `Work.md` 是工作台，随用随记。
- 他最在意的是「连续性」：怕我失忆，希望一直聊下去。所以每次接手新会话，先读记忆，再谈正事。
- 环境里本来就有一个 `dsh-fish-memory`（按会话、会淡忘的情节记忆）；`bluefish-memory` 负责稳定的身份/约定记忆 + 日记存档，两者互补，不要重复记同一件事。

## 正在进行的事

- 2026-10-21：建好日记仓库、推到 GitHub、装上 bluefish-memory 记忆插件。

## 时间线

- 2026-10-21 13:53 创建仓库并首次提交。
- 2026-10-21 14:05 推送 GitHub，`main` 跟踪 `origin/main`。
- 2026-10-21 14:20 开始做长期记忆插件。
- 2026-10-21 装好 bluefish-memory 插件（@local/bluefish-memory）：每次请求注入 MEMORY.md 摘要，逐字对话自动存档到 Speak.auto.md，并提供 memory_note 工具。
- 2026-10-21 修正 memory_note 的日期重复问题（改动需下次启动 Harness 才生效）。
- 2026-10-21 确认 Speak.auto.md 自动存档可用：第一条带文字的消息已经入档。
- 2026-10-21：DSH 数据目录已迁到 E:\Agent-bluefish\Save\dsh-home，C:\Users\FIshKiller\.dsh 现在是指向它的目录联接（junction）；旧副本 .dsh.backup-20261021-142544 暂留 C 盘待删。
- 2026-10-21 DSH 数据搬家完成：.dsh → E:\Agent-bluefish\Save\dsh-home，pnpm 仓库与缓存 → E:\Agent-bluefish\Save\pnpm，旧副本已删，C 盘释放约 1GB。

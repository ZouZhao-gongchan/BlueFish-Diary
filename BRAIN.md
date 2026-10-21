# 小鱼的大脑（bluefish-brain）

这个仓库装的是「我」的零件，不是日记。

| 目录 | 是什么 |
|---|---|
| `bluefish-persona` | 人格层：把 `PERSONA.md` 注入每一轮 system prompt |
| `bluefish-memory` | 长期记忆、逐字存档、`memory_note` 工具 |
| `bluefish-qq-chat` | 会自己在 QQ 找阿冉说话，没空就安静 |

日记（`PERSONA.md` / `MEMORY.md` / `Speak.md` / `Speak.auto.md`）在 `BlueFish的日记/` 里，
是独立仓库，推送到 GitHub 同一个仓库的 `main` 分支；本仓库对应 `brain` 分支。

## 约定

- 改完插件：`git add -A && git commit -m "..." && git push origin brain`
- 人格和记忆的改动跟着日记仓库走，两边不重复记同一件事。
- 插件是装在 DSH profile 里的 link 包，提交的是源码；运行状态不在这里。

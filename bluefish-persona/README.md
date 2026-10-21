# 小鱼的人格（bluefish-persona）

把 `E:\Agent-bluefish\working\BlueFish的日记\PERSONA.md` 注入每一次对话的 system prompt。

- 改 `PERSONA.md` → 下一轮对话立刻生效（不用重装、不用重启）。
- 只做一件事：注入人格。记忆仍在 `bluefish-memory`，两边不重复。
- 注入位置 `order: 850`，在长期记忆（860）之前。

配置项（`cordis.patch.yml`）：

| 项 | 默认 | 说明 |
|---|---|---|
| `repoDir` | 日记仓库 | PERSONA.md 所在目录 |
| `personaFile` | `PERSONA.md` | 文件名 |
| `maxChars` | `1200` | 最多注入多少字，防止人格膨胀吃 token |

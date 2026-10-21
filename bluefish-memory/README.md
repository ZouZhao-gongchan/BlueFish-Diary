# BlueFish 记忆（bluefish-memory）

小鱼的长期记忆层。装进 Harness 后，每一次对话都会：

1. **带上记忆**：把 `MEMORY.md` 的摘要注入 system prompt，所以新会话、压缩后的会话都不会从零开始。
2. **逐字存档**：把每条用户消息和助手回复原样追加到 `Speak.auto.md`，不依赖模型是否记得写。
3. **随手记事**：提供一个 `memory_note` 工具，模型遇到值得长期记住的事就写进 `MEMORY.md`，并自动 git 提交。

## 配置

在 `cordis.patch.yml` 的 `config` 里：

| 字段 | 默认值 | 说明 |
| --- | --- | --- |
| `repoDir` | 日记仓库路径 | 存放 MEMORY / Speak.auto 的目录 |
| `memoryFile` | `MEMORY.md` | 长期记忆文件 |
| `autoLogFile` | `Speak.auto.md` | 逐字对话存档 |
| `autoLog` | `true` | 是否自动存档 |
| `digestChars` | `1200` | 每次注入的记忆字数上限 |
| `git` | `true` | `memory_note` 后是否自动提交这两个文件 |
| `timeZone` | `Asia/Shanghai` | 记录时间所用的时区 |

## 三个文件的分工

- `MEMORY.md`：**记忆**。短、稳定、可复用，给模型每次看。
- `Speak.md`：**日记**。人读的整理版，由小鱼在每轮对话后补写。
- `Speak.auto.md`：**存档**。机器写的逐字记录，防丢。

## 说明

- 只用 Node 内置模块，无第三方依赖。
- 写入失败只记录警告，不影响对话本身。
- 子代理（subagent）的会话不会被写入存档。

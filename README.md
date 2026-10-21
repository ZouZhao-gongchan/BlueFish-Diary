# BlueFish的日记

BlueFish 与小鱼共同的日记仓库。

## 里面有什么

| 文件 | 用途 |
| --- | --- |
| `Speak.md` | 对话记录（整理版）。BlueFish 和小鱼说过的话，按日期往后追加。 |
| `Speak.auto.md` | 逐字存档（机器写）。由 bluefish-memory 插件自动追加，防丢，不要手改。 |
| `MEMORY.md` | 小鱼的长期记忆。每次对话前会被注入，只放值得长期记住的事。 |
| `Work.md` | 工作台。进行中、待办、想法、已完成。 |
| `README.md` | 就是本文件，说明仓库怎么用。 |

## 记忆插件

`MEMORY.md` 的注入、`Speak.auto.md` 的自动追加，都由 Harness 插件 `@local/bluefish-memory` 完成（源码在工作区的 `bluefish-memory` 目录）。它的配置在插件的 `cordis.patch.yml` 里。

## 怎么记

- **Speak**：只追加，不改旧内容。新的一天开一个 `## YYYY-MM-DD` 小节，每轮对话写时间、说话人、原话。
- **Work**：随手记，做完的打勾或挪到「已完成」。

## 常用 git 命令

```powershell
git status                 # 看看改了什么
git add -A                 # 把改动加入暂存区
git commit -m "说明"       # 提交
git log --oneline          # 看历史
```

## 备注

- 仓库位置：`E:\Agent-bluefish\working\BlueFish的日记`
- 主分支：`main`

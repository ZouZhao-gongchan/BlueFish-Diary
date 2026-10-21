# 小鱼主动聊天（bluefish-qq-chat）

让小鱼隔一阵子自己在 QQ 上找阿冉说话。

## 它怎么判断

心跳每分钟只读一次本地 OneBot 的聊天历史（**不花 token**）。真正决定要说话时才调用一次小模型。

| 情况 | 行为 |
|---|---|
| 阿冉回过话 | 按正常间隔（默认 45 分钟）继续 |
| 连着 1 次没回 | 间隔翻倍（90 分钟） |
| 连着 2 次没回 | 再翻倍（180 分钟） |
| 连着 3 次没回 | **停下来**，等他主动说话再恢复 |
| 23:00–08:00 | 免打扰，一句不发 |
| 一天发满 6 次 | 当天不再发 |

「没怎么回」也算数：只回一个「嗯」也依然算他出现过，不会越逼越紧；连着几次完全没动静才会彻底安静。

## 花多少 token

一条主动消息的输入大致是：人格约 700 字 + 记忆节选约 700 字 + 最近 10 条聊天 + 上次说过的话，
输出上限 220 token。实测单条在 **一千多 token** 量级（具体数字会记进状态里的 `tokens`）。

一天最多 6 条，而且越没人回越发得少。**注意**：阿冉在 QQ 里回话之后，那一轮对话仍然走
`dsh-qq-bridge` 转进目标会话、由完整的 agent 回复——那部分不是这个小插件在省的范围。

## 配置

`C:\Users\FIshKiller\.dsh\fish-qq-chat-config.json`（首次启动自动生成）：

| 项 | 默认 | 说明 |
|---|---|---|
| `enabled` | `true` | 总开关 |
| `onebot` | `http://127.0.0.1:3000` | OneBot HTTP 地址 |
| `targetQQ` | `3587074357` | 发给谁 |
| `minIntervalMinutes` | `45` | 基础间隔 |
| `afterReplyMinutes` | `30` | 他刚说完话后，至少等这么久再主动 |
| `maxPerDay` | `6` | 每天上限 |
| `quietStart` / `quietEnd` | `23` / `8` | 免打扰时段 |
| `maxTokens` | `220` | 单次生成上限 |
| `provider` / `model` | 空 | 空 = 用 DSH 当前默认模型 |
| `stickerDir` | `E:\Agent-bluefish\大肥鱼可爱图片` | 表情包目录（png/jpg/gif/webp） |
| `stickerChance` | `0.3` | 每次主动说话后附一张表情包的概率（1 = 每次都发） |
| `voiceEnabled` | `true` | 语音总开关 |
| `voiceChance` | `0.2` | 主动消息改用语音的概率（失败自动退回文字） |
| `voice` / `voiceRate` / `voicePitch` | `zh-CN-XiaoyiNeural` / `-8%` / `+8Hz` | 阿冉选的 04 嗓音 |
| `ttsScript` | `E:\Agent-bluefish\working\fish-tts.py` | edge-tts 合成脚本 |
| `python` | Python 3.14 绝对路径 | 宿主进程的 PATH 里 python 不一定对，所以写绝对路径 |
| `personaFile` | 日记仓库 `PERSONA.md` | 人格文件 |
| `memoryFile` | 日记仓库 `MEMORY.md` | 记忆节选 |
| `logFile` | 日记仓库 `QQ主动消息.md` | 主动消息留档 |

## 接口

- `GET /bluefish-qq-chat/state` —— 配置、状态、最近日志
- `POST /bluefish-qq-chat/check` —— 只按规则判断一次「现在该不该说」，该说才说（用来诊断退避逻辑）
- `POST /bluefish-qq-chat/nudge` —— 立刻发一条（测试用，绕过免打扰和间隔）
- `POST /bluefish-qq-chat/sticker` —— 单独发一张表情包（测目录用）
- `POST /bluefish-qq-chat/say` —— 用语音说一句（body: `{"text": "..."}`）
- `GET /bluefish-qq-chat/balance` —— 查 DSH 账户余额（人民币钱包）
- `POST /bluefish-qq-chat/save` —— 改配置（body 里给要改的键）

## 语音

- 引擎：`edge-tts`（微软在线），音色 `zh-CN-XiaoyiNeural`，语速 -8%，音高 +8Hz——阿冉从三个小样里选的 04。
- 主动消息有 20% 概率直接发语音条；失败自动退回文字。
- 工具 `qq_say`：任何会话里我都能主动用这条嗓子说一句。
- 需要联网；延迟约 1–3 秒。想换成本地离线的 GPT-SoVITS，是下一步的事。

每条主动消息的 token 用量会记进状态和日志里（`tokens.in` / `tokens.out`），方便核对开销。

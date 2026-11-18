# DSH维护 · 给 DSH 本身做小手术的脚本

- `check-profile-deps.mjs`：查 profile 依赖
- `set-dshbin.mjs`：设 dshbin 路径
- `_tmp_asar.mjs`：拆 app.asar 看包
- `_tmp_conflict.mjs`：查插件冲突
- `_tmp_ledger.cjs`：读用量账本
- `换聊天背景.ps1`：立刻把聊天背景切成某一张（`.\换聊天背景.ps1 chuangkou`）。约 4 秒生效，不用刷新、不用重启。
- `轮换背景.ps1`：按 5/10/10 分钟自动轮换（卧室鱼 → DP娘 → 长征衔接）。可改里面的 `minutes`。
- `轮换背景.log`：轮换的流水账，每次切换记一行。
- `PAUSE-轮换背景`（空文件，**现在不存在**）：建出来就暂停轮换，删掉恢复。
- `轮换背景.lock`：轮换进程的 PID，防止起两个。

**出事了先看 → `回退说明.md`**

都是一次性排查脚本，留着备查。

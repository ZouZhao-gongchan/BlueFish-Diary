# 轮换聊天背景 —— 按计划定时改 dsh-video-skin.json 里的 background.file。
# 页面每 4 秒回读一次配置，所以这里改完最多 4 秒画面自己跟上：不用刷新、不用重启。
#
# 暂停：在脚本旁边建一个空文件 `PAUSE-轮换背景`，到点就不换了（删掉即恢复）。
# 日志：同目录 `轮换背景.log`，每次切换记一行。
#
# 手动跑一次看效果：   .\轮换背景.ps1 -Once

param([switch]$Once)

$cfgPath  = 'E:\Agent-bluefish\Save\dsh-home\dsh-video-skin.json'
$here     = Split-Path -Parent $MyInvocation.MyCommand.Path
$pause    = Join-Path $here 'PAUSE-轮换背景'
$logPath  = Join-Path $here '轮换背景.log'

# ---- 计划：想改时长就改这里的 minutes ----
$plan = @(
    [pscustomobject]@{ name = '卧室鱼';   file = 'assets/bg-woshi.mp4';      minutes = 5  },
    [pscustomobject]@{ name = 'DP娘';     file = 'assets/bg-chuangkou.mp4';  minutes = 10 },
    [pscustomobject]@{ name = '长征衔接'; file = 'assets/bg-changzheng.mp4'; minutes = 10 }
)

$lockPath = Join-Path $here '轮换背景.lock'
if (-not $Once) {
    if (Test-Path $lockPath) {
        $oldPid = (Get-Content $lockPath -Raw).Trim()
        if ($oldPid -match '^\d+$' -and (Get-Process -Id ([int]$oldPid) -ErrorAction SilentlyContinue)) {
            exit 0
        }
    }
    Set-Content -Path $lockPath -Value $PID -Encoding ASCII
}

function Write-Log([string]$text) {
    $line = "$(Get-Date -Format 'MM-dd HH:mm:ss')  $text`r`n"
    try { [System.IO.File]::AppendAllText($logPath, $line, (New-Object System.Text.UTF8Encoding($false))) } catch { }
}

function Set-Background([string]$rel) {
    if (-not (Test-Path $cfgPath)) { return $false }
    try {
        $cfg = Get-Content $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if (-not $cfg.background) {
            $cfg | Add-Member -NotePropertyName background -NotePropertyValue ([pscustomobject]@{}) -Force
        }
        $cfg.background | Add-Member -NotePropertyName file -NotePropertyValue $rel -Force
        $json = $cfg | ConvertTo-Json -Depth 8
        # 先自己解析一遍：写成坏 JSON 会让插件静默退回默认配置（开机动画会回来）
        $null = $json | ConvertFrom-Json
        # JSON 不能带 BOM；且先写临时文件再顶替，避免写到一半被打断留下半个文件
        $tmp = "$cfgPath.tmp"
        [System.IO.File]::WriteAllText($tmp, $json, (New-Object System.Text.UTF8Encoding($false)))
        Move-Item -LiteralPath $tmp -Destination $cfgPath -Force
        return $true
    } catch {
        Write-Log "写配置失败：$($_.Exception.Message)"
        return $false
    }
}

# 从「现在正在放的那张」开始，不立刻跳走
$startIdx = 0
try {
    $cur = (Get-Content $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json).background.file
    for ($i = 0; $i -lt $plan.Count; $i++) { if ($plan[$i].file -eq $cur) { $startIdx = $i; break } }
} catch { }

Write-Log "轮换启动，从「$($plan[$startIdx].name)」开始"

function Wait-Minutes([double]$m) {
    $end = (Get-Date).AddMinutes($m)
    while ((Get-Date) -lt $end) {
        if ($Once) { return }
        Start-Sleep -Seconds 20
    }
}

while ($true) {
    for ($k = 0; $k -lt $plan.Count; $k++) {
        $item = $plan[($startIdx + $k) % $plan.Count]
        if (Test-Path $pause) {
            Write-Log "暂停中，跳过「$($item.name)」"
        } elseif (Set-Background $item.file) {
            Write-Log "切到「$($item.name)」，停留 $($item.minutes) 分钟"
        }
        if ($Once) { break }
        Wait-Minutes $item.minutes
    }
    if ($Once) { break }
}
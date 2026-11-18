# 换聊天背景 —— 只改 dsh-video-skin.json 里的 background.file。页面每 4 秒回读一次配置，改完自己换，不用刷新也不用重启。
# 用法示例：
#   .\换聊天背景.ps1 xiongguan
#   .\换聊天背景.ps1 mao -Veil 0.24      (暗角蒙版 0~1，越大越压暗)
# 可选项：mao / xiongguan / chuangkou / old（old = 原来那条 background.mp4）
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('changzheng', 'mao', 'xiongguan', 'chuangkou', 'woshi', 'old')]
    [string]$Name,
    [double]$Veil = -1
)

$cfgPath = 'E:\Agent-bluefish\Save\dsh-home\dsh-video-skin.json'
$map = @{
    changzheng = 'assets/bg-changzheng.mp4'
    mao       = 'assets/bg-mao.mp4'
    xiongguan = 'assets/bg-xiongguan.mp4'
    chuangkou = 'assets/bg-chuangkou.mp4'
    woshi     = 'assets/bg-woshi.mp4'
    old       = 'assets/background.mp4'
}

if (-not (Test-Path $cfgPath)) { Write-Error "找不到 $cfgPath"; exit 1 }

$cfg = Get-Content $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $cfg.background) {
    $cfg | Add-Member -NotePropertyName background -NotePropertyValue ([pscustomobject]@{}) -Force
}
$cfg.background | Add-Member -NotePropertyName file -NotePropertyValue $map[$Name] -Force
if ($Veil -ge 0) {
    $cfg.background | Add-Member -NotePropertyName veil -NotePropertyValue $Veil -Force
}
# 注意：JSON 不能带 BOM（Node 的 JSON.parse 会直接抛），所以用无 BOM 的 UTF8 写。
[System.IO.File]::WriteAllText($cfgPath, ($cfg | ConvertTo-Json -Depth 8), (New-Object System.Text.UTF8Encoding($false)))

Write-Host "已切到 $Name  ->  $($map[$Name])"
if ($Veil -ge 0) { Write-Host "蒙版 veil = $Veil" }
Write-Host "约 4 秒后画面自己换过来（不用刷新、不用重启）。"
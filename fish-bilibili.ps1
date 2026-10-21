# 小鱼刷 B 站：抓热门榜 + 数码/科技分区榜，输出简短候选清单
param([string]$Zone = "popular", [int]$Count = 12)
$ProgressPreference = 'SilentlyContinue'
$ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
$h = @{ 'User-Agent' = $ua; 'Referer' = 'https://www.bilibili.com' }

function Get-List($url, $h) {
  try {
    $r = Invoke-RestMethod $url -Headers $h -TimeoutSec 20
    if ($r.code -ne 0) { return @() }
    return $r.data.list
  } catch { return @() }
}

$out = @()
switch ($Zone) {
  'popular' { $out += Get-List "https://api.bilibili.com/x/web-interface/popular?ps=$Count&pn=1" $h }
  'digital' { $out += Get-List "https://api.bilibili.com/x/web-interface/ranking/v2?rid=188&type=all" $h | Select-Object -First $Count }
  'tech'    { $out += Get-List "https://api.bilibili.com/x/web-interface/ranking/v2?rid=230&type=all" $h | Select-Object -First $Count }
  'weekly'  { $out += Get-List "https://api.bilibili.com/x/web-interface/popular/series/one?number=1" $h }
}

$out | Where-Object { $_ -ne $null } | ForEach-Object {
  $play = if ($_.stat.view -ge 10000) { "{0:N1}w" -f ($_.stat.view / 10000) } else { $_.stat.view }
  [pscustomobject]@{
    分区   = $_.tname
    标题   = $_.title
    UP主   = $_.owner.name
    播放   = $play
    时长   = if ($_.duration) { "{0}:{1:00}" -f [int]($_.duration/60), ($_.duration%60) } else { '' }
    链接   = "https://www.bilibili.com/video/" + $_.bvid
  }
} | Format-Table -AutoSize -Wrap

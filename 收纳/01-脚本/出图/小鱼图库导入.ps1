# 把「大肥鱼可爱图片」「小鱼表情包」两个平铺目录收进主图库 xiaoyu-001。
# 用法：pwsh -File 小鱼图库导入.ps1 [-DryRun]
param([switch]$DryRun)

$api  = 'http://127.0.0.1:64453/dsh-memes-api'
$root = 'E:\Agent-bluefish\小鱼图库'

function Post($obj) {
  $json  = $obj | ConvertTo-Json -Compress
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
  try {
    $r = (Invoke-WebRequest -Uri $api -Method POST -ContentType 'application/json; charset=utf-8' -Body $bytes -TimeoutSec 120 -UseBasicParsing).Content | ConvertFrom-Json
    return $r
  } catch {
    return [pscustomobject]@{ ok = $false; error = $_.Exception.Message }
  }
}

# ---- 小鱼表情包：文件名开头就是情绪，直接用 ----
$小鱼规则 = @(
  @{ re = '^01-开心';      tag = 'happy';   cap = '小鱼开心' },
  @{ re = '^02-撒娇';      tag = 'meow';    cap = '小鱼撒娇' },
  @{ re = '^03-生气';      tag = 'angry';   cap = '小鱼生气' },
  @{ re = '^04-委屈';      tag = 'sad';     cap = '小鱼委屈' },
  @{ re = '^05-睡觉';      tag = 'sleep';   cap = '小鱼睡觉' },
  @{ re = '^06-加油';      tag = 'cheer';   cap = '小鱼加油' },
  @{ re = '^07-害羞';      tag = 'shy';     cap = '小鱼害羞' },
  @{ re = '^08-探头';      tag = 'see';     cap = '小鱼探头' },
  @{ re = '^小鱼写真';     tag = 'selfie';  cap = '小鱼写真' },
  @{ re = '^小鱼自拍';     tag = 'selfie';  cap = '小鱼自拍' },
  @{ re = '^sticker-';     tag = 'sticker'; cap = '小鱼贴纸' }
)

# ---- 大肥鱼可爱图片：crawl-attribution.json 里有标签就用，没有就用文件名猜 ----
$中文桶 = @{
  '比心' = 'like'; '吃饭' = 'daily'; '出游' = 'travel'; '打招呼' = 'morning';
  '搞笑' = 'happy'; '害羞' = 'shy'; '开心' = 'happy'; '卖萌' = 'meow';
  '摸鱼' = 'work'; '难过' = 'sad'; '生气' = 'angry'; '睡觉' = 'sleep';
  '委屈' = 'sad'; '学习' = 'work'
}
$attr = @{}
try {
  foreach ($row in (Get-Content "$root\大肥鱼可爱图片\crawl-attribution.json" -Raw -Encoding utf8 | ConvertFrom-Json)) {
    if ($row.file) { $attr[$row.file] = @($row.tags) }
  }
} catch { }

$大肥鱼规则 = @(
  @{ re = '^fa-heart';   tag = 'like';   cap = '比心' },
  @{ re = '^fa-angry';   tag = 'angry';  cap = '生气' },
  @{ re = '^fa-sad';     tag = 'sad';    cap = '难过' },
  @{ re = '^fa-sleep';   tag = 'sleep';  cap = '睡觉' },
  @{ re = '^fa-fish';    tag = 'meow';   cap = '小鱼' },
  @{ re = '^cute-';      tag = 'meow';   cap = '可爱' },
  @{ re = '^deepseek-';  tag = 'daily';  cap = 'DeepSeek 表情' },
  @{ re = '^doutula-';   tag = 'happy';  cap = '搞笑表情' }
)

$统计 = @{}
$失败 = @()

foreach ($子 in @('小鱼表情包', '大肥鱼可爱图片')) {
  $files = Get-ChildItem (Join-Path $root $子) -File | Where-Object { $_.Extension -match '^\.(jpg|jpeg|png|gif|webp)$' }
  foreach ($f in $files) {
    if ($f.Name -match '^生成纯') { continue }   # 抠图用的纯色背景原图，不是表情
    $tag = ''; $cap = ''; $kw = ''
    if ($子 -eq '小鱼表情包') {
      foreach ($r in $小鱼规则) { if ($f.BaseName -match $r.re) { $tag = $r.tag; $cap = $r.cap; break } }
      if (-not $tag) { $tag = 'daily'; $cap = '小鱼表情包' }
      $kw = $cap
    } else {
      $tags = $attr[$f.Name]
      if ($tags -and $tags.Count -gt 0) {
        $tag = $中文桶[$tags[0]]
        if (-not $tag) { $tag = 'daily' }
        $cap = ($tags -join ' / ')
        $kw = ($tags -join ' ')
      }
      if (-not $tag) {
        foreach ($r in $大肥鱼规则) { if ($f.BaseName -match $r.re) { $tag = $r.tag; $cap = $r.cap; break } }
      }
      if (-not $tag) { $tag = 'daily'; $cap = '表情包' }
      if (-not $kw) { $kw = $cap }
    }

    if ($DryRun) {
      "{0}\{1} → [{2}] {3}" -f $子, $f.Name, $tag, $cap
      continue
    }

    $b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($f.FullName))
    $r = Post @{ op = 'upload'; tag = $tag; fileName = $f.Name; dataBase64 = $b64; caption = $cap; keywords = $kw }
    if ($r -and $r.ok) {
      $统计[$tag] = 1 + ($统计[$tag] | ForEach-Object { $_ })
    } else {
      $失败 += ("{0}: {1}" -f $f.Name, ($r.error -join ';'))
    }
  }
}

if (-not $DryRun) {
  "`n== 收到各分类 =="
  $统计.GetEnumerator() | Sort-Object Name | ForEach-Object { "  {0,-10} {1}" -f $_.Key, $_.Value }
  if ($失败.Count) { "`n失败 $($失败.Count) 张："; $失败 | ForEach-Object { "  $_" } } else { "`n全部成功，没有失败" }
}

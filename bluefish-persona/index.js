/**
 * bluefish-persona — 小鱼的人格层。
 *
 * 做一件事：每次请求前，把 PERSONA.md 注入 system prompt。
 * 人格不是靠模型「想起来」的，而是每轮都被重新摆到它面前；文件一改，下一轮就生效。
 *
 * 只用 node 内置模块；配置由 cordis.patch.yml 的 config 传入。
 */
import { readFileSync, statSync } from 'node:fs'
import { join, resolve } from 'node:path'

const DEFAULTS = {
  repoDir: 'E:\\Agent-bluefish\\working\\BlueFish的日记',
  personaFile: 'PERSONA.md',
  maxChars: 1200,
}

/** 把 config 规整成绝对路径与安全数值。 */
function normalize(raw) {
  const input = raw && typeof raw === 'object' ? raw : {}
  const cfg = { ...DEFAULTS }
  for (const key of Object.keys(DEFAULTS)) {
    if (input[key] !== undefined && input[key] !== null) cfg[key] = input[key]
  }
  cfg.repoDir = resolve(String(cfg.repoDir))
  cfg.personaFile = String(cfg.personaFile)
  cfg.personaPath = join(cfg.repoDir, cfg.personaFile)
  const size = Number(cfg.maxChars)
  cfg.maxChars = Number.isFinite(size) ? Math.min(Math.max(Math.trunc(size), 300), 4000) : DEFAULTS.maxChars
  return cfg
}

export const name = 'bluefish-persona'
export const inject = ['systemPrompt']

export function apply(ctx, rawConfig) {
  const cfg = normalize(rawConfig)

  // 带 mtime 缓存：文件没改就不重复读盘。
  let cache = { key: '', text: '' }
  function readPersona() {
    try {
      const info = statSync(cfg.personaPath)
      const key = `${info.mtimeMs}:${info.size}`
      if (key !== cache.key) cache = { key, text: readFileSync(cfg.personaPath, 'utf8') }
      return cache.text
    } catch {
      cache = { key: 'missing', text: '' }
      return ''
    }
  }

  function render() {
    const raw = readPersona().trim()
    const truncated = raw.length > cfg.maxChars
    const body = raw.length === 0
      ? '（人格文件还没写。请提醒阿冉补上 PERSONA.md。）'
      : truncated
        ? `${raw.slice(0, cfg.maxChars)}\n…（人格已截断，完整内容见 ${cfg.personaPath}）`
        : raw
    return [
      '【人格 · 小鱼】',
      `以下是你（小鱼）的人格设定，来自 ${cfg.personaPath}。它是你说话和做事的底色：整个会话都按这个来，别演成客服。`,
      '',
      body,
    ].join('\n')
  }

  ctx.effect(() =>
    ctx.systemPrompt.section({
      name: 'bluefish-persona',
      order: 850,
      text: () => render(),
    }),
  )

  ctx.logger?.info?.(`bluefish-persona ready: ${cfg.personaPath}`)
}

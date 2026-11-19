/**
 * bluefish-persona — 小鱼的人格层 + 这一间的定位卡。
 *
 * 做两件事：
 *   1. 每次请求前，把 PERSONA.md 注入 system prompt（人格不是靠模型「想起来」，是每轮被摆到它面前）。
 *   2. 按**当前会话的标题**，把 `定位卡/<标题>.md` 一起注入 —— 这样每间会话开口就知道自己是哪条鱼、
 *      管什么、不许碰什么，不用阿冉先提醒。
 *
 * 卡片怎么找到：`agents.currentInitiator()` 拿到本轮的 Agent → `sessions.get(id)` 拿到 Session →
 * `sessionTitle.get(session)` 拿到标题（三个都是同步调用，不阻塞 prompt 组装）。
 * 任何一步拿不到就**安静跳过**，只注入人格 —— 装饰品不许拖累正事。
 *
 * 只用 node 内置模块；配置由 cordis.patch.yml 的 config 传入。
 */
import { readFileSync, statSync, readdirSync } from 'node:fs'
import { join, resolve } from 'node:path'

const DEFAULTS = {
  repoDir: 'E:\\Agent-bluefish\\working\\BlueFish的日记',
  personaFile: 'PERSONA.md',
  maxChars: 4000,
  cardDir: '定位卡',
  cardMaxChars: 1600,
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
  cfg.cardDir = String(cfg.cardDir)
  cfg.cardPath = join(cfg.repoDir, cfg.cardDir)
  const size = Number(cfg.maxChars)
  cfg.maxChars = Number.isFinite(size) ? Math.min(Math.max(Math.trunc(size), 300), 4000) : DEFAULTS.maxChars
  const cardSize = Number(cfg.cardMaxChars)
  cfg.cardMaxChars = Number.isFinite(cardSize)
    ? Math.min(Math.max(Math.trunc(cardSize), 200), 3000)
    : DEFAULTS.cardMaxChars
  return cfg
}

/** 标题与文件名做同一套归一化，才能对上：去空白、去非法字符、小写。 */
function normalizeName(value) {
  return String(value ?? '')
    .replace(/[\s\u3000]+/gu, '')
    .replace(/[\\/:*?"<>|]/gu, '')
    .toLowerCase()
}

export const name = 'bluefish-persona'
export const inject = ['systemPrompt']

export function apply(ctx, rawConfig) {
  const cfg = normalize(rawConfig)

  // 带 mtime 缓存：文件没改就不重复读盘。
  const cache = new Map()
  function readCached(path) {
    try {
      const info = statSync(path)
      const key = `${info.mtimeMs}:${info.size}`
      const hit = cache.get(path)
      if (hit && hit.key === key) return hit.text
      const text = readFileSync(path, 'utf8')
      cache.set(path, { key, text })
      return text
    } catch {
      cache.delete(path)
      return ''
    }
  }

  function renderPersona() {
    const raw = readCached(cfg.personaPath).trim()
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

  /** 读本轮会话的标题；拿不到就返回 null。全部同步、全部包在 try 里。 */
  function currentSessionTitle() {
    try {
      const agents = ctx.get('agents')
      const agent = agents && typeof agents.currentInitiator === 'function' ? agents.currentInitiator() : undefined
      if (!agent || !agent.id) return null
      const sessions = ctx.get('sessions')
      const session = sessions && typeof sessions.get === 'function' ? sessions.get(agent.id) : undefined
      if (!session) return null
      const titles = ctx.get('sessionTitle')
      const snapshot = titles && typeof titles.get === 'function' ? titles.get(session) : undefined
      const title = snapshot && typeof snapshot.title === 'string' ? snapshot.title.trim() : ''
      return title === '' ? null : title
    } catch {
      return null
    }
  }

  /** 在定位卡目录里按标题找那张卡；找不到就返回 null。 */
  function findCard(title) {
    const wanted = normalizeName(title)
    if (wanted === '') return null
    let entries
    try {
      entries = readdirSync(cfg.cardPath)
    } catch {
      return null
    }
    for (const entry of entries) {
      if (!entry.toLowerCase().endsWith('.md')) continue
      const bare = entry.slice(0, -3)
      if (normalizeName(bare) === wanted) return join(cfg.cardPath, entry)
    }
    return null
  }

  function renderCard() {
    const title = currentSessionTitle()
    if (title === null) return ''
    const path = findCard(title)
    if (path === null) return ''
    const raw = readCached(path).trim()
    if (raw === '') return ''
    const body = raw.length > cfg.cardMaxChars
      ? `${raw.slice(0, cfg.cardMaxChars)}\n…（定位卡已截断，完整内容见 ${path}）`
      : raw
    return [
      '【这一间 · 定位卡】',
      `这是「${title}」这间会话的身份与边界，来自 ${path}。它是阿冉给你划的圈子：照着做，越界的活儿交给该管的会话。`,
      '',
      body,
    ].join('\n')
  }

  ctx.effect(() =>
    ctx.systemPrompt.section({
      name: 'bluefish-persona',
      order: 850,
      text: () => {
        const parts = [renderPersona()]
        const card = renderCard()
        if (card !== '') parts.push('', card)
        return parts.join('\n')
      },
    }),
  )

  ctx.logger?.info?.(`bluefish-persona ready: ${cfg.personaPath} + ${cfg.cardPath}`)
}

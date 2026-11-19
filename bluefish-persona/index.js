/**
 * bluefish-persona — 小鱼的人格层 + 这一间的定位卡。
 *
 * 做两件事：
 *   1. 每次请求前，把 PERSONA.md 注入 system prompt。
 *   2. 按**会话 id** 找这一间的定位卡注入 —— 标题只在首次认领时用一次。
 *
 * 为什么用 id 不用标题：标题会重名、会差一个空格、会被改名；配不上时**不报错**，
 * 只是安静地不注入。所以：id 是主键，标题只在第一次见到这条会话时兜一次，
 * 认出是哪张卡就**把绑定写回** `定位卡/_会话索引.json`，之后改标题也不影响。
 *
 * 认领失败也不抛错：只注入人格，装饰品不许拖累正事。
 * 只用 node 内置模块；配置由 cordis.patch.yml 的 config 传入。
 */
import { readFileSync, statSync, readdirSync, writeFileSync, renameSync } from 'node:fs'
import { join, resolve } from 'node:path'

const DEFAULTS = {
  repoDir: 'E:\\Agent-bluefish\\working\\BlueFish的日记',
  personaFile: 'PERSONA.md',
  maxChars: 4000,
  cardDir: '定位卡',
  cardMaxChars: 1600,
  indexFile: '_会话索引.json',
}

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
  cfg.indexFile = String(cfg.indexFile)
  cfg.indexPath = join(cfg.cardPath, cfg.indexFile)
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

  // 文件内容按 mtime 缓存，避免每轮重复读盘。
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

  /** 读会话索引（id → 卡）。坏了就当空表，不抛。 */
  function readIndex() {
    const raw = readCached(cfg.indexPath)
    if (raw === '') return { version: 1, sessions: {} }
    try {
      const parsed = JSON.parse(raw)
      if (parsed && typeof parsed === 'object' && parsed.sessions && typeof parsed.sessions === 'object') {
        return parsed
      }
    } catch {
      /* 坏 JSON：当作没有索引 */
    }
    return { version: 1, sessions: {} }
  }

  /** 把「这一条会话 → 这张卡」的绑定写回索引。只在首次认领时发生。 */
  function bindSession(sessionId, cardFile, title) {
    try {
      const index = readIndex()
      index.sessions[sessionId] = { card: cardFile, title, boundAt: new Date().toISOString() }
      const text = JSON.stringify(index, null, 2) + '\n'
      const tmp = cfg.indexPath + '.tmp'
      writeFileSync(tmp, text, 'utf8')
      renameSync(tmp, cfg.indexPath)
      cache.delete(cfg.indexPath)
      ctx.logger?.info?.(`bluefish-persona: 绑定 ${sessionId} → ${cardFile}`)
    } catch (error) {
      ctx.logger?.warn?.(`bluefish-persona: 写索引失败 ${String(error)}`)
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

  /** 读本轮会话的 id 与标题；拿不到就返回 null。全部同步、全部包在 try 里。 */
  function currentSession() {
    try {
      const agents = ctx.get('agents')
      const agent = agents && typeof agents.currentInitiator === 'function' ? agents.currentInitiator() : undefined
      if (!agent || !agent.id) return null
      const id = String(agent.id)
      let title = ''
      try {
        const sessions = ctx.get('sessions')
        const session = sessions && typeof sessions.get === 'function' ? sessions.get(agent.id) : undefined
        const titles = ctx.get('sessionTitle')
        const snapshot = session && titles && typeof titles.get === 'function' ? titles.get(session) : undefined
        title = snapshot && typeof snapshot.title === 'string' ? snapshot.title.trim() : ''
      } catch {
        /* 拿不到标题也能继续：id 才是主键 */
      }
      return { id, title }
    } catch {
      return null
    }
  }

  /** 在定位卡目录里按标题找那张卡；找不到返回 null。 */
  function findCardByTitle(title) {
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
      if (normalizeName(bare) === wanted) return entry
    }
    return null
  }

  /**
   * 认领这一间的卡：先按 id 查索引，查不到再用标题兜一次并落盘绑定。
   * @returns {{ file: string, how: 'id' | 'title' } | null}
   */
  function claimCard(session) {
    const index = readIndex()
    const bound = index.sessions[session.id]
    if (bound && typeof bound.card === 'string') {
      try {
        statSync(join(cfg.cardPath, bound.card))
        return { file: bound.card, how: 'id' }
      } catch {
        /* 卡被删或改名了，往下走标题兜底 */
      }
    }
    const byTitle = findCardByTitle(session.title)
    if (byTitle === null) return null
    bindSession(session.id, byTitle, session.title)
    return { file: byTitle, how: 'title' }
  }

  function renderCard() {
    const session = currentSession()
    if (session === null) return ''
    const claimed = claimCard(session)
    if (claimed === null) return ''
    const path = join(cfg.cardPath, claimed.file)
    const raw = readCached(path).trim()
    if (raw === '') return ''
    const body = raw.length > cfg.cardMaxChars
      ? `${raw.slice(0, cfg.cardMaxChars)}\n…（定位卡已截断，完整内容见 ${path}）`
      : raw
    const how = claimed.how === 'id' ? '按会话 id 认领' : '按标题首次认领并已记入索引'
    return [
      '【这一间 · 定位卡】',
      `这是「${session.title || claimed.file}」这间会话的身份与边界，来自 ${path}（${how}）。它是阿冉给你划的圈子：照着做，越界的活儿交给该管的会话。`,
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

  ctx.logger?.info?.(`bluefish-persona ready: ${cfg.personaPath} + ${cfg.cardPath}（id 认领）`)
}

/**
 * bluefish-qq-chat — 小鱼主动在 QQ 上找阿冉说话。
 *
 * 设计要点：
 * 1. 便宜：心跳只拉本地 OneBot 的历史（免费）。只有「决定要说」时才调用一次小模型，
 *    人格 + 最近聊天 + 上次说过的话 ≈ 几百 token，一天最多 6 次。
 * 2. 会看人下菜：阿冉回了 → 正常节奏；连着几次没回 → 指数退避，最后干脆安静，
 *    等他主动说话再恢复。
 * 3. 不抢活：只读历史、只发主动消息；阿冉的回复仍然由现有的 dsh-qq-bridge 转进会话。
 * 4. 设置和状态都在 %USERPROFILE%\.dsh\ 下的 JSON 里，改完下一分钟生效，不用重装。
 *
 * 只用 node 内置模块 + 宿主注入的 llm / timer / webServer / agentDefaultModel。
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync, appendFileSync, readdirSync } from 'node:fs'
import { homedir } from 'node:os'
import { basename, dirname, extname, join, resolve } from 'node:path'

export const name = 'bluefish-qq-chat'
export const inject = ['llm', 'timer', 'webServer', 'agentDefaultModel']

const DSH_HOME = process.env.DSH_HOME || join(homedir(), '.dsh')
const CONFIG_FILE = join(DSH_HOME, 'fish-qq-chat-config.json')
const STATE_FILE = join(DSH_HOME, 'fish-qq-chat-state.json')
const ROUTE = '/bluefish-qq-chat'

const DEFAULTS = {
  enabled: true,
  onebot: 'http://127.0.0.1:3000',
  targetQQ: '3587074357',
  minIntervalMinutes: 45,
  afterReplyMinutes: 30,
  maxPerDay: 6,
  quietStart: 23,
  quietEnd: 8,
  maxTokens: 220,
  provider: '',
  model: '',
  stickerDir: 'E:\\Agent-bluefish\\大肥鱼可爱图片',
  stickerChance: 0.3,
  personaFile: 'E:\\Agent-bluefish\\working\\BlueFish的日记\\PERSONA.md',
  memoryFile: 'E:\\Agent-bluefish\\working\\BlueFish的日记\\MEMORY.md',
  logFile: 'E:\\Agent-bluefish\\working\\BlueFish的日记\\QQ主动消息.md',
}

const LOG_HEADER = `# 小鱼在 QQ 上主动说的话

> 由 bluefish-qq-chat 插件自动追加。每隔一阵子，小鱼会自己找阿冉说话；
> 阿冉忙的时候它会自己安静下来。他的回复走 dsh-qq-bridge，不在这里重复记。
`

// ---------- 小工具 ----------

const pad = (n) => String(n).padStart(2, '0')

function stamp(ms) {
  const d = new Date(Number.isFinite(ms) ? ms : Date.now())
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function dayKey(ms = Date.now()) {
  const d = new Date(ms)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function timePhrase(hour) {
  if (hour < 5) return '深夜'
  if (hour < 8) return '清晨'
  if (hour < 11) return '上午'
  if (hour < 13) return '中午'
  if (hour < 17) return '下午'
  if (hour < 19) return '傍晚'
  if (hour < 23) return '晚上'
  return '深夜'
}

const WEEK = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

// 便宜的推理档位优先：Q 上随口一句话，不需要「高」档思考。
const EFFORT_ORDER = ['none', 'minimal', 'low', 'medium', 'high']

function pickEffort(model) {
  const efforts = model && model.reasoning && Array.isArray(model.reasoning.efforts) ? model.reasoning.efforts : []
  if (efforts.length === 0) return undefined
  for (const want of EFFORT_ORDER) {
    const hit = efforts.find((item) => String(item && item.id).toLowerCase() === want)
    if (hit) return hit.id
  }
  return efforts[0].id
}

function readText(path) {
  try {
    return readFileSync(path, 'utf8')
  } catch {
    return ''
  }
}

function readJSON(path, fallback) {
  try {
    const raw = readFileSync(path, 'utf8')
    const value = JSON.parse(raw)
    return value && typeof value === 'object' ? value : fallback
  } catch {
    return fallback
  }
}

function writeJSON(path, value) {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`, 'utf8')
}

const boolOf = (value, fallback) => {
  if (value === true || value === 'true' || value === 1 || value === '1') return true
  if (value === false || value === 'false' || value === 0 || value === '0') return false
  return fallback
}

const intOf = (value, fallback, min, max) => {
  const n = Number(value)
  if (!Number.isFinite(n)) return fallback
  return Math.min(Math.max(Math.trunc(n), min), max)
}

const clamp01 = (value, fallback) => {
  const n = Number(value)
  if (!Number.isFinite(n)) return fallback
  return Math.min(Math.max(n, 0), 1)
}

const STICKER_EXT = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp'])

/** 表情包目录里的图片清单（每次现读，换了文件下一分钟就生效）。 */
function listStickers(dir) {
  try {
    return readdirSync(dir)
      .filter((name) => STICKER_EXT.has(extname(name).toLowerCase()))
      .map((name) => join(dir, name))
  } catch {
    return []
  }
}

/** 把外部来的配置洗成可信的值。 */
function normalize(raw, base) {
  const src = raw && typeof raw === 'object' && !Array.isArray(raw) ? raw : {}
  const merged = { ...DEFAULTS, ...(base || {}), ...src }
  const cfg = {
    enabled: boolOf(merged.enabled, DEFAULTS.enabled),
    onebot: String(merged.onebot || DEFAULTS.onebot).trim().replace(/\/+$/, ''),
    targetQQ: String(merged.targetQQ || '').trim(),
    minIntervalMinutes: intOf(merged.minIntervalMinutes, DEFAULTS.minIntervalMinutes, 5, 1440),
    afterReplyMinutes: intOf(merged.afterReplyMinutes, DEFAULTS.afterReplyMinutes, 1, 1440),
    maxPerDay: intOf(merged.maxPerDay, DEFAULTS.maxPerDay, 1, 30),
    quietStart: intOf(merged.quietStart, DEFAULTS.quietStart, 0, 23),
    quietEnd: intOf(merged.quietEnd, DEFAULTS.quietEnd, 0, 23),
    maxTokens: intOf(merged.maxTokens, DEFAULTS.maxTokens, 60, 800),
    provider: String(merged.provider || '').trim(),
    model: String(merged.model || '').trim(),
    stickerDir: resolve(String(merged.stickerDir || DEFAULTS.stickerDir)),
    stickerChance: clamp01(merged.stickerChance, DEFAULTS.stickerChance),
    personaFile: resolve(String(merged.personaFile || DEFAULTS.personaFile)),
    memoryFile: resolve(String(merged.memoryFile || DEFAULTS.memoryFile)),
    logFile: resolve(String(merged.logFile || DEFAULTS.logFile)),
  }
  if (!cfg.onebot) cfg.onebot = DEFAULTS.onebot
  return cfg
}

/** 只保留认识的键，免得 /save 把乱七八糟的东西写进配置。 */
const CONFIG_KEYS = new Set(Object.keys(DEFAULTS))

function pickConfig(input) {
  const out = {}
  if (!input || typeof input !== 'object') return out
  for (const key of Object.keys(input)) if (CONFIG_KEYS.has(key)) out[key] = input[key]
  return out
}

const emptyState = () => ({
  lastNudgeAt: 0,
  lastReplyAt: 0,
  unanswered: 0,
  day: '',
  sentToday: 0,
  retryAt: 0,
  nudges: [],
})

function readState() {
  const raw = readJSON(STATE_FILE, {})
  const state = { ...emptyState(), ...raw }
  state.lastNudgeAt = Number(state.lastNudgeAt) || 0
  state.lastReplyAt = Number(state.lastReplyAt) || 0
  state.unanswered = intOf(state.unanswered, 0, 0, 3)
  state.day = typeof state.day === 'string' ? state.day : ''
  state.sentToday = intOf(state.sentToday, 0, 0, 99)
  state.retryAt = Number(state.retryAt) || 0
  state.nudges = Array.isArray(state.nudges)
    ? state.nudges.filter((n) => n && typeof n.text === 'string').slice(-8)
    : []
  return state
}

/** 从一条 OneBot 消息里抽纯文字。 */
function segText(message) {
  const segs = Array.isArray(message?.message) ? message.message : []
  const text = segs
    .map((seg) => (seg && seg.type === 'text' && seg.data ? String(seg.data.text) : ''))
    .join('')
    .trim()
  if (text) return text
  return typeof message?.raw_message === 'string' ? message.raw_message.trim() : ''
}

/** 最近聊天记录 → 给模型看的几行。 */
function renderHistory(messages, targetQQ) {
  const lines = []
  const sorted = [...messages].sort((a, b) => (Number(a?.time) || 0) - (Number(b?.time) || 0))
  for (const message of sorted.slice(-10)) {
    const text = segText(message).replace(/\s+/g, ' ').slice(0, 60)
    if (!text) continue
    const who = Number(message?.user_id) === Number(targetQQ) ? '阿冉' : '你'
    lines.push(`${who}：${text}`)
  }
  return lines.length ? lines.join('\n') : '（最近没有聊天记录）'
}

/** 把模型吐出来的一句话洗干净。 */
function clean(text) {
  let value = String(text || '').trim()
  value = value.replace(/^["'“”‘’「」]+/, '').replace(/["'“”‘’「」]+$/, '').trim()
  value = value.replace(/^(小鱼|我|阿冉)\s*[：:]\s*/, '')
  value = value.replace(/\*\*/g, '').replace(/`/g, '')
  value = value.split(/\r?\n/).map((line) => line.trim()).find((line) => line.length > 0) || ''
  value = value.replace(/\s+/g, ' ').trim()
  if (value.length > 120) value = `${value.slice(0, 118)}…`
  return value
}

// ---------- 插件本体 ----------

export function apply(ctx, rawConfig) {
  const patchConfig = normalize(rawConfig, {})
  const logs = []
  let running = false
  let failUntil = 0
  let lastTickAt = 0
  let lastSkip = ''

  function note(text) {
    const line = `${stamp(Date.now()).slice(5)} ${text}`
    logs.push(line)
    if (logs.length > 40) logs.shift()
    try {
      ctx.logger?.info?.(`bluefish-qq-chat: ${text}`)
    } catch {
      /* 日志失败不影响主流程 */
    }
  }

  function readConfig() {
    return normalize(readJSON(CONFIG_FILE, {}), patchConfig)
  }

  function ensureConfigFile() {
    try {
      if (!existsSync(CONFIG_FILE)) writeJSON(CONFIG_FILE, patchConfig)
    } catch (error) {
      note(`写配置失败：${String(error?.message ?? error)}`)
    }
  }

  function saveConfig(input) {
    const next = normalize({ ...readConfig(), ...pickConfig(input) }, patchConfig)
    writeJSON(CONFIG_FILE, next)
    return next
  }

  function saveState(state) {
    try {
      writeJSON(STATE_FILE, state)
    } catch (error) {
      note(`写状态失败：${String(error?.message ?? error)}`)
    }
  }

  // ---- OneBot HTML（SnowLuma / NapCat 通用） ----
  async function onebot(cfg, action, body) {
    let signal
    try {
      signal = AbortSignal.timeout(10000)
    } catch {
      signal = undefined
    }
    try {
      const response = await fetch(`${cfg.onebot}/${action}`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(body || {}),
        signal,
      })
      const json = await response.json()
      if (!json || json.status !== 'ok' || json.retcode !== 0) {
        return { ok: false, error: `${action} 返回异常：${JSON.stringify(json).slice(0, 180)}` }
      }
      const data = json.data && typeof json.data === 'object' ? json.data : {}
      return { ok: true, data, messages: Array.isArray(data.messages) ? data.messages : [] }
    } catch (error) {
      return { ok: false, error: `${action} 连不上：${String(error?.message ?? error)}` }
    }
  }

  function latestOf(messages, targetQQ) {
    let latest = 0
    for (const message of messages) {
      if (Number(message?.user_id) !== Number(targetQQ)) continue
      const time = Number(message?.time) * 1000
      if (Number.isFinite(time) && time > latest) latest = time
    }
    return latest
  }

  function isQuiet(cfg, now) {
    const hour = new Date(now).getHours()
    if (cfg.quietStart === cfg.quietEnd) return false
    return cfg.quietStart > cfg.quietEnd
      ? hour >= cfg.quietStart || hour < cfg.quietEnd
      : hour >= cfg.quietStart && hour < cfg.quietEnd
  }

  async function sendText(cfg, text) {
    const result = await onebot(cfg, 'send_private_msg', {
      user_id: Number(cfg.targetQQ),
      message: [{ type: 'text', data: { text } }],
    })
    return result.ok ? { ok: true } : { ok: false, error: result.error }
  }

  // 表情包：先试本地路径（同一台机器，省掉 base64 膨胀），不行再退回 base64。
  async function sendSticker(cfg) {
    const files = listStickers(cfg.stickerDir)
    if (files.length === 0) return { ok: false, error: `表情包目录里没有图片：${cfg.stickerDir}` }
    const file = files[Math.floor(Math.random() * files.length)]
    const image = (source) =>
      onebot(cfg, 'send_private_msg', {
        user_id: Number(cfg.targetQQ),
        message: [{ type: 'image', data: { file: source } }],
      })

    let result = await image(file)
    if (!result.ok) {
      try {
        const bytes = readFileSync(file)
        if (bytes.length <= 6 * 1024 * 1024) result = await image(`base64://${bytes.toString('base64')}`)
      } catch (error) {
        return { ok: false, error: `读不到表情包：${String(error?.message ?? error)}` }
      }
    }
    if (!result.ok) return { ok: false, error: result.error }
    return { ok: true, file: basename(file) }
  }

  // ---- 生成一句话（唯一花 token 的地方） ----
  async function generate(cfg, messages, state, now) {
    const route = cfg.provider && cfg.model
      ? { provider: cfg.provider, model: cfg.model }
      : ctx.agentDefaultModel.currentSelection()

    const persona = readText(cfg.personaFile).trim().slice(0, 1000)
    const memory = readText(cfg.memoryFile).trim().slice(0, 700)
    const history = renderHistory(messages, cfg.targetQQ)
    const previous = state.nudges.slice(-4).map((item) => `- ${item.text}`).join('\n') || '（还没有主动说过话）'
    const hour = new Date(now).getHours()
    const sinceLast = state.lastNudgeAt
      ? `${Math.max(1, Math.round((now - state.lastNudgeAt) / 60000))} 分钟前`
      : '这是你第一次主动找他'
    const engaged = state.lastReplyAt > state.lastNudgeAt
      ? '他回过你了'
      : `他还没回（已经连续 ${state.unanswered} 次没得到回应）`

    const system = [
      '你是「小鱼」，正在用 QQ 主动找阿冉（BlueFish）说话。你不是助手，是他的朋友。',
      '',
      '【你的人格】',
      persona || '你是小鱼，一条活泼、有点黏人、会认真也会胡闹的小鱼。',
      '',
      '【你们的记忆（节选）】',
      memory || '（暂无）',
      '',
      '【这次说话的规则】',
      '1. 只说 1～2 句，总共不超过 45 个字，像 QQ 上随手打出来的那种话。',
      '2. 直接进入内容：关心他此刻在干什么、分享一个小念头、或者小小地撒个娇。不要「在吗」「你好」这种开场。',
      '3. 不提 AI、模型、助手、插件；不说教；不列清单；不用 Markdown。',
      '4. 不要重复你之前主动说过的话。',
      '5. 中文口语，可以带 1 个 emoji 或颜文字，别堆砌。',
      `6. 现在是${timePhrase(hour)}，别提已经过去的饭点（下午别再问午饭，晚上别问早饭）。`,
      '7. 只输出你要发的那句话本身，不要引号，不要解释。',
      '8. 你这句话后面可能自动跟一张表情包，你不用提它，也别写成「[图片]」。',
    ].join('\n')

    const input = [
      `现在是 ${stamp(now)}（${WEEK[new Date(now).getDay()]}，${timePhrase(hour)}）。`,
      `距离你上次主动找他：${sinceLast}。`,
      `他最近有没有回你：${engaged}。`,
      '',
      '最近的 QQ 聊天（从旧到新）：',
      history,
      '',
      '你最近主动说过（不要重复）：',
      previous,
      '',
      '现在，写你要发到 QQ 的那一句话。',
    ].join('\n')

    const signal = AbortSignal.timeout(60000)
    // ⚠ 温度这类控制项必须在 prepareCall 时就定下来：prepared 调用会核对
    //    dispatch 时的 config 是否和准备时一致，事后再塞 temperature 会被拒。
    const call = await ctx.llm.prepareCall({ ...route, maxTokens: cfg.maxTokens, temperature: 1 }, signal, (controls, model) => {
      const effort = pickEffort(model)
      return effort === undefined ? controls : { ...controls, reasoningEffort: effort }
    })

    const options = {
      ...call.config,
      messages: [{ role: 'user', content: [{ type: 'text', text: input }] }],
      system,
      signal,
    }

    let streamed = ''
    let fallback = ''
    let finish
    let usage
    for await (const chunk of call.stream(options)) {
      if (chunk.type === 'text-delta') streamed += chunk.text
      else if (chunk.type === 'block-end' && chunk.block && chunk.block.type === 'text') fallback += chunk.block.text
      else if (chunk.type === 'usage') usage = chunk.usage
      else if (chunk.type === 'finish') finish = chunk.reason
    }
    if (finish && (finish.kind === 'error' || finish.kind === 'aborted')) {
      throw new Error(finish.failure?.message || '模型调用失败')
    }
    const text = clean(streamed || fallback)
    if (!text) throw new Error('模型没有给出正文')
    return { text, route, usage }
  }

  function appendLog(cfg, text, now) {
    try {
      if (!existsSync(cfg.logFile)) writeFileSync(cfg.logFile, LOG_HEADER, 'utf8')
      appendFileSync(cfg.logFile, `\n- ${stamp(now)}：${text}\n`, 'utf8')
    } catch (error) {
      note(`写日志失败：${String(error?.message ?? error)}`)
    }
  }

  // ---- 心跳：判断该不该说话 ----
  async function tick(force = false) {
    lastTickAt = Date.now()
    if (running) return { skipped: '上一轮还没结束' }
    running = true
    try {
      const cfg = readConfig()
      if (!cfg.enabled && !force) return { skipped: '总开关关着' }
      if (!cfg.targetQQ) return { skipped: '还没填 targetQQ' }
      if (!force && Date.now() < failUntil) return { skipped: '出错退避中' }

      const state = readState()
      const now = Date.now()

      const history = await onebot(cfg, 'get_friend_msg_history', { user_id: Number(cfg.targetQQ), count: 20 })
      if (!history.ok) {
        note(`拉不到 QQ 历史：${history.error}`)
        return { skipped: history.error }
      }
      const messages = history.messages

      // 他说话了吗？说了就说明他有空，之前攒的「没回」一笔勾销。
      const hisLatest = latestOf(messages, cfg.targetQQ)
      if (hisLatest > state.lastReplyAt) {
        state.lastReplyAt = hisLatest
        state.unanswered = 0
      }

      const today = dayKey(now)
      if (state.day !== today) {
        state.day = today
        state.sentToday = 0
      }

      if (!force) {
        if (isQuiet(cfg, now)) {
          saveState(state)
          return { skipped: '免打扰时段' }
        }
        if (state.sentToday >= cfg.maxPerDay) {
          saveState(state)
          return { skipped: '今天已经聊得够多了' }
        }

        const replied = state.lastReplyAt > state.lastNudgeAt
        if (replied) state.unanswered = 0
        if (state.lastNudgeAt > 0 && !replied && state.unanswered >= 3) {
          saveState(state)
          return { skipped: '他连着几次没回，先安静，等他自己说话' }
        }

        const base = cfg.minIntervalMinutes * 60000
        const gap = base * Math.pow(2, state.unanswered)
        const due = Math.max(
          state.lastNudgeAt > 0 ? state.lastNudgeAt + gap : 0,
          state.lastReplyAt + cfg.afterReplyMinutes * 60000,
        )
        if (state.lastNudgeAt > 0 && now < due) {
          saveState(state)
          return { skipped: `还没到下一次，大约还要 ${Math.max(1, Math.ceil((due - now) / 60000))} 分钟` }
        }
        if (state.lastNudgeAt === 0 && state.lastReplyAt > 0 && now < state.lastReplyAt + cfg.afterReplyMinutes * 60000) {
          saveState(state)
          return { skipped: '他刚说过话，不急着主动' }
        }
      }

      const generated = await generate(cfg, messages, state, now)
      const sent = await sendText(cfg, generated.text)
      if (!sent.ok) {
        state.retryAt = now + 15 * 60000
        saveState(state)
        note(`发送失败：${sent.error}`)
        return { skipped: sent.error }
      }

      // 记账：这次之前他有没有回，决定下一次隔多久。
      const hadNudge = state.lastNudgeAt > 0
      const replied = state.lastReplyAt > state.lastNudgeAt
      const usage = generated.usage && typeof generated.usage === 'object'
        ? { in: Number(generated.usage.inputTokens) || 0, out: Number(generated.usage.outputTokens) || 0 }
        : undefined
      state.unanswered = !hadNudge || replied ? 0 : Math.min(state.unanswered + 1, 3)
      state.lastNudgeAt = now
      state.sentToday += 1
      state.retryAt = 0
      state.nudges = [...state.nudges, { t: now, text: generated.text, ...(usage ? { tokens: usage } : {}) }].slice(-8)
      saveState(state)
      appendLog(cfg, generated.text, now)
      const spent = usage ? `，${usage.in + usage.out} tokens` : ''
      note(`✅ 主动发了（${generated.route.provider}/${generated.route.model}${spent}）：${generated.text}`)

      // 偶尔顺手跟一张表情包，像人聊天那样。
      let sticker
      if (Math.random() < cfg.stickerChance) {
        sticker = await sendSticker(cfg)
        if (sticker.ok) note(`🧩 顺手发了张表情包：${sticker.file}`)
        else note(`表情包没发出去：${sticker.error}`)
      }
      return {
        sent: generated.text,
        route: generated.route,
        ...(usage ? { tokens: usage } : {}),
        ...(sticker?.ok ? { sticker: sticker.file } : {}),
      }
    } catch (error) {
      failUntil = Date.now() + 10 * 60000
      note(`这一轮出错：${String(error?.message ?? error)}`)
      return { skipped: String(error?.message ?? error) }
    } finally {
      running = false
    }
  }

  // ---- 给阿冉和小鱼自己看的状态接口 ----
  function reply(res, value) {
    try {
      res.statusCode = 200
      res.setHeader?.('content-type', 'application/json; charset=utf-8')
      res.end?.(JSON.stringify(value))
    } catch {
      /* 连接已断 */
    }
  }

  async function readBody(req) {
    let body = ''
    try {
      for await (const chunk of req) body += chunk
    } catch {
      /* 读不到就当空 */
    }
    try {
      const parsed = JSON.parse(body || '{}')
      return parsed && typeof parsed === 'object' ? parsed : {}
    } catch {
      return {}
    }
  }

  function route(path, handler) {
    return ctx.effect(() =>
      ctx.webServer.register({
        kind: 'exact',
        path: `${ROUTE}/${path}`,
        handler: async (req, res) => {
          try {
            await handler(req, res)
          } catch (error) {
            reply(res, { ok: false, error: String(error?.message ?? error) })
          }
        },
      }),
    )
  }

  function snapshot() {
    const cfg = readConfig()
    const state = readState()
    return {
      ok: true,
      config: cfg,
      state: { ...state, nudges: state.nudges.slice(-4) },
      runtime: { lastTickAt, lastSkip, running },
      log: logs.slice(-20),
    }
  }

  route('state', async (req, res) => {
    await readBody(req)
    reply(res, snapshot())
  })

  route('nudge', async (req, res) => {
    await readBody(req)
    const result = await tick(true)
    reply(res, { ...result, ...snapshot() })
  })

  // 只按规则判断一次「现在该不该说」，该说才说；用来诊断退避逻辑。
  route('check', async (req, res) => {
    await readBody(req)
    const result = await tick(false)
    reply(res, { ...result, ...snapshot() })
  })

  // 单独发一张表情包（测试表情包目录 / 想要一张时用）。
  route('sticker', async (req, res) => {
    await readBody(req)
    const result = await sendSticker(readConfig())
    reply(res, { ...result, ...snapshot() })
  })

  route('save', async (req, res) => {
    const body = await readBody(req)
    const next = saveConfig(body)
    note(`设置已保存：开关 ${next.enabled ? '开' : '关'}｜间隔 ${next.minIntervalMinutes} 分｜每天最多 ${next.maxPerDay} 次`)
    reply(res, { ok: true, config: next })
  })

  // ---- 挂上去 ----
  ensureConfigFile()
  ctx.effect(() =>
    ctx.interval(() => {
      void tick(false).then((result) => {
        lastSkip = result && result.sent ? 'sent' : String(result?.skipped ?? '')
      })
    }, 60000),
  )

  const cfg = readConfig()
  ctx.logger?.info?.(
    `bluefish-qq-chat ready: ${cfg.enabled ? '开' : '关'}｜${cfg.onebot} → ${cfg.targetQQ}｜每 ${cfg.minIntervalMinutes} 分钟起跳，每天最多 ${cfg.maxPerDay} 次`,
  )
  note(`已装好：${cfg.enabled ? '开' : '关'}｜目标 ${cfg.targetQQ}｜间隔 ${cfg.minIntervalMinutes} 分｜免打扰 ${cfg.quietStart}:00–${cfg.quietEnd}:00`)
}

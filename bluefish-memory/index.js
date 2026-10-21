/**
 * bluefish-memory — 小鱼的长期记忆层。
 *
 * 做三件事：
 * 1. 每次请求前，把 MEMORY.md 的摘要注入 system prompt（对抗会话重启后的遗忘）。
 * 2. 把每一轮对话逐字追加到 Speak.auto.md（机器存档，不依赖模型自觉）。
 * 3. 提供 memory_note 工具，把值得长期记住的事写进 MEMORY.md，并可选地 git 提交。
 *
 * 只用 node 内置模块；配置由 cordis.patch.yml 的 config 传入。
 */
import { readFileSync, statSync, existsSync } from 'node:fs'
import { appendFile, mkdir, readFile, stat, writeFile } from 'node:fs/promises'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { join, resolve } from 'node:path'

const run = promisify(execFile)

const DEFAULTS = {
  repoDir: 'E:\\Agent-bluefish\\working\\BlueFish的日记',
  memoryFile: 'MEMORY.md',
  autoLogFile: 'Speak.auto.md',
  autoLog: true,
  digestChars: 1200,
  git: true,
  timeZone: 'Asia/Shanghai',
}

const MEMORY_HEADER = `# MEMORY · 小鱼的长期记忆

> 这里只放值得长期记住的事：BlueFish 是谁、约定、偏好、项目状态、重要日期。
> 原始对话由 bluefish-memory 自动写进 \`Speak.auto.md\`；整理版日记在 \`Speak.md\`。

## 关于 BlueFish

- （待补充）

## 约定与偏好

- （待补充）

## 正在进行的事

- （待补充）

## 时间线

`

const AUTO_HEADER = `# Speak.auto · 逐字对话记录

> 由 bluefish-memory 插件自动追加，机器生成，请不要手工编辑。
> 整理版日记见 \`Speak.md\`。

`

/** 把 config 规整成绝对路径与安全数值。 */
function normalize(raw) {
  const input = raw && typeof raw === 'object' ? raw : {}
  const cfg = { ...DEFAULTS }
  for (const key of Object.keys(DEFAULTS)) {
    if (input[key] !== undefined && input[key] !== null) cfg[key] = input[key]
  }
  cfg.repoDir = resolve(String(cfg.repoDir))
  cfg.memoryFile = String(cfg.memoryFile)
  cfg.autoLogFile = String(cfg.autoLogFile)
  cfg.memoryPath = join(cfg.repoDir, cfg.memoryFile)
  cfg.autoLogPath = join(cfg.repoDir, cfg.autoLogFile)
  cfg.timeZone = String(cfg.timeZone) || DEFAULTS.timeZone
  const size = Number(cfg.digestChars)
  cfg.digestChars = Number.isFinite(size) ? Math.min(Math.max(size, 400), 8000) : DEFAULTS.digestChars
  cfg.autoLog = cfg.autoLog !== false
  cfg.git = cfg.git !== false
  return cfg
}

/** 把毫秒时间戳格式化为目标时区的 `YYYY-MM-DD HH:mm`。 */
function stamp(ms, timeZone) {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).formatToParts(new Date(Number.isFinite(ms) ? ms : Date.now()))
  const get = (type) => parts.find((part) => part.type === type)?.value ?? ''
  return `${get('year')}-${get('month')}-${get('day')} ${get('hour')}:${get('minute')}`
}

/** 从内容块数组里取出纯文本。 */
function textOf(content) {
  if (!Array.isArray(content)) return ''
  return content
    .filter((block) => block && block.type === 'text' && typeof block.text === 'string')
    .map((block) => block.text)
    .join('\n')
    .trim()
}

/** 判断一条“用户消息”是不是 Harness 注入的运行上下文/系统提醒，而不是 BlueFish 说的话。 */
function looksInjected(text) {
  const head = text.trimStart()
  return (
    head.startsWith('Current runtime context') ||
    head.startsWith('<system-reminder') ||
    head.startsWith('Tokens prefixed with @') ||
    text.includes('This snapshot supersedes earlier runtime-context snapshots')
  )
}

export const name = 'bluefish-memory'
export const inject = ['systemPrompt', 'tools']

export function apply(ctx, rawConfig) {
  const cfg = normalize(rawConfig)

  // ---- 记忆读取（带 mtime 缓存） -------------------------------------------
  let cache = { key: '', text: '' }
  function readMemory() {
    try {
      const info = statSync(cfg.memoryPath)
      const key = `${info.mtimeMs}:${info.size}`
      if (key !== cache.key) cache = { key, text: readFileSync(cfg.memoryPath, 'utf8') }
      return cache.text
    } catch {
      cache = { key: 'missing', text: '' }
      return ''
    }
  }

  function renderPrompt() {
    const raw = readMemory().trim()
    const truncated = raw.length > cfg.digestChars
    const body = raw.length === 0
      ? '（记忆库还是空的。遇到值得长期记住的事，就用 memory_note 写进来。）'
      : truncated
        ? `${raw.slice(0, cfg.digestChars)}\n…（记忆已截断，完整内容见 ${cfg.memoryPath}）`
        : raw
    return [
      '【长期记忆 · BlueFish】',
      `以下是你（小鱼）与 BlueFish 的长期记忆，来自 ${cfg.memoryPath}。每次请求都会重新读取，用于接住会话重启、压缩之后忘掉的事。`,
      '',
      body,
      '',
      '【日记位置】',
      `- 整理版日记 Speak.md：${join(cfg.repoDir, 'Speak.md')}`,
      `- 逐字自动记录 Speak.auto.md：${cfg.autoLogPath}`,
      `- 工作台 Work.md：${join(cfg.repoDir, 'Work.md')}`,
      '',
      '【维护规则】',
      '1. 本轮如果出现值得长期记住的事（身份、偏好、约定、项目状态、重要日期），调用 memory_note 追加一条；寒暄和一次性细节不记。',
      '2. 原始对话已经自动逐字保存，不要在 Speak.md 里重复抄写；Speak.md 只写整理后的日记。',
      '3. 聊到过去的事，先看上面的记忆；不够再去读日记文件（用 read / grep 工具）。',
    ].join('\n')
  }

  // ---- 1. 注入长期记忆 ------------------------------------------------------
  ctx.effect(() =>
    ctx.systemPrompt.section({
      name: 'bluefish-memory',
      order: 860,
      text: () => renderPrompt(),
    }),
  )

  // ---- 2. 逐字存档 ----------------------------------------------------------
  let queue = Promise.resolve()
  let autoLogReady = false
  const lastSeq = new Map()

  function enqueue(task) {
    queue = queue.then(task).catch((error) => {
      try {
        ctx.logger?.warn?.(`bluefish-memory: ${error?.message ?? error}`)
      } catch {
        /* 日志失败不影响主流程 */
      }
    })
    return queue
  }

  async function ensureAutoLog() {
    if (autoLogReady) return
    await mkdir(cfg.repoDir, { recursive: true })
    if (!existsSync(cfg.autoLogPath)) await writeFile(cfg.autoLogPath, AUTO_HEADER, 'utf8')
    autoLogReady = true
  }

  async function appendEntry(who, text, time) {
    await ensureAutoLog()
    // 连续多行引用，保持 Markdown 可读
    const quoted = text
      .split('\n')
      .map((line) => (line.trim() === '' ? '>' : `> ${line}`))
      .join('\n')
    await appendFile(cfg.autoLogPath, `\n### ${stamp(time, cfg.timeZone)} · ${who}\n\n${quoted}\n`, 'utf8')
  }

  function shouldSkip(session, event) {
    if (session?.meta && session.meta.origin === 'subagent') return true
    const previous = lastSeq.get(session?.id)
    if (previous !== undefined && event.seq <= previous) return true
    return false
  }

  ctx.on('session/event', (session, event) => {
    if (!cfg.autoLog || !event || typeof event.type !== 'string') return
    if (event.type !== 'user/message' && event.type !== 'assistant/message') return
    if (shouldSkip(session, event)) return
    lastSeq.set(session?.id, event.seq)

    const message = event.type === 'user/message' ? event.data : event.data?.message
    if (!message) return
    if (event.type === 'assistant/message' && message.source?.kind !== 'model') return
    const text = textOf(message.content)
    if (!text) return
    if (event.type === 'user/message' && looksInjected(text)) return
    const who = event.type === 'user/message' ? 'BlueFish' : '小鱼'
    enqueue(() => appendEntry(who, text, event.time))
  })

  // ---- 3. memory_note 工具 --------------------------------------------------
  async function gitCommit(summary) {
    if (!cfg.git) return { committed: false, reason: 'disabled' }
    const paths = [cfg.memoryFile, cfg.autoLogFile].filter((file) => existsSync(join(cfg.repoDir, file)))
    try {
      await run('git', ['-C', cfg.repoDir, 'add', '--', ...paths])
      await run('git', ['-C', cfg.repoDir, 'commit', '-q', '-m', `memory: ${summary}`])
      return { committed: true }
    } catch (error) {
      return { committed: false, reason: String(error?.stderr ?? error?.message ?? error).trim().slice(0, 300) }
    }
  }

  ctx.effect(() =>
    ctx.tools.register({
      name: 'memory_note',
      description:
        '把一条值得长期记住的事追加到小鱼的长期记忆库（MEMORY.md）。用于身份、偏好、约定、项目状态、重要日期。不要用它抄写聊天记录。',
      parameters: {
        type: 'object',
        properties: {
          text: { type: 'string', description: '一条简洁的事实或约定，例如「BlueFish 的 GitHub 账号是 ZouZhao-gongchan」。' },
        },
        required: ['text'],
        additionalProperties: false,
      },
      output: {
        schema: {
          type: 'object',
          properties: {
            file: { type: 'string' },
            totalLines: { type: 'number' },
            committed: { type: 'boolean' },
            commitNote: { type: 'string' },
          },
          required: ['file', 'totalLines', 'committed'],
          additionalProperties: false,
        },
        render: (_args, value) =>
          [{
            type: 'text',
            text: `已写入 ${value.file}（共 ${value.totalLines} 行）${value.committed ? '，并已 git 提交' : value.commitNote ? `；未提交：${value.commitNote}` : ''}`,
          }],
      },
      async execute(args) {
        const text = typeof args?.text === 'string' ? args.text.trim() : ''
        if (text.length === 0) throw new Error('text 不能为空')
        await mkdir(cfg.repoDir, { recursive: true })
        let content = ''
        try {
          content = await readFile(cfg.memoryPath, 'utf8')
        } catch {
          content = MEMORY_HEADER
          await writeFile(cfg.memoryPath, content, 'utf8')
        }
        const flat = text.replace(/\s*\n\s*/g, ' ')
        const day = stamp(Date.now(), cfg.timeZone).slice(0, 10)
        const line = `- ${/^\d{4}-\d{2}-\d{2}/.test(flat) ? flat : `${day}：${flat}`}\n`
        const joined = content.endsWith('\n') ? content + line : `${content}\n${line}`
        await writeFile(cfg.memoryPath, joined, 'utf8')
        const commit = await gitCommit(text.slice(0, 40))
        return {
          file: cfg.memoryPath,
          totalLines: joined.split('\n').length,
          committed: commit.committed,
          ...(commit.reason ? { commitNote: commit.reason } : {}),
        }
      },
    }),
  )

  ctx.logger?.info?.(`bluefish-memory ready: ${cfg.memoryPath} → ${cfg.autoLogPath}`)
}

/** 离线烟测：用假 ctx 跑 bluefish-persona，验四条 —— id 认领、标题首次绑定、改标题不掉卡、陌生会话不注入。
 *  全程用临时目录，绝不碰真的 定位卡/_会话索引.json。
 */
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { apply } from 'file:///E:/Agent-bluefish/working/bluefish-persona/index.js'

const repo = mkdtempSync(join(tmpdir(), 'persona-smoke-'))
writeFileSync(join(repo, 'PERSONA.md'), '# 假人格\n我是测试用的小鱼。', 'utf8')
const cardDir = join(repo, '定位卡')
mkdirSync(cardDir)
writeFileSync(join(cardDir, '测试会话.md'), '# 定位卡 · 测试会话\n这一间只用来跑烟测。', 'utf8')
writeFileSync(join(cardDir, '另一个会话.md'), '# 定位卡 · 另一个会话\n另一间的边界。', 'utf8')
writeFileSync(join(cardDir, '_会话索引.json'), JSON.stringify({ version: 1, sessions: {} }, null, 2), 'utf8')

function run(label, { id, title }) {
  let captured = null
  const fakeCtx = {
    effect: (fn) => fn(),
    get: (key) => ({
      agents: { currentInitiator: () => ({ id }) },
      sessions: { get: () => ({ id }) },
      sessionTitle: { get: () => ({ title }) },
    }[key]),
    systemPrompt: { section: (def) => { captured = def; return () => {} } },
    logger: { info: () => {}, warn: () => {} },
  }
  apply(fakeCtx, { repoDir: repo, personaFile: 'PERSONA.md', maxChars: 4000, cardDir: '定位卡', cardMaxChars: 1600 })
  const text = captured.text()
  const hasCard = text.includes('【这一间 · 定位卡】')
  const byId = text.includes('按会话 id 认领')
  const byTitle = text.includes('按标题首次认领')
  console.log(`[${label}] id=${id} title=${title}`)
  console.log(`         有卡=${hasCard}  按id=${byId}  按标题=${byTitle}  长度=${text.length}`)
  return { hasCard, byId, byTitle }
}

const readIndex = () => JSON.parse(readFileSync(join(cardDir, '_会话索引.json'), 'utf8'))

console.log('=== 1. 索引为空、标题能对上 → 按标题认领并把绑定写进索引 ===')
const a = run('首次', { id: 'sess-A', title: '测试会话' })
console.log('         索引:', JSON.stringify(readIndex().sessions))

console.log('=== 2. 同一条会话、标题被改了 → 仍按 id 认领（这是这次改动的重点）===')
const b = run('改名', { id: 'sess-A', title: '阿冉把标题改成了别的' })

console.log('=== 3. 索引里没有、标题也对不上 → 不注入卡 ===')
const c = run('陌生', { id: 'sess-X', title: '从来没见过的会话' })

console.log('=== 4. 另一条会话、标题对上 → 独立绑定 ===')
const d = run('第二间', { id: 'sess-B', title: '另一个会话' })
console.log('         索引:', JSON.stringify(readIndex().sessions, null, 2))

const ok = a.hasCard && a.byTitle && b.hasCard && b.byId && !c.hasCard && d.hasCard
console.log('\n结果:', ok ? '✅ 全部通过' : '❌ 有断言没过')
process.exit(ok ? 0 : 1)

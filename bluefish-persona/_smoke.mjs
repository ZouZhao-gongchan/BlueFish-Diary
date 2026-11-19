/** 离线烟测：用假 ctx 跑一遍 bluefish-persona，看看人格和定位卡能不能拼出来。 */
import { apply } from 'file:///E:/Agent-bluefish/working/bluefish-persona/index.js'

let captured = null
const title = process.argv[2] ?? 'B站和插件更新'

const fakeCtx = {
  effect: (fn) => fn(),
  get: (key) => {
    const table = {
      agents: { currentInitiator: () => ({ id: 'sess-demo' }) },
      sessions: { get: () => ({ id: 'sess-demo' }) },
      sessionTitle: { get: () => ({ title }) },
    }
    return table[key]
  },
  systemPrompt: {
    section: (def) => {
      captured = def
      return () => {}
    },
  },
  logger: { info: () => {} },
}

apply(fakeCtx, {
  repoDir: 'E:\\Agent-bluefish\\working\\BlueFish的日记',
  personaFile: 'PERSONA.md',
  maxChars: 4000,
  cardDir: '定位卡',
  cardMaxChars: 1600,
})

const text = captured.text()
console.log('=== 标题 ===', title)
console.log('=== 总长 ===', text.length)
console.log('=== 有没有卡 ===', text.includes('【这一间 · 定位卡】'))
console.log('=== 尾巴 700 字 ===')
console.log(text.slice(-700))

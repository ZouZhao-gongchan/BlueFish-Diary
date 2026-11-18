import fs from 'node:fs'

const file = 'C:/Users/FIshKiller/.dsh/bili-duty/config.json'
const config = JSON.parse(fs.readFileSync(file, 'utf8'))

config.keywords = ['音乐现场 4K', '宅舞', '游戏实况 解说']
config.perDay = 2

fs.writeFileSync(file, `${JSON.stringify(config, null, 2)}\n`, 'utf8')
console.log(JSON.stringify({ keywords: config.keywords, perDay: config.perDay }, null, 2))

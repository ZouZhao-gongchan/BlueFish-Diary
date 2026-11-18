import fs from 'node:fs'

const file = 'C:/Users/FIshKiller/.dsh/bili-duty/config.json'
const config = JSON.parse(fs.readFileSync(file, 'utf8'))
config.dshBin = 'E:\\deepseek\\resources\\app.asar\\dsh\\node_modules\\@deepseek-ai\\dsh\\lib\\bin.js'
fs.writeFileSync(file, `${JSON.stringify(config, null, 2)}\n`, 'utf8')
console.log(JSON.stringify(config.dshBin))

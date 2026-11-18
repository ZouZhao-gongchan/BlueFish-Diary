import fs from 'node:fs'
const b = fs.readFileSync('E:/deepseek/resources/app.asar')
const headerLen = b.readUInt32LE(4) - 8
const H = JSON.parse(b.slice(16, 16 + headerLen).toString('utf8'))
const pkgs = Object.keys(H.files.dsh.files.node_modules.files['@deepseek-ai'].files)
console.log(pkgs.filter(x => /app-boot|dsh-tools$|schemastery/.test(x)).join('\n'))

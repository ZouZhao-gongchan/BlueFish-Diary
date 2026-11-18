import fs from 'node:fs'
import path from 'node:path'
const root = 'E:/Agent-bluefish/Save/dsh-home/profiles/desktop/node_modules'
const counts = new Map()
const dirs = fs.readdirSync(root, { withFileTypes: true }).filter(d => d.isDirectory() && !d.name.startsWith('.'))
for (const d of dirs) {
  let files = []
  if (d.name.startsWith('@')) {
    for (const sub of fs.readdirSync(path.join(root, d.name), { withFileTypes: true })) {
      if (!sub.isDirectory()) continue
      files.push(...['index.js', 'client.js'].map(f => path.join(root, d.name, sub.name, f)))
    }
  } else {
    files = ['index.js', 'client.js'].map(f => path.join(root, d.name, f))
  }
  for (const f of files) {
    if (!fs.existsSync(f)) continue
    const txt = fs.readFileSync(f, 'utf8')
    const re = /name:\s*'([a-z][a-z0-9_]{2,40})'/g
    let m
    while ((m = re.exec(txt))) {
      const n = m[1]
      if (!counts.has(n)) counts.set(n, new Set())
      counts.get(n).add(d.name.startsWith('@') ? d.name + '/' + path.basename(path.dirname(f)) : d.name)
    }
  }
}
const dup = [...counts].filter(([, v]) => v.size > 1)
console.log('duplicate candidate names:', dup.length)
for (const [n, v] of dup.slice(0, 40)) console.log(n, '->', [...v].join(', '))

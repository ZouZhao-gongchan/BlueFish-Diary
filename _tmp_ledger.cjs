const fs = require('fs')
const l = JSON.parse(fs.readFileSync('C:/Users/FIshKiller/.dsh/storages/cost-meter/ledger.json', 'utf8'))
const d = l.days['2026-10-24']
const rows = (d.sessions || []).map(s => ({ id: s.id.slice(0, 20), title: (s.title || '').slice(0, 30), cny: +(s.costCny || 0).toFixed(3), calls: s.calls, cacheRead: s.cacheRead }))
rows.sort((a, b) => b.cny - a.cny)
console.log('day total CNY:', d.costCny.toFixed(3), 'calls:', d.calls)
for (const r of rows) console.log(r.cny, 'CNY |', r.calls, 'calls | cacheRead', r.cacheRead, '|', r.id, '|', r.title)

import fs from 'node:fs'
import Module from 'node:module'

const profile = 'C:/Users/FIshKiller/.dsh/profiles/desktop'
const pkg = JSON.parse(fs.readFileSync(`${profile}/package.json`, 'utf8'))
const req = Module.createRequire(`${profile}/package.json`)
const missing = []
for (const name of Object.keys(pkg.dependencies)) {
  try {
    req.resolve(name)
  } catch {
    missing.push(name)
  }
}
console.log(JSON.stringify({ total: Object.keys(pkg.dependencies).length, missing }, null, 2))

import { loadCred, listSessions, fetchMsgs } from 'file:///E:/Agent-bluefish/Save/dsh-home/profiles/desktop/node_modules/dsh-bili-scroll/lib/dm.mjs'

const stateDir = 'C:/Users/FIshKiller/.dsh/bili-duty'
const cred = loadCred(stateDir)
if (!cred) { console.log('no credential'); process.exit(0) }
const sessions = await listSessions(cred)
console.log('conversations:', sessions.length)
for (const s of sessions.slice(0, 5)) {
  const msgs = await fetchMsgs(cred, s.uid, 6)
  console.log('--- uid', s.uid, 'unread', s.unread, '|', s.preview.slice(0, 40))
  for (const m of msgs.slice(-4)) console.log('   ', m.fromMe ? 'me >' : 'him>', m.text.slice(0, 80))
}

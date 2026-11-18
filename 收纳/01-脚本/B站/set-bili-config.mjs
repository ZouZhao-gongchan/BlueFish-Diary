import fs from 'node:fs'

const file = 'C:/Users/FIshKiller/.dsh/bili-duty/config.json'
const config = JSON.parse(fs.readFileSync(file, 'utf8'))

Object.assign(config, {
  // 只在谷时跑：工作日 12–14 与 18:00 之后；周末整体算谷时
  peakValley: true,
  noon: true,
  night: true,
  // 先跑 1 条验收，之后可以调回 2
  perDay: 1,
  // 有真见解才评论，并 @ 阿冉
  autoComment: true,
  commentPerRound: 1,
  mentionName: '杀鱼佬不会遇见鲨鱼',
  // 楼中楼：适当回复；阿冉的回复必须回
  replyToComments: true,
  replyPerRound: 2,
  // 桌面版 dsh 的 CLI 入口
  dshBin: 'E:\\deepseek\\resources\\app.asar\\dsh\\node_modules\\@deepseek-ai\\dsh\\lib\\bin.js',
  headlessProfile: 'headless',
  pythonPath: 'python',
})

fs.writeFileSync(file, `${JSON.stringify(config, null, 2)}\n`, 'utf8')
console.log(JSON.stringify({
  peakValley: config.peakValley,
  perDay: config.perDay,
  autoComment: config.autoComment,
  mentionName: config.mentionName,
  replyToComments: config.replyToComments,
  replyPerRound: config.replyPerRound,
}, null, 2))

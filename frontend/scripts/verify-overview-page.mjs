import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const page = readFileSync(
  resolve(dirname(fileURLToPath(import.meta.url)), '../src/modules/overview/pages/OverviewPage.vue'),
  'utf8',
)

const requiredVisibleTexts = [
  '首页 / 质量驾驶舱',
  '模块快捷入口',
  '需求中心',
  'Case 中心',
  '系统设置',
  '服务状态',
]

for (const text of requiredVisibleTexts) {
  assert.ok(page.includes(text), `首页缺少可验收可见文案：${text}`)
}

console.log('overview page verification passed')

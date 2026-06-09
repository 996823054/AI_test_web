import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const page = readFileSync(
  resolve(dirname(fileURLToPath(import.meta.url)), '../src/modules/cases/pages/CasesPage.vue'),
  'utf8',
)

const requiredVisibleTexts = [
  'Case 资产工作台',
  '可信资产边界',
  '来源追溯',
  '人工确认记录',
  '覆盖信息',
  '最近执行',
  'AI 确认后的 case',
  '版本历史',
  '废弃 case',
]

for (const text of requiredVisibleTexts) {
  assert.ok(page.includes(text), `Case 中心缺少可验收可见文案：${text}`)
}

assert.ok(page.includes('fetchCaseVersions'), 'Case 中心应接入版本 API')
assert.ok(page.includes('deprecateCase'), 'Case 中心应接入废弃 API')
assert.ok(page.includes('class="workspace-layout"'), 'Case 中心应使用工作台三栏结构')

console.log('cases page verification passed')

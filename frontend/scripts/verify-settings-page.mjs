import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const page = readFileSync(
  resolve(dirname(fileURLToPath(import.meta.url)), '../src/modules/settings/pages/SettingsPage.vue'),
  'utf8',
)

const requiredVisibleTexts = [
  '系统设置',
  'AI 模型',
  '安全脱敏',
  '报告策略',
  'api_key_masked',
  '脱敏',
]

for (const text of requiredVisibleTexts) {
  assert.ok(page.includes(text), `系统设置缺少可验收可见文案：${text}`)
}

console.log('settings page verification passed')

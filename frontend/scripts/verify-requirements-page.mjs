import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const page = readFileSync(
  resolve(dirname(fileURLToPath(import.meta.url)), '../src/modules/requirements/pages/RequirementsPage.vue'),
  'utf8',
)

const requiredVisibleTexts = [
  '需求资产工作台',
  '需求关系树',
  '解析工作区 / 入库门禁',
  'AI 摘要暂不可用',
  '关联需复核需求点',
  '查看原文依据',
  '展开原文预览',
  'AI 草稿需人工确认',
  '检查未通过不得生成 case',
  '触发解析',
  '确认入库',
  '挂载节点',
  '新增域',
]

for (const text of requiredVisibleTexts) {
  assert.ok(page.includes(text), `需求中心缺少可验收可见文案：${text}`)
}

assert.ok(page.includes('fetchRequirementTree'), '需求中心应接入需求树 API')
assert.ok(page.includes('parseDocument'), '需求中心应接入解析 API')
assert.ok(page.includes('requirement-workspace-layout'), '需求中心应使用加宽的需求解析工作台结构')

console.log('requirements page verification passed')

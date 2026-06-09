import assert from 'node:assert/strict'

import { navGroups, hiddenUntilImplemented } from '../src/app/navigation.js'

const labels = navGroups.flatMap((group) => group.items.map((item) => item.label))
const expectedGroups = [
  {
    label: '质量工作台',
    items: ['首页 / 质量驾驶舱'],
  },
  {
    label: '测试资产中台',
    items: ['需求中心', 'Case 中心'],
  },
  {
    label: '系统设置',
    items: ['系统设置'],
  },
]

for (const expectedGroup of expectedGroups) {
  const group = navGroups.find((item) => item.label === expectedGroup.label)
  assert.ok(group, `缺少左侧导航分组：${expectedGroup.label}`)
  assert.deepEqual(
    group.items.map((item) => item.label),
    expectedGroup.items,
    `左侧导航分组「${expectedGroup.label}」未按需求文档归类`,
  )
}

for (const label of hiddenUntilImplemented) {
  assert.equal(labels.includes(label), false, `未实现模块不应作为可点击左侧导航入口：${label}`)
}

console.log('navigation verification passed with implemented modules only')

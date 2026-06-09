import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const tokens = readFileSync(resolve(root, 'src/styles/tokens.css'), 'utf8')
const layout = readFileSync(resolve(root, 'src/styles/layout.css'), 'utf8')
const components = readFileSync(resolve(root, 'src/styles/components.css'), 'utf8')
const styles = `${tokens}\n${layout}\n${components}`

const requiredTokens = ['--color-primary', '--color-sidebar', '--sidebar-width']
const requiredSelectors = ['.app-shell', '.sidebar', '.page-header', '.workspace-layout', '.panel-card']

for (const token of requiredTokens) {
  assert.ok(styles.includes(token), `缺少设计令牌：${token}`)
}

for (const selector of requiredSelectors) {
  assert.ok(styles.includes(selector), `缺少新版平台样式选择器：${selector}`)
}

assert.ok(styles.includes('#f4f6f9'), '平台背景应使用浅色企业级背景')
assert.ok(styles.includes('#151922'), '侧边栏应使用专业深色导航')

console.log('page style verification passed')

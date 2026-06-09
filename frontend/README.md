# 前端 - AI 自动化测试平台

## 技术栈

- Vue 3 + Vite
- Element Plus (UI 组件)
- Axios (HTTP 请求)
- Vue Router (路由)
- Pinia (状态管理)

## 运行方式

```bash
npm install
npm run dev
```

## 页面清单

| 页面 | 路由 | 说明 |
|------|------|------|
| 接口管理 | /apis | 团队成员维护接口信息 |
| 测试用例 | /cases | 用例列表（手动+AI生成） |
| 执行中心 | /executions | 执行测试、查看结果 |
| 报告中心 | /reports | 测试报告、统计图表 |
| AI 助手 | /ai | AI 对话、智能分析 |
| 变更记录 | /changelog | 接口变更历史、同步状态 |

## 当前页面骨架

当前 `frontend` 已经改造成一个 `Vue 3 + Vite` 多页面骨架，包含：

- `平台总览`
- `设备管理`
- `测试用例`
- `执行中心`
- `报告中心`
- `AI 助手`
- `变更记录`

如果只想看最早的单页静态原型，也可以直接打开：

`mobile-appium-platform-demo.html`


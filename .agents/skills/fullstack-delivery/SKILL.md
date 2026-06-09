---
name: fullstack-delivery
description: Implements full-stack vertical slices across backend models, services, APIs, frontend entries, and regression tests. Use when the user asks for 全栈开发, implement a feature end-to-end, wire frontend and backend, or complete a user-visible workflow.
phase: deliver
version: "1.0.0"
updated: 2026-05-20
license: MIT
metadata:
  category: engineering
  frameworks: [tdd, diagnose, vertical-slice]
  author: Ai_test_web
---

# Fullstack Delivery

Implement one user-visible behavior at a time from test to backend to frontend.

## When to Use

- A feature requires backend and frontend changes.
- A workflow must be usable end-to-end.
- APIs, data models, UI entries, and tests all need to align.
- The user asks to implement rather than only design.

## Instructions

1. **Read the PRD and local patterns**  
   Understand requirements, existing services, routes, models, tests, and page patterns first.

2. **Use TDD vertical slices**  
   Start with one behavior and one failing test or reproduction. Then implement the smallest full path.

3. **Wire the whole path**  
   A feature is incomplete if it has only backend API or only frontend UI.

4. **Check bypass paths**  
   Hidden APIs, batch sync endpoints, and direct update routes must enforce the same rules.

5. **Report evidence**  
   Include tests run, changed behavior, and remaining gaps.

## Prompt

```md
请按全栈垂直切片实现该功能。

必须先参考：
- docs/product/AI测试平台PRD.md
- docs/product/AI测试平台模块功能逻辑确认.md
- docs/product/AI测试平台开发任务拆分.md
- .agents/skills/tdd/SKILL.md
- .agents/skills/diagnose/SKILL.md

执行顺序：
1. 列出本次切片的用户可见行为
2. 先写或扩展一个失败测试 / 可复现脚本
3. 实现后端模型 / 服务 / API
4. 接前端页面入口
5. 跑回归测试
6. 反查绕过路径

每完成一个切片，输出：
- 改了什么
- 验证了什么
- 还没覆盖什么
- 下一切片建议
```

## Output Contract

- Behavior slice summary
- Tests added or updated
- Backend contract
- Frontend entry
- Verification results
- Residual risks

## Quality Checklist

- [ ] User-visible workflow works end-to-end
- [ ] Backend API enforces rules
- [ ] Frontend entry is available
- [ ] Data persists correctly
- [ ] Regression tests pass
- [ ] Bypass paths are checked

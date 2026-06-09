---
name: frontend-page-design
description: Designs frontend pages, information architecture, user flows, UI states, and API contracts before implementation. Use when the user asks for 前端页面设计, UI workflow, page layout, prototype, interaction design, or frontend acceptance criteria.
phase: design
version: "1.0.0"
updated: 2026-05-20
license: MIT
metadata:
  category: frontend
  frameworks: [prototype, information-architecture, acceptance-criteria]
  author: Ai_test_web
---

# Frontend Page Design

Turn PRD requirements into page structure, interaction flows, UI states, and API data contracts.

## When to Use

- A new page or workflow needs design before coding.
- A page must expose PRD guardrails clearly.
- Existing UI has entry gaps, confusing state, or incomplete empty/error states.
- The user wants prototypes or page design options.

## Instructions

1. **Start from user tasks**  
   Identify who uses the page and what they need to complete.

2. **Read existing UI patterns**  
   Inspect nearby frontend modules before inventing new layout or components.

3. **Map page to data**  
   Define required backend APIs and frontend state for every visible section.

4. **Cover states**  
   Include loading, empty, error, disabled, pending review, archived, deleted, and permission states where relevant.

5. **Prototype when uncertain**  
   Use `prototype` if multiple UI approaches need exploration.

## Prompt

```md
请基于 PRD 做前端页面设计，先不要写最终业务代码。

必须参考：
- docs/product/AI测试平台PRD.md
- docs/product/AI测试平台模块功能逻辑确认.md
- 现有 frontend/src/modules 页面结构
- .agents/skills/prototype/SKILL.md

请输出：
1. 页面目标
2. 用户角色和主要任务
3. 信息架构
4. 页面区域划分
5. 关键交互流程
6. 空状态 / 加载态 / 错误态 / 禁用态
7. 权限和不可操作状态
8. API 数据契约
9. 验收用例

如有多个合理方案，请给出 2-3 个方案并比较优缺点。
确认后再实现页面。
```

## Output Contract

- Page goal and user tasks
- Layout / region breakdown
- Interaction flow
- UI state matrix
- API contract list
- Acceptance scenarios

## Quality Checklist

- [ ] Page completes the main user task
- [ ] PRD guardrails are visible in UI
- [ ] API data supports every section
- [ ] Loading, empty, error, and disabled states are specified
- [ ] Existing frontend patterns are respected
- [ ] Acceptance cases are testable

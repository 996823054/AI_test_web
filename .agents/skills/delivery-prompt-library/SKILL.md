---
name: delivery-prompt-library
description: Routes users to the correct delivery Skill for product discovery, PRD writing, architecture, frontend design, task breakdown, full-stack delivery, PRD alignment, acceptance tests, or AI capability authoring. Use when the user asks for a prompt library, skill library, AI delivery standard, or is unsure which delivery skill to use.
phase: route
version: "2.0.0"
updated: 2026-05-20
license: MIT
metadata:
  category: routing
  frameworks: [skill-routing, delivery-governance]
  author: Ai_test_web
---

# Delivery Prompt Library

This is an index Skill. It should route to a focused Skill instead of carrying all templates itself.

## When to Use

- The user asks for a prompt library or skill library.
- The user is unsure which delivery prompt to use.
- A task spans product, PRD, architecture, development, QA, or AI capability creation.
- The user wants to standardize AI delivery and avoid PRD drift.

## Instructions

1. Identify the user's scenario.
2. Load the matching focused Skill.
3. If multiple scenarios apply, recommend an order.
4. Keep the delivery gate: completion means PRD clause has evidence, not merely changed files.

## Scenario Routing

| Scenario | Focused Skill |
| --- | --- |
| 产品讨论立项 / 方案沉淀 | `product-discovery` |
| 需求 PRD 编写 | `prd-writing` |
| 技术架构设计 | `technical-architecture` |
| 前端页面设计 | `frontend-page-design` |
| 开发任务拆解 | `development-task-breakdown` |
| 全栈开发 | `fullstack-delivery` |
| PRD 对齐开发 | `prd-aligned-development` |
| 测试 case / 验收用例 | `acceptance-test-cases` |
| 新增专用 AI 能力 | `ai-capability-authoring` |

## Prompt

```md
请使用 delivery-prompt-library 帮我选择正确的交付 Skill。

任务：<描述任务>

请输出：
1. 应使用哪个 focused Skill
2. 为什么
3. 推荐 Skill 链
4. 预计产出物
5. 验收证据
```

## Output Contract

- Selected focused Skill
- Supporting skill chain
- Execution order
- Expected output artifact
- Acceptance evidence

## Quality Checklist

- [ ] Focused Skill is selected instead of using this index for all work
- [ ] Scenario boundaries are clear
- [ ] PRD evidence remains the completion standard
- [ ] If multiple skills apply, order is explicit

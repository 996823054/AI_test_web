---
name: development-task-breakdown
description: Breaks PRDs, architecture designs, or product plans into independently verifiable vertical development tasks. Use when the user asks for 开发任务拆解, implementation tickets, issue breakdown, AFK agent tasks, or sequencing work by dependency and risk.
phase: plan
version: "1.0.0"
updated: 2026-05-20
license: MIT
metadata:
  category: delivery
  frameworks: [vertical-slice, tdd, issue-breakdown]
  author: Ai_test_web
---

# Development Task Breakdown

Split plans into vertical slices that each deliver user-visible, testable behavior.

## When to Use

- A PRD or architecture plan needs engineering tasks.
- Work should be assigned to AI agents or human developers.
- Existing task breakdown is too horizontal.
- The user asks for issues, tickets, or implementation sequencing.

## Instructions

1. **Use vertical slices**  
   Avoid “all tables first, all APIs second, all UI last.” Each task should prove one behavior.

2. **Preserve dependencies**  
   Identify prerequisites, blocked items, and data migrations.

3. **Add acceptance and tests**  
   Every task needs acceptance criteria and a verification method.

4. **Classify execution mode**  
   Mark tasks as AFK, HITL, or product-confirmation required.

5. **Keep guardrails explicit**  
   If a guardrail exists, create tasks and tests that prevent bypass paths.

## Prompt

```md
请把这个 PRD / 技术方案拆成可执行开发任务。

必须参考：
- docs/product/AI测试平台开发任务拆分.md 的格式
- .agents/skills/to-issues/SKILL.md
- .agents/skills/tdd/SKILL.md

拆解原则：
- 使用垂直切片
- 每个任务都能独立验收
- 每个任务都有测试方式
- 不按纯表/API/UI 横向拆分

请输出：
| 任务 ID | 任务名 | 用户价值 | 涉及模块 | 依赖 | 开发内容 | 验收标准 | 测试方式 | 是否适合 AI |

并标注：
- P0 / P1 / P2
- 是否涉及数据迁移
- 是否涉及 Guardrail
- 是否需要人工确认
```

## Output Contract

- Sequenced task table
- Dependencies and priorities
- Acceptance criteria
- Test approach
- AI suitability and HITL needs

## Quality Checklist

- [ ] Every task is independently verifiable
- [ ] User value is clear
- [ ] Dependencies are explicit
- [ ] Guardrails have tests
- [ ] High-risk tasks are early
- [ ] Tasks avoid horizontal slicing

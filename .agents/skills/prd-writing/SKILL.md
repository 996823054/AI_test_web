---
name: prd-writing
description: Writes or reviews implementation-ready PRDs with problem statements, user stories, acceptance criteria, guardrails, non-goals, and AI evaluation strategy. Use when the user asks to write PRD, 需求PRD编写, refine requirements, or turn a product discussion into a source-of-truth document.
phase: define
version: "1.0.0"
updated: 2026-05-20
license: MIT
metadata:
  category: product
  frameworks: [prd, acceptance-criteria, ai-evaluation]
  author: Ai_test_web
---

# PRD Writing

Create PRDs that engineering, QA, and AI agents can implement without guessing intent.

## When to Use

- The user asks to write, revise, or review a PRD.
- A product idea needs user stories and acceptance criteria.
- Requirements need guardrails, non-goals, metrics, and implementation implications.
- AI-powered features need evaluation and human-confirmation boundaries.

## Instructions

1. **Load product references**  
   Read project PRD, module logic confirmation, task breakdown, and relevant third-party PRD skills.

2. **Prefer measurable requirements**  
   Avoid vague terms like “easy”, “fast”, “smart”, or “complete” unless paired with observable criteria.

3. **Number requirements**  
   Functional requirements should use stable IDs such as `FR-001`; acceptance criteria should map back to them.

4. **Include guardrails**  
   For this project, explicitly call out human confirmation, PRD alignment, AI output auditability, and no bypass paths where relevant.

5. **Stop before implementation**  
   A PRD is complete when it can be turned into tasks, not when code is planned in detail.

## Prompt

```md
请把当前需求整理为可执行 PRD。

必须参考：
- docs/product/AI测试平台PRD.md
- docs/product/AI测试平台模块功能逻辑确认.md
- docs/delivery/AI测试平台开发任务拆分.md
- .agents/skills/to-prd/SKILL.md
- .agents/third-party-skills/github-awesome-copilot-prd/skills/prd/SKILL.md

请输出：
## Problem Statement
## Goals
## Non-goals
## Personas / Users
## User Stories
## Functional Requirements
每条需求编号为 FR-xxx。
## Acceptance Criteria
使用 Given / When / Then，并关联 FR 编号。
## Guardrails
列出不得绕过的规则。
## Data / API / UI Implications
## AI Evaluation Strategy（如涉及 AI）
## Risks / Open Questions

最后输出 PRD 完成度自检表。
```

## Output Contract

- PRD document in structured Markdown
- Functional requirement IDs
- Acceptance criteria mapped to requirements
- Guardrails and non-goals
- Risks, open questions, and implementation implications

## Quality Checklist

- [ ] Problem is user-centered, not feature-centered
- [ ] Requirements are numbered
- [ ] Acceptance criteria are testable
- [ ] Guardrails are explicit
- [ ] Non-goals protect scope
- [ ] AI features include evaluation and human confirmation

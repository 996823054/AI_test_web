---
name: product-discovery
description: Structures product discussion, project initiation, opportunity framing, and solution alignment into a decision-ready product proposal. Use when the user wants 产品讨论立项, 方案沉淀, opportunity framing, scope clarification, or stakeholder-ready product direction.
phase: discover
version: "1.0.0"
updated: 2026-05-20
license: MIT
metadata:
  category: product
  frameworks: [prd-alignment, jtbd, opportunity-solution-tree]
  author: Ai_test_web
---

# Product Discovery

Turn vague product ideas into a scoped proposal with clear users, problems, non-goals, risks, and next steps.

## When to Use

- A new product idea needs立项 or方案沉淀.
- The problem, user, value, or scope is unclear.
- A feature may affect existing module boundaries or product language.
- The user wants to stress-test a product direction before PRD writing.

## Instructions

1. **Read the source of truth**  
   Check `docs/product/AI测试平台PRD.md`, `docs/product/AI测试平台模块功能逻辑确认.md`, `CONTEXT.md`, and relevant `.cursor/rules/`.

2. **Use product skills**  
   Reference `grill-with-docs`, `grill-me`, `to-prd`, and PM third-party skills for persona, JTBD, acceptance criteria, edge cases, OKRs, and non-goals.

3. **Clarify before solving**  
   If user intent is ambiguous, ask 1-2 critical questions. If repo/docs can answer, inspect them instead of asking.

4. **Frame the decision**  
   Separate problem, user, opportunity, proposed solution, non-goals, success metrics, risks, and open questions.

5. **Do not jump to implementation**  
   Product discovery output is not a task list unless the user asks to proceed to task breakdown.

## Prompt

```md
请作为产品负责人和架构评审助手，基于当前项目文档与上下文，完成一次产品讨论立项 / 方案沉淀。

必须参考：
- docs/product/AI测试平台PRD.md
- docs/product/AI测试平台模块功能逻辑确认.md
- CONTEXT.md
- .agents/skills/grill-with-docs/SKILL.md
- .agents/third-party-skills/product-on-purpose-pm-skills/

请输出：
1. 问题陈述：谁遇到什么问题，为什么现在要解决
2. 目标用户 / 使用场景 / JTBD
3. 当前项目已有相关能力
4. 影响的模块边界
5. 关键假设与待确认问题
6. 非目标
7. 推荐立项结论：做 / 暂缓 / 先调研
8. 成功指标和风险

如果边界不清，一次只问 1-2 个关键问题。
```

## Output Contract

- Product proposal summary
- Personas / JTBD
- Problem and opportunity statement
- Scope and non-goals
- Success metrics
- Risks and open questions
- Recommended next step

## Quality Checklist

- [ ] User and problem are explicit
- [ ] Why-now is clear
- [ ] Scope and non-goals are separated
- [ ] Terminology matches project docs
- [ ] Success metrics are measurable
- [ ] Open questions are limited and actionable

---
name: prd-aligned-development
description: Audits and implements software against PRD clauses with reproducible bugs, gap analysis, guardrail checks, TDD fixes, and completion evidence. Use when the user says PRD对齐开发, PRD alignment, completed but not matching PRD, fix poor completion quality, or asks to compare implementation against requirements.
phase: verify
version: "1.0.0"
updated: 2026-05-20
license: MIT
metadata:
  category: quality
  frameworks: [diagnose, tdd, prd-alignment]
  author: Ai_test_web
---

# PRD-Aligned Development

Prevent “AI says done, but PRD is not satisfied” by making PRD clauses the completion standard.

## When to Use

- Existing implementation may not match PRD.
- A feature is “done” but lacks tests, UI entry, or data flow.
- Guardrails may be bypassed by old routes or sync APIs.
- The user asks for PRD alignment, completion audit, or gap repair.

## Instructions

1. **Audit before editing**  
   Compare PRD, module confirmation, task breakdown, and implementation. Do not start with code changes.

2. **Separate bugs from gaps**  
   Bugs are broken promised behavior; gaps are PRD capabilities not implemented.

3. **Require reproduction**  
   Each bug or gap should have an API call, UI path, or test proving the symptom.

4. **Fix with TDD**  
   For each prioritized item: failing test -> minimal fix -> regression test.

5. **Close with evidence**  
   Summarize by PRD clause, not by changed files.

## Prompt

```md
请对当前实现做 PRD 对齐开发。不要直接写代码。

必须先阅读：
- docs/product/AI测试平台PRD.md
- docs/product/AI测试平台模块功能逻辑确认.md
- docs/product/AI测试平台开发任务拆分.md
- .agents/skills/diagnose/SKILL.md
- .agents/skills/tdd/SKILL.md

第一阶段：审计
| PRD 条款 | 当前实现 | Bug / 不一致点 | 可复现方式 | 影响范围 | 修复建议 | 回归验证 |

第二阶段：分波次
- P0：主链路阻断、Guardrail 绕过、数据污染
- P1：PRD 明确要求但缺失
- P2：体验、追溯、治理不足
- P3：架构优化或增强

第三阶段：执行
每项必须先写失败测试或复现脚本，再最小实现，再回归。

完成后输出 PRD 反查表，不允许只说“已完成”。
```

## Output Contract

- PRD alignment matrix
- Bug and gap list
- Prioritized repair waves
- Regression tests
- Completion evidence by PRD clause
- Remaining risks

## Quality Checklist

- [ ] PRD clauses are cited
- [ ] Bugs have reproducible steps
- [ ] Guardrail bypass paths are checked
- [ ] Tests verify behavior, not implementation details
- [ ] Frontend, backend, data, and state are aligned
- [ ] Unfinished items are explicit

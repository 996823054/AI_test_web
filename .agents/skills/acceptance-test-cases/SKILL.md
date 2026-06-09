---
name: acceptance-test-cases
description: Generates QA test cases, acceptance scenarios, and regression coverage from PRDs, workflows, APIs, or UI designs. Use when the user asks for 测试case, 验收用例, QA case, Given/When/Then scenarios, or test plan coverage.
phase: validate
version: "1.0.0"
updated: 2026-05-20
license: MIT
metadata:
  category: qa
  frameworks: [acceptance-criteria, edge-cases, regression]
  author: Ai_test_web
---

# Acceptance Test Cases

Create executable QA cases and acceptance scenarios that trace back to requirements.

## When to Use

- The user asks for test cases, QA cases, or acceptance cases.
- PRD requirements need Given/When/Then criteria.
- A feature needs regression coverage before or after implementation.
- Existing test cases need review for completeness and executability.

## Instructions

1. **Read the requirement source**  
   Use PRD, module logic docs, UI flow, API docs, or existing cases.

2. **Use QA skills**  
   Reference `test_case`, `diagnose`, `tdd`, and PM acceptance / edge-case references.

3. **Trace every case**  
   Each case must link to a requirement, user story, API, page, or workflow.

4. **Cover more than happy path**  
   Include main path, edge cases, error states, permission/state cases, and regression cases.

5. **Make expected results observable**  
   Avoid “works normally”; use user-visible result or API/data assertion.

## Prompt

```md
请基于 PRD 和当前实现生成测试 case / 验收用例。

必须参考：
- .agents/skills/test_case/SKILL.md
- docs/product/AI测试平台PRD.md
- docs/product/AI测试平台模块功能逻辑确认.md

请输出：
1. 覆盖范围摘要
2. 主路径用例
3. 异常路径用例
4. 边界用例
5. 权限 / 状态 / 数据依赖用例
6. 回归用例
7. 不覆盖项和原因

字段：
| 用例 ID | 标题 | 关联需求 | 前置条件 | 步骤 | 预期结果 | 重要性 | 类型 |

验收用例使用 Given / When / Then。
自动化建议需标明后端 API、前端 E2E 或单元测试。
```

## Output Contract

- Coverage summary
- QA test case table
- Given/When/Then acceptance scenarios
- Regression suggestions
- Coverage gaps

## Quality Checklist

- [ ] Each case is executable
- [ ] Expected result is observable
- [ ] Requirement trace is present
- [ ] Guardrails are covered
- [ ] Edge and error states are included
- [ ] Uncovered risks are listed

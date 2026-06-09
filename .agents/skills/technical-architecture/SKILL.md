---
name: technical-architecture
description: Designs technical architecture for backend, frontend, data models, state machines, AI workflows, and integration boundaries. Use when the user asks for 技术架构设计, system design, module boundaries, data/API design, or architecture review before implementation.
phase: design
version: "1.0.0"
updated: 2026-05-20
license: MIT
metadata:
  category: architecture
  frameworks: [deep-modules, state-machine, tdd]
  author: Ai_test_web
---

# Technical Architecture

Design implementation architecture that maps PRD requirements to modules, APIs, data, state, and tests.

## When to Use

- A change affects data models, service layers, AI workflows, or shared execution flow.
- A PRD needs a technical design before coding.
- Existing implementation has shallow modules, hidden coupling, or poor test seams.
- The user asks for architecture, technical design, or module boundary decisions.

## Instructions

1. **Read the domain and decisions**  
   Start from `CONTEXT.md`, PRD docs, technical docs, and any ADRs.

2. **Use architecture skills**  
   Reference `improve-codebase-architecture`, `grill-with-docs`, `tdd`, and `diagnose`.

3. **Map requirements to design**  
   Every model, API, state, and page should trace to a PRD need or explicit technical constraint.

4. **Design for testability**  
   Define public interfaces and behavior tests before implementation details.

5. **Call out trade-offs**  
   If alternatives exist, compare them and recommend one.

## Prompt

```md
请基于 PRD 和现有代码做技术架构设计，先不要写代码。

必须参考：
- CONTEXT.md
- docs/product/AI测试平台PRD.md
- docs/product/AI测试平台模块功能逻辑确认.md
- docs/technical/
- .agents/skills/improve-codebase-architecture/SKILL.md
- .agents/skills/tdd/SKILL.md

请输出：
1. 现有实现概览
2. 目标能力和边界
3. 数据模型设计
4. API 设计
5. 前端状态与页面流
6. 核心状态机
7. 模块依赖关系
8. 可测试接口
9. 迁移策略
10. 风险与备选方案

必须附：
- Mermaid 流程图或状态图
- PRD 条款到技术方案映射表
- 回归测试计划
```

## Output Contract

- Architecture overview
- Data model and API contracts
- State machine or flow diagram
- Frontend data-flow notes
- Migration and compatibility plan
- Test strategy

## Quality Checklist

- [ ] Every design element maps to a requirement or constraint
- [ ] State transitions prevent bypass paths
- [ ] Data model supports auditability and traceability
- [ ] Interfaces are testable through behavior
- [ ] Alternatives and trade-offs are explicit
- [ ] Migration risks are named

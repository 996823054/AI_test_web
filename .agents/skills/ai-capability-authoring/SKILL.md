---
name: ai-capability-authoring
description: Creates project-specific AI capabilities such as Skills, prompts, evaluators, RAG workflows, and reusable AI agents with validation plans. Use when the user asks to 新增专用AI能力, write a skill, create evaluator, add prompt workflow, or productize repeated AI behavior.
phase: extend
version: "1.0.0"
updated: 2026-05-20
license: MIT
metadata:
  category: ai-capability
  frameworks: [skill-authoring, evaluator, prompt-engineering]
  author: Ai_test_web
---

# AI Capability Authoring

Turn repeated AI work into reusable project capabilities with prompts, Skills, evaluators, and validation.

## When to Use

- The user wants a new project Skill or reusable prompt workflow.
- AI behavior should be governed, tested, and reused.
- A new evaluator, RAG retrieval step, or AI workflow is needed.
- Repeated manual prompting should become a formal capability.

## Instructions

1. **Clarify capability type**  
   Decide whether this is a Skill, prompt template, evaluator, RAG workflow, service capability, or agent workflow.

2. **Read authoring references**  
   Use `write-a-skill`, `create-skill`, existing `.agents/skills/*`, and project AI capability docs.

3. **Define trigger and contract**  
   A capability must state when to use it, required inputs, outputs, and validation method.

4. **Keep Skills small**  
   Put large templates in `references/`; keep `SKILL.md` focused on behavior and routing.

5. **Add validation**  
   Include sample prompts, expected outputs, and evaluator or test approach where possible.

## Prompt

```md
请帮我新增一个项目专用 AI 能力。

必须先参考：
- .agents/skills/write-a-skill/SKILL.md
- 已有 .agents/skills/*/SKILL.md
- .cursor/rules/

请先确认：
1. 能力类型：Skill / Prompt / Evaluator / RAG / Workflow
2. 名称和触发场景
3. 输入要求
4. 输出格式
5. 是否需要 references
6. 是否需要 scripts
7. 如何验证有效

然后创建：
skill-name/
├── SKILL.md
├── references/
└── scripts/

SKILL.md 必须包含 frontmatter、When to Use、Instructions、Prompt、Output Contract、Quality Checklist。
```

## Output Contract

- Capability type and name
- Trigger description
- Input/output contract
- Skill or prompt files
- Validation plan
- Usage examples

## Quality Checklist

- [ ] Trigger is specific enough for automatic selection
- [ ] Inputs and outputs are clear
- [ ] Large templates live in references
- [ ] Validation method exists
- [ ] Capability does not duplicate an existing Skill
- [ ] Usage example is included

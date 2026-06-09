# Third-Party Skills

This directory keeps third-party AI skill references used by this project.

These skills are development and product methodology references for Cursor/AI collaboration. They are not runtime business plugins of the AI testing platform.

## Sources

### mattpocock/skills

- Source: https://github.com/mattpocock/skills
- Local installed skills: `.agents/skills/`
- Local index: `.agents/third-party-skills/mattpocock-skills/`
- Role: engineering workflow guidance for diagnosis, TDD, PRD creation, issue slicing, architecture review, and handoff.

### product-on-purpose/pm-skills

- Source: https://github.com/product-on-purpose/pm-skills
- Local copy: `.agents/third-party-skills/product-on-purpose-pm-skills/`
- Role: product management methodology guidance.
- Scope: 40 PM skills covering discovery, definition, development, delivery, measurement, iteration, foundations, and utilities.

Useful skill groups for this AI testing platform:

- `define-*`: problem statements, opportunity trees, hypotheses, JTBD.
- `discover-*`: interviews, stakeholder summaries, competitive analysis.
- `deliver-*`: PRD, user stories, acceptance criteria, edge cases, release notes.
- `measure-*`: OKRs, dashboards, experiment design, instrumentation.
- `iterate-*`: retrospectives, lessons, refinement, pivot decisions.
- `foundation-*`: lean canvas, personas, meeting lifecycle, stakeholder updates.

### github/awesome-copilot PRD and PM references

- Source: https://github.com/github/awesome-copilot
- Local copy: `.agents/third-party-skills/github-awesome-copilot-prd/`
- Key files:
  - `skills/prd/SKILL.md`
  - `agents/prd.agent.md`
  - `agents/se-product-manager-advisor.agent.md`
- Role: PRD generation, requirement quality standards, product manager issue writing, and measurable success criteria.

## Project Priority

When these third-party skills conflict with project-specific context, prefer:

1. `ai平台.md`
2. `CONTEXT.md`
3. `.cursor/rules/`
4. third-party skills in this directory

## Recommended Usage

Use explicit prompts:

```text
结合 product-on-purpose/pm-skills，帮我重新审视 AI 测试平台完整模块 的用户画像和成功指标。
```

```text
用 github/awesome-copilot PRD skill 的方式，把报告中心完整模块需求整理成 PRD。
```

```text
结合 mattpocock grill-with-docs 和 PM skills，继续澄清 移动端完整闭环。
```

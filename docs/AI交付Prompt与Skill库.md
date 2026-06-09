# AI 交付 Prompt 与 Skill 库

本文档是团队使用 AI 做产品、设计、开发、测试交付时的入口索引。模板已拆成多个 focused Skill，避免一个大 Skill 混用所有场景。

- 总入口：`.agents/skills/delivery-prompt-library/SKILL.md`
- 产品讨论立项：`.agents/skills/product-discovery/SKILL.md`
- 需求 PRD 编写：`.agents/skills/prd-writing/SKILL.md`
- 技术架构设计：`.agents/skills/technical-architecture/SKILL.md`
- 前端页面设计：`.agents/skills/frontend-page-design/SKILL.md`
- 开发任务拆解：`.agents/skills/development-task-breakdown/SKILL.md`
- 全栈开发：`.agents/skills/fullstack-delivery/SKILL.md`
- PRD 对齐开发：`.agents/skills/prd-aligned-development/SKILL.md`
- 测试 case / 验收用例：`.agents/skills/acceptance-test-cases/SKILL.md`
- 新增专用 AI 能力：`.agents/skills/ai-capability-authoring/SKILL.md`

## 使用方式

在 Cursor 中可直接说：

```md
使用 delivery-prompt-library skill，帮我选择正确的交付 Skill。
任务：<你的任务>
```

如果是 PRD 对齐、全栈开发、测试用例、架构设计等场景，建议明确场景：

```md
使用 prd-aligned-development skill，检查并修复需求中心与 PRD 的不一致。
```

## 场景索引

| 场景 | 使用模板 | 推荐 Skill |
| --- | --- | --- |
| 产品讨论立项 / 方案沉淀 | `product-discovery` | `grill-with-docs`、`grill-me`、`to-prd`、PM third-party skills |
| 需求 PRD 编写 | `prd-writing` | `to-prd`、`grill-with-docs`、PRD third-party skills |
| 技术架构设计 | `technical-architecture` | `improve-codebase-architecture`、`grill-with-docs`、`tdd` |
| 前端页面设计 | `frontend-page-design` | `prototype`、`grill-with-docs`、`test_case` |
| 开发任务拆解 | `development-task-breakdown` | `to-issues`、`tdd`、`diagnose` |
| 全栈开发 | `fullstack-delivery` | `tdd`、`diagnose`、`improve-codebase-architecture` |
| PRD 对齐开发 | `prd-aligned-development` | `diagnose`、`tdd`、`grill-with-docs` |
| 测试 case / 验收用例 | `acceptance-test-cases` | `test_case`、`diagnose`、`tdd` |
| 新增专用 AI 能力 | `ai-capability-authoring` | `write-a-skill`、`create-skill`、`tdd` |

## 最重要的交付原则

不要让 AI 以“代码写完”为完成标准，要以“PRD 条款有证据通过”为完成标准。

每次交付后必须反查：

| 验收项 | 要求 |
| --- | --- |
| PRD 条款覆盖 | 明确对应条款 |
| 前端入口 | 用户能操作 |
| 后端 API | 接口可调用且有校验 |
| 数据模型 | 能支撑状态和追溯 |
| 测试覆盖 | 有后端 / 前端 / 验收验证 |
| 绕过路径 | 旧 API、批量同步、直接 update 都要检查 |
| 未完成项 | 必须列出，不能用“完成了”概括 |

## 快速复制 Prompt

```md
请使用 <对应 focused Skill>。

任务：<写清楚任务>
场景：<产品讨论立项 / PRD 编写 / 技术架构设计 / 前端页面设计 / 开发任务拆解 / 全栈开发 / PRD 对齐开发 / 测试 case / 新增专用 AI 能力>

请先输出：
1. 需要使用的 Skill 链
2. 对照哪些 PRD / 模块确认 / 任务拆分条款
3. 本次范围和非范围
4. 预计产出物
5. 验收证据

执行后请输出：
| 验收项 | 结果 | 证据 |
| --- | --- | --- |
| PRD 条款覆盖 | 是/否 | |
| 前端入口 | 有/无/不适用 | |
| 后端 API | 有/无/不适用 | |
| 数据模型 | 有/无/不适用 | |
| 测试覆盖 | 有/无 | |
| 绕过路径 | 有/无 | |
| 未完成项 | 列出 | |
```

## 维护建议

- 新增高频场景时，优先新增独立 focused Skill，并在 `delivery-prompt-library` 里补路由。
- 如果某个 Skill 超过 100 行，应把大段模板拆到该 Skill 的 `references/`。
- 如果发现 AI 再次出现“完成但不符合 PRD”，先把失败模式沉淀到“反假完成”或“Guardrail 检查”模板。

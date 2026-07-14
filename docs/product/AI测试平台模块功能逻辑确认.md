# AI 测试平台模块功能逻辑确认

版本：v2.0
文档角色：模块边界确认与 PRD 索引
唯一产品需求事实源：[AI 测试平台 PRD](AI测试平台PRD.md)

本文不承载用户故事、功能需求、验收标准、护栏、数据 / API / UI 影响或 AI 评估策略；这些内容均以 PRD 为准。

## 1. 模块索引

| 模块 | PRD 章节 | 需求编号范围 | 模块定位 |
|---|---|---|---|
| 首页 / 质量驾驶舱 | [PRD §5](AI测试平台PRD.md#5-module-首页--质量驾驶舱) | `FR-HOME-*` | 质量判断、风险与待办聚合入口。 |
| 需求中心 | [PRD §6](AI测试平台PRD.md#6-module-需求中心) | `FR-REQ-*` | 需求事实源与 Case 生成上游。 |
| Case 中心 | [PRD §7](AI测试平台PRD.md#7-module-case-中心) | `FR-CASE-*` | 正式 Case、草稿、版本与回归资产中心。 |
| 接口中心 | [PRD §8](AI测试平台PRD.md#8-module-接口中心) | `FR-API-*` | 平台内 API 定义事实源。 |
| 移动端执行中心 | [PRD §9](AI测试平台PRD.md#9-module-移动端执行中心) | `FR-MOB-*` | Android 设备、App、页面、元素和执行上下文。 |
| 执行中心 | [PRD §10](AI测试平台PRD.md#10-module-执行中心) | `FR-EXEC-*` | 跨执行类型的统一任务控制台。 |
| 报告中心 | [PRD §11](AI测试平台PRD.md#11-module-报告中心) | `FR-REPORT-*` | 执行结果与可复盘证据中心。 |
| AI 能力中心 | [PRD §12](AI测试平台PRD.md#12-module-ai-能力中心) | `FR-AI-*` | AI 任务、RAG、Prompt、Skill、Evaluator、反馈与成本治理。 |
| 变更中心 | [PRD §13](AI测试平台PRD.md#13-module-变更中心) | `FR-CHANGE-*` | 跨模块变更影响与回归建议中心。 |
| 待办中心 | [PRD §14](AI测试平台PRD.md#14-module-待办中心) | `FR-TODO-*` | 人工复核入口与核销闭环。 |
| 系统设置 | [PRD §15](AI测试平台PRD.md#15-module-系统设置) | `FR-SET-*` | 模型、环境、Appium、报告、脱敏和权限占位配置。 |
| Bug 中心 | [PRD §16](AI测试平台PRD.md#16-future-module-bug-中心) | `FR-BUG-*` | 未来模块；当前只保留关联与接入边界。 |

## 2. 模块边界结论

| 边界主题 | 已确认结论 | PRD 条款 |
|---|---|---|
| 当前一级模块 | 当前产品包含上述 11 个一级模块；Bug 中心为未来模块。 | [PRD §4](AI测试平台PRD.md#4-functional-modules)、[PRD §16](AI测试平台PRD.md#16-future-module-bug-中心) |
| 变更治理 | 变更中心是一级模块，负责影响分析；需求层差异事实仍以 `RequirementDiff` 为准。 | [PRD §13](AI测试平台PRD.md#13-module-变更中心) |
| 人工复核 | 待办中心是一级模块，只承接复核入口与核销，不绕过来源模块修改正式资产。 | [PRD §14](AI测试平台PRD.md#14-module-待办中心) |
| AI 治理 | RAG、Prompt、Skill、Evaluator、反馈样本和成本统一归 AI 能力中心。 | [PRD §12](AI测试平台PRD.md#12-module-ai-能力中心) |
| Case 治理 | Case 版本、可信分层、废弃和回归资产治理统一归 Case 中心。 | [PRD §7](AI测试平台PRD.md#7-module-case-中心) |
| 正式资产 | AI 输出影响正式资产时必须经过评估和人工确认。 | [PRD §18](AI测试平台PRD.md#18-global-guardrails) |
| AI 失败 | 真实 AI 调用失败必须显式失败，不允许模板、规则、缓存或模拟结果降级冒充成功。 | [`FR-AI-013`](AI测试平台PRD.md#124-functional-requirements)、[`FR-SET-012`](AI测试平台PRD.md#154-functional-requirements) |
| 需求门禁 | 检查未通过的需求或接口文档不得生成 Case 草稿。 | [`FR-REQ-009`](AI测试平台PRD.md#64-functional-requirements)、[PRD §18](AI测试平台PRD.md#18-global-guardrails) |
| 权限边界 | 当前只保留基础权限配置占位，不声明业务模块已完成完整鉴权。 | [`FR-SET-010`](AI测试平台PRD.md#154-functional-requirements) |
| 移动端边界 | 当前正式产品范围为 Android；iOS、云真机、多设备调度和 AI 视觉定位不在当前范围。 | [`FR-MOB-011`](AI测试平台PRD.md#94-functional-requirements)、[PRD §19](AI测试平台PRD.md#19-non-goals) |

## 3. 核心链路索引

| 核心链路 | 模块边界 | PRD |
|---|---|---|
| 需求到 Case | 需求中心提供基线、差异和覆盖事实；Case 中心按生成计划管理草稿与正式资产。 | [PRD §17.1](AI测试平台PRD.md#171-需求到-case) |
| 接口 Case 到报告 | 接口中心提供接口事实，执行中心运行，报告中心沉淀证据。 | [PRD §17.2](AI测试平台PRD.md#172-接口-case-到报告) |
| Android 执行到报告 | 移动端执行中心提供设备与资产上下文，执行与报告模块承接任务和证据。 | [PRD §17.3](AI测试平台PRD.md#173-android-移动端执行到报告) |
| 变更到回归推荐 | 需求与接口差异作为来源事实，变更中心分析影响，待办中心承接人工复核。 | [PRD §17.4](AI测试平台PRD.md#174-变更到回归推荐) |
| 覆盖缺口到待办 | 覆盖矩阵保留缺口事实，来源模块处理，待办中心只负责复核入口与核销。 | [PRD §17.5](AI测试平台PRD.md#175-覆盖缺口到待办闭环) |

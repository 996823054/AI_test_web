# AI 测试平台开发技术架构设计

## 1. 设计口径与目标

本文档基于以下资料整理：

- `docs/product/AI测试平台PRD.md`
- `docs/product/AI测试平台模块功能逻辑确认.md`
- `docs/technical/AI测试平台技术设计文档.md`
- `CONTEXT.md`
- 当前代码结构：`backend/`、`frontend/`

当前架构设计以 `CONTEXT.md` 和 PRD 的模块完整开发口径为准：

1. 需求文档 -> AI case 草稿 -> 测试人员确认 -> case 资产。
2. API case -> 单 case 执行 / 调试 -> 报告。
3. Android 设备 / 移动端基础路径 -> 设备识别 -> 移动 case 编辑 / 执行证据。

需要特别说明：当前不再按阶段标签区分移动端能力，Android 移动端闭环按模块完整交付口径进入完整验收范围。开发任务和验收以“三条基础业务闭环”为准。

架构目标：

- 前端按业务域组织，保持页面、接口调用、状态展示和证据查看的本地性。
- 后端按 Router -> Service -> Harness -> Runner -> Report 的链路拆分，避免执行逻辑散落在接口层。
- AI 能力以 Skill / Prompt / Evaluator 形式沉淀，所有影响正式资产的 AI 输出必须经过门禁和人工确认。
- 数据模型区分事实源、草稿、执行记录、报告证据、AI 过程记录和 RAG 知识片段。
- 当前模块可以用轻量实现先跑通闭环，但目录、状态机和数据结构必须为 RAG、Phoenix、后台任务队列和变更治理预留接口。

## 2. 当前代码现状

当前仓库已经具备 AI 测试平台雏形：

- 后端：`backend/`
 - 框架：FastAPI、SQLAlchemy、Pydantic、Uvicorn。
 - 已有模块：cases、executions、reports、requirements、apis、settings、ai、changelog、mobile / midscene。
 - 已有能力：部分 case service、需求文档 service、AI skill、Phoenix evaluator、API runner、mobile runner、report generator。
- 前端：`frontend/`
 - 框架：Vue 3、Vue Router、Vite。
 - 已有模块：overview、requirements、cases、apis、executions、reports、mobile、aiWorkspace、governance、settings。
 - 已有 shared 组件：表格、指标卡、状态标签、日志、步骤时间线、证据查看器、反馈弹窗。
- 自动化依赖：
 - 后端 Python 依赖包含 `requests`、`pypdf`、`python-docx`、`openai`、`arize-phoenix-evals`。
 - 根目录 Node 依赖用于 Appium / uiautomator2。

当前主要架构改造方向不是从零开始，而是把已有能力收敛到更稳定的模块边界：

- Router 只做参数校验、权限校验、DTO 转换和调用 Service。
- Service 负责编排业务流程和状态流转。
- Harness 负责环境、变量、依赖、测试数据、清理和证据增强。
- Runner 只执行具体协议动作，不修改业务资产，不生成最终报告。
- Skill 只承载单一 AI 能力，不直接写业务表。
- Evaluator 只负责评估和门禁结论，不直接替用户确认资产。

## 3. 前端模块结构

### 3.1 推荐目录结构

```text
frontend/src
 app/
 layout/
 router/
 navigation.js
 shared/
 api/
 http.js
 error.js
 components/
 DataTable.vue
 StatusBadge.vue
 EvidenceViewer.vue
 StepTimeline.vue
 LogPanel.vue
 FeedbackModal.vue
 composables/
 useFeedback.js
 usePollingTask.js
 useProjectContext.js
 utils/
 format.js
 status.js
 modules/
 overview/
 requirements/
 cases/
 apis/
 executions/
 reports/
 mobile/
 ai/
 governance/
 settings/
```

### 3.2 模块职责

#### 2026-05-19 前端全量重建后的页面信息架构与可见范围

本轮删除旧 `frontend/src` 业务实现并重建，按“已实现可验收模块可见、未实现模块不出现在导航”的原则处理：

- 左侧导航暴露 4 个入口：首页 / 质量驾驶舱、需求中心、Case 中心、系统设置。
- 导航分组：`质量工作台`（首页）、`测试资产中台`（需求中心、Case 中心）、`系统设置`（系统设置）。
- 需求中心：三栏工作台（需求关系树占位 + 文档列表 + 原文预览 / 解析与入库门禁），对接 `/api/ai/documents*`。
- Case 中心：三栏工作台（可信资产边界 + case 列表 + 来源追溯 / 确认 / 覆盖 / 执行摘要），对接 `/api/cases/*`。
- 系统设置：Tab 化配置页（AI 模型、安全脱敏、报告策略），对接 `/api/settings/*`；环境 / Appium 为后面启用占位。
- 接口中心、移动端执行中心、执行中心、报告中心、AI 能力中心、治理类入口不在导航层展示。
- 视觉体系改为企业级浅色平台风格：固定深色侧边栏、浅灰背景、白底卡片、`PageHeader` + `workspace-layout`，不再使用深色渐变 hero。

#### 2026-05-19 本轮页面信息架构与可见范围（历史记录）

本轮前端重构按“已实现可验收模块可见、未实现模块在 UI / 导航层隐藏”的原则处理，避免用户把规划能力误认为已交付能力：

- 左侧导航仅暴露：首页 / 质量驾驶舱、需求中心、Case 中心。
- 需求中心当前为 模块展示层，采用三栏资产工作台：左侧需求关系树，中间需求文档列表，右侧原文预览与解析 / 入库门禁说明。
- Case 中心当前为 模块展示层，采用三栏资产工作台：左侧可信资产边界与统计，中间 case 列表，右侧来源追溯、人工确认记录、覆盖信息和最近执行摘要。
- 接口中心、移动端执行中心、执行中心、报告中心、AI 能力中心、系统设置、治理类入口仍保留规划和路由代码，但在左侧导航中隐藏，待对应任务具备可验收页面后再恢复入口。
- 本轮页面视觉统一为深色渐变头图 + 资产卡片 + 三栏工作台布局，验证脚本覆盖关键文案、三栏结构和导航隐藏策略。

#### `overview`

首页 / 质量驾驶舱。

职责：

- 展示需求数、case 数、接口数、设备状态、今日执行、失败任务、AI 待确认 case。
- 展示风险摘要，但必须带证据来源、置信度、触发原因和人工确认边界。
- 作为待办和风险入口，不承载复杂流程引擎。

#### `requirements`

需求中心。

职责：

- 需求文档上传、原文预览、下载、移动、归档、软删除。
- 需求关系树：业务域 -> 模块 -> 功能 -> 需求版本 -> 验收点。
- 解析结果确认、逻辑检查结果展示、历史对比展示。
- 检查通过后入库，成为 case 生成依据。

建议页面：

- `RequirementDocumentsPage.vue`：文档库 + 关系树。
- `RequirementDetailPage.vue`：原文、元信息、版本、解析摘要。
- `RequirementParseReviewPage.vue`：解析结果和门禁问题确认。
- `RequirementTreePage.vue`：需求树视图。

#### `cases`

Case 中心。

职责：

- 统一管理功能 case、接口 case、移动端 case、AI case 草稿。
- 展示 case 来源、确认记录、最近执行结果、健康状态。
- AI 草稿确认、编辑后接受、拒绝、合并。
- 模块完整交付 / 重要性标记作为当前回归依据。

建议页面：

- `CasesPage.vue`：统一 case 列表。
- `CaseDetailPage.vue`：来源、步骤、版本、执行记录。
- `CaseEditorPage.vue`：统一 case 编辑器。
- `AiCaseDraftsPage.vue`：AI case 待确认队列。

#### `apis`

接口中心。

职责：

- API 定义管理：method、path、headers、params、body schema、response schema、状态码。
- 接口文档导入和解析结果确认。
- 环境、变量集、鉴权配置。
- 单接口调试和调试结果沉淀。
- 接口废弃后禁止关联 case 执行。

#### `executions`

执行中心。

职责：

- 统一展示接口、移动端和后面 WebSocket / LLM 执行任务。
- 支持任务状态、步骤状态、日志、取消、重跑、重试。
- 失败后展示处理建议：重跑、检查环境、修复 case、标记 bug 占位、人工复核。

#### `reports`

报告中心。

职责：

- 展示单 case 报告、批次报告和 HTML 报告。
- 展示请求、响应、断言、变量上下文、截图、XML、Appium 日志。
- 支持报告导出、保留策略、人工确认和失败分析结果。

#### `mobile`

移动端执行中心。

职责：

- Android 设备识别、状态、占用锁。
- App 信息管理：package、versionName、versionCode、build。
- 元素资产管理：页面、模块、主定位、备用定位预留。
- 移动端 case 调试和执行入口。

#### `ai`

AI 能力中心。

职责：

- Skill 管理、Prompt 管理、Evaluator 管理。
- AI 调用日志、模型配置、成本统计。
- RAG 知识库、反馈样本库、负样本库。
- AI 能力不作为孤立工作台，而是主流程中的可配置能力中心。

当前代码中已有 `aiWorkspace`，建议按模块逐步改名或映射为 `ai`，避免产品口径和代码目录长期不一致。

#### `governance`

治理能力。

职责：

- 变更记录、影响分析、待处理 case。
- 当前模块可作为占位或轻量视图；增强能力再补齐完整变更治理。

#### `settings`

系统设置。

职责：

- 项目、模块树、用户角色、环境配置、模型配置、Appium capability、脱敏规则、报告保留策略。

### 3.3 前端接口调用规范

- 所有 HTTP 调用统一经过 `shared/api/http.js`。
- API 返回统一处理 `code`、`message`、`data`、`trace_id`。
- 长任务页面使用统一轮询组合函数 `usePollingTask`。
- 状态展示统一使用 `StatusBadge`，避免每个页面重复维护状态颜色和文案。
- 执行证据统一使用 `EvidenceViewer`，避免报告、执行详情、case 详情各自实现证据展示。

## 4. 后端模块结构

### 4.1 推荐目录结构

```text
backend/app
 main.py
 core/
 config.py
 database.py
 lifecycle.py
 logging.py
 errors.py
 api/
 deps.py
 response.py
 routers/
 overview.py
 requirements.py
 cases.py
 apis.py
 executions.py
 reports.py
 mobile.py
 ai.py
 governance.py
 settings.py
 services/
 requirement_service.py
 case_service.py
 api_definition_service.py
 execution_service.py
 harness_service.py
 report_service.py
 ai_orchestration_service.py
 rag_service.py
 settings_service.py
 governance_service.py
 harness/
 execution_context.py
 environment_harness.py
 variable_harness.py
 dependency_harness.py
 test_data_harness.py
 observability_harness.py
 runners/
 base_runner.py
 api_runner.py
 mobile_runner.py
 websocket_runner.py
 skills/
 base_skill.py
 requirement_parse_skill.py
 case_generate_skill.py
 interface_parse_skill.py
 rag_retrieve_skill.py
 requirement_diff_skill.py
 conflict_detect_skill.py
 case_impact_skill.py
 coverage_evaluate_skill.py
 failure_analysis_skill.py
 evaluators/
 base_evaluator.py
 field_completeness_evaluator.py
 phoenix_case_evaluator.py
 coverage_evaluator.py
 prompts/
 registry.py
 renderer.py
 templates/
 models/
 schemas/
 repositories/
 storage/
 file_storage.py
 artifact_storage.py
 security/
 masking.py
 secrets.py
 audit.py
```

当前代码已经存在 `routers/`、`services/`、`models/`、`schemas/`、`skills/`、`modules/executions/runners/`。短期不必一次性大搬迁，可以按以下方式演进：

1. 当前模块先在现有目录中补齐职责，避免大规模改路径。
2. 新增 `harness/`、`evaluators/`、`security/`、`repositories/`。
3. 将 `modules/executions/runners/` 中的 Runner 契约统一，再决定是否迁移到 `app/runners/`。
4. 将实验性能力，例如 `midscene_ios`、`vision_automation`，标记为预研或 预研能力，避免混入 基础业务链路。

### 4.2 后端调用方向

```text
Router
 -> Service
 -> Repository / Storage
 -> Skill / Evaluator
 -> Harness
 -> Runner
 -> ReportService
```

约束：

- Router 不直接调用 Runner。
- Runner 不直接写 case、需求、报告主表。
- Skill 不直接修改正式业务资产。
- Evaluator 不直接替用户确认。
- ReportService 只根据执行结果和证据生成报告，不重新执行 case。

## 5. 数据模型分层

### 5.1 分层原则

数据模型按“事实源、过程态、执行态、证据态、AI 态、治理态”分层。

#### 基础上下文层

用于所有资产归属。

- `projects`
- `module_nodes`
- `users`
- `roles`
- `audit_logs`

#### 需求事实源层

用于承载需求进入平台后的可信来源。

- `requirement_documents`
- `requirement_document_versions`
- `requirement_tree_nodes`
- `requirement_items`
- `requirement_check_results`

说明：

- 原始文档是证据和来源。
- 人工确认后的 `requirement_items` 是 case 生成和覆盖率计算的主要流转对象。
- 检查未通过的文档不能生成 case，也不能进入正式 RAG 知识库。

#### Case 资产层

用于承载正式测试资产和 AI 草稿。

- `ai_case_drafts`
- `test_cases`
- `case_steps`
- `case_versions`
- `case_source_links`

说明：

- `ai_case_drafts` 是草稿，不是正式资产。
- `test_cases` 是正式 case 主表。
- `case_source_links` 用于统一维护 case 与需求、接口、元素、变更、AI 输出的来源关系。

#### 接口事实源层

用于承载平台内 API 定义。

- `api_definitions`
- `api_definition_versions`
- `api_environments`
- `api_variable_sets`
- `api_auth_configs`
- `api_debug_results`

说明：

- 导入文档和 AI 解析结果是候选接口。
- 人工确认后的接口定义才是可引用接口。
- 已废弃接口禁止关联 case 执行。

#### 移动端资产层

用于承载 Android 执行上下文。

- `devices`
- `device_locks`
- `apps`
- `mobile_pages`
- `mobile_elements`
- `mobile_element_versions`

说明：

- 模块完整交付支持 Android 模拟器 / 本机设备。
- 正式移动端 case 必须引用元素资产。
- 调试态可以临时使用 locator，调试成功后应沉淀为元素资产。

#### 执行任务层

用于统一追踪任务。

- `execution_tasks`
- `execution_batches`
- `execution_step_results`
- `execution_logs`
- `dependency_records`
- `test_data_records`

说明：

- `execution_tasks` 是执行事实源。
- 当前模块可以使用进程内后台任务或轻量 worker。
- 增强能力再引入 Celery / RQ / Arq 等队列。

#### 报告证据层

用于沉淀可复盘证据。

- `test_reports`
- `report_artifacts`
- `report_confirmations`
- `failure_analysis_results`

说明：

- 报告不只是结果展示，而是执行证据中心。
- 取消任务不生成正式质量报告，只保留任务日志。

#### AI 与 RAG 层

用于 AI 调用、Prompt、评估、反馈和知识库。

- `ai_call_logs`
- `prompt_templates`
- `skill_registry`
- `skill_prompt_bindings`
- `evaluator_configs`
- `phoenix_evaluation_results`
- `knowledge_chunks`
- `rag_retrieval_logs`
- `feedback_samples`

说明：

- 模块完整交付 记录 AI 输入、输出、错误、耗时和人工确认结果。
- 增强能力再启用正式 RAG 生命周期和 Phoenix 强门禁。
- 未确认的 AI 输出、检查未通过需求、未脱敏内容不得进入正式知识库。

#### 治理层

用于后面变更与回归治理。

- `change_records`
- `case_impacts`
- `todo_items`

说明：

- 当前模块可以先支持待办队列和轻量变更占位。
- 增强能力再做完整 diff、影响分析和 case 更新建议。

## 6. API 分层

### 6.1 API 路径建议

```text
/api/overview
/api/projects
/api/modules
/api/requirements
/api/requirement-documents
/api/cases
/api/ai-case-drafts
/api/apis
/api/api-environments
/api/executions
/api/reports
/api/mobile/devices
/api/mobile/apps
/api/mobile/elements
/api/ai/skills
/api/ai/prompts
/api/ai/evaluators
/api/rag
/api/governance
/api/todos
/api/settings
```

### 6.2 API 职责规范

Router 层只做：

- 请求参数校验。
- 权限和项目上下文校验。
- 调用 Service。
- 返回统一响应结构。

Router 层不做：

- 文档解析逻辑。
- AI Prompt 拼接。
- Runner 执行。
- 报告生成。
- RAG 入库。
- 状态机分支散落。

### 6.3 统一响应结构

```json
{
 "code": "ok",
 "message": "success",
 "data": {},
 "trace_id": "trace-xxx"
}
```

错误响应：

```json
{
 "code": "requirement_check_failed",
 "message": "需求检查未通过，不能生成 case",
 "details": {},
 "trace_id": "trace-xxx"
}
```

### 6.4 长任务 API

长任务统一采用创建任务 + 查询状态：

```text
POST /api/executions
GET /api/executions/{task_id}
POST /api/executions/{task_id}/cancel
POST /api/executions/{task_id}/retry
GET /api/executions/{task_id}/logs
GET /api/executions/{task_id}/report
```

文档解析、AI 生成、RAG 入库、移动端执行等耗时操作也应尽量复用任务状态模型。

## 7. Service / Runner / Skill / Evaluator 边界

### 7.1 Service

Service 是业务编排层。

典型 Service：

- `RequirementService`
- `CaseService`
- `ApiDefinitionService`
- `ExecutionService`
- `HarnessService`
- `ReportService`
- `AiOrchestrationService`
- `RagService`
- `SettingsService`
- `GovernanceService`

Service 负责：

- 业务状态流转。
- 数据一致性。
- 调用 Skill、Evaluator、Harness、ReportService。
- 写业务主表和过程记录。

Service 不负责：

- 具体 HTTP 请求执行。
- Appium 动作执行。
- Prompt 模板散落拼接。
- 报告 HTML 细节拼装。

### 7.2 Harness

Harness 是执行工程层，位于 Service 和 Runner 之间。

Harness 负责：

- 加载 case。
- 解析环境、变量、鉴权和密钥引用。
- 处理步骤依赖。
- 处理 setup、test、teardown。
- 记录测试数据创建和清理策略。
- 生成 Runner 可执行上下文。
- 收集执行过程中的观测信息，交给 ReportService。

建议拆分：

- `EnvironmentHarness`
- `VariableHarness`
- `DependencyHarness`
- `TestDataHarness`
- `ObservabilityHarness`

### 7.3 Runner

Runner 是协议执行适配器。

Runner 负责：

- 执行 HTTP 请求。
- 执行 Appium 动作。
- 执行 WebSocket / LLM 多轮测试。
- 返回标准化步骤结果、错误分类和产物引用。

Runner 不负责：

- 写正式 case。
- 改需求。
- 决定是否生成正式报告。
- 直接调用 AI。
- 直接读取密钥明文。

Runner 统一返回：

```json
{
 "status": "passed",
 "duration_ms": 1234,
 "steps": [],
 "artifacts": [],
 "error": null
}
```

### 7.4 Skill

Skill 是 AI 单能力封装。

典型 Skill：

- `RequirementParseSkill`
- `CaseGenerateSkill`
- `InterfaceParseSkill`
- `RagRetrieveSkill`
- `RequirementDiffSkill`
- `ConflictDetectSkill`
- `CaseImpactSkill`
- `CoverageEvaluateSkill`
- `FailureAnalysisSkill`
- `PromptOptimizeSkill`

Skill 负责：

- 定义输入契约。
- 选择 Prompt。
- 调用 AI Client。
- 解析和校验 AI 输出。
- 返回结构化结果。

Skill 不负责：

- 直接修改正式业务资产。
- 直接做人工确认。
- 自己决定 RAG 入库。
- 自己绕过 Evaluator。

### 7.5 Evaluator

Evaluator 是质量门禁层。

Evaluator 负责：

- 字段完整性检查。
- case 可执行性检查。
- 需求忠实度检查。
- 覆盖度检查。
- Phoenix 评分。

Evaluator 输出：

```json
{
 "passed": true,
 "score": 0.91,
 "label": "pass",
 "rationale": "字段完整且断言可执行",
 "issues": []
}
```

Evaluator 不负责：

- 替测试人员接受 case。
- 直接删除 AI 输出。
- 直接写正式 case。

## 8. 执行链路设计

### 8.1 接口 case 执行链路

```text
用户点击执行接口 case
 -> ExecutionService 创建 execution_task
 -> HarnessService 加载 case、环境、变量、鉴权
 -> DependencyHarness 处理步骤依赖
 -> ApiRunner 执行 HTTP 请求
 -> AssertionEvaluator 执行断言
 -> ExecutionService 写 step_results
 -> ReportService 生成报告
 -> 前端展示任务和报告
```

关键状态：

- `pending`
- `running`
- `passed`
- `failed`
- `blocked`
- `cancel_requested`
- `cancelled`
- `timeout`
- `need_review`

失败分类：

- 环境错误。
- 鉴权错误。
- 请求超时。
- 断言失败。
- 变量提取失败。
- 依赖步骤失败。
- Runner 异常。

### 8.2 移动端 case 执行链路

```text
用户选择移动端 case 和设备
 -> ExecutionService 创建任务
 -> MobileHarness 锁定设备、加载 App、合并 capability
 -> MobileRunner 创建 Appium session
 -> 执行点击、输入、等待、断言、截图步骤
 -> 失败时采集截图、XML、Appium 日志
 -> 释放设备锁
 -> ReportService 生成移动端报告
```

完整交付范围：

- 单设备。
- 单条移动端 case。
- Android 模拟器或本机设备。
- 基础 Appium 动作。
- 截图、XML、日志证据。

增强能力再补：

- 设备锁续约。
- session 复用。
- 元素备用定位。
- 公共步骤。
- 真机兼容增强。

### 8.3 需求到 AI case 链路

```text
上传需求文档
 -> 文本提取
 -> AI 解析需求点
 -> 逻辑检查、缺失检查、模糊点检查
 -> 人工确认并入库
 -> 触发 AI case 生成
 -> Evaluator 门禁
 -> 测试人员确认 / 编辑 / 拒绝
 -> 正式 case 资产
```

门禁原则：

- 检查未通过的需求不能生成 case。
- AI case 草稿不能直接入正式 case 库。
- 所有 AI 输出必须保留原始输入、原始输出、Prompt 版本、模型、耗时、错误信息和人工确认记录。

## 9. 报告证据链设计

报告中心定位为证据中心，不只是结果页。

### 9.1 报告主结构

报告应包含：

- 基础信息：任务、case、执行人、环境、设备、App、时间、耗时。
- 结论：passed、failed、blocked、cancelled、need_review。
- 步骤结果：每一步状态、耗时、输入、输出、错误。
- 证据产物：请求、响应、断言、变量、截图、XML、日志。
- 失败分析：失败分类、建议动作、AI 分析结果。
- 追溯关系：需求、接口、元素、case 版本、执行任务。

### 9.2 接口报告证据

- HTTP method、URL、headers、query、body。
- response status、headers、body。
- 断言 expected / actual。
- 变量提取结果。
- 环境变量快照。
- 脱敏状态。

### 9.3 移动端报告证据

- 设备 ID、系统版本、分辨率、占用信息。
- App package、versionName、versionCode、build。
- capability 快照。
- 失败步骤截图。
- XML 快照。
- Appium 日志。
- crash / ANR / 系统弹窗预留。

### 9.4 报告生成规则

- 任务完成才生成正式报告。
- 取消任务只保留任务日志，不生成正式质量结论。
- 报告导出默认脱敏。
- 报告产物默认设置保留时间，失败报告可长期保留。
- 报告必须可以从 task、case、接口、需求跳转访问。

## 10. 开发任务拆分建议

已有任务拆分文档：`docs/product/AI测试平台开发任务拆分.md`。

建议按以下技术顺序推进：

### 模块组一：框架与事实源

1. 平台基础框架与健康检查。
2. 项目、模块树与基础权限上下文。
3. 需求文档上传、原文预览与关系树挂载。
4. Case 中心基础资产管理。
5. 接口定义导入、确认与单接口调试。
6. 安全、脱敏、审计与配置中心。

### 模块组二：两条核心闭环

1. 需求文档解析、逻辑检查与入库门禁。
2. AI case 草稿生成、门禁检查与人工确认。
3. 接口 case 编写、Harness 基础能力与单 case 执行。
4. 接口执行报告与 HTML 证据链。

### 模块组三：移动端基础闭环

1. Android 设备识别、App 管理与元素资产基础链路。
2. 移动端 case 编辑、单设备执行与移动报告。
3. 统一执行中心、重试、取消与失败处理建议。

### 模块组四：工作台与验收

1. 首页质量驾驶舱与人工复核队列。
2. 端到端执行验收与种子数据。

## 11. 后端技术选型层与自动化技术选型

### 11.1 后端技术选型

当前模块推荐：

- Web 框架：FastAPI。
- ORM：SQLAlchemy 2。
- 数据校验：Pydantic 2。
- 数据库：SQLite 本地开发，生产建议 PostgreSQL 或 MySQL。
- 文件存储：本地 `uploads/`、`artifacts/`，生产可切对象存储。
- HTTP 执行：`requests` 或后面切 `httpx`。
- 文档解析：`pypdf`、`python-docx`、Markdown 原文读取。
- AI 调用：OpenAI SDK 兼容接口，支持 DeepSeek / OpenAI / 其他兼容模型。
- 评估：模块完整交付 规则 Evaluator，增强能力 接 Phoenix。

增强能力推荐：

- 后台任务：Celery / RQ / Arq 三选一。若保持 FastAPI 异步风格，建议 Arq；若团队熟悉 Redis + Celery，可用 Celery。
- 缓存和队列：Redis。
- 对象存储：MinIO 或云对象存储。
- 向量检索：pgvector、Milvus 或 Qdrant。单体平台建议先 pgvector，减少运维复杂度。
- 结构化日志：标准 logging + JSON formatter，后面接 Loki / ELK。

### 11.2 自动化技术选型

接口自动化：

- 模块完整交付：Python requests + 自研 `ApiRunner`。
- 增强能力：补充契约校验、OpenAPI schema 校验、并发执行、数据工厂。

移动端自动化：

- 模块完整交付：Appium 3 + uiautomator2，Android 模拟器 / 本机设备。
- 元素来源：Appium XML / Inspector 导入。
- 增强能力：设备锁续约、session 复用、真机兼容、备用定位、公共步骤。
- 预研能力：多设备并发、云真机、iOS、AI 视觉定位兜底。

Web / LLM / WebSocket：

- 增强能力成熟后再做。
- WebSocket Runner 应独立为 Runner 适配器，不混入 API Runner。
- LLM 多轮测试需要保留 prompt、上下文、流式消息、结束条件和 evaluator 证据。

## 12. 数据存储与 RAG 生命周期选型设计

### 12.1 存储分层

结构化数据库：

- 需求、case、接口、元素、执行、报告、AI 调用、Prompt、RAG chunk 元数据。

文件存储：

- 原始需求文档。
- 接口文档。
- APK。
- 报告 HTML。
- 截图、XML、日志。

对象存储：

- 当前模块可先本地。
- 增强能力 生产部署建议迁移 MinIO 或云对象存储。

向量存储：

- 模块完整交付 只预留字段。
- 增强能力推荐 pgvector 起步。
- 数据规模增大后再评估 Milvus / Qdrant。

### 12.2 RAG 生命周期

RAG 生命周期分为：

1. 来源采集。
2. 脱敏。
3. 切片。
4. 质量检查。
5. 入正式知识库或负样本库。
6. 检索召回。
7. AI 使用。
8. 人工反馈。
9. 版本更新或归档。

### 12.3 入库规则

允许进入正式知识库：

- 检查通过并人工确认的需求文档片段。
- 已确认 case。
- 已确认接口定义。
- 已确认失败报告摘要。
- 被人工确认有价值的变更记录。

不允许进入正式知识库：

- 检查未通过需求文档。
- 未确认 AI case 草稿。
- 未脱敏 request / response。
- 线上原始敏感日志。
- 模糊、冲突、未确认的 AI 输出。

负样本库：

- 被拒绝的 AI case 草稿。
- Phoenix 或规则 Evaluator 明确低分样本。
- 人工标注为错误的失败分析。

### 12.4 RAG 检索策略

模块完整交付：

- 可以先做结构化检索：项目、模块、需求版本、关键词。
- 保留召回日志。

增强能力：

- 启用 embedding。
- 粗排 + 精排。
- 记录召回片段、来源、权重、是否被采用、人工反馈。

## 13. Skill、Prompt 管理、生成与联动绑定

### 13.1 Skill Registry

建议维护 `skill_registry`：

- `skill_name`
- `display_name`
- `description`
- `input_schema`
- `output_schema`
- `enabled`
- `owner`
- `version`

Skill 作为稳定接口，Prompt 作为可迭代实现细节。

### 13.2 Prompt Template

建议维护 `prompt_templates`：

- `name`
- `skill_name`
- `case_type`
- `version`
- `template_text`
- `variables_json`
- `status`
- `evaluation_status`
- `activated_at`

Prompt 状态：

- `draft`
- `testing`
- `active`
- `deprecated`
- `rollback`

### 13.3 Skill 与 Prompt 绑定

建议维护 `skill_prompt_bindings`：

- 一个 Skill 可以绑定多个 Prompt。
- 按场景选择 Prompt，例如功能 case、接口 case、移动端 case。
- 每次 AI 调用必须记录 Skill、Prompt 版本、模型、输入摘要、输出、耗时、错误。

调用链路：

```text
AiOrchestrationService
 -> SkillRegistry 查找 Skill
 -> PromptRegistry 选择 active Prompt
 -> PromptRenderer 注入变量
 -> AiClient 调用模型
 -> Skill 解析输出
 -> Evaluator 评估
 -> Service 写入草稿 / 检查结果 / 调用日志
```

### 13.4 Prompt 生成与优化

Prompt 可以由人工维护，也可以由 `PromptOptimizeSkill` 生成建议。

上线规则：

- Prompt 修改后必须先进入 `testing`。
- 跑评估集或样例集。
- 记录评分和人工确认。
- 通过后才能切换为 `active`。
- 保留回滚版本。

### 13.5 与业务流程联动

- 需求解析绑定 `RequirementParseSkill`。
- case 生成绑定 `CaseGenerateSkill`。
- 接口文档解析绑定 `InterfaceParseSkill`。
- 覆盖率评估绑定 `CoverageEvaluateSkill`。
- 失败归因绑定 `FailureAnalysisSkill`。
- 变更影响绑定 `CaseImpactSkill`。

所有业务页面只调用 Service，不直接选择 Prompt。Prompt 选择由 AI 能力中心配置和 `AiOrchestrationService` 执行。

## 14. 后面部署服务器环境依赖

### 14.1 模块完整交付 单机部署依赖

基础环境：

- Linux 服务器，建议 Ubuntu 22.04+。
- Python 3.11+。
- Node.js 20+。
- pnpm 或 npm。
- SQLite / PostgreSQL / MySQL。
- Nginx。
- Git。

后端服务：

- FastAPI + Uvicorn。
- 后端环境变量。
- 上传目录 `uploads/`。
- 产物目录 `artifacts/`。
- 日志目录 `logs/`。

前端服务：

- Vite 构建静态文件。
- Nginx 托管静态资源。
- Nginx 反向代理 `/api` 到后端。

移动端执行：

- Java JDK 17。
- Android SDK。
- Android platform-tools。
- adb。
- Appium 3。
- appium-uiautomator2-driver。
- Android 模拟器或连接设备。
- Appium server 启动脚本。

AI 能力：

- 模型 API Key。
- 模型 base URL。
- 模型连接检测。
- 超时、重试、token 限制配置。

### 14.2 生产增强依赖

- Redis：后台任务、缓存、队列。
- Celery / RQ / Arq：长任务执行。
- MinIO 或对象存储：文档、截图、报告、日志。
- PostgreSQL + pgvector：结构化数据和向量检索。
- 结构化日志系统：Loki / ELK。
- 监控：Prometheus + Grafana。
- 进程管理：systemd、Docker Compose 或 Kubernetes。

### 14.3 部署目录建议

```text
/opt/ai-test-platform
 backend/
 frontend/
 uploads/
 artifacts/
 logs/
 appium/
 config/
 backups/
```

### 14.4 运维关注点

- 定期备份数据库。
- 定期清理过期报告产物。
- 失败报告可标记长期保留。
- 密钥不写日志。
- AI 调用成本需要按功能和模型统计。
- Appium 设备异常后要释放锁。
- 生产环境不建议使用 SQLite。

## 15. 架构深化建议

结合当前代码和目标架构，继续做以下深化：

1. 建立 `Harness` 模块，把环境、变量、依赖、测试数据和证据增强从 Runner / Service 中抽出来。
2. 建立统一 `RunnerResult` 契约，让 API、Mobile、WebSocket Runner 都返回一致结构。
3. 建立 `ReportEvidence` 结构，报告中心不再从各类 Runner 临时拼字段。
4. 建立 `AiOrchestrationService`，统一 Skill、Prompt、Evaluator、AI 调用日志。
5. 建立 `PromptRegistry` 和 `SkillRegistry`，避免 Prompt 散落在代码里。
6. 建立 `security/masking.py` 和 `security/secrets.py`，让脱敏和密钥引用成为平台底座。
7. 将 `midscene_ios`、`vision_automation` 标记为 预研能力，避免影响 基础业务链路理解。
8. 为技术设计中的移动端 模块完整交付/移动端完整交付 差异补一条 ADR 或直接修订分期章节。

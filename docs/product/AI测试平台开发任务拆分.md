# AI 测试平台开发任务拆分

## 1. 拆分原则

本文档基于以下文档整理：

- `docs/product/AI测试平台PRD.md`
- `docs/technical/AI测试平台技术设计文档.md`
- `docs/product/AI测试平台模块功能逻辑确认.md`
- `CONTEXT.md`

任务拆分遵循垂直切片原则：

- 每个任务尽量交付一条可演示、可验收的端到端能力。
- 每个任务应覆盖必要的数据模型、API、前端页面、状态流转、测试和验收。
- 避免只拆成数据库、后端、前端等横向任务。
- AI 输出影响正式资产时，必须保留证据、门禁结果和人工确认边界。
- 每个可交给 AI agent 的任务必须明确：PRD 条款、输入、输出、建议修改文件、禁止绕过规则、测试命令和验收证据。

### 1.1 AI agent 可执行任务格式

后续新增或细化任务时，统一使用以下格式。AI agent 可以直接按该格式进入代码实现，不需要再反推需求边界。

```text
任务编号：
任务目标：
PRD 对应条款：
前置依赖：
输入：
输出：
建议修改文件：
数据模型：
API / Service：
前端页面 / 交互：
状态流转：
Guardrails：
测试要求：
验收证据：
非范围：
```

字段说明：

- `PRD 对应条款` 必须写到 `FR-*`、`AC-*` 或模块 Guardrails，不能只写模块名。
- `输入` 写清楚用户输入、上游数据、配置、AI 返回或测试夹具。
- `输出` 写清楚数据库记录、API 响应、页面状态、报告或待办。
- `建议修改文件` 写到目录或具体文件，方便 AI agent 直接定位。
- `Guardrails` 写清不可绕过规则，例如 AI 不降级、人工确认边界、正式资产不可自动修改。
- `测试要求` 至少包含后端单测；涉及前端时必须包含构建或组件测试；涉及执行链路时必须包含绕过路径测试。
- `验收证据` 必须能在最终回复中复述，例如测试命令、通过数量、构建结果、手工验收清单。

### 1.2 PRD 对齐审计结论

对比 `docs/product/AI测试平台PRD.md` 后，当前拆分文档需要补齐和澄清以下内容：

- `AI 能力中心` 在 PRD 中是一级模块，但原任务拆分只散落在需求、Case 和系统设置中；需要增加独立任务覆盖 AI 任务记录、RAG、Prompt、Evaluator、模型效果、反馈样本库、成本统计和 AI 不降级。
- `变更中心` 在 PRD 中是一级模块，但原任务拆分缺少独立开发任务；需要补齐变更记录、影响分析、回归推荐、case 修改草稿和人工确认闭环。
- `待办中心` 在 PRD 中是一级模块，原任务拆分放在首页任务中，粒度不足；需要补齐来源类型、优先级、状态流转、来源跳转和自动核销。
- `Bug 中心` 是未来模块，当前不实现完整外部同步，但 PRD 要求保留标准模型和接入点；需要增加预留任务，避免后续 case、report、change 无法关联缺陷对象。
- 需求中心与 Case 中心补缺专项已经覆盖问题项、修订版、AI 不降级、草稿确认、废弃隔离和负样本闭环；新版 PRD 进一步要求补齐 `RequirementBaseline`、`RequirementDiff`、`CoverageMatrix`、`CaseGenerationPlan` 和 `AutomationCandidate`，因此本文新增 `RCP-*` 全量开发任务，保证 AI agent 可按长任务列表逐项实现。
- 旧任务 4 / 5 是早期“需求入库 -> AI case 草稿”的过渡切片，不再代表 PRD 合规主链路。PRD 合规主链路必须以 RCP 为准：历史基线 -> 差异分析 -> 覆盖矩阵 -> 生成计划 -> 分类型 case 草稿。
- 原任务 3、4、5、6 的当前状态中仍有未完成项：PDF/Word 文本提取、原始文件下载、删除 / 归档影响提示、历史同模块需求对比、解析失败重试 UI、合并 AI case 草稿、Case 健康度展示。这些应在专项任务或后续模块任务中有明确承接。

当前按 `CONTEXT.md` 口径处理：平台按功能模块完整闭环开发。以下三条基础业务链路只作为早期演示切片和工程底座，不得作为新版 PRD 的最终合规路径：

1. 需求文档 -> AI case 草稿 -> 测试人员确认 -> case 资产。该链路在 RCP 完成后必须收敛为 `RequirementBaseline -> RequirementDiff -> CoverageMatrix -> CaseGenerationPlan -> AI case 草稿 -> 人工确认 -> case 资产`。
2. API case -> 单 case 执行 / 调试 -> 报告。
3. Android 设备 / 移动端基础路径 -> 设备识别 -> 移动 case 编辑 / 执行证据。

## 2. 任务总览

| 序号 | 任务名称 | 类型 | 前置依赖 | 是否适合 AI agent |
|---|---|---|---|---|
| 1 | 平台基础框架与健康检查 | AFK | 无 | 是 |
| 2 | 项目、模块树与基础权限上下文 | AFK | 1 | 是 |
| 3 | 需求文档上传、原文预览与关系树挂载 | AFK | 1、2 | 是 |
| 4 | 需求文档解析、逻辑检查与入库门禁 | HITL | 3 | 部分适合 |
| 5 | AI case 草稿生成、门禁检查与人工确认 | HITL | 4 | 部分适合 |
| 6 | Case 中心基础资产管理 | AFK | 2、5 | 是 |
| 7 | 接口定义导入、确认与单接口调试 | AFK | 1、2 | 是 |
| 8 | 接口 case 编写、Harness 基础能力与单 case 执行 | AFK | 6、7 | 是 |
| 9 | 接口执行报告与 HTML 证据链 | AFK | 8 | 是 |
| 10 | Android 设备识别、App 管理与元素资产基础链路 | HITL | 1、2、6 | 部分适合 |
| 11 | 移动端 case 编辑、单设备执行与移动报告 | HITL | 10 | 部分适合 |
| 12 | 统一执行中心、重试、取消与失败处理建议 | AFK | 8、11 | 是 |
| 13 | 首页质量驾驶舱与人工复核队列 | AFK | 4、5、8、9、12 | 是 |
| 14 | 安全、脱敏、审计与配置中心 | AFK | 1、7、9 | 是 |
| 15 | 端到端执行验收与种子数据 | HITL | 1-14 | 部分适合 |
| 16 | AI 能力中心治理闭环 | AFK | 4、5、13、14 | 是 |
| 17 | 变更中心影响分析与回归推荐 | HITL | 3、6、7、8、16 | 部分适合 |
| 18 | 待办中心独立复核队列 | AFK | 4、5、9、12、16、17 | 是 |
| 19 | Bug 标准模型与接入点预留 | AFK | 6、9、12、17 | 是 |

说明：

- AFK：边界清晰，可交给 AI agent 独立实现并提交验收结果。
- HITL：需要人工参与设计确认、环境联调或最终验收。

## 3. 详细任务

### 任务 1：平台基础框架与健康检查

#### 任务目标

搭建可运行的前后端基础骨架，形成所有模块的统一工程规范。

#### 涉及模块

- 系统框架
- 首页 / 质量驾驶舱
- 系统设置
- 公共组件
- 后端基础服务

#### 前置依赖

无。

#### 开发内容

- 初始化后端 FastAPI 应用、路由分组、统一响应、异常处理、配置加载。
- 初始化数据库连接、迁移机制、基础表结构占位。
- 初始化前端路由、页面布局、导航菜单、空状态页面。
- 增加 `/health`、系统版本、数据库连通性检查。
- 建立最小测试、启动脚本、环境变量样例。

#### 验收标准

- 本地能一键启动前后端。
- 首页能访问，导航包含 PRD 确认的一级模块。
- `/health` 返回服务、数据库、配置加载状态。
- 后端至少有基础单测，前端至少能通过构建检查。

#### 是否适合交给 AI agent 执行

适合。该任务为 AFK 类型，边界清楚，适合作为第一个工程化任务。

---

### 任务 2：项目、模块树与基础权限上下文

#### 任务目标

建立平台所有资产的归属上下文，避免需求、case、接口、报告后面无项目和模块归属。

#### 涉及模块

- 系统设置
- 需求中心
- Case 中心
- 接口中心
- 首页 / 质量驾驶舱

#### 前置依赖

- 任务 1：平台基础框架与健康检查

#### 开发内容

- 实现项目 `projects` 和模块树 `module_nodes` 的基础 CRUD。
- 支持业务域 -> 模块 -> 功能的层级结构。
- 前端提供项目切换、模块树查看和简单维护能力。
- 后端所有核心资源预留 `project_id`、`module_id`。
- 实现基础角色：管理员、测试人员、只读用户。

#### 验收标准

- 用户可以创建项目和模块树。
- 创建需求、case、接口时可以选择项目和模块。
- 只读用户不能创建、修改、删除资产。
- 首页指标可以按当前项目过滤。

#### 是否适合交给 AI agent 执行

适合。该任务为 AFK 类型。

---

### 任务 3：需求文档上传、原文预览与关系树挂载

#### 任务目标

先把需求中心变成可信文档库，而不是普通上传页。

#### 涉及模块

- 需求中心
- 文件存储
- 模块树
- 系统设置

#### 前置依赖

- 任务 1：平台基础框架与健康检查
- 任务 2：项目、模块树与基础权限上下文

#### 开发内容

- 实现需求文档上传，支持 PDF、Word、Markdown。
- 保存原始文件、文件元信息、上传人、文件指纹。
- 支持需求关系树挂载：业务域 -> 模块 -> 功能 -> 需求版本。
- 支持文档列表、树形视图、文档详情、原文预览和下载。
- 支持移动、重命名、修改元信息、归档、软删除。
- 删除或归档前展示影响提示占位：需求条目数、case 数、知识库片段数。

#### 验收标准

- 用户可以上传文档并在需求树下看到它。
- 用户可以在线查看原始文档或下载原始文件。
- 文档可以移动到其他功能或版本节点。
- 软删除后不在默认列表展示，但可在回收站或归档视图看到。
- 同名或重复文件有提示，不直接静默覆盖。

#### 是否适合交给 AI agent 执行

适合。该任务为 AFK 类型。

#### 当前状态（2026-05-19 任务 3 切片完成）

- [x] 后端：`requirement_tree_nodes` 模型与 `/api/requirements/tree` CRUD（domain/module/feature/version）。
- [x] 后端：文档挂载 `/api/requirements/documents/{id}/mount`、归档 / 软删除 / 恢复、重复文件 `file_hash` 检测。
- [x] 前端：需求中心对接真实需求树，支持节点 CRUD、按节点过滤文档、挂载、回收站 / 归档视图。
- [x] 测试：`test_requirement_tree.py` 覆盖树 CRUD 与文档挂载。
- [ ] 未完成：原始文件下载、删除 / 归档前影响提示（需求条目 / case / 知识库计数）、完整 PDF/Word 文本提取链路。

---

### 任务 4：需求文档解析、逻辑检查与入库门禁

#### 任务目标

让需求文档进入 case 生成前，先经过解析、检查和人工确认。

#### 涉及模块

- 需求中心
- AI 能力中心
- 待办队列
- RAG 预留

#### 前置依赖

- 任务 3：需求文档上传、原文预览与关系树挂载

#### 开发内容

- 实现文本提取：PDF、Word、Markdown。
- 实现 `RequirementParseSkill` 的基础封装，输出结构化需求点、风险点、原文片段。
- 实现基础检查：缺失、模糊点、冲突项、历史同模块需求对比占位。
- 建立 `requirement_items` 和解析结果确认页面。
- 文档状态流转：未解析、解析中、待确认、检查未通过、已入库。
- 检查未通过时阻止 case 生成，只允许查看问题和重新上传 / 重新解析。

#### 验收标准

- 上传文档后可以触发解析并看到结构化需求点。
- 每个需求点能看到原文依据。
- 有冲突、模糊或缺失问题时，文档不能进入 case 生成。
- 人工确认后，需求点成为正式 case 生成输入。
- 解析失败有明确错误原因和重试入口。

#### 是否适合交给 AI agent 执行

部分适合。该任务为 HITL 类型，AI 调用协议、检查规则和门禁阈值需要人工确认，基础实现可交给 AI agent。

#### 当前状态（2026-05-19 任务 4 切片完成）

- [x] 后端：`RequirementParseSkill` 集成，`requirement_items` 持久化，解析状态机 `unparsed → parsing → pending_review | check_failed → stored`。
- [x] 后端：`/api/requirements/documents/{id}/parse`、`/confirm`；`parse_status != stored` 时阻止 `/api/ai/generate-cases-from-document`。
- [x] 前端：需求中心展示解析状态、触发解析、确认入库、结构化需求点与检查问题列表。
- [x] 测试：`test_requirement_parse_gate.py` 覆盖解析门禁与 case 生成拦截。
- [ ] 未完成：历史同模块需求对比、待办队列联动、PDF/Word 专用提取器、解析失败重试 UI 细化。

---

### 任务 5：AI case 草稿生成、门禁检查与人工确认

#### 任务目标

跑通早期“需求文档 -> AI case 草稿 -> 测试人员确认 -> 正式 case”的过渡切片。新版 PRD 合规实现中，本任务不得继续保留绕过 `CaseGenerationPlan` 的生成入口；生成能力最终必须迁移到 RCP-13 / RCP-14 / RCP-15 / RCP-17。

#### 涉及模块

- 需求中心
- Case 中心
- AI 能力中心
- 待办队列

#### 前置依赖

- 任务 4：需求文档解析、逻辑检查与入库门禁

#### 开发内容

- 基于已入库需求点触发 case 草稿生成。该能力仅作为过渡实现；RCP-01 必须审计并标记旧直生成入口废弃，RCP-14 之后统一改为按生成计划生成。
- 保存 `ai_case_drafts`：原始 AI 输出、结构化内容、来源需求、状态。
- 实现基础字段完整性和规则门禁。
- 前端提供 AI case 待确认页：接受、编辑后接受、拒绝、合并占位。
- 接受后写入正式 `test_cases` 和 `case_steps`。
- 拒绝后记录拒绝原因，为负样本库预留。

#### 验收标准

- 已入库需求可以生成 AI case 草稿。
- 草稿必须经过门禁检查和人工确认后才能进入正式 case。
- 正式 case 能追溯到需求点、原文片段、AI 原始输出和确认人。
- 字段缺失的草稿不能同步为正式 case。
- 拒绝草稿后不会污染正式 case 库。

#### 是否适合交给 AI agent 执行

部分适合。该任务为 HITL 类型，页面和状态机适合 AI agent，case 模板和门禁规则建议人工先定。

#### 当前状态（2026-05-19 后台 worker 模块完整交付）

- [x] 已完成 页面完整性切片：需求中心保留 AI 草稿确认入口，Case 中心展示 AI 确认后的 case 进入正式资产库的边界。
- [ ] 未完成完整任务：AI case 草稿持久化、门禁评估、接受 / 编辑后接受 / 拒绝 / 合并状态机、确认人和确认时间追溯仍需后面实现。

---

### 任务 6：Case 中心基础资产管理

#### 任务目标

提供统一 case 资产中心，承接人工 case、AI case、接口 case 和移动端 case 的共同管理。

#### 涉及模块

- Case 中心
- 需求中心
- 接口中心
- 移动端执行中心

#### 前置依赖

- 任务 2：项目、模块树与基础权限上下文
- 任务 5：AI case 草稿生成、门禁检查与人工确认

#### 开发内容

- 实现 `test_cases`、`case_steps`、`case_versions` 的基础 CRUD。
- 支持 case 类型：功能 case、接口 case、移动端 case。
- 支持统一状态：草稿、待确认、已启用、已废弃。
- case 详情展示来源需求、原文片段、接口、元素、AI 生成依据、确认记录。
- 支持复制、编辑、废弃、版本快照。
- 支持 模块完整交付 / 重要性标记，作为当前回归依据。

#### 验收标准

- 用户可以创建、编辑、查看、废弃 case。
- AI 确认后的 case 能在 Case 中心统一查看。
- 修改步骤、断言、来源、接口或元素后，需要重新确认或验证。
- case 详情有完整来源追溯。
- 模块完整交付 / 重要性能用于列表筛选。

#### 是否适合交给 AI agent 执行

适合。该任务为 AFK 类型。

#### 当前状态（2026-05-19 任务 6 深化切片完成）

- [x] 后端：`case_versions` 模型；更新前自动快照；`GET /api/cases/{id}/versions`、`POST /api/cases/{id}/deprecate`。
- [x] 后端：列表仅展示 `lifecycle_status=active` 且 `is_active=1` 的 case；废弃后移出正式资产列表。
- [x] 前端：Case 中心展示当前版本号、版本历史列表、废弃 case 操作。
- [x] 测试：`test_case_version.py` 覆盖版本快照与废弃。
- [ ] 未完成：复制 case、关键字段修改后需复核状态、完整来源原文片段 / 接口 / 元素关联视图。

---

### 任务 7：接口定义导入、确认与单接口调试

#### 任务目标

建立接口中心事实源，让接口 case 不再重复维护接口信息。

#### 涉及模块

- 接口中心
- AI 能力中心
- 执行中心
- 报告中心

#### 前置依赖

- 任务 1：平台基础框架与健康检查
- 任务 2：项目、模块树与基础权限上下文

#### 开发内容

- 实现接口定义 CRUD：method、path、headers、params、body schema、response schema、状态码。
- 支持接口文档上传和基础解析，AI 解析可先做简单结构化。
- 支持候选接口 -> 人工确认 -> 可引用接口。
- 实现环境、变量集、鉴权配置基础能力。
- 实现单接口调试，保存请求、响应、耗时、错误原因。
- 接口废弃后禁止被新 case 引用或执行。

#### 验收标准

- 用户可以维护接口定义并标记为已确认。
- 用户可以选择环境和变量执行单接口调试。
- 调试失败展示可行动错误原因。
- 已废弃接口不能被 case 执行。
- 接口详情能看到最近调试结果。

#### 是否适合交给 AI agent 执行

适合。该任务为 AFK 类型。

---

### 任务 8：接口 case 编写、Harness 基础能力与单 case 执行

#### 任务目标

跑通“接口 case -> 执行任务 -> Runner 执行 -> 步骤结果”的最小执行链路。

#### 涉及模块

- Case 中心
- 接口中心
- 执行中心
- Harness
- Runner

#### 前置依赖

- 任务 6：Case 中心基础资产管理
- 任务 7：接口定义导入、确认与单接口调试

#### 开发内容

- 支持接口 case 步骤引用接口定义。
- 支持请求参数、变量提取、断言、超时、是否继续执行。
- 实现 `execution_tasks` 和 `execution_step_results`。
- 实现最小 `HarnessService`：加载 case、环境变量、变量注入、结果标准化。
- 实现 `ApiRunner`：执行 HTTP 请求，返回请求、响应、耗时、断言结果。
- 支持任务状态：pending、running、passed、failed、cancelled。

#### 验收标准

- 用户可以从接口 case 页面发起单 case 执行。
- 执行中心能看到任务状态、步骤状态、耗时和失败原因。
- 断言失败和请求失败能区分展示。
- 变量提取结果能传递给后面步骤。
- 任务取消后不生成正式报告，只保留任务日志。

#### 是否适合交给 AI agent 执行

适合。该任务为 AFK 类型，但需要人工提供一组真实接口样例用于验收。

---

### 任务 9：接口执行报告与 HTML 证据链

#### 任务目标

让接口执行结果可复盘，而不是只显示成功 / 失败。

#### 涉及模块

- 报告中心
- 执行中心
- 接口中心
- Case 中心

#### 前置依赖

- 任务 8：接口 case 编写、Harness 基础能力与单 case 执行

#### 开发内容

- 实现 `test_reports`、`report_artifacts`。
- 生成接口单 case HTML 报告。
- 报告包含 request、response、headers、断言 expected / actual、变量上下文、耗时、错误堆栈。
- 支持报告在线预览和下载。
- 实现基础脱敏：Authorization、Cookie、token、password。
- 报告关联 task、case、接口、环境。

#### 验收标准

- 每次完成的接口执行都生成报告。
- 报告能从执行任务、case 详情进入。
- 失败报告能定位到具体步骤和断言。
- 导出报告默认脱敏。
- 报告缺少核心证据时不允许标记为可复盘。

#### 是否适合交给 AI agent 执行

适合。该任务为 AFK 类型。

---

### 任务 10：Android 设备识别、App 管理与元素资产基础链路

#### 任务目标

建立移动端自动化执行的基础资产，让移动 case 有设备、App、元素上下文。

#### 涉及模块

- 移动端执行中心
- 系统设置
- Case 中心
- 报告中心

#### 前置依赖

- 任务 1：平台基础框架与健康检查
- 任务 2：项目、模块树与基础权限上下文
- 任务 6：Case 中心基础资产管理

#### 开发内容

- 实现 Android 设备列表：模拟器 / 真机识别、在线状态、系统版本、分辨率、占用状态。
- 实现设备锁基础逻辑，异常释放。
- 支持 APK 上传或登记 App 信息：package、versionName、versionCode、build。
- 支持 Appium XML 导入，生成元素资产。
- 元素绑定页面、模块、主定位、可读名称。
- 提供移动端执行中心基础页面。

#### 验收标准

- 平台能展示当前可用 Android 设备。
- 设备异常退出后能释放占用锁。
- App 信息能绑定到执行任务和报告。
- XML 导入后能生成可被移动 case 引用的元素。
- 不支持 iOS、云真机、多设备调度。

#### 是否适合交给 AI agent 执行

部分适合。该任务为 HITL 类型，设备和 Appium 环境依赖本机，需要人工协助验收。

---

### 任务 11：移动端 case 编辑、单设备执行与移动报告

#### 任务目标

跑通“移动端 case -> 单设备 Appium 执行 -> 截图 / XML / 日志报告”的 移动端完整闭环。

#### 涉及模块

- 移动端执行中心
- Case 中心
- 执行中心
- 报告中心
- Runner

#### 前置依赖

- 任务 10：Android 设备识别、App 管理与元素资产基础链路

#### 开发内容

- 支持移动端 case 步骤：点击、输入、等待、断言、截图。
- 正式移动端 case 必须引用元素库；调试态可临时写 locator。
- 实现 `MobileRunner` 基础动作执行。
- 执行任务记录设备、App、capability、步骤状态。
- 失败时采集截图、XML、Appium 日志、错误信息。
- 报告中心展示移动端证据链。

#### 验收标准

- 用户可以选择单设备执行单条移动端 case。
- 执行报告绑定 App package、version、build。
- 失败报告包含失败步骤、截图、XML、Appium 日志中的关键证据。
- 正式移动 case 不允许只保存裸 locator。
- 不做多设备并发和 AI 视觉兜底。

#### 是否适合交给 AI agent 执行

部分适合。该任务为 HITL 类型，代码可交给 AI agent，设备联调和稳定性验收需要人工参与。

---

### 任务 12：统一执行中心、重试、取消与失败处理建议

#### 任务目标

把接口和移动端执行统一到同一个任务控制台。

#### 涉及模块

- 执行中心
- Case 中心
- 接口中心
- 移动端执行中心
- 报告中心

#### 前置依赖

- 任务 8：接口 case 编写、Harness 基础能力与单 case 执行
- 任务 11：移动端 case 编辑、单设备执行与移动报告

#### 开发内容

- 执行中心展示所有 `execution_tasks`。
- 支持按类型、状态、项目、执行人筛选。
- 支持取消、重跑、最多 3 次重试策略。
- 展示实时 / 准实时日志、步骤进度、失败分类。
- 失败后提供处理建议：重跑、检查环境、修复 case、标记 bug 占位、人工复核。
- 取消任务只保留日志，不生成正式报告。

#### 验收标准

- 接口和移动端任务都能在执行中心统一查看。
- 任务状态 100% 可追踪。
- 自动重试不超过 3 次。
- 取消任务不会生成正式质量结论。
- 用户能从失败任务跳转到 case 和报告。

#### 是否适合交给 AI agent 执行

适合。该任务为 AFK 类型。

---

### 任务 13：首页质量驾驶舱与人工复核队列

#### 任务目标

把平台从多个功能页串成日常工作入口。

#### 涉及模块

- 首页 / 质量驾驶舱
- 待办队列
- 需求中心
- Case 中心
- 执行中心
- 报告中心
- AI 能力中心

#### 前置依赖

- 任务 4：需求文档解析、逻辑检查与入库门禁
- 任务 5：AI case 草稿生成、门禁检查与人工确认
- 任务 8：接口 case 编写、Harness 基础能力与单 case 执行
- 任务 9：接口执行报告与 HTML 证据链
- 任务 12：统一执行中心、重试、取消与失败处理建议

#### 开发内容

- 首页展示需求数、case 数、接口数、设备状态、今日执行、失败任务、AI 待确认 case。
- 展示风险摘要，但必须带证据来源、置信度、触发原因、人工确认边界。
- 建立 `todo_items` 基础表。
- 待办来源：需求冲突、AI case 待确认、失败报告复核、设备异常、变更影响占位。
- 首页指标和待办支持跳转来源对象。

#### 验收标准

- 测试经理进入首页 1 分钟内能判断当前版本状态。
- 所有首页指标都能跳转到来源页面。
- AI 风险摘要不能只有自然语言结论，必须有证据。
- 用户能在待办队列处理 AI case 确认和失败报告复核。
- 待办中心不做复杂流程引擎。

#### 是否适合交给 AI agent 执行

适合。该任务为 AFK 类型。

---

### 任务 14：安全、脱敏、审计与配置中心

#### 任务目标

补齐 完整交付前的安全底座，避免报告、AI 输入和日志泄露敏感信息。

#### 涉及模块

- 系统设置
- 报告中心
- AI 能力中心
- 接口中心
- 执行中心

#### 前置依赖

- 任务 1：平台基础框架与健康检查
- 任务 7：接口定义导入、确认与单接口调试
- 任务 9：接口执行报告与 HTML 证据链

#### 开发内容

- 实现统一脱敏函数和敏感字段规则。
- 密钥只允许写入和引用，不允许接口明文返回。
- 报告导出默认脱敏。
- AI 输入、RAG 入库、Phoenix 输入前调用脱敏。
- 查看未脱敏内容记录审计日志。
- 配置中心支持模型配置、环境配置、Appium capability、报告保留策略。

#### 验收标准

- Authorization、Cookie、token、password 不出现在普通日志和默认报告中。
- 密钥接口不返回明文。
- 报告导出默认脱敏。
- 修改关键配置有操作记录。
- AI 调用前能确认已走脱敏处理。

#### 是否适合交给 AI agent 执行

适合。该任务为 AFK 类型，但脱敏规则清单需要人工确认。

#### 当前状态（2026-05-19 前端全量重建）

- [x] 已完成系统设置前端 模块完整交付：Tab 化展示 AI 模型、安全脱敏、报告策略，对接 `/api/settings/*`。
- [x] 已落实密钥展示边界：前端仅展示 `api_key_masked`，编辑时空 key 不覆盖已保存密钥。
- [x] 已补充前端验证：`verify-settings-page.mjs`。
- [ ] 未完成完整任务：审计日志 UI、报告导出脱敏验收、AI 调用前脱敏确认链、Appium / 环境配置页仍待剩余切片。

---

### 任务 15：端到端执行验收与种子数据

#### 任务目标

把所有 模块完整交付 垂直链路用固定样例跑通，形成可回归的验收包。

#### 涉及模块

- 全平台

#### 前置依赖

- 任务 1-14

#### 开发内容

- 准备样例需求文档、接口文档、接口服务 mock、移动端样例 App 或 Demo 页面。
- 编写端到端验收脚本或手工验收清单。
- 覆盖三条主链路：
 - 需求文档 -> AI case 草稿 -> 人工确认 -> case 资产。
 - API case -> 单 case 执行 / 调试 -> HTML 报告。
 - Android 设备 -> 移动 case -> Appium 执行 -> 截图 / XML / 日志报告。
- 记录已知限制和 增强能力 待办。
- 固化冒烟测试入口。

#### 验收标准

- 三条主链路都能从 UI 完整跑通。
- 每条链路都有可复用测试数据。
- 完整验收失败能定位到具体模块和任务。
- 验收报告包含通过项、失败项、阻塞项和后续建议。
- 新人可以按验收文档复现平台核心能力。

#### 是否适合交给 AI agent 执行

部分适合。该任务为 HITL 类型，验收脚本和清单适合 AI agent，最终验收需要人确认。

---

### 任务 16：AI 能力中心治理闭环

#### 任务目标

把 AI 能力从散落在各模块中的调用点，收敛成可配置、可追踪、可评估、可复盘的一级模块，支撑需求解析、case 生成、失败分析、覆盖评估、RAG、Prompt、Evaluator、反馈样本库和成本统计。

#### PRD 对应条款

- `FR-AI-001` - `FR-AI-013`
- `FR-SET-012`
- `AC-AI-001` - `AC-AI-007`
- AI 能力中心 Guardrails：AI 输出不能绕过人工确认；AI 调用失败不允许降级。

#### 涉及模块

- AI 能力中心
- 系统设置
- 需求中心
- Case 中心
- 待办中心

#### 前置依赖

- 任务 4：需求文档解析、逻辑检查与入库门禁
- 任务 5：AI case 草稿生成、门禁检查与人工确认
- 任务 13：首页质量驾驶舱与人工复核队列
- 任务 14：安全、脱敏、审计与配置中心

#### 输入

- 模型配置、API Key、base URL、模型状态。
- Prompt / Skill 配置。
- 需求文档、case 草稿、执行日志、报告证据、反馈样本。
- Evaluator 阈值和评估集。

#### 输出

- AI 任务记录：输入摘要、输出摘要、模型、Prompt / Skill 版本、耗时、token、状态、失败原因。
- RAG 知识片段和反馈样本。
- Prompt / Skill 版本和评估结果。
- Evaluator 门禁结论。
- AI 成本和模型效果统计。

#### 建议修改文件

- `backend/app/models/ai_task.py`
- `backend/app/models/ai_feedback_sample.py`
- `backend/app/models/prompt_version.py`
- `backend/app/services/ai_client.py`
- `backend/app/services/phoenix_evaluator.py`
- `backend/app/services/negative_case_sample_service.py`
- `backend/app/skills/*`
- `backend/app/routers/ai_service.py`
- `frontend/src/modules/ai/`
- `frontend/src/modules/settings/`

#### 数据模型

- `AITaskRecord`：记录 AI 调用、状态、耗时、token、成本、失败原因、关联对象。
- `PromptVersion`：记录 Prompt 内容、版本、适用模块、评估状态。
- `AIFeedbackSample`：记录正样本、负样本、拒绝原因、用户反馈、来源对象和脱敏内容。
- `RagFragment`：记录知识片段、来源、向量集合、更新时间和引用次数。

#### API / Service

- `GET /api/ai/tasks`：查询 AI 任务记录。
- `GET /api/ai/tasks/{id}`：查看 AI 输入输出摘要和失败原因。
- `GET /api/ai/feedback-samples`：查询反馈样本。
- `POST /api/ai/prompts/{id}/evaluate`：执行 Prompt 评估集。
- `GET /api/ai/model-metrics`：查看模型耗时、失败率、成本和采纳率。
- AI Service 必须统一抛出可行动错误，不能返回伪成功文本。

#### 前端页面 / 交互

- AI 能力中心首页：展示任务量、失败率、平均耗时、采纳率、成本估算。
- AI 任务列表：支持按模块、模型、状态、日期筛选。
- Prompt / Skill 管理：展示版本、适用模块、评估结果和最近修改人。
- 反馈样本库：展示正 / 负样本、来源对象、脱敏内容和影响模块。
- 模型效果页：展示不同模型在需求解析、case 生成、失败分析上的效果统计。

#### 状态流转

```text
created -> running -> success | failed | blocked_by_config | blocked_by_evaluator
```

#### Guardrails

- AI 未配置、连接失败、鉴权失败、模型不可用或超时，必须直接失败并返回错误，不允许规则或模板降级。
- AI 输出不得直接修改正式需求、正式 case、质量结论或变更结果。
- AI 输入、RAG 入库和反馈样本必须先脱敏。
- Prompt 修改后必须记录版本；需要进入正式链路的 Prompt 必须通过评估集。

#### 验收标准

- 任一 AI 调用都能查询到任务记录。
- AI 失败有明确失败原因、关联对象和可行动错误提示。
- Prompt / Skill 版本可追踪。
- 反馈样本可按来源对象查询。
- 模型效果和成本可按功能模块聚合。

#### 测试要求

- 后端单测覆盖 AI 失败不降级。
- 后端单测覆盖 AI 任务记录写入。
- 后端单测覆盖反馈样本脱敏。
- 前端构建必须通过。

#### 是否适合交给 AI agent 执行

适合。该任务以数据、API 和页面为主，AI agent 可以按垂直切片实现。

---

### 任务 17：变更中心影响分析与回归推荐

#### 任务目标

建立需求、接口、元素、App、bug 修复等变更的统一记录、影响分析、回归推荐和人工确认闭环。

#### PRD 对应条款

- `FR-CHANGE-001` - `FR-CHANGE-010`
- `AC-CHANGE-*`
- `FR-CASE-011.4`
- `FR-TODO-*`

#### 涉及模块

- 变更中心
- 需求中心
- Case 中心
- 接口中心
- 移动端执行中心
- 待办中心

#### 前置依赖

- 任务 3：需求文档上传、原文预览与关系树挂载
- 任务 6：Case 中心基础资产管理
- 任务 7：接口定义导入、确认与单接口调试
- 任务 8：接口 case 编写、Harness 基础能力与单 case 执行
- 任务 16：AI 能力中心治理闭环

#### 输入

- 新旧需求文档差异。
- 接口定义变更。
- 移动端元素、页面或 App 版本变更。
- Bug 修复记录或外部 bug id 预留。
- 历史 case、执行结果和报告。

#### 输出

- `ChangeRecord` 变更记录。
- 影响对象列表：需求点、接口、case、元素、报告。
- 回归推荐列表。
- case 新增 / 修改 / 废弃草稿。
- 待办项：待人工确认影响分析或 case 修改草稿。

#### 建议修改文件

- `backend/app/models/changelog.py`
- `backend/app/routers/changelog.py`
- `backend/app/services/changelog_service.py`
- `backend/app/services/case_service.py`
- `backend/app/services/todo_service.py`
- `frontend/src/modules/changelog/`
- `frontend/src/modules/cases/`

#### 数据模型

- `ChangeRecord`：变更来源、类型、模块、摘要、原始内容、影响范围、状态。
- `ChangeImpactItem`：被影响对象类型、对象 ID、影响原因、风险等级。
- `RegressionRecommendation`：推荐 case、推荐原因、优先级、人工确认状态。
- `CaseChangeDraft`：case 新增、修改、废弃建议草稿。

#### API / Service

- `POST /api/changelog/records`：创建变更记录。
- `POST /api/changelog/records/{id}/analyze-impact`：执行影响分析。
- `GET /api/changelog/records/{id}/impacts`：查询影响对象。
- `GET /api/changelog/records/{id}/regression-recommendations`：查询回归推荐。
- `POST /api/changelog/case-drafts/{id}/confirm`：确认 case 修改草稿。
- `POST /api/changelog/case-drafts/{id}/reject`：拒绝 case 修改草稿并记录原因。

#### 前端页面 / 交互

- 变更列表：按来源、模块、状态、风险筛选。
- 变更详情：展示变更摘要、影响对象、AI 分析依据、回归推荐和待确认草稿。
- 影响分析结果必须能跳转到需求、接口、case、元素或报告。
- case 修改草稿必须人工确认后才生效。

#### 状态流转

```text
recorded -> analyzing -> pending_review -> confirmed | rejected | archived
```

#### Guardrails

- 变更影响分析不能自动修改正式 case。
- AI 回归推荐只能作为建议，必须展示依据和人工确认状态。
- 被废弃 case 不能被推荐进入执行集。
- 变更中心不得替代 Bug 中心完整缺陷流转。

#### 验收标准

- 用户可以创建变更记录并执行影响分析。
- 影响分析结果能列出受影响 case 和推荐回归 case。
- 自动生成的 case 修改草稿必须人工确认后才生效。
- 影响分析待确认事项进入待办中心。

#### 测试要求

- 覆盖创建变更、影响分析、回归推荐。
- 覆盖 case 修改草稿确认后才更新正式 case。
- 覆盖被废弃 case 不进入回归推荐。

#### 是否适合交给 AI agent 执行

部分适合。数据、API、页面适合 AI agent；影响分析规则和推荐阈值需要人工确认。

---

### 任务 18：待办中心独立复核队列

#### 任务目标

把待办中心从首页聚合入口升级为独立人工复核队列，承接需求问题、AI case 草稿、失败报告、元素失效、变更影响和 AI 低分等事项。

#### PRD 对应条款

- `FR-TODO-001` - `FR-TODO-008`
- `AC-TODO-*`
- `FR-HOME-003`
- `FR-REQ-018`
- `FR-CASE-005.4`
- `FR-MOB-010.3`

#### 涉及模块

- 待办中心
- 首页 / 质量驾驶舱
- 需求中心
- Case 中心
- 报告中心
- 移动端执行中心
- 变更中心

#### 前置依赖

- 任务 4：需求文档解析、逻辑检查与入库门禁
- 任务 5：AI case 草稿生成、门禁检查与人工确认
- 任务 9：接口执行报告与 HTML 证据链
- 任务 12：统一执行中心、重试、取消与失败处理建议
- 任务 16：AI 能力中心治理闭环
- 任务 17：变更中心影响分析与回归推荐

#### 输入

- 来源模块产生的复核事项。
- 来源对象 ID、标题、描述、风险等级、优先级。
- 处理动作：开始处理、解决、忽略、阻塞、跳转来源。

#### 输出

- `TodoItem` 待办记录。
- `TodoActionLog` 操作日志。
- 首页待办计数。
- 来源模块状态更新或核销结果。

#### 建议修改文件

- `backend/app/models/todo.py`
- `backend/app/services/todo_service.py`
- `backend/app/routers/todos.py`
- `frontend/src/modules/todos/`
- `frontend/src/modules/home/`

#### 数据模型

- `TodoItem`：来源类型、来源 ID、标题、描述、重要性、风险等级、状态、忽略原因。
- `TodoActionLog`：待办 ID、动作类型、操作人、原因、时间。

#### API / Service

- `GET /api/todos`：列表和筛选。
- `GET /api/todos/count`：首页计数。
- `POST /api/todos/{id}/start`：开始处理。
- `POST /api/todos/{id}/resolve`：解决。
- `POST /api/todos/{id}/dismiss`：忽略并记录原因。
- `GET /api/todos/{id}/source`：返回来源跳转信息。

#### 前端页面 / 交互

- 待办列表：按来源类型、状态、优先级、风险等级筛选。
- 待办详情：展示来源摘要、处理建议和来源跳转。
- 支持解决、忽略、标记阻塞。
- 首页只展示聚合入口，不承接复杂处理。

#### 状态流转

```text
pending -> in_progress -> resolved | dismissed | blocked
```

#### Guardrails

- 忽略待办必须填写不少于 10 字原因。
- 待办不能替代来源模块的业务确认；解决待办必须同步来源状态或记录无法同步原因。
- 同源、同类型、未完成待办不得重复创建。

#### 验收标准

- 需求阻断问题、AI case 草稿、高风险负样本、变更影响都能生成待办。
- 处理来源对象后，对应待办能自动核销。
- 待办可跳转回来源模块。
- 首页待办数量与待办列表一致。

#### 测试要求

- 覆盖待办注册去重。
- 覆盖来源对象处理后自动核销。
- 覆盖忽略原因校验。

#### 是否适合交给 AI agent 执行

适合。该任务边界清晰，可以独立按数据、API、前端列表和测试实现。

---

### 任务 19：Bug 标准模型与接入点预留

#### 任务目标

为未来 Bug 中心和外部缺陷平台同步预留标准模型和关联字段，但当前不实现完整外部同步、独立 Bug 页面和复杂缺陷流转。

#### PRD 对应条款

- `FR-BUG-*`
- 报告中心、执行中心、变更中心中关于标记 bug、关联 report / case / change 的预留要求。

#### 涉及模块

- 未来 Bug 中心
- Case 中心
- 执行中心
- 报告中心
- 变更中心

#### 前置依赖

- 任务 6：Case 中心基础资产管理
- 任务 9：接口执行报告与 HTML 证据链
- 任务 12：统一执行中心、重试、取消与失败处理建议
- 任务 17：变更中心影响分析与回归推荐

#### 输入

- 执行失败结果。
- 报告证据链。
- case、change、report 关联对象。
- 外部 bug id、来源、标题、严重级别等可选字段。

#### 输出

- `BugIntegrationPlaceholder` 或 `BugRecord` 预留记录。
- case / report / change 上的 bug 关联字段。
- 未来 connector 所需的标准字段。

#### 建议修改文件

- `backend/app/models/bug_record.py`
- `backend/app/schemas/bug_record.py`
- `backend/app/services/bug_link_service.py`
- `backend/app/models/test_case.py`
- `backend/app/models/execution.py`
- `backend/app/models/changelog.py`

#### 数据模型

- `BugRecord`：标题、描述、严重级别、状态、来源、外部 ID、关联 case、report、change。
- `BugLink`：来源对象类型、来源对象 ID、bug ID、创建人、创建时间。

#### API / Service

- `POST /api/bug-links`：创建内部 bug 关联占位。
- `GET /api/bug-links?source_type=&source_id=`：查询对象关联 bug。
- Connector 接口仅预留，不要求真实同步外部系统。

#### 前端页面 / 交互

- 当前阶段不做独立 Bug 页面。
- 在报告详情、执行失败详情或 case 详情中预留 bug 关联展示区域。
- 支持手动录入外部 bug id 或内部 bug 占位。

#### 状态流转

```text
placeholder -> linked_external | resolved | ignored
```

#### Guardrails

- 当前阶段不得假装完成外部缺陷平台同步。
- Bug 关联不能替代报告证据链。
- 删除 case、report 或 change 时不得静默删除 bug 关联历史。

#### 验收标准

- case / report / change 能保存 bug 关联占位。
- 能查询某个对象关联的 bug 信息。
- 文档明确当前不支持外部同步，只保留 connector 扩展点。

#### 测试要求

- 覆盖 bug 关联创建和查询。
- 覆盖删除或归档来源对象时 bug 关联不丢失。

#### 是否适合交给 AI agent 执行

适合。该任务是预留模型和关联服务，不依赖外部平台。

---

## 3.1 需求中心与 Case 中心补缺专项任务

本专项基于 `docs/product/AI测试平台PRD.md` 中需求中心、Case 中心、AI 不降级、待办队列和可信资产治理要求拆分。该专项不再按 P0/P1 分级，以下任务均属于需求中心与 Case 中心完整交付范围。

### 专项任务总览

| 编号 | 任务名称 | 交付类型 | 前置依赖 | 是否适合 AI agent |
|---|---|---|---|---|
| RC-01 | 文档问题项、修订版与处理动作模型 | AFK | 任务 4 | 是 |
| RC-02 | 文档问题项处理 API 与入库 / 生成强门禁 | AFK | RC-01 | 是 |
| RC-03 | 需求中心问题项工作台前端闭环 | HITL | RC-01、RC-02 | 部分适合 |
| RC-04 | AI 调用不降级 Guardrail | AFK | 任务 14、RC-02 | 是 |
| RC-05 | AI case 草稿、拒绝、废弃与正式入库契约修复 | AFK | 任务 5、任务 6 | 是 |
| RC-06 | Case 来源追溯与可信详情补齐 | AFK | RC-05 | 是 |
| RC-07 | Case 健康度与废弃执行隔离 | AFK | RC-05、任务 12 | 是 |
| RC-08 | 需求问题项与待办队列联动 | AFK | RC-02、任务 13 | 是 |
| RC-09 | 负样本闭环与相似草稿门禁 | AFK | RC-05、RC-06 | 是 |
| RC-10 | 全量联动、绕过路径与验收证据 | HITL | RC-01 - RC-09 | 部分适合 |

### 专项代码定位与测试索引

AI agent 执行 `RC-*` 任务时，优先从下表定位代码，不要跨模块做无关重构。

| 任务 | 后端重点文件 | 前端重点文件 | 测试文件 / 命令 |
|---|---|---|---|
| RC-01 | `backend/app/models/requirement_issue.py`、`backend/app/models/requirement_document.py`、`backend/app/database.py` | 无或仅展示占位 | `backend/tests/test_requirement_issue_workflow.py` |
| RC-02 | `backend/app/services/requirement_doc_service.py`、`backend/app/routers/requirements.py`、`backend/app/schemas/requirement_document.py` | 无或仅 API 联调 | `backend/tests/test_requirement_issue_workflow.py`、`backend/tests/test_requirement_parse_gate.py` |
| RC-03 | `backend/app/routers/requirements.py` | `frontend/src/modules/requirements/api.js`、`frontend/src/modules/requirements/pages/RequirementsPage.vue` | `cd frontend && npm run build`；如有前端测试框架则补交互测试 |
| RC-04 | `backend/app/services/ai_client.py`、`backend/app/skills/requirement_parse_skill.py`、`backend/app/skills/case_generate_skill.py`、`backend/app/skills/rag_retrieve_skill.py`、`backend/app/skills/conflict_detect_skill.py`、`backend/app/skills/failure_analysis_skill.py`、`backend/app/skills/coverage_evaluate_skill.py`、`backend/app/routers/ai_service.py` | 调用方统一展示后端错误 | `backend/tests/test_ai_no_fallback.py`、`backend/tests/test_plan_completion_guards.py` |
| RC-05 | `backend/app/services/case_service.py`、`backend/app/services/ai_case_draft_service.py`、`backend/app/routers/test_cases.py`、`backend/app/schemas/test_case.py` | `frontend/src/modules/cases/api.js`、`frontend/src/modules/cases/pages/CasesPage.vue` | `backend/tests/test_case_contract_guards.py`、`backend/tests/test_ai_case_draft.py`、`backend/tests/test_case_version.py` |
| RC-06 | `backend/app/models/test_case.py`、`backend/app/models/ai_case_draft.py`、`backend/app/services/case_service.py`、`backend/app/services/ai_case_draft_service.py` | `frontend/src/modules/cases/pages/CasesPage.vue` | `backend/tests/test_ai_case_draft.py`、`backend/tests/test_case_reconfirm_reset.py` |
| RC-07 | `backend/app/services/case_service.py`、`backend/app/services/test_executor.py`、`backend/app/routers/executions.py` | `frontend/src/modules/cases/pages/CasesPage.vue` | `backend/tests/test_case_contract_guards.py`、`backend/tests/test_plan_completion_guards.py` |
| RC-08 | `backend/app/services/requirement_doc_service.py`、`backend/app/services/todo_service.py`、`backend/app/routers/todos.py` | `frontend/src/modules/todos/`、`frontend/src/modules/requirements/pages/RequirementsPage.vue` | `backend/tests/test_plan_completion_guards.py` |
| RC-09 | `backend/app/services/negative_case_sample_service.py`、`backend/app/services/ai_case_draft_service.py`、`backend/app/skills/case_generate_skill.py` | `frontend/src/modules/cases/pages/CasesPage.vue` | `backend/tests/test_ai_case_draft.py`、`backend/tests/test_plan_completion_guards.py` |
| RC-10 | 测试聚合，不新增业务代码，除非测试暴露缺陷 | 测试聚合，不新增业务代码，除非构建暴露缺陷 | `python -m unittest ...`、`cd frontend && npm run build` |

### 专项统一 Guardrails

- 所有 AI 调用失败必须直接报错，不允许生成规则、模板或 mock 结果冒充成功。
- AI case 草稿不得绕过人工确认进入正式 case。
- 阻断级需求问题未处理前，不得入库、不得生成 case。
- 忽略问题、拒绝草稿、废弃 case 都必须记录结构化原因，原因字数不足时后端拦截。
- 正式资产的关键字段修改必须有版本快照或审计记录。
- 已废弃或停用 case 不得进入单 case 执行、批量执行、回归推荐或报告生成。
- 待办只能承接复核流转，不能替代来源模块的业务状态确认。

### 专项验收命令

执行完整专项后，至少运行：

```bash
cd backend && python -m unittest \
  tests.test_requirement_issue_workflow \
  tests.test_ai_no_fallback \
  tests.test_case_contract_guards \
  tests.test_plan_completion_guards \
  tests.test_requirement_parse_gate \
  tests.test_case_sync_gate \
  tests.test_ai_case_draft \
  tests.test_case_reconfirm_reset \
  tests.test_case_delete \
  tests.test_case_version -v
cd frontend && npm run build
```

### RC-01：文档问题项、修订版与处理动作模型

#### 任务目标

将需求检查结果从 `parse_result.issues` 快照升级为可处理、可追踪、可审计的问题项资产。

#### 涉及模块

- 需求中心
- AI 能力中心
- 数据库模型

#### 开发内容

- 新增 `RequirementIssue` 模型，记录文档、需求点、问题类型、严重级别、阻断标记、原文位置、原文片段、AI 判断原因、建议动作和处理状态。
- 新增 `RequirementRevision` 模型，保存平台内修改后的修订片段、完整内容快照、差异摘要、来源问题项和修改人。
- 新增 `RequirementIssueAction` 模型，记录修改、忽略、转人工、重新检查、解决等动作。
- 文档解析完成后，将解析结果中的问题同步落库，保留 `parse_result` 作为解析快照。
- 重复解析时刷新未处理问题项，避免历史误报污染当前门禁。

#### 验收标准

- 解析后可以按文档查询问题项。
- 阻断级问题必须带 `blocking=true`。
- 问题项能追溯原文片段、AI 判断原因和建议处理方式。
- 修改动作能生成修订版，不覆盖原始文件。

#### 测试要求

- 覆盖解析生成问题项。
- 覆盖阻断级字段完整性。
- 覆盖修改问题项生成修订版。

### RC-02：文档问题项处理 API 与入库 / 生成强门禁

#### 任务目标

让产品或测试人员能在平台内完成“查看问题 -> 修改 / 忽略 / 转人工 -> 重新检查 -> 入库”的闭环，并防止直接调用 API 绕过门禁。

#### 涉及模块

- 需求中心
- Case 中心
- 后端服务层
- 后端路由

#### 开发内容

- 增加文档问题项列表接口。
- 增加问题项修改接口，写入 `RequirementRevision` 并更新文档可检查内容。
- 增加忽略接口，强制填写不少于 10 字原因；阻断级问题需要确认风险后才能忽略。
- 增加转人工确认、标记解决、重新检查接口。
- 强化 `confirm_storage()`：存在未解决阻断问题时禁止入库。
- 强化 `assert_can_generate_cases()`：存在未解决阻断问题时禁止生成 case。

#### 验收标准

- 阻断问题未处理时，确认入库返回明确错误。
- 阻断问题未处理时，生成 case 返回明确错误。
- 待优化问题可以忽略，但必须留痕。
- 忽略不能删除问题项，只能改变状态。

#### 测试要求

- 覆盖确认入库绕过。
- 覆盖生成 case 绕过。
- 覆盖忽略原因过短拦截。
- 覆盖修订后重新检查并允许入库。

### RC-03：需求中心问题项工作台前端闭环

#### 任务目标

在需求中心页面提供可用的问题项工作台，让用户不离开平台即可处理需求文档问题。

#### 涉及模块

- 需求中心前端
- 全局弹窗 / 错误提示
- 需求树与文档详情

#### 开发内容

- 增加问题项、修订版、修改、忽略、重新检查等 API 封装。
- 在文档详情中展示“原文 / 问题项 / 修订版 / 检查结果”联动视图。
- 问题项展示类型、严重级别、阻断状态、原文片段、AI 判断原因和建议动作。
- 支持修改原文片段、忽略并填写原因、重新检查。
- 入库和生成 case 的后端错误通过统一弹窗展示。

#### 验收标准

- 用户可以在文档详情中看到问题项和修订版。
- 用户可以提交修改并看到文档状态回到待重新检查。
- 用户可以忽略问题并留下原因。
- 阻断问题未解决时，即使前端按钮可见，后端仍能拦截。

#### 测试要求

- 若前端测试框架已建立，补交互测试。
- 若暂未建立前端测试框架，至少提供后端 API 测试和手动验收清单。

### RC-04：AI 调用不降级 Guardrail

#### 任务目标

落实 PRD 中“AI 解析或其他逻辑触发 AI 时，不允许使用降级逻辑；AI 连接失败或链接错误时直接弹窗报错”的规则。

#### 涉及模块

- AI 能力中心
- 需求中心
- Case 中心
- 系统设置

#### 开发内容

- `RequirementParseSkill` 不允许在 AI 失败时规则降级。
- `CaseGenerateSkill` 不允许在 AI 失败时模板降级。
- RAG、冲突检测、失败分析、覆盖评估等 AI Skill 不允许在模型未配置或调用失败时规则降级。
- `AIClient` 在未配置、鉴权失败、连接失败、超时、响应格式错误时抛出明确异常。
- 路由层将 AI 失败转成前端可展示的错误响应。
- 测试环境只能通过显式 mock 模型结果，不能走生产降级代码路径。

#### 验收标准

- 模拟模型未配置时，需求解析失败且不产生伪解析结果。
- 模拟模型未配置时，AI case 生成失败且不产生 case 草稿。
- 模拟模型未配置时，覆盖评估、失败分析、冲突检测、RAG 语义重排均失败并给出明确错误。
- 前端展示后端错误，不展示“生成成功”类误导提示。

#### 测试要求

- 覆盖 `FR-AI-013` 和 `FR-SET-012`。
- 覆盖需求解析、case 生成、覆盖评估、失败分析、冲突检测和 RAG。

### RC-05：AI case 草稿、拒绝、废弃与正式入库契约修复

#### 任务目标

确保 AI 生成结果只能先进入草稿队列，必须人工确认后才能成为正式 case；拒绝和废弃操作必须结构化留痕。

#### 涉及模块

- Case 中心
- AI case 草稿队列
- 负样本库
- 前端 Case 页面

#### 开发内容

- `/api/cases/ai-generate` 只生成 AI 草稿，不直接写入正式 case。
- 接受草稿时才创建正式 case，并记录确认人、确认时间和来源文档。
- 拒绝草稿前端改为结构化表单，传 `category`、`reason`、`rejected_by`。
- 废弃 case 前端改为结构化表单，传 `category`、`reason`、`replaced_by_case_id`、`change_record_id`。
- 后端保持强校验：分类必须合法，原因不少于 10 字。
- 功能、自动化、移动端 case 必须包含步骤；接口 case 必须包含请求数据或接口断言。

#### 验收标准

- AI 生成不会直接污染正式 case 库。
- 接受草稿后正式 case 可在 Case 中心查看。
- 拒绝草稿后进入负样本库。
- 废弃 case 后默认不出现在活跃资产列表。
- 原因过短或分类缺失时，后端返回错误。

#### 测试要求

- 覆盖 AI 直连入库绕过。
- 覆盖拒绝草稿参数契约。
- 覆盖废弃 case 参数契约。
- 覆盖空白幽灵 case 拦截。

### RC-06：Case 来源追溯与可信详情补齐

#### 任务目标

让测试经理和测试人员能判断 case 是否可信，并能回溯到来源文档、需求点、原文片段、AI 草稿和人工确认记录。

#### 涉及模块

- Case 中心
- 需求中心
- AI 草稿
- 版本快照

#### 开发内容

- Case 详情展示来源文档 ID、需求点 ID、来源类型、确认人、确认时间。
- 接受 AI 草稿时保存结构化来源数据，包括原文片段、AI 原始输出、团队 case 模板字段。
- Case 详情展示当前版本号、版本历史、废弃元数据和最近执行结果。
- 编辑关键字段时生成版本快照，并将可信状态重置为需重新确认。

#### 验收标准

- 从正式 case 详情能看到来源文档、来源类型、人工确认记录。
- AI 草稿转正式 case 后，原文片段和团队 case 模板字段不丢失。
- 修改步骤、断言、来源、前置条件、预期结果等关键字段后，case 标记为待重新确认。

#### 测试要求

- 覆盖接受草稿后查询 case 来源字段。
- 覆盖关键字段修改后的版本快照和可信状态重置。

### RC-07：Case 健康度与废弃执行隔离

#### 任务目标

防止废弃 case 污染执行和报告，同时为 case 健康度治理提供证据。

#### 涉及模块

- Case 中心
- 执行中心
- 报告中心预留

#### 开发内容

- Case 列表默认过滤 `lifecycle_status=deprecated` 或 `is_active=0` 的 case。
- 显式包含废弃时，可以在治理视图看到废弃资产。
- 单 case 执行入口拦截废弃或停用 case。
- 批量执行、按接口执行、按项目执行时过滤废弃或停用 case。
- 前端展示生命周期状态、最近执行结果、缺断言、废弃原因等健康信号。

#### 验收标准

- 废弃 case 默认不在正式活跃资产列表中展示。
- 单条执行废弃 case 返回明确错误。
- 批量执行不会包含废弃 case。
- 废弃资产仍可在治理视图追溯。

#### 测试要求

- 覆盖单条执行废弃 case 拦截。
- 覆盖批量执行过滤废弃 case。
- 覆盖废弃 case 显式查询可见。

### RC-08：需求问题项与待办队列联动

#### 任务目标

让阻断级需求问题进入人工复核队列，处理后自动核销，形成需求中心与待办队列闭环。

#### 涉及模块

- 需求中心
- 待办中心
- 首页 / 质量驾驶舱

#### 开发内容

- 文档解析出阻断级问题时，按问题项生成 `REQ_ISSUE_BLOCKING` 待办。
- 问题项修改、忽略、解决后自动核销对应待办。
- 待办保留来源类型、来源 ID、标题、描述、重要性和风险级别。
- 待办列表支持按 `source_type` 过滤。
- 后续首页质量驾驶舱可基于待办计数展示人工复核压力。

#### 验收标准

- 解析出阻断问题后，待办列表出现对应记录。
- 处理问题项后，待办状态变为 `resolved`。
- 同一未完成问题项不会重复生成多个待办。

#### 测试要求

- 覆盖问题项生成待办。
- 覆盖问题项忽略 / 修改后待办核销。

### RC-09：负样本闭环与相似草稿门禁

#### 任务目标

让被拒绝的 AI case 真实影响下一次生成，不只是保存一条历史记录。

#### 涉及模块

- Case 中心
- AI 草稿队列
- 负样本库
- 待办中心

#### 开发内容

- 拒绝 AI 草稿时写入负样本，保存拒绝分类、用户反馈、来源需求和脱敏后的草稿内容。
- 生成新草稿时，与历史拒绝负样本做相似度检查。
- 相似度超过阈值时，新草稿进入 `check_failed`，不进入普通待确认队列。
- 高风险拦截草稿生成待办，供人工复核。
- 前端草稿列表或详情展示高风险拦截原因。

#### 验收标准

- 被拒绝草稿进入负样本库。
- 与负样本高度相似的新草稿进入 `check_failed`。
- 高风险拦截结果可查询、可追溯。
- 负样本内容经过基础脱敏。

#### 测试要求

- 覆盖拒绝草稿生成负样本。
- 覆盖相似草稿被拦截。
- 覆盖高风险草稿进入待办。

### RC-10：全量联动、绕过路径与验收证据

#### 任务目标

用自动化测试和构建检查证明需求中心与 Case 中心可信闭环成立。

#### 涉及模块

- 需求中心
- Case 中心
- AI 能力中心
- 待办中心
- 执行中心

#### 开发内容

- 建立需求问题项工作流测试。
- 建立 AI 不降级测试。
- 建立 Case 合约和草稿门禁测试。
- 建立需求门禁、case 同步、草稿确认、废弃隔离、负样本相似拦截回归测试。
- 前端至少通过生产构建；如后续引入前端测试框架，再补组件交互测试。

#### 验收标准

- 后端测试覆盖直接 API 绕过路径。
- 前端生产构建通过。
- Linter 无新增错误。
- 验收结果能明确列出通过的测试命令和覆盖点。

#### 测试要求

- `python -m unittest` 覆盖需求中心与 Case 中心相关测试。
- `cd frontend && npm run build` 通过。

## 3.2 需求中心与 Case 中心全量开发任务拆分

本节按 `docs/product/AI测试平台PRD.md` 最新逻辑，对需求中心与 Case 中心进行全量任务拆分。它不是 `RC-*` 的替代，而是在 `RC-*` 已覆盖的问题项、AI 不降级、草稿确认、废弃隔离和负样本闭环基础上，继续补齐 `RequirementBaseline -> RequirementDiff -> CoverageMatrix -> CaseGenerationPlan -> 分类型 case 草稿 -> 正式 case 资产` 的完整开发任务。

执行要求：

- 不做 P0 / P1 / P2 分级，以下任务均属于完整交付范围。
- 每个任务必须按文档中的 `PRD 对应条款` 完成，不得只做最小接口或最小页面。
- 每个任务完成后必须补自动化测试；涉及前端交互的任务至少通过 `cd frontend && npm run build`。
- AI agent 执行时一次只做一个任务；任务完成后输出修改文件、测试命令、覆盖的 PRD 条款和仍需人工确认的点。
- 所有 AI 解析、AI 差异分析、AI 生成、AI 评估都遵守 AI 不降级：模型连接失败、鉴权失败、超时、配置错误时直接失败并提示用户，不得用本地规则或模板伪造成 AI 成功结果。
- 所有功能 case、接口 case、自动化脚本 case 草稿都必须符合项目内 `.agents/skills/test_case/SKILL.md` 的统一字段契约；AI agent 实现时应以运行时 `CaseGenerateSkill.case_format_contract()` 为最终落地契约。

### 3.2.1 全量任务总览

| 编号 | 任务名称 | 交付类型 | 前置依赖 | 主要覆盖 |
|---|---|---|---|---|
| RCP-01 | 当前实现审计、数据迁移基线与任务护栏 | AFK | RC-01 - RC-10 | 防重复、迁移边界、测试基线 |
| RCP-02 | RequirementBaseline 数据模型与基线版本体系 | AFK | RCP-01 | `FR-REQ-022` |
| RCP-03 | 入库后基线生成 / 更新 / 首次基线确认服务 | AFK | RCP-02 | `FR-REQ-022`、`FR-REQ-023`、`AC-REQ-012` |
| RCP-04 | 历史基线 API 与需求中心基线 UI | HITL | RCP-03 | `AC-REQ-012`、需求中心 Data / API / UI |
| RCP-05 | RequirementDiff 数据模型、枚举与证据结构 | AFK | RCP-02 | `FR-REQ-024`、`FR-REQ-025` |
| RCP-06 | 新旧需求差异分析服务、最小差异 UI 与 AI 任务记录 | HITL | RCP-05、RCP-03、RC-04 | `FR-REQ-008`、`FR-REQ-023` - `FR-REQ-026`、`AC-REQ-013` |
| RCP-07 | 差异阻断、问题项联动与变更中心事件输出 | AFK | RCP-06、RC-02、RC-08 | `FR-REQ-026`、`AC-REQ-014` |
| RCP-08 | CoverageMatrix 数据模型与覆盖状态机 | AFK | RCP-05 | `FR-REQ-027`、`FR-REQ-028` |
| RCP-09 | 需求点 / 差异到已有 case 的覆盖计算服务 | HITL | RCP-08、RC-06、RCP-06、RCP-07 | `FR-REQ-027`、`FR-REQ-030` |
| RCP-10 | 覆盖矩阵缺口处理、风险接受与前端工作台 | HITL | RCP-09、RC-08 | `FR-REQ-029`、`AC-REQ-015`、`AC-REQ-016` |
| RCP-11 | CaseGenerationPlan 数据模型与状态流转 | AFK | RCP-08 | `FR-REQ-031`、`FR-CASE-015` |
| RCP-12 | 基于覆盖矩阵的生成计划推荐服务 | HITL | RCP-09、RCP-11 | `FR-CASE-015` - `FR-CASE-017` |
| RCP-13 | 生成计划确认、编辑、批量门禁与待办联动 UI | HITL | RCP-12、任务 18 | `AC-CASE-010`、`AC-CASE-011`、`FR-TODO-009` |
| RCP-14 | 功能 case 草稿生成策略与 test_case 契约绑定 | AFK | RCP-13、RC-05 | `FR-CASE-018`、`FR-CASE-024`、`FR-CASE-025` |
| RCP-15 | 接口 case 草稿生成策略、接口事实源绑定与可运行检查 | HITL | RCP-13、任务 7、任务 8 | `FR-CASE-019`、`FR-CASE-024`、`FR-API-014`、`FR-API-015` |
| RCP-16 | AutomationCandidate 数据模型与可行性评估 | HITL | RCP-13、任务 10、任务 11 | `FR-CASE-020`、`FR-CASE-021` |
| RCP-17 | 自动化脚本 case 草稿生成、资产依赖门禁与可运行检查 | HITL | RCP-16、RCP-14、RCP-15 | `AC-CASE-013`、`FR-MOB-014`、`FR-MOB-015` |
| RCP-18 | Case 详情覆盖状态、生成计划、差异与历史版本整合 | AFK | RCP-14、RCP-15、RCP-16、RC-06 | `FR-CASE-022`、`AC-CASE-014` |
| RCP-19 | AI 草稿人工编辑、批量同意门禁与绕过路径防护 | AFK | RCP-10、RCP-13、RC-05 | `FR-CASE-023`、`FR-CASE-026`、`FR-CASE-027`、`AC-CASE-015` |
| RCP-20 | 统一 RunnableCheck、运行入口与覆盖矩阵回写 | HITL | RCP-08、任务 8、任务 9、任务 11、任务 12 | `FR-EXEC-015` - `FR-EXEC-025`、`FR-REQ-027`、执行 / 报告联动 |
| RCP-21 | 需求中心与 Case 中心跨页集成工作台 | HITL | RCP-04、RCP-10、RCP-13、RCP-18 | UI 全链路 |
| RCP-22 | 报告 / 首页覆盖证据链与 AI 上下文指标对齐 | HITL | RCP-20、任务 13、任务 16 | `FR-HOME-007`、`FR-AI-014`、`FR-AI-015`、`FR-REPORT-013` - `FR-REPORT-015` |
| RCP-23 | 种子数据、端到端验收夹具与长任务回归命令 | AFK | RCP-01 - RCP-22 | 全链路验收 |
| RCP-24 | PRD 条款覆盖审计与缺失项关闭 | AFK | RCP-23 | 逐条逻辑检查 |

### RCP-01：当前实现审计、数据迁移基线与任务护栏

任务目标：
在正式开发新版需求 / Case 逻辑前，锁定当前代码状态、已完成能力、未完成能力和迁移边界，避免 AI agent 重复实现已存在模型或破坏用户已有改动。

PRD 对应条款：
`FR-REQ-001` - `FR-REQ-032`、`FR-CASE-001` - `FR-CASE-023`、需求中心 Guardrails、Case 中心 Guardrails。

前置依赖：
RC-01 - RC-10。

输入：
`docs/product/AI测试平台PRD.md`、现有后端模型 / service / router、现有前端页面、现有测试文件、当前数据库初始化逻辑。

输出：
一份实现审计清单，写入本任务开发记录或 PR 描述；明确哪些模型复用、哪些新增、哪些迁移需要兼容现有 SQLite 数据；同时必须输出待废弃旧生成接口、待改测试、数据迁移策略和门禁责任表。

建议修改文件：
不强制修改业务文件；如需要可新增 `docs/product/需求中心Case中心实现审计.md`。不得修改 PRD 原文。

数据模型：
仅审计，不新增模型。

API / Service：
梳理 `backend/app/routers/requirements.py`、`backend/app/routers/test_cases.py`、`backend/app/routers/ai_service.py`、`backend/app/services/requirement_doc_service.py`、`backend/app/services/case_service.py`。重点识别 `/api/ai/generate-cases-from-document`、`/api/cases/ai-generate` 等绕过 `CaseGenerationPlan` 的旧生成入口，并制定废弃或重定向到 RCP 生成计划接口的方案。

前端页面 / 交互：
梳理 `frontend/src/modules/requirements/pages/RequirementsPage.vue`、`frontend/src/modules/cases/pages/CasesPage.vue`。

状态流转：
梳理文档状态、问题项状态、AI 草稿状态、case 生命周期状态、待办状态。

Guardrails：
不得删除现有测试；不得重置数据库初始化；不得把 AI no-fallback 改回本地模板或规则降级；不得保留可绕过 `RequirementDiff`、`CoverageMatrix`、`CaseGenerationPlan` 的正式生成入口。

测试要求：
先运行当前需求 / Case 相关测试，记录基线。建议命令：`cd backend && python -m unittest tests.test_requirement_parse_gate tests.test_requirement_issue_workflow tests.test_case_contract_guards tests.test_ai_case_draft tests.test_case_version tests.test_plan_completion_guards`。

验收证据：
列出当前测试结果、已存在能力、需要新增能力、不会触碰的非范围、待废弃接口、待改测试、数据迁移策略和门禁责任表。门禁责任表至少包含：RC-02 负责问题项门禁；RCP-07 负责差异门禁；RCP-10 负责覆盖矩阵门禁；RCP-13 负责生成计划门禁；RCP-19 负责批量接受门禁。

非范围：
不实现新业务逻辑。

### RCP-02：RequirementBaseline 数据模型与基线版本体系

任务目标：
建立需求历史基线事实源，让新文档不再只和当前文件或 AI 上下文比较。

PRD 对应条款：
`FR-REQ-022`、`FR-REQ-023`、`AC-REQ-012`、需求中心 Data / API / UI Implications。

前置依赖：
RCP-01。

输入：
已确认入库的 `RequirementDocument`、`RequirementItem`、项目 / 模块 / 需求树路径、人工确认信息。

输出：
`RequirementBaseline`、`RequirementBaselineItem`、必要的基线版本字段和数据库初始化 / 迁移逻辑。

建议修改文件：
`backend/app/models/requirement_baseline.py`、`backend/app/models/__init__.py`、`backend/app/database.py`、`backend/app/services/requirement_baseline_service.py`、`backend/tests/test_requirement_baseline.py`。

数据模型：
`RequirementBaseline` 至少包含 `id`、`project_id`、`module_id`、`business_domain`、`feature_key`、`baseline_version`、`status`、`source_document_ids`、`created_by`、`confirmed_by`、`confirmed_at`、`created_at`、`updated_at`。
`RequirementBaselineItem` 至少包含 `baseline_id`、`requirement_item_id`、`requirement_key`、`title`、`content`、`acceptance_criteria`、`source_excerpt`、`source_location`、`item_hash`、`is_active`。

API / Service：
先实现 service 层创建、查询当前有效基线、查询基线项、停用旧基线。

前端页面 / 交互：
本任务可只提供后端能力，前端在 RCP-04 完成。

状态流转：
`draft -> active -> superseded -> archived`。

Guardrails：
同一业务域 / 模块 / 功能只能有一个 `active` 基线；基线项必须可追溯到原始文档和结构化需求点。

测试要求：
覆盖首次创建基线、同功能新版本替换 active 基线、旧基线变为 superseded、基线项保留原文片段。

验收证据：
后端测试通过；数据库初始化包含新表；旧需求问题项测试不回归。

非范围：
不做差异分析，不做覆盖矩阵。

### RCP-03：入库后基线生成 / 更新 / 首次基线确认服务

任务目标：
把“人工确认入库”与 `RequirementBaseline` 自动关联，形成稳定历史事实源。

PRD 对应条款：
`FR-REQ-010`、`FR-REQ-022`、`FR-REQ-023`、`AC-REQ-012`。

前置依赖：
RCP-02、RC-02。

输入：
文档确认入库请求、结构化需求点、文档修订版、当前用户。

输出：
确认入库后自动生成或更新基线；无历史基线时返回“首次基线需确认”标识。

建议修改文件：
`backend/app/services/requirement_doc_service.py`、`backend/app/services/requirement_baseline_service.py`、`backend/app/routers/requirements.py`、`backend/tests/test_requirement_baseline.py`。

数据模型：
复用 `RequirementBaseline`、`RequirementBaselineItem`。

API / Service：
增强 `/api/requirements/documents/{id}/confirm`；新增 `RequirementBaselineService.create_from_document()`、`get_active_baseline()`、`mark_first_baseline_confirmed()`。

前端页面 / 交互：
先返回 API 字段，RCP-04 补 UI。

状态流转：
文档 `pending_review -> stored` 时触发基线；首次基线需要人工确认后才能作为 active。

Guardrails：
文档仍有阻断问题项时不得生成 active 基线；不得用未确认 AI 解析结果直接写基线。

测试要求：
覆盖有阻断问题时不建基线、首次基线确认、再次入库生成新基线、旧基线保留。

验收证据：
确认入库接口响应包含 baseline 信息；测试覆盖阻断路径。

非范围：
不展示基线 UI。

### RCP-04：历史基线 API 与需求中心基线 UI

任务目标：
让用户能在需求中心看到当前文档对应的历史基线、基线版本、基线项和首次基线确认入口。

PRD 对应条款：
`AC-REQ-012`、需求中心 Data / API / UI Implications。

前置依赖：
RCP-03。

输入：
文档 ID、项目 / 模块 / 功能筛选、基线 ID。

输出：
基线列表、当前 active 基线、基线详情、基线项详情、首次基线确认操作。

建议修改文件：
`backend/app/routers/requirements.py`、`frontend/src/modules/requirements/api.js`、`frontend/src/modules/requirements/pages/RequirementsPage.vue`、`backend/tests/test_requirement_baseline.py`。

数据模型：
复用 RCP-02。

API / Service：
新增 `GET /api/requirements/baselines`、`GET /api/requirements/baselines/{id}`、`POST /api/requirements/documents/{id}/baseline/confirm-first`。

前端页面 / 交互：
在文档详情增加“历史基线”页签；展示基线版本、来源文档、需求点、确认人、确认时间；首次基线需二次确认。

状态流转：
首次基线 `draft -> active`；旧基线只读。

Guardrails：
前端隐藏按钮不是安全边界；后端必须校验阻断问题和文档确认状态。

测试要求：
后端 API 测试；前端构建通过；手工验收基线页签。

验收证据：
截图或文字说明能证明文档详情可定位到基线项。

非范围：
不做差异分析。

### RCP-05：RequirementDiff 数据模型、枚举与证据结构

任务目标：
建立结构化差异事实，替代只展示自然语言历史对比摘要。

PRD 对应条款：
`FR-REQ-024`、`FR-REQ-025`、`AC-REQ-013`。

前置依赖：
RCP-02。

输入：
当前文档结构化需求点、active 基线项。

输出：
`RequirementDiff`、`RequirementDiffEvidence` 或等价 JSON 字段。

建议修改文件：
`backend/app/models/requirement_diff.py`、`backend/app/models/__init__.py`、`backend/app/database.py`、`backend/app/services/requirement_diff_service.py`、`backend/tests/test_requirement_diff.py`。

数据模型：
`RequirementDiff` 至少包含 `id`、`document_id`、`baseline_id`、`old_item_id`、`new_item_id`、`diff_type`、`risk_level`、`impact_scope`、`summary`、`evidence`、`blocking`、`status`、`created_at`、`updated_at`。
`diff_type` 至少包含 `added`、`modified`、`deleted`、`conflict`、`unchanged`、`acceptance_changed`、`api_contract_changed`、`permission_changed`、`flow_changed`、`boundary_changed`。

API / Service：
先实现 service 层创建、批量查询、按文档查询、按阻断状态查询。

前端页面 / 交互：
本任务不做 UI。

状态流转：
`detected -> pending_review -> accepted -> resolved -> ignored`。

Guardrails：
差异必须保留证据片段；高风险差异不能只存在 AI 文本中。

测试要求：
覆盖所有核心 diff_type 入库、证据字段、阻断状态、按文档查询。

验收证据：
后端测试通过；模型注册到数据库初始化。

非范围：
不做 AI 差异分析。

### RCP-06：新旧需求差异分析服务、最小差异 UI 与 AI 任务记录

任务目标：
在新文档解析后自动对比 active baseline，输出结构化 `RequirementDiff`，提供最小差异列表 UI，并记录 AI 任务上下文。

PRD 对应条款：
`FR-REQ-008`、`FR-REQ-023`、`FR-REQ-024`、`FR-REQ-025`、`FR-REQ-026`、`AC-REQ-003`、`AC-REQ-013`、需求中心 AI Evaluation Strategy。

前置依赖：
RCP-03、RCP-05、RC-04。

输入：
当前文档结构化需求点、active baseline、RAG 召回、Prompt / Skill 版本。

输出：
差异列表、耦合需求检查结果、最小差异列表 UI、AI 任务记录、失败原因或 no-fallback 错误。

建议修改文件：
`backend/app/services/requirement_diff_service.py`、`backend/app/skills/conflict_detect_skill.py` 或新增 `requirement_diff_skill.py`、可新增 `coupling_check_skill.py`、`backend/app/services/ai_client.py`、`backend/app/routers/requirements.py`、`frontend/src/modules/requirements/api.js`、`frontend/src/modules/requirements/pages/RequirementsPage.vue`、`backend/tests/test_requirement_diff.py`、`backend/tests/test_ai_no_fallback.py`。

数据模型：
复用 `RequirementDiff`；AI 任务记录复用或扩展 `AiTask`。

API / Service：
新增 `analyze_document_diff(document_id)`、`analyze_coupling_requirements(document_id)`；可新增 `POST /api/requirements/documents/{id}/diff/analyze`、`GET /api/requirements/documents/{id}/diffs`。

前端页面 / 交互：
需求中心先提供最小“差异分析”列表页签，展示 diff_type、风险等级、证据片段、阻断状态和耦合检查结果；RCP-21 再做跨页集成工作台。

状态流转：
文档 `pending_review` 后可触发 diff；diff 分析失败时文档不得进入 case 生成。

Guardrails：
AI 失败不得降级为规则 diff 或规则耦合检查；没有 active baseline 且未确认首次基线时不得伪造历史对比。

测试要求：
mock AI 成功返回结构化 diff 和耦合检查结果；mock AI 失败返回显式错误；无基线时要求首次基线确认；前端构建通过。

验收证据：
测试证明新增、修改、删除、冲突和验收标准变化可落表。

非范围：
不做完整跨页集成工作台；只做满足 `AC-REQ-013` 的最小差异列表展示。

### RCP-07：差异阻断、问题项联动与变更中心事件输出

任务目标：
把高风险差异从“展示结果”变成可处理问题项和可被变更中心消费的事件。

PRD 对应条款：
`FR-REQ-026`、`AC-REQ-014`、需求中心 Guardrails、`FR-CHANGE-010` - `FR-CHANGE-012`。

前置依赖：
RCP-06、RC-02、RC-08。

输入：
`RequirementDiff` 列表、风险等级、影响范围、当前文档。

输出：
关联 `RequirementIssue`、待办事件、变更中心事件 payload。

建议修改文件：
`backend/app/services/requirement_doc_service.py`、`backend/app/services/requirement_diff_service.py`、`backend/app/services/todo_service.py`、`backend/app/services/change_service.py` 或事件占位、`backend/tests/test_requirement_diff_gate.py`。

数据模型：
复用 `RequirementIssue`、`RequirementDiff`、`TodoItem`；必要时新增 `RequirementDiffAction`。

API / Service：
新增 `sync_diff_issues()`、`publish_diff_change_event()`；增强文档确认和生成上下文接口的阻断校验。

前端页面 / 交互：
问题项工作台展示来源为 `RequirementDiff` 的问题。

状态流转：
阻断 diff 未处理时，文档不能入库、不能生成覆盖矩阵、不能生成 case。

Guardrails：
删除历史需求、冲突、接口契约变化、高风险验收变化必须阻断或要求风险留痕。

测试要求：
覆盖高风险 diff 生成问题项、处理后解除阻断、未处理时 API 绕过失败。

验收证据：
测试证明直接调用生成接口也不能绕过 diff 阻断。

非范围：
不实现完整变更中心 UI。

### RCP-08：CoverageMatrix 数据模型与覆盖状态机

任务目标：
建立需求点 / 差异与 case、草稿、执行结果、缺口和建议动作之间的结构化覆盖关系。

PRD 对应条款：
`FR-REQ-027`、`FR-REQ-028`、`FR-REQ-029`、`FR-REQ-030`、`AC-REQ-015`。

前置依赖：
RCP-05。

输入：
`RequirementItem`、`RequirementDiff`、已有 `TestCase`、`AiCaseDraft`、执行结果占位。

输出：
`CoverageMatrix`、`CoverageMatrixItem`、覆盖状态枚举。

建议修改文件：
`backend/app/models/coverage_matrix.py`、`backend/app/models/__init__.py`、`backend/app/database.py`、`backend/app/services/coverage_matrix_service.py`、`backend/tests/test_coverage_matrix.py`。

数据模型：
`CoverageMatrix` 至少包含 `id`、`document_id`、`baseline_id`、`status`、`generated_by`、`confirmed_by`、`created_at`、`updated_at`。
`CoverageMatrixItem` 至少包含 `matrix_id`、`requirement_item_id`、`requirement_diff_id`、`coverage_status`、`linked_case_ids`、`linked_draft_ids`、`gap_reason`、`suggested_action`、`execution_status`、`manual_decision`。

API / Service：
先实现 service 层创建、查询、状态更新、缺口确认。

前端页面 / 交互：
本任务不做 UI。

状态流转：
矩阵 `draft -> generated -> pending_gap_review -> confirmed -> stale`；矩阵项状态包含 `covered`、`partial_covered`、`not_covered`、`outdated`、`duplicated`、`need_update`、`need_deprecate`。

Guardrails：
覆盖矩阵必须可结构化查询；不得只存一段 AI 总结。

测试要求：
覆盖矩阵创建、枚举校验、缺口项查询、状态流转。

验收证据：
后端测试通过；矩阵项能关联需求点、差异和 case。

非范围：
不做覆盖计算。

### RCP-09：需求点 / 差异到已有 case 的覆盖计算服务

任务目标：
根据需求点、差异和已有 case 生成覆盖矩阵，识别历史需求回归覆盖和新需求新增覆盖。

PRD 对应条款：
`FR-REQ-027`、`FR-REQ-030`、`AC-REQ-015`、Case 中心 AI Evaluation Strategy。

前置依赖：
RCP-08、RC-06、RCP-06、RCP-07。

输入：
需求点、差异列表、已有正式 case、已废弃 case、AI 草稿、负样本、执行摘要。

输出：
覆盖矩阵和建议动作：保留、更新、废弃、新增、合并候选；覆盖评估 AI 任务记录。

建议修改文件：
`backend/app/services/coverage_matrix_service.py`、`backend/app/services/case_service.py`、`backend/app/skills/coverage_evaluate_skill.py`、`backend/tests/test_coverage_matrix.py`。

数据模型：
复用 `CoverageMatrix`、`CoverageMatrixItem`、`TestCase`、`AiCaseDraft`。

API / Service：
新增 `generate_matrix_for_document(document_id)`、`match_requirement_to_cases()`、`classify_coverage_status()`；方法入口必须统一校验 RCP-07 差异门禁已通过且不存在未处理阻断 diff。

前端页面 / 交互：
RCP-10 完成 UI。

状态流转：
已有矩阵在需求、case、diff 或执行结果变化后标记为 `stale`。

Guardrails：
已废弃 case 不能算作有效覆盖；重复 case 不能提升覆盖率；低置信度匹配必须进入人工确认；AI 覆盖评估失败不得降级生成看似可信的 CoverageMatrix。

测试要求：
覆盖无 case 时 not_covered、已有有效 case 时 covered、废弃 case 时 outdated / need_update、重复 case 时 duplicated；覆盖阻断 diff 未处理时不得生成 confirmed 矩阵；AI 失败时显式报错。

验收证据：
测试能证明历史需求不会因为新文档缺失而从矩阵里消失。

非范围：
不生成 case。

### RCP-10：覆盖矩阵缺口处理、风险接受与前端工作台

任务目标：
让用户在需求中心看到覆盖矩阵并处理缺口，处理前不得批量生成或接受 AI case。

PRD 对应条款：
`FR-REQ-029`、`AC-REQ-015`、`AC-REQ-016`、需求中心 UI Implications。

前置依赖：
RCP-09、RC-08。

输入：
覆盖矩阵、矩阵项、待办、用户处理动作。

输出：
覆盖矩阵页签、缺口处理记录、风险接受记录、待办核销。

建议修改文件：
`backend/app/routers/requirements.py`、`backend/app/services/coverage_matrix_service.py`、`frontend/src/modules/requirements/api.js`、`frontend/src/modules/requirements/pages/RequirementsPage.vue`、`backend/tests/test_coverage_matrix_gate.py`。

数据模型：
复用 `CoverageMatrixItem.manual_decision`；必要时新增 `CoverageGapAction`。

API / Service：
新增 `GET /api/requirements/documents/{id}/coverage-matrix`、`POST /api/requirements/documents/{id}/coverage-matrix/generate`、`POST /api/requirements/coverage-items/{id}/resolve-gap`、`POST /api/requirements/coverage-items/{id}/accept-risk`。

前端页面 / 交互：
文档详情增加“覆盖矩阵”页签；支持按覆盖状态筛选；缺口项可跳转关联 case、生成计划或问题项；风险接受必须填写原因。

状态流转：
缺口 `open -> planned -> resolved -> risk_accepted`；风险接受不得等同于 covered。

Guardrails：
覆盖矩阵缺失或阻断缺口未处理时，后端必须阻止生成计划确认、批量生成和批量接受。

测试要求：
覆盖 API 绕过失败、风险接受必须填写原因、缺口处理后矩阵状态更新。

验收证据：
前端构建通过；后端测试证明门禁有效。

非范围：
不生成 case 草稿。

### RCP-11：CaseGenerationPlan 数据模型与状态流转

任务目标：
建立生成计划对象，让所有 AI case 草稿都从计划出发，而不是从文档直接生成。

PRD 对应条款：
`FR-REQ-031`、`FR-CASE-015`、`FR-CASE-016`、`AC-CASE-010`。

前置依赖：
RCP-08。

输入：
文档、基线、差异、覆盖矩阵、已有 case、废弃 case、相关接口、负样本。

输出：
`CaseGenerationPlan`、`CaseGenerationPlanItem`。

建议修改文件：
`backend/app/models/case_generation_plan.py`、`backend/app/models/__init__.py`、`backend/app/database.py`、`backend/app/services/case_generation_plan_service.py`、`backend/tests/test_case_generation_plan.py`。

数据模型：
`CaseGenerationPlan` 至少包含 `id`、`document_id`、`baseline_id`、`coverage_matrix_id`、`status`、`created_by`、`confirmed_by`、`confirmed_at`。
`CaseGenerationPlanItem` 至少包含 `plan_id`、`requirement_item_id`、`requirement_diff_id`、`target_case_type`、`suggested_action`、`reason`、`existing_case_id`、`draft_id`、`status`。

API / Service：
先实现 service 层创建、查询、确认、取消、标记 stale。

前端页面 / 交互：
RCP-13 完成 UI。

状态流转：
`draft -> pending_review -> confirmed -> generating -> generated -> partially_failed -> cancelled -> stale`。

Guardrails：
计划项必须绑定覆盖矩阵项；没有覆盖矩阵不得创建计划。

测试要求：
覆盖无覆盖矩阵创建失败、计划项类型枚举、确认状态流转。

验收证据：
后端测试通过；数据库初始化包含计划表。

非范围：
不调用 AI 生成 case。

### RCP-12：基于覆盖矩阵的生成计划推荐服务

任务目标：
根据覆盖矩阵和已有 case 生成计划建议，明确新增、更新、废弃、保留、合并候选和三类 case 生成范围。

PRD 对应条款：
`FR-CASE-015`、`FR-CASE-016`、`FR-CASE-017`、`AC-CASE-010`、`AC-CASE-011`。

前置依赖：
RCP-09、RCP-11。

输入：
覆盖矩阵、差异风险、已有 case、废弃 case、接口定义、元素资产、负样本。

输出：
生成计划建议项和建议理由。

建议修改文件：
`backend/app/services/case_generation_plan_service.py`、`backend/app/services/coverage_matrix_service.py`、`backend/app/services/case_service.py`、`backend/tests/test_case_generation_plan.py`。

数据模型：
复用 `CaseGenerationPlanItem.suggested_action`：`keep`、`update`、`deprecate`、`add_new`、`merge_candidate`。

API / Service：
新增 `propose_plan(document_id)`、`build_plan_context()`、`validate_plan_readiness()`。

前端页面 / 交互：
RCP-13 完成 UI。

状态流转：
生成计划建议默认为 `pending_review`，用户确认后才可生成草稿。

Guardrails：
更新、废弃、合并候选不得自动修改正式 case；必须进入人工确认或待办。

测试要求：
覆盖 not_covered 生成 add_new、outdated 生成 update、need_deprecate 生成 deprecate、duplicated 生成 merge_candidate。

验收证据：
测试证明计划建议可解释且不会修改正式资产。

非范围：
不生成 AI 草稿。

### RCP-13：生成计划确认、编辑、批量门禁与待办联动 UI

任务目标：
让测试人员在 Case 中心或需求中心确认、编辑和锁定生成计划，并把高风险计划项推送待办。

PRD 对应条款：
`FR-CASE-015` - `FR-CASE-017`、`AC-CASE-010`、`AC-CASE-011`、`FR-TODO-009`。

前置依赖：
RCP-12、任务 18。

输入：
生成计划、计划项、用户编辑动作、待办来源。

输出：
计划确认 UI、计划项编辑、批量确认门禁、高风险待办；若任务 18 未完成，仅允许 RC-08 作为临时 shim，且必须在 RCP-21 前迁移到任务 18 的标准待办模型。

建议修改文件：
`backend/app/routers/test_cases.py`、`backend/app/services/case_generation_plan_service.py`、`frontend/src/modules/cases/api.js`、`frontend/src/modules/cases/pages/CasesPage.vue`、`frontend/src/modules/requirements/pages/RequirementsPage.vue`、`backend/tests/test_case_generation_plan.py`。

数据模型：
复用 `CaseGenerationPlan`、`CaseGenerationPlanItem`、`TodoItem`；待办来源必须符合任务 18 的来源类型和核销规则。

API / Service：
新增 `GET /api/cases/generation-plans/{id}`、`POST /api/cases/generation-plans/{id}/confirm`、`PATCH /api/cases/generation-plan-items/{id}`、`POST /api/cases/generation-plans/{id}/cancel`。

前端页面 / 交互：
Case 中心增加“生成计划”区域；需求中心覆盖矩阵可以跳转到对应计划；计划项展示来源差异、覆盖状态、目标 case 类型、建议动作和理由。

状态流转：
计划确认后锁定输入上下文；覆盖矩阵 stale 时计划自动 stale。

Guardrails：
未确认计划不能触发 AI case 生成；计划项编辑必须保留审计。

测试要求：
覆盖确认计划、编辑计划项、覆盖矩阵 stale 后计划不可生成、待办生成和核销；若使用 RC-08 shim，必须有迁移测试或兼容测试。

验收证据：
后端测试和前端构建通过。

非范围：
不生成具体 case 草稿。

### RCP-14：功能 case 草稿生成策略与 test_case 契约绑定

任务目标：
按已确认 `CaseGenerationPlan` 生成功能 case 草稿，并绑定需求点、差异和覆盖类型；草稿结构必须符合项目内 `test_case` skill 统一字段契约。

PRD 对应条款：
`FR-CASE-004`、`FR-CASE-006`、`FR-CASE-018`、`FR-CASE-024`、`FR-CASE-025`、`AC-CASE-002`、`AC-CASE-003`、`AC-CASE-016`、`AC-CASE-017`。

前置依赖：
RCP-13、RC-05。

输入：
confirmed 计划项、需求点、差异、覆盖矩阵、负样本、Prompt / Skill 版本。

输出：
功能 case AI 草稿、`test_case` 字段契约校验结果、门禁结果、关联矩阵项、待确认队列。

建议修改文件：
`backend/app/services/ai_case_draft_service.py`、`backend/app/services/case_generation_plan_service.py`、`backend/app/skills/case_generate_skill.py`、`backend/app/schemas/test_case.py`、`backend/tests/test_case_generation_plan.py`、`backend/tests/test_ai_case_draft.py`。

数据模型：
增强 `AiCaseDraft` 关联 `plan_id`、`plan_item_id`、`requirement_diff_id`、`coverage_matrix_item_id`、`coverage_type`；草稿和正式 case 必须保存 `case_no`、`title`、`requirement_ref`、`precondition`、`steps`、`expected_result`、`importance`、`test_type`、`test_data`、`remarks`。

API / Service：
新增 `POST /api/cases/generation-plans/{id}/generate-drafts`；只处理 plan 中 `functional_case` 项。新增或复用 `validate_test_case_contract()` 校验 `test_case` skill 字段契约。

前端页面 / 交互：
草稿列表展示生成计划、覆盖类型、来源差异和字段契约校验结果；支持单条编辑后重新校验。

状态流转：
`planned -> generating -> draft_generated -> gate_passed | check_failed -> pending_review`。

Guardrails：
AI 生成失败不得降级；计划未确认不得生成；缺少 `test_case` 必填字段、步骤少于契约要求、预期结果不可验证或来源绑定缺失的草稿不得进入待确认队列。

测试要求：
覆盖计划未确认失败、AI 失败显式报错、功能 case 缺步骤被拦截、草稿绑定计划项、编辑后重新校验、字段契约缺失项展示。

验收证据：
测试证明 AI 草稿不是直接从文档生成。

非范围：
不生成接口 case 和自动化脚本 case。

### RCP-15：接口 case 草稿生成策略、接口事实源绑定与可运行检查

任务目标：
按生成计划生成接口 case 草稿，并确保接口 case 绑定接口中心事实源或接口文档解析结果；可执行接口 case 必须具备平台内直接运行所需的请求、环境、鉴权和断言依赖。

PRD 对应条款：
`FR-CASE-016`、`FR-CASE-019`、`FR-CASE-024`、`FR-API-014`、`FR-API-015`、`AC-CASE-012`、`AC-API-007`、`AC-API-008`、Case 中心 Guardrails。

前置依赖：
RCP-13、任务 7、任务 8。

输入：
计划项、接口定义、接口 diff、接口文档解析结果、环境 / 变量引用。

输出：
接口 case 草稿、候选草稿状态、执行可信状态、运行依赖检查结果。

建议修改文件：
`backend/app/services/ai_case_draft_service.py`、`backend/app/services/case_generation_plan_service.py`、`backend/app/services/interface_service.py`、`backend/app/schemas/test_case.py`、`backend/tests/test_api_case_generation_plan.py`。

数据模型：
`AiCaseDraft` 和正式 `TestCase` 必须能记录 `interface_definition_id`、`interface_diff_id`、`api_contract_status`、`request_data`、`request_headers`、`expected_status`、`expected_body`、`expected_contains`、`assertions`、`environment_ref`、`auth_ref`。

API / Service：
复用按计划生成草稿接口；为 `api_case` 计划项增加接口事实源校验。新增或复用 `validate_api_case_runnable()`，检查接口定义、环境变量、鉴权配置、请求体和断言是否完整。

前端页面 / 交互：
接口 case 草稿展示接口 method、path、字段 diff、接口确认状态和运行依赖检查结果；未确认接口显示候选草稿标签；可运行接口 case 在 Case 中心和接口中心都提供运行入口。

状态流转：
接口未确认：`candidate_draft`；接口确认后才可进入 `pending_review` 或正式资产。正式设计资产还需区分 `runnable` / `not_runnable` 运行状态。

Guardrails：
接口 case 不得只依赖自然语言需求生成；未确认接口定义不得生成可执行正式接口 case；缺少环境、鉴权或断言时不得进入执行队列。

测试要求：
覆盖无接口定义失败、接口未确认时候选草稿、接口确认后可接受、正式 case 包含接口引用、缺环境 / 鉴权 / 断言时运行被阻止、依赖完整时能创建执行任务。

验收证据：
测试证明接口 case 的事实源可追溯。

非范围：
不实现接口中心字段 diff 本身，若缺失需在任务 7 / 接口中心专项中补。

### RCP-16：AutomationCandidate 数据模型与可行性评估

任务目标：
为自动化脚本 case 建立可行性判断对象，避免自动化脚本孤立生成。

PRD 对应条款：
`FR-CASE-020`、`FR-CASE-021`、`AC-CASE-013`。

前置依赖：
RCP-13、任务 10、任务 11。

输入：
功能 case、接口 case、元素资产、接口定义、App 版本、设备能力、测试数据、断言依赖。

输出：
`AutomationCandidate`、可行性等级、阻塞原因、缺失资产待办。

建议修改文件：
`backend/app/models/automation_candidate.py`、`backend/app/services/automation_candidate_service.py`、`backend/app/routers/test_cases.py`、`backend/tests/test_automation_candidate.py`。

数据模型：
`AutomationCandidate` 至少包含 `id`、`source_case_id`、`source_case_type`、`target_automation_type`、`feasibility_level`、`blocking_reasons`、`required_assets`、`interface_dependencies`、`element_dependencies`、`test_data_dependencies`、`recommended_environment`、`status`。

API / Service：
新增 `POST /api/cases/{id}/automation-candidates/evaluate`、`GET /api/cases/automation-candidates`。

前端页面 / 交互：
RCP-18 展示详情；RCP-21 完成集成视图。

状态流转：
`evaluating -> high | medium | low | blocked -> accepted_for_generation | dismissed`。

Guardrails：
没有来源功能 case 或接口 case，不允许生成自动化候选；资产缺失时必须生成待办或阻塞原因。

测试要求：
覆盖无来源 case 失败、缺元素资产 blocked、有完整资产 high、缺测试数据 medium / low。

验收证据：
测试证明自动化脚本不会孤立生成。

非范围：
不生成自动化脚本代码。

### RCP-17：自动化脚本 case 草稿生成、资产依赖门禁与可运行检查

任务目标：
基于 high / confirmed `AutomationCandidate` 生成自动化脚本 case 草稿，并保证正式入库前资产依赖完整；可执行自动化 case 必须能从平台内直接运行。

PRD 对应条款：
`FR-CASE-020`、`FR-CASE-021`、`FR-MOB-014`、`FR-MOB-015`、`AC-CASE-013`、`AC-MOB-009`、`AC-MOB-010`、Case 中心 Guardrails。

前置依赖：
RCP-16、RCP-14、RCP-15。

输入：
confirmed 生成计划项、AutomationCandidate、来源功能 / 接口 case、元素 / 接口 / 测试数据资产。

输出：
自动化脚本 case 草稿、资产依赖校验结果、运行依赖检查结果、阻断待办。

建议修改文件：
`backend/app/services/ai_case_draft_service.py`、`backend/app/services/automation_candidate_service.py`、`backend/app/skills/case_generate_skill.py`、`backend/tests/test_automation_case_generation.py`。

数据模型：
`AiCaseDraft.case_kind=automation_script`，并关联 `automation_candidate_id`、`source_case_id`、`element_dependencies`、`app_version_ref`、`device_requirements`、`test_data_dependencies`、`assertions`。

API / Service：
按计划生成草稿接口支持 `automation_script_case`；新增资产依赖二次校验。新增或复用 `validate_automation_case_runnable()`，检查来源 case、元素、App、设备、测试数据和断言。

前端页面 / 交互：
草稿列表展示依赖资产、阻塞原因、运行依赖检查结果和来源 case；可运行自动化 case 在 Case 中心和移动端执行中心都提供运行入口。

状态流转：
候选 high 且已确认后才能 `draft_generated`；medium / low / blocked 只能进入待办或人工确认。正式设计资产还需区分 `runnable` / `not_runnable` 运行状态。

Guardrails：
自动化脚本 case 必须绑定功能 case 或接口 case；资产依赖不完整不得正式入库；运行依赖不完整不得进入执行队列。

测试要求：
覆盖无来源 case、无元素资产、无接口依赖、无 App / 设备 / 测试数据、AI 失败、成功生成但仍需人工确认、依赖完整时能创建执行任务。

验收证据：
测试证明资产依赖校验在后端生效。

非范围：
不做真实设备执行。

### RCP-18：Case 详情覆盖状态、生成计划、差异与历史版本整合

任务目标：
把 case 详情从普通资产详情升级为可信覆盖资产详情。

PRD 对应条款：
`FR-CASE-007`、`FR-CASE-010`、`FR-CASE-013`、`FR-CASE-022`、`AC-CASE-014`。

前置依赖：
RCP-14、RCP-15、RCP-16、RC-06。

输入：
正式 case、来源需求点、RequirementDiff、CoverageMatrixItem、CaseGenerationPlanItem、版本快照、执行摘要、健康信号。

输出：
case 详情聚合 API 和前端详情视图。

建议修改文件：
`backend/app/services/case_service.py`、`backend/app/routers/test_cases.py`、`frontend/src/modules/cases/api.js`、`frontend/src/modules/cases/pages/CasesPage.vue`、`backend/tests/test_case_traceability.py`。

数据模型：
复用 `CaseSourceRelation`、`CaseVersion`、`CaseHealthSignal`、覆盖矩阵和生成计划关联字段。

API / Service：
增强 `GET /api/cases/{id}`，返回来源差异、覆盖状态、生成计划、版本历史、健康信号、最近执行结果。

前端页面 / 交互：
详情页增加“来源追溯 / 覆盖状态 / 生成计划 / 历史版本 / 健康信号”区域。

状态流转：
关键字段修改后 case 进入 `needs_reconfirm` 或 `needs_validation`。

Guardrails：
详情展示不能只显示 AI 文本；必须能跳转到结构化来源对象。

测试要求：
覆盖详情聚合字段、关键字段修改产生版本快照、来源缺失时标记不可信。

验收证据：
后端测试和前端构建通过。

非范围：
不改执行中心。

### RCP-19：AI 草稿人工编辑、批量同意门禁与绕过路径防护

任务目标：
确保人工编辑和批量同意 AI 草稿不能绕过字段契约、覆盖矩阵、生成计划、草稿门禁、运行依赖校验和人工确认。

PRD 对应条款：
`FR-REQ-029`、`FR-CASE-023`、`FR-CASE-025`、`FR-CASE-026`、`FR-CASE-027`、`AC-CASE-015`、`AC-CASE-017`、`AC-CASE-018`、需求中心 / Case 中心 Guardrails。

前置依赖：
RCP-10、RCP-13、RC-05。

输入：
AI 草稿、生成计划、覆盖矩阵、字段契约校验结果、运行依赖检查结果、用户编辑和批量操作请求。

输出：
安全的单条编辑、重新校验、单条接受和批量同意 API，缺口清单和阻断错误。

建议修改文件：
`backend/app/services/ai_case_draft_service.py`、`backend/app/services/case_service.py`、`backend/app/routers/test_cases.py`、`frontend/src/modules/cases/pages/CasesPage.vue`、`backend/tests/test_case_batch_accept_gate.py`。

数据模型：
复用 `AiCaseDraft`、`CaseGenerationPlan`、`CoverageMatrixItem`，新增或复用 `CaseReviewBatch` 记录批量同意批次号、确认人、确认时间和失败明细。

API / Service：
新增或增强 `PATCH /api/cases/drafts/{id}`、`POST /api/cases/drafts/{id}/recheck`、`POST /api/cases/drafts/batch-accept`；统一调用 `validate_draft_acceptance()`。

前端页面 / 交互：
批量同意前展示阻断项；无法同意的草稿展示原因。默认支持单条编辑后重新校验；批量编辑只允许低风险字段，步骤、断言、接口请求、元素依赖和预期结果仍需逐条复核或重新门禁。

状态流转：
只有 `gate_passed + pending_review + plan_confirmed + coverage_ready + skill_contract_valid + runnable_dependency_valid_or_not_required` 的草稿可接受。

Guardrails：
后端必须阻止直接 API 绕过；批量操作不能跳过单条校验；批量同意不得掩盖字段缺失、接口未确认、自动化资产缺失或覆盖缺口。

测试要求：
覆盖无计划、计划 stale、覆盖缺口、check_failed 草稿、字段契约缺失、接口未确认、自动化依赖缺失、成功批量同意、批次记录和失败清单。

验收证据：
测试证明批量接受与单条接受走同一校验。

非范围：
不改 AI 生成逻辑。

### RCP-20：统一 RunnableCheck、运行入口与覆盖矩阵回写

任务目标：
建立统一 `RunnableCheck` 机制，让接口 case、自动化 case 和未来可执行资产都使用同一种可运行检查结果；在检查通过后可从平台直接运行，并让执行结果反向更新覆盖矩阵，区分新需求执行、历史需求回归执行和未执行缺口。`RunnableCheck` 失败后必须按“可立即修复 / 资产维护 / 需求或 case 设计问题”分流处理。

PRD 对应条款：
`FR-REQ-027`、`FR-REQ-030`、`FR-EXEC-014`、`FR-EXEC-015`、`FR-EXEC-016`、`FR-EXEC-017`、`FR-EXEC-018`、`FR-EXEC-019`、`FR-EXEC-020`、`FR-EXEC-021`、`FR-EXEC-022`、`FR-EXEC-023`、`FR-EXEC-024`、`FR-EXEC-025`、`AC-EXEC-008`、`AC-EXEC-009`、`AC-EXEC-010`、`AC-EXEC-011`、`AC-EXEC-012`、`AC-EXEC-013`、`AC-EXEC-014`、`FR-REPORT-013`、`FR-REPORT-014`。

前置依赖：
RCP-08、任务 8、任务 9、任务 11、任务 12。

输入：
接口 case、自动化 case、未来可执行 case 类型、统一 `RunnableCheck` 结果、执行任务结果、覆盖矩阵项、报告证据。

输出：
Case 中心 / 接口中心 / 移动端执行中心的运行入口、统一 `RunnableCheck` 服务、统一可运行状态面板、快捷修复入口、待办流转、设计回流入口、自动重检、覆盖矩阵执行状态、报告覆盖摘要、未执行缺口。

建议修改文件：
`backend/app/models/runnable_check.py`、`backend/app/services/runnable_check_service.py`、`backend/app/services/test_executor.py`、`backend/app/services/case_service.py`、`backend/app/services/todo_service.py`、`backend/app/services/coverage_matrix_service.py`、`backend/app/services/report_service.py`、`backend/app/routers/executions.py`、`backend/app/routers/test_cases.py`、`frontend/src/modules/cases/pages/CasesPage.vue`、`frontend/src/modules/api/`、`frontend/src/modules/mobile/`、`frontend/src/modules/todos/`、`backend/tests/test_runnable_check.py`、`backend/tests/test_executable_case_dependencies.py`、`backend/tests/test_coverage_execution_writeback.py`。

数据模型：
新增 `RunnableCheck`、`RunnableCheckItem`；可新增 `ExecutionCoverageLink` 或复用执行结果与矩阵项关联表；case 需要区分设计状态和运行状态，例如 `design_status` 与 `runnable_status`。`RunnableCheck` 至少包含 case、case 类型、是否可运行、运行状态、风险级别、检查时间、检查来源和触发人；`RunnableCheckItem` 至少包含依赖类型、依赖对象、检查结果、阻断原因、修复入口、关联待办、处理分类和最近一次重检结果。处理分类至少包括 `quick_fix`、`asset_maintenance`、`design_rework`。

API / Service：
新增 `RunnableCheckService.check(case_id, source)`、`RunnableCheckService.get_latest(case_id)`、`RunnableCheckService.refresh(case_id)`、`RunnableCheckService.apply_quick_fix(item_id, payload)`；各类型 case 只实现依赖适配器，例如 `ApiCaseRunnableAdapter`、`AutomationCaseRunnableAdapter`，统一由 `RunnableCheckService` 输出结果。执行入口调用 `execute_case_from_source(case_id, source)` 前必须读取最新 `RunnableCheck`。立即修复后自动调用 `refresh()` 重新检查，但不得自动执行 case；执行完成后调用 `CoverageMatrixService.writeback_execution_result()`。

前端页面 / 交互：
Case 中心、接口中心和移动端执行中心都提供运行入口，并展示同一份 `RunnableCheck` 状态；运行前展示是否可运行、缺失依赖、阻断原因、修复入口、关联待办和最近检查时间。`quick_fix` 问题在当前页面直接提示和修复；`asset_maintenance` 问题进入待办或来源资产模块；`design_rework` 问题回到覆盖矩阵、生成计划或 case 编辑。覆盖矩阵页签展示最近执行状态；报告中心展示覆盖摘要。

状态流转：
RunnableCheck 状态：`unknown -> checking -> runnable | not_runnable | blocked | stale`；case 运行状态：`not_runnable -> runnable -> queued -> running -> passed | failed | blocked | skipped`；矩阵项执行状态：`not_executed -> passed | failed | blocked | skipped`。

Guardrails：
废弃 case 执行结果不能算有效覆盖；取消任务不生成正式覆盖证据；字段契约完整不等于可运行，接口、环境、鉴权、元素、App、设备、测试数据和断言依赖必须通过 `RunnableCheck` 单独校验；各模块不得绕过 `RunnableCheck` 自行判断可运行状态。可立即修复的问题不得制造待办噪音；资产维护问题不得仅用页面提示替代待办；设计问题不得通过待办中心简单核销绕过覆盖矩阵、生成计划或 case 编辑。立即修复后只能自动重新检查，不得自动执行 case。

测试要求：
覆盖接口 case 依赖完整时 `RunnableCheck=runnable`、接口依赖缺失时 `not_runnable` 并给出修复入口；自动化 case 依赖完整时 `runnable`、元素 / App / 设备 / 测试数据缺失时 `not_runnable`；同一 case 在 Case 中心、接口中心、移动端执行中心展示同一份检查结果；`quick_fix` 修复后自动重检但不自动执行；`asset_maintenance` 生成或关联待办；`design_rework` 引导回覆盖矩阵 / 生成计划 / case 编辑；成功回写、失败回写、取消不回写、废弃 case 不计覆盖。

验收证据：
测试证明各入口共享同一份 `RunnableCheck`，且报告和矩阵能看到同一执行证据。

非范围：
不实现完整报告 UI 改造。

### RCP-21：需求中心与 Case 中心跨页集成工作台

任务目标：
把需求详情、问题项、基线、差异、覆盖矩阵、生成计划、AI 草稿和正式 case 串成可操作的前端工作流。

PRD 对应条款：
需求中心 UI Implications、Case 中心 UI Implications、`AC-REQ-012` - `AC-REQ-016`、`AC-CASE-010` - `AC-CASE-015`。

前置依赖：
RCP-04、RCP-10、RCP-13、RCP-18。

输入：
需求文档详情、基线、差异、覆盖矩阵、生成计划、草稿、case 详情。

输出：
需求中心和 Case 中心跨页跳转、筛选、状态提示和操作闭环。

建议修改文件：
`frontend/src/modules/requirements/api.js`、`frontend/src/modules/requirements/pages/RequirementsPage.vue`、`frontend/src/modules/cases/api.js`、`frontend/src/modules/cases/pages/CasesPage.vue`、公共 feedback 组件。

数据模型：
不新增模型。

API / Service：
消费前述 API；必要时增加轻量聚合接口。

前端页面 / 交互：
需求中心：原文 / 问题项 / 修订版 / 历史基线 / 差异分析 / 覆盖矩阵 / 检查结果。
Case 中心：case 列表 / AI 草稿 / 生成计划 / 覆盖矩阵 / 详情追溯。

状态流转：
页面状态必须与后端真实状态一致；生成、确认、接受、拒绝、风险接受后刷新相关视图。

Guardrails：
前端只做引导，不能通过隐藏按钮代替后端校验；所有失败使用统一弹窗或错误提示。

测试要求：
`cd frontend && npm run build`；如已引入前端测试框架，补基线页签、覆盖矩阵页签、生成计划确认、批量接受阻断交互测试。

验收证据：
前端构建通过；手工验收清单覆盖需求到 case 全链路。

非范围：
不新增后端核心逻辑。

### RCP-22：报告 / 首页覆盖证据链与 AI 上下文指标对齐

任务目标：
把 RCP 链路产生的基线、差异、覆盖矩阵、生成计划和执行回写，接入报告中心、首页质量驾驶舱和 AI 能力中心，避免全局流程末端只有后端数据、没有可复盘证据。

PRD 对应条款：
`FR-HOME-007`、`AC-HOME-005`、`FR-AI-014`、`FR-AI-015`、`AC-AI-008`、`AC-AI-009`、`FR-REPORT-013`、`FR-REPORT-014`、`FR-REPORT-015`。

前置依赖：
RCP-20、任务 13、任务 16。

输入：
CoverageMatrix、CaseGenerationPlan、RequirementDiff、执行结果、报告证据、AI 任务记录。

输出：
报告覆盖摘要、首页覆盖指标、AI 生成上下文追溯字段和对应 API / UI。

建议修改文件：
`backend/app/services/report_service.py`、`backend/app/services/coverage_matrix_service.py`、`backend/app/services/ai_task_service.py`、`backend/app/routers/reports.py`、`backend/app/routers/home.py` 或首页摘要路由、`frontend/src/modules/dashboard/`、`frontend/src/modules/reports/`、`frontend/src/modules/ai/`、`backend/tests/test_report_coverage_summary.py`、`backend/tests/test_ai_generation_context.py`。

数据模型：
可新增或复用 `ReportCoverageSummary`、`AiGenerationContext`、首页摘要 DTO；不得重复定义 RequirementDiff 或 CoverageMatrix。

API / Service：
新增报告覆盖摘要查询、首页覆盖指标摘要、AI 任务生成上下文查询；报告中的 AI 风险摘要必须能跳转到 CoverageMatrix、执行证据、变更记录或待办。

前端页面 / 交互：
首页展示未处理需求差异数、未覆盖需求点数、待确认生成计划数、自动化候选未落地数、新需求覆盖率和历史回归通过率；报告详情展示需求点、差异、生成计划项、历史基线回归项和未覆盖缺口。

状态流转：
执行回写后同步刷新报告覆盖摘要和首页指标；覆盖矩阵 stale 时首页指标必须标记为待刷新或不可作为最终质量结论。

Guardrails：
报告不能只证明 case 执行过，还必须证明对应需求点 / 差异 / 覆盖缺口是否被验证；AI 上下文不得缺失基线、差异、覆盖矩阵和生成计划。

测试要求：
覆盖报告展示新需求未执行、历史需求已回归、AI 风险摘要可追溯、首页指标聚合；前端构建通过。

验收证据：
测试和构建结果；可在报告和首页看到 RCP 链路产生的覆盖证据。

非范围：
不重新实现覆盖矩阵计算。

### RCP-23：种子数据、端到端验收夹具与长任务回归命令

任务目标：
为长时间 AI agent 开发提供稳定可复现的数据和测试命令，减少每个 agent 重新造数据。

PRD 对应条款：
`AC-REQ-001` - `AC-REQ-016`、`AC-CASE-001` - `AC-CASE-015`、Release Readiness Checklist。

前置依赖：
RCP-01 - RCP-22。

输入：
示例需求文档、接口文档、历史基线、已有 case、废弃 case、负样本、执行结果、报告覆盖摘要、首页指标。

输出：
测试夹具、种子数据脚本、回归命令清单、端到端验收用例。

建议修改文件：
`backend/tests/fixtures/`、`backend/tests/test_requirement_case_e2e.py`、`backend/tests/test_prd_requirement_case_coverage.py`、可选 `scripts/seed_requirement_case_demo.py`。

数据模型：
覆盖所有新增模型。

API / Service：
端到端调用真实 API 或 service。

前端页面 / 交互：
不强制新增 UI。

状态流转：
覆盖文档上传、解析、问题处理、入库、基线、差异、覆盖矩阵、生成计划、草稿、接受、正式 case、执行回写、报告覆盖摘要和首页指标。

Guardrails：
测试中 AI 调用必须 mock 成真实 AI 成功 / 失败结果，不得恢复业务降级逻辑。

测试要求：
提供后端聚合测试命令和前端构建命令；必要时拆成短命令避免单测过慢。

验收证据：
最终回复必须列出命令、通过结果和覆盖链路。

非范围：
不实现新功能，只补测试和夹具。

### RCP-24：PRD 条款覆盖审计与缺失项关闭

任务目标：
逐条确认需求中心与 Case 中心 PRD 是否被开发任务覆盖，关闭遗漏、冲突和逻辑不清楚的问题。

PRD 对应条款：
需求中心 `FR-REQ-001` - `FR-REQ-032`、`AC-REQ-001` - `AC-REQ-016`、Case 中心 `FR-CASE-001` - `FR-CASE-023`、`AC-CASE-001` - `AC-CASE-015`、两个模块 Guardrails、Data / API / UI、AI Evaluation Strategy。

前置依赖：
RCP-23。

输入：
PRD、开发任务拆分、实现代码、测试结果。

输出：
覆盖审计结果、缺失项列表、冲突项列表、后续确认项。

建议修改文件：
可新增 `docs/product/需求中心Case中心PRD覆盖审计.md`，也可以在 PR / 最终回复中输出。

数据模型：
不新增。

API / Service：
不新增。

前端页面 / 交互：
不新增。

状态流转：
缺失项必须进入待办或任务文档，不得只在最终回复中口头说明。

Guardrails：
不能因为某条 PRD 复杂就标记为“后续优化”；只有真正需要产品确认的阈值、评分规则、枚举策略可以进入 Open Questions。

测试要求：
运行 RCP-23 定义的回归命令；检查 `ReadLints` 无新增诊断。

验收证据：
输出逐条覆盖结论：已覆盖、部分覆盖、未覆盖、需产品确认。

非范围：
不写业务代码。

### 3.2.2 PRD 逐条覆盖检查矩阵

需求中心覆盖：

- `FR-REQ-001` - `FR-REQ-004`：由任务 3 承接，RCP-01 复核原始文件下载、预览和影响提示是否仍有缺口。
- `FR-REQ-005` - `FR-REQ-010`：由任务 4、RC-02、RC-04 承接，其中任务 4 仅为早期基础解析门禁；RCP-06 / RCP-07 补齐 PRD v2 要求的差异分析后入库门禁。
- `FR-REQ-011` - `FR-REQ-012`：由任务 3、RC-06 承接，RCP-18 / RCP-24 检查关联关系和影响提示是否包含基线、差异、覆盖矩阵和生成计划。
- `FR-REQ-013` - `FR-REQ-021`：由 RC-01 - RC-03、RC-08 承接，RCP-07 保证差异阻断也进入问题项。
- `FR-REQ-022` - `FR-REQ-023`：由 RCP-02 - RCP-04 承接。
- `FR-REQ-024` - `FR-REQ-026`：由 RCP-05 - RCP-07 承接，且 `FR-REQ-008` 业务耦合检查由 RCP-06 / RCP-07 补充为 AI 检查结果和问题项沉淀。
- `FR-REQ-027` - `FR-REQ-030`：由 RCP-08 - RCP-10、RCP-20 承接；`AC-REQ-016` 的批量生成门禁由 RCP-10 覆盖，批量接受门禁由 RCP-19 覆盖。
- `FR-REQ-031`：由 RCP-11 - RCP-13 承接。
- `FR-REQ-032`：由 RCP-01、RCP-18、RCP-24 检查并补齐影响提示。
- `AC-REQ-001` - `AC-REQ-011`：由任务 3、任务 4、RC-01 - RC-03 承接。
- `AC-REQ-012` - `AC-REQ-016`：由 RCP-03、RCP-04、RCP-06、RCP-07、RCP-10、RCP-19 承接。

Case 中心覆盖：

- `FR-CASE-001` - `FR-CASE-004`：由任务 5、任务 6、RC-05 承接，但任务 5 / RC-05 中所有直生成入口必须在 RCP-01 标记废弃并迁移到 RCP-13 / RCP-14 / RCP-15 / RCP-17；RCP-19 复核批量接受门禁。
- `FR-CASE-005`：由 RC-09 承接，RCP-14 / RCP-19 确认负样本继续参与计划生成后的草稿门禁。
- `FR-CASE-006` - `FR-CASE-010`：由任务 6、RC-05、RC-06 承接，RCP-18 补齐覆盖、差异和计划展示。
- `FR-CASE-011` - `FR-CASE-014`：由 RC-05、RC-07 承接，RCP-12 / RCP-18 检查废弃建议和健康信号进入生成计划。
- `FR-CASE-015` - `FR-CASE-017`：由 RCP-11 - RCP-13 承接。
- `FR-CASE-018`：由 RCP-14 承接。
- `FR-CASE-019`：由 RCP-15 承接。
- `FR-CASE-020` - `FR-CASE-021`：由 RCP-16 - RCP-17 承接。
- `FR-CASE-022`：由 RCP-18 承接。
- `FR-CASE-023`：由 RCP-19 承接。
- `FR-CASE-024` - `FR-CASE-027`：由 RCP-14、RCP-15、RCP-17、RCP-19 承接，覆盖 `test_case` skill 字段契约、人工编辑、批量同意和批量编辑边界。
- `AC-CASE-001` - `AC-CASE-009`：由任务 5、任务 6、RC-05、RC-07、RC-09 承接。
- `AC-CASE-010` - `AC-CASE-015`：由 RCP-13、RCP-15、RCP-16、RCP-18、RCP-19 承接。
- `AC-CASE-016` - `AC-CASE-018`：由 RCP-14、RCP-19 承接，覆盖字段契约校验、人工编辑后重校验和批量同意失败清单。

Guardrails / Data / API / UI / AI Evaluation 多维覆盖：

- 需求中心 Guardrails：RC-02 承接问题项门禁；RCP-07 承接差异门禁；RCP-10 承接覆盖矩阵门禁；RCP-01 / RCP-24 检查旧直生成入口是否已废弃。
- Case 中心 Guardrails：RC-05 承接草稿接受 / 拒绝 / 废弃契约；RCP-13 承接生成计划确认门禁；RCP-16 / RCP-17 承接自动化候选和资产依赖门禁；RCP-19 承接批量接受绕过路径。
- 需求中心 Data / API / UI：RCP-02 - RCP-04 承接基线；RCP-05 - RCP-07 承接差异和最小差异 UI；RCP-08 - RCP-10 承接覆盖矩阵和缺口处理 UI；RCP-21 承接最终集成工作台。
- Case 中心 Data / API / UI：RCP-11 - RCP-13 承接生成计划；RCP-14 - RCP-17 承接三类 case 草稿和自动化候选；RCP-18 承接 case 详情可信资产视图；RCP-21 承接跨页集成工作台。
- 可执行 case 运行链路：RCP-15 承接接口 case 可运行字段和依赖适配；RCP-17 承接自动化 case 可运行字段和依赖适配；RCP-20 承接统一 `RunnableCheck` 数据模型、服务、API、UI、运行入口、执行任务创建和覆盖矩阵回写。所有入口的“是否可运行”必须以同一份 `RunnableCheck` 为准。
- AI Evaluation Strategy：RCP-06 记录差异分析和耦合检查 AI 上下文；RCP-09 记录覆盖评估 AI 上下文；RCP-12 记录生成计划评估；RCP-14 / RCP-15 / RCP-17 分别记录功能 / 接口 / 自动化脚本草稿生成的 Prompt、Skill、负样本、Evaluator 和人工采纳结果；RCP-22 汇总到 AI 能力中心指标和报告 / 首页证据链。
- 报告 / 首页 / AI 全局证据：RCP-20 写回执行结果到 CoverageMatrix；RCP-22 展示报告覆盖摘要、首页覆盖指标和 AI 生成上下文；RCP-23 / RCP-24 用端到端测试和审计关闭遗漏。

专项逻辑检查结论：

- 旧 `RC-*` 专项覆盖“可信闭环基础”，新 `RCP-*` 专项覆盖“新版 PRD 全量平台逻辑”。两者不是重复关系。
- 需求中心的基线、差异、覆盖矩阵不应放入 Case 中心实现；Case 中心只消费这些事实并执行生成计划。
- Case 中心的生成计划不应反向修改需求事实源；若发现需求缺口，必须回到需求中心的问题项或覆盖缺口处理。
- 接口 case 和自动化脚本 case 虽然在 Case 中心展示和确认，但必须依赖接口中心、移动端元素资产和执行中心，不得孤立生成。
- 待办中心只承接复核入口，不直接修改需求、case、接口、覆盖矩阵或报告结论。
- AI agent 不得把缺少模型连接、缺少接口事实源、缺少元素资产、缺少覆盖矩阵解释为“可继续生成”；这些都是阻断或待确认状态。
- RCP-01 必须输出待废弃接口和门禁责任表；未完成该审计前，不得继续扩展任何旧的“从文档直接生成 case”接口。
- AI Evaluation 不只在任务 16 承接；RCP-06、RCP-09、RCP-12、RCP-14、RCP-15、RCP-17、RCP-22 都必须记录各自的 AI 输入、上下文、Prompt / Skill 版本、Evaluator 结果和人工采纳结果。

## 4. 推荐执行顺序

### 模块组一：框架与资产底座

建议先完成：

1. 任务 1：平台基础框架与健康检查
2. 任务 2：项目、模块树与基础权限上下文
3. 任务 3：需求文档上传、原文预览与关系树挂载
4. 任务 7：接口定义导入、确认与单接口调试
5. 任务 14：安全、脱敏、审计与配置中心

目标是先形成平台骨架、项目上下文、文档资产、接口事实源和安全底座。任务 6 依赖任务 5，不能在模块组一提前执行。

### 模块组二：需求到 case 与接口执行报告

建议推进两条过渡链路，并明确它们不是新版 PRD 最终合规主链路：

1. 任务 4：需求文档解析、逻辑检查与入库门禁
2. 任务 5：AI case 草稿生成、门禁检查与人工确认
3. 任务 6：Case 中心基础资产管理
4. 任务 8：接口 case 编写、Harness 基础能力与单 case 执行
5. 任务 9：接口执行报告与 HTML 证据链

目标是跑通早期工程切片：需求到 case、接口 case 到报告。进入 RCP 后，任务 5 的直生成入口必须废弃或重定向到 `CaseGenerationPlan`，不得继续作为正式主链路。

### 模块组三：移动端基础链路与统一执行

建议完成：

1. 任务 10：Android 设备识别、App 管理与元素资产基础链路
2. 任务 11：移动端 case 编辑、单设备执行与移动报告
3. 任务 12：统一执行中心、重试、取消与失败处理建议

目标是补齐 Android 移动端基础执行闭环，并把接口和移动端统一到执行中心。

### 模块组四：首页、待办与完整验收

建议在 RCP-20 / RCP-21 / RCP-22 后完成最终版首页、待办和完整验收：

1. 任务 13：首页质量驾驶舱与人工复核队列
2. 任务 18：待办中心独立复核队列
3. 任务 15：端到端执行验收与种子数据

目标是形成日常工作入口和可复现的完整验收包。任务 13 / 15 必须在 RCP 链路完成后补齐 Diff、CoverageMatrix、CaseGenerationPlan、AutomationCandidate 和历史回归指标，不得只验旧三条基础链路。

### 模块组五：AI 治理、变更闭环与预留模型

建议在需求、Case、接口、执行和报告基础链路稳定后推进，并在 RCP-22 对齐新版 AI 上下文治理：

1. 任务 16：AI 能力中心治理闭环
2. 任务 17：变更中心影响分析与回归推荐
3. 任务 19：Bug 标准模型与接入点预留

目标是补齐 PRD 中独立一级模块的治理能力，并为后续 Bug 中心和外部 connector 留好稳定扩展点。任务 16 必须扩展承接 `FR-AI-014` / `FR-AI-015`，记录基线、差异、覆盖矩阵、生成计划和分类型 case 草稿上下文。

### 模块组六：需求中心与 Case 中心补缺专项

如果当前开发目标聚焦“需求中心 + Case 中心完整闭环”，优先按 `RC-01 -> RC-10` 顺序执行，不再按 P0 / P1 分级：

1. RC-01：文档问题项、修订版与处理动作模型
2. RC-02：文档问题项处理 API 与入库 / 生成强门禁
3. RC-04：AI 调用不降级 Guardrail
4. RC-05：AI case 草稿、拒绝、废弃与正式入库契约修复
5. RC-03：需求中心问题项工作台前端闭环
6. RC-06：Case 来源追溯与可信详情补齐
7. RC-07：Case 健康度与废弃执行隔离
8. RC-08：需求问题项与待办队列联动
9. RC-09：负样本闭环与相似草稿门禁
10. RC-10：全量联动、绕过路径与验收证据

目标是形成可信主链路：文档解析与检查 -> 问题处理 -> 入库 -> AI case 草稿 -> 人工确认 -> 正式 case -> 废弃 / 负样本 / 待办 / 执行隔离。

### 模块组七：需求中心与 Case 中心 PRD 全量逻辑改造

当 `RC-*` 可信基础闭环可运行后，继续按 `RCP-*` 执行新版 PRD 的全量逻辑改造。该任务组不替代 `RC-*`，而是把平台从“文档入库后生成 AI case 草稿”升级为“历史基线 -> 差异分析 -> 覆盖矩阵 -> 生成计划 -> 分类型 case 草稿 -> 正式测试资产”。

建议执行顺序：

1. RCP-01：当前实现审计、数据迁移基线与任务护栏
2. RCP-02：RequirementBaseline 数据模型与基线版本体系
3. RCP-03：入库后基线生成 / 更新 / 首次基线确认服务
4. RCP-04：历史基线 API 与需求中心基线 UI
5. RCP-05：RequirementDiff 数据模型、枚举与证据结构
6. RCP-06：新旧需求差异分析服务与 AI 任务记录
7. RCP-07：差异阻断、问题项联动与变更中心事件输出
8. RCP-08：CoverageMatrix 数据模型与覆盖状态机
9. RCP-09：需求点 / 差异到已有 case 的覆盖计算服务
10. RCP-10：覆盖矩阵缺口处理、风险接受与前端工作台
11. RCP-11：CaseGenerationPlan 数据模型与状态流转
12. RCP-12：基于覆盖矩阵的生成计划推荐服务
13. RCP-13：生成计划确认、编辑、批量门禁与待办联动 UI
14. RCP-14：功能 case 草稿生成策略与覆盖类型绑定
15. RCP-15：接口 case 草稿生成策略与接口事实源绑定
16. RCP-16：AutomationCandidate 数据模型与可行性评估
17. RCP-17：自动化脚本 case 草稿生成与资产依赖门禁
18. RCP-18：Case 详情覆盖状态、生成计划、差异与历史版本整合
19. RCP-19：AI 草稿批量接受门禁与绕过路径防护
20. RCP-20：执行结果回写覆盖矩阵与历史回归状态同步
21. RCP-21：需求中心与 Case 中心跨页集成工作台
22. RCP-22：报告 / 首页覆盖证据链与 AI 上下文指标对齐
23. RCP-23：种子数据、端到端验收夹具与长任务回归命令
24. RCP-24：PRD 条款覆盖审计与缺失项关闭

目标是形成新版 PRD 的完整可信链路：文档解析与问题处理 -> 人工确认入库 -> 历史基线 -> 新旧差异 -> 覆盖矩阵 -> 生成计划 -> 功能 / 接口 / 自动化脚本 case 草稿 -> 门禁与人工确认 -> 正式 case -> 执行回写覆盖矩阵 -> 报告和首页展示覆盖证据。

## 5. 待确认事项

以下事项会影响剩余任务粒度和验收口径：

1. 移动端基础链路是否最终固定为 完整交付范围。当前本文档按 `CONTEXT.md` 处理为 模块完整交付。
2. AI 能力当前完整版本可以在自动化测试中使用显式 mock，但业务运行路径不允许规则降级或模板降级；真实模型验收需要在系统设置中配置可用模型后单独执行。
3. 需求文档逻辑检查的当前完整版本门禁规则是否需要产品、测试和研发共同确认。
4. 接口执行验收是否已有固定 mock 服务或测试环境。
5. Android 移动端验收是否已有稳定模拟器、Appium 环境和样例 App。

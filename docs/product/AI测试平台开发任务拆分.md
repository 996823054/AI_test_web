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
- 需求中心与 Case 中心补缺专项已经覆盖问题项、修订版、AI 不降级、草稿确认、废弃隔离和负样本闭环，但需要补充目标文件、API、状态流转和测试命令，保证 AI agent 可直接编码。
- 原任务 3、4、5、6 的当前状态中仍有未完成项：PDF/Word 文本提取、原始文件下载、删除 / 归档影响提示、历史同模块需求对比、解析失败重试 UI、合并 AI case 草稿、Case 健康度展示。这些应在专项任务或后续模块任务中有明确承接。

当前按 `CONTEXT.md` 口径处理：平台按功能模块完整闭环开发，至少覆盖三条基础业务链路：

1. 需求文档 -> AI case 草稿 -> 测试人员确认 -> case 资产。
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

跑通“需求文档 -> AI case 草稿 -> 测试人员确认 -> 正式 case”的主链路。

#### 涉及模块

- 需求中心
- Case 中心
- AI 能力中心
- 待办队列

#### 前置依赖

- 任务 4：需求文档解析、逻辑检查与入库门禁

#### 开发内容

- 基于已入库需求点触发 case 草稿生成。
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

## 4. 推荐执行顺序

### 模块组一：框架与资产底座

建议先完成：

1. 任务 1：平台基础框架与健康检查
2. 任务 2：项目、模块树与基础权限上下文
3. 任务 3：需求文档上传、原文预览与关系树挂载
4. 任务 6：Case 中心基础资产管理
5. 任务 7：接口定义导入、确认与单接口调试
6. 任务 14：安全、脱敏、审计与配置中心

目标是先形成平台骨架、项目上下文、文档资产、case 资产、接口事实源和安全底座。

### 模块组二：需求到 case 与接口执行报告

建议并行推进两条主链路：

1. 任务 4：需求文档解析、逻辑检查与入库门禁
2. 任务 5：AI case 草稿生成、门禁检查与人工确认
3. 任务 8：接口 case 编写、Harness 基础能力与单 case 执行
4. 任务 9：接口执行报告与 HTML 证据链

目标是跑通 当前核心链路：需求到 case、接口 case 到报告。

### 模块组三：移动端基础链路与统一执行

建议完成：

1. 任务 10：Android 设备识别、App 管理与元素资产基础链路
2. 任务 11：移动端 case 编辑、单设备执行与移动报告
3. 任务 12：统一执行中心、重试、取消与失败处理建议

目标是补齐 Android 移动端基础执行闭环，并把接口和移动端统一到执行中心。

### 模块组四：首页、待办与完整验收

建议最后完成：

1. 任务 13：首页质量驾驶舱与人工复核队列
2. 任务 18：待办中心独立复核队列
3. 任务 15：端到端执行验收与种子数据

目标是形成日常工作入口和可复现的完整验收包。

### 模块组五：AI 治理、变更闭环与预留模型

建议在需求、Case、接口、执行和报告基础链路稳定后推进：

1. 任务 16：AI 能力中心治理闭环
2. 任务 17：变更中心影响分析与回归推荐
3. 任务 19：Bug 标准模型与接入点预留

目标是补齐 PRD 中独立一级模块的治理能力，并为后续 Bug 中心和外部 connector 留好稳定扩展点。

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

## 5. 待确认事项

以下事项会影响剩余任务粒度和验收口径：

1. 移动端基础链路是否最终固定为 完整交付范围。当前本文档按 `CONTEXT.md` 处理为 模块完整交付。
2. AI 能力当前完整版本可以在自动化测试中使用显式 mock，但业务运行路径不允许规则降级或模板降级；真实模型验收需要在系统设置中配置可用模型后单独执行。
3. 需求文档逻辑检查的当前完整版本门禁规则是否需要产品、测试和研发共同确认。
4. 接口执行验收是否已有固定 mock 服务或测试环境。
5. Android 移动端验收是否已有稳定模拟器、Appium 环境和样例 App。

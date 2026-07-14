# AI 测试平台 AI 可执行开发计划

## 1. 文档用途

本文档用于把 AI 测试平台拆成可交给 AI agent 执行的垂直切片任务。每个任务都应尽量交付一条可演示、可验证的端到端能力，而不是只完成数据库、后端或前端中的某一层。

参考文档：

- `docs/product/AI测试平台PRD.md`
- `docs/product/AI测试平台模块功能逻辑确认.md`
- `docs/architecture/平台技术架构.md`
- `docs/architecture/平台技术架构.md`
- `CONTEXT.md`

当前模块完整开发口径：

1. 需求文档 -> AI case 草稿 -> 测试人员确认 -> case 资产。
2. API case -> 单 case 执行 / 调试 -> 报告。
3. Android 设备 / 移动端基础路径 -> 设备识别 -> 移动 case 编辑 / 执行证据。

说明：本开发计划不再按阶段标签区分移动端能力，Android 移动端能力按模块完整交付口径进入完整验收范围。

## 2. AI agent 执行通用规则

每个任务开始前，AI agent 必须先阅读：

- 本任务说明。
- `docs/architecture/平台技术架构.md` 中相关章节。
- 当前代码中对应模块目录。

每个任务提交前，AI agent 必须完成：

- 后端相关改动：运行对应单测或最小可行接口验证。
- 前端相关改动：运行构建或至少完成页面自检。
- 涉及执行链路：提供可复现的验证步骤。
- 涉及 AI 输出：保留输入、输出、Prompt / Skill 版本、错误和人工确认边界。
- 涉及报告、日志、AI 输入：确认敏感字段经过脱敏处理。

禁止事项：

- 不要绕过 Service 直接在 Router 中写业务编排。
- 不要让 Runner 修改需求、case、报告主表。
- 不要让 Skill 直接写正式业务资产。
- 不要让 Evaluator 替代人工确认。
- 不要把未确认 AI 输出、未脱敏日志、检查未通过需求写入正式 RAG。
- 不要把预研能力混进当前完整验收主链路。

## 3. 任务总览

| ID | 任务名称 | 类型 | 前置依赖 | AI agent 适合度 |
|---|---|---|---|---|
| T01 | 平台基础框架、导航与健康检查 | AFK | 无 | 适合 |
| T02 | 项目、模块树与基础权限上下文 | AFK | T01 | 适合 |
| T03 | 统一配置、安全脱敏与审计底座 | AFK | T01 | 适合 |
| T04 | 需求文档库、原文预览与关系树挂载 | AFK | T01、T02、T03 | 适合 |
| T05 | 需求文本提取、解析结果与入库门禁 | HITL | T04 | 部分适合 |
| T06 | AI 编排、Skill、Prompt、Evaluator 基础闭环 | HITL | T03、T05 | 部分适合 |
| T07 | AI case 草稿生成与人工确认入库 | HITL | T05、T06 | 部分适合 |
| T08 | Case 中心统一资产管理 | AFK | T02、T07 | 适合 |
| T09 | 接口定义、环境变量与单接口调试 | AFK | T01、T02、T03 | 适合 |
| T10 | 接口 case 编辑、Harness 与单 case 执行 | AFK | T08、T09 | 适合 |
| T11 | 接口执行报告与 HTML 证据链 | AFK | T10、T03 | 适合 |
| T12 | Android 设备、App 与元素资产基础链路 | HITL | T01、T02、T03 | 部分适合 |
| T13 | 移动端 case 编辑、Appium 执行与移动报告 | HITL | T08、T12 | 部分适合 |
| T14 | 统一执行中心、任务治理、重试与取消 | AFK | T10、T11、T13 | 适合 |
| T15 | 首页质量驾驶舱与人工复核队列 | AFK | T05、T07、T11、T14 | 适合 |
| T16 | RAG 生命周期基础闭环与知识片段治理 | HITL | T03、T05、T07、T11 | 部分适合 |
| T17 | Prompt / Skill 管理后台与版本绑定 | HITL | T06、T16 | 部分适合 |
| T18 | 端到端验收、种子数据与回归脚本 | HITL | T01-T15 | 部分适合 |

类型说明：

- AFK：边界清楚，AI agent 可独立开发、验证并提交。
- HITL：需要人工确认规则、模型、设备环境或最终验收。

## 4. 垂直切片任务

---

## T01：平台基础框架、导航与健康检查

### 1. 任务目标

搭建可稳定运行的前后端基础框架，让所有业务模块有统一入口、统一响应、统一错误处理和最小健康检查。

### 2. 涉及模块

- 前端：`app`、`shared`、`overview`、全局导航。
- 后端：`core`、`routers`、`modules`、`database`。
- 系统：启动脚本、环境变量、基础测试。

### 3. 前置依赖

无。

### 4. 开发内容

- 梳理并补齐 FastAPI 入口、路由注册、生命周期、配置加载、数据库连接。
- 建立统一 API 响应结构：`code`、`message`、`data`、`trace_id`。
- 建立统一异常处理和错误码约定。
- 补齐前端 Vue Router、全局布局、一级导航和空状态页面。
- 导航模块包含：首页 / 质量驾驶舱、需求中心、Case 中心、接口中心、移动端执行中心、执行中心、报告中心、AI 能力中心、系统设置。
- 增加健康检查接口：服务状态、数据库状态、配置加载状态。
- 提供本地启动说明和环境变量示例。

### 5. 验收标准

- 前后端可以在本地启动。
- 访问首页能看到一级模块导航。
- 健康检查接口返回服务、数据库和配置状态。
- API 成功和失败响应格式统一。
- 至少有一个后端基础测试覆盖健康检查。
- 前端构建或开发服务可正常运行。

### 6. 是否适合交给 AI agent 执行

适合，AFK。

### 7. 开发记录

#### 2026-05-19 后台 worker TDD 切片

- 任务选择规则：选择第一个未完成、无前置依赖且验收标准可通过公开接口验证的任务，因此从 T01 开始。
- 本轮可验收行为：
 - 调用 `GET /health` 时，接口通过统一响应结构返回服务、数据库、配置加载三类健康状态；调用方无需了解内部检查实现即可判断平台基础服务是否可用。
 - 访问前端首页导航时，一级导航包含 T01 约定的首页 / 质量驾驶舱、需求中心、Case 中心、接口中心、移动端执行中心、执行中心、报告中心、AI 能力中心、系统设置。
- RED 结果：
 - `PYTHONPATH=".venv/lib/python3.13/site-packages:." python -m unittest tests.test_health` 失败于 `KeyError: 'code'`，证明当前 `/health` 未返回统一响应结构。
 - `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-navigation.mjs"` 失败于缺少 `首页 / 质量驾驶舱`，证明当前导航文案未覆盖 T01 一级模块要求。
- GREEN / refactor 结果：
 - 健康检查返回 `code`、`message`、`data`、`trace_id`，并在 `data` 中包含 `service`、`database`、`config` 状态。
 - 健康检查只暴露数据库类型，不暴露完整连接串。
 - 导航验证脚本通过，前端导航文案与 T01 要求对齐。
- 验证命令：
 - `PYTHONPATH=".venv/lib/python3.13/site-packages:." python -m unittest discover -s tests`
 - `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-navigation.mjs"`
 - `npm --prefix "/Users/binwu/Desktop/Ai_test_web/frontend" run build`
- 改动摘要：补充健康检查接口测试和实现；补充导航验证脚本；调整前端一级导航文案；完成前端构建验证。
- 剩余风险 / 剩余任务：T01 整体仍处于进行中，后面应继续用 TDD 切片覆盖全局 API 失败响应格式、一键启动脚本的真实启动验证，以及必要的环境变量样例说明；不要将 T01 整体标记为完成。
- 当前状态：本轮 TDD 切片完成，T01 整体进行中。

#### 2026-05-19 左侧功能归类补充 TDD 切片

- 触发原因：前一轮 T01 只验证了一级导航存在性，未验证左侧导航是否按需求文档的信息架构进行功能归类。
- 文档依据：
 - `docs/product/AI测试平台PRD.md` 确认平台采用 9 个一级模块，并要求 Case 中心承接回归治理、AI 能力中心合并 AI 工作台 / RAG / Prompt / Evaluator / 模型效果 / 反馈样本库 / AI 成本监控。
 - `docs/product/AI测试平台模块功能逻辑确认.md` 确认核心闭环为“文档解析与检查 -> 入库落档 -> 生成测试 case / 接口 case / 移动端自动化 case -> 门禁检查 -> 人工确认 -> 执行 -> 报告”，且 Bug、独立回归治理和复杂待办流程不纳入当前主线。
 - `docs/delivery/AI测试平台开发任务拆分.md` 与本计划均将 T01 边界限定为前端路由、页面布局、导航菜单和空状态页面，不扩大到其他业务模块实现。
- 本轮可验收行为：
 - 左侧导航不仅包含 9 个确认一级模块，还必须按文档归类展示分组标题和分组下功能项。
 - 本切片采用的最小确定分组为：质量工作台：首页 / 质量驾驶舱；测试资产中台：需求中心、Case 中心、接口中心；执行与报告闭环：移动端执行中心、执行中心、报告中心；AI 能力中心：AI 能力中心；系统设置：系统设置。
 - 左侧导航不把“治理中心”作为 T01 一级入口；变更、回归、待办等边界按文档从首页、Case 中心、AI 能力中心、报告中心等既有模块承接。
- RED 结果：
 - 更新 `frontend/scripts/verify-navigation.mjs` 后，执行 `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-navigation.mjs"` 失败于 `缺少左侧导航分组：质量工作台`，证明当前前端仍按阶段分组，未按需求文档归类。
- GREEN / refactor 结果：
 - `frontend/src/app/navigation.js` 的 `navGroups` 调整为上述文档分组，保留 9 个确认一级模块，并移除左侧导航中的独立“治理中心”入口。
 - 本轮未做大范围重构；仅复用现有 `navGroups`、`AppShell` 渲染方式和验证脚本补充行为断言。
- 验证命令：
 - `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-navigation.mjs"`
 - `npm --prefix "/Users/binwu/Desktop/Ai_test_web/frontend" run build`
- 改动摘要：补充导航验证脚本的分组结构断言；调整左侧导航分组标题和模块归属；前端构建生成最新 `frontend/dist` 产物。
- 剩余风险 / 剩余任务：T01 整体仍处于进行中；本切片只覆盖左侧导航归类，不代表一键启动、全局失败响应格式、空状态页面和环境变量样例已全部验收完成。
- 当前状态：左侧功能归类补充切片完成，T01 整体进行中。

---

## T02：项目、模块树与基础权限上下文

### 1. 任务目标

建立平台所有资产的项目和模块归属，避免需求、case、接口、执行、报告后面缺少上下文。

### 2. 涉及模块

- 系统设置
- 首页 / 质量驾驶舱
- 需求中心
- Case 中心
- 接口中心
- 执行中心

### 3. 前置依赖

- T01：平台基础框架、导航与健康检查

### 4. 开发内容

- 建立 `projects` 数据模型和 CRUD。
- 建立 `module_nodes` 数据模型和 CRUD。
- 模块树支持业务域 -> 模块 -> 功能的层级关系。
- 前端支持当前项目选择、模块树查看和基础维护。
- 后端核心资产模型预留 `project_id`、`module_id`。
- 实现基础角色：管理员、测试人员、只读用户。
- Router 层统一校验项目上下文和基础权限。

### 5. 验收标准

- 用户可以创建、编辑、删除项目。
- 用户可以创建和维护模块树。
- 用户可以切换当前项目。
- 创建需求文档、case、接口时可以选择项目和模块。
- 只读用户不能创建、修改、删除资产。
- 首页指标可以按当前项目过滤。

### 6. 是否适合交给 AI agent 执行

适合，AFK。

---

## T03：统一配置、安全脱敏与审计底座

### 1. 任务目标

建立 完整交付前必须具备的安全、脱敏、密钥引用和审计能力，供接口执行、报告、AI 调用和 RAG 入库复用。

### 2. 涉及模块

- 系统设置
- 接口中心
- 执行中心
- 报告中心
- AI 能力中心
- RAG

### 3. 前置依赖

- T01：平台基础框架、导航与健康检查

### 4. 开发内容

- 建立统一脱敏函数，默认覆盖 Authorization、Cookie、token、password、secret、apikey 等字段。
- 建立密钥引用模型，密钥只允许写入和引用，不允许接口明文返回。
- 建立基础审计日志：关键配置修改、查看敏感信息、导出报告、AI 调用。
- 系统设置支持模型配置、环境配置、Appium capability、报告保留策略、脱敏规则。
- 后端提供配置读取接口，前端提供基础设置页面。
- AI 输入、RAG 入库、报告导出、执行日志展示前预留统一脱敏调用。

### 5. 验收标准

- 密钥创建后，查询接口不返回明文。
- 默认报告和普通日志不展示敏感字段明文。
- 修改关键配置会产生审计记录。
- 报告导出默认脱敏。
- AI 调用前可以确认已经过脱敏处理。
- 脱敏函数有单元测试覆盖常见敏感字段。

### 6. 是否适合交给 AI agent 执行

适合，AFK。脱敏字段清单可后面由人工补充。

---

## T04：需求文档库、原文预览与关系树挂载

### 1. 任务目标

把需求中心先建成可信文档库，支持原始文档查看、需求关系树挂载和基础文档管理。

### 2. 涉及模块

- 需求中心
- 文件存储
- 项目和模块树
- 系统设置

### 3. 前置依赖

- T01：平台基础框架、导航与健康检查
- T02：项目、模块树与基础权限上下文
- T03：统一配置、安全脱敏与审计底座

### 4. 开发内容

- 建立 `requirement_documents`、`requirement_document_versions`、`requirement_tree_nodes` 基础模型。
- 支持 PDF、Word、Markdown 文档上传。
- 保存原始文件、文件路径、文件大小、格式、上传人、上传时间、文件指纹。
- 支持文档在线预览和下载。
- 支持需求关系树：业务域 -> 模块 -> 功能 -> 需求版本 -> 验收点。
- 支持文档挂载到指定关系树节点。
- 支持文档移动、重命名、元信息修改、归档、软删除。
- 删除和归档前展示影响提示占位：需求条目数、关联 case 数、知识库片段数。
- 前端提供三栏视图：左侧关系树，中间文档列表，右侧文档详情 / 原文预览。

### 5. 验收标准

- 用户可以上传需求文档并挂载到需求树节点。
- 用户可以查看原始文档预览和下载原始文件。
- 用户可以移动文档到其他功能或版本节点。
- 归档文档不再出现在默认可用列表。
- 软删除文档不物理删除原始文件。
- 同名或重复文件有提示，不直接静默覆盖。

### 6. 是否适合交给 AI agent 执行

适合，AFK。

---

## T05：需求文本提取、解析结果与入库门禁

### 1. 任务目标

让需求文档在进入 case 生成前，先经过文本提取、结构化解析、逻辑检查和人工确认。

### 2. 涉及模块

- 需求中心
- AI 能力中心
- 待办队列
- RAG 预留

### 3. 前置依赖

- T04：需求文档库、原文预览与关系树挂载

### 4. 开发内容

- 支持 PDF、Word、Markdown 的文本提取。
- 建立 `requirement_items`、`requirement_check_results`。
- 封装 `RequirementParseSkill`，输出需求点、模块、重要性、风险、原文片段、AI 摘要。
- 实现基础检查：缺失项、模糊点、明显冲突、历史同模块需求对比占位。
- 实现文档状态流转：未解析、解析中、待确认、检查未通过、已入库、解析失败。
- 前端提供解析结果确认页。
- 检查未通过时，只允许查看问题、重新上传或重新解析，不允许生成 case。
- 解析和检查结果写入待办队列占位，供首页和待办入口展示。

### 5. 验收标准

- 上传文档后可以触发文本提取和解析。
- 用户能看到结构化需求点和原文依据。
- 用户能看到缺失、模糊、冲突等检查结果。
- 检查未通过的文档不能生成 case 草稿。
- 人工确认后，需求点进入正式可用状态。
- 解析失败展示错误原因和重试入口。

### 6. 是否适合交给 AI agent 执行

部分适合，HITL。基础流程适合 AI agent；检查规则、模型输出格式和门禁强度需要人工确认。

---

## T06：AI 编排、Skill、Prompt、Evaluator 基础闭环

### 1. 任务目标

建立统一 AI 调用链路，避免业务页面直接拼 Prompt 或直接调用模型，为需求解析、case 生成、失败分析、RAG 和评估能力打底。

### 2. 涉及模块

- AI 能力中心
- 需求中心
- Case 中心
- RAG
- 系统设置

### 3. 前置依赖

- T03：统一配置、安全脱敏与审计底座
- T05：需求文本提取、解析结果与入库门禁

### 4. 开发内容

- 建立 `AiOrchestrationService`。
- 建立 `skill_registry`、`prompt_templates`、`skill_prompt_bindings`、`ai_call_logs` 基础模型。
- 建立 Prompt 渲染器，支持变量注入和版本记录。
- 建立 Skill 调用契约：输入 schema、输出 schema、错误模式。
- 建立 Evaluator 基础契约：字段完整性、格式合法性、规则评分。
- 当前模块先支持规则 Evaluator；Phoenix Evaluator 可接入但不强制作为阻断门禁。
- 每次 AI 调用记录 Skill、Prompt 版本、模型、输入摘要、输出、耗时、错误。
- 前端 AI 能力中心提供 Skill / Prompt / 调用日志的只读或基础管理页面。

### 5. 验收标准

- 需求解析和 case 生成不直接从页面调用模型，而是通过 `AiOrchestrationService`。
- 每次 AI 调用都有日志。
- Prompt 修改能产生版本记录。
- Skill 能绑定 active Prompt。
- Evaluator 能返回 passed、score、label、rationale、issues。
- AI 调用失败时保留错误码、错误信息和重试入口。

### 6. 是否适合交给 AI agent 执行

部分适合，HITL。框架和数据结构适合 AI agent；Prompt 内容、模型选择和评估阈值需要人工确认。

---

## T07：AI case 草稿生成与人工确认入库

### 1. 任务目标

跑通需求文档到 AI case 草稿，再到测试人员确认入库为正式 case 的主链路。

### 2. 涉及模块

- 需求中心
- Case 中心
- AI 能力中心
- 待办队列

### 3. 前置依赖

- T05：需求文本提取、解析结果与入库门禁
- T06：AI 编排、Skill、Prompt、Evaluator 基础闭环

### 4. 开发内容

- 建立 `ai_case_drafts`。
- 封装 `CaseGenerateSkill`，基于已入库需求点生成 case 草稿。
- 保存原始 AI 输出、结构化草稿、来源需求、Prompt 版本、模型、Evaluator 结果。
- 实现 AI case 草稿状态：generated、evaluated、pending_review、accepted、edited、merged、rejected、archived。
- 前端提供 AI case 待确认页面。
- 支持接受、编辑后接受、拒绝、合并到已有 case 占位。
- 接受后写入 `test_cases`、`case_steps`、`case_source_links`。
- 拒绝后记录拒绝原因，并为负样本库预留。

### 5. 验收标准

- 已入库需求点可以生成 AI case 草稿。
- AI case 草稿展示来源需求、原文片段、AI 原始输出和门禁结果。
- 字段缺失或格式不合法的草稿不能入正式 case。
- 草稿必须经测试人员确认后才能写入正式 case。
- 拒绝的草稿不会污染正式 case 库。
- 正式 case 能追溯确认人、确认时间、来源需求和 AI 输出。

### 6. 是否适合交给 AI agent 执行

部分适合，HITL。状态机和页面适合 AI agent；case 模板和接受标准需要人工确认。

---

## T08：Case 中心统一资产管理

### 1. 任务目标

建立统一 case 资产中心，承接功能 case、接口 case、移动端 case 和 AI case 入库后的正式资产管理。

### 2. 涉及模块

- Case 中心
- 需求中心
- 接口中心
- 移动端执行中心
- 执行中心

### 3. 前置依赖

- T02：项目、模块树与基础权限上下文
- T07：AI case 草稿生成与人工确认入库

### 4. 开发内容

- 建立或补齐 `test_cases`、`case_steps`、`case_versions`、`case_source_links`。
- 支持 case 类型：功能 case、接口 case、移动端 case。
- 支持统一主状态：草稿、待确认、已启用、已废弃、需复核。
- 支持 case 创建、编辑、复制、废弃、版本快照。
- 支持 模块完整交付 / 重要性标记，作为当前回归依据。
- case 详情展示来源需求、原文片段、接口、元素、AI 生成依据、人工确认记录、最近执行记录。
- 修改步骤、断言、来源、接口或元素后，标记为需重新确认或验证。

### 5. 验收标准

- 用户可以创建、编辑、查看、废弃 case。
- AI 确认后的 case 能在 Case 中心查看。
- case 详情能看到来源和最近执行结果。
- 模块完整交付 / 重要性可以用于筛选。
- 修改关键字段后，case 状态能提示需重新确认或验证。
- case 版本快照能记录修改前后内容。

### 6. 是否适合交给 AI agent 执行

适合，AFK。

---

## T09：接口定义、环境变量与单接口调试

### 1. 任务目标

建立接口中心事实源，让接口 case 可以引用已确认接口定义，并支持单接口调试。

### 2. 涉及模块

- 接口中心
- 系统设置
- 执行中心
- 报告中心
- AI 能力中心

### 3. 前置依赖

- T01：平台基础框架、导航与健康检查
- T02：项目、模块树与基础权限上下文
- T03：统一配置、安全脱敏与审计底座

### 4. 开发内容

- 建立 `api_definitions`、`api_definition_versions`、`api_environments`、`api_variable_sets`、`api_auth_configs`、`api_debug_results`。
- 支持接口定义 CRUD：method、path、headers、params、body schema、response schema、状态码。
- 支持接口文档上传和基础解析占位，AI 解析可在后面增强。
- 支持候选接口 -> 人工确认 -> 可引用接口 -> 已验证接口。
- 支持环境、变量集、鉴权配置。
- 支持单接口调试，保存请求、响应、耗时、错误原因。
- 接口废弃后禁止被新 case 引用或执行。

### 5. 验收标准

- 用户可以创建并确认接口定义。
- 用户可以配置环境和变量。
- 用户可以执行单接口调试。
- 调试失败展示可行动错误原因。
- 接口详情能看到最近调试结果。
- 已废弃接口不能被 case 执行。

### 6. 是否适合交给 AI agent 执行

适合，AFK。

---

## T10：接口 case 编辑、Harness 与单 case 执行

### 1. 任务目标

跑通 API case 从编辑到执行任务、Harness 处理、Runner 执行、步骤结果写入的基础闭环。

### 2. 涉及模块

- Case 中心
- 接口中心
- 执行中心
- Harness
- Runner

### 3. 前置依赖

- T08：Case 中心统一资产管理
- T09：接口定义、环境变量与单接口调试

### 4. 开发内容

- 支持接口 case 步骤引用 `api_definitions`。
- 支持请求参数、变量提取、断言、超时、失败后是否继续执行。
- 建立 `execution_tasks`、`execution_step_results`、`dependency_records`。
- 建立最小 `HarnessService`，负责加载 case、环境、变量、鉴权、密钥引用、执行上下文。
- 建立或统一 `ApiRunner`，负责执行 HTTP 请求并返回标准化结果。
- 支持任务状态：pending、running、passed、failed、blocked、cancel_requested、cancelled、timeout。
- 支持步骤级结果、耗时、错误分类。

### 5. 验收标准

- 用户可以从接口 case 页面发起单 case 执行。
- 执行中心能看到任务状态和步骤状态。
- 请求失败、断言失败、变量提取失败能区分展示。
- 变量提取结果可以传递给后面步骤。
- 任务取消后不生成正式报告，只保留任务日志。
- Runner 不直接修改 case 或报告主表。

### 6. 是否适合交给 AI agent 执行

适合，AFK。需要人工提供一个可访问的接口样例或 mock 服务用于最终验收。

---

## T11：接口执行报告与 HTML 证据链

### 1. 任务目标

让接口执行结果具备可复盘证据链，报告不只展示通过或失败。

### 2. 涉及模块

- 报告中心
- 执行中心
- Case 中心
- 接口中心
- 安全脱敏

### 3. 前置依赖

- T10：接口 case 编辑、Harness 与单 case 执行
- T03：统一配置、安全脱敏与审计底座

### 4. 开发内容

- 建立 `test_reports`、`report_artifacts`、`report_confirmations`。
- 建立 `ReportService`，根据执行任务和步骤结果生成报告。
- 支持接口单 case HTML 报告。
- 报告包含 request、response、headers、断言 expected / actual、变量上下文、耗时、错误堆栈、脱敏状态。
- 支持报告在线预览和下载。
- 报告关联 task、case、接口、环境、执行人。
- 导出和展示默认脱敏。

### 5. 验收标准

- 接口执行完成后生成报告。
- 报告可以从执行任务和 case 详情进入。
- 失败报告能定位到具体步骤和断言。
- 报告展示 request / response / expected / actual。
- 报告导出默认脱敏。
- 取消任务不生成正式质量报告。

### 6. 是否适合交给 AI agent 执行

适合，AFK。

---

## T12：Android 设备、App 与元素资产基础链路

### 1. 任务目标

建立移动端自动化执行的基础资产，让移动 case 具备设备、App、元素上下文。

### 2. 涉及模块

- 移动端执行中心
- 系统设置
- Case 中心
- 报告中心

### 3. 前置依赖

- T01：平台基础框架、导航与健康检查
- T02：项目、模块树与基础权限上下文
- T03：统一配置、安全脱敏与审计底座

### 4. 开发内容

- 建立 `devices`、`device_locks`、`apps`、`mobile_pages`、`mobile_elements`。
- 支持 Android 设备识别：设备 ID、在线状态、系统版本、分辨率、占用状态。
- 支持设备锁基础逻辑，异常释放。
- 支持 APK 上传或 App 信息登记：package、versionName、versionCode、build。
- 支持 Appium XML 导入，生成元素资产。
- 元素绑定页面、模块、主定位、可读名称。
- 前端提供移动端执行中心基础页面。

### 5. 验收标准

- 平台能展示当前可用 Android 设备。
- 设备占用后其他任务不能同时使用。
- 设备异常或任务结束后能释放锁。
- App 信息能绑定到执行任务和报告。
- XML 导入后能生成可被移动 case 引用的元素。
- 当前模块完整交付暂不包含 iOS、云真机、多设备调度和 AI 视觉定位。

### 6. 是否适合交给 AI agent 执行

部分适合，HITL。代码实现适合 AI agent；设备、Appium 和模拟器环境需要人工协助验收。

---

## T13：移动端 case 编辑、Appium 执行与移动报告

### 1. 任务目标

跑通 Android 移动端基础闭环：移动 case 编辑、单设备 Appium 执行、截图 / XML / 日志报告。

### 2. 涉及模块

- 移动端执行中心
- Case 中心
- 执行中心
- 报告中心
- Runner

### 3. 前置依赖

- T08：Case 中心统一资产管理
- T12：Android 设备、App 与元素资产基础链路

### 4. 开发内容

- 支持移动端 case 步骤：点击、输入、等待、断言、截图。
- 正式移动端 case 必须引用元素资产。
- 调试态允许临时 locator，但调试成功后应沉淀为元素资产。
- 建立或统一 `MobileRunner`，负责 Appium session 和基础动作执行。
- 执行任务记录设备、App、capability、步骤状态。
- 失败时采集截图、XML、Appium 日志、错误信息。
- ReportService 支持移动端报告证据。
- 执行结束后释放设备锁。

### 5. 验收标准

- 用户可以选择单设备执行单条移动端 case。
- 执行报告绑定 App package、version、build。
- 失败报告包含失败步骤、截图、XML 或 Appium 日志中的关键证据。
- 正式移动 case 不允许只保存裸 locator。
- 执行结束或失败后释放设备锁。
- 不做多设备并发和 AI 视觉兜底。

### 6. 是否适合交给 AI agent 执行

部分适合，HITL。代码可交给 AI agent，Appium 环境和稳定性需要人工确认。

---

## T14：统一执行中心、任务治理、重试与取消

### 1. 任务目标

把接口和移动端执行统一到执行中心，提供任务列表、状态追踪、日志、取消、重跑和失败处理建议。

### 2. 涉及模块

- 执行中心
- Case 中心
- 接口中心
- 移动端执行中心
- 报告中心

### 3. 前置依赖

- T10：接口 case 编辑、Harness 与单 case 执行
- T11：接口执行报告与 HTML 证据链
- T13：移动端 case 编辑、Appium 执行与移动报告

### 4. 开发内容

- 执行中心统一展示所有 `execution_tasks`。
- 支持按项目、类型、状态、执行人、时间筛选。
- 支持任务详情：步骤状态、日志、耗时、错误、报告入口。
- 支持取消任务、重跑任务、最多 3 次重试策略。
- 支持失败分类和处理建议：重跑、检查环境、修复 case、标记 bug 占位、人工复核。
- 当前模块可使用进程内后台任务或轻量 worker；增强能力再升级 Celery / RQ / Arq。

### 5. 验收标准

- 接口任务和移动端任务都能在执行中心查看。
- 任务状态 100% 可追踪。
- 自动重试不超过 3 次。
- 取消任务不会生成正式质量报告。
- 失败任务能跳转到 case、接口 / 设备和报告。
- 日志中不展示敏感字段明文。

### 6. 是否适合交给 AI agent 执行

适合，AFK。

---

## T15：首页质量驾驶舱与人工复核队列

### 1. 任务目标

建立日常工作入口，让测试经理和测试人员能快速看到质量状态、待处理事项和高风险问题。

### 2. 涉及模块

- 首页 / 质量驾驶舱
- 待办队列
- 需求中心
- Case 中心
- 执行中心
- 报告中心
- AI 能力中心

### 3. 前置依赖

- T05：需求文本提取、解析结果与入库门禁
- T07：AI case 草稿生成与人工确认入库
- T11：接口执行报告与 HTML 证据链
- T14：统一执行中心、任务治理、重试与取消

### 4. 开发内容

- 建立 `todo_items` 基础模型。
- 首页展示需求数、case 数、接口数、设备状态、今日执行、失败任务、AI 待确认 case。
- 展示 AI 风险摘要，但必须包含证据来源、置信度、触发原因和人工确认边界。
- 待办来源包含：需求冲突、AI case 待确认、失败报告复核、设备异常、变更影响占位。
- 首页指标和待办支持跳转来源对象。
- 待办中心只做人工复核队列，不做复杂流程引擎。

### 5. 验收标准

- 测试经理进入首页后能看到核心质量状态。
- 首页指标能跳转到来源页面。
- AI 风险摘要不能只有自然语言结论，必须有证据和置信度。
- 用户能在待办队列处理 AI case 确认和失败报告复核。
- 待办处理后，来源对象状态同步更新。

### 6. 是否适合交给 AI agent 执行

适合，AFK。

---

## T16：RAG 生命周期基础闭环与知识片段治理

### 1. 任务目标

建立 RAG 生命周期的最小可用闭环，为后面 AI 生成、失败分析、变更影响分析提供可信上下文。

### 2. 涉及模块

- RAG
- AI 能力中心
- 需求中心
- Case 中心
- 报告中心
- 安全脱敏

### 3. 前置依赖

- T03：统一配置、安全脱敏与审计底座
- T05：需求文本提取、解析结果与入库门禁
- T07：AI case 草稿生成与人工确认入库
- T11：接口执行报告与 HTML 证据链

### 4. 开发内容

- 建立 `knowledge_chunks`、`rag_retrieval_logs`、`feedback_samples`。
- 实现知识片段来源类型：需求文档、需求点、正式 case、接口定义、失败报告摘要、负样本。
- 当前模块先支持结构化检索：项目、模块、来源类型、关键词、状态。
- 增强能力 预留 embedding 字段和向量检索适配。
- 入库前调用脱敏。
- 检查未通过需求、未确认 AI 输出、未脱敏日志不得进入正式知识库。
- 被拒绝 AI case 可进入负样本库。
- 记录召回日志：来源、权重、是否被采用、人工反馈。

### 5. 验收标准

- 已确认需求点和正式 case 可以生成知识片段。
- 检查未通过需求不能进入正式知识库。
- 未确认 AI case 不能进入正式知识库。
- 结构化检索能返回相关知识片段。
- 每次 RAG 召回都有日志。
- 负样本库与正式知识库有明确区分。

### 6. 是否适合交给 AI agent 执行

部分适合，HITL。结构和检索适合 AI agent；入库策略、召回权重和向量库选型需要人工确认。

---

## T17：Prompt / Skill 管理后台与版本绑定

### 1. 任务目标

让 Prompt 和 Skill 成为可治理资产，而不是散落在代码里的字符串，实现版本、绑定、测试、启用和回滚。

### 2. 涉及模块

- AI 能力中心
- 系统设置
- RAG
- Case 中心
- 需求中心

### 3. 前置依赖

- T06：AI 编排、Skill、Prompt、Evaluator 基础闭环
- T16：RAG 生命周期基础闭环与知识片段治理

### 4. 开发内容

- 完善 Skill 管理页面：Skill 名称、描述、输入 schema、输出 schema、启用状态、版本。
- 完善 Prompt 管理页面：Prompt 内容、变量、绑定 Skill、版本、状态。
- Prompt 状态支持 draft、testing、active、deprecated、rollback。
- 支持一个 Skill 按场景绑定多个 Prompt，例如功能 case、接口 case、移动端 case。
- Prompt 修改后必须进入 testing，跑样例集或评估集后才能 active。
- 每次业务 AI 调用记录 Skill、Prompt、模型、版本和 Evaluator 结果。
- 支持回滚到上一 active 版本。

### 5. 验收标准

- 用户可以查看 Skill 列表和绑定的 Prompt。
- 用户可以创建 Prompt 草稿并绑定 Skill。
- 只有 active Prompt 会被业务流程默认使用。
- Prompt 修改不会直接影响线上调用，必须先 testing。
- Prompt 回滚后，新 AI 调用使用回滚版本。
- AI 调用日志能追溯到 Skill 和 Prompt 版本。

### 6. 是否适合交给 AI agent 执行

部分适合，HITL。管理页面和状态机适合 AI agent；Prompt 质量标准和评估集需要人工确认。

---

## T18：端到端验收、种子数据与回归脚本

### 1. 任务目标

把三条基础业务链路用固定样例跑通，形成可重复执行的验收包，支持后续 AI agent 开发后的回归验证。

### 2. 涉及模块

- 全平台
- 需求中心
- Case 中心
- 接口中心
- 移动端执行中心
- 执行中心
- 报告中心
- AI 能力中心
- 系统设置

### 3. 前置依赖

- T01-T15
- T16、T17 可作为增强项，不阻塞模块完整交付基础验收

### 4. 开发内容

- 准备样例需求文档。
- 准备样例接口文档和 mock 接口服务。
- 准备样例移动端 App 或可执行 Demo 页面。
- 准备示例项目、模块树、接口定义、case、设备、App、元素数据。
- 编写端到端验收清单。
- 编写可重复执行的冒烟测试脚本。
- 验收三条主链路：
 - 需求文档 -> AI case 草稿 -> 人工确认 -> case 资产。
 - API case -> 单 case 执行 / 调试 -> HTML 报告。
 - Android 设备 -> 移动 case -> Appium 执行 -> 截图 / XML / 日志报告。
- 输出完整验收报告模板：通过项、失败项、阻塞项、风险项、后续建议。

### 5. 验收标准

- 三条基础业务链路都能从 UI 完整跑通。
- 每条链路都有可复用测试数据。
- 冒烟测试可以在本地重复执行。
- 验收失败能定位到具体模块和任务。
- 验收报告包含证据截图、接口响应、执行日志或报告链接。
- 新 AI agent 接手任务时，可以按该验收包复现平台核心能力。

### 6. 是否适合交给 AI agent 执行

部分适合，HITL。验收脚本和数据整理适合 AI agent；真实模型、移动设备、Appium 环境和最终验收需要人工确认。

## 5. 推荐执行顺序

### 模块组一：框架与事实源

建议顺序：

1. T01：平台基础框架、导航与健康检查
2. T02：项目、模块树与基础权限上下文
3. T03：统一配置、安全脱敏与审计底座
4. T04：需求文档库、原文预览与关系树挂载
5. T08：Case 中心统一资产管理
6. T09：接口定义、环境变量与单接口调试

目标：形成平台骨架、项目上下文、文档事实源、case 资产中心、接口事实源和安全底座。

### 模块组二：需求到 case 与接口执行报告

建议顺序：

1. T05：需求文本提取、解析结果与入库门禁
2. T06：AI 编排、Skill、Prompt、Evaluator 基础闭环
3. T07：AI case 草稿生成与人工确认入库
4. T10：接口 case 编辑、Harness 与单 case 执行
5. T11：接口执行报告与 HTML 证据链

目标：跑通需求到 case、API case 到执行报告两条主链路。

### 模块组三：移动端基础闭环与统一执行

建议顺序：

1. T12：Android 设备、App 与元素资产基础链路
2. T13：移动端 case 编辑、Appium 执行与移动报告
3. T14：统一执行中心、任务治理、重试与取消

目标：补齐 Android 移动端基础执行闭环，并统一接口与移动端执行治理。

### 模块组四：工作台、RAG 治理与验收

建议顺序：

1. T15：首页质量驾驶舱与人工复核队列
2. T16：RAG 生命周期基础闭环与知识片段治理
3. T17：Prompt / Skill 管理后台与版本绑定
4. T18：端到端验收、种子数据与回归脚本

目标：形成日常工作入口、AI 治理能力和可重复执行的验收包。

## 6. 可直接复制给 AI agent 的执行提示模板

```text
你要实现 docs/delivery/AI测试平台AI可执行开发计划.md 中的任务 <任务 ID>。

请先阅读：
1. docs/delivery/AI测试平台AI可执行开发计划.md 的任务说明
2. docs/architecture/平台技术架构.md
3. docs/product/AI测试平台PRD.md
4. docs/product/AI测试平台模块功能逻辑确认.md
5. 当前代码中与任务相关的 backend/ 和 frontend/ 模块

执行要求：
- 按垂直切片完成，覆盖数据模型、API、Service、前端页面、状态流转和必要测试。
- 遵守 Router -> Service -> Harness -> Runner -> Report 的边界。
- AI 输出必须经过 Skill / Prompt / Evaluator / 人工确认链路。
- 报告、日志、AI 输入和 RAG 入库必须经过脱敏。
- 不要修改与任务无关的模块。
- 完成后运行相关测试或提供可复现验证步骤。

输出要求：
- 总结实现内容。
- 列出修改文件。
- 说明验证方式和结果。
- 说明未完成项或需要人工确认的事项。
```

## 7. 开发记录

### 2026-05-19 需求中心与 Case 中心页面重构 TDD 切片

- 触发原因：前两轮被反馈“未在设计文档体现、未真正按需求文档重构页面”，本轮按 PRD 和模块功能逻辑确认重新收敛页面可见范围。
- 本轮可验收行为：
 - 需求中心作为 模块展示层，呈现“需求资产工作台”，包含需求关系树、需求文档列表、原文预览、解析与入库门禁说明，并明确检查未通过不得生成 case、AI 草稿需人工确认。
 - Case 中心作为 模块展示层，呈现“Case 资产工作台”，包含可信资产边界、正式 case 列表、来源追溯、人工确认记录、覆盖信息和最近执行摘要。
 - 左侧导航只展示已实现 / 可验证入口：首页 / 质量驾驶舱、需求中心、Case 中心；接口中心、移动端执行中心、执行中心、报告中心、AI 能力中心、系统设置、治理类入口在 UI 导航层隐藏。
 - 已实现页面统一采用深色渐变头图、资产卡片和三栏工作台布局，避免继续停留在普通表格后台样式。
- RED 结果：
 - `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-requirements-page.mjs"` 失败于 `需求中心缺少可验收可见文案：需求资产工作台`。
 - `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-cases-page.mjs"` 失败于 `Case 中心缺少可验收可见文案：Case 资产工作台`。
 - `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-navigation.mjs"` 失败于测试资产中台仍展示未完成的 `接口中心`。
 - `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-page-style.mjs"` 失败于缺少新版工作台样式选择器 `.asset-hero`。
- GREEN / refactor 结果：
 - `frontend/src/modules/requirements/pages/RequirementsPage.vue` 改为需求资产工作台，保留现有文档加载、上传、解析结果、AI 草稿确认入口。
 - `frontend/src/modules/cases/pages/CasesPage.vue` 改为 Case 资产工作台，保留现有 case 列表、详情、编辑、保存入口。
 - `frontend/src/app/navigation.js` 只暴露首页 / 质量驾驶舱、需求中心、Case 中心；路由和规划代码未删除。
 - `frontend/src/styles.css` 增加工作台式深色头图、三栏布局和资产列表样式。
- 验证命令：
 - `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-requirements-page.mjs"`
 - `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-cases-page.mjs"`
 - `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-navigation.mjs"`
 - `node "/Users/binwu/Desktop/Ai_test_web/frontend/scripts/verify-page-style.mjs"`
 - `npm --prefix "/Users/binwu/Desktop/Ai_test_web/frontend" run build`
- 改动摘要：补充需求中心 / Case 中心页面重构、导航隐藏策略、新版页面样式、前端验证脚本，并更新任务拆分和设计文档。
- 剩余风险：本轮完成前端模块展示层和可见边界，不声明后端真实需求树 CRUD、完整 AI 门禁、case 版本快照、执行报告联动已完成；这些能力仍需按 T04/T05/T07/T08 剩余切片推进。

### 2026-05-19 Case 列表 500 与 CORS 误报修复 TDD 切片

- 触发原因：Case 中心页面访问 `GET /api/cases/` 时浏览器报 CORS blocked，同时后端实际返回 500。
- 根因说明：CORS 报错是连带现象；`.logs/backend.log` 显示 `ResponseValidationError`，历史数据中部分 case 的 `steps` / `request_data` 等 JSON 字段为 `NULL`，与 `TestCaseResponse` schema 不一致。
- 本轮可验收行为：
 - `GET /api/cases/` 在存在 `steps=NULL` 的历史数据时仍返回 200，且每条 item 的 `steps` 为数组而非 null。
 - `GET /api/cases/{id}` 同样归一化空 JSON 字段后返回 200。
 - 本地开发 CORS 明确允许 `http://localhost:5173` 与 `http://127.0.0.1:5173`，避免 `allow_credentials=True` 与 `allow_origins=["*"]` 组合隐患。
- RED 结果：
 - 新增 `backend/tests/test_case_center.py` 后，`GET /api/cases/` 与 `GET /api/cases/{id}` 均失败于 `ResponseValidationError: steps/request_data/... input: None`。
- GREEN / refactor 结果：
 - `backend/app/models/test_case.py` 的 `to_dict()` 归一化 `steps`、`request_data`、`request_headers`、`expected_body`、`expected_contains` 等空 JSON 字段。
 - `backend/app/services/case_service.py` 新增 `serialize_case()`，列表与详情统一走序列化出口。
 - `backend/app/routers/test_cases.py` 详情接口改为返回 `serialize_case()` 结果。
 - `backend/app/main.py` 本地 CORS 改为显式允许 Vite 开发源。
- 验证命令：
 - `python -m unittest backend.tests.test_case_center -v`
 - `python -m unittest discover -s backend/tests -v`
 - `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/cases/` → 200
- 改动摘要：修复 Case 列表/详情响应校验失败，消除前端 CORS 误报；`runtime.lastError: message port closed` 为浏览器扩展噪音，无需改应用代码。
- 剩余风险：数据库历史脏数据仅在 API 层归一化，未做一次性 migration 写回；create/update 路由若直接返回 ORM 对象仍可能受同类问题影响，后面可按需统一改为 `serialize_case()`。

### 2026-05-19 前端全量重建 TDD 切片

- 触发原因：用户要求删除旧前端并按专业平台风格重建，本轮完成需求中心、Case 中心、系统设置（另保留轻量首页）。
- 本轮可验收行为：
 - 删除旧 `frontend/src` 与 `frontend/dist`，重建 Vue 3 + Vite 前端，仅注册 4 个可见模块路由。
 - 左侧导航分组：质量工作台 / 测试资产中台 / 系统设置；未实现模块不出现在导航。
 - 首页展示健康检查与资产概览，并提供需求 / Case / 设置快捷入口。
 - 需求中心三栏页对接文档 API；Case 中心三栏页对接 case API；系统设置 Tab 页对接 settings API。
 - 视觉改为企业级浅色平台：深色 sidebar、浅灰背景、白底卡片、`workspace-layout`。
- RED 结果：
 - 更新 `verify-navigation.mjs` 期望 4 入口 + 系统设置分组。
 - 重写 `verify-page-style.mjs` 检查新 design tokens。
 - 新增 `verify-overview-page.mjs`、`verify-settings-page.mjs`；更新 requirements / cases 验证脚本。
- GREEN / refactor 结果：
 - 新建 `frontend/src/app/layout/AppShell.vue`、`styles/tokens.css`、`modules/{overview,requirements,cases,settings}`。
 - 删除 apis / executions / mobile / reports / aiWorkspace / governance 等旧模块代码。
- 验证命令：
 - `node frontend/scripts/verify-navigation.mjs`
 - `node frontend/scripts/verify-page-style.mjs`
 - `node frontend/scripts/verify-overview-page.mjs`
 - `node frontend/scripts/verify-requirements-page.mjs`
 - `node frontend/scripts/verify-cases-page.mjs`
 - `node frontend/scripts/verify-settings-page.mjs`
 - `npm --prefix frontend run build`
 - `python -m unittest discover -s backend/tests -v`
- 改动摘要：前端全量重建 + 四模块 API 联调 + 新验证脚本 + 设计 / 任务文档更新。
- 剩余风险：需求关系树仍为 category 占位；解析状态机、case 版本 / 废弃、审计日志 UI、环境 / Appium 配置页未在本轮宣称完成。

### 2026-05-19 任务 3 / 4 / 6 后端 + 前端 TDD 切片

- 触发原因：用户要求完成需求树 CRUD + 文档挂载、解析状态机 + 入库门禁、Case 版本 / 废弃。
- 本轮可验收行为：
 - 需求中心左侧为真实 `/api/requirements/tree` 关系树，支持域 / 模块 / 功能 / 版本节点 CRUD、按节点过滤文档、挂载、归档 / 回收站 / 恢复。
 - 需求中心右侧支持触发解析、确认入库、展示解析状态与结构化需求点；`stored` 前阻止 AI case 生成。
 - Case 中心展示 `current_version_no`、版本历史列表，支持废弃 case 并从正式列表隐藏。
- RED 结果：
 - `test_requirement_tree.py` 树 children 为空（relationship 未 eager load）。
 - `test_requirement_parse_gate.py` 失败于 `result.data`（Skill 返回 dict 非 dataclass）。
 - `test_requirement_center.py` 因入库门禁拦截 `generate_api_case_drafts`。
- GREEN / refactor 结果：
 - 新增 `requirement_tree_nodes`、`requirement_items`、`case_versions` 模型与服务 / 路由。
 - `RequirementDocService.trigger_parse` 修复 Skill 返回值处理；`list_tree` 改为内存组树。
 - 前端 `RequirementsPage.vue` / `CasesPage.vue` 对接新 API；验证脚本更新。
- 验证命令：
 - `python -m unittest discover -s backend/tests -v` → 14 passed
 - `node frontend/scripts/verify-requirements-page.mjs`
 - `node frontend/scripts/verify-cases-page.mjs`
 - `npm --prefix frontend run build`
- 改动摘要：任务 3 / 4 / 6 核心链路贯通；文档下载、影响提示占位、审计日志 UI、Appium 配置仍为剩余切片。

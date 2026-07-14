# AI 测试平台 PRD

版本：v2.0  
文档角色：唯一产品需求主文档  
整理方法：参考 `.agents/skills/prd-writing/SKILL.md`、`.agents/skills/to-prd/SKILL.md`、`.agents/third-party-skills/github-awesome-copilot-prd/skills/prd/SKILL.md`  
适用对象：产品、测试、测试开发、后端、前端、AI agent  
维护原则：一个功能模块的目标、用户、需求、验收、护栏、数据 / API / UI 影响全部放在同一节内，避免 AI 或研发跨章节猜测意图。

## 0. 文档使用方式

本文档是 AI 测试平台的产品需求唯一主文档。后续技术设计、任务拆分、代码实现、PRD 对齐检查和 bug 修复都应优先参考本文档。

`docs/product/AI测试平台模块功能逻辑确认.md` 只保留模块边界确认、索引和待确认事项，不再重复承载完整需求正文。

需求编号规则：

- `FR-HOME-*`：首页 / 质量驾驶舱。
- `FR-REQ-*`：需求中心。
- `FR-CASE-*`：Case 中心。
- `FR-API-*`：接口中心。
- `FR-MOB-*`：移动端执行中心。
- `FR-EXEC-*`：执行中心。
- `FR-REPORT-*`：报告中心。
- `FR-AI-*`：AI 能力中心。
- `FR-CHANGE-*`：变更中心。
- `FR-TODO-*`：待办中心。
- `FR-SET-*`：系统设置。
- `FR-BUG-*`：未来 Bug 中心。

所有验收标准必须能映射到功能需求编号。涉及 AI 输出、正式资产、质量结论、报告证据和变更生效的功能，必须明确人工确认边界和不可绕过规则。

## 1. Executive Summary

### 1.1 Problem Statement

当前测试工作的核心问题不是缺少某一个执行工具，而是需求、case、接口、移动端元素、执行任务、报告、AI 输出、变更记录和人工复核事项分散在不同环节。测试人员难以从需求追溯到 case，从 case 追溯到执行和报告，也难以在需求或接口变化后判断哪些 case 需要新增、修改、废弃或回归。

AI 能力如果只停留在单次问答或孤立生成，也无法成为可信的测试资产生产流程。平台必须让 AI 输出具备来源、上下文、门禁、评分、人工确认和反馈闭环，否则 AI 生成的 case、失败分析和风险摘要不能进入正式质量流程。

### 1.2 Proposed Solution

建设一个统一的 AI 测试平台，产品形态是“测试资产中台 + AI 能力中心 + 统一执行与报告闭环”。平台以需求事实源和 case 资产为核心，以接口执行、Android 自动化执行和报告证据链为执行底座，以 AI 解析、生成、评估、失败分析和变更影响分析作为效率增强能力。

平台完整主链路如下：

```text
需求文档 / 接口文档
 -> 上传、预览、挂载到需求树
 -> AI 解析、结构化需求点、业务规则、验收点和问题项
 -> 查询同业务域 / 模块 / 功能下的历史需求基线
 -> 生成新旧需求差异，识别新增、修改、删除、冲突、验收标准变化、接口契约变化、权限变化、流程变化和边界变化
 -> 冲突 / 缺失 / 模糊 / 逻辑漏洞 / 耦合需求检查
 -> 检查通过后入库落档
 -> 生成需求覆盖矩阵，识别已覆盖、部分覆盖、未覆盖、过期、重复、需更新和需废弃
 -> 生成 case 生成计划，明确新增、更新、废弃、保留和自动化候选
 -> 按计划生成测试 case / 接口 case / 移动端自动化 case 草稿
 -> AI / Evaluator 门禁检查
 -> 测试人员人工确认
 -> Case 中心形成正式测试资产
 -> 接口中心 / 移动端执行中心提供执行对象和执行上下文
 -> 执行中心统一任务状态、重试、取消、失败分类和处理建议
 -> 报告中心输出 HTML 报告和证据链
 -> 变更中心分析需求、接口、元素、App、bug 修复带来的影响
 -> 待办中心承接人工复核事项
```

新增核心闭环对象如下：

- `RequirementBaseline`：同业务域 / 模块 / 功能下经人工确认的当前有效需求事实基线，用于避免新文档只和自身比较。
- `RequirementDiff`：新旧需求之间的结构化差异事实，覆盖新增、修改、删除、冲突、验收标准变化、接口契约变化、权限变化、流程变化和边界变化。
- `CoverageMatrix`：需求点 / 差异与已有 case、新增草稿、执行结果、覆盖状态、缺口原因和建议动作之间的结构化映射。
- `CaseGenerationPlan`：生成 case 前的执行计划，决定功能 case、接口 case、自动化脚本 case 的生成范围，以及已有 case 的保留、更新、废弃、合并或新增。
- `AutomationCandidate`：自动化脚本 case 的可行性判断对象，记录来源 case、依赖资产、可行性等级、阻塞原因和推荐执行环境。

### 1.3 Success Criteria

以下目标值为产品假设，试运行后需要用真实基线校准：

- 需求文档入库到 AI case 草稿生成的平均耗时降低 50%。
- AI case 草稿采纳率达到 60% 以上，采纳包含直接接受和编辑后接受。
- AI case 字段完整率达到 95% 以上。
- 接口单 case 执行成功率达到 90% 以上，排除被测服务真实业务失败。
- Android 单 case 稳定率达到 80% 以上，排除 App 业务缺陷和设备离线。
- 报告可复盘率达到 95% 以上，报告必须包含关键输入、输出、断言、日志、截图或错误证据。
- 待办处理闭环率达到 90% 以上。
- 新需求覆盖率和历史需求回归覆盖率可被度量，并能追溯到覆盖矩阵和执行报告。
- AI 调用失败率低于 5%，并能按功能、模型和日期统计 token、耗时、失败原因和估算成本。

## 2. Product Principles

- 平台以“可追溯测试资产”为核心，而不是只做执行器、上传页或 AI 聊天页。
- 每个模块必须说明输入、处理、输出、失败处理和验收方式。
- 所有正式资产必须能追溯来源，例如需求原文、结构化需求点、接口定义、元素、AI 生成依据、人工确认记录或执行报告。
- 新需求必须先与历史需求基线形成差异事实，再进入覆盖矩阵和 case 生成计划。
- AI 只能辅助生成、分析和评估，不能绕过人工确认直接修改正式 case、需求事实源、质量结论或变更结果。
- 首页展示的指标和 AI 风险摘要必须能跳转到来源对象，不能只展示无法复核的自然语言结论。
- 报告中心是证据中心，必须能回答“当时执行了什么、输入是什么、输出是什么、哪个判断失败、证据在哪里”。
- 变更中心和待办中心是一级模块，分别承担影响分析和人工复核闭环。
- Bug 中心是未来完整模块，当前文档写清目标和边界，但当前实现不要求外部同步、页面和流程闭环。
- 基础权限当前只做系统设置中的配置占位，不要求所有业务模块完成真实鉴权。

## 3. Personas / Users

### 测试经理

关注版本质量、覆盖情况、执行趋势、失败风险、待处理事项和回归范围。需要通过首页、报告中心、变更中心和待办中心快速判断当前版本是否可继续推进。

### 功能测试工程师

关注需求是否可信、case 是否完整、AI 生成是否可用、失败报告是否能定位问题。需要从需求中心生成 case，在 Case 中心维护正式资产，并通过待办中心处理人工确认事项。

### 测试开发 / 自动化工程师

关注接口定义、接口 case、移动端 case、执行任务、设备和报告证据链。需要稳定的调试入口、可复用的接口与元素资产、清晰的执行失败分类和可回归的自动化资产。

### 产品经理 / 研发负责人

关注需求变更、接口变更、bug 修复对测试范围和版本质量的影响。需要看到需求检查结果、变更影响分析、风险摘要和回归建议。

### 平台管理员 / 维护者

关注模型、Prompt、Skill、Evaluator、RAG、Appium capability、环境、报告策略、脱敏和成本。需要确保配置可验证、密钥不泄露、AI 能力可治理。

## 4. Functional Modules

当前一级模块为 11 个：

1. 首页 / 质量驾驶舱。
2. 需求中心。
3. Case 中心。
4. 接口中心。
5. 移动端执行中心。
6. 执行中心。
7. 报告中心。
8. AI 能力中心。
9. 变更中心。
10. 待办中心。
11. 系统设置。

未来模块：Bug 中心。Bug 中心作为未来完整模块写入本 PRD，但当前开发不要求外部缺陷平台同步、独立页面和完整缺陷流转。

---

## 5. Module: 首页 / 质量驾驶舱

### 5.1 Intent

首页是测试团队进入平台后的质量判断入口。它不是普通统计看板，而是让测试经理和测试人员在一分钟内看到当前版本的测试资产规模、执行健康度、风险摘要和待办入口。

### 5.2 Problem

需求、case、接口、设备、执行任务、失败报告和 AI 待确认事项散落在各模块时，测试经理无法快速判断当前版本是否健康，测试人员也不知道当天最需要处理的质量事项是什么。

### 5.3 User Stories

- 作为测试经理，我想看到需求、case、接口、设备、今日执行、失败任务、通过率和趋势，以便快速判断版本测试状态。
- 作为测试人员，我想从首页进入 AI case 待确认、失败报告复核、设备异常和变更影响事项，以便减少跨页面查找成本。
- 作为测试经理，我想看到 AI 风险摘要的证据来源、置信度和触发原因，以便判断风险是否需要人工复核。

### 5.4 Functional Requirements

- `FR-HOME-001` 首页必须展示质量指标：需求总数、case 总数、接口总数、在线设备数、今日执行次数、失败任务数、整体通过率和最近质量趋势。
- `FR-HOME-002` 首页指标必须支持跳转到来源对象或来源列表，例如需求列表、case 列表、报告列表、执行任务列表或设备列表。
- `FR-HOME-003` 首页必须展示待办入口，至少覆盖 AI case 待确认、失败报告复核、元素失效、设备异常和变更影响。
- `FR-HOME-004` 首页可以展示 AI 风险摘要，但每条摘要必须包含证据来源、置信度、触发原因、关联对象和人工确认状态。
- `FR-HOME-005` 首页不得承接复杂待办流转，只提供聚合入口和风险导航；具体处理在待办中心或来源模块完成。
- `FR-HOME-006` 首页应支持按当前项目或模块上下文过滤指标，避免跨项目数据混杂。
- `FR-HOME-007` 首页必须展示需求覆盖闭环指标，至少包括未处理需求差异数、未覆盖需求点数、待确认生成计划数、自动化候选未落地数、高风险变更数、新需求覆盖率和历史回归通过率。

### 5.5 Acceptance Criteria

- `AC-HOME-001` Given 测试经理进入首页，When 页面加载完成，Then 能在一个页面看到 `FR-HOME-001` 中列出的核心质量指标。
- `AC-HOME-002` Given 用户点击任一首页指标，When 指标存在来源对象，Then 平台跳转到对应来源列表并带入筛选条件。
- `AC-HOME-003` Given 首页展示 AI 风险摘要，When 用户查看风险详情，Then 必须看到证据来源、置信度、触发原因、关联对象和人工确认状态。
- `AC-HOME-004` Given 存在 AI case 待确认或失败报告复核事项，When 用户查看首页待办入口，Then 首页展示数量并能跳转到待办中心。
- `AC-HOME-005` Given 当前版本存在需求差异、覆盖缺口或生成计划待确认，When 测试经理进入首页，Then 首页展示对应数量和趋势，并能跳转到需求中心覆盖矩阵、Case 生成计划或变更中心。对应 `FR-HOME-007`。

### 5.6 Guardrails

- 首页不能展示无法追溯来源的 AI 风险结论。
- 首页不能替代待办中心完成复杂处理流转。
- 首页自动加载成功不弹成功提示；只有用户主动操作后的保存、刷新、同步、执行等动作才使用统一反馈。

### 5.7 Data / API / UI Implications

- 数据需要聚合需求、case、接口、设备、执行任务、报告、AI 评估、待办、RequirementDiff、CoverageMatrix、CaseGenerationPlan、AutomationCandidate、ChangeRecord 和 RegressionRecommendation。
- API 需要提供首页摘要接口、趋势接口、风险摘要接口、待办摘要接口、覆盖缺口摘要接口和生成计划摘要接口。
- UI 应采用质量驾驶舱布局：顶部核心指标，中部风险摘要、覆盖缺口和趋势，下方待办入口、生成计划入口与最近执行。

### 5.8 Open Questions

- 首页质量指标的默认排序、展示密度和趋势时间窗口需要在原型阶段确认。

---

## 6. Module: 需求中心

### 6.1 Intent

需求中心是平台测试资产链路的事实源。它必须把原始文档、结构化解析结果、人工确认状态、需求树路径和检查结果管理在一起，保证只有可信需求才能生成 case。

### 6.2 Problem

如果需求文档、接口文档、变更说明和验收标准未经解析、历史对比和逻辑检查就进入 case 生成，会把模糊、缺失、冲突和过期信息放大成错误 case，导致后续执行和报告都不可信。

### 6.3 User Stories

- 作为产品经理，我想上传需求文档、接口文档、变更说明和验收标准，并在入库前看到解析和逻辑检查结果，以便问题需求不会进入测试资产链路。
- 作为测试人员，我想看到文档状态、原文预览、需求树路径、结构化需求点和检查问题，以便判断是否可以生成 case。
- 作为产品经理 / 研发负责人，我想确认冲突、缺失和模糊点，以便需求含义在进入需求树前被澄清。
- 作为测试经理，我想知道哪些需求已经转化为 case，哪些需求仍停留在待确认或检查失败状态，以便管理测试设计进度。
- 作为产品经理，我想在平台内直接处理 AI 检查出来的待修改、待优化和待确认问题项，而不是反复本地修改后重新上传，以便需求修正和入库闭环都沉淀在平台内。

### 6.4 Functional Requirements

- `FR-REQ-001` 需求中心必须支持上传需求文档、接口文档、变更说明、验收标准和测试需求说明。
- `FR-REQ-002` 文档上传必须保存原始文件、文件名、类型、上传人、上传时间、文件指纹、项目和模块归属。
- `FR-REQ-003` 文档必须挂载到需求树，需求树层级为业务域 -> 模块 -> 功能 -> 需求版本 -> 验收点。
- `FR-REQ-004` 需求中心必须支持原文预览和下载；解析失败时应允许用户查看原文和错误原因。
- `FR-REQ-005` 文档必须具备状态流转：未解析、解析中、待确认、检查未通过、已入库、已归档、已删除。
- `FR-REQ-006` 平台必须从文档中提取结构化需求点、业务规则、风险点、验收点和原文片段。
- `FR-REQ-007` 平台必须执行同一模块历史需求对比，并展示新增、修改、删除、冲突和模糊项。
- `FR-REQ-008` 平台必须支持 AI 识别业务耦合需求，并将耦合检查结果展示给用户。
- `FR-REQ-009` 检查未通过的文档不得生成 AI case 草稿、不得进入正式需求事实源。
- `FR-REQ-010` 检查通过并经人工确认后，文档和结构化需求点才能入库落档并成为 case 生成输入。
- `FR-REQ-011` 需求中心必须展示需求与 case、接口、模块、变更记录之间的关联关系。
- `FR-REQ-012` 删除或归档需求文档前，平台必须展示影响提示，至少包括关联需求点、case、知识库片段和变更记录数量。
- `FR-REQ-013` 需求中心必须将 AI 检查出的冲突、缺失、模糊、逻辑漏洞、格式问题和优化建议沉淀为文档问题项，并关联原文位置、原文片段、问题类型、严重级别、AI 判断原因、建议处理方式和阻断状态。
- `FR-REQ-014` 文档问题项类型至少包括待确认、待修改、待优化、误报 / 已忽略、已修改、已解决；严重级别至少包括阻断、高、中、低。
- `FR-REQ-015` 用户必须能在平台内对文档问题项执行处理动作：手动修改、采纳 AI 修改建议、忽略并填写原因、转人工确认、重新检查。
- `FR-REQ-016` 平台内修改不得直接覆盖原始上传文件，必须生成文档修订版，并保留原始文档、修订版、修改人、修改时间、修改前后差异和关联问题项。
- `FR-REQ-017` 忽略问题项必须填写忽略原因并记录操作者、时间、问题类型、严重级别和影响范围；忽略不得删除问题项，只能改变其处理状态。
- `FR-REQ-018` 阻断级待修改、待确认或冲突问题未被解决、确认或具备风险留痕前，文档不得入库落档，不得生成 case 草稿。
- `FR-REQ-019` 对待优化问题，用户可以选择忽略；忽略后不阻断当前文档入库，但必须在文档详情和审计记录中保留。
- `FR-REQ-020` case 生成必须基于检查通过后的修订版文档或人工确认后的结构化需求点，不得基于仍存在阻断问题的原始文档生成。
- `FR-REQ-021` 接口文档解析出的 `need_review` 结构化需求点必须同步沉淀为可处理的文档问题项，而不能只停留在“结构化需求点 -> 待确认”标签中；用户必须能在同一套“待优化 / 需人工关注”问题项卡片中完成修改、采纳 AI 建议、忽略留痕、转人工确认、标记解决和重新检查。
- `FR-REQ-022` 需求中心必须支持 `RequirementBaseline` 需求基线。每次文档和结构化需求点经人工确认入库后，系统必须按业务域、模块、功能、需求版本和验收点生成或更新当前有效基线。
- `FR-REQ-023` 新需求文档、接口文档、变更说明或验收标准进入 case 生成前，必须与同业务域 / 模块 / 功能下最近一个有效 `RequirementBaseline` 做对比；若没有历史基线，系统必须明确标记为“首次基线”并要求人工确认。
- `FR-REQ-024` 需求中心必须支持 `RequirementDiff` 差异对象，记录新旧需求的 added、modified、deleted、conflict、unchanged，以及验收标准变化、接口契约变化、权限变化、流程变化和边界条件变化。
- `FR-REQ-025` `RequirementDiff` 必须包含差异摘要、风险等级、影响范围、证据片段、关联旧需求点、关联新需求点和是否阻断入库 / 生成 case。
- `FR-REQ-026` 差异分析中的冲突、删除、验收标准变化、接口契约变化、权限变化、流程变化和高风险边界变化必须同步沉淀为 `RequirementIssue` 或进入变更中心，不得只作为自然语言摘要展示。
- `FR-REQ-027` 需求中心必须支持 `CoverageMatrix` 覆盖矩阵，记录每个结构化需求点或需求差异与已有 case、新增草稿、执行结果、覆盖状态、缺口原因和建议动作之间的关系。
- `FR-REQ-028` 覆盖状态必须至少包括 covered、partial_covered、not_covered、outdated、duplicated、need_update、need_deprecate。
- `FR-REQ-029` 生成 case 前必须先生成覆盖矩阵；没有覆盖矩阵或覆盖矩阵存在未处理阻断缺口时，不允许批量生成或批量接受 AI case 草稿。
- `FR-REQ-030` 覆盖矩阵必须区分历史需求回归覆盖和新需求新增覆盖，避免新 case 只覆盖当前文档而遗漏历史需求。
- `FR-REQ-031` 需求中心必须向 Case 中心输出 `CaseGenerationPlan` 所需的上下文，包括当前文档、修订版、历史基线、差异列表、覆盖矩阵、相关接口定义、已有 case、废弃 case、负样本和变更记录。
- `FR-REQ-032` 删除、归档或替换需求文档前，影响提示必须包含该文档参与的基线、差异、覆盖矩阵、生成计划、case、接口、变更和待办数量。

### 6.5 Acceptance Criteria

- `AC-REQ-001` Given 用户上传支持格式文档，When 上传完成，Then 平台保存文件元信息并展示在需求树对应节点下。对应 `FR-REQ-001`、`FR-REQ-002`、`FR-REQ-003`。
- `AC-REQ-002` Given 文档处于未解析状态，When 用户触发解析，Then 平台进入解析中状态并最终展示结构化需求点、原文片段和解析警告。对应 `FR-REQ-005`、`FR-REQ-006`。
- `AC-REQ-003` Given 文档存在冲突、缺失或模糊项，When 用户尝试生成 case，Then 平台阻止生成并展示检查失败原因。对应 `FR-REQ-007`、`FR-REQ-008`、`FR-REQ-009`。
- `AC-REQ-004` Given 产品经理确认检查通过，When 文档入库，Then 结构化需求点成为 case 生成输入，并可在 Case 中心追溯来源。对应 `FR-REQ-010`、`FR-REQ-011`。
- `AC-REQ-005` Given 用户归档或删除文档，When 文档存在下游关联，Then 平台展示影响提示并要求二次确认。对应 `FR-REQ-012`。
- `AC-REQ-006` Given AI 检查发现待修改、待优化或待确认问题，When 用户查看文档详情，Then 平台按原文位置展示问题项、严重级别、AI 判断原因、建议处理方式和是否阻断入库。对应 `FR-REQ-013`、`FR-REQ-014`。
- `AC-REQ-007` Given 用户在平台内修改问题项关联的文档片段，When 保存修改，Then 平台生成文档修订版并记录修改前后差异、修改人、修改时间和关联问题项。对应 `FR-REQ-015`、`FR-REQ-016`。
- `AC-REQ-008` Given 用户选择忽略问题项，When 提交忽略，Then 平台要求填写忽略原因并记录审计信息；若该问题为阻断级问题，Then 平台必须展示带风险处理提示并阻止无留痕绕过。对应 `FR-REQ-017`、`FR-REQ-018`、`FR-REQ-019`。
- `AC-REQ-009` Given 文档仍存在未解决的阻断级问题，When 用户尝试入库或生成 case，Then 平台阻止操作并展示未处理问题清单。对应 `FR-REQ-018`、`FR-REQ-020`。
- `AC-REQ-010` Given 用户处理完问题项并触发重新检查，When 检查通过，Then 平台将问题项更新为已解决，并允许基于修订版文档进入入库和 case 生成流程。对应 `FR-REQ-015`、`FR-REQ-020`。
- `AC-REQ-011` Given 接口文档解析出的接口点缺少推荐断言、响应字段或验收口径，When 该结构化需求点被标记为 `need_review`，Then 平台必须同步生成关联 `RequirementItem` 的 `待确认` 问题项，并展示原文位置、接口 method/path/description、复核原因和建议处理方式；用户应在问题项卡片中完成复核处理，而不是在结构化需求点列表中面对无动作的静态标签。对应 `FR-REQ-013`、`FR-REQ-014`、`FR-REQ-015`、`FR-REQ-021`。
- `AC-REQ-012` Given 文档经人工确认入库，When 入库完成，Then 平台生成或更新对应业务域 / 模块 / 功能下的 `RequirementBaseline`，并能在文档详情中查看基线版本和包含的需求点。对应 `FR-REQ-022`。
- `AC-REQ-013` Given 用户上传同模块新文档，When 触发解析和检查，Then 平台自动与最近有效基线对比并展示 `RequirementDiff` 列表，包括新增、修改、删除、冲突和验收标准变化。对应 `FR-REQ-023`、`FR-REQ-024`、`FR-REQ-025`。
- `AC-REQ-014` Given 差异分析发现高风险冲突或删除历史需求，When 用户尝试入库或生成 case，Then 平台必须阻止操作并要求处理对应问题项或进入变更确认。对应 `FR-REQ-026`。
- `AC-REQ-015` Given 文档检查通过并准备生成 case，When 用户进入生成前检查，Then 平台展示 `CoverageMatrix`，列出每个需求点和差异的覆盖状态、已有 case、新增草稿、缺口原因和建议动作。对应 `FR-REQ-027`、`FR-REQ-028`、`FR-REQ-030`。
- `AC-REQ-016` Given 覆盖矩阵不存在或仍有未处理阻断缺口，When 用户尝试批量生成或批量接受 AI case，Then 平台阻止操作并展示缺口清单。对应 `FR-REQ-029`、`FR-REQ-031`。

### 6.6 Guardrails

- 检查未通过的需求文档或接口文档不得生成 case 草稿。
- AI 解析结果必须展示原文依据，不得只给结构化结论。
- 入库落档必须有人工确认边界。
- 文档修订必须保留原始文档，不得用修订版静默覆盖原始上传文件。
- 忽略不是删除问题项；所有忽略必须有原因、操作者和时间记录。
- 阻断级问题不得通过前端隐藏按钮、直接 API 调用或批量操作绕过入库和 case 生成门禁。
- 接口文档中的 `need_review` 不得只有展示标签；任何需要用户判断的接口解析结果都必须有可处理的问题项、来源依据和复核动作入口。
- 新需求不得只与当前文档自身比较；生成 case 前必须与同业务域 / 模块 / 功能的历史需求基线比较。
- 没有 `RequirementDiff` 或差异分析失败时，不允许批量生成 AI case。
- 没有 `CoverageMatrix` 或覆盖矩阵存在未处理阻断缺口时，不允许批量接受 AI case 草稿。
- 覆盖矩阵不能只展示自然语言总结，必须展示需求点、差异、case 和建议动作的结构化关系。
- 删除、归档和覆盖必须二次确认并保留操作记录。

### 6.7 Data / API / UI Implications

- 数据对象包括 RequirementDocument、RequirementNode、RequirementItem、RequirementCheckResult、RequirementIssue、RequirementRevision、RequirementIssueAction、RequirementVersion、RequirementRelation、RequirementBaseline、RequirementDiff、CoverageMatrix、CoverageMatrixItem。
- `RequirementItem.need_review=true` 的接口文档解析结果必须能映射到 `RequirementIssue.requirement_item_id`，并保留 `source_location`、`source_excerpt`、`suggestion` 和 `ai_reason`。
- `RequirementBaseline` 需要记录业务域、模块、功能、版本、文档集合、需求点集合、确认人、确认时间和状态。
- `RequirementDiff` 需要记录旧需求点、新需求点、差异类型、风险等级、影响范围、证据和阻断状态。
- `CoverageMatrix` 需要记录需求点 / 差异、关联 case、覆盖状态、缺口原因、建议动作、执行结果和人工确认状态。
- API 需要覆盖上传、预览、下载、解析、确认、归档、恢复、删除、树节点管理、影响分析、问题项列表、问题项修改、AI 修改建议、忽略、转人工确认、重新检查、修订版管理、基线查询、基线生成、差异分析、覆盖矩阵生成、覆盖缺口确认和生成计划上下文输出。
- UI 建议三栏工作台：左侧需求树，中间文档列表和问题项列表，右侧原文预览 / 解析结果 / 检查结果 / 问题项处理 / 修订版对比 / 入库确认。
- “结构化需求点 -> 待确认”区域只能作为解析结果说明和定位入口；真实复核动作必须集中到“待优化 / 需人工关注”问题项卡片，避免同一事项出现两个处理入口或无处理入口。
- 文档详情页应提供“原文 / 问题项 / 修订版 / 历史基线 / 差异分析 / 覆盖矩阵 / 检查结果”的联动视图，点击问题项或覆盖缺口可定位到原文片段、修订片段、历史需求点和关联 case。

### 6.8 AI Evaluation Strategy

- 需求解析需要记录输入文档、模型、Prompt / Skill 版本、结构化输出、原文片段映射和解析警告。
- 冲突 / 缺失 / 模糊检查需要给出证据来源和建议处理动作。
- AI 修改建议必须展示建议变更片段、修改理由、影响范围和置信度；用户确认前不得直接写入修订版。
- 需求基线对比、差异分析和覆盖矩阵生成需要记录输入基线、当前文档、RAG 召回、已有 case、Prompt / Skill 版本、模型、评估结果和人工确认结果。
- 覆盖缺口、误判差异、被用户忽略的差异和修改后的需求项应进入 AI 能力中心统计，用于评估历史对比准确率和覆盖建议准确率。
- 用户对问题项的修改、忽略、拒绝 AI 修改建议和重新检查结果应进入 AI 能力中心统计，用于评估问题识别准确率和建议采纳率。
- 需求解析采纳率、解析字段完整率和人工修改率应进入 AI 能力中心统计。

### 6.9 Open Questions

- 需求树页面的最佳交互和默认展开层级需要原型确认。
- 解析失败时是否允许用户手动粘贴文本作为新的原始输入并重新触发真实 AI 解析需要确认；不得将手动输入包装成 AI 解析降级结果。

---

## 7. Module: Case 中心

### 7.1 Intent

Case 中心是测试资产中心。它统一管理功能 case、接口 case、移动端 case、AI case 草稿、场景 / 编排 case，以及 case 的来源、状态、版本、可信分层、执行摘要和回归价值。

### 7.2 Problem

如果不同类型 case 各自拥有不同格式和状态，AI 生成、人工维护、接口执行、移动端执行和报告回溯会割裂。测试经理无法判断哪些 case 是草稿、正式资产、已验证资产或高价值回归资产。

### 7.3 User Stories

- 作为功能测试工程师，我想创建、编辑、复制、废弃和归档 case，以便维护正式测试资产。
- 作为测试人员，我想确认、编辑后接受、拒绝或合并 AI case 草稿，以便 AI 输出只有经过人工确认后进入正式 case 库。
- 作为测试开发工程师，我想维护接口 case 和移动端 case 的步骤、断言、变量、元素和执行配置，以便 case 可以被执行中心运行。
- 作为测试经理，我想看到 case 的来源、状态、版本、最近执行结果、健康度和回归价值，以便判断它能否作为可信回归资产。

### 7.4 Functional Requirements

- `FR-CASE-001` Case 中心必须支持统一 case 模型，至少包含标题、类型、状态、项目、模块、来源、步骤、断言、重要性、标签、创建人和更新时间。
- `FR-CASE-002` case 类型必须包含功能 case、接口 case、移动端自动化 case、AI case 草稿、场景 / 编排 case。
- `FR-CASE-003` case 主状态必须覆盖草稿、待确认、正式资产、已验证资产、高价值资产、已废弃、已归档。
- `FR-CASE-004` AI case 草稿必须先进入待确认队列，支持接受、编辑后接受、拒绝和合并。
- `FR-CASE-005` **AI case 草稿拒绝与负样本闭环沉淀机制**：
  - `FR-CASE-005.1` **拒绝操作与结构化原因采集**：测试人员在待确认队列中拒绝（Reject）某条 `AiCaseDraft` 时，系统必须强制弹出“拒绝原因采集弹窗”并收集结构化字段：`rejection_category`（逻辑错乱/步骤错乱 `LOGIC_ERROR`、缺失关键断言 `MISSING_ASSERTION`、超出需求范围/过度生成 `OUT_OF_SCOPE`、与已有用例重复 `DUPLICATE`、幻觉/伪造字段元素 `HALLUCINATION`、格式不符合规范 `FORMAT_ERROR`、其他 `OTHER`）以及 `user_feedback_comment`（详细拒绝理由与改进建议，字数必填 >= 10字）。
  - `FR-CASE-005.2` **负样本脱敏与 RAG 入库（Feedback Sinking）**：点击确认拒绝后，系统启动异步任务调用 `FeedbackSampleSinkingService`。该服务先调用 `MaskingService` 对原始输入需求与草稿中的敏感字段进行安全脱敏，然后组合为标准负样本对象 `AiFeedbackSample` 存储于关系型数据库。同时，将其格式化为“原始需求文本 + 错误用例结构 + 拒绝类别与详细用户反馈”的文本片段，写入 RAG 向量数据库的 `ai_feedback_samples` 集合，标记元数据 `type=negative_sample`, `module_id=xxx`，使其具备即时语义检索能力。
  - `FR-CASE-005.3` **闭环消费（Few-Shot Negative Learning）**：在下一次针对相同或相似模块进行 AI case 生成（`CaseGenerateSkill`）时，生成引擎在加载正向少样本（Few-Shot）的同时，必须先调用 `RagRetrieveSkill` 自动检索与当前需求语义相似度高（Cosine Similarity > 0.70）的历史被拒负样本记录（最多 3 条）。在最终的生成 Prompt 中动态注入一个独立块：`### 过去被拒绝的错误用例模式（请务必避免）`。以此作为硬性负向 Few-Shot 约束，强制大语言模型规避逻辑错误、重复步骤或幻觉元素。
  - `FR-CASE-005.4` **闭环消费（门禁评估的相似度拦截）**：在 AI 新生成用例提交给测试人员前，`PhoenixEvaluateSkill` 与门禁引擎需自动检索相似负样本。若新生成用例与被拒用例的步骤相似度（编辑距离或 Token 余弦相似度）超过 0.85，且未根据反馈意见修正对应的错误点，门禁系统必须直接将其标记为 `check_failed`，状态归类为 `high_risk_duplicate_of_rejected_pattern`，拦截在待确认队列之外并进入待办复核。
- `FR-CASE-006` 接受 AI case 后必须写入正式 case 和 case steps，并保留 AI 原始输出、人工编辑版本、确认人和确认时间。
- `FR-CASE-007` 正式 case 详情必须展示来源需求点、原文片段、接口、元素、变更来源、AI 生成依据、人工确认记录和最近执行结果。
- `FR-CASE-008` 人工新增 case 必须选择项目和模块；如果来自需求补充，应绑定对应需求点或原文片段。
- `FR-CASE-009` 对已有 case 的文案小改可以直接保存；步骤、断言、来源、接口或元素变更必须重新确认或验证。
- `FR-CASE-010` Case 中心必须支持版本快照，关键字段修改前自动保留历史版本。
- `FR-CASE-011` **Case 废弃、归档与反向防错机制**：
  - `FR-CASE-011.1` **废弃分类与原因采集**：测试人员在 Case 中心发起废弃（Deprecate）一个正式 `TestCase` 时，系统必须强制采集废弃元数据，包括 `deprecation_category`（业务功能已下线 `FEATURE_REMOVED`、与其他用例合并 `REDUNDANT`、不稳定性高误报 `FLAKY`、移动端元素/接口变更无法维护 `STALE_LOCATOR`、其他 `OTHER`）和 `user_comment`（详细废弃说明）。
  - `FR-CASE-011.2` **版本关联与链路溯源**：如果废弃因需求或接口变更触发，系统必须强制关联具体的变更记录 ID（来自 `FR-CHANGE-001`）；若是被新用例取代，则必须关联新用例 ID `replaced_by_case_id`，在关系网中保留其作为历史资产的演进状态。
  - `FR-CASE-011.3` **归档流转与执行中心物理隔离**：废弃 case 的物理数据不删除，仅其 `is_active` 被置为 `0`，状态流转为 `已废弃` 并转移至“已归档资产视图”。**执行中心（Module: 执行中心）**在运行单 case、场景流、回归集或生成回归推荐列表时，必须 100% 自动过滤处于 `已废弃` 状态的 case，确保其不参与执行或污染任何报告。
  - `FR-CASE-011.4` **废弃资产反向引导**：变更中心（Module: 变更中心）在为后续版本生成推荐用例或自适应修改草稿时，需调用 RAG 索引对本模块的历史废弃案例进行匹配。若检测到推荐步骤与因 `FLAKY` 或 `STALE_LOCATOR` 废弃的代码具有高度重合风险，必须在前台触发显著预警提示，指导设计人员规避“已知的历史技术债用例模式”。
- `FR-CASE-012` Case 中心必须支持重要性 / 模块完整交付标记，用作当前回归依据。
- `FR-CASE-013` Case 中心必须支持 case 健康度，记录长期未执行、重复、缺断言、flaky、元素失效和最近失败摘要。
- `FR-CASE-014` 系统不得自动删除 case，只能建议废弃、归档、合并或修复。
- `FR-CASE-015` Case 中心必须支持 `CaseGenerationPlan`。所有由需求或接口文档触发的 AI case 生成必须先生成计划，计划中必须声明来源文档、历史基线、需求差异、覆盖矩阵、目标 case 类型、已有 case 建议动作和生成原因。
- `FR-CASE-016` `CaseGenerationPlan` 的目标 case 类型至少包括 functional_case、api_case、automation_script_case；每类 case 必须使用对应事实源和上下文，不得用同一套自然语言结果直接生成全部类型。
- `FR-CASE-017` 对已有 case 的建议动作必须至少包括 keep、update、deprecate、add_new、merge_candidate；update、deprecate 和 merge_candidate 必须进入人工确认或待办，不得自动修改正式资产。
- `FR-CASE-018` 功能 case 草稿必须绑定 `RequirementItem` 和 / 或 `RequirementDiff`，并标明覆盖类型：主流程、异常、边界、权限、状态流转或历史回归。
- `FR-CASE-019` 接口 case 草稿必须绑定接口中心已确认接口定义、接口文档解析结果或接口差异；如果接口定义未确认，接口 case 只能处于候选草稿状态，不得进入可执行正式资产。
- `FR-CASE-020` 自动化脚本 case 必须先经过 `AutomationCandidate` 可行性判断，且必须绑定功能 case 或接口 case；不得孤立生成不关联业务 case 的自动化脚本。
- `FR-CASE-021` `AutomationCandidate` 必须记录自动化类型、可行性等级、阻塞原因、所需资产、依赖接口、依赖元素、测试数据和推荐执行环境。
- `FR-CASE-022` Case 中心必须消费 `CoverageMatrix`，在 case 列表和详情中展示该 case 覆盖的需求点、差异、覆盖状态、生成计划、执行结果和缺口状态。
- `FR-CASE-023` 批量接受 AI case 草稿前，系统必须检查关联覆盖矩阵和生成计划；若计划未确认、覆盖矩阵缺失或存在未处理阻断缺口，则必须阻止批量接受。
- `FR-CASE-024` AI 生成的功能 case、接口 case 和自动化脚本 case 草稿必须符合项目内 `test_case` skill 的统一字段契约；基础必填字段至少包括 `case_no`、`title`、`requirement_ref`、`precondition`、`steps`、`expected_result`、`importance`、`test_type`，可选字段包括 `test_data`、`remarks`。
- `FR-CASE-025` 平台必须支持用户对 AI case 草稿进行人工修改；人工修改后必须重新执行字段契约校验、来源绑定校验、覆盖矩阵校验和对应类型的执行依赖校验。
- `FR-CASE-026` 平台允许批量同意 AI case 草稿，但批量同意仅适用于已通过门禁的草稿；批量同意必须记录确认人、确认时间、批次号、原始 AI 输出、人工修改版本和门禁结果。
- `FR-CASE-027` 批量编辑 AI case 草稿不得作为默认主路径；若后续支持，必须限制为标签、重要性、归属模块、备注等低风险字段，步骤、断言、接口请求、元素依赖和预期结果仍需逐条复核或重新门禁。

### 7.5 Acceptance Criteria

- `AC-CASE-001` Given 用户创建 case，When 保存成功，Then case 出现 Case 中心并具备项目、模块、类型、状态和步骤信息。对应 `FR-CASE-001`、`FR-CASE-002`。
- `AC-CASE-002` Given AI 生成 case 草稿，When 草稿缺少必填字段，Then 平台阻止同步为正式 case 并展示缺失项。对应 `FR-CASE-004`。
- `AC-CASE-003` Given 测试人员接受 AI case 草稿，When 保存完成，Then 正式 case 保留 AI 原始输出、人工确认人、确认时间和来源需求点。对应 `FR-CASE-006`、`FR-CASE-007`。
- `AC-CASE-004` Given 用户修改 case 步骤或断言，When 保存完成，Then 平台生成版本快照并将 case 标记为需要重新确认或验证。对应 `FR-CASE-009`、`FR-CASE-010`。
- `AC-CASE-005` Given 用户废弃 case，When 用户确认输入废弃元数据，Then 系统将其 `is_active` 置 0 且状态标为 `已废弃`，将其转移至归档资产视图，并强制限制执行中心在运行所有任务时过滤此类 case。对应 `FR-CASE-011.1`、`FR-CASE-011.2`、`FR-CASE-011.3`。
- `AC-CASE-006` Given case 存在多次失败和重跑通过记录，When 查看 case 健康度，Then 平台按规则识别 flaky 风险并展示证据。对应 `FR-CASE-013`。
- `AC-CASE-007` Given 测试人员拒绝了某条 AI case 草稿，When 点击确认并输入了结构化的拒绝大类与详细意见，Then 系统将草稿置为 `已拒绝` 状态并转存入 `AiFeedbackSample` 库中，且同步脱敏并写入 RAG 负样本向量集中。对应 `FR-CASE-005.1`、`FR-CASE-005.2`。
- `AC-CASE-008` Given 某模块存在历史被拒绝的负样本，When 用户再次请求 AI 生成，Then 生成 Prompt 必须包含对应的 `### 过去被拒绝的错误用例模式` 少样本负向约束段落，且召回的负样本与新生成草稿如果相似度超过 0.85，门禁将直接拦截该草稿进入 `check_failed` 状态。对应 `FR-CASE-005.3`、`FR-CASE-005.4`。
- `AC-CASE-009` Given 变更推荐算法进行自适应修改推荐，When 推荐步骤与已因 `FLAKY` 或 `STALE_LOCATOR` 废弃的历史代码模式重合，Then 平台在前台页面上触发醒目的规避警告。对应 `FR-CASE-011.4`。
- `AC-CASE-010` Given 用户从已入库需求或接口文档生成 case，When 点击生成，Then 平台先展示 `CaseGenerationPlan`，包含来源基线、差异、覆盖矩阵、目标 case 类型和已有 case 建议动作。对应 `FR-CASE-015`、`FR-CASE-016`。
- `AC-CASE-011` Given 生成计划建议更新或废弃已有 case，When 用户未人工确认，Then 正式 case 不发生变化，只产生待确认草稿或待办。对应 `FR-CASE-017`。
- `AC-CASE-012` Given 用户生成接口 case，When 关联接口定义尚未确认，Then 接口 case 保持候选草稿状态，不能进入可执行正式资产。对应 `FR-CASE-019`。
- `AC-CASE-013` Given 用户生成自动化脚本 case，When 缺少绑定的功能 case / 接口 case 或必要接口 / 元素 / 测试数据资产，Then 平台阻止正式入库并展示 `AutomationCandidate` 的阻塞原因。对应 `FR-CASE-020`、`FR-CASE-021`。
- `AC-CASE-014` Given 用户查看正式 case 详情，When case 来源于生成计划，Then 详情展示覆盖的需求点、差异、覆盖状态、生成计划、人工确认记录和最近执行结果。对应 `FR-CASE-022`。
- `AC-CASE-015` Given 覆盖矩阵存在未处理阻断缺口，When 用户尝试批量接受 AI case 草稿，Then 平台阻止接受并展示缺口清单。对应 `FR-CASE-023`。
- `AC-CASE-016` Given AI 生成任意类型 case 草稿，When 草稿缺少 `test_case` skill 规定的必填字段或步骤少于契约要求，Then 平台将草稿标记为 `check_failed` 并展示缺失字段。对应 `FR-CASE-024`。
- `AC-CASE-017` Given 测试人员编辑 AI case 草稿，When 保存编辑内容，Then 平台重新执行字段契约、来源、覆盖和类型依赖校验，通过后才允许进入待确认或批量同意队列。对应 `FR-CASE-025`。
- `AC-CASE-018` Given 用户批量同意 AI case 草稿，When 批次内存在未通过门禁、未绑定生成计划、覆盖矩阵缺口未处理、接口未确认或自动化依赖缺失的草稿，Then 平台阻止整批或逐条跳过失败项，并展示失败原因清单。对应 `FR-CASE-026`、`FR-CASE-027`。

### 7.6 Guardrails

- AI case 草稿不得绕过门禁检查和人工确认进入正式 case 库。
- AI case 草稿必须来自 `CaseGenerationPlan`，不得绕过生成计划直接从文档进入待确认队列。
- case 删除、废弃、归档和关键字段修改必须保留审计或版本记录。
- 系统不得自动删除正式 case。
- 影响执行语义的修改必须重新确认或验证。
- **草稿拒绝门禁**：拒绝动作必须强制要求输入拒绝分类与详细文本理由，不合规输入（如小于 10 字）应阻止提交。
- 自动化脚本 case 不能孤立存在，必须绑定功能 case 或接口 case。
- 接口 case 必须绑定接口定义、接口文档解析结果或接口差异；未确认接口定义不得生成可执行正式接口 case。
- 批量接受 AI 草稿不得绕过覆盖矩阵和生成计划门禁。
- AI case 草稿不得绕过 `test_case` skill 字段契约校验；缺失必填字段、步骤不可执行或预期结果不可验证时不得进入正式资产。
- 批量同意只能处理已通过门禁的草稿；不得用批量同意掩盖字段缺失、接口未确认、自动化资产缺失或覆盖缺口。

### 7.7 Data / API / UI Implications

- **数据对象**：包括 TestCase、CaseStep、CaseVersion、AiCaseDraft、CaseSourceRelation、CaseHealthSignal、CaseReviewRecord、AiFeedbackSample、CaseGenerationPlan、CaseGenerationPlanItem、AutomationCandidate（负样本表：增加 `rejection_category`，`user_feedback_comment`，`prompt_version`，`source_requirement` 字段）。
- `TestCase` 与 `AiCaseDraft` 需要实现与 `test_case` skill 对齐的基础字段契约：`case_no`、`title`、`requirement_ref`、`precondition`、`steps`、`expected_result`、`importance`、`test_type`、`test_data`、`remarks`。
- `CaseGenerationPlan` 需要记录来源文档、基线、差异、覆盖矩阵、目标 case 类型、已有 case 建议动作、生成原因、状态和人工确认记录。
- `AutomationCandidate` 需要记录来源 case、自动化类型、可行性等级、阻塞原因、依赖接口、依赖元素、测试数据和推荐执行环境。
- **API**：需要覆盖 case CRUD、版本列表、复制、废弃（Deprecate 且包含收集废弃大类/关联变更等入参）、归档恢复、AI 草稿确认、拒绝（Reject 且强制传入结构化原因 DTO）、合并、健康度查询、生成计划创建、生成计划确认、按计划生成草稿、覆盖矩阵查询、自动化候选评估、草稿字段契约校验、草稿编辑保存和批量同意。
- **UI**：采用资产工作台：左侧筛选和可信分层，中间 case 列表、生成计划、覆盖矩阵和待确认草稿，右侧详情、来源追溯、版本历史、执行摘要和健康度。拒绝草稿时弹出原因采集对话框；在详情页显示被拒绝样本归档列表、相似度匹配结果、覆盖状态、自动化候选状态和生成计划依据。待确认草稿必须提供单条编辑、重新校验和批量同意入口，并展示批量同意失败原因。

### 7.8 AI Evaluation Strategy

- AI case 生成必须经过字段完整性、可执行性、覆盖度、重复风险和幻觉风险检查。
- AI case 生成必须以 `test_case` skill 字段契约作为结构化输出约束，Evaluator 需要检查必填字段完整性、步骤可执行性、预期结果可验证性、来源需求绑定和类型依赖完整性。
- AI 草稿采纳、编辑后接受、拒绝和合并都应沉淀为反馈样本并自动生成向量嵌入提供给生成引擎作负向引导。
- AI 生成依据必须可追溯到需求点、原文片段或 RAG 召回上下文。
- 生成计划本身也需要进入 AI 评估：评估是否遗漏历史需求、是否重复生成、是否错误废弃已有 case、是否错误判断自动化可行性。
- 三类 case 生成应分别记录 Prompt / Skill 版本、输入上下文、负样本召回、Evaluator 结果和人工采纳结果。

### 7.9 Open Questions

- 场景 / 编排 case 与普通 case 的组合关系需要在技术设计中确认。
- flaky 规则是否需要按接口 case 和移动端 case 分别配置需要确认。

---

## 8. Module: 接口中心

### 8.1 Intent

接口中心是平台内 API 事实源。它负责接口文档导入、接口定义解析、人工确认、单接口调试、接口状态治理和接口 case 引用，避免接口信息只散落在 case 步骤中。

### 8.2 Problem

如果接口定义只存在于导入文档或 case 步骤里，测试开发需要重复维护 method、path、headers、params、body 和断言。接口变更后也难以知道哪些 case 受影响。

### 8.3 User Stories

- 作为测试开发工程师，我想导入接口文档并解析为接口定义，以便形成平台内接口事实源。
- 作为测试开发工程师，我想确认接口字段并执行单接口调试，以便在编写接口 case 前验证接口可用。
- 作为测试人员，我想知道接口是否候选、已确认、已验证或已废弃，以便避免使用无效接口。
- 作为测试经理，我想接口变更后看到受影响 case，以便组织回归和维护。

### 8.4 Functional Requirements

- `FR-API-001` 接口中心必须支持导入接口文档，并保存源文件、解析结果和导入记录。
- `FR-API-002` 接口定义必须包含 method、path、headers、params、body schema、response schema、状态码、描述、模块和版本。
- `FR-API-003` 接口可信分层必须覆盖候选接口、可引用接口、已验证接口和已废弃接口。
- `FR-API-004` 候选接口必须经过人工确认后才能成为可引用接口。
- `FR-API-005` 接口中心必须支持单接口调试，并保存请求、响应、耗时、错误原因和调试人。
- `FR-API-006` 接口 case 步骤应引用平台内已确认接口定义，或保存等价结构和来源说明。
- `FR-API-007` 接口废弃后，关联 case 禁止执行，并生成待办或变更影响提示。
- `FR-API-008` 接口字段允许根据导入文档自动更新，但必须保留变更摘要并提示受影响 case。
- `FR-API-009` 接口中心必须支持环境、变量集、鉴权配置引用，实际配置来源由系统设置管理。
- `FR-API-010` 单接口调试失败时必须展示可行动错误原因，例如网络失败、鉴权失败、断言失败、超时或响应格式不匹配。
- `FR-API-011` 接口中心必须支持接口定义版本和接口字段 diff，至少覆盖 method、path、headers、params、request body、response schema、状态码、鉴权和描述变化。
- `FR-API-012` 接口 case 生成必须优先绑定接口中心已确认接口定义；若仅来自接口文档解析结果，则必须保留接口文档来源和待确认状态。
- `FR-API-013` 接口定义 diff 必须进入变更中心影响分析或需求覆盖矩阵，用于识别需要新增、更新、废弃或回归的接口 case。
- `FR-API-014` 接口 case 必须能在平台内直接运行；可运行接口 case 除满足 `test_case` skill 基础字段契约外，还必须包含或引用 method、path、headers、params、request body、鉴权配置、环境变量、断言和期望状态码。
- `FR-API-015` 接口 case 从 Case 中心或接口中心发起运行前，系统必须执行依赖检查；接口定义未确认、接口已废弃、环境变量缺失、鉴权配置不可用或断言缺失时必须阻止执行并展示原因。

### 8.5 Acceptance Criteria

- `AC-API-001` Given 用户导入接口文档，When 解析完成，Then 平台展示候选接口列表和字段完整性提示。对应 `FR-API-001`、`FR-API-002`。
- `AC-API-002` Given 用户确认候选接口，When 保存成功，Then 接口变为可引用接口并可被接口 case 使用。对应 `FR-API-003`、`FR-API-004`。
- `AC-API-003` Given 用户执行单接口调试，When 请求完成，Then 平台展示请求、响应、耗时和可行动错误原因。对应 `FR-API-005`、`FR-API-010`。
- `AC-API-004` Given 接口已废弃，When 用户执行关联 case，Then 平台阻止执行并展示废弃原因和受影响 case。对应 `FR-API-007`。
- `AC-API-005` Given 接口字段被新文档更新，When 保存变更，Then 平台记录变更摘要并提示可能受影响 case。对应 `FR-API-008`。
- `AC-API-006` Given 接口文档或接口定义发生变化，When 平台完成接口 diff，Then 用户能看到字段级变化和受影响接口 case，且接口 case 生成计划优先引用已确认接口定义。对应 `FR-API-011`、`FR-API-012`、`FR-API-013`。
- `AC-API-007` Given 接口 case 已绑定已确认接口定义且执行依赖完整，When 用户在 Case 中心或接口中心点击运行，Then 平台创建执行任务并展示请求、响应、断言和报告入口。对应 `FR-API-014`。
- `AC-API-008` Given 接口 case 缺少环境变量、鉴权、断言或接口定义未确认，When 用户点击运行，Then 平台阻止执行并展示缺失依赖清单。对应 `FR-API-015`。

### 8.6 Guardrails

- 未确认接口不得作为正式接口事实源。
- 已废弃接口不得继续被执行。
- 单接口调试失败不能只显示“失败”，必须输出可行动错误原因。
- 接口 case 不得只依赖自然语言需求生成；必须绑定接口定义、接口文档解析结果或接口 diff。
- 接口 case 不得在缺少接口事实源、环境变量、鉴权或断言时进入可执行状态。

### 8.7 Data / API / UI Implications

- 数据对象包括 InterfaceDocument、InterfaceDefinition、InterfaceVersion、InterfaceDiff、InterfaceDebugResult、InterfaceChangeRecord。
- API 需要覆盖接口导入、解析、确认、更新、废弃、调试、接口 diff、受影响 case 查询、接口 case 生成上下文输出、接口 case 执行依赖检查和运行入口。
- UI 建议包含接口列表、候选接口确认、接口详情、字段 diff、调试面板、接口 case 运行入口、依赖缺失提示和变更影响提示。

### 8.8 AI Evaluation Strategy

- 接口文档解析需记录原文来源、字段置信度、缺失字段和人工修改。
- AI 生成断言建议时必须展示依据和可编辑结果。

### 8.9 Open Questions

- 接口字段自动更新是否需要完整版本快照，还是只保留变更摘要，需要技术设计确认。

---

## 9. Module: 移动端执行中心

### 9.1 Intent

移动端执行中心负责 Android 设备、App、页面、元素和移动端 case 执行上下文，打通 Appium 执行与报告证据回传。

### 9.2 Problem

移动端自动化失败常常由设备离线、App 版本不一致、元素定位失效、Appium session 异常或业务断言失败引起。如果平台不保存设备、App、元素和执行证据，失败无法可信定位。

### 9.3 User Stories

- 作为测试开发工程师，我想识别 Android 模拟器和真机，并看到在线状态、占用状态和系统信息，以便选择可用设备执行。
- 作为测试人员，我想登记或上传 APK，并让报告绑定 App package、version 和 build，以便执行结果可追溯。
- 作为测试开发工程师，我想从 Appium XML 或 Inspector 导入元素，并绑定页面、模块和主定位，以便移动端 case 引用稳定元素资产。
- 作为测试人员，我想运行移动端 case 并查看截图、XML 和 Appium 日志，以便定位失败原因。

### 9.4 Functional Requirements

- `FR-MOB-001` 移动端执行中心必须支持 Android 设备扫描，展示设备 id、名称、系统版本、分辨率、连接状态和占用状态。
- `FR-MOB-002` 设备状态必须至少覆盖 idle、running、offline、error、disabled。
- `FR-MOB-003` 平台必须提供设备占用锁，保证同一时间一个设备只执行一套测试任务，并在异常退出后释放。
- `FR-MOB-004` 平台必须支持 APK 上传或 App 信息登记，保存 package、version_name、version_code、build、上传人和上传时间。
- `FR-MOB-005` 移动端执行任务和报告必须绑定 App package、version 和 build。
- `FR-MOB-006` 平台必须支持 Appium XML 或 Inspector 导入，生成页面和元素资产。
- `FR-MOB-007` 元素必须绑定页面、模块、App 版本或页面版本、activity、截图、XML 快照、主定位和可读名称。
- `FR-MOB-008` 正式移动端 case 必须引用元素库；调试时可以临时写 locator，但调试成功后应沉淀为元素资产。
- `FR-MOB-009` 移动端执行失败时必须保存失败步骤、截图、XML、Appium 日志或设备异常信息中的关键证据。
- `FR-MOB-010` **移动端元素定位失效自动诊断与自愈自适应机制 (Mobile Element Stale Auto-Diagnosis & Self-Healing)**：
  - `FR-MOB-010.1` **多模态异常快照捕获 (Evidence Capture)**：在 Appium 自动化用例运行过程中，一旦发生元素定位失败（例如抛出 `NoSuchElementException`, `TimeoutException`），系统必须在捕获异常的同时阻断该用例并执行以下快照存储动作：
    - **UI 截图**：调用物理或模拟器截图 API 并存储。
    - **XML 瞬时 DOM 树**：执行 Appium `getPageSource()`，抓取完全格式化的布局树快照并持久化。
    - **日志提取**：抓取并存储最近 10 行 Appium 操作日志与运行栈 Traceback。
  - `FR-MOB-010.2` **AI 结构比对与偏置纠错算法 (Heuristics Matching)**：诊断引擎（`LocatorSelfHealingSkill`）在用例流产后，需比对原始 `MobileElement` 的结构描述、位置偏置和瞬时布局 XML tree。诊断模型需基于属性文本相似、同胞节点索引不变以及 Activity 上下文等维度，计算在最新 XML 树上指向相同意图元素的全新主定位候选（New Locator Candidate），并生成置信评分。
  - `FR-MOB-010.3` **自愈修复提案与待办流转 (Self-Healing Proposal Sinking)**：如果 AI 生成的修复提案置信度评分 >= 0.70，系统自动组装包含 `old_locator`, `new_proposed_locator`, `confidence_score` 的“元素修复提案对象”，并将该事件作为 `ELEMENT_STALE` 类型的 Todo 条目推送到**“待办中心（Module: 待办中心）”**。
  - `FR-MOB-010.4` **一键确认自愈与核销回写 (Self-Healing Action)**：用户进入待办中心该条待办，系统在抽屉内提供双视图比对（旧截图、旧定位 VS 新 XML 候选 DOM 对比）。用户点击“应用此修复”后，系统调用接口物理改写该 `MobileElement` 的 `主定位` 字段，并同步将该待办核销为 `resolved`，下一次执行中心运行任务时即可应用最新定位，达成线上资产免重构、自愈修复的完整闭环。
- `FR-MOB-011` 当前完整交付不要求 iOS、云真机、多设备调度和 AI 视觉定位。
- `FR-MOB-012` 移动端自动化脚本 case 生成前必须检查 `AutomationCandidate`，确认已具备必要的元素资产、App 版本、页面上下文、测试数据和执行环境。
- `FR-MOB-013` 需求差异或页面 / 元素变化影响移动端自动化时，系统必须生成元素检查或自动化候选资产缺失待办，不得直接生成正式移动端自动化 case。
- `FR-MOB-014` 移动端自动化 case 必须能在平台内直接运行；可运行自动化 case 除满足 `test_case` skill 基础字段契约外，还必须绑定来源功能 / 接口 case、元素资产、App 版本、设备能力、测试数据和断言。
- `FR-MOB-015` 用户从 Case 中心或移动端执行中心运行自动化 case 前，系统必须执行依赖检查；元素缺失、App 版本不匹配、设备不可用、测试数据缺失或 `AutomationCandidate` 未通过时必须阻止执行并展示原因。

### 9.5 Acceptance Criteria

- `AC-MOB-001` Given Android 设备连接成功，When 用户进入移动端执行中心，Then 平台展示设备状态、系统版本、分辨率和占用状态。对应 `FR-MOB-001`、`FR-MOB-002`。
- `AC-MOB-002` Given 执行任务异常退出，When 设备锁检测运行，Then 平台释放设备占用并记录异常原因。对应 `FR-MOB-003`。
- `AC-MOB-003` Given 用户登记 App 信息，When 移动端 case 执行完成，Then 报告绑定 App package、version 和 build。对应 `FR-MOB-004`、`FR-MOB-005`。
- `AC-MOB-004` Given 用户导入 XML，When 解析成功，Then 元素资产可被移动端 case 引用。对应 `FR-MOB-006`、`FR-MOB-007`。
- `AC-MOB-005` Given 正式移动端 case 保存，When 步骤只包含裸 locator 且未引用元素库，Then 平台阻止保存或标记为调试态。对应 `FR-MOB-008`。
- `AC-MOB-006` Given 移动端 case 执行失败，When 用户查看报告，Then 报告包含失败步骤和至少一种关键证据：截图、XML、Appium 日志或设备异常。对应 `FR-MOB-009`。
- `AC-MOB-007` Given Appium 用例定位失败，When 诊断置信度 >= 0.70，Then 平台抓取多模态截图与 XML，向待办中心推送 `ELEMENT_STALE` 待办，且用户一键应用后能成功回写定位并核销该待办。对应 `FR-MOB-010.1`、`FR-MOB-010.2`、`FR-MOB-010.3`、`FR-MOB-010.4`。
- `AC-MOB-008` Given 用户请求生成移动端自动化脚本 case，When 元素资产、App 版本或测试数据不完整，Then 平台标记 `AutomationCandidate` 为 medium / low 并生成待办，不允许进入正式自动化资产。对应 `FR-MOB-012`、`FR-MOB-013`。
- `AC-MOB-009` Given 移动端自动化 case 依赖完整且设备可用，When 用户在 Case 中心或移动端执行中心点击运行，Then 平台创建执行任务并在报告中绑定 App、设备、截图、XML 和 Appium 日志。对应 `FR-MOB-014`。
- `AC-MOB-010` Given 自动化 case 缺少元素资产、App 版本、设备、测试数据或自动化候选未通过，When 用户点击运行，Then 平台阻止执行并展示缺失依赖清单。对应 `FR-MOB-015`。

### 9.6 Guardrails

- 正式移动端 case 不允许只依赖裸 locator。
- 元素失效不能自动改写正式 case。
- 设备异常必须释放占用锁，避免阻塞后续执行。
- **失效限流阻断**：当同一设备上的同一用例执行发生连续定位失效超过 3 次时，执行中心必须立刻终止后续执行，防止生成过多冗余的 DOM 异常快照和重复生成垃圾待办。
- 自动化脚本 case 不得绕过 `AutomationCandidate` 可行性检查。
- 自动化 case 不得在元素、App、设备、测试数据或断言依赖不完整时进入可执行状态。

### 9.7 Data / API / UI Implications

- **数据对象**：包括 MobileDevice、MobileApp、MobilePage、MobileElement、MobileExecutionEvidence、MobileElementRepairProposal、AutomationCandidate。
- **API**：需要覆盖设备扫描、设备状态、App 登记、XML 导入、元素管理、设备锁、多模态快照上传、AI 自愈提案接口、自动化候选评估、自动化 case 执行依赖检查、运行入口和待办一键更新。
- **UI**：资产中心：左侧筛选和可信分层，中间用例列表和自动化候选列表，右侧详情、元素资产和健康状态。提供自动化 case 运行入口和依赖缺失提示；提供“自愈对比抽屉”：支持点击后在一屏内展示当时定位失败的现场截图、闪烁标红指出 AI 建议纠偏位置、定位前后代码对比以及一键合并生效按钮。

### 9.8 AI Evaluation Strategy

- AI 可辅助识别元素失效原因和失败分类，但必须基于截图、XML、日志和步骤上下文。
- AI 视觉定位属于未来探索能力，不进入当前正式移动端执行闭环。

### 9.9 Open Questions

- 调试 locator 沉淀为元素资产的交互方式需要原型确认。

---

## 10. Module: 执行中心

### 10.1 Intent

执行中心是统一运行控制台，负责承接接口 case、移动端 case、未来 WebSocket / LLM case、场景流和回归任务的执行状态、配置、日志、重试、取消和失败处理建议。

### 10.2 Problem

如果接口执行和移动端执行只存在于各自页面，测试人员无法统一查看任务状态、失败原因和报告产物。执行失败后也难以区分业务失败、断言失败、环境失败、执行器异常或数据问题。

### 10.3 User Stories

- 作为测试人员，我想从 case、接口或移动端页面发起执行，并在执行中心统一查看任务状态。
- 作为测试开发工程师，我想在执行前选择环境、变量、设备、App、超时时间和 capability 覆盖，以便执行配置可控。
- 作为测试人员，我想查看步骤状态、实时日志、失败分类、重试记录和处理建议，以便快速定位问题。
- 作为测试经理，我想看到当前执行队列、失败趋势和取消任务，以便掌握执行健康度。

### 10.4 Functional Requirements

- `FR-EXEC-001` 执行中心必须提供统一任务模型，包含执行对象、执行来源、执行类型、项目、模块、环境、变量、设备、App、状态、步骤结果、报告产物、创建人和时间。
- `FR-EXEC-002` 执行类型必须支持接口 case 和移动端 case，并为未来 WebSocket / LLM case、场景流和回归任务预留扩展字段。
- `FR-EXEC-003` 执行状态必须至少包含 pending、running、passed、failed、error、cancelled、need_review。
- `FR-EXEC-004` 用户必须能从 Case 中心、接口中心、移动端执行中心发起单 case 执行或调试。
- `FR-EXEC-005` 执行前配置必须支持环境、变量、设备、App、超时时间和 Appium capability 覆盖。
- `FR-EXEC-006` 执行中心必须展示步骤状态、耗时、日志、异常、请求响应摘要和证据产物。
- `FR-EXEC-007` 执行失败必须做轻量分类：业务失败、断言失败、环境失败、执行器异常、数据问题、设备异常。
- `FR-EXEC-008` 执行失败后最多自动重试 3 次，并展示重试记录。
- `FR-EXEC-009` 最终失败后必须展示处理建议：重跑、检查环境、修复 case、标记 bug、人工复核。
- `FR-EXEC-010` 用户取消任务后，只保留任务日志，不生成正式质量报告。
- `FR-EXEC-011` 执行中心必须能跳转到关联 case、接口、设备、App 和报告。
- `FR-EXEC-012` 执行中心不得执行未确认 AI 草稿、已废弃 case、已停用 case、接口定义未确认的接口 case 或资产依赖不完整的自动化脚本 case。
- `FR-EXEC-013` 回归执行集应优先来源于 CoverageMatrix、CaseGenerationPlan 和变更中心回归推荐，并保留推荐依据和人工调整记录。
- `FR-EXEC-014` 执行结果必须能回写到 CoverageMatrix，区分新需求覆盖执行、历史需求回归执行、覆盖缺口未执行和执行失败未闭环。
- `FR-EXEC-015` 执行中心必须支持从 Case 中心、接口中心和移动端执行中心直接运行接口 case 与自动化 case，并在创建任务前统一执行依赖检查。
- `FR-EXEC-016` 可执行 case 必须区分设计状态和运行状态；字段契约完整但运行依赖不完整的 case 可以作为正式设计资产存在，但不得进入可执行队列。
- `FR-EXEC-017` 平台必须提供统一 `RunnableCheck` 机制，所有可执行资产（接口 case、移动端自动化 case，以及未来 Web / LLM / 场景执行 case）在运行前都必须生成同一种结构的可运行检查结果。
- `FR-EXEC-018` `RunnableCheck` 必须至少输出：是否可运行、运行状态、缺失依赖、阻断原因、风险级别、修复入口、关联待办、检查来源、检查时间和检查人 / 触发人。
- `FR-EXEC-019` `RunnableCheck` 必须支持按 case 类型扩展依赖项；接口 case 检查接口定义、环境、鉴权、请求、断言，自动化 case 检查来源 case、元素、App、设备、测试数据、断言，但对外状态和 API 响应保持统一。
- `FR-EXEC-020` Case 中心、接口中心、移动端执行中心和执行中心必须消费同一份 `RunnableCheck` 结果；不得各自维护互相不一致的“是否可运行”判断。
- `FR-EXEC-021` `RunnableCheck` 失败原因必须按处理方式分流为三类：可立即修复、资产维护、需求 / case 设计问题。
- `FR-EXEC-022` 可立即修复的问题不得默认进入待办中心，应在当前页面直接提示并提供快捷修复入口；例如选择环境、补变量值、选择设备、补测试数据、选择鉴权配置或选择 App 版本。
- `FR-EXEC-023` 资产维护类问题必须进入待办中心或来源资产模块；例如接口未确认、接口已废弃、元素资产缺失、元素定位失效、App 版本不匹配、自动化候选依赖不完整或来源接口 / 元素 / 页面不存在。
- `FR-EXEC-024` 需求 / case 设计问题必须回到覆盖矩阵、生成计划或 case 编辑处理；例如步骤不可执行、预期结果不可验证、断言缺失、来源需求已变化、case 已过期或生成计划建议更新 / 废弃。
- `FR-EXEC-025` 用户完成立即修复后，系统必须自动重新触发 `RunnableCheck` 并刷新运行状态，但不得自动执行 case；用户仍需再次点击运行。

### 10.5 Acceptance Criteria

- `AC-EXEC-001` Given 用户从接口 case 发起执行，When 任务创建成功，Then 执行中心展示任务状态、步骤状态和关联 case。对应 `FR-EXEC-001`、`FR-EXEC-004`。
- `AC-EXEC-002` Given 用户配置环境和变量，When 执行开始，Then Runner 使用该配置并在任务详情中保留配置摘要。对应 `FR-EXEC-005`。
- `AC-EXEC-003` Given 执行失败，When 用户查看任务详情，Then 平台展示失败分类、异常信息、重试记录和处理建议。对应 `FR-EXEC-007`、`FR-EXEC-008`、`FR-EXEC-009`。
- `AC-EXEC-004` Given 用户取消任务，When 取消成功，Then 任务状态为 cancelled，只保留日志，不生成正式报告。对应 `FR-EXEC-010`。
- `AC-EXEC-005` Given 执行完成，When 用户查看任务详情，Then 可以跳转到 case、接口、设备、App 和报告。对应 `FR-EXEC-011`。
- `AC-EXEC-006` Given 用户尝试执行废弃 case、未确认草稿或资产依赖不完整的自动化脚本 case，When 执行请求提交，Then 平台阻止执行并展示原因。对应 `FR-EXEC-012`。
- `AC-EXEC-007` Given 用户基于变更中心推荐创建回归执行集，When 执行完成，Then 执行中心记录推荐依据、人工调整记录，并将结果回写到覆盖矩阵。对应 `FR-EXEC-013`、`FR-EXEC-014`。
- `AC-EXEC-008` Given 用户从 Case 中心、接口中心或移动端执行中心运行接口 / 自动化 case，When 依赖检查通过，Then 执行中心创建统一执行任务并可跳转回来源 case。对应 `FR-EXEC-015`。
- `AC-EXEC-009` Given case 已是正式设计资产但运行依赖不完整，When 用户尝试执行，Then 平台阻止进入执行队列并展示设计状态和运行状态差异。对应 `FR-EXEC-016`。
- `AC-EXEC-010` Given 用户在任一模块查看可执行 case，When 打开运行状态，Then 平台展示统一 `RunnableCheck` 结果，包括是否可运行、缺失依赖、阻断原因、修复入口、关联待办和最近检查时间。对应 `FR-EXEC-017`、`FR-EXEC-018`。
- `AC-EXEC-011` Given 同一个 case 在 Case 中心、接口中心或移动端执行中心展示，When 其运行依赖发生变化，Then 所有入口展示同一份最新 `RunnableCheck` 状态，不得出现一个入口可运行、另一个入口不可运行的矛盾。对应 `FR-EXEC-019`、`FR-EXEC-020`。
- `AC-EXEC-012` Given `RunnableCheck` 失败原因属于可立即修复，When 用户查看运行状态，Then 当前页面展示快捷修复入口而不是默认生成待办；用户修复后系统自动重新检查但不自动执行。对应 `FR-EXEC-021`、`FR-EXEC-022`、`FR-EXEC-025`。
- `AC-EXEC-013` Given `RunnableCheck` 失败原因属于资产维护，When 用户查看运行状态，Then 平台生成或关联待办并提供跳转到来源资产模块的入口。对应 `FR-EXEC-021`、`FR-EXEC-023`。
- `AC-EXEC-014` Given `RunnableCheck` 失败原因属于需求或 case 设计问题，When 用户查看运行状态，Then 平台引导用户回到覆盖矩阵、生成计划或 case 编辑处理，不允许直接关闭为已解决。对应 `FR-EXEC-021`、`FR-EXEC-024`。

### 10.6 Guardrails

- Runner 只能执行动作和产出步骤结果，不得直接修改需求、case 或报告主表。
- 取消任务不得生成正式质量结论。
- 自动重试次数不得超过 3 次。
- 执行入口必须校验 case 生命周期、草稿状态、接口可信状态和自动化资产依赖，不得只依赖前端按钮隐藏。
- 执行中心不得把“设计字段完整”误判为“可运行”；接口、环境、鉴权、元素、App、设备和测试数据依赖必须单独校验。
- 是否可运行只能以统一 `RunnableCheck` 为准；各业务模块不得各自实现独立且不可追溯的运行状态判断。
- 可立即修复的问题不得制造待办噪音；资产维护问题不得仅用页面提示替代待办；设计问题不得通过待办中心简单核销绕过覆盖矩阵、生成计划或 case 编辑。
- 立即修复后只能自动重新检查，不得自动执行 case。

### 10.7 Data / API / UI Implications

- 数据对象包括 ExecutionTask、ExecutionStepResult、ExecutionLog、ExecutionRetryRecord、ExecutionArtifact、ExecutionCoverageLink、RunnableCheck、RunnableCheckItem。
- `RunnableCheck` 需要记录 case、case 类型、是否可运行、运行状态、风险级别、检查时间、检查来源和触发人；`RunnableCheckItem` 需要记录依赖类型、依赖对象、检查结果、阻断原因、修复入口和关联待办。
- `RunnableCheckItem` 还需要记录处理分类：`quick_fix`、`asset_maintenance`、`design_rework`，以及处理后的最近一次重检结果。
- API 需要覆盖任务创建、任务列表、详情、取消、重跑、日志查询、状态轮询、回归推荐执行集创建、覆盖矩阵回写、RunnableCheck 触发、RunnableCheck 查询和按来源模块刷新运行状态。
- API 需要提供立即修复后的 `RunnableCheck` 自动重检能力，但不得直接触发执行任务。
- UI 需要提供执行列表、任务详情、步骤时间线、日志面板、证据入口、覆盖矩阵回写状态、统一可运行状态面板、快捷修复入口、待办跳转入口和设计回流入口。

### 10.8 AI Evaluation Strategy

- AI 可基于执行日志、请求响应、截图、XML 和历史报告生成失败分析建议。
- AI 失败分析必须展示证据来源，不得直接作为最终质量结论。

### 10.9 Open Questions

- 不同执行对象的字段差异需要在技术设计中拆分清楚。

---

## 11. Module: 报告中心

### 11.1 Intent

报告中心是执行可信性的证据中心。它必须保存执行输入、输出、断言、日志、截图、XML、Appium 日志、AI 评估依据和复现上下文，让失败能被复盘。

### 11.2 Problem

传统报告只展示 passed 或 failed，无法回答失败发生时请求了什么、返回了什么、哪个断言失败、移动端截图是什么、设备是否异常、是否经过重试。没有证据链的报告无法支持 bug 定位和回归决策。

### 11.3 User Stories

- 作为测试人员，我想查看 request、response、断言 expected / actual、变量上下文和日志，以便定位接口失败。
- 作为测试开发工程师，我想查看移动端截图、XML、Appium 日志和设备异常，以便区分业务问题和自动化问题。
- 作为测试经理，我想查看通过率、失败率、趋势、失败聚类和重试记录，以便跟踪版本质量。
- 作为平台管理员，我想报告默认脱敏并可配置保留周期，以便控制数据风险。

### 11.4 Functional Requirements

- `FR-REPORT-001` 报告中心必须支持单 case 报告和批次报告。
- `FR-REPORT-002` 报告状态必须覆盖 passed、failed、error、need_review、cancelled。
- `FR-REPORT-003` 接口报告必须包含 request、response、headers、断言 expected / actual、变量上下文、耗时和错误信息。
- `FR-REPORT-004` 移动端报告必须包含设备、App package、version、build、失败步骤、截图、XML、Appium 日志或设备异常。
- `FR-REPORT-005` 报告必须关联执行任务、case、接口、设备、App、环境和执行配置。
- `FR-REPORT-006` 报告必须支持在线预览和 HTML 导出。
- `FR-REPORT-007` 报告导出必须默认脱敏。
- `FR-REPORT-008` 报告默认保留 14 天，保留周期可配置。
- `FR-REPORT-009` 取消任务不得生成正式质量报告，但应保留任务日志。
- `FR-REPORT-010` 报告缺少核心证据链时，不得标记为可复盘报告。
- `FR-REPORT-011` 高风险、AI、LLM 场景的质量结论需要人工确认。
- `FR-REPORT-012` AI 失败分析只能作为证据化建议，不能替代人工最终判断。
- `FR-REPORT-013` 报告必须能展示本次执行覆盖了哪些需求点、哪些 RequirementDiff、哪些 CaseGenerationPlan 项和哪些历史基线回归项。
- `FR-REPORT-014` 报告必须展示覆盖缺口：新需求未执行、历史需求未回归、执行失败未闭环和被跳过的自动化候选。
- `FR-REPORT-015` AI 风险摘要必须能追溯到 CoverageMatrix、执行证据、变更影响记录或待办，不能只给自然语言结论。

### 11.5 Acceptance Criteria

- `AC-REPORT-001` Given 接口 case 执行完成，When 用户查看报告，Then 报告展示 request、response、断言、变量上下文、耗时和错误信息。对应 `FR-REPORT-003`。
- `AC-REPORT-002` Given 移动端 case 执行失败，When 用户查看报告，Then 报告展示设备、App、失败步骤和至少一种移动端关键证据。对应 `FR-REPORT-004`。
- `AC-REPORT-003` Given 用户导出报告，When 导出完成，Then Authorization、Cookie、token、password 等敏感字段默认脱敏。对应 `FR-REPORT-006`、`FR-REPORT-007`。
- `AC-REPORT-004` Given 任务被取消，When 用户查看报告中心，Then 不存在正式质量报告，但任务日志可查看。对应 `FR-REPORT-009`。
- `AC-REPORT-005` Given 报告缺少核心证据链，When 系统生成报告，Then 报告不得标记为可复盘。对应 `FR-REPORT-010`。
- `AC-REPORT-006` Given 执行来自覆盖矩阵或变更推荐，When 用户查看报告，Then 报告展示覆盖的需求点、差异、生成计划项和未覆盖缺口。对应 `FR-REPORT-013`、`FR-REPORT-014`。
- `AC-REPORT-007` Given 报告展示 AI 风险摘要，When 用户查看风险来源，Then 能跳转到覆盖矩阵、执行证据、变更记录或待办。对应 `FR-REPORT-015`。

### 11.6 Guardrails

- 报告导出默认脱敏。
- AI 失败分析不能直接成为最终质量结论。
- 没有核心证据链的报告不能作为可信质量证据。
- 报告不能只证明 case 执行过，还必须能证明对应需求点、差异或覆盖缺口是否被验证。

### 11.7 Data / API / UI Implications

- 数据对象包括 TestReport、ReportArtifact、ReportEvidence、ReportExportRecord、ReportRetentionPolicy、ReportCoverageSummary。
- API 需要覆盖报告生成、列表、详情、预览、导出、证据查询、保留策略和覆盖摘要查询。
- UI 需要展示报告摘要、步骤证据、请求响应、移动端证据、覆盖摘要、未覆盖缺口、AI 分析建议和导出入口。

### 11.8 AI Evaluation Strategy

- AI 失败分析需要引用报告证据，并输出原因、置信度、建议动作和人工确认状态。
- AI 分析被采纳、被修改、被拒绝都应进入反馈样本。

### 11.9 Open Questions

- 报告默认保留 14 天是否符合团队实际需要。
- 高风险 / AI / LLM 场景的人工确认策略需要细化。

---

## 12. Module: AI 能力中心

### 12.1 Intent

AI 能力中心统一管理 AI 任务、RAG、Prompt、Skill、Evaluator、Phoenix、反馈样本、模型效果和成本监控。它的价值是让 AI 输出可解释、可评估、可审计、可迭代。

### 12.2 Problem

如果 AI 工作台、RAG、Prompt、Evaluator 和反馈样本分散建设，AI 输出会缺少上下文、缺少质量门禁、缺少失败复盘，最终只能作为一次性辅助文本，无法进入正式测试资产链路。

### 12.3 User Stories

- 作为测试人员，我想使用 AI 解析需求、生成 case、检查覆盖度和分析失败，以便减少重复工作。
- 作为测试经理，我想 AI 输出保留输入、上下文、评分、风险和人工确认记录，以便 AI 建议可审计。
- 作为平台维护者，我想管理 RAG、Prompt、Skill、Evaluator、反馈样本和成本，以便持续优化 AI 能力。
- 作为测试开发工程师，我想 AI 能力以 Skill 形式拆分和组合，以便能力边界清晰、便于测试。

### 12.4 Functional Requirements

- `FR-AI-001` AI 能力中心必须支持 AI 任务记录，覆盖需求解析、接口解析、case 生成、门禁检查、覆盖评估和失败分析。
- `FR-AI-002` AI 任务必须记录输入、输出、模型、Prompt / Skill 版本、RAG 上下文、耗时、错误、成本估算和发起人。
- `FR-AI-003` RAG 入库内容必须包含需求、case、接口、元素、报告、失败分析、变更记录和未来 bug 数据。
- `FR-AI-004` RAG 入库前必须脱敏，召回结果必须展示来源、权重和是否被采用。
- `FR-AI-005` Prompt 修改后必须跑评估集或等效验证，但当前不要求支持回滚。
- `FR-AI-006` Skill 必须按单一能力组织，例如 RequirementParseSkill、RagRetrieveSkill、CaseGenerateSkill、CoverageEvaluateSkill、PhoenixEvaluateSkill、FailureAnalysisSkill。
- `FR-AI-007` Evaluator 阈值必须支持按模块和风险等级配置。
- `FR-AI-008` Phoenix 或等价评估必须能记录 hallucination、relevance、correctness、coverage 等指标。
- `FR-AI-009` AI 输出影响正式资产时，必须通过评估和人工确认。
- `FR-AI-010` AI 低分、格式错误、超时或调用失败必须进入 failed 或 need_review，并提供错误原因。
- `FR-AI-011` AI 反馈样本库必须记录被接受、被修改、被拒绝、失败样本和低分样本。
- `FR-AI-012` AI 成本监控必须按功能、模型、日期展示 token、耗时、失败率和估算成本。
- `FR-AI-013` 凡需求解析、接口解析、case 生成、门禁检查、覆盖评估、失败分析或其他业务逻辑触发 AI 调用时，系统不允许使用本地模板、规则生成、缓存结果、模拟结果或静默跳过等降级逻辑替代真实 AI 调用；AI 连接失败、模型不可用、鉴权错误、超时或配置错误时，任务必须直接失败并向用户弹窗报错。
- `FR-AI-014` 每次 case 生成相关 AI 任务必须记录完整生成上下文，包括当前文档、修订版、历史基线、RequirementDiff、CoverageMatrix、CaseGenerationPlan、RAG 召回、负样本、Prompt 版本、Skill 版本和 Evaluator 结果。
- `FR-AI-015` AI 不得绕过 RequirementDiff、CoverageMatrix 和 CaseGenerationPlan 直接产出可接受的正式 case；AI 只能生成差异建议、覆盖建议、生成计划建议和 case 草稿。

### 12.5 Acceptance Criteria

- `AC-AI-001` Given AI case 生成任务完成，When 用户查看任务详情，Then 能看到输入、RAG 上下文、输出、模型、Prompt / Skill 版本、评分和人工确认状态。对应 `FR-AI-001`、`FR-AI-002`。
- `AC-AI-002` Given RAG 召回结果被用于 AI 输出，When 用户查看依据，Then 平台展示来源对象、权重和采用情况。对应 `FR-AI-003`、`FR-AI-004`。
- `AC-AI-003` Given Prompt 被修改，When 管理员保存，Then 平台要求跑评估集或等效验证后才能标记为可用。对应 `FR-AI-005`。
- `AC-AI-004` Given AI 输出低于阈值，When 任务完成，Then 平台进入 need_review 或阻止入库，并生成待办。对应 `FR-AI-007`、`FR-AI-008`、`FR-AI-010`。
- `AC-AI-005` Given AI case 被拒绝，When 状态更新，Then 记录拒绝原因并进入反馈样本库。对应 `FR-AI-011`。
- `AC-AI-006` Given AI 功能被调用，When 查看成本监控，Then 可按功能、模型和日期查看 token、耗时、失败率和估算成本。对应 `FR-AI-012`。
- `AC-AI-007` Given 需求解析或其他业务流程需要调用 AI，When AI 连接失败、鉴权失败、模型不可用、超时或配置错误，Then 平台必须中断当前 AI 任务、记录失败原因，并通过统一弹窗向用户展示错误，不得自动切换到降级逻辑继续产出解析结果、case 草稿、门禁结论或失败分析。对应 `FR-AI-013`。
- `AC-AI-008` Given 用户查看某次 AI case 生成任务，When 展开任务详情，Then 能看到当前文档、历史基线、需求差异、覆盖矩阵、生成计划、RAG 召回、负样本和 Evaluator 结果。对应 `FR-AI-014`。
- `AC-AI-009` Given 覆盖矩阵或生成计划缺失，When 用户触发 AI case 生成，Then AI 任务直接失败并展示缺失上下文，而不是继续输出可接受草稿。对应 `FR-AI-015`。

### 12.6 Guardrails

- AI 输出不得直接写正式业务资产。
- 敏感数据不得明文进入 RAG、AI 输入和 Phoenix 输入。
- Evaluator 不得替代人工确认。
- Prompt 修改未经验证不得标记为可用。
- AI 调用不得使用降级逻辑掩盖连接、鉴权、模型、超时或配置错误；任何 AI 调用失败都必须显式失败并弹窗提示用户。
- AI 生成不得绕过差异分析、覆盖矩阵、生成计划和人工确认。

### 12.7 Data / API / UI Implications

- 数据对象包括 AiTask、RagChunk、PromptTemplate、SkillDefinition、EvaluatorConfig、EvaluationSample、AiUsageRecord、AiFeedbackSample、AiGenerationContext。
- API 需要覆盖 AI 任务、RAG 入库 / 召回、Prompt 管理、Skill 管理、Evaluator 配置、反馈样本、成本统计和生成上下文查询。
- UI 需要提供 AI 任务列表、RAG 片段、Prompt / Skill 管理、Evaluator 结果、反馈样本、生成上下文追溯和成本看板。

### 12.8 AI Evaluation Strategy

- AI case 生成：评估字段完整性、需求覆盖、步骤可执行性、断言质量、重复风险和幻觉风险。
- 需求解析：评估原文片段映射率、需求点完整率、冲突识别准确率和人工修改率。
- 差异分析和覆盖矩阵：评估历史需求遗漏率、差异分类准确率、覆盖状态准确率、生成计划漏判率和人工采纳率。
- 失败分析：评估证据引用完整性、原因分类准确率和建议采纳率。
- RAG：评估召回可用率、来源准确率和人工反馈。

### 12.9 Open Questions

- Prompt 修改验证使用完整评估集还是轻量冒烟集。
- 模块完整交付是否需要真实向量检索，还是先用结构化解析和简单检索。
- Evaluator 阈值的模块和风险等级枚举需要细化。

---

## 13. Module: 变更中心

### 13.1 Intent

变更中心是一级模块，负责记录需求、接口、元素、case、App 版本、bug 修复和报告趋势变化，并分析这些变化对 case、执行和回归范围的影响。

### 13.2 Problem

需求、接口、元素和 App 版本变化后，测试团队往往靠经验判断回归范围，容易漏测。case 长期不维护后会失效，质量风险也无法与变更原因关联。

### 13.3 User Stories

- 作为测试经理，我想查看本版本发生了哪些需求、接口、元素、App 和 bug 修复变化，以便判断回归范围。
- 作为测试人员，我想看到变更影响的 case、接口、元素和报告，以便新增、修改、废弃或回归 case。
- 作为产品经理 / 研发负责人，我想看到需求变化带来的测试影响，以便评估版本风险。
- 作为测试人员，我想系统生成 case 修改草稿，但必须由我确认后才生效，以便提升维护效率但不失控。

### 13.4 Functional Requirements

- `FR-CHANGE-001` 变更中心必须支持变更记录，变更来源包括需求变更、接口变更、元素失效、App 版本变化、case 变更、bug 修复和报告趋势变化。
- `FR-CHANGE-002` 变更记录必须关联项目、模块、来源对象、变更类型、变更摘要、影响范围、创建人和状态。
- `FR-CHANGE-003` **变更影响图谱的多维拓扑解析算法机制 (Multi-Dimensional Topology Parsing)**：
  - `FR-CHANGE-003.1` **精准依赖链条追踪 (Traceability Chain)**：当变更记录（`ChangeRecord`）触发时，系统必须自动在后台构建以变更源为核心的依赖有向图（Dependency Directed Graph）并提取以下三条核心链路：
    - **需求链 (Requirement Chain)**：若新需求文档导入，提取其与旧版 RAG 语义对比的核心修改节点，通过 `TestCase.source_requirement` 外键和相似度索引，自动捞取引用了该需求点的所有正式用例（TestCase）。
    - **接口链 (API Chain)**：若接口定义修改（例如某字段的 `response_schema` 由数字变更为对象），系统必须扫描接口引用元数据表，自动捞取所有步骤（`TestCaseStep`）引用了该 `Interface_ID` 的正式用例，将其标记为“契约受损”状态。
    - **元素链 (Locator Chain)**：当移动端发生版本变化或页面元素主定位器因 `NoSuchElementException` 废弃时，自动抓取绑定了该 `MobileElement_ID` 的全部移动端测试步骤，将其标记为“定位受损”状态。
  - `FR-CHANGE-003.2` **RAG 上下文语义推荐 (Semantic Regression Recommendation)**：除显式外键和引用的强硬拓扑外，变更分析引擎还必须调用 `RagRetrieveSkill` 进行语义匹配（Cosine Similarity > 0.65），推荐那些尽管没有显式引用、但在功能场景上具有高度相关性的用例作为回归推荐列表的一部分，并按置信度由高到低排序，附带具体的 RAG 召回评分作为依据。
- `FR-CHANGE-004` 变更中心必须输出受影响 case、接口、元素、模块和报告列表，并以“变更依赖树图 (Dependency Tree Map)”的可视化形式进行直观呈现。
- `FR-CHANGE-005` 变更中心必须支持推荐回归 case，回归依据必须标明是由于“直接契约变更、间接拓扑影响还是 RAG 语义召回”，并允许人工自由勾选、添加或移除，完成最终回归集的锁版确认。
- `FR-CHANGE-006` **AI 变更自适应修改草稿自生成机制 (Adaptive Change Drafts)**：
  - `FR-CHANGE-006.1` **自动修改提议生成**：对于拓扑链路中被标为受损的用例（如接口契约改变），系统不得直接修改正式资产。它应启动 `ChangeCaseAdaptSkill` 异步任务，将当前用例的旧步骤与新的变更记录（RAG 变更对比片段、新接口 schema 格式）一同提交给大模型，自动预测并生成包含针对性修正（如更新 assertion、修改 parameters）的 `ChangeCaseDraft`（修改草稿）。
  - `FR-CHANGE-006.2` **草稿留存与人工双活确认**：自适应草稿必须作为分支状态（`TestCase.draft_version` 或存入 `ChangeCaseDraft` 物理表）保存。只有当测试人员在待办中心点击“合并并更新”后，草稿修改内容才能覆盖正式 TestCase 资产并生成快照版本，彻底杜绝 AI 自动篡改线上正式资产造成的不可逆破坏。
- `FR-CHANGE-007` 变更影响分析任务一旦完成，必须在后台监听器中捕获其事件，并自动向**“待办中心（Module: 待办中心）”**注册一条来源为 `CHANGE_IMPACT_REVIEW` 的待办事项，形成人工闭环流转。
- `FR-CHANGE-008` 变更中心必须能跳转到来源需求、接口、元素、case、报告和待办。
- `FR-CHANGE-009` 变更中心不得直接自动修改正式 case、接口或需求事实源。
- `FR-CHANGE-010` `RequirementDiff` 是需求层差异事实，`ChangeRecord` 是跨模块影响分析事实；变更中心必须消费 `RequirementDiff`，而不是重复生成另一套需求差异结论。
- `FR-CHANGE-011` 变更中心必须输出受影响的 case、接口、元素、报告、覆盖矩阵项和回归推荐，并标明影响依据来自需求差异、接口 diff、元素变化、App 版本或报告趋势。
- `FR-CHANGE-012` 变更中心生成的 case 修改、废弃、合并或回归推荐必须进入 CaseGenerationPlan、ChangeCaseDraft 或待办中心，由人工确认后才更新正式资产。

### 13.5 Acceptance Criteria

- `AC-CHANGE-001` Given 新需求版本入库，When 变更中心生成记录，Then 记录关联来源需求、模块和变更摘要。对应 `FR-CHANGE-001`、`FR-CHANGE-002`。
- `AC-CHANGE-002` Given 接口契约发生变更，When 系统完成多维拓扑追踪，Then 变更树状图上精准展示出所有直接调用该 API 及受间接拓扑链影响的 case 列表，且列出影响依据。对应 `FR-CHANGE-003.1`、`FR-CHANGE-004`。
- `AC-CHANGE-003` Given 系统基于变更自适应生成了用例步骤修改草稿，When 用户未在待办中心点击“确认合并”，Then 正式 case 数据 100% 保持原样，仅在修改历史中保存对比。对应 `FR-CHANGE-006.1`、`FR-CHANGE-006.2`、`FR-CHANGE-009`。
- `AC-CHANGE-004` Given 变更影响需要人工处理，When 分析完成，Then 待办中心生成对应待办并可跳转回变更详情。对应 `FR-CHANGE-007`、`FR-CHANGE-008`。
- `AC-CHANGE-005` Given 需求中心生成 `RequirementDiff`，When 变更中心消费差异，Then 变更记录引用该差异并展示跨模块影响，不重复生成独立需求差异。对应 `FR-CHANGE-010`。
- `AC-CHANGE-006` Given 变更中心建议修改、废弃或回归 case，When 用户未确认，Then 正式资产保持不变，并生成生成计划项、修改草稿或待办。对应 `FR-CHANGE-011`、`FR-CHANGE-012`。

### 13.6 Guardrails

- 变更中心不得自动修改正式资产。
- 影响分析必须展示依据，不得只输出建议列表。
- 回归推荐必须允许人工调整。
- **防止图谱循环引用**：在追踪递归有向图时，必须内置深度限制（最大 Trace 深度 <= 5）和环路检测算法（Cycle Detection），防止由于场景编排用例循环引用而导致的堆栈溢出。
- 变更中心不得重复定义需求差异事实；需求差异以 `RequirementDiff` 为准，变更中心只承接影响分析和行动建议。

### 13.7 Data / API / UI Implications

- **数据对象**：包括 ChangeRecord、ChangeImpactGraph、ChangeCaseDraft、RegressionRecommendation、RequirementDiffImpactLink。
- **API**：需要覆盖变更记录入库、RequirementDiff 消费、拓扑分析触发、RAG 语义召回、回归推荐生成、修改草稿生成与双活应用合并、待办状态流转关联。
- **UI**：采用“变更分析大地图”工作台：左侧为版本变更历史与类型分类，中间为交互式的有向拓扑树（不同节点的受损状态使用红黄绿等颜色渲染，显示直接受累和间接受累路径），右侧为选中节点的“自适应修改草稿”预览、正式步骤对比、覆盖矩阵影响及一键确认入口。

### 13.8 AI Evaluation Strategy

- 影响分析需要评估召回准确率、受影响 case 命中率和人工采纳率。
- case 修改草稿需要经过覆盖度和可执行性评估，并要求人工确认。

### 13.9 Open Questions

- 变更类型枚举和默认状态流转需要在原型或技术设计中细化。

---

## 14. Module: 待办中心

### 14.1 Intent

待办中心是一级模块，负责统一承接需要人工判断、确认、修改或复核的质量事项。它不是复杂流程引擎，但必须提供清晰的待办来源、状态、重要性、关联对象和处理入口。

### 14.2 Problem

AI case 待确认、需求冲突、失败报告复核、元素失效、flaky case、变更影响、设备异常和 AI 低分如果分散在各模块，测试人员很容易遗漏处理，质量闭环无法完成。

### 14.3 User Stories

- 作为测试人员，我想在待办中心看到所有需要我确认或处理的事项，以便不用逐个模块查找。
- 作为测试经理，我想看到待办数量、处理状态和阻塞事项，以便判断当前版本风险。
- 作为测试人员，我想从待办跳转到来源对象并处理后回写状态，以便形成闭环。
- 作为平台维护者，我想待办有标准来源和状态，以便后续接入 Agent 或通知能力。

### 14.4 Functional Requirements

- `FR-TODO-001` 待办中心必须支持标准待办对象，包含来源类型、来源对象、标题、描述、重要性、风险级别、状态、处理人占位、创建时间和更新时间。
- `FR-TODO-002` **待办来源与自动事件注册机制**：
  - `FR-TODO-002.1` **待办事件源注册**：待办事件必须由下游业务模块主动发布并触发注册。至少包括：需求冲突/模糊点登记（`REQ_CONFLICT`）、AI case 草稿待确认（`AI_CASE_DRAFT_PENDING`）、Evaluator 质量评估低分/严重警告（`AI_LOW_SCORE`）、移动端执行定位失效（`ELEMENT_STALE`）、失败报告未复核（`FAILURE_REPORT_REVIEW`）、由于 flaky 被强制标记的用例复审（`FLAKY_CASE_REVIEW`）、App 版本或接口契约更新造成的影响范围（`CHANGE_IMPACT_REVIEW`）、Android 执行机掉线/异常终止（`DEVICE_EXCEPTION`）。
  - `FR-TODO-002.2` **状态核销闭环与自清洗机制 (Auto-Reconciliation & Self-Cleaning)**：为杜绝“同一事项跨页面双重操作”的技术债，系统必须支持强核销监听。一旦在来源业务模块完成最终决策，待办中心必须 100% 自动将对应的 `TodoItem` 置为 `resolved` 状态并移入已归档视图。包括：
    - 当测试人员在“Case 中心”接受、拒绝或合并某条 AI 用例草稿后，关联的 `AI_CASE_DRAFT_PENDING` 待办必须在同一个数据库事务（或事件总线）内自动核销。
    - 当产品经理在“需求中心”对存在冲突/模糊的需求文档进行重新解析或点击“手动澄清入库”后，对应的 `REQ_CONFLICT` 待办自动核销。
    - 当测试开发工程师在“移动端执行中心”对报错元素更新定位并点击“应用修复”后，关联的 `ELEMENT_STALE` 待办自动核销。
    - 当异常报告关联的流水任务，经过人工重跑（Re-run）并全量通过后，上一批次未复核的 `FAILURE_REPORT_REVIEW` 待办自动核销，状态流转为 `dismissed_by_repass`。
- `FR-TODO-003` 待办状态必须至少覆盖 pending（待处理）、in_progress（处理中）、resolved（已核销）、dismissed（手动忽略）、blocked（被阻塞）。
- `FR-TODO-004` 待办必须能跳转到来源模块和来源对象。
- `FR-TODO-005` 待办手动忽略（Dismiss）或阻塞（Block）时，前台必须强制要求输入原因（字数 >= 10 字），并记录于 `TodoActionLog` 中。
- `FR-TODO-006` 待办中心必须支持按来源、状态、重要性、风险级别、项目和模块筛选。
- `FR-TODO-007` 待办中心不要求复杂分配、审批流和 SLA，但需要保留后续扩展字段。
- `FR-TODO-008` 待办中心必须能被首页聚合展示，且支持 SSE (Server-Sent Events) 或 WebSockets 实时向前台推送待办计数更新。
- `FR-TODO-009` 待办中心必须新增需求覆盖闭环来源，至少包括需求阻断问题、覆盖缺口、CaseGenerationPlan 待确认、case 更新 / 废弃待确认、自动化候选资产缺失、接口变更影响和高风险 AI 草稿 / Evaluator 低分。
- `FR-TODO-010` 待办中心只承接人工复核和处理入口，不得直接绕过来源模块校验修改正式需求、正式 case、接口定义、覆盖矩阵或报告结论。

### 14.5 Acceptance Criteria

- `AC-TODO-001` Given AI case 草稿需要确认，When 草稿生成成功，Then 待办中心出现 AI case 待确认事项。对应 `FR-TODO-002.1`。
- `AC-TODO-002` Given 用户点击待办，When 来源对象存在，Then 平台跳转到对应模块详情页。对应 `FR-TODO-004`。
- `AC-TODO-003` Given 用户手动忽略（Dismiss）待办，When 提交保存，Then 平台校验输入理由，若不符合规范（少于 10 字）则提示拦截，通过后标记为 `dismissed`。对应 `FR-TODO-005`。
- `AC-TODO-004` Given 用户在 Case 库中对某条 AI case 草稿执行了“拒绝并沉淀负样本”，When 操作成功，Then 待办中心关联的 `AI_CASE_DRAFT_PENDING` 待办状态在后台自动变更为 `resolved`。对应 `FR-TODO-002.2`。
- `AC-TODO-005` Given 待办数量变化，When 系统完成状态更新，Then 通过 SSE 实时推送，首页待办看板入口的计数气泡（Badge）同步刷新。对应 `FR-TODO-008`。
- `AC-TODO-006` Given 覆盖矩阵存在缺口或生成计划待确认，When 来源模块发布待办事件，Then 待办中心展示来源、风险、影响范围和跳转入口。对应 `FR-TODO-009`。
- `AC-TODO-007` Given 用户在待办中心处理 case 废弃、覆盖缺口或自动化候选待办，When 点击处理，Then 平台跳转到来源模块执行校验和保存，待办中心只接收核销结果。对应 `FR-TODO-010`。

### 14.6 Guardrails

- 待办中心不得绕过来源模块的业务校验。
- dismiss 待办必须保留原因。
- 待办状态变更不能直接修改正式 case、需求或报告结论，除非来源模块提供明确处理动作。
- 历史已核销（resolved）与已忽略（dismissed）的待办在 14 天后自动移入历史归档分区，避免默认视图性能退化。
- 覆盖缺口、生成计划确认和自动化候选待办不得被简单“完成”替代来源模块处理；必须保留来源模块的处理结果和证据。

### 14.7 Data / API / UI Implications

- **数据对象**：包括 TodoItem、TodoSourceRelation、TodoActionLog、TodoResolutionEvidence（待办操作日志表：增加 `rejection_reason/dismiss_reason`，`action_type`，`operator_id` 字段）。
- **API**：需要覆盖待办创建（事件监听器接收端）、批量查询、状态流转（处理/忽略/挂起）、SSE/WebSocket 计数推送、来源详情穿透接口、来源模块处理结果回写。
- **UI**：统一人工复核工作台：左侧按来源大类和紧急度卡片进行聚合过滤，中间为待办简要信息和可触发现场处理的快捷动作，右侧支持抽屉展示来源对象（例如：直接在抽屉里显示接口文档、报错截图、覆盖缺口、生成计划或 RAG 解析冲突片段），支持跳转来源模块完成“澄清/确认/修复”并回写核销。

### 14.8 AI Evaluation Strategy

- Agent 可推荐待办处理顺序，但必须解释依据，例如风险级别、阻塞链路、失败次数和影响范围。
- AI 推荐不得自动关闭待办。

### 14.9 Open Questions

- 待办状态流转是否需要加入 assignee 和 due date，当前只保留扩展字段。

---

## 15. Module: 系统设置

### 15.1 Intent

系统设置负责平台运行所需的配置、检测和安全边界，包括模型、Prompt、Skill、门禁、环境、Appium capability、报告保留、脱敏和基础权限配置占位。

### 15.2 Problem

如果 AI 模型、环境、Appium、报告策略和脱敏规则散落在业务页面，会导致配置不一致、排障困难和密钥泄露风险。配置未经检测即生效，也会影响主流程稳定性。

### 15.3 User Stories

- 作为平台管理员，我想配置模型 provider、model、base_url、api_key 和连接检测，以便 AI 功能稳定可用。
- 作为平台管理员，我想配置环境、headers、Appium capability 和报告策略，以便执行任务有统一默认配置。
- 作为平台管理员，我想配置脱敏规则和报告保留策略，以便控制敏感数据风险。
- 作为平台管理员，我想保留基础权限配置占位，以便后续开启真实鉴权时有明确边界。

### 15.4 Functional Requirements

- `FR-SET-001` 系统设置必须支持模型配置，字段包括 provider、model、api_key、base_url、temperature、max_tokens、timeout、enabled。
- `FR-SET-002` API Key 只允许写入，不允许明文返回；前端只展示 masked key。
- `FR-SET-003` 编辑已有模型时，空 API Key 不得覆盖已保存密钥。
- `FR-SET-004` 启用模型必须最近一次连接检测通过。
- `FR-SET-005` 连接检测必须区分 passed、failed、timeout、invalid_config，并展示可行动失败原因。
- `FR-SET-006` 系统设置必须支持环境配置，包括 HTTP base url、WebSocket base url、model endpoint、login_api 和 default headers。
- `FR-SET-007` 系统设置必须支持 Appium capability 模板，并允许设备级、App 级、任务级覆盖。
- `FR-SET-008` 系统设置必须支持报告保留、产物保留、自动清理、导出格式和导出脱敏策略。
- `FR-SET-009` 系统设置必须支持敏感字段规则，覆盖 Authorization、Cookie、token、password、手机号、身份证等字段。
- `FR-SET-010` 系统设置保留基础权限配置占位，但当前不要求所有业务模块完成真实鉴权。
- `FR-SET-011` 危险操作必须二次确认并记录操作日志。
- `FR-SET-012` 当任何业务功能触发 AI 调用时，必须使用当前已启用且连接检测通过的模型配置；若运行时发现连接失败、鉴权失败、模型不存在、base_url 不通、超时或 invalid_config，平台必须直接弹窗报错并阻断该 AI 任务，不得回退到默认文案、规则模板、历史缓存、空结果或模拟结果。

### 15.5 Acceptance Criteria

- `AC-SET-001` Given 管理员保存模型配置，When API Key 有值，Then 后端保存密钥，前端只展示 masked key。对应 `FR-SET-001`、`FR-SET-002`。
- `AC-SET-002` Given 管理员编辑模型但 API Key 留空，When 保存，Then 已保存密钥不被覆盖。对应 `FR-SET-003`。
- `AC-SET-003` Given 模型连接检测失败，When 用户查看结果，Then 平台展示 failed、timeout 或 invalid_config 及可行动原因。对应 `FR-SET-004`、`FR-SET-005`。
- `AC-SET-004` Given 报告导出或 AI 输入包含敏感字段，When 脱敏规则启用，Then 平台按规则脱敏。对应 `FR-SET-008`、`FR-SET-009`。
- `AC-SET-005` Given 用户执行危险操作，When 点击确认，Then 平台进行二次确认并记录操作日志。对应 `FR-SET-011`。
- `AC-SET-006` Given 用户触发需求解析、case 生成或其他 AI 功能，When 当前启用模型运行时连接失败或配置错误，Then 平台通过统一弹窗展示失败原因并阻断任务，不生成任何降级结果。对应 `FR-SET-012`。

### 15.6 Guardrails

- 密钥不得明文返回前端。
- 连接检测失败的模型不得设为启用模型。
- 配置检测或验证失败时不得静默生效。
- AI 连接失败或连接错误不得静默降级，不得产出看似成功的解析、生成、评估或分析结果。
- 当前权限只做配置占位，不应在 PRD 中假设业务模块已完成完整鉴权。

### 15.7 Data / API / UI Implications

- 数据对象包括 AppSettings、ModelConfig、EnvironmentConfig、AppiumCapabilityTemplate、ReportPolicy、MaskingRule、PermissionPlaceholder。
- API 需要覆盖配置读取、保存、连接检测、脱敏规则、报告策略和操作日志。
- UI 建议使用 Tab：AI 模型、环境配置、Appium、报告策略、安全脱敏、权限占位。

### 15.8 AI Evaluation Strategy

- 模型连接检测结果进入 AI 能力中心的模型可用性统计。
- AI 调用失败率和成本不在系统设置展示，归 AI 能力中心展示。

### 15.9 Open Questions

- 基础权限占位字段是否需要提前设计为角色、用户、项目权限三层，待技术设计确认。

---

## 16. Future Module: Bug 中心

### 16.1 Intent

Bug 中心是未来完整模块，用于承接缺陷记录、外部缺陷平台同步、bug 修复影响分析和回归闭环。当前平台只要求在变更中心、待办中心和数据模型中保留未来接入边界，不要求开发独立页面或外部同步。

### 16.2 Problem

bug 修复会影响需求、case、接口、元素和回归范围。如果平台完全没有 bug 边界，未来接入缺陷系统时会难以把缺陷修复和测试资产关联起来。

### 16.3 Future User Stories

- 作为测试人员，我想把失败报告转成 bug，以便研发修复后能关联回归 case。
- 作为测试经理，我想看到 bug 修复影响了哪些需求和 case，以便安排回归。
- 作为研发负责人，我想看到 bug 修复后的验证状态，以便判断修复是否闭环。

### 16.4 Future Functional Requirements

- `FR-BUG-001` 未来 Bug 中心应支持 bug 记录、状态、严重级别、来源报告、关联 case 和修复版本。
- `FR-BUG-002` 未来 Bug 中心应支持外部缺陷平台 connector 和双向同步。
- `FR-BUG-003` bug 修复应进入变更中心，触发影响分析和回归推荐。
- `FR-BUG-004` bug 验证应能关联执行报告和回归 case。

### 16.5 Current Boundary

当前不开发 Bug 中心页面、不做外部平台同步、不要求业务模块保存完整 bug 字段。当前只在变更来源、待办来源和未来扩展说明中保留 bug 修复概念。

---

## 17. Cross-module User Flows

### 17.1 需求到 case

```text
需求文档上传
 -> 原文预览和需求树挂载
 -> AI 解析、结构化需求点和文档问题项检查
 -> 查询同业务域 / 模块 / 功能历史基线
 -> 生成 RequirementDiff
 -> 处理冲突 / 缺失 / 模糊 / 删除 / 验收变化 / 接口契约变化
 -> 人工确认入库并更新 RequirementBaseline
 -> 生成 CoverageMatrix
 -> 生成并确认 CaseGenerationPlan
 -> 按计划生成 AI case 草稿
 -> Evaluator 门禁
 -> 人工接受 / 编辑后接受 / 拒绝 / 合并
 -> 正式 case 资产
 -> Case 中心展示来源差异、覆盖状态、生成计划、版本、确认记录和执行摘要
```

必须成立：

- 检查未通过、差异未分析或覆盖矩阵缺失的文档不能生成 case 草稿。
- AI case 草稿必须来自 `CaseGenerationPlan`。
- AI case 草稿不能绕过人工确认。
- 正式 case 必须能追溯需求点、RequirementDiff、CoverageMatrix、CaseGenerationPlan 和原文片段。

### 17.2 接口 case 到报告

```text
接口文档导入
 -> 接口解析和人工确认
 -> 平台内接口事实源
 -> 接口定义版本和字段 diff
 -> RequirementDiff / 变更中心承接接口契约变化
 -> CaseGenerationPlan 决定新增、更新、废弃或保留接口 case
 -> 接口 case 步骤引用已确认接口定义
 -> 执行前选择环境和变量
 -> ApiRunner 执行
 -> 断言和变量提取
 -> 执行中心记录任务状态和重试
 -> 执行结果回写 CoverageMatrix
 -> 报告中心输出 HTML 报告、覆盖摘要和证据链
```

必须成立：

- 接口废弃后关联 case 不得执行。
- 接口 case 必须绑定接口定义、接口文档解析结果或接口 diff。
- 执行失败最多自动重试 3 次。
- 报告必须包含 request、response、assertion、log 和需求 / 接口覆盖证据。

### 17.3 Android 移动端执行到报告

```text
Android 设备识别
 -> App package / version / build 记录
 -> 页面 XML 导入
 -> 元素绑定
 -> AutomationCandidate 检查元素、App、设备、测试数据和断言依赖
 -> 移动端 case 步骤引用元素和来源功能 / 接口 case
 -> 单设备执行
 -> 截图 / XML / Appium 日志采集
 -> 执行结果回写 CoverageMatrix
 -> 报告中心输出移动端证据链和自动化候选落地状态
```

必须成立：

- 正式移动端 case 必须引用元素库。
- 自动化脚本 case 必须绑定功能 case 或接口 case。
- 自动化资产依赖不完整时不得进入正式可执行资产。
- 设备异常后必须释放设备锁。
- 移动端报告必须绑定 App package、version、build。

### 17.4 变更到回归推荐

```text
RequirementDiff / 接口 diff / 元素 / App / bug 修复变化
 -> 变更中心记录 ChangeRecord
 -> RAG 召回和拓扑追踪相关资产
 -> 影响 case / 接口 / 元素 / 报告 / 覆盖矩阵分析
 -> 回归推荐、生成计划项和 case 修改草稿
 -> 待办中心生成复核事项
 -> 人工确认后生效
 -> 执行中心创建回归执行集
 -> 报告中心展示新需求覆盖和历史回归结果
```

必须成立：

- 变更中心不得自动修改正式资产。
- 需求层差异事实以 `RequirementDiff` 为准，变更中心只承接影响分析。
- 待办中心承接人工复核。
- 回归推荐必须展示依据并允许人工调整。

### 17.5 覆盖缺口到待办闭环

```text
CoverageMatrix 发现 not_covered / partial_covered / outdated / need_update / need_deprecate
 -> 生成覆盖缺口、case 更新 / 废弃或自动化候选待办
 -> 来源模块完成处理和校验
 -> 待办中心核销并保留处理证据
 -> CoverageMatrix 更新覆盖状态
 -> 首页和报告中心同步覆盖指标
```

必须成立：

- 待办中心不能直接修改正式需求、case、接口或报告结论。
- 覆盖缺口不能通过简单核销消失，必须有来源模块处理结果、忽略理由或风险接受记录。

## 18. Global Guardrails

- AI 输出影响正式资产时，必须通过评估和人工确认。
- 检查未通过的需求文档或接口文档不得生成 case 草稿。
- 没有历史基线对比或首次基线人工确认，不允许批量生成 case。
- 没有 RequirementDiff，不允许进入覆盖矩阵和生成计划。
- 没有 CoverageMatrix，不允许批量接受 AI case 草稿。
- case 生成必须来自 CaseGenerationPlan。
- 自动化脚本 case 必须绑定功能 case 或接口 case。
- 接口 case 必须绑定接口定义、接口文档解析结果或接口 diff。
- 正式 case 必须能追溯来源需求、接口、元素、AI 依据、确认人和最近执行记录。
- Runner 不得直接修改需求、case 或报告主表。
- Evaluator 不得替代人工确认。
- AI 不得使用降级逻辑替代真实调用；AI 失败必须显式失败并提示用户。
- 取消任务不生成正式报告。
- 报告导出默认脱敏。
- 密钥不允许明文返回。
- 自动生成的 case 修改草稿必须人工确认后才生效。
- 系统不得自动删除 case。
- Bug 中心当前不开发外部同步和页面。

## 19. Non-goals

当前不做：

- iOS 自动化。
- 云真机和远程设备池。
- 多设备并发调度。
- AI 视觉定位兜底。
- Web 自动化独立建设。
- 完全自由脚本执行模式。
- 复杂拖拽式低代码编排。
- 录制回放。
- 定时回归、CI/CD 自动触发和发布门禁。
- 外部缺陷平台双向同步。
- Bug 中心独立页面。
- Prompt 回滚。
- 所有业务模块的真实权限鉴权。

## 20. Product Metrics

- 需求解析成功率。
- 需求检查问题命中率。
- 历史需求差异识别准确率。
- 覆盖矩阵需求点覆盖完整率。
- 覆盖缺口处理闭环率。
- 需求到 AI case 草稿耗时。
- 需求到 CaseGenerationPlan 确认耗时。
- AI case 草稿采纳率。
- AI case 字段完整率。
- 新需求覆盖率。
- 历史需求回归通过率。
- 自动化候选落地率。
- 正式 case 来源追溯完整率。
- 接口定义字段完整率。
- 接口单 case 执行成功率。
- Android 单 case 稳定率。
- 报告可复盘率。
- 待办处理闭环率。
- 变更影响 case 识别准确率。
- AI 调用失败率、token、耗时和估算成本。

## 21. Release Readiness Checklist

- 需求文档上传、解析、检查、确认入库链路可运行。
- 检查未通过的文档不能生成 case。
- RequirementBaseline、RequirementDiff、CoverageMatrix 和 CaseGenerationPlan 链路可运行。
- 未完成历史基线对比、差异分析或覆盖矩阵时不能批量生成 / 接受 case。
- AI case 草稿生成、门禁、人工确认、拒绝和正式入库链路可运行，且草稿必须来自生成计划。
- Case 中心能展示来源、状态、版本、确认记录和最近执行。
- Case 中心能展示覆盖状态、来源差异、生成计划和自动化候选状态。
- 接口定义导入、确认、单接口调试和接口 case 执行链路可运行。
- 接口定义版本 diff 能进入变更影响分析或覆盖矩阵。
- Android 设备识别、App 绑定、元素导入、移动端 case 执行和移动端报告链路可运行。
- 自动化脚本 case 生成前能完成 AutomationCandidate 评估。
- 执行中心能统一展示任务状态、日志、重试、取消和失败建议。
- 执行结果能回写 CoverageMatrix，报告能展示需求差异覆盖证据。
- 报告中心能输出 HTML 报告和关键证据链。
- AI 能力中心能记录 AI 输入、输出、历史基线、差异、覆盖矩阵、生成计划、评估、人工确认和成本。
- 变更中心能消费 RequirementDiff 并输出影响 case、覆盖矩阵项和回归建议。
- 待办中心能聚合 AI case、失败报告、元素失效、覆盖缺口、生成计划、自动化候选和变更影响等人工复核事项。
- 系统设置能完成模型连接检测、密钥掩码、报告脱敏和 Appium / 环境配置。
- 全局敏感字段在报告、日志、AI 输入和 RAG 入库前被脱敏。

## 22. Open Questions

- 需求树页面如何最直观表达业务域 -> 模块 -> 功能 -> 需求版本 -> 验收点。
- Prompt 修改验证使用完整评估集还是轻量冒烟集。
- Evaluator 阈值的模块和风险等级枚举如何定义。
- RequirementDiff 相似度阈值、冲突判定规则和验收标准变化识别规则如何定义。
- CoverageMatrix 覆盖评分、部分覆盖和重复覆盖规则如何定义。
- CaseGenerationPlan 的默认生成策略和批量确认边界如何定义。
- AutomationCandidate 的可行性等级、资产依赖和阻塞原因枚举如何定义。
- 待办状态是否需要加入 assignee、due date 和 SLA。
- 变更类型枚举和默认状态流转如何定义。
- 报告默认保留 14 天是否符合团队实际需要。
- 基础权限占位字段是否提前设计为角色、用户、项目权限三层。

## 23. PRD 一致性检查结论

### 23.1 内部逻辑冲突检查

- `FR-REQ-007` 原有“历史需求对比”已升级为 `RequirementBaseline` 和 `RequirementDiff` 的结构化事实链路，避免停留在解析阶段的自然语言摘要。
- `FR-CASE-004` 原有“AI case 草稿”已补充为必须来自 `CaseGenerationPlan`，不再允许从文档直接绕过计划生成可接受草稿。
- `FR-CHANGE-*` 与 `RequirementDiff` 的职责已拆分：`RequirementDiff` 负责需求层差异事实，`ChangeRecord` 负责跨模块影响分析和行动建议，不重复定义事实源。
- `FR-API-*` 已明确接口中心是接口事实源，接口 case 必须绑定接口定义、接口文档解析结果或接口 diff，需求中心不是接口 case 的唯一来源。
- `FR-TODO-*` 已明确待办中心只承接人工复核和处理入口，不直接修改正式需求、正式 case、接口定义、覆盖矩阵或报告结论。
- AI no-fallback 规则已在 AI 能力中心、系统设置、需求中心和全局护栏中保持一致：AI 连接、鉴权、模型、超时或配置失败时必须显式失败并提示用户，不得用模板、规则、缓存或模拟结果降级。

### 23.2 本轮目标逻辑对照

- 历史基线：已定义 `RequirementBaseline`，并在需求入库、差异分析、首页指标、AI 上下文和发布验收中引用。
- 差异分析：已定义 `RequirementDiff`，覆盖新增、修改、删除、冲突、验收标准变化、接口契约变化、权限变化、流程变化和边界变化。
- 覆盖矩阵：已定义 `CoverageMatrix`，并约束 case 生成、批量接受、执行回写、报告覆盖证据和待办缺口闭环。
- 生成计划：已定义 `CaseGenerationPlan`，并要求功能 case、接口 case、自动化脚本 case 都从计划产生。
- 分类型 case 草稿：已分别补充 functional_case、api_case、automation_script_case 的来源、绑定关系、门禁和自动化候选逻辑。
- 历史需求不遗漏：已通过基线对比、覆盖矩阵、历史回归覆盖率、报告覆盖摘要和首页指标形成闭环。
- AI 不降级：已明确 AI 失败直接报错，且任何 AI 输出不能绕过差异、覆盖矩阵、生成计划和人工确认。
- 其他模块联动：首页、接口、移动端、执行、报告、AI、变更、待办和系统设置已同步补充数据 / API / UI 和 Guardrails 影响。

### 23.3 仍需产品确认的开放点

- `RequirementDiff` 的相似度阈值、冲突判定规则和验收标准变化识别规则需要在原型或技术设计中细化。
- `CoverageMatrix` 的覆盖评分、部分覆盖、重复覆盖和风险接受规则需要形成可配置策略。
- `CaseGenerationPlan` 的默认生成策略、批量确认边界和人工编辑权限需要在交互设计中明确。
- `AutomationCandidate` 的可行性等级、资产依赖和阻塞原因枚举需要结合自动化工程实践定义。

## 24. PRD 完成度自检

- [x] 问题陈述以用户和测试工作流为中心。
- [x] 每个功能模块集中描述目标、用户、需求、验收、护栏和影响。
- [x] 功能需求使用稳定编号。
- [x] 验收标准使用 Given / When / Then 并映射需求编号。
- [x] AI 功能包含评估策略和人工确认边界。
- [x] Non-goals 明确保护范围。
- [x] Guardrails 明确不可绕过规则。
- [x] 待确认问题集中在文末，便于后续澄清。

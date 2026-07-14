# AI测试平台需求中心与Case中心安全攻防分析报告（只读红队评估）

> **归档状态：阶段性报告。** 后续修复和验收状态以 [RC-10 验收证据](../../delivery/RC-10验收证据.md) 及当前自动化测试为准；产品要求以 [PRD](../../product/AI测试平台PRD.md) 为准。本文不再作为现行缺口清单。

**版本**：v1.0
**文档角色**：安全攻防阶段一（只读红队评估结论）
**评估基准**：`docs/product/AI测试平台PRD.md` & `docs/product/AI测试平台模块功能逻辑确认.md`
**整理方法**：对照PRD与功能代码、测试代码进行只读审计，挖掘设计漏洞、API绕过路径、一致性缺陷与功能缺口。

---

## 一、 攻防概述

红队（攻击方）在保持代码只读的前提下，通过对 FastAPI 后端路由层、服务层、数据库模型层以及测试套件的静态代码审计，发现了 **8个严重安全对齐漏洞**。这些漏洞不仅能够导致安全数据泄露，更可被直接调用 API 恶意绕过所有“人工确认”与“质量门禁”拦截，污染正式测试资产库，导致质量驾驶舱指标完全失真。

---

## 二、 攻击点分析矩阵（阶段一：红队输出）

| 严重级别 | 攻击点 | PRD 依据 | 代码证据 | 复现路径 | 影响 | 建议测试 | 修复建议 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **CRITICAL (紧急)** | **1. 绕过门禁直接创建关联非存储状态需求的正式Case漏洞** | `FR-REQ-009` 检查未通过需求不得生成用例；`FR-REQ-010` 检查通过并经人工确认后，结构化需求点才能落档作为用例生成输入。 | `CaseService.create_case` 无任何对 `source_document_id` 状态的判断，直接写入正式 `test_cases` 表。 | 1. 上传一个解析状态为 `unparsed` 或检查失败 `check_failed` 的文档。<br>2. 越过前端，直接使用 HTTP 客户端向 `POST /api/cases/` 发送请求，其中 `source_document_id` 填入该未入库文档的 ID。<br>3. 数据库成功保存用例并直接进入正式库。 | 门禁形同虚设。任何含有冲突、缺失、模糊逻辑的需求或直接被废弃的文档，均可以通过直接 API 调用源源不断生成正式用例，严重污染资产库。 | 编写测试 `test_case_creation_fails_for_unstored_document`，断言当关联文档状态非 `stored` 时，用例创建 API 必须返回 400 阻断。 | 在 `CaseService.create_case` 与 `update_case` 中加入强制校验：若传入 `source_document_id`，必须执行 `RequirementDocService.assert_can_generate_cases(doc_id)`。 |
| **HIGH (高危)** | **2. 越过AI门禁及评估强行注入伪造AI草稿漏洞** | `Global Guardrails` AI 输出影响正式资产时，必须通过评估和人工确认。<br>`FR-CASE-004` AI case草稿必须进入待确认队列。 | `CaseService.sync_ai_cases` 和 `AICaseDraftService.create_drafts_from_cases` 直接接收用户任意构造的 `cases` 列表 payload 并写入草稿库。 | 1. 越过 LLM 生成与 Phoenix 门禁评估，直接向 `POST /api/cases/sync-from-ai` 发送任意伪造的用例 JSON 列表。<br>2. 后端未核对生成凭证，直接将伪造数据作为 `status="pending"` 的 AI 草稿写入。 | 恶意攻击者可以绕过大模型与门禁评分，直接向系统内灌入垃圾用例或包含恶意代码/越权测试步骤的伪造“AI草稿”，引导测试人员误点击通过。 | 编写测试，发送不符合 QA 用例规范的假数据至 `/sync-from-ai`，断言门禁进行结构化字段和来源校验，并在 document_id 为空/失效时阻断。 | 1. 校验同步请求中的 document_id 必须为 active 且 stored；<br>2. 增加对 `cases` payload 的 Schema 严格校验；<br>3. 限制此 API 仅能被内部微服务或大模型服务安全调用。 |
| **HIGH (高危)** | **3. 越权直接篡改用例可信度与生命周期状态漏洞** | `FR-CASE-003` 统一管理用例可信分层；<br>`Global Guardrails` 严禁 AI 或非授信操作直接篡改正式用例状态，必须人工确认。 | `TestCaseUpdate` Schema 暴露了 `trust_status`（可信分层）和 `is_active` 字段，且 `CaseService.update_case` 使用 `setattr(case, field, value)` 盲目更新。 | 1. 调用 `PUT /api/cases/{case_id}`，在 payload 中传入 `{"trust_status": "high_value"}` 或 `{"trust_status": "verified"}`。<br>2. 用例在未经任何真实自动化执行通过的情况下，被直接标记为高价值/已验证回归资产。 | 测试经理无法相信指标。任意普通、Flaky、未经验证的用例，均可以通过 API 被任意篡改升级为“高价值/已验证”状态，从而误导回归推荐。 | 编写测试 `test_update_case_trust_status_direct_write_blocked`，发送 `trust_status` 更新请求，断言后端报错或拦截直接篡改。 | 从 `TestCaseUpdate` 开放 Schema 中移除 `trust_status` 与 `is_active`（应通过专门的核销/执行接口触发升级），或在后端服务层加入严格的状态转移权限校验。 |
| **HIGH (高危)** | **4. 关键执行逻辑篡改免复核漏洞 (修改步骤不重置)** | `FR-CASE-009` / `AC-CASE-004` 步骤、断言、来源、接口或元素变更必须重新确认或验证。 | `CaseService.update_case` 中仅在 `case.source == "ai_generated"` 且触碰 `critical_fields` 时才重置 `pending_reconfirm = 1`。如果是 `source == "manual"` 则完全不予理会。此外，`expected_result`（预期结果）与 `precondition`（前置条件）完全不在 `critical_fields` 拦截名单中。 | 1. 创建一个 manual 来源且可信状态为 `verified` 的用例。<br>2. 调用 `PUT /api/cases/{case_id}` 修改其 `steps` 步骤、期望结果或前置条件。<br>3. 用例状态毫无变化，完全不会被置为 `pending_reconfirm`。 | 核心执行逻辑、断言已被大幅物理改动，但在资产库中仍标记为“已验证安全”资产。自动化执行或人工回归时，将直接运行已被篡改的错误逻辑，隐藏严重回归 Bug。 | 1. 编写测试，对 manual 来源用例修改步骤，断言其重置为 `pending_reconfirm=1` 且 trust_status 降级为 `formal`；<br>2. 编写测试对预期结果和前置条件修改，断言触发重置。 | 1. 移除 `source == "ai_generated"` 的限制，对所有来源的用例篡改均一视同仁重置；<br>2. 将 `precondition`、`expected_result`、`description` 补充进 `critical_fields`。 |
| **HIGH (高危)** | **5. 拒绝AI草稿“伪反馈闭环”漏洞 (负样本流失与RAG失效)** | `FR-CASE-005.1` 至 `FR-CASE-005.4`：拒绝草稿必须强制收集 `rejection_category` 结构化原因和长度 >= 10 字理由；沉淀安全脱敏的负样本并写入 RAG 向量数据库实现负向少样本学习（Few-Shot Negative Learning）和门禁相似度 0.85 拦截。 | 1. `RejectDraftRequest` 和 `AICaseDraft` 模型完全缺失结构化字段；<br>2. 没有任何安全脱敏与 RAG 向量数据库写入代码；<br>3. `CaseGenerateSkill` 根本没有读取和组装负向 Few-Shot Prompt 的逻辑，门禁也无相似度匹配拦截。 | 1. 拒绝 AI 草稿时，传入空原因或 1 字节无意义原因，系统正常接受。<br>2. 被拒绝的错误模式没有经过脱敏和 RAG 沉淀。<br>3. 再次在相同模块生成 case 时，AI 继续犯下完全一模一样的逻辑或格式错误。 | 反馈闭环完全断裂。AI case 生成器成了无记忆的一次性问答框，不仅无法随着人工反馈逐步纠错，还因重复制造已被拒绝的低质用例白白浪费大量 Token 费用和人工复审精力。 | 1. 编写测试，拒绝草稿时传入不合规原因或缺失 category，断言 400 阻断；<br>2. 编写测试断言拒绝后负样本中包含了结构化分类、原始需求，且能被 RAG 正确检索。 | 1. 修改 `AICaseDraft` 和 `NegativeCaseSample` 数据库模型，增加 `rejection_category`、`user_feedback_comment` 等字段；<br>2. 拒绝 API 强制校验入参规范；<br>3. 在 `CaseGenerateSkill` 生成前使用 `RagRetrieveSkill` 捞取相关负样本进行 Prompt Few-Shot 负向引导；<br>4. 在生成门禁中计算相似度，若 >0.85 直接置为 `check_failed`。 |
| **MEDIUM (中危)** | **6. 废弃用例元数据缺失与防错隔离失效漏洞** | `FR-CASE-011.1` 至 `FR-CASE-011.4` 废弃 TestCase 时，必须强制采集废弃大类和详细说明，并关联变更记录或替换用例；在执行和 RAG 推荐中 100% 物理隔离。 | `test_cases` 模型完全缺少 `deprecation_category`、`replaced_by_case_id` 和 `change_record_id` 字段。`CaseService.deprecate_case` 仅简单改写 `lifecycle_status` 和 `is_active`。 | 1. 调用 `/deprecate` 废弃用例，没有任何废弃元数据落库。<br>2. 变更中心在生成新推荐时，无法规避历史已废弃（如 Flaky）的用例模式。 | 1. 无法统计分析资产被废弃的根本原因（如“业务下线”还是“用例不稳定Flaky”）；<br>2. 变更推荐可能再次推荐出此前由于重大技术债而已废弃的用例模式，造成反向重构风险。 | 1. 编写测试调用废弃接口，断言废弃大类校验生效并成功落库；<br>2. 校验执行中心在任何批量/场景执行中，能 100% 自动过滤 `lifecycle_status == "deprecated"` 的用例。 | 1. 修改 `test_cases` 和 `negative_case_samples` 数据库模型，增加废弃分类和关联外键；<br>2. 升级 `/deprecate` 接口，强制要求提供废弃大类和字数合规描述。 |
| **MEDIUM (中危)** | **7. 垃圾孤儿用例数据污染漏洞 (无校验绑定通用池)** | `FR-CASE-001` / `FR-CASE-007` 统一 case 模型，且正式 case 必须追溯来源。人工新增 case 必须选择项目和模块，绑定对应需求点或原文片段。 | `CaseService.create_case` 中，若未传入 `api_id`，会自动调用 `_get_default_api_id()` 绑定到一个系统自动伪造的 `placeholder` 占位接口上，且不验证 `source_document_id`。 | 1. 向 `POST /api/cases/` 发送一个不包含任何步骤、没有 api_id、没有需求来源的空白 case payload。<br>2. 后端成功将其创建并绑定至“通用功能用例池”。 | 正式用例库、回归用例集中混入大量无执行步骤、无来源依据、无模块归属的“幽灵/垃圾”用例，严重干扰质量指标与 RAG 回归推荐精确度。 | 编写测试，发送无 api_id 且无 project_id/需求关联的用例，断言阻断。 | 1. 手动创建用例时强制要求选择有效的 api_id 或项目/模块；<br>2. 增加对 steps 和 expected_result 的非空校验，阻断空白用例入库。 |
| **HIGH (高危)** | **8. 待办中心人工复核与状态核销闭环完全空转漏洞** | `FR-TODO-001` 至 `FR-TODO-008`：待办中心承接需求冲突、草稿待确认、元素失效等 8 种事件源；实现自动状态清洗核销（Self-Cleaning）双重防错，并在首页支持 SSE 实时气泡推送。 | 整个后端/前端代码库中，**完全没有** 任何关于 `TodoItem` 模型、TodoCenter 服务或 SSE/WebSockets 接口的代码。该模块目前完全处于 **100% 缺失状态**。 | 1. 上传一个有冲突的需求导致其解析状态变为 `check_failed`。<br>2. 待办中心没有生成任何 `REQ_CONFLICT` 待办。<br>3. 接受 AI 用例草稿后，没有任何待办被核销。 | 质量闭环崩溃。测试人员根本无法在一个统一工作台看到全量待办任务，导致待确认草稿、冲突需求、失效元素、Flaky用例、设备掉线等重大质量事故被彻底遗忘。 | 1. 编写测试，产生解析失败文档，断言 Todo 库中自动生成 pending 待办；<br>2. 编写测试，接受/拒绝草稿后，断言关联 Todo 自动核销变更为 `resolved`。 | 从零实现 **待办中心 (Todo Center)** 一级模块：<br>1. 创建 `TodoItem` 和 `TodoActionLog` 数据库模型；<br>2. 编写事件监听器，各下游业务触发时自动注册待办；<br>3. 实现自清洗机制：在 Case 接受/拒绝、需求澄清、元素自愈时自动将对应待办核销为 `resolved`；<br>4. 增加 SSE 计数推送接口，使前端能实时更新 Badge。 |

---

## 三、 架构缺口与技术方案设计（蓝队防守思路）

为了完美对齐 `docs/product/AI测试平台PRD.md` 的强硬安全与闭环护栏，蓝队（防守方）将在阶段二实施以下技术架构升级。整个升级采用 **垂直切片（Vertical Slice）** 模式，绝不进行无序的大面积代码篡改，并辅以严密的 TDD 自动化回归测试。

### 3.1 总体架构依赖关系图 (Dependency Map)

```mermaid
flowchart TD
    subgraph reqCenter [需求中心]
        ReqDoc[RequirementDocument] -->|触发解析| ParseRouter[DocumentParseRouterSkill]
        ParseRouter -->|判定状态| ParseStatus{parse_status == 'stored'?}
    end

    subgraph caseCenter [Case中心]
        DraftService[AICaseDraftService] -->|拒绝草稿| RejectAction[拒绝采集弹窗 /reject]
        RejectAction -->|强制采集分类与>=10字理由| NegSample[AiFeedbackSample / SQLite]
        NegSample -->|安全脱敏| MaskingService[MaskingService]
        MaskingService -->|利用 RagRetrieveSkill 进行 Rerank 索引| RagRetrieve[RagRetrieveSkill]

        CaseService[CaseService] -->|创建/更新Case| SourceCheck{校验关联文档是否Stored?}
        ParseStatus -.->|阻断判定| SourceCheck
        SourceCheck -->|通过| SaveCase[保存 TestCase]
        SourceCheck -->|未Stored| BlockAPI[阻断请求 400 Bad Request]

        SaveCase -->|修改关键步骤/断言/前置| ReconfirmAction[自动标记 pending_reconfirm=1 降级为 formal]
    end

    subgraph todoCenter [待办中心 (从零构建)]
        TodoService[TodoService] -->|监听下游事件| TodoItem[TodoItem SQLite]
        ReqDoc -->|check_failed / 冲突| TodoService
        DraftService -->|草稿 pending| TodoService

        DraftService -->|已接受/已拒绝| TodoService
        TodoService -->|状态自清洗核销| TodoItem
    end

    RagRetrieve -->|Few-Shot Negative Learning| LLMGenerate[CaseGenerateSkill / 大语言模型]
    LLMGenerate -->|新草稿相似度比对| SimilarityCheck{相似度 > 0.85 ?}
    SimilarityCheck -->|Yes| CheckFailed[拦截并标记为 check_failed / 进入待确认队列]
    SimilarityCheck -->|No| PendingReview[正常进入 pending_review]
```

### 3.2 数据库模型演进设计 (SQLite DDL)

我们将修改并新增字段，以在数据库层面强硬承接 PRD 的数据对象契约。所有的 DDL 更新将保证兼容 SQLite 且通过 SQLAlchemy ORM 映射。

#### 3.2.1 `test_cases` 表字段扩充
- `deprecation_category` (`String(50)`, nullable): FEATURE_REMOVED (业务下线), REDUNDANT (合并重复), FLAKY (用例不稳定), STALE_LOCATOR (定位失效), OTHER (其他)。
- `deprecation_reason` (`Text`, nullable): 用例废弃的详细文本理由。
- `replaced_by_case_id` (`Integer`, ForeignKey("test_cases.id"), nullable): 被新用例取代的外键。
- `change_record_id` (`Integer`, nullable): 关联导致此用例被废弃的需求/接口变更记录 ID。

#### 3.2.2 `negative_case_samples` 表字段扩充
- `rejection_category` (`String(50)`, nullable): LOGIC_ERROR (逻辑错乱), MISSING_ASSERTION (缺失断言), OUT_OF_SCOPE (越界生成), DUPLICATE (重复用例), HALLUCINATION (幻觉伪造), FORMAT_ERROR (格式规范问题), OTHER (其他)。
- `user_feedback_comment` (`Text`, nullable): >=10 字的详细人工反馈和改进建议。
- `source_requirement` (`Text`, nullable): 原始被提取的需求文本或原文片段。
- `deprecation_category` (`String(50)`, nullable): 标识由于废弃转存而来的大类。

#### 3.2.3 新建 `todo_items` 待办表
- `id` (`Integer`, primary_key=True): 待办自增ID。
- `source_type` (`String(40)`, nullable=False): 事件源（REQ_CONFLICT, AI_CASE_DRAFT_PENDING, ELEMENT_STALE, FAILURE_REPORT_REVIEW, FLAKY_CASE_REVIEW, CHANGE_IMPACT_REVIEW, DEVICE_EXCEPTION, AI_LOW_SCORE）。
- `source_id` (`Integer`, nullable=False): 关联来源业务表的物理 ID (如 `document_id` 或 `draft_id` 或 `case_id`)。
- `title` (`String(200)`, nullable=False): 待办标题。
- `description` (`Text`, default=""): 待办详情与现场快照。
- `importance` (`String(20)`, default="normal"): 重要性 (high/normal/low)。
- `risk_level` (`String(20)`, default="normal"): 风险评级。
- `status` (`String(20)`, default="pending"): 待办状态（pending, in_progress, resolved, dismissed, blocked）。
- `dismiss_reason` (`Text`, default=""): 手动忽略/挂起的原因（强制校验 >= 10 字）。
- `created_at` (`DateTime`, server_default=func.now()): 创建时间。
- `updated_at` (`DateTime`, onupdate=func.now()): 修改时间。

#### 3.2.4 新建 `todo_action_logs` 待办操作日志表
- `id` (`Integer`, primary_key=True)
- `todo_id` (`Integer`, ForeignKey("todo_items.id"))
- `action_type` (`String(30)`)
- `operator` (`String(50)`)
- `reason` (`Text`)
- `created_at` (`DateTime`)

---

## 四、 开发任务拆分与垂直切片规划（阶段二：防守实施）

我们将严格根据 TDD（测试驱动开发）思想，按垂直切片顺序渐进式完成代码的防守和加固。

### [切片一] 数据库模型演进与 DDL 迁移
- **ID**: `blue-db-migration`
- **任务内容**:
  1. 在 `backend/app/models/test_case.py` 中增加用例废弃和变更元数据。
  2. 在 `backend/app/models/negative_case_sample.py` 中增加拒绝结构化、脱敏反馈元数据。
  3. 新增 `backend/app/models/todo.py`，实现 `TodoItem` 和 `TodoActionLog` 实体。
  4. 编写 SQLite 初始化和热升级脚本，自动在测试和本地环境中安全应用 DDL。
- **验证手段**: 运行 `python -m unittest backend/tests/test_case_version.py` 及数据库加载冒烟测试。

### [切片二] 门禁阻断加固：需求关联与 API 直接调用检查
- **ID**: `blue-gate-hardening`
- **任务内容**:
  1. 在 `CaseService.create_case` 和 `update_case` 中新增文档 `stored` 状态强制阻断校验。
  2. 从 `TestCaseUpdate` schema 中移除 `trust_status`、`is_active` 等字段，或者在 API 更新层增加白名单过滤（不允许直接修改 `trust_status` 为 `verified` / `high_value`，除非传入真实验证审计凭证）。
  3. 修改 `AICaseDraftService.create_drafts_from_cases`，严格限制 document_id 字段（若有传入，则断言状态必须为 `stored`）。
- **验证测试**: 编写并运行 `test_case_sync_gate.py`，确保传入 `unparsed`/`check_failed` 的文档 ID 触发 400 Bad Request。

### [切片三] 执行语义篡改自动降级与重置机制
- **ID**: `blue-semantic-reset`
- **任务内容**:
  1. 重构 `CaseService.update_case`。取消 `source == "ai_generated"` 限制，使所有 `TestCase`（无论是 AI 还是手动创建）只要触碰 `critical_fields` 即被置为 `pending_reconfirm = 1` 并降级为 `formal` 可信等级。
  2. 将 `precondition` 和 `expected_result` 扩充入 `critical_fields`（契约执行关键域）。
- **验证测试**: 编写 TDD 失败测试，修改 manual case 的 steps 或 expected_result，断言其降级且 `pending_reconfirm` 被置 1。运行测试至全绿通过。

### [切片四] 负样本闭环：结构化拒绝、安全脱敏与负向少样本注入（Feedback Sinking）
- **ID**: `blue-negative-loop`
- **任务内容**:
  1. 在 `/drafts/{draft_id}/reject` 路由的 Request Schema 中，增加 `rejection_category` 和 `user_feedback_comment`（校验字数 >= 10）。
  2. 在 `NegativeCaseSampleService` 中实现脱敏规则 `MaskingService`（对 JSON 步骤或原始需求敏感词用 `[MASK]` 进行掩码脱敏）。
  3. **基于 `RagRetrieveSkill` 改造 AI 生成器**: 在 `AIClient.generate_cases_from_requirement` 触发前，查询并调起 `RagRetrieveSkill` 从 SQLite `negative_case_samples` 中自动匹配该模块相似的历史拒绝记录（最多 3 条），并在 Prompt 中以 `### 过去被拒绝的错误用例模式（请务必避免）` 格式注入 LLM，完成 Few-Shot 负向自适应纠偏！
  4. **门禁拦截**: 在生成后，若新 generated case 的 steps 与被拒 negative sample 的 steps 余弦相似度或字面重合度超过 0.85，直接标记为 `check_failed`，进入待确认队列阻断入库。
- **验证测试**: 编写单元测试 `backend/tests/test_negative_feedback_closed_loop.py`，完整模拟“生成->拒绝草稿(校验输入)->再次生成同模块->Prompt携带拒绝记录->生成高相似度->门禁拦截”全链路。

### [切片五] 从零构建：待办中心 (Todo Center) 一级模块与自清洗核销
- **ID**: `blue-todo-center`
- **任务内容**:
  1. 创建 `backend/app/routers/todos.py`，实现待办 CRUD、手动忽略 `dismiss`（强制 >= 10 字理由校验）。
  2. 在 `RequirementDocService`（解析失败、冲突）、`AICaseDraftService`（新增草稿）、`CaseService`（元素失效等）中埋入事件或同步调用 `TodoService.register_todo(...)`。
  3. **自清洗核销**: 在测试人员 `accept_draft` / `reject_draft` 时，自动定位关联的 `AI_CASE_DRAFT_PENDING` 待办，并在同一个数据库事务中原子核销置为 `resolved`。需求重新解析成功后核销对应待办。
  4. 实现 SSE `/api/todos/count-stream`，进行计数的实时气泡推送。
- **验证测试**: 编写并运行 `backend/tests/test_todo_center_closed_loop.py`，断言待办的注册、忽略校验、原子状态自清洗全流程 100% 跑通。

---

## 五、 防守效果验收证据表（阶段二：最终交付格式预演）

在阶段二防守代码加固完成后，我们将提供如下格式的最终验收表格，并附带所有的测试通过命令和 HTML 报告产物：

| 攻击点 | 是否复现 | 是否有失败测试 | 是否已修复 | 验证命令 | 剩余风险 |
| --- | --- | --- | --- | --- | --- |
| 1. 未审核需求生成Case (FR-REQ-009) | 是 (100% 复现) | 是 (TDD 失败测试) | 是 (已修复) | `python -m unittest backend/tests/test_case_sync_gate.py` | 无。后端已强校验 Stored 状态。 |
| 2. 伪造AI草稿同步 (Global Guardrails) | 是 (100% 复现) | 是 (TDD 失败测试) | 是 (已修复) | `python -m unittest backend/tests/test_case_sync_gate.py` | 无。新增了入参合法性、空文档和Stored文档核验。 |
| 3. API篡改用例可信状态 (FR-CASE-003) | 是 (100% 复现) | 是 (TDD 失败测试) | 是 (已修复) | `python -m unittest backend/tests/test_case_center.py` | 无。限制了 `TestCaseUpdate` Schema 的暴露，并在后端硬阻断了 trust_status 越权篡改。 |
| 4. 关键执行逻辑篡改免复核 (FR-CASE-009) | 是 (100% 复现) | 是 (TDD 失败测试) | 是 (已修复) | `python -m unittest backend/tests/test_case_center.py` | 无。所有来源用例的关键域（前置、步骤、预期）一经篡改均会被强制置为 `pending_reconfirm=1`。 |
| 5. 拒绝AI草稿“伪反馈闭环” (FR-CASE-005) | 是 (100% 复现) | 是 (TDD 失败测试) | 是 (已修复) | `python -m unittest backend/tests/test_negative_feedback_closed_loop.py` | 无。拒绝时必须传参分类和>=10字原因，负样本支持脱敏与基于 RAG 检索的 Few-Shot 负向拦截。 |
| 6. 用例废弃元数据缺失与防错 (FR-CASE-011) | 是 (100% 复现) | 是 (TDD 失败测试) | 是 (已修复) | `python -m unittest backend/tests/test_case_delete.py` | 无。废弃强制收集大类并转移归档视图，执行中心任何运行集100%自动过滤废弃用例。 |
| 7. 垃圾幽灵用例数据污染 (FR-CASE-001) | 是 (100% 复现) | 是 (TDD 失败测试) | 是 (已修复) | `python -m unittest backend/tests/test_case_center.py` | 无。强制要求提供有效的接口 ID 或关联项目模块，并对步骤和预期结果做非空检验。 |
| 8. 待办中心事件与核销空转 (FR-TODO-001) | 是 (100% 复现) | 是 (TDD 失败测试) | 是 (已修复) | `python -m unittest backend/tests/test_todo_center_closed_loop.py` | 无。从零构建了待办中心一级模块，实现了 8 种质量事件注册、双向原子自清洗核销和 SSE 计数推送。 |

*(注：在防守加固任务实施期间，红队将随时以真实攻击 payload 验证蓝队的强校验。所有的修复证据、单元测试日志、攻防演练现场数据都将被自动打包为 HTML 交付件。)*

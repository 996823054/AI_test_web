# 文件架构整理设计

**状态：** 已确认，待实施计划  
**日期：** 2026-07-15  
**范围：** 文档体系、后端与前端目录、兼容迁移、运行产物治理  

## 1. 目标

将当前横向散落的代码、重复/过时的技术文档和被 Git 跟踪的运行产物，收敛为以业务域为中心、可追溯、可渐进迁移的文件架构。

本次整理必须实现：

1. PRD 是唯一产品需求事实源；技术、交付、运维和历史文档有明确位置。
2. 后端代码以需求、Case、接口、执行、报告、移动端、变更和待办等业务域聚合。
3. 前端模块与后端业务域建立稳定映射。
4. 旧 API 和 Python 导入保留薄兼容适配层，直到调用方完成迁移。
5. 日志、SQLite、上传文件、Python 缓存、前端构建和测试缓存不再被 Git 跟踪。
6. 每个迁移阶段均可验证、可回退，目录调整不与数据库 schema 行为变更绑定。

## 2. 非目标

- 本轮不直接补齐 PRD 中未实现的全部业务能力。
- 本轮不改变既有 API 的响应字段语义。
- 本轮不做生产队列、对象存储、向量数据库或完整鉴权的落地。
- 本轮不把预研能力作为正式业务域扩展。
- 本轮不在单个提交中同时完成目录迁移和数据库 schema 重构。

## 3. 目标目录

```text
Ai_test_web/
├── backend/
│   ├── app/
│   │   ├── api/                    # Router、DTO、依赖与兼容端点
│   │   ├── domains/
│   │   │   ├── requirements/       # 需求文档、问题项、基线、差异、覆盖
│   │   │   ├── cases/              # Case、草稿、版本、来源关系
│   │   │   ├── apis/               # 接口事实源、环境、变量、调试
│   │   │   ├── executions/         # 任务、Harness、Runner、可运行检查
│   │   │   ├── reports/            # 报告、证据、导出与保留策略
│   │   │   ├── mobile/             # 设备、App、元素、移动端执行
│   │   │   ├── changes/            # ChangeRecord、影响分析、回归推荐
│   │   │   └── todos/              # 待办、事件注册、核销
│   │   ├── ai/                     # Skill、Prompt、Evaluator、RAG、调用记录
│   │   ├── platform/               # Config、DB、Storage、Masking、Audit、任务底座
│   │   └── shared/                 # 通用类型、异常、分页、时间、ID
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/                    # 入口、路由、导航、布局
│       ├── modules/                # 与后端 domains 对应的业务域
│       ├── shared/                 # HTTP、组件、composables、样式
│       └── legacy/                 # 短期兼容页面/API adapter
├── docs/
│   ├── product/                    # PRD、模块边界、验收证据
│   ├── architecture/               # 目标架构、领域模型、ADR
│   ├── delivery/                   # 任务拆分、迁移计划、实施状态
│   ├── operations/                 # 启动、部署、排障、运行策略
│   ├── reference/                  # 外部接口文档、样例资料
│   ├── archive/                    # 被替代文档的只读归档
│   └── superpowers/specs/          # 本设计与后续实施规格
├── scripts/                        # 启动、检查、迁移辅助脚本
├── tests/                          # 跨端到端、契约与仓库治理测试
├── .gitignore
├── README.md
└── CONTEXT.md
```

## 4. 模块边界

### 4.1 后端

| 目录 | 职责 | 禁止事项 |
|---|---|---|
| `api` | HTTP 路由、DTO、请求校验、依赖注入、旧路径代理 | 不编排业务、不调用 Runner |
| `domains/*` | 领域模型、应用服务、该域 Repository/Schema、领域测试 | 不跨域直接改写其他域聚合 |
| `ai` | 单一 Skill、Prompt、Evaluator、RAG 检索与 AI 调用记录 | 不直接写正式业务资产、不替代人工确认 |
| `platform` | 配置、数据库、存储、脱敏、审计、后台任务基础能力 | 不承载需求、Case 或执行业务规则 |
| `shared` | 稳定的通用类型、错误、分页、ID、时间 | 不放领域 Service 或业务状态机 |

执行域内部调用方向固定为：

```text
API Router -> ExecutionService -> Harness -> Runner -> ReportService
```

`Runner` 只能返回标准化步骤结果和产物引用；不能写需求、Case 或报告主表。`Harness` 负责环境、变量、依赖、测试数据、清理与证据增强。

### 4.2 前端

| 目录 | 职责 |
|---|---|
| `app` | 应用启动、Router、导航、全局布局 |
| `modules` | 各业务域的页面、状态、本域 API adapter、模块测试 |
| `shared` | HTTP、状态标签、证据查看、轮询、通用组件、样式 tokens |
| `legacy` | 被保留的旧入口，只转发，不新增业务逻辑 |

前端业务域目标为：`overview`、`requirements`、`cases`、`apis`、`executions`、`reports`、`mobile`、`ai`、`changes`、`todos`、`settings`。

## 5. 文档体系

| 分类 | 权威规则 |
|---|---|
| `docs/product` | `AI测试平台PRD.md` 是唯一产品需求事实源；模块确认文档只保存索引和边界结论。 |
| `docs/architecture` | 保存现行目标架构、领域模型、状态机、ADR；不得复制 PRD 需求正文。 |
| `docs/delivery` | 保存经确认的任务拆分、迁移顺序、验收状态和交付记录。 |
| `docs/operations` | 保存本地启动、部署、运行产物、排障与备份说明。 |
| `docs/reference` | 保存 httpbin 等外部接口文档和样例，不作为产品需求来源。 |
| `docs/archive` | 保存被替代的设计或历史记录；文档头必须标记替代关系。 |

首次整理要完成：

1. 新增根目录 `README.md`，说明项目结构、启动入口、权威文档和运行目录。
2. 修订 `docs/README.md`，覆盖所有现行文档目录。
3. 将两份技术设计文档收敛为一份 PRD v2 对齐的现行架构文档；旧稿进入 `docs/archive`。
4. 建立 `docs/architecture/adr/`，至少记录移动端验收范围、统一响应 `code` 类型、变更 API 命名、RAG 当前范围、执行状态枚举。

## 6. 兼容策略

### 6.1 API 兼容

1. 新路径先落在 `api` 与对应 `domains/*`。
2. 旧路由仅调用新应用服务，不复制原业务逻辑。
3. 旧路径响应字段、状态码和错误码在弃用期内保持不变。
4. 每个兼容端点标注弃用目标、引入版本、移除条件。
5. 每个兼容端点必须有新旧等价契约测试。

需求文档的 `/api/ai/documents*` 与 `/api/requirements*` 双前缀，要收敛为 `/api/requirements*`；旧 `/api/ai/documents*` 仅作为弃用代理保留。

### 6.2 Python 导入兼容

1. 旧文件保留轻量 re-export，指向新领域模块。
2. 新代码禁止继续 import 旧目录。
3. 每个 re-export 记录目标路径和删除条件。
4. 删除旧导入前，先通过全库搜索和测试证明调用数为零。

### 6.3 数据与行为兼容

目录迁移只改变代码位置和调用组织，不与数据库字段改名、表拆分或状态语义变化混合提交。数据模型深化在后续单独的领域迁移中执行。

## 7. 运行产物治理

`.gitignore` 必须覆盖：

```gitignore
# Python
__pycache__/
*.py[cod]

# Runtime data
.logs/
logs/
backend/*.db
uploads/
backend/uploads/
artifacts/

# Frontend generated content
frontend/dist/
frontend/node_modules/
frontend/node_modules/.vite/

# IDE and local tools
.idea/
.superpowers/
```

若仓库已有被跟踪的运行产物，实施时应使用 `git rm --cached` 停止跟踪，不删除本地运行所需文件。正式源码、需求样例或可复现 fixture 必须移动到受版本控制的测试 fixture 目录，不能放进真实上传目录。

## 8. 迁移阶段

### 阶段 0：仓库卫生与文档权威关系

- 建立 `.gitignore`、根 `README.md`、修订 `docs/README.md`。
- 清理 Git 跟踪的日志、数据库、缓存、上传文件和前端构建物。
- 建立 `architecture`、`delivery`、`operations`、`archive` 文档结构。
- 产出 ADR 清单与技术文档收敛清单。

**验收：** `git status` 不再因本地运行新增生成文件；PRD 与现行架构文档位置明确。

### 阶段 1：目标目录与兼容层

- 建立后端 `api`、`domains`、`ai`、`platform`、`shared`。
- 建立前端 `legacy` 及未实现业务域的目录约定。
- 迁移现有模块，同时添加旧导入和旧 API 适配层。
- 禁止业务逻辑继续进入旧横向目录。

**验收：** 现有后端测试、前端 HTTP 契约测试、前端构建通过；旧/新路径等价。

### 阶段 2：需求与 Case 资产域收敛

- 将 `RequirementDocService` 拆为文档、解析、问题工作流、生成上下文四个深 Module。
- 将 AI 草稿、版本、来源追溯和反馈沉淀聚合到 Case 域与 AI 域。
- 统一需求 API 前缀并保留旧前缀适配。

**验收：** 文档上传、解析、门禁、AI 草稿、确认和正式 Case 的现有测试全部通过。

### 阶段 3：执行与报告域收敛

- 建立 `ExecutionService`、Harness 接口、统一 `RunnerResult`、报告证据模型。
- 把现有 `TestExecutorService` 下沉为 API Runner 的执行实现。
- 为任务、日志、取消、重试、超时和报告证据建立独立测试。

**验收：** 接口 Case 执行从旧入口和新入口均可运行，得到等价任务与报告结果。

### 阶段 4：补齐业务域并退役兼容层

- 以 PRD 的模块边界逐步完善接口、移动端、变更、待办和 AI 中心。
- 每个模块完成前端入口、后端 API、服务编排、状态/证据和端到端测试。
- 依据调用统计与全库搜索删除无调用的兼容层。

**验收：** 前端导航、后端域目录、API 文档和 PRD 11 个一级模块一致；无旧路径调用。

## 9. 错误处理与回滚

1. 每阶段独立提交；不能通过的测试不得进入下一阶段。
2. API 兼容层发生差异时，保留旧路径并回滚新调用方迁移，不回滚已验证的目录结构。
3. 目录迁移失败时，按阶段提交回退；避免用硬重置丢弃其他工作。
4. 运行产物停止跟踪后，必须保留本地创建目录的启动逻辑或 `.gitkeep`，不能导致本地运行失败。
5. 预研模块（例如 `midscene_ios`、视觉自动化）必须通过 feature flag 或独立实验目录隔离，不能作为正式主路由默认加载。

## 10. 测试策略

| 层级 | 验证内容 |
|---|---|
| 仓库治理 | `.gitignore` 检查；禁止新增运行产物跟踪。 |
| 模块 | 每个领域服务的行为测试。 |
| 兼容 | 旧/新 Python import 与 API endpoint 的等价契约测试。 |
| 前端 | HTTP adapter 测试、构建、关键页面自检。 |
| 主链 | 需求到正式 Case、接口 Case 到报告、移动端基础链路的端到端回归。 |
| 架构 | Router 不直连 Runner、Skill 不写正式资产、Evaluator 不替代人工确认的守卫测试。 |

## 11. 风险与取舍

| 风险 | 应对 |
|---|---|
| 一次性目录迁移与未提交改动混淆 | 已先建立业务基线提交；运行产物另行治理。 |
| 新旧目录长期并存 | 兼容层只允许转发，设删除条件并在阶段 4 统一清理。 |
| 大文件简单搬家后仍然高耦合 | 阶段 2、3 要按领域职责拆分，而不是只 rename。 |
| 文档再度分叉 | PRD 为需求事实源，ADR 为关键技术决策，其他技术文档引用而不复制。 |
| 目录迁移影响运行 | 目录迁移与 schema/行为变更分离；每阶段保留回归门禁。 |

## 12. 完成定义

当满足下列条件时，文件架构整理完成：

1. 根 README、文档索引、PRD、现行技术架构和 ADR 的关系清晰且无相互冲突。
2. 后端和前端均以业务域为主组织，新代码不再落入旧横向目录。
3. 旧 API/导入仅存薄兼容层，且有迁移进度与删除标准。
4. 所有运行产物不再被 Git 跟踪。
5. 所有阶段的模块、兼容和主链回归测试通过。
6. PRD 当前范围内的模块能够按“页面入口 + 数据/API + 服务编排 + 证据/状态 + 端到端验证”持续交付。

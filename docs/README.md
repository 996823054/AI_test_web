# 项目文档导航

## 权威关系

1. [AI 测试平台 PRD](product/AI测试平台PRD.md) 是唯一产品需求事实源，定义产品目标、范围、功能需求、验收标准和护栏。
2. [模块功能逻辑确认](product/AI测试平台模块功能逻辑确认.md) 只维护模块边界、索引和确认结论；与 PRD 冲突时必须以 PRD 为准。
3. [平台技术架构](architecture/平台技术架构.md) 解释如何实现 PRD，不得复制或改写产品需求。
4. [ADR](architecture/adr/README.md) 记录关键技术决策；任务和进度只进入 `delivery/`。
5. `archive/` 仅保存被替代历史资料，不作为当前实现依据。

## 目录职责

- `product/`：PRD、模块边界和产品验收证据；产品语义只能在此维护。
- `architecture/`：当前技术架构、领域边界、状态机和 ADR。
- `delivery/`：开发任务拆分、AI 可执行计划、迁移计划和验收记录。
- `operations/`：本地启动、部署、运行产物、备份和排障说明。
- `reference/`：外部接口样例、测试资料和 AI 交付方法参考，不构成产品需求。
- `archive/`：被现行文档替代的历史设计和阶段性报告，默认只读。
- `superpowers/specs/`：已确认的重构规格与实施设计。

## 当前入口

### 产品

- [AI 测试平台 PRD](product/AI测试平台PRD.md)
- [AI 测试平台模块功能逻辑确认](product/AI测试平台模块功能逻辑确认.md)

### 架构

- [平台技术架构](architecture/平台技术架构.md)
- [架构决策记录索引](architecture/adr/README.md)

### 交付

- [AI 测试平台开发任务拆分](delivery/AI测试平台开发任务拆分.md)
- [AI 测试平台 AI 可执行开发计划](delivery/AI测试平台AI可执行开发计划.md)
- [批次 1 仓库治理验收证据](delivery/批次1仓库治理验收证据.md)
- [RC-10 验收证据](delivery/RC-10验收证据.md)

### 运维

- [本地运行](operations/本地运行.md)
- [运行产物](operations/运行产物.md)

### 参考与历史

- [httpbin 状态码接口文档](reference/httpbin状态码接口文档.md)
- [计算器需求文档样例](reference/计算器需求文档样例.md)
- [AI 交付 Prompt 与 Skill 库](reference/AI交付Prompt与Skill库.md)
- [归档说明](archive/README.md)

根目录 [CONTEXT.md](../CONTEXT.md) 保存稳定领域语言；根目录 [README.md](../README.md) 提供项目入口。

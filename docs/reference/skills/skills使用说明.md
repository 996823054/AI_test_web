# 第三方 Skills 使用说明手册

## 1. 使用原则

本项目当前整理了三类第三方 AI skills / agent 方法论：

```text
.agents/skills/ # mattpocock/skills 已安装位置
.agents/third-party-skills/ # 第三方 skill 来源索引与 PM skill 包
```

这些内容用于指导 AI 在 Cursor 中进行工程开发、产品设计、需求澄清、PRD、任务拆分、诊断、TDD、架构改进和交接。它们不是 AI 测试平台运行时的业务插件。

项目重要性顺序：

```text
docs/product/AI测试平台PRD.md -> docs/product/AI测试平台模块功能逻辑确认.md -> CONTEXT.md -> .cursor/rules/ -> .agents/skills/ -> .agents/third-party-skills/
```

## 2. 总览

| 来源 | 本地位置 | 数量 | 主要用途 |
|---|---|---:|---|
| mattpocock/skills：工程开发方法论 | `.agents/skills/` | 14 | 用于指导 AI 做工程开发、诊断、TDD、需求澄清、PRD、issue 拆分、架构改进和交接。 |
| product-on-purpose/pm-skills：产品经理方法论 | `.agents/third-party-skills/product-on-purpose-pm-skills/` | 40 | 用于产品发现、问题定义、用户画像、JTBD、用户故事、验收标准、OKR、指标、实验和迭代复盘。 |
| github/awesome-copilot：PRD 与产品经理 Agent | `.agents/third-party-skills/github-awesome-copilot-prd/` | 3 | 用于更标准的 PRD、产品经理视角审查、用户故事、成功指标、非目标、验收标准和 GitHub issue 质量控制。 |

## 3. 调用方法格式

后面在 Cursor 中推荐使用“相对路径 + skill/agent”的方式点名，避免 AI 误用其他同名能力。每个 skill 条目下面都提供了可直接复制的示例。

## 4. mattpocock/skills：工程开发方法论

用于指导 AI 做工程开发、诊断、TDD、需求澄清、PRD、issue 拆分、架构改进和交接。

### `diagnose`

- **名称**：`diagnose`
- **相对路径**：`.agents/skills/diagnose/SKILL.md`
- **用途**：用于按“复现、假设、探针、修复、回归测试”的闭环排查复杂 bug、失败和性能退化。
- **核心解决问题**：解决 AI 直接猜原因、跳过复现、修完没有回归验证的问题。
- **参数 / 输入信息**：`问题现象`、`复现步骤`、`日志/截图/报错`、`期望结果`、`实际结果`、`相关模块或接口`
- **使用示例**：

```text
参考 .agents/skills/diagnose/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "问题现象": "完整交付范围包含移动端后，验收边界不清",
 "复现步骤": "请根据当前 AI 测试平台上下文填写",
 "日志/截图/报错": "后端执行日志、浏览器控制台、Appium log、失败截图",
 "期望结果": "请根据当前 AI 测试平台上下文填写",
 "实际结果": "请根据当前 AI 测试平台上下文填写",
 "相关模块或接口": "backend/app/services、frontend/src/modules、backend/runners"
}
```

### `tdd`

- **名称**：`tdd`
- **相对路径**：`.agents/skills/tdd/SKILL.md`
- **用途**：用于按红绿重构循环开发功能或修复问题，强调从公开接口验证真实行为。
- **核心解决问题**：解决先写实现后补测试、测试耦合实现细节、改动缺少反馈闭环的问题。
- **参数 / 输入信息**：`要实现的行为`、`公开接口或入口`、`关键测试场景`、`验收标准`、`测试命令`
- **使用示例**：

```text
参考 .agents/skills/tdd/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "要实现的行为": "请根据当前 AI 测试平台上下文填写",
 "公开接口或入口": "请根据当前 AI 测试平台上下文填写",
 "关键测试场景": "请根据当前 AI 测试平台上下文填写",
 "验收标准": "用户可以完成上传、解析、确认、执行、查看报告的闭环",
 "测试命令": "请根据当前 AI 测试平台上下文填写"
}
```

### `grill-with-docs`

- **名称**：`grill-with-docs`
- **相对路径**：`.agents/skills/grill-with-docs/SKILL.md`
- **用途**：用于结合项目文档反复追问需求边界，并把确认后的术语和决策沉淀到上下文文档。
- **核心解决问题**：解决需求模糊、术语漂移、聊天里确认过但文档没有记录的问题。
- **参数 / 输入信息**：`待澄清需求`、`相关文档`、`当前假设`、`需要确认的边界`、`是否写入 CONTEXT.md`
- **使用示例**：

```text
参考 .agents/skills/grill-with-docs/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "待澄清需求": "请根据当前 AI 测试平台上下文填写",
 "相关文档": "docs/product/AI测试平台PRD.md、docs/product/AI测试平台模块功能逻辑确认.md、CONTEXT.md",
 "当前假设": "请根据当前 AI 测试平台上下文填写",
 "需要确认的边界": "请根据当前 AI 测试平台上下文填写",
 "是否写入 CONTEXT.md": "请根据当前 AI 测试平台上下文填写"
}
```

### `grill-me`

- **名称**：`grill-me`
- **相对路径**：`.agents/skills/grill-me/SKILL.md`
- **用途**：用于快速拷问一个计划或设计，逐个拆解决策树直到需求足够清楚。
- **核心解决问题**：解决方案想得不够细、隐藏分支没有被提前暴露的问题。
- **参数 / 输入信息**：`待澄清需求`、`相关文档`、`当前假设`、`需要确认的边界`、`是否写入 CONTEXT.md`
- **使用示例**：

```text
参考 .agents/skills/grill-me/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "待澄清需求": "请根据当前 AI 测试平台上下文填写",
 "相关文档": "docs/product/AI测试平台PRD.md、docs/product/AI测试平台模块功能逻辑确认.md、CONTEXT.md",
 "当前假设": "请根据当前 AI 测试平台上下文填写",
 "需要确认的边界": "请根据当前 AI 测试平台上下文填写",
 "是否写入 CONTEXT.md": "请根据当前 AI 测试平台上下文填写"
}
```

### `to-prd`

- **名称**：`to-prd`
- **相对路径**：`.agents/skills/to-prd/SKILL.md`
- **用途**：用于把当前上下文整理成 PRD，包含问题、方案、用户故事、实现和测试决策。
- **核心解决问题**：解决讨论内容零散、无法交给开发或评审的问题。
- **参数 / 输入信息**：`目标用户`、`核心问题`、`功能范围`、`非目标`、`成功指标`、`测试决策`
- **使用示例**：

```text
参考 .agents/skills/to-prd/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "目标用户": "测试开发、功能测试工程师、测试经理",
 "核心问题": "完整交付范围包含移动端后，验收边界不清",
 "功能范围": "模块完整交付 需求中心、case 中心、接口执行、移动端单设备闭环、报告中心",
 "非目标": "请根据当前 AI 测试平台上下文填写",
 "成功指标": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "测试决策": "请根据当前 AI 测试平台上下文填写"
}
```

### `to-issues`

- **名称**：`to-issues`
- **相对路径**：`.agents/skills/to-issues/SKILL.md`
- **用途**：用于把计划、PRD 或规格拆成可独立开发的垂直切片任务。
- **核心解决问题**：解决任务拆得太大、只按前后端横切、无法单独验收的问题。
- **参数 / 输入信息**：`计划/PRD/issue 内容`、`重要性`、`依赖关系`、`验收标准`、`issue tracker 位置`
- **使用示例**：

```text
参考 .agents/skills/to-issues/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "计划/PRD/issue 内容": "请根据当前 AI 测试平台上下文填写",
 "重要性": "请根据当前 AI 测试平台上下文填写",
 "依赖关系": "请根据当前 AI 测试平台上下文填写",
 "验收标准": "用户可以完成上传、解析、确认、执行、查看报告的闭环",
 "issue tracker 位置": "请根据当前 AI 测试平台上下文填写"
}
```

### `triage`

- **名称**：`triage`
- **相对路径**：`.agents/skills/triage/SKILL.md`
- **用途**：用于把 issue 按 bug/enhancement 和状态机进行分流、补信息或标记可开发。
- **核心解决问题**：解决需求和 bug 堆积后重要性不清、状态不清、agent 不知道能否接手的问题。
- **参数 / 输入信息**：`计划/PRD/issue 内容`、`重要性`、`依赖关系`、`验收标准`、`issue tracker 位置`
- **使用示例**：

```text
参考 .agents/skills/triage/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "计划/PRD/issue 内容": "请根据当前 AI 测试平台上下文填写",
 "重要性": "请根据当前 AI 测试平台上下文填写",
 "依赖关系": "请根据当前 AI 测试平台上下文填写",
 "验收标准": "用户可以完成上传、解析、确认、执行、查看报告的闭环",
 "issue tracker 位置": "请根据当前 AI 测试平台上下文填写"
}
```

### `improve-codebase-architecture`

- **名称**：`improve-codebase-architecture`
- **相对路径**：`.agents/skills/improve-codebase-architecture/SKILL.md`
- **用途**：用于发现模块过浅、耦合过强、难测试和难理解的架构摩擦，并提出加深模块的机会。
- **核心解决问题**：解决代码越写越散、接口复杂度过高、AI 和人都难以维护的问题。
- **参数 / 输入信息**：`目标模块`、`当前痛点`、`相关代码范围`、`测试困难点`、`已有上下文/ADR`
- **使用示例**：

```text
参考 .agents/skills/improve-codebase-architecture/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "目标模块": "backend/app/services、frontend/src/modules、backend/runners",
 "当前痛点": "请根据当前 AI 测试平台上下文填写",
 "相关代码范围": "模块完整交付 需求中心、case 中心、接口执行、移动端单设备闭环、报告中心",
 "测试困难点": "请根据当前 AI 测试平台上下文填写",
 "已有上下文/ADR": "请根据当前 AI 测试平台上下文填写"
}
```

### `zoom-out`

- **名称**：`zoom-out`
- **相对路径**：`.agents/skills/zoom-out/SKILL.md`
- **用途**：用于从更高层解释陌生代码区域，梳理相关模块、调用方和整体关系。
- **核心解决问题**：解决还没理解全局就直接改代码导致误改的问题。
- **参数 / 输入信息**：`目标模块`、`当前痛点`、`相关代码范围`、`测试困难点`、`已有上下文/ADR`
- **使用示例**：

```text
参考 .agents/skills/zoom-out/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "目标模块": "backend/app/services、frontend/src/modules、backend/runners",
 "当前痛点": "请根据当前 AI 测试平台上下文填写",
 "相关代码范围": "模块完整交付 需求中心、case 中心、接口执行、移动端单设备闭环、报告中心",
 "测试困难点": "请根据当前 AI 测试平台上下文填写",
 "已有上下文/ADR": "请根据当前 AI 测试平台上下文填写"
}
```

### `prototype`

- **名称**：`prototype`
- **相对路径**：`.agents/skills/prototype/SKILL.md`
- **用途**：用于构建一次性原型验证状态机、业务逻辑、数据模型或 UI 方案。
- **核心解决问题**：解决只靠文字争论方案，无法快速看见交互或状态变化的问题。
- **参数 / 输入信息**：`要验证的问题`、`原型类型`、`关键状态/交互`、`运行方式`、`删除或吸收标准`
- **使用示例**：

```text
参考 .agents/skills/prototype/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "要验证的问题": "完整交付范围包含移动端后，验收边界不清",
 "原型类型": "请根据当前 AI 测试平台上下文填写",
 "关键状态/交互": "请根据当前 AI 测试平台上下文填写",
 "运行方式": "请根据当前 AI 测试平台上下文填写",
 "删除或吸收标准": "请根据当前 AI 测试平台上下文填写"
}
```

### `setup-matt-pocock-skills`

- **名称**：`setup-matt-pocock-skills`
- **相对路径**：`.agents/skills/setup-matt-pocock-skills/SKILL.md`
- **用途**：用于初始化 mattpocock skills 所依赖的 issue tracker、标签和领域文档配置。
- **核心解决问题**：解决 PRD、issue、triage 等 skill 缺少项目级配置的问题。
- **参数 / 输入信息**：`issue tracker 类型`、`标签映射`、`领域文档位置`、`ADR 位置`
- **使用示例**：

```text
参考 .agents/skills/setup-matt-pocock-skills/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "issue tracker 类型": "请根据当前 AI 测试平台上下文填写",
 "标签映射": "请根据当前 AI 测试平台上下文填写",
 "领域文档位置": "docs/product/AI测试平台PRD.md、docs/product/AI测试平台模块功能逻辑确认.md、CONTEXT.md",
 "ADR 位置": "请根据当前 AI 测试平台上下文填写"
}
```

### `caveman`

- **名称**：`caveman`
- **相对路径**：`.agents/skills/caveman/SKILL.md`
- **用途**：用于开启极简沟通模式，让 AI 去掉寒暄和冗余说明，只保留技术要点。
- **核心解决问题**：解决回答太长、排查时信息密度不够的问题。
- **参数 / 输入信息**：`是否启用极简模式`、`是否保持持续生效`、`需要保留的技术细节`
- **使用示例**：

```text
参考 .agents/skills/caveman/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "是否启用极简模式": "请根据当前 AI 测试平台上下文填写",
 "是否保持持续生效": "请根据当前 AI 测试平台上下文填写",
 "需要保留的技术细节": "请根据当前 AI 测试平台上下文填写"
}
```

### `handoff`

- **名称**：`handoff`
- **相对路径**：`.agents/skills/handoff/SKILL.md`
- **用途**：用于把当前长会话压缩成交接文档，让新会话或另一个 agent 能继续。
- **核心解决问题**：解决上下文太长、换会话后信息丢失的问题。
- **参数 / 输入信息**：`当前任务目标`、`已完成内容`、`未完成事项`、`关键文件`、`下一步重点`
- **使用示例**：

```text
参考 .agents/skills/handoff/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "当前任务目标": "请根据当前 AI 测试平台上下文填写",
 "已完成内容": "请根据当前 AI 测试平台上下文填写",
 "未完成事项": "请根据当前 AI 测试平台上下文填写",
 "关键文件": "请根据当前 AI 测试平台上下文填写",
 "下一步重点": "请根据当前 AI 测试平台上下文填写"
}
```

### `write-a-skill`

- **名称**：`write-a-skill`
- **相对路径**：`.agents/skills/write-a-skill/SKILL.md`
- **用途**：用于创建新的 agent skill，包括触发场景、说明结构、参考资料和可选脚本。
- **核心解决问题**：解决重复性工作没有沉淀成可复用 AI 方法论的问题。
- **参数 / 输入信息**：`新 skill 任务域`、`触发场景`、`输入输出`、`参考资料`、`是否需要脚本`
- **使用示例**：

```text
参考 .agents/skills/write-a-skill/SKILL.md 这个 skill，结合 docs/product/AI测试平台PRD.md，帮我处理：模块完整交付 阶段接口执行报告证据链如何设计。
```

- **参数 / 输入示例**：

```json
{
 "新 skill 任务域": "请根据当前 AI 测试平台上下文填写",
 "触发场景": "请根据当前 AI 测试平台上下文填写",
 "输入输出": "Markdown 文档，包含结论、表格和可执行清单",
 "参考资料": "请根据当前 AI 测试平台上下文填写",
 "是否需要脚本": "请根据当前 AI 测试平台上下文填写"
}
```

## 5. product-on-purpose/pm-skills：产品经理方法论

用于产品发现、问题定义、用户画像、JTBD、用户故事、验收标准、OKR、指标、实验和迭代复盘。

### 定义类

#### `define-hypothesis`

- **名称**：`define-hypothesis`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/define-hypothesis/SKILL.md`
- **用途**：用于把产品假设写成可验证的结构，明确预期结果和验证方式。
- **核心解决问题**：解决产品判断不可验证、上线后不知道是否成功的问题。
- **参数 / 输入信息**：`目标用户`、`当前问题`、`业务背景`、`证据/数据`、`约束和假设`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/define-hypothesis/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "目标用户": "测试开发、功能测试工程师、测试经理",
 "当前问题": "完整交付范围包含移动端后，验收边界不清",
 "业务背景": "请根据当前 AI 测试平台上下文填写",
 "证据/数据": "请根据当前 AI 测试平台上下文填写",
 "约束和假设": "请根据当前 AI 测试平台上下文填写"
}
```

#### `define-jtbd-canvas`

- **名称**：`define-jtbd-canvas`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/define-jtbd-canvas/SKILL.md`
- **用途**：用于用 JTBD 方法描述用户在什么场景下雇佣产品完成什么任务。
- **核心解决问题**：解决用户画像只有角色标签，缺少真实任务和场景的问题。
- **参数 / 输入信息**：`目标用户`、`当前问题`、`业务背景`、`证据/数据`、`约束和假设`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/define-jtbd-canvas/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "目标用户": "测试开发、功能测试工程师、测试经理",
 "当前问题": "完整交付范围包含移动端后，验收边界不清",
 "业务背景": "请根据当前 AI 测试平台上下文填写",
 "证据/数据": "请根据当前 AI 测试平台上下文填写",
 "约束和假设": "请根据当前 AI 测试平台上下文填写"
}
```

#### `define-opportunity-tree`

- **名称**：`define-opportunity-tree`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/define-opportunity-tree/SKILL.md`
- **用途**：用于构建机会树，把目标、机会、方案和实验连接起来。
- **核心解决问题**：解决需求重要性只靠感觉、机会和方案混在一起的问题。
- **参数 / 输入信息**：`目标用户`、`当前问题`、`业务背景`、`证据/数据`、`约束和假设`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/define-opportunity-tree/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "目标用户": "测试开发、功能测试工程师、测试经理",
 "当前问题": "完整交付范围包含移动端后，验收边界不清",
 "业务背景": "请根据当前 AI 测试平台上下文填写",
 "证据/数据": "请根据当前 AI 测试平台上下文填写",
 "约束和假设": "请根据当前 AI 测试平台上下文填写"
}
```

#### `define-problem-statement`

- **名称**：`define-problem-statement`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/define-problem-statement/SKILL.md`
- **用途**：用于把模糊想法整理成清晰的问题陈述，明确用户、痛点、影响和证据。
- **核心解决问题**：解决“想做功能”但没有说明为什么要做、为谁做、痛点有多严重的问题。
- **参数 / 输入信息**：`目标用户`、`当前问题`、`业务背景`、`证据/数据`、`约束和假设`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/define-problem-statement/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "目标用户": "测试开发、功能测试工程师、测试经理",
 "当前问题": "完整交付范围包含移动端后，验收边界不清",
 "业务背景": "请根据当前 AI 测试平台上下文填写",
 "证据/数据": "请根据当前 AI 测试平台上下文填写",
 "约束和假设": "请根据当前 AI 测试平台上下文填写"
}
```

### 发现类

#### `discover-competitive-analysis`

- **名称**：`discover-competitive-analysis`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/discover-competitive-analysis/SKILL.md`
- **用途**：用于做竞品分析，比较定位、能力、差异化和机会。
- **核心解决问题**：解决不知道竞品怎么做、自己产品差异点不清的问题。
- **参数 / 输入信息**：`访谈记录/调研材料`、`目标用户`、`竞品或市场信息`、`待验证问题`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/discover-competitive-analysis/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "访谈记录/调研材料": "请根据当前 AI 测试平台上下文填写",
 "目标用户": "测试开发、功能测试工程师、测试经理",
 "竞品或市场信息": "请根据当前 AI 测试平台上下文填写",
 "待验证问题": "完整交付范围包含移动端后，验收边界不清"
}
```

#### `discover-interview-synthesis`

- **名称**：`discover-interview-synthesis`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/discover-interview-synthesis/SKILL.md`
- **用途**：用于综合用户访谈内容，提炼痛点、模式、机会和证据。
- **核心解决问题**：解决访谈记录很多但没有转化成可行动洞察的问题。
- **参数 / 输入信息**：`访谈记录/调研材料`、`目标用户`、`竞品或市场信息`、`待验证问题`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/discover-interview-synthesis/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "访谈记录/调研材料": "请根据当前 AI 测试平台上下文填写",
 "目标用户": "测试开发、功能测试工程师、测试经理",
 "竞品或市场信息": "请根据当前 AI 测试平台上下文填写",
 "待验证问题": "完整交付范围包含移动端后，验收边界不清"
}
```

#### `discover-stakeholder-summary`

- **名称**：`discover-stakeholder-summary`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/discover-stakeholder-summary/SKILL.md`
- **用途**：用于汇总干系人访谈或意见，提炼共识、分歧和待决策点。
- **核心解决问题**：解决多方意见分散、需求来源和立场不清的问题。
- **参数 / 输入信息**：`访谈记录/调研材料`、`目标用户`、`竞品或市场信息`、`待验证问题`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/discover-stakeholder-summary/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "访谈记录/调研材料": "请根据当前 AI 测试平台上下文填写",
 "目标用户": "测试开发、功能测试工程师、测试经理",
 "竞品或市场信息": "请根据当前 AI 测试平台上下文填写",
 "待验证问题": "完整交付范围包含移动端后，验收边界不清"
}
```

### 方案类

#### `develop-adr`

- **名称**：`develop-adr`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/develop-adr/SKILL.md`
- **用途**：用于产出架构决策记录，记录背景、选择、取舍和后果。
- **核心解决问题**：解决重大技术/产品架构决策没有可追溯记录的问题。
- **参数 / 输入信息**：`候选方案`、`技术约束`、`设计取舍`、`风险`、`待验证假设`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/develop-adr/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "候选方案": "请根据当前 AI 测试平台上下文填写",
 "技术约束": "请根据当前 AI 测试平台上下文填写",
 "设计取舍": "请根据当前 AI 测试平台上下文填写",
 "风险": "请根据当前 AI 测试平台上下文填写",
 "待验证假设": "请根据当前 AI 测试平台上下文填写"
}
```

#### `develop-design-rationale`

- **名称**：`develop-design-rationale`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/develop-design-rationale/SKILL.md`
- **用途**：用于记录设计理由，说明为什么选择当前方案而不是其他方案。
- **核心解决问题**：解决未来不知道当初为什么这样设计的问题。
- **参数 / 输入信息**：`候选方案`、`技术约束`、`设计取舍`、`风险`、`待验证假设`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/develop-design-rationale/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "候选方案": "请根据当前 AI 测试平台上下文填写",
 "技术约束": "请根据当前 AI 测试平台上下文填写",
 "设计取舍": "请根据当前 AI 测试平台上下文填写",
 "风险": "请根据当前 AI 测试平台上下文填写",
 "待验证假设": "请根据当前 AI 测试平台上下文填写"
}
```

#### `develop-solution-brief`

- **名称**：`develop-solution-brief`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/develop-solution-brief/SKILL.md`
- **用途**：用于把候选解决方案整理成 brief，说明目标、方案、范围和取舍。
- **核心解决问题**：解决方案散落在讨论里，无法评审和推进的问题。
- **参数 / 输入信息**：`候选方案`、`技术约束`、`设计取舍`、`风险`、`待验证假设`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/develop-solution-brief/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "候选方案": "请根据当前 AI 测试平台上下文填写",
 "技术约束": "请根据当前 AI 测试平台上下文填写",
 "设计取舍": "请根据当前 AI 测试平台上下文填写",
 "风险": "请根据当前 AI 测试平台上下文填写",
 "待验证假设": "请根据当前 AI 测试平台上下文填写"
}
```

#### `develop-spike-summary`

- **名称**：`develop-spike-summary`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/develop-spike-summary/SKILL.md`
- **用途**：用于总结技术 spike 或探索结果，沉淀结论、风险和建议。
- **核心解决问题**：解决技术探索做完后没有形成产品/技术决策依据的问题。
- **参数 / 输入信息**：`候选方案`、`技术约束`、`设计取舍`、`风险`、`待验证假设`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/develop-spike-summary/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "候选方案": "请根据当前 AI 测试平台上下文填写",
 "技术约束": "请根据当前 AI 测试平台上下文填写",
 "设计取舍": "请根据当前 AI 测试平台上下文填写",
 "风险": "请根据当前 AI 测试平台上下文填写",
 "待验证假设": "请根据当前 AI 测试平台上下文填写"
}
```

### 交付类

#### `deliver-acceptance-criteria`

- **名称**：`deliver-acceptance-criteria`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-acceptance-criteria/SKILL.md`
- **用途**：用于把需求转成可测试、可验收的条件。
- **核心解决问题**：解决“做完了”没有明确判定标准的问题。
- **参数 / 输入信息**：`功能范围`、`用户故事`、`验收标准`、`边界场景`、`发布目标`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-acceptance-criteria/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "功能范围": "模块完整交付 需求中心、case 中心、接口执行、移动端单设备闭环、报告中心",
 "用户故事": "测试开发、功能测试工程师、测试经理",
 "验收标准": "用户可以完成上传、解析、确认、执行、查看报告的闭环",
 "边界场景": "请根据当前 AI 测试平台上下文填写",
 "发布目标": "请根据当前 AI 测试平台上下文填写"
}
```

#### `deliver-edge-cases`

- **名称**：`deliver-edge-cases`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-edge-cases/SKILL.md`
- **用途**：用于系统性补充边界场景、异常路径和极端输入。
- **核心解决问题**：解决只覆盖主流程，漏掉异常和边界条件的问题。
- **参数 / 输入信息**：`功能范围`、`用户故事`、`验收标准`、`边界场景`、`发布目标`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-edge-cases/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "功能范围": "模块完整交付 需求中心、case 中心、接口执行、移动端单设备闭环、报告中心",
 "用户故事": "测试开发、功能测试工程师、测试经理",
 "验收标准": "用户可以完成上传、解析、确认、执行、查看报告的闭环",
 "边界场景": "请根据当前 AI 测试平台上下文填写",
 "发布目标": "请根据当前 AI 测试平台上下文填写"
}
```

#### `deliver-launch-checklist`

- **名称**：`deliver-launch-checklist`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-launch-checklist/SKILL.md`
- **用途**：用于生成上线检查清单，覆盖发布前准备、风险、回滚和沟通。
- **核心解决问题**：解决上线前遗漏验证、通知、监控或回滚准备的问题。
- **参数 / 输入信息**：`功能范围`、`用户故事`、`验收标准`、`边界场景`、`发布目标`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-launch-checklist/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "功能范围": "模块完整交付 需求中心、case 中心、接口执行、移动端单设备闭环、报告中心",
 "用户故事": "测试开发、功能测试工程师、测试经理",
 "验收标准": "用户可以完成上传、解析、确认、执行、查看报告的闭环",
 "边界场景": "请根据当前 AI 测试平台上下文填写",
 "发布目标": "请根据当前 AI 测试平台上下文填写"
}
```

#### `deliver-prd`

- **名称**：`deliver-prd`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-prd/SKILL.md`
- **用途**：用于生成产品需求文档，组织目标、范围、用户故事、验收标准和风险。
- **核心解决问题**：解决需求无法被设计、研发、测试共同理解和验收的问题。
- **参数 / 输入信息**：`功能范围`、`用户故事`、`验收标准`、`边界场景`、`发布目标`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-prd/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "功能范围": "模块完整交付 需求中心、case 中心、接口执行、移动端单设备闭环、报告中心",
 "用户故事": "测试开发、功能测试工程师、测试经理",
 "验收标准": "用户可以完成上传、解析、确认、执行、查看报告的闭环",
 "边界场景": "请根据当前 AI 测试平台上下文填写",
 "发布目标": "请根据当前 AI 测试平台上下文填写"
}
```

#### `deliver-release-notes`

- **名称**：`deliver-release-notes`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-release-notes/SKILL.md`
- **用途**：用于生成发布说明，面向用户说明变化、价值和注意事项。
- **核心解决问题**：解决发布后用户不知道改了什么、为什么重要的问题。
- **参数 / 输入信息**：`功能范围`、`用户故事`、`验收标准`、`边界场景`、`发布目标`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-release-notes/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "功能范围": "模块完整交付 需求中心、case 中心、接口执行、移动端单设备闭环、报告中心",
 "用户故事": "测试开发、功能测试工程师、测试经理",
 "验收标准": "用户可以完成上传、解析、确认、执行、查看报告的闭环",
 "边界场景": "请根据当前 AI 测试平台上下文填写",
 "发布目标": "请根据当前 AI 测试平台上下文填写"
}
```

#### `deliver-user-stories`

- **名称**：`deliver-user-stories`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-user-stories/SKILL.md`
- **用途**：用于把需求转成用户故事，描述用户、动作和价值。
- **核心解决问题**：解决功能列表没有用户视角，开发不知道每项能力服务谁的问题。
- **参数 / 输入信息**：`功能范围`、`用户故事`、`验收标准`、`边界场景`、`发布目标`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/deliver-user-stories/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "功能范围": "模块完整交付 需求中心、case 中心、接口执行、移动端单设备闭环、报告中心",
 "用户故事": "测试开发、功能测试工程师、测试经理",
 "验收标准": "用户可以完成上传、解析、确认、执行、查看报告的闭环",
 "边界场景": "请根据当前 AI 测试平台上下文填写",
 "发布目标": "请根据当前 AI 测试平台上下文填写"
}
```

### 度量类

#### `measure-dashboard-requirements`

- **名称**：`measure-dashboard-requirements`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/measure-dashboard-requirements/SKILL.md`
- **用途**：用于定义看板需求，包括指标、维度、数据来源和展示方式。
- **核心解决问题**：解决看板只做图表但不知道服务什么决策的问题。
- **参数 / 输入信息**：`目标指标`、`数据来源`、`实验设计`、`基线数据`、`成功阈值`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/measure-dashboard-requirements/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "目标指标": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "数据来源": "请根据当前 AI 测试平台上下文填写",
 "实验设计": "请根据当前 AI 测试平台上下文填写",
 "基线数据": "请根据当前 AI 测试平台上下文填写",
 "成功阈值": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%"
}
```

#### `measure-experiment-design`

- **名称**：`measure-experiment-design`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/measure-experiment-design/SKILL.md`
- **用途**：用于设计产品实验，明确假设、样本、指标和判定标准。
- **核心解决问题**：解决实验目标不清、结果不可解释的问题。
- **参数 / 输入信息**：`目标指标`、`数据来源`、`实验设计`、`基线数据`、`成功阈值`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/measure-experiment-design/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "目标指标": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "数据来源": "请根据当前 AI 测试平台上下文填写",
 "实验设计": "请根据当前 AI 测试平台上下文填写",
 "基线数据": "请根据当前 AI 测试平台上下文填写",
 "成功阈值": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%"
}
```

#### `measure-experiment-results`

- **名称**：`measure-experiment-results`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/measure-experiment-results/SKILL.md`
- **用途**：用于分析实验结果，判断是否通过、学习到了什么和下一步怎么做。
- **核心解决问题**：解决实验结束后只看数字，没有形成产品决策的问题。
- **参数 / 输入信息**：`目标指标`、`数据来源`、`实验设计`、`基线数据`、`成功阈值`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/measure-experiment-results/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "目标指标": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "数据来源": "请根据当前 AI 测试平台上下文填写",
 "实验设计": "请根据当前 AI 测试平台上下文填写",
 "基线数据": "请根据当前 AI 测试平台上下文填写",
 "成功阈值": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%"
}
```

#### `measure-instrumentation-spec`

- **名称**：`measure-instrumentation-spec`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/measure-instrumentation-spec/SKILL.md`
- **用途**：用于定义埋点和数据采集规格。
- **核心解决问题**：解决上线后没有数据验证产品效果的问题。
- **参数 / 输入信息**：`目标指标`、`数据来源`、`实验设计`、`基线数据`、`成功阈值`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/measure-instrumentation-spec/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "目标指标": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "数据来源": "请根据当前 AI 测试平台上下文填写",
 "实验设计": "请根据当前 AI 测试平台上下文填写",
 "基线数据": "请根据当前 AI 测试平台上下文填写",
 "成功阈值": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%"
}
```

#### `measure-okr-grader`

- **名称**：`measure-okr-grader`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/measure-okr-grader/SKILL.md`
- **用途**：用于检查 OKR 质量，判断目标和关键结果是否清晰、可衡量。
- **核心解决问题**：解决 OKR 空泛、不可衡量、和产品动作脱节的问题。
- **参数 / 输入信息**：`目标指标`、`数据来源`、`实验设计`、`基线数据`、`成功阈值`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/measure-okr-grader/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "目标指标": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "数据来源": "请根据当前 AI 测试平台上下文填写",
 "实验设计": "请根据当前 AI 测试平台上下文填写",
 "基线数据": "请根据当前 AI 测试平台上下文填写",
 "成功阈值": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%"
}
```

### 迭代类

#### `iterate-lessons-log`

- **名称**：`iterate-lessons-log`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/iterate-lessons-log/SKILL.md`
- **用途**：用于沉淀经验教训，把项目过程中的学习记录下来。
- **核心解决问题**：解决做完一个阶段后经验没有复用的问题。
- **参数 / 输入信息**：`上线结果`、`用户反馈`、`指标变化`、`问题清单`、`下一步选择`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/iterate-lessons-log/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "上线结果": "请根据当前 AI 测试平台上下文填写",
 "用户反馈": "测试开发、功能测试工程师、测试经理",
 "指标变化": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "问题清单": "完整交付范围包含移动端后，验收边界不清",
 "下一步选择": "请根据当前 AI 测试平台上下文填写"
}
```

#### `iterate-pivot-decision`

- **名称**：`iterate-pivot-decision`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/iterate-pivot-decision/SKILL.md`
- **用途**：用于支持继续、调整或转向决策。
- **核心解决问题**：解决指标和反馈不佳时不知道该坚持还是转向的问题。
- **参数 / 输入信息**：`上线结果`、`用户反馈`、`指标变化`、`问题清单`、`下一步选择`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/iterate-pivot-decision/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "上线结果": "请根据当前 AI 测试平台上下文填写",
 "用户反馈": "测试开发、功能测试工程师、测试经理",
 "指标变化": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "问题清单": "完整交付范围包含移动端后，验收边界不清",
 "下一步选择": "请根据当前 AI 测试平台上下文填写"
}
```

#### `iterate-refinement-notes`

- **名称**：`iterate-refinement-notes`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/iterate-refinement-notes/SKILL.md`
- **用途**：用于整理需求细化记录，把反馈转成下一轮改进。
- **核心解决问题**：解决评审反馈分散，后面迭代方向不清的问题。
- **参数 / 输入信息**：`上线结果`、`用户反馈`、`指标变化`、`问题清单`、`下一步选择`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/iterate-refinement-notes/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "上线结果": "请根据当前 AI 测试平台上下文填写",
 "用户反馈": "测试开发、功能测试工程师、测试经理",
 "指标变化": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "问题清单": "完整交付范围包含移动端后，验收边界不清",
 "下一步选择": "请根据当前 AI 测试平台上下文填写"
}
```

#### `iterate-retrospective`

- **名称**：`iterate-retrospective`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/iterate-retrospective/SKILL.md`
- **用途**：用于项目复盘，提炼做得好、问题和改进行动。
- **核心解决问题**：解决阶段结束后没有系统复盘的问题。
- **参数 / 输入信息**：`上线结果`、`用户反馈`、`指标变化`、`问题清单`、`下一步选择`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/iterate-retrospective/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "上线结果": "请根据当前 AI 测试平台上下文填写",
 "用户反馈": "测试开发、功能测试工程师、测试经理",
 "指标变化": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "问题清单": "完整交付范围包含移动端后，验收边界不清",
 "下一步选择": "请根据当前 AI 测试平台上下文填写"
}
```

### 基础类

#### `foundation-lean-canvas`

- **名称**：`foundation-lean-canvas`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-lean-canvas/SKILL.md`
- **用途**：用于创建精益画布，梳理问题、用户、价值主张、渠道、成本和收益。
- **核心解决问题**：解决产品商业和价值假设没有结构化表达的问题。
- **参数 / 输入信息**：`项目背景`、`参与角色`、`会议/画布目标`、`需要输出的模板类型`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-lean-canvas/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "项目背景": "请根据当前 AI 测试平台上下文填写",
 "参与角色": "请根据当前 AI 测试平台上下文填写",
 "会议/画布目标": "请根据当前 AI 测试平台上下文填写",
 "需要输出的模板类型": "Markdown 文档，包含结论、表格和可执行清单"
}
```

#### `foundation-meeting-agenda`

- **名称**：`foundation-meeting-agenda`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-meeting-agenda/SKILL.md`
- **用途**：用于生成会议议程，明确目标、议题和产出。
- **核心解决问题**：解决会议没有目标、讨论发散的问题。
- **参数 / 输入信息**：`项目背景`、`参与角色`、`会议/画布目标`、`需要输出的模板类型`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-meeting-agenda/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "项目背景": "请根据当前 AI 测试平台上下文填写",
 "参与角色": "请根据当前 AI 测试平台上下文填写",
 "会议/画布目标": "请根据当前 AI 测试平台上下文填写",
 "需要输出的模板类型": "Markdown 文档，包含结论、表格和可执行清单"
}
```

#### `foundation-meeting-brief`

- **名称**：`foundation-meeting-brief`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-meeting-brief/SKILL.md`
- **用途**：用于生成会前 brief，帮助参与者提前理解背景和决策点。
- **核心解决问题**：解决会议开始后还在补背景的问题。
- **参数 / 输入信息**：`项目背景`、`参与角色`、`会议/画布目标`、`需要输出的模板类型`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-meeting-brief/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "项目背景": "请根据当前 AI 测试平台上下文填写",
 "参与角色": "请根据当前 AI 测试平台上下文填写",
 "会议/画布目标": "请根据当前 AI 测试平台上下文填写",
 "需要输出的模板类型": "Markdown 文档，包含结论、表格和可执行清单"
}
```

#### `foundation-meeting-recap`

- **名称**：`foundation-meeting-recap`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-meeting-recap/SKILL.md`
- **用途**：用于生成会议纪要，记录结论、行动项和责任人。
- **核心解决问题**：解决会议结束后决策和行动没人跟进的问题。
- **参数 / 输入信息**：`项目背景`、`参与角色`、`会议/画布目标`、`需要输出的模板类型`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-meeting-recap/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "项目背景": "请根据当前 AI 测试平台上下文填写",
 "参与角色": "请根据当前 AI 测试平台上下文填写",
 "会议/画布目标": "请根据当前 AI 测试平台上下文填写",
 "需要输出的模板类型": "Markdown 文档，包含结论、表格和可执行清单"
}
```

#### `foundation-meeting-synthesize`

- **名称**：`foundation-meeting-synthesize`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-meeting-synthesize/SKILL.md`
- **用途**：用于综合多场会议或多份会议记录，提炼共同主题和分歧。
- **核心解决问题**：解决会议资料多但缺少汇总洞察的问题。
- **参数 / 输入信息**：`项目背景`、`参与角色`、`会议/画布目标`、`需要输出的模板类型`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-meeting-synthesize/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "项目背景": "请根据当前 AI 测试平台上下文填写",
 "参与角色": "请根据当前 AI 测试平台上下文填写",
 "会议/画布目标": "请根据当前 AI 测试平台上下文填写",
 "需要输出的模板类型": "Markdown 文档，包含结论、表格和可执行清单"
}
```

#### `foundation-okr-writer`

- **名称**：`foundation-okr-writer`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-okr-writer/SKILL.md`
- **用途**：用于编写 OKR，明确目标、关键结果和衡量方式。
- **核心解决问题**：解决目标表达空泛、无法衡量的问题。
- **参数 / 输入信息**：`项目背景`、`参与角色`、`会议/画布目标`、`需要输出的模板类型`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-okr-writer/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "项目背景": "请根据当前 AI 测试平台上下文填写",
 "参与角色": "请根据当前 AI 测试平台上下文填写",
 "会议/画布目标": "请根据当前 AI 测试平台上下文填写",
 "需要输出的模板类型": "Markdown 文档，包含结论、表格和可执行清单"
}
```

#### `foundation-persona`

- **名称**：`foundation-persona`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-persona/SKILL.md`
- **用途**：用于生成用户画像，描述角色、目标、痛点、场景和行为。
- **核心解决问题**：解决目标用户只有职位名称，没有真实使用场景的问题。
- **参数 / 输入信息**：`项目背景`、`参与角色`、`会议/画布目标`、`需要输出的模板类型`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-persona/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "项目背景": "请根据当前 AI 测试平台上下文填写",
 "参与角色": "请根据当前 AI 测试平台上下文填写",
 "会议/画布目标": "请根据当前 AI 测试平台上下文填写",
 "需要输出的模板类型": "Markdown 文档，包含结论、表格和可执行清单"
}
```

#### `foundation-stakeholder-update`

- **名称**：`foundation-stakeholder-update`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-stakeholder-update/SKILL.md`
- **用途**：用于生成干系人同步材料，说明进展、风险和需要决策的事项。
- **核心解决问题**：解决项目进展沟通不清、风险暴露不及时的问题。
- **参数 / 输入信息**：`项目背景`、`参与角色`、`会议/画布目标`、`需要输出的模板类型`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/foundation-stakeholder-update/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "项目背景": "请根据当前 AI 测试平台上下文填写",
 "参与角色": "请根据当前 AI 测试平台上下文填写",
 "会议/画布目标": "请根据当前 AI 测试平台上下文填写",
 "需要输出的模板类型": "Markdown 文档，包含结论、表格和可执行清单"
}
```

### 工具类

#### `utility-mermaid-diagrams`

- **名称**：`utility-mermaid-diagrams`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-mermaid-diagrams/SKILL.md`
- **用途**：用于生成 Mermaid 图，表达流程、架构、依赖和状态。
- **核心解决问题**：解决复杂关系只用文字很难看懂的问题。
- **参数 / 输入信息**：`要生成/校验/更新的材料`、`目标格式`、`质量标准`、`参考示例`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-mermaid-diagrams/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "要生成/校验/更新的材料": "请根据当前 AI 测试平台上下文填写",
 "目标格式": "Markdown 文档，包含结论、表格和可执行清单",
 "质量标准": "请根据当前 AI 测试平台上下文填写",
 "参考示例": "请根据当前 AI 测试平台上下文填写"
}
```

#### `utility-pm-skill-builder`

- **名称**：`utility-pm-skill-builder`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-pm-skill-builder/SKILL.md`
- **用途**：用于创建新的产品管理 skill。
- **核心解决问题**：解决 PM 工作流无法复用和标准化的问题。
- **参数 / 输入信息**：`要生成/校验/更新的材料`、`目标格式`、`质量标准`、`参考示例`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-pm-skill-builder/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "要生成/校验/更新的材料": "请根据当前 AI 测试平台上下文填写",
 "目标格式": "Markdown 文档，包含结论、表格和可执行清单",
 "质量标准": "请根据当前 AI 测试平台上下文填写",
 "参考示例": "请根据当前 AI 测试平台上下文填写"
}
```

#### `utility-pm-skill-iterate`

- **名称**：`utility-pm-skill-iterate`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-pm-skill-iterate/SKILL.md`
- **用途**：用于迭代改进已有 PM skill。
- **核心解决问题**：解决 skill 使用后发现不适配但没有优化流程的问题。
- **参数 / 输入信息**：`要生成/校验/更新的材料`、`目标格式`、`质量标准`、`参考示例`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-pm-skill-iterate/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "要生成/校验/更新的材料": "请根据当前 AI 测试平台上下文填写",
 "目标格式": "Markdown 文档，包含结论、表格和可执行清单",
 "质量标准": "请根据当前 AI 测试平台上下文填写",
 "参考示例": "请根据当前 AI 测试平台上下文填写"
}
```

#### `utility-pm-skill-validate`

- **名称**：`utility-pm-skill-validate`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-pm-skill-validate/SKILL.md`
- **用途**：用于校验 PM skill 的结构、触发条件和输出质量。
- **核心解决问题**：解决 skill 写得不清晰、AI 不知道何时使用的问题。
- **参数 / 输入信息**：`要生成/校验/更新的材料`、`目标格式`、`质量标准`、`参考示例`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-pm-skill-validate/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "要生成/校验/更新的材料": "请根据当前 AI 测试平台上下文填写",
 "目标格式": "Markdown 文档，包含结论、表格和可执行清单",
 "质量标准": "请根据当前 AI 测试平台上下文填写",
 "参考示例": "请根据当前 AI 测试平台上下文填写"
}
```

#### `utility-slideshow-creator`

- **名称**：`utility-slideshow-creator`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-slideshow-creator/SKILL.md`
- **用途**：用于创建产品汇报或方案展示幻灯片。
- **核心解决问题**：解决需要对外沟通但材料结构不清的问题。
- **参数 / 输入信息**：`要生成/校验/更新的材料`、`目标格式`、`质量标准`、`参考示例`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-slideshow-creator/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "要生成/校验/更新的材料": "请根据当前 AI 测试平台上下文填写",
 "目标格式": "Markdown 文档，包含结论、表格和可执行清单",
 "质量标准": "请根据当前 AI 测试平台上下文填写",
 "参考示例": "请根据当前 AI 测试平台上下文填写"
}
```

#### `utility-update-pm-skills`

- **名称**：`utility-update-pm-skills`
- **相对路径**：`.agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-update-pm-skills/SKILL.md`
- **用途**：用于更新 PM skills 包或相关索引。
- **核心解决问题**：解决第三方 PM skill 版本和本地说明不同步的问题。
- **参数 / 输入信息**：`要生成/校验/更新的材料`、`目标格式`、`质量标准`、`参考示例`
- **使用示例**：

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/utility-update-pm-skills/SKILL.md 这个 PM skill，结合 docs/product/AI测试平台PRD.md，帮我完成：AI 测试平台 模块完整交付 的产品分析和验收标准梳理。
```

- **参数 / 输入示例**：

```json
{
 "要生成/校验/更新的材料": "请根据当前 AI 测试平台上下文填写",
 "目标格式": "Markdown 文档，包含结论、表格和可执行清单",
 "质量标准": "请根据当前 AI 测试平台上下文填写",
 "参考示例": "请根据当前 AI 测试平台上下文填写"
}
```

## 6. github/awesome-copilot：PRD 与产品经理 Agent

用于更标准的 PRD、产品经理视角审查、用户故事、成功指标、非目标、验收标准和 GitHub issue 质量控制。

### `prd`

- **名称**：`prd`
- **相对路径**：`.agents/third-party-skills/github-awesome-copilot-prd/skills/prd/SKILL.md`
- **用途**：用于生成高质量 PRD，覆盖执行摘要、用户故事、验收标准、技术规格、AI 评估和风险路线图。
- **核心解决问题**：解决 PRD 只有想法没有可测试需求、成功指标和非目标的问题。
- **参数 / 输入信息**：`产品/功能背景`、`目标用户`、`核心问题`、`成功指标`、`约束条件`、`期望输出格式`
- **使用示例**：

```text
参考 .agents/third-party-skills/github-awesome-copilot-prd/skills/prd/SKILL.md 这个 PRD/PM agent，结合 docs/product/AI测试平台PRD.md，帮我输出：AI 测试平台 模块完整交付 的 PRD、用户故事和成功指标。
```

- **参数 / 输入示例**：

```json
{
 "产品/功能背景": "请根据当前 AI 测试平台上下文填写",
 "目标用户": "测试开发、功能测试工程师、测试经理",
 "核心问题": "完整交付范围包含移动端后，验收边界不清",
 "成功指标": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "约束条件": "请根据当前 AI 测试平台上下文填写",
 "期望输出格式": "Markdown 文档，包含结论、表格和可执行清单"
}
```

### `prd.agent`

- **名称**：`Create PRD Chat Mode`
- **相对路径**：`.agents/third-party-skills/github-awesome-copilot-prd/agents/prd.agent.md`
- **用途**：用于以产品经理 chat mode 方式创建完整 PRD，并在确认后可进一步转成 GitHub issue。
- **核心解决问题**：解决 PRD 缺少澄清问题、代码库分析、需求 ID 和可测试用户故事的问题。
- **参数 / 输入信息**：`产品/功能背景`、`目标用户`、`核心问题`、`成功指标`、`约束条件`、`期望输出格式`
- **使用示例**：

```text
参考 .agents/third-party-skills/github-awesome-copilot-prd/agents/prd.agent.md 这个 PRD/PM agent，结合 docs/product/AI测试平台PRD.md，帮我输出：AI 测试平台 模块完整交付 的 PRD、用户故事和成功指标。
```

- **参数 / 输入示例**：

```json
{
 "产品/功能背景": "请根据当前 AI 测试平台上下文填写",
 "目标用户": "测试开发、功能测试工程师、测试经理",
 "核心问题": "完整交付范围包含移动端后，验收边界不清",
 "成功指标": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "约束条件": "请根据当前 AI 测试平台上下文填写",
 "期望输出格式": "Markdown 文档，包含结论、表格和可执行清单"
}
```

### `se-product-manager-advisor.agent`

- **名称**：`SE: Product Manager`
- **相对路径**：`.agents/third-party-skills/github-awesome-copilot-prd/agents/se-product-manager-advisor.agent.md`
- **用途**：用于从产品经理视角检查功能是否有真实用户、业务价值、成功指标和可执行 issue。
- **核心解决问题**：解决功能先行、缺少用户问题和业务上下文的问题。
- **参数 / 输入信息**：`产品/功能背景`、`目标用户`、`核心问题`、`成功指标`、`约束条件`、`期望输出格式`
- **使用示例**：

```text
参考 .agents/third-party-skills/github-awesome-copilot-prd/agents/se-product-manager-advisor.agent.md 这个 PRD/PM agent，结合 docs/product/AI测试平台PRD.md，帮我输出：AI 测试平台 模块完整交付 的 PRD、用户故事和成功指标。
```

- **参数 / 输入示例**：

```json
{
 "产品/功能背景": "请根据当前 AI 测试平台上下文填写",
 "目标用户": "测试开发、功能测试工程师、测试经理",
 "核心问题": "完整交付范围包含移动端后，验收边界不清",
 "成功指标": "需求到当前完整版本 case 产出时间下降 50%，接口报告可复盘率 100%",
 "约束条件": "请根据当前 AI 测试平台上下文填写",
 "期望输出格式": "Markdown 文档，包含结论、表格和可执行清单"
}
```

## 7. 推荐组合

### 产品视角澄清 模块完整交付

```text
product-on-purpose PM skills -> grill-with-docs -> awesome-copilot PRD -> to-issues
```

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/define-problem-statement/SKILL.md 和 .agents/skills/grill-with-docs/SKILL.md，帮我澄清 AI 测试平台 完整交付范围。
```

### 开发接口执行链路

```text
grill-with-docs -> tdd -> diagnose
```

```text
参考 .agents/skills/tdd/SKILL.md，帮我按 TDD 实现接口执行报告证据链。
```

### 整理标准 PRD

```text
awesome-copilot PRD skill -> mattpocock to-prd -> to-issues
```

```text
参考 .agents/third-party-skills/github-awesome-copilot-prd/skills/prd/SKILL.md，帮我把报告中心 模块完整交付 整理成 PRD。
```

### 定义成功指标

```text
product-on-purpose measure-* -> Product Manager Advisor -> dashboard requirements
```

```text
参考 .agents/third-party-skills/product-on-purpose-pm-skills/skills/measure-okr-grader/SKILL.md，帮我定义 AI 测试平台 模块完整交付 成功指标。
```

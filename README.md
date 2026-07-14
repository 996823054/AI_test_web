# AI 测试平台

AI 测试平台以可追溯测试资产为核心，连接需求、Case、接口、执行、报告、AI 能力、变更和人工复核流程。

## 权威文档

- 产品需求唯一事实源：[AI 测试平台 PRD](docs/product/AI测试平台PRD.md)
- 模块边界索引：[模块功能逻辑确认](docs/product/AI测试平台模块功能逻辑确认.md)
- 当前技术架构：[平台技术架构](docs/architecture/平台技术架构.md)
- 文档导航：[docs/README.md](docs/README.md)
- 领域上下文：[CONTEXT.md](CONTEXT.md)

产品语义冲突时以 PRD 为准。技术取舍记录在 ADR，实施任务记录在 `docs/delivery/`，运维说明记录在 `docs/operations/`。

## 目录

```text
backend/          FastAPI 后端与后端测试
frontend/         Vue 3 前端
docs/product/     产品需求事实源与模块边界
docs/architecture 当前架构和 ADR
docs/delivery/    任务拆分、执行计划与验收记录
docs/operations/  本地运行和运行产物说明
docs/reference/   外部接口、样例和方法参考
docs/archive/     已被替代的历史文档
tests/            跨仓库治理检查
```

## 本地运行

完整环境要求和命令见[本地运行说明](docs/operations/本地运行.md)。

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

## 验证

```bash
python -m unittest tests.test_repository_governance -v
python scripts/check_document_links.py
cd backend && python -m unittest discover -s tests
cd ../frontend && npm test && npm run build
```

仓库治理测试会同时调用文档链接检查；单独运行脚本可获得链接数量和失败位置。

日志、SQLite、真实上传文件、Python 缓存、构建产物、依赖目录和本地工具状态都属于运行产物，不得提交。具体规则见[运行产物说明](docs/operations/运行产物.md)。

"""
数据库连接模块
==============
SQLAlchemy 数据库引擎和会话管理
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# 创建引擎
# SQLite 需要 check_same_thread=False
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG  # 调试模式下打印 SQL
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话（FastAPI 依赖注入用）

    使用示例:
        @router.get("/")
        def list_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建所有表）"""
    # 导入所有模型，确保 Base 知道它们
    from app.models import project, api_info, test_case, execution, changelog, user, requirement_document  # noqa
    from app.models import requirement_tree_node, requirement_item, requirement_issue, case_version, case_step, ai_case_draft, negative_case_sample, ai_feedback_sample, todo  # noqa
    Base.metadata.create_all(bind=engine)
    apply_lightweight_migrations()
    seed_demo_data()
    print("✅ 数据库表已创建")


def apply_lightweight_migrations():
    """开发阶段的轻量迁移，补齐新增字段"""
    migrations = {
        "requirement_documents": {
            "tree_node_id": "ALTER TABLE requirement_documents ADD COLUMN tree_node_id INTEGER",
            "file_hash": "ALTER TABLE requirement_documents ADD COLUMN file_hash VARCHAR(64) DEFAULT ''",
            "project_id": "ALTER TABLE requirement_documents ADD COLUMN project_id INTEGER",
            "parse_status": "ALTER TABLE requirement_documents ADD COLUMN parse_status VARCHAR(30) DEFAULT 'unparsed'",
            "parse_result": "ALTER TABLE requirement_documents ADD COLUMN parse_result TEXT DEFAULT ''",
            "version_no": "ALTER TABLE requirement_documents ADD COLUMN version_no INTEGER DEFAULT 1",
            "parent_document_id": "ALTER TABLE requirement_documents ADD COLUMN parent_document_id INTEGER",
        },
        "test_cases": {
            "case_kind": "ALTER TABLE test_cases ADD COLUMN case_kind VARCHAR(20) DEFAULT 'api'",
            "platform": "ALTER TABLE test_cases ADD COLUMN platform VARCHAR(20) DEFAULT ''",
            "version_group": "ALTER TABLE test_cases ADD COLUMN version_group VARCHAR(100) DEFAULT ''",
            "source_document_id": "ALTER TABLE test_cases ADD COLUMN source_document_id INTEGER",
            "steps": "ALTER TABLE test_cases ADD COLUMN steps JSON",
            "precondition": "ALTER TABLE test_cases ADD COLUMN precondition TEXT DEFAULT ''",
            "expected_result": "ALTER TABLE test_cases ADD COLUMN expected_result TEXT DEFAULT ''",
            "dependency_consideration": "ALTER TABLE test_cases ADD COLUMN dependency_consideration TEXT DEFAULT ''",
            "lifecycle_status": "ALTER TABLE test_cases ADD COLUMN lifecycle_status VARCHAR(20) DEFAULT 'active'",
            "current_version_no": "ALTER TABLE test_cases ADD COLUMN current_version_no INTEGER DEFAULT 1",
            "trust_status": "ALTER TABLE test_cases ADD COLUMN trust_status VARCHAR(30) DEFAULT 'formal'",
            "module_delivery": "ALTER TABLE test_cases ADD COLUMN module_delivery INTEGER DEFAULT 0",
            "importance": "ALTER TABLE test_cases ADD COLUMN importance VARCHAR(20) DEFAULT 'normal'",
            "confirmed_by": "ALTER TABLE test_cases ADD COLUMN confirmed_by VARCHAR(50) DEFAULT ''",
            "confirmed_at": "ALTER TABLE test_cases ADD COLUMN confirmed_at DATETIME",
            "requirement_item_id": "ALTER TABLE test_cases ADD COLUMN requirement_item_id INTEGER",
            "pending_reconfirm": "ALTER TABLE test_cases ADD COLUMN pending_reconfirm INTEGER DEFAULT 0",
            "deprecation_category": "ALTER TABLE test_cases ADD COLUMN deprecation_category VARCHAR(50)",
            "deprecation_reason": "ALTER TABLE test_cases ADD COLUMN deprecation_reason TEXT DEFAULT ''",
            "replaced_by_case_id": "ALTER TABLE test_cases ADD COLUMN replaced_by_case_id INTEGER",
            "change_record_id": "ALTER TABLE test_cases ADD COLUMN change_record_id INTEGER",
        },
        "negative_case_samples": {
            "source_type": "ALTER TABLE negative_case_samples ADD COLUMN source_type VARCHAR(30) DEFAULT ''",
            "source_case_id": "ALTER TABLE negative_case_samples ADD COLUMN source_case_id INTEGER",
            "source_draft_id": "ALTER TABLE negative_case_samples ADD COLUMN source_draft_id INTEGER",
            "source_document_id": "ALTER TABLE negative_case_samples ADD COLUMN source_document_id INTEGER",
            "reason": "ALTER TABLE negative_case_samples ADD COLUMN reason TEXT DEFAULT ''",
            "sample_payload": "ALTER TABLE negative_case_samples ADD COLUMN sample_payload TEXT DEFAULT ''",
            "tags": "ALTER TABLE negative_case_samples ADD COLUMN tags TEXT DEFAULT ''",
            "created_by": "ALTER TABLE negative_case_samples ADD COLUMN created_by VARCHAR(50) DEFAULT 'system'",
            "created_at": "ALTER TABLE negative_case_samples ADD COLUMN created_at DATETIME",
            "rejection_category": "ALTER TABLE negative_case_samples ADD COLUMN rejection_category VARCHAR(50)",
            "user_feedback_comment": "ALTER TABLE negative_case_samples ADD COLUMN user_feedback_comment TEXT DEFAULT ''",
            "source_requirement": "ALTER TABLE negative_case_samples ADD COLUMN source_requirement TEXT DEFAULT ''",
            "deprecation_category": "ALTER TABLE negative_case_samples ADD COLUMN deprecation_category VARCHAR(50)",
        },
    }

    with engine.connect() as connection:
        for table_name, table_migrations in migrations.items():
            existing_columns = {
                row[1]
                for row in connection.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
            }
            for column_name, statement in table_migrations.items():
                if column_name not in existing_columns:
                    connection.execute(text(statement))
        
        # 清理和矫正历史遗留非标准分类，避免在分类下拉框中展示无用的非标准分类
        connection.execute(text(
            "CREATE TABLE IF NOT EXISTS case_steps ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "case_id INTEGER NOT NULL, "
            "step_no INTEGER NOT NULL, "
            "action TEXT DEFAULT '', "
            "expected_result TEXT DEFAULT '', "
            "step_type VARCHAR(30) DEFAULT 'action', "
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
            ")"
        ))
        connection.execute(text(
            "CREATE TABLE IF NOT EXISTS ai_feedback_samples ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "negative_sample_id INTEGER NOT NULL, "
            "source_type VARCHAR(40) DEFAULT 'negative_sample', "
            "module_id VARCHAR(100) DEFAULT '', "
            "chunk_text TEXT DEFAULT '', "
            "metadata_json TEXT DEFAULT '', "
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
            ")"
        ))
        connection.execute(text(
            "UPDATE requirement_documents SET category = '需求文档' "
            "WHERE category IN ('认证中心', '支付中心') OR (category = '功能' AND title NOT LIKE '%接口%')"
        ))
        connection.execute(text(
            "UPDATE requirement_documents SET category = '接口文档' "
            "WHERE category = '功能' AND title LIKE '%接口%'"
        ))
        connection.commit()


def seed_demo_data():
    """初始化演示数据，便于前端原型直接联调"""
    from app.models.project import Project
    from app.models.api_info import APIInfo
    from app.models.test_case import TestCase
    from app.models.execution import ExecBatch, Execution
    from app.models.changelog import Changelog
    from app.models.requirement_document import RequirementDocument

    db = SessionLocal()
    try:
        existing_project = db.query(Project).first()
        if existing_project:
            return

        demo_project = Project(
            name="移动测试平台演示项目",
            description="用于联调前端页面的演示项目",
            base_url="https://api.demo.local",
            created_by="system",
        )
        db.add(demo_project)
        db.flush()

        login_api = APIInfo(
            project_id=demo_project.id,
            module="认证中心",
            name="用户登录",
            method="POST",
            path="/api/auth/login",
            description="用户通过账号密码登录",
            params_schema={
                "username": {"type": "string", "required": True, "description": "用户名"},
                "password": {"type": "string", "required": True, "description": "密码"},
            },
            request_body_example={"username": "demo_user", "password": "123456"},
            response_example={"token": "demo-token", "user_id": 1},
            success_status=200,
            tags=["登录", "P0"],
            created_by="system",
            updated_by="system",
        )
        profile_api = APIInfo(
            project_id=demo_project.id,
            module="用户中心",
            name="获取用户资料",
            method="GET",
            path="/api/users/profile",
            description="获取当前登录用户资料",
            params_schema={},
            request_body_example={},
            response_example={"id": 1, "nickname": "Demo User"},
            success_status=200,
            tags=["资料"],
            created_by="system",
            updated_by="system",
        )
        db.add_all([login_api, profile_api])
        db.flush()

        cases = [
            TestCase(
                api_id=login_api.id,
                name="登录成功-正常账号",
                description="使用正确的用户名密码登录",
                category="positive",
                priority="P0",
                request_data={"username": "demo_user", "password": "123456"},
                expected_status=200,
                expected_contains=["token"],
                source="manual",
                last_result="passed",
            ),
            TestCase(
                api_id=login_api.id,
                name="登录失败-密码错误",
                description="密码错误时应返回错误提示",
                category="negative",
                priority="P1",
                request_data={"username": "demo_user", "password": "wrong"},
                expected_status=401,
                expected_contains=["error"],
                source="ai_generated",
                last_result="failed",
            ),
            TestCase(
                api_id=profile_api.id,
                name="获取资料成功",
                description="带 token 获取资料成功",
                category="positive",
                priority="P1",
                request_headers={"Authorization": "Bearer demo-token"},
                expected_status=200,
                expected_contains=["nickname"],
                source="manual",
                last_result="passed",
            ),
        ]
        db.add_all(cases)
        db.flush()

        batch = ExecBatch(
            name="演示批次_登录回归",
            status="completed",
            total=3,
            passed=2,
            failed=1,
            errors=0,
            triggered_by="system",
        )
        db.add(batch)
        db.flush()

        executions = [
            Execution(
                batch_id=batch.id,
                case_id=cases[0].id,
                api_id=login_api.id,
                status="passed",
                request_snapshot={"url": "/api/auth/login", "method": "POST"},
                response_snapshot={"status_code": 200, "body": {"token": "demo-token"}},
                assertions=[{"type": "status_code", "passed": True}],
                response_time=420,
            ),
            Execution(
                batch_id=batch.id,
                case_id=cases[1].id,
                api_id=login_api.id,
                status="failed",
                request_snapshot={"url": "/api/auth/login", "method": "POST"},
                response_snapshot={"status_code": 500, "body": {"error": "internal error"}},
                assertions=[{"type": "status_code", "passed": False}],
                error_message="预期 401，实际返回 500",
                response_time=512,
            ),
            Execution(
                batch_id=batch.id,
                case_id=cases[2].id,
                api_id=profile_api.id,
                status="passed",
                request_snapshot={"url": "/api/users/profile", "method": "GET"},
                response_snapshot={"status_code": 200, "body": {"nickname": "Demo User"}},
                assertions=[{"type": "contains", "passed": True}],
                response_time=318,
            ),
        ]
        db.add_all(executions)

        changelog = Changelog(
            api_id=login_api.id,
            change_type="updated",
            old_value={"description": "旧版登录接口"},
            new_value={"description": "用户通过账号密码登录", "path": "/api/auth/login"},
            diff_summary="登录接口文案与路径说明已更新，建议复核 2 条断言",
            changed_fields=["description"],
            cases_synced=0,
            changed_by="system",
        )
        db.add(changelog)

        demo_doc = RequirementDocument(
            title="登录需求说明",
            file_name="login_requirement.md",
            file_type="md",
            file_path="./uploads/requirement_docs/login_requirement.md",
            file_size=256,
            category="需求文档",
            module="登录模块",
            dependency_scope="账号系统, 首页",
            dependency_notes="登录成功后依赖首页欢迎文案展示和 token 下发。",
            tags="登录,P0,回归",
            extracted_content=(
                "用户可以通过账号密码登录。用户名不能为空，密码不能为空。"
                "登录成功后进入首页并显示欢迎文案。登录失败时展示错误提示。"
            ),
            ai_summary="该文档描述了登录成功、失败提示和首页跳转三个核心需求点。",
            created_by="system",
        )
        db.add(demo_doc)

        db.commit()
        print("✅ 演示数据已初始化")
    finally:
        db.close()


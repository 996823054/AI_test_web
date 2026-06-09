"""
测试用例模型
============
存储手动创建和 AI 自动生成的测试用例
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class TestCase(Base):
    """
    测试用例表

    来源：
    - manual: 手动创建
    - ai_generated: AI 自动生成
    """
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(Integer, ForeignKey("api_infos.id"), nullable=False, comment="关联接口")

    # ===== 用例基本信息 =====
    name = Column(String(200), nullable=False, comment="用例名称")
    description = Column(Text, default="", comment="用例描述")
    case_kind = Column(String(20), default="api", comment="case 类型: api/automation/functional")
    category = Column(String(20), default="positive",
                      comment="用例类型: positive/boundary/negative/security")
    priority = Column(String(5), default="P1", comment="优先级: P0/P1/P2/P3")
    platform = Column(String(20), default="", comment="平台: api/web/android/ios")
    version_group = Column(String(100), default="", comment="版本分组，如 V1.0.0")
    source_document_id = Column(Integer, nullable=True, comment="来源需求文档ID")
    requirement_item_id = Column(Integer, nullable=True, comment="来源需求点ID")

    # ===== 请求内容 =====
    request_data = Column(JSON, default=dict, comment="请求参数/请求体")
    request_headers = Column(JSON, default=dict, comment="自定义请求头（覆盖接口默认头）")
    steps = Column(JSON, default=list, comment="步骤列表，功能/自动化 case 使用")
    precondition = Column(Text, default="", comment="前置条件")

    # ===== 期望结果 =====
    expected_status = Column(Integer, comment="期望状态码")
    expected_body = Column(JSON, default=dict, comment="期望响应体（部分匹配）")
    expected_contains = Column(JSON, default=list, comment="期望响应包含的关键字列表")
    expected_result = Column(Text, default="", comment="预期结果，功能/自动化 case 使用")
    dependency_consideration = Column(Text, default="", comment="上下游依赖关注点")

    # ===== 元信息 =====
    source = Column(String(20), default="manual", comment="来源: manual/ai_generated")
    lifecycle_status = Column(String(20), default="active", comment="生命周期: active/deprecated")
    trust_status = Column(String(30), default="formal", comment="可信分层: draft/formal/verified/high_value")
    module_delivery = Column(Integer, default=0, comment="模块完整交付标记")
    importance = Column(String(20), default="normal", comment="重要性: normal/high")
    confirmed_by = Column(String(50), default="", comment="确认人")
    confirmed_at = Column(DateTime, nullable=True, comment="确认时间")
    pending_reconfirm = Column(Integer, default=0, comment="关键字段变更待复核")
    current_version_no = Column(Integer, default=1, comment="当前版本号")
    is_active = Column(Integer, default=1, comment="是否启用: 1=启用 0=禁用")
    last_result = Column(String(20), default="", comment="最近一次执行结果")

    # ===== 废弃与变更关联元数据 =====
    deprecation_category = Column(String(50), nullable=True, comment="废弃分类: FEATURE_REMOVED/REDUNDANT/FLAKY/STALE_LOCATOR/OTHER")
    deprecation_reason = Column(Text, default="", comment="详细废弃原因")
    replaced_by_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=True, comment="替代的用例ID")
    change_record_id = Column(Integer, nullable=True, comment="关联的变更记录ID")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # ===== 关系 =====
    api = relationship("APIInfo", back_populates="test_cases")
    executions = relationship("Execution", back_populates="test_case", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "api_id": self.api_id,
            "name": self.name,
            "description": self.description,
            "case_kind": self.case_kind,
            "category": self.category,
            "priority": self.priority,
            "platform": self.platform,
            "version_group": self.version_group,
            "source_document_id": self.source_document_id,
            "requirement_item_id": self.requirement_item_id,
            "trust_status": self.trust_status or "formal",
            "module_delivery": self.module_delivery or 0,
            "importance": self.importance or "normal",
            "confirmed_by": self.confirmed_by or "",
            "confirmed_at": str(self.confirmed_at) if self.confirmed_at else None,
            "pending_reconfirm": self.pending_reconfirm or 0,
            "request_data": self.request_data or {},
            "request_headers": self.request_headers or {},
            "steps": self.steps or [],
            "precondition": self.precondition or "",
            "expected_status": self.expected_status,
            "expected_body": self.expected_body or {},
            "expected_contains": self.expected_contains or [],
            "expected_result": self.expected_result or "",
            "dependency_consideration": self.dependency_consideration or "",
            "source": self.source,
            "lifecycle_status": self.lifecycle_status or "active",
            "deprecation_category": self.deprecation_category or "",
            "deprecation_reason": self.deprecation_reason or "",
            "replaced_by_case_id": self.replaced_by_case_id,
            "change_record_id": self.change_record_id,
            "current_version_no": self.current_version_no or 1,
            "is_active": self.is_active,
            "last_result": self.last_result or "",
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }


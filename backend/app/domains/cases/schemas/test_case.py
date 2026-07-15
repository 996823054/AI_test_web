"""
测试用例 Schema
===============
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class TestCaseCreate(BaseModel):
    """创建测试用例"""
    api_id: Optional[int] = Field(default=None, description="关联接口ID")
    name: str = Field(..., min_length=1, description="用例名称")
    description: str = Field(default="", description="用例描述")
    case_kind: str = Field(default="api", description="case 类型: api/automation/functional")
    category: str = Field(default="positive",
                          description="类型: positive/boundary/negative/security")
    priority: str = Field(default="P1", description="优先级: P0/P1/P2/P3")
    platform: str = Field(default="api", description="平台: api/web/android/ios")
    version_group: str = Field(default="", description="版本分组")
    source_document_id: Optional[int] = Field(default=None, description="来源需求文档ID")
    requirement_item_id: Optional[int] = Field(default=None, description="来源需求点ID")
    trust_status: str = Field(default="formal", description="可信分层")
    module_delivery: int = Field(default=0, description="模块完整交付")
    importance: str = Field(default="normal", description="重要性")

    request_data: Dict[str, Any] = Field(default_factory=dict, description="请求参数")
    request_headers: Dict[str, str] = Field(default_factory=dict, description="自定义请求头")
    steps: List[str] = Field(default_factory=list, description="步骤列表")
    precondition: str = Field(default="", description="前置条件")

    expected_status: Optional[int] = Field(default=None, description="期望状态码")
    expected_body: Dict[str, Any] = Field(default_factory=dict, description="期望响应体")
    expected_contains: List[str] = Field(default_factory=list, description="期望包含关键字")
    expected_result: str = Field(default="", description="预期结果")
    dependency_consideration: str = Field(default="", description="依赖关注点")


class TestCaseUpdate(BaseModel):
    """更新测试用例"""
    name: Optional[str] = None
    description: Optional[str] = None
    case_kind: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    platform: Optional[str] = None
    version_group: Optional[str] = None
    source_document_id: Optional[int] = None
    requirement_item_id: Optional[int] = None
    trust_status: Optional[str] = None
    module_delivery: Optional[int] = None
    importance: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    request_headers: Optional[Dict[str, str]] = None
    steps: Optional[List[str]] = None
    precondition: Optional[str] = None
    expected_status: Optional[int] = None
    expected_body: Optional[Dict[str, Any]] = None
    expected_contains: Optional[List[str]] = None
    expected_result: Optional[str] = None
    dependency_consideration: Optional[str] = None
    is_active: Optional[int] = None


class TestCaseResponse(BaseModel):
    """测试用例响应"""
    id: int
    api_id: int
    name: str
    description: str = ""
    case_kind: str = "api"
    category: str = "positive"
    priority: str = "P1"
    platform: str = "api"
    version_group: str = ""
    source_document_id: Optional[int] = None
    requirement_item_id: Optional[int] = None
    trust_status: str = "formal"
    module_delivery: int = 0
    importance: str = "normal"
    confirmed_by: str = ""
    confirmed_at: Optional[datetime] = None
    pending_reconfirm: int = 0

    request_data: Dict[str, Any] = {}
    request_headers: Dict[str, str] = {}
    steps: List[str] = []
    precondition: str = ""

    expected_status: Optional[int] = None
    expected_body: Dict[str, Any] = {}
    expected_contains: List[str] = []
    expected_result: str = ""
    dependency_consideration: str = ""
    case_steps: List[Dict[str, Any]] = []

    source: str = "manual"
    lifecycle_status: str = "active"
    deprecation_category: str = ""
    deprecation_reason: str = ""
    replaced_by_case_id: Optional[int] = None
    change_record_id: Optional[int] = None
    current_version_no: int = 1
    is_active: int = 1
    last_result: str = ""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 额外信息
    api_name: str = Field(default="", description="关联接口名称")
    api: Optional[Dict[str, Any]] = None
    project_id: Optional[int] = None
    module: str = ""
    source_document: Optional[Dict[str, Any]] = None
    requirement_item: Optional[Dict[str, Any]] = None
    source_excerpt: str = ""
    ai_draft: Optional[Dict[str, Any]] = None
    version_history_count: int = 0
    health_info: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class TestCaseListResponse(BaseModel):
    """用例列表响应"""
    total: int
    page: int
    page_size: int
    items: List[TestCaseResponse]


class AIGenerateRequest(BaseModel):
    """AI 生成用例请求"""
    api_id: int = Field(..., description="接口ID")
    source_document_id: Optional[int] = Field(default=None, description="来源需求文档ID（若提供则校验已入库）")
    categories: List[str] = Field(
        default=["positive", "boundary", "negative", "security"],
        description="生成的用例类型"
    )
    count_per_category: int = Field(default=3, description="每种类型生成的条数")


class SyncAICasesRequest(BaseModel):
    """将 AI 生成结果同步到 case 模块"""
    document_id: int = Field(..., description="来源需求文档ID")
    version_group: str = Field(..., description="版本分组，如 V1.0.0")
    case_kind: str = Field(default="functional", description="同步为哪种 case，默认 functional")
    platform: str = Field(default="android", description="目标平台")
    created_by: str = Field(default="binwu", description="同步人")
    cases: List[Dict[str, Any]] = Field(default_factory=list, description="AI 生成的 case 列表")


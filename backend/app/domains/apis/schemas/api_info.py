"""
接口信息 Schema
===============
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class ParamSchema(BaseModel):
    """单个参数定义"""
    type: str = Field(default="string", description="参数类型: string/integer/boolean/number")
    required: bool = Field(default=False, description="是否必填")
    description: str = Field(default="", description="参数说明")
    min_length: Optional[int] = Field(default=None, description="最小长度(string)")
    max_length: Optional[int] = Field(default=None, description="最大长度(string)")
    min_value: Optional[float] = Field(default=None, alias="min", description="最小值(number)")
    max_value: Optional[float] = Field(default=None, alias="max", description="最大值(number)")
    format: Optional[str] = Field(default=None, description="格式: email/url/phone 等")
    enum: Optional[List[str]] = Field(default=None, description="枚举值列表")

    class Config:
        populate_by_name = True


# ===== 创建接口 =====
class APIInfoCreate(BaseModel):
    """创建接口请求体"""
    project_id: int = Field(..., description="所属项目ID")
    module: str = Field(default="", description="所属模块")
    name: str = Field(..., min_length=1, max_length=200, description="接口名称")
    method: str = Field(..., description="请求方法: GET/POST/PUT/DELETE/PATCH")
    path: str = Field(..., min_length=1, description="接口路径")
    description: str = Field(default="", description="接口描述")

    headers: Dict[str, str] = Field(default_factory=dict, description="默认请求头")
    params_schema: Dict[str, Any] = Field(default_factory=dict, description="参数定义")
    request_body_example: Dict[str, Any] = Field(default_factory=dict, description="请求体示例")

    response_schema: Dict[str, Any] = Field(default_factory=dict, description="响应结构")
    response_example: Dict[str, Any] = Field(default_factory=dict, description="响应示例")
    success_status: int = Field(default=200, description="成功状态码")

    tags: List[str] = Field(default_factory=list, description="标签")
    created_by: str = Field(default="", description="创建人")

    auto_generate_cases: bool = Field(default=False, description="保存后是否自动生成测试用例")


# ===== 更新接口 =====
class APIInfoUpdate(BaseModel):
    """更新接口请求体（所有字段可选）"""
    module: Optional[str] = None
    name: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    description: Optional[str] = None

    headers: Optional[Dict[str, str]] = None
    params_schema: Optional[Dict[str, Any]] = None
    request_body_example: Optional[Dict[str, Any]] = None

    response_schema: Optional[Dict[str, Any]] = None
    response_example: Optional[Dict[str, Any]] = None
    success_status: Optional[int] = None

    tags: Optional[List[str]] = None
    status: Optional[str] = None
    updated_by: str = Field(default="", description="修改人")


# ===== 响应模型 =====
class APIInfoResponse(BaseModel):
    """接口信息响应"""
    id: int
    project_id: int
    module: str
    name: str
    method: str
    path: str
    description: str

    headers: Dict[str, str] = {}
    params_schema: Dict[str, Any] = {}
    request_body_example: Dict[str, Any] = {}

    response_schema: Dict[str, Any] = {}
    response_example: Dict[str, Any] = {}
    success_status: int = 200

    tags: List[str] = []
    status: str = "active"
    version: int = 1

    created_by: str = ""
    updated_by: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 额外统计
    case_count: int = Field(default=0, description="关联用例数")

    class Config:
        from_attributes = True


class APIInfoListResponse(BaseModel):
    """接口列表响应（带分页）"""
    total: int
    page: int
    page_size: int
    items: List[APIInfoResponse]


class ApiEnvironmentConfig(BaseModel):
    """接口调试环境配置"""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    base_url: str = ""
    headers: Dict[str, str] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    timeout: int = Field(default=30, ge=1, le=300)


class ApiVariableSetConfig(BaseModel):
    """接口变量集配置"""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    variables: Dict[str, Any] = Field(default_factory=dict)


class ApiAuthProfileConfig(BaseModel):
    """接口鉴权配置"""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    type: str = Field(default="none", description="none/bearer/api_key/basic/custom")
    config: Dict[str, Any] = Field(default_factory=dict)


class ApiModuleSettings(BaseModel):
    """接口模块配置"""

    environments: List[ApiEnvironmentConfig] = Field(default_factory=list)
    variable_sets: List[ApiVariableSetConfig] = Field(default_factory=list)
    auth_profiles: List[ApiAuthProfileConfig] = Field(default_factory=list)


class ApiImportRequest(BaseModel):
    """接口导入解析请求"""

    content: str = Field(..., min_length=1, description="OpenAPI/Postman/Markdown/文本内容")
    source_type: str = Field(default="auto", description="auto/openapi/postman/markdown/text")
    project_id: int = Field(default=1)
    module: str = Field(default="")
    save: bool = Field(default=False, description="是否直接保存为接口定义")
    created_by: str = Field(default="system")


class ApiImportResponse(BaseModel):
    """接口导入解析响应"""

    success: bool = True
    count: int = 0
    items: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ApiDefinitionDebugRequest(BaseModel):
    """基于接口定义发起调试"""

    environment_id: str = Field(default="default")
    variable_set_id: str = Field(default="default")
    auth_profile_id: str = Field(default="none")
    headers: Dict[str, str] = Field(default_factory=dict)
    params: Dict[str, Any] = Field(default_factory=dict)
    body: Optional[Any] = None
    assertions: List[Dict[str, Any]] = Field(default_factory=list)
    extract: List[Dict[str, Any]] = Field(default_factory=list)
    timeout: Optional[int] = None


class ApiBatchDebugRequest(BaseModel):
    """批量调试接口"""

    api_ids: List[int] = Field(default_factory=list)
    environment_id: str = Field(default="default")
    variable_set_id: str = Field(default="default")
    auth_profile_id: str = Field(default="none")
    timeout: Optional[int] = None


class ApiSaveCaseRequest(BaseModel):
    """将接口调试配置保存为接口 case"""

    name: str = Field(..., min_length=1)
    description: str = ""
    priority: str = "P1"
    category: str = "positive"
    request_config: Dict[str, Any] = Field(default_factory=dict)
    assertions: List[Dict[str, Any]] = Field(default_factory=list)
    created_by: str = "system"

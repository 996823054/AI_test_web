"""
执行记录 Schema
===============
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class ExecuteSingleRequest(BaseModel):
    """执行单条用例"""
    case_id: int = Field(..., description="用例ID")
    base_url: Optional[str] = Field(default=None, description="基础URL（覆盖默认值）")


class ExecuteBatchRequest(BaseModel):
    """批量执行请求"""
    case_ids: Optional[List[int]] = Field(default=None, description="用例ID列表")
    api_id: Optional[int] = Field(default=None, description="接口ID（执行该接口所有用例）")
    project_id: Optional[int] = Field(default=None, description="项目ID（执行该项目所有用例）")
    base_url: Optional[str] = Field(default=None, description="基础URL（覆盖默认值）")
    triggered_by: str = Field(default="", description="触发人")


class ApiAssertion(BaseModel):
    """单接口调试断言配置"""

    type: str = Field(..., description="断言类型: status_code/json_equals/json_contains/body_contains/max_response_time/header_equals")
    path: Optional[str] = Field(default=None, description="JSON 字段路径，如 data.token 或 $.data.token")
    expected: Optional[Any] = Field(default=None, description="期望值")
    contains: Optional[str] = Field(default=None, description="期望包含的文本")
    header: Optional[str] = Field(default=None, description="响应头名称")


class ApiVariableExtraction(BaseModel):
    """单接口调试变量提取配置"""

    name: str = Field(..., min_length=1, description="变量名")
    path: str = Field(..., description="JSON 字段路径，如 data.token 或 $.data.token")
    source: str = Field(default="body", description="提取来源: body/header")


class ApiDebugRequest(BaseModel):
    """单接口调试请求"""

    base_url: str = Field(default="", description="基础 URL，如 https://api.example.com")
    method: str = Field(default="GET", description="请求方法")
    path: str = Field(..., min_length=1, description="接口路径或完整 URL")
    headers: Dict[str, str] = Field(default_factory=dict, description="请求头")
    params: Dict[str, Any] = Field(default_factory=dict, description="Query 参数")
    body: Optional[Any] = Field(default=None, description="JSON 请求体")
    timeout: int = Field(default=30, ge=1, le=300, description="请求超时时间，单位秒")
    assertions: List[ApiAssertion] = Field(default_factory=list, description="断言配置")
    extract: List[ApiVariableExtraction] = Field(default_factory=list, description="变量提取配置")
    variables: Dict[str, Any] = Field(default_factory=dict, description="临时变量")
    auth: Dict[str, Any] = Field(default_factory=dict, description="临时鉴权配置")
    environment_id: str = Field(default="default", description="环境配置 ID")
    variable_set_id: str = Field(default="default", description="变量集 ID")
    auth_profile_id: str = Field(default="none", description="鉴权配置 ID")


class ApiDebugResponse(BaseModel):
    """单接口调试响应"""

    status: str
    request_snapshot: Dict[str, Any] = Field(default_factory=dict)
    response_snapshot: Dict[str, Any] = Field(default_factory=dict)
    assertions: List[Dict[str, Any]] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    response_time: int = 0
    error_message: str = ""


class ExecutionResponse(BaseModel):
    """执行结果响应"""
    id: int
    batch_id: Optional[int] = None
    case_id: int
    api_id: int
    status: str
    request_snapshot: Dict[str, Any] = {}
    response_snapshot: Dict[str, Any] = {}
    assertions: List[Dict[str, Any]] = []
    error_message: str = ""
    response_time: int = 0
    executed_at: Optional[datetime] = None

    # 额外信息
    case_name: str = Field(default="", description="用例名称")
    api_name: str = Field(default="", description="接口名称")

    class Config:
        from_attributes = True


class BatchResultResponse(BaseModel):
    """批次执行结果响应"""
    batch_id: int
    name: str = ""
    status: str
    total: int
    passed: int
    failed: int
    errors: int
    pass_rate: str = "0%"
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    details: List[ExecutionResponse] = []


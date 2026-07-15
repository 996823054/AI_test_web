"""
Midscene iOS automation routes
==============================
Expose iOS environment checks and single-run automation through FastAPI.
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.midscene_ios_runner import (
    DEFAULT_WDA_HOST,
    DEFAULT_WDA_PORT,
    MidsceneIOSRunnerService,
)


router = APIRouter()


class WDACheckRequest(BaseModel):
    """WebDriverAgent connectivity check request."""

    wda_host: str = Field(DEFAULT_WDA_HOST, description="WDA host")
    wda_port: int = Field(DEFAULT_WDA_PORT, ge=1, le=65535, description="WDA port")


class MidsceneModelConfig(BaseModel):
    """Optional Midscene model override for one run."""

    name: Optional[str] = Field(None, description="MIDSCENE_MODEL_NAME")
    api_key: Optional[str] = Field(None, description="MIDSCENE_MODEL_API_KEY")
    base_url: Optional[str] = Field(None, description="MIDSCENE_MODEL_BASE_URL")


class MidsceneIOSRunRequest(BaseModel):
    """Single Midscene iOS automation run request."""

    task_name: str = Field("Midscene iOS 单条调试", min_length=1, max_length=120)
    wda_host: str = Field(DEFAULT_WDA_HOST, description="WDA host")
    wda_port: int = Field(DEFAULT_WDA_PORT, ge=1, le=65535, description="WDA port")
    wda_mjpeg_port: Optional[int] = Field(None, ge=1, le=65535)
    device_id: Optional[str] = Field(None, description="Optional iOS device UDID")
    app: Optional[str] = Field(None, description="App name, bundle id or URL to launch")
    steps: list[str] = Field(default_factory=list, description="Natural language actions")
    assertions: list[str] = Field(default_factory=list, description="Natural language assertions")
    model: Optional[MidsceneModelConfig] = None
    timeout: int = Field(300, ge=30, le=1800, description="Runner timeout in seconds")


@router.get("/health", summary="Midscene iOS 环境检查")
def health() -> dict[str, Any]:
    service = MidsceneIOSRunnerService()
    return service.health()


@router.post("/check-wda", summary="检查 WebDriverAgent 连通性")
def check_wda(request: WDACheckRequest) -> dict[str, Any]:
    service = MidsceneIOSRunnerService()
    return service.check_wda(host=request.wda_host, port=request.wda_port)


@router.post("/run", summary="执行 Midscene iOS 单条任务")
def run_midscene_ios(request: MidsceneIOSRunRequest) -> dict[str, Any]:
    if not request.steps and not request.assertions:
        raise HTTPException(status_code=400, detail="请至少提供一个执行步骤或断言")

    service = MidsceneIOSRunnerService()
    payload = request.model_dump(exclude={"timeout"}, exclude_none=True)
    return service.run(payload=payload, timeout=request.timeout)

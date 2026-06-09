"""
AI 视觉自动化路由
================
当前作为占位接口，便于主应用正常启动。
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="视觉自动化健康检查")
def health():
    return {
        "status": "ok",
        "module": "vision_automation",
        "message": "视觉自动化模块占位路由已启用",
    }
"""
AI 视觉自动化路由
=================

提供 Web API 接口，让前端可以调用 AI 视觉自动化能力。
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "./uploads/screenshots"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===== 请求/响应模型 =====

class LocateRequest(BaseModel):
    """元素定位请求"""
    description: str
    screenshot_path: Optional[str] = None

class ActionRequest(BaseModel):
    """操作执行请求"""
    instruction: str
    screenshot_path: Optional[str] = None

class QueryRequest(BaseModel):
    """数据提取请求"""
    question: str
    screenshot_path: Optional[str] = None

class AssertRequest(BaseModel):
    """断言验证请求"""
    assertion: str
    screenshot_path: Optional[str] = None

class TestFlowStep(BaseModel):
    """测试流程步骤"""
    instruction: str

class TestFlowRequest(BaseModel):
    """测试流程请求"""
    task_desc: str
    steps: List[str]
    assertions: Optional[List[str]] = []
    mode: str = "mock"
    device_serial: Optional[str] = ""

class VisionResponse(BaseModel):
    """视觉分析响应"""
    success: bool
    action: str
    text: str = ""
    coordinates: Optional[List[int]] = None
    data: Optional[dict] = None
    error: str = ""
    duration: float = 0.0


# ===== API 路由 =====

@router.post("/locate", response_model=VisionResponse, summary="AI 定位元素")
async def locate_element(request: LocateRequest):
    """
    用自然语言描述定位 UI 元素

    示例: "登录按钮"、"搜索框"、"购物车图标"
    """
    from app.services.vision_engine import VisionAI

    if not request.screenshot_path:
        raise HTTPException(400, "请提供截图路径或先上传截图")

    ai = VisionAI()
    result = ai.ai_locate(request.screenshot_path, request.description)

    return VisionResponse(
        success=result.success,
        action=result.action,
        text=result.text,
        coordinates=list(result.coordinates) if result.coordinates else None,
        data=result.data if isinstance(result.data, dict) else None,
        error=result.error,
        duration=result.duration,
    )


@router.post("/action", response_model=VisionResponse, summary="AI 规划操作")
async def plan_action(request: ActionRequest):
    """
    用自然语言描述要执行的操作，AI 分析截图并规划步骤

    示例: "输入用户名 admin 并点击登录"
    """
    from app.services.vision_engine import VisionAI

    if not request.screenshot_path:
        raise HTTPException(400, "请提供截图路径或先上传截图")

    ai = VisionAI()
    result = ai.ai_action(request.screenshot_path, request.instruction)

    return VisionResponse(
        success=result.success,
        action=result.action,
        text=result.text,
        data={"steps": result.data} if result.data else None,
        error=result.error,
        duration=result.duration,
    )


@router.post("/query", response_model=VisionResponse, summary="AI 提取界面数据")
async def query_ui(request: QueryRequest):
    """
    用自然语言提问，从截图中提取数据

    示例: "页面上有哪些商品？价格分别是多少？"
    """
    from app.services.vision_engine import VisionAI

    if not request.screenshot_path:
        raise HTTPException(400, "请提供截图路径或先上传截图")

    ai = VisionAI()
    result = ai.ai_query(request.screenshot_path, request.question)

    return VisionResponse(
        success=result.success,
        action=result.action,
        text=result.text,
        data={"answer": result.text, "extracted": result.data},
        error=result.error,
        duration=result.duration,
    )


@router.post("/assert", response_model=VisionResponse, summary="AI 断言验证")
async def assert_ui(request: AssertRequest):
    """
    用自然语言描述断言条件，AI 分析截图判断是否满足

    示例: "页面显示了登录成功提示"
    """
    from app.services.vision_engine import VisionAI

    if not request.screenshot_path:
        raise HTTPException(400, "请提供截图路径或先上传截图")

    ai = VisionAI()
    result = ai.ai_assert(request.screenshot_path, request.assertion)

    return VisionResponse(
        success=result.success,
        action=result.action,
        text=result.text,
        data=result.data if isinstance(result.data, dict) else None,
        error=result.error,
        duration=result.duration,
    )


@router.post("/upload-screenshot", summary="上传截图")
async def upload_screenshot(file: UploadFile = File(...)):
    """上传截图文件，返回文件路径供后续 API 使用"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"upload_{timestamp}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"filepath": filepath, "filename": filename}


@router.post("/run-flow", summary="执行完整测试流程")
async def run_test_flow(request: TestFlowRequest):
    """
    执行一组自然语言测试步骤 + 断言

    示例::

        {
          "task_desc": "登录功能测试",
          "steps": [
            "点击用户名输入框并输入 admin",
            "点击密码输入框并输入 123456",
            "点击登录按钮",
            "等待 2 秒"
          ],
          "assertions": [
            "页面跳转到了首页",
            "页面显示了欢迎信息"
          ],
          "mode": "mock"
        }
    """
    if request.mode == "mock":
        from app.services.vision_executor import MockVisionAgent
        agent = MockVisionAgent()
    elif request.mode == "adb":
        from app.services.vision_executor import VisionAgent
        agent = VisionAgent(mode="adb", device_serial=request.device_serial or "")
    else:
        raise HTTPException(400, f"不支持的模式: {request.mode}，可选: mock / adb")

    report = agent.run_test_flow(
        task_desc=request.task_desc,
        steps=request.steps,
        assertions=request.assertions or [],
    )

    return {
        "task_id": report.task_id,
        "task_desc": report.task_desc,
        "status": report.status,
        "total_steps": report.total_steps,
        "passed_steps": report.passed_steps,
        "failed_steps": report.failed_steps,
        "total_duration": round(report.total_duration, 2),
        "started_at": report.started_at,
        "finished_at": report.finished_at,
        "steps": [
            {
                "step_index": s.step_index,
                "instruction": s.instruction,
                "action": s.action,
                "success": s.success,
                "duration": round(s.duration, 2),
                "error": s.error,
            }
            for s in report.steps
        ],
    }


@router.get("/capabilities", summary="查看视觉自动化能力")
async def get_capabilities():
    """返回 AI 视觉自动化支持的功能列表"""
    return {
        "name": "AI Vision Automation (Python Midscene)",
        "version": "1.0.0",
        "apis": [
            {
                "name": "ai_locate",
                "endpoint": "/locate",
                "description": "用自然语言定位 UI 元素，返回坐标",
                "example": '{"description": "登录按钮"}',
            },
            {
                "name": "ai_action",
                "endpoint": "/action",
                "description": "用自然语言描述操作，AI 规划执行步骤",
                "example": '{"instruction": "输入用户名 admin 并点击登录"}',
            },
            {
                "name": "ai_query",
                "endpoint": "/query",
                "description": "用自然语言提问，从界面提取数据",
                "example": '{"question": "页面上有哪些菜单项？"}',
            },
            {
                "name": "ai_assert",
                "endpoint": "/assert",
                "description": "用自然语言描述断言，验证界面状态",
                "example": '{"assertion": "登录成功提示已显示"}',
            },
            {
                "name": "run_flow",
                "endpoint": "/run-flow",
                "description": "执行完整测试流程（步骤 + 断言）",
                "example": '{"task_desc": "登录测试", "steps": [...], "assertions": [...]}',
            },
        ],
        "supported_models": [
            "gpt-4o (推荐)",
            "gpt-4-vision-preview",
            "qwen-vl-max (通义千问)",
            "gemini-pro-vision (Google)",
            "doubao-vision (字节豆包)",
        ],
        "supported_modes": ["adb (Android)", "appium (Android/iOS)", "mock (演示)"],
    }

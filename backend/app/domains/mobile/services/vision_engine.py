"""
AI 视觉引擎
===========
类似 Midscene.js 的核心能力，用 Python 实现。

原理：截图 → 发送给多模态 AI → 解析坐标/文本 → 执行操作

支持模型：GPT-4o / Qwen-VL / Gemini Pro Vision 等多模态模型
"""

import os
import re
import json
import base64
import time
import subprocess
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field

from app.config import settings


@dataclass
class VisionResult:
    """视觉分析结果"""
    success: bool
    action: str = ""
    coordinates: Optional[Tuple[int, int]] = None
    text: str = ""
    data: Any = None
    screenshot_path: str = ""
    raw_response: str = ""
    error: str = ""
    duration: float = 0.0


class ScreenCapture:
    """
    屏幕截图工具

    支持三种截图方式：
    1. ADB（Android，无需 Appium）
    2. Appium Driver
    3. 本地文件
    """

    def __init__(self, screenshot_dir: str = "./screenshots"):
        self.screenshot_dir = screenshot_dir
        os.makedirs(screenshot_dir, exist_ok=True)

    def capture_adb(self, device_serial: str = "") -> str:
        """通过 ADB 截图（Android）"""
        timestamp = int(time.time() * 1000)
        filepath = os.path.join(self.screenshot_dir, f"screen_{timestamp}.png")

        cmd = ["adb"]
        if device_serial:
            cmd.extend(["-s", device_serial])
        cmd.extend(["exec-out", "screencap", "-p"])

        try:
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            if result.returncode == 0:
                with open(filepath, "wb") as f:
                    f.write(result.stdout)
                return filepath
            raise RuntimeError(f"ADB 截图失败: {result.stderr.decode()}")
        except FileNotFoundError:
            raise RuntimeError("ADB 未安装或不在 PATH 中")

    def capture_appium(self, driver) -> str:
        """通过 Appium Driver 截图"""
        timestamp = int(time.time() * 1000)
        filepath = os.path.join(self.screenshot_dir, f"screen_{timestamp}.png")
        driver.save_screenshot(filepath)
        return filepath

    def from_file(self, filepath: str) -> str:
        """直接使用已有截图"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"截图文件不存在: {filepath}")
        return filepath

    @staticmethod
    def to_base64(filepath: str) -> str:
        """将图片转为 base64 编码"""
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")


class VisionAI:
    """
    AI 视觉分析引擎

    核心能力（对标 Midscene.js）：
    - ai_locate(描述)   → 定位元素坐标
    - ai_action(指令)   → 规划并返回操作步骤
    - ai_query(问题)    → 从界面提取数据
    - ai_assert(断言)   → 验证界面状态
    """

    def __init__(self, model: str = "", api_key: str = "", base_url: str = ""):
        self.model = model or os.getenv("VISION_MODEL") or settings.LLM_MODEL or "gpt-4o"
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = base_url or settings.LLM_BASE_URL
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                kwargs = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self._client = OpenAI(**kwargs)
            except ImportError:
                raise RuntimeError("请安装 openai 库: pip install openai")
        return self._client

    def _call_vision(self, image_base64: str, prompt: str,
                     system_prompt: str = "") -> str:
        """调用多模态 AI 分析图片"""
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}",
                        "detail": "high",
                    },
                },
            ],
        })

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=4096,
        )
        return response.choices[0].message.content

    def ai_locate(self, image_path: str, description: str) -> VisionResult:
        """
        定位元素 —— 对标 Midscene 的 aiLocate()

        输入：截图 + "登录按钮" 这样的自然语言描述
        输出：元素的中心坐标 (x, y)
        """
        start = time.time()
        image_b64 = ScreenCapture.to_base64(image_path)

        system_prompt = """你是一个 UI 元素定位专家。用户会给你一张 App/网页截图和一个元素描述。
你需要找到该元素并返回其中心点坐标。

必须严格按以下 JSON 格式返回：
{"found": true, "x": 320, "y": 580, "element_desc": "登录按钮", "confidence": 0.95}

如果找不到元素：
{"found": false, "x": 0, "y": 0, "element_desc": "", "confidence": 0, "reason": "未找到该元素"}

只返回 JSON，不要其他内容。"""

        prompt = f'请在截图中找到以下元素的位置："{description}"'

        try:
            raw = self._call_vision(image_b64, prompt, system_prompt)
            data = self._parse_json(raw)

            if data.get("found"):
                return VisionResult(
                    success=True,
                    action="locate",
                    coordinates=(data["x"], data["y"]),
                    text=data.get("element_desc", description),
                    data=data,
                    screenshot_path=image_path,
                    raw_response=raw,
                    duration=time.time() - start,
                )
            return VisionResult(
                success=False, action="locate",
                error=data.get("reason", "未找到元素"),
                raw_response=raw, duration=time.time() - start,
            )
        except Exception as e:
            return VisionResult(
                success=False, action="locate", error=str(e),
                duration=time.time() - start,
            )

    def ai_action(self, image_path: str, instruction: str) -> VisionResult:
        """
        规划操作步骤 —— 对标 Midscene 的 aiAction()

        输入：截图 + "输入用户名 test 并点击登录"
        输出：操作步骤列表（含坐标）
        """
        start = time.time()
        image_b64 = ScreenCapture.to_base64(image_path)

        system_prompt = """你是一个 App/网页自动化操作专家。用户给你一张截图和一个操作指令。
你需要分析截图，将指令拆解为具体的操作步骤。

每个步骤必须包含操作类型和精确坐标。

必须严格按以下 JSON 格式返回：
{
  "steps": [
    {"action": "tap", "x": 200, "y": 300, "description": "点击用户名输入框"},
    {"action": "input", "x": 200, "y": 300, "text": "test", "description": "输入用户名"},
    {"action": "tap", "x": 200, "y": 500, "description": "点击登录按钮"},
    {"action": "swipe", "from_x": 200, "from_y": 600, "to_x": 200, "to_y": 200, "description": "向上滑动"},
    {"action": "wait", "seconds": 2, "description": "等待页面加载"}
  ]
}

支持的 action 类型：tap（点击）、input（输入文字）、swipe（滑动）、wait（等待）、long_press（长按）
只返回 JSON，不要其他内容。"""

        prompt = f'请根据截图分析并执行以下操作："{instruction}"'

        try:
            raw = self._call_vision(image_b64, prompt, system_prompt)
            data = self._parse_json(raw)
            steps = data.get("steps", [])

            return VisionResult(
                success=len(steps) > 0,
                action="plan",
                data=steps,
                text=instruction,
                screenshot_path=image_path,
                raw_response=raw,
                duration=time.time() - start,
            )
        except Exception as e:
            return VisionResult(
                success=False, action="plan", error=str(e),
                duration=time.time() - start,
            )

    def ai_query(self, image_path: str, question: str) -> VisionResult:
        """
        提取界面数据 —— 对标 Midscene 的 aiQuery()

        输入：截图 + "页面上有哪些商品？价格分别是多少？"
        输出：结构化数据
        """
        start = time.time()
        image_b64 = ScreenCapture.to_base64(image_path)

        system_prompt = """你是一个 UI 数据提取专家。用户给你一张截图和一个问题。
请分析截图并回答问题，提取需要的数据。

必须严格按以下 JSON 格式返回：
{
  "answer": "你的回答文本",
  "data": 提取的结构化数据（可以是列表、字典等）,
  "confidence": 0.95
}

只返回 JSON，不要其他内容。"""

        prompt = f"请分析截图并回答：{question}"

        try:
            raw = self._call_vision(image_b64, prompt, system_prompt)
            data = self._parse_json(raw)

            return VisionResult(
                success=True,
                action="query",
                text=data.get("answer", ""),
                data=data.get("data"),
                screenshot_path=image_path,
                raw_response=raw,
                duration=time.time() - start,
            )
        except Exception as e:
            return VisionResult(
                success=False, action="query", error=str(e),
                duration=time.time() - start,
            )

    def ai_assert(self, image_path: str, assertion: str) -> VisionResult:
        """
        验证界面状态 —— 对标 Midscene 的 aiAssert()

        输入：截图 + "页面上显示了登录成功的提示"
        输出：True/False + 原因
        """
        start = time.time()
        image_b64 = ScreenCapture.to_base64(image_path)

        system_prompt = """你是一个 UI 测试断言专家。用户给你一张截图和一个断言条件。
请判断截图中是否满足该断言条件。

必须严格按以下 JSON 格式返回：
{
  "passed": true,
  "reason": "截图中可以看到'登录成功'提示文字",
  "confidence": 0.95
}

只返回 JSON，不要其他内容。"""

        prompt = f'请验证截图是否满足以下条件："{assertion}"'

        try:
            raw = self._call_vision(image_b64, prompt, system_prompt)
            data = self._parse_json(raw)

            return VisionResult(
                success=data.get("passed", False),
                action="assert",
                text=data.get("reason", ""),
                data=data,
                screenshot_path=image_path,
                raw_response=raw,
                duration=time.time() - start,
            )
        except Exception as e:
            return VisionResult(
                success=False, action="assert", error=str(e),
                duration=time.time() - start,
            )

    def _parse_json(self, text: str) -> dict:
        """从 AI 响应中提取 JSON"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        match = re.search(r"[{\[][\s\S]*[}\]]", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return {"error": "无法解析 AI 响应", "raw": text}

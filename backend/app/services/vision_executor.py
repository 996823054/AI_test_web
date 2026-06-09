"""
AI 视觉自动化执行器
===================
将 AI 视觉分析结果转化为实际的设备操作。

两种执行方式：
1. ADB 模式：直接通过 adb 命令操作（轻量，无需 Appium）
2. Appium 模式：通过 Appium Driver 操作（功能更全）

使用方式类似 Midscene.js：
    agent = VisionAgent(mode="adb")
    agent.ai_action("点击登录按钮")
    agent.ai_action("输入用户名 test")
    result = agent.ai_assert("页面显示了首页")
"""

import os
import time
import subprocess
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

from app.services.vision_engine import VisionAI, ScreenCapture, VisionResult


@dataclass
class StepRecord:
    """单步操作记录"""
    step_index: int
    instruction: str
    action: str
    coordinates: str
    success: bool
    duration: float
    screenshot_before: str = ""
    screenshot_after: str = ""
    error: str = ""
    ai_response: str = ""


@dataclass
class TaskReport:
    """任务执行报告"""
    task_id: str
    task_desc: str
    status: str  # passed / failed / error
    total_steps: int
    passed_steps: int
    failed_steps: int
    total_duration: float
    steps: List[StepRecord] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""


class DeviceController:
    """
    设备控制器 —— 通过 ADB 执行实际操作

    支持：点击、输入、滑动、长按、返回、截图
    无需 Appium，只要手机连了 USB 并开启 ADB 调试即可
    """

    def __init__(self, device_serial: str = ""):
        self.device_serial = device_serial

    def _adb(self, *args) -> subprocess.CompletedProcess:
        cmd = ["adb"]
        if self.device_serial:
            cmd.extend(["-s", self.device_serial])
        cmd.extend(args)
        return subprocess.run(cmd, capture_output=True, text=True, timeout=15)

    def tap(self, x: int, y: int):
        """点击指定坐标"""
        self._adb("shell", "input", "tap", str(x), str(y))

    def input_text(self, text: str):
        """输入文本（先清除再输入）"""
        escaped = text.replace(" ", "%s").replace("&", "\\&")
        self._adb("shell", "input", "text", escaped)

    def swipe(self, from_x: int, from_y: int, to_x: int, to_y: int,
              duration_ms: int = 500):
        """滑动"""
        self._adb("shell", "input", "swipe",
                  str(from_x), str(from_y), str(to_x), str(to_y),
                  str(duration_ms))

    def long_press(self, x: int, y: int, duration_ms: int = 1000):
        """长按"""
        self._adb("shell", "input", "swipe",
                  str(x), str(y), str(x), str(y), str(duration_ms))

    def press_back(self):
        """按返回键"""
        self._adb("shell", "input", "keyevent", "4")

    def press_home(self):
        """按 Home 键"""
        self._adb("shell", "input", "keyevent", "3")

    def get_screen_size(self) -> tuple:
        """获取屏幕分辨率"""
        result = self._adb("shell", "wm", "size")
        if result.returncode == 0:
            parts = result.stdout.strip().split()[-1].split("x")
            return int(parts[0]), int(parts[1])
        return 1080, 1920

    def is_connected(self) -> bool:
        """检查设备是否已连接"""
        result = self._adb("devices")
        lines = result.stdout.strip().split("\n")
        for line in lines[1:]:
            if "device" in line and "offline" not in line:
                return True
        return False


class VisionAgent:
    """
    AI 视觉自动化 Agent —— Python 版 Midscene

    用自然语言控制 App，AI 看截图来理解界面。

    使用示例::

        agent = VisionAgent(mode="adb")

        # 像说话一样写自动化
        agent.ai_action("点击用户名输入框")
        agent.ai_action("输入用户名 test_user")
        agent.ai_action("点击密码输入框")
        agent.ai_action("输入密码 123456")
        agent.ai_action("点击登录按钮")
        agent.ai_action("等待 2 秒")

        # 验证结果
        result = agent.ai_assert("页面显示了首页内容")
        print(f"登录测试: {'通过' if result.success else '失败'}")

        # 提取数据
        data = agent.ai_query("当前页面的用户名是什么？")
        print(f"用户名: {data.text}")
    """

    def __init__(self, mode: str = "adb", device_serial: str = "",
                 appium_driver=None, screenshot_dir: str = "./screenshots",
                 vision_model: str = "", api_key: str = "",
                 base_url: str = ""):
        """
        Args:
            mode: 执行模式 "adb"（轻量） 或 "appium"（功能全）
            device_serial: ADB 设备序列号（多设备时指定）
            appium_driver: Appium WebDriver 实例（appium 模式必传）
            screenshot_dir: 截图保存目录
            vision_model: 视觉模型名称（默认 gpt-4o）
            api_key: AI API Key
            base_url: AI API Base URL
        """
        self.mode = mode
        self.vision = VisionAI(
            model=vision_model, api_key=api_key, base_url=base_url,
        )
        self.capture = ScreenCapture(screenshot_dir)
        self.appium_driver = appium_driver
        self.step_records: List[StepRecord] = []
        self.step_counter = 0

        if mode == "adb":
            self.device = DeviceController(device_serial)
        else:
            self.device = None

    def _take_screenshot(self) -> str:
        """根据模式截图"""
        if self.mode == "adb":
            return self.capture.capture_adb(
                self.device.device_serial if self.device else "",
            )
        elif self.mode == "appium" and self.appium_driver:
            return self.capture.capture_appium(self.appium_driver)
        else:
            raise RuntimeError(f"无法截图: 模式={self.mode}")

    def ai_action(self, instruction: str) -> VisionResult:
        """
        执行自然语言指令 —— 对标 Midscene 的 aiAction()

        示例:
            agent.ai_action("点击登录按钮")
            agent.ai_action("输入用户名 admin 并点击确认")
            agent.ai_action("向下滑动查看更多")
        """
        self.step_counter += 1
        start = time.time()

        screenshot = self._take_screenshot()

        plan_result = self.vision.ai_action(screenshot, instruction)
        if not plan_result.success:
            record = StepRecord(
                step_index=self.step_counter,
                instruction=instruction,
                action="plan_failed",
                coordinates="",
                success=False,
                duration=time.time() - start,
                screenshot_before=screenshot,
                error=plan_result.error,
                ai_response=plan_result.raw_response,
            )
            self.step_records.append(record)
            return plan_result

        steps = plan_result.data or []
        for step in steps:
            self._execute_device_action(step)
            time.sleep(0.3)

        after_screenshot = self._take_screenshot()

        record = StepRecord(
            step_index=self.step_counter,
            instruction=instruction,
            action=json.dumps(steps, ensure_ascii=False) if steps else "",
            coordinates=str([(s.get("x"), s.get("y")) for s in steps]),
            success=True,
            duration=time.time() - start,
            screenshot_before=screenshot,
            screenshot_after=after_screenshot,
            ai_response=plan_result.raw_response,
        )
        self.step_records.append(record)
        plan_result.screenshot_path = after_screenshot
        return plan_result

    def ai_locate(self, description: str) -> VisionResult:
        """
        定位元素 —— 对标 Midscene 的 aiLocate()

        示例:
            result = agent.ai_locate("搜索框")
            print(f"坐标: {result.coordinates}")
        """
        screenshot = self._take_screenshot()
        return self.vision.ai_locate(screenshot, description)

    def ai_query(self, question: str) -> VisionResult:
        """
        提取界面数据 —— 对标 Midscene 的 aiQuery()

        示例:
            result = agent.ai_query("页面上有哪些菜单项？")
            print(result.data)
        """
        screenshot = self._take_screenshot()
        return self.vision.ai_query(screenshot, question)

    def ai_assert(self, assertion: str) -> VisionResult:
        """
        断言验证 —— 对标 Midscene 的 aiAssert()

        示例:
            result = agent.ai_assert("登录成功提示已显示")
            assert result.success, f"断言失败: {result.text}"
        """
        screenshot = self._take_screenshot()
        return self.vision.ai_assert(screenshot, assertion)

    def ai_wait_for(self, condition: str, timeout: int = 30,
                    interval: float = 2.0) -> VisionResult:
        """
        等待某个条件满足 —— 对标 Midscene 的 aiWaitFor()

        示例:
            agent.ai_wait_for("页面加载完成，显示了首页内容", timeout=15)
        """
        start = time.time()
        last_result = None

        while time.time() - start < timeout:
            result = self.ai_assert(condition)
            if result.success:
                return result
            last_result = result
            time.sleep(interval)

        if last_result:
            last_result.error = f"等待超时({timeout}s): {condition}"
        return last_result or VisionResult(
            success=False, action="wait_for",
            error=f"等待超时({timeout}s)",
        )

    def _execute_device_action(self, step: Dict):
        """将 AI 规划的步骤转化为实际设备操作"""
        action = step.get("action", "")

        if action == "tap":
            x, y = step.get("x", 0), step.get("y", 0)
            if self.mode == "adb":
                self.device.tap(x, y)
            elif self.appium_driver:
                from appium.webdriver.common.touch_action import TouchAction
                TouchAction(self.appium_driver).tap(x=x, y=y).perform()

        elif action == "input":
            text = step.get("text", "")
            x, y = step.get("x", 0), step.get("y", 0)
            if self.mode == "adb":
                if x and y:
                    self.device.tap(x, y)
                    time.sleep(0.2)
                self.device.input_text(text)
            elif self.appium_driver:
                if x and y:
                    from appium.webdriver.common.touch_action import TouchAction
                    TouchAction(self.appium_driver).tap(x=x, y=y).perform()
                    time.sleep(0.2)
                self.appium_driver.press_keycode(text)

        elif action == "swipe":
            fx = step.get("from_x", 0)
            fy = step.get("from_y", 0)
            tx = step.get("to_x", 0)
            ty = step.get("to_y", 0)
            if self.mode == "adb":
                self.device.swipe(fx, fy, tx, ty)
            elif self.appium_driver:
                self.appium_driver.swipe(fx, fy, tx, ty, 500)

        elif action == "long_press":
            x, y = step.get("x", 0), step.get("y", 0)
            ms = step.get("duration_ms", 1000)
            if self.mode == "adb":
                self.device.long_press(x, y, ms)

        elif action == "wait":
            seconds = step.get("seconds", 1)
            time.sleep(seconds)

    def run_test_flow(self, task_desc: str,
                      steps: List[str],
                      assertions: List[str] = None) -> TaskReport:
        """
        执行完整测试流程

        Args:
            task_desc: 任务描述
            steps: 操作步骤列表（自然语言）
            assertions: 断言列表（自然语言）

        示例::

            report = agent.run_test_flow(
                task_desc="登录功能测试",
                steps=[
                    "点击用户名输入框并输入 admin",
                    "点击密码输入框并输入 123456",
                    "点击登录按钮",
                    "等待 2 秒",
                ],
                assertions=[
                    "页面跳转到了首页",
                    "页面显示了用户头像",
                ]
            )
        """
        self.step_records = []
        self.step_counter = 0
        started = datetime.now()
        failed_steps = 0

        for step_text in steps:
            result = self.ai_action(step_text)
            if not result.success:
                failed_steps += 1

        if assertions:
            for assertion in assertions:
                result = self.ai_assert(assertion)
                self.step_counter += 1
                record = StepRecord(
                    step_index=self.step_counter,
                    instruction=f"[断言] {assertion}",
                    action="assert",
                    coordinates="",
                    success=result.success,
                    duration=result.duration,
                    error=result.error if not result.success else "",
                    ai_response=result.raw_response,
                )
                self.step_records.append(record)
                if not result.success:
                    failed_steps += 1

        finished = datetime.now()
        total_duration = (finished - started).total_seconds()
        passed_steps = len(self.step_records) - failed_steps

        return TaskReport(
            task_id=f"TASK_{started.strftime('%Y%m%d_%H%M%S')}",
            task_desc=task_desc,
            status="passed" if failed_steps == 0 else "failed",
            total_steps=len(self.step_records),
            passed_steps=passed_steps,
            failed_steps=failed_steps,
            total_duration=total_duration,
            steps=self.step_records,
            started_at=started.isoformat(),
            finished_at=finished.isoformat(),
        )


class MockVisionAgent(VisionAgent):
    """
    模拟 Agent（不需要真实设备和 AI）

    用于演示和测试流程
    """

    def __init__(self, **kwargs):
        self.step_records: List[StepRecord] = []
        self.step_counter = 0
        self.mode = "mock"

    def _take_screenshot(self) -> str:
        return "mock_screenshot.png"

    def ai_action(self, instruction: str) -> VisionResult:
        self.step_counter += 1
        time.sleep(0.2)
        print(f"  [模拟] 执行: {instruction}")

        record = StepRecord(
            step_index=self.step_counter,
            instruction=instruction,
            action="mock",
            coordinates="(540, 960)",
            success=True,
            duration=0.2,
        )
        self.step_records.append(record)

        return VisionResult(
            success=True, action="action",
            text=instruction, duration=0.2,
            data=[{"action": "tap", "x": 540, "y": 960,
                   "description": instruction}],
        )

    def ai_locate(self, description: str) -> VisionResult:
        print(f"  [模拟] 定位: {description}")
        return VisionResult(
            success=True, action="locate",
            coordinates=(540, 960), text=description, duration=0.1,
        )

    def ai_query(self, question: str) -> VisionResult:
        print(f"  [模拟] 查询: {question}")
        return VisionResult(
            success=True, action="query",
            text="模拟查询结果", data={"answer": "模拟数据"}, duration=0.1,
        )

    def ai_assert(self, assertion: str) -> VisionResult:
        print(f"  [模拟] 断言: {assertion}")
        return VisionResult(
            success=True, action="assert",
            text="断言通过", duration=0.1,
        )

    def ai_wait_for(self, condition: str, timeout: int = 30,
                    interval: float = 2.0) -> VisionResult:
        print(f"  [模拟] 等待: {condition}")
        return VisionResult(
            success=True, action="wait_for", text="条件已满足", duration=0.5,
        )


# 需要 json 导入
import json

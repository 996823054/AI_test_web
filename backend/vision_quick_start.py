#!/usr/bin/env python3
"""
AI 视觉自动化 - 快速体验
========================

无需真实设备和 AI Key，即可体验完整流程。

运行方式:
    python vision_quick_start.py
"""

import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def demo_basic_usage():
    """演示 1：基本用法 —— 像说话一样写自动化"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║             AI 视觉自动化 - Python 版 Midscene              ║
║                                                              ║
║   核心理念：用自然语言写自动化，AI 看截图理解界面             ║
╚══════════════════════════════════════════════════════════════╝
    """)

    print("=" * 60)
    print("  演示 1：基本用法")
    print("=" * 60)

    print("""
# 传统方式（需要写 XPath / ID）：
    driver.find_element(By.XPATH, '//android.widget.EditText[@resource-id="username"]').click()
    driver.find_element(By.XPATH, '//android.widget.EditText[@resource-id="username"]').send_keys("admin")
    driver.find_element(By.ID, 'com.app:id/login_btn').click()

# AI 视觉方式（只需说人话）：
    agent.ai_action("点击用户名输入框")
    agent.ai_action("输入用户名 admin")
    agent.ai_action("点击登录按钮")
    """)

    from app.services.vision_executor import MockVisionAgent

    agent = MockVisionAgent()
    print("--- 开始模拟执行 ---\n")

    agent.ai_action("点击用户名输入框")
    agent.ai_action("输入用户名 admin")
    agent.ai_action("点击密码输入框")
    agent.ai_action("输入密码 123456")
    agent.ai_action("点击登录按钮")
    time.sleep(0.3)
    agent.ai_action("等待 2 秒")

    result = agent.ai_assert("页面显示了首页内容")
    print(f"\n  断言结果: {'通过 ✅' if result.success else '失败 ❌'}")

    data = agent.ai_query("当前页面的用户名是什么？")
    print(f"  查询结果: {data.text}")

    locate = agent.ai_locate("设置按钮")
    print(f"  定位结果: 坐标 {locate.coordinates}\n")


def demo_test_flow():
    """演示 2：完整测试流程"""
    print("=" * 60)
    print("  演示 2：完整测试流程")
    print("=" * 60)

    from app.services.vision_executor import MockVisionAgent

    agent = MockVisionAgent()

    print("\n--- 执行登录功能测试 ---\n")

    report = agent.run_test_flow(
        task_desc="登录功能测试",
        steps=[
            "点击用户名输入框并输入 admin",
            "点击密码输入框并输入 123456",
            "点击记住密码复选框",
            "点击登录按钮",
            "等待 2 秒",
        ],
        assertions=[
            "页面跳转到了首页",
            "页面显示了欢迎信息",
            "底部导航栏可见",
        ],
    )

    print(f"""
╔══════════════════════════════════════════╗
║            测试报告                      ║
╠══════════════════════════════════════════╣
║  任务: {report.task_desc:<30s}  ║
║  状态: {'通过 ✅' if report.status == 'passed' else '失败 ❌':<30s}  ║
║  总步骤: {report.total_steps:<28d}  ║
║  通过: {report.passed_steps:<30d}  ║
║  失败: {report.failed_steps:<30d}  ║
║  耗时: {report.total_duration:.2f}s{' ':<26s}  ║
╚══════════════════════════════════════════╝
    """)

    print("  步骤详情:")
    for step in report.steps:
        icon = "✅" if step.success else "❌"
        print(f"    {icon} [{step.step_index}] {step.instruction}")


def demo_comparison():
    """演示 3：对比传统自动化 vs AI 视觉自动化"""
    print("\n" + "=" * 60)
    print("  演示 3：传统方式 vs AI 视觉方式")
    print("=" * 60)

    print("""
┌────────────────────────────────────────────────────────────────┐
│                 传统 Appium 自动化                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  # 需要精确的元素定位符                                          │
│  username = driver.find_element(                               │
│      By.XPATH,                                                 │
│      '//android.widget.EditText[@resource-id="username"]'      │
│  )                                                             │
│  username.click()                                              │
│  username.send_keys("admin")                                   │
│                                                                │
│  password = driver.find_element(By.ID, "com.app:id/password")  │
│  password.send_keys("123456")                                  │
│                                                                │
│  login_btn = driver.find_element(By.ID, "com.app:id/login")   │
│  login_btn.click()                                             │
│                                                                │
│  # 断言也需要定位                                                │
│  welcome = driver.find_element(By.ID, "com.app:id/welcome")   │
│  assert welcome.is_displayed()                                 │
│                                                                │
│  问题：                                                         │
│  ❌ UI 改了 ID/XPath 就挂了                                     │
│  ❌ 需要开发提供元素标识                                          │
│  ❌ 维护成本高                                                   │
│  ❌ 不同分辨率可能定位失败                                        │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                 AI 视觉自动化（类 Midscene）                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  agent = VisionAgent(mode="adb")                               │
│                                                                │
│  agent.ai_action("在用户名输入框输入 admin")                     │
│  agent.ai_action("在密码输入框输入 123456")                      │
│  agent.ai_action("点击登录按钮")                                 │
│                                                                │
│  result = agent.ai_assert("页面显示了欢迎信息")                  │
│  assert result.success                                         │
│                                                                │
│  优势：                                                         │
│  ✅ UI 改了布局也能找到元素（AI 看截图识别）                      │
│  ✅ 不需要知道元素 ID/XPath                                     │
│  ✅ 像说话一样写测试                                             │
│  ✅ 适配不同分辨率                                               │
│  ✅ 非技术人员也能写自动化                                       │
└────────────────────────────────────────────────────────────────┘
    """)


def demo_real_code():
    """演示 4：真实使用的代码模板"""
    print("=" * 60)
    print("  演示 4：可以直接用的代码模板")
    print("=" * 60)

    print("""
# ============================================================
# 模板 1：连接真实 Android 设备（ADB 模式）
# ============================================================

from app.services.vision_executor import VisionAgent

# 初始化（需要手机连 USB 并开启 ADB 调试）
agent = VisionAgent(
    mode="adb",                           # 用 ADB，不需要 Appium
    vision_model="gpt-4o",                # 多模态模型
    api_key="your-api-key",               # OpenAI Key
)

# 执行测试
agent.ai_action("打开设置应用")
agent.ai_action("点击 WLAN 选项")
data = agent.ai_query("当前连接的 WiFi 名称是什么？")
print(f"WiFi: {data.text}")

# ============================================================
# 模板 2：使用国产模型（通义千问 VL）
# ============================================================

agent = VisionAgent(
    mode="adb",
    vision_model="qwen-vl-max",
    api_key="your-dashscope-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# ============================================================
# 模板 3：批量执行测试用例
# ============================================================

test_cases = [
    {
        "name": "登录成功",
        "steps": [
            "在用户名输入框输入 admin",
            "在密码输入框输入 123456",
            "点击登录按钮",
            "等待 3 秒",
        ],
        "assertions": ["页面显示了首页", "底部导航栏可见"],
    },
    {
        "name": "登录失败-密码错误",
        "steps": [
            "在用户名输入框输入 admin",
            "在密码输入框输入 wrong",
            "点击登录按钮",
        ],
        "assertions": ["页面显示了错误提示", "仍在登录页面"],
    },
]

for tc in test_cases:
    report = agent.run_test_flow(
        task_desc=tc["name"],
        steps=tc["steps"],
        assertions=tc["assertions"],
    )
    print(f"{tc['name']}: {report.status}")

# ============================================================
# 模板 4：通过 Web API 调用（前后端分离）
# ============================================================

import requests

BASE = "http://localhost:8000/api/vision"

# 上传截图
with open("screenshot.png", "rb") as f:
    resp = requests.post(f"{BASE}/upload-screenshot", files={"file": f})
    path = resp.json()["filepath"]

# AI 定位元素
resp = requests.post(f"{BASE}/locate", json={
    "description": "搜索框",
    "screenshot_path": path,
})
print(resp.json())

# 执行完整测试流程（Mock 模式）
resp = requests.post(f"{BASE}/run-flow", json={
    "task_desc": "搜索功能测试",
    "steps": ["点击搜索框", "输入 iPhone", "点击搜索按钮"],
    "assertions": ["搜索结果中包含 iPhone 相关商品"],
    "mode": "mock",
})
print(resp.json())
    """)


def demo_architecture():
    """演示 5：架构原理"""
    print("\n" + "=" * 60)
    print("  演示 5：架构原理")
    print("=" * 60)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│                    AI 视觉自动化架构                             │
│                                                                 │
│                                                                 │
│     你说的话              AI 做的事               设备执行       │
│     ────────             ──────────             ──────────       │
│                                                                 │
│   "点击登录按钮"  ──→  📱 截图（ADB/Appium）                    │
│                         ↓                                       │
│                   🤖 发送给 GPT-4o                               │
│                         ↓                                       │
│                   📍 返回坐标 (320, 580)                        │
│                         ↓                                       │
│                   👆 adb shell input tap 320 580                │
│                         ↓                                       │
│                   📱 再次截图验证                                 │
│                                                                 │
│                                                                 │
│   项目文件结构:                                                  │
│                                                                 │
│   backend/app/services/                                         │
│   ├── vision_engine.py      ← AI 视觉引擎（核心）               │
│   │   ├── ScreenCapture     ← 截图工具（ADB/Appium/文件）       │
│   │   └── VisionAI          ← AI 分析（定位/操作/查询/断言）     │
│   │                                                             │
│   └── vision_executor.py    ← 自动化执行器                      │
│       ├── DeviceController  ← ADB 设备控制                      │
│       ├── VisionAgent       ← 主 Agent（对标 Midscene）         │
│       └── MockVisionAgent   ← 模拟 Agent（演示用）              │
│                                                                 │
│   backend/app/routers/                                          │
│   └── vision_automation.py  ← Web API 路由                      │
│       ├── POST /locate      ← 定位元素                          │
│       ├── POST /action      ← 执行操作                          │
│       ├── POST /query       ← 提取数据                          │
│       ├── POST /assert      ← 断言验证                          │
│       └── POST /run-flow    ← 完整测试流程                      │
│                                                                 │
│                                                                 │
│   对标 Midscene.js:                                             │
│                                                                 │
│   Midscene (JS)              本项目 (Python)                    │
│   ─────────────              ──────────────                     │
│   aiAction("点击登录")   →   agent.ai_action("点击登录")        │
│   aiLocate("搜索框")    →   agent.ai_locate("搜索框")           │
│   aiQuery("获取价格")   →   agent.ai_query("获取价格")          │
│   aiAssert("已登录")    →   agent.ai_assert("已登录")           │
│   aiWaitFor("加载完成") →   agent.ai_wait_for("加载完成")       │
│                                                                 │
│   Puppeteer/Playwright   →   ADB / Appium                      │
│   Chrome Extension       →   Web API (FastAPI)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    demo_basic_usage()
    demo_test_flow()
    demo_comparison()
    demo_real_code()
    demo_architecture()

    print("\n" + "=" * 60)
    print("  下一步")
    print("=" * 60)
    print("""
  1. 连接真实设备:
     - 手机连 USB，开启开发者选项和 USB 调试
     - 运行 adb devices 确认设备已连接

  2. 配置 AI 模型:
     - 设置环境变量: export LLM_API_KEY="your-key"
     - 或在代码中指定: VisionAgent(api_key="your-key")

  3. 启动 Web 平台:
     - cd backend && python run.py
     - 访问 http://localhost:8000/docs 查看 API 文档
     - 在 "AI 视觉自动化" 分组下测试各接口

  4. 推荐模型:
     - GPT-4o（效果最好，需要 OpenAI Key）
     - 通义千问 qwen-vl-max（国内可用，阿里云 Key）
     - Gemini Pro Vision（Google，免费额度）
    """)

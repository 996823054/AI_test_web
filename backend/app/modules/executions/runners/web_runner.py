"""
Web 自动化执行器
================
封装 Web UI 自动化的执行逻辑（Selenium + VisionEngine）。

你需要实现 WebRunner 类（进阶功能）：

    __init__(self, db: Session)

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. run(self, url: str, steps: list) → dict
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    → 启动 Selenium WebDriver
    → 导航到 url
    → 调用 VisionExecutor.execute_flow(steps)
    → 关闭 driver
    → return 执行结果

提示：
    - 依赖 selenium、VisionEngine、VisionExecutor
    - 进阶功能占位，优先完成接口测试
"""

# TODO: 在这里实现 WebRunner 类（进阶功能）

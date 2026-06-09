"""
链路测试执行引擎
================
核心流程：解析步骤 → 变量替换 → 逐步执行 → 提取变量 → 传递给下一步

你需要实现两个类：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
类 1: VariableContext（变量上下文）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    管理步骤间的变量传递。

    方法：
        set(key, value)           → 存入变量
        get(key, default=None)    → 读取变量
        resolve(obj)              → 递归替换对象中的 {{variable}} 占位符
                                     支持 str / dict / list 递归
                                     "Bearer {{token}}" → "Bearer eyJ..."
                                     {"id": "{{order_id}}"} → {"id": 10086}

        extract_from_response(response_body, extract_rules)
                                  → 从响应 JSON 中按规则提取变量
                                     extract_rules: {"token": "$.data.token"}
                                     用 "." 分隔路径逐层取值
        to_dict()                 → 返回所有变量的字典

    提示：
        - resolve 是核心方法，需要处理三种情况：
          a) 整个值就是 {{var}} → 保留原始类型（数字、布尔等）
          b) 字符串中嵌入 {{var}} → 替换后还是字符串
          c) dict/list → 递归处理每个值
        - 用 re.fullmatch(r"\\{\\{(\\w+)\\}\\}", text) 判断是否完全匹配
        - 用 re.sub(r"\\{\\{(\\w+)\\}\\}", replacer, text) 替换嵌入的变量

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
类 2: FlowExecutorService（链路执行引擎）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    编排多个步骤的执行。

    方法：
        __init__(db, base_url)    → 初始化数据库会话和 requests.Session
        execute_flow(flow_id)     → 执行一条链路测试

    execute_flow 的流程：
        1. 从数据库查询 TestFlow
        2. 创建 ExecBatch 批次记录
        3. 初始化 VariableContext（注入 global_variables）
        4. 按 step_order 排序步骤
        5. 逐步执行 _execute_step
        6. 如果某步失败且 stop_on_fail=True，跳过后续步骤
        7. 更新批次统计（passed/failed/errors）
        8. 返回执行结果

    _execute_step(step, ctx, batch_id) 的流程：
        1. 从数据库查询 APIInfo（获取接口定义）
        2. 合并请求：接口默认值 + step.request_override
        3. 用 ctx.resolve() 替换 {{变量}}
        4. 发送 HTTP 请求
        5. 用 ctx.extract_from_response() 提取变量
        6. 执行断言
        7. 记录 Execution 到数据库
        8. 返回步骤结果

    _run_step_assertions(step, resp, resp_body) 的流程：
        支持的断言类型：
        - status_code:  resp.status_code == expected
        - body_field:   resp_body 中某字段 == expected（用 JSONPath 取值）
        - contains:     resp_body 中包含某关键字
        - not_empty:    resp_body 中某字段不为空

变量传递流程图：
    Step1 登录
      请求: {"username": "admin"}
      响应: {"data": {"token": "eyJ..."}}
      提取: token = "eyJ..."
              ↓ 存入 VariableContext
    Step2 创建订单
      请求头: "Authorization": "Bearer {{token}}"  → 替换为实际值
      响应: {"data": {"orderId": 10086}}
      提取: order_id = 10086
              ↓ 存入 VariableContext
    Step3 支付
      请求体: {"orderId": "{{order_id}}"}  → 替换为 10086

这个文件未来会成为“接口编排 / 场景编排”的核心执行文件。

你后续实现时请注意：
    - VariableContext 只负责变量管理，不要耦合数据库
    - FlowExecutorService 只负责编排执行，不要和普通单 case 执行混成一个类
    - 统一返回步骤级结果，方便前端执行详情页和实时日志页消费

建议最终返回结构至少包含：
    {
        "batch_id": ...,
        "status": ...,
        "steps": [...],
        "variables": {...},
        "summary": {...}
    }
"""

# import re
# import json
# import time
# import requests
# from datetime import datetime
# from typing import Dict, List, Any
# from sqlalchemy.orm import Session

# TODO: 在这里实现 VariableContext 和 FlowExecutorService

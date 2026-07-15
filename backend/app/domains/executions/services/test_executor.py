"""
测试执行服务
============
核心流程：加载用例 → 发送请求 → 执行断言 → 记录结果

当前这个文件已经能支撑“接口用例执行”，但还不是完整的平台级执行中心。

你后续补核心实现时建议按下面方向演进：
    1. 保留 execute_case / execute_batch 作为最小可用执行能力
    2. 再逐步抽出统一任务模型（Task / Batch / StepLog / Artifact）
    3. 将环境、变量、鉴权、重试策略从 execute_case 中解耦
    4. 为后续移动端执行预留统一执行结果结构

不要在当前阶段把这个文件扩展成“什么都管”的超级类。
建议新增而不是硬塞：
    - _build_request_context(...)
    - _record_execution_artifacts(...)
    - _normalize_result(...)
"""

import requests
import time
import base64
import re
from datetime import datetime
from typing import Any, List, Dict, Optional
from urllib.parse import urljoin

from sqlalchemy.orm import Session

from app.models.api_info import APIInfo
from app.models.test_case import TestCase
from app.models.execution import Execution, ExecBatch
from app.config import settings
from app.services.app_settings_service import AppSettingsService


class TestExecutorService:
    """测试执行引擎"""

    def __init__(self, db: Session, base_url: str = ""):
        self.db = db
        self.base_url = base_url or settings.DEFAULT_BASE_URL
        self.session = requests.Session()
        self.timeout = settings.REQUEST_TIMEOUT

    def execute_api_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """执行一条原始接口请求，用于单接口调试和 Runner 复用"""
        method = str(request.get("method") or "GET").upper()
        variables = request.get("variables") or {}
        base_url = self._render_template(request.get("base_url") or self.base_url, variables)
        path = self._render_template(request.get("path") or "", variables)
        headers = self._render_template(request.get("headers") or {}, variables)
        params = self._render_template(request.get("params") or {}, variables)
        body = self._render_template(request.get("body", None), variables)
        headers = self._apply_auth(headers, request.get("auth") or {}, variables)
        timeout = int(request.get("timeout") or self.timeout)
        assertions_config = request.get("assertions") or []
        extract_config = request.get("extract") or []
        url = self._build_url(base_url, path)

        request_snapshot = {
            "url": url,
            "method": method,
            "headers": self._mask_sensitive(headers),
            "params": self._mask_sensitive(params),
            "body": self._mask_sensitive(body),
            "timeout": timeout,
        }

        try:
            start_time = time.time()
            response = self.session.request(
                method=method,
                url=url,
                params=params or None,
                json=body if body is not None and method not in ("GET", "HEAD") else None,
                headers=headers,
                timeout=timeout,
            )
            elapsed_ms = int((time.time() - start_time) * 1000)
            response_body = self._parse_response_body(response)
            response_snapshot = {
                "status_code": response.status_code,
                "headers": self._mask_sensitive(dict(response.headers)),
                "body": self._mask_sensitive(response_body),
                "text": response.text[:5000],
            }
            variables = self._extract_variables(response, response_body, extract_config)
            assertions = self._run_api_assertions(response, response_body, elapsed_ms, assertions_config)
            status = "passed" if all(item.get("passed") for item in assertions) else "failed"
            if not assertions:
                status = "passed" if 200 <= response.status_code < 400 else "failed"

            return {
                "status": status,
                "request_snapshot": request_snapshot,
                "response_snapshot": response_snapshot,
                "assertions": assertions,
                "variables": variables,
                "response_time": elapsed_ms,
                "error_message": "",
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "request_snapshot": request_snapshot,
                "response_snapshot": {},
                "assertions": [],
                "variables": {},
                "response_time": timeout * 1000,
                "error_message": f"请求超时（{timeout}s）",
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "request_snapshot": request_snapshot,
                "response_snapshot": {},
                "assertions": [],
                "variables": {},
                "response_time": 0,
                "error_message": f"连接失败: {url}",
            }
        except Exception as e:
            return {
                "status": "error",
                "request_snapshot": request_snapshot,
                "response_snapshot": {},
                "assertions": [],
                "variables": {},
                "response_time": 0,
                "error_message": str(e),
            }

    def execute_case(self, case_id: int, batch_id: int = None) -> Dict:
        """执行单条测试用例"""

        # 1. 加载用例和接口信息
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not case:
            raise ValueError(f"用例不存在: {case_id}")
        if case.is_active != 1 or case.lifecycle_status == "deprecated":
            raise ValueError(f"用例已废弃或停用，禁止执行: {case_id}")

        api = self.db.query(APIInfo).filter(APIInfo.id == case.api_id).first()
        if not api:
            raise ValueError(f"关联接口不存在: {case.api_id}")

        request_data = case.request_data or {}
        params = request_data.get("params", {}) if isinstance(request_data, dict) else {}
        body = request_data.get("body", request_data) if isinstance(request_data, dict) else request_data
        if api.method.upper() in ("GET", "HEAD") and not params:
            params = request_data if isinstance(request_data, dict) else {}
            body = None

        assertions_config = self._build_case_assertions(case)
        environment_id = request_data.get("environment_id", "default") if isinstance(request_data, dict) else "default"
        variable_set_id = request_data.get("variable_set_id", "default") if isinstance(request_data, dict) else "default"
        auth_profile_id = request_data.get("auth_profile_id", "none") if isinstance(request_data, dict) else "none"
        api_context = self._load_api_context(environment_id, variable_set_id, auth_profile_id)
        result = self.execute_api_request({
            "base_url": self.base_url or api_context["base_url"],
            "method": api.method,
            "path": api.path,
            "headers": {**api_context["headers"], **(api.headers or {}), **(case.request_headers or {})},
            "params": params,
            "body": body,
            "timeout": api_context["timeout"] or self.timeout,
            "assertions": assertions_config,
            "extract": self._extract_case_variables(case),
            "variables": api_context["variables"],
            "auth": api_context["auth"],
        })

        execution = Execution(
            batch_id=batch_id,
            case_id=case_id,
            api_id=api.id,
            status=result["status"],
            request_snapshot=result["request_snapshot"],
            response_snapshot={
                **(result["response_snapshot"] or {}),
                "variables": result.get("variables") or {},
            },
            assertions=result["assertions"],
            response_time=result["response_time"],
            error_message=result["error_message"],
        )

        self.db.add(execution)

        # 更新用例的最近一次执行结果
        case.last_result = execution.status
        self.db.commit()

        return {
            "id": execution.id,
            "case_id": case_id,
            "case_name": case.name,
            "api_id": api.id,
            "api_name": api.name,
            "status": execution.status,
            "response_time": execution.response_time or 0,
            "assertions": execution.assertions or [],
            "request_snapshot": execution.request_snapshot or {},
            "response_snapshot": execution.response_snapshot or {},
            "error_message": execution.error_message or "",
        }

    def execute_batch(
        self,
        case_ids: Optional[List[int]] = None,
        api_id: Optional[int] = None,
        project_id: Optional[int] = None,
        triggered_by: str = "",
    ) -> Dict:
        """批量执行测试用例"""

        # 创建批次
        batch = ExecBatch(
            name=f"批次_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            status="running",
            triggered_by=triggered_by,
        )
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)

        # 确定要执行的用例
        cases = self._resolve_cases(case_ids, api_id, project_id)

        # 逐条执行
        results = []
        for case in cases:
            try:
                result = self.execute_case(case.id, batch_id=batch.id)
                results.append(result)
            except Exception as e:
                results.append({
                    "case_id": case.id,
                    "case_name": case.name,
                    "status": "error",
                    "error_message": str(e),
                })

        # 更新批次统计
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        errors = sum(1 for r in results if r.get("status") == "error")

        batch.total = len(results)
        batch.passed = passed
        batch.failed = failed
        batch.errors = errors
        batch.status = "completed"
        batch.finished_at = datetime.now()
        self.db.commit()

        return {
            "batch_id": batch.id,
            "name": batch.name,
            "status": "completed",
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": f"{(passed / len(results) * 100):.1f}%" if results else "0%",
            "started_at": batch.started_at,
            "finished_at": batch.finished_at,
            "details": results,
        }

    def _resolve_cases(
        self,
        case_ids: Optional[List[int]],
        api_id: Optional[int],
        project_id: Optional[int],
    ) -> List[TestCase]:
        """解析要执行的用例列表"""
        if case_ids:
            return self.db.query(TestCase).filter(
                TestCase.id.in_(case_ids),
                TestCase.is_active == 1,
                TestCase.lifecycle_status == "active",
            ).all()

        if api_id:
            return self.db.query(TestCase).filter(
                TestCase.api_id == api_id,
                TestCase.is_active == 1,
                TestCase.lifecycle_status == "active",
            ).all()

        if project_id:
            api_ids = [
                a.id for a in self.db.query(APIInfo).filter(
                    APIInfo.project_id == project_id,
                    APIInfo.status == "active",
                ).all()
            ]
            return self.db.query(TestCase).filter(
                TestCase.api_id.in_(api_ids),
                TestCase.is_active == 1,
                TestCase.lifecycle_status == "active",
            ).all()

        return []

    def _run_assertions(self, case: TestCase, response: requests.Response) -> List[Dict]:
        """执行断言"""
        assertions = []

        # 1. 状态码断言
        if case.expected_status:
            assertions.append({
                "type": "status_code",
                "expected": case.expected_status,
                "actual": response.status_code,
                "passed": response.status_code == case.expected_status,
            })

        # 2. 响应体字段断言
        if case.expected_body:
            try:
                actual_body = response.json()
                for key, expected_val in case.expected_body.items():
                    actual_val = actual_body.get(key)
                    assertions.append({
                        "type": "body_field",
                        "field": key,
                        "expected": expected_val,
                        "actual": actual_val,
                        "passed": actual_val == expected_val,
                    })
            except Exception:
                assertions.append({
                    "type": "body_parse",
                    "passed": False,
                    "error": "响应体不是有效JSON",
                })

        # 3. 包含关键字检查
        if case.expected_contains:
            body_text = response.text
            for keyword in case.expected_contains:
                assertions.append({
                    "type": "contains",
                    "keyword": keyword,
                    "passed": keyword in body_text,
                })

        return assertions

    def _build_url(self, base_url: str, path: str) -> str:
        """拼接基础 URL 和路径，同时允许 path 传完整 URL"""
        if path.startswith(("http://", "https://")):
            return path
        if not base_url:
            return path
        return urljoin(f"{base_url.rstrip('/')}/", path.lstrip("/"))

    def _parse_response_body(self, response: requests.Response) -> Any:
        try:
            return response.json()
        except Exception:
            return {"raw": response.text[:5000]}

    def _build_case_assertions(self, case: TestCase) -> List[Dict[str, Any]]:
        assertions = []
        if case.expected_status:
            assertions.append({"type": "status_code", "expected": case.expected_status})
        for path, expected in (case.expected_body or {}).items():
            assertions.append({"type": "json_equals", "path": path, "expected": expected})
        for keyword in (case.expected_contains or []):
            assertions.append({"type": "body_contains", "contains": keyword})
        return assertions

    def _extract_case_variables(self, case: TestCase) -> List[Dict[str, str]]:
        steps = case.steps or []
        extract_items = []
        for step in steps:
            if isinstance(step, dict) and step.get("extract"):
                extract = step["extract"]
                if isinstance(extract, list):
                    extract_items.extend(extract)
        return extract_items

    def _run_api_assertions(
        self,
        response: requests.Response,
        response_body: Any,
        elapsed_ms: int,
        assertions_config: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        assertions = []
        for item in assertions_config:
            assertion_type = item.get("type")
            expected = item.get("expected")
            path = item.get("path")
            result = {
                "type": assertion_type,
                "path": path,
                "expected": expected,
                "actual": None,
                "passed": False,
            }

            if assertion_type == "status_code":
                result["actual"] = response.status_code
                result["passed"] = response.status_code == expected
            elif assertion_type == "json_equals":
                actual = self._get_by_path(response_body, path)
                result["actual"] = actual
                result["passed"] = actual == expected
            elif assertion_type == "json_contains":
                actual = self._get_by_path(response_body, path)
                contains = item.get("contains", expected)
                result["actual"] = actual
                result["contains"] = contains
                result["passed"] = contains in actual if isinstance(actual, (str, list, dict)) else False
            elif assertion_type == "body_contains":
                contains = item.get("contains", expected)
                result["contains"] = contains
                result["actual"] = response.text[:5000]
                result["passed"] = str(contains) in response.text
            elif assertion_type == "max_response_time":
                result["actual"] = elapsed_ms
                result["passed"] = elapsed_ms <= int(expected)
            elif assertion_type == "header_equals":
                header_name = item.get("header") or path or ""
                actual = response.headers.get(header_name)
                result["header"] = header_name
                result["actual"] = actual
                result["passed"] = actual == expected
            else:
                result["error"] = f"不支持的断言类型: {assertion_type}"

            assertions.append(result)
        return assertions

    def _extract_variables(
        self,
        response: requests.Response,
        response_body: Any,
        extract_config: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        variables = {}
        for item in extract_config:
            name = item.get("name")
            path = item.get("path")
            source = item.get("source", "body")
            if not name or not path:
                continue
            if source == "header":
                variables[name] = response.headers.get(path)
            else:
                variables[name] = self._get_by_path(response_body, path)
        return self._mask_sensitive(variables)

    def _get_by_path(self, data: Any, path: Optional[str]) -> Any:
        if not path:
            return data
        normalized = path.strip()
        if normalized.startswith("$."):
            normalized = normalized[2:]
        elif normalized.startswith("$"):
            normalized = normalized[1:]
        current = data
        for part in normalized.split("."):
            if part == "":
                continue
            if isinstance(current, list) and part.isdigit():
                index = int(part)
                current = current[index] if index < len(current) else None
            elif isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def _mask_sensitive(self, value: Any) -> Any:
        sensitive_keys = {"password", "token", "authorization", "cookie", "secret", "api_key", "phone", "id_card"}
        if isinstance(value, dict):
            masked = {}
            for key, item in value.items():
                if str(key).lower() in sensitive_keys:
                    masked[key] = "***"
                else:
                    masked[key] = self._mask_sensitive(item)
            return masked
        if isinstance(value, list):
            return [self._mask_sensitive(item) for item in value]
        return value

    def _render_template(self, value: Any, variables: Dict[str, Any]) -> Any:
        """替换字符串中的 {{variable}} 占位符"""
        if isinstance(value, str):
            def replace(match):
                key = match.group(1).strip()
                return str(variables.get(key, match.group(0)))

            return re.sub(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}", replace, value)
        if isinstance(value, dict):
            return {key: self._render_template(item, variables) for key, item in value.items()}
        if isinstance(value, list):
            return [self._render_template(item, variables) for item in value]
        return value

    def _apply_auth(self, headers: Dict[str, str], auth: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, str]:
        auth_type = (auth or {}).get("type", "none")
        config = self._render_template((auth or {}).get("config", {}), variables)
        merged = {**(headers or {})}
        if auth_type == "bearer" and config.get("token"):
            merged["Authorization"] = f"Bearer {config['token']}"
        elif auth_type == "api_key" and config.get("key"):
            key = config.get("key")
            value = config.get("value", "")
            location = config.get("in", "header")
            if location == "header":
                merged[key] = value
        elif auth_type == "basic" and config.get("username") is not None:
            raw = f"{config.get('username', '')}:{config.get('password', '')}"
            merged["Authorization"] = f"Basic {base64.b64encode(raw.encode()).decode()}"
        elif auth_type == "custom":
            merged.update(config.get("headers", {}))
        return merged

    def _load_api_context(self, environment_id: str, variable_set_id: str, auth_profile_id: str) -> Dict[str, Any]:
        settings_data = AppSettingsService().get_api_module_settings(masked=False)
        environment = self._find_by_id(settings_data.get("environments", []), environment_id)
        variable_set = self._find_by_id(settings_data.get("variable_sets", []), variable_set_id)
        auth_profile = self._find_by_id(settings_data.get("auth_profiles", []), auth_profile_id)
        variables = {
            **(environment.get("variables") or {}),
            **(variable_set.get("variables") or {}),
        }
        return {
            "base_url": environment.get("base_url", ""),
            "headers": environment.get("headers", {}),
            "variables": variables,
            "auth": auth_profile,
            "timeout": environment.get("timeout"),
        }

    def _find_by_id(self, items: List[Dict[str, Any]], item_id: str) -> Dict[str, Any]:
        for item in items:
            if item.get("id") == item_id:
                return item
        return items[0] if items else {}

    def list_batches(self, page: int = 1, page_size: int = 20) -> Dict:
        """获取执行批次列表"""
        query = self.db.query(ExecBatch)
        total = query.count()

        items = query.order_by(ExecBatch.started_at.desc()) \
                     .offset((page - 1) * page_size) \
                     .limit(page_size) \
                     .all()

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [b.to_dict() for b in items],
        }

    def get_batch_detail(self, batch_id: int) -> Optional[Dict]:
        """获取批次执行详情"""
        batch = self.db.query(ExecBatch).filter(ExecBatch.id == batch_id).first()
        if not batch:
            return None

        executions = self.db.query(Execution).filter(
            Execution.batch_id == batch_id
        ).all()

        details = []
        for exe in executions:
            case = self.db.query(TestCase).filter(TestCase.id == exe.case_id).first()
            api = self.db.query(APIInfo).filter(APIInfo.id == exe.api_id).first()
            detail = exe.to_dict()
            detail["case_name"] = case.name if case else ""
            detail["api_name"] = api.name if api else ""
            details.append(detail)

        result = batch.to_dict()
        result["details"] = details
        return result

    def get_case_history(self, case_id: int, limit: int = 10) -> List[Dict]:
        """获取用例执行历史"""
        executions = self.db.query(Execution).filter(
            Execution.case_id == case_id
        ).order_by(Execution.executed_at.desc()).limit(limit).all()

        return [e.to_dict() for e in executions]


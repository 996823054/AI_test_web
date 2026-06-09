"""
接口管理服务
============
接口信息的 CRUD 业务逻辑

这个 service 是接口中心的核心服务，后续建议继续保持“单一职责”：
    - 这里只处理接口资产本身
    - 不在这里写 HTTP 调用逻辑
    - 不在这里写 AI 推理逻辑

你后续优先补的能力：
    1. 环境管理
       - 不要继续把环境信息散落在接口字段里
       - 建议拆成独立 Environment 模型
    2. 变量管理
       - 支持公共变量、环境变量、步骤变量
    3. 鉴权配置
       - 支持 Bearer / API Key / Basic Auth 模板化配置
    4. 覆盖关系
       - 返回接口与 case、报告、变更记录的聚合信息
"""

import json
from typing import Any, Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.execution import Execution
from app.models.api_info import APIInfo
from app.models.changelog import Changelog
from app.models.test_case import TestCase
from app.schemas.api_info import APIInfoCreate, APIInfoUpdate
from app.services.app_settings_service import AppSettingsService
from app.services.test_executor import TestExecutorService
from app.skills.interface_parse_skill import InterfaceParseSkill


class APIManagerService:
    """接口管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_apis(
        self,
        project_id: Optional[int] = None,
        module: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        """获取接口列表"""
        query = self.db.query(APIInfo)

        # 筛选条件
        if project_id:
            query = query.filter(APIInfo.project_id == project_id)
        if module:
            query = query.filter(APIInfo.module == module)
        if status:
            query = query.filter(APIInfo.status == status)
        if keyword:
            query = query.filter(
                or_(
                    APIInfo.name.contains(keyword),
                    APIInfo.path.contains(keyword),
                    APIInfo.description.contains(keyword),
                )
            )

        # 总数
        total = query.count()

        # 分页
        items = query.order_by(APIInfo.updated_at.desc()) \
                     .offset((page - 1) * page_size) \
                     .limit(page_size) \
                     .all()

        # 附加用例数
        result_items = []
        for api in items:
            api_dict = api.to_dict()
            api_dict["case_count"] = self.db.query(TestCase).filter(
                TestCase.api_id == api.id, TestCase.is_active == 1
            ).count()
            result_items.append(api_dict)

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": result_items,
        }

    def get_api(self, api_id: int) -> Optional[APIInfo]:
        """获取单个接口"""
        return self.db.query(APIInfo).filter(APIInfo.id == api_id).first()

    def get_api_detail(self, api_id: int) -> Optional[Dict[str, Any]]:
        api = self.get_api(api_id)
        if not api:
            return None
        detail = api.to_dict()
        detail["coverage"] = self.get_api_coverage(api_id)
        return detail

    def create_api(self, data: APIInfoCreate) -> APIInfo:
        """创建接口"""
        api_info = APIInfo(
            project_id=data.project_id,
            module=data.module,
            name=data.name,
            method=data.method.upper(),
            path=data.path,
            description=data.description,
            headers=data.headers,
            params_schema=data.params_schema,
            request_body_example=data.request_body_example,
            response_schema=data.response_schema,
            response_example=data.response_example,
            success_status=data.success_status,
            tags=data.tags,
            created_by=data.created_by,
        )
        self.db.add(api_info)
        self.db.commit()
        self.db.refresh(api_info)
        return api_info

    def update_api(self, api_id: int, data: APIInfoUpdate) -> Optional[APIInfo]:
        """更新接口"""
        api_info = self.get_api(api_id)
        if not api_info:
            return None

        # 只更新提供了的字段
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(api_info, field):
                setattr(api_info, field, value)

        # 版本号 +1
        api_info.version = (api_info.version or 0) + 1

        self.db.commit()
        self.db.refresh(api_info)
        return api_info

    def deprecate_api(self, api_id: int) -> bool:
        """废弃接口"""
        api_info = self.get_api(api_id)
        if not api_info:
            return False

        api_info.status = "deprecated"
        self.db.commit()
        return True

    def import_apis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """解析接口文档并按需保存为接口定义"""
        content = payload.get("content", "")
        source_type = payload.get("source_type", "auto")
        project_id = payload.get("project_id") or 1
        module = payload.get("module") or ""
        save = bool(payload.get("save"))
        created_by = payload.get("created_by", "system")
        warnings: List[str] = []

        items = self._parse_structured_api_docs(content, source_type)
        if not items:
            skill_result = InterfaceParseSkill().run({"content": content})
            data = skill_result.data.get("api_definition", {}) if skill_result.data else {}
            items = [self._normalize_import_item(data, project_id, module, created_by)]
            warnings.extend(skill_result.warnings or [])
        else:
            items = [self._normalize_import_item(item, project_id, module, created_by) for item in items]

        if save:
            saved_items = []
            for item in items:
                api_info = self.create_api(APIInfoCreate(**item))
                saved_items.append(api_info.to_dict())
            items = saved_items

        return {"success": True, "count": len(items), "items": items, "warnings": warnings}

    def debug_api_definition(self, api_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """基于已保存接口定义进行调试"""
        api = self.get_api(api_id)
        if not api:
            raise ValueError(f"接口不存在: {api_id}")

        request_payload = self.build_debug_payload(api, payload)
        executor = TestExecutorService(self.db, base_url=request_payload.get("base_url", ""))
        return executor.execute_api_request(request_payload)

    def debug_batch(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """批量调试接口定义"""
        api_ids = payload.get("api_ids") or []
        if not api_ids:
            api_ids = [row.id for row in self.db.query(APIInfo).filter(APIInfo.status == "active").limit(20).all()]

        results = []
        for api_id in api_ids:
            try:
                result = self.debug_api_definition(api_id, payload)
                api = self.get_api(api_id)
                result["api_id"] = api_id
                result["api_name"] = api.name if api else ""
                results.append(result)
            except Exception as exc:
                results.append({"api_id": api_id, "status": "error", "error_message": str(exc)})

        passed = sum(1 for item in results if item.get("status") == "passed")
        failed = sum(1 for item in results if item.get("status") == "failed")
        errors = sum(1 for item in results if item.get("status") == "error")
        return {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": f"{(passed / len(results) * 100):.1f}%" if results else "0%",
            "items": results,
        }

    def save_debug_as_case(self, api_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """把调试配置保存为接口 case"""
        api = self.get_api(api_id)
        if not api:
            raise ValueError(f"接口不存在: {api_id}")

        request_config = payload.get("request_config") or {}
        assertions = payload.get("assertions") or request_config.get("assertions") or []
        expected_status = None
        expected_body = {}
        expected_contains = []
        for assertion in assertions:
            if assertion.get("type") == "status_code":
                expected_status = assertion.get("expected")
            elif assertion.get("type") == "json_equals" and assertion.get("path"):
                expected_body[assertion["path"]] = assertion.get("expected")
            elif assertion.get("type") == "body_contains":
                expected_contains.append(assertion.get("contains") or assertion.get("expected"))

        case = TestCase(
            api_id=api_id,
            name=payload.get("name") or f"{api.name} 调试用例",
            description=payload.get("description", ""),
            case_kind="api",
            category=payload.get("category", "positive"),
            priority=payload.get("priority", "P1"),
            platform="api",
            request_data={
                "params": request_config.get("params", {}),
                "body": request_config.get("body"),
                "environment_id": request_config.get("environment_id", "default"),
                "variable_set_id": request_config.get("variable_set_id", "default"),
                "auth_profile_id": request_config.get("auth_profile_id", "none"),
            },
            request_headers=request_config.get("headers", {}),
            steps=[{"action": "api_request", "api_id": api_id, "extract": request_config.get("extract", [])}],
            expected_status=expected_status or api.success_status,
            expected_body=expected_body,
            expected_contains=[item for item in expected_contains if item],
            expected_result="接口响应满足断言配置",
            source="manual",
        )
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case.to_dict()

    def get_api_coverage(self, api_id: int) -> Dict[str, Any]:
        """获取接口关联 case、执行、变更和风险摘要"""
        cases = self.db.query(TestCase).filter(TestCase.api_id == api_id, TestCase.is_active == 1).all()
        executions = (
            self.db.query(Execution)
            .filter(Execution.api_id == api_id)
            .order_by(Execution.executed_at.desc())
            .limit(10)
            .all()
        )
        changelogs = (
            self.db.query(Changelog)
            .filter(Changelog.api_id == api_id)
            .order_by(Changelog.changed_at.desc())
            .limit(10)
            .all()
        )
        failed_count = sum(1 for item in executions if item.status in ("failed", "error"))
        unsynced_count = sum(1 for item in changelogs if item.cases_synced == 0)
        return {
            "api_id": api_id,
            "case_count": len(cases),
            "recent_execution_count": len(executions),
            "recent_failed_count": failed_count,
            "unsynced_change_count": unsynced_count,
            "risk_level": "high" if failed_count or unsynced_count else "normal",
            "cases": [case.to_dict() for case in cases],
            "recent_executions": [execution.to_dict() for execution in executions],
            "changelogs": [log.to_dict() for log in changelogs],
        }

    def build_debug_payload(self, api: APIInfo, payload: Dict[str, Any]) -> Dict[str, Any]:
        """合并接口定义、环境、变量集和鉴权配置"""
        context = self._load_debug_context(payload)
        environment = context["environment"]
        variables = context["variables"]
        auth_profile = context["auth_profile"]
        headers = {
            **(environment.get("headers") or {}),
            **(api.headers or {}),
            **(payload.get("headers") or {}),
        }

        request_payload = {
            "base_url": payload.get("base_url") or environment.get("base_url", ""),
            "method": api.method,
            "path": api.path,
            "headers": headers,
            "params": payload.get("params") or {},
            "body": payload.get("body", api.request_body_example or None),
            "timeout": payload.get("timeout") or environment.get("timeout") or 30,
            "assertions": payload.get("assertions") or [{"type": "status_code", "expected": api.success_status}],
            "extract": payload.get("extract") or [],
            "variables": variables,
            "auth": auth_profile,
        }
        return request_payload

    def build_raw_debug_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """为未入库调试请求合并环境、变量和鉴权配置"""
        context = self._load_debug_context(payload)
        environment = context["environment"]
        variables = context["variables"]
        auth_profile = context["auth_profile"]
        return {
            **payload,
            "base_url": payload.get("base_url") or environment.get("base_url", ""),
            "headers": {**(environment.get("headers") or {}), **(payload.get("headers") or {})},
            "timeout": payload.get("timeout") or environment.get("timeout") or 30,
            "variables": {**variables, **(payload.get("variables") or {})},
            "auth": payload.get("auth") or auth_profile,
        }

    def _load_debug_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """加载调试上下文配置"""
        settings_service = AppSettingsService()
        api_settings = settings_service.get_api_module_settings(masked=False)
        environment = self._find_by_id(api_settings.get("environments", []), payload.get("environment_id", "default"))
        variable_set = self._find_by_id(api_settings.get("variable_sets", []), payload.get("variable_set_id", "default"))
        auth_profile = self._find_by_id(api_settings.get("auth_profiles", []), payload.get("auth_profile_id", "none"))

        variables = {
            **(environment.get("variables") or {}),
            **(variable_set.get("variables") or {}),
            **(payload.get("variables") or {}),
        }
        return {
            "environment": environment,
            "variable_set": variable_set,
            "auth_profile": auth_profile,
            "variables": variables,
        }

    def list_modules(self, project_id: Optional[int] = None) -> List[str]:
        """获取所有模块名"""
        query = self.db.query(APIInfo.module).distinct()
        if project_id:
            query = query.filter(APIInfo.project_id == project_id)

        modules = [row[0] for row in query.all() if row[0]]
        return modules

    def mark_cases_need_review(self, api_id: int):
        """标记接口关联的用例需要重新验证"""
        cases = self.db.query(TestCase).filter(TestCase.api_id == api_id, TestCase.is_active == 1).all()
        for case in cases:
            case.last_result = "need_review"
        self.db.commit()
        return {"api_id": api_id, "affected_cases": len(cases)}

    def _find_by_id(self, items: List[Dict[str, Any]], item_id: str) -> Dict[str, Any]:
        for item in items:
            if item.get("id") == item_id:
                return item
        return items[0] if items else {}

    def _parse_structured_api_docs(self, content: str, source_type: str) -> List[Dict[str, Any]]:
        try:
            doc = json.loads(content)
        except Exception:
            return []

        if source_type in ("auto", "openapi") and isinstance(doc, dict) and doc.get("paths"):
            items = []
            for path, methods in doc.get("paths", {}).items():
                for method, spec in (methods or {}).items():
                    if method.upper() not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                        continue
                    items.append({
                        "name": spec.get("summary") or spec.get("operationId") or f"{method.upper()} {path}",
                        "method": method.upper(),
                        "path": path,
                        "description": spec.get("description", ""),
                        "headers": {},
                        "params_schema": {"parameters": spec.get("parameters", [])},
                        "request_body_example": self._extract_openapi_example(spec.get("requestBody", {})),
                        "response_schema": spec.get("responses", {}),
                        "response_example": {},
                        "success_status": self._guess_success_status(spec.get("responses", {})),
                        "tags": spec.get("tags", []),
                    })
            return items

        if source_type in ("auto", "postman") and isinstance(doc, dict) and doc.get("item"):
            return self._parse_postman_items(doc.get("item", []))

        return []

    def _normalize_import_item(
        self,
        item: Dict[str, Any],
        project_id: int,
        module: str,
        created_by: str,
    ) -> Dict[str, Any]:
        return {
            "project_id": project_id,
            "module": module or item.get("module", ""),
            "name": item.get("name") or f"{item.get('method', 'GET')} {item.get('path', '')}",
            "method": (item.get("method") or "GET").upper(),
            "path": item.get("path") or "/",
            "description": item.get("description", ""),
            "headers": item.get("headers", {}),
            "params_schema": item.get("params_schema") or item.get("request_schema", {}),
            "request_body_example": item.get("request_body_example") or {},
            "response_schema": item.get("response_schema") or {},
            "response_example": item.get("response_example") or {},
            "success_status": item.get("success_status") or 200,
            "tags": item.get("tags", []),
            "created_by": created_by,
            "auto_generate_cases": False,
        }

    def _extract_openapi_example(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        content = (request_body or {}).get("content", {})
        for media in content.values():
            if isinstance(media, dict):
                if "example" in media:
                    return media["example"]
                examples = media.get("examples", {})
                if examples:
                    first = next(iter(examples.values()))
                    return first.get("value", {}) if isinstance(first, dict) else {}
        return {}

    def _guess_success_status(self, responses: Dict[str, Any]) -> int:
        for code in ("200", "201", "204"):
            if code in (responses or {}):
                return int(code)
        return 200

    def _parse_postman_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parsed = []
        for item in items:
            if item.get("item"):
                parsed.extend(self._parse_postman_items(item["item"]))
                continue
            request = item.get("request", {})
            url = request.get("url", {})
            path = "/" + "/".join(url.get("path", [])) if isinstance(url, dict) else str(url)
            headers = {
                header.get("key"): header.get("value", "")
                for header in request.get("header", [])
                if header.get("key")
            }
            body = request.get("body", {}).get("raw")
            try:
                body_example = json.loads(body) if body else {}
            except Exception:
                body_example = {"raw": body}
            parsed.append({
                "name": item.get("name") or f"{request.get('method', 'GET')} {path}",
                "method": request.get("method", "GET"),
                "path": path,
                "description": request.get("description", ""),
                "headers": headers,
                "request_body_example": body_example,
                "success_status": 200,
            })
        return parsed


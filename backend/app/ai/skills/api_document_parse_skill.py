"""
接口文档解析 Skill
==================

将 Markdown / OpenAPI 接口文档解析为需求中心统一的结构化需求点。
"""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any, Dict, List, Optional

from app.ai.skills.base_skill import BaseSkill, SkillResult, normalize_text


class ApiDocumentParseSkill(BaseSkill):
    name = "ApiDocumentParseSkill"
    description = "接口文档结构化解析，输出需求中心接口契约需求点"
    required_fields = ["content"]

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        content = normalize_text(input_data.get("content"))
        title = normalize_text(input_data.get("title"))
        analysis = self.parse_document(content, title)
        points = self.build_requirement_points(analysis)
        issues = [
            {"type": "optimization", "severity": "medium", "message": warning}
            for warning in analysis.get("warnings", [])
        ]
        return SkillResult(
            success=True,
            data={
                "requirement_points": points,
                "issues": issues,
                "skill_output": analysis,
                "total": len(points),
            },
            message="接口文档 Skill 解析完成",
            metadata={"skill": self.name, "parser": "api_document_skill"},
        )

    def parse_document(self, content: str, title: str = "") -> Dict[str, Any]:
        base_url = self._extract_base_url(content)
        overview_endpoints = self._parse_overview_table(content)
        detail_endpoints = self._parse_detail_sections(content, overview_endpoints)
        openapi_endpoints = self._parse_openapi_paths(content)
        endpoints = self._merge_endpoints(overview_endpoints, detail_endpoints + openapi_endpoints)
        status_scenarios = self._extract_status_scenarios(content, base_url)
        expects_status_endpoint = self._expects_status_endpoint(content, title, base_url)
        if status_scenarios and "/status/{codes}" not in {endpoint.get("path") for endpoint in endpoints}:
            endpoints.append({
                "category": "Status codes",
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "TRACE"],
                "path": "/status/{codes}",
                "description": "返回指定状态码；多个状态码时随机返回一个",
                "examples": [],
                "assertions": [],
            })

        category_counts = Counter(endpoint.get("category") or "未分类" for endpoint in endpoints)
        warnings = []
        if not base_url:
            warnings.append("未识别到基础地址，生成 case 时将使用相对 path。")
        if not endpoints:
            warnings.append("未识别到接口清单，请检查文档是否包含接口总览表或接口标题。")
        if expects_status_endpoint and "/status/{codes}" not in {endpoint.get("path") for endpoint in endpoints} and not status_scenarios:
            warnings.append("未识别到状态码专项接口。")

        return {
            "doc_type": "api_markdown" if endpoints else "text",
            "title": title,
            "base_url": base_url,
            "stats": {
                "endpoint_count": len(endpoints),
                "category_count": len(category_counts),
                "status_scenario_count": len(status_scenarios),
                "assertion_endpoint_count": sum(1 for endpoint in endpoints if endpoint.get("assertions")),
            },
            "categories": [{"name": name, "count": count} for name, count in category_counts.items()],
            "endpoints": endpoints,
            "status_scenarios": status_scenarios,
            "warnings": warnings,
            "test_focus": [
                "接口定义结构化解析",
                "状态码成功、客户端错误和服务端错误覆盖",
                "请求示例、响应状态和断言一致性",
            ],
            "suggested_generation_modes": [
                {"id": "status_codes", "label": "状态码专项"},
                {"id": "smoke", "label": "接口主流程"},
                {"id": "full", "label": "全量接口冒烟"},
            ],
            "completeness": {
                "has_base_url": bool(base_url),
                "has_endpoint_overview": bool(overview_endpoints),
                "has_status_codes": bool(status_scenarios),
                "ready_for_api_case": bool(endpoints or status_scenarios),
            },
        }

    def build_requirement_points(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        points = []
        for index, endpoint in enumerate(analysis.get("endpoints", []), start=1):
            methods = endpoint.get("methods") or []
            method_text = "/".join(methods) if methods else "METHOD"
            path = endpoint.get("path", "")
            description = endpoint.get("description") or "接口定义"
            source_text = f"{method_text} {path} {description}".strip()
            points.append(
                {
                    "requirement_no": f"API-{index:03d}",
                    "module": endpoint.get("category") or "接口文档",
                    "title": f"{method_text} {path} - {description}"[:120],
                    "content": f"接口 {method_text} {path} 应符合文档定义：{description}",
                    "type": "api_contract",
                    "priority": "P1",
                    "risk_level": "medium",
                    "dependency_scope": ["api"],
                    "version": "",
                    "source_text": source_text,
                    "need_review": not endpoint.get("assertions"),
                }
            )
        return points

    def _extract_base_url(self, content: str) -> str:
        patterns = [
            r"基础地址\s*\|\s*`?(https?://[^`\s|]+)`?",
            r"Base URL\s*[:：]\s*`?(https?://[^`\s]+)`?",
            r"-\s*url:\s*(https?://[^\s]+)",
            r"GET\s+(https?://[^\s/]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, content, flags=re.IGNORECASE)
            if match:
                return match.group(1).rstrip("/")
        return ""

    def _parse_overview_table(self, content: str) -> List[Dict[str, Any]]:
        endpoints = []
        for line in content.splitlines():
            if not line.startswith("|") or "`/" not in line:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 3 or set(cells) == {"---"}:
                continue
            path_idx = next((idx for idx, cell in enumerate(cells) if self._strip_code(cell).startswith("/")), -1)
            if path_idx < 0:
                continue
            path = self._strip_code(cells[path_idx])
            method_idx = next((idx for idx, cell in enumerate(cells) if idx != path_idx and self._split_methods(self._strip_code(cell))), -1)
            if path_idx + 1 < len(cells):
                description_idx = path_idx + 1
            else:
                description_idx = next((idx for idx in range(len(cells)) if idx not in {path_idx, method_idx}), -1)
            endpoints.append({
                "category": cells[0] if method_idx not in {0, -1} and path_idx != 0 else "接口文档",
                "methods": self._split_methods(self._strip_code(cells[method_idx])) if method_idx >= 0 else [],
                "path": path,
                "description": cells[description_idx] if description_idx >= 0 else "",
                "examples": [],
                "assertions": [],
            })
        return endpoints

    def _parse_openapi_paths(self, content: str) -> List[Dict[str, Any]]:
        endpoints: List[Dict[str, Any]] = []
        in_paths = False
        current_path = ""
        current_endpoint: Optional[Dict[str, Any]] = None
        current_responses = False

        def flush_endpoint() -> None:
            nonlocal current_endpoint
            if current_endpoint:
                current_endpoint["assertions"] = self._assertions_from_status_codes(current_endpoint.pop("_status_codes", []))
                endpoints.append(current_endpoint)
                current_endpoint = None

        for line in content.splitlines():
            if re.match(r"^paths:\s*$", line):
                in_paths = True
                continue
            if not in_paths:
                continue
            if re.match(r"^[A-Za-z_][\w-]*:\s*$", line):
                flush_endpoint()
                break

            path_match = re.match(r"^\s{2}(/[^:]+):\s*$", line)
            if path_match:
                flush_endpoint()
                current_path = path_match.group(1)
                current_responses = False
                continue

            method_match = re.match(r"^\s{4}(get|post|put|patch|delete|trace|head|options):\s*$", line, flags=re.IGNORECASE)
            if method_match and current_path:
                flush_endpoint()
                current_endpoint = {
                    "category": "接口文档",
                    "methods": [method_match.group(1).upper()],
                    "path": current_path,
                    "description": "",
                    "examples": [],
                    "_status_codes": [],
                }
                current_responses = False
                continue

            if not current_endpoint:
                continue

            tag_match = re.match(r"^\s{6}tags:\s*\[([^\]]+)\]", line)
            if tag_match:
                current_endpoint["category"] = tag_match.group(1).split(",")[0].strip().strip("\"'")
                continue
            summary_match = re.match(r"^\s{6}summary:\s*(.+)$", line)
            if summary_match:
                current_endpoint["description"] = summary_match.group(1).strip()
                continue
            if re.match(r"^\s{6}responses:\s*$", line):
                current_responses = True
                continue
            if current_responses:
                code_match = re.match(r"^\s{8}\"?([1-5]\d\d)\"?:\s*$", line)
                if code_match:
                    current_endpoint.setdefault("_status_codes", []).append(int(code_match.group(1)))

        flush_endpoint()
        return endpoints

    def _parse_detail_sections(self, content: str, overview: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        overview_by_path = {item["path"]: item for item in overview}
        headings = list(re.finditer(r"^####\s+(?:(?P<methods>[A-Z/]+)\s+)?`(?P<path>/[^`]+)`", content, flags=re.MULTILINE))
        endpoints = []
        for index, heading in enumerate(headings):
            start = heading.end()
            end = headings[index + 1].start() if index + 1 < len(headings) else len(content)
            section = content[start:end]
            path = heading.group("path")
            methods = self._split_methods(heading.group("methods") or "")
            overview_item = overview_by_path.get(path, {})
            if not methods:
                methods = overview_item.get("methods") or self._infer_methods_from_examples(section) or ["GET"]
            assertions = self._parse_recommended_assertions(section) or self._infer_assertions_from_section(section)
            endpoints.append({
                "category": overview_item.get("category") or self._nearest_category(content, heading.start()),
                "methods": methods,
                "path": path,
                "description": self._first_text_line(section) or overview_item.get("description", ""),
                "examples": self._parse_http_examples(section),
                "assertions": assertions,
            })
        return endpoints

    def _extract_status_scenarios(self, content: str, base_url: str) -> List[Dict[str, Any]]:
        scenarios_by_key: Dict[str, Dict[str, Any]] = {}
        for match in re.finditer(r"/status/([0-9]{3}(?:,[0-9]{3})*)", content):
            codes = [int(code) for code in match.group(1).split(",")]
            key = ",".join(str(code) for code in codes)
            scenarios_by_key[key] = {
                "path": f"/status/{key}",
                "method": "GET",
                "expected_status": codes[0] if len(codes) == 1 else None,
                "expected_statuses": codes,
                "description": self._status_description(codes),
                "base_url": base_url,
            }

        preferred = ["200", "404", "500", "200,400,500"]
        ordered = [scenarios_by_key.pop(key) for key in preferred if key in scenarios_by_key]
        ordered.extend(scenarios_by_key.values())
        return ordered

    def _expects_status_endpoint(self, content: str, title: str, base_url: str) -> bool:
        del title
        source = f"{base_url}\n{content}".lower()
        if "/status/{codes}" in source or re.search(r"/status/[1-5]\d\d", source):
            return True
        return "httpbin" in base_url.lower() and "状态码" in content

    def _merge_endpoints(self, overview: List[Dict[str, Any]], details: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        merged = {item["path"]: {**item} for item in overview}
        for item in details:
            current = merged.get(item["path"], {})
            merged[item["path"]] = {**current, **item}
            if not merged[item["path"]].get("methods"):
                merged[item["path"]]["methods"] = current.get("methods", ["GET"])
        return list(merged.values())

    def _parse_recommended_assertions(self, section: str) -> List[Dict[str, Any]]:
        if "推荐断言" not in section:
            return []
        match = re.search(r"推荐断言：?\s*```json\s*([\s\S]*?)```", section)
        if not match:
            return []
        try:
            parsed = json.loads(match.group(1).strip())
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []

    def _infer_assertions_from_section(self, section: str) -> List[Dict[str, Any]]:
        status_codes: List[int] = []
        patterns = (
            r"(?:响应状态码|状态码|Status\s*Code|status_code)\s*[:：=]?\s*([1-5]\d\d(?:\s*[,/]\s*[1-5]\d\d)*)",
            r"HTTP/\d(?:\.\d)?\s+([1-5]\d\d)",
        )
        for pattern in patterns:
            for match in re.finditer(pattern, section, flags=re.IGNORECASE):
                codes = [int(code) for code in re.findall(r"[1-5]\d\d", match.group(1))]
                status_codes.extend(codes)
        return self._assertions_from_status_codes(sorted(set(status_codes)))

    def _assertions_from_status_codes(self, status_codes: List[int]) -> List[Dict[str, Any]]:
        if len(status_codes) == 1:
            return [{"type": "status_code", "expected": status_codes[0]}]
        if len(status_codes) > 1:
            return [{"type": "status_in", "expected": status_codes}]
        return []

    def _parse_http_examples(self, section: str) -> List[Dict[str, str]]:
        examples = []
        for block in re.findall(r"```http\s*([\s\S]*?)```", section):
            first_line = next((line.strip() for line in block.splitlines() if line.strip()), "")
            match = re.match(r"(?P<method>[A-Z]+)\s+(?P<url>\S+)", first_line)
            if match:
                examples.append(match.groupdict())
        return examples

    def _infer_methods_from_examples(self, section: str) -> List[str]:
        methods = [example["method"] for example in self._parse_http_examples(section)]
        return sorted(set(methods), key=methods.index)

    def _first_text_line(self, section: str) -> str:
        for line in section.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith(("```", "示例", "请求示例", "推荐断言")):
                return stripped
        return ""

    def _nearest_category(self, content: str, position: int) -> str:
        prefix = content[:position]
        matches = list(re.finditer(r"^###\s+(.+)$", prefix, flags=re.MULTILINE))
        return matches[-1].group(1).strip() if matches else "未分类"

    def _status_description(self, codes: List[int]) -> str:
        if len(codes) > 1:
            return f"随机返回 {'/'.join(str(code) for code in codes)} 之一"
        labels = {200: "成功状态", 401: "未授权", 403: "禁止访问", 404: "资源不存在", 500: "服务端错误"}
        return labels.get(codes[0], f"返回状态码 {codes[0]}")

    def _strip_code(self, value: str) -> str:
        return value.replace("`", "").strip()

    def _split_methods(self, value: str) -> List[str]:
        methods = [item.strip().upper() for item in str(value or "").split("/") if item.strip()]
        return [method for method in methods if re.fullmatch(r"[A-Z]+", method)]

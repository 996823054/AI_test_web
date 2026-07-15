"""
用例管理服务
============
用例的 CRUD + AI 生成
"""

from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.test_case import TestCase
from app.models.case_version import CaseVersion
from app.models.case_step import CaseStep
from app.models.execution import Execution
from app.models.api_info import APIInfo
from app.models.project import Project
from app.models.ai_case_draft import AICaseDraft
from app.models.requirement_document import RequirementDocument
from app.models.requirement_item import RequirementItem
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate, AIGenerateRequest, SyncAICasesRequest
from app.services.case_generator import CaseGeneratorService
from app.services.ai_client import AIClient
from app.services.negative_case_sample_service import NegativeCaseSampleService
from app.services.requirement_doc_service import RequirementDocService


class CaseService:
    """用例管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_cases(
        self,
        api_id: Optional[int] = None,
        case_kind: Optional[str] = None,
        category: Optional[str] = None,
        source: Optional[str] = None,
        priority: Optional[str] = None,
        version_group: Optional[str] = None,
        keyword: Optional[str] = None,
        include_deprecated: bool = False,
        lifecycle_status: Optional[str] = None,
        trust_status: Optional[str] = None,
        module_delivery: Optional[int] = None,
        importance: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        """获取用例列表"""
        if include_deprecated:
            query = self.db.query(TestCase).filter(
                or_(TestCase.is_active == 1, TestCase.lifecycle_status == "deprecated")
            )
        else:
            query = self.db.query(TestCase).filter(TestCase.is_active == 1)
            query = query.filter(TestCase.lifecycle_status == "active")

        if api_id:
            query = query.filter(TestCase.api_id == api_id)
        if case_kind:
            query = query.filter(TestCase.case_kind == case_kind)
        if category:
            query = query.filter(TestCase.category == category)
        if source:
            query = query.filter(TestCase.source == source)
        if priority:
            query = query.filter(TestCase.priority == priority)
        if version_group:
            query = query.filter(TestCase.version_group == version_group)
        if keyword:
            query = query.filter(
                or_(
                    TestCase.name.contains(keyword),
                    TestCase.description.contains(keyword),
                )
            )
        if trust_status:
            query = query.filter(TestCase.trust_status == trust_status)
        if module_delivery is not None:
            query = query.filter(TestCase.module_delivery == module_delivery)
        if importance:
            query = query.filter(TestCase.importance == importance)
        if lifecycle_status:
            query = query.filter(TestCase.lifecycle_status == lifecycle_status)

        total = query.count()
        items = query.order_by(TestCase.created_at.desc()) \
                     .offset((page - 1) * page_size) \
                     .limit(page_size) \
                     .all()

        # 附加接口名称
        result_items = []
        for case in items:
            result_items.append(self.serialize_case(case))

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": result_items,
        }

    def get_case(self, case_id: int) -> Optional[TestCase]:
        """获取用例详情"""
        return self.db.query(TestCase).filter(TestCase.id == case_id).first()

    def serialize_case(self, case: TestCase) -> Dict:
        """序列化用例，归一化空 JSON 字段并附加接口名称"""
        case_dict = case.to_dict()
        api = self.db.query(APIInfo).filter(APIInfo.id == case.api_id).first()
        case_dict["api_name"] = api.name if api else ""
        case_dict["api"] = api.to_dict() if api else None
        case_dict["project_id"] = api.project_id if api else None
        case_dict["module"] = api.module if api else ""
        source_document = (
            self.db.query(RequirementDocument)
            .filter(RequirementDocument.id == case.source_document_id)
            .first()
            if case.source_document_id
            else None
        )
        requirement_item = (
            self.db.query(RequirementItem)
            .filter(RequirementItem.id == case.requirement_item_id)
            .first()
            if case.requirement_item_id
            else None
        )
        ai_draft = (
            self.db.query(AICaseDraft)
            .filter(AICaseDraft.confirmed_case_id == case.id)
            .first()
        )
        case_dict["source_document"] = source_document.to_dict() if source_document else None
        case_dict["requirement_item"] = requirement_item.to_dict() if requirement_item else None
        case_dict["source_excerpt"] = (
            ai_draft.source_excerpt
            if ai_draft and ai_draft.source_excerpt
            else (requirement_item.source_text if requirement_item else "")
        )
        case_dict["ai_draft"] = ai_draft.to_dict() if ai_draft else None
        case_dict["version_history_count"] = (
            self.db.query(CaseVersion).filter(CaseVersion.case_id == case.id).count()
        )
        case_dict["health_info"] = self.build_case_health(case)
        case_dict["case_steps"] = [
            step.to_dict()
            for step in self.db.query(CaseStep)
            .filter(CaseStep.case_id == case.id)
            .order_by(CaseStep.step_no.asc())
            .all()
        ]
        return case_dict

    def build_case_health(self, case: TestCase) -> Dict:
        signals = []
        if case.case_kind == "api" and not (case.expected_status is not None or case.expected_body or case.expected_contains):
            signals.append("缺少明确断言")
        if case.case_kind in {"functional", "automation", "mobile"} and not case.steps:
            signals.append("缺少可执行步骤")
        latest_executions = (
            self.db.query(Execution)
            .filter(Execution.case_id == case.id)
            .order_by(Execution.executed_at.desc())
            .limit(5)
            .all()
        )
        if not latest_executions:
            signals.append("长期未执行")
        else:
            latest = latest_executions[0]
            if latest.status in {"failed", "error"}:
                signals.append(f"最近失败：{latest.error_message or latest.status}")
            statuses = {item.status for item in latest_executions}
            if "passed" in statuses and ({"failed", "error"} & statuses):
                signals.append("疑似 flaky")
        if case.deprecation_category == "STALE_LOCATOR":
            signals.append("元素失效")
        return {
            "score": max(0, 100 - len(signals) * 20),
            "signals": signals,
            "level": "good" if not signals else ("warning" if len(signals) <= 2 else "risk"),
        }

    def create_case(self, data: TestCaseCreate) -> TestCase:
        """创建用例"""
        if data.source_document_id:
            RequirementDocService(self.db).assert_can_generate_cases(data.source_document_id)
        self._validate_case_contract(data)
        if not data.api_id:
            raise ValueError("手动创建 case 必须选择项目和模块对应的接口归属(api_id)，不能落入占位池")

        case = TestCase(
            api_id=data.api_id,
            name=data.name,
            description=data.description,
            case_kind=data.case_kind,
            category=data.category,
            priority=data.priority,
            platform=data.platform,
            version_group=data.version_group,
            source_document_id=data.source_document_id,
            requirement_item_id=data.requirement_item_id,
            trust_status=data.trust_status,
            module_delivery=data.module_delivery,
            importance=data.importance,
            request_data=data.request_data,
            request_headers=data.request_headers,
            steps=data.steps,
            precondition=data.precondition,
            expected_status=data.expected_status,
            expected_body=data.expected_body,
            expected_contains=data.expected_contains,
            expected_result=data.expected_result,
            dependency_consideration=data.dependency_consideration,
            source="manual",
        )
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        self._sync_case_steps(case.id, data.steps, data.expected_result)
        self.create_version_snapshot(case.id, change_reason="create", created_by="system")
        return case

    def update_case(self, case_id: int, data: TestCaseUpdate) -> Optional[TestCase]:
        """更新用例"""
        case = self.get_case(case_id)
        if not case:
            return None
        if case.lifecycle_status == "deprecated":
            raise ValueError("已废弃 case 不可直接编辑，请先恢复或复制")

        update_data = data.model_dump(exclude_unset=True)
        if "trust_status" in update_data and update_data["trust_status"] not in {"draft", "formal"}:
            raise ValueError("禁止通过 API 直接将用例可信度篡改为 verified 或 high_value")
        if "source_document_id" in update_data and update_data["source_document_id"]:
            RequirementDocService(self.db).assert_can_generate_cases(update_data["source_document_id"])

        self.create_version_snapshot(case.id, change_reason="update", created_by="system")

        critical_fields = {
            "steps",
            "request_data",
            "expected_status",
            "expected_body",
            "expected_contains",
            "source_document_id",
            "api_id",
            "precondition",
            "expected_result",
        }
        touched_critical = any(field in update_data for field in critical_fields)
        for field, value in update_data.items():
            if hasattr(case, field):
                setattr(case, field, value)

        if touched_critical:
            case.pending_reconfirm = 1
            case.trust_status = "formal"

        case.current_version_no = (case.current_version_no or 1) + 1
        self.db.commit()
        self.db.refresh(case)
        if "steps" in update_data or "expected_result" in update_data:
            self._sync_case_steps(case.id, case.steps or [], case.expected_result or "")
        return case

    def create_version_snapshot(
        self,
        case_id: int,
        change_reason: str = "manual",
        created_by: str = "system",
    ) -> CaseVersion:
        case = self.get_case(case_id)
        if not case:
            raise ValueError("用例不存在")
        latest = (
            self.db.query(CaseVersion)
            .filter(CaseVersion.case_id == case_id)
            .order_by(CaseVersion.version_no.desc())
            .first()
        )
        version_no = (latest.version_no + 1) if latest else 1
        version = CaseVersion(
            case_id=case_id,
            version_no=version_no,
            snapshot=self.serialize_case(case),
            change_reason=change_reason,
            created_by=created_by,
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def list_case_versions(self, case_id: int) -> List[Dict]:
        rows = (
            self.db.query(CaseVersion)
            .filter(CaseVersion.case_id == case_id)
            .order_by(CaseVersion.version_no.desc())
            .all()
        )
        return [row.to_dict() for row in rows]

    def copy_case(self, case_id: int, *, copied_by: str = "frontend") -> TestCase:
        source = self.get_case(case_id)
        if not source:
            raise ValueError("用例不存在")
        copied = TestCase(
            api_id=source.api_id,
            name=f"{source.name}（副本）",
            description=f"复制自 case #{source.id}：{source.description or source.name}",
            case_kind=source.case_kind,
            category=source.category,
            priority=source.priority,
            platform=source.platform,
            version_group=source.version_group,
            source_document_id=source.source_document_id,
            requirement_item_id=source.requirement_item_id,
            request_data=source.request_data or {},
            request_headers=source.request_headers or {},
            steps=source.steps or [],
            precondition=source.precondition or "",
            expected_status=source.expected_status,
            expected_body=source.expected_body or {},
            expected_contains=source.expected_contains or [],
            expected_result=source.expected_result or "",
            dependency_consideration=source.dependency_consideration or "",
            source=source.source,
            trust_status="draft",
            pending_reconfirm=1,
        )
        self.db.add(copied)
        self.db.commit()
        self.db.refresh(copied)
        self._sync_case_steps(copied.id, copied.steps or [], copied.expected_result or "")
        self.create_version_snapshot(copied.id, change_reason=f"copy from case #{source.id}", created_by=copied_by)
        return copied

    def deprecate_case(
        self,
        case_id: int,
        category: str,
        reason: str,
        replaced_by_case_id: Optional[int] = None,
        change_record_id: Optional[int] = None,
    ) -> TestCase:
        case = self.get_case(case_id)
        if not case:
            raise ValueError("用例不存在")
        if case.lifecycle_status == "deprecated":
            return case

        # 废弃防御性强校验 (FR-CASE-011)
        valid_categories = {"FEATURE_REMOVED", "REDUNDANT", "FLAKY", "STALE_LOCATOR", "OTHER"}
        if not category or category not in valid_categories:
            raise ValueError("废弃用例必须指定合法的废弃大类(deprecation_category)")
        if not reason or len(reason.strip()) < 10:
            raise ValueError("废弃用例必须填写详细原因(reason)，字数必填 >= 10字")
        if category == "REDUNDANT" and not replaced_by_case_id:
            raise ValueError("冗余废弃必须关联替代用例(replaced_by_case_id)，不能断开追溯链路")
        if category in {"FEATURE_REMOVED", "STALE_LOCATOR"} and not change_record_id:
            raise ValueError("功能移除或定位失效废弃必须关联变更记录(change_record_id)")

        self.create_version_snapshot(case_id, change_reason=reason, created_by="system")

        # 写入元数据
        case.deprecation_category = category
        case.deprecation_reason = reason
        case.replaced_by_case_id = replaced_by_case_id
        case.change_record_id = change_record_id
        case.lifecycle_status = "deprecated"
        case.is_active = 0

        # 进入负样本库记录
        NegativeCaseSampleService(self.db).create_from_deprecated_case(
            case,
            reason=f"[{category}] {reason}",
            created_by="system",
        )

        self.db.commit()
        self.db.refresh(case)
        return case

    def delete_case(self, case_id: int) -> bool:
        """禁止裸删除，避免绕过废弃元数据与审计链路。"""
        case = self.get_case(case_id)
        if not case:
            return False
        raise ValueError("删除 case 必须走废弃治理流程，请调用 deprecate 并填写废弃分类、原因和必要关联")

    def ai_generate(self, request: AIGenerateRequest) -> Dict:
        """AI 生成测试用例，只进入草稿队列，人工确认后才能成为正式 case。"""
        if request.source_document_id:
            RequirementDocService(self.db).assert_can_generate_cases(request.source_document_id)

        ai_client = AIClient()
        generator = CaseGeneratorService(self.db, ai_client)
        cases = generator.generate_for_api(
            api_id=request.api_id,
            categories=request.categories,
        )
        if not cases:
            raise ValueError("AI 未生成任何 case 草稿")

        from app.services.ai_case_draft_service import AICaseDraftService

        enriched_cases = []
        for item in cases:
            enriched = dict(item)
            enriched["api_id"] = request.api_id
            enriched["case_kind"] = "api"
            enriched_cases.append(enriched)
        drafts = AICaseDraftService(self.db).create_drafts_from_cases(
            document_id=request.source_document_id,
            cases=enriched_cases,
            case_kind="api",
            platform="api",
            version_group="",
            created_by="ai_generate",
            raw_payload={"api_id": request.api_id, "categories": request.categories},
        )
        return {
            "success": True,
            "message": "AI 生成结果已进入待确认草稿队列，人工确认后才能入正式库",
            "generated_count": len(drafts),
            "draft_ids": [draft.id for draft in drafts],
        }

    def list_version_groups(self, case_kind: str = "functional") -> List[str]:
        rows = (
            self.db.query(TestCase.version_group)
            .filter(
                TestCase.is_active == 1,
                TestCase.case_kind == case_kind,
                TestCase.version_group != "",
            )
            .distinct()
            .all()
        )
        return [row[0] for row in rows if row[0]]

    def sync_ai_cases(self, request: SyncAICasesRequest) -> Dict:
        """把 AI 生成的 case 写入草稿队列，需人工确认后进入正式库"""
        if not request.cases:
            return {"success": False, "message": "没有可同步的 case", "count": 0}

        from app.services.ai_case_draft_service import AICaseDraftService

        draft_service = AICaseDraftService(self.db)
        drafts = draft_service.create_drafts_from_cases(
            document_id=request.document_id,
            cases=request.cases,
            case_kind=request.case_kind,
            platform=request.platform,
            version_group=request.version_group,
            created_by=request.created_by,
        )
        return {
            "success": True,
            "message": "AI 生成用例已写入待确认草稿",
            "count": len(drafts),
            "draft_ids": [draft.id for draft in drafts],
        }

    def _get_default_api_id(self) -> int:
        """为功能/自动化 case 找一个默认归属接口"""
        api = self.db.query(APIInfo).first()
        if api:
            return api.id

        project = self.db.query(Project).first()
        if not project:
            project = Project(
                name="默认项目",
                description="系统自动创建的默认项目",
                base_url="",
                created_by="system",
            )
            self.db.add(project)
            self.db.flush()

        placeholder_api = APIInfo(
            project_id=project.id,
            module="通用",
            name="功能用例池",
            method="POST",
            path="/placeholder/functional-case-pool",
            description="系统自动创建，用于归档功能/自动化 case",
            created_by="system",
            updated_by="system",
        )
        self.db.add(placeholder_api)
        self.db.commit()
        self.db.refresh(placeholder_api)
        return placeholder_api.id

    def _validate_case_contract(self, data: TestCaseCreate) -> None:
        if data.trust_status not in {"draft", "formal"}:
            raise ValueError("新建 case 的可信状态只能是 draft 或 formal，verified/high_value 必须由执行或回归治理产生")
        if not data.name.strip():
            raise ValueError("创建测试用例失败：用例名称不能为空")
        has_executable_content = bool(
            data.steps
            or data.expected_result.strip()
            or data.expected_body
            or data.expected_contains
            or data.request_data
            or data.expected_status is not None
        )
        if not has_executable_content:
            raise ValueError("创建测试用例失败：用例必须包含有效的步骤、预期结果或接口数据，不可为空白幽灵数据")
        if data.case_kind in {"functional", "automation", "mobile"} and not data.steps:
            raise ValueError("功能、自动化、移动端 case 必须包含可执行步骤")
        if data.case_kind == "api" and not (data.request_data or data.expected_status is not None or data.expected_body):
            raise ValueError("接口 case 必须包含请求数据或接口断言")

    def _sync_case_steps(self, case_id: int, steps: List[str], expected_result: str = "") -> None:
        self.db.query(CaseStep).filter(CaseStep.case_id == case_id).delete(synchronize_session=False)
        for index, step in enumerate(steps or [], start=1):
            self.db.add(
                CaseStep(
                    case_id=case_id,
                    step_no=index,
                    action=str(step),
                    expected_result=expected_result or "",
                )
            )
        self.db.commit()


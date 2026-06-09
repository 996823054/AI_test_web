"""
变更检测服务
============
核心能力：
1. 记录每次接口修改
2. 生成变更摘要
3. 触发用例同步更新

这个 service 是“变更中心”的核心实现文件。

你后续应该把能力继续集中到这里，而不是散落到 router：
    - 变更影响分析
    - before / after diff 生成
    - 受影响 case 聚合
    - AI 建议补充或修改 case

建议后续新增的方法：
    1. detect_impact(api_id) -> dict
       返回受影响的 case、最近报告、风险等级
    2. get_diff(changelog_id or api_id + version) -> dict
       返回 before / after / changed_fields
    3. mark_review_status(...)
       记录某条变更是否已处理、由谁处理
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.api_info import APIInfo
from app.models.changelog import Changelog
from app.models.negative_case_sample import NegativeCaseSample
from app.models.test_case import TestCase
from app.services.case_generator import CaseGeneratorService
from app.services.ai_client import AIClient


class ChangeDetectorService:
    """接口变更检测与同步服务"""

    def __init__(self, db: Session):
        self.db = db

    def log_change(
        self,
        api_id: int,
        change_type: str,
        old_value: dict = None,
        new_value: dict = None,
        changed_by: str = "",
    ) -> Changelog:
        """记录一次变更"""
        old_value = old_value or {}
        new_value = new_value or {}

        # 计算变更字段
        changed_fields = []
        if change_type == "updated":
            for key in new_value:
                if key in old_value and old_value[key] != new_value[key]:
                    changed_fields.append(key)

        # 生成变更摘要
        diff_summary = self._generate_diff_summary(
            change_type, old_value, new_value, changed_fields
        )

        changelog = Changelog(
            api_id=api_id,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value,
            diff_summary=diff_summary,
            changed_fields=changed_fields,
            changed_by=changed_by,
            # 新增接口自动标记为已同步（无旧用例需要更新）
            cases_synced=1 if change_type == "created" else 0,
        )

        self.db.add(changelog)
        self.db.commit()
        self.db.refresh(changelog)
        return changelog

    def list_changelogs(
        self,
        api_id: Optional[int] = None,
        change_type: Optional[str] = None,
        synced: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        """获取变更记录列表"""
        query = self.db.query(Changelog)

        if api_id:
            query = query.filter(Changelog.api_id == api_id)
        if change_type:
            query = query.filter(Changelog.change_type == change_type)
        if synced is not None:
            query = query.filter(Changelog.cases_synced == synced)

        total = query.count()
        items = query.order_by(Changelog.changed_at.desc()) \
                     .offset((page - 1) * page_size) \
                     .limit(page_size) \
                     .all()

        # 附加接口名称
        result_items = []
        for log in items:
            log_dict = log.to_dict()
            api = self.db.query(APIInfo).filter(APIInfo.id == log.api_id).first()
            log_dict["api_name"] = api.name if api else "已删除"
            log_dict["api_method"] = api.method if api else ""
            log_dict["api_path"] = api.path if api else ""
            result_items.append(log_dict)

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": result_items,
        }

    def get_unsync_changes(self) -> Dict:
        """获取所有未同步的变更"""
        unsynced = self.db.query(Changelog).filter(
            Changelog.cases_synced == 0,
        ).order_by(Changelog.changed_at.desc()).all()

        items = []
        for log in unsynced:
            api = self.db.query(APIInfo).filter(APIInfo.id == log.api_id).first()
            case_count = self.db.query(TestCase).filter(
                TestCase.api_id == log.api_id,
                TestCase.is_active == 1,
            ).count()

            items.append({
                "changelog_id": log.id,
                "api_id": log.api_id,
                "api_name": api.name if api else "已删除",
                "change_type": log.change_type,
                "diff_summary": log.diff_summary,
                "changed_fields": log.changed_fields,
                "changed_by": log.changed_by,
                "changed_at": str(log.changed_at),
                "affected_cases": case_count,
            })

        return {
            "count": len(items),
            "items": items,
        }

    def sync_cases(self, changelog_id: int) -> Dict:
        """同步变更：重新生成 AI 用例"""
        changelog = self.db.query(Changelog).filter(
            Changelog.id == changelog_id
        ).first()

        if not changelog:
            raise ValueError(f"变更记录不存在: {changelog_id}")

        if changelog.cases_synced == 1:
            return {"message": "该变更已同步", "changelog_id": changelog_id}

        # 调用 AI 重新生成用例
        ai = AIClient()
        generator = CaseGeneratorService(self.db, ai)

        try:
            result = generator.regenerate_for_changed_api(changelog.api_id)

            # 标记已同步
            changelog.cases_synced = 1
            self.db.commit()

            return {
                "message": "同步成功",
                "changelog_id": changelog_id,
                **result,
            }
        except Exception as e:
            return {
                "message": f"同步失败: {str(e)}",
                "changelog_id": changelog_id,
            }

    def get_api_changelog(self, api_id: int) -> List[Dict]:
        """获取指定接口的变更历史"""
        logs = self.db.query(Changelog).filter(
            Changelog.api_id == api_id
        ).order_by(Changelog.changed_at.desc()).all()

        return [log.to_dict() for log in logs]

    def get_change_warnings(self, changelog_id: int) -> Dict:
        """根据历史废弃 case 负样本给出变更反向预警。"""
        changelog = self.db.query(Changelog).filter(Changelog.id == changelog_id).first()
        if not changelog:
            raise ValueError(f"变更记录不存在: {changelog_id}")

        samples = (
            self.db.query(NegativeCaseSample)
            .filter(
                NegativeCaseSample.source_type == "deprecated_case",
                NegativeCaseSample.deprecation_category.in_(["FLAKY", "STALE_LOCATOR"]),
            )
            .all()
        )
        items = []
        for sample in samples:
            case = self.db.query(TestCase).filter(TestCase.id == sample.source_case_id).first()
            if not case or case.api_id != changelog.api_id:
                continue
            items.append(
                {
                    "category": sample.deprecation_category,
                    "source_case_id": sample.source_case_id,
                    "source_case_name": case.name,
                    "reason": sample.reason,
                    "warning": self._warning_text(sample.deprecation_category),
                }
            )
        return {"changelog_id": changelog_id, "count": len(items), "items": items}

    def _warning_text(self, category: str) -> str:
        if category == "FLAKY":
            return "历史上该接口存在不稳定 case，变更后建议优先复核断言、等待策略和环境依赖。"
        if category == "STALE_LOCATOR":
            return "历史上该接口关联用例曾因元素定位失效废弃，变更后建议优先复核选择器和页面结构。"
        return "历史废弃 case 模式命中，建议人工复核。"

    def _generate_diff_summary(
        self,
        change_type: str,
        old_value: dict,
        new_value: dict,
        changed_fields: list,
    ) -> str:
        """生成变更摘要"""
        if change_type == "created":
            return f"新增接口: {new_value.get('name', '未命名')}"

        if change_type == "deprecated":
            return "接口已废弃"

        if change_type == "deleted":
            return "接口已删除"

        if not changed_fields:
            return "未知变更"

        # 构建变更描述
        diffs = []
        for field in changed_fields:
            old_val = old_value.get(field, "无")
            new_val = new_value.get(field, "无")

            # 简化显示
            if isinstance(old_val, (dict, list)):
                old_val = f"[{type(old_val).__name__}]"
            if isinstance(new_val, (dict, list)):
                new_val = f"[{type(new_val).__name__}]"

            diffs.append(f"{field}: {old_val} → {new_val}")

        return "；".join(diffs)


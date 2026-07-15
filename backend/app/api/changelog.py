"""
变更记录路由
============
查看接口变更历史、未同步变更提醒

这个文件建议保持“薄路由”：
    - list / unsync / sync / history 这些接口只做参数接收和 service 转发
    - 真正的变更影响分析、diff 生成、用例同步规则都写在 ChangeDetectorService

你后续优先补的点：
    - impact 分析接口
    - diff 详情接口
    - 与报告中心、case 中心联动需要的聚合字段
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.change_detector import ChangeDetectorService

router = APIRouter()


@router.get("/", summary="获取变更记录列表")
def list_changelogs(
    api_id: Optional[int] = Query(None, description="接口ID"),
    change_type: Optional[str] = Query(None, description="变更类型"),
    synced: Optional[int] = Query(None, description="同步状态: 0=未同步 1=已同步"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取变更记录列表"""
    service = ChangeDetectorService(db)
    return service.list_changelogs(
        api_id=api_id, change_type=change_type,
        synced=synced, page=page, page_size=page_size,
    )


@router.get("/unsync", summary="获取未同步的变更")
def get_unsync_changes(db: Session = Depends(get_db)):
    """
    获取所有未同步的变更

    前端用来显示提醒：「有 N 个接口变更未同步测试用例」
    """
    service = ChangeDetectorService(db)
    return service.get_unsync_changes()


@router.post("/{changelog_id}/sync", summary="同步变更到测试用例")
def sync_change(changelog_id: int, db: Session = Depends(get_db)):
    """
    同步变更：根据接口变更，AI 重新生成/更新测试用例
    """
    service = ChangeDetectorService(db)
    result = service.sync_cases(changelog_id)
    return result


@router.get("/{changelog_id}/warnings", summary="获取变更反向预警")
def get_change_warnings(changelog_id: int, db: Session = Depends(get_db)):
    service = ChangeDetectorService(db)
    try:
        return service.get_change_warnings(changelog_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/{api_id}", summary="获取单个接口的变更历史")
def get_api_changelog(api_id: int, db: Session = Depends(get_db)):
    """获取指定接口的完整变更历史"""
    service = ChangeDetectorService(db)
    return service.get_api_changelog(api_id)


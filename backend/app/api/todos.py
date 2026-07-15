"""待办中心 HTTP 路由"""

import asyncio
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models.todo import TodoItem
from app.services.todo_service import TodoService

router = APIRouter()


class DismissTodoRequest(BaseModel):
    reason: str = Field(..., min_length=10, description="详细忽略原因 (>=10字)")
    operator: str = Field(default="tester", description="操作人")


@router.get("/", summary="获取待办列表")
def list_todos(
    status: Optional[str] = Query(None, description="待办状态: pending/resolved/dismissed 等"),
    source_type: Optional[str] = Query(None, description="事件来源大类"),
    importance: Optional[str] = Query(None, description="紧急度"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = TodoService(db)
    return service.list_todos(
        status=status, source_type=source_type, importance=importance, page=page, page_size=page_size
    )


@router.get("/count", summary="获取待办计数")
def get_todo_count(db: Session = Depends(get_db)):
    service = TodoService(db)
    return {"count": service.get_pending_count()}


@router.post("/{todo_id}/dismiss", summary="手动忽略待办")
def dismiss_todo(todo_id: int, request: DismissTodoRequest, db: Session = Depends(get_db)):
    service = TodoService(db)
    try:
        todo = service.dismiss_todo(todo_id, reason=request.reason, operator=request.operator)
        return todo.to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


async def sse_todo_count_generator():
    """SSE 计数事件流生成器：自动感知并秒级推送计数更新"""
    last_count = -1
    while True:
        db = SessionLocal()
        try:
            count = db.query(TodoItem).filter(TodoItem.status.in_({"pending", "in_progress"})).count()
            if count != last_count:
                yield f"data: {json.dumps({'count': count}, ensure_ascii=False)}\n\n"
                last_count = count
        except Exception:
            pass
        finally:
            db.close()
        await asyncio.sleep(2)


@router.get("/count-stream", summary="SSE 待办计数长连接推送")
async def sse_todo_count_stream():
    """SSE 计数推送接口"""
    return StreamingResponse(sse_todo_count_generator(), media_type="text/event-stream")

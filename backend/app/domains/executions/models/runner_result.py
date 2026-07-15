"""Standardized runner outcome used by ExecutionService / Harness / Reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


NORMALIZED_STATUSES = {
    "pending",
    "running",
    "passed",
    "failed",
    "error",
    "cancelled",
    "need_review",
}


@dataclass
class StepResult:
    step_no: int
    name: str
    status: str
    detail: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArtifactRef:
    kind: str
    uri: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunnerResult:
    """Runner may only return steps/artifacts; never write formal assets."""

    status: str
    steps: List[StepResult] = field(default_factory=list)
    artifacts: List[ArtifactRef] = field(default_factory=list)
    request_snapshot: Dict[str, Any] = field(default_factory=dict)
    response_snapshot: Dict[str, Any] = field(default_factory=dict)
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    response_time: int = 0
    error_message: str = ""
    logs: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.status not in NORMALIZED_STATUSES:
            raise ValueError(f"unsupported runner status: {self.status}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_executor_dict(cls, payload: Dict[str, Any]) -> "RunnerResult":
        status = str(payload.get("status") or "error")
        if status == "completed":
            status = "passed"
        return cls(
            status=status,
            steps=[
                StepResult(
                    step_no=1,
                    name="api_request",
                    status=status,
                    detail={"assertions": payload.get("assertions") or []},
                )
            ],
            artifacts=[
                ArtifactRef(kind="request_snapshot", uri="inline:request", meta=payload.get("request_snapshot") or {}),
                ArtifactRef(kind="response_snapshot", uri="inline:response", meta=payload.get("response_snapshot") or {}),
            ],
            request_snapshot=payload.get("request_snapshot") or {},
            response_snapshot=payload.get("response_snapshot") or {},
            assertions=payload.get("assertions") or [],
            variables=payload.get("variables") or {},
            response_time=int(payload.get("response_time") or 0),
            error_message=payload.get("error_message") or "",
            logs=list(payload.get("logs") or []),
        )

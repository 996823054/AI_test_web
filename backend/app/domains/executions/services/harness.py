"""Execution Harness seam: env/vars/data/cleanup/evidence enrichment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol

from app.domains.executions.models.runner_result import RunnerResult


@dataclass
class HarnessContext:
    case_id: Optional[int] = None
    batch_id: Optional[int] = None
    base_url: str = ""
    environment: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    cleanup_hooks: list = field(default_factory=list)


class ExecutionHarness(Protocol):
    def prepare(self, context: HarnessContext) -> HarnessContext: ...

    def enrich(self, context: HarnessContext, result: RunnerResult) -> RunnerResult: ...

    def cleanup(self, context: HarnessContext) -> None: ...


class DefaultExecutionHarness:
    """Minimal harness used until platform env/data services deepen."""

    def prepare(self, context: HarnessContext) -> HarnessContext:
        context.variables = dict(context.variables or {})
        context.environment = dict(context.environment or {})
        return context

    def enrich(self, context: HarnessContext, result: RunnerResult) -> RunnerResult:
        result.logs = list(result.logs or [])
        result.logs.append(
            f"harness:enriched case_id={context.case_id} batch_id={context.batch_id}"
        )
        if context.variables:
            merged = dict(result.variables or {})
            merged.update(context.variables)
            result.variables = merged
        return result

    def cleanup(self, context: HarnessContext) -> None:
        for hook in list(context.cleanup_hooks):
            hook()

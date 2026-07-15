"""Requirement domain service errors."""

from __future__ import annotations

from typing import Any, Dict, List


class RequirementBlockingIssuesError(ValueError):
    """Raised when unresolved blocking requirement issues prevent an operation."""

    def __init__(self, message: str, issues: List[Dict[str, Any]]):
        super().__init__(message)
        self.issues = issues

    def to_detail(self) -> Dict[str, Any]:
        return {"message": str(self), "blocking_issues": self.issues}

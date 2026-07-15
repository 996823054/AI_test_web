"""
Compatibility shim for router registration.

Prefer: from app.api import register_routers
Remove when all startup entrypoints import app.api.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI


def register_routers(app: "FastAPI") -> None:
    from app.api import register_routers as _register_routers

    return _register_routers(app)


__all__ = ["register_routers"]

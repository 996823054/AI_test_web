"""Compatibility shim. Prefer app.platform.lifecycle."""
from app.platform.lifecycle import on_startup

__all__ = ["on_startup"]

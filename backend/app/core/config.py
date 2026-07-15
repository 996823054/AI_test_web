"""Compatibility shim. Prefer app.platform.config."""
from app.platform.config import settings

__all__ = ["settings"]

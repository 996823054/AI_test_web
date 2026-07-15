"""Compatibility shim. Prefer app.platform.config. Remove when call sites migrated."""
from app.platform.config import *  # noqa: F403
from app.platform.config import settings

__all__ = ["settings"]

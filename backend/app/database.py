"""Compatibility shim. Prefer app.platform.database. Remove when call sites migrated."""
from app.platform.database import *  # noqa: F403

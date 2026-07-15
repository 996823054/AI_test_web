"""Compatibility shim. Prefer app.domains.todos.models.todo. Remove after import migration."""
from app.domains.todos.models.todo import *  # noqa: F403

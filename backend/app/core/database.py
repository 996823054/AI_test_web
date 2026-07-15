"""Compatibility shim. Prefer app.platform.database."""
from app.platform.database import Base, SessionLocal, apply_lightweight_migrations, engine, get_db, init_db, seed_demo_data

__all__ = [
    "Base",
    "SessionLocal",
    "apply_lightweight_migrations",
    "engine",
    "get_db",
    "init_db",
    "seed_demo_data",
]

"""
Platform infrastructure (config, DB, storage helpers, masking, settings).

Migration target: keep new infra code under app.platform.
Delete condition: when no callers import app.config/app.database/app.core/*.
"""

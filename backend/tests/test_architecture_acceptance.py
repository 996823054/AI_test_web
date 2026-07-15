"""Architecture acceptance guards for the platform reorganization."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"


class ArchitectureAcceptanceTests(unittest.TestCase):
    def test_target_packages_exist(self):
        for rel in [
            "api",
            "domains/requirements",
            "domains/cases",
            "domains/apis",
            "domains/executions",
            "domains/reports",
            "domains/mobile",
            "domains/changes",
            "domains/todos",
            "ai/skills",
            "platform",
            "shared",
            "experiments",
        ]:
            self.assertTrue((APP / rel).exists(), rel)

    def test_execution_router_does_not_touch_runner_directly(self):
        source = (APP / "api" / "executions.py").read_text(encoding="utf-8")
        self.assertIn("ExecutionService", source)
        self.assertNotIn("TestExecutorService(", source)
        self.assertNotIn("APIRunner(", source)

    def test_reports_router_uses_report_service(self):
        source = (APP / "api" / "reports.py").read_text(encoding="utf-8")
        self.assertIn("ReportService", source)
        self.assertNotIn("ReportGeneratorService(", source)

    def test_default_register_excludes_midscene(self):
        from fastapi import FastAPI
        import os
        from app.api import register_routers

        os.environ.pop("FEATURE_MIDSCENE_IOS", None)
        app = FastAPI()
        register_routers(app)
        paths = {getattr(route, "path", "") for route in app.routes}
        self.assertFalse(any(path.startswith("/api/midscene-ios") for path in paths))
        self.assertTrue(any(path.startswith("/api/requirements") for path in paths))
        self.assertTrue(any(path.startswith("/api/executions") for path in paths))
        self.assertTrue(any(path.startswith("/api/reports") for path in paths))

    def test_removed_empty_module_packages_stay_gone(self):
        for name in ["cases", "ai", "api_management", "changelog", "reports"]:
            self.assertFalse((APP / "modules" / name).exists(), name)


if __name__ == "__main__":
    unittest.main()

"""Compatibility contracts for the platform architecture shell."""

from __future__ import annotations

import unittest


class PlatformShellCompatibilityTests(unittest.TestCase):
    def test_platform_config_and_database_aliases(self) -> None:
        from app import config as legacy_config
        from app import database as legacy_database
        from app.core import config as core_config
        from app.core import database as core_database
        from app.platform import config as platform_config
        from app.platform import database as platform_database

        self.assertIs(legacy_config.settings, platform_config.settings)
        self.assertIs(core_config.settings, platform_config.settings)
        self.assertIs(legacy_database.Base, platform_database.Base)
        self.assertIs(core_database.engine, platform_database.engine)

    def test_domain_service_and_model_aliases(self) -> None:
        from app.domains.cases.models.test_case import TestCase as DomainTestCase
        from app.domains.cases.services.case_service import CaseService as DomainCaseService
        from app.domains.requirements.services.requirement_doc_service import (
            RequirementDocService as DomainRequirementDocService,
        )
        from app.models.test_case import TestCase as LegacyTestCase
        from app.services.case_service import CaseService as LegacyCaseService
        from app.services.requirement_doc_service import (
            RequirementDocService as LegacyRequirementDocService,
        )

        self.assertIs(LegacyTestCase, DomainTestCase)
        self.assertIs(LegacyCaseService, DomainCaseService)
        self.assertIs(LegacyRequirementDocService, DomainRequirementDocService)

    def test_ai_skill_aliases(self) -> None:
        from app.ai.skills.base_skill import BaseSkill as DomainBaseSkill
        from app.ai.skills.case_generate_skill import CaseGenerateSkill as DomainCaseGenerateSkill
        from app.skills.base_skill import BaseSkill as LegacyBaseSkill
        from app.skills.case_generate_skill import CaseGenerateSkill as LegacyCaseGenerateSkill

        self.assertIs(LegacyBaseSkill, DomainBaseSkill)
        self.assertIs(LegacyCaseGenerateSkill, DomainCaseGenerateSkill)

    def test_router_registration_aliases_expose_same_paths(self) -> None:
        from fastapi import FastAPI

        from app.api import register_routers as register_from_api
        from app.modules import register_routers as register_from_modules

        api_app = FastAPI()
        modules_app = FastAPI()
        register_from_api(api_app)
        register_from_modules(modules_app)

        api_paths = sorted({getattr(route, "path", "") for route in api_app.routes})
        module_paths = sorted({getattr(route, "path", "") for route in modules_app.routes})
        self.assertEqual(api_paths, module_paths)
        self.assertTrue(any(path.startswith("/api/cases") for path in api_paths))
        self.assertTrue(any(path.startswith("/api/requirements") for path in api_paths))
        self.assertTrue(any(path.startswith("/api/executions") for path in api_paths))

    def test_main_app_still_loads(self) -> None:
        from app.main import app

        paths = {getattr(route, "path", "") for route in app.routes}
        self.assertIn("/health", paths)
        self.assertTrue(any(path.startswith("/api/cases") for path in paths))


if __name__ == "__main__":
    unittest.main()

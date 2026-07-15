"""Execution / report platform seams and guardrails."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.domains.executions.models.runner_result import RunnerResult
from app.domains.executions.services.execution_service import ExecutionService, _TaskStore
from app.domains.reports.services.report_service import ReportService
from app.models import (  # noqa: F401
    ai_case_draft,
    api_info,
    case_version,
    changelog,
    execution,
    negative_case_sample,
    project,
    requirement_document,
    requirement_item,
    requirement_tree_node,
    test_case,
    user,
)
from app.models.api_info import APIInfo
from app.models.execution import ExecBatch, Execution
from app.models.project import Project
from app.models.test_case import TestCase


class RunnerResultTests(unittest.TestCase):
    def test_from_executor_dict_normalizes_status(self):
        result = RunnerResult.from_executor_dict(
            {
                "status": "passed",
                "request_snapshot": {"url": "/x"},
                "response_snapshot": {"status_code": 200},
                "assertions": [{"passed": True}],
                "variables": {"a": 1},
                "response_time": 12,
                "error_message": "",
            }
        )
        self.assertEqual(result.status, "passed")
        self.assertEqual(len(result.steps), 1)
        self.assertEqual(len(result.artifacts), 2)


class ExecutionTaskSeamTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.Session()
        self.store = _TaskStore()
        project_row = Project(name="p", description="", base_url="https://example.test", created_by="t")
        self.db.add(project_row)
        self.db.flush()
        api = APIInfo(
            project_id=project_row.id,
            module="m",
            name="ping",
            method="GET",
            path="/ping",
            created_by="t",
            updated_by="t",
        )
        self.db.add(api)
        self.db.flush()
        case = TestCase(
            api_id=api.id,
            name="ping ok",
            category="positive",
            priority="P0",
            request_data={},
            expected_status=200,
            source="manual",
        )
        self.db.add(case)
        self.db.commit()
        self.case_id = case.id

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_create_cancel_and_logs(self):
        service = ExecutionService(self.db, task_store=self.store)
        task = service.create_task(case_ids=[self.case_id], timeout_seconds=30)
        self.assertEqual(task["status"], "pending")
        cancelled = service.cancel_task(task["task_id"])
        self.assertEqual(cancelled["status"], "cancelled")
        logs = service.get_task_logs(task["task_id"])
        self.assertIn("task:created", logs)
        self.assertIn("task:cancelled", logs)

    def test_timeout_before_start(self):
        service = ExecutionService(self.db, task_store=self.store)
        task = service.create_task(case_ids=[self.case_id], timeout_seconds=1)
        stored = self.store.get(task["task_id"])
        stored.created_at -= 10
        self.store.update(stored)
        started = service.start_task(task["task_id"])
        self.assertEqual(started["status"], "error")
        self.assertIn("超时", started["error_message"])


class ReportEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.Session()
        batch = ExecBatch(name="b", status="completed", total=1, passed=1, failed=0, errors=0, triggered_by="t")
        self.db.add(batch)
        self.db.flush()
        self.db.add(
            Execution(
                batch_id=batch.id,
                case_id=1,
                api_id=1,
                status="passed",
                request_snapshot={"url": "/x"},
                response_snapshot={"status_code": 200},
                assertions=[{"passed": True}],
                response_time=10,
            )
        )
        self.db.commit()
        self.batch_id = batch.id

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_collect_evidence_and_export(self):
        service = ReportService(self.db)
        evidence = service.collect_batch_evidence(self.batch_id)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["artifacts"][0]["kind"], "request_snapshot")
        exported = service.export_batch_report(self.batch_id)
        self.assertEqual(exported["format"], "json")
        self.assertIn("payload", exported)
        policy = service.retention_policy()
        self.assertEqual(policy["retention_days"], 90)


class RunnerGuardTests(unittest.TestCase):
    def test_api_runner_module_does_not_write_formal_assets(self):
        root = Path(__file__).resolve().parents[1]
        path = root / "app/domains/executions/runners/api_runner.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = set()
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
                for alias in node.names:
                    imported.add(f"{node.module}.{alias.name}")
        forbidden = {
            "app.services.case_service",
            "app.domains.cases.services.case_service",
            "app.services.requirement_doc_service",
            "app.domains.requirements.services.requirement_doc_service",
            "app.services.report_generator",
            "app.domains.reports.services.report_generator",
            "app.domains.reports.services.report_service",
        }
        self.assertTrue(forbidden.isdisjoint(imported))

    def test_execution_service_is_router_entry_not_runner(self):
        from app.api import executions as executions_api

        source = Path(executions_api.__file__).read_text(encoding="utf-8")
        self.assertIn("ExecutionService", source)
        self.assertNotIn("TestExecutorService(", source)
        self.assertNotIn("APIRunner(", source)


class CompatibilityAliasTests(unittest.TestCase):
    def test_service_aliases(self):
        from app.domains.executions.services.execution_service import ExecutionService as Dom
        from app.domains.reports.services.report_service import ReportService as DomReport
        from app.services.execution_service import ExecutionService as Leg
        from app.services.report_service import ReportService as LegReport

        self.assertIs(Dom, Leg)
        self.assertIs(DomReport, LegReport)


if __name__ == "__main__":
    unittest.main()

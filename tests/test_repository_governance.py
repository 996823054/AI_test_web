from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_TRACKED_PARTS = {
    ".idea",
    ".logs",
    ".superpowers",
    "__pycache__",
    "artifacts",
    "dist",
    "logs",
    "node_modules",
    "uploads",
}
FORBIDDEN_TRACKED_SUFFIXES = {".db", ".pyc", ".pyo", ".sqlite", ".sqlite3"}

IGNORED_EXAMPLES = (
    ".idea/workspace.xml",
    ".logs/backend.log",
    ".superpowers/state/server.pid",
    "artifacts/report.html",
    "backend/ai_test_platform.db",
    "backend/app/__pycache__/main.cpython-313.pyc",
    "backend/uploads/requirement_docs/runtime.md",
    "frontend/dist/index.html",
    "frontend/node_modules/.vite/vitest/results.json",
    "logs/app.log",
    "node_modules/appium/package.json",
    "uploads/requirement_docs/runtime.md",
)


def run_git(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=ROOT,
        check=False,
        capture_output=True,
        input=input_text,
        text=True,
    )


class RepositoryGovernanceTest(unittest.TestCase):
    def test_document_links_are_valid(self) -> None:
        result = subprocess.run(
            (sys.executable, "scripts/check_document_links.py"),
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_runtime_products_are_not_tracked(self) -> None:
        result = run_git("ls-files")
        self.assertEqual(result.returncode, 0, result.stderr)

        forbidden = []
        for raw_path in result.stdout.splitlines():
            path = Path(raw_path)
            if (
                FORBIDDEN_TRACKED_PARTS.intersection(path.parts)
                or path.suffix in FORBIDDEN_TRACKED_SUFFIXES
            ):
                forbidden.append(raw_path)

        self.assertEqual(
            forbidden,
            [],
            "以下运行产物仍被 Git 跟踪：\n" + "\n".join(forbidden),
        )

    def test_runtime_product_examples_are_ignored(self) -> None:
        result = run_git(
            "check-ignore",
            "--stdin",
            "--no-index",
            input_text="\n".join(IGNORED_EXAMPLES) + "\n",
        )
        ignored = set(result.stdout.splitlines())
        missing = sorted(set(IGNORED_EXAMPLES) - ignored)
        self.assertEqual(
            missing,
            [],
            "以下运行产物样例未被 .gitignore 覆盖：\n" + "\n".join(missing),
        )


if __name__ == "__main__":
    unittest.main()

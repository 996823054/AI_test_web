"""
Midscene iOS runner service
===========================
Bridges the FastAPI backend to the Node-based Midscene iOS SDK.
"""

import json
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

import requests

from app.config import PROJECT_DIR, settings


BACKEND_DIR = Path(__file__).resolve().parents[2]
RUNNER_DIR = BACKEND_DIR / "runners" / "midscene-ios"
RUNNER_FILE = RUNNER_DIR / "run.mjs"
MIDSCENE_REPO_DIR = PROJECT_DIR / "midscene"
DEFAULT_WDA_HOST = "127.0.0.1"
DEFAULT_WDA_PORT = 8100


class MidsceneIOSRunnerService:
    """Environment checks and execution bridge for Midscene iOS."""

    def health(self) -> dict[str, Any]:
        node_path = shutil.which("node")
        pnpm_path = shutil.which("pnpm")
        xcrun_path = shutil.which("xcrun")
        xcodebuild_path = shutil.which("xcodebuild")
        is_macos = platform.system() == "Darwin"

        checks = {
            "macos": {
                "ok": is_macos,
                "detail": platform.platform(),
            },
            "node": {
                "ok": bool(node_path),
                "detail": node_path or "未找到 node，请先安装 Node.js >= 18.19.0",
            },
            "pnpm": {
                "ok": bool(pnpm_path),
                "detail": pnpm_path or "未找到 pnpm；可继续使用 npx pnpm@9.3.0",
            },
            "xcrun": {
                "ok": bool(xcrun_path),
                "detail": xcrun_path or "未找到 xcrun，请确认已安装 Xcode Command Line Tools",
            },
            "xcodebuild": {
                "ok": bool(xcodebuild_path),
                "detail": xcodebuild_path or "未找到 xcodebuild，请确认已安装 Xcode",
            },
            "runner": {
                "ok": RUNNER_FILE.exists(),
                "detail": str(RUNNER_FILE),
            },
            "midscene_repo": {
                "ok": MIDSCENE_REPO_DIR.exists(),
                "detail": str(MIDSCENE_REPO_DIR),
            },
        }

        required_ok = checks["macos"]["ok"] and checks["node"]["ok"] and checks["runner"]["ok"]
        return {
            "ready": required_ok,
            "checks": checks,
            "message": "基础环境可用" if required_ok else "基础环境未就绪，请按检查项修复",
        }

    def check_wda(self, host: str = DEFAULT_WDA_HOST, port: int = DEFAULT_WDA_PORT) -> dict[str, Any]:
        url = f"http://{host}:{port}/status"
        started_at = time.time()
        try:
            response = requests.get(url, timeout=3)
            duration = round(time.time() - started_at, 3)
            body = response.text[:1000]
            ready = response.ok and "sessionId" in body
            return {
                "ready": ready,
                "url": url,
                "status_code": response.status_code,
                "duration": duration,
                "message": "WebDriverAgent 已连接" if ready else "WebDriverAgent 返回异常状态",
                "raw": body,
                "guidance": self._wda_guidance(host, port) if not ready else [],
            }
        except requests.RequestException as exc:
            duration = round(time.time() - started_at, 3)
            return {
                "ready": False,
                "url": url,
                "status_code": None,
                "duration": duration,
                "message": f"无法连接 WebDriverAgent: {exc}",
                "raw": "",
                "guidance": self._wda_guidance(host, port),
            }

    def run(self, payload: dict[str, Any], timeout: int = 300) -> dict[str, Any]:
        if not RUNNER_FILE.exists():
            return {
                "success": False,
                "error": f"Midscene iOS runner 不存在: {RUNNER_FILE}",
                "steps": [],
                "assertions": [],
            }

        node_path = shutil.which("node")
        if not node_path:
            return {
                "success": False,
                "error": "未找到 node，请先安装 Node.js >= 18.19.0",
                "steps": [],
                "assertions": [],
            }

        runner_payload = {
            **payload,
            "midsceneRepoDir": str(MIDSCENE_REPO_DIR),
        }
        env = self._build_env(payload.get("model"))
        started_at = time.time()

        try:
            process = subprocess.run(
                [node_path, str(RUNNER_FILE)],
                input=json.dumps(runner_payload, ensure_ascii=False),
                text=True,
                capture_output=True,
                timeout=timeout,
                env=env,
                cwd=str(BACKEND_DIR),
            )
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Midscene iOS 执行超时，超过 {timeout} 秒",
                "steps": [],
                "assertions": [],
                "duration": round(time.time() - started_at, 3),
            }

        duration = round(time.time() - started_at, 3)
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()

        if not stdout:
            return {
                "success": False,
                "error": stderr or "Midscene iOS runner 未返回结果",
                "steps": [],
                "assertions": [],
                "duration": duration,
                "exit_code": process.returncode,
            }

        try:
            result = json.loads(stdout)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Midscene iOS runner 返回了非 JSON 内容",
                "raw": stdout,
                "stderr": stderr,
                "steps": [],
                "assertions": [],
                "duration": duration,
                "exit_code": process.returncode,
            }

        result.setdefault("duration", duration)
        result.setdefault("exit_code", process.returncode)
        if stderr:
            result["stderr"] = stderr
        if process.returncode != 0:
            result["success"] = False
        return result

    def _build_env(self, model: Optional[dict[str, Any]]) -> dict[str, str]:
        env = {
            key: value
            for key, value in dict(**os.environ).items()
            if value is not None
        }
        model = model or {}

        model_name = model.get("name") or settings.LLM_MODEL
        api_key = model.get("api_key") or settings.LLM_API_KEY
        base_url = model.get("base_url") or settings.LLM_BASE_URL

        if model_name:
            env["MIDSCENE_MODEL_NAME"] = str(model_name)
        if api_key:
            env["MIDSCENE_MODEL_API_KEY"] = str(api_key)
            env["OPENAI_API_KEY"] = str(api_key)
        if base_url:
            env["MIDSCENE_MODEL_BASE_URL"] = str(base_url)
            env["OPENAI_BASE_URL"] = str(base_url)
        if settings.LLM_TIMEOUT:
            env["MIDSCENE_MODEL_TIMEOUT"] = str(settings.LLM_TIMEOUT * 1000)
        return env

    def _wda_guidance(self, host: str, port: int) -> list[str]:
        return [
            "Midscene iOS 不会自动启动 WebDriverAgent，需要先手动启动 WDA。",
            "模拟器：在 Xcode 中选择目标 simulator，运行 WebDriverAgentRunner。",
            f"真机：启动 WDA 后使用 iproxy {port} 8100 将本机端口转发到设备。",
            f"确认浏览器或 curl 能访问 http://{host}:{port}/status。",
        ]

from __future__ import annotations

import importlib
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import path_setup


class _FakeExecInput:
    def __init__(self, command: str, cwd: str | None = None, env: dict[str, str] | None = None, timeout_sec: int | None = None):
        self.command = command
        self.cwd = cwd
        self.env = env
        self.timeout_sec = timeout_sec


class _FakeCodex:
    _OUTPUT_FILENAME = "codex.txt"

    def __init__(
        self,
        logs_dir: Path,
        model_name: str | None = None,
        reasoning_effort: str | None = "high",
        *args,
        **kwargs,
    ) -> None:
        self.logs_dir = logs_dir
        self.model_name = model_name
        self._reasoning_effort = reasoning_effort


class _FakeEnvironmentPaths:
    agent_dir = Path("/logs/agent")


def _install_fake_harbor_modules() -> None:
    harbor_module = types.ModuleType("harbor")
    agents_module = types.ModuleType("harbor.agents")
    installed_module = types.ModuleType("harbor.agents.installed")
    base_module = types.ModuleType("harbor.agents.installed.base")
    codex_module = types.ModuleType("harbor.agents.installed.codex")
    models_module = types.ModuleType("harbor.models")
    trial_module = types.ModuleType("harbor.models.trial")
    paths_module = types.ModuleType("harbor.models.trial.paths")

    base_module.ExecInput = _FakeExecInput
    codex_module.Codex = _FakeCodex
    paths_module.EnvironmentPaths = _FakeEnvironmentPaths

    sys.modules["harbor"] = harbor_module
    sys.modules["harbor.agents"] = agents_module
    sys.modules["harbor.agents.installed"] = installed_module
    sys.modules["harbor.agents.installed.base"] = base_module
    sys.modules["harbor.agents.installed.codex"] = codex_module
    sys.modules["harbor.models"] = models_module
    sys.modules["harbor.models.trial"] = trial_module
    sys.modules["harbor.models.trial.paths"] = paths_module


def _load_module():
    _install_fake_harbor_modules()
    sys.modules.pop("skillx.harbor_agents", None)
    return importlib.import_module("skillx.harbor_agents")


class HarborAgentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_auth_backed_codex_cleans_auth_file_and_preserves_pipeline_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir)
            with mock.patch.object(
                self.module.AuthBackedCodex,
                "_resolve_auth_json_text",
                return_value='{"auth_mode":"chatgpt"}',
            ):
                agent = self.module.AuthBackedCodex(logs_dir=logs_dir, model_name="openai/gpt-5.4")
                commands = agent.create_run_agent_commands("Create hello.txt")

        self.assertEqual(len(commands), 2)
        self.assertIn('printf "%s" "$CODEX_AUTH_JSON_B64" | base64 -d >"$CODEX_HOME/auth.json"', commands[0].command)
        self.assertEqual(commands[1].env["CODEX_HOME"], "/logs/agent")
        self.assertIn("CODEX_AUTH_JSON_B64", commands[1].env)
        self.assertIn("/bin/bash -lc", commands[1].command)
        self.assertIn("set -o pipefail;", commands[1].command)
        self.assertIn("codex exec", commands[1].command)
        self.assertIn("tee /logs/agent/codex.txt;", commands[1].command)
        self.assertIn('rm -rf "$CODEX_HOME/auth.json"; exit "$status"', commands[1].command)


if __name__ == "__main__":
    unittest.main()

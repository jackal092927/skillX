from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import path_setup
from skillx.c4ar.playbook_agent_runner import (
    PlaybookAgentExecutionError,
    PlaybookAgentTimeoutError,
    ensure_playbook_path,
    resolve_cli_model_name,
    resolve_playbook_cli_name,
    run_playbook_agent,
)


class C4arPlaybookAgentRunnerTests(unittest.TestCase):
    def test_ensure_playbook_path_rejects_missing_value(self) -> None:
        with self.assertRaises(ValueError):
            ensure_playbook_path(None, role_name="role_a")

    def test_resolve_cli_model_name_maps_role_models(self) -> None:
        self.assertEqual(resolve_cli_model_name("codex-5.3"), "gpt-5.3-codex")
        self.assertEqual(resolve_cli_model_name("gpt-5.4"), "gpt-5.4")
        self.assertEqual(resolve_cli_model_name("anthropic/claude-sonnet-4-5"), "claude-sonnet-4-5")
        self.assertEqual(resolve_cli_model_name("openai/gpt-5.2-codex"), "gpt-5.2-codex")
        self.assertEqual(resolve_cli_model_name("custom-model"), "custom-model")

    def test_resolve_playbook_cli_name_switches_on_model_family(self) -> None:
        self.assertEqual(resolve_playbook_cli_name("codex-5.3"), "codex")
        self.assertEqual(resolve_playbook_cli_name("gpt-5.4"), "codex")
        self.assertEqual(resolve_playbook_cli_name("anthropic/claude-sonnet-4-5"), "claude")
        self.assertEqual(resolve_playbook_cli_name("sonnet"), "claude")

    def test_run_playbook_agent_writes_logs_and_validates_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            playbook = tmp / "role_a.md"
            playbook.write_text("# playbook\n")
            output_dir = tmp / "out"
            expected_json = output_dir / "session_evidence.json"
            expected_md = output_dir / "session_evidence.md"
            captured: dict[str, object] = {}

            def fake_subprocess_runner(command, **kwargs):
                captured["command"] = command
                captured["cwd"] = kwargs.get("cwd")
                captured["input"] = kwargs.get("input")
                expected_json.parent.mkdir(parents=True, exist_ok=True)
                expected_json.write_text(json.dumps({"ok": True}) + "\n")
                expected_md.write_text("# Session Evidence\n")
                last_message_path = Path(command[command.index("--output-last-message") + 1])
                last_message_path.write_text(
                    json.dumps(
                        {
                            "status": "ok",
                            "json_path": str(expected_json),
                            "markdown_path": str(expected_md),
                            "notes": "completed",
                        }
                    )
                    + "\n"
                )
                return subprocess.CompletedProcess(command, 0, stdout='{"event":"done"}\n', stderr="")

            result = run_playbook_agent(
                role_name="role_a",
                model_name="codex-5.3",
                playbook_path=playbook,
                output_dir=output_dir,
                prompt="read the playbook and write outputs",
                final_response_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "json_path": {"type": "string"},
                        "markdown_path": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["status", "json_path", "markdown_path", "notes"],
                    "additionalProperties": False,
                },
                expected_output_paths=[expected_json, expected_md],
                subprocess_runner=fake_subprocess_runner,
            )

            self.assertEqual(result.final_message["status"], "ok")
            self.assertTrue(Path(result.command_path).exists())
            self.assertTrue(Path(result.prompt_path).exists())
            self.assertTrue(Path(result.stdout_path).exists())
            self.assertEqual(captured["command"][0], "codex")
            self.assertIn("--output-schema", captured["command"])
            self.assertIn("--output-last-message", captured["command"])
            self.assertIn("--model", captured["command"])
            self.assertIn("read the playbook", str(captured["input"]))

    def test_run_playbook_agent_uses_claude_cli_for_anthropic_models(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            playbook = tmp / "role_b.md"
            playbook.write_text("# playbook\n")
            output_dir = tmp / "out"
            expected_json = output_dir / "refine_plan.json"
            expected_md = output_dir / "refine_plan.md"
            captured: dict[str, object] = {}

            def fake_subprocess_runner(command, **kwargs):
                captured["command"] = command
                captured["cwd"] = kwargs.get("cwd")
                captured["input"] = kwargs.get("input")
                expected_json.parent.mkdir(parents=True, exist_ok=True)
                expected_json.write_text(json.dumps({"ok": True}) + "\n")
                expected_md.write_text("# Refine Plan\n")
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout=json.dumps(
                        {
                            "result": "completed",
                            "structured_output": {
                                "status": "ok",
                                "json_path": str(expected_json),
                                "markdown_path": str(expected_md),
                                "notes": "completed",
                            },
                        }
                    )
                    + "\n",
                    stderr="",
                )

            result = run_playbook_agent(
                role_name="role_b",
                model_name="anthropic/claude-sonnet-4-5",
                playbook_path=playbook,
                output_dir=output_dir,
                prompt="read the playbook and write outputs",
                final_response_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "json_path": {"type": "string"},
                        "markdown_path": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["status", "json_path", "markdown_path", "notes"],
                    "additionalProperties": False,
                },
                expected_output_paths=[expected_json, expected_md],
                subprocess_runner=fake_subprocess_runner,
            )

            self.assertEqual(captured["command"][0], "claude")
            self.assertIn("--print", captured["command"])
            self.assertIn("--output-format", captured["command"])
            self.assertIn("json", captured["command"])
            self.assertIn("--json-schema", captured["command"])
            self.assertIn("--model", captured["command"])
            self.assertNotIn("--output-last-message", captured["command"])
            self.assertEqual(result.final_message["status"], "ok")
            self.assertEqual(json.loads(Path(result.last_message_path).read_text())["status"], "ok")

    def test_run_playbook_agent_retries_timeout_and_records_attempts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            playbook = tmp / "role_a.md"
            playbook.write_text("# playbook\n")
            output_dir = tmp / "out"
            expected_json = output_dir / "session_evidence.json"
            expected_md = output_dir / "session_evidence.md"
            attempts = {"count": 0}

            def fake_subprocess_runner(command, **kwargs):
                attempts["count"] += 1
                if attempts["count"] == 1:
                    raise subprocess.TimeoutExpired(
                        cmd=command,
                        timeout=kwargs["timeout"],
                        output='{"event":"partial"}\n',
                        stderr="still running\n",
                    )
                expected_json.parent.mkdir(parents=True, exist_ok=True)
                expected_json.write_text(json.dumps({"ok": True}) + "\n")
                expected_md.write_text("# Session Evidence\n")
                last_message_path = Path(command[command.index("--output-last-message") + 1])
                last_message_path.write_text(
                    json.dumps(
                        {
                            "status": "ok",
                            "json_path": str(expected_json),
                            "markdown_path": str(expected_md),
                            "notes": "completed",
                        }
                    )
                    + "\n"
                )
                return subprocess.CompletedProcess(command, 0, stdout='{"event":"done"}\n', stderr="")

            result = run_playbook_agent(
                role_name="role_a",
                model_name="codex-5.3",
                playbook_path=playbook,
                output_dir=output_dir,
                prompt="retry after timeout",
                final_response_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "json_path": {"type": "string"},
                        "markdown_path": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["status", "json_path", "markdown_path", "notes"],
                    "additionalProperties": False,
                },
                expected_output_paths=[expected_json, expected_md],
                timeout_sec=12,
                max_attempts=2,
                retry_backoff_sec=0.0,
                subprocess_runner=fake_subprocess_runner,
            )

            metadata = json.loads(Path(result.metadata_path).read_text())
            self.assertEqual(attempts["count"], 2)
            self.assertEqual(len(metadata["attempts"]), 2)
            self.assertTrue(metadata["attempts"][0]["timed_out"])
            self.assertEqual(metadata["attempts"][1]["returncode"], 0)
            self.assertTrue((output_dir / "agent_run" / "stdout.attempt-1.jsonl").exists())
            self.assertEqual(result.final_message["status"], "ok")

    def test_run_playbook_agent_raises_after_exhausting_timeout_retries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            playbook = tmp / "role_a.md"
            playbook.write_text("# playbook\n")
            output_dir = tmp / "out"
            attempts = {"count": 0}

            def fake_subprocess_runner(command, **kwargs):
                attempts["count"] += 1
                raise subprocess.TimeoutExpired(
                    cmd=command,
                    timeout=kwargs["timeout"],
                    output="partial\n",
                    stderr="hung\n",
                )

            with self.assertRaises(PlaybookAgentTimeoutError):
                run_playbook_agent(
                    role_name="role_a",
                    model_name="codex-5.3",
                    playbook_path=playbook,
                    output_dir=output_dir,
                    prompt="always times out",
                    final_response_schema={"type": "object"},
                    expected_output_paths=[output_dir / "session_evidence.json"],
                    timeout_sec=3,
                    max_attempts=2,
                    retry_backoff_sec=0.0,
                    subprocess_runner=fake_subprocess_runner,
                )

            metadata = json.loads((output_dir / "agent_run" / "run_metadata.json").read_text())
            self.assertEqual(attempts["count"], 2)
            self.assertEqual(len(metadata["attempts"]), 2)
            self.assertTrue(all(item["timed_out"] for item in metadata["attempts"]))

    def test_run_playbook_agent_does_not_retry_nonzero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            playbook = tmp / "role_b.md"
            playbook.write_text("# playbook\n")
            output_dir = tmp / "out"
            attempts = {"count": 0}

            def fake_subprocess_runner(command, **kwargs):
                attempts["count"] += 1
                return subprocess.CompletedProcess(command, 23, stdout="bad\n", stderr="exit\n")

            with self.assertRaises(PlaybookAgentExecutionError):
                run_playbook_agent(
                    role_name="role_b",
                    model_name="codex-5.3",
                    playbook_path=playbook,
                    output_dir=output_dir,
                    prompt="nonzero exit",
                    final_response_schema={"type": "object"},
                    expected_output_paths=[output_dir / "refine_plan.json"],
                    timeout_sec=5,
                    max_attempts=3,
                    retry_backoff_sec=0.0,
                    subprocess_runner=fake_subprocess_runner,
                )

            metadata = json.loads((output_dir / "agent_run" / "run_metadata.json").read_text())
            self.assertEqual(attempts["count"], 1)
            self.assertEqual(len(metadata["attempts"]), 1)
            self.assertEqual(metadata["attempts"][0]["returncode"], 23)


if __name__ == "__main__":
    unittest.main()

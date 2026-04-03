from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import path_setup
from skillx.c4ar.role_a import RoleAConfig, RoleAInputs, run_role_a


class C4arRoleATests(unittest.TestCase):
    def test_role_a_requires_playbook_without_custom_model_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            log_path = tmp / "session.log"
            log_path.write_text("tool=read_file path=skill.md\n")

            with self.assertRaises(ValueError):
                run_role_a(
                    RoleAInputs(
                        task_id="trend-anomaly-causal-inference",
                        round_index=0,
                        source_log_paths=[str(log_path)],
                        output_dir=str(tmp / "role_a"),
                    ),
                    config=RoleAConfig(model_name="codex-5.3"),
                )

    def test_role_a_rejects_missing_source_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            missing = tmp / "missing.jsonl"
            with self.assertRaises(FileNotFoundError):
                run_role_a(
                    RoleAInputs(
                        task_id="trend-anomaly-causal-inference",
                        round_index=0,
                        source_log_paths=[str(missing)],
                        output_dir=str(tmp / "role_a"),
                    )
                )

    def test_role_a_uses_custom_model_runner_and_writes_validated_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            log_path = tmp / "session.log"
            log_path.write_text("tool=read_file path=skill.md\n")
            calls: list[tuple[str, int]] = []

            def runner(inputs, config):
                calls.append((inputs.task_id, inputs.round_index))
                return {
                    "task_id": inputs.task_id,
                    "round_index": inputs.round_index,
                    "role": config.role_name,
                    "model_name": config.model_name,
                    "source_log_paths": inputs.source_log_paths,
                    "dominant_failure_pattern": "custom runner summary",
                    "wasted_loop_signals": [],
                    "tool_misuse_signals": [],
                    "critical_turns": [],
                    "skill_misguidance_signals": [],
                    "recommended_edit_targets": ["aggregation guidance"],
                    "evidence_refs": [f"{inputs.source_log_paths[0]}:1"],
                    "observed_at": "2026-03-25T00:00:00+00:00",
                }

            outputs = run_role_a(
                RoleAInputs(
                    task_id="trend-anomaly-causal-inference",
                    round_index=1,
                    source_log_paths=[str(log_path)],
                    output_dir=str(tmp / "role_a"),
                ),
                config=RoleAConfig(model_name="codex-5.3"),
                model_runner=runner,
            )

            self.assertEqual(calls, [("trend-anomaly-causal-inference", 1)])
            payload = json.loads(Path(outputs.json_path).read_text())
            self.assertEqual(payload["dominant_failure_pattern"], "custom runner summary")

    def test_role_a_rejects_invalid_model_runner_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            log_path = tmp / "session.log"
            log_path.write_text("tool=read_file path=skill.md\n")

            def runner(inputs, config):
                return {
                    "task_id": "",
                    "round_index": -1,
                    "role": config.role_name,
                    "model_name": config.model_name,
                    "source_log_paths": [],
                    "dominant_failure_pattern": "",
                    "evidence_refs": [],
                    "observed_at": "",
                }

            with self.assertRaises(ValueError):
                run_role_a(
                    RoleAInputs(
                        task_id="trend-anomaly-causal-inference",
                        round_index=1,
                        source_log_paths=[str(log_path)],
                        output_dir=str(tmp / "role_a"),
                    ),
                    config=RoleAConfig(model_name="codex-5.3"),
                    model_runner=runner,
                )


if __name__ == "__main__":
    unittest.main()

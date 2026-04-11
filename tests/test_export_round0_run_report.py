from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "export_round0_run_report.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("export_round0_run_report", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ExportRound0RunReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def _write_run_status(self, path: Path, *, status: str, round_budget: int) -> None:
        path.write_text(
            "\n".join(
                [
                    f"- status: `{status}`",
                    "- run_id: `demo-run`",
                    "- task: `demo-task`",
                    "- source_run_dir: `/tmp/source`",
                    f"- round_budget: `{round_budget}`",
                    "- orchestration_mode: `c4ar`",
                    "- updated_at: `2026-04-11T06:00:00+00:00`",
                ]
            )
            + "\n"
        )

    def test_build_run_report_collects_round_scores_and_launcher_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            materialized_root = root / "materialized"
            log_dir = materialized_root / "launcher_logs" / "demo-run"
            log_dir.mkdir(parents=True)

            success_output_dir = root / "outputs" / "task-alpha__artifact-generation"
            failure_output_dir = root / "outputs" / "task-beta__artifact-generation"
            success_rounds_dir = success_output_dir / "refine" / "task-alpha" / "rounds"
            failure_output_dir.mkdir(parents=True)
            success_rounds_dir.mkdir(parents=True)

            pair_specs = [
                {
                    "pair_id": "task-alpha__artifact-generation",
                    "task_name": "task-alpha",
                    "schema_id": "artifact-generation",
                    "official_scores": {"no_skills": 5.0, "with_skills": 10.0},
                },
                {
                    "pair_id": "task-beta__artifact-generation",
                    "task_name": "task-beta",
                    "schema_id": "artifact-generation",
                    "official_scores": {"no_skills": 0.0, "with_skills": 20.0},
                },
            ]
            (materialized_root / "pair_specs.jsonl").write_text(
                "\n".join(json.dumps(item) for item in pair_specs) + "\n"
            )

            summary = {
                "total_pairs": 2,
                "completed_pairs": 2,
                "succeeded_pairs": 1,
                "failed_pairs": 1,
                "results": [
                    {
                        "pair_id": "task-alpha__artifact-generation",
                        "task_name": "task-alpha",
                        "schema_id": "artifact-generation",
                        "status": "succeeded",
                        "stage": "run",
                        "returncode": 0,
                        "output_dir": str(success_output_dir),
                    },
                    {
                        "pair_id": "task-beta__artifact-generation",
                        "task_name": "task-beta",
                        "schema_id": "artifact-generation",
                        "status": "failed",
                        "stage": "run",
                        "returncode": 1,
                        "output_dir": str(failure_output_dir),
                    },
                ],
            }
            (log_dir / "summary.json").write_text(json.dumps(summary))
            (log_dir / "events.ndjson").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "event": "pair_started",
                                "pair_id": "task-alpha__artifact-generation",
                                "observed_at": "2026-04-11T00:00:00+00:00",
                            }
                        ),
                        json.dumps(
                            {
                                "event": "pair_succeeded",
                                "pair_id": "task-alpha__artifact-generation",
                                "observed_at": "2026-04-11T00:10:00+00:00",
                            }
                        ),
                        json.dumps(
                            {
                                "event": "pair_started",
                                "pair_id": "task-beta__artifact-generation",
                                "observed_at": "2026-04-11T00:10:00+00:00",
                            }
                        ),
                        json.dumps(
                            {
                                "event": "pair_failed",
                                "pair_id": "task-beta__artifact-generation",
                                "observed_at": "2026-04-11T00:10:30+00:00",
                            }
                        ),
                    ]
                )
                + "\n"
            )
            (log_dir / "launcher.stdout.log").write_text(
                "\n".join(
                    [
                        "[1/2] task-alpha__artifact-generation",
                        "  OK",
                        "[2/2] task-beta__artifact-generation",
                        "Traceback (most recent call last):",
                        "FileNotFoundError: missing task skill file",
                        "  FAILED with exit code 1",
                    ]
                )
                + "\n"
            )

            self._write_run_status(success_output_dir / "RUN_STATUS.md", status="completed", round_budget=3)
            self._write_run_status(failure_output_dir / "RUN_STATUS.md", status="failed", round_budget=3)

            round0 = success_rounds_dir / "round-0"
            round1 = success_rounds_dir / "round-1"
            (round0 / "tune_check").mkdir(parents=True)
            (round0 / "role_b").mkdir(parents=True)
            (round1 / "tune_check").mkdir(parents=True)
            (round1 / "role_b").mkdir(parents=True)
            (round0 / "tune_check" / "result.json").write_text(
                json.dumps({"reward": 0.0, "exception_stats": {}, "classification": {"kind": "scientific_failure"}})
            )
            (round1 / "tune_check" / "result.json").write_text(
                json.dumps({"reward": 0.5, "exception_stats": {}, "classification": {"kind": "clean_success"}})
            )
            (round0 / "role_b" / "round_decision.json").write_text(json.dumps({"decision": "continue", "reason": "keep going"}))
            (round1 / "role_b" / "round_decision.json").write_text(json.dumps({"decision": "stop", "reason": "good enough"}))
            (round0 / "orchestrator_log.ndjson").write_text(
                "\n".join(
                    [
                        json.dumps({"event_type": "round_started", "timestamp": "2026-04-11T00:00:00+00:00"}),
                        json.dumps({"event_type": "executor_completed", "timestamp": "2026-04-11T00:01:00+00:00"}),
                        json.dumps({"event_type": "role_a_completed", "timestamp": "2026-04-11T00:02:00+00:00"}),
                        json.dumps({"event_type": "role_b_completed", "timestamp": "2026-04-11T00:03:00+00:00"}),
                        json.dumps({"event_type": "round_decision_loaded", "timestamp": "2026-04-11T00:03:30+00:00"}),
                    ]
                )
                + "\n"
            )
            (round1 / "orchestrator_log.ndjson").write_text(
                "\n".join(
                    [
                        json.dumps({"event_type": "round_started", "timestamp": "2026-04-11T00:04:00+00:00"}),
                        json.dumps({"event_type": "executor_completed", "timestamp": "2026-04-11T00:05:00+00:00"}),
                        json.dumps({"event_type": "role_a_completed", "timestamp": "2026-04-11T00:06:00+00:00"}),
                        json.dumps({"event_type": "role_b_completed", "timestamp": "2026-04-11T00:07:00+00:00"}),
                        json.dumps({"event_type": "round_decision_loaded", "timestamp": "2026-04-11T00:07:30+00:00"}),
                    ]
                )
                + "\n"
            )
            refine_summary_path = success_output_dir / "refine" / "task-alpha" / "refine_summary.json"
            refine_summary_path.parent.mkdir(parents=True, exist_ok=True)
            refine_summary_path.write_text(
                json.dumps(
                    {
                        "task_id": "task-alpha",
                        "selected": {"round_index": 1, "reward": 0.5, "classification": {"kind": "clean_success"}},
                        "rounds": [
                            {"round_index": 0, "reward": 0.0},
                            {"round_index": 1, "reward": 0.5},
                        ],
                    }
                )
            )

            report = self.module.build_run_report(
                materialized_root=materialized_root,
                run_label="demo-run",
            )

            self.assertEqual(report["pair_count_succeeded"], 1)
            self.assertEqual(report["pair_count_failed"], 1)
            success_pair = next(item for item in report["pair_results"] if item["pair_id"] == "task-alpha__artifact-generation")
            failure_pair = next(item for item in report["pair_results"] if item["pair_id"] == "task-beta__artifact-generation")

            self.assertEqual(success_pair["selected"]["round_index"], 1)
            self.assertEqual(success_pair["selected"]["score_pct"], 50.0)
            self.assertTrue(success_pair["early_stop"])
            self.assertEqual(success_pair["delta_vs_c1_pp"], 40.0)
            self.assertIn("FileNotFoundError", failure_pair["failure"]["summary"])

            table = self.module.render_results_table(report)
            self.assertIn("## task-alpha", table)
            self.assertIn("task-beta", table)
            self.assertIn("FileNotFoundError", table)

    def test_build_run_report_prefers_run_failure_payload_and_detects_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            materialized_root = root / "materialized"
            log_dir = materialized_root / "launcher_logs" / "timeout-run"
            log_dir.mkdir(parents=True)

            pair_output_dir = root / "outputs" / "task-gamma__artifact-generation"
            pair_output_dir.mkdir(parents=True)
            self._write_run_status(pair_output_dir / "RUN_STATUS.md", status="failed", round_budget=3)
            (pair_output_dir / "run_failure.json").write_text(
                json.dumps(
                    {
                        "error_type": "PlaybookAgentTimeoutError",
                        "error_message": "role_a timed out after 3 attempts",
                        "failed_stage": "role_a",
                        "failed_round": 1,
                        "manual_intervention": False,
                    }
                )
            )

            (materialized_root / "pair_specs.jsonl").write_text(
                json.dumps(
                    {
                        "pair_id": "task-gamma__artifact-generation",
                        "task_name": "task-gamma",
                        "schema_id": "artifact-generation",
                        "official_scores": {"no_skills": 0.0, "with_skills": 5.0},
                    }
                )
                + "\n"
            )
            (log_dir / "summary.json").write_text(
                json.dumps(
                    {
                        "total_pairs": 1,
                        "completed_pairs": 1,
                        "succeeded_pairs": 0,
                        "failed_pairs": 1,
                        "results": [
                            {
                                "pair_id": "task-gamma__artifact-generation",
                                "task_name": "task-gamma",
                                "schema_id": "artifact-generation",
                                "status": "failed",
                                "stage": "run",
                                "returncode": 1,
                                "output_dir": str(pair_output_dir),
                            }
                        ],
                    }
                )
            )
            (log_dir / "events.ndjson").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "event": "pair_started",
                                "pair_id": "task-gamma__artifact-generation",
                                "observed_at": "2026-04-11T02:00:00+00:00",
                            }
                        ),
                        json.dumps(
                            {
                                "event": "pair_failed",
                                "pair_id": "task-gamma__artifact-generation",
                                "observed_at": "2026-04-11T02:10:00+00:00",
                            }
                        ),
                    ]
                )
                + "\n"
            )
            (log_dir / "launcher.stdout.log").write_text("[1/1] task-gamma__artifact-generation\n  FAILED with exit code 1\n")

            report = self.module.build_run_report(
                materialized_root=materialized_root,
                run_label="timeout-run",
            )
            pair = report["pair_results"][0]

            self.assertEqual(pair["failure"]["error_type"], "PlaybookAgentTimeoutError")
            self.assertTrue(pair["timeout_detected"])
            self.assertEqual(pair["failure"]["failed_round"], 1)

    def test_build_run_report_marks_stale_running_status_failed_and_sanitizes_home_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            materialized_root = root / "materialized"
            log_dir = materialized_root / "launcher_logs" / "stale-run"
            log_dir.mkdir(parents=True)

            pair_output_dir = root / "outputs" / "task-delta__artifact-generation"
            pair_output_dir.mkdir(parents=True)
            self._write_run_status(pair_output_dir / "RUN_STATUS.md", status="running", round_budget=3)

            (materialized_root / "pair_specs.jsonl").write_text(
                json.dumps(
                    {
                        "pair_id": "task-delta__artifact-generation",
                        "task_name": "task-delta",
                        "schema_id": "artifact-generation",
                        "official_scores": {"no_skills": 1.0, "with_skills": 2.0},
                    }
                )
                + "\n"
            )
            (log_dir / "summary.json").write_text(
                json.dumps(
                    {
                        "total_pairs": 1,
                        "completed_pairs": 1,
                        "succeeded_pairs": 0,
                        "failed_pairs": 1,
                        "results": [
                            {
                                "pair_id": "task-delta__artifact-generation",
                                "task_name": "task-delta",
                                "schema_id": "artifact-generation",
                                "status": "failed",
                                "stage": "run",
                                "returncode": 1,
                                "output_dir": str(pair_output_dir),
                            }
                        ],
                    }
                )
            )
            (log_dir / "events.ndjson").write_text(
                json.dumps(
                    {
                        "event": "pair_failed",
                        "pair_id": "task-delta__artifact-generation",
                        "observed_at": "2026-04-11T02:10:00+00:00",
                    }
                )
                + "\n"
            )
            sensitive_path = str(Path.home() / "iWorld" / "projects" / "skillsbench-src" / "tasks" / "demo" / "SKILL.md")
            (log_dir / "launcher.stdout.log").write_text(
                "\n".join(
                    [
                        "[1/1] task-delta__artifact-generation",
                        "Traceback (most recent call last):",
                        f"FileNotFoundError: missing {sensitive_path}",
                    ]
                )
                + "\n"
            )

            report = self.module.build_run_report(
                materialized_root=materialized_root,
                run_label="stale-run",
            )
            pair = report["pair_results"][0]

            self.assertEqual(pair["run"]["status"], "failed")
            self.assertTrue(pair["run"]["stale_status"])
            self.assertIn("~/iWorld/projects/skillsbench-src", pair["failure"]["summary"])
            self.assertNotIn(str(Path.home()), pair["failure"]["summary"])

            runtime_md = self.module.render_runtime_status(report)
            eval_md = self.module.render_evaluation_matrices(report)
            self.assertIn("task-delta__artifact-generation", runtime_md)
            self.assertIn("Failure", runtime_md)
            self.assertIn("Evaluation Matrices", eval_md)


if __name__ == "__main__":
    unittest.main()

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
    / "build_round0_global_status.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("build_round0_global_status", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BuildRound0GlobalStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_build_global_status_aggregates_attempts_and_unrun_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skillsbench_root = root / "skillsbench-src"
            round0_root = root / "outer-loop-round0"

            for task_name in ("task-alpha", "task-beta"):
                (skillsbench_root / "tasks" / task_name).mkdir(parents=True)

            materialized_root = round0_root / "slice"
            materialized_root.mkdir(parents=True)
            (materialized_root / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_ids": ["artifact-generation", "analytic-pipeline"],
                        "task_names": ["task-alpha", "task-beta"],
                    }
                )
            )

            report_a_dir = materialized_root / "reports" / "run-a"
            report_b_dir = materialized_root / "reports" / "run-b"
            report_a_dir.mkdir(parents=True)
            report_b_dir.mkdir(parents=True)

            report_a = {
                "run_label": "run-a",
                "pair_count_total": 2,
                "pair_count_completed": 2,
                "pair_count_succeeded": 0,
                "pair_count_failed": 2,
                "pair_results": [
                    {
                        "pair_id": "task-alpha__artifact-generation",
                        "task_name": "task-alpha",
                        "schema_id": "artifact-generation",
                        "launcher": {
                            "status": "failed",
                            "stage": "run",
                            "returncode": 1,
                            "started_at": "2026-04-11T00:00:00+00:00",
                            "finished_at": "2026-04-11T00:10:00+00:00",
                        },
                        "run": {
                            "status": "failed",
                            "updated_at": "2026-04-11T00:10:00+00:00",
                            "output_dir": "<repo-root>/outputs/task-alpha__artifact-generation/run-a",
                        },
                        "failure": {
                            "failed_stage": "environment_check",
                            "error_type": "RuntimeError",
                            "summary": "RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes",
                        },
                        "selected": {"round_index": None, "score_pct": None},
                        "best_observed": {"round_index": None, "score_pct": None},
                        "early_stop": False,
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                    },
                    {
                        "pair_id": "task-beta__artifact-generation",
                        "task_name": "task-beta",
                        "schema_id": "artifact-generation",
                        "launcher": {
                            "status": "failed",
                            "stage": "run",
                            "returncode": 1,
                            "started_at": "2026-04-11T00:11:00+00:00",
                            "finished_at": "2026-04-11T00:11:05+00:00",
                        },
                        "run": {
                            "status": "failed",
                            "updated_at": "2026-04-11T00:11:05+00:00",
                            "output_dir": "<repo-root>/outputs/task-beta__artifact-generation/run-a",
                        },
                        "failure": {
                            "failed_stage": "discover_task_inputs",
                            "error_type": "FileNotFoundError",
                            "summary": "FileNotFoundError: missing task inputs for task-beta",
                        },
                        "selected": {"round_index": None, "score_pct": None},
                        "best_observed": {"round_index": None, "score_pct": None},
                        "early_stop": False,
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                    },
                ],
            }
            report_b = {
                "run_label": "run-b",
                "pair_count_total": 2,
                "pair_count_completed": 2,
                "pair_count_succeeded": 2,
                "pair_count_failed": 0,
                "pair_results": [
                    {
                        "pair_id": "task-alpha__artifact-generation",
                        "task_name": "task-alpha",
                        "schema_id": "artifact-generation",
                        "launcher": {
                            "status": "succeeded",
                            "stage": "run",
                            "returncode": 0,
                            "started_at": "2026-04-12T00:00:00+00:00",
                            "finished_at": "2026-04-12T00:10:00+00:00",
                        },
                        "run": {
                            "status": "completed",
                            "updated_at": "2026-04-12T00:10:00+00:00",
                            "output_dir": "<repo-root>/outputs/task-alpha__artifact-generation/run-b",
                        },
                        "failure": None,
                        "selected": {"round_index": 2, "score_pct": 75.0},
                        "best_observed": {"round_index": 2, "score_pct": 75.0},
                        "early_stop": True,
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                    },
                    {
                        "pair_id": "task-alpha__analytic-pipeline",
                        "task_name": "task-alpha",
                        "schema_id": "analytic-pipeline",
                        "launcher": {
                            "status": "failed",
                            "stage": "run",
                            "returncode": 1,
                            "started_at": "2026-04-12T00:11:00+00:00",
                            "finished_at": "2026-04-12T00:11:05+00:00",
                        },
                        "run": {
                            "status": "failed",
                            "updated_at": "2026-04-12T00:11:05+00:00",
                            "output_dir": "<repo-root>/outputs/task-alpha__analytic-pipeline/run-b",
                        },
                        "failure": {
                            "failed_stage": "environment_check",
                            "error_type": "RuntimeError",
                            "summary": "RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes",
                        },
                        "selected": {"round_index": None, "score_pct": None},
                        "best_observed": {"round_index": None, "score_pct": None},
                        "early_stop": False,
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                    },
                ],
            }
            (report_a_dir / "run_report.json").write_text(json.dumps(report_a))
            (report_b_dir / "run_report.json").write_text(json.dumps(report_b))

            payload = self.module.build_global_status(
                skillsbench_root=skillsbench_root,
                round0_root=round0_root,
            )

            self.assertEqual(payload["task_count_detected"], 2)
            self.assertEqual(payload["pair_count_expected"], 4)
            self.assertEqual(payload["pair_count_attempted"], 3)
            self.assertEqual(payload["pair_count_completed"], 1)
            self.assertEqual(payload["pair_count_docker_incident"], 1)
            self.assertEqual(payload["pair_count_other_failed"], 1)
            self.assertEqual(payload["pair_count_unrun"], 1)

            rows_by_pair = {row["pair_id"]: row for row in payload["pairs"]}
            recovered = rows_by_pair["task-alpha__artifact-generation"]
            self.assertEqual(recovered["latest_status"], "completed")
            self.assertEqual(recovered["attempt_count"], 2)
            self.assertEqual(recovered["latest_run_label"], "run-b")
            self.assertEqual(recovered["latest_selected_score_pct"], 75.0)

            docker_row = rows_by_pair["task-alpha__analytic-pipeline"]
            self.assertEqual(docker_row["latest_status"], "docker_incident")
            self.assertEqual(docker_row["rerun_reason"], "docker_incident")

            other_row = rows_by_pair["task-beta__artifact-generation"]
            self.assertEqual(other_row["latest_status"], "failed_other")
            self.assertEqual(other_row["rerun_reason"], "missing_task_inputs")

            unrun_row = rows_by_pair["task-beta__analytic-pipeline"]
            self.assertEqual(unrun_row["latest_status"], "unrun")
            self.assertEqual(unrun_row["attempt_count"], 0)
            self.assertEqual(unrun_row["rerun_reason"], "unrun")

            markdown = self.module.render_markdown(
                generated_at=payload["generated_at"],
                skillsbench_root=skillsbench_root,
                report_rows=payload["reports"],
                pair_rows=payload["pairs"],
                schema_ids=payload["schema_ids"],
            )
            self.assertIn("task_count_detected: `2`", markdown)
            self.assertIn("| task-alpha | C2 | D1 |", markdown)
            self.assertIn("`task-beta__artifact-generation`", markdown)


if __name__ == "__main__":
    unittest.main()

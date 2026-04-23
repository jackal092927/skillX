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
    / "build_round0_outer_loop_artifacts.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("build_round0_outer_loop_artifacts", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BuildRound0OuterLoopArtifactsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def _write_run_report(
        self,
        reports_root: Path,
        *,
        run_label: str,
        pair_results: list[dict[str, object]],
    ) -> None:
        run_dir = reports_root / "reports" / run_label
        run_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "run_label": run_label,
            "pair_results": pair_results,
        }
        (run_dir / "run_report.json").write_text(json.dumps(payload))

    def test_build_outer_loop_artifacts_uses_latest_pair_attempt_and_emits_conservative_assignments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            round0_root = root / "outer-loop-round0"
            reports_root = round0_root / "slice-a"
            global_status_dir = round0_root / "reports" / "global-round0-status"
            global_status_dir.mkdir(parents=True)

            prompt_bank_path = root / "skillx-prompt-bank.json"
            prompt_bank_path.write_text(
                json.dumps(
                    {
                        "categories": [
                            {"category_id": "artifact-generation"},
                            {"category_id": "analytic-pipeline"},
                            {"category_id": "engineering-composition"},
                        ]
                    }
                )
            )

            self._write_run_report(
                reports_root,
                run_label="run-old",
                pair_results=[
                    {
                        "pair_id": "task-alpha__artifact-generation",
                        "task_name": "task-alpha",
                        "schema_id": "artifact-generation",
                        "selected": {"score_pct": 10.0},
                        "best_observed": {"score_pct": 10.0},
                        "official_scores": {"c0_pct": 0.0, "c1_pct": 5.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                        "failure": None,
                    }
                ],
            )
            self._write_run_report(
                reports_root,
                run_label="run-new",
                pair_results=[
                    {
                        "pair_id": "task-alpha__artifact-generation",
                        "task_name": "task-alpha",
                        "schema_id": "artifact-generation",
                        "selected": {"score_pct": 85.0},
                        "best_observed": {"score_pct": 85.0},
                        "official_scores": {"c0_pct": 50.0, "c1_pct": 55.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                        "failure": None,
                    },
                    {
                        "pair_id": "task-alpha__analytic-pipeline",
                        "task_name": "task-alpha",
                        "schema_id": "analytic-pipeline",
                        "selected": {"score_pct": 74.0},
                        "best_observed": {"score_pct": 74.0},
                        "official_scores": {"c0_pct": 50.0, "c1_pct": 60.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                        "failure": None,
                    },
                    {
                        "pair_id": "task-alpha__engineering-composition",
                        "task_name": "task-alpha",
                        "schema_id": "engineering-composition",
                        "selected": {"score_pct": 70.0},
                        "best_observed": {"score_pct": 70.0},
                        "official_scores": {"c0_pct": 50.0, "c1_pct": 60.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                        "failure": None,
                    },
                    {
                        "pair_id": "task-beta__artifact-generation",
                        "task_name": "task-beta",
                        "schema_id": "artifact-generation",
                        "selected": {"score_pct": 60.0},
                        "best_observed": {"score_pct": 60.0},
                        "official_scores": {"c0_pct": 10.0, "c1_pct": 20.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                        "failure": None,
                    },
                    {
                        "pair_id": "task-beta__analytic-pipeline",
                        "task_name": "task-beta",
                        "schema_id": "analytic-pipeline",
                        "selected": {"score_pct": 57.0},
                        "best_observed": {"score_pct": 57.0},
                        "official_scores": {"c0_pct": 10.0, "c1_pct": 20.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                        "failure": None,
                    },
                    {
                        "pair_id": "task-beta__engineering-composition",
                        "task_name": "task-beta",
                        "schema_id": "engineering-composition",
                        "selected": {"score_pct": 52.0},
                        "best_observed": {"score_pct": 52.0},
                        "official_scores": {"c0_pct": 10.0, "c1_pct": 20.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                        "failure": None,
                    },
                    {
                        "pair_id": "task-gamma__artifact-generation",
                        "task_name": "task-gamma",
                        "schema_id": "artifact-generation",
                        "selected": {"score_pct": 20.0},
                        "best_observed": {"score_pct": 20.0},
                        "official_scores": {"c0_pct": 0.0, "c1_pct": 5.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                        "failure": None,
                    },
                    {
                        "pair_id": "task-gamma__engineering-composition",
                        "task_name": "task-gamma",
                        "schema_id": "engineering-composition",
                        "selected": {"score_pct": 10.0},
                        "best_observed": {"score_pct": 10.0},
                        "official_scores": {"c0_pct": 0.0, "c1_pct": 5.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                        "failure": None,
                    },
                    {
                        "pair_id": "task-delta__artifact-generation",
                        "task_name": "task-delta",
                        "schema_id": "artifact-generation",
                        "selected": {"score_pct": 0.0},
                        "best_observed": {"score_pct": 0.0},
                        "official_scores": {"c0_pct": 10.0, "c1_pct": 10.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": True,
                        "failure": {"summary": "RuntimeError=['trial-123']", "error_type": "TuneExceptionStats"},
                    },
                    {
                        "pair_id": "task-delta__analytic-pipeline",
                        "task_name": "task-delta",
                        "schema_id": "analytic-pipeline",
                        "selected": {"score_pct": 5.0},
                        "best_observed": {"score_pct": 5.0},
                        "official_scores": {"c0_pct": 10.0, "c1_pct": 10.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                        "failure": None,
                    },
                    {
                        "pair_id": "task-delta__engineering-composition",
                        "task_name": "task-delta",
                        "schema_id": "engineering-composition",
                        "selected": {"score_pct": 15.0},
                        "best_observed": {"score_pct": 15.0},
                        "official_scores": {"c0_pct": 10.0, "c1_pct": 10.0},
                        "timeout_detected": False,
                        "has_intermediate_exceptions": False,
                        "failure": None,
                    },
                ],
            )

            global_pair_status = {
                "schema_ids": [
                    "artifact-generation",
                    "analytic-pipeline",
                    "engineering-composition",
                ],
                "pairs": [
                    {
                        "pair_id": "task-alpha__artifact-generation",
                        "task_name": "task-alpha",
                        "schema_id": "artifact-generation",
                        "latest_status": "completed",
                        "latest_status_code": "C",
                        "attempt_count": 2,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": 85.0,
                        "latest_best_observed_score_pct": 85.0,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": False,
                        "latest_failure_summary": "",
                    },
                    {
                        "pair_id": "task-alpha__analytic-pipeline",
                        "task_name": "task-alpha",
                        "schema_id": "analytic-pipeline",
                        "latest_status": "completed",
                        "latest_status_code": "C",
                        "attempt_count": 1,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": 74.0,
                        "latest_best_observed_score_pct": 74.0,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": False,
                        "latest_failure_summary": "",
                    },
                    {
                        "pair_id": "task-alpha__engineering-composition",
                        "task_name": "task-alpha",
                        "schema_id": "engineering-composition",
                        "latest_status": "completed",
                        "latest_status_code": "C",
                        "attempt_count": 1,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": 70.0,
                        "latest_best_observed_score_pct": 70.0,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": False,
                        "latest_failure_summary": "",
                    },
                    {
                        "pair_id": "task-beta__artifact-generation",
                        "task_name": "task-beta",
                        "schema_id": "artifact-generation",
                        "latest_status": "completed",
                        "latest_status_code": "C",
                        "attempt_count": 1,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": 60.0,
                        "latest_best_observed_score_pct": 60.0,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": False,
                        "latest_failure_summary": "",
                    },
                    {
                        "pair_id": "task-beta__analytic-pipeline",
                        "task_name": "task-beta",
                        "schema_id": "analytic-pipeline",
                        "latest_status": "completed",
                        "latest_status_code": "C",
                        "attempt_count": 1,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": 57.0,
                        "latest_best_observed_score_pct": 57.0,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": False,
                        "latest_failure_summary": "",
                    },
                    {
                        "pair_id": "task-beta__engineering-composition",
                        "task_name": "task-beta",
                        "schema_id": "engineering-composition",
                        "latest_status": "completed",
                        "latest_status_code": "C",
                        "attempt_count": 1,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": 52.0,
                        "latest_best_observed_score_pct": 52.0,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": False,
                        "latest_failure_summary": "",
                    },
                    {
                        "pair_id": "task-gamma__artifact-generation",
                        "task_name": "task-gamma",
                        "schema_id": "artifact-generation",
                        "latest_status": "completed",
                        "latest_status_code": "C",
                        "attempt_count": 1,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": 20.0,
                        "latest_best_observed_score_pct": 20.0,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": False,
                        "latest_failure_summary": "",
                    },
                    {
                        "pair_id": "task-gamma__analytic-pipeline",
                        "task_name": "task-gamma",
                        "schema_id": "analytic-pipeline",
                        "latest_status": "docker_incident",
                        "latest_status_code": "D",
                        "attempt_count": 1,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": None,
                        "latest_best_observed_score_pct": None,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": False,
                        "latest_failure_summary": "RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes",
                    },
                    {
                        "pair_id": "task-gamma__engineering-composition",
                        "task_name": "task-gamma",
                        "schema_id": "engineering-composition",
                        "latest_status": "completed",
                        "latest_status_code": "C",
                        "attempt_count": 1,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": 10.0,
                        "latest_best_observed_score_pct": 10.0,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": False,
                        "latest_failure_summary": "",
                    },
                    {
                        "pair_id": "task-delta__artifact-generation",
                        "task_name": "task-delta",
                        "schema_id": "artifact-generation",
                        "latest_status": "completed",
                        "latest_status_code": "C",
                        "attempt_count": 1,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": 0.0,
                        "latest_best_observed_score_pct": 0.0,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": True,
                        "latest_failure_summary": "RuntimeError=['trial-123']",
                    },
                    {
                        "pair_id": "task-delta__analytic-pipeline",
                        "task_name": "task-delta",
                        "schema_id": "analytic-pipeline",
                        "latest_status": "completed",
                        "latest_status_code": "C",
                        "attempt_count": 1,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": 5.0,
                        "latest_best_observed_score_pct": 5.0,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": False,
                        "latest_failure_summary": "",
                    },
                    {
                        "pair_id": "task-delta__engineering-composition",
                        "task_name": "task-delta",
                        "schema_id": "engineering-composition",
                        "latest_status": "completed",
                        "latest_status_code": "C",
                        "attempt_count": 1,
                        "latest_run_label": "run-new",
                        "latest_selected_score_pct": 15.0,
                        "latest_best_observed_score_pct": 15.0,
                        "latest_timeout_detected": False,
                        "latest_has_intermediate_exceptions": False,
                        "latest_failure_summary": "",
                    },
                ],
            }
            global_status_path = global_status_dir / "global_pair_status.json"
            global_status_path.write_text(json.dumps(global_pair_status))

            payload = self.module.build_outer_loop_artifacts(
                round0_root=round0_root,
                global_pair_status_path=global_status_path,
                prompt_bank_path=prompt_bank_path,
                round_id="round0-test",
                assignment_score_mode="trajectory",
                terminal_score_weight=0.50,
                round_mean_score_weight=0.30,
                growth_score_weight=0.20,
                epsilon_pp=5.0,
                high_confidence_margin_pp=10.0,
                medium_confidence_margin_pp=5.0,
                require_full_coverage=True,
                dominant_share_threshold=0.60,
                top3_tie_threshold_pp=10.0,
                near_empty_threshold=3,
                update_floor_fraction=0.10,
                flat_column_range_pp=10.0,
            )

            pair_rows_by_pair = {row["pair_id"]: row for row in payload["pair_rows"]}
            self.assertEqual(pair_rows_by_pair["task-alpha__artifact-generation"]["reported_score_pct"], 85.0)
            self.assertEqual(pair_rows_by_pair["task-gamma__analytic-pipeline"]["evidence_class"], "infra-blocked")
            self.assertEqual(pair_rows_by_pair["task-delta__artifact-generation"]["evidence_class"], "ambiguous")

            assignments_by_task = {row["task_name"]: row for row in payload["assignments"]}
            self.assertEqual(assignments_by_task["task-alpha"]["assigned_category"], "artifact-generation")
            self.assertEqual(assignments_by_task["task-alpha"]["assignment_confidence"], "high")
            self.assertEqual(assignments_by_task["task-beta"]["assigned_category"], "analytic-pipeline")
            self.assertTrue(assignments_by_task["task-beta"]["tie_break_used"])
            self.assertEqual(assignments_by_task["task-beta"]["tie_break_reason"], "balance")
            self.assertEqual(assignments_by_task["task-gamma"]["assignment_status"], "unassigned_incomplete_row")

            diagnostics = payload["diagnostics"]
            self.assertEqual(diagnostics["summary"]["assigned_task_count"], 3)
            self.assertEqual(diagnostics["summary"]["occupied_cluster_count"], 3)
            self.assertEqual(diagnostics["summary"]["cluster_sizes"]["engineering-composition"], 1)
            self.assertEqual(diagnostics["summary"]["task_count_partial_coverage"], 1)
            self.assertEqual(diagnostics["summary"]["task_count_full_coverage"], 3)
            self.assertEqual(len(diagnostics["low_margin_tasks"]), 1)
            self.assertEqual(diagnostics["low_margin_tasks"][0]["task_name"], "task-beta")
            self.assertEqual(len(diagnostics["top3_tied_tasks"]), 1)
            self.assertEqual(diagnostics["top3_tied_tasks"][0]["task_name"], "task-beta")
            schema_rows = {row["schema_id"]: row for row in diagnostics["schema_diagnostics"]}
            self.assertTrue(schema_rows["artifact-generation"]["below_update_floor"])
            self.assertIn("task-beta", schema_rows["artifact-generation"]["top_k_tasks_added"])

            with tempfile.TemporaryDirectory() as outdir:
                outputs = self.module.write_outer_loop_artifacts(
                    payload=payload,
                    output_dir=Path(outdir),
                )
                self.assertTrue((Path(outdir) / "score_matrix.csv").exists())
                self.assertTrue((Path(outdir) / "assignments.csv").exists())
                self.assertTrue((Path(outdir) / "diagnostics.json").exists())
                self.assertTrue((Path(outdir) / "summary.md").exists())
                self.assertIn("score_matrix_csv", outputs)

    def test_trajectory_score_uses_round_curves_to_break_final_score_ties(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            round0_root = root / "outer-loop-round0"
            reports_root = round0_root / "slice-a"
            global_status_dir = round0_root / "reports" / "global-round0-status"
            global_status_dir.mkdir(parents=True)

            schema_ids = [
                "artifact-generation",
                "analytic-pipeline",
                "engineering-composition",
            ]
            prompt_bank_path = root / "skillx-prompt-bank.json"
            prompt_bank_path.write_text(
                json.dumps({"categories": [{"category_id": schema_id} for schema_id in schema_ids]})
            )

            def pair_result(schema_id: str, round_scores: list[float]) -> dict[str, object]:
                return {
                    "pair_id": f"task-curve__{schema_id}",
                    "task_name": "task-curve",
                    "schema_id": schema_id,
                    "selected": {"score_pct": 80.0},
                    "best_observed": {"score_pct": 80.0},
                    "official_scores": {"c0_pct": 0.0, "c1_pct": 0.0},
                    "timeout_detected": False,
                    "has_intermediate_exceptions": False,
                    "failure": None,
                    "rounds": [
                        {"round_index": idx, "score_pct": score}
                        for idx, score in enumerate(round_scores)
                    ],
                }

            self._write_run_report(
                reports_root,
                run_label="run-curves",
                pair_results=[
                    pair_result("artifact-generation", [0.0, 20.0, 40.0, 80.0]),
                    pair_result("analytic-pipeline", [80.0, 80.0, 80.0, 80.0]),
                    pair_result("engineering-composition", [0.0, 80.0, 80.0, 80.0]),
                ],
            )

            global_status_path = global_status_dir / "global_pair_status.json"
            global_status_path.write_text(
                json.dumps(
                    {
                        "schema_ids": schema_ids,
                        "pairs": [
                            {
                                "pair_id": f"task-curve__{schema_id}",
                                "task_name": "task-curve",
                                "schema_id": schema_id,
                                "latest_status": "completed",
                                "latest_status_code": "C",
                                "attempt_count": 1,
                                "latest_run_label": "run-curves",
                                "latest_selected_score_pct": 80.0,
                                "latest_best_observed_score_pct": 80.0,
                                "latest_timeout_detected": False,
                                "latest_has_intermediate_exceptions": False,
                                "latest_failure_summary": "",
                            }
                            for schema_id in schema_ids
                        ],
                    }
                )
            )

            payload = self.module.build_outer_loop_artifacts(
                round0_root=round0_root,
                global_pair_status_path=global_status_path,
                prompt_bank_path=prompt_bank_path,
                round_id="round0-trajectory-test",
                assignment_score_mode="trajectory",
                terminal_score_weight=0.50,
                round_mean_score_weight=0.30,
                growth_score_weight=0.20,
                epsilon_pp=5.0,
                high_confidence_margin_pp=10.0,
                medium_confidence_margin_pp=5.0,
                require_full_coverage=True,
                dominant_share_threshold=0.60,
                top3_tie_threshold_pp=10.0,
                near_empty_threshold=3,
                update_floor_fraction=0.10,
                flat_column_range_pp=10.0,
            )

            rows_by_pair = {row["pair_id"]: row for row in payload["pair_rows"]}
            self.assertEqual(rows_by_pair["task-curve__analytic-pipeline"]["reported_score_pct"], 80.0)
            self.assertGreater(
                rows_by_pair["task-curve__engineering-composition"]["assignment_score_pct"],
                rows_by_pair["task-curve__analytic-pipeline"]["assignment_score_pct"],
            )
            assignments_by_task = {row["task_name"]: row for row in payload["assignments"]}
            self.assertEqual(assignments_by_task["task-curve"]["assigned_category"], "engineering-composition")
            self.assertEqual(assignments_by_task["task-curve"]["assigned_reported_score"], 80.0)


if __name__ == "__main__":
    unittest.main()

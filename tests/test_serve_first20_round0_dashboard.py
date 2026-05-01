from __future__ import annotations

import importlib.util
import json
import socket
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "serve_first20_round0_dashboard.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("serve_first20_round0_dashboard", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _make_checkpoint(root: Path) -> Path:
    checkpoint_dir = root / "checkpoint"
    checkpoint_dir.mkdir()
    _write_json(
        checkpoint_dir / "checkpoint_summary.json",
        {
            "checkpoint_label": "unit-first20",
            "generated_at": "2026-04-29T05:00:02+00:00",
            "task_count": 2,
            "schema_count": 2,
            "effective_pair_count": 4,
        },
    )
    _write_json(
        checkpoint_dir / "task_summary.json",
        [
            {
                "task_name": "task-a",
                "pair_count": 2,
                "c0_pct": 10.0,
                "c1_pct": 20.0,
                "best_score_pct": 80.0,
                "best_schemas": ["analytic-pipeline"],
                "delta_vs_c0_pp": 70.0,
                "delta_vs_c1_pp": 60.0,
            },
            {
                "task_name": "task-b",
                "pair_count": 2,
                "c0_pct": 50.0,
                "c1_pct": 80.0,
                "best_score_pct": 70.0,
                "best_schemas": ["artifact-generation"],
                "delta_vs_c0_pp": 20.0,
                "delta_vs_c1_pp": -10.0,
            },
        ],
    )
    _write_json(
        checkpoint_dir / "schema_summary.json",
        [
            {
                "schema_id": "analytic-pipeline",
                "pair_count": 2,
                "succeeded_pairs": 2,
                "clean_success": 1,
                "scientific_failure": 1,
                "runtime_failure": 0,
            },
            {
                "schema_id": "artifact-generation",
                "pair_count": 2,
                "succeeded_pairs": 2,
                "clean_success": 2,
                "scientific_failure": 0,
                "runtime_failure": 0,
            },
        ],
    )
    _write_json(
        checkpoint_dir / "final_pair_results.json",
        [
            {
                "pair_id": "task-a__analytic-pipeline",
                "task_name": "task-a",
                "schema_id": "analytic-pipeline",
                "round_r0_score_pct": 20.0,
                "round_r1_score_pct": 50.0,
                "round_r2_score_pct": 80.0,
                "round_r3_score_pct": 80.0,
                "post_r0_best_score_pct": 80.0,
                "selected_score_pct": 80.0,
                "selected_round": "R2",
                "delta_vs_r0_best_pp": 60.0,
                "delta_vs_c0_pp": 70.0,
                "delta_vs_c1_pp": 60.0,
                "trajectory_quality": "stable_non_decreasing_gain",
                "selected_classification": "clean_success",
            },
            {
                "pair_id": "task-a__artifact-generation",
                "task_name": "task-a",
                "schema_id": "artifact-generation",
                "round_r0_score_pct": 30.0,
                "round_r1_score_pct": 30.0,
                "round_r2_score_pct": 30.0,
                "round_r3_score_pct": 30.0,
                "post_r0_best_score_pct": 30.0,
                "selected_score_pct": 30.0,
                "selected_round": "R0",
                "delta_vs_r0_best_pp": 0.0,
                "delta_vs_c0_pp": 20.0,
                "delta_vs_c1_pp": 10.0,
                "trajectory_quality": "stable_no_loss",
                "selected_classification": "scientific_failure",
            },
            {
                "pair_id": "task-b__analytic-pipeline",
                "task_name": "task-b",
                "schema_id": "analytic-pipeline",
                "round_r0_score_pct": 60.0,
                "round_r1_score_pct": 40.0,
                "round_r2_score_pct": 40.0,
                "round_r3_score_pct": 40.0,
                "post_r0_best_score_pct": 40.0,
                "selected_score_pct": 40.0,
                "selected_round": "R0",
                "delta_vs_r0_best_pp": 0.0,
                "delta_vs_c0_pp": -10.0,
                "delta_vs_c1_pp": -40.0,
                "trajectory_quality": "regression_or_mixed",
                "selected_classification": "scientific_failure",
            },
            {
                "pair_id": "task-b__artifact-generation",
                "task_name": "task-b",
                "schema_id": "artifact-generation",
                "round_r0_score_pct": 20.0,
                "round_r1_score_pct": 70.0,
                "round_r2_score_pct": 70.0,
                "round_r3_score_pct": 70.0,
                "post_r0_best_score_pct": 70.0,
                "selected_score_pct": 70.0,
                "selected_round": "R1",
                "delta_vs_r0_best_pp": 50.0,
                "delta_vs_c0_pp": 20.0,
                "delta_vs_c1_pp": -10.0,
                "trajectory_quality": "non_monotonic_gain",
                "selected_classification": "clean_success",
            },
        ],
    )
    return checkpoint_dir


def _make_control_plane(root: Path) -> Path:
    control_plane_dir = root / "control-plane"
    control_plane_dir.mkdir()
    _write_json(
        control_plane_dir / "schema_training_assignments.json",
        {
            "generated_at": "2026-04-29T06:00:00+00:00",
            "config": {
                "min_schema_training_tasks": 2,
                "schema_floor_fraction": 0.1,
                "score_threshold": 70.0,
            },
            "schema_training_assignments": [
                {
                    "schema_id": "analytic-pipeline",
                    "task_name": "task-a",
                    "evidence_role": "primary_assignment",
                    "evidence_reasons": "primary;near_best;stable_gain",
                    "schema_score": 100.0,
                    "schema_reported_score": 100.0,
                    "schema_rank_for_task": 1,
                    "schema_delta_vs_r0_post_best_pp": 80.0,
                    "schema_trajectory_quality": "ideal_zero_to_full_stable",
                    "primary_assigned_category": "analytic-pipeline",
                    "task_best_schema": "analytic-pipeline",
                    "task_best_score": 100.0,
                },
                {
                    "schema_id": "artifact-generation",
                    "task_name": "task-b",
                    "evidence_role": "floor_top_score",
                    "evidence_reasons": "",
                    "schema_score": 31.25,
                    "schema_reported_score": 70.0,
                    "schema_rank_for_task": 4,
                    "schema_delta_vs_r0_post_best_pp": "",
                    "schema_trajectory_quality": "",
                    "primary_assigned_category": "analytic-pipeline",
                    "task_best_schema": "analytic-pipeline",
                    "task_best_score": 100.0,
                },
                {
                    "schema_id": "artifact-generation",
                    "task_name": "task-c",
                    "evidence_role": "stable_gain_support",
                    "evidence_reasons": "near_best;high_score;stable_gain",
                    "schema_score": 86.5,
                    "schema_reported_score": 90.0,
                    "schema_rank_for_task": 2,
                    "schema_delta_vs_r0_post_best_pp": 50.0,
                    "schema_trajectory_quality": "stable_non_decreasing_gain",
                    "primary_assigned_category": "engineering-composition",
                    "task_best_schema": "engineering-composition",
                    "task_best_score": 90.0,
                },
            ],
        },
    )
    return control_plane_dir


class ServeFirst20Round0DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_build_dashboard_payload_aggregates_trajectories_and_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = _make_checkpoint(Path(tmpdir))
            payload = self.module.build_dashboard_payload(checkpoint_dir)

        self.assertEqual(payload["summary_metrics"]["task_count"], 2)
        self.assertEqual(payload["summary_metrics"]["schema_count"], 2)
        self.assertEqual(payload["summary_metrics"]["pair_count"], 4)
        self.assertEqual(payload["delta_overview"]["vs_r0"]["positive"], 2)
        self.assertEqual(payload["delta_overview"]["vs_c1"]["negative"], 2)
        analytic = next(
            item
            for item in payload["schema_cards"]
            if item["schema_id"] == "analytic-pipeline"
        )
        self.assertEqual(analytic["trajectory"]["R0"], 40.0)
        self.assertEqual(analytic["trajectory"]["R2"], 60.0)
        self.assertEqual(analytic["deltas"]["vs_c1"], 10.0)
        self.assertEqual(payload["matrix_rows"][0]["cells"][0]["pair_id"], "task-a__analytic-pipeline")
        self.assertEqual(payload["best_task_delta_overview"]["positive"], 2)
        task_b = next(
            item
            for item in payload["best_task_rows"]
            if item["task_name"] == "task-b"
        )
        self.assertEqual(task_b["schema_id"], "artifact-generation")
        self.assertEqual(task_b["round_scores"]["R1"], 70.0)
        self.assertEqual(task_b["round_deltas_vs_r0"]["R1"], 50.0)
        self.assertEqual(task_b["best_delta_vs_r0_pp"], 50.0)

    def test_render_dashboard_html_contains_requested_views(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = _make_checkpoint(Path(tmpdir))
            payload = self.module.build_dashboard_payload(checkpoint_dir)
            html = self.module.render_dashboard_html(payload)

        self.assertIn("Best-Schema Task Curves", html)
        self.assertIn("Best-Schema R0 Trajectories", html)
        self.assertIn("R1 / dR0", html)
        self.assertIn("dBest vs R0", html)
        self.assertIn("dFinal vs R0", html)
        self.assertIn("task-a", html)
        self.assertIn("focus-spark", html)
        self.assertIn("/api/dashboard", html)
        self.assertIn("/training-evidence", html)

    def test_build_training_evidence_payload_describes_rows_and_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            control_plane_dir = _make_control_plane(Path(tmpdir))
            payload = self.module.build_training_evidence_payload(control_plane_dir)

        self.assertEqual(payload["summary_metrics"]["row_count"], 3)
        self.assertEqual(payload["summary_metrics"]["schema_count"], 2)
        self.assertEqual(payload["summary_metrics"]["floor_count"], 1)
        self.assertEqual(payload["role_counts"]["primary_assignment"], 1)
        artifact = next(
            item
            for item in payload["schema_summary"]
            if item["schema_id"] == "artifact-generation"
        )
        self.assertEqual(artifact["evidence_count"], 2)
        self.assertEqual(artifact["floor_top_score"], 1)
        self.assertEqual(payload["rows"][0]["schema_id"], "analytic-pipeline")
        self.assertEqual(payload["rows"][1]["evidence_role"], "stable_gain_support")
        self.assertIn("schema_score", [column["key"] for column in payload["columns"]])

    def test_render_training_evidence_html_contains_table_and_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            control_plane_dir = _make_control_plane(Path(tmpdir))
            payload = self.module.build_training_evidence_payload(control_plane_dir)
            html = self.module.render_training_evidence_html(payload)

        self.assertIn("Schema Training Evidence", html)
        self.assertIn("Evidence Table", html)
        self.assertIn("Column Definitions", html)
        self.assertIn("Assignment Score", html)
        self.assertIn("floor_top_score", html)
        self.assertIn("schema_score", html)
        self.assertIn("/", html)

    def test_http_server_serves_dashboard_and_api(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = _make_checkpoint(Path(tmpdir))
            control_plane_dir = _make_control_plane(Path(tmpdir))
            port = _free_port()
            server = self.module.build_server(
                checkpoint_dir=checkpoint_dir,
                control_plane_dir=control_plane_dir,
                host="127.0.0.1",
                port=port,
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                html = urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5).read().decode("utf-8")
                payload = json.loads(
                    urllib.request.urlopen(f"http://127.0.0.1:{port}/api/dashboard", timeout=5).read().decode("utf-8")
                )
                training_html = urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/training-evidence", timeout=5
                ).read().decode("utf-8")
                training_payload = json.loads(
                    urllib.request.urlopen(
                        f"http://127.0.0.1:{port}/api/training-evidence", timeout=5
                    ).read().decode("utf-8")
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertIn("Best-Schema Task Curves", html)
        self.assertEqual(payload["summary_metrics"]["pair_count"], 4)
        self.assertEqual(payload["summary_metrics"]["best_task_improved_count"], 2)
        self.assertEqual(payload["schemas"], ["analytic-pipeline", "artifact-generation"])
        self.assertIn("Schema Training Evidence", training_html)
        self.assertEqual(training_payload["summary_metrics"]["row_count"], 3)
        self.assertEqual(training_payload["summary_metrics"]["floor_count"], 1)


if __name__ == "__main__":
    unittest.main()

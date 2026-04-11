from __future__ import annotations

import importlib.util
import json
import os
import socket
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from unittest import mock


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "serve_round0_monitor.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("serve_round0_monitor", SCRIPT_PATH)
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


class ServeRound0MonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_collect_launcher_status_uses_stdout_and_events_before_summary_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_log_dir = Path(tmpdir) / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "\n".join(
                    [
                        "Selected 3 task(s) -> 21 pair(s)",
                        "Tasks: civ6-adjacency-optimizer, earthquake-phase-association, energy-ac-optimal-power-flow",
                        "Launcher logs: /tmp/demo",
                        "[1/21] civ6-adjacency-optimizer__artifact-generation",
                    ]
                )
                + "\n"
            )
            (launcher_log_dir / "events.ndjson").write_text(
                json.dumps(
                    {
                        "event": "pair_started",
                        "index": 1,
                        "observed_at": "2026-04-10T07:56:04+00:00",
                        "pair_id": "civ6-adjacency-optimizer__artifact-generation",
                        "schema_id": "artifact-generation",
                        "task_name": "civ6-adjacency-optimizer",
                    }
                )
                + "\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:00:00+00:00",
            )

            self.assertEqual(status["run_label"], "run-demo")
            self.assertEqual(status["total_pairs"], 21)
            self.assertEqual(status["completed_pairs"], 0)
            self.assertEqual(status["succeeded_pairs"], 0)
            self.assertEqual(status["failed_pairs"], 0)
            self.assertEqual(status["selected_task_names"][0], "civ6-adjacency-optimizer")
            self.assertEqual(status["current_pair_id"], "civ6-adjacency-optimizer__artifact-generation")
            self.assertEqual(status["current_pair_index"], 1)
            self.assertEqual(status["health"], "running")
            self.assertFalse(status["summary_exists"])

    def test_collect_launcher_status_includes_current_round_and_role_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            materialized_root = Path(tmpdir)
            launcher_log_dir = materialized_root / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            active_run_dir = (
                materialized_root
                / "pairs"
                / "civ6-adjacency-optimizer__artifact-generation"
                / "refine_run_run-demo"
            )
            round0 = active_run_dir / "refine" / "civ6-adjacency-optimizer" / "rounds" / "round-0"
            round1 = active_run_dir / "refine" / "civ6-adjacency-optimizer" / "rounds" / "round-1"
            round0.mkdir(parents=True)
            round1.mkdir(parents=True)
            (active_run_dir / "RUN_STATUS.md").write_text("- status: `running`\n- task: `civ6-adjacency-optimizer`\n")
            (round0 / "orchestrator_log.ndjson").write_text(
                "\n".join(
                    [
                        json.dumps({"round_index": 0, "event_type": "round_started", "status": "ok", "timestamp": "2026-04-10T08:00:00+00:00"}),
                        json.dumps({"round_index": 0, "event_type": "executor_completed", "status": "ok", "timestamp": "2026-04-10T08:01:00+00:00"}),
                        json.dumps({"round_index": 0, "event_type": "role_a_completed", "status": "ok", "timestamp": "2026-04-10T08:02:00+00:00"}),
                        json.dumps({"round_index": 0, "event_type": "role_b_completed", "status": "ok", "timestamp": "2026-04-10T08:03:00+00:00"}),
                        json.dumps({"round_index": 0, "event_type": "round_decision_loaded", "status": "continue", "timestamp": "2026-04-10T08:03:01+00:00"}),
                    ]
                )
                + "\n"
            )
            (round1 / "orchestrator_log.ndjson").write_text(
                json.dumps(
                    {
                        "round_index": 1,
                        "event_type": "round_started",
                        "status": "ok",
                        "timestamp": "2026-04-10T08:04:00+00:00",
                    }
                )
                + "\n"
            )
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 1 task(s) -> 7 pair(s)\n"
                "Tasks: civ6-adjacency-optimizer\n"
            )
            (launcher_log_dir / "events.ndjson").write_text(
                json.dumps(
                    {
                        "event": "pair_started",
                        "index": 1,
                        "observed_at": "2026-04-10T07:56:04+00:00",
                        "pair_id": "civ6-adjacency-optimizer__artifact-generation",
                        "schema_id": "artifact-generation",
                        "task_name": "civ6-adjacency-optimizer",
                    }
                )
                + "\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:04:30+00:00",
            )

            pair_detail = status["pair_detail"]
            self.assertEqual(pair_detail["task_id"], "civ6-adjacency-optimizer")
            self.assertEqual(pair_detail["current_round_index"], 1)
            self.assertEqual(pair_detail["current_stage"], "executor")
            self.assertEqual(pair_detail["last_completed_stage"], "role_b")
            self.assertEqual(pair_detail["round_rows"][0]["stage_states"]["role_b"], "completed")
            self.assertEqual(pair_detail["round_rows"][1]["stage_states"]["executor"], "running")
            self.assertEqual(pair_detail["round_rows"][1]["stage_states"]["role_a"], "pending")
            self.assertEqual(pair_detail["round_rows"][1]["stage_states"]["role_b"], "pending")

    def test_collect_launcher_status_prefers_summary_counts_after_pairs_finish(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_log_dir = Path(tmpdir) / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 3 task(s) -> 21 pair(s)\n"
                "Tasks: civ6-adjacency-optimizer, earthquake-phase-association, energy-ac-optimal-power-flow\n"
            )
            (launcher_log_dir / "events.ndjson").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "event": "pair_started",
                                "index": 1,
                                "observed_at": "2026-04-10T07:56:04+00:00",
                                "pair_id": "civ6-adjacency-optimizer__artifact-generation",
                                "schema_id": "artifact-generation",
                                "task_name": "civ6-adjacency-optimizer",
                            }
                        ),
                        json.dumps(
                            {
                                "event": "pair_succeeded",
                                "index": 1,
                                "observed_at": "2026-04-10T08:10:00+00:00",
                                "pair_id": "civ6-adjacency-optimizer__artifact-generation",
                                "schema_id": "artifact-generation",
                                "task_name": "civ6-adjacency-optimizer",
                                "returncode": 0,
                            }
                        ),
                    ]
                )
                + "\n"
            )
            (launcher_log_dir / "summary.json").write_text(
                json.dumps(
                    {
                        "selected_task_names": [
                            "civ6-adjacency-optimizer",
                            "earthquake-phase-association",
                            "energy-ac-optimal-power-flow",
                        ],
                        "total_pairs": 21,
                        "completed_pairs": 7,
                        "succeeded_pairs": 6,
                        "failed_pairs": 1,
                        "results": [
                            {
                                "pair_id": "civ6-adjacency-optimizer__artifact-generation",
                                "status": "succeeded",
                                "returncode": 0,
                            },
                            {
                                "pair_id": "civ6-adjacency-optimizer__analytic-pipeline",
                                "status": "failed",
                                "returncode": 17,
                                "error": "subprocess exited with code 17",
                            },
                        ],
                    }
                )
                + "\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:10:05+00:00",
            )

            self.assertTrue(status["summary_exists"])
            self.assertEqual(status["completed_pairs"], 7)
            self.assertEqual(status["succeeded_pairs"], 6)
            self.assertEqual(status["failed_pairs"], 1)
            self.assertEqual(status["health"], "running")
            self.assertEqual(status["progress_percent"], 100.0 * 7 / 21)
            self.assertEqual(status["last_failure"]["pair_id"], "civ6-adjacency-optimizer__analytic-pipeline")

    def test_collect_launcher_status_builds_pair_result_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            materialized_root = Path(tmpdir)
            launcher_log_dir = materialized_root / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            (materialized_root / "manifest.json").write_text(
                json.dumps({"schema_ids": ["artifact-generation", "analytic-pipeline"]}) + "\n"
            )
            pair_specs = [
                {
                    "pair_id": "task-alpha__artifact-generation",
                    "task_name": "task-alpha",
                    "schema_id": "artifact-generation",
                    "pair_dir": str(materialized_root / "pairs" / "task-alpha__artifact-generation"),
                    "official_scores": {"no_skills": 10.0, "with_skills": 20.0},
                },
                {
                    "pair_id": "task-alpha__analytic-pipeline",
                    "task_name": "task-alpha",
                    "schema_id": "analytic-pipeline",
                    "pair_dir": str(materialized_root / "pairs" / "task-alpha__analytic-pipeline"),
                    "official_scores": {"no_skills": 10.0, "with_skills": 20.0},
                },
            ]
            (materialized_root / "pair_specs.jsonl").write_text(
                "\n".join(json.dumps(item) for item in pair_specs) + "\n"
            )
            completed_run = materialized_root / "pairs" / "task-alpha__artifact-generation" / "refine_run_run-demo"
            task_root = completed_run / "refine" / "task-alpha"
            (task_root / "rounds" / "round-0" / "tune_check").mkdir(parents=True)
            (task_root / "rounds" / "round-1" / "tune_check").mkdir(parents=True)
            (task_root / "rounds" / "round-0" / "tune_check" / "result.json").write_text(
                json.dumps({"reward": 0.21}) + "\n"
            )
            (task_root / "rounds" / "round-1" / "tune_check" / "result.json").write_text(
                json.dumps({"reward": 0.26}) + "\n"
            )
            (task_root / "refine_summary.json").write_text(
                json.dumps(
                    {
                        "task_id": "task-alpha",
                        "selected": {"round_index": 1, "reward": 0.26},
                        "rounds": [
                            {"round_index": 0, "reward": 0.21},
                            {"round_index": 1, "reward": 0.26},
                        ],
                    }
                )
                + "\n"
            )
            (completed_run / "RUN_STATUS.md").write_text("- status: `completed`\n")

            running_run = materialized_root / "pairs" / "task-alpha__analytic-pipeline" / "refine_run_run-demo"
            running_task_root = running_run / "refine" / "task-alpha"
            (running_task_root / "rounds" / "round-0" / "tune_check").mkdir(parents=True)
            (running_task_root / "rounds" / "round-0" / "tune_check" / "result.json").write_text(
                json.dumps({"reward": 0.225}) + "\n"
            )
            (running_run / "RUN_STATUS.md").write_text("- status: `running`\n")

            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 1 task(s) -> 2 pair(s)\n"
                "Tasks: task-alpha\n"
            )
            (launcher_log_dir / "events.ndjson").write_text("")
            (launcher_log_dir / "summary.json").write_text(
                json.dumps(
                    {
                        "selected_task_names": ["task-alpha"],
                        "total_pairs": 2,
                        "completed_pairs": 1,
                        "succeeded_pairs": 1,
                        "failed_pairs": 0,
                        "results": [
                            {
                                "pair_id": "task-alpha__artifact-generation",
                                "status": "succeeded",
                                "returncode": 0,
                            }
                        ],
                    }
                )
                + "\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:10:05+00:00",
            )

            pair_rows = status["pair_rows"]
            self.assertEqual(len(pair_rows), 2)
            completed = pair_rows[0]
            running = pair_rows[1]
            self.assertEqual(completed["task_name"], "task-alpha")
            self.assertEqual(completed["schema_id"], "artifact-generation")
            self.assertEqual(completed["official_c0"], 10.0)
            self.assertEqual(completed["official_c1"], 20.0)
            self.assertEqual(completed["round_rewards_raw"]["R0"], 0.21)
            self.assertEqual(completed["round_scores"]["R0"], 21.0)
            self.assertEqual(completed["round_scores"]["R1"], 26.0)
            self.assertEqual(completed["selected_round"], "R1")
            self.assertEqual(completed["selected_score"], 26.0)
            self.assertEqual(completed["selected_score_raw"], 0.26)
            self.assertEqual(completed["delta_vs_c0"], 16.0)
            self.assertEqual(completed["delta_vs_c1"], 6.0)
            self.assertEqual(completed["pair_status"], "completed")
            self.assertEqual(running["schema_id"], "analytic-pipeline")
            self.assertEqual(running["round_scores"]["R0"], 22.5)
            self.assertEqual(running["round_rewards_raw"]["R0"], 0.225)
            self.assertIsNone(running["selected_round"])
            self.assertEqual(running["pair_status"], "running")

    def test_collect_launcher_status_marks_completed_stop_pairs_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            materialized_root = Path(tmpdir)
            launcher_log_dir = materialized_root / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            (materialized_root / "manifest.json").write_text(
                json.dumps({"schema_ids": ["artifact-generation"]}) + "\n"
            )
            pair_dir = materialized_root / "pairs" / "task-alpha__artifact-generation"
            pair_dir.mkdir(parents=True)
            (materialized_root / "pair_specs.jsonl").write_text(
                json.dumps(
                    {
                        "pair_id": "task-alpha__artifact-generation",
                        "task_name": "task-alpha",
                        "schema_id": "artifact-generation",
                        "pair_dir": str(pair_dir),
                        "official_scores": {"no_skills": 10.0, "with_skills": 20.0},
                    }
                )
                + "\n"
            )
            run_dir = pair_dir / "refine_run_run-demo"
            round0 = run_dir / "refine" / "task-alpha" / "rounds" / "round-0"
            round1 = run_dir / "refine" / "task-alpha" / "rounds" / "round-1"
            (round0 / "tune_check").mkdir(parents=True)
            (round1 / "tune_check").mkdir(parents=True)
            (round0 / "tune_check" / "result.json").write_text(json.dumps({"reward": 0.21}) + "\n")
            (round1 / "tune_check" / "result.json").write_text(json.dumps({"reward": 0.18}) + "\n")
            (round1 / "orchestrator_log.ndjson").write_text(
                "\n".join(
                    [
                        json.dumps({"round_index": 1, "event_type": "round_started", "status": "ok"}),
                        json.dumps({"round_index": 1, "event_type": "executor_completed", "status": "ok"}),
                        json.dumps({"round_index": 1, "event_type": "role_a_completed", "status": "ok"}),
                        json.dumps({"round_index": 1, "event_type": "role_b_completed", "status": "ok"}),
                        json.dumps({"round_index": 1, "event_type": "round_decision_loaded", "status": "stop"}),
                    ]
                )
                + "\n"
            )
            (run_dir / "RUN_STATUS.md").write_text(
                "- status: `completed`\n"
                "- round_budget: `3`\n"
            )
            (launcher_log_dir / "summary.json").write_text(
                json.dumps(
                    {
                        "selected_task_names": ["task-alpha"],
                        "total_pairs": 1,
                        "completed_pairs": 1,
                        "succeeded_pairs": 1,
                        "failed_pairs": 0,
                        "results": [
                            {
                                "pair_id": "task-alpha__artifact-generation",
                                "status": "succeeded",
                                "returncode": 0,
                                "output_dir": str(run_dir),
                            }
                        ],
                    }
                )
                + "\n"
            )
            (launcher_log_dir / "events.ndjson").write_text(
                json.dumps(
                    {
                        "event": "pair_succeeded",
                        "index": 1,
                        "observed_at": "2026-04-10T08:10:00+00:00",
                        "pair_id": "task-alpha__artifact-generation",
                        "schema_id": "artifact-generation",
                        "task_name": "task-alpha",
                        "returncode": 0,
                    }
                )
                + "\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:10:05+00:00",
            )

            self.assertEqual(status["pair_rows"][0]["pair_status"], "completed (stop@R1)")

    def test_collect_launcher_status_uses_pair_rows_total_when_summary_total_is_partial_and_stdout_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            materialized_root = Path(tmpdir)
            launcher_log_dir = materialized_root / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            (materialized_root / "manifest.json").write_text(
                json.dumps({"schema_ids": ["artifact-generation", "analytic-pipeline"]}) + "\n"
            )
            pair_specs = [
                {
                    "pair_id": "task-alpha__artifact-generation",
                    "task_name": "task-alpha",
                    "schema_id": "artifact-generation",
                    "pair_dir": str(materialized_root / "pairs" / "task-alpha__artifact-generation"),
                    "official_scores": {"no_skills": 10.0, "with_skills": 20.0},
                },
                {
                    "pair_id": "task-alpha__analytic-pipeline",
                    "task_name": "task-alpha",
                    "schema_id": "analytic-pipeline",
                    "pair_dir": str(materialized_root / "pairs" / "task-alpha__analytic-pipeline"),
                    "official_scores": {"no_skills": 10.0, "with_skills": 20.0},
                },
            ]
            (materialized_root / "pair_specs.jsonl").write_text(
                "\n".join(json.dumps(item) for item in pair_specs) + "\n"
            )
            completed_run = materialized_root / "pairs" / "task-alpha__artifact-generation" / "refine_run_run-demo"
            completed_run.mkdir(parents=True)
            (completed_run / "RUN_STATUS.md").write_text("- status: `completed`\n")
            (completed_run / "refine" / "task-alpha" / "rounds" / "round-0" / "tune_check").mkdir(parents=True)
            (
                completed_run
                / "refine"
                / "task-alpha"
                / "rounds"
                / "round-0"
                / "tune_check"
                / "result.json"
            ).write_text(json.dumps({"reward": 0.21}) + "\n")
            running_run = materialized_root / "pairs" / "task-alpha__analytic-pipeline" / "refine_run_run-demo"
            running_run.mkdir(parents=True)
            (running_run / "RUN_STATUS.md").write_text("- status: `running`\n")

            (launcher_log_dir / "events.ndjson").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "event": "pair_succeeded",
                                "index": 1,
                                "observed_at": "2026-04-10T08:10:00+00:00",
                                "pair_id": "task-alpha__artifact-generation",
                                "schema_id": "artifact-generation",
                                "task_name": "task-alpha",
                                "returncode": 0,
                            }
                        ),
                        json.dumps(
                            {
                                "event": "pair_started",
                                "index": 2,
                                "observed_at": "2026-04-10T08:11:00+00:00",
                                "pair_id": "task-alpha__analytic-pipeline",
                                "schema_id": "analytic-pipeline",
                                "task_name": "task-alpha",
                            }
                        ),
                    ]
                )
                + "\n"
            )
            (launcher_log_dir / "summary.json").write_text(
                json.dumps(
                    {
                        "selected_task_names": ["task-alpha"],
                        "total_pairs": 1,
                        "completed_pairs": 1,
                        "succeeded_pairs": 1,
                        "failed_pairs": 0,
                        "results": [
                            {
                                "pair_id": "task-alpha__artifact-generation",
                                "status": "succeeded",
                                "returncode": 0,
                            }
                        ],
                    }
                )
                + "\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:11:05+00:00",
            )

            self.assertEqual(status["total_pairs"], 2)
            self.assertEqual(status["completed_pairs"], 1)
            self.assertEqual(status["progress_percent"], 50.0)

    def test_collect_launcher_status_uses_stdout_total_when_summary_total_is_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_log_dir = Path(tmpdir) / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "\n".join(
                    [
                        "Selected 3 task(s) -> 21 pair(s)",
                        "Tasks: civ6-adjacency-optimizer, earthquake-phase-association, energy-ac-optimal-power-flow",
                        "Launcher logs: /tmp/demo",
                        "[1/21] civ6-adjacency-optimizer__artifact-generation",
                        "  OK",
                        "[2/21] civ6-adjacency-optimizer__analytic-pipeline",
                    ]
                )
                + "\n"
            )
            (launcher_log_dir / "events.ndjson").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "event": "pair_started",
                                "index": 1,
                                "observed_at": "2026-04-10T07:56:04+00:00",
                                "pair_id": "civ6-adjacency-optimizer__artifact-generation",
                                "schema_id": "artifact-generation",
                                "task_name": "civ6-adjacency-optimizer",
                            }
                        ),
                        json.dumps(
                            {
                                "event": "pair_succeeded",
                                "index": 1,
                                "observed_at": "2026-04-10T09:05:26+00:00",
                                "pair_id": "civ6-adjacency-optimizer__artifact-generation",
                                "schema_id": "artifact-generation",
                                "task_name": "civ6-adjacency-optimizer",
                                "returncode": 0,
                            }
                        ),
                        json.dumps(
                            {
                                "event": "pair_started",
                                "index": 2,
                                "observed_at": "2026-04-10T09:05:26+00:00",
                                "pair_id": "civ6-adjacency-optimizer__analytic-pipeline",
                                "schema_id": "analytic-pipeline",
                                "task_name": "civ6-adjacency-optimizer",
                            }
                        ),
                    ]
                )
                + "\n"
            )
            (launcher_log_dir / "summary.json").write_text(
                json.dumps(
                    {
                        "selected_task_names": [
                            "civ6-adjacency-optimizer",
                            "earthquake-phase-association",
                            "energy-ac-optimal-power-flow",
                        ],
                        "total_pairs": 1,
                        "completed_pairs": 1,
                        "succeeded_pairs": 1,
                        "failed_pairs": 0,
                        "results": [
                            {
                                "pair_id": "civ6-adjacency-optimizer__artifact-generation",
                                "status": "succeeded",
                                "returncode": 0,
                            }
                        ],
                    }
                )
                + "\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T09:10:00+00:00",
            )

            self.assertEqual(status["total_pairs"], 21)
            self.assertEqual(status["completed_pairs"], 1)
            self.assertEqual(status["progress_percent"], 100.0 / 21.0)
            self.assertEqual(status["health"], "running")
            self.assertEqual(status["current_pair_id"], "civ6-adjacency-optimizer__analytic-pipeline")

    def test_collect_launcher_status_uses_active_process_output_dir_when_pair_dir_is_external(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_log_dir = Path(tmpdir) / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            external_run_dir = Path(tmpdir) / "external" / "refine_run_run-demo"
            external_run_dir.mkdir(parents=True)
            (external_run_dir / "RUN_STATUS.md").write_text("- status: `running`\n")
            fresh_ts = 1775813395
            os.utime(external_run_dir / "RUN_STATUS.md", (fresh_ts, fresh_ts))
            os.utime(external_run_dir, (fresh_ts, fresh_ts))
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 1 task(s) -> 7 pair(s)\n"
                "Tasks: civ6-adjacency-optimizer\n"
            )
            (launcher_log_dir / "events.ndjson").write_text(
                json.dumps(
                    {
                        "event": "pair_started",
                        "index": 1,
                        "observed_at": "2026-04-10T07:56:04+00:00",
                        "pair_id": "civ6-adjacency-optimizer__artifact-generation",
                        "schema_id": "artifact-generation",
                        "task_name": "civ6-adjacency-optimizer",
                    }
                )
                + "\n"
            )
            process_line = (
                "python scripts/run_skillx_refine_benchmark.py "
                "--run-id civ6-adjacency-optimizer__artifact-generation__run-demo "
                f"--output-dir {external_run_dir}"
            )

            with mock.patch.object(
                self.module.subprocess,
                "run",
                return_value=mock.Mock(returncode=0, stdout=process_line + "\n"),
            ):
                status = self.module.collect_launcher_status(
                    launcher_log_dir,
                    now="2026-04-10T08:30:00+00:00",
                    stale_seconds=60,
                )

            self.assertEqual(status["health"], "running")
            self.assertEqual(status["active_run_dir"], str(external_run_dir.resolve()))
            self.assertEqual(status["active_run_status"]["status"], "running")

    def test_http_server_serves_json_and_auto_refresh_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_log_dir = Path(tmpdir) / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            active_run_dir = (
                Path(tmpdir)
                / "pairs"
                / "civ6-adjacency-optimizer__artifact-generation"
                / "refine_run_run-demo"
            )
            active_run_dir.mkdir(parents=True)
            (active_run_dir / "RUN_STATUS.md").write_text("- status: `running`\n")
            round1 = active_run_dir / "refine" / "civ6-adjacency-optimizer" / "rounds" / "round-1"
            round1.mkdir(parents=True)
            (round1 / "orchestrator_log.ndjson").write_text(
                json.dumps(
                    {
                        "round_index": 1,
                        "event_type": "round_started",
                        "status": "ok",
                        "timestamp": "2026-04-10T07:56:05+00:00",
                    }
                )
                + "\n"
            )
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 1 task(s) -> 7 pair(s)\n"
                "Tasks: civ6-adjacency-optimizer\n"
            )
            (launcher_log_dir / "events.ndjson").write_text(
                json.dumps(
                    {
                        "event": "pair_started",
                        "index": 1,
                        "observed_at": "2026-04-10T07:56:04+00:00",
                        "pair_id": "civ6-adjacency-optimizer__artifact-generation",
                        "schema_id": "artifact-generation",
                        "task_name": "civ6-adjacency-optimizer",
                    }
                )
                + "\n"
            )

            port = _free_port()
            server = self.module.build_server(
                launcher_log_dir=launcher_log_dir,
                host="127.0.0.1",
                port=port,
                refresh_seconds=9,
                stale_seconds=600,
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                html = urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5).read().decode("utf-8")
                payload = json.loads(
                    urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status", timeout=5).read().decode("utf-8")
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

            self.assertIn('<meta http-equiv="refresh" content="9">', html)
            self.assertIn("civ6-adjacency-optimizer__artifact-generation", html)
            self.assertIn("Current Pair Detail", html)
            self.assertIn("Current round", html)
            self.assertIn("executor", html)
            self.assertIn("Task / Pair Results", html)
            self.assertIn("0-100 scale", html)
            self.assertEqual(payload["total_pairs"], 7)
            self.assertEqual(payload["health"], "running")
            self.assertEqual(payload["pair_detail"]["current_round_index"], 1)


if __name__ == "__main__":
    unittest.main()

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

    def test_collect_launcher_status_surfaces_rate_limit_retry_archives(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            materialized_root = Path(tmpdir)
            launcher_log_dir = materialized_root / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            (materialized_root / "manifest.json").write_text(
                json.dumps({"schema_ids": ["artifact-generation"]}) + "\n"
            )
            pair_dir = materialized_root / "pairs" / "task-alpha__artifact-generation"
            run_dir = pair_dir / "refine_run_run-demo"
            round0 = run_dir / "refine" / "task-alpha" / "rounds" / "round-0"
            round0.mkdir(parents=True)
            (run_dir / "RUN_STATUS.md").write_text("- status: `running`\n- task: `task-alpha`\n")
            (round0 / "orchestrator_log.ndjson").write_text(
                json.dumps({"round_index": 0, "event_type": "round_started", "timestamp": "2026-04-10T08:00:00+00:00"})
                + "\n"
            )
            archive_dir = run_dir / "archives" / "rate-limit-fallback-20260410T081500Z"
            (archive_dir / "rounds" / "round-0" / "tune_check").mkdir(parents=True)
            (archive_dir / "rounds" / "round-1" / "tune_check").mkdir(parents=True)
            (archive_dir / "RUN_STATUS.md").write_text("- status: `completed_with_quota_issues`\n")
            (archive_dir / "rate_limit_signal.json").write_text(
                json.dumps({"signal_level": "hard", "hard_terms": ["api_error_status_429"]}) + "\n"
            )
            (archive_dir / "refine_summary.json").write_text(
                json.dumps({"selected": {"round_index": 1, "reward": 0.42}}) + "\n"
            )
            (materialized_root / "pair_specs.jsonl").write_text(
                json.dumps(
                    {
                        "pair_id": "task-alpha__artifact-generation",
                        "task_name": "task-alpha",
                        "schema_id": "artifact-generation",
                        "pair_dir": str(pair_dir),
                    }
                )
                + "\n"
            )
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 1 task(s) -> 1 pair(s)\n"
                "Tasks: task-alpha\n"
            )
            (launcher_log_dir / "events.ndjson").write_text(
                json.dumps(
                    {
                        "event": "pair_started",
                        "index": 1,
                        "observed_at": "2026-04-10T07:56:04+00:00",
                        "pair_id": "task-alpha__artifact-generation",
                        "schema_id": "artifact-generation",
                        "task_name": "task-alpha",
                    }
                )
                + "\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:16:00+00:00",
            )

            self.assertEqual(status["archived_retry_count"], 1)
            self.assertEqual(status["pair_rows"][0]["archive_count"], 1)
            self.assertEqual(status["pair_rows"][0]["latest_archive_rounds"], [0, 1])
            archive = status["active_pair_details"][0]["retry_archives"][0]
            self.assertEqual(archive["status"], "completed_with_quota_issues")
            self.assertEqual(archive["hard_terms"], ["api_error_status_429"])
            self.assertEqual(archive["selected_round"], 1)
            self.assertEqual(archive["selected_score"], 42.0)

    def test_collect_launcher_status_uses_pair_manifest_from_inner_loop_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            worktree_root = Path(tmpdir)
            materialized_root = worktree_root / "materialized"
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
                },
                {
                    "pair_id": "task-alpha__analytic-pipeline",
                    "task_name": "task-alpha",
                    "schema_id": "analytic-pipeline",
                    "pair_dir": str(materialized_root / "pairs" / "task-alpha__analytic-pipeline"),
                },
            ]
            (materialized_root / "pair_specs.jsonl").write_text(
                "\n".join(json.dumps(item) for item in pair_specs) + "\n"
            )
            pair_manifest = materialized_root / "reports" / "batch-01_pair_manifest.json"
            pair_manifest.parent.mkdir(parents=True)
            pair_manifest.write_text(
                json.dumps(
                    {
                        "pair_count": 1,
                        "task_names": ["task-alpha"],
                        "selected_pair_ids": ["task-alpha__artifact-generation"],
                    }
                )
                + "\n"
            )
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 1 task(s) -> 1 pair(s)\n"
                "Tasks: task-alpha\n"
            )
            (launcher_log_dir / "events.ndjson").write_text("")
            (launcher_log_dir / "run_inner_loop.sh").write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f"cd {worktree_root}\n"
                "uv run python scripts/launch_skillx_round0.py "
                "--pair-manifest materialized/reports/batch-01_pair_manifest.json "
                f"--materialized-root {materialized_root} "
                "--output-suffix run-demo\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:16:00+00:00",
            )

            self.assertEqual(status["total_pairs"], 1)
            self.assertEqual(len(status["pair_rows"]), 1)
            self.assertEqual(status["pair_rows"][0]["pair_id"], "task-alpha__artifact-generation")

    def test_collect_launcher_status_uses_selected_pair_ids_from_summary(self) -> None:
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
                },
                {
                    "pair_id": "task-alpha__analytic-pipeline",
                    "task_name": "task-alpha",
                    "schema_id": "analytic-pipeline",
                    "pair_dir": str(materialized_root / "pairs" / "task-alpha__analytic-pipeline"),
                },
            ]
            (materialized_root / "pair_specs.jsonl").write_text(
                "\n".join(json.dumps(item) for item in pair_specs) + "\n"
            )
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 1 task(s) -> 1 pair(s)\n"
                "Tasks: task-alpha\n"
            )
            (launcher_log_dir / "events.ndjson").write_text("")
            (launcher_log_dir / "summary.json").write_text(
                json.dumps(
                    {
                        "selected_task_names": ["task-alpha"],
                        "selected_pair_ids": ["task-alpha__analytic-pipeline"],
                        "total_pairs": 1,
                        "completed_pairs": 0,
                        "succeeded_pairs": 0,
                        "failed_pairs": 0,
                        "results": [],
                    }
                )
                + "\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:16:00+00:00",
            )

            self.assertEqual(status["total_pairs"], 1)
            self.assertEqual(len(status["pair_rows"]), 1)
            self.assertEqual(status["pair_rows"][0]["pair_id"], "task-alpha__analytic-pipeline")

    def test_pair_status_labels_skipped_baseline_perfect(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            label = self.module._pair_status_from_sources(
                launcher_result={"status": "succeeded"},
                run_status={
                    "status": "skipped_baseline_perfect",
                    "baseline_perfect_reruns": "3",
                },
                run_dir=Path(tmpdir),
            )

            self.assertEqual(label, "skipped (R0 100%, reruns=3)")

    def test_collect_launcher_status_synthesizes_latest_event_from_active_run_activity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            materialized_root = Path(tmpdir)
            launcher_log_dir = materialized_root / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            active_run_dir = (
                materialized_root
                / "pairs"
                / "task-alpha__artifact-generation"
                / "refine_run_run-demo"
            )
            round0 = active_run_dir / "refine" / "task-alpha" / "rounds" / "round-0"
            round0.mkdir(parents=True)
            (active_run_dir / "RUN_STATUS.md").write_text(
                "- status: `running`\n"
                "- task: `task-alpha`\n"
            )
            (round0 / "placeholder.txt").write_text("working\n")
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 1 task(s) -> 1 pair(s)\n"
                "Tasks: task-alpha\n"
            )
            (launcher_log_dir / "events.ndjson").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "event": "pair_started",
                                "index": 1,
                                "observed_at": "2026-04-10T07:56:04+00:00",
                                "pair_id": "task-alpha__artifact-generation",
                                "schema_id": "artifact-generation",
                                "task_name": "task-alpha",
                            }
                        ),
                        json.dumps(
                            {
                                "event": "docker_health_probe",
                                "observed_at": "2026-04-10T07:56:05+00:00",
                                "pair_id": "task-alpha__artifact-generation",
                                "schema_id": "artifact-generation",
                                "task_name": "task-alpha",
                            }
                        ),
                    ]
                )
                + "\n"
            )
            fresh_ts = self.module._coerce_datetime("2026-04-10T08:04:30+00:00").timestamp()
            for path in [
                active_run_dir,
                active_run_dir / "refine",
                active_run_dir / "refine" / "task-alpha",
                active_run_dir / "refine" / "task-alpha" / "rounds",
                round0,
                active_run_dir / "RUN_STATUS.md",
                round0 / "placeholder.txt",
            ]:
                os.utime(path, (fresh_ts, fresh_ts))

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:04:35+00:00",
            )

            self.assertEqual(status["latest_event"]["event"], "active_run_heartbeat")
            self.assertEqual(status["latest_event"]["task_name"], "task-alpha")
            self.assertEqual(status["latest_event"]["status"], "running")
            self.assertEqual(status["latest_event_at"], "2026-04-10T08:04:30+00:00")

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

    def test_collect_launcher_status_reads_preflight_risk_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_log_dir = Path(tmpdir) / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 1 task(s) -> 1 pair(s)\n"
                "Tasks: task-alpha\n"
            )
            (launcher_log_dir / "events.ndjson").write_text("")
            (launcher_log_dir / "preflight_docker_risk_audit.json").write_text(
                json.dumps(
                    {
                        "docker_server_os": "linux",
                        "docker_server_arch": "arm64",
                        "affected_pairs": 1,
                        "high_risk_pairs": 1,
                        "medium_risk_pairs": 0,
                        "low_risk_pairs": 0,
                        "pairs": [
                            {
                                "pair_id": "task-alpha__artifact-generation",
                                "task_name": "task-alpha",
                                "schema_id": "artifact-generation",
                                "risk_level": "high",
                                "risk_count": 1,
                                "risks": [
                                    {
                                        "code": "amd64_platform_pin",
                                        "severity": "high",
                                        "summary": "Dockerfile pins linux/amd64 while Docker server arch is arm64",
                                    }
                                ],
                            }
                        ],
                    }
                )
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:04:35+00:00",
            )

            audit = status["preflight_risk_audit"]
            self.assertEqual(audit["affected_pairs"], 1)
            self.assertEqual(audit["pairs"][0]["risk_level"], "high")

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
            self.assertEqual(completed["delta_vs_r0"], 5.0)
            self.assertEqual(completed["pair_status"], "completed")
            self.assertEqual(running["schema_id"], "analytic-pipeline")
            self.assertEqual(running["round_scores"]["R0"], 22.5)
            self.assertEqual(running["round_rewards_raw"]["R0"], 0.225)
            self.assertIsNone(running["selected_round"])
            self.assertEqual(running["pair_status"], "running")

    def test_collect_launcher_status_handles_relative_pair_dirs_and_active_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            materialized_root = Path(tmpdir)
            launcher_log_dir = materialized_root / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            (materialized_root / "manifest.json").write_text(
                json.dumps({"schema_ids": ["schema-a", "schema-b"]}) + "\n"
            )
            pair_specs = [
                {
                    "pair_id": "task-alpha__schema-a",
                    "task_name": "task-alpha",
                    "schema_id": "schema-a",
                    "pair_dir": "pairs/task-alpha__schema-a",
                },
                {
                    "pair_id": "task-alpha__schema-b",
                    "task_name": "task-alpha",
                    "schema_id": "schema-b",
                    "pair_dir": "pairs/task-alpha__schema-b",
                },
            ]
            (materialized_root / "pair_specs.jsonl").write_text(
                "\n".join(json.dumps(item) for item in pair_specs) + "\n"
            )
            for pair_id in ("task-alpha__schema-a", "task-alpha__schema-b"):
                run_dir = materialized_root / "pairs" / pair_id / "refine_run_run-demo"
                run_dir.mkdir(parents=True)
                (run_dir / "docker_preflight_risk.json").write_text("{}\n")
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 1 task(s) -> 2 pair(s)\n"
                "Tasks: task-alpha\n"
                "Running pairs with max_concurrent_pairs=3\n"
            )
            (launcher_log_dir / "events.ndjson").write_text(
                json.dumps(
                    {
                        "event": "pair_started",
                        "index": 1,
                        "pair_id": "task-alpha__schema-a",
                        "observed_at": "2026-04-10T08:10:00+00:00",
                    }
                )
                + "\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:10:05+00:00",
            )

            self.assertEqual(status["active_pair_count"], 1)
            self.assertEqual(status["max_concurrent_pairs"], 3)
            self.assertEqual(len(status["active_pair_details"]), 1)
            self.assertEqual(status["active_pair_details"][0]["pair_id"], "task-alpha__schema-a")
            pair_statuses = {
                row["pair_id"]: row["pair_status"]
                for row in status["pair_rows"]
            }
            self.assertEqual(pair_statuses["task-alpha__schema-a"], "running")
            self.assertEqual(pair_statuses["task-alpha__schema-b"], "pending")

    def test_render_dashboard_shows_multiple_active_pair_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            materialized_root = Path(tmpdir)
            launcher_log_dir = materialized_root / "launcher_logs" / "run-demo"
            launcher_log_dir.mkdir(parents=True)
            (materialized_root / "manifest.json").write_text(
                json.dumps({"schema_ids": ["schema-a", "schema-b"]}) + "\n"
            )
            pair_specs = [
                {
                    "pair_id": "task-alpha__schema-a",
                    "task_name": "task-alpha",
                    "schema_id": "schema-a",
                    "pair_dir": "pairs/task-alpha__schema-a",
                },
                {
                    "pair_id": "task-beta__schema-b",
                    "task_name": "task-beta",
                    "schema_id": "schema-b",
                    "pair_dir": "pairs/task-beta__schema-b",
                },
            ]
            (materialized_root / "pair_specs.jsonl").write_text(
                "\n".join(json.dumps(item) for item in pair_specs) + "\n"
            )
            for pair in pair_specs:
                pair_id = pair["pair_id"]
                task_name = pair["task_name"]
                run_dir = materialized_root / "pairs" / pair_id / "refine_run_run-demo"
                round0 = run_dir / "refine" / task_name / "rounds" / "round-0"
                round0.mkdir(parents=True)
                (run_dir / "RUN_STATUS.md").write_text(
                    f"- status: `running`\n- task: `{task_name}`\n"
                )
                (round0 / "orchestrator_log.ndjson").write_text(
                    json.dumps(
                        {
                            "round_index": 0,
                            "event_type": "executor_completed",
                            "status": "ok",
                            "timestamp": "2026-04-10T08:10:02+00:00",
                        }
                    )
                    + "\n"
                )
            (launcher_log_dir / "launcher.stdout.log").write_text(
                "Selected 2 task(s) -> 2 pair(s)\n"
                "Tasks: task-alpha, task-beta\n"
                "Running pairs with max_concurrent_pairs=3\n"
            )
            (launcher_log_dir / "events.ndjson").write_text(
                json.dumps(
                    {
                        "event": "pair_started",
                        "index": 1,
                        "pair_id": "task-alpha__schema-a",
                        "task_name": "task-alpha",
                        "schema_id": "schema-a",
                        "observed_at": "2026-04-10T08:10:00+00:00",
                    }
                )
                + "\n"
                + json.dumps(
                    {
                        "event": "pair_started",
                        "index": 2,
                        "pair_id": "task-beta__schema-b",
                        "task_name": "task-beta",
                        "schema_id": "schema-b",
                        "observed_at": "2026-04-10T08:10:01+00:00",
                    }
                )
                + "\n"
            )

            status = self.module.collect_launcher_status(
                launcher_log_dir,
                now="2026-04-10T08:10:05+00:00",
            )
            html = self.module.render_dashboard_html(status, refresh_seconds=9)

            self.assertEqual(status["active_pair_count"], 2)
            self.assertEqual(len(status["active_pair_details"]), 2)
            self.assertEqual(
                [detail["pair_id"] for detail in status["active_pair_details"]],
                ["task-alpha__schema-a", "task-beta__schema-b"],
            )
            self.assertIn("Current Pair Details", html)
            self.assertEqual(html.count('<div class="pair-detail-card">'), 2)
            self.assertIn("task-alpha__schema-a", html)
            self.assertIn("task-beta__schema-b", html)

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

    def test_collect_launcher_status_marks_completed_keep_current_pairs_explicitly(self) -> None:
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
                    }
                )
                + "\n"
            )
            run_dir = pair_dir / "refine_run_run-demo"
            round0 = run_dir / "refine" / "task-alpha" / "rounds" / "round-0"
            round1 = run_dir / "refine" / "task-alpha" / "rounds" / "round-1"
            (round0 / "tune_check").mkdir(parents=True)
            (round1 / "tune_check").mkdir(parents=True)
            (round0 / "tune_check" / "result.json").write_text(json.dumps({"reward": 1.0}) + "\n")
            (round1 / "tune_check" / "result.json").write_text(json.dumps({"reward": 1.0}) + "\n")
            (round1 / "orchestrator_log.ndjson").write_text(
                "\n".join(
                    [
                        json.dumps({"round_index": 1, "event_type": "round_started", "status": "ok"}),
                        json.dumps({"round_index": 1, "event_type": "executor_completed", "status": "ok"}),
                        json.dumps({"round_index": 1, "event_type": "role_a_completed", "status": "ok"}),
                        json.dumps({"round_index": 1, "event_type": "role_b_completed", "status": "ok"}),
                        json.dumps({"round_index": 1, "event_type": "round_decision_loaded", "status": "keep_current"}),
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

            self.assertEqual(status["pair_rows"][0]["pair_status"], "completed (keep_current@R1)")

    def test_collect_launcher_status_marks_completed_runtime_failures_explicitly(self) -> None:
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
            (run_dir / "refine" / "task-alpha" / "rounds" / "round-0" / "tune_check").mkdir(parents=True)
            (
                run_dir
                / "refine"
                / "task-alpha"
                / "rounds"
                / "round-0"
                / "tune_check"
                / "result.json"
            ).write_text(json.dumps({"reward": 0.0}) + "\n")
            (run_dir / "RUN_STATUS.md").write_text(
                "- status: `completed_with_runtime_failures`\n"
                "- round_budget: `3`\n"
                "- runtime_failure_rounds: `R0`\n"
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

            self.assertEqual(status["health"], "completed_with_issues")
            self.assertEqual(status["issue_pairs"], 1)
            self.assertEqual(status["pair_rows"][0]["pair_status"], "completed (runtime exceptions)")
            self.assertTrue(status["pair_rows"][0]["pair_has_issues"])

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
            self.assertIn("Current Pair Details", html)
            self.assertIn("Current round", html)
            self.assertIn("executor", html)
            self.assertIn("Task / Pair Results", html)
            self.assertIn("0-100 scale", html)
            self.assertEqual(payload["total_pairs"], 7)
            self.assertEqual(payload["health"], "running")
            self.assertEqual(payload["pair_detail"]["current_round_index"], 1)


if __name__ == "__main__":
    unittest.main()

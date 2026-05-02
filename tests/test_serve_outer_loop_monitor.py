from __future__ import annotations

import importlib.util
import json
import os
import socket
import sys
import tempfile
import threading
import time
import unittest
import urllib.request
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "serve_outer_loop_monitor.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("serve_outer_loop_monitor", SCRIPT_PATH)
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _make_outer_loop_artifacts(root: Path) -> tuple[Path, Path, Path]:
    control_plane_dir = root / "reports" / "outer-label" / "control-plane"
    schema_update_dir = root / "reports" / "outer-label" / "schema-updates"
    next_root = root / "outer-label-candidates"
    _write_json(
        control_plane_dir / "control_plane_bundle.json",
        {
            "schema_ids": ["schema-alpha", "schema-beta"],
            "assignments": [
                {
                    "task_name": "task-a",
                    "assignment_status": "assigned",
                    "assigned_category": "schema-alpha",
                },
                {
                    "task_name": "task-b",
                    "assignment_status": "assigned",
                    "assigned_category": "schema-beta",
                },
            ],
            "score_matrix": {"long_rows": [{"task_name": "task-a"} for _ in range(4)]},
            "diagnostics": {
                "schema_training_assignments": [
                    {"schema_id": "schema-alpha", "task_name": "task-a"},
                    {"schema_id": "schema-beta", "task_name": "task-b"},
                ]
            },
        },
    )
    _write_json(
        schema_update_dir / "llm_runs" / "schema-alpha" / "attempts.json",
        {
            "attempts": [
                {
                    "attempt": 1,
                    "profile": {"label": "primary-claude"},
                    "returncode": 1,
                    "status": "hard_rate_limit",
                    "quota_hard_terms": ["http_429"],
                },
                {
                    "attempt": 2,
                    "profile": {"label": "fallback-claude-1"},
                    "returncode": 0,
                    "status": "succeeded",
                    "quota_hard_terms": [],
                },
            ]
        },
    )
    _write_json(
        schema_update_dir / "llm_runs" / "schema-beta" / "attempts.json",
        {
            "attempts": [
                {
                    "attempt": 1,
                    "profile": {"label": "fallback-claude-1"},
                    "returncode": 0,
                    "status": "succeeded",
                    "quota_hard_terms": [],
                }
            ]
        },
    )
    _write_json(
        schema_update_dir / "rewrite_verification.json",
        {
            "status": "passed",
            "expected_rewrite_schema_count": 2,
            "completed_rewrite_schema_count": 2,
        },
    )
    _write_json(
        next_root / "manifest.json",
        {
            "task_count": 20,
            "schema_count": 7,
            "pair_count": 140,
        },
    )
    return control_plane_dir, schema_update_dir, next_root


class ServeOuterLoopMonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_payload_reports_completed_run_and_fallback_attempts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            control_plane_dir, schema_update_dir, next_root = _make_outer_loop_artifacts(
                Path(tmpdir)
            )
            payload = self.module.build_monitor_payload(
                control_plane_dir=control_plane_dir,
                schema_update_dir=schema_update_dir,
                next_materialized_root=next_root,
                stale_after_sec=600,
            )

        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["health_level"], "ok")
        self.assertEqual(payload["phase"], "completed")
        self.assertEqual(payload["control_plane"]["assigned_count"], 2)
        self.assertEqual(payload["schema_rewrite"]["succeeded_schema_count"], 2)
        self.assertEqual(payload["schema_rewrite"]["rate_limited_schema_count"], 1)
        self.assertEqual(payload["schema_rewrite"]["fallback_schema_count"], 2)
        self.assertEqual(payload["materialization"]["pair_count"], 140)

    def test_payload_does_not_mark_non_quota_warning_as_rate_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            control_plane_dir = root / "control-plane"
            schema_update_dir = root / "schema-updates"
            next_root = root / "next"
            _write_json(control_plane_dir / "control_plane_bundle.json", {"assignments": []})
            _write_json(
                schema_update_dir / "llm_runs" / "schema-alpha" / "attempts.json",
                {
                    "attempts": [
                        {
                            "attempt": 1,
                            "profile": {"label": "primary-claude"},
                            "returncode": 1,
                            "status": "failed",
                            "quota_hard_terms": [],
                        }
                    ]
                },
            )
            payload = self.module.build_monitor_payload(
                control_plane_dir=control_plane_dir,
                schema_update_dir=schema_update_dir,
                next_materialized_root=next_root,
                stale_after_sec=600,
            )

        self.assertEqual(payload["health_level"], "error")
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(payload["schema_rewrite"]["failed_schema_count"], 1)
        self.assertEqual(payload["schema_rewrite"]["rate_limited_schema_count"], 0)

    def test_payload_marks_incomplete_run_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            control_plane_dir = root / "control-plane"
            schema_update_dir = root / "schema-updates"
            next_root = root / "next"
            _write_json(control_plane_dir / "control_plane_bundle.json", {"assignments": []})
            old_timestamp = time.time() - 3600
            for path in [control_plane_dir / "control_plane_bundle.json", control_plane_dir]:
                os.utime(path, (old_timestamp, old_timestamp))
            payload = self.module.build_monitor_payload(
                control_plane_dir=control_plane_dir,
                schema_update_dir=schema_update_dir,
                next_materialized_root=next_root,
                stale_after_sec=1,
            )

        self.assertEqual(payload["health_level"], "warn")
        self.assertEqual(payload["status"], "stale")
        self.assertIn("no artifact update", payload["issues"][0])

    def test_http_server_serves_monitor_and_api(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            control_plane_dir, schema_update_dir, next_root = _make_outer_loop_artifacts(
                Path(tmpdir)
            )
            port = _free_port()
            server = self.module.build_server(
                control_plane_dir=control_plane_dir,
                schema_update_dir=schema_update_dir,
                next_materialized_root=next_root,
                log_path=None,
                stale_after_sec=600,
                host="127.0.0.1",
                port=port,
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                html = urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5).read().decode("utf-8")
                payload = json.loads(
                    urllib.request.urlopen(
                        f"http://127.0.0.1:{port}/api/outer-loop", timeout=5
                    ).read().decode("utf-8")
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertIn("Outer-Loop Monitor", html)
        self.assertIn("Schema Rewrite Attempts", html)
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["schema_rewrite"]["fallback_schema_count"], 2)


if __name__ == "__main__":
    unittest.main()

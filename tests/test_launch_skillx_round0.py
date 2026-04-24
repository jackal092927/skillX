from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

import path_setup
from skillx import docker_health


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "launch_skillx_round0.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("launch_skillx_round0", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LaunchSkillXRound0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def setUp(self) -> None:
        docker_health._reset_fake_docker_health_state()

    def tearDown(self) -> None:
        docker_health._reset_fake_docker_health_state()

    def _build_fixture(self, root: Path) -> dict[str, Path]:
        task_slice_path = root / "task-slice.json"
        task_slice_path.write_text(
            json.dumps(
                {
                    "tasks": [
                        {"task_name": "task-alpha", "seed_schema_id": "analytic-pipeline"},
                        {"task_name": "task-beta", "seed_schema_id": "artifact-generation"},
                        {"task_name": "task-gamma", "seed_schema_id": "environment-control"},
                    ]
                }
            )
        )

        materialized_root = root / "round0-root"
        pairs_dir = materialized_root / "pairs"
        pairs_dir.mkdir(parents=True)
        manifest_path = materialized_root / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "schema_ids": ["analytic-pipeline", "artifact-generation"],
                    "task_names": ["task-alpha", "task-beta", "task-gamma"],
                }
            )
        )

        for task_name in ("task-alpha", "task-beta", "task-gamma"):
            task_root = root / "skillsbench-src" / "tasks" / task_name
            (task_root / "environment" / "skills" / "starter").mkdir(parents=True)
            (task_root / "instruction.md").write_text("instruction\n")
            (task_root / "task.toml").write_text(
                "\n".join(
                    [
                        '[metadata]',
                        f'id = "{task_name}"',
                        '',
                        '[environment]',
                        'memory_mb = 2048',
                        'storage_mb = 10240',
                        'build_timeout_sec = 600',
                        '',
                    ]
                )
            )
            (task_root / "environment" / "Dockerfile").write_text(
                "\n".join(
                    [
                        "FROM python:3.11-slim",
                        "RUN pip install --no-cache-dir pandas==2.2.3",
                        "",
                    ]
                )
            )
            skill_file = task_root / "environment" / "skills" / "starter" / "SKILL.md"
            skill_file.write_text("# starter\n")
            for schema_id in ("analytic-pipeline", "artifact-generation"):
                pair_dir = pairs_dir / f"{task_name}__{schema_id}"
                pair_dir.mkdir(parents=True)
                pair_spec = {
                    "pair_id": f"{task_name}__{schema_id}",
                    "task_name": task_name,
                    "schema_id": schema_id,
                    "pair_dir": str(pair_dir.relative_to(materialized_root)),
                    "skillsbench_task_dir": str(root / "skillsbench-src" / "tasks" / task_name),
                    "starting_skillpack_dir": str(
                        root / "skillsbench-src" / "tasks" / task_name / "environment" / "skills"
                    ),
                    "starting_label": "C1",
                }
                (pair_dir / "pair_spec.json").write_text(json.dumps(pair_spec))

        protocol_path = root / "docs" / "protocols" / "skillx-refine-protocol-v0.1.md"
        protocol_path.parent.mkdir(parents=True)
        protocol_path.write_text("protocol\n")

        bundle_path = root / "docs" / "protocols" / "skillx-refine-bundle-contract-v0.1.md"
        bundle_path.write_text("bundle\n")

        oauth_file = root / ".claude" / "claude-code-oauth-token"
        oauth_file.parent.mkdir(parents=True)
        oauth_file.write_text("token\n")

        return {
            "task_slice_path": task_slice_path,
            "materialized_root": materialized_root,
            "protocol_path": protocol_path,
            "bundle_path": bundle_path,
            "oauth_file": oauth_file,
        }

    def test_validate_selected_pair_inputs_raises_for_missing_task_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            _, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])
            broken_pair = dict(pair_specs[0])
            broken_pair["skillsbench_task_dir"] = "../missing/tasks/task-alpha"

            with self.assertRaises(FileNotFoundError) as ctx:
                self.module.validate_selected_pair_inputs(
                    [broken_pair],
                    materialized_root=fixture["materialized_root"],
                )

            self.assertIn("Re-run scripts/rematerialize_round0_root.sh", str(ctx.exception))

    def test_select_first_n_tasks_expands_all_schemas(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            task_names = self.module.load_task_names(fixture["task_slice_path"])
            manifest, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])

            selected = self.module.select_pair_specs(
                pair_specs,
                task_names=task_names,
                schema_ids=manifest["schema_ids"],
                first_n=2,
                explicit_tasks=None,
            )

            self.assertEqual(
                [pair["pair_id"] for pair in selected],
                [
                    "task-alpha__analytic-pipeline",
                    "task-alpha__artifact-generation",
                    "task-beta__analytic-pipeline",
                    "task-beta__artifact-generation",
                ],
            )

    def test_select_explicit_task_returns_single_task_across_all_schemas(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            task_names = self.module.load_task_names(fixture["task_slice_path"])
            manifest, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])

            selected = self.module.select_pair_specs(
                pair_specs,
                task_names=task_names,
                schema_ids=manifest["schema_ids"],
                first_n=None,
                explicit_tasks=["task-gamma"],
            )

            self.assertEqual(
                [pair["pair_id"] for pair in selected],
                [
                    "task-gamma__analytic-pipeline",
                    "task-gamma__artifact-generation",
                ],
            )

    def test_select_explicit_tasks_preserves_slice_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            task_names = self.module.load_task_names(fixture["task_slice_path"])
            manifest, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])

            selected = self.module.select_pair_specs(
                pair_specs,
                task_names=task_names,
                schema_ids=manifest["schema_ids"],
                first_n=None,
                explicit_tasks=["task-gamma", "task-alpha"],
            )

            self.assertEqual(
                [pair["pair_id"] for pair in selected],
                [
                    "task-alpha__analytic-pipeline",
                    "task-alpha__artifact-generation",
                    "task-gamma__analytic-pipeline",
                    "task-gamma__artifact-generation",
                ],
            )

    def test_select_pair_specs_by_pair_ids_preserves_manifest_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            _, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])

            selected = self.module.select_pair_specs_by_pair_ids(
                pair_specs,
                pair_ids=[
                    "task-gamma__artifact-generation",
                    "task-alpha__analytic-pipeline",
                ],
            )

            self.assertEqual(
                [pair["pair_id"] for pair in selected],
                [
                    "task-gamma__artifact-generation",
                    "task-alpha__analytic-pipeline",
                ],
            )

    def test_load_pair_ids_from_manifest_reads_selected_pair_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "pair-manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "selected_pair_ids": [
                            "task-beta__artifact-generation",
                            "task-alpha__analytic-pipeline",
                        ]
                    }
                )
            )

            pair_ids = self.module.load_pair_ids_from_manifest(manifest_path)

            self.assertEqual(
                pair_ids,
                [
                    "task-beta__artifact-generation",
                    "task-alpha__analytic-pipeline",
                ],
            )

    def test_build_refine_command_uses_uv_and_explicit_protocol_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            _, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])
            pair = next(spec for spec in pair_specs if spec["pair_id"] == "task-beta__artifact-generation")

            command = self.module.build_refine_command(
                pair,
                materialized_root=fixture["materialized_root"],
                oauth_file=fixture["oauth_file"],
                round_budget=3,
                agent="claude-code",
                model="anthropic/claude-sonnet-4-5",
                refine_protocol_path=fixture["protocol_path"],
                bundle_contract_path=fixture["bundle_path"],
                output_suffix="smoke3",
            )

            command_text = " ".join(command)
            self.assertEqual(command[:5], ["uv", "run", "--python", "3.11", "python"])
            self.assertIn("--task task-beta", command_text)
            self.assertIn("--starting-label C1", command_text)
            self.assertIn("--refine-protocol-path", command_text)
            self.assertIn(str(fixture["protocol_path"]), command_text)
            self.assertIn("--bundle-contract-path", command_text)
            self.assertIn(str(fixture["bundle_path"]), command_text)
            self.assertIn("refine_run_smoke3", command_text)
            self.assertIn("task-beta__artifact-generation__smoke3", command_text)

    def test_build_refine_command_infers_codex_agent_from_model_and_omits_oauth(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            _, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])
            pair = next(spec for spec in pair_specs if spec["pair_id"] == "task-beta__artifact-generation")

            command = self.module.build_refine_command(
                pair,
                materialized_root=fixture["materialized_root"],
                oauth_file=fixture["oauth_file"],
                round_budget=3,
                agent=None,
                model="openai/gpt-5.2-codex",
                refine_protocol_path=fixture["protocol_path"],
                bundle_contract_path=fixture["bundle_path"],
                output_suffix="smoke4",
            )

            command_text = " ".join(command)
            self.assertIn("--agent codex", command_text)
            self.assertNotIn("--oauth-file", command_text)

    def test_build_refine_command_prefers_local_materialized_pair_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            _, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])
            pair = next(spec for spec in pair_specs if spec["pair_id"] == "task-beta__artifact-generation")
            pair["pair_dir"] = str(Path(tmpdir) / "elsewhere" / pair["pair_id"])

            command = self.module.build_refine_command(
                pair,
                materialized_root=fixture["materialized_root"],
                oauth_file=fixture["oauth_file"],
                round_budget=3,
                agent="claude-code",
                model="anthropic/claude-sonnet-4-5",
                refine_protocol_path=fixture["protocol_path"],
                bundle_contract_path=fixture["bundle_path"],
                output_suffix="local-run",
            )

            expected_output_dir = (
                fixture["materialized_root"]
                / "pairs"
                / "task-beta__artifact-generation"
                / "refine_run_local-run"
            )
            expected_source_stub = (
                fixture["materialized_root"]
                / "pairs"
                / "task-beta__artifact-generation"
                / "source_stub"
            )
            command_text = " ".join(command)
            self.assertIn(str(expected_output_dir), command_text)
            self.assertTrue(expected_source_stub.exists())

    def test_build_refine_command_forwards_environment_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            _, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])
            pair = next(spec for spec in pair_specs if spec["pair_id"] == "task-beta__artifact-generation")

            command = self.module.build_refine_command(
                pair,
                materialized_root=fixture["materialized_root"],
                oauth_file=fixture["oauth_file"],
                round_budget=3,
                agent="claude-code",
                model="anthropic/claude-sonnet-4-5",
                refine_protocol_path=fixture["protocol_path"],
                bundle_contract_path=fixture["bundle_path"],
                output_suffix="override-check",
                override_memory_mb=8192,
                override_storage_mb=12288,
            )

            command_text = " ".join(command)
            self.assertIn("--override-memory-mb 8192", command_text)
            self.assertIn("--override-storage-mb 12288", command_text)

    def test_resolve_pair_dir_supports_materialized_relative_pair_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            _, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])
            pair = next(spec for spec in pair_specs if spec["pair_id"] == "task-alpha__analytic-pipeline")

            resolved = self.module.resolve_pair_dir(pair, materialized_root=fixture["materialized_root"])

            self.assertEqual(
                resolved,
                (fixture["materialized_root"] / "pairs" / "task-alpha__analytic-pipeline").resolve(),
            )

    def test_build_launcher_summary_keeps_selected_pair_total_during_partial_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            summary = self.module.build_launcher_summary(
                task_slice_path=root / "task-slice.json",
                materialized_root=root / "round0-root",
                selected_task_names=["task-alpha", "task-beta"],
                selected_pair_count=4,
                max_concurrent_pairs=3,
                results=[
                    {
                        "pair_id": "task-alpha__artifact-generation",
                        "status": "succeeded",
                    }
                ],
            )

            self.assertEqual(summary["total_pairs"], 4)
            self.assertEqual(summary["completed_pairs"], 1)
            self.assertEqual(summary["succeeded_pairs"], 1)
            self.assertEqual(summary["failed_pairs"], 0)

    def test_build_preflight_docker_risk_audit_flags_amd64_pin_as_medium_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            task_root = Path(tmpdir) / "skillsbench-src" / "tasks" / "task-beta"
            (task_root / "task.toml").write_text(
                "\n".join(
                    [
                        '[metadata]',
                        'id = "task-beta"',
                        '',
                        '[environment]',
                        'memory_mb = 8192',
                        'storage_mb = 10240',
                        'build_timeout_sec = 900',
                        '',
                    ]
                )
            )
            (task_root / "environment" / "Dockerfile").write_text(
                "\n".join(
                    [
                        "FROM --platform=linux/amd64 ubuntu:20.04",
                        "RUN pip install netCDF4==1.6.5",
                        "",
                    ]
                )
            )
            _, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])
            selected_pairs = [spec for spec in pair_specs if spec["pair_id"] == "task-beta__analytic-pipeline"]

            audit = self.module.build_preflight_docker_risk_audit(
                selected_pairs=selected_pairs,
                materialized_root=fixture["materialized_root"],
                docker_health_report={
                    "observed_at": "2026-04-13T00:00:00+00:00",
                    "docker_mem_bytes": 17_179_869_184,
                    "required_memory_bytes": 16_000_000_000,
                    "docker_version_server": {"Os": "linux", "Arch": "arm64"},
                    "docker_info": {"MemTotal": 17_179_869_184},
                },
            )

            self.assertEqual(audit["affected_pairs"], 1)
            self.assertEqual(audit["high_risk_pairs"], 0)
            self.assertEqual(audit["medium_risk_pairs"], 1)
            pair = audit["pairs"][0]
            self.assertEqual(pair["risk_level"], "medium")
            risk_codes = {item["code"] for item in pair["risks"]}
            self.assertIn("amd64_platform_pin", risk_codes)
            self.assertIn("high_task_memory_requirement", risk_codes)

    def test_main_writes_preflight_docker_risk_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            task_root = Path(tmpdir) / "skillsbench-src" / "tasks" / "task-alpha"
            (task_root / "task.toml").write_text(
                "\n".join(
                    [
                        '[metadata]',
                        'id = "task-alpha"',
                        '',
                        '[environment]',
                        'memory_mb = 8192',
                        'storage_mb = 10240',
                        'build_timeout_sec = 900',
                        '',
                    ]
                )
            )
            (task_root / "environment" / "Dockerfile").write_text(
                "\n".join(
                    [
                        "FROM --platform=linux/amd64 ubuntu:20.04",
                        "RUN pip install netCDF4==1.6.5",
                        "",
                    ]
                )
            )

            with mock.patch.object(
                self.module,
                "probe_docker_health",
                return_value={
                    "healthy": True,
                    "category": "healthy",
                    "message": "ok",
                    "observed_at": "2026-04-13T00:00:00+00:00",
                    "docker_mem_bytes": 17_179_869_184,
                    "required_memory_bytes": 16_000_000_000,
                    "docker_version_server": {"Os": "linux", "Arch": "arm64"},
                    "docker_info": {"MemTotal": 17_179_869_184},
                },
            ):
                with mock.patch.object(
                    self.module.subprocess,
                    "run",
                    return_value=mock.Mock(returncode=0),
                ):
                    exit_code = self.module.main(
                        [
                            "1",
                            "--task-slice",
                            str(fixture["task_slice_path"]),
                            "--materialized-root",
                            str(fixture["materialized_root"]),
                            "--oauth-file",
                            str(fixture["oauth_file"]),
                            "--refine-protocol-path",
                            str(fixture["protocol_path"]),
                            "--bundle-contract-path",
                            str(fixture["bundle_path"]),
                            "--output-suffix",
                            "preflight-audit",
                            "--max-concurrent-pairs",
                            "1",
                        ]
                    )

            self.assertEqual(exit_code, 0)
            audit_path = (
                fixture["materialized_root"]
                / "launcher_logs"
                / "preflight-audit"
                / "preflight_docker_risk_audit.json"
            )
            self.assertTrue(audit_path.exists())
            audit_payload = json.loads(audit_path.read_text())
            self.assertEqual(audit_payload["affected_pairs"], 2)
            pair_risk_path = (
                fixture["materialized_root"]
                / "pairs"
                / "task-alpha__analytic-pipeline"
                / "refine_run_preflight-audit"
                / "docker_preflight_risk.json"
            )
            self.assertTrue(pair_risk_path.exists())
            pair_payload = json.loads(pair_risk_path.read_text())
            self.assertEqual(pair_payload["pair_id"], "task-alpha__analytic-pipeline")
            events_path = (
                fixture["materialized_root"]
                / "launcher_logs"
                / "preflight-audit"
                / "events.ndjson"
            )
            events = [json.loads(line) for line in events_path.read_text().splitlines() if line.strip()]
            event_names = [event["event"] for event in events]
            self.assertIn("preflight_risk_audit_completed", event_names)
            self.assertIn("preflight_risk_detected", event_names)

    def test_main_dry_run_accepts_numeric_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = self.module.main(
                    [
                        "2",
                        "--dry-run",
                        "--task-slice",
                        str(fixture["task_slice_path"]),
                        "--materialized-root",
                        str(fixture["materialized_root"]),
                        "--oauth-file",
                        str(fixture["oauth_file"]),
                        "--refine-protocol-path",
                        str(fixture["protocol_path"]),
                        "--bundle-contract-path",
                        str(fixture["bundle_path"]),
                    ]
                )

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Selected 2 task(s) -> 4 pair(s)", output)
            self.assertIn("task-alpha__analytic-pipeline", output)
            self.assertIn("task-beta__artifact-generation", output)
            self.assertNotIn("task-gamma__analytic-pipeline", output)

    def test_main_dry_run_accepts_task_index_and_task_union(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = self.module.main(
                    [
                        "--dry-run",
                        "--task-index",
                        "2",
                        "--task",
                        "task-gamma",
                        "--task-slice",
                        str(fixture["task_slice_path"]),
                        "--materialized-root",
                        str(fixture["materialized_root"]),
                        "--oauth-file",
                        str(fixture["oauth_file"]),
                        "--refine-protocol-path",
                        str(fixture["protocol_path"]),
                        "--bundle-contract-path",
                        str(fixture["bundle_path"]),
                    ]
                )

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Selected 2 task(s) -> 4 pair(s)", output)
            self.assertIn("Tasks: task-beta, task-gamma", output)
            self.assertIn("task-beta__analytic-pipeline", output)
            self.assertIn("task-gamma__artifact-generation", output)
            self.assertNotIn("task-alpha__analytic-pipeline", output)

    def test_main_dry_run_accepts_pair_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            pair_manifest_path = Path(tmpdir) / "pair-manifest.json"
            pair_manifest_path.write_text(
                json.dumps(
                    {
                        "selected_pair_ids": [
                            "task-gamma__artifact-generation",
                            "task-alpha__analytic-pipeline",
                        ]
                    }
                )
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = self.module.main(
                    [
                        "--dry-run",
                        "--pair-manifest",
                        str(pair_manifest_path),
                        "--task-slice",
                        str(fixture["task_slice_path"]),
                        "--materialized-root",
                        str(fixture["materialized_root"]),
                        "--oauth-file",
                        str(fixture["oauth_file"]),
                        "--refine-protocol-path",
                        str(fixture["protocol_path"]),
                        "--bundle-contract-path",
                        str(fixture["bundle_path"]),
                    ]
                )

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Selected 2 task(s) -> 2 pair(s)", output)
            self.assertIn("task-gamma__artifact-generation", output)
            self.assertIn("task-alpha__analytic-pipeline", output)
            self.assertNotIn("task-beta__artifact-generation", output)

    def test_main_continues_after_subprocess_failure_and_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            seen_commands: list[list[str]] = []

            def fake_run(command: list[str], cwd: str, check: bool) -> object:
                seen_commands.append(command)
                joined = " ".join(command)
                if "--task task-alpha" in joined and "--starting-label C1" in joined and "artifact-generation" in joined:
                    raise self.module.subprocess.CalledProcessError(returncode=17, cmd=command)
                return mock.Mock(returncode=0)

            stdout = io.StringIO()
            with mock.patch.object(self.module.subprocess, "run", side_effect=fake_run):
                with contextlib.redirect_stdout(stdout):
                    exit_code = self.module.main(
                        [
                            "2",
                            "--task-slice",
                            str(fixture["task_slice_path"]),
                            "--materialized-root",
                            str(fixture["materialized_root"]),
                            "--oauth-file",
                            str(fixture["oauth_file"]),
                            "--refine-protocol-path",
                            str(fixture["protocol_path"]),
                            "--bundle-contract-path",
                            str(fixture["bundle_path"]),
                            "--output-suffix",
                            "robust-smoke",
                            "--max-concurrent-pairs",
                            "1",
                            "--no-docker-health-check",
                        ]
                    )

            self.assertEqual(exit_code, 1)
            self.assertEqual(len(seen_commands), 4)
            summary_path = (
                fixture["materialized_root"]
                / "launcher_logs"
                / "robust-smoke"
                / "summary.json"
            )
            self.assertTrue(summary_path.exists())
            summary = json.loads(summary_path.read_text())
            self.assertEqual(summary["total_pairs"], 4)
            self.assertEqual(summary["failed_pairs"], 1)
            self.assertEqual(summary["succeeded_pairs"], 3)
            failed = [item for item in summary["results"] if item["status"] == "failed"]
            self.assertEqual(len(failed), 1)
            self.assertEqual(failed[0]["pair_id"], "task-alpha__artifact-generation")
            self.assertEqual(failed[0]["returncode"], 17)
            failure_path = (
                fixture["materialized_root"]
                / "pairs"
                / "task-alpha__artifact-generation"
                / "refine_run_robust-smoke"
                / "run_failure.json"
            )
            self.assertTrue(failure_path.exists())
            failure_payload = json.loads(failure_path.read_text())
            self.assertEqual(failure_payload["launcher_stage"], "run")
            self.assertEqual(failure_payload["returncode"], 17)
            self.assertIn("launcher_logs/robust-smoke", stdout.getvalue())

    def test_main_aborts_early_when_docker_health_gate_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))

            with mock.patch.object(
                self.module,
                "probe_docker_health",
                return_value={
                    "healthy": False,
                    "category": "daemon_internal_error",
                    "message": "Docker daemon returned an internal API error",
                    "observed_at": "2026-04-13T00:00:00+00:00",
                },
            ):
                with mock.patch.object(self.module.subprocess, "run") as mock_run:
                    exit_code = self.module.main(
                        [
                            "2",
                            "--task-slice",
                            str(fixture["task_slice_path"]),
                            "--materialized-root",
                            str(fixture["materialized_root"]),
                            "--oauth-file",
                            str(fixture["oauth_file"]),
                            "--refine-protocol-path",
                            str(fixture["protocol_path"]),
                            "--bundle-contract-path",
                            str(fixture["bundle_path"]),
                            "--output-suffix",
                            "health-stop",
                            "--max-concurrent-pairs",
                            "1",
                            "--no-docker-auto-recover",
                        ]
                    )

            self.assertEqual(exit_code, 1)
            mock_run.assert_not_called()
            summary_path = fixture["materialized_root"] / "launcher_logs" / "health-stop" / "summary.json"
            summary = json.loads(summary_path.read_text())
            self.assertTrue(summary["aborted"])
            self.assertEqual(summary["failed_pairs"], 1)
            self.assertEqual(summary["completed_pairs"], 1)
            self.assertEqual(summary["results"][0]["stage"], "docker_health_gate")
            failure_path = (
                fixture["materialized_root"]
                / "pairs"
                / "task-alpha__analytic-pipeline"
                / "refine_run_health-stop"
                / "run_failure.json"
            )
            failure_payload = json.loads(failure_path.read_text())
            self.assertEqual(failure_payload["launcher_stage"], "docker_health_gate")
            self.assertEqual(failure_payload["docker_health_category"], "daemon_internal_error")

    def test_main_recovers_when_cleanup_restores_docker_health(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))

            probe_reports = [
                {
                    "healthy": False,
                    "category": "invalid_memory",
                    "message": "Docker info reported MemTotal=0 bytes",
                    "observed_at": "2026-04-13T00:00:00+00:00",
                },
                {
                    "healthy": True,
                    "category": "healthy",
                    "message": "ok",
                    "observed_at": "2026-04-13T00:00:05+00:00",
                },
                {
                    "healthy": True,
                    "category": "healthy",
                    "message": "ok",
                    "observed_at": "2026-04-13T00:00:10+00:00",
                },
            ]

            with mock.patch.object(self.module, "probe_docker_health", side_effect=probe_reports):
                with mock.patch.object(
                    self.module,
                    "attempt_docker_recovery",
                    return_value={
                        "attempted": True,
                        "observed_at": "2026-04-13T00:00:03+00:00",
                        "commands": [],
                        "successful": True,
                    },
                ) as mock_recovery:
                    with mock.patch.object(
                        self.module.subprocess,
                        "run",
                        return_value=mock.Mock(returncode=0),
                    ) as mock_run:
                        exit_code = self.module.main(
                            [
                                "1",
                                "--task-slice",
                                str(fixture["task_slice_path"]),
                                "--materialized-root",
                                str(fixture["materialized_root"]),
                                "--oauth-file",
                                str(fixture["oauth_file"]),
                                "--refine-protocol-path",
                                str(fixture["protocol_path"]),
                                "--bundle-contract-path",
                                str(fixture["bundle_path"]),
                                "--output-suffix",
                                "health-recover",
                                "--max-concurrent-pairs",
                                "1",
                                "--docker-auto-recover",
                            ]
                        )

            self.assertEqual(exit_code, 0)
            mock_recovery.assert_called_once()
            self.assertEqual(mock_run.call_count, 2)
            health_path = (
                fixture["materialized_root"]
                / "pairs"
                / "task-alpha__analytic-pipeline"
                / "refine_run_health-recover"
                / "docker_health.json"
            )
            recovery_path = health_path.with_name("docker_recovery.json")
            self.assertTrue(health_path.exists())
            self.assertTrue(recovery_path.exists())

    def test_main_recovers_with_fault_injected_docker_health(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))

            with mock.patch.dict(
                "os.environ",
                {
                    docker_health.FAKE_DOCKER_HEALTH_ENV: "internal_error_once,healthy_always",
                    docker_health.FAKE_DOCKER_RECOVERY_ENV: "success",
                },
                clear=False,
            ):
                with mock.patch.object(
                    self.module.subprocess,
                    "run",
                    return_value=mock.Mock(returncode=0),
                ) as mock_run:
                    exit_code = self.module.main(
                        [
                            "1",
                            "--task-slice",
                            str(fixture["task_slice_path"]),
                            "--materialized-root",
                            str(fixture["materialized_root"]),
                            "--oauth-file",
                            str(fixture["oauth_file"]),
                            "--refine-protocol-path",
                            str(fixture["protocol_path"]),
                            "--bundle-contract-path",
                            str(fixture["bundle_path"]),
                            "--output-suffix",
                            "fault-injected-recover",
                            "--max-concurrent-pairs",
                            "1",
                            "--docker-auto-recover",
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertEqual(mock_run.call_count, 2)
            health_path = (
                fixture["materialized_root"]
                / "pairs"
                / "task-alpha__analytic-pipeline"
                / "refine_run_fault-injected-recover"
                / "docker_health.json"
            )
            recovery_path = health_path.with_name("docker_recovery.json")
            self.assertTrue(health_path.exists())
            self.assertTrue(recovery_path.exists())
            health_payload = json.loads(health_path.read_text())
            recovery_payload = json.loads(recovery_path.read_text())
            self.assertTrue(health_payload["healthy"])
            self.assertTrue(health_payload["fault_injected"])
            self.assertEqual(health_payload["fault_injection_scenario"], "healthy")
            self.assertTrue(recovery_payload["successful"])
            self.assertTrue(recovery_payload["fault_injected"])

    def test_main_aborts_with_persistent_fault_injected_docker_health(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))

            with mock.patch.dict(
                "os.environ",
                {
                    docker_health.FAKE_DOCKER_HEALTH_ENV: "internal_error_always",
                    docker_health.FAKE_DOCKER_RECOVERY_ENV: "failure",
                },
                clear=False,
            ):
                with mock.patch.object(self.module.subprocess, "run") as mock_run:
                    exit_code = self.module.main(
                        [
                            "1",
                            "--task-slice",
                            str(fixture["task_slice_path"]),
                            "--materialized-root",
                            str(fixture["materialized_root"]),
                            "--oauth-file",
                            str(fixture["oauth_file"]),
                            "--refine-protocol-path",
                            str(fixture["protocol_path"]),
                            "--bundle-contract-path",
                            str(fixture["bundle_path"]),
                            "--output-suffix",
                            "fault-injected-stop",
                            "--max-concurrent-pairs",
                            "1",
                            "--docker-auto-recover",
                        ]
                    )

            self.assertEqual(exit_code, 1)
            mock_run.assert_not_called()
            summary_path = (
                fixture["materialized_root"]
                / "launcher_logs"
                / "fault-injected-stop"
                / "summary.json"
            )
            summary = json.loads(summary_path.read_text())
            self.assertTrue(summary["aborted"])
            self.assertEqual(summary["results"][0]["stage"], "docker_health_gate")
            self.assertTrue(summary["results"][0]["docker_recovery_attempted"])

    def test_main_continues_when_command_build_fails_for_one_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            seen_pair_ids: list[str] = []
            original_build = self.module.build_refine_command

            def fake_build(*args, **kwargs):
                pair_spec = args[0]
                pair_id = pair_spec["pair_id"]
                if pair_id == "task-alpha__artifact-generation":
                    raise RuntimeError("broken pair spec")
                return original_build(*args, **kwargs)

            def fake_run(command: list[str], cwd: str, check: bool) -> object:
                joined = " ".join(command)
                if "--task task-alpha" in joined and "analytic-pipeline" in joined:
                    seen_pair_ids.append("task-alpha__analytic-pipeline")
                elif "--task task-beta" in joined and "analytic-pipeline" in joined:
                    seen_pair_ids.append("task-beta__analytic-pipeline")
                elif "--task task-beta" in joined and "artifact-generation" in joined:
                    seen_pair_ids.append("task-beta__artifact-generation")
                return mock.Mock(returncode=0)

            with mock.patch.object(self.module, "build_refine_command", side_effect=fake_build):
                with mock.patch.object(self.module.subprocess, "run", side_effect=fake_run):
                    exit_code = self.module.main(
                        [
                            "2",
                            "--task-slice",
                            str(fixture["task_slice_path"]),
                            "--materialized-root",
                            str(fixture["materialized_root"]),
                            "--oauth-file",
                            str(fixture["oauth_file"]),
                            "--refine-protocol-path",
                            str(fixture["protocol_path"]),
                            "--bundle-contract-path",
                            str(fixture["bundle_path"]),
                            "--output-suffix",
                            "build-fail",
                            "--max-concurrent-pairs",
                            "1",
                            "--no-docker-health-check",
                        ]
                    )

            self.assertEqual(exit_code, 1)
            self.assertEqual(
                seen_pair_ids,
                [
                    "task-alpha__analytic-pipeline",
                    "task-beta__analytic-pipeline",
                    "task-beta__artifact-generation",
                ],
            )
            summary_path = (
                fixture["materialized_root"]
                / "launcher_logs"
                / "build-fail"
                / "summary.json"
            )
            self.assertTrue(summary_path.exists())
            summary = json.loads(summary_path.read_text())
            failed = [item for item in summary["results"] if item["status"] == "failed"]
            self.assertEqual(len(failed), 1)
            self.assertEqual(failed[0]["pair_id"], "task-alpha__artifact-generation")
            self.assertEqual(failed[0]["stage"], "build_command")
            self.assertIn("broken pair spec", failed[0]["error"])
            failure_path = (
                fixture["materialized_root"]
                / "pairs"
                / "task-alpha__artifact-generation"
                / "refine_run_build-fail"
                / "run_failure.json"
            )
            self.assertTrue(failure_path.exists())
            failure_payload = json.loads(failure_path.read_text())
            self.assertEqual(failure_payload["launcher_stage"], "build_command")
            self.assertIn("broken pair spec", failure_payload["error_message"])

    def test_main_runs_pairs_with_configured_parallelism(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            active = 0
            max_active = 0
            lock = threading.Lock()

            def fake_run(command: list[str], cwd: str, check: bool) -> object:
                nonlocal active, max_active
                with lock:
                    active += 1
                    max_active = max(max_active, active)
                try:
                    time.sleep(0.05)
                    return mock.Mock(returncode=0)
                finally:
                    with lock:
                        active -= 1

            with mock.patch.object(self.module.subprocess, "run", side_effect=fake_run):
                exit_code = self.module.main(
                    [
                        "2",
                        "--task-slice",
                        str(fixture["task_slice_path"]),
                        "--materialized-root",
                        str(fixture["materialized_root"]),
                        "--oauth-file",
                        str(fixture["oauth_file"]),
                        "--refine-protocol-path",
                        str(fixture["protocol_path"]),
                        "--bundle-contract-path",
                        str(fixture["bundle_path"]),
                        "--output-suffix",
                        "parallel-smoke",
                        "--max-concurrent-pairs",
                        "2",
                        "--no-docker-health-check",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(max_active, 2)
            summary_path = (
                fixture["materialized_root"]
                / "launcher_logs"
                / "parallel-smoke"
                / "summary.json"
            )
            summary = json.loads(summary_path.read_text())
            self.assertEqual(summary["max_concurrent_pairs"], 2)
            self.assertEqual(summary["succeeded_pairs"], 4)
            self.assertEqual(summary["failed_pairs"], 0)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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
            for schema_id in ("analytic-pipeline", "artifact-generation"):
                pair_dir = pairs_dir / f"{task_name}__{schema_id}"
                pair_dir.mkdir(parents=True)
                pair_spec = {
                    "pair_id": f"{task_name}__{schema_id}",
                    "task_name": task_name,
                    "schema_id": schema_id,
                    "pair_dir": str(pair_dir),
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

    def test_build_refine_command_uses_uv_and_explicit_protocol_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            _, pair_specs = self.module.load_materialized_pairs(fixture["materialized_root"])
            pair = next(spec for spec in pair_specs if spec["pair_id"] == "task-beta__artifact-generation")

            command = self.module.build_refine_command(
                pair,
                oauth_file=fixture["oauth_file"],
                round_budget=3,
                agent="claude-code",
                model="anthropic/claude-sonnet-4-5",
                refine_protocol_path=fixture["protocol_path"],
                bundle_contract_path=fixture["bundle_path"],
                output_suffix="smoke3",
            )

            command_text = " ".join(command)
            self.assertTrue(command[:3] == ["uv", "run", "python"])
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
            self.assertIn("launcher_logs/robust-smoke", stdout.getvalue())

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


if __name__ == "__main__":
    unittest.main()

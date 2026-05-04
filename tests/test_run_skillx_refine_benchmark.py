from __future__ import annotations

import importlib.util
import json
import os
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import path_setup
from skillx.c4ar.contracts import (
    NextSkillpackManifest,
    RoundDecisionArtifact,
    SessionEvidenceArtifact,
)
from skillx.c4ar.playbook_agent_runner import (
    PlaybookAgentExecutionError,
    PlaybookAgentTimeoutError,
)
from skillx.session_evidence import distill_session_logs


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "run_skillx_refine_benchmark.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("run_skillx_refine_benchmark", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RunSkillxRefineBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def _make_source_artifacts(
        self,
        *,
        starting_skillpack_dir: Path,
        starting_label: str = "C3",
        starting_bundle_path: Path | None = None,
    ):
        return self.module.SourceArtifacts(
            starting_skillpack_dir=starting_skillpack_dir,
            starting_label=starting_label,
            starting_bundle_path=starting_bundle_path,
            rewrite_manifest_path=None,
        )

    def _build_demo_refine_fixture(self, root: Path):
        task_root = root / "skillsbench" / "tasks" / "demo-task"
        skills_dir = task_root / "environment" / "skills" / "skill-a"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
        (task_root / "instruction.md").write_text("instr\n")
        (task_root / "task.toml").write_text("[agent]\n")
        (task_root / "tests").mkdir()
        (task_root / "tests" / "test.sh").write_text("echo ok\n")
        (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
        task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
        paths = self.module.ensure_refine_paths(root / "out", task.task_id)
        starting_skillpack_dir = root / "start" / "skillpack"
        (starting_skillpack_dir / "skill-a").mkdir(parents=True)
        (starting_skillpack_dir / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\ncustom\n")
        source = self._make_source_artifacts(
            starting_skillpack_dir=starting_skillpack_dir,
            starting_label="R0",
        )
        r0_row = self.module.make_round_zero_artifacts(task=task, paths=paths, source=source, tune_rows=[])
        protocols = self.module.ProtocolInputs(
            refine_protocol_path=root / "proto.md",
            bundle_contract_path=root / "bundle.md",
        )
        protocols.refine_protocol_path.write_text("proto\n")
        protocols.bundle_contract_path.write_text("bundle\n")
        return task, paths, r0_row, protocols

    def test_collect_tune_evidence_from_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "run-a"
            (run_dir / "results").mkdir(parents=True)
            payload = [
                {"task_id": "task-a", "condition": "c1", "reward": 0.4},
                {"task_id": "task-a", "condition": "c3", "reward": 0.9},
                {"task_id": "task-b", "condition": "c2", "reward": 1.0},
            ]
            (run_dir / "results" / "benchmark_summary.json").write_text(json.dumps(payload))
            rows = self.module.collect_tune_evidence("task-a", [run_dir])
            self.assertEqual([row["condition"] for row in rows], ["c1", "c3"])
            self.assertTrue(all(row["source_run_dir"] == str(run_dir) for row in rows))

    def test_select_final_candidate_prefers_earliest_on_tie(self) -> None:
        rows = [
            {"round_index": 0, "reward": 0.8},
            {"round_index": 1, "reward": 0.9},
            {"round_index": 2, "reward": 0.9},
        ]
        selected = self.module.select_final_candidate(rows)
        self.assertEqual(selected["round_index"], 1)

    def test_derive_completed_run_status_marks_runtime_failures(self) -> None:
        round_rows = [
            {
                "round_index": 0,
                "reward": 0.0,
                "classification": {"kind": "runtime_failure", "reason": "exception_stats_present"},
            },
            {
                "round_index": 1,
                "reward": 0.25,
                "classification": {"kind": "clean_success", "reason": "positive_reward_with_no_exception_stats"},
            },
        ]

        status, details = self.module.derive_completed_run_status(round_rows)

        self.assertEqual(status, "completed_with_runtime_failures")
        self.assertEqual(details["selected_round"], "R1")
        self.assertEqual(details["selected_reward"], 0.25)
        self.assertEqual(details["selected_classification"], "clean_success")
        self.assertEqual(details["runtime_failure_rounds"], "R0")

    def test_resolve_benchmark_agent_name_infers_from_model(self) -> None:
        self.assertEqual(
            self.module.resolve_benchmark_agent_name(agent_name=None, model_name="anthropic/claude-sonnet-4-5"),
            "claude-code",
        )
        self.assertEqual(
            self.module.resolve_benchmark_agent_name(agent_name=None, model_name="openai/gpt-5.2-codex"),
            "codex",
        )

    def test_resolve_benchmark_agent_name_rejects_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            self.module.resolve_benchmark_agent_name(
                agent_name="claude-code",
                model_name="openai/gpt-5.2-codex",
            )

    def test_main_writes_structured_run_failure_for_setup_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            source_run_dir = root / "source"
            source_run_dir.mkdir(parents=True)
            oauth_file = root / "oauth.json"
            oauth_file.write_text("token\n")
            protocol_path = root / "refine.md"
            protocol_path.write_text("protocol\n")
            bundle_path = root / "bundle.md"
            bundle_path.write_text("bundle\n")

            with mock.patch.object(self.module, "discover_task_inputs", side_effect=FileNotFoundError("missing task inputs")):
                with mock.patch.object(
                    sys,
                    "argv",
                    [
                        "run_skillx_refine_benchmark.py",
                        "--skillsbench-root",
                        str(root / "skillsbench"),
                        "--task",
                        "demo-task",
                        "--run-id",
                        "demo-run",
                        "--output-dir",
                        str(output_dir),
                        "--oauth-file",
                        str(oauth_file),
                        "--source-run-dir",
                        str(source_run_dir),
                        "--refine-protocol-path",
                        str(protocol_path),
                        "--bundle-contract-path",
                        str(bundle_path),
                        "--orchestration-mode",
                        "c4ar",
                    ],
                ):
                    with self.assertRaises(FileNotFoundError):
                        self.module.main()

            failure_payload = json.loads((output_dir / "run_failure.json").read_text())
            self.assertEqual(failure_payload["error_type"], "FileNotFoundError")
            self.assertEqual(failure_payload["failed_stage"], "discover_task_inputs")
            self.assertEqual(failure_payload["run_id"], "demo-run")

    def test_build_job_config_infers_agent_from_model_when_unspecified(self) -> None:
        payload = self.module.build_job_config(
            job_name="demo-job",
            jobs_dir=Path("/tmp/jobs"),
            task_path=Path("/tmp/task"),
            agent_name=None,
            model_name="openai/gpt-5.2-codex",
            timeout_multiplier=1.0,
            n_concurrent_trials=1,
        )
        self.assertIsNone(payload["agents"][0]["name"])
        self.assertEqual(payload["agents"][0]["import_path"], "skillx.harbor_agents:AuthBackedCodex")

    def test_build_job_config_uses_custom_claude_agent_wrapper(self) -> None:
        payload = self.module.build_job_config(
            job_name="demo-job",
            jobs_dir=Path("/tmp/jobs"),
            task_path=Path("/tmp/task"),
            agent_name=None,
            model_name="anthropic/claude-sonnet-4-5",
            timeout_multiplier=1.0,
            n_concurrent_trials=1,
        )
        self.assertIsNone(payload["agents"][0]["name"])
        self.assertEqual(
            payload["agents"][0]["import_path"],
            "skillx.harbor_agents:AuthBackedClaudeCode",
        )

    def test_build_job_config_can_keep_harbor_images(self) -> None:
        payload = self.module.build_job_config(
            job_name="demo-job",
            jobs_dir=Path("/tmp/jobs"),
            task_path=Path("/tmp/task"),
            agent_name="claude-code",
            model_name="anthropic/claude-sonnet-4-5",
            timeout_multiplier=1.0,
            n_concurrent_trials=1,
            keep_harbor_images=True,
        )

        self.assertFalse(payload["environment"]["delete"])

    def test_build_arg_parser_defaults_tune_timeout_multiplier_to_one(self) -> None:
        parser = self.module.build_arg_parser()
        args = parser.parse_args(
            [
                "--skillsbench-root",
                "/tmp/skillsbench",
                "--task",
                "demo-task",
                "--run-id",
                "run-001",
                "--output-dir",
                "/tmp/out",
                "--source-run-dir",
                "/tmp/source",
            ]
        )
        self.assertEqual(args.tune_timeout_multiplier, 1.0)

    def test_find_executor_session_log_path_accepts_codex_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trial_dir = Path(tmpdir) / "trial-001"
            agent_dir = trial_dir / "agent"
            agent_dir.mkdir(parents=True)
            codex_log = agent_dir / "codex.txt"
            codex_log.write_text("{\"event\":\"done\"}\n")

            self.assertEqual(self.module.find_executor_session_log_path(trial_dir), codex_log)

    def test_check_environment_for_codex_requires_auth_file_but_not_oauth(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skillsbench_root = Path(tmpdir) / "skillsbench"
            skillsbench_root.mkdir()
            codex_home = Path(tmpdir) / "codex-home"
            (codex_home / ".codex").mkdir(parents=True)
            auth_file = codex_home / ".codex" / "auth.json"
            auth_file.write_text('{"auth_mode":"chatgpt","tokens":{"access_token":"x"}}\n')
            with mock.patch.object(self.module.Path, "home", return_value=codex_home):
                with mock.patch.object(
                    self.module,
                    "probe_docker_health",
                    return_value={
                        "healthy": True,
                        "category": "healthy",
                        "message": "ok",
                        "docker_mem_bytes": 17179869184,
                    },
                ):
                    with mock.patch.object(self.module.shutil, "which", return_value="/usr/bin/uv"):
                        payload = self.module.check_environment(
                            skillsbench_root,
                            oauth_file=None,
                            agent_name="codex",
                        )

            self.assertEqual(payload["benchmark_agent"], "codex")
            self.assertIsNone(payload["oauth_file"])
            self.assertEqual(payload["codex_auth_file"], str(auth_file))
            self.assertEqual(payload["docker_health_category"], "healthy")

    def test_check_environment_raises_clear_error_when_docker_unhealthy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skillsbench_root = Path(tmpdir) / "skillsbench"
            skillsbench_root.mkdir()
            oauth_file = Path(tmpdir) / "oauth.txt"
            oauth_file.write_text("token\n")

            with mock.patch.object(
                self.module,
                "probe_docker_health",
                return_value={
                    "healthy": False,
                    "category": "daemon_internal_error",
                    "message": "Docker daemon returned an internal API error",
                    "docker_mem_bytes": 0,
                },
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    self.module.check_environment(
                        skillsbench_root,
                        oauth_file=oauth_file,
                        agent_name="claude-code",
                    )

            self.assertIn("Docker health check failed", str(ctx.exception))

    def test_build_job_config_records_environment_overrides(self) -> None:
        payload = self.module.build_job_config(
            job_name="demo-job",
            jobs_dir=Path("/tmp/jobs"),
            task_path=Path("/tmp/task"),
            agent_name="codex",
            model_name="openai/gpt-5.2-codex",
            timeout_multiplier=1.0,
            n_concurrent_trials=1,
            override_memory_mb=8192,
            override_storage_mb=12288,
        )
        self.assertEqual(payload["environment"]["override_memory_mb"], 8192)
        self.assertEqual(payload["environment"]["override_storage_mb"], 12288)

    def test_render_refine_task_toml_uses_override_limits(self) -> None:
        payload = self.module.render_refine_task_toml(memory_mb=8192, storage_mb=12288)
        self.assertIn("memory_mb = 8192", payload)
        self.assertIn("storage_mb = 12288", payload)

    def test_make_round_zero_artifacts_copies_c3_skillpack(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            c3_dir = root / "source-run" / "rewrite_jobs" / "demo-task" / "outputs" / "materialized_skillpacks" / "demo-task" / "c3_derived" / "skill-a"
            c3_dir.mkdir(parents=True)
            (c3_dir / "SKILL.md").write_text("# Derived Execution Layer\nrefined\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            source = self._make_source_artifacts(starting_skillpack_dir=c3_dir.parent)
            row = self.module.make_round_zero_artifacts(task=task, paths=paths, source=source, tune_rows=[])
            copied = paths.rounds_dir / "round-0" / "skillpack" / "skills" / "skill-a" / "SKILL.md"
            self.assertTrue(copied.exists())
            self.assertIn("# Derived Execution Layer", copied.read_text())
            self.assertIsNone(row["reward"])

    def test_discover_task_inputs_ignores_non_skill_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skill_a = task_root / "environment" / "skills" / "skill-a"
            skill_b = task_root / "environment" / "skills" / "skill-b"
            licenses = task_root / "environment" / "skills" / "licenses"
            skill_a.mkdir(parents=True)
            skill_b.mkdir(parents=True)
            licenses.mkdir(parents=True)
            (skill_a / "SKILL.md").write_text("a\n")
            (skill_b / "SKILL.md").write_text("b\n")
            (licenses / "obspy.LICENSE").write_text("license\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            self.assertEqual(task.skill_names, ["skill-a", "skill-b"])

    def test_discover_task_inputs_accepts_tasks_without_test_outputs_py(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("demo\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            tests_dir = task_root / "tests"
            tests_dir.mkdir()
            (tests_dir / "test.sh").write_text("pytest /tests/test_setup.py\n")
            (tests_dir / "testing_utils.py").write_text("HELPER = True\n")
            (tests_dir / "test_setup.py").write_text("def test_ok():\n    assert True\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            self.assertEqual(task.tests_dir, tests_dir)
            self.assertEqual(task.skill_names, ["skill-a"])

    def test_write_static_bundle_ignores_non_skill_directories_in_starting_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skill_a = task_root / "environment" / "skills" / "skill-a"
            skill_b = task_root / "environment" / "skills" / "skill-b"
            licenses = task_root / "environment" / "skills" / "licenses"
            skill_a.mkdir(parents=True)
            skill_b.mkdir(parents=True)
            licenses.mkdir(parents=True)
            (skill_a / "SKILL.md").write_text("a\n")
            (skill_b / "SKILL.md").write_text("b\n")
            (licenses / "obspy.LICENSE").write_text("license\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            starting_skillpack_dir = root / "start" / "skillpack"
            (starting_skillpack_dir / "skill-a").mkdir(parents=True)
            (starting_skillpack_dir / "skill-b").mkdir(parents=True)
            (starting_skillpack_dir / "licenses").mkdir(parents=True)
            (starting_skillpack_dir / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\na\n")
            (starting_skillpack_dir / "skill-b" / "SKILL.md").write_text("# Derived Execution Layer\nb\n")
            (starting_skillpack_dir / "licenses" / "seisbench.LICENSE").write_text("license\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            source = self._make_source_artifacts(starting_skillpack_dir=starting_skillpack_dir)
            (root / "protocol.md").write_text("protocol\n")
            (root / "bundle.md").write_text("bundle\n")

            self.module.write_static_bundle(
                task=task,
                paths=paths,
                protocols=self.module.ProtocolInputs(
                    refine_protocol_path=root / "protocol.md",
                    bundle_contract_path=root / "bundle.md",
                ),
                source=source,
                tune_rows=[],
                tune_run_dirs=[root / "run-a"],
                round_budget=3,
                source_run_dir=root / "source",
                session_evidence=None,
            )

            copied_root = paths.static_dir / "ancestry" / "current_starting_skillpack"
            self.assertTrue((copied_root / "skill-a" / "SKILL.md").exists())
            self.assertTrue((copied_root / "skill-b" / "SKILL.md").exists())
            self.assertFalse((copied_root / "licenses").exists())

    def test_write_static_bundle_copies_full_tests_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("demo\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            tests_dir = task_root / "tests"
            tests_dir.mkdir()
            (tests_dir / "test.sh").write_text("pytest /tests/test_setup.py\n")
            (tests_dir / "testing_utils.py").write_text("HELPER = True\n")
            (tests_dir / "test_setup.py").write_text("def test_ok():\n    assert True\n")

            starting_skillpack_dir = root / "start" / "skillpack" / "skill-a"
            starting_skillpack_dir.mkdir(parents=True)
            (starting_skillpack_dir / "SKILL.md").write_text("# Derived Execution Layer\ndemo\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            source = self._make_source_artifacts(starting_skillpack_dir=starting_skillpack_dir.parent)
            (root / "protocol.md").write_text("protocol\n")
            (root / "bundle.md").write_text("bundle\n")

            self.module.write_static_bundle(
                task=task,
                paths=paths,
                protocols=self.module.ProtocolInputs(
                    refine_protocol_path=root / "protocol.md",
                    bundle_contract_path=root / "bundle.md",
                ),
                source=source,
                tune_rows=[],
                tune_run_dirs=[root / "run-a"],
                round_budget=3,
                source_run_dir=root / "source",
                session_evidence=None,
            )

            copied_tests_dir = paths.static_dir / "task_context" / "tests"
            self.assertTrue((copied_tests_dir / "test.sh").exists())
            self.assertTrue((copied_tests_dir / "testing_utils.py").exists())
            self.assertTrue((copied_tests_dir / "test_setup.py").exists())
            self.assertFalse((copied_tests_dir / "test_outputs.py").exists())

    def test_make_round_zero_artifacts_ignores_non_skill_directories_in_starting_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skill_a = task_root / "environment" / "skills" / "skill-a"
            licenses = task_root / "environment" / "skills" / "licenses"
            skill_a.mkdir(parents=True)
            licenses.mkdir(parents=True)
            (skill_a / "SKILL.md").write_text("original\n")
            (licenses / "obspy.LICENSE").write_text("license\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            starting_skillpack_dir = root / "start" / "skillpack"
            (starting_skillpack_dir / "skill-a").mkdir(parents=True)
            (starting_skillpack_dir / "licenses").mkdir(parents=True)
            (starting_skillpack_dir / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\ncustom\n")
            (starting_skillpack_dir / "licenses" / "seisbench.LICENSE").write_text("license\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            source = self._make_source_artifacts(starting_skillpack_dir=starting_skillpack_dir)

            self.module.make_round_zero_artifacts(task=task, paths=paths, source=source, tune_rows=[])

            copied = paths.rounds_dir / "round-0" / "skillpack" / "skills" / "skill-a" / "SKILL.md"
            self.assertTrue(copied.exists())
            self.assertFalse((paths.rounds_dir / "round-0" / "skillpack" / "skills" / "licenses").exists())

    def test_make_round_zero_artifacts_fails_clearly_when_starting_pack_is_missing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skill_a = task_root / "environment" / "skills" / "skill-a"
            skill_b = task_root / "environment" / "skills" / "skill-b"
            skill_a.mkdir(parents=True)
            skill_b.mkdir(parents=True)
            (skill_a / "SKILL.md").write_text("a\n")
            (skill_b / "SKILL.md").write_text("b\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            starting_skillpack_dir = root / "start" / "skillpack"
            (starting_skillpack_dir / "skill-a").mkdir(parents=True)
            (starting_skillpack_dir / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\na\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            source = self._make_source_artifacts(starting_skillpack_dir=starting_skillpack_dir)

            with self.assertRaisesRegex(FileNotFoundError, "starting skillpack missing required skill file"):
                self.module.make_round_zero_artifacts(task=task, paths=paths, source=source, tune_rows=[])

    def test_locate_source_artifacts_uses_explicit_starting_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_run_dir = root / "source-run"
            (source_run_dir / "rewrite_jobs" / "demo-task" / "outputs" / "rewrite_manifest.json").parent.mkdir(
                parents=True
            )
            (source_run_dir / "rewrite_jobs" / "demo-task" / "outputs" / "rewrite_manifest.json").write_text("{}\n")
            explicit_skillpack_dir = root / "r0-skillpack"
            (explicit_skillpack_dir / "skill-a").mkdir(parents=True)
            (explicit_skillpack_dir / "skill-a" / "SKILL.md").write_text("explicit\n")
            explicit_bundle_path = root / "r0-bundle.yaml"
            explicit_bundle_path.write_text("bundle: true\n")

            source = self.module.locate_source_artifacts(
                "demo-task",
                source_run_dir,
                starting_skillpack_dir=explicit_skillpack_dir,
                starting_bundle_path=explicit_bundle_path,
                starting_label="R0",
            )

            self.assertEqual(source.starting_skillpack_dir, explicit_skillpack_dir)
            self.assertEqual(source.starting_label, "R0")
            self.assertEqual(source.starting_bundle_path, explicit_bundle_path)

    def test_locate_source_artifacts_defaults_custom_starting_pack_to_r0_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_run_dir = root / "source-run"
            (source_run_dir / "rewrite_jobs" / "demo-task" / "outputs" / "rewrite_manifest.json").parent.mkdir(
                parents=True
            )
            (source_run_dir / "rewrite_jobs" / "demo-task" / "outputs" / "rewrite_manifest.json").write_text("{}\n")
            explicit_skillpack_dir = root / "c2_class_aware"
            (explicit_skillpack_dir / "skill-a").mkdir(parents=True)
            (explicit_skillpack_dir / "skill-a" / "SKILL.md").write_text("explicit\n")

            source = self.module.locate_source_artifacts(
                "demo-task",
                source_run_dir,
                starting_skillpack_dir=explicit_skillpack_dir,
            )

            self.assertEqual(source.starting_skillpack_dir, explicit_skillpack_dir)
            self.assertEqual(source.starting_label, "R0")
            self.assertIsNone(source.starting_bundle_path)

    def test_make_round_zero_artifacts_uses_explicit_starting_pack_and_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            starting_skillpack_dir = root / "start" / "skillpack"
            (starting_skillpack_dir / "skill-a").mkdir(parents=True)
            (starting_skillpack_dir / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\ncustom\n")
            starting_bundle_path = root / "start" / "bundle.yaml"
            starting_bundle_path.write_text("bundle: true\n")
            source = self._make_source_artifacts(
                starting_skillpack_dir=starting_skillpack_dir,
                starting_label="R0",
                starting_bundle_path=starting_bundle_path,
            )

            self.module.make_round_zero_artifacts(task=task, paths=paths, source=source, tune_rows=[])

            copied = paths.rounds_dir / "round-0" / "skillpack" / "skills" / "skill-a" / "SKILL.md"
            self.assertTrue(copied.exists())
            self.assertIn("custom", copied.read_text())
            self.assertTrue((paths.rounds_dir / "round-0" / "skillpack_bundle.yaml").exists())
            self.assertIn("R0", (paths.rounds_dir / "round-0" / "round_0_refine_memo.md").read_text())
            self.assertIn("R0", (paths.rounds_dir / "round-0" / "round_0_risk_note.md").read_text())

    def test_write_bundle_manifest_contains_round_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            source = self._make_source_artifacts(
                starting_skillpack_dir=root
                / "source-run"
                / "rewrite_jobs"
                / "demo-task"
                / "outputs"
                / "materialized_skillpacks"
                / "demo-task"
                / "c3_derived",
            )
            self.module.write_bundle_manifest(
                paths=paths,
                task=task,
                source_run_dir=root / "source",
                source=source,
                tune_run_dirs=[root / "run-a"],
                round_budget=4,
                rounds=[{"round_index": 0, "reward": 0.7}],
            )
            payload = json.loads(paths.manifest_path.read_text())
            self.assertEqual(payload["round_budget"], 4)
            self.assertEqual(payload["starting_artifact"], "C3")
            self.assertEqual(payload["starting_label"], "C3")
            self.assertEqual(payload["starting_skillpack_dir"], str(source.starting_skillpack_dir))

    def test_write_bundle_manifest_records_explicit_starting_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            explicit_skillpack_dir = root / "start" / "skillpack"
            (explicit_skillpack_dir / "skill-a").mkdir(parents=True)
            (explicit_skillpack_dir / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\ncustom\n")
            explicit_bundle_path = root / "start" / "bundle.yaml"
            explicit_bundle_path.write_text("bundle: true\n")
            source = self._make_source_artifacts(
                starting_skillpack_dir=explicit_skillpack_dir,
                starting_label="R0",
                starting_bundle_path=explicit_bundle_path,
            )

            self.module.write_bundle_manifest(
                paths=paths,
                task=task,
                source_run_dir=root / "source",
                source=source,
                tune_run_dirs=[root / "run-a"],
                round_budget=2,
                rounds=[{"round_index": 0, "reward": 0.2}],
            )

            payload = json.loads(paths.manifest_path.read_text())
            self.assertEqual(payload["starting_artifact"], "R0")
            self.assertEqual(payload["starting_label"], "R0")
            self.assertEqual(payload["starting_skillpack_dir"], str(explicit_skillpack_dir))
            self.assertEqual(payload["starting_bundle_path"], str(explicit_bundle_path))

    def test_write_static_bundle_attaches_session_evidence_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            c3_dir = root / "source-run" / "rewrite_jobs" / "demo-task" / "outputs" / "materialized_skillpacks" / "demo-task" / "c3_derived" / "skill-a"
            c3_dir.mkdir(parents=True)
            (c3_dir / "SKILL.md").write_text("# Derived Execution Layer\nrefined\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            source = self._make_source_artifacts(starting_skillpack_dir=c3_dir.parent)
            session_evidence = self.module.SessionDerivedEvidence(
                source_paths=(str(root / "session.log"),),
                dominant_failure_pattern="repeated loop / low-progress churn",
                wasted_loop_signals=["Repeated wasted loop 3x: tool_use edit"],
                tool_misuse_signals=["Tool misuse: wrong tool"],
                critical_turns=["Critical turn: timeout"],
                skill_misguidance_signals=["Skill misguidance: too verbose"],
                recommended_edit_targets=["compress_derived_layer", "tighten_scope_boundary"],
                evidence_refs=[f"{root / 'session.log'}:12"],
                observed_at="2026-03-25T00:00:00+00:00",
            )
            (root / "protocol.md").write_text("protocol\n")
            (root / "bundle.md").write_text("bundle\n")
            self.module.write_static_bundle(
                task=task,
                paths=paths,
                protocols=self.module.ProtocolInputs(
                    refine_protocol_path=root / "protocol.md",
                    bundle_contract_path=root / "bundle.md",
                ),
                source=source,
                tune_rows=[
                    {
                        "condition": "c3",
                        "reward": 0.7,
                        "result_path": "/tmp/c3/result.json",
                        "source_run_dir": "/tmp/source",
                        "exception_stats": {},
                    }
                ],
                tune_run_dirs=[root / "run-a"],
                round_budget=3,
                source_run_dir=root / "source",
                session_evidence=session_evidence,
            )
            session_dir = paths.static_dir / "session_evidence"
            self.assertTrue((session_dir / "session_evidence.json").exists())
            self.assertTrue((session_dir / "session_evidence.md").exists())
            self.assertIn("repeated loop", (session_dir / "session_evidence.md").read_text())
            self.assertIn(
                "starting_artifact: `C3`",
                (paths.static_dir / "constraints" / "refine_constraints.md").read_text(),
            )

    def test_write_static_bundle_records_explicit_starting_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            explicit_skillpack_dir = root / "start" / "skillpack"
            (explicit_skillpack_dir / "skill-a").mkdir(parents=True)
            (explicit_skillpack_dir / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\ncustom\n")
            explicit_bundle_path = root / "start" / "bundle.yaml"
            explicit_bundle_path.write_text("bundle: true\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            source = self._make_source_artifacts(
                starting_skillpack_dir=explicit_skillpack_dir,
                starting_label="R0",
                starting_bundle_path=explicit_bundle_path,
            )
            (root / "protocol.md").write_text("protocol\n")
            (root / "bundle.md").write_text("bundle\n")

            self.module.write_static_bundle(
                task=task,
                paths=paths,
                protocols=self.module.ProtocolInputs(
                    refine_protocol_path=root / "protocol.md",
                    bundle_contract_path=root / "bundle.md",
                ),
                source=source,
                tune_rows=[
                    {
                        "condition": "r0",
                        "reward": 0.7,
                        "result_path": "/tmp/r0/result.json",
                        "source_run_dir": "/tmp/source",
                        "exception_stats": {},
                    }
                ],
                tune_run_dirs=[root / "run-a"],
                round_budget=3,
                source_run_dir=root / "source",
                session_evidence=None,
            )

            constraints = (paths.static_dir / "constraints" / "refine_constraints.md").read_text()
            self.assertIn("starting_artifact: `R0`", constraints)
            self.assertIn(str(explicit_skillpack_dir), constraints)
            self.assertIn(str(explicit_bundle_path), constraints)

    def test_round_decision_context_is_bounded_and_copied_forward(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            session_evidence = self.module.SessionDerivedEvidence(
                source_paths=(str(root / "session.log"),),
                dominant_failure_pattern="repeated loop / low-progress churn",
                wasted_loop_signals=["Repeated wasted loop 3x: tool_use edit"],
                tool_misuse_signals=[],
                critical_turns=[],
                skill_misguidance_signals=["Skill misguidance: too verbose"],
                recommended_edit_targets=["compress_derived_layer", "remove_speculative_evaluator_content"],
                evidence_refs=[f"{root / 'session.log'}:12"],
                observed_at="2026-03-25T00:00:00+00:00",
            )
            tune_rows = [
                {
                    "condition": "c3",
                    "reward": 0.7,
                    "result_path": "/tmp/c3/result.json",
                    "source_run_dir": "/tmp/source",
                    "exception_stats": {},
                }
            ]
            c3_dir = root / "source-run" / "rewrite_jobs" / "demo-task" / "outputs" / "materialized_skillpacks" / "demo-task" / "c3_derived" / "skill-a"
            c3_dir.mkdir(parents=True)
            (c3_dir / "SKILL.md").write_text("# Derived Execution Layer\nrefined\n")
            source = self._make_source_artifacts(starting_skillpack_dir=c3_dir.parent)
            (root / "protocol.md").write_text("protocol\n")
            (root / "bundle.md").write_text("bundle\n")
            self.module.write_static_bundle(
                task=task,
                paths=paths,
                protocols=self.module.ProtocolInputs(
                    refine_protocol_path=root / "protocol.md",
                    bundle_contract_path=root / "bundle.md",
                ),
                source=source,
                tune_rows=tune_rows,
                tune_run_dirs=[root / "run-a"],
                round_budget=3,
                source_run_dir=root / "source",
                session_evidence=session_evidence,
            )
            round_dir = paths.rounds_dir / "round-0"
            (round_dir / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_dir / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\nrefined\n")
            (round_dir / "session_logs").mkdir()
            (round_dir / "session_logs" / "raw.log").write_text("full raw log that should not be copied\n")
            context = self.module.write_round_context_artifacts(
                task=task,
                round_index=0,
                source_run_dir=root / "source",
                round_rows=[
                    self.module.build_round_row(
                        0,
                        round_dir,
                        {
                            "reward": 0.9,
                            "exception_stats": {},
                            "eval_name": "demo",
                        },
                    )
                ],
                tune_rows=tune_rows,
                paths=paths,
                session_evidence=session_evidence,
            )
            paths.ledger_path.write_text("# Refine Ledger\n\n")
            decision_dir = round_dir / "decision_context"
            self.assertTrue((decision_dir / "round_0_evidence_bundle.json").exists())
            self.assertTrue((decision_dir / "round_0_decision.json").exists())
            self.assertEqual(context["refine_intent"]["primary_action"], "compress_derived_layer")
            self.assertTrue(context["disposition"]["keep_candidate"])

            target_dir = root / "next-round-inputs"
            protocols = self.module.ProtocolInputs(
                refine_protocol_path=root / "protocol.md",
                bundle_contract_path=root / "bundle.md",
            )
            self.module.populate_refine_inputs_dir(
                task=task,
                paths=paths,
                protocols=protocols,
                target_dir=target_dir,
                previous_round_dir=round_dir,
            )
            self.assertTrue((target_dir / "decision_context" / "round_0_evidence_bundle.json").exists())
            self.assertTrue((target_dir / "decision_context" / "round_0_decision.json").exists())
            self.assertTrue((target_dir / "static" / "session_evidence" / "session_evidence.json").exists())
            self.assertFalse((target_dir / "session_logs" / "raw.log").exists())

    def test_existing_tune_result_recovers_nested_harbor_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            round_dir = root / "round-1"
            tune_root = round_dir / "tune_check"
            tune_root.mkdir(parents=True)
            (tune_root / "config.json").write_text(
                json.dumps({"job_name": "demo-task-round-1-c4-tune"})
            )
            job_dir = tune_root / "demo-task-round-1-c4-tune"
            job_dir.mkdir()
            (job_dir / "result.json").write_text(
                json.dumps(
                    {
                        "stats": {
                            "evals": {
                                "demo": {
                                    "metrics": [{"mean": 0.6}],
                                    "exception_stats": {},
                                }
                            }
                        }
                    }
                )
            )
            row = self.module.existing_tune_result(
                task_id="demo-task",
                round_dir_path=round_dir,
                skill_source="/tmp/skillpack",
            )
            self.assertIsNotNone(row)
            self.assertEqual(row["reward"], 0.6)
            self.assertTrue((tune_root / "result.json").exists())

    def test_parse_job_result_normalizes_false_claude_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            job_dir = Path(tmpdir) / "job-a"
            trial_dir = job_dir / "trial-a"
            (trial_dir / "agent").mkdir(parents=True)
            (job_dir / "result.json").write_text(
                json.dumps(
                    {
                        "stats": {
                            "evals": {
                                "demo": {
                                    "metrics": [{"mean": 0.5}],
                                    "exception_stats": {
                                        "AgentTimeoutError": ["trial-a"],
                                    },
                                }
                            }
                        }
                    }
                )
            )
            (trial_dir / "result.json").write_text(
                json.dumps(
                    {
                        "verifier_result": {"rewards": {"reward": 0.5}},
                        "exception_info": {
                            "exception_type": "AgentTimeoutError",
                        },
                    }
                )
            )
            (trial_dir / "agent" / "claude-code.txt").write_text(
                '{"type":"result","subtype":"success","is_error":false}\n'
            )

            row = self.module.parse_job_result(
                job_dir,
                condition="c4",
                task_id="demo-task",
                skill_source="/tmp/skillpack",
            )
            self.assertEqual(row["reward"], 0.5)
            self.assertEqual(row["exception_stats"], {})

    def test_existing_tune_result_rewrites_cached_false_timeout_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            round_dir = root / "round-1"
            tune_root = round_dir / "tune_check"
            tune_root.mkdir(parents=True)
            (tune_root / "config.json").write_text(
                json.dumps({"job_name": "demo-task-round-1-c4-tune"})
            )
            (tune_root / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "reward": 0.5,
                        "exception_stats": {"AgentTimeoutError": ["trial-a"]},
                    }
                )
            )
            job_dir = tune_root / "demo-task-round-1-c4-tune"
            trial_dir = job_dir / "trial-a"
            (trial_dir / "agent").mkdir(parents=True)
            (job_dir / "result.json").write_text(
                json.dumps(
                    {
                        "stats": {
                            "evals": {
                                "demo": {
                                    "metrics": [{"mean": 0.5}],
                                    "exception_stats": {
                                        "AgentTimeoutError": ["trial-a"],
                                    },
                                }
                            }
                        }
                    }
                )
            )
            (trial_dir / "result.json").write_text(
                json.dumps(
                    {
                        "verifier_result": {"rewards": {"reward": 0.5}},
                        "exception_info": {
                            "exception_type": "AgentTimeoutError",
                        },
                    }
                )
            )
            (trial_dir / "agent" / "claude-code.txt").write_text(
                '{"type":"result","subtype":"success","is_error":false}\n'
            )

            row = self.module.existing_tune_result(
                task_id="demo-task",
                round_dir_path=round_dir,
                skill_source="/tmp/skillpack",
            )
            self.assertIsNotNone(row)
            self.assertEqual(row["exception_stats"], {})
            self.assertEqual(
                json.loads((tune_root / "result.json").read_text())["exception_stats"],
                {},
            )

    def test_run_round_tune_check_retries_timeout_once_with_double_multiplier(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            round_dir = root / "round-1"
            (round_dir / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_dir / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("candidate\n")
            sandbox_dir = root / "sandbox"
            sandbox_dir.mkdir()

            seen_multipliers: list[float] = []
            seen_deletes: list[bool] = []
            attempt_results = [
                {
                    "reward": 0.1,
                    "eval_name": "pytest",
                    "exception_stats": {"AgentTimeoutError": ["trial-a"]},
                    "n_trials": 1,
                    "n_errors": 1,
                },
                {
                    "reward": 0.9,
                    "eval_name": "pytest",
                    "exception_stats": {},
                    "n_trials": 1,
                    "n_errors": 0,
                },
            ]

            original_materialize = self.module.materialize_c4_sandbox
            original_run_harbor_job = self.module.run_harbor_job
            original_parse_job_result = self.module.parse_job_result
            try:
                self.module.materialize_c4_sandbox = lambda *args, **kwargs: sandbox_dir

                def fake_run_harbor_job(**kwargs):
                    config_payload = json.loads(Path(kwargs["config_path"]).read_text())
                    seen_multipliers.append(config_payload["timeout_multiplier"])
                    seen_deletes.append(config_payload["environment"]["delete"])

                def fake_parse_job_result(*args, **kwargs):
                    return attempt_results.pop(0)

                self.module.run_harbor_job = fake_run_harbor_job
                self.module.parse_job_result = fake_parse_job_result

                result = self.module.run_round_tune_check(
                    task=task,
                    run_dir=root / "out",
                    round_dir_path=round_dir,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    timeout_multiplier=1.0,
                    keep_harbor_images=True,
                )
            finally:
                self.module.materialize_c4_sandbox = original_materialize
                self.module.run_harbor_job = original_run_harbor_job
                self.module.parse_job_result = original_parse_job_result

            self.assertEqual(seen_multipliers, [1.0, 2.0])
            self.assertEqual(seen_deletes, [False, False])
            self.assertEqual(result["reward"], 0.9)
            self.assertEqual(
                json.loads((round_dir / "tune_check" / "result.json").read_text())["reward"],
                0.9,
            )

    def test_run_round_tune_check_stops_after_second_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            round_dir = root / "round-1"
            (round_dir / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_dir / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("candidate\n")
            sandbox_dir = root / "sandbox"
            sandbox_dir.mkdir()

            seen_multipliers: list[float] = []
            timeout_result = {
                "reward": 0.0,
                "eval_name": "pytest",
                "exception_stats": {"AgentTimeoutError": ["trial-a"]},
                "n_trials": 1,
                "n_errors": 1,
            }
            attempt_results = [dict(timeout_result), dict(timeout_result)]

            original_materialize = self.module.materialize_c4_sandbox
            original_run_harbor_job = self.module.run_harbor_job
            original_parse_job_result = self.module.parse_job_result
            try:
                self.module.materialize_c4_sandbox = lambda *args, **kwargs: sandbox_dir

                def fake_run_harbor_job(**kwargs):
                    config_payload = json.loads(Path(kwargs["config_path"]).read_text())
                    seen_multipliers.append(config_payload["timeout_multiplier"])

                def fake_parse_job_result(*args, **kwargs):
                    return attempt_results.pop(0)

                self.module.run_harbor_job = fake_run_harbor_job
                self.module.parse_job_result = fake_parse_job_result

                result = self.module.run_round_tune_check(
                    task=task,
                    run_dir=root / "out",
                    round_dir_path=round_dir,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    timeout_multiplier=1.0,
                )
            finally:
                self.module.materialize_c4_sandbox = original_materialize
                self.module.run_harbor_job = original_run_harbor_job
                self.module.parse_job_result = original_parse_job_result

            self.assertEqual(seen_multipliers, [1.0, 2.0])
            self.assertEqual(result["exception_stats"], {"AgentTimeoutError": ["trial-a"]})

    def test_run_round_tune_check_does_not_retry_non_timeout_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            round_dir = root / "round-1"
            (round_dir / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_dir / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("candidate\n")
            sandbox_dir = root / "sandbox"
            sandbox_dir.mkdir()

            seen_multipliers: list[float] = []
            attempt_results = [
                {
                    "reward": 0.0,
                    "eval_name": "pytest",
                    "exception_stats": {"VerifierOutputParseError": ["trial-a"]},
                    "n_trials": 1,
                    "n_errors": 1,
                }
            ]

            original_materialize = self.module.materialize_c4_sandbox
            original_run_harbor_job = self.module.run_harbor_job
            original_parse_job_result = self.module.parse_job_result
            try:
                self.module.materialize_c4_sandbox = lambda *args, **kwargs: sandbox_dir

                def fake_run_harbor_job(**kwargs):
                    config_payload = json.loads(Path(kwargs["config_path"]).read_text())
                    seen_multipliers.append(config_payload["timeout_multiplier"])

                def fake_parse_job_result(*args, **kwargs):
                    return attempt_results.pop(0)

                self.module.run_harbor_job = fake_run_harbor_job
                self.module.parse_job_result = fake_parse_job_result

                result = self.module.run_round_tune_check(
                    task=task,
                    run_dir=root / "out",
                    round_dir_path=round_dir,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    timeout_multiplier=1.0,
                )
            finally:
                self.module.materialize_c4_sandbox = original_materialize
                self.module.run_harbor_job = original_run_harbor_job
                self.module.parse_job_result = original_parse_job_result

            self.assertEqual(seen_multipliers, [1.0])
            self.assertEqual(result["exception_stats"], {"VerifierOutputParseError": ["trial-a"]})

    def test_run_round_tune_check_marks_repeated_harbor_command_errors_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            round_dir = root / "round-1"
            (round_dir / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_dir / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("candidate\n")
            sandbox_dir = root / "sandbox"
            sandbox_dir.mkdir()

            original_materialize = self.module.materialize_c4_sandbox
            original_run_harbor_job = self.module.run_harbor_job
            original_parse_job_result = self.module.parse_job_result
            observed = {"parse_called": False}
            try:
                self.module.materialize_c4_sandbox = lambda *args, **kwargs: sandbox_dir

                def fail_run_harbor_job(**kwargs):
                    raise RuntimeError("docker compose exec failed")

                def fail_parse_job_result(*args, **kwargs):
                    observed["parse_called"] = True
                    raise AssertionError("parse_job_result should not run after Harbor command failure")

                self.module.run_harbor_job = fail_run_harbor_job
                self.module.parse_job_result = fail_parse_job_result

                with self.assertRaises(self.module.TuneInfraFailure) as raised:
                    self.module.run_round_tune_check(
                        task=task,
                        run_dir=root / "out",
                        round_dir_path=round_dir,
                        skillsbench_root=root / "skillsbench",
                        oauth_file=root / "oauth.txt",
                        agent_name="claude-code",
                        model_name="anthropic/claude-sonnet-4-5",
                        timeout_multiplier=1.0,
                    )
            finally:
                self.module.materialize_c4_sandbox = original_materialize
                self.module.run_harbor_job = original_run_harbor_job
                self.module.parse_job_result = original_parse_job_result

            self.assertFalse(observed["parse_called"])
            self.assertEqual(len(raised.exception.attempts), self.module.DEFAULT_TUNE_INFRA_MAX_ATTEMPTS)
            self.assertEqual(raised.exception.result["failure_stage"], "harbor_run_failed")
            self.assertFalse((round_dir / "tune_check" / "result.json").exists())
            self.assertTrue((round_dir / "tune_check" / "infra_failure.json").exists())
            self.assertTrue((round_dir / "tune_check" / "infra_failure_attempts" / "attempt-0").exists())

    def test_parse_job_result_marks_docker_trial_failure_as_infra_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            round_dir = root / "round-2"
            job_dir = round_dir / "tune_check" / "demo-task-round-2-c4-tune"
            trial_dir = job_dir / "trial-a"
            trial_dir.mkdir(parents=True)
            (job_dir / "result.json").write_text(
                json.dumps(
                    {
                        "stats": {
                            "n_trials": 1,
                            "n_errors": 1,
                            "evals": {
                                "pytest": {
                                    "metrics": [{"mean": 0.0}],
                                    "exception_stats": {"RuntimeError": ["trial-a"]},
                                }
                            },
                        }
                    }
                )
            )
            (trial_dir / "exception.txt").write_text(
                "RuntimeError: Docker compose command failed. "
                "failed to connect to the docker API at unix:///Users/demo/.docker/run/docker.sock"
            )

            result = self.module.parse_job_result(
                job_dir,
                condition="c4",
                task_id="demo-task",
                skill_source=str(round_dir / "skillpack"),
            )

            self.assertTrue(result["executor_unavailable"])
            self.assertIsNone(result["reward"])
            self.assertEqual(result["failure_stage"], "harbor_trial_infra_failure")
            self.assertIn("HarborJobExecutionError", result["exception_stats"])
            self.assertEqual(result["original_exception_stats"], {"RuntimeError": ["trial-a"]})

    def test_existing_tune_result_ignores_no_prior_evidence_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            round_dir = root / "round-0"
            tune_root = round_dir / "tune_check"
            job_dir = tune_root / "demo-task-round-0-c4-tune"
            (job_dir / "trial-without-result").mkdir(parents=True)
            (tune_root / "config.json").write_text(json.dumps({"job_name": job_dir.name}))
            (tune_root / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c1",
                        "reward": None,
                        "exception_stats": {},
                        "skill_source": "/tmp/source/skills",
                        "note": "no prior c1 tune evidence available",
                    }
                )
            )

            result = self.module.existing_tune_result(
                task_id="demo-task",
                round_dir_path=round_dir,
                skill_source=str(round_dir / "skillpack"),
            )

            self.assertIsNone(result)

    def test_run_round_tune_check_retries_infra_failure_and_persists_success_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            round_dir = root / "round-1"
            (round_dir / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_dir / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("candidate\n")
            sandbox_dir = root / "sandbox"
            sandbox_dir.mkdir()

            parse_results = [
                {
                    "task_id": "demo-task",
                    "condition": "c4",
                    "reward": None,
                    "eval_name": None,
                    "exception_stats": {
                        "HarborJobExecutionError": ["harbor_trial_infra_failure: docker daemon is not running"]
                    },
                    "n_trials": 0,
                    "n_errors": 1,
                    "skill_source": str(round_dir / "skillpack"),
                    "executor_unavailable": True,
                    "failure_stage": "harbor_trial_infra_failure",
                    "failure_message": "docker daemon is not running",
                },
                {
                    "task_id": "demo-task",
                    "condition": "c4",
                    "reward": 0.75,
                    "eval_name": "pytest",
                    "exception_stats": {},
                    "n_trials": 1,
                    "n_errors": 0,
                    "skill_source": str(round_dir / "skillpack"),
                },
            ]
            seen_multipliers: list[float] = []

            original_materialize = self.module.materialize_c4_sandbox
            original_run_harbor_job = self.module.run_harbor_job
            original_parse_job_result = self.module.parse_job_result
            try:
                self.module.materialize_c4_sandbox = lambda *args, **kwargs: sandbox_dir

                def fake_run_harbor_job(**kwargs):
                    config_payload = json.loads(Path(kwargs["config_path"]).read_text())
                    seen_multipliers.append(config_payload["timeout_multiplier"])

                def fake_parse_job_result(*args, **kwargs):
                    return parse_results.pop(0)

                self.module.run_harbor_job = fake_run_harbor_job
                self.module.parse_job_result = fake_parse_job_result

                result = self.module.run_round_tune_check(
                    task=task,
                    run_dir=root / "out",
                    round_dir_path=round_dir,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    timeout_multiplier=1.0,
                )
            finally:
                self.module.materialize_c4_sandbox = original_materialize
                self.module.run_harbor_job = original_run_harbor_job
                self.module.parse_job_result = original_parse_job_result

            self.assertEqual(seen_multipliers, [1.0, 1.0])
            self.assertEqual(result["reward"], 0.75)
            persisted = json.loads((round_dir / "tune_check" / "result.json").read_text())
            self.assertEqual(persisted["reward"], 0.75)
            self.assertTrue((round_dir / "tune_check" / "infra_failure_attempts" / "attempt-0").exists())
            self.assertFalse((round_dir / "tune_check" / "infra_failure.json").exists())

    def test_is_round_materialized_checks_required_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            round_dir = root / "rounds" / "round-1"
            (round_dir / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_dir / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("refined\n")
            for name in [
                "round_1_skill.md",
                "round_1_refine_memo.md",
                "round_1_diff_summary.md",
                "round_1_effect_estimate.md",
                "round_1_risk_note.md",
                "round_1_diagnosis_table.md",
            ]:
                (round_dir / name).write_text("ok\n")
            self.assertTrue(
                self.module.is_round_materialized(task=task, round_dir_path=round_dir, round_index=1)
            )

    def test_append_refine_ledger_skips_duplicate_round(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = self.module.ensure_refine_paths(Path(tmpdir) / "out", "demo-task")
            self.module.append_refine_ledger(
                paths=paths,
                round_index=1,
                parent_round_index=0,
                tune_result={"reward": 0.4, "exception_stats": {}},
            )
            self.module.append_refine_ledger(
                paths=paths,
                round_index=1,
                parent_round_index=0,
                tune_result={"reward": 0.9, "exception_stats": {}},
            )
            lines = paths.ledger_path.read_text().splitlines()
            self.assertEqual(sum(1 for line in lines if line.startswith("| R1 |")), 1)

    def test_is_retryable_refine_contract_failure_detects_missing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            job_dir = Path(tmpdir) / "job-a" / "trial-1" / "verifier"
            job_dir.mkdir(parents=True)
            (job_dir / "test-stdout.txt").write_text("missing refined skill for box-least-squares\n")
            self.assertTrue(
                self.module.is_retryable_refine_contract_failure(Path(tmpdir) / "job-a")
            )

    def test_write_round_context_artifacts_writes_bounded_decision_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            round_zero = paths.rounds_dir / "round-0"
            (round_zero / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_zero / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nrefined\n"
            )

            log_path = root / "session.jsonl"
            log_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "assistant",
                                "message": {
                                    "role": "assistant",
                                    "content": [
                                        {
                                            "type": "tool_use",
                                            "name": "Edit",
                                            "input": {"description": "edit derived layer"},
                                        }
                                    ],
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "assistant",
                                "message": {
                                    "role": "assistant",
                                    "content": [{"type": "text", "text": "verifier contract failed"}],
                                },
                            }
                        ),
                    ]
                )
                + "\n"
            )
            session_evidence = distill_session_logs([log_path])

            c3_row = {
                "condition": "c3",
                "reward": 0.4,
                "result_path": str(root / "c3-result.json"),
                "source_run_dir": str(root / "source-run"),
                "exception_stats": {},
            }
            round_rows = [
                {
                    "round_index": 0,
                    "reward": 0.4,
                    "result_path": str(round_zero / "tune_check" / "result.json"),
                    "round_dir": str(round_zero),
                    "exception_stats": {},
                    "classification": {"kind": "scientific_failure"},
                }
            ]
            decision_context = self.module.write_round_context_artifacts(
                task=task,
                round_index=0,
                source_run_dir=root / "source-run",
                round_rows=round_rows,
                tune_rows=[c3_row],
                paths=paths,
                session_evidence=session_evidence,
            )

            decision_dir = round_zero / "decision_context"
            evidence_bundle = json.loads((decision_dir / "round_0_evidence_bundle.json").read_text())
            round_decision = json.loads((decision_dir / "round_0_decision.json").read_text())

            self.assertTrue((decision_dir / "round_0_evidence_bundle.md").exists())

    def test_write_round_context_artifacts_accepts_r0_evidence_without_c3(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            round_zero = paths.rounds_dir / "round-0"
            (round_zero / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_zero / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nrefined\n"
            )

            decision_context = self.module.write_round_context_artifacts(
                task=task,
                round_index=0,
                source_run_dir=root / "source-run",
                round_rows=[
                    {
                        "round_index": 0,
                        "reward": 0.8,
                        "result_path": str(round_zero / "tune_check" / "result.json"),
                        "round_dir": str(round_zero),
                        "exception_stats": {},
                        "classification": {"kind": "clean_success"},
                    }
                ],
                tune_rows=[
                    {
                        "condition": "r0",
                        "reward": 0.6,
                        "result_path": str(root / "r0-result.json"),
                        "source_run_dir": str(root / "source-run"),
                        "exception_stats": {},
                    }
                ],
                paths=paths,
                starting_label="R0",
                session_evidence=None,
            )

            decision_dir = round_zero / "decision_context"
            evidence_bundle = json.loads((decision_dir / "round_0_evidence_bundle.json").read_text())
            self.assertEqual(evidence_bundle["starting_label"], "R0")
            self.assertEqual(evidence_bundle["starting_result"]["condition"], "r0")
            self.assertEqual(decision_context["refine_intent"]["primary_action"], "preserve_core_structure")

    def test_write_round_context_artifacts_tolerates_missing_starting_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            round_zero = paths.rounds_dir / "round-0"
            (round_zero / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_zero / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nrefined\n"
            )

            self.module.write_round_context_artifacts(
                task=task,
                round_index=0,
                source_run_dir=root / "source-run",
                round_rows=[
                    {
                        "round_index": 0,
                        "reward": None,
                        "result_path": str(round_zero / "tune_check" / "result.json"),
                        "round_dir": str(round_zero),
                        "exception_stats": {},
                        "classification": {"kind": "runtime_failure"},
                    }
                ],
                tune_rows=[],
                paths=paths,
                starting_label="R0",
                session_evidence=None,
            )

            evidence_bundle = json.loads(
                (round_zero / "decision_context" / "round_0_evidence_bundle.json").read_text()
            )
            self.assertEqual(evidence_bundle["starting_label"], "R0")
            self.assertEqual(evidence_bundle["starting_result"]["condition"], "r0")
            self.assertIsNone(evidence_bundle["starting_result"]["reward"])
            self.assertTrue((round_zero / "decision_context" / "round_0_decision.md").exists())
            self.assertFalse(evidence_bundle["bounded"]["raw_session_logs_attached"])
            self.assertFalse(evidence_bundle["bounded"]["session_evidence_attached"])
            self.assertIsNone(evidence_bundle["session_evidence"])

    def test_populate_refine_inputs_dir_copies_decision_context_without_raw_session_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            previous_round = paths.rounds_dir / "round-0"
            (previous_round / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (previous_round / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nrefined\n"
            )
            decision_dir = previous_round / "decision_context"
            decision_dir.mkdir(parents=True)
            (decision_dir / "round_0_decision.json").write_text("{}\n")
            (decision_dir / "round_0_evidence_bundle.json").write_text("{}\n")
            paths.ledger_path.write_text("# ledger\n")
            session_static_dir = paths.static_dir / "session_evidence"
            session_static_dir.mkdir(parents=True)
            (session_static_dir / "session_evidence.json").write_text("{}\n")
            (session_static_dir / "session_evidence.md").write_text("# evidence\n")

            protocols = self.module.ProtocolInputs(
                refine_protocol_path=root / "proto.md",
                bundle_contract_path=root / "bundle.md",
            )
            protocols.refine_protocol_path.write_text("proto\n")
            protocols.bundle_contract_path.write_text("bundle\n")

            target_dir = root / "sandbox" / "environment" / "refine_inputs"
            self.module.populate_refine_inputs_dir(
                task=task,
                paths=paths,
                protocols=protocols,
                target_dir=target_dir,
                previous_round_dir=previous_round,
            )

            self.assertTrue((target_dir / "decision_context" / "round_0_decision.json").exists())
            self.assertTrue((target_dir / "static" / "session_evidence" / "session_evidence.json").exists())
            self.assertFalse((target_dir / "static" / "session_logs").exists())

    def test_populate_refine_inputs_dir_copies_full_tests_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            tests_dir = task_root / "tests"
            tests_dir.mkdir()
            (tests_dir / "test.sh").write_text("pytest /tests/test_setup.py\n")
            (tests_dir / "testing_utils.py").write_text("HELPER = True\n")
            (tests_dir / "test_setup.py").write_text("def test_ok():\n    assert True\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            previous_round = paths.rounds_dir / "round-0"
            (previous_round / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (previous_round / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nrefined\n"
            )
            paths.ledger_path.write_text("# ledger\n")

            protocols = self.module.ProtocolInputs(
                refine_protocol_path=root / "proto.md",
                bundle_contract_path=root / "bundle.md",
            )
            protocols.refine_protocol_path.write_text("proto\n")
            protocols.bundle_contract_path.write_text("bundle\n")

            target_dir = root / "sandbox" / "environment" / "refine_inputs"
            self.module.populate_refine_inputs_dir(
                task=task,
                paths=paths,
                protocols=protocols,
                target_dir=target_dir,
                previous_round_dir=previous_round,
            )

            copied_tests_dir = target_dir / "task_context" / "tests"
            self.assertTrue((copied_tests_dir / "test.sh").exists())
            self.assertTrue((copied_tests_dir / "testing_utils.py").exists())
            self.assertTrue((copied_tests_dir / "test_setup.py").exists())
            self.assertFalse((copied_tests_dir / "test_outputs.py").exists())

    def test_materialize_c4_sandbox_excludes_refine_plan_and_decision_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            round_dir = root / "round-1"
            (round_dir / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_dir / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nrefined\n"
            )
            (round_dir / "decision_context").mkdir(parents=True)
            (round_dir / "decision_context" / "round_0_decision.json").write_text("{}\n")
            (round_dir / "refine_plan.json").write_text("{\"summary\": \"should not leak\"}\n")
            (round_dir / "refine_plan.md").write_text("# Refine Plan\n")
            (round_dir / "next_skillpack_manifest.json").write_text("{}\n")

            sandbox_dir = self.module.materialize_c4_sandbox(task, root / "out", round_dir)

            self.assertTrue((sandbox_dir / "instruction.md").exists())
            self.assertTrue((sandbox_dir / "environment" / "skills" / "skill-a" / "SKILL.md").exists())
            self.assertFalse((sandbox_dir / "environment" / "refine_inputs").exists())
            self.assertFalse((sandbox_dir / "decision_context").exists())
            self.assertFalse((sandbox_dir / "session_evidence").exists())
            self.assertFalse((sandbox_dir / "refine_plan.json").exists())
            self.assertFalse((sandbox_dir / "refine_plan.md").exists())
            self.assertFalse((sandbox_dir / "round_decision.json").exists())
            self.assertFalse((sandbox_dir / "next_skillpack_manifest.json").exists())

    def test_materialize_c4_sandbox_uses_stable_harbor_image_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            round_dir = root / "round-1"
            (round_dir / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_dir / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("refined\n")

            sandbox_dir = self.module.materialize_c4_sandbox(
                task,
                root / "out",
                round_dir,
                harbor_image_name="Demo-Task__Schema-A",
            )

            self.assertEqual(sandbox_dir.name, "demo-task__schema-a")
            self.assertTrue((sandbox_dir / "environment" / "skills" / "skill-a" / "SKILL.md").exists())

    def test_materialize_c4ar_next_round_clears_stale_round_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paths = self.module.ensure_refine_paths(root / "out", "demo-task")
            target_round_dir = paths.rounds_dir / "round-1"
            (target_round_dir / "role_a").mkdir(parents=True)
            (target_round_dir / "role_a" / "session_evidence.json").write_text("{}\n")
            (target_round_dir / "role_b").mkdir(parents=True)
            (target_round_dir / "role_b" / "round_decision.json").write_text("{}\n")
            (target_round_dir / "tune_check").mkdir(parents=True)
            (target_round_dir / "tune_check" / "result.json").write_text("{}\n")

            next_skillpack_dir = root / "candidate" / "skillpack"
            (next_skillpack_dir / "skills" / "skill-a").mkdir(parents=True)
            (next_skillpack_dir / "skills" / "skill-a" / "SKILL.md").write_text("# next\n")

            self.module.materialize_c4ar_next_round(
                paths=paths,
                next_round_index=1,
                next_skillpack_dir=next_skillpack_dir,
                bundle_path=None,
            )

            self.assertTrue((target_round_dir / "skillpack" / "skills" / "skill-a" / "SKILL.md").exists())
            self.assertFalse((target_round_dir / "role_a").exists())
            self.assertFalse((target_round_dir / "role_b").exists())
            self.assertFalse((target_round_dir / "tune_check").exists())

    def test_run_c4ar_round_with_harbor_ignores_synthetic_r0_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            round_zero = paths.rounds_dir / "round-0"
            (round_zero / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_zero / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nr0\n"
            )
            synthetic_tune_root = round_zero / "tune_check"
            synthetic_tune_root.mkdir(parents=True)
            (synthetic_tune_root / "result.json").write_text(json.dumps({"reward": 0.5}) + "\n")

            observed = {"stale_result_present": None}
            original_run_round_tune_check = self.module.run_round_tune_check
            try:
                def fake_run_round_tune_check(**kwargs):
                    tune_root = kwargs["round_dir_path"] / "tune_check"
                    observed["stale_result_present"] = (tune_root / "result.json").exists()
                    job_name = "demo-task-round-0-c4-tune"
                    (tune_root / "config.json").write_text(json.dumps({"job_name": job_name}) + "\n")
                    trial_dir = tune_root / job_name / "trial-001"
                    (trial_dir / "agent").mkdir(parents=True)
                    (trial_dir / "agent" / "claude-code.txt").write_text("read skill\n")
                    (trial_dir / "verifier").mkdir(parents=True)
                    (trial_dir / "verifier" / "report.json").write_text(
                        json.dumps({"summary": {"passed": 1, "failed": 0, "total": 1}, "exitcode": 0}) + "\n"
                    )
                    (trial_dir / "result.json").write_text("{}\n")
                    return {
                        "reward": 0.8444,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "n_trials": 1,
                        "n_errors": 0,
                    }

                self.module.run_round_tune_check = fake_run_round_tune_check

                def fake_role_a_runner(inputs, **kwargs):
                    out_dir = Path(inputs.output_dir)
                    out_dir.mkdir(parents=True, exist_ok=True)
                    payload = {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": "role_a",
                        "model_name": "codex-5.3",
                        "source_log_paths": inputs.source_log_paths,
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": [f"{inputs.source_log_paths[0]}:1"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                    (out_dir / "session_evidence.json").write_text(json.dumps(payload) + "\n")
                    (out_dir / "session_evidence.md").write_text("# Session-Derived Evidence\n")
                    return type(
                        "RoleAResult",
                        (),
                        {
                            "json_path": str(out_dir / "session_evidence.json"),
                            "markdown_path": str(out_dir / "session_evidence.md"),
                        },
                    )()

                def fake_role_b_runner(inputs, **kwargs):
                    out_dir = Path(inputs.output_dir)
                    next_skill = out_dir / "next_skillpack" / "skills" / "skill-a"
                    next_skill.mkdir(parents=True, exist_ok=True)
                    (next_skill / "SKILL.md").write_text("# Derived Execution Layer\nnext\n")
                    (out_dir / "refine_plan.json").write_text(
                        json.dumps(
                            {
                                "task_id": inputs.task_id,
                                "round_index": inputs.round_index,
                                "role": "role_b",
                                "model_name": "gpt-5.4",
                                "summary": "tighten aggregation guidance",
                                "atomic_operations": [],
                            }
                        )
                        + "\n"
                    )
                    (out_dir / "refine_plan.md").write_text("# Refine Plan\n")
                    (out_dir / "next_skillpack_manifest.json").write_text(
                        json.dumps(
                            {
                                "task_id": inputs.task_id,
                                "round_index": inputs.round_index,
                                "role": "role_b",
                                "model_name": "gpt-5.4",
                                "skillpack_dir": str(out_dir / "next_skillpack"),
                                "skill_files": ["skills/skill-a/SKILL.md"],
                                "prompt_invariant": True,
                                "derived_from_round": inputs.round_index,
                            }
                        )
                        + "\n"
                    )
                    (out_dir / "round_decision.json").write_text(
                        json.dumps(
                            {
                                "task_id": inputs.task_id,
                                "round_index": inputs.round_index,
                                "role": "role_b",
                                "model_name": "gpt-5.4",
                                "decision": "continue",
                                "reason": "candidate prepared",
                                "next_round_index": inputs.round_index + 1,
                                "next_skillpack_dir": str(out_dir / "next_skillpack"),
                            }
                        )
                        + "\n"
                    )
                    return type(
                        "RoleBResult",
                        (),
                        {
                            "refine_plan_json_path": str(out_dir / "refine_plan.json"),
                            "refine_plan_markdown_path": str(out_dir / "refine_plan.md"),
                            "next_skillpack_manifest_json_path": str(out_dir / "next_skillpack_manifest.json"),
                            "round_decision_json_path": str(out_dir / "round_decision.json"),
                            "next_skillpack_dir": str(out_dir / "next_skillpack"),
                        },
                    )()

                outputs, tune_result = self.module.run_c4ar_round_with_harbor(
                    task=task,
                    round_index=0,
                    round_dir_path=round_zero,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    tune_timeout_multiplier=3.0,
                    run_dir=root / "out",
                    role_a_runner=fake_role_a_runner,
                    role_b_runner=fake_role_b_runner,
                )
            finally:
                self.module.run_round_tune_check = original_run_round_tune_check

            self.assertFalse(observed["stale_result_present"])
            self.assertEqual(tune_result["reward"], 0.8444)
            self.assertTrue((round_zero / "role_a" / "session_evidence.json").exists())
            self.assertTrue((round_zero / "role_b" / "round_decision.json").exists())

    def test_run_c4ar_round_with_harbor_resumes_from_existing_executor_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            round_one = paths.rounds_dir / "round-1"
            (round_one / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_one / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nr1\n"
            )

            tune_root = round_one / "tune_check"
            job_name = "demo-task-round-1-c4-tune"
            job_dir = tune_root / job_name
            trial_dir = job_dir / "trial-001"
            (trial_dir / "agent").mkdir(parents=True)
            (trial_dir / "agent" / "claude-code.txt").write_text("cached session log\n")
            (trial_dir / "verifier").mkdir(parents=True)
            (trial_dir / "verifier" / "report.json").write_text(
                json.dumps({"summary": {"passed": 1, "failed": 0, "total": 1}, "exitcode": 0}) + "\n"
            )
            (trial_dir / "result.json").write_text("{}\n")
            (tune_root / "config.json").write_text(json.dumps({"job_name": job_name}) + "\n")
            (tune_root / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "job_dir": str(job_dir),
                        "result_path": str(job_dir / "result.json"),
                        "reward": 0.61,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "skill_source": str(round_one / "skillpack"),
                        "n_trials": 1,
                        "n_errors": 0,
                    }
                )
                + "\n"
            )
            (round_one / "executor").mkdir()
            (round_one / "executor" / "verifier_summary.json").write_text(
                json.dumps(
                    {
                        "reward": 0.61,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "n_trials": 1,
                        "n_errors": 0,
                        "report_path": str(trial_dir / "verifier" / "report.json"),
                        "trial_result_path": str(trial_dir / "result.json"),
                        "passed_tests": 1,
                        "failed_tests": 0,
                        "total_tests": 1,
                        "pytest_exitcode": 0,
                    }
                )
                + "\n"
            )

            original_run_round_tune_check = self.module.run_round_tune_check
            observed = {"executor_reran": False}
            try:
                def fail_run_round_tune_check(**kwargs):
                    observed["executor_reran"] = True
                    raise AssertionError("executor should not rerun when cached executor outputs exist")

                self.module.run_round_tune_check = fail_run_round_tune_check

                def fake_role_a_runner(inputs, **kwargs):
                    out_dir = Path(inputs.output_dir)
                    out_dir.mkdir(parents=True, exist_ok=True)
                    payload = {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": "role_a",
                        "model_name": "codex-5.3",
                        "source_log_paths": inputs.source_log_paths,
                        "dominant_failure_pattern": "cached executor resume",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": [f"{inputs.source_log_paths[0]}:1"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                    (out_dir / "session_evidence.json").write_text(json.dumps(payload) + "\n")
                    (out_dir / "session_evidence.md").write_text("# Session-Derived Evidence\n")
                    return type(
                        "RoleAResult",
                        (),
                        {
                            "json_path": str(out_dir / "session_evidence.json"),
                            "markdown_path": str(out_dir / "session_evidence.md"),
                        },
                    )()

                def fake_role_b_runner(inputs, **kwargs):
                    out_dir = Path(inputs.output_dir)
                    next_skill = out_dir / "next_skillpack" / "skills" / "skill-a"
                    next_skill.mkdir(parents=True, exist_ok=True)
                    (next_skill / "SKILL.md").write_text("# Derived Execution Layer\nnext\n")
                    (out_dir / "refine_plan.json").write_text(
                        json.dumps(
                            {
                                "task_id": inputs.task_id,
                                "round_index": inputs.round_index,
                                "role": "role_b",
                                "model_name": "gpt-5.4",
                                "summary": "resume from cached executor",
                                "atomic_operations": [],
                            }
                        )
                        + "\n"
                    )
                    (out_dir / "refine_plan.md").write_text("# Refine Plan\n")
                    (out_dir / "next_skillpack_manifest.json").write_text(
                        json.dumps(
                            {
                                "task_id": inputs.task_id,
                                "round_index": inputs.round_index,
                                "role": "role_b",
                                "model_name": "gpt-5.4",
                                "skillpack_dir": str(out_dir / "next_skillpack"),
                                "skill_files": ["skills/skill-a/SKILL.md"],
                                "prompt_invariant": True,
                                "derived_from_round": inputs.round_index,
                            }
                        )
                        + "\n"
                    )
                    (out_dir / "round_decision.json").write_text(
                        json.dumps(
                            {
                                "task_id": inputs.task_id,
                                "round_index": inputs.round_index,
                                "role": "role_b",
                                "model_name": "gpt-5.4",
                                "decision": "stop",
                                "reason": "resume test complete",
                                "next_round_index": None,
                                "next_skillpack_dir": None,
                                "selected_candidate_label": "R1",
                            }
                        )
                        + "\n"
                    )
                    return type(
                        "RoleBResult",
                        (),
                        {
                            "refine_plan_json_path": str(out_dir / "refine_plan.json"),
                            "refine_plan_markdown_path": str(out_dir / "refine_plan.md"),
                            "next_skillpack_manifest_json_path": str(out_dir / "next_skillpack_manifest.json"),
                            "round_decision_json_path": str(out_dir / "round_decision.json"),
                            "next_skillpack_dir": str(out_dir / "next_skillpack"),
                        },
                    )()

                outputs, tune_result = self.module.run_c4ar_round_with_harbor(
                    task=task,
                    round_index=1,
                    round_dir_path=round_one,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    tune_timeout_multiplier=3.0,
                    run_dir=root / "out",
                    role_a_runner=fake_role_a_runner,
                    role_b_runner=fake_role_b_runner,
                )
            finally:
                self.module.run_round_tune_check = original_run_round_tune_check

            self.assertFalse(observed["executor_reran"])
            self.assertEqual(tune_result["reward"], 0.61)
            self.assertEqual(outputs.round_decision.decision, "stop")

    def test_run_c4ar_round_with_harbor_soft_fails_executor_infrastructure_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            round_zero = paths.rounds_dir / "round-0"
            (round_zero / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_zero / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nr0\n"
            )

            original_run_round_tune_check = self.module.run_round_tune_check
            try:
                def fake_run_round_tune_check(**kwargs):
                    tune_result = {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "reward": None,
                        "eval_name": None,
                        "exception_stats": {
                            "HarborJobExecutionError": ["harbor_run_failed: RuntimeError: docker compose exec failed"]
                        },
                        "n_trials": 0,
                        "n_errors": 1,
                        "skill_source": str(kwargs["round_dir_path"] / "skillpack"),
                        "executor_unavailable": True,
                        "failure_stage": "harbor_run_failed",
                        "failure_message": "RuntimeError: docker compose exec failed",
                    }
                    tune_root = kwargs["round_dir_path"] / "tune_check"
                    tune_root.mkdir(parents=True, exist_ok=True)
                    (tune_root / "result.json").write_text(json.dumps(tune_result) + "\n")
                    return tune_result

                def fail_role_a_runner(*args, **kwargs):
                    raise AssertionError("role_a_runner should be skipped on executor infrastructure failure")

                def fail_role_b_runner(*args, **kwargs):
                    raise AssertionError("role_b_runner should be skipped on executor infrastructure failure")

                self.module.run_round_tune_check = fake_run_round_tune_check

                outputs, tune_result = self.module.run_c4ar_round_with_harbor(
                    task=task,
                    round_index=0,
                    round_dir_path=round_zero,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    tune_timeout_multiplier=1.0,
                    run_dir=root / "out",
                    role_a_runner=fail_role_a_runner,
                    role_b_runner=fail_role_b_runner,
                )
            finally:
                self.module.run_round_tune_check = original_run_round_tune_check

            self.assertTrue(tune_result["executor_unavailable"])
            self.assertEqual(outputs.round_decision.decision, "stop")
            self.assertTrue((round_zero / "executor" / "verifier_summary.json").exists())
            self.assertTrue((round_zero / "role_a" / "session_evidence.json").exists())
            self.assertTrue((round_zero / "role_b" / "refine_plan.json").exists())
            self.assertTrue((round_zero / "role_b" / "round_decision.json").exists())
            cached_executor = self.module.existing_executor_outputs(round_dir_path=round_zero, task_id="demo-task")
            self.assertIsNone(cached_executor)
            cached_round = self.module.existing_c4ar_round_outputs(round_dir_path=round_zero, task_id="demo-task")
            self.assertIsNone(cached_round)

    def test_run_c4ar_round_with_harbor_soft_fails_role_a_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            round_one = paths.rounds_dir / "round-1"
            (round_one / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_one / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nr1\n"
            )

            tune_root = round_one / "tune_check"
            job_name = "demo-task-round-1-c4-tune"
            job_dir = tune_root / job_name
            trial_dir = job_dir / "trial-001"
            (trial_dir / "agent").mkdir(parents=True)
            (trial_dir / "agent" / "claude-code.txt").write_text("cached session log\n")
            (trial_dir / "verifier").mkdir(parents=True)
            report_path = trial_dir / "verifier" / "report.json"
            report_path.write_text(
                json.dumps({"summary": {"passed": 0, "failed": 1, "total": 1}, "exitcode": 1}) + "\n"
            )
            (trial_dir / "result.json").write_text("{}\n")
            (tune_root / "config.json").write_text(json.dumps({"job_name": job_name}) + "\n")
            (tune_root / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "job_dir": str(job_dir),
                        "result_path": str(job_dir / "result.json"),
                        "reward": 0.41,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "skill_source": str(round_one / "skillpack"),
                        "n_trials": 1,
                        "n_errors": 0,
                    }
                )
                + "\n"
            )
            (round_one / "executor").mkdir()
            (round_one / "executor" / "verifier_summary.json").write_text(
                json.dumps(
                    {
                        "reward": 0.41,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "n_trials": 1,
                        "n_errors": 0,
                        "report_path": str(report_path),
                        "trial_result_path": str(trial_dir / "result.json"),
                        "passed_tests": 0,
                        "failed_tests": 1,
                        "total_tests": 1,
                        "pytest_exitcode": 1,
                    }
                )
                + "\n"
            )

            observed = {"role_b_called": False}

            def fail_role_a_runner(*args, **kwargs):
                raise PlaybookAgentTimeoutError("role_a CLI hung after 3 attempts")

            def fail_role_b_runner(*args, **kwargs):
                observed["role_b_called"] = True
                raise AssertionError("role_b_runner should not be called after role_a timeout")

            outputs, tune_result = self.module.run_c4ar_round_with_harbor(
                task=task,
                round_index=1,
                round_dir_path=round_one,
                skillsbench_root=root / "skillsbench",
                oauth_file=root / "oauth.txt",
                agent_name="claude-code",
                model_name="anthropic/claude-sonnet-4-5",
                tune_timeout_multiplier=1.0,
                run_dir=root / "out",
                role_a_runner=fail_role_a_runner,
                role_b_runner=fail_role_b_runner,
            )

            self.assertFalse(observed["role_b_called"])
            self.assertEqual(outputs.round_decision.decision, "stop")
            self.assertIn("RoleAAgentTimeoutError", tune_result["exception_stats"])
            self.assertTrue((round_one / "role_a" / "session_evidence.json").exists())
            self.assertTrue((round_one / "role_b" / "round_decision.json").exists())
            cached_round = self.module.existing_c4ar_round_outputs(round_dir_path=round_one, task_id="demo-task")
            self.assertIsNotNone(cached_round)

            cached_tune_result = json.loads((tune_root / "result.json").read_text())
            self.assertIn("RoleAAgentTimeoutError", cached_tune_result["exception_stats"])
            events = [
                json.loads(line)
                for line in (round_one / "orchestrator_log.ndjson").read_text().splitlines()
                if line.strip()
            ]
            event_types = [item["event_type"] for item in events]
            self.assertEqual(
                event_types,
                ["round_started", "executor_completed", "role_a_failed", "round_decision_loaded"],
            )

    def test_run_c4ar_round_with_harbor_soft_fails_role_b_execution_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            round_one = paths.rounds_dir / "round-1"
            (round_one / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_one / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nr1\n"
            )

            tune_root = round_one / "tune_check"
            job_name = "demo-task-round-1-c4-tune"
            job_dir = tune_root / job_name
            trial_dir = job_dir / "trial-001"
            (trial_dir / "agent").mkdir(parents=True)
            (trial_dir / "agent" / "claude-code.txt").write_text("cached session log\n")
            (trial_dir / "verifier").mkdir(parents=True)
            report_path = trial_dir / "verifier" / "report.json"
            report_path.write_text(
                json.dumps({"summary": {"passed": 0, "failed": 1, "total": 1}, "exitcode": 1}) + "\n"
            )
            (trial_dir / "result.json").write_text("{}\n")
            (tune_root / "config.json").write_text(json.dumps({"job_name": job_name}) + "\n")
            (tune_root / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "job_dir": str(job_dir),
                        "result_path": str(job_dir / "result.json"),
                        "reward": 0.38,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "skill_source": str(round_one / "skillpack"),
                        "n_trials": 1,
                        "n_errors": 0,
                    }
                )
                + "\n"
            )
            (round_one / "executor").mkdir()
            (round_one / "executor" / "verifier_summary.json").write_text(
                json.dumps(
                    {
                        "reward": 0.38,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "n_trials": 1,
                        "n_errors": 0,
                        "report_path": str(report_path),
                        "trial_result_path": str(trial_dir / "result.json"),
                        "passed_tests": 0,
                        "failed_tests": 1,
                        "total_tests": 1,
                        "pytest_exitcode": 1,
                    }
                )
                + "\n"
            )

            def fake_role_a_runner(inputs, **kwargs):
                out_dir = Path(inputs.output_dir)
                out_dir.mkdir(parents=True, exist_ok=True)
                payload = {
                    "task_id": inputs.task_id,
                    "round_index": inputs.round_index,
                    "role": "role_a",
                    "model_name": "codex-5.3",
                    "source_log_paths": inputs.source_log_paths,
                    "dominant_failure_pattern": "executor regression pattern",
                    "wasted_loop_signals": [],
                    "tool_misuse_signals": [],
                    "critical_turns": [],
                    "skill_misguidance_signals": [],
                    "recommended_edit_targets": ["guidance.block_1"],
                    "evidence_refs": [f"{inputs.source_log_paths[0]}:1"],
                    "observed_at": "2026-03-27T00:00:00+00:00",
                }
                (out_dir / "session_evidence.json").write_text(json.dumps(payload) + "\n")
                (out_dir / "session_evidence.md").write_text("# Session-Derived Evidence\n")
                return type(
                    "RoleAResult",
                    (),
                    {
                        "json_path": str(out_dir / "session_evidence.json"),
                        "markdown_path": str(out_dir / "session_evidence.md"),
                    },
                )()

            def fail_role_b_runner(*args, **kwargs):
                raise PlaybookAgentExecutionError("role_b CLI exited 7")

            outputs, tune_result = self.module.run_c4ar_round_with_harbor(
                task=task,
                round_index=1,
                round_dir_path=round_one,
                skillsbench_root=root / "skillsbench",
                oauth_file=root / "oauth.txt",
                agent_name="claude-code",
                model_name="anthropic/claude-sonnet-4-5",
                tune_timeout_multiplier=1.0,
                run_dir=root / "out",
                role_a_runner=fake_role_a_runner,
                role_b_runner=fail_role_b_runner,
            )

            self.assertEqual(outputs.round_decision.decision, "stop")
            self.assertIn("RoleBAgentExecutionError", tune_result["exception_stats"])
            session_evidence_payload = json.loads((round_one / "role_a" / "session_evidence.json").read_text())
            self.assertEqual(
                session_evidence_payload["dominant_failure_pattern"],
                "executor regression pattern",
            )
            events = [
                json.loads(line)
                for line in (round_one / "orchestrator_log.ndjson").read_text().splitlines()
                if line.strip()
            ]
            event_types = [item["event_type"] for item in events]
            self.assertEqual(
                event_types,
                [
                    "round_started",
                    "executor_completed",
                    "role_a_completed",
                    "role_b_failed",
                    "round_decision_loaded",
                ],
            )

    def test_run_c4ar_round_with_harbor_reuses_cached_role_a_and_role_b_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            round_one = paths.rounds_dir / "round-1"
            (round_one / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_one / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nr1\n"
            )

            tune_root = round_one / "tune_check"
            job_name = "demo-task-round-1-c4-tune"
            job_dir = tune_root / job_name
            trial_dir = job_dir / "trial-001"
            (trial_dir / "agent").mkdir(parents=True)
            (trial_dir / "agent" / "claude-code.txt").write_text("cached session log\n")
            (trial_dir / "verifier").mkdir(parents=True)
            report_path = trial_dir / "verifier" / "report.json"
            report_path.write_text(
                json.dumps({"summary": {"passed": 1, "failed": 0, "total": 1}, "exitcode": 0}) + "\n"
            )
            (trial_dir / "result.json").write_text("{}\n")
            (tune_root / "config.json").write_text(json.dumps({"job_name": job_name}) + "\n")
            (tune_root / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "job_dir": str(job_dir),
                        "result_path": str(job_dir / "result.json"),
                        "reward": 0.55,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "skill_source": str(round_one / "skillpack"),
                        "n_trials": 1,
                        "n_errors": 0,
                    }
                )
                + "\n"
            )
            (round_one / "executor").mkdir()
            (round_one / "executor" / "verifier_summary.json").write_text(
                json.dumps(
                    {
                        "reward": 0.55,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "n_trials": 1,
                        "n_errors": 0,
                        "report_path": str(report_path),
                        "trial_result_path": str(trial_dir / "result.json"),
                        "passed_tests": 1,
                        "failed_tests": 0,
                        "total_tests": 1,
                        "pytest_exitcode": 0,
                    }
                )
                + "\n"
            )

            session_evidence = SessionEvidenceArtifact(
                task_id="demo-task",
                round_index=1,
                role="role_a",
                model_name="codex-5.3",
                source_log_paths=[str(trial_dir / "agent" / "claude-code.txt")],
                dominant_failure_pattern="cached role artifacts",
                observed_at="2026-03-27T00:00:00+00:00",
            )
            role_a_dir = round_one / "role_a"
            role_a_dir.mkdir()
            (role_a_dir / "session_evidence.json").write_text(json.dumps(session_evidence.to_dict()))
            (role_a_dir / "session_evidence.md").write_text("# Session-Derived Evidence\n")

            next_skillpack_dir = round_one / "role_b" / "next_skillpack"
            (next_skillpack_dir / "skills" / "skill-a").mkdir(parents=True)
            (next_skillpack_dir / "skills" / "skill-a" / "SKILL.md").write_text("# next r1\n")
            role_b_dir = round_one / "role_b"
            role_b_dir.mkdir(exist_ok=True)
            (role_b_dir / "refine_plan.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "round_index": 1,
                        "role": "role_b",
                        "model_name": "gpt-5.4",
                        "summary": "cached role_b output",
                        "atomic_operations": [],
                    }
                )
                + "\n"
            )
            (role_b_dir / "refine_plan.md").write_text("# Refine Plan\n")
            next_manifest = NextSkillpackManifest(
                task_id="demo-task",
                round_index=1,
                role="role_b",
                model_name="gpt-5.4",
                skillpack_dir=str(next_skillpack_dir),
                skill_files=["skills/skill-a/SKILL.md"],
                prompt_invariant=True,
                derived_from_round=1,
            )
            (role_b_dir / "next_skillpack_manifest.json").write_text(json.dumps(next_manifest.to_dict()))
            round_decision = RoundDecisionArtifact(
                task_id="demo-task",
                round_index=1,
                role="role_b",
                model_name="gpt-5.4",
                decision="stop",
                reason="cached role outputs complete",
                next_round_index=None,
                next_skillpack_dir=None,
                selected_candidate_label="R1",
            )
            (role_b_dir / "round_decision.json").write_text(json.dumps(round_decision.to_dict()))

            original_existing_c4ar_round_outputs = self.module.existing_c4ar_round_outputs
            observed = {"role_a_called": False, "role_b_called": False}
            try:
                self.module.existing_c4ar_round_outputs = lambda **kwargs: None

                def fail_role_a_runner(*args, **kwargs):
                    observed["role_a_called"] = True
                    raise AssertionError("role_a_runner should not rerun when cached role_a outputs exist")

                def fail_role_b_runner(*args, **kwargs):
                    observed["role_b_called"] = True
                    raise AssertionError("role_b_runner should not rerun when cached role_b outputs exist")

                outputs, tune_result = self.module.run_c4ar_round_with_harbor(
                    task=task,
                    round_index=1,
                    round_dir_path=round_one,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    tune_timeout_multiplier=3.0,
                    run_dir=root / "out",
                    role_a_runner=fail_role_a_runner,
                    role_b_runner=fail_role_b_runner,
                )
            finally:
                self.module.existing_c4ar_round_outputs = original_existing_c4ar_round_outputs

            self.assertFalse(observed["role_a_called"])
            self.assertFalse(observed["role_b_called"])
            self.assertEqual(tune_result["reward"], 0.55)
            self.assertEqual(outputs.round_decision.decision, "stop")

    def test_run_c4ar_round_with_harbor_passes_default_playbooks_to_orchestrator(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            round_zero = paths.rounds_dir / "round-0"
            (round_zero / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_zero / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text(
                "# Derived Execution Layer\nr0\n"
            )

            captured: dict[str, object] = {}
            original_run_round_tune_check = self.module.run_round_tune_check
            original_run_c4ar_round = self.module.run_c4ar_round
            try:
                def fake_run_round_tune_check(**kwargs):
                    tune_root = kwargs["round_dir_path"] / "tune_check"
                    tune_root.mkdir(parents=True, exist_ok=True)
                    job_name = "demo-task-round-0-c4-tune"
                    (tune_root / "config.json").write_text(json.dumps({"job_name": job_name}) + "\n")
                    trial_dir = tune_root / job_name / "trial-001"
                    (trial_dir / "agent").mkdir(parents=True)
                    (trial_dir / "agent" / "claude-code.txt").write_text("read skill\n")
                    (trial_dir / "verifier").mkdir(parents=True)
                    (trial_dir / "verifier" / "report.json").write_text(
                        json.dumps({"summary": {"passed": 1, "failed": 0, "total": 1}, "exitcode": 0}) + "\n"
                    )
                    (trial_dir / "result.json").write_text("{}\n")
                    return {
                        "reward": 0.8444,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "n_trials": 1,
                        "n_errors": 0,
                    }

                def fake_run_c4ar_round(inputs, *, config, executor_runner, role_a_runner, role_b_runner):
                    captured["role_a_config"] = config.role_a_config
                    captured["role_b_config"] = config.role_b_config
                    executor_runner(
                        type(
                            "ExecutorInputs",
                            (),
                            {
                                "output_dir": str(Path(inputs.round_root_dir) / "executor"),
                                "skillpack_dir": inputs.current_skillpack_dir,
                                "bundle_path": inputs.current_bundle_path,
                            },
                        )()
                    )
                    return self.module.OrchestratorOutputs(
                        event_log_path=str(Path(inputs.round_root_dir) / "orchestrator_log.ndjson"),
                        session_evidence=SessionEvidenceArtifact(
                            task_id=inputs.task_id,
                            round_index=inputs.round_index,
                            role="role_a",
                            model_name="codex-5.3",
                            source_log_paths=[],
                            dominant_failure_pattern="aggregation drift",
                            wasted_loop_signals=[],
                            tool_misuse_signals=[],
                            critical_turns=[],
                            skill_misguidance_signals=[],
                            recommended_edit_targets=[],
                            evidence_refs=[],
                            observed_at="2026-03-25T00:00:00+00:00",
                        ),
                        next_skillpack_manifest=NextSkillpackManifest(
                            task_id=inputs.task_id,
                            round_index=inputs.round_index,
                            role="role_b",
                            model_name="gpt-5.4",
                            skillpack_dir=str(round_zero / "skillpack"),
                            skill_files=["skills/skill-a/SKILL.md"],
                            prompt_invariant=True,
                            derived_from_round=inputs.round_index,
                            bundle_path=None,
                        ),
                        round_decision=RoundDecisionArtifact(
                            task_id=inputs.task_id,
                            round_index=inputs.round_index,
                            role="role_b",
                            model_name="gpt-5.4",
                            decision="continue",
                            reason="candidate prepared",
                            next_round_index=1,
                            next_skillpack_dir=str(round_zero / "skillpack"),
                        ),
                    )

                self.module.run_round_tune_check = fake_run_round_tune_check
                self.module.run_c4ar_round = fake_run_c4ar_round

                self.module.run_c4ar_round_with_harbor(
                    task=task,
                    round_index=0,
                    round_dir_path=round_zero,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    tune_timeout_multiplier=3.0,
                    run_dir=root / "run",
                )
            finally:
                self.module.run_round_tune_check = original_run_round_tune_check
                self.module.run_c4ar_round = original_run_c4ar_round

            role_a_config = captured["role_a_config"]
            role_b_config = captured["role_b_config"]
            self.assertEqual(role_a_config.model_name, "codex-5.3")
            self.assertEqual(role_b_config.model_name, "gpt-5.4")
            self.assertTrue(role_a_config.playbook_path.endswith("C4AR_ROLE_A_SESSION_DISTILL_PLAYBOOK.md"))
            self.assertTrue(role_b_config.playbook_path.endswith("C4AR_ROLE_B_REFINE_BRAIN_PLAYBOOK.md"))

    def test_run_refine_rounds_c4ar_budget_zero_uses_terminal_executor_and_skips_legacy_refine_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            starting_skillpack_dir = root / "start" / "skillpack"
            (starting_skillpack_dir / "skill-a").mkdir(parents=True)
            (starting_skillpack_dir / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\ncustom\n")
            source = self._make_source_artifacts(
                starting_skillpack_dir=starting_skillpack_dir,
                starting_label="R0",
            )
            r0_row = self.module.make_round_zero_artifacts(task=task, paths=paths, source=source, tune_rows=[])

            protocols = self.module.ProtocolInputs(
                refine_protocol_path=root / "proto.md",
                bundle_contract_path=root / "bundle.md",
            )
            protocols.refine_protocol_path.write_text("proto\n")
            protocols.bundle_contract_path.write_text("bundle\n")

            recorded: dict[str, object] = {}

            def fail_run_c4ar_round_with_harbor(**kwargs):
                raise AssertionError("full orchestrator should not run when round_budget=0")

            def fake_run_terminal_c4ar_round(**kwargs):
                recorded["task_prompt_path"] = kwargs["task"].instruction_path
                recorded["round_index"] = kwargs["round_index"]
                recorded["round_dir_path"] = kwargs["round_dir_path"]
                recorded["current_skillpack_dir"] = kwargs["round_dir_path"] / "skillpack"
                return {
                    "reward": 0.8444,
                    "eval_name": "pytest",
                    "exception_stats": {},
                    "n_trials": 1,
                    "n_errors": 0,
                }

            original_c4ar_round = getattr(self.module, "run_c4ar_round_with_harbor", None)
            original_terminal_round = getattr(self.module, "run_terminal_c4ar_round", None)
            original_write_context = self.module.write_round_context_artifacts
            original_create_refine = self.module.create_refine_round_task_sandbox
            try:
                setattr(self.module, "run_c4ar_round_with_harbor", fail_run_c4ar_round_with_harbor)
                setattr(self.module, "run_terminal_c4ar_round", fake_run_terminal_c4ar_round)

                def fail_write_context(**kwargs):
                    raise AssertionError("legacy decision_context path should not run in c4ar mode")

                def fail_create_refine(*args, **kwargs):
                    raise AssertionError("legacy Harbor refine task should not run in c4ar mode")

                self.module.write_round_context_artifacts = fail_write_context
                self.module.create_refine_round_task_sandbox = fail_create_refine

                rows = self.module.run_refine_rounds(
                    task=task,
                    paths=paths,
                    protocols=protocols,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    round_timeout_multiplier=2.0,
                    tune_timeout_multiplier=3.0,
                    round_budget=0,
                    r0_row=r0_row,
                    run_dir=root / "out",
                    source_run_dir=root / "source-run",
                    starting_label="R0",
                    session_evidence=None,
                    tune_rows=[],
                    orchestration_mode="c4ar",
                )
            finally:
                if original_c4ar_round is None:
                    delattr(self.module, "run_c4ar_round_with_harbor")
                else:
                    setattr(self.module, "run_c4ar_round_with_harbor", original_c4ar_round)
                if original_terminal_round is None:
                    delattr(self.module, "run_terminal_c4ar_round")
                else:
                    setattr(self.module, "run_terminal_c4ar_round", original_terminal_round)
                self.module.write_round_context_artifacts = original_write_context
                self.module.create_refine_round_task_sandbox = original_create_refine

            self.assertEqual(recorded["round_index"], 0)
            self.assertEqual(recorded["task_prompt_path"], task.instruction_path)
            self.assertEqual(recorded["round_dir_path"], paths.rounds_dir / "round-0")
            self.assertEqual(recorded["current_skillpack_dir"], paths.rounds_dir / "round-0" / "skillpack")
            copied = paths.rounds_dir / "round-0" / "skillpack" / "skills" / "skill-a" / "SKILL.md"
            self.assertIn("custom", copied.read_text())
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["round_index"], 0)
            self.assertEqual(rows[0]["reward"], 0.8444)

    def test_run_refine_rounds_c4ar_reruns_perfect_r0_before_roles(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task, paths, r0_row, protocols = self._build_demo_refine_fixture(root)
            attempt_rewards = [1.0, 0.6]
            observed_attempts: list[float] = []

            def fake_executor_outputs(**kwargs):
                reward = attempt_rewards[len(observed_attempts)]
                observed_attempts.append(reward)
                round_dir_path = kwargs["round_dir_path"]
                tune_dir = round_dir_path / "tune_check"
                executor_dir = round_dir_path / "executor"
                tune_dir.mkdir(parents=True, exist_ok=True)
                executor_dir.mkdir(parents=True, exist_ok=True)
                tune_result = {
                    "reward": reward,
                    "eval_name": "pytest",
                    "exception_stats": {},
                    "n_trials": 1,
                    "n_errors": 0,
                }
                (tune_dir / "result.json").write_text(json.dumps(tune_result) + "\n")
                verifier_summary = executor_dir / "verifier_summary.json"
                verifier_summary.write_text(json.dumps({"reward": reward}) + "\n")
                session_log = executor_dir / "executor.log"
                session_log.write_text("ok\n")
                return (
                    self.module.ExecutorOutputs(
                        session_log_path=str(session_log),
                        verifier_summary_path=str(verifier_summary),
                        current_skillpack_dir=str(round_dir_path / "skillpack"),
                        current_bundle_path=None,
                    ),
                    tune_result,
                )

            c4ar_called = 0

            def fake_run_c4ar_round_with_harbor(**kwargs):
                nonlocal c4ar_called
                c4ar_called += 1
                self.assertEqual(kwargs["round_index"], 0)
                self.assertEqual(observed_attempts, [1.0, 0.6])
                round_dir_path = kwargs["round_dir_path"]
                next_skillpack_dir = round_dir_path / "role_b" / "next_skillpack"
                (next_skillpack_dir / "skills" / "skill-a").mkdir(parents=True, exist_ok=True)
                (next_skillpack_dir / "skills" / "skill-a" / "SKILL.md").write_text("# next\n")
                return (
                    type(
                        "FakeOrchestratorOutputs",
                        (),
                        {
                            "session_evidence": type(
                                "FakeSessionEvidence",
                                (),
                                {"dominant_failure_pattern": "none", "recommended_edit_targets": []},
                            )(),
                            "next_skillpack_manifest": type(
                                "FakeNextManifest",
                                (),
                                {
                                    "skill_files": ["skills/skill-a/SKILL.md"],
                                    "prompt_invariant": True,
                                    "skillpack_dir": str(next_skillpack_dir),
                                    "bundle_path": None,
                                },
                            )(),
                            "round_decision": type(
                                "FakeRoundDecision",
                                (),
                                {
                                    "decision": "continue",
                                    "reason": "continue after non-perfect rerun",
                                    "next_round_index": 1,
                                    "next_skillpack_dir": str(next_skillpack_dir),
                                    "selected_candidate_label": "R0",
                                },
                            )(),
                        },
                    )(),
                    {
                        "reward": 0.6,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "n_trials": 1,
                        "n_errors": 0,
                    },
                )

            def fake_run_terminal_c4ar_round(**kwargs):
                self.assertEqual(kwargs["round_index"], 1)
                return {
                    "reward": 0.7,
                    "eval_name": "pytest",
                    "exception_stats": {},
                    "n_trials": 1,
                    "n_errors": 0,
                }

            original_executor = self.module.ensure_c4ar_executor_outputs
            original_c4ar_round = getattr(self.module, "run_c4ar_round_with_harbor", None)
            original_terminal_round = getattr(self.module, "run_terminal_c4ar_round", None)
            try:
                self.module.ensure_c4ar_executor_outputs = fake_executor_outputs
                setattr(self.module, "run_c4ar_round_with_harbor", fake_run_c4ar_round_with_harbor)
                setattr(self.module, "run_terminal_c4ar_round", fake_run_terminal_c4ar_round)
                rows = self.module.run_refine_rounds(
                    task=task,
                    paths=paths,
                    protocols=protocols,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    round_timeout_multiplier=1.0,
                    tune_timeout_multiplier=1.0,
                    round_budget=1,
                    r0_row=r0_row,
                    run_dir=root / "out",
                    source_run_dir=root / "source-run",
                    starting_label="R0",
                    session_evidence=None,
                    tune_rows=[],
                    orchestration_mode="c4ar",
                    r0_perfect_max_reruns=3,
                )
            finally:
                self.module.ensure_c4ar_executor_outputs = original_executor
                if original_c4ar_round is None:
                    delattr(self.module, "run_c4ar_round_with_harbor")
                else:
                    setattr(self.module, "run_c4ar_round_with_harbor", original_c4ar_round)
                if original_terminal_round is None:
                    delattr(self.module, "run_terminal_c4ar_round")
                else:
                    setattr(self.module, "run_terminal_c4ar_round", original_terminal_round)

            report = json.loads((paths.root_dir / "baseline_perfect_rerun.json").read_text())
            self.assertEqual(observed_attempts, [1.0, 0.6])
            self.assertEqual(report["rerun_count"], 1)
            self.assertFalse(report["skipped_inner_loop"])
            self.assertTrue((paths.rounds_dir / "round-0" / "baseline_perfect_reruns" / "attempt-0").exists())
            self.assertEqual(c4ar_called, 1)
            self.assertEqual([row["round_index"] for row in rows], [0, 1])
            self.assertEqual([row["reward"] for row in rows], [0.6, 0.7])

    def test_cleanup_rate_limit_retry_artifacts_archives_r0_rerun_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = root / "run"
            task_id = "demo-task"
            task_root = run_dir / "refine" / task_id
            round0_tune = task_root / "rounds" / "round-0" / "tune_check"
            round0_tune.mkdir(parents=True)
            (round0_tune / "result.json").write_text(
                json.dumps({"type": "result", "is_error": True, "api_error_status": 429}) + "\n"
            )
            report_path = task_root / "baseline_perfect_rerun.json"
            report_path.write_text(json.dumps({"enabled": True, "final_reward": 1.0}) + "\n")

            cleanup = self.module.cleanup_rate_limit_retry_artifacts(
                run_dir=run_dir,
                task_id=task_id,
                round_budget=1,
            )

            self.assertTrue(cleanup["cleaned"])
            self.assertEqual(cleanup["first_rate_limit_round"], 0)
            self.assertFalse(report_path.exists())
            archived_sources = {row["source"] for row in cleanup["archived_paths"]}
            self.assertIn(str(report_path), archived_sources)
            archived_report = [
                Path(row["archive"])
                for row in cleanup["archived_paths"]
                if row["source"] == str(report_path)
            ][0]
            self.assertTrue(archived_report.exists())

    def test_r0_guard_reuses_matching_rerun_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task, paths, _r0_row, _protocols = self._build_demo_refine_fixture(root)
            round0 = paths.rounds_dir / "round-0"
            (round0 / "tune_check").mkdir(parents=True, exist_ok=True)
            (round0 / "tune_check" / "result.json").write_text(json.dumps({"reward": 0.5}) + "\n")
            report = {
                "enabled": True,
                "rerun_count": 1,
                "skipped_inner_loop": False,
                "attempts": [{"attempt_index": 0, "reward": 1.0}, {"attempt_index": 1, "reward": 0.5}],
                "final_reward": 0.5,
                "reason": "r0_baseline_reward_not_perfect",
            }
            (paths.root_dir / "baseline_perfect_rerun.json").write_text(json.dumps(report) + "\n")

            original_executor = self.module.ensure_c4ar_executor_outputs
            try:
                self.module.ensure_c4ar_executor_outputs = mock.Mock(
                    side_effect=AssertionError("matching rerun report should be reused")
                )
                observed = self.module.guard_r0_perfect_baseline_before_inner_loop(
                    task=task,
                    paths=paths,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    tune_timeout_multiplier=1.0,
                    run_dir=root / "out",
                    max_reruns=3,
                )
            finally:
                self.module.ensure_c4ar_executor_outputs = original_executor

            self.assertEqual(observed, report)

    def test_r0_guard_does_not_reuse_stale_rerun_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task, paths, _r0_row, _protocols = self._build_demo_refine_fixture(root)
            round0 = paths.rounds_dir / "round-0"
            (round0 / "tune_check").mkdir(parents=True, exist_ok=True)
            (round0 / "tune_check" / "result.json").write_text(json.dumps({"reward": 0.5}) + "\n")
            (paths.root_dir / "baseline_perfect_rerun.json").write_text(
                json.dumps(
                    {
                        "enabled": True,
                        "rerun_count": 1,
                        "skipped_inner_loop": False,
                        "attempts": [
                            {"attempt_index": 0, "reward": 1.0},
                            {"attempt_index": 1, "reward": 1.0},
                        ],
                        "final_reward": 1.0,
                        "reason": "r0_baseline_reward_not_perfect",
                    }
                )
                + "\n"
            )
            observed_calls = 0

            def fake_executor_outputs(**kwargs):
                nonlocal observed_calls
                observed_calls += 1
                round_dir_path = kwargs["round_dir_path"]
                tune_dir = round_dir_path / "tune_check"
                executor_dir = round_dir_path / "executor"
                tune_dir.mkdir(parents=True, exist_ok=True)
                executor_dir.mkdir(parents=True, exist_ok=True)
                tune_result = {"reward": 0.4, "eval_name": "pytest", "exception_stats": {}}
                (tune_dir / "result.json").write_text(json.dumps(tune_result) + "\n")
                verifier_summary = executor_dir / "verifier_summary.json"
                verifier_summary.write_text(json.dumps({"reward": 0.4}) + "\n")
                session_log = executor_dir / "executor.log"
                session_log.write_text("ok\n")
                return (
                    self.module.ExecutorOutputs(
                        session_log_path=str(session_log),
                        verifier_summary_path=str(verifier_summary),
                        current_skillpack_dir=str(round_dir_path / "skillpack"),
                        current_bundle_path=None,
                    ),
                    tune_result,
                )

            original_executor = self.module.ensure_c4ar_executor_outputs
            try:
                self.module.ensure_c4ar_executor_outputs = fake_executor_outputs
                observed = self.module.guard_r0_perfect_baseline_before_inner_loop(
                    task=task,
                    paths=paths,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    tune_timeout_multiplier=1.0,
                    run_dir=root / "out",
                    max_reruns=3,
                )
            finally:
                self.module.ensure_c4ar_executor_outputs = original_executor

            self.assertEqual(observed_calls, 1)
            self.assertEqual(observed["final_reward"], 0.4)
            self.assertEqual(observed["rerun_count"], 0)

    def test_run_refine_rounds_c4ar_skips_after_three_perfect_r0_reruns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task, paths, r0_row, protocols = self._build_demo_refine_fixture(root)
            observed_attempts: list[int] = []

            def fake_executor_outputs(**kwargs):
                observed_attempts.append(len(observed_attempts))
                round_dir_path = kwargs["round_dir_path"]
                tune_dir = round_dir_path / "tune_check"
                executor_dir = round_dir_path / "executor"
                tune_dir.mkdir(parents=True, exist_ok=True)
                executor_dir.mkdir(parents=True, exist_ok=True)
                tune_result = {
                    "reward": 1.0,
                    "eval_name": "pytest",
                    "exception_stats": {},
                    "n_trials": 1,
                    "n_errors": 0,
                }
                (tune_dir / "result.json").write_text(json.dumps(tune_result) + "\n")
                verifier_summary = executor_dir / "verifier_summary.json"
                verifier_summary.write_text(json.dumps({"reward": 1.0}) + "\n")
                session_log = executor_dir / "executor.log"
                session_log.write_text("ok\n")
                return (
                    self.module.ExecutorOutputs(
                        session_log_path=str(session_log),
                        verifier_summary_path=str(verifier_summary),
                        current_skillpack_dir=str(round_dir_path / "skillpack"),
                        current_bundle_path=None,
                    ),
                    tune_result,
                )

            def fail_run_c4ar_round_with_harbor(**kwargs):
                raise AssertionError("role A/B should not run when R0 baseline remains perfect")

            original_executor = self.module.ensure_c4ar_executor_outputs
            original_c4ar_round = getattr(self.module, "run_c4ar_round_with_harbor", None)
            try:
                self.module.ensure_c4ar_executor_outputs = fake_executor_outputs
                setattr(self.module, "run_c4ar_round_with_harbor", fail_run_c4ar_round_with_harbor)
                rows = self.module.run_refine_rounds(
                    task=task,
                    paths=paths,
                    protocols=protocols,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    round_timeout_multiplier=1.0,
                    tune_timeout_multiplier=1.0,
                    round_budget=3,
                    r0_row=r0_row,
                    run_dir=root / "out",
                    source_run_dir=root / "source-run",
                    starting_label="R0",
                    session_evidence=None,
                    tune_rows=[],
                    orchestration_mode="c4ar",
                    r0_perfect_max_reruns=3,
                )
            finally:
                self.module.ensure_c4ar_executor_outputs = original_executor
                if original_c4ar_round is None:
                    delattr(self.module, "run_c4ar_round_with_harbor")
                else:
                    setattr(self.module, "run_c4ar_round_with_harbor", original_c4ar_round)

            report = json.loads((paths.root_dir / "baseline_perfect_rerun.json").read_text())
            self.assertEqual(observed_attempts, [0, 1, 2, 3])
            self.assertEqual(report["rerun_count"], 3)
            self.assertTrue(report["skipped_inner_loop"])
            self.assertEqual(report["final_reward"], 1.0)
            self.assertEqual([row["round_index"] for row in rows], [0])
            self.assertEqual(rows[0]["reward"], 1.0)
            self.assertTrue(rows[0]["baseline_perfect_rerun"]["skipped_inner_loop"])
            self.assertFalse((paths.rounds_dir / "round-0" / "role_a").exists())
            self.assertFalse((paths.rounds_dir / "round-1").exists())

    def test_run_refine_rounds_c4ar_keeps_base_timeout_multiplier_after_timeout_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text(
                "[agent]\n"
                "timeout_sec = 300\n"
                "[verifier]\n"
                "timeout_sec = 180\n"
                "[build]\n"
                "timeout_sec = 120\n"
            )
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            starting_skillpack_dir = root / "start" / "skillpack"
            (starting_skillpack_dir / "skill-a").mkdir(parents=True)
            (starting_skillpack_dir / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\ncustom\n")
            source = self._make_source_artifacts(
                starting_skillpack_dir=starting_skillpack_dir,
                starting_label="R0",
            )
            r0_row = self.module.make_round_zero_artifacts(task=task, paths=paths, source=source, tune_rows=[])
            protocols = self.module.ProtocolInputs(
                refine_protocol_path=root / "proto.md",
                bundle_contract_path=root / "bundle.md",
            )
            protocols.refine_protocol_path.write_text("proto\n")
            protocols.bundle_contract_path.write_text("bundle\n")

            seen_multipliers: list[float] = []

            def fake_run_c4ar_round_with_harbor(**kwargs):
                round_index = kwargs["round_index"]
                seen_multipliers.append(kwargs["tune_timeout_multiplier"])
                next_skillpack_dir = kwargs["round_dir_path"] / "role_b" / "next_skillpack"
                (next_skillpack_dir / "skills" / "skill-a").mkdir(parents=True, exist_ok=True)
                (next_skillpack_dir / "skills" / "skill-a" / "SKILL.md").write_text(
                    "# Derived Execution Layer\nnext\n"
                )
                self.assertEqual(round_index, 0)
                return (
                    type(
                        "FakeOrchestratorOutputs",
                        (),
                        {
                            "session_evidence": type(
                                "FakeSessionEvidence",
                                (),
                                {
                                    "dominant_failure_pattern": "resolved",
                                    "recommended_edit_targets": [],
                                },
                            )(),
                            "next_skillpack_manifest": type(
                                "FakeNextManifest",
                                (),
                                {
                                    "skill_files": ["skills/skill-a/SKILL.md"],
                                    "prompt_invariant": True,
                                    "skillpack_dir": str(next_skillpack_dir),
                                    "bundle_path": None,
                                },
                            )(),
                            "round_decision": type(
                                "FakeRoundDecision",
                                (),
                                {
                                    "decision": "continue",
                                    "reason": "retry with more time",
                                    "next_round_index": 1,
                                    "next_skillpack_dir": str(next_skillpack_dir),
                                    "selected_candidate_label": "R0",
                                },
                            )(),
                        },
                    )(),
                    {
                        "reward": 0.2,
                        "eval_name": "pytest",
                        "exception_stats": {"AgentTimeoutError": ["trial-a"]},
                        "n_trials": 1,
                        "n_errors": 1,
                    },
                )

            def fake_run_terminal_c4ar_round(**kwargs):
                self.assertEqual(kwargs["round_index"], 1)
                seen_multipliers.append(kwargs["tune_timeout_multiplier"])
                materialized_skill = kwargs["round_dir_path"] / "skillpack" / "skills" / "skill-a" / "SKILL.md"
                self.assertTrue(materialized_skill.exists())
                return {
                    "reward": 0.7,
                    "eval_name": "pytest",
                    "exception_stats": {},
                    "n_trials": 1,
                    "n_errors": 0,
                }

            original_c4ar_round = getattr(self.module, "run_c4ar_round_with_harbor", None)
            original_terminal_round = getattr(self.module, "run_terminal_c4ar_round", None)
            try:
                setattr(self.module, "run_c4ar_round_with_harbor", fake_run_c4ar_round_with_harbor)
                setattr(self.module, "run_terminal_c4ar_round", fake_run_terminal_c4ar_round)
                rows = self.module.run_refine_rounds(
                    task=task,
                    paths=paths,
                    protocols=protocols,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    round_timeout_multiplier=1.0,
                    tune_timeout_multiplier=2.0,
                    round_budget=1,
                    r0_row=r0_row,
                    run_dir=root / "out",
                    source_run_dir=root / "source-run",
                    starting_label="R0",
                    session_evidence=None,
                    tune_rows=[],
                    orchestration_mode="c4ar",
                )
            finally:
                if original_c4ar_round is None:
                    delattr(self.module, "run_c4ar_round_with_harbor")
                else:
                    setattr(self.module, "run_c4ar_round_with_harbor", original_c4ar_round)
                if original_terminal_round is None:
                    delattr(self.module, "run_terminal_c4ar_round")
                else:
                    setattr(self.module, "run_terminal_c4ar_round", original_terminal_round)

            self.assertEqual([round(row["reward"], 4) for row in rows], [0.2, 0.7])
            self.assertEqual(seen_multipliers, [2.0, 2.0])

    def test_run_refine_rounds_c4ar_does_not_rematerialize_existing_next_round(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            starting_skillpack_dir = root / "start" / "skillpack"
            (starting_skillpack_dir / "skill-a").mkdir(parents=True)
            (starting_skillpack_dir / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\ncustom\n")
            source = self._make_source_artifacts(
                starting_skillpack_dir=starting_skillpack_dir,
                starting_label="R0",
            )
            r0_row = self.module.make_round_zero_artifacts(task=task, paths=paths, source=source, tune_rows=[])
            protocols = self.module.ProtocolInputs(
                refine_protocol_path=root / "proto.md",
                bundle_contract_path=root / "bundle.md",
            )
            protocols.refine_protocol_path.write_text("proto\n")
            protocols.bundle_contract_path.write_text("bundle\n")
            existing_round_one = paths.rounds_dir / "round-1"
            (existing_round_one / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (existing_round_one / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("# existing next\n")

            def fake_run_c4ar_round_with_harbor(**kwargs):
                round_index = kwargs["round_index"]
                round_dir_path = kwargs["round_dir_path"]
                self.assertEqual(round_index, 0)
                next_skillpack_dir = round_dir_path / "role_b" / "next_skillpack"
                (next_skillpack_dir / "skills" / "skill-a").mkdir(parents=True, exist_ok=True)
                (next_skillpack_dir / "skills" / "skill-a" / "SKILL.md").write_text("# next\n")
                return (
                    type(
                        "FakeOrchestratorOutputs",
                        (),
                        {
                            "session_evidence": type(
                                "FakeSessionEvidence",
                                (),
                                {
                                    "dominant_failure_pattern": "none",
                                    "recommended_edit_targets": [],
                                },
                            )(),
                            "next_skillpack_manifest": type(
                                "FakeNextManifest",
                                (),
                                {
                                    "skill_files": ["skills/skill-a/SKILL.md"],
                                    "prompt_invariant": True,
                                    "skillpack_dir": str(next_skillpack_dir),
                                    "bundle_path": None,
                                },
                            )(),
                            "round_decision": type(
                                "FakeRoundDecision",
                                (),
                                {
                                    "decision": "continue",
                                    "reason": "resume guard",
                                    "next_round_index": 1,
                                    "next_skillpack_dir": str(next_skillpack_dir),
                                    "selected_candidate_label": "R0",
                                },
                            )(),
                        },
                    )(),
                    {
                        "reward": 0.5,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "n_trials": 1,
                        "n_errors": 0,
                    },
                )

            def fake_run_terminal_c4ar_round(**kwargs):
                self.assertEqual(kwargs["round_index"], 1)
                return {
                    "reward": 0.7,
                    "eval_name": "pytest",
                    "exception_stats": {},
                    "n_trials": 1,
                    "n_errors": 0,
                }

            original_c4ar_round = getattr(self.module, "run_c4ar_round_with_harbor", None)
            original_terminal_round = getattr(self.module, "run_terminal_c4ar_round", None)
            original_materialize = self.module.materialize_c4ar_next_round
            try:
                setattr(self.module, "run_c4ar_round_with_harbor", fake_run_c4ar_round_with_harbor)
                setattr(self.module, "run_terminal_c4ar_round", fake_run_terminal_c4ar_round)

                def fail_materialize(**kwargs):
                    raise AssertionError("existing next round must not be rematerialized")

                self.module.materialize_c4ar_next_round = fail_materialize

                rows = self.module.run_refine_rounds(
                    task=task,
                    paths=paths,
                    protocols=protocols,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    round_timeout_multiplier=1.0,
                    tune_timeout_multiplier=1.0,
                    round_budget=1,
                    r0_row=r0_row,
                    run_dir=root / "out",
                    source_run_dir=root / "source-run",
                    starting_label="R0",
                    session_evidence=None,
                    tune_rows=[],
                    orchestration_mode="c4ar",
                )
            finally:
                if original_c4ar_round is None:
                    delattr(self.module, "run_c4ar_round_with_harbor")
                else:
                    setattr(self.module, "run_c4ar_round_with_harbor", original_c4ar_round)
                if original_terminal_round is None:
                    delattr(self.module, "run_terminal_c4ar_round")
                else:
                    setattr(self.module, "run_terminal_c4ar_round", original_terminal_round)
                self.module.materialize_c4ar_next_round = original_materialize

            self.assertEqual([row["round_index"] for row in rows], [0, 1])

    def test_run_refine_rounds_c4ar_materializes_missing_next_round_before_executor(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Derived Execution Layer\noriginal\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            starting_skillpack_dir = root / "start" / "skillpack"
            (starting_skillpack_dir / "skill-a").mkdir(parents=True)
            (starting_skillpack_dir / "skill-a" / "SKILL.md").write_text("# Derived Execution Layer\ncustom\n")
            source = self._make_source_artifacts(
                starting_skillpack_dir=starting_skillpack_dir,
                starting_label="R0",
            )
            r0_row = self.module.make_round_zero_artifacts(task=task, paths=paths, source=source, tune_rows=[])
            protocols = self.module.ProtocolInputs(
                refine_protocol_path=root / "proto.md",
                bundle_contract_path=root / "bundle.md",
            )
            protocols.refine_protocol_path.write_text("proto\n")
            protocols.bundle_contract_path.write_text("bundle\n")

            seen_rounds: list[int] = []

            def fake_run_c4ar_round_with_harbor(**kwargs):
                round_index = kwargs["round_index"]
                round_dir_path = kwargs["round_dir_path"]
                seen_rounds.append(round_index)
                self.assertEqual(round_index, 0)
                next_skillpack_dir = round_dir_path / "role_b" / "next_skillpack"
                (next_skillpack_dir / "skills" / "skill-a").mkdir(parents=True, exist_ok=True)
                (next_skillpack_dir / "skills" / "skill-a" / "SKILL.md").write_text(f"# next round {round_index}\n")
                return (
                    type(
                        "FakeOrchestratorOutputs",
                        (),
                        {
                            "session_evidence": type(
                                "FakeSessionEvidence",
                                (),
                                {
                                    "dominant_failure_pattern": "none",
                                    "recommended_edit_targets": [],
                                },
                            )(),
                            "next_skillpack_manifest": type(
                                "FakeNextManifest",
                                (),
                                {
                                    "skill_files": ["skills/skill-a/SKILL.md"],
                                    "prompt_invariant": True,
                                    "skillpack_dir": str(next_skillpack_dir),
                                    "bundle_path": None,
                                },
                            )(),
                            "round_decision": type(
                                "FakeRoundDecision",
                                (),
                                {
                                    "decision": "continue",
                                    "reason": "materialize next round",
                                    "next_round_index": 1,
                                    "next_skillpack_dir": str(next_skillpack_dir),
                                    "selected_candidate_label": "R0",
                                },
                            )(),
                        },
                    )(),
                    {
                        "reward": 0.1,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "n_trials": 1,
                        "n_errors": 0,
                    },
                )

            def fake_run_terminal_c4ar_round(**kwargs):
                seen_rounds.append(kwargs["round_index"])
                materialized_skill = kwargs["round_dir_path"] / "skillpack" / "skills" / "skill-a" / "SKILL.md"
                self.assertTrue(
                    materialized_skill.exists(),
                    "round-1 skillpack must be materialized before terminal executor starts",
                )
                return {
                    "reward": 0.2,
                    "eval_name": "pytest",
                    "exception_stats": {},
                    "n_trials": 1,
                    "n_errors": 0,
                }

            original_c4ar_round = getattr(self.module, "run_c4ar_round_with_harbor", None)
            original_terminal_round = getattr(self.module, "run_terminal_c4ar_round", None)
            try:
                setattr(self.module, "run_c4ar_round_with_harbor", fake_run_c4ar_round_with_harbor)
                setattr(self.module, "run_terminal_c4ar_round", fake_run_terminal_c4ar_round)
                rows = self.module.run_refine_rounds(
                    task=task,
                    paths=paths,
                    protocols=protocols,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    round_timeout_multiplier=1.0,
                    tune_timeout_multiplier=1.0,
                    round_budget=1,
                    r0_row=r0_row,
                    run_dir=root / "out",
                    source_run_dir=root / "source-run",
                    starting_label="R0",
                    session_evidence=None,
                    tune_rows=[],
                    orchestration_mode="c4ar",
                )
            finally:
                if original_c4ar_round is None:
                    delattr(self.module, "run_c4ar_round_with_harbor")
                else:
                    setattr(self.module, "run_c4ar_round_with_harbor", original_c4ar_round)
                if original_terminal_round is None:
                    delattr(self.module, "run_terminal_c4ar_round")
                else:
                    setattr(self.module, "run_terminal_c4ar_round", original_terminal_round)

            self.assertEqual(seen_rounds, [0, 1])
            self.assertEqual([row["round_index"] for row in rows], [0, 1])

    def test_c4ar_resume_requires_backup_when_complete_round_would_rewrite_existing_next_round(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = root / "batch-run" / "task_runs" / "demo-run"
            round_zero = run_dir / "refine" / "demo-task" / "rounds" / "round-0"
            (round_zero / "tune_check").mkdir(parents=True)
            (round_zero / "tune_check" / "result.json").write_text(
                json.dumps(
                    {
                        "reward": 0.8,
                        "exception_stats": {},
                    }
                )
            )
            session_evidence = SessionEvidenceArtifact(
                task_id="demo-task",
                round_index=0,
                role="role_a",
                model_name="codex-5.3",
                source_log_paths=["/tmp/session.log"],
                dominant_failure_pattern="none",
                observed_at="2026-03-27T00:00:00+00:00",
            )
            next_manifest = NextSkillpackManifest(
                task_id="demo-task",
                round_index=0,
                role="role_b",
                model_name="gpt-5.4",
                skillpack_dir=str(round_zero / "role_b" / "next_skillpack"),
                skill_files=["skills/skill-a/SKILL.md"],
                prompt_invariant=True,
                derived_from_round=0,
            )
            round_decision = RoundDecisionArtifact(
                task_id="demo-task",
                round_index=0,
                role="role_b",
                model_name="gpt-5.4",
                decision="continue",
                reason="keep refining",
                next_round_index=1,
                next_skillpack_dir=str(round_zero / "role_b" / "next_skillpack"),
                selected_candidate_label="R0",
            )
            (round_zero / "role_a").mkdir()
            (round_zero / "role_a" / "session_evidence.json").write_text(json.dumps(session_evidence.to_dict()))
            (round_zero / "role_b").mkdir()
            (round_zero / "role_b" / "next_skillpack_manifest.json").write_text(json.dumps(next_manifest.to_dict()))
            (round_zero / "role_b" / "round_decision.json").write_text(json.dumps(round_decision.to_dict()))
            (run_dir / "refine" / "demo-task" / "rounds" / "round-1" / "skillpack").mkdir(parents=True)

            self.assertTrue(
                self.module.c4ar_resume_requires_backup(
                    run_dir=run_dir,
                    task_id="demo-task",
                    round_budget=3,
                )
            )

    def test_backup_run_dir_before_resume_writes_archive_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = root / "batch-run" / "task_runs" / "demo-run"
            run_dir.mkdir(parents=True)
            (run_dir / "RUN_STATUS.md").write_text("status\n")

            archive_path = self.module.backup_run_dir_before_resume(
                run_dir=run_dir,
                reason="test backup",
                timestamp_label="20260327T150000Z",
            )

            self.assertTrue(archive_path.exists())
            manifest_path = archive_path.parent / "BACKUP_MANIFEST.md"
            self.assertTrue(manifest_path.exists())
            self.assertIn("test backup", manifest_path.read_text())
            with tarfile.open(archive_path, "r:gz") as handle:
                names = handle.getnames()
            self.assertIn("task_runs/demo-run/RUN_STATUS.md", names)

    def test_infer_c4ar_resume_round_index_prefers_existing_partial_high_round(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = root / "batch-run" / "task_runs" / "demo-run"
            round_two = run_dir / "refine" / "demo-task" / "rounds" / "round-2"
            (round_two / "skillpack").mkdir(parents=True)
            (round_two / "tune_check").mkdir()
            (round_two / "tune_check" / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "reward": 0.77,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "skill_source": str(round_two / "skillpack"),
                    }
                )
            )
            (round_two / "executor").mkdir()
            (round_two / "executor" / "verifier_summary.json").write_text(
                json.dumps(
                    {
                        "trial_result_path": str(round_two / "trial" / "result.json"),
                    }
                )
            )
            session_evidence = SessionEvidenceArtifact(
                task_id="demo-task",
                round_index=2,
                role="role_a",
                model_name="codex-5.3",
                source_log_paths=["/tmp/session.log"],
                dominant_failure_pattern="none",
                observed_at="2026-03-27T00:00:00+00:00",
            )
            next_manifest = NextSkillpackManifest(
                task_id="demo-task",
                round_index=2,
                role="role_b",
                model_name="gpt-5.4",
                skillpack_dir=str(round_two / "role_b" / "next_skillpack"),
                skill_files=["skills/skill-a/SKILL.md"],
                prompt_invariant=True,
                derived_from_round=2,
            )
            round_decision = RoundDecisionArtifact(
                task_id="demo-task",
                round_index=2,
                role="role_b",
                model_name="gpt-5.4",
                decision="continue",
                reason="continue from branch",
                next_round_index=3,
                next_skillpack_dir=str(round_two / "role_b" / "next_skillpack"),
                selected_candidate_label="R2",
            )
            (round_two / "role_a").mkdir()
            (round_two / "role_a" / "session_evidence.json").write_text(json.dumps(session_evidence.to_dict()))
            (round_two / "role_b" / "next_skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_two / "role_b" / "next_skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("# next\n")
            (round_two / "role_b").mkdir(exist_ok=True)
            (round_two / "role_b" / "next_skillpack_manifest.json").write_text(json.dumps(next_manifest.to_dict()))
            (round_two / "role_b" / "round_decision.json").write_text(json.dumps(round_decision.to_dict()))
            (run_dir / "refine" / "demo-task" / "rounds" / "round-3").mkdir(parents=True)

            self.assertEqual(
                self.module.infer_c4ar_resume_round_index(
                    run_dir=run_dir,
                    task_id="demo-task",
                    round_budget=3,
                ),
                3,
            )

    def test_prepare_c4ar_resume_round_materializes_missing_skillpack_from_previous_round(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            round_two = paths.rounds_dir / "round-2"
            (round_two / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_two / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("# current\n")
            (round_two / "tune_check").mkdir()
            (round_two / "tune_check" / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "reward": 0.77,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "skill_source": str(round_two / "skillpack"),
                    }
                )
            )
            (round_two / "executor").mkdir()
            trial_dir = round_two / "trial"
            trial_dir.mkdir()
            (trial_dir / "result.json").write_text("{}\n")
            (trial_dir / "agent").mkdir()
            (trial_dir / "agent" / "claude-code.txt").write_text("cached session log\n")
            (round_two / "executor" / "verifier_summary.json").write_text(
                json.dumps({"trial_result_path": str(trial_dir / "result.json")})
            )
            session_evidence = SessionEvidenceArtifact(
                task_id="demo-task",
                round_index=2,
                role="role_a",
                model_name="codex-5.3",
                source_log_paths=["/tmp/session.log"],
                dominant_failure_pattern="none",
                observed_at="2026-03-27T00:00:00+00:00",
            )
            next_skillpack = round_two / "role_b" / "next_skillpack" / "skills" / "skill-a"
            next_skillpack.mkdir(parents=True)
            (next_skillpack / "SKILL.md").write_text("# next\n")
            next_manifest = NextSkillpackManifest(
                task_id="demo-task",
                round_index=2,
                role="role_b",
                model_name="gpt-5.4",
                skillpack_dir=str(round_two / "role_b" / "next_skillpack"),
                skill_files=["skills/skill-a/SKILL.md"],
                prompt_invariant=True,
                derived_from_round=2,
            )
            round_decision = RoundDecisionArtifact(
                task_id="demo-task",
                round_index=2,
                role="role_b",
                model_name="gpt-5.4",
                decision="continue",
                reason="continue from branch",
                next_round_index=3,
                next_skillpack_dir=str(round_two / "role_b" / "next_skillpack"),
                selected_candidate_label="R2",
            )
            (round_two / "role_a").mkdir()
            (round_two / "role_a" / "session_evidence.json").write_text(json.dumps(session_evidence.to_dict()))
            (round_two / "role_b").mkdir(exist_ok=True)
            (round_two / "role_b" / "next_skillpack_manifest.json").write_text(json.dumps(next_manifest.to_dict()))
            (round_two / "role_b" / "round_decision.json").write_text(json.dumps(round_decision.to_dict()))

            round_three = paths.rounds_dir / "round-3"
            round_three.mkdir()

            self.module.prepare_c4ar_resume_round(
                task=task,
                paths=paths,
                round_index=3,
            )

            self.assertTrue((round_three / "skillpack" / "skills" / "skill-a" / "SKILL.md").exists())
            self.assertIn("next", (round_three / "skillpack" / "skills" / "skill-a" / "SKILL.md").read_text())

    def test_infer_c4ar_resume_round_index_clamps_past_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = root / "batch-run" / "task_runs" / "demo-run"
            round_two = run_dir / "refine" / "demo-task" / "rounds" / "round-2"
            (round_two / "skillpack").mkdir(parents=True)
            (round_two / "tune_check").mkdir()
            (round_two / "tune_check" / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "reward": 0.77,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "skill_source": str(round_two / "skillpack"),
                    }
                )
            )
            (round_two / "executor").mkdir()
            trial_dir = round_two / "trial"
            trial_dir.mkdir()
            (trial_dir / "result.json").write_text("{}\n")
            (trial_dir / "agent").mkdir()
            (trial_dir / "agent" / "claude-code.txt").write_text("cached session log\n")
            (round_two / "executor" / "verifier_summary.json").write_text(
                json.dumps({"trial_result_path": str(trial_dir / "result.json")})
            )
            session_evidence = SessionEvidenceArtifact(
                task_id="demo-task",
                round_index=2,
                role="role_a",
                model_name="codex-5.3",
                source_log_paths=["/tmp/session.log"],
                dominant_failure_pattern="none",
                observed_at="2026-03-27T00:00:00+00:00",
            )
            next_manifest = NextSkillpackManifest(
                task_id="demo-task",
                round_index=2,
                role="role_b",
                model_name="gpt-5.4",
                skillpack_dir=str(round_two / "role_b" / "next_skillpack"),
                skill_files=["skills/skill-a/SKILL.md"],
                prompt_invariant=True,
                derived_from_round=2,
            )
            round_decision = RoundDecisionArtifact(
                task_id="demo-task",
                round_index=2,
                role="role_b",
                model_name="gpt-5.4",
                decision="continue",
                reason="corrupted next round",
                next_round_index=99,
                next_skillpack_dir=str(round_two / "role_b" / "next_skillpack"),
                selected_candidate_label="R2",
            )
            (round_two / "role_a").mkdir()
            (round_two / "role_a" / "session_evidence.json").write_text(json.dumps(session_evidence.to_dict()))
            (round_two / "role_b" / "next_skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_two / "role_b" / "next_skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("# next\n")
            (round_two / "role_b").mkdir(exist_ok=True)
            (round_two / "role_b" / "next_skillpack_manifest.json").write_text(json.dumps(next_manifest.to_dict()))
            (round_two / "role_b" / "round_decision.json").write_text(json.dumps(round_decision.to_dict()))

            self.assertEqual(
                self.module.infer_c4ar_resume_round_index(
                    run_dir=run_dir,
                    task_id="demo-task",
                    round_budget=3,
                ),
                3,
            )

    def test_infer_c4ar_resume_round_index_accepts_completed_terminal_executor_only_round(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = root / "batch-run" / "task_runs" / "demo-run"
            round_three = run_dir / "refine" / "demo-task" / "rounds" / "round-3"
            (round_three / "skillpack").mkdir(parents=True)
            (round_three / "tune_check").mkdir()
            (round_three / "tune_check" / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "reward": 0.88,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "skill_source": str(round_three / "skillpack"),
                    }
                )
            )
            (round_three / "executor").mkdir()
            trial_dir = round_three / "trial"
            trial_dir.mkdir()
            (trial_dir / "result.json").write_text("{}\n")
            (trial_dir / "agent").mkdir()
            (trial_dir / "agent" / "claude-code.txt").write_text("cached session log\n")
            (round_three / "executor" / "verifier_summary.json").write_text(
                json.dumps({"trial_result_path": str(trial_dir / "result.json")})
            )

            self.assertEqual(
                self.module.infer_c4ar_resume_round_index(
                    run_dir=run_dir,
                    task_id="demo-task",
                    round_budget=3,
                ),
                3,
            )

    def test_c4ar_resume_requires_backup_ignores_completed_terminal_executor_only_round(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = root / "batch-run" / "task_runs" / "demo-run"
            round_three = run_dir / "refine" / "demo-task" / "rounds" / "round-3"
            (round_three / "skillpack").mkdir(parents=True)
            (round_three / "tune_check").mkdir()
            (round_three / "tune_check" / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "reward": 0.88,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "skill_source": str(round_three / "skillpack"),
                    }
                )
            )
            (round_three / "executor").mkdir()
            trial_dir = round_three / "trial"
            trial_dir.mkdir()
            (trial_dir / "result.json").write_text("{}\n")
            (trial_dir / "agent").mkdir()
            (trial_dir / "agent" / "claude-code.txt").write_text("cached session log\n")
            (round_three / "executor" / "verifier_summary.json").write_text(
                json.dumps({"trial_result_path": str(trial_dir / "result.json")})
            )

            self.assertFalse(
                self.module.c4ar_resume_requires_backup(
                    run_dir=run_dir,
                    task_id="demo-task",
                    round_budget=3,
                )
            )

    def test_run_refine_rounds_c4ar_resume_preserves_existing_completed_rounds(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            protocols = self.module.ProtocolInputs(
                refine_protocol_path=root / "proto.md",
                bundle_contract_path=root / "bundle.md",
            )
            protocols.refine_protocol_path.write_text("proto\n")
            protocols.bundle_contract_path.write_text("bundle\n")

            round_two = paths.rounds_dir / "round-2"
            (round_two / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_two / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("# existing r2\n")
            (round_two / "tune_check").mkdir()
            (round_two / "tune_check" / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "reward": 0.77,
                        "eval_name": "pytest",
                        "exception_stats": {},
                        "skill_source": str(round_two / "skillpack"),
                    }
                )
            )
            (round_two / "executor").mkdir()
            trial_dir = round_two / "trial"
            trial_dir.mkdir()
            (trial_dir / "result.json").write_text("{}\n")
            (trial_dir / "agent").mkdir()
            (trial_dir / "agent" / "claude-code.txt").write_text("cached session log\n")
            (round_two / "executor" / "verifier_summary.json").write_text(
                json.dumps({"trial_result_path": str(trial_dir / "result.json")})
            )
            session_evidence = SessionEvidenceArtifact(
                task_id="demo-task",
                round_index=2,
                role="role_a",
                model_name="codex-5.3",
                source_log_paths=["/tmp/session.log"],
                dominant_failure_pattern="none",
                observed_at="2026-03-27T00:00:00+00:00",
            )
            next_skillpack_dir = round_two / "role_b" / "next_skillpack"
            (next_skillpack_dir / "skills" / "skill-a").mkdir(parents=True)
            (next_skillpack_dir / "skills" / "skill-a" / "SKILL.md").write_text("# next r3\n")
            next_manifest = NextSkillpackManifest(
                task_id="demo-task",
                round_index=2,
                role="role_b",
                model_name="gpt-5.4",
                skillpack_dir=str(next_skillpack_dir),
                skill_files=["skills/skill-a/SKILL.md"],
                prompt_invariant=True,
                derived_from_round=2,
            )
            round_decision = RoundDecisionArtifact(
                task_id="demo-task",
                round_index=2,
                role="role_b",
                model_name="gpt-5.4",
                decision="continue",
                reason="continue to r3",
                next_round_index=3,
                next_skillpack_dir=str(next_skillpack_dir),
                selected_candidate_label="R2",
            )
            (round_two / "role_a").mkdir()
            (round_two / "role_a" / "session_evidence.json").write_text(json.dumps(session_evidence.to_dict()))
            (round_two / "role_b").mkdir(exist_ok=True)
            (round_two / "role_b" / "next_skillpack_manifest.json").write_text(json.dumps(next_manifest.to_dict()))
            (round_two / "role_b" / "round_decision.json").write_text(json.dumps(round_decision.to_dict()))
            (paths.rounds_dir / "round-3").mkdir()

            def fail_run_c4ar_round_with_harbor(**kwargs):
                raise AssertionError("terminal round should not invoke full orchestrator")

            def fake_run_terminal_c4ar_round(**kwargs):
                self.assertEqual(kwargs["round_index"], 3)
                return {
                    "reward": 0.72,
                    "eval_name": "pytest",
                    "exception_stats": {},
                    "n_trials": 1,
                    "n_errors": 0,
                }

            original_c4ar_round = getattr(self.module, "run_c4ar_round_with_harbor", None)
            original_terminal_round = getattr(self.module, "run_terminal_c4ar_round", None)
            try:
                setattr(self.module, "run_c4ar_round_with_harbor", fail_run_c4ar_round_with_harbor)
                setattr(self.module, "run_terminal_c4ar_round", fake_run_terminal_c4ar_round)
                rows = self.module.run_refine_rounds(
                    task=task,
                    paths=paths,
                    protocols=protocols,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    round_timeout_multiplier=1.0,
                    tune_timeout_multiplier=2.0,
                    round_budget=3,
                    r0_row=None,
                    run_dir=root / "out",
                    source_run_dir=root / "source-run",
                    starting_label="R0",
                    session_evidence=None,
                    tune_rows=[],
                    orchestration_mode="c4ar",
                    start_round_index=3,
                )
            finally:
                if original_c4ar_round is None:
                    delattr(self.module, "run_c4ar_round_with_harbor")
                else:
                    setattr(self.module, "run_c4ar_round_with_harbor", original_c4ar_round)
                if original_terminal_round is None:
                    delattr(self.module, "run_terminal_c4ar_round")
                else:
                    setattr(self.module, "run_terminal_c4ar_round", original_terminal_round)

            self.assertEqual([row["round_index"] for row in rows], [2, 3])
            self.assertEqual(rows[0]["reward"], 0.77)
            self.assertEqual(rows[1]["reward"], 0.72)

    def test_run_refine_rounds_c4ar_resume_uses_base_timeout_multiplier(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# original\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text(
                "[agent]\n"
                "timeout_sec = 500\n"
                "[verifier]\n"
                "timeout_sec = 180\n"
                "[build]\n"
                "timeout_sec = 200\n"
            )
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")
            paths = self.module.ensure_refine_paths(root / "out", task.task_id)
            protocols = self.module.ProtocolInputs(
                refine_protocol_path=root / "proto.md",
                bundle_contract_path=root / "bundle.md",
            )
            protocols.refine_protocol_path.write_text("proto\n")
            protocols.bundle_contract_path.write_text("bundle\n")

            round_two = paths.rounds_dir / "round-2"
            (round_two / "skillpack" / "skills" / "skill-a").mkdir(parents=True)
            (round_two / "skillpack" / "skills" / "skill-a" / "SKILL.md").write_text("# existing r2\n")
            (round_two / "tune_check").mkdir()
            (round_two / "tune_check" / "result.json").write_text(
                json.dumps(
                    {
                        "task_id": "demo-task",
                        "condition": "c4",
                        "reward": 0.2,
                        "eval_name": "pytest",
                        "exception_stats": {"AgentTimeoutError": ["trial-a"]},
                        "skill_source": str(round_two / "skillpack"),
                    }
                )
            )
            (round_two / "executor").mkdir()
            trial_dir = round_two / "trial"
            trial_dir.mkdir()
            (trial_dir / "result.json").write_text("{}\n")
            (trial_dir / "agent").mkdir()
            (trial_dir / "agent" / "claude-code.txt").write_text("cached session log\n")
            (round_two / "executor" / "verifier_summary.json").write_text(
                json.dumps({"trial_result_path": str(trial_dir / "result.json")})
            )
            session_evidence = SessionEvidenceArtifact(
                task_id="demo-task",
                round_index=2,
                role="role_a",
                model_name="codex-5.3",
                source_log_paths=["/tmp/session.log"],
                dominant_failure_pattern="timeout",
                observed_at="2026-03-27T00:00:00+00:00",
            )
            next_skillpack_dir = round_two / "role_b" / "next_skillpack"
            (next_skillpack_dir / "skills" / "skill-a").mkdir(parents=True)
            (next_skillpack_dir / "skills" / "skill-a" / "SKILL.md").write_text("# next r3\n")
            next_manifest = NextSkillpackManifest(
                task_id="demo-task",
                round_index=2,
                role="role_b",
                model_name="gpt-5.4",
                skillpack_dir=str(next_skillpack_dir),
                skill_files=["skills/skill-a/SKILL.md"],
                prompt_invariant=True,
                derived_from_round=2,
            )
            round_decision = RoundDecisionArtifact(
                task_id="demo-task",
                round_index=2,
                role="role_b",
                model_name="gpt-5.4",
                decision="continue",
                reason="continue to r3",
                next_round_index=3,
                next_skillpack_dir=str(next_skillpack_dir),
                selected_candidate_label="R2",
            )
            (round_two / "role_a").mkdir()
            (round_two / "role_a" / "session_evidence.json").write_text(json.dumps(session_evidence.to_dict()))
            (round_two / "role_b").mkdir(exist_ok=True)
            (round_two / "role_b" / "next_skillpack_manifest.json").write_text(json.dumps(next_manifest.to_dict()))
            (round_two / "role_b" / "round_decision.json").write_text(json.dumps(round_decision.to_dict()))
            (paths.rounds_dir / "round-3").mkdir()

            seen_multipliers: list[float] = []

            def fail_run_c4ar_round_with_harbor(**kwargs):
                raise AssertionError("terminal round should not invoke full orchestrator")

            def fake_run_terminal_c4ar_round(**kwargs):
                seen_multipliers.append(kwargs["tune_timeout_multiplier"])
                self.assertEqual(kwargs["round_index"], 3)
                return {
                    "reward": 0.72,
                    "eval_name": "pytest",
                    "exception_stats": {},
                    "n_trials": 1,
                    "n_errors": 0,
                }

            original_c4ar_round = getattr(self.module, "run_c4ar_round_with_harbor", None)
            original_terminal_round = getattr(self.module, "run_terminal_c4ar_round", None)
            try:
                setattr(self.module, "run_c4ar_round_with_harbor", fail_run_c4ar_round_with_harbor)
                setattr(self.module, "run_terminal_c4ar_round", fake_run_terminal_c4ar_round)
                self.module.run_refine_rounds(
                    task=task,
                    paths=paths,
                    protocols=protocols,
                    skillsbench_root=root / "skillsbench",
                    oauth_file=root / "oauth.txt",
                    agent_name="claude-code",
                    model_name="anthropic/claude-sonnet-4-5",
                    round_timeout_multiplier=1.0,
                    tune_timeout_multiplier=2.0,
                    round_budget=3,
                    r0_row=None,
                    run_dir=root / "out",
                    source_run_dir=root / "source-run",
                    starting_label="R0",
                    session_evidence=None,
                    tune_rows=[],
                    orchestration_mode="c4ar",
                    start_round_index=3,
                )
            finally:
                if original_c4ar_round is None:
                    delattr(self.module, "run_c4ar_round_with_harbor")
                else:
                    setattr(self.module, "run_c4ar_round_with_harbor", original_c4ar_round)
                if original_terminal_round is None:
                    delattr(self.module, "run_terminal_c4ar_round")
                else:
                    setattr(self.module, "run_terminal_c4ar_round", original_terminal_round)

            self.assertEqual(seen_multipliers, [2.0])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "run_skillx_rewrite_benchmark.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("run_skillx_rewrite_benchmark", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RunSkillxRewriteBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_extract_fenced_block(self) -> None:
        markdown = """
## 9. Standard Rewrite Prompt

```text
alpha
beta
```
""".strip()
        result = self.module.extract_fenced_block(markdown, "## 9. Standard Rewrite Prompt")
        self.assertEqual(result, "alpha\nbeta")

    def test_normalize_claude_model_name(self) -> None:
        self.assertEqual(
            self.module.normalize_claude_model_name("anthropic/claude-sonnet-4-5"),
            "claude-sonnet-4-5",
        )
        self.assertEqual(self.module.normalize_claude_model_name("sonnet"), "sonnet")

    def test_discover_task_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "tasks" / "demo-task"
            skills_dir = task_root / "environment" / "skills" / "skill-a"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("demo\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            payload = self.module.discover_task_inputs(root, "demo-task")
            self.assertEqual(payload.task_id, "demo-task")
            self.assertEqual(payload.skill_names, ["skill-a"])
            self.assertEqual(payload.skills_dir, task_root / "environment" / "skills")

    def test_discover_task_inputs_ignores_non_skill_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "tasks" / "demo-task"
            skill_dir = task_root / "environment" / "skills" / "skill-a"
            licenses_dir = task_root / "environment" / "skills" / "licenses"
            skill_dir.mkdir(parents=True)
            licenses_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("demo\n")
            (licenses_dir / "obspy.LICENSE").write_text("license\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            payload = self.module.discover_task_inputs(root, "demo-task")

            self.assertEqual(payload.skill_names, ["skill-a"])

    def test_snapshot_rewrite_inputs_skips_non_skill_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "tasks" / "demo-task"
            skill_dir = task_root / "environment" / "skills" / "skill-a"
            licenses_dir = task_root / "environment" / "skills" / "licenses"
            skill_dir.mkdir(parents=True)
            licenses_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("demo\n")
            (licenses_dir / "obspy.LICENSE").write_text("license\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")

            task = self.module.discover_task_inputs(root, "demo-task")
            paths = self.module.make_rewrite_paths(root / "run", task.task_id)

            self.module.snapshot_rewrite_inputs(task, paths)

            self.assertTrue((paths.registry_dir / "original__skill-a__SKILL.md").exists())
            self.assertFalse((paths.registry_dir / "original__licenses__SKILL.md").exists())

    def test_parse_condition_skill_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skillpack_dir = Path(tmpdir) / "skillpack"
            parsed = self.module.parse_condition_skill_sources([f"r0={skillpack_dir}"])
            self.assertEqual(parsed["r0"], skillpack_dir.resolve())

    def test_parse_condition_skill_sources_rejects_builtin_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skillpack_dir = Path(tmpdir) / "skillpack"
            with self.assertRaises(ValueError):
                self.module.parse_condition_skill_sources([f"c2={skillpack_dir}"])

    def test_materialize_task_sandbox_uses_custom_condition_skill_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_root = root / "skillsbench" / "tasks" / "demo-task"
            base_skill_dir = task_root / "environment" / "skills" / "skill-a"
            base_skill_dir.mkdir(parents=True)
            (base_skill_dir / "SKILL.md").write_text("base skill\n")
            (task_root / "instruction.md").write_text("instr\n")
            (task_root / "task.toml").write_text("[agent]\n")
            (task_root / "tests").mkdir()
            (task_root / "tests" / "test.sh").write_text("echo ok\n")
            (task_root / "tests" / "test_outputs.py").write_text("print('ok')\n")
            task = self.module.discover_task_inputs(root / "skillsbench", "demo-task")

            run_dir = root / "run"
            rewrite_paths = self.module.make_rewrite_paths(run_dir, task.task_id)

            custom_skillpack = root / "custom-skillpack"
            custom_skill_dir = custom_skillpack / "skill-x"
            custom_skill_dir.mkdir(parents=True)
            (custom_skill_dir / "SKILL.md").write_text("custom skill\n")

            sandbox_dir = self.module.materialize_task_sandbox(
                task=task,
                run_dir=run_dir,
                condition="r0",
                rewrite_paths=rewrite_paths,
                condition_skill_sources={"r0": custom_skillpack},
            )

            copied_skill = sandbox_dir / "environment" / "skills" / "skill-x" / "SKILL.md"
            self.assertEqual(copied_skill.read_text(), "custom skill\n")
            self.assertFalse((sandbox_dir / "environment" / "skills" / "skill-a").exists())

    def test_main_writes_run_failure_for_rewrite_setup_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            oauth_file = root / "oauth.json"
            oauth_file.write_text("token\n")
            output_dir = root / "out"

            with mock.patch.object(self.module, "check_environment", side_effect=RuntimeError("docker missing")):
                with mock.patch.object(
                    sys,
                    "argv",
                    [
                        "run_skillx_rewrite_benchmark.py",
                        "--skillsbench-root",
                        str(root / "skillsbench"),
                        "--task",
                        "demo-task",
                        "--run-id",
                        "rewrite-run",
                        "--output-dir",
                        str(output_dir),
                        "--oauth-file",
                        str(oauth_file),
                    ],
                ):
                    with self.assertRaises(RuntimeError):
                        self.module.main()

            failure_payload = json.loads((output_dir / "run_failure.json").read_text())
            self.assertEqual(failure_payload["error_type"], "RuntimeError")
            self.assertEqual(failure_payload["failed_stage"], "environment_check")
            self.assertEqual(failure_payload["run_id"], "rewrite-run")


if __name__ == "__main__":
    unittest.main()

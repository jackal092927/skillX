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
    / "monitor_skillx_runs.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("monitor_skillx_runs", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MonitorSkillxRunsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_summarize_c4_run_detects_completed_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "c4-demo"
            task_root = run_dir / "refine" / "demo-task"
            round0 = task_root / "rounds" / "round-0"
            (round0 / "tune_check").mkdir(parents=True)
            (round0 / "round_0_skill.md").write_text("ok\n")
            (round0 / "tune_check" / "result.json").write_text(
                json.dumps({"reward": 0.7, "exception_stats": {}})
            )
            (task_root / "bundle_manifest.json").write_text(json.dumps({"round_budget": 3}))
            (task_root / "refine_summary.json").write_text(
                json.dumps({"selected": {"round_index": 0, "reward": 0.7}})
            )
            (run_dir / "RUN_STATUS.md").write_text("- status: `completed`\n")

            row = self.module.summarize_c4_run(run_dir)
            self.assertEqual(row["status"], "completed")
            self.assertEqual(row["phase"], "completed")
            self.assertEqual(row["latest_tune_completed"], 0)
            self.assertEqual(row["selected_round"], 0)
            self.assertEqual(row["selected_reward"], 0.7)

    def test_monitor_once_marks_progress_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "c4-demo"
            task_root = run_dir / "refine" / "demo-task"
            round0 = task_root / "rounds" / "round-0"
            (round0 / "tune_check").mkdir(parents=True)
            (round0 / "round_0_skill.md").write_text("ok\n")
            (round0 / "tune_check" / "result.json").write_text(
                json.dumps({"reward": 0.5, "exception_stats": {}})
            )
            (run_dir / "RUN_STATUS.md").write_text("- status: `running`\n")

            out_dir = Path(tmpdir) / "watch"
            paths = self.module.ensure_monitor_paths(out_dir)
            first = self.module.monitor_once([run_dir], paths)
            self.assertEqual(first[0]["progress_state"], "new_progress")

            second = self.module.monitor_once([run_dir], paths)
            self.assertEqual(second[0]["progress_state"], "unchanged")

    def test_summarize_c4_run_surfaces_tune_exceptions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "c4-demo"
            task_root = run_dir / "refine" / "demo-task"
            round1 = task_root / "rounds" / "round-1"
            (round1 / "tune_check").mkdir(parents=True)
            (round1 / "round_1_skill.md").write_text("ok\n")
            (round1 / "tune_check" / "result.json").write_text(
                json.dumps({"reward": 0.0, "exception_stats": {"AgentTimeoutError": 1}})
            )
            (run_dir / "RUN_STATUS.md").write_text("- status: `running`\n")

            row = self.module.summarize_c4_run(run_dir)
            self.assertEqual(row["tune_exception_rounds"], [1])
            self.assertEqual(row["phase"], "blocked")


if __name__ == "__main__":
    unittest.main()

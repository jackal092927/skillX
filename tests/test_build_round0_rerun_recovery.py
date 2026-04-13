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
    / "build_round0_rerun_recovery.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("build_round0_rerun_recovery", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BuildRound0RerunRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_select_default_rerun_rows_includes_docker_incidents_and_setup_fuzzing(self) -> None:
        rows = [
            {
                "pair_id": "task-a__artifact-generation",
                "task_name": "task-a",
                "latest_status": "docker_incident",
                "rerun_reason": "docker_incident",
            },
            {
                "pair_id": "setup-fuzzing-py__artifact-generation",
                "task_name": "setup-fuzzing-py",
                "latest_status": "failed_other",
                "rerun_reason": "missing_task_inputs",
            },
            {
                "pair_id": "energy-ac-optimal-power-flow__artifact-generation",
                "task_name": "energy-ac-optimal-power-flow",
                "latest_status": "failed_other",
                "rerun_reason": "other_failure",
            },
            {
                "pair_id": "task-b__artifact-generation",
                "task_name": "task-b",
                "latest_status": "completed",
                "rerun_reason": "",
            },
        ]

        selected = self.module.select_default_rerun_rows(
            rows,
            excluded_pair_ids={"energy-ac-optimal-power-flow__artifact-generation"},
        )

        self.assertEqual(
            [row["pair_id"] for row in selected],
            [
                "task-a__artifact-generation",
                "setup-fuzzing-py__artifact-generation",
            ],
        )

    def test_main_writes_task_slice_and_pair_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            global_status_path = root / "global_pair_status.json"
            task_slice_path = root / "task-slice.json"
            pair_manifest_path = root / "pair-manifest.json"
            summary_path = root / "summary.md"
            global_status_path.write_text(
                json.dumps(
                    {
                        "pairs": [
                            {
                                "pair_id": "task-a__artifact-generation",
                                "task_name": "task-a",
                                "latest_status": "docker_incident",
                                "rerun_reason": "docker_incident",
                            },
                            {
                                "pair_id": "setup-fuzzing-py__artifact-generation",
                                "task_name": "setup-fuzzing-py",
                                "latest_status": "failed_other",
                                "rerun_reason": "missing_task_inputs",
                            },
                            {
                                "pair_id": "energy-ac-optimal-power-flow__artifact-generation",
                                "task_name": "energy-ac-optimal-power-flow",
                                "latest_status": "failed_other",
                                "rerun_reason": "other_failure",
                            },
                        ]
                    }
                )
            )

            exit_code = self.module.main(
                [
                    "--global-status",
                    str(global_status_path),
                    "--task-slice-out",
                    str(task_slice_path),
                    "--pair-manifest-out",
                    str(pair_manifest_path),
                    "--summary-out",
                    str(summary_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            task_slice = json.loads(task_slice_path.read_text())
            pair_manifest = json.loads(pair_manifest_path.read_text())
            self.assertEqual(
                [row["task_name"] for row in task_slice["tasks"]],
                ["task-a", "setup-fuzzing-py"],
            )
            self.assertEqual(
                pair_manifest["selected_pair_ids"],
                [
                    "task-a__artifact-generation",
                    "setup-fuzzing-py__artifact-generation",
                ],
            )
            self.assertEqual(pair_manifest["pair_count_total"], 2)
            self.assertTrue(summary_path.exists())


if __name__ == "__main__":
    unittest.main()

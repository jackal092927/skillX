from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_outer_loop_update_decision.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_outer_loop_update_decision", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BuildOuterLoopUpdateDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def _write_bundle(self, path: Path, scores: dict[tuple[str, str], float]) -> None:
        long_rows = [
            {
                "task_name": task_name,
                "schema_id": schema_id,
                "score": score,
                "reported_score": score,
                "trajectory_signal_score_pct": score,
                "evidence_class": "measured",
            }
            for (task_name, schema_id), score in sorted(scores.items())
        ]
        path.write_text(
            json.dumps(
                {
                    "schema_ids": ["schema-alpha", "schema-beta"],
                    "assignments": [
                        {
                            "task_name": "task-a",
                            "assignment_status": "assigned",
                            "assigned_category": "schema-alpha",
                        },
                        {
                            "task_name": "task-c",
                            "assignment_status": "assigned",
                            "assigned_category": "schema-beta",
                        },
                    ],
                    "multi_assignments": [
                        {"task_name": "task-a", "schema_id": "schema-alpha"},
                        {"task_name": "task-c", "schema_id": "schema-beta"},
                    ],
                    "diagnostics": {
                        "schema_training_assignments": [
                            {"task_name": "task-a", "schema_id": "schema-alpha"},
                            {"task_name": "task-c", "schema_id": "schema-beta"},
                        ]
                    },
                    "score_matrix": {"long_rows": long_rows},
                }
            )
        )

    def test_auto_selects_guarded_patch_when_positive_transfer_has_protected_regression(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            previous_path = root / "previous.json"
            current_path = root / "current.json"
            self._write_bundle(
                previous_path,
                {
                    ("task-a", "schema-alpha"): 100.0,
                    ("task-b", "schema-alpha"): 0.0,
                    ("task-c", "schema-beta"): 20.0,
                },
            )
            self._write_bundle(
                current_path,
                {
                    ("task-a", "schema-alpha"): 0.0,
                    ("task-b", "schema-alpha"): 100.0,
                    ("task-c", "schema-beta"): 100.0,
                },
            )

            decision = self.module.build_outer_loop_update_decision(
                current_control_plane_bundle_path=current_path,
                previous_control_plane_bundle_path=previous_path,
                requested_mode="auto",
                max_protected_regressions_for_rewrite=0,
            )

            self.assertEqual(decision["global_update_mode"], "guarded_patch")
            self.assertEqual(len(decision["positive_transfer_pairs"]), 2)
            self.assertEqual(len(decision["protected_regression_pairs"]), 1)
            self.assertEqual(
                decision["schema_decisions"]["schema-alpha"]["update_mode"],
                "guarded_patch",
            )
            self.assertEqual(
                decision["schema_decisions"]["schema-beta"]["update_mode"],
                "guarded_patch",
            )

    def test_no_previous_bundle_defaults_to_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            current_path = root / "current.json"
            self._write_bundle(current_path, {("task-a", "schema-alpha"): 80.0})

            decision = self.module.build_outer_loop_update_decision(
                current_control_plane_bundle_path=current_path,
                previous_control_plane_bundle_path=None,
            )

            self.assertEqual(decision["global_update_mode"], "rewrite")
            self.assertEqual(
                decision["schema_decisions"]["schema-alpha"]["update_mode"],
                "rewrite",
            )

    def test_writes_decision_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            decision = {
                "global_update_mode": "guarded_patch",
                "mode_reason": "test",
                "scorecard": {},
                "positive_transfer_pairs": [],
                "protected_regression_pairs": [],
                "schema_decisions": {},
            }
            outputs = self.module.write_outer_loop_update_decision_artifacts(
                decision=decision,
                output_dir=root / "out",
            )

            self.assertTrue((root / "out" / "outer_loop_update_decision.json").exists())
            self.assertTrue((root / "out" / "summary.md").exists())
            self.assertIn("outer_loop_update_decision_json", outputs)


if __name__ == "__main__":
    unittest.main()

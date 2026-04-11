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
    / "materialize_skillx_round0_runner.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("materialize_skillx_round0_runner", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MaterializeSkillXRound0RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def _build_fixture(self, root: Path) -> dict[str, Path]:
        skillsbench_root = root / "skillsbench-src"
        for task_name in ("task-alpha", "task-beta"):
            skill_dir = skillsbench_root / "tasks" / task_name / "environment" / "skills" / "main-skill"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(f"# Skill\n\nCurrent skill for {task_name}.\n")
            (skillsbench_root / "tasks" / task_name / "instruction.md").write_text(
                f"Task {task_name} instruction line one.\nSecond line with more detail.\n"
            )
            (skillsbench_root / "tasks" / task_name / "task.toml").write_text(
                "[agent]\ntimeout_sec = 120\n[verifier]\ntimeout_sec = 180\n"
            )
            tests_dir = skillsbench_root / "tasks" / task_name / "tests"
            tests_dir.mkdir(parents=True, exist_ok=True)
            (tests_dir / "test.sh").write_text("#!/bin/sh\nexit 0\n")
            (tests_dir / "test_outputs.py").write_text("EXPECTED = {}\n")

        prompt_bank_path = root / "prompt-bank.json"
        prompt_bank_path.write_text(
            json.dumps(
                {
                    "categories": [
                        {
                            "category_id": "analytic-pipeline",
                            "semantic_intent": "Do staged analysis.",
                            "emphasize": ["stage decomposition"],
                            "avoid": ["vague prose"],
                            "expected_good_fit": ["analysis tasks"],
                            "expected_bad_fit": ["artifact tasks"],
                            "meta_prompt": "Preserve staged handoffs.",
                        },
                        {
                            "category_id": "artifact-generation",
                            "semantic_intent": "Produce exact artifacts.",
                            "emphasize": ["exact contract"],
                            "avoid": ["guessing"],
                            "expected_good_fit": ["formatting tasks"],
                            "expected_bad_fit": ["control tasks"],
                            "meta_prompt": "Stay exact.",
                        },
                    ]
                }
            )
        )

        inventory_path = root / "cluster-inputs.jsonl"
        inventory_rows = [
            {
                "task_name": "task-alpha",
                "cluster_inputs": {
                    "semantic_contract": {
                        "task_object_seed": "analytic-pipeline",
                        "verifier_mode": "deterministic-output-contract",
                    },
                    "tool_topology": {
                        "workflow_topology": "staged-multi-step",
                        "tool_surface_regime": "tool-medium",
                    },
                },
                "tags": {
                    "primary_pattern": "pipeline",
                    "secondary_patterns": ["reviewer"],
                    "confidence": "high",
                    "evidence_note": "Alpha evidence note.",
                },
            },
            {
                "task_name": "task-beta",
                "cluster_inputs": {
                    "semantic_contract": {
                        "task_object_seed": "artifact-generation",
                        "verifier_mode": "deterministic-output-contract",
                    },
                    "tool_topology": {
                        "workflow_topology": "single-artifact",
                        "tool_surface_regime": "tool-light",
                    },
                },
                "tags": {
                    "primary_pattern": "artifact",
                    "secondary_patterns": ["generator"],
                    "confidence": "medium",
                    "evidence_note": "Beta evidence note.",
                },
            },
        ]
        inventory_path.write_text("".join(json.dumps(row) + "\n" for row in inventory_rows))

        task_slice_path = root / "task-slice.json"
        task_slice_path.write_text(
            json.dumps(
                {
                    "tasks": [
                        {
                            "task_name": "task-alpha",
                            "seed_schema_id": "analytic-pipeline",
                            "official_sonnet45_with_skills_score": 20,
                        },
                        {
                            "task_name": "task-beta",
                            "seed_schema_id": "artifact-generation",
                            "official_sonnet45_with_skills_score": 0,
                        },
                    ]
                }
            )
        )

        official_results_path = root / "official_task_results.jsonl"
        official_rows = [
            {
                "task_id": "task-alpha",
                "model": "Claude Code (Sonnet 4.5)",
                "condition": "No Skills",
                "score": 40,
            },
            {
                "task_id": "task-alpha",
                "model": "Claude Code (Sonnet 4.5)",
                "condition": "With Skills",
                "score": 20,
            },
            {
                "task_id": "task-beta",
                "model": "Claude Code (Sonnet 4.5)",
                "condition": "No Skills",
                "score": 0,
            },
            {
                "task_id": "task-beta",
                "model": "Claude Code (Sonnet 4.5)",
                "condition": "With Skills",
                "score": 0,
            },
        ]
        official_results_path.write_text("".join(json.dumps(row) + "\n" for row in official_rows))

        render_template_path = root / "render-template.md"
        render_template_path.write_text("Frozen render template placeholder.\n")

        return {
            "skillsbench_root": skillsbench_root,
            "prompt_bank_path": prompt_bank_path,
            "inventory_path": inventory_path,
            "task_slice_path": task_slice_path,
            "official_results_path": official_results_path,
            "render_template_path": render_template_path,
        }

    def test_build_pair_specs_expands_task_schema_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            result = self.module.build_round0_materialization(
                skillsbench_root=fixture["skillsbench_root"],
                task_slice_path=fixture["task_slice_path"],
                prompt_bank_path=fixture["prompt_bank_path"],
                inventory_path=fixture["inventory_path"],
                official_results_path=fixture["official_results_path"],
                render_template_path=fixture["render_template_path"],
                output_dir=Path(tmpdir) / "out",
                run_id="round0-test",
                round_budget=3,
                oauth_file=Path("/tmp/oauth.json"),
            )
            self.assertEqual(result["manifest"]["pair_count"], 4)
            self.assertEqual(len(result["pair_specs"]), 4)
            pair_ids = {pair["pair_id"] for pair in result["pair_specs"]}
            self.assertIn("task-alpha__analytic-pipeline", pair_ids)
            self.assertIn("task-beta__artifact-generation", pair_ids)
            sample_pair = next(item for item in result["pair_specs"] if item["pair_id"] == "task-alpha__analytic-pipeline")
            self.assertEqual(sample_pair["pair_dir"], "pairs/task-alpha__analytic-pipeline")
            self.assertEqual(
                sample_pair["rendered_meta_skill_path"],
                "pairs/task-alpha__analytic-pipeline/rendered_meta_skill.md",
            )
            self.assertEqual(
                result["manifest"]["path_strategy"]["pair_dir"],
                "materialized_root_relative",
            )

    def test_rendered_meta_skill_preserves_frozen_block_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            result = self.module.build_round0_materialization(
                skillsbench_root=fixture["skillsbench_root"],
                task_slice_path=fixture["task_slice_path"],
                prompt_bank_path=fixture["prompt_bank_path"],
                inventory_path=fixture["inventory_path"],
                official_results_path=fixture["official_results_path"],
                render_template_path=fixture["render_template_path"],
                output_dir=Path(tmpdir) / "out",
                run_id="round0-test",
                round_budget=3,
                oauth_file=Path("/tmp/oauth.json"),
            )
            pair = next(item for item in result["pair_specs"] if item["pair_id"] == "task-alpha__analytic-pipeline")
            rendered = ((Path(tmpdir) / "out") / pair["rendered_meta_skill_path"]).read_text()
            expected_order = [
                "[Common wrapper]",
                "[Meta schema block]",
                "[Task context block]",
                "[Current Task skill block]",
                "[Evidence block]",
                "[Output contract block]",
            ]
            cursor = -1
            for marker in expected_order:
                next_cursor = rendered.find(marker)
                self.assertGreater(next_cursor, cursor)
                cursor = next_cursor
            self.assertIn("No Skills: `40`", rendered)
            self.assertIn("With Skills: `20`", rendered)
            self.assertIn("Current skill for task-alpha.", rendered)

    def test_refine_command_uses_task_c1_skillpack_as_starting_point(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = self._build_fixture(Path(tmpdir))
            result = self.module.build_round0_materialization(
                skillsbench_root=fixture["skillsbench_root"],
                task_slice_path=fixture["task_slice_path"],
                prompt_bank_path=fixture["prompt_bank_path"],
                inventory_path=fixture["inventory_path"],
                official_results_path=fixture["official_results_path"],
                render_template_path=fixture["render_template_path"],
                output_dir=Path(tmpdir) / "out",
                run_id="round0-test",
                round_budget=3,
                oauth_file=Path("/tmp/oauth.json"),
            )
            pair = next(item for item in result["pair_specs"] if item["pair_id"] == "task-beta__artifact-generation")
            command = " ".join(pair["refine_command"])
            self.assertIn("--starting-label C1", command)
            self.assertIn("--output-dir pairs/task-beta__artifact-generation/refine_run", command)
            self.assertIn("--source-run-dir pairs/task-beta__artifact-generation/source_stub", command)
            self.assertIn(
                str(fixture["skillsbench_root"] / "tasks" / "task-beta" / "environment" / "skills"),
                command,
            )
            self.assertIn("--task task-beta", command)
            self.assertIn("--round-budget 3", command)


if __name__ == "__main__":
    unittest.main()

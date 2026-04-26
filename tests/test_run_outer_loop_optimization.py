from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_outer_loop_optimization.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("run_outer_loop_optimization", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RunOuterLoopOptimizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def _write_task(self, skillsbench_root: Path, task_name: str) -> None:
        task_root = skillsbench_root / "tasks" / task_name
        skills_dir = task_root / "environment" / "skills" / "skill-a"
        skills_dir.mkdir(parents=True)
        (task_root / "instruction.md").write_text(f"Solve {task_name}.\nReturn answer.txt.\n")
        (task_root / "task.toml").write_text("name = \"demo\"\n")
        (skills_dir / "SKILL.md").write_text("# Skill A\nUse the existing task skill.\n")

    def _write_inventory(self, path: Path, task_names: list[str]) -> None:
        rows = []
        for task_name in task_names:
            rows.append(
                {
                    "task_name": task_name,
                    "cluster_inputs": {
                        "semantic_contract": {
                            "task_object_seed": "schema-alpha",
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
                        "evidence_note": f"{task_name} evidence note",
                    },
                }
            )
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")

    def _write_official_results(self, path: Path, task_names: list[str]) -> None:
        rows = []
        for task_name in task_names:
            rows.extend(
                [
                    {
                        "task_id": task_name,
                        "model": "Claude Code (Sonnet 4.5)",
                        "condition": "No Skills",
                        "score": 10.0,
                    },
                    {
                        "task_id": task_name,
                        "model": "Claude Code (Sonnet 4.5)",
                        "condition": "With Skills",
                        "score": 20.0,
                    },
                ]
            )
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")

    def _write_prompt_bank(self, path: Path) -> None:
        path.write_text(
            json.dumps(
                {
                    "artifact_type": "skillx_prompt_bank",
                    "version": "v0.1",
                    "categories": [
                        {
                            "category_id": "schema-alpha",
                            "semantic_intent": "Alpha schema.",
                            "emphasize": ["alpha stage discipline"],
                            "avoid": ["alpha overreach"],
                            "expected_good_fit": ["alpha tasks"],
                            "expected_bad_fit": ["beta tasks"],
                            "meta_prompt": "Use alpha guidance.",
                        },
                        {
                            "category_id": "schema-beta",
                            "semantic_intent": "Beta schema.",
                            "emphasize": ["beta review discipline"],
                            "avoid": ["beta overreach"],
                            "expected_good_fit": ["beta tasks"],
                            "expected_bad_fit": ["alpha tasks"],
                            "meta_prompt": "Use beta guidance.",
                        },
                    ],
                }
            )
        )

    def _write_round0_inputs(self, round0_root: Path, global_status_path: Path) -> None:
        report_dir = round0_root / "slice-a" / "reports" / "run-a"
        report_dir.mkdir(parents=True)
        pair_results = []
        pairs = []
        scores = {
            ("task-a", "schema-alpha"): 80.0,
            ("task-a", "schema-beta"): 76.0,
            ("task-b", "schema-alpha"): 40.0,
            ("task-b", "schema-beta"): 55.0,
        }
        for (task_name, schema_id), score in scores.items():
            pair_id = f"{task_name}__{schema_id}"
            pair_results.append(
                {
                    "pair_id": pair_id,
                    "task_name": task_name,
                    "schema_id": schema_id,
                    "selected": {"score_pct": score},
                    "best_observed": {"score_pct": score},
                    "official_scores": {"c0_pct": 10.0, "c1_pct": 20.0},
                    "timeout_detected": False,
                    "has_intermediate_exceptions": False,
                    "failure": None,
                    "rounds": [
                        {"round_index": 0, "score_pct": max(0.0, score - 10.0)},
                        {"round_index": 1, "score_pct": score},
                    ],
                }
            )
            pairs.append(
                {
                    "pair_id": pair_id,
                    "task_name": task_name,
                    "schema_id": schema_id,
                    "latest_status": "completed",
                    "latest_status_code": "C",
                    "attempt_count": 1,
                    "latest_run_label": "run-a",
                    "latest_selected_score_pct": score,
                    "latest_best_observed_score_pct": score,
                    "latest_timeout_detected": False,
                    "latest_has_intermediate_exceptions": False,
                    "latest_failure_summary": "",
                }
            )
        (report_dir / "run_report.json").write_text(
            json.dumps({"run_label": "run-a", "pair_results": pair_results})
        )
        global_status_path.parent.mkdir(parents=True)
        global_status_path.write_text(
            json.dumps({"schema_ids": ["schema-alpha", "schema-beta"], "pairs": pairs})
        )

    def test_materialize_next_round_pairs_writes_launcher_compatible_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skillsbench_root = root / "skillsbench"
            self._write_task(skillsbench_root, "task-a")
            inventory_path = root / "inventory.jsonl"
            official_path = root / "official.jsonl"
            render_template_path = root / "render.md"
            self._write_inventory(inventory_path, ["task-a"])
            self._write_official_results(official_path, ["task-a"])
            render_template_path.write_text("render")
            package = {
                "config": {"round_id": "round0", "next_round_id": "round1"},
                "candidate_prompt_bank": {
                    "categories": [
                        {
                            "category_id": "schema-alpha",
                            "semantic_intent": "Alpha schema.",
                            "emphasize": ["alpha"],
                            "avoid": ["overreach"],
                            "expected_good_fit": ["task-a"],
                            "expected_bad_fit": [],
                            "meta_prompt": "Use alpha.",
                            "outer_loop_candidate_id": "schema-alpha::round1::conservative",
                            "outer_loop_candidate_mode": "conservative",
                        }
                    ]
                },
                "schema_evidence_bundles": {
                    "schema-alpha": {
                        "assigned_task_summaries": [{"task_name": "task-a"}],
                        "ambiguous_borderline_cases": [{"task_name": "task-a"}],
                        "cross_schema_losses": [],
                    }
                },
                "challenger_eval_plan": [
                    {
                        "schema_id": "schema-alpha",
                        "candidate_mode": "conservative",
                        "task_names": ["task-a"],
                    }
                ],
            }

            result = self.module.materialize_next_round_pairs(
                package=package,
                output_dir=root / "materialized",
                skillsbench_root=skillsbench_root,
                inventory_path=inventory_path,
                official_results_path=official_path,
                render_template_path=render_template_path,
                run_id="round1-run",
                round_budget=3,
                oauth_file=root / "oauth-token",
                agent="claude-code",
                model="anthropic/claude-sonnet-4-5",
                schema_update_package_path=root / "schema_update_package.json",
            )

            materialized = root / "materialized"
            self.assertEqual(result["manifest"]["pair_count"], 1)
            self.assertEqual(result["manifest"]["next_pair_plan_mode"], "full_matrix")
            self.assertTrue((materialized / "manifest.json").exists())
            self.assertTrue((materialized / "pair_specs.jsonl").exists())
            self.assertTrue((materialized / "pairs" / "task-a__schema-alpha" / "pair_spec.json").exists())
            rendered = (
                materialized / "pairs" / "task-a__schema-alpha" / "rendered_meta_skill.md"
            ).read_text()
            self.assertIn("[Outer-loop candidate block]", rendered)
            pair_spec = json.loads((materialized / "pair_specs.jsonl").read_text().splitlines()[0])
            self.assertEqual(pair_spec["pair_reason"], "assigned_support;boundary_case")
            self.assertEqual(pair_spec["next_pair_plan_mode"], "full_matrix")

    def test_materialize_next_round_pairs_can_keep_challenger_subset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skillsbench_root = root / "skillsbench"
            for task_name in ("task-a", "task-b"):
                self._write_task(skillsbench_root, task_name)
            inventory_path = root / "inventory.jsonl"
            official_path = root / "official.jsonl"
            render_template_path = root / "render.md"
            self._write_inventory(inventory_path, ["task-a", "task-b"])
            self._write_official_results(official_path, ["task-a", "task-b"])
            render_template_path.write_text("render")
            package = {
                "config": {"round_id": "round0", "next_round_id": "round1"},
                "schema_ids": ["schema-alpha", "schema-beta"],
                "candidate_prompt_bank": {
                    "categories": [
                        {
                            "category_id": "schema-alpha",
                            "semantic_intent": "Alpha schema.",
                            "emphasize": ["alpha"],
                            "avoid": ["overreach"],
                            "expected_good_fit": ["task-a"],
                            "expected_bad_fit": [],
                            "meta_prompt": "Use alpha.",
                            "outer_loop_candidate_id": "schema-alpha::round1::conservative",
                            "outer_loop_candidate_mode": "conservative",
                        },
                        {
                            "category_id": "schema-beta",
                            "semantic_intent": "Beta schema.",
                            "emphasize": ["beta"],
                            "avoid": ["overreach"],
                            "expected_good_fit": ["task-b"],
                            "expected_bad_fit": [],
                            "meta_prompt": "Use beta.",
                            "outer_loop_candidate_id": "schema-beta::round1::conservative",
                            "outer_loop_candidate_mode": "conservative",
                        },
                    ]
                },
                "schema_evidence_bundles": {
                    "schema-alpha": {"assigned_task_summaries": [{"task_name": "task-a"}]},
                    "schema-beta": {"assigned_task_summaries": [{"task_name": "task-b"}]},
                },
                "challenger_eval_plan": [
                    {
                        "schema_id": "schema-alpha",
                        "candidate_mode": "conservative",
                        "task_names": ["task-a"],
                    }
                ],
            }

            result = self.module.materialize_next_round_pairs(
                package=package,
                output_dir=root / "materialized",
                skillsbench_root=skillsbench_root,
                inventory_path=inventory_path,
                official_results_path=official_path,
                render_template_path=render_template_path,
                run_id="round1-run",
                round_budget=3,
                oauth_file=root / "oauth-token",
                agent="claude-code",
                model="anthropic/claude-sonnet-4-5",
                schema_update_package_path=root / "schema_update_package.json",
                next_pair_plan_mode="challenger_eval",
            )

            self.assertEqual(result["manifest"]["next_pair_plan_mode"], "challenger_eval")
            self.assertEqual(result["manifest"]["pair_count"], 1)
            self.assertEqual(result["pair_plan"][0]["pair_id"], "task-a__schema-alpha")

    def test_run_outer_loop_optimization_builds_control_update_and_next_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            round0_root = root / "round0"
            global_status_path = round0_root / "reports" / "global-round0-status" / "global_pair_status.json"
            prompt_bank_path = root / "prompt-bank.json"
            inventory_path = root / "inventory.jsonl"
            official_path = root / "official.jsonl"
            render_template_path = root / "render.md"
            skillsbench_root = root / "skillsbench"
            for task_name in ("task-a", "task-b"):
                self._write_task(skillsbench_root, task_name)
            self._write_prompt_bank(prompt_bank_path)
            self._write_inventory(inventory_path, ["task-a", "task-b"])
            self._write_official_results(official_path, ["task-a", "task-b"])
            render_template_path.write_text("render")
            self._write_round0_inputs(round0_root, global_status_path)

            result = self.module.run_outer_loop_optimization(
                round0_root=round0_root,
                global_pair_status_path=global_status_path,
                prompt_bank_path=prompt_bank_path,
                task_cluster_inputs_path=inventory_path,
                control_plane_output_dir=root / "control",
                schema_update_output_dir=root / "schema-updates",
                next_materialized_root=root / "round1-materialized",
                skillsbench_root=skillsbench_root,
                inventory_path=inventory_path,
                official_results_path=official_path,
                render_template_path=render_template_path,
                oauth_file=root / "oauth-token",
                round_id="round0-test",
                next_round_id="round1-test",
                next_run_id="round1-run",
                round_budget=3,
                agent="claude-code",
                model="anthropic/claude-sonnet-4-5",
                rewrite_mode="deterministic",
                llm_model="anthropic/claude-sonnet-4-5",
                llm_timeout_sec=1.0,
                max_update_schemas=0,
                max_eval_tasks_per_schema=4,
                min_support_size=1,
                next_pair_plan_mode="full_matrix",
                allow_partial_assignment=False,
            )

            self.assertEqual(result["summary"]["next_pair_plan_mode"], "full_matrix")
            self.assertEqual(result["summary"]["next_round_pair_count"], 4)
            self.assertTrue((root / "control" / "control_plane_bundle.json").exists())
            self.assertTrue((root / "schema-updates" / "schema_update_package.json").exists())
            self.assertTrue((root / "round1-materialized" / "manifest.json").exists())
            self.assertTrue((root / "round1-materialized" / "pair_specs.jsonl").exists())
            materialized_manifest = json.loads((root / "round1-materialized" / "manifest.json").read_text())
            self.assertEqual(materialized_manifest["task_count"], 2)
            self.assertEqual(materialized_manifest["schema_count"], 2)


if __name__ == "__main__":
    unittest.main()

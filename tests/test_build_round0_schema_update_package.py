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
    / "build_round0_schema_update_package.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("build_round0_schema_update_package", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BuildRound0SchemaUpdatePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def _write_prompt_bank(self, root: Path) -> Path:
        prompt_bank_path = root / "prompt-bank.json"
        prompt_bank_path.write_text(
            json.dumps(
                {
                    "artifact_type": "skillx_prompt_bank",
                    "version": "v0.1",
                    "categories": [
                        {
                            "category_id": "schema-alpha",
                            "semantic_intent": "Alpha schema intent.",
                            "emphasize": ["alpha first principle"],
                            "avoid": ["alpha avoid"],
                            "expected_good_fit": ["alpha good"],
                            "expected_bad_fit": ["alpha bad"],
                            "meta_prompt": "alpha prompt",
                        },
                        {
                            "category_id": "schema-beta",
                            "semantic_intent": "Beta schema intent.",
                            "emphasize": ["beta first principle"],
                            "avoid": ["beta avoid"],
                            "expected_good_fit": ["beta good"],
                            "expected_bad_fit": ["beta bad"],
                            "meta_prompt": "beta prompt",
                        },
                    ],
                }
            )
        )
        return prompt_bank_path

    def _write_task_profiles(self, root: Path) -> Path:
        task_profiles_path = root / "task-profiles.jsonl"
        rows = [
            {
                "task_name": "task-a",
                "cluster_inputs": {
                    "semantic_contract": {
                        "task_object_seed": "schema-alpha",
                        "verifier_mode": "deterministic-output-contract",
                    },
                    "tool_topology": {
                        "workflow_topology": "staged-multi-step",
                        "tool_surface_regime": "tool-heavy-script-recommended",
                    },
                },
                "tags": {"primary_pattern": "pipeline", "secondary_patterns": ["tool-wrapper"]},
            },
            {
                "task_name": "task-b",
                "cluster_inputs": {
                    "semantic_contract": {
                        "task_object_seed": "schema-beta",
                        "verifier_mode": "benchmark-threshold",
                    },
                    "tool_topology": {
                        "workflow_topology": "single-step-with-review",
                        "tool_surface_regime": "tool-light",
                    },
                },
                "tags": {"primary_pattern": "reviewer", "secondary_patterns": ["reviewer"]},
            },
        ]
        task_profiles_path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
        return task_profiles_path

    def _write_control_bundle(self, root: Path) -> Path:
        bundle_path = root / "control-plane-bundle.json"
        bundle_path.write_text(
            json.dumps(
                {
                    "assignments": [
                        {
                            "task_name": "task-a",
                            "assignment_status": "assigned",
                            "assigned_categories": ["schema-alpha", "schema-beta"],
                            "assignment_confidence": "low",
                            "margin_pp": 1.0,
                        },
                        {
                            "task_name": "task-b",
                            "assignment_status": "assigned",
                            "assigned_category": "schema-alpha",
                            "assignment_confidence": "medium",
                            "margin_pp": 4.0,
                        },
                    ],
                    "score_matrix": {
                        "long_rows": [
                            {
                                "task_name": "task-a",
                                "schema_id": "schema-alpha",
                                "score": 80.0,
                                "reported_score": 80.0,
                                "delta_vs_c1_pp": 10.0,
                                "round_r0_to_best_delta_pp": 20.0,
                                "evidence_class": "measured",
                            },
                            {
                                "task_name": "task-a",
                                "schema_id": "schema-beta",
                                "score": 79.0,
                                "reported_score": 79.0,
                                "delta_vs_c1_pp": 9.0,
                                "round_r0_to_best_delta_pp": 18.0,
                                "evidence_class": "measured",
                            },
                            {
                                "task_name": "task-b",
                                "schema_id": "schema-alpha",
                                "score": 40.0,
                                "reported_score": 40.0,
                                "delta_vs_c1_pp": -15.0,
                                "round_r0_to_best_delta_pp": -5.0,
                                "evidence_class": "measured",
                                "failure_type": "VerifierFailure",
                                "failure_summary": "negative lift",
                            },
                            {
                                "task_name": "task-b",
                                "schema_id": "schema-beta",
                                "score": 42.0,
                                "reported_score": 42.0,
                                "delta_vs_c1_pp": -13.0,
                                "round_r0_to_best_delta_pp": -4.0,
                                "evidence_class": "measured",
                            },
                        ]
                    },
                }
            )
        )
        return bundle_path

    def test_builds_multi_assignment_evidence_and_candidate_bank(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            prompt_bank_path = self._write_prompt_bank(root)
            task_profiles_path = self._write_task_profiles(root)
            bundle_path = self._write_control_bundle(root)

            package = self.module.build_schema_update_package(
                control_plane_bundle_path=bundle_path,
                prompt_bank_path=prompt_bank_path,
                task_cluster_inputs_path=task_profiles_path,
                rewrite_mode="deterministic",
                llm_model="anthropic/claude-sonnet-4-5",
                llm_timeout_sec=1.0,
                llm_work_dir=None,
                round_id="round0-test",
                next_round_id="round1-test",
                min_support_size=1,
                low_margin_pp=5.0,
                boundary_margin_pp=10.0,
                max_update_schemas=0,
                max_eval_tasks_per_schema=5,
            )

            evidence = package["schema_evidence_bundles"]
            self.assertEqual(evidence["schema-alpha"]["support_size"], 2)
            self.assertEqual(evidence["schema-beta"]["support_size"], 1)
            self.assertEqual(evidence["schema-beta"]["assigned_task_summaries"][0]["task_name"], "task-a")

            plan_by_schema = {row["category_id"]: row for row in package["round_update_plan"]}
            self.assertEqual(plan_by_schema["schema-alpha"]["action"], "update")
            self.assertEqual(plan_by_schema["schema-beta"]["action"], "update")
            self.assertEqual(plan_by_schema["schema-alpha"]["recommended_challenger_mode"], "differentiating")
            self.assertEqual(package["rewrite_verification"]["status"], "passed")
            self.assertEqual(package["rewrite_verification"]["completed_rewrite_schema_count"], 2)

            candidate_bank = package["candidate_prompt_bank"]
            candidate_schema = {
                row["category_id"]: row for row in candidate_bank["categories"]
            }["schema-alpha"]
            self.assertEqual(candidate_schema["outer_loop_candidate_status"], "proposed_for_rerun")
            self.assertIn("hypothesized_primary_failure_modes", candidate_schema)
            self.assertIn("Outer-loop update mode:", candidate_schema["meta_prompt"])

            with tempfile.TemporaryDirectory() as outdir:
                outputs = self.module.write_schema_update_package(
                    package=package,
                    output_dir=Path(outdir),
                )
                self.assertTrue((Path(outdir) / "schema_update_package.json").exists())
                self.assertTrue((Path(outdir) / "rewrite_verification.json").exists())
                self.assertTrue((Path(outdir) / "round1_candidate_prompt_bank.json").exists())
                self.assertIn("summary_md", outputs)

    def test_freezes_schema_below_support_floor(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            prompt_bank_path = self._write_prompt_bank(root)
            task_profiles_path = self._write_task_profiles(root)
            bundle_path = self._write_control_bundle(root)

            package = self.module.build_schema_update_package(
                control_plane_bundle_path=bundle_path,
                prompt_bank_path=prompt_bank_path,
                task_cluster_inputs_path=task_profiles_path,
                rewrite_mode="deterministic",
                llm_model="anthropic/claude-sonnet-4-5",
                llm_timeout_sec=1.0,
                llm_work_dir=None,
                round_id="round0-test",
                next_round_id="round1-test",
                min_support_size=2,
                low_margin_pp=5.0,
                boundary_margin_pp=10.0,
                max_update_schemas=0,
                max_eval_tasks_per_schema=5,
            )

            plan_by_schema = {row["category_id"]: row for row in package["round_update_plan"]}
            self.assertEqual(plan_by_schema["schema-alpha"]["action"], "update")
            self.assertEqual(plan_by_schema["schema-beta"]["action"], "freeze")
            self.assertEqual(plan_by_schema["schema-beta"]["reason"], "freeze_low_support")

            candidate_schema = {
                row["category_id"]: row for row in package["candidate_prompt_bank"]["categories"]
            }["schema-beta"]
            self.assertNotIn("outer_loop_candidate_status", candidate_schema)
            self.assertEqual(candidate_schema["meta_prompt"], "beta prompt")

    def test_zero_support_floor_rewrites_all_schemas(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            prompt_bank_path = self._write_prompt_bank(root)
            task_profiles_path = self._write_task_profiles(root)
            bundle_path = self._write_control_bundle(root)

            package = self.module.build_schema_update_package(
                control_plane_bundle_path=bundle_path,
                prompt_bank_path=prompt_bank_path,
                task_cluster_inputs_path=task_profiles_path,
                rewrite_mode="deterministic",
                llm_model="anthropic/claude-sonnet-4-5",
                llm_timeout_sec=1.0,
                llm_work_dir=None,
                round_id="round0-test",
                next_round_id="round1-test",
                min_support_size=0,
                low_margin_pp=5.0,
                boundary_margin_pp=10.0,
                max_update_schemas=0,
                max_eval_tasks_per_schema=5,
            )

            plan_by_schema = {row["category_id"]: row for row in package["round_update_plan"]}
            self.assertEqual(plan_by_schema["schema-alpha"]["action"], "update")
            self.assertEqual(plan_by_schema["schema-beta"]["action"], "update")
            self.assertEqual(package["rewrite_verification"]["status"], "passed")
            self.assertEqual(package["rewrite_verification"]["expected_rewrite_schema_count"], 2)
            self.assertEqual(package["rewrite_verification"]["completed_rewrite_schema_count"], 2)

            candidate_schemas = {
                row["category_id"]: row for row in package["candidate_prompt_bank"]["categories"]
            }
            self.assertEqual(candidate_schemas["schema-alpha"]["outer_loop_candidate_status"], "proposed_for_rerun")
            self.assertEqual(candidate_schemas["schema-beta"]["outer_loop_candidate_status"], "proposed_for_rerun")

    def test_llm_rewrite_mode_accepts_remove_and_sharpen_operations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            prompt_bank_path = self._write_prompt_bank(root)
            task_profiles_path = self._write_task_profiles(root)
            bundle_path = self._write_control_bundle(root)

            def fake_llm_runner(prompt, response_schema, model_name, output_dir, timeout_sec):
                self.assertIn("CURRENT_SCHEMA", prompt)
                self.assertIn("EVIDENCE_BUNDLE", prompt)
                self.assertEqual(model_name, "anthropic/claude-sonnet-4-5")
                output_dir.mkdir(parents=True, exist_ok=True)
                return {
                    "operator_summary": {
                        "keep": ["alpha first principle"],
                        "add": ["add evidence-specific boundary handling"],
                        "remove": ["alpha avoid"],
                        "sharpen": ["alpha first principle -> alpha sharpened principle"],
                        "exclude": ["exclude mismatched beta-like tasks"],
                    },
                    "slot_edits": {
                        "emphasize": {
                            "add": ["add evidence-specific boundary handling"],
                            "remove": [],
                            "sharpen": [
                                {
                                    "old": "alpha first principle",
                                    "new": "alpha sharpened principle",
                                }
                            ],
                        },
                        "avoid": {
                            "add": ["avoid generic low-evidence broadening"],
                            "remove": ["alpha avoid"],
                            "sharpen": [],
                        },
                        "expected_good_fit": {"add": ["alpha-like verified workflows"], "remove": []},
                        "expected_bad_fit": {"add": ["beta-like reviewer tasks"], "remove": []},
                        "hypothesized_primary_failure_modes": {
                            "add": ["schema-boundary confusion"],
                            "remove": [],
                            "sharpen": [],
                        },
                    },
                    "challenger_guidance": {
                        "conservative": "apply only sharpened alpha principle",
                        "exploratory": "activate broader evidence handling",
                        "differentiating": "separate from schema-beta",
                    },
                    "expected_effect": ["better boundary behavior"],
                    "acceptance_notes": ["rerun before accepting"],
                }

            package = self.module.build_schema_update_package(
                control_plane_bundle_path=bundle_path,
                prompt_bank_path=prompt_bank_path,
                task_cluster_inputs_path=task_profiles_path,
                rewrite_mode="llm",
                llm_model="anthropic/claude-sonnet-4-5",
                llm_timeout_sec=1.0,
                llm_work_dir=root / "llm-runs",
                llm_json_runner=fake_llm_runner,
                round_id="round0-test",
                next_round_id="round1-test",
                min_support_size=2,
                low_margin_pp=5.0,
                boundary_margin_pp=10.0,
                max_update_schemas=0,
                max_eval_tasks_per_schema=5,
            )

            proposal = {
                row["category_id"]: row for row in package["schema_update_proposals"]
            }["schema-alpha"]
            self.assertEqual(proposal["rewrite_source"], "llm")
            self.assertEqual(proposal["slot_edits"]["avoid"]["remove"], ["alpha avoid"])

            candidate_schema = {
                row["category_id"]: row for row in package["candidate_prompt_bank"]["categories"]
            }["schema-alpha"]
            self.assertIn("alpha sharpened principle", candidate_schema["emphasize"])
            self.assertNotIn("alpha avoid", candidate_schema["avoid"])
            self.assertIn("avoid generic low-evidence broadening", candidate_schema["avoid"])


if __name__ == "__main__":
    unittest.main()

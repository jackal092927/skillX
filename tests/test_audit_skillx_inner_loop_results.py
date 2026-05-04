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
    / "audit_skillx_inner_loop_results.py"
)


def _load_module():
    scripts_dir = str(SCRIPT_PATH.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location("audit_skillx_inner_loop_results", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AuditSkillXInnerLoopResultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def _write_run_status(
        self,
        output_dir: Path,
        *,
        status: str,
        task_name: str,
        extra_lines: list[str] | None = None,
    ) -> None:
        lines = [
            f"- status: `{status}`",
            "- run_id: `demo-run`",
            f"- task: `{task_name}`",
            "- source_run_dir: `/tmp/source`",
            "- round_budget: `3`",
            "- orchestration_mode: `c4ar`",
        ]
        lines.extend(extra_lines or [])
        lines.append("- updated_at: `2026-05-04T00:00:00+00:00`")
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "RUN_STATUS.md").write_text("\n".join(lines) + "\n")

    def _write_scored_output(
        self,
        output_dir: Path,
        *,
        task_name: str,
        status: str = "completed",
        reward: float = 1.0,
        selected_round_index: int = 0,
        extra_status_lines: list[str] | None = None,
    ) -> None:
        self._write_run_status(
            output_dir,
            status=status,
            task_name=task_name,
            extra_lines=extra_status_lines,
        )
        round_dir = output_dir / "refine" / task_name / "rounds" / f"round-{selected_round_index}"
        (round_dir / "tune_check").mkdir(parents=True, exist_ok=True)
        (round_dir / "role_b").mkdir(parents=True, exist_ok=True)
        (round_dir / "tune_check" / "result.json").write_text(
            json.dumps(
                {
                    "reward": reward,
                    "exception_stats": {},
                    "classification": {"kind": "clean_success" if reward > 0 else "scientific_failure"},
                }
            )
        )
        (round_dir / "role_b" / "round_decision.json").write_text(
            json.dumps({"decision": "stop", "reason": "test"})
        )
        summary_path = output_dir / "refine" / task_name / "refine_summary.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(
                {
                    "task_id": task_name,
                    "selected": {
                        "round_index": selected_round_index,
                        "reward": reward,
                        "classification": {"kind": "clean_success" if reward > 0 else "scientific_failure"},
                    },
                }
            )
        )

    def test_audit_classifies_validity_and_writes_rerun_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            materialized_root = root / "materialized"
            log_dir = materialized_root / "launcher_logs" / "demo-run"
            log_dir.mkdir(parents=True)
            outputs = root / "outputs"
            pair_ids = [
                "task-clean__artifact-generation",
                "task-rate__artifact-generation",
                "task-codex__artifact-generation",
                "task-runtime__artifact-generation",
                "task-fail__artifact-generation",
                "task-skip__artifact-generation",
                "task-missing__artifact-generation",
            ]
            (materialized_root / "pair_specs.jsonl").write_text(
                "\n".join(
                    json.dumps(
                        {
                            "pair_id": pair_id,
                            "task_name": pair_id.split("__", 1)[0],
                            "schema_id": "artifact-generation",
                            "official_scores": {"no_skills": 0.0, "with_skills": 0.0},
                        }
                    )
                    for pair_id in pair_ids
                )
                + "\n"
            )

            result_rows = []
            for pair_id in pair_ids[:-1]:
                task_name = pair_id.split("__", 1)[0]
                output_dir = outputs / pair_id
                if pair_id == "task-fail__artifact-generation":
                    self._write_run_status(output_dir, status="failed", task_name=task_name)
                    (output_dir / "run_failure.json").write_text(
                        json.dumps(
                            {
                                "error_type": "RuntimeError",
                                "error_message": "expected exactly one trial dir under /tmp/job, found 0",
                                "failed_stage": "r0_guard",
                            }
                        )
                    )
                    launcher_status = "failed"
                    returncode = 1
                    runtime_profile = {"label": "primary-claude", "agent": "claude-code", "model": "anthropic/claude-sonnet-4-5"}
                    attempts = [{"runtime_profile": runtime_profile, "returncode": 1}]
                elif pair_id == "task-skip__artifact-generation":
                    self._write_run_status(output_dir, status="skipped_baseline_perfect", task_name=task_name)
                    launcher_status = "succeeded"
                    returncode = 0
                    runtime_profile = {"label": "primary-claude", "agent": "claude-code", "model": "anthropic/claude-sonnet-4-5"}
                    attempts = [{"runtime_profile": runtime_profile, "returncode": 0}]
                else:
                    status = "completed"
                    reward = 1.0
                    extra_status_lines: list[str] | None = None
                    if pair_id == "task-runtime__artifact-generation":
                        status = "completed_with_runtime_failures"
                        reward = 0.0
                        extra_status_lines = ["- runtime_failure_rounds: `R2, R3`"]
                    self._write_scored_output(
                        output_dir,
                        task_name=task_name,
                        status=status,
                        reward=reward,
                        extra_status_lines=extra_status_lines,
                    )
                    launcher_status = "succeeded"
                    returncode = 0
                    runtime_profile = {"label": "primary-claude", "agent": "claude-code", "model": "anthropic/claude-sonnet-4-5"}
                    attempts = [{"runtime_profile": runtime_profile, "returncode": 0}]
                    if pair_id == "task-rate__artifact-generation":
                        fallback_profile = {
                            "label": "fallback-claude-1",
                            "agent": "claude-code",
                            "model": "anthropic/claude-sonnet-4-5",
                        }
                        runtime_profile = fallback_profile
                        attempts = [
                            {"runtime_profile": {"label": "primary-claude", "agent": "claude-code", "model": "anthropic/claude-sonnet-4-5"}, "returncode": 1},
                            {"runtime_profile": fallback_profile, "returncode": 0},
                        ]
                        (output_dir / "rate_limit_signal.json").write_text(
                            json.dumps(
                                {
                                    "has_hard_signal": True,
                                    "hard_terms": ["api_error_status_429", "hit_your_limit"],
                                }
                            )
                        )
                    if pair_id == "task-codex__artifact-generation":
                        runtime_profile = {"label": "fallback-codex", "agent": "codex", "model": "gpt-5.4"}
                        attempts = [{"runtime_profile": runtime_profile, "returncode": 0}]

                result_rows.append(
                    {
                        "pair_id": pair_id,
                        "task_name": task_name,
                        "schema_id": "artifact-generation",
                        "status": launcher_status,
                        "stage": "run",
                        "returncode": returncode,
                        "output_dir": str(output_dir),
                        "runtime_profile": runtime_profile,
                        "attempts": attempts,
                    }
                )

            (log_dir / "summary.json").write_text(
                json.dumps(
                    {
                        "total_pairs": len(pair_ids),
                        "completed_pairs": len(result_rows),
                        "succeeded_pairs": 5,
                        "failed_pairs": 1,
                        "selected_pair_ids": pair_ids,
                        "results": result_rows,
                    }
                )
            )
            (log_dir / "events.ndjson").write_text("")

            audit = self.module.build_inner_loop_audit(
                materialized_root=materialized_root,
                run_label="demo-run",
            )

            self.assertEqual(audit["counts"]["total_pairs"], 7)
            self.assertEqual(
                set(audit["rerun_plan"]["required_pair_ids"]),
                {
                    "task-codex__artifact-generation",
                    "task-runtime__artifact-generation",
                    "task-fail__artifact-generation",
                    "task-missing__artifact-generation",
                },
            )

            rows = {row["pair_id"]: row for row in audit["pair_audits"]}
            self.assertEqual(rows["task-rate__artifact-generation"]["rerun_decision"], "none")
            self.assertIn("rate_limit_fallback", rows["task-rate__artifact-generation"]["issue_codes"])
            self.assertIn("claude_account_fallback", rows["task-rate__artifact-generation"]["issue_codes"])
            self.assertIn("basic_model_fallback", rows["task-codex__artifact-generation"]["issue_codes"])
            self.assertIn("missing_trial_dir", rows["task-fail__artifact-generation"]["issue_codes"])
            self.assertEqual(rows["task-skip__artifact-generation"]["validity"], "valid_intentional_skip")
            self.assertEqual(rows["task-missing__artifact-generation"]["run_status"], "not_started")

            audit_dir = root / "audit"
            artifacts = self.module.write_audit_artifacts(audit=audit, audit_dir=audit_dir)
            required_manifest = Path(artifacts["required_pair_manifest"])
            self.assertTrue(required_manifest.exists())
            self.assertEqual(
                set(json.loads(required_manifest.read_text())["selected_pair_ids"]),
                set(audit["rerun_plan"]["required_pair_ids"]),
            )
            required_script = Path(artifacts["required_rerun_script"])
            self.assertTrue(required_script.exists())
            self.assertIn("--pair-manifest", required_script.read_text())
            self.assertIn("Rerun Required", (audit_dir / "inner_loop_audit.md").read_text())

    def test_observed_round1_rerun_reference_examples(self) -> None:
        """Reference cases from the 2026-05 round1 first20 audit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            materialized_root = root / "materialized"
            log_dir = materialized_root / "launcher_logs" / "round1-reference"
            log_dir.mkdir(parents=True)
            outputs = root / "outputs"
            cases = [
                {
                    "pair_id": "adaptive-cruise-control__retrieval-heavy-synthesis",
                    "task_name": "adaptive-cruise-control",
                    "schema_id": "retrieval-heavy-synthesis",
                },
                {
                    "pair_id": "data-to-d3__retrieval-heavy-synthesis",
                    "task_name": "data-to-d3",
                    "schema_id": "retrieval-heavy-synthesis",
                },
                {
                    "pair_id": "3d-scan-calc__artifact-generation",
                    "task_name": "3d-scan-calc",
                    "schema_id": "artifact-generation",
                },
            ]
            (materialized_root / "pair_specs.jsonl").write_text(
                "\n".join(
                    json.dumps(
                        {
                            "pair_id": case["pair_id"],
                            "task_name": case["task_name"],
                            "schema_id": case["schema_id"],
                            "official_scores": {"no_skills": 0.0, "with_skills": 0.0},
                        }
                    )
                    for case in cases
                )
                + "\n"
            )

            results = []
            for case in cases:
                output_dir = outputs / case["pair_id"]
                if case["pair_id"] == "adaptive-cruise-control__retrieval-heavy-synthesis":
                    self._write_run_status(output_dir, status="failed", task_name=case["task_name"])
                    (output_dir / "run_failure.json").write_text(
                        json.dumps(
                            {
                                "error_type": "RuntimeError",
                                "error_message": "expected exactly one trial dir under /tmp/job, found 0",
                                "failed_stage": "r0_guard",
                            }
                        )
                    )
                    launcher_status = "failed"
                    returncode = 1
                elif case["pair_id"] == "data-to-d3__retrieval-heavy-synthesis":
                    self._write_scored_output(
                        output_dir,
                        task_name=case["task_name"],
                        status="completed_with_runtime_failures",
                        reward=0.0,
                        selected_round_index=0,
                        extra_status_lines=["- runtime_failure_rounds: `R2, R3`"],
                    )
                    launcher_status = "succeeded"
                    returncode = 0
                else:
                    self._write_scored_output(
                        output_dir,
                        task_name=case["task_name"],
                        status="completed_with_runtime_failures",
                        reward=1.0,
                        selected_round_index=2,
                        extra_status_lines=["- runtime_failure_rounds: `R0, R1`"],
                    )
                    launcher_status = "succeeded"
                    returncode = 0
                results.append(
                    {
                        "pair_id": case["pair_id"],
                        "task_name": case["task_name"],
                        "schema_id": case["schema_id"],
                        "status": launcher_status,
                        "stage": "run",
                        "returncode": returncode,
                        "output_dir": str(output_dir),
                        "runtime_profile": {
                            "label": "primary-claude",
                            "agent": "claude-code",
                            "model": "anthropic/claude-sonnet-4-5",
                        },
                    }
                )

            (log_dir / "summary.json").write_text(
                json.dumps(
                    {
                        "total_pairs": len(cases),
                        "completed_pairs": len(cases),
                        "succeeded_pairs": 2,
                        "failed_pairs": 1,
                        "selected_pair_ids": [case["pair_id"] for case in cases],
                        "results": results,
                    }
                )
            )
            (log_dir / "events.ndjson").write_text("")

            audit = self.module.build_inner_loop_audit(
                materialized_root=materialized_root,
                run_label="round1-reference",
            )
            rows = {row["pair_id"]: row for row in audit["pair_audits"]}

            self.assertEqual(
                rows["adaptive-cruise-control__retrieval-heavy-synthesis"]["rerun_decision"],
                "required",
            )
            self.assertIn(
                "missing_trial_dir",
                rows["adaptive-cruise-control__retrieval-heavy-synthesis"]["issue_codes"],
            )
            self.assertEqual(
                rows["data-to-d3__retrieval-heavy-synthesis"]["rerun_decision"],
                "required",
            )
            self.assertEqual(
                rows["3d-scan-calc__artifact-generation"]["rerun_decision"],
                "recommended",
            )
            self.assertEqual(
                audit["rerun_plan"]["required_pair_ids"],
                [
                    "adaptive-cruise-control__retrieval-heavy-synthesis",
                    "data-to-d3__retrieval-heavy-synthesis",
                ],
            )
            self.assertEqual(
                audit["rerun_plan"]["recommended_pair_ids"],
                ["3d-scan-calc__artifact-generation"],
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from dataclasses import asdict
import json
import tempfile
import unittest
from pathlib import Path

import path_setup
from skillx.c4ar.orchestrator import (
    ExecutorOutputs,
    OrchestratorConfig,
    OrchestratorInputs,
    run_c4ar_round,
)
from skillx.c4ar.role_a import RoleAConfig
from skillx.c4ar.role_b import RoleBConfig


class C4arOrchestratorTests(unittest.TestCase):
    def test_orchestrator_runs_c_then_a_then_b_and_writes_event_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            current_skillpack_dir = tmp / "round-0" / "skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# R0 Skill\n")

            calls: list[str] = []

            def executor_runner(inputs):
                calls.append("c")
                session_log = Path(inputs.output_dir) / "executor" / "session.log"
                session_log.parent.mkdir(parents=True)
                session_log.write_text("tool=read_file path=skill.md\n")
                verifier = Path(inputs.output_dir) / "executor" / "verifier_summary.json"
                verifier.write_text(json.dumps({"reward": 0.8444, "failed_tests": 3}) + "\n")
                return ExecutorOutputs(
                    session_log_path=str(session_log),
                    verifier_summary_path=str(verifier),
                    current_skillpack_dir=inputs.skillpack_dir,
                    current_bundle_path=None,
                )

            def role_a_runner(inputs, **kwargs):
                calls.append("a")
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

            def role_b_runner(inputs, **kwargs):
                calls.append("b")
                out_dir = Path(inputs.output_dir)
                next_skill = out_dir / "next_skillpack" / "skills" / "analysis"
                next_skill.mkdir(parents=True)
                (next_skill / "SKILL.md").write_text("# R1 Skill\n")
                refine_plan = {
                    "task_id": inputs.task_id,
                    "round_index": inputs.round_index,
                    "role": "role_b",
                    "model_name": "gpt-5.4",
                    "summary": "tighten aggregation guidance",
                    "atomic_operations": [
                        {
                            "op_id": "op-1",
                            "action_type": "rewrite_block",
                            "target_id": "guidance.block_2",
                            "rationale": "narrow aggregation guidance",
                            "expected_effect": "reduce zero-spend rows",
                            "risk": "may over-tighten",
                            "status": "planned",
                        }
                    ],
                }
                manifest = {
                    "task_id": inputs.task_id,
                    "round_index": inputs.round_index,
                    "role": "role_b",
                    "model_name": "gpt-5.4",
                    "skillpack_dir": str(out_dir / "next_skillpack"),
                    "skill_files": ["skills/analysis/SKILL.md"],
                    "prompt_invariant": True,
                    "derived_from_round": inputs.round_index,
                }
                decision = {
                    "task_id": inputs.task_id,
                    "round_index": inputs.round_index,
                    "role": "role_b",
                    "model_name": "gpt-5.4",
                    "decision": "continue",
                    "reason": "candidate prepared",
                    "next_round_index": 1,
                    "next_skillpack_dir": str(out_dir / "next_skillpack"),
                }
                (out_dir / "refine_plan.json").write_text(json.dumps(refine_plan) + "\n")
                (out_dir / "refine_plan.md").write_text("# Refine Plan\n")
                (out_dir / "next_skillpack_manifest.json").write_text(json.dumps(manifest) + "\n")
                (out_dir / "round_decision.json").write_text(json.dumps(decision) + "\n")
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

            outputs = run_c4ar_round(
                OrchestratorInputs(
                    task_id="trend-anomaly-causal-inference",
                    round_index=0,
                    task_prompt_path=str(tmp / "task_prompt.md"),
                    current_skillpack_dir=str(tmp / "round-0" / "skillpack"),
                    current_bundle_path=None,
                    round_root_dir=str(tmp / "orchestrator_round"),
                ),
                config=OrchestratorConfig(),
                executor_runner=executor_runner,
                role_a_runner=role_a_runner,
                role_b_runner=role_b_runner,
            )

            self.assertEqual(calls, ["c", "a", "b"])
            self.assertEqual(outputs.round_decision.decision, "continue")
            self.assertTrue(Path(outputs.event_log_path).exists())
            events = [json.loads(line) for line in Path(outputs.event_log_path).read_text().splitlines() if line.strip()]
            event_types = [event["event_type"] for event in events]
            self.assertIn("executor_completed", event_types)
            self.assertIn("role_a_completed", event_types)
            self.assertIn("role_b_completed", event_types)

    def test_orchestrator_stops_on_malformed_role_a_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            current_skillpack_dir = tmp / "round-0" / "skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# R0 Skill\n")

            calls: list[str] = []

            def executor_runner(inputs):
                calls.append("c")
                session_log = Path(inputs.output_dir) / "executor" / "session.log"
                session_log.parent.mkdir(parents=True)
                session_log.write_text("tool=read_file path=skill.md\n")
                verifier = Path(inputs.output_dir) / "executor" / "verifier_summary.json"
                verifier.write_text(json.dumps({"reward": 0.8444, "failed_tests": 3}) + "\n")
                return ExecutorOutputs(
                    session_log_path=str(session_log),
                    verifier_summary_path=str(verifier),
                    current_skillpack_dir=inputs.skillpack_dir,
                    current_bundle_path=None,
                )

            def role_a_runner(inputs, **kwargs):
                calls.append("a")
                out_dir = Path(inputs.output_dir)
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "session_evidence.json").write_text(json.dumps({"task_id": ""}) + "\n")
                (out_dir / "session_evidence.md").write_text("# Session-Derived Evidence\n")
                return type(
                    "RoleAResult",
                    (),
                    {
                        "json_path": str(out_dir / "session_evidence.json"),
                        "markdown_path": str(out_dir / "session_evidence.md"),
                    },
                )()

            def role_b_runner(inputs, **kwargs):
                calls.append("b")
                raise AssertionError("Role B should not be called when Role A handoff is malformed")

            with self.assertRaises(ValueError):
                run_c4ar_round(
                    OrchestratorInputs(
                        task_id="trend-anomaly-causal-inference",
                        round_index=0,
                        task_prompt_path=str(tmp / "task_prompt.md"),
                        current_skillpack_dir=str(tmp / "round-0" / "skillpack"),
                        current_bundle_path=None,
                        round_root_dir=str(tmp / "orchestrator_round"),
                    ),
                    config=OrchestratorConfig(),
                    executor_runner=executor_runner,
                    role_a_runner=role_a_runner,
                    role_b_runner=role_b_runner,
                )

            self.assertEqual(calls, ["c", "a"])

    def test_orchestrator_passes_only_executor_contract_fields_to_role_c(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            current_skillpack_dir = tmp / "round-0" / "skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# R0 Skill\n")
            captured: dict[str, object] = {}

            def executor_runner(inputs):
                captured.update(asdict(inputs))
                session_log = Path(inputs.output_dir) / "executor" / "session.log"
                session_log.parent.mkdir(parents=True)
                session_log.write_text("tool=read_file path=skill.md\n")
                verifier = Path(inputs.output_dir) / "executor" / "verifier_summary.json"
                verifier.write_text(json.dumps({"reward": 0.8444, "failed_tests": 3}) + "\n")
                return ExecutorOutputs(
                    session_log_path=str(session_log),
                    verifier_summary_path=str(verifier),
                    current_skillpack_dir=inputs.skillpack_dir,
                    current_bundle_path=None,
                )

            def role_a_runner(inputs, **kwargs):
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
                return type("RoleAResult", (), {"json_path": str(out_dir / "session_evidence.json"), "markdown_path": str(out_dir / "session_evidence.md")})()

            def role_b_runner(inputs, **kwargs):
                out_dir = Path(inputs.output_dir)
                next_skill = out_dir / "next_skillpack" / "skills" / "analysis"
                next_skill.mkdir(parents=True)
                (next_skill / "SKILL.md").write_text("# R1 Skill\n")
                (out_dir / "refine_plan.json").write_text(json.dumps({"task_id": inputs.task_id, "round_index": inputs.round_index, "role": "role_b", "model_name": "gpt-5.4", "summary": "x", "atomic_operations": []}) + "\n")
                (out_dir / "refine_plan.md").write_text("# Refine Plan\n")
                (out_dir / "next_skillpack_manifest.json").write_text(json.dumps({"task_id": inputs.task_id, "round_index": inputs.round_index, "role": "role_b", "model_name": "gpt-5.4", "skillpack_dir": str(out_dir / "next_skillpack"), "skill_files": ["skills/analysis/SKILL.md"], "prompt_invariant": True, "derived_from_round": inputs.round_index}) + "\n")
                (out_dir / "round_decision.json").write_text(json.dumps({"task_id": inputs.task_id, "round_index": inputs.round_index, "role": "role_b", "model_name": "gpt-5.4", "decision": "continue", "reason": "candidate prepared", "next_round_index": 1, "next_skillpack_dir": str(out_dir / "next_skillpack")}) + "\n")
                return type("RoleBResult", (), {"refine_plan_json_path": str(out_dir / "refine_plan.json"), "refine_plan_markdown_path": str(out_dir / "refine_plan.md"), "next_skillpack_manifest_json_path": str(out_dir / "next_skillpack_manifest.json"), "round_decision_json_path": str(out_dir / "round_decision.json"), "next_skillpack_dir": str(out_dir / "next_skillpack")})()

            run_c4ar_round(
                OrchestratorInputs(
                    task_id="trend-anomaly-causal-inference",
                    round_index=0,
                    task_prompt_path=str(tmp / "task_prompt.md"),
                    current_skillpack_dir=str(tmp / "round-0" / "skillpack"),
                    current_bundle_path=None,
                    round_root_dir=str(tmp / "orchestrator_round"),
                ),
                config=OrchestratorConfig(),
                executor_runner=executor_runner,
                role_a_runner=role_a_runner,
                role_b_runner=role_b_runner,
            )

            self.assertEqual(
                set(captured.keys()),
                {"task_id", "round_index", "task_prompt_path", "skillpack_dir", "bundle_path", "output_dir"},
            )
            self.assertNotIn("session_evidence_path", captured)
            self.assertNotIn("refine_plan_json_path", captured)
            self.assertNotIn("round_decision_json_path", captured)

    def test_orchestrator_passes_role_configs_to_role_a_and_role_b(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            current_skillpack_dir = tmp / "round-0" / "skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# R0 Skill\n")
            seen: dict[str, object] = {}

            def executor_runner(inputs):
                session_log = Path(inputs.output_dir) / "executor" / "session.log"
                session_log.parent.mkdir(parents=True)
                session_log.write_text("tool=read_file path=skill.md\n")
                verifier = Path(inputs.output_dir) / "executor" / "verifier_summary.json"
                verifier.write_text(json.dumps({"reward": 0.8444, "failed_tests": 3}) + "\n")
                return ExecutorOutputs(
                    session_log_path=str(session_log),
                    verifier_summary_path=str(verifier),
                    current_skillpack_dir=inputs.skillpack_dir,
                    current_bundle_path=None,
                )

            def role_a_runner(inputs, **kwargs):
                seen["role_a_config"] = kwargs.get("config")
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
                return type("RoleAResult", (), {"json_path": str(out_dir / "session_evidence.json"), "markdown_path": str(out_dir / "session_evidence.md")})()

            def role_b_runner(inputs, **kwargs):
                seen["role_b_config"] = kwargs.get("config")
                out_dir = Path(inputs.output_dir)
                next_skill = out_dir / "next_skillpack" / "skills" / "analysis"
                next_skill.mkdir(parents=True)
                (next_skill / "SKILL.md").write_text("# R1 Skill\n")
                (out_dir / "refine_plan.json").write_text(json.dumps({"task_id": inputs.task_id, "round_index": inputs.round_index, "role": "role_b", "model_name": "gpt-5.4", "summary": "x", "atomic_operations": []}) + "\n")
                (out_dir / "refine_plan.md").write_text("# Refine Plan\n")
                (out_dir / "next_skillpack_manifest.json").write_text(json.dumps({"task_id": inputs.task_id, "round_index": inputs.round_index, "role": "role_b", "model_name": "gpt-5.4", "skillpack_dir": str(out_dir / "next_skillpack"), "skill_files": ["skills/analysis/SKILL.md"], "prompt_invariant": True, "derived_from_round": inputs.round_index}) + "\n")
                (out_dir / "round_decision.json").write_text(json.dumps({"task_id": inputs.task_id, "round_index": inputs.round_index, "role": "role_b", "model_name": "gpt-5.4", "decision": "continue", "reason": "candidate prepared", "next_round_index": 1, "next_skillpack_dir": str(out_dir / "next_skillpack")}) + "\n")
                return type("RoleBResult", (), {"refine_plan_json_path": str(out_dir / "refine_plan.json"), "refine_plan_markdown_path": str(out_dir / "refine_plan.md"), "next_skillpack_manifest_json_path": str(out_dir / "next_skillpack_manifest.json"), "round_decision_json_path": str(out_dir / "round_decision.json"), "next_skillpack_dir": str(out_dir / "next_skillpack")})()

            role_a_config = RoleAConfig(model_name="codex-5.3", playbook_path="/tmp/role-a-playbook.md")
            role_b_config = RoleBConfig(model_name="gpt-5.4", playbook_path="/tmp/role-b-playbook.md")

            run_c4ar_round(
                OrchestratorInputs(
                    task_id="trend-anomaly-causal-inference",
                    round_index=0,
                    task_prompt_path=str(tmp / "task_prompt.md"),
                    current_skillpack_dir=str(tmp / "round-0" / "skillpack"),
                    current_bundle_path=None,
                    round_root_dir=str(tmp / "orchestrator_round"),
                ),
                config=OrchestratorConfig(role_a_config=role_a_config, role_b_config=role_b_config),
                executor_runner=executor_runner,
                role_a_runner=role_a_runner,
                role_b_runner=role_b_runner,
            )

            self.assertEqual(seen["role_a_config"], role_a_config)
            self.assertEqual(seen["role_b_config"], role_b_config)


if __name__ == "__main__":
    unittest.main()

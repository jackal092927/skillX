from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import path_setup
from skillx.c4ar.role_b import RoleBConfig, RoleBInputs, run_role_b


class C4arRoleBTests(unittest.TestCase):
    def test_role_b_requires_playbook_without_custom_model_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verifier_summary = tmp / "verifier_summary.json"
            verifier_summary.write_text(json.dumps({"reward": 0.8444, "failed_tests": 3}) + "\n")
            session_evidence = tmp / "session_evidence.json"
            session_evidence.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 0,
                        "role": "role_a",
                        "model_name": "codex-5.3",
                        "source_log_paths": ["/tmp/session.log"],
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": ["/tmp/session.log:10"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            current_skillpack_dir = tmp / "current_skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# Skill\n")

            with self.assertRaises(ValueError):
                run_role_b(
                    RoleBInputs(
                        task_id="trend-anomaly-causal-inference",
                        round_index=0,
                        verifier_summary_path=str(verifier_summary),
                        session_evidence_path=str(session_evidence),
                        current_skillpack_dir=str(tmp / "current_skillpack"),
                        prior_round_summary_path=None,
                        output_dir=str(tmp / "role_b"),
                    ),
                    config=RoleBConfig(model_name="gpt-5.4"),
                )

    def test_role_b_reads_inputs_and_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verifier_summary = tmp / "verifier_summary.json"
            verifier_summary.write_text(json.dumps({"reward": 0.8444, "failed_tests": 3}) + "\n")
            session_evidence = tmp / "session_evidence.json"
            session_evidence.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 0,
                        "role": "role_a",
                        "model_name": "codex-5.3",
                        "source_log_paths": ["/tmp/session.log"],
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": ["/tmp/session.log:10"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            current_skillpack_dir = tmp / "current_skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# Skill\n")
            prior_round_summary = tmp / "prior_round_summary.json"
            prior_round_summary.write_text(json.dumps({"selected_reward": 0.8444}) + "\n")

            calls: list[tuple[str, int]] = []

            def runner(inputs, config, output_dir):
                calls.append((inputs.task_id, inputs.round_index))
                next_skillpack_dir = output_dir / "next_skillpack" / "skills" / "analysis"
                next_skillpack_dir.mkdir(parents=True)
                (next_skillpack_dir / "SKILL.md").write_text("# Refined Skill\n")
                return {
                    "refine_plan": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "summary": "tighten aggregation guidance",
                        "atomic_operations": [
                            {
                                "op_id": "op-1",
                                "action_type": "rewrite_block",
                                "target_id": "guidance.block_2",
                                "rationale": "narrow aggregation guidance",
                                "expected_effect": "fewer zero-spend rows",
                                "risk": "may over-tighten",
                                "status": "planned",
                            }
                        ],
                    },
                    "next_skillpack_manifest": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "skillpack_dir": str(output_dir / "next_skillpack"),
                        "skill_files": ["skills/analysis/SKILL.md"],
                        "prompt_invariant": True,
                        "derived_from_round": inputs.round_index,
                    },
                    "round_decision": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "decision": "continue",
                        "reason": "candidate prepared",
                        "next_round_index": 1,
                        "next_skillpack_dir": str(output_dir / "next_skillpack"),
                    },
                }

            outputs = run_role_b(
                RoleBInputs(
                    task_id="trend-anomaly-causal-inference",
                    round_index=0,
                    verifier_summary_path=str(verifier_summary),
                    session_evidence_path=str(session_evidence),
                    current_skillpack_dir=str(tmp / "current_skillpack"),
                    prior_round_summary_path=str(prior_round_summary),
                    output_dir=str(tmp / "role_b"),
                ),
                config=RoleBConfig(model_name="gpt-5.4"),
                model_runner=runner,
            )

            self.assertEqual(calls, [("trend-anomaly-causal-inference", 0)])
            self.assertTrue(Path(outputs.refine_plan_json_path).exists())
            self.assertTrue(Path(outputs.refine_plan_markdown_path).exists())
            self.assertTrue(Path(outputs.next_skillpack_manifest_json_path).exists())
            self.assertTrue(Path(outputs.round_decision_json_path).exists())
            self.assertTrue(Path(outputs.next_skillpack_dir, "skills", "analysis", "SKILL.md").exists())
            payload = json.loads(Path(outputs.refine_plan_json_path).read_text())
            self.assertEqual(payload["summary"], "tighten aggregation guidance")

    def test_role_b_fails_if_next_skillpack_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verifier_summary = tmp / "verifier_summary.json"
            verifier_summary.write_text(json.dumps({"reward": 0.8444}) + "\n")
            session_evidence = tmp / "session_evidence.json"
            session_evidence.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 0,
                        "role": "role_a",
                        "model_name": "codex-5.3",
                        "source_log_paths": ["/tmp/session.log"],
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": ["/tmp/session.log:10"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            current_skillpack_dir = tmp / "current_skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# Skill\n")

            def runner(inputs, config, output_dir):
                return {
                    "refine_plan": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "summary": "tighten aggregation guidance",
                        "atomic_operations": [],
                    },
                    "next_skillpack_manifest": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "skillpack_dir": str(output_dir / "next_skillpack"),
                        "skill_files": ["skills/analysis/SKILL.md"],
                        "prompt_invariant": True,
                        "derived_from_round": inputs.round_index,
                    },
                    "round_decision": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "decision": "continue",
                        "reason": "candidate prepared",
                        "next_round_index": 1,
                        "next_skillpack_dir": str(output_dir / "next_skillpack"),
                    },
                }

            with self.assertRaises(FileNotFoundError):
                run_role_b(
                    RoleBInputs(
                        task_id="trend-anomaly-causal-inference",
                        round_index=0,
                        verifier_summary_path=str(verifier_summary),
                        session_evidence_path=str(session_evidence),
                        current_skillpack_dir=str(tmp / "current_skillpack"),
                        prior_round_summary_path=None,
                        output_dir=str(tmp / "role_b"),
                    ),
                    model_runner=runner,
                )

    def test_role_b_rejects_invalid_model_runner_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verifier_summary = tmp / "verifier_summary.json"
            verifier_summary.write_text(json.dumps({"reward": 0.8444}) + "\n")
            session_evidence = tmp / "session_evidence.json"
            session_evidence.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 0,
                        "role": "role_a",
                        "model_name": "codex-5.3",
                        "source_log_paths": ["/tmp/session.log"],
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": ["/tmp/session.log:10"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            current_skillpack_dir = tmp / "current_skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# Skill\n")

            def runner(inputs, config, output_dir):
                return {
                    "refine_plan": {
                        "task_id": "",
                        "round_index": -1,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "summary": "",
                        "atomic_operations": [],
                    },
                    "next_skillpack_manifest": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "skillpack_dir": str(output_dir / "next_skillpack"),
                        "skill_files": ["skills/analysis/SKILL.md"],
                        "prompt_invariant": True,
                        "derived_from_round": inputs.round_index,
                    },
                    "round_decision": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "decision": "continue",
                        "reason": "candidate prepared",
                        "next_round_index": 1,
                        "next_skillpack_dir": str(output_dir / "next_skillpack"),
                    },
                }

            with self.assertRaises(ValueError):
                run_role_b(
                    RoleBInputs(
                        task_id="trend-anomaly-causal-inference",
                        round_index=0,
                        verifier_summary_path=str(verifier_summary),
                        session_evidence_path=str(session_evidence),
                        current_skillpack_dir=str(tmp / "current_skillpack"),
                        prior_round_summary_path=None,
                        output_dir=str(tmp / "role_b"),
                    ),
                    model_runner=runner,
                )

    def test_role_b_rejects_misaligned_output_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verifier_summary = tmp / "verifier_summary.json"
            verifier_summary.write_text(json.dumps({"reward": 0.8444}) + "\n")
            session_evidence = tmp / "session_evidence.json"
            session_evidence.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 0,
                        "role": "role_a",
                        "model_name": "codex-5.3",
                        "source_log_paths": ["/tmp/session.log"],
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": ["/tmp/session.log:10"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            current_skillpack_dir = tmp / "current_skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# Skill\n")

            def runner(inputs, config, output_dir):
                next_skillpack_dir = output_dir / "next_skillpack" / "skills" / "analysis"
                next_skillpack_dir.mkdir(parents=True)
                (next_skillpack_dir / "SKILL.md").write_text("# Refined Skill\n")
                return {
                    "refine_plan": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "summary": "tighten aggregation guidance",
                        "atomic_operations": [],
                    },
                    "next_skillpack_manifest": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "skillpack_dir": str(output_dir / "next_skillpack"),
                        "skill_files": ["skills/analysis/SKILL.md"],
                        "prompt_invariant": True,
                        "derived_from_round": inputs.round_index,
                    },
                    "round_decision": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "decision": "continue",
                        "reason": "candidate prepared",
                        "next_round_index": 1,
                        "next_skillpack_dir": str(output_dir / "different_skillpack"),
                    },
                }

            with self.assertRaises(ValueError):
                run_role_b(
                    RoleBInputs(
                        task_id="trend-anomaly-causal-inference",
                        round_index=0,
                        verifier_summary_path=str(verifier_summary),
                        session_evidence_path=str(session_evidence),
                        current_skillpack_dir=str(tmp / "current_skillpack"),
                        prior_round_summary_path=None,
                        output_dir=str(tmp / "role_b"),
                    ),
                    model_runner=runner,
                )

    def test_role_b_rejects_role_or_model_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verifier_summary = tmp / "verifier_summary.json"
            verifier_summary.write_text(json.dumps({"reward": 0.8444}) + "\n")
            session_evidence = tmp / "session_evidence.json"
            session_evidence.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 0,
                        "role": "role_a",
                        "model_name": "codex-5.3",
                        "source_log_paths": ["/tmp/session.log"],
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": ["/tmp/session.log:10"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            current_skillpack_dir = tmp / "current_skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# Skill\n")

            def runner(inputs, config, output_dir):
                next_skillpack_dir = output_dir / "next_skillpack" / "skills" / "analysis"
                next_skillpack_dir.mkdir(parents=True)
                (next_skillpack_dir / "SKILL.md").write_text("# Refined Skill\n")
                return {
                    "refine_plan": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": "role_a",
                        "model_name": "codex-5.3",
                        "summary": "tighten aggregation guidance",
                        "atomic_operations": [],
                    },
                    "next_skillpack_manifest": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "skillpack_dir": str(output_dir / "next_skillpack"),
                        "skill_files": ["skills/analysis/SKILL.md"],
                        "prompt_invariant": True,
                        "derived_from_round": inputs.round_index,
                    },
                    "round_decision": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "decision": "continue",
                        "reason": "candidate prepared",
                        "next_round_index": 1,
                        "next_skillpack_dir": str(output_dir / "next_skillpack"),
                    },
                }

            with self.assertRaises(ValueError):
                run_role_b(
                    RoleBInputs(
                        task_id="trend-anomaly-causal-inference",
                        round_index=0,
                        verifier_summary_path=str(verifier_summary),
                        session_evidence_path=str(session_evidence),
                        current_skillpack_dir=str(tmp / "current_skillpack"),
                        prior_round_summary_path=None,
                        output_dir=str(tmp / "role_b"),
                    ),
                    model_runner=runner,
                )

    def test_role_b_accepts_consistent_emitted_model_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verifier_summary = tmp / "verifier_summary.json"
            verifier_summary.write_text(json.dumps({"reward": 0.95}) + "\n")
            session_evidence = tmp / "session_evidence.json"
            session_evidence.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 0,
                        "role": "role_a",
                        "model_name": "claude-sonnet-4-5-20250929",
                        "source_log_paths": ["/tmp/session.log"],
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": ["/tmp/session.log:10"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            current_skillpack_dir = tmp / "current_skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# Skill\n")

            def runner(inputs, config, output_dir):
                next_skillpack_dir = output_dir / "next_skillpack" / "skills" / "analysis"
                next_skillpack_dir.mkdir(parents=True)
                (next_skillpack_dir / "SKILL.md").write_text("# Refined Skill\n")
                emitted_model_name = "gpt-5-codex"
                return {
                    "refine_plan": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": emitted_model_name,
                        "summary": "tighten aggregation guidance",
                        "atomic_operations": [],
                    },
                    "next_skillpack_manifest": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": emitted_model_name,
                        "skillpack_dir": str(output_dir / "next_skillpack"),
                        "skill_files": ["skills/analysis/SKILL.md"],
                        "prompt_invariant": True,
                        "derived_from_round": inputs.round_index,
                    },
                    "round_decision": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": emitted_model_name,
                        "decision": "continue",
                        "reason": "candidate prepared",
                        "next_round_index": 1,
                        "next_skillpack_dir": str(output_dir / "next_skillpack"),
                    },
                }

            outputs = run_role_b(
                RoleBInputs(
                    task_id="trend-anomaly-causal-inference",
                    round_index=0,
                    verifier_summary_path=str(verifier_summary),
                    session_evidence_path=str(session_evidence),
                    current_skillpack_dir=str(tmp / "current_skillpack"),
                    prior_round_summary_path=None,
                    output_dir=str(tmp / "role_b"),
                ),
                config=RoleBConfig(model_name="gpt-5.4"),
                model_runner=runner,
            )

            self.assertEqual(outputs.refine_plan.model_name, "gpt-5-codex")
            self.assertEqual(outputs.next_skillpack_manifest.model_name, "gpt-5-codex")
            self.assertEqual(outputs.round_decision.model_name, "gpt-5-codex")

    def test_role_b_rejects_model_name_drift_across_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verifier_summary = tmp / "verifier_summary.json"
            verifier_summary.write_text(json.dumps({"reward": 0.95}) + "\n")
            session_evidence = tmp / "session_evidence.json"
            session_evidence.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 0,
                        "role": "role_a",
                        "model_name": "claude-sonnet-4-5-20250929",
                        "source_log_paths": ["/tmp/session.log"],
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": ["/tmp/session.log:10"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            current_skillpack_dir = tmp / "current_skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# Skill\n")

            def runner(inputs, config, output_dir):
                next_skillpack_dir = output_dir / "next_skillpack" / "skills" / "analysis"
                next_skillpack_dir.mkdir(parents=True)
                (next_skillpack_dir / "SKILL.md").write_text("# Refined Skill\n")
                return {
                    "refine_plan": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": "gpt-5-codex",
                        "summary": "tighten aggregation guidance",
                        "atomic_operations": [],
                    },
                    "next_skillpack_manifest": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": "gpt-5.4",
                        "skillpack_dir": str(output_dir / "next_skillpack"),
                        "skill_files": ["skills/analysis/SKILL.md"],
                        "prompt_invariant": True,
                        "derived_from_round": inputs.round_index,
                    },
                    "round_decision": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": "gpt-5-codex",
                        "decision": "continue",
                        "reason": "candidate prepared",
                        "next_round_index": 1,
                        "next_skillpack_dir": str(output_dir / "next_skillpack"),
                    },
                }

            with self.assertRaises(ValueError):
                run_role_b(
                    RoleBInputs(
                        task_id="trend-anomaly-causal-inference",
                        round_index=0,
                        verifier_summary_path=str(verifier_summary),
                        session_evidence_path=str(session_evidence),
                        current_skillpack_dir=str(tmp / "current_skillpack"),
                        prior_round_summary_path=None,
                        output_dir=str(tmp / "role_b"),
                    ),
                    config=RoleBConfig(model_name="gpt-5.4"),
                    model_runner=runner,
                )

    def test_role_b_normalizes_absolute_skill_file_paths_within_skillpack(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verifier_summary = tmp / "verifier_summary.json"
            verifier_summary.write_text(json.dumps({"reward": 0.95}) + "\n")
            session_evidence = tmp / "session_evidence.json"
            session_evidence.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 0,
                        "role": "role_a",
                        "model_name": "claude-sonnet-4-5-20250929",
                        "source_log_paths": ["/tmp/session.log"],
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": ["/tmp/session.log:10"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            current_skillpack_dir = tmp / "current_skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# Skill\n")

            def runner(inputs, config, output_dir):
                next_skillpack_dir = output_dir / "next_skillpack" / "skills" / "analysis"
                next_skillpack_dir.mkdir(parents=True)
                skill_file = next_skillpack_dir / "SKILL.md"
                skill_file.write_text("# Refined Skill\n")
                return {
                    "refine_plan": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "summary": "tighten aggregation guidance",
                        "atomic_operations": [
                            {
                                "op_id": "op-1",
                                "action_type": "rewrite_block",
                                "target_id": "guidance.block_2",
                                "rationale": "normalize manifest paths",
                                "expected_effect": "stable manifest contract",
                                "risk": "low",
                                "status": "applied",
                            }
                        ],
                    },
                    "next_skillpack_manifest": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "skillpack_dir": str(output_dir / "next_skillpack"),
                        "skill_files": [str(skill_file)],
                        "prompt_invariant": True,
                        "derived_from_round": inputs.round_index,
                    },
                    "round_decision": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "decision": "continue",
                        "reason": "candidate prepared",
                        "next_round_index": 1,
                        "next_skillpack_dir": str(output_dir / "next_skillpack"),
                    },
                }

            outputs = run_role_b(
                RoleBInputs(
                    task_id="trend-anomaly-causal-inference",
                    round_index=0,
                    verifier_summary_path=str(verifier_summary),
                    session_evidence_path=str(session_evidence),
                    current_skillpack_dir=str(tmp / "current_skillpack"),
                    prior_round_summary_path=None,
                    output_dir=str(tmp / "role_b"),
                ),
                config=RoleBConfig(model_name="gpt-5.4"),
                model_runner=runner,
            )

            self.assertEqual(
                outputs.next_skillpack_manifest.skill_files,
                ["skills/analysis/SKILL.md"],
            )

    def test_role_b_normalizes_status_synonyms_from_file_outputs_and_rewrites_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verifier_summary = tmp / "verifier_summary.json"
            verifier_summary.write_text(json.dumps({"reward": 0.95}) + "\n")
            session_evidence = tmp / "session_evidence.json"
            session_evidence.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 2,
                        "role": "role_a",
                        "model_name": "claude-sonnet-4-5-20250929",
                        "source_log_paths": ["/tmp/session.log"],
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": ["/tmp/session.log:10"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            current_skillpack_dir = tmp / "current_skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# Skill\n")

            def runner(inputs, config, output_dir):
                next_skillpack_dir = output_dir / "next_skillpack" / "skills" / "analysis"
                next_skillpack_dir.mkdir(parents=True)
                skill_file = next_skillpack_dir / "SKILL.md"
                skill_file.write_text("# Refined Skill\n")

                refine_plan_json_path = output_dir / "refine_plan.json"
                refine_plan_markdown_path = output_dir / "refine_plan.md"
                next_manifest_json_path = output_dir / "next_skillpack_manifest.json"
                round_decision_json_path = output_dir / "round_decision.json"

                refine_plan_json_path.write_text(
                    json.dumps(
                        {
                            "task_id": inputs.task_id,
                            "round_index": inputs.round_index,
                            "role": config.role_name,
                            "model_name": config.model_name,
                            "summary": "normalize operation statuses",
                            "atomic_operations": [
                                {
                                    "op_id": "op-1",
                                    "action_type": "rewrite_block",
                                    "target_id": "guidance.block_2",
                                    "rationale": "accept legacy completion wording",
                                    "expected_effect": "canonical status output",
                                    "risk": "low",
                                    "status": "completed",
                                },
                                {
                                    "op_id": "op-2",
                                    "action_type": "tighten_block",
                                    "target_id": "guidance.block_3",
                                    "rationale": "accept common synonym",
                                    "expected_effect": "canonical status output",
                                    "risk": "low",
                                    "status": "done",
                                },
                                {
                                    "op_id": "op-3",
                                    "action_type": "merge_blocks",
                                    "target_id": "guidance.block_4",
                                    "rationale": "accept another common synonym",
                                    "expected_effect": "canonical status output",
                                    "risk": "low",
                                    "status": "finished",
                                },
                            ],
                        }
                    )
                    + "\n"
                )
                refine_plan_markdown_path.write_text("# Refine Plan\n")
                next_manifest_json_path.write_text(
                    json.dumps(
                        {
                            "task_id": inputs.task_id,
                            "round_index": inputs.round_index,
                            "role": config.role_name,
                            "model_name": config.model_name,
                            "skillpack_dir": str(output_dir / "next_skillpack"),
                            "skill_files": [str(skill_file)],
                            "prompt_invariant": True,
                            "derived_from_round": inputs.round_index,
                        }
                    )
                    + "\n"
                )
                round_decision_json_path.write_text(
                    json.dumps(
                        {
                            "task_id": inputs.task_id,
                            "round_index": inputs.round_index,
                            "role": config.role_name,
                            "model_name": config.model_name,
                            "decision": "continue",
                            "reason": "candidate prepared",
                            "next_round_index": inputs.round_index + 1,
                            "next_skillpack_dir": str(output_dir / "next_skillpack"),
                        }
                    )
                    + "\n"
                )
                return {
                    "refine_plan_json_path": str(refine_plan_json_path),
                    "refine_plan_markdown_path": str(refine_plan_markdown_path),
                    "next_skillpack_manifest_json_path": str(next_manifest_json_path),
                    "round_decision_json_path": str(round_decision_json_path),
                    "next_skillpack_dir": str(output_dir / "next_skillpack"),
                }

            outputs = run_role_b(
                RoleBInputs(
                    task_id="trend-anomaly-causal-inference",
                    round_index=2,
                    verifier_summary_path=str(verifier_summary),
                    session_evidence_path=str(session_evidence),
                    current_skillpack_dir=str(tmp / "current_skillpack"),
                    prior_round_summary_path=None,
                    output_dir=str(tmp / "role_b"),
                ),
                config=RoleBConfig(model_name="gpt-5.4"),
                model_runner=runner,
            )

            self.assertEqual(
                [operation["status"] for operation in outputs.refine_plan.atomic_operations],
                ["applied", "applied", "applied"],
            )
            rewritten_payload = json.loads(Path(outputs.refine_plan_json_path).read_text())
            self.assertEqual(
                [operation["status"] for operation in rewritten_payload["atomic_operations"]],
                ["applied", "applied", "applied"],
            )
            rewritten_manifest = json.loads(Path(outputs.next_skillpack_manifest_json_path).read_text())
            self.assertEqual(rewritten_manifest["skill_files"], ["skills/analysis/SKILL.md"])

    def test_role_b_rejects_unknown_status_after_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            verifier_summary = tmp / "verifier_summary.json"
            verifier_summary.write_text(json.dumps({"reward": 0.95}) + "\n")
            session_evidence = tmp / "session_evidence.json"
            session_evidence.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 2,
                        "role": "role_a",
                        "model_name": "claude-sonnet-4-5-20250929",
                        "source_log_paths": ["/tmp/session.log"],
                        "dominant_failure_pattern": "aggregation drift",
                        "wasted_loop_signals": [],
                        "tool_misuse_signals": [],
                        "critical_turns": [],
                        "skill_misguidance_signals": [],
                        "recommended_edit_targets": ["guidance.block_2"],
                        "evidence_refs": ["/tmp/session.log:10"],
                        "observed_at": "2026-03-25T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            current_skillpack_dir = tmp / "current_skillpack" / "skills" / "analysis"
            current_skillpack_dir.mkdir(parents=True)
            (current_skillpack_dir / "SKILL.md").write_text("# Skill\n")

            def runner(inputs, config, output_dir):
                next_skillpack_dir = output_dir / "next_skillpack" / "skills" / "analysis"
                next_skillpack_dir.mkdir(parents=True)
                (next_skillpack_dir / "SKILL.md").write_text("# Refined Skill\n")
                return {
                    "refine_plan": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "summary": "reject unknown status",
                        "atomic_operations": [
                            {
                                "op_id": "op-1",
                                "action_type": "rewrite_block",
                                "target_id": "guidance.block_2",
                                "rationale": "unknown status should not slip through",
                                "expected_effect": "hard failure",
                                "risk": "low",
                                "status": "half_done",
                            }
                        ],
                    },
                    "next_skillpack_manifest": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "skillpack_dir": str(output_dir / "next_skillpack"),
                        "skill_files": ["skills/analysis/SKILL.md"],
                        "prompt_invariant": True,
                        "derived_from_round": inputs.round_index,
                    },
                    "round_decision": {
                        "task_id": inputs.task_id,
                        "round_index": inputs.round_index,
                        "role": config.role_name,
                        "model_name": config.model_name,
                        "decision": "continue",
                        "reason": "candidate prepared",
                        "next_round_index": inputs.round_index + 1,
                        "next_skillpack_dir": str(output_dir / "next_skillpack"),
                    },
                }

            with self.assertRaises(ValueError):
                run_role_b(
                    RoleBInputs(
                        task_id="trend-anomaly-causal-inference",
                        round_index=2,
                        verifier_summary_path=str(verifier_summary),
                        session_evidence_path=str(session_evidence),
                        current_skillpack_dir=str(tmp / "current_skillpack"),
                        prior_round_summary_path=None,
                        output_dir=str(tmp / "role_b"),
                    ),
                    config=RoleBConfig(model_name="gpt-5.4"),
                    model_runner=runner,
                )

    def test_role_b_validator_script_runs_from_repo_root_and_rewrites_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            role_b_dir = tmp / "role_b"
            next_skillpack_dir = role_b_dir / "next_skillpack" / "skills" / "analysis"
            next_skillpack_dir.mkdir(parents=True)
            skill_file = next_skillpack_dir / "SKILL.md"
            skill_file.write_text("# Refined Skill\n")

            refine_plan_json_path = role_b_dir / "refine_plan.json"
            refine_plan_json_path.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 2,
                        "role": "role_b",
                        "model_name": "gpt-5-codex",
                        "summary": "normalize operation statuses",
                        "atomic_operations": [
                            {
                                "op_id": "op-1",
                                "action_type": "rewrite_block",
                                "target_id": "guidance.block_2",
                                "rationale": "accept legacy completion wording",
                                "expected_effect": "canonical status output",
                                "risk": "low",
                                "status": "completed",
                            }
                        ],
                    }
                )
                + "\n"
            )
            next_manifest_json_path = role_b_dir / "next_skillpack_manifest.json"
            next_manifest_json_path.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 2,
                        "role": "role_b",
                        "model_name": "gpt-5-codex",
                        "skillpack_dir": str(role_b_dir / "next_skillpack"),
                        "skill_files": [str(skill_file)],
                        "prompt_invariant": True,
                        "derived_from_round": 2,
                    }
                )
                + "\n"
            )
            round_decision_json_path = role_b_dir / "round_decision.json"
            round_decision_json_path.write_text(
                json.dumps(
                    {
                        "task_id": "trend-anomaly-causal-inference",
                        "round_index": 2,
                        "role": "role_b",
                        "model_name": "gpt-5-codex",
                        "decision": "continue",
                        "reason": "candidate prepared",
                        "next_round_index": 3,
                        "next_skillpack_dir": str(role_b_dir / "next_skillpack"),
                    }
                )
                + "\n"
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_c4ar_role_b_outputs.py",
                    "--refine-plan",
                    str(refine_plan_json_path),
                    "--next-skillpack-manifest",
                    str(next_manifest_json_path),
                    "--round-decision",
                    str(round_decision_json_path),
                    "--task-id",
                    "trend-anomaly-causal-inference",
                    "--round-index",
                    "2",
                    "--role-name",
                    "role_b",
                    "--rewrite",
                ],
                cwd=Path.cwd(),
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])
            rewritten_refine_plan = json.loads(refine_plan_json_path.read_text())
            self.assertEqual(rewritten_refine_plan["atomic_operations"][0]["status"], "applied")
            rewritten_manifest = json.loads(next_manifest_json_path.read_text())
            self.assertEqual(rewritten_manifest["skill_files"], ["skills/analysis/SKILL.md"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

import path_setup
from skillx.c4ar.contracts import (
    NextSkillpackManifest,
    OrchestratorEvent,
    RefinePlanArtifact,
    RoundDecisionArtifact,
    SessionEvidenceArtifact,
    ensure_valid_next_skillpack_manifest,
    ensure_valid_orchestrator_event,
    ensure_valid_refine_plan_artifact,
    ensure_valid_round_decision_artifact,
    ensure_valid_session_evidence_artifact,
    validate_next_skillpack_manifest,
    validate_orchestrator_event,
    validate_refine_plan_artifact,
    validate_round_decision_artifact,
    validate_session_evidence_artifact,
)


class C4arContractTests(unittest.TestCase):
    def test_valid_session_evidence_artifact_passes_validation(self) -> None:
        artifact = SessionEvidenceArtifact(
            task_id="trend-anomaly-causal-inference",
            round_index=0,
            role="role_a",
            model_name="codex-5.3",
            source_log_paths=["/tmp/round-0/session.jsonl"],
            dominant_failure_pattern="over-aggregation and verifier-adjacent drift",
            wasted_loop_signals=["repeated file rereads without narrowing the scope"],
            tool_misuse_signals=["looked for non-existent deferred tools before reading the skillpack"],
            critical_turns=["shifted from stage workflow to one-shot script synthesis"],
            skill_misguidance_signals=["aggregation contract remained too implicit"],
            recommended_edit_targets=["aggregation guidance", "derived execution layer"],
            evidence_refs=["/tmp/round-0/session.jsonl:42"],
            observed_at="2026-03-25T00:00:00+00:00",
        )

        result = validate_session_evidence_artifact(artifact)

        self.assertTrue(result.ok)
        self.assertEqual(result.errors, ())
        self.assertEqual(ensure_valid_session_evidence_artifact(artifact), artifact)

    def test_invalid_session_evidence_artifact_is_rejected(self) -> None:
        payload = {
            "task_id": "",
            "round_index": -1,
            "role": "role_a",
            "model_name": "",
            "source_log_paths": [],
            "dominant_failure_pattern": "",
            "evidence_refs": [],
            "observed_at": "",
        }

        result = validate_session_evidence_artifact(payload)

        self.assertFalse(result.ok)
        self.assertIn("task_id must be a non-empty string", result.errors)
        self.assertIn("round_index must be a non-negative integer", result.errors)
        self.assertIn("source_log_paths must be a non-empty sequence", result.errors)
        with self.assertRaises(ValueError):
            ensure_valid_session_evidence_artifact(payload)

    def test_valid_next_skillpack_manifest_passes_validation(self) -> None:
        manifest = NextSkillpackManifest(
            task_id="trend-anomaly-causal-inference",
            round_index=1,
            role="role_b",
            model_name="GPT-5.4",
            skillpack_dir="/tmp/round-1/skillpack",
            skill_files=[
                "skills/data_cleaning/SKILL.md",
                "skills/did_causal_analysis/SKILL.md",
            ],
            bundle_path="/tmp/round-1/skillpack/skillpack_bundle.yaml",
            prompt_invariant=True,
            derived_from_round=0,
        )

        result = validate_next_skillpack_manifest(manifest)

        self.assertTrue(result.ok)
        self.assertEqual(result.errors, ())
        self.assertEqual(ensure_valid_next_skillpack_manifest(manifest), manifest)

    def test_invalid_next_skillpack_manifest_is_rejected(self) -> None:
        payload = {
            "task_id": "trend-anomaly-causal-inference",
            "round_index": 1,
            "role": "role_b",
            "model_name": "GPT-5.4",
            "skillpack_dir": "",
            "skill_files": ["/tmp/outside/SKILL.md"],
            "prompt_invariant": "yes",
            "derived_from_round": -1,
        }

        result = validate_next_skillpack_manifest(payload)

        self.assertFalse(result.ok)
        self.assertIn("skillpack_dir must be a non-empty string", result.errors)
        self.assertIn("skill_files must contain only relative paths", result.errors)
        self.assertIn("prompt_invariant must be a boolean", result.errors)
        self.assertIn("derived_from_round must be a non-negative integer", result.errors)
        with self.assertRaises(ValueError):
            ensure_valid_next_skillpack_manifest(payload)

    def test_valid_refine_plan_artifact_passes_validation(self) -> None:
        artifact = RefinePlanArtifact(
            task_id="trend-anomaly-causal-inference",
            round_index=1,
            role="role_b",
            model_name="gpt-5.4",
            summary="tighten aggregation guidance and remove low-signal redundancy",
            atomic_operations=[
                {
                    "op_id": "op-1",
                    "action_type": "rewrite_block",
                    "target_id": "guidance.block_2",
                    "rationale": "current aggregation guidance is too broad",
                    "expected_effect": "reduce zero-spend leakage",
                    "risk": "may over-tighten",
                    "status": "planned",
                }
            ],
        )

        result = validate_refine_plan_artifact(artifact)

        self.assertTrue(result.ok)
        self.assertEqual(result.errors, ())
        self.assertEqual(ensure_valid_refine_plan_artifact(artifact), artifact)

    def test_refine_plan_artifact_accepts_applied_status(self) -> None:
        artifact = RefinePlanArtifact(
            task_id="trend-anomaly-causal-inference",
            round_index=1,
            role="role_b",
            model_name="gpt-5.4",
            summary="apply the bounded rewrite",
            atomic_operations=[
                {
                    "op_id": "op-1",
                    "action_type": "rewrite_block",
                    "target_id": "guidance.block_2",
                    "rationale": "the rewrite already landed in the staged skillpack",
                    "expected_effect": "reduce zero-spend leakage",
                    "risk": "may over-tighten",
                    "status": "applied",
                }
            ],
        )

        result = validate_refine_plan_artifact(artifact)

        self.assertTrue(result.ok)
        self.assertEqual(result.errors, ())
        self.assertEqual(ensure_valid_refine_plan_artifact(artifact), artifact)

    def test_invalid_refine_plan_artifact_is_rejected(self) -> None:
        payload = {
            "task_id": "",
            "round_index": -1,
            "role": "role_b",
            "model_name": "gpt-5.4",
            "summary": "",
            "atomic_operations": [
                {
                    "op_id": "",
                    "action_type": "rewrite_block",
                    "target_id": "",
                    "rationale": "",
                    "expected_effect": "",
                    "risk": "",
                    "status": "maybe",
                }
            ],
        }

        result = validate_refine_plan_artifact(payload)

        self.assertFalse(result.ok)
        self.assertIn("task_id must be a non-empty string", result.errors)
        self.assertIn("round_index must be a non-negative integer", result.errors)
        self.assertIn("summary must be a non-empty string", result.errors)
        self.assertIn("atomic_operations.op_id must be a non-empty string", result.errors)
        self.assertIn("atomic_operations.status must be one of", result.errors[-1])
        with self.assertRaises(ValueError):
            ensure_valid_refine_plan_artifact(payload)

    def test_valid_round_decision_artifact_passes_validation(self) -> None:
        decision = RoundDecisionArtifact(
            task_id="trend-anomaly-causal-inference",
            round_index=1,
            role="role_b",
            model_name="GPT-5.4",
            decision="continue",
            reason="R0 was runtime-valid and the next skillpack passes contract validation.",
            next_round_index=2,
            next_skillpack_dir="/tmp/round-1/skillpack",
            selected_candidate_label=None,
        )

        result = validate_round_decision_artifact(decision)

        self.assertTrue(result.ok)
        self.assertEqual(result.errors, ())
        self.assertEqual(ensure_valid_round_decision_artifact(decision), decision)

    def test_invalid_round_decision_artifact_is_rejected(self) -> None:
        payload = {
            "task_id": "trend-anomaly-causal-inference",
            "round_index": 1,
            "role": "role_b",
            "model_name": "GPT-5.4",
            "decision": "continue",
            "reason": "",
        }

        result = validate_round_decision_artifact(payload)

        self.assertFalse(result.ok)
        self.assertIn("reason must be a non-empty string", result.errors)
        self.assertIn("continue decision requires next_round_index", result.errors)
        self.assertIn("continue decision requires next_skillpack_dir", result.errors)
        with self.assertRaises(ValueError):
            ensure_valid_round_decision_artifact(payload)

    def test_select_final_decision_requires_candidate_label(self) -> None:
        payload = {
            "task_id": "trend-anomaly-causal-inference",
            "round_index": 1,
            "role": "role_b",
            "model_name": "GPT-5.4",
            "decision": "select_final",
            "reason": "best candidate already chosen",
        }

        result = validate_round_decision_artifact(payload)

        self.assertFalse(result.ok)
        self.assertIn("select_final decision requires selected_candidate_label", result.errors)

    def test_valid_orchestrator_event_passes_validation(self) -> None:
        event = OrchestratorEvent(
            task_id="trend-anomaly-causal-inference",
            round_index=1,
            role="orchestrator",
            event_type="handoff_validated",
            status="ok",
            timestamp="2026-03-25T00:00:00+00:00",
            artifact_ref="/tmp/round-1/role-b/round_decision.json",
            note="Role B handoff accepted.",
        )

        result = validate_orchestrator_event(event)

        self.assertTrue(result.ok)
        self.assertEqual(result.errors, ())
        self.assertEqual(ensure_valid_orchestrator_event(event), event)

    def test_invalid_orchestrator_event_is_rejected(self) -> None:
        payload = {
            "task_id": "trend-anomaly-causal-inference",
            "round_index": -3,
            "role": "",
            "event_type": "",
            "status": "",
            "timestamp": "",
        }

        result = validate_orchestrator_event(payload)

        self.assertFalse(result.ok)
        self.assertIn("round_index must be a non-negative integer", result.errors)
        self.assertIn("role must be a non-empty string", result.errors)
        self.assertIn("event_type must be a non-empty string", result.errors)
        self.assertIn("status must be a non-empty string", result.errors)
        self.assertIn("timestamp must be a non-empty string", result.errors)
        with self.assertRaises(ValueError):
            ensure_valid_orchestrator_event(payload)


if __name__ == "__main__":
    unittest.main()

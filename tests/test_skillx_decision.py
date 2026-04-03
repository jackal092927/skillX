from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import path_setup
from skillx.decision import (
    build_skillx_decision_bundle,
    decide_refine_intent,
    decide_round_disposition,
)
from skillx.evidence import load_skillx_c3_result, load_skillx_c4_summary
from skillx.session_evidence import distill_session_logs


ROOT = Path(__file__).resolve().parents[1]
TREND_SESSION_LOG = (
    ROOT
    / "experiments"
    / "skillx-skillsbench-001"
    / "runs"
    / "c4-trend-001-v0-1"
    / "refine"
    / "trend-anomaly-causal-inference"
    / "rounds"
    / "round-1"
    / "tune_check"
    / "trend-anomaly-causal-inference-round-1-c4-tune"
    / "c4-trend-anomaly-causal-inferenc__S4GAvjk"
    / "agent"
    / "sessions"
    / "projects"
    / "-app"
    / "0fd0c72b-5c9a-4358-a839-3a253769a001.jsonl"
)


class SkillxDecisionTests(unittest.TestCase):
    def test_contract_failure_is_retryable_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result_dir = Path(tmpdir)
            (result_dir / "result.json").write_text(
                "{\"stats\": {\"n_trials\": 1, \"n_errors\": 0, \"evals\": {\"demo\": {\"exception_stats\": {}}}}}"
            )
            c3_result = load_skillx_c3_result(result_dir)
            bundle = build_skillx_decision_bundle(c3_result=c3_result)

            disposition = decide_round_disposition(bundle)
            intent = decide_refine_intent(bundle)

            self.assertTrue(disposition.retry_allowed)
            self.assertFalse(disposition.keep_candidate)
            self.assertEqual(disposition.classification_kind, "contract_failure")
            self.assertEqual(intent.primary_action, "repair_contract")
            self.assertIn("repair", intent.rationale.lower())
            self.assertIn("restore_missing_output", intent.edit_targets)

    def test_scientific_failure_does_not_retry_but_tightens_scope(self) -> None:
        c3_result = load_skillx_c3_result(
            ROOT
            / "experiments"
            / "skillx-skillsbench-001"
            / "runs"
            / "rewrite-benchmark-004-exoplanet"
            / "benchmark_jobs"
            / "exoplanet-detection-period-c3"
        )
        bundle = build_skillx_decision_bundle(c3_result=c3_result)

        disposition = decide_round_disposition(bundle)
        intent = decide_refine_intent(bundle)

        self.assertFalse(disposition.retry_allowed)
        self.assertFalse(disposition.keep_candidate)
        self.assertEqual(disposition.classification_kind, "scientific_failure")
        self.assertEqual(intent.primary_action, "tighten_scope_boundary")
        self.assertIn("scope", intent.rationale.lower())
        self.assertIn("tighten_scope_boundary", intent.edit_targets)

    def test_trend_like_bundle_recommends_compression_and_anti_speculation(self) -> None:
        c3_result = load_skillx_c3_result(
            ROOT
            / "experiments"
            / "skillx-skillsbench-001"
            / "runs"
            / "rewrite-benchmark-003-harbor-rewrite"
            / "benchmark_jobs"
            / "trend-anomaly-causal-inference-c3"
        )
        c4_summary = load_skillx_c4_summary(
            ROOT / "experiments" / "skillx-skillsbench-001" / "runs" / "c4-trend-001-v0-1"
        )
        session_evidence = distill_session_logs([TREND_SESSION_LOG])
        bundle = build_skillx_decision_bundle(
            c3_result=c3_result,
            c4_summary=c4_summary,
            session_evidence=session_evidence,
        )

        disposition = decide_round_disposition(bundle)
        intent = decide_refine_intent(bundle)

        self.assertFalse(disposition.retry_allowed)
        self.assertTrue(disposition.keep_candidate)
        self.assertEqual(intent.primary_action, "compress_derived_layer")
        self.assertTrue(intent.compress_derived_layer)
        self.assertTrue(intent.de_bloat_derived_layer)
        self.assertTrue(intent.anti_speculation)
        self.assertIn("compress_derived_layer", intent.edit_targets)
        self.assertIn("de_bloat_derived_layer", intent.edit_targets)
        self.assertIn("remove_speculative_evaluator_content", intent.edit_targets)
        self.assertIn("tighten_scope_boundary", intent.edit_targets)
        self.assertIn("compression", intent.rationale.lower())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import path_setup
from skillx import classify_skillx_outcome, load_skillx_c3_result, load_skillx_c4_summary


ROOT = Path(__file__).resolve().parents[1]


class SkillxEvidenceTests(unittest.TestCase):
    def test_load_skillx_c3_result_reads_actual_reward_and_classification(self) -> None:
        result = load_skillx_c3_result(
            ROOT
            / "experiments"
            / "skillx-skillsbench-001"
            / "runs"
            / "rewrite-benchmark-003-harbor-rewrite"
            / "benchmark_jobs"
            / "trend-anomaly-causal-inference-c3"
        )
        self.assertEqual(result.task_id, "trend-anomaly-causal-inference")
        self.assertEqual(result.condition, "c3")
        self.assertAlmostEqual(result.reward or 0.0, 0.7944)
        self.assertEqual(result.classification.kind, "clean_success")
        self.assertEqual(result.exception_stats, {})

    def test_load_skillx_c3_result_marks_clean_zero_as_scientific_failure(self) -> None:
        result = load_skillx_c3_result(
            ROOT
            / "experiments"
            / "skillx-skillsbench-001"
            / "runs"
            / "rewrite-benchmark-004-exoplanet"
            / "benchmark_jobs"
            / "exoplanet-detection-period-c3"
        )
        self.assertEqual(result.task_id, "exoplanet-detection-period")
        self.assertEqual(result.reward, 0.0)
        self.assertEqual(result.classification.kind, "scientific_failure")

    def test_load_skillx_c3_result_marks_missing_metrics_as_contract_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result_dir = Path(tmpdir)
            (result_dir / "result.json").write_text(
                "{\"stats\": {\"n_trials\": 1, \"n_errors\": 0, \"evals\": {\"demo\": {\"exception_stats\": {}}}}}"
            )
            result = load_skillx_c3_result(result_dir)
            self.assertIsNone(result.reward)
            self.assertEqual(result.classification.kind, "contract_failure")
            self.assertTrue(result.classification.reward_is_missing)

    def test_load_skillx_c3_result_marks_exception_stats_as_runtime_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result_dir = Path(tmpdir)
            (result_dir / "result.json").write_text(
                "{\"stats\": {\"n_trials\": 1, \"n_errors\": 1, \"evals\": {\"demo\": {\"metrics\": [{\"mean\": 0.0}], \"exception_stats\": {\"TimeoutError\": {\"n_trials\": 1}}}}}}"
            )
            result = load_skillx_c3_result(result_dir)
            self.assertEqual(result.reward, 0.0)
            self.assertEqual(result.classification.kind, "runtime_failure")
            self.assertTrue(result.classification.has_exception_stats)

    def test_load_skillx_c4_summary_reads_selected_round_and_round_rows(self) -> None:
        summary = load_skillx_c4_summary(
            ROOT / "experiments" / "skillx-skillsbench-001" / "runs" / "c4-trend-001-v0-1"
        )
        self.assertEqual(summary.task_id, "trend-anomaly-causal-inference")
        self.assertEqual(summary.selected_round_index, 2)
        self.assertAlmostEqual(summary.selected_reward or 0.0, 1.0)
        self.assertEqual(len(summary.rounds), 4)
        self.assertEqual(summary.rounds[0].classification.kind, "clean_success")
        self.assertAlmostEqual(summary.rounds[3].reward or 0.0, 0.95)

    def test_classify_skillx_outcome_handles_positive_and_zero_rewards(self) -> None:
        success = classify_skillx_outcome(reward=1.0, exception_stats={})
        failure = classify_skillx_outcome(reward=0.0, exception_stats={})
        self.assertEqual(success.kind, "clean_success")
        self.assertEqual(failure.kind, "scientific_failure")


if __name__ == "__main__":
    unittest.main()

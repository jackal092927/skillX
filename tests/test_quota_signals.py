from __future__ import annotations

import tempfile
from pathlib import Path

from tests.path_setup import SRC  # noqa: F401

from skillx.quota_signals import scan_payload, summarize_run_dir


def test_allowed_rate_limit_event_is_not_hard_signal() -> None:
    scan = scan_payload(
        {
            "path": "/tmp/rate-limit-rerun/run/RUN_STATUS.md",
            "text": (
                '{"type":"rate_limit_event","rate_limit_info":{"status":"allowed",'
                '"resetsAt":1777255200,"rateLimitType":"five_hour",'
                '"overageStatus":"rejected","overageDisabledReason":"org_level_disabled"}}'
            ),
        }
    )

    assert scan["signal_level"] == "none"
    assert scan["hard_terms"] == []


def test_rejected_rate_limit_event_is_hard_signal() -> None:
    scan = scan_payload(
        {
            "text": (
                '{"type":"rate_limit_event","rate_limit_info":{"status":"rejected",'
                '"resetsAt":1777251600,"rateLimitType":"five_hour"}}'
            ),
        }
    )

    assert scan["signal_level"] == "hard"
    assert "rate_limit_rejected_event" in scan["hard_terms"]


def test_api_429_result_remains_hard_signal() -> None:
    scan = scan_payload(
        {
            "text": (
                '{"type":"result","is_error":true,"api_error_status":429,'
                '"result":"You have hit your limit; resets later"}'
            ),
        }
    )

    assert scan["signal_level"] == "hard"
    assert "api_error_status_429" in scan["hard_terms"]
    assert "hit_your_limit" in scan["hard_terms"]


def test_rate_limit_rerun_paths_do_not_create_hard_signal() -> None:
    scan = scan_payload(
        {
            "failure_message": (
                "role_a agent failed; see "
                "/Users/example/rate-limit-rerun/run/role_a/agent_run/stderr.txt"
            ),
            "trial_result_path": "/Users/example/rate-limit-rerun/run/tune_check/result.json",
        }
    )

    assert scan["signal_level"] == "none"
    assert scan["hard_terms"] == []


def test_derived_quota_signal_fields_do_not_create_hard_signal() -> None:
    scan = scan_payload(
        {
            "attempts": [
                {
                    "quota_signal_level": "hard",
                    "quota_hard_terms": ["api_error_status_429", "rate_limit_reached"],
                }
            ],
            "quota_signal": {
                "signal_level": "hard",
                "hard_terms": ["status_429"],
                "matches": [{"excerpt": "api_error_status=429"}],
            },
        }
    )

    assert scan["signal_level"] == "none"
    assert scan["hard_terms"] == []


def test_run_status_is_not_used_as_quota_evidence() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir)
        (run_dir / "RUN_STATUS.md").write_text(
            "- status: `completed_with_quota_issues`\n"
            "- quota_hard_terms: `api_error_status_429, rate_limit_reached`\n"
        )

        scan = summarize_run_dir(run_dir)

    assert scan["signal_level"] == "none"
    assert scan["hard_terms"] == []

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "build_round0_checkpoint_report.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("build_round0_checkpoint_report", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _pair(pair_id: str, status: str, score_pct: float | None = None) -> dict:
    task_name, schema_id = pair_id.split("__", 1)
    return {
        "pair_id": pair_id,
        "task_name": task_name,
        "schema_id": schema_id,
        "launcher": {"status": status},
        "run": {"status": "completed" if status == "succeeded" else "failed"},
        "official_scores": {"c0_pct": 0.0, "c1_pct": 0.0},
        "reported_score": {"round_index": 1, "score_pct": score_pct},
        "selected": {
            "round_index": 1,
            "score_pct": score_pct,
            "classification": {
                "kind": "clean_success" if score_pct and score_pct > 0 else "scientific_failure"
            },
        },
        "delta_vs_c0_pp": score_pct,
        "delta_vs_c1_pp": score_pct,
    }


def test_merge_pair_reports_replaces_failed_base_pair_with_successful_rerun() -> None:
    module = _load_module()
    base = {
        "run_label": "base-run",
        "pair_results": [
            _pair("task-a__schema-a", "succeeded", 100.0),
            _pair("task-b__schema-b", "failed", None),
        ],
    }
    rerun = {
        "run_label": "rerun-v2",
        "pair_results": [
            _pair("task-b__schema-b", "succeeded", 50.0),
        ],
    }

    merged, replacements = module.merge_pair_reports(base, [rerun])

    merged_by_pair = {pair["pair_id"]: pair for pair in merged}
    assert merged_by_pair["task-a__schema-a"]["source_run_label"] == "base-run"
    assert merged_by_pair["task-b__schema-b"]["source_run_label"] == "rerun-v2"
    assert merged_by_pair["task-b__schema-b"]["launcher"]["status"] == "succeeded"
    assert replacements == [
        {
            "pair_id": "task-b__schema-b",
            "base_status": "failed",
            "rerun_status": "succeeded",
            "rerun_label": "rerun-v2",
        }
    ]

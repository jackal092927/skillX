#!/usr/bin/env python3
"""Build round-0 score-matrix, assignment, and diagnostics artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROUND0_ROOT = (
    ROOT
    / "experiments"
    / "skillx-skillsbench-001"
    / "results"
    / "outer-loop-round0"
)
DEFAULT_GLOBAL_PAIR_STATUS_PATH = (
    DEFAULT_ROUND0_ROOT / "reports" / "global-round0-status" / "global_pair_status.json"
)
DEFAULT_PROMPT_BANK_PATH = ROOT / "docs" / "plans" / "skillx" / "skillx-prompt-bank-v0.1.json"
DEFAULT_TASK_CLUSTER_INPUTS_PATH = (
    ROOT / "docs" / "plans" / "skillx" / "skillsbench-task-cluster-inputs-v0.1.jsonl"
)
DEFAULT_OUTPUT_DIR = DEFAULT_ROUND0_ROOT / "reports" / "outer-loop-control-plane"
DEFAULT_SCHEMA_IDS = [
    "artifact-generation",
    "analytic-pipeline",
    "engineering-composition",
    "retrieval-heavy-synthesis",
    "environment-control",
    "methodology-guardrail",
    "orchestration-delegation",
]
DEFAULT_HIGH_CONFIDENCE_MARGIN_PP = 10.0
DEFAULT_MEDIUM_CONFIDENCE_MARGIN_PP = 5.0
DEFAULT_DOMINANT_SHARE_THRESHOLD = 0.60
DEFAULT_TOP3_TIE_THRESHOLD_PP = 10.0
DEFAULT_NEAR_EMPTY_THRESHOLD = 3
DEFAULT_UPDATE_FLOOR_FRACTION = 0.10
DEFAULT_FLAT_COLUMN_RANGE_PP = 10.0
DEFAULT_ASSIGNMENT_SCORE_MODE = "trajectory"
DEFAULT_POST_R0_IMPROVEMENT_AREA_WEIGHT = 0.40
DEFAULT_POST_R0_MONOTONICITY_WEIGHT = 0.25
DEFAULT_POST_R0_IMPROVED_ROUND_COUNT_WEIGHT = 0.20
DEFAULT_POST_R0_TERMINAL_IMPROVEMENT_WEIGHT = 0.15
DEFAULT_MIN_ASSIGNMENT_SCORE_PCT = 0.0
DEFAULT_BALANCE_TIE_MAX_LOSS_PP = 1.0
DEFAULT_ASSIGNMENT_RANDOM_SEED = "skillx-round0-assignment-v1"
DEFAULT_MULTI_ASSIGNMENT_MIN_SCORE_PCT = 80.0
DEFAULT_MULTI_ASSIGNMENT_NEAR_BEST_MARGIN_PP = 10.0
DEFAULT_MULTI_ASSIGNMENT_MIN_DELTA_VS_R0_PP = 10.0
DEFAULT_ROUND_SCORE_WEIGHTS = {
    0: 0.15,
    1: 0.20,
    2: 0.30,
    3: 0.35,
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def discover_run_report_paths(round0_root: Path) -> list[Path]:
    return sorted(round0_root.glob("**/reports/*/run_report.json"))


def load_schema_bank(prompt_bank_path: Path) -> list[dict[str, Any]]:
    payload = read_json(prompt_bank_path)
    categories = payload.get("categories")
    if not isinstance(categories, list):
        raise ValueError(f"prompt bank missing categories list: {prompt_bank_path}")
    rows: list[dict[str, Any]] = []
    for item in categories:
        if not isinstance(item, dict):
            continue
        category_id = item.get("category_id")
        if not isinstance(category_id, str):
            continue
        rows.append(item)
    return rows


def load_schema_ids(prompt_bank_path: Path) -> list[str]:
    schema_bank = load_schema_bank(prompt_bank_path)
    schema_ids = [str(item["category_id"]) for item in schema_bank]
    if schema_ids:
        return schema_ids
    return list(DEFAULT_SCHEMA_IDS)


def load_task_profile_index(task_cluster_inputs_path: Path | None) -> dict[str, dict[str, Any]]:
    if task_cluster_inputs_path is None or not task_cluster_inputs_path.exists():
        return {}

    profiles: dict[str, dict[str, Any]] = {}
    for line in task_cluster_inputs_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        payload = json.loads(stripped)
        task_name = payload.get("task_name")
        if not isinstance(task_name, str) or not task_name:
            continue
        cluster_inputs = payload.get("cluster_inputs") or {}
        semantic_contract = cluster_inputs.get("semantic_contract") or {}
        tool_topology = cluster_inputs.get("tool_topology") or {}
        tags = payload.get("tags") or {}
        profiles[task_name] = {
            "task_object_seed": semantic_contract.get("task_object_seed"),
            "verifier_mode": semantic_contract.get("verifier_mode"),
            "workflow_topology": tool_topology.get("workflow_topology"),
            "tool_surface_regime": tool_topology.get("tool_surface_regime"),
            "primary_pattern": tags.get("primary_pattern"),
            "secondary_patterns": tags.get("secondary_patterns") or [],
            "confidence": tags.get("confidence"),
            "evidence_note": tags.get("evidence_note"),
        }
    return profiles


def load_run_report_index(round0_root: Path) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for report_path in discover_run_report_paths(round0_root):
        payload = read_json(report_path)
        run_label = payload.get("run_label")
        if not isinstance(run_label, str):
            continue
        for pair_result in payload.get("pair_results", []):
            if not isinstance(pair_result, dict):
                continue
            pair_id = pair_result.get("pair_id")
            if not isinstance(pair_id, str):
                continue
            row = dict(pair_result)
            row["run_label"] = run_label
            row["report_path"] = display_path(report_path)
            index[(run_label, pair_id)] = row
    return index


def coerce_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return float(stripped)
        except ValueError:
            return None
    return None


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes"}:
            return True
        if lowered in {"0", "false", "no", ""}:
            return False
    return bool(value)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def round_score_key(round_index: int) -> str:
    return f"round_r{round_index}_score_pct"


def extract_round_score_map(pair_report: dict[str, Any] | None) -> dict[int, float]:
    if not isinstance(pair_report, dict):
        return {}
    round_scores: dict[int, float] = {}
    rounds = pair_report.get("rounds")
    if not isinstance(rounds, list):
        return round_scores
    for round_info in rounds:
        if not isinstance(round_info, dict):
            continue
        round_index = round_info.get("round_index")
        score_pct = coerce_float(round_info.get("score_pct"))
        if isinstance(round_index, int) and score_pct is not None:
            round_scores[round_index] = score_pct
    return round_scores


def weighted_round_mean_score(round_scores: dict[int, float]) -> float | None:
    weighted_sum = 0.0
    total_weight = 0.0
    for round_index, weight in DEFAULT_ROUND_SCORE_WEIGHTS.items():
        score = round_scores.get(round_index)
        if score is None:
            continue
        weighted_sum += score * weight
        total_weight += weight
    if total_weight <= 0:
        return None
    return weighted_sum / total_weight


def arithmetic_round_mean_score(round_scores: dict[int, float]) -> float | None:
    if not round_scores:
        return None
    return mean(float(value) for value in round_scores.values())


def _round_values(round_scores: dict[int, float], indexes: list[int]) -> list[float]:
    return [float(round_scores[index]) for index in indexes if index in round_scores]


def _is_non_decreasing(values: list[float]) -> bool | None:
    if len(values) < 2:
        return None
    return all(right >= left for left, right in zip(values, values[1:]))


def build_trajectory_features(round_scores: dict[int, float]) -> dict[str, Any]:
    r0_score = round_scores.get(0)
    ordered_scores = _round_values(round_scores, [0, 1, 2, 3])
    post_scores = _round_values(round_scores, [1, 2, 3])
    post_score_non_decreasing = _is_non_decreasing(post_scores)
    post_round_scores = {
        round_index: float(round_scores[round_index])
        for round_index in (1, 2, 3)
        if round_index in round_scores
    }
    best_round_score = max(ordered_scores, default=None)
    final_round_index = max(round_scores, default=None)
    final_round_score = (
        float(round_scores[final_round_index]) if final_round_index is not None else None
    )
    post_r0_best_score = max(post_scores, default=None)
    deltas_vs_r0 = {
        round_index: (
            round(float(score) - float(r0_score), 4) if r0_score is not None else None
        )
        for round_index, score in post_round_scores.items()
    }
    post_delta_values = [
        float(deltas_vs_r0[round_index])
        for round_index in (1, 2, 3)
        if deltas_vs_r0.get(round_index) is not None
    ]
    positive_post_deltas = [max(delta, 0.0) for delta in post_delta_values]
    post_r0_improved_round_count = sum(1 for delta in post_delta_values if delta > 0.0)
    post_r0_improvement_area_score = (
        round(mean(positive_post_deltas), 4)
        if positive_post_deltas
        else (0.0 if r0_score is not None else None)
    )
    post_r0_improved_round_fraction_score = (
        round(100.0 * post_r0_improved_round_count / len(post_delta_values), 4)
        if post_delta_values
        else (0.0 if r0_score is not None else None)
    )
    last_post_score = post_scores[-1] if post_scores else None
    post_r0_terminal_improvement_score = (
        round(clamp(float(last_post_score) - float(r0_score), 0.0, 100.0), 4)
        if last_post_score is not None and r0_score is not None
        else (0.0 if r0_score is not None else None)
    )
    all_rounds_non_decreasing = _is_non_decreasing(ordered_scores)
    post_r0_delta_non_decreasing = _is_non_decreasing(post_delta_values)
    post_r0_all_ge_r0 = (
        all(score >= float(r0_score) for score in post_scores)
        if r0_score is not None and post_scores
        else None
    )
    post_r0_all_100 = bool(post_scores) and all(score >= 100.0 for score in post_scores)
    earliest_full_score_round = min(
        (round_index for round_index, score in round_scores.items() if float(score) >= 100.0),
        default=None,
    )
    delta_vs_r0_best = (
        round(float(best_round_score) - float(r0_score), 4)
        if best_round_score is not None and r0_score is not None
        else None
    )
    delta_vs_r0_final = (
        round(float(final_round_score) - float(r0_score), 4)
        if final_round_score is not None and r0_score is not None
        else None
    )
    delta_vs_r0_post_best = (
        round(float(post_r0_best_score) - float(r0_score), 4)
        if post_r0_best_score is not None and r0_score is not None
        else None
    )
    ideal_zero_to_full_stable = (
        r0_score is not None
        and float(r0_score) <= 0.0
        and len(post_scores) == 3
        and post_r0_all_100
    )
    full_post_r0_non_decreasing_gain = bool(
        post_scores
        and post_r0_all_ge_r0
        and post_score_non_decreasing
        and post_r0_improved_round_count > 0
    )
    terminal_gain = bool(
        post_r0_terminal_improvement_score is not None
        and post_r0_terminal_improvement_score > 0
    )

    if not post_scores:
        trajectory_quality = "baseline_only"
        trajectory_signal_score = 0.0 if r0_score is not None else None
    elif ideal_zero_to_full_stable:
        trajectory_quality = "ideal_zero_to_full_stable"
        trajectory_signal_score = 100.0
    elif post_r0_all_100 and r0_score is not None and float(r0_score) < 100.0:
        trajectory_quality = "fast_to_full_stable"
        trajectory_signal_score = 100.0
    elif full_post_r0_non_decreasing_gain:
        trajectory_quality = "stable_non_decreasing_gain"
        trajectory_signal_score = 100.0
    elif post_score_non_decreasing and terminal_gain:
        trajectory_quality = "post_r0_monotonic_gain"
        trajectory_signal_score = 80.0
    elif post_r0_all_ge_r0 and post_r0_improved_round_count > 0 and terminal_gain:
        trajectory_quality = "stable_no_loss_gain"
        trajectory_signal_score = 70.0
    elif post_r0_all_ge_r0 and post_r0_improved_round_count > 0:
        trajectory_quality = "partial_gain_then_regression"
        trajectory_signal_score = 45.0
    elif post_r0_improved_round_count >= 2:
        trajectory_quality = "non_monotonic_multi_gain"
        trajectory_signal_score = 45.0
    elif terminal_gain:
        trajectory_quality = "late_or_noisy_gain"
        trajectory_signal_score = 35.0
    elif post_r0_improved_round_count > 0:
        trajectory_quality = "transient_gain"
        trajectory_signal_score = 25.0
    elif post_r0_all_ge_r0:
        trajectory_quality = "stable_no_loss"
        trajectory_signal_score = 0.0
    else:
        trajectory_quality = "regression_or_mixed"
        trajectory_signal_score = 0.0

    return {
        "trajectory_quality": trajectory_quality,
        "trajectory_signal_score_pct": trajectory_signal_score,
        "trajectory_round_count": len(ordered_scores),
        "trajectory_post_r0_round_count": len(post_scores),
        "trajectory_non_decreasing_all_rounds": all_rounds_non_decreasing,
        "trajectory_post_r0_score_non_decreasing": post_score_non_decreasing,
        "trajectory_post_r0_delta_non_decreasing": post_r0_delta_non_decreasing,
        "trajectory_post_r0_all_ge_r0": post_r0_all_ge_r0,
        "trajectory_post_r0_all_100": post_r0_all_100,
        "trajectory_ideal_zero_to_full_stable": ideal_zero_to_full_stable,
        "post_r0_improved_round_count": post_r0_improved_round_count,
        "post_r0_improvement_area_score_pct": post_r0_improvement_area_score,
        "post_r0_improved_round_fraction_score_pct": post_r0_improved_round_fraction_score,
        "post_r0_terminal_improvement_score_pct": post_r0_terminal_improvement_score,
        "earliest_full_score_round": earliest_full_score_round,
        "rounds_at_100_count": sum(1 for score in ordered_scores if score >= 100.0),
        "post_r0_best_score_pct": post_r0_best_score,
        "delta_vs_r0_best_pp": delta_vs_r0_best,
        "delta_vs_r0_final_pp": delta_vs_r0_final,
        "delta_vs_r0_post_best_pp": delta_vs_r0_post_best,
        "delta_vs_r0_r1_pp": deltas_vs_r0.get(1),
        "delta_vs_r0_r2_pp": deltas_vs_r0.get(2),
        "delta_vs_r0_r3_pp": deltas_vs_r0.get(3),
    }


def compute_growth_component_score(round_scores: dict[int, float]) -> float | None:
    r0_score = round_scores.get(0)
    if r0_score is None:
        return None
    best_score = max(round_scores.values(), default=r0_score)
    # Center at 50 so stable runs are not treated as failures, while positive
    # R0-relative growth can still break ties between equal final scores.
    return clamp(50.0 + (best_score - r0_score), 0.0, 100.0)


def compute_assignment_score(
    *,
    reported_score_pct: float | None,
    round_scores: dict[int, float],
    trajectory_features: dict[str, Any],
    assignment_score_mode: str,
    post_r0_improvement_area_weight: float,
    post_r0_monotonicity_weight: float,
    post_r0_improved_round_count_weight: float,
    post_r0_terminal_improvement_weight: float,
) -> float | None:
    if reported_score_pct is None:
        return None
    if assignment_score_mode == "reported":
        return round(reported_score_pct, 4)
    if assignment_score_mode != "trajectory":
        raise ValueError(f"unsupported assignment score mode: {assignment_score_mode}")

    if round_scores.get(0) is None:
        return round(reported_score_pct, 4)

    components = [
        (
            coerce_float(trajectory_features.get("post_r0_improvement_area_score_pct")),
            post_r0_improvement_area_weight,
        ),
        (
            coerce_float(trajectory_features.get("trajectory_signal_score_pct")),
            post_r0_monotonicity_weight,
        ),
        (
            coerce_float(trajectory_features.get("post_r0_improved_round_fraction_score_pct")),
            post_r0_improved_round_count_weight,
        ),
        (
            coerce_float(trajectory_features.get("post_r0_terminal_improvement_score_pct")),
            post_r0_terminal_improvement_weight,
        ),
    ]
    total_weight = sum(weight for value, weight in components if value is not None and weight > 0)
    if total_weight <= 0:
        return 0.0
    score = sum(float(value) * weight for value, weight in components if value is not None and weight > 0)
    return round(score / total_weight, 4)


def semantic_prior_score(schema_id: str, task_profile: dict[str, Any] | None) -> float:
    if not task_profile:
        return 0.0

    task_object_seed = str(task_profile.get("task_object_seed") or "")
    verifier_mode = str(task_profile.get("verifier_mode") or "")
    workflow_topology = str(task_profile.get("workflow_topology") or "")
    tool_surface_regime = str(task_profile.get("tool_surface_regime") or "")
    primary_pattern = str(task_profile.get("primary_pattern") or "")
    secondary_patterns = {
        str(pattern)
        for pattern in task_profile.get("secondary_patterns", [])
        if isinstance(pattern, str)
    }

    score = 0.0
    if schema_id == task_object_seed:
        score += 4.0

    if primary_pattern == "generator" and schema_id == "artifact-generation":
        score += 2.0
    elif primary_pattern in {"reviewer", "inversion"} and schema_id == "methodology-guardrail":
        score += 2.0
    elif primary_pattern == "pipeline" and schema_id == "analytic-pipeline":
        score += 1.0

    if "generator" in secondary_patterns and schema_id == "artifact-generation":
        score += 1.0
    if "reviewer" in secondary_patterns and schema_id == "methodology-guardrail":
        score += 1.0
    if "tool-wrapper" in secondary_patterns and schema_id == "engineering-composition":
        score += 1.0

    if verifier_mode in {"deterministic-output-contract", "deterministic-artifact-plus-stage-check"}:
        if schema_id == "artifact-generation":
            score += 1.0
        if schema_id == "methodology-guardrail":
            score += 0.5
    if verifier_mode == "benchmark-threshold":
        if schema_id == "environment-control":
            score += 1.0
        if schema_id == "engineering-composition":
            score += 0.5

    if workflow_topology == "single-step-with-review":
        if schema_id == "methodology-guardrail":
            score += 1.0
        if schema_id == "artifact-generation":
            score += 0.5
    elif workflow_topology == "staged-multi-step" and schema_id == "analytic-pipeline":
        score += 0.5

    if tool_surface_regime.startswith("tool-heavy"):
        if schema_id in {"engineering-composition", "environment-control"}:
            score += 0.5
    elif tool_surface_regime == "tool-light" and schema_id == "artifact-generation":
        score += 0.5

    return score


def stable_random_sort_key(*, seed: str, task_name: str, schema_id: str) -> str:
    payload = f"{seed}\0{task_name}\0{schema_id}".encode()
    return hashlib.sha256(payload).hexdigest()


def _looks_infra_blocked(text: str) -> bool:
    lowered = text.lower()
    return any(
        needle in lowered
        for needle in (
            "docker memory too low",
            "out of memory",
            "cannot connect to the docker daemon",
            "docker api internal server error",
            "failed to pull image",
            "image not found",
            "no space left on device",
        )
    )


def classify_pair_evidence(
    *,
    latest_status: str,
    failure_summary: str,
    timeout_detected: bool,
    has_intermediate_exceptions: bool,
    reported_score_pct: float | None,
) -> str:
    if latest_status == "docker_incident" or _looks_infra_blocked(failure_summary):
        return "infra-blocked"
    if reported_score_pct is None:
        if timeout_detected or latest_status == "failed_other":
            return "runtime-blocked"
        return "missing"
    if timeout_detected or has_intermediate_exceptions or failure_summary:
        return "ambiguous"
    return "measured"


def extract_reported_score(pair_report: dict[str, Any] | None, pair_status: dict[str, Any]) -> tuple[float | None, str]:
    if pair_report is not None:
        selected_score = coerce_float((pair_report.get("selected") or {}).get("score_pct"))
        if selected_score is not None:
            return selected_score, "selected"
        best_observed_score = coerce_float((pair_report.get("best_observed") or {}).get("score_pct"))
        if best_observed_score is not None:
            return best_observed_score, "best_observed"
    selected_score = coerce_float(pair_status.get("latest_selected_score_pct"))
    if selected_score is not None:
        return selected_score, "selected"
    best_observed_score = coerce_float(pair_status.get("latest_best_observed_score_pct"))
    if best_observed_score is not None:
        return best_observed_score, "best_observed"
    return None, "missing"


def summarize_pair_row(
    *,
    pair_status: dict[str, Any],
    pair_report: dict[str, Any] | None,
    assignment_score_mode: str,
    post_r0_improvement_area_weight: float,
    post_r0_monotonicity_weight: float,
    post_r0_improved_round_count_weight: float,
    post_r0_terminal_improvement_weight: float,
) -> dict[str, Any]:
    latest_status = str(pair_status.get("latest_status") or "unrun")
    reported_score_pct, score_basis = extract_reported_score(pair_report, pair_status)
    round_scores = extract_round_score_map(pair_report)
    trajectory_features = build_trajectory_features(round_scores)
    round_mean_score_pct = arithmetic_round_mean_score(round_scores)
    round_weighted_mean_score_pct = weighted_round_mean_score(round_scores)
    growth_component_score_pct = compute_growth_component_score(round_scores)
    r0_score = round_scores.get(0)
    best_round_score = max(round_scores.values(), default=None)
    final_round_index = max(round_scores, default=None)
    final_round_score = round_scores.get(final_round_index) if final_round_index is not None else None
    assignment_score_pct = compute_assignment_score(
        reported_score_pct=reported_score_pct,
        round_scores=round_scores,
        trajectory_features=trajectory_features,
        assignment_score_mode=assignment_score_mode,
        post_r0_improvement_area_weight=post_r0_improvement_area_weight,
        post_r0_monotonicity_weight=post_r0_monotonicity_weight,
        post_r0_improved_round_count_weight=post_r0_improved_round_count_weight,
        post_r0_terminal_improvement_weight=post_r0_terminal_improvement_weight,
    )
    failure = pair_report.get("failure") if isinstance(pair_report, dict) else {}
    failure_summary = ""
    failure_type = ""
    if isinstance(failure, dict):
        failure_summary = str(failure.get("summary") or failure.get("error_message") or "")
        failure_type = str(failure.get("error_type") or "")
    if not failure_summary:
        failure_summary = str(pair_status.get("latest_failure_summary") or "")
    if not failure_type:
        failure_type = str(pair_status.get("latest_failure_type") or "")

    timeout_detected = coerce_bool(
        (pair_report or {}).get("timeout_detected", pair_status.get("latest_timeout_detected"))
    )
    has_intermediate_exceptions = coerce_bool(
        (pair_report or {}).get(
            "has_intermediate_exceptions",
            pair_status.get("latest_has_intermediate_exceptions"),
        )
    )
    official_scores = (pair_report or {}).get("official_scores") or {}
    c0_pct = coerce_float(official_scores.get("c0_pct"))
    c1_pct = coerce_float(official_scores.get("c1_pct"))

    evidence_class = classify_pair_evidence(
        latest_status=latest_status,
        failure_summary=failure_summary,
        timeout_detected=timeout_detected,
        has_intermediate_exceptions=has_intermediate_exceptions,
        reported_score_pct=reported_score_pct,
    )
    assignment_eligible = latest_status == "completed" and assignment_score_pct is not None and evidence_class != "infra-blocked"

    notes: list[str] = []
    if latest_status != "completed":
        notes.append(f"latest_status={latest_status}")
    if evidence_class == "infra-blocked":
        notes.append("infra-corrupted")
    elif evidence_class == "runtime-blocked":
        notes.append("runtime-blocked")
    elif evidence_class == "ambiguous":
        notes.append("completed-with-runtime-exceptions")
    if score_basis != "selected":
        notes.append(f"score_basis={score_basis}")
    if failure_summary and evidence_class != "infra-blocked":
        notes.append(f"failure={failure_type or failure_summary}")

    return {
        "pair_id": str(pair_status["pair_id"]),
        "task_name": str(pair_status["task_name"]),
        "schema_id": str(pair_status["schema_id"]),
        "latest_status": latest_status,
        "latest_status_code": str(pair_status.get("latest_status_code") or ""),
        "latest_run_label": str(pair_status.get("latest_run_label") or ""),
        "latest_output_dir": str(pair_status.get("latest_output_dir") or ""),
        "attempt_count": int(pair_status.get("attempt_count") or 0),
        "reported_score_pct": reported_score_pct,
        "assignment_score_pct": assignment_score_pct,
        "assignment_score_mode": assignment_score_mode,
        "round_mean_score_pct": round(round_mean_score_pct, 4) if round_mean_score_pct is not None else None,
        "round_weighted_mean_score_pct": (
            round(round_weighted_mean_score_pct, 4) if round_weighted_mean_score_pct is not None else None
        ),
        "growth_component_score_pct": (
            round(growth_component_score_pct, 4) if growth_component_score_pct is not None else None
        ),
        "trajectory_signal_score_pct": (
            round(float(trajectory_features["trajectory_signal_score_pct"]), 4)
            if trajectory_features["trajectory_signal_score_pct"] is not None
            else None
        ),
        "trajectory_quality": trajectory_features["trajectory_quality"],
        "trajectory_round_count": trajectory_features["trajectory_round_count"],
        "trajectory_post_r0_round_count": trajectory_features["trajectory_post_r0_round_count"],
        "trajectory_non_decreasing_all_rounds": trajectory_features["trajectory_non_decreasing_all_rounds"],
        "trajectory_post_r0_score_non_decreasing": trajectory_features[
            "trajectory_post_r0_score_non_decreasing"
        ],
        "trajectory_post_r0_delta_non_decreasing": trajectory_features[
            "trajectory_post_r0_delta_non_decreasing"
        ],
        "trajectory_post_r0_all_ge_r0": trajectory_features["trajectory_post_r0_all_ge_r0"],
        "trajectory_post_r0_all_100": trajectory_features["trajectory_post_r0_all_100"],
        "trajectory_ideal_zero_to_full_stable": trajectory_features[
            "trajectory_ideal_zero_to_full_stable"
        ],
        "post_r0_improved_round_count": trajectory_features["post_r0_improved_round_count"],
        "post_r0_improvement_area_score_pct": trajectory_features[
            "post_r0_improvement_area_score_pct"
        ],
        "post_r0_improved_round_fraction_score_pct": trajectory_features[
            "post_r0_improved_round_fraction_score_pct"
        ],
        "post_r0_terminal_improvement_score_pct": trajectory_features[
            "post_r0_terminal_improvement_score_pct"
        ],
        "earliest_full_score_round": trajectory_features["earliest_full_score_round"],
        "rounds_at_100_count": trajectory_features["rounds_at_100_count"],
        "post_r0_best_score_pct": trajectory_features["post_r0_best_score_pct"],
        "delta_vs_r0_best_pp": trajectory_features["delta_vs_r0_best_pp"],
        "delta_vs_r0_final_pp": trajectory_features["delta_vs_r0_final_pp"],
        "delta_vs_r0_post_best_pp": trajectory_features["delta_vs_r0_post_best_pp"],
        "delta_vs_r0_r1_pp": trajectory_features["delta_vs_r0_r1_pp"],
        "delta_vs_r0_r2_pp": trajectory_features["delta_vs_r0_r2_pp"],
        "delta_vs_r0_r3_pp": trajectory_features["delta_vs_r0_r3_pp"],
        "round_r0_to_best_delta_pp": (
            round(best_round_score - r0_score, 4)
            if best_round_score is not None and r0_score is not None
            else None
        ),
        "round_r0_to_final_delta_pp": (
            round(final_round_score - r0_score, 4)
            if final_round_score is not None and r0_score is not None
            else None
        ),
        **{
            round_score_key(round_index): (
                round(round_scores[round_index], 4) if round_index in round_scores else None
            )
            for round_index in DEFAULT_ROUND_SCORE_WEIGHTS
        },
        "score_basis": score_basis,
        "selected_score_pct": coerce_float(
            (pair_report or {}).get("selected", {}).get("score_pct")
            if isinstance(pair_report, dict)
            else pair_status.get("latest_selected_score_pct")
        ),
        "best_observed_score_pct": coerce_float(
            (pair_report or {}).get("best_observed", {}).get("score_pct")
            if isinstance(pair_report, dict)
            else pair_status.get("latest_best_observed_score_pct")
        ),
        "official_c0_pct": c0_pct,
        "official_c1_pct": c1_pct,
        "delta_vs_c0_pp": (
            round(reported_score_pct - c0_pct, 2)
            if reported_score_pct is not None and c0_pct is not None
            else None
        ),
        "delta_vs_c1_pp": (
            round(reported_score_pct - c1_pct, 2)
            if reported_score_pct is not None and c1_pct is not None
            else None
        ),
        "timeout_detected": timeout_detected,
        "has_intermediate_exceptions": has_intermediate_exceptions,
        "failure_type": failure_type,
        "failure_summary": failure_summary,
        "evidence_class": evidence_class,
        "assignment_eligible": assignment_eligible,
        "report_path": "" if pair_report is None else str(pair_report.get("report_path") or ""),
        "notes": "; ".join(notes),
    }


def build_pair_rows(
    *,
    global_pair_status_path: Path,
    round0_root: Path,
    assignment_score_mode: str,
    post_r0_improvement_area_weight: float,
    post_r0_monotonicity_weight: float,
    post_r0_improved_round_count_weight: float,
    post_r0_terminal_improvement_weight: float,
) -> tuple[list[str], list[dict[str, Any]]]:
    payload = read_json(global_pair_status_path)
    schema_ids = payload.get("schema_ids")
    if not isinstance(schema_ids, list) or not schema_ids:
        schema_ids = list(DEFAULT_SCHEMA_IDS)
    run_report_index = load_run_report_index(round0_root)

    pair_rows: list[dict[str, Any]] = []
    for pair_status in payload.get("pairs", []):
        if not isinstance(pair_status, dict):
            continue
        pair_id = pair_status.get("pair_id")
        run_label = pair_status.get("latest_run_label")
        pair_report = None
        if isinstance(pair_id, str) and isinstance(run_label, str):
            pair_report = run_report_index.get((run_label, pair_id))
        pair_rows.append(
            summarize_pair_row(
                pair_status=pair_status,
                pair_report=pair_report,
                assignment_score_mode=assignment_score_mode,
                post_r0_improvement_area_weight=post_r0_improvement_area_weight,
                post_r0_monotonicity_weight=post_r0_monotonicity_weight,
                post_r0_improved_round_count_weight=post_r0_improved_round_count_weight,
                post_r0_terminal_improvement_weight=post_r0_terminal_improvement_weight,
            )
        )
    return [str(item) for item in schema_ids], sorted(pair_rows, key=lambda row: (row["task_name"], row["schema_id"]))


def group_pair_rows_by_task(
    pair_rows: list[dict[str, Any]],
    schema_ids: list[str],
    task_profiles: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in pair_rows:
        grouped[row["task_name"]][row["schema_id"]] = row

    task_rows: list[dict[str, Any]] = []
    for task_name in sorted(grouped):
        schema_map = grouped[task_name]
        scores = {
            schema_id: (
                schema_map[schema_id]["assignment_score_pct"]
                if schema_id in schema_map and schema_map[schema_id]["assignment_eligible"]
                else None
            )
            for schema_id in schema_ids
        }
        reported_scores = {
            schema_id: (
                schema_map[schema_id]["reported_score_pct"]
                if schema_id in schema_map and schema_map[schema_id]["assignment_eligible"]
                else None
            )
            for schema_id in schema_ids
        }
        evidence_classes = {
            schema_id: (
                schema_map[schema_id]["evidence_class"]
                if schema_id in schema_map
                else "missing"
            )
            for schema_id in schema_ids
        }
        statuses = {
            schema_id: (
                schema_map[schema_id]["latest_status"]
                if schema_id in schema_map
                else "unrun"
            )
            for schema_id in schema_ids
        }
        observed_scores = [
            {"schema_id": schema_id, "score_pct": score}
            for schema_id, score in scores.items()
            if score is not None
        ]
        observed_scores.sort(key=lambda item: (-float(item["score_pct"]), str(item["schema_id"])))

        missing_schema_ids = [schema_id for schema_id, score in scores.items() if score is None]
        infra_blocked_schema_ids = [
            schema_id for schema_id, evidence in evidence_classes.items() if evidence == "infra-blocked"
        ]
        runtime_blocked_schema_ids = [
            schema_id for schema_id, evidence in evidence_classes.items() if evidence == "runtime-blocked"
        ]
        ambiguous_schema_ids = [
            schema_id for schema_id, evidence in evidence_classes.items() if evidence == "ambiguous"
        ]
        best_schema = observed_scores[0]["schema_id"] if observed_scores else None
        best_score = observed_scores[0]["score_pct"] if observed_scores else None
        second_schema = observed_scores[1]["schema_id"] if len(observed_scores) > 1 else None
        second_score = observed_scores[1]["score_pct"] if len(observed_scores) > 1 else None
        third_score = observed_scores[2]["score_pct"] if len(observed_scores) > 2 else None
        task_rows.append(
            {
                "task_name": task_name,
                "task_profile": task_profiles.get(task_name, {}),
                "scores": scores,
                "reported_scores": reported_scores,
                "evidence_classes": evidence_classes,
                "statuses": statuses,
                "observed_schema_count": len(observed_scores),
                "full_coverage": len(observed_scores) == len(schema_ids),
                "missing_schema_ids": missing_schema_ids,
                "infra_blocked_schema_ids": infra_blocked_schema_ids,
                "runtime_blocked_schema_ids": runtime_blocked_schema_ids,
                "ambiguous_schema_ids": ambiguous_schema_ids,
                "best_observed_schema": best_schema,
                "best_observed_score": best_score,
                "second_observed_schema": second_schema,
                "second_observed_score": second_score,
                "top3_spread_pp": (
                    round(float(best_score) - float(third_score), 2)
                    if best_score is not None and third_score is not None
                    else None
                ),
            }
        )
    return task_rows


def _truthy(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"1", "true", "yes"}


def build_multi_assignments(
    *,
    pair_rows: list[dict[str, Any]],
    assignments: list[dict[str, Any]],
    min_score_pct: float,
    near_best_margin_pp: float,
    min_delta_vs_r0_pp: float,
) -> list[dict[str, Any]]:
    primary_by_task = {str(row["task_name"]): row for row in assignments}
    rows_by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        if not row.get("assignment_eligible"):
            continue
        if row.get("assignment_score_pct") is None:
            continue
        rows_by_task[str(row["task_name"])].append(row)

    multi_rows: list[dict[str, Any]] = []
    for task_name, rows in sorted(rows_by_task.items()):
        best_score = max(float(row["assignment_score_pct"]) for row in rows)
        primary = primary_by_task.get(task_name, {})
        primary_schema = primary.get("assigned_category")
        for row in sorted(rows, key=lambda item: str(item["schema_id"])):
            assignment_score = float(row["assignment_score_pct"])
            reported_score = coerce_float(row.get("reported_score_pct"))
            near_best_delta = round(best_score - assignment_score, 4)
            near_best = near_best_delta <= near_best_margin_pp
            high_score = assignment_score >= min_score_pct
            delta_vs_r0 = coerce_float(row.get("delta_vs_r0_post_best_pp"))
            if delta_vs_r0 is None:
                delta_vs_r0 = coerce_float(row.get("delta_vs_r0_best_pp"))
            stable_gain = bool(
                (
                    _truthy(row.get("trajectory_ideal_zero_to_full_stable"))
                    or _truthy(row.get("trajectory_non_decreasing_all_rounds"))
                    or (
                        _truthy(row.get("trajectory_post_r0_all_ge_r0"))
                        and _truthy(row.get("trajectory_post_r0_delta_non_decreasing"))
                    )
                )
                and delta_vs_r0 is not None
                and delta_vs_r0 >= min_delta_vs_r0_pp
            )
            primary_assignment = row["schema_id"] == primary_schema
            include = primary_assignment or (near_best and high_score) or stable_gain
            if not include:
                continue

            reasons: list[str] = []
            if primary_assignment:
                reasons.append("primary")
            if near_best:
                reasons.append("near_best")
            if high_score:
                reasons.append("high_score")
            if stable_gain:
                reasons.append("stable_gain")
            if _truthy(row.get("trajectory_ideal_zero_to_full_stable")):
                reasons.append("ideal_zero_to_full")

            if primary_assignment:
                role = "primary_assignment"
            elif stable_gain:
                role = "stable_gain_support"
            elif high_score and near_best:
                role = "near_best_high_score_support"
            else:
                role = "secondary_support"

            multi_rows.append(
                {
                    "task_name": task_name,
                    "schema_id": row["schema_id"],
                    "assignment_role": role,
                    "assignment_reasons": ";".join(reasons),
                    "primary_assigned_category": primary_schema,
                    "primary_assignment": primary_assignment,
                    "assignment_score_pct": row["assignment_score_pct"],
                    "reported_score_pct": row["reported_score_pct"],
                    "best_task_assignment_score_pct": round(best_score, 4),
                    "within_best_margin_pp": near_best_delta,
                    "delta_vs_r0_post_best_pp": row.get("delta_vs_r0_post_best_pp"),
                    "delta_vs_r0_final_pp": row.get("delta_vs_r0_final_pp"),
                    "trajectory_quality": row.get("trajectory_quality"),
                    "trajectory_signal_score_pct": row.get("trajectory_signal_score_pct"),
                    "post_r0_improved_round_count": row.get("post_r0_improved_round_count"),
                    "post_r0_improvement_area_score_pct": row.get(
                        "post_r0_improvement_area_score_pct"
                    ),
                    "post_r0_improved_round_fraction_score_pct": row.get(
                        "post_r0_improved_round_fraction_score_pct"
                    ),
                    "post_r0_terminal_improvement_score_pct": row.get(
                        "post_r0_terminal_improvement_score_pct"
                    ),
                    "trajectory_non_decreasing_all_rounds": row.get(
                        "trajectory_non_decreasing_all_rounds"
                    ),
                    "trajectory_post_r0_delta_non_decreasing": row.get(
                        "trajectory_post_r0_delta_non_decreasing"
                    ),
                    "trajectory_post_r0_all_ge_r0": row.get("trajectory_post_r0_all_ge_r0"),
                    "trajectory_ideal_zero_to_full_stable": row.get(
                        "trajectory_ideal_zero_to_full_stable"
                    ),
                    "evidence_class": row.get("evidence_class"),
                    "latest_status": row.get("latest_status"),
                }
            )
    return multi_rows


def classify_margin_confidence(
    margin_pp: float | None,
    *,
    high_confidence_margin_pp: float,
    medium_confidence_margin_pp: float,
) -> str:
    if margin_pp is None:
        return "unknown"
    if margin_pp >= high_confidence_margin_pp:
        return "high"
    if margin_pp >= medium_confidence_margin_pp:
        return "medium"
    return "low"


def assign_tasks(
    *,
    task_rows: list[dict[str, Any]],
    schema_ids: list[str],
    epsilon_pp: float,
    min_assignment_score_pct: float,
    high_confidence_margin_pp: float,
    medium_confidence_margin_pp: float,
    require_full_coverage: bool,
    balance_tie_max_loss_pp: float,
    assignment_random_seed: str,
) -> list[dict[str, Any]]:
    cluster_sizes: Counter[str] = Counter()
    assignments: list[dict[str, Any]] = []

    for task_row in sorted(task_rows, key=lambda row: row["task_name"]):
        observed_scores = [
            {"schema_id": schema_id, "score_pct": score}
            for schema_id, score in task_row["scores"].items()
            if score is not None
        ]
        observed_scores.sort(key=lambda item: (-float(item["score_pct"]), str(item["schema_id"])))
        best_observed = observed_scores[0] if observed_scores else None
        second_observed = observed_scores[1] if len(observed_scores) > 1 else None
        best_score = None if best_observed is None else float(best_observed["score_pct"])
        second_score = None if second_observed is None else float(second_observed["score_pct"])
        provisional_margin = (
            round(best_score - second_score, 2)
            if best_score is not None and second_score is not None
            else None
        )

        assignment_status = "assigned"
        assigned_category = None
        tie_break_used = False
        tie_break_reason = ""
        candidate_schema_ids: list[str] = []
        candidate_semantic_scores: dict[str, float] = {}

        if not observed_scores:
            assignment_status = "unassigned_no_scores"
        elif len(observed_scores) < 2:
            assignment_status = "unassigned_insufficient_scores"
        elif require_full_coverage and not task_row["full_coverage"]:
            assignment_status = "unassigned_incomplete_row"
        elif best_score is None or best_score <= min_assignment_score_pct:
            assignment_status = "unassigned_no_positive_signal"
        else:
            top_score = float(observed_scores[0]["score_pct"])
            candidates = [
                item for item in observed_scores if top_score - float(item["score_pct"]) <= epsilon_pp
            ]
            candidate_schema_ids = [str(item["schema_id"]) for item in candidates]
            chosen = candidates[0]
            if len(candidates) > 1:
                tie_break_used = True
                candidate_score_values = [float(item["score_pct"]) for item in candidates]
                candidate_score_range = max(candidate_score_values) - min(candidate_score_values)
                candidate_semantic_scores = {
                    str(item["schema_id"]): semantic_prior_score(
                        str(item["schema_id"]),
                        task_row.get("task_profile"),
                    )
                    for item in candidates
                }
                semantic_ranked = sorted(
                    candidates,
                    key=lambda item: (
                        -candidate_semantic_scores[str(item["schema_id"])],
                        -float(item["score_pct"]),
                        stable_random_sort_key(
                            seed=assignment_random_seed,
                            task_name=str(task_row["task_name"]),
                            schema_id=str(item["schema_id"]),
                        ),
                    ),
                )
                best_semantic = candidate_semantic_scores[str(semantic_ranked[0]["schema_id"])]
                second_semantic = (
                    candidate_semantic_scores[str(semantic_ranked[1]["schema_id"])]
                    if len(semantic_ranked) > 1
                    else 0.0
                )
                if best_semantic >= 2.0 and best_semantic - second_semantic >= 1.0:
                    chosen = semantic_ranked[0]
                    tie_break_reason = "semantic_prior"
                elif candidate_score_range <= balance_tie_max_loss_pp:
                    smallest_cluster_size = min(cluster_sizes[str(item["schema_id"])] for item in candidates)
                    balance_candidates = [
                        item
                        for item in candidates
                        if cluster_sizes[str(item["schema_id"])] == smallest_cluster_size
                    ]
                    if len(balance_candidates) == 1:
                        chosen = balance_candidates[0]
                        tie_break_reason = "balance"
                    else:
                        balance_candidates.sort(
                            key=lambda item: stable_random_sort_key(
                                seed=assignment_random_seed,
                                task_name=str(task_row["task_name"]),
                                schema_id=str(item["schema_id"]),
                            )
                        )
                        chosen = balance_candidates[0]
                        tie_break_reason = "stable_random"
                else:
                    top_score_candidates = [
                        item for item in candidates if abs(top_score - float(item["score_pct"])) <= 1e-9
                    ]
                    if len(top_score_candidates) > 1:
                        top_score_candidates.sort(
                            key=lambda item: stable_random_sort_key(
                                seed=assignment_random_seed,
                                task_name=str(task_row["task_name"]),
                                schema_id=str(item["schema_id"]),
                            )
                        )
                        chosen = top_score_candidates[0]
                        tie_break_reason = "stable_random_top_score"
                    else:
                        chosen = candidates[0]
                        tie_break_reason = "score_preferred"
            assigned_category = str(chosen["schema_id"])
            cluster_sizes[assigned_category] += 1

        assigned_score = (
            task_row["scores"].get(assigned_category) if assigned_category is not None else None
        )
        assigned_reported_score = (
            task_row["reported_scores"].get(assigned_category) if assigned_category is not None else None
        )
        best_reported_score = (
            task_row["reported_scores"].get(best_observed["schema_id"]) if best_observed is not None else None
        )
        second_reported_score = (
            task_row["reported_scores"].get(second_observed["schema_id"]) if second_observed is not None else None
        )
        candidate_scores = [
            float(task_row["scores"][schema_id])
            for schema_id in candidate_schema_ids
            if task_row["scores"].get(schema_id) is not None
        ]
        assignment_row = {
            "task_name": task_row["task_name"],
            "assignment_status": assignment_status,
            "assigned_category": assigned_category,
            "best_observed_category": None if best_observed is None else best_observed["schema_id"],
            "best_score": best_score,
            "best_reported_score": best_reported_score,
            "second_best_category": None if second_observed is None else second_observed["schema_id"],
            "second_best_score": second_score,
            "second_reported_score": second_reported_score,
            "margin_pp": provisional_margin,
            "assignment_confidence": (
                classify_margin_confidence(
                    provisional_margin,
                    high_confidence_margin_pp=high_confidence_margin_pp,
                    medium_confidence_margin_pp=medium_confidence_margin_pp,
                )
                if assignment_status == "assigned"
                else "unassigned"
            ),
            "tie_break_used": tie_break_used,
            "tie_break_reason": tie_break_reason,
            "tie_candidate_schema_ids": ";".join(candidate_schema_ids),
            "tie_candidate_count": len(candidate_schema_ids),
            "tie_candidate_semantic_scores": ";".join(
                f"{schema_id}:{candidate_semantic_scores[schema_id]:.1f}"
                for schema_id in candidate_schema_ids
                if schema_id in candidate_semantic_scores
            ),
            "tie_candidate_score_range_pp": (
                round(max(candidate_scores) - min(candidate_scores), 2)
                if candidate_scores
                else None
            ),
            "observed_schema_count": task_row["observed_schema_count"],
            "full_coverage": task_row["full_coverage"],
            "missing_schema_ids": ";".join(task_row["missing_schema_ids"]),
            "infra_blocked_schema_ids": ";".join(task_row["infra_blocked_schema_ids"]),
            "runtime_blocked_schema_ids": ";".join(task_row["runtime_blocked_schema_ids"]),
            "ambiguous_schema_ids": ";".join(task_row["ambiguous_schema_ids"]),
            "top3_spread_pp": task_row["top3_spread_pp"],
            "assigned_score": assigned_score,
            "assigned_reported_score": assigned_reported_score,
        }
        assignments.append(assignment_row)
    return assignments


def pearson_correlation(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    centered_x = [value - mean_x for value in xs]
    centered_y = [value - mean_y for value in ys]
    denom_x = math.sqrt(sum(value * value for value in centered_x))
    denom_y = math.sqrt(sum(value * value for value in centered_y))
    if denom_x == 0 or denom_y == 0:
        return None
    numerator = sum(value_x * value_y for value_x, value_y in zip(centered_x, centered_y))
    return numerator / (denom_x * denom_y)


def compute_schema_pair_correlations(task_rows: list[dict[str, Any]], schema_ids: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, left_schema in enumerate(schema_ids):
        for right_schema in schema_ids[idx + 1 :]:
            xs: list[float] = []
            ys: list[float] = []
            for task_row in task_rows:
                left_score = task_row["scores"].get(left_schema)
                right_score = task_row["scores"].get(right_schema)
                if left_score is None or right_score is None:
                    continue
                xs.append(float(left_score))
                ys.append(float(right_score))
            correlation = pearson_correlation(xs, ys)
            rows.append(
                {
                    "left_schema_id": left_schema,
                    "right_schema_id": right_schema,
                    "pair_task_count": len(xs),
                    "pearson_correlation": round(correlation, 4) if correlation is not None else None,
                }
            )
    return rows


def compute_update_floor(task_rows: list[dict[str, Any]], fraction: float) -> int:
    scored_task_count = sum(1 for row in task_rows if row["observed_schema_count"] > 0)
    if scored_task_count <= 0:
        return 2
    return max(2, math.ceil(fraction * scored_task_count))


def build_diagnostics(
    *,
    task_rows: list[dict[str, Any]],
    assignments: list[dict[str, Any]],
    multi_assignments: list[dict[str, Any]],
    schema_ids: list[str],
    epsilon_pp: float,
    dominant_share_threshold: float,
    top3_tie_threshold_pp: float,
    near_empty_threshold: int,
    update_floor_fraction: float,
    flat_column_range_pp: float,
) -> dict[str, Any]:
    assigned_rows = [row for row in assignments if row["assignment_status"] == "assigned"]
    cluster_sizes = Counter(str(row["assigned_category"]) for row in assigned_rows if row["assigned_category"])
    cluster_size_map = {schema_id: int(cluster_sizes.get(schema_id, 0)) for schema_id in schema_ids}
    assigned_task_count = len(assigned_rows)
    occupied_cluster_count = sum(1 for value in cluster_size_map.values() if value > 0)
    margins = [float(row["margin_pp"]) for row in assigned_rows if row["margin_pp"] is not None]
    low_margin_tasks = [
        row
        for row in assigned_rows
        if row["margin_pp"] is not None and float(row["margin_pp"]) < epsilon_pp
    ]
    largest_cluster_size = max(cluster_size_map.values(), default=0)
    largest_cluster_share = (
        round(largest_cluster_size / assigned_task_count, 4) if assigned_task_count else 0.0
    )

    entropy = 0.0
    if assigned_task_count:
        for cluster_size in cluster_size_map.values():
            if cluster_size <= 0:
                continue
            share = cluster_size / assigned_task_count
            entropy -= share * math.log(share)

    update_floor_k = compute_update_floor(task_rows, update_floor_fraction)
    scored_task_count = sum(1 for row in task_rows if row["observed_schema_count"] > 0)
    top3_tied_tasks = [
        {
            "task_name": row["task_name"],
            "best_observed_schema": row["best_observed_schema"],
            "best_observed_score": row["best_observed_score"],
            "second_observed_schema": row["second_observed_schema"],
            "second_observed_score": row["second_observed_score"],
            "top3_spread_pp": row["top3_spread_pp"],
        }
        for row in task_rows
        if row["top3_spread_pp"] is not None and float(row["top3_spread_pp"]) < top3_tie_threshold_pp
    ]
    incomplete_tasks = [
        {
            "task_name": row["task_name"],
            "observed_schema_count": row["observed_schema_count"],
            "missing_schema_ids": row["missing_schema_ids"],
            "infra_blocked_schema_ids": row["infra_blocked_schema_ids"],
            "runtime_blocked_schema_ids": row["runtime_blocked_schema_ids"],
            "ambiguous_schema_ids": row["ambiguous_schema_ids"],
        }
        for row in task_rows
        if not row["full_coverage"]
    ]

    schema_pair_correlations = compute_schema_pair_correlations(task_rows, schema_ids)
    correlation_values = [
        abs(float(row["pearson_correlation"]))
        for row in schema_pair_correlations
        if row["pearson_correlation"] is not None
    ]
    mean_abs_schema_pair_correlation = (
        round(mean(correlation_values), 4) if correlation_values else None
    )

    schema_diagnostics: list[dict[str, Any]] = []
    schema_training_assignments: list[dict[str, Any]] = []
    flat_schema_columns: list[dict[str, Any]] = []
    assignments_by_task = {str(row["task_name"]): row for row in assigned_rows}
    multi_by_schema: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in multi_assignments:
        multi_by_schema[str(row["schema_id"])].append(row)
    for schema_id in schema_ids:
        observed_scores = [
            float(row["scores"][schema_id])
            for row in task_rows
            if row["scores"].get(schema_id) is not None
        ]
        assigned_for_schema = [
            row for row in assigned_rows if row["assigned_category"] == schema_id and row["best_score"] is not None
        ]
        assigned_score_values = [
            float(row["best_score"])
            for row in assigned_for_schema
            if row["best_score"] is not None
        ]
        top_tasks = sorted(
            (
                {
                    "task_name": row["task_name"],
                    "score_pct": row["scores"][schema_id],
                    "reported_score_pct": row["reported_scores"].get(schema_id),
                    "best_observed_schema": row["best_observed_schema"],
                    "best_observed_score": row["best_observed_score"],
                    "schema_rank": (
                        1
                        + sum(
                            1
                            for other_schema_id in schema_ids
                            if row["scores"].get(other_schema_id) is not None
                            and float(row["scores"][other_schema_id]) > float(row["scores"][schema_id])
                        )
                    ),
                }
                for row in task_rows
                if row["scores"].get(schema_id) is not None
            ),
            key=lambda item: (-float(item["score_pct"]), str(item["task_name"])),
        )
        update_evidence_task_names = [
            str(row["task_name"])
            for row in sorted(
                multi_by_schema.get(schema_id, []),
                key=lambda item: (
                    0 if item.get("primary_assignment") else 1,
                    -float(item.get("assignment_score_pct") or 0.0),
                    str(item.get("task_name")),
                ),
            )
        ]
        top_k_tasks_added: list[str] = []
        for item in top_tasks:
            task_name = str(item["task_name"])
            if task_name in update_evidence_task_names:
                continue
            if len(update_evidence_task_names) >= update_floor_k:
                break
            update_evidence_task_names.append(task_name)
            top_k_tasks_added.append(task_name)

        top_task_by_name = {str(item["task_name"]): item for item in top_tasks}
        multi_by_task = {
            str(row["task_name"]): row
            for row in multi_by_schema.get(schema_id, [])
        }
        for task_name in update_evidence_task_names:
            item = top_task_by_name.get(task_name)
            if item is None:
                continue
            primary_assignment = assignments_by_task.get(task_name)
            multi_row = multi_by_task.get(task_name, {})
            schema_training_assignments.append(
                {
                    "schema_id": schema_id,
                    "task_name": task_name,
                    "evidence_role": (
                        str(multi_row.get("assignment_role"))
                        if task_name not in top_k_tasks_added and multi_row
                        else "floor_top_score"
                    ),
                    "evidence_reasons": str(multi_row.get("assignment_reasons") or ""),
                    "schema_score": item["score_pct"],
                    "schema_reported_score": item["reported_score_pct"],
                    "schema_rank_for_task": item["schema_rank"],
                    "schema_delta_vs_r0_post_best_pp": (
                        multi_row.get("delta_vs_r0_post_best_pp") if multi_row else None
                    ),
                    "schema_trajectory_quality": (
                        multi_row.get("trajectory_quality") if multi_row else None
                    ),
                    "primary_assigned_category": (
                        None if primary_assignment is None else primary_assignment.get("assigned_category")
                    ),
                    "task_best_schema": item["best_observed_schema"],
                    "task_best_score": item["best_observed_score"],
                }
            )

        score_range_pp = (
            round(max(observed_scores) - min(observed_scores), 2) if len(observed_scores) >= 2 else None
        )
        schema_row = {
            "schema_id": schema_id,
            "primary_assigned_count": cluster_size_map[schema_id],
            "multi_assigned_count": len(multi_by_schema.get(schema_id, [])),
            "observed_task_count": len(observed_scores),
            "occupancy_share": (
                round(cluster_size_map[schema_id] / assigned_task_count, 4) if assigned_task_count else 0.0
            ),
            "mean_assigned_score": (
                round(mean(assigned_score_values), 2) if assigned_score_values else None
            ),
            "mean_observed_score": round(mean(observed_scores), 2) if observed_scores else None,
            "score_stddev_pp": (
                round(pstdev(observed_scores), 2) if len(observed_scores) >= 2 else None
            ),
            "score_range_pp": score_range_pp,
            "empty": cluster_size_map[schema_id] == 0,
            "near_empty": 0 < cluster_size_map[schema_id] < near_empty_threshold,
            "below_update_floor": cluster_size_map[schema_id] < update_floor_k,
            "training_evidence_count": len(update_evidence_task_names),
            "below_training_floor": len(update_evidence_task_names) < update_floor_k,
            "update_floor_k": update_floor_k,
            "update_evidence_task_names": update_evidence_task_names,
            "top_k_tasks_added": top_k_tasks_added,
        }
        schema_diagnostics.append(schema_row)
        if score_range_pp is not None and score_range_pp <= flat_column_range_pp:
            flat_schema_columns.append(
                {
                    "schema_id": schema_id,
                    "observed_task_count": len(observed_scores),
                    "score_range_pp": score_range_pp,
                    "score_stddev_pp": schema_row["score_stddev_pp"],
                }
            )

    collapse_warnings: list[dict[str, Any]] = []
    if occupied_cluster_count <= 2 and assigned_task_count:
        collapse_warnings.append(
            {
                "kind": "low_occupied_cluster_count",
                "message": f"Only {occupied_cluster_count} schemas are occupied by primary assignment.",
            }
        )
    if largest_cluster_share >= dominant_share_threshold and assigned_task_count:
        collapse_warnings.append(
            {
                "kind": "dominant_schema",
                "message": f"Largest cluster share is {largest_cluster_share:.2f}.",
            }
        )
    low_margin_fraction = (
        round(len(low_margin_tasks) / assigned_task_count, 4) if assigned_task_count else 0.0
    )
    if low_margin_fraction >= 0.50 and assigned_task_count:
        collapse_warnings.append(
            {
                "kind": "high_low_margin_fraction",
                "message": f"Low-margin fraction is {low_margin_fraction:.2f}.",
            }
        )
    if mean_abs_schema_pair_correlation is not None and mean_abs_schema_pair_correlation >= 0.95:
        collapse_warnings.append(
            {
                "kind": "high_schema_pair_correlation",
                "message": f"Mean absolute schema-pair correlation is {mean_abs_schema_pair_correlation:.2f}.",
            }
        )

    return {
        "summary": {
            "task_count_total": len(task_rows),
            "task_count_with_scores": scored_task_count,
            "task_count_full_coverage": sum(1 for row in task_rows if row["full_coverage"]),
            "task_count_partial_coverage": sum(
                1
                for row in task_rows
                if 0 < row["observed_schema_count"] < len(schema_ids)
            ),
            "task_count_no_scores": sum(1 for row in task_rows if row["observed_schema_count"] == 0),
            "assigned_task_count": assigned_task_count,
            "unassigned_task_count": len(assignments) - assigned_task_count,
            "occupied_cluster_count": occupied_cluster_count,
            "cluster_sizes": cluster_size_map,
            "multi_assignment_count": len(multi_assignments),
            "multi_assignment_schema_counts": {
                schema_id: len(multi_by_schema.get(schema_id, []))
                for schema_id in schema_ids
            },
            "largest_cluster_share": largest_cluster_share,
            "cluster_size_entropy": round(entropy, 4) if assigned_task_count else None,
            "mean_assignment_margin_pp": round(mean(margins), 2) if margins else None,
            "low_margin_task_fraction": low_margin_fraction,
            "mean_abs_schema_pair_correlation": mean_abs_schema_pair_correlation,
            "update_floor_k": update_floor_k,
        },
        "low_margin_tasks": low_margin_tasks,
        "top3_tied_tasks": top3_tied_tasks,
        "incomplete_tasks": incomplete_tasks,
        "schema_diagnostics": schema_diagnostics,
        "schema_training_assignments": schema_training_assignments,
        "flat_schema_columns": flat_schema_columns,
        "schema_pair_correlations": schema_pair_correlations,
        "collapse_warnings": collapse_warnings,
    }


def build_score_matrix_artifacts(
    *,
    pair_rows: list[dict[str, Any]],
    task_rows: list[dict[str, Any]],
    schema_ids: list[str],
    round_id: str,
) -> dict[str, Any]:
    long_rows: list[dict[str, Any]] = []
    for row in sorted(pair_rows, key=lambda item: (item["task_name"], item["schema_id"])):
        long_rows.append(
            {
                "round_id": round_id,
                "task_name": row["task_name"],
                "schema_id": row["schema_id"],
                "pair_id": row["pair_id"],
                "score": row["assignment_score_pct"],
                "reported_score": row["reported_score_pct"],
                "assignment_score_mode": row["assignment_score_mode"],
                "round_mean_score_pct": row["round_mean_score_pct"],
                "round_weighted_mean_score_pct": row["round_weighted_mean_score_pct"],
                "growth_component_score_pct": row["growth_component_score_pct"],
                "trajectory_signal_score_pct": row["trajectory_signal_score_pct"],
                "trajectory_quality": row["trajectory_quality"],
                "trajectory_round_count": row["trajectory_round_count"],
                "trajectory_post_r0_round_count": row["trajectory_post_r0_round_count"],
                "trajectory_non_decreasing_all_rounds": row["trajectory_non_decreasing_all_rounds"],
                "trajectory_post_r0_score_non_decreasing": row[
                    "trajectory_post_r0_score_non_decreasing"
                ],
                "trajectory_post_r0_delta_non_decreasing": row["trajectory_post_r0_delta_non_decreasing"],
                "trajectory_post_r0_all_ge_r0": row["trajectory_post_r0_all_ge_r0"],
                "trajectory_post_r0_all_100": row["trajectory_post_r0_all_100"],
                "trajectory_ideal_zero_to_full_stable": row["trajectory_ideal_zero_to_full_stable"],
                "post_r0_improved_round_count": row["post_r0_improved_round_count"],
                "post_r0_improvement_area_score_pct": row[
                    "post_r0_improvement_area_score_pct"
                ],
                "post_r0_improved_round_fraction_score_pct": row[
                    "post_r0_improved_round_fraction_score_pct"
                ],
                "post_r0_terminal_improvement_score_pct": row[
                    "post_r0_terminal_improvement_score_pct"
                ],
                "earliest_full_score_round": row["earliest_full_score_round"],
                "rounds_at_100_count": row["rounds_at_100_count"],
                "post_r0_best_score_pct": row["post_r0_best_score_pct"],
                "delta_vs_r0_best_pp": row["delta_vs_r0_best_pp"],
                "delta_vs_r0_final_pp": row["delta_vs_r0_final_pp"],
                "delta_vs_r0_post_best_pp": row["delta_vs_r0_post_best_pp"],
                "delta_vs_r0_r1_pp": row["delta_vs_r0_r1_pp"],
                "delta_vs_r0_r2_pp": row["delta_vs_r0_r2_pp"],
                "delta_vs_r0_r3_pp": row["delta_vs_r0_r3_pp"],
                "round_r0_to_best_delta_pp": row["round_r0_to_best_delta_pp"],
                "round_r0_to_final_delta_pp": row["round_r0_to_final_delta_pp"],
                "round_r0_score_pct": row[round_score_key(0)],
                "round_r1_score_pct": row[round_score_key(1)],
                "round_r2_score_pct": row[round_score_key(2)],
                "round_r3_score_pct": row[round_score_key(3)],
                "success": row["latest_status"] == "completed",
                "best_score": row["best_observed_score_pct"],
                "final_score": row["selected_score_pct"],
                "timeout_flag": row["timeout_detected"],
                "has_intermediate_exceptions": row["has_intermediate_exceptions"],
                "assignment_eligible": row["assignment_eligible"],
                "latest_status": row["latest_status"],
                "evidence_class": row["evidence_class"],
                "official_c0_pct": row["official_c0_pct"],
                "official_c1_pct": row["official_c1_pct"],
                "delta_vs_c0_pp": row["delta_vs_c0_pp"],
                "delta_vs_c1_pp": row["delta_vs_c1_pp"],
                "failure_type": row["failure_type"],
                "failure_summary": row["failure_summary"],
                "notes": row["notes"],
            }
        )

    wide_rows: list[dict[str, Any]] = []
    for task_row in task_rows:
        row: dict[str, Any] = {
            "task_name": task_row["task_name"],
            "observed_schema_count": task_row["observed_schema_count"],
            "full_coverage": task_row["full_coverage"],
            "best_observed_schema": task_row["best_observed_schema"],
            "best_observed_score": task_row["best_observed_score"],
            "second_observed_schema": task_row["second_observed_schema"],
            "second_observed_score": task_row["second_observed_score"],
            "top3_spread_pp": task_row["top3_spread_pp"],
            "missing_schema_ids": ";".join(task_row["missing_schema_ids"]),
            "infra_blocked_schema_ids": ";".join(task_row["infra_blocked_schema_ids"]),
            "runtime_blocked_schema_ids": ";".join(task_row["runtime_blocked_schema_ids"]),
            "ambiguous_schema_ids": ";".join(task_row["ambiguous_schema_ids"]),
        }
        for schema_id in schema_ids:
            row[schema_id] = task_row["scores"].get(schema_id)
        wide_rows.append(row)

    return {
        "schema_ids": schema_ids,
        "long_rows": long_rows,
        "wide_rows": wide_rows,
        "task_rows": task_rows,
    }


def render_summary_markdown(
    *,
    generated_at: str,
    round_id: str,
    schema_ids: list[str],
    assignments: list[dict[str, Any]],
    diagnostics: dict[str, Any],
    output_dir: Path,
) -> str:
    summary = diagnostics["summary"]
    lines = [
        f"# SkillX Round0 Outer-Loop Control Plane: `{round_id}`",
        "",
        f"- generated_at: `{generated_at}`",
        f"- output_dir: `{display_path(output_dir)}`",
        f"- schemas: `{', '.join(schema_ids)}`",
        f"- assignment_score_mode: `{summary.get('assignment_score_mode')}`",
        f"- assignment_score_formula: `{summary.get('assignment_score_formula')}`",
        f"- tie_break_policy: `{summary.get('tie_break_policy')}`",
        f"- tasks_total: `{summary['task_count_total']}`",
        f"- tasks_with_scores: `{summary['task_count_with_scores']}`",
        f"- full_coverage_tasks: `{summary['task_count_full_coverage']}`",
        f"- assigned_tasks: `{summary['assigned_task_count']}`",
        f"- multi_assignments: `{summary.get('multi_assignment_count')}`",
        f"- occupied_cluster_count: `{summary['occupied_cluster_count']}`",
        f"- mean_assignment_margin_pp: `{summary['mean_assignment_margin_pp']}`",
        f"- low_margin_task_fraction: `{summary['low_margin_task_fraction']}`",
        "",
        "## Cluster Occupancy",
        "",
        "| schema_id | primary_assigned | multi_assigned | training_evidence | mean_assigned_score | observed_task_count | floor_k | below_training_floor |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in diagnostics["schema_diagnostics"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["schema_id"]),
                    str(row["primary_assigned_count"]),
                    str(row["multi_assigned_count"]),
                    str(row["training_evidence_count"]),
                    "-" if row["mean_assigned_score"] is None else f"{row['mean_assigned_score']:.2f}",
                    str(row["observed_task_count"]),
                    str(row["update_floor_k"]),
                    "yes" if row["below_training_floor"] else "no",
                ]
            )
            + " |"
        )

    if diagnostics.get("schema_training_assignments"):
        lines.extend(
            [
                "",
                "## Schema Training Assignments",
                "",
                "| schema_id | task | role | reasons | score | dR0 | trajectory | rank | primary_assigned |",
                "| --- | --- | --- | --- | ---: | ---: | --- | ---: | --- |",
            ]
        )
        for row in diagnostics["schema_training_assignments"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row["schema_id"]),
                        str(row["task_name"]),
                        str(row["evidence_role"]),
                        str(row.get("evidence_reasons") or "-"),
                        "-" if row["schema_score"] is None else f"{float(row['schema_score']):.2f}",
                        (
                            "-"
                            if row.get("schema_delta_vs_r0_post_best_pp") is None
                            else f"{float(row['schema_delta_vs_r0_post_best_pp']):.2f}"
                        ),
                        str(row.get("schema_trajectory_quality") or "-"),
                        "-" if row["schema_rank_for_task"] is None else str(row["schema_rank_for_task"]),
                        str(row["primary_assigned_category"]),
                    ]
                )
                + " |"
            )

    lines.extend(["", "## Assigned Tasks", "", "| task | assigned | best | second | margin_pp | confidence | tie_break |", "| --- | --- | ---: | ---: | ---: | --- | --- |"])
    for row in assignments:
        if row["assignment_status"] != "assigned":
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["task_name"]),
                    str(row["assigned_category"]),
                    "-" if row["best_score"] is None else f"{float(row['best_score']):.2f}",
                    "-" if row["second_best_score"] is None else f"{float(row['second_best_score']):.2f}",
                    "-" if row["margin_pp"] is None else f"{float(row['margin_pp']):.2f}",
                    str(row["assignment_confidence"]),
                    str(row["tie_break_reason"] or "no"),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Unassigned Tasks", ""])
    for row in assignments:
        if row["assignment_status"] == "assigned":
            continue
        lines.append(
            f"- `{row['task_name']}`: status=`{row['assignment_status']}`, observed=`{row['observed_schema_count']}`, missing=`{row['missing_schema_ids']}`"
        )

    if diagnostics["collapse_warnings"]:
        lines.extend(["", "## Collapse Warnings", ""])
        for warning in diagnostics["collapse_warnings"]:
            lines.append(f"- `{warning['kind']}`: {warning['message']}")

    if diagnostics["low_margin_tasks"]:
        lines.extend(["", "## Low-Margin Tasks", ""])
        for row in diagnostics["low_margin_tasks"]:
            lines.append(
                f"- `{row['task_name']}`: assigned=`{row['assigned_category']}`, margin_pp=`{row['margin_pp']}`, tie_break=`{row['tie_break_reason'] or 'no'}`"
            )

    if diagnostics["top3_tied_tasks"]:
        lines.extend(["", "## Top-3 Near Ties", ""])
        for row in diagnostics["top3_tied_tasks"]:
            lines.append(
                f"- `{row['task_name']}`: top3_spread_pp=`{row['top3_spread_pp']}`, best=`{row['best_observed_schema']}`"
            )

    return "\n".join(lines) + "\n"


def build_outer_loop_artifacts(
    *,
    round0_root: Path,
    global_pair_status_path: Path,
    prompt_bank_path: Path,
    round_id: str,
    assignment_score_mode: str,
    post_r0_improvement_area_weight: float = DEFAULT_POST_R0_IMPROVEMENT_AREA_WEIGHT,
    post_r0_monotonicity_weight: float = DEFAULT_POST_R0_MONOTONICITY_WEIGHT,
    post_r0_improved_round_count_weight: float = DEFAULT_POST_R0_IMPROVED_ROUND_COUNT_WEIGHT,
    post_r0_terminal_improvement_weight: float = DEFAULT_POST_R0_TERMINAL_IMPROVEMENT_WEIGHT,
    min_assignment_score_pct: float = DEFAULT_MIN_ASSIGNMENT_SCORE_PCT,
    epsilon_pp: float,
    high_confidence_margin_pp: float,
    medium_confidence_margin_pp: float,
    require_full_coverage: bool,
    dominant_share_threshold: float,
    top3_tie_threshold_pp: float,
    near_empty_threshold: int,
    update_floor_fraction: float,
    flat_column_range_pp: float,
    multi_assignment_min_score_pct: float = DEFAULT_MULTI_ASSIGNMENT_MIN_SCORE_PCT,
    multi_assignment_near_best_margin_pp: float = DEFAULT_MULTI_ASSIGNMENT_NEAR_BEST_MARGIN_PP,
    multi_assignment_min_delta_vs_r0_pp: float = DEFAULT_MULTI_ASSIGNMENT_MIN_DELTA_VS_R0_PP,
    task_cluster_inputs_path: Path | None = DEFAULT_TASK_CLUSTER_INPUTS_PATH,
    balance_tie_max_loss_pp: float = DEFAULT_BALANCE_TIE_MAX_LOSS_PP,
    assignment_random_seed: str = DEFAULT_ASSIGNMENT_RANDOM_SEED,
) -> dict[str, Any]:
    prompt_bank_schema_ids = load_schema_ids(prompt_bank_path)
    task_profiles = load_task_profile_index(task_cluster_inputs_path)
    discovered_schema_ids, pair_rows = build_pair_rows(
        global_pair_status_path=global_pair_status_path,
        round0_root=round0_root,
        assignment_score_mode=assignment_score_mode,
        post_r0_improvement_area_weight=post_r0_improvement_area_weight,
        post_r0_monotonicity_weight=post_r0_monotonicity_weight,
        post_r0_improved_round_count_weight=post_r0_improved_round_count_weight,
        post_r0_terminal_improvement_weight=post_r0_terminal_improvement_weight,
    )
    schema_ids = [
        schema_id for schema_id in prompt_bank_schema_ids if schema_id in discovered_schema_ids
    ] + [
        schema_id for schema_id in discovered_schema_ids if schema_id not in prompt_bank_schema_ids
    ]
    task_rows = group_pair_rows_by_task(pair_rows, schema_ids, task_profiles)
    assignments = assign_tasks(
        task_rows=task_rows,
        schema_ids=schema_ids,
        epsilon_pp=epsilon_pp,
        min_assignment_score_pct=min_assignment_score_pct,
        high_confidence_margin_pp=high_confidence_margin_pp,
        medium_confidence_margin_pp=medium_confidence_margin_pp,
        require_full_coverage=require_full_coverage,
        balance_tie_max_loss_pp=balance_tie_max_loss_pp,
        assignment_random_seed=assignment_random_seed,
    )
    multi_assignments = build_multi_assignments(
        pair_rows=pair_rows,
        assignments=assignments,
        min_score_pct=multi_assignment_min_score_pct,
        near_best_margin_pp=multi_assignment_near_best_margin_pp,
        min_delta_vs_r0_pp=multi_assignment_min_delta_vs_r0_pp,
    )
    multi_by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in multi_assignments:
        multi_by_task[str(row["task_name"])].append(row)
    for assignment in assignments:
        task_multi = sorted(
            multi_by_task.get(str(assignment["task_name"]), []),
            key=lambda item: str(item["schema_id"]),
        )
        assignment["multi_assigned_categories"] = ";".join(
            str(row["schema_id"]) for row in task_multi
        )
        assignment["multi_assignment_count"] = len(task_multi)
    diagnostics = build_diagnostics(
        task_rows=task_rows,
        assignments=assignments,
        multi_assignments=multi_assignments,
        schema_ids=schema_ids,
        epsilon_pp=epsilon_pp,
        dominant_share_threshold=dominant_share_threshold,
        top3_tie_threshold_pp=top3_tie_threshold_pp,
        near_empty_threshold=near_empty_threshold,
        update_floor_fraction=update_floor_fraction,
        flat_column_range_pp=flat_column_range_pp,
    )
    diagnostics["summary"]["assignment_score_mode"] = assignment_score_mode
    diagnostics["summary"]["assignment_score_formula"] = (
        "reported_score" if assignment_score_mode == "reported"
        else (
            f"{post_r0_improvement_area_weight:g}*mean(max(R1..R3 - R0, 0)) + "
            f"{post_r0_monotonicity_weight:g}*post_r0_monotonicity + "
            f"{post_r0_improved_round_count_weight:g}*fraction(R1..R3 > R0) + "
            f"{post_r0_terminal_improvement_weight:g}*max(last_post_round - R0, 0)"
        )
    )
    diagnostics["summary"]["tie_break_policy"] = (
        "semantic_prior -> balance_when_score_range_leq_threshold -> stable_random"
    )
    score_matrix = build_score_matrix_artifacts(
        pair_rows=pair_rows,
        task_rows=task_rows,
        schema_ids=schema_ids,
        round_id=round_id,
    )
    return {
        "generated_at": _timestamp(),
        "config": {
            "round_id": round_id,
            "round0_root": display_path(round0_root.resolve()),
            "global_pair_status_path": display_path(global_pair_status_path.resolve()),
            "prompt_bank_path": display_path(prompt_bank_path.resolve()),
            "task_cluster_inputs_path": (
                None if task_cluster_inputs_path is None else display_path(task_cluster_inputs_path.resolve())
            ),
            "assignment_score_mode": assignment_score_mode,
            "post_r0_improvement_area_weight": post_r0_improvement_area_weight,
            "post_r0_monotonicity_weight": post_r0_monotonicity_weight,
            "post_r0_improved_round_count_weight": post_r0_improved_round_count_weight,
            "post_r0_terminal_improvement_weight": post_r0_terminal_improvement_weight,
            "min_assignment_score_pct": min_assignment_score_pct,
            "round_score_weights": DEFAULT_ROUND_SCORE_WEIGHTS,
            "balance_tie_max_loss_pp": balance_tie_max_loss_pp,
            "assignment_random_seed": assignment_random_seed,
            "epsilon_pp": epsilon_pp,
            "high_confidence_margin_pp": high_confidence_margin_pp,
            "medium_confidence_margin_pp": medium_confidence_margin_pp,
            "require_full_coverage": require_full_coverage,
            "dominant_share_threshold": dominant_share_threshold,
            "top3_tie_threshold_pp": top3_tie_threshold_pp,
            "near_empty_threshold": near_empty_threshold,
            "update_floor_fraction": update_floor_fraction,
            "flat_column_range_pp": flat_column_range_pp,
            "multi_assignment_min_score_pct": multi_assignment_min_score_pct,
            "multi_assignment_near_best_margin_pp": multi_assignment_near_best_margin_pp,
            "multi_assignment_min_delta_vs_r0_pp": multi_assignment_min_delta_vs_r0_pp,
        },
        "schema_ids": schema_ids,
        "pair_rows": pair_rows,
        "score_matrix": score_matrix,
        "assignments": assignments,
        "multi_assignments": multi_assignments,
        "diagnostics": diagnostics,
    }


def write_outer_loop_artifacts(*, payload: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    score_matrix = payload["score_matrix"]
    assignments = payload["assignments"]
    multi_assignments = payload["multi_assignments"]
    diagnostics = payload["diagnostics"]

    score_matrix_csv_path = output_dir / "score_matrix.csv"
    score_matrix_wide_csv_path = output_dir / "score_matrix_wide.csv"
    score_matrix_json_path = output_dir / "score_matrix.json"
    assignments_csv_path = output_dir / "assignments.csv"
    assignments_json_path = output_dir / "assignments.json"
    multi_assignments_csv_path = output_dir / "multi_assignments.csv"
    multi_assignments_json_path = output_dir / "multi_assignments.json"
    schema_training_assignments_csv_path = output_dir / "schema_training_assignments.csv"
    schema_training_assignments_json_path = output_dir / "schema_training_assignments.json"
    diagnostics_json_path = output_dir / "diagnostics.json"
    bundle_json_path = output_dir / "control_plane_bundle.json"
    summary_md_path = output_dir / "summary.md"

    write_csv(
        score_matrix_csv_path,
        score_matrix["long_rows"],
        fieldnames=list(score_matrix["long_rows"][0].keys()) if score_matrix["long_rows"] else [
            "round_id",
            "task_name",
            "schema_id",
            "pair_id",
            "score",
            "reported_score",
            "assignment_score_mode",
            "round_mean_score_pct",
            "round_weighted_mean_score_pct",
            "growth_component_score_pct",
            "trajectory_signal_score_pct",
            "trajectory_quality",
            "trajectory_post_r0_score_non_decreasing",
            "post_r0_improved_round_count",
            "post_r0_improvement_area_score_pct",
            "post_r0_improved_round_fraction_score_pct",
            "post_r0_terminal_improvement_score_pct",
            "round_r0_to_best_delta_pp",
            "round_r0_to_final_delta_pp",
            "round_r0_score_pct",
            "round_r1_score_pct",
            "round_r2_score_pct",
            "round_r3_score_pct",
            "success",
            "best_score",
            "final_score",
            "timeout_flag",
            "has_intermediate_exceptions",
            "assignment_eligible",
            "latest_status",
            "evidence_class",
            "official_c0_pct",
            "official_c1_pct",
            "delta_vs_c0_pp",
            "delta_vs_c1_pp",
            "failure_type",
            "failure_summary",
            "notes",
        ],
    )
    write_csv(
        score_matrix_wide_csv_path,
        score_matrix["wide_rows"],
        fieldnames=list(score_matrix["wide_rows"][0].keys()) if score_matrix["wide_rows"] else [
            "task_name",
            "observed_schema_count",
            "full_coverage",
            "best_observed_schema",
            "best_observed_score",
            "second_observed_schema",
            "second_observed_score",
            "top3_spread_pp",
            "missing_schema_ids",
            "infra_blocked_schema_ids",
            "runtime_blocked_schema_ids",
            "ambiguous_schema_ids",
            *payload["schema_ids"],
        ],
    )
    write_json(
        score_matrix_json_path,
        {
            "generated_at": payload["generated_at"],
            "config": payload["config"],
            "schema_ids": payload["schema_ids"],
            "long_rows": score_matrix["long_rows"],
            "wide_rows": score_matrix["wide_rows"],
        },
    )
    write_csv(
        assignments_csv_path,
        assignments,
        fieldnames=list(assignments[0].keys()) if assignments else [
            "task_name",
            "assignment_status",
            "assigned_category",
            "best_observed_category",
            "best_score",
            "best_reported_score",
            "second_best_category",
            "second_best_score",
            "second_reported_score",
            "margin_pp",
            "assignment_confidence",
            "tie_break_used",
            "tie_break_reason",
            "tie_candidate_schema_ids",
            "tie_candidate_count",
            "tie_candidate_semantic_scores",
            "tie_candidate_score_range_pp",
            "observed_schema_count",
            "full_coverage",
            "missing_schema_ids",
            "infra_blocked_schema_ids",
            "runtime_blocked_schema_ids",
            "ambiguous_schema_ids",
            "top3_spread_pp",
            "assigned_score",
            "assigned_reported_score",
        ],
    )
    write_json(
        assignments_json_path,
        {
            "generated_at": payload["generated_at"],
            "config": payload["config"],
            "assignments": assignments,
        },
    )
    write_csv(
        multi_assignments_csv_path,
        multi_assignments,
        fieldnames=list(multi_assignments[0].keys()) if multi_assignments else [
            "task_name",
            "schema_id",
            "assignment_role",
            "assignment_reasons",
            "primary_assigned_category",
            "primary_assignment",
            "assignment_score_pct",
            "reported_score_pct",
            "best_task_assignment_score_pct",
            "within_best_margin_pp",
            "delta_vs_r0_post_best_pp",
            "delta_vs_r0_final_pp",
            "trajectory_quality",
            "trajectory_signal_score_pct",
            "post_r0_improved_round_count",
            "post_r0_improvement_area_score_pct",
            "post_r0_improved_round_fraction_score_pct",
            "post_r0_terminal_improvement_score_pct",
            "trajectory_non_decreasing_all_rounds",
            "trajectory_post_r0_delta_non_decreasing",
            "trajectory_post_r0_all_ge_r0",
            "trajectory_ideal_zero_to_full_stable",
            "evidence_class",
            "latest_status",
        ],
    )
    write_json(
        multi_assignments_json_path,
        {
            "generated_at": payload["generated_at"],
            "config": payload["config"],
            "multi_assignments": multi_assignments,
        },
    )
    schema_training_assignments = diagnostics.get("schema_training_assignments", [])
    write_csv(
        schema_training_assignments_csv_path,
        schema_training_assignments,
        fieldnames=list(schema_training_assignments[0].keys()) if schema_training_assignments else [
            "schema_id",
            "task_name",
            "evidence_role",
            "evidence_reasons",
            "schema_score",
            "schema_reported_score",
            "schema_rank_for_task",
            "schema_delta_vs_r0_post_best_pp",
            "schema_trajectory_quality",
            "primary_assigned_category",
            "task_best_schema",
            "task_best_score",
        ],
    )
    write_json(
        schema_training_assignments_json_path,
        {
            "generated_at": payload["generated_at"],
            "config": payload["config"],
            "schema_training_assignments": schema_training_assignments,
        },
    )
    write_json(
        diagnostics_json_path,
        {
            "generated_at": payload["generated_at"],
            "config": payload["config"],
            "diagnostics": diagnostics,
        },
    )
    write_json(bundle_json_path, payload)
    summary_md_path.write_text(
        render_summary_markdown(
            generated_at=str(payload["generated_at"]),
            round_id=str(payload["config"]["round_id"]),
            schema_ids=payload["schema_ids"],
            assignments=assignments,
            diagnostics=diagnostics,
            output_dir=output_dir,
        )
    )
    return {
        "score_matrix_csv": display_path(score_matrix_csv_path),
        "score_matrix_wide_csv": display_path(score_matrix_wide_csv_path),
        "score_matrix_json": display_path(score_matrix_json_path),
        "assignments_csv": display_path(assignments_csv_path),
        "assignments_json": display_path(assignments_json_path),
        "multi_assignments_csv": display_path(multi_assignments_csv_path),
        "multi_assignments_json": display_path(multi_assignments_json_path),
        "schema_training_assignments_csv": display_path(schema_training_assignments_csv_path),
        "schema_training_assignments_json": display_path(schema_training_assignments_json_path),
        "diagnostics_json": display_path(diagnostics_json_path),
        "bundle_json": display_path(bundle_json_path),
        "summary_md": display_path(summary_md_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round0-root", type=Path, default=DEFAULT_ROUND0_ROOT)
    parser.add_argument("--global-pair-status-path", type=Path, default=DEFAULT_GLOBAL_PAIR_STATUS_PATH)
    parser.add_argument("--prompt-bank-path", type=Path, default=DEFAULT_PROMPT_BANK_PATH)
    parser.add_argument("--task-cluster-inputs-path", type=Path, default=DEFAULT_TASK_CLUSTER_INPUTS_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--round-id", default="outer-loop-round0")
    parser.add_argument(
        "--assignment-score-mode",
        choices=["trajectory", "reported"],
        default=DEFAULT_ASSIGNMENT_SCORE_MODE,
        help="Use reported final/best score only, or the default trajectory-aware score.",
    )
    parser.add_argument(
        "--post-r0-improvement-area-weight",
        type=float,
        default=DEFAULT_POST_R0_IMPROVEMENT_AREA_WEIGHT,
        help="Weight for the average positive R1/R2/R3 improvement over R0.",
    )
    parser.add_argument(
        "--post-r0-monotonicity-weight",
        type=float,
        default=DEFAULT_POST_R0_MONOTONICITY_WEIGHT,
        help="Weight for the R0-relative monotonicity/persistence signal.",
    )
    parser.add_argument(
        "--post-r0-improved-round-count-weight",
        type=float,
        default=DEFAULT_POST_R0_IMPROVED_ROUND_COUNT_WEIGHT,
        help="Weight for the fraction of post-R0 rounds that beat R0.",
    )
    parser.add_argument(
        "--post-r0-terminal-improvement-weight",
        type=float,
        default=DEFAULT_POST_R0_TERMINAL_IMPROVEMENT_WEIGHT,
        help="Weight for the last observed post-R0 round's improvement over R0.",
    )
    parser.add_argument(
        "--min-assignment-score-pct",
        type=float,
        default=DEFAULT_MIN_ASSIGNMENT_SCORE_PCT,
        help="Do not primary-assign tasks whose best R0-relative score is at or below this value.",
    )
    parser.add_argument(
        "--balance-tie-max-loss-pp",
        type=float,
        default=DEFAULT_BALANCE_TIE_MAX_LOSS_PP,
        help="Only let cluster balance override the top score inside this near-tie score range.",
    )
    parser.add_argument(
        "--assignment-random-seed",
        default=DEFAULT_ASSIGNMENT_RANDOM_SEED,
        help="Seed string for reproducible random tie-breaking.",
    )
    parser.add_argument("--epsilon-pp", type=float, default=DEFAULT_MEDIUM_CONFIDENCE_MARGIN_PP)
    parser.add_argument(
        "--high-confidence-margin-pp",
        type=float,
        default=DEFAULT_HIGH_CONFIDENCE_MARGIN_PP,
    )
    parser.add_argument(
        "--medium-confidence-margin-pp",
        type=float,
        default=DEFAULT_MEDIUM_CONFIDENCE_MARGIN_PP,
    )
    parser.add_argument("--allow-partial-assignment", action="store_true")
    parser.add_argument(
        "--dominant-share-threshold",
        type=float,
        default=DEFAULT_DOMINANT_SHARE_THRESHOLD,
    )
    parser.add_argument(
        "--top3-tie-threshold-pp",
        type=float,
        default=DEFAULT_TOP3_TIE_THRESHOLD_PP,
    )
    parser.add_argument(
        "--near-empty-threshold",
        type=int,
        default=DEFAULT_NEAR_EMPTY_THRESHOLD,
    )
    parser.add_argument(
        "--update-floor-fraction",
        type=float,
        default=DEFAULT_UPDATE_FLOOR_FRACTION,
    )
    parser.add_argument(
        "--flat-column-range-pp",
        type=float,
        default=DEFAULT_FLAT_COLUMN_RANGE_PP,
    )
    parser.add_argument(
        "--multi-assignment-min-score-pct",
        type=float,
        default=DEFAULT_MULTI_ASSIGNMENT_MIN_SCORE_PCT,
    )
    parser.add_argument(
        "--multi-assignment-near-best-margin-pp",
        type=float,
        default=DEFAULT_MULTI_ASSIGNMENT_NEAR_BEST_MARGIN_PP,
    )
    parser.add_argument(
        "--multi-assignment-min-delta-vs-r0-pp",
        type=float,
        default=DEFAULT_MULTI_ASSIGNMENT_MIN_DELTA_VS_R0_PP,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_outer_loop_artifacts(
        round0_root=args.round0_root,
        global_pair_status_path=args.global_pair_status_path,
        prompt_bank_path=args.prompt_bank_path,
        round_id=str(args.round_id),
        assignment_score_mode=str(args.assignment_score_mode),
        post_r0_improvement_area_weight=float(args.post_r0_improvement_area_weight),
        post_r0_monotonicity_weight=float(args.post_r0_monotonicity_weight),
        post_r0_improved_round_count_weight=float(args.post_r0_improved_round_count_weight),
        post_r0_terminal_improvement_weight=float(args.post_r0_terminal_improvement_weight),
        min_assignment_score_pct=float(args.min_assignment_score_pct),
        epsilon_pp=float(args.epsilon_pp),
        high_confidence_margin_pp=float(args.high_confidence_margin_pp),
        medium_confidence_margin_pp=float(args.medium_confidence_margin_pp),
        require_full_coverage=not bool(args.allow_partial_assignment),
        dominant_share_threshold=float(args.dominant_share_threshold),
        top3_tie_threshold_pp=float(args.top3_tie_threshold_pp),
        near_empty_threshold=int(args.near_empty_threshold),
        update_floor_fraction=float(args.update_floor_fraction),
        flat_column_range_pp=float(args.flat_column_range_pp),
        multi_assignment_min_score_pct=float(args.multi_assignment_min_score_pct),
        multi_assignment_near_best_margin_pp=float(args.multi_assignment_near_best_margin_pp),
        multi_assignment_min_delta_vs_r0_pp=float(args.multi_assignment_min_delta_vs_r0_pp),
        task_cluster_inputs_path=args.task_cluster_inputs_path,
        balance_tie_max_loss_pp=float(args.balance_tie_max_loss_pp),
        assignment_random_seed=str(args.assignment_random_seed),
    )
    outputs = write_outer_loop_artifacts(payload=payload, output_dir=args.output_dir)
    print(json.dumps(outputs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

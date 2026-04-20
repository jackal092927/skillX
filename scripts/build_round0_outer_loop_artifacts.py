#!/usr/bin/env python3
"""Build round-0 score-matrix, assignment, and diagnostics artifacts."""

from __future__ import annotations

import argparse
import csv
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
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
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
) -> dict[str, Any]:
    latest_status = str(pair_status.get("latest_status") or "unrun")
    reported_score_pct, score_basis = extract_reported_score(pair_report, pair_status)
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
    assignment_eligible = latest_status == "completed" and reported_score_pct is not None and evidence_class != "infra-blocked"

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
        pair_rows.append(summarize_pair_row(pair_status=pair_status, pair_report=pair_report))
    return [str(item) for item in schema_ids], sorted(pair_rows, key=lambda row: (row["task_name"], row["schema_id"]))


def group_pair_rows_by_task(pair_rows: list[dict[str, Any]], schema_ids: list[str]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in pair_rows:
        grouped[row["task_name"]][row["schema_id"]] = row

    task_rows: list[dict[str, Any]] = []
    for task_name in sorted(grouped):
        schema_map = grouped[task_name]
        scores = {
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
                "scores": scores,
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
    high_confidence_margin_pp: float,
    medium_confidence_margin_pp: float,
    require_full_coverage: bool,
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

        if not observed_scores:
            assignment_status = "unassigned_no_scores"
        elif len(observed_scores) < 2:
            assignment_status = "unassigned_insufficient_scores"
        elif require_full_coverage and not task_row["full_coverage"]:
            assignment_status = "unassigned_incomplete_row"
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
                use_balance = 0.0 < candidate_score_range <= epsilon_pp and len(candidates) <= 3
                if use_balance:
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
                        balance_candidates.sort(key=lambda item: str(item["schema_id"]))
                        chosen = balance_candidates[0]
                        tie_break_reason = "deterministic_fallback"
                else:
                    candidates.sort(key=lambda item: str(item["schema_id"]))
                    chosen = candidates[0]
                    tie_break_reason = "deterministic_fallback"
            assigned_category = str(chosen["schema_id"])
            cluster_sizes[assigned_category] += 1

        assigned_score = (
            task_row["scores"].get(assigned_category) if assigned_category is not None else None
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
            "second_best_category": None if second_observed is None else second_observed["schema_id"],
            "second_best_score": second_score,
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
    flat_schema_columns: list[dict[str, Any]] = []
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
                }
                for row in task_rows
                if row["scores"].get(schema_id) is not None
            ),
            key=lambda item: (-float(item["score_pct"]), str(item["task_name"])),
        )
        update_evidence_task_names = [str(row["task_name"]) for row in assigned_for_schema]
        top_k_tasks_added: list[str] = []
        for item in top_tasks:
            task_name = str(item["task_name"])
            if task_name in update_evidence_task_names:
                continue
            if len(update_evidence_task_names) >= update_floor_k:
                break
            update_evidence_task_names.append(task_name)
            top_k_tasks_added.append(task_name)

        score_range_pp = (
            round(max(observed_scores) - min(observed_scores), 2) if len(observed_scores) >= 2 else None
        )
        schema_row = {
            "schema_id": schema_id,
            "primary_assigned_count": cluster_size_map[schema_id],
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
                "score": row["reported_score_pct"],
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
        f"- tasks_total: `{summary['task_count_total']}`",
        f"- tasks_with_scores: `{summary['task_count_with_scores']}`",
        f"- full_coverage_tasks: `{summary['task_count_full_coverage']}`",
        f"- assigned_tasks: `{summary['assigned_task_count']}`",
        f"- occupied_cluster_count: `{summary['occupied_cluster_count']}`",
        f"- mean_assignment_margin_pp: `{summary['mean_assignment_margin_pp']}`",
        f"- low_margin_task_fraction: `{summary['low_margin_task_fraction']}`",
        "",
        "## Cluster Occupancy",
        "",
        "| schema_id | assigned_count | mean_assigned_score | observed_task_count | update_floor_k | below_floor |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in diagnostics["schema_diagnostics"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["schema_id"]),
                    str(row["primary_assigned_count"]),
                    "-" if row["mean_assigned_score"] is None else f"{row['mean_assigned_score']:.2f}",
                    str(row["observed_task_count"]),
                    str(row["update_floor_k"]),
                    "yes" if row["below_update_floor"] else "no",
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
    epsilon_pp: float,
    high_confidence_margin_pp: float,
    medium_confidence_margin_pp: float,
    require_full_coverage: bool,
    dominant_share_threshold: float,
    top3_tie_threshold_pp: float,
    near_empty_threshold: int,
    update_floor_fraction: float,
    flat_column_range_pp: float,
) -> dict[str, Any]:
    prompt_bank_schema_ids = load_schema_ids(prompt_bank_path)
    discovered_schema_ids, pair_rows = build_pair_rows(
        global_pair_status_path=global_pair_status_path,
        round0_root=round0_root,
    )
    schema_ids = [
        schema_id for schema_id in prompt_bank_schema_ids if schema_id in discovered_schema_ids
    ] + [
        schema_id for schema_id in discovered_schema_ids if schema_id not in prompt_bank_schema_ids
    ]
    task_rows = group_pair_rows_by_task(pair_rows, schema_ids)
    assignments = assign_tasks(
        task_rows=task_rows,
        schema_ids=schema_ids,
        epsilon_pp=epsilon_pp,
        high_confidence_margin_pp=high_confidence_margin_pp,
        medium_confidence_margin_pp=medium_confidence_margin_pp,
        require_full_coverage=require_full_coverage,
    )
    diagnostics = build_diagnostics(
        task_rows=task_rows,
        assignments=assignments,
        schema_ids=schema_ids,
        epsilon_pp=epsilon_pp,
        dominant_share_threshold=dominant_share_threshold,
        top3_tie_threshold_pp=top3_tie_threshold_pp,
        near_empty_threshold=near_empty_threshold,
        update_floor_fraction=update_floor_fraction,
        flat_column_range_pp=flat_column_range_pp,
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
            "round0_root": str(round0_root.resolve()),
            "global_pair_status_path": str(global_pair_status_path.resolve()),
            "prompt_bank_path": str(prompt_bank_path.resolve()),
            "epsilon_pp": epsilon_pp,
            "high_confidence_margin_pp": high_confidence_margin_pp,
            "medium_confidence_margin_pp": medium_confidence_margin_pp,
            "require_full_coverage": require_full_coverage,
            "dominant_share_threshold": dominant_share_threshold,
            "top3_tie_threshold_pp": top3_tie_threshold_pp,
            "near_empty_threshold": near_empty_threshold,
            "update_floor_fraction": update_floor_fraction,
            "flat_column_range_pp": flat_column_range_pp,
        },
        "schema_ids": schema_ids,
        "pair_rows": pair_rows,
        "score_matrix": score_matrix,
        "assignments": assignments,
        "diagnostics": diagnostics,
    }


def write_outer_loop_artifacts(*, payload: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    score_matrix = payload["score_matrix"]
    assignments = payload["assignments"]
    diagnostics = payload["diagnostics"]

    score_matrix_csv_path = output_dir / "score_matrix.csv"
    score_matrix_wide_csv_path = output_dir / "score_matrix_wide.csv"
    score_matrix_json_path = output_dir / "score_matrix.json"
    assignments_csv_path = output_dir / "assignments.csv"
    assignments_json_path = output_dir / "assignments.json"
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
            "second_best_category",
            "second_best_score",
            "margin_pp",
            "assignment_confidence",
            "tie_break_used",
            "tie_break_reason",
            "tie_candidate_schema_ids",
            "tie_candidate_count",
            "tie_candidate_score_range_pp",
            "observed_schema_count",
            "full_coverage",
            "missing_schema_ids",
            "infra_blocked_schema_ids",
            "runtime_blocked_schema_ids",
            "ambiguous_schema_ids",
            "top3_spread_pp",
            "assigned_score",
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
        "diagnostics_json": display_path(diagnostics_json_path),
        "bundle_json": display_path(bundle_json_path),
        "summary_md": display_path(summary_md_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round0-root", type=Path, default=DEFAULT_ROUND0_ROOT)
    parser.add_argument("--global-pair-status-path", type=Path, default=DEFAULT_GLOBAL_PAIR_STATUS_PATH)
    parser.add_argument("--prompt-bank-path", type=Path, default=DEFAULT_PROMPT_BANK_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--round-id", default="outer-loop-round0")
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_outer_loop_artifacts(
        round0_root=args.round0_root,
        global_pair_status_path=args.global_pair_status_path,
        prompt_bank_path=args.prompt_bank_path,
        round_id=str(args.round_id),
        epsilon_pp=float(args.epsilon_pp),
        high_confidence_margin_pp=float(args.high_confidence_margin_pp),
        medium_confidence_margin_pp=float(args.medium_confidence_margin_pp),
        require_full_coverage=not bool(args.allow_partial_assignment),
        dominant_share_threshold=float(args.dominant_share_threshold),
        top3_tie_threshold_pp=float(args.top3_tie_threshold_pp),
        near_empty_threshold=int(args.near_empty_threshold),
        update_floor_fraction=float(args.update_floor_fraction),
        flat_column_range_pp=float(args.flat_column_range_pp),
    )
    outputs = write_outer_loop_artifacts(payload=payload, output_dir=args.output_dir)
    print(json.dumps(outputs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Serve a local dashboard for the finalized first20 x 7 round0 results."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any


DEFAULT_CHECKPOINT_DIR = Path(
    "experiments/skillx-skillsbench-001/results/outer-loop-round0/"
    "sonnet45-task-list-first20-v0.1/reports/"
    "checkpoint-first20-round0-rate-limit-rerun-3batch-final-2026-04-29"
)
DEFAULT_CONTROL_PLANE_DIR = Path(
    "experiments/skillx-skillsbench-001/results/outer-loop-round0/"
    "sonnet45-task-list-first20-v0.1/reports/"
    "outer-loop-control-plane-first20-final-2026-04-29"
)

ROUND_FIELDS = (
    ("R0", "round_r0_score_pct"),
    ("R1", "round_r1_score_pct"),
    ("R2", "round_r2_score_pct"),
    ("R3", "round_r3_score_pct"),
)
DELTA_TARGETS = (
    ("vs_r0", "Best - R0", "delta_vs_r0_best_pp"),
    ("vs_c1", "Best - C1", "delta_vs_c1_pp"),
    ("vs_c0", "Best - C0", "delta_vs_c0_pp"),
)
SCHEMA_COLORS = {
    "analytic-pipeline": "#67e8f9",
    "artifact-generation": "#fbbf24",
    "engineering-composition": "#a7f3d0",
    "environment-control": "#fb7185",
    "methodology-guardrail": "#c084fc",
    "orchestration-delegation": "#38bdf8",
    "retrieval-heavy-synthesis": "#f97316",
}
TARGET_COLORS = {
    "vs_r0": "#67e8f9",
    "vs_c1": "#fbbf24",
    "vs_c0": "#86efac",
}
TRAINING_EVIDENCE_COLUMNS = (
    ("schema_id", "Schema"),
    ("task_name", "Task"),
    ("evidence_role", "Evidence Role"),
    ("evidence_reasons", "Evidence Reasons"),
    ("schema_score", "Assignment Score"),
    ("schema_reported_score", "Reported Score"),
    ("schema_rank_for_task", "Schema Rank"),
    ("schema_delta_vs_r0_post_best_pp", "Best dR0"),
    ("schema_trajectory_quality", "Trajectory Quality"),
    ("primary_assigned_category", "Primary Assignment"),
    ("task_best_schema", "Task Best Schema"),
    ("task_best_score", "Task Best Score"),
)
TRAINING_EVIDENCE_COLUMN_DEFINITIONS = {
    "schema_id": "The meta schema that will receive this task as training evidence in the next outer-loop rewrite.",
    "task_name": "The SkillsBench task that produced the evidence.",
    "evidence_role": "Why this schema-task row is included. Primary rows are the main assignment; support rows are extra high-signal matches; floor rows fill a schema that otherwise has too little evidence.",
    "evidence_reasons": "The specific routing signals behind the row, such as near-best score, high score, stable gain, or ideal 0-to-100 improvement.",
    "schema_score": "The trajectory-aware assignment score used for routing this task to schemas. It is not just the raw final score.",
    "schema_reported_score": "The raw selected/best score reported for this schema-task pair on a 0-100 scale.",
    "schema_rank_for_task": "This schema's rank among all schemas for the same task by assignment score. Lower is better.",
    "schema_delta_vs_r0_post_best_pp": "The best post-R0 improvement over R0 for this schema-task pair, measured in percentage points.",
    "schema_trajectory_quality": "A qualitative label for the R0-R3 curve, for example stable gain or ideal zero-to-full stable.",
    "primary_assigned_category": "The single primary schema selected for this task. It can differ from schema_id for multi-assignment or floor-fill rows.",
    "task_best_schema": "The highest-scoring schema for this task by the assignment score.",
    "task_best_score": "The best assignment score achieved by any schema for this task.",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _safe_read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return _read_json(path)
    except json.JSONDecodeError:
        return fallback


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _mean(values: list[float | None]) -> float | None:
    numeric = [value for value in values if value is not None]
    if not numeric:
        return None
    return round(sum(numeric) / len(numeric), 4)


def _median(values: list[float | None]) -> float | None:
    numeric = sorted(value for value in values if value is not None)
    if not numeric:
        return None
    midpoint = len(numeric) // 2
    if len(numeric) % 2:
        return round(numeric[midpoint], 4)
    return round((numeric[midpoint - 1] + numeric[midpoint]) / 2.0, 4)


def _fmt(value: Any, *, digits: int = 1) -> str:
    numeric = _as_float(value)
    if numeric is None:
        return "" if value is None else str(value)
    text = f"{numeric:.{digits}f}"
    return text.rstrip("0").rstrip(".")


def _escape(value: Any) -> str:
    return html.escape(str(value))


def _short_schema(schema_id: str) -> str:
    return {
        "analytic-pipeline": "analytic",
        "artifact-generation": "artifact",
        "engineering-composition": "engineering",
        "environment-control": "environment",
        "methodology-guardrail": "guardrail",
        "orchestration-delegation": "orchestration",
        "retrieval-heavy-synthesis": "retrieval",
    }.get(schema_id, schema_id)


def _delta_class(value: Any) -> str:
    numeric = _as_float(value)
    if numeric is None:
        return "num"
    if numeric > 0.5:
        return "num delta-pos"
    if numeric < -0.5:
        return "num delta-neg"
    return "num delta-zero"


def _heat_class(value: Any) -> str:
    numeric = _as_float(value)
    if numeric is None:
        return "heat-empty"
    if numeric >= 80:
        return "heat-5"
    if numeric >= 60:
        return "heat-4"
    if numeric >= 40:
        return "heat-3"
    if numeric >= 20:
        return "heat-2"
    return "heat-1"


def _round_scores(pair: dict[str, Any]) -> list[float | None]:
    return [_as_float(pair.get(field)) for _, field in ROUND_FIELDS]


def _round_score_dict(pair: dict[str, Any]) -> dict[str, float | None]:
    return {label: _as_float(pair.get(field)) for label, field in ROUND_FIELDS}


def _score_or_selected(pair: dict[str, Any]) -> float | None:
    score = _as_float(pair.get("selected_score_pct"))
    if score is not None:
        return score
    return _as_float(pair.get("post_r0_best_score_pct"))


def _count_delta(values: list[float | None]) -> dict[str, Any]:
    numeric = [value for value in values if value is not None]
    return {
        "count": len(numeric),
        "positive": sum(1 for value in numeric if value > 0.5),
        "flat": sum(1 for value in numeric if -0.5 <= value <= 0.5),
        "negative": sum(1 for value in numeric if value < -0.5),
        "mean": _mean(numeric),
        "median": _median(numeric),
        "min": round(min(numeric), 4) if numeric else None,
        "max": round(max(numeric), 4) if numeric else None,
    }


def _best_pair_key(row: dict[str, Any], schema_order: dict[str, int]) -> tuple[float, float, int, int]:
    score = _score_or_selected(row)
    delta = _as_float(row.get("delta_vs_r0_best_pp"))
    clean_bonus = 1 if row.get("selected_classification") == "clean_success" else 0
    schema_index = schema_order.get(str(row.get("schema_id") or ""), 10**6)
    return (
        score if score is not None else -10**9,
        delta if delta is not None else -10**9,
        clean_bonus,
        -schema_index,
    )


def _last_available_score(round_scores: dict[str, float | None]) -> tuple[str | None, float | None]:
    for label, _ in reversed(ROUND_FIELDS):
        score = round_scores.get(label)
        if score is not None:
            return label, score
    return None, None


def _build_best_task_rows(
    *,
    tasks: list[str],
    pairs_by_task: dict[str, list[dict[str, Any]]],
    schema_order: dict[str, int],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_name in tasks:
        pairs = pairs_by_task.get(task_name, [])
        scored_pairs = [(pair, _score_or_selected(pair)) for pair in pairs]
        numeric_scores = [score for _, score in scored_pairs if score is not None]
        if not numeric_scores:
            continue
        best_score = max(numeric_scores)
        tied_pairs = [
            pair
            for pair, score in scored_pairs
            if score is not None and abs(score - best_score) <= 1e-9
        ]
        best_pair = max(tied_pairs, key=lambda row: _best_pair_key(row, schema_order))
        round_scores = _round_score_dict(best_pair)
        r0_score = round_scores.get("R0")
        round_deltas = {
            label: (
                round(float(score) - float(r0_score), 4)
                if score is not None and r0_score is not None
                else None
            )
            for label, score in round_scores.items()
        }
        final_round, final_score = _last_available_score(round_scores)
        final_delta = (
            round(float(final_score) - float(r0_score), 4)
            if final_score is not None and r0_score is not None
            else None
        )
        rows.append(
            {
                "task_name": task_name,
                "schema_id": best_pair.get("schema_id"),
                "short_schema": _short_schema(str(best_pair.get("schema_id") or "")),
                "schema_color": SCHEMA_COLORS.get(str(best_pair.get("schema_id") or ""), "#94a3b8"),
                "pair_id": best_pair.get("pair_id"),
                "round_scores": round_scores,
                "round_deltas_vs_r0": round_deltas,
                "r0_score_pct": r0_score,
                "best_score_pct": _score_or_selected(best_pair),
                "best_round": best_pair.get("selected_round"),
                "best_delta_vs_r0_pp": best_pair.get("delta_vs_r0_best_pp"),
                "final_round": final_round,
                "final_score_pct": final_score,
                "final_delta_vs_r0_pp": final_delta,
                "tie_count": len(tied_pairs),
                "tie_schemas": [
                    str(pair.get("schema_id"))
                    for pair in sorted(tied_pairs, key=lambda row: str(row.get("schema_id") or ""))
                ],
                "trajectory_quality": best_pair.get("trajectory_quality"),
                "classification": best_pair.get("selected_classification"),
            }
        )
    return rows


def _schema_ids(
    schema_summary: list[dict[str, Any]],
    pair_rows: list[dict[str, Any]],
) -> list[str]:
    ordered = [
        str(row.get("schema_id"))
        for row in schema_summary
        if isinstance(row, dict) and isinstance(row.get("schema_id"), str)
    ]
    discovered = sorted(
        {
            str(row.get("schema_id"))
            for row in pair_rows
            if isinstance(row, dict) and isinstance(row.get("schema_id"), str)
        }
    )
    for schema_id in discovered:
        if schema_id not in ordered:
            ordered.append(schema_id)
    return ordered


def _task_names(
    task_summary: list[dict[str, Any]],
    pair_rows: list[dict[str, Any]],
) -> list[str]:
    ordered = [
        str(row.get("task_name"))
        for row in task_summary
        if isinstance(row, dict) and isinstance(row.get("task_name"), str)
    ]
    discovered = sorted(
        {
            str(row.get("task_name"))
            for row in pair_rows
            if isinstance(row, dict) and isinstance(row.get("task_name"), str)
        }
    )
    for task_name in discovered:
        if task_name not in ordered:
            ordered.append(task_name)
    return ordered


def build_dashboard_payload(checkpoint_dir: Path) -> dict[str, Any]:
    checkpoint_dir = checkpoint_dir.resolve()
    checkpoint_summary = _safe_read_json(checkpoint_dir / "checkpoint_summary.json", {})
    pair_rows = _safe_read_json(checkpoint_dir / "final_pair_results.json", [])
    task_summary = _safe_read_json(checkpoint_dir / "task_summary.json", [])
    schema_summary = _safe_read_json(checkpoint_dir / "schema_summary.json", [])

    if not isinstance(checkpoint_summary, dict):
        checkpoint_summary = {}
    if not isinstance(pair_rows, list):
        pair_rows = []
    if not isinstance(task_summary, list):
        task_summary = []
    if not isinstance(schema_summary, list):
        schema_summary = []

    pair_rows = [row for row in pair_rows if isinstance(row, dict)]
    task_summary = [row for row in task_summary if isinstance(row, dict)]
    schema_summary = [row for row in schema_summary if isinstance(row, dict)]
    schema_summary_by_id = {
        str(row.get("schema_id")): row
        for row in schema_summary
        if isinstance(row.get("schema_id"), str)
    }
    task_summary_by_name = {
        str(row.get("task_name")): row
        for row in task_summary
        if isinstance(row.get("task_name"), str)
    }
    schemas = _schema_ids(schema_summary, pair_rows)
    tasks = _task_names(task_summary, pair_rows)

    pairs_by_schema: dict[str, list[dict[str, Any]]] = defaultdict(list)
    pairs_by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    pairs_by_task_schema: dict[tuple[str, str], dict[str, Any]] = {}
    schema_order = {schema_id: index for index, schema_id in enumerate(schemas)}
    for pair in pair_rows:
        task_name = str(pair.get("task_name") or "")
        schema_id = str(pair.get("schema_id") or "")
        if not task_name or not schema_id:
            continue
        pairs_by_schema[schema_id].append(pair)
        pairs_by_task[task_name].append(pair)
        pairs_by_task_schema[(task_name, schema_id)] = pair

    best_task_rows = _build_best_task_rows(
        tasks=tasks,
        pairs_by_task=pairs_by_task,
        schema_order=schema_order,
    )

    schema_cards: list[dict[str, Any]] = []
    for schema_id in schemas:
        rows = pairs_by_schema.get(schema_id, [])
        summary_row = schema_summary_by_id.get(schema_id, {})
        trajectory = {
            label: _mean([_as_float(row.get(field)) for row in rows])
            for label, field in ROUND_FIELDS
        }
        deltas = {
            target_id: _mean([_as_float(row.get(field)) for row in rows])
            for target_id, _, field in DELTA_TARGETS
        }
        quality_counts = Counter(str(row.get("trajectory_quality") or "unknown") for row in rows)
        class_counts = Counter(str(row.get("selected_classification") or "unknown") for row in rows)
        schema_cards.append(
            {
                "schema_id": schema_id,
                "short_label": _short_schema(schema_id),
                "color": SCHEMA_COLORS.get(schema_id, "#94a3b8"),
                "pair_count": len(rows),
                "succeeded_pairs": summary_row.get("succeeded_pairs"),
                "mean_selected_score_pct": _mean([_score_or_selected(row) for row in rows]),
                "mean_post_best_score_pct": _mean([_as_float(row.get("post_r0_best_score_pct")) for row in rows]),
                "mean_r0_score_pct": trajectory.get("R0"),
                "trajectory": trajectory,
                "deltas": deltas,
                "classification_counts": dict(class_counts),
                "trajectory_quality_counts": dict(quality_counts),
                "clean_success": summary_row.get("clean_success"),
                "scientific_failure": summary_row.get("scientific_failure"),
                "runtime_failure": summary_row.get("runtime_failure"),
            }
        )

    task_cards: list[dict[str, Any]] = []
    for task_name in tasks:
        rows = pairs_by_task.get(task_name, [])
        summary_row = task_summary_by_name.get(task_name, {})
        scored = [
            (score, row)
            for row in rows
            for score in [_score_or_selected(row)]
            if score is not None
        ]
        best_score = _as_float(summary_row.get("best_score_pct"))
        if best_score is None:
            best_score = max((score for score, _ in scored), default=None)
        best_schemas = summary_row.get("best_schemas")
        if not isinstance(best_schemas, list):
            best_schemas = [
                str(row.get("schema_id"))
                for score, row in scored
                if best_score is not None and abs(score - best_score) <= 1e-9
            ]
        task_cards.append(
            {
                "task_name": task_name,
                "pair_count": len(rows),
                "c0_pct": summary_row.get("c0_pct"),
                "c1_pct": summary_row.get("c1_pct"),
                "best_score_pct": best_score,
                "best_schemas": [str(item) for item in best_schemas],
                "delta_vs_c0_pp": summary_row.get("delta_vs_c0_pp"),
                "delta_vs_c1_pp": summary_row.get("delta_vs_c1_pp"),
                "mean_delta_vs_r0_pp": _mean([_as_float(row.get("delta_vs_r0_best_pp")) for row in rows]),
                "best_delta_vs_r0_pp": max(
                    [
                        value
                        for value in [_as_float(row.get("delta_vs_r0_best_pp")) for row in rows]
                        if value is not None
                    ],
                    default=None,
                ),
                "clean_success_pairs": sum(1 for row in rows if row.get("selected_classification") == "clean_success"),
                "scientific_failure_pairs": sum(1 for row in rows if row.get("selected_classification") == "scientific_failure"),
            }
        )

    delta_overview = {
        target_id: _count_delta([_as_float(row.get(field)) for row in pair_rows])
        for target_id, _, field in DELTA_TARGETS
    }
    trajectory_quality_counts = Counter(str(row.get("trajectory_quality") or "unknown") for row in pair_rows)
    classification_counts = Counter(str(row.get("selected_classification") or "unknown") for row in pair_rows)
    selected_scores = [_score_or_selected(row) for row in pair_rows]
    r0_scores = [_as_float(row.get("round_r0_score_pct")) for row in pair_rows]
    best_task_delta_overview = _count_delta(
        [_as_float(row.get("best_delta_vs_r0_pp")) for row in best_task_rows]
    )
    best_task_r0_scores = [_as_float(row.get("r0_score_pct")) for row in best_task_rows]
    best_task_scores = [_as_float(row.get("best_score_pct")) for row in best_task_rows]

    matrix_rows: list[dict[str, Any]] = []
    for task_name in tasks:
        cells = []
        for schema_id in schemas:
            pair = pairs_by_task_schema.get((task_name, schema_id))
            cells.append(
                {
                    "schema_id": schema_id,
                    "pair_id": pair.get("pair_id") if isinstance(pair, dict) else None,
                    "score_pct": _score_or_selected(pair) if isinstance(pair, dict) else None,
                    "round_scores": _round_scores(pair) if isinstance(pair, dict) else [],
                    "delta_vs_r0_pp": pair.get("delta_vs_r0_best_pp") if isinstance(pair, dict) else None,
                    "delta_vs_c1_pp": pair.get("delta_vs_c1_pp") if isinstance(pair, dict) else None,
                    "delta_vs_c0_pp": pair.get("delta_vs_c0_pp") if isinstance(pair, dict) else None,
                    "selected_round": pair.get("selected_round") if isinstance(pair, dict) else None,
                    "classification": pair.get("selected_classification") if isinstance(pair, dict) else None,
                    "trajectory_quality": pair.get("trajectory_quality") if isinstance(pair, dict) else None,
                }
            )
        matrix_rows.append({"task_name": task_name, "cells": cells})

    top_delta_r0 = sorted(
        pair_rows,
        key=lambda row: _as_float(row.get("delta_vs_r0_best_pp")) if _as_float(row.get("delta_vs_r0_best_pp")) is not None else -10**9,
        reverse=True,
    )[:12]
    bottom_delta_c1 = sorted(
        pair_rows,
        key=lambda row: _as_float(row.get("delta_vs_c1_pp")) if _as_float(row.get("delta_vs_c1_pp")) is not None else 10**9,
    )[:12]

    return {
        "checkpoint_dir": str(checkpoint_dir),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checkpoint_summary": checkpoint_summary,
        "schemas": schemas,
        "tasks": tasks,
        "pair_rows": pair_rows,
        "schema_cards": schema_cards,
        "task_cards": task_cards,
        "best_task_rows": best_task_rows,
        "best_task_delta_overview": best_task_delta_overview,
        "matrix_rows": matrix_rows,
        "delta_overview": delta_overview,
        "classification_counts": dict(classification_counts),
        "trajectory_quality_counts": dict(trajectory_quality_counts),
        "top_delta_r0_pairs": top_delta_r0,
        "bottom_delta_c1_pairs": bottom_delta_c1,
        "summary_metrics": {
            "task_count": len(tasks),
            "schema_count": len(schemas),
            "pair_count": len(pair_rows),
            "mean_selected_score_pct": _mean(selected_scores),
            "mean_r0_score_pct": _mean(r0_scores),
            "mean_delta_vs_r0_pp": delta_overview["vs_r0"]["mean"],
            "mean_delta_vs_c1_pp": delta_overview["vs_c1"]["mean"],
            "mean_delta_vs_c0_pp": delta_overview["vs_c0"]["mean"],
            "clean_success_count": classification_counts.get("clean_success", 0),
            "scientific_failure_count": classification_counts.get("scientific_failure", 0),
            "runtime_failure_count": classification_counts.get("runtime_failure", 0),
            "best_task_mean_r0_score_pct": _mean(best_task_r0_scores),
            "best_task_mean_best_score_pct": _mean(best_task_scores),
            "best_task_mean_delta_vs_r0_pp": best_task_delta_overview["mean"],
            "best_task_improved_count": best_task_delta_overview["positive"],
            "best_task_flat_count": best_task_delta_overview["flat"],
            "best_task_regressed_count": best_task_delta_overview["negative"],
        },
    }


def _coerce_training_evidence_row(row: dict[str, Any]) -> dict[str, Any]:
    coerced = {field: row.get(field) for field, _ in TRAINING_EVIDENCE_COLUMNS}
    for field in (
        "schema_score",
        "schema_reported_score",
        "schema_delta_vs_r0_post_best_pp",
        "task_best_score",
    ):
        value = coerced.get(field)
        if value in ("", None):
            coerced[field] = None
            continue
        if isinstance(value, bool):
            coerced[field] = None
            continue
        if isinstance(value, (int, float)):
            coerced[field] = float(value)
            continue
        try:
            coerced[field] = float(str(value))
        except ValueError:
            coerced[field] = None
    rank = coerced.get("schema_rank_for_task")
    if rank in ("", None) or isinstance(rank, bool):
        coerced["schema_rank_for_task"] = None
    else:
        try:
            coerced["schema_rank_for_task"] = int(float(str(rank)))
        except ValueError:
            coerced["schema_rank_for_task"] = None
    for field in (
        "schema_id",
        "task_name",
        "evidence_role",
        "evidence_reasons",
        "schema_trajectory_quality",
        "primary_assigned_category",
        "task_best_schema",
    ):
        value = coerced.get(field)
        coerced[field] = "" if value is None else str(value)
    return coerced


def _load_training_evidence_rows(control_plane_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    json_path = control_plane_dir / "schema_training_assignments.json"
    csv_path = control_plane_dir / "schema_training_assignments.csv"
    metadata: dict[str, Any] = {
        "source_path": str(json_path if json_path.exists() else csv_path),
        "source_format": "missing",
        "generated_at": None,
        "config": {},
    }
    raw_rows: list[Any] = []
    if json_path.exists():
        data = _safe_read_json(json_path, {})
        metadata["source_format"] = "json"
        if isinstance(data, dict):
            raw_rows = data.get("schema_training_assignments") or []
            metadata["generated_at"] = data.get("generated_at")
            if isinstance(data.get("config"), dict):
                metadata["config"] = data.get("config")
        elif isinstance(data, list):
            raw_rows = data
    elif csv_path.exists():
        metadata["source_format"] = "csv"
        with csv_path.open(newline="") as handle:
            raw_rows = list(csv.DictReader(handle))

    rows = [
        _coerce_training_evidence_row(row)
        for row in raw_rows
        if isinstance(row, dict)
    ]
    role_order = {
        "primary_assignment": 0,
        "stable_gain_support": 1,
        "high_score_support": 2,
        "floor_top_score": 3,
    }
    rows.sort(
        key=lambda row: (
            str(row.get("schema_id") or ""),
            role_order.get(str(row.get("evidence_role") or ""), 99),
            row.get("schema_rank_for_task") if row.get("schema_rank_for_task") is not None else 10**6,
            str(row.get("task_name") or ""),
        )
    )
    return rows, metadata


def build_training_evidence_payload(control_plane_dir: Path) -> dict[str, Any]:
    control_plane_dir = control_plane_dir.resolve()
    rows, metadata = _load_training_evidence_rows(control_plane_dir)
    role_counts = Counter(str(row.get("evidence_role") or "unknown") for row in rows)
    schema_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        schema_counts[str(row.get("schema_id") or "")][str(row.get("evidence_role") or "unknown")] += 1

    schema_summary = []
    for schema_id in sorted(schema_id for schema_id in schema_counts if schema_id):
        counts = schema_counts[schema_id]
        schema_summary.append(
            {
                "schema_id": schema_id,
                "evidence_count": sum(counts.values()),
                "primary_assignment": counts.get("primary_assignment", 0),
                "stable_gain_support": counts.get("stable_gain_support", 0),
                "high_score_support": counts.get("high_score_support", 0),
                "floor_top_score": counts.get("floor_top_score", 0),
                "other": sum(
                    count
                    for role, count in counts.items()
                    if role
                    not in {
                        "primary_assignment",
                        "stable_gain_support",
                        "high_score_support",
                        "floor_top_score",
                    }
                ),
            }
        )

    return {
        "control_plane_dir": str(control_plane_dir),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_path": metadata.get("source_path"),
        "source_format": metadata.get("source_format"),
        "source_generated_at": metadata.get("generated_at"),
        "config": metadata.get("config") if isinstance(metadata.get("config"), dict) else {},
        "columns": [
            {
                "key": key,
                "label": label,
                "description": TRAINING_EVIDENCE_COLUMN_DEFINITIONS[key],
            }
            for key, label in TRAINING_EVIDENCE_COLUMNS
        ],
        "rows": rows,
        "schema_summary": schema_summary,
        "role_counts": dict(sorted(role_counts.items())),
        "summary_metrics": {
            "row_count": len(rows),
            "schema_count": len({row.get("schema_id") for row in rows if row.get("schema_id")}),
            "task_count": len({row.get("task_name") for row in rows if row.get("task_name")}),
            "primary_assignment_count": role_counts.get("primary_assignment", 0),
            "support_count": sum(
                count
                for role, count in role_counts.items()
                if role not in {"primary_assignment", "floor_top_score"}
            ),
            "floor_count": role_counts.get("floor_top_score", 0),
        },
    }


def _metric_card(label: str, value: Any, suffix: str = "", tone: str = "") -> str:
    tone_class = f" metric-{tone}" if tone else ""
    return (
        f'<div class="metric-card{tone_class}">'
        f'<div class="metric-label">{_escape(label)}</div>'
        f'<div class="metric-value">{_escape(value)}{_escape(suffix)}</div>'
        "</div>"
    )


def _line_chart_svg(schema_cards: list[dict[str, Any]]) -> str:
    width = 920
    height = 330
    left = 54
    right = 26
    top = 24
    bottom = 56
    plot_w = width - left - right
    plot_h = height - top - bottom
    x_positions = [left + (plot_w * index / 3.0) for index in range(4)]

    def y_for(value: float | None) -> float:
        numeric = 0.0 if value is None else max(0.0, min(100.0, value))
        return top + (100.0 - numeric) / 100.0 * plot_h

    grid = []
    for tick in (0, 25, 50, 75, 100):
        y = y_for(float(tick))
        grid.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{width-right}" y2="{y:.2f}" class="chart-grid" />'
            f'<text x="{left-12}" y="{y+4:.2f}" class="chart-axis" text-anchor="end">{tick}</text>'
        )
    x_labels = []
    for index, label in enumerate(("R0", "R1", "R2", "R3")):
        x = x_positions[index]
        x_labels.append(
            f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{height-bottom}" class="chart-grid faint" />'
            f'<text x="{x:.2f}" y="{height-24}" class="chart-axis" text-anchor="middle">{label}</text>'
        )

    lines = []
    dots = []
    for card in schema_cards:
        trajectory = card.get("trajectory") if isinstance(card.get("trajectory"), dict) else {}
        values = [_as_float(trajectory.get(label)) for label, _ in ROUND_FIELDS]
        points = [
            f"{x_positions[index]:.2f},{y_for(values[index]):.2f}"
            for index in range(4)
            if values[index] is not None
        ]
        if len(points) < 2:
            continue
        color = str(card.get("color") or "#94a3b8")
        label = str(card.get("schema_id") or "")
        lines.append(
            f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" '
            f'stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
            f"<title>{_escape(label)}</title></polyline>"
        )
        for index, value in enumerate(values):
            if value is None:
                continue
            dots.append(
                f'<circle cx="{x_positions[index]:.2f}" cy="{y_for(value):.2f}" r="4.5" '
                f'fill="{color}" stroke="#050505" stroke-width="1.5">'
                f"<title>{_escape(label)} {ROUND_FIELDS[index][0]}: {_escape(_fmt(value))}</title></circle>"
            )

    return (
        f'<svg class="trajectory-svg" viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Optimization trajectory by schema">'
        f'{"".join(grid)}{"".join(x_labels)}'
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" class="chart-axis-line" />'
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" class="chart-axis-line" />'
        f'{"".join(lines)}{"".join(dots)}'
        "</svg>"
    )


def _delta_bars_svg(schema_cards: list[dict[str, Any]]) -> str:
    rows: list[tuple[str, str, float | None, str]] = []
    for card in schema_cards:
        deltas = card.get("deltas") if isinstance(card.get("deltas"), dict) else {}
        label = str(card.get("short_label") or card.get("schema_id") or "")
        for target_id, target_label, _ in DELTA_TARGETS:
            rows.append((label, target_label, _as_float(deltas.get(target_id)), target_id))

    numeric_values = [value for _, _, value, _ in rows if value is not None]
    low = min(-10.0, min(numeric_values, default=-10.0))
    high = max(10.0, max(numeric_values, default=10.0))
    padding = max(5.0, (high - low) * 0.08)
    low -= padding
    high += padding
    width = 920
    row_h = 24
    top = 24
    left = 168
    right = 58
    height = top + row_h * len(rows) + 30
    plot_w = width - left - right

    def x_for(value: float) -> float:
        return left + (value - low) / (high - low) * plot_w

    zero_x = x_for(0.0)
    row_items = [
        f'<line x1="{zero_x:.2f}" y1="12" x2="{zero_x:.2f}" y2="{height-22}" class="zero-line" />'
    ]
    for index, (schema_label, target_label, value, target_id) in enumerate(rows):
        y = top + index * row_h
        y_mid = y + row_h / 2.0
        color = TARGET_COLORS.get(target_id, "#94a3b8")
        row_items.append(
            f'<text x="12" y="{y_mid+4:.2f}" class="bar-label">{_escape(schema_label)} / {_escape(target_label)}</text>'
        )
        if value is None:
            continue
        x = x_for(value)
        bar_x = min(x, zero_x)
        bar_w = abs(x - zero_x)
        row_items.append(
            f'<rect x="{bar_x:.2f}" y="{y+4:.2f}" width="{bar_w:.2f}" height="{row_h-8}" '
            f'rx="3" fill="{color}" opacity="0.82"><title>{_escape(schema_label)} {_escape(target_label)}: {_escape(_fmt(value))}</title></rect>'
            f'<text x="{x + (6 if value >= 0 else -6):.2f}" y="{y_mid+4:.2f}" '
            f'class="bar-value" text-anchor="{"start" if value >= 0 else "end"}">{_escape(_fmt(value))}</text>'
        )
    return (
        f'<svg class="delta-svg" viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Mean delta bars by schema">'
        f'<text x="{left}" y="14" class="chart-axis">mean percentage point delta</text>'
        f'{"".join(row_items)}</svg>'
    )


def _sparkline_svg(scores: list[float | None], color: str) -> str:
    values = [value for value in scores if value is not None]
    if len(values) < 2:
        return '<svg class="spark" viewBox="0 0 96 28" aria-hidden="true"></svg>'
    width = 96
    height = 28
    pad = 4
    plot_w = width - 2 * pad
    plot_h = height - 2 * pad

    def y_for(value: float | None) -> float:
        numeric = 0.0 if value is None else max(0.0, min(100.0, value))
        return pad + (100.0 - numeric) / 100.0 * plot_h

    points = [
        f"{pad + index * plot_w / 3.0:.2f},{y_for(score):.2f}"
        for index, score in enumerate(scores)
        if score is not None
    ]
    return (
        '<svg class="spark" viewBox="0 0 96 28" aria-hidden="true">'
        '<line x1="4" y1="24" x2="92" y2="24" class="spark-base" />'
        f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" '
        'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />'
        "</svg>"
    )


def _focused_sparkline_svg(scores: list[float | None], color: str) -> str:
    if len([score for score in scores if score is not None]) < 2:
        return '<svg class="focus-spark" viewBox="0 0 156 42" aria-hidden="true"></svg>'
    width = 156
    height = 42
    pad_x = 8
    pad_y = 6
    plot_w = width - 2 * pad_x
    plot_h = height - 2 * pad_y

    def y_for(value: float | None) -> float:
        numeric = 0.0 if value is None else max(0.0, min(100.0, value))
        return pad_y + (100.0 - numeric) / 100.0 * plot_h

    points = [
        f"{pad_x + index * plot_w / 3.0:.2f},{y_for(score):.2f}"
        for index, score in enumerate(scores)
        if score is not None
    ]
    dots = "".join(
        f'<circle cx="{pad_x + index * plot_w / 3.0:.2f}" cy="{y_for(score):.2f}" r="3.1" fill="{color}" />'
        for index, score in enumerate(scores)
        if score is not None
    )
    return (
        '<svg class="focus-spark" viewBox="0 0 156 42" role="img" aria-label="R0 to R3 growth curve">'
        '<line x1="8" y1="36" x2="148" y2="36" class="spark-base" />'
        '<line x1="8" y1="6" x2="148" y2="6" class="spark-ceiling" />'
        f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" '
        'stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
        f"{dots}</svg>"
    )


def _score_delta_cell(score: Any, delta: Any) -> str:
    return (
        f'<td class="score-delta {_delta_class(delta)}">'
        f'<b>{_escape(_fmt(score))}</b>'
        f'<em>{_escape(_fmt(delta))}</em>'
        "</td>"
    )


def _render_best_task_rows(best_task_rows: list[dict[str, Any]]) -> str:
    rows = []
    for row in sorted(best_task_rows, key=lambda item: str(item.get("task_name") or "")):
        round_scores = row.get("round_scores") if isinstance(row.get("round_scores"), dict) else {}
        round_deltas = (
            row.get("round_deltas_vs_r0")
            if isinstance(row.get("round_deltas_vs_r0"), dict)
            else {}
        )
        schema_color = str(row.get("schema_color") or "#94a3b8")
        tie_count = int(row.get("tie_count") or 0)
        tie_note = f'<span class="tie-note">{tie_count} tied</span>' if tie_count > 1 else ""
        rows.append(
            "<tr>"
            f'<td class="task-name">{_escape(row.get("task_name"))}</td>'
            '<td class="schema-choice">'
            f'<span class="schema-chip" style="--schema-color:{_escape(schema_color)}">{_escape(row.get("short_schema"))}</span>'
            f"{tie_note}</td>"
            f'<td class="num score-strong">{_escape(_fmt(row.get("r0_score_pct")))}</td>'
            f'{_score_delta_cell(round_scores.get("R1"), round_deltas.get("R1"))}'
            f'{_score_delta_cell(round_scores.get("R2"), round_deltas.get("R2"))}'
            f'{_score_delta_cell(round_scores.get("R3"), round_deltas.get("R3"))}'
            f'<td class="num">{_escape(row.get("best_round") or "")}</td>'
            f'<td class="num score-strong">{_escape(_fmt(row.get("best_score_pct")))}</td>'
            f'<td class="{_delta_class(row.get("best_delta_vs_r0_pp"))}">{_escape(_fmt(row.get("best_delta_vs_r0_pp")))}</td>'
            f'<td class="{_delta_class(row.get("final_delta_vs_r0_pp"))}">{_escape(_fmt(row.get("final_delta_vs_r0_pp")))}</td>'
            f'<td>{_focused_sparkline_svg([round_scores.get(label) for label, _ in ROUND_FIELDS], schema_color)}</td>'
            "</tr>"
        )
    return "\n".join(rows)


def _render_schema_legend(schema_cards: list[dict[str, Any]]) -> str:
    items = []
    for card in schema_cards:
        color = str(card.get("color") or "#94a3b8")
        label = str(card.get("schema_id") or "")
        selected = _fmt(card.get("mean_selected_score_pct"))
        delta = _fmt((card.get("deltas") or {}).get("vs_r0") if isinstance(card.get("deltas"), dict) else None)
        items.append(
            '<li>'
            f'<span class="legend-dot" style="background:{_escape(color)}"></span>'
            f'<span>{_escape(label)}</span>'
            f'<b>{_escape(selected)}</b>'
            f'<em>+{_escape(delta)} vs R0</em>'
            '</li>'
        )
    return "<ul class=\"legend-list\">" + "".join(items) + "</ul>"


def _render_delta_scorecards(payload: dict[str, Any]) -> str:
    cards = []
    for target_id, label, _ in DELTA_TARGETS:
        stats = payload.get("delta_overview", {}).get(target_id, {})
        cards.append(
            '<div class="delta-card">'
            f'<div class="delta-title">{_escape(label)}</div>'
            f'<div class="delta-mean">{_escape(_fmt(stats.get("mean")))} pp</div>'
            '<div class="delta-splits">'
            f'<span class="pos">{_escape(stats.get("positive", 0))} positive</span>'
            f'<span>{_escape(stats.get("flat", 0))} flat</span>'
            f'<span class="neg">{_escape(stats.get("negative", 0))} negative</span>'
            '</div>'
            f'<div class="delta-range">median {_escape(_fmt(stats.get("median")))} / range {_escape(_fmt(stats.get("min")))} to {_escape(_fmt(stats.get("max")))}</div>'
            "</div>"
        )
    return "".join(cards)


def _render_task_rows(task_cards: list[dict[str, Any]]) -> str:
    rows = []
    for task in sorted(
        task_cards,
        key=lambda item: (
            -(_as_float(item.get("delta_vs_c1_pp")) or -10**9),
            str(item.get("task_name")),
        ),
    ):
        best_schemas = ", ".join(_short_schema(str(item)) for item in task.get("best_schemas", [])[:7])
        rows.append(
            "<tr>"
            f'<td class="task-name">{_escape(task.get("task_name"))}</td>'
            f'<td class="num">{_escape(_fmt(task.get("c0_pct")))}</td>'
            f'<td class="num">{_escape(_fmt(task.get("c1_pct")))}</td>'
            f'<td class="num score-strong">{_escape(_fmt(task.get("best_score_pct")))}</td>'
            f'<td class="{_delta_class(task.get("best_delta_vs_r0_pp"))}">{_escape(_fmt(task.get("best_delta_vs_r0_pp")))}</td>'
            f'<td class="{_delta_class(task.get("delta_vs_c1_pp"))}">{_escape(_fmt(task.get("delta_vs_c1_pp")))}</td>'
            f'<td class="{_delta_class(task.get("delta_vs_c0_pp"))}">{_escape(_fmt(task.get("delta_vs_c0_pp")))}</td>'
            f'<td>{_escape(best_schemas)}</td>'
            f'<td class="num">{_escape(task.get("clean_success_pairs"))}/{_escape(task.get("pair_count"))}</td>'
            "</tr>"
        )
    return "\n".join(rows)


def _render_matrix(payload: dict[str, Any]) -> str:
    schema_cards_by_id = {
        str(card.get("schema_id")): card for card in payload.get("schema_cards", [])
    }
    schema_headers = "".join(
        f'<th>{_escape(_short_schema(schema_id))}</th>' for schema_id in payload.get("schemas", [])
    )
    rows = []
    for matrix_row in payload.get("matrix_rows", []):
        cells = []
        for cell in matrix_row.get("cells", []):
            schema_id = str(cell.get("schema_id") or "")
            color = str(schema_cards_by_id.get(schema_id, {}).get("color") or "#94a3b8")
            score = cell.get("score_pct")
            delta = cell.get("delta_vs_r0_pp")
            cls = _heat_class(score)
            cells.append(
                f'<td class="matrix-cell {cls}">'
                f'<div class="cell-score">{_escape(_fmt(score))}</div>'
                f'<div class="cell-meta">dR0 {_escape(_fmt(delta))} / {_escape(cell.get("selected_round") or "")}</div>'
                f'{_sparkline_svg(cell.get("round_scores") or [], color)}'
                "</td>"
            )
        rows.append(
            "<tr>"
            f'<th class="matrix-task">{_escape(matrix_row.get("task_name"))}</th>'
            f'{"".join(cells)}'
            "</tr>"
        )
    return (
        '<div class="matrix-wrap"><table class="matrix-table">'
        f'<thead><tr><th>Task</th>{schema_headers}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody>'
        "</table></div>"
    )


def _render_pair_table(payload: dict[str, Any]) -> str:
    rows = []
    ordered_pairs = sorted(
        payload.get("pair_rows", []),
        key=lambda row: (
            str(row.get("task_name") or ""),
            str(row.get("schema_id") or ""),
        ),
    )
    for row in ordered_pairs:
        rows.append(
            "<tr>"
            f'<td class="task-name">{_escape(row.get("task_name"))}</td>'
            f'<td class="schema-name">{_escape(_short_schema(str(row.get("schema_id") or "")))}</td>'
            f'<td class="num">{_escape(_fmt(row.get("round_r0_score_pct")))}</td>'
            f'<td class="num">{_escape(_fmt(row.get("round_r1_score_pct")))}</td>'
            f'<td class="num">{_escape(_fmt(row.get("round_r2_score_pct")))}</td>'
            f'<td class="num">{_escape(_fmt(row.get("round_r3_score_pct")))}</td>'
            f'<td class="num score-strong">{_escape(_fmt(row.get("selected_score_pct")))}</td>'
            f'<td class="{_delta_class(row.get("delta_vs_r0_best_pp"))}">{_escape(_fmt(row.get("delta_vs_r0_best_pp")))}</td>'
            f'<td class="{_delta_class(row.get("delta_vs_c1_pp"))}">{_escape(_fmt(row.get("delta_vs_c1_pp")))}</td>'
            f'<td class="{_delta_class(row.get("delta_vs_c0_pp"))}">{_escape(_fmt(row.get("delta_vs_c0_pp")))}</td>'
            f'<td>{_escape(row.get("trajectory_quality") or "")}</td>'
            f'<td>{_escape(row.get("selected_classification") or "")}</td>'
            "</tr>"
        )
    return "\n".join(rows)


def _role_class(role: Any) -> str:
    role_text = str(role or "")
    if role_text == "primary_assignment":
        return "role-primary"
    if role_text == "floor_top_score":
        return "role-floor"
    if role_text.endswith("_support") or "support" in role_text:
        return "role-support"
    return "role-other"


def _render_training_schema_summary(schema_summary: list[dict[str, Any]]) -> str:
    rows = []
    for row in schema_summary:
        rows.append(
            "<tr>"
            f'<td class="schema-name">{_escape(row.get("schema_id"))}</td>'
            f'<td class="num score-strong">{_escape(row.get("evidence_count"))}</td>'
            f'<td class="num">{_escape(row.get("primary_assignment"))}</td>'
            f'<td class="num">{_escape(row.get("stable_gain_support"))}</td>'
            f'<td class="num">{_escape(row.get("high_score_support"))}</td>'
            f'<td class="num">{_escape(row.get("floor_top_score"))}</td>'
            f'<td class="num">{_escape(row.get("other"))}</td>'
            "</tr>"
        )
    return "\n".join(rows)


def _render_training_column_definitions(columns: list[dict[str, Any]]) -> str:
    rows = []
    for column in columns:
        rows.append(
            "<tr>"
            f'<td><code>{_escape(column.get("key"))}</code></td>'
            f'<td>{_escape(column.get("label"))}</td>'
            f'<td>{_escape(column.get("description"))}</td>'
            "</tr>"
        )
    return "\n".join(rows)


def _render_training_evidence_rows(rows: list[dict[str, Any]]) -> str:
    rendered_rows = []
    for row in rows:
        role = row.get("evidence_role")
        rendered_rows.append(
            "<tr>"
            f'<td class="schema-name">{_escape(row.get("schema_id"))}</td>'
            f'<td class="task-name">{_escape(row.get("task_name"))}</td>'
            f'<td><span class="role-chip {_role_class(role)}">{_escape(role)}</span></td>'
            f'<td class="reasons">{_escape(row.get("evidence_reasons") or "")}</td>'
            f'<td class="num score-strong">{_escape(_fmt(row.get("schema_score"), digits=4))}</td>'
            f'<td class="num">{_escape(_fmt(row.get("schema_reported_score")))}</td>'
            f'<td class="num">{_escape(row.get("schema_rank_for_task") or "")}</td>'
            f'<td class="{_delta_class(row.get("schema_delta_vs_r0_post_best_pp"))}">{_escape(_fmt(row.get("schema_delta_vs_r0_post_best_pp")))}</td>'
            f'<td>{_escape(row.get("schema_trajectory_quality") or "")}</td>'
            f'<td>{_escape(row.get("primary_assigned_category") or "")}</td>'
            f'<td>{_escape(row.get("task_best_schema") or "")}</td>'
            f'<td class="num">{_escape(_fmt(row.get("task_best_score"), digits=4))}</td>'
            "</tr>"
        )
    return "\n".join(rendered_rows)


def render_training_evidence_html(payload: dict[str, Any]) -> str:
    summary = payload.get("summary_metrics", {})
    config = payload.get("config") if isinstance(payload.get("config"), dict) else {}
    source_generated_at = payload.get("source_generated_at") or payload.get("generated_at")
    threshold_parts = []
    for key in (
        "score_threshold",
        "near_best_margin",
        "min_schema_training_tasks",
        "schema_floor_fraction",
    ):
        if key in config:
            threshold_parts.append(f"{key}={config.get(key)}")
    threshold_text = ", ".join(threshold_parts) if threshold_parts else "thresholds recorded in control-plane config"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>SkillX Schema Training Evidence</title>
  <style>
    :root {{
      --bg: #050505;
      --panel: #101112;
      --panel-alt: #17191b;
      --panel-soft: #1d2023;
      --ink: #f7f3ea;
      --ink-soft: #d7d0c0;
      --muted: #938f86;
      --border: #303337;
      --border-strong: #44484f;
      --accent: #67e8f9;
      --pos: #86efac;
      --pos-bg: rgba(134, 239, 172, 0.14);
      --neg: #fb7185;
      --neg-bg: rgba(251, 113, 133, 0.14);
      --warn: #fbbf24;
      --warn-bg: rgba(251, 191, 36, 0.13);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(180deg, rgba(255,255,255,0.022) 1px, transparent 1px),
        var(--bg);
      background-size: 28px 28px;
      color: var(--ink);
      font-family: "Avenir Next", "Helvetica Neue", Helvetica, sans-serif;
      font-size: 14px;
      line-height: 1.45;
      color-scheme: dark;
    }}
    main {{
      width: min(1720px, calc(100vw - 36px));
      margin: 0 auto;
      padding: 26px 0 52px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 20px;
      align-items: start;
      margin-bottom: 18px;
    }}
    .eyebrow {{
      color: var(--accent);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.14em;
    }}
    h1 {{
      margin: 4px 0 8px;
      font-family: Georgia, "Iowan Old Style", serif;
      font-size: clamp(28px, 3vw, 48px);
      line-height: 1;
      font-weight: 700;
      letter-spacing: 0;
    }}
    .subhead {{
      color: var(--muted);
      max-width: 1040px;
      font-size: 13px;
    }}
    .nav-links {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 12px;
    }}
    .nav-links a {{
      color: var(--ink);
      text-decoration: none;
      border: 1px solid var(--border-strong);
      background: var(--panel);
      border-radius: 6px;
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 800;
    }}
    .status-badge, .metric-card, .panel {{
      background: var(--panel);
      border: 1px solid var(--border-strong);
      border-radius: 8px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.28);
    }}
    .status-badge {{
      justify-self: end;
      padding: 10px 14px;
      text-align: right;
      min-width: 240px;
    }}
    .status-badge b {{
      display: block;
      font-size: 18px;
      color: var(--pos);
    }}
    .status-badge span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-top: 3px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }}
    .metric-card {{
      min-height: 86px;
      padding: 13px 14px;
    }}
    .metric-label {{
      color: var(--muted);
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }}
    .metric-value {{
      margin-top: 7px;
      color: var(--ink);
      font-size: 27px;
      font-weight: 800;
      font-variant-numeric: tabular-nums;
    }}
    .metric-pos .metric-value {{ color: var(--pos); }}
    .metric-warn .metric-value {{ color: var(--warn); }}
    .panel {{
      padding: 16px;
      overflow: hidden;
      margin-bottom: 16px;
    }}
    .panel h2 {{
      margin: 0 0 12px;
      color: var(--ink);
      font-size: 13px;
      font-weight: 850;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .panel .note {{
      margin: -5px 0 14px;
      color: var(--muted);
      font-size: 12px;
    }}
    .table-wrap {{
      overflow: auto;
      border: 1px solid var(--border-strong);
      border-radius: 6px;
      background: var(--panel);
      max-height: 74vh;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
    }}
    th, td {{
      padding: 8px 10px;
      border-bottom: 1px solid var(--border);
      color: var(--ink-soft);
      white-space: nowrap;
      text-align: left;
      vertical-align: middle;
      font-size: 12px;
    }}
    thead th {{
      position: sticky;
      top: 0;
      z-index: 3;
      background: var(--panel-alt);
      color: var(--muted);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 850;
    }}
    tbody tr:hover td {{ background: var(--panel-soft); }}
    .num {{
      text-align: right;
      font-variant-numeric: tabular-nums;
      font-family: "SF Mono", Menlo, Consolas, monospace;
    }}
    .score-strong {{
      color: var(--ink);
      font-weight: 850;
    }}
    .task-name {{
      color: var(--ink);
      font-weight: 750;
    }}
    .schema-name {{
      color: var(--ink-soft);
      font-weight: 800;
    }}
    .reasons {{
      max-width: 280px;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .delta-pos {{
      color: var(--pos) !important;
      background: var(--pos-bg) !important;
      font-weight: 850;
    }}
    .delta-neg {{
      color: var(--neg) !important;
      background: var(--neg-bg) !important;
      font-weight: 850;
    }}
    .delta-zero {{
      color: var(--muted) !important;
    }}
    .role-chip {{
      display: inline-block;
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 11px;
      font-weight: 850;
    }}
    .role-primary {{
      color: var(--pos);
      background: var(--pos-bg);
    }}
    .role-support {{
      color: var(--accent);
      background: rgba(103, 232, 249, 0.12);
    }}
    .role-floor {{
      color: var(--warn);
      background: var(--warn-bg);
    }}
    .role-other {{
      color: var(--muted);
      background: var(--panel-alt);
    }}
    code {{
      font-family: "SF Mono", Menlo, Consolas, monospace;
      color: var(--ink-soft);
      background: var(--panel-alt);
      border: 1px solid var(--border);
      padding: 2px 6px;
      border-radius: 4px;
    }}
    .footer {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 18px;
      text-align: center;
    }}
    @media (max-width: 1180px) {{
      main {{ width: min(100vw - 24px, 980px); }}
      .metrics {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
      .hero {{ grid-template-columns: 1fr; }}
      .status-badge {{ justify-self: stretch; text-align: left; }}
    }}
    @media (max-width: 720px) {{
      main {{ width: calc(100vw - 20px); padding-top: 18px; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div>
        <div class="eyebrow">SkillX outer-loop control plane</div>
        <h1>Schema Training Evidence</h1>
        <div class="subhead">
          This table preserves the finalized round0 results and shows the extra routing layer used by the next outer-loop rewrite. Rows are schema-task evidence assignments, including primary assignments, multi-assignment support rows, and floor-fill rows.
        </div>
        <div class="nav-links">
          <a href="/">Results Dashboard</a>
          <a href="/api/training-evidence">JSON API</a>
        </div>
      </div>
      <div class="status-badge">
        <b>{_escape(summary.get("row_count"))} evidence rows</b>
        <span>{_escape(source_generated_at)}</span>
      </div>
    </section>

    <section class="metrics">
      {_metric_card("Evidence Rows", summary.get("row_count"))}
      {_metric_card("Schemas", summary.get("schema_count"))}
      {_metric_card("Tasks", summary.get("task_count"))}
      {_metric_card("Primary", summary.get("primary_assignment_count"), " rows", "pos")}
      {_metric_card("Support", summary.get("support_count"), " rows")}
      {_metric_card("Floor Fill", summary.get("floor_count"), " rows", "warn")}
    </section>

    <section class="panel">
      <h2>Schema Evidence Counts</h2>
      <div class="note">Counts show how many tasks will be used as evidence for each schema rewrite. Floor-fill rows are included so under-supported schemas can still receive at least the configured minimum evidence.</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Schema</th>
              <th class="num">Total</th>
              <th class="num">Primary</th>
              <th class="num">Stable Support</th>
              <th class="num">High Score Support</th>
              <th class="num">Floor Fill</th>
              <th class="num">Other</th>
            </tr>
          </thead>
          <tbody>{_render_training_schema_summary(payload.get("schema_summary", []))}</tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <h2>Evidence Table</h2>
      <div class="note">Routing policy: {_escape(threshold_text)}. Source: <code>{_escape(payload.get("source_path"))}</code></div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Schema</th>
              <th>Task</th>
              <th>Evidence Role</th>
              <th>Evidence Reasons</th>
              <th class="num">Assignment Score</th>
              <th class="num">Reported Score</th>
              <th class="num">Schema Rank</th>
              <th class="num">Best dR0</th>
              <th>Trajectory Quality</th>
              <th>Primary Assignment</th>
              <th>Task Best Schema</th>
              <th class="num">Task Best Score</th>
            </tr>
          </thead>
          <tbody>{_render_training_evidence_rows(payload.get("rows", []))}</tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <h2>Column Definitions</h2>
      <div class="note">These definitions describe what each evidence-table column means operationally.</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Key</th><th>Column</th><th>Meaning</th></tr>
          </thead>
          <tbody>{_render_training_column_definitions(payload.get("columns", []))}</tbody>
        </table>
      </div>
    </section>

    <div class="footer">JSON API: <code>/api/training-evidence</code></div>
  </main>
</body>
</html>
"""


def render_dashboard_html(payload: dict[str, Any]) -> str:
    summary = payload.get("summary_metrics", {})
    checkpoint_summary = payload.get("checkpoint_summary", {})
    checkpoint_label = checkpoint_summary.get("checkpoint_label") or Path(
        str(payload.get("checkpoint_dir") or "")
    ).name
    best_task_rows = payload.get("best_task_rows", [])
    best_task_delta_overview = payload.get("best_task_delta_overview", {})
    generated_at = checkpoint_summary.get("generated_at") or payload.get("generated_at")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>SkillX First20 Round0 Dashboard</title>
  <style>
    :root {{
      --bg: #050505;
      --panel: #101112;
      --panel-alt: #17191b;
      --panel-soft: #1d2023;
      --ink: #f7f3ea;
      --ink-soft: #d7d0c0;
      --muted: #938f86;
      --border: #303337;
      --border-strong: #44484f;
      --accent: #67e8f9;
      --pos: #86efac;
      --pos-bg: rgba(134, 239, 172, 0.14);
      --neg: #fb7185;
      --neg-bg: rgba(251, 113, 133, 0.14);
      --warn: #fbbf24;
      --warn-bg: rgba(251, 191, 36, 0.13);
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ min-height: 100%; }}
    body {{
      margin: 0;
      background:
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(180deg, rgba(255,255,255,0.022) 1px, transparent 1px),
        var(--bg);
      background-size: 28px 28px;
      color: var(--ink);
      font-family: "Avenir Next", "Helvetica Neue", Helvetica, sans-serif;
      font-size: 14px;
      line-height: 1.45;
      color-scheme: dark;
    }}
    main {{
      width: min(1720px, calc(100vw - 36px));
      margin: 0 auto;
      padding: 26px 0 52px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 20px;
      align-items: start;
      margin-bottom: 18px;
    }}
    .eyebrow {{
      color: var(--accent);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.14em;
    }}
    h1 {{
      margin: 4px 0 8px;
      font-family: Georgia, "Iowan Old Style", serif;
      font-size: clamp(28px, 3vw, 48px);
      line-height: 1;
      font-weight: 700;
      letter-spacing: 0;
    }}
    .subhead {{
      color: var(--muted);
      max-width: 980px;
      font-size: 13px;
    }}
    .nav-links {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 12px;
    }}
    .nav-links a {{
      color: var(--ink);
      text-decoration: none;
      border: 1px solid var(--border-strong);
      background: var(--panel);
      border-radius: 6px;
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 800;
    }}
    .status-badge {{
      justify-self: end;
      border: 1px solid var(--border-strong);
      background: var(--panel);
      padding: 10px 14px;
      border-radius: 6px;
      text-align: right;
      min-width: 220px;
    }}
    .status-badge b {{
      display: block;
      font-size: 18px;
      color: var(--pos);
    }}
    .status-badge span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-top: 3px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }}
    .metric-card, .panel {{
      background: var(--panel);
      border: 1px solid var(--border-strong);
      border-radius: 8px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.28);
    }}
    .metric-card {{
      min-height: 86px;
      padding: 13px 14px;
    }}
    .metric-label {{
      color: var(--muted);
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }}
    .metric-value {{
      margin-top: 7px;
      color: var(--ink);
      font-size: 27px;
      font-weight: 800;
      font-variant-numeric: tabular-nums;
    }}
    .metric-pos .metric-value {{ color: var(--pos); }}
    .metric-warn .metric-value {{ color: var(--warn); }}
    .metric-neg .metric-value {{ color: var(--neg); }}
    .grid-2 {{
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 16px;
      align-items: start;
      margin-bottom: 16px;
    }}
    .panel {{
      padding: 16px;
      overflow: hidden;
    }}
    .panel h2 {{
      margin: 0 0 12px;
      color: var(--ink);
      font-size: 13px;
      font-weight: 850;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .panel .note {{
      margin: -5px 0 14px;
      color: var(--muted);
      font-size: 12px;
    }}
    .chart-grid {{
      stroke: rgba(255,255,255,0.12);
      stroke-width: 1;
    }}
    .chart-grid.faint {{ stroke: rgba(255,255,255,0.055); }}
    .chart-axis, .bar-label, .bar-value {{
      fill: var(--muted);
      font-size: 11px;
      font-family: "SF Mono", Menlo, Consolas, monospace;
    }}
    .bar-value {{ fill: var(--ink-soft); font-weight: 700; }}
    .chart-axis-line, .zero-line {{
      stroke: var(--border-strong);
      stroke-width: 1.4;
    }}
    .trajectory-svg, .delta-svg {{
      width: 100%;
      height: auto;
      display: block;
      background: #0a0b0c;
      border: 1px solid var(--border);
      border-radius: 6px;
    }}
    .legend-list {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 7px 16px;
      list-style: none;
      padding: 0;
      margin: 14px 0 0;
    }}
    .legend-list li {{
      display: grid;
      grid-template-columns: 12px minmax(0, 1fr) 44px 74px;
      gap: 8px;
      align-items: center;
      color: var(--ink-soft);
      font-size: 12px;
      min-width: 0;
    }}
    .legend-list span:nth-child(2) {{
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 2px;
      display: inline-block;
    }}
    .legend-list b {{
      text-align: right;
      font-variant-numeric: tabular-nums;
    }}
    .legend-list em {{
      color: var(--muted);
      font-style: normal;
      text-align: right;
      font-variant-numeric: tabular-nums;
    }}
    .delta-scorecards {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-bottom: 14px;
    }}
    .delta-card {{
      background: var(--panel-alt);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 12px;
    }}
    .delta-title {{
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .delta-mean {{
      margin-top: 4px;
      font-size: 28px;
      font-weight: 850;
      color: var(--ink);
      font-variant-numeric: tabular-nums;
    }}
    .delta-splits {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
    }}
    .delta-splits .pos {{ color: var(--pos); }}
    .delta-splits .neg {{ color: var(--neg); }}
    .delta-range {{
      margin-top: 7px;
      color: var(--muted);
      font-size: 11px;
      font-variant-numeric: tabular-nums;
    }}
    .table-wrap, .matrix-wrap {{
      overflow: auto;
      border: 1px solid var(--border-strong);
      border-radius: 6px;
      background: var(--panel);
      max-height: 74vh;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
    }}
    th, td {{
      padding: 8px 10px;
      border-bottom: 1px solid var(--border);
      color: var(--ink-soft);
      white-space: nowrap;
      text-align: left;
      vertical-align: middle;
      font-size: 12px;
    }}
    thead th {{
      position: sticky;
      top: 0;
      z-index: 3;
      background: var(--panel-alt);
      color: var(--muted);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 850;
    }}
    tbody tr:hover td, tbody tr:hover th {{ background: var(--panel-soft); }}
    .num {{
      text-align: right;
      font-variant-numeric: tabular-nums;
      font-family: "SF Mono", Menlo, Consolas, monospace;
    }}
    .score-strong {{
      color: var(--ink);
      font-weight: 850;
    }}
    .task-name {{
      color: var(--ink);
      font-weight: 750;
    }}
    .schema-name {{
      color: var(--muted);
    }}
    .delta-pos {{
      color: var(--pos) !important;
      background: var(--pos-bg) !important;
      font-weight: 850;
    }}
    .delta-neg {{
      color: var(--neg) !important;
      background: var(--neg-bg) !important;
      font-weight: 850;
    }}
    .delta-zero {{
      color: var(--muted) !important;
    }}
    .matrix-table th, .matrix-table td {{
      min-width: 122px;
      padding: 8px;
    }}
    .matrix-table thead th:first-child, .matrix-task {{
      position: sticky;
      left: 0;
      z-index: 4;
      min-width: 230px;
      max-width: 230px;
      overflow: hidden;
      text-overflow: ellipsis;
      background: var(--panel-alt);
    }}
    .matrix-cell {{
      height: 76px;
      border-left: 1px solid var(--border);
    }}
    .cell-score {{
      color: var(--ink);
      font-weight: 850;
      font-size: 17px;
      font-variant-numeric: tabular-nums;
    }}
    .cell-meta {{
      margin-top: 1px;
      color: var(--muted);
      font-size: 10px;
      font-family: "SF Mono", Menlo, Consolas, monospace;
    }}
    .spark {{
      width: 96px;
      height: 28px;
      margin-top: 4px;
      display: block;
    }}
    .spark-base {{
      stroke: rgba(255,255,255,0.16);
      stroke-width: 1;
    }}
    .spark-ceiling {{
      stroke: rgba(255,255,255,0.08);
      stroke-width: 1;
    }}
    .focus-panel {{
      padding: 18px;
    }}
    .focus-summary {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin: 0 0 14px;
    }}
    .focus-summary span {{
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 5px 10px;
      background: var(--panel-alt);
      color: var(--muted);
      font-size: 11px;
      font-weight: 750;
      letter-spacing: 0;
    }}
    .focus-table th, .focus-table td {{
      padding: 10px 10px;
      font-size: 12px;
    }}
    .focus-table thead th:first-child,
    .focus-table .task-name {{
      position: sticky;
      left: 0;
      z-index: 4;
      background: var(--panel);
      min-width: 250px;
      max-width: 250px;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .focus-table thead th:first-child {{
      background: var(--panel-alt);
    }}
    .schema-choice {{
      min-width: 158px;
    }}
    .schema-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--ink);
      font-weight: 800;
    }}
    .schema-chip::before {{
      content: "";
      width: 10px;
      height: 10px;
      border-radius: 2px;
      background: var(--schema-color);
      box-shadow: 0 0 12px color-mix(in srgb, var(--schema-color), transparent 55%);
    }}
    .tie-note {{
      display: block;
      margin-top: 3px;
      color: var(--muted);
      font-size: 10px;
      font-family: "SF Mono", Menlo, Consolas, monospace;
    }}
    .score-delta {{
      min-width: 88px;
      text-align: right;
      font-family: "SF Mono", Menlo, Consolas, monospace;
      font-variant-numeric: tabular-nums;
    }}
    .score-delta b {{
      display: block;
      color: var(--ink);
      font-size: 13px;
    }}
    .score-delta em {{
      display: block;
      margin-top: 2px;
      color: currentColor;
      font-style: normal;
      font-size: 10px;
    }}
    .focus-spark {{
      width: 156px;
      height: 42px;
      display: block;
    }}
    .heat-1 {{ background: rgba(251, 113, 133, 0.13); }}
    .heat-2 {{ background: rgba(249, 115, 22, 0.13); }}
    .heat-3 {{ background: rgba(251, 191, 36, 0.13); }}
    .heat-4 {{ background: rgba(103, 232, 249, 0.12); }}
    .heat-5 {{ background: rgba(134, 239, 172, 0.14); }}
    .heat-empty {{ background: var(--panel); }}
    .footer {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 18px;
      text-align: center;
    }}
    code {{
      font-family: "SF Mono", Menlo, Consolas, monospace;
      color: var(--ink-soft);
      background: var(--panel-alt);
      border: 1px solid var(--border);
      padding: 2px 6px;
      border-radius: 4px;
    }}
    @media (max-width: 1180px) {{
      main {{ width: min(100vw - 24px, 980px); }}
      .metrics {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
      .grid-2 {{ grid-template-columns: 1fr; }}
      .hero {{ grid-template-columns: 1fr; }}
      .status-badge {{ justify-self: stretch; text-align: left; }}
    }}
    @media (max-width: 720px) {{
      main {{ width: calc(100vw - 20px); padding-top: 18px; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .delta-scorecards {{ grid-template-columns: 1fr; }}
      .legend-list {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div>
        <div class="eyebrow">SkillX round0 results dashboard</div>
        <h1>Best-Schema Task Curves</h1>
        <div class="subhead">
          Checkpoint <code>{_escape(checkpoint_label)}</code>. Each row picks the schema with the highest best score for that task; if schemas tie, it picks the tied schema with the largest best-vs-R0 lift.
        </div>
        <div class="nav-links">
          <a href="/training-evidence">Schema Training Evidence</a>
          <a href="/api/dashboard">JSON API</a>
        </div>
      </div>
      <div class="status-badge">
        <b>{_escape(summary.get("task_count"))} task curves</b>
        <span>{_escape(generated_at)}</span>
      </div>
    </section>

    <section class="metrics">
      {_metric_card("Tasks", summary.get("task_count"))}
      {_metric_card("Mean R0", _fmt(summary.get("best_task_mean_r0_score_pct")), "%")}
      {_metric_card("Mean Best", _fmt(summary.get("best_task_mean_best_score_pct")), "%", "pos")}
      {_metric_card("Mean dBest vs R0", _fmt(summary.get("best_task_mean_delta_vs_r0_pp")), " pp", "pos")}
      {_metric_card("Improved", summary.get("best_task_improved_count"), " tasks", "pos")}
      {_metric_card("Flat", summary.get("best_task_flat_count"), " tasks")}
    </section>

    <section class="panel focus-panel">
      <h2>Best-Schema R0 Trajectories</h2>
      <div class="note">Scores are 0-100. R1/R2/R3 cells show score first and delta vs R0 underneath. dBest is best score minus R0; dFinal is the last available round minus R0.</div>
      <div class="focus-summary">
        <span>{_escape(best_task_delta_overview.get("positive", 0))} tasks improved vs R0</span>
        <span>{_escape(best_task_delta_overview.get("flat", 0))} flat vs R0</span>
        <span>{_escape(best_task_delta_overview.get("negative", 0))} regressed vs R0</span>
        <span>median dBest {_escape(_fmt(best_task_delta_overview.get("median")))} pp</span>
        <span>range {_escape(_fmt(best_task_delta_overview.get("min")))} to {_escape(_fmt(best_task_delta_overview.get("max")))} pp</span>
      </div>
      <div class="table-wrap">
        <table class="focus-table">
          <thead>
            <tr>
              <th>Task</th>
              <th>Best Schema</th>
              <th class="num">R0</th>
              <th class="num">R1 / dR0</th>
              <th class="num">R2 / dR0</th>
              <th class="num">R3 / dR0</th>
              <th class="num">Best Round</th>
              <th class="num">Best</th>
              <th class="num">dBest vs R0</th>
              <th class="num">dFinal vs R0</th>
              <th>Curve</th>
            </tr>
          </thead>
          <tbody>{_render_best_task_rows(best_task_rows)}</tbody>
        </table>
      </div>
    </section>

    <div class="footer">JSON API: <code>/api/dashboard</code></div>
  </main>
</body>
</html>
"""


def build_server(
    *,
    checkpoint_dir: Path,
    control_plane_dir: Path,
    host: str,
    port: int,
) -> ThreadingHTTPServer:
    checkpoint_dir = checkpoint_dir.resolve()
    control_plane_dir = control_plane_dir.resolve()

    class DashboardHandler(BaseHTTPRequestHandler):
        def _payload(self) -> dict[str, Any]:
            return build_dashboard_payload(checkpoint_dir)

        def _training_evidence_payload(self) -> dict[str, Any]:
            return build_training_evidence_payload(control_plane_dir)

        def _write_json(self, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _write_html(self, body_text: str) -> None:
            body = body_text.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
                return
            if path == "/api/dashboard":
                self._write_json(self._payload())
                return
            if path == "/api/training-evidence":
                self._write_json(self._training_evidence_payload())
                return
            if path in {"/training-evidence", "/training-evidence.html"}:
                self._write_html(render_training_evidence_html(self._training_evidence_payload()))
                return
            if path in {"/", "/index.html"}:
                self._write_html(render_dashboard_html(self._payload()))
                return
            self.send_error(404, "Not Found")

        def log_message(self, format: str, *args: object) -> None:
            return

    return ThreadingHTTPServer((host, port), DashboardHandler)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Serve the finalized first20 x 7 SkillX round0 visualization dashboard."
    )
    parser.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINT_DIR)
    parser.add_argument("--control-plane-dir", type=Path, default=DEFAULT_CONTROL_PLANE_DIR)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8770)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    server = build_server(
        checkpoint_dir=args.checkpoint_dir,
        control_plane_dir=args.control_plane_dir,
        host=args.host,
        port=args.port,
    )
    url = f"http://{args.host}:{args.port}/"
    print(f"Serving first20 round0 dashboard for {args.checkpoint_dir.resolve()}")
    print(f"Schema training evidence: {args.control_plane_dir.resolve()}")
    print(f"Open: {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

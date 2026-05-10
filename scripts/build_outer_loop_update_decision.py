#!/usr/bin/env python3
"""Classify whether an outer-loop step should rewrite, patch, or hold.

The decision compares a stable reference control-plane bundle with the latest
candidate control-plane bundle. A clean positive lift can proceed as a rewrite;
mixed lift with protected regressions becomes a guarded patch; no usable lift
with heavy regressions becomes a hold.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROUND0_ROOT = (
    ROOT
    / "experiments"
    / "skillx-skillsbench-001"
    / "results"
    / "outer-loop-round0"
)
DEFAULT_CURRENT_CONTROL_PLANE_BUNDLE_PATH = (
    DEFAULT_ROUND0_ROOT / "reports" / "outer-loop-control-plane" / "control_plane_bundle.json"
)
DEFAULT_OUTPUT_DIR = DEFAULT_ROUND0_ROOT / "reports" / "outer-loop-update-decision"
DEFAULT_UPDATE_DECISION_MODE = "auto"
DEFAULT_MIN_POSITIVE_TRANSFER_DELTA_PP = 25.0
DEFAULT_STRONG_SCORE_PCT = 80.0
DEFAULT_WEAK_SCORE_PCT = 20.0
DEFAULT_REGRESSION_DROP_PP = 50.0
DEFAULT_MAX_PROTECTED_REGRESSIONS_FOR_REWRITE = 2
DEFAULT_MIN_TARGETED_LIFT_FOR_REWRITE_PP = 5.0

UPDATE_DECISION_MODES = ("auto", "rewrite", "guarded_patch", "hold")


def timestamp() -> str:
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


def normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(";") if part.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def score_rows_from_bundle(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    score_matrix = bundle.get("score_matrix") or {}
    long_rows = score_matrix.get("long_rows")
    if isinstance(long_rows, list) and long_rows:
        return [row for row in long_rows if isinstance(row, dict)]
    pair_rows = bundle.get("pair_rows")
    if isinstance(pair_rows, list):
        return [row for row in pair_rows if isinstance(row, dict)]
    return []


def score_value(row: dict[str, Any]) -> float | None:
    for key in ("score", "assignment_score_pct", "reported_score", "reported_score_pct"):
        value = coerce_float(row.get(key))
        if value is not None:
            return value
    return None


def reported_score_value(row: dict[str, Any]) -> float | None:
    for key in ("reported_score", "reported_score_pct", "final_score"):
        value = coerce_float(row.get(key))
        if value is not None:
            return value
    return None


def trajectory_signal_value(row: dict[str, Any]) -> float | None:
    return coerce_float(row.get("trajectory_signal_score_pct"))


def pair_key(task_name: str, schema_id: str) -> str:
    return f"{task_name}__{schema_id}"


def index_score_rows(bundle: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for row in score_rows_from_bundle(bundle):
        task_name = row.get("task_name")
        schema_id = row.get("schema_id")
        if isinstance(task_name, str) and isinstance(schema_id, str):
            indexed[(task_name, schema_id)] = row
    return indexed


def schema_ids_from_bundles(*bundles: dict[str, Any]) -> list[str]:
    seen: list[str] = []
    for bundle in bundles:
        for schema_id in bundle.get("schema_ids") or []:
            if isinstance(schema_id, str) and schema_id not in seen:
                seen.append(schema_id)
        for row in score_rows_from_bundle(bundle):
            schema_id = row.get("schema_id")
            if isinstance(schema_id, str) and schema_id not in seen:
                seen.append(schema_id)
    return seen


def primary_assignment_pairs(bundle: dict[str, Any]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for row in bundle.get("assignments") or []:
        if not isinstance(row, dict):
            continue
        task_name = row.get("task_name")
        schema_id = row.get("assigned_category")
        if row.get("assignment_status") == "assigned" and isinstance(task_name, str) and isinstance(schema_id, str):
            pairs.add((task_name, schema_id))
    return pairs


def multi_assignment_pairs(bundle: dict[str, Any]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for row in bundle.get("multi_assignments") or []:
        if not isinstance(row, dict):
            continue
        task_name = row.get("task_name")
        schema_id = row.get("schema_id")
        if isinstance(task_name, str) and isinstance(schema_id, str):
            pairs.add((task_name, schema_id))
    return pairs


def schema_training_pairs(bundle: dict[str, Any]) -> set[tuple[str, str]]:
    diagnostics = bundle.get("diagnostics") or {}
    rows = diagnostics.get("schema_training_assignments")
    if not isinstance(rows, list) or not rows:
        rows = bundle.get("schema_training_assignments")
    pairs: set[tuple[str, str]] = set()
    if not isinstance(rows, list):
        return pairs
    for row in rows:
        if not isinstance(row, dict):
            continue
        task_name = row.get("task_name")
        schema_id = row.get("schema_id")
        if isinstance(task_name, str) and isinstance(schema_id, str):
            pairs.add((task_name, schema_id))
    return pairs


def previous_pair_roles(bundle: dict[str, Any]) -> dict[tuple[str, str], set[str]]:
    roles: dict[tuple[str, str], set[str]] = defaultdict(set)
    for key in primary_assignment_pairs(bundle):
        roles[key].add("previous_primary_assignment")
    for key in multi_assignment_pairs(bundle):
        roles[key].add("previous_multi_assignment")
    for key in schema_training_pairs(bundle):
        roles[key].add("previous_schema_training_assignment")
    return roles


def rounded(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 4)


def delta(current: float | None, previous: float | None) -> float | None:
    if current is None or previous is None:
        return None
    return round(current - previous, 4)


def build_pair_comparisons(
    previous_bundle: dict[str, Any],
    current_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    previous_scores = index_score_rows(previous_bundle)
    current_scores = index_score_rows(current_bundle)
    roles_by_pair = previous_pair_roles(previous_bundle)
    rows: list[dict[str, Any]] = []
    for task_name, schema_id in sorted(set(previous_scores) & set(current_scores)):
        previous_row = previous_scores[(task_name, schema_id)]
        current_row = current_scores[(task_name, schema_id)]
        previous_score = score_value(previous_row)
        current_score = score_value(current_row)
        previous_reported = reported_score_value(previous_row)
        current_reported = reported_score_value(current_row)
        previous_trajectory = trajectory_signal_value(previous_row)
        current_trajectory = trajectory_signal_value(current_row)
        rows.append(
            {
                "pair_id": pair_key(task_name, schema_id),
                "task_name": task_name,
                "schema_id": schema_id,
                "previous_score": rounded(previous_score),
                "current_score": rounded(current_score),
                "score_delta_pp": delta(current_score, previous_score),
                "previous_reported_score": rounded(previous_reported),
                "current_reported_score": rounded(current_reported),
                "reported_score_delta_pp": delta(current_reported, previous_reported),
                "previous_trajectory_signal_score": rounded(previous_trajectory),
                "current_trajectory_signal_score": rounded(current_trajectory),
                "trajectory_signal_delta_pp": delta(current_trajectory, previous_trajectory),
                "previous_roles": sorted(roles_by_pair.get((task_name, schema_id), set())),
                "previous_evidence_class": previous_row.get("evidence_class"),
                "current_evidence_class": current_row.get("evidence_class"),
                "current_failure_type": current_row.get("failure_type"),
                "current_failure_summary": current_row.get("failure_summary"),
            }
        )
    return rows


def has_role(row: dict[str, Any], role: str) -> bool:
    return role in set(normalize_string_list(row.get("previous_roles")))


def build_scorecard(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups = {
        "all_common_pairs": rows,
        "previous_primary_assignment": [
            row for row in rows if has_role(row, "previous_primary_assignment")
        ],
        "previous_multi_assignment": [
            row for row in rows if has_role(row, "previous_multi_assignment")
        ],
        "previous_schema_training_assignment": [
            row for row in rows if has_role(row, "previous_schema_training_assignment")
        ],
    }
    scorecard: dict[str, Any] = {}
    for group_name, group_rows in groups.items():
        score_deltas = [
            float(row["score_delta_pp"])
            for row in group_rows
            if row.get("score_delta_pp") is not None
        ]
        reported_deltas = [
            float(row["reported_score_delta_pp"])
            for row in group_rows
            if row.get("reported_score_delta_pp") is not None
        ]
        previous_scores = [
            float(row["previous_score"])
            for row in group_rows
            if row.get("previous_score") is not None
        ]
        current_scores = [
            float(row["current_score"])
            for row in group_rows
            if row.get("current_score") is not None
        ]
        scorecard[group_name] = {
            "pair_count": len(group_rows),
            "comparable_score_count": len(score_deltas),
            "mean_previous_score": rounded(mean(previous_scores)) if previous_scores else None,
            "mean_current_score": rounded(mean(current_scores)) if current_scores else None,
            "mean_score_delta_pp": rounded(mean(score_deltas)) if score_deltas else None,
            "mean_reported_score_delta_pp": rounded(mean(reported_deltas)) if reported_deltas else None,
        }
    return scorecard


def is_positive_transfer(
    row: dict[str, Any],
    *,
    min_positive_transfer_delta_pp: float,
    strong_score_pct: float,
) -> bool:
    score_delta = coerce_float(row.get("score_delta_pp"))
    reported_delta = coerce_float(row.get("reported_score_delta_pp"))
    trajectory_delta = coerce_float(row.get("trajectory_signal_delta_pp"))
    previous_reported = coerce_float(row.get("previous_reported_score"))
    current_reported = coerce_float(row.get("current_reported_score"))
    if score_delta is not None and score_delta >= min_positive_transfer_delta_pp:
        return True
    if trajectory_delta is not None and trajectory_delta >= min_positive_transfer_delta_pp:
        return True
    if (
        reported_delta is not None
        and previous_reported is not None
        and current_reported is not None
        and previous_reported < strong_score_pct
        and current_reported >= strong_score_pct
        and reported_delta >= min_positive_transfer_delta_pp
    ):
        return True
    return False


def is_protected_regression(
    row: dict[str, Any],
    *,
    strong_score_pct: float,
    weak_score_pct: float,
    regression_drop_pp: float,
) -> bool:
    previous_score = coerce_float(row.get("previous_score"))
    current_score = coerce_float(row.get("current_score"))
    previous_reported = coerce_float(row.get("previous_reported_score"))
    current_reported = coerce_float(row.get("current_reported_score"))
    score_delta = coerce_float(row.get("score_delta_pp"))
    reported_delta = coerce_float(row.get("reported_score_delta_pp"))
    previously_targeted = bool(normalize_string_list(row.get("previous_roles")))
    previous_strong = (
        (previous_score is not None and previous_score >= strong_score_pct)
        or (previous_reported is not None and previous_reported >= strong_score_pct)
    )
    current_weak = (
        (current_score is not None and current_score <= weak_score_pct)
        or (current_reported is not None and current_reported <= weak_score_pct)
    )
    large_drop = (
        (score_delta is not None and score_delta <= -regression_drop_pp)
        or (reported_delta is not None and reported_delta <= -regression_drop_pp)
    )
    return previous_strong and current_weak and large_drop and previously_targeted


def compact_evidence_row(row: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "pair_id",
        "task_name",
        "schema_id",
        "previous_score",
        "current_score",
        "score_delta_pp",
        "previous_reported_score",
        "current_reported_score",
        "reported_score_delta_pp",
        "previous_trajectory_signal_score",
        "current_trajectory_signal_score",
        "trajectory_signal_delta_pp",
        "previous_roles",
        "current_evidence_class",
        "current_failure_type",
        "current_failure_summary",
    ]
    return {key: row.get(key) for key in keys}


def decide_global_mode(
    *,
    requested_mode: str,
    scorecard: dict[str, Any],
    positive_transfer_count: int,
    protected_regression_count: int,
    max_protected_regressions_for_rewrite: int,
    min_targeted_lift_for_rewrite_pp: float,
) -> tuple[str, str]:
    if requested_mode != "auto":
        return requested_mode, f"manual_{requested_mode}"
    targeted = scorecard.get("previous_schema_training_assignment") or {}
    if not targeted.get("pair_count"):
        targeted = scorecard.get("previous_primary_assignment") or {}
    targeted_delta = coerce_float(targeted.get("mean_score_delta_pp"))
    if protected_regression_count > max_protected_regressions_for_rewrite:
        if positive_transfer_count > 0:
            return (
                "guarded_patch",
                "protected regressions exceed rewrite guard, but positive transfer evidence exists",
            )
        return "hold", "protected regressions exceed rewrite guard and no positive transfer evidence exists"
    if targeted_delta is not None and targeted_delta >= min_targeted_lift_for_rewrite_pp:
        return "rewrite", "targeted evidence has positive lift with acceptable protected regressions"
    if positive_transfer_count > 0:
        return "guarded_patch", "positive transfer exists but targeted evidence is not rewrite-stable"
    return "hold", "no positive transfer evidence after comparing with the stable reference bundle"


def build_schema_decisions(
    *,
    schema_ids: list[str],
    global_update_mode: str,
    positive_transfer_pairs: list[dict[str, Any]],
    protected_regression_pairs: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    positives_by_schema: dict[str, list[dict[str, Any]]] = defaultdict(list)
    regressions_by_schema: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in positive_transfer_pairs:
        positives_by_schema[str(row.get("schema_id"))].append(row)
    for row in protected_regression_pairs:
        regressions_by_schema[str(row.get("schema_id"))].append(row)

    decisions: dict[str, dict[str, Any]] = {}
    for schema_id in schema_ids:
        positive_rows = positives_by_schema.get(schema_id, [])
        regression_rows = regressions_by_schema.get(schema_id, [])
        if global_update_mode == "rewrite":
            schema_mode = "rewrite"
            reason = "global rewrite decision"
        elif global_update_mode == "guarded_patch":
            if positive_rows:
                schema_mode = "guarded_patch"
                reason = "schema has positive transfer evidence; patch against stable base"
            else:
                schema_mode = "hold"
                reason = "no schema-local positive transfer; keep stable base"
        else:
            schema_mode = "hold"
            reason = "global hold decision"
        decisions[schema_id] = {
            "schema_id": schema_id,
            "update_mode": schema_mode,
            "reason": reason,
            "positive_transfer_count": len(positive_rows),
            "protected_regression_count": len(regression_rows),
            "positive_transfer_pairs": positive_rows[:12],
            "protected_regression_pairs": regression_rows[:12],
            "allowed_patch_scope": (
                [
                    "narrow slot edits grounded in positive transfer pairs",
                    "preserve incumbent behavior unless evidence requires a small sharpen",
                ]
                if schema_mode == "guarded_patch"
                else []
            ),
            "blocked_regression_patterns": [
                f"{row['task_name']} regressed from {row.get('previous_reported_score')} to {row.get('current_reported_score')}"
                for row in regression_rows[:8]
            ],
        }
    return decisions


def build_outer_loop_update_decision(
    *,
    current_control_plane_bundle_path: Path,
    previous_control_plane_bundle_path: Path | None,
    requested_mode: str = DEFAULT_UPDATE_DECISION_MODE,
    min_positive_transfer_delta_pp: float = DEFAULT_MIN_POSITIVE_TRANSFER_DELTA_PP,
    strong_score_pct: float = DEFAULT_STRONG_SCORE_PCT,
    weak_score_pct: float = DEFAULT_WEAK_SCORE_PCT,
    regression_drop_pp: float = DEFAULT_REGRESSION_DROP_PP,
    max_protected_regressions_for_rewrite: int = DEFAULT_MAX_PROTECTED_REGRESSIONS_FOR_REWRITE,
    min_targeted_lift_for_rewrite_pp: float = DEFAULT_MIN_TARGETED_LIFT_FOR_REWRITE_PP,
) -> dict[str, Any]:
    if requested_mode not in UPDATE_DECISION_MODES:
        raise ValueError(f"unsupported update decision mode: {requested_mode}")

    current_bundle = read_json(current_control_plane_bundle_path)
    if previous_control_plane_bundle_path is None:
        schema_ids = schema_ids_from_bundles(current_bundle)
        update_mode = "rewrite" if requested_mode == "auto" else requested_mode
        return {
            "artifact_type": "skillx_outer_loop_update_decision",
            "version": "v0.1",
            "generated_at": timestamp(),
            "global_update_mode": update_mode,
            "mode_reason": "no previous control-plane bundle supplied",
            "config": {
                "requested_mode": requested_mode,
                "previous_control_plane_bundle_path": None,
                "current_control_plane_bundle_path": display_path(current_control_plane_bundle_path.resolve()),
                "min_positive_transfer_delta_pp": min_positive_transfer_delta_pp,
                "strong_score_pct": strong_score_pct,
                "weak_score_pct": weak_score_pct,
                "regression_drop_pp": regression_drop_pp,
                "max_protected_regressions_for_rewrite": max_protected_regressions_for_rewrite,
                "min_targeted_lift_for_rewrite_pp": min_targeted_lift_for_rewrite_pp,
            },
            "scorecard": {},
            "positive_transfer_pairs": [],
            "protected_regression_pairs": [],
            "schema_decisions": build_schema_decisions(
                schema_ids=schema_ids,
                global_update_mode=update_mode,
                positive_transfer_pairs=[],
                protected_regression_pairs=[],
            ),
        }

    previous_bundle = read_json(previous_control_plane_bundle_path)
    comparisons = build_pair_comparisons(previous_bundle, current_bundle)
    scorecard = build_scorecard(comparisons)
    positive_transfer_pairs = [
        compact_evidence_row(row)
        for row in comparisons
        if is_positive_transfer(
            row,
            min_positive_transfer_delta_pp=min_positive_transfer_delta_pp,
            strong_score_pct=strong_score_pct,
        )
    ]
    protected_regression_pairs = [
        compact_evidence_row(row)
        for row in comparisons
        if is_protected_regression(
            row,
            strong_score_pct=strong_score_pct,
            weak_score_pct=weak_score_pct,
            regression_drop_pp=regression_drop_pp,
        )
    ]
    update_mode, reason = decide_global_mode(
        requested_mode=requested_mode,
        scorecard=scorecard,
        positive_transfer_count=len(positive_transfer_pairs),
        protected_regression_count=len(protected_regression_pairs),
        max_protected_regressions_for_rewrite=max_protected_regressions_for_rewrite,
        min_targeted_lift_for_rewrite_pp=min_targeted_lift_for_rewrite_pp,
    )
    schema_ids = schema_ids_from_bundles(previous_bundle, current_bundle)
    return {
        "artifact_type": "skillx_outer_loop_update_decision",
        "version": "v0.1",
        "generated_at": timestamp(),
        "global_update_mode": update_mode,
        "mode_reason": reason,
        "config": {
            "requested_mode": requested_mode,
            "previous_control_plane_bundle_path": display_path(previous_control_plane_bundle_path.resolve()),
            "current_control_plane_bundle_path": display_path(current_control_plane_bundle_path.resolve()),
            "min_positive_transfer_delta_pp": min_positive_transfer_delta_pp,
            "strong_score_pct": strong_score_pct,
            "weak_score_pct": weak_score_pct,
            "regression_drop_pp": regression_drop_pp,
            "max_protected_regressions_for_rewrite": max_protected_regressions_for_rewrite,
            "min_targeted_lift_for_rewrite_pp": min_targeted_lift_for_rewrite_pp,
        },
        "scorecard": scorecard,
        "positive_transfer_pairs": positive_transfer_pairs,
        "protected_regression_pairs": protected_regression_pairs,
        "schema_decisions": build_schema_decisions(
            schema_ids=schema_ids,
            global_update_mode=update_mode,
            positive_transfer_pairs=positive_transfer_pairs,
            protected_regression_pairs=protected_regression_pairs,
        ),
    }


def render_summary_markdown(decision: dict[str, Any], output_dir: Path) -> str:
    scorecard = decision.get("scorecard") or {}
    lines = [
        "# SkillX Outer-Loop Update Decision",
        "",
        f"- generated_at: `{decision.get('generated_at')}`",
        f"- output_dir: `{display_path(output_dir)}`",
        f"- global_update_mode: `{decision.get('global_update_mode')}`",
        f"- mode_reason: {decision.get('mode_reason')}",
        f"- positive_transfer_pairs: `{len(decision.get('positive_transfer_pairs') or [])}`",
        f"- protected_regression_pairs: `{len(decision.get('protected_regression_pairs') or [])}`",
        "",
        "## Scorecard",
        "",
        "| group | pairs | mean previous | mean current | mean delta |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for group_name, row in scorecard.items():
        lines.append(
            "| "
            + " | ".join(
                [
                    str(group_name),
                    str(row.get("pair_count")),
                    str(row.get("mean_previous_score")),
                    str(row.get("mean_current_score")),
                    str(row.get("mean_score_delta_pp")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Schema Decisions",
            "",
            "| schema | mode | positives | protected regressions | reason |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for schema_id, row in sorted((decision.get("schema_decisions") or {}).items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(schema_id),
                    str(row.get("update_mode")),
                    str(row.get("positive_transfer_count")),
                    str(row.get("protected_regression_count")),
                    str(row.get("reason")),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def write_outer_loop_update_decision_artifacts(
    *,
    decision: dict[str, Any],
    output_dir: Path,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    decision_path = output_dir / "outer_loop_update_decision.json"
    positive_path = output_dir / "positive_transfer_pairs.csv"
    regressions_path = output_dir / "protected_regression_pairs.csv"
    summary_path = output_dir / "summary.md"
    write_json(decision_path, decision)
    evidence_fields = [
        "pair_id",
        "task_name",
        "schema_id",
        "previous_score",
        "current_score",
        "score_delta_pp",
        "previous_reported_score",
        "current_reported_score",
        "reported_score_delta_pp",
        "previous_trajectory_signal_score",
        "current_trajectory_signal_score",
        "trajectory_signal_delta_pp",
        "previous_roles",
        "current_evidence_class",
        "current_failure_type",
        "current_failure_summary",
    ]
    write_csv(
        positive_path,
        decision.get("positive_transfer_pairs") or [],
        evidence_fields,
    )
    write_csv(
        regressions_path,
        decision.get("protected_regression_pairs") or [],
        evidence_fields,
    )
    summary_path.write_text(render_summary_markdown(decision, output_dir))
    return {
        "outer_loop_update_decision_json": display_path(decision_path),
        "positive_transfer_pairs_csv": display_path(positive_path),
        "protected_regression_pairs_csv": display_path(regressions_path),
        "summary_md": display_path(summary_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-control-plane-bundle-path", type=Path, default=DEFAULT_CURRENT_CONTROL_PLANE_BUNDLE_PATH)
    parser.add_argument("--previous-control-plane-bundle-path", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--update-decision-mode",
        choices=UPDATE_DECISION_MODES,
        default=DEFAULT_UPDATE_DECISION_MODE,
    )
    parser.add_argument("--min-positive-transfer-delta-pp", type=float, default=DEFAULT_MIN_POSITIVE_TRANSFER_DELTA_PP)
    parser.add_argument("--strong-score-pct", type=float, default=DEFAULT_STRONG_SCORE_PCT)
    parser.add_argument("--weak-score-pct", type=float, default=DEFAULT_WEAK_SCORE_PCT)
    parser.add_argument("--regression-drop-pp", type=float, default=DEFAULT_REGRESSION_DROP_PP)
    parser.add_argument(
        "--max-protected-regressions-for-rewrite",
        type=int,
        default=DEFAULT_MAX_PROTECTED_REGRESSIONS_FOR_REWRITE,
    )
    parser.add_argument(
        "--min-targeted-lift-for-rewrite-pp",
        type=float,
        default=DEFAULT_MIN_TARGETED_LIFT_FOR_REWRITE_PP,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    decision = build_outer_loop_update_decision(
        current_control_plane_bundle_path=args.current_control_plane_bundle_path,
        previous_control_plane_bundle_path=args.previous_control_plane_bundle_path,
        requested_mode=str(args.update_decision_mode),
        min_positive_transfer_delta_pp=float(args.min_positive_transfer_delta_pp),
        strong_score_pct=float(args.strong_score_pct),
        weak_score_pct=float(args.weak_score_pct),
        regression_drop_pp=float(args.regression_drop_pp),
        max_protected_regressions_for_rewrite=int(args.max_protected_regressions_for_rewrite),
        min_targeted_lift_for_rewrite_pp=float(args.min_targeted_lift_for_rewrite_pp),
    )
    outputs = write_outer_loop_update_decision_artifacts(
        decision=decision,
        output_dir=args.output_dir,
    )
    print(json.dumps(outputs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

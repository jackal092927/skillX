#!/usr/bin/env python3
"""Build post-assignment outer-loop schema update packages.

This script consumes the round-0 control-plane bundle after task-to-schema
assignment and emits auditable schema-level update proposals. It intentionally
does not overwrite the seed prompt bank; instead it writes a candidate prompt
bank and evidence bundles for the next outer-loop round.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from copy import deepcopy
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
DEFAULT_CONTROL_PLANE_BUNDLE_PATH = (
    DEFAULT_ROUND0_ROOT / "reports" / "outer-loop-control-plane" / "control_plane_bundle.json"
)
DEFAULT_PROMPT_BANK_PATH = ROOT / "docs" / "plans" / "skillx" / "skillx-prompt-bank-v0.1.json"
DEFAULT_TASK_CLUSTER_INPUTS_PATH = (
    ROOT / "docs" / "plans" / "skillx" / "skillsbench-task-cluster-inputs-v0.1.jsonl"
)
DEFAULT_OUTPUT_DIR = DEFAULT_ROUND0_ROOT / "reports" / "outer-loop-schema-updates"
DEFAULT_ROUND_ID = "outer-loop-round0"
DEFAULT_NEXT_ROUND_ID = "outer-loop-round1"
DEFAULT_MIN_SUPPORT_SIZE = 2
DEFAULT_LOW_MARGIN_PP = 5.0
DEFAULT_BOUNDARY_MARGIN_PP = 10.0
DEFAULT_MAX_UPDATE_SCHEMAS = 3

SLOT_FIELDS = (
    "emphasize",
    "avoid",
    "expected_good_fit",
    "expected_bad_fit",
    "hypothesized_primary_failure_modes",
)


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
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        delimiter = ";" if ";" in value else ","
        items = value.split(delimiter)
    else:
        items = [value]
    normalized: list[str] = []
    for item in items:
        text = str(item).strip()
        if text and text.lower() != "none" and text not in normalized:
            normalized.append(text)
    return normalized


def load_prompt_bank(prompt_bank_path: Path) -> dict[str, Any]:
    payload = read_json(prompt_bank_path)
    categories = payload.get("categories")
    if not isinstance(categories, list):
        raise ValueError(f"prompt bank missing categories list: {prompt_bank_path}")
    return payload


def load_task_profiles(task_cluster_inputs_path: Path | None) -> dict[str, dict[str, Any]]:
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


def assignment_schema_ids(assignment: dict[str, Any]) -> list[str]:
    schema_ids: list[str] = []
    for key in (
        "assigned_categories",
        "assigned_schema_ids",
        "assigned_cluster_ids",
        "assigned_category",
        "assigned_schema_id",
    ):
        for schema_id in normalize_string_list(assignment.get(key)):
            if schema_id not in schema_ids:
                schema_ids.append(schema_id)
    if schema_ids:
        return schema_ids
    if assignment.get("assignment_status") != "assigned":
        return []
    return normalize_string_list(assignment.get("assigned_category"))


def score_value(row: dict[str, Any]) -> float | None:
    for key in ("score", "assignment_score_pct", "reported_score", "reported_score_pct"):
        value = coerce_float(row.get(key))
        if value is not None:
            return value
    return None


def score_rows_from_bundle(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    score_matrix = bundle.get("score_matrix") or {}
    long_rows = score_matrix.get("long_rows")
    if isinstance(long_rows, list) and long_rows:
        return [row for row in long_rows if isinstance(row, dict)]
    pair_rows = bundle.get("pair_rows")
    if isinstance(pair_rows, list):
        return [row for row in pair_rows if isinstance(row, dict)]
    return []


def index_score_rows(
    score_rows: list[dict[str, Any]],
) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, dict[str, float]]]:
    by_pair: dict[tuple[str, str], dict[str, Any]] = {}
    by_task_scores: dict[str, dict[str, float]] = defaultdict(dict)
    for row in score_rows:
        task_name = row.get("task_name")
        schema_id = row.get("schema_id")
        if not isinstance(task_name, str) or not isinstance(schema_id, str):
            continue
        by_pair[(task_name, schema_id)] = row
        value = score_value(row)
        if value is not None:
            by_task_scores[task_name][schema_id] = value
    return by_pair, by_task_scores


def sorted_task_scores(task_scores: dict[str, float]) -> list[dict[str, Any]]:
    rows = [
        {"schema_id": schema_id, "score": score}
        for schema_id, score in task_scores.items()
        if score is not None
    ]
    rows.sort(key=lambda row: (-float(row["score"]), str(row["schema_id"])))
    return rows


def classify_outcome(score_row: dict[str, Any]) -> str:
    score = score_value(score_row)
    if str(score_row.get("evidence_class") or "") in {"infra-blocked", "runtime-blocked"}:
        return "blocked"
    if score is None:
        return "missing"
    delta_vs_c1 = coerce_float(score_row.get("delta_vs_c1_pp"))
    has_runtime_issue = bool(score_row.get("timeout_flag")) or bool(
        score_row.get("has_intermediate_exceptions")
    )
    if delta_vs_c1 is not None:
        if delta_vs_c1 >= 5.0 and not has_runtime_issue:
            return "success"
        if delta_vs_c1 < 0:
            return "failure"
    if has_runtime_issue:
        return "mixed"
    if score >= 75.0:
        return "success"
    if score < 50.0:
        return "failure"
    return "mixed"


def numeric_mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(mean(values), 4)


def counter_summary(counter: Counter[str], limit: int = 5) -> list[dict[str, Any]]:
    return [
        {"value": value, "count": count}
        for value, count in counter.most_common(limit)
        if value
    ]


def build_schema_evidence(
    *,
    schema_id: str,
    assignments: list[dict[str, Any]],
    score_by_pair: dict[tuple[str, str], dict[str, Any]],
    scores_by_task: dict[str, dict[str, float]],
    task_profiles: dict[str, dict[str, Any]],
    low_margin_pp: float,
    boundary_margin_pp: float,
) -> dict[str, Any]:
    assigned_task_summaries: list[dict[str, Any]] = []
    profile_counters: dict[str, Counter[str]] = {
        "task_object_seed": Counter(),
        "verifier_mode": Counter(),
        "workflow_topology": Counter(),
        "tool_surface_regime": Counter(),
        "primary_pattern": Counter(),
    }
    outcome_counts: Counter[str] = Counter()
    failure_patterns: Counter[str] = Counter()
    score_values: list[float] = []
    delta_vs_c1_values: list[float] = []
    growth_values: list[float] = []
    assigned_task_names: set[str] = set()

    for assignment in assignments:
        task_name = assignment.get("task_name")
        if not isinstance(task_name, str):
            continue
        if schema_id not in assignment_schema_ids(assignment):
            continue
        assigned_task_names.add(task_name)
        score_row = score_by_pair.get((task_name, schema_id), {})
        score = score_value(score_row)
        outcome = classify_outcome(score_row)
        outcome_counts[outcome] += 1
        if score is not None:
            score_values.append(score)
        delta_vs_c1 = coerce_float(score_row.get("delta_vs_c1_pp"))
        if delta_vs_c1 is not None:
            delta_vs_c1_values.append(delta_vs_c1)
        growth = coerce_float(score_row.get("round_r0_to_best_delta_pp"))
        if growth is not None:
            growth_values.append(growth)
        profile = task_profiles.get(task_name, {})
        for key, counter in profile_counters.items():
            value = profile.get(key)
            if value:
                counter[str(value)] += 1

        failure_type = str(score_row.get("failure_type") or "").strip()
        failure_summary = str(score_row.get("failure_summary") or "").strip()
        if failure_type:
            failure_patterns[failure_type] += 1
        if outcome == "failure":
            failure_patterns["negative_or_low_score"] += 1
        if bool(score_row.get("timeout_flag")):
            failure_patterns["timeout"] += 1
        if bool(score_row.get("has_intermediate_exceptions")):
            failure_patterns["intermediate_exception"] += 1
        if growth is not None and growth <= 0:
            failure_patterns["stalled_or_regressed_round_curve"] += 1

        assigned_task_summaries.append(
            {
                "task_name": task_name,
                "score": score,
                "reported_score": coerce_float(
                    score_row.get("reported_score", score_row.get("reported_score_pct"))
                ),
                "delta_vs_c1_pp": delta_vs_c1,
                "round_r0_to_best_delta_pp": growth,
                "outcome": outcome,
                "assignment_confidence": assignment.get("assignment_confidence"),
                "margin_pp": assignment.get("margin_pp"),
                "main_failure_notes": [failure_summary] if failure_summary else [],
                "task_profile": profile,
            }
        )

    ambiguous_borderline_cases: list[dict[str, Any]] = []
    cross_schema_losses: list[dict[str, Any]] = []
    competitor_counter: Counter[str] = Counter()

    for task_name, task_scores in sorted(scores_by_task.items()):
        schema_score = task_scores.get(schema_id)
        if schema_score is None:
            continue
        ranked = sorted_task_scores(task_scores)
        if not ranked:
            continue
        best = ranked[0]
        second = ranked[1] if len(ranked) > 1 else None
        best_schema = str(best["schema_id"])
        best_score = float(best["score"])
        schema_is_best = best_schema == schema_id
        if schema_is_best and second is not None:
            margin = round(best_score - float(second["score"]), 4)
            if margin <= low_margin_pp:
                competitor = str(second["schema_id"])
                competitor_counter[competitor] += 1
                ambiguous_borderline_cases.append(
                    {
                        "task_name": task_name,
                        "case_type": "assigned_low_margin",
                        "current_schema_score": schema_score,
                        "competing_schema_id": competitor,
                        "competing_schema_score": second["score"],
                        "margin_pp": margin,
                    }
                )
        elif not schema_is_best:
            gap = round(best_score - float(schema_score), 4)
            if gap <= boundary_margin_pp:
                competitor_counter[best_schema] += 1
                ambiguous_borderline_cases.append(
                    {
                        "task_name": task_name,
                        "case_type": "near_boundary_loss",
                        "current_schema_score": schema_score,
                        "competing_schema_id": best_schema,
                        "competing_schema_score": best_score,
                        "margin_pp": gap,
                    }
                )
            if task_name in assigned_task_names or gap <= boundary_margin_pp:
                cross_schema_losses.append(
                    {
                        "task_name": task_name,
                        "won_by": best_schema,
                        "current_schema_score": schema_score,
                        "winning_score": best_score,
                        "gap_pp": gap,
                    }
                )

    low_margin_assigned_count = sum(
        1
        for row in assigned_task_summaries
        if coerce_float(row.get("margin_pp")) is not None
        and float(row["margin_pp"]) <= low_margin_pp
    )
    support_size = len(assigned_task_summaries)
    reliable_support_size = sum(
        1 for row in assigned_task_summaries if row["outcome"] not in {"blocked", "missing"}
    )
    stability_notes: list[str] = []
    if support_size == 0:
        stability_notes.append("no assigned tasks; freeze or inspect schema separately")
    if reliable_support_size < support_size:
        stability_notes.append("some assigned evidence is blocked or missing")
    if low_margin_assigned_count:
        stability_notes.append("assigned evidence contains low-margin boundary cases")
    if growth_values and numeric_mean(growth_values) is not None and numeric_mean(growth_values) <= 0:
        stability_notes.append("assigned round curves are flat or regressive on average")

    return {
        "category_id": schema_id,
        "support_size": support_size,
        "reliable_support_size": reliable_support_size,
        "assigned_task_summaries": assigned_task_summaries,
        "observed_task_count": sum(1 for scores in scores_by_task.values() if schema_id in scores),
        "mean_assigned_score": numeric_mean(score_values),
        "mean_delta_vs_c1_pp": numeric_mean(delta_vs_c1_values),
        "mean_r0_to_best_delta_pp": numeric_mean(growth_values),
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "main_failure_patterns": counter_summary(failure_patterns),
        "ambiguous_borderline_cases": ambiguous_borderline_cases,
        "cross_schema_losses": cross_schema_losses[:20],
        "main_borderline_competitors": counter_summary(competitor_counter),
        "task_profile_signals": {
            key: counter_summary(counter)
            for key, counter in profile_counters.items()
        },
        "stability_notes": stability_notes,
    }


def existing_text_set(schema: dict[str, Any]) -> set[str]:
    texts: set[str] = set()
    for field in SLOT_FIELDS:
        values = schema.get(field)
        if isinstance(values, list):
            texts.update(str(value).strip().lower() for value in values)
    return texts


def append_unique(edits: list[str], item: str, existing: set[str]) -> None:
    normalized = item.strip()
    if not normalized:
        return
    lowered = normalized.lower()
    if lowered in existing:
        return
    if normalized not in edits:
        edits.append(normalized)


def top_signal(evidence: dict[str, Any], key: str) -> str | None:
    signals = evidence.get("task_profile_signals", {}).get(key) or []
    if not signals:
        return None
    return str(signals[0]["value"])


def top_competitor(evidence: dict[str, Any]) -> str | None:
    competitors = evidence.get("main_borderline_competitors") or []
    if not competitors:
        return None
    return str(competitors[0]["value"])


def empty_slot_edits() -> dict[str, Any]:
    return {
        "emphasize": {"add": [], "remove": [], "sharpen": []},
        "avoid": {"add": [], "remove": [], "sharpen": []},
        "expected_good_fit": {"add": [], "remove": []},
        "expected_bad_fit": {"add": [], "remove": []},
        "hypothesized_primary_failure_modes": {"add": [], "remove": [], "sharpen": []},
    }


def propose_slot_edits(schema: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    edits = empty_slot_edits()
    existing = existing_text_set(schema)
    support_size = int(evidence["support_size"])
    reliable_support_size = int(evidence["reliable_support_size"])
    outcome_counts = Counter(evidence.get("outcome_counts") or {})
    low_margin_count = len(evidence.get("ambiguous_borderline_cases") or [])
    competitor = top_competitor(evidence)
    verifier_mode = top_signal(evidence, "verifier_mode")
    workflow_topology = top_signal(evidence, "workflow_topology")
    tool_surface_regime = top_signal(evidence, "tool_surface_regime")
    primary_pattern = top_signal(evidence, "primary_pattern")

    if reliable_support_size >= 2:
        append_unique(
            edits["emphasize"]["add"],
            "extract the task-specific failure mode before adding broader procedural scaffolding",
            existing,
        )
    if verifier_mode:
        append_unique(
            edits["expected_good_fit"]["add"],
            f"tasks with {verifier_mode} verifier behavior when the schema's workflow bias matches the task",
            existing,
        )
    if workflow_topology:
        append_unique(
            edits["emphasize"]["add"],
            f"make the {workflow_topology} workflow assumption explicit before rendering task-specific guidance",
            existing,
        )
    if tool_surface_regime and tool_surface_regime.startswith("tool-heavy"):
        append_unique(
            edits["emphasize"]["add"],
            "name the required execution and verification handoffs instead of leaving tool use implicit",
            existing,
        )
    if primary_pattern:
        append_unique(
            edits["expected_good_fit"]["add"],
            f"tasks whose dominant operational pattern is {primary_pattern}",
            existing,
        )

    if low_margin_count and competitor:
        append_unique(
            edits["emphasize"]["add"],
            f"state why this schema should win over {competitor} on borderline tasks",
            existing,
        )
        append_unique(
            edits["expected_bad_fit"]["add"],
            f"borderline tasks where {competitor} wins because its workflow bias is more central",
            existing,
        )
        append_unique(
            edits["hypothesized_primary_failure_modes"]["add"],
            f"low-margin schema-boundary ambiguity against {competitor}",
            existing,
        )

    if outcome_counts.get("failure", 0):
        append_unique(
            edits["avoid"]["add"],
            "generic schema broadening that hides negative lift against C1",
            existing,
        )
        append_unique(
            edits["hypothesized_primary_failure_modes"]["add"],
            "schema-task mismatch despite completed inner-loop execution",
            existing,
        )
    if outcome_counts.get("mixed", 0):
        append_unique(
            edits["avoid"]["add"],
            "treating runtime exceptions as usable positive evidence without an explicit caveat",
            existing,
        )
    failure_names = {
        str(item["value"])
        for item in evidence.get("main_failure_patterns", [])
        if isinstance(item, dict)
    }
    if "timeout" in failure_names:
        append_unique(
            edits["avoid"]["add"],
            "unbounded tool exploration without early-stop or checkpoint criteria",
            existing,
        )
    if "stalled_or_regressed_round_curve" in failure_names:
        append_unique(
            edits["emphasize"]["add"],
            "preserve R0 strengths and require regression checks after each refinement round",
            existing,
        )
        append_unique(
            edits["hypothesized_primary_failure_modes"]["add"],
            "round-level refinement regression after initially useful behavior",
            existing,
        )

    if support_size == 0:
        append_unique(
            edits["expected_bad_fit"]["add"],
            "do not infer schema updates from unassigned or infrastructure-corrupted rows",
            existing,
        )

    return edits


def summarize_edits(edits: dict[str, Any], schema: dict[str, Any]) -> dict[str, list[str]]:
    keep = [str(item) for item in schema.get("emphasize", [])[:2]]
    added: list[str] = []
    excluded: list[str] = []
    for slot_name, slot_payload in edits.items():
        for item in slot_payload.get("add", []):
            if slot_name == "expected_bad_fit":
                excluded.append(str(item))
            else:
                added.append(str(item))
    return {
        "keep": keep,
        "add": added[:8],
        "remove": [],
        "sharpen": [],
        "exclude": excluded[:5],
    }


def limited_adds(edits: dict[str, Any], mode: str, slot_name: str) -> list[str]:
    add_items = list(edits.get(slot_name, {}).get("add", []))
    if mode == "conservative":
        limits = {
            "emphasize": 2,
            "avoid": 1,
            "expected_good_fit": 1,
            "expected_bad_fit": 1,
            "hypothesized_primary_failure_modes": 1,
        }
        return add_items[: limits.get(slot_name, 1)]
    if mode == "differentiating":
        if slot_name in {"emphasize", "expected_bad_fit", "hypothesized_primary_failure_modes"}:
            boundary_items = [
                item for item in add_items if "borderline" in item or "schema-boundary" in item or "win over" in item
            ]
            return (boundary_items + add_items)[:3]
        return add_items[:1]
    return add_items[:4]


def apply_slot_edits(schema: dict[str, Any], edits: dict[str, Any], *, mode: str) -> dict[str, Any]:
    candidate = deepcopy(schema)
    for slot_name in SLOT_FIELDS:
        current = [str(item) for item in candidate.get(slot_name, []) if str(item).strip()]
        seen = {item.lower() for item in current}
        for item in limited_adds(edits, mode, slot_name):
            if item.lower() not in seen:
                current.append(item)
                seen.add(item.lower())
        if current:
            candidate[slot_name] = current
    candidate["meta_prompt"] = render_meta_prompt(candidate, mode=mode)
    return candidate


def render_meta_prompt(schema: dict[str, Any], *, mode: str) -> str:
    category_id = str(schema.get("category_id") or "unknown-schema")
    semantic_intent = str(schema.get("semantic_intent") or "").strip()
    lines = [
        f"You are revising a skill for a {category_id} task.",
    ]
    if semantic_intent:
        lines.append(f"Schema intent: {semantic_intent}")
    lines.extend(
        [
            "",
            f"Outer-loop update mode: {mode}. Keep the Render layer fixed and change only schema-level guidance.",
            "",
            "Prioritize:",
        ]
    )
    for idx, item in enumerate(schema.get("emphasize", []) or [], start=1):
        lines.append(f"{idx}. {item}")
    lines.extend(["", "Avoid:"])
    for idx, item in enumerate(schema.get("avoid", []) or [], start=1):
        lines.append(f"{idx}. {item}")
    good_fit = schema.get("expected_good_fit") or []
    if good_fit:
        lines.extend(["", "Good fit when:"])
        for item in good_fit:
            lines.append(f"- {item}")
    bad_fit = schema.get("expected_bad_fit") or []
    if bad_fit:
        lines.extend(["", "Bad fit when:"])
        for item in bad_fit:
            lines.append(f"- {item}")
    failure_modes = schema.get("hypothesized_primary_failure_modes") or []
    if failure_modes:
        lines.extend(["", "Primary failure modes to guard against:"])
        for item in failure_modes:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Regenerate task-specific skill guidance from these slots; do not invent a new policy outside them.",
        ]
    )
    return "\n".join(lines)


def schema_update_priority(evidence: dict[str, Any]) -> float:
    support = float(evidence.get("reliable_support_size") or 0)
    low_margin = float(len(evidence.get("ambiguous_borderline_cases") or []))
    failures = float((evidence.get("outcome_counts") or {}).get("failure", 0))
    mixed = float((evidence.get("outcome_counts") or {}).get("mixed", 0))
    mean_delta = coerce_float(evidence.get("mean_delta_vs_c1_pp"))
    negative_delta_bonus = abs(mean_delta) / 10.0 if mean_delta is not None and mean_delta < 0 else 0.0
    return round(support + 0.5 * low_margin + 0.75 * failures + 0.25 * mixed + negative_delta_bonus, 4)


def choose_challenger_mode(evidence: dict[str, Any]) -> str:
    outcome_counts = Counter(evidence.get("outcome_counts") or {})
    if evidence.get("main_borderline_competitors"):
        return "differentiating"
    if outcome_counts.get("failure", 0) > outcome_counts.get("success", 0):
        return "exploratory"
    return "conservative"


def build_schema_update_proposal(
    *,
    schema: dict[str, Any],
    evidence: dict[str, Any],
    min_support_size: int,
) -> dict[str, Any]:
    schema_id = str(schema["category_id"])
    edits = propose_slot_edits(schema, evidence)
    reliable_support_size = int(evidence["reliable_support_size"])
    if reliable_support_size < min_support_size:
        proposal_status = "freeze_low_support"
    elif not evidence.get("assigned_task_summaries"):
        proposal_status = "freeze_unassigned"
    else:
        proposal_status = "candidate_update"

    challengers: list[dict[str, Any]] = []
    for mode in ("conservative", "exploratory", "differentiating"):
        candidate_schema = apply_slot_edits(schema, edits, mode=mode)
        challengers.append(
            {
                "candidate_id": f"{schema_id}::round1::{mode}",
                "mode": mode,
                "schema": candidate_schema,
                "slot_edit_count": sum(
                    len(slot_payload.get("add", []))
                    for slot_payload in edits.values()
                ),
                "expected_effect": expected_effects(mode, evidence),
            }
        )

    selected_mode = choose_challenger_mode(evidence) if proposal_status == "candidate_update" else "incumbent"
    return {
        "category_id": schema_id,
        "proposal_status": proposal_status,
        "support_size": evidence["support_size"],
        "reliable_support_size": reliable_support_size,
        "mean_assigned_score": evidence["mean_assigned_score"],
        "mean_delta_vs_c1_pp": evidence["mean_delta_vs_c1_pp"],
        "priority_score": schema_update_priority(evidence),
        "recommended_challenger_mode": selected_mode,
        "operator_summary": summarize_edits(edits, schema),
        "slot_edits": edits,
        "challenger_schemas": challengers,
        "acceptance_notes": acceptance_notes(evidence, min_support_size),
    }


def expected_effects(mode: str, evidence: dict[str, Any]) -> list[str]:
    effects = [
        "preserve the frozen Render path while changing only schema-level guidance",
        "make the next rerun auditable against round-0 assigned tasks",
    ]
    if mode == "conservative":
        effects.append("test a low-risk local slot edit before broader schema search")
    elif mode == "exploratory":
        effects.append("expand the active meta-item pool for weak or negative-support schemas")
    else:
        competitor = top_competitor(evidence)
        if competitor:
            effects.append(f"increase behavioral separation from {competitor}")
        else:
            effects.append("increase schema distinctness on low-margin boundaries")
    return effects


def acceptance_notes(evidence: dict[str, Any], min_support_size: int) -> list[str]:
    notes = [
        "accept only after challenger rerun improves assigned-task utility or clarifies a boundary case",
        "reject if prompt text becomes more generic or less distinct from neighboring schemas",
    ]
    if int(evidence["reliable_support_size"]) < min_support_size:
        notes.append("below support floor; do not accept schema edits this round")
    if evidence.get("ambiguous_borderline_cases"):
        notes.append("evaluate on borderline tasks, not only primary assigned tasks")
    return notes


def select_round_updates(
    proposals: list[dict[str, Any]],
    *,
    max_update_schemas: int,
) -> list[dict[str, Any]]:
    eligible = [
        proposal
        for proposal in proposals
        if proposal["proposal_status"] == "candidate_update"
    ]
    eligible.sort(
        key=lambda proposal: (
            -float(proposal["priority_score"]),
            str(proposal["category_id"]),
        )
    )
    selected_ids = {
        proposal["category_id"]
        for proposal in (eligible if max_update_schemas <= 0 else eligible[:max_update_schemas])
    }
    plan: list[dict[str, Any]] = []
    for proposal in sorted(proposals, key=lambda item: str(item["category_id"])):
        category_id = str(proposal["category_id"])
        if category_id in selected_ids:
            action = "update"
            reason = "selected_by_priority"
        elif proposal["proposal_status"] != "candidate_update":
            action = "freeze"
            reason = proposal["proposal_status"]
        else:
            action = "defer"
            reason = "candidate_not_selected_this_round"
        plan.append(
            {
                "category_id": category_id,
                "action": action,
                "reason": reason,
                "priority_score": proposal["priority_score"],
                "recommended_challenger_mode": proposal["recommended_challenger_mode"],
                "support_size": proposal["support_size"],
                "reliable_support_size": proposal["reliable_support_size"],
            }
        )
    return plan


def candidate_for_mode(proposal: dict[str, Any], mode: str) -> dict[str, Any] | None:
    for candidate in proposal.get("challenger_schemas", []):
        if candidate.get("mode") == mode:
            return candidate
    return None


def build_candidate_prompt_bank(
    *,
    prompt_bank: dict[str, Any],
    proposals_by_schema: dict[str, dict[str, Any]],
    round_update_plan: list[dict[str, Any]],
    next_round_id: str,
) -> dict[str, Any]:
    selected_plan = {row["category_id"]: row for row in round_update_plan}
    candidate_bank = deepcopy(prompt_bank)
    candidate_bank["artifact_type"] = "skillx_prompt_bank_candidate"
    candidate_bank["source_artifact_type"] = prompt_bank.get("artifact_type")
    candidate_bank["version"] = f"{prompt_bank.get('version', 'v0.1')}+{next_round_id}"
    candidate_bank["status"] = "candidate; requires challenger rerun before acceptance"
    candidate_bank["outer_loop_update"] = {
        "next_round_id": next_round_id,
        "update_policy": "slot-first schema edits with frozen Render",
    }

    updated_categories: list[dict[str, Any]] = []
    for schema in candidate_bank.get("categories", []):
        schema_id = str(schema.get("category_id") or "")
        plan_row = selected_plan.get(schema_id)
        proposal = proposals_by_schema.get(schema_id)
        if not plan_row or not proposal or plan_row["action"] != "update":
            updated_categories.append(schema)
            continue
        mode = str(plan_row["recommended_challenger_mode"])
        candidate = candidate_for_mode(proposal, mode)
        if candidate is None:
            updated_categories.append(schema)
            continue
        replacement = deepcopy(candidate["schema"])
        replacement["outer_loop_candidate_id"] = candidate["candidate_id"]
        replacement["outer_loop_candidate_mode"] = mode
        replacement["outer_loop_candidate_status"] = "proposed_for_rerun"
        updated_categories.append(replacement)
    candidate_bank["categories"] = updated_categories
    return candidate_bank


def build_challenger_eval_plan(
    *,
    evidence_by_schema: dict[str, dict[str, Any]],
    round_update_plan: list[dict[str, Any]],
    max_tasks_per_schema: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for plan_row in round_update_plan:
        if plan_row["action"] != "update":
            continue
        schema_id = str(plan_row["category_id"])
        evidence = evidence_by_schema[schema_id]
        task_names: list[str] = []
        for task in evidence.get("assigned_task_summaries", []):
            name = str(task["task_name"])
            if name not in task_names:
                task_names.append(name)
        for case in evidence.get("ambiguous_borderline_cases", []):
            name = str(case["task_name"])
            if name not in task_names:
                task_names.append(name)
            if len(task_names) >= max_tasks_per_schema:
                break
        rows.append(
            {
                "schema_id": schema_id,
                "candidate_mode": plan_row["recommended_challenger_mode"],
                "task_names": task_names[:max_tasks_per_schema],
                "task_count": min(len(task_names), max_tasks_per_schema),
                "purpose": "evaluate assigned tasks plus low-margin boundary cases",
            }
        )
    return rows


def build_schema_update_package(
    *,
    control_plane_bundle_path: Path,
    prompt_bank_path: Path,
    task_cluster_inputs_path: Path | None,
    round_id: str,
    next_round_id: str,
    min_support_size: int,
    low_margin_pp: float,
    boundary_margin_pp: float,
    max_update_schemas: int,
    max_eval_tasks_per_schema: int,
) -> dict[str, Any]:
    bundle = read_json(control_plane_bundle_path)
    prompt_bank = load_prompt_bank(prompt_bank_path)
    task_profiles = load_task_profiles(task_cluster_inputs_path)
    schema_ids = [str(item["category_id"]) for item in prompt_bank["categories"]]
    assignments = [
        row for row in bundle.get("assignments", []) if isinstance(row, dict)
    ]
    score_rows = score_rows_from_bundle(bundle)
    score_by_pair, scores_by_task = index_score_rows(score_rows)

    evidence_by_schema: dict[str, dict[str, Any]] = {}
    proposals: list[dict[str, Any]] = []
    schema_by_id = {str(schema["category_id"]): schema for schema in prompt_bank["categories"]}
    for schema_id in schema_ids:
        evidence = build_schema_evidence(
            schema_id=schema_id,
            assignments=assignments,
            score_by_pair=score_by_pair,
            scores_by_task=scores_by_task,
            task_profiles=task_profiles,
            low_margin_pp=low_margin_pp,
            boundary_margin_pp=boundary_margin_pp,
        )
        evidence_by_schema[schema_id] = evidence
        proposals.append(
            build_schema_update_proposal(
                schema=schema_by_id[schema_id],
                evidence=evidence,
                min_support_size=min_support_size,
            )
        )

    round_update_plan = select_round_updates(
        proposals,
        max_update_schemas=max_update_schemas,
    )
    proposals_by_schema = {proposal["category_id"]: proposal for proposal in proposals}
    candidate_prompt_bank = build_candidate_prompt_bank(
        prompt_bank=prompt_bank,
        proposals_by_schema=proposals_by_schema,
        round_update_plan=round_update_plan,
        next_round_id=next_round_id,
    )
    challenger_eval_plan = build_challenger_eval_plan(
        evidence_by_schema=evidence_by_schema,
        round_update_plan=round_update_plan,
        max_tasks_per_schema=max_eval_tasks_per_schema,
    )

    return {
        "artifact_type": "skillx_outer_loop_schema_update_package",
        "version": "v0.1",
        "generated_at": timestamp(),
        "config": {
            "round_id": round_id,
            "next_round_id": next_round_id,
            "control_plane_bundle_path": display_path(control_plane_bundle_path.resolve()),
            "prompt_bank_path": display_path(prompt_bank_path.resolve()),
            "task_cluster_inputs_path": (
                None
                if task_cluster_inputs_path is None
                else display_path(task_cluster_inputs_path.resolve())
            ),
            "min_support_size": min_support_size,
            "low_margin_pp": low_margin_pp,
            "boundary_margin_pp": boundary_margin_pp,
            "max_update_schemas": max_update_schemas,
            "max_eval_tasks_per_schema": max_eval_tasks_per_schema,
        },
        "schema_ids": schema_ids,
        "schema_evidence_bundles": evidence_by_schema,
        "schema_update_proposals": proposals,
        "round_update_plan": round_update_plan,
        "challenger_eval_plan": challenger_eval_plan,
        "candidate_prompt_bank": candidate_prompt_bank,
    }


def render_summary_markdown(package: dict[str, Any], output_dir: Path) -> str:
    lines = [
        f"# SkillX Outer-Loop Schema Update Package: `{package['config']['round_id']}`",
        "",
        f"- generated_at: `{package['generated_at']}`",
        f"- output_dir: `{display_path(output_dir)}`",
        f"- next_round_id: `{package['config']['next_round_id']}`",
        f"- min_support_size: `{package['config']['min_support_size']}`",
        f"- max_update_schemas: `{package['config']['max_update_schemas']}`",
        "",
        "## Round Update Plan",
        "",
        "| schema_id | action | reason | support | reliable | priority | challenger |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in package["round_update_plan"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["category_id"]),
                    str(row["action"]),
                    str(row["reason"]),
                    str(row["support_size"]),
                    str(row["reliable_support_size"]),
                    f"{float(row['priority_score']):.2f}",
                    str(row["recommended_challenger_mode"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Evidence Summary", ""])
    for schema_id in package["schema_ids"]:
        evidence = package["schema_evidence_bundles"][schema_id]
        competitors = ", ".join(
            f"{item['value']} ({item['count']})"
            for item in evidence.get("main_borderline_competitors", [])[:3]
        ) or "none"
        lines.append(
            f"- `{schema_id}`: support=`{evidence['support_size']}`, "
            f"reliable=`{evidence['reliable_support_size']}`, "
            f"mean_score=`{evidence['mean_assigned_score']}`, "
            f"competitors=`{competitors}`"
        )

    lines.extend(["", "## Challenger Eval Plan", ""])
    for row in package["challenger_eval_plan"]:
        lines.append(
            f"- `{row['schema_id']}` / `{row['candidate_mode']}`: "
            f"{row['task_count']} task(s): `{', '.join(row['task_names'])}`"
        )
    return "\n".join(lines) + "\n"


def write_schema_update_package(*, package: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    package_json_path = output_dir / "schema_update_package.json"
    evidence_json_path = output_dir / "schema_evidence_bundles.json"
    proposals_json_path = output_dir / "schema_update_proposals.json"
    update_plan_json_path = output_dir / "round_update_plan.json"
    eval_plan_json_path = output_dir / "challenger_eval_plan.json"
    candidate_prompt_bank_path = output_dir / "round1_candidate_prompt_bank.json"
    summary_md_path = output_dir / "summary.md"
    update_plan_csv_path = output_dir / "round_update_plan.csv"

    write_json(package_json_path, package)
    write_json(evidence_json_path, package["schema_evidence_bundles"])
    write_json(proposals_json_path, package["schema_update_proposals"])
    write_json(update_plan_json_path, package["round_update_plan"])
    write_json(eval_plan_json_path, package["challenger_eval_plan"])
    write_json(candidate_prompt_bank_path, package["candidate_prompt_bank"])
    write_csv(
        update_plan_csv_path,
        package["round_update_plan"],
        [
            "category_id",
            "action",
            "reason",
            "priority_score",
            "recommended_challenger_mode",
            "support_size",
            "reliable_support_size",
        ],
    )
    summary_md_path.write_text(render_summary_markdown(package, output_dir))
    return {
        "schema_update_package_json": display_path(package_json_path),
        "schema_evidence_bundles_json": display_path(evidence_json_path),
        "schema_update_proposals_json": display_path(proposals_json_path),
        "round_update_plan_json": display_path(update_plan_json_path),
        "round_update_plan_csv": display_path(update_plan_csv_path),
        "challenger_eval_plan_json": display_path(eval_plan_json_path),
        "candidate_prompt_bank_json": display_path(candidate_prompt_bank_path),
        "summary_md": display_path(summary_md_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-plane-bundle-path", type=Path, default=DEFAULT_CONTROL_PLANE_BUNDLE_PATH)
    parser.add_argument("--prompt-bank-path", type=Path, default=DEFAULT_PROMPT_BANK_PATH)
    parser.add_argument("--task-cluster-inputs-path", type=Path, default=DEFAULT_TASK_CLUSTER_INPUTS_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--round-id", default=DEFAULT_ROUND_ID)
    parser.add_argument("--next-round-id", default=DEFAULT_NEXT_ROUND_ID)
    parser.add_argument("--min-support-size", type=int, default=DEFAULT_MIN_SUPPORT_SIZE)
    parser.add_argument("--low-margin-pp", type=float, default=DEFAULT_LOW_MARGIN_PP)
    parser.add_argument("--boundary-margin-pp", type=float, default=DEFAULT_BOUNDARY_MARGIN_PP)
    parser.add_argument("--max-update-schemas", type=int, default=DEFAULT_MAX_UPDATE_SCHEMAS)
    parser.add_argument("--max-eval-tasks-per-schema", type=int, default=6)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package = build_schema_update_package(
        control_plane_bundle_path=args.control_plane_bundle_path,
        prompt_bank_path=args.prompt_bank_path,
        task_cluster_inputs_path=args.task_cluster_inputs_path,
        round_id=str(args.round_id),
        next_round_id=str(args.next_round_id),
        min_support_size=int(args.min_support_size),
        low_margin_pp=float(args.low_margin_pp),
        boundary_margin_pp=float(args.boundary_margin_pp),
        max_update_schemas=int(args.max_update_schemas),
        max_eval_tasks_per_schema=int(args.max_eval_tasks_per_schema),
    )
    outputs = write_schema_update_package(package=package, output_dir=args.output_dir)
    print(json.dumps(outputs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

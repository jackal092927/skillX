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
import os
import subprocess
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Callable


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
DEFAULT_MIN_SUPPORT_SIZE = 0
DEFAULT_LOW_MARGIN_PP = 5.0
DEFAULT_BOUNDARY_MARGIN_PP = 10.0
DEFAULT_MAX_UPDATE_SCHEMAS = 0
DEFAULT_REWRITE_MODE = "llm"
DEFAULT_LLM_MODEL = "anthropic/claude-sonnet-4-5"
DEFAULT_LLM_TIMEOUT_SEC = 900.0

SLOT_FIELDS = (
    "emphasize",
    "avoid",
    "expected_good_fit",
    "expected_bad_fit",
    "hypothesized_primary_failure_modes",
)
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from runtime_guard import assert_supported_python_runtime  # noqa: E402

assert_supported_python_runtime()

from skillx.model_routing import resolve_cli_model_name, resolve_playbook_cli_name  # noqa: E402
from skillx.quota_signals import scan_payload  # noqa: E402

LLMJsonRunner = Callable[[str, dict[str, Any], str, Path, float], dict[str, Any]]
DEFAULT_FALLBACK_CLAUDE_CONFIG_DIR = Path.home() / ".claude-skillx-fallback"
CLAUDE_CLI_ACTIVE_PROFILE_INDEX = 0
CLAUDE_CLI_ACTIVE_PROFILE_KEY: tuple[str, ...] | None = None


def log_progress(message: str) -> None:
    print(f"[schema-update] {message}", file=sys.stderr, flush=True)


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


def split_env_paths(raw_value: str | None) -> list[Path]:
    if not raw_value:
        return []
    return [
        Path(item).expanduser()
        for item in raw_value.split(os.pathsep)
        if item.strip()
    ]


def comparable_path(path: Path | None) -> str | None:
    if path is None:
        return None
    expanded = path.expanduser()
    try:
        return str(expanded.resolve())
    except OSError:
        return str(expanded)


def claude_config_has_token(config_dir: Path) -> bool:
    return (config_dir.expanduser() / "claude-code-oauth-token").exists()


def claude_rate_limit_fallback_disabled() -> bool:
    for env_name in (
        "SKILLX_DISABLE_LLM_RATE_LIMIT_FALLBACK",
        "SKILLX_DISABLE_RATE_LIMIT_FALLBACK",
    ):
        value = os.environ.get(env_name, "").strip().lower()
        if value in {"1", "true", "yes"}:
            return True
    return False


def claude_cli_runtime_profiles() -> list[dict[str, Any]]:
    primary_config_raw = (
        os.environ.get("SKILLX_LLM_CLAUDE_CONFIG_DIR")
        or os.environ.get("CLAUDE_CONFIG_DIR")
    )
    primary_config_dir = Path(primary_config_raw).expanduser() if primary_config_raw else None
    profiles: list[dict[str, Any]] = [
        {
            "index": 0,
            "label": "primary-claude",
            "config_dir": primary_config_dir,
            "source": (
                "env"
                if primary_config_raw
                else "default-claude-config"
            ),
        }
    ]
    if claude_rate_limit_fallback_disabled():
        return profiles

    fallback_dirs: list[Path] = []
    fallback_dirs.extend(split_env_paths(os.environ.get("SKILLX_LLM_FALLBACK_CLAUDE_CONFIG_DIRS")))
    fallback_dirs.extend(split_env_paths(os.environ.get("SKILLX_LLM_FALLBACK_CLAUDE_CONFIG_DIR")))
    fallback_dirs.extend(split_env_paths(os.environ.get("SKILLX_FALLBACK_CLAUDE_CONFIG_DIR")))
    fallback_oauth = (
        os.environ.get("SKILLX_LLM_FALLBACK_CLAUDE_OAUTH_FILE")
        or os.environ.get("SKILLX_FALLBACK_CLAUDE_OAUTH_FILE")
    )
    if fallback_oauth:
        fallback_dirs.append(Path(fallback_oauth).expanduser().parent)
    if DEFAULT_FALLBACK_CLAUDE_CONFIG_DIR.exists():
        fallback_dirs.append(DEFAULT_FALLBACK_CLAUDE_CONFIG_DIR)

    seen: set[str] = {
        comparable_path(primary_config_dir) or comparable_path(Path.home() / ".claude") or ""
    }
    for config_dir in fallback_dirs:
        key = comparable_path(config_dir)
        if not key or key in seen:
            continue
        seen.add(key)
        if not config_dir.expanduser().exists() or not claude_config_has_token(config_dir):
            continue
        profiles.append(
            {
                "index": len(profiles),
                "label": f"fallback-claude-{len(profiles)}",
                "config_dir": config_dir.expanduser(),
                "source": "fallback-config-dir",
            }
        )
    return profiles


def claude_profile_key(profile: dict[str, Any]) -> str:
    config_dir = profile.get("config_dir")
    return f"{profile.get('label')}:{comparable_path(config_dir) if config_dir is not None else 'default'}"


def ordered_claude_cli_runtime_profiles() -> list[dict[str, Any]]:
    global CLAUDE_CLI_ACTIVE_PROFILE_INDEX
    global CLAUDE_CLI_ACTIVE_PROFILE_KEY
    profiles = claude_cli_runtime_profiles()
    profile_key = tuple(claude_profile_key(profile) for profile in profiles)
    if profile_key != CLAUDE_CLI_ACTIVE_PROFILE_KEY:
        CLAUDE_CLI_ACTIVE_PROFILE_KEY = profile_key
        CLAUDE_CLI_ACTIVE_PROFILE_INDEX = 0
    start_index = min(CLAUDE_CLI_ACTIVE_PROFILE_INDEX, max(len(profiles) - 1, 0))
    return profiles[start_index:]


def remember_claude_cli_profile(profile: dict[str, Any]) -> None:
    global CLAUDE_CLI_ACTIVE_PROFILE_INDEX
    CLAUDE_CLI_ACTIVE_PROFILE_INDEX = int(profile.get("index") or 0)


def llm_runtime_profile_summary(model_name: str) -> list[dict[str, Any]]:
    if resolve_playbook_cli_name(model_name) != "claude":
        return [
            {
                "index": 0,
                "label": "codex",
                "cli": "codex",
                "config_dir": None,
                "source": "model-routing",
            }
        ]
    return [
        {
            "index": int(profile["index"]),
            "label": str(profile["label"]),
            "cli": "claude",
            "config_dir": (
                None
                if profile.get("config_dir") is None
                else str(Path(profile["config_dir"]).expanduser())
            ),
            "source": profile.get("source"),
        }
        for profile in claude_cli_runtime_profiles()
    ]


def cli_quota_signal(*, stdout: str, stderr: str, returncode: int | None) -> dict[str, Any]:
    text = "\n".join(part for part in (stdout, stderr) if part)
    return scan_payload(
        {
            "type": "error",
            "returncode": returncode,
            "message": text,
        }
    )


def sanitized_profile_label(label: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in label).strip("-") or "profile"


def command_for_record(command: list[str], profile: dict[str, Any]) -> str:
    config_dir = profile.get("config_dir")
    prefix = ""
    if config_dir is not None:
        prefix = f"CLAUDE_CONFIG_DIR={Path(config_dir).expanduser()} "
    return prefix + " ".join(command)


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


def training_evidence_rows_from_bundle(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """Return schema-level training evidence rows, falling back to legacy assignments."""
    diagnostics = bundle.get("diagnostics") or {}
    rows = diagnostics.get("schema_training_assignments")
    if isinstance(rows, list) and rows:
        return [row for row in rows if isinstance(row, dict)]

    rows = bundle.get("schema_training_assignments")
    if isinstance(rows, list) and rows:
        return [row for row in rows if isinstance(row, dict)]

    fallback_rows: list[dict[str, Any]] = []
    for assignment in bundle.get("assignments", []) or []:
        if not isinstance(assignment, dict):
            continue
        task_name = assignment.get("task_name")
        if not isinstance(task_name, str):
            continue
        for schema_id in assignment_schema_ids(assignment):
            fallback_rows.append(
                {
                    "schema_id": schema_id,
                    "task_name": task_name,
                    "evidence_role": "assignment_support",
                    "evidence_reasons": "legacy_assignment",
                    "primary_assigned_category": assignment.get("assigned_category"),
                }
            )
    return fallback_rows


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


def default_update_decision(schema_ids: list[str]) -> dict[str, Any]:
    return {
        "artifact_type": "skillx_outer_loop_update_decision",
        "version": "v0.1",
        "global_update_mode": "rewrite",
        "mode_reason": "no outer-loop update decision supplied",
        "scorecard": {},
        "positive_transfer_pairs": [],
        "protected_regression_pairs": [],
        "schema_decisions": {
            schema_id: {
                "schema_id": schema_id,
                "update_mode": "rewrite",
                "reason": "default rewrite mode",
                "positive_transfer_count": 0,
                "protected_regression_count": 0,
                "positive_transfer_pairs": [],
                "protected_regression_pairs": [],
                "allowed_patch_scope": [],
                "blocked_regression_patterns": [],
            }
            for schema_id in schema_ids
        },
    }


def schema_update_decision(update_decision: dict[str, Any], schema_id: str) -> dict[str, Any]:
    schema_decisions = update_decision.get("schema_decisions")
    if isinstance(schema_decisions, dict):
        decision = schema_decisions.get(schema_id)
        if isinstance(decision, dict):
            return decision
    global_mode = str(update_decision.get("global_update_mode") or "rewrite")
    return {
        "schema_id": schema_id,
        "update_mode": global_mode,
        "reason": str(update_decision.get("mode_reason") or "global update decision"),
        "positive_transfer_count": 0,
        "protected_regression_count": 0,
        "positive_transfer_pairs": [],
        "protected_regression_pairs": [],
        "allowed_patch_scope": [],
        "blocked_regression_patterns": [],
    }


def attach_update_decision_evidence(
    evidence: dict[str, Any],
    *,
    update_decision: dict[str, Any],
) -> dict[str, Any]:
    schema_id = str(evidence["category_id"])
    decision = schema_update_decision(update_decision, schema_id)
    enriched = dict(evidence)
    enriched["outer_loop_global_update_mode"] = str(update_decision.get("global_update_mode") or "rewrite")
    enriched["outer_loop_global_update_reason"] = str(update_decision.get("mode_reason") or "")
    enriched["outer_loop_update_mode"] = str(decision.get("update_mode") or "rewrite")
    enriched["outer_loop_update_reason"] = str(decision.get("reason") or "")
    enriched["positive_transfer_pairs"] = [
        row for row in decision.get("positive_transfer_pairs") or [] if isinstance(row, dict)
    ]
    enriched["protected_regression_pairs"] = [
        row for row in decision.get("protected_regression_pairs") or [] if isinstance(row, dict)
    ]
    enriched["allowed_patch_scope"] = normalize_string_list(decision.get("allowed_patch_scope"))
    enriched["blocked_regression_patterns"] = normalize_string_list(decision.get("blocked_regression_patterns"))
    return enriched


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
    training_evidence_rows: list[dict[str, Any]],
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
    assignments_by_task = {
        str(row.get("task_name")): row
        for row in assignments
        if isinstance(row.get("task_name"), str)
    }
    seen_support_keys: set[tuple[str, str]] = set()

    for support_row in training_evidence_rows:
        if str(support_row.get("schema_id") or "") != schema_id:
            continue
        task_name = support_row.get("task_name")
        if not isinstance(task_name, str):
            continue
        support_key = (schema_id, task_name)
        if support_key in seen_support_keys:
            continue
        seen_support_keys.add(support_key)
        assigned_task_names.add(task_name)
        assignment = assignments_by_task.get(task_name, {})
        score_row = dict(score_by_pair.get((task_name, schema_id), {}))
        if score_value(score_row) is None:
            score_row["score"] = support_row.get("schema_score")
        if coerce_float(score_row.get("reported_score")) is None:
            score_row["reported_score"] = support_row.get("schema_reported_score")
        if coerce_float(score_row.get("round_r0_to_best_delta_pp")) is None:
            score_row["round_r0_to_best_delta_pp"] = support_row.get(
                "schema_delta_vs_r0_post_best_pp"
            )
        if not score_row.get("trajectory_quality"):
            score_row["trajectory_quality"] = support_row.get("schema_trajectory_quality")
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
                "evidence_role": str(support_row.get("evidence_role") or "assignment_support"),
                "evidence_reasons": normalize_string_list(support_row.get("evidence_reasons")),
                "schema_rank_for_task": coerce_float(support_row.get("schema_rank_for_task")),
                "schema_trajectory_quality": support_row.get("schema_trajectory_quality")
                or score_row.get("trajectory_quality"),
                "primary_assigned_category": support_row.get("primary_assigned_category")
                or assignment.get("assigned_category"),
                "task_best_schema": support_row.get("task_best_schema"),
                "task_best_score": coerce_float(support_row.get("task_best_score")),
                "floor_evidence": str(support_row.get("evidence_role") or "") == "floor_top_score",
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


def normalize_slot_edits(value: Any) -> dict[str, Any]:
    normalized = empty_slot_edits()
    if not isinstance(value, dict):
        return normalized
    for slot_name in SLOT_FIELDS:
        slot_payload = value.get(slot_name)
        if not isinstance(slot_payload, dict):
            continue
        normalized[slot_name]["add"] = normalize_string_list(slot_payload.get("add"))
        normalized[slot_name]["remove"] = normalize_string_list(slot_payload.get("remove"))
        sharpen_payload = slot_payload.get("sharpen")
        sharpen_rows: list[dict[str, str]] = []
        if isinstance(sharpen_payload, list):
            for item in sharpen_payload:
                if not isinstance(item, dict):
                    continue
                old = str(item.get("old") or "").strip()
                new = str(item.get("new") or "").strip()
                if old and new:
                    sharpen_rows.append({"old": old, "new": new})
        if slot_name in {"expected_good_fit", "expected_bad_fit"}:
            normalized[slot_name].pop("sharpen", None)
        else:
            normalized[slot_name]["sharpen"] = sharpen_rows
    return normalized


def normalize_operator_summary(value: Any, schema: dict[str, Any]) -> dict[str, list[str]]:
    fallback = {
        "keep": [str(item) for item in schema.get("emphasize", [])[:2]],
        "add": [],
        "remove": [],
        "sharpen": [],
        "exclude": [],
    }
    if not isinstance(value, dict):
        return fallback
    return {
        "keep": normalize_string_list(value.get("keep")) or fallback["keep"],
        "add": normalize_string_list(value.get("add")),
        "remove": normalize_string_list(value.get("remove")),
        "sharpen": normalize_string_list(value.get("sharpen")),
        "exclude": normalize_string_list(value.get("exclude")),
    }


def propose_slot_edits(schema: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    edits = empty_slot_edits()
    existing = existing_text_set(schema)
    support_size = int(evidence["support_size"])
    reliable_support_size = int(evidence["reliable_support_size"])
    outer_loop_update_mode = str(evidence.get("outer_loop_update_mode") or "rewrite")
    positive_transfer_count = len(evidence.get("positive_transfer_pairs") or [])
    protected_regression_count = len(evidence.get("protected_regression_pairs") or [])
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
    if outer_loop_update_mode == "guarded_patch":
        append_unique(
            edits["emphasize"]["add"],
            "limit this update to narrow evidence-backed patches against the stable base schema",
            existing,
        )
    if positive_transfer_count:
        append_unique(
            edits["expected_good_fit"]["add"],
            "task patterns matching positive-transfer evidence from the candidate outer-loop round",
            existing,
        )
    if protected_regression_count:
        append_unique(
            edits["avoid"]["add"],
            "schema broadening that regresses previously stable task-schema behavior",
            existing,
        )
        append_unique(
            edits["hypothesized_primary_failure_modes"]["add"],
            "outer-loop candidate regression on protected prior-success tasks",
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


def llm_update_json_schema() -> dict[str, Any]:
    slot_with_sharpen = {
        "type": "object",
        "properties": {
            "add": {"type": "array", "items": {"type": "string"}},
            "remove": {"type": "array", "items": {"type": "string"}},
            "sharpen": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "old": {"type": "string"},
                        "new": {"type": "string"},
                    },
                    "required": ["old", "new"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["add", "remove", "sharpen"],
        "additionalProperties": False,
    }
    slot_without_sharpen = {
        "type": "object",
        "properties": {
            "add": {"type": "array", "items": {"type": "string"}},
            "remove": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["add", "remove"],
        "additionalProperties": False,
    }
    string_array = {"type": "array", "items": {"type": "string"}}
    return {
        "type": "object",
        "properties": {
            "operator_summary": {
                "type": "object",
                "properties": {
                    "keep": string_array,
                    "add": string_array,
                    "remove": string_array,
                    "sharpen": string_array,
                    "exclude": string_array,
                },
                "required": ["keep", "add", "remove", "sharpen", "exclude"],
                "additionalProperties": False,
            },
            "slot_edits": {
                "type": "object",
                "properties": {
                    "emphasize": slot_with_sharpen,
                    "avoid": slot_with_sharpen,
                    "expected_good_fit": slot_without_sharpen,
                    "expected_bad_fit": slot_without_sharpen,
                    "hypothesized_primary_failure_modes": slot_with_sharpen,
                },
                "required": list(SLOT_FIELDS),
                "additionalProperties": False,
            },
            "challenger_guidance": {
                "type": "object",
                "properties": {
                    "conservative": {"type": "string"},
                    "exploratory": {"type": "string"},
                    "differentiating": {"type": "string"},
                },
                "required": ["conservative", "exploratory", "differentiating"],
                "additionalProperties": False,
            },
            "expected_effect": string_array,
            "acceptance_notes": string_array,
        },
        "required": [
            "operator_summary",
            "slot_edits",
            "challenger_guidance",
            "expected_effect",
            "acceptance_notes",
        ],
        "additionalProperties": False,
    }


def build_llm_update_prompt(
    *,
    schema: dict[str, Any],
    evidence: dict[str, Any],
    deterministic_edits: dict[str, Any],
) -> str:
    update_mode = str(evidence.get("outer_loop_update_mode") or "rewrite")
    compact_evidence = {
        "category_id": evidence["category_id"],
        "outer_loop_global_update_mode": evidence.get("outer_loop_global_update_mode"),
        "outer_loop_global_update_reason": evidence.get("outer_loop_global_update_reason"),
        "outer_loop_update_mode": update_mode,
        "outer_loop_update_reason": evidence.get("outer_loop_update_reason"),
        "support_size": evidence["support_size"],
        "reliable_support_size": evidence["reliable_support_size"],
        "mean_assigned_score": evidence["mean_assigned_score"],
        "mean_delta_vs_c1_pp": evidence["mean_delta_vs_c1_pp"],
        "mean_r0_to_best_delta_pp": evidence["mean_r0_to_best_delta_pp"],
        "outcome_counts": evidence["outcome_counts"],
        "main_failure_patterns": evidence["main_failure_patterns"],
        "main_borderline_competitors": evidence["main_borderline_competitors"],
        "task_profile_signals": evidence["task_profile_signals"],
        "stability_notes": evidence["stability_notes"],
        "assigned_task_summaries": evidence["assigned_task_summaries"][:8],
        "ambiguous_borderline_cases": evidence["ambiguous_borderline_cases"][:12],
        "cross_schema_losses": evidence["cross_schema_losses"][:12],
        "positive_transfer_pairs": (evidence.get("positive_transfer_pairs") or [])[:12],
        "protected_regression_pairs": (evidence.get("protected_regression_pairs") or [])[:12],
        "allowed_patch_scope": evidence.get("allowed_patch_scope") or [],
        "blocked_regression_patterns": evidence.get("blocked_regression_patterns") or [],
    }
    mode_rules = [
        f"- Current outer-loop update mode is `{update_mode}`.",
    ]
    if update_mode == "guarded_patch":
        mode_rules.extend(
            [
                "- Treat CURRENT_SCHEMA as the stable base, not as a failed artifact to replace.",
                "- Make the smallest patch that explains positive_transfer_pairs.",
                "- Do not broaden the schema from globally regressed evidence.",
                "- Turn protected_regression_pairs into explicit avoid/failure-mode guardrails.",
                "- Prefer add/sharpen operations; remove only if an incumbent item directly caused a protected regression.",
            ]
        )
    elif update_mode == "hold":
        mode_rules.extend(
            [
                "- Do not invent a rewrite when the update decision says hold.",
                "- Preserve the stable base schema and use the evidence only as acceptance-risk notes.",
            ]
        )
    else:
        mode_rules.append("- A full evidence-grounded slot rewrite is allowed.")
    return (
        "You are the SkillX outer-loop schema update operator.\n"
        "Update the schema as structured operations, not as a final accepted prompt bank.\n\n"
        "Rules:\n"
        "- Use evidence-grounded operations only.\n"
        "- Prefer slot-level operations over free-form prompt rewriting.\n"
        "- You may add, remove, and sharpen items when evidence supports it.\n"
        "- Do not remove a useful incumbent item unless it is redundant, harmful, or contradicted by evidence.\n"
        "- Keep Render frozen; optimize only the schema-level guidance.\n"
        "- Preserve schema distinctness and explicitly handle low-margin competitors.\n"
        "- Output strictly valid JSON matching the provided schema.\n\n"
        "Update-mode rules:\n"
        + "\n".join(mode_rules)
        + "\n\n"
        f"CURRENT_SCHEMA:\n{json.dumps(schema, indent=2, sort_keys=True)}\n\n"
        f"EVIDENCE_BUNDLE:\n{json.dumps(compact_evidence, indent=2, sort_keys=True)}\n\n"
        "DETERMINISTIC_SEED_EDITS_FOR_REFERENCE_ONLY:\n"
        f"{json.dumps(deterministic_edits, indent=2, sort_keys=True)}\n"
    )


def run_llm_json_prompt(
    prompt: str,
    response_schema: dict[str, Any],
    model_name: str,
    output_dir: Path,
    timeout_sec: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    schema_path = output_dir / "response_schema.json"
    prompt_path = output_dir / "prompt.txt"
    stdout_path = output_dir / "stdout.json"
    stderr_path = output_dir / "stderr.txt"
    last_message_path = output_dir / "last_message.json"
    command_path = output_dir / "command.txt"
    attempts_path = output_dir / "attempts.json"
    schema_path.write_text(json.dumps(response_schema, indent=2, sort_keys=True) + "\n")
    prompt_path.write_text(prompt + "\n")

    cli_name = resolve_playbook_cli_name(model_name)
    cli_model_name = resolve_cli_model_name(model_name)
    if cli_name == "claude":
        command = [
            "claude",
            "--print",
            "--dangerously-skip-permissions",
            "--output-format",
            "json",
            "--model",
            cli_model_name,
            "--json-schema",
            json.dumps(response_schema, separators=(",", ":")),
        ]
    else:
        command = [
            "codex",
            "exec",
            "--dangerously-bypass-approvals-and-sandbox",
            "--skip-git-repo-check",
            "--json",
            "--model",
            cli_model_name,
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(last_message_path),
            "--",
        ]
    profiles = ordered_claude_cli_runtime_profiles() if cli_name == "claude" else [
        {"index": 0, "label": "codex", "config_dir": None, "source": "model-routing"}
    ]
    attempt_records: list[dict[str, Any]] = []
    last_error: Exception | None = None

    for attempt_index, profile in enumerate(profiles, start=1):
        profile_label = str(profile["label"])
        attempt_dir = output_dir / "attempts" / f"{attempt_index:02d}-{sanitized_profile_label(profile_label)}"
        attempt_dir.mkdir(parents=True, exist_ok=True)
        attempt_stdout_path = attempt_dir / "stdout.json"
        attempt_stderr_path = attempt_dir / "stderr.txt"
        attempt_last_message_path = attempt_dir / "last_message.json"
        attempt_command_path = attempt_dir / "command.txt"
        attempt_env = os.environ.copy()
        if cli_name == "claude":
            config_dir = profile.get("config_dir")
            if config_dir is None:
                attempt_env.pop("CLAUDE_CONFIG_DIR", None)
            else:
                attempt_env["CLAUDE_CONFIG_DIR"] = str(Path(config_dir).expanduser())
        attempt_command_path.write_text(command_for_record(command, profile) + "\n")
        command_path.write_text(command_for_record(command, profile) + "\n")

        proc = subprocess.run(
            command,
            cwd=str(ROOT),
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            env=attempt_env,
        )
        stdout_text = proc.stdout or ""
        stderr_text = proc.stderr or ""
        attempt_stdout_path.write_text(stdout_text)
        attempt_stderr_path.write_text(stderr_text)
        stdout_path.write_text(stdout_text)
        stderr_path.write_text(stderr_text)
        quota_signal = cli_quota_signal(
            stdout=stdout_text,
            stderr=stderr_text,
            returncode=int(proc.returncode),
        )
        attempt_record = {
            "attempt": attempt_index,
            "profile": {
                "index": int(profile["index"]),
                "label": profile_label,
                "cli": cli_name,
                "config_dir": (
                    None
                    if profile.get("config_dir") is None
                    else str(Path(profile["config_dir"]).expanduser())
                ),
                "source": profile.get("source"),
            },
            "returncode": int(proc.returncode),
            "quota_signal_level": quota_signal.get("signal_level"),
            "quota_hard_terms": quota_signal.get("hard_terms") or [],
            "stdout_path": str(attempt_stdout_path),
            "stderr_path": str(attempt_stderr_path),
        }

        if proc.returncode != 0:
            attempt_record["status"] = "hard_rate_limit" if quota_signal.get("has_hard_signal") else "failed"
            attempt_record["quota_signal"] = quota_signal
            attempt_records.append(attempt_record)
            write_json(attempts_path, {"attempts": attempt_records})
            if cli_name == "claude" and quota_signal.get("has_hard_signal") and attempt_index < len(profiles):
                log_progress(
                    "LLM rewrite rate/quota fallback: "
                    f"{profile_label} -> {profiles[attempt_index]['label']} "
                    f"terms={','.join(str(item) for item in quota_signal.get('hard_terms') or [])}"
                )
                remember_claude_cli_profile(profiles[attempt_index])
                continue
            last_error = RuntimeError(
                f"LLM rewrite failed with exit code {proc.returncode}; see {stderr_path}"
            )
            break

        try:
            if cli_name == "claude":
                payload = json.loads(stdout_text)
                structured_output = payload.get("structured_output")
                if not isinstance(structured_output, dict):
                    raise ValueError(f"Claude output missing structured_output: {stdout_path}")
                write_json(attempt_last_message_path, structured_output)
                write_json(last_message_path, structured_output)
                attempt_record["status"] = "succeeded"
                attempt_records.append(attempt_record)
                write_json(attempts_path, {"attempts": attempt_records})
                return structured_output
            if not last_message_path.exists():
                raise ValueError(f"Codex output missing last message: {last_message_path}")
            structured_output = read_json(last_message_path)
            attempt_record["status"] = "succeeded"
            attempt_records.append(attempt_record)
            write_json(attempts_path, {"attempts": attempt_records})
            return structured_output
        except (json.JSONDecodeError, ValueError) as exc:
            quota_signal = cli_quota_signal(
                stdout=stdout_text,
                stderr=stderr_text,
                returncode=int(proc.returncode),
            )
            attempt_record["status"] = (
                "hard_rate_limit_parse_failure"
                if quota_signal.get("has_hard_signal")
                else "parse_failed"
            )
            attempt_record["quota_signal"] = quota_signal
            attempt_records.append(attempt_record)
            write_json(attempts_path, {"attempts": attempt_records})
            if cli_name == "claude" and quota_signal.get("has_hard_signal") and attempt_index < len(profiles):
                log_progress(
                    "LLM rewrite rate/quota fallback after parse failure: "
                    f"{profile_label} -> {profiles[attempt_index]['label']}"
                )
                remember_claude_cli_profile(profiles[attempt_index])
                continue
            last_error = exc
            break

    if last_error is not None:
        raise last_error
    raise RuntimeError(f"LLM rewrite failed without a completed attempt; see {output_dir}")


def propose_llm_slot_edits(
    *,
    schema: dict[str, Any],
    evidence: dict[str, Any],
    deterministic_edits: dict[str, Any],
    llm_model: str,
    llm_timeout_sec: float,
    llm_work_dir: Path,
    llm_json_runner: LLMJsonRunner | None,
) -> dict[str, Any]:
    response_schema = llm_update_json_schema()
    prompt = build_llm_update_prompt(
        schema=schema,
        evidence=evidence,
        deterministic_edits=deterministic_edits,
    )
    runner = llm_json_runner or run_llm_json_prompt
    payload = runner(prompt, response_schema, llm_model, llm_work_dir, llm_timeout_sec)
    return {
        "operator_summary": normalize_operator_summary(payload.get("operator_summary"), schema),
        "slot_edits": normalize_slot_edits(payload.get("slot_edits")),
        "challenger_guidance": {
            "conservative": str((payload.get("challenger_guidance") or {}).get("conservative") or ""),
            "exploratory": str((payload.get("challenger_guidance") or {}).get("exploratory") or ""),
            "differentiating": str((payload.get("challenger_guidance") or {}).get("differentiating") or ""),
        },
        "expected_effect": normalize_string_list(payload.get("expected_effect")),
        "acceptance_notes": normalize_string_list(payload.get("acceptance_notes")),
    }


def summarize_edits(edits: dict[str, Any], schema: dict[str, Any]) -> dict[str, list[str]]:
    keep = [str(item) for item in schema.get("emphasize", [])[:2]]
    added: list[str] = []
    removed: list[str] = []
    sharpened: list[str] = []
    excluded: list[str] = []
    for slot_name, slot_payload in edits.items():
        for item in slot_payload.get("add", []):
            if slot_name == "expected_bad_fit":
                excluded.append(str(item))
            else:
                added.append(str(item))
        for item in slot_payload.get("remove", []):
            removed.append(str(item))
        for item in slot_payload.get("sharpen", []):
            if isinstance(item, dict):
                sharpened.append(f"{item.get('old')} -> {item.get('new')}")
    return {
        "keep": keep,
        "add": added[:8],
        "remove": removed[:8],
        "sharpen": sharpened[:8],
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


def limited_removes(edits: dict[str, Any], mode: str, slot_name: str) -> list[str]:
    remove_items = list(edits.get(slot_name, {}).get("remove", []))
    if mode == "conservative":
        return remove_items[:1]
    if mode == "differentiating":
        return remove_items[:2]
    return remove_items[:3]


def limited_sharpens(edits: dict[str, Any], mode: str, slot_name: str) -> list[dict[str, str]]:
    sharpen_items = [
        item
        for item in edits.get(slot_name, {}).get("sharpen", [])
        if isinstance(item, dict) and item.get("old") and item.get("new")
    ]
    if mode == "conservative":
        return sharpen_items[:1]
    if mode == "differentiating":
        return sharpen_items[:3]
    return sharpen_items[:4]


def apply_slot_operations(
    current_items: list[str],
    *,
    remove_items: list[str],
    sharpen_items: list[dict[str, str]],
    add_items: list[str],
    allow_add_when_sharpen_old_missing: bool,
) -> list[str]:
    current = [str(item) for item in current_items if str(item).strip()]
    remove_lookup = {item.strip().lower() for item in remove_items if item.strip()}
    if remove_lookup:
        current = [item for item in current if item.strip().lower() not in remove_lookup]

    for sharpen in sharpen_items:
        old = str(sharpen.get("old") or "").strip()
        new = str(sharpen.get("new") or "").strip()
        if not old or not new:
            continue
        replaced = False
        for idx, item in enumerate(current):
            if item.strip().lower() == old.lower():
                current[idx] = new
                replaced = True
                break
        if not replaced and allow_add_when_sharpen_old_missing:
            current.append(new)

    seen = {item.lower() for item in current}
    for item in add_items:
        text = str(item).strip()
        if text and text.lower() not in seen:
            current.append(text)
            seen.add(text.lower())
    return current


def apply_slot_edits(schema: dict[str, Any], edits: dict[str, Any], *, mode: str) -> dict[str, Any]:
    candidate = deepcopy(schema)
    for slot_name in SLOT_FIELDS:
        current = apply_slot_operations(
            [str(item) for item in candidate.get(slot_name, []) if str(item).strip()],
            remove_items=limited_removes(edits, mode, slot_name),
            sharpen_items=limited_sharpens(edits, mode, slot_name),
            add_items=limited_adds(edits, mode, slot_name),
            allow_add_when_sharpen_old_missing=mode != "conservative",
        )
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
    rewrite_mode: str,
    llm_model: str,
    llm_timeout_sec: float,
    llm_work_dir: Path | None,
    llm_json_runner: LLMJsonRunner | None,
) -> dict[str, Any]:
    schema_id = str(schema["category_id"])
    outer_loop_global_update_mode = str(evidence.get("outer_loop_global_update_mode") or "rewrite")
    outer_loop_update_mode = str(evidence.get("outer_loop_update_mode") or "rewrite")
    deterministic_edits = propose_slot_edits(schema, evidence)
    reliable_support_size = int(evidence["reliable_support_size"])
    if outer_loop_update_mode == "hold":
        proposal_status = "freeze_update_decision_hold"
    elif min_support_size > 0 and reliable_support_size < min_support_size:
        proposal_status = "freeze_low_support"
    elif min_support_size > 0 and not evidence.get("assigned_task_summaries"):
        proposal_status = "freeze_unassigned"
    else:
        proposal_status = "candidate_update"

    llm_payload: dict[str, Any] | None = None
    rewrite_source = "deterministic"
    rewrite_error = ""
    if rewrite_mode == "llm" and proposal_status == "candidate_update":
        try:
            llm_payload = propose_llm_slot_edits(
                schema=schema,
                evidence=evidence,
                deterministic_edits=deterministic_edits,
                llm_model=llm_model,
                llm_timeout_sec=llm_timeout_sec,
                llm_work_dir=(llm_work_dir or Path(".") / "llm_runs") / schema_id,
                llm_json_runner=llm_json_runner,
            )
            edits = normalize_slot_edits(llm_payload.get("slot_edits"))
            rewrite_source = "llm"
        except Exception as exc:  # pragma: no cover - covered by integration runs.
            edits = deterministic_edits
            rewrite_source = "deterministic_fallback"
            rewrite_error = f"{type(exc).__name__}: {exc}"
    elif rewrite_mode == "llm":
        edits = deterministic_edits
        rewrite_source = "deterministic_low_support"
    elif rewrite_mode == "deterministic":
        edits = deterministic_edits
    else:
        raise ValueError(f"unsupported rewrite mode: {rewrite_mode}")

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
                    + len(slot_payload.get("remove", []))
                    + len(slot_payload.get("sharpen", []))
                    for slot_payload in edits.values()
                ),
                "expected_effect": expected_effects(mode, evidence),
            }
        )

    if proposal_status != "candidate_update":
        selected_mode = "incumbent"
    elif outer_loop_update_mode == "guarded_patch":
        selected_mode = "conservative"
    else:
        selected_mode = choose_challenger_mode(evidence)
    return {
        "category_id": schema_id,
        "proposal_status": proposal_status,
        "outer_loop_global_update_mode": outer_loop_global_update_mode,
        "outer_loop_update_mode": outer_loop_update_mode,
        "outer_loop_update_reason": evidence.get("outer_loop_update_reason"),
        "positive_transfer_count": len(evidence.get("positive_transfer_pairs") or []),
        "protected_regression_count": len(evidence.get("protected_regression_pairs") or []),
        "support_size": evidence["support_size"],
        "reliable_support_size": reliable_support_size,
        "mean_assigned_score": evidence["mean_assigned_score"],
        "mean_delta_vs_c1_pp": evidence["mean_delta_vs_c1_pp"],
        "priority_score": schema_update_priority(evidence),
        "recommended_challenger_mode": selected_mode,
        "rewrite_mode": rewrite_mode,
        "rewrite_source": rewrite_source,
        "rewrite_model": llm_model if rewrite_source == "llm" else None,
        "rewrite_error": rewrite_error,
        "operator_summary": (
            llm_payload["operator_summary"]
            if llm_payload is not None and rewrite_source == "llm"
            else summarize_edits(edits, schema)
        ),
        "deterministic_seed_slot_edits": deterministic_edits,
        "slot_edits": edits,
        "challenger_schemas": challengers,
        "llm_challenger_guidance": (
            llm_payload.get("challenger_guidance") if llm_payload is not None else None
        ),
        "expected_effect": (
            llm_payload.get("expected_effect")
            if llm_payload is not None and rewrite_source == "llm"
            else expected_effects(selected_mode, evidence)
        ),
        "acceptance_notes": (
            llm_payload.get("acceptance_notes")
            if llm_payload is not None and rewrite_source == "llm"
            else acceptance_notes(evidence, min_support_size)
        ),
    }


def expected_effects(mode: str, evidence: dict[str, Any]) -> list[str]:
    effects = [
        "preserve the frozen Render path while changing only schema-level guidance",
        "make the next rerun auditable against round-0 assigned tasks",
    ]
    if evidence.get("outer_loop_update_mode") == "guarded_patch":
        effects.append("absorb only positive-transfer evidence while protecting prior stable behavior")
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
    if evidence.get("outer_loop_update_mode") == "guarded_patch":
        notes.append("reject if protected regression pairs remain worse than the stable reference schema")
    if min_support_size > 0 and int(evidence["reliable_support_size"]) < min_support_size:
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
            reason = (
                "selected_by_guarded_patch_positive_transfer"
                if proposal.get("outer_loop_update_mode") == "guarded_patch"
                else "selected_by_priority"
            )
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
                "outer_loop_update_mode": proposal.get("outer_loop_update_mode") or "rewrite",
                "positive_transfer_count": proposal.get("positive_transfer_count") or 0,
                "protected_regression_count": proposal.get("protected_regression_count") or 0,
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
    update_modes = sorted(
        {
            str(proposal.get("outer_loop_update_mode") or "rewrite")
            for proposal in proposals_by_schema.values()
        }
    )
    candidate_bank["outer_loop_update"] = {
        "next_round_id": next_round_id,
        "update_policy": "slot-first schema edits with frozen Render",
        "schema_update_modes": update_modes,
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
        replacement["outer_loop_update_mode"] = proposal.get("outer_loop_update_mode") or "rewrite"
        replacement["outer_loop_update_reason"] = proposal.get("outer_loop_update_reason")
        updated_categories.append(replacement)
    candidate_bank["categories"] = updated_categories
    return candidate_bank


def schema_projection(schema: dict[str, Any]) -> dict[str, Any]:
    return {
        field_name: schema.get(field_name)
        for field_name in (*SLOT_FIELDS, "meta_prompt")
        if field_name in schema
    }


def schemas_are_rewritten(original_schema: dict[str, Any], candidate_schema: dict[str, Any]) -> bool:
    return schema_projection(original_schema) != schema_projection(candidate_schema)


def build_rewrite_verification(
    *,
    prompt_bank: dict[str, Any],
    candidate_prompt_bank: dict[str, Any],
    proposals_by_schema: dict[str, dict[str, Any]],
    round_update_plan: list[dict[str, Any]],
    rewrite_mode: str,
    min_support_size: int,
    max_update_schemas: int,
) -> dict[str, Any]:
    original_by_schema = {
        str(schema.get("category_id")): schema
        for schema in prompt_bank.get("categories", [])
        if isinstance(schema, dict) and schema.get("category_id")
    }
    candidate_by_schema = {
        str(schema.get("category_id")): schema
        for schema in candidate_prompt_bank.get("categories", [])
        if isinstance(schema, dict) and schema.get("category_id")
    }
    schema_ids = [str(schema_id) for schema_id in original_by_schema]
    expected_schema_ids = [
        str(row["category_id"])
        for row in round_update_plan
        if row.get("action") == "update"
    ]
    failures: list[dict[str, Any]] = []
    completed_schema_ids: list[str] = []

    decision_limited_update = any(
        proposal.get("proposal_status") == "freeze_update_decision_hold"
        or proposal.get("outer_loop_update_mode") in {"guarded_patch", "hold"}
        for proposal in proposals_by_schema.values()
    )
    unrestricted_update = min_support_size <= 0 and max_update_schemas <= 0 and not decision_limited_update
    if unrestricted_update and set(expected_schema_ids) != set(schema_ids):
        failures.append(
            {
                "schema_id": None,
                "reason": "unrestricted_policy_did_not_select_all_schemas",
                "expected_schema_ids": schema_ids,
                "actual_schema_ids": expected_schema_ids,
            }
        )

    for schema_id in expected_schema_ids:
        schema_failures: list[str] = []
        original_schema = original_by_schema.get(schema_id)
        candidate_schema = candidate_by_schema.get(schema_id)
        proposal = proposals_by_schema.get(schema_id)
        if original_schema is None:
            schema_failures.append("missing_original_schema")
        if candidate_schema is None:
            schema_failures.append("missing_candidate_schema")
        if proposal is None:
            schema_failures.append("missing_update_proposal")
        elif proposal.get("proposal_status") != "candidate_update":
            schema_failures.append(f"proposal_status_is_{proposal.get('proposal_status')}")
        if rewrite_mode == "llm" and proposal is not None and proposal.get("rewrite_source") != "llm":
            schema_failures.append(f"rewrite_source_is_{proposal.get('rewrite_source')}")
        if candidate_schema is not None:
            if candidate_schema.get("outer_loop_candidate_status") != "proposed_for_rerun":
                schema_failures.append("missing_outer_loop_candidate_status")
            if not candidate_schema.get("outer_loop_candidate_id"):
                schema_failures.append("missing_outer_loop_candidate_id")
            if not candidate_schema.get("outer_loop_candidate_mode"):
                schema_failures.append("missing_outer_loop_candidate_mode")
        if original_schema is not None and candidate_schema is not None and not schemas_are_rewritten(
            original_schema,
            candidate_schema,
        ):
            schema_failures.append("candidate_schema_matches_original_schema")
        if schema_failures:
            failures.append({"schema_id": schema_id, "reason": ";".join(schema_failures)})
        else:
            completed_schema_ids.append(schema_id)

    if len(completed_schema_ids) != len(expected_schema_ids):
        failures.append(
            {
                "schema_id": None,
                "reason": "completed_rewrite_count_mismatch",
                "expected": len(expected_schema_ids),
                "actual": len(completed_schema_ids),
            }
        )

    return {
        "artifact_type": "skillx_outer_loop_rewrite_verification",
        "status": "failed" if failures else "passed",
        "rewrite_mode": rewrite_mode,
        "min_support_size": min_support_size,
        "max_update_schemas": max_update_schemas,
        "unrestricted_update": unrestricted_update,
        "decision_limited_update": decision_limited_update,
        "schema_count": len(schema_ids),
        "expected_rewrite_schema_count": len(expected_schema_ids),
        "completed_rewrite_schema_count": len(completed_schema_ids),
        "expected_rewrite_schema_ids": expected_schema_ids,
        "completed_rewrite_schema_ids": completed_schema_ids,
        "failures": failures,
    }


def assert_rewrite_verification_passed(verification: dict[str, Any]) -> None:
    if verification.get("status") == "passed":
        return
    failures = verification.get("failures") or []
    raise AssertionError(
        "outer-loop schema rewrite verification failed: "
        + json.dumps(failures[:5], sort_keys=True)
    )


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
        for task in evidence.get("positive_transfer_pairs", []):
            if not isinstance(task, dict):
                continue
            name = str(task.get("task_name") or "")
            if name and name not in task_names:
                task_names.append(name)
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
                "purpose": (
                    "evaluate guarded positive-transfer tasks plus assigned/boundary tasks"
                    if evidence.get("outer_loop_update_mode") == "guarded_patch"
                    else "evaluate assigned tasks plus low-margin boundary cases"
                ),
            }
        )
    return rows


def build_schema_update_package(
    *,
    control_plane_bundle_path: Path,
    prompt_bank_path: Path,
    task_cluster_inputs_path: Path | None,
    update_decision: dict[str, Any] | None = None,
    rewrite_mode: str,
    llm_model: str,
    llm_timeout_sec: float,
    llm_work_dir: Path | None,
    llm_json_runner: LLMJsonRunner | None = None,
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
    effective_update_decision = update_decision or default_update_decision(schema_ids)
    assignments = [
        row for row in bundle.get("assignments", []) if isinstance(row, dict)
    ]
    training_evidence_rows = training_evidence_rows_from_bundle(bundle)
    score_rows = score_rows_from_bundle(bundle)
    score_by_pair, scores_by_task = index_score_rows(score_rows)
    task_names = sorted(
        {
            str(row.get("task_name"))
            for row in [*assignments, *training_evidence_rows]
            if isinstance(row.get("task_name"), str)
        }
    )
    log_progress(
        "start package build: "
        f"round_id={round_id} next_round_id={next_round_id} "
        f"rewrite_mode={rewrite_mode} "
        f"outer_loop_update_mode={effective_update_decision.get('global_update_mode')} "
        f"schemas={len(schema_ids)} tasks={len(task_names)} "
        f"assignments={len(assignments)} score_rows={len(score_rows)}"
    )
    if task_names:
        log_progress("evidence tasks: " + ", ".join(task_names))

    evidence_by_schema: dict[str, dict[str, Any]] = {}
    proposals: list[dict[str, Any]] = []
    schema_by_id = {str(schema["category_id"]): schema for schema in prompt_bank["categories"]}
    for schema_index, schema_id in enumerate(schema_ids, start=1):
        log_progress(f"schema {schema_index}/{len(schema_ids)}: building evidence for {schema_id}")
        evidence = build_schema_evidence(
            schema_id=schema_id,
            assignments=assignments,
            training_evidence_rows=training_evidence_rows,
            score_by_pair=score_by_pair,
            scores_by_task=scores_by_task,
            task_profiles=task_profiles,
            low_margin_pp=low_margin_pp,
            boundary_margin_pp=boundary_margin_pp,
        )
        evidence = attach_update_decision_evidence(
            evidence,
            update_decision=effective_update_decision,
        )
        evidence_by_schema[schema_id] = evidence
        assigned_count = len(evidence.get("assigned_task_summaries", []) or [])
        boundary_count = len(evidence.get("ambiguous_borderline_cases", []) or [])
        loss_count = len(evidence.get("cross_schema_losses", []) or [])
        log_progress(
            f"schema {schema_index}/{len(schema_ids)}: update proposal for {schema_id} "
            f"(assigned={assigned_count}, boundary={boundary_count}, cross_losses={loss_count})"
        )
        proposal = build_schema_update_proposal(
            schema=schema_by_id[schema_id],
            evidence=evidence,
            min_support_size=min_support_size,
            rewrite_mode=rewrite_mode,
            llm_model=llm_model,
            llm_timeout_sec=llm_timeout_sec,
            llm_work_dir=llm_work_dir,
            llm_json_runner=llm_json_runner,
        )
        proposals.append(proposal)
        log_progress(
            f"schema {schema_index}/{len(schema_ids)}: proposal complete for {schema_id} "
            f"status={proposal.get('proposal_status')} "
            f"update_mode={proposal.get('outer_loop_update_mode')} "
            f"source={proposal.get('rewrite_source')} "
            f"support={proposal.get('support_size')}"
        )

    round_update_plan = select_round_updates(
        proposals,
        max_update_schemas=max_update_schemas,
    )
    update_schema_ids = [
        str(row.get("category_id"))
        for row in round_update_plan
        if isinstance(row, dict) and row.get("action") == "update"
    ]
    log_progress(
        "round update plan selected: "
        f"updates={len(update_schema_ids)}/{len(schema_ids)} "
        f"schemas={', '.join(update_schema_ids) if update_schema_ids else 'none'}"
    )
    proposals_by_schema = {proposal["category_id"]: proposal for proposal in proposals}
    candidate_prompt_bank = build_candidate_prompt_bank(
        prompt_bank=prompt_bank,
        proposals_by_schema=proposals_by_schema,
        round_update_plan=round_update_plan,
        next_round_id=next_round_id,
    )
    rewrite_verification = build_rewrite_verification(
        prompt_bank=prompt_bank,
        candidate_prompt_bank=candidate_prompt_bank,
        proposals_by_schema=proposals_by_schema,
        round_update_plan=round_update_plan,
        rewrite_mode=rewrite_mode,
        min_support_size=min_support_size,
        max_update_schemas=max_update_schemas,
    )
    assert_rewrite_verification_passed(rewrite_verification)
    log_progress(
        "rewrite verification: "
        f"status={rewrite_verification.get('status')} "
        f"completed={rewrite_verification.get('completed_rewrite_schema_count')}/"
        f"{rewrite_verification.get('expected_rewrite_schema_count')}"
    )
    challenger_eval_plan = build_challenger_eval_plan(
        evidence_by_schema=evidence_by_schema,
        round_update_plan=round_update_plan,
        max_tasks_per_schema=max_eval_tasks_per_schema,
    )
    next_pair_count = sum(int(row.get("task_count") or 0) for row in challenger_eval_plan)
    log_progress(
        "challenger eval plan: "
        f"schemas={len(challenger_eval_plan)} planned_pairs={next_pair_count}"
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
            "rewrite_mode": rewrite_mode,
            "llm_model": llm_model if rewrite_mode == "llm" else None,
            "llm_timeout_sec": llm_timeout_sec if rewrite_mode == "llm" else None,
            "llm_work_dir": None if llm_work_dir is None else display_path(llm_work_dir.resolve()),
            "llm_runtime_profiles": (
                llm_runtime_profile_summary(llm_model) if rewrite_mode == "llm" else []
            ),
            "training_evidence_source": (
                "schema_training_assignments"
                if training_evidence_rows
                and (
                    (bundle.get("diagnostics") or {}).get("schema_training_assignments")
                    or bundle.get("schema_training_assignments")
                )
                else "legacy_assignments"
            ),
            "min_support_size": min_support_size,
            "low_margin_pp": low_margin_pp,
            "boundary_margin_pp": boundary_margin_pp,
            "max_update_schemas": max_update_schemas,
            "max_eval_tasks_per_schema": max_eval_tasks_per_schema,
            "outer_loop_global_update_mode": effective_update_decision.get("global_update_mode"),
            "outer_loop_update_reason": effective_update_decision.get("mode_reason"),
        },
        "outer_loop_update_decision": effective_update_decision,
        "schema_ids": schema_ids,
        "schema_evidence_bundles": evidence_by_schema,
        "schema_update_proposals": proposals,
        "round_update_plan": round_update_plan,
        "rewrite_verification": rewrite_verification,
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
        f"- rewrite_mode: `{package['config']['rewrite_mode']}`",
        f"- outer_loop_update_mode: `{package['config'].get('outer_loop_global_update_mode')}`",
        f"- llm_model: `{package['config']['llm_model']}`",
        f"- min_support_size: `{package['config']['min_support_size']}`",
        f"- max_update_schemas: `{package['config']['max_update_schemas']}`",
        f"- rewrite_verification: `{package['rewrite_verification']['status']}` "
        f"({package['rewrite_verification']['completed_rewrite_schema_count']}/"
        f"{package['rewrite_verification']['expected_rewrite_schema_count']})",
        "",
        "## Round Update Plan",
        "",
        "| schema_id | action | update_mode | reason | support | reliable | priority | challenger |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in package["round_update_plan"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["category_id"]),
                    str(row["action"]),
                    str(row.get("outer_loop_update_mode") or "rewrite"),
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
    update_decision_json_path = output_dir / "outer_loop_update_decision.json"
    evidence_json_path = output_dir / "schema_evidence_bundles.json"
    proposals_json_path = output_dir / "schema_update_proposals.json"
    update_plan_json_path = output_dir / "round_update_plan.json"
    rewrite_verification_json_path = output_dir / "rewrite_verification.json"
    eval_plan_json_path = output_dir / "challenger_eval_plan.json"
    candidate_prompt_bank_path = output_dir / "round1_candidate_prompt_bank.json"
    summary_md_path = output_dir / "summary.md"
    update_plan_csv_path = output_dir / "round_update_plan.csv"

    write_json(package_json_path, package)
    write_json(update_decision_json_path, package.get("outer_loop_update_decision") or {})
    write_json(evidence_json_path, package["schema_evidence_bundles"])
    write_json(proposals_json_path, package["schema_update_proposals"])
    write_json(update_plan_json_path, package["round_update_plan"])
    write_json(rewrite_verification_json_path, package["rewrite_verification"])
    write_json(eval_plan_json_path, package["challenger_eval_plan"])
    write_json(candidate_prompt_bank_path, package["candidate_prompt_bank"])
    write_csv(
        update_plan_csv_path,
        package["round_update_plan"],
        [
            "category_id",
            "action",
            "reason",
            "outer_loop_update_mode",
            "positive_transfer_count",
            "protected_regression_count",
            "priority_score",
            "recommended_challenger_mode",
            "support_size",
            "reliable_support_size",
        ],
    )
    summary_md_path.write_text(render_summary_markdown(package, output_dir))
    return {
        "schema_update_package_json": display_path(package_json_path),
        "outer_loop_update_decision_json": display_path(update_decision_json_path),
        "schema_evidence_bundles_json": display_path(evidence_json_path),
        "schema_update_proposals_json": display_path(proposals_json_path),
        "round_update_plan_json": display_path(update_plan_json_path),
        "round_update_plan_csv": display_path(update_plan_csv_path),
        "rewrite_verification_json": display_path(rewrite_verification_json_path),
        "challenger_eval_plan_json": display_path(eval_plan_json_path),
        "candidate_prompt_bank_json": display_path(candidate_prompt_bank_path),
        "summary_md": display_path(summary_md_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-plane-bundle-path", type=Path, default=DEFAULT_CONTROL_PLANE_BUNDLE_PATH)
    parser.add_argument("--prompt-bank-path", type=Path, default=DEFAULT_PROMPT_BANK_PATH)
    parser.add_argument("--task-cluster-inputs-path", type=Path, default=DEFAULT_TASK_CLUSTER_INPUTS_PATH)
    parser.add_argument("--update-decision-path", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--rewrite-mode",
        choices=["llm", "deterministic"],
        default=DEFAULT_REWRITE_MODE,
        help="Use the current authenticated CLI model to author update operations, or use deterministic seed rules.",
    )
    parser.add_argument(
        "--llm-model",
        default=DEFAULT_LLM_MODEL,
        help=(
            "Model used for --rewrite-mode llm. Routed to claude or codex CLI from the model name. "
            "Claude CLI rewrites auto-retry configured fallback Claude profiles on hard rate/quota signals."
        ),
    )
    parser.add_argument("--llm-timeout-sec", type=float, default=DEFAULT_LLM_TIMEOUT_SEC)
    parser.add_argument("--round-id", default=DEFAULT_ROUND_ID)
    parser.add_argument("--next-round-id", default=DEFAULT_NEXT_ROUND_ID)
    parser.add_argument(
        "--min-support-size",
        type=int,
        default=DEFAULT_MIN_SUPPORT_SIZE,
        help="Minimum reliable assigned-task support required before updating a schema; 0 updates all schemas.",
    )
    parser.add_argument("--low-margin-pp", type=float, default=DEFAULT_LOW_MARGIN_PP)
    parser.add_argument("--boundary-margin-pp", type=float, default=DEFAULT_BOUNDARY_MARGIN_PP)
    parser.add_argument(
        "--max-update-schemas",
        type=int,
        default=DEFAULT_MAX_UPDATE_SCHEMAS,
        help="Maximum schemas to update by priority; 0 updates every eligible schema.",
    )
    parser.add_argument("--max-eval-tasks-per-schema", type=int, default=6)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    update_decision = read_json(args.update_decision_path) if args.update_decision_path is not None else None
    package = build_schema_update_package(
        control_plane_bundle_path=args.control_plane_bundle_path,
        prompt_bank_path=args.prompt_bank_path,
        task_cluster_inputs_path=args.task_cluster_inputs_path,
        update_decision=update_decision,
        rewrite_mode=str(args.rewrite_mode),
        llm_model=str(args.llm_model),
        llm_timeout_sec=float(args.llm_timeout_sec),
        llm_work_dir=args.output_dir / "llm_runs",
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

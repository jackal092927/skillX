#!/usr/bin/env python3
"""Audit completed SkillX inner-loop results and prepare targeted reruns."""

from __future__ import annotations

import argparse
import json
import re
import shlex
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from export_round0_run_report import (
    build_run_report,
    parse_run_status_markdown,
    read_json,
    read_ndjson,
    write_json,
)


ROOT = Path(__file__).resolve().parents[1]
DECISION_RANK = {"none": 0, "recommended": 1, "required": 2}


def promote_decision(current: str, candidate: str) -> str:
    return candidate if DECISION_RANK[candidate] > DECISION_RANK[current] else current


def parse_pair_id(pair_id: str) -> tuple[str, str]:
    if "__" not in pair_id:
        return pair_id, "unknown-schema"
    task_name, schema_id = pair_id.rsplit("__", 1)
    return task_name, schema_id


def load_pair_specs(materialized_root: Path) -> dict[str, dict[str, Any]]:
    pair_specs_path = materialized_root / "pair_specs.jsonl"
    pair_specs: dict[str, dict[str, Any]] = {}
    if not pair_specs_path.exists():
        return pair_specs
    for raw_line in pair_specs_path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        pair_id = payload.get("pair_id")
        if isinstance(pair_id, str):
            pair_specs[pair_id] = payload
    return pair_specs


def index_events_by_pair(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        pair_id = event.get("pair_id")
        if isinstance(pair_id, str):
            by_pair[pair_id].append(event)
    return dict(by_pair)


def profile_label(profile: Any) -> str | None:
    if not isinstance(profile, dict):
        return None
    label = profile.get("label")
    return label if isinstance(label, str) and label else None


def profile_agent(profile: Any) -> str | None:
    if not isinstance(profile, dict):
        return None
    agent = profile.get("agent")
    return agent if isinstance(agent, str) and agent else None


def profile_model(profile: Any) -> str | None:
    if not isinstance(profile, dict):
        return None
    model = profile.get("model")
    return model if isinstance(model, str) and model else None


def runtime_profiles_seen(launcher_result: dict[str, Any], pair_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []

    def add(profile: Any) -> None:
        if isinstance(profile, dict):
            key = json.dumps(profile, sort_keys=True)
            if key not in seen:
                seen.add(key)
                profiles.append(profile)

    seen: set[str] = set()
    for attempt in launcher_result.get("attempts") or []:
        if isinstance(attempt, dict):
            add(attempt.get("runtime_profile"))
    add(launcher_result.get("runtime_profile"))
    for event in pair_events:
        add(event.get("runtime_profile"))
        add(event.get("exhausted_profile"))
        add(event.get("next_profile"))
    return profiles


def is_fallback_claude_profile(profile: dict[str, Any]) -> bool:
    label = (profile_label(profile) or "").lower()
    agent = (profile_agent(profile) or "").lower()
    return label.startswith("fallback-claude") or (label.startswith("fallback") and agent == "claude-code")


def is_basic_model_fallback_profile(profile: dict[str, Any]) -> bool:
    label = (profile_label(profile) or "").lower()
    agent = (profile_agent(profile) or "").lower()
    model = (profile_model(profile) or "").lower()
    if label == "fallback-codex":
        return True
    if label.startswith("fallback") and agent == "codex":
        return True
    return label.startswith("fallback") and (model.startswith("gpt-") or "codex" in model)


def parse_runtime_failure_rounds(run_status: dict[str, str]) -> list[int]:
    value = run_status.get("runtime_failure_rounds") or ""
    rounds: list[int] = []
    for token in re.findall(r"R?(\d+)", value):
        try:
            rounds.append(int(token))
        except ValueError:
            pass
    return sorted(set(rounds))


def read_run_failure(output_dir: Path) -> dict[str, Any] | None:
    failure_path = output_dir / "run_failure.json"
    if not failure_path.exists():
        return None
    try:
        payload = read_json(failure_path)
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def collect_rate_limit_signals(output_dir: Path) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    if not output_dir.exists():
        return signals
    for path in sorted(output_dir.glob("**/rate_limit_signal.json")):
        try:
            payload = read_json(path)
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        hard_terms = payload.get("hard_terms") or payload.get("matched_terms") or []
        signals.append(
            {
                "path": str(path),
                "has_hard_signal": bool(payload.get("has_hard_signal") or hard_terms),
                "hard_terms": [str(term) for term in hard_terms if isinstance(term, str)],
                "signal_level": payload.get("signal_level"),
            }
        )
    return signals


def text_blob(*items: Any) -> str:
    return "\n".join(str(item) for item in items if item is not None)


def looks_missing_trial_dir(text: str) -> bool:
    lowered = text.lower()
    return "expected exactly one trial dir" in lowered or ("trial dir" in lowered and "found 0" in lowered)


def looks_docker_or_machine(text: str) -> bool:
    lowered = text.lower()
    needles = (
        "docker_health_gate",
        "cannot connect to the docker daemon",
        "docker daemon",
        "docker memory",
        "out of memory",
        "no space left on device",
        "failed to pull image",
        "image not found",
        "buildkit",
    )
    return any(needle in lowered for needle in needles)


def looks_timeout(text: str) -> bool:
    lowered = text.lower()
    return "timed out" in lowered or "timeout" in lowered or "time limit" in lowered


def hard_rate_terms(signals: list[dict[str, Any]], pair_events: list[dict[str, Any]]) -> list[str]:
    terms: set[str] = set()
    for signal in signals:
        if signal.get("has_hard_signal"):
            terms.update(str(term) for term in signal.get("hard_terms") or [] if term)
    for event in pair_events:
        if event.get("event") in {"rate_limit_detected", "rate_limit_fallback_selected"}:
            terms.update(str(term) for term in event.get("quota_hard_terms") or [] if term)
    return sorted(terms)


def build_missing_pair_audit(pair_id: str, pair_spec: dict[str, Any] | None) -> dict[str, Any]:
    task_name, schema_id = parse_pair_id(pair_id)
    if pair_spec:
        task_name = str(pair_spec.get("task_name") or task_name)
        schema_id = str(pair_spec.get("schema_id") or schema_id)
    return {
        "pair_id": pair_id,
        "task_name": task_name,
        "schema_id": schema_id,
        "launcher_status": "not_started",
        "run_status": "not_started",
        "evidence_class": "runtime-blocked",
        "reported_score_pct": None,
        "selected_round_index": None,
        "issue_codes": ["launcher_incomplete"],
        "severity": "error",
        "validity": "invalid",
        "rerun_decision": "required",
        "recommendation": "Rerun this pair; the launcher summary expected it but no pair result was recorded.",
        "failure_summary": "launcher completed fewer pair results than selected_pair_ids",
        "runtime_failure_rounds": [],
        "hard_rate_limit_terms": [],
        "rate_limit_signal_count": 0,
        "runtime_profiles_seen": [],
        "final_runtime_profile": None,
        "output_dir": None,
    }


def classify_pair_audit(
    *,
    pair_report: dict[str, Any],
    launcher_result: dict[str, Any],
    pair_events: list[dict[str, Any]],
) -> dict[str, Any]:
    pair_id = str(pair_report["pair_id"])
    output_dir = Path(str(launcher_result.get("output_dir") or ""))
    run_status = parse_run_status_markdown(output_dir / "RUN_STATUS.md")
    run_failure = read_run_failure(output_dir)
    rate_signals = collect_rate_limit_signals(output_dir)
    profiles = runtime_profiles_seen(launcher_result, pair_events)
    final_profile = launcher_result.get("runtime_profile")
    if not isinstance(final_profile, dict) and profiles:
        final_profile = profiles[-1]
    runtime_failure_rounds = parse_runtime_failure_rounds(run_status)
    failure_summary = (
        (pair_report.get("failure") or {}).get("summary")
        or (run_failure or {}).get("error_message")
        or launcher_result.get("error")
        or ""
    )
    status_text = text_blob(
        launcher_result.get("stage"),
        launcher_result.get("error"),
        failure_summary,
        run_failure,
        pair_report.get("launcher_log_excerpt"),
    )
    launcher_status = str(launcher_result.get("status") or pair_report.get("launcher", {}).get("status") or "unknown")
    raw_run_status = str(
        run_status.get("status")
        or pair_report.get("run", {}).get("status")
        or "unknown"
    )
    reported_score_pct = pair_report.get("reported_score", {}).get("score_pct")
    selected_round_index = pair_report.get("reported_score", {}).get("round_index")
    issue_codes: list[str] = []
    rerun_decision = "none"
    recommendation = "No rerun needed; this pair has clean completed evidence."
    validity = "valid"

    def add_issue(code: str) -> None:
        if code not in issue_codes:
            issue_codes.append(code)

    has_hard_rate_limit = bool(hard_rate_terms(rate_signals, pair_events))
    has_basic_model_fallback = any(is_basic_model_fallback_profile(profile) for profile in profiles)
    has_claude_fallback = any(is_fallback_claude_profile(profile) for profile in profiles)
    timeout_detected = bool(pair_report.get("timeout_detected") or looks_timeout(status_text))

    if raw_run_status == "skipped_baseline_perfect":
        add_issue("baseline_perfect_skip")
        validity = "valid_intentional_skip"
        recommendation = "No rerun by default; R0 stayed perfect and the inner loop was intentionally skipped."
    elif launcher_status == "failed" or raw_run_status == "failed":
        validity = "invalid"
        rerun_decision = "required"
        recommendation = "Rerun this pair after addressing the classified runtime issue."
        if launcher_result.get("stage") == "rate_limit_exhausted":
            add_issue("rate_limit_exhausted")
            recommendation = "Switch to a fresh Claude quota/account and rerun this pair."
        elif looks_missing_trial_dir(status_text):
            add_issue("missing_trial_dir")
            recommendation = "Rerun this pair after cleaning its failed output dir; the R0 tune_check trial artifact was incomplete."
        elif looks_docker_or_machine(status_text):
            add_issue("docker_or_machine_failure")
            recommendation = "Repair Docker/machine health, then rerun this pair."
        elif timeout_detected:
            add_issue("timeout")
            recommendation = "Rerun this pair with a larger timeout or after checking whether the task is inherently slow."
        else:
            add_issue("launcher_or_runtime_failure")
    else:
        if raw_run_status == "completed_with_runtime_failures" or runtime_failure_rounds:
            add_issue("completed_with_runtime_failures")
            validity = "questionable"
            if reported_score_pct is None or float(reported_score_pct) <= 0.0:
                rerun_decision = promote_decision(rerun_decision, "required")
                recommendation = (
                    "Rerun this pair; later runtime failures can hide a possible inner-loop improvement."
                )
            else:
                rerun_decision = promote_decision(rerun_decision, "recommended")
                recommendation = (
                    "Rerun is recommended for a clean trajectory, although a positive clean selected score exists."
                )
        if pair_report.get("run", {}).get("stale_status"):
            add_issue("stale_run_status")
            validity = "questionable"
            rerun_decision = promote_decision(rerun_decision, "required")
            recommendation = "Rerun or repair stale RUN_STATUS artifacts before using this result."
        if timeout_detected:
            add_issue("timeout")
            validity = "questionable"
            rerun_decision = promote_decision(
                rerun_decision,
                "required" if reported_score_pct is None else "recommended",
            )
            recommendation = "Rerun with a larger timeout if this pair matters for aggregate evidence."
        if reported_score_pct is None and raw_run_status != "skipped_baseline_perfect":
            add_issue("missing_score")
            validity = "questionable"
            rerun_decision = promote_decision(rerun_decision, "required")
            recommendation = "Rerun this pair; no usable verifier score was found."

    if has_basic_model_fallback:
        add_issue("basic_model_fallback")
        validity = "questionable_model_mismatch"
        rerun_decision = promote_decision(rerun_decision, "required")
        recommendation = "Rerun this pair on the intended primary executor/model to keep results comparable."
    if has_hard_rate_limit:
        add_issue("rate_limit_fallback")
        if rerun_decision == "none" and validity == "valid":
            validity = "valid_with_notes"
            recommendation = "No rerun by default; a hard rate-limit fallback occurred but final evidence completed."
    if has_claude_fallback:
        add_issue("claude_account_fallback")
        if rerun_decision == "none" and validity == "valid":
            validity = "valid_with_notes"
            recommendation = "No rerun by default; only the Claude account/token changed."
    if not issue_codes and raw_run_status == "completed":
        add_issue("complete_without_exceptions")

    if rerun_decision == "required":
        severity = "error"
    elif rerun_decision == "recommended":
        severity = "warning"
    elif issue_codes == ["complete_without_exceptions"]:
        severity = "ok"
    else:
        severity = "note"

    return {
        "pair_id": pair_id,
        "task_name": pair_report.get("task_name"),
        "schema_id": pair_report.get("schema_id"),
        "launcher_status": launcher_status,
        "run_status": raw_run_status,
        "evidence_class": pair_report.get("evidence_class"),
        "reported_score_pct": reported_score_pct,
        "selected_round_index": selected_round_index,
        "issue_codes": issue_codes,
        "severity": severity,
        "validity": validity,
        "rerun_decision": rerun_decision,
        "recommendation": recommendation,
        "failure_summary": failure_summary or None,
        "runtime_failure_rounds": runtime_failure_rounds,
        "hard_rate_limit_terms": hard_rate_terms(rate_signals, pair_events),
        "rate_limit_signal_count": len(rate_signals),
        "runtime_profiles_seen": profiles,
        "final_runtime_profile": final_profile if isinstance(final_profile, dict) else None,
        "output_dir": str(output_dir) if str(output_dir) else None,
    }


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def build_inner_loop_audit(*, materialized_root: Path, run_label: str) -> dict[str, Any]:
    log_dir = materialized_root / "launcher_logs" / run_label
    summary_path = log_dir / "summary.json"
    events_path = log_dir / "events.ndjson"
    summary = read_json(summary_path)
    events = read_ndjson(events_path)
    events_by_pair = index_events_by_pair(events)
    report = build_run_report(materialized_root=materialized_root, run_label=run_label)
    pair_specs = load_pair_specs(materialized_root)
    report_by_pair = {str(pair["pair_id"]): pair for pair in report["pair_results"]}
    launcher_by_pair = {
        str(item["pair_id"]): item
        for item in summary.get("results", [])
        if isinstance(item, dict) and isinstance(item.get("pair_id"), str)
    }
    expected_pair_ids = summary.get("selected_pair_ids") or list(launcher_by_pair)
    expected_pair_ids = [str(pair_id) for pair_id in expected_pair_ids]

    pair_audits: list[dict[str, Any]] = []
    for pair_id in expected_pair_ids:
        pair_report = report_by_pair.get(pair_id)
        launcher_result = launcher_by_pair.get(pair_id)
        if pair_report is None or launcher_result is None:
            pair_audits.append(build_missing_pair_audit(pair_id, pair_specs.get(pair_id)))
            continue
        pair_audits.append(
            classify_pair_audit(
                pair_report=pair_report,
                launcher_result=launcher_result,
                pair_events=events_by_pair.get(pair_id, []),
            )
        )

    status_counts = Counter(str(row["run_status"]) for row in pair_audits)
    severity_counts = Counter(str(row["severity"]) for row in pair_audits)
    issue_counts = Counter(code for row in pair_audits for code in row["issue_codes"])
    required_pair_ids = [row["pair_id"] for row in pair_audits if row["rerun_decision"] == "required"]
    recommended_pair_ids = [row["pair_id"] for row in pair_audits if row["rerun_decision"] == "recommended"]
    all_flagged_pair_ids = unique_preserve_order(required_pair_ids + recommended_pair_ids)
    global_issues: list[dict[str, Any]] = []
    if summary.get("aborted"):
        global_issues.append(
            {
                "code": "launcher_aborted",
                "severity": "error",
                "message": str(summary.get("abort_reason") or "launcher aborted"),
            }
        )
    if int(summary.get("completed_pairs") or 0) < int(summary.get("total_pairs") or 0):
        global_issues.append(
            {
                "code": "launcher_incomplete",
                "severity": "error",
                "message": f"completed_pairs={summary.get('completed_pairs')} total_pairs={summary.get('total_pairs')}",
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_label": run_label,
        "materialized_root": str(materialized_root.resolve()),
        "launcher_summary_path": str(summary_path.resolve()),
        "launcher_events_path": str(events_path.resolve()),
        "counts": {
            "total_pairs": len(pair_audits),
            "run_status": dict(sorted(status_counts.items())),
            "severity": dict(sorted(severity_counts.items())),
            "issues": dict(sorted(issue_counts.items())),
            "rerun_required": len(required_pair_ids),
            "rerun_recommended": len(recommended_pair_ids),
        },
        "global_issues": global_issues,
        "pair_audits": pair_audits,
        "rerun_plan": {
            "required_pair_ids": required_pair_ids,
            "recommended_pair_ids": recommended_pair_ids,
            "all_flagged_pair_ids": all_flagged_pair_ids,
            "required_policy": "rerun before outer-loop if non-empty",
            "recommended_policy": "rerun before publication or aggregate claims if cost allows",
        },
    }


def md_escape(value: Any) -> str:
    text = "-" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def render_pair_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Pair | Status | Issues | Validity | Rerun | Recommendation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{md_escape(row['pair_id'])}`",
                    f"`{md_escape(row['run_status'])}`",
                    "`" + ", ".join(row["issue_codes"]) + "`",
                    f"`{md_escape(row['validity'])}`",
                    f"`{md_escape(row['rerun_decision'])}`",
                    md_escape(row.get("recommendation")),
                ]
            )
            + " |"
        )
    return lines


def render_audit_markdown(audit: dict[str, Any], artifact_paths: dict[str, str | None]) -> str:
    counts = audit["counts"]
    rows = audit["pair_audits"]
    required = [row for row in rows if row["rerun_decision"] == "required"]
    recommended = [row for row in rows if row["rerun_decision"] == "recommended"]
    notes = [
        row
        for row in rows
        if row["rerun_decision"] == "none" and row["issue_codes"] != ["complete_without_exceptions"]
    ]

    lines = [
        f"# SkillX Inner-Loop Audit: `{audit['run_label']}`",
        "",
        f"- total_pairs: `{counts['total_pairs']}`",
        f"- rerun_required: `{counts['rerun_required']}`",
        f"- rerun_recommended: `{counts['rerun_recommended']}`",
        f"- materialized_root: `{audit['materialized_root']}`",
        "",
        "## Status Counts",
        "",
    ]
    for key, value in counts["run_status"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Issue Counts", ""])
    for key, value in counts["issues"].items():
        lines.append(f"- `{key}`: `{value}`")
    if audit["global_issues"]:
        lines.extend(["", "## Global Issues", ""])
        for issue in audit["global_issues"]:
            lines.append(f"- `{issue['code']}`: {md_escape(issue['message'])}")
    lines.extend(["", "## Rerun Required", ""])
    lines.extend(render_pair_table(required) if required else ["None."])
    lines.extend(["", "## Rerun Recommended", ""])
    lines.extend(render_pair_table(recommended) if recommended else ["None."])
    lines.extend(["", "## Non-Rerun Notes", ""])
    lines.extend(render_pair_table(notes) if notes else ["None."])
    lines.extend(["", "## Generated Rerun Artifacts", ""])
    for key, value in artifact_paths.items():
        lines.append(f"- `{key}`: `{value or '-'}`")
    lines.append("")
    return "\n".join(lines)


def write_pair_manifest(path: Path, pair_ids: list[str], *, run_label: str, decision: str) -> None:
    write_json(
        path,
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_run_label": run_label,
            "rerun_decision": decision,
            "selected_pair_ids": pair_ids,
        },
    )


def write_rerun_script(
    path: Path,
    *,
    materialized_root: Path,
    pair_manifest_path: Path,
    source_run_label: str,
    suffix: str,
) -> None:
    body = f"""#!/usr/bin/env bash
set -euo pipefail

WORKTREE_ROOT={shlex.quote(str(ROOT.resolve()))}
MATERIALIZED_ROOT={shlex.quote(str(materialized_root.resolve()))}
PAIR_MANIFEST={shlex.quote(str(pair_manifest_path.resolve()))}
BASE_RUN_LABEL={shlex.quote(source_run_label)}

RERUN_LABEL="${{1:-${{BASE_RUN_LABEL}}-{suffix}-$(date +%Y-%m-%d-%H%M)}}"
SESSION_NAME="${{2:-skillx-${{RERUN_LABEL}}}}"
MONITOR_PORT="${{3:-}}"

export SKILLX_MATERIALIZED_ROOT="$MATERIALIZED_ROOT"
export SKILLX_MAX_CONCURRENT_PAIRS="${{SKILLX_MAX_CONCURRENT_PAIRS:-1}}"
export SKILLX_DOCKER_AUTO_RECOVER="${{SKILLX_DOCKER_AUTO_RECOVER:-1}}"

cd "$WORKTREE_ROOT"
if [[ -n "$MONITOR_PORT" ]]; then
  scripts/run_skillx_inner_loop_tmux.sh "$RERUN_LABEL" "$SESSION_NAME" "$MONITOR_PORT" -- --pair-manifest "$PAIR_MANIFEST"
else
  scripts/run_skillx_inner_loop_tmux.sh "$RERUN_LABEL" "$SESSION_NAME" -- --pair-manifest "$PAIR_MANIFEST"
fi
"""
    path.write_text(body)
    path.chmod(0o755)


def write_audit_artifacts(*, audit: dict[str, Any], audit_dir: Path) -> dict[str, str | None]:
    audit_dir.mkdir(parents=True, exist_ok=True)
    materialized_root = Path(str(audit["materialized_root"]))
    run_label = str(audit["run_label"])
    rerun_plan = audit["rerun_plan"]
    artifact_paths: dict[str, str | None] = {
        "audit_json": str((audit_dir / "inner_loop_audit.json").resolve()),
        "audit_markdown": str((audit_dir / "inner_loop_audit.md").resolve()),
        "required_pair_manifest": None,
        "recommended_pair_manifest": None,
        "all_flagged_pair_manifest": None,
        "required_rerun_script": None,
        "recommended_rerun_script": None,
        "all_flagged_rerun_script": None,
    }
    bundles = [
        ("required", "audit-rerun-required", rerun_plan["required_pair_ids"]),
        ("recommended", "audit-rerun-recommended", rerun_plan["recommended_pair_ids"]),
        ("all_flagged", "audit-rerun-all-flagged", rerun_plan["all_flagged_pair_ids"]),
    ]
    for key, suffix, pair_ids in bundles:
        if not pair_ids:
            continue
        manifest_path = audit_dir / f"{key}_pair_manifest.json"
        script_path = audit_dir / f"run_{key}_rerun.sh"
        write_pair_manifest(manifest_path, pair_ids, run_label=run_label, decision=key)
        write_rerun_script(
            script_path,
            materialized_root=materialized_root,
            pair_manifest_path=manifest_path,
            source_run_label=run_label,
            suffix=suffix,
        )
        artifact_paths[f"{key}_pair_manifest"] = str(manifest_path.resolve())
        artifact_paths[f"{key}_rerun_script"] = str(script_path.resolve())

    audit_with_paths = dict(audit)
    audit_with_paths["artifacts"] = artifact_paths
    write_json(audit_dir / "inner_loop_audit.json", audit_with_paths)
    (audit_dir / "inner_loop_audit.md").write_text(render_audit_markdown(audit_with_paths, artifact_paths))
    return artifact_paths


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit a completed SkillX inner-loop run and prepare targeted rerun artifacts."
    )
    parser.add_argument("--materialized-root", type=Path, required=True)
    parser.add_argument("--run-label", required=True)
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=None,
        help="Output directory. Default: <materialized-root>/reports/<run-label>/inner_loop_audit",
    )
    parser.add_argument(
        "--fail-on-rerun-required",
        action="store_true",
        help="Exit with code 2 when required rerun pairs are present.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    materialized_root = args.materialized_root.resolve()
    audit_dir = args.audit_dir or (materialized_root / "reports" / args.run_label / "inner_loop_audit")
    audit = build_inner_loop_audit(materialized_root=materialized_root, run_label=args.run_label)
    artifact_paths = write_audit_artifacts(audit=audit, audit_dir=audit_dir)
    required_count = int(audit["counts"]["rerun_required"])
    recommended_count = int(audit["counts"]["rerun_recommended"])
    print(f"wrote inner-loop audit to {artifact_paths['audit_markdown']}")
    print(f"rerun_required={required_count} rerun_recommended={recommended_count}")
    if required_count and artifact_paths.get("required_rerun_script"):
        print(f"required rerun script: {artifact_paths['required_rerun_script']}")
    if args.fail_on_rerun_required and required_count:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

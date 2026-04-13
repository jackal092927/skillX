#!/usr/bin/env python3
"""Export structured reports for a SkillX round-0 launcher run."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home().resolve()
PAIR_HEADER_RE = re.compile(r"^\[(\d+)/(\d+)\] (\S+)$")
RUN_STATUS_RE = re.compile(r"^- ([a-zA-Z0-9_]+): `(.*)`$")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def read_ndjson(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            records.append(payload)
    return records


def parse_run_status_markdown(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text().splitlines():
        match = RUN_STATUS_RE.match(line.strip())
        if match is None:
            continue
        values[match.group(1)] = match.group(2)
    return values


def parse_iso8601(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def duration_seconds(started_at: str | None, finished_at: str | None) -> float | None:
    started = parse_iso8601(started_at)
    finished = parse_iso8601(finished_at)
    if started is None or finished is None:
        return None
    return round((finished - started).total_seconds(), 3)


def pct_from_reward(reward: Any) -> float | None:
    if not isinstance(reward, (int, float)):
        return None
    return round(float(reward) * 100.0, 2)


def sanitize_text(text: str) -> str:
    value = text
    repo_root = str(ROOT.resolve())
    home_root = str(HOME)
    if repo_root in value:
        value = value.replace(repo_root, "<repo-root>")
    if home_root in value:
        value = value.replace(home_root, "~")
    return value


def sanitize_payload(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [sanitize_payload(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_payload(item) for key, item in value.items()}
    return value


def load_pair_specs(pair_specs_path: Path) -> dict[str, dict[str, Any]]:
    pair_specs: dict[str, dict[str, Any]] = {}
    for raw_line in pair_specs_path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict) and isinstance(payload.get("pair_id"), str):
            pair_specs[payload["pair_id"]] = payload
    return pair_specs


def parse_launcher_stdout_blocks(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    blocks: dict[str, list[str]] = defaultdict(list)
    current_pair_id: str | None = None
    for raw_line in path.read_text().splitlines():
        line = raw_line.rstrip("\n")
        match = PAIR_HEADER_RE.match(line.strip())
        if match is not None:
            current_pair_id = match.group(3)
            blocks[current_pair_id].append(line)
            continue
        if current_pair_id is not None:
            blocks[current_pair_id].append(line)
    return dict(blocks)


def index_pair_timings(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    timings: dict[str, dict[str, Any]] = {}
    for event in events:
        pair_id = event.get("pair_id")
        if not isinstance(pair_id, str):
            continue
        record = timings.setdefault(
            pair_id,
            {
                "started_at": None,
                "finished_at": None,
                "final_event": None,
            },
        )
        event_name = event.get("event")
        observed_at = event.get("observed_at")
        if event_name == "pair_started":
            record["started_at"] = observed_at
        elif event_name in {"pair_succeeded", "pair_failed"}:
            record["finished_at"] = observed_at
            record["final_event"] = event_name
    return timings


def parse_round_index(round_dir: Path) -> int:
    return int(round_dir.name.split("-")[-1])


def collect_orchestrator_events(path: Path) -> list[dict[str, Any]]:
    return read_ndjson(path)


def collect_round_reports(pair_output_dir: Path, task_name: str) -> list[dict[str, Any]]:
    rounds_root = pair_output_dir / "refine" / task_name / "rounds"
    if not rounds_root.exists():
        return []

    reports: list[dict[str, Any]] = []
    for round_dir in sorted(rounds_root.glob("round-*"), key=parse_round_index):
        round_index = parse_round_index(round_dir)
        result_path = round_dir / "tune_check" / "result.json"
        decision_path = round_dir / "role_b" / "round_decision.json"
        verifier_summary_path = round_dir / "executor" / "verifier_summary.json"
        orchestrator_log_path = round_dir / "orchestrator_log.ndjson"
        terminal_marker_path = round_dir / "terminal_round.json"

        result = read_json(result_path) if result_path.exists() else {}
        decision = read_json(decision_path) if decision_path.exists() else {}
        verifier_summary = read_json(verifier_summary_path) if verifier_summary_path.exists() else {}
        events = collect_orchestrator_events(orchestrator_log_path)
        event_times = {
            str(event.get("event_type")): event.get("timestamp")
            for event in events
            if isinstance(event.get("event_type"), str)
        }

        reward_raw = result.get("reward")
        verifier_reward = verifier_summary.get("reward")
        evaluation = {
            "reward_raw": verifier_reward,
            "score_pct": pct_from_reward(verifier_reward),
            "passed_tests": verifier_summary.get("passed_tests"),
            "failed_tests": verifier_summary.get("failed_tests"),
            "total_tests": verifier_summary.get("total_tests"),
            "n_errors": verifier_summary.get("n_errors"),
            "pytest_exitcode": verifier_summary.get("pytest_exitcode"),
            "exception_stats": verifier_summary.get("exception_stats") or result.get("exception_stats") or {},
        }
        reports.append(
            {
                "round_index": round_index,
                "reward_raw": reward_raw,
                "score_pct": pct_from_reward(reward_raw),
                "eval_name": result.get("eval_name"),
                "exception_stats": result.get("exception_stats") or {},
                "classification": result.get("classification"),
                "decision": decision.get("decision"),
                "decision_reason": decision.get("reason"),
                "selected_candidate_label": decision.get("selected_candidate_label"),
                "event_times": event_times,
                "evaluation": evaluation,
                "verifier_summary": verifier_summary,
                "terminal_executor_only": terminal_marker_path.exists(),
                "result_path": str(result_path) if result_path.exists() else None,
                "round_dir": str(round_dir),
            }
        )
    return reports


def load_refine_summary(pair_output_dir: Path, task_name: str) -> dict[str, Any] | None:
    summary_path = pair_output_dir / "refine" / task_name / "refine_summary.json"
    if not summary_path.exists():
        return None
    payload = read_json(summary_path)
    return payload if isinstance(payload, dict) else None


def load_run_failure(pair_output_dir: Path) -> dict[str, Any] | None:
    failure_path = pair_output_dir / "run_failure.json"
    if not failure_path.exists():
        return None
    payload = read_json(failure_path)
    return payload if isinstance(payload, dict) else None


def compute_best_observed_round(rounds: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [round_info for round_info in rounds if isinstance(round_info.get("reward_raw"), (int, float))]
    if not candidates:
        return None
    return max(candidates, key=lambda item: (float(item["reward_raw"]), -int(item["round_index"])))


def detect_timeout(*texts: str) -> bool:
    return any("timeout" in text.lower() or "timed out" in text.lower() for text in texts if text)


def build_evaluation_matrix(rounds: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for round_info in rounds:
        evaluation = round_info.get("evaluation") or {}
        classification = round_info.get("classification") or {}
        rows.append(
            {
                "round_index": round_info.get("round_index"),
                "score_pct": evaluation.get("score_pct", round_info.get("score_pct")),
                "passed_tests": evaluation.get("passed_tests"),
                "failed_tests": evaluation.get("failed_tests"),
                "total_tests": evaluation.get("total_tests"),
                "n_errors": evaluation.get("n_errors"),
                "pytest_exitcode": evaluation.get("pytest_exitcode"),
                "classification_kind": classification.get("kind"),
                "decision": round_info.get("decision"),
                "terminal_executor_only": round_info.get("terminal_executor_only"),
                "exception_stats": evaluation.get("exception_stats") or round_info.get("exception_stats") or {},
            }
        )
    return {
        "columns": [
            "round_index",
            "score_pct",
            "passed_tests",
            "failed_tests",
            "total_tests",
            "n_errors",
            "pytest_exitcode",
            "classification_kind",
            "decision",
            "terminal_executor_only",
            "exception_stats",
        ],
        "rows": rows,
    }


def build_failure_summary(
    *,
    run_failure: dict[str, Any] | None,
    launcher_block: list[str],
    rounds: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if run_failure:
        return {
            "error_type": run_failure.get("error_type"),
            "error_message": run_failure.get("error_message"),
            "failed_stage": run_failure.get("failed_stage"),
            "failed_round": run_failure.get("failed_round"),
            "manual_intervention": bool(run_failure.get("manual_intervention")),
            "summary": (
                f"{run_failure.get('error_type')}: {run_failure.get('error_message')}"
                if run_failure.get("error_type") and run_failure.get("error_message")
                else run_failure.get("error_message") or run_failure.get("error_type")
            ),
        }

    for round_info in rounds:
        exception_stats = round_info.get("exception_stats") or {}
        if not isinstance(exception_stats, dict) or not exception_stats:
            continue
        summary_parts = [f"{key}={value}" for key, value in sorted(exception_stats.items())]
        return {
            "error_type": "TuneExceptionStats",
            "error_message": "; ".join(summary_parts),
            "failed_stage": round_info.get("decision") or "tune_check",
            "failed_round": round_info.get("round_index"),
            "manual_intervention": False,
            "summary": "; ".join(summary_parts),
        }

    for line in reversed(launcher_block):
        stripped = line.strip()
        if not stripped or stripped.startswith("FAILED with exit code") or stripped.startswith("["):
            continue
        if "Error:" in stripped or stripped.startswith("FileNotFoundError:") or stripped.startswith("Traceback"):
            if stripped.startswith("Traceback"):
                continue
            return {
                "error_type": "LauncherTraceback",
                "error_message": stripped,
                "failed_stage": "run",
                "failed_round": None,
                "manual_intervention": False,
                "summary": stripped,
            }
    return None


def detect_early_stop(
    *,
    run_status: dict[str, str],
    rounds: list[dict[str, Any]],
) -> bool:
    if run_status.get("status") != "completed":
        return False
    try:
        round_budget = int(run_status.get("round_budget", "0"))
    except ValueError:
        return False
    if not rounds:
        return False
    highest_round = max(int(round_info["round_index"]) for round_info in rounds)
    if highest_round < round_budget:
        return True
    for round_info in rounds:
        decision = round_info.get("decision")
        if decision and decision != "continue" and int(round_info["round_index"]) < round_budget:
            return True
    return False


def build_pair_report(
    *,
    launcher_result: dict[str, Any],
    pair_spec: dict[str, Any],
    pair_timing: dict[str, Any],
    launcher_block: list[str],
) -> dict[str, Any]:
    pair_output_dir = Path(str(launcher_result["output_dir"]))
    task_name = str(launcher_result["task_name"])
    run_status = parse_run_status_markdown(pair_output_dir / "RUN_STATUS.md")
    rounds = collect_round_reports(pair_output_dir, task_name)
    refine_summary = load_refine_summary(pair_output_dir, task_name)
    run_failure = load_run_failure(pair_output_dir)
    selected = refine_summary.get("selected") if isinstance(refine_summary, dict) else None
    best_observed = compute_best_observed_round(rounds)
    official_scores = pair_spec.get("official_scores") or {}
    c0_pct = official_scores.get("no_skills")
    c1_pct = official_scores.get("with_skills")
    selected_reward = selected.get("reward") if isinstance(selected, dict) else None
    selected_score_pct = pct_from_reward(selected_reward)
    failure = build_failure_summary(
        run_failure=run_failure,
        launcher_block=launcher_block,
        rounds=rounds,
    )
    timeout_detected = detect_timeout(
        json.dumps(run_failure or {}, sort_keys=True),
        json.dumps([round_info.get("exception_stats") for round_info in rounds], sort_keys=True),
        "\n".join(launcher_block),
    )
    launcher_status = launcher_result.get("status")
    raw_run_status = run_status.get("status")
    effective_run_status = raw_run_status
    stale_run_status = False
    if launcher_status == "failed" and raw_run_status in {None, "running"}:
        effective_run_status = "failed"
        stale_run_status = raw_run_status == "running"
    elif launcher_status == "succeeded" and raw_run_status in {None, "running"}:
        effective_run_status = "completed"
        stale_run_status = raw_run_status == "running"

    round_event_sequence = [
        {
            "round_index": round_info.get("round_index"),
            "event_times": round_info.get("event_times") or {},
        }
        for round_info in rounds
    ]
    reported_round_index = selected.get("round_index") if isinstance(selected, dict) else None
    reported_reward_raw = selected_reward
    reported_score_pct = selected_score_pct
    score_basis = "selected"
    if reported_score_pct is None and best_observed is not None:
        reported_round_index = best_observed.get("round_index")
        reported_reward_raw = best_observed.get("reward_raw")
        reported_score_pct = best_observed.get("score_pct")
        score_basis = "best_observed"

    evidence_class, diagnosis_note = classify_evidence(
        launcher_status=launcher_status,
        run_status=effective_run_status,
        failure=failure,
        timeout_detected=timeout_detected,
        has_intermediate_exceptions=any(bool(round_info.get("exception_stats")) for round_info in rounds),
        reported_score_pct=reported_score_pct,
    )

    return {
        "pair_id": launcher_result["pair_id"],
        "task_name": task_name,
        "schema_id": launcher_result["schema_id"],
        "official_scores": {
            "c0_pct": c0_pct if isinstance(c0_pct, (int, float)) else None,
            "c1_pct": c1_pct if isinstance(c1_pct, (int, float)) else None,
        },
        "launcher": {
            "status": launcher_result.get("status"),
            "stage": launcher_result.get("stage"),
            "returncode": launcher_result.get("returncode"),
            "started_at": pair_timing.get("started_at"),
            "finished_at": pair_timing.get("finished_at"),
            "duration_sec": duration_seconds(pair_timing.get("started_at"), pair_timing.get("finished_at")),
        },
        "run": {
            "status": effective_run_status,
            "raw_status": raw_run_status,
            "stale_status": stale_run_status,
            "round_budget": int(run_status["round_budget"]) if run_status.get("round_budget", "").isdigit() else None,
            "updated_at": run_status.get("updated_at"),
            "output_dir": str(pair_output_dir),
        },
        "selected": {
            "round_index": selected.get("round_index") if isinstance(selected, dict) else None,
            "reward_raw": selected_reward,
            "score_pct": selected_score_pct,
            "classification": selected.get("classification") if isinstance(selected, dict) else None,
        },
        "best_observed": {
            "round_index": None if best_observed is None else best_observed.get("round_index"),
            "reward_raw": None if best_observed is None else best_observed.get("reward_raw"),
            "score_pct": None if best_observed is None else best_observed.get("score_pct"),
        },
        "reported_score": {
            "basis": score_basis,
            "round_index": reported_round_index,
            "reward_raw": reported_reward_raw,
            "score_pct": reported_score_pct,
        },
        "delta_vs_c0_pp": (
            round(reported_score_pct - float(c0_pct), 2)
            if reported_score_pct is not None and isinstance(c0_pct, (int, float))
            else None
        ),
        "delta_vs_c1_pp": (
            round(reported_score_pct - float(c1_pct), 2)
            if reported_score_pct is not None and isinstance(c1_pct, (int, float))
            else None
        ),
        "early_stop": detect_early_stop(run_status=run_status, rounds=rounds),
        "timeout_detected": timeout_detected,
        "evidence_class": evidence_class,
        "diagnosis_note": diagnosis_note,
        "failure": failure,
        "has_intermediate_exceptions": any(bool(round_info.get("exception_stats")) for round_info in rounds),
        "runtime": {
            "round_event_sequence": round_event_sequence,
            "terminal_round_index": max((int(round_info["round_index"]) for round_info in rounds), default=None),
        },
        "evaluation_matrix": build_evaluation_matrix(rounds),
        "rounds": rounds,
        "launcher_log_excerpt": launcher_block[-12:],
    }


def summarize_failure_groups(pair_reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for pair_report in pair_reports:
        if pair_report["launcher"]["status"] != "failed":
            continue
        summary = pair_report.get("failure", {}).get("summary") or "unknown failure"
        groups[summary].append(pair_report["pair_id"])
    grouped_rows: list[dict[str, Any]] = []
    for summary, pair_ids in sorted(groups.items()):
        grouped_rows.append(
            {
                "summary": summary,
                "count": len(pair_ids),
                "pair_ids": sorted(pair_ids),
            }
        )
    return grouped_rows


def build_run_report(*, materialized_root: Path, run_label: str) -> dict[str, Any]:
    log_dir = materialized_root / "launcher_logs" / run_label
    summary_path = log_dir / "summary.json"
    events_path = log_dir / "events.ndjson"
    stdout_path = log_dir / "launcher.stdout.log"
    pair_specs_path = materialized_root / "pair_specs.jsonl"

    summary = read_json(summary_path)
    pair_specs = load_pair_specs(pair_specs_path)
    events = read_ndjson(events_path)
    pair_timings = index_pair_timings(events)
    launcher_blocks = parse_launcher_stdout_blocks(stdout_path)
    pair_reports = [
        build_pair_report(
            launcher_result=item,
            pair_spec=pair_specs[item["pair_id"]],
            pair_timing=pair_timings.get(item["pair_id"], {}),
            launcher_block=launcher_blocks.get(item["pair_id"], []),
        )
        for item in summary["results"]
    ]
    start_times = [pair["launcher"]["started_at"] for pair in pair_reports if pair["launcher"]["started_at"]]
    finish_times = [pair["launcher"]["finished_at"] for pair in pair_reports if pair["launcher"]["finished_at"]]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_label": run_label,
        "materialized_root": str(materialized_root.resolve()),
        "artifacts": {
            "summary_path": str(summary_path),
            "events_path": str(events_path),
            "launcher_stdout_path": str(stdout_path),
            "pair_specs_path": str(pair_specs_path),
        },
        "tasks": sorted({pair["task_name"] for pair in pair_reports}),
        "pair_count_total": summary.get("total_pairs"),
        "pair_count_completed": summary.get("completed_pairs"),
        "pair_count_succeeded": summary.get("succeeded_pairs"),
        "pair_count_failed": summary.get("failed_pairs"),
        "started_at": min(start_times) if start_times else None,
        "finished_at": max(finish_times) if finish_times else None,
        "duration_sec": duration_seconds(min(start_times) if start_times else None, max(finish_times) if finish_times else None),
        "pair_results": pair_reports,
        "failure_groups": summarize_failure_groups(pair_reports),
    }
    return sanitize_payload(report)


def _format_number(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.1f}"


def _format_bool(value: bool) -> str:
    return "yes" if value else "no"


def _looks_infra_blocked(text: str) -> bool:
    lowered = text.lower()
    return any(
        needle in lowered
        for needle in (
            "docker memory too low",
            "out of memory",
            "cannot connect to the docker daemon",
            "failed to pull image",
            "image not found",
            "no space left on device",
        )
    )


def classify_evidence(
    *,
    launcher_status: str | None,
    run_status: str | None,
    failure: dict[str, Any] | None,
    timeout_detected: bool,
    has_intermediate_exceptions: bool,
    reported_score_pct: float | None,
) -> tuple[str, str]:
    failure_summary = ""
    if failure:
        failure_summary = " ".join(
            str(part)
            for part in (
                failure.get("summary"),
                failure.get("error_type"),
                failure.get("error_message"),
                failure.get("failed_stage"),
            )
            if part
        )
    if _looks_infra_blocked(failure_summary):
        return "infra-blocked", "Infrastructure blocked a fair task evaluation."
    if reported_score_pct is None:
        if timeout_detected or launcher_status == "failed" or run_status == "failed":
            return "runtime-blocked", "Run failed before clean verifier evidence was produced."
        return "ambiguous", "No clean score and no definitive blocker classification was available."
    if timeout_detected or has_intermediate_exceptions or failure:
        return "ambiguous", "A score exists, but runtime exceptions or failures make it hard to treat as clean evidence."
    return "measured", "Clean verifier-facing score available for comparison against C0/C1."


def render_results_table(report: dict[str, Any]) -> str:
    lines = [
        f"# SkillX Round0 Result Table: `{report['run_label']}`",
        "",
        f"- tasks: `{', '.join(report['tasks'])}`",
        f"- pairs: `{report['pair_count_completed']}/{report['pair_count_total']}` completed",
        f"- succeeded: `{report['pair_count_succeeded']}`",
        f"- failed: `{report['pair_count_failed']}`",
        f"- started_at: `{report['started_at']}`",
        f"- finished_at: `{report['finished_at']}`",
        f"- duration_sec: `{report['duration_sec']}`",
        "",
    ]

    pair_results = report["pair_results"]
    for task_name in report["tasks"]:
        lines.extend(
            [
                f"## {task_name}",
                "",
                "| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |",
                "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |",
            ]
        )
        for pair in [item for item in pair_results if item["task_name"] == task_name]:
            round_scores = {round_info["round_index"]: round_info.get("score_pct") for round_info in pair["rounds"]}
            reported_round_index = pair["reported_score"]["round_index"]
            reported_score_pct = pair["reported_score"]["score_pct"]
            reported_basis = pair["reported_score"]["basis"]
            final_best = (
                f"R{reported_round_index} ({_format_number(reported_score_pct)})"
                if reported_round_index is not None and reported_score_pct is not None and reported_basis == "selected"
                else (
                    f"BestObs R{reported_round_index} ({_format_number(reported_score_pct)})"
                    if reported_round_index is not None and reported_score_pct is not None
                    else "-"
                )
            )
            lines.append(
                "| "
                + " | ".join(
                    [
                        pair["schema_id"],
                        str(pair["launcher"]["status"]),
                        str(pair["launcher"]["returncode"]),
                        str(pair["run"]["status"]),
                        _format_number(pair["official_scores"]["c0_pct"]),
                        _format_number(pair["official_scores"]["c1_pct"]),
                        _format_number(round_scores.get(0)),
                        _format_number(round_scores.get(1)),
                        _format_number(round_scores.get(2)),
                        _format_number(round_scores.get(3)),
                        final_best,
                        _format_number(pair["delta_vs_c0_pp"]),
                        _format_number(pair["delta_vs_c1_pp"]),
                        str(pair["evidence_class"]),
                        _format_bool(pair["early_stop"]),
                        _format_bool(pair["timeout_detected"]),
                    ]
                )
                + " |"
            )
        lines.append("")

    lines.extend(["## Evidence Notes", ""])
    for pair in pair_results:
        lines.append(
            f"- `{pair['pair_id']}`: `{pair['evidence_class']}` - {pair['diagnosis_note']}"
        )
    lines.append("")

    failed_pairs = [pair for pair in pair_results if pair["launcher"]["status"] == "failed"]
    if failed_pairs:
        lines.extend(["## Failure Notes", ""])
        for pair in failed_pairs:
            failure = pair.get("failure") or {}
            summary = failure.get("summary") or "unknown failure"
            lines.append(
                f"- `{pair['pair_id']}`: `{summary}`"
            )
        lines.append("")

    return "\n".join(lines)


def render_runtime_status(report: dict[str, Any]) -> str:
    lines = [
        f"# SkillX Round0 Runtime Status: `{report['run_label']}`",
        "",
        "| Pair | Launcher | Return | Run | Evidence | Failure | Timeout | Early Stop | Started | Finished | Duration (s) |",
        "| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | ---: |",
    ]
    for pair in report["pair_results"]:
        failure_summary = (pair.get("failure") or {}).get("summary") or "-"
        lines.append(
            "| "
            + " | ".join(
                [
                    pair["pair_id"],
                    str(pair["launcher"]["status"]),
                    str(pair["launcher"]["returncode"]),
                    str(pair["run"]["status"]),
                    str(pair["evidence_class"]),
                    failure_summary,
                    _format_bool(bool(pair["timeout_detected"])),
                    _format_bool(bool(pair["early_stop"])),
                    str(pair["launcher"]["started_at"] or "-"),
                    str(pair["launcher"]["finished_at"] or "-"),
                    _format_number(pair["launcher"]["duration_sec"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Pair Details", ""])
    for pair in report["pair_results"]:
        lines.extend(
            [
                f"### {pair['pair_id']}",
                "",
                f"- launcher_status: `{pair['launcher']['status']}`",
                f"- run_status: `{pair['run']['status']}`",
                f"- returncode: `{pair['launcher']['returncode']}`",
                f"- stale_run_status: `{pair['run']['stale_status']}`",
                f"- timeout_detected: `{pair['timeout_detected']}`",
                f"- early_stop: `{pair['early_stop']}`",
                f"- evidence_class: `{pair['evidence_class']}`",
                f"- diagnosis_note: `{pair['diagnosis_note']}`",
            ]
        )
        failure = pair.get("failure") or {}
        if failure:
            lines.extend(
                [
                    f"- failure_type: `{failure.get('error_type')}`",
                    f"- failure_stage: `{failure.get('failed_stage')}`",
                    f"- failure_round: `{failure.get('failed_round')}`",
                    f"- failure_summary: `{failure.get('summary')}`",
                ]
            )
        lines.extend(
            [
                "",
                "| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |",
                "| ---: | --- | --- | --- | --- | --- |",
            ]
        )
        for round_info in pair["rounds"]:
            event_times = round_info.get("event_times") or {}
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(round_info["round_index"]),
                        str(event_times.get("round_started") or "-"),
                        str(event_times.get("executor_completed") or "-"),
                        str(event_times.get("role_a_completed") or "-"),
                        str(event_times.get("role_b_completed") or "-"),
                        str(round_info.get("decision") or "-"),
                    ]
                )
                + " |"
            )
        lines.append("")
    return "\n".join(lines)


def render_evaluation_matrices(report: dict[str, Any]) -> str:
    lines = [f"# SkillX Round0 Evaluation Matrices: `{report['run_label']}`", ""]
    for pair in report["pair_results"]:
        lines.extend(
            [
                f"## {pair['pair_id']}",
                "",
                "| Round | Score | Passed | Failed | Total | Errors | Exit | Classification | Decision | Terminal Exec Only | Exceptions |",
                "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
            ]
        )
        for row in pair["evaluation_matrix"]["rows"]:
            exception_text = json.dumps(row.get("exception_stats") or {}, sort_keys=True)
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row.get("round_index")),
                        _format_number(row.get("score_pct")),
                        str(row.get("passed_tests") if row.get("passed_tests") is not None else "-"),
                        str(row.get("failed_tests") if row.get("failed_tests") is not None else "-"),
                        str(row.get("total_tests") if row.get("total_tests") is not None else "-"),
                        str(row.get("n_errors") if row.get("n_errors") is not None else "-"),
                        str(row.get("pytest_exitcode") if row.get("pytest_exitcode") is not None else "-"),
                        str(row.get("classification_kind") or "-"),
                        str(row.get("decision") or "-"),
                        _format_bool(bool(row.get("terminal_executor_only"))),
                        exception_text,
                    ]
                )
                + " |"
            )
        lines.append("")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export structured SkillX round-0 run reports.")
    parser.add_argument("--materialized-root", type=Path, required=True)
    parser.add_argument("--run-label", required=True)
    parser.add_argument("--report-dir", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    report_dir = args.report_dir or (args.materialized_root / "reports" / args.run_label)
    report_dir.mkdir(parents=True, exist_ok=True)

    report = build_run_report(materialized_root=args.materialized_root, run_label=args.run_label)
    write_json(report_dir / "run_report.json", report)
    (report_dir / "results_table.md").write_text(render_results_table(report))
    (report_dir / "runtime_status.md").write_text(render_runtime_status(report))
    (report_dir / "evaluation_matrices.md").write_text(render_evaluation_matrices(report))
    print(f"wrote report artifacts to {report_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

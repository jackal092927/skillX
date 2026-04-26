#!/usr/bin/env python3
"""Build a merged SkillX round-0 checkpoint from a base run and reruns."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def selected_classification(pair: dict[str, Any]) -> str:
    classification = pair.get("selected", {}).get("classification")
    if isinstance(classification, dict):
        return str(classification.get("kind") or "")
    return ""


def selected_round_label(pair: dict[str, Any]) -> str:
    round_index = pair.get("reported_score", {}).get("round_index")
    if round_index is None:
        round_index = pair.get("selected", {}).get("round_index")
    return "" if round_index is None else f"R{round_index}"


def selected_score(pair: dict[str, Any]) -> float | None:
    value = pair.get("reported_score", {}).get("score_pct")
    if isinstance(value, (int, float)):
        return float(value)
    value = pair.get("selected", {}).get("score_pct")
    if isinstance(value, (int, float)):
        return float(value)
    return None


def index_report(report: dict[str, Any], source_label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for pair in report.get("pair_results", []):
        if not isinstance(pair, dict) or not isinstance(pair.get("pair_id"), str):
            continue
        copied = dict(pair)
        copied["source_run_label"] = source_label
        indexed[copied["pair_id"]] = copied
    return indexed


def merge_pair_reports(base_report: dict[str, Any], rerun_reports: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base_label = str(base_report.get("run_label") or "base")
    effective_by_pair = index_report(base_report, base_label)
    replacements: list[dict[str, Any]] = []
    for rerun_report in rerun_reports:
        rerun_label = str(rerun_report.get("run_label") or "rerun")
        for pair_id, rerun_pair in index_report(rerun_report, rerun_label).items():
            previous = effective_by_pair.get(pair_id)
            if previous is None:
                effective_by_pair[pair_id] = rerun_pair
                replacements.append(
                    {
                        "pair_id": pair_id,
                        "base_status": None,
                        "rerun_status": rerun_pair.get("launcher", {}).get("status"),
                        "rerun_label": rerun_label,
                    }
                )
                continue
            rerun_status = rerun_pair.get("launcher", {}).get("status")
            previous_status = previous.get("launcher", {}).get("status")
            if rerun_status == "succeeded" or previous_status != "succeeded":
                effective_by_pair[pair_id] = rerun_pair
                replacements.append(
                    {
                        "pair_id": pair_id,
                        "base_status": previous_status,
                        "rerun_status": rerun_status,
                        "rerun_label": rerun_label,
                    }
                )
    return sorted(effective_by_pair.values(), key=lambda item: (str(item.get("task_name")), str(item.get("schema_id")))), replacements


def build_task_summary(pair_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pair_results:
        by_task[str(pair.get("task_name"))].append(pair)
    rows: list[dict[str, Any]] = []
    for task_name, pairs in sorted(by_task.items()):
        complete_pairs = [pair for pair in pairs if pair.get("launcher", {}).get("status") == "succeeded"]
        scored = [(selected_score(pair), pair) for pair in complete_pairs]
        scored = [(score, pair) for score, pair in scored if score is not None]
        best_score = max((score for score, _ in scored), default=None)
        best_schemas = sorted(pair["schema_id"] for score, pair in scored if score == best_score)
        c0 = pairs[0].get("official_scores", {}).get("c0_pct") if pairs else None
        c1 = pairs[0].get("official_scores", {}).get("c1_pct") if pairs else None
        rows.append(
            {
                "task_name": task_name,
                "pair_count": len(pairs),
                "succeeded_pairs": len(complete_pairs),
                "all_7_succeeded": len(pairs) == 7 and len(complete_pairs) == 7,
                "c0_pct": c0,
                "c1_pct": c1,
                "best_score_pct": best_score,
                "best_schemas": best_schemas,
                "delta_vs_c0_pp": round(best_score - float(c0), 2) if best_score is not None and isinstance(c0, (int, float)) else None,
                "delta_vs_c1_pp": round(best_score - float(c1), 2) if best_score is not None and isinstance(c1, (int, float)) else None,
            }
        )
    return rows


def build_schema_summary(pair_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_schema: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pair_results:
        by_schema[str(pair.get("schema_id"))].append(pair)
    rows: list[dict[str, Any]] = []
    for schema_id, pairs in sorted(by_schema.items()):
        scores = [selected_score(pair) for pair in pairs]
        numeric_scores = [score for score in scores if score is not None]
        classifications = Counter(selected_classification(pair) or "unknown" for pair in pairs)
        rows.append(
            {
                "schema_id": schema_id,
                "pair_count": len(pairs),
                "succeeded_pairs": sum(1 for pair in pairs if pair.get("launcher", {}).get("status") == "succeeded"),
                "mean_score_pct": round(sum(numeric_scores) / len(numeric_scores), 2) if numeric_scores else None,
                "clean_success": classifications.get("clean_success", 0),
                "scientific_failure": classifications.get("scientific_failure", 0),
                "runtime_failure": classifications.get("runtime_failure", 0),
                "contract_failure": classifications.get("contract_failure", 0),
                "unknown_classification": classifications.get("unknown", 0),
            }
        )
    return rows


def build_pair_rows(pair_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pair in pair_results:
        rows.append(
            {
                "pair_id": pair.get("pair_id"),
                "task_name": pair.get("task_name"),
                "schema_id": pair.get("schema_id"),
                "source_run_label": pair.get("source_run_label"),
                "launcher_status": pair.get("launcher", {}).get("status"),
                "run_status": pair.get("run", {}).get("status"),
                "evidence_class": pair.get("evidence_class"),
                "selected_round": selected_round_label(pair),
                "selected_score_pct": selected_score(pair),
                "selected_classification": selected_classification(pair),
                "c0_pct": pair.get("official_scores", {}).get("c0_pct"),
                "c1_pct": pair.get("official_scores", {}).get("c1_pct"),
                "delta_vs_c0_pp": pair.get("delta_vs_c0_pp"),
                "delta_vs_c1_pp": pair.get("delta_vs_c1_pp"),
                "early_stop": pair.get("early_stop"),
                "timeout_detected": pair.get("timeout_detected"),
            }
        )
    return rows


def build_score_matrix_rows(pair_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    schemas = sorted({str(pair.get("schema_id")) for pair in pair_results})
    by_task: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for pair in pair_results:
        by_task[str(pair.get("task_name"))][str(pair.get("schema_id"))] = pair
    rows: list[dict[str, Any]] = []
    for task_name, by_schema in sorted(by_task.items()):
        row: dict[str, Any] = {"task_name": task_name}
        any_pair = next(iter(by_schema.values()))
        row["c0_pct"] = any_pair.get("official_scores", {}).get("c0_pct")
        row["c1_pct"] = any_pair.get("official_scores", {}).get("c1_pct")
        for schema_id in schemas:
            pair = by_schema.get(schema_id)
            row[f"{schema_id}.score_pct"] = selected_score(pair) if pair else None
            row[f"{schema_id}.round"] = selected_round_label(pair) if pair else None
            row[f"{schema_id}.classification"] = selected_classification(pair) if pair else None
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def render_markdown(summary: dict[str, Any], pair_rows: list[dict[str, Any]], task_rows: list[dict[str, Any]], schema_rows: list[dict[str, Any]]) -> str:
    lines = [
        f"# SkillX First20 Round0 Checkpoint: `{summary['checkpoint_label']}`",
        "",
        "## Scope",
        "",
        f"- base_run_label: `{summary['base_run_label']}`",
        f"- rerun_labels: `{', '.join(summary['rerun_labels'])}`",
        f"- tasks: `{summary['task_count']}`",
        f"- schemas: `{summary['schema_count']}`",
        f"- effective_pairs: `{summary['effective_pair_count']}`",
        f"- launcher_succeeded_pairs: `{summary['launcher_succeeded_pairs']}`",
        f"- launcher_failed_pairs: `{summary['launcher_failed_pairs']}`",
        f"- all_tasks_have_7_succeeded_pairs: `{summary['all_tasks_have_7_succeeded_pairs']}`",
        f"- generated_at: `{summary['generated_at']}`",
        "",
        "## Rerun Overlay",
        "",
        f"- base_failed_pairs: `{summary['base_failed_pairs']}`",
        f"- rerun_replaced_pairs: `{summary['rerun_replaced_pairs']}`",
        f"- final_failed_pairs: `{summary['launcher_failed_pairs']}`",
        "",
        "## Classification Summary",
        "",
        "| Classification | Count |",
        "| --- | ---: |",
    ]
    for name, count in sorted(summary["classification_counts"].items()):
        lines.append(f"| {name} | {count} |")

    lines.extend(["", "## Schema Summary", "", "| Schema | Pairs | Mean Score | Clean Success | Scientific Failure | Runtime Failure | Contract Failure |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for row in schema_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["schema_id"]),
                    fmt(row["pair_count"]),
                    fmt(row["mean_score_pct"]),
                    fmt(row["clean_success"]),
                    fmt(row["scientific_failure"]),
                    fmt(row["runtime_failure"]),
                    fmt(row["contract_failure"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Task Summary", "", "| Task | Pairs | C0 | C1 | Best Score | Best Schemas | dC0 | dC1 |", "| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |"])
    for row in task_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["task_name"]),
                    f"{row['succeeded_pairs']}/{row['pair_count']}",
                    fmt(row["c0_pct"]),
                    fmt(row["c1_pct"]),
                    fmt(row["best_score_pct"]),
                    ", ".join(row["best_schemas"]),
                    fmt(row["delta_vs_c0_pp"]),
                    fmt(row["delta_vs_c1_pp"]),
                ]
            )
            + " |"
        )

    scientific_failures = [row for row in pair_rows if row["selected_classification"] == "scientific_failure"]
    lines.extend(["", "## Scientific Failures", ""])
    if scientific_failures:
        for row in scientific_failures:
            lines.append(
                f"- `{row['pair_id']}`: selected `{row['selected_round']}` score `{fmt(row['selected_score_pct'])}` from `{row['source_run_label']}`"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Next Step", "", "- Use `final_pair_results.csv` / `score_matrix_wide.csv` as the effective round-0 input for assignment, diagnostics, and outer-loop schema update.", "- Treat `scientific_failure` rows as measured low-score evidence, not infrastructure failures.", ""])
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-run-report", type=Path, required=True)
    parser.add_argument("--rerun-report", type=Path, action="append", default=[])
    parser.add_argument("--checkpoint-label", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    base_report = read_json(args.base_run_report)
    rerun_reports = [read_json(path) for path in args.rerun_report]
    pair_results, replacements = merge_pair_reports(base_report, rerun_reports)
    pair_rows = build_pair_rows(pair_results)
    task_rows = build_task_summary(pair_results)
    schema_rows = build_schema_summary(pair_results)
    score_matrix_rows = build_score_matrix_rows(pair_results)
    classification_counts = Counter(row["selected_classification"] or "unknown" for row in pair_rows)
    launcher_status_counts = Counter(row["launcher_status"] or "unknown" for row in pair_rows)
    base_failed_pairs = [
        pair.get("pair_id")
        for pair in base_report.get("pair_results", [])
        if pair.get("launcher", {}).get("status") != "succeeded"
    ]
    summary = {
        "artifact_type": "skillx_first20_round0_checkpoint",
        "checkpoint_label": args.checkpoint_label,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_run_label": base_report.get("run_label"),
        "rerun_labels": [report.get("run_label") for report in rerun_reports],
        "base_run_report": str(args.base_run_report),
        "rerun_reports": [str(path) for path in args.rerun_report],
        "task_count": len(task_rows),
        "schema_count": len({row["schema_id"] for row in pair_rows}),
        "effective_pair_count": len(pair_rows),
        "launcher_succeeded_pairs": launcher_status_counts.get("succeeded", 0),
        "launcher_failed_pairs": len(pair_rows) - launcher_status_counts.get("succeeded", 0),
        "all_tasks_have_7_succeeded_pairs": all(row["all_7_succeeded"] for row in task_rows),
        "base_failed_pairs": len(base_failed_pairs),
        "base_failed_pair_ids": base_failed_pairs,
        "rerun_replaced_pairs": len(replacements),
        "rerun_replacements": replacements,
        "classification_counts": dict(classification_counts),
        "launcher_status_counts": dict(launcher_status_counts),
    }
    write_json(args.output_dir / "checkpoint_summary.json", summary)
    write_json(args.output_dir / "final_pair_results.json", pair_rows)
    write_json(args.output_dir / "task_summary.json", task_rows)
    write_json(args.output_dir / "schema_summary.json", schema_rows)
    write_json(args.output_dir / "score_matrix_wide.json", score_matrix_rows)
    write_csv(args.output_dir / "final_pair_results.csv", pair_rows)
    write_csv(args.output_dir / "task_summary.csv", task_rows)
    write_csv(args.output_dir / "schema_summary.csv", schema_rows)
    write_csv(args.output_dir / "score_matrix_wide.csv", score_matrix_rows)
    (args.output_dir / "checkpoint.md").write_text(render_markdown(summary, pair_rows, task_rows, schema_rows))
    print(f"wrote checkpoint artifacts to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

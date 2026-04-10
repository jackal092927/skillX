#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skillx.io_utils import ensure_dir, write_json


DEFAULT_INVENTORY_PATH = ROOT / "docs" / "plans" / "skillx" / "skillsbench-task-cluster-inputs-v0.1.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "skillx-skillsbench-001" / "results" / "official-task-results"
TASK_URL_TEMPLATE = "https://www.skillsbench.ai/tasks/{task_id}"
RESULT_ROW_PATTERN = re.compile(r'\{\\"task\\":\\".*?perfectCount\\":\d+\}')
CSV_FIELDNAMES = [
    "task_id",
    "source_url",
    "cached_at",
    "model",
    "model_short",
    "condition",
    "score",
    "trials",
    "pass_count",
    "perfect_count",
    "harness",
    "family",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_task_inventory(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        rows.append(
            {
                "task_id": payload["task_name"],
                "task_object_seed": payload["cluster_inputs"]["semantic_contract"]["task_object_seed"],
            }
        )
    return rows


def extract_results_rows(html: str, task_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for match in RESULT_ROW_PATTERN.finditer(html):
        raw = match.group(0)
        try:
            payload = json.loads(raw.replace('\\"', '"'))
        except json.JSONDecodeError:
            continue
        if payload.get("task") == task_id:
            rows.append(payload)
    return rows


def normalize_result_row(task_id: str, source_url: str, cached_at: str, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "source_url": source_url,
        "cached_at": cached_at,
        "model": row["model"],
        "model_short": row["modelShort"],
        "harness": row["harness"],
        "family": row["family"],
        "condition": row["condition"],
        "score": row["score"],
        "trials": row["trials"],
        "pass_count": row["passCount"],
        "perfect_count": row["perfectCount"],
    }


def fetch_task_html(task_id: str, timeout_sec: int = 30) -> str:
    url = TASK_URL_TEMPLATE.format(task_id=task_id)
    with urlopen(url, timeout=timeout_sec) as response:
        return response.read().decode("utf-8", "ignore")


def scrape_task_result(task_row: dict[str, str], *, cached_at: str) -> dict[str, Any]:
    task_id = task_row["task_id"]
    source_url = TASK_URL_TEMPLATE.format(task_id=task_id)
    try:
        html = fetch_task_html(task_id)
    except (HTTPError, URLError, TimeoutError) as exc:
        return {
            "task_id": task_id,
            "task_object_seed": task_row["task_object_seed"],
            "source_url": source_url,
            "cached_at": cached_at,
            "results": [],
            "error": str(exc),
            "raw_html": None,
        }
    rows = [normalize_result_row(task_id, source_url, cached_at, row) for row in extract_results_rows(html, task_id)]
    return {
        "task_id": task_id,
        "task_object_seed": task_row["task_object_seed"],
        "source_url": source_url,
        "cached_at": cached_at,
        "results": rows,
        "error": None if rows else "missing_results",
        "raw_html": html if not rows else None,
    }


def build_manifest(task_payloads: list[dict[str, Any]], *, cached_at: str) -> dict[str, Any]:
    aggregate_rows = [row for payload in task_payloads for row in payload["results"]]
    sonnet45_rows = [
        row
        for row in aggregate_rows
        if row["model"] == "Claude Code (Sonnet 4.5)" and row["condition"] == "With Skills"
    ]
    opus46_rows = [
        row
        for row in aggregate_rows
        if row["model"] == "Claude Code (Opus 4.6)" and row["condition"] == "With Skills"
    ]
    missing_results = [payload["task_id"] for payload in task_payloads if not payload["results"]]
    return {
        "cached_at": cached_at,
        "task_count_attempted": len(task_payloads),
        "task_count_succeeded": sum(1 for payload in task_payloads if payload["results"]),
        "task_count_missing_results": len(missing_results),
        "missing_results_tasks": missing_results,
        "baseline_coverage": {
            "claude_code_sonnet_4_5_with_skills": len(sonnet45_rows),
            "claude_code_opus_4_6_with_skills": len(opus46_rows),
        },
    }


def write_cache_outputs(
    *,
    output_dir: Path,
    task_payloads: list[dict[str, Any]],
    aggregate_rows: list[dict[str, Any]],
    manifest: dict[str, Any],
    save_raw_html_failures: bool = False,
) -> None:
    tasks_dir = ensure_dir(output_dir / "tasks")
    raw_html_dir = ensure_dir(output_dir / "raw_html") if save_raw_html_failures else None

    for payload in task_payloads:
        task_json_payload = {
            "task_id": payload["task_id"],
            "task_object_seed": payload.get("task_object_seed"),
            "source_url": payload["source_url"],
            "cached_at": payload["cached_at"],
            "results": payload["results"],
            "error": payload.get("error"),
        }
        write_json(tasks_dir / f"{payload['task_id']}.json", task_json_payload)
        if save_raw_html_failures and payload.get("raw_html") and raw_html_dir is not None:
            (raw_html_dir / f"{payload['task_id']}.html").write_text(payload["raw_html"])

    jsonl_path = output_dir / "official_task_results.jsonl"
    ensure_dir(jsonl_path.parent)
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in aggregate_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    csv_path = output_dir / "official_task_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for row in aggregate_rows:
            writer.writerow(row)

    write_json(output_dir / "manifest.json", manifest)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cache official SkillsBench task-level results to local artifacts.")
    parser.add_argument("--inventory-path", type=Path, default=DEFAULT_INVENTORY_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--task", action="append", help="Optional specific task id to cache. Repeatable.")
    parser.add_argument("--max-workers", type=int, default=8)
    parser.add_argument("--save-raw-html-failures", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    inventory = load_task_inventory(args.inventory_path.resolve())
    if args.task:
        requested = set(args.task)
        inventory = [row for row in inventory if row["task_id"] in requested]
    cached_at = utc_now()

    with ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as pool:
        task_payloads = list(pool.map(lambda row: scrape_task_result(row, cached_at=cached_at), inventory))

    task_payloads.sort(key=lambda row: row["task_id"])
    aggregate_rows = sorted(
        [result for payload in task_payloads for result in payload["results"]],
        key=lambda row: (row["task_id"], row["harness"], row["model_short"], row["condition"]),
    )
    manifest = build_manifest(task_payloads, cached_at=cached_at)
    write_cache_outputs(
        output_dir=args.output_dir.resolve(),
        task_payloads=task_payloads,
        aggregate_rows=aggregate_rows,
        manifest=manifest,
        save_raw_html_failures=args.save_raw_html_failures,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

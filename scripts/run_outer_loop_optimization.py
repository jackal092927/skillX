#!/usr/bin/env python3
"""Run the SkillX outer-loop control plane and materialize next-round pairs."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SRC = ROOT / "src"
for path in (SCRIPTS, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import build_round0_outer_loop_artifacts as control_plane  # noqa: E402
import build_round0_schema_update_package as schema_updates  # noqa: E402
import materialize_skillx_round0_runner as round_materializer  # noqa: E402
from skillx.io_utils import ensure_dir, write_json  # noqa: E402


DEFAULT_ROUND0_ROOT = (
    ROOT
    / "experiments"
    / "skillx-skillsbench-001"
    / "results"
    / "outer-loop-round0"
)
DEFAULT_CONTROL_PLANE_OUTPUT_DIR = DEFAULT_ROUND0_ROOT / "reports" / "outer-loop-control-plane"
DEFAULT_SCHEMA_UPDATE_OUTPUT_DIR = DEFAULT_ROUND0_ROOT / "reports" / "outer-loop-schema-updates"
DEFAULT_NEXT_MATERIALIZED_ROOT = DEFAULT_ROUND0_ROOT / "outer-loop-round1-candidate-rerun"
DEFAULT_GLOBAL_PAIR_STATUS_PATH = (
    DEFAULT_ROUND0_ROOT / "reports" / "global-round0-status" / "global_pair_status.json"
)
DEFAULT_PROMPT_BANK_PATH = ROOT / "docs" / "plans" / "skillx" / "skillx-prompt-bank-v0.1.json"
DEFAULT_TASK_CLUSTER_INPUTS_PATH = (
    ROOT / "docs" / "plans" / "skillx" / "skillsbench-task-cluster-inputs-v0.1.jsonl"
)
DEFAULT_OFFICIAL_RESULTS_PATH = (
    ROOT
    / "experiments"
    / "skillx-skillsbench-001"
    / "results"
    / "official-task-results"
    / "official_task_results.jsonl"
)
DEFAULT_RENDER_TEMPLATE_PATH = ROOT / "docs" / "plans" / "skillx" / "skillx-render-template-frozen-v0.1.md"
DEFAULT_OAUTH_FILE = Path.home() / ".claude" / "claude-code-oauth-token"
DEFAULT_ROUND_ID = "outer-loop-round0"
DEFAULT_NEXT_ROUND_ID = "outer-loop-round1"
DEFAULT_NEXT_RUN_ID = "outer-loop-round1-candidates"
DEFAULT_ROUND_BUDGET = 3


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


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


def infer_skillsbench_root() -> Path:
    try:
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--git-common-dir"],
            check=True,
            capture_output=True,
            text=True,
        )
        git_common_dir = Path(proc.stdout.strip())
        if not git_common_dir.is_absolute():
            git_common_dir = (ROOT / git_common_dir).resolve()
        shared_repo_root = git_common_dir.parent
        return shared_repo_root.parent / "skillsbench-src"
    except Exception:
        return ROOT.parent / "skillsbench-src"


def category_by_id(prompt_bank_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    categories = prompt_bank_payload.get("categories")
    if not isinstance(categories, list):
        raise ValueError("candidate prompt bank missing categories")
    for category in categories:
        if not isinstance(category, dict):
            continue
        category_id = category.get("category_id")
        if isinstance(category_id, str) and category_id:
            rows[category_id] = category
    return rows


def evidence_task_names(evidence: dict[str, Any], key: str) -> set[str]:
    names: set[str] = set()
    for row in evidence.get(key, []) or []:
        if isinstance(row, dict) and isinstance(row.get("task_name"), str):
            names.add(str(row["task_name"]))
    return names


def build_next_round_pair_plan(package: dict[str, Any]) -> list[dict[str, Any]]:
    evidence_by_schema = package.get("schema_evidence_bundles") or {}
    candidate_by_schema = category_by_id(package["candidate_prompt_bank"])
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for plan_row in package.get("challenger_eval_plan", []):
        if not isinstance(plan_row, dict):
            continue
        schema_id = str(plan_row.get("schema_id") or "")
        if not schema_id:
            continue
        candidate_schema = candidate_by_schema.get(schema_id, {})
        evidence = evidence_by_schema.get(schema_id, {})
        assigned_names = evidence_task_names(evidence, "assigned_task_summaries")
        boundary_names = evidence_task_names(evidence, "ambiguous_borderline_cases")
        cross_loss_names = evidence_task_names(evidence, "cross_schema_losses")
        for task_name in plan_row.get("task_names", []) or []:
            if not isinstance(task_name, str) or not task_name:
                continue
            dedupe_key = (task_name, schema_id)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            reasons: list[str] = []
            if task_name in assigned_names:
                reasons.append("assigned_support")
            if task_name in boundary_names:
                reasons.append("boundary_case")
            if task_name in cross_loss_names:
                reasons.append("competitor_check")
            if not reasons:
                reasons.append("challenger_eval")
            rows.append(
                {
                    "pair_id": f"{task_name}__{schema_id}",
                    "task_name": task_name,
                    "schema_id": schema_id,
                    "candidate_mode": plan_row.get("candidate_mode"),
                    "outer_loop_candidate_id": candidate_schema.get("outer_loop_candidate_id"),
                    "pair_reason": ";".join(reasons),
                    "source_round_id": package["config"]["round_id"],
                    "next_round_id": package["config"]["next_round_id"],
                }
            )
    return rows


def render_outer_loop_pair_meta_block(pair_plan: dict[str, Any], schema: dict[str, Any]) -> str:
    lines = [
        "",
        "[Outer-loop candidate block]",
        f"Source round: {pair_plan['source_round_id']}",
        f"Next round: {pair_plan['next_round_id']}",
        f"Candidate id: {pair_plan.get('outer_loop_candidate_id') or 'incumbent'}",
        f"Candidate mode: {pair_plan.get('candidate_mode') or schema.get('outer_loop_candidate_mode') or 'incumbent'}",
        f"Pair reason: {pair_plan['pair_reason']}",
        "Use this as a candidate schema rerun, not as an accepted final schema.",
    ]
    return "\n".join(lines) + "\n"


def materialize_next_round_pairs(
    *,
    package: dict[str, Any],
    output_dir: Path,
    skillsbench_root: Path,
    inventory_path: Path,
    official_results_path: Path,
    render_template_path: Path,
    run_id: str,
    round_budget: int,
    oauth_file: Path,
    agent: str,
    model: str,
    schema_update_package_path: Path | None,
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    ensure_dir(output_dir)
    skillsbench_root = skillsbench_root.resolve()
    inventory = round_materializer.load_task_inventory(inventory_path)
    official_scores = round_materializer.load_official_scores(
        official_results_path,
        model_name="Claude Code (Sonnet 4.5)",
    )
    schema_bank = category_by_id(package["candidate_prompt_bank"])
    pair_plan = build_next_round_pair_plan(package)
    pairs_dir = ensure_dir(output_dir / "pairs")
    pair_specs: list[dict[str, Any]] = []

    for row in pair_plan:
        task_name = row["task_name"]
        schema_id = row["schema_id"]
        if schema_id not in schema_bank:
            raise KeyError(f"schema {schema_id} missing from candidate prompt bank")
        inventory_row = inventory.get(task_name)
        if inventory_row is None:
            raise KeyError(f"task {task_name} missing from inventory")
        task = round_materializer.materialize_task(skillsbench_root, inventory_row, task_name)
        baseline_scores = official_scores.get(task_name, {})
        schema = schema_bank[schema_id]
        pair_id = str(row["pair_id"])
        pair_dir = ensure_dir(pairs_dir / pair_id)
        rendered = round_materializer.render_meta_skill(
            schema=schema,
            task=task,
            inventory_row=inventory_row,
            baseline_scores=baseline_scores,
        )
        rendered += render_outer_loop_pair_meta_block(row, schema)
        rendered_meta_skill_path = pair_dir / "rendered_meta_skill.md"
        rendered_meta_skill_path.write_text(rendered)
        pair_spec = {
            "pair_id": pair_id,
            "run_id": run_id,
            "round_id": package["config"]["next_round_id"],
            "task_name": task_name,
            "schema_id": schema_id,
            "candidate_mode": row.get("candidate_mode"),
            "outer_loop_candidate_id": row.get("outer_loop_candidate_id"),
            "pair_reason": row["pair_reason"],
            "source_round_id": package["config"]["round_id"],
            "schema_update_package_path": (
                None if schema_update_package_path is None else display_path(schema_update_package_path.resolve())
            ),
            "pair_dir": round_materializer.materialized_relative_path(pair_dir, materialized_root=output_dir),
            "skillsbench_task_dir": str(task.task_dir),
            "starting_skillpack_dir": str(task.skills_dir),
            "starting_label": "C1",
            "official_scores": {
                "no_skills": baseline_scores.get("No Skills"),
                "with_skills": baseline_scores.get("With Skills"),
            },
            "rendered_meta_skill_path": round_materializer.materialized_relative_path(
                rendered_meta_skill_path,
                materialized_root=output_dir,
            ),
            "refine_command": round_materializer.build_refine_command(
                materialized_root=output_dir,
                pair_dir=pair_dir,
                skillsbench_root=skillsbench_root,
                task=task,
                oauth_file=oauth_file,
                round_budget=round_budget,
                agent=agent,
                model=model,
            ),
        }
        write_json(pair_dir / "pair_spec.json", pair_spec)
        pair_specs.append(pair_spec)

    schema_ids = sorted({str(row["schema_id"]) for row in pair_plan})
    task_names = sorted({str(row["task_name"]) for row in pair_plan})
    manifest = {
        "artifact_type": "skillx_outer_loop_next_round_materialization_manifest",
        "run_id": run_id,
        "round_id": package["config"]["next_round_id"],
        "source_round_id": package["config"]["round_id"],
        "render_template_path": display_path(render_template_path.resolve()),
        "candidate_prompt_bank_path": "round1_candidate_prompt_bank.json",
        "schema_update_package_path": (
            None if schema_update_package_path is None else display_path(schema_update_package_path.resolve())
        ),
        "inventory_path": display_path(inventory_path.resolve()),
        "official_results_path": display_path(official_results_path.resolve()),
        "skillsbench_root": str(skillsbench_root),
        "task_count": len(task_names),
        "schema_count": len(schema_ids),
        "pair_count": len(pair_specs),
        "round_budget": round_budget,
        "agent": agent,
        "model": model,
        "schema_ids": schema_ids,
        "task_names": task_names,
        "path_strategy": {
            "pair_dir": "materialized_root_relative",
            "rendered_meta_skill_path": "materialized_root_relative",
            "refine_command_cwd": "materialized_root",
        },
    }

    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "next_round_pair_plan.json", {"pairs": pair_plan})
    write_json(output_dir / "round1_candidate_prompt_bank.json", package["candidate_prompt_bank"])
    write_csv(
        output_dir / "next_round_pair_plan.csv",
        pair_plan,
        [
            "pair_id",
            "task_name",
            "schema_id",
            "candidate_mode",
            "outer_loop_candidate_id",
            "pair_reason",
            "source_round_id",
            "next_round_id",
        ],
    )
    (output_dir / "pair_specs.jsonl").write_text(
        "".join(json.dumps(pair_spec, sort_keys=True) + "\n" for pair_spec in pair_specs)
    )
    (output_dir / "launch_next_round.sh").write_text(
        "#!/bin/sh\nset -eu\n\nSCRIPT_DIR=$(CDPATH= cd -- \"$(dirname \"$0\")\" && pwd)\ncd \"$SCRIPT_DIR\"\n\n"
        + "\n".join(" ".join(pair["refine_command"]) for pair in pair_specs)
        + "\n"
    )
    os.chmod(output_dir / "launch_next_round.sh", 0o755)
    return {
        "manifest": manifest,
        "pair_plan": pair_plan,
        "pair_specs": pair_specs,
        "outputs": {
            "manifest_json": display_path(output_dir / "manifest.json"),
            "pair_specs_jsonl": display_path(output_dir / "pair_specs.jsonl"),
            "next_round_pair_plan_json": display_path(output_dir / "next_round_pair_plan.json"),
            "next_round_pair_plan_csv": display_path(output_dir / "next_round_pair_plan.csv"),
            "candidate_prompt_bank_json": display_path(output_dir / "round1_candidate_prompt_bank.json"),
            "launch_script": display_path(output_dir / "launch_next_round.sh"),
        },
    }


def run_outer_loop_optimization(
    *,
    round0_root: Path,
    global_pair_status_path: Path,
    prompt_bank_path: Path,
    task_cluster_inputs_path: Path | None,
    control_plane_output_dir: Path,
    schema_update_output_dir: Path,
    next_materialized_root: Path,
    skillsbench_root: Path,
    inventory_path: Path,
    official_results_path: Path,
    render_template_path: Path,
    oauth_file: Path,
    round_id: str,
    next_round_id: str,
    next_run_id: str,
    round_budget: int,
    agent: str,
    model: str,
    rewrite_mode: str,
    llm_model: str,
    llm_timeout_sec: float,
    max_update_schemas: int,
    max_eval_tasks_per_schema: int,
    min_support_size: int,
    allow_partial_assignment: bool,
) -> dict[str, Any]:
    control_payload = control_plane.build_outer_loop_artifacts(
        round0_root=round0_root,
        global_pair_status_path=global_pair_status_path,
        prompt_bank_path=prompt_bank_path,
        task_cluster_inputs_path=task_cluster_inputs_path,
        round_id=round_id,
        assignment_score_mode=control_plane.DEFAULT_ASSIGNMENT_SCORE_MODE,
        terminal_score_weight=control_plane.DEFAULT_TERMINAL_SCORE_WEIGHT,
        round_mean_score_weight=control_plane.DEFAULT_ROUND_MEAN_SCORE_WEIGHT,
        growth_score_weight=control_plane.DEFAULT_GROWTH_SCORE_WEIGHT,
        epsilon_pp=control_plane.DEFAULT_MEDIUM_CONFIDENCE_MARGIN_PP,
        high_confidence_margin_pp=control_plane.DEFAULT_HIGH_CONFIDENCE_MARGIN_PP,
        medium_confidence_margin_pp=control_plane.DEFAULT_MEDIUM_CONFIDENCE_MARGIN_PP,
        require_full_coverage=not allow_partial_assignment,
        dominant_share_threshold=control_plane.DEFAULT_DOMINANT_SHARE_THRESHOLD,
        top3_tie_threshold_pp=control_plane.DEFAULT_TOP3_TIE_THRESHOLD_PP,
        near_empty_threshold=control_plane.DEFAULT_NEAR_EMPTY_THRESHOLD,
        update_floor_fraction=control_plane.DEFAULT_UPDATE_FLOOR_FRACTION,
        flat_column_range_pp=control_plane.DEFAULT_FLAT_COLUMN_RANGE_PP,
    )
    control_outputs = control_plane.write_outer_loop_artifacts(
        payload=control_payload,
        output_dir=control_plane_output_dir,
    )
    control_bundle_path = control_plane_output_dir / "control_plane_bundle.json"

    package = schema_updates.build_schema_update_package(
        control_plane_bundle_path=control_bundle_path,
        prompt_bank_path=prompt_bank_path,
        task_cluster_inputs_path=task_cluster_inputs_path,
        rewrite_mode=rewrite_mode,
        llm_model=llm_model,
        llm_timeout_sec=llm_timeout_sec,
        llm_work_dir=schema_update_output_dir / "llm_runs",
        round_id=round_id,
        next_round_id=next_round_id,
        min_support_size=min_support_size,
        low_margin_pp=schema_updates.DEFAULT_LOW_MARGIN_PP,
        boundary_margin_pp=schema_updates.DEFAULT_BOUNDARY_MARGIN_PP,
        max_update_schemas=max_update_schemas,
        max_eval_tasks_per_schema=max_eval_tasks_per_schema,
    )
    schema_update_outputs = schema_updates.write_schema_update_package(
        package=package,
        output_dir=schema_update_output_dir,
    )
    materialized = materialize_next_round_pairs(
        package=package,
        output_dir=next_materialized_root,
        skillsbench_root=skillsbench_root,
        inventory_path=inventory_path,
        official_results_path=official_results_path,
        render_template_path=render_template_path,
        run_id=next_run_id,
        round_budget=round_budget,
        oauth_file=oauth_file,
        agent=agent,
        model=model,
        schema_update_package_path=schema_update_output_dir / "schema_update_package.json",
    )
    summary = {
        "artifact_type": "skillx_outer_loop_optimization_run",
        "round_id": round_id,
        "next_round_id": next_round_id,
        "control_plane_outputs": control_outputs,
        "schema_update_outputs": schema_update_outputs,
        "next_round_materialized_outputs": materialized["outputs"],
        "next_round_pair_count": len(materialized["pair_specs"]),
        "next_round_schema_count": materialized["manifest"]["schema_count"],
        "next_round_task_count": materialized["manifest"]["task_count"],
    }
    write_json(schema_update_output_dir / "outer_loop_optimization_summary.json", summary)
    return {
        "summary": summary,
        "control_plane": control_payload,
        "schema_update_package": package,
        "next_round_materialization": materialized,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round0-root", type=Path, default=DEFAULT_ROUND0_ROOT)
    parser.add_argument("--global-pair-status-path", type=Path, default=DEFAULT_GLOBAL_PAIR_STATUS_PATH)
    parser.add_argument("--prompt-bank-path", type=Path, default=DEFAULT_PROMPT_BANK_PATH)
    parser.add_argument("--task-cluster-inputs-path", type=Path, default=DEFAULT_TASK_CLUSTER_INPUTS_PATH)
    parser.add_argument("--control-plane-output-dir", type=Path, default=DEFAULT_CONTROL_PLANE_OUTPUT_DIR)
    parser.add_argument("--schema-update-output-dir", type=Path, default=DEFAULT_SCHEMA_UPDATE_OUTPUT_DIR)
    parser.add_argument("--next-materialized-root", type=Path, default=DEFAULT_NEXT_MATERIALIZED_ROOT)
    parser.add_argument("--skillsbench-root", type=Path, default=infer_skillsbench_root())
    parser.add_argument("--inventory-path", type=Path, default=DEFAULT_TASK_CLUSTER_INPUTS_PATH)
    parser.add_argument("--official-results-path", type=Path, default=DEFAULT_OFFICIAL_RESULTS_PATH)
    parser.add_argument("--render-template-path", type=Path, default=DEFAULT_RENDER_TEMPLATE_PATH)
    parser.add_argument("--oauth-file", type=Path, default=DEFAULT_OAUTH_FILE)
    parser.add_argument("--round-id", default=DEFAULT_ROUND_ID)
    parser.add_argument("--next-round-id", default=DEFAULT_NEXT_ROUND_ID)
    parser.add_argument("--next-run-id", default=DEFAULT_NEXT_RUN_ID)
    parser.add_argument("--round-budget", type=int, default=DEFAULT_ROUND_BUDGET)
    parser.add_argument("--agent", default=round_materializer.DEFAULT_AGENT)
    parser.add_argument("--model", default=round_materializer.DEFAULT_MODEL)
    parser.add_argument(
        "--rewrite-mode",
        choices=["llm", "deterministic"],
        default=schema_updates.DEFAULT_REWRITE_MODE,
    )
    parser.add_argument("--llm-model", default=schema_updates.DEFAULT_LLM_MODEL)
    parser.add_argument("--llm-timeout-sec", type=float, default=schema_updates.DEFAULT_LLM_TIMEOUT_SEC)
    parser.add_argument(
        "--max-update-schemas",
        type=int,
        default=schema_updates.DEFAULT_MAX_UPDATE_SCHEMAS,
        help="Maximum schemas to rewrite by priority; 0 rewrites all eligible schemas.",
    )
    parser.add_argument("--max-eval-tasks-per-schema", type=int, default=6)
    parser.add_argument(
        "--min-support-size",
        type=int,
        default=schema_updates.DEFAULT_MIN_SUPPORT_SIZE,
        help="Reliable assigned-task support floor before rewriting; 0 rewrites all schemas.",
    )
    parser.add_argument("--allow-partial-assignment", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    result = run_outer_loop_optimization(
        round0_root=args.round0_root,
        global_pair_status_path=args.global_pair_status_path,
        prompt_bank_path=args.prompt_bank_path,
        task_cluster_inputs_path=args.task_cluster_inputs_path,
        control_plane_output_dir=args.control_plane_output_dir,
        schema_update_output_dir=args.schema_update_output_dir,
        next_materialized_root=args.next_materialized_root,
        skillsbench_root=args.skillsbench_root,
        inventory_path=args.inventory_path,
        official_results_path=args.official_results_path,
        render_template_path=args.render_template_path,
        oauth_file=args.oauth_file,
        round_id=str(args.round_id),
        next_round_id=str(args.next_round_id),
        next_run_id=str(args.next_run_id),
        round_budget=int(args.round_budget),
        agent=str(args.agent),
        model=str(args.model),
        rewrite_mode=str(args.rewrite_mode),
        llm_model=str(args.llm_model),
        llm_timeout_sec=float(args.llm_timeout_sec),
        max_update_schemas=int(args.max_update_schemas),
        max_eval_tasks_per_schema=int(args.max_eval_tasks_per_schema),
        min_support_size=int(args.min_support_size),
        allow_partial_assignment=bool(args.allow_partial_assignment),
    )
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

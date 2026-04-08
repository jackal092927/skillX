#!/usr/bin/env python3
"""Materialize a SkillX round-0 outer-loop manifest and pair specs."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skillx.io_utils import ensure_dir, write_json


DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"
DEFAULT_AGENT = "claude-code"


@dataclass(frozen=True)
class TaskMaterialization:
    task_name: str
    task_dir: Path
    skills_dir: Path
    instruction_path: Path
    task_toml_path: Path
    skill_names: list[str]
    current_task_skill: str
    task_summary: str
    task_constraints: list[str]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_prompt_bank(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text())
    categories = payload.get("categories")
    if not isinstance(categories, list):
        raise ValueError("prompt bank missing categories")
    result: dict[str, dict[str, Any]] = {}
    for category in categories:
        category_id = category.get("category_id")
        if not isinstance(category_id, str) or not category_id:
            raise ValueError("prompt bank category missing category_id")
        result[category_id] = category
    return result


def load_task_slice(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    tasks = payload.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("task slice missing tasks")
    return tasks


def load_task_inventory(path: Path) -> dict[str, dict[str, Any]]:
    inventory: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(path):
        task_name = row.get("task_name")
        if isinstance(task_name, str) and task_name:
            inventory[task_name] = row
    return inventory


def load_official_scores(path: Path, *, model_name: str) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {}
    for row in _read_jsonl(path):
        if row.get("model") != model_name:
            continue
        task_id = row.get("task_id")
        condition = row.get("condition")
        score = row.get("score")
        if not isinstance(task_id, str) or not isinstance(condition, str) or not isinstance(score, (int, float)):
            continue
        scores.setdefault(task_id, {})[condition] = float(score)
    return scores


def summarize_instruction(path: Path) -> str:
    lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if not lines:
        return "No instruction summary available."
    return " ".join(lines[:2])


def read_current_task_skill(skills_dir: Path) -> tuple[list[str], str]:
    skill_paths = sorted(skills_dir.glob("*/SKILL.md"))
    if not skill_paths:
        raise FileNotFoundError(f"no SKILL.md files found under {skills_dir}")
    skill_names = [path.parent.name for path in skill_paths]
    parts: list[str] = []
    for path in skill_paths:
        parts.append(f"## {path.parent.name}\n{path.read_text().rstrip()}\n")
    return skill_names, "\n".join(parts).strip() + "\n"


def materialize_task(skillsbench_root: Path, inventory_row: dict[str, Any], task_name: str) -> TaskMaterialization:
    task_dir = skillsbench_root / "tasks" / task_name
    instruction_path = task_dir / "instruction.md"
    task_toml_path = task_dir / "task.toml"
    skills_dir = task_dir / "environment" / "skills"
    missing = [path for path in (instruction_path, task_toml_path, skills_dir) if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing task inputs for {task_name}: {[str(path) for path in missing]}")
    skill_names, current_task_skill = read_current_task_skill(skills_dir)
    semantic = inventory_row.get("cluster_inputs", {}).get("semantic_contract", {})
    topology = inventory_row.get("cluster_inputs", {}).get("tool_topology", {})
    tags = inventory_row.get("tags", {})
    constraints = [
        f"seed schema prior: {semantic.get('task_object_seed', 'unknown')}",
        f"verifier mode: {semantic.get('verifier_mode', 'unknown')}",
        f"workflow topology: {topology.get('workflow_topology', 'unknown')}",
        f"tool surface regime: {topology.get('tool_surface_regime', 'unknown')}",
        f"primary pattern: {tags.get('primary_pattern', 'unknown')}",
        f"annotation confidence: {tags.get('confidence', 'unknown')}",
    ]
    secondary = tags.get("secondary_patterns")
    if isinstance(secondary, list) and secondary:
        constraints.append(f"secondary patterns: {', '.join(str(item) for item in secondary)}")
    return TaskMaterialization(
        task_name=task_name,
        task_dir=task_dir,
        skills_dir=skills_dir,
        instruction_path=instruction_path,
        task_toml_path=task_toml_path,
        skill_names=skill_names,
        current_task_skill=current_task_skill,
        task_summary=summarize_instruction(instruction_path),
        task_constraints=constraints,
    )


def render_meta_skill(
    *,
    schema: dict[str, Any],
    task: TaskMaterialization,
    inventory_row: dict[str, Any],
    baseline_scores: dict[str, float],
) -> str:
    emphasize = schema.get("emphasize") or []
    avoid = schema.get("avoid") or []
    good_fit = schema.get("expected_good_fit") or []
    bad_fit = schema.get("expected_bad_fit") or []
    evidence_note = inventory_row.get("tags", {}).get("evidence_note", "No annotation evidence note available.")
    no_skills = baseline_scores.get("No Skills")
    with_skills = baseline_scores.get("With Skills")
    delta = None if no_skills is None or with_skills is None else round(with_skills - no_skills, 1)

    def _render_list(values: list[Any]) -> list[str]:
        return [f"- {value}" for value in values] if values else ["- none recorded"]

    lines = [
        "[Common wrapper]",
        "You are revising a Task skill, not directly solving the task.",
        "Use the provided Meta schema as class-level guidance.",
        "Your goal is to improve the Task skill for this task while preserving useful existing structure.",
        "",
        "[Meta schema block]",
        f"Category: {schema['category_id']}",
        f"Semantic intent: {schema.get('semantic_intent', 'unspecified')}",
        "Emphasize:",
        *_render_list(emphasize),
        "Avoid:",
        *_render_list(avoid),
        "Expected good fit:",
        *_render_list(good_fit),
        "Expected bad fit:",
        *_render_list(bad_fit),
        "Hypothesized primary failure modes:",
        "- unavailable in prompt-bank-v0.1; use task-local evidence instead",
        "Meta schema seed guidance:",
        str(schema.get("meta_prompt", "No meta prompt available.")).strip(),
        "",
        "[Task context block]",
        f"Task name: {task.task_name}",
        f"Task summary: {task.task_summary}",
        "Task constraints:",
        *[f"- {item}" for item in task.task_constraints],
        "Task output requirements:",
        f"- verifier note: {inventory_row.get('cluster_inputs', {}).get('semantic_contract', {}).get('verifier_mode', 'unknown')}",
        f"- current skill count: {len(task.skill_names)}",
        "",
        "[Current Task skill block]",
        "Current Task skill:",
        task.current_task_skill.rstrip(),
        "",
        "[Evidence block]",
        f"No Skills: `{_format_score(no_skills)}`",
        f"With Skills: `{_format_score(with_skills)}`",
        f"Delta: `{_format_score(delta)}`",
        f"Failure summary: {evidence_note}",
        "Competing schema note: No prior round-0 pair evidence available.",
        "",
        "[Output contract block]",
        "Return YAML with fields:",
        "revised_task_skill, change_summary{keep/add/remove/sharpen}, rationale",
        "",
        "```yaml",
        "revised_task_skill: |",
        "  ...",
        "change_summary:",
        "  keep:",
        "    - ...",
        "  add:",
        "    - ...",
        "  remove:",
        "    - ...",
        "  sharpen:",
        "    - ...",
        "rationale: |",
        "  ...",
        "```",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _format_score(value: float | None) -> str:
    if value is None:
        return "unavailable"
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def build_refine_command(
    *,
    pair_dir: Path,
    skillsbench_root: Path,
    task: TaskMaterialization,
    oauth_file: Path,
    round_budget: int,
    agent: str,
    model: str,
) -> list[str]:
    run_dir = pair_dir / "refine_run"
    source_stub = pair_dir / "source_stub"
    ensure_dir(source_stub)
    return [
        "python3.12",
        str(ROOT / "scripts" / "run_skillx_refine_benchmark.py"),
        "--skillsbench-root",
        str(skillsbench_root),
        "--task",
        task.task_name,
        "--run-id",
        pair_dir.name,
        "--output-dir",
        str(run_dir),
        "--oauth-file",
        str(oauth_file),
        "--source-run-dir",
        str(source_stub),
        "--starting-skillpack-dir",
        str(task.skills_dir),
        "--starting-label",
        "C1",
        "--round-budget",
        str(round_budget),
        "--agent",
        agent,
        "--model",
        model,
        "--orchestration-mode",
        "c4ar",
    ]


def build_round0_materialization(
    *,
    skillsbench_root: Path,
    task_slice_path: Path,
    prompt_bank_path: Path,
    inventory_path: Path,
    official_results_path: Path,
    render_template_path: Path,
    output_dir: Path,
    run_id: str,
    round_budget: int,
    oauth_file: Path,
    agent: str = DEFAULT_AGENT,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    skillsbench_root = skillsbench_root.resolve()
    output_dir = output_dir.resolve()
    ensure_dir(output_dir)

    prompt_bank = load_prompt_bank(prompt_bank_path)
    task_slice = load_task_slice(task_slice_path)
    inventory = load_task_inventory(inventory_path)
    official_scores = load_official_scores(official_results_path, model_name="Claude Code (Sonnet 4.5)")
    schema_ids = list(prompt_bank.keys())

    pairs_dir = ensure_dir(output_dir / "pairs")
    pair_specs: list[dict[str, Any]] = []

    for task_row in task_slice:
        task_name = task_row["task_name"]
        inventory_row = inventory.get(task_name)
        if inventory_row is None:
            raise KeyError(f"task {task_name} missing from inventory")
        task = materialize_task(skillsbench_root, inventory_row, task_name)
        baseline_scores = official_scores.get(task_name, {})
        for schema_id in schema_ids:
            schema = prompt_bank[schema_id]
            pair_id = f"{task_name}__{schema_id}"
            pair_dir = ensure_dir(pairs_dir / pair_id)
            rendered = render_meta_skill(
                schema=schema,
                task=task,
                inventory_row=inventory_row,
                baseline_scores=baseline_scores,
            )
            (pair_dir / "rendered_meta_skill.md").write_text(rendered)
            pair_spec = {
                "pair_id": pair_id,
                "run_id": run_id,
                "task_name": task_name,
                "schema_id": schema_id,
                "pair_dir": str(pair_dir),
                "skillsbench_task_dir": str(task.task_dir),
                "starting_skillpack_dir": str(task.skills_dir),
                "starting_label": "C1",
                "official_scores": {
                    "no_skills": baseline_scores.get("No Skills"),
                    "with_skills": baseline_scores.get("With Skills"),
                },
                "rendered_meta_skill_path": str(pair_dir / "rendered_meta_skill.md"),
                "refine_command": build_refine_command(
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

    manifest = {
        "artifact_type": "skillx_round0_materialization_manifest",
        "run_id": run_id,
        "round_id": "pilot-round-0",
        "render_template_path": str(render_template_path),
        "task_slice_path": str(task_slice_path),
        "prompt_bank_path": str(prompt_bank_path),
        "inventory_path": str(inventory_path),
        "official_results_path": str(official_results_path),
        "skillsbench_root": str(skillsbench_root),
        "task_count": len(task_slice),
        "schema_count": len(schema_ids),
        "pair_count": len(pair_specs),
        "round_budget": round_budget,
        "agent": agent,
        "model": model,
        "schema_ids": schema_ids,
        "task_names": [task["task_name"] for task in task_slice],
    }
    write_json(output_dir / "manifest.json", manifest)
    (output_dir / "pair_specs.jsonl").write_text(
        "".join(json.dumps(pair_spec) + "\n" for pair_spec in pair_specs)
    )
    (output_dir / "launch_round0.sh").write_text(
        "#!/bin/sh\nset -eu\n\n" + "\n".join(" ".join(pair["refine_command"]) for pair in pair_specs) + "\n"
    )
    return {"manifest": manifest, "pair_specs": pair_specs}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skillsbench-root", type=Path, required=True)
    parser.add_argument("--task-slice", type=Path, required=True)
    parser.add_argument("--prompt-bank", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--official-results", type=Path, required=True)
    parser.add_argument("--render-template", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--oauth-file", type=Path, required=True)
    parser.add_argument("--round-budget", type=int, default=3)
    parser.add_argument("--agent", default=DEFAULT_AGENT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    build_round0_materialization(
        skillsbench_root=args.skillsbench_root,
        task_slice_path=args.task_slice,
        prompt_bank_path=args.prompt_bank,
        inventory_path=args.inventory,
        official_results_path=args.official_results,
        render_template_path=args.render_template,
        output_dir=args.output_dir,
        run_id=args.run_id,
        round_budget=args.round_budget,
        oauth_file=args.oauth_file,
        agent=args.agent,
        model=args.model,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

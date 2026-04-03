from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_utils import read_json
from .models import (
    SkillXC3Result,
    SkillXC4Summary,
    SkillXResultClassification,
    SkillXRoundResult,
)


def _resolve_file(root: Path, direct_name: str, nested_name: str) -> Path:
    if root.is_file():
        return root
    direct = root / direct_name
    if direct.exists():
        return direct
    nested = list(root.glob(nested_name))
    if len(nested) == 1:
        return nested[0]
    if not nested:
        raise FileNotFoundError(f"could not find {direct_name} under {root}")
    raise RuntimeError(f"expected one {direct_name} under {root}, found {len(nested)}")


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def classify_skillx_outcome(
    *,
    reward: float | None,
    exception_stats: dict[str, Any],
    reward_missing: bool = False,
) -> SkillXResultClassification:
    if exception_stats:
        return SkillXResultClassification(
            kind="runtime_failure",
            reason="exception_stats_present",
            has_exception_stats=True,
            reward_is_missing=reward is None or reward_missing,
            reward_is_zero=reward == 0.0,
        )
    if reward_missing or reward is None:
        return SkillXResultClassification(
            kind="contract_failure",
            reason="reward_missing_or_unparseable",
            reward_is_missing=True,
        )
    if reward <= 0.0:
        return SkillXResultClassification(
            kind="scientific_failure",
            reason="clean_zero_or_negative_reward",
            reward_is_zero=reward == 0.0,
        )
    return SkillXResultClassification(
        kind="clean_success",
        reason="positive_reward_with_no_exception_stats",
    )


def _parse_reward_from_payload(payload: dict[str, Any]) -> tuple[float | None, str | None, dict[str, Any], int | None, int | None, bool]:
    stats = payload.get("stats")
    if not isinstance(stats, dict):
        return None, None, {}, None, None, True
    n_trials = stats.get("n_trials")
    n_errors = stats.get("n_errors")
    evals = stats.get("evals")
    if not isinstance(evals, dict) or not evals:
        return None, None, {}, n_trials, n_errors, True
    eval_name, eval_payload = next(iter(evals.items()))
    if not isinstance(eval_payload, dict):
        return None, eval_name, {}, n_trials, n_errors, True
    exception_stats = eval_payload.get("exception_stats") or {}
    if not isinstance(exception_stats, dict):
        exception_stats = {"__unparsed__": exception_stats}
    metrics = eval_payload.get("metrics") or []
    reward = None
    if isinstance(metrics, list) and metrics:
        first_metric = metrics[0]
        if isinstance(first_metric, dict):
            reward = _coerce_float(first_metric.get("mean"))
    reward_missing = reward is None
    return reward, eval_name, exception_stats, n_trials, n_errors, reward_missing


def load_skillx_c3_result(run_dir: Path) -> SkillXC3Result:
    result_path = _resolve_file(run_dir, "result.json", "*/result.json")
    payload = read_json(result_path)
    reward, eval_name, exception_stats, n_trials, n_errors, reward_missing = _parse_reward_from_payload(payload)
    classification = classify_skillx_outcome(
        reward=reward,
        exception_stats=exception_stats,
        reward_missing=reward_missing,
    )
    source_run_dir = str(run_dir.resolve()) if run_dir.exists() else str(run_dir)
    if not run_dir.is_dir():
        source_run_dir = str(result_path.parent.resolve())
    return SkillXC3Result(
        task_id=str(payload.get("task_id") or result_path.parent.name.replace("-c3", "")),
        condition=str(payload.get("condition") or "c3"),
        reward=reward,
        result_path=str(result_path.resolve()),
        source_run_dir=source_run_dir,
        eval_name=eval_name,
        exception_stats=exception_stats,
        n_trials=n_trials if isinstance(n_trials, int) else None,
        n_errors=n_errors if isinstance(n_errors, int) else None,
        classification=classification,
        raw=payload,
    )


def load_skillx_c4_summary(run_dir: Path) -> SkillXC4Summary:
    summary_path = _resolve_file(run_dir, "refine_summary.json", "refine/*/refine_summary.json")
    payload = read_json(summary_path)
    task_id = str(payload.get("task_id") or summary_path.parent.name)
    selected = payload.get("selected") or {}
    selected_round_index = selected.get("round_index")
    selected_reward = _coerce_float(selected.get("reward"))
    rounds_payload = payload.get("rounds") or []
    rounds: list[SkillXRoundResult] = []
    if isinstance(rounds_payload, list):
        for row in rounds_payload:
            if not isinstance(row, dict):
                continue
            reward = _coerce_float(row.get("reward"))
            exception_stats = row.get("exception_stats") or {}
            if not isinstance(exception_stats, dict):
                exception_stats = {"__unparsed__": exception_stats}
            classification = classify_skillx_outcome(
                reward=reward,
                exception_stats=exception_stats,
                reward_missing=reward is None,
            )
            round_index = row.get("round_index")
            rounds.append(
                SkillXRoundResult(
                    round_index=int(round_index) if isinstance(round_index, int) else -1,
                    reward=reward,
                    result_path=str(row.get("result_path") or ""),
                    round_dir=str(row.get("round_dir") or ""),
                    eval_name=row.get("eval_name"),
                    exception_stats=exception_stats,
                    n_trials=row.get("n_trials") if isinstance(row.get("n_trials"), int) else None,
                    n_errors=row.get("n_errors") if isinstance(row.get("n_errors"), int) else None,
                    classification=classification,
                    raw=row,
                )
            )
    selected_result_path = selected.get("result_path")
    selected_round_dir = selected.get("round_dir")
    source_run_dir = str(run_dir.resolve()) if run_dir.exists() else str(run_dir)
    if not run_dir.is_dir():
        source_run_dir = str(summary_path.parent.parent.resolve())
    return SkillXC4Summary(
        task_id=task_id,
        source_run_dir=source_run_dir,
        selected_round_index=int(selected_round_index) if isinstance(selected_round_index, int) else -1,
        selected_reward=selected_reward,
        selected_result_path=str(selected_result_path) if selected_result_path is not None else None,
        selected_round_dir=str(selected_round_dir) if selected_round_dir is not None else None,
        rounds=rounds,
        raw=payload,
    )

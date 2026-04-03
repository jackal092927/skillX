from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class SkillXResultClassification:
    kind: str
    reason: str
    has_exception_stats: bool = False
    reward_is_missing: bool = False
    reward_is_zero: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SkillXC3Result:
    task_id: str
    condition: str
    reward: float | None
    result_path: str
    source_run_dir: str
    eval_name: str | None
    exception_stats: dict[str, Any]
    n_trials: int | None
    n_errors: int | None
    classification: SkillXResultClassification
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "condition": self.condition,
            "reward": self.reward,
            "result_path": self.result_path,
            "source_run_dir": self.source_run_dir,
            "eval_name": self.eval_name,
            "exception_stats": self.exception_stats,
            "n_trials": self.n_trials,
            "n_errors": self.n_errors,
            "classification": self.classification.to_dict(),
            "raw": self.raw,
        }


@dataclass(slots=True)
class SkillXRoundResult:
    round_index: int
    reward: float | None
    result_path: str
    round_dir: str
    eval_name: str | None
    exception_stats: dict[str, Any]
    n_trials: int | None
    n_errors: int | None
    classification: SkillXResultClassification
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "round_index": self.round_index,
            "reward": self.reward,
            "result_path": self.result_path,
            "round_dir": self.round_dir,
            "eval_name": self.eval_name,
            "exception_stats": self.exception_stats,
            "n_trials": self.n_trials,
            "n_errors": self.n_errors,
            "classification": self.classification.to_dict(),
            "raw": self.raw,
        }


@dataclass(slots=True)
class SkillXC4Summary:
    task_id: str
    source_run_dir: str
    selected_round_index: int
    selected_reward: float | None
    selected_result_path: str | None
    selected_round_dir: str | None
    rounds: list[SkillXRoundResult]
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "source_run_dir": self.source_run_dir,
            "selected_round_index": self.selected_round_index,
            "selected_reward": self.selected_reward,
            "selected_result_path": self.selected_result_path,
            "selected_round_dir": self.selected_round_dir,
            "rounds": [round_result.to_dict() for round_result in self.rounds],
            "raw": self.raw,
        }

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .evidence import classify_skillx_outcome
from .models import SkillXC3Result, SkillXC4Summary, SkillXResultClassification, SkillXRoundResult
from .session_evidence import SessionDerivedEvidence


@dataclass(slots=True)
class SkillXDecisionBundle:
    task_id: str
    c3_result: SkillXC3Result
    c4_summary: SkillXC4Summary | None = None
    session_evidence: SessionDerivedEvidence | None = None
    source_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "c3_result": self.c3_result.to_dict(),
            "c4_summary": None if self.c4_summary is None else self.c4_summary.to_dict(),
            "session_evidence": None if self.session_evidence is None else self.session_evidence.to_dict(),
            "source_notes": self.source_notes,
        }


@dataclass(slots=True)
class SkillXRoundDisposition:
    retry_allowed: bool
    keep_candidate: bool
    reason: str
    classification_kind: str
    classification_reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SkillXRefineIntent:
    primary_action: str
    edit_targets: list[str] = field(default_factory=list)
    rationale: str = ""
    preserve_core_structure: bool = True
    compress_derived_layer: bool = False
    de_bloat_derived_layer: bool = False
    anti_speculation: bool = False
    source_signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_skillx_decision_bundle(
    *,
    c3_result: SkillXC3Result,
    c4_summary: SkillXC4Summary | None = None,
    session_evidence: SessionDerivedEvidence | None = None,
    source_notes: list[str] | None = None,
) -> SkillXDecisionBundle:
    return SkillXDecisionBundle(
        task_id=c3_result.task_id,
        c3_result=c3_result,
        c4_summary=c4_summary,
        session_evidence=session_evidence,
        source_notes=list(source_notes or []),
    )


def _selected_round(bundle: SkillXDecisionBundle) -> SkillXRoundResult | None:
    if bundle.c4_summary is None:
        return None
    for round_result in bundle.c4_summary.rounds:
        if round_result.round_index == bundle.c4_summary.selected_round_index:
            return round_result
    return None


def _effective_classification(bundle: SkillXDecisionBundle) -> SkillXResultClassification:
    selected_round = _selected_round(bundle)
    if selected_round is not None:
        return selected_round.classification
    if bundle.c4_summary is not None and bundle.c4_summary.selected_reward is not None:
        return classify_skillx_outcome(
            reward=bundle.c4_summary.selected_reward,
            exception_stats={},
            reward_missing=False,
        )
    return bundle.c3_result.classification


def _has_churn_signal(bundle: SkillXDecisionBundle) -> bool:
    evidence = bundle.session_evidence
    if evidence is None:
        return False
    if evidence.wasted_loop_signals:
        return True
    text = evidence.dominant_failure_pattern.lower()
    return "loop" in text or "churn" in text or "low-progress" in text


def _has_improvement_signal(bundle: SkillXDecisionBundle) -> bool:
    if bundle.c4_summary is None:
        return False
    selected_reward = bundle.c4_summary.selected_reward
    current_reward = bundle.c3_result.reward
    if selected_reward is None or current_reward is None:
        return False
    return selected_reward > current_reward


def _session_signal_text(bundle: SkillXDecisionBundle) -> list[str]:
    signals: list[str] = []
    if bundle.session_evidence is None:
        return signals
    if bundle.session_evidence.wasted_loop_signals:
        signals.append("session churn")
    if bundle.session_evidence.tool_misuse_signals:
        signals.append("tool misuse")
    if bundle.session_evidence.skill_misguidance_signals:
        signals.append("skill misguidance")
    if bundle.session_evidence.critical_turns:
        signals.append("critical turn")
    return signals


def decide_round_disposition(bundle: SkillXDecisionBundle) -> SkillXRoundDisposition:
    classification = _effective_classification(bundle)
    if classification.kind == "contract_failure":
        return SkillXRoundDisposition(
            retry_allowed=True,
            keep_candidate=False,
            reason="retryable contract failure",
            classification_kind=classification.kind,
            classification_reason=classification.reason,
        )
    if classification.kind == "runtime_failure":
        return SkillXRoundDisposition(
            retry_allowed=False,
            keep_candidate=False,
            reason="runtime failure is not retryable in this loop",
            classification_kind=classification.kind,
            classification_reason=classification.reason,
        )
    if classification.kind == "scientific_failure":
        return SkillXRoundDisposition(
            retry_allowed=False,
            keep_candidate=False,
            reason="scientific failure should be recorded, not retried blindly",
            classification_kind=classification.kind,
            classification_reason=classification.reason,
        )
    return SkillXRoundDisposition(
        retry_allowed=False,
        keep_candidate=True,
        reason="clean success can remain as the current candidate",
        classification_kind=classification.kind,
        classification_reason=classification.reason,
    )


def decide_refine_intent(bundle: SkillXDecisionBundle) -> SkillXRefineIntent:
    classification = _effective_classification(bundle)
    signals = _session_signal_text(bundle)

    if classification.kind == "contract_failure":
        return SkillXRefineIntent(
            primary_action="repair_contract",
            edit_targets=["restore_missing_output", "repair_artifact_contract"],
            rationale="Only contract failures are retryable, so the next round should repair the missing or malformed output contract.",
            preserve_core_structure=True,
            source_signals=signals,
        )

    if _has_improvement_signal(bundle) and _has_churn_signal(bundle):
        return SkillXRefineIntent(
            primary_action="compress_derived_layer",
            edit_targets=[
                "compress_derived_layer",
                "de_bloat_derived_layer",
                "reduce_repeated_retry_loop",
                "tighten_scope_boundary",
                "remove_speculative_evaluator_content",
            ],
            rationale=(
                "The selected C4 round improved over C3 while the session log shows repeated low-progress churn, "
                "so the next intent should preserve the useful structure but apply compression, de-bloating, and anti-speculation."
            ),
            preserve_core_structure=True,
            compress_derived_layer=True,
            de_bloat_derived_layer=True,
            anti_speculation=True,
            source_signals=signals or ["improved_reward", "session_churn"],
        )

    if bundle.session_evidence is not None and bundle.session_evidence.skill_misguidance_signals:
        return SkillXRefineIntent(
            primary_action="remove_speculative_evaluator_content",
            edit_targets=[
                "remove_speculative_evaluator_content",
                "tighten_scope_boundary",
            ],
            rationale="The session evidence suggests the skill is over-guiding the agent, so the next round should remove speculative evaluator-facing detail.",
            preserve_core_structure=True,
            anti_speculation=True,
            source_signals=signals or ["skill_misguidance"],
        )

    if bundle.session_evidence is not None and bundle.session_evidence.tool_misuse_signals:
        return SkillXRefineIntent(
            primary_action="clarify_tool_choice",
            edit_targets=[
                "clarify_tool_choice",
                "tighten_scope_boundary",
            ],
            rationale="The session evidence suggests tool choice is unclear, so the next round should make tool selection rules explicit and bounded.",
            preserve_core_structure=True,
            source_signals=signals or ["tool_misuse"],
        )

    if classification.kind == "scientific_failure":
        return SkillXRefineIntent(
            primary_action="tighten_scope_boundary",
            edit_targets=[
                "tighten_scope_boundary",
                "preserve_core_structure",
            ],
            rationale="A clean scientific failure should not be retried blindly; the safer move is to tighten the scope boundary and preserve the core shape.",
            preserve_core_structure=True,
            source_signals=signals or ["scientific_failure"],
        )

    if classification.kind == "runtime_failure":
        return SkillXRefineIntent(
            primary_action="stabilize_execution",
            edit_targets=[
                "stabilize_execution",
                "preserve_core_structure",
            ],
            rationale="Runtime failure means the next step should stabilize execution details before refining the substance of the skill.",
            preserve_core_structure=True,
            source_signals=signals or ["runtime_failure"],
        )

    return SkillXRefineIntent(
        primary_action="preserve_core_structure",
        edit_targets=["preserve_core_structure"],
        rationale="The current evidence is stable enough that the safest next move is to preserve the core structure and avoid unnecessary edits.",
        preserve_core_structure=True,
        source_signals=signals or ["clean_success"],
    )

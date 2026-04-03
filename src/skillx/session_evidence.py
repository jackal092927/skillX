from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


_WHITESPACE_RE = re.compile(r"\s+")
_JSONISH_RE = re.compile(r"^\s*[\[{]")
_KEY_VALUE_RE = re.compile(r"(?P<key>[A-Za-z_][A-Za-z0-9_-]*)=(?P<value>[^=]+?)(?=\s+[A-Za-z_][A-Za-z0-9_-]*=|$)")
_LOW_SIGNAL_ACTIONS = {"bash", "todowrite", "todo_write", "plan", "think", "wait", "idle"}
_LOW_SIGNAL_EVENT_TYPES = {"user", "assistant", "queue-operation", "system", "result"}
_MISUSE_PATTERNS = (
    "wrong tool",
    "tool misuse",
    "misuse",
    "unsupported tool",
    "failed to parse",
    "tool error",
)
_CRITICAL_PATTERNS = (
    "timeout",
    "exception",
    "verifier",
    "contract failed",
    "missing refined skill",
    "missing derived layer",
    "error",
    "failed",
)
_MISGUIDANCE_PATTERNS = (
    "misleading",
    "misguide",
    "over-guidance",
    "too verbose",
    "too much guidance",
    "skill may be misleading",
)


@dataclass(slots=True)
class SessionDerivedEvidence:
    source_paths: tuple[str, ...]
    dominant_failure_pattern: str
    wasted_loop_signals: list[str] = field(default_factory=list)
    tool_misuse_signals: list[str] = field(default_factory=list)
    critical_turns: list[str] = field(default_factory=list)
    skill_misguidance_signals: list[str] = field(default_factory=list)
    recommended_edit_targets: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    observed_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class _SessionEvent:
    source_path: Path
    line_no: int
    raw_text: str
    normalized_text: str
    summary_text: str
    signal_key: str | None

    @property
    def evidence_ref(self) -> str:
        return f"{self.source_path}:{self.line_no}"


def _normalize_text(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text.strip().lower())


def _shorten(text: str, limit: int = 140) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _first_nonempty(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, (list, tuple, dict)) and not value:
            continue
        return value
    return None


def _scalar_text(value: Any) -> str | None:
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    if isinstance(value, (int, float, bool)):
        return str(value)
    return None


def _summarize_message_content(content: Any) -> str | None:
    if isinstance(content, str):
        return _shorten(content, 120)
    if isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                continue
            item_type = _scalar_text(item.get("type")) or ""
            if item_type == "tool_use":
                tool_name = _scalar_text(item.get("name")) or "tool"
                tool_input = item.get("input")
                description = None
                command = None
                if isinstance(tool_input, dict):
                    description = _scalar_text(tool_input.get("description"))
                    command = _scalar_text(tool_input.get("command"))
                detail = description or command
                if detail:
                    return _shorten(f"tool_use {tool_name}: {detail}", 120)
                return _shorten(f"tool_use {tool_name}", 120)
            if item_type == "text":
                text = _scalar_text(item.get("text"))
                if text:
                    return _shorten(text, 120)
            if item_type == "thinking":
                continue
    return None


def _split_key_values(text: str) -> dict[str, str]:
    return {match.group("key").lower(): match.group("value").strip() for match in _KEY_VALUE_RE.finditer(text)}


def _summarize_json_payload(payload: Any) -> str:
    if isinstance(payload, dict):
        payload_type = _scalar_text(payload.get("type"))
        if payload_type == "queue-operation":
            operation = _scalar_text(payload.get("operation"))
            content = _summarize_message_content(payload.get("content"))
            if operation and content:
                return _shorten(f"{operation}: {content}", 120)
            if operation:
                return _shorten(f"queue {operation}", 120)
        if payload_type in {"user", "assistant"}:
            message = payload.get("message")
            if isinstance(message, dict):
                role = _scalar_text(message.get("role")) or payload_type
                content_summary = _summarize_message_content(message.get("content"))
                if content_summary:
                    return _shorten(f"{role}: {content_summary}", 120)
                status_summary = _scalar_text(message.get("status"))
                if status_summary and status_summary.lower() not in _LOW_SIGNAL_EVENT_TYPES:
                    return _shorten(f"{role}: {status_summary}", 120)
        status = _scalar_text(_first_nonempty(payload.get("status"), payload.get("type")))
        tool = _scalar_text(_first_nonempty(payload.get("tool"), payload.get("action"), payload.get("name")))
        path = _scalar_text(_first_nonempty(payload.get("path"), payload.get("file")))
        message = _scalar_text(
            _first_nonempty(
                payload.get("message"),
                payload.get("observation"),
                payload.get("error"),
                payload.get("exception_info"),
                payload.get("stdout"),
                payload.get("stderr"),
                payload.get("content"),
                payload.get("prompt"),
            )
        )
        pieces: list[str] = []
        if status:
            pieces.append(str(status))
        if tool and str(tool).lower() not in _LOW_SIGNAL_ACTIONS:
            pieces.append(str(tool))
        if path:
            pieces.append(str(path))
        if message:
            pieces.append(str(message))
        if pieces:
            if len(pieces) == 1 and str(pieces[0]).lower() in _LOW_SIGNAL_EVENT_TYPES:
                return ""
            return _shorten(" ".join(pieces), 120)
        extracted = _extract_text_from_json_value(payload)
        if extracted:
            return _shorten(" ".join(extracted[:2]), 120)
    if isinstance(payload, list):
        extracted = _extract_text_from_json_value(payload)
        if extracted:
            return _shorten(" ".join(extracted[:2]), 120)
    return ""


def _summarize_text_payload(text: str) -> str:
    kv = _split_key_values(text)
    tool = kv.get("tool") or kv.get("action")
    if tool:
        pieces = [tool]
        path = kv.get("path") or kv.get("file")
        if path:
            pieces.append(path)
        message = kv.get("message") or kv.get("observation") or kv.get("error")
        if message:
            pieces.append(message)
        return _shorten(" ".join(pieces), 120)
    return _shorten(text, 120)


def _summarize_payload(raw_text: str, payload: Any | None) -> str:
    if payload is not None:
        summary = _summarize_json_payload(payload)
        if summary:
            return summary
    return _summarize_text_payload(raw_text)


def _action_signature(summary_text: str, normalized_text: str) -> str | None:
    summary_lower = summary_text.lower().strip()
    normalized_lower = normalized_text.lower().strip()
    if not summary_lower:
        return None
    if summary_lower in _LOW_SIGNAL_ACTIONS or summary_lower in _LOW_SIGNAL_EVENT_TYPES:
        return None
    if summary_lower.startswith("bash ") or summary_lower.startswith("todowrite "):
        return None
    if normalized_lower in _LOW_SIGNAL_ACTIONS:
        return None

    if any(pattern in normalized_lower for pattern in _CRITICAL_PATTERNS):
        return f"failure:{summary_lower}"
    if any(pattern in normalized_lower for pattern in _MISUSE_PATTERNS):
        return f"misuse:{summary_lower}"

    if (
        "=" not in summary_text
        and len(summary_lower.split()) <= 2
        and all(token in _LOW_SIGNAL_EVENT_TYPES for token in summary_lower.split())
    ):
        return None
    if any(token in summary_lower for token in ("read_file", "search", "edit", "open", "click", "run", "exec", "write", "tool_use")):
        return f"action:{summary_lower}"
    return None


def _extract_text_from_json_value(value: Any) -> list[str]:
    texts: list[str] = []
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned:
            texts.append(cleaned)
    elif isinstance(value, dict):
        for key in (
            "message",
            "content",
            "text",
            "action",
            "observation",
            "command",
            "tool",
            "path",
            "name",
            "status",
            "stdout",
            "stderr",
            "prompt",
        ):
            if key in value:
                texts.extend(_extract_text_from_json_value(value[key]))
    elif isinstance(value, list):
        for item in value:
            texts.extend(_extract_text_from_json_value(item))
    return texts


def _read_session_events(paths: Iterable[Path]) -> list[_SessionEvent]:
    events: list[_SessionEvent] = []
    for source_path in paths:
        for line_no, line in enumerate(source_path.read_text().splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload: Any | None = None
            payload_text = stripped
            if _JSONISH_RE.match(stripped):
                try:
                    payload = json.loads(stripped)
                except json.JSONDecodeError:
                    payload = None
            if payload is not None:
                extracted = _extract_text_from_json_value(payload)
                if extracted:
                    payload_text = " | ".join(extracted[:3])
            summary_text = _summarize_payload(stripped, payload)
            signal_key = _action_signature(summary_text, _normalize_text(payload_text))
            events.append(
                _SessionEvent(
                    source_path=source_path,
                    line_no=line_no,
                    raw_text=stripped,
                    normalized_text=_normalize_text(payload_text),
                    summary_text=summary_text,
                    signal_key=signal_key,
                )
            )
    return events


def _rank_dominant_pattern(events: list[_SessionEvent]) -> str:
    if not events:
        return "no session evidence available"
    counts = Counter(event.normalized_text for event in events if event.normalized_text)
    if not counts:
        return "no structured signal extracted"
    top_text, top_count = counts.most_common(1)[0]
    if top_count >= 3:
        return f"repeated execution loop ({top_count}x): {_shorten(top_text)}"
    if any(pattern in top_text for pattern in _CRITICAL_PATTERNS):
        return f"critical failure pressure: {_shorten(top_text)}"
    if any(pattern in top_text for pattern in _MISGUIDANCE_PATTERNS):
        return f"skill misguidance: {_shorten(top_text)}"
    return f"mixed session signals: {_shorten(top_text)}"


def _collect_repeated_loop_signals(events: list[_SessionEvent]) -> list[str]:
    counts = Counter(event.signal_key for event in events if event.signal_key)
    signals: list[str] = []
    for signal_key, count in counts.most_common():
        if count < 3:
            continue
        if len(signals) >= 3:
            break
        if signal_key is None:
            continue
        signals.append(f"Repeated wasted loop {count}x: {_shorten(signal_key.removeprefix('action:').removeprefix('failure:').removeprefix('misuse:'))}")
    return signals


def _collect_keyword_signals(events: list[_SessionEvent], patterns: tuple[str, ...], label: str) -> list[str]:
    signals: list[str] = []
    for event in events:
        haystack = _normalize_text(event.summary_text or event.raw_text)
        if any(pattern in haystack for pattern in patterns):
            signal = f"{label}: {_shorten(event.summary_text or event.raw_text, 120)}"
            if signal not in signals:
                signals.append(signal)
        if len(signals) >= 4:
            break
    return signals


def _collect_evidence_refs(events: list[_SessionEvent]) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()
    for event in events:
        haystack = _normalize_text(event.summary_text or event.raw_text)
        if any(
            pattern in haystack
            for pattern in (*_CRITICAL_PATTERNS, *_MISGUIDANCE_PATTERNS)
        ):
            ref = event.evidence_ref
            if ref not in seen:
                seen.add(ref)
                refs.append(ref)
        if len(refs) >= 8:
            break
    if not refs and events:
        refs.append(events[0].evidence_ref)
    return refs


def _recommended_edit_targets(
    *,
    wasted_loop_signals: list[str],
    tool_misuse_signals: list[str],
    critical_turns: list[str],
    skill_misguidance_signals: list[str],
) -> list[str]:
    targets: list[str] = []
    if wasted_loop_signals:
        targets.extend(["compress_derived_layer", "reduce_repeated_retry_loop"])
    if tool_misuse_signals:
        targets.append("clarify_tool_choice")
    if critical_turns:
        targets.append("tighten_scope_boundary")
    if skill_misguidance_signals:
        targets.append("remove_speculative_evaluator_content")
    if not targets:
        targets.append("tighten_scope_boundary")
    deduped: list[str] = []
    for target in targets:
        if target not in deduped:
            deduped.append(target)
    return deduped


def _dominant_failure_pattern(
    *,
    wasted_loop_signals: list[str],
    tool_misuse_signals: list[str],
    critical_turns: list[str],
    skill_misguidance_signals: list[str],
) -> str:
    if any("contract" in signal.lower() or "missing refined skill" in signal.lower() for signal in critical_turns):
        return "refine contract failure"
    if any("timeout" in signal.lower() for signal in critical_turns):
        return "timeout pressure"
    if wasted_loop_signals:
        return "repeated loop / low-progress churn"
    if tool_misuse_signals:
        return "tool misuse"
    if skill_misguidance_signals:
        return "skill misguidance"
    if critical_turns:
        return "critical runtime failure"
    return "mixed evidence"


def distill_session_logs(session_log_paths: Iterable[Path]) -> SessionDerivedEvidence:
    paths = tuple(Path(path).resolve() for path in session_log_paths)
    events = _read_session_events(paths)
    wasted_loop_signals = _collect_repeated_loop_signals(events)
    tool_misuse_signals = _collect_keyword_signals(events, _MISUSE_PATTERNS, "Tool misuse")
    critical_turns = _collect_keyword_signals(events, _CRITICAL_PATTERNS, "Critical turn")
    skill_misguidance_signals = _collect_keyword_signals(events, _MISGUIDANCE_PATTERNS, "Skill misguidance")
    recommended_edit_targets = _recommended_edit_targets(
        wasted_loop_signals=wasted_loop_signals,
        tool_misuse_signals=tool_misuse_signals,
        critical_turns=critical_turns,
        skill_misguidance_signals=skill_misguidance_signals,
    )
    dominant_failure_pattern = _dominant_failure_pattern(
        wasted_loop_signals=wasted_loop_signals,
        tool_misuse_signals=tool_misuse_signals,
        critical_turns=critical_turns,
        skill_misguidance_signals=skill_misguidance_signals,
    )
    evidence_refs = _collect_evidence_refs(events)
    return SessionDerivedEvidence(
        source_paths=tuple(str(path) for path in paths),
        dominant_failure_pattern=dominant_failure_pattern,
        wasted_loop_signals=wasted_loop_signals,
        tool_misuse_signals=tool_misuse_signals,
        critical_turns=critical_turns,
        skill_misguidance_signals=skill_misguidance_signals,
        recommended_edit_targets=recommended_edit_targets,
        evidence_refs=evidence_refs,
        observed_at=_timestamp(),
    )


def render_session_evidence_markdown(evidence: SessionDerivedEvidence) -> str:
    lines = [
        "# Session-Derived Evidence",
        "",
        f"- dominant_failure_pattern: `{evidence.dominant_failure_pattern}`",
        f"- source_paths: `{', '.join(evidence.source_paths)}`",
        f"- observed_at: `{evidence.observed_at}`",
        "",
        "## Wasted Loop Signals",
    ]
    lines.extend(f"- {signal}" for signal in (evidence.wasted_loop_signals or ["none"]))
    lines.extend(
        [
            "",
            "## Tool Misuse Signals",
        ]
    )
    lines.extend(f"- {signal}" for signal in (evidence.tool_misuse_signals or ["none"]))
    lines.extend(
        [
            "",
            "## Critical Turns",
        ]
    )
    lines.extend(f"- {signal}" for signal in (evidence.critical_turns or ["none"]))
    lines.extend(
        [
            "",
            "## Skill Misguidance Signals",
        ]
    )
    lines.extend(f"- {signal}" for signal in (evidence.skill_misguidance_signals or ["none"]))
    lines.extend(
        [
            "",
            "## Recommended Edit Targets",
        ]
    )
    lines.extend(f"- {target}" for target in evidence.recommended_edit_targets)
    lines.extend(
        [
            "",
            "## Evidence Refs",
        ]
    )
    lines.extend(f"- {ref}" for ref in evidence.evidence_refs)
    return "\n".join(lines) + "\n"

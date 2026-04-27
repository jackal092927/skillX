from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable


HARD_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("api_error_status_429", re.compile(r"api_error_status[^0-9]{0,20}429", re.I)),
    (
        "rate_limit_rejected_event",
        re.compile(
            r"rate_limit_event.{0,500}rate_limit_info.{0,200}[\"']status[\"']\s*:\s*[\"']rejected[\"']",
            re.I | re.S,
        ),
    ),
    ("http_429", re.compile(r"\bHTTP\s*429\b", re.I)),
    ("status_429", re.compile(r"\b(?:status|code|error)[^A-Za-z0-9]{0,20}429\b", re.I)),
    ("too_many_requests", re.compile(r"too many requests", re.I)),
    ("rate_limit_error", re.compile(r"\bRateLimitError\b", re.I)),
    (
        "rate_limit_reached",
        re.compile(
            r"\brate[-_\s]*limit(?:ed|ing)?[-_\s]*(?:reached|exceeded|hit|stop|cutoff|failure|abort|blocked|rejected)\b",
            re.I,
        ),
    ),
    ("usage_limit_reached", re.compile(r"(?:usage|quota|provider)[-\s]*(?:limit|quota)[-\s]*(?:reached|exceeded|hit|blocked)", re.I)),
    ("claude_limit_reached", re.compile(r"(?:Claude|Anthropic)[-\s]*(?:usage|rate)?[-\s]*limit[-\s]*(?:reached|exceeded|hit)", re.I)),
    ("hit_your_limit", re.compile(r"hit your limit", re.I)),
    ("provider_quota", re.compile(r"provider[-\s]*(?:side[-\s]*)?(?:quota|limit|rate[-\s]*limit)", re.I)),
    ("quota_blocked", re.compile(r"quota[-\s]*(?:gated|blocked|abort(?:ed)?|stop(?:ped)?|rejected|failure|fail)", re.I)),
    ("infra_quota", re.compile(r"infra[_\s-]*(?:blocked[_\s-]*)?quota|infra[_\s-]*quota[_\s-]*abort", re.I)),
]

SOFT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("quota_aware", re.compile(r"quota[-\s]*(?:aware|safe|headroom|recovery|gate|gating)", re.I)),
    ("rate_limit_guard", re.compile(r"rate[-\s]*limit(?:[-\s]*(?:guard|handling|routing|fallback))", re.I)),
]

RUNTIME_ERROR_EVENT_TYPES = {
    "error",
    "result",
    "turn.failed",
    "turn_failed",
    "response.failed",
    "response_failed",
}

SCAN_FILE_NAMES = {
    "result.json",
    "run_failure.json",
    "round_decision.json",
    "session_evidence.json",
    "verifier_summary.json",
    "orchestrator_log.ndjson",
    "claude-code.txt",
    "codex.txt",
    "codex.jsonl",
    "stderr.txt",
    "stdout.txt",
    "stdout.jsonl",
    "trial.log",
}
MAX_SCAN_BYTES = 2_000_000
SKIP_DIR_NAMES = {"archives", "__pycache__", ".git"}
PATH_METADATA_FIELD_RE = re.compile(
    r"(?:^|[.$])(?:path|paths|uri|uris|ref|refs|dir|dirs|root|roots)(?:$|\[|[.$])",
    re.I,
)
PATH_METADATA_SUFFIXES = (
    "_path",
    "_paths",
    "_uri",
    "_uris",
    "_ref",
    "_refs",
    "_dir",
    "_dirs",
    "_root",
    "_roots",
)
DERIVED_SIGNAL_FIELD_RE = re.compile(
    r"(?:^|[.$])(?:"
    r"quota_signal(?:_level|_hard_terms|_soft_terms|_matches)?|"
    r"quota_hard_terms|quota_soft_terms|"
    r"hard_terms|soft_terms|matches|signal_level|has_hard_signal"
    r")(?:$|\[|[.$])",
    re.I,
)


def iter_strings(value: Any, prefix: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield prefix, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from iter_strings(child, f"{prefix}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_strings(child, f"{prefix}[{index}]")


def iter_dicts(value: Any, prefix: str = "$") -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(value, dict):
        yield prefix, value
        for key, child in value.items():
            child_path = f"{prefix}.{key}"
            if is_metadata_path_field(child_path) or is_derived_signal_field(child_path):
                continue
            yield from iter_dicts(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_dicts(child, f"{prefix}[{index}]")


def iter_json_objects_from_text(text: str) -> Iterable[dict[str, Any]]:
    stripped = text.strip()
    if not stripped:
        return
    candidates = [stripped] if stripped[:1] in "{[" else []
    candidates.extend(line.strip() for line in text.splitlines() if line.lstrip().startswith(("{", "[")))
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            yield payload
        elif isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    yield item


def compact_excerpt(text: str, match: re.Match[str], width: int = 110) -> str:
    start = max(0, match.start() - width)
    end = min(len(text), match.end() + width)
    excerpt = text[start:end].replace("\n", " ")
    return re.sub(r"\s+", " ", excerpt).strip()


def is_metadata_path_field(field_path: str) -> bool:
    normalized = field_path.replace("[", ".").replace("]", ".")
    parts = [part for part in re.split(r"[.$]+", normalized) if part]
    if any(part.lower().endswith(PATH_METADATA_SUFFIXES) for part in parts):
        return True
    return bool(PATH_METADATA_FIELD_RE.search(field_path))


def is_derived_signal_field(field_path: str) -> bool:
    return bool(DERIVED_SIGNAL_FIELD_RE.search(field_path))


def is_true(value: Any) -> bool:
    return value is True or (isinstance(value, str) and value.lower() == "true")


def coerce_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def event_text_fields(event: dict[str, Any]) -> str:
    fields: list[str] = []
    for key in ("error", "message", "result", "detail", "details", "reason", "status"):
        value = event.get(key)
        if isinstance(value, str):
            fields.append(value)
    message = event.get("message")
    if isinstance(message, dict):
        error = message.get("error")
        if isinstance(error, str):
            fields.append(error)
        content = message.get("content")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    fields.append(item["text"])
    error = event.get("error")
    if isinstance(error, dict):
        for key in ("message", "type", "code", "status"):
            value = error.get(key)
            if isinstance(value, str):
                fields.append(value)
    return "\n".join(fields)


def add_runtime_text_matches(
    *,
    text: str,
    field: str,
    hard_terms: set[str],
    matches: list[dict[str, str]],
) -> None:
    for name, pattern in HARD_PATTERNS:
        match = pattern.search(text)
        if match:
            hard_terms.add(name)
            matches.append(
                {
                    "level": "hard",
                    "term": name,
                    "field": field,
                    "excerpt": compact_excerpt(text, match),
                }
            )


def scan_runtime_event(event: dict[str, Any], field: str) -> dict[str, Any]:
    matches: list[dict[str, str]] = []
    hard_terms: set[str] = set()
    event_type = event.get("type")
    event_error = event.get("error")

    rate_limit_info = event.get("rate_limit_info")
    if isinstance(rate_limit_info, dict):
        status = str(rate_limit_info.get("status") or "").lower()
        if status == "rejected":
            hard_terms.add("rate_limit_rejected_event")
            matches.append(
                {
                    "level": "hard",
                    "term": "rate_limit_rejected_event",
                    "field": f"{field}.rate_limit_info.status",
                    "excerpt": f"rate_limit_event status={status}",
                }
            )

    api_error_status = coerce_int(event.get("api_error_status"))
    if api_error_status == 429 and is_true(event.get("is_error")):
        hard_terms.add("api_error_status_429")
        matches.append(
            {
                "level": "hard",
                "term": "api_error_status_429",
                "field": f"{field}.api_error_status",
                "excerpt": "runtime result is_error=true api_error_status=429",
            }
        )

    eligible_runtime_error = (
        event_type in RUNTIME_ERROR_EVENT_TYPES
        or event_error == "rate_limit"
        or api_error_status == 429
    )
    if eligible_runtime_error:
        text = event_text_fields(event)
        if text:
            add_runtime_text_matches(text=text, field=field, hard_terms=hard_terms, matches=matches)

    return {
        "hard_terms": hard_terms,
        "matches": matches,
    }


def scan_payload(payload: Any) -> dict[str, Any]:
    matches: list[dict[str, str]] = []
    hard_terms: set[str] = set()
    soft_terms: set[str] = set()

    for path, event in iter_dicts(payload):
        event_scan = scan_runtime_event(event, path)
        hard_terms.update(str(term) for term in event_scan.get("hard_terms") or [])
        matches.extend(event_scan.get("matches") or [])

    for path, text in iter_strings(payload):
        if is_metadata_path_field(path) or is_derived_signal_field(path):
            continue
        for event_index, event in enumerate(iter_json_objects_from_text(text)):
            event_scan = scan_runtime_event(event, f"{path}.jsonl[{event_index}]")
            hard_terms.update(str(term) for term in event_scan.get("hard_terms") or [])
            matches.extend(event_scan.get("matches") or [])
        for name, pattern in SOFT_PATTERNS:
            match = pattern.search(text)
            if match:
                soft_terms.add(name)
                matches.append(
                    {
                        "level": "soft",
                        "term": name,
                        "field": path,
                        "excerpt": compact_excerpt(text, match),
                    }
                )
    level = "hard" if hard_terms else "soft" if soft_terms else "none"
    return {
        "signal_level": level,
        "has_hard_signal": bool(hard_terms),
        "hard_terms": sorted(hard_terms),
        "soft_terms": sorted(soft_terms),
        "matches": matches,
    }


def combine_scans(scans: Iterable[dict[str, Any]]) -> dict[str, Any]:
    hard_terms: set[str] = set()
    soft_terms: set[str] = set()
    matches: list[dict[str, str]] = []
    for scan in scans:
        hard_terms.update(str(term) for term in scan.get("hard_terms") or [])
        soft_terms.update(str(term) for term in scan.get("soft_terms") or [])
        for match in scan.get("matches") or []:
            if isinstance(match, dict):
                matches.append({str(key): str(value) for key, value in match.items()})
    level = "hard" if hard_terms else "soft" if soft_terms else "none"
    return {
        "signal_level": level,
        "has_hard_signal": bool(hard_terms),
        "hard_terms": sorted(hard_terms),
        "soft_terms": sorted(soft_terms),
        "matches": matches,
    }


def read_scan_payload(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if len(text) > MAX_SCAN_BYTES:
        text = text[-MAX_SCAN_BYTES:]
    if path.suffix == ".json":
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"path": str(path), "text": text}
    return {"path": str(path), "text": text}


def summarize_path(path: Path) -> dict[str, Any]:
    payload = read_scan_payload(path)
    if payload is None:
        return {
            "signal_level": "none",
            "has_hard_signal": False,
            "hard_terms": [],
            "soft_terms": [],
            "matches": [],
        }
    scan = scan_payload(payload)
    for match in scan["matches"]:
        match.setdefault("source_path", str(path))
    return scan


def summarize_run_dir(run_dir: Path) -> dict[str, Any]:
    scans: list[dict[str, Any]] = []
    scanned_files: list[str] = []
    if not run_dir.exists():
        combined = combine_scans([])
        combined["scanned_files"] = scanned_files
        return combined
    for path in sorted(run_dir.rglob("*")):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if not path.is_file() or path.name not in SCAN_FILE_NAMES:
            continue
        scanned_files.append(str(path))
        scan = summarize_path(path)
        if scan["signal_level"] != "none":
            scans.append(scan)
    combined = combine_scans(scans)
    combined["scanned_files"] = scanned_files
    return combined


__all__ = [
    "combine_scans",
    "scan_payload",
    "summarize_path",
    "summarize_run_dir",
]

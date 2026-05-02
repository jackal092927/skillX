#!/usr/bin/env python3
"""Serve a lightweight local monitor for a SkillX outer-loop optimization run."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any


DEFAULT_ROUND_ROOT = Path(
    "experiments/skillx-skillsbench-001/results/outer-loop-round0/"
    "sonnet45-task-list-first20-v0.1"
)
DEFAULT_STALE_AFTER_SEC = 600.0


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _safe_read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return fallback


def _escape(value: Any) -> str:
    return html.escape(str(value))


def _fmt_age(seconds: float | None) -> str:
    if seconds is None:
        return "n/a"
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds / 60:.1f}m"
    return f"{seconds / 3600:.1f}h"


def _latest_mtime(path: Path) -> float | None:
    if not path.exists():
        return None
    latest = path.stat().st_mtime
    for child in path.rglob("*"):
        try:
            latest = max(latest, child.stat().st_mtime)
        except FileNotFoundError:
            continue
    return latest


def _tail_text(path: Path | None, *, lines: int = 80) -> list[str]:
    if path is None or not path.exists():
        return []
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return []
    return text.splitlines()[-lines:]


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _control_plane_summary(control_plane_dir: Path) -> dict[str, Any]:
    bundle = _safe_read_json(control_plane_dir / "control_plane_bundle.json", {})
    assignments = bundle.get("assignments") if isinstance(bundle, dict) else None
    diagnostics = bundle.get("diagnostics") if isinstance(bundle, dict) else None
    score_matrix = bundle.get("score_matrix") if isinstance(bundle, dict) else None
    long_rows = score_matrix.get("long_rows") if isinstance(score_matrix, dict) else None
    training_rows = (
        diagnostics.get("schema_training_assignments")
        if isinstance(diagnostics, dict)
        else None
    )
    assigned_count = 0
    task_names: set[str] = set()
    if isinstance(assignments, list):
        for row in assignments:
            if not isinstance(row, dict):
                continue
            if row.get("assignment_status") == "assigned":
                assigned_count += 1
            task_name = row.get("task_name")
            if isinstance(task_name, str):
                task_names.add(task_name)
    schema_ids = bundle.get("schema_ids") if isinstance(bundle, dict) else None
    if not isinstance(schema_ids, list):
        prompt_bank = bundle.get("prompt_bank") if isinstance(bundle, dict) else None
        categories = prompt_bank.get("categories") if isinstance(prompt_bank, dict) else None
        schema_ids = [
            row.get("category_id")
            for row in categories
            if isinstance(row, dict) and isinstance(row.get("category_id"), str)
        ] if isinstance(categories, list) else []
    return {
        "exists": (control_plane_dir / "control_plane_bundle.json").exists(),
        "path": str(control_plane_dir),
        "assignment_count": len(assignments) if isinstance(assignments, list) else 0,
        "assigned_count": assigned_count,
        "task_count": len(task_names),
        "schema_count": len(schema_ids),
        "score_row_count": len(long_rows) if isinstance(long_rows, list) else 0,
        "training_evidence_count": len(training_rows) if isinstance(training_rows, list) else 0,
    }


def _attempts_for_schema(schema_dir: Path) -> list[dict[str, Any]]:
    payload = _safe_read_json(schema_dir / "attempts.json", {})
    attempts = payload.get("attempts") if isinstance(payload, dict) else None
    if not isinstance(attempts, list):
        return []
    return [row for row in attempts if isinstance(row, dict)]


def _schema_attempt_summary(schema_dir: Path) -> dict[str, Any]:
    attempts = _attempts_for_schema(schema_dir)
    status = "pending"
    last_attempt = attempts[-1] if attempts else {}
    last_status = last_attempt.get("status") if isinstance(last_attempt, dict) else None
    if attempts:
        status = str(last_status or "unknown")
    elif (schema_dir / "prompt.txt").exists():
        status = "started"

    succeeded = any(str(row.get("status")) == "succeeded" for row in attempts)
    failed = bool(attempts) and not succeeded and status not in {
        "hard_rate_limit",
        "hard_rate_limit_parse_failure",
    }
    rate_limited = any(
        str(row.get("status")) in {"hard_rate_limit", "hard_rate_limit_parse_failure"}
        or bool(row.get("quota_hard_terms"))
        for row in attempts
    )
    fallback_used = any(
        isinstance(row.get("profile"), dict)
        and str(row["profile"].get("label") or "").startswith("fallback-")
        for row in attempts
    )
    hard_terms = sorted(
        {
            str(term)
            for row in attempts
            for term in (row.get("quota_hard_terms") or [])
        }
    )
    profile = last_attempt.get("profile") if isinstance(last_attempt, dict) else None
    latest = _latest_mtime(schema_dir)
    return {
        "schema_id": schema_dir.name,
        "path": str(schema_dir),
        "status": "succeeded" if succeeded else status,
        "attempt_count": len(attempts),
        "last_profile": profile.get("label") if isinstance(profile, dict) else None,
        "fallback_used": fallback_used,
        "rate_limited": rate_limited,
        "quota_hard_terms": hard_terms,
        "returncode": last_attempt.get("returncode") if isinstance(last_attempt, dict) else None,
        "failed": failed,
        "latest_mtime": latest,
    }


def _schema_rewrite_summary(schema_update_dir: Path) -> dict[str, Any]:
    llm_root = schema_update_dir / "llm_runs"
    schema_rows = []
    if llm_root.exists():
        schema_rows = [
            _schema_attempt_summary(path)
            for path in sorted(llm_root.iterdir())
            if path.is_dir()
        ]
    verification = _safe_read_json(schema_update_dir / "rewrite_verification.json", {})
    package = _safe_read_json(schema_update_dir / "schema_update_package.json", {})
    expected_count = _coerce_int(verification.get("expected_rewrite_schema_count"))
    completed_count = _coerce_int(verification.get("completed_rewrite_schema_count"))
    if expected_count is None:
        schema_ids = package.get("schema_ids") if isinstance(package, dict) else None
        expected_count = len(schema_ids) if isinstance(schema_ids, list) else None
    succeeded_count = sum(1 for row in schema_rows if row["status"] == "succeeded")
    failed_count = sum(1 for row in schema_rows if row["failed"])
    rate_limit_count = sum(1 for row in schema_rows if row["rate_limited"])
    fallback_count = sum(1 for row in schema_rows if row["fallback_used"])
    return {
        "exists": schema_update_dir.exists(),
        "path": str(schema_update_dir),
        "llm_runs_path": str(llm_root),
        "schema_rows": schema_rows,
        "observed_schema_count": len(schema_rows),
        "expected_schema_count": expected_count,
        "succeeded_schema_count": succeeded_count,
        "failed_schema_count": failed_count,
        "rate_limited_schema_count": rate_limit_count,
        "fallback_schema_count": fallback_count,
        "verification": verification if isinstance(verification, dict) else {},
        "verification_status": (
            verification.get("status") if isinstance(verification, dict) else None
        ),
        "completed_rewrite_schema_count": completed_count,
        "package_exists": (schema_update_dir / "schema_update_package.json").exists(),
        "summary_exists": (schema_update_dir / "outer_loop_optimization_summary.json").exists(),
    }


def _materialization_summary(next_materialized_root: Path) -> dict[str, Any]:
    manifest = _safe_read_json(next_materialized_root / "manifest.json", {})
    return {
        "exists": (next_materialized_root / "manifest.json").exists(),
        "path": str(next_materialized_root),
        "manifest": manifest if isinstance(manifest, dict) else {},
        "task_count": manifest.get("task_count") if isinstance(manifest, dict) else None,
        "schema_count": manifest.get("schema_count") if isinstance(manifest, dict) else None,
        "pair_count": manifest.get("pair_count") if isinstance(manifest, dict) else None,
    }


def _infer_phase(
    *,
    control: dict[str, Any],
    schema: dict[str, Any],
    materialized: dict[str, Any],
) -> str:
    if materialized["exists"]:
        return "completed"
    if schema["verification_status"]:
        return "materializing_next_pairs"
    if schema["observed_schema_count"] or schema["exists"]:
        return "schema_rewrite"
    if control["exists"]:
        return "control_plane_complete"
    return "waiting_for_control_plane"


def _overall_health(
    *,
    phase: str,
    schema: dict[str, Any],
    materialized: dict[str, Any],
    latest_age_sec: float | None,
    stale_after_sec: float,
) -> tuple[str, str, list[str]]:
    issues: list[str] = []
    verification_status = schema.get("verification_status")
    if schema["failed_schema_count"]:
        issues.append(f"{schema['failed_schema_count']} schema rewrite attempt(s) failed")
    if verification_status and verification_status != "passed":
        issues.append(f"rewrite verification is {verification_status}")
    if schema["rate_limited_schema_count"]:
        issues.append(f"{schema['rate_limited_schema_count']} schema(s) hit hard rate/quota signal")
    stale = (
        phase != "completed"
        and latest_age_sec is not None
        and latest_age_sec > stale_after_sec
    )
    if stale:
        issues.append(f"no artifact update for {_fmt_age(latest_age_sec)}")

    if schema["failed_schema_count"] or (verification_status and verification_status != "passed"):
        return "error", "failed", issues
    if materialized["exists"] and verification_status in {None, "passed"}:
        return "ok", "completed", issues
    if stale:
        return "warn", "stale", issues
    if schema["rate_limited_schema_count"]:
        return "warn", "running_with_fallback", issues
    return "ok", "running", issues


def build_monitor_payload(
    *,
    control_plane_dir: Path,
    schema_update_dir: Path,
    next_materialized_root: Path,
    log_path: Path | None = None,
    stale_after_sec: float = DEFAULT_STALE_AFTER_SEC,
) -> dict[str, Any]:
    control_plane_dir = control_plane_dir.resolve()
    schema_update_dir = schema_update_dir.resolve()
    next_materialized_root = next_materialized_root.resolve()
    log_path = log_path.resolve() if log_path is not None else None
    now = _utc_now().timestamp()
    control = _control_plane_summary(control_plane_dir)
    schema = _schema_rewrite_summary(schema_update_dir)
    materialized = _materialization_summary(next_materialized_root)
    phase = _infer_phase(control=control, schema=schema, materialized=materialized)
    mtimes = [
        value
        for value in (
            _latest_mtime(control_plane_dir),
            _latest_mtime(schema_update_dir),
            _latest_mtime(next_materialized_root),
            log_path.stat().st_mtime if log_path is not None and log_path.exists() else None,
        )
        if value is not None
    ]
    latest_mtime = max(mtimes) if mtimes else None
    latest_age_sec = None if latest_mtime is None else max(0.0, now - latest_mtime)
    health_level, status, issues = _overall_health(
        phase=phase,
        schema=schema,
        materialized=materialized,
        latest_age_sec=latest_age_sec,
        stale_after_sec=stale_after_sec,
    )
    return {
        "generated_at": _utc_now().isoformat(),
        "status": status,
        "health_level": health_level,
        "phase": phase,
        "issues": issues,
        "latest_artifact_age_sec": latest_age_sec,
        "stale_after_sec": stale_after_sec,
        "control_plane": control,
        "schema_rewrite": schema,
        "materialization": materialized,
        "log_path": None if log_path is None else str(log_path),
        "log_tail": _tail_text(log_path),
    }


def _status_class(health_level: str) -> str:
    return {
        "ok": "status-ok",
        "warn": "status-warn",
        "error": "status-error",
    }.get(health_level, "status-warn")


def _render_schema_rows(rows: list[dict[str, Any]]) -> str:
    rendered = []
    for row in rows:
        classes = []
        if row.get("status") == "succeeded":
            classes.append("good")
        if row.get("failed"):
            classes.append("bad")
        if row.get("rate_limited"):
            classes.append("warn")
        rendered.append(
            f'<tr class="{" ".join(classes)}">'
            f'<td>{_escape(row.get("schema_id"))}</td>'
            f'<td>{_escape(row.get("status"))}</td>'
            f'<td class="num">{_escape(row.get("attempt_count"))}</td>'
            f'<td>{_escape(row.get("last_profile") or "")}</td>'
            f'<td>{_escape("yes" if row.get("fallback_used") else "")}</td>'
            f'<td>{_escape(", ".join(row.get("quota_hard_terms") or []))}</td>'
            f'<td class="num">{_escape(row.get("returncode") if row.get("returncode") is not None else "")}</td>'
            "</tr>"
        )
    return "\n".join(rendered)


def render_monitor_html(payload: dict[str, Any]) -> str:
    control = payload["control_plane"]
    schema = payload["schema_rewrite"]
    materialized = payload["materialization"]
    manifest = materialized.get("manifest") or {}
    issues = payload.get("issues") or []
    issue_html = "".join(f"<li>{_escape(item)}</li>" for item in issues) or "<li>none</li>"
    log_tail = "\n".join(payload.get("log_tail") or [])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="10">
  <link rel="icon" href="data:,">
  <title>SkillX Outer-Loop Monitor</title>
  <style>
    :root {{
      --bg: #050505;
      --panel: #101112;
      --panel-alt: #17191b;
      --ink: #f7f3ea;
      --muted: #938f86;
      --border: #303337;
      --accent: #67e8f9;
      --pos: #86efac;
      --warn: #fbbf24;
      --neg: #fb7185;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Avenir Next", "Helvetica Neue", Helvetica, sans-serif;
      font-size: 14px;
      line-height: 1.45;
      color-scheme: dark;
    }}
    main {{
      width: min(1500px, calc(100vw - 36px));
      margin: 0 auto;
      padding: 26px 0 52px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 20px;
      align-items: start;
      margin-bottom: 16px;
    }}
    h1 {{
      margin: 0 0 6px;
      font-family: Georgia, "Iowan Old Style", serif;
      font-size: clamp(28px, 3vw, 44px);
      line-height: 1;
      letter-spacing: 0;
    }}
    .subhead, .muted {{ color: var(--muted); font-size: 12px; }}
    .badge {{
      border: 1px solid var(--border);
      background: var(--panel);
      border-radius: 8px;
      padding: 12px 14px;
      min-width: 240px;
      text-align: right;
    }}
    .badge b {{ display: block; font-size: 20px; }}
    .status-ok b {{ color: var(--pos); }}
    .status-warn b {{ color: var(--warn); }}
    .status-error b {{ color: var(--neg); }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }}
    .metric, .panel {{
      border: 1px solid var(--border);
      background: var(--panel);
      border-radius: 8px;
    }}
    .metric {{ padding: 12px; min-height: 78px; }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .metric b {{
      display: block;
      margin-top: 5px;
      font-size: 24px;
      font-variant-numeric: tabular-nums;
    }}
    .panel {{ padding: 16px; margin-bottom: 16px; overflow: hidden; }}
    .panel h2 {{
      margin: 0 0 12px;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .table-wrap {{
      overflow: auto;
      border: 1px solid var(--border);
      border-radius: 6px;
      max-height: 62vh;
    }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{
      padding: 8px 10px;
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
      text-align: left;
      color: #d7d0c0;
      font-size: 12px;
    }}
    thead th {{
      position: sticky;
      top: 0;
      background: var(--panel-alt);
      color: var(--muted);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .num {{
      text-align: right;
      font-family: "SF Mono", Menlo, Consolas, monospace;
      font-variant-numeric: tabular-nums;
    }}
    tr.good td {{ background: rgba(134, 239, 172, 0.08); }}
    tr.warn td {{ background: rgba(251, 191, 36, 0.10); }}
    tr.bad td {{ background: rgba(251, 113, 133, 0.12); }}
    code, pre {{
      font-family: "SF Mono", Menlo, Consolas, monospace;
      color: #d7d0c0;
      background: var(--panel-alt);
      border: 1px solid var(--border);
      border-radius: 6px;
    }}
    code {{ padding: 2px 6px; }}
    pre {{
      white-space: pre-wrap;
      overflow: auto;
      max-height: 360px;
      padding: 12px;
      font-size: 11px;
    }}
    @media (max-width: 1080px) {{
      main {{ width: min(100vw - 24px, 980px); }}
      .metrics {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
      .hero {{ grid-template-columns: 1fr; }}
      .badge {{ text-align: left; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div>
        <h1>Outer-Loop Monitor</h1>
        <div class="subhead">
          Auto-refreshes every 10 seconds. API: <code>/api/outer-loop</code>
        </div>
      </div>
      <div class="badge {_status_class(str(payload.get("health_level")))}">
        <b>{_escape(payload.get("status"))}</b>
        <span class="muted">{_escape(payload.get("phase"))} / latest {_escape(_fmt_age(payload.get("latest_artifact_age_sec")))}</span>
      </div>
    </section>

    <section class="metrics">
      <div class="metric"><span>Assignments</span><b>{_escape(control.get("assigned_count"))}/{_escape(control.get("assignment_count"))}</b></div>
      <div class="metric"><span>Training Evidence</span><b>{_escape(control.get("training_evidence_count"))}</b></div>
      <div class="metric"><span>Schema Attempts</span><b>{_escape(schema.get("succeeded_schema_count"))}/{_escape(schema.get("expected_schema_count") or schema.get("observed_schema_count"))}</b></div>
      <div class="metric"><span>Fallback Used</span><b>{_escape(schema.get("fallback_schema_count"))}</b></div>
      <div class="metric"><span>Rate Limited</span><b>{_escape(schema.get("rate_limited_schema_count"))}</b></div>
      <div class="metric"><span>Next Pairs</span><b>{_escape(materialized.get("pair_count") or "")}</b></div>
    </section>

    <section class="panel">
      <h2>Health</h2>
      <ul>{issue_html}</ul>
      <div class="muted">control-plane: <code>{_escape(control.get("path"))}</code></div>
      <div class="muted">schema-updates: <code>{_escape(schema.get("path"))}</code></div>
      <div class="muted">next-root: <code>{_escape(materialized.get("path"))}</code></div>
    </section>

    <section class="panel">
      <h2>Schema Rewrite Attempts</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Schema</th>
              <th>Status</th>
              <th class="num">Attempts</th>
              <th>Last Profile</th>
              <th>Fallback</th>
              <th>Hard Terms</th>
              <th class="num">Returncode</th>
            </tr>
          </thead>
          <tbody>{_render_schema_rows(schema.get("schema_rows") or [])}</tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <h2>Verification / Materialization</h2>
      <div class="muted">rewrite_verification: <code>{_escape(schema.get("verification_status") or "pending")}</code></div>
      <div class="muted">manifest: tasks=<code>{_escape(manifest.get("task_count") or "")}</code> schemas=<code>{_escape(manifest.get("schema_count") or "")}</code> pairs=<code>{_escape(manifest.get("pair_count") or "")}</code></div>
    </section>

    <section class="panel">
      <h2>Log Tail</h2>
      <pre>{_escape(log_tail)}</pre>
    </section>
  </main>
</body>
</html>
"""


def resolve_monitor_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    round_root = args.round_root
    if args.outer_label:
        control_plane_dir = args.control_plane_dir or round_root / "reports" / args.outer_label / "control-plane"
        schema_update_dir = args.schema_update_dir or round_root / "reports" / args.outer_label / "schema-updates"
        next_materialized_root = args.next_materialized_root or round_root / f"{args.outer_label}-candidates"
    else:
        control_plane_dir = args.control_plane_dir or round_root / "reports" / "outer-loop-control-plane"
        schema_update_dir = args.schema_update_dir or round_root / "reports" / "outer-loop-schema-updates"
        next_materialized_root = args.next_materialized_root or round_root / "outer-loop-round1-candidate-rerun"
    return control_plane_dir, schema_update_dir, next_materialized_root


def build_server(
    *,
    control_plane_dir: Path,
    schema_update_dir: Path,
    next_materialized_root: Path,
    log_path: Path | None,
    stale_after_sec: float,
    host: str,
    port: int,
) -> ThreadingHTTPServer:
    class MonitorHandler(BaseHTTPRequestHandler):
        def _payload(self) -> dict[str, Any]:
            return build_monitor_payload(
                control_plane_dir=control_plane_dir,
                schema_update_dir=schema_update_dir,
                next_materialized_root=next_materialized_root,
                log_path=log_path,
                stale_after_sec=stale_after_sec,
            )

        def _write_json(self, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _write_html(self, body_text: str) -> None:
            body = body_text.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
                return
            if path == "/api/outer-loop":
                self._write_json(self._payload())
                return
            if path in {"/", "/index.html"}:
                self._write_html(render_monitor_html(self._payload()))
                return
            self.send_error(404, "Not Found")

        def log_message(self, format: str, *args: object) -> None:
            return

    return ThreadingHTTPServer((host, port), MonitorHandler)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round-root", type=Path, default=DEFAULT_ROUND_ROOT)
    parser.add_argument("--outer-label")
    parser.add_argument("--control-plane-dir", type=Path)
    parser.add_argument("--schema-update-dir", type=Path)
    parser.add_argument("--next-materialized-root", type=Path)
    parser.add_argument("--log-path", type=Path)
    parser.add_argument("--stale-after-sec", type=float, default=DEFAULT_STALE_AFTER_SEC)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8771)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    control_plane_dir, schema_update_dir, next_materialized_root = resolve_monitor_paths(args)
    server = build_server(
        control_plane_dir=control_plane_dir,
        schema_update_dir=schema_update_dir,
        next_materialized_root=next_materialized_root,
        log_path=args.log_path,
        stale_after_sec=args.stale_after_sec,
        host=args.host,
        port=args.port,
    )
    print("Serving SkillX outer-loop monitor")
    print(f"  control-plane: {control_plane_dir.resolve()}")
    print(f"  schema-updates: {schema_update_dir.resolve()}")
    print(f"  next-root: {next_materialized_root.resolve()}")
    print(f"Open: http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down outer-loop monitor.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

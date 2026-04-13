from __future__ import annotations

import json
import sys
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DOCKER_INTERNAL_ERROR_MARKERS = (
    "Internal Server Error",
    "Cannot connect to the Docker daemon",
    "docker daemon is not running",
    "error during connect",
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _trim_output(text: str | None, *, limit: int = 4000) -> str:
    if text is None:
        return ""
    normalized = text.strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    timeout_sec: float = 20.0,
) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
    except FileNotFoundError as exc:
        return {
            "command": list(command),
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "timed_out": False,
            "error": f"{type(exc).__name__}: {exc}",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": list(command),
            "returncode": None,
            "stdout": _trim_output(exc.stdout),
            "stderr": _trim_output(exc.stderr),
            "timed_out": True,
            "error": f"command timed out after {timeout_sec} seconds",
        }
    return {
        "command": list(command),
        "returncode": proc.returncode,
        "stdout": _trim_output(proc.stdout),
        "stderr": _trim_output(proc.stderr),
        "timed_out": False,
        "error": None,
    }


def _contains_internal_error(*parts: str | None) -> bool:
    haystack = "\n".join(part or "" for part in parts)
    return any(marker in haystack for marker in DOCKER_INTERNAL_ERROR_MARKERS)


def _parse_json_object(stdout: str) -> dict[str, Any] | None:
    if not stdout.strip():
        return None
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _coerce_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def probe_docker_health(
    *,
    min_memory_bytes: int,
    timeout_sec: float = 20.0,
) -> dict[str, Any]:
    info_result = _run_command(
        ["docker", "info", "--format", "{{json .}}"],
        timeout_sec=timeout_sec,
    )
    version_result = _run_command(
        ["docker", "version", "--format", "{{json .Server}}"],
        timeout_sec=timeout_sec,
    )
    ps_result = _run_command(
        ["docker", "ps", "--format", "{{json .Names}}"],
        timeout_sec=timeout_sec,
    )

    info_payload = _parse_json_object(info_result["stdout"])
    version_payload = _parse_json_object(version_result["stdout"])
    docker_mem_bytes = _coerce_int(None if info_payload is None else info_payload.get("MemTotal"))

    issues: list[str] = []
    category = "healthy"

    commands = {
        "docker_info": info_result,
        "docker_version": version_result,
        "docker_ps": ps_result,
    }
    internal_error_detected = any(
        _contains_internal_error(result.get("stdout"), result.get("stderr"), result.get("error"))
        for result in commands.values()
    )
    if internal_error_detected:
        category = "daemon_internal_error"
        issues.append("Docker daemon returned an internal API error")

    for name, result in commands.items():
        if result["error"]:
            if category == "healthy":
                category = "command_error"
            issues.append(f"{name} failed: {result['error']}")
        elif result["returncode"] not in (0, None):
            if category == "healthy":
                category = "command_error"
            issues.append(f"{name} returned exit code {result['returncode']}")

    if info_payload is None:
        if category == "healthy":
            category = "invalid_info"
        issues.append("Docker info output was not valid JSON")

    if version_payload is None:
        if category == "healthy":
            category = "invalid_version"
        issues.append("Docker version server output was not valid JSON")

    if docker_mem_bytes is None:
        if category == "healthy":
            category = "invalid_memory"
        issues.append("Docker info did not report a parseable MemTotal value")
    elif docker_mem_bytes == 0:
        if category == "healthy":
            category = "invalid_memory"
        issues.append("Docker info reported MemTotal=0 bytes")
    elif docker_mem_bytes < min_memory_bytes:
        category = "insufficient_memory"
        issues.append(
            f"Docker memory too low: {docker_mem_bytes} bytes < required {min_memory_bytes} bytes"
        )

    healthy = not issues
    if healthy:
        message = (
            f"Docker healthy: MemTotal={docker_mem_bytes} bytes >= required {min_memory_bytes} bytes"
        )
    else:
        message = issues[0]

    return {
        "healthy": healthy,
        "category": category,
        "message": message,
        "observed_at": _timestamp(),
        "docker_mem_bytes": docker_mem_bytes,
        "required_memory_bytes": min_memory_bytes,
        "docker_info": info_payload,
        "docker_version_server": version_payload,
        "checks": commands,
        "issues": issues,
    }


def _run_recovery_commands(
    *,
    skillsbench_root: Path | None = None,
) -> list[dict[str, Any]]:
    commands: list[tuple[list[str], Path | None]] = [
        (["docker", "builder", "prune", "-af"], None),
        (["docker", "system", "prune", "-af", "--volumes"], None),
    ]
    if skillsbench_root is not None:
        commands.append((["uv", "run", "harbor", "cache", "clean", "-f"], skillsbench_root))

    results: list[dict[str, Any]] = []
    for command, cwd in commands:
        results.append(_run_command(command, cwd=cwd, timeout_sec=60.0))
    return results


def _restart_docker_desktop(*, startup_timeout_sec: float = 180.0) -> dict[str, Any]:
    if sys.platform != "darwin":
        return {
            "attempted": False,
            "supported": False,
            "message": f"Docker Desktop restart is not implemented on platform {sys.platform}",
            "commands": [],
            "successful": False,
        }

    commands = [
        ["osascript", "-e", 'tell application "Docker" to quit'],
        ["pkill", "-f", "/Applications/Docker.app/Contents/MacOS/com.docker.backend"],
        ["pkill", "-f", "/Applications/Docker.app/Contents/MacOS/com.docker.virtualization"],
        ["pkill", "-f", "/Applications/Docker.app/Contents/MacOS/Docker Desktop"],
        ["pkill", "-f", "docker serve --address unix:///Users/Jackal/.docker/run/docker-cli-api.sock"],
        ["open", "-a", "Docker"],
    ]

    results: list[dict[str, Any]] = []
    for index, command in enumerate(commands):
        if command[0] == "open":
            time.sleep(3.0)
        result = _run_command(command, timeout_sec=30.0)
        if command[0] in {"osascript", "pkill"} and result["error"] is None and result["returncode"] not in (0, 1):
            result["error"] = f"unexpected return code {result['returncode']}"
        if command[0] in {"osascript", "pkill"} and result["returncode"] == 1:
            result["returncode"] = 0
        results.append(result)
        if index < len(commands) - 1:
            time.sleep(1.0)

    deadline = time.time() + startup_timeout_sec
    wait_checks: list[dict[str, Any]] = []
    while time.time() < deadline:
        version_result = _run_command(
            ["docker", "version", "--format", "{{json .Server}}"],
            timeout_sec=10.0,
        )
        wait_checks.append(version_result)
        if version_result["returncode"] == 0 and _parse_json_object(version_result["stdout"]) is not None:
            return {
                "attempted": True,
                "supported": True,
                "message": "Docker Desktop restart succeeded",
                "commands": results,
                "wait_checks": wait_checks,
                "successful": True,
            }
        time.sleep(2.0)

    return {
        "attempted": True,
        "supported": True,
        "message": "Docker Desktop restart did not restore a healthy server in time",
        "commands": results,
        "wait_checks": wait_checks,
        "successful": False,
    }


def attempt_docker_recovery(*, skillsbench_root: Path | None = None) -> dict[str, Any]:
    pre_cleanup = _run_recovery_commands(skillsbench_root=skillsbench_root)
    desktop_restart = _restart_docker_desktop()
    post_cleanup = _run_recovery_commands(skillsbench_root=skillsbench_root)

    successful = (
        desktop_restart["successful"]
        or any(result["returncode"] == 0 for result in pre_cleanup + post_cleanup)
    )
    return {
        "attempted": True,
        "observed_at": _timestamp(),
        "commands": pre_cleanup + post_cleanup,
        "pre_cleanup": pre_cleanup,
        "desktop_restart": desktop_restart,
        "post_cleanup": post_cleanup,
        "successful": successful,
    }

from __future__ import annotations

import base64
import json
import shlex
from pathlib import Path

from harbor.agents.installed.base import ExecInput
from harbor.agents.installed.codex import Codex
from harbor.models.trial.paths import EnvironmentPaths


class AuthBackedCodex(Codex):
    @staticmethod
    def _resolve_auth_json_text() -> str:
        auth_path = Path.home() / ".codex" / "auth.json"
        if not auth_path.exists():
            raise ValueError(f"Codex auth file not found: {auth_path}")
        raw_text = auth_path.read_text().strip()
        if not raw_text:
            raise ValueError(f"Codex auth file is empty: {auth_path}")
        payload = json.loads(raw_text)
        if not isinstance(payload, dict):
            raise ValueError(f"Codex auth file is not a JSON object: {auth_path}")
        return json.dumps(payload)

    def create_run_agent_commands(self, instruction: str) -> list[ExecInput]:
        escaped_instruction = shlex.quote(instruction)

        if not self.model_name:
            raise ValueError("Model name is required")

        model = self.model_name.split("/")[-1]
        auth_json_b64 = base64.b64encode(self._resolve_auth_json_text().encode("utf-8")).decode("ascii")

        env = {
            "CODEX_HOME": EnvironmentPaths.agent_dir.as_posix(),
            "CODEX_AUTH_JSON_B64": auth_json_b64,
        }

        reasoning_effort = self._reasoning_effort
        reasoning_flag = f"-c model_reasoning_effort={reasoning_effort} " if reasoning_effort else ""
        output_path = shlex.quote((EnvironmentPaths.agent_dir / self._OUTPUT_FILENAME).as_posix())
        run_script = (
            "set -o pipefail; "
            "codex exec "
            "--dangerously-bypass-approvals-and-sandbox "
            "--skip-git-repo-check "
            f"--model {model} "
            "--json "
            "--enable unified_exec "
            f"{reasoning_flag}"
            "-- "
            f"{escaped_instruction} "
            f"2>&1 </dev/null | tee {output_path}; "
            'status=$?; rm -rf "$CODEX_HOME/auth.json"; exit "$status"'
        )

        return [
            ExecInput(
                command=(
                    'mkdir -p "$CODEX_HOME" && '
                    'printf "%s" "$CODEX_AUTH_JSON_B64" | base64 -d >"$CODEX_HOME/auth.json"'
                ),
                env=env,
            ),
            ExecInput(
                command=f"/bin/bash -lc {shlex.quote(run_script)}",
                env=env,
            ),
        ]


__all__ = ["AuthBackedCodex"]

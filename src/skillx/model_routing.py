from __future__ import annotations

from typing import Literal


BenchmarkAgentName = Literal["claude-code", "codex"]
PlaybookCliName = Literal["claude", "codex"]
ModelFamily = Literal["claude", "codex"]
AUTH_BACKED_CLAUDE_CODE_IMPORT_PATH = "skillx.harbor_agents:AuthBackedClaudeCode"
AUTH_BACKED_CODEX_IMPORT_PATH = "skillx.harbor_agents:AuthBackedCodex"


MODEL_NAME_ALIASES = {
    "codex-5.3": "gpt-5.3-codex",
    "gpt-5.4": "gpt-5.4",
}


def resolve_model_name(model_name: str) -> str:
    return MODEL_NAME_ALIASES.get(model_name, model_name)


def strip_model_provider(model_name: str) -> str:
    return model_name.split("/", 1)[1] if "/" in model_name else model_name


def infer_model_family(model_name: str) -> ModelFamily:
    normalized = strip_model_provider(resolve_model_name(model_name)).strip().lower()
    if "claude" in normalized or normalized.startswith(("sonnet", "opus")):
        return "claude"
    return "codex"


def infer_benchmark_agent_name(model_name: str) -> BenchmarkAgentName:
    if infer_model_family(model_name) == "claude":
        return "claude-code"
    return "codex"


def resolve_benchmark_agent_name(agent_name: str | None, model_name: str) -> BenchmarkAgentName:
    inferred = infer_benchmark_agent_name(model_name)
    if agent_name is None:
        return inferred
    normalized = agent_name.strip()
    if not normalized:
        return inferred
    if normalized != inferred:
        raise ValueError(
            f"agent {normalized!r} is incompatible with model {model_name!r}; expected {inferred!r}"
        )
    return inferred


def resolve_playbook_cli_name(model_name: str) -> PlaybookCliName:
    if infer_model_family(model_name) == "claude":
        return "claude"
    return "codex"


def resolve_cli_model_name(model_name: str) -> str:
    return strip_model_provider(resolve_model_name(model_name))


__all__ = [
    "AUTH_BACKED_CLAUDE_CODE_IMPORT_PATH",
    "AUTH_BACKED_CODEX_IMPORT_PATH",
    "MODEL_NAME_ALIASES",
    "infer_benchmark_agent_name",
    "infer_model_family",
    "resolve_benchmark_agent_name",
    "resolve_cli_model_name",
    "resolve_model_name",
    "resolve_playbook_cli_name",
    "strip_model_provider",
]

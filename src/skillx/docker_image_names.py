"""Helpers for stable, readable Harbor Docker image names."""

from __future__ import annotations

import re

_INVALID_IMAGE_NAME_CHARS = re.compile(r"[^a-z0-9._-]+")
_EDGE_SEPARATORS = re.compile(r"^[._-]+|[._-]+$")
_REPEATED_DASHES = re.compile(r"-{2,}")


def sanitize_harbor_image_name(raw_name: str) -> str:
    """Return a Docker-repository-safe image name component for Harbor."""
    normalized = raw_name.strip().lower().replace("/", "-")
    normalized = _INVALID_IMAGE_NAME_CHARS.sub("-", normalized)
    normalized = _REPEATED_DASHES.sub("-", normalized)
    normalized = _EDGE_SEPARATORS.sub("", normalized)
    if not normalized:
        raise ValueError(f"invalid Harbor image name: {raw_name!r}")
    return normalized


def build_harbor_task_pair_image_name(*, task_name: str, schema_id: str) -> str:
    return sanitize_harbor_image_name(f"{task_name}__{schema_id}")

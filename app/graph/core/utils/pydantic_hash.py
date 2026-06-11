"""Canonical hashing for Pydantic models (graph state snapshots, change detection)."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel
from pydantic.main import IncEx


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize ``value`` to stable UTF-8 JSON bytes (sorted keys, compact)."""
    if isinstance(value, BaseModel):
        payload: Any = value.model_dump(mode="json", exclude_none=True)
    else:
        payload = value
    text = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return text.encode("utf-8")


def hash_pydantic_value(
    value: BaseModel | None,
    *,
    algorithm: str = "sha256",
) -> str | None:
    """Return hex digest of canonical JSON for a Pydantic model, or ``None`` if absent."""
    if value is None:
        return None
    return hash_model_dump(value, algorithm=algorithm)


def hash_model_dump(
    model: BaseModel,
    *,
    exclude: IncEx | None = None,
    algorithm: str = "sha256",
) -> str:
    """Return hex digest of canonical JSON for selected model fields."""
    payload = model.model_dump(
        mode="json",
        exclude=exclude,
        exclude_none=True,
    )
    digest = hashlib.new(algorithm)
    digest.update(canonical_json_bytes(payload))
    return digest.hexdigest()

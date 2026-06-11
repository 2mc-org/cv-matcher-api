"""Load JSON fixture files from configurable paths (e.g. env-driven mocks)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast


def load_json_fixture(raw_path: str | None) -> dict[str, object] | None:
    """Load a JSON object from ``raw_path``.

    ``~`` is expanded; relative paths are resolved against ``Path.cwd()``.
    """

    if not raw_path:
        return None

    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.is_file():
        msg = f"JSON fixture file not found: {path}"
        raise FileNotFoundError(msg)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"JSON fixture root must be an object, got {type(data).__name__}: {path}"
        raise TypeError(msg)
    return cast(dict[str, object], data)

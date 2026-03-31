"""
Simple JSON-file-backed persistent key-value store.

Used by dynamic agent/crew management so data survives server restarts
without requiring a new database migration.
"""

import json
from pathlib import Path
from typing import Any

# Persist files next to this package, under backend/storage/data/
_DATA_DIR = Path(__file__).parent / "data"


def _path(name: str) -> Path:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    return _DATA_DIR / f"{name}.json"


def load(name: str) -> dict[str, Any]:
    """Load a named store from disk, returning an empty dict if not found."""
    p = _path(name)
    if not p.exists():
        return {}
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save(name: str, data: dict[str, Any]) -> None:
    """Persist a named store to disk atomically."""
    p = _path(name)
    tmp = p.with_suffix(".tmp")
    try:
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        tmp.replace(p)
    except OSError:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise

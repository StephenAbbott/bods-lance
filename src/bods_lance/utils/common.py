"""Shared helpers used across transform modules."""

from __future__ import annotations

from typing import Any


def get(d: dict, *keys: str, default: Any = None) -> Any:
    """Safe nested dict lookup — returns *default* if any key is missing."""
    current = d
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def coerce_float(value: Any) -> float | None:
    """Return *value* as float, or None if conversion fails."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def pick_primary_name(names: list[dict] | None) -> str | None:
    """Return the most appropriate display name from a BODS names array.

    Preference order: ``legal`` → ``trading`` → first entry.
    """
    if not names:
        return None
    for preferred_type in ("legal", "trading"):
        for n in names:
            if n.get("type") == preferred_type and n.get("fullName"):
                return n["fullName"]
    # Fall back to first non-empty fullName
    for n in names:
        if n.get("fullName"):
            return n["fullName"]
    return None

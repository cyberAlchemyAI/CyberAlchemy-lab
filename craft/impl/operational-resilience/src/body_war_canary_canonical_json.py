"""Canonical JSON helpers for Body War canary receipts."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any


def _validate(value: Any) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("CANONICAL_JSON_NON_FINITE")
        return
    if isinstance(value, list):
        for item in value:
            _validate(item)
        return
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("CANONICAL_JSON_NON_STRING_KEY")
        for item in value.values():
            _validate(item)
        return
    raise ValueError(f"CANONICAL_JSON_UNSUPPORTED:{type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    _validate(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()

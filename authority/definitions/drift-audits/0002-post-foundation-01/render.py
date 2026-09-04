#!/usr/bin/env python3
"""Invoke the admitted Foundation projection contract for one drift audit."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB_ROOT = ROOT.parents[3]
FOUNDATION_RENDERER = LAB_ROOT / "authority/foundation/v1/render.py"
SOURCE = ROOT / "drift-audit.json"
OUTPUT = ROOT / "DEFINITION-DRIFT-AUDIT.md"


def render(data: dict) -> str:
    spec = importlib.util.spec_from_file_location("foundation_projection_renderer", FOUNDATION_RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Foundation-01 renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.drift(data).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()

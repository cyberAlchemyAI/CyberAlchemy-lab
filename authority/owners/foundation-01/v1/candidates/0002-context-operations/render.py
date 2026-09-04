#!/usr/bin/env python3
"""Render the context-operations owner-registry successor candidate."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "owners.json"
OUTPUT = ROOT / "OWNERS.md"
FOUNDATION_RENDERER = ROOT.parents[4] / "foundation/v1/render.py"


def _renderer():
    spec = importlib.util.spec_from_file_location("foundation_owner_renderer", FOUNDATION_RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {FOUNDATION_RENDERER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.owners


def render(data: dict) -> str:
    return _renderer()(data).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()

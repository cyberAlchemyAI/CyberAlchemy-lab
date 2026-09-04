#!/usr/bin/env python3
"""Render Definition/v1 candidate.2 through the shared v1 artifact renderer."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SHARED_RENDERER = ROOT.parents[1] / "render.py"
SOURCE = ROOT / "artifact.json"
OUTPUT = ROOT / "ARTIFACT.md"


def render(data: dict) -> str:
    spec = importlib.util.spec_from_file_location("definition_v1_artifact_renderer", SHARED_RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load shared Definition/v1 artifact renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render(data)


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()

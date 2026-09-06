#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SHARED = LAB / "tooling/generators/ctx01_artifact.py"


def render(data: dict) -> str:
    spec = importlib.util.spec_from_file_location("ctx01_instance_renderer", SHARED)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SHARED}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render_instance(data, "coordination-context")


def main() -> None:
    data = json.loads((ROOT / "coordination-context.json").read_text(encoding="utf-8"))
    (ROOT / "COORDINATION-CONTEXT.md").write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()

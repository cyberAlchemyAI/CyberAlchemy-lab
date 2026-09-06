#!/usr/bin/env python3
"""Verify all human projections in the admitted Definition closure."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    decision_root = LAB / "docs/decisions/0018-definition-and-ctx00-promotion"
    decision = load(decision_root / "decision.json")
    definition_renderer = load_module("ctx00_projection_definition", LAB / "authority/artifact-types/definition/v1/generator.py")
    foundation_renderer = load_module("ctx00_projection_foundation", LAB / "authority/foundation/v1/render.py")
    decision_renderer = load_module("ctx00_projection_decision", decision_root / "render-decision.py")
    results = []
    for item in decision["admitted_definitions"]:
        source = LAB / item["path"]
        output = source.with_name("DEFINITION.md")
        results.append(output.is_file() and output.read_text(encoding="utf-8") == definition_renderer.render(load(source)))
    registry = load(LAB / "authority/definitions/registry.json")
    results.append((LAB / "authority/definitions/DEFINITIONS-INDEX.md").read_text(encoding="utf-8") == foundation_renderer.registry(registry).rstrip() + "\n")
    drift = load(LAB / "authority/definitions/drift-audit.json")
    results.append((LAB / "authority/definitions/DEFINITION-DRIFT-AUDIT.md").read_text(encoding="utf-8") == foundation_renderer.drift(drift).rstrip() + "\n")
    results.append((decision_root / "DECISION.md").read_text(encoding="utf-8") == decision_renderer.render(decision))
    status = "PASS" if len(results) == 11 and all(results) else "FAIL"
    print(f"CTX00_ADMISSION_PROJECTIONS={status}")
    print(f"CHECKS={sum(results)}/{len(results)}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render(data: dict) -> str:
    source = data["source_selection"]
    lines = [
        "<!-- Generated from test-profile.json. Do not edit. -->", "",
        "# Ontology Product end-to-end test epoch 001", "",
        f"- Test epoch: `{data['test_epoch_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Construction stage: `{data['construction_stage']}`", "",
        "## Selected real source", "",
        f"- Ontology: `{source['ontology_id']}`",
        f"- Nodes: `{source['expected_nodes']}`",
        f"- Relations: `{source['expected_relations']}`",
        f"- Typed residue: `{source['expected_residue']}`",
        f"- Bound sources: `{source['expected_sources']}`", "",
        "## Acceptance criteria", "",
    ]
    lines.extend(f"- {item}" for item in data["acceptance_criteria"])
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    data = json.loads((ROOT / "test-profile.json").read_text(encoding="utf-8"))
    (ROOT / "PRODUCT-TEST.md").write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()

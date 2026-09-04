#!/usr/bin/env python3
"""Render the CTX04 Governance-to-Ontology-Lifecycle map pack."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "map-pack.json"
OUTPUT = ROOT / "MAP-PACK.md"


def render(data: dict) -> str:
    pattern = data["selected_pattern"]
    lines = [
        "<!-- GENERATED FILE: edit map-pack.json and rerun render.py. -->",
        "",
        "# Governance to Ontology Lifecycle Context Map candidate pack",
        "",
        "> Generated from `map-pack.json`; this view is not canonical.",
        "",
        f"- Pack: `{data['pack_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Selected candidate pattern",
        "",
        f"`{pattern['upstream_context_ref']}` → `{pattern['downstream_context_ref']}`",
        "",
        f"Pattern: `{pattern['pattern_ref']}`",
        "",
        pattern["meaning"],
        "",
        f"Reverse dependency: `{pattern['reverse_dependency']}`",
        "",
        "## Four facets",
        "",
    ]
    for facet, statement in data["four_facet_contract"].items():
        lines.extend([f"### {facet.replace('_', ' ').title()}", "", statement, ""])
    lines.extend(["## Orthogonality contract", ""])
    lines.extend(f"- {item}" for item in data["orthogonality_contract"])
    lines.extend(["", "## Exact selected inputs", "", "| Input | Path | SHA-256 | Purpose |", "| --- | --- | --- | --- |"])
    for item in data["selected_inputs"]:
        lines.append(f"| `{item['input_id']}` | `{item['path']}` | `{item['sha256']}` | {item['purpose']} |")
    lines.extend(["", "## Unselected successors", ""])
    lines.extend(f"- {item}" for item in data["unselected_successors"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")

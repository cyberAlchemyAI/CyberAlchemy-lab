#!/usr/bin/env python3
"""Render the CTX03 context candidate pack projection."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "context-pack.json"
OUTPUT = ROOT / "CONTEXT-PACK.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit context-pack.json and rerun render.py. -->",
        "",
        "# Governance and Ontology Lifecycle candidate pack",
        "",
        "> Generated from `context-pack.json`; this view is not canonical.",
        "",
        f"- Pack: `{data['pack_id']}`",
        f"- Version: `{data['version']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Objective",
        "",
        data["objective"],
        "",
        "## Canonical artifacts",
        "",
        "| Kind | Identity | Canonical | Projection |",
        "| --- | --- | --- | --- |",
    ]
    for item in data["canonical_artifacts"]:
        lines.append(f"| `{item['artifact_type']}` | `{item['artifact_id']}` | `{item['path']}` | `{item['projection']}` |")
    lines.extend(["", "## Four facets", ""])
    for facet, statement in data["four_facet_contract"].items():
        lines.extend([f"### {facet.replace('_', ' ').title()}", "", statement, ""])
    lines.extend(["## Orthogonality contract", ""])
    lines.extend(f"- {item}" for item in data["orthogonality_contract"])
    lines.extend(["", "## Exact selected inputs", "", "| Input | Root | Path | SHA-256 | Purpose |", "| --- | --- | --- | --- | --- |"])
    for item in data["selected_inputs"]:
        lines.append(f"| `{item['input_id']}` | `{item['root']}` | `{item['path']}` | `{item['sha256']}` | {item['purpose']} |")
    lines.extend(["", "## Unselected successors", ""])
    lines.extend(f"- {item}" for item in data["unselected_successors"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")

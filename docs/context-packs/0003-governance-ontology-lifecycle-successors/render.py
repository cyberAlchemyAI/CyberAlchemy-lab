#!/usr/bin/env python3
"""Render the CTX05 successor candidate pack."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "successor-pack.json"
OUTPUT = ROOT / "SUCCESSOR-PACK.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit successor-pack.json and rerun render.py. -->",
        "",
        "# Governance and Ontology Lifecycle successor candidate pack",
        "",
        "> Machine-canonical pack; this Markdown is a generated projection.",
        "",
        f"- Pack: `{data['pack_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Gate: `{data['current_gate']}`",
        "",
        "## Objective",
        "",
        data["objective"],
        "",
        "## Authorship direction",
        "",
        f"- Principal: `{data['authorship_direction']['principal']}`",
        f"- Instruction: {data['authorship_direction']['instruction']}",
        f"- Effect: `{data['authorship_direction']['effect']}`",
        "",
        "## Canonical artifacts",
        "",
        "| Artifact | Type | Canonical path | Digest | Projection |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in data["canonical_artifacts"]:
        lines.append(f"| `{item['artifact_id']}` | `{item['artifact_type']}` | `{item['path']}` | `{item['sha256']}` | `{item['projection']}` |")
    boundary = data["migration_boundary"]
    lines.extend([
        "",
        "## Migration boundary",
        "",
        f"- Source repository: `{boundary['source_repository_ref']}`",
        f"- Exact source selections: `{boundary['selected_source_count']}`",
        f"- Destination candidates: `{boundary['destination_candidate_count']}`",
        f"- Predecessor preservation: `{boundary['predecessor_preservation']}`",
        f"- Physical source relocation: `{boundary['physical_source_package_relocation']}`",
        f"- Execution authority: `{str(boundary['execution_authority']).lower()}`",
        "",
        "## Residue",
        "",
    ])
    lines.extend(f"- {item}" for item in data["residue_refs"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")

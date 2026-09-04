#!/usr/bin/env python3
"""Render the Definition/v1 artifact-type candidate for human review."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "artifact.json"
OUTPUT = ROOT / "ARTIFACT.md"


def render(data: dict) -> str:
    meaning = data["definition_semantics"]
    lines = [
        "<!-- GENERATED FILE: edit artifact.json and run render.py. -->",
        "",
        f"# {data['name']} {data['version']}",
        "",
        "> Human projection generated from `artifact.json`; it is not canonical.",
        "",
        f"- Artifact type ID: `{data['artifact_type_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Semantic owner: `{data['semantic_owner_ref']}`",
        "",
        "## Definition semantics",
        "",
        meaning["scientific_formal_voice"],
        "",
        "### Plain language",
        "",
        meaning["plain_language_voice"],
        "",
        "### CyberAlchemy Lab context",
        "",
        meaning["domain_context_voice"],
        "",
        "### Boundaries",
        "",
    ]
    lines.extend(f"- {item}" for item in meaning["boundaries"])
    lines.extend([
        "", "## Instance contract", "",
        f"- Schema: `{data['schema_ref']}`",
        f"- Schema digest: `{data['schema_digest']}`",
        f"- Canonical filename: `{data['projection_contract']['canonical_filename']}`",
        f"- Human filename: `{data['projection_contract']['human_filename']}`",
        f"- Generator: `{data['projection_contract']['generator_ref']}`",
        f"- Generator digest: `{data['projection_contract']['generator_sha256']}`",
        "", "## Producer constraints", "",
    ])
    lines.extend(f"- {item}" for item in data["producer_constraints"])
    lines.extend(["", "## Origin constraints", ""])
    lines.extend(f"- {item}" for item in data["origin_constraints"])
    lines.extend(["", "## Allowed relation kinds", ""])
    lines.extend(f"- `{item}`" for item in data["allowed_relation_kinds"])
    lines.extend(["", "## Typed residue", ""])
    for item in data["typed_residue"]:
        lines.extend([f"### {item['residue_id']}", "", item["missing"], "", f"Consequence: {item['consequence']}", ""])
    lines.extend(["## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()

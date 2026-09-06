#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render(migration: dict, bindings: dict) -> str:
    counts = migration["expected_counts"]
    lines = [
        "<!-- Generated from migration.json and source-bindings.json. Do not edit. -->",
        "",
        "# Source-preserving Product Ontology package",
        "",
        f"- Migration: `{migration['migration_id']}`",
        f"- Source ontology: `{migration['source_ontology_ref']}`",
        f"- Destination role: `{migration['destination_ontology_ref']}`",
        f"- Status: `{migration['status']}`",
        f"- Authority effect: `{migration['authority_effect']}`",
        f"- Shape: `{counts['nodes']}` nodes, `{counts['relations']}` relations, `{counts['relation_types']}` relation types, `{counts['residue']}` residue records",
        "",
        "## Imported files",
        "",
    ]
    lines.extend(f"- `{item['path']}` — `{item['sha256']}`" for item in migration["imported_files"])
    lines += ["", "## Source bindings", "", "| Source | Status | Legacy digest | Current digest |", "| --- | --- | --- | --- |"]
    for item in bindings["bindings"]:
        lines.append(f"| `{item['source_id']}` | `{item['binding_status']}` | `{item['legacy_sha256']}` | `{item['current_sha256']}` |")
    lines += ["", "## Preservation rules", ""]
    lines.extend(f"- {item}" for item in migration["preservation_rules"])
    lines += ["", "## Claim ceiling", "", migration["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    migration = json.loads((ROOT / "migration.json").read_text(encoding="utf-8"))
    bindings = json.loads((ROOT / "source-bindings.json").read_text(encoding="utf-8"))
    (ROOT / "SOURCE-PACKAGE.md").write_text(render(migration, bindings), encoding="utf-8")


if __name__ == "__main__":
    main()

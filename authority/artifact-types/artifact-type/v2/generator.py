#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit artifact.json and run generator.py. -->", "",
        "# Artifact Type v2", "", "> Generated from `artifact.json`; this view is not canonical.", "",
        f"- Status: `{data['status']}`", f"- Authority effect: `{data['authority_effect']}`",
        f"- Owner: `{data['semantic_owner_ref']}`", f"- Predecessor: `{data['predecessor']['artifact_type_ref']}`", "",
        "## Semantic Definition bindings", "",
    ]
    for item in data["semantic_definition_bindings"]:
        lines.append(f"- `{item['definition_ref']}` — `{item['admission_posture']}` — `{item['path']}`")
    lines += ["", "## Registration policy", ""]
    for key, value in data["registration_policy"].items():
        lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
    lines += ["", "## Registrations authored under v2", "", "| Type | Semantic kind | Definition refs | Schema | Purpose |", "| --- | --- | --- | --- | --- |"]
    for item in data["registered_types"]:
        refs = ", ".join(f"`{value}`" for value in item["semantic_definition_refs"])
        lines.append(f"| `{item['artifact_type_ref']}` | `{item['semantic_kind']}` | {refs} | `{item['schema_path']}` | {item['distinct_validation_purpose']} |")
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    data = json.loads((ROOT / "artifact.json").read_text(encoding="utf-8"))
    (ROOT / "ARTIFACT.md").write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()

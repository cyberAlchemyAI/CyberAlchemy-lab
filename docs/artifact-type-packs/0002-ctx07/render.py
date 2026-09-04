#!/usr/bin/env python3
"""Render the CTX07 artifact-type candidate pack."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "artifact-type-pack.json"
OUTPUT = ROOT / "ARTIFACT-TYPE-PACK.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit artifact-type-pack.json and rerun render.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Generated from `artifact-type-pack.json`; this view is not canonical.",
        "",
        f"- Pack: `{data['pack_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Candidate artifact types",
        "",
        "| Artifact type | Definition | Predecessor | Machine candidate |",
        "| --- | --- | --- | --- |",
    ]
    for item in data["artifact_types"]:
        lines.append(f"| `{item['artifact_type_ref']}` | `{item['definition_ref']}` | `{item['predecessor_ref']}` | `{item['artifact_path']}` |")
    lines.extend(["", "## Cross-type invariants", ""])
    lines.extend(f"- `{item['invariant_id']}` — {item['statement']}" for item in data["cross_type_invariants"])
    lines.extend(["", "## Promotion boundary", "", data["promotion_gate"]["required_effect"], "", data["promotion_gate"]["non_effect"], "", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")

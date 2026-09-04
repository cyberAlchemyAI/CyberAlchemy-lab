#!/usr/bin/env python3
"""Render the CTX08 normalized context successor candidate pack."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "context-pack.json"
OUTPUT = ROOT / "CONTEXT-PACK.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit context-pack.json and rerun render.py. -->",
        "",
        "# CTX08 normalized context successor candidate pack",
        "",
        "> Machine-canonical pack; this Markdown is a generated projection.",
        "",
        f"- Pack: `{data['pack_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Objective",
        "",
        data["objective"],
        "",
        "## Authorship direction",
        "",
        f"- Principal: `{data['authorship_direction']['principal']}`",
        f"- Instruction: `{data['authorship_direction']['instruction']}`",
        f"- Effect: `{data['authorship_direction']['effect']}`",
        "",
        "## Canonical candidates",
        "",
        "| Artifact | Type | Owner | Path | Digest |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in data["canonical_artifacts"]:
        lines.append(
            f"| `{item['artifact_id']}` | `{item['artifact_type_ref']}` | `{item['owner_role']}` | "
            f"`{item['path']}` | `{item['sha256']}` |"
        )
    lines.extend(["", "## Preserved admitted languages", "", "| Language | Stable context | Path | Digest |", "| --- | --- | --- | --- |"])
    for item in data["preserved_languages"]:
        lines.append(f"| `{item['language_ref']}` | `{item['stable_context_id']}` | `{item['path']}` | `{item['sha256']}` |")
    contract = data["normalization_contract"]
    lines.extend(
        [
            "",
            "## Normalization contract",
            "",
            f"- Canonical membership owner: `{contract['canonical_membership_owner']}`",
            f"- Language reuse: {contract['language_reuse_rule']}",
            f"- Lineage: {contract['lineage_rule']}",
            "- Forbidden endpoint fields:",
        ]
    )
    lines.extend(f"  - `{field}`" for field in contract["forbidden_endpoint_fields"])
    lines.extend(["", "## Promotion gate", "", f"- State: `{data['promotion_gate']['current_state']}`", f"- Required effect: {data['promotion_gate']['required_effect']}", "", "## Residue", ""])
    lines.extend(f"- {item}" for item in data["residue_refs"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")

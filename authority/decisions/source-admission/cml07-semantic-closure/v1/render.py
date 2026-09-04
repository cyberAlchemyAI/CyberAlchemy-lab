#!/usr/bin/env python3
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def render(data: dict) -> str:
    lines = [
        "# CML-07 Semantic Closure Source Admissions",
        "",
        "> Generated from `admissions.json`. Do not edit this projection directly.",
        "",
        f"- Record: `{data['record_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Owner: `{data['owner_ref']}` (`{data['owner_principal_ref']}`)",
        f"- Construction unit: `{data['target_scope']['construction_unit_id']}`",
        "",
        "## Exact selections",
        "",
    ]
    for item in data["admissions"]:
        lines.extend([
            f"### {item['admission_id']}",
            "",
            f"- Source: `{item['source_repository']}:{item['source_path']}:{item['start_line']}-{item['end_line']}`",
            f"- Selected SHA-256: `{item['selected_sha256']}`",
            f"- Target Definitions: {', '.join(f'`{x}`' for x in item['target_definition_ids'])}",
            f"- Permitted use: {item['target_use']}",
            "- Non-effects:",
        ])
        lines.extend(f"  - {value}" for value in item["non_effects"])
        lines.append("")
    lines.extend(["## Claim ceiling", "", data["claim_ceiling"], ""])
    return "\n".join(lines)


if __name__ == "__main__":
    data = json.loads((HERE / "admissions.json").read_text())
    (HERE / "SOURCE-ADMISSIONS.md").write_text(render(data))

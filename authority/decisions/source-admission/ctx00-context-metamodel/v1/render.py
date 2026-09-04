#!/usr/bin/env python3
"""Render the CTX-00 source-admission human projection."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "admissions.json"
OUTPUT = ROOT / "SOURCE-ADMISSIONS.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit admissions.json and run render.py. -->",
        "",
        "# CTX-00 context-metamodel source admissions",
        "",
        "> Human projection generated from `admissions.json`; it is not canonical.",
        "",
        f"- Record: `{data['record_id']}`",
        f"- Candidate status: `{data['status']}`",
        f"- Owner: `{data['owner_principal_ref']}` as `{data['owner_ref']}`",
        f"- Definition Pack: `{data['target_scope']['definition_pack_id']}`",
        "",
        "| Admission | Selection | Digest | Permitted concepts |",
        "| --- | --- | --- | --- |",
    ]
    for item in data["admissions"]:
        concepts = ", ".join(f"`{value}`" for value in item["target_concept_ids"])
        lines.append(
            f"| `{item['admission_id']}` | `{item['selector']}` | `{item['selected_sha256']}` | {concepts} |"
        )
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")

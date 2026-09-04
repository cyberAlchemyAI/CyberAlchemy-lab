#!/usr/bin/env python3
"""Render the successor CTX-00 Definition Pack."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "definition-pack.json"
OUTPUT = ROOT / "DEFINITION-PACK.md"


def render(data: dict) -> str:
    candidate = data["candidate_set"]
    lines = ["<!-- GENERATED FILE: edit definition-pack.json and run render.py. -->", "", f"# {data['title']}", "", "> Generated from the machine-canonical Definition Pack; it is not authority.", "", f"- Pack: `{data['pack_id']}`", f"- Status: `{data['status']}`", f"- Authority effect: `{data['authority_effect']}`", f"- Candidate set: `{candidate['candidate_id']}`", f"- Validation: `{candidate['validation_result']}` ({candidate['validation_checks']}/{candidate['validation_checks']})", f"- Promotion eligibility: `{candidate['promotion_eligibility']}`", "", "## Definition candidates", ""]
    lines.extend(f"- `{item}`" for item in data["definition_ids"])
    lines.extend(["", "## Resolved predecessor blockers", ""])
    lines.extend(f"- {item}" for item in data["resolved_predecessor_blockers"])
    lines.extend(["", "## Remaining authority gate", "", data["remaining_authority_gate"], "", "## Successor work after admission", ""])
    lines.extend(f"- {item}" for item in data["successor_work_after_admission"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")

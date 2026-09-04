#!/usr/bin/env python3
"""Render the CTX-00 source-admission decision human projection."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit decision.json and run render.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Human projection generated from `decision.json`; it is not canonical.",
        "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Selected option: `{data['selection']['option_id']}`",
        f"- Principal: `{data['selection']['selected_by_principal']}` as `{data['selection']['selected_role']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Accepted source record: `{data['accepted_candidate']['sha256']}`",
        "",
        "## Outcome",
        "",
        data["admission_result"]["effect"],
        "",
        "## Exact admitted selections",
        "",
        "| Admission | Selector | Digest | Target concepts |",
        "| --- | --- | --- | --- |",
    ]
    for item in data["admitted_source_selections"]:
        concepts = ", ".join(f"`{value}`" for value in item["target_concept_ids"])
        lines.append(f"| `{item['admission_id']}` | `{item['selector']}` | `{item['selected_sha256']}` | {concepts} |")
    lines.extend(["", "## Decision Gate", "", f"- Route: `{data['admissibility']['route_outcome']}`", f"- Result: `{data['admission_result']['decision_gate_result']}`", f"- Request digest: `{data['admissibility']['request_digest']}`", f"- Limitation: {data['admissibility']['ordering_limitation']}", "", "## Explicit exclusions", ""])
    lines.extend(f"- {item}" for item in data["excluded_effects"])
    lines.extend(["", "## Successor obligations", ""])
    lines.extend(f"- {item}" for item in data["successor_obligations"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")

#!/usr/bin/env python3
"""Render the context-operational owner admission decision."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"


def render(data: dict) -> str:
    selection = data["selection"]
    lines = ["<!-- GENERATED FILE: edit decision.json and rerun render-decision.py. -->", "", "# Context-operational owner admission decision", "", "> Machine-canonical decision; this Markdown is a generated projection.", "", f"- Status: `{data['status']}`", f"- Selection: `{selection['option_id']}`", f"- Principal: `{selection['selected_by_principal']}`", f"- Recorded: `{selection['recorded_at']}`", "", "## Admitted operational roles", "", "| Role | Principal | Effect |", "| --- | --- | --- |"]
    for item in data["admitted_operational_roles"]:
        lines.append(f"| `{item['role_id']}` | `{item['principal_id']}` | {item['effect']} |")
    result = data["admission_result"]
    lines += ["", "## Admission result", "", f"- Foundation roles preserved: `{result['foundation_roles_preserved']}`", f"- Operational roles admitted: `{result['operational_roles_admitted']}`", f"- Current role count: `{result['current_role_count']}`", f"- Context instances created: `{result['context_instances_created']}`", "", "## Excluded effects", ""]
    lines.extend(f"- {item}" for item in data["excluded_effects"])
    lines += ["", "## Successor obligations", ""]
    lines.extend(f"- {item}" for item in data["successor_obligations"])
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()

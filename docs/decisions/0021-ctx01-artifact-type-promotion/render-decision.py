#!/usr/bin/env python3
"""Render the exact CTX01 artifact-type admission decision."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"


def render(data: dict) -> str:
    selection = data["selection"]
    lines = ["<!-- GENERATED FILE: edit decision.json and rerun render-decision.py. -->", "", "# CTX01 artifact-type admission decision", "", "> Machine-canonical decision; this Markdown is a generated projection.", "", f"- Status: `{data['status']}`", f"- Selection: `{selection['option_id']}`", f"- Owner: `{selection['selected_role']} -> {selection['selected_by_principal']}`", f"- Recorded: `{selection['recorded_at']}`", "", "## Admitted artifact types", "", "| Artifact type | Artifact | Schema |", "| --- | --- | --- |"]
    for item in data["admitted_artifact_types"]:
        lines.append(f"| `{item['artifact_type_ref']}` | `{item['artifact_path']}` | `{item['schema_path']}` |")
    lines += ["", "## Admission result", "", f"Artifact Type/v1 successor current: `{data['admission_result']['artifact_type_successor_current']}`", "", f"Artifact types admitted: `{data['admission_result']['artifact_types_admitted']}`", "", "## Excluded effects", ""]
    lines.extend(f"- {item}" for item in data["excluded_effects"])
    lines += ["", "## Successor obligations", ""]
    lines.extend(f"- {item}" for item in data["successor_obligations"])
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()

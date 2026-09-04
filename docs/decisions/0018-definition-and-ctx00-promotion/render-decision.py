#!/usr/bin/env python3
"""Render the Definition and CTX00 admission decision from canonical JSON."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit decision.json and rerun render-decision.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Generated from `decision.json`; this view is not canonical.",
        "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Selected by: `{data['selection']['selected_by_principal']}` as `{data['selection']['selected_role']}`",
        f"- Selection token: `{data['selection']['selection_token']}`",
        "",
        "## Admitted Definitions",
        "",
        "| Definition | Version | Canonical machine record | Digest |",
        "| --- | --- | --- | --- |",
    ]
    for item in data["admitted_definitions"]:
        lines.append(f"| `{item['definition_id']}` | `{item['version']}` | `{item['path']}` | `{item['sha256']}` |")
    result = data["admission_result"]
    lines.extend([
        "",
        "## Result",
        "",
        f"- Definitions admitted: `{result['definitions_admitted']}`",
        f"- Registry entries: `{result['registry_entries']}`",
        f"- Definition evaluation gate: `{result['definition_evaluation_gate']}`",
        f"- Open successor context blockers: `{result['successor_context_blockers']}`",
        "",
        "## Materialization rule",
        "",
        data["materialization"]["rule"],
        "",
        data["materialization"]["version_label_note"],
        "",
        "## Explicit non-effects",
        "",
    ])
    lines.extend(f"- {item}" for item in data["excluded_effects"])
    lines.extend(["", "## Successor obligations", ""])
    lines.extend(f"- {item}" for item in data["successor_obligations"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()

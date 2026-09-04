#!/usr/bin/env python3
"""Render the CTX05 successor admission decision."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"


def render(data: dict) -> str:
    selection = data["selection"]
    result = data["admission_result"]
    lines = [
        "<!-- GENERATED FILE: edit decision.json and rerun render.py. -->",
        "",
        "# CTX05 successor context, lineage, and migration-plan admission",
        "",
        "> Machine-canonical decision; this Markdown is a generated projection.",
        "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Selection: `{selection['selection_token']}`",
        f"- Principal: `{selection['selected_by_principal']}`",
        f"- Recorded: `{selection['recorded_at']}`",
        "",
        "## Admitted artifacts",
        "",
        "| Artifact | Type | Owner | Overlay | Digest |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in data["admitted_artifacts"]:
        lines.append(f"| `{item['artifact_id']}` | `{item['artifact_type_ref']}` | `{item['owner_role']}` | `{item['decision_overlay_status']}` | `{item['sha256']}` |")
    lines.extend([
        "",
        "## Admission result",
        "",
        f"- Bounded Context successors: `{result['bounded_context_successors_admitted']}`",
        f"- Ubiquitous Language successors: `{result['ubiquitous_language_successors_admitted']}`",
        f"- Lineage records: `{result['lineage_records_admitted']}`",
        f"- Migration plans: `{result['migration_plans_admitted']}`",
        f"- Migration execution authorizations: `{result['migration_execution_authorizations']}`",
        f"- Predecessors superseded: `{result['predecessors_superseded']}`",
        "",
        "## Boundaries",
        "",
    ])
    lines.extend(data["materialization"][field] for field in ("rule", "successor_boundary", "lineage_boundary", "map_boundary", "migration_boundary"))
    lines.extend(["", "## Excluded effects", ""])
    lines.extend(f"- {item}" for item in data["excluded_effects"])
    lines.extend(["", "## Successor obligations", ""])
    lines.extend(f"- {item}" for item in data["successor_obligations"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")

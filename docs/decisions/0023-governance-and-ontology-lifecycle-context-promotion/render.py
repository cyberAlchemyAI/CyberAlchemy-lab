#!/usr/bin/env python3
"""Render the CTX03 context-language admission decision."""

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
        "# Governance and Ontology Lifecycle context-language admission",
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
        "| Artifact | Type | Version | Owner role | Effect |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in data["admitted_artifacts"]:
        lines.append(f"| `{item['artifact_id']}` | `{item['artifact_type_ref']}` | `{item['version']}` | `{item['owner_role']}` | `{item['decision_overlay_status']}` |")
    lines.extend([
        "",
        "## Admission result",
        "",
        f"- Bounded Contexts admitted: `{result['bounded_contexts_admitted']}`",
        f"- Ubiquitous Languages admitted: `{result['ubiquitous_languages_admitted']}`",
        f"- Context Maps admitted: `{result['context_maps_admitted']}`",
        f"- Migration Manifests admitted: `{result['migration_manifests_admitted']}`",
        "",
        "## Materialization",
        "",
        data["materialization"]["rule"],
        "",
        data["materialization"]["context_language_pairing"],
        "",
        data["materialization"]["cross_context_boundary"],
        "",
        "## Excluded effects",
        "",
    ])
    lines.extend(f"- {item}" for item in data["excluded_effects"])
    lines.extend(["", "## Successor obligations", ""])
    lines.extend(f"- {item}" for item in data["successor_obligations"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")

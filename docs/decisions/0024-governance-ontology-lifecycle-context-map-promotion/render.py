#!/usr/bin/env python3
"""Render the CTX04 Context Map admission decision."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"


def render(data: dict) -> str:
    selection = data["selection"]
    map_binding = data["admitted_map"]
    relationship = data["admitted_relationship"]
    result = data["admission_result"]
    lines = [
        "<!-- GENERATED FILE: edit decision.json and rerun render.py. -->",
        "",
        "# Governance to Ontology Lifecycle Context Map admission",
        "",
        "> Machine-canonical decision; this Markdown is a generated projection.",
        "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Selection: `{selection['selection_token']}`",
        f"- Principal: `{selection['selected_by_principal']}`",
        f"- Authority: `{selection['selected_authority']}`",
        f"- Recorded: `{selection['recorded_at']}`",
        "",
        "## Admitted map",
        "",
        f"- Map: `{map_binding['context_map_id']}`",
        f"- Type: `{map_binding['artifact_type_ref']}`",
        f"- Version: `{map_binding['version']}`",
        f"- Candidate digest: `{map_binding['sha256']}`",
        f"- Overlay: `{map_binding['decision_overlay_status']}`",
        "",
        "## Admitted directional relationship",
        "",
        f"- Relationship: `{relationship['relationship_id']}`",
        f"- Direction: `{relationship['source_context_ref']}` -> `{relationship['target_context_ref']}`",
        f"- Pattern: `{relationship['relationship_kind_ref']}`",
        f"- Scope: `{relationship['relationship_kind_scope']}`",
        f"- Global relationship-kind status: `{relationship['global_relationship_kind_status']}`",
        "",
        "## Admission result",
        "",
        f"- Context Maps admitted: `{result['context_maps_admitted']}`",
        f"- Directional relationships admitted: `{result['directional_relationships_admitted']}`",
        f"- Global relationship kinds admitted: `{result['global_relationship_kinds_admitted']}`",
        f"- Reverse dependencies admitted: `{result['reverse_dependencies_admitted']}`",
        f"- Endpoint artifacts mutated: `{result['endpoint_artifacts_mutated']}`",
        "",
        "## Materialization",
        "",
        data["materialization"]["rule"],
        "",
        data["materialization"]["relationship_scope"],
        "",
        data["materialization"]["authority_boundary"],
        "",
        data["materialization"]["endpoint_references"],
        "",
        "## Excluded effects",
        "",
    ]
    lines.extend(f"- {item}" for item in data["excluded_effects"])
    lines.extend(["", "## Successor obligations", ""])
    lines.extend(f"- {item}" for item in data["successor_obligations"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")

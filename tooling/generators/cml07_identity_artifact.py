#!/usr/bin/env python3
"""Deterministic human projections for CML-07 identity Artifact Types."""

from __future__ import annotations

import json
from typing import Any


def render_artifact(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit artifact.json and run generator.py. -->",
        "",
        f"# {data['name']} Artifact Type v1",
        "",
        "> Generated from `artifact.json`; this view is explanatory and not canonical.",
        "",
        f"- Type: `{data['artifact_type_ref']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Semantic owner: `{data['semantic_owner_ref']}`",
        f"- Canonical instance: `{data['instance_contract']['canonical_filename']}`",
        f"- Human projection: `{data['instance_contract']['human_filename']}`",
        "",
        "## Semantic Definition bindings",
        "",
    ]
    for item in data["semantic_definition_bindings"]:
        lines.append(f"- `{item['definition_ref']}` — `{item['admission_posture']}` — `{item['path']}`")
    lines.extend(["", "## Distinct validation purpose", "", data["distinct_validation_purpose"], "", "## Orthogonality rules", ""])
    for item in data["orthogonality_rules"]:
        lines.append(f"- **{item['rule_id']}**: {item['statement']}")
    lines.extend(["", "## Four facets", ""])
    for key, value in data["four_facets"].items():
        lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
    lines.extend(["", "## Typed residue", ""])
    for item in data["typed_residue"]:
        lines.append(f"- `{item['residue_id']}` ({item['owner_ref']}): {item['missing']} Consequence: {item['consequence']}")
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def render_instance(artifact: dict[str, Any], data: dict[str, Any]) -> str:
    identity_field = artifact["instance_contract"]["identity_field"]
    lines = [
        "<!-- GENERATED FILE: canonical data is the sibling JSON fixture. -->",
        "",
        f"# {artifact['name']} Fixture",
        "",
        f"- Identity: `{data[identity_field]}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Canonical field projection",
        "",
    ]
    for key, value in data.items():
        if key in {identity_field, "status", "authority_effect"}:
            continue
        label = key.replace("_", " ").title()
        if isinstance(value, (dict, list)):
            lines.extend([f"### {label}", "", "```json", json.dumps(value, indent=2, sort_keys=True), "```", ""])
        else:
            lines.extend([f"- **{label}**: `{value}`"])
    lines.extend(["", "## Projection boundary", "", "This document is generated from the canonical machine fixture and adds no identity, relation, lifecycle, conformance, or authority field."])
    return "\n".join(lines).rstrip() + "\n"

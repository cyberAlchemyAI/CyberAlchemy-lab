#!/usr/bin/env python3
"""Deterministic projections for immutable modernized Artifact Type successors."""

from __future__ import annotations

import json
from typing import Any


def render_artifact(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is artifact.json. -->", "",
        f"# {data['name']} Artifact Type successor", "",
        f"- Type: `{data['artifact_type_ref']}`",
        f"- Version: `{data['version']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Admitted predecessor: `{data['predecessor_contract']['artifact_type_ref']}`",
        f"- Definition: `{data['semantic_definition_refs'][0]}`", "",
        "## Distinct validation purpose", "", data["distinct_validation_purpose"], "",
        "## Relation surface", "",
    ]
    if data["relation_roles"]:
        for role in data["relation_roles"]:
            lines.append(f"- `{role['direction']}` `{role['relation_kind_ref']}` with `{', '.join(role['counterpart_kinds'])}`")
    else:
        lines.append("- No Relation Kind in the closed candidate relation model currently names this carrier as an endpoint.")
    lines += ["", "## Orthogonality rules", ""]
    lines += [f"- **{rule['rule_id']}**: {rule['statement']}" for rule in data["orthogonality_rules"]]
    lines += ["", "## Typed residue", ""]
    lines += [f"- `{item['residue_id']}` ({item['owner_ref']}): {item['missing']} Consequence: {item['consequence']}" for item in data["typed_residue"]]
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def render_instance(artifact: dict[str, Any], data: dict[str, Any]) -> str:
    identity = artifact["instance_contract"]["identity_field"]
    lines = [
        "<!-- GENERATED FILE: canonical data is the sibling JSON file. -->", "",
        f"# {artifact['name']} successor fixture", "",
        f"- Identity: `{data[identity]}`",
        f"- Schema version: `{data.get('schema_version', 'not-declared')}`", "",
        "## Canonical fixture", "", "```json", json.dumps(data, indent=2, sort_keys=True), "```", "",
        "## Projection boundary", "", "This generated view adds no admission, authority, relation, lifecycle, migration, deletion, or runtime effect.",
    ]
    return "\n".join(lines).rstrip() + "\n"

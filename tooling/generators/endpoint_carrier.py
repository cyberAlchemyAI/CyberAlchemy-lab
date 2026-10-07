#!/usr/bin/env python3
"""Deterministic projections for closed endpoint carrier candidates."""

from __future__ import annotations

import json
from typing import Any


def render_artifact(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is artifact.json. -->",
        "",
        f"# {data['name']} Artifact Type v1",
        "",
        f"- Type: `{data['artifact_type_ref']}`",
        f"- Version: `{data['version']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Semantic Definition: `{data['semantic_definition_refs'][0]}`",
        "",
        "## Distinct validation purpose",
        "",
        data["distinct_validation_purpose"],
        "",
        "## Closed relation roles",
        "",
        "| Relation Kind | Direction | Counterpart kinds |",
        "| --- | --- | --- |",
    ]
    for role in data["relation_roles"]:
        lines.append(f"| `{role['relation_kind_ref']}` | `{role['direction']}` | `{', '.join(role['counterpart_kinds'])}` |")
    lines += ["", "## Non-collapse boundaries", ""]
    lines += [f"- `{data['classification']['semantic_kind']}` remains distinct from `{neighbor}`." for neighbor in data["hostile_non_collapse"]]
    lines += ["", "## Orthogonality rules", ""]
    lines += [f"- **{rule['rule_id']}**: {rule['statement']}" for rule in data["orthogonality_rules"]]
    lines += ["", "## Typed residue", ""]
    lines += [f"- `{item['residue_id']}` ({item['owner_ref']}): {item['missing']} Consequence: {item['consequence']}" for item in data["typed_residue"]]
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def render_instance(artifact: dict[str, Any], data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is record.json. -->",
        "",
        f"# {artifact['name']} fixture",
        "",
        f"- Identity: `{data['node_id']}`",
        f"- Kind: `{data['kind']}`",
        f"- Lifecycle: `{data['lifecycle_state']}`",
        f"- Owner: `{data['owner_ref']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Semantic payload",
        "",
        "```json",
        json.dumps(data["payload"], indent=2, sort_keys=True),
        "```",
        "",
        "## Declared relation roles",
        "",
    ]
    for relation in data["relation_refs"]:
        lines.append(f"- `{relation['direction']}` on `{relation['relation_kind_ref']}` with `{relation['counterpart_kind']}` `{relation['counterpart_ref']}`")
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"], "", "## Projection boundary", "", "This generated view adds no admission, authority, relation, lifecycle, or runtime effect."]
    return "\n".join(lines).rstrip() + "\n"

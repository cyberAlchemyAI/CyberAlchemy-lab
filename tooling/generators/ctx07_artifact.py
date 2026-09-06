#!/usr/bin/env python3
"""Deterministic projections for normalized CTX07 artifact types and fixtures."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

CONFIG = {
    "bounded-context": {
        "title": "Bounded Context",
        "identity": "context_id",
        "canonical": "context.json",
        "human": "CONTEXT.md",
    },
    "context-map": {
        "title": "Context Map",
        "identity": "context_map_id",
        "canonical": "map.json",
        "human": "MAP.md",
    },
}

COMMON_FIELDS = {
    "schema_version",
    "version",
    "status",
    "authority_effect",
    "classification",
    "source_direction",
    "evidence_refs",
    "residue_refs",
    "claim_ceiling",
}


def label(value: str) -> str:
    return value.replace("_", " ").title()


def render_value(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if value is None:
        return ["`null`"]
    if isinstance(value, bool):
        return [f"`{str(value).lower()}`"]
    if isinstance(value, (int, float)):
        return [f"`{value}`"]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return [f"- {item}" for item in value] or ["None declared."]
    return ["```json", json.dumps(value, indent=2, sort_keys=True), "```"]


def render_instance(data: dict, slug: str) -> str:
    config = CONFIG[slug]
    identity = data[config["identity"]]
    lines = [
        f"<!-- GENERATED FILE: edit {config['canonical']} and rerun generator.py. -->",
        "",
        f"# {config['title']}: {identity}",
        "",
        f"> Generated from `{config['canonical']}`; this view is not canonical.",
        "",
        f"- Identity: `{identity}`",
        f"- Version: `{data['version']}`",
        f"- Status: `{data['status']}`",
        f"- Artifact type: `{data['classification']['artifact_type_ref']}`",
        f"- Semantic kind: `{data['classification']['semantic_kind']}`",
        f"- Authority effect: `{data['authority_effect']}`",
    ]
    for field, value in data.items():
        if field in COMMON_FIELDS or field == config["identity"]:
            continue
        lines.extend(["", f"## {label(field)}", ""])
        lines.extend(render_value(value))
    lines.extend(["", "## Evidence", ""])
    lines.extend(render_value(data["evidence_refs"]))
    lines.extend(["", "## Residue", ""])
    lines.extend(render_value(data["residue_refs"]))
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def render_artifact_type(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit artifact.json and rerun generator.py. -->",
        "",
        f"# {data['name']} artifact type v2",
        "",
        "> Generated from `artifact.json`; this view is not canonical.",
        "",
        f"- Artifact type: `{data['artifact_type_ref']}`",
        f"- Candidate version: `{data['version']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Definition: `{data['definition_binding']['definition_id']}@{data['definition_binding']['version']}`",
        f"- Predecessor type: `{data['predecessor_artifact_type']['artifact_type_ref']}`",
        "",
        "## Representation contract",
        "",
        f"- Canonical machine file: `{data['instance_contract']['canonical_filename']}`",
        f"- Generated human file: `{data['instance_contract']['human_filename']}`",
        f"- Stable identity field: `{data['instance_contract']['identity_field']}`",
        f"- Schema: `{data['schema_ref']}`",
        "",
        "## Distinct validation purpose",
        "",
        data["distinct_validation_purpose"],
        "",
        "## Orthogonality rules",
        "",
        "| Rule | Mode | Requirement |",
        "| --- | --- | --- |",
    ]
    for rule in data["orthogonality_rules"]:
        lines.append(f"| `{rule['rule_id']}` | `{rule['validation_mode']}` | {rule['statement']} |")
    lines.extend(["", "## Four facets", ""])
    for facet, statement in data["four_facets"].items():
        lines.extend([f"### {label(facet)}", "", statement, ""])
    if "generated_projection_contract" in data:
        lines.extend(["## Generated projection contract", "", data["generated_projection_contract"]["purpose"], ""])
        lines.append(f"- Canonical inputs: `{data['generated_projection_contract']['canonical_inputs']}`")
        lines.append(f"- Generated machine projection: `{data['generated_projection_contract']['generated_machine_projection']}`")
        lines.append(f"- Authority effect: `{data['generated_projection_contract']['authority_effect']}`")
        lines.append("")
    lines.extend(["## Remaining residue", ""])
    for item in data["typed_residue"]:
        lines.append(f"- `{item['residue_id']}` — {item['missing']} Consequence: {item['consequence']}")
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def build_membership_index(map_sources: list[tuple[str, dict, str]]) -> dict:
    memberships: dict[str, set[str]] = defaultdict(set)
    generated_from = []
    for path, data, digest in sorted(map_sources, key=lambda item: (item[1]["context_map_id"], item[1]["version"], item[0])):
        map_ref = f"{data['context_map_id']}/v2"
        generated_from.append({"context_map_ref": map_ref, "path": path, "sha256": digest})
        for context_ref in data["context_refs"]:
            memberships[context_ref].add(map_ref)
    return {
        "schema_version": "cyberalchemy-lab-context-map-membership-index-projection/v1",
        "projection_id": "cal.projection.context-map-membership-index/v1",
        "canonical": False,
        "authority_effect": "none",
        "generated_from": generated_from,
        "memberships": [
            {"context_ref": context_ref, "context_map_refs": sorted(map_refs)}
            for context_ref, map_refs in sorted(memberships.items())
        ],
        "rebuild_rule": "Delete and deterministically rebuild this projection from the exact Context Map records listed in generated_from; endpoint Bounded Context records are not inputs.",
        "claim_ceiling": "This generated index is convenience lookup state. It cannot establish, amend, or revoke Context Map membership, context identity, authority, admission, or migration state.",
    }


def main_for(package_root: Path, slug: str) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.input is None:
        source = package_root / "artifact.json"
        output = package_root / "ARTIFACT.md"
        text = render_artifact_type(json.loads(source.read_text(encoding="utf-8")))
    else:
        source = args.input
        output = args.output or source.with_name(CONFIG[slug]["human"])
        text = render_instance(json.loads(source.read_text(encoding="utf-8")), slug)
    output.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render one CTX07 artifact instance")
    parser.add_argument("slug", choices=sorted(CONFIG))
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(render_instance(json.loads(args.input.read_text(encoding="utf-8")), args.slug), encoding="utf-8")

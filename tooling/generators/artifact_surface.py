#!/usr/bin/env python3
"""Deterministic human projections for Artifact Surface Foundation candidates."""

from __future__ import annotations
import json
from typing import Any

def render_artifact(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit artifact.json and run generator.py. -->", "",
        f"# {data['name']} Artifact Type v1", "",
        "> Generated from `artifact.json`; this view is explanatory and not canonical.", "",
        f"- Type: `{data['artifact_type_ref']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Canonical instance: `{data['instance_contract']['canonical_filename']}`",
        f"- Human projection: `{data['instance_contract']['human_filename']}`", "",
        "## Semantic bindings", "",
    ]
    for item in data["semantic_definition_bindings"]:
        lines.append(f"- `{item['definition_ref']}` — `{item['admission_posture']}` — `{item['path']}`")
    lines += ["", "## Distinct validation purpose", "", data["distinct_validation_purpose"], "", "## Orthogonality rules", ""]
    lines += [f"- **{x['rule_id']}**: {x['statement']}" for x in data["orthogonality_rules"]]
    lines += ["", "## Four facets", ""]
    lines += [f"- **{k.replace('_',' ').title()}**: {v}" for k,v in data["four_facets"].items()]
    lines += ["", "## Typed residue", ""]
    lines += [f"- `{x['residue_id']}` ({x['owner_ref']}): {x['missing']} Consequence: {x['consequence']}" for x in data["typed_residue"]]
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip()+"\n"

def render_instance(artifact: dict[str, Any], data: dict[str, Any]) -> str:
    ident = artifact["instance_contract"]["identity_field"]
    lines = ["<!-- GENERATED FILE: canonical data is the sibling JSON file. -->","",f"# {artifact['name']} Fixture","",f"- Identity: `{data[ident]}`",f"- Status: `{data['status']}`",f"- Authority effect: `{data['authority_effect']}`","","## Canonical machine projection",""]
    for key,value in data.items():
        if key in {ident,"status","authority_effect"}: continue
        label=key.replace('_',' ').title()
        if isinstance(value,(dict,list)):
            lines += [f"### {label}","","```json",json.dumps(value,indent=2,sort_keys=True),"```",""]
        else: lines.append(f"- **{label}**: `{value}`")
    lines += ["","## Projection boundary","","This generated view adds no canonical identity, lifecycle, conformance, or authority field."]
    return "\n".join(lines).rstrip()+"\n"

def render_registry(data: dict[str, Any]) -> str:
    lines=["<!-- GENERATED FILE: canonical data is registry.json. -->","","# Artifact Type Registry candidate","",f"- Registry: `{data['registry_id']}`",f"- Status: `{data['status']}`",f"- Entries: `{len(data['entries'])}`","","| Artifact Type | State | Discriminator | Contract | Decision |","| --- | --- | --- | --- | --- |"]
    for x in data["entries"]:
        disc=x["instance_discriminator"]
        lines.append(f"| `{x['artifact_type_ref']}` | `{x['lifecycle_state']}` | `{disc['path']}={disc['value']}` | `{x['artifact_path']}` | `{x['admission_decision_ref']}` |")
    lines += ["","## Claim ceiling","",data["claim_ceiling"]]
    return "\n".join(lines).rstrip()+"\n"

def render_audit(data: dict[str, Any]) -> str:
    lines=["<!-- GENERATED FILE: canonical data is audit.json. -->","",f"# {data['title']}","",f"- Result: `{data['result']}`",f"- Authority effect: `{data['authority_effect']}`","","## Findings",""]
    for x in data["findings"]: lines += [f"### {x['finding_id']} — {x['classification']}","",x['statement'],"",f"- Path: `{x['path']}`",f"- Treatment: {x['treatment']}",""]
    lines += ["## Claim ceiling","",data["claim_ceiling"]]
    return "\n".join(lines).rstrip()+"\n"

#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render_artifact(data: dict) -> str:
    lines = [
        "<!-- Generated from artifact.json. Do not edit. -->",
        "",
        "# Ontology Package Artifact Type v1",
        "",
        f"- Type: `{data['artifact_type_ref']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Owner: `{data['semantic_owner_ref']}`",
        f"- Schema: `{data['schema_ref']}`",
        "",
        "## Distinct validation purpose",
        "",
        data["distinct_validation_purpose"],
        "",
        "## Semantic Definition bindings",
        "",
    ]
    for item in data["semantic_definition_bindings"]:
        lines.append(f"- `{item['definition_ref']}` — `{item['admission_posture']}` — `{item['path']}` — selector `{item['selector']}`")
    lines += ["", "## Four facets", ""]
    for key, value in data["four_facets"].items():
        lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
    lines += ["", "## Typed residue", ""]
    for item in data["typed_residue"]:
        lines.append(f"- `{item['residue_id']}` — {item['missing']} Owner: `{item['owner_ref']}`. Consequence: {item['consequence']}")
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"], ""]
    return "\n".join(lines)


def cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_instance(package: dict) -> str:
    lines = [
        "<!-- Generated from ontology-package.json. Do not edit. -->",
        "",
        f"# Ontology package `{package['package_id']}`",
        "",
        f"- Version: `{package['version']}`",
        f"- Domain: `{package['domain']}`",
        f"- Status: `{package['status']}`",
        f"- Authority effect: `{package['authority_effect']}`",
        f"- Product: `{package['product_ref']}`",
        f"- Product output: `{package['product_output_ref']}`",
        f"- Source: `{package['source_binding']['source_id']}`",
        f"- Source digest: `{package['source_binding']['sha256']}`",
        "",
        "## Nodes",
        "",
        "| ID | Type | Label | Scope |",
        "| --- | --- | --- | --- |",
    ]
    for node in package["nodes"]:
        lines.append(f"| `{cell(node['node_id'])}` | `{cell(node['type_ref'])}` | {cell(node['label'])} | {cell(node['scope'])} |")
    lines += ["", "## Relations", "", "| ID | Type | Source | Target |", "| --- | --- | --- | --- |"]
    for relation in package["relations"]:
        lines.append(f"| `{cell(relation['relation_id'])}` | `{cell(relation['type_ref'])}` | `{cell(relation['source_node_id'])}` | `{cell(relation['target_node_id'])}` |")
    lines += ["", "## Residue", ""]
    if package["residue"]:
        for item in package["residue"]:
            lines.append(f"- `{item['residue_id']}` — {item['statement']} Owner: `{item['owner_route']}`; treatment: `{item['treatment']}`.")
    else:
        lines.append("- None.")
    lines += ["", "## Query contract", "", f"- Allowed operations: `{'`, `'.join(package['query_contract']['allowed_operations'])}`", f"- Unknown identity: `{package['query_contract']['unknown_identity_behavior']}`", f"- Filesystem reach: `{package['query_contract']['filesystem_reach']}`", "", "## Claim ceiling", "", package["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    artifact = json.loads((ROOT / "artifact.json").read_text(encoding="utf-8"))
    package = json.loads((ROOT / "fixtures/valid/ontology-package.json").read_text(encoding="utf-8"))
    (ROOT / "ARTIFACT.md").write_text(render_artifact(artifact), encoding="utf-8")
    (ROOT / "fixtures/valid/ONTOLOGY-PACKAGE.md").write_text(render_instance(package), encoding="utf-8")


if __name__ == "__main__":
    main()

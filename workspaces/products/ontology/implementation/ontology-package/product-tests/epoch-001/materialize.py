#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[5]
IMPORTED = LAB / "product/products/ontology/v1/product-ontology/source-package/imported"


def load(name: str) -> dict:
    return json.loads((IMPORTED / name).read_text(encoding="utf-8"))


def canonical(value: dict) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def build_source(profile: dict) -> dict:
    selection = profile["source_selection"]
    nodes = []
    for item in load("nodes.json")["nodes"]:
        nodes.append({
            "node_id": item["id"],
            "type_ref": f"cal.ontology-role.{item['role']}/v1",
            "label": item["label"],
            "definition_or_claim": item["claim"],
            "scope": item["scope"],
            "source_refs": item["source_refs"],
            "use_obligations": [
                f"Respect meaning owner: {item['owner_route']}.",
                f"Preserve candidate posture: {item['candidate_status']}.",
                item["forbidden_collapse"],
            ],
            "forbidden_collapse": [{
                "left_ref": item["id"],
                "right_ref": "implicit-canonical-collapse",
                "reason": item["forbidden_collapse"],
            }],
        })
    relations = []
    for item in load("relations.json")["relations"]:
        relations.append({
            "relation_id": item["id"],
            "type_ref": f"cal.ontology-relation.{item['type']}/v1",
            "source_node_id": item["source"],
            "target_node_id": item["target"],
            "source_refs": item["source_refs"],
            "forbidden_collapse": [{
                "left_ref": item["source"],
                "right_ref": item["target"],
                "reason": item["forbidden_collapse"],
            }],
        })
    residue = []
    for item in load("residue.json")["residue"]:
        residue.append({
            "residue_id": item["id"],
            "statement": f"{item['label']}: {item['description']}",
            "owner_route": item["owner_route"],
            "treatment": f"status={item['status']}; next_action={item['next_action']}",
        })
    return {
        "schema_version": "cyberalchemy-lab-ontology-source/v1",
        "source_id": selection["source_id"],
        "package_id": selection["package_id"],
        "package_version": selection["package_version"],
        "domain": selection["domain"],
        "owner_route": selection["owner_route"],
        "product_ref": profile["product_ref"],
        "product_output_ref": profile["product_output_ref"],
        "authority_effect": "none",
        "nodes": sorted(nodes, key=lambda item: item["node_id"]),
        "relations": sorted(relations, key=lambda item: item["relation_id"]),
        "residue": sorted(residue, key=lambda item: item["residue_id"]),
    }


def render_source(source: dict) -> str:
    lines = [
        "<!-- Generated from selected-source.json. Do not edit. -->", "",
        f"# Selected ontology source `{source['source_id']}`", "",
        f"- Package: `{source['package_id']}`",
        f"- Version: `{source['package_version']}`",
        f"- Domain: `{source['domain']}`",
        f"- Authority effect: `{source['authority_effect']}`",
        f"- Nodes: `{len(source['nodes'])}`",
        f"- Relations: `{len(source['relations'])}`",
        f"- Typed residue: `{len(source['residue'])}`", "",
        "This is a generated machine-contract selection over the imported canonical registries; it does not admit or rewrite their meaning.", "",
    ]
    return "\n".join(lines)


def main() -> None:
    profile = json.loads((ROOT / "test-profile.json").read_text(encoding="utf-8"))
    source = build_source(profile)
    (ROOT / "selected-source.json").write_text(canonical(source), encoding="utf-8")
    (ROOT / "SOURCE.md").write_text(render_source(source), encoding="utf-8")


if __name__ == "__main__":
    main()

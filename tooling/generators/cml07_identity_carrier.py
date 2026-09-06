#!/usr/bin/env python3
"""Render deterministic human projections from canonical CML-07 carriers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def bullets(values: list[str]) -> list[str]:
    return [f"- {value}" for value in values]


def common(data: dict[str, Any], title: str, identity_label: str, identity: str) -> list[str]:
    return [
        "<!-- GENERATED FILE: edit the adjacent canonical JSON and run the carrier generator. -->",
        "",
        f"# {title}",
        "",
        f"- {identity_label}: `{identity}`",
        f"- Version: `{data['version']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
    ]


def render_scope(lines: list[str], heading: str, scope: dict[str, list[str]]) -> None:
    lines.extend([f"## {heading}", "", "### Includes", "", *bullets(scope["includes"]), "", "### Excludes", "", *bullets(scope["excludes"]), ""])


def render(data: dict[str, Any]) -> str:
    kind = data["schema_version"]
    if kind == "cyberalchemy-lab-product-identity/v1":
        lines = common(data, data["name"], "Product", data["product_id"])
        lines.extend(["## Purpose", "", data["purpose"], ""])
        render_scope(lines, "Product scope", data["scope"])
        lines.extend(["## Identity boundaries", "", f"- Semantic owner: `{data['semantic_owner_ref']}`", f"- Lineage: `{data['lineage_ref']}`", f"- Challenge route: `{data['challenge_route']}`", ""])
    elif kind == "cyberalchemy-lab-project-identity/v1":
        lines = common(data, f"{data['name']} Project", "Project", data["project_id"])
        lines.extend(["## Purpose", "", data["purpose"], ""])
        render_scope(lines, "Coordination scope", data["coordination_scope"])
        lines.extend(["## Accountability", "", f"- Accountable owner: `{data['accountable_owner_ref']}`", f"- Challenge route: `{data['challenge_route']}`", ""])
    elif kind == "cyberalchemy-lab-method-binding/v1":
        lines = common(data, data["name"], "Binding", data["binding_id"])
        lines.extend(["## Binding", "", f"- Method: `{data['method_ref']}`", f"- Subject: `{data['subject_ref']}`", f"- Subject kind: `{data['subject_kind']}`", f"- Binding owner: `{data['binding_owner_ref']}`", ""])
        render_scope(lines, "Application scope", data["application_scope"])
    elif kind == "cyberalchemy-lab-goal/v1":
        lines = common(data, data["name"], "Goal", data["goal_id"])
        lines.extend(["## Outcome", "", data["outcome"], "", "## Rationale", "", data["rationale"], "", "## Success conditions", "", *bullets(data["success_conditions"]), "", "## Evidence requirements", "", *bullets(data["evidence_requirements"]), "", "## Accountability", "", f"- Accountable owner: `{data['accountable_owner_ref']}`", f"- Challenge route: `{data['challenge_route']}`", ""])
    elif kind == "cyberalchemy-lab-identity-lineage/v1":
        lines = common(data, data["name"], "Lineage", data["lineage_id"])
        lines.extend(["## Rename", "", f"- Kind: `{data['lineage_kind']}`", f"- Subject kind: `{data['subject_kind']}`", f"- Predecessor: `{data['predecessor_ref']}` — {data['predecessor_name']}", f"- Successor: `{data['successor_ref']}` — {data['successor_name']}", "", "## Preserved identity assertions", "", *bullets(data["preserved_identity_assertions"]), "", "## Changed attributes", "", *bullets(data["changed_attributes"]), "", "## Accountability", "", f"- Lineage owner: `{data['lineage_owner_ref']}`", f"- Challenge route: `{data['challenge_route']}`", ""])
    elif kind == "cyberalchemy-lab-identity-graph/v1":
        lines = common(data, data["name"], "Graph", data["graph_id"])
        lines.extend(["## Nodes", ""])
        lines.extend(f"- `{item['identity_ref']}` — `{item['identity_kind']}`" for item in data["nodes"])
        lines.extend(["", "## Relations", ""])
        lines.extend(f"- `{item['relation_id']}`: `{item['source_ref']}` — **{item['relation_kind']}** → `{item['target_ref']}`" for item in data["relations"])
        lines.extend(["", "## Accountability", "", f"- Graph owner: `{data['graph_owner_ref']}`", f"- Challenge route: `{data['challenge_route']}`", ""])
    else:
        raise ValueError(f"unsupported carrier schema_version: {kind}")

    lines.extend(["## Semantic definitions", "", *[f"- `{ref}`" for ref in data["semantic_definition_refs"]], ""])
    if "evidence_refs" in data:
        lines.extend(["## Evidence", "", *[f"- `{ref}`" for ref in data["evidence_refs"]], ""])
    lines.extend(["## Claim ceiling", "", data["claim_ceiling"], ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.source.read_text(encoding="utf-8"))
    expected = render(data)
    if args.check:
        if not args.target.is_file() or args.target.read_text(encoding="utf-8") != expected:
            print(f"PROJECTION=BLOCK target={args.target}")
            return 1
        print(f"PROJECTION=PASS target={args.target}")
        return 0
    args.target.parent.mkdir(parents=True, exist_ok=True)
    args.target.write_text(expected, encoding="utf-8")
    print(f"GENERATED={args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

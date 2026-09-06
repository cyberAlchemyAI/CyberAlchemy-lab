#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ONTOLOGY = Path(__file__).resolve().parent
ROOT = ONTOLOGY.parent
LAB = ROOT.parents[3]
FIXTURE_ROOT = ROOT / "tests/scaffold-non-authority"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def render_scaffold(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit scaffold.json and run build.py. -->",
        "",
        "# Craft Agent-Facing Ontology Scaffold — Epoch 001",
        "",
        "> Prototype navigation only. This scaffold is not semantic or operational authority.",
        "",
        f"- Scaffold: `{data['scaffold_id']}`",
        f"- Stage: `{data['stage_id']}`",
        f"- Lifecycle: `{data['lifecycle_posture']}`",
        f"- Canonicality: `{data['canonicality']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Definition nodes",
        "",
        "| Prototype definition | Term | Canonical object digest | Posture |",
        "| --- | --- | --- | --- |",
    ]
    for node in data["definition_nodes"]:
        lines.append(f"| `{node['definition_id']}` | {node['term']} | `{node['definition_sha256']}` | `{node['posture']}` |")
    lines += [
        "",
        "## Relation hints",
        "",
        "| Source | Hint | Target | Posture |",
        "| --- | --- | --- | --- |",
    ]
    for hint in data["relation_hints"]:
        lines.append(f"| `{hint['source_ref']}` | `{hint['relation_type']}` | `{hint['target_ref']}` | `{hint['posture']}` |")
    lines += [
        "",
        "## Selected sources",
        "",
        "| Dependency | Selector | Relevance | Drift effect | Digest |",
        "| --- | --- | --- | --- | --- |",
    ]
    for source in data["source_selector_index"]:
        lines.append(f"| `{source['dependency_id']}` | `{source['selector']}` | {source['relevance']} | `{source['drift_effect']}` | `{source['sha256']}` |")
    lines += ["", "## Challenge routes", ""]
    for route in data["challenge_route_index"]:
        lines += [
            f"### {route['challenge_id']}",
            "",
            f"- Condition: {route['condition']}",
            f"- Route: `{route['route']}`",
            f"- Outcome: {route['outcome']}",
            "",
        ]
    policy = data["dependency_drift_policy"]
    transition = data["stage_transition"]
    lines += [
        "## Dependency drift boundary",
        "",
        f"- Selected dependency drift: `{policy['selected_dependency_drift']}`",
        f"- Unselected ambient drift: `{policy['unselected_ambient_drift']}`",
        f"- Implicit dependency expansion: `{policy['implicit_dependency_expansion']}`",
        f"- Mandatory ontology runtime gate: `{str(policy['mandatory_ontology_runtime_gate']).lower()}`",
        "",
        "## Stage transition evidence",
        "",
        f"- Tested state: `{transition['tested_stage_state']}`",
        f"- Next stage: `{transition['next_stage_id']}`",
        f"- Next frontier candidate: `{transition['next_frontier_candidate']}`",
        f"- Effect: {transition['transition_effect']}",
        "",
        "## Claim ceiling",
        "",
        data["claim_ceiling"],
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_schema(schema: dict[str, Any]) -> str:
    required = ", ".join(f"`{field}`" for field in schema["required"])
    return "\n".join([
        "<!-- GENERATED FILE: edit scaffold.schema.json and run build.py. -->",
        "",
        "# Agent-Facing Ontology Scaffold Prototype Schema",
        "",
        "> Human projection of the machine schema; it is not a competing schema authority.",
        "",
        f"- Schema: `{schema['$id']}`",
        f"- Closed top-level object: `{schema.get('additionalProperties') is False}`",
        f"- Required fields: {required}",
        "",
        "Machine JSON remains canonical. This Markdown file is generated only.",
        "",
    ])


def hostile_failures(subject: dict[str, Any]) -> set[str]:
    failures: set[str] = set()
    if any([
        subject.get("canonicality") not in (None, "non-authoritative"),
        subject.get("authority_effect") not in (None, "none"),
        subject.get("lifecycle_posture") not in (None, "prototype-scaffold"),
    ]):
        failures.add("scaffold-zero-authority")
    if any(item.get("posture") != "prototype-hint" for item in subject.get("relation_hints", [])):
        failures.add("relation-hints-prototype-only")
    if any(len(item.get("definition_sha256", "")) != 64 for item in subject.get("definition_nodes", [])):
        failures.add("exact-definition-digest-closure")
    policy = subject.get("dependency_drift_policy", {})
    if policy.get("unselected_ambient_drift") not in (None, "diagnostic-only"):
        failures.add("unselected-ambient-drift-diagnostic-only")
    if policy.get("implicit_dependency_expansion") not in (None, "forbidden"):
        failures.add("selected-dependency-set-closed")
    return failures


def render_fixtures(fixtures: list[dict[str, Any]]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit fixture JSON and run ../../ontology/build.py. -->",
        "",
        "# CML08-P1 Scaffold Non-Authority Fixtures",
        "",
        "> Machine fixtures are canonical hostile inputs; this is their generated index.",
        "",
        "| Fixture | Expected rejection rule |",
        "| --- | --- |",
    ]
    for fixture in fixtures:
        lines.append(f"| `{fixture['fixture_id']}` | `{fixture['expected_rule']}` |")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    scaffold = load(ONTOLOGY / "scaffold.json")
    schema = load(ONTOLOGY / "scaffold.schema.json")
    fixture_paths = sorted(FIXTURE_ROOT.glob("*.json"))
    fixtures = [load(path) for path in fixture_paths]

    (ONTOLOGY / "SCAFFOLD.md").write_text(render_scaffold(scaffold), encoding="utf-8")
    (ONTOLOGY / "SCHEMA.md").write_text(render_schema(schema), encoding="utf-8")
    (FIXTURE_ROOT / "FIXTURES.md").write_text(render_fixtures(fixtures), encoding="utf-8")

    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    jsonschema.Draft202012Validator.check_schema(schema)
    schema_errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(scaffold)]
    check("scaffold-schema-valid", not schema_errors, schema_errors)

    binding = scaffold["definition_registry_binding"]
    definition_path = ROOT / binding["path"]
    p0_receipt_path = ROOT / binding["validation_receipt_path"]
    definitions = load(definition_path)
    p0_receipt = load(p0_receipt_path)
    check("p0-definition-registry-current", sha(definition_path) == binding["sha256"], {"expected": binding["sha256"], "actual": sha(definition_path)})
    check("p0-validation-receipt-current", sha(p0_receipt_path) == binding["validation_receipt_sha256"], {"expected": binding["validation_receipt_sha256"], "actual": sha(p0_receipt_path)})
    check("p0-stage-passed", p0_receipt.get("result") == binding["required_result"] and p0_receipt.get("required_stage_state") == binding["required_stage_state"], {"result": p0_receipt.get("result"), "stage_state": p0_receipt.get("required_stage_state")})

    preserved = []
    for item in scaffold["preserved_p0_materials"]:
        path = ROOT / item["path"]
        actual = sha(path)
        preserved.append({"path": item["path"], "expected": item["sha256"], "actual": actual, "current": actual == item["sha256"]})
    check("p0-materials-byte-preserved", all(item["current"] for item in preserved), preserved)

    expected_definitions = {item["definition_id"]: item for item in definitions["definitions"]}
    scaffold_nodes = {item["definition_id"]: item for item in scaffold["definition_nodes"]}
    check("exact-twelve-definition-nodes", len(scaffold["definition_nodes"]) == 12 and set(scaffold_nodes) == set(expected_definitions), sorted(scaffold_nodes))
    definition_closure = []
    for definition_id, definition in expected_definitions.items():
        expected = object_sha(definition)
        actual = scaffold_nodes.get(definition_id, {}).get("definition_sha256")
        definition_closure.append({"definition_id": definition_id, "expected": expected, "actual": actual, "current": expected == actual})
    check("exact-definition-digest-closure", all(item["current"] for item in definition_closure), definition_closure)

    node_ids = set(scaffold_nodes)
    relation_results = [
        {
            "source_ref": item["source_ref"],
            "target_ref": item["target_ref"],
            "endpoints_resolve": item["source_ref"] in node_ids and item["target_ref"] in node_ids,
            "prototype_hint": item["posture"] == "prototype-hint",
        }
        for item in scaffold["relation_hints"]
    ]
    check("relation-endpoint-closure", all(item["endpoints_resolve"] for item in relation_results), relation_results)
    check("relation-hints-prototype-only", all(item["prototype_hint"] for item in relation_results), relation_results)
    related_nodes = {item["source_ref"] for item in scaffold["relation_hints"]} | {item["target_ref"] for item in scaffold["relation_hints"]}
    check("all-definition-nodes-navigable", related_nodes == node_ids, sorted(node_ids - related_nodes))

    source_results = []
    for item in scaffold["source_selector_index"]:
        path = Path(item["repository"]) / item["path"]
        actual = sha(path) if path.is_file() else None
        source_results.append({"dependency_id": item["dependency_id"], "selector": item["selector"], "expected": item["sha256"], "actual": actual, "current": actual == item["sha256"]})
    check("selected-source-selector-currentness", all(item["current"] for item in source_results), source_results)
    check("selected-dependency-set-closed", scaffold["dependency_drift_policy"]["implicit_dependency_expansion"] == "forbidden", scaffold["dependency_drift_policy"])
    check("unselected-ambient-drift-diagnostic-only", scaffold["dependency_drift_policy"]["unselected_ambient_drift"] == "diagnostic-only" and scaffold["dependency_drift_policy"]["mandatory_ontology_runtime_gate"] is False, scaffold["dependency_drift_policy"])

    challenge_ids = {item["challenge_id"] for item in scaffold["challenge_route_index"]}
    required_challenges = {
        "CAL-P1-CHALLENGE-DEFINITION-DIGEST",
        "CAL-P1-CHALLENGE-SELECTED-SOURCE-DRIFT",
        "CAL-P1-CHALLENGE-AUTHORITY-COLLAPSE",
        "CAL-P1-CHALLENGE-AMBIENT-DRIFT",
        "CAL-P1-CHALLENGE-P2-SELECTIONS",
    }
    check("challenge-route-coverage", challenge_ids == required_challenges, sorted(challenge_ids))
    check("scaffold-zero-authority", scaffold["canonicality"] == "non-authoritative" and scaffold["authority_effect"] == "none" and scaffold["lifecycle_posture"] == "prototype-scaffold", {"canonicality": scaffold["canonicality"], "authority_effect": scaffold["authority_effect"], "lifecycle_posture": scaffold["lifecycle_posture"]})

    fixture_results = []
    for fixture in fixtures:
        failures = hostile_failures(fixture["subject"])
        fixture_results.append({"fixture_id": fixture["fixture_id"], "expected_rule": fixture["expected_rule"], "failures": sorted(failures), "rejected": fixture["expected_rule"] in failures})
    expected_rules = {
        "scaffold-zero-authority",
        "relation-hints-prototype-only",
        "exact-definition-digest-closure",
        "unselected-ambient-drift-diagnostic-only",
        "selected-dependency-set-closed",
    }
    check("five-hostile-fixtures-rejected", len(fixture_results) == 5 and all(item["rejected"] for item in fixture_results), fixture_results)
    check("hostile-rule-coverage", {item["expected_rule"] for item in fixture_results} == expected_rules, fixture_results)

    check("scaffold-projection-parity", (ONTOLOGY / "SCAFFOLD.md").read_text(encoding="utf-8") == render_scaffold(scaffold), sha(ONTOLOGY / "SCAFFOLD.md"))
    check("schema-projection-parity", (ONTOLOGY / "SCHEMA.md").read_text(encoding="utf-8") == render_schema(schema), sha(ONTOLOGY / "SCHEMA.md"))
    check("fixture-projection-parity", (FIXTURE_ROOT / "FIXTURES.md").read_text(encoding="utf-8") == render_fixtures(fixtures), sha(FIXTURE_ROOT / "FIXTURES.md"))

    failed = [item for item in checks if item["result"] == "FAIL"]
    result = "PASS" if not failed else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-prototype-stage-validation/v1",
        "subject": scaffold["scaffold_id"],
        "stage_id": scaffold["stage_id"],
        "result": result,
        "required_stage_state": "TESTED_PROTOTYPE" if result == "PASS" else "NOT_EVALUABLE",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {
            "scaffold_sha256": sha(ONTOLOGY / "scaffold.json"),
            "schema_sha256": sha(ONTOLOGY / "scaffold.schema.json"),
            "fixture_sha256": {path.name: sha(path) for path in fixture_paths},
            "projection_sha256": {
                "SCAFFOLD.md": sha(ONTOLOGY / "SCAFFOLD.md"),
                "SCHEMA.md": sha(ONTOLOGY / "SCHEMA.md"),
                "FIXTURES.md": sha(FIXTURE_ROOT / "FIXTURES.md"),
            },
        },
        "product_construction_frontier": {
            "completed_evidence_stage": "ontology_scaffolds" if result == "PASS" else "definition_prototypes",
            "next_frontier_candidate": "product_business_domainspec_compiled_system_implementation_prototypes" if result == "PASS" else "ontology_scaffolds",
            "next_stage_id": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE" if result == "PASS" else "CML08-P1-AUTHOR-AGENT-ONTOLOGY-SCAFFOLD",
            "continuation_status": "runnable-with-p2-construction-choices" if result == "PASS" else "blocked-by-p1-validation",
            "current_causal_blockers": [],
            "future_frontier_prerequisites": [
                {"prerequisite_id": "CAL-CML09-PREREQ-CAPABILITY-IDENTITY", "state": "unresolved-p2-choice", "owner": "role:craft-project-owner"},
                {"prerequisite_id": "CAL-CML09-PREREQ-CONTEXT-PLACEMENT", "state": "unresolved-p2-choice", "owner": "role:craft-project-owner"},
                {"prerequisite_id": "CAL-CML09-PREREQ-SOURCE-CLOSURE", "state": "unresolved-p2-choice", "owner": "role:craft-project-owner"},
            ],
        },
        "operational_support": [
            {"task_id": "CAL-OP-TRACK-P1-IN-GIT", "state": "deferred", "owner_route": "CA2-ROUTE-PUBLISH", "applies_to_stage": None, "blocking_basis": "none"},
            {"task_id": "CAL-OP-SCAFFOLD-PROMOTION", "state": "outside-prototype-construction", "owner_route": "CA2-ROUTE-GOVERNANCE", "applies_to_stage": None, "blocking_basis": "none"},
        ],
        "claim_ceiling": "PASS establishes TESTED_PROTOTYPE evidence only for the exact P1 scaffold, schema, generated projections, selected dependency closure, prototype relation hints, challenge routes, and hostile non-authority fixtures. It does not admit ontology, activate a runtime gate, select or implement the P2 product, approve a product, or grant operational authority.",
    }
    dump(ONTOLOGY / "receipts/validation.json", receipt)
    print(f"CML08_P1_AGENT_ONTOLOGY_SCAFFOLD={result}")
    print(f"STAGE_STATE={receipt['required_stage_state']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"NEXT_STAGE={receipt['product_construction_frontier']['next_stage_id']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

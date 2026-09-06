#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SOURCE = Path("/home/vrondelli/projects/domainspec-core")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def heading_bytes(path: Path, heading: str) -> bytes:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    selected: list[str] = []
    active = False
    for line in lines:
        if line.startswith("## "):
            if active:
                break
            active = line.rstrip("\n") == heading
        if active:
            selected.append(line)
    if not selected:
        raise ValueError(f"heading not found: {heading}")
    return "".join(selected).encode("utf-8")


def render_prototype(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit prototype.json and run build.py. -->",
        "",
        "# Craft First Capability Definition Prototype Epoch 001",
        "",
        "> Non-authoritative product-construction prototype.",
        "",
        f"- Prototype: `{data['prototype_id']}`",
        f"- Stage: `{data['stage_id']}`",
        f"- State: `{data['state']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Selected dependencies",
        "",
        "| Dependency | Posture | Selector | Digest |",
        "| --- | --- | --- | --- |",
    ]
    for item in data["selected_dependencies"]:
        lines.append(f"| `{item['dependency_id']}` | `{item['posture']}` | `{item['selector']}` | `{item['sha256']}` |")
    transition = data["stage_transition"]
    lines += [
        "",
        "## Stage transition evidence",
        "",
        f"- From frontier: `{transition['from_frontier']}`",
        f"- Tested state: `{transition['tested_stage_state']}`",
        f"- Next frontier candidate: `{transition['next_frontier_candidate']}`",
        f"- Effect: {transition['transition_effect']}",
        "",
        "## Claim ceiling",
        "",
        data["claim_ceiling"],
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_definitions(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit definitions.json and run ../build.py. -->",
        "",
        "# Craft First Capability Definition Prototypes",
        "",
        "> Prototype meanings for construction and testing; not the Lab authority registry.",
        "",
        f"- Registry: `{data['registry_id']}`",
        f"- Status: `{data['status']}`",
        f"- Canonicality: `{data['canonicality']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Index",
        "",
        "| ID | Term | Version |",
        "| --- | --- | --- |",
    ]
    for item in data["definitions"]:
        lines.append(f"| `{item['definition_id']}` | {item['term']} | `{item['version']}` |")
    for item in data["definitions"]:
        formal = item["voices"]["scientific_formal"]
        lines += [
            "",
            f"## {item['term']}",
            "",
            f"- ID: `{item['definition_id']}`",
            f"- Classification: `{item['classification']}`",
            f"- Lifecycle: `{item['lifecycle_posture']}`",
            f"- Authority effect: `{item['authority_effect']}`",
            "",
            "### Scientific/formal voice",
            "",
            formal["normative_statement"],
            "",
            "```text",
            formal["formal_expression"],
            "```",
            "",
            "Notation:",
            "",
        ]
        lines += [f"- `{n['symbol']}` — {n['meaning']}" for n in formal["notation"]]
        lines += ["", "Testable conditions:", ""] + [f"- {value}" for value in formal["testable_conditions"]]
        lines += [
            "",
            "### Plain-language voice",
            "",
            item["voices"]["plain_language"]["explanation"],
            "",
            "### CyberAlchemy Lab context",
            "",
            item["voices"]["domain_context"]["explanation"],
            "",
            "### Boundaries",
            "",
        ]
        lines += [f"- {value}" for value in item["boundaries"]]
        lines += ["", "### Four facets", ""]
        for key, value in item["four_facets"].items():
            rendered = ", ".join(value) if isinstance(value, list) else value
            lines.append(f"- **{key.replace('_', ' ').title()}** — {rendered}")
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def render_drift(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit drift-audit.json and run ../build.py. -->",
        "",
        "# CML08-P0 Prototype Definition Drift Audit",
        "",
        "> Prototype audit only; no semantic promotion.",
        "",
        "## Summary",
        "",
    ]
    for key, value in data["summary"].items():
        lines.append(f"- {key.replace('_', ' ').title()}: `{value}`")
    lines += ["", "## Findings", ""]
    for item in data["findings"]:
        lines += [
            f"### {item['finding_id']} — {item['state']}",
            "",
            f"Target: `{item['target']}`",
            "",
            item["condition"],
            "",
            f"Remediation: {item['remediation']}",
            "",
        ]
    lines += ["## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def render_schema(data: dict[str, Any]) -> str:
    defs = data["$defs"]
    lines = [
        "<!-- GENERATED FILE: edit prototype-artifacts.schema.json and run ../build.py. -->",
        "",
        "# Prototype Artifact Machine Contracts",
        "",
        "> Human projection of the P0 machine schema.",
        "",
        f"- Schema: `{data['$id']}`",
        "",
        "| Contract | Required fields | Closed |",
        "| --- | --- | --- |",
    ]
    for name in ("prototypeDefinition", "prototypeDefinitionRegistry", "prototypePackage"):
        item = defs[name]
        required = ", ".join(f"`{field}`" for field in item["required"])
        lines.append(f"| `{name}` | {required} | `{item.get('additionalProperties') is False}` |")
    lines += [
        "",
        "## Direction",
        "",
        "Machine JSON is canonical inside this prototype epoch. Markdown views are generated only and cannot redefine the records.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def hostile_failures(subject: dict[str, Any]) -> set[str]:
    failures: set[str] = set()
    if subject.get("product_feature_id") and subject.get("product_feature_id") == subject.get("product_capability_id"):
        failures.add("product-feature-product-capability-distinct")
    if subject.get("product_capability_id") and subject.get("product_capability_id") == subject.get("capability_instance_id"):
        failures.add("product-capability-instance-distinct")
    if subject.get("context_identity_source") == "directory-placement" or subject.get("semantic_scope_present") is False or subject.get("language_ref_present") is False:
        failures.add("bounded-context-not-inferred-from-directory")
    if subject.get("kind") == "agent-ontology-scaffold" and (subject.get("canonicality") != "non-authoritative" or subject.get("authority_effect") != "none"):
        failures.add("ontology-scaffold-non-authoritative")
    if subject.get("validation_result") == "PASS" and subject.get("product_test_result") == "PASS" and set(subject.get("executed_product_test_ids", [])) != set(subject.get("required_product_test_ids", [])):
        failures.add("validation-pass-not-product-test-pass")
    if subject.get("kind") == "product-approval" and (subject.get("authority_effect") != "product-approval-only" or subject.get("grants_operational_authority") is True):
        failures.add("product-approval-no-operational-authority")
    return failures


def render_fixtures(fixtures: list[dict[str, Any]]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit fixture JSON and run ../../build.py. -->",
        "",
        "# CML08-P0 Semantic Hostile Fixtures",
        "",
        "> Machine fixtures are canonical test inputs; this is their generated human projection.",
        "",
        "| Fixture | Expected rejection rule |",
        "| --- | --- |",
    ]
    for item in fixtures:
        lines.append(f"| `{item['fixture_id']}` | `{item['expected_rule']}` |")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    prototype = load(ROOT / "prototype.json")
    definitions = load(ROOT / "definitions/definitions.json")
    drift = load(ROOT / "definitions/drift-audit.json")
    schema = load(ROOT / "schemas/prototype-artifacts.schema.json")
    fixture_paths = sorted((ROOT / "tests/semantic-hostile-fixtures").glob("*.json"))
    fixtures = [load(path) for path in fixture_paths]

    (ROOT / "PROTOTYPE.md").write_text(render_prototype(prototype), encoding="utf-8")
    (ROOT / "definitions/DEFINITIONS.md").write_text(render_definitions(definitions), encoding="utf-8")
    (ROOT / "definitions/DEFINITION-DRIFT-AUDIT.md").write_text(render_drift(drift), encoding="utf-8")
    (ROOT / "schemas/PROTOTYPE-ARTIFACTS.md").write_text(render_schema(schema), encoding="utf-8")
    (ROOT / "tests/semantic-hostile-fixtures/FIXTURES.md").write_text(render_fixtures(fixtures), encoding="utf-8")

    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    jsonschema.Draft202012Validator.check_schema(schema)
    package_schema = {"$schema": schema["$schema"], "$ref": "#/$defs/prototypePackage", "$defs": schema["$defs"]}
    registry_schema = {"$schema": schema["$schema"], "$ref": "#/$defs/prototypeDefinitionRegistry", "$defs": schema["$defs"]}
    package_errors = [error.message for error in jsonschema.Draft202012Validator(package_schema).iter_errors(prototype)]
    registry_errors = [error.message for error in jsonschema.Draft202012Validator(registry_schema).iter_errors(definitions)]
    check("prototype-package-schema-valid", not package_errors, package_errors)
    check("definition-registry-schema-valid", not registry_errors, registry_errors)
    chain_binding = prototype["chain_binding"]
    check(
        "successor-chain-current",
        sha(LAB / chain_binding["path"]) == chain_binding["sha256"],
        {"expected": chain_binding["sha256"], "actual": sha(LAB / chain_binding["path"])},
    )

    expected_ids = {
        "cal.prototype.definition.definition-prototype",
        "cal.prototype.definition.agent-ontology-scaffold",
        "cal.prototype.definition.product-capability-prototype",
        "cal.prototype.definition.business-ontology-prototype",
        "cal.prototype.definition.domainspec-source-prototype",
        "cal.prototype.definition.compiled-graph-prototype",
        "cal.prototype.definition.system-ontology-prototype",
        "cal.prototype.definition.implementation-prototype",
        "cal.prototype.definition.testable-product-candidate",
        "cal.prototype.definition.product-test-evidence",
        "cal.prototype.definition.product-approval",
        "cal.prototype.definition.post-approval-authority-decision",
    }
    ids = [item["definition_id"] for item in definitions["definitions"]]
    check("exact-twelve-definition-prototypes", set(ids) == expected_ids and len(ids) == len(set(ids)) == 12, ids)
    check("all-prototype-zero-authority", definitions["canonicality"] == "non-authoritative" and definitions["authority_effect"] == "none" and all(item["authority_effect"] == "none" for item in definitions["definitions"]), ids)
    check("three-voice-contract", all(item["voices"]["plain_language"]["normative"] is False and item["voices"]["domain_context"]["normative"] is False and item["voices"]["scientific_formal"]["normative_statement"] for item in definitions["definitions"]), ids)
    check("four-facet-contract", all(set(item["four_facets"]) == {"classification", "schema", "human_projection", "machine_checkable"} for item in definitions["definitions"]), ids)

    source_results = []
    for item in prototype["selected_dependencies"]:
        base = Path(item["repository"])
        path = base / item["path"]
        if item["selector"].startswith("heading:"):
            actual = hashlib.sha256(heading_bytes(path, item["selector"].removeprefix("heading:"))).hexdigest()
        else:
            actual = sha(path)
        source_results.append({"dependency_id": item["dependency_id"], "expected": item["sha256"], "actual": actual, "current": actual == item["sha256"]})
    check("selected-dependencies-current", all(item["current"] for item in source_results), source_results)

    live_registry = load(LAB / "authority/definitions/registry.json")
    live_ids = {item["definition_id"] for item in live_registry.get("entries", [])}
    collisions = sorted(expected_ids & live_ids)
    check("no-live-authority-registry-collisions", not collisions, collisions)
    check("live-authority-registry-unmodified", sha(LAB / "authority/definitions/registry.json") == "59c9fc6b5e76f828e655ee72c065a6c2ffb524ba592ec4f0f225a889ab4cfd45", sha(LAB / "authority/definitions/registry.json"))

    source_binding_ids = {item["source_ref"] for item in definitions["source_bindings"]}
    definition_source_results = [{"definition_id": item["definition_id"], "closed": set(item["source_refs"]) <= source_binding_ids} for item in definitions["definitions"]]
    check("definition-source-reference-closure", all(item["closed"] for item in definition_source_results), definition_source_results)

    fixture_results = []
    for fixture in fixtures:
        failures = hostile_failures(fixture["subject"])
        fixture_results.append({"fixture_id": fixture["fixture_id"], "expected_rule": fixture["expected_rule"], "failures": sorted(failures), "rejected": fixture["expected_rule"] in failures})
    check("six-hostile-fixtures-rejected", len(fixture_results) == 6 and all(item["rejected"] for item in fixture_results), fixture_results)
    expected_rules = {
        "product-feature-product-capability-distinct",
        "product-capability-instance-distinct",
        "bounded-context-not-inferred-from-directory",
        "ontology-scaffold-non-authoritative",
        "validation-pass-not-product-test-pass",
        "product-approval-no-operational-authority",
    }
    check("hostile-rule-coverage", {item["expected_rule"] for item in fixture_results} == expected_rules, fixture_results)

    check("prototype-projection-parity", (ROOT / "PROTOTYPE.md").read_text(encoding="utf-8") == render_prototype(prototype), sha(ROOT / "PROTOTYPE.md"))
    check("definition-projection-parity", (ROOT / "definitions/DEFINITIONS.md").read_text(encoding="utf-8") == render_definitions(definitions), sha(ROOT / "definitions/DEFINITIONS.md"))
    check("drift-projection-parity", (ROOT / "definitions/DEFINITION-DRIFT-AUDIT.md").read_text(encoding="utf-8") == render_drift(drift), sha(ROOT / "definitions/DEFINITION-DRIFT-AUDIT.md"))
    check("schema-projection-parity", (ROOT / "schemas/PROTOTYPE-ARTIFACTS.md").read_text(encoding="utf-8") == render_schema(schema), sha(ROOT / "schemas/PROTOTYPE-ARTIFACTS.md"))
    check("fixture-projection-parity", (ROOT / "tests/semantic-hostile-fixtures/FIXTURES.md").read_text(encoding="utf-8") == render_fixtures(fixtures), sha(ROOT / "tests/semantic-hostile-fixtures/FIXTURES.md"))

    check("drift-audit-counts-current", drift["summary"]["prototype_definition_count"] == 12 and drift["summary"]["live_registry_collisions"] == len(collisions), drift["summary"])
    check("p1-not-implemented", drift["findings"][-1]["state"] == "future-consumer-not-yet-authored", drift["findings"][-1])

    failed = [item for item in checks if item["result"] == "FAIL"]
    result = "PASS" if not failed else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-prototype-stage-validation/v1",
        "subject": prototype["prototype_id"],
        "stage_id": prototype["stage_id"],
        "result": result,
        "required_stage_state": "TESTED_PROTOTYPE" if result == "PASS" else "NOT_EVALUABLE",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {
            "prototype_sha256": sha(ROOT / "prototype.json"),
            "definition_registry_sha256": sha(ROOT / "definitions/definitions.json"),
            "schema_sha256": sha(ROOT / "schemas/prototype-artifacts.schema.json"),
            "drift_audit_sha256": sha(ROOT / "definitions/drift-audit.json"),
            "fixture_sha256": {path.name: sha(path) for path in fixture_paths},
            "projection_sha256": {
                "PROTOTYPE.md": sha(ROOT / "PROTOTYPE.md"),
                "DEFINITIONS.md": sha(ROOT / "definitions/DEFINITIONS.md"),
                "DEFINITION-DRIFT-AUDIT.md": sha(ROOT / "definitions/DEFINITION-DRIFT-AUDIT.md"),
                "PROTOTYPE-ARTIFACTS.md": sha(ROOT / "schemas/PROTOTYPE-ARTIFACTS.md"),
                "FIXTURES.md": sha(ROOT / "tests/semantic-hostile-fixtures/FIXTURES.md"),
            },
        },
        "product_construction_frontier": {
            "completed_evidence_stage": "definition_prototypes" if result == "PASS" else None,
            "next_frontier_candidate": "ontology_scaffolds" if result == "PASS" else "definition_prototypes",
            "continuation_status": "runnable" if result == "PASS" else "blocked-by-p0-validation",
        },
        "operational_support": [
            {"task_id": "CAL-OP-TRACK-P0-IN-GIT", "state": "deferred", "owner_route": "CA2-ROUTE-PUBLISH", "applies_to_stage": None, "blocking_basis": "none"},
            {"task_id": "CAL-OP-DEFINITION-PROMOTION", "state": "outside-prototype-construction", "owner_route": "CA2-ROUTE-DEFINITIONS", "applies_to_stage": None, "blocking_basis": "none"},
        ],
        "claim_ceiling": "PASS establishes TESTED_PROTOTYPE evidence only for the exact P0 machine records, three-voice prototype meanings, schema, selected dependencies, deterministic human projections, and hostile non-collapse fixtures. It does not admit or canonize meaning, implement the P1 scaffold or P2 product, approve a product, or grant operational authority.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"CML08_P0_DEFINITION_PROTOTYPES={result}")
    print(f"STAGE_STATE={receipt['required_stage_state']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"NEXT_FRONTIER={receipt['product_construction_frontier']['next_frontier_candidate']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

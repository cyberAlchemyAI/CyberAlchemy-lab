#!/usr/bin/env python3
"""Shared deterministic validator for orthogonal CML-07 identity Artifact Types."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import jsonschema

LAB = Path(__file__).resolve().parents[2]
REGISTRY = LAB / "authority/definitions/registry.json"
DECISION = LAB / "docs/decisions/0029-cml07-semantic-foundation-v1/decision.json"
ROOT_TYPE = LAB / "authority/artifact-types/artifact-type/v2/artifact.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_errors(kind: str, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if kind == "identity-graph":
        nodes = data.get("nodes", [])
        node_kinds: dict[str, str] = {}
        for node in nodes:
            ref = node.get("identity_ref")
            if ref in node_kinds:
                errors.append(f"duplicate or collapsed node identity: {ref}")
            node_kinds[ref] = node.get("identity_kind")
        signatures = {
            "contains_product": ("product", "product"),
            "coordinated_by": ("product", "project"),
            "embodies_method": ("product", "method"),
            "uses_method": ("project", "method"),
            "pursues_goal": ("project", "goal"),
        }
        relation_ids = set()
        for relation in data.get("relations", []):
            relation_id = relation.get("relation_id")
            if relation_id in relation_ids:
                errors.append(f"duplicate relation identity: {relation_id}")
            relation_ids.add(relation_id)
            source = relation.get("source_ref")
            target = relation.get("target_ref")
            if source not in node_kinds or target not in node_kinds:
                errors.append(f"unresolved relation endpoint: {source} -> {target}")
                continue
            expected = signatures.get(relation.get("relation_kind"))
            observed = (node_kinds[source], node_kinds[target])
            if expected != observed:
                errors.append(f"invalid relation signature: {relation.get('relation_kind')} {observed}")
    elif kind == "method-binding":
        if data.get("binding_id") in {data.get("method_ref"), data.get("subject_ref")}:
            errors.append("binding identity collapses into an endpoint identity")
        if data.get("method_ref") == data.get("subject_ref"):
            errors.append("method endpoint collapses into subject endpoint")
    elif kind == "identity-lineage":
        if data.get("lineage_id") in {data.get("predecessor_ref"), data.get("successor_ref")}:
            errors.append("lineage identity collapses into an endpoint identity")
    return errors


def materialize_hostile_fixture(root: Path, fixture: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if fixture.get("fixture_kind") != "mutation-v1":
        return fixture, "any"
    data = deepcopy(load(root / fixture["base_path"]))
    for mutation in fixture["mutations"]:
        parts = [part for part in mutation["path"].split("/") if part]
        target: Any = data
        for part in parts[:-1]:
            target = target[int(part)] if isinstance(target, list) else target[part]
        leaf = parts[-1]
        if mutation["op"] == "remove":
            if isinstance(target, list):
                target.pop(int(leaf))
            else:
                target.pop(leaf)
        elif mutation["op"] in {"add", "replace"}:
            value = mutation["value"]
            if isinstance(target, list):
                if leaf == "-":
                    target.append(value)
                elif mutation["op"] == "add":
                    target.insert(int(leaf), value)
                else:
                    target[int(leaf)] = value
            else:
                target[leaf] = value
        else:
            raise ValueError(f"unsupported hostile mutation: {mutation['op']}")
    return data, fixture["expected_rejection"]


def run(root: Path, kind: str) -> int:
    artifact = load(root / "artifact.json")
    schema = load(root / "schema.json")
    valid_path = root / artifact["validation_contract"]["positive_witness"]
    valid = load(valid_path)
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    required_artifact_fields = {
        "schema_version", "artifact_type_id", "artifact_type_ref", "version", "name", "status", "authority_effect",
        "classification", "artifact_type_root_binding", "semantic_owner_ref", "semantic_definition_refs",
        "semantic_definition_bindings", "schema_ref", "schema_digest", "instance_contract", "distinct_validation_purpose",
        "orthogonality_rules", "source_direction", "four_facets", "validation_contract", "typed_residue", "claim_ceiling",
    }
    check("artifact-contract-complete", set(artifact) == required_artifact_fields, sorted(set(artifact) ^ required_artifact_fields))
    check("candidate-has-no-authority-effect", artifact.get("status") == "candidate-unadmitted" and artifact.get("authority_effect") == "none", {"status": artifact.get("status"), "authority_effect": artifact.get("authority_effect")})
    check("artifact-type-v2-classification", artifact.get("classification", {}).get("artifact_type_ref") == "cal.artifact-type.artifact-type/v2", artifact.get("classification"))

    decision = load(DECISION)
    root_binding = artifact["artifact_type_root_binding"]
    check("admitted-artifact-type-v2-bound", root_binding["path"] == str(ROOT_TYPE.relative_to(LAB)) and root_binding["sha256"] == sha(ROOT_TYPE) and root_binding["admission_decision_ref"] == decision["decision_id"] and decision["admitted_artifact_type"]["sha256"] == sha(ROOT_TYPE), root_binding)
    check("schema-digest-current", artifact["schema_digest"] == sha(root / "schema.json"), {"declared": artifact["schema_digest"], "actual": sha(root / "schema.json")})
    check("closed-top-level-schema", schema.get("additionalProperties") is False and schema.get("type") == "object", {"additionalProperties": schema.get("additionalProperties")})

    registry = load(REGISTRY)
    registry_entries = {f"{x['definition_id']}@{x['version']}": x for x in registry["entries"] if x.get("lifecycle_state") == "admitted"}
    refs = set(artifact["semantic_definition_refs"])
    bindings = {x["definition_ref"]: x for x in artifact["semantic_definition_bindings"]}
    check("semantic-definition-ref-closure", refs == set(bindings), {"refs": sorted(refs), "bindings": sorted(bindings)})
    binding_results = []
    for ref, binding in bindings.items():
        entry = registry_entries.get(ref)
        path = LAB / binding["path"]
        ok = bool(entry) and path.is_file() and sha(path) == binding["sha256"] == entry["sha256"] and binding["admission_posture"] == "admitted" and binding["admission_decision_ref"] == decision["decision_id"]
        binding_results.append({"definition_ref": ref, "ok": ok, "actual": sha(path) if path.is_file() else "missing"})
    check("semantic-definitions-admitted-current", bool(binding_results) and all(x["ok"] for x in binding_results), binding_results)

    schema_errors = sorted(error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(valid))
    custom_errors = semantic_errors(kind, valid)
    check("positive-witness-schema-valid", not schema_errors, schema_errors)
    check("positive-witness-semantically-valid", not custom_errors, custom_errors)
    check("explicit-instance-identity", bool(valid.get(artifact["instance_contract"]["identity_field"])), artifact["instance_contract"]["identity_field"])

    generator_binding = artifact["source_direction"]
    shared_generator = LAB / generator_binding["shared_generator_path"]
    check("shared-generator-current", shared_generator.is_file() and sha(shared_generator) == generator_binding["shared_generator_sha256"], {"declared": generator_binding["shared_generator_sha256"], "actual": sha(shared_generator) if shared_generator.is_file() else "missing"})
    spec = importlib.util.spec_from_file_location("cml07_identity_generator", shared_generator)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    artifact_md = root / "ARTIFACT.md"
    fixture_md = root / artifact["validation_contract"]["positive_projection"]
    check("artifact-projection-parity", artifact_md.is_file() and artifact_md.read_text(encoding="utf-8") == module.render_artifact(artifact), sha(artifact_md) if artifact_md.is_file() else "missing")
    check("fixture-projection-parity", fixture_md.is_file() and fixture_md.read_text(encoding="utf-8") == module.render_instance(artifact, valid), sha(fixture_md) if fixture_md.is_file() else "missing")

    validator_contract = artifact["validation_contract"]
    validator_path = LAB / validator_contract["shared_validator_path"]
    check("shared-validator-current", validator_path.resolve() == Path(__file__).resolve() and validator_contract["shared_validator_sha256"] == sha(validator_path), {"declared": validator_contract["shared_validator_sha256"], "actual": sha(validator_path)})

    negative_results = []
    for relative in artifact["validation_contract"]["negative_witnesses"]:
        path = root / relative
        data, expected_rejection = materialize_hostile_fixture(root, load(path))
        schema_failures = sorted(error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(data))
        semantic_failures = semantic_errors(kind, data)
        expected_seen = bool(schema_failures) if expected_rejection == "schema" else bool(semantic_failures) if expected_rejection == "semantic" else bool(schema_failures or semantic_failures)
        errors = schema_failures + semantic_failures
        negative_results.append({"path": relative, "rejected": bool(errors), "expected_rejection": expected_rejection, "expected_seen": expected_seen, "errors": errors})
    check("hostile-fixtures-rejected", bool(negative_results) and all(x["rejected"] and x["expected_seen"] for x in negative_results), negative_results)
    check("schema-conformance-separated-from-admission", artifact["validation_contract"]["assessment_scope"] == "schema-and-artifact-type-contract" and artifact["validation_contract"]["admission_effect"] == "none", artifact["validation_contract"])

    blocked = [x for x in checks if x["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-cml07-identity-artifact-type-validation/v1",
        "subject": artifact["artifact_type_ref"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "none",
        "assessment": {
            "validation_result": "PASS" if not blocked else "BLOCK",
            "schema_conformance": "PASS" if not blocked else "NOT_ESTABLISHED",
            "admission_posture": "candidate-unadmitted",
            "implementation_conformance": "not_evaluable",
            "runtime_conformance": "not_evaluable",
        },
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "materials": {
            "artifact_sha256": sha(root / "artifact.json"),
            "schema_sha256": sha(root / "schema.json"),
            "artifact_projection_sha256": sha(artifact_md) if artifact_md.is_file() else None,
            "positive_witness_sha256": sha(valid_path),
            "positive_projection_sha256": sha(fixture_md) if fixture_md.is_file() else None,
        },
        "claim_ceiling": "PASS establishes candidate schema-and-artifact-type-contract conformance for the exact fixture and package only. It does not admit the Artifact Type, validate a future Craft identity instance, establish identity-contract, implementation, or runtime conformance, or grant authority.",
    }
    receipt_path = root / "receipts/validation.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{artifact['artifact_type_id'].upper().replace('.', '_').replace('-', '_')}_VALIDATION={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if not blocked else 1

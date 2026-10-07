#!/usr/bin/env python3
"""Validate a closed endpoint carrier candidate against the relation model."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import jsonschema


LAB = Path(__file__).resolve().parents[2]
ROOT_TYPE = LAB / "authority/artifact-types/artifact-type/v2/artifact.json"
DEFINITIONS = LAB / "authority/definitions/registry.json"
RELATION_MODEL = LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json"
GENERATOR = LAB / "tooling/generators/endpoint_carrier.py"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def expected_roles(kind: str, model: dict) -> list[dict]:
    roles = []
    for relation in model["entries"]:
        sources = sorted({pair["target_kind"] for pair in relation["allowed_endpoint_pairs"] if pair["source_kind"] == kind})
        targets = sorted({pair["source_kind"] for pair in relation["allowed_endpoint_pairs"] if pair["target_kind"] == kind})
        if sources:
            roles.append({"relation_kind_ref": relation["relation_kind_id"], "direction": "source", "counterpart_kinds": sources})
        if targets:
            roles.append({"relation_kind_ref": relation["relation_kind_id"], "direction": "target", "counterpart_kinds": targets})
    return sorted(roles, key=lambda item: (item["relation_kind_ref"], item["direction"]))


def validate_package(root: Path) -> int:
    artifact = load(root / "artifact.json")
    schema = load(root / "schema.json")
    witness = load(root / artifact["validation_contract"]["positive_witness"])
    definitions = load(DEFINITIONS)
    model = load(RELATION_MODEL)
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    modern = {"semantic_owner_ref", "semantic_definition_refs", "instance_contract", "distinct_validation_purpose", "orthogonality_rules", "source_direction", "four_facets", "validation_contract", "typed_residue", "claim_ceiling", "allowed_relation_kinds", "relation_roles", "hostile_non_collapse"}
    check("modern-carrier-contract", modern <= set(artifact), sorted(modern - set(artifact)))
    check("candidate-no-effect", artifact["status"] == "candidate-unadmitted" and artifact["authority_effect"] == witness["authority_effect"] == "none", {"status": artifact["status"], "authority_effect": artifact["authority_effect"]})
    root_binding = artifact["artifact_type_root_binding"]
    check("artifact-type-v2-root", root_binding["path"] == str(ROOT_TYPE.relative_to(LAB)) and root_binding["sha256"] == sha(ROOT_TYPE), root_binding)
    check("closed-schema-current", schema.get("additionalProperties") is False and artifact["schema_digest"] == sha(root / "schema.json"), {"schema_digest": sha(root / "schema.json")})

    binding = artifact["semantic_definition_bindings"][0]
    definition_id = binding["definition_ref"].split("@", 1)[0]
    check(
        "one-current-admitted-definition",
        artifact["semantic_definition_refs"] == [binding["definition_ref"]]
        and definitions["current_lookup"].get(definition_id) == binding["definition_ref"]
        and binding["admission_posture"] == "admitted"
        and sha(LAB / binding["path"]) == binding["sha256"],
        binding,
    )

    kind = artifact["classification"]["semantic_kind"]
    roles = expected_roles(kind, model)
    allowed = sorted({role["relation_kind_ref"] for role in roles})
    check("closed-relation-role-surface", artifact["relation_roles"] == roles and artifact["allowed_relation_kinds"] == allowed and bool(roles), {"declared": artifact["relation_roles"], "expected": roles})

    errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(witness)]
    check("positive-witness", not errors, errors)
    hostile = []
    for relative in artifact["validation_contract"]["negative_witnesses"]:
        rejected = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(load(root / relative))]
        hostile.append({"path": relative, "rejected": bool(rejected), "errors": rejected})
    check("five-hostile-rejections", len(hostile) == 5 and all(item["rejected"] for item in hostile), hostile)
    check("explicit-non-collapse", len(artifact["hostile_non_collapse"]) >= 1 and kind not in artifact["hostile_non_collapse"] and len(artifact["orthogonality_rules"]) == 4, {"kind": kind, "distinct_from": artifact["hostile_non_collapse"]})

    role_set = {(role["relation_kind_ref"], role["direction"], counterpart) for role in roles for counterpart in role["counterpart_kinds"]}
    fixture_roles = {(relation["relation_kind_ref"], relation["direction"], relation["counterpart_kind"]) for relation in witness["relation_refs"]}
    check("fixture-relations-declared", bool(fixture_roles) and fixture_roles <= role_set, {"fixture": sorted(fixture_roles), "allowed": sorted(role_set)})

    direction = artifact["source_direction"]
    check("shared-generator-current", direction["shared_generator_path"] == str(GENERATOR.relative_to(LAB)) and direction["shared_generator_sha256"] == sha(GENERATOR), direction)
    spec = importlib.util.spec_from_file_location("endpoint_carrier_generator", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    artifact_view = root / "ARTIFACT.md"
    witness_view = root / artifact["validation_contract"]["positive_projection"]
    check("deterministic-projections", artifact_view.read_text(encoding="utf-8") == module.render_artifact(artifact) and witness_view.read_text(encoding="utf-8") == module.render_instance(artifact, witness), {"artifact": sha(artifact_view), "witness": sha(witness_view)})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    receipt = {
        "schema_version": "cyberalchemy-lab-endpoint-carrier-validation/v1",
        "subject": artifact["artifact_type_ref"],
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {"artifact_sha256": sha(root / "artifact.json"), "schema_sha256": sha(root / "schema.json"), "positive_witness_sha256": sha(root / artifact["validation_contract"]["positive_witness"])},
        "claim_ceiling": "PASS proves the exact candidate carrier contract, Definition binding, closed schema, declared relation roles, hostile cases, fixture, and projections. It does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.",
    }
    dump(root / "receipts/validation.json", receipt)
    print(json.dumps({"subject": artifact["artifact_type_ref"], "result": result, "checks": len(checks)}, sort_keys=True))
    return 0 if result == "PASS" else 1

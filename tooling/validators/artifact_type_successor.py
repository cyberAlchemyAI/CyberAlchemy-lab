#!/usr/bin/env python3
"""Validate an immutable modernized Artifact Type successor candidate."""

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
REGISTRY = LAB / "authority/artifact-types/candidates/0008-registry-snapshot-0002/registry.json"
RELATIONS = LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json"
GENERATOR = LAB / "tooling/generators/artifact_type_successor.py"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def roles_for(kind: str, model: dict) -> list[dict]:
    roles = []
    for relation in model["entries"]:
        outgoing = sorted({pair["target_kind"] for pair in relation["allowed_endpoint_pairs"] if pair["source_kind"] == kind})
        incoming = sorted({pair["source_kind"] for pair in relation["allowed_endpoint_pairs"] if pair["target_kind"] == kind})
        if outgoing:
            roles.append({"relation_kind_ref": relation["relation_kind_id"], "direction": "source", "counterpart_kinds": outgoing})
        if incoming:
            roles.append({"relation_kind_ref": relation["relation_kind_id"], "direction": "target", "counterpart_kinds": incoming})
    return sorted(roles, key=lambda row: (row["relation_kind_ref"], row["direction"]))


def schema_is_closed(schema: dict) -> bool:
    if schema.get("additionalProperties") is False or schema.get("unevaluatedProperties") is False:
        return True
    ref = schema.get("$ref", "")
    if ref.startswith("#/$defs/"):
        target = schema.get("$defs", {}).get(ref.rsplit("/", 1)[1], {})
        return target.get("additionalProperties") is False or target.get("unevaluatedProperties") is False
    return False


def validate_package(root: Path) -> int:
    artifact = load(root / "artifact.json")
    schema = load(root / "schema.json")
    witness = load(root / artifact["validation_contract"]["positive_witness"])
    definitions = load(DEFINITIONS)
    registry = load(REGISTRY)
    model = load(RELATIONS)
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    modern = {"semantic_owner_ref", "semantic_definition_refs", "instance_contract", "distinct_validation_purpose", "orthogonality_rules", "source_direction", "four_facets", "validation_contract", "typed_residue", "claim_ceiling", "predecessor_contract", "allowed_relation_kinds", "relation_roles"}
    check("modern-successor-contract", modern <= set(artifact), sorted(modern - set(artifact)))
    check("candidate-no-effect", artifact["status"] == "candidate-unadmitted" and artifact["authority_effect"] == "none", {"status": artifact["status"], "authority_effect": artifact["authority_effect"]})
    root_binding = artifact["artifact_type_root_binding"]
    check("artifact-type-v2-root", root_binding["sha256"] == sha(ROOT_TYPE), root_binding)
    predecessor = artifact["predecessor_contract"]
    admitted = next((row for row in registry["admitted_contracts"] if row["artifact_type_ref"] == predecessor["artifact_type_ref"] and row["artifact_path"] == predecessor["path"]), None)
    check("exact-admitted-predecessor", admitted is not None and admitted["artifact_sha256"] == predecessor["sha256"] == sha(LAB / predecessor["path"]) and admitted["admission_decision_ref"] == predecessor["admission_decision_ref"], predecessor)
    check("closed-schema-current", schema_is_closed(schema) and artifact["schema_digest"] == sha(root / "schema.json"), {"closed": schema_is_closed(schema), "schema": sha(root / "schema.json")})
    binding = artifact["semantic_definition_bindings"][0]
    did = binding["definition_ref"].split("@", 1)[0]
    check("current-admitted-definition", artifact["semantic_definition_refs"] == [binding["definition_ref"]] and definitions["current_lookup"].get(did) == binding["definition_ref"] and binding["admission_posture"] == "admitted" and sha(LAB / binding["path"]) == binding["sha256"], binding)
    kind = artifact["classification"]["semantic_kind"]
    roles = roles_for(kind, model)
    check("closed-relation-surface", artifact["relation_roles"] == roles and artifact["allowed_relation_kinds"] == sorted({row["relation_kind_ref"] for row in roles}), {"declared": artifact["relation_roles"], "expected": roles})
    errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(witness)]
    check("positive-witness", not errors, errors)
    hostile = []
    for relative in artifact["validation_contract"]["negative_witnesses"]:
        errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(load(root / relative))]
        hostile.append({"path": relative, "rejected": bool(errors), "errors": errors})
    check("hostile-rejections", len(hostile) >= 2 and all(row["rejected"] for row in hostile), hostile)
    check("successor-non-collapse", artifact["artifact_type_ref"] != predecessor["artifact_type_ref"] and len(artifact["orthogonality_rules"]) == 4, {"successor": artifact["artifact_type_ref"], "predecessor": predecessor["artifact_type_ref"]})
    direction = artifact["source_direction"]
    check("shared-generator-current", direction["shared_generator_sha256"] == sha(GENERATOR), direction)
    spec = importlib.util.spec_from_file_location("artifact_type_successor_generator", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    av = root / "ARTIFACT.md"
    wv = root / artifact["validation_contract"]["positive_projection"]
    check("deterministic-projections", av.read_text(encoding="utf-8") == module.render_artifact(artifact) and wv.read_text(encoding="utf-8") == module.render_instance(artifact, witness), {"artifact": sha(av), "witness": sha(wv)})
    result = "PASS" if all(row["result"] == "PASS" for row in checks) else "BLOCK"
    receipt = {"schema_version": "cyberalchemy-lab-artifact-type-successor-validation/v1", "subject": artifact["artifact_type_ref"], "result": result, "authority_effect": "none", "checks": checks, "materials": {"artifact_sha256": sha(root / "artifact.json"), "schema_sha256": sha(root / "schema.json"), "positive_witness_sha256": sha(root / artifact["validation_contract"]["positive_witness"])}, "claim_ceiling": "PASS proves this exact candidate successor, admitted predecessor binding, current Definition, closed schema, fixture behavior, relation surface, and projections. It does not admit or activate the successor, transition the predecessor, or create an instance."}
    dump(root / "receipts/validation.json", receipt)
    print(json.dumps({"subject": artifact["artifact_type_ref"], "result": result, "checks": len(checks)}, sort_keys=True))
    return 0 if result == "PASS" else 1

#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import jsonschema

LAB = Path(__file__).resolve().parents[4]
ROOT_TYPE = LAB / "authority/artifact-types/artifact-type/v2/artifact.json"
GENERATOR = LAB / "tooling/generators/endpoint_carrier.py"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def roles_for(kind: str, model: dict) -> list[dict]:
    roles = []
    for entry in model["entries"]:
        targets = sorted({pair["target_kind"] for pair in entry["allowed_endpoint_pairs"] if pair["source_kind"] == kind})
        sources = sorted({pair["source_kind"] for pair in entry["allowed_endpoint_pairs"] if pair["target_kind"] == kind})
        if targets:
            roles.append({"relation_kind_ref": entry["relation_kind_id"], "direction": "source", "counterpart_kinds": targets})
        if sources:
            roles.append({"relation_kind_ref": entry["relation_kind_id"], "direction": "target", "counterpart_kinds": sources})
    return sorted(roles, key=lambda item: (item["relation_kind_ref"], item["direction"]))


def validate_package(root: Path) -> int:
    artifact = load(root / "artifact.json")
    schema = load(root / "schema.json")
    witness = load(root / artifact["validation_contract"]["positive_witness"])
    binding = artifact["semantic_definition_bindings"][0]
    model_binding = artifact["relation_model_binding"]
    model = load(LAB / model_binding["path"])
    checks = []

    def check(check_id: str, passed: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    check("candidate-no-effect", artifact["status"] == "candidate-unadmitted" and artifact["authority_effect"] == witness["authority_effect"] == "none", {"status": artifact["status"], "effect": artifact["authority_effect"]})
    check("artifact-type-v2-root", artifact["artifact_type_root_binding"]["path"] == str(ROOT_TYPE.relative_to(LAB)) and artifact["artifact_type_root_binding"]["sha256"] == sha(ROOT_TYPE), artifact["artifact_type_root_binding"])
    definition_path = LAB / binding["path"]
    definition = load(definition_path)
    expected_ref = f"{definition['definition_id']}@{definition['version']}"
    check("exact-definition", expected_ref == binding["definition_ref"] and sha(definition_path) == binding["sha256"] and binding["admission_posture"] in {"admitted", "candidate-unadmitted"}, binding)
    check("relation-model-current", sha(LAB / model_binding["path"]) == model_binding["sha256"] and model["status"] == "candidate-complete-awaiting-owner-review" and model["authority_effect"] == "none", model_binding)
    expected_roles = roles_for(artifact["classification"]["semantic_kind"], model)
    check("closed-relation-role-surface", artifact["relation_roles"] == expected_roles and artifact["allowed_relation_kinds"] == sorted({role["relation_kind_ref"] for role in expected_roles}) and bool(expected_roles), {"declared": artifact["relation_roles"], "expected": expected_roles})
    check("closed-schema-current", schema.get("additionalProperties") is False and artifact["schema_digest"] == sha(root / "schema.json"), artifact["schema_digest"])
    errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(witness)]
    check("positive-witness", not errors, errors)
    hostile = []
    for relative in artifact["validation_contract"]["negative_witnesses"]:
        failures = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(load(root / relative))]
        hostile.append({"path": relative, "rejected": bool(failures), "errors": failures})
    check("five-hostile-rejections", len(hostile) == 5 and all(item["rejected"] for item in hostile), hostile)
    allowed = {(role["relation_kind_ref"], role["direction"], counterpart) for role in expected_roles for counterpart in role["counterpart_kinds"]}
    actual = {(item["relation_kind_ref"], item["direction"], item["counterpart_kind"]) for item in witness["relation_refs"]}
    check("fixture-relations-declared", bool(actual) and actual <= allowed, {"actual": sorted(actual), "allowed": sorted(allowed)})
    check("explicit-non-collapse", bool(artifact["hostile_non_collapse"]) and artifact["classification"]["semantic_kind"] not in artifact["hostile_non_collapse"] and len(artifact["orthogonality_rules"]) == 4, artifact["hostile_non_collapse"])
    spec = importlib.util.spec_from_file_location("carrier_generator", GENERATOR)
    generator = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(generator)
    check("deterministic-projections", (root / "ARTIFACT.md").read_text(encoding="utf-8") == generator.render_artifact(artifact) and (root / artifact["validation_contract"]["positive_projection"]).read_text(encoding="utf-8") == generator.render_instance(artifact, witness), {"artifact": sha(root / "ARTIFACT.md"), "fixture": sha(root / artifact["validation_contract"]["positive_projection"])})
    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    receipt = {"schema_version": "cyberalchemy-lab-governance-transaction-carrier-validation/v1", "subject": artifact["artifact_type_ref"], "result": result, "authority_effect": "none", "checks": checks, "materials": {"artifact_sha256": sha(root / "artifact.json"), "schema_sha256": sha(root / "schema.json"), "positive_witness_sha256": sha(root / artifact["validation_contract"]["positive_witness"])}, "claim_ceiling": "PASS proves this exact candidate carrier, Definition binding, relation surface, closed schema, fixture, hostile cases, and projections. It admits nothing."}
    dump(root / "receipts/validation.json", receipt)
    print(json.dumps({"subject": artifact["artifact_type_ref"], "result": result, "checks": len(checks)}, sort_keys=True))
    return 0 if result == "PASS" else 1

#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    artifact = load(ROOT / "artifact.json")
    schema = load(ROOT / "schema.json")
    witness = load(ROOT / artifact["validation_contract"]["positive_witness"])
    definitions = load(LAB / "authority/definitions/registry.json")
    checks = []

    def check(check_id, ok, detail):
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(witness)]
    check("closed-schema-positive-witness", schema.get("additionalProperties") is False and not errors, errors)
    negatives = []
    for relative in artifact["validation_contract"]["negative_witnesses"]:
        rejected = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(load(ROOT / relative))]
        negatives.append({"path": relative, "rejected": bool(rejected), "errors": rejected})
    check("negative-and-non-collapse-witnesses", len(negatives) == 6 and all(item["rejected"] for item in negatives), negatives)
    root = artifact["artifact_type_root_binding"]
    check("artifact-type-v2-root", sha(LAB / root["path"]) == root["sha256"] and root["admission_decision_ref"] == "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1", root)
    predecessor = artifact["predecessor_contract"]
    admission = load(LAB / "authority/artifact-types/admissions/migration-26/v1/capability-realization-binding.json")
    check(
        "exact-admitted-predecessor",
        predecessor["artifact_type_ref"] == admission["artifact_type_ref"] == "cal.artifact-type.capability-realization-binding/v1"
        and predecessor["sha256"] == admission["artifact_sha256"] == sha(LAB / predecessor["path"])
        and predecessor["admission_decision_ref"] == admission["admission_decision_ref"],
        predecessor,
    )
    binding = artifact["semantic_definition_bindings"][0]
    definition_id = binding["definition_ref"].split("@", 1)[0]
    check(
        "positive-definition-current",
        artifact["semantic_definition_refs"] == [binding["definition_ref"]]
        and binding["definition_ref"] == "cal.definition.capability-realization-binding@1.0.0-candidate.1"
        and definitions["current_lookup"].get(definition_id) == binding["definition_ref"]
        and sha(LAB / binding["path"]) == binding["sha256"],
        binding,
    )
    endpoint_results = [
        endpoint["realization_ref"] != witness["node_id"]
        and endpoint["realization_ref"] != witness["capability_ref"]
        and endpoint["realization_ref"] != witness["capability_version_ref"]
        for endpoint in witness["realization_refs"]
    ]
    check(
        "binding-capability-realization-non-collapse",
        witness["node_id"] not in {witness["capability_ref"], witness["capability_version_ref"]}
        and all(endpoint_results)
        and len(artifact["orthogonality_rules"]) == 4,
        {"binding": witness["node_id"], "capability": witness["capability_version_ref"], "realizations": [item["realization_ref"] for item in witness["realization_refs"]]},
    )
    generator = ROOT / artifact["source_direction"]["generator"]
    check("schema-and-generator-digests", artifact["schema_digest"] == sha(ROOT / "schema.json") and artifact["source_direction"]["generator_sha256"] == sha(generator), {"schema": sha(ROOT / "schema.json"), "generator": sha(generator)})
    spec = importlib.util.spec_from_file_location("crb_v2_generator", generator)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    artifact_view = ROOT / "ARTIFACT.md"
    witness_view = ROOT / artifact["validation_contract"]["positive_projection"]
    check("deterministic-projections", artifact_view.read_text(encoding="utf-8") == module.render_artifact(artifact) and witness_view.read_text(encoding="utf-8") == module.render_instance(artifact, witness), {"artifact": sha(artifact_view), "witness": sha(witness_view)})
    check(
        "candidate-no-authority-effect",
        artifact["artifact_type_ref"] == "cal.artifact-type.capability-realization-binding/v2"
        and artifact["version"] == "2.0.0-candidate.1"
        and artifact["status"] == witness["status"] == "candidate-unadmitted"
        and artifact["authority_effect"] == witness["authority_effect"] == "none",
        {"type": artifact["artifact_type_ref"], "version": artifact["version"], "status": artifact["status"], "authority_effect": artifact["authority_effect"]},
    )
    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    receipt = {
        "schema_version": "cyberalchemy-lab-capability-realization-binding-v2-validation/v1",
        "subject": artifact["artifact_type_ref"],
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {"artifact_sha256": sha(ROOT / "artifact.json"), "schema_sha256": sha(ROOT / "schema.json"), "positive_witness_sha256": sha(ROOT / artifact["validation_contract"]["positive_witness"])},
        "claim_ceiling": "PASS proves the exact candidate v2 contract, predecessor, semantic binding, schema, non-collapse cases, fixtures, and projections. It does not admit v2 or any instance, transition v1, or activate a realization.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(json.dumps({"subject": receipt["subject"], "result": result, "checks": len(checks)}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Materialize the five semantic repairs and CRB/v2 successor for Step 5."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
DEFINITIONS = LAB / "authority/definitions/registry.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def definition_binding(name: str) -> dict:
    registry = load(DEFINITIONS)
    definition_id = f"cal.definition.{name}"
    ref = registry["current_lookup"][definition_id]
    row = next(
        item for item in registry["entries"]
        if item["definition_id"] == definition_id
        and f"{item['definition_id']}@{item['version']}" == ref
    )
    return {
        "admission_decision_ref": row["admission_decision_ref"],
        "admission_posture": "admitted",
        "definition_ref": ref,
        "path": row["path"],
        "sha256": row["sha256"],
    }


def revise_standard_candidate(kind: str, version: str) -> dict:
    package = LAB / f"authority/artifact-types/{kind}/v1"
    artifact = load(package / "artifact.json")
    binding = definition_binding(kind)
    artifact["version"] = version
    artifact["semantic_definition_refs"] = [binding["definition_ref"]]
    artifact["semantic_definition_bindings"] = [binding]
    artifact["classification"]["lifecycle_posture_ref"] = "candidate:step5-carrier-closure/v1"
    artifact["typed_residue"] = [
        {
            "residue_id": "STEP5-ADMISSION-R1",
            "missing": f"Artifact Type owner admission for the exact revised {artifact['artifact_type_ref']} candidate.",
            "owner_ref": "role:artifact-type-owner",
            "consequence": "The revised carrier remains candidate-only.",
        },
        {
            "residue_id": "STEP5-ACTIVATION-R2",
            "missing": "A real instance, bounded consumer integration, and a separate activation decision.",
            "owner_ref": "role:migration-consumer-owner",
            "consequence": "Validation supplies no runtime, operational, or external effect.",
        },
    ]
    dump(package / "artifact.json", artifact)

    materialization_path = package / "materialization.json"
    if materialization_path.exists():
        materialization = load(materialization_path)
        materialization["definition_admission"] = {
            "decision_ref": binding["admission_decision_ref"],
            "path": "docs/decisions/0066-definition-specialization-resolution-admission/decision.json",
            "sha256": sha(LAB / "docs/decisions/0066-definition-specialization-resolution-admission/decision.json"),
        }
        materialization["semantic_definition_bindings"] = [binding]
        materialization["status"] = "candidate-semantically-rebound"
        dump(materialization_path, materialization)
    return {"artifact_type_ref": artifact["artifact_type_ref"], "artifact_path": str((package / "artifact.json").relative_to(LAB)), "definition_refs": artifact["semantic_definition_refs"]}


def revise_ontology_package() -> dict:
    package = LAB / "authority/artifact-types/ontology-package/v1"
    artifact = load(package / "artifact.json")
    bindings = []
    for name in ("ontology", "generated-output"):
        binding = definition_binding(name)
        binding.update({"root": "lab", "selector": "whole-file", "content_sha256": binding["sha256"]})
        bindings.append(binding)
    artifact["version"] = "1.0.0-candidate.2"
    artifact["semantic_definition_refs"] = [item["definition_ref"] for item in bindings]
    artifact["semantic_definition_bindings"] = bindings
    artifact["classification"]["lifecycle_posture_ref"] = "candidate:step5-carrier-closure/v1"
    artifact["typed_residue"] = [
        {
            "residue_id": "STEP5-ONTOLOGY-PACKAGE-R1",
            "missing": "Artifact Type owner admission for this exact locally rebound Ontology Package/v1 candidate.",
            "owner_ref": "role:artifact-type-owner",
            "consequence": "The package remains candidate-only and cannot establish Product or ontology authority.",
        },
        {
            "residue_id": "STEP5-ONTOLOGY-PACKAGE-R2",
            "missing": "A separately admitted package instance and consumer activation decision.",
            "owner_ref": "role:ontology-product-owner",
            "consequence": "The fixture remains validation evidence and is not an active ontology runtime.",
        },
    ]
    artifact["claim_ceiling"] = "This candidate binds Ontology Package/v1 to the admitted local Ontology and Generated Output Definitions. PASS proves only its exact schema, bindings, fixtures, and projections; it does not admit the type or an instance, approve the Product, activate a consumer, or authorize publication, deployment, or source retirement."
    dump(package / "artifact.json", artifact)
    return {"artifact_type_ref": artifact["artifact_type_ref"], "artifact_path": str((package / "artifact.json").relative_to(LAB)), "definition_refs": artifact["semantic_definition_refs"]}


def materialize_crb_v2() -> dict:
    source = LAB / "authority/artifact-types/capability-realization-binding/v1"
    target = LAB / "authority/artifact-types/capability-realization-binding/v2"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    artifact = load(target / "artifact.json")
    binding = definition_binding("capability-realization-binding")
    artifact["artifact_type_ref"] = "cal.artifact-type.capability-realization-binding/v2"
    artifact["version"] = "2.0.0-candidate.1"
    artifact["classification"]["lifecycle_posture_ref"] = "candidate:step5-carrier-closure/v1"
    artifact["semantic_definition_refs"] = [binding["definition_ref"]]
    artifact["semantic_definition_bindings"] = [binding]
    artifact["schema_ref"] = "cal.schema.capability-realization-binding/v2"
    artifact["predecessor_contract"] = {
        "artifact_type_ref": "cal.artifact-type.capability-realization-binding/v1",
        "path": "authority/artifact-types/capability-realization-binding/v1/artifact.json",
        "sha256": sha(source / "artifact.json"),
        "admission_decision_ref": "CAL-DECISION-0060-CAPABILITY-REALIZATION-BINDING-V1-ADMISSION",
    }
    artifact["orthogonality_rules"] = [
        {
            "rule_id": "CRB2-BINDING-IDENTITY",
            "statement": "The binding, Product Capability, realization endpoint, Capability Instance, Implementation, owner, contract, evidence, and lifecycle state retain separate identities.",
        },
        {
            "rule_id": "CRB2-ONE-CAPABILITY-VERSION",
            "statement": "Each binding names exactly one Product Capability version and one or more explicitly typed realization endpoints.",
        },
        {
            "rule_id": "CRB2-CLAIM-SEPARATION",
            "statement": "Candidate, adopted, conformant, observed, operational, effective, and valuable remain independent claims with independent evidence and decisions.",
        },
        {
            "rule_id": "CRB2-NO-IMPLICIT-REALIZATION",
            "statement": "Schema conformance or relation membership cannot imply that a realization exists, runs, conforms, succeeds, or produces Product value.",
        },
    ]
    artifact["typed_residue"] = [
        {
            "residue_id": "CRB2-R1",
            "missing": "Artifact Type owner admission for this exact v2 successor contract.",
            "owner_ref": "role:artifact-type-owner",
            "consequence": "v2 remains candidate-only and v1 remains admitted-current.",
        },
        {
            "residue_id": "CRB2-R2",
            "missing": "A separately admitted binding instance and consumer activation decision.",
            "owner_ref": "role:migration-consumer-owner",
            "consequence": "No implementation, workflow, service, or Agent capability is adopted or activated.",
        },
    ]
    artifact["claim_ceiling"] = "This candidate is the immutable Capability Realization Binding/v2 successor with its own admitted positive Definition. PASS proves its exact schema, semantic binding, predecessor, fixtures, and non-collapse rules; it does not admit v2 or an instance, transition v1, adopt a realization, establish conformance, operation, effectiveness, or Product value, or activate a consumer."
    artifact["source_direction"] = {
        "canonical": "artifact.json",
        "human_projection": "ARTIFACT.md",
        "projection_policy": "generated-only",
        "generator": "generator.py",
        "generator_sha256": "PENDING-GENERATOR-DIGEST",
    }
    artifact["validation_contract"]["validator_path"] = "authority/artifact-types/capability-realization-binding/v2/validate.py"
    artifact["validation_contract"].pop("shared_validator_path", None)
    artifact["validation_contract"].pop("shared_validator_sha256", None)
    artifact["validation_contract"]["required_checks"] = [
        "closed schema and positive witness",
        "negative and hostile rejection",
        "exact Artifact Type/v2 root binding",
        "exact admitted v1 predecessor binding",
        "exact current Capability Realization Binding Definition",
        "binding, capability, realization, and claim non-collapse",
        "deterministic projections",
        "candidate authority effect none",
    ]
    artifact["validation_contract"]["negative_witnesses"] = [
        "fixtures/invalid/authority.json",
        "fixtures/invalid/missing-field.json",
        "fixtures/invalid/extra-field.json",
        "fixtures/invalid/missing-capability-version.json",
        "fixtures/invalid/collapsed-as-product-capability.json",
        "fixtures/invalid/collapsed-as-implementation.json",
    ]
    witness = load(target / "fixtures/valid/record.json")
    witness["binding_version"] = artifact["version"]
    dump(target / "fixtures/valid/record.json", witness)
    for path in target.glob("fixtures/invalid/*.json"):
        item = load(path)
        if "binding_version" in item:
            item["binding_version"] = artifact["version"]
            dump(path, item)
    collapsed_capability = copy.deepcopy(witness)
    collapsed_capability["kind"] = "product-capability"
    dump(target / "fixtures/invalid/collapsed-as-product-capability.json", collapsed_capability)
    collapsed_implementation = copy.deepcopy(witness)
    collapsed_implementation["kind"] = "implementation"
    dump(target / "fixtures/invalid/collapsed-as-implementation.json", collapsed_implementation)
    shutil.copyfile(ROOT / "templates/crb-v2-generator.py", target / "generator.py")
    shutil.copyfile(ROOT / "templates/crb-v2-validate.py", target / "validate.py")
    artifact["source_direction"]["generator_sha256"] = sha(target / "generator.py")
    dump(target / "artifact.json", artifact)
    return {"artifact_type_ref": artifact["artifact_type_ref"], "artifact_path": str((target / "artifact.json").relative_to(LAB)), "definition_refs": artifact["semantic_definition_refs"]}


def main() -> None:
    postimages = [
        revise_standard_candidate("context-profile", "1.0.0-candidate.3"),
        revise_standard_candidate("measurement-method", "1.0.0-candidate.3"),
        revise_standard_candidate("measurement-result", "1.0.0-candidate.3"),
        revise_standard_candidate("model-instance-binding", "1.0.0-candidate.3"),
        revise_ontology_package(),
        materialize_crb_v2(),
    ]
    dump(ROOT / "hard-corrections-postimages.json", {
        "schema_version": "cyberalchemy-lab-step5-hard-corrections-postimages/v1",
        "status": "candidate-materialized",
        "authority_effect": "none",
        "postimages": postimages,
        "claim_ceiling": "This manifest identifies six materialized candidate postimages. It does not admit, supersede, or activate them.",
    })


if __name__ == "__main__":
    main()

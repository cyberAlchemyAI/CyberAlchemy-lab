#!/usr/bin/env python3
"""Validate Capability Realization Binding/v1 admission and Product sequence completion."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
PACKAGE = LAB / "authority/artifact-types/capability-realization-binding/v1"
ADMISSION = LAB / "authority/artifact-types/admissions/migration-26/v1/capability-realization-binding.json"
REFINEMENT = LAB / "authority/artifact-types/candidates/0004-remaining-26-materialization/refinements/type.capability-realization-binding.json"
MODEL_SELECTION = LAB / "authority/product-context/selected/v1/selection.json"
SEQUENCE_STATUS = LAB / "authority/product-context/selected/v1/admission-status.json"
PREREQUISITES = [
    LAB / "docs/decisions/0057-product-identity-v2-successor-admission/decision.json",
    LAB / "docs/decisions/0058-product-thesis-v1-admission/decision.json",
    LAB / "docs/decisions/0059-product-capability-v1-admission/decision.json",
]
SHARED_VALIDATOR = LAB / "tooling/validators/artifact_surface.py"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    authorization = load(ROOT / "authorization.json")
    decision = load(ROOT / "decision.json")
    admission = load(ADMISSION)
    artifact = load(PACKAGE / "artifact.json")
    selection = load(MODEL_SELECTION)
    prerequisite_decisions = [load(path) for path in PREREQUISITES]
    sequence_status = load(SEQUENCE_STATUS)

    check(
        "authorization-exact",
        authorization["artifact"]["sha256"] == sha(PACKAGE / "artifact.json")
        and authorization["schema"]["sha256"] == sha(PACKAGE / "schema.json")
        and authorization["validation_receipt"]["sha256"] == sha(PACKAGE / "receipts/validation.json")
        and authorization["review_refinement"]["sha256"] == sha(REFINEMENT)
        and authorization["governing_model_selection"]["sha256"] == sha(MODEL_SELECTION)
        and authorization["prerequisite_decisions"] == [
            {"path": str(path.relative_to(LAB)), "sha256": sha(path)} for path in PREREQUISITES
        ],
        authorization,
    )
    check(
        "governing-sequence-fourth-item",
        selection["status"] == "owner-approved-governing-model"
        and selection["separate_decision_required_per_item"] is True
        and selection["admission_sequence"][3] == "cal.artifact-type.capability-realization-binding/v1",
        selection["admission_sequence"],
    )
    expected_prerequisites = [
        "cal.artifact-type.product-identity/v2",
        "cal.artifact-type.product-thesis/v1",
        "cal.artifact-type.product-capability/v1",
    ]
    observed_prerequisites = [
        prerequisite_decisions[0]["lifecycle_result"]["current"]["artifact_type_ref"],
        prerequisite_decisions[1]["admitted_artifact_type"]["artifact_type_ref"],
        prerequisite_decisions[2]["admitted_artifact_type"]["artifact_type_ref"],
    ]
    check(
        "product-model-prerequisites-admitted",
        all(item["status"] == "owner-admitted" for item in prerequisite_decisions)
        and observed_prerequisites == expected_prerequisites,
        observed_prerequisites,
    )
    check(
        "overlay-admits-only-type",
        admission["artifact_type_ref"] == "cal.artifact-type.capability-realization-binding/v1"
        and admission["artifact_version"] == "1.0.0-candidate.2"
        and admission["lifecycle_state"] == "admitted-current"
        and admission["instance_admissions"] == 0
        and admission["consumer_activations"] == 0,
        admission,
    )
    check(
        "definition-binding-admitted",
        all(binding["admission_posture"] == "admitted" for binding in artifact["semantic_definition_bindings"]),
        artifact["semantic_definition_bindings"],
    )
    spec = importlib.util.spec_from_file_location("capability_binding_artifact_validator", SHARED_VALIDATOR)
    validator = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(validator)
    check(
        "package-validation-pass",
        validator.validate_package(PACKAGE) == 0
        and load(PACKAGE / "receipts/validation.json")["result"] == "PASS"
        and load(PACKAGE / "receipts/validation.json")["summary"] == {"blocked": 0, "passed": 12, "total": 12},
        {"receipt": "authority/artifact-types/capability-realization-binding/v1/receipts/validation.json"},
    )
    status_refs = [item["artifact_type_ref"] for item in sequence_status["items"]]
    check(
        "product-model-sequence-complete",
        sequence_status["selection"]["sha256"] == sha(MODEL_SELECTION)
        and sequence_status["status"] == "artifact-type-sequence-complete"
        and status_refs == selection["admission_sequence"]
        and sequence_status["summary"] == {
            "admitted_current_items": 4,
            "consumer_activations_by_sequence": 0,
            "expected_items": 4,
            "instances_admitted_by_sequence": 0,
        }
        and all(item["lifecycle_state"] == "admitted-current" for item in sequence_status["items"]),
        sequence_status,
    )
    check(
        "decision-exact",
        decision["authorization"]["sha256"] == sha(ROOT / "authorization.json")
        and decision["admission_record"]["sha256"] == sha(ADMISSION)
        and decision["governing_model_selection"]["sha256"] == sha(MODEL_SELECTION)
        and decision["admitted_artifact_type"]["sha256"] == sha(PACKAGE / "artifact.json")
        and decision["admitted_artifact_type"]["schema_sha256"] == sha(PACKAGE / "schema.json")
        and decision["product_model_sequence_result"] == {
            "admitted_current_items": 4,
            "expected_items": 4,
            "result": "complete",
        },
        decision["product_model_sequence_result"],
    )
    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-validation/v1",
        "subject": decision["decision_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "validation-only",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "claim_ceiling": "PASS proves the exact authorization, Product model sequence, prerequisite admissions, Capability Realization Binding/v1 admission overlay, admitted Definition binding, package validation, and four-item sequence status. It does not admit a binding instance or activate a realization, implementation, consumer, or runtime.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"CAPABILITY_REALIZATION_BINDING_V1_ADMISSION={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())

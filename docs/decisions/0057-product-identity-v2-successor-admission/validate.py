#!/usr/bin/env python3
"""Validate the Product Identity/v2 successor admission overlay."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
CURRENT = LAB / "authority/artifact-types/product-identity/v2"
PREDECESSOR = LAB / "authority/artifact-types/product-identity/v1"
SUCCESSOR = CURRENT / "successor.json"
PREDECESSOR_DECISION = LAB / "docs/decisions/0030-cml07-s2-artifact-types-v1/decision.json"
MODEL_SELECTION = LAB / "authority/product-context/selected/v1/selection.json"
ADMISSION = LAB / "authority/artifact-types/admissions/migration-26/v1/product-identity.json"
SHARED_VALIDATOR = LAB / "tooling/validators/cml07_identity_artifact_type.py"


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
    artifact = load(CURRENT / "artifact.json")
    successor = load(SUCCESSOR)
    predecessor_decision = load(PREDECESSOR_DECISION)
    selection = load(MODEL_SELECTION)

    check(
        "authorization-exact",
        authorization["current_artifact"]["sha256"] == sha(CURRENT / "artifact.json")
        and authorization["current_schema"]["sha256"] == sha(CURRENT / "schema.json")
        and authorization["current_validation_receipt"]["sha256"] == sha(CURRENT / "receipts/validation.json")
        and authorization["predecessor_artifact"]["sha256"] == sha(PREDECESSOR / "artifact.json")
        and authorization["predecessor_schema"]["sha256"] == sha(PREDECESSOR / "schema.json")
        and authorization["successor_record"]["sha256"] == sha(SUCCESSOR)
        and authorization["predecessor_admission_decision"]["sha256"] == sha(PREDECESSOR_DECISION)
        and authorization["governing_model_selection"]["sha256"] == sha(MODEL_SELECTION),
        authorization,
    )
    check(
        "governing-sequence-first-item",
        selection["status"] == "owner-approved-governing-model"
        and selection["separate_decision_required_per_item"] is True
        and selection["admission_sequence"][0] == "cal.artifact-type.product-identity/v2",
        selection["admission_sequence"],
    )
    predecessor_entry = next(
        item for item in predecessor_decision["admitted_artifact_types"]
        if item["artifact_type_ref"] == "cal.artifact-type.product-identity/v1"
    )
    check(
        "predecessor-was-admitted-current",
        predecessor_decision["status"] == "owner-admitted"
        and predecessor_entry["decision_overlay_status"] == "admitted-current"
        and predecessor_entry["artifact_sha256"] == sha(PREDECESSOR / "artifact.json")
        and predecessor_entry["schema_sha256"] == sha(PREDECESSOR / "schema.json"),
        predecessor_entry,
    )
    check(
        "successor-binding-exact",
        successor["status"] == "candidate-unadmitted"
        and successor["authority_effect"] == "none"
        and successor["successor_ref"] == "cal.artifact-type.product-identity/v2"
        and successor["predecessor_ref"] == "cal.artifact-type.product-identity/v1"
        and successor["predecessor_artifact"]["sha256"] == sha(PREDECESSOR / "artifact.json")
        and successor["predecessor_schema"]["sha256"] == sha(PREDECESSOR / "schema.json"),
        successor,
    )
    lifecycle = admission["lifecycle"]
    check(
        "single-current-lifecycle",
        lifecycle["current"]["artifact_type_ref"] == "cal.artifact-type.product-identity/v2"
        and lifecycle["current"]["lifecycle_state"] == "admitted-current"
        and lifecycle["predecessor"]["artifact_type_ref"] == "cal.artifact-type.product-identity/v1"
        and lifecycle["predecessor"]["previous_lifecycle_state"] == "admitted-current"
        and lifecycle["predecessor"]["lifecycle_state"] == "admitted-historical"
        and admission["instance_admissions"] == 0
        and admission["consumer_activations"] == 0,
        lifecycle,
    )
    check(
        "definition-bindings-admitted",
        all(binding["admission_posture"] == "admitted" for binding in artifact["semantic_definition_bindings"]),
        artifact["semantic_definition_bindings"],
    )
    spec = importlib.util.spec_from_file_location("product_identity_v2_validator", SHARED_VALIDATOR)
    validator = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(validator)
    check(
        "package-validation-pass",
        validator.run(CURRENT, "product-identity") == 0
        and load(CURRENT / "receipts/validation.json")["result"] == "PASS"
        and load(CURRENT / "receipts/validation.json")["summary"] == {"blocked": 0, "passed": 17, "total": 17},
        {"receipt": "authority/artifact-types/product-identity/v2/receipts/validation.json"},
    )
    check(
        "decision-exact",
        decision["authorization"]["sha256"] == sha(ROOT / "authorization.json")
        and decision["admission_record"]["sha256"] == sha(ADMISSION)
        and decision["governing_model_selection"]["sha256"] == sha(MODEL_SELECTION)
        and decision["admission_result"] == {
            "artifact_types_admitted": 1,
            "consumer_activations": 0,
            "instances_admitted": 0,
            "predecessors_transitioned_to_historical": 1,
            "result": "complete",
        },
        decision["admission_result"],
    )
    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-successor-admission-validation/v1",
        "subject": decision["decision_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "validation-only",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "claim_ceiling": "PASS proves the exact authorization, predecessor admission, successor binding, lifecycle overlay, admitted Definition bindings, and Product Identity/v2 package validation. It does not admit or migrate a Product instance or activate a consumer or runtime.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"PRODUCT_IDENTITY_V2_SUCCESSOR_ADMISSION={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())

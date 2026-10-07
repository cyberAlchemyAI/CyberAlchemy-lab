#!/usr/bin/env python3
"""Validate the exact Intent Artifact Type admission overlay."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
PACKAGE = LAB / "authority/artifact-types/intent/v1"
ADMISSION = LAB / "authority/artifact-types/admissions/migration-26/v1/intent.json"
SHARED_VALIDATOR = LAB / "tooling/validators/artifact_surface.py"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    authorization = load(ROOT / "authorization.json")
    decision = load(ROOT / "decision.json")
    admission = load(ADMISSION)
    artifact = load(PACKAGE / "artifact.json")
    schema_path = PACKAGE / "schema.json"
    receipt_path = PACKAGE / "receipts/validation.json"
    check("authorization-exact", authorization["artifact"]["sha256"] == sha(PACKAGE / "artifact.json") and authorization["schema"]["sha256"] == sha(schema_path) and authorization["validation_receipt"]["sha256"] == sha(receipt_path), authorization)
    check("decision-exact", decision["admitted_artifact_type"]["sha256"] == sha(PACKAGE / "artifact.json") and decision["admitted_artifact_type"]["schema_sha256"] == sha(schema_path) and decision["authorization"]["sha256"] == sha(ROOT / "authorization.json") and decision["admission_record"]["sha256"] == sha(ADMISSION), decision["admitted_artifact_type"])
    check("overlay-admits-only-type", admission["artifact_type_ref"] == "cal.artifact-type.intent/v1" and admission["artifact_version"] == "1.0.0-candidate.2" and admission["lifecycle_state"] == "admitted-current" and admission["instance_admissions"] == 0 and admission["consumer_activations"] == 0, admission)
    check("definition-binding-admitted", all(binding["admission_posture"] == "admitted" for binding in artifact["semantic_definition_bindings"]), artifact["semantic_definition_bindings"])
    spec = importlib.util.spec_from_file_location("intent_artifact_validator", SHARED_VALIDATOR)
    validator = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(validator)
    check("package-validation-pass", validator.validate_package(PACKAGE) == 0 and load(receipt_path)["result"] == "PASS", {"receipt": str(receipt_path.relative_to(LAB))})
    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-validation/v1",
        "subject": decision["decision_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "validation-only",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "claim_ceiling": "PASS proves the exact authorization, decision, admission overlay, admitted Definition binding, and candidate package validation. It does not admit instances or activate consumers.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"INTENT_ARTIFACT_TYPE_ADMISSION={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())

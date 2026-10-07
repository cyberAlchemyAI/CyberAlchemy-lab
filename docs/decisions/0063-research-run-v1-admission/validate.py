#!/usr/bin/env python3
"""Validate the exact Research Run/v1 Artifact Type admission overlay."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
PACKAGE = LAB / "authority/artifact-types/research-run/v1"
ADMISSION = LAB / "authority/artifact-types/admissions/migration-26/v1/research-run.json"
REFINEMENT = LAB / "authority/artifact-types/candidates/0004-remaining-26-materialization/refinements/type.research-run.json"
MATERIALIZATION = PACKAGE / "materialization.json"
INQUIRY_DECISION = LAB / "docs/decisions/0062-research-inquiry-v1-admission/decision.json"
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
    materialization = load(MATERIALIZATION)
    inquiry_decision = load(INQUIRY_DECISION)

    check(
        "authorization-exact",
        authorization["artifact"]["sha256"] == sha(PACKAGE / "artifact.json")
        and authorization["schema"]["sha256"] == sha(PACKAGE / "schema.json")
        and authorization["validation_receipt"]["sha256"] == sha(PACKAGE / "receipts/validation.json")
        and authorization["review_refinement"]["sha256"] == sha(REFINEMENT)
        and authorization["package_materialization"]["sha256"] == sha(MATERIALIZATION)
        and authorization["migration_contract"]["sha256"] == sha(PACKAGE / "migration-contract.json")
        and authorization["research_inquiry_prerequisite"]["sha256"] == sha(INQUIRY_DECISION),
        authorization,
    )
    check(
        "research-inquiry-prerequisite-admitted",
        inquiry_decision["status"] == "owner-admitted"
        and inquiry_decision["admitted_artifact_type"]["artifact_type_ref"] == "cal.artifact-type.research-inquiry/v1"
        and inquiry_decision["admitted_artifact_type"]["decision_overlay_status"] == "admitted-current",
        inquiry_decision["admitted_artifact_type"],
    )
    check(
        "materialization-entry-current",
        materialization["artifact_type_ref"] == "cal.artifact-type.research-run/v1"
        and materialization["target_id"] == "type.research-run"
        and materialization["status"] == "candidate-refined"
        and materialization["review_refinement"]["sha256"] == sha(REFINEMENT),
        materialization,
    )
    check(
        "overlay-admits-only-type",
        admission["artifact_type_ref"] == "cal.artifact-type.research-run/v1"
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
    spec = importlib.util.spec_from_file_location("research_run_artifact_validator", SHARED_VALIDATOR)
    validator = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(validator)
    check(
        "package-validation-pass",
        validator.validate_package(PACKAGE) == 0
        and load(PACKAGE / "receipts/validation.json")["result"] == "PASS"
        and load(PACKAGE / "receipts/validation.json")["summary"] == {"blocked": 0, "passed": 12, "total": 12},
        {"receipt": "authority/artifact-types/research-run/v1/receipts/validation.json"},
    )
    check(
        "decision-exact",
        decision["authorization"]["sha256"] == sha(ROOT / "authorization.json")
        and decision["admission_record"]["sha256"] == sha(ADMISSION)
        and decision["package_materialization"]["sha256"] == sha(MATERIALIZATION)
        and decision["research_inquiry_prerequisite"]["sha256"] == sha(INQUIRY_DECISION)
        and decision["admitted_artifact_type"]["sha256"] == sha(PACKAGE / "artifact.json")
        and decision["admitted_artifact_type"]["schema_sha256"] == sha(PACKAGE / "schema.json"),
        decision["admitted_artifact_type"],
    )
    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-validation/v1",
        "subject": decision["decision_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "validation-only",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "claim_ceiling": "PASS proves the exact authorization, admitted Research Inquiry prerequisite, package materialization, Research Run/v1 admission overlay, admitted Definition binding, and package validation. It does not admit or execute a run, authenticate evidence, establish a Finding, or activate a consumer or runtime.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"RESEARCH_RUN_V1_ADMISSION={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())

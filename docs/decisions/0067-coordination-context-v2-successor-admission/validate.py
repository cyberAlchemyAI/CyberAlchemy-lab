#!/usr/bin/env python3
"""Validate the Coordination Context/v2 successor admission overlay."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
CURRENT = LAB / "authority/artifact-types/coordination-context/v2"
PREDECESSOR = LAB / "authority/artifact-types/coordination-context/v1"
PREDECESSOR_DECISION = LAB / "docs/decisions/0021-ctx01-artifact-type-promotion/decision.json"
ADMISSION = LAB / "authority/artifact-types/admissions/context-metamodel/v2/coordination-context.json"
REGISTRY_ROOT = LAB / "authority/artifact-types/candidates/0006-effective-state-registry"
REGISTRY = REGISTRY_ROOT / "registry.json"
DECISION_ID = "CAL-DECISION-0067-COORDINATION-CONTEXT-V2-SUCCESSOR-ADMISSION"


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
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    authorization = load(ROOT / "authorization.json")
    decision = load(ROOT / "decision.json")
    admission = load(ADMISSION)
    artifact = load(CURRENT / "artifact.json")
    predecessor_decision = load(PREDECESSOR_DECISION)
    registry = load(REGISTRY)
    package_receipt = load(CURRENT / "receipts/validation.json")

    check(
        "authorization-exact",
        authorization["current_artifact"]["sha256"] == sha(CURRENT / "artifact.json")
        and authorization["current_schema"]["sha256"] == sha(CURRENT / "schema.json")
        and authorization["current_validation_receipt"]["sha256"] == sha(CURRENT / "receipts/validation.json")
        and authorization["predecessor_artifact"]["sha256"] == sha(PREDECESSOR / "artifact.json")
        and authorization["predecessor_schema"]["sha256"] == sha(PREDECESSOR / "schema.json")
        and authorization["predecessor_admission_decision"]["sha256"] == sha(PREDECESSOR_DECISION)
        and authorization["non_collapse_audit"]["sha256"]
        == sha(LAB / authorization["non_collapse_audit"]["path"]),
        authorization,
    )
    predecessor_entry = next(
        item for item in predecessor_decision["admitted_artifact_types"]
        if item["artifact_type_ref"] == "cal.artifact-type.coordination-context/v1"
    )
    check(
        "predecessor-was-admitted-current",
        predecessor_decision["status"] == "owner-admitted"
        and predecessor_entry["artifact_sha256"] == sha(PREDECESSOR / "artifact.json")
        and predecessor_entry["schema_sha256"] == sha(PREDECESSOR / "schema.json"),
        predecessor_entry,
    )
    check(
        "package-validation-pass",
        package_receipt["result"] == "PASS"
        and package_receipt["summary"] == {
            "failed": 0, "hostile_cases": 18, "lifecycle_cases": 6,
            "passed": 14, "positive_cases": 4, "total": 14,
        },
        package_receipt["summary"],
    )
    check(
        "definition-binding-admitted-current",
        all(binding["admission_posture"] == "admitted" for binding in artifact["semantic_definition_bindings"]),
        artifact["semantic_definition_bindings"],
    )
    lifecycle = admission["lifecycle"]
    check(
        "single-current-lifecycle",
        lifecycle["current"]["artifact_type_ref"] == "cal.artifact-type.coordination-context/v2"
        and lifecycle["current"]["lifecycle_state"] == "admitted-current"
        and lifecycle["predecessor"]["artifact_type_ref"] == "cal.artifact-type.coordination-context/v1"
        and lifecycle["predecessor"]["previous_lifecycle_state"] == "admitted-current"
        and lifecycle["predecessor"]["lifecycle_state"] == "admitted-historical",
        lifecycle,
    )
    check(
        "relation-authority-separated",
        admission["relation_endpoint_pairs_admitted"] == 0
        and artifact["relation_projection_contract"]["admission_posture"] == "candidate-endpoint-extensions-required"
        and decision["admission_result"]["relation_endpoint_pairs_admitted"] == 0,
        artifact["relation_projection_contract"],
    )
    contracts = [item for item in registry["admitted_contracts"] if "coordination-context" in item["artifact_type_ref"]]
    descriptors = [item for item in registry["descriptors"] if "coordination-context" in item["artifact_type_ref"]]
    check(
        "effective-registry-postimage",
        registry["current_by_identity"]["cal.artifact-type.coordination-context"] == "cal.artifact-type.coordination-context/v2"
        and {item["artifact_type_ref"]: item["lifecycle_state"] for item in contracts} == {
            "cal.artifact-type.coordination-context/v1": "admitted-historical",
            "cal.artifact-type.coordination-context/v2": "admitted-current",
        }
        and {item["artifact_type_ref"]: item["effective_state"] for item in descriptors} == {
            "cal.artifact-type.coordination-context/v1": "admitted-historical",
            "cal.artifact-type.coordination-context/v2": "admitted-current",
        },
        {"contracts": contracts, "descriptors": descriptors},
    )
    check(
        "decision-exact",
        decision["decision_id"] == DECISION_ID
        and decision["status"] == "owner-admitted"
        and decision["authorization"]["sha256"] == sha(ROOT / "authorization.json")
        and decision["admission_record"]["sha256"] == sha(ADMISSION)
        and decision["admission_result"] == {
            "artifact_types_admitted": 1,
            "consumer_activations": 0,
            "instances_admitted": 0,
            "predecessors_transitioned_to_historical": 1,
            "relation_endpoint_pairs_admitted": 0,
            "result": "complete",
        },
        decision["admission_result"],
    )
    failed = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-successor-admission-validation/v1",
        "subject": DECISION_ID,
        "result": "PASS" if not failed else "FAIL",
        "authority_effect": "validation-only",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {
            "authorization_sha256": sha(ROOT / "authorization.json"),
            "decision_sha256": sha(ROOT / "decision.json"),
            "admission_sha256": sha(ADMISSION),
            "artifact_sha256": sha(CURRENT / "artifact.json"),
            "schema_sha256": sha(CURRENT / "schema.json"),
            "package_validation_sha256": sha(CURRENT / "receipts/validation.json"),
            "effective_registry_sha256": sha(REGISTRY),
        },
        "claim_ceiling": "PASS proves the exact Coordination Context/v2 successor admission and v1 historical transition. It does not admit an instance, relation endpoint extension, projection, consumer, implementation, or runtime.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"COORDINATION_CONTEXT_V2_SUCCESSOR_ADMISSION={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

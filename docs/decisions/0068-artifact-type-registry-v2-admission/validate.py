#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
PACKAGE = LAB / "authority/artifact-types/candidates/0006-effective-state-registry"
ARTIFACT = PACKAGE / "artifact-type-candidate.json"
SCHEMA = PACKAGE / "schema.json"
INSTANCE = PACKAGE / "registry.json"
SOURCE_RECEIPT = PACKAGE / "receipts/validation.json"
ADMISSION = LAB / "authority/artifact-types/admissions/artifact-surface/v2/artifact-type-registry.json"
DECISION_ID = "CAL-DECISION-0068-ARTIFACT-TYPE-REGISTRY-V2-ADMISSION"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    authorization = load(ROOT / "authorization.json")
    decision = load(ROOT / "decision.json")
    admission = load(ADMISSION)
    artifact = load(ARTIFACT)
    instance = load(INSTANCE)
    source_receipt = load(SOURCE_RECEIPT)
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    exact_materials = {
        "artifact_type_contract": ARTIFACT,
        "schema": SCHEMA,
        "initial_registry_instance": INSTANCE,
        "candidate_envelope": PACKAGE / "candidate.json",
        "content_audit": PACKAGE / "content-audit.json",
        "hostile_matrix": PACKAGE / "hostile-cases.json",
        "review": PACKAGE / "REVIEW.md",
        "validation_receipt": SOURCE_RECEIPT,
    }
    check(
        "authorization-binds-reviewed-envelope",
        all(authorization[name]["sha256"] == sha(path) for name, path in exact_materials.items()),
        {name: authorization[name] for name in exact_materials},
    )
    check(
        "source-validation-pass",
        source_receipt["result"] == "PASS"
        and source_receipt["summary"] == {"failed": 0, "passed": 23, "total": 23}
        and next(item for item in source_receipt["checks"] if item["check_id"] == "hostile-structure-matrix")["result"] == "PASS",
        source_receipt["summary"],
    )
    check(
        "artifact-type-contract-exact",
        artifact["artifact_type_ref"] == "cal.artifact-type.artifact-type-registry/v2"
        and artifact["version"] == "2.0.0-candidate.2"
        and artifact["schema_digest"] == sha(SCHEMA)
        and all(binding["admission_posture"] == "admitted" for binding in artifact["semantic_definition_bindings"]),
        {"artifact_type_ref": artifact["artifact_type_ref"], "version": artifact["version"], "schema_digest": artifact["schema_digest"]},
    )
    lineage = [item for item in instance["descriptors"] if item["artifact_type_id"] == "cal.artifact-type.artifact-type-registry"]
    check(
        "predecessor-remains-unadmitted-lineage",
        len(lineage) == 2
        and all(item["artifact_type_ref"] == "cal.artifact-type.artifact-type-registry/v1" and item["effective_state"] == "candidate-unadmitted" for item in lineage)
        and admission["predecessor_posture"]["transitioned_to_historical"] is False,
        lineage,
    )
    check(
        "exact-initial-instance-admitted",
        admission["initial_instance"]["registry_id"] == instance["registry_id"]
        and admission["initial_instance"]["registry"]["sha256"] == sha(INSTANCE)
        and admission["initial_instance"]["descriptor_count"] == 56
        and admission["initial_instance"]["admitted_contract_count"] == 33
        and admission["initial_instance"]["lifecycle_state"] == "admitted-current",
        admission["initial_instance"],
    )
    check(
        "bootstrap-snapshot-preserved",
        instance["current_by_identity"].get("cal.artifact-type.artifact-type-registry") is None
        and all(item["path"] != "docs/decisions/0068-artifact-type-registry-v2-admission/decision.json" for item in instance["overlay_sources"])
        and decision["transaction_model"]["bootstrap_self_inclusion_deferred"] is True,
        {"registry_sha256": sha(INSTANCE), "overlay_count": len(instance["overlay_sources"])},
    )
    check(
        "scope-separation",
        admission["other_artifact_type_admissions"] == 0
        and admission["consumer_activations"] == 0
        and decision["admission_result"]["other_artifact_types_admitted"] == 0,
        decision["admission_result"],
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
            "other_artifact_types_admitted": 0,
            "predecessors_transitioned_to_historical": 0,
            "registry_instances_admitted": 1,
            "result": "complete",
        },
        decision["admission_result"],
    )
    failed = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-registry-admission-validation/v1",
        "subject": DECISION_ID,
        "result": "PASS" if not failed else "FAIL",
        "authority_effect": "validation-only",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {
            "authorization_sha256": sha(ROOT / "authorization.json"),
            "decision_sha256": sha(ROOT / "decision.json"),
            "admission_sha256": sha(ADMISSION),
            "artifact_type_contract_sha256": sha(ARTIFACT),
            "schema_sha256": sha(SCHEMA),
            "initial_registry_instance_sha256": sha(INSTANCE),
            "source_validation_sha256": sha(SOURCE_RECEIPT),
        },
        "claim_ceiling": "PASS proves the exact Registry/v2 contract and initial snapshot admission. It does not admit another Artifact Type or instance, update the admitted snapshot, activate a consumer, or grant runtime authority.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"ARTIFACT_TYPE_REGISTRY_V2_ADMISSION={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

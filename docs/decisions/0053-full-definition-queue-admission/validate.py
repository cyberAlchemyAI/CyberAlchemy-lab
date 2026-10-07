#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
BUNDLE = LAB / "docs/admission-bundles/0005-full-definition-queue-v1"
DECISION_ID = "CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    auth = load(HERE / "authorization.json")
    decision = load(HERE / "decision.json")
    receipt = load(HERE / "receipts/admission-validation.json")
    manifest = load(BUNDLE / "manifest.json")
    registry = load(LAB / "authority/definitions/registry.json")
    drift = load(LAB / "authority/definitions/drift-audit.json")
    source_admissions = load(LAB / "authority/decisions/source-admission/full-definition-queue/v1/admissions.json")
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "ok": ok, "detail": detail})

    check("authorization-bound", sha(BUNDLE / "manifest.json") == auth["manifest"]["sha256"] and sha(BUNDLE / "receipts/validation.json") == auth["validation_receipt"]["sha256"], auth["status"])
    check("decision-owner-admitted", decision.get("status") == "owner-admitted" and decision.get("decision_id") == DECISION_ID, decision.get("status"))
    check("decision-inputs-bound", decision["selection"]["manifest_sha256"] == sha(BUNDLE / "manifest.json") and decision["selection"]["validation_receipt_sha256"] == sha(BUNDLE / "receipts/validation.json"), decision["selection"])
    for item in manifest["postimages"]:
        source = BUNDLE / item["path"]
        target = LAB / item["target_path"]
        check(f"postimage:{item['target_path']}", source.is_file() and target.is_file() and sha(source) == sha(target) == item["sha256"], sha(target) if target.is_file() else "missing")

    promoted = [item for item in registry["entries"] if item.get("admission_decision_ref") == DECISION_ID]
    check("definition-registry-closure", len(registry["entries"]) == 118 and len(registry["current_lookup"]) == 112 and len(promoted) == 85, {"versions": len(registry["entries"]), "current": len(registry["current_lookup"]), "promoted": len(promoted)})
    check("reconstructed-closure", sum(item["path"].startswith("evidence/migrations/") for item in promoted) == 70, sum(item["path"].startswith("evidence/migrations/") for item in promoted))
    historical = sum(item["source_state"] == "historical-snapshot" for item in source_admissions["admissions"])
    check("source-selection-closure", source_admissions["status"] == "owner-admitted" and len(source_admissions["admissions"]) == 58 and historical == 1, {"status": source_admissions["status"], "count": len(source_admissions["admissions"]), "historical_snapshots": historical})
    check("successors-current", all(registry["current_lookup"][key].endswith("@1.0.0-candidate.2") for key in ["cal.definition.artifact-surface-classification", "cal.definition.artifact-type-request", "cal.definition.artifact-type-resolution", "cal.definition.canonical-package-manifest"]), "four candidate.2 selections")
    check("queue-empty", drift["summary"]["remaining_unadmitted_definition_versions_in_indexed_queue"] == 0, drift["summary"])
    check("admission-counts", decision["admission_result"] == {"result": "complete", "definitions_admitted": 85, "definition_identities_added": 81, "reconstructed_definitions_admitted": 70, "source_selections_admitted": 58, "historical_source_snapshot_selections": 1, "canonical_definition_versions": 118, "current_definition_terms": 112, "remaining_unadmitted_definition_versions_in_indexed_queue": 0, "consumer_activations": 0}, decision["admission_result"])
    check("transaction-receipt-pass", receipt.get("result") == "PASS" and receipt["materials"]["decision_sha256"] == sha(HERE / "decision.json"), receipt.get("result"))
    check("generated-projections-present", all((HERE / relative).is_file() for relative in ["AUTHORIZATION.md", "DECISION.md", "receipts/ADMISSION-VALIDATION.md"]), "authorization, decision, and receipt projections")

    failed = [item for item in checks if not item["ok"]]
    print(f"FULL_DEFINITION_QUEUE_ADMISSION_VALIDATION={'BLOCK' if failed else 'PASS'}")
    print(f"CHECKS={len(checks)-len(failed)}/{len(checks)}")
    for item in failed:
        print(f"BLOCK {item['check_id']}: {item['detail']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

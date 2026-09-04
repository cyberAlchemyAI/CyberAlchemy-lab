#!/usr/bin/env python3
"""Independently validate decision 0029 and its exact installed postimages."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
BUNDLE = LAB / "docs/admission-bundles/0002-cml07-semantic-foundation-v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    authorization = load(ROOT / "authorization.json")
    decision = load(ROOT / "decision.json")
    receipt = load(ROOT / "receipts/admission-validation.json")
    manifest = load(BUNDLE / "manifest.json")
    checks = []

    def check(check_id, ok, detail):
        checks.append((check_id, ok, detail))

    check("authorization-bound", sha(BUNDLE / "manifest.json") == authorization["manifest"]["sha256"] and sha(BUNDLE / "receipts/validation.json") == authorization["validation_receipt"]["sha256"], authorization["selection_token"])
    check("decision-owner-admitted", decision.get("status") == "owner-admitted", decision.get("status"))
    check("decision-manifest-bound", decision["selection"]["manifest_sha256"] == sha(BUNDLE / "manifest.json"), sha(BUNDLE / "manifest.json"))
    check("decision-receipt-bound", decision["selection"]["validation_receipt_sha256"] == sha(BUNDLE / "receipts/validation.json") and load(BUNDLE / "receipts/validation.json")["result"] == "PASS", sha(BUNDLE / "receipts/validation.json"))
    for item in manifest["postimages"]:
        parts = Path(item["path"]).parts
        source = BUNDLE / item["path"]
        target = LAB.joinpath(*parts[1:])
        check(f"postimage:{target.relative_to(LAB)}", source.is_file() and target.is_file() and sha(source) == sha(target) == item["sha256"], sha(target) if target.is_file() else "missing")
    registry = load(LAB / "authority/definitions/registry.json")
    promoted = [x for x in registry["entries"] if x.get("admission_decision_ref") == decision["decision_id"]]
    check("definition-registry-closure", len(registry["entries"]) == 32 and len(registry["current_lookup"]) == 30 and len(promoted) == 14, {"entries": len(registry["entries"]), "current": len(registry["current_lookup"]), "promoted": len(promoted)})
    owners = load(LAB / "authority/owners/foundation-01/v1/candidates/0004-craft-identity/owners.json")
    roles = [x["role_id"] for x in owners["role_assignments"]]
    check("owner-registry-closure", len(roles) == len(set(roles)) == 20, roles)
    check("artifact-type-v2-bound", sha(LAB / decision["admitted_artifact_type"]["path"]) == decision["admitted_artifact_type"]["sha256"], decision["admitted_artifact_type"])
    check("successor-chain-bound", sha(LAB / decision["selected_chain"]["path"]) == decision["selected_chain"]["sha256"], decision["selected_chain"])
    check("admission-counts", decision["admission_result"] == {"result": "complete-cml07-pre-s2-semantic-foundation-admission", "decision_requests_admitted": 8, "source_selections_admitted": 11, "owner_bindings_admitted": 4, "definitions_admitted": 14, "canonical_definition_versions": 32, "current_definition_terms": 30, "artifact_types_admitted": 1, "selected_construction_chains": 1, "identity_carriers_admitted": 0, "implementation_bindings_accepted": 0, "s2_posture": "evaluable-not-executed"}, decision["admission_result"])
    check("transaction-receipt-pass", receipt.get("result") == "PASS" and receipt["materials"]["decision_sha256"] == sha(ROOT / "decision.json"), receipt.get("result"))
    check("generated-projections-present", (ROOT / "AUTHORIZATION.md").is_file() and (ROOT / "DECISION.md").is_file() and (ROOT / "receipts/ADMISSION-VALIDATION.md").is_file(), "authorization, decision, and receipt projections present")
    failed = [item for item in checks if not item[1]]
    print(f"CML07_SEMANTIC_FOUNDATION_ADMISSION_VALIDATION={'BLOCK' if failed else 'PASS'}")
    print(f"CHECKS={len(checks)-len(failed)}/{len(checks)}")
    for check_id, _, detail in failed:
        print(f"BLOCK {check_id}: {detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

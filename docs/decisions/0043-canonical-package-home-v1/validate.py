#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
BUNDLE = LAB / "docs/admission-bundles/0003-canonical-package-home-v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    auth = load(ROOT / "authorization.json")
    decision = load(ROOT / "decision.json")
    receipt = load(ROOT / "receipts/admission-validation.json")
    manifest = load(BUNDLE / "manifest.json")
    checks = []
    def check(check_id, ok, detail):
        checks.append((check_id, ok, detail))
    check("authorization-bound", sha(BUNDLE / "manifest.json") == auth["manifest"]["sha256"] and sha(BUNDLE / "receipts/validation.json") == auth["validation_receipt"]["sha256"], auth["selection_token"])
    check("decision-owner-admitted", decision.get("status") == "owner-admitted", decision.get("status"))
    check("decision-inputs-bound", decision["selection"]["manifest_sha256"] == sha(BUNDLE / "manifest.json") and decision["selection"]["validation_receipt_sha256"] == sha(BUNDLE / "receipts/validation.json"), decision["selection"])
    for item in manifest["postimages"]:
        source = BUNDLE / item["path"]
        target = LAB.joinpath(*Path(item["path"]).parts[1:])
        check(f"postimage:{target.relative_to(LAB)}", source.is_file() and target.is_file() and sha(source) == sha(target) == item["sha256"], sha(target) if target.is_file() else "missing")
    registry = load(LAB / "authority/definitions/registry.json")
    promoted = [x for x in registry["entries"] if x.get("admission_decision_ref") == decision["decision_id"]]
    check("definition-registry-closure", len(registry["entries"]) == 33 and len(registry["current_lookup"]) == 31 and len(promoted) == 1 and promoted[0]["definition_id"] == "cal.definition.canonical-package-home", {"entries": len(registry["entries"]), "current": len(registry["current_lookup"]), "promoted": len(promoted)})
    check("admission-counts", decision["admission_result"] == {"result": "complete", "source_selections_admitted": 5, "definitions_admitted": 1, "canonical_definition_versions": 33, "current_definition_terms": 31, "artifact_types_admitted": 0, "registry_context_migrations": 0}, decision["admission_result"])
    check("transaction-receipt-pass", receipt.get("result") == "PASS" and receipt["materials"]["decision_sha256"] == sha(ROOT / "decision.json"), receipt.get("result"))
    check("generated-projections-present", all((ROOT / x).is_file() for x in ["AUTHORIZATION.md", "DECISION.md", "receipts/ADMISSION-VALIDATION.md"]), "authorization, decision, and receipt projections")
    failed = [x for x in checks if not x[1]]
    print(f"CANONICAL_PACKAGE_HOME_ADMISSION_VALIDATION={'BLOCK' if failed else 'PASS'}")
    print(f"CHECKS={len(checks)-len(failed)}/{len(checks)}")
    for check_id, _, detail in failed:
        print(f"BLOCK {check_id}: {detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

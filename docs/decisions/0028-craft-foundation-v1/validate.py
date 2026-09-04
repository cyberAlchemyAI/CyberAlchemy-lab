#!/usr/bin/env python3
"""Independently revalidate the admitted Craft foundation decision."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
BUNDLE = LAB / "docs/admission-bundles/0001-craft-foundation-v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    decision = load(ROOT / "decision.json")
    receipt = load(ROOT / "receipts/admission-validation.json")
    manifest = load(BUNDLE / "manifest.json")
    checks = []

    def check(name, ok, detail):
        checks.append((name, ok, detail))

    check("decision-owner-admitted", decision.get("status") == "owner-admitted", decision.get("status"))
    check("manifest-bound", decision["selection"]["manifest_sha256"] == sha(BUNDLE / "manifest.json"), sha(BUNDLE / "manifest.json"))
    check("bundle-receipt-bound", decision["selection"]["validation_receipt_sha256"] == sha(BUNDLE / "receipts/validation.json") and load(BUNDLE / "receipts/validation.json")["result"] == "PASS", decision["selection"]["validation_receipt_sha256"])
    for item in manifest["postimages"]:
        rel = Path(item["path"])
        source = BUNDLE / rel
        target = LAB.joinpath(*rel.parts[1:])
        check(f"postimage:{target.relative_to(LAB)}", sha(source) == sha(target) == item["sha256"], sha(target))
    registry = load(LAB / "authority/definitions/registry.json")
    check("registry-counts", len(registry["entries"]) == 18 and len(registry["current_lookup"]) == 16, {"entries": len(registry["entries"]), "current": len(registry["current_lookup"])})
    check("decision-counts", decision["admission_result"] == {"result": "complete-craft-foundation-v1-admission", "source_selections_admitted": 5, "owner_bindings_admitted": 1, "definitions_admitted": 8, "canonical_definition_versions": 18, "current_definition_terms": 16, "bounded_contexts_created": 0, "implementation_bindings_accepted": 0}, decision["admission_result"])
    check("transaction-receipt-pass", receipt.get("result") == "PASS" and receipt["materials"]["decision_sha256"] == sha(ROOT / "decision.json"), receipt.get("result"))
    failed = [item for item in checks if not item[1]]
    print(f"CRAFT_FOUNDATION_ADMISSION_VALIDATION={'FAIL' if failed else 'PASS'}")
    print(f"CHECKS={len(checks)-len(failed)}/{len(checks)}")
    for name, _, detail in failed:
        print(f"FAIL {name}: {detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

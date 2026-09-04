#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from candidate_support import composed_registry_postimage

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SHARED = ROOT.parent / "_candidate_pack.py"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hostile(subject: dict) -> set[str]:
    failures: set[str] = set()
    if subject.get("kind") == "validation" and subject.get("result") == "PASS" and subject.get("claims_conformance") is True:
        failures.add("validation-pass-must-not-imply-conformance")
    if subject.get("kind") == "conformance" and subject.get("scope") == "schema" and subject.get("claims_runtime_conformance") is True:
        failures.add("schema-conformance-must-not-imply-runtime-conformance")
    if subject.get("kind") == "artifact-type-registration" and not subject.get("semantic_definition_refs"):
        failures.add("new-artifact-type-must-reference-definitions")
    if subject.get("kind") == "validation-receipt" and subject.get("authority_effect") != "none":
        failures.add("receipt-must-not-carry-authority")
    if subject.get("kind") == "identity-lineage" and subject.get("subject_kind") == "product" and subject.get("uses_context_lineage_as_authority") is True:
        failures.add("context-lineage-must-not-substitute-for-product-lineage")
    return failures


def main() -> int:
    spec = importlib.util.spec_from_file_location("candidate_pack", SHARED)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.registry_postimage = lambda root, candidate: composed_registry_postimage(module, root, candidate)
    module.hostile_failures = hostile
    expected = {
        "cal.definition.artifact-type", "cal.definition.evidence", "cal.definition.evaluation",
        "cal.definition.validation", "cal.definition.conformance", "cal.definition.validation-receipt",
        "cal.definition.identity-carrier", "cal.definition.identity-lineage",
    }
    base = module.validate(ROOT, expected)
    receipt_path = ROOT / "receipts/validation.json"
    receipt = load(receipt_path)
    checks = receipt["checks"]

    def check(check_id: str, ok: bool, detail) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    candidate = load(ROOT / "candidate.json")
    predecessor = candidate["predecessor_candidate"]
    predecessor_path = LAB / predecessor["path"]
    check("candidate-0006-immutable", sha(predecessor_path) == predecessor["sha256"], {"expected": predecessor["sha256"], "actual": sha(predecessor_path)})
    registry = load(ROOT / "registry-postimage.json")
    check("composed-registry-count", len(registry["entries"]) == 32, len(registry["entries"]))
    at2 = LAB / "authority/artifact-types/artifact-type/v2/artifact.json"
    chain2 = LAB / "docs/identity-packs/0002-craft-identity-chain-semantic-closure/chain.json"
    check("artifact-type-v2-consumer-present", at2.is_file(), str(at2))
    if at2.is_file():
        at2_data = load(at2)
        check("artifact-type-v2-binds-definition", "cal.definition.artifact-type@1.0.0-candidate.1" in at2_data["semantic_definition_refs"], at2_data["semantic_definition_refs"])
    check("successor-chain-present", chain2.is_file(), str(chain2))
    if chain2.is_file():
        chain = load(chain2)
        text = json.dumps(chain, sort_keys=True)
        check("successor-chain-uses-closure", candidate["candidate_id"] in text and "schema-and-identity-contract" in text, chain["chain_id"])

    failed = [item for item in checks if item["result"] == "FAIL"]
    receipt["result"] = "PASS" if not failed and base == 0 else "FAIL"
    receipt["summary"] = {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)}
    receipt["promotion_eligibility"] = "blocked-by-declared-dependencies" if receipt["result"] == "PASS" else "not-eligible"
    receipt["claim_ceiling"] = "PASS proves the eight-definition candidate is structurally valid, composes over immutable candidate 0006, rejects the five collapse fixtures, and is referenced by Artifact Type/v2 and successor chain 0002. It does not admit any Definition or authorize S2."
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CML07_SEMANTIC_CLOSURE={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

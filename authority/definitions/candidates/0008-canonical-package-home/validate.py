#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent / "_candidate_pack.py"


def hostile(subject: dict) -> set[str]:
    failures: set[str] = set()
    if subject.get("kind") == "canonical-package-home-selection" and subject.get("selection_basis") == "directory-classification":
        failures.add("directory-must-not-select-canonical-home")
    if subject.get("kind") == "canonical-carrier" and len(subject.get("canonical_home_refs", [])) != 1:
        failures.add("canonical-carrier-must-have-one-home")
    if subject.get("kind") == "global-index" and subject.get("duplicates_canonical_carrier") is True:
        failures.add("index-must-not-duplicate-canonical-carrier")
    if subject.get("kind") == "colocation" and subject.get("collapses_semantic_identities") is True:
        failures.add("colocation-must-not-collapse-identities")
    return failures


def main() -> int:
    spec = importlib.util.spec_from_file_location("candidate_pack", SHARED)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.hostile_failures = hostile
    result = module.validate(ROOT, {"cal.definition.canonical-package-home"})
    receipt_path = ROOT / "receipts/validation.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "registry-postimage.json").read_text(encoding="utf-8"))
    checks = receipt["checks"]
    count_ok = len(registry["entries"]) == 33
    checks.append({
        "check_id": "successor-registry-count",
        "result": "PASS" if count_ok else "FAIL",
        "detail": {"expected": 33, "actual": len(registry["entries"])}
    })
    failed = [item for item in checks if item["result"] == "FAIL"]
    receipt["result"] = "PASS" if result == 0 and not failed else "FAIL"
    receipt["summary"] = {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)}
    receipt["promotion_eligibility"] = "blocked-by-declared-dependencies" if receipt["result"] == "PASS" else "not-eligible"
    receipt["claim_ceiling"] = "PASS proves the one-Definition candidate is structurally valid, source-current, projection-deterministic, registry-synchronized, and rejects the four package-home collapse fixtures. It does not admit the Definition, select a Registry Context home, alter an Artifact Type, or move files."
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CANONICAL_PACKAGE_HOME={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

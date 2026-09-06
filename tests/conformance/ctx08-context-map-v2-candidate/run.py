#!/usr/bin/env python3
"""Run deterministic conformance for the additive v2 Context Map prototype."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
VALIDATOR = LAB / "docs/context-packs/0004-governance-ontology-lifecycle-v2-map/validate.py"
RECEIPT = HERE / "receipts/last-run.json"


def load_module():
    spec = importlib.util.spec_from_file_location("ctxmap2_validator", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def main() -> int:
    module = load_module()
    first = module.run(write_outputs=True)
    first_bytes = canonical_bytes(first)
    second = module.run(write_outputs=True)
    second_bytes = canonical_bytes(second)
    deterministic = first_bytes == second_bytes
    validation_pass = first.get("result") == second.get("result") == "PASS"
    hostile_pass = first.get("hostile_probes_passed") == first.get("hostile_probes_total") == 6
    product_state = first.get("product_state") == "testable-prototype-pass"
    no_authority = first.get("product_approval") == "not-requested" and first.get("authority_effect") == "none"
    v1_preserved = next(
        item for item in first["checks"] if item["check_id"] == "admitted-v1-map-byte-preserved"
    )["result"] == "PASS"
    tests = [
        {"test_id": "validation-pass", "result": "PASS" if validation_pass else "FAIL"},
        {"test_id": "two-run-determinism", "result": "PASS" if deterministic else "FAIL"},
        {"test_id": "hostile-probes", "result": "PASS" if hostile_pass else "FAIL"},
        {"test_id": "v1-predecessor-preserved", "result": "PASS" if v1_preserved else "FAIL"},
        {"test_id": "testable-prototype-state", "result": "PASS" if product_state else "FAIL"},
        {"test_id": "no-product-approval-or-authority", "result": "PASS" if no_authority else "FAIL"},
    ]
    passed = all(item["result"] == "PASS" for item in tests)
    receipt = {
        "schema_version": "cyberalchemy-lab-context-map-v2-conformance/v1",
        "suite_id": "CAL-CONFORMANCE-CTXMAP2-0001",
        "stage_id": "CTXMAP2-S1",
        "result": "PASS" if passed else "FAIL",
        "tests_passed": sum(item["result"] == "PASS" for item in tests),
        "tests_total": len(tests),
        "deterministic_runs": 2,
        "run_digest": hashlib.sha256(first_bytes).hexdigest(),
        "tests": tests,
        "validation_receipt_path": "docs/context-packs/0004-governance-ontology-lifecycle-v2-map/receipts/validation.json",
        "product_state": "tested-prototype-candidate" if passed else "prototype-test-failed",
        "next_product_frontier": "D65-S1" if passed else "CTXMAP2-S1",
        "product_approval": "not-requested",
        "cutover_authorized": False,
        "authority_effect": "none",
        "claim_ceiling": "PASS proves only deterministic, hostile-tested behavior of the additive v2 Context Map prototype with the admitted v1 predecessor preserved. It does not approve, admit, activate, migrate, cut over, publish, release, deploy, or authorize an external effect."
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTXMAP2_CONFORMANCE={receipt['result']}")
    print(f"TESTS={receipt['tests_passed']}/{receipt['tests_total']}")
    print(f"NEXT_PRODUCT_FRONTIER={receipt['next_product_frontier']}")
    print("PRODUCT_APPROVAL=not-requested")
    print("AUTHORITY_EFFECT=none")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

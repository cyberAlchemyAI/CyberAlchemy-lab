#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    plan = load(ROOT / "plan.json")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    predecessor = plan["predecessor"]
    predecessor_actual = {
        "candidate": sha(LAB / predecessor["candidate_ref"]),
        "receipt": sha(LAB / predecessor["test_receipt_ref"]),
    }
    check(
        "P6-01-PREDECESSOR-BINDING",
        predecessor_actual["candidate"] == predecessor["candidate_sha256"]
        and predecessor_actual["receipt"] == predecessor["test_receipt_sha256"],
        predecessor_actual,
    )

    product_receipt = load(
        LAB / "product/products/ontology/v1/product-tests/epoch-001/receipts/validation.json"
    )
    candidate_receipt = load(
        LAB / "product/products/ontology/v1/candidates/0004-first-stable/receipts/validation.json"
    )
    check(
        "P6-02-COLLECT-ALL-PRODUCT-EVIDENCE",
        product_receipt["result"] == candidate_receipt["result"] == "PASS"
        and product_receipt["summary"]["passed"] == 9
        and product_receipt["summary"]["rust_product_tests"] == 9,
        {"product_test": product_receipt["summary"], "candidate": candidate_receipt["summary"]},
    )

    check(
        "P6-03-DONE-CRITERIA-COVERAGE",
        len(plan["product_construction"]["done_criteria"]) == 10
        and len(product_receipt["capabilities_proved"]) == 10,
        product_receipt["capabilities_proved"],
    )
    expected_scope = {
        "docs/migration-plans/0006-ontology-product-first-stable-candidate-v1/**",
        "product/products/ontology/v1/product-tests/epoch-001/**",
        "product/products/ontology/v1/candidates/0004-first-stable/**",
    }
    check("P6-04-EXACT-WRITE-SCOPE", set(plan["write_scope"]) == expected_scope, plan["write_scope"])

    operational = plan["operational_support"]
    check(
        "P6-05-TWO-LANE-SEPARATION",
        len(operational) == 3
        and sum(item["blocking_posture"] == "deferred" for item in operational) == 2
        and sum(item["blocking_posture"] == "non-blocking for exact successor-only construction" for item in operational) == 1,
        operational,
    )
    boundary = plan["approval_boundary"]
    check(
        "P6-06-SINGLE-PRODUCT-APPROVAL-BOUNDARY",
        boundary["mode"] == "single-final-product-boundary"
        and boundary["effect_if_approved"] == "Product approval only"
        and len(boundary["not_granted"]) == 11
        and candidate_receipt["product_approval"]["eligible"]
        and not candidate_receipt["product_approval"]["granted"],
        {"boundary": boundary, "candidate_product_approval": candidate_receipt["product_approval"]},
    )
    check(
        "P6-07-NO-AUTHORITY-EFFECT",
        plan["authority_effect"] == product_receipt["authority_effect"] == candidate_receipt["authority_effect"] == "none",
        "plan and all L4 receipts retain authority_effect none",
    )

    generator_path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("plan_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    projection = ROOT / "PLAN.md"
    check(
        "P6-08-PROJECTION-PARITY",
        projection.is_file() and projection.read_text(encoding="utf-8") == module.render(plan),
        sha(projection) if projection.is_file() else "missing",
    )
    check(
        "P6-09-PLAN-TO-RESULT-CLOSURE",
        plan["status"] == "implemented-and-tested"
        and candidate_receipt["candidate_id"] == "CAL-ONTOLOGY-AS-PRODUCT-CANDIDATE-0004"
        and candidate_receipt["construction_stage"] == plan["execution_unit"]["construction_stage"],
        {
            "plan_status": plan["status"],
            "candidate_id": candidate_receipt["candidate_id"],
            "construction_stage": candidate_receipt["construction_stage"],
        },
    )

    failures = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-product-l4-plan-validation/v1",
        "plan_id": plan["plan_id"],
        "result": "PASS" if not failures else "FAIL",
        "authority_effect": "none",
        "summary": {"passed": len(checks) - len(failures), "failed": len(failures), "total": len(checks)},
        "implementation_receipts": {
            "product_test": "product/products/ontology/v1/product-tests/epoch-001/receipts/validation.json",
            "candidate": "product/products/ontology/v1/candidates/0004-first-stable/receipts/validation.json",
        },
        "boundary": "One Product approval decision is now eligible against the exact candidate and receipt digests; it has not been granted.",
        "claim_ceiling": "PASS proves plan-to-result closure for this exact private L4 construction unit. It does not approve the Product or grant any lifecycle or operational authority.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": receipt["result"], "summary": receipt["summary"]}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

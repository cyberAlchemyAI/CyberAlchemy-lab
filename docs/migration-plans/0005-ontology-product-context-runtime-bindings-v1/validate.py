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
    predecessor_path = LAB / predecessor["candidate_ref"]
    check("P5-01-PREDECESSOR-BINDING", predecessor_path.is_file() and sha(predecessor_path) == predecessor["candidate_sha256"], sha(predecessor_path) if predecessor_path.is_file() else "missing")
    coordination_receipt = load(LAB / "coordination/contexts/ontology-product/v1/receipts/validation.json")
    binding_receipt = load(LAB / "implementation/bindings/ontology-product-lifecycle/v1/receipts/validation.json")
    candidate_receipt = load(LAB / "product/products/ontology/v1/candidates/0003-context-runtime-evolution/receipts/validation.json")
    check("P5-02-IMPLEMENTATION-EVIDENCE", coordination_receipt["result"] == binding_receipt["result"] == candidate_receipt["result"] == "PASS", {"coordination": coordination_receipt["result"], "binding": binding_receipt["result"], "candidate": candidate_receipt["result"]})
    check("P5-03-DONE-CRITERIA-COVERAGE", len(plan["product_construction"]["done_criteria"]) == 8 and binding_receipt["summary"]["rust_product_tests"] == 5 and set(binding_receipt["capabilities_proved"]) == {"evolution", "replay", "checkpoint-recovery", "context-observation", "runtime-replacement", "hostile-chain-rejection"}, binding_receipt["capabilities_proved"])
    expected_scope = {"docs/migration-plans/0005-ontology-product-context-runtime-bindings-v1/**", "coordination/contexts/ontology-product/v1/**", "implementation/bindings/ontology-product-lifecycle/v1/**", "product/products/ontology/v1/candidates/0003-context-runtime-evolution/**"}
    check("P5-04-EXACT-WRITE-SCOPE", set(plan["write_scope"]) == expected_scope, plan["write_scope"])
    operational = plan["operational_support"]
    check("P5-05-TWO-LANE-SEPARATION", len(operational) == 3 and sum(item["blocking_posture"] == "deferred" for item in operational) == 2 and sum(item["blocking_posture"] == "non-blocking for Product construction" for item in operational) == 1, operational)
    boundary = plan["approval_boundary"]
    check("P5-06-SINGLE-FINAL-APPROVAL-BOUNDARY", boundary["mode"] == "single-final-product-boundary" and not boundary["current_increment_requires_approval"] and boundary["eligible_after"] == "L4-FIRST-TESTABLE-ONTOLOGY-AS-PRODUCT-CANDIDATE" and len(boundary["not_granted"]) == 11, boundary)
    check("P5-07-NO-AUTHORITY-EFFECT", plan["authority_effect"] == coordination_receipt["authority_effect"] == binding_receipt["authority_effect"] == candidate_receipt["authority_effect"] == "none", "plan and all L3 receipts retain authority_effect none")

    generator_path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("plan_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    projection = ROOT / "PLAN.md"
    check("P5-08-PROJECTION-PARITY", projection.is_file() and projection.read_text(encoding="utf-8") == module.render(plan), sha(projection) if projection.is_file() else "missing")
    check("P5-09-NEXT-FRONTIER", candidate_receipt["next_product_frontier"]["stage"] == "L4-FIRST-TESTABLE-ONTOLOGY-AS-PRODUCT-CANDIDATE" and not candidate_receipt["next_product_frontier"]["approval_eligible"], candidate_receipt["next_product_frontier"])

    failures = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-product-l3-plan-validation/v1",
        "plan_id": plan["plan_id"],
        "result": "PASS" if not failures else "FAIL",
        "authority_effect": "none",
        "summary": {"passed": len(checks) - len(failures), "failed": len(failures), "total": len(checks)},
        "checks": checks,
        "implementation_receipts": {
            "coordination_context": "coordination/contexts/ontology-product/v1/receipts/validation.json",
            "runtime_binding": "implementation/bindings/ontology-product-lifecycle/v1/receipts/validation.json",
            "candidate": "product/products/ontology/v1/candidates/0003-context-runtime-evolution/receipts/validation.json"
        },
        "next_product_frontier": candidate_receipt["next_product_frontier"],
        "claim_ceiling": "PASS proves plan-to-implementation closure for the exact private L3 construction increment. It does not approve the Product or grant admission, adoption, activation, cutover, publication, release, deployment, or source-retirement authority."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

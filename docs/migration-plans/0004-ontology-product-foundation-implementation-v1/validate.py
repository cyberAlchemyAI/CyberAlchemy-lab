#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE_REPO = Path("/home/vrondelli/projects/domainspec-core")
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    plan = load(ROOT / "plan.json")
    predecessor = plan["predecessor"]
    predecessor_candidate = LAB / predecessor["candidate_ref"]
    check("P4-01-PREDECESSOR-BINDING", predecessor_candidate.is_file() and sha(predecessor_candidate) == predecessor["candidate_sha256"], sha(predecessor_candidate) if predecessor_candidate.is_file() else "missing")

    source_rows = []
    source_root = SOURCE_REPO / plan["source_package"]["source_path"]
    for item in plan["source_package"]["files"]:
        path = source_root / item["path"]
        source_rows.append({"path": item["path"], "expected": item["sha256"], "actual": sha(path) if path.is_file() else None})
    check("P4-02-SOURCE-EPOCH", all(row["expected"] == row["actual"] for row in source_rows), source_rows)

    source_receipt = load(LAB / "product/products/ontology/v1/product-ontology/source-package/receipts/validation.json")
    artifact_receipt = load(LAB / "authority/artifact-types/ontology-package/v1/receipts/validation.json")
    candidate_receipt = load(LAB / "product/products/ontology/v1/candidates/0002-source-preserving-foundation/receipts/validation.json")
    check("P4-03-IMPLEMENTATION-EVIDENCE", source_receipt["result"] == artifact_receipt["result"] == candidate_receipt["result"] == "PASS", {"source_package": source_receipt["result"], "artifact_type": artifact_receipt["result"], "candidate": candidate_receipt["result"]})

    done = plan["product_construction"]["done_criteria"]
    check("P4-04-DONE-CRITERIA-COVERAGE", len(done) == 7 and source_receipt["summary"]["drift_reconciliations"] == 3 and source_receipt["summary"]["nodes"] == 23 and source_receipt["summary"]["relations"] == 24 and artifact_receipt["summary"]["hostile_fixtures"] == 3, {"criteria": len(done), "source_checks": source_receipt["summary"], "artifact_checks": artifact_receipt["summary"]})

    operational = plan["operational_support"]
    construction_separation = plan["product_construction"]["frontier"] and len(operational) == 3 and any(item["blocking_posture"] == "next construction frontier" for item in operational) and any(item["blocking_posture"] == "deferred" for item in operational)
    check("P4-05-TWO-LANE-SEPARATION", bool(construction_separation), operational)

    boundary = plan["approval_boundary"]
    check("P4-06-SINGLE-FINAL-APPROVAL-BOUNDARY", boundary["mode"] == "single-final-product-boundary" and not boundary["current_increment_requires_approval"] and len(boundary["not_granted"]) == 10, boundary)

    no_effect = plan["authority_effect"] == source_receipt["authority_effect"] == artifact_receipt["authority_effect"] == candidate_receipt["authority_effect"] == "none"
    check("P4-07-NO-AUTHORITY-EFFECT", no_effect, "plan and all implementation receipts retain authority_effect none")

    generator_path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("plan_generator", generator_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    view = ROOT / "PLAN.md"
    check("P4-08-PROJECTION-PARITY", view.is_file() and view.read_text(encoding="utf-8") == module.render(plan), sha(view) if view.is_file() else "missing")

    failures = [row for row in checks if row["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-product-foundation-plan-validation/v1",
        "plan_id": plan["plan_id"],
        "result": "PASS" if not failures else "FAIL",
        "authority_effect": "none",
        "summary": {"passed": len(checks) - len(failures), "failed": len(failures), "total": len(checks)},
        "checks": checks,
        "implementation_receipts": {
            "source_package": "product/products/ontology/v1/product-ontology/source-package/receipts/validation.json",
            "artifact_type": "authority/artifact-types/ontology-package/v1/receipts/validation.json",
            "candidate": "product/products/ontology/v1/candidates/0002-source-preserving-foundation/receipts/validation.json"
        },
        "next_product_frontier": candidate_receipt["next_product_frontier"],
        "claim_ceiling": "PASS proves plan-to-implementation closure for this exact private construction increment and identifies the next Product frontier. It does not approve the Product or grant admission, activation, cutover, publication, release, deployment, or source-retirement authority."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[5]
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    candidate = load(ROOT / "candidate.json")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    predecessor = candidate["predecessor"]
    predecessor_actual = {
        "candidate": sha(LAB / predecessor["candidate_ref"]),
        "receipt": sha(LAB / predecessor["test_receipt_ref"]),
    }
    check(
        "C4-01-PREDECESSOR-IMMUTABLE",
        predecessor_actual["candidate"] == predecessor["candidate_sha256"]
        and predecessor_actual["receipt"] == predecessor["test_receipt_sha256"],
        predecessor_actual,
    )

    material = []
    for relative in candidate["material_paths"]:
        path = LAB / relative
        material.append({
            "path": relative,
            "exists": path.is_file(),
            "sha256": sha(path) if path.is_file() else None,
            "size": path.stat().st_size if path.is_file() else None,
        })
    check(
        "C4-02-MATERIAL-CLOSURE",
        len(material) == len({item["path"] for item in material}) == 18
        and all(item["exists"] for item in material),
        {"count": len(material), "missing": [item["path"] for item in material if not item["exists"]]},
    )

    evidence = candidate["product_test_evidence"]
    evidence_path = LAB / evidence["receipt_ref"]
    product_receipt = load(evidence_path)
    check(
        "C4-03-EXACT-PRODUCT-TEST-EVIDENCE",
        sha(evidence_path) == evidence["receipt_sha256"]
        and product_receipt["result"] == evidence["result"] == "PASS"
        and product_receipt["summary"]["passed"] == evidence["structural_checks"] == 9
        and product_receipt["summary"]["rust_product_tests"] == evidence["rust_product_tests"] == 9,
        {
            "receipt_sha256": sha(evidence_path),
            "result": product_receipt["result"],
            "summary": product_receipt["summary"],
        },
    )
    check(
        "C4-04-REAL-SOURCE-AND-PACKAGE-BINDING",
        product_receipt["selected_source_sha256"] == evidence["selected_source_sha256"]
        and product_receipt["package_sha256"] == evidence["package_sha256"]
        and product_receipt["summary"]["nodes"] == evidence["nodes"] == 23
        and product_receipt["summary"]["relations"] == evidence["relations"] == 24
        and product_receipt["summary"]["typed_residue"] == evidence["typed_residue"] == 5,
        evidence,
    )

    plan = load(LAB / candidate["construction_increment"]["plan_ref"])
    check(
        "C4-05-PLAN-AND-STAGE-BINDING",
        plan["status"] == "implemented-and-tested"
        and plan["execution_unit"]["unit_id"] == candidate["construction_increment"]["unit_id"]
        and plan["execution_unit"]["construction_stage"] == candidate["construction_stage"]
        and plan["approval_boundary"]["mode"] == "single-final-product-boundary",
        {"plan_id": plan["plan_id"], "unit": plan["execution_unit"], "status": plan["status"]},
    )
    check(
        "C4-06-CAPABILITY-CLOSURE",
        set(product_receipt["capabilities_proved"]) == {
            "source-to-package-trace",
            "deterministic-package-construction",
            "bounded-retrieval",
            "typed-residue-preservation",
            "evolution",
            "replay",
            "checkpoint-recovery",
            "context-coordination",
            "runtime-replacement",
            "authority-mutation-rejection",
        }
        and len(candidate["acceptance_criteria"]) == 9,
        product_receipt["capabilities_proved"],
    )
    approval = candidate["product_approval"]
    check(
        "C4-07-SINGLE-PRODUCT-APPROVAL-READINESS",
        candidate["status"] == "ready-for-product-approval"
        and approval["eligible"]
        and not approval["granted"]
        and approval["decision_scope"] == "Product approval only"
        and len(approval["not_granted"]) == 11,
        approval,
    )
    check(
        "C4-08-NO-AUTHORITY-OR-HIDDEN-EFFECT",
        candidate["authority_effect"] == product_receipt["authority_effect"] == "none"
        and not product_receipt["product_approval_granted"]
        and len(candidate["operational_residue"]) == 3,
        {
            "authority_effect": candidate["authority_effect"],
            "product_approval_granted": product_receipt["product_approval_granted"],
            "operational_residue": candidate["operational_residue"],
        },
    )

    generator_path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("candidate_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    projection = ROOT / "CANDIDATE.md"
    check(
        "C4-09-PROJECTION-PARITY",
        projection.is_file() and projection.read_text(encoding="utf-8") == module.render(candidate),
        sha(projection) if projection.is_file() else "missing",
    )

    material_digest = hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    failures = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-product-candidate-validation/v1",
        "candidate_id": candidate["candidate_id"],
        "construction_stage": candidate["construction_stage"],
        "result": "PASS" if not failures else "FAIL",
        "authority_effect": "none",
        "candidate_sha256": sha(ROOT / "candidate.json"),
        "material_digest": material_digest,
        "material": material,
        "summary": {
            "passed": len(checks) - len(failures),
            "failed": len(failures),
            "total": len(checks),
            "material_files": len(material),
            "rust_product_tests": product_receipt["summary"]["rust_product_tests"],
        },
        "checks": checks,
        "product_approval": approval,
        "claim_ceiling": "PASS proves this exact immutable private Product candidate is evidence-complete and eligible for one Product approval decision. It does not grant that decision or any lifecycle or operational authority.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": receipt["result"], "summary": receipt["summary"]}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

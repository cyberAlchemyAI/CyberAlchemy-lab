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
    predecessor_candidate = LAB / predecessor["candidate_ref"]
    predecessor_receipt = LAB / predecessor["test_receipt_ref"]
    check("C3-01-PREDECESSOR-IMMUTABLE", sha(predecessor_candidate) == predecessor["candidate_sha256"] and sha(predecessor_receipt) == predecessor["test_receipt_sha256"], {"candidate": sha(predecessor_candidate), "receipt": sha(predecessor_receipt)})

    material = []
    for relative in candidate["material_paths"]:
        path = LAB / relative
        material.append({"path": relative, "exists": path.is_file(), "sha256": sha(path) if path.is_file() else None, "size": path.stat().st_size if path.is_file() else None})
    check("C3-02-MATERIAL-CLOSURE", len(material) == len({item["path"] for item in material}) == 17 and all(item["exists"] for item in material), {"count": len(material), "missing": [item["path"] for item in material if not item["exists"]]})

    coordination_receipt = load(LAB / candidate["evidence_refs"][0])
    binding_receipt = load(LAB / candidate["evidence_refs"][1])
    check("C3-03-L3-EVIDENCE", coordination_receipt["result"] == binding_receipt["result"] == "PASS" and coordination_receipt["summary"]["passed"] == 9 and binding_receipt["summary"]["passed"] == 9 and binding_receipt["summary"]["rust_product_tests"] == 5, {"coordination": coordination_receipt["summary"], "binding": binding_receipt["summary"]})

    plan = load(LAB / candidate["construction_increment"]["plan_ref"])
    check("C3-04-PLAN-BINDING", plan["execution_unit"]["unit_id"] == candidate["construction_increment"]["unit_id"] and plan["approval_boundary"]["mode"] == "single-final-product-boundary", plan["execution_unit"])
    coordination = load(LAB / candidate["construction_increment"]["coordination_context_ref"])
    binding = load(LAB / candidate["construction_increment"]["runtime_binding_ref"])
    expected_contexts = ["cal.context.governance/v2", "cal.context.ontology-lifecycle/v2"]
    check("C3-05-CONTEXT-OWNERSHIP-BOUNDARY", coordination["bounded_context_refs"] == expected_contexts and [item["context_ref"] for item in binding["semantic_contexts"]] == expected_contexts and binding["owner_boundaries"]["meaning_owners_unchanged"], expected_contexts)
    check("C3-06-RUNTIME-REPLACEMENT-BOUNDARY", len(binding["runtime_implementations"]) == 2 and all(item["replaceable"] and not item["adopted"] for item in binding["runtime_implementations"]) and "runtime-replacement" in binding_receipt["capabilities_proved"], binding["runtime_implementations"])
    check("C3-07-NO-AUTHORITY-OR-APPROVAL", candidate["authority_effect"] == coordination_receipt["authority_effect"] == binding_receipt["authority_effect"] == "none" and not candidate["next_product_frontier"]["approval_eligible"], {"authority_effect": candidate["authority_effect"], "approval_eligible": candidate["next_product_frontier"]["approval_eligible"]})
    check("C3-08-NEXT-FRONTIER", candidate["next_product_frontier"]["stage"] == "L4-FIRST-TESTABLE-ONTOLOGY-AS-PRODUCT-CANDIDATE" and len(candidate["next_product_frontier"]["work"]) == 3, candidate["next_product_frontier"])

    generator_path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("candidate_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    projection = ROOT / "CANDIDATE.md"
    check("C3-09-PROJECTION-PARITY", projection.is_file() and projection.read_text(encoding="utf-8") == module.render(candidate), sha(projection) if projection.is_file() else "missing")

    material_digest = hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    failures = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-product-construction-validation/v1",
        "candidate_id": candidate["candidate_id"],
        "result": "PASS" if not failures else "FAIL",
        "authority_effect": "none",
        "candidate_sha256": sha(ROOT / "candidate.json"),
        "material_digest": material_digest,
        "material": material,
        "summary": {"passed": len(checks) - len(failures), "failed": len(failures), "total": len(checks), "material_files": len(material)},
        "checks": checks,
        "next_product_frontier": candidate["next_product_frontier"],
        "claim_ceiling": "PASS proves this exact private L3 candidate preserves its predecessor and closes context/runtime prototype evidence. It does not make the Product approval-eligible or grant lifecycle or operational authority."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

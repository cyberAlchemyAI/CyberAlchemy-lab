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
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    candidate = load(ROOT / "candidate.json")
    predecessor = candidate["predecessor"]
    predecessor_candidate = LAB / predecessor["candidate_ref"]
    predecessor_receipt = LAB / predecessor["test_receipt_ref"]
    check("C2-01-PREDECESSOR-IMMUTABLE", sha(predecessor_candidate) == predecessor["candidate_sha256"] and sha(predecessor_receipt) == predecessor["test_receipt_sha256"], {"candidate": sha(predecessor_candidate), "receipt": sha(predecessor_receipt)})

    material_rows = []
    for relative in candidate["material_paths"]:
        path = LAB / relative
        material_rows.append({"path": relative, "exists": path.is_file(), "sha256": sha(path) if path.is_file() else None, "size": path.stat().st_size if path.is_file() else None})
    check("C2-02-MATERIAL-CLOSURE", len(material_rows) == len({row["path"] for row in material_rows}) == 21 and all(row["exists"] for row in material_rows), {"count": len(material_rows), "missing": [row["path"] for row in material_rows if not row["exists"]]})

    source_receipt = load(LAB / candidate["evidence_refs"][0])
    artifact_receipt = load(LAB / candidate["evidence_refs"][1])
    check("C2-03-FOUNDATION-EVIDENCE", source_receipt["result"] == "PASS" and source_receipt["summary"]["nodes"] == 23 and source_receipt["summary"]["relations"] == 24 and source_receipt["summary"]["drift_reconciliations"] == 3 and artifact_receipt["result"] == "PASS" and artifact_receipt["summary"]["hostile_fixtures"] == 3, {"source": source_receipt["result"], "artifact_type": artifact_receipt["result"]})

    plan = load(LAB / candidate["construction_increment"]["plan_ref"])
    check("C2-04-PLAN-BINDING", plan["execution_unit"]["unit_id"] == candidate["construction_increment"]["unit_id"] and plan["approval_boundary"]["mode"] == "single-final-product-boundary", plan["execution_unit"])

    no_effect = candidate["authority_effect"] == source_receipt["authority_effect"] == artifact_receipt["authority_effect"] == "none" and not candidate["next_product_frontier"]["approval_eligible"]
    check("C2-05-NO-AUTHORITY-OR-APPROVAL", no_effect, {"candidate": candidate["authority_effect"], "approval_eligible": candidate["next_product_frontier"]["approval_eligible"]})

    expected_frontier = {"Author the Ontology Product Coordination Context over Governance and Ontology Lifecycle", "Bind the existing lifecycle runtime as one replaceable capability implementation", "Add evolution, replay, recovery, and runtime-replacement Product tests"}
    check("C2-06-NEXT-FRONTIER", candidate["next_product_frontier"]["stage"] == "L3-CONTEXT-AND-RUNTIME-PROTOTYPES" and set(candidate["next_product_frontier"]["work"]) == expected_frontier, candidate["next_product_frontier"])

    generator_path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("candidate_generator", generator_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    view = ROOT / "CANDIDATE.md"
    check("C2-07-PROJECTION-PARITY", view.is_file() and view.read_text(encoding="utf-8") == module.render(candidate), sha(view) if view.is_file() else "missing")

    material_digest = hashlib.sha256(json.dumps(material_rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    failures = [row for row in checks if row["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-product-construction-validation/v1",
        "candidate_id": candidate["candidate_id"],
        "result": "PASS" if not failures else "FAIL",
        "authority_effect": "none",
        "candidate_sha256": sha(ROOT / "candidate.json"),
        "material_digest": material_digest,
        "material": material_rows,
        "summary": {"passed": len(checks) - len(failures), "failed": len(failures), "total": len(checks), "material_files": len(material_rows)},
        "checks": checks,
        "next_product_frontier": candidate["next_product_frontier"],
        "claim_ceiling": "PASS proves this exact private construction increment preserves its predecessor, closes its selected material and evidence, and is ready for the L3 context/runtime prototype stage. It does not make the Product approval-eligible or grant any admission or operational effect."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

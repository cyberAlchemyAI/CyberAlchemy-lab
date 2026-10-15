#!/usr/bin/env python3
"""Check-only validator for the Define runtime discovery Design."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

DESIGN = Path(__file__).resolve().parent.parent
ONTOLOGY = DESIGN.parent

checks: list[dict[str, str]] = []


def add(check_id: str, ok: bool, detail: str) -> None:
    checks.append({"check_id": check_id, "outcome": "PASS" if ok else "BLOCK", "detail": detail})


def load(name: str):
    return json.loads((DESIGN / name).read_text(encoding="utf-8"))


design = load("DESIGN-CANDIDATE.json")
gaps = load("GAPS.json")
witnesses = load("PLANNED-WITNESSES.json")
nodes = load("../NODES.json")["nodes"]

expected_files = {
    "ARCHITECTURE.md",
    "DESIGN-CANDIDATE.json",
    "GAPS.json",
    "PLANNED-WITNESSES.json",
    "README.md",
    "scripts/validate.py",
}
actual_files = {str(path.relative_to(DESIGN)) for path in DESIGN.rglob("*") if path.is_file()}
add("closed-design-inventory", actual_files == expected_files, f"{len(actual_files)} files")

groups = ["components", "contracts", "workflow_steps", "decisions", "dependencies"]
all_records = [row for group in groups for row in design[group]]
record_ids = [row["id"] for row in all_records]
record_set = set(record_ids)
add("record-id-uniqueness", len(record_ids) == len(record_set), f"{len(record_ids)} typed design records")

relations = design["relations"]
add(
    "relation-endpoint-closure",
    all(row["from"] in record_set and row["to"] in record_set for row in relations),
    f"{len(relations)} design relationships",
)

required_views = {"context", "high-level-structure", "low-level-components", "workflow-process", "decision-flow", "dependency-interface"}
view_ids = [row["view_id"] for row in design["views"]]
view_refs = [ref for view in design["views"] for ref in view["record_ids"]]
add("six-view-contract", set(view_ids) == required_views and len(view_ids) == 6, "all six governed Design navigation views")
add("view-reference-closure", all(ref in record_set for ref in view_refs), f"{len(view_refs)} view memberships")
add("view-coverage", set(view_refs) == record_set, "every typed record appears in at least one view")

ontology_ids = {row["node_id"] for row in nodes}
bindings = design["ontology_node_bindings"]
add("ontology-binding-closure", len(bindings) == len(set(bindings)) and set(bindings) <= ontology_ids, f"{len(bindings)} DomainSpec node bindings")

contract_ok = all(row.get("required_fields") and len(row["required_fields"]) == len(set(row["required_fields"])) for row in design["contracts"])
add("contract-field-closure", contract_ok, "every contract has a nonempty unique required-field denominator")
add("workflow-owner-closure", all(row.get("owner") for row in design["workflow_steps"]), "every workflow step names an owner component")
add("decision-outcome-closure", all(len(row.get("outcomes", [])) >= 2 for row in design["decisions"]), "every decision names at least two outcomes")

gap_ids = [row["gap_id"] for row in gaps["gaps"]]
witness_ids = [row["witness_id"] for row in witnesses["witnesses"]]
add("gap-closure", len(gap_ids) == len(set(gap_ids)) and all(row["status"] in {"open", "blocked"} and row["owner_route"] for row in gaps["gaps"]), f"{len(gap_ids)} owner-routed gaps")
add("planned-witness-closure", witnesses["execution_status"] == "not-run" and len(witness_ids) == len(set(witness_ids)) and all(row["required_observation"] for row in witnesses["witnesses"]), f"{len(witness_ids)} unexecuted witness contracts")

posture = design["design_posture"]
ceiling_ok = design["status"] == "discovery-candidate" and posture["canonical_w1_w3_status"] == "not-run" and design["authority_effect"] == gaps["authority_effect"] == witnesses["authority_effect"] == "none"
add("design-and-authority-ceiling", ceiling_ok, "discovery-only, no canonical Design receipt, authority effect none")

material_hash = hashlib.sha256()
for relative in sorted(expected_files):
    material_hash.update(relative.encode())
    material_hash.update(b"\0")
    material_hash.update(hashlib.sha256((DESIGN / relative).read_bytes()).digest())

blocked = sum(row["outcome"] == "BLOCK" for row in checks)
result = {
    "schema_version": "cav2.define.runtime-design-validation/v1",
    "design_id": design["design_id"],
    "overall": "PASS" if blocked == 0 else "BLOCK",
    "material_digest": material_hash.hexdigest(),
    "summary": {"checks": len(checks), "passed": len(checks) - blocked, "blocked": blocked, "records": len(record_ids), "relations": len(relations), "views": len(view_ids), "gaps": len(gap_ids), "planned_witnesses": len(witness_ids)},
    "checks": checks,
    "claim_ceiling": "Discovery architecture structure only; no governed Design, implementation, witness execution, conformance, Plan admission, acceptance, publication, release, or deployment.",
    "authority_effect": "none",
}
sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
sys.exit(1 if blocked else 0)

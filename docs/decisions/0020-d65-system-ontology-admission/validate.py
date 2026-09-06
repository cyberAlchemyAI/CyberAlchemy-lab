#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
DECISION = HERE / "decision.json"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "receipts/validation.json"
PLAN = LAB / "docs/plans/0003-d65-native-ontology-integration/d65-plan.json"

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    decision = load(DECISION)
    schema = load(SCHEMA)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    errors = [error.message for error in Draft202012Validator(schema).iter_errors(decision)]
    record("decision-schema", not errors, {"errors": errors})

    source = decision.get("decision_source", {})
    selection = decision.get("selection", {})
    record(
        "explicit-owner-selection",
        source.get("kind") == "explicit-user-selection"
        and source.get("normalized_option_id") == "D65SYS-1"
        and "admitted" in source.get("verbatim", "").lower()
        and selection.get("option_id") == "D65SYS-1"
        and decision.get("status") == "selected",
        {"source": source, "option_id": selection.get("option_id")},
    )

    admissibility = decision.get("admissibility", {})
    admissibility_failures: list[str] = []
    for key in ("request", "receipt"):
        path = LAB / str(admissibility.get(f"{key}_path", ""))
        if not path.is_file() or digest(path) != admissibility.get(f"{key}_sha256"):
            admissibility_failures.append(f"{key}-digest-mismatch")
    admissibility_receipt = load(LAB / str(admissibility.get("receipt_path", "")))
    expected_options = {"D65SYS-1", "D65SYS-2", "D65SYS-3", "D65SYS-4"}
    record(
        "option-admissibility",
        not admissibility_failures
        and admissibility_receipt.get("routeOutcome") == "gate"
        and set(admissibility_receipt.get("presentedOptionIds", [])) == expected_options
        and set(admissibility_receipt.get("admissibleOptionIds", [])) == expected_options,
        {"failures": admissibility_failures, "route_outcome": admissibility_receipt.get("routeOutcome")},
    )

    refs = decision.get("candidate_refs", {})
    artifact_names = ("profile", "sources", "graph", "source_manifest", "event_contract", "system_ontology", "compile_receipt", "validation", "hostile_validation", "owner_request")
    candidate_failures: list[str] = []
    for name in artifact_names:
        path = LAB / str(refs.get(f"{name}_path", ""))
        if not path.is_file() or digest(path) != refs.get(f"{name}_sha256"):
            candidate_failures.append(f"{name}-digest-mismatch")
    graph = load(LAB / str(refs.get("graph_path", "")))
    manifest = load(LAB / str(refs.get("source_manifest_path", "")))
    event_contract = load(LAB / str(refs.get("event_contract_path", "")))
    system = load(LAB / str(refs.get("system_ontology_path", "")))
    compilation = load(LAB / str(refs.get("compile_receipt_path", "")))
    validation = load(LAB / str(refs.get("validation_path", "")))
    hostile = load(LAB / str(refs.get("hostile_validation_path", "")))
    record(
        "immutable-candidate-and-preselection-evidence",
        not candidate_failures
        and compilation.get("result") == "PASS"
        and compilation.get("deterministic_internal_double_compile") is True
        and validation.get("result") == "PASS"
        and validation.get("gate_state") == "BLOCK"
        and hostile.get("result") == "PASS"
        and len(graph.get("nodes", [])) == 41
        and len(graph.get("edges", [])) == 43
        and len(manifest.get("records", [])) == 84
        and [len(event_contract.get(key, [])) for key in ("streams", "events", "projections", "joins")] == [5, 5, 3, 2]
        and system.get("semantic_graph", {}).get("nodes") == graph.get("nodes")
        and system.get("semantic_graph", {}).get("edges") == graph.get("edges")
        and system.get("event_calculus", {}).get("contract") == event_contract,
        {"failures": candidate_failures, "validation": validation.get("result"), "hostile": hostile.get("result")},
    )

    admitted = decision.get("admitted_system_ontology", {})
    record(
        "admitted-system-ontology-closure",
        admitted.get("package_id") == refs.get("package_id")
        and admitted.get("ontology_id") == refs.get("ontology_id")
        and admitted.get("domainspec_nodes") == len(graph.get("nodes", [])) == 41
        and admitted.get("canonical_domainspec_edges") == len(graph.get("edges", [])) == 43
        and admitted.get("provenance_records") == len(manifest.get("records", [])) == 84
        and admitted.get("event_streams") == len(event_contract.get("streams", [])) == 5
        and admitted.get("event_definitions") == len(event_contract.get("events", [])) == 5
        and admitted.get("projections") == len(event_contract.get("projections", [])) == 3
        and admitted.get("exact_governance_joins") == len(event_contract.get("joins", [])) == 2
        and admitted.get("graph_identity") == refs.get("graph_sha256")
        and admitted.get("system_ontology_identity") == refs.get("system_ontology_sha256"),
        {"package_id": admitted.get("package_id"), "graph_identity": admitted.get("graph_identity")},
    )

    plan = load(PLAN)
    preimage = decision.get("selected_plan_preimage", {})
    stages = {item.get("stage_id"): item for item in plan.get("stages", [])}
    binding = plan.get("selected_dependencies", {}).get("system_ontology_owner_decision", {})
    direct = plan.get("revision") == 13 and plan.get("supersedes_plan_sha256") == preimage.get("sha256") and preimage.get("revision") == 12
    descendant = plan.get("revision", 0) > 13 and binding.get("path") == str(DECISION.relative_to(LAB)) and binding.get("sha256") == digest(DECISION)
    state = plan.get("system_ontology_candidate", {})
    record(
        "plan-transition-boundary",
        (direct or descendant)
        and binding.get("path") == str(DECISION.relative_to(LAB))
        and binding.get("sha256") == digest(DECISION)
        and all(stages.get(stage_id, {}).get("state") == "PASS" for stage_id in ("D65-S1", "D65-S2", "D65-S3", "D65-S4", "D65-S5"))
        and stages.get("D65-S6", {}).get("state") == "BLOCK"
        and all(stages.get(f"D65-S{index}", {}).get("state") == "not_evaluable" for index in range(7, 9))
        and state.get("owner_decision_state") == "selected"
        and state.get("selected_option_id") == "D65SYS-1"
        and state.get("gate_state") == "PASS"
        and plan.get("first_blocking_gate") == "G-D65-BINDING"
        and plan.get("execution", {}).get("authorized") is False,
        {"revision": plan.get("revision"), "s5": stages.get("D65-S5", {}).get("state"), "s6": stages.get("D65-S6", {}).get("state")},
    )

    record(
        "authority-and-successor-boundary",
        decision.get("authority_effect") == "admit-exact-d65-s5-system-ontology-only"
        and decision.get("next_gate") == "G-D65-BINDING"
        and len(decision.get("non_effects", [])) >= 8
        and any("does not accept or author" in item for item in decision.get("non_effects", []))
        and any("does not mutate Rust" in item for item in decision.get("non_effects", []))
        and any("does not make the compiled graph" in item for item in decision.get("non_effects", [])),
        {"next_gate": decision.get("next_gate"), "authority_effect": decision.get("authority_effect")},
    )

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-system-ontology-admission-validation/v1",
        "decision_id": decision.get("decision_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "resolved_gate": "G-D65-COMPILE" if result == "PASS" else None,
        "next_gate": "G-D65-BINDING" if result == "PASS" else "G-D65-COMPILE",
        "execution_authorized": False,
        "inputs": [
            {"path": str(DECISION.relative_to(LAB)), "sha256": digest(DECISION)},
            {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)},
            {"path": str(Path(__file__).relative_to(LAB)), "sha256": digest(Path(__file__))},
            {"path": str(PLAN.relative_to(LAB)), "sha256": digest(PLAN)}
        ],
        "authority_effect": "admit-exact-d65-s5-system-ontology-only" if result == "PASS" else "none",
        "claim_ceiling": "PASS proves the exact D65SYS-1 owner admission and D65-S5 to D65-S6 eligibility transition only. It does not author or accept a binding, implement, migrate, cut over, publish, release, deploy, or create external effects."
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision_id": receipt["decision_id"], "result": result, "failed_checks": failed, "resolved_gate": receipt["resolved_gate"], "next_gate": receipt["next_gate"], "execution_authorized": False}, indent=2, sort_keys=True))
    return 0 if result == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

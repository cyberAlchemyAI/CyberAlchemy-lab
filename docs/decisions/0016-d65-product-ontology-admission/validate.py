#!/usr/bin/env python3
"""Validate the exact D65PROD-1 owner admission and D65 stage boundary."""

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

    schema_errors = [error.message for error in Draft202012Validator(schema).iter_errors(decision)]
    record("decision-schema", not schema_errors, {"errors": schema_errors})

    source = decision.get("decision_source", {})
    selection = decision.get("selection", {})
    record(
        "explicit-owner-selection",
        source.get("kind") == "explicit-user-selection"
        and source.get("token") == "D65PROD-1"
        and source.get("observed_count", 0) >= 1
        and selection.get("option_id") == "D65PROD-1"
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
    expected_options = {"D65PROD-1", "D65PROD-2", "D65PROD-3", "D65PROD-4"}
    record(
        "option-admissibility",
        not admissibility_failures
        and admissibility_receipt.get("routeOutcome") == "gate"
        and set(admissibility_receipt.get("presentedOptionIds", [])) == expected_options
        and set(admissibility_receipt.get("admissibleOptionIds", [])) == expected_options,
        {"failures": admissibility_failures, "route_outcome": admissibility_receipt.get("routeOutcome")},
    )

    refs = decision.get("candidate_refs", {})
    artifact_names = (
        "profile",
        "sources",
        "product_capability",
        "nodes",
        "relations",
        "residue",
        "schema",
        "validator",
        "candidate_validation",
        "owner_request",
    )
    candidate_failures: list[str] = []
    for name in artifact_names:
        path = LAB / str(refs.get(f"{name}_path", ""))
        if not path.is_file() or digest(path) != refs.get(f"{name}_sha256"):
            candidate_failures.append(f"{name}-digest-mismatch")
    candidate_validation = load(LAB / str(refs.get("candidate_validation_path", "")))
    record(
        "immutable-candidate-and-preselection-evidence",
        not candidate_failures
        and candidate_validation.get("result") == "PASS"
        and candidate_validation.get("gate_id") == "G-D65-PRODUCT"
        and candidate_validation.get("gate_state") == "BLOCK",
        {"failures": candidate_failures, "preselection_result": candidate_validation.get("result")},
    )

    profile = load(LAB / str(refs.get("profile_path", "")))
    capability = load(LAB / str(refs.get("product_capability_path", "")))
    nodes = load(LAB / str(refs.get("nodes_path", "")))
    relations = load(LAB / str(refs.get("relations_path", "")))
    admitted = decision.get("admitted_product_meaning", {})
    record(
        "admitted-product-meaning-closure",
        profile.get("ontology_id") == refs.get("ontology_id") == admitted.get("ontology_id")
        and profile.get("ontology_type") == admitted.get("ontology_type") == "business-domain"
        and capability.get("capability_id") == admitted.get("capability_id")
        and len(nodes.get("nodes", [])) == admitted.get("node_count") == 16
        and len(relations.get("relation_vocabulary", [])) == admitted.get("relation_type_count") == 7
        and len(relations.get("relations", [])) == admitted.get("relation_count") == 15
        and len(capability.get("definition_binding_refs", [])) == admitted.get("handled_definition_binding_count") == 13
        and capability.get("adoption_state") == "not-adopted"
        and profile.get("candidate_status") == "validated-candidate-awaiting-owner-admission",
        {
            "ontology_id": admitted.get("ontology_id"),
            "capability_id": admitted.get("capability_id"),
            "candidate_bytes_remain_preselection": True,
        },
    )

    plan = load(PLAN)
    plan_preimage = decision.get("selected_plan_preimage", {})
    stage_by_id = {item.get("stage_id"): item for item in plan.get("stages", [])}
    decision_binding = plan.get("selected_dependencies", {}).get("product_ontology_owner_decision", {})
    direct_transition = (
        plan.get("revision") == 7
        and plan.get("supersedes_plan_sha256") == plan_preimage.get("sha256")
        and plan_preimage.get("revision") == 6
    )
    descendant_transition = (
        plan.get("revision", 0) > 7
        and decision_binding.get("path") == str(DECISION.relative_to(LAB))
        and decision_binding.get("sha256") == digest(DECISION)
    )
    successor_states = [stage_by_id.get(f"D65-S{index}", {}).get("state") for index in range(3, 9)]
    if "BLOCK" in successor_states:
        block_index = successor_states.index("BLOCK")
        successor_frontier = (
            successor_states.count("BLOCK") == 1
            and all(state == "PASS" for state in successor_states[:block_index])
            and all(state == "not_evaluable" for state in successor_states[block_index + 1 :])
        )
    else:
        successor_frontier = all(state == "PASS" for state in successor_states)
    product_state = plan.get("product_ontology_candidate", {})
    record(
        "plan-transition-boundary",
        (direct_transition or descendant_transition)
        and decision_binding.get("path") == str(DECISION.relative_to(LAB))
        and decision_binding.get("sha256") == digest(DECISION)
        and stage_by_id.get("D65-S1", {}).get("state") == "PASS"
        and stage_by_id.get("D65-S2", {}).get("state") == "PASS"
        and successor_frontier
        and product_state.get("owner_decision_state") == "selected"
        and product_state.get("selected_option_id") == "D65PROD-1"
        and product_state.get("gate_state") == "PASS"
        and plan.get("execution", {}).get("authorized") is False,
        {
            "revision": plan.get("revision"),
            "s2": stage_by_id.get("D65-S2", {}).get("state"),
            "s3": stage_by_id.get("D65-S3", {}).get("state"),
            "execution_authorized": plan.get("execution", {}).get("authorized"),
        },
    )

    record(
        "authority-and-successor-boundary",
        decision.get("authority_effect") == "admit-exact-d65-s2-product-ontology-only"
        and decision.get("next_gate") == "G-D65-BUSINESS"
        and len(decision.get("non_effects", [])) >= 5
        and any("does not author or admit the D65-S3" in item for item in decision.get("non_effects", []))
        and any("does not make Invoke" in item for item in decision.get("non_effects", [])),
        {"next_gate": decision.get("next_gate"), "authority_effect": decision.get("authority_effect")},
    )

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-product-ontology-admission-validation/v1",
        "decision_id": decision.get("decision_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "resolved_gate": "G-D65-PRODUCT" if result == "PASS" else None,
        "next_gate": "G-D65-BUSINESS" if result == "PASS" else "G-D65-PRODUCT",
        "execution_authorized": False,
        "inputs": [
            {"path": str(DECISION.relative_to(LAB)), "sha256": digest(DECISION)},
            {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)},
            {"path": str(Path(__file__).relative_to(LAB)), "sha256": digest(Path(__file__))},
            {"path": str(PLAN.relative_to(LAB)), "sha256": digest(PLAN)},
        ],
        "authority_effect": "admit-exact-d65-s2-product-ontology-only" if result == "PASS" else "none",
        "claim_ceiling": "PASS proves the exact D65PROD-1 owner admission and D65-S2 to D65-S3 plan transition only. It does not author or admit D65-S3, implement, migrate, cut over, publish, release, deploy, or create external effects.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "decision_id": receipt["decision_id"],
        "result": result,
        "failed_checks": failed,
        "resolved_gate": receipt["resolved_gate"],
        "next_gate": receipt["next_gate"],
        "execution_authorized": False,
    }, indent=2, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

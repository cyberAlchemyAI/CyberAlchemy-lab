#!/usr/bin/env python3
"""Validate the exact D65SRC-1 owner admission and D65 stage boundary."""

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
        and source.get("verbatim") == "Approved"
        and source.get("normalized_option_id") == "D65SRC-1"
        and source.get("observed_count", 0) >= 2
        and selection.get("option_id") == "D65SRC-1"
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
    expected_options = {"D65SRC-1", "D65SRC-2", "D65SRC-3", "D65SRC-4"}
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
        "profile", "sources", "business_mapping", "event_sourcing_source",
        "event_payload_schema", "development_profile", "development_profile_registry",
        "project", "feature", "residue", "schema", "readme", "validator",
        "compile_check", "hostile_checks", "candidate_validation", "hostile_validation",
        "owner_request",
    )
    candidate_failures: list[str] = []
    for name in artifact_names:
        path = LAB / str(refs.get(f"{name}_path", ""))
        if not path.is_file() or digest(path) != refs.get(f"{name}_sha256"):
            candidate_failures.append(f"{name}-digest-mismatch")
    validation = load(LAB / str(refs.get("candidate_validation_path", "")))
    hostile = load(LAB / str(refs.get("hostile_validation_path", "")))
    record(
        "immutable-candidate-and-preselection-evidence",
        not candidate_failures
        and validation.get("result") == "PASS"
        and validation.get("gate_state") == "BLOCK"
        and validation.get("compile_result", {}).get("minted", {}).get("source_set_digest") == refs.get("minted_source_set_digest")
        and validation.get("compile_result", {}).get("minted", {}).get("deterministic_double_compile") is True
        and validation.get("compile_result", {}).get("event_sourcing", {}).get("deterministic_double_compile") is True
        and hostile.get("result") == "PASS",
        {"failures": candidate_failures, "preselection_result": validation.get("result"), "hostile_result": hostile.get("result")},
    )

    admitted = decision.get("admitted_source_meaning", {})
    mapping = load(LAB / str(refs.get("business_mapping_path", "")))
    event_source = load(LAB / str(refs.get("event_sourcing_source_path", "")))
    feature = load(LAB / str(refs.get("feature_path", "")))
    record(
        "admitted-source-meaning-closure",
        admitted.get("package_id") == refs.get("package_id")
        and len(mapping.get("node_mappings", [])) == admitted.get("business_nodes_mapped") == 26
        and len(mapping.get("relation_mappings", [])) == admitted.get("business_relations_mapped") == 35
        and len(mapping.get("contract_mappings", [])) == admitted.get("business_contracts_mapped") == 8
        and len(mapping.get("failure_mappings", [])) == admitted.get("business_failures_mapped") == 13
        and len(feature.get("node_sources", [])) == admitted.get("domainspec_nodes") == 41
        and len(event_source.get("streams", [])) == admitted.get("event_streams") == 5
        and len(event_source.get("events", [])) == admitted.get("event_definitions") == 5
        and len(event_source.get("projections", [])) == admitted.get("projections") == 3
        and len(event_source.get("joins", [])) == admitted.get("exact_governance_joins") == 2,
        {"package_id": admitted.get("package_id"), "candidate_bytes_remain_preselection": True},
    )

    plan = load(PLAN)
    preimage = decision.get("selected_plan_preimage", {})
    stages = {item.get("stage_id"): item for item in plan.get("stages", [])}
    binding = plan.get("selected_dependencies", {}).get("domainspec_source_owner_decision", {})
    direct = plan.get("revision") == 11 and plan.get("supersedes_plan_sha256") == preimage.get("sha256") and preimage.get("revision") == 10
    descendant = plan.get("revision", 0) > 11 and binding.get("path") == str(DECISION.relative_to(LAB)) and binding.get("sha256") == digest(DECISION)
    source_state = plan.get("domainspec_source_candidate", {})
    record(
        "plan-transition-boundary",
        (direct or descendant)
        and binding.get("path") == str(DECISION.relative_to(LAB))
        and binding.get("sha256") == digest(DECISION)
        and all(stages.get(stage_id, {}).get("state") == "PASS" for stage_id in ("D65-S1", "D65-S2", "D65-S3", "D65-S4"))
        and stages.get("D65-S5", {}).get("state") == "BLOCK"
        and all(stages.get(f"D65-S{index}", {}).get("state") == "not_evaluable" for index in range(6, 9))
        and source_state.get("owner_decision_state") == "selected"
        and source_state.get("selected_option_id") == "D65SRC-1"
        and source_state.get("gate_state") == "PASS"
        and plan.get("first_blocking_gate") == "G-D65-COMPILE"
        and plan.get("execution", {}).get("authorized") is False,
        {"revision": plan.get("revision"), "s4": stages.get("D65-S4", {}).get("state"), "s5": stages.get("D65-S5", {}).get("state"), "execution_authorized": plan.get("execution", {}).get("authorized")},
    )

    record(
        "authority-and-successor-boundary",
        decision.get("authority_effect") == "admit-exact-d65-s4-domainspec-source-only"
        and decision.get("next_gate") == "G-D65-COMPILE"
        and len(decision.get("non_effects", [])) >= 8
        and any("does not materialize or admit a D65-S5" in item for item in decision.get("non_effects", []))
        and any("does not release or generally admit" in item for item in decision.get("non_effects", []))
        and any("does not mutate Rust" in item for item in decision.get("non_effects", []))
        and any("does not make Invoke" in item for item in decision.get("non_effects", [])),
        {"next_gate": decision.get("next_gate"), "authority_effect": decision.get("authority_effect")},
    )

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-domainspec-source-admission-validation/v1",
        "decision_id": decision.get("decision_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "resolved_gate": "G-D65-DOMAINSPEC-SOURCE" if result == "PASS" else None,
        "next_gate": "G-D65-COMPILE" if result == "PASS" else "G-D65-DOMAINSPEC-SOURCE",
        "execution_authorized": False,
        "inputs": [
            {"path": str(DECISION.relative_to(LAB)), "sha256": digest(DECISION)},
            {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)},
            {"path": str(Path(__file__).relative_to(LAB)), "sha256": digest(Path(__file__))},
            {"path": str(PLAN.relative_to(LAB)), "sha256": digest(PLAN)},
        ],
        "authority_effect": "admit-exact-d65-s4-domainspec-source-only" if result == "PASS" else "none",
        "claim_ceiling": "PASS proves the exact D65SRC-1 owner admission and D65-S4 to D65-S5 eligibility transition only. It does not materialize or admit D65-S5 outputs, implement, migrate, cut over, publish, release, deploy, or create external effects.",
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

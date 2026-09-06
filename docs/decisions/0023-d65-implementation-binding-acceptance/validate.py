#!/usr/bin/env python3
"""Validate the exact D65BIND-1 owner acceptance decision."""

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
RECEIPT = HERE / "receipts" / "validation.json"


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
        and source.get("verbatim") == "D65BIND-1"
        and source.get("normalized_option_id") == "D65BIND-1"
        and source.get("observed_count") == 1
        and selection.get("option_id") == "D65BIND-1"
        and decision.get("status") == "selected",
        {"source": source, "option_id": selection.get("option_id")},
    )

    refs = decision.get("candidate_refs", {})
    artifact_names = (
        "binding",
        "owner_request",
        "admissibility_request",
        "validation_receipt",
        "admissibility_receipt",
    )
    ref_failures: list[str] = []
    for name in artifact_names:
        path = LAB / str(refs.get(f"{name}_path", ""))
        if not path.is_file() or digest(path) != refs.get(f"{name}_sha256"):
            ref_failures.append(f"{name}-digest-mismatch")

    binding = load(LAB / str(refs.get("binding_path", "")))
    owner_request = load(LAB / str(refs.get("owner_request_path", "")))
    validation = load(LAB / str(refs.get("validation_receipt_path", "")))
    admissibility = load(LAB / str(refs.get("admissibility_receipt_path", "")))
    record(
        "immutable-candidate-and-evidence",
        not ref_failures
        and binding.get("binding_id") == refs.get("binding_id")
        and binding.get("ontology_id") == refs.get("ontology_id")
        and binding.get("status") == "candidate-pending-owner-acceptance"
        and binding.get("gate", {}).get("state") == "BLOCK"
        and binding.get("implementation_authorized") is False
        and validation.get("result") == "PASS"
        and validation.get("candidate_valid") is True
        and validation.get("candidate_sha256") == refs.get("binding_sha256")
        and admissibility.get("prefilter_result") == "PASS"
        and admissibility.get("admissible_for_owner_decision") is True
        and admissibility.get("candidate_sha256") == refs.get("binding_sha256"),
        {"failures": ref_failures, "validation": validation.get("result"), "admissibility": admissibility.get("prefilter_result")},
    )

    expected_options = ["D65BIND-1", "D65BIND-2", "D65BIND-3", "D65BIND-4"]
    record(
        "presented-option-selected",
        [item.get("option_id") for item in owner_request.get("options", [])] == expected_options
        and admissibility.get("presented_option_ids") == expected_options
        and owner_request.get("candidate_sha256") == refs.get("binding_sha256")
        and owner_request.get("gate_id") == "G-D65-BINDING"
        and selection.get("option_id") == "D65BIND-1",
        {"presented_options": admissibility.get("presented_option_ids")},
    )

    preimage = decision.get("selected_plan_preimage", {})
    plan_path = LAB / str(preimage.get("path", ""))
    plan = load(plan_path)
    stages = {item.get("stage_id"): item for item in plan.get("stages", [])}
    bound_plan = next(
        (item for item in binding.get("bound_artifacts", []) if item.get("artifact_id") == "D65-PLAN-REV14"),
        {},
    )
    record(
        "immutable-plan-preimage",
        plan_path.is_file()
        and digest(plan_path) == preimage.get("sha256") == bound_plan.get("sha256")
        and preimage.get("revision") == plan.get("revision") == 14
        and bound_plan.get("path") == preimage.get("path")
        and plan.get("first_blocking_gate") == "G-D65-BINDING"
        and stages.get("D65-S6", {}).get("state") == "BLOCK"
        and stages.get("D65-S7", {}).get("state") == "not_evaluable",
        {"revision": plan.get("revision"), "sha256": digest(plan_path) if plan_path.is_file() else None},
    )

    accepted = decision.get("accepted_binding", {})
    prospective = binding.get("planned_adapters", [])
    expected_targets = [item.get("target_path") for item in prospective]
    target_states = {target: (LAB / str(target)).exists() for target in expected_targets}
    record(
        "accepted-binding-closure",
        accepted.get("binding_id") == refs.get("binding_id")
        and accepted.get("binding_identity") == refs.get("binding_sha256")
        and accepted.get("bound_artifact_count") == validation.get("bound_artifact_count") == 28
        and accepted.get("existing_rust_symbol_count") == validation.get("existing_symbol_count") == 34
        and accepted.get("prospective_target_count") == validation.get("prospective_target_count") == 3
        and accepted.get("prospective_targets") == expected_targets
        and not any(target_states.values()),
        {"target_states": target_states},
    )

    successor = decision.get("successor_eligibility", {})
    non_effects = decision.get("non_effects", [])
    record(
        "authority-and-successor-boundary",
        decision.get("authority_effect") == "accept-exact-d65-s6-implementation-binding-only"
        and decision.get("implementation_authorized") is False
        and decision.get("next_gate") == "G-D65-IMPLEMENTATION"
        and successor == {
            "stage_id": "D65-S7",
            "gate_id": "G-D65-IMPLEMENTATION",
            "state": "eligible-awaiting-separate-implementation-authorization",
            "execution_authorized": False,
        }
        and any("does not authorize or perform D65-S7" in item for item in non_effects)
        and any("does not rewrite" in item for item in non_effects)
        and any("does not make Invoke" in item for item in non_effects),
        {"successor": successor, "authority_effect": decision.get("authority_effect")},
    )

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-implementation-binding-acceptance-validation/v1",
        "decision_id": decision.get("decision_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "resolved_gate": "G-D65-BINDING" if result == "PASS" else None,
        "next_gate": "G-D65-IMPLEMENTATION" if result == "PASS" else "G-D65-BINDING",
        "d65_s7_eligible": result == "PASS",
        "execution_authorized": False,
        "inputs": [
            {"path": str(DECISION.relative_to(LAB)), "sha256": digest(DECISION)},
            {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)},
            {"path": str(Path(__file__).relative_to(LAB)), "sha256": digest(Path(__file__))},
            {"path": str(plan_path.relative_to(LAB)), "sha256": digest(plan_path)},
            {"path": refs.get("binding_path"), "sha256": digest(LAB / str(refs.get("binding_path")))},
        ],
        "authority_effect": "accept-exact-d65-s6-implementation-binding-only" if result == "PASS" else "none",
        "claim_ceiling": "PASS proves only the exact D65BIND-1 owner acceptance, G-D65-BINDING resolution, and D65-S7 eligibility. It does not authorize or perform implementation, conformance, migration, cutover, publication, deployment, or external effects.",
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
        "d65_s7_eligible": receipt["d65_s7_eligible"],
        "execution_authorized": False,
    }, indent=2, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

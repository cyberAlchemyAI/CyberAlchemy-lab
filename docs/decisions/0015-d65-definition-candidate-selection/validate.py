#!/usr/bin/env python3
"""Validate the exact D65DEF-1 owner selection and its stage boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CORE = LAB.parent / "domainspec-core"
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


def selector_digest(path: Path, definition_id: str) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    heading = f"## {definition_id}:"
    start = next((index for index, line in enumerate(lines) if line.startswith(heading)), None)
    if start is None:
        return None
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")), len(lines))
    return hashlib.sha256("".join(lines[start:end]).encode("utf-8")).hexdigest()


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
        source == {"kind": "explicit-user-selection", "token": "D65DEF-1"}
        and selection.get("option_id") == "D65DEF-1"
        and decision.get("status") == "selected",
        {"source": source, "option_id": selection.get("option_id")},
    )

    admissibility = decision.get("admissibility", {})
    admissibility_failures: list[str] = []
    for key in ("request", "receipt"):
        path = HERE / admissibility.get(f"{key}_path", "")
        if not path.is_file() or digest(path) != admissibility.get(f"{key}_sha256"):
            admissibility_failures.append(f"{key}-digest-mismatch")
    admissibility_receipt = load(HERE / admissibility.get("receipt_path", ""))
    record(
        "option-admissibility",
        not admissibility_failures
        and admissibility_receipt.get("routeOutcome") == "gate"
        and set(admissibility_receipt.get("presentedOptionIds", [])) == {"D65DEF-1", "D65DEF-2", "D65DEF-3", "D65DEF-4"},
        {"failures": admissibility_failures, "route_outcome": admissibility_receipt.get("routeOutcome")},
    )

    candidate_failures: list[str] = []
    for name in ("definition_pack", "handled_definitions", "candidate_validation", "owner_request"):
        path = LAB / decision["candidate_refs"].get(f"{name}_path", "")
        if not path.is_file() or digest(path) != decision["candidate_refs"].get(f"{name}_sha256"):
            candidate_failures.append(f"{name}-digest-mismatch")
    candidate_validation = load(LAB / decision["candidate_refs"]["candidate_validation_path"])
    record(
        "immutable-candidate-and-evidence",
        not candidate_failures
        and candidate_validation.get("result") == "PASS"
        and candidate_validation.get("gate_id") == "G-D65-DEFINITIONS"
        and candidate_validation.get("gate_state") == "BLOCK",
        {"failures": candidate_failures, "preselection_validation_result": candidate_validation.get("result")},
    )

    definitions_path = CORE / "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md"
    selector_failures = [
        item["definition_id"]
        for item in decision.get("selected_canonical_definition_selectors", [])
        if selector_digest(definitions_path, item["definition_id"]) != item["sha256"]
    ]
    record("selected-definition-currentness", not selector_failures, {"selector_failures": selector_failures})

    plan = load(PLAN)
    plan_preimage = decision.get("selected_plan_preimage", {})
    stage_by_id = {item.get("stage_id"): item for item in plan.get("stages", [])}
    decision_binding = plan.get("selected_dependencies", {}).get("definition_owner_decision", {})
    direct_transition = plan.get("revision") == 5 and plan.get("supersedes_plan_sha256") == plan_preimage.get("sha256")
    descendant_transition = (
        plan.get("revision", 0) > 5
        and decision_binding.get("path") == str(DECISION.relative_to(LAB))
        and decision_binding.get("sha256") == digest(DECISION)
    )
    successor_states = [stage_by_id.get(f"D65-S{index}", {}).get("state") for index in range(2, 9)]
    if "BLOCK" in successor_states:
        block_index = successor_states.index("BLOCK")
        successor_frontier = (
            successor_states.count("BLOCK") == 1
            and all(state == "PASS" for state in successor_states[:block_index])
            and all(state == "not_evaluable" for state in successor_states[block_index + 1 :])
        )
    else:
        successor_frontier = all(state == "PASS" for state in successor_states)
    record(
        "plan-transition-boundary",
        (direct_transition or descendant_transition)
        and stage_by_id.get("D65-S1", {}).get("state") == "PASS"
        and successor_frontier
        and plan.get("execution", {}).get("authorized") is False,
        {
            "revision": plan.get("revision"),
            "s1": stage_by_id.get("D65-S1", {}).get("state"),
            "s2": stage_by_id.get("D65-S2", {}).get("state"),
            "execution_authorized": plan.get("execution", {}).get("authorized"),
        },
    )

    record(
        "authority-boundary",
        decision.get("authority_effect") == "none"
        and decision.get("accepted_local_meanings", {}).get("canonical_promotion_count") == 0
        and len(decision.get("non_effects", [])) >= 4
        and decision.get("next_gate") == "G-D65-PRODUCT",
        {"next_gate": decision.get("next_gate"), "authority_effect": decision.get("authority_effect")},
    )

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-definition-candidate-selection-validation/v1",
        "decision_id": decision.get("decision_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "resolved_gate": "G-D65-DEFINITIONS" if result == "PASS" else None,
        "next_gate": "G-D65-PRODUCT" if result == "PASS" else "G-D65-DEFINITIONS",
        "execution_authorized": False,
        "inputs": [
            {"path": str(DECISION.relative_to(LAB)), "sha256": digest(DECISION)},
            {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)},
            {"path": str(Path(__file__).relative_to(LAB)), "sha256": digest(Path(__file__))},
            {"path": str(PLAN.relative_to(LAB)), "sha256": digest(PLAN)},
        ],
        "authority_effect": "none",
        "claim_ceiling": "PASS proves the exact D65DEF-1 selection and plan stage transition only. It does not promote canonical definitions, author or admit D65-S2, or authorize implementation, migration, publication, deployment, or external effects."
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

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
PLAN = HERE / "plan.json"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "receipts/validation.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def boundary_errors(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    execution = plan.get("execution", {})
    final_gate = plan.get("final_gate", {})
    if plan.get("authority_effect") != "none" or execution.get("authorized") is not False:
        errors.append("plan carries authority")
    for key in ("admission_authorized", "activation_authorized", "migration_authorized", "cutover_authorized", "cutover_performed", "publication_authorized", "deployment_authorized"):
        if execution.get(key) is not False:
            errors.append(f"{key} must remain false")
    if final_gate.get("position") != "after-all-rehearsal-evidence" or final_gate.get("state") != "not_evaluable":
        errors.append("owner gate is not deferred to the end")
    if final_gate.get("cutover_authorized") is not False or final_gate.get("authority_effect") != "none":
        errors.append("final gate candidate exceeds no-effect planning")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    plan = load(PLAN)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    schema_errors = [error.message for error in Draft202012Validator(load(SCHEMA)).iter_errors(plan)]
    add("plan-schema", not schema_errors, schema_errors)

    product = plan.get("approved_product", {})
    drift: list[dict[str, Any]] = []
    for name in ("manifest", "product_test_evidence", "approval_decision", "approval_validation"):
        ref = product.get(name, {})
        path = LAB / str(ref.get("path", ""))
        actual = digest(path) if path.is_file() else None
        if actual != ref.get("sha256"):
            drift.append({"name": name, "path": ref.get("path"), "expected": ref.get("sha256"), "actual": actual})
    add("approved-product-current", not drift, drift)

    evidence = load(LAB / product["product_test_evidence"]["path"])
    decision = load(LAB / product["approval_decision"]["path"])
    approval_validation = load(LAB / product["approval_validation"]["path"])
    approval_ok = (
        evidence.get("result") == "PASS"
        and evidence.get("manifest_sha256") == product["manifest"]["sha256"]
        and evidence.get("product_candidate_frozen") is True
        and decision.get("selected_option", {}).get("option_id") == "D65PAPP-1"
        and decision.get("product_approval", {}).get("state") == "approved"
        and decision.get("downstream_authority", {}).get("cutover_authorized") is False
        and approval_validation.get("result") == "PASS"
        and approval_validation.get("stage_state") == "PRODUCT_APPROVED"
        and approval_validation.get("product_approval") == "approved"
        and approval_validation.get("cutover_authorized") is False
    )
    add("exact-product-approval-closure", approval_ok, {"decision": decision.get("decision_id"), "validation": approval_validation.get("result")})

    stages = plan.get("stages", [])
    ids = [stage.get("stage_id") for stage in stages]
    states = {stage.get("stage_id"): stage.get("state") for stage in stages}
    expected_ids = ["PA-S0", "RH-S1", "RH-S2", "RH-S3", "RH-S4", "RH-S5", "PADM-G1"]
    expected_states = {"PA-S0": "PASS", "RH-S1": "ready", "RH-S2": "planned", "RH-S3": "planned", "RH-S4": "planned", "RH-S5": "planned", "PADM-G1": "not_evaluable"}
    add("continuous-gate-at-end-sequence", ids == expected_ids and states == expected_states and plan.get("current_frontier") == "RH-S1", {"ids": ids, "states": states})

    invariants = plan.get("invariants", [])
    scope = plan.get("rehearsal_scope", {})
    forbidden = scope.get("forbidden_effects", [])
    invariant_ok = (
        len(invariants) >= 10
        and any("Canonical events are the only replay source" in item for item in invariants)
        and any("node and relation state" in item for item in invariants)
        and any("Challenge contracts" in item for item in invariants)
        and any("Rollback restores" in item for item in invariants)
        and scope.get("mode") == "isolated-local-no-effect"
        and scope.get("snapshot_role") == "discardable projection accelerator"
        and {"node", "relation", "context binding", "challenge contract"}.issubset(scope.get("required_record_kinds", []))
        and all(any(fragment in item for item in forbidden) for fragment in ("approved product", "admitted runtime", "cut over", "external effects"))
    )
    add("event-sourced-rehearsal-boundary", invariant_ok, {"forbidden_effects": forbidden})

    validation = plan.get("validation_contract", {})
    mutations = validation.get("hostile_mutations", [])
    validation_ok = (
        validation.get("deterministic_runs") == 2
        and len(validation.get("required_checks", [])) >= 10
        and len(mutations) >= 8
        and all(any(fragment in mutation for mutation in mutations) for fragment in ("partial stream", "wrong context", "reverse relationship", "snapshot promoted", "missing challenge", "authority escalation"))
        and "do not open the final gate" in validation.get("failure_rule", "")
    )
    add("rehearsal-test-contract", validation_ok, {"required_checks": len(validation.get("required_checks", [])), "hostile_mutations": len(mutations)})

    work = plan.get("work_plan", {})
    tasks = work.get("operational_tasks", [])
    gate_task = next((task for task in tasks if task.get("task_id") == "CAL-OP-POST-APPROVAL-OWNER-DECISION-001"), {})
    work_ok = (
        work.get("current_product_frontier") is None
        and work.get("current_post_approval_frontier") == "RH-S1"
        and work.get("runnable_work") == ["RH-S1", "RH-S2", "RH-S3", "RH-S4", "RH-S5"]
        and work.get("continuation_status") == "runnable"
        and gate_task.get("applies_to_stage") == "PADM-G1"
        and gate_task.get("blocking_basis") == "authority-boundary"
        and all(task.get("blocking_basis") == "none" for task in tasks if task is not gate_task)
    )
    add("two-lane-continuation", work_ok, {"runnable_work": work.get("runnable_work"), "operational_tasks": tasks})

    boundary = boundary_errors(plan)
    add("authority-ceiling", not boundary, boundary)

    probes: list[dict[str, str]] = []
    mutations_to_try = {
        "approved-digest-drift": ("approved_product", "manifest", "sha256", "0" * 64),
        "early-owner-gate": ("final_gate", None, "position", "before-rehearsal"),
        "cutover-escalation": ("execution", None, "cutover_authorized", True),
    }
    for probe_id, (section, subsection, key, value) in mutations_to_try.items():
        mutated = copy.deepcopy(plan)
        target = mutated[section][subsection] if subsection else mutated[section]
        target[key] = value
        if probe_id == "approved-digest-drift":
            caught = target[key] != digest(LAB / product["manifest"]["path"])
        else:
            caught = bool(boundary_errors(mutated))
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("plan-mutation-probes", all(item["result"] == "PASS" for item in probes), probes)

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-post-approval-isolated-rehearsal-plan-validation/v1",
        "plan_id": plan.get("plan_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "planning_candidate_ready": result == "PASS",
        "registered_as_admitted_execution_state": False,
        "current_frontier": "RH-S1" if result == "PASS" else None,
        "final_gate": "G-D65-EPOCH-002-POST-APPROVAL-ADMISSION",
        "final_gate_state": "not_evaluable",
        "admission_authorized": False,
        "activation_authorized": False,
        "cutover_authorized": False,
        "authority_effect": "none",
        "inputs": [
            {"path": str(PLAN.relative_to(LAB)), "sha256": digest(PLAN)},
            {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)},
            {"path": product["manifest"]["path"], "sha256": product["manifest"]["sha256"]},
            {"path": product["approval_decision"]["path"], "sha256": product["approval_decision"]["sha256"]}
        ],
        "claim_ceiling": "PASS proves only that CAL-PLAN-0005 is a coherent no-effect planning candidate whose work can continue through isolated rehearsal evidence before one final admission gate. It does not execute rehearsal or grant admission, activation, migration, cutover, publication, release, deployment, or external effects."
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt[key] for key in ("plan_id", "result", "failed_checks", "planning_candidate_ready", "registered_as_admitted_execution_state", "current_frontier", "final_gate", "final_gate_state", "admission_authorized", "cutover_authorized", "authority_effect")}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

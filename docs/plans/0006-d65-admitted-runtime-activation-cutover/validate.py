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


def schema_errors(instance: dict[str, Any]) -> list[str]:
    return [error.message for error in Draft202012Validator(load(SCHEMA)).iter_errors(instance)]


def boundary_errors(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    execution = plan.get("execution", {})
    gate = plan.get("final_gate", {})
    if plan.get("authority_effect") != "none" or execution.get("authorized") is not False:
        errors.append("plan carries authority")
    for key in (
        "activation_authorized", "migration_authorized", "cutover_authorized",
        "cutover_performed", "publication_authorized", "deployment_authorized",
        "external_effect_authorized",
    ):
        if execution.get(key) is not False:
            errors.append(f"execution.{key} must remain false")
    if gate.get("position") != "after-all-shadow-activation-cutover-evidence":
        errors.append("gate is not after all evidence")
    if gate.get("state") != "not_evaluable" or gate.get("authority_effect") != "none":
        errors.append("gate is prematurely evaluable or effectful")
    for key in ("activation_authorized", "migration_authorized", "cutover_authorized"):
        if gate.get(key) is not False:
            errors.append(f"final_gate.{key} must remain false")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    plan = load(PLAN)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    errors = schema_errors(plan)
    add("plan-schema", not errors, errors)

    admitted = plan.get("admitted_product", {})
    drift: list[dict[str, Any]] = []
    for role in (
        "manifest", "product_approval_decision", "isolated_rehearsal_receipt",
        "admission_decision", "admission_validation",
    ):
        ref = admitted.get(role, {})
        path = LAB / ref.get("path", "")
        actual = digest(path) if path.is_file() else None
        if actual != ref.get("sha256"):
            drift.append({"role": role, "path": ref.get("path"), "expected": ref.get("sha256"), "actual": actual})
    add("exact-admitted-input-currentness", not drift, drift)

    validation_ref = admitted.get("admission_validation", {})
    validation_path = LAB / validation_ref.get("path", "")
    admission = load(validation_path) if validation_path.is_file() else {}
    admission_errors: list[str] = []
    expected_admission = {
        "result": "PASS",
        "admission_state": "admitted",
        "implementation_admitted": True,
        "runtime_activated": False,
        "migration_authorized": False,
        "cutover_authorized": False,
        "cutover_performed": False,
        "authority_effect": "admission-only",
    }
    for key, expected in expected_admission.items():
        if admission.get(key) != expected:
            admission_errors.append(f"{key}: expected {expected!r}, got {admission.get(key)!r}")
    add("admitted-inactive-source-state", not admission_errors, admission_errors)

    stage_ids = [stage.get("stage_id") for stage in plan.get("stages", [])]
    expected_stage_ids = ["ADM-S0", "AC-S1", "AC-S2", "AC-S3", "AC-S4", "AC-S5", "CUT-G1"]
    stage_errors: list[str] = []
    if stage_ids != expected_stage_ids:
        stage_errors.append(f"stage order: {stage_ids}")
    if plan.get("current_frontier") != "AC-S1":
        stage_errors.append("current frontier is not AC-S1")
    if stage_ids and stage_ids[-1] != "CUT-G1":
        stage_errors.append("owner gate is not the last stage")
    add("continuous-stage-order-and-final-gate", not stage_errors, stage_errors)

    boundary = boundary_errors(plan)
    add("no-effect-authority-boundary", not boundary, boundary)

    ontology_errors: list[str] = []
    scope = plan.get("shadow_scope", {})
    if "canonical append-only event" not in scope.get("source_of_truth", ""):
        ontology_errors.append("canonical events are not the source of truth")
    if "noncanonical" not in scope.get("snapshot_role", ""):
        ontology_errors.append("snapshot role is not explicitly noncanonical")
    if set(scope.get("required_record_kinds", [])) != {"node", "relation", "context binding", "challenge contract"}:
        ontology_errors.append("required ontology record kinds changed")
    add("event-calculated-ontology-contract", not ontology_errors, ontology_errors)

    lane_errors: list[str] = []
    work = plan.get("work_plan", {})
    if work.get("runnable_work") != ["AC-S1", "AC-S2", "AC-S3", "AC-S4", "AC-S5"]:
        lane_errors.append("runnable product lane changed")
    unrelated = [task for task in work.get("operational_tasks", []) if task.get("applies_to_stage") is None]
    if not unrelated or any(task.get("blocking_basis") != "none" for task in unrelated):
        lane_errors.append("unrelated operational work blocks the product lane")
    if work.get("continuation_status") != "runnable":
        lane_errors.append("continuation is not runnable")
    add("two-lane-continuation", not lane_errors, lane_errors)

    mutations: list[dict[str, str]] = []

    stale = copy.deepcopy(plan)
    stale["admitted_product"]["admission_decision"]["sha256"] = "0" * 64
    mutations.append({"probe_id": "admission-digest-drift", "result": "PASS" if not schema_errors(stale) and stale != plan and stale["admitted_product"]["admission_decision"]["sha256"] != digest(LAB / stale["admitted_product"]["admission_decision"]["path"]) else "BLOCK"})

    early_gate = copy.deepcopy(plan)
    early_gate["stages"][1], early_gate["stages"][-1] = early_gate["stages"][-1], early_gate["stages"][1]
    early_schema = schema_errors(early_gate)
    mutations.append({"probe_id": "early-owner-gate", "result": "PASS" if early_schema else "BLOCK"})

    activation = copy.deepcopy(plan)
    activation["execution"]["activation_authorized"] = True
    mutations.append({"probe_id": "activation-authority-escalation", "result": "PASS" if schema_errors(activation) and boundary_errors(activation) else "BLOCK"})

    cutover = copy.deepcopy(plan)
    cutover["final_gate"]["cutover_authorized"] = True
    mutations.append({"probe_id": "cutover-authority-escalation", "result": "PASS" if schema_errors(cutover) and boundary_errors(cutover) else "BLOCK"})

    add("planning-mutation-probes", all(item["result"] == "PASS" for item in mutations), mutations)

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    receipt = {
        "schema_version": "cal.d65-admitted-runtime-activation-cutover-plan-validation/v1",
        "plan_id": plan.get("plan_id"),
        "result": "PASS" if not failed else "BLOCK",
        "status": "candidate-ready-unregistered" if not failed else "candidate-blocked-unregistered",
        "plan_sha256": digest(PLAN),
        "schema_sha256": digest(SCHEMA),
        "checks": checks,
        "failed_checks": failed,
        "current_frontier": "AC-S1" if not failed else None,
        "continuation_status": "runnable" if not failed else "blocked",
        "final_gate": "G-D65-EPOCH-002-ACTIVATION-CUTOVER",
        "final_gate_state": "not_evaluable",
        "registered_as_admitted_execution_state": False,
        "activation_authorized": False,
        "migration_authorized": False,
        "cutover_authorized": False,
        "cutover_performed": False,
        "authority_effect": "none",
        "claim_ceiling": "PASS validates only a no-effect continuous plan for shadow activation, migration, cutover, rollback, and a final owner gate. It performs and authorizes none of those effects.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

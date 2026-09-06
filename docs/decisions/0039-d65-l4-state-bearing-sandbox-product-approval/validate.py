#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CANDIDATE = HERE / "product-candidate.json"
REQUEST = HERE / "product-approval-request.json"
ADMISSIBILITY_REQUEST = HERE / "admissibility-request.json"
ADMISSIBILITY_RECEIPT = HERE / "admissibility-receipt.json"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "receipts/validation.json"
DECISION = HERE / "decision.json"
L4_VALIDATOR = LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/v1/validate-l4.py"
EXPECTED_OPTIONS = {
    "L4PAPP-1": "product-approval-only",
    "L4PAPP-2": "product-rejection-only",
    "L4PAPP-3": "none",
    "L4PAPP-4": "none",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def current(path_value: Any, digest_value: Any) -> bool:
    path = LAB / str(path_value or "")
    return path.is_file() and digest(path) == digest_value


def candidate_errors(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence_ref = candidate.get("product_test_evidence", {})
    evidence_path = LAB / str(evidence_ref.get("path", ""))
    if not current(evidence_ref.get("path"), evidence_ref.get("sha256")):
        errors.append("product-test-evidence-digest-mismatch")
        return errors
    evidence = load(evidence_path)
    required_evidence = (
        evidence.get("candidate_id")
        == "CAL-D65-EPOCH-003-STATE-BEARING-SANDBOX-PROTOTYPE-005"
        and evidence.get("candidate_identity")
        == "cal.prototype.rust-state-bearing-sandbox-target/epoch-003"
        and evidence.get("result") == "PASS"
        and evidence.get("deterministic_runs") == 2
        and evidence.get("rust_tests_per_run") == 35
        and evidence.get("contract", {}).get("result") == "PASS"
        and evidence.get("contract", {}).get("invariant_count") == 7
        and evidence.get("sandbox_report_deterministic") is True
        and evidence.get("state_survives_activation_observation") is True
        and evidence.get("explicit_teardown_verified") is True
        and evidence.get("cleanup_verified") is True
        and evidence.get("selected_dependencies_current") is True
        and evidence.get("product_approved") is False
        and evidence.get("adapter_admitted") is False
        and evidence.get("runtime_activated") is False
        and evidence.get("live_execution_ready") is False
        and evidence.get("external_effects") is False
        and evidence.get("authority_effect") == "none"
    )
    if not required_evidence:
        errors.append("product-test-evidence-claim-mismatch")
    inputs = evidence.get("inputs", [])
    if len(inputs) != 24 or any(
        not current(item.get("path"), item.get("sha256")) for item in inputs
    ):
        errors.append("frozen-input-set-not-current")
    frozen = candidate.get("frozen_input_set", {})
    if (
        frozen.get("input_count") != len(inputs)
        or frozen.get("canonical_input_set_sha256") != canonical_digest(inputs)
        or frozen.get("all_inputs_current_at_freeze") is not True
    ):
        errors.append("frozen-input-set-binding-mismatch")
    for ref_kind in ("selection_refs", "planning_refs", "predecessor_receipts"):
        if any(
            not current(item.get("path"), item.get("sha256"))
            for item in candidate.get(ref_kind, [])
        ):
            errors.append(f"{ref_kind.replace('_', '-')}-digest-mismatch")
    target = candidate.get("target_boundary", {})
    expected_target = {
        "kind": "filesystem-state-bearing-sandbox-target",
        "identity": "cal.prototype.rust-state-bearing-sandbox-target/epoch-003",
        "caller_supplied_path": False,
        "credential_kind": "none",
        "live": False,
        "production_data": False,
        "network": False,
        "state_survival_boundary": "activation-return-to-explicit-teardown",
        "local_disposable_filesystem_effects": True,
        "migration_performed": False,
        "cutover_performed": False,
        "runtime_activated": False,
        "external_effects": False,
    }
    if target != expected_target:
        errors.append("target-boundary-mismatch")
    blocked_true = (
        candidate.get("adapter_admitted"),
        candidate.get("runtime_activated"),
        candidate.get("live_execution_ready"),
        candidate.get("migration_authorized"),
        candidate.get("cutover_authorized"),
        candidate.get("publication_authorized"),
        candidate.get("deployment_authorized"),
    )
    if (
        any(value is not False for value in blocked_true)
        or candidate.get("product_approval") != "not-requested"
        or candidate.get("authority_effect") != "none"
    ):
        errors.append("candidate-authority-ceiling-violated")
    return errors


def request_errors(request: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not current(
        request.get("product_candidate_path"), request.get("product_candidate_sha256")
    ):
        errors.append("candidate-manifest-digest-mismatch")
    if not current(
        request.get("product_test_evidence_path"),
        request.get("product_test_evidence_sha256"),
    ):
        errors.append("product-test-evidence-digest-mismatch")
    options = {
        option.get("option_id"): option.get("authority_effect")
        for option in request.get("options", [])
    }
    if options != EXPECTED_OPTIONS or len(request.get("options", [])) != 4:
        errors.append("approval-option-set-mismatch")
    if (
        request.get("eligibility") != "eligible"
        or request.get("decision_state") != "not-decided"
        or request.get("product_approval")
        != "not-requested-from-user-by-this-artifact"
        or request.get("adapter_admitted") is not False
        or request.get("runtime_activated") is not False
        or request.get("live_execution_ready") is not False
        or request.get("cutover_authorized") is not False
        or request.get("external_effect_authorized") is not False
        or request.get("authority_effect") != "none"
    ):
        errors.append("request-authority-ceiling-violated")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    candidate = load(CANDIDATE)
    request = load(REQUEST)
    schema = load(SCHEMA)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({
            "check_id": check_id,
            "result": "PASS" if passed else "BLOCK",
            "detail": detail,
        })

    candidate_schema_errors = [
        error.message for error in Draft202012Validator(schema).iter_errors(candidate)
    ]
    request_schema_errors = [
        error.message for error in Draft202012Validator(schema).iter_errors(request)
    ]
    add(
        "packet-schema",
        not candidate_schema_errors and not request_schema_errors,
        {"candidate": candidate_schema_errors, "request": request_schema_errors},
    )

    live_validation = subprocess.run(
        [sys.executable, str(L4_VALIDATOR)],
        cwd=L4_VALIDATOR.parent,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    live_summary: dict[str, Any] = {}
    try:
        live_summary = json.loads(live_validation.stdout)
    except json.JSONDecodeError:
        pass
    add(
        "live-product-tests",
        live_validation.returncode == 0
        and live_summary.get("result") == "PASS"
        and live_summary.get("rust_tests_per_run") == 35
        and live_summary.get("invariants") == 7
        and live_summary.get("state_survives_activation_observation") is True
        and live_summary.get("explicit_teardown_verified") is True,
        {
            "exit": live_validation.returncode,
            "summary": live_summary,
            "tail": live_validation.stdout[-2000:] if live_validation.returncode else "",
        },
    )

    candidate_failures = candidate_errors(candidate)
    add("frozen-tested-product", not candidate_failures, candidate_failures)
    request_failures = request_errors(request)
    add("undecided-approval-request", not request_failures, request_failures)

    admissibility_request = load(ADMISSIBILITY_REQUEST)
    admissibility_receipt = load(ADMISSIBILITY_RECEIPT)
    admissibility_failures: list[str] = []
    if admissibility_receipt.get("requestDigest") != canonical_digest(
        admissibility_request
    ):
        admissibility_failures.append("canonical-request-digest-mismatch")
    if (
        admissibility_receipt.get("decisionId") != "CAL-D65-L4PAPP-0039"
        or admissibility_receipt.get("routeOutcome") != "gate"
        or admissibility_receipt.get("decisionGateRequired") is not True
        or set(admissibility_receipt.get("admissibleOptionIds", []))
        != set(EXPECTED_OPTIONS)
        or set(admissibility_receipt.get("presentedOptionIds", []))
        != set(EXPECTED_OPTIONS)
        or admissibility_receipt.get("rejectedOptions") != []
    ):
        admissibility_failures.append("four-option-owner-gate-mismatch")
    add("option-admissibility", not admissibility_failures, admissibility_failures)

    add(
        "owner-selection-absent",
        not DECISION.exists(),
        {
            "decision_path": str(DECISION.relative_to(LAB)),
            "decision_exists": DECISION.exists(),
        },
    )

    probes: list[dict[str, str]] = []
    mutated_candidate = copy.deepcopy(candidate)
    mutated_candidate["target_boundary"]["live"] = True
    probes.append({
        "probe_id": "live-target-escalation",
        "result": "PASS" if candidate_errors(mutated_candidate) else "BLOCK",
    })
    mutated_candidate = copy.deepcopy(candidate)
    mutated_candidate["target_boundary"]["runtime_activated"] = True
    probes.append({
        "probe_id": "runtime-activation-escalation",
        "result": "PASS" if candidate_errors(mutated_candidate) else "BLOCK",
    })
    mutated_request = copy.deepcopy(request)
    mutated_request["product_candidate_sha256"] = "0" * 64
    probes.append({
        "probe_id": "candidate-digest-substitution",
        "result": "PASS" if request_errors(mutated_request) else "BLOCK",
    })
    mutated_request = copy.deepcopy(request)
    mutated_request["decision_state"] = "selected"
    probes.append({
        "probe_id": "implicit-selection",
        "result": "PASS" if request_errors(mutated_request) else "BLOCK",
    })
    mutated_request = copy.deepcopy(request)
    mutated_request["options"][0]["authority_effect"] = "external-effect"
    probes.append({
        "probe_id": "approval-authority-escalation",
        "result": "PASS" if request_errors(mutated_request) else "BLOCK",
    })
    add(
        "mutation-probes",
        all(probe["result"] == "PASS" for probe in probes),
        probes,
    )

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    validation = {
        "schema_version": "cal.d65-l4-product-approval-packet-validation/v1",
        "decision_id": "CAL-D65-L4PAPP-0039",
        "gate_id": "G-D65-L4-STATE-BEARING-SANDBOX-PRODUCT-APPROVAL",
        "result": result,
        "stage_state": "PRODUCT_APPROVAL_PACKET_READY" if result == "PASS" else "not_evaluable",
        "checks": checks,
        "failed_checks": failed,
        "product_candidate_id": candidate.get("product_candidate_id"),
        "product_candidate_sha256": digest(CANDIDATE),
        "product_test_evidence_sha256": request.get("product_test_evidence_sha256"),
        "product_approval_eligible": result == "PASS",
        "decision_gate_required": result == "PASS",
        "decision_state": "not-decided",
        "product_approval": "not-requested",
        "adapter_admitted": False,
        "runtime_activated": False,
        "live_execution_ready": False,
        "cutover_authorized": False,
        "external_effect_authorized": False,
        "authority_effect": "none",
        "inputs": [
            {"path": str(path.relative_to(LAB)), "sha256": digest(path)}
            for path in (
                CANDIDATE, REQUEST, ADMISSIBILITY_REQUEST,
                ADMISSIBILITY_RECEIPT, SCHEMA, HERE / "DECISION.md",
                HERE / "README.md", HERE / "validate.py",
            )
        ],
        "claim_ceiling": "PASS proves only that the exact tested L4 state-bearing sandbox product candidate has a current, structurally admissible, undecided approval packet. It does not approve or admit the adapter, activate a governed runtime, authorize live execution, migration, cutover, publication, deployment, credentials, destructive action, or external effects.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        key: validation[key]
        for key in (
            "decision_id", "gate_id", "result", "failed_checks",
            "stage_state", "product_approval_eligible",
            "decision_gate_required", "decision_state", "product_approval",
            "adapter_admitted", "runtime_activated", "live_execution_ready",
            "cutover_authorized", "authority_effect",
        )
    }, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

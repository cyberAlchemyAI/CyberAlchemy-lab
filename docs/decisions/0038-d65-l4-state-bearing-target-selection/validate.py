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
CANDIDATE = HERE / "target-selection-candidate.json"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "candidate-validation.json"
DECISION = HERE / "decision.json"
ADMISSION_VALIDATOR = LAB / "docs/decisions/0037-d65-l3-filesystem-adapter-admission/validate-decision.py"
EXPECTED_PRESENTED = {"L4TGT-1", "L4TGT-4", "L4TGT-5"}
EXPECTED_REJECTED = {"L4TGT-2", "L4TGT-3"}


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


def boundary_errors(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evaluation = candidate.get("direct_activation_evaluation", {})
    evidence = evaluation.get("evidence", {})
    successor = candidate.get("recommended_successor", {})
    non_effects = candidate.get("candidate_non_effects", {})
    if candidate.get("decision_state") != "not-decided":
        errors.append("candidate contains an owner selection")
    if candidate.get("authority_effect") != "none":
        errors.append("candidate carries authority")
    if evaluation.get("result") != "not_evaluable":
        errors.append("direct activation was inflated into an evaluable claim")
    required_evidence = {
        "always_rollback": True,
        "cleanup_required": True,
        "target_directory_absent_after_return": True,
        "live_mode_rejected_before_mutation": True,
        "runtime_activated": False,
        "live_execution_ready": False,
    }
    if any(evidence.get(key) != value for key, value in required_evidence.items()):
        errors.append("direct activation evidence does not preserve the L3 boundary")
    if successor.get("option_id") != "L4TGT-1" or successor.get("authority_effect") != "none":
        errors.append("recommended successor exceeds a non-effectful recommendation")
    if any(value is not False for value in non_effects.values()):
        errors.append("candidate non-effects contain a granted effect")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    candidate = load(CANDIDATE)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append(
            {
                "check_id": check_id,
                "result": "PASS" if passed else "BLOCK",
                "detail": detail,
            }
        )

    schema_errors = [
        error.message
        for error in Draft202012Validator(load(SCHEMA)).iter_errors(candidate)
    ]
    add("candidate-schema", not schema_errors, schema_errors)

    predecessor = candidate["admitted_predecessor"]
    refs = (
        ("admission_decision_path", "admission_decision_sha256"),
        ("admission_validation_path", "admission_validation_sha256"),
        ("admission_candidate_path", "admission_candidate_sha256"),
        ("rehearsal_evidence_path", "rehearsal_evidence_sha256"),
        ("adapter_source_path", "adapter_source_sha256"),
        ("engine_binding_path", "engine_binding_sha256"),
    )
    drift = []
    for path_key, hash_key in refs:
        path = LAB / predecessor[path_key]
        actual = digest(path) if path.is_file() else None
        if actual != predecessor[hash_key]:
            drift.append(
                {
                    "path": predecessor[path_key],
                    "expected": predecessor[hash_key],
                    "actual": actual,
                }
            )
    add("exact-predecessor-currentness", not drift, drift)

    decision = load(LAB / predecessor["admission_decision_path"])
    validation = load(LAB / predecessor["admission_validation_path"])
    admission_candidate = load(LAB / predecessor["admission_candidate_path"])
    rehearsal = load(LAB / predecessor["rehearsal_evidence_path"])
    closure = (
        decision.get("selected_option", {}).get("option_id") == "L3AADM-1"
        and decision.get("adapter_admission", {}).get("state") == "admitted"
        and decision.get("adapter_admission", {}).get("identity")
        == predecessor["adapter_identity"]
        and decision.get("adapter_admission", {}).get("scope")
        == predecessor["admission_scope"]
        and validation.get("result") == "PASS"
        and validation.get("stage_state") == "ADAPTER_ADMITTED"
        and validation.get("adapter_admitted") is True
        and validation.get("runtime_activated") is False
        and validation.get("live_execution_ready") is False
        and validation.get("authority_effect") == "adapter-admission-only"
        and admission_candidate.get("adapter_binding", {}).get("always_rollback") is True
        and admission_candidate.get("adapter_binding", {}).get("cleanup_required") is True
        and admission_candidate.get("adapter_binding", {}).get("live") is False
        and rehearsal.get("result") == "PASS"
        and rehearsal.get("rehearsal_report", {}).get("rollback_exact") is True
        and rehearsal.get("cleanup_verified") is True
        and rehearsal.get("runtime_activated") is False
        and rehearsal.get("live_execution_ready") is False
        and rehearsal.get("external_effects") is False
    )
    add(
        "admitted-disposable-predecessor-closure",
        closure,
        {
            "admission": validation.get("result"),
            "adapter_admitted": validation.get("adapter_admitted"),
            "runtime_activated": validation.get("runtime_activated"),
            "rollback_exact": rehearsal.get("rehearsal_report", {}).get("rollback_exact"),
            "cleanup_verified": rehearsal.get("cleanup_verified"),
        },
    )

    admissibility = candidate["admissibility"]
    request_path = LAB / admissibility["request_path"]
    receipt_path = LAB / admissibility["receipt_path"]
    request = load(request_path)
    prefilter = load(receipt_path)
    rejected_ids = {item.get("optionId") for item in prefilter.get("rejectedOptions", [])}
    option_ids = {item.get("option_id") for item in candidate["presented_options"]}
    candidate_rejected_ids = {item.get("option_id") for item in candidate["rejected_options"]}
    admissible = (
        digest(request_path) == admissibility["request_sha256"]
        and digest(receipt_path) == admissibility["receipt_sha256"]
        and prefilter.get("requestDigest") == canonical_digest(request)
        and prefilter.get("routeOutcome") == "gate"
        and prefilter.get("decisionGateRequired") is True
        and set(prefilter.get("admissibleOptionIds", []))
        == set(prefilter.get("presentedOptionIds", []))
        == set(admissibility["admissible_option_ids"])
        == option_ids
        == EXPECTED_PRESENTED
        and rejected_ids
        == set(admissibility["rejected_option_ids"])
        == candidate_rejected_ids
        == EXPECTED_REJECTED
    )
    add(
        "decision-gate-admissibility",
        admissible,
        {
            "route_outcome": prefilter.get("routeOutcome"),
            "presented": sorted(option_ids),
            "rejected": sorted(rejected_ids),
        },
    )

    boundary = boundary_errors(candidate)
    add("vacuity-and-authority-boundary", not boundary, boundary)
    add("owner-selection-absent", not DECISION.exists(), {"decision_exists": DECISION.exists()})

    live_validation = subprocess.run(
        [sys.executable, str(ADMISSION_VALIDATOR)],
        cwd=LAB,
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
        "current-admission-and-product-tests",
        live_validation.returncode == 0
        and live_summary.get("result") == "PASS"
        and live_summary.get("stage_state") == "ADAPTER_ADMITTED"
        and live_summary.get("adapter_admitted") is True
        and live_summary.get("runtime_activated") is False,
        {
            "exit": live_validation.returncode,
            "summary": live_summary,
            "tail": live_validation.stdout[-2000:] if live_validation.returncode else "",
        },
    )

    probes: list[dict[str, str]] = []
    mutations = {
        "implicit-owner-selection": ("decision_state", "selected"),
        "direct-activation-inflation": ("direct_activation_evaluation.result", "PASS"),
        "rollback-erasure": ("direct_activation_evaluation.evidence.always_rollback", False),
        "successor-authority-escalation": ("recommended_successor.authority_effect", "activation-authorization"),
        "runtime-activation-escalation": ("candidate_non_effects.runtime_activated", True),
        "live-execution-escalation": ("candidate_non_effects.live_execution_ready", True),
        "external-effect-escalation": ("candidate_non_effects.external_effect_authorized", True),
    }
    for probe_id, (path_text, value) in mutations.items():
        mutated = copy.deepcopy(candidate)
        target: Any = mutated
        parts = path_text.split(".")
        for part in parts[:-1]:
            target = target[part]
        target[parts[-1]] = value
        probes.append(
            {
                "probe_id": probe_id,
                "result": "PASS" if boundary_errors(mutated) else "BLOCK",
            }
        )
    add(
        "candidate-mutation-probes",
        all(probe["result"] == "PASS" for probe in probes),
        probes,
    )

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-l4-state-bearing-target-selection-validation/v1",
        "candidate_id": candidate.get("candidate_id"),
        "decision_id": candidate.get("decision_id"),
        "gate_id": candidate.get("gate_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "candidate_frozen": result == "PASS",
        "decision_gate_ready": result == "PASS",
        "decision_state": "not-decided",
        "direct_activation": "not_evaluable",
        "recommended_option_id": "L4TGT-1",
        "admissible_option_ids": sorted(option_ids),
        "rejected_option_ids": sorted(rejected_ids),
        "product_direction_selected": False,
        "prototype_construction_started": False,
        "runtime_activated": False,
        "live_execution_ready": False,
        "cutover_authorized": False,
        "external_effect_authorized": False,
        "authority_effect": "none",
        "inputs": [
            {
                "path": str(path.relative_to(LAB)),
                "sha256": digest(path),
            }
            for path in (
                CANDIDATE,
                SCHEMA,
                request_path,
                receipt_path,
                LAB / predecessor["admission_decision_path"],
                LAB / predecessor["admission_validation_path"],
                LAB / predecessor["admission_candidate_path"],
                LAB / predecessor["rehearsal_evidence_path"],
                LAB / predecessor["adapter_source_path"],
                LAB / predecessor["engine_binding_path"],
                HERE / "DECISION.md",
                HERE / "README.md",
                HERE / "validate.py",
            )
        ],
        "claim_ceiling": "PASS proves only that direct activation of the admitted disposable adapter is not evaluable without vacuity and that L4TGT-1, L4TGT-4, and L4TGT-5 are ready for one owner decision. It selects no direction, starts no construction, approves or admits no successor, activates no runtime, and authorizes no live execution, migration, cutover, publication, deployment, or external effect.",
    }
    if args.write_receipt:
        RECEIPT.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        json.dumps(
            {
                key: receipt[key]
                for key in (
                    "candidate_id",
                    "decision_id",
                    "gate_id",
                    "result",
                    "failed_checks",
                    "candidate_frozen",
                    "decision_gate_ready",
                    "decision_state",
                    "direct_activation",
                    "recommended_option_id",
                    "admissible_option_ids",
                    "rejected_option_ids",
                    "runtime_activated",
                    "live_execution_ready",
                    "cutover_authorized",
                    "external_effect_authorized",
                    "authority_effect",
                )
            },
            indent=2,
        )
    )
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

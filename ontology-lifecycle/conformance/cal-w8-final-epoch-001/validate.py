#!/usr/bin/env python3
"""Collect-all W8 validation over one exact W0-W7 candidate epoch."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
EPOCH = SCRIPT.parent
LAB = SCRIPT.parents[3]
MANIFEST = EPOCH / "manifest.json"
VERDICT = EPOCH / "verdict.json"
W1_RUNNER = LAB / "ontology-lifecycle/scripts/validate-governed-node-schemas.py"
W1_RECEIPT = LAB / "ontology-lifecycle/conformance/w1-schema-validation.json"
W2_RECEIPT = LAB / "ontology-lifecycle/conformance/w2-model-validation.json"
W3_RECEIPT = LAB / "ontology-lifecycle/conformance/w3-source-validation.json"
W4_RECEIPT = LAB / "ontology-lifecycle/conformance/w4-gate.json"
W5_RECEIPT = LAB / "ontology-lifecycle/conformance/w5-runtime-validation.json"
W6_RUNNER = LAB / "ontology-lifecycle/scripts/validate-w6-conformance.py"
W6_BINDING = LAB / "ontology-lifecycle/conformance/construction-binding.json"
W6_VERIFICATION = LAB / "ontology-lifecycle/conformance/verification.json"
W6_DECISION = LAB / "docs/decisions/0010-w6-candidate-acceptance/decision.json"
W7_DIR = LAB / "ontology-lifecycle/migration/cal-w7-ontology-product-epoch-001"
W7_RUNNER = W7_DIR / "fixtures/validate.py"
W7_RECEIPT = W7_DIR / "receipt.json"
W7_DECISION = LAB / "docs/decisions/0011-w7-legacy-slice-selection/decision.json"
W0_DECISION = LAB / "docs/decisions/0005-governed-ontology-node-architecture/decision.json"
W2_DECISION = LAB / "docs/decisions/0009-w2-product-business-admission/decision.json"
W3_DECISION = LAB / "docs/decisions/0008-domainspec-development-profile-admission/decision.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def stable_write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(
    arguments: list[str], cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env=env,
    )


def parse_json_output(output: str) -> dict[str, Any] | None:
    try:
        value = json.loads(output)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def find_node() -> str | None:
    direct = shutil.which("node")
    if direct:
        return direct
    candidates = sorted(Path("/home/vrondelli/.nvm/versions/node").glob("v*/bin/node"))
    return str(candidates[-1]) if candidates else None


def tree_digest(root: Path) -> str:
    entries = [
        {"path": path.relative_to(root).as_posix(), "sha256": digest(path)}
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    ]
    preimage = "".join(f"{item['path']}\0{item['sha256']}\n" for item in entries)
    return hashlib.sha256(preimage.encode("utf-8")).hexdigest()


def verify_refs(refs: list[dict[str, Any]], root: Path) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for ref in refs:
        path = root / ref["path"]
        if not path.is_file():
            failures.append({"path": ref["path"], "failure": "missing"})
        elif digest(path) != ref["sha256"]:
            failures.append({"path": ref["path"], "failure": "digest-mismatch"})
    return failures


def verify_receipt_inputs(path: Path) -> list[dict[str, str]]:
    value = load(path)
    refs = value.get("inputs", [])
    if not isinstance(refs, list):
        return [{"path": str(path.relative_to(LAB)), "failure": "inputs-not-list"}]
    return verify_refs(refs, LAB)


def isolated_w1() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="cal-w8-w1-") as raw:
        receipt_path = Path(raw) / "w1-schema-validation.json"
        spec = importlib.util.spec_from_file_location("cal_w8_w1_validator", W1_RUNNER)
        if spec is None or spec.loader is None:
            return {"exit_code": 1, "receipt_equal": False, "result": None}
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.RECEIPT = receipt_path
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                exit_code = int(module.main())
        except Exception as exc:  # collect-all evidence, never hide the failure
            return {"exit_code": 1, "receipt_equal": False, "result": None, "error": type(exc).__name__}
        generated = load(receipt_path) if receipt_path.is_file() else None
        accepted = load(W1_RECEIPT)
        return {
            "exit_code": exit_code,
            "result": generated.get("result") if isinstance(generated, dict) else None,
            "receipt_equal": receipt_path.is_file() and receipt_path.read_bytes() == W1_RECEIPT.read_bytes(),
            "negative_witness_count": len(generated.get("negative_witnesses", [])) if isinstance(generated, dict) else 0,
            "all_negative_witnesses_pass": bool(generated)
            and all(item.get("result") == "PASS" for item in generated.get("negative_witnesses", [])),
            "accepted_result": accepted.get("result"),
        }


def result_map(checks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["check_id"]: item for item in checks}


def run_once(manifest: dict[str, Any], node: str | None) -> dict[str, Any]:
    dependency_failures = verify_refs(manifest["dependencies"], LAB)
    external = manifest["selected_external_dependencies"]
    external_failures = verify_refs(external["files"], Path(external["source_repository"]))
    epoch_current = not dependency_failures and not external_failures

    # Independent checks all execute even if another predecessor fails.
    w1_run = isolated_w1()
    w6_command = [sys.executable, str(W6_RUNNER)]
    if node:
        w6_command.extend(["--node", node])
    w6_env = dict(os.environ)
    complete_rust_toolchain = Path(
        "/home/vrondelli/.rustup/toolchains/1.94.1-x86_64-unknown-linux-gnu/bin"
    )
    if complete_rust_toolchain.is_dir():
        w6_env["PATH"] = str(complete_rust_toolchain) + os.pathsep + w6_env.get("PATH", "")
    w6_process = run(w6_command, LAB, w6_env)
    w6_run = parse_json_output(w6_process.stdout)
    w7_process = run([sys.executable, str(W7_RUNNER)], LAB)
    w7_run = parse_json_output(w7_process.stdout)

    w0 = load(W0_DECISION)
    w1 = load(W1_RECEIPT)
    w2 = load(W2_RECEIPT)
    w3 = load(W3_RECEIPT)
    w4 = load(W4_RECEIPT)
    w5 = load(W5_RECEIPT)
    binding = load(W6_BINDING)
    verification = load(W6_VERIFICATION)
    w6_decision = load(W6_DECISION)
    w7 = load(W7_RECEIPT)
    w7_decision = load(W7_DECISION)
    w2_decision = load(W2_DECISION)
    w3_decision = load(W3_DECISION)
    w6_checks = result_map(verification.get("checks", []))
    w7_checks = result_map(w7.get("checks", []))

    input_failures = {
        "W1": verify_receipt_inputs(W1_RECEIPT),
        "W2": verify_receipt_inputs(W2_RECEIPT),
        "W3": verify_receipt_inputs(W3_RECEIPT),
        "W4": verify_receipt_inputs(W4_RECEIPT),
        "W5": verify_receipt_inputs(W5_RECEIPT),
        "W6": verify_receipt_inputs(W6_VERIFICATION),
    }
    binding_failures = verify_refs(binding.get("artifact_bindings", []), LAB)
    output_digest = tree_digest(W7_DIR / "fixtures/output")

    w0_pass = (
        epoch_current
        and w0.get("selection", {}).get("option_id") == "GONA-1"
        and w0.get("decision_gate_result", {}).get("result") == "PASS"
        and digest(LAB / w0["selected_proposal"]["path"]) == w0["selected_proposal"]["sha256"]
        and digest(LAB / w0["plan_binding"]["path"]) == w0["plan_binding"]["sha256"]
    )
    w1_pass = (
        w1.get("result") == "PASS"
        and not input_failures["W1"]
        and w1_run.get("exit_code") == 0
        and w1_run.get("result") == "PASS"
        and w1_run.get("receipt_equal") is True
        and w1_run.get("all_negative_witnesses_pass") is True
    )
    w2_pass = (
        w2.get("result") == "PASS"
        and not input_failures["W2"]
        and w2_decision.get("decision_source", {}).get("selection_token") == "W2ADM-1"
        and w2_decision.get("admission_status") == "admitted"
    )
    w3_pass = (
        w3.get("result") == "PASS"
        and not input_failures["W3"]
        and w3_decision.get("decision_source", {}).get("selection_token") == "DPADM-1"
        and w3_decision.get("admission_status") == "admitted"
    )
    w4_pass = w4.get("result") == "PASS" and not input_failures["W4"] and not w4.get("blockers")
    w5_pass = w5.get("result") == "PASS" and not input_failures["W5"] and not w5.get("blockers")
    accepted_refs = w6_decision.get("accepted_w6_epoch", {})
    w6_acceptance_pass = (
        w6_decision.get("decision_source", {}).get("selection_token") == "W6ACC-1"
        and w6_decision.get("acceptance_status") == "accepted-for-isolated-w7-rehearsal"
        and accepted_refs.get("construction_binding_ref", {}).get("sha256") == digest(W6_BINDING)
        and accepted_refs.get("verification_ref", {}).get("sha256") == digest(W6_VERIFICATION)
        and accepted_refs.get("d65_status_ref", {}).get("sha256")
        == digest(LAB / "ontology-lifecycle/conformance/d65-status.json")
    )
    w6_technical_pass = (
        verification.get("technical_result") == "PASS"
        and all(item.get("result") == "PASS" for item in verification.get("checks", []))
        and not input_failures["W6"]
        and not binding_failures
        and not binding.get("residue")
        and w6_process.returncode == 0
        and isinstance(w6_run, dict)
        and w6_run.get("technical_result") == "PASS"
        and not w6_run.get("failed_checks")
    )
    w6_pass = w6_technical_pass and w6_acceptance_pass
    w7_pass = (
        w7.get("result") == "PASS"
        and not w7.get("failed_checks")
        and not w7.get("blockers")
        and w7.get("source_bytes_unchanged") is True
        and not w7.get("unclassified_inputs")
        and not w7.get("acceptance_critical_residue")
        and w7.get("determinism", {}).get("byte_identical") is True
        and output_digest == manifest["w7_output_tree_sha256"]
        and w7_decision.get("decision_source", {}).get("selection_token") == "W7SRC-1"
        and w7_process.returncode == 0
        and isinstance(w7_run, dict)
        and w7_run.get("result") == "PASS"
        and w7_run.get("output_tree_digest") == manifest["w7_output_tree_sha256"]
    )

    gates = [
        {"gate_id": "G-W0", "result": "PASS" if w0_pass else "BLOCK"},
        {"gate_id": "G-W1", "result": "PASS" if w1_pass else "BLOCK"},
        {"gate_id": "G-W2", "result": "PASS" if w2_pass else "BLOCK"},
        {"gate_id": "G-W3", "result": "PASS" if w3_pass else "BLOCK"},
        {"gate_id": "G-W4", "result": "PASS" if w4_pass else "BLOCK"},
        {"gate_id": "G-W5", "result": "PASS" if w5_pass else "BLOCK"},
        {
            "gate_id": "G-W6",
            "result": "PASS" if w6_pass else "BLOCK",
            "join": "technical-verification-plus-W6ACC-1",
        },
        {"gate_id": "G-W7", "result": "PASS" if w7_pass else "BLOCK"},
    ]
    predecessors_pass = epoch_current and all(item["result"] == "PASS" for item in gates)

    validations: list[dict[str, Any]] = []

    def add(validation_id: str, passed: bool, detail: dict[str, Any], prerequisite: bool = True) -> None:
        result = "PASS" if prerequisite and passed else ("BLOCK" if prerequisite else "not_evaluable")
        validations.append({"validation_id": validation_id, "result": result, "detail": detail})

    add(
        "VAL-W0-DECISION",
        w0_pass,
        {"selection_token": w0.get("selection", {}).get("option_id"), "dependency_failures": dependency_failures},
    )
    add("VAL-SCHEMA-NEGATIVE", w1_pass, w1_run, prerequisite=w0_pass)
    compile_check = w6_checks.get("domainspec-and-event-contract-two-run", {})
    add(
        "VAL-DOMAINSPEC-TWICE",
        w6_technical_pass and compile_check.get("result") == "PASS" and compile_check.get("detail", {}).get("graph_runs_equal") is True,
        compile_check.get("detail", {}),
        prerequisite=w0_pass and w1_pass and w2_pass and w3_pass and w4_pass and w5_pass,
    )
    add(
        "VAL-EVENT-CONTRACT-TWICE",
        w6_technical_pass and compile_check.get("result") == "PASS" and compile_check.get("detail", {}).get("event_runs_equal") is True,
        compile_check.get("detail", {}),
        prerequisite=w0_pass and w1_pass and w2_pass and w3_pass and w4_pass and w5_pass,
    )
    backend_check = w6_checks.get("domainspec-backend-full-suite", {})
    add(
        "VAL-DOMAINSPEC-BACKEND",
        w6_technical_pass and backend_check.get("result") == "PASS",
        backend_check.get("detail", {}),
        prerequisite=w0_pass and w1_pass and w2_pass and w3_pass and w4_pass and w5_pass,
    )
    rust_check = w6_checks.get("independent-rust-and-mutation-execution", {})
    add(
        "VAL-RUST-RUNTIME",
        w6_technical_pass and rust_check.get("result") == "PASS",
        rust_check.get("detail", {}),
        prerequisite=w0_pass and w1_pass and w2_pass and w3_pass and w4_pass and w5_pass,
    )
    replay_pass = (
        w6_technical_pass
        and w5.get("checks", {}).get("replay_equality") == "PASS"
        and w7_checks.get("replay-equality-and-one-consistent-cut", {}).get("result") == "PASS"
    )
    add(
        "VAL-REPLAY-EQUALITY",
        replay_pass,
        {"w5_replay": w5.get("checks", {}).get("replay_equality"), "w7_replay": w7_checks.get("replay-equality-and-one-consistent-cut", {}).get("result")},
        prerequisite=w6_pass and w7_pass,
    )
    vacuity_pass = (
        w1_run.get("all_negative_witnesses_pass") is True
        and w6_checks.get("runtime-obligation-and-vacuity-contract", {}).get("result") == "PASS"
        and rust_check.get("result") == "PASS"
    )
    add(
        "VAL-VACUITY",
        vacuity_pass,
        {"schema_negative_witnesses": w1_run.get("negative_witness_count"), "rust_individual_vacuity_tests": verification.get("coverage", {}).get("individual_vacuity_tests")},
        prerequisite=w1_pass and w6_pass,
    )
    binding_pass = (
        w6_pass
        and not binding_failures
        and w6_checks.get("exact-artifact-binding-currentness", {}).get("result") == "PASS"
        and w6_checks.get("compiled-node-and-symbol-closure", {}).get("result") == "PASS"
        and w6_checks.get("declared-residue-closure", {}).get("result") == "PASS"
    )
    add(
        "VAL-BINDING-CURRENTNESS",
        binding_pass,
        {"artifact_bindings": len(binding.get("artifact_bindings", [])), "binding_failures": binding_failures},
        prerequisite=w0_pass and w1_pass and w2_pass and w3_pass and w4_pass and w5_pass,
    )
    add(
        "VAL-MIGRATION-REHEARSAL",
        w7_pass,
        {"coverage": w7.get("coverage", {}), "output_tree_sha256": output_digest},
        prerequisite=w6_pass,
    )
    preaggregate_pass = all(item["result"] == "PASS" for item in validations)
    residue = manifest.get("acceptance_critical_residue", [])
    add(
        "VAL-AGGREGATE",
        predecessors_pass and preaggregate_pass and not residue,
        {"predecessor_gates_pass": predecessors_pass, "acceptance_critical_residue": residue},
        prerequisite=True,
    )

    blockers: list[dict[str, Any]] = []
    if dependency_failures:
        blockers.append({"code": "FROZEN_DEPENDENCY_DRIFT", "failures": dependency_failures})
    if external_failures:
        blockers.append({"code": "SELECTED_SOURCE_DRIFT", "failures": external_failures})
    for gate in gates:
        if gate["result"] != "PASS":
            blockers.append({"code": "PREDECESSOR_GATE_NOT_PASS", "gate_id": gate["gate_id"]})
    for validation in validations:
        if validation["result"] != "PASS":
            blockers.append({"code": "VALIDATION_NOT_PASS", "validation_id": validation["validation_id"], "result": validation["result"]})

    result = "PASS" if not blockers else "BLOCK"
    return {
        "result": result,
        "dependency_currentness": {
            "result": "PASS" if epoch_current else "BLOCK",
            "repository_failures": dependency_failures,
            "selected_external_failures": external_failures,
        },
        "gates": gates,
        "validations": validations,
        "acceptance_critical_residue": residue,
        "blockers": blockers,
        "executions": {
            "w1_isolated": {"exit_code": w1_run.get("exit_code"), "receipt_equal": w1_run.get("receipt_equal")},
            "w6_read_only": {"exit_code": w6_process.returncode, "technical_result": w6_run.get("technical_result") if w6_run else None},
            "w7_read_only": {"exit_code": w7_process.returncode, "result": w7_run.get("result") if w7_run else None},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-verdict", action="store_true")
    args = parser.parse_args()
    manifest = load(MANIFEST)
    node = find_node()
    first = run_once(manifest, node)
    second = run_once(manifest, node)
    first_bytes = canonical_bytes(first)
    second_bytes = canonical_bytes(second)
    equal = first_bytes == second_bytes
    final_pass = first["result"] == "PASS" and second["result"] == "PASS" and equal
    blockers = list(first["blockers"])
    if not equal:
        blockers.append({"code": "TWO_RUN_AGGREGATE_DRIFT"})
    verdict = {
        "schema_version": "cal-w8-aggregate-candidate-verdict/v1",
        "epoch_id": manifest["epoch_id"],
        "gate_id": "G-W8-FINAL",
        "result": "PASS" if final_pass else "BLOCK",
        "immutable_epoch": {
            "manifest_path": str(MANIFEST.relative_to(LAB)),
            "manifest_sha256": digest(MANIFEST),
            "validator_path": str(SCRIPT.relative_to(LAB)),
            "validator_sha256": digest(SCRIPT),
        },
        "two_run_determinism": {
            "result": "PASS" if equal else "BLOCK",
            "byte_identical": equal,
            "run_1_sha256": hashlib.sha256(first_bytes).hexdigest(),
            "run_2_sha256": hashlib.sha256(second_bytes).hexdigest(),
        },
        "dependency_currentness": first["dependency_currentness"],
        "predecessor_gates": first["gates"],
        "validations": first["validations"],
        "executions": first["executions"],
        "acceptance_critical_residue": first["acceptance_critical_residue"],
        "blockers": blockers,
        "authority_effect": "none",
        "claim_ceiling": "G-W8-FINAL PASS is a validated candidate verdict for this exact frozen epoch only. It is not ontology admission or acceptance and grants no publication, release, deployment, migration cutover, credential, destructive-action, or external-effect authority.",
    }
    if args.write_verdict:
        stable_write(VERDICT, verdict)
    print(json.dumps({
        "epoch_id": verdict["epoch_id"],
        "gate_id": verdict["gate_id"],
        "result": verdict["result"],
        "two_run_byte_identical": equal,
        "failed_validations": [item["validation_id"] for item in verdict["validations"] if item["result"] != "PASS"],
        "blockers": blockers,
    }, indent=2, sort_keys=True))
    return 0 if final_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

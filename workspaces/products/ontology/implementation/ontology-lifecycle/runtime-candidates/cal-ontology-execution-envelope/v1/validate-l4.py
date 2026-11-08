#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[3]
L4_RECEIPT = HERE / "receipts/stateful-sandbox.json"
CONTRACT_FIXTURE = HERE / "tests/fixtures/stateful-sandbox.json"
CONTRACT_SCHEMA = HERE / "schemas/stateful-sandbox.schema.json"
SANDBOX_SOURCE = HERE / "src/stateful_sandbox_target.rs"
TEST_RE = re.compile(r"^test ([^ ]+) \.\.\. (ok|FAILED|ignored)$")
REPORT_RE = re.compile(r"STATEFUL_SANDBOX_REPORT_JSON=(\{.*\})")
EXPECTED_INVARIANT_IDS = [
    "SBX-01-NEW-IDENTITY",
    "SBX-02-PATH-CONFINEMENT",
    "SBX-03-STATE-SURVIVES-OBSERVATION",
    "SBX-04-EXPLICIT-TEARDOWN",
    "SBX-05-LIVE-REFUSAL",
    "SBX-06-ENGINE-SUBSTITUTION-REFUSAL",
    "SBX-07-DETERMINISTIC-REPORT",
]
SELECTED_DEPENDENCIES = [
    ("docs/decisions/0038-d65-l4-state-bearing-target-selection/decision.json", "405b0a017038f85faea86f686e1289f330375587982772172947577a4c5227dc"),
    ("docs/decisions/0038-d65-l4-state-bearing-target-selection/receipts/decision-validation.json", "cfb97c8d5ea8e0a338a37a1abd6530bcc0d3ba1023223fe10a2c150cfbd6ee87"),
    ("docs/decisions/0037-d65-l3-filesystem-adapter-admission/decision.json", "3fcc48868691d7c7ab6e3fa9bd87062271f8aae895ee0edd93644bc93482885c"),
    ("docs/decisions/0037-d65-l3-filesystem-adapter-admission/receipts/decision-validation.json", "c8165f710e6b5e70371ae07948faf5e8d9c484ead07976f794c13e830cc18e2e"),
    ("ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/v1/receipts/filesystem-rehearsal.json", "24168bc1b692b8ed1893372201349f46e75955aab9c3dd173dc2a32e576f77fc"),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(command: list[str], target: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=HERE,
        env={**os.environ, "CARGO_TARGET_DIR": str(target)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {
        "exit": completed.returncode,
        "tail": completed.stdout[-4000:] if completed.returncode else "",
    }


def run_once(target: Path) -> dict[str, Any]:
    completed = subprocess.run(
        ["cargo", "test", "--locked", "--tests", "--", "--test-threads=1"],
        cwd=HERE,
        env={**os.environ, "CARGO_TARGET_DIR": str(target)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    tests = sorted(
        (match.group(1), match.group(2))
        for line in completed.stdout.splitlines()
        if (match := TEST_RE.match(line.strip()))
    )
    return {
        "exit": completed.returncode,
        "test_count": len(tests),
        "tests": tests,
        "tail": completed.stdout[-4000:] if completed.returncode else "",
    }


def emit_report(target: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [
            "cargo", "test", "--locked", "--test", "stateful_sandbox",
            "stateful_sandbox_report_is_byte_deterministic", "--", "--exact",
            "--nocapture", "--test-threads=1",
        ],
        cwd=HERE,
        env={**os.environ, "CARGO_TARGET_DIR": str(target)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    match = REPORT_RE.search(completed.stdout)
    raw = match.group(1) if match else ""
    try:
        report = json.loads(raw)
    except json.JSONDecodeError:
        report = {}
    return {
        "exit": completed.returncode,
        "raw": raw,
        "report": report,
        "tail": completed.stdout[-4000:] if completed.returncode or not raw else "",
    }


def dependency_records() -> list[dict[str, Any]]:
    records = []
    for relative, expected in SELECTED_DEPENDENCIES:
        path = LAB / relative
        current = digest(path) if path.is_file() else None
        records.append({
            "path": relative,
            "expected_sha256": expected,
            "current_sha256": current,
            "result": "PASS" if current == expected else "BLOCK",
        })
    return records


def contract_result() -> dict[str, Any]:
    contract = json.loads(CONTRACT_FIXTURE.read_text(encoding="utf-8"))
    schema = json.loads(CONTRACT_SCHEMA.read_text(encoding="utf-8"))
    target = contract.get("target", {})
    invariants = contract.get("invariants", [])
    ids = [invariant.get("invariant_id") for invariant in invariants]
    required_target = set(schema["properties"]["target"]["required"])
    passed = (
        contract.get("schema_version") == "cal.d65-state-bearing-sandbox-contract/v1"
        and set(contract) == {"schema_version", "target", "invariants"}
        and set(target) == required_target
        and ids == EXPECTED_INVARIANT_IDS
        and len(set(ids)) == 7
        and target.get("kind") == "filesystem-state-bearing-sandbox-target"
        and target.get("identity") == "cal.prototype.rust-state-bearing-sandbox-target/epoch-003"
        and target.get("path_policy") == "adapter-created-process-temporary-directory"
        and target.get("caller_supplied_path") is False
        and target.get("state_survival_boundary") == "activation-return-to-explicit-teardown"
        and target.get("live") is False
        and target.get("production_data") is False
        and target.get("credential_kind") == "none"
        and target.get("network") is False
        and target.get("external_effects") is False
        and target.get("local_disposable_filesystem_effects") is True
    )
    return {
        "result": "PASS" if passed else "BLOCK",
        "invariant_count": len(invariants),
        "invariant_ids": ids,
        "target": target,
    }


def report_passes(report: dict[str, Any]) -> bool:
    binding = report.get("target_binding", {})
    observation = report.get("observation", {})
    teardown = report.get("teardown", {})
    return (
        report.get("schema_version") == "cal.d65-state-bearing-sandbox-report/v1"
        and report.get("candidate_id") == "CAL-D65-EPOCH-003-STATE-BEARING-SANDBOX-PROTOTYPE-005"
        and report.get("selected_option_id") == "L4TGT-1"
        and report.get("selection_decision_digest") == SELECTED_DEPENDENCIES[0][1]
        and report.get("selection_validation_digest") == SELECTED_DEPENDENCIES[1][1]
        and report.get("predecessor_receipt_digest") == SELECTED_DEPENDENCIES[4][1]
        and binding.get("kind") == "filesystem-state-bearing-sandbox-target"
        and binding.get("identity") == "cal.prototype.rust-state-bearing-sandbox-target/epoch-003"
        and binding.get("credential_kind") == "none"
        and binding.get("live") is False
        and binding.get("production_data") is False
        and binding.get("external_effects") is False
        and observation.get("active_cut_unchanged") is True
        and observation.get("staged_cut_exact") is True
        and observation.get("sandbox_activation_observed") is True
        and observation.get("state_survives_observation") is True
        and observation.get("explicit_teardown_required") is True
        and observation.get("migration_performed") is False
        and observation.get("cutover_performed") is False
        and observation.get("runtime_activated") is False
        and observation.get("external_effects") is False
        and observation.get("preimage_digest") != observation.get("activated_state_digest")
        and teardown.get("restored_preimage_exact") is True
        and teardown.get("restored_state_digest") == observation.get("preimage_digest")
        and teardown.get("cleanup_verified") is True
        and teardown.get("external_effects") is False
        and teardown.get("authority_effect") == "none"
        and report.get("path_policy") == "adapter-created-process-temporary-directory"
        and report.get("local_disposable_filesystem_effects") is True
        and report.get("live_execution_ready") is False
        and report.get("product_approved") is False
        and report.get("adapter_admitted") is False
        and report.get("result") == "PASS"
        and report.get("authority_effect") == "none"
        and len(report.get("report_digest", "")) == 64
    )


def source_boundary_result() -> dict[str, Any]:
    source = SANDBOX_SOURCE.read_text(encoding="utf-8")
    forbidden = [
        "std::net", "TcpStream", "UdpSocket", "credential_kind: \"secret\"",
        "production_data: true", "live: true", "Command::new", "reqwest",
    ]
    passed = (
        all(token not in source for token in forbidden)
        and "pub fn new()" in source
        and "std::env::temp_dir()" in source
        and "pub fn new(path" not in source
        and "pub fn with_root" not in source
        and "STATEFUL_SANDBOX_MIGRATION_FORBIDDEN" in source
        and "STATEFUL_SANDBOX_CUTOVER_FORBIDDEN" in source
    )
    return {
        "result": "PASS" if passed else "BLOCK",
        "forbidden_tokens": forbidden,
        "caller_path_constructor_absent": "pub fn new(path" not in source and "pub fn with_root" not in source,
        "migration_and_cutover_forbidden": "STATEFUL_SANDBOX_MIGRATION_FORBIDDEN" in source and "STATEFUL_SANDBOX_CUTOVER_FORBIDDEN" in source,
    }


def input_records() -> list[dict[str, str]]:
    relative_paths = [
        "Cargo.toml", "Cargo.lock", "src/lib.rs", "src/certification.rs",
        "src/filesystem_target.rs", "src/stateful_sandbox_target.rs",
        "tests/public_contract.rs", "tests/adapter_conformance.rs",
        "tests/certification_contract.rs", "tests/filesystem_rehearsal.rs",
        "tests/stateful_sandbox.rs", "tests/fixtures/certification-vectors.json",
        "tests/fixtures/filesystem-rehearsal.json", "tests/fixtures/stateful-sandbox.json",
        "schemas/certification-vectors.schema.json", "schemas/filesystem-rehearsal.schema.json",
        "schemas/stateful-sandbox.schema.json", "validate.py", "validate-l3.py",
        "validate-l4.py", "README.md", "implementation-layering.md",
    ]
    paths = [HERE / relative for relative in relative_paths] + [
        LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l4/plan.md",
        LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l4/contract.json",
    ]
    return [{"path": str(path.relative_to(LAB)), "sha256": digest(path)} for path in paths]


def sandbox_roots() -> set[str]:
    return {
        str(path)
        for path in Path(tempfile.gettempdir()).glob("cal-d65-state-bearing-sandbox-*")
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    roots_before = sandbox_roots()
    with tempfile.TemporaryDirectory(prefix="cal-d65-rust-stateful-sandbox-") as temporary:
        target = Path(temporary) / "cargo-target"
        formatting = run_command(["cargo", "fmt", "--all", "--", "--check"], target)
        clippy = run_command(["cargo", "clippy", "--locked", "--tests", "--", "-D", "warnings"], target)
        run_a = run_once(target)
        run_b = run_once(target)
        report_a = emit_report(target)
        report_b = emit_report(target)
    roots_after = sandbox_roots()

    dependencies = dependency_records()
    contract = contract_result()
    source_boundary = source_boundary_result()
    report = report_b["report"]
    report_deterministic = (
        report_a["exit"] == report_b["exit"] == 0
        and bool(report_a["raw"])
        and report_a["raw"] == report_b["raw"]
    )
    cleanup_verified = roots_after == roots_before
    repository_target_absent = not (HERE / "target").exists()
    passed = (
        formatting["exit"] == 0
        and clippy["exit"] == 0
        and run_a == run_b
        and run_a["exit"] == 0
        and run_a["test_count"] == 35
        and all(result == "ok" for _, result in run_a["tests"])
        and all(record["result"] == "PASS" for record in dependencies)
        and contract["result"] == "PASS"
        and source_boundary["result"] == "PASS"
        and report_deterministic
        and report_passes(report)
        and cleanup_verified
        and repository_target_absent
    )
    receipt = {
        "schema_version": "cal.d65-state-bearing-sandbox-test-evidence/v1",
        "candidate_id": "CAL-D65-EPOCH-003-STATE-BEARING-SANDBOX-PROTOTYPE-005",
        "candidate_identity": "cal.prototype.rust-state-bearing-sandbox-target/epoch-003",
        "selected_option_id": "L4TGT-1",
        "result": "PASS" if passed else "BLOCK",
        "deterministic_runs": 2,
        "rust_tests_per_run": run_a["test_count"],
        "run_a": run_a,
        "run_b": run_b,
        "formatting": formatting,
        "clippy": clippy,
        "selected_dependencies_current": all(record["result"] == "PASS" for record in dependencies),
        "selected_dependencies": dependencies,
        "contract": contract,
        "source_boundary": source_boundary,
        "sandbox_report_deterministic": report_deterministic,
        "sandbox_report_sha256": hashlib.sha256(report_b["raw"].encode("utf-8")).hexdigest() if report_b["raw"] else None,
        "sandbox_report": report,
        "state_survives_activation_observation": report.get("observation", {}).get("state_survives_observation", False),
        "explicit_teardown_verified": report.get("teardown", {}).get("cleanup_verified", False),
        "cleanup_verified": cleanup_verified,
        "repository_cargo_target_absent": repository_target_absent,
        "local_disposable_filesystem_effects": True,
        "product_approved": False,
        "adapter_admitted": False,
        "live_execution_ready": False,
        "runtime_activated": False,
        "migration_performed": False,
        "cutover_performed": False,
        "external_effects": False,
        "authority_effect": "none",
        "inputs": input_records(),
        "claim_ceiling": "PASS proves the isolated L4 state-bearing local sandbox candidate, distinct binding, bounded state survival through activation observation, exact explicit teardown, live refusal, engine-substitution refusal, failure restoration, and deterministic evidence. It does not approve or admit the candidate, activate a governed runtime, make live execution ready, use credentials, migrate production data, perform an operational cutover, publish, deploy, or authorize external effects.",
    }
    if args.write_receipt:
        L4_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        L4_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_id": receipt["candidate_id"],
        "candidate_identity": receipt["candidate_identity"],
        "result": receipt["result"],
        "deterministic_runs": receipt["deterministic_runs"],
        "rust_tests_per_run": receipt["rust_tests_per_run"],
        "invariants": contract["invariant_count"],
        "sandbox_report_deterministic": report_deterministic,
        "state_survives_activation_observation": receipt["state_survives_activation_observation"],
        "explicit_teardown_verified": receipt["explicit_teardown_verified"],
        "selected_dependencies_current": receipt["selected_dependencies_current"],
        "cleanup_verified": cleanup_verified,
        "repository_cargo_target_absent": repository_target_absent,
        "product_approved": False,
        "adapter_admitted": False,
        "live_execution_ready": False,
        "runtime_activated": False,
        "external_effects": False,
        "authority_effect": "none",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

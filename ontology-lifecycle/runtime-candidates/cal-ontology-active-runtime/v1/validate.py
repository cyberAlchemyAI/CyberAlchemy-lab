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
RECEIPT = HERE / "receipts/active-runtime.json"
CONTRACT = HERE / "contract.json"
SCHEMA = HERE / "schemas/active-runtime-contract.schema.json"
SEMANTIC = LAB / "ontology-lifecycle/migration/cal-w7-ontology-product-epoch-001/fixtures/output/semantic-events"
GOVERNANCE = LAB / "ontology-lifecycle/migration/cal-w7-ontology-product-epoch-001/fixtures/output/governance-events"
PROJECTION = LAB / "ontology-lifecycle/migration/cal-w7-ontology-product-epoch-001/fixtures/output/projections/ontology-at-cursor.json"
TEST_RE = re.compile(r"^test ([^ ]+) \.\.\. (ok|FAILED|ignored)$")
REPORT_RE = re.compile(r"ACTIVE_RUNTIME_REPORT_JSON=(\{.*\})")
EXPECTED_INVARIANTS = [
    "ACT-01-ADMITTED-L4-BINDING",
    "ACT-02-EXACT-EVENT-CUT",
    "ACT-03-NON-VACUOUS-CALCULATED-PROJECTION",
    "ACT-04-ACTIVE-ACROSS-COMMANDS",
    "ACT-05-EXPLICIT-STOP-TEARDOWN",
    "ACT-06-EOF-AND-DROP-CLEANUP",
    "ACT-07-LIVE-AND-ARGUMENT-REFUSAL",
    "ACT-08-DETERMINISTIC-REPORT",
]
SELECTED_DEPENDENCIES = [
    ("docs/decisions/0039-d65-l4-state-bearing-sandbox-product-approval/decision.json", "6f57ea86f8547fece058fa70e01c7afe4ed65bc97ec6b3a4f66f774a1f6301f3"),
    ("docs/decisions/0039-d65-l4-state-bearing-sandbox-product-approval/receipts/decision-validation.json", "a2030d07bcec5e53b41a8754c525166cc56773a1ee3710a656f5a7b1dd81eb96"),
    ("docs/decisions/0040-d65-l4-state-bearing-sandbox-adapter-admission/decision.json", "8adade17ddbbdaa9e145a940d3cc2f7245a767aae40411ef961f6368ac022d92"),
    ("docs/decisions/0040-d65-l4-state-bearing-sandbox-adapter-admission/receipts/decision-validation.json", "41beb5b374f5e9fe7124c6929caaebbdcae2145d76755e7ddc983834ce91d523"),
    ("ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/v1/receipts/stateful-sandbox.json", "bc9f367f18ce9530e6a8cd78a6d8b3edcbe788c753505847e7e5b999e1d4ddb3"),
    ("ontology-lifecycle/migration/cal-w7-ontology-product-epoch-001/fixtures/output/projections/ontology-at-cursor.json", "dcf396c8e50c6f9d81daa889d80e84b604be2cfcf3614b5ba0317bdcbc07b6c6"),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def directory_digest(path: Path) -> tuple[int, str]:
    records = [
        {"path": item.name, "sha256": digest(item)}
        for item in sorted(path.glob("*.json"))
    ]
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return len(records), hashlib.sha256(canonical).hexdigest()


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
            "cargo", "test", "--locked", "--test", "active_runtime",
            "active_runtime_report_is_byte_deterministic", "--", "--exact",
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


def cli_probe(target: Path) -> dict[str, Any]:
    completed = subprocess.run(
        ["cargo", "run", "--locked", "--quiet", "--bin", "cal-ontology-active-runtime"],
        cwd=HERE,
        env={**os.environ, "CARGO_TARGET_DIR": str(target)},
        input="status\nprojection\nstop\n",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        records = [json.loads(line) for line in completed.stdout.splitlines()]
    except json.JSONDecodeError:
        records = []
    kinds = [record.get("kind") for record in records]
    passed = (
        completed.returncode == 0
        and kinds == ["ready", "status", "projection", "stopped"]
        and records[0].get("body") == records[1].get("body")
        and records[0].get("body", {}).get("prototype_runtime_active") is True
        and records[2].get("body", {}).get("semantic_cursor") == 47
        and records[2].get("body", {}).get("source_event_count") == 47
        and len(records[2].get("body", {}).get("subjects", [])) == 47
        and records[3].get("body", {}).get("cleanup_verified") is True
    )
    return {
        "result": "PASS" if passed else "BLOCK",
        "exit": completed.returncode,
        "record_kinds": kinds,
        "ready_status": records[0].get("body") if records else None,
        "projection_subject_count": len(records[2].get("body", {}).get("subjects", [])) if len(records) == 4 else None,
        "stop_receipt": records[3].get("body") if len(records) == 4 else None,
        "stderr_tail": completed.stderr[-2000:] if completed.returncode else "",
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


def event_cut_result() -> dict[str, Any]:
    semantic_count, semantic_digest = directory_digest(SEMANTIC)
    governance_count, governance_digest = directory_digest(GOVERNANCE)
    projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
    passed = (
        semantic_count == governance_count == 47
        and semantic_digest == "7d3a1f48490ec38bfc3d6995beefeb3df0bb852c2a814828c7b745bb53410b89"
        and governance_digest == "69691f13120fd04162f0dbfc89c232048497a79e826af28daede8dbeabdcba03"
        and projection.get("semantic_cursor") == 47
        and projection.get("source_event_count") == 47
        and len(projection.get("subjects", [])) == 47
        and projection.get("source_event_set_digest") == "7a1089513ef4ed74bf70d6ed724d78f42a0e15cd267ac141213880026f06d6e2"
    )
    return {
        "result": "PASS" if passed else "BLOCK",
        "semantic_event_count": semantic_count,
        "governance_event_count": governance_count,
        "semantic_event_directory_sha256": semantic_digest,
        "governance_event_directory_sha256": governance_digest,
        "semantic_cursor": projection.get("semantic_cursor"),
        "projected_subject_count": len(projection.get("subjects", [])),
        "source_event_set_digest": projection.get("source_event_set_digest"),
    }


def contract_result() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    boundary = contract.get("runtime_boundary", {})
    event_cut = contract.get("event_cut", {})
    predecessors = contract.get("predecessors", {})
    invariants = contract.get("required_invariants", [])
    passed = (
        contract.get("schema_version") == schema["properties"]["schema_version"]["const"]
        and contract.get("candidate_id") == "CAL-D65-EPOCH-004-LOCAL-ACTIVE-RUNTIME-PROTOTYPE-006"
        and contract.get("runtime_identity") == "cal.prototype.rust-local-active-ontology-runtime/epoch-004"
        and invariants == EXPECTED_INVARIANTS
        and predecessors.get("l4_product_approval_decision_sha256") == SELECTED_DEPENDENCIES[0][1]
        and predecessors.get("l4_product_approval_validation_sha256") == SELECTED_DEPENDENCIES[1][1]
        and predecessors.get("l4_adapter_admission_decision_sha256") == SELECTED_DEPENDENCIES[2][1]
        and predecessors.get("l4_adapter_admission_validation_sha256") == SELECTED_DEPENDENCIES[3][1]
        and event_cut.get("semantic_event_directory_sha256") == "7d3a1f48490ec38bfc3d6995beefeb3df0bb852c2a814828c7b745bb53410b89"
        and event_cut.get("governance_event_directory_sha256") == "69691f13120fd04162f0dbfc89c232048497a79e826af28daede8dbeabdcba03"
        and boundary.get("interaction") == "stdin-json-lines"
        and boundary.get("commands") == ["status", "projection", "help", "stop"]
        and boundary.get("live") is False
        and boundary.get("network") is False
        and boundary.get("credential_kind") == "none"
        and boundary.get("production_data") is False
        and boundary.get("migration") is False
        and boundary.get("cutover") is False
        and boundary.get("external_effects") is False
        and contract.get("product_approved") is False
        and contract.get("governed_runtime_activated") is False
        and contract.get("live_execution_ready") is False
        and contract.get("authority_effect") == "none"
    )
    return {
        "result": "PASS" if passed else "BLOCK",
        "invariant_count": len(invariants),
        "invariant_ids": invariants,
        "runtime_boundary": boundary,
    }


def source_boundary_result() -> dict[str, Any]:
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted((HERE / "src").glob("*.rs"))
    )
    forbidden = [
        "std::net", "TcpListener", "TcpStream", "UdpSocket", "reqwest",
        "credential_kind: \"secret\"", "production_data: true", "live: true",
        "Command::new", "append_semantic_batch", "append_governance_batch",
    ]
    passed = (
        all(token not in source for token in forbidden)
        and "ActiveRuntime::start_canonical" in source
        and '"status"' in source
        and '"projection"' in source
        and '"stop"' in source
        and "target.teardown()" in source
    )
    return {
        "result": "PASS" if passed else "BLOCK",
        "forbidden_tokens": forbidden,
        "stdin_command_surface_present": all(token in source for token in ['"status"', '"projection"', '"stop"']),
        "explicit_teardown_present": "target.teardown()" in source,
    }


def report_passes(report: dict[str, Any]) -> bool:
    status = report.get("active_status", {})
    stop = report.get("stop", {})
    observation = report.get("activation_observation", {})
    return (
        report.get("schema_version") == "cal.d65-local-active-runtime-report/v1"
        and report.get("candidate_id") == "CAL-D65-EPOCH-004-LOCAL-ACTIVE-RUNTIME-PROTOTYPE-006"
        and report.get("runtime_identity") == "cal.prototype.rust-local-active-ontology-runtime/epoch-004"
        and observation.get("sandbox_activation_observed") is True
        and observation.get("state_survives_observation") is True
        and status.get("session_state") == "active"
        and status.get("prototype_runtime_active") is True
        and status.get("calculated_projection_available") is True
        and status.get("semantic_cursor") == 47
        and status.get("source_event_count") == 47
        and status.get("subject_count") == 47
        and status.get("source_event_set_digest") == "7a1089513ef4ed74bf70d6ed724d78f42a0e15cd267ac141213880026f06d6e2"
        and status.get("state_survives_commands") is True
        and status.get("explicit_stop_required") is True
        and report.get("projection_matches_canonical_fixture") is True
        and report.get("repeated_status_is_stable") is True
        and stop.get("session_state") == "stopped"
        and stop.get("restored_preimage_exact") is True
        and stop.get("cleanup_verified") is True
        and status.get("product_approved") is False
        and status.get("governed_runtime_activated") is False
        and status.get("live_execution_ready") is False
        and status.get("external_effects") is False
        and report.get("result") == "PASS"
        and report.get("authority_effect") == "none"
    )


def input_records() -> list[dict[str, str]]:
    relative = [
        "Cargo.toml", "Cargo.lock", "contract.json", "plan.md", "README.md",
        "src/lib.rs", "src/main.rs", "tests/active_runtime.rs", "tests/cli_runtime.rs",
        "schemas/active-runtime-contract.schema.json", "validate.py",
    ]
    return [
        {"path": str((HERE / item).relative_to(LAB)), "sha256": digest(HERE / item)}
        for item in relative
    ]


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
    with tempfile.TemporaryDirectory(prefix="cal-d65-local-active-runtime-") as temporary:
        target = Path(temporary) / "cargo-target"
        formatting = run_command(["cargo", "fmt", "--all", "--", "--check"], target)
        clippy = run_command(["cargo", "clippy", "--locked", "--tests", "--", "-D", "warnings"], target)
        run_a = run_once(target)
        run_b = run_once(target)
        report_a = emit_report(target)
        report_b = emit_report(target)
        cli = cli_probe(target)
    roots_after = sandbox_roots()

    dependencies = dependency_records()
    event_cut = event_cut_result()
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
        and run_a["test_count"] == 10
        and all(result == "ok" for _, result in run_a["tests"])
        and all(record["result"] == "PASS" for record in dependencies)
        and event_cut["result"] == "PASS"
        and contract["result"] == "PASS"
        and source_boundary["result"] == "PASS"
        and report_deterministic
        and report_passes(report)
        and cli["result"] == "PASS"
        and cleanup_verified
        and repository_target_absent
    )
    receipt = {
        "schema_version": "cal.d65-local-active-runtime-test-evidence/v1",
        "candidate_id": "CAL-D65-EPOCH-004-LOCAL-ACTIVE-RUNTIME-PROTOTYPE-006",
        "candidate_identity": "cal.prototype.rust-local-active-ontology-runtime/epoch-004",
        "result": "PASS" if passed else "BLOCK",
        "deterministic_runs": 2,
        "rust_tests_per_run": run_a["test_count"],
        "run_a": run_a,
        "run_b": run_b,
        "formatting": formatting,
        "clippy": clippy,
        "selected_dependencies_current": all(record["result"] == "PASS" for record in dependencies),
        "selected_dependencies": dependencies,
        "event_cut": event_cut,
        "contract": contract,
        "source_boundary": source_boundary,
        "active_runtime_report_deterministic": report_deterministic,
        "active_runtime_report_sha256": hashlib.sha256(report_b["raw"].encode()).hexdigest() if report_b["raw"] else None,
        "active_runtime_report": report,
        "cli_probe": cli,
        "cleanup_verified": cleanup_verified,
        "repository_cargo_target_absent": repository_target_absent,
        "prototype_runtime_active_during_test": report.get("active_status", {}).get("prototype_runtime_active", False),
        "calculated_projection_available_during_test": report.get("active_status", {}).get("calculated_projection_available", False),
        "explicit_stop_verified": report.get("stop", {}).get("cleanup_verified", False),
        "product_approved": False,
        "governed_runtime_activated": False,
        "live_execution_ready": False,
        "migration_performed": False,
        "cutover_performed": False,
        "external_effects": False,
        "authority_effect": "none",
        "inputs": input_records(),
        "claim_ceiling": "PASS proves that the exact L5 process-local runtime candidate binds the admitted L4 adapter, calculates the exact 47-subject W7 ontology from canonical events, remains active across commands, exposes the projection, and tears down exactly. It does not approve the product, activate a governed or live runtime, migrate, cut over, publish, deploy, or authorize external effects.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_id": receipt["candidate_id"],
        "candidate_identity": receipt["candidate_identity"],
        "result": receipt["result"],
        "deterministic_runs": 2,
        "rust_tests_per_run": receipt["rust_tests_per_run"],
        "invariants": contract["invariant_count"],
        "selected_dependencies_current": receipt["selected_dependencies_current"],
        "event_cut_exact": event_cut["result"] == "PASS",
        "prototype_runtime_active_during_test": receipt["prototype_runtime_active_during_test"],
        "calculated_projection_available_during_test": receipt["calculated_projection_available_during_test"],
        "cli_probe": cli["result"],
        "explicit_stop_verified": receipt["explicit_stop_verified"],
        "cleanup_verified": cleanup_verified,
        "repository_cargo_target_absent": repository_target_absent,
        "product_approved": False,
        "governed_runtime_activated": False,
        "live_execution_ready": False,
        "external_effects": False,
        "authority_effect": "none",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

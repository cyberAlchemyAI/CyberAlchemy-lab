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
L1_RECEIPT = HERE / "receipts/tests.json"
L2_RECEIPT = HERE / "receipts/certification.json"
L3_RECEIPT = HERE / "receipts/filesystem-rehearsal.json"
CONTRACT_FIXTURE = HERE / "tests/fixtures/filesystem-rehearsal.json"
CONTRACT_SCHEMA = HERE / "schemas/filesystem-rehearsal.schema.json"
FILESYSTEM_SOURCE = HERE / "src/filesystem_target.rs"
TEST_RE = re.compile(r"^test ([^ ]+) \.\.\. (ok|FAILED|ignored)$")
REPORT_RE = re.compile(r"FILESYSTEM_REHEARSAL_REPORT_JSON=(\{.*\})")
EXPECTED_INVARIANT_IDS = [
    "FSR-01-PATH-CONFINEMENT",
    "FSR-02-EXACT-BINDING",
    "FSR-03-BYTE-PREIMAGE",
    "FSR-04-FAILURE-RESTORATION",
    "FSR-05-CLEANUP",
    "FSR-06-DETERMINISTIC-REPORT",
]
SELECTED_DEPENDENCIES = [
    ("docs/decisions/0035-d65-epoch-002-activation-cutover/decision.json", "f7850289e28ddc71c65ffb76dd753c578d0c12230efd08e63fcf36cf5c69e4e8"),
    ("ontology-lifecycle/activation/cal-d65-epoch-002/activation-contract.json", "37e326b87d1fb82c0f8b32f2d213854c705fa78e5245dc7b7cda4c7ccbd46416"),
    ("ontology-lifecycle/activation/cal-d65-epoch-002/fixtures/source-events.jsonl", "d6014bf9c8624526a6597c25439065934a90ccf204e63de3e5b3e693e08e910b"),
    ("ontology-lifecycle/activation/cal-d65-epoch-002/fixtures/migration-inventory.json", "1adee0ad666c212de5b37fc87428b2977c6f7549cb3cbe933450d49d8456035f"),
    ("ontology-lifecycle/activation/cal-d65-epoch-002/fixtures/expected-projections.json", "829eaba67ebd9213e986926b72e8dfac674d1a1f73009e5339f409794992d929"),
    ("ontology-lifecycle/runtime/Cargo.toml", "6e17c6f449dd7068f9d2aa4bd664e8e1e8a8a0083c3e93ceca5e78def13364dc"),
    ("ontology-lifecycle/runtime/src/lib.rs", "534d6421bc0657c3e10dc1061174423375a10cf4eaf346916b471f198a8f4451"),
    ("ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l2/plan.md", "5a3db86bddbb6ab2af8702e9afd0b0f8b830f707f7755040d9dae321a630fbea"),
    ("ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l2/contract.json", "2b57e14ca755ff822e7abb154e5486bf7cdd79ab9d5f9f56927360fda634009d"),
    ("ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l3/plan.md", "aaae2e4f667fbb5ff3091d180912f5b15de391bb14123dda025fc108d4ca716f"),
    ("ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l3/contract.json", "aa66bc600494ad416571ac6b9ffc14cbf250eff935f64597a38504a6c63359b7"),
]
FROZEN_PREDECESSOR_RECEIPTS = [
    (L1_RECEIPT, "802b91186fa6c41b21609bfe63428c3466fbc1519033e3692e39cf65fb00e509"),
    (L2_RECEIPT, "4046bc8954c232e40e37b0e3b9d8d9f54f0a59b378cabc8f4d9d2d8277ad5080"),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
            "cargo",
            "test",
            "--locked",
            "--test",
            "filesystem_rehearsal",
            "filesystem_rehearsal_report_is_byte_deterministic",
            "--",
            "--exact",
            "--nocapture",
            "--test-threads=1",
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


def predecessor_records() -> list[dict[str, Any]]:
    records = []
    for path, expected in FROZEN_PREDECESSOR_RECEIPTS:
        current = digest(path) if path.is_file() else None
        records.append({
            "path": str(path.relative_to(LAB)),
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
        contract.get("schema_version") == "cal.d65-filesystem-rehearsal-contract/v1"
        and set(contract) == {"schema_version", "target", "invariants"}
        and set(target) == required_target
        and ids == EXPECTED_INVARIANT_IDS
        and len(set(ids)) == 6
        and target.get("kind") == "filesystem-disposable-target"
        and target.get("identity") == "cal.prototype.rust-disposable-filesystem-target/epoch-002"
        and target.get("path_policy") == "adapter-created-process-temporary-directory"
        and target.get("caller_supplied_path") is False
        and target.get("live") is False
        and target.get("production_data") is False
        and target.get("credential_kind") == "none"
        and target.get("network") is False
        and target.get("external_effects") is False
        and target.get("disposable_local_filesystem_effects") is True
    )
    return {
        "result": "PASS" if passed else "BLOCK",
        "invariant_count": len(invariants),
        "invariant_ids": ids,
        "target": target,
    }


def report_passes(report: dict[str, Any]) -> bool:
    binding = report.get("target_binding", {})
    return (
        report.get("schema_version") == "cal.d65-filesystem-rehearsal-report/v1"
        and report.get("candidate_id") == "CAL-D65-EPOCH-002-FILESYSTEM-REHEARSAL-PROTOTYPE-004"
        and report.get("baseline_candidate_id") == "CAL-D65-EPOCH-002-ADAPTER-CERTIFICATION-PROTOTYPE-003"
        and report.get("baseline_receipt_digest") == "4046bc8954c232e40e37b0e3b9d8d9f54f0a59b378cabc8f4d9d2d8277ad5080"
        and binding.get("kind") == "filesystem-disposable-target"
        and binding.get("identity") == "cal.prototype.rust-disposable-filesystem-target/epoch-002"
        and binding.get("credential_kind") == "none"
        and binding.get("live") is False
        and binding.get("production_data") is False
        and binding.get("external_effects") is False
        and report.get("rollback_exact") is True
        and report.get("cleanup_verified") is True
        and report.get("path_policy") == "adapter-created-process-temporary-directory"
        and report.get("disposable_local_filesystem_effects") is True
        and report.get("live_execution_ready") is False
        and report.get("external_effects") is False
        and report.get("result") == "PASS"
        and report.get("authority_effect") == "none"
        and report.get("preimage_digest") == report.get("final_state_digest")
        and len(report.get("execution_trace_digest", "")) == 64
        and len(report.get("report_digest", "")) == 64
    )


def source_boundary_result() -> dict[str, Any]:
    source = FILESYSTEM_SOURCE.read_text(encoding="utf-8")
    forbidden = ["std::net", "TcpStream", "credential:", "production_data: true", "live: true"]
    passed = (
        all(token not in source for token in forbidden)
        and "pub fn new()" in source
        and "std::env::temp_dir()" in source
        and "pub fn new(path" not in source
        and "pub fn with_root" not in source
    )
    return {
        "result": "PASS" if passed else "BLOCK",
        "forbidden_tokens": forbidden,
        "caller_path_constructor_absent": "pub fn new(path" not in source and "pub fn with_root" not in source,
    }


def input_records() -> list[dict[str, str]]:
    paths = [
        HERE / "Cargo.toml",
        HERE / "Cargo.lock",
        HERE / "src/lib.rs",
        HERE / "src/certification.rs",
        FILESYSTEM_SOURCE,
        HERE / "tests/public_contract.rs",
        HERE / "tests/adapter_conformance.rs",
        HERE / "tests/certification_contract.rs",
        HERE / "tests/filesystem_rehearsal.rs",
        HERE / "tests/fixtures/certification-vectors.json",
        CONTRACT_FIXTURE,
        HERE / "schemas/certification-vectors.schema.json",
        CONTRACT_SCHEMA,
        HERE / "validate.py",
        HERE / "validate-l3.py",
        HERE / "README.md",
        HERE / "implementation-layering.md",
        LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l2/plan.md",
        LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l2/contract.json",
        LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l3/plan.md",
        LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l3/contract.json",
    ]
    return [
        {"path": str(path.relative_to(LAB)), "sha256": digest(path)}
        for path in paths
    ]


def rehearsal_roots() -> set[str]:
    return {
        str(path)
        for path in Path(tempfile.gettempdir()).glob("cal-d65-filesystem-rehearsal-*")
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    roots_before = rehearsal_roots()
    with tempfile.TemporaryDirectory(prefix="cal-d65-rust-filesystem-rehearsal-") as temporary:
        target = Path(temporary) / "cargo-target"
        run_a = run_once(target)
        run_b = run_once(target)
        report_a = emit_report(target)
        report_b = emit_report(target)
    roots_after = rehearsal_roots()

    dependencies = dependency_records()
    predecessors = predecessor_records()
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
        run_a == run_b
        and run_a["exit"] == 0
        and run_a["test_count"] == 27
        and all(result == "ok" for _, result in run_a["tests"])
        and all(record["result"] == "PASS" for record in dependencies)
        and all(record["result"] == "PASS" for record in predecessors)
        and contract["result"] == "PASS"
        and source_boundary["result"] == "PASS"
        and report_deterministic
        and report_passes(report)
        and cleanup_verified
        and repository_target_absent
    )
    receipt = {
        "schema_version": "cal.d65-filesystem-rehearsal-test-evidence/v1",
        "candidate_id": "CAL-D65-EPOCH-002-FILESYSTEM-REHEARSAL-PROTOTYPE-004",
        "result": "PASS" if passed else "BLOCK",
        "deterministic_runs": 2,
        "rust_tests_per_run": run_a["test_count"],
        "run_a": run_a,
        "run_b": run_b,
        "selected_dependencies_current": all(record["result"] == "PASS" for record in dependencies),
        "selected_dependencies": dependencies,
        "frozen_predecessor_receipts_current": all(record["result"] == "PASS" for record in predecessors),
        "frozen_predecessor_receipts": predecessors,
        "contract": contract,
        "source_boundary": source_boundary,
        "rehearsal_report_deterministic": report_deterministic,
        "rehearsal_report_sha256": hashlib.sha256(report_b["raw"].encode("utf-8")).hexdigest() if report_b["raw"] else None,
        "rehearsal_report": report,
        "cleanup_verified": cleanup_verified,
        "repository_cargo_target_absent": repository_target_absent,
        "disposable_local_filesystem_effects": True,
        "live_execution_ready": False,
        "runtime_activated": False,
        "migration_performed": False,
        "cutover_performed": False,
        "external_effects": False,
        "authority_effect": "none",
        "inputs": input_records(),
        "claim_ceiling": "PASS proves the isolated L3 disposable-filesystem rehearsal candidate, exact binding, path confinement, byte-exact rollback, failure restoration, cleanup, and deterministic evidence. It does not approve or admit an adapter, make a live target available, use credentials, migrate production data, perform an operational cutover, publish, deploy, or authorize external effects.",
    }
    if args.write_receipt:
        L3_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        L3_RECEIPT.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "candidate_id": receipt["candidate_id"],
        "result": receipt["result"],
        "deterministic_runs": receipt["deterministic_runs"],
        "rust_tests_per_run": receipt["rust_tests_per_run"],
        "invariants": contract["invariant_count"],
        "rehearsal_report_deterministic": report_deterministic,
        "selected_dependencies_current": receipt["selected_dependencies_current"],
        "frozen_predecessor_receipts_current": receipt["frozen_predecessor_receipts_current"],
        "cleanup_verified": cleanup_verified,
        "repository_cargo_target_absent": repository_target_absent,
        "live_execution_ready": False,
        "external_effects": False,
        "authority_effect": "none",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

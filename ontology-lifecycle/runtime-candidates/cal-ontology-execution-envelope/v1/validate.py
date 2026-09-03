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
RECEIPT = HERE / "receipts/tests.json"
TEST_RE = re.compile(r"^test ([^ ]+) \.\.\. (ok|FAILED|ignored)$")
SELECTED_DEPENDENCIES = [
    ("docs/decisions/0035-d65-epoch-002-activation-cutover/decision.json", "f7850289e28ddc71c65ffb76dd753c578d0c12230efd08e63fcf36cf5c69e4e8"),
    ("ontology-lifecycle/activation/cal-d65-epoch-002/activation-contract.json", "37e326b87d1fb82c0f8b32f2d213854c705fa78e5245dc7b7cda4c7ccbd46416"),
    ("ontology-lifecycle/activation/cal-d65-epoch-002/fixtures/source-events.jsonl", "d6014bf9c8624526a6597c25439065934a90ccf204e63de3e5b3e693e08e910b"),
    ("ontology-lifecycle/activation/cal-d65-epoch-002/fixtures/migration-inventory.json", "1adee0ad666c212de5b37fc87428b2977c6f7549cb3cbe933450d49d8456035f"),
    ("ontology-lifecycle/activation/cal-d65-epoch-002/fixtures/expected-projections.json", "829eaba67ebd9213e986926b72e8dfac674d1a1f73009e5339f409794992d929"),
    ("ontology-lifecycle/runtime/Cargo.toml", "6e17c6f449dd7068f9d2aa4bd664e8e1e8a8a0083c3e93ceca5e78def13364dc"),
    ("ontology-lifecycle/runtime/src/lib.rs", "534d6421bc0657c3e10dc1061174423375a10cf4eaf346916b471f198a8f4451"),
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
    tests = sorted((match.group(1), match.group(2)) for line in completed.stdout.splitlines() if (match := TEST_RE.match(line.strip())))
    return {"exit": completed.returncode, "test_count": len(tests), "tests": tests, "tail": completed.stdout[-4000:] if completed.returncode else ""}


def selected_dependency_records() -> list[dict[str, Any]]:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="cal-d65-rust-execution-") as temporary:
        target = Path(temporary) / "cargo-target"
        run_a = run_once(target)
        run_b = run_once(target)
    selected_dependencies = selected_dependency_records()
    selected_dependencies_current = all(record["result"] == "PASS" for record in selected_dependencies)
    passed = (
        run_a == run_b
        and run_a["exit"] == 0
        and run_a["test_count"] == 12
        and all(result == "ok" for _, result in run_a["tests"])
        and selected_dependencies_current
    )
    receipt = {
        "schema_version": "cal.d65-rust-execution-envelope-test-evidence/v2",
        "candidate_id": "CAL-D65-EPOCH-002-RUST-EXECUTION-PROTOTYPE-002",
        "result": "PASS" if passed else "BLOCK",
        "deterministic_runs": 2,
        "rust_tests_per_run": run_a["test_count"],
        "selected_dependencies_current": selected_dependencies_current,
        "selected_dependencies": selected_dependencies,
        "run_a": run_a,
        "run_b": run_b,
        "tested_behaviors": [
            "ten-step prototype execution and exact rollback",
            "live-mode fail-closed refusal",
            "stale decision rejection",
            "step-order enforcement",
            "credential rejection",
            "live/external target rejection",
            "automatic rollback after target-verification failure",
            "event-cut substitution rejection"
            ,"public adapter implementation outside the crate"
            ,"adapter binding mismatch rejection before mutation"
            ,"emergency restoration after rollback failure"
            ,"emergency restoration after rollback-verification failure"
        ],
        "live_execution_ready": False,
        "runtime_activated": False,
        "migration_performed": False,
        "cutover_performed": False,
        "external_effects": False,
        "authority_effect": "none",
        "inputs": [
            {"path": str((HERE / "Cargo.toml").relative_to(LAB)), "sha256": digest(HERE / "Cargo.toml")},
            {"path": str((HERE / "Cargo.lock").relative_to(LAB)), "sha256": digest(HERE / "Cargo.lock")},
            {"path": str((HERE / "src/lib.rs").relative_to(LAB)), "sha256": digest(HERE / "src/lib.rs")},
            {"path": str((HERE / "tests/public_contract.rs").relative_to(LAB)), "sha256": digest(HERE / "tests/public_contract.rs")},
            {"path": str((HERE / "tests/adapter_conformance.rs").relative_to(LAB)), "sha256": digest(HERE / "tests/adapter_conformance.rs")},
            {"path": str((HERE / "implementation-layering.md").relative_to(LAB)), "sha256": digest(HERE / "implementation-layering.md")}
        ],
        "claim_ceiling": "PASS proves the isolated Rust execution-envelope engine prototype, its public target-adapter contract, and its fail-closed disposable adapter behavior. It does not certify a real-system adapter, make a live target available, satisfy live prerequisites, activate a runtime, migrate or cut over data, use credentials, publish, deploy, or create external effects."
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_id": receipt["candidate_id"],
        "result": receipt["result"],
        "deterministic_runs": receipt["deterministic_runs"],
        "rust_tests_per_run": receipt["rust_tests_per_run"],
        "selected_dependencies_current": receipt["selected_dependencies_current"],
        "live_execution_ready": False,
        "runtime_activated": False,
        "cutover_performed": False,
        "external_effects": False,
        "authority_effect": "none"
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

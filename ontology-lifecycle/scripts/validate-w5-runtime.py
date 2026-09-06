#!/usr/bin/env python3
"""Validate the W5 Rust runtime against the exact W4 compiled contract."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
RUNTIME = ROOT / "runtime"
CONTRACT = ROOT / "domainspec" / "event-sourcing" / "generated" / "contract.json"
W4 = ROOT / "conformance" / "w4-gate.json"
LEDGER = RUNTIME / "fixtures" / "mutation-ledger.json"
TESTS = RUNTIME / "tests" / "replay.rs"
RECEIPT = ROOT / "conformance" / "w5-runtime-validation.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=RUNTIME,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    contract = load(CONTRACT)
    w4 = load(W4)
    ledger = load(LEDGER)
    test_source = TESTS.read_text(encoding="utf-8")
    test_names = set(re.findall(r"(?m)^#\[test\]\nfn ([a-z0-9_]+)\(\)", test_source))

    contract_obligations = set(contract.get("runtimeObligations", []))
    ledger_entries = ledger.get("obligations", [])
    ledger_obligations = {entry.get("obligation") for entry in ledger_entries}
    missing_tests = sorted(
        {
            name
            for entry in ledger_entries
            for name in [entry.get("positive_test"), entry.get("mutation_test")]
            if name not in test_names
        }
    )

    formatting = run("cargo", "fmt", "--all", "--", "--check")
    build = run("cargo", "check", "--locked", "--all-targets")
    tests = run("cargo", "test", "--locked")
    test_output = tests.stdout + tests.stderr
    passed_counts = [int(value) for value in re.findall(r"test result: ok\. (\d+) passed", test_output)]
    executed_tests = max(passed_counts, default=0)

    w4_ready = w4.get("result") == "PASS" and w4.get("downstream", {}).get("W5") == "ready"
    checks = {
        "w4_predecessor": "PASS" if w4_ready else "not_evaluable",
        "compiled_contract_identity": "PASS"
        if ledger.get("contract_id") == contract.get("contractId")
        else "FAIL",
        "runtime_obligation_coverage": "PASS"
        if contract_obligations == ledger_obligations and len(contract_obligations) == 12
        else "FAIL",
        "mutation_test_resolution": "PASS" if not missing_tests else "FAIL",
        "format_check": "PASS" if formatting.returncode == 0 else "FAIL",
        "locked_all_target_check": "PASS" if build.returncode == 0 else "FAIL",
        "rust_tests": "PASS" if tests.returncode == 0 and executed_tests == len(test_names) else "FAIL",
        "replay_equality": "PASS"
        if "deterministic_rebuilds_match_for_all_read_models" in test_names
        and "checkpoint_tail_matches_empty_rebuild_and_rejects_drift" in test_names
        else "FAIL",
        "projection_source_rejection": "PASS"
        if "noncanonical_json_and_projection_replay_sources_fail_closed" in test_names
        else "FAIL",
    }
    blockers = []
    for check_id, result in checks.items():
        if check_id == "w4_predecessor":
            continue
        if result != "PASS":
            blockers.append({"code": "W5_CHECK_FAILED", "check_id": check_id})
    if contract_obligations != ledger_obligations:
        blockers.append(
            {
                "code": "RUNTIME_OBLIGATION_COVERAGE_MISMATCH",
                "missing": sorted(contract_obligations - ledger_obligations),
                "extra": sorted(ledger_obligations - contract_obligations),
            }
        )
    if missing_tests:
        blockers.append({"code": "MUTATION_TEST_MISSING", "tests": missing_tests})

    technical_result = "PASS" if not blockers else "FAIL"
    if technical_result == "FAIL":
        result = "FAIL"
    elif not w4_ready:
        result = "not_evaluable"
        blockers.append(
            {
                "code": "W4_PREDECESSOR_NOT_PASS",
                "owner": "G-W4 owners",
                "observed_result": w4.get("result"),
            }
        )
    else:
        result = "PASS"
    inputs = [
        Path(__file__).resolve(),
        CONTRACT,
        W4,
        RUNTIME / "Cargo.toml",
        RUNTIME / "Cargo.lock",
        RUNTIME / "src" / "lib.rs",
        RUNTIME / "src" / "main.rs",
        TESTS,
        LEDGER,
    ]
    receipt = {
        "schema_version": "cal.w5-runtime-validation/v1",
        "gate_id": "G-W5",
        "result": result,
        "technical_result": technical_result,
        "compiled_contract": {
            "contract_id": contract.get("contractId"),
            "sha256": digest(CONTRACT),
            "runtime_obligation_count": len(contract_obligations),
        },
        "checks": checks,
        "evidence": {
            "rust_test_count": executed_tests,
            "declared_test_count": len(test_names),
            "mutation_entry_count": len(ledger_entries),
            "missing_test_names": missing_tests,
            "digest_preimage_rule": ledger.get("digest_preimage_rule"),
        },
        "blockers": blockers,
        "downstream": {"W6": "ready" if result == "PASS" else "not_evaluable"},
        "authority_effect": "none",
        "claim_ceiling": "Technical PASS establishes a focused Rust candidate against the compiled contract. G-W5 PASS additionally requires a current passing G-W4 predecessor. Neither establishes independent conformance, human acceptance, migration authority, publication, release, deployment, cutover, or external effects.",
        "inputs": [
            {"path": str(path.relative_to(REPO)), "sha256": digest(path)} for path in inputs
        ],
    }
    RECEIPT.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "gate_id": "G-W5",
                "result": result,
                "checks": checks,
                "test_count": executed_tests,
                "blockers": blockers,
            },
            indent=2,
        )
    )
    if formatting.returncode:
        print(formatting.stdout + formatting.stderr)
    if build.returncode:
        print(build.stdout + build.stderr)
    if tests.returncode:
        print(test_output)
    return 0 if result == "PASS" else (1 if result == "FAIL" else 2)


if __name__ == "__main__":
    raise SystemExit(main())

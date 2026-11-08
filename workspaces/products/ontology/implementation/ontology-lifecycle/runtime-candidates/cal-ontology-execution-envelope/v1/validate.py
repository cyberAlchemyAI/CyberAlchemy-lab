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
VECTOR_FIXTURE = HERE / "tests/fixtures/certification-vectors.json"
VECTOR_SCHEMA = HERE / "schemas/certification-vectors.schema.json"
CERTIFICATION_TEST_SOURCE = HERE / "tests/certification_contract.rs"
TEST_RE = re.compile(r"^test ([^ ]+) \.\.\. (ok|FAILED|ignored)$")
REPORT_RE = re.compile(r"CERTIFICATION_REPORT_JSON=(\{.*\})")
EXPECTED_VECTOR_IDS = [
    f"CERT-{position:02d}-{name}"
    for position, name in enumerate(
        [
            "BASELINE",
            "CALL-ORDER",
            "BINDING-IDENTITY",
            "LIVE-BINDING",
            "CREDENTIAL-BINDING",
            "PREIMAGE-DRIFT",
            "STAGE-FAILURE",
            "ACTIVATE-FAILURE",
            "MIGRATE-FAILURE",
            "VERIFY-TARGET-FAILURE",
            "CUTOVER-FAILURE",
            "VERIFY-POSTIMAGE-FAILURE",
            "ROLLBACK-FAILURE",
            "VERIFY-ROLLBACK-FAILURE",
            "REPORT-DETERMINISM",
            "INDEPENDENT-FIXTURE",
            "VECTOR-OMISSION",
            "VECTOR-MUTATION",
        ],
        start=1,
    )
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
]
FROZEN_L1_INPUTS = [
    (L1_RECEIPT, "802b91186fa6c41b21609bfe63428c3466fbc1519033e3692e39cf65fb00e509"),
    (HERE / "tests/public_contract.rs", "fdafdf15c7cf8f09b86acf0a68d01937caefc801502040177af145e035fd0f43"),
    (HERE / "tests/adapter_conformance.rs", "5de59e0e5d84be99e3ee1f3dff2608ced901cf60a646d9ee49fbcca56104ccec"),
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


def emit_certification_report(target: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [
            "cargo",
            "test",
            "--locked",
            "--test",
            "certification_contract",
            "certification_report_is_byte_deterministic",
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


def frozen_l1_records() -> list[dict[str, Any]]:
    records = []
    for path, expected in FROZEN_L1_INPUTS:
        current = digest(path) if path.is_file() else None
        records.append({
            "path": str(path.relative_to(LAB)),
            "expected_sha256": expected,
            "current_sha256": current,
            "result": "PASS" if current == expected else "BLOCK",
        })
    return records


def vector_contract_result() -> dict[str, Any]:
    document = json.loads(VECTOR_FIXTURE.read_text(encoding="utf-8"))
    schema = json.loads(VECTOR_SCHEMA.read_text(encoding="utf-8"))
    vectors = document.get("vectors", [])
    ids = [vector.get("vector_id") for vector in vectors]
    required = set(schema["properties"]["vectors"]["items"]["required"])
    shape_pass = all(set(vector) == required for vector in vectors)
    passed = (
        document.get("schema_version") == schema["properties"]["schema_version"]["const"]
        and len(vectors) == 18
        and ids == EXPECTED_VECTOR_IDS
        and len(set(ids)) == 18
        and shape_pass
        and all(vector.get("state_invariant") == "exact-preimage" for vector in vectors)
        and all(vector.get("external_effects") is False for vector in vectors)
    )
    return {
        "result": "PASS" if passed else "BLOCK",
        "vector_count": len(vectors),
        "vector_ids": ids,
    }


def certification_report_passes(report: dict[str, Any]) -> bool:
    outcomes = report.get("outcomes", [])
    return (
        report.get("candidate_id") == "CAL-D65-EPOCH-002-ADAPTER-CERTIFICATION-PROTOTYPE-003"
        and report.get("baseline_commit") == "5b665f4dc351853bee777f14e56cccdab6cbfb26"
        and report.get("baseline_receipt_digest") == "802b91186fa6c41b21609bfe63428c3466fbc1519033e3692e39cf65fb00e509"
        and report.get("result") == "PASS"
        and report.get("passed_vectors") == report.get("total_vectors") == 18
        and [outcome.get("vector_id") for outcome in outcomes] == EXPECTED_VECTOR_IDS
        and all(outcome.get("result") == "PASS" for outcome in outcomes)
        and report.get("preimage_digest") == report.get("final_state_digest")
        and report.get("external_effects") is False
        and report.get("authority_effect") == "none"
        and len(report.get("report_digest", "")) == 64
    )


def input_records() -> list[dict[str, str]]:
    paths = [
        HERE / "Cargo.toml",
        HERE / "Cargo.lock",
        HERE / "src/lib.rs",
        HERE / "src/certification.rs",
        VECTOR_SCHEMA,
        VECTOR_FIXTURE,
        HERE / "tests/public_contract.rs",
        HERE / "tests/adapter_conformance.rs",
        CERTIFICATION_TEST_SOURCE,
        HERE / "validate.py",
        HERE / "README.md",
        HERE / "implementation-layering.md",
        LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l2/plan.md",
        LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/planning/l2/contract.json",
    ]
    return [
        {"path": str(path.relative_to(LAB)), "sha256": digest(path)}
        for path in paths
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="cal-d65-rust-certification-") as temporary:
        target = Path(temporary) / "cargo-target"
        run_a = run_once(target)
        run_b = run_once(target)
        report_a = emit_certification_report(target)
        report_b = emit_certification_report(target)

    selected_dependencies = selected_dependency_records()
    dependencies_current = all(record["result"] == "PASS" for record in selected_dependencies)
    frozen_l1 = frozen_l1_records()
    frozen_l1_current = all(record["result"] == "PASS" for record in frozen_l1)
    vector_contract = vector_contract_result()
    independent_source = "InMemoryTarget" not in CERTIFICATION_TEST_SOURCE.read_text(encoding="utf-8")
    report = report_b["report"]
    report_deterministic = (
        report_a["exit"] == report_b["exit"] == 0
        and bool(report_a["raw"])
        and report_a["raw"] == report_b["raw"]
    )
    passed = (
        run_a == run_b
        and run_a["exit"] == 0
        and run_a["test_count"] == 20
        and all(result == "ok" for _, result in run_a["tests"])
        and dependencies_current
        and frozen_l1_current
        and vector_contract["result"] == "PASS"
        and independent_source
        and report_deterministic
        and certification_report_passes(report)
    )
    receipt = {
        "schema_version": "cal.d65-adapter-certification-test-evidence/v1",
        "candidate_id": "CAL-D65-EPOCH-002-ADAPTER-CERTIFICATION-PROTOTYPE-003",
        "result": "PASS" if passed else "BLOCK",
        "deterministic_runs": 2,
        "rust_tests_per_run": run_a["test_count"],
        "run_a": run_a,
        "run_b": run_b,
        "selected_dependencies_current": dependencies_current,
        "selected_dependencies": selected_dependencies,
        "frozen_l1_current": frozen_l1_current,
        "frozen_l1_inputs": frozen_l1,
        "vector_contract": vector_contract,
        "independent_fixture_source": "PASS" if independent_source else "BLOCK",
        "certification_report_deterministic": report_deterministic,
        "certification_report_sha256": hashlib.sha256(report_b["raw"].encode("utf-8")).hexdigest() if report_b["raw"] else None,
        "certification_report": report,
        "live_execution_ready": False,
        "runtime_activated": False,
        "migration_performed": False,
        "cutover_performed": False,
        "external_effects": False,
        "authority_effect": "none",
        "inputs": input_records(),
        "claim_ceiling": "PASS proves the isolated L2 disposable-adapter certification prototype, exact 18-vector contract, independent fixture, deterministic report, failure restoration, and mutation rejection. It does not certify or admit a real-system adapter, approve a product, make a live target available, use credentials, activate a runtime, migrate or cut over data, publish, deploy, or create external effects.",
    }
    if args.write_receipt:
        L2_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        L2_RECEIPT.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "candidate_id": receipt["candidate_id"],
        "result": receipt["result"],
        "deterministic_runs": receipt["deterministic_runs"],
        "rust_tests_per_run": receipt["rust_tests_per_run"],
        "certification_vectors": vector_contract["vector_count"],
        "certification_report_deterministic": report_deterministic,
        "selected_dependencies_current": dependencies_current,
        "frozen_l1_current": frozen_l1_current,
        "live_execution_ready": False,
        "runtime_activated": False,
        "cutover_performed": False,
        "external_effects": False,
        "authority_effect": "none",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

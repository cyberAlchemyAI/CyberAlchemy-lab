#!/usr/bin/env python3
"""Independently validate the current W6 exact binding and vacuity evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
PACKAGE = SCRIPT.parents[1]
LAB = PACKAGE.parent
DOMAINSPEC_CORE = LAB.parent / "domainspec-core"
DOMAINSPEC_IMPL = DOMAINSPEC_CORE / "projects" / "domainspec-v2" / "impl"
BACKEND = DOMAINSPEC_CORE / "implementation" / "domainspec" / "backend"
RUNTIME = PACKAGE / "runtime"
BINDING_PATH = PACKAGE / "conformance" / "construction-binding.json"
VERIFICATION_PATH = PACKAGE / "conformance" / "verification.json"
D65_STATUS_PATH = PACKAGE / "conformance" / "d65-status.json"
GRAPH_PATH = PACKAGE / "domainspec" / ".domainspec" / "generated" / "graph.json"
SYSTEM_NODES_PATH = PACKAGE / "system-ontology" / "NODES.json"
CONTRACT_PATH = PACKAGE / "domainspec" / "event-sourcing" / "generated" / "contract.json"
LEDGER_PATH = RUNTIME / "fixtures" / "mutation-ledger.json"
TEST_PATH = RUNTIME / "tests" / "replay.rs"
LIBRARY_PATH = RUNTIME / "src" / "lib.rs"
CLI_PATH = RUNTIME / "src" / "main.rs"
W1_PATH = PACKAGE / "conformance" / "w1-schema-validation.json"
W2_PATH = PACKAGE / "conformance" / "w2-model-validation.json"
W3_PATH = PACKAGE / "conformance" / "w3-source-validation.json"
W4_PATH = PACKAGE / "conformance" / "w4-gate.json"
W5_PATH = PACKAGE / "conformance" / "w5-runtime-validation.json"
BACKEND_RECEIPT_PATH = PACKAGE / "conformance" / "domainspec-backend-validation.json"
W2_DECISION_PATH = LAB / "docs" / "decisions" / "0009-w2-product-business-admission" / "decision.json"
PROFILE_DECISION_PATH = LAB / "docs" / "decisions" / "0008-domainspec-development-profile-admission" / "decision.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(arguments: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env=env,
    )


def find_node(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    direct = shutil.which("node")
    if direct:
        return direct
    candidates = sorted(Path("/home/vrondelli/.nvm/versions/node").glob("v*/bin/node"))
    return str(candidates[-1]) if candidates else None


def find_cargo() -> str | None:
    direct = shutil.which("cargo")
    if direct:
        return direct
    candidates = sorted(Path("/home/vrondelli/.rustup/toolchains").glob("*/bin/cargo"))
    if candidates:
        return str(candidates[-1])
    cargo_home = Path("/home/vrondelli/.cargo/bin/cargo")
    return str(cargo_home) if cargo_home.is_file() else None


def test_bodies(source: str) -> dict[str, str]:
    bodies: dict[str, str] = {}
    header = re.compile(r"#\[test\]\s*fn\s+([a-z0-9_]+)\s*\(\)\s*\{")
    for match in header.finditer(source):
        depth = 1
        cursor = match.end()
        while cursor < len(source) and depth:
            if source[cursor] == "{":
                depth += 1
            elif source[cursor] == "}":
                depth -= 1
            cursor += 1
        if depth == 0:
            bodies[match.group(1)] = source[match.end(): cursor - 1]
    return bodies


def parse_json_output(result: subprocess.CompletedProcess[str]) -> dict[str, Any] | None:
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--node")
    parser.add_argument("--write-receipts", action="store_true")
    args = parser.parse_args()

    binding = load(BINDING_PATH)
    graph = load(GRAPH_PATH)
    system_nodes = load(SYSTEM_NODES_PATH)
    contract = load(CONTRACT_PATH)
    ledger = load(LEDGER_PATH)
    w1, w2, w3, w4, w5 = map(load, [W1_PATH, W2_PATH, W3_PATH, W4_PATH, W5_PATH])
    profile_decision = load(PROFILE_DECISION_PATH)
    w2_decision = load(W2_DECISION_PATH)
    test_source = TEST_PATH.read_text(encoding="utf-8")
    implementation_source = LIBRARY_PATH.read_text(encoding="utf-8") + "\n" + CLI_PATH.read_text(encoding="utf-8")
    bodies = test_bodies(test_source)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})

    predecessor_pass = (
        w1.get("result") == "PASS"
        and w2.get("result") == "PASS"
        and w3.get("result") == "PASS"
        and w4.get("result") == "PASS"
        and w5.get("result") == "PASS"
        and w5.get("downstream", {}).get("W6") == "ready"
        and binding.get("entry_gate", {}).get("receipt_sha256") == digest(W5_PATH)
        and binding.get("entry_gate", {}).get("result") == "PASS"
        and binding.get("entry_gate", {}).get("successor_state") == "ready"
    )
    record("w1-through-w5-predecessor", predecessor_pass, {
        "w1": w1.get("result"), "w2": w2.get("result"), "w3": w3.get("result"),
        "w4": w4.get("result"), "w5": w5.get("result"), "w6": w5.get("downstream", {}).get("W6"),
    })

    admission_pass = (
        profile_decision.get("decision_source", {}).get("selection_token") == "DPADM-1"
        and profile_decision.get("admission_status") == "admitted"
        and w2_decision.get("decision_source", {}).get("selection_token") == "W2ADM-1"
        and w2_decision.get("admission_status") == "admitted"
        and binding.get("ontology_id") == "cal.ontology-lifecycle.business-domain.v2-candidate"
        and binding.get("status") == "candidate-pending-human-acceptance"
        and binding.get("authority_effect") == "none"
    )
    record("bounded-predecessor-admissions", admission_pass, {
        "profile_selection": profile_decision.get("decision_source", {}).get("selection_token"),
        "w2_selection": w2_decision.get("decision_source", {}).get("selection_token"),
        "binding_status": binding.get("status"),
    })

    artifact_bindings = binding.get("artifact_bindings", [])
    artifact_paths = [entry.get("path") for entry in artifact_bindings]
    duplicate_artifacts = sorted({path for path in artifact_paths if artifact_paths.count(path) > 1})
    artifact_failures: list[dict[str, str]] = []
    for entry in artifact_bindings:
        path = (LAB / entry["path"]).resolve()
        if not path.is_file():
            artifact_failures.append({"path": entry["path"], "failure": "missing"})
        elif digest(path) != entry.get("sha256"):
            artifact_failures.append({"path": entry["path"], "failure": "digest-mismatch"})
    required_artifacts = {
        "docs/definition-packs/0002-governed-ontology-node-model/handled-definitions.json",
        "docs/decisions/0008-domainspec-development-profile-admission/decision.json",
        "docs/decisions/0009-w2-product-business-admission/decision.json",
        "ontology-lifecycle/product-capability.json",
        "ontology-lifecycle/business-ontology.json",
        "ontology-lifecycle/domainspec/project.json",
        "ontology-lifecycle/domainspec/.domainspec/generated/graph.json",
        "ontology-lifecycle/domainspec/event-sourcing/generated/contract.json",
        "ontology-lifecycle/system-ontology/NODES.json",
        "ontology-lifecycle/system-ontology/RELATIONS.json",
        "ontology-lifecycle/system-ontology/PROFILE.json",
        "ontology-lifecycle/runtime/Cargo.toml",
        "ontology-lifecycle/runtime/Cargo.lock",
        "ontology-lifecycle/runtime/src/lib.rs",
        "ontology-lifecycle/runtime/src/main.rs",
        "ontology-lifecycle/runtime/tests/replay.rs",
        "ontology-lifecycle/runtime/fixtures/mutation-ledger.json",
        "ontology-lifecycle/conformance/w4-gate.json",
        "ontology-lifecycle/conformance/w5-runtime-validation.json",
    }
    missing_required = sorted(required_artifacts - set(artifact_paths))
    artifact_pass = not artifact_failures and not duplicate_artifacts and not missing_required
    record("exact-artifact-binding-currentness", artifact_pass, {
        "bound_count": len(artifact_bindings), "failures": artifact_failures,
        "duplicates": duplicate_artifacts, "missing_required": missing_required,
    })

    graph_ids = {entry["node_id"] for entry in graph.get("nodes", [])}
    system_ids = {entry["node_id"] for entry in system_nodes.get("nodes", [])}
    node_bindings = binding.get("node_bindings", [])
    bound_ids = {entry.get("node_id") for entry in node_bindings}
    node_failures: list[dict[str, str]] = []
    symbol_failures: list[dict[str, str]] = []
    for entry in node_bindings:
        source = (LAB / entry["source_path"]).resolve()
        if not source.is_file() or digest(source) != entry.get("source_sha256"):
            node_failures.append({"node_id": entry.get("node_id", ""), "failure": "source-digest"})
        symbols = entry.get("implementation_symbols", [])
        if not symbols:
            node_failures.append({"node_id": entry.get("node_id", ""), "failure": "no-symbol"})
        for symbol in symbols:
            parts = symbol.split("::")
            if any(re.search(rf"\b{re.escape(part)}\b", implementation_source) is None for part in parts):
                symbol_failures.append({"node_id": entry.get("node_id", ""), "symbol": symbol})
    node_pass = graph_ids == system_ids == bound_ids and not node_failures and not symbol_failures
    record("compiled-node-and-symbol-closure", node_pass, {
        "graph_nodes": len(graph_ids), "system_nodes": len(system_ids), "bound_nodes": len(bound_ids),
        "missing_bindings": sorted(graph_ids - bound_ids), "extra_bindings": sorted(bound_ids - graph_ids),
        "node_failures": node_failures, "symbol_failures": symbol_failures,
    })

    contract_obligations = set(contract.get("runtimeObligations", []))
    ledger_map = {entry.get("obligation"): entry for entry in ledger.get("obligations", [])}
    obligation_bindings = {entry.get("obligation"): entry for entry in binding.get("runtime_obligation_bindings", [])}
    obligation_failures: list[dict[str, str]] = []
    for obligation in sorted(contract_obligations):
        ledger_entry = ledger_map.get(obligation, {})
        bound_entry = obligation_bindings.get(obligation, {})
        for field in ("positive_test", "mutation_test", "expected_failure"):
            if bound_entry.get(field) != ledger_entry.get(field):
                obligation_failures.append({"obligation": obligation, "failure": f"{field}-mismatch"})
        if not bound_entry.get("implementation_symbols"):
            obligation_failures.append({"obligation": obligation, "failure": "no-symbol"})
        mutation_name = bound_entry.get("mutation_test")
        body = bodies.get(mutation_name, "")
        expected_codes = re.findall(r"[A-Z][A-Z0-9_]{2,}", str(bound_entry.get("expected_failure", "")))
        for code in expected_codes:
            if code not in body:
                obligation_failures.append({"obligation": obligation, "failure": f"expected-code-not-asserted:{code}"})
        if bound_entry.get("positive_test") not in bodies:
            obligation_failures.append({"obligation": obligation, "failure": "positive-test-missing"})
        if mutation_name not in bodies:
            obligation_failures.append({"obligation": obligation, "failure": "mutation-test-missing"})
    obligation_pass = (
        contract_obligations == set(ledger_map) == set(obligation_bindings)
        and len(contract_obligations) == 12
        and not obligation_failures
    )
    record("runtime-obligation-and-vacuity-contract", obligation_pass, {
        "contract": len(contract_obligations), "ledger": len(ledger_map), "binding": len(obligation_bindings),
        "failures": obligation_failures,
    })

    declared_empty = all(not binding.get(field) for field in (
        "unbound_artifacts", "unbound_nodes", "unbound_runtime_obligations",
        "unbound_implementation_symbols", "residue",
    ))
    record("declared-residue-closure", declared_empty, {
        field: binding.get(field) for field in (
            "unbound_artifacts", "unbound_nodes", "unbound_runtime_obligations",
            "unbound_implementation_symbols", "residue",
        )
    })

    cargo = find_cargo()
    individual_results: list[dict[str, Any]] = []
    formatting = build = full_tests = None
    if cargo:
        rust_env = dict(os.environ)
        rust_env["PATH"] = str(Path(cargo).parent) + os.pathsep + rust_env.get("PATH", "")
        rust_env["TMPDIR"] = "/tmp"
        test_names = sorted({
            entry[field]
            for entry in obligation_bindings.values()
            for field in ("positive_test", "mutation_test")
        })
        for name in test_names:
            result = run([cargo, "test", "--locked", "--test", "replay", name, "--", "--exact"], RUNTIME, rust_env)
            individual_results.append({"test": name, "exit_code": result.returncode, "one_passed": "1 passed; 0 failed" in result.stdout})
        formatting = run([cargo, "fmt", "--all", "--", "--check"], RUNTIME, rust_env)
        build = run([cargo, "check", "--locked", "--all-targets"], RUNTIME, rust_env)
        full_tests = run([cargo, "test", "--locked"], RUNTIME, rust_env)
        passed_counts = [int(value) for value in re.findall(r"test result: ok\. (\d+) passed", full_tests.stdout)]
        executed = max(passed_counts, default=0)
        rust_pass = (
            all(item["exit_code"] == 0 and item["one_passed"] for item in individual_results)
            and formatting.returncode == 0 and build.returncode == 0
            and full_tests.returncode == 0 and executed == len(bodies) == 19
        )
        cargo_version = run([cargo, "--version"], RUNTIME, rust_env).stdout.strip()
    else:
        rust_pass = False
        executed = 0
        cargo_version = "unavailable"
    record("independent-rust-and-mutation-execution", rust_pass, {
        "individual_tests": individual_results,
        "format_exit": formatting.returncode if formatting else None,
        "check_exit": build.returncode if build else None,
        "test_exit": full_tests.returncode if full_tests else None,
        "executed_tests": executed, "declared_tests": len(bodies),
    })

    node = find_node(args.node)
    compile_runs: list[dict[str, Any] | None] = []
    event_runs: list[dict[str, Any] | None] = []
    node_version = "unavailable"
    if node:
        node_version = run([node, "--version"], DOMAINSPEC_IMPL).stdout.strip()
        env = dict(os.environ)
        env["PATH"] = str(Path(node).parent) + os.pathsep + env.get("PATH", "")
        env["TMPDIR"] = "/tmp"
        env["NODE_NO_WARNINGS"] = "1"
        for _ in range(2):
            result = run([node, "--import", "tsx", str(PACKAGE / "scripts" / "compile-domainspec.ts"), "--check"], DOMAINSPEC_IMPL, env)
            compile_runs.append(parse_json_output(result) if result.returncode == 0 else None)
            result = run([node, "--import", "tsx", str(PACKAGE / "scripts" / "compile-event-sourcing-contract.ts"), "--check"], DOMAINSPEC_IMPL, env)
            event_runs.append(parse_json_output(result) if result.returncode == 0 else None)
        tsc = BACKEND / "node_modules" / ".bin" / "tsc"
        tsx = BACKEND / "node_modules" / ".bin" / "tsx"
        backend_tests = sorted(str(path.relative_to(BACKEND)) for path in (BACKEND / "src").rglob("*.test.ts"))
        typecheck = run([str(tsc), "-p", "tsconfig.json", "--noEmit"], BACKEND, env)
        backend_suite = run([str(tsx), "--test", *backend_tests], BACKEND, env)
        backend_test_match = re.search(r"(?:ℹ|#) tests (\d+)", backend_suite.stdout)
        backend_pass_match = re.search(r"(?:ℹ|#) pass (\d+)", backend_suite.stdout)
        backend_test_count = int(backend_test_match.group(1)) if backend_test_match else 0
        backend_pass_count = int(backend_pass_match.group(1)) if backend_pass_match else 0
        backend_pass = (
            typecheck.returncode == 0
            and backend_suite.returncode == 0
            and backend_test_count == backend_pass_count == 34
        )
    else:
        typecheck = backend_suite = None
        backend_tests = []
        backend_test_count = 0
        backend_pass_count = 0
        backend_pass = False
    compile_pass = (
        len(compile_runs) == 2 and None not in compile_runs and compile_runs[0] == compile_runs[1]
        and compile_runs[0].get("status") == "PASS"
        and len(event_runs) == 2 and None not in event_runs and event_runs[0] == event_runs[1]
        and event_runs[0].get("status") == "PASS"
    )
    record("domainspec-and-event-contract-two-run", compile_pass, {
        "graph_runs_equal": len(compile_runs) == 2 and compile_runs[0] == compile_runs[1],
        "event_runs_equal": len(event_runs) == 2 and event_runs[0] == event_runs[1],
        "graph_sha256": digest(GRAPH_PATH), "contract_sha256": digest(CONTRACT_PATH),
    })
    record("domainspec-backend-full-suite", backend_pass, {
        "typecheck_exit": typecheck.returncode if typecheck else None,
        "suite_exit": backend_suite.returncode if backend_suite else None,
        "test_file_count": len(backend_tests), "test_count": backend_test_count,
        "pass_count": backend_pass_count,
        "bound_receipt_sha256": digest(BACKEND_RECEIPT_PATH),
    })

    technical_pass = all(check["result"] == "PASS" for check in checks)
    acceptance_state = "pending-human-decision"
    result = "not_evaluable" if technical_pass else "FAIL"
    blockers = ([{
        "code": "W6_HUMAN_ACCEPTANCE_REQUIRED",
        "owner": "independent validation and human acceptance owners",
        "resolution": "Bind one explicit owner selection to this exact ConstructionBinding and verification digest before W7.",
    }] if technical_pass else [{
        "code": "W6_TECHNICAL_CONFORMANCE_FAILED",
        "failed_checks": [check["check_id"] for check in checks if check["result"] != "PASS"],
    }])
    inputs = [
        SCRIPT, BINDING_PATH, GRAPH_PATH, SYSTEM_NODES_PATH, CONTRACT_PATH, LEDGER_PATH,
        TEST_PATH, LIBRARY_PATH, CLI_PATH, W1_PATH, W2_PATH, W3_PATH, W4_PATH, W5_PATH,
        BACKEND_RECEIPT_PATH, PROFILE_DECISION_PATH, W2_DECISION_PATH,
    ]
    verification = {
        "schema_version": "cal-ontology-lifecycle-verification/v2",
        "verification_id": "CAL-VERIFY-ONTOLOGY-LIFECYCLE-W6-002",
        "gate_id": "G-W6",
        "result": result,
        "technical_result": "PASS" if technical_pass else "FAIL",
        "acceptance_state": acceptance_state,
        "construction_binding": {"path": "ontology-lifecycle/conformance/construction-binding.json", "sha256": digest(BINDING_PATH)},
        "checks": checks,
        "coverage": {
            "artifact_bindings": len(artifact_bindings), "compiled_nodes": len(graph_ids),
            "runtime_obligations": len(contract_obligations), "rust_tests": executed,
            "individual_vacuity_tests": len(individual_results),
        },
        "runtime": {"node": node_version, "cargo": cargo_version},
        "blockers": blockers,
        "downstream": {"W7": "not_evaluable"},
        "inputs": [{"path": str(path.relative_to(LAB)), "sha256": digest(path)} for path in inputs],
        "authority_effect": "none",
        "claim_ceiling": "Independent W6 technical conformance evidence only. Human acceptance of this exact immutable candidate is required before any W7 migration rehearsal. No publication, release, deployment, cutover, credential, destructive-action, or external-effect authority is granted.",
    }
    if args.write_receipts:
        stable_write(VERIFICATION_PATH, verification)
        d65_status = {
            "schema_version": "cal-d65-status-projection/v2-candidate",
            "status_id": "CAL-D65-ONTOLOGY-LIFECYCLE-002",
            "construction_invariant": "CAV2-D65",
            "ontology_id": binding.get("ontology_id"),
            "status": "candidate-pending-human-acceptance" if technical_pass else "candidate-blocked",
            "stages": [
                {"stage": "canonical-definitions", "state": "selected-candidate", "ref": "docs/decisions/0006-governed-node-definition-selection/decision.json"},
                {"stage": "product-capability", "state": "admitted-for-lab-d65", "ref": "docs/decisions/0009-w2-product-business-admission/decision.json"},
                {"stage": "capability-local-business-ontology", "state": "admitted-for-lab-d65", "ref": "docs/decisions/0009-w2-product-business-admission/decision.json"},
                {"stage": "domainspec-v2-authored-source", "state": "validated", "ref": "ontology-lifecycle/conformance/w3-source-validation.json"},
                {"stage": "deterministic-compiled-graph-and-system-ontology", "state": "PASS", "ref": "ontology-lifecycle/conformance/w4-gate.json"},
                {"stage": "rust-implementation", "state": "PASS", "ref": "ontology-lifecycle/conformance/w5-runtime-validation.json"},
                {"stage": "exact-implementation-binding", "state": "current-candidate", "ref": "ontology-lifecycle/conformance/construction-binding.json", "sha256": digest(BINDING_PATH)},
                {"stage": "independent-non-vacuous-conformance", "state": "PASS" if technical_pass else "FAIL", "ref": "ontology-lifecycle/conformance/verification.json", "sha256": digest(VERIFICATION_PATH)},
                {"stage": "human-w6-acceptance", "state": "pending"},
            ],
            "residue": [
                "Exact human acceptance of the frozen W6 binding and verification candidate is pending.",
                "W7 isolated migration rehearsal has not started and no legacy source is selected.",
                "W8 aggregate immutable-epoch validation has not run.",
            ],
            "authority_effect": "none",
            "claim_ceiling": "Current D65 candidate status projection only. Technical W6 PASS does not accept the implementation, authorize migration rehearsal, publish, release, deploy, cut over, or grant external effects.",
        }
        stable_write(D65_STATUS_PATH, d65_status)
    print(json.dumps({
        "gate_id": "G-W6", "result": result, "technical_result": verification["technical_result"],
        "acceptance_state": acceptance_state, "coverage": verification["coverage"],
        "failed_checks": [check["check_id"] for check in checks if check["result"] != "PASS"],
        "blockers": blockers,
    }, indent=2, sort_keys=True))
    return 0 if technical_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

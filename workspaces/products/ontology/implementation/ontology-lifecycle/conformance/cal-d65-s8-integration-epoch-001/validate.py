#!/usr/bin/env python3
"""Collect-all independent D65-S8 integration conformance validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
EPOCH = SCRIPT.parent
LAB = SCRIPT.parents[3]
MANIFEST = EPOCH / "manifest.json"
VERDICT = EPOCH / "verdict.json"
RUNTIME = LAB / "ontology-lifecycle/runtime"

RUNTIME_COPY_FILES = (
    "Cargo.toml",
    "Cargo.lock",
    "src/lib.rs",
    "src/main.rs",
    "src/context_adapter.rs",
    "src/governance_context_adapter.rs",
    "tests/context_binding.rs",
)

TEST_LINE = re.compile(r"^test ([^ ]+) \.\.\. (ok|FAILED|ignored)$")
RUN_LINE = re.compile(r"^\s*Running (?:unittests )?([^ ]+)")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(
    arguments: list[str], cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def rust_env(target: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["CARGO_TARGET_DIR"] = str(target)
    complete_toolchain = Path(
        "/home/vrondelli/.rustup/toolchains/1.94.1-x86_64-unknown-linux-gnu/bin"
    )
    if complete_toolchain.is_dir():
        env["PATH"] = str(complete_toolchain) + os.pathsep + env.get("PATH", "")
    return env


def verify_refs(refs: list[dict[str, Any]]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for ref in refs:
        path = LAB / ref["path"]
        if not path.is_file():
            failures.append({"path": ref["path"], "failure": "missing"})
            continue
        actual = digest(path)
        if actual != ref["sha256"]:
            failures.append(
                {
                    "path": ref["path"],
                    "failure": "digest-mismatch",
                    "expected_sha256": ref["sha256"],
                    "actual_sha256": actual,
                }
            )
    return failures


def ref_digests(refs: list[dict[str, Any]]) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for ref in refs:
        path = LAB / ref["path"]
        result[ref["path"]] = digest(path) if path.is_file() else None
    return result


def suite_name(raw: str) -> str:
    normalized = raw.replace("\\", "/")
    if "tests/context_binding.rs" in normalized:
        return "context_binding"
    if "tests/replay.rs" in normalized:
        return "replay"
    if "src/lib.rs" in normalized:
        return "lib"
    if "src/main.rs" in normalized:
        return "main"
    return Path(normalized).stem


def parse_tests(output: str) -> list[dict[str, str]]:
    suite = "unknown"
    results: list[dict[str, str]] = []
    for line in output.splitlines():
        running = RUN_LINE.match(line)
        if running:
            suite = suite_name(running.group(1))
            continue
        test = TEST_LINE.match(line.strip())
        if test:
            results.append(
                {
                    "test": f"{suite}::{test.group(1)}",
                    "status": test.group(2),
                }
            )
    return sorted(results, key=lambda item: (item["test"], item["status"]))


def execute_full_suite(target: Path) -> dict[str, Any]:
    process = run(
        ["cargo", "test", "--locked", "--", "--test-threads=1"],
        RUNTIME,
        rust_env(target),
    )
    results = parse_tests(process.stdout)
    return {
        "exit_code": process.returncode,
        "tests": results,
        "test_count": len(results),
        "passed_count": sum(item["status"] == "ok" for item in results),
        "replay_test_count": sum(item["test"].startswith("replay::") for item in results),
        "context_binding_test_count": sum(
            item["test"].startswith("context_binding::") for item in results
        ),
    }


def create_runtime_copy(destination: Path) -> None:
    for relative in RUNTIME_COPY_FILES:
        source = RUNTIME / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"mutation anchor count for {path.name}: {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def failed_test_probe(
    root: Path,
    name: str,
    test_name: str,
    mutate: Callable[[Path], None],
) -> dict[str, Any]:
    crate = root / name
    create_runtime_copy(crate)
    try:
        mutate(crate)
    except Exception as exc:
        return {
            "probe_id": name,
            "result": "BLOCK",
            "mutation_applied": False,
            "error": type(exc).__name__,
        }
    process = run(
        [
            "cargo",
            "test",
            "--locked",
            "--test",
            "context_binding",
            "--",
            test_name,
            "--exact",
            "--test-threads=1",
        ],
        crate,
        rust_env(root / f"target-{name}"),
    )
    tests = parse_tests(process.stdout)
    expected = f"context_binding::{test_name}"
    detector_fired = (
        process.returncode != 0
        and {"test": expected, "status": "FAILED"} in tests
    )
    return {
        "probe_id": name,
        "result": "PASS" if detector_fired else "BLOCK",
        "mutation_applied": True,
        "expected_detector": expected,
        "process_exit_code": process.returncode,
        "normalized_test_results": tests,
        "detector_fired": detector_fired,
    }


def surviving_test_probe(
    root: Path,
    name: str,
    test_name: str,
    mutate: Callable[[Path], None],
) -> dict[str, Any]:
    crate = root / name
    create_runtime_copy(crate)
    try:
        mutate(crate)
    except Exception as exc:
        return {
            "probe_id": name,
            "result": "BLOCK",
            "mutation_applied": False,
            "error": type(exc).__name__,
        }
    process = run(
        [
            "cargo",
            "test",
            "--locked",
            "--test",
            "context_binding",
            "--",
            test_name,
            "--exact",
            "--test-threads=1",
        ],
        crate,
        rust_env(root / f"target-{name}"),
    )
    tests = parse_tests(process.stdout)
    expected = f"context_binding::{test_name}"
    surviving_guard_detected = (
        process.returncode == 0 and {"test": expected, "status": "ok"} in tests
    )
    return {
        "probe_id": name,
        "result": "PASS" if surviving_guard_detected else "BLOCK",
        "mutation_applied": True,
        "expected_surviving_detector": expected,
        "process_exit_code": process.returncode,
        "normalized_test_results": tests,
        "surviving_guard_detected": surviving_guard_detected,
    }


def canonical_source_mutation(crate: Path) -> None:
    replace_once(
        crate / "src/context_adapter.rs",
        "canonical_replay_source: false,",
        "canonical_replay_source: true,",
    )


def fractured_cut_mutation(crate: Path) -> None:
    replace_once(
        crate / "src/governance_context_adapter.rs",
        "source_cursor: projection.source_cursor,\n"
        "        source_event_set_digest: projection.source_event_set_digest.clone(),",
        "source_cursor: projection.source_cursor.saturating_add(1),\n"
        "        source_event_set_digest: format!(\"fractured-{}\", projection.source_event_set_digest),",
    )


def missing_join_mutation(crate: Path) -> None:
    replace_once(
        crate / "src/governance_context_adapter.rs",
        "let mut governed_nodes = request\n"
        "        .selector\n"
        "        .required_subject_set\n"
        "        .iter()\n"
        "        .filter(|identity| identity.subject_kind == SubjectKind::Node)\n"
        "        .map(|identity| {\n"
        "            store.governed_node_view(\n"
        "                identity,\n"
        "                request.selector.semantic_cursor,\n"
        "                Some(request.selector_ref.clone()),\n"
        "            )\n"
        "        })\n"
        "        .collect::<Result<Vec<_>, _>>()?;",
        "let mut governed_nodes: Vec<GovernedOntologyNodeView> = Vec::new();",
    )


def context_projection_governance_mutation(crate: Path) -> None:
    replace_once(
        crate / "src/lib.rs",
        "if !self.governance_events.iter().any(|governance| {\n"
        "                exact_reference_matches(&governance.event.semantic_ref, &loaded.event)\n"
        "            }) {\n"
        "                return Err(ReplayFailure::new(\n"
        "                    \"EXACT_GOVERNANCE_STATE_MISSING\",\n"
        "                    loaded.event.event_id.clone(),\n"
        "                ));\n"
        "            }",
        "let _exact_governance_guard_neutralized_for_hostile_probe = true;",
    )


def all_governance_join_guards_mutation(crate: Path) -> None:
    missing_join_mutation(crate)
    context_projection_governance_mutation(crate)


WRONG_CONTEXT_PROBES = r'''

#[test]
fn hostile_wrong_ontology_context_id_fails_closed() {
    let fixture = fixture(true);
    let store = EventStore::load(&fixture.semantic, &fixture.governance).expect("event store");
    let mut request = ontology_request();
    request.context_id = "cal.context.wrong".to_owned();
    assert_eq!(
        OntologyLifecycleContextAdapter::new(&store)
            .project(&request)
            .expect_err("wrong ontology context id must fail")
            .code,
        "CONTEXT_ID_MISMATCH"
    );
}

#[test]
fn hostile_wrong_ontology_context_version_fails_closed() {
    let fixture = fixture(true);
    let store = EventStore::load(&fixture.semantic, &fixture.governance).expect("event store");
    let mut request = ontology_request();
    request.context_version = "0.0.0-wrong".to_owned();
    assert_eq!(
        OntologyLifecycleContextAdapter::new(&store)
            .project(&request)
            .expect_err("wrong ontology context version must fail")
            .code,
        "CONTEXT_VERSION_MISMATCH"
    );
}

#[test]
fn hostile_wrong_governance_context_id_fails_closed() {
    let fixture = fixture(true);
    let store = EventStore::load(&fixture.semantic, &fixture.governance).expect("event store");
    let mut request = governance_request();
    request.context_id = "cal.context.wrong".to_owned();
    assert_eq!(
        GovernanceContextAdapter::new(&store)
            .project(&request)
            .expect_err("wrong governance context id must fail")
            .code,
        "CONTEXT_ID_MISMATCH"
    );
}

#[test]
fn hostile_wrong_governance_context_version_fails_closed() {
    let fixture = fixture(true);
    let store = EventStore::load(&fixture.semantic, &fixture.governance).expect("event store");
    let mut request = governance_request();
    request.context_version = "0.0.0-wrong".to_owned();
    assert_eq!(
        GovernanceContextAdapter::new(&store)
            .project(&request)
            .expect_err("wrong governance context version must fail")
            .code,
        "CONTEXT_VERSION_MISMATCH"
    );
}
'''


def wrong_context_probes(root: Path) -> dict[str, Any]:
    name = "wrong-context-id-version"
    crate = root / name
    create_runtime_copy(crate)
    tests_path = crate / "tests/context_binding.rs"
    tests_path.write_text(
        tests_path.read_text(encoding="utf-8") + WRONG_CONTEXT_PROBES,
        encoding="utf-8",
    )
    process = run(
        [
            "cargo",
            "test",
            "--locked",
            "--test",
            "context_binding",
            "--",
            "hostile_wrong_",
            "--test-threads=1",
        ],
        crate,
        rust_env(root / f"target-{name}"),
    )
    tests = parse_tests(process.stdout)
    expected = {
        "context_binding::hostile_wrong_ontology_context_id_fails_closed",
        "context_binding::hostile_wrong_ontology_context_version_fails_closed",
        "context_binding::hostile_wrong_governance_context_id_fails_closed",
        "context_binding::hostile_wrong_governance_context_version_fails_closed",
    }
    observed_passes = {item["test"] for item in tests if item["status"] == "ok"}
    passed = process.returncode == 0 and observed_passes == expected
    return {
        "probe_id": name,
        "result": "PASS" if passed else "BLOCK",
        "process_exit_code": process.returncode,
        "expected_probe_count": 4,
        "observed_probe_count": len(tests),
        "normalized_test_results": tests,
        "failed_closed": passed,
    }


def static_isolation() -> dict[str, Any]:
    governance = (RUNTIME / "src/governance_context_adapter.rs").read_text(
        encoding="utf-8"
    )
    library = (RUNTIME / "src/lib.rs").read_text(encoding="utf-8")
    dependency_tokens = (
        "context_adapter",
        "OntologyLifecycleContextAdapter",
        "ONTOLOGY_LIFECYCLE_CONTEXT_ID",
        "project_ontology_lifecycle_context",
    )
    governance_dependencies = [token for token in dependency_tokens if token in governance]
    export_pattern = re.compile(
        r"(?m)^\s*(?:pub\s+)?mod\s+(?:context_adapter|governance_context_adapter)\s*;"
    )
    exports = export_pattern.findall(library)
    passed = not governance_dependencies and not exports
    return {
        "probe_id": "static-adapter-isolation",
        "result": "PASS" if passed else "BLOCK",
        "governance_adapter_context_adapter_dependencies": governance_dependencies,
        "frozen_library_adapter_exports": exports,
        "isolated": passed,
    }


def accepted_contract_state(manifest: dict[str, Any]) -> dict[str, Any]:
    w8_acceptance = load(
        LAB / "docs/decisions/0012-w8-candidate-acceptance/decision.json"
    )
    w8_manifest_path = (
        LAB / "ontology-lifecycle/conformance/cal-w8-final-epoch-001/manifest.json"
    )
    w8_verdict_path = (
        LAB / "ontology-lifecycle/conformance/cal-w8-final-epoch-001/verdict.json"
    )
    w8_verdict = load(w8_verdict_path)
    d65_acceptance = load(
        LAB / "docs/decisions/0023-d65-implementation-binding-acceptance/decision.json"
    )
    d65_validation = load(
        LAB
        / "docs/decisions/0023-d65-implementation-binding-acceptance/receipts/validation.json"
    )
    binding_path = (
        LAB
        / "ontology-lifecycle/conformance/implementation-binding/cal-ontology-runtime-integration-epoch-001/binding.json"
    )
    binding = load(binding_path)
    w8_refs = w8_acceptance.get("accepted_w8_epoch", {})
    d65_refs = d65_acceptance.get("candidate_refs", {})
    assertions = {
        "w8_selection_is_W8ACC_1": w8_acceptance.get("selection", {}).get("option_id")
        == "W8ACC-1",
        "w8_acceptance_manifest_is_current": w8_refs.get("manifest_ref", {}).get(
            "sha256"
        )
        == digest(w8_manifest_path),
        "w8_acceptance_verdict_is_current": w8_refs.get("verdict_ref", {}).get(
            "sha256"
        )
        == digest(w8_verdict_path),
        "w8_verdict_passes": w8_verdict.get("result") == "PASS"
        and w8_verdict.get("gate_id") == "G-W8-FINAL"
        and not w8_verdict.get("blockers"),
        "d65_selection_is_D65BIND_1": d65_acceptance.get("selection", {}).get(
            "option_id"
        )
        == "D65BIND-1",
        "d65_binding_is_current": d65_refs.get("binding_sha256")
        == digest(binding_path),
        "d65_acceptance_validation_passes": d65_validation.get("result") == "PASS"
        and d65_validation.get("resolved_gate") == "G-D65-BINDING",
        "ontology_identity_matches": binding.get("ontology_id")
        == manifest.get("ontology_id"),
    }
    return {
        "result": "PASS" if all(assertions.values()) else "BLOCK",
        "assertions": assertions,
        "w8_manifest_sha256": digest(w8_manifest_path),
        "w8_verdict_sha256": digest(w8_verdict_path),
        "accepted_binding_sha256": digest(binding_path),
    }


def validation(
    validation_id: str,
    passed: bool,
    detail: dict[str, Any],
    prerequisite: bool = True,
    causes: list[str] | None = None,
) -> dict[str, Any]:
    if not prerequisite:
        return {
            "validation_id": validation_id,
            "result": "not_evaluable",
            "causes": causes or ["prerequisite-not-pass"],
            "detail": detail,
        }
    return {
        "validation_id": validation_id,
        "result": "PASS" if passed else "BLOCK",
        "detail": detail,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-verdict", action="store_true")
    args = parser.parse_args()

    manifest = load(MANIFEST)
    dependencies = manifest["dependencies"]
    postimages = manifest["d65_s7_postimages"]
    all_refs = dependencies + postimages
    before = ref_digests(all_refs)
    initial_dependency_failures = verify_refs(dependencies)
    initial_postimage_failures = verify_refs(postimages)
    contract = accepted_contract_state(manifest)

    with tempfile.TemporaryDirectory(prefix="cal-d65-s8-") as raw:
        temporary = Path(raw)
        target = temporary / "integration-target"
        run_1 = execute_full_suite(target)
        run_2 = execute_full_suite(target)

        hostile = [
            failed_test_probe(
                temporary,
                "canonical-replay-source-flip",
                "context_projection_never_becomes_replay_source",
                canonical_source_mutation,
            ),
            failed_test_probe(
                temporary,
                "fractured-governance-envelope-cut",
                "both_contexts_share_one_exact_cut",
                fractured_cut_mutation,
            ),
            surviving_test_probe(
                temporary,
                "missing-governance-adapter-guard-only-disabled",
                "missing_exact_governance_join_fails_closed",
                missing_join_mutation,
            ),
            failed_test_probe(
                temporary,
                "missing-governance-all-guards-disabled",
                "missing_exact_governance_join_fails_closed",
                all_governance_join_guards_mutation,
            ),
            wrong_context_probes(temporary),
            static_isolation(),
        ]

    final_dependency_failures = verify_refs(dependencies)
    final_postimage_failures = verify_refs(postimages)
    after = ref_digests(all_refs)
    no_during_run_change = before == after
    source_current = (
        not initial_dependency_failures
        and not initial_postimage_failures
        and not final_dependency_failures
        and not final_postimage_failures
        and no_during_run_change
    )

    expected = manifest["runtime_suite"]
    normalized_equal = run_1["tests"] == run_2["tests"]
    suite_shape_pass = all(
        run_data["exit_code"] == 0
        and run_data["test_count"] == expected["expected_total_tests"]
        and run_data["passed_count"] == expected["expected_total_tests"]
        and run_data["replay_test_count"] == expected["expected_replay_tests"]
        and run_data["context_binding_test_count"]
        == expected["expected_context_binding_tests"]
        for run_data in (run_1, run_2)
    )
    integration_pass = normalized_equal and suite_shape_pass
    observed_passes = {
        item["test"] for item in run_1["tests"] if item["status"] == "ok"
    }
    required_replay = set(expected["required_replay_equality_tests"])
    replay_pass = required_replay.issubset(observed_passes)
    vacuity_pass = all(item["result"] == "PASS" for item in hostile)

    checks: list[dict[str, Any]] = []
    frozen_prerequisite = not initial_dependency_failures
    checks.append(
        validation(
            "VAL-FROZEN-W8-CONTRACT",
            contract["result"] == "PASS",
            contract,
            prerequisite=frozen_prerequisite,
            causes=["selected-dependency-currentness-failed"],
        )
    )
    integration_prerequisite = source_current and contract["result"] == "PASS"
    checks.append(
        validation(
            "VAL-INTEGRATION-TWICE",
            integration_pass,
            {
                "serial_execution": True,
                "normalized_result_sets_equal": normalized_equal,
                "run_1": run_1,
                "run_2": run_2,
                "expected_total_tests": expected["expected_total_tests"],
                "expected_replay_tests": expected["expected_replay_tests"],
                "expected_context_binding_tests": expected[
                    "expected_context_binding_tests"
                ],
            },
            prerequisite=integration_prerequisite,
            causes=["frozen-input-or-accepted-contract-prerequisite-failed"],
        )
    )
    checks.append(
        validation(
            "VAL-REPLAY-EQUALITY",
            replay_pass,
            {
                "required_tests": sorted(required_replay),
                "observed_required_tests": sorted(required_replay & observed_passes),
            },
            prerequisite=integration_prerequisite and integration_pass,
            causes=["integration-twice-not-pass"],
        )
    )
    checks.append(
        validation(
            "VAL-VACUITY",
            vacuity_pass,
            {
                "temporary_mutations_only": True,
                "hostile_probes": hostile,
            },
            prerequisite=integration_prerequisite and integration_pass,
            causes=["integration-twice-not-pass"],
        )
    )
    checks.append(
        validation(
            "VAL-SOURCE-IMMUTABILITY",
            source_current,
            {
                "selected_dependency_count": len(dependencies),
                "d65_s7_postimage_count": len(postimages),
                "initial_dependency_failures": initial_dependency_failures,
                "initial_postimage_failures": initial_postimage_failures,
                "final_dependency_failures": final_dependency_failures,
                "final_postimage_failures": final_postimage_failures,
                "selected_bytes_unchanged_during_run": no_during_run_change,
                "ambient_unselected_drift": "excluded",
            },
        )
    )
    preaggregate_pass = all(item["result"] == "PASS" for item in checks)
    residue = manifest.get("acceptance_critical_residue", [])
    checks.append(
        validation(
            "VAL-AGGREGATE-INTEGRATION",
            preaggregate_pass and not residue,
            {
                "all_preaggregate_validations_pass": preaggregate_pass,
                "acceptance_critical_residue": residue,
            },
        )
    )

    blockers = [
        {
            "code": "VALIDATION_NOT_PASS",
            "validation_id": item["validation_id"],
            "result": item["result"],
        }
        for item in checks
        if item["result"] != "PASS"
    ]
    result = "PASS" if not blockers else "BLOCK"
    verdict = {
        "schema_version": "cal.d65-s8-integration-candidate-verdict/v1",
        "epoch_id": manifest["epoch_id"],
        "construction_id": manifest["construction_id"],
        "ontology_id": manifest["ontology_id"],
        "stage_id": "D65-S8",
        "gate_id": "G-D65-CONFORMANCE",
        "result": result,
        "immutable_epoch": {
            "manifest_path": str(MANIFEST.relative_to(LAB)),
            "manifest_sha256": digest(MANIFEST),
            "validator_path": str(SCRIPT.relative_to(LAB)),
            "validator_sha256": digest(SCRIPT),
        },
        "validations": checks,
        "blockers": blockers,
        "acceptance_critical_residue": residue,
        "next_owner_gate": "G-INTEGRATION-ADMISSION-CUTOVER"
        if result == "PASS"
        else None,
        "authority_effect": "none",
        "claim_ceiling": manifest["claim_ceiling"],
    }
    if args.write_verdict:
        stable_write(VERDICT, verdict)
    print(
        json.dumps(
            {
                "epoch_id": verdict["epoch_id"],
                "gate_id": verdict["gate_id"],
                "result": result,
                "validation_results": {
                    item["validation_id"]: item["result"] for item in checks
                },
                "run_1_test_count": run_1["test_count"],
                "run_2_test_count": run_2["test_count"],
                "normalized_result_sets_equal": normalized_equal,
                "hostile_probe_results": {
                    item["probe_id"]: item["result"] for item in hostile
                },
                "blockers": blockers,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

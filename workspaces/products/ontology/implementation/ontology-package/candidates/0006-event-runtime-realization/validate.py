#!/usr/bin/env python3
"""Validate and exercise the exact event-runtime Product candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

CANDIDATE_DIR = Path(__file__).resolve().parent
REPO = CANDIDATE_DIR.parents[5]
CANDIDATE_PATH = CANDIDATE_DIR / "candidate.json"
BINDING_PATH = REPO / "implementation/bindings/ontology-product-event-runtime/v2/binding.json"
MANIFEST_PATH = REPO / "implementation/bindings/ontology-product-event-runtime/v2/Cargo.toml"
NAVIGATION_PATH = REPO / "product/products/ontology/v1/navigation/cohesive-lab-system/navigation.json"
RECEIPT_PATH = CANDIDATE_DIR / "receipts/validation.json"
VALIDATOR_TEST_PATH = CANDIDATE_DIR / "test_validate.py"

RUST_TESTS = {
    "exact_admitted_navigation_realizes_as_canonical_events",
    "independent_materializations_are_byte_equivalent",
    "latest_root_snapshot_is_calculated_from_latest_subject_event",
    "multiple_root_updates_survive_restart",
    "checkpoint_plus_tail_equals_full_replay",
    "context_projection_contains_all_nodes_and_relations_with_exact_governance",
    "restart_loads_the_same_event_calculated_observation",
    "missing_integration_epoch_fails_closed",
    "missing_event_fails_closed",
    "event_digest_tampering_fails_closed",
    "child_authority_inflation_is_rejected",
    "domainspec_collision_cannot_be_removed",
    "exact_navigation_digest_is_required",
    "nonempty_runtime_target_is_refused",
    "projected_subject_kinds_remain_distinct",
}


class ValidationFailure(Exception):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValidationFailure(code)


def validate_documents(candidate: dict[str, Any], binding: dict[str, Any], *, check_files: bool = True) -> list[str]:
    checks: list[str] = []
    require(candidate.get("schema_version") == "cyberalchemy-lab-ontology-product-event-runtime-candidate/v1", "CANDIDATE_SCHEMA_MISMATCH")
    require(candidate.get("candidate_id") == "CAL-ONTOLOGY-AS-PRODUCT-CANDIDATE-0006-EVENT-RUNTIME-REALIZATION", "CANDIDATE_ID_MISMATCH")
    require(candidate.get("status") == "ready-for-product-approval", "CANDIDATE_STATUS_MISMATCH")
    require(candidate.get("construction_stage") == "CAV2-D65-TESTABLE-PRODUCT-FREEZE", "CONSTRUCTION_STAGE_MISMATCH")
    require(candidate.get("authority_effect") == "none", "CANDIDATE_AUTHORITY_INFLATION")
    require(candidate["product_test"] == {
        "required": True,
        "result": "PASS",
        "rust_test_cases": 15,
        "candidate_validator_tests": 5,
        "deterministic_rust_runs": 2,
        "cli_materializations": 2,
        "cli_restart_observations": 1,
        "receipt_path": "product/products/ontology/v1/candidates/0006-event-runtime-realization/receipts/validation.json",
        "product_approval_eligible": True,
        "product_approval_granted": False,
    }, "PRODUCT_TEST_CONTRACT_MISMATCH")
    checks.append("candidate-identity-and-claim-ceiling")

    require(binding.get("schema_version") == "cyberalchemy-lab-ontology-product-event-runtime-binding/v2", "BINDING_SCHEMA_MISMATCH")
    require(binding.get("binding_id") == "cal.binding.ontology-product-event-runtime/v2", "BINDING_ID_MISMATCH")
    require(binding.get("status") == "test-candidate", "BINDING_STATUS_MISMATCH")
    require(binding.get("authority_effect") == "none", "BINDING_AUTHORITY_INFLATION")
    require(binding["runtime_source"]["adopted"] is False, "RUNTIME_ADOPTION_INFLATION")
    require(binding["authority_source"]["preserved_effect"] == "root-admission-only", "ROOT_AUTHORITY_SCOPE_MISMATCH")
    initial = binding["implementation"]["initial_cut"]
    require(initial == {"node_subjects": 14, "relation_subjects": 15, "semantic_events": 29, "governance_events": 29, "integration_epochs": 1, "latest_subject_snapshots": 29}, "INITIAL_CUT_MISMATCH")
    checks.append("binding-semantics-and-authority-boundary")

    material = candidate.get("acceptance_material", [])
    require(len(material) == 19, "ACCEPTANCE_MATERIAL_COUNT_MISMATCH")
    paths = [item.get("path") for item in material]
    require(len(set(paths)) == len(paths), "ACCEPTANCE_MATERIAL_DUPLICATE")
    if check_files:
        for item in material:
            path = REPO / item["path"]
            require(path.is_file(), f"ACCEPTANCE_MATERIAL_MISSING:{item['path']}")
            require(digest(path) == item["sha256"], f"ACCEPTANCE_MATERIAL_DRIFT:{item['path']}")
    require(candidate["product_increment"]["binding_sha256"] == digest(BINDING_PATH), "PRODUCT_BINDING_DIGEST_MISMATCH")
    require(binding["predecessor"]["sha256"] == digest(REPO / binding["predecessor"]["path"]), "FROZEN_PREDECESSOR_DRIFT")
    checks.append("exact-source-and-implementation-digests")

    test_source = (REPO / "implementation/bindings/ontology-product-event-runtime/v2/tests/product_candidate.rs").read_text(encoding="utf-8")
    found = {name for name in RUST_TESTS if f"fn {name}()" in test_source}
    require(found == RUST_TESTS, "RUST_TEST_CONTRACT_INCOMPLETE")
    require("Eleven profile-qualified packages" in NAVIGATION_PATH.read_text(encoding="utf-8"), "DOMAINSPEC_COLLISION_RESIDUE_MISSING")
    checks.append("hostile-test-and-residue-coverage")
    return checks


def run_command(command: list[str], env: dict[str, str]) -> str:
    completed = subprocess.run(command, cwd=REPO, env=env, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise ValidationFailure(f"COMMAND_FAILED:{' '.join(command)}\n{completed.stdout}\n{completed.stderr}")
    return completed.stdout + completed.stderr


def run_product_tests() -> tuple[list[str], dict[str, Any], str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    checks: list[str] = []
    validator_output = run_command(["python3", "-m", "unittest", str(VALIDATOR_TEST_PATH)], env)
    require("Ran 5 tests" in validator_output, "CANDIDATE_VALIDATOR_TEST_COUNT_MISMATCH")
    checks.append("candidate-validator-hostile-tests")
    run_command(["cargo", "fmt", "--manifest-path", str(MANIFEST_PATH), "--", "--check"], env)
    checks.append("rust-format")
    for run_number in (1, 2):
        output = run_command(["cargo", "test", "--manifest-path", str(MANIFEST_PATH)], env)
        require("15 passed; 0 failed" in output, f"RUST_TEST_COUNT_MISMATCH:run-{run_number}")
        checks.append(f"rust-product-tests-run-{run_number}")

    with tempfile.TemporaryDirectory(prefix="cal-event-runtime-product-") as temporary:
        base = Path(temporary)
        observations: list[dict[str, Any]] = []
        tree_digests: list[str] = []
        for name in ("first", "second"):
            target = base / name
            output = run_command([
                "cargo", "run", "--quiet", "--manifest-path", str(MANIFEST_PATH), "--",
                "materialize", str(NAVIGATION_PATH), str(target),
            ], env)
            observation = json.loads(output)
            observations.append(observation)
            files = sorted(path for path in target.rglob("*") if path.is_file())
            require(len(files) == 59, f"RUNTIME_FILE_COUNT_MISMATCH:{name}")
            tree_hash = hashlib.sha256()
            for path in files:
                tree_hash.update(path.relative_to(target).as_posix().encode())
                tree_hash.update(b"\0")
                tree_hash.update(path.read_bytes())
            tree_digests.append(tree_hash.hexdigest())
        require(observations[0] == observations[1], "MATERIALIZATION_OBSERVATION_NONDETERMINISTIC")
        require(tree_digests[0] == tree_digests[1], "MATERIALIZATION_EVENT_TREE_NONDETERMINISTIC")
        restarted = json.loads(run_command([
            "cargo", "run", "--quiet", "--manifest-path", str(MANIFEST_PATH), "--",
            "observe", str(base / "first"),
        ], env))
        require(restarted == observations[0], "RESTART_OBSERVATION_MISMATCH")
        observation = observations[0]
        require(observation["node_count"] == 14 and observation["relation_count"] == 15, "OBSERVATION_GRAPH_COUNT_MISMATCH")
        require(observation["semantic_event_count"] == 29 and observation["governance_event_count"] == 29, "OBSERVATION_EVENT_COUNT_MISMATCH")
        require(observation["latest_snapshot_count"] == 29, "OBSERVATION_SNAPSHOT_COUNT_MISMATCH")
        require(observation["root_admission_preserved"] is True, "ROOT_ADMISSION_NOT_PRESERVED")
        require(observation["child_ontologies_admitted_by_binding"] == 0, "CHILD_ADMISSION_INFLATION")
        require(observation["canonical_replay_source_is_event_history"] is True, "REPLAY_SOURCE_MISMATCH")
        require(observation["authority_effect"] == "none", "OBSERVATION_AUTHORITY_INFLATION")
        checks.extend(["two-byte-equivalent-cli-materializations", "restart-observation-equality", "calculated-read-model-contract"])
        return checks, observation, tree_digests[0]


def receipt(candidate: dict[str, Any], checks: list[str], observation: dict[str, Any], tree_digest: str) -> dict[str, Any]:
    return {
        "schema_version": "cyberalchemy-lab-ontology-product-event-runtime-validation-receipt/v1",
        "candidate_id": candidate["candidate_id"],
        "candidate_path": "product/products/ontology/v1/candidates/0006-event-runtime-realization/candidate.json",
        "candidate_sha256": digest(CANDIDATE_PATH),
        "binding_path": "implementation/bindings/ontology-product-event-runtime/v2/binding.json",
        "binding_sha256": digest(BINDING_PATH),
        "result": "PASS",
        "checks": checks,
        "check_count": len(checks),
        "rust_test_cases": 15,
        "candidate_validator_tests": 5,
        "deterministic_rust_runs": 2,
        "cli_materializations": 2,
        "runtime_event_tree_sha256": tree_digest,
        "observation": observation,
        "product_approval_eligible": True,
        "product_approval_granted": False,
        "authority_effect": "none",
        "claim_ceiling": "PASS proves this exact candidate's package-to-event realization and calculated read-model behavior. It does not grant Product approval, binding admission, runtime adoption or activation, migration, cutover, publication, release, deployment, or any external effect."
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    arguments = parser.parse_args()
    candidate = load_json(CANDIDATE_PATH)
    binding = load_json(BINDING_PATH)
    checks = validate_documents(candidate, binding)
    runtime_checks, observation, tree_digest = run_product_tests()
    result = receipt(candidate, checks + runtime_checks, observation, tree_digest)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.write_receipt:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationFailure as error:
        print(json.dumps({"result": "FAIL", "error": str(error)}, indent=2))
        raise SystemExit(1)

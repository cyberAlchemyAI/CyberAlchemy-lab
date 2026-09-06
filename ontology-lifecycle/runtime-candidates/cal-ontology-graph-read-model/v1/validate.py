#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[3]
RECEIPT = HERE / "receipts/prototype-validation.json"
DEPENDENCIES = {
    "docs/decisions/0041-d65-l5-local-active-runtime-product-approval/decision.json": "5e3401348d5bf17cffa9ac37cc281436bc18c9ee6ea1254bcf87266da51ecc68",
    "ontology-lifecycle/benchmarks/graph-read-model/v1/evidence/adjudication-large.jsonl": "7600b5a24b30ac3c58ac24f837080a668e201c193309ccb73dfe5355cee7c2b0",
    "ontology-lifecycle/benchmarks/graph-read-model/v1/RESULTS.md": "4feaeeaf81d74e71e2df3bfd90406a09cf8c939bd8cbad8eadf1b1ac9b5edbf4",
    "ontology-lifecycle/migration/cal-w7-ontology-product-epoch-001/fixtures/output/projections/ontology-at-cursor.json": "dcf396c8e50c6f9d81daa889d80e84b604be2cfcf3614b5ba0317bdcbc07b6c6",
}
SOURCE_FILES = [
    "Cargo.toml",
    "Cargo.lock",
    "contract.json",
    "plan.md",
    "README.md",
    "recovery-expectation-w7.json",
    "recovery-requirements.json",
    "recovery-requirements.schema.json",
    "src/bin/generate_event_fixture.rs",
    "src/bin/sustained_ingestion.rs",
    "src/lib.rs",
    "src/main.rs",
    "tests/canonical_graph.rs",
    "tests/cli.rs",
    "tests/ingestion.rs",
    "benchmark/EXPERIMENT-PROFILE.md",
    "benchmark/PROTOCOL.md",
    "benchmark/RESULTS.md",
    "benchmark/profiles.json",
    "benchmark/src/main.rs",
    "benchmark/run.py",
    "benchmark/validate.py",
    "benchmark/validation.json",
    "process-recovery/EXPERIMENT-PROFILE.md",
    "process-recovery/RESULTS.md",
    "process-recovery/run.py",
    "process-recovery/validate.py",
    "process-recovery/validation.json",
    "event-file-benchmark/.gitignore",
    "event-file-benchmark/EXPERIMENT-PROFILE.md",
    "event-file-benchmark/PROTOCOL.md",
    "event-file-benchmark/RESULTS.md",
    "event-file-benchmark/profiles.json",
    "event-file-benchmark/run.py",
    "event-file-benchmark/validate.py",
    "event-file-benchmark/validation.json",
    "event-file-parity/.gitignore",
    "event-file-parity/EXPERIMENT-PROFILE.md",
    "event-file-parity/PROTOCOL.md",
    "event-file-parity/RESULTS.md",
    "event-file-parity/profiles.json",
    "event-file-parity/resource-requirements.json",
    "event-file-parity/resource-requirements.schema.json",
    "event-file-parity/run.py",
    "event-file-parity/validate.py",
    "event-file-parity/validation.json",
    "checkpoint-recovery/.gitignore",
    "checkpoint-recovery/EXPERIMENT-PROFILE.md",
    "checkpoint-recovery/PROTOCOL.md",
    "checkpoint-recovery/RESULTS.md",
    "checkpoint-recovery/profiles.json",
    "checkpoint-recovery/resource-requirements.json",
    "checkpoint-recovery/run.py",
    "checkpoint-recovery/validate.py",
    "checkpoint-recovery/validation.json",
    "checkpoint-crash-consistency/.gitignore",
    "checkpoint-crash-consistency/EXPERIMENT-PROFILE.md",
    "checkpoint-crash-consistency/PROTOCOL.md",
    "checkpoint-crash-consistency/RESULTS.md",
    "checkpoint-crash-consistency/requirements.json",
    "checkpoint-crash-consistency/requirements.schema.json",
    "checkpoint-crash-consistency/run.py",
    "checkpoint-crash-consistency/validate.py",
    "checkpoint-crash-consistency/validation.json",
    "sustained-ingestion/.gitignore",
    "sustained-ingestion/EXPERIMENT-PROFILE.md",
    "sustained-ingestion/PROTOCOL.md",
    "sustained-ingestion/RESULTS.md",
    "sustained-ingestion/requirements.json",
    "sustained-ingestion/requirements.schema.json",
    "sustained-ingestion/run.py",
    "sustained-ingestion/validate.py",
    "sustained-ingestion/validation.json",
    "../../../runtime/src/lib.rs",
    "../../../runtime/tests/replay.rs",
    "validate.py",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(arguments: list[str], target: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=HERE,
        env={**os.environ, "CARGO_TARGET_DIR": str(target)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def parse_cli(arguments: list[str], target: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    completed = command(
        ["cargo", "run", "--locked", "--quiet", "--bin", "cal-ontology-graph-read-model", "--", *arguments],
        target,
    )
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError:
        parsed = {}
    return parsed, {
        "arguments": arguments,
        "exit": completed.returncode,
        "stderr": completed.stderr[-1000:] if completed.returncode else "",
    }


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
    recovery_requirements = json.loads(
        (HERE / "recovery-requirements.json").read_text(encoding="utf-8")
    )
    benchmark_profiles = json.loads(
        (HERE / "benchmark/profiles.json").read_text(encoding="utf-8")
    )["profiles"]
    event_file_profiles = json.loads(
        (HERE / "event-file-benchmark/profiles.json").read_text(encoding="utf-8")
    )["profiles"]
    checkpoint_requirements = json.loads(
        (HERE / "checkpoint-recovery/resource-requirements.json").read_text(
            encoding="utf-8"
        )
    )
    crash_consistency_requirements = json.loads(
        (HERE / "checkpoint-crash-consistency/requirements.json").read_text(
            encoding="utf-8"
        )
    )
    sustained_ingestion_requirements = json.loads(
        (HERE / "sustained-ingestion/requirements.json").read_text(encoding="utf-8")
    )
    recovery_requirements_pass = (
        recovery_requirements.get("schema_version")
        == "cal-graph-recovery-requirements/v1-prototype"
        and recovery_requirements.get("recovery_strategy")
        == "full_rebuild_from_verified_calculated_cut"
        and recovery_requirements.get("checkpoint_policy")
        == "disposable_checkpoint_is_eligible_only_as_a_self_digested_source_bound_cache_with_verified_canonical_tail_equivalence"
        and recovery_requirements.get("canonical_replay_source") is False
        and recovery_requirements.get("authority_effect") == "none"
        and all(
            recovery_requirements["cold_recovery_objectives"][profile][
                "maximum_elapsed_ns"
            ]
            == benchmark_profiles[profile]["maximum_cold_recovery_ns"]
            for profile in ("smoke", "medium", "large")
        )
        and all(
            recovery_requirements["generated_event_file_objectives"][profile][
                "node_count"
            ]
            == event_file_profiles[profile]["node_count"]
            and recovery_requirements["generated_event_file_objectives"][profile][
                "subject_count"
            ]
            == event_file_profiles[profile]["node_count"]
            * (event_file_profiles[profile]["relations_per_node"] + 1)
            and recovery_requirements["generated_event_file_objectives"][profile][
                "maximum_process_recovery_ns"
            ]
            == event_file_profiles[profile]["maximum_process_recovery_ns"]
            for profile in ("medium", "large")
        )
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "subject_count"
        )
        == checkpoint_requirements["subject_count"]
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "checkpoint_semantic_cursor"
        )
        == checkpoint_requirements["checkpoint_semantic_cursor"]
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "checkpoint_governance_cursor"
        )
        == checkpoint_requirements["checkpoint_governance_cursor"]
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "semantic_tail_event_count"
        )
        == checkpoint_requirements["semantic_tail_event_count"]
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "governance_tail_event_count"
        )
        == checkpoint_requirements["governance_tail_event_count"]
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "attempt_count_per_strategy"
        )
        == checkpoint_requirements["attempt_count_per_strategy"]
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "require_exact_full_replay_equivalence"
        )
        is True
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "require_checkpoint_median_faster_than_full_replay"
        )
        is False
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "minimum_checkpoint_pair_wins_for_performance_claim"
        )
        == checkpoint_requirements["minimum_checkpoint_pair_wins"]
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "maximum_checkpoint_to_full_median_ratio"
        )
        == checkpoint_requirements["maximum_checkpoint_to_full_median_ratio"]
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "checkpoint_kind"
        )
        == checkpoint_requirements["checkpoint_kind"]
        and recovery_requirements.get("checkpoint_tail_objective", {}).get(
            "checkpoint_is_canonical_replay_source"
        )
        is False
        and recovery_requirements.get(
            "checkpoint_atomic_maintenance_objective", {}
        ).get("dataset")
        == crash_consistency_requirements["dataset"]
        and recovery_requirements.get(
            "checkpoint_atomic_maintenance_objective", {}
        ).get("attempt_count")
        == crash_consistency_requirements["attempt_count"]
        and recovery_requirements.get(
            "checkpoint_atomic_maintenance_objective", {}
        ).get("replacement_strategy")
        == crash_consistency_requirements["required_replacement_strategy"]
        and recovery_requirements.get(
            "checkpoint_atomic_maintenance_objective", {}
        ).get("fault_process_exit")
        == crash_consistency_requirements["fault_process_exit"]
        and recovery_requirements.get(
            "checkpoint_atomic_maintenance_objective", {}
        ).get("power_loss_durability_claim")
        is False
    )
    current_recovery_requirements_digest = digest(HERE / "recovery-requirements.json")
    dependencies = []
    for relative, expected in DEPENDENCIES.items():
        path = LAB / relative
        current = digest(path) if path.is_file() else None
        dependencies.append({
            "path": relative,
            "expected_sha256": expected,
            "current_sha256": current,
            "result": "PASS" if current == expected else "BLOCK",
        })

    with tempfile.TemporaryDirectory(prefix="cal-graph-read-model-") as temporary:
        target = Path(temporary) / "target"
        test_runs = []
        for run_id in (1, 2):
            completed = command(
                ["cargo", "test", "--locked", "--tests", "--", "--test-threads=1"],
                target,
            )
            test_runs.append({
                "run": run_id,
                "exit": completed.returncode,
                "result": "PASS" if completed.returncode == 0 else "BLOCK",
                "stderr_tail": completed.stderr[-3000:] if completed.returncode else "",
            })

        summary, summary_run = parse_cli(["summary"], target)
        outgoing, outgoing_run = parse_cli(
            ["outgoing", "CA2-PRODUCT-ONTOLOGY", "includes_capability"], target
        )
        traversal, traversal_run = parse_cli(
            ["traverse", "CA2-PROJECT-ONTOLOGY-PRODUCT", "develops,includes_capability"], target
        )
        context, context_run = parse_cli(
            ["context", "CA2-PROJECT-ONTOLOGY-PRODUCT"], target
        )
        challenge, challenge_run = parse_cli(
            ["challenge", "CA2-PRODUCT-ONTOLOGY"], target
        )

    probes_pass = (
        all(item["exit"] == 0 for item in [summary_run, outgoing_run, traversal_run, context_run, challenge_run])
        and summary.get("result", {}).get("semantic_cursor") == 47
        and summary.get("result", {}).get("node_count") == 23
        and summary.get("result", {}).get("relation_count") == 24
        and summary.get("canonical_replay_source") is False
        and summary.get("authority_effect") == "none"
        and len(outgoing.get("result", [])) == 5
        and len(traversal.get("result", [])) == 5
        and any(
            subject.get("identity", {}).get("subject_id") == "CA2-GOAL-ONTOLOGY-PRODUCT-FOUNDATION"
            for subject in context.get("result", [])
        )
        and len(challenge.get("result", {}).get("valid_challenge_modes", [])) == 3
    )
    benchmark_completed = subprocess.run(
        ["python3", "benchmark/validate.py"],
        cwd=HERE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        benchmark_receipt = json.loads((HERE / "benchmark/validation.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        benchmark_receipt = {}
    benchmark_pass = (
        benchmark_completed.returncode == 0
        and benchmark_receipt.get("result") == "PASS"
        and [
            item.get("result")
            for item in benchmark_receipt.get("profile_checks", [])
        ]
        == ["PASS", "PASS", "PASS"]
    )
    process_recovery_completed = subprocess.run(
        ["python3", "process-recovery/validate.py"],
        cwd=HERE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        process_recovery_receipt = json.loads(
            (HERE / "process-recovery/validation.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        process_recovery_receipt = {}
    process_recovery_pass = (
        process_recovery_completed.returncode == 0
        and process_recovery_receipt.get("result") == "PASS"
        and process_recovery_receipt.get("selected_sources_current") is True
    )
    event_file_completed = subprocess.run(
        ["python3", "event-file-benchmark/validate.py"],
        cwd=HERE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        event_file_receipt = json.loads(
            (HERE / "event-file-benchmark/validation.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        event_file_receipt = {}
    event_file_pass = (
        event_file_completed.returncode == 0
        and event_file_receipt.get("result") == "PASS"
        and [
            item.get("result") for item in event_file_receipt.get("profile_checks", [])
        ]
        == ["PASS", "PASS"]
    )
    parity_completed = subprocess.run(
        ["python3", "event-file-parity/validate.py"],
        cwd=HERE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        parity_receipt = json.loads(
            (HERE / "event-file-parity/validation.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        parity_receipt = {}
    parity_pass = (
        parity_completed.returncode == 0
        and parity_receipt.get("result") == "PASS"
        and parity_receipt.get("subject_count") == 250000
        and parity_receipt.get("total_event_file_count") == 500000
        and parity_receipt.get("sources_current") is True
        and parity_receipt.get("fixture_resources_valid") is True
        and parity_receipt.get("attempt_resources_valid") is True
    )
    checkpoint_completed = subprocess.run(
        ["python3", "checkpoint-recovery/validate.py"],
        cwd=HERE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        checkpoint_receipt = json.loads(
            (HERE / "checkpoint-recovery/validation.json").read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError):
        checkpoint_receipt = {}
    checkpoint_pass = (
        checkpoint_completed.returncode == 0
        and checkpoint_receipt.get("result") == "PASS"
        and checkpoint_receipt.get("subject_count")
        == checkpoint_requirements["subject_count"]
        and checkpoint_receipt.get("semantic_tail_event_count")
        == checkpoint_requirements["semantic_tail_event_count"]
        and checkpoint_receipt.get("governance_tail_event_count")
        == checkpoint_requirements["governance_tail_event_count"]
        and checkpoint_receipt.get("sources_current") is True
        and checkpoint_receipt.get("exact_outputs") is True
        and checkpoint_receipt.get("controls_valid") is True
        and checkpoint_receipt.get("performance_valid") is True
        and checkpoint_receipt.get("checkpoint_tail_bounded") is True
        and checkpoint_receipt.get("checkpoint_to_full_median_ratio")
        <= checkpoint_requirements["maximum_checkpoint_to_full_median_ratio"]
    )
    crash_consistency_completed = subprocess.run(
        ["python3", "checkpoint-crash-consistency/validate.py"],
        cwd=HERE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        crash_consistency_receipt = json.loads(
            (HERE / "checkpoint-crash-consistency/validation.json").read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError):
        crash_consistency_receipt = {}
    crash_consistency_pass = (
        crash_consistency_completed.returncode == 0
        and crash_consistency_receipt.get("result") == "PASS"
        and crash_consistency_receipt.get("attempt_results") == ["PASS", "PASS"]
        and crash_consistency_receipt.get("sources_current") is True
        and crash_consistency_receipt.get("controls_valid") is True
        and crash_consistency_receipt.get("deterministic_normalized_state") is True
        and crash_consistency_receipt.get("power_loss_durability_claim") is False
    )
    sustained_ingestion_completed = subprocess.run(
        ["python3", "sustained-ingestion/validate.py"],
        cwd=HERE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        sustained_ingestion_receipt = json.loads(
            (HERE / "sustained-ingestion/validation.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        sustained_ingestion_receipt = {}
    sustained_ingestion_pass = (
        sustained_ingestion_completed.returncode == 0
        and sustained_ingestion_receipt.get("result") == "PASS"
        and sustained_ingestion_receipt.get("attempt_results") == ["PASS", "PASS"]
        and sustained_ingestion_receipt.get("sources_current") is True
        and sustained_ingestion_receipt.get("controls_valid") is True
        and sustained_ingestion_receipt.get("deterministic_normalized_receipt") is True
        and sustained_ingestion_receipt.get("batch_count")
        == sustained_ingestion_requirements["batch_count"]
        and sustained_ingestion_receipt.get("queue_capacity")
        == sustained_ingestion_requirements["queue_capacity"]
        and sustained_ingestion_receipt.get("canonical_replay_source") is False
        and sustained_ingestion_receipt.get("authority_effect") == "none"
    )
    contract_pass = (
        contract.get("status") == "prototype-construction"
        and contract.get("canonical_replay_source") is False
        and contract.get("authority_effect") == "none"
        and contract.get("recovery_requirements", {}).get("sha256")
        == current_recovery_requirements_digest
        and contract.get("large_graph_benchmark", {}).get(
            "implementation_digest_sha256"
        )
        == benchmark_receipt.get("implementation_digest_sha256")
        and "GRM-14-PROCESS-RECOVERY-LOADS-AND-VERIFIES-CANONICAL-EVENT-FILES"
        in contract.get("required_invariants", [])
        and "GRM-15-GENERATED-CANONICAL-FORMAT-EVENT-RECOVERY-IS-EXACT-BOUNDED-AND-SOURCE-BINDING"
        in contract.get("required_invariants", [])
        and "GRM-16-EVENT-FILE-PARITY-IS-RESOURCE-BOUNDED-DETERMINISTIC-AND-TRANSITIVELY-SOURCE-BOUND"
        in contract.get("required_invariants", [])
        and "GRM-17-DISPOSABLE-CHECKPOINTS-ARE-SELF-DIGESTED-SOURCE-BOUND-AND-CANONICAL-TAIL-EQUIVALENT"
        in contract.get("required_invariants", [])
        and "GRM-18-CHECKPOINT-REPLACEMENT-IS-MONOTONIC-SINGLE-WRITER-AND-PROCESS-INTERRUPTION-SAFE"
        in contract.get("required_invariants", [])
        and "GRM-19-CALCULATED-BATCH-INGESTION-IS-BOUNDED-OBSERVABLE-DRAINABLE-AND-SNAPSHOT-ATOMIC"
        in contract.get("required_invariants", [])
        and contract.get("generated_event_file_benchmark", {}).get(
            "runtime_digest_sha256"
        )
        == event_file_receipt.get("runtime_digest_sha256")
        and contract.get("generated_event_file_benchmark", {}).get(
            "generator_digest_sha256"
        )
        == event_file_receipt.get("generator_digest_sha256")
        and contract.get("event_file_parity_benchmark", {}).get(
            "runtime_digest_sha256"
        )
        == parity_receipt.get("runtime_digest_sha256")
        and contract.get("event_file_parity_benchmark", {}).get(
            "experiment_digest_sha256"
        )
        == parity_receipt.get("experiment_digest_sha256")
        and contract.get("event_file_parity_benchmark", {}).get(
            "resource_requirements_sha256"
        )
        == parity_receipt.get("resource_requirements_sha256")
        and contract.get("checkpoint_tail_benchmark", {}).get(
            "runtime_digest_sha256"
        )
        == checkpoint_receipt.get("runtime_digest_sha256")
        and contract.get("checkpoint_tail_benchmark", {}).get(
            "experiment_digest_sha256"
        )
        == checkpoint_receipt.get("experiment_digest_sha256")
        and contract.get("checkpoint_tail_benchmark", {}).get(
            "generator_digest_sha256"
        )
        == checkpoint_receipt.get("generator_digest_sha256")
        and contract.get("checkpoint_tail_benchmark", {}).get(
            "resource_requirements_sha256"
        )
        == checkpoint_receipt.get("resource_requirements_sha256")
        and contract.get("checkpoint_tail_benchmark", {}).get(
            "checkpoint_median_speedup_ratio"
        )
        == checkpoint_receipt.get("checkpoint_median_speedup_ratio")
        and contract.get("checkpoint_tail_benchmark", {}).get(
            "checkpoint_to_full_median_ratio"
        )
        == checkpoint_receipt.get("checkpoint_to_full_median_ratio")
        and contract.get("checkpoint_tail_benchmark", {}).get(
            "checkpoint_pair_wins"
        )
        == checkpoint_receipt.get("checkpoint_pair_wins")
        and contract.get("checkpoint_tail_benchmark", {}).get(
            "checkpoint_performance_benefit_supported"
        )
        == checkpoint_receipt.get("checkpoint_performance_benefit_supported")
        and contract.get("checkpoint_crash_consistency", {}).get(
            "implementation_digest_sha256"
        )
        == crash_consistency_receipt.get("implementation_digest_sha256")
        and contract.get("checkpoint_crash_consistency", {}).get(
            "experiment_digest_sha256"
        )
        == crash_consistency_receipt.get("experiment_digest_sha256")
        and contract.get("checkpoint_crash_consistency", {}).get(
            "requirements_sha256"
        )
        == crash_consistency_receipt.get("requirements_sha256")
        and contract.get("checkpoint_crash_consistency", {}).get(
            "power_loss_durability_claim"
        )
        is False
        and contract.get("sustained_ingestion_benchmark", {}).get(
            "implementation_digest_sha256"
        )
        == sustained_ingestion_receipt.get("implementation_digest_sha256")
        and contract.get("sustained_ingestion_benchmark", {}).get(
            "experiment_digest_sha256"
        )
        == sustained_ingestion_receipt.get("experiment_digest_sha256")
        and contract.get("sustained_ingestion_benchmark", {}).get(
            "requirements_sha256"
        )
        == sustained_ingestion_receipt.get("requirements_sha256")
        and contract.get("sustained_ingestion_benchmark", {}).get("final_index_digest")
        == sustained_ingestion_receipt.get("final_index_digest")
        and contract.get("sustained_ingestion_benchmark", {}).get(
            "canonical_replay_source"
        )
        is False
        and contract.get("sustained_ingestion_benchmark", {}).get("authority_effect")
        == "none"
    )
    all_pass = (
        contract_pass
        and recovery_requirements_pass
        and all(item["result"] == "PASS" for item in dependencies)
        and all(item["result"] == "PASS" for item in test_runs)
        and probes_pass
        and benchmark_pass
        and process_recovery_pass
        and event_file_pass
        and parity_pass
        and checkpoint_pass
        and crash_consistency_pass
        and sustained_ingestion_pass
    )
    receipt = {
        "schema_version": "cal-ontology-graph-read-model-validation/v1-prototype",
        "candidate_id": "CAL-ONTOLOGY-GRAPH-READ-MODEL-PROTOTYPE-001",
        "result": "PASS" if all_pass else "BLOCK",
        "claim": "prototype evidence only",
        "canonical_replay_source": False,
        "authority_effect": "none",
        "contract_validation": {
            "result": "PASS" if contract_pass else "BLOCK",
            "recovery_requirements_sha256": current_recovery_requirements_digest,
            "benchmark_implementation_digest_sha256": benchmark_receipt.get(
                "implementation_digest_sha256"
            ),
        },
        "dependencies": dependencies,
        "recovery_requirements": {
            "result": "PASS" if recovery_requirements_pass else "BLOCK",
            "strategy": recovery_requirements.get("recovery_strategy"),
            "checkpoint_policy": recovery_requirements.get("checkpoint_policy"),
        },
        "test_runs": test_runs,
        "cli_probes": {
            "result": "PASS" if probes_pass else "BLOCK",
            "summary": summary_run,
            "outgoing": outgoing_run,
            "traversal": traversal_run,
            "context": context_run,
            "challenge": challenge_run,
            "index_digest": summary.get("result", {}).get("index_digest"),
        },
        "benchmark_validation": {
            "result": "PASS" if benchmark_pass else "BLOCK",
            "exit": benchmark_completed.returncode,
            "implementation_digest_sha256": benchmark_receipt.get("implementation_digest_sha256"),
            "profile_results": [
                item.get("result") for item in benchmark_receipt.get("profile_checks", [])
            ],
            "stderr_tail": benchmark_completed.stderr[-2000:] if benchmark_completed.returncode else "",
        },
        "process_recovery_validation": {
            "result": "PASS" if process_recovery_pass else "BLOCK",
            "exit": process_recovery_completed.returncode,
            "implementation_digest_sha256": process_recovery_receipt.get(
                "implementation_digest_sha256"
            ),
            "selected_sources_current": process_recovery_receipt.get(
                "selected_sources_current"
            ),
            "attempt_results": process_recovery_receipt.get("attempt_results", []),
            "failure_control_results": process_recovery_receipt.get(
                "failure_control_results", {}
            ),
            "stderr_tail": process_recovery_completed.stderr[-2000:]
            if process_recovery_completed.returncode
            else "",
        },
        "generated_event_file_validation": {
            "result": "PASS" if event_file_pass else "BLOCK",
            "exit": event_file_completed.returncode,
            "runtime_digest_sha256": event_file_receipt.get("runtime_digest_sha256"),
            "generator_digest_sha256": event_file_receipt.get(
                "generator_digest_sha256"
            ),
            "profile_results": [
                item.get("result")
                for item in event_file_receipt.get("profile_checks", [])
            ],
            "stderr_tail": event_file_completed.stderr[-2000:]
            if event_file_completed.returncode
            else "",
        },
        "event_file_parity_validation": {
            "result": "PASS" if parity_pass else "BLOCK",
            "exit": parity_completed.returncode,
            "runtime_digest_sha256": parity_receipt.get("runtime_digest_sha256"),
            "experiment_digest_sha256": parity_receipt.get("experiment_digest_sha256"),
            "subject_count": parity_receipt.get("subject_count"),
            "total_event_file_count": parity_receipt.get("total_event_file_count"),
            "generation_peak_rss_kib": parity_receipt.get("generation_peak_rss_kib"),
            "recovery_peak_rss_kib": parity_receipt.get("recovery_peak_rss_kib"),
            "stderr_tail": parity_completed.stderr[-2000:]
            if parity_completed.returncode
            else "",
        },
        "checkpoint_tail_validation": {
            "result": "PASS" if checkpoint_pass else "BLOCK",
            "exit": checkpoint_completed.returncode,
            "runtime_digest_sha256": checkpoint_receipt.get(
                "runtime_digest_sha256"
            ),
            "experiment_digest_sha256": checkpoint_receipt.get(
                "experiment_digest_sha256"
            ),
            "subject_count": checkpoint_receipt.get("subject_count"),
            "semantic_tail_event_count": checkpoint_receipt.get(
                "semantic_tail_event_count"
            ),
            "governance_tail_event_count": checkpoint_receipt.get(
                "governance_tail_event_count"
            ),
            "checkpoint_median_speedup_ratio": checkpoint_receipt.get(
                "checkpoint_median_speedup_ratio"
            ),
            "checkpoint_to_full_median_ratio": checkpoint_receipt.get(
                "checkpoint_to_full_median_ratio"
            ),
            "checkpoint_pair_wins": checkpoint_receipt.get(
                "checkpoint_pair_wins"
            ),
            "checkpoint_performance_benefit_supported": checkpoint_receipt.get(
                "checkpoint_performance_benefit_supported"
            ),
            "stderr_tail": checkpoint_completed.stderr[-2000:]
            if checkpoint_completed.returncode
            else "",
        },
        "checkpoint_crash_consistency_validation": {
            "result": "PASS" if crash_consistency_pass else "BLOCK",
            "exit": crash_consistency_completed.returncode,
            "implementation_digest_sha256": crash_consistency_receipt.get(
                "implementation_digest_sha256"
            ),
            "experiment_digest_sha256": crash_consistency_receipt.get(
                "experiment_digest_sha256"
            ),
            "attempt_results": crash_consistency_receipt.get("attempt_results"),
            "controls_valid": crash_consistency_receipt.get("controls_valid"),
            "deterministic_normalized_state": crash_consistency_receipt.get(
                "deterministic_normalized_state"
            ),
            "power_loss_durability_claim": crash_consistency_receipt.get(
                "power_loss_durability_claim"
            ),
            "stderr_tail": crash_consistency_completed.stderr[-2000:]
            if crash_consistency_completed.returncode
            else "",
        },
        "sustained_ingestion_validation": {
            "result": "PASS" if sustained_ingestion_pass else "BLOCK",
            "exit": sustained_ingestion_completed.returncode,
            "implementation_digest_sha256": sustained_ingestion_receipt.get(
                "implementation_digest_sha256"
            ),
            "experiment_digest_sha256": sustained_ingestion_receipt.get(
                "experiment_digest_sha256"
            ),
            "attempt_results": sustained_ingestion_receipt.get("attempt_results"),
            "batch_count": sustained_ingestion_receipt.get("batch_count"),
            "queue_capacity": sustained_ingestion_receipt.get("queue_capacity"),
            "attempt_ingestion_elapsed_ns": sustained_ingestion_receipt.get(
                "attempt_ingestion_elapsed_ns"
            ),
            "attempt_throughput_batches_per_second": sustained_ingestion_receipt.get(
                "attempt_throughput_batches_per_second"
            ),
            "attempt_maximum_projection_latency_ns": sustained_ingestion_receipt.get(
                "attempt_maximum_projection_latency_ns"
            ),
            "attempt_rejected_overload_count": sustained_ingestion_receipt.get(
                "attempt_rejected_overload_count"
            ),
            "final_index_digest": sustained_ingestion_receipt.get("final_index_digest"),
            "stderr_tail": sustained_ingestion_completed.stderr[-2000:]
            if sustained_ingestion_completed.returncode
            else "",
        },
        "source_manifest": [
            {"path": relative, "sha256": digest(HERE / relative)}
            for relative in SOURCE_FILES
        ],
        "forbidden_claims_preserved": [
            "product approval",
            "ontology admission",
            "runtime activation",
            "production durability",
            "publication",
            "cutover",
        ],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

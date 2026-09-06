#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
RUNS = HERE / "runs"
LOGS = HERE / "raw-logs"
PROFILES = HERE / "profiles.json"
ATTEMPTS = 2
BUILD_SPREAD_LIMIT = 4.0
LATENCY_SPREAD_LIMIT = 5.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def attempt_path(profile: str, attempt: int) -> Path:
    return EVIDENCE / f"{profile}-attempt-{attempt}.jsonl"


def log_path(profile: str, attempt: int) -> Path:
    return LOGS / f"{profile}-attempt-{attempt}.log"


def run_attempt(profile: str, attempt: int, rerun: bool) -> dict[str, Any]:
    output = attempt_path(profile, attempt)
    log = log_path(profile, attempt)
    if output.exists() and not rerun:
        raise RuntimeError(f"{output} exists; pass --rerun to replace exact attempt evidence")
    if output.exists():
        output.unlink()
    command = [
        "cargo",
        "run",
        "--release",
        "--locked",
        "--quiet",
        "--",
        "--profile",
        profile,
        "--profiles",
        str(PROFILES),
        "--attempt",
        str(attempt),
        "--output",
        str(output),
    ]
    completed = subprocess.run(
        command,
        cwd=HERE,
        env={**os.environ, "CARGO_TARGET_DIR": str(HERE / "target")},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    log.write_text(
        "COMMAND=" + json.dumps(command) + "\n"
        + "EXIT=" + str(completed.returncode) + "\n"
        + "STDOUT\n" + completed.stdout
        + "STDERR\n" + completed.stderr,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(f"attempt {attempt} failed; inspect {log}")
    records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    if len(records) != 1:
        raise RuntimeError(f"expected one record in {output}; got {len(records)}")
    validate_attempt(records[0], profile, attempt)
    return records[0]


def load_attempt(profile: str, attempt: int) -> dict[str, Any]:
    path = attempt_path(profile, attempt)
    if not path.is_file():
        raise RuntimeError(f"missing {path}")
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if len(records) != 1:
        raise RuntimeError(f"expected one record in {path}; got {len(records)}")
    validate_attempt(records[0], profile, attempt)
    return records[0]


def validate_attempt(record: dict[str, Any], profile: str, attempt: int) -> None:
    expected = {
        "schema_version": "cal-ontology-graph-benchmark-attempt/v1",
        "benchmark_id": "CAL-ONTOLOGY-GRAPH-READ-MODEL-BENCHMARK-002",
        "profile_id": profile,
        "attempt": attempt,
        "status": "pass",
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": "local_single_process_synthetic_prototype_evidence_only",
    }
    mismatches = {
        key: {"expected": value, "observed": record.get(key)}
        for key, value in expected.items()
        if record.get(key) != value
    }
    correctness = record.get("correctness", {})
    if correctness.get("status") != "pass":
        mismatches["correctness.status"] = correctness.get("status")
    if correctness.get("deterministic_rebuild_digest_match") is not True:
        mismatches["deterministic_rebuild_digest_match"] = correctness.get(
            "deterministic_rebuild_digest_match"
        )
    delta = record.get("calculated_delta", {})
    if delta.get("exact_model_equivalence") is not True:
        mismatches["calculated_delta.exact_model_equivalence"] = delta.get(
            "exact_model_equivalence"
        )
    if delta.get("transaction_strategy") != "bounded_rollback_journal":
        mismatches["calculated_delta.transaction_strategy"] = delta.get(
            "transaction_strategy"
        )
    if delta.get("full_model_clone") is not False:
        mismatches["calculated_delta.full_model_clone"] = delta.get("full_model_clone")
    if delta.get("staged_previous_subject_count", 0) >= record.get(
        "generated_subject_count", 0
    ):
        mismatches["calculated_delta.staged_previous_subject_count"] = delta.get(
            "staged_previous_subject_count"
        )
    if not isinstance(delta.get("total_changes"), int) or delta.get("total_changes", 0) <= 0:
        mismatches["calculated_delta.total_changes"] = delta.get("total_changes")
    concurrent = record.get("concurrent_snapshots", {})
    concurrent_expected = {
        "publication_strategy": "structurally_shared_arc_snapshot",
        "invalid_observations": 0,
        "writer_completed_while_old_snapshot_held": True,
        "old_snapshot_retained_after_publication": True,
        "publication_staged_full_model_clone": False,
        "published_generation": 1,
        "exact_final_model_equivalence": True,
        "readers_are_blocking": False,
    }
    for key, value in concurrent_expected.items():
        if concurrent.get(key) != value:
            mismatches[f"concurrent_snapshots.{key}"] = concurrent.get(key)
    sharing_pairs = (
        ("shared_subject_count", "previous_subject_count"),
        ("shared_challenge_contract_count", "previous_challenge_contract_count"),
        ("shared_index_bucket_count", "previous_index_bucket_count"),
    )
    for shared_key, previous_key in sharing_pairs:
        shared = concurrent.get(shared_key)
        previous = concurrent.get(previous_key)
        if (
            not isinstance(shared, int)
            or not isinstance(previous, int)
            or shared <= 0
            or shared >= previous
        ):
            mismatches[f"concurrent_snapshots.{shared_key}"] = {
                "shared": shared,
                "previous": previous,
            }
    observation_total = (
        concurrent.get("old_generation_observations", 0)
        + concurrent.get("new_generation_observations", 0)
        + concurrent.get("invalid_observations", 0)
    )
    if observation_total != concurrent.get("worker_observations", -2) + 2:
        mismatches["concurrent_snapshots.observation_total"] = observation_total
    recovery = record.get("restart_recovery", {})
    recovery_expected = {
        "recovery_strategy": "full_rebuild_from_verified_calculated_cut",
        "within_objective": True,
        "exact_model_equivalence": True,
        "exact_index_digest_match": True,
        "checkpoint_used": False,
        "corruption_controls_in_test_suite": 4,
    }
    for key, value in recovery_expected.items():
        if recovery.get(key) != value:
            mismatches[f"restart_recovery.{key}"] = recovery.get(key)
    if recovery.get("cold_recovery_ns", 0) > recovery.get("maximum_cold_recovery_ns", -1):
        mismatches["restart_recovery.cold_recovery_ns"] = recovery.get("cold_recovery_ns")
    if recovery.get("maximum_cold_recovery_ns") != record.get("config", {}).get(
        "maximum_cold_recovery_ns"
    ):
        mismatches["restart_recovery.maximum_cold_recovery_ns"] = recovery.get(
            "maximum_cold_recovery_ns"
        )
    if recovery.get("recovered_semantic_cursor") != record.get("generated_subject_count"):
        mismatches["restart_recovery.recovered_semantic_cursor"] = recovery.get(
            "recovered_semantic_cursor"
        )
    if recovery.get("recovered_source_event_count") != record.get("generated_subject_count"):
        mismatches["restart_recovery.recovered_source_event_count"] = recovery.get(
            "recovered_source_event_count"
        )
    if recovery.get("recovered_index_digest_sha256") != record.get(
        "candidate_index_digest_sha256"
    ):
        mismatches["restart_recovery.recovered_index_digest_sha256"] = recovery.get(
            "recovered_index_digest_sha256"
        )
    families = set(record.get("candidate", {}).get("latency_by_query", {}))
    required_families = {
        "subject", "type", "property", "outgoing", "incoming", "two_hop", "context", "challenge"
    }
    if families != required_families:
        mismatches["query_families"] = sorted(families)
    if mismatches:
        raise RuntimeError("attempt validation blocked: " + json.dumps(mismatches, sort_keys=True))


def spread(values: list[float]) -> float:
    minimum = max(min(values), 1.0)
    return max(values) / minimum


def adjudicate(profile: str, attempts: list[dict[str, Any]]) -> dict[str, Any]:
    fixture_digests = {item["fixture_digest_sha256"] for item in attempts}
    result_digests = {
        item["correctness"]["shared_result_digest_sha256"] for item in attempts
    }
    index_digests = {item["candidate_index_digest_sha256"] for item in attempts}
    implementation_digests = {item["implementation_digest_sha256"] for item in attempts}
    delta_projection_digests = {
        item["calculated_delta"]["target_projection_digest_sha256"] for item in attempts
    }
    delta_index_digests = {
        item["calculated_delta"]["resulting_index_digest_sha256"] for item in attempts
    }
    delta_digests = {
        item["calculated_delta"]["delta_digest_sha256"] for item in attempts
    }
    concurrent_index_digests = {
        item["concurrent_snapshots"]["published_index_digest_sha256"]
        for item in attempts
    }
    recovery_index_digests = {
        item["restart_recovery"]["recovered_index_digest_sha256"] for item in attempts
    }
    deterministic = (
        len(fixture_digests)
        == len(result_digests)
        == len(index_digests)
        == len(implementation_digests)
        == len(delta_projection_digests)
        == len(delta_index_digests)
        == len(delta_digests)
        == len(concurrent_index_digests)
        == len(recovery_index_digests)
        == 1
    )
    build_spread = spread([float(item["candidate"]["build_ns"]) for item in attempts])
    delta_apply_spread = spread([
        float(item["calculated_delta"]["incremental_apply_ns"]) for item in attempts
    ])
    concurrent_writer_spread = spread([
        float(item["concurrent_snapshots"]["writer_publication_ns_under_contention"])
        for item in attempts
    ])
    cold_recovery_spread = spread([
        float(item["restart_recovery"]["cold_recovery_ns"]) for item in attempts
    ])
    latency_spread = {}
    for family in attempts[0]["candidate"]["latency_by_query"]:
        latency_spread[family] = spread([
            float(item["candidate"]["latency_by_query"][family]["p50_ns"])
            for item in attempts
        ])
    timing_stable = (
        build_spread <= BUILD_SPREAD_LIMIT
        and delta_apply_spread <= BUILD_SPREAD_LIMIT
        and concurrent_writer_spread <= BUILD_SPREAD_LIMIT
        and cold_recovery_spread <= BUILD_SPREAD_LIMIT
        and all(value <= LATENCY_SPREAD_LIMIT for value in latency_spread.values())
    )
    if not deterministic:
        status = "block"
    elif not timing_stable:
        status = "flag"
    else:
        status = "pass"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return {
        "schema_version": "cal-ontology-graph-benchmark-report/v1",
        "benchmark_id": "CAL-ONTOLOGY-GRAPH-READ-MODEL-BENCHMARK-002",
        "profile_id": profile,
        "run_at_utc": now.isoformat().replace("+00:00", "Z"),
        "status": status,
        "quality_bar_status": "pass" if deterministic else "fail",
        "anti_pattern_hits": [],
        "workflow_gaps": [
            "RSS is not measured",
            "copy-on-write generation staging clones ordered map spines",
            "no multi-writer workload",
            "recovery workload rebuilds from a calculated cut rather than durable canonical event files",
            "no persistent backend",
            "delta batches are synthetic calculated projections rather than durable event ingestion"
        ],
        "attempt_count": len(attempts),
        "correctness": {
            "all_attempts_pass": all(item["correctness"]["status"] == "pass" for item in attempts),
            "fixture_digest_stable": len(fixture_digests) == 1,
            "result_digest_stable": len(result_digests) == 1,
            "index_digest_stable": len(index_digests) == 1,
            "implementation_digest_stable": len(implementation_digests) == 1,
            "delta_projection_digest_stable": len(delta_projection_digests) == 1,
            "delta_index_digest_stable": len(delta_index_digests) == 1,
            "delta_digest_stable": len(delta_digests) == 1,
            "concurrent_published_index_digest_stable": len(concurrent_index_digests) == 1,
            "recovery_index_digest_stable": len(recovery_index_digests) == 1,
            "fixture_digest_sha256": next(iter(fixture_digests)) if len(fixture_digests) == 1 else None,
            "result_digest_sha256": next(iter(result_digests)) if len(result_digests) == 1 else None,
            "index_digest_sha256": next(iter(index_digests)) if len(index_digests) == 1 else None,
            "implementation_digest_sha256": next(iter(implementation_digests)) if len(implementation_digests) == 1 else None,
        },
        "stability": {
            "status": "pass" if timing_stable else "flag",
            "candidate_build_max_over_min": build_spread,
            "calculated_delta_apply_max_over_min": delta_apply_spread,
            "concurrent_writer_max_over_min": concurrent_writer_spread,
            "cold_recovery_max_over_min": cold_recovery_spread,
            "candidate_p50_max_over_min": latency_spread,
            "build_spread_limit": BUILD_SPREAD_LIMIT,
            "latency_spread_limit": LATENCY_SPREAD_LIMIT,
        },
        "attempt_evidence": [
            {
                "path": str(attempt_path(profile, index).relative_to(HERE)),
                "sha256": sha256(attempt_path(profile, index)),
            }
            for index in range(1, ATTEMPTS + 1)
        ],
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "rustc": rust_version(),
        },
        "profile": attempts[0]["config"],
        "representative_metrics": attempts[-1],
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": "local_single_process_synthetic_prototype_evidence_only",
        "forbidden_claims": [
            "production readiness", "RSS or allocator usage", "concurrent correctness beyond the controlled workload",
            "durability", "crash recovery", "product approval", "ontology admission",
            "runtime activation", "publication", "cutover"
        ],
    }


def rust_version() -> str:
    completed = subprocess.run(
        ["rustc", "--version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def write_report(profile: str, report: dict[str, Any]) -> Path:
    stamp = report["run_at_utc"].replace(":", "").replace("-", "")
    timestamped = RUNS / f"{stamp}-{profile}.json"
    body = json.dumps(report, indent=2, sort_keys=True) + "\n"
    timestamped.write_text(body, encoding="utf-8")
    (RUNS / f"latest-{profile}.json").write_text(body, encoding="utf-8")
    return timestamped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["run", "validate", "report"])
    parser.add_argument("profile", choices=["smoke", "medium", "large"])
    parser.add_argument("--rerun", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    try:
        if arguments.mode == "run":
            attempts = [
                run_attempt(arguments.profile, attempt, arguments.rerun)
                for attempt in range(1, ATTEMPTS + 1)
            ]
        else:
            attempts = [
                load_attempt(arguments.profile, attempt)
                for attempt in range(1, ATTEMPTS + 1)
            ]
        report = adjudicate(arguments.profile, attempts)
        report_path = write_report(arguments.profile, report)
        print(json.dumps({
            "mode": arguments.mode,
            "profile": arguments.profile,
            "status": report["status"],
            "report": str(report_path),
            "profile_validation": "pass",
            "observation": "skipped-no-repository-observability-binding",
        }, indent=2))
        return 1 if report["status"] == "block" else 0
    except (OSError, RuntimeError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "block", "error": str(error)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

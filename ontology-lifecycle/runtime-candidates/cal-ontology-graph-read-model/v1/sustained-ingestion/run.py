#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
RUNTIME_SOURCE = CANDIDATE.parents[2] / "runtime/src/lib.rs"
REQUIREMENTS_PATH = HERE / "requirements.json"


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def digest_set(entries: tuple[tuple[str, Path], ...]) -> str:
    hasher = hashlib.sha256()
    for label, path in entries:
        hasher.update(label.encode())
        hasher.update(b"\0")
        hasher.update(path.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def implementation_digest() -> str:
    return digest_set(tuple(
        (relative, CANDIDATE / relative)
        for relative in (
            "Cargo.toml",
            "Cargo.lock",
            "src/lib.rs",
            "src/bin/sustained_ingestion.rs",
        )
    ) + (("../../../runtime/src/lib.rs", RUNTIME_SOURCE),))


def experiment_digest() -> str:
    return digest_set(tuple(
        (relative, HERE / relative)
        for relative in (
            "EXPERIMENT-PROFILE.md",
            "PROTOCOL.md",
            "requirements.json",
            "requirements.schema.json",
            "run.py",
            "validate.py",
        )
    ))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def normalized(attempt: dict[str, Any]) -> dict[str, Any]:
    output = attempt["output"]
    return {
        "result": output["result"],
        "batch_count": output["batch_count"],
        "queue_capacity": output["queue_capacity"],
        "reader_threads": output["reader_threads"],
        "invalid_reader_observations": output["invalid_reader_observations"],
        "accepted_batch_count": output["accepted_batch_count"],
        "projected_batch_count": output["projected_batch_count"],
        "deterministic_initial_overload": output["deterministic_initial_overload"],
        "overload_retry_succeeded": output["overload_retry_succeeded"],
        "pending_bound_observed": output["pending_bound_observed"],
        "final_semantic_cursor": output["final_semantic_cursor"],
        "final_governance_cursor": output["final_governance_cursor"],
        "final_generation": output["final_generation"],
        "final_index_digest": output["final_index_digest"],
        "expected_index_digest": output["expected_index_digest"],
        "exact_final_rebuild_equivalence": output["exact_final_rebuild_equivalence"],
        "old_snapshot_retained": output["old_snapshot_retained"],
        "drained_exactly": output["drained_exactly"],
        "final_semantic_cursor_lag": output["final_semantic_cursor_lag"],
        "final_governance_cursor_lag": output["final_governance_cursor_lag"],
        "canonical_replay_source": output["canonical_replay_source"],
        "authority_effect": output["authority_effect"],
        "claim_ceiling": output["claim_ceiling"],
    }


def attempt_passes(attempt: dict[str, Any], requirements: dict[str, Any]) -> bool:
    output = attempt["output"]
    return (
        attempt["exit"] == 0
        and output.get("result") == "PASS"
        and output.get("batch_count") == requirements["batch_count"]
        and output.get("queue_capacity") == requirements["queue_capacity"]
        and output.get("reader_threads") == requirements["reader_thread_count"]
        and output.get("accepted_batch_count") == requirements["batch_count"]
        and output.get("projected_batch_count") == requirements["batch_count"]
        and output.get("rejected_overload_count", 0) >= 1
        and output.get("deterministic_initial_overload") is True
        and output.get("overload_retry_succeeded") is True
        and output.get("maximum_pending_batch_count", 0)
        <= requirements["queue_capacity"] + requirements["maximum_pending_over_capacity"]
        and output.get("pending_bound_observed") is True
        and output.get("reader_observations", 0) >= requirements["minimum_reader_observations"]
        and output.get("invalid_reader_observations") == 0
        and output.get("exact_final_rebuild_equivalence") is True
        and output.get("final_index_digest") == output.get("expected_index_digest")
        and output.get("old_snapshot_retained") is True
        and output.get("drained_exactly") is True
        and output.get("final_semantic_cursor_lag") == 0
        and output.get("final_governance_cursor_lag") == 0
        and attempt.get("process_elapsed_ns", 0) <= requirements["maximum_process_elapsed_ns"]
        and output.get("ingestion_elapsed_ns", 0) <= requirements["maximum_process_elapsed_ns"]
        and output.get("throughput_batches_per_second", 0)
        >= requirements["minimum_throughput_batches_per_second"]
        and output.get("maximum_projection_latency_ns", 0)
        <= requirements["maximum_projection_latency_ns"]
        and output.get("canonical_replay_source") is False
        and output.get("authority_effect") == "none"
        and output.get("claim_ceiling") == requirements["claim_ceiling"]
    )


def run(rerun: bool) -> dict[str, Any]:
    requirements = read_json(REQUIREMENTS_PATH)
    evidence_paths = [HERE / f"evidence/attempt-{attempt}.json" for attempt in (1, 2)]
    if not rerun and any(path.exists() for path in evidence_paths):
        raise RuntimeError("evidence exists; pass --rerun to replace this run-local epoch")
    target = HERE / "target"
    build = subprocess.run(
        ["cargo", "build", "--locked", "--release", "--bin", "cal-sustained-ingestion-prototype"],
        cwd=CANDIDATE,
        env={**os.environ, "CARGO_TARGET_DIR": str(target)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if build.returncode:
        raise RuntimeError(f"release build failed: {build.stderr[-2000:]}")
    binary = target / "release/cal-sustained-ingestion-prototype"
    current_implementation = implementation_digest()
    current_experiment = experiment_digest()
    attempt_summaries = []
    normalized_digests = []
    for attempt_number, evidence_path in enumerate(evidence_paths, start=1):
        started = time.perf_counter_ns()
        completed = subprocess.run(
            [
                str(binary),
                str(requirements["batch_count"]),
                str(requirements["queue_capacity"]),
                str(requirements["reader_thread_count"]),
            ],
            cwd=CANDIDATE,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=requirements["maximum_process_elapsed_ns"] / 1_000_000_000 + 5,
        )
        process_elapsed_ns = time.perf_counter_ns() - started
        try:
            output = json.loads(completed.stdout)
        except json.JSONDecodeError:
            output = {}
        raw_path = HERE / f"raw/attempt-{attempt_number}.log"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(
            f"EXIT {completed.returncode}\nSTDOUT\n{completed.stdout}STDERR\n{completed.stderr}",
            encoding="utf-8",
        )
        evidence = {
            "schema_version": "cal-sustained-ingestion-attempt/v1-prototype",
            "attempt": attempt_number,
            "result": "PASS" if output and completed.returncode == 0 else "BLOCK",
            "exit": completed.returncode,
            "process_elapsed_ns": process_elapsed_ns,
            "output": output,
            "raw_log_path": raw_path.relative_to(HERE).as_posix(),
            "raw_log_sha256": digest_file(raw_path),
            "implementation_digest_sha256": current_implementation,
            "experiment_digest_sha256": current_experiment,
            "requirements_sha256": digest_file(REQUIREMENTS_PATH),
            "canonical_replay_source": False,
            "authority_effect": "none",
        }
        evidence["quality_bar_pass"] = attempt_passes(evidence, requirements)
        evidence["result"] = "PASS" if evidence["quality_bar_pass"] else "BLOCK"
        write_json(evidence_path, evidence)
        normalized_digest = digest_bytes(
            json.dumps(normalized(evidence), sort_keys=True, separators=(",", ":")).encode()
        )
        normalized_digests.append(normalized_digest)
        attempt_summaries.append({
            "attempt": attempt_number,
            "path": evidence_path.relative_to(HERE).as_posix(),
            "sha256": digest_file(evidence_path),
            "result": evidence["result"],
            "process_elapsed_ns": process_elapsed_ns,
            "ingestion_elapsed_ns": output.get("ingestion_elapsed_ns"),
            "throughput_batches_per_second": output.get("throughput_batches_per_second"),
            "maximum_projection_latency_ns": output.get("maximum_projection_latency_ns"),
            "rejected_overload_count": output.get("rejected_overload_count"),
            "reader_observations": output.get("reader_observations"),
        })
    deterministic = len(set(normalized_digests)) == 1
    passed = all(item["result"] == "PASS" for item in attempt_summaries) and deterministic
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report = {
        "schema_version": "cal-sustained-ingestion-experiment-report/v1-prototype",
        "profile_id": "sustained",
        "run_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": "PASS" if passed else "BLOCK",
        "quality_bar_status": "pass" if passed else "fail",
        "anti_pattern_hits": [],
        "attempt_count": requirements["attempt_count"],
        "attempts": attempt_summaries,
        "deterministic_normalized_receipt": deterministic,
        "normalized_receipt_sha256": normalized_digests[0],
        "implementation_digest_sha256": current_implementation,
        "experiment_digest_sha256": current_experiment,
        "requirements_sha256": digest_file(REQUIREMENTS_PATH),
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": requirements["claim_ceiling"],
        "workflow_gaps": [
            "synthetic calculated batches are not a durable canonical event append workload",
            "only one ingress owner and one projection worker are modeled",
            "sudden power loss, cross-platform durability, and production service levels remain untested",
        ],
    }
    timestamp_path = HERE / f"runs/{timestamp}-sustained.json"
    latest_path = HERE / "runs/latest-sustained.json"
    write_json(timestamp_path, report)
    write_json(latest_path, report)
    print(json.dumps({
        "mode": "run",
        "profile": "sustained",
        "status": report["quality_bar_status"],
        "report": str(timestamp_path),
        "observation": "skipped-no-repository-observability-binding",
    }, indent=2, sort_keys=True))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("run",))
    parser.add_argument("profile", choices=("sustained",))
    parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()
    try:
        report = run(args.rerun)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"result": "BLOCK", "detail": str(error)}, indent=2))
        return 1
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

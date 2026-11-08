#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
RUNTIME_SOURCE = CANDIDATE.parents[2] / "runtime/src/lib.rs"
REQUIREMENTS_PATH = HERE / "requirements.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def read(path: Path) -> dict[str, Any]:
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


def normalized_digest(attempt: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(normalized(attempt), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def attempt_valid(attempt: dict[str, Any], requirements: dict[str, Any]) -> bool:
    output = attempt.get("output", {})
    return (
        attempt.get("result") == "PASS"
        and attempt.get("quality_bar_pass") is True
        and attempt.get("exit") == 0
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


def main() -> int:
    requirements = read(REQUIREMENTS_PATH)
    schema = read(HERE / "requirements.schema.json")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(requirements, schema)
    report_path = HERE / "runs/latest-sustained.json"
    attempt_paths = [HERE / f"evidence/attempt-{attempt}.json" for attempt in (1, 2)]
    report = read(report_path)
    attempts = [read(path) for path in attempt_paths]
    current_implementation = implementation_digest()
    current_experiment = experiment_digest()
    requirements_sha256 = digest(REQUIREMENTS_PATH)
    evidence_bound = (
        report.get("requirements_sha256") == requirements_sha256
        and all(
            report["attempts"][index].get("sha256") == digest(path)
            for index, path in enumerate(attempt_paths)
        )
        and all(item.get("requirements_sha256") == requirements_sha256 for item in attempts)
    )
    sources_current = (
        report.get("implementation_digest_sha256") == current_implementation
        and report.get("experiment_digest_sha256") == current_experiment
        and all(
            item.get("implementation_digest_sha256") == current_implementation
            and item.get("experiment_digest_sha256") == current_experiment
            for item in attempts
        )
    )
    normalized_digests = [normalized_digest(item) for item in attempts]
    deterministic = (
        report.get("deterministic_normalized_receipt") is True
        and len(set(normalized_digests)) == 1
        and report.get("normalized_receipt_sha256") == normalized_digests[0]
    )
    controls_valid = all(attempt_valid(item, requirements) for item in attempts)
    passed = (
        report.get("result") == "PASS"
        and report.get("quality_bar_status") == "pass"
        and report.get("attempt_count") == requirements["attempt_count"]
        and all(item.get("result") == "PASS" for item in attempts)
        and evidence_bound
        and sources_current
        and deterministic
        and controls_valid
        and report.get("canonical_replay_source") is False
        and report.get("authority_effect") == "none"
    )
    receipt = {
        "schema_version": "cal-sustained-ingestion-validation/v1-prototype",
        "result": "PASS" if passed else "BLOCK",
        "profile_validation": "pass" if passed else "fail",
        "attempt_results": [item.get("result") for item in attempts],
        "evidence_bound": evidence_bound,
        "sources_current": sources_current,
        "deterministic_normalized_receipt": deterministic,
        "controls_valid": controls_valid,
        "implementation_digest_sha256": current_implementation,
        "experiment_digest_sha256": current_experiment,
        "requirements_sha256": requirements_sha256,
        "attempt_evidence_sha256": [digest(path) for path in attempt_paths],
        "latest_report_sha256": digest(report_path),
        "batch_count": requirements["batch_count"],
        "queue_capacity": requirements["queue_capacity"],
        "reader_thread_count": requirements["reader_thread_count"],
        "attempt_ingestion_elapsed_ns": [
            item.get("output", {}).get("ingestion_elapsed_ns") for item in attempts
        ],
        "attempt_process_elapsed_ns": [item.get("process_elapsed_ns") for item in attempts],
        "attempt_throughput_batches_per_second": [
            item.get("output", {}).get("throughput_batches_per_second") for item in attempts
        ],
        "attempt_maximum_projection_latency_ns": [
            item.get("output", {}).get("maximum_projection_latency_ns") for item in attempts
        ],
        "attempt_rejected_overload_count": [
            item.get("output", {}).get("rejected_overload_count") for item in attempts
        ],
        "attempt_reader_observations": [
            item.get("output", {}).get("reader_observations") for item in attempts
        ],
        "final_index_digest": attempts[0].get("output", {}).get("final_index_digest"),
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": requirements["claim_ceiling"],
    }
    (HERE / "validation.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

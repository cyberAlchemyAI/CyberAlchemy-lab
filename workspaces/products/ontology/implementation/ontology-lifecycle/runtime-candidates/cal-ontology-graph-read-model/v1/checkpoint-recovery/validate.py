#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
REQUIREMENTS_PATH = HERE / "resource-requirements.json"
PROFILES_PATH = HERE / "profiles.json"
RUNTIME_SOURCE = CANDIDATE.parents[2] / "runtime/src/lib.rs"


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


def runtime_digest() -> str:
    return digest_set(tuple(
        (relative, CANDIDATE / relative)
        for relative in ("Cargo.toml", "Cargo.lock", "src/lib.rs", "src/main.rs")
    ) + (("../../../runtime/src/lib.rs", RUNTIME_SOURCE),))


def generator_digest() -> str:
    return digest_set((
        ("Cargo.toml", CANDIDATE / "Cargo.toml"),
        ("Cargo.lock", CANDIDATE / "Cargo.lock"),
        ("src/lib.rs", CANDIDATE / "src/lib.rs"),
        ("src/bin/generate_event_fixture.rs", CANDIDATE / "src/bin/generate_event_fixture.rs"),
        ("../../../runtime/src/lib.rs", RUNTIME_SOURCE),
        ("checkpoint-recovery/profiles.json", PROFILES_PATH),
    ))


def experiment_digest() -> str:
    return digest_set(tuple(
        (relative, HERE / relative)
        for relative in (
            "EXPERIMENT-PROFILE.md", "PROTOCOL.md", "profiles.json",
            "resource-requirements.json", "run.py", "validate.py",
        )
    ))


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def main() -> int:
    requirements = read(REQUIREMENTS_PATH)
    fixture_path = HERE / "evidence/checkpoint-fixture.json"
    report_path = HERE / "runs/latest-large.json"
    attempt_ids = tuple(range(1, requirements["attempt_count_per_strategy"] + 1))
    evidence_paths = {
        strategy: [HERE / f"evidence/{strategy}-attempt-{attempt}.json" for attempt in attempt_ids]
        for strategy in ("full-replay", "checkpoint-tail")
    }
    fixture = read(fixture_path)
    report = read(report_path)
    attempts = {
        strategy: [read(path) for path in paths]
        for strategy, paths in evidence_paths.items()
    }
    current_runtime = runtime_digest()
    current_generator = generator_digest()
    current_experiment = experiment_digest()
    report_attempts = report.get("attempts", {})
    evidence_bound = (
        report.get("fixture", {}).get("sha256") == digest(fixture_path)
        and all(
            report_attempts[strategy][index]["sha256"] == digest(path)
            for strategy, paths in evidence_paths.items()
            for index, path in enumerate(paths)
        )
        and all(
            item.get("fixture_receipt_sha256") == digest(fixture_path)
            for records in attempts.values()
            for item in records
        )
    )
    sources_current = (
        report.get("runtime_digest_sha256") == current_runtime
        and report.get("generator_digest_sha256") == current_generator
        and report.get("experiment_digest_sha256") == current_experiment
        and fixture.get("runtime_digest_sha256") == current_runtime
        and fixture.get("generator_digest_sha256") == current_generator
        and fixture.get("experiment_digest_sha256") == current_experiment
        and all(
            item.get("runtime_digest_sha256") == current_runtime
            and item.get("generator_digest_sha256") == current_generator
            and item.get("experiment_digest_sha256") == current_experiment
            for records in attempts.values()
            for item in records
        )
    )
    exact_outputs = all(
        item.get("result") == "PASS"
        and item.get("canonical_replay_source") is False
        and item.get("authority_effect") == "none"
        and item.get("recovery_result", {}).get("semantic_cursor") == requirements["subject_count"]
        and item.get("recovery_result", {}).get("source_event_count") == requirements["subject_count"]
        and item.get("recovery_result", {}).get("source_event_set_digest")
        == fixture.get("expectation", {}).get("source_event_set_digest")
        and item.get("recovery_result", {}).get("rebuilt_index_digest")
        == fixture.get("expectation", {}).get("expected_index_digest")
        for records in attempts.values()
        for item in records
    )
    checkpoint_tail_bounded = all(
        item.get("recovery_result", {}).get("checkpoint_used") is True
        and item.get("recovery_result", {}).get("loaded_semantic_tail_event_count")
        == requirements["semantic_tail_event_count"]
        and item.get("recovery_result", {}).get("loaded_governance_tail_event_count")
        == requirements["governance_tail_event_count"]
        for item in attempts["checkpoint-tail"]
    )
    resources_valid = (
        fixture.get("preflight", {}).get("result") == "PASS"
        and fixture.get("allocated_fixture_bytes", 0) <= requirements["maximum_allocated_fixture_bytes"]
        and fixture.get("logical_event_bytes", 0) <= requirements["maximum_logical_event_bytes"]
        and fixture.get("checkpoint_creation", {}).get("checkpoint_bytes", 0)
        <= requirements["maximum_checkpoint_bytes"]
        and fixture.get("checkpoint_creation", {}).get("checkpoint_allocated_bytes", 0)
        <= requirements["maximum_checkpoint_allocated_bytes"]
        and fixture.get("checkpoint_creation", {}).get("result") == "PASS"
        and all(
            item.get("process_elapsed_ns", 0) <= requirements["maximum_process_recovery_ns"]
            and item.get("resource_measurement", {}).get("timed_out") is False
            and item.get("resource_measurement", {}).get("maximum_rss_kib", 0)
            <= requirements["maximum_recovery_peak_rss_kib"]
            for records in attempts.values()
            for item in records
        )
    )
    determinism_valid = all(report.get("deterministic_normalized_receipt", {}).values())
    controls_valid = (
        set(report.get("controls", {}))
        == {"noncanonical-checkpoint", "stale-checkpoint-body-digest", "noncanonical-tail-event"}
        and all(item.get("result") == "PASS" for item in report["controls"].values())
    )
    performance_valid = (
        report.get("checkpoint_performance_within_bound") is True
        and report.get("checkpoint_to_full_median_ratio", 0) > 0
        and report.get("checkpoint_to_full_median_ratio", 0)
        <= requirements["maximum_checkpoint_to_full_median_ratio"]
        and isinstance(report.get("checkpoint_pair_wins"), int)
        and 0 <= report.get("checkpoint_pair_wins", -1)
        <= requirements["attempt_count_per_strategy"]
        and report.get("minimum_checkpoint_pair_wins")
        == requirements["minimum_checkpoint_pair_wins"]
        and report.get("maximum_checkpoint_to_full_median_ratio")
        == requirements["maximum_checkpoint_to_full_median_ratio"]
    )
    passed = (
        report.get("result") == "PASS"
        and fixture.get("result") == "PASS"
        and evidence_bound
        and sources_current
        and exact_outputs
        and checkpoint_tail_bounded
        and resources_valid
        and determinism_valid
        and controls_valid
        and performance_valid
        and report.get("temporary_fixture_removed") is True
        and report.get("temporary_checkpoint_removed") is True
        and report.get("canonical_replay_source") is False
        and report.get("authority_effect") == "none"
    )
    receipt = {
        "schema_version": "cal-checkpoint-tail-recovery-validation/v1-prototype",
        "result": "PASS" if passed else "BLOCK",
        "evidence_bound": evidence_bound,
        "sources_current": sources_current,
        "exact_outputs": exact_outputs,
        "checkpoint_tail_bounded": checkpoint_tail_bounded,
        "resources_valid": resources_valid,
        "determinism_valid": determinism_valid,
        "controls_valid": controls_valid,
        "performance_valid": performance_valid,
        "subject_count": requirements["subject_count"],
        "semantic_tail_event_count": requirements["semantic_tail_event_count"],
        "governance_tail_event_count": requirements["governance_tail_event_count"],
        "median_process_elapsed_ns": report.get("median_process_elapsed_ns"),
        "checkpoint_median_speedup_ratio": report.get("checkpoint_median_speedup_ratio"),
        "checkpoint_to_full_median_ratio": report.get("checkpoint_to_full_median_ratio"),
        "checkpoint_performance_benefit_supported": report.get(
            "checkpoint_performance_benefit_supported"
        ),
        "checkpoint_pair_wins": report.get("checkpoint_pair_wins"),
        "runtime_digest_sha256": current_runtime,
        "generator_digest_sha256": current_generator,
        "experiment_digest_sha256": current_experiment,
        "resource_requirements_sha256": digest(REQUIREMENTS_PATH),
        "fixture_receipt_sha256": digest(fixture_path),
        "latest_report_sha256": digest(report_path),
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": "local_synthetic_50000_subject_disposable_checkpoint_evidence_only",
    }
    (HERE / "validation.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
PROFILES_PATH = HERE / "profiles.json"
RESOURCE_REQUIREMENTS_PATH = HERE / "resource-requirements.json"
RESOURCE_SCHEMA_PATH = HERE / "resource-requirements.schema.json"
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
        ("event-file-parity/profiles.json", PROFILES_PATH),
    ))


def experiment_digest() -> str:
    return digest_set((
        ("EXPERIMENT-PROFILE.md", HERE / "EXPERIMENT-PROFILE.md"),
        ("PROTOCOL.md", HERE / "PROTOCOL.md"),
        ("profiles.json", PROFILES_PATH),
        ("resource-requirements.json", RESOURCE_REQUIREMENTS_PATH),
        ("resource-requirements.schema.json", RESOURCE_SCHEMA_PATH),
        ("run.py", HERE / "run.py"),
        ("validate.py", HERE / "validate.py"),
    ))


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def main() -> int:
    requirements = read(RESOURCE_REQUIREMENTS_PATH)
    profile = read(PROFILES_PATH)["profiles"]["parity"]
    fixture_path = HERE / "evidence/parity-fixture.json"
    attempt_paths = [HERE / f"evidence/parity-attempt-{attempt}.json" for attempt in (1, 2)]
    report_path = HERE / "runs/latest-parity.json"
    fixture = read(fixture_path)
    attempts = [read(path) for path in attempt_paths]
    report = read(report_path)
    current_runtime = runtime_digest()
    current_generator = generator_digest()
    current_experiment = experiment_digest()

    evidence_bound = (
        report.get("fixture", {}).get("sha256") == digest(fixture_path)
        and all(
            report["attempts"][index - 1]["sha256"] == digest(attempt_paths[index - 1])
            for index in (1, 2)
        )
        and all(item.get("fixture_receipt_sha256") == digest(fixture_path) for item in attempts)
    )
    sources_current = (
        report.get("runtime_digest_sha256") == current_runtime
        and report.get("generator_digest_sha256") == current_generator
        and report.get("experiment_digest_sha256") == current_experiment
        and fixture.get("runtime_digest_sha256") == current_runtime
        and fixture.get("generator_digest_sha256") == current_generator
        and fixture.get("experiment_digest_sha256") == current_experiment
        and all(item.get("runtime_digest_sha256") == current_runtime for item in attempts)
        and all(item.get("generator_digest_sha256") == current_generator for item in attempts)
        and all(item.get("experiment_digest_sha256") == current_experiment for item in attempts)
    )
    preflight = fixture.get("preflight", {})
    preflight_valid = (
        preflight.get("result") == "PASS"
        and preflight.get("available_memory_bytes", 0) >= requirements["minimum_available_memory_bytes"]
        and preflight.get("available_filesystem_bytes", 0) >= requirements["minimum_available_filesystem_bytes"]
        and preflight.get("available_filesystem_inodes", 0) >= requirements["minimum_available_filesystem_inodes"]
        and preflight.get("gnu_time_available") is True
    )
    fixture_resources_valid = (
        fixture.get("logical_event_bytes", 0) <= requirements["maximum_logical_event_bytes"]
        and fixture.get("allocated_fixture_bytes", 0) <= requirements["maximum_allocated_fixture_bytes"]
        and fixture.get("generation_process_ns", 0) <= requirements["maximum_generation_ns"]
        and fixture.get("generation_resource_measurement", {}).get("timed_out") is False
        and fixture.get("generation_resource_measurement", {}).get("maximum_rss_kib", 0)
        <= requirements["maximum_generation_peak_rss_kib"]
        and fixture.get("hard_virtual_memory_bytes") == requirements["hard_virtual_memory_bytes"]
    )
    attempt_resources_valid = all(
        isinstance(item.get("event_store_load_ns"), int)
        and item["event_store_load_ns"] > 0
        and isinstance(item.get("graph_rebuild_ns"), int)
        and item["graph_rebuild_ns"] > 0
        and item["event_store_load_ns"] + item["graph_rebuild_ns"] <= item["process_elapsed_ns"]
        and item["process_elapsed_ns"] <= requirements["maximum_process_recovery_ns"]
        and item.get("resource_measurement", {}).get("timed_out") is False
        and item.get("resource_measurement", {}).get("maximum_rss_kib", 0)
        <= requirements["maximum_recovery_peak_rss_kib"]
        and item.get("hard_virtual_memory_bytes") == requirements["hard_virtual_memory_bytes"]
        for item in attempts
    )
    deterministic = (
        report.get("deterministic_recovery_receipt") is True
        and len({item.get("normalized_recovery_digest_sha256") for item in attempts}) == 1
    )
    dimensions_valid = (
        profile["node_count"] == requirements["node_count"]
        and profile["node_count"] * profile["relations_per_node"] == requirements["relation_count"]
        and profile["node_count"] * (profile["relations_per_node"] + 1)
        == requirements["subject_count"]
        and profile["maximum_process_recovery_ns"]
        == requirements["maximum_process_recovery_ns"]
        and fixture.get("generated_node_count") == requirements["node_count"]
        and fixture.get("generated_relation_count") == requirements["relation_count"]
        and fixture.get("generated_subject_count") == requirements["subject_count"]
        and fixture.get("actual_semantic_event_file_count")
        == requirements["semantic_event_file_count"]
        and fixture.get("actual_governance_event_file_count")
        == requirements["governance_event_file_count"]
    )
    passed = (
        report.get("result") == "PASS"
        and report.get("quality_bar_status") == "pass"
        and report.get("attempt_count") == requirements["attempt_count"] == 2
        and report.get("fixture", {}).get("removed_after_measurement") is True
        and report.get("canonical_replay_source") is False
        and report.get("authority_effect") == "none"
        and report.get("tampered_canonical_json_control", {}).get("result") == "PASS"
        and report.get("tampered_canonical_json_control", {}).get("code") == "NON_CANONICAL_JSON"
        and fixture.get("result") == "PASS"
        and fixture.get("fixture_kind") == requirements["fixture_kind"]
        and fixture.get("canonical_replay_source") is False
        and fixture.get("authority_effect") == "none"
        and all(item.get("result") == "PASS" for item in attempts)
        and evidence_bound
        and sources_current
        and preflight_valid
        and fixture_resources_valid
        and attempt_resources_valid
        and deterministic
        and dimensions_valid
    )
    receipt = {
        "schema_version": "cal-event-file-parity-validation/v1-prototype",
        "result": "PASS" if passed else "BLOCK",
        "profile_validation": "pass" if passed else "block",
        "runtime_digest_sha256": current_runtime,
        "generator_digest_sha256": current_generator,
        "experiment_digest_sha256": current_experiment,
        "resource_requirements_sha256": digest(RESOURCE_REQUIREMENTS_PATH),
        "evidence_bound": evidence_bound,
        "sources_current": sources_current,
        "preflight_valid": preflight_valid,
        "fixture_resources_valid": fixture_resources_valid,
        "attempt_resources_valid": attempt_resources_valid,
        "dimensions_valid": dimensions_valid,
        "deterministic_recovery_receipt": deterministic,
        "subject_count": requirements["subject_count"],
        "total_event_file_count": requirements["semantic_event_file_count"]
        + requirements["governance_event_file_count"],
        "generation_peak_rss_kib": fixture.get("generation_resource_measurement", {}).get("maximum_rss_kib"),
        "recovery_peak_rss_kib": [
            item.get("resource_measurement", {}).get("maximum_rss_kib") for item in attempts
        ],
        "fixture_receipt_sha256": digest(fixture_path),
        "attempt_evidence_sha256": [digest(path) for path in attempt_paths],
        "latest_report_sha256": digest(report_path),
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": "local_synthetic_250000_subject_event_file_parity_evidence_only",
    }
    write_path = HERE / "validation.json"
    write_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

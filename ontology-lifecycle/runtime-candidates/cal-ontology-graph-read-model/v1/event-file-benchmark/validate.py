#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
PROFILES = ("medium", "large")
EXPECTED = {
    "medium": {"nodes": 1000, "relations": 4000, "subjects": 5000},
    "large": {"nodes": 10000, "relations": 40000, "subjects": 50000},
}
PROFILES_PATH = HERE / "profiles.json"
REQUIREMENTS = CANDIDATE / "recovery-requirements.json"
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
        ("event-file-benchmark/profiles.json", PROFILES_PATH),
    ))


def experiment_digest() -> str:
    return digest_set((
        ("EXPERIMENT-PROFILE.md", HERE / "EXPERIMENT-PROFILE.md"),
        ("PROTOCOL.md", HERE / "PROTOCOL.md"),
        ("profiles.json", PROFILES_PATH),
        ("run.py", HERE / "run.py"),
        ("../recovery-requirements.json", REQUIREMENTS),
    ))


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def main() -> int:
    profile_config = read(PROFILES_PATH)
    requirements = read(REQUIREMENTS)["generated_event_file_objectives"]
    current_runtime = runtime_digest()
    current_generator = generator_digest()
    current_experiment = experiment_digest()
    profile_checks = []
    for profile in PROFILES:
        expected = EXPECTED[profile]
        config = profile_config["profiles"][profile]
        fixture_path = HERE / f"evidence/{profile}-fixture.json"
        attempt_paths = [
            HERE / f"evidence/{profile}-attempt-{attempt}.json" for attempt in (1, 2)
        ]
        report_path = HERE / f"runs/latest-{profile}.json"
        fixture = read(fixture_path)
        attempts = [read(path) for path in attempt_paths]
        report = read(report_path)
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
        deterministic = (
            report.get("deterministic_recovery_receipt") is True
            and len({item.get("normalized_recovery_digest_sha256") for item in attempts}) == 1
        )
        objective = requirements[profile]
        objective_matches = (
            objective["node_count"] == expected["nodes"]
            and objective["relation_count"] == expected["relations"]
            and objective["subject_count"] == expected["subjects"]
            and objective["semantic_event_file_count"] == expected["subjects"]
            and objective["governance_event_file_count"] == expected["subjects"]
            and objective["maximum_process_recovery_ns"]
            == config["maximum_process_recovery_ns"]
        )
        timings_valid = all(
            isinstance(item.get("event_store_load_ns"), int)
            and item["event_store_load_ns"] > 0
            and isinstance(item.get("graph_rebuild_ns"), int)
            and item["graph_rebuild_ns"] > 0
            and item["event_store_load_ns"] + item["graph_rebuild_ns"]
            <= item["process_elapsed_ns"]
            and item["process_elapsed_ns"] <= item["maximum_process_recovery_ns"]
            for item in attempts
        )
        passed = (
            report.get("result") == "PASS"
            and report.get("quality_bar_status") == "pass"
            and report.get("attempt_count") == 2
            and report.get("canonical_replay_source") is False
            and report.get("authority_effect") == "none"
            and report.get("tampered_canonical_json_control", {}).get("result") == "PASS"
            and report.get("tampered_canonical_json_control", {}).get("code")
            == "NON_CANONICAL_JSON"
            and fixture.get("result") == "PASS"
            and fixture.get("fixture_kind") == "synthetic-canonical-format-event-files"
            and fixture.get("generated_node_count") == expected["nodes"]
            and fixture.get("generated_relation_count") == expected["relations"]
            and fixture.get("generated_subject_count") == expected["subjects"]
            and fixture.get("semantic_event_file_count") == expected["subjects"]
            and fixture.get("governance_event_file_count") == expected["subjects"]
            and all(item.get("result") == "PASS" for item in attempts)
            and evidence_bound
            and sources_current
            and deterministic
            and objective_matches
            and timings_valid
        )
        profile_checks.append({
            "profile": profile,
            "result": "PASS" if passed else "BLOCK",
            "subject_count": expected["subjects"],
            "attempt_count": len(attempts),
            "evidence_bound": evidence_bound,
            "sources_current": sources_current,
            "deterministic_recovery_receipt": deterministic,
            "timings_valid": timings_valid,
            "latest_report_sha256": digest(report_path),
            "fixture_receipt_sha256": digest(fixture_path),
            "attempt_evidence_sha256": [digest(path) for path in attempt_paths],
        })

    passed = all(item["result"] == "PASS" for item in profile_checks)
    receipt = {
        "schema_version": "cal-generated-event-file-recovery-validation/v1-prototype",
        "result": "PASS" if passed else "BLOCK",
        "profile_validation": "pass" if passed else "block",
        "runtime_digest_sha256": current_runtime,
        "generator_digest_sha256": current_generator,
        "experiment_digest_sha256": current_experiment,
        "profile_checks": profile_checks,
        "authority_effect": "none",
        "claim_ceiling": "declared_local_synthetic_canonical_format_event_file_profiles_only",
    }
    (HERE / "validation.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

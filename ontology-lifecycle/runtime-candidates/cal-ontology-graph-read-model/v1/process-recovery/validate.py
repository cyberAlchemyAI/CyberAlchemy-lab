#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
ONTOLOGY_LIFECYCLE = CANDIDATE.parents[2]
FIXTURE = ONTOLOGY_LIFECYCLE / "migration/cal-w7-ontology-product-epoch-001/fixtures/output"
SEMANTIC = FIXTURE / "semantic-events"
GOVERNANCE = FIXTURE / "governance-events"
REQUIREMENTS = CANDIDATE / "recovery-requirements.json"
RUNTIME_SOURCE = ONTOLOGY_LIFECYCLE / "runtime/src/lib.rs"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_tree(path: Path) -> str:
    hasher = hashlib.sha256()
    for item in sorted(candidate for candidate in path.iterdir() if candidate.is_file()):
        hasher.update(item.name.encode())
        hasher.update(b"\0")
        hasher.update(item.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def runtime_digest() -> str:
    hasher = hashlib.sha256()
    for relative in (
        "Cargo.toml",
        "Cargo.lock",
        "src/lib.rs",
        "src/main.rs",
        "recovery-expectation-w7.json",
    ):
        hasher.update(relative.encode())
        hasher.update(b"\0")
        hasher.update((CANDIDATE / relative).read_bytes())
        hasher.update(b"\0")
    hasher.update(b"../../../runtime/src/lib.rs\0")
    hasher.update(RUNTIME_SOURCE.read_bytes())
    hasher.update(b"\0")
    return hasher.hexdigest()


def experiment_digest() -> str:
    hasher = hashlib.sha256()
    for path, label in (
        (HERE / "EXPERIMENT-PROFILE.md", "EXPERIMENT-PROFILE.md"),
        (HERE / "run.py", "run.py"),
        (REQUIREMENTS, "../recovery-requirements.json"),
    ):
        hasher.update(label.encode())
        hasher.update(b"\0")
        hasher.update(path.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def main() -> int:
    report = json.loads((HERE / "runs/latest-w7-event-files.json").read_text(encoding="utf-8"))
    attempts = [
        json.loads((HERE / f"evidence/w7-event-files-attempt-{attempt}.json").read_text(encoding="utf-8"))
        for attempt in (1, 2)
    ]
    evidence_bound = all(
        report["attempts"][index - 1]["sha256"]
        == digest(HERE / f"evidence/w7-event-files-attempt-{index}.json")
        for index in (1, 2)
    )
    current_implementation = runtime_digest()
    current_experiment = experiment_digest()
    semantic_digest = digest_tree(SEMANTIC)
    governance_digest = digest_tree(GOVERNANCE)
    selected_sources_current = (
        report.get("implementation_digest_sha256") == current_implementation
        and report.get("experiment_digest_sha256") == current_experiment
        and report.get("semantic_event_directory_digest_sha256") == semantic_digest
        and report.get("governance_event_directory_digest_sha256")
        == governance_digest
        and all(
            item.get("implementation_digest_sha256") == current_implementation
            and item.get("experiment_digest_sha256") == current_experiment
            and item.get("semantic_event_directory_digest_sha256") == semantic_digest
            and item.get("governance_event_directory_digest_sha256")
            == governance_digest
            for item in attempts
        )
    )
    passed = (
        report.get("result") == "PASS"
        and report.get("attempt_count") == 2
        and report.get("deterministic_output") is True
        and report.get("canonical_replay_source") is False
        and report.get("authority_effect") == "none"
        and evidence_bound
        and selected_sources_current
        and all(item.get("result") == "PASS" for item in attempts)
        and all(
            isinstance(item.get("event_store_load_ns"), int)
            and item["event_store_load_ns"] > 0
            and isinstance(item.get("graph_rebuild_ns"), int)
            and item["graph_rebuild_ns"] > 0
            and item["event_store_load_ns"] + item["graph_rebuild_ns"]
            <= item["elapsed_ns"]
            for item in attempts
        )
        and all(
            item["elapsed_ns"] <= item["maximum_elapsed_ns"] for item in attempts
        )
        and all(
            control.get("result") == "PASS"
            for control in report.get("failure_controls", {}).values()
        )
    )
    receipt = {
        "schema_version": "cal-event-file-process-recovery-validation/v1-prototype",
        "result": "PASS" if passed else "BLOCK",
        "profile_validation": "pass" if passed else "block",
        "implementation_digest_sha256": report.get("implementation_digest_sha256"),
        "experiment_digest_sha256": report.get("experiment_digest_sha256"),
        "evidence_bound": evidence_bound,
        "latest_report_sha256": digest(HERE / "runs/latest-w7-event-files.json"),
        "attempt_evidence_sha256": [
            digest(HERE / f"evidence/w7-event-files-attempt-{index}.json")
            for index in (1, 2)
        ],
        "selected_sources_current": selected_sources_current,
        "semantic_event_directory_digest_sha256": semantic_digest,
        "governance_event_directory_digest_sha256": governance_digest,
        "attempt_results": [item.get("result") for item in attempts],
        "failure_control_results": {
            key: value.get("result")
            for key, value in report.get("failure_controls", {}).items()
        },
        "authority_effect": "none",
    }
    (HERE / "validation.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
LAB = CANDIDATE.parents[3]
RUNTIME_SOURCE = CANDIDATE.parents[2] / "runtime/src/lib.rs"
FIXTURE = LAB / "ontology-lifecycle/migration/cal-w7-ontology-product-epoch-001/fixtures/output"
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


def digest_tree(path: Path) -> str:
    return digest_set(tuple(
        (item.relative_to(path).as_posix(), item)
        for item in sorted(path.rglob("*"))
        if item.is_file()
    ))


def implementation_digest() -> str:
    return digest_set(tuple(
        (relative, CANDIDATE / relative)
        for relative in ("Cargo.toml", "Cargo.lock", "src/lib.rs", "src/main.rs")
    ) + (("../../../runtime/src/lib.rs", RUNTIME_SOURCE),))


def experiment_digest() -> str:
    return digest_set(tuple(
        (relative, HERE / relative)
        for relative in (
            "EXPERIMENT-PROFILE.md", "PROTOCOL.md", "requirements.json",
            "requirements.schema.json", "run.py", "validate.py",
        )
    ))


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def main() -> int:
    requirements = read(REQUIREMENTS_PATH)
    report_path = HERE / "runs/latest-w7-process-interruption.json"
    attempt_paths = [HERE / f"evidence/attempt-{attempt}.json" for attempt in (1, 2)]
    report = read(report_path)
    attempts = [read(path) for path in attempt_paths]
    current_implementation = implementation_digest()
    current_experiment = experiment_digest()
    semantic_digest = digest_tree(FIXTURE / "semantic-events")
    governance_digest = digest_tree(FIXTURE / "governance-events")

    evidence_bound = (
        all(
            report["attempts"][index]["sha256"] == digest(path)
            for index, path in enumerate(attempt_paths)
        )
        and report.get("requirements_sha256") == digest(REQUIREMENTS_PATH)
        and all(item.get("requirements_sha256") == digest(REQUIREMENTS_PATH) for item in attempts)
    )
    sources_current = (
        report.get("implementation_digest_sha256") == current_implementation
        and report.get("experiment_digest_sha256") == current_experiment
        and report.get("semantic_event_directory_digest_sha256") == semantic_digest
        and report.get("governance_event_directory_digest_sha256") == governance_digest
        and all(
            item.get("implementation_digest_sha256") == current_implementation
            and item.get("experiment_digest_sha256") == current_experiment
            and item.get("semantic_event_directory_digest_sha256") == semantic_digest
            and item.get("governance_event_directory_digest_sha256") == governance_digest
            for item in attempts
        )
    )
    required_controls = set(requirements["required_controls"])
    controls_valid = all(
        required_controls.issubset(item.get("checks", {}))
        and all(item["checks"].get(control) is True for control in required_controls)
        for item in attempts
    )
    initial_and_recovery_valid = all(
        item.get("checks", {}).get("initial_synced_create") is True
        and item.get("checks", {}).get("normal_replacement_is_synced") is True
        and item.get("checks", {}).get("temporary_state_scoped") is True
        and item.get("temporary_state_removed") is True
        for item in attempts
    )
    deterministic = (
        report.get("deterministic_normalized_state") is True
        and len({item.get("normalized_state_digest_sha256") for item in attempts}) == 1
    )
    claim_boundary_valid = (
        report.get("power_loss_durability_claim") is False
        and report.get("canonical_replay_source") is False
        and report.get("authority_effect") == "none"
        and all(
            item.get("power_loss_durability_claim") is False
            and item.get("canonical_replay_source") is False
            and item.get("authority_effect") == "none"
            for item in attempts
        )
    )
    passed = (
        report.get("result") == "PASS"
        and report.get("attempt_count") == requirements["attempt_count"]
        and all(item.get("result") == "PASS" for item in attempts)
        and evidence_bound
        and sources_current
        and controls_valid
        and initial_and_recovery_valid
        and deterministic
        and claim_boundary_valid
    )
    receipt = {
        "schema_version": "cal-checkpoint-crash-consistency-validation/v1-prototype",
        "result": "PASS" if passed else "BLOCK",
        "profile_validation": "pass" if passed else "fail",
        "evidence_bound": evidence_bound,
        "sources_current": sources_current,
        "controls_valid": controls_valid,
        "initial_and_recovery_valid": initial_and_recovery_valid,
        "deterministic_normalized_state": deterministic,
        "claim_boundary_valid": claim_boundary_valid,
        "attempt_results": [item.get("result") for item in attempts],
        "normalized_state_digest_sha256": attempts[0].get("normalized_state_digest_sha256"),
        "implementation_digest_sha256": current_implementation,
        "experiment_digest_sha256": current_experiment,
        "semantic_event_directory_digest_sha256": semantic_digest,
        "governance_event_directory_digest_sha256": governance_digest,
        "requirements_sha256": digest(REQUIREMENTS_PATH),
        "attempt_evidence_sha256": [digest(path) for path in attempt_paths],
        "latest_report_sha256": digest(report_path),
        "power_loss_durability_claim": False,
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": "local_w7_process_interruption_atomic_checkpoint_replacement_evidence_only",
    }
    (HERE / "validation.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

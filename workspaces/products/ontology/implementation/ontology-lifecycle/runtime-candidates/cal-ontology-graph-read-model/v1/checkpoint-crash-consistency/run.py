#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
LAB = CANDIDATE.parents[3]
RUNTIME_SOURCE = CANDIDATE.parents[2] / "runtime/src/lib.rs"
FIXTURE = LAB / "ontology-lifecycle/migration/cal-w7-ontology-product-epoch-001/fixtures/output"
EXPECTATION = CANDIDATE / "recovery-expectation-w7.json"
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
            "EXPERIMENT-PROFILE.md",
            "PROTOCOL.md",
            "requirements.json",
            "requirements.schema.json",
            "run.py",
            "validate.py",
        )
    ))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_json(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def invoke(
    binary: Path,
    arguments: list[str],
    environment: dict[str, str] | None = None,
) -> dict[str, Any]:
    started = time.perf_counter_ns()
    completed = subprocess.run(
        [str(binary), *arguments],
        env={**os.environ, **(environment or {})},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "arguments": arguments,
        "exit": completed.returncode,
        "elapsed_ns": time.perf_counter_ns() - started,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "output": parse_json(completed.stdout),
        "error": parse_json(completed.stderr),
    }


def atomic_arguments(requirements: dict[str, Any], target: Path, prefix: str) -> list[str]:
    return [
        "checkpoint-write-atomic",
        str(FIXTURE / "semantic-events"),
        str(FIXTURE / "governance-events"),
        str(requirements[f"{prefix}_semantic_cursor"]),
        str(requirements[f"{prefix}_governance_cursor"]),
        str(target),
    ]


def recover_arguments(requirements: dict[str, Any], target: Path) -> list[str]:
    return [
        "recover-checkpoint-tail",
        str(target),
        str(FIXTURE / "semantic-events"),
        str(FIXTURE / "governance-events"),
        str(EXPECTATION),
        str(requirements["final_governance_cursor"]),
    ]


def recovery_valid(
    step: dict[str, Any],
    requirements: dict[str, Any],
    checkpoint_cursor: int,
) -> bool:
    result = step.get("output", {}).get("result", {})
    return (
        step.get("exit") == 0
        and result.get("exact_index_digest_match") is True
        and result.get("rebuilt_index_digest") == requirements["expected_final_index_digest"]
        and result.get("semantic_cursor") == requirements["final_semantic_cursor"]
        and result.get("checkpoint_semantic_cursor") == checkpoint_cursor
        and result.get("loaded_semantic_tail_event_count")
        == requirements["final_semantic_cursor"] - checkpoint_cursor
        and result.get("loaded_governance_tail_event_count")
        == requirements["final_governance_cursor"] - checkpoint_cursor
        and result.get("canonical_replay_source") is False
        and result.get("authority_effect") == "none"
    )


def public_step(step: dict[str, Any]) -> dict[str, Any]:
    return {
        "exit": step["exit"],
        "elapsed_ns": step["elapsed_ns"],
        "output": step["output"],
        "error": step["error"],
    }


def run_attempt(
    binary: Path,
    requirements: dict[str, Any],
    attempt: int,
    current_implementation: str,
    current_experiment: str,
    semantic_digest: str,
    governance_digest: str,
) -> dict[str, Any]:
    raw_sections: list[str] = []

    def step(name: str, arguments: list[str], environment: dict[str, str] | None = None) -> dict[str, Any]:
        result = invoke(binary, arguments, environment)
        raw_sections.append(
            f"STEP {name}\nEXIT {result['exit']}\nSTDOUT\n{result['stdout']}STDERR\n{result['stderr']}"
        )
        return result

    temporary_removed = False
    with tempfile.TemporaryDirectory(prefix=f"cal-checkpoint-crash-{attempt}-") as temporary:
        temporary_path = Path(temporary)
        target = temporary_path / "checkpoint.json"
        initial = step("initial", atomic_arguments(requirements, target, "initial"))
        initial_result = initial["output"].get("result", {})
        initial_bytes = target.read_bytes() if target.is_file() else b""

        after_stage = step(
            "terminate-after-stage-sync",
            atomic_arguments(requirements, target, "staged_replacement"),
            {
                "CAL_CHECKPOINT_ATOMIC_FAULT": "after-stage-sync",
                "CAL_CHECKPOINT_ATOMIC_TERMINATE": "exit-75",
            },
        )
        after_stage_bytes = target.read_bytes() if target.is_file() else b""
        stage_files_after_stage = sorted(
            item.name
            for item in temporary_path.iterdir()
            if item.name.startswith(".checkpoint.json.stage.")
        )
        recovery_after_stage = step(
            "recover-old-after-stage-termination", recover_arguments(requirements, target)
        )

        normal_replacement = step(
            "normal-replacement", atomic_arguments(requirements, target, "staged_replacement")
        )
        replacement_result = normal_replacement["output"].get("result", {})
        recovery_after_replacement = step(
            "recover-normal-replacement", recover_arguments(requirements, target)
        )

        before_rename_fault = target.read_bytes() if target.is_file() else b""
        after_rename = step(
            "terminate-after-rename",
            atomic_arguments(requirements, target, "renamed_replacement"),
            {
                "CAL_CHECKPOINT_ATOMIC_FAULT": "after-rename-before-directory-sync",
                "CAL_CHECKPOINT_ATOMIC_TERMINATE": "exit-75",
            },
        )
        after_rename_bytes = target.read_bytes() if target.is_file() else b""
        stage_files_after_rename = sorted(
            item.name
            for item in temporary_path.iterdir()
            if item.name.startswith(".checkpoint.json.stage.")
        )
        recovery_after_rename = step(
            "recover-new-after-rename-termination", recover_arguments(requirements, target)
        )

        unchanged = step(
            "idempotent-retry", atomic_arguments(requirements, target, "renamed_replacement")
        )
        unchanged_result = unchanged["output"].get("result", {})
        stable_bytes = target.read_bytes() if target.is_file() else b""

        regression = step(
            "regression-control", atomic_arguments(requirements, target, "staged_replacement")
        )
        regression_bytes = target.read_bytes() if target.is_file() else b""

        incomparable_arguments = [
            "checkpoint-write-atomic",
            str(FIXTURE / "semantic-events"),
            str(FIXTURE / "governance-events"),
            "40",
            "30",
            str(target),
        ]
        incomparable = step("incomparable-control", incomparable_arguments)
        incomparable_bytes = target.read_bytes() if target.is_file() else b""

        invalid_target = temporary_path / "invalid-checkpoint.json"
        invalid_target.write_bytes(b"invalid-existing-checkpoint")
        invalid_existing = step(
            "invalid-existing-control",
            atomic_arguments(requirements, invalid_target, "staged_replacement"),
        )
        invalid_bytes = invalid_target.read_bytes()

        symlink_victim = temporary_path / "symlink-victim.json"
        symlink_target = temporary_path / "symlink-checkpoint.json"
        symlink_victim.write_bytes(b"do-not-touch")
        symlink_target.symlink_to(symlink_victim)
        symlink_control = step(
            "symlink-target-control",
            atomic_arguments(requirements, symlink_target, "staged_replacement"),
        )
        symlink_victim_bytes = symlink_victim.read_bytes()

        lock_path = temporary_path / ".checkpoint.json.lock"
        with lock_path.open("a+b") as held_lock:
            fcntl.flock(held_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            busy = step(
                "concurrent-writer-control",
                [
                    "checkpoint-write-atomic",
                    str(FIXTURE / "semantic-events"),
                    str(FIXTURE / "governance-events"),
                    "40",
                    "40",
                    str(target),
                ],
            )
        busy_bytes = target.read_bytes() if target.is_file() else b""

        checks = {
            "initial_synced_create": (
                initial["exit"] == 0
                and initial_result.get("disposition") == "created"
                and initial_result.get("replacement_strategy")
                == requirements["required_replacement_strategy"]
                and initial_result.get("staged_file_synced") is True
                and initial_result.get("atomic_rename_completed") is True
                and initial_result.get("parent_directory_synced") is True
            ),
            "termination_after_stage_sync_preserves_old_target": (
                after_stage["exit"] == requirements["fault_process_exit"]
                and after_stage["stdout"] == ""
                and after_stage_bytes == initial_bytes
                and len(stage_files_after_stage) == 1
                and recovery_valid(
                    recovery_after_stage, requirements, requirements["initial_semantic_cursor"]
                )
            ),
            "normal_replacement_is_synced": (
                normal_replacement["exit"] == 0
                and replacement_result.get("disposition") == "replaced"
                and replacement_result.get("prior_semantic_cursor")
                == requirements["initial_semantic_cursor"]
                and replacement_result.get("parent_directory_synced") is True
                and recovery_valid(
                    recovery_after_replacement,
                    requirements,
                    requirements["staged_replacement_semantic_cursor"],
                )
            ),
            "termination_after_rename_exposes_valid_new_target": (
                after_rename["exit"] == requirements["fault_process_exit"]
                and after_rename["stdout"] == ""
                and after_rename_bytes != before_rename_fault
                and len(stage_files_after_rename) == 1
                and recovery_valid(
                    recovery_after_rename,
                    requirements,
                    requirements["renamed_replacement_semantic_cursor"],
                )
            ),
            "same_bytes_are_idempotent": (
                unchanged["exit"] == 0
                and unchanged_result.get("disposition") == "unchanged"
                and unchanged_result.get("staged_file_synced") is False
                and unchanged_result.get("atomic_rename_completed") is False
                and stable_bytes == after_rename_bytes
            ),
            "cursor_regression_preserves_target": (
                regression["exit"] == 2
                and regression["error"].get("code") == "CHECKPOINT_REPLACEMENT_REGRESSION"
                and regression_bytes == stable_bytes
            ),
            "incomparable_cursor_preserves_target": (
                incomparable["exit"] == 2
                and incomparable["error"].get("code") == "CHECKPOINT_REPLACEMENT_INCOMPARABLE"
                and incomparable_bytes == stable_bytes
            ),
            "invalid_existing_target_is_preserved": (
                invalid_existing["exit"] == 2
                and invalid_existing["error"].get("code") == "CHECKPOINT_EXISTING_INVALID"
                and invalid_bytes == b"invalid-existing-checkpoint"
            ),
            "symlink_target_is_rejected_without_touching_referent": (
                symlink_control["exit"] == 2
                and symlink_control["error"].get("code")
                == "CHECKPOINT_TARGET_SYMLINK_FORBIDDEN"
                and symlink_victim_bytes == b"do-not-touch"
            ),
            "concurrent_writer_lock_preserves_target": (
                busy["exit"] == 2
                and busy["error"].get("code") == "CHECKPOINT_WRITER_BUSY"
                and busy_bytes == stable_bytes
            ),
            "temporary_state_scoped": True,
        }
        state_signature = {
            "initial_disposition": initial_result.get("disposition"),
            "stage_exit": after_stage["exit"],
            "stage_orphan_count": len(stage_files_after_stage),
            "old_recovery_cursor": recovery_after_stage["output"].get("result", {}).get("checkpoint_semantic_cursor"),
            "normal_disposition": replacement_result.get("disposition"),
            "replacement_recovery_cursor": recovery_after_replacement["output"].get("result", {}).get("checkpoint_semantic_cursor"),
            "rename_exit": after_rename["exit"],
            "rename_orphan_count": len(stage_files_after_rename),
            "new_recovery_cursor": recovery_after_rename["output"].get("result", {}).get("checkpoint_semantic_cursor"),
            "idempotent_disposition": unchanged_result.get("disposition"),
            "regression_code": regression["error"].get("code"),
            "incomparable_code": incomparable["error"].get("code"),
            "invalid_existing_code": invalid_existing["error"].get("code"),
            "symlink_target_code": symlink_control["error"].get("code"),
            "busy_code": busy["error"].get("code"),
            "final_target_digest": digest_bytes(stable_bytes),
        }
        record = {
            "schema_version": "cal-checkpoint-crash-consistency-attempt/v1-prototype",
            "profile_id": requirements["profile_id"],
            "attempt": attempt,
            "result": "PASS" if all(checks.values()) else "BLOCK",
            "checks": checks,
            "state_signature": state_signature,
            "normalized_state_digest_sha256": digest_bytes(
                json.dumps(state_signature, sort_keys=True, separators=(",", ":")).encode()
            ),
            "steps": {
                "initial": public_step(initial),
                "terminate_after_stage_sync": public_step(after_stage),
                "recover_after_stage_sync": public_step(recovery_after_stage),
                "normal_replacement": public_step(normal_replacement),
                "recover_after_normal_replacement": public_step(recovery_after_replacement),
                "terminate_after_rename": public_step(after_rename),
                "recover_after_rename": public_step(recovery_after_rename),
                "idempotent_retry": public_step(unchanged),
                "regression": public_step(regression),
                "incomparable": public_step(incomparable),
                "invalid_existing": public_step(invalid_existing),
                "symlink_target": public_step(symlink_control),
                "concurrent_writer": public_step(busy),
            },
            "implementation_digest_sha256": current_implementation,
            "experiment_digest_sha256": current_experiment,
            "semantic_event_directory_digest_sha256": semantic_digest,
            "governance_event_directory_digest_sha256": governance_digest,
            "requirements_sha256": digest_file(REQUIREMENTS_PATH),
            "power_loss_durability_claim": False,
            "canonical_replay_source": False,
            "authority_effect": "none",
        }
    temporary_removed = not Path(temporary).exists()
    checks["temporary_state_scoped"] = temporary_removed
    record["result"] = "PASS" if all(checks.values()) else "BLOCK"
    record["temporary_state_removed"] = temporary_removed
    (HERE / f"raw-logs/attempt-{attempt}.log").write_text(
        "\n".join(raw_sections), encoding="utf-8"
    )
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("run",))
    parser.add_argument("profile", choices=("w7-process-interruption",))
    parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()
    requirements = json.loads(REQUIREMENTS_PATH.read_text(encoding="utf-8"))
    for directory in (HERE / "evidence", HERE / "raw-logs", HERE / "runs"):
        directory.mkdir(parents=True, exist_ok=True)
    attempt_paths = [HERE / f"evidence/attempt-{attempt}.json" for attempt in (1, 2)]
    if not args.rerun and (
        any(path.exists() for path in attempt_paths)
        or (HERE / "runs/latest-w7-process-interruption.json").exists()
    ):
        raise SystemExit("crash-consistency evidence exists; pass --rerun to replace the exact epoch")

    target = HERE / "target"
    build = subprocess.run(
        ["cargo", "build", "--release", "--locked", "--bins"],
        cwd=CANDIDATE,
        env={**os.environ, "CARGO_TARGET_DIR": str(target)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if build.returncode != 0:
        raise SystemExit("locked release build failed: " + build.stderr[-3000:])
    binary = target / "release/cal-ontology-graph-read-model"
    current_implementation = implementation_digest()
    current_experiment = experiment_digest()
    semantic_digest = digest_tree(FIXTURE / "semantic-events")
    governance_digest = digest_tree(FIXTURE / "governance-events")
    attempts = []
    for attempt, path in zip((1, 2), attempt_paths, strict=True):
        record = run_attempt(
            binary,
            requirements,
            attempt,
            current_implementation,
            current_experiment,
            semantic_digest,
            governance_digest,
        )
        write_json(path, record)
        attempts.append(record)

    deterministic = len({item["normalized_state_digest_sha256"] for item in attempts}) == 1
    passed = all(item["result"] == "PASS" for item in attempts) and deterministic
    now = datetime.now(timezone.utc).replace(microsecond=0)
    report = {
        "schema_version": "cal-checkpoint-crash-consistency-report/v1-prototype",
        "profile_id": "cal-checkpoint-crash-consistency/v1",
        "regime_id": args.profile,
        "run_at_utc": now.isoformat().replace("+00:00", "Z"),
        "result": "PASS" if passed else "BLOCK",
        "quality_bar_status": "pass" if passed else "fail",
        "anti_pattern_hits": [],
        "workflow_gaps": [
            "sudden power loss and storage-controller persistence are not simulated",
            "automatic orphan-stage retention and deletion policy remains operational residue",
            "cross-platform replacement semantics are not established",
            "sustained ingestion, backpressure, and multi-writer event ordering remain undefined",
        ],
        "attempt_count": len(attempts),
        "attempts": [
            {
                "path": str(path.relative_to(HERE)),
                "sha256": digest_file(path),
                "result": record["result"],
                "normalized_state_digest_sha256": record["normalized_state_digest_sha256"],
            }
            for path, record in zip(attempt_paths, attempts, strict=True)
        ],
        "deterministic_normalized_state": deterministic,
        "implementation_digest_sha256": current_implementation,
        "experiment_digest_sha256": current_experiment,
        "semantic_event_directory_digest_sha256": semantic_digest,
        "governance_event_directory_digest_sha256": governance_digest,
        "requirements_sha256": digest_file(REQUIREMENTS_PATH),
        "power_loss_durability_claim": False,
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": "local_w7_process_interruption_atomic_checkpoint_replacement_evidence_only",
    }
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    report_path = HERE / f"runs/{stamp}-w7-process-interruption.json"
    write_json(report_path, report)
    write_json(HERE / "runs/latest-w7-process-interruption.json", report)
    print(json.dumps({
        "mode": "run",
        "profile": args.profile,
        "status": report["quality_bar_status"],
        "report": str(report_path),
        "observation": "skipped-no-repository-observability-binding",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
PROFILES_PATH = HERE / "profiles.json"
REQUIREMENTS = CANDIDATE / "recovery-requirements.json"
RUNTIME_SOURCE = CANDIDATE.parents[2] / "runtime/src/lib.rs"
ATTEMPTS = 2


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


def invoke(binary: Path, fixture: Path, expectation: Path) -> tuple[subprocess.CompletedProcess[str], int]:
    started = time.perf_counter_ns()
    completed = subprocess.run(
        [
            str(binary),
            "recover-files",
            str(fixture / "semantic-events"),
            str(fixture / "governance-events"),
            str(expectation),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed, time.perf_counter_ns() - started


def parse_json(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def normalized_recovery_digest(output: dict[str, Any]) -> str:
    normalized = json.loads(json.dumps(output))
    result = normalized.get("result", {})
    result.pop("event_store_load_ns", None)
    result.pop("graph_rebuild_ns", None)
    return digest_bytes(json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("run",))
    parser.add_argument("profile", choices=("medium", "large"))
    parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()
    profiles = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))["profiles"]
    config = profiles[args.profile]
    for directory in (HERE / "evidence", HERE / "raw-logs", HERE / "runs"):
        directory.mkdir(parents=True, exist_ok=True)
    evidence_paths = [
        HERE / f"evidence/{args.profile}-attempt-{attempt}.json" for attempt in (1, 2)
    ]
    fixture_receipt_path = HERE / f"evidence/{args.profile}-fixture.json"
    if not args.rerun and (fixture_receipt_path.exists() or any(path.exists() for path in evidence_paths)):
        raise SystemExit("profile evidence exists; pass --rerun to replace the exact epoch")

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
    generator = target / "release/generate-event-fixture"
    recovery = target / "release/cal-ontology-graph-read-model"
    current_runtime = runtime_digest()
    current_generator = generator_digest()
    current_experiment = experiment_digest()

    with tempfile.TemporaryDirectory(prefix=f"cal-event-file-{args.profile}-") as temporary:
        temporary_path = Path(temporary)
        fixture = temporary_path / "fixture"
        generation_started = time.perf_counter_ns()
        generated = subprocess.run(
            [
                str(generator),
                "--profile",
                args.profile,
                "--profiles",
                str(PROFILES_PATH),
                "--output-root",
                str(fixture),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        generation_process_ns = time.perf_counter_ns() - generation_started
        fixture_receipt = parse_json(generated.stdout)
        expected_subjects = config["node_count"] * (config["relations_per_node"] + 1)
        fixture_pass = (
            generated.returncode == 0
            and fixture_receipt.get("schema_version")
            == "cal-event-file-generation-receipt/v1-prototype"
            and fixture_receipt.get("profile_id") == args.profile
            and fixture_receipt.get("fixture_kind")
            == "synthetic-canonical-format-event-files"
            and fixture_receipt.get("generated_subject_count") == expected_subjects
            and fixture_receipt.get("semantic_event_file_count") == expected_subjects
            and fixture_receipt.get("governance_event_file_count") == expected_subjects
            and fixture_receipt.get("canonical_replay_source") is False
            and fixture_receipt.get("authority_effect") == "none"
        )
        if not fixture_pass:
            raise SystemExit("fixture generation failed: " + generated.stderr[-3000:])
        fixture_evidence = {
            **fixture_receipt,
            "generation_process_ns": generation_process_ns,
            "runtime_digest_sha256": current_runtime,
            "generator_digest_sha256": current_generator,
            "experiment_digest_sha256": current_experiment,
            "result": "PASS",
        }
        fixture_receipt_path.write_text(
            json.dumps(fixture_evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        expectation_path = temporary_path / "expectation.json"
        expectation_path.write_text(
            json.dumps(fixture_receipt["expectation"], sort_keys=True) + "\n",
            encoding="utf-8",
        )

        attempts = []
        for attempt, evidence_path in zip((1, 2), evidence_paths, strict=True):
            completed, process_elapsed = invoke(recovery, fixture, expectation_path)
            output = parse_json(completed.stdout)
            result = output.get("result", {})
            load_ns = result.get("event_store_load_ns")
            rebuild_ns = result.get("graph_rebuild_ns")
            passed = (
                completed.returncode == 0
                and isinstance(load_ns, int)
                and load_ns > 0
                and isinstance(rebuild_ns, int)
                and rebuild_ns > 0
                and load_ns + rebuild_ns <= process_elapsed
                and process_elapsed <= config["maximum_process_recovery_ns"]
                and result.get("recovery_strategy")
                == "full_rebuild_from_canonical_event_files"
                and result.get("semantic_cursor") == expected_subjects
                and result.get("source_event_count") == expected_subjects
                and result.get("source_event_set_digest")
                == fixture_receipt["expectation"]["source_event_set_digest"]
                and result.get("rebuilt_index_digest")
                == fixture_receipt["expectation"]["expected_index_digest"]
                and result.get("checkpoint_used") is False
                and output.get("canonical_replay_source") is False
                and output.get("authority_effect") == "none"
            )
            record = {
                "schema_version": "cal-generated-event-file-recovery-attempt/v1-prototype",
                "profile_id": args.profile,
                "attempt": attempt,
                "result": "PASS" if passed else "BLOCK",
                "process_elapsed_ns": process_elapsed,
                "event_store_load_ns": load_ns,
                "graph_rebuild_ns": rebuild_ns,
                "maximum_process_recovery_ns": config["maximum_process_recovery_ns"],
                "normalized_recovery_digest_sha256": normalized_recovery_digest(output),
                "fixture_receipt_sha256": digest_file(fixture_receipt_path),
                "runtime_digest_sha256": current_runtime,
                "generator_digest_sha256": current_generator,
                "experiment_digest_sha256": current_experiment,
                "semantic_event_directory_digest_sha256": fixture_receipt[
                    "semantic_event_directory_digest_sha256"
                ],
                "governance_event_directory_digest_sha256": fixture_receipt[
                    "governance_event_directory_digest_sha256"
                ],
                "exit": completed.returncode,
                "canonical_replay_source": False,
                "authority_effect": "none",
            }
            evidence_path.write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            (HERE / f"raw-logs/{args.profile}-attempt-{attempt}.log").write_text(
                "STDOUT\n" + completed.stdout + "STDERR\n" + completed.stderr,
                encoding="utf-8",
            )
            attempts.append(record)

        first_event = sorted((fixture / "semantic-events").glob("*.json"))[0]
        first_event.write_bytes(b" " + first_event.read_bytes())
        tampered, _ = invoke(recovery, fixture, expectation_path)
        tamper_error = parse_json(tampered.stderr)
        control = {
            "result": "PASS"
            if tampered.returncode != 0 and tamper_error.get("code") == "NON_CANONICAL_JSON"
            else "BLOCK",
            "exit": tampered.returncode,
            "code": tamper_error.get("code"),
        }

    deterministic = len({item["normalized_recovery_digest_sha256"] for item in attempts}) == 1
    passed = (
        all(item["result"] == "PASS" for item in attempts)
        and deterministic
        and control["result"] == "PASS"
    )
    now = datetime.now(timezone.utc).replace(microsecond=0)
    report = {
        "schema_version": "cal-generated-event-file-recovery-report/v1-prototype",
        "profile_id": "cal-ontology-generated-event-file-recovery/v1",
        "regime_id": args.profile,
        "run_at_utc": now.isoformat().replace("+00:00", "Z"),
        "result": "PASS" if passed else "BLOCK",
        "quality_bar_status": "pass" if passed else "fail",
        "anti_pattern_hits": [],
        "workflow_gaps": [
            "generated event-file recovery stops at 50000 subjects rather than the 250000-subject calculated-cut profile",
            "fixture generation is excluded from recovery timing",
            "RSS, checkpoint, crash-consistency, and durability are not measured",
        ],
        "runtime_digest_sha256": current_runtime,
        "generator_digest_sha256": current_generator,
        "experiment_digest_sha256": current_experiment,
        "fixture": {
            "path": str(fixture_receipt_path.relative_to(HERE)),
            "sha256": digest_file(fixture_receipt_path),
            "generated_subject_count": fixture_receipt["generated_subject_count"],
            "semantic_event_file_count": fixture_receipt["semantic_event_file_count"],
            "governance_event_file_count": fixture_receipt["governance_event_file_count"],
            "semantic_event_bytes": fixture_receipt["semantic_event_bytes"],
            "governance_event_bytes": fixture_receipt["governance_event_bytes"],
            "generation_process_ns": generation_process_ns,
        },
        "attempt_count": len(attempts),
        "attempts": [
            {
                "path": str(path.relative_to(HERE)),
                "sha256": digest_file(path),
                "process_elapsed_ns": attempt["process_elapsed_ns"],
                "event_store_load_ns": attempt["event_store_load_ns"],
                "graph_rebuild_ns": attempt["graph_rebuild_ns"],
                "result": attempt["result"],
            }
            for path, attempt in zip(evidence_paths, attempts, strict=True)
        ],
        "deterministic_recovery_receipt": deterministic,
        "tampered_canonical_json_control": control,
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": "declared_local_synthetic_canonical_format_event_file_profiles_only",
    }
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    body = json.dumps(report, indent=2, sort_keys=True) + "\n"
    report_path = HERE / f"runs/{stamp}-{args.profile}.json"
    report_path.write_text(body, encoding="utf-8")
    (HERE / f"runs/latest-{args.profile}.json").write_text(body, encoding="utf-8")
    print(json.dumps({
        "mode": "run",
        "profile": args.profile,
        "status": report["quality_bar_status"],
        "report": str(report_path),
        "profile_validation": report["quality_bar_status"],
        "observation": "skipped-no-repository-observability-binding",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

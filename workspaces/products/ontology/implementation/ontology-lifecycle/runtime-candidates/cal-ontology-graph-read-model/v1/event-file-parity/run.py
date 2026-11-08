#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
PROFILES_PATH = HERE / "profiles.json"
RESOURCE_REQUIREMENTS_PATH = HERE / "resource-requirements.json"
RESOURCE_SCHEMA_PATH = HERE / "resource-requirements.schema.json"
GNU_TIME = Path("/usr/bin/time")
RUNTIME_SOURCE = CANDIDATE.parents[2] / "runtime/src/lib.rs"


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


def parse_json(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def mem_available_bytes() -> int:
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    return 0


def filesystem_available(path: Path) -> tuple[int, int]:
    state = os.statvfs(path)
    return state.f_bavail * state.f_frsize, state.f_favail


def limit_virtual_memory(limit_bytes: int) -> None:
    resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))


def measured_run(
    arguments: list[str],
    measurement_path: Path,
    hard_virtual_memory_bytes: int,
    timeout_ns: int,
) -> tuple[subprocess.CompletedProcess[str], int, dict[str, float | int | bool]]:
    measurement_format = "\n".join((
        "maximum_rss_kib=%M",
        "filesystem_inputs=%I",
        "filesystem_outputs=%O",
        "major_page_faults=%F",
        "minor_page_faults=%R",
        "wall_seconds=%e",
    ))
    started = time.perf_counter_ns()
    process = subprocess.Popen(
        [
            str(GNU_TIME),
            "--quiet",
            f"--format={measurement_format}",
            "--output",
            str(measurement_path),
            "--",
            *arguments,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=lambda: limit_virtual_memory(hard_virtual_memory_bytes),
        start_new_session=True,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout_ns / 1_000_000_000)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
    elapsed_ns = time.perf_counter_ns() - started
    completed = subprocess.CompletedProcess(arguments, process.returncode, stdout, stderr)
    measurement: dict[str, float | int | bool] = {"timed_out": timed_out}
    if measurement_path.is_file():
        for line in measurement_path.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if not separator:
                continue
            measurement[key] = float(value) if key == "wall_seconds" else int(value)
    return completed, elapsed_ns, measurement


def normalized_recovery_digest(output: dict[str, Any]) -> str:
    normalized = json.loads(json.dumps(output))
    result = normalized.get("result", {})
    result.pop("event_store_load_ns", None)
    result.pop("graph_rebuild_ns", None)
    return digest_bytes(json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode())


def allocated_bytes(path: Path) -> int:
    completed = subprocess.run(
        ["du", "--block-size=1", "--summarize", str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return int(completed.stdout.split()[0])


def file_count(path: Path) -> int:
    return sum(1 for item in os.scandir(path) if item.is_file(follow_symlinks=False))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("run",))
    parser.add_argument("profile", choices=("parity",))
    parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()
    requirements = json.loads(RESOURCE_REQUIREMENTS_PATH.read_text(encoding="utf-8"))
    profile = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))["profiles"][args.profile]
    for directory in (HERE / "evidence", HERE / "raw-logs", HERE / "runs"):
        directory.mkdir(parents=True, exist_ok=True)
    fixture_path = HERE / "evidence/parity-fixture.json"
    attempt_paths = [HERE / f"evidence/parity-attempt-{attempt}.json" for attempt in (1, 2)]
    if not args.rerun and (
        fixture_path.exists()
        or any(path.exists() for path in attempt_paths)
        or (HERE / "runs/latest-parity.json").exists()
    ):
        raise SystemExit("parity evidence exists; pass --rerun to replace the exact epoch")

    temporary_root = Path(tempfile.gettempdir())
    available_filesystem_bytes, available_filesystem_inodes = filesystem_available(temporary_root)
    preflight = {
        "available_memory_bytes": mem_available_bytes(),
        "available_filesystem_bytes": available_filesystem_bytes,
        "available_filesystem_inodes": available_filesystem_inodes,
        "minimum_available_memory_bytes": requirements["minimum_available_memory_bytes"],
        "minimum_available_filesystem_bytes": requirements["minimum_available_filesystem_bytes"],
        "minimum_available_filesystem_inodes": requirements["minimum_available_filesystem_inodes"],
        "gnu_time_available": GNU_TIME.is_file(),
    }
    preflight_pass = (
        preflight["available_memory_bytes"] >= preflight["minimum_available_memory_bytes"]
        and preflight["available_filesystem_bytes"] >= preflight["minimum_available_filesystem_bytes"]
        and preflight["available_filesystem_inodes"] >= preflight["minimum_available_filesystem_inodes"]
        and preflight["gnu_time_available"] is True
    )
    preflight["result"] = "PASS" if preflight_pass else "BLOCK"
    if not preflight_pass:
        write_json(HERE / "evidence/preflight-block.json", preflight)
        raise SystemExit("resource preflight blocked fixture allocation")

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
    hard_limit = requirements["hard_virtual_memory_bytes"]
    fixture_removed = False

    with tempfile.TemporaryDirectory(prefix="cal-event-file-parity-") as temporary:
        temporary_path = Path(temporary)
        fixture = temporary_path / "fixture"
        generation_measurement_path = HERE / "raw-logs/parity-generation.time"
        generated, generation_process_ns, generation_resource = measured_run(
            [
                str(generator),
                "--profile",
                args.profile,
                "--profiles",
                str(PROFILES_PATH),
                "--output-root",
                str(fixture),
            ],
            generation_measurement_path,
            hard_limit,
            requirements["maximum_generation_ns"],
        )
        (HERE / "raw-logs/parity-generation.log").write_text(
            "STDOUT\n" + generated.stdout + "STDERR\n" + generated.stderr,
            encoding="utf-8",
        )
        fixture_receipt = parse_json(generated.stdout)
        logical_bytes = (
            fixture_receipt.get("semantic_event_bytes", 0)
            + fixture_receipt.get("governance_event_bytes", 0)
        )
        actual_semantic_files = file_count(fixture / "semantic-events") if fixture.exists() else 0
        actual_governance_files = file_count(fixture / "governance-events") if fixture.exists() else 0
        actual_allocated_bytes = allocated_bytes(fixture) if fixture.exists() else 0
        fixture_pass = (
            generated.returncode == 0
            and fixture_receipt.get("schema_version") == "cal-event-file-generation-receipt/v1-prototype"
            and fixture_receipt.get("profile_id") == args.profile
            and fixture_receipt.get("generated_node_count") == requirements["node_count"]
            and fixture_receipt.get("generated_relation_count") == requirements["relation_count"]
            and fixture_receipt.get("generated_subject_count") == requirements["subject_count"]
            and actual_semantic_files == requirements["semantic_event_file_count"]
            and actual_governance_files == requirements["governance_event_file_count"]
            and logical_bytes <= requirements["maximum_logical_event_bytes"]
            and actual_allocated_bytes <= requirements["maximum_allocated_fixture_bytes"]
            and generation_process_ns <= requirements["maximum_generation_ns"]
            and generation_resource.get("timed_out") is False
            and generation_resource.get("maximum_rss_kib", 0)
            <= requirements["maximum_generation_peak_rss_kib"]
            and fixture_receipt.get("fixture_kind") == requirements["fixture_kind"]
            and fixture_receipt.get("canonical_replay_source") is False
            and fixture_receipt.get("authority_effect") == "none"
        )
        fixture_evidence = {
            **fixture_receipt,
            "actual_semantic_event_file_count": actual_semantic_files,
            "actual_governance_event_file_count": actual_governance_files,
            "logical_event_bytes": logical_bytes,
            "allocated_fixture_bytes": actual_allocated_bytes,
            "generation_process_ns": generation_process_ns,
            "generation_resource_measurement": generation_resource,
            "hard_virtual_memory_bytes": hard_limit,
            "preflight": preflight,
            "runtime_digest_sha256": current_runtime,
            "generator_digest_sha256": current_generator,
            "experiment_digest_sha256": current_experiment,
            "result": "PASS" if fixture_pass else "BLOCK",
        }
        write_json(fixture_path, fixture_evidence)
        if not fixture_pass:
            raise SystemExit("fixture generation or resource bound failed: " + generated.stderr[-3000:])

        expectation_path = temporary_path / "expectation.json"
        write_json(expectation_path, fixture_receipt["expectation"])
        attempts: list[dict[str, Any]] = []
        for attempt, evidence_path in zip((1, 2), attempt_paths, strict=True):
            measurement_path = HERE / f"raw-logs/parity-attempt-{attempt}.time"
            completed, process_elapsed_ns, measured = measured_run(
                [
                    str(recovery),
                    "recover-files",
                    str(fixture / "semantic-events"),
                    str(fixture / "governance-events"),
                    str(expectation_path),
                ],
                measurement_path,
                hard_limit,
                requirements["maximum_process_recovery_ns"],
            )
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
                and load_ns + rebuild_ns <= process_elapsed_ns
                and process_elapsed_ns <= requirements["maximum_process_recovery_ns"]
                and measured.get("timed_out") is False
                and measured.get("maximum_rss_kib", 0)
                <= requirements["maximum_recovery_peak_rss_kib"]
                and result.get("recovery_strategy") == "full_rebuild_from_canonical_event_files"
                and result.get("semantic_cursor") == requirements["subject_count"]
                and result.get("source_event_count") == requirements["subject_count"]
                and result.get("source_event_set_digest")
                == fixture_receipt["expectation"]["source_event_set_digest"]
                and result.get("rebuilt_index_digest")
                == fixture_receipt["expectation"]["expected_index_digest"]
                and result.get("checkpoint_used") is False
                and output.get("canonical_replay_source") is False
                and output.get("authority_effect") == "none"
            )
            record = {
                "schema_version": "cal-event-file-parity-recovery-attempt/v1-prototype",
                "profile_id": args.profile,
                "attempt": attempt,
                "result": "PASS" if passed else "BLOCK",
                "process_elapsed_ns": process_elapsed_ns,
                "event_store_load_ns": load_ns,
                "graph_rebuild_ns": rebuild_ns,
                "resource_measurement": measured,
                "hard_virtual_memory_bytes": hard_limit,
                "maximum_process_recovery_ns": requirements["maximum_process_recovery_ns"],
                "maximum_recovery_peak_rss_kib": requirements["maximum_recovery_peak_rss_kib"],
                "normalized_recovery_digest_sha256": normalized_recovery_digest(output),
                "fixture_receipt_sha256": digest_file(fixture_path),
                "runtime_digest_sha256": current_runtime,
                "generator_digest_sha256": current_generator,
                "experiment_digest_sha256": current_experiment,
                "exit": completed.returncode,
                "canonical_replay_source": False,
                "authority_effect": "none",
            }
            write_json(evidence_path, record)
            (HERE / f"raw-logs/parity-attempt-{attempt}.log").write_text(
                "STDOUT\n" + completed.stdout + "STDERR\n" + completed.stderr,
                encoding="utf-8",
            )
            attempts.append(record)

        first_event = fixture / "semantic-events/00000001-synthetic-semantic-00000001.json"
        first_event.write_bytes(b" " + first_event.read_bytes())
        tamper_measurement = HERE / "raw-logs/parity-noncanonical-control.time"
        tampered, tamper_elapsed_ns, tamper_resource = measured_run(
            [
                str(recovery),
                "recover-files",
                str(fixture / "semantic-events"),
                str(fixture / "governance-events"),
                str(expectation_path),
            ],
            tamper_measurement,
            hard_limit,
            requirements["maximum_process_recovery_ns"],
        )
        tamper_error = parse_json(tampered.stderr)
        control = {
            "result": "PASS"
            if tampered.returncode != 0 and tamper_error.get("code") == "NON_CANONICAL_JSON"
            else "BLOCK",
            "exit": tampered.returncode,
            "code": tamper_error.get("code"),
            "process_elapsed_ns": tamper_elapsed_ns,
            "resource_measurement": tamper_resource,
        }
    fixture_removed = not fixture.exists()

    deterministic = len({item["normalized_recovery_digest_sha256"] for item in attempts}) == 1
    passed = (
        all(item["result"] == "PASS" for item in attempts)
        and deterministic
        and control["result"] == "PASS"
        and fixture_removed
    )
    now = datetime.now(timezone.utc).replace(microsecond=0)
    report = {
        "schema_version": "cal-event-file-parity-report/v1-prototype",
        "profile_id": "cal-ontology-event-file-parity/v1",
        "regime_id": args.profile,
        "run_at_utc": now.isoformat().replace("+00:00", "Z"),
        "result": "PASS" if passed else "BLOCK",
        "quality_bar_status": "pass" if passed else "fail",
        "anti_pattern_hits": [],
        "workflow_gaps": [
            "the fixture is synthetic rather than a representative production workload",
            "peak RSS is an operating-system process measure rather than allocator accounting",
            "sustained ingestion, checkpoints, crash consistency, durability, backpressure, and multi-writer ordering remain undefined",
        ],
        "runtime_digest_sha256": current_runtime,
        "generator_digest_sha256": current_generator,
        "experiment_digest_sha256": current_experiment,
        "resource_requirements_sha256": digest_file(RESOURCE_REQUIREMENTS_PATH),
        "preflight": preflight,
        "fixture": {
            "path": str(fixture_path.relative_to(HERE)),
            "sha256": digest_file(fixture_path),
            "subject_count": fixture_evidence["generated_subject_count"],
            "total_event_file_count": actual_semantic_files + actual_governance_files,
            "logical_event_bytes": logical_bytes,
            "allocated_fixture_bytes": actual_allocated_bytes,
            "generation_process_ns": generation_process_ns,
            "generation_peak_rss_kib": generation_resource.get("maximum_rss_kib"),
            "removed_after_measurement": fixture_removed,
        },
        "attempt_count": len(attempts),
        "attempts": [
            {
                "path": str(path.relative_to(HERE)),
                "sha256": digest_file(path),
                "process_elapsed_ns": attempt["process_elapsed_ns"],
                "event_store_load_ns": attempt["event_store_load_ns"],
                "graph_rebuild_ns": attempt["graph_rebuild_ns"],
                "maximum_rss_kib": attempt["resource_measurement"].get("maximum_rss_kib"),
                "result": attempt["result"],
            }
            for path, attempt in zip(attempt_paths, attempts, strict=True)
        ],
        "deterministic_recovery_receipt": deterministic,
        "tampered_canonical_json_control": control,
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": "local_synthetic_250000_subject_event_file_parity_evidence_only",
    }
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    report_path = HERE / f"runs/{stamp}-parity.json"
    write_json(report_path, report)
    write_json(HERE / "runs/latest-parity.json", report)
    print(json.dumps({
        "mode": "run",
        "profile": args.profile,
        "status": report["quality_bar_status"],
        "report": str(report_path),
        "fixture_removed": fixture_removed,
        "observation": "skipped-no-repository-observability-binding",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

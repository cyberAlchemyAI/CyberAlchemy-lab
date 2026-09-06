#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import signal
import statistics
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
PROFILES_PATH = HERE / "profiles.json"
REQUIREMENTS_PATH = HERE / "resource-requirements.json"
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
        ("checkpoint-recovery/profiles.json", PROFILES_PATH),
    ))


def experiment_digest() -> str:
    return digest_set(tuple(
        (relative, HERE / relative)
        for relative in (
            "EXPERIMENT-PROFILE.md",
            "PROTOCOL.md",
            "profiles.json",
            "resource-requirements.json",
            "run.py",
            "validate.py",
        )
    ))


def parse_json(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def mem_available_bytes() -> int:
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    return 0


def filesystem_available(path: Path) -> tuple[int, int]:
    state = os.statvfs(path)
    return state.f_bavail * state.f_frsize, state.f_favail


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
            if separator:
                measurement[key] = float(value) if key == "wall_seconds" else int(value)
    return completed, elapsed_ns, measurement


def normalized_recovery_digest(output: dict[str, Any]) -> str:
    normalized = json.loads(json.dumps(output))
    result = normalized.get("result", {})
    for field in (
        "event_store_load_ns",
        "checkpoint_read_decode_ns",
        "canonical_tail_load_ns",
        "graph_rebuild_ns",
    ):
        result.pop(field, None)
    return digest_bytes(json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode())


def recovery_pass(
    output: dict[str, Any],
    expected: dict[str, Any],
    process_elapsed_ns: int,
    measured: dict[str, float | int | bool],
    requirements: dict[str, Any],
    checkpoint: bool,
) -> bool:
    result = output.get("result", {})
    timings = [result.get("graph_rebuild_ns")]
    timings.append(result.get("canonical_tail_load_ns") if checkpoint else result.get("event_store_load_ns"))
    if checkpoint:
        timings.append(result.get("checkpoint_read_decode_ns"))
    return (
        all(isinstance(value, int) and value > 0 for value in timings)
        and sum(timings) <= process_elapsed_ns
        and process_elapsed_ns <= requirements["maximum_process_recovery_ns"]
        and measured.get("timed_out") is False
        and measured.get("maximum_rss_kib", 0) <= requirements["maximum_recovery_peak_rss_kib"]
        and result.get("semantic_cursor") == requirements["subject_count"]
        and result.get("source_event_count") == requirements["subject_count"]
        and result.get("source_event_set_digest") == expected["source_event_set_digest"]
        and result.get("rebuilt_index_digest") == expected["expected_index_digest"]
        and result.get("exact_index_digest_match") is True
        and result.get("checkpoint_used") is checkpoint
        and result.get("canonical_replay_source") is False
        and output.get("canonical_replay_source") is False
        and output.get("authority_effect") == "none"
        and (
            result.get("recovery_strategy")
            == (
                "verified_disposable_checkpoint_plus_canonical_event_tail"
                if checkpoint
                else "full_rebuild_from_canonical_event_files"
            )
        )
        and (
            not checkpoint
            or (
                result.get("checkpoint_semantic_cursor") == requirements["checkpoint_semantic_cursor"]
                and result.get("checkpoint_governance_cursor") == requirements["checkpoint_governance_cursor"]
                and result.get("loaded_semantic_tail_event_count") == requirements["semantic_tail_event_count"]
                and result.get("loaded_governance_tail_event_count") == requirements["governance_tail_event_count"]
            )
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("run",))
    parser.add_argument("profile", choices=("large",))
    parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()
    requirements = json.loads(REQUIREMENTS_PATH.read_text(encoding="utf-8"))
    attempt_ids = tuple(range(1, requirements["attempt_count_per_strategy"] + 1))
    for directory in (HERE / "evidence", HERE / "raw-logs", HERE / "runs"):
        directory.mkdir(parents=True, exist_ok=True)
    evidence_paths = {
        strategy: [HERE / f"evidence/{strategy}-attempt-{attempt}.json" for attempt in attempt_ids]
        for strategy in ("full-replay", "checkpoint-tail")
    }
    fixture_path = HERE / "evidence/checkpoint-fixture.json"
    if not args.rerun and (
        fixture_path.exists()
        or any(path.exists() for paths in evidence_paths.values() for path in paths)
        or (HERE / "runs/latest-large.json").exists()
    ):
        raise SystemExit("checkpoint evidence exists; pass --rerun to replace the exact epoch")

    temporary_root = Path(tempfile.gettempdir())
    available_bytes, available_inodes = filesystem_available(temporary_root)
    preflight = {
        "available_memory_bytes": mem_available_bytes(),
        "available_filesystem_bytes": available_bytes,
        "available_filesystem_inodes": available_inodes,
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
    checkpoint_removed = False

    with tempfile.TemporaryDirectory(prefix="cal-checkpoint-recovery-") as temporary:
        temporary_path = Path(temporary)
        fixture = temporary_path / "fixture"
        checkpoint_path = temporary_path / "checkpoint.json"
        generated, generation_ns, generation_resource = measured_run(
            [
                str(generator), "--profile", args.profile, "--profiles", str(PROFILES_PATH),
                "--output-root", str(fixture),
            ],
            HERE / "raw-logs/generation.time",
            hard_limit,
            requirements["maximum_generation_ns"],
        )
        (HERE / "raw-logs/generation.log").write_text(
            "STDOUT\n" + generated.stdout + "STDERR\n" + generated.stderr,
            encoding="utf-8",
        )
        fixture_receipt = parse_json(generated.stdout)
        expected = fixture_receipt.get("expectation", {})
        expectation_path = temporary_path / "expectation.json"
        write_json(expectation_path, expected)
        semantic_files = file_count(fixture / "semantic-events") if fixture.exists() else 0
        governance_files = file_count(fixture / "governance-events") if fixture.exists() else 0
        logical_bytes = fixture_receipt.get("semantic_event_bytes", 0) + fixture_receipt.get("governance_event_bytes", 0)
        fixture_allocated = allocated_bytes(fixture) if fixture.exists() else 0
        fixture_pass = (
            generated.returncode == 0
            and fixture_receipt.get("generated_node_count") == requirements["node_count"]
            and fixture_receipt.get("generated_relation_count") == requirements["relation_count"]
            and fixture_receipt.get("generated_subject_count") == requirements["subject_count"]
            and semantic_files == requirements["semantic_event_file_count"]
            and governance_files == requirements["governance_event_file_count"]
            and logical_bytes <= requirements["maximum_logical_event_bytes"]
            and fixture_allocated <= requirements["maximum_allocated_fixture_bytes"]
            and generation_ns <= requirements["maximum_generation_ns"]
            and generation_resource.get("timed_out") is False
            and generation_resource.get("maximum_rss_kib", 0) <= requirements["maximum_generation_peak_rss_kib"]
        )
        if not fixture_pass:
            write_json(fixture_path, {
                **fixture_receipt,
                "result": "BLOCK",
                "preflight": preflight,
                "semantic_event_file_count": semantic_files,
                "governance_event_file_count": governance_files,
                "logical_event_bytes": logical_bytes,
                "allocated_fixture_bytes": fixture_allocated,
                "generation_process_ns": generation_ns,
                "generation_resource_measurement": generation_resource,
                "runtime_digest_sha256": current_runtime,
                "generator_digest_sha256": current_generator,
                "experiment_digest_sha256": current_experiment,
            })
            raise SystemExit("fixture generation failed before checkpoint construction")

        created, creation_ns, creation_resource = measured_run(
            [
                str(recovery), "checkpoint-create",
                str(fixture / "semantic-events"), str(fixture / "governance-events"),
                str(requirements["checkpoint_semantic_cursor"]),
                str(requirements["checkpoint_governance_cursor"]), str(checkpoint_path),
            ],
            HERE / "raw-logs/checkpoint-creation.time",
            hard_limit,
            requirements["maximum_checkpoint_creation_ns"],
        )
        (HERE / "raw-logs/checkpoint-creation.log").write_text(
            "STDOUT\n" + created.stdout + "STDERR\n" + created.stderr,
            encoding="utf-8",
        )
        creation_output = parse_json(created.stdout)
        creation_result = creation_output.get("result", {})
        checkpoint_bytes = checkpoint_path.stat().st_size if checkpoint_path.is_file() else 0
        checkpoint_allocated = allocated_bytes(checkpoint_path) if checkpoint_path.is_file() else 0
        checkpoint_pass = (
            created.returncode == 0
            and creation_result.get("checkpoint_kind") == requirements["checkpoint_kind"]
            and creation_result.get("semantic_cursor") == requirements["checkpoint_semantic_cursor"]
            and creation_result.get("governance_cursor") == requirements["checkpoint_governance_cursor"]
            and creation_result.get("checkpoint_bytes") == checkpoint_bytes
            and creation_result.get("canonical_replay_source") is False
            and creation_result.get("authority_effect") == "none"
            and checkpoint_bytes <= requirements["maximum_checkpoint_bytes"]
            and checkpoint_allocated <= requirements["maximum_checkpoint_allocated_bytes"]
            and creation_ns <= requirements["maximum_checkpoint_creation_ns"]
            and creation_resource.get("timed_out") is False
            and creation_resource.get("maximum_rss_kib", 0) <= requirements["maximum_checkpoint_creation_peak_rss_kib"]
        )
        fixture_evidence = {
            **fixture_receipt,
            "result": "PASS" if fixture_pass and checkpoint_pass else "BLOCK",
            "preflight": preflight,
            "semantic_event_file_count": semantic_files,
            "governance_event_file_count": governance_files,
            "logical_event_bytes": logical_bytes,
            "allocated_fixture_bytes": fixture_allocated,
            "generation_process_ns": generation_ns,
            "generation_resource_measurement": generation_resource,
            "checkpoint_creation": {
                **creation_result,
                "process_elapsed_ns": creation_ns,
                "resource_measurement": creation_resource,
                "checkpoint_file_sha256": digest_file(checkpoint_path) if checkpoint_path.is_file() else None,
                "checkpoint_allocated_bytes": checkpoint_allocated,
                "result": "PASS" if checkpoint_pass else "BLOCK",
            },
            "runtime_digest_sha256": current_runtime,
            "generator_digest_sha256": current_generator,
            "experiment_digest_sha256": current_experiment,
        }
        write_json(fixture_path, fixture_evidence)
        if not fixture_pass or not checkpoint_pass:
            raise SystemExit("fixture or checkpoint construction failed")

        attempts: dict[str, list[dict[str, Any]]] = {"full-replay": [], "checkpoint-tail": []}
        for attempt in attempt_ids:
            strategy_order = (
                ("full-replay", "checkpoint-tail")
                if attempt % 2 == 1
                else ("checkpoint-tail", "full-replay")
            )
            for strategy in strategy_order:
                evidence_path = evidence_paths[strategy][attempt - 1]
                arguments = (
                    [str(recovery), "recover-files", str(fixture / "semantic-events"), str(fixture / "governance-events"), str(expectation_path)]
                    if strategy == "full-replay"
                    else [
                        str(recovery), "recover-checkpoint-tail", str(checkpoint_path),
                        str(fixture / "semantic-events"), str(fixture / "governance-events"),
                        str(expectation_path), str(requirements["subject_count"]),
                    ]
                )
                completed, elapsed_ns, measured = measured_run(
                    arguments,
                    HERE / f"raw-logs/{strategy}-attempt-{attempt}.time",
                    hard_limit,
                    requirements["maximum_process_recovery_ns"],
                )
                output = parse_json(completed.stdout)
                passed = completed.returncode == 0 and recovery_pass(
                    output, expected, elapsed_ns, measured, requirements, strategy == "checkpoint-tail"
                )
                record = {
                    "schema_version": "cal-checkpoint-recovery-attempt/v1-prototype",
                    "profile_id": args.profile,
                    "strategy": strategy,
                    "attempt": attempt,
                    "result": "PASS" if passed else "BLOCK",
                    "process_elapsed_ns": elapsed_ns,
                    "resource_measurement": measured,
                    "normalized_recovery_digest_sha256": normalized_recovery_digest(output),
                    "recovery_result": output.get("result", {}),
                    "fixture_receipt_sha256": digest_file(fixture_path),
                    "runtime_digest_sha256": current_runtime,
                    "generator_digest_sha256": current_generator,
                    "experiment_digest_sha256": current_experiment,
                    "exit": completed.returncode,
                    "canonical_replay_source": False,
                    "authority_effect": "none",
                }
                write_json(evidence_path, record)
                (HERE / f"raw-logs/{strategy}-attempt-{attempt}.log").write_text(
                    "STDOUT\n" + completed.stdout + "STDERR\n" + completed.stderr,
                    encoding="utf-8",
                )
                attempts[strategy].append(record)

        controls: dict[str, dict[str, Any]] = {}
        bad_canonical = temporary_path / "checkpoint-noncanonical.json"
        bad_canonical.write_bytes(b" " + checkpoint_path.read_bytes())
        stale_digest = temporary_path / "checkpoint-stale-digest.json"
        stale_value = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        stale_value["body"]["base_expectation"]["expected_index_digest"] = "0" * 64
        stale_digest.write_text(
            json.dumps(stale_value, separators=(",", ":")) + "\n", encoding="utf-8"
        )
        control_inputs = (
            ("noncanonical-checkpoint", bad_canonical, "CHECKPOINT_NON_CANONICAL_JSON"),
            ("stale-checkpoint-body-digest", stale_digest, "CHECKPOINT_BODY_DIGEST_MISMATCH"),
        )
        for name, selected_checkpoint, expected_code in control_inputs:
            completed = subprocess.run(
                [
                    str(recovery), "recover-checkpoint-tail", str(selected_checkpoint),
                    str(fixture / "semantic-events"), str(fixture / "governance-events"),
                    str(expectation_path), str(requirements["subject_count"]),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            error = parse_json(completed.stderr)
            controls[name] = {
                "result": "PASS" if completed.returncode != 0 and error.get("code") == expected_code else "BLOCK",
                "exit": completed.returncode,
                "code": error.get("code"),
                "expected_code": expected_code,
            }

        first_tail = fixture / "semantic-events" / f"{requirements['checkpoint_semantic_cursor'] + 1:08d}-synthetic-semantic-{requirements['checkpoint_semantic_cursor'] + 1:08d}.json"
        first_tail.write_bytes(b" " + first_tail.read_bytes())
        tail_control = subprocess.run(
            [
                str(recovery), "recover-checkpoint-tail", str(checkpoint_path),
                str(fixture / "semantic-events"), str(fixture / "governance-events"),
                str(expectation_path), str(requirements["subject_count"]),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        tail_error = parse_json(tail_control.stderr)
        controls["noncanonical-tail-event"] = {
            "result": "PASS" if tail_control.returncode != 0 and tail_error.get("code") == "NON_CANONICAL_JSON" else "BLOCK",
            "exit": tail_control.returncode,
            "code": tail_error.get("code"),
            "expected_code": "NON_CANONICAL_JSON",
        }
    fixture_removed = not fixture.exists()
    checkpoint_removed = not checkpoint_path.exists()

    deterministic = {
        strategy: len({item["normalized_recovery_digest_sha256"] for item in records}) == 1
        for strategy, records in attempts.items()
    }
    medians = {
        strategy: int(statistics.median(item["process_elapsed_ns"] for item in records))
        for strategy, records in attempts.items()
    }
    checkpoint_pair_wins = sum(
        checkpoint["process_elapsed_ns"] < full["process_elapsed_ns"]
        for checkpoint, full in zip(
            attempts["checkpoint-tail"], attempts["full-replay"], strict=True
        )
    )
    performance_benefit_supported = (
        medians["checkpoint-tail"] < medians["full-replay"]
        and checkpoint_pair_wins >= requirements["minimum_checkpoint_pair_wins"]
    )
    checkpoint_to_full_median_ratio = (
        medians["checkpoint-tail"] / medians["full-replay"]
    )
    performance_bound_pass = (
        checkpoint_to_full_median_ratio
        <= requirements["maximum_checkpoint_to_full_median_ratio"]
    )
    passed = (
        all(item["result"] == "PASS" for records in attempts.values() for item in records)
        and all(deterministic.values())
        and performance_bound_pass
        and all(control["result"] == "PASS" for control in controls.values())
        and fixture_removed
        and checkpoint_removed
    )
    now = datetime.now(timezone.utc).replace(microsecond=0)
    report = {
        "schema_version": "cal-checkpoint-tail-recovery-report/v1-prototype",
        "profile_id": "cal-checkpoint-tail-recovery/v1",
        "regime_id": args.profile,
        "run_at_utc": now.isoformat().replace("+00:00", "Z"),
        "result": "PASS" if passed else "BLOCK",
        "quality_bar_status": "pass" if passed else "fail",
        "anti_pattern_hits": [],
        "workflow_gaps": [
            "the fixture is synthetic rather than a representative production workload",
            "checkpoint creation currently loads the complete event store",
            "checkpoint process-interruption replacement is measured separately; sudden-power-loss durability remains undefined",
            "sustained ingestion, backpressure, and multi-writer ordering remain undefined",
        ],
        "runtime_digest_sha256": current_runtime,
        "generator_digest_sha256": current_generator,
        "experiment_digest_sha256": current_experiment,
        "resource_requirements_sha256": digest_file(REQUIREMENTS_PATH),
        "fixture": {"path": str(fixture_path.relative_to(HERE)), "sha256": digest_file(fixture_path)},
        "attempt_count_per_strategy": requirements["attempt_count_per_strategy"],
        "attempts": {
            strategy: [
                {
                    "path": str(path.relative_to(HERE)),
                    "sha256": digest_file(path),
                    "process_elapsed_ns": record["process_elapsed_ns"],
                    "maximum_rss_kib": record["resource_measurement"].get("maximum_rss_kib"),
                    "result": record["result"],
                }
                for path, record in zip(evidence_paths[strategy], records, strict=True)
            ]
            for strategy, records in attempts.items()
        },
        "deterministic_normalized_receipt": deterministic,
        "median_process_elapsed_ns": medians,
        "checkpoint_median_speedup_ratio": medians["full-replay"] / medians["checkpoint-tail"],
        "checkpoint_to_full_median_ratio": checkpoint_to_full_median_ratio,
        "checkpoint_median_faster_than_full_replay": medians["checkpoint-tail"]
        < medians["full-replay"],
        "checkpoint_performance_benefit_supported": performance_benefit_supported,
        "checkpoint_performance_within_bound": performance_bound_pass,
        "checkpoint_pair_wins": checkpoint_pair_wins,
        "minimum_checkpoint_pair_wins": requirements["minimum_checkpoint_pair_wins"],
        "maximum_checkpoint_to_full_median_ratio": requirements[
            "maximum_checkpoint_to_full_median_ratio"
        ],
        "controls": controls,
        "temporary_fixture_removed": fixture_removed,
        "temporary_checkpoint_removed": checkpoint_removed,
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": "local_synthetic_50000_subject_disposable_checkpoint_evidence_only",
    }
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    report_path = HERE / f"runs/{stamp}-large.json"
    write_json(report_path, report)
    write_json(HERE / "runs/latest-large.json", report)
    print(json.dumps({
        "mode": "run",
        "profile": args.profile,
        "status": report["quality_bar_status"],
        "report": str(report_path),
        "checkpoint_median_speedup_ratio": report["checkpoint_median_speedup_ratio"],
        "observation": "skipped-no-repository-observability-binding",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Dependency-free semantic validator for append-only benchmark JSONL."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_BACKENDS = {"rust_scan_control", "rust_spo_pos_index"}


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_scalars = {
        "record_type": "benchmark_run",
        "benchmark_id": "CAL-GRAPH-READ-MODEL-BENCHMARK-001",
        "status": "pass",
        "canonical_authority": "canonical events only; every read model is disposable and rebuildable",
        "claim_ceiling": "local_single_process_experiment_only",
    }
    for key, expected in expected_scalars.items():
        if record.get(key) != expected:
            errors.append(f"{key}: expected {expected!r}")
    schema_version = record.get("schema_version")
    if schema_version not in {"1.0.0", "1.1.0"}:
        errors.append("schema_version: expected 1.0.0 or 1.1.0")

    config = record.get("config", {})
    for key in ("node_count", "relation_edges_per_node", "query_count", "repetitions"):
        if not isinstance(config.get(key), int) or config[key] < 1:
            errors.append(f"config.{key}: expected positive integer")
    if isinstance(config.get("node_count"), int) and isinstance(config.get("relation_edges_per_node"), int):
        expected_triples = config["node_count"] * (config["relation_edges_per_node"] + 2)
        if record.get("triple_count") != expected_triples:
            errors.append(f"triple_count: expected {expected_triples}")
    if isinstance(config.get("query_count"), int) and isinstance(config.get("repetitions"), int):
        expected_executions = config["query_count"] * config["repetitions"]
        if record.get("query_executions_per_backend") != expected_executions:
            errors.append(f"query_executions_per_backend: expected {expected_executions}")

    for path, value in (
        ("fixture_digest_sha256", record.get("fixture_digest_sha256")),
        (
            "correctness.shared_result_digest_sha256",
            record.get("correctness", {}).get("shared_result_digest_sha256"),
        ),
    ):
        if not isinstance(value, str) or not SHA256.fullmatch(value):
            errors.append(f"{path}: expected lowercase SHA-256")
    interop_digest = record.get("correctness", {}).get("interop_result_digest_sha256")
    if schema_version == "1.1.0" and (
        not isinstance(interop_digest, str) or not SHA256.fullmatch(interop_digest)
    ):
        errors.append("correctness.interop_result_digest_sha256: expected lowercase SHA-256")

    correctness = record.get("correctness", {})
    if correctness.get("status") != "pass":
        errors.append("correctness.status: expected pass")
    if set(correctness.get("compared_backends", [])) != EXPECTED_BACKENDS:
        errors.append("correctness.compared_backends: missing required controls")
    if correctness.get("query_results_compared") != config.get("query_count"):
        errors.append("correctness.query_results_compared: must equal config.query_count")

    backends = record.get("backends", [])
    by_id = {backend.get("backend_id"): backend for backend in backends if isinstance(backend, dict)}
    if not EXPECTED_BACKENDS.issubset(by_id):
        errors.append("backends: missing required controls")
    else:
        digests = set()
        for backend_id in EXPECTED_BACKENDS:
            backend = by_id[backend_id]
            if backend.get("status") != "pass":
                errors.append(f"backends.{backend_id}.status: expected pass")
            digest = backend.get("result_digest_sha256")
            if not isinstance(digest, str) or not SHA256.fullmatch(digest):
                errors.append(f"backends.{backend_id}.result_digest_sha256: invalid")
            else:
                digests.add(digest)
        if len(digests) != 1:
            errors.append("backends: result digests differ; timing is inadmissible")

    external = record.get("external_backends", [])
    wavedb = next((item for item in external if item.get("backend_id") == "wavedb_graph"), None)
    if wavedb is None:
        errors.append("external_backends: WaveDB lane must not be omitted")
    elif wavedb.get("status") not in {"pass", "fail", "not_evaluable"}:
        errors.append("external_backends.wavedb_graph.status: invalid")
    elif wavedb.get("status") != "pass" and not wavedb.get("blocker"):
        errors.append("external_backends.wavedb_graph.blocker: required when not pass")
    return errors


def validate_file(path: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    records = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        records += 1
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON: {exc}")
            continue
        errors.extend(f"line {line_number}: {error}" for error in validate_record(record))
    if records == 0:
        errors.append("no benchmark records")
    return records, errors


def self_test(root: Path) -> int:
    pass_records, pass_errors = validate_file(root / "fixtures" / "pass.jsonl")
    _, fail_errors = validate_file(root / "fixtures" / "fail-mismatched-results.jsonl")
    if pass_records != 1 or pass_errors:
        print(json.dumps({"status": "fail", "fixture": "pass", "errors": pass_errors}))
        return 1
    if not any("result digests differ" in error for error in fail_errors):
        print(json.dumps({"status": "fail", "fixture": "fail-mismatched-results", "errors": fail_errors}))
        return 1
    print(json.dumps({"status": "pass", "passing_fixture": "accepted", "failing_fixture": "rejected"}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if args.self_test:
        return self_test(root)
    if args.path is None:
        parser.error("path is required unless --self-test is used")
    records, errors = validate_file(args.path)
    print(json.dumps({"status": "pass" if not errors else "fail", "records": records, "errors": errors}))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

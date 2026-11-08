#!/usr/bin/env python3
"""Compare a WaveDB run with the correctness and timing Rust receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def last_record(path: Path) -> dict[str, Any]:
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not records:
        raise ValueError(f"no records in {path}")
    return records[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rust-timing", required=True, type=Path)
    parser.add_argument("--rust-correctness", required=True, type=Path)
    parser.add_argument("--wavedb", required=True, type=Path)
    args = parser.parse_args()

    rust_timing = last_record(args.rust_timing)
    rust_correctness = last_record(args.rust_correctness)
    wavedb = last_record(args.wavedb)
    indexed = next(
        backend
        for backend in rust_timing["backends"]
        if backend["backend_id"] == "rust_spo_pos_index"
    )
    same_workload = (
        wavedb["node_count"] == rust_correctness["config"]["node_count"]
        and wavedb["triple_count"] == rust_correctness["triple_count"]
        and wavedb["query_count"] == rust_correctness["config"]["query_count"]
        and wavedb["repetitions"] == rust_timing["config"]["repetitions"]
    )
    digest_match = (
        wavedb["interop_result_digest_sha256"]
        == rust_correctness["correctness"]["interop_result_digest_sha256"]
    )
    ratios = {
        family: wavedb["latency_by_query"][family]["p50_ns"] / summary["p50_ns"]
        for family, summary in indexed["latency_by_query"].items()
    }
    result = {
        "record_type": "benchmark_adjudication",
        "schema_version": "1.0.0",
        "benchmark_id": "CAL-GRAPH-READ-MODEL-BENCHMARK-001",
        "status": "pass" if same_workload and digest_match else "fail",
        "same_workload": same_workload,
        "correctness_digest_match": digest_match,
        "wavedb_build_over_rust_index_ratio": wavedb["build_ns"] / indexed["build_ns"],
        "wavedb_p50_over_rust_index_ratio": ratios,
        "wavedb_lifecycle_status": wavedb["lifecycle_status"],
        "wavedb_adoption_status": wavedb["adoption_status"],
        "recommendation": "retain_rust_index_and_reject_wavedb_for_current_product",
        "claim_ceiling": "local_single_process_synthetic_experiment_only",
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PROFILES = ("smoke", "medium", "large")
EXPECTED_COUNTS = {
    "smoke": (1000, 4000, 5000),
    "medium": (10000, 40000, 50000),
    "large": (50000, 200000, 250000),
}
RECEIPT = HERE / "validation.json"
IMPLEMENTATION_FILES = (
    "../src/lib.rs",
    "src/main.rs",
    "profiles.json",
    "Cargo.lock",
    "../Cargo.lock",
    "../../../../runtime/src/lib.rs",
)
SOURCE_FILES = (
    ".gitignore",
    "Cargo.toml",
    "Cargo.lock",
    "EXPERIMENT-PROFILE.md",
    "PROTOCOL.md",
    "RESULTS.md",
    "profiles.json",
    "run.py",
    "schemas/benchmark-attempt.schema.json",
    "src/main.rs",
    "validate.py",
    "../recovery-requirements.json",
    "../recovery-requirements.schema.json",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def implementation_digest() -> str:
    hasher = hashlib.sha256()
    for relative in IMPLEMENTATION_FILES:
        hasher.update(relative.encode())
        hasher.update(b"\0")
        hasher.update((HERE / relative).read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def one_record(path: Path) -> dict[str, Any]:
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if len(records) != 1:
        raise ValueError(f"expected one record in {path}; got {len(records)}")
    return records[0]


def main() -> int:
    current_implementation = implementation_digest()
    profile_checks = []
    for profile in PROFILES:
        attempts = [one_record(HERE / f"evidence/{profile}-attempt-{attempt}.jsonl") for attempt in (1, 2)]
        latest_path = HERE / f"runs/latest-{profile}.json"
        latest = json.loads(latest_path.read_text(encoding="utf-8"))
        expected_nodes, expected_relations, expected_subjects = EXPECTED_COUNTS[profile]
        deterministic = all(
            len({item[field] for item in attempts}) == 1
            for field in (
                "implementation_digest_sha256",
                "fixture_digest_sha256",
                "candidate_index_digest_sha256",
            )
        ) and len({item["correctness"]["shared_result_digest_sha256"] for item in attempts}) == 1 \
          and len({item["calculated_delta"]["target_projection_digest_sha256"] for item in attempts}) == 1 \
          and len({item["calculated_delta"]["resulting_index_digest_sha256"] for item in attempts}) == 1 \
          and len({item["calculated_delta"]["delta_digest_sha256"] for item in attempts}) == 1 \
          and len({item["concurrent_snapshots"]["published_index_digest_sha256"] for item in attempts}) == 1 \
          and len({item["restart_recovery"]["recovered_index_digest_sha256"] for item in attempts}) == 1
        hashes_match = all(
            latest["attempt_evidence"][index - 1]["sha256"]
            == digest(HERE / f"evidence/{profile}-attempt-{index}.jsonl")
            for index in (1, 2)
        )
        passed = (
            all(item["status"] == "pass" for item in attempts)
            and all(item["correctness"]["status"] == "pass" for item in attempts)
            and all(item["implementation_digest_sha256"] == current_implementation for item in attempts)
            and all(item["generated_node_count"] == expected_nodes for item in attempts)
            and all(item["generated_relation_count"] == expected_relations for item in attempts)
            and all(item["generated_subject_count"] == expected_subjects for item in attempts)
            and all(item["calculated_delta"]["exact_model_equivalence"] is True for item in attempts)
            and all(item["calculated_delta"]["transaction_strategy"] == "bounded_rollback_journal" for item in attempts)
            and all(item["calculated_delta"]["full_model_clone"] is False for item in attempts)
            and all(item["calculated_delta"]["staged_previous_subject_count"] < expected_subjects for item in attempts)
            and all(item["concurrent_snapshots"]["publication_strategy"] == "structurally_shared_arc_snapshot" for item in attempts)
            and all(item["concurrent_snapshots"]["invalid_observations"] == 0 for item in attempts)
            and all(item["concurrent_snapshots"]["writer_completed_while_old_snapshot_held"] is True for item in attempts)
            and all(item["concurrent_snapshots"]["old_snapshot_retained_after_publication"] is True for item in attempts)
            and all(item["concurrent_snapshots"]["publication_staged_full_model_clone"] is False for item in attempts)
            and all(0 < item["concurrent_snapshots"]["shared_subject_count"] < item["concurrent_snapshots"]["previous_subject_count"] for item in attempts)
            and all(0 < item["concurrent_snapshots"]["shared_challenge_contract_count"] < item["concurrent_snapshots"]["previous_challenge_contract_count"] for item in attempts)
            and all(0 < item["concurrent_snapshots"]["shared_index_bucket_count"] < item["concurrent_snapshots"]["previous_index_bucket_count"] for item in attempts)
            and all(item["concurrent_snapshots"]["published_generation"] == 1 for item in attempts)
            and all(item["concurrent_snapshots"]["exact_final_model_equivalence"] is True for item in attempts)
            and all(item["restart_recovery"]["recovery_strategy"] == "full_rebuild_from_verified_calculated_cut" for item in attempts)
            and all(item["restart_recovery"]["within_objective"] is True for item in attempts)
            and all(item["restart_recovery"]["exact_model_equivalence"] is True for item in attempts)
            and all(item["restart_recovery"]["exact_index_digest_match"] is True for item in attempts)
            and all(item["restart_recovery"]["checkpoint_used"] is False for item in attempts)
            and all(item["restart_recovery"]["corruption_controls_in_test_suite"] >= 4 for item in attempts)
            and all(item["restart_recovery"]["cold_recovery_ns"] <= item["restart_recovery"]["maximum_cold_recovery_ns"] for item in attempts)
            and deterministic
            and hashes_match
            and latest["status"] == "pass"
            and latest["correctness"]["implementation_digest_sha256"] == current_implementation
            and latest["canonical_replay_source"] is False
            and latest["authority_effect"] == "none"
        )
        profile_checks.append({
            "profile": profile,
            "result": "PASS" if passed else "BLOCK",
            "attempt_count": len(attempts),
            "source_bound": all(item["implementation_digest_sha256"] == current_implementation for item in attempts),
            "deterministic": deterministic,
            "latest_report_sha256": digest(latest_path),
            "attempt_hashes_match_latest_report": hashes_match,
        })

    compiled = subprocess.run(
        ["cargo", "test", "--locked"],
        cwd=HERE,
        env={**os.environ, "CARGO_TARGET_DIR": str(HERE / "target")},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    passed = all(item["result"] == "PASS" for item in profile_checks) and compiled.returncode == 0
    receipt = {
        "schema_version": "cal-ontology-graph-benchmark-validation/v1",
        "benchmark_id": "CAL-ONTOLOGY-GRAPH-READ-MODEL-BENCHMARK-002",
        "result": "PASS" if passed else "BLOCK",
        "claim": "source-bound local synthetic prototype evidence only",
        "implementation_digest_sha256": current_implementation,
        "profile_checks": profile_checks,
        "compile_check": {
            "result": "PASS" if compiled.returncode == 0 else "BLOCK",
            "exit": compiled.returncode,
            "stderr_tail": compiled.stderr[-3000:] if compiled.returncode else "",
        },
        "source_manifest": [
            {"path": relative, "sha256": digest(HERE / relative)}
            for relative in SOURCE_FILES
        ],
        "authority_effect": "none",
        "forbidden_claims_preserved": [
            "production readiness",
            "concurrent correctness",
            "durability",
            "crash recovery",
            "product approval",
            "ontology admission",
            "runtime activation",
            "publication",
            "cutover",
        ],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

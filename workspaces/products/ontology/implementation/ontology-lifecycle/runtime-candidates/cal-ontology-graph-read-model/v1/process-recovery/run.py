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
ONTOLOGY_LIFECYCLE = CANDIDATE.parents[2]
FIXTURE = ONTOLOGY_LIFECYCLE / "migration/cal-w7-ontology-product-epoch-001/fixtures/output"
SEMANTIC = FIXTURE / "semantic-events"
GOVERNANCE = FIXTURE / "governance-events"
EXPECTATION = CANDIDATE / "recovery-expectation-w7.json"
REQUIREMENTS = CANDIDATE / "recovery-requirements.json"
RUNTIME_SOURCE = ONTOLOGY_LIFECYCLE / "runtime/src/lib.rs"
ATTEMPTS = 2


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


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


def invoke(binary: Path, semantic: Path, governance: Path, expectation: Path) -> tuple[subprocess.CompletedProcess[str], int]:
    started = time.perf_counter_ns()
    completed = subprocess.run(
        [str(binary), "recover-files", str(semantic), str(governance), str(expectation)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed, time.perf_counter_ns() - started


def parse_error(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        return json.loads(completed.stderr)
    except json.JSONDecodeError:
        return {}


def normalized_output_digest(output: dict[str, Any]) -> str:
    normalized = json.loads(json.dumps(output))
    result = normalized.get("result", {})
    result.pop("event_store_load_ns", None)
    result.pop("graph_rebuild_ns", None)
    return digest_bytes(
        json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()
    evidence_paths = [HERE / f"evidence/w7-event-files-attempt-{attempt}.json" for attempt in (1, 2)]
    if not args.rerun and any(path.exists() for path in evidence_paths):
        raise SystemExit("attempt evidence exists; pass --rerun to replace the exact process epoch")

    requirements = json.loads(REQUIREMENTS.read_text(encoding="utf-8"))
    objective = requirements["canonical_event_file_process_objective"]
    expectation = json.loads(EXPECTATION.read_text(encoding="utf-8"))
    semantic_digest = digest_tree(SEMANTIC)
    governance_digest = digest_tree(GOVERNANCE)
    implementation = runtime_digest()
    experiment = experiment_digest()

    with tempfile.TemporaryDirectory(prefix="cal-process-recovery-") as temporary:
        temporary_path = Path(temporary)
        target = temporary_path / "target"
        build = subprocess.run(
            ["cargo", "build", "--release", "--locked", "--bin", "cal-ontology-graph-read-model"],
            cwd=CANDIDATE,
            env={**os.environ, "CARGO_TARGET_DIR": str(target)},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if build.returncode != 0:
            raise SystemExit("locked release build failed: " + build.stderr[-2000:])
        binary = target / "release/cal-ontology-graph-read-model"
        attempts = []
        for attempt, evidence_path in zip((1, 2), evidence_paths, strict=True):
            completed, elapsed = invoke(binary, SEMANTIC, GOVERNANCE, EXPECTATION)
            try:
                output = json.loads(completed.stdout)
            except json.JSONDecodeError:
                output = {}
            passed = (
                completed.returncode == 0
                and elapsed <= objective["maximum_elapsed_ns"]
                and output.get("command") == "recover-files"
                and output.get("result", {}).get("recovery_strategy")
                == "full_rebuild_from_canonical_event_files"
                and output.get("result", {}).get("semantic_cursor") == expectation["semantic_cursor"]
                and output.get("result", {}).get("source_event_count") == expectation["source_event_count"]
                and output.get("result", {}).get("source_event_set_digest")
                == expectation["source_event_set_digest"]
                and output.get("result", {}).get("rebuilt_index_digest")
                == expectation["expected_index_digest"]
                and output.get("result", {}).get("checkpoint_used") is False
                and isinstance(output.get("result", {}).get("event_store_load_ns"), int)
                and output["result"]["event_store_load_ns"] > 0
                and isinstance(output.get("result", {}).get("graph_rebuild_ns"), int)
                and output["result"]["graph_rebuild_ns"] > 0
                and output["result"]["event_store_load_ns"]
                + output["result"]["graph_rebuild_ns"]
                <= elapsed
            )
            record = {
                "schema_version": "cal-event-file-process-recovery-attempt/v1-prototype",
                "attempt": attempt,
                "result": "PASS" if passed else "BLOCK",
                "elapsed_ns": elapsed,
                "event_store_load_ns": output.get("result", {}).get("event_store_load_ns"),
                "graph_rebuild_ns": output.get("result", {}).get("graph_rebuild_ns"),
                "maximum_elapsed_ns": objective["maximum_elapsed_ns"],
                "implementation_digest_sha256": implementation,
                "experiment_digest_sha256": experiment,
                "semantic_event_directory_digest_sha256": semantic_digest,
                "governance_event_directory_digest_sha256": governance_digest,
                "output": output,
                "exit": completed.returncode,
                "canonical_replay_source": False,
                "authority_effect": "none",
            }
            evidence_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            (HERE / f"raw-logs/w7-event-files-attempt-{attempt}.log").write_text(
                "STDOUT\n" + completed.stdout + "STDERR\n" + completed.stderr,
                encoding="utf-8",
            )
            attempts.append(record)

        missing, _ = invoke(binary, temporary_path / "missing-semantic", GOVERNANCE, EXPECTATION)
        changed = dict(expectation)
        changed["expected_index_digest"] = "0" * 64
        changed_path = temporary_path / "changed-expectation.json"
        changed_path.write_text(json.dumps(changed), encoding="utf-8")
        wrong_digest, _ = invoke(binary, SEMANTIC, GOVERNANCE, changed_path)
        controls = {
            "missing_event_directory": {
                "result": "PASS"
                if missing.returncode != 0
                and parse_error(missing).get("code") == "EVENT_DIRECTORY_READ_FAILED"
                else "BLOCK",
                "exit": missing.returncode,
                "code": parse_error(missing).get("code"),
            },
            "wrong_expected_index_digest": {
                "result": "PASS"
                if wrong_digest.returncode != 0
                and parse_error(wrong_digest).get("code") == "RECOVERY_INDEX_DIGEST_MISMATCH"
                else "BLOCK",
                "exit": wrong_digest.returncode,
                "code": parse_error(wrong_digest).get("code"),
            },
        }

    output_digests = {normalized_output_digest(item["output"]) for item in attempts}
    passed = (
        all(item["result"] == "PASS" for item in attempts)
        and len(output_digests) == 1
        and all(item["result"] == "PASS" for item in controls.values())
    )
    now = datetime.now(timezone.utc).replace(microsecond=0)
    report = {
        "schema_version": "cal-event-file-process-recovery-report/v1-prototype",
        "profile_id": "cal-ontology-event-file-process-recovery/v1",
        "regime_id": "w7-event-files",
        "run_at_utc": now.isoformat().replace("+00:00", "Z"),
        "result": "PASS" if passed else "BLOCK",
        "quality_bar_status": "pass" if passed else "fail",
        "anti_pattern_hits": [],
        "workflow_gaps": [
            "this regime proves the frozen 47-event W7 fixture only",
            "generated canonical-format recovery is measured separately and stops at 50000 subjects",
            "no checkpoint, crash-consistency, or durability workload",
        ],
        "implementation_digest_sha256": implementation,
        "experiment_digest_sha256": experiment,
        "semantic_event_directory_digest_sha256": semantic_digest,
        "governance_event_directory_digest_sha256": governance_digest,
        "attempt_count": len(attempts),
        "attempts": [
            {
                "path": str(path.relative_to(HERE)),
                "sha256": digest_file(path),
                "elapsed_ns": attempt["elapsed_ns"],
                "event_store_load_ns": attempt["event_store_load_ns"],
                "graph_rebuild_ns": attempt["graph_rebuild_ns"],
                "result": attempt["result"],
            }
            for path, attempt in zip(evidence_paths, attempts, strict=True)
        ],
        "deterministic_output": len(output_digests) == 1,
        "failure_controls": controls,
        "canonical_replay_source": False,
        "authority_effect": "none",
        "claim_ceiling": "frozen_w7_local_process_recovery_prototype_evidence_only",
    }
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    body = json.dumps(report, indent=2, sort_keys=True) + "\n"
    report_path = HERE / f"runs/{stamp}-w7-event-files.json"
    report_path.write_text(body, encoding="utf-8")
    (HERE / "runs/latest-w7-event-files.json").write_text(body, encoding="utf-8")
    print(body, end="")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

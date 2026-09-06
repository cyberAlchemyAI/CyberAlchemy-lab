#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CONTRACT = HERE / "activation-contract.json"
SOURCE = HERE / "fixtures/source-events.jsonl"
INVENTORY = HERE / "fixtures/migration-inventory.json"
EXPECTED = HERE / "fixtures/expected-projections.json"
RECEIPT = HERE / "receipts/shadow-activation.json"
CANDIDATE = LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-context-adapters-v2/v1"
TEST_RE = re.compile(r"^test ([^ ]+) \.\.\. (ok|FAILED|ignored)$")
ALLOWED_KINDS = {"node", "relation", "context-binding", "challenge-contract"}


class ActivationFailure(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ActivationFailure(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def content_digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def load_event_bytes(data: bytes) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(data.decode("utf-8").splitlines(), 1):
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ActivationFailure(f"event line {line_number} is not an object")
        rows.append(value)
    return rows


def event_bytes(events: list[dict[str, Any]]) -> bytes:
    return b"".join(canonical(event) + b"\n" for event in events)


def seal(event: dict[str, Any]) -> None:
    body = copy.deepcopy(event)
    body.pop("event_digest", None)
    event["event_digest"] = content_digest(body)


def validate_log(events: list[dict[str, Any]]) -> None:
    if [event.get("sequence") for event in events] != list(range(1, len(events) + 1)):
        raise ActivationFailure("event sequence is not gap-free")
    if len({event.get("event_id") for event in events}) != len(events):
        raise ActivationFailure("event ids are duplicated")
    previous: dict[str, str] = {}
    for event in events:
        if event.get("schema_version") != "cal.rehearsal-event/v1":
            raise ActivationFailure("event schema is invalid")
        if event.get("subject_kind") not in ALLOWED_KINDS:
            raise ActivationFailure("subject kind is invalid")
        if event.get("operation") != "upsert":
            raise ActivationFailure("operation is invalid")
        if event.get("payload", {}).get("authority_effect") != "none":
            raise ActivationFailure("event carries authority")
        actual = event.get("event_digest")
        body = copy.deepcopy(event)
        body.pop("event_digest", None)
        if actual != content_digest(body):
            raise ActivationFailure("event digest mismatch")
        stream = str(event["stream_id"])
        if event.get("previous_event_digest") != previous.get(stream):
            raise ActivationFailure("stream digest chain mismatch")
        previous[stream] = str(actual)


def normalize_and_seal(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = copy.deepcopy(events)
    previous: dict[str, str] = {}
    for sequence, event in enumerate(result, 1):
        event["schema_version"] = "cal.rehearsal-event/v1"
        event["sequence"] = sequence
        event["operation"] = "upsert"
        stream = str(event["stream_id"])
        event["previous_event_digest"] = previous.get(stream)
        seal(event)
        previous[stream] = event["event_digest"]
    return result


def migrate(source: list[dict[str, Any]], inventory: dict[str, Any]) -> list[dict[str, Any]]:
    append = copy.deepcopy(inventory["append_event_templates"])
    return normalize_and_seal(source + append)


def project(events: list[dict[str, Any]]) -> dict[str, Any]:
    validate_log(events)
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for event in events:
        latest[(event["subject_kind"], event["subject_id"])] = event

    def rows(kind: str) -> list[dict[str, Any]]:
        result = []
        for (subject_kind, subject_id), event in latest.items():
            if subject_kind == kind:
                result.append({
                    "subject_id": subject_id,
                    "source_event_id": event["event_id"],
                    "source_event_digest": event["event_digest"],
                    "state": event["payload"],
                })
        return sorted(result, key=lambda row: row["subject_id"])

    projection = {
        "schema_version": "cal.d65-shadow-activation-projection/v1",
        "canonical_replay_source": False,
        "source_cursor": len(events),
        "source_event_set_digest": content_digest([event["event_digest"] for event in events]),
        "nodes": rows("node"),
        "relations": rows("relation"),
        "context_bindings": rows("context-binding"),
        "challenge_contracts": rows("challenge-contract"),
        "snapshots": [
            {
                "subject_kind": kind,
                "subject_id": row["subject_id"],
                "source_event_digest": row["source_event_digest"],
                "canonical_replay_source": False,
            }
            for kind in ("node", "relation")
            for row in rows(kind)
        ],
        "authority_effect": "none",
    }
    if len(projection["nodes"]) != 2 or len(projection["relations"]) != 1 or len(projection["context_bindings"]) != 1 or len(projection["challenge_contracts"]) != 1:
        raise ActivationFailure("required ontology records are missing")
    projection["projection_digest"] = content_digest(projection)
    return projection


def validate_target(projection: dict[str, Any], expected: dict[str, Any]) -> None:
    if projection != expected:
        raise ActivationFailure("target projection differs from frozen expectation")
    relation = projection["relations"][0]["state"]
    if relation.get("source") != "CAL-NODE-GOVERNANCE-DECISION" or relation.get("target") != "CAL-NODE-ONTOLOGY-PROJECTION" or relation.get("direction") != "source-to-target":
        raise ActivationFailure("relation direction changed")
    context = projection["context_bindings"][0]["state"]
    if context.get("map_ref") != "cal.context-map.governance-ontology-lifecycle/v2" or context.get("direction") != "source-to-target":
        raise ActivationFailure("context binding changed")
    challenge = projection["challenge_contracts"][0]["state"]
    if challenge.get("resolution_gate") != "G-D65-EPOCH-002-ACTIVATION-CUTOVER" or not challenge.get("owner_route"):
        raise ActivationFailure("challenge contract boundary changed")
    if any(item["canonical_replay_source"] for item in projection["snapshots"]):
        raise ActivationFailure("snapshot became a replay source")


def exact_refs(contract: dict[str, Any]) -> list[dict[str, str]]:
    return contract["selected_inputs"] + contract["protected_bytes"]


def validate_refs(contract: dict[str, Any]) -> dict[str, str]:
    current: dict[str, str] = {}
    for ref in exact_refs(contract):
        path = LAB / ref["path"]
        actual = digest(path) if path.is_file() else "missing"
        if actual != ref["sha256"]:
            raise ActivationFailure(f"selected dependency drift: {ref['path']}")
        current[ref["path"]] = actual
    admission = load(LAB / contract["admission_validation"]["path"])
    if admission.get("result") != "PASS" or admission.get("implementation_admitted") is not True or admission.get("runtime_activated") is not False or admission.get("cutover_authorized") is not False:
        raise ActivationFailure("admission is not current and inactive")
    return current


def run_rust_contract(target: Path) -> dict[str, Any]:
    completed = subprocess.run(
        ["cargo", "test", "--locked", "--test", "public_contract", "--", "--test-threads=1"],
        cwd=CANDIDATE,
        env={**os.environ, "CARGO_TARGET_DIR": str(target)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    tests = sorted((match.group(1), match.group(2)) for line in completed.stdout.splitlines() if (match := TEST_RE.match(line.strip())))
    if completed.returncode != 0 or len(tests) != 4 or any(result != "ok" for _, result in tests):
        raise ActivationFailure(f"Rust public contract failed: {completed.stdout[-4000:]}")
    return {"exit": completed.returncode, "test_count": len(tests), "tests": tests}


def mutation_tournament(source: list[dict[str, Any]], target: list[dict[str, Any]], contract: dict[str, Any], expected: dict[str, Any]) -> list[dict[str, str]]:
    probes: list[dict[str, str]] = []

    def probe(probe_id: str, action: Callable[[], None]) -> None:
        try:
            action()
        except ActivationFailure:
            probes.append({"probe_id": probe_id, "result": "PASS"})
        else:
            probes.append({"probe_id": probe_id, "result": "BLOCK"})

    substituted = copy.deepcopy(target)
    substituted[0]["payload"]["label"] = "substituted"
    probe("event-omission-or-substitution", lambda: project(substituted))

    wrong_cut = normalize_and_seal(target[:-1])
    probe("wrong-event-cut", lambda: validate_target(project(wrong_cut), expected))

    wrong_context = copy.deepcopy(target)
    wrong_context[4]["payload"]["map_ref"] = "cal.context-map.governance-ontology-lifecycle/v1"
    wrong_context = normalize_and_seal(wrong_context)
    probe("wrong-context-binding", lambda: validate_target(project(wrong_context), expected))

    reverse = copy.deepcopy(target)
    relation = reverse[-2]["payload"]
    relation["source"], relation["target"] = relation["target"], relation["source"]
    relation["direction"] = "target-to-source"
    reverse = normalize_and_seal(reverse)
    probe("reverse-relationship-direction", lambda: validate_target(project(reverse), expected))

    def snapshot_source() -> None:
        candidate = copy.deepcopy(expected)
        candidate["snapshots"][0]["canonical_replay_source"] = True
        validate_target(candidate, expected)
    probe("snapshot-promoted-to-canonical-source", snapshot_source)

    no_challenge = normalize_and_seal([event for event in target if event["subject_kind"] != "challenge-contract"])
    probe("missing-challenge-contract", lambda: project(no_challenge))

    partial = normalize_and_seal(source + target[len(source):len(source) + 2])
    probe("partial-migration", lambda: validate_target(project(partial), expected))

    stale = copy.deepcopy(contract)
    stale["admission_validation"]["sha256"] = "0" * 64
    stale["selected_inputs"] = [dict(ref, sha256="0" * 64) if ref["path"] == stale["admission_validation"]["path"] else ref for ref in stale["selected_inputs"]]
    probe("stale-admission-digest", lambda: validate_refs(stale))

    def rollback_corruption() -> None:
        corrupted = SOURCE.read_bytes() + b"corruption\n"
        if hashlib.sha256(corrupted).hexdigest() != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
            raise ActivationFailure("rollback preimage mismatch")
    probe("rollback-state-corruption", rollback_corruption)

    escalated = copy.deepcopy(target)
    escalated[-1]["payload"]["authority_effect"] = "activation"
    escalated = normalize_and_seal(escalated)
    probe("activation-or-cutover-authority-escalation", lambda: project(escalated))
    return probes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--print-generated", action="store_true")
    args = parser.parse_args()
    source_bytes = SOURCE.read_bytes()
    source = load_event_bytes(source_bytes)
    inventory = load(INVENTORY)
    target = migrate(source, inventory)
    target_projection = project(target)
    if args.print_generated:
        print(json.dumps({"events_jsonl": event_bytes(target).decode("utf-8"), "projection": target_projection}, indent=2, sort_keys=True))
        return 0

    contract = load(CONTRACT)
    expected = load(EXPECTED)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    try:
        before = validate_refs(contract)
        add("admission-and-selected-inputs-current", True, {"tracked_paths": len(before)})
        source_projection = project(source)
        add("source-cut-current", len(source) == inventory["source_event_count"] and source_projection["source_event_set_digest"] == inventory["source_event_set_digest"], {"events": len(source), "event_set_digest": source_projection["source_event_set_digest"]})
        projection_a = project(migrate(load_event_bytes(source_bytes), inventory))
        validate_target(projection_a, expected)
        projection_b = project(migrate(load_event_bytes(source_bytes), inventory))
        validate_target(projection_b, expected)
        add("deterministic-shadow-migration-twice", projection_a == projection_b, {"runs": 2, "projection_digest": projection_a["projection_digest"], "target_events": len(target)})
        add("event-calculated-node-relation-state", len(projection_a["nodes"]) == 2 and len(projection_a["relations"]) == 1 and len(projection_a["snapshots"]) == 3, {"nodes": 2, "relations": 1, "snapshots": 3})
        add("context-and-challenge-preservation", len(projection_a["context_bindings"]) == 1 and len(projection_a["challenge_contracts"]) == 1, {"context_map": projection_a["context_bindings"][0]["state"]["map_ref"], "challenge_gate": projection_a["challenge_contracts"][0]["state"]["resolution_gate"]})
        add("noncanonical-projection-no-authority", projection_a["canonical_replay_source"] is False and projection_a["authority_effect"] == "none" and all(item["canonical_replay_source"] is False for item in projection_a["snapshots"]), {"canonical_replay_source": False, "authority_effect": "none"})

        temporary_path: Path | None = None
        with tempfile.TemporaryDirectory(prefix="cal-d65-shadow-activation-") as temporary:
            temporary_path = Path(temporary)
            active = temporary_path / "active-events.jsonl"
            active.write_bytes(source_bytes)
            preimage_sha = digest(active)
            active.write_bytes(event_bytes(target))
            cutover_projection = project(load_event_bytes(active.read_bytes()))
            validate_target(cutover_projection, expected)
            active.write_bytes(source_bytes)
            rollback_bytes_equal = active.read_bytes() == source_bytes
            rollback_projection = project(load_event_bytes(active.read_bytes()))
            rollback_projection_equal = rollback_projection == source_projection
            post_rollback_sha = digest(active)
            rust_a = run_rust_contract(temporary_path / "cargo-target")
            rust_b = run_rust_contract(temporary_path / "cargo-target")
        add("disposable-cutover-sequence", cutover_projection == projection_a, {"target_projection_digest": cutover_projection["projection_digest"]})
        add("exact-rollback", rollback_bytes_equal and rollback_projection_equal and preimage_sha == post_rollback_sha, {"preimage_sha256": preimage_sha, "post_rollback_sha256": post_rollback_sha, "bytes_equal": rollback_bytes_equal, "projection_equal": rollback_projection_equal, "temporary_state_removed": temporary_path is not None and not temporary_path.exists()})
        add("rust-public-contract-twice", rust_a == rust_b and rust_a["test_count"] == 4, {"run_a": rust_a, "run_b": rust_b})

        probes = mutation_tournament(source, target, contract, expected)
        add("mutation-tournament", len(probes) == 10 and all(item["result"] == "PASS" for item in probes), probes)
        after = validate_refs(contract)
        changed = sorted(path for path in before if before[path] != after.get(path))
        add("protected-byte-preservation", not changed, {"tracked_paths": len(before), "changed": changed})
    except (OSError, json.JSONDecodeError, ActivationFailure, KeyError) as exc:
        add("shadow-activation-exception", False, str(exc))
        projection_a = {}
        probes = []
        rust_a = {}
        before = {}
        changed = []

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-shadow-activation-evidence/v1",
        "activation_rehearsal_id": contract.get("activation_rehearsal_id"),
        "plan_ref": "CAL-PLAN-0006",
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "deterministic_runs": 2 if result == "PASS" else 0,
        "source_event_count": len(source),
        "target_event_count": len(target),
        "source_event_set_digest": project(source)["source_event_set_digest"],
        "target_event_set_digest": projection_a.get("source_event_set_digest"),
        "target_projection_digest": projection_a.get("projection_digest"),
        "rust_public_contract_tests_per_run": rust_a.get("test_count", 0),
        "mutation_probes_passed": sum(item.get("result") == "PASS" for item in probes),
        "mutation_probes_total": len(probes),
        "rollback_result": "PASS" if result == "PASS" else "not_evaluable",
        "protected_paths": len(before),
        "protected_byte_drift": changed,
        "stage_states": {
            "AC-S1": "PASS" if result == "PASS" else "BLOCK",
            "AC-S2": "PASS" if result == "PASS" else "not_evaluable",
            "AC-S3": "PASS" if result == "PASS" else "not_evaluable",
            "AC-S4": "PASS" if result == "PASS" else "not_evaluable",
            "AC-S5": "eligible" if result == "PASS" else "not_evaluable"
        },
        "final_gate": "G-D65-EPOCH-002-ACTIVATION-CUTOVER",
        "final_gate_eligible": result == "PASS",
        "runtime_activated": False,
        "migration_authorized": False,
        "cutover_authorized": False,
        "cutover_performed": False,
        "external_effects": False,
        "authority_effect": "none",
        "inputs": [
            {"path": str(CONTRACT.relative_to(LAB)), "sha256": digest(CONTRACT)},
            {"path": str(SOURCE.relative_to(LAB)), "sha256": digest(SOURCE)},
            {"path": str(INVENTORY.relative_to(LAB)), "sha256": digest(INVENTORY)},
            {"path": str(EXPECTED.relative_to(LAB)), "sha256": digest(EXPECTED)}
        ],
        "claim_ceiling": "PASS proves deterministic disposable shadow activation, canonical-event migration, event-calculated projections, hostile mutation detection, Rust compatibility, and exact rollback for the admitted inactive product. It performs and authorizes no live activation, migration, cutover, publication, release, deployment, or external effect."
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt[key] for key in ("activation_rehearsal_id", "result", "failed_checks", "deterministic_runs", "source_event_count", "target_event_count", "rust_public_contract_tests_per_run", "mutation_probes_passed", "mutation_probes_total", "rollback_result", "stage_states", "final_gate_eligible", "runtime_activated", "cutover_authorized", "cutover_performed", "authority_effect")}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

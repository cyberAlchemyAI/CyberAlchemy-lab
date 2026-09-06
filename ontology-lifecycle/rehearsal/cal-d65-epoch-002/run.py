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
from typing import Any

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CONTRACT = HERE / "rehearsal-contract.json"
EVENTS = HERE / "fixtures/canonical-events.jsonl"
EXPECTED_NODES = HERE / "fixtures/expected-node-projections.json"
EXPECTED_RELATIONS = HERE / "fixtures/expected-relation-projections.json"
RECEIPT = HERE / "receipts/rehearsal.json"
CANDIDATE = LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-context-adapters-v2/v1"
TEST_RE = re.compile(r"^test ([^ ]+) \.\.\. (ok|FAILED|ignored)$")
ALLOWED_KINDS = {"node", "relation", "context-binding", "challenge-contract"}


class RehearsalFailure(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RehearsalFailure(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def content_digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def seal_event(event: dict[str, Any]) -> None:
    body = copy.deepcopy(event)
    body.pop("event_digest", None)
    event["event_digest"] = content_digest(body)


def load_events() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(EVENTS.read_text(encoding="utf-8").splitlines(), 1):
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RehearsalFailure(f"event line {line_number} is not an object")
        rows.append(value)
    return rows


def validate_log(events: list[dict[str, Any]]) -> None:
    if [event.get("sequence") for event in events] != list(range(1, len(events) + 1)):
        raise RehearsalFailure("event sequence is not complete and gap-free")
    event_ids = [event.get("event_id") for event in events]
    if len(event_ids) != len(set(event_ids)):
        raise RehearsalFailure("event ids are duplicated")
    previous_by_stream: dict[str, str] = {}
    for event in events:
        if event.get("schema_version") != "cal.rehearsal-event/v1":
            raise RehearsalFailure("event schema is invalid")
        if event.get("subject_kind") not in ALLOWED_KINDS:
            raise RehearsalFailure("event subject kind is invalid")
        if event.get("operation") != "upsert":
            raise RehearsalFailure("only complete upsert events are supported")
        if event.get("payload", {}).get("authority_effect") != "none":
            raise RehearsalFailure("event carries authority escalation")
        actual = event.get("event_digest")
        body = copy.deepcopy(event)
        body.pop("event_digest", None)
        if actual != content_digest(body):
            raise RehearsalFailure("event digest mismatch")
        stream = str(event.get("stream_id"))
        if event.get("previous_event_digest") != previous_by_stream.get(stream):
            raise RehearsalFailure("per-stream digest chain mismatch")
        previous_by_stream[stream] = str(actual)


def normalize_and_reseal(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = copy.deepcopy(events)
    previous_by_stream: dict[str, str] = {}
    for sequence, event in enumerate(result, 1):
        event["sequence"] = sequence
        stream = str(event["stream_id"])
        event["previous_event_digest"] = previous_by_stream.get(stream)
        seal_event(event)
        previous_by_stream[stream] = event["event_digest"]
    return result


def project(events: list[dict[str, Any]]) -> dict[str, Any]:
    validate_log(events)
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for event in events:
        latest[(event["subject_kind"], event["subject_id"])] = event
    event_set_digest = content_digest([event["event_digest"] for event in events])

    def projected(kind: str) -> list[dict[str, Any]]:
        rows = []
        for (subject_kind, subject_id), event in latest.items():
            if subject_kind == kind:
                rows.append({
                    "subject_id": subject_id,
                    "source_event_id": event["event_id"],
                    "source_event_digest": event["event_digest"],
                    "state": event["payload"],
                })
        return sorted(rows, key=lambda row: row["subject_id"])

    nodes = projected("node")
    relations = projected("relation")
    contexts = projected("context-binding")
    challenges = projected("challenge-contract")
    if len(nodes) != 2 or len(relations) != 1 or len(contexts) != 1 or len(challenges) != 1:
        raise RehearsalFailure("required node, relation, context, or challenge projection is missing")
    relation = relations[0]["state"]
    if relation != {
        "source": "CAL-NODE-GOVERNANCE-DECISION",
        "predicate": "feeds-evidence-to",
        "target": "CAL-NODE-ONTOLOGY-PROJECTION",
        "direction": "source-to-target",
        "context_map_ref": "cal.context-map.governance-ontology-lifecycle/v2",
        "lifecycle": "validated",
        "authority_effect": "none",
    }:
        raise RehearsalFailure("relationship direction or contract is invalid")
    context = contexts[0]["state"]
    if context != {
        "map_ref": "cal.context-map.governance-ontology-lifecycle/v2",
        "map_version": "2.0.0-candidate.1",
        "source_context_ref": "cal.context.governance/v2",
        "target_context_ref": "cal.context.ontology-lifecycle/v2",
        "direction": "source-to-target",
        "authority_effect": "none",
    }:
        raise RehearsalFailure("context binding is invalid")
    challenge = challenges[0]["state"]
    required_challenge = {
        "subject_ref": "CAL-NODE-ONTOLOGY-PROJECTION",
        "owner_route": "governance context owner plus ontology-lifecycle context owner",
        "resolution_gate": "G-D65-EPOCH-002-POST-APPROVAL-ADMISSION",
        "authority_effect": "none",
    }
    if any(challenge.get(key) != value for key, value in required_challenge.items()):
        raise RehearsalFailure("challenge contract is missing or invalid")

    projection = {
        "schema_version": "cal.d65-rehearsal-projection/v1",
        "canonical_replay_source": False,
        "source_cursor": len(events),
        "source_event_set_digest": event_set_digest,
        "nodes": nodes,
        "relations": relations,
        "context_bindings": contexts,
        "challenge_contracts": challenges,
        "snapshots": [
            {"subject_kind": kind, "subject_id": row["subject_id"], "canonical_replay_source": False, "source_event_digest": row["source_event_digest"]}
            for kind, rows in (("node", nodes), ("relation", relations))
            for row in rows
        ],
        "authority_effect": "none",
    }
    projection["projection_digest"] = content_digest(projection)
    return projection


def validate_expected(projection: dict[str, Any]) -> None:
    expected_nodes = load(EXPECTED_NODES)
    expected_relations = load(EXPECTED_RELATIONS)
    common = ("canonical_replay_source", "source_cursor", "source_event_set_digest")
    if any(projection[key] != expected_nodes[key] for key in common) or projection["nodes"] != expected_nodes["nodes"]:
        raise RehearsalFailure("node projection differs from frozen expectation")
    if any(projection[key] != expected_relations[key] for key in common) or projection["relations"] != expected_relations["relations"]:
        raise RehearsalFailure("relation projection differs from frozen expectation")
    if any(snapshot["canonical_replay_source"] for snapshot in projection["snapshots"]):
        raise RehearsalFailure("snapshot was promoted to canonical replay source")


def exact_refs(contract: dict[str, Any]) -> list[dict[str, str]]:
    product = contract["approved_product"]
    return [
        {"path": product["manifest_path"], "sha256": product["manifest_sha256"]},
        {"path": product["product_test_evidence_path"], "sha256": product["product_test_evidence_sha256"]},
        {"path": product["approval_decision_path"], "sha256": product["approval_decision_sha256"]},
        {"path": product["approval_validation_path"], "sha256": product["approval_validation_sha256"]},
        *contract["selected_inputs"],
        *contract["protected_bytes"],
    ]


def validate_refs(contract: dict[str, Any]) -> dict[str, str]:
    current: dict[str, str] = {}
    for ref in exact_refs(contract):
        path = LAB / ref["path"]
        actual = digest(path) if path.is_file() else "missing"
        if actual != ref["sha256"]:
            raise RehearsalFailure(f"selected dependency drift: {ref['path']}")
        current[ref["path"]] = actual
    approval = load(LAB / contract["approved_product"]["approval_validation_path"])
    if approval.get("result") != "PASS" or approval.get("product_approval") != "approved" or approval.get("cutover_authorized") is not False:
        raise RehearsalFailure("approved-product validation is not current")
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
        raise RehearsalFailure(f"Rust public contract failed: {completed.stdout[-4000:]}")
    return {"exit": completed.returncode, "test_count": len(tests), "tests": tests}


def mutation_tournament(events: list[dict[str, Any]], contract: dict[str, Any]) -> list[dict[str, str]]:
    probes: list[dict[str, str]] = []

    def probe(probe_id: str, action) -> None:
        try:
            action()
        except RehearsalFailure:
            probes.append({"probe_id": probe_id, "result": "PASS"})
        else:
            probes.append({"probe_id": probe_id, "result": "BLOCK"})

    substituted = copy.deepcopy(events)
    substituted[0]["payload"]["label"] = "Substituted decision"
    probe("event-substitution", lambda: project(substituted))

    probe("event-omission-partial-stream", lambda: project(events[:3] + events[4:]))

    wrong_context = copy.deepcopy(events)
    wrong_context[4]["payload"]["map_ref"] = "cal.context-map.governance-ontology-lifecycle/v1"
    probe("wrong-context-binding", lambda: project(normalize_and_reseal(wrong_context)))

    reversed_relation = copy.deepcopy(events)
    relation = reversed_relation[6]["payload"]
    relation["source"], relation["target"] = relation["target"], relation["source"]
    relation["direction"] = "target-to-source"
    probe("reverse-relation", lambda: project(normalize_and_reseal(reversed_relation)))

    def snapshot_escalation() -> None:
        candidate = project(events)
        candidate["snapshots"][0]["canonical_replay_source"] = True
        validate_expected(candidate)
    probe("snapshot-source-escalation", snapshot_escalation)

    without_challenge = normalize_and_reseal([event for event in events if event["subject_kind"] != "challenge-contract"])
    probe("missing-challenge-contract", lambda: project(without_challenge))

    stale = copy.deepcopy(contract)
    stale["approved_product"]["manifest_sha256"] = "0" * 64
    probe("stale-approved-product-digest", lambda: validate_refs(stale))

    escalated = copy.deepcopy(events)
    escalated[3]["payload"]["authority_effect"] = "admission-only"
    probe("authority-escalation", lambda: project(normalize_and_reseal(escalated)))
    return probes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    contract = load(CONTRACT)
    events = load_events()
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    try:
        before = validate_refs(contract)
        add("approved-and-selected-inputs-current", True, {"tracked_paths": len(before)})
        projection_a = project(events)
        validate_expected(projection_a)
        projection_b = project(load_events())
        validate_expected(projection_b)
        add("deterministic-event-replay-twice", projection_a == projection_b, {"projection_digest": projection_a["projection_digest"], "runs": 2})
        add("node-and-relation-latest-snapshots", len(projection_a["nodes"]) == 2 and len(projection_a["relations"]) == 1 and len(projection_a["snapshots"]) == 3, {"nodes": len(projection_a["nodes"]), "relations": len(projection_a["relations"]), "snapshots": len(projection_a["snapshots"])})
        add("context-and-challenge-contracts", len(projection_a["context_bindings"]) == 1 and len(projection_a["challenge_contracts"]) == 1, {"contexts": len(projection_a["context_bindings"]), "challenges": len(projection_a["challenge_contracts"])})
        add("projection-noncanonical-and-no-authority", projection_a["canonical_replay_source"] is False and projection_a["authority_effect"] == "none" and all(snapshot["canonical_replay_source"] is False for snapshot in projection_a["snapshots"]), {"canonical_replay_source": projection_a["canonical_replay_source"], "authority_effect": projection_a["authority_effect"]})

        temporary_path: Path | None = None
        with tempfile.TemporaryDirectory(prefix="cal-d65-rehearsal-") as temporary:
            temporary_path = Path(temporary)
            (temporary_path / "projection-a.json").write_bytes(canonical(projection_a))
            (temporary_path / "projection-b.json").write_bytes(canonical(projection_b))
            rust_a = run_rust_contract(temporary_path / "cargo-target")
            rust_b = run_rust_contract(temporary_path / "cargo-target")
        add("rust-public-contract-twice", rust_a == rust_b and rust_a["test_count"] == 4, {"run_a": rust_a, "run_b": rust_b})
        add("temporary-state-rollback", temporary_path is not None and not temporary_path.exists(), {"removed": temporary_path is not None and not temporary_path.exists()})

        probes = mutation_tournament(events, contract)
        add("mutation-tournament", len(probes) == 8 and all(item["result"] == "PASS" for item in probes), probes)
        after = validate_refs(contract)
        changed = sorted(path for path in before if before[path] != after.get(path))
        add("protected-byte-preservation", not changed, {"tracked_paths": len(before), "changed": changed})
    except (OSError, json.JSONDecodeError, RehearsalFailure, KeyError) as exc:
        add("rehearsal-exception", False, str(exc))
        projection_a = {}
        projection_b = {}
        probes = []
        rust_a = {}
        rust_b = {}
        before = {}

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-isolated-rehearsal-evidence/v1",
        "rehearsal_id": contract.get("rehearsal_id"),
        "plan_ref": contract.get("plan_ref"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "deterministic_runs": 2 if result == "PASS" else 0,
        "projection_digest": projection_a.get("projection_digest"),
        "source_event_set_digest": projection_a.get("source_event_set_digest"),
        "rust_public_contract_tests_per_run": rust_a.get("test_count", 0),
        "mutation_probes_passed": sum(item.get("result") == "PASS" for item in probes),
        "mutation_probes_total": len(probes),
        "protected_paths": len(before),
        "protected_byte_drift": [],
        "rollback_result": "PASS" if result == "PASS" else "not_evaluable",
        "stage_states": {
            "RH-S1": "PASS" if result == "PASS" else "BLOCK",
            "RH-S2": "PASS" if result == "PASS" else "not_evaluable",
            "RH-S3": "PASS" if result == "PASS" else "not_evaluable",
            "RH-S4": "PASS" if result == "PASS" else "not_evaluable",
            "RH-S5": "eligible" if result == "PASS" else "not_evaluable"
        },
        "final_gate": "G-D65-EPOCH-002-POST-APPROVAL-ADMISSION",
        "final_gate_eligible": result == "PASS",
        "admission_authorized": False,
        "activation_authorized": False,
        "migration_authorized": False,
        "cutover_authorized": False,
        "authority_effect": "none",
        "inputs": [{"path": str(CONTRACT.relative_to(LAB)), "sha256": digest(CONTRACT)}, {"path": str(EVENTS.relative_to(LAB)), "sha256": digest(EVENTS)}, {"path": str(EXPECTED_NODES.relative_to(LAB)), "sha256": digest(EXPECTED_NODES)}, {"path": str(EXPECTED_RELATIONS.relative_to(LAB)), "sha256": digest(EXPECTED_RELATIONS)}],
        "claim_ceiling": "PASS proves deterministic isolated replay, context/challenge projection, mutation detection, Rust adapter compatibility, and rollback for the exact approved product. It grants no admission, activation, migration, cutover, publication, release, deployment, or external effect."
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt[key] for key in ("rehearsal_id", "result", "failed_checks", "deterministic_runs", "rust_public_contract_tests_per_run", "mutation_probes_passed", "mutation_probes_total", "rollback_result", "stage_states", "final_gate_eligible", "admission_authorized", "cutover_authorized", "authority_effect")}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

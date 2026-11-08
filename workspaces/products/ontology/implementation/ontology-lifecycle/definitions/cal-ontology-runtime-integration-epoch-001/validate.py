#!/usr/bin/env python3
"""Validate the D65-S1 ontology-runtime integration Definition Pack candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CORE = LAB.parent / "domainspec-core"
PACK_PATH = HERE / "definition-pack.json"
REGISTRY_PATH = HERE / "handled-definitions.json"
SCHEMA_PATH = HERE / "schema.json"
REQUEST_PATH = HERE / "owner-decision-request.json"
RECEIPT_PATH = HERE / "receipts/validation.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one object")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_digest(path: Path, definition_id: str) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    heading = f"## {definition_id}:"
    start = next((i for i, line in enumerate(lines) if line.startswith(heading)), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return hashlib.sha256("".join(lines[start:end]).encode("utf-8")).hexdigest()


def repository_root(raw: str) -> Path:
    if raw == str(CORE):
        return CORE
    if raw == str(LAB):
        return LAB
    raise ValueError(f"unregistered repository: {raw}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    pack = load(PACK_PATH)
    registry = load(REGISTRY_PATH)
    schema = load(SCHEMA_PATH)
    request = load(REQUEST_PATH)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    required_pack_keys = set(schema.get("required", []))
    record(
        "pack-schema-and-authority",
        set(pack) == required_pack_keys
        and pack.get("schema_version") == "cal.ontology-runtime-integration-definition-pack/v1"
        and pack.get("pack_id") == "CAL-DEFINE-PACK-ONTOLOGY-RUNTIME-INTEGRATION-001"
        and pack.get("status") == "validated-candidate-awaiting-owner-selection"
        and pack.get("authority_effect") == "none",
        {"keys": sorted(pack), "authority_effect": pack.get("authority_effect")},
    )

    source_failures: list[dict[str, str]] = []
    selected_selector_ids: set[str] = set()
    for source in pack.get("source_refs", []):
        root = repository_root(str(source.get("repository")))
        path = root / str(source.get("path"))
        if not path.is_file():
            source_failures.append({"source_id": str(source.get("source_id")), "failure": "missing"})
            continue
        if source.get("source_id") == "SRC-CAL-D65-PLAN-PREIMAGE":
            current_plan = load(path)
            expected_preimage = source.get("sha256")
            carried_pack = current_plan.get("selected_dependencies", {}).get("definition_pack", {}).get("sha256")
            descendant_carries_pack = current_plan.get("revision", 0) >= 4 and carried_pack == digest(PACK_PATH)
            if digest(path) != expected_preimage and current_plan.get("supersedes_plan_sha256") != expected_preimage and not descendant_carries_pack:
                source_failures.append({"source_id": str(source.get("source_id")), "failure": "preimage-not-in-current-revision-chain"})
        elif source.get("currentness_mode") == "selector-set":
            for selector in source.get("selectors", []):
                definition_id = str(selector.get("definition_id"))
                selected_selector_ids.add(definition_id)
                if section_digest(path, definition_id) != selector.get("sha256"):
                    source_failures.append({"source_id": str(source.get("source_id")), "failure": f"selector-drift:{definition_id}"})
        elif digest(path) != source.get("sha256"):
            source_failures.append({"source_id": str(source.get("source_id")), "failure": "digest-drift"})
    record("selected-source-currentness", not source_failures, source_failures or {"source_count": len(pack.get("source_refs", [])), "selector_ids": sorted(selected_selector_ids)})

    records = registry.get("records", [])
    record_ids = [item.get("record_id") for item in records]
    concept_ids = [item.get("concept_id") for item in records]
    required_ids = pack.get("required_concept_ids", [])
    packed_concepts = pack.get("concepts", [])
    record(
        "required-concept-and-record-closure",
        len(records) == len(required_ids) == len(packed_concepts) == 13
        and len(record_ids) == len(set(record_ids))
        and len(concept_ids) == len(set(concept_ids))
        and set(concept_ids) == set(required_ids)
        and {item.get("handled_definition_ref") for item in packed_concepts} == set(record_ids),
        {"required": len(required_ids), "records": len(records), "packed": len(packed_concepts)},
    )

    payload_names = {"reuse", "specialize", "propose", "open"}
    disposition_failures: list[str] = []
    voice_failures: list[str] = []
    expected_reuse = {"CAV2-D19", "CAV2-D26", "CAV2-D40", "CAV2-D65", "CAV2-D66"}
    actual_reuse: set[str] = set()
    for item in records:
        disposition = item.get("current_disposition")
        present = payload_names.intersection(item)
        if present != {disposition} or item.get("authority_effect") != "none":
            disposition_failures.append(str(item.get("record_id")))
            continue
        payload = item.get(str(disposition), {})
        if disposition == "reuse":
            actual_reuse.add(str(payload.get("canonical_definition_id")))
            if payload.get("canonical_definition_id") not in selected_selector_ids or not payload.get("selector_sha256"):
                disposition_failures.append(str(item.get("record_id")))
        elif disposition in {"specialize", "propose"}:
            for field in ("normative_voice", "formal_voice", "plain_language_voice", "domain_context_voice", "boundary"):
                if not isinstance(payload.get(field), str) or not payload[field].strip():
                    voice_failures.append(f"{item.get('record_id')}:{field}")
        if not item.get("decision_owner_route") or not item.get("challenge_or_refresh_route") or not item.get("source_refs"):
            disposition_failures.append(str(item.get("record_id")))
    record("one-current-disposition", not disposition_failures and actual_reuse == expected_reuse, {"failures": disposition_failures, "canonical_reuse": sorted(actual_reuse)})
    record("three-voice-and-boundary-coverage", not voice_failures, {"failures": voice_failures, "candidate_voice_records": sum(item.get("current_disposition") in {"specialize", "propose"} for item in records)})

    endpoints = set(required_ids)
    relation_ids = [item.get("relation_id") for item in pack.get("relationships", [])]
    relation_failures = [
        str(item.get("relation_id"))
        for item in pack.get("relationships", [])
        if item.get("source") not in endpoints or item.get("target") not in endpoints
    ]
    record("relationship-endpoint-closure", len(relation_ids) == len(set(relation_ids)) and not relation_failures, {"relation_count": len(relation_ids), "failures": relation_failures})

    request_ok = (
        request.get("schema_version") == "cal.definition-pack-owner-decision-request/v1"
        and request.get("gate_id") == "G-D65-DEFINITIONS"
        and request.get("status") == "pending-owner-selection"
        and request.get("candidate_refs", {}).get("definition_pack_sha256") == digest(PACK_PATH)
        and request.get("candidate_refs", {}).get("handled_definitions_sha256") == digest(REGISTRY_PATH)
        and {item.get("option_id") for item in request.get("options", [])} == {"D65DEF-1", "D65DEF-2", "D65DEF-3", "D65DEF-4"}
    )
    record("owner-decision-gate-prepared", request_ok and pack.get("owner_decision", {}).get("state") == "pending", {"request_status": request.get("status"), "pack_owner_state": pack.get("owner_decision", {}).get("state")})

    blocked = pack.get("blocked_actions", [])
    authority_pass = (
        registry.get("authority_effect") == registry.get("implementation_effect") == registry.get("promotion_effect") == "none"
        and any("D65-S2" in item for item in blocked)
        and any("Invoke" in item for item in blocked)
    )
    record("authority-and-successor-boundary", authority_pass, {"blocked_action_count": len(blocked)})

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.ontology-runtime-integration-definition-validation/v1",
        "pack_id": pack.get("pack_id"),
        "result": result,
        "gate_id": "G-D65-DEFINITIONS",
        "gate_state": "BLOCK" if result == "PASS" else "BLOCK",
        "gate_blocker": "Definitions-governance owner selection is pending." if result == "PASS" else "Candidate validation failed.",
        "checks": checks,
        "failed_checks": failed,
        "inputs": [
            {"path": str(PACK_PATH.relative_to(LAB)), "sha256": digest(PACK_PATH)},
            {"path": str(REGISTRY_PATH.relative_to(LAB)), "sha256": digest(REGISTRY_PATH)},
            {"path": str(SCHEMA_PATH.relative_to(LAB)), "sha256": digest(SCHEMA_PATH)},
            {"path": str(REQUEST_PATH.relative_to(LAB)), "sha256": digest(REQUEST_PATH)},
            {"path": str(Path(__file__).relative_to(LAB)), "sha256": digest(Path(__file__))}
        ],
        "authority_effect": "none",
        "claim_ceiling": "PASS proves candidate definition structure, selected source currentness, disposition closure, three-voice coverage, and a prepared owner gate. It does not select the meanings, pass D65-S1, authorize D65-S2, promote definitions, implement, migrate, cut over, publish, release, deploy, or create external effects."
    }
    if args.write_receipt:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"pack_id": receipt["pack_id"], "result": result, "failed_checks": failed, "gate_id": receipt["gate_id"], "gate_state": receipt["gate_state"], "gate_blocker": receipt["gate_blocker"]}, indent=2, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

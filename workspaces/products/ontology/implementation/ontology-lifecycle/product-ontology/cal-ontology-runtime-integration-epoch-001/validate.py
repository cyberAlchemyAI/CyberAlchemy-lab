#!/usr/bin/env python3
"""Validate the D65-S2 Product Capability and product-ontology candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CORE = LAB.parent / "domainspec-core"
PROFILE = HERE / "profile.json"
SOURCES = HERE / "sources.json"
CAPABILITY = HERE / "product-capability.json"
NODES = HERE / "nodes.json"
RELATIONS = HERE / "relations.json"
RESIDUE = HERE / "residue.json"
SCHEMA = HERE / "schema.json"
REQUEST = HERE / "owner-decision-request.json"
RECEIPT = HERE / "receipts/validation.json"

CAPABILITY_ID = "CA2-CAP-CONSUME-GOVERNED-EVENT-CALCULATED-ONTOLOGY-PROJECTIONS"
EXPECTED_DEFINITION_BINDINGS = {
    "CAL-HDEF-INTEGRATION-ONTOLOGY",
    "CAL-HDEF-INTEGRATION-APPEND-ONLY-EVENT-LEDGER",
    "CAL-HDEF-INTEGRATION-CHALLENGE-CONTRACT",
    "CAL-HDEF-INTEGRATION-D65-CONSTRUCTION",
    "CAL-HDEF-INTEGRATION-CONTEXT",
    "CAL-HDEF-INTEGRATION-BUSINESS-SYSTEM-BRIDGE",
    "CAL-HDEF-INTEGRATION-CONTEXT-SELECTOR",
    "CAL-HDEF-INTEGRATION-CANONICAL-EVENT-CUT",
    "CAL-HDEF-INTEGRATION-EVENT-CALCULATED-PROJECTION",
    "CAL-HDEF-INTEGRATION-CONTEXT-PROJECTION-BINDING",
    "CAL-HDEF-INTEGRATION-EPOCH",
    "CAL-HDEF-INTEGRATION-SYSTEM-RUNTIME-ONTOLOGY",
    "CAL-HDEF-INTEGRATION-CHALLENGE-ROUTE",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selector_digest(path: Path, definition_id: str) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    heading = f"## {definition_id}:"
    start = next((index for index, line in enumerate(lines) if line.startswith(heading)), None)
    if start is None:
        return None
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")), len(lines))
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

    documents = {
        "profile": load(PROFILE),
        "sources": load(SOURCES),
        "capability": load(CAPABILITY),
        "nodes": load(NODES),
        "relations": load(RELATIONS),
        "residue": load(RESIDUE),
        "decision_request": load(REQUEST),
    }
    schema = load(SCHEMA)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    schema_failures: dict[str, list[str]] = {}
    for name, document in documents.items():
        errors = [error.message for error in Draft202012Validator(schema["$defs"][name]).iter_errors(document)]
        if errors:
            schema_failures[name] = errors
    record("package-schema", not schema_failures, schema_failures or {"documents": sorted(documents)})

    profile = documents["profile"]
    record(
        "business-domain-package-profile",
        profile.get("ontology_id") == "cal.product-ontology.ontology-runtime-integration"
        and profile.get("ontology_type") == "business-domain"
        and profile.get("branch") == "business"
        and profile.get("materialization") == "package-required"
        and profile.get("candidate_status") == "validated-candidate-awaiting-owner-admission"
        and profile.get("owner_gate") == "G-D65-PRODUCT"
        and profile.get("authority_effect") == "none",
        {
            "ontology_id": profile.get("ontology_id"),
            "type": profile.get("ontology_type"),
            "materialization": profile.get("materialization"),
            "gate": profile.get("owner_gate"),
        },
    )

    source_items = documents["sources"].get("sources", [])
    source_ids = [item.get("source_id") for item in source_items]
    source_failures: list[dict[str, str]] = []
    selector_ids: set[str] = set()
    for source in source_items:
        source_id = str(source.get("source_id"))
        try:
            path = repository_root(str(source.get("repository"))) / str(source.get("path"))
        except ValueError as error:
            source_failures.append({"source_id": source_id, "failure": str(error)})
            continue
        if not path.is_file():
            source_failures.append({"source_id": source_id, "failure": "missing"})
            continue
        mode = source.get("currentness_mode")
        if mode == "selector-set":
            for selector in source.get("selectors", []):
                definition_id = str(selector.get("definition_id"))
                selector_ids.add(definition_id)
                if selector_digest(path, definition_id) != selector.get("sha256"):
                    source_failures.append({"source_id": source_id, "failure": f"selector-drift:{definition_id}"})
        elif mode == "plan-preimage":
            expected = source.get("sha256")
            current_plan = load(path)
            carried = current_plan.get("selected_dependencies", {}).get("product_capability", {}).get("sha256")
            descendant = current_plan.get("revision", 0) >= 6 and carried == digest(CAPABILITY)
            if digest(path) != expected and current_plan.get("supersedes_plan_sha256") != expected and not descendant:
                source_failures.append({"source_id": source_id, "failure": "preimage-not-in-current-plan-chain"})
        elif mode == "whole-file":
            if digest(path) != source.get("sha256"):
                source_failures.append({"source_id": source_id, "failure": "digest-drift"})
        else:
            source_failures.append({"source_id": source_id, "failure": f"unsupported-currentness-mode:{mode}"})
    record(
        "selected-source-currentness",
        len(source_items) == 8 and len(source_ids) == len(set(source_ids)) and not source_failures and selector_ids == {"CAV2-D63", "CAV2-D67"},
        {"source_count": len(source_items), "selector_ids": sorted(selector_ids), "failures": source_failures},
    )

    nodes = documents["nodes"].get("nodes", [])
    node_by_id = {item.get("id"): item for item in nodes}
    allowed_roles = {"product", "thesis", "capability", "actor", "goal", "problem", "outcome", "business_rule"}
    required_roles = {"product": 1, "thesis": 1, "capability": 1, "actor": 4, "goal": 1, "problem": 1, "outcome": 3, "business_rule": 4}
    role_counts = {role: sum(item.get("role") == role for item in nodes) for role in allowed_roles}
    node_failures = [
        str(item.get("id"))
        for item in nodes
        if item.get("role") not in allowed_roles
        or item.get("authority_effect") != "none"
        or not item.get("source_refs")
        or not set(item.get("source_refs", [])).issubset(set(source_ids))
        or not item.get("owner_route")
        or item.get("evidence_confidence") not in {"low", "medium", "high"}
        or item.get("commitment_confidence") not in {"open", "conditional", "committed"}
        or not isinstance(item.get("forbidden_collapse"), str)
        or not isinstance(item.get("open_questions"), list)
    ]
    record(
        "node-model-closure",
        len(nodes) == 16 and len(node_by_id) == 16 and role_counts == required_roles and not node_failures,
        {"node_count": len(nodes), "role_counts": role_counts, "failures": node_failures},
    )

    capability = documents["capability"]
    handled = load(LAB / "ontology-lifecycle/definitions/cal-ontology-runtime-integration-epoch-001/handled-definitions.json")
    handled_ids = {item.get("record_id") for item in handled.get("records", [])}
    capability_refs = (
        set(capability.get("outcome_refs", []))
        | set(capability.get("participant_refs", []))
        | set(capability.get("consumer_refs", []))
        | {capability.get("product_ref")}
    )
    record(
        "product-capability-closure",
        capability.get("capability_id") == CAPABILITY_ID
        and node_by_id.get(CAPABILITY_ID, {}).get("role") == "capability"
        and capability_refs.issubset(set(node_by_id))
        and set(capability.get("definition_binding_refs", [])) == EXPECTED_DEFINITION_BINDINGS == handled_ids
        and len(capability.get("owner_routes", [])) == 5
        and capability.get("lifecycle_posture", {}).get("status") == "authored-candidate-awaiting-owner-admission"
        and capability.get("adoption_state") == "not-adopted"
        and capability.get("authority_effect") == "none",
        {
            "capability_id": capability.get("capability_id"),
            "node_refs_closed": capability_refs.issubset(set(node_by_id)),
            "definition_binding_count": len(capability.get("definition_binding_refs", [])),
            "owner_route_count": len(capability.get("owner_routes", [])),
        },
    )

    relation_doc = documents["relations"]
    vocabulary = relation_doc.get("relation_vocabulary", [])
    vocabulary_by_type = {item.get("type"): item for item in vocabulary}
    relations = relation_doc.get("relations", [])
    relation_ids = [item.get("id") for item in relations]
    relation_failures: list[str] = []
    for relation in relations:
        relation_type = vocabulary_by_type.get(relation.get("type"), {})
        source = node_by_id.get(relation.get("source"), {})
        target = node_by_id.get(relation.get("target"), {})
        if (
            not source
            or not target
            or source.get("role") not in relation_type.get("source_roles", [])
            or target.get("role") not in relation_type.get("target_roles", [])
            or not set(relation.get("source_refs", [])).issubset(set(source_ids))
            or relation.get("authority_effect") != "none"
        ):
            relation_failures.append(str(relation.get("id")))
    record(
        "typed-relation-endpoint-closure",
        len(vocabulary) == 7
        and len(vocabulary_by_type) == 7
        and len(relations) == 15
        and len(relation_ids) == len(set(relation_ids))
        and not relation_failures,
        {"vocabulary_count": len(vocabulary), "relation_count": len(relations), "failures": relation_failures},
    )

    residues = documents["residue"].get("residue", [])
    residue_ids = [item.get("id") for item in residues]
    residue_failures = [
        str(item.get("id"))
        for item in residues
        if not set(item.get("subject_refs", [])).issubset(set(node_by_id))
        or not set(item.get("source_refs", [])).issubset(set(source_ids))
        or item.get("status") not in {"blocked", "deferred", "open"}
    ]
    record(
        "residue-and-successor-closure",
        len(residues) == 4
        and len(residue_ids) == len(set(residue_ids))
        and not residue_failures
        and any(item.get("id") == "CAL-PROD-RES-OWNER-ADMISSION" and item.get("status") == "blocked" for item in residues)
        and any(item.get("id") == "CAL-PROD-RES-BUSINESS-ONTOLOGY" and item.get("status") == "blocked" for item in residues),
        {"residue_count": len(residues), "failures": residue_failures},
    )

    decision = load(LAB / "docs/decisions/0015-d65-definition-candidate-selection/decision.json")
    w8 = load(LAB / "docs/decisions/0012-w8-candidate-acceptance/decision.json")
    record(
        "predecessor-owner-selection-and-w8-boundary",
        decision.get("status") == "selected"
        and decision.get("decision_source", {}).get("token") == "D65DEF-1"
        and decision.get("next_gate") == "G-D65-PRODUCT"
        and w8.get("status") == "selected"
        and w8.get("decision_source", {}).get("selection_token") == "W8ACC-1"
        and w8.get("selection", {}).get("option_id") == "W8ACC-1",
        {
            "definition_selection": decision.get("decision_source", {}).get("token"),
            "definition_next_gate": decision.get("next_gate"),
            "w8_selection": w8.get("decision_source", {}).get("selection_token"),
        },
    )

    request = documents["decision_request"]
    candidate_refs = request.get("candidate_refs", {})
    expected_ref_hashes = {
        "profile_sha256": digest(PROFILE),
        "sources_sha256": digest(SOURCES),
        "product_capability_sha256": digest(CAPABILITY),
        "nodes_sha256": digest(NODES),
        "relations_sha256": digest(RELATIONS),
        "residue_sha256": digest(RESIDUE),
        "schema_sha256": digest(SCHEMA),
        "validator_sha256": digest(Path(__file__)),
    }
    record(
        "owner-decision-gate-prepared",
        request.get("request_id") == "CAL-D65PROD-REQUEST-001"
        and request.get("gate_id") == "G-D65-PRODUCT"
        and request.get("status") == "pending-owner-admission"
        and candidate_refs == expected_ref_hashes
        and {item.get("option_id") for item in request.get("options", [])} == {"D65PROD-1", "D65PROD-2", "D65PROD-3", "D65PROD-4"}
        and request.get("authority_effect") == "none",
        {"request_status": request.get("status"), "candidate_hashes_match": candidate_refs == expected_ref_hashes},
    )

    blocked = profile.get("blocked_outputs", [])
    record(
        "direct-d65-authority-boundary",
        profile.get("authority_effect") == capability.get("authority_effect") == "none"
        and any("Invoke" in item for item in blocked)
        and any("D65-S3" in item for item in blocked)
        and capability.get("adoption_state") == "not-adopted",
        {"blocked_output_count": len(blocked), "adoption_state": capability.get("adoption_state")},
    )

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.product-ontology-validation/v1",
        "ontology_id": profile.get("ontology_id"),
        "capability_id": capability.get("capability_id"),
        "result": result,
        "gate_id": "G-D65-PRODUCT",
        "gate_state": "BLOCK",
        "gate_blocker": "CyberAlchemy product-ontology owner admission is pending." if result == "PASS" else "Product-ontology candidate validation failed.",
        "checks": checks,
        "failed_checks": failed,
        "inputs": [
            {"path": str(path.relative_to(LAB)), "sha256": digest(path)}
            for path in (PROFILE, SOURCES, CAPABILITY, NODES, RELATIONS, RESIDUE, SCHEMA, REQUEST, Path(__file__))
        ],
        "authority_effect": "none",
        "claim_ceiling": "PASS proves only candidate structure, exact selected-source currentness, Product Capability closure, node and typed-relation closure, residue visibility, and a prepared owner gate. It does not admit or adopt D65-S2, make D65-S3 eligible, implement, migrate, cut over, publish, release, deploy, or create external effects.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "ontology_id": receipt["ontology_id"],
        "result": result,
        "failed_checks": failed,
        "gate_id": receipt["gate_id"],
        "gate_state": receipt["gate_state"],
        "gate_blocker": receipt["gate_blocker"],
    }, indent=2, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

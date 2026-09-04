#!/usr/bin/env python3
"""Validate the bounded governed-node Definition Pack."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import render


ROOT = Path(__file__).resolve().parent
RECEIPT = ROOT / "receipts" / "validation.json"
VOICE_FIELDS = {
    "normative_voice",
    "formal_voice",
    "operational_interpretation",
    "plain_language_voice",
    "domain_context_voice",
    "boundary",
}
CHALLENGE_FIELDS = {
    "challenge_response",
    "valid_challenge_modes",
    "contradiction_edges",
    "validation_edges",
    "owner_route",
    "resolution_gate",
    "blocking_questions",
    "challenge_residue_route",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selector_digest(path: Path, selector: str) -> str | None:
    if not re.fullmatch(r"CAV2-D\d+", selector):
        return None
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(selector)}:.*?(?=^## |\Z)", text, re.M | re.S)
    if not match:
        return "missing"
    return hashlib.sha256(match.group(0).encode()).hexdigest()


def main() -> int:
    pack = json.loads((ROOT / "definition-pack.json").read_text(encoding="utf-8"))
    handled = json.loads((ROOT / "handled-definitions.json").read_text(encoding="utf-8"))
    semantics = json.loads((ROOT / "schema-semantics.json").read_text(encoding="utf-8"))
    drift = json.loads((ROOT / "definition-drift-audit.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def record(check_id: str, passed: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    record("pack-shape", pack.get("pack_id") == "DEFINE-PACK-CAL-GOVERNED-ONTOLOGY-NODE-002" and pack.get("authority_effect") == "none", {"pack_id": pack.get("pack_id"), "status": pack.get("status")})

    source_results = []
    source_ids = set()
    for source in pack["source_refs"]:
        source_ids.add(source["source_id"])
        path = Path(source["path"])
        current = path.is_file() and sha(path) == source["sha256"]
        selected = selector_digest(path, source["selector"])
        selector_current = selected is None or selected == source.get("selector_sha256")
        source_results.append({"source_id": source["source_id"], "file_current": current, "selector_current": selector_current})
    record("selected-source-currentness", all(r["file_current"] and r["selector_current"] for r in source_results), source_results)

    material_results = []
    for material in pack["material_refs"].values():
        path = ROOT / material["path"]
        material_results.append({"path": material["path"], "current": path.is_file() and sha(path) == material["sha256"]})
    record("material-currentness", all(r["current"] for r in material_results), material_results)

    records = handled["records"]
    record_ids = [item["record_id"] for item in records]
    concept_ids = [item["concept_id"] for item in records]
    record("definition-identity", len(records) == 23 and len(record_ids) == len(set(record_ids)) and len(concept_ids) == len(set(concept_ids)), {"records": len(records)})
    record("required-concept-closure", set(concept_ids) == set(pack["required_concept_ids"]), {"required": len(pack["required_concept_ids"]), "handled": len(concept_ids)})
    record("definition-voices", all(VOICE_FIELDS <= set(item.get("definition", {})) and all(str(item["definition"][field]).strip() for field in VOICE_FIELDS) for item in records), {"required_voices": sorted(VOICE_FIELDS)})
    record("definition-dispositions", all(item["current_disposition"] in {"reuse", "specialize", "propose", "open"} for item in records), sorted({item["current_disposition"] for item in records}))
    record("definition-source-closure", all(set(item["source_refs"]) <= source_ids and item["source_refs"] for item in records), sorted(source_ids))

    relationships = pack["relationships"]
    relation_ids = [item["relation_id"] for item in relationships]
    endpoint_closure = all(item["source_concept_id"] in concept_ids and item["target_concept_id"] in concept_ids for item in relationships)
    record("relationship-closure", len(relation_ids) == len(set(relation_ids)) and endpoint_closure, {"relationships": len(relationships)})

    semantics_by_name = {item["name"]: item for item in semantics["records"]}
    challenge = semantics_by_name.get("ChallengeContract", {})
    governance = semantics_by_name.get("OntologyGovernanceState", {})
    record("challenge-contract-completeness", set(challenge.get("required_fields", [])) == CHALLENGE_FIELDS, sorted(challenge.get("required_fields", [])))
    record(
        "confidence-axis-separation",
        {"evidence_confidence", "commitment_confidence"} <= set(governance.get("required_fields", []))
        and {"semantic_confidence", "governance_confidence", "aggregate_confidence"} <= set(governance.get("forbidden_fields", []))
        and {"semantic confidence", "governance confidence"} <= {alias for item in records for alias in item.get("rejected_aliases", [])},
        {"required": governance.get("required_fields"), "forbidden": governance.get("forbidden_fields")},
    )

    negative = semantics["negative_witness_requirements"]
    negative_ids = [item["id"] for item in negative]
    failure_ids = {item["expected_failure"] for item in negative}
    required_failures = {"identity-incomplete", "relation-endpoint-integrity", "challenge-contract-incomplete", "confidence-axis-collapse", "exact-reference-digest-mismatch", "fractured-context-cut", "noncanonical-replay-source", "untyped-residue"}
    record("negative-witness-contract", len(negative) == 12 and len(negative_ids) == len(set(negative_ids)) and required_failures <= failure_ids, {"witnesses": len(negative), "failure_ids": sorted(failure_ids)})
    record(
        "implementation-boundary",
        semantics["implementation_boundary"]["json_schema_status"] == "not_evaluable_under_CA2-ROUTE-DEFINE"
        and pack["w1_result"]["G-W1"] == "BLOCK"
        and "not_evaluable" in pack["w1_result"]["SWU-W1-002"],
        {"w1": pack["w1_result"], "implementation": semantics["implementation_boundary"]},
    )

    findings = drift["findings"]
    actual_open = sum(item["status"] in {"open", "not_evaluable-under-current-route", "deferred-to-W7", "open-nonblocking-for-candidate-pack"} for item in findings)
    actual_handled = len(findings) - actual_open
    record("drift-audit-closure", drift["summary"]["finding_count"] == len(findings) and drift["summary"]["open_count"] == actual_open and drift["summary"]["handled_count"] == actual_handled, {"findings": len(findings), "open": actual_open, "handled": actual_handled})

    decision = json.loads(Path(next(item["path"] for item in pack["source_refs"] if item["source_id"] == "SRC-GONA-DECISION")).read_text(encoding="utf-8"))
    proposal_ref = next(item for item in pack["source_refs"] if item["source_id"] == "SRC-PROP-0004")
    record("selected-architecture-binding", decision["selection"]["option_id"] == "GONA-1" and decision["selected_proposal"]["sha256"] == proposal_ref["sha256"], {"option": decision["selection"]["option_id"], "proposal": proposal_ref["sha256"]})

    rendered_results = []
    for name, expected in render.rendered().items():
        path = ROOT / name
        rendered_results.append({"path": name, "current": path.is_file() and path.read_text(encoding="utf-8") == expected})
    record("generated-view-currentness", all(item["current"] for item in rendered_results), rendered_results)

    passed = all(item["result"] == "PASS" for item in checks)
    receipt = {
        "schema_version": "cal.definition-pack-validation-receipt/v1",
        "pack_id": pack["pack_id"],
        "result": "PASS" if passed else "BLOCK",
        "validated_material": {
            "definition_pack_sha256": sha(ROOT / "definition-pack.json"),
            "handled_definitions_sha256": sha(ROOT / "handled-definitions.json"),
            "schema_semantics_sha256": sha(ROOT / "schema-semantics.json"),
            "drift_audit_sha256": sha(ROOT / "definition-drift-audit.json")
        },
        "checks": checks,
        "w1_gate": pack["w1_result"]["G-W1"],
        "claim_ceiling": "PASS validates the bounded candidate Definition Pack, selected-source currentness, semantic closure, and generated views. G-W1 remains BLOCK because definition selection, executable schemas, negative fixtures, and the lifecycle vocabulary are absent."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"DEFINITION_PACK_VALIDATION={receipt['result']}")
    for item in checks:
        print(f"{item['check_id']}={item['result']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

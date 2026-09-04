#!/usr/bin/env python3
"""Validate the CTX-00 context-migration metamodel Definition Pack."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import render


ROOT = Path(__file__).resolve().parent
LAB_ROOT = ROOT.parents[2]
RECEIPT = ROOT / "receipts" / "validation.json"
VOICE_FIELDS = {
    "scientific_formal_voice",
    "formal_model",
    "operational_interpretation",
    "plain_language_voice",
    "domain_context_voice",
    "boundary",
}
EXPECTED_DISPOSITIONS = {
    "cal.coordination-context": "specialize",
    "cal.bounded-context": "propose",
    "cal.ubiquitous-language": "revise",
    "cal.context-map": "propose",
    "cal.capability-instance": "specialize",
    "cal.context-migration-manifest": "propose",
    "cal.context-lineage-record": "propose",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else LAB_ROOT / candidate


def selector_digest(path: Path, selector: str) -> str | None:
    if not re.fullmatch(r"CAV2-D\d+", selector):
        return None
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(selector)}:.*?(?=^## |\Z)", text, re.M | re.S)
    return hashlib.sha256(match.group(0).encode()).hexdigest() if match else "missing"


def main() -> int:
    pack = load(ROOT / "definition-pack.json")
    handled = load(ROOT / "handled-definitions.json")
    audit = load(ROOT / "definition-drift-audit.json")
    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "BLOCK", "detail": detail})

    check(
        "pack-identity",
        pack.get("pack_id") == "DEFINE-PACK-CAL-CONTEXT-MIGRATION-METAMODEL-003"
        and pack.get("status") == "candidate-authored-pending-source-admission-and-owner-review"
        and pack.get("authority_effect") == "none",
        {"pack_id": pack.get("pack_id"), "status": pack.get("status"), "effect": pack.get("authority_effect")},
    )
    direction = pack.get("source_direction", {})
    check(
        "machine-canonical-human-generated",
        set(direction.get("canonical_machine_records", []))
        == {"definition-pack.json", "handled-definitions.json", "definition-drift-audit.json"}
        and set(direction.get("generated_human_projections", []))
        == {"DEFINITION-PACK.md", "DEFINITIONS-INDEX.md"}
        and direction.get("projection_policy") == "generated-only",
        direction,
    )

    source_ids = {item["source_id"] for item in pack.get("source_refs", [])}
    source_results = []
    for source in pack.get("source_refs", []):
        path = resolve(source["path"])
        expected_file = source.get("file_sha256", source.get("sha256"))
        file_current = path.is_file() and sha256(path) == expected_file
        selected = selector_digest(path, source["selector"]) if path.is_file() else "missing-file"
        selector_current = selected is None or selected == source.get("selector_sha256")
        source_results.append(
            {
                "source_id": source["source_id"],
                "file_current": file_current,
                "selector_current": selector_current,
            }
        )
    check("selected-source-currentness", all(item["file_current"] and item["selector_current"] for item in source_results), source_results)
    check("source-identity-unique", len(source_ids) == len(pack.get("source_refs", [])), sorted(source_ids))

    records = handled.get("records", [])
    concept_ids = [item.get("concept_id") for item in records]
    record_ids = [item.get("record_id") for item in records]
    check(
        "concept-closure",
        len(records) == 7
        and len(concept_ids) == len(set(concept_ids))
        and len(record_ids) == len(set(record_ids))
        and set(concept_ids) == set(pack.get("required_concept_ids", [])) == set(EXPECTED_DISPOSITIONS),
        {"records": len(records), "concept_ids": concept_ids},
    )
    actual_dispositions = {item["concept_id"]: item["current_disposition"] for item in records}
    check("disposition-model", actual_dispositions == EXPECTED_DISPOSITIONS, actual_dispositions)
    summary = pack.get("disposition_summary", {})
    flattened = {concept_id: disposition for disposition, ids in summary.items() for concept_id in ids}
    check("disposition-summary-current", flattened == EXPECTED_DISPOSITIONS, flattened)
    check(
        "definition-voices-complete",
        all(
            VOICE_FIELDS == set(item.get("definition", {}))
            and all(str(item["definition"][field]).strip() for field in VOICE_FIELDS)
            for item in records
        ),
        {"required_fields": sorted(VOICE_FIELDS)},
    )
    check(
        "definition-source-closure",
        all(item.get("source_refs") and set(item["source_refs"]) <= source_ids for item in records),
        {item["concept_id"]: item.get("source_refs") for item in records},
    )
    check(
        "candidate-authority-ceiling",
        handled.get("authority_effect") == "none"
        and all(item.get("candidate_status") == "candidate-unadmitted" for item in records),
        {"handled_effect": handled.get("authority_effect"), "statuses": sorted({item.get("candidate_status") for item in records})},
    )

    relations = pack.get("relationships", [])
    relation_ids = [item.get("relation_id") for item in relations]
    check(
        "relationship-closure",
        len(relations) == 6
        and len(relation_ids) == len(set(relation_ids))
        and all(item.get("source_concept_id") in concept_ids and item.get("target_concept_id") in concept_ids for item in relations),
        {"relations": len(relations), "ids": relation_ids},
    )
    boundary_text = " ".join(item["definition"]["boundary"] for item in records)
    check(
        "non-collapse-boundaries",
        all(
            phrase in boundary_text
            for phrase in (
                "not a DDD Bounded Context",
                "not a folder",
                "not a repository-wide dictionary",
                "not a directory tree",
                "not the Product Capability",
                "not source admission",
                "not a migration manifest",
            )
        ),
        boundary_text,
    )

    external_sources = [item for item in pack["source_refs"] if item["repository"] == "domainspec-core"]
    check(
        "external-sources-not-inflated",
        len(external_sources) == 7
        and all("unadmitted" in item["admission_posture"] for item in external_sources),
        {item["source_id"]: item["admission_posture"] for item in external_sources},
    )
    check(
        "promotion-blockers-explicit",
        len(pack.get("promotion_blockers", [])) == 5
        and any("canonical Definition term" in item for item in pack["promotion_blockers"])
        and any("not admitted for CTX-00" in item for item in pack["promotion_blockers"])
        and any("not bound" in item for item in pack["promotion_blockers"]),
        pack.get("promotion_blockers"),
    )

    findings = audit.get("findings", [])
    summary = audit.get("summary", {})
    open_count = sum(item.get("status") == "open" for item in findings)
    check(
        "drift-audit-closure",
        len(findings) == 9
        and summary.get("finding_count") == 9
        and summary.get("open_count") == open_count == 9
        and summary.get("handled_count") == 0
        and summary.get("promotion_ready") is False,
        {"findings": len(findings), "summary": summary},
    )

    registry = load(LAB_ROOT / "authority/definitions/registry.json")
    check(
        "canonical-registry-unchanged-empty",
        sha256(LAB_ROOT / "authority/definitions/registry.json") == "ed7575bd0754136c3075ba1a8d132d4673f2b6f6c1fc258c3734debc8c51b33f"
        and registry.get("entries") == [],
        {"sha256": sha256(LAB_ROOT / "authority/definitions/registry.json"), "entries": len(registry.get("entries", []))},
    )
    definition_type_decision = load(LAB_ROOT / "docs/decisions/0015-definition-v1-admission/decision.json")
    check(
        "definition-v1-admitted-term-absent",
        definition_type_decision.get("status") == "owner-admitted"
        and definition_type_decision.get("admitted_contract", {}).get("artifact_type_ref") == "cal.artifact-type.definition/v1"
        and any(item.get("residue_id") == "CAL-DEFV1-R7" for item in definition_type_decision.get("residue_transition", {}).get("remaining", [])),
        {"status": definition_type_decision.get("status"), "remaining": definition_type_decision.get("residue_transition", {}).get("remaining")},
    )
    placement = load(LAB_ROOT / "docs/decisions/0016-ontology-lifecycle-context-placement/decision.json")
    check(
        "context-placement-binding",
        placement.get("selection", {}).get("option_id") == "OLC-2-SEPARATE-BOUNDED-CONTEXT"
        and placement.get("selected_context_model", {}).get("bounded_context_candidate_id") == "CAL-BC-ONTOLOGY-LIFECYCLE"
        and placement.get("selected_context_model", {}).get("governance_boundary", {}).get("context_map_pattern") == "unresolved",
        {"selection": placement.get("selection"), "model": placement.get("selected_context_model")},
    )

    rendered_a = render.rendered()
    rendered_b = render.rendered()
    check("two-run-render-determinism", rendered_a == rendered_b, sorted(rendered_a))
    projection_results = []
    for name, expected in rendered_a.items():
        path = ROOT / name
        projection_results.append({"path": name, "current": path.is_file() and path.read_text(encoding="utf-8") == expected})
    check("generated-projection-currentness", all(item["current"] for item in projection_results), projection_results)

    passed = all(item["result"] == "PASS" for item in checks)
    receipt = {
        "schema_version": "cal.definition-pack-validation-receipt/v1",
        "pack_id": pack.get("pack_id"),
        "result": "PASS" if passed else "BLOCK",
        "authority_effect": "none",
        "validated_material": {
            "definition_pack_sha256": sha256(ROOT / "definition-pack.json"),
            "handled_definitions_sha256": sha256(ROOT / "handled-definitions.json"),
            "definition_drift_audit_sha256": sha256(ROOT / "definition-drift-audit.json"),
            "definition_pack_projection_sha256": sha256(ROOT / "DEFINITION-PACK.md") if (ROOT / "DEFINITION-PACK.md").is_file() else None,
            "definitions_index_projection_sha256": sha256(ROOT / "DEFINITIONS-INDEX.md") if (ROOT / "DEFINITIONS-INDEX.md").is_file() else None,
        },
        "checks": checks,
        "promotion_ready": False,
        "claim_ceiling": "PASS proves only current source bindings, candidate semantic closure, explicit blockers, and deterministic generated views. It does not admit sources, definitions, owners, artifact types, contexts, context maps, migrations, implementations, publication, or deployment.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"DEFINITION_PACK_VALIDATION={receipt['result']}")
    print(f"CHECKS={sum(item['result'] == 'PASS' for item in checks)}/{len(checks)}")
    for item in checks:
        if item["result"] != "PASS":
            print(f"{item['check_id']}={item['result']}: {item['detail']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Collect-all validation for the Definition and CTX-00 semantic candidate set."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import jsonschema

import render as candidate_renderer

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SOURCE_REPO = Path("/home/vrondelli/projects/domainspec-core")
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def h2_digest(path: Path, selector: str) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.startswith(f"## {selector}:")]
    if len(starts) != 1:
        return None
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return hashlib.sha256("".join(lines[start:end]).encode()).hexdigest()


def semantic_rules(record: dict) -> set[str]:
    failures: set[str] = set()
    if record.get("context_identity_source") == "directory":
        failures.add("explicit-context-identity-required")
    if "canonical_kind" in record:
        failures.add("no-redundant-canonical-axis")
    if "upstream_context" in record and not any(
        rel.get("from_ref") == record.get("upstream_context") or rel.get("to_ref") == record.get("upstream_context")
        for rel in record.get("typed_relations", [])
    ):
        failures.add("dependent-classification-requires-explicit-relation")
    if "folder_label" in record:
        failures.add("generated-label-is-not-canonical")
    return failures


def apply_fixture(base: dict, fixture: dict) -> dict:
    mutated = copy.deepcopy(base)
    operation = fixture["mutation"]["operation"]
    if operation == "remove-explicit-context-identity-and-infer-from-directory":
        mutated["context_identity_source"] = "directory"
    else:
        mutated[fixture["mutation"]["field"]] = fixture["mutation"]["value"]
    return mutated


def main() -> int:
    candidate = load(ROOT / "candidate.json")
    schema_path = LAB / "authority/artifact-types/definition/v1/schema.json"
    generator_path = LAB / "authority/artifact-types/definition/v1/generator.py"
    schema = load(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    spec = importlib.util.spec_from_file_location("definition_v1_generator", generator_path)
    definition_generator = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(definition_generator)
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("candidate-identity", candidate["candidate_id"] == "CAL-DEFINITION-CANDIDATE-SET-DEFINITION-CTX00-0001" and candidate["authority_effect"] == "none", {"candidate_id": candidate["candidate_id"], "authority_effect": candidate["authority_effect"]})
    check("definition-schema-current", sha(schema_path) == "c39a2c6fe7bdc2cd306152c1b8c4c9dc045d784e44e35d9d9da4e1517bd03adf", sha(schema_path))
    check("definition-generator-current", sha(generator_path) == "1bac2e064c11eb4b5e945172a21fe6e1635bc48023269fba6dbbdb11d585167c", sha(generator_path))
    check("candidate-generator-current", sha(ROOT / candidate["source_direction"]["generator"]) == candidate["source_direction"]["generator_sha256"], sha(ROOT / candidate["source_direction"]["generator"]))
    artifact_decision_path = LAB / candidate["artifact_type_admission"]["path"]
    artifact_decision = load(artifact_decision_path)
    check("definition-v1-admitted", sha(artifact_decision_path) == candidate["artifact_type_admission"]["sha256"] and artifact_decision["status"] == "owner-admitted" and artifact_decision["authority_effect"] == "definition-v1-artifact-type-admission-only", {"sha256": sha(artifact_decision_path), "status": artifact_decision["status"]})
    owners_path = LAB / "authority/owners/foundation-01/v1/owners.json"
    owners = load(owners_path)
    owner_pairs = {(x["role_id"], x["principal_id"]) for x in owners["role_assignments"]}
    check("definition-owner-bound", ("definition-owner", "person:<vrondelli>") in owner_pairs, sorted([list(x) for x in owner_pairs]))

    definition_records: dict[str, dict] = {}
    schema_errors: dict[str, list[str]] = {}
    digest_results = []
    projection_results = []
    for item in candidate["definitions"]:
        path = LAB / item["path"]
        record = load(path)
        definition_records[item["definition_id"]] = record
        schema_errors[item["definition_id"]] = [err.message for err in validator.iter_errors(record)]
        digest_results.append({"id": item["definition_id"], "expected": item["sha256"], "actual": sha(path), "current": sha(path) == item["sha256"]})
        projection_path = path.with_name("DEFINITION.md")
        expected = definition_generator.render(record)
        projection_results.append({"id": item["definition_id"], "exists": projection_path.is_file(), "parity": projection_path.is_file() and projection_path.read_text(encoding="utf-8") == expected, "two_run_identity": expected == definition_generator.render(record)})
    ids = list(definition_records)
    terms = [record["term"] for record in definition_records.values()]
    check("eight-unique-definitions", len(ids) == 8 and len(set(ids)) == 8 and len(set(terms)) == 8, {"ids": ids, "terms": terms})
    check("foundational-definition-present", "cal.definition.definition" in definition_records, "cal.definition.definition")
    check("all-schema-valid", all(not errors for errors in schema_errors.values()), schema_errors)
    check("all-definition-digests-current", all(x["current"] for x in digest_results), digest_results)
    check("three-voice-contract", all(r["voices"]["plain_language"]["normative"] is False and r["voices"]["domain_context"]["normative"] is False and r["voices"]["scientific_formal"]["normative_statement"] for r in definition_records.values()), sorted(ids))
    check("workspace-voice-current", all(r["voices"]["domain_context"]["workspace_ref"] == "/home/vrondelli/projects/CyberAlchemy-lab" for r in definition_records.values()), {key: value["voices"]["domain_context"]["workspace_ref"] for key, value in definition_records.items()})
    check("definition-projection-parity", all(x["parity"] for x in projection_results), projection_results)
    check("definition-two-run-determinism", all(x["two_run_identity"] for x in projection_results), projection_results)
    check("canonical-axes-closed", all(not semantic_rules(r) for r in definition_records.values()), {key: sorted(semantic_rules(value)) for key, value in definition_records.items()})
    check("explicit-governance-relations", all(r["typed_relations"] and all(rel["relation_kind_ref"] in {"relation.originates-from", "relation.successor-of", "relation.supersedes", "relation.governed-by"} for rel in r["typed_relations"]) for r in definition_records.values()), {key: value["typed_relations"] for key, value in definition_records.items()})

    allowed_sources = {}
    for decision_spec in candidate["source_admission_decisions"]:
        decision_path = LAB / decision_spec["path"]
        decision = load(decision_path)
        check(f"source-decision-{decision_spec['decision_ref']}-current", sha(decision_path) == decision_spec["sha256"] and decision["status"] == "owner-admitted", {"sha256": sha(decision_path), "status": decision["status"]})
        source_items = decision.get("source_admissions", decision.get("admitted_source_selections", []))
        for item in source_items:
            allowed_sources[item["admission_id"]] = (item["selected_sha256"], decision_spec["decision_ref"])
    source_ref_results = []
    for definition_id, record in definition_records.items():
        for source_ref in record["source_refs"]:
            expected = allowed_sources.get(source_ref["source_ref"])
            source_ref_results.append({"definition_id": definition_id, "source_ref": source_ref["source_ref"], "known": expected is not None, "digest_match": expected is not None and source_ref["content_sha256"] == expected[0], "decision_match": expected is not None and source_ref["source_admission_ref"] == expected[1], "posture": source_ref["admission_posture"]})
    check("source-admission-closure", all(x["known"] and x["digest_match"] and x["decision_match"] and x["posture"] == "admitted" for x in source_ref_results), source_ref_results)

    definitions_source = SOURCE_REPO / "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md"
    current_sources = {
        "CAL-SOURCE-ADMISSION-CAV2-D21": h2_digest(definitions_source, "CAV2-D21"),
        "CAL-SOURCE-ADMISSION-CAV2-D33": h2_digest(definitions_source, "CAV2-D33"),
        "CAL-SOURCE-ADMISSION-CAV2-D51": h2_digest(definitions_source, "CAV2-D51"),
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D29": h2_digest(definitions_source, "CAV2-D29"),
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D64": h2_digest(definitions_source, "CAV2-D64"),
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D66": h2_digest(definitions_source, "CAV2-D66"),
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D67": h2_digest(definitions_source, "CAV2-D67"),
        "CAL-SOURCE-ADMISSION-CTX00-LANGUAGE-CONCEPTS": sha(SOURCE_REPO / "cyberAlchemy-v2/language/concepts.json"),
        "CAL-SOURCE-ADMISSION-CTX00-GOVERNANCE-LANGUAGE": sha(SOURCE_REPO / "cyberAlchemy-v2/language/languages/governance-ubiquitous-language.json"),
        "CAL-SOURCE-ADMISSION-CTX00-CONTEXT-PACKAGE": sha(SOURCE_REPO / "cyberAlchemy-v2/context/README.md"),
    }
    check("selected-source-bytes-current", all(current_sources[key] == value[0] for key, value in allowed_sources.items()), {key: {"actual": current_sources.get(key), "expected": value[0]} for key, value in allowed_sources.items()})

    registry_path = ROOT / "registry-postimage.json"
    registry = load(registry_path)
    registry_results = []
    for entry in registry["entries"]:
        item = next((x for x in candidate["definitions"] if x["definition_id"] == entry["definition_id"]), None)
        registry_results.append({"id": entry["definition_id"], "candidate_match": item is not None and item["path"] == entry["path"] and item["sha256"] == entry["sha256"], "file_current": sha(LAB / entry["path"]) == entry["sha256"]})
    check("registry-postimage-current", sha(registry_path) == candidate["postimages"]["registry"]["sha256"] and len(registry_results) == 8 and all(x["candidate_match"] and x["file_current"] for x in registry_results), registry_results)
    index_path = ROOT / "DEFINITIONS-INDEX.md"
    check("generated-index-parity", sha(index_path) == candidate["postimages"]["generated_index"]["sha256"] and index_path.read_text(encoding="utf-8") == candidate_renderer.render_registry(registry).rstrip() + "\n", sha(index_path))
    drift_path = ROOT / "drift-audit-postimage.json"
    drift = load(drift_path)
    check("drift-postimage-current", sha(drift_path) == candidate["postimages"]["drift_audit"]["sha256"] and drift["summary"]["definition_evaluation_blockers_before_owner_decision"] == 0 and drift["summary"]["owner_decision_required"] is True, {"sha256": sha(drift_path), "summary": drift["summary"]})
    drift_view_path = ROOT / "DEFINITION-DRIFT-AUDIT.md"
    check("generated-drift-parity", sha(drift_view_path) == candidate["postimages"]["generated_drift_view"]["sha256"] and drift_view_path.read_text(encoding="utf-8") == candidate_renderer.render_drift(drift).rstrip() + "\n", sha(drift_view_path))
    live_registry_path = LAB / candidate["predecessor_registry"]["path"]
    check("live-registry-preserved", sha(live_registry_path) == candidate["predecessor_registry"]["sha256"] and load(live_registry_path)["entries"] == [], {"sha256": sha(live_registry_path), "entries": len(load(live_registry_path)["entries"])})

    fixture_results = []
    for fixture_path in sorted((ROOT / "fixtures/invalid").glob("*.json")):
        fixture = load(fixture_path)
        base = definition_records[fixture["base_definition_id"]]
        mutated = apply_fixture(base, fixture)
        schema_rejected = bool(list(validator.iter_errors(mutated)))
        semantic_failures = semantic_rules(mutated)
        fixture_results.append({"fixture_id": fixture["fixture_id"], "schema_rejected": schema_rejected, "semantic_failures": sorted(semantic_failures), "expected_rule": fixture["expected_rule"], "rejected": fixture["expected_rule"] in semantic_failures})
    check("hostile-fixtures-rejected", len(fixture_results) == 4 and all(x["rejected"] for x in fixture_results), fixture_results)
    check("hostile-rule-coverage", {x["expected_rule"] for x in fixture_results} == set(candidate["hostile_fixture_rules"]), fixture_results)
    candidate_view = ROOT / "CANDIDATE.md"
    check("candidate-projection-parity", candidate_view.is_file() and candidate_view.read_text(encoding="utf-8") == candidate_renderer.render_candidate(candidate).rstrip() + "\n", str(candidate_view))
    check("decision-gate-not-crossed", candidate["authority_effect"] == "none" and "exact definition-owner decision" in candidate["remaining_gate"], candidate["remaining_gate"])

    failed = [x for x in checks if x["result"] != "PASS"]
    result = "PASS" if not failed else "FAIL"
    evaluation = {
        "DEF-EVAL-01-SCHEMA": "PASS" if all(not errors for errors in schema_errors.values()) else "FAIL",
        "DEF-EVAL-02-VOICES": next(x["result"] for x in checks if x["check_id"] == "three-voice-contract"),
        "DEF-EVAL-03-SOURCES": "PASS" if all(x["result"] == "PASS" for x in checks if x["check_id"] in {"source-admission-closure", "selected-source-bytes-current"}) else "FAIL",
        "DEF-EVAL-04-OWNER": "PASS" if ("definition-owner", "person:<vrondelli>") in owner_pairs else "FAIL",
        "DEF-EVAL-05-PROJECTION": "PASS" if all(x["result"] == "PASS" for x in checks if "projection" in x["check_id"] or "determinism" in x["check_id"]) else "FAIL",
        "DEF-EVAL-06-REGISTRY": "PASS" if all(x["result"] == "PASS" for x in checks if x["check_id"] in {"registry-postimage-current", "generated-index-parity", "drift-postimage-current", "generated-drift-parity", "live-registry-preserved"}) else "FAIL",
        "DEF-EVAL-07-DECISION": "NOT_EVALUABLE"
    }
    eligible = result == "PASS" and all(evaluation[key] == "PASS" for key in list(evaluation)[:6]) and evaluation["DEF-EVAL-07-DECISION"] == "NOT_EVALUABLE"
    receipt = {"schema_version": "cyberalchemy-lab-definition-candidate-validation/v1", "subject": candidate["candidate_id"], "result": result, "promotion_eligibility": "eligible-for-exact-owner-decision" if eligible else "not-eligible", "authority_effect": "none", "evaluation": evaluation, "checks": checks, "summary": {"passed": len(checks) - len(failed), "total": len(checks), "failed": len(failed)}, "claim_ceiling": "PASS proves candidate structure, admitted-source currentness, owner resolution, deterministic projections, synchronized postimages, and hostile rejection only. It does not perform owner review or admission."}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"DEFINITION_CTX00_CANDIDATE_VALIDATION={result}")
    print(f"PROMOTION_ELIGIBILITY={receipt['promotion_eligibility']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

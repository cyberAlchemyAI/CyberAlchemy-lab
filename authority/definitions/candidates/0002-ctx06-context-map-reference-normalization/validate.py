#!/usr/bin/env python3
"""Collect-all validation for the CTX06 reference-normalization Definition candidate."""

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


def semantic_failures(record: dict) -> set[str]:
    failures: set[str] = set()
    if "context_map_refs" in record:
        failures.add("endpoint-map-backreference-forbidden")
    if "canonical_reverse_membership_index" in record:
        failures.add("derived-reverse-index-must-not-be-canonical")
    return failures


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

    check(
        "candidate-identity",
        candidate["candidate_id"] == "CAL-DEFINITION-CANDIDATE-SET-CTX06-REFERENCE-NORMALIZATION-0002"
        and candidate["authority_effect"] == "none",
        {"candidate_id": candidate["candidate_id"], "authority_effect": candidate["authority_effect"]},
    )
    check("definition-schema-current", sha(schema_path) == "c39a2c6fe7bdc2cd306152c1b8c4c9dc045d784e44e35d9d9da4e1517bd03adf", sha(schema_path))
    check("definition-generator-current", sha(generator_path) == "1bac2e064c11eb4b5e945172a21fe6e1635bc48023269fba6dbbdb11d585167c", sha(generator_path))
    check("candidate-generator-current", sha(ROOT / candidate["source_direction"]["generator"]) == candidate["source_direction"]["generator_sha256"], sha(ROOT / candidate["source_direction"]["generator"]))

    artifact_decision_path = LAB / candidate["artifact_type_admission"]["path"]
    artifact_decision = load(artifact_decision_path)
    check(
        "definition-v1-admitted",
        sha(artifact_decision_path) == candidate["artifact_type_admission"]["sha256"]
        and artifact_decision["status"] == "owner-admitted",
        {"sha256": sha(artifact_decision_path), "status": artifact_decision["status"]},
    )

    owners_path = LAB / "authority/owners/foundation-01/v1/owners.json"
    owners = load(owners_path)
    owner_pairs = {(x["role_id"], x["principal_id"]) for x in owners["role_assignments"]}
    check("definition-owner-bound", ("definition-owner", "person:<vrondelli>") in owner_pairs, sorted([list(x) for x in owner_pairs]))

    principle = candidate["admitted_semantic_principle"]
    principle_path = LAB / principle["path"]
    principle_record = load(principle_path)
    check(
        "admitted-anti-inference-principle-current",
        sha(principle_path) == principle["sha256"]
        and principle["principle"] in principle_record["boundaries"]
        and principle_record["definition_id"] == "cal.definition.definition",
        {"actual": sha(principle_path), "expected": principle["sha256"]},
    )

    definition_records: dict[str, dict] = {}
    schema_errors: dict[str, list[str]] = {}
    digest_results = []
    projection_results = []
    predecessor_results = []
    for item in candidate["definitions"]:
        path = LAB / item["path"]
        record = load(path)
        definition_records[item["definition_id"]] = record
        schema_errors[item["definition_id"]] = [err.message for err in validator.iter_errors(record)]
        digest_results.append({"id": item["definition_id"], "expected": item["sha256"], "actual": sha(path), "current": sha(path) == item["sha256"]})
        projection_path = LAB / item["human_projection_path"]
        expected_projection = definition_generator.render(record)
        projection_results.append(
            {
                "id": item["definition_id"],
                "expected_sha256": item["human_projection_sha256"],
                "actual_sha256": sha(projection_path),
                "parity": projection_path.read_text(encoding="utf-8") == expected_projection,
                "two_run_identity": expected_projection == definition_generator.render(record),
            }
        )
        predecessor_path = LAB / item["predecessor_path"]
        predecessor_results.append(
            {
                "id": item["definition_id"],
                "expected": item["predecessor_sha256"],
                "actual": sha(predecessor_path),
                "current": sha(predecessor_path) == item["predecessor_sha256"],
            }
        )

    ids = set(definition_records)
    check("two-successor-definitions", ids == {"cal.definition.bounded-context", "cal.definition.context-map"}, sorted(ids))
    check("successor-versions", all(record["version"] == "2.0.0-candidate.1" for record in definition_records.values()), {key: value["version"] for key, value in definition_records.items()})
    check("all-schema-valid", all(not errors for errors in schema_errors.values()), schema_errors)
    check("all-definition-digests-current", all(x["current"] for x in digest_results), digest_results)
    check("predecessor-bytes-preserved", all(x["current"] for x in predecessor_results), predecessor_results)
    check("three-voice-contract", all(r["voices"]["plain_language"]["normative"] is False and r["voices"]["domain_context"]["normative"] is False and r["voices"]["scientific_formal"]["normative_statement"] for r in definition_records.values()), sorted(ids))
    check("workspace-voice-current", all(r["voices"]["domain_context"]["workspace_ref"] == "/home/vrondelli/projects/CyberAlchemy-lab" for r in definition_records.values()), {key: value["voices"]["domain_context"]["workspace_ref"] for key, value in definition_records.items()})
    check("definition-projection-parity", all(x["parity"] and x["actual_sha256"] == x["expected_sha256"] for x in projection_results), projection_results)
    check("definition-two-run-determinism", all(x["two_run_identity"] for x in projection_results), projection_results)
    check(
        "explicit-successor-relations",
        all(
            any(
                rel["relation_kind_ref"] == "relation.successor-of"
                and rel["from_ref"] == f"{record['definition_id']}@{record['version']}"
                and rel["to_ref"] == next(item["predecessor_ref"] for item in candidate["definitions"] if item["definition_id"] == record["definition_id"])
                for rel in record["typed_relations"]
            )
            for record in definition_records.values()
        ),
        {key: value["typed_relations"] for key, value in definition_records.items()},
    )

    bc = definition_records["cal.definition.bounded-context"]
    cm = definition_records["cal.definition.context-map"]
    bc_tuple = bc["voices"]["scientific_formal"]["formal_expression"].split(");", 1)[0]
    check("bounded-context-does-not-own-map-membership", "context_map_refs" not in bc_tuple and "CanonicalOwner(ContextMapMembership) = ContextMap" in bc["voices"]["scientific_formal"]["formal_expression"], bc_tuple)
    check("context-map-sole-ownership-explicit", "CanonicalOwner(context_refs,relationships) = ContextMap" in cm["voices"]["scientific_formal"]["formal_expression"], cm["voices"]["scientific_formal"]["formal_expression"])
    check("reverse-membership-generated", all("ReverseMembershipIndex" in r["voices"]["scientific_formal"]["formal_expression"] for r in definition_records.values()), {key: value["voices"]["scientific_formal"]["formal_expression"] for key, value in definition_records.items()})
    check("no-new-canonical-axis", all(not semantic_failures(record) for record in definition_records.values()), {key: sorted(semantic_failures(value)) for key, value in definition_records.items()})

    allowed_sources: dict[str, tuple[str, str]] = {}
    for decision_spec in candidate["source_admission_decisions"]:
        decision_path = LAB / decision_spec["path"]
        decision = load(decision_path)
        check(f"source-decision-{decision_spec['decision_ref']}-current", sha(decision_path) == decision_spec["sha256"] and decision["status"] == "owner-admitted", {"sha256": sha(decision_path), "status": decision["status"]})
        for item in decision.get("source_admissions") or decision.get("admitted_source_selections") or []:
            allowed_sources[item["admission_id"]] = (item["selected_sha256"], decision_spec["decision_ref"])

    source_ref_results = []
    for definition_id, record in definition_records.items():
        for source_ref in record["source_refs"]:
            expected = allowed_sources.get(source_ref["source_ref"])
            source_ref_results.append(
                {
                    "definition_id": definition_id,
                    "source_ref": source_ref["source_ref"],
                    "known": expected is not None,
                    "digest_match": expected is not None and source_ref["content_sha256"] == expected[0],
                    "decision_match": expected is not None and source_ref["source_admission_ref"] == expected[1],
                    "posture": source_ref["admission_posture"],
                }
            )
    check("source-admission-closure", all(x["known"] and x["digest_match"] and x["decision_match"] and x["posture"] == "admitted" for x in source_ref_results), source_ref_results)

    definitions_source = SOURCE_REPO / "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md"
    current_sources = {
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D29": h2_digest(definitions_source, "CAV2-D29"),
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D66": h2_digest(definitions_source, "CAV2-D66"),
        "CAL-SOURCE-ADMISSION-CTX00-LANGUAGE-CONCEPTS": sha(SOURCE_REPO / "cyberAlchemy-v2/language/concepts.json"),
        "CAL-SOURCE-ADMISSION-CTX00-GOVERNANCE-LANGUAGE": sha(SOURCE_REPO / "cyberAlchemy-v2/language/languages/governance-ubiquitous-language.json"),
    }
    used_source_ids = {item["source_ref"] for record in definition_records.values() for item in record["source_refs"]}
    check("selected-source-bytes-current", all(current_sources[key] == allowed_sources[key][0] for key in used_source_ids), {key: {"actual": current_sources[key], "expected": allowed_sources[key][0]} for key in sorted(used_source_ids)})

    evidence_results = []
    for item in candidate["admitted_evidence_bindings"]:
        path = LAB / item["path"]
        record = load(path)
        evidence_results.append({"decision_ref": item["decision_ref"], "current": sha(path) == item["sha256"], "status": record["status"], "actual": sha(path), "expected": item["sha256"]})
    check("admitted-evidence-current", all(x["current"] and x["status"] == "owner-admitted" for x in evidence_results), evidence_results)

    registry_path = ROOT / "registry-postimage.json"
    registry = load(registry_path)
    registry_candidate_results = []
    for item in candidate["definitions"]:
        entry = next((x for x in registry["entries"] if x["definition_id"] == item["definition_id"] and x["version"] == item["version"]), None)
        registry_candidate_results.append({"id": item["definition_id"], "match": entry is not None and entry["path"] == item["path"] and entry["sha256"] == item["sha256"] and entry["lifecycle_state"] == "candidate-unadmitted"})
    check("registry-postimage-current", sha(registry_path) == candidate["postimages"]["registry"]["sha256"] and len(registry["entries"]) == 10 and all(x["match"] for x in registry_candidate_results), {"sha256": sha(registry_path), "entries": len(registry["entries"]), "candidates": registry_candidate_results})
    expected_lookup = {
        "cal.definition.bounded-context": "cal.definition.bounded-context@2.0.0-candidate.1",
        "cal.definition.context-map": "cal.definition.context-map@2.0.0-candidate.1",
    }
    check("proposed-current-lookup", all(registry["proposed_current_lookup"].get(key) == value for key, value in expected_lookup.items()), registry["proposed_current_lookup"])
    index_path = ROOT / "DEFINITIONS-INDEX.md"
    check("generated-index-parity", sha(index_path) == candidate["postimages"]["generated_index"]["sha256"] and index_path.read_text(encoding="utf-8") == candidate_renderer.render_registry(registry).rstrip() + "\n", sha(index_path))

    drift_path = ROOT / "drift-audit-postimage.json"
    drift = load(drift_path)
    check("drift-postimage-current", sha(drift_path) == candidate["postimages"]["drift_audit"]["sha256"] and drift["summary"]["definition_evaluation_blockers_before_owner_decision"] == 0 and drift["summary"]["owner_decision_required"] is True, {"sha256": sha(drift_path), "summary": drift["summary"]})
    drift_view_path = ROOT / "DEFINITION-DRIFT-AUDIT.md"
    check("generated-drift-parity", sha(drift_view_path) == candidate["postimages"]["generated_drift_view"]["sha256"] and drift_view_path.read_text(encoding="utf-8") == candidate_renderer.render_drift(drift).rstrip() + "\n", sha(drift_view_path))

    live_registry_path = LAB / candidate["predecessor_registry"]["path"]
    live_drift_path = LAB / candidate["predecessor_drift_audit"]["path"]
    check("live-registry-preserved", sha(live_registry_path) == candidate["predecessor_registry"]["sha256"] and len(load(live_registry_path)["entries"]) == candidate["predecessor_registry"]["entry_count"], {"sha256": sha(live_registry_path), "entries": len(load(live_registry_path)["entries"])})
    check("live-drift-audit-preserved", sha(live_drift_path) == candidate["predecessor_drift_audit"]["sha256"], sha(live_drift_path))

    fixture_results = []
    for fixture_path in sorted((ROOT / "fixtures/invalid").glob("*.json")):
        fixture = load(fixture_path)
        mutated = copy.deepcopy(definition_records[fixture["base_definition_id"]])
        mutated[fixture["mutation"]["field"]] = fixture["mutation"]["value"]
        schema_rejected = bool(list(validator.iter_errors(mutated)))
        failures = semantic_failures(mutated)
        fixture_results.append({"fixture_id": fixture["fixture_id"], "schema_rejected": schema_rejected, "semantic_failures": sorted(failures), "expected_rule": fixture["expected_rule"], "rejected": fixture["expected_rule"] in failures})
    check("hostile-fixtures-rejected", len(fixture_results) == 2 and all(x["schema_rejected"] and x["rejected"] for x in fixture_results), fixture_results)
    check("hostile-rule-coverage", {x["expected_rule"] for x in fixture_results} == set(candidate["hostile_fixture_rules"]), fixture_results)

    candidate_view = ROOT / "CANDIDATE.md"
    check("candidate-projection-parity", candidate_view.is_file() and candidate_view.read_text(encoding="utf-8") == candidate_renderer.render_candidate(candidate).rstrip() + "\n", str(candidate_view))
    check("decision-gate-not-crossed", candidate["authority_effect"] == "none" and "exact definition-owner decision" in candidate["remaining_gate"], candidate["remaining_gate"])

    failed = [x for x in checks if x["result"] != "PASS"]
    result = "PASS" if not failed else "FAIL"
    evaluation = {
        "DEF-EVAL-01-SCHEMA": "PASS" if next(x for x in checks if x["check_id"] == "all-schema-valid")["result"] == "PASS" else "FAIL",
        "DEF-EVAL-02-VOICES": next(x["result"] for x in checks if x["check_id"] == "three-voice-contract"),
        "DEF-EVAL-03-SOURCES": "PASS" if all(x["result"] == "PASS" for x in checks if x["check_id"] in {"source-admission-closure", "selected-source-bytes-current", "admitted-evidence-current"}) else "FAIL",
        "DEF-EVAL-04-OWNER": "PASS" if ("definition-owner", "person:<vrondelli>") in owner_pairs else "FAIL",
        "DEF-EVAL-05-PROJECTION": "PASS" if all(x["result"] == "PASS" for x in checks if "projection" in x["check_id"] or "determinism" in x["check_id"]) else "FAIL",
        "DEF-EVAL-06-REGISTRY-AND-DRIFT": "PASS" if all(x["result"] == "PASS" for x in checks if x["check_id"] in {"registry-postimage-current", "proposed-current-lookup", "generated-index-parity", "drift-postimage-current", "generated-drift-parity", "live-registry-preserved", "live-drift-audit-preserved"}) else "FAIL",
        "DEF-EVAL-07-DECISION": "NOT_EVALUABLE",
    }
    eligible = result == "PASS" and all(evaluation[key] == "PASS" for key in list(evaluation)[:6])
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-candidate-validation/v1",
        "subject": candidate["candidate_id"],
        "result": result,
        "promotion_eligibility": "eligible-for-exact-owner-decision" if eligible else "not-eligible",
        "authority_effect": "none",
        "evaluation": evaluation,
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "total": len(checks), "failed": len(failed)},
        "materials": {
            "candidate_json_sha256": sha(ROOT / "candidate.json"),
            "candidate_md_sha256": sha(candidate_view),
            "definition_digests": {item["definition_id"]: item["sha256"] for item in candidate["definitions"]},
            "registry_postimage_sha256": sha(registry_path),
            "drift_audit_postimage_sha256": sha(drift_path),
        },
        "claim_ceiling": "PASS proves candidate structure, normalized relation ownership, admitted-source currentness, owner resolution, exact predecessor preservation, deterministic projections, synchronized postimages, drift routing, and hostile rejection only. It does not perform owner review or admission, revise artifact types or instances, or authorize migration.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX06_DEFINITION_CANDIDATE_VALIDATION={result}")
    print(f"PROMOTION_ELIGIBILITY={receipt['promotion_eligibility']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    if failed:
        print("FAILED=" + ",".join(x["check_id"] for x in failed))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

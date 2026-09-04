#!/usr/bin/env python3
"""Collect-all validation for the single-decision-checkpoint Definition Pack."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import jsonschema

import render as candidate_renderer

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hostile_failures(subject: dict) -> set[str]:
    failures: set[str] = set()
    if subject.get("kind") == "decision-checkpoint" and subject.get("authority_effect") != "none":
        failures.add("checkpoint-must-not-carry-authority")
    if subject.get("kind") == "user-decision-preference" and subject.get("changes_authority_scope") is True:
        failures.add("preference-must-not-widen-authority")
    if (
        subject.get("kind") == "representation-revision"
        and subject.get("normative_meaning_equal") is True
        and subject.get("semantic_identity_equal") is True
        and subject.get("semantic_epoch_equal") is not True
    ):
        failures.add("representation-only-change-must-not-create-semantic-epoch")
    if subject.get("kind") == "derived-refresh" and subject.get("canonical_input_digest_unchanged") is not True:
        failures.add("derived-refresh-must-not-change-canonical-input")
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
        "candidate-identity-and-ceiling",
        candidate["candidate_id"] == "CAL-DEFINITION-CANDIDATE-SET-SINGLE-DECISION-CHECKPOINT-0003"
        and candidate["authority_effect"] == "none"
        and candidate["status"] == "candidate-authored-awaiting-validation-and-dependency-resolution",
        {"candidate_id": candidate["candidate_id"], "status": candidate["status"], "authority_effect": candidate["authority_effect"]},
    )
    check("definition-schema-current", sha(schema_path) == "c39a2c6fe7bdc2cd306152c1b8c4c9dc045d784e44e35d9d9da4e1517bd03adf", sha(schema_path))
    check("definition-generator-current", sha(generator_path) == "1bac2e064c11eb4b5e945172a21fe6e1635bc48023269fba6dbbdb11d585167c", sha(generator_path))
    local_generator = ROOT / candidate["source_direction"]["generator"]
    check("candidate-generator-current", sha(local_generator) == candidate["source_direction"]["generator_sha256"], sha(local_generator))

    artifact_decision_path = LAB / candidate["artifact_type_admission"]["path"]
    artifact_decision = load(artifact_decision_path)
    check(
        "definition-v1-admitted",
        sha(artifact_decision_path) == candidate["artifact_type_admission"]["sha256"] and artifact_decision["status"] == "owner-admitted",
        {"sha256": sha(artifact_decision_path), "status": artifact_decision["status"]},
    )

    owners = load(LAB / "authority/owners/foundation-01/v1/owners.json")
    owner_pairs = {(item["role_id"], item["principal_id"]) for item in owners["role_assignments"]}
    check("definition-owner-bound", ("definition-owner", "person:<vrondelli>") in owner_pairs, sorted([list(item) for item in owner_pairs]))
    check("role-separation-explicit", "does not collapse" in owners["separation_rule"] or "cannot satisfy" in owners["separation_rule"], owners["separation_rule"])

    source_bindings = {item["source_ref"]: item for item in candidate["admitted_source_bindings"]}
    source_results = []
    for source in candidate["admitted_source_bindings"]:
        source_path = LAB / source["path"]
        decision_path = LAB / source["decision_path"]
        decision = load(decision_path)
        source_results.append({
            "source_ref": source["source_ref"],
            "source_current": sha(source_path) == source["sha256"],
            "decision_current": sha(decision_path) == source["decision_sha256"],
            "decision_status": decision["status"],
        })
    check("admitted-source-bindings-current", all(item["source_current"] and item["decision_current"] and item["decision_status"] == "owner-admitted" for item in source_results), source_results)

    definition_records: dict[str, dict] = {}
    schema_results = []
    digest_results = []
    projection_results = []
    source_ref_results = []
    for item in candidate["definitions"]:
        path = LAB / item["path"]
        projection_path = LAB / item["human_projection_path"]
        record = load(path)
        definition_records[item["definition_id"]] = record
        errors = [error.message for error in validator.iter_errors(record)]
        schema_results.append({"id": item["definition_id"], "errors": errors})
        digest_results.append({"id": item["definition_id"], "expected": item["sha256"], "actual": sha(path)})
        expected_projection = definition_generator.render(record)
        projection_results.append({
            "id": item["definition_id"],
            "digest_current": sha(projection_path) == item["human_projection_sha256"],
            "parity": projection_path.read_text(encoding="utf-8") == expected_projection,
            "deterministic": definition_generator.render(record) == expected_projection,
        })
        for source_ref in record["source_refs"]:
            binding = source_bindings.get(source_ref["source_ref"])
            source_ref_results.append({
                "definition_id": item["definition_id"],
                "source_ref": source_ref["source_ref"],
                "known": binding is not None,
                "digest_match": binding is not None and source_ref["content_sha256"] == binding["sha256"],
                "decision_match": binding is not None and source_ref["source_admission_ref"] == binding["decision_ref"],
                "posture": source_ref["admission_posture"],
            })

    expected_ids = {
        "cal.definition.authority-boundary",
        "cal.definition.decision-bundle",
        "cal.definition.decision-checkpoint",
        "cal.definition.derived-refresh",
        "cal.definition.representation-revision",
        "cal.definition.semantic-epoch",
        "cal.definition.user-decision-preference",
        "cal.definition.workflow-decision-profile",
    }
    check("exact-definition-set", set(definition_records) == expected_ids and len(candidate["definitions"]) == 8, sorted(definition_records))
    check("all-schema-valid", all(not item["errors"] for item in schema_results), schema_results)
    check("all-definition-digests-current", all(item["expected"] == item["actual"] for item in digest_results), digest_results)
    check("three-voice-contract", all(record["voices"]["plain_language"]["normative"] is False and record["voices"]["domain_context"]["normative"] is False and record["voices"]["scientific_formal"]["normative_statement"] for record in definition_records.values()), sorted(definition_records))
    check("domain-context-current", all(record["voices"]["domain_context"]["workspace_ref"] == "/home/vrondelli/projects/CyberAlchemy-lab" for record in definition_records.values()), sorted(definition_records))
    check("definition-projection-parity", all(item["digest_current"] and item["parity"] and item["deterministic"] for item in projection_results), projection_results)
    check("definition-source-closure", all(item["known"] and item["digest_match"] and item["decision_match"] and item["posture"] == "admitted" for item in source_ref_results), source_ref_results)
    check("canonical-terminology", definition_records["cal.definition.decision-checkpoint"]["term"] == "Decision Checkpoint" and "approval boundary" in definition_records["cal.definition.decision-checkpoint"]["aliases"], definition_records["cal.definition.decision-checkpoint"]["aliases"])
    check("orthogonal-authority-and-checkpoint", "Authority Boundary is not Decision Checkpoint." in definition_records["cal.definition.authority-boundary"]["boundaries"] and "Decision Checkpoint is not Authority Boundary." in definition_records["cal.definition.decision-checkpoint"]["boundaries"], "explicit two-way non-collapse")
    check("orthogonal-version-axes", "Semantic Epoch is not Representation Revision." in definition_records["cal.definition.semantic-epoch"]["boundaries"] and "Representation Revision is not Semantic Epoch." in definition_records["cal.definition.representation-revision"]["boundaries"], "explicit two-way non-collapse")
    check("single-or-none-mode", "decision_mode in {none,single}" in definition_records["cal.definition.workflow-decision-profile"]["voices"]["scientific_formal"]["formal_expression"], definition_records["cal.definition.workflow-decision-profile"]["voices"]["scientific_formal"]["formal_expression"])
    check("invalid-preference-blocks", "invalid preference blocks resolution" in definition_records["cal.definition.user-decision-preference"]["voices"]["scientific_formal"]["normative_statement"].lower(), definition_records["cal.definition.user-decision-preference"]["voices"]["scientific_formal"]["normative_statement"])
    check("decision-bundle-preserves-roles", "cannot merge roles" in definition_records["cal.definition.decision-bundle"]["voices"]["scientific_formal"]["normative_statement"], definition_records["cal.definition.decision-bundle"]["voices"]["scientific_formal"]["normative_statement"])

    registry_path = ROOT / "registry-postimage.json"
    registry = load(registry_path)
    pairs = [(item["definition_id"], item["version"]) for item in registry["entries"]]
    new_registry_results = []
    for item in candidate["definitions"]:
        entry = next((entry for entry in registry["entries"] if entry["definition_id"] == item["definition_id"] and entry["version"] == item["version"]), None)
        new_registry_results.append({"id": item["definition_id"], "match": entry is not None and entry["path"] == item["path"] and entry["sha256"] == item["sha256"] and entry["lifecycle_state"] == "candidate-unadmitted"})
    check("registry-postimage-current", sha(registry_path) == candidate["postimages"]["registry"]["sha256"] and len(registry["entries"]) == 18 and len(pairs) == len(set(pairs)) and all(item["match"] for item in new_registry_results), {"sha256": sha(registry_path), "entries": len(registry["entries"]), "new": new_registry_results})
    check("proposed-current-lookup-complete", len(registry["proposed_current_lookup"]) == 16 and all(registry["proposed_current_lookup"].get(definition_id) == f"{definition_id}@1.0.0-candidate.1" for definition_id in expected_ids), registry["proposed_current_lookup"])
    index_path = ROOT / "DEFINITIONS-INDEX.md"
    check("generated-index-parity", sha(index_path) == candidate["postimages"]["generated_index"]["sha256"] and index_path.read_text(encoding="utf-8") == candidate_renderer.render_registry(registry).rstrip() + "\n", sha(index_path))

    drift_path = ROOT / "drift-audit-postimage.json"
    drift = load(drift_path)
    check("drift-postimage-current", sha(drift_path) == candidate["postimages"]["drift_audit"]["sha256"] and drift["summary"]["candidate_definition_count"] == 8 and drift["summary"]["open_definition_dependencies"] == 1, {"sha256": sha(drift_path), "summary": drift["summary"]})
    drift_view_path = ROOT / "DEFINITION-DRIFT-AUDIT.md"
    check("generated-drift-parity", sha(drift_view_path) == candidate["postimages"]["generated_drift_view"]["sha256"] and drift_view_path.read_text(encoding="utf-8") == candidate_renderer.render_drift(drift).rstrip() + "\n", sha(drift_view_path))

    live_registry_path = LAB / candidate["predecessor_registry"]["path"]
    live_drift_path = LAB / candidate["predecessor_drift_audit"]["path"]
    check("live-registry-preserved", sha(live_registry_path) == candidate["predecessor_registry"]["sha256"] and len(load(live_registry_path)["entries"]) == 10, {"sha256": sha(live_registry_path), "entries": len(load(live_registry_path)["entries"])})
    check("live-drift-preserved", sha(live_drift_path) == candidate["predecessor_drift_audit"]["sha256"], sha(live_drift_path))

    fixture_results = []
    for path in sorted((ROOT / "fixtures/invalid").glob("*.json")):
        fixture = load(path)
        failures = hostile_failures(fixture["subject"])
        fixture_results.append({"fixture_id": fixture["fixture_id"], "expected_rule": fixture["expected_rule"], "failures": sorted(failures), "rejected": fixture["expected_rule"] in failures})
    check("hostile-fixtures-rejected", len(fixture_results) == 4 and all(item["rejected"] for item in fixture_results), fixture_results)
    check("hostile-rule-coverage", {item["expected_rule"] for item in fixture_results} == set(candidate["hostile_fixture_rules"]), fixture_results)

    check("derived-rule-complete", all(fragment in candidate["derived_rule"] for fragment in ["none or single", "exactly one Decision Checkpoint", "invalid explicit preference blocks", "retains its own Authority Boundary", "separate dependent workflow", "Derived Refreshes"]), candidate["derived_rule"])
    check("workflow-dependency-fail-closed", candidate["workflow_dependency"]["disposition"] == "open-for-reuse-from-craft" and "before promotion review" in candidate["workflow_dependency"]["required_resolution"], candidate["workflow_dependency"])
    candidate_view = ROOT / "CANDIDATE.md"
    check("candidate-projection-parity", candidate_view.is_file() and candidate_view.read_text(encoding="utf-8") == candidate_renderer.render_candidate(candidate).rstrip() + "\n", str(candidate_view))
    check("decision-gate-not-crossed", candidate["authority_effect"] == "none" and "one exact definition-owner decision" in candidate["remaining_gate"], candidate["remaining_gate"])

    failed = [item for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "FAIL"
    dependency_open = candidate["workflow_dependency"]["disposition"] == "open-for-reuse-from-craft"
    evaluation = {
        "DEF-EVAL-01-SCHEMA": next(item["result"] for item in checks if item["check_id"] == "all-schema-valid"),
        "DEF-EVAL-02-VOICES": next(item["result"] for item in checks if item["check_id"] == "three-voice-contract"),
        "DEF-EVAL-03-SOURCES": "PASS" if all(item["result"] == "PASS" for item in checks if item["check_id"] in {"admitted-source-bindings-current", "definition-source-closure"}) else "FAIL",
        "DEF-EVAL-04-OWNER": "PASS" if ("definition-owner", "person:<vrondelli>") in owner_pairs else "FAIL",
        "DEF-EVAL-05-PROJECTION": "PASS" if all(item["result"] == "PASS" for item in checks if "projection" in item["check_id"] or "generated-" in item["check_id"]) else "FAIL",
        "DEF-EVAL-06-REGISTRY": "PASS" if all(item["result"] == "PASS" for item in checks if item["check_id"] in {"registry-postimage-current", "proposed-current-lookup-complete", "generated-index-parity", "drift-postimage-current", "generated-drift-parity", "live-registry-preserved", "live-drift-preserved"}) else "FAIL",
        "DEF-EVAL-07-DECISION": "NOT_EVALUABLE",
    }
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-candidate-validation/v1",
        "subject": candidate["candidate_id"],
        "result": result,
        "promotion_eligibility": "blocked-by-open-workflow-definition-dependency" if result == "PASS" and dependency_open else ("not-eligible" if result != "PASS" else "eligible-for-exact-owner-decision"),
        "authority_effect": "none",
        "evaluation": evaluation,
        "dependency_evaluation": {"Workflow": "NOT_EVALUABLE", "disposition": candidate["workflow_dependency"]["disposition"], "required_resolution": candidate["workflow_dependency"]["required_resolution"]},
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "total": len(checks), "failed": len(failed)},
        "materials": {
            "candidate_json_sha256": sha(ROOT / "candidate.json"),
            "candidate_md_sha256": sha(candidate_view),
            "definition_digests": {item["definition_id"]: item["sha256"] for item in candidate["definitions"]},
            "registry_postimage_sha256": sha(registry_path),
            "drift_audit_postimage_sha256": sha(drift_path),
        },
        "claim_ceiling": "PASS proves the eight candidate Definitions, admitted-source bindings, orthogonal semantics, deterministic projections, proposed postimages, and hostile rejection only. The Workflow dependency remains NOT_EVALUABLE. This receipt does not admit Definitions, adopt governance, replace CTX08, authorize migration, publish, deploy, or establish a stable release.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SINGLE_DECISION_CHECKPOINT_DEFINITION_VALIDATION={result}")
    print(f"PROMOTION_ELIGIBILITY={receipt['promotion_eligibility']}")
    print(f"WORKFLOW_DEPENDENCY={receipt['dependency_evaluation']['Workflow']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    if failed:
        print("FAILED=" + ",".join(item["check_id"] for item in failed))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

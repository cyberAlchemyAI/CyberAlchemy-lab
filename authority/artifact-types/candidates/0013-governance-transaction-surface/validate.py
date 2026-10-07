#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    manifest = load(ROOT / "carrier-manifest.json")
    checks = []

    def check(check_id: str, passed: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    impacted = load(ROOT / "impacted-carrier-successors.json")
    canonical = [ROOT / "carrier-manifest.json", ROOT / "impacted-carrier-successors.json", ROOT / "admission-target-set.json", ROOT / "representation-closure-repair.json", ROOT / "integrated-example.json", ROOT / "REVIEW.md"]
    for item in manifest["entries"]:
        canonical += [LAB / item["artifact_path"], LAB / item["schema_path"], LAB / item["fixture_path"]]
    for item in impacted["entries"]:
        canonical += [LAB / item["artifact_path"], LAB / item["schema_path"], LAB / item["fixture_path"]]
    before = {str(path): sha(path) for path in canonical}
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    after = {str(path): sha(path) for path in canonical}
    check("deterministic-materialization", before == after, {"files": len(before), "manifest_sha256": sha(ROOT / "carrier-manifest.json")})
    results = []
    for item in manifest["entries"]:
        package = (LAB / item["artifact_path"]).parent
        run = subprocess.run([sys.executable, str(package / "validate.py")], text=True, capture_output=True)
        receipt = load(package / "receipts/validation.json")
        results.append({"artifact_type_ref": item["artifact_type_ref"], "exit": run.returncode, "result": receipt["result"], "artifact_current": sha(package / "artifact.json") == item["artifact_sha256"], "schema_current": sha(package / "schema.json") == item["schema_sha256"], "fixture_current": sha(package / "fixtures/valid/record.json") == item["fixture_sha256"]})
    check("six-carriers-pass", len(results) == 6 and all(row["exit"] == 0 and row["result"] == "PASS" and row["artifact_current"] and row["schema_current"] and row["fixture_current"] for row in results), results)
    import jsonschema
    successor_results = []
    model = load(LAB / manifest["relation_model"]["path"])
    from validate_carrier import roles_for
    for item in impacted["entries"]:
        artifact = load(LAB / item["artifact_path"]); schema = load(LAB / item["schema_path"]); witness = load(LAB / item["fixture_path"])
        errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(witness)]
        predecessor_current = sha(LAB / item["predecessor_artifact_path"]) == item["predecessor_artifact_sha256"]
        if item["kind"] == "typed-relation":
            relation_enum = schema["properties"]["payload"]["properties"]["relation_kind_ref"]["enum"]
            roles_exact = len(relation_enum) == 41 and len(schema["allOf"]) == 41 and "relation.materializes-consequence" in relation_enum
        else:
            expected_roles = roles_for(item["kind"], model)
            roles_exact = artifact["relation_roles"] == expected_roles
        successor_results.append({"artifact_type_ref": item["artifact_type_ref"], "schema_valid": not errors, "artifact_current": sha(LAB / item["artifact_path"]) == item["artifact_sha256"], "schema_current": sha(LAB / item["schema_path"]) == item["schema_sha256"], "fixture_current": sha(LAB / item["fixture_path"]) == item["fixture_sha256"], "predecessor_current": predecessor_current, "roles_exact": roles_exact, "errors": errors})
    check("eight-impacted-successors-pass", len(successor_results) == 8 and all(all(value for key, value in row.items() if key not in {"artifact_type_ref", "errors"}) and not row["errors"] for row in successor_results), successor_results)
    expected = {"authority-boundary", "decision-bundle", "decision-checkpoint", "user-decision-preference", "workflow-decision-profile", "admission-transaction"}
    actual = {item["artifact_type_ref"].removeprefix("cal.artifact-type.").split("/")[0] for item in manifest["entries"]}
    check("exact-gap-closure", actual == expected, sorted(actual))
    relation_receipt = load((LAB / manifest["relation_model"]["path"]).parent / "receipts/validation.json")
    check("relation-model-pass-current", manifest["relation_model"]["sha256"] == sha(LAB / manifest["relation_model"]["path"]) and relation_receipt["result"] == "PASS", relation_receipt["materials"])
    definition_receipt = load((LAB / manifest["admission_transaction_definition"]["path"]).parents[3] / "receipts/validation.json")
    check("definition-pass-current", manifest["admission_transaction_definition"]["sha256"] == sha(LAB / manifest["admission_transaction_definition"]["path"]) and definition_receipt["result"] == "PASS", definition_receipt["materials"])
    example = load(ROOT / "integrated-example.json")
    check("single-checkpoint-boundary", example["human_response_count"] == 1 and example["decision_count"] == 3 and example["new_checkpoint_for_successor"] is False and example["runtime_activations"] == 0 and not example["external_effect_refs"], example)
    tx = load(LAB / "authority/artifact-types/admission-transaction/v1/fixtures/valid/record.json")["payload"]
    check("digest-acyclicity", tx["decision_core_hash_policy"] == "stable-core-excludes-generated-consequence-digests" and tx["output_binding_policy"] == "application-receipt-binds-final-output-digests", {"core": tx["decision_core_hash_policy"], "output": tx["output_binding_policy"]})
    bundle = load(LAB / "authority/artifact-types/decision-bundle/v1/fixtures/valid/record.json")["payload"]
    check("approval-is-decision-outcome", all(item["selected_outcome"] is None for item in bundle["ordered_decisions"]), "Before owner review each Decision.selected_outcome is null; no Approval carrier is created.")
    target_set = load(ROOT / "admission-target-set.json")
    expected_target_digests = [sha(ROOT / "admission-target-set.json"), sha(LAB / manifest["admission_transaction_definition"]["path"]), sha(LAB / "authority/relation-kinds/candidates/0007-governance-transaction-extension/relation-kind-successor-manifest.json")]
    actual_target_digests = [item["target_sha256"] for item in tx["admission_targets"]]
    correction = load(ROOT / "representation-closure-repair.json")
    check("representation-closure-repair", correction["reviewed_target_set_sha256"] == "9324030cacd0e1078129f8cbd3181a9af4b4046032bbd1d54413c97869c7f613" and correction["admission_target_set_sha256"] == sha(ROOT / "admission-target-set.json") and correction["semantic_scope_changed"] is False and correction["new_relation_kinds"] == correction["new_runtime_effects"] == correction["new_external_effects"] == 0, correction)
    check("exact-target-digests", target_set["count"] == 14 and actual_target_digests == expected_target_digests and [item["target_digests"][0]["sha256"] for item in bundle["ordered_decisions"]] == expected_target_digests, {"expected": expected_target_digests, "actual": actual_target_digests})
    check("planned-authorization-boundary", tx["application_state"] == "planned" and tx["resolved_bundle_digest"] is None and tx["authorization_evidence_ref"] is None and tx["authorization_evidence_sha256"] is None and tx["application_receipt_ref"] is None, {key: tx[key] for key in ("application_state", "resolved_bundle_digest", "authorization_evidence_ref", "authorization_evidence_sha256", "application_receipt_ref")})
    transition = load(LAB / "authority/project-state-transitions/candidates/0002-decision-0073-successor/transition.json")
    expected_outputs = {item["semantic_kind"]: item["sha256"] for item in transition["artifact_instances"]}
    actual_outputs = {item["consequence_kind"]: item["output_sha256"] for item in tx["deterministic_consequences"]}
    check("exact-deterministic-consequences", all(actual_outputs[kind] == digest for kind, digest in expected_outputs.items()) and actual_outputs["generated-output"] is None, {"expected": expected_outputs, "actual": actual_outputs})
    serialized = json.dumps({"bundle": bundle, "transaction": tx}, sort_keys=True)
    sentinels = {character * 64 for character in "0123456789abcdef"}
    check("no-sentinel-digests", not any(value in serialized for value in sentinels), "No repeated-character placeholder SHA-256 values remain.")
    check("candidate-no-effect", manifest["status"] == "candidate-awaiting-owner-review" and manifest["authority_effect"] == "none", {"status": manifest["status"], "authority_effect": manifest["authority_effect"]})
    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    receipt = {"schema_version": "cyberalchemy-lab-governance-transaction-surface-validation/v1", "result": result, "authority_effect": "none", "checks": checks, "materials": {"carrier_manifest_sha256": sha(ROOT / "carrier-manifest.json"), "impacted_successors_sha256": sha(ROOT / "impacted-carrier-successors.json"), "admission_target_set_sha256": sha(ROOT / "admission-target-set.json"), "representation_closure_repair_sha256": sha(ROOT / "representation-closure-repair.json"), "integrated_example_sha256": sha(ROOT / "integrated-example.json"), "review_sha256": sha(ROOT / "REVIEW.md")}, "claim_ceiling": "PASS proves six exact candidate carriers, seven endpoint-role successors, one Typed Relation representation-closure successor, the Admission Transaction Definition, relation closure, exact review targets, a single-checkpoint example, digest acyclicity, and hostile rejection. It admits or applies nothing."}
    dump(ROOT / "receipts/validation.json", receipt)
    print(json.dumps({"result": result, "checks": len(checks), **receipt["materials"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

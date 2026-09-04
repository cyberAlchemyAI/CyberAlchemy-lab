#!/usr/bin/env python3
"""Validate Definition/v1 candidate.2 without admitting it."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from render import OUTPUT as ARTIFACT_OUTPUT
from render import SOURCE as ARTIFACT_SOURCE
from render import render as render_artifact


ROOT = Path(__file__).resolve().parent
V1_ROOT = ROOT.parents[1]
LAB_ROOT = ROOT.parents[5]
SOURCE_REPOSITORY = Path("/home/vrondelli/projects/domainspec-core")
SCHEMA = V1_ROOT / "schema.json"
DEFINITION_GENERATOR = V1_ROOT / "generator.py"
ARTIFACT_RENDERER = V1_ROOT / "render.py"
VALID_FIXTURE = V1_ROOT / "fixtures/valid/definition.json"
VALID_PROJECTION = V1_ROOT / "fixtures/valid/DEFINITION.md"
PREDECESSOR = V1_ROOT / "artifact.json"
FOUNDATION_DECISION = LAB_ROOT / "docs/decisions/0013-foundation-01-admission/decision.json"
FOUNDATION_DECISION_RECEIPT = LAB_ROOT / "docs/decisions/0013-foundation-01-admission/receipts/validation.json"
RECEIPT = ROOT / "receipts/validation.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_function(path: Path, module_name: str, function_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def selected_heading_digest(path: Path, selector: str) -> str | None:
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    starts = [index for index, line in enumerate(lines) if line.startswith(f"## {selector}:")]
    if len(starts) != 1:
        return None
    start = starts[0]
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return hashlib.sha256("".join(lines[start:end]).encode("utf-8")).hexdigest()


def resolve_source_path(source: dict) -> Path:
    path = Path(source["path"])
    return path if path.is_absolute() else LAB_ROOT / path


def source_digest(source: dict) -> str | None:
    path = resolve_source_path(source)
    if source.get("digest_scope") == "whole-file":
        return digest(path) if path.is_file() else None
    if source.get("digest_scope") == "markdown-h2-block-v1":
        return selected_heading_digest(path, source["selector"])
    return None


def main() -> int:
    artifact = load(ARTIFACT_SOURCE)
    predecessor = load(PREDECESSOR)
    schema = load(SCHEMA)
    valid = load(VALID_FIXTURE)
    foundation_decision = load(FOUNDATION_DECISION)
    foundation_decision_receipt = load(FOUNDATION_DECISION_RECEIPT)
    render_definition = load_function(DEFINITION_GENERATOR, "definition_v1_instance_generator", "render")
    validator = Draft202012Validator(schema)
    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    check(
        "successor-candidate-non-effectful",
        artifact.get("version") == "1.0.0-candidate.2"
        and artifact.get("status") == "candidate-unadmitted"
        and artifact.get("authority_effect") == "none",
        f"version={artifact.get('version')!r} status={artifact.get('status')!r}",
    )
    lineage = artifact.get("candidate_lineage", {})
    check(
        "candidate-1-predecessor-immutable",
        digest(PREDECESSOR) == lineage.get("predecessor_sha256") == "d30e0fd85dacacbda5e9e9c927c034302a1ebcc18b214da0b45fed1d7b32edd7"
        and predecessor.get("version") == lineage.get("predecessor_version") == "1.0.0-candidate.1"
        and lineage.get("relation_kind_ref") == "relation.successor-of",
        f"predecessor_sha256={digest(PREDECESSOR)} version={predecessor.get('version')!r}",
    )
    bootstrap = artifact.get("bootstrap", {})
    check(
        "bootstrap-predecessor-admitted",
        bootstrap.get("artifact_type_status") == "admitted-predecessor"
        and bootstrap.get("predecessor_ref") == "cal.artifact-type.artifact-type/v1"
        and bootstrap.get("admission_decision_sha256") == digest(FOUNDATION_DECISION),
        json.dumps(bootstrap, sort_keys=True),
    )
    foundation_checks = foundation_decision_receipt.get("checks", [])
    check(
        "foundation-admission-evidence-current",
        digest(FOUNDATION_DECISION) == "2aec4fc4cee04804047dbdfecdf521837b0bd1b006fc6b7ea55f46c9a15b4f52"
        and foundation_decision.get("status") == "owner-admitted"
        and foundation_decision_receipt.get("result") == "PASS"
        and len(foundation_checks) == 31
        and all(item.get("result") == "PASS" for item in foundation_checks),
        f"decision_sha256={digest(FOUNDATION_DECISION)} receipt_result={foundation_decision_receipt.get('result')!r}",
    )

    decision_records = {item["path"]: item["sha256"] for item in foundation_decision.get("admitted_records", [])}
    stale_foundation_bindings = []
    unadmitted_foundation_bindings = []
    for binding_id, binding in artifact.get("foundation_bindings", {}).items():
        path = LAB_ROOT / binding["path"]
        if not path.is_file() or digest(path) != binding["sha256"]:
            stale_foundation_bindings.append(binding_id)
        if binding_id not in {"foundation_decision", "post_admission_drift_audit"} and decision_records.get(binding["path"]) != binding["sha256"]:
            unadmitted_foundation_bindings.append(binding_id)
    check(
        "foundation-binding-digest-closure",
        not stale_foundation_bindings,
        f"stale_or_missing={stale_foundation_bindings}",
    )
    check(
        "foundation-binding-admission-closure",
        not unadmitted_foundation_bindings,
        f"not_in_admission_decision={unadmitted_foundation_bindings}",
    )

    owner_registry = load(LAB_ROOT / artifact["foundation_bindings"]["owner_registry"]["path"])
    assigned_roles = {item["role_id"] for item in owner_registry.get("role_assignments", [])}
    check(
        "accountable-owner-bindings",
        assigned_roles
        == {
            "artifact-mechanics-owner",
            "artifact-type-owner",
            "definition-owner",
            "source-admission-owner",
            "evidence-conformance-owner",
        }
        and {item["principal_id"] for item in owner_registry.get("role_assignments", [])} == {"person:<vrondelli>"},
        f"roles={sorted(assigned_roles)}",
    )
    lifecycle = load(LAB_ROOT / artifact["foundation_bindings"]["lifecycle_profile"]["path"])
    evaluation = load(LAB_ROOT / artifact["foundation_bindings"]["evaluation_profile"]["path"])
    check(
        "lifecycle-evaluation-profiles-bound",
        artifact.get("lifecycle_vocabulary_refs") == [lifecycle.get("record_id")]
        and artifact.get("evaluation_profile_refs") == [evaluation.get("record_id")],
        f"lifecycle={lifecycle.get('record_id')!r} evaluation={evaluation.get('record_id')!r}",
    )

    registry = load(LAB_ROOT / artifact["foundation_bindings"]["definition_registry"]["path"])
    check(
        "canonical-registry-remains-empty",
        registry.get("entries") == []
        and artifact["foundation_bindings"]["definition_registry"]["sha256"] == digest(LAB_ROOT / "authority/definitions/registry.json"),
        f"entries={len(registry.get('entries', []))}",
    )
    drift_binding = artifact["foundation_bindings"]["post_admission_drift_audit"]
    drift_audit = load(LAB_ROOT / drift_binding["path"])
    drift_receipt = load(LAB_ROOT / drift_binding["validation_path"])
    check(
        "post-admission-drift-audit-pass",
        digest(LAB_ROOT / drift_binding["validation_path"]) == drift_binding["validation_sha256"]
        and drift_receipt.get("result") == "PASS"
        and all(item.get("result") == "PASS" for item in drift_receipt.get("checks", []))
        and drift_audit.get("summary", {}).get("undefined_critical_terms") == 1
        and any(item.get("finding_id") == "CAL-DRIFT-001-UNDEFINED-DEFINITION" and item.get("severity") == "blocker" for item in drift_audit.get("findings", [])),
        f"audit_sha256={digest(LAB_ROOT / drift_binding['path'])} receipt_result={drift_receipt.get('result')!r}",
    )

    source_drift = [item["source_id"] for item in artifact.get("source_refs", []) if source_digest(item) != item["sha256"]]
    check("selected-source-currentness", not source_drift, f"stale_or_missing={source_drift}")
    decision_admissions = {item["admission_id"]: item for item in foundation_decision.get("source_admissions", [])}
    external_sources = [item for item in artifact.get("source_refs", []) if item.get("source_repository") == "domainspec-core"]
    bounded_source_mismatches = []
    for source in external_sources:
        admitted = decision_admissions.get(source.get("source_admission_ref"))
        if (
            admitted is None
            or source.get("selector") != admitted.get("selector")
            or source.get("sha256") != admitted.get("selected_sha256")
            or source.get("target_use") != admitted.get("target_use")
            or source.get("admission_decision_ref") != foundation_decision.get("decision_id")
            or source.get("admission_posture") != "admitted-for-bounded-target-use"
        ):
            bounded_source_mismatches.append(source.get("source_id"))
    check(
        "external-source-admission-scope-exact",
        len(external_sources) == 3 and not bounded_source_mismatches,
        f"mismatches={bounded_source_mismatches}",
    )

    check("schema-self-valid", not list(Draft202012Validator.check_schema(schema) or []), "Draft 2020-12 schema accepted")
    check("schema-binding-current", digest(SCHEMA) == artifact.get("schema_digest"), f"actual={digest(SCHEMA)}")
    check(
        "definition-generator-binding-current",
        digest(DEFINITION_GENERATOR) == artifact.get("projection_contract", {}).get("generator_sha256"),
        f"actual={digest(DEFINITION_GENERATOR)}",
    )
    check(
        "artifact-renderer-binding-current",
        digest(ARTIFACT_RENDERER) == artifact.get("source_direction", {}).get("generator_sha256"),
        f"actual={digest(ARTIFACT_RENDERER)}",
    )
    semantics = artifact.get("definition_semantics", {})
    check(
        "artifact-three-voice-semantics",
        all(semantics.get(key) for key in ("scientific_formal_voice", "plain_language_voice", "domain_context_voice"))
        and "CyberAlchemy Lab" in semantics.get("domain_context_voice", ""),
        f"voices={sorted(key for key, value in semantics.items() if value)}",
    )

    valid_errors = sorted(validator.iter_errors(valid), key=lambda error: list(error.path))
    check("valid-fixture-accepted", not valid_errors, "; ".join(error.message for error in valid_errors) or "accepted")
    check(
        "valid-fixture-bindings-current",
        valid.get("schema_digest") == digest(SCHEMA)
        and valid.get("source_direction", {}).get("generator_sha256") == digest(DEFINITION_GENERATOR),
        f"schema={valid.get('schema_digest')} generator={valid.get('source_direction', {}).get('generator_sha256')}",
    )
    check(
        "three-instance-voices-colocated",
        set(valid.get("voices", {})) == {"scientific_formal", "plain_language", "domain_context"}
        and valid["voices"]["plain_language"].get("normative") is False
        and valid["voices"]["domain_context"].get("normative") is False,
        f"voices={sorted(valid.get('voices', {}))}",
    )
    invalid_results: dict[str, list[dict]] = {}
    for path in sorted((V1_ROOT / "fixtures/invalid").glob("*.json")):
        instance = load(path)
        invalid_results[path.name] = [
            {"validator": error.validator, "path": list(error.path), "message": error.message}
            for error in sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
        ]
    expected_negative_reasons = (
        any(
            error["validator"] == "required" and error["path"] == ["voices"] and "domain_context" in error["message"]
            for error in invalid_results.get("missing-domain-context.json", [])
        )
        and any(
            error["validator"] == "additionalProperties" and error["path"] == [] and "unexpected_authority" in error["message"]
            for error in invalid_results.get("additional-property.json", [])
        )
    )
    check(
        "negative-fixtures-rejected-for-intended-reasons",
        expected_negative_reasons,
        json.dumps(invalid_results, sort_keys=True),
    )

    generated_definition_a = render_definition(valid)
    generated_definition_b = render_definition(valid)
    check(
        "definition-projection-determinism-and-parity",
        generated_definition_a == generated_definition_b
        and VALID_PROJECTION.is_file()
        and VALID_PROJECTION.read_text(encoding="utf-8") == generated_definition_a,
        f"sha256={hashlib.sha256(generated_definition_a.encode()).hexdigest()}",
    )
    generated_artifact_a = render_artifact(artifact)
    generated_artifact_b = render_artifact(artifact)
    check(
        "artifact-projection-determinism",
        generated_artifact_a == generated_artifact_b,
        f"sha256={hashlib.sha256(generated_artifact_a.encode()).hexdigest()}",
    )
    check(
        "artifact-projection-parity",
        ARTIFACT_OUTPUT.is_file() and ARTIFACT_OUTPUT.read_text(encoding="utf-8") == generated_artifact_a,
        "ARTIFACT.md must equal the shared v1 renderer output",
    )

    resolved_ids = {item["residue_id"] for item in artifact.get("resolved_residue", [])}
    open_ids = {item["residue_id"] for item in artifact.get("typed_residue", [])}
    check(
        "residue-transition-explicit",
        resolved_ids == {f"CAL-DEFV1-R{index}" for index in range(1, 6)}
        and open_ids == {"CAL-DEFV1-R6", "CAL-DEFV1-R7", "CAL-DEFV1-R8"},
        f"resolved={sorted(resolved_ids)} open={sorted(open_ids)}",
    )
    check(
        "promotion-and-implementation-remain-excluded",
        all(term in artifact.get("claim_ceiling", "") for term in ("does not admit Definition/v1", "does not", "implementation", "first stable version")),
        artifact.get("claim_ceiling", ""),
    )

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-artifact-type-validation/v0",
        "artifact_type_id": artifact.get("artifact_type_id"),
        "artifact_type_version": artifact.get("version"),
        "candidate_epoch": "0002-post-foundation-01",
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {
            "artifact_json_sha256": digest(ARTIFACT_SOURCE),
            "artifact_md_sha256": digest(ARTIFACT_OUTPUT) if ARTIFACT_OUTPUT.is_file() else None,
            "predecessor_artifact_json_sha256": digest(PREDECESSOR),
            "schema_json_sha256": digest(SCHEMA),
            "definition_generator_sha256": digest(DEFINITION_GENERATOR),
            "artifact_renderer_sha256": digest(ARTIFACT_RENDERER),
            "local_render_adapter_sha256": digest(ROOT / "render.py"),
            "valid_fixture_json_sha256": digest(VALID_FIXTURE),
            "valid_fixture_md_sha256": digest(VALID_PROJECTION),
            "foundation_decision_sha256": digest(FOUNDATION_DECISION),
            "foundation_decision_validation_sha256": digest(FOUNDATION_DECISION_RECEIPT),
            "post_admission_drift_audit_sha256": digest(LAB_ROOT / drift_binding["path"]),
            "post_admission_drift_validation_sha256": digest(LAB_ROOT / drift_binding["validation_path"]),
            "validator_sha256": digest(ROOT / "validate.py"),
        },
        "claim_ceiling": artifact.get("claim_ceiling"),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{result}: {sum(item['result'] == 'PASS' for item in checks)}/{len(checks)} checks passed")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

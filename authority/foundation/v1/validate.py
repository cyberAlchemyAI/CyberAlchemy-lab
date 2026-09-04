#!/usr/bin/env python3
"""Validate the Foundation-01 candidate cohort without admitting it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

import render as projections


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SCHEMA_PATH = ROOT / "schema.json"
TYPE_SCHEMA_PATH = LAB / "authority/artifact-types/artifact-type/v1/schema.json"
MANIFEST_PATH = ROOT / "manifest.json"
RECEIPT = ROOT / "receipts/validation.json"


def load(rel: str) -> dict:
    return json.loads((LAB / rel).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_heading_digest(path: Path, selector: str) -> str | None:
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.startswith(f"## {selector}:")]
    if len(starts) != 1:
        return None
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return hashlib.sha256("".join(lines[start:end]).encode("utf-8")).hexdigest()


def validator_for(schema: dict, definition: str) -> Draft202012Validator:
    return Draft202012Validator({"$ref": f"#/$defs/{definition}", "$defs": schema["$defs"]})


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    type_schema = json.loads(TYPE_SCHEMA_PATH.read_text(encoding="utf-8"))
    records = {
        "artifact-type": ("authority/artifact-types/artifact-type/v1/artifact.json", Draft202012Validator(type_schema)),
        "lifecycle": ("authority/profiles/definition/v1/lifecycle.json", validator_for(schema, "lifecycleProfile")),
        "evaluation": ("authority/profiles/definition/v1/evaluation.json", validator_for(schema, "evaluationProfile")),
        "owners": ("authority/owners/foundation-01/v1/owners.json", validator_for(schema, "ownerRegistry")),
        "source-admissions": ("authority/decisions/source-admission/foundation-01/v1/admissions.json", validator_for(schema, "sourceAdmissions")),
        "definition-registry": ("authority/definitions/registry.json", validator_for(schema, "definitionRegistry")),
        "drift-audit": ("authority/definitions/drift-audit.json", validator_for(schema, "driftAudit")),
        "manifest": ("authority/foundation/v1/manifest.json", validator_for(schema, "manifest")),
    }
    data = {name: load(rel) for name, (rel, _) in records.items()}
    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(type_schema)
    check("schemas-self-valid", True, "Foundation and Artifact Type schemas are valid Draft 2020-12 schemas")
    for name, (rel, validator) in records.items():
        errors = sorted(validator.iter_errors(data[name]), key=lambda error: list(error.path))
        check(f"schema-{name}", not errors, "; ".join(error.message for error in errors) or "accepted")

    artifact_type = data["artifact-type"]
    check("artifact-type-schema-binding", artifact_type["schema_digest"] == sha256(TYPE_SCHEMA_PATH),
          f"declared={artifact_type['schema_digest']} actual={sha256(TYPE_SCHEMA_PATH)}")
    registered = artifact_type["registered_types"]
    type_refs = [item["artifact_type_ref"] for item in registered]
    check("registered-type-uniqueness", len(type_refs) == len(set(type_refs)), f"count={len(type_refs)} unique={len(set(type_refs))}")
    stale_type_schemas = []
    for item in registered:
        path = LAB / item["schema_path"]
        if not path.is_file() or sha256(path) != item["schema_sha256"]:
            stale_type_schemas.append(item["artifact_type_ref"])
    check("registered-type-schema-currentness", not stale_type_schemas, f"stale_or_missing={stale_type_schemas}")

    generator_digest = sha256(ROOT / "render.py")
    direction_records = [artifact_type, data["lifecycle"], data["evaluation"], data["owners"], data["source-admissions"], data["definition-registry"], data["drift-audit"], data["manifest"]]
    check("generator-bindings-current", all(item["source_direction"]["generator_sha256"] == generator_digest for item in direction_records),
          f"actual={generator_digest}")

    owners = data["owners"]
    principal_ids = {item["principal_id"] for item in owners["principals"]}
    role_ids = [item["role_id"] for item in owners["role_assignments"]]
    expected_roles = {"artifact-mechanics-owner", "artifact-type-owner", "definition-owner", "source-admission-owner", "evidence-conformance-owner"}
    check("principal-exact", principal_ids == {"person:<vrondelli>"}, f"principals={sorted(principal_ids)}")
    check("role-assignment-closure", set(role_ids) == expected_roles and len(role_ids) == len(set(role_ids)), f"roles={sorted(role_ids)}")
    check("role-principal-closure", all(item["principal_id"] in principal_ids for item in owners["role_assignments"]), "Every assignment resolves to the exact declared principal")

    source_file = Path("/home/vrondelli/projects/domainspec-core/cyberAlchemy-v2/authority/definitions/DEFINITIONS.md")
    admission_results = {}
    for item in data["source-admissions"]["admissions"]:
        admission_results[item["selector"]] = selected_heading_digest(source_file, item["selector"])
    expected_admission_results = {item["selector"]: item["selected_sha256"] for item in data["source-admissions"]["admissions"]}
    check("source-selector-currentness", admission_results == expected_admission_results,
          f"actual={admission_results}")
    check("source-admissions-remain-candidates", all(item["candidate_status"] == "pending-exact-owner-decision" for item in data["source-admissions"]["admissions"]),
          "No candidate source is represented as admitted")

    registry = data["definition-registry"]
    registry_ids = [(item["definition_id"], item["version"]) for item in registry["entries"]]
    check("definition-registry-uniqueness", len(registry_ids) == len(set(registry_ids)), f"entries={len(registry_ids)}")
    stale_definitions = []
    for item in registry["entries"]:
        path = LAB / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            stale_definitions.append(item["definition_id"])
    check("definition-registry-currentness", not stale_definitions, f"stale_or_missing={stale_definitions}")
    audit = data["drift-audit"]
    check("drift-audit-registry-binding", audit["registry_sha256"] == sha256(LAB / audit["registry_ref"]),
          f"declared={audit['registry_sha256']} actual={sha256(LAB / audit['registry_ref'])}")
    check("undefined-definition-visible", audit["summary"]["undefined_critical_terms"] == 1 and any(x["finding_id"] == "CAL-DRIFT-001-UNDEFINED-DEFINITION" and x["severity"] == "blocker" for x in audit["findings"]),
          "The empty registry does not masquerade as semantic completion")

    projection_mismatches = []
    deterministic_failures = []
    for source_rel, output_rel, renderer in projections.SURFACES:
        source = LAB / source_rel
        if not source.is_file():
            continue
        projected_a = renderer(load(source_rel)).rstrip() + "\n"
        projected_b = renderer(load(source_rel)).rstrip() + "\n"
        if projected_a != projected_b:
            deterministic_failures.append(source_rel)
        output = LAB / output_rel
        if not output.is_file() or output.read_text(encoding="utf-8") != projected_a:
            projection_mismatches.append(output_rel)
    check("projection-two-run-determinism", not deterministic_failures, f"failures={deterministic_failures}")
    check("projection-parity", not projection_mismatches, f"mismatches={projection_mismatches}")

    definition_receipt_path = LAB / "authority/artifact-types/definition/v1/receipts/validation.json"
    definition_receipt = json.loads(definition_receipt_path.read_text(encoding="utf-8"))
    check("definition-v1-predecessor-evidence", definition_receipt.get("result") == "PASS",
          f"result={definition_receipt.get('result')}")

    manifest = data["manifest"]
    stale_materials = []
    for item in manifest["materials"]:
        path = LAB / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            stale_materials.append(item["material_id"])
    check("manifest-material-closure", not stale_materials, f"stale_or_missing={stale_materials}")
    d65 = {item["stage"]: item["status"] for item in manifest["d65_boundary"]}
    check("d65-claim-ceiling-explicit", d65.get("exact implementation binding") == "not_evaluable" and d65.get("conformance evidence") == "not_evaluable",
          f"stages={d65}")
    check("admission-remains-future-human-gate", manifest["admission_posture"] == "requires-new-exact-human-decision-over-this-manifest-digest",
          manifest["admission_posture"])

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-foundation-validation/v1",
        "record_id": "CAL-FOUNDATION-01-VALIDATION",
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {
            "manifest_sha256": sha256(MANIFEST_PATH),
            "manifest_projection_sha256": sha256(ROOT / "MANIFEST.md") if (ROOT / "MANIFEST.md").is_file() else None,
            "foundation_schema_sha256": sha256(SCHEMA_PATH),
            "artifact_type_schema_sha256": sha256(TYPE_SCHEMA_PATH),
            "renderer_sha256": sha256(ROOT / "render.py"),
            "validator_sha256": sha256(ROOT / "validate.py")
        },
        "claim_ceiling": manifest["claim_ceiling"]
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

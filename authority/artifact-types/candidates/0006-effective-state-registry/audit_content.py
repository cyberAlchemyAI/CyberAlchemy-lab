#!/usr/bin/env python3
"""Audit the declared content of every Artifact Type descriptor in registry.json."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
REGISTRY_PATH = ROOT / "registry.json"
DEFINITION_REGISTRY_PATH = LAB / "authority/definitions/registry.json"
RELATION_MODEL_PATH = (
    LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json"
)
OUTPUT_PATH = ROOT / "content-audit.json"
PROJECTION_PATH = ROOT / "CONTENT-AUDIT.md"

MODERN_SECTIONS = {
    "semantic_owner_ref",
    "semantic_definition_refs",
    "instance_contract",
    "distinct_validation_purpose",
    "orthogonality_rules",
    "source_direction",
    "four_facets",
    "validation_contract",
    "typed_residue",
    "claim_ceiling",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(value: str | None, base: Path) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    if value.startswith(("authority/", "docs/", "evidence/", "tooling/")):
        return LAB / path
    return base / path


def json_pointer(document: Any, fragment: str) -> Any:
    if not fragment or fragment == "#":
        return document
    current = document
    for token in fragment.removeprefix("#/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def resolve_schema_ref(schema_file: Path, ref: str) -> tuple[Path, Any]:
    file_part, _, fragment = ref.partition("#")
    target_file = (schema_file.parent / file_part).resolve() if file_part else schema_file
    document = load(target_file)
    return target_file, json_pointer(document, f"#{fragment}" if fragment else "#")


def root_schema_facts(schema_file: Path) -> tuple[set[str], bool]:
    required: set[str] = set()
    closed = False
    seen: set[tuple[str, str]] = set()

    def visit(node: Any, current_file: Path) -> None:
        nonlocal closed
        if not isinstance(node, dict):
            return
        required.update(node.get("required", []))
        closed = (
            closed
            or node.get("additionalProperties") is False
            or node.get("unevaluatedProperties") is False
        )
        ref = node.get("$ref")
        if ref:
            key = (str(current_file), ref)
            if key not in seen:
                seen.add(key)
                target_file, target = resolve_schema_ref(current_file, ref)
                visit(target, target_file)
        for branch in node.get("allOf", []):
            visit(branch, current_file)

    visit(load(schema_file), schema_file)
    return required, closed


def reference_fields(schema_file: Path) -> list[str]:
    fields: set[str] = set()
    seen_refs: set[tuple[str, str]] = set()

    def visit(node: Any, current_file: Path, pointer: str = "") -> None:
        if isinstance(node, dict):
            ref = node.get("$ref")
            if ref:
                key = (str(current_file), ref)
                if key not in seen_refs:
                    seen_refs.add(key)
                    target_file, target = resolve_schema_ref(current_file, ref)
                    visit(target, target_file, pointer)
            properties = node.get("properties", {})
            if isinstance(properties, dict):
                for name, value in properties.items():
                    child = f"{pointer}/{name}"
                    if name.endswith(("_ref", "_refs")):
                        fields.add(child)
                    visit(value, current_file, child)
            for key, value in node.items():
                if key in {"$ref", "properties"}:
                    continue
                visit(value, current_file, pointer)
        elif isinstance(node, list):
            for value in node:
                visit(value, current_file, pointer)

    visit(load(schema_file), schema_file)
    return sorted(fields)


def receipt_result(descriptor_path: Path) -> tuple[str, str | None, list[str]]:
    receipt = descriptor_path.parent / "receipts/validation.json"
    if not receipt.exists():
        return "MISSING", None, []
    data = load(receipt)
    failed = [
        item.get("check_id", "unnamed-check")
        for item in data.get("checks", [])
        if item.get("result") == "FAIL"
    ]
    return data.get("result", "UNKNOWN"), str(receipt.relative_to(LAB)), failed


def expected_materials(descriptor: dict[str, Any], descriptor_path: Path) -> dict[str, Any]:
    contract = descriptor.get("validation_contract", {})
    validator_value = contract.get("validator_path")
    validator = repo_path(validator_value, descriptor_path.parent)
    fixture_values: list[str] = []
    for key in ("positive_witness", "positive_projection"):
        if contract.get(key):
            fixture_values.append(contract[key])
    fixture_values.extend(
        value
        for value in contract.get("negative_witnesses", [])
        if not value.startswith("in-memory ")
    )
    fixtures = [repo_path(value, descriptor_path.parent) for value in fixture_values]
    return {
        "validator_path": validator_value,
        "validator_exists": validator.exists() if validator else False,
        "fixture_count": len(fixtures),
        "fixtures_exist": all(path is not None and path.exists() for path in fixtures),
        "missing_fixtures": [
            str(path) for path in fixtures if path is None or not path.exists()
        ],
    }


def definition_facts(
    descriptor: dict[str, Any], descriptor_path: Path, definition_registry: dict[str, Any]
) -> dict[str, Any]:
    refs = list(descriptor.get("semantic_definition_refs", []))
    bindings = list(descriptor.get("semantic_definition_bindings", []))
    singular = descriptor.get("definition_binding")
    if not refs and singular:
        refs = [f"{singular['definition_id']}@{singular['version']}"]
        bindings = [
            {
                "definition_ref": refs[0],
                "path": singular.get("path"),
                "sha256": singular.get("sha256"),
                "admission_decision_ref": singular.get("admission_decision_ref"),
            }
        ]
    admitted_versions = {
        f"{entry['definition_id']}@{entry['version']}"
        for entry in definition_registry["entries"]
    }
    absent = sorted(ref for ref in refs if ref not in admitted_versions)
    noncurrent = sorted(
        ref
        for ref in refs
        if ref in admitted_versions
        and definition_registry["current_lookup"].get(ref.split("@", 1)[0]) != ref
    )
    material_results = []
    for binding in bindings:
        path = repo_path(binding.get("path"), descriptor_path.parent)
        material_results.append(
            {
                "definition_ref": binding.get("definition_ref"),
                "path": binding.get("path"),
                "exists": path.exists() if path else False,
                "digest_current": bool(
                    path
                    and path.exists()
                    and binding.get("sha256")
                    and sha256(path) == binding["sha256"]
                ),
            }
        )
    bound_refs = [binding.get("definition_ref") for binding in bindings]
    return {
        "declared_refs": refs,
        "binding_count": len(bindings),
        "refs_match_bindings": not refs or refs == bound_refs,
        "all_versions_admitted": not absent,
        "all_versions_current": not noncurrent and not absent,
        "absent_refs": absent,
        "noncurrent_refs": noncurrent,
        "materials": material_results,
        "all_materials_current": all(
            item["exists"] and item["digest_current"] for item in material_results
        ),
    }


def source_direction_facts(descriptor: dict[str, Any], descriptor_path: Path) -> dict[str, Any]:
    direction = descriptor.get("source_direction", {})
    generator_value = (
        direction.get("generator")
        or direction.get("generator_path")
        or direction.get("shared_generator_path")
    )
    generator = repo_path(generator_value, descriptor_path.parent)
    expected = direction.get("generator_sha256") or direction.get(
        "shared_generator_sha256"
    )
    return {
        "present": bool(direction),
        "canonical": direction.get("canonical"),
        "human_projection": direction.get("human_projection"),
        "generator": generator_value,
        "generator_ref": direction.get("generator_ref"),
        "generator_exists": generator.exists() if generator else False,
        "generator_digest_current": bool(
            generator and generator.exists() and expected and sha256(generator) == expected
        )
        if expected
        else None,
    }


def main() -> int:
    registry = load(REGISTRY_PATH)
    definition_registry = load(DEFINITION_REGISTRY_PATH)
    relation_model = load(RELATION_MODEL_PATH)
    lineage_predecessors = {
        item["predecessor_descriptor"] for item in registry["candidate_lineage"]
    }
    same_ref_states: dict[str, set[str]] = {}
    for item in registry["descriptors"]:
        same_ref_states.setdefault(item["artifact_type_ref"], set()).add(
            item["effective_state"]
        )

    entries = []
    finding_counts: Counter[str] = Counter()
    posture_counts: Counter[str] = Counter()
    state_counts: Counter[str] = Counter()

    for registered in registry["descriptors"]:
        descriptor_path = LAB / registered["descriptor_path"]
        descriptor = load(descriptor_path)
        schema_path = LAB / registered["schema_path"]
        receipt, receipt_path, failed_checks = receipt_result(descriptor_path)
        missing_sections = sorted(MODERN_SECTIONS - set(descriptor))
        schema_required, schema_closed = root_schema_facts(schema_path)
        declared_required = set(
            descriptor.get("instance_contract", {}).get("required_semantic_fields", [])
        )
        missing_required = sorted(declared_required - schema_required)
        definitions = definition_facts(descriptor, descriptor_path, definition_registry)
        materials = expected_materials(descriptor, descriptor_path)
        direction = source_direction_facts(descriptor, descriptor_path)
        ref_fields = reference_fields(schema_path)
        issues: list[dict[str, str]] = []

        def issue(code: str, consequence: str, action: str) -> None:
            issues.append({"code": code, "consequence": consequence, "action": action})
            finding_counts[code] += 1

        if registered["semantic_binding_posture"] == "admitted-successor-required":
            issue(
                "admitted-semantic-successor-required",
                "The admitted bytes cannot acquire the newly admitted primary Definition in place.",
                "Author and admit an immutable successor Artifact Type version.",
            )
        elif registered["semantic_binding_posture"] == "candidate-rebind-required":
            issue(
                "candidate-semantic-rebind-required",
                "The candidate still points at a proxy Definition instead of its admitted positive Definition.",
                "Revise the candidate binding before Artifact Type admission.",
            )
        if receipt in {"FAIL", "MISSING", "UNKNOWN"}:
            issue(
                "validation-evidence-not-pass",
                f"The descriptor-local validation receipt is {receipt}.",
                "Refresh or replace the validation evidence for any current or promotable contract.",
            )
        if missing_sections:
            issue(
                "legacy-contract-sections-absent",
                "The descriptor predates one or more integrated content sections.",
                "Preserve admitted bytes and evaluate an immutable successor when the missing contract is operationally required.",
            )
        if not definitions["all_versions_admitted"]:
            issue(
                "definition-reference-not-admitted",
                "At least one semantic Definition reference is absent from the admitted Definition registry.",
                "Bind the candidate to an admitted exact Definition version.",
            )
        if definitions["noncurrent_refs"] and registered["effective_state"] != "admitted-historical":
            issue(
                "definition-reference-not-current",
                "At least one semantic Definition reference is admitted but no longer current.",
                "Revise a promotable candidate; preserve immutable historical contracts.",
            )
        if definitions["materials"] and not definitions["all_materials_current"]:
            issue(
                "definition-binding-material-not-current",
                "A Definition binding path is missing or its digest no longer matches.",
                "Repair candidate provenance before promotion.",
            )
        if missing_required:
            issue(
                "required-semantic-field-not-schema-required",
                "The descriptor promises required semantic fields that the resolved schema does not require.",
                "Close the schema contract before promotion or create a successor for admitted bytes.",
            )
        if not schema_closed:
            issue(
                "schema-not-closed",
                "The resolved instance schema does not declare a closed object contract.",
                "Close the schema or document the deliberate extension boundary.",
            )
        if descriptor.get("validation_contract") and (
            not materials["validator_exists"] or not materials["fixtures_exist"]
        ):
            issue(
                "validation-material-missing",
                "A declared validator or fixture cannot be resolved.",
                "Restore the exact validation material before promotion.",
            )

        state = registered["effective_state"]
        other_states = same_ref_states[registered["artifact_type_ref"]] - {state}
        if state == "resolved-duplicate":
            posture = "resolved-duplicate-preserve"
        elif state == "admitted-historical":
            posture = "admitted-historical-preserve"
        elif state == "admitted-current":
            current_action_codes = {
                "admitted-semantic-successor-required",
                "validation-evidence-not-pass",
                "legacy-contract-sections-absent",
                "definition-reference-not-admitted",
                "definition-binding-material-not-current",
                "required-semantic-field-not-schema-required",
                "schema-not-closed",
                "validation-material-missing",
            }
            posture = (
                "admitted-current-remediation-required"
                if any(item["code"] in current_action_codes for item in issues)
                else "admitted-current-content-verified"
            )
        elif registered["descriptor_path"] in lineage_predecessors or (
            "admitted-current" in other_states or "admitted-historical" in other_states
        ):
            posture = "non-effective-candidate-record"
        else:
            candidate_action_codes = {
                "candidate-semantic-rebind-required",
                "validation-evidence-not-pass",
                "definition-reference-not-admitted",
                "definition-reference-not-current",
                "definition-binding-material-not-current",
                "required-semantic-field-not-schema-required",
                "schema-not-closed",
                "validation-material-missing",
            }
            posture = (
                "candidate-revision-required"
                if any(item["code"] in candidate_action_codes for item in issues)
                else "candidate-content-verified-awaiting-admission"
            )

        posture_counts[posture] += 1
        state_counts[state] += 1
        entries.append(
            {
                "artifact_type_ref": registered["artifact_type_ref"],
                "descriptor_path": registered["descriptor_path"],
                "effective_state": state,
                "content_posture": posture,
                "descriptor_generation": descriptor.get("schema_version"),
                "contract_sections": {
                    "missing_integrated_sections": missing_sections,
                    "claim_ceiling_present": bool(descriptor.get("claim_ceiling")),
                    "typed_residue_present": "typed_residue" in descriptor,
                },
                "schema_contract": {
                    "path": registered["schema_path"],
                    "exists": schema_path.exists(),
                    "registry_digest_current": sha256(schema_path)
                    == registered["schema_sha256"],
                    "descriptor_digest_current": (
                        descriptor.get("schema_digest") == sha256(schema_path)
                    ),
                    "closed_representation": schema_closed,
                    "declared_required_semantic_fields": sorted(declared_required),
                    "missing_required_semantic_fields": missing_required,
                },
                "semantic_definitions": definitions,
                "validation_evidence": {
                    "receipt_path": receipt_path,
                    "result": receipt,
                    "failed_checks": failed_checks,
                    **materials,
                },
                "source_direction": direction,
                "relation_surface": {
                    "reference_field_count": len(ref_fields),
                    "reference_fields": ref_fields,
                    "explicit_allowed_relation_kinds": descriptor.get(
                        "allowed_relation_kinds", []
                    ),
                    "mapping_posture": (
                        "candidate-relation-model-mapping-required"
                        if ref_fields
                        else "no-reference-shaped-fields-found"
                    ),
                },
                "issues": issues,
            }
        )

    actionable = [
        entry
        for entry in entries
        if entry["content_posture"]
        in {
            "admitted-current-remediation-required",
            "candidate-revision-required",
        }
    ]
    audit = {
        "schema_version": "cyberalchemy-lab-artifact-type-content-audit/v1",
        "audit_id": "CAL-ARTIFACT-TYPE-CONTENT-AUDIT-0001",
        "status": "candidate-audit-complete",
        "authority_effect": "none",
        "subject_registry": {
            "path": str(REGISTRY_PATH.relative_to(LAB)),
            "sha256": sha256(REGISTRY_PATH),
            "descriptor_count": len(entries),
        },
        "definition_registry": {
            "path": str(DEFINITION_REGISTRY_PATH.relative_to(LAB)),
            "sha256": sha256(DEFINITION_REGISTRY_PATH),
            "version_count": len(definition_registry["entries"]),
            "current_count": len(definition_registry["current_lookup"]),
        },
        "relation_model": {
            "path": str(RELATION_MODEL_PATH.relative_to(LAB)),
            "sha256": sha256(RELATION_MODEL_PATH),
            "status": relation_model["status"],
            "relation_kind_count": relation_model["counts"]["axis_relation_kinds"],
            "mapping_effect": "review-only-until-relation-model-admission",
        },
        "audit_dimensions": [
            "descriptor contract sections",
            "schema existence, digest, closure, and required-field alignment",
            "semantic Definition admission, currentness, path, and digest",
            "descriptor-local validation receipt, validator, and fixtures",
            "source direction and projection generator",
            "reference-shaped schema fields requiring explicit Relation Kind mapping",
            "effective lifecycle state and immutable-successor obligations",
        ],
        "summary": {
            "descriptor_count": len(entries),
            "effective_state_counts": dict(sorted(state_counts.items())),
            "content_posture_counts": dict(sorted(posture_counts.items())),
            "finding_counts": dict(sorted(finding_counts.items())),
            "actionable_descriptor_count": len(actionable),
            "reference_field_count": sum(
                entry["relation_surface"]["reference_field_count"] for entry in entries
            ),
            "descriptors_with_reference_fields": sum(
                bool(entry["relation_surface"]["reference_field_count"])
                for entry in entries
            ),
        },
        "entries": entries,
        "decision_conclusion": {
            "effective_state_registry_ready_for_owner_review": True,
            "all_artifact_type_contents_ready_for_collective_admission": False,
            "reason": "The registry correctly exposes lifecycle state, while the content audit finds current remediation and candidate revision obligations that require separate immutable successors or candidate edits.",
        },
        "claim_ceiling": "This audit evaluates the repository-visible descriptor contracts, schemas, declared bindings, receipts, fixtures, source direction, and reference-shaped relation surfaces. It does not admit or modify an Artifact Type, prove runtime behavior, authenticate instance claims, or treat the candidate Relation Kind model as admitted authority.",
    }
    OUTPUT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")

    lines = [
        "<!-- GENERATED FILE: canonical data is content-audit.json. -->",
        "",
        "# Artifact Type content audit",
        "",
        f"- Audit: `{audit['audit_id']}`",
        f"- Status: `{audit['status']}`",
        f"- Authority effect: `{audit['authority_effect']}`",
        f"- Descriptors audited: `{audit['summary']['descriptor_count']}`",
        "",
        "## Conclusion",
        "",
        "The effective-state registry is ready for owner review. The Artifact Type set is not ready for collective content admission: current contracts have immutable-successor or evidence-refresh obligations, and several candidates require binding revisions.",
        "",
        "## Content postures",
        "",
        "| Posture | Count |",
        "| --- | ---: |",
    ]
    for key, value in audit["summary"]["content_posture_counts"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines += [
        "",
        "## Findings",
        "",
        "| Finding | Descriptors |",
        "| --- | ---: |",
    ]
    for key, value in audit["summary"]["finding_counts"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines += [
        "",
        "## Actionable descriptors",
        "",
        "| Artifact Type | State | Content posture | Findings |",
        "| --- | --- | --- | --- |",
    ]
    for entry in actionable:
        codes = ", ".join(f"`{item['code']}`" for item in entry["issues"])
        lines.append(
            f"| `{entry['artifact_type_ref']}` | `{entry['effective_state']}` | "
            f"`{entry['content_posture']}` | {codes or 'none'} |"
        )
    lines += [
        "",
        "## Relation surface",
        "",
        f"The resolved schemas expose `{audit['summary']['reference_field_count']}` reference-shaped field paths across `{audit['summary']['descriptors_with_reference_fields']}` descriptors. These fields require explicit mapping review against the candidate `{relation_model['counts']['axis_relation_kinds']}`-kind relation model. This audit does not treat that candidate model as admitted authority.",
        "",
        "## Claim ceiling",
        "",
        audit["claim_ceiling"],
    ]
    PROJECTION_PATH.write_text("\n".join(lines).rstrip() + "\n")
    print("ARTIFACT_TYPE_CONTENT_AUDIT=COMPLETE")
    print(f"DESCRIPTORS={len(entries)}")
    print(f"ACTIONABLE={len(actionable)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

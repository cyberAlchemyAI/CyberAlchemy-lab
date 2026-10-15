#!/usr/bin/env python3
"""Validate the Define Shared Meaning Product Capability candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
MATERIAL_FILES = (
    "README.md",
    "profile.json",
    "define-shared-meaning.product-capability.json",
    "contracts/define-shared-meaning.input-contract.json",
    "contracts/define-shared-meaning.definition-pack.output-contract.json",
    "contracts/define-shared-meaning.handled-registry.output-contract.json",
    "policies/define-shared-meaning.context-policy.json",
    "realizations/define-cli.realization.json",
    "obligations/define-shared-meaning.obligations.json",
    "evidence/define-session-runtime/README.md",
    "evidence/define-session-runtime/profile.json",
    "evidence/define-session-runtime/coverage-matrix.json",
    "evidence/define-session-runtime/gaps.json",
    "evidence/define-session-runtime/dry-run-summary.json",
    "evidence/define-session-runtime/schemas/conformance-evidence.schema.json",
    "evidence/define-session-runtime/experiments/cli-chat-continuity.experiment.json",
    "evidence/define-session-runtime/fixtures/pass/cli-chat-continuity.json",
    "evidence/define-session-runtime/fixtures/fail/missing-metadata.json",
    "evidence/define-session-runtime/fixtures/fail/session-mismatch.json",
    "evidence/define-session-runtime/fixtures/fail/revision-digest-mismatch.json",
    "evidence/define-session-runtime/fixtures/fail/question-disappears.json",
    "evidence/define-session-runtime/fixtures/fail/live-run-not-implemented.json",
    "evidence/define-session-runtime/scripts/validate.py",
    "evidence/define-session-runtime/tests/test_negative_mutations.py",
    "scripts/validate.py",
    "tests/test_negative_mutations.py",
)
CLAIM_CEILING = (
    "Closed owner-local record shapes, stable Define Product Capability identity, "
    "exact source and external-record manifest currency, cross-record closure, "
    "explicit obligation coverage, candidate substantial standalone runtime binding, "
    "a byte-current standalone runtime verification plus preserved superseded dry-run fixtures, "
    "and authority_effect none only; no Product Capability "
    "adoption, Definition Pack acceptance, complete realization, behavioral conformance, "
    "definition promotion, product value, execution authority, "
    "publication, release, deployment, or external effect."
)
EXPECTED_IDS = {
    "product": "CA2-CAP-DEFINE-SHARED-MEANING",
    "input": "CA2-CAP-CONTRACT-DEFINE-INPUT",
    "definition_pack": "CA2-CAP-CONTRACT-DEFINE-DEFINITION-PACK",
    "handled_registry": "CA2-CAP-CONTRACT-DEFINE-HANDLED-REGISTRY",
    "policy": "CA2-CAP-POLICY-DEFINE-CONTEXT",
    "binding": "CA2-CAP-BIND-DEFINE-CLI",
    "obligations": "CA2-CAP-OBLIGATIONS-DEFINE-SHARED-MEANING",
}
RECORD_SPECS = (
    ("define-shared-meaning.product-capability.json", "productCapability", "capability_id", EXPECTED_IDS["product"]),
    ("contracts/define-shared-meaning.input-contract.json", "capabilityContract", "contract_id", EXPECTED_IDS["input"]),
    ("contracts/define-shared-meaning.definition-pack.output-contract.json", "capabilityContract", "contract_id", EXPECTED_IDS["definition_pack"]),
    ("contracts/define-shared-meaning.handled-registry.output-contract.json", "capabilityContract", "contract_id", EXPECTED_IDS["handled_registry"]),
    ("policies/define-shared-meaning.context-policy.json", "contextPolicy", "policy_id", EXPECTED_IDS["policy"]),
    ("realizations/define-cli.realization.json", "realizationBinding", "binding_id", EXPECTED_IDS["binding"]),
    ("obligations/define-shared-meaning.obligations.json", "obligationRegistry", "registry_id", EXPECTED_IDS["obligations"]),
)


@lru_cache(maxsize=1)
def current_runtime_verification() -> tuple[int, dict[str, Any] | None, str]:
    verifier = REPOSITORY_ROOT / "cyberAlchemy-v2/implementation/define-cli/scripts/verify-durable-runtime.mjs"
    completed = subprocess.run(
        ["node", str(verifier)],
        cwd=REPOSITORY_ROOT / "cyberAlchemy-v2/implementation/define-cli",
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        receipt = json.loads(completed.stdout)
    except json.JSONDecodeError:
        receipt = None
    return completed.returncode, receipt, completed.stderr.strip()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path, label: str, errors: list[str], overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    key = path.relative_to(PACKAGE_ROOT).as_posix() if path.is_relative_to(PACKAGE_ROOT) else None
    if overrides and key in overrides:
        value = overrides[key]
    else:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot load {label}: {exc}")
            return {}
    if not isinstance(value, dict):
        errors.append(f"{label} must contain one JSON object")
        return {}
    return value


def validate_instance(schema: dict[str, Any], definition: str, value: dict[str, Any], label: str, errors: list[str]) -> None:
    wrapper = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": schema["$defs"],
        "$ref": f"#/$defs/{definition}",
    }
    for violation in sorted(Draft202012Validator(wrapper).iter_errors(value), key=lambda item: list(item.path)):
        locator = ".".join(str(part) for part in violation.path)
        errors.append(f"{label}{'.' + locator if locator else ''}: {violation.message}")


def material_digest(root: Path, errors: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(MATERIAL_FILES):
        path = root / relative
        if not path.is_file():
            errors.append(f"missing material file: {relative}")
            continue
        digest.update(relative.encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def collect_selection_refs(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"source_refs", "evidence_refs", "status_basis_refs"} and isinstance(child, list):
                found.update(item for item in child if isinstance(item, str) and item.startswith("CAP-SEL-"))
            found.update(collect_selection_refs(child))
    elif isinstance(value, list):
        for child in value:
            found.update(collect_selection_refs(child))
    return found


def validate_package(
    package_root: Path = PACKAGE_ROOT,
    repository_root: Path = REPOSITORY_ROOT,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    schema_path = repository_root / "cyberAlchemy-v2/capability/schemas/capability.schema.json"
    schema = load_json(schema_path, "shared schema", errors)
    if schema:
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # jsonschema exposes several schema-error subclasses
            errors.append(f"shared schema invalid: {exc}")

    profile = load_json(package_root / "profile.json", "profile", errors, overrides)
    records: dict[str, dict[str, Any]] = {}
    for relative, definition, id_field, expected_id in RECORD_SPECS:
        value = load_json(package_root / relative, relative, errors, overrides)
        records[relative] = value
        if schema and value:
            validate_instance(schema, definition, value, relative, errors)
        if value.get(id_field) != expected_id:
            errors.append(f"{relative} stable identity changed: expected {expected_id}")
    if schema and profile:
        validate_instance(schema, "defineCapabilityProfile", profile, "profile", errors)

    schema_digest = sha256(schema_path.read_bytes()) if schema_path.is_file() else "0" * 64
    if profile.get("shared_schema_sha256") != schema_digest:
        errors.append("profile shared_schema_sha256 does not match current shared schema")

    product = records[RECORD_SPECS[0][0]]
    input_contract = records[RECORD_SPECS[1][0]]
    definition_pack = records[RECORD_SPECS[2][0]]
    handled_registry = records[RECORD_SPECS[3][0]]
    policy = records[RECORD_SPECS[4][0]]
    binding = records[RECORD_SPECS[5][0]]
    obligation_doc = records[RECORD_SPECS[6][0]]

    if product.get("business_ontology_ref") != "B-DEFINE-PRODUCT-CAPABILITY":
        errors.append("Product Capability must preserve B-DEFINE-PRODUCT-CAPABILITY as business meaning")
    expected_responsibilities = {"product-meaning", "definition-pack-shape", "runtime-contract", "runtime-realization", "next-use-suitability"}
    responsibilities = [route.get("responsibility") for route in product.get("owner_routes", []) if isinstance(route, dict)]
    if set(responsibilities) != expected_responsibilities or len(responsibilities) != len(expected_responsibilities):
        errors.append("Product Capability must contain exactly the five typed owner responsibilities")
    if product.get("input_contract_refs") != [EXPECTED_IDS["input"]]:
        errors.append("Product Capability input contract closure mismatch")
    if product.get("output_contract_refs") != [EXPECTED_IDS["definition_pack"], EXPECTED_IDS["handled_registry"]]:
        errors.append("Product Capability output contract closure mismatch")
    if product.get("context_policy_refs") != [EXPECTED_IDS["policy"]]:
        errors.append("Product Capability ContextPolicy closure mismatch")
    if product.get("realization_binding_refs") != [EXPECTED_IDS["binding"]]:
        errors.append("Product Capability realization binding closure mismatch")
    if product.get("obligation_registry_ref") != EXPECTED_IDS["obligations"]:
        errors.append("Product Capability obligation registry closure mismatch")

    contract_checks = (
        (input_contract, "input", "start"),
        (definition_pack, "output", "definition-pack-complete"),
        (handled_registry, "output", "handled-registry-complete"),
    )
    for contract, direction, readiness in contract_checks:
        if contract.get("capability_ref") != EXPECTED_IDS["product"]:
            errors.append(f"contract {contract.get('contract_id')} has dangling capability_ref")
        if contract.get("direction") != direction or contract.get("readiness_point") != readiness:
            errors.append(f"contract {contract.get('contract_id')} direction/readiness mismatch")
    goal_items = [item for item in input_contract.get("items", []) if item.get("item_id") == "CAP-IN-DEFINE-GOAL-AND-INTENT"]
    if len(goal_items) != 1 or goal_items[0].get("required") is not True:
        errors.append("bounded Goal and intent must remain the single hard start input")
    if any(item.get("required") is True for item in input_contract.get("items", []) if item.get("item_id") != "CAP-IN-DEFINE-GOAL-AND-INTENT"):
        errors.append("non-core missing inputs must remain progressive questions, not hard start gates")

    if policy.get("context_refs") != ["CA2-CONTEXT-DEFINE-SHARED-MEANING"]:
        errors.append("ContextPolicy must reference the exact Define Context")
    if policy.get("resolution_order") != ["explicit-context", "current-window-candidate", "saved-session-candidate"]:
        errors.append("ContextPolicy resolution order changed")
    if policy.get("explicit_context_precedence") is not True:
        errors.append("explicit user Context must have precedence")
    if policy.get("sufficiency_states") != ["sufficient", "insufficient", "indeterminate"] or policy.get("continuation_state") != "sufficient":
        errors.append("ContextPolicy must use three states and permit continuation only for sufficient")

    obligations = obligation_doc.get("obligations", [])
    obligation_ids = [item.get("obligation_id") for item in obligations if isinstance(item, dict)]
    if len(obligation_ids) != len(set(obligation_ids)):
        errors.append("duplicate obligation IDs")
    if len(obligations) != 23:
        errors.append(f"expected 23 Define obligations, found {len(obligations)}")
    gaps = [item for item in obligations if item.get("current_status") == "known-gap"]
    if gaps:
        errors.append("standalone runtime rebinding must not preserve obsolete known-gap statuses")
    if any(item.get("current_status") not in {"not-assessed", "known-gap"} for item in obligations):
        errors.append("candidate obligation registry may not claim satisfied, violated, blocked, or aggregate conformance")

    if binding.get("product_capability_ref") != EXPECTED_IDS["product"]:
        errors.append("realization binding has dangling Product Capability reference")
    if binding.get("agent_capability_ref") != "CA2-AGENT-CAP-DEFINE-CLI" or binding.get("agent_capability_reference_ref") != "CA2-REF-DEFINE-CLI":
        errors.append("realization binding must identify the standalone Define CLI capability")
    if binding.get("coverage") != "substantial" or binding.get("conformance_posture", {}).get("state") != "not-assessed":
        errors.append("Define CLI binding must remain substantial and behaviorally not assessed")
    declared = set(binding.get("declared_support_obligation_refs", []))
    known_gaps = set(binding.get("known_gap_obligation_refs", []))
    if declared & known_gaps or not (declared | known_gaps) <= set(obligation_ids):
        errors.append("realization binding obligation references are overlapping or dangling")
    if known_gaps:
        errors.append("realization binding contains obsolete known-gap obligations")

    source_registry = load_json(repository_root / "cyberAlchemy-v2/capability/sources.json", "central source registry", errors)
    known_selections = {item.get("selection_id") for item in source_registry.get("selections", [])}
    used_selections = set()
    for value in records.values():
        used_selections.update(collect_selection_refs(value))
    dangling_selections = sorted(used_selections - known_selections)
    if dangling_selections:
        errors.append("dangling source selection refs: " + ", ".join(dangling_selections))

    migration = load_json(repository_root / "cyberAlchemy-v2/capability/migration.json", "migration manifest", errors)
    manifest_by_path = {item.get("path"): item for item in migration.get("external_records", []) if isinstance(item, dict)}
    expected_paths = {f"cyberAlchemy-v2/define/capabilities/{relative}" for relative, _, _, _ in RECORD_SPECS}
    if set(manifest_by_path) != expected_paths:
        errors.append("migration external-record manifest paths are not the exact seven owner-local records")
    for relative, definition, id_field, expected_id in RECORD_SPECS:
        repo_relative = f"cyberAlchemy-v2/define/capabilities/{relative}"
        item = manifest_by_path.get(repo_relative, {})
        path = repository_root / repo_relative
        if item.get("schema_def") != definition or item.get("record_id") != expected_id:
            errors.append(f"migration manifest identity/schema mismatch for {relative}")
        if path.is_file() and item.get("sha256") != sha256(path.read_bytes()):
            errors.append(f"migration manifest digest mismatch for {relative}")
    if migration.get("source_projection_ref") != migration.get("target_instance_ref") or migration.get("source_projection_unchanged") is not True:
        errors.append("migration changed Product Capability identity or source projection")

    top_level_values = [profile, *records.values(), migration]
    if any(value.get("authority_effect") != "none" for value in top_level_values if value):
        errors.append("authority_effect must remain none across every candidate record")
    if profile.get("adoption_state") != "not-adopted" or profile.get("conformance_state") != "not-assessed":
        errors.append("profile may not claim adoption or conformance")

    runtime_exit, runtime_receipt, runtime_stderr = current_runtime_verification()
    if runtime_receipt is None:
        errors.append(f"cannot parse standalone Define runtime verification: exit={runtime_exit} stderr={runtime_stderr}")
    elif runtime_exit != 0 or runtime_receipt.get("overall") != "PASS":
        errors.append("standalone Define runtime binding is not byte-current and test-passing")
    elif runtime_receipt.get("authority_effect") != "none":
        errors.append("standalone Define runtime verification exceeds its no-effect ceiling")
    warnings.append(
        "evidence/define-session-runtime is a preserved pre-runtime dry-run model; "
        "it is not used as current implementation or conformance evidence"
    )

    checks = [
        "closed shared JSON schemas for profile and seven owner-local records",
        "stable Product Capability, contract, policy, binding, and obligation identities",
        "typed owner-route and cross-record reference closure",
        "progressive input readiness and distinct output artifacts",
        "ordered Context resolution, inference controls, and three-state sufficiency",
        "twenty-three unique obligations with no stale runtime known-gap status",
        "candidate substantial standalone Define runtime binding with behavioral conformance not assessed",
        "central source-selection closure and exact seven-record migration manifest",
        "authority_effect none and no adoption or aggregate conformance claim",
        "byte-current standalone Define runtime verification with local regression tests",
        "superseded dry-run fixtures retained as non-current model evidence",
    ]
    return {
        "schema_ref": "../../capability/schemas/capability.schema.json#/$defs/defineCapabilityValidationReceipt",
        "schema_version": "cav2-define-capability-validation/v1",
        "validated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "PASS" if not errors else "BLOCK",
        "package_root": "cyberAlchemy-v2/define/capabilities",
        "authority_effect": "none",
        "counts": {"records": len(RECORD_SPECS), "obligations": len(obligations), "known_gaps": len(gaps), "checks": len(checks)},
        "shared_schema_sha256": schema_digest,
        "material_digest": material_digest(package_root, errors),
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "claim_ceiling": CLAIM_CEILING,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    receipt = validate_package()
    if args.write_receipt:
        receipts = PACKAGE_ROOT / "receipts"
        receipts.mkdir(parents=True, exist_ok=True)
        stamp = receipt["validated_at"].replace(":", "").replace("-", "").replace(".", "")
        path = receipts / f"validation-{stamp}.json"
        path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        receipt["receipt_path"] = str(path.relative_to(REPOSITORY_ROOT))
    if args.json or args.write_receipt:
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
    else:
        print(f"{receipt['status']} Define capability records={receipt['counts']['records']} obligations={receipt['counts']['obligations']} errors={len(receipt['errors'])}")
        for error in receipt["errors"]:
            print(f"ERROR {error}")
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate the bounded composite work model-first package."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SHARED_CAPABILITY_SCHEMA = REPOSITORY_ROOT / "cyberAlchemy-v2/capability/schemas/capability.schema.json"
MATERIAL_FILES = (
    "README.md",
    "definitions.json",
    "nodes.json",
    "product-capability-support.json",
    "product-capability.json",
    "profile.json",
    "relations.json",
    "residue.json",
    "schemas/work-orchestration.schema.json",
    "scripts/validate.py",
    "sources.json",
    "tests/test_negative_mutations.py",
)
CAPABILITY_ID = "CA2-CAP-EXECUTE-BOUNDED-COMPOSITE-WORK"
BUSINESS_CAPABILITY_ID = "WO-CAP-EXECUTE-BOUNDED-COMPOSITE-WORK"
UNSELECTED_BINDING_ID = "CA2-CAP-BIND-WORK-ORCHESTRATION-UNSELECTED"
OBLIGATION_REGISTRY_ID = "CA2-CAP-OBLIGATIONS-BOUNDED-COMPOSITE-WORK"


def load(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path} must contain one JSON object")
        return {}
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def unique(values: list[str], label: str, errors: list[str]) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        errors.append(f"duplicate {label}: {', '.join(duplicates)}")


def validate_definition(
    instance: Any,
    root_schema: dict[str, Any],
    definition: str,
    label: str,
    errors: list[str],
) -> None:
    candidate = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": root_schema.get("$defs", {}),
        "$ref": f"#/$defs/{definition}",
    }
    try:
        Draft202012Validator.check_schema(candidate)
    except SchemaError as exc:
        errors.append(f"{label} schema is invalid: {exc.message}")
        return
    validator = Draft202012Validator(candidate, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"{label} schema violation at {location}: {error.message}")


def markdown_section(text: str, heading: str) -> str | None:
    lines = text.splitlines(keepends=True)
    starts = [index for index, line in enumerate(lines) if line.rstrip("\r\n") == heading]
    if len(starts) != 1:
        return None
    start = starts[0]
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return "".join(lines[start:end])


def source_selection(source: dict[str, Any], errors: list[str]) -> tuple[bytes, str] | None:
    relative = str(source.get("path", ""))
    path = (REPOSITORY_ROOT / relative).resolve()
    if REPOSITORY_ROOT.resolve() not in path.parents:
        errors.append(f"source escapes repository: {relative}")
        return None
    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"source unreadable: {relative}: {exc}")
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(f"source is not UTF-8 text: {relative}")
        return None
    kind = source.get("selection_kind")
    if kind == "whole-file":
        selected = raw
        selected_text = text
    elif kind == "markdown-section":
        section = markdown_section(text, str(source.get("selector", "")))
        if section is None:
            errors.append(f"source selector does not resolve exactly once: {source.get('source_id')}")
            return None
        selected = section.encode("utf-8")
        selected_text = section
    else:
        errors.append(f"unsupported source selection kind: {kind!r}")
        return None
    if sha256_bytes(selected) != source.get("sha256"):
        errors.append(f"source digest drift: {source.get('source_id')}: {sha256_bytes(selected)}")
    if str(source.get("selector", "")) not in selected_text:
        errors.append(f"source selector text absent: {source.get('source_id')}")
    return selected, selected_text


def check_source_refs(
    refs: Any,
    source_text: dict[str, str],
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(refs, list) or not refs:
        errors.append(f"{label} must have source_refs")
        return
    for index, ref in enumerate(refs):
        if not isinstance(ref, dict) or set(ref) != {"source_id", "selector"}:
            errors.append(f"{label} source_refs[{index}] has invalid shape")
            continue
        source_id = str(ref.get("source_id", ""))
        selector = str(ref.get("selector", ""))
        if source_id not in source_text:
            errors.append(f"{label} source_refs[{index}] has unknown source {source_id!r}")
        elif selector not in source_text[source_id]:
            errors.append(f"{label} source_refs[{index}] selector is absent: {selector!r}")


def check_shared_product_capability(
    product_capability: dict[str, Any],
    shared_schema: dict[str, Any],
    errors: list[str],
) -> None:
    localized = copy.deepcopy(shared_schema)
    try:
        localized["$defs"]["productCapability"]["properties"]["schema_ref"]["const"] = (
            "../capability/schemas/capability.schema.json#/$defs/productCapability"
        )
    except (KeyError, TypeError):
        errors.append("shared capability schema is missing the Product Capability schema_ref contract")
        return
    validate_definition(product_capability, localized, "productCapability", "product capability", errors)


def material_digest(errors: list[str]) -> str:
    actual = sorted(
        path.relative_to(PACKAGE_ROOT).as_posix()
        for path in PACKAGE_ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    if actual != sorted(MATERIAL_FILES):
        errors.append(f"closed material inventory mismatch: expected {len(MATERIAL_FILES)}, observed {len(actual)}")
    digest = hashlib.sha256()
    for relative in sorted(MATERIAL_FILES):
        path = PACKAGE_ROOT / relative
        if not path.is_file():
            errors.append(f"missing material file: {relative}")
            continue
        digest.update(relative.encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def validate() -> dict[str, Any]:
    errors: list[str] = []
    schema = load(PACKAGE_ROOT / "schemas/work-orchestration.schema.json", errors)
    profile = load(PACKAGE_ROOT / "profile.json", errors)
    sources_doc = load(PACKAGE_ROOT / "sources.json", errors)
    definitions_doc = load(PACKAGE_ROOT / "definitions.json", errors)
    product_capability = load(PACKAGE_ROOT / "product-capability.json", errors)
    support = load(PACKAGE_ROOT / "product-capability-support.json", errors)
    nodes_doc = load(PACKAGE_ROOT / "nodes.json", errors)
    relations_doc = load(PACKAGE_ROOT / "relations.json", errors)
    residue_doc = load(PACKAGE_ROOT / "residue.json", errors)
    shared_schema = load(SHARED_CAPABILITY_SCHEMA, errors)

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        errors.append(f"package schema is invalid: {exc.message}")

    for value, definition, label in (
        (profile, "profile", "profile"),
        (sources_doc, "sourceRegistry", "source registry"),
        (definitions_doc, "definitionRegistry", "definition registry"),
        (support, "productCapabilitySupport", "product capability support"),
        (nodes_doc, "nodeRegistry", "node registry"),
        (relations_doc, "relationRegistry", "relation registry"),
        (residue_doc, "residueRegistry", "residue registry"),
    ):
        validate_definition(value, schema, definition, label, errors)
    check_shared_product_capability(product_capability, shared_schema, errors)

    sources = sources_doc.get("sources", [])
    source_ids = [str(item.get("source_id")) for item in sources if isinstance(item, dict)]
    unique(source_ids, "source IDs", errors)
    selected_bytes: dict[str, bytes] = {}
    source_text: dict[str, str] = {}
    for source in sources:
        if not isinstance(source, dict):
            continue
        selection = source_selection(source, errors)
        if selection is not None:
            selected_bytes[str(source.get("source_id"))] = selection[0]
            source_text[str(source.get("source_id"))] = selection[1]

    bindings = definitions_doc.get("canonical_bindings", [])
    binding_refs = {item.get("definition_ref") for item in bindings if isinstance(item, dict)}
    if binding_refs != {"CAV2-D65", "CAV2-D67"} or len(bindings) != 2:
        errors.append("definition registry must bind exactly CAV2-D65 and CAV2-D67")
    source_by_id = {item.get("source_id"): item for item in sources if isinstance(item, dict)}
    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        source = source_by_id.get(binding.get("source_ref"))
        if source is None or source.get("sha256") != binding.get("selector_sha256"):
            errors.append(f"definition binding digest mismatch: {binding.get('definition_ref')}")
    terms = definitions_doc.get("local_terms", [])
    term_ids = [str(item.get("term_id")) for item in terms if isinstance(item, dict)]
    unique(term_ids, "local term IDs", errors)

    nodes = nodes_doc.get("nodes", [])
    node_ids = [str(item.get("id")) for item in nodes if isinstance(item, dict)]
    unique(node_ids, "node IDs", errors)
    node_id_set = set(node_ids)
    node_roles = {str(item.get("id")): str(item.get("role")) for item in nodes if isinstance(item, dict)}
    capability_nodes = [item for item in nodes if isinstance(item, dict) and item.get("role") == "product_capability"]
    if len(capability_nodes) != 1 or capability_nodes[0].get("id") != BUSINESS_CAPABILITY_ID:
        errors.append("package must contain exactly one Product Capability business node")
    for node in nodes:
        if isinstance(node, dict):
            check_source_refs(node.get("source_refs"), source_text, f"node {node.get('id')}", errors)

    if product_capability.get("capability_id") != profile.get("product_capability_ref") != CAPABILITY_ID:
        errors.append("Product Capability identity does not match package profile")
    if product_capability.get("capability_id") != CAPABILITY_ID:
        errors.append("unexpected Product Capability identity")
    if product_capability.get("product_ref") != "CA2-PRODUCT-CYBERALCHEMY":
        errors.append("Product Capability must remain anchored to CyberAlchemy")
    business_refs = {
        str(product_capability.get("product_ref")),
        str(product_capability.get("business_ontology_ref")),
        *map(str, product_capability.get("outcome_refs", [])),
        *map(str, product_capability.get("participant_refs", [])),
        *map(str, product_capability.get("consumer_refs", [])),
        *map(str, product_capability.get("input_contract_refs", [])),
        *map(str, product_capability.get("output_contract_refs", [])),
        *map(str, product_capability.get("context_policy_refs", [])),
    }
    missing_business = sorted(business_refs - node_id_set)
    if missing_business:
        errors.append(f"Product Capability has missing business references: {missing_business!r}")
    responsibilities = [item.get("responsibility") for item in product_capability.get("owner_routes", []) if isinstance(item, dict)]
    expected_responsibilities = {"product-meaning", "definition-pack-shape", "runtime-contract", "public-realization", "next-use-suitability"}
    if len(responsibilities) != 5 or set(responsibilities) != expected_responsibilities:
        errors.append("Product Capability must preserve exactly five owner responsibilities")
    source_id_set = set(source_ids)
    for ref in product_capability.get("evidence_refs", []):
        if ref not in source_id_set:
            errors.append(f"Product Capability has unknown evidence ref: {ref}")
    for owner in product_capability.get("owner_routes", []):
        for ref in owner.get("source_refs", []) if isinstance(owner, dict) else []:
            if ref not in source_id_set:
                errors.append(f"Product Capability owner route has unknown source ref: {ref}")

    binding = support.get("realization_binding", {})
    if binding.get("binding_id") != UNSELECTED_BINDING_ID:
        errors.append("realization binding identity changed")
    if binding.get("state") != "not_evaluable" or binding.get("system_ontology_ref") is not None or binding.get("implementation_ref") is not None:
        errors.append("realization must remain unselected and not_evaluable")
    if product_capability.get("realization_binding_refs") != [UNSELECTED_BINDING_ID]:
        errors.append("Product Capability realization reference does not close")
    obligation_registry = support.get("obligation_registry", {})
    if obligation_registry.get("registry_id") != OBLIGATION_REGISTRY_ID:
        errors.append("obligation registry identity changed")
    if product_capability.get("obligation_registry_ref") != OBLIGATION_REGISTRY_ID:
        errors.append("Product Capability obligation reference does not close")
    obligations = obligation_registry.get("obligations", [])
    obligation_ids = [str(item.get("obligation_id")) for item in obligations if isinstance(item, dict)]
    unique(obligation_ids, "obligation IDs", errors)
    required_obligations = {
        "WO-OBL-ONE-CAPABILITY-PACKAGE",
        "WO-OBL-SINGLE-ROOT-AUTHORITY",
        "WO-OBL-BOUNDED-CYCLES",
        "WO-OBL-REPLAY",
        "WO-OBL-DOMAIN-SEPARATION",
        "WO-OBL-EFFECT-ADAPTER",
        "WO-OBL-SINGLE-HISTORY-OWNER",
        "WO-OBL-UNKNOWN-FAILS-CLOSED",
    }
    if not required_obligations.issubset(set(obligation_ids)):
        errors.append("required work-orchestration obligations are missing")

    vocabulary = relations_doc.get("relation_vocabulary", [])
    vocabulary_by_type = {str(item.get("type")): item for item in vocabulary if isinstance(item, dict)}
    unique(list(vocabulary_by_type), "relation types", errors)
    relations = relations_doc.get("relations", [])
    relation_ids = [str(item.get("id")) for item in relations if isinstance(item, dict)]
    unique(relation_ids, "relation IDs", errors)
    observed_relations: set[tuple[str, str, str]] = set()
    for relation in relations:
        if not isinstance(relation, dict):
            continue
        label = f"relation {relation.get('id')}"
        source = str(relation.get("source", ""))
        target = str(relation.get("target", ""))
        relation_type = str(relation.get("type", ""))
        if source not in node_id_set or target not in node_id_set:
            errors.append(f"{label} has an unknown endpoint")
        contract = vocabulary_by_type.get(relation_type)
        if contract is None:
            errors.append(f"{label} has unknown relation type {relation_type!r}")
        else:
            if node_roles.get(source) not in contract.get("source_roles", []):
                errors.append(f"{label} has invalid source role")
            if node_roles.get(target) not in contract.get("target_roles", []):
                errors.append(f"{label} has invalid target role")
        check_source_refs(relation.get("source_refs"), source_text, label, errors)
        observed_relations.add((relation_type, source, target))
    required_relations = {
        ("offers", "CA2-PRODUCT-CYBERALCHEMY", BUSINESS_CAPABILITY_ID),
        ("accepts", BUSINESS_CAPABILITY_ID, "CA2-CAP-CONTRACT-WORK-DEFINITION-INPUT"),
        ("produces", BUSINESS_CAPABILITY_ID, "CA2-CAP-CONTRACT-STRUCTURAL-EXECUTION-RECORD"),
        ("contains", "WO-CONCEPT-WORK-DEFINITION", "WO-CONCEPT-WORK-GRAPH"),
        ("derived_from", "WO-CONCEPT-ORCHESTRATION-CURSOR", "WO-CONCEPT-ACCEPTED-HISTORY"),
        ("may_be_realized_by", BUSINESS_CAPABILITY_ID, "WO-REALIZATION-RWO-KERNEL"),
    }
    if not required_relations.issubset(observed_relations):
        errors.append("required business relations are missing")

    residue = residue_doc.get("residue", [])
    residue_ids = [str(item.get("residue_id")) for item in residue if isinstance(item, dict)]
    unique(residue_ids, "residue IDs", errors)
    for item in residue:
        if not isinstance(item, dict):
            continue
        unknown_subjects = sorted(set(item.get("subject_refs", [])) - node_id_set)
        if unknown_subjects:
            errors.append(f"residue {item.get('residue_id')} has unknown subjects: {unknown_subjects!r}")
        unknown_evidence = sorted(set(item.get("evidence_refs", [])) - source_id_set)
        if unknown_evidence:
            errors.append(f"residue {item.get('residue_id')} has unknown evidence: {unknown_evidence!r}")
    lifecycle_residue = set(product_capability.get("lifecycle_posture", {}).get("residue_refs", []))
    if lifecycle_residue != set(residue_ids):
        errors.append("Product Capability lifecycle residue does not exactly cover package residue")
    required_residue = {
        "CAP-RES-WORK-ORCH-ADOPTION",
        "CAP-RES-WORK-ORCH-DOMAINSPEC",
        "CAP-RES-WORK-ORCH-REALIZATION",
        "CAP-RES-WORK-ORCH-HISTORY-OWNER",
        "CAP-RES-WORK-ORCH-DURABLE-RECOVERY",
        "CAP-RES-WORK-ORCH-COUNTEREXAMPLES",
    }
    if set(residue_ids) != required_residue:
        errors.append("required construction and architecture residue is not exact")

    for forbidden_surface in ("domainspec", "system-ontology", "implementation", "runtime"):
        if (PACKAGE_ROOT / forbidden_surface).exists():
            errors.append(f"model-first package must not contain {forbidden_surface}")

    digest = material_digest(errors)
    source_digest_builder = hashlib.sha256()
    for source_id in sorted(selected_bytes):
        source_digest_builder.update(source_id.encode("utf-8") + b"\0" + selected_bytes[source_id] + b"\0")
    return {
        "schema_version": "cav2-work-orchestration-validation/v1",
        "status": "PASS" if not errors else "BLOCK",
        "package_root": "cyberAlchemy-v2/work-orchestration",
        "ontology_id": "cav2.work-orchestration.business",
        "ontology_type": "business-domain",
        "branch": "business",
        "visibility": "private",
        "authority_effect": "none",
        "material_digest": digest,
        "source_digest": source_digest_builder.hexdigest(),
        "counts": {
            "product_capabilities": len(capability_nodes),
            "sources": len(source_ids),
            "canonical_definitions": len(bindings),
            "local_terms": len(term_ids),
            "nodes": len(node_ids),
            "relation_types": len(vocabulary_by_type),
            "relations": len(relation_ids),
            "obligations": len(obligation_ids),
            "residue": len(residue_ids),
        },
        "construction": {
            "definitions": "validated-reference",
            "product_capability": "candidate-validated-shape",
            "business_ontology": "candidate-validated-package",
            "domainspec_source": "absent",
            "compiled_graph": "not_evaluable",
            "system_ontology": "not_evaluable",
            "implementation_binding": "not_evaluable",
            "conformance": "not_evaluable",
        },
        "claim_ceiling": "Current source-bound candidate Product Capability and business ontology package only; no adoption, DomainSpec admission, compiled graph, system ontology, RWO selection, implementation, journal ownership, conformance, publication, release, deployment, or external effect.",
        "errors": errors,
    }


def main() -> int:
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

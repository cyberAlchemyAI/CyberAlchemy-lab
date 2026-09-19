#!/usr/bin/env python3
"""Validate the candidate Commercial Agent Access package without effects."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - reported as a validation failure
    Draft202012Validator = None


PACKAGE_FILES = {
    "profile.json": "profile",
    "sources.json": "sources",
    "definitions.json": "definitions",
    "product-capability-support.json": "productCapabilitySupport",
    "nodes.json": "nodes",
    "relations.json": "relations",
    "residue.json": "residue",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add_unique_errors(errors: list[str], label: str, values: list[str]) -> None:
    if len(values) != len(set(values)):
        errors.append(f"{label} contains duplicate identities")


def validate(package_root: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    schema_path = package_root / "schemas/commercial-agent-access.schema.json"
    if Draft202012Validator is None:
        return ["python package jsonschema is required"]

    try:
        schema = load_json(schema_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"schema load failed: {exc}"]

    docs: dict[str, Any] = {}
    for filename, definition in PACKAGE_FILES.items():
        path = package_root / filename
        try:
            document = load_json(path)
            docs[filename] = document
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{filename}: load failed: {exc}")
            continue
        validation_schema = {
            "$schema": schema["$schema"],
            "$defs": schema["$defs"],
            "$ref": f"#/$defs/{definition}",
        }
        validator = Draft202012Validator(validation_schema)
        for item in sorted(validator.iter_errors(document), key=lambda error: list(error.path)):
            location = "/".join(str(part) for part in item.path) or "<root>"
            errors.append(f"{filename}:{location}: {item.message}")

    capability_path = package_root / "product-capability.json"
    try:
        capability = load_json(capability_path)
        docs["product-capability.json"] = capability
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"product-capability.json: load failed: {exc}")
        capability = {}

    shared_schema_path = repo_root / "cyberAlchemy-v2/capability/schemas/capability.schema.json"
    try:
        shared_schema = load_json(shared_schema_path)
        shared_shape_document = copy.deepcopy(capability)
        if shared_shape_document.get("schema_ref") != "../capability/schemas/capability.schema.json#/$defs/productCapability":
            errors.append("product-capability.json: package-local shared schema locator changed")
        shared_shape_document["schema_ref"] = "../../capability/schemas/capability.schema.json#/$defs/productCapability"
        shared_validation_schema = {
            "$schema": shared_schema["$schema"],
            "$defs": shared_schema["$defs"],
            "$ref": "#/$defs/productCapability",
        }
        shared_validator = Draft202012Validator(shared_validation_schema)
        for item in sorted(shared_validator.iter_errors(shared_shape_document), key=lambda error: list(error.path)):
            location = "/".join(str(part) for part in item.path) or "<root>"
            errors.append(f"product-capability.json:{location}: {item.message}")
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        errors.append(f"shared Product Capability schema validation failed: {exc}")

    if errors:
        return errors

    profile = docs["profile.json"]
    sources = docs["sources.json"]
    definitions = docs["definitions.json"]
    support = docs["product-capability-support.json"]
    nodes = docs["nodes.json"]
    relations = docs["relations.json"]
    residue = docs["residue.json"]

    expected_capability = "CA2-CAP-PROVIDE-GOVERNED-SYSTEM-BUILDING-ACCESS"
    if capability.get("capability_id") != expected_capability:
        errors.append("product-capability.json: stable capability identity changed")
    if capability.get("definition_ref") != "CAV2-D67":
        errors.append("product-capability.json: definition_ref must remain CAV2-D67")
    if capability.get("product_ref") != "CA2-PRODUCT-CYBERALCHEMY":
        errors.append("product-capability.json: capability must belong to CyberAlchemy")
    if capability.get("business_ontology_ref") != "CAA-CAP-PROVIDE-GOVERNED-SYSTEM-BUILDING-ACCESS":
        errors.append("product-capability.json: business ontology binding changed")
    if profile["product_capability_ref"] != capability.get("capability_id"):
        errors.append("profile and Product Capability identities disagree")
    if support["capability_ref"] != capability.get("capability_id"):
        errors.append("support and Product Capability identities disagree")
    if capability.get("authority_effect") != "none":
        errors.append("Product Capability authority_effect must be none")
    if len(capability.get("owner_routes", [])) != 5:
        errors.append("Product Capability must retain exactly five owner routes")

    identity_text = " ".join(
        str(capability.get(field, "")) for field in ("capability_id", "outcome")
    ).lower()
    if "domainspec" in identity_text or "ontology cli" in identity_text or "agent" in identity_text:
        errors.append("delivery technology must not define Product Capability identity or outcome")

    source_ids = [source["source_id"] for source in sources["sources"]]
    add_unique_errors(errors, "sources", source_ids)
    source_id_set = set(source_ids)
    for source in sources["sources"]:
        source_path = repo_root / source["path"]
        try:
            data = source_path.read_bytes()
        except OSError as exc:
            errors.append(f"{source['source_id']}: source unreadable: {exc}")
            continue
        if len(data) != source["expected_size"]:
            errors.append(f"{source['source_id']}: source size drift")
        if sha256(data) != source["expected_sha256"]:
            errors.append(f"{source['source_id']}: source digest drift")
        if source["selector"] not in data.decode("utf-8", errors="replace"):
            errors.append(f"{source['source_id']}: selector not found")

    definition_ids = [item["definition_id"] for item in definitions["definitions"]]
    add_unique_errors(errors, "definitions", definition_ids)
    required_definitions = {
        "CAA-DEF-GOVERNED-SYSTEM-BUILDING-ACCESS",
        "CAA-DEF-DOMAINSPEC-CLI-SURFACE",
        "CAA-DEF-ONTOLOGY-CLI-SURFACE",
        "CAA-DEF-TYPED-INTENT-PROJECT",
        "CAA-DEF-DETERMINISTIC-INSTANTIATION",
        "CAA-DEF-ONTOLOGY-SNAPSHOT",
        "CAA-DEF-EVIDENCE-RECEIPT",
        "CAA-DEF-CLI-ACCESS-ENTITLEMENT",
        "CAA-DEF-CUSTOMER-ARTIFACT-CUSTODY",
        "CAA-DEF-CLI-REALIZATION-BINDING",
        "CAA-DEF-SELF-HOSTED-INSTANTIATION-SERVICE",
        "CAA-DEF-AGENT-INSTANTIATION-REQUEST",
        "CAA-DEF-CREATE-ONLY-TARGET-BOUNDARY",
        "CAA-DEF-KEP-API-ADAPTER",
        "CAA-DEF-KEP-SERVICE-EXCHANGE-ENVELOPE",
        "CAA-DEF-KEP-SERVICE-CAPABILITY-PREREQUISITE",
    }
    if set(definition_ids) != required_definitions:
        errors.append("capability-local definition denominator changed")
    for item in definitions["definitions"]:
        unknown = set(item["source_refs"]) - source_id_set
        if unknown:
            errors.append(f"{item['definition_id']}: unknown source refs {sorted(unknown)}")

    node_ids = [node["node_id"] for node in nodes["nodes"]]
    add_unique_errors(errors, "nodes", node_ids)
    node_id_set = set(node_ids)
    required_nodes = {
        "CAA-CAP-PROVIDE-GOVERNED-SYSTEM-BUILDING-ACCESS",
        "CAA-ACTOR-CUSTOMER-BUILDER",
        "CAA-ACTOR-CUSTOMER-AUTHORIZED-AGENT",
        "CAA-ACTOR-DOMAINSPEC-OWNER",
        "CAA-ACTOR-ONTOLOGY-OWNER",
        "CAA-ENTITLEMENT-CLI-ACCESS",
        "CAA-SERVICE-GOVERNED-SYSTEM-BUILDING",
        "CAA-CONTRACT-TYPED-INTENT-PROJECT",
        "CAA-CONTRACT-AGENT-INSTANTIATION-REQUEST",
        "CAA-CONTRACT-KEP-SERVICE-REQUEST-ENVELOPE",
        "CAA-CONTRACT-KEP-SERVICE-RESPONSE-ENVELOPE",
        "CAA-CONTRACT-KEP-SERVICE-FAILURE-ENVELOPE",
        "CAA-PREREQUISITE-KEP-SERVICE-EXCHANGE-CAPABILITY",
        "CAA-DECISION-WORKSPACE-AUTHORIZATION",
        "CAA-CONTRACT-REGISTERED-ONTOLOGY-SELECTION",
        "CAA-ARTIFACT-GOVERNED-SYSTEM",
        "CAA-BOUNDARY-CREATE-ONLY-TARGET",
        "CAA-READMODEL-ONTOLOGY",
        "CAA-RECEIPT-SYSTEM-BUILDING",
        "CAA-POLICY-CLI-SCOPE",
        "CAA-POLICY-ONTOLOGY-READ-ONLY",
        "CAA-POLICY-VALIDATION-NON-AUTHORITY",
        "CAA-POLICY-CUSTOMER-ARTIFACT-CUSTODY",
        "CAA-POLICY-EFFECT-NON-INHERITANCE",
        "CAA-POLICY-AGENT-REQUEST-NON-AUTHORITY",
        "CAA-OP-DOMAINSPEC-AUTHOR-LINT",
        "CAA-OP-DOMAINSPEC-INSTANTIATE-RECEIPT",
        "CAA-OP-ONTOLOGY-CATALOG-SNAPSHOT",
        "CAA-OP-ONTOLOGY-GET-VALIDATE",
        "CAA-REALIZATION-DOMAINSPEC-CLI",
        "CAA-REALIZATION-SELF-HOSTED-META-TYPE-SERVICE",
        "CAA-REALIZATION-KEP-AGENT-API-ADAPTER",
        "CAA-REALIZATION-ONTOLOGY-CLI-READ-ONLY",
        "CAA-LATER-PRODUCT-SOVEREIGN-AGENT-SERVICE",
    }
    missing_nodes = required_nodes - node_id_set
    if missing_nodes:
        errors.append(f"required business nodes missing: {sorted(missing_nodes)}")
    for node in nodes["nodes"]:
        unknown = set(node["source_refs"]) - source_id_set
        if unknown:
            errors.append(f"{node['node_id']}: unknown source refs {sorted(unknown)}")

    relation_ids = [relation["relation_id"] for relation in relations["relations"]]
    add_unique_errors(errors, "relations", relation_ids)
    for relation in relations["relations"]:
        if relation["from"] not in node_id_set or relation["to"] not in node_id_set:
            errors.append(f"{relation['relation_id']}: relation endpoint missing")
    required_relations = {
        "CAA-REL-DOMAINSPEC-CLI-FIRST-OFFER",
        "CAA-REL-SELF-HOSTED-SERVICE-FIRST-OFFER",
        "CAA-REL-AGENT-SUBMITS-REQUEST",
        "CAA-REL-AGENT-SUBMITS-KEP-ENVELOPE",
        "CAA-REL-KEP-REQUEST-TRANSLATES-TO-INSTANTIATION",
        "CAA-REL-REQUEST-REQUIRES-AUTHORIZATION",
        "CAA-REL-REQUEST-CONSTRAINED-NONAUTHORITY",
        "CAA-REL-INSTANTIATE-USES-TARGET-BOUNDARY",
        "CAA-REL-KEP-ADAPTER-REQUIRES-CAPABILITY",
        "CAA-REL-KEP-ADAPTER-PRODUCES-RESPONSE",
        "CAA-REL-KEP-ADAPTER-PRODUCES-FAILURE",
        "CAA-REL-KEP-RESPONSE-BINDS-RECEIPT",
        "CAA-REL-ONTOLOGY-CLI-FIRST-OFFER",
        "CAA-REL-ONTOLOGY-OPS-CONSTRAINED-READONLY",
        "CAA-REL-RECEIPT-CONSTRAINED-NONAUTHORITY",
        "CAA-REL-SOVEREIGN-AGENT-LATER-THAN-CLI-OFFER",
    }
    if not required_relations.issubset(set(relation_ids)):
        errors.append("first-offer and authority-boundary relations are missing")

    candidates = support["realization_candidates"]
    candidate_kinds = {candidate["candidate_id"]: candidate["kind"] for candidate in candidates}
    expected_candidates = {
        "CAA-REALIZATION-SELF-HOSTED-META-TYPE-SERVICE": "self-hosted-instantiation-service",
        "CAA-REALIZATION-KEP-AGENT-API-ADAPTER": "protocol-api-adapter",
        "CAA-REALIZATION-DOMAINSPEC-CLI": "system-authoring-cli",
        "CAA-REALIZATION-ONTOLOGY-CLI-READ-ONLY": "ontology-inspection-cli",
    }
    if candidate_kinds != expected_candidates:
        errors.append("realization candidate denominator or kinds changed")
    if any(candidate.get("state") != "unselected" for candidate in candidates):
        errors.append("every delivery realization must remain unselected")
    if support["realization_binding"].get("state") != "not_evaluable":
        errors.append("realization binding must remain not_evaluable")
    if support["adoption_state"] != "not-adopted":
        errors.append("Product Capability must remain not-adopted")

    obligation_ids = [
        item["obligation_id"] for item in support["obligation_registry"].get("obligations", [])
    ]
    add_unique_errors(errors, "obligations", obligation_ids)
    required_obligations = {
        "CAA-OBL-ONE-STABLE-CAPABILITY",
        "CAA-OBL-FIRST-OFFER-TWO-CLI-SURFACES",
        "CAA-OBL-SELF-HOSTED-FIRST-OFFER",
        "CAA-OBL-AGENT-REQUEST-NOT-AUTHORITY",
        "CAA-OBL-KEP-SERVICE-CAPABILITY-FIRST",
        "CAA-OBL-KEP-COOWNERSHIP-NON-COLLAPSE",
        "CAA-OBL-KEP-IDENTITY-NOT-WORKSPACE-AUTHORITY",
        "CAA-OBL-KEP-EXCHANGE-CORRELATION",
        "CAA-OBL-CLOSED-META-TYPE-SELECTION",
        "CAA-OBL-CREATE-ONLY-CONTAINED-TARGET",
        "CAA-OBL-DOMAINSPEC-TYPED-INTENT",
        "CAA-OBL-DETERMINISTIC-INSTANTIATION",
        "CAA-OBL-ONTOLOGY-READ-ONLY",
        "CAA-OBL-NATIVE-VERDICT-PRESERVATION",
        "CAA-OBL-VALIDATION-NOT-AUTHORITY",
        "CAA-OBL-ENTITLEMENT-FIRST",
        "CAA-OBL-CUSTOMER-ARTIFACT-CUSTODY",
        "CAA-OBL-CLI-REALIZATION-SEPARATION",
        "CAA-OBL-SUSPENDED-RUNTIME-NON-ENFORCEMENT",
        "CAA-OBL-EFFECT-NON-INHERITANCE",
        "CAA-OBL-AUDITABLE-RECEIPTS",
        "CAA-OBL-UNKNOWN-FAILS-CLOSED",
        "CAA-OBL-SOVEREIGN-AGENT-LATER",
    }
    if not required_obligations.issubset(set(obligation_ids)):
        errors.append("required Product Capability obligations are missing")

    exclusions = " ".join(capability.get("exclusions", [])).lower()
    if "suspended python ontology runtime" not in exclusions or "managed sovereign-agent product" not in exclusions:
        errors.append("Product Capability must preserve ontology-enforcement and first-offer boundaries")
    if "agent invent a meta type" not in exclusions or "self-hosting" not in exclusions:
        errors.append("Product Capability must preserve agent-request and self-hosting claim boundaries")
    if "encrypted co-ownership kep capability" not in exclusions or "kep identity" not in exclusions:
        errors.append("Product Capability must preserve the KEP capability and authorization boundaries")

    residue_ids = [item["residue_id"] for item in residue["residue"]]
    add_unique_errors(errors, "residue", residue_ids)
    if set(capability["lifecycle_posture"]["residue_refs"]) != set(residue_ids):
        errors.append("Product Capability residue refs do not close over residue registry")

    for filename, document in docs.items():
        if isinstance(document, dict) and "authority_effect" in document:
            if document["authority_effect"] != "none":
                errors.append(f"{filename}: authority_effect must be none")

    if profile["construction_stage"] != "business-ontology-candidate":
        errors.append("construction must stop at business-ontology-candidate")
    forbidden_profile_claims = {"publication", "release", "deployment", "sale or external effect"}
    if not forbidden_profile_claims.issubset(set(profile["blocked_outputs"])):
        errors.append("profile does not block every terminal external effect")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    package_default = Path(__file__).resolve().parents[1]
    repo_default = package_default.parents[1]
    parser.add_argument("--package-root", type=Path, default=package_default)
    parser.add_argument("--repo-root", type=Path, default=repo_default)
    args = parser.parse_args()

    errors = validate(args.package_root.resolve(), args.repo_root.resolve())
    result = {
        "schema_version": "cav2-commercial-agent-access-validation/v1",
        "package": "cav2.commercial-agent-access",
        "result": "pass" if not errors else "block",
        "checks": {
            "local_schema": "pass" if not errors else "block",
            "source_bindings": "pass" if not errors else "block",
            "relationship_closure": "pass" if not errors else "block",
            "realization_separation": "pass" if not errors else "block",
            "authority_ceiling": "pass" if not errors else "block"
        },
        "errors": errors,
        "authority_effect": "none",
        "claim_ceiling": "Local candidate-package structural validity only; no adoption, realization selection, implementation, conformance, deployment, sale, or external effect."
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

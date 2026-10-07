#!/usr/bin/env python3
"""Validate the complete Product context candidate and cross-linked example."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import jsonschema


LAB = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
IDENTITY = LAB / "authority/artifact-types/product-identity/v2"
THESIS = LAB / "authority/artifact-types/product-thesis/v1"
CAPABILITY = LAB / "authority/artifact-types/product-capability/v1"
BINDING = LAB / "authority/artifact-types/capability-realization-binding/v1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    model = load(ROOT / "model.json")
    example = load(ROOT / "example.json")
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    component_results = []
    for component in model["components"]:
        artifact = LAB / component["artifact"]["path"]
        schema = LAB / component["schema"]["path"]
        component_results.append({
            "role": component["role"],
            "artifact_current": artifact.is_file() and sha(artifact) == component["artifact"]["sha256"],
            "schema_current": schema.is_file() and sha(schema) == component["schema"]["sha256"],
        })
    check("component-bindings-current", all(item["artifact_current"] and item["schema_current"] for item in component_results), component_results)

    package_examples = [
        ("product", IDENTITY / "schema.json", example["product"]),
        ("product-thesis", THESIS / "schema.json", example["product_thesis"]),
        ("product-capability", CAPABILITY / "schema.json", example["product_capability"]),
        ("capability-realization-binding", BINDING / "schema.json", example["capability_realization_binding"]),
    ]
    schema_results = []
    for role, schema_path, record in package_examples:
        errors = sorted(error.message for error in jsonschema.Draft202012Validator(load(schema_path)).iter_errors(record))
        schema_results.append({"role": role, "ok": not errors, "errors": errors})
    check("all-example-records-schema-valid", all(item["ok"] for item in schema_results), schema_results)

    product = example["product"]
    thesis = example["product_thesis"]
    capability = example["product_capability"]
    realization = example["capability_realization_binding"]
    outcomes = {item["outcome_id"] for item in thesis["intended_outcomes"]}
    cross_ref_ok = (
        product["current_thesis_ref"] == thesis["node_id"]
        and thesis["product_ref"] == product["product_id"]
        and capability["product_ref"] == product["product_id"]
        and capability["product_thesis_ref"] == thesis["node_id"]
        and set(capability["thesis_outcome_refs"]) <= outcomes
        and realization["capability_ref"] == capability["node_id"]
        and realization["node_id"] in capability["realization_binding_refs"]
        and example["derived_product_capability_refs"] == [capability["node_id"]]
    )
    check("cross-record-reference-closure", cross_ref_ok, {"product": product["product_id"], "thesis": thesis["node_id"], "outcomes": sorted(outcomes), "capability": capability["node_id"], "binding": realization["node_id"]})
    check("canonical-ownership-boundaries", "capability_refs" not in product and "implementation_refs" not in product and all(not key.endswith("implementation_refs") for key in capability) and bool(realization["realization_refs"]), {"product_fields": sorted(product), "capability_fields": sorted(capability)})
    check("authority-effect-closed", all(record["authority_effect"] == "none" for _, _, record in package_examples) and model["authority_effect"] == "none" and example["authority_effect"] == "none", "all model and example records declare no authority effect")

    required_relations = {"relation.belongs-to-product", "relation.derives-from", "relation.realizes", "relation.instance-of", "relation.adopts", "relation.evaluates", "relation.supports", "relation.contradicts"}
    contract_ids = {item["target_id"] for item in model["supporting_migration_contracts"]}
    active = [item for item in model["supporting_migration_contracts"] if item["consumer_activation"] != "not-applied"]
    check("governance-contract-coverage", required_relations <= contract_ids and not active, {"required": sorted(required_relations), "available": sorted(contract_ids), "active": active})

    manifest_results = []
    for item in load(ROOT / "manifest.json")["files"]:
        path = LAB / item["path"]
        manifest_results.append({"path": item["path"], "ok": path.is_file() and sha(path) == item["sha256"]})
    check("manifest-current", bool(manifest_results) and all(item["ok"] for item in manifest_results), manifest_results)
    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-complete-product-context-validation/v1",
        "subject": model["model_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "claim_ceiling": "PASS proves exact component bindings, schema-valid example records, cross-record reference closure, canonical ownership boundaries, inactive governance contracts, and manifest integrity. It does not admit or activate any candidate.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"COMPLETE_PRODUCT_CONTEXT={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())

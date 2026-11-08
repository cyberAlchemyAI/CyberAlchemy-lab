#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[5]
SOURCE_REPO = Path("/home/vrondelli/projects/domainspec-core")
SOURCE_PACKAGE = SOURCE_REPO / "cyberAlchemy-v2/ontology/ontology-product"
IMPORTED = ROOT / "imported"
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_definition(instance: Any, schema: dict[str, Any], name: str) -> list[str]:
    validator = Draft202012Validator({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": schema["$defs"],
        "$ref": f"#/$defs/{name}"
    })
    return [error.message for error in validator.iter_errors(instance)]


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    migration = load(ROOT / "migration.json")
    bindings = load(ROOT / "source-bindings.json")
    profile = load(IMPORTED / "profile.json")
    nodes_doc = load(IMPORTED / "nodes.json")
    relations_doc = load(IMPORTED / "relations.json")
    sources_doc = load(IMPORTED / "sources.json")
    residue_doc = load(IMPORTED / "residue.json")
    schema = load(IMPORTED / "schema.json")

    byte_rows = []
    for item in migration["imported_files"]:
        source = SOURCE_PACKAGE / item["path"]
        destination = IMPORTED / item["path"]
        byte_rows.append({
            "path": item["path"],
            "expected": item["sha256"],
            "source": sha(source) if source.is_file() else None,
            "destination": sha(destination) if destination.is_file() else None,
            "byte_equal": source.is_file() and destination.is_file() and source.read_bytes() == destination.read_bytes()
        })
    check("SPM-01-BYTE-PRESERVATION", all(row["byte_equal"] and row["source"] == row["expected"] == row["destination"] for row in byte_rows), byte_rows)

    schema_errors = []
    for instance, definition in ((profile, "profile"), (sources_doc, "source_registry"), (nodes_doc, "node_registry"), (relations_doc, "relation_registry"), (residue_doc, "residue_registry")):
        schema_errors.extend(f"{definition}:{error}" for error in validate_definition(instance, schema, definition))
    check("SPM-02-ORIGINAL-SCHEMA", not schema_errors, schema_errors)

    source_rows = {row["source_id"]: row for row in bindings["bindings"]}
    legacy_rows = {row["id"]: row for row in sources_doc["sources"]}
    binding_errors = []
    for source_id, legacy in legacy_rows.items():
        row = source_rows.get(source_id)
        path = SOURCE_REPO / legacy["path"]
        current = sha(path) if path.is_file() else None
        if not row or row["legacy_sha256"] != legacy["sha256"] or row["current_sha256"] != current or row["path"] != legacy["path"]:
            binding_errors.append(source_id)
    drifted = sorted(row["source_id"] for row in bindings["bindings"] if row["binding_status"] == "drift-reconciled-by-successor-binding")
    expected_drift = sorted(["SRC-CAV2-DEFINITIONS", "SRC-CAV2-ONTOLOGY-PRODUCT-THESIS", "SRC-CAV2-UMBRELLA-PRODUCT-THESIS"])
    check("SPM-03-SUCCESSOR-SOURCE-BINDINGS", not binding_errors and len(source_rows) == 8 and drifted == expected_drift, {"binding_errors": binding_errors, "drifted": drifted})

    nodes = nodes_doc["nodes"]
    relations = relations_doc["relations"]
    vocabulary = relations_doc["relation_vocabulary"]
    residue = residue_doc["residue"]
    node_ids = [item["id"] for item in nodes]
    relation_ids = [item["id"] for item in relations]
    endpoints_ok = all(item["source"] in node_ids and item["target"] in node_ids for item in relations)
    check("SPM-04-GRAPH-CLOSURE", len(node_ids) == len(set(node_ids)) == 23 and len(relation_ids) == len(set(relation_ids)) == 24 and len(vocabulary) == 13 and endpoints_ok and len(residue) == 5, {"nodes": len(nodes), "relations": len(relations), "relation_types": len(vocabulary), "residue": len(residue), "endpoints_ok": endpoints_ok})

    required = {
        ("subproduct_of", "CA2-PRODUCT-ONTOLOGY", "CA2-PRODUCT-CYBERALCHEMY"),
        ("claims_value_through", "CA2-PRODUCT-ONTOLOGY", "CA2-THESIS-ONTOLOGY-PRODUCT"),
        ("develops", "CA2-PROJECT-ONTOLOGY-PRODUCT", "CA2-PRODUCT-ONTOLOGY"),
        ("tests_realization_of", "CA2-PROJECT-ONTOLOGY-PRODUCT", "CA2-THESIS-ONTOLOGY-PRODUCT"),
        ("belongs_to", "CA2-GOAL-ONTOLOGY-PRODUCT-FOUNDATION", "CA2-PROJECT-ONTOLOGY-PRODUCT"),
        ("advances", "CA2-GOAL-ONTOLOGY-PRODUCT-FOUNDATION", "CA2-THESIS-ONTOLOGY-PRODUCT")
    }
    observed = {(item["type"], item["source"], item["target"]) for item in relations}
    check("SPM-05-CORE-RELATIONS", required.issubset(observed), {"missing": sorted(required - observed)})

    selector_errors = []
    current_text = {}
    for source_id, row in source_rows.items():
        current_text[source_id] = (SOURCE_REPO / row["path"]).read_text(encoding="utf-8")
    for collection_name, collection in (("node", nodes), ("relation", relations), ("residue", residue)):
        for item in collection:
            for ref in item["source_refs"]:
                if ref["source_id"] not in current_text or ref["selector"] not in current_text[ref["source_id"]]:
                    selector_errors.append(f"{collection_name}:{item['id']}:{ref['source_id']}:{ref['selector']}")
    check("SPM-06-SELECTOR-CLOSURE", not selector_errors, selector_errors)

    scaffold = load(ROOT.parent / "ontology.json")
    scaffold_ids = {item["node_id"] for item in scaffold["nodes"]}
    imported_product_nodes = [item for item in nodes if item["id"] == "CA2-PRODUCT-ONTOLOGY" and item["role"] == "product"]
    separation = scaffold["ontology_id"] != profile["ontology_id"] and scaffold["represented_product_ref"] == profile["product_node_id"] and len(scaffold_ids) == 3 and len(imported_product_nodes) == 1 and all("!=" in rule for rule in migration["non_collapse_invariants"])
    check("SPM-07-PRODUCT-ONTOLOGY-SEPARATION", separation, {"scaffold": scaffold["ontology_id"], "imported": profile["ontology_id"], "scaffold_nodes": len(scaffold_ids), "imported_nodes": len(nodes)})

    authority_ok = migration["authority_effect"] == bindings["authority_effect"] == profile["authority_effect"] == "none" and all(item["authority_effect"] == "none" for item in nodes + relations)
    check("SPM-08-NO-AUTHORITY-INFLATION", authority_ok, "migration, bindings, profile, nodes, and relations retain authority_effect none")

    generator_path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("source_package_generator", generator_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    expected_view = module.render(migration, bindings)
    view = ROOT / "SOURCE-PACKAGE.md"
    check("SPM-09-PROJECTION-PARITY", view.is_file() and view.read_text(encoding="utf-8") == expected_view, sha(view) if view.is_file() else "missing")

    failures = [row for row in checks if row["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-source-preserving-product-ontology-validation/v1",
        "migration_id": migration["migration_id"],
        "result": "PASS" if not failures else "FAIL",
        "authority_effect": "none",
        "summary": {"passed": len(checks) - len(failures), "failed": len(failures), "total": len(checks), "sources": 8, "nodes": len(nodes), "relations": len(relations), "relation_types": len(vocabulary), "residue": len(residue), "drift_reconciliations": len(drifted)},
        "checks": checks,
        "materials": {"migration_sha256": sha(ROOT / "migration.json"), "source_bindings_sha256": sha(ROOT / "source-bindings.json"), "projection_sha256": sha(view) if view.is_file() else None},
        "claim_ceiling": "PASS proves exact byte preservation, structural graph closure, live selector closure, explicit successor drift bindings, Product-scaffold separation, no authority inflation, and projection parity for this private import. It does not admit or activate either ontology or retire any source."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

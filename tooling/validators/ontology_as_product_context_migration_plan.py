#!/usr/bin/env python3
"""Validate the Ontology-as-a-Product migration successor."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("/home/vrondelli/projects/domainspec-core")
BASE = Path("docs/migration-plans/0003-ontology-as-product-context-migration-v1")
GENERATOR = Path("tooling/generators/ontology_as_product_context_migration_plan.py")
RECEIPT = BASE / "receipts/validation.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load_generator():
    spec = importlib.util.spec_from_file_location("ontology_as_product_generator", ROOT / GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_receipt(receipt: dict[str, Any]) -> str:
    lines = ["<!-- Generated from validation.json. Do not edit. -->", "", "# Ontology-as-a-Product migration validation", "", f"- Result: `{receipt['validation_result']}`", f"- Checks: `{receipt['summary']['checks_passed']}/{receipt['summary']['checks_total']}`", f"- Product Ontology source status: `{receipt['source_status']}`", f"- Plan digest: `{receipt['artifacts']['plan_sha256']}`", f"- Semantic model digest: `{receipt['artifacts']['semantic_model_sha256']}`", "", "## Checks", ""]
    lines.extend(f"- `{row['result']}` — `{row['check_id']}`: {row['detail']}" for row in receipt["validation"])
    lines += ["", "## Remaining blockers", ""]
    lines.extend(f"- {item}" for item in receipt["blockers"])
    lines += ["", "## Claim ceiling", "", receipt["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> int:
    plan_path = ROOT / BASE / "plan.json"
    model_path = ROOT / BASE / "semantic-model.json"
    dispatch_path = ROOT / BASE / "dispatch.json"
    plan = json.loads(plan_path.read_text())
    model = json.loads(model_path.read_text())
    dispatch = json.loads(dispatch_path.read_text())
    generator = load_generator()
    checks: list[dict[str, str]] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    successor = plan["successor_epoch"]
    predecessor_bindings = [
        (successor["supersedes_plan_ref"], successor["supersedes_plan_sha256"]),
        (successor["predecessor_dispatch_ref"], successor["predecessor_dispatch_sha256"]),
        (successor["predecessor_receipt_ref"], successor["predecessor_receipt_sha256"]),
    ]
    check("MIG3-01-PREDECESSOR-IMMUTABLE", all((ROOT / path).is_file() and digest(ROOT / path) == expected for path, expected in predecessor_bindings), "plan 0002, its dispatch, and its PASS receipt still match the bound immutable digests")

    product_binding = model["canonical_bindings"]["product_definition"]
    ontology_binding = model["canonical_bindings"]["ontology_definition"]
    check("MIG3-02-DEFINITION-BINDINGS", digest(ROOT / product_binding["path"]) == product_binding["sha256"] and digest(SOURCE / ontology_binding["path"]) == ontology_binding["source_file_sha256"], "the admitted Product Definition and active CAV2-D19 Ontology source are current")
    registry = json.loads((ROOT / "authority/definitions/registry.json").read_text())
    product_entries = [row for row in registry["entries"] if row.get("definition_id") == "cal.definition.product"]
    check("MIG3-03-PRODUCT-DEFINITION-ADMITTED", len(product_entries) == 1 and product_entries[0].get("lifecycle_state") == "admitted" and product_entries[0].get("sha256") == product_binding["sha256"], "the Product Definition binding resolves through the admitted Lab registry")

    source_epoch = plan["source_epoch"]
    source_files = [(source_epoch["product_thesis_ref"], source_epoch["product_thesis_sha256"]), (source_epoch["identity_decision_ref"], source_epoch["identity_decision_sha256"])]
    source_files += [(f"cyberAlchemy-v2/ontology/ontology-product/{name}", expected) for name, expected in source_epoch["product_ontology_files"].items()]
    check("MIG3-04-SOURCE-EPOCH", all((SOURCE / path).is_file() and digest(SOURCE / path) == expected for path, expected in source_files), "Product Thesis, identity decision, and four selected Product Ontology files match the planning epoch")

    nodes = json.loads((SOURCE / "cyberAlchemy-v2/ontology/ontology-product/nodes.json").read_text())["nodes"]
    relations = json.loads((SOURCE / "cyberAlchemy-v2/ontology/ontology-product/relations.json").read_text())["relations"]
    node_ids = {row["id"]: row for row in nodes}
    relation_ids = {row["id"]: row for row in relations}
    check("MIG3-05-PRODUCT-AND-OUTPUT-NODES", node_ids.get("CA2-PRODUCT-ONTOLOGY", {}).get("role") == "product" and node_ids.get("CA2-OUTPUT-ONTOLOGY-PACKAGE", {}).get("role") == "product_output", "the source graph distinguishes Product identity from governed ontology-package output")
    include = relation_ids.get("CA2-REL-ONTOLOGY-PRODUCT-INCLUDES-TYPED-MEANING", {})
    produces = relation_ids.get("CA2-REL-TYPED-MEANING-PRODUCES-PACKAGE", {})
    check("MIG3-06-CAPABILITY-OUTPUT-PATH", include.get("type") == "includes_capability" and include.get("source") == "CA2-PRODUCT-ONTOLOGY" and include.get("target") == "CA2-CAP-ONTOLOGY-TYPED-MEANING" and produces.get("type") == "produces" and produces.get("source") == "CA2-CAP-ONTOLOGY-TYPED-MEANING" and produces.get("target") == "CA2-OUTPUT-ONTOLOGY-PACKAGE", "the exact Product -> capability -> ontology-package output path resolves")

    subjects = {row["subject_id"]: row for row in model["subjects"]}
    check("MIG3-07-PRODUCT-ONTOLOGY-ROLE", subjects["cav2.ontology-product"]["role"] == "product-ontology-scaffold" and subjects["cav2.ontology-product"]["represented_subject_ref"] == "CA2-PRODUCT-ONTOLOGY", "the Product Ontology is a descriptive scaffold representing the Product")
    labels = {row["label"]: row for row in model["derived_labels"]}
    check("MIG3-08-DERIVED-LABELS", set(labels) == {"Ontology-as-a-Product", "Product Ontology"} and all(row["projection_policy"] == "generated-only" and row["canonical_axis"] is False for row in labels.values()), "both convenience labels are generated projections and create no canonical axes")
    check("MIG3-09-NON-COLLAPSE", len(model["non_collapse_invariants"]) == 7 and len({subjects["CA2-PRODUCT-ONTOLOGY"]["role"], subjects["cav2.ontology-product"]["role"], subjects["CA2-OUTPUT-ONTOLOGY-PACKAGE"]["role"], subjects["CA2-PRODUCT-CRAFT"]["role"]}) == 4, "seven invariants and four distinct subject roles prevent Product, scaffold, output, and Craft collapse")

    source_env = os.environ.copy()
    source_env["PYTHONDONTWRITEBYTECODE"] = "1"
    source_run = subprocess.run(["python3", "cyberAlchemy-v2/ontology/ontology-product/validate.py"], cwd=SOURCE, text=True, capture_output=True, check=False, env=source_env)
    try:
        source_receipt = json.loads(source_run.stdout)
    except json.JSONDecodeError:
        source_receipt = {}
    expected_errors = {f"source digest drift: {item}" for item in source_epoch["source_drift_ids"]}
    check("MIG3-10-SOURCE-BLOCK-PRESERVED", source_receipt.get("status") == "BLOCK" and set(source_receipt.get("errors", [])) == expected_errors and source_receipt.get("material_digest") == source_epoch["material_digest"], "the Product Ontology source remains honestly BLOCKED on the same three selected drifts")

    layers = plan["layers"]
    check("MIG3-11-LAYERING", [row["layer_id"] for row in layers] == ["L0-SEMANTIC-GRAPH-CLOSURE", "L1-PRODUCT-IDENTITY-AND-PRODUCT-ONTOLOGY", "L2-ONTOLOGY-PACKAGE-PRODUCT-CONTRACT", "L3-CONTEXT-AND-RUNTIME-PROTOTYPES", "L4-FIRST-TESTABLE-ONTOLOGY-AS-PRODUCT-CANDIDATE"] and len({row["swu_id"] for row in layers}) == 5, "five unique layers progress from semantic closure to one tested end-to-end Product candidate")
    check("MIG3-12-CONSTRUCTION-FRONTIER", layers[0]["state"] == "implemented-in-this-planning-epoch" and plan["two_lane_work"]["product_construction_frontier"] == "SWU-CML11-202-PRODUCT-ONTOLOGY-MIGRATION", "semantic closure is complete and the next frontier is Product identity/Product Ontology migration")
    check("MIG3-13-DISTILL", plan["distill"]["smallest_coherent_unit"] == "SWU-CML11-201-SEMANTIC-GRAPH-CLOSURE" and plan["distill"]["verdict"] == "pass" and len(plan["distill"]["rounds"]) == 2, "Distill rejects artifact-to-Product collapse and preserves the minimum semantic graph unit")

    audit = plan["definitions_governance"]
    check("MIG3-14-DEFINITIONS-GOVERNANCE", audit["definitions_updated"] == [] and audit["undefined_critical_terms"] == [] and audit["generated_projection_labels"] == ["Ontology-as-a-Product", "Product Ontology"] and audit["drift_found"] is True, "no hidden definitions were authored; dependent labels are projections and predecessor wording drift is routed")
    approval = plan["workflow_preferences"]["approval_boundary"]
    check("MIG3-15-SINGLE-APPROVAL", plan["workflow_preferences"]["approval_mode"] == "single-final-product-boundary" and approval["eligible_after_layer"] == "L4-FIRST-TESTABLE-ONTOLOGY-AS-PRODUCT-CANDIDATE" and len(approval["not_granted"]) == 10, "one final Product approval boundary grants none of ten later authority effects")
    check("MIG3-16-CRAFT-BOUNDARY", plan["craft_intake"]["status"] == "planned-not-written" and len(plan["craft_intake"]["work_items"]) == 4 and plan["product_architecture"]["work_receiver"]["authority_effect"] == "none", "Craft receives four future work items with no authority transfer or ledger mutation")

    dispatch_validator = SOURCE / ".agents/skills/dispatch-spec/scripts/validate-dispatch.py"
    dispatch_run = subprocess.run(["python3", str(dispatch_validator), str(dispatch_path)], cwd=SOURCE, text=True, capture_output=True, check=False)
    check("MIG3-17-DISPATCH", dispatch_run.returncode == 0, "Dispatch Spec accepts the sequential Definitions Governance -> Distill -> Invoke -> validation route" if dispatch_run.returncode == 0 else (dispatch_run.stdout + dispatch_run.stderr)[-600:])

    rendered = generator.projections(plan, model, dispatch)
    exact = all((ROOT / path).is_file() and (ROOT / path).read_text() == content for path, content in rendered.items())
    deterministic = rendered == generator.projections(json.loads(json.dumps(plan)), json.loads(json.dumps(model)), json.loads(json.dumps(dispatch)))
    check("MIG3-18-GENERATED-PROJECTIONS", exact, "all six human views are exact generated projections")
    check("MIG3-19-DETERMINISM", deterministic, "projection generation is byte-deterministic")
    check("MIG3-20-NONAUTHORITY", plan["authority_effect"] == "none" and model["authority_effect"] == "none" and not plan["route"]["execution_candidate"] and dispatch["subagent_strategy"]["status"] == "none", "the successor has no migration, admission, approval, or delegated-execution authority")

    result = "PASS" if all(row["result"] == "PASS" for row in checks) else "FAIL"
    blockers = ["CML11-B01: reconcile three selected Product Ontology source digests before L1 migration.", "CML11-B02: context and Context Map candidates require their separate owners before admitted-context conformance can be claimed."]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-as-product-migration-validation/v1",
        "dispatch_id": dispatch["dispatch_id"],
        "status": result,
        "validation_result": result,
        "authority_effect": "none",
        "artifacts": {"plan_ref": (BASE / "plan.json").as_posix(), "plan_sha256": digest(plan_path), "semantic_model_ref": (BASE / "semantic-model.json").as_posix(), "semantic_model_sha256": digest(model_path), "dispatch_ref": (BASE / "dispatch.json").as_posix(), "dispatch_sha256": digest(dispatch_path), "human_projections": [path.as_posix() for path in rendered]},
        "source_status": source_receipt.get("status", "not_evaluable"),
        "summary": {"checks_passed": sum(row["result"] == "PASS" for row in checks), "checks_total": len(checks), "layers": len(layers), "non_collapse_invariants": len(model["non_collapse_invariants"]), "generated_labels": len(model["derived_labels"])},
        "validation": checks,
        "blockers": blockers,
        "claim_ceiling": "PASS proves the successor planning architecture preserves the canonical Product -> capability -> governed ontology-package output path, separates the descriptive Product Ontology, keeps labels generated-only, preserves predecessor evidence, and provides deterministic projections with one final approval boundary. It does not clear source drift, migrate bytes, mutate Craft, create or admit an artifact type, prove a runtime or Product, approve the Product, or authorize operational effects."
    }
    receipt_path = ROOT / RECEIPT
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    (receipt_path.parent / "VALIDATION.md").write_text(render_receipt(receipt))
    print(json.dumps(receipt, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

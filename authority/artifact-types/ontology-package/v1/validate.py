#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SOURCE_REPO = Path("/home/vrondelli/projects/domainspec-core")
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_section(path: Path, selector: str) -> bytes:
    text = path.read_text(encoding="utf-8")
    start = text.index(selector)
    end = text.find("\n## ", start + len(selector))
    return text[start:end if end >= 0 else None].encode()


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    artifact = load(ROOT / "artifact.json")
    schema = load(ROOT / "schema.json")
    valid = load(ROOT / "fixtures/valid/ontology-package.json")
    validator = jsonschema.Draft202012Validator(schema)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        valid_errors = [error.message for error in validator.iter_errors(valid)]
    except Exception as exc:
        valid_errors = [str(exc)]
    check("OPA-01-CLOSED-INSTANCE-SCHEMA", not valid_errors, valid_errors)

    invalid_results = {}
    for name in ("authority-effect.json", "missing-source-binding.json", "unknown-field.json"):
        errors = [error.message for error in validator.iter_errors(load(ROOT / "fixtures/invalid" / name))]
        invalid_results[name] = errors
    check("OPA-02-HOSTILE-FIXTURES", all(invalid_results.values()), invalid_results)

    root_binding = artifact["artifact_type_root_binding"]
    root_path = LAB / root_binding["path"]
    check("OPA-03-ARTIFACT-TYPE-V2-BINDING", root_path.is_file() and sha(root_path) == root_binding["sha256"] and root_binding["admission_decision_ref"] == "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1", root_binding)

    binding_rows = []
    roots = {"lab": LAB, "domainspec-core": SOURCE_REPO}
    for binding in artifact["semantic_definition_bindings"]:
        path = roots[binding["root"]] / binding["path"]
        if binding["selector"] == "whole-file":
            actual = sha(path) if path.is_file() else None
        else:
            actual = hashlib.sha256(selected_section(path, binding["selector"])).hexdigest() if path.is_file() else None
        binding_rows.append({"definition_ref": binding["definition_ref"], "expected": binding["content_sha256"], "actual": actual, "current": actual == binding["content_sha256"]})
    refs = set(artifact["semantic_definition_refs"])
    bound_refs = {row["definition_ref"] for row in binding_rows}
    check("OPA-04-SEMANTIC-DEFINITION-BINDINGS", refs == bound_refs and all(row["current"] for row in binding_rows), binding_rows)

    check("OPA-05-SCHEMA-AND-GENERATOR-BINDINGS", artifact["schema_digest"] == sha(ROOT / "schema.json") and artifact["source_direction"]["generator_sha256"] == sha(ROOT / "generator.py"), {"schema": sha(ROOT / "schema.json"), "generator": sha(ROOT / "generator.py")})

    product_witness = LAB / "product/products/ontology/v1/fixtures/valid/ontology-package.json"
    check("OPA-06-PRODUCT-WITNESS-PARITY", product_witness.is_file() and product_witness.read_bytes() == (ROOT / "fixtures/valid/ontology-package.json").read_bytes(), sha(product_witness) if product_witness.is_file() else "missing")

    identity_ok = valid["package_id"] not in {valid["product_ref"], valid["product_output_ref"]} and valid["product_ref"] == "CA2-PRODUCT-ONTOLOGY/v1" and valid["product_output_ref"] == "CA2-OUTPUT-ONTOLOGY-PACKAGE" and valid["source_binding"]["sha256"] and valid["query_contract"]["allowed_operations"] == ["list", "get"]
    check("OPA-07-IDENTITY-AND-BOUNDARY", identity_ok, {"package_id": valid["package_id"], "product_ref": valid["product_ref"], "product_output_ref": valid["product_output_ref"], "source_id": valid["source_binding"]["source_id"]})

    generator_path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("ontology_package_generator", generator_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    artifact_view = ROOT / "ARTIFACT.md"
    instance_view = ROOT / "fixtures/valid/ONTOLOGY-PACKAGE.md"
    artifact_expected = module.render_artifact(artifact)
    instance_expected = module.render_instance(valid)
    check("OPA-08-GENERATED-PROJECTIONS", artifact_view.is_file() and instance_view.is_file() and artifact_view.read_text(encoding="utf-8") == artifact_expected and instance_view.read_text(encoding="utf-8") == instance_expected, {"artifact": sha(artifact_view) if artifact_view.is_file() else None, "instance": sha(instance_view) if instance_view.is_file() else None})

    facets_ok = set(artifact["four_facets"]) == {"classification", "schema", "human_continuation", "machine_checkable"} and all(artifact["four_facets"].values())
    check("OPA-09-FOUR-FACET-CLOSURE", facets_ok, artifact["four_facets"])

    residue_ids = {item["residue_id"] for item in artifact["typed_residue"]}
    no_effect = artifact["status"] == "candidate-unadmitted" and artifact["authority_effect"] == valid["authority_effect"] == "none" and "CML11-OP-01-R1" in residue_ids and "CML11-OP-01-R2" in residue_ids
    check("OPA-10-CANDIDATE-NO-EFFECT", no_effect, {"status": artifact["status"], "authority_effect": artifact["authority_effect"], "residue": sorted(residue_ids)})

    failures = [row for row in checks if row["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-package-artifact-type-validation/v1",
        "subject": artifact["artifact_type_ref"],
        "result": "PASS" if not failures else "FAIL",
        "authority_effect": "none",
        "summary": {"passed": len(checks) - len(failures), "failed": len(failures), "total": len(checks), "hostile_fixtures": 3},
        "checks": checks,
        "materials": {"artifact_sha256": sha(ROOT / "artifact.json"), "schema_sha256": sha(ROOT / "schema.json"), "artifact_projection_sha256": sha(artifact_view) if artifact_view.is_file() else None, "instance_sha256": sha(ROOT / "fixtures/valid/ontology-package.json"), "instance_projection_sha256": sha(instance_view) if instance_view.is_file() else None},
        "residue": ["A Lab-local Ontology Definition and an Artifact Type owner admission decision remain absent."],
        "claim_ceiling": "PASS proves Ontology Package/v1 candidate schema-and-artifact-type conformance, current semantic bindings, hostile rejection, Product witness parity, four-facet closure, and deterministic projections. It does not admit the Artifact Type or any instance, approve the Product, or authorize runtime adoption or external effects."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

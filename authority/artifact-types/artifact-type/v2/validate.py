#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    artifact = load(ROOT / "artifact.json")
    schema = load(ROOT / "schema.json")
    checks = []

    def check(check_id: str, ok: bool, detail) -> None:
        checks.append({"check_id":check_id,"result":"PASS" if ok else "FAIL","detail":detail})

    errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(artifact)]
    check("closed-schema", not errors, errors)
    check("schema-digest-current", artifact["schema_digest"] == sha(ROOT / "schema.json"), {"declared":artifact["schema_digest"],"actual":sha(ROOT / "schema.json")})
    predecessor = artifact["predecessor"]
    check("predecessor-v1-current", sha(LAB / predecessor["artifact_path"]) == predecessor["artifact_sha256"] and sha(LAB / predecessor["schema_path"]) == predecessor["schema_sha256"], predecessor)
    binding_results = []
    for item in artifact["semantic_definition_bindings"]:
        path = LAB / item["path"]
        binding_results.append({"definition_ref":item["definition_ref"],"exists":path.is_file(),"expected":item["sha256"],"actual":sha(path) if path.is_file() else None})
    check("semantic-definition-bindings-current", all(x["exists"] and x["expected"] == x["actual"] for x in binding_results), binding_results)
    refs = set(artifact["semantic_definition_refs"])
    bound_refs = {item["definition_ref"] for item in artifact["semantic_definition_bindings"]}
    check("top-level-definition-closure", refs == bound_refs, {"refs":sorted(refs),"bindings":sorted(bound_refs)})
    check("new-registration-definition-refs", all(item["semantic_definition_refs"] for item in artifact["registered_types"]), [item["artifact_type_ref"] for item in artifact["registered_types"]])
    generator_path = ROOT / "generator.py"
    check("generator-digest-current", artifact["source_direction"]["generator_sha256"] == sha(generator_path), {"declared":artifact["source_direction"]["generator_sha256"],"actual":sha(generator_path)})
    spec = importlib.util.spec_from_file_location("artifact_type_v2_generator", generator_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    expected_md = module.render(artifact)
    md_path = ROOT / "ARTIFACT.md"
    check("projection-parity", md_path.is_file() and md_path.read_text(encoding="utf-8") == expected_md and module.render(artifact) == expected_md, sha(md_path) if md_path.is_file() else "missing")
    fixture = load(ROOT / "fixtures/invalid/new-registration-without-definition-ref.json")
    invalid = dict(artifact)
    invalid["registered_types"] = [fixture["registered_type"]]
    fixture_errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(invalid)]
    check("missing-definition-ref-fixture-rejected", any("semantic_definition_refs" in message for message in fixture_errors), fixture_errors)
    check("candidate-no-effect", artifact["status"] == "candidate-unadmitted" and artifact["authority_effect"] == "none", artifact["status"])
    failed = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version":"cyberalchemy-lab-artifact-type-v2-validation/v1",
        "subject":"cal.artifact-type.artifact-type/v2",
        "result":"PASS" if not failed else "FAIL",
        "authority_effect":"none",
        "checks":checks,
        "summary":{"passed":len(checks)-len(failed),"failed":len(failed),"total":len(checks)},
        "materials":{"artifact_sha256":sha(ROOT / "artifact.json"),"schema_sha256":sha(ROOT / "schema.json"),"projection_sha256":sha(md_path) if md_path.is_file() else None},
        "claim_ceiling":"PASS proves Artifact Type/v2 is schema-valid, binds its candidate semantic Definition, preserves v1 by exact reference, requires semantic Definition references for registrations authored under v2, rejects the missing-reference fixture, and reproduces its human projection. It does not admit v2 or any registration."
    }
    receipt_path = ROOT / "receipts/validation.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ARTIFACT_TYPE_V2_VALIDATION={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

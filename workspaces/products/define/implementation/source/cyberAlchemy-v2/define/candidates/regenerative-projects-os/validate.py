#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DEFAULT_RPOS = REPO.parent / "fit-farms"
RPOS = Path(os.environ.get("RPOS_PROJECT_ROOT", DEFAULT_RPOS)).resolve()


def load(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    errors = []
    profile = load(HERE / "profile.json")
    source_package = load(HERE / "source-package.json")
    adapter = load(HERE / "RPOS-DEFINITION-PACK.v1-candidate.json")
    definitions_root = RPOS / "definitions"

    for material in source_package.get("materials", []):
        path = definitions_root / material["path"]
        if not path.is_file():
            errors.append(f"source-package.missing:{material['path']}")
        elif material.get("sha256") and sha256(path) != material["sha256"]:
            errors.append(f"source-package.digest-drift:{material['path']}")

    source_definitions = load(definitions_root / "definitions.json")
    source_handled = load(definitions_root / "handled-definitions.json")
    source_dependencies = load(definitions_root / "semantic-dependencies.json")
    source_pack = load(definitions_root / "definition-packs" / "RPOS-KERNEL-DEFINITION-PACK.v1-candidate.json")
    source_ids = {item["definition_id"] for item in source_definitions["definitions"]}
    vendor_refs = {item["definition_ref"] for item in load(definitions_root / "vendor" / "cyberalchemy-lab" / "vendor-manifest.json")["definitions"]}
    source_dispositions = {item["concept_id"]: item["disposition"] for item in source_handled["records"]}
    adapter_dispositions = {item["concept_id"]: item["disposition"] for item in adapter["concepts"]}

    if source_ids != set(adapter_dispositions):
        errors.append("adapter.definition-coverage-mismatch")
    if source_dispositions != adapter_dispositions:
        errors.append("adapter.disposition-drift")
    for edge in source_dependencies.get("edges", []):
        if edge.get("from_ref") not in source_ids:
            errors.append(f"adapter.dependency-source-missing:{edge.get('from_ref')}")
        if edge.get("to_ref") not in source_ids and edge.get("to_ref") not in vendor_refs:
            errors.append(f"adapter.dependency-target-missing:{edge.get('to_ref')}")
    for definition in source_definitions["definitions"]:
        formalization = definition.get("formalization", {})
        if formalization.get("level") not in {"formal-expression", "structured-invariants", "open"}:
            errors.append(f"adapter.formalization-missing:{definition['definition_id']}")
        if formalization.get("level") == "formal-expression" and not formalization.get("expression"):
            errors.append(f"adapter.formal-expression-missing:{definition['definition_id']}")
        if not formalization.get("semantic_tests"):
            errors.append(f"adapter.semantic-tests-missing:{definition['definition_id']}")
    if adapter.get("source_pack_id") != source_pack.get("pack_id"):
        errors.append("adapter.pack-id-mismatch")
    expected_open = {item["definition_id"] for item in source_definitions["definitions"] if item["status"] == "open"}
    if expected_open != set(adapter.get("open_questions", [])):
        errors.append("adapter.open-question-drift")
    if profile.get("authority_effect") != "none" or adapter.get("authority_effect") != "none":
        errors.append("adapter.authority-effect-invalid")

    result = {
        "schema_version": "cav2.define-rpos-adapter-validation/v1",
        "status": "PASS" if not errors else "BLOCK",
        "package_id": profile.get("package_id"),
        "source_package_id": source_package.get("source_package_id"),
        "concept_count": len(adapter_dispositions),
        "open_concept_count": len(expected_open),
        "dependency_edge_count": len(source_dependencies.get("edges", [])),
        "formal_expression_count": sum(1 for item in source_definitions["definitions"] if item.get("formalization", {}).get("level") == "formal-expression"),
        "structured_invariant_count": sum(1 for item in source_definitions["definitions"] if item.get("formalization", {}).get("level") == "structured-invariants"),
        "vendor_snapshot_bound": any(item.get("path") == "vendor/cyberalchemy-lab/vendor-manifest.json" for item in source_package.get("materials", [])),
        "errors": sorted(errors),
        "claim_ceiling": "Exact local adapter and source-binding validation only; no semantic promotion, ARE qualification, publication, deployment, or external action.",
        "authority_effect": "none"
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Collect-all product validation for Artifact Surface successor 0002."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
PREDECESSOR = LAB / "authority/artifact-types/candidates/0001-artifact-surface-foundation"
DEFINITIONS = LAB / "authority/definitions/candidates/0010-artifact-surface-foundation-revision"
TYPE_ROOTS = [LAB / f"authority/artifact-types/{name}/v1/candidates/0002-executable-surface" for name in ["artifact-type-registry", "artifact-type-request", "canonical-package-manifest"]]
VALIDATOR_PATH = LAB / "tooling/validators/artifact_surface_candidate_2.py"
SUITE = LAB / "tests/conformance/artifact-surface-foundation/revision-0002/suite.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


checks: list[dict[str, Any]] = []


def check(check_id: str, ok: bool, detail: Any) -> None:
    checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})


def run(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=LAB, text=True, capture_output=True)
    return {"returncode": completed.returncode, "stdout": completed.stdout.strip(), "stderr": completed.stderr.strip()}


def main() -> int:
    candidate = load(ROOT / "candidate.json")
    check("candidate-no-authority-effect", candidate["status"] == "test-candidate-unapproved" and candidate["authority_effect"] == "none", {"status": candidate["status"], "authority_effect": candidate["authority_effect"]})

    predecessor_hashes = {
        "manifest": sha(PREDECESSOR / "manifest.json"),
        "receipt": sha(PREDECESSOR / "receipts/validation.json"),
    }
    check("predecessor-envelope-immutable", predecessor_hashes == {"manifest": candidate["predecessor"]["manifest_sha256"], "receipt": candidate["predecessor"]["receipt_sha256"]}, predecessor_hashes)
    predecessor_manifest = load(PREDECESSOR / "manifest.json")
    predecessor_stale = [item["path"] for item in predecessor_manifest["materials"] if not (LAB / item["path"]).is_file() or sha(LAB / item["path"]) != item["sha256"]]
    check("predecessor-byte-closure-current", not predecessor_stale, {"materials": len(predecessor_manifest["materials"]), "stale": predecessor_stale})

    definition_result = run([sys.executable, str(DEFINITIONS / "validate.py")])
    check("definition-successors-validate", definition_result["returncode"] == 0, definition_result)
    type_results = []
    for root in TYPE_ROOTS:
        result = run([sys.executable, str(root / "validate.py")])
        type_results.append({"path": str(root.relative_to(LAB)), **result})
    check("artifact-type-candidate-epochs-validate", all(item["returncode"] == 0 for item in type_results), type_results)

    build_result = run([sys.executable, str(ROOT / "build.py")])
    check("successor-build", build_result["returncode"] == 0, build_result)
    registry = load(ROOT / "registry.json")
    registry_schema = load(TYPE_ROOTS[0] / "schema.json")
    registry_errors = sorted(error.message for error in jsonschema.Draft202012Validator(registry_schema).iter_errors(registry))
    check("registry-schema-valid", not registry_errors, registry_errors)
    refs = [entry["artifact_type_ref"] for entry in registry["entries"]]
    check("exact-25-admitted-type-versions", len(refs) == 25 and len(set(refs)) == 25, {"count": len(refs), "unique": len(set(refs))})
    binding_results = []
    for entry in registry["entries"]:
        artifact = LAB / entry["artifact_path"]
        schema = LAB / entry["schema_path"]
        binding_results.append({"ref": entry["artifact_type_ref"], "artifact_current": artifact.is_file() and sha(artifact) == entry["artifact_sha256"], "schema_current": schema.is_file() and sha(schema) == entry["schema_sha256"]})
    check("registry-exact-byte-bindings", all(item["artifact_current"] and item["schema_current"] for item in binding_results), binding_results)

    validator = import_path("artifact_surface_validator_c2", VALIDATOR_PATH)
    suite = load(SUITE)
    resolution_results = []
    for case in suite["cases"]:
        test_registry = copy.deepcopy(registry)
        artifact = load(LAB / case["artifact"])
        label = case.get("move_label_to", case["artifact"])
        if "inject_duplicate_discriminator_as" in case:
            discriminator = artifact.get("schema_version")
            original = next(entry for entry in test_registry["entries"] if entry["lifecycle_state"] == "admitted-current" and entry["instance_discriminator"]["value"] == discriminator)
            shadow = copy.deepcopy(original)
            shadow["artifact_type_ref"] = case["inject_duplicate_discriminator_as"]
            test_registry["entries"].append(shadow)
        observed = validator.resolve(test_registry, artifact, label)
        ok = observed["outcome"] == case["expected"] and ("expected_matches" not in case or observed["matches"] == case["expected_matches"])
        resolution_results.append({"case_id": case["case_id"], "ok": ok, "outcome": observed["outcome"], "matches": observed["matches"], "artifact_path": observed["artifact_path"]})
    check("executable-resolution-suite", all(item["ok"] for item in resolution_results), resolution_results)

    plan = load(ROOT / "audit-plan.json")
    expected_audit = validator.audit(registry, plan)
    actual_audit = load(ROOT / "audit.json")
    check("computed-audit-current", actual_audit == expected_audit and actual_audit["result"] == "PASS", {"equal": actual_audit == expected_audit, "summary": actual_audit["summary"]})
    check("audit-covers-selected-tree", actual_audit["summary"]["total"] == 25, actual_audit["summary"])

    manifest_root = TYPE_ROOTS[2]
    manifest_fixture = load(manifest_root / "fixtures/valid/package.json")
    manifest_semantics = validator.manifest_semantic_failures(manifest_fixture)
    self_entries = [entry for entry in manifest_fixture["surface_entries"] if entry["path"] == "package.json"]
    check("manifest-self-classification", not manifest_semantics and len(self_entries) == 1, {"self_entries": self_entries, "semantic_failures": manifest_semantics})

    manifest = load(ROOT / "manifest.json")
    stale = [item["path"] for item in manifest["materials"] if not (LAB / item["path"]).is_file() or sha(LAB / item["path"]) != item["sha256"]]
    check("successor-byte-manifest-closed", len(manifest["materials"]) >= 55 and not stale, {"materials": len(manifest["materials"]), "stale": stale})

    definition_receipt_path = DEFINITIONS / "receipts/validation.json"
    type_receipt_paths = [root / "receipts/validation.json" for root in TYPE_ROOTS]
    receipt_set_complete = definition_receipt_path.is_file() and all(path.is_file() for path in type_receipt_paths)
    definition_receipt = load(definition_receipt_path) if definition_receipt_path.is_file() else {}
    type_receipts = [load(path) for path in type_receipt_paths if path.is_file()]
    lifecycle_ok = receipt_set_complete and definition_receipt.get("authority_effect") == "none" and len(type_receipts) == len(TYPE_ROOTS) and all(receipt.get("authority_effect") == "none" and receipt.get("assessment", {}).get("admission_posture") == "candidate-unadmitted" for receipt in type_receipts)
    check("candidate-only-lifecycle-ceiling", lifecycle_ok, {"receipt_set_complete": receipt_set_complete, "definitions": definition_receipt.get("result", "not_evaluable"), "types": [receipt.get("result", "not_evaluable") for receipt in type_receipts]})

    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-surface-foundation-validation/v2",
        "subject": candidate["candidate_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "none",
        "assessment": {
            "product_candidate": "TESTED" if not blocked else "NOT_ESTABLISHED",
            "product_approval": "not_granted",
            "definition_admission": "not_granted",
            "artifact_type_admission": "not_granted",
            "registry_activation": "not_authorized",
            "migration": "not_authorized",
            "commit": "not_authorized",
            "publication": "not_authorized"
        },
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "materials": {
            "candidate_sha256": sha(ROOT / "candidate.json"),
            "definition_receipt_sha256": sha(definition_receipt_path) if definition_receipt_path.is_file() else None,
            "registry_sha256": sha(ROOT / "registry.json"),
            "audit_sha256": sha(ROOT / "audit.json"),
            "manifest_sha256": sha(ROOT / "manifest.json"),
            "suite_sha256": sha(SUITE),
            "resolver_sha256": sha(VALIDATOR_PATH)
        },
        "predecessor": predecessor_hashes,
        "claim_ceiling": "PASS establishes current exact test evidence for unapproved successor candidate 0002 only. It does not approve the product, admit Definitions or Artifact Types, activate the registry, establish repository-wide conformance, migrate files, commit, push, publish, release, or deploy."
    }
    output = ROOT / "receipts/validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ARTIFACT_SURFACE_FOUNDATION_SUCCESSOR={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    if blocked:
        print("BLOCKED=" + ",".join(item["check_id"] for item in blocked))
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())

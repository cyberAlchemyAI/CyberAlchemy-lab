#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SCHEMA = LAB / "authority/artifact-types/definition/v1/schema.json"
GENERATOR = LAB / "authority/artifact-types/definition/v1/generator.py"
LIVE = LAB / "authority/definitions/registry.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    live_before = sha(LIVE)
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    definition_path = ROOT / "definitions/admission-transaction/v1/definition.json"
    definition = load(definition_path)
    checks = []

    def check(check_id: str, passed: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    errors = [error.message for error in jsonschema.Draft202012Validator(load(SCHEMA)).iter_errors(definition)]
    check("definition-schema", not errors, errors)
    spec = importlib.util.spec_from_file_location("definition_generator", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    check("projection-parity", (definition_path.parent / "DEFINITION.md").read_text(encoding="utf-8") == module.render(definition), sha(definition_path.parent / "DEFINITION.md"))
    registry = load(ROOT / "registry-postimage.json")
    candidate_entries = [entry for entry in registry["entries"] if entry["definition_id"] == definition["definition_id"]]
    check("registry-postimage", len(candidate_entries) == 1 and candidate_entries[0]["sha256"] == sha(definition_path) and registry["proposed_current_lookup"][definition["definition_id"]] == f"{definition['definition_id']}@{definition['version']}", candidate_entries)
    drift = load(ROOT / "drift-audit-postimage.json")
    check("downstream-drift", len(drift["checks"]) == 5 and all(item["result"] == "PASS" for item in drift["checks"]), drift["checks"])
    check("live-registry-preserved", live_before == sha(LIVE), {"sha256": live_before})
    canonical = [definition_path, definition_path.parent / "DEFINITION.md", ROOT / "registry-postimage.json", ROOT / "DEFINITIONS-INDEX.md", ROOT / "drift-audit-postimage.json"]
    before = {str(path): sha(path) for path in canonical}
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    after = {str(path): sha(path) for path in canonical}
    check("deterministic", before == after, before)
    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    receipt = {
        "schema_version": "cyberalchemy-lab-admission-transaction-definition-validation/v1",
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {"definition_sha256": sha(definition_path), "registry_postimage_sha256": sha(ROOT / "registry-postimage.json"), "index_sha256": sha(ROOT / "DEFINITIONS-INDEX.md"), "drift_sha256": sha(ROOT / "drift-audit-postimage.json")},
        "claim_ceiling": "PASS validates the candidate Definition and synchronized postimages. It admits nothing and leaves the live registry unchanged.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(json.dumps({"result": result, "checks": len(checks), **receipt["materials"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

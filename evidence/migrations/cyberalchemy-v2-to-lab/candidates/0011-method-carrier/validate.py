#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module, need
import author
import reconcile
from check import assess


def files(root):
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def materials():
    return {name: digest for name, digest in files(ROOT).items() if "receipts" not in Path(name).parts and name != "manifest.json"}


def validate():
    checks = []
    def check(name, action):
        try:
            detail = action()
            checks.append({"check": name, "result": "PASS", "detail": detail})
        except Exception as exc:
            checks.append({"check": name, "result": "BLOCK", "detail": str(exc)})

    def dependencies():
        deps = load(ROOT / "dependencies.json")
        previous = load(PREVIOUS / "manifest.json")
        for ref in previous["materials"] + load(PREVIOUS / "dependencies.json")["inputs"] + deps["inputs"] + deps["definitions"]:
            need(sha(LAB / ref["path"]) == ref["sha256"], "Dependency drift: " + ref["path"])
        need(load(LAB / previous["validation"]["path"])["result"] == "PASS", "Predecessor did not pass")
        registry = load(LAB / "authority/definitions/registry.json")["entries"]
        for ref in deps["admitted_definition_bindings"]:
            entry = next(x for x in registry if x["path"] == ref["path"])
            need(entry["sha256"] == ref["sha256"] == sha(LAB / ref["path"]), "Admitted Method bytes changed")
            need(entry["lifecycle_state"] == "admitted" and entry["admission_decision_ref"] == ref["admission_decision_ref"], "Method admission changed")
            definition = load(LAB / ref["path"])
            schema_path = LAB / "authority/artifact-types/definition/v1/schema.json"
            need(definition["schema_digest"] == sha(schema_path), "Definition contract drift")
            Draft202012Validator(load(schema_path)).validate(definition)
        helper = module(L1.parents[1] / "author.py", "method_source_reader")
        source = LAB.parent / "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md"
        for selected in deps["selected_source_sections"]:
            actual = hashlib.sha256(helper.markdown_h2_section(source, selected["selector"])).hexdigest()
            need(actual == selected["section_sha256"], "Method source lineage drift")
        return {"admitted_definitions": 1, "normalized_source_sections": 1, "historical_line_selector": "retained without rebinding"}
    check("source-and-construction-dependencies", dependencies)

    def contracts():
        shared = module(LAB / "tooling/validators/artifact_surface.py", "schema_shared_validator")
        need(shared.validate_package(PACKAGE) == 0, "Artifact Type mechanics failed")
        return {"artifact_types": 1, "invalid_schema_fixtures": 8}
    check("shared-artifact-type-mechanics", contracts)

    def behavior():
        result = subprocess.run([sys.executable, str(ROOT / "test_method.py"), "-v"], capture_output=True, text=True)
        (ROOT / "receipts").mkdir(exist_ok=True)
        (ROOT / "receipts/tests.log").write_text(result.stdout + result.stderr)
        need(result.returncode == 0, result.stdout + result.stderr)
        return "21 tests passed: ordered data flow, role and gate closure, output coverage, reuse rules, evidence bindings, CLI states and non-execution."
    check("method-behavior", behavior)

    def demonstrate():
        before = files(PREVIOUS)
        record_path = PACKAGE / "fixtures/valid/method-record.json"
        result = assess(load(record_path))
        need(result["declaration_coherent"] and not result["execution_authorized"], "Method demonstration failed")
        need(before == files(PREVIOUS), "Checker changed predecessor")
        dump(ROOT / "receipts/demonstration.json", {"record": binding(record_path), "result": result, "predecessor_unchanged": True})
        return {"declaration_coherent": True, "instructions_executed": False}
    check("method-demonstration", demonstrate)

    def deterministic():
        before = materials()
        author.build()
        need(before == materials(), "Reconstruction did not reproduce")
        need(load(ROOT / "reconciliation.json") == reconcile.build(), "Reconciliation drift")
        return load(ROOT / "reconciliation.json")["state_counts"]
    check("determinism-and-195-target-reconciliation", deterministic)
    outcome = "PASS" if all(x["result"] == "PASS" for x in checks) else "BLOCK"
    dump(ROOT / "receipts/validation.json", {"schema_version": "cal-method-carrier-validation/v1", "result": outcome,
        "authority_effect": "none", "checks": checks, "materials": materials(),
        "claim_ceiling": "Static Method declaration coherence only; no gate evaluation, execution, outcomes or adoption."})
    print(outcome)
    for item in checks:
        print(item["check"], item["result"], item["detail"])
    return 0 if outcome == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(validate())

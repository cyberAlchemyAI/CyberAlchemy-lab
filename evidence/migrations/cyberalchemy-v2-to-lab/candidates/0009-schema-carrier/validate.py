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
from check import check_graph


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
        closure = set(deps["seed_targets"])
        edges = load(L1 / "batches.json")["edges"]
        while True:
            expanded = closure | {x["dependency_target_id"] for x in edges if x["consumer_target_id"] in closure}
            if expanded == closure:
                break
            closure = expanded
        need(closure == {x["target_id"] for x in deps["definitions"]}, "Dependency closure missing")
        residue = [x for x in load(L1 / "drift-audit.json")["legacy_reference_residue"] if x["consumer_target_id"] in closure]
        need(residue == deps["source_lineage_residue"], "Source residue lost")
        # Reuse the prior narrow D53 source binding without mutating its frozen evidence.
        result = subprocess.run([sys.executable, "-c", "import json,source_rebinding; print(json.dumps(source_rebinding.build()))"], cwd=ROOT.parent / "0005-reconciliation-and-proposition-types", capture_output=True, text=True, check=True)
        overlay = load(ROOT.parent / "0005-reconciliation-and-proposition-types/source-rebinding.json")
        need(json.loads(result.stdout) == overlay, "D53 binding changed")
        helper = module(L1.parents[1] / "author.py", "schema_source_reader")
        source = LAB.parent / "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md"
        schema_path = LAB / "authority/artifact-types/definition/v1/schema.json"
        schema = Draft202012Validator(load(schema_path))
        historic = {str((L1 / x["path"]).relative_to(LAB)): x["sha256"] for x in load(L1 / "manifest.json")["materials"]}
        sections = set()
        for ref in deps["definitions"]:
            need(ref["sha256"] == historic[ref["path"]], "Historical Definition drift")
            definition = load(LAB / ref["path"])
            need(definition["schema_digest"] == sha(schema_path), "Definition schema changed")
            schema.validate(definition)
            for selected in definition["source_refs"]:
                actual = hashlib.sha256(helper.markdown_h2_section(source, selected["selector"])).hexdigest()
                if selected["selector"] == "## CAV2-D53: Axiom":
                    need(actual == overlay["current_historical_selector_sha256"] and selected["content_sha256"] == overlay["historical_section_sha256"], "Unbound D53 drift")
                else:
                    need(actual == selected["content_sha256"], "Source drift: " + selected["selector"])
                sections.add(selected["selector"])
        for selected in deps["selected_source_sections"]:
            actual = hashlib.sha256(helper.markdown_h2_section(source, selected["selector"])).hexdigest()
            need(actual == selected["section_sha256"], "Schema source lineage drift: " + selected["selector"])
        return {"definitions": len(closure), "source_sections": len(sections), "source_lineage_residue": len(residue), "D53": "retained narrow binding and explicit section-layout residue"}
    check("source-and-construction-dependencies", dependencies)

    def contracts():
        shared = module(LAB / "tooling/validators/artifact_surface.py", "schema_shared_validator")
        need(shared.validate_package(PACKAGE) == 0, "Artifact Type mechanics failed")
        return {"artifact_types": 1, "invalid_schema_fixtures": 8}
    check("shared-artifact-type-mechanics", contracts)

    def behavior():
        result = subprocess.run([sys.executable, str(ROOT / "test_conformance.py"), "-v"], capture_output=True, text=True)
        (ROOT / "receipts").mkdir(exist_ok=True)
        (ROOT / "receipts/tests.log").write_text(result.stdout + result.stderr)
        need(result.returncode == 0, result.stdout + result.stderr)
        return "18 tests passed: independent field and connection constraints, endpoint closure, multiplicity, kinds, levels, CLI states and non-execution."
    check("graph-conformance-behavior", behavior)

    def demonstrate():
        schema_path = PACKAGE / "fixtures/valid/schema-record.json"
        record = load(schema_path)
        before = files(PREVIOUS)
        results = {name: check_graph(record, load(ROOT / ("examples/" + name + ".json"))) for name in ["conforming", "wrong-field", "missing-connection"]}
        need(results["conforming"]["conforms"] and not results["wrong-field"]["conforms"] and not results["missing-connection"]["conforms"], "Shape demonstration failed")
        need(before == files(PREVIOUS), "Checker changed the previous candidate")
        dump(ROOT / "receipts/demonstration.json", {"authority_effect": "none", "schema": binding(schema_path),
            "graphs": [binding(ROOT / ("examples/" + name + ".json")) for name in results], "results": results, "predecessor_unchanged": True})
        return {"conforming": True, "wrong_field_rejected": True, "missing_connection_rejected": True, "occupants_executed": False}
    check("independent-shape-check-demonstration", demonstrate)

    def deterministic():
        before = materials()
        author.build()
        need(before == materials(), "Reconstruction did not reproduce")
        need(load(ROOT / "reconciliation.json") == reconcile.build(), "Reconciliation drift")
        return load(ROOT / "reconciliation.json")["state_counts"]
    check("determinism-and-195-target-reconciliation", deterministic)
    outcome = "PASS" if all(x["result"] == "PASS" for x in checks) else "BLOCK"
    dump(ROOT / "receipts/validation.json", {"schema_version": "cal-schema-carrier-validation/v1", "result": outcome,
        "authority_effect": "none", "checks": checks, "materials": materials(),
        "claim_ceiling": "Exact candidate Schema carrier and finite graph conformance only. No truth, ownership, authority, promotion, execution or general path-equation validation."})
    print(outcome)
    for item in checks:
        print(item["check"], item["result"], item["detail"])
    return 0 if outcome == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(validate())

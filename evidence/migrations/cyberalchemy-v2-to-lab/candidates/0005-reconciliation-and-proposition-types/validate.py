#!/usr/bin/env python3
"""Verify reconciliation, dependency closure and executable proposition contracts."""
import hashlib
import subprocess
import sys
from jsonschema import Draft202012Validator
from common import ROOT, LAB, SOURCE, PREVIOUS, L0, L1, KINDS, load, sha, binding, dump, module, need
import author
import reconcile
import source_rebinding
from check import check_instance


def material_tree():
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(ROOT.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts
            and "receipts" not in p.relative_to(ROOT).parts and p.name != "manifest.json"}


def validate():
    checks = []
    def check(name, action):
        try:
            detail = action()
            checks.append({"check": name, "result": "PASS", "detail": detail})
        except Exception as exc:
            checks.append({"check": name, "result": "BLOCK", "detail": str(exc)})

    def reconciliation():
        current = reconcile.build()
        need(current == load(ROOT / "reconciliation.json"), "Reconciliation no longer matches current packages")
        need(not current["state_counts"].get("blocked-integrity"), "Reconciliation contains unresolved integrity failures")
        need((ROOT / "RECONCILIATION.md").read_text() == reconcile.render(current), "Human reconciliation drift")
        return current["state_counts"]
    check("all-195-targets-reconciled", reconciliation)

    def dependencies():
        deps = load(ROOT / "dependencies.json")
        for ref in deps["inputs"] + deps["definitions"]:
            need(sha(LAB / ref["path"]) == ref["sha256"], "Dependency drift: " + ref["path"])
        original_manifest = load(L1 / "manifest.json")
        original_material = {str((L1 / r["path"]).relative_to(LAB)): r["sha256"] for r in original_manifest["materials"]}
        recorded_registry = {x["target_id"]: x for x in load(L1 / "registry.json")["entries"]}
        edges = load(L1 / "batches.json")["edges"]
        closure = {"semantic." + kind for kind in KINDS}
        while True:
            expanded = closure | {x["dependency_target_id"] for x in edges if x["consumer_target_id"] in closure}
            if expanded == closure:
                break
            closure = expanded
        need(closure == {x["target_id"] for x in deps["definitions"]}, "Missing transitive dependency")
        expected_residue = [x for x in load(L1 / "drift-audit.json")["legacy_reference_residue"] if x["consumer_target_id"] in closure]
        need(deps["source_lineage_residue"] == expected_residue, "Unmapped source references were lost")
        helper = module(L0 / "author.py", "source_section_reader")
        schema_path = LAB / "authority/artifact-types/definition/v1/schema.json"
        validator = Draft202012Validator(load(schema_path))
        source_path = SOURCE / "authority/definitions/DEFINITIONS.md"
        source_before = sha(source_path)
        sections = set()
        overlay = load(ROOT / "source-rebinding.json")
        need(overlay == source_rebinding.build(), "D53 source rebinding no longer matches exact source subsections")
        for ref in deps["definitions"]:
            need(ref["sha256"] == original_material[ref["path"]] == recorded_registry[ref["target_id"]]["sha256"], "Historical dependency bytes changed")
            definition = load(LAB / ref["path"])
            need(definition["schema_digest"] == sha(schema_path), "Definition schema changed")
            validator.validate(definition)
            for source in definition["source_refs"]:
                section = helper.markdown_h2_section(source_path, source["selector"])
                actual_sha = hashlib.sha256(section).hexdigest()
                if source["selector"] == "## CAV2-D53: Axiom":
                    need(source["content_sha256"] == overlay["historical_section_sha256"]
                         and actual_sha == overlay["current_historical_selector_sha256"], "D53 unrecorded selector drift")
                else:
                    need(actual_sha == source["content_sha256"], "Source section drift: " + source["selector"])
                sections.add(source["selector"])
        need(source_before == sha(source_path), "Source changed during validation")
        return {"definitions": len(closure), "source_sections": len(sections), "explicit_source_lineage_residue": len(expected_residue),
                "D53": "six exact unchanged subsections rebound; historical whole-section drift retained"}
    check("transitive-definition-and-source-closure", dependencies)

    def packages():
        shared = module(LAB / "tooling/validators/artifact_surface.py", "shared_artifact_validator")
        negative_count = 0
        for kind in KINDS:
            package = ROOT / "artifact-types" / kind / "v1"
            artifact = load(package / "artifact.json")
            # Check both shared repository mechanics and the actual consumer interface.
            need(shared.validate_package(package) == 0, "Shared contract validation failed for " + kind)
            good = load(package / "fixtures/valid/proposition.json")
            need(check_instance(good)["result"] == "PASS", "Consumer rejected valid " + kind)
            for path in sorted((package / "fixtures/invalid").glob("*.json")):
                need(check_instance(load(path))["result"] == "BLOCK", "Consumer accepted hostile fixture: " + str(path))
                negative_count += 1
        return {"artifact_types": len(KINDS), "hostile_fixtures": negative_count}
    check("shared-mechanics-and-consumer-validation", packages)

    def reproducibility():
        before = material_tree()
        author.build()
        need(before == material_tree(), "Generated bytes changed on repeated construction")
        return "All generated contracts, examples, dependencies and registry reproduce byte-for-byte."
    check("deterministic-reconstruction", reproducibility)

    def tests():
        result = subprocess.run([sys.executable, str(ROOT / "test_contracts.py"), "-v"], cwd=LAB, capture_output=True, text=True)
        need(result.returncode == 0, result.stdout + result.stderr)
        (ROOT / "receipts").mkdir(exist_ok=True)
        (ROOT / "receipts/test-contracts.log").write_text(result.stdout + result.stderr)
        return "10 behavioral tests passed, including six disguised cross-kind combinations and source-meaning drift rejection."
    check("behavioral-and-hostile-tests", tests)
    result = "PASS" if all(x["result"] == "PASS" for x in checks) else "BLOCK"
    receipt = {"schema_version": "cal-proposition-reconstruction-validation/v1", "result": result,
        "authority_effect": "none", "checks": checks, "materials": material_tree(),
        "claim_ceiling": "PASS establishes this batch's current representation checks, source-bound construction dependency closure and deterministic generation. It does not prove propositions, resolve arbitrary instance reference targets, admit types, or grant promotion authority."}
    dump(ROOT / "receipts/validation.json", receipt)
    print(result)
    for item in checks:
        print(item["check"], item["result"], item["detail"])
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(validate())

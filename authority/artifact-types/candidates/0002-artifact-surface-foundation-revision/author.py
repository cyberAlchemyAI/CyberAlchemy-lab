#!/usr/bin/env python3
"""Author the Artifact Surface Foundation successor without touching 0001/0009."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
OLD_DEFS = LAB / "authority/definitions/candidates/0009-artifact-surface-foundation"
NEW_DEFS = LAB / "authority/definitions/candidates/0010-artifact-surface-foundation-revision"
SHARED_VALIDATOR = LAB / "tooling/validators/artifact_surface_candidate_2.py"
SHARED_GENERATOR = LAB / "tooling/generators/artifact_surface.py"
TYPE_NAMES = ["artifact-type-registry", "artifact-type-request", "canonical-package-manifest"]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(LAB))


def import_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def revise_definition(name: str) -> dict[str, Any]:
    old_path = OLD_DEFS / f"definitions/{name}/v1/definition.json"
    record = copy.deepcopy(load(old_path))
    old_ref = f"{record['definition_id']}@{record['version']}"
    record["version"] = "1.0.0-candidate.2"
    new_ref = f"{record['definition_id']}@{record['version']}"
    record["source_refs"].append({
        "source_ref": old_ref,
        "selector": "whole-json",
        "content_sha256": sha(old_path),
        "admission_posture": "candidate-unadmitted",
        "source_admission_ref": None,
    })
    record["typed_relations"] = [{
        "relation_kind_ref": "relation.successor-of",
        "from_ref": new_ref,
        "to_ref": old_ref,
        "owner_ref": "role:definition-owner",
    }]
    record["index_entry"] = {
        "index_ref": "authority/definitions/candidates/0010-artifact-surface-foundation-revision/DEFINITIONS-INDEX.md",
        "entry_id": new_ref,
    }
    record["drift_route"]["audit_ref"] = "authority/definitions/candidates/0010-artifact-surface-foundation-revision/drift-audit-postimage.json"
    record["evidence_refs"] = ["ASF-REVISION-REVIEW-01"]

    formal = record["voices"]["scientific_formal"]
    if name == "artifact-surface-classification":
        formal["normative_statement"] = "Every governed file f in package P, including P's package.json manifest, has exactly one declared surface role from canonical-instance, declared-component, generated-projection, evidence, fixture, or transient-state. The manifest self-entry is a canonical instance of Canonical Package Manifest/v1. Every canonical instance resolves to exactly one admitted Artifact Type; every other role cannot silently become canonical."
        formal["formal_expression"] = "for all f in governed(P), exists exactly one role_P(f) in {I,C,G,E,F,T}; role_P(package.json)=I and type(package.json)=CanonicalPackageManifest/v1; role_P(f)=I => |resolve_R(f)|=1; role_P(f)!=I => not canonical_subject(f)."
        formal["testable_conditions"] = [
            "Every governed file has exactly one manifest-declared role.",
            "The package manifest classifies package.json exactly once as its own canonical instance.",
            "Every canonical instance resolves to exactly one admitted Artifact Type.",
            "No generated, fixture, evidence, or transient file is accepted as a canonical subject.",
        ]
        record["voices"]["plain_language"]["explanation"] = "Every important file needs one declared job, and the manifest must list itself too. Its location never decides its role."
        record["residue_refs"] = ["Repository-wide package manifests remain unauthored; this successor only closes the manifest self-classification rule."]
    elif name == "artifact-type-resolution":
        formal["normative_statement"] = "Artifact Type Resolution is an executable deterministic operation resolve_R(a) over one canonical machine carrier and one exact registry. An explicit exact reference may select an admitted-current or admitted-historical type; discriminator-only evidence selects admitted-current types. The operation returns resolved for exactly one match, unresolved for zero, and ambiguous for multiple distinct matches. Paths, filenames, extensions, and nearest-name similarity are excluded evidence."
        formal["formal_expression"] = "M_R(a)=explicit_matches_admitted_R(a) union discriminator_matches_current_R(a); resolve_R(a)={resolved(t,state_R(t)) if |M|=1, unresolved if |M|=0, ambiguous(M) if |M|>1}; authority_effect(resolve_R)=none."
        formal["testable_conditions"] = [
            "The reusable resolver accepts an artifact and exact registry and emits one structured result.",
            "Directory movement does not change the match set.",
            "Unknown discriminators return unresolved and conflicting evidence returns ambiguous.",
            "An exact explicit historical reference resolves with its recorded historical lifecycle state while discriminator-only lookup selects current entries.",
            "Every result carries the exact registry identity and no authority effect.",
        ]
        record["voices"]["plain_language"]["explanation"] = "One reusable operation reads the file and registry, reports one exact contract or a clear unresolved/ambiguous result, and never guesses from the path."
        record["primary_consumer_refs"] = ["tooling/validators/artifact_surface_candidate_2.py", "cal.artifact-type.artifact-type-request/v1"]
        record["residue_refs"] = ["The resolver remains candidate product code until the enclosing product candidate is approved and separately admitted or activated."]
    elif name == "artifact-type-request":
        formal["normative_statement"] = "An Artifact Type Request Q is a candidate-only intake record created only after resolve_R(a) is unresolved and compatibility analysis rejects exact reuse. Q describes intended semantics, owner, package home, representation direction, validation purpose, proposed discriminator, and dependencies. Q is neither subject artifact a nor Artifact Type T, cannot satisfy a subject dependency, and has no authority effect."
        formal["formal_expression"] = "create(Q,a) only if M_R(a)=empty and no_exact_fit(a); Q != a; Q != T; authority_effect(Q)=none; consumed_as_subject(Q)=false."
        formal["testable_conditions"] = [
            "The proposed discriminator has zero admitted-current matches in the bound registry.",
            "Every request includes an existing-type compatibility analysis.",
            "Every request declares no authority effect and cannot satisfy subject dependencies.",
            "Every accepted request produces a separately identified Artifact Type candidate.",
        ]
        record["residue_refs"] = ["No real unresolved carrier receives a request until its owner selects that treatment."]
    elif name == "canonical-package-manifest":
        formal["normative_statement"] = "A Canonical Package Manifest M declares one canonical package home, aggregate, lifecycle owner, unit of change, every governed member's unique surface role, and every independent nested package relation. M must classify its own package.json exactly once as a canonical instance of Canonical Package Manifest/v1. Membership and nesting are explicit data, not directory inference."
        formal["formal_expression"] = "M=(home,aggregate,owner,unit,members,nested); members[package.json]=(I,CanonicalPackageManifest/v1,1); for all f in governed(home), exists exactly one members[f]; independent(n) => exists manifest(n) and relation(M,n)."
        formal["testable_conditions"] = [
            "package.json occurs exactly once and is a canonical instance of Canonical Package Manifest/v1.",
            "Every canonical carrier has exactly one admitted type resolution.",
            "Every governed non-carrier has exactly one declared surface role.",
            "Every independent nested lifecycle has its own manifest and explicit parent relation.",
        ]
        record["voices"]["plain_language"]["explanation"] = "The manifest says what changes together and what every file does, including itself. Nested lifecycles are declared, never guessed from folders."
        record["residue_refs"] = ["No existing package home is migrated by this Definition successor."]
    return record


def author_definitions() -> None:
    names = ["artifact-surface-classification", "artifact-type-resolution", "artifact-type-request", "canonical-package-manifest"]
    old_candidate = load(OLD_DEFS / "candidate.json")
    definitions = []
    source_bindings = copy.deepcopy(old_candidate["source_bindings"])
    for name in names:
        old_path = OLD_DEFS / f"definitions/{name}/v1/definition.json"
        old = load(old_path)
        source_bindings.append({
            "source_ref": f"{old['definition_id']}@{old['version']}",
            "repository": "CyberAlchemy-lab",
            "path": relative(old_path),
            "selector": {"kind": "whole-file"},
            "sha256": sha(old_path),
            "admission_posture": "candidate-unadmitted",
        })
        new_path = NEW_DEFS / f"definitions/{name}/v1/definition.json"
        dump(new_path, revise_definition(name))
        definitions.append({
            "definition_id": old["definition_id"],
            "version": "1.0.0-candidate.2",
            "disposition": "successor-candidate-epoch",
            "path": relative(new_path),
            "human_projection_path": relative(new_path.with_name("DEFINITION.md")),
        })
    source_predecessor_registry = OLD_DEFS / "registry-postimage.json"
    predecessor_data = copy.deepcopy(load(source_predecessor_registry))
    predecessor_data["current_lookup"] = predecessor_data["proposed_current_lookup"]
    predecessor_data["adapter_source"] = {"path": relative(source_predecessor_registry), "sha256": sha(source_predecessor_registry)}
    predecessor_registry = NEW_DEFS / "predecessor-registry-adapter.json"
    dump(predecessor_registry, predecessor_data)
    candidate = {
        "schema_version": "cyberalchemy-lab-definition-candidate-set/v1",
        "candidate_id": "CAL-DEFINITION-CANDIDATE-SET-ARTIFACT-SURFACE-FOUNDATION-REVISION-0010",
        "title": "Artifact Surface Foundation Definition Successors",
        "status": "candidate-authored-owner-review-open",
        "authority_effect": "none",
        "semantic_owner_ref": "role:definition-owner",
        "definition_contract": old_candidate["definition_contract"],
        "predecessor_registry": {"path": relative(predecessor_registry), "sha256": sha(predecessor_registry), "entry_count": len(load(predecessor_registry)["entries"])},
        "definitions": definitions,
        "source_bindings": source_bindings,
        "ownership_boundary": "Definitions own revised meaning; executable candidate code realizes but cannot redefine or admit it. Candidate 0009 remains immutable provenance.",
        "registry_postimage_id": "CAL-DEFINITION-REGISTRY-POSTIMAGE-ARTIFACT-SURFACE-FOUNDATION-REVISION-0010",
        "registry_claim_ceiling": "Successor postimage over candidate 0009. It adds four unadmitted successor epochs and changes neither the live registry nor admission state.",
        "hostile_fixture_rules": old_candidate["hostile_fixture_rules"],
        "promotion_blockers": [
            "Four successor Definitions require exact definition-owner review.",
            "Artifact Type candidate.2 packages and executable resolver remain product-construction outputs.",
            "Validation and product tests grant no admission, activation, migration, or publication authority.",
        ],
        "source_direction": {"canonical": "candidate.json", "human_projection": "CANDIDATE.md", "projection_policy": "generated-only", "generator": "render.py", "generator_ref": "candidate:cal.generator.definition-candidate-pack/v1"},
        "claim_ceiling": "This successor corrects and makes executable four Artifact Surface meanings. It does not admit Definitions or Artifact Types, activate the registry, migrate packages, commit, push, publish, release, or deploy.",
    }
    dump(NEW_DEFS / "candidate.json", candidate)
    drift = {
        "schema_version": "cyberalchemy-lab-definition-drift-audit/v1",
        "audit_id": "CAL-DEFINITION-DRIFT-AUDIT-ARTIFACT-SURFACE-REVISION-0010",
        "title": "Artifact Surface Foundation successor drift audit",
        "status": "candidate-postimage",
        "authority_effect": "none",
        "summary": {"review_defects": 4, "successor_definitions": 4, "undefined_critical_terms": 0, "conflicting_consumers": 0},
        "findings": [
            {"finding_id": "ASF-REV-001", "severity": "required", "status": "resolved-in-successor", "condition": "Artifact Type Request candidate.1 contains a broken normative phrase.", "target": relative(NEW_DEFS / "definitions/artifact-type-request/v1/definition.json"), "remediation": "Correct Q's non-identity with both subject artifact a and Artifact Type T."},
            {"finding_id": "ASF-REV-002", "severity": "required", "status": "resolved-in-successor", "condition": "Artifact Type Resolution candidate.1 lacks an executable operation contract.", "target": relative(NEW_DEFS / "definitions/artifact-type-resolution/v1/definition.json"), "remediation": "Require a reusable structured resolver with resolved, unresolved, and ambiguous outcomes."},
            {"finding_id": "ASF-REV-003", "severity": "required", "status": "resolved-in-successor", "condition": "Canonical Package Manifest candidate.1 does not require its own role entry.", "target": relative(NEW_DEFS / "definitions/canonical-package-manifest/v1/definition.json"), "remediation": "Require exactly one canonical package.json self-entry."},
            {"finding_id": "ASF-REV-004", "severity": "required", "status": "resolved-in-product-candidate", "condition": "The selected-tree audit was authored as fixed findings instead of computed from exact subjects.", "target": "tooling/validators/artifact_surface_candidate_2.py", "remediation": "Compute the audit from an explicit plan, current bytes, and the reusable resolver."},
        ],
        "claim_ceiling": "Candidate drift assessment only; resolved-in-successor does not mean admitted or activated.",
    }
    dump(NEW_DEFS / "drift-audit-postimage.json", drift)
    for source in sorted((OLD_DEFS / "fixtures/invalid").glob("*.json")):
        dump(NEW_DEFS / "fixtures/invalid" / source.name, load(source))
    write(NEW_DEFS / "render.py", '''#!/usr/bin/env python3
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parent/"_candidate_pack.py"
spec=importlib.util.spec_from_file_location("candidate_pack",SHARED)
module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
if __name__=="__main__": module.render(ROOT)
''')
    write(NEW_DEFS / "build.py", '''#!/usr/bin/env python3
from pathlib import Path
import runpy
if __name__=="__main__": runpy.run_path(str(Path(__file__).with_name("render.py")),run_name="__main__")
''')
    write(NEW_DEFS / "validate.py", '''#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parent; SHARED=ROOT.parent/"_candidate_pack.py"
def hostile(subject):
 failures=set()
 if subject.get("resolution_basis")=="directory": failures.add("directory-must-not-resolve-artifact-type")
 if subject.get("kind")=="canonical-carrier" and not subject.get("declared_by_package_manifest"): failures.add("canonical-carrier-must-be-declared")
 if subject.get("kind")=="artifact-type-resolution" and len(subject.get("matches",[]))!=1: failures.add("artifact-type-resolution-must-be-unique")
 if subject.get("kind")=="artifact-type-request" and subject.get("consumed_as_subject") is True: failures.add("artifact-type-request-must-not-substitute-for-subject")
 if subject.get("independent_lifecycle") is True and not subject.get("package_manifest_ref"): failures.add("independent-lifecycle-must-have-package-manifest")
 return failures
if __name__=="__main__":
 spec=importlib.util.spec_from_file_location("candidate_pack",SHARED); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); module.hostile_failures=hostile
 result=module.validate(ROOT,{"cal.definition.artifact-surface-classification","cal.definition.artifact-type-resolution","cal.definition.artifact-type-request","cal.definition.canonical-package-manifest"})
 receipt=json.loads((ROOT/"receipts/validation.json").read_text()); count=len(json.loads((ROOT/"registry-postimage.json").read_text())["entries"]); ok=count==42
 receipt["checks"].append({"check_id":"successor-registry-count","result":"PASS" if ok else "FAIL","detail":{"expected":42,"actual":count}})
 failed=[x for x in receipt["checks"] if x["result"]=="FAIL"]; receipt["result"]="PASS" if result==0 and not failed else "FAIL"; receipt["summary"]={"passed":len(receipt["checks"])-len(failed),"failed":len(failed),"total":len(receipt["checks"])}; receipt["promotion_eligibility"]="blocked-by-declared-dependencies" if receipt["result"]=="PASS" else "not-eligible"
 (ROOT/"receipts/validation.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\\n"); print(f"ARTIFACT_SURFACE_DEFINITION_SUCCESSORS={receipt['result']}"); print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}"); raise SystemExit(0 if receipt["result"]=="PASS" else 1)
''')
    pack = import_path("candidate_pack", NEW_DEFS.parent / "_candidate_pack.py")
    pack.render(NEW_DEFS)


def self_entry() -> dict[str, Any]:
    return {"path": "package.json", "role": "canonical-instance", "artifact_type_ref": "cal.artifact-type.canonical-package-manifest/v1", "resolution_count": 1}


def author_type(name: str) -> None:
    old_root = LAB / f"authority/artifact-types/{name}/v1"
    new_root = old_root / "candidates/0002-executable-surface"
    artifact = copy.deepcopy(load(old_root / "artifact.json"))
    schema = copy.deepcopy(load(old_root / "schema.json"))
    artifact["version"] = "1.0.0-candidate.2"
    artifact["validation_contract"]["shared_validator_path"] = relative(SHARED_VALIDATOR)
    artifact["validation_contract"]["shared_validator_sha256"] = sha(SHARED_VALIDATOR)

    replacements = {
        "cal.definition.artifact-surface-classification@1.0.0-candidate.1": "cal.definition.artifact-surface-classification@1.0.0-candidate.2",
        "cal.definition.artifact-type-resolution@1.0.0-candidate.1": "cal.definition.artifact-type-resolution@1.0.0-candidate.2",
        "cal.definition.artifact-type-request@1.0.0-candidate.1": "cal.definition.artifact-type-request@1.0.0-candidate.2",
        "cal.definition.canonical-package-manifest@1.0.0-candidate.1": "cal.definition.canonical-package-manifest@1.0.0-candidate.2",
    }
    artifact["semantic_definition_refs"] = [replacements.get(ref, ref) for ref in artifact["semantic_definition_refs"]]
    for binding in artifact["semantic_definition_bindings"]:
        if binding["definition_ref"] in replacements:
            new_ref = replacements[binding["definition_ref"]]
            definition_id = new_ref.split("@")[0].split("cal.definition.", 1)[1]
            path = NEW_DEFS / f"definitions/{definition_id}/v1/definition.json"
            binding.update({"definition_ref": new_ref, "path": relative(path), "sha256": sha(path), "admission_posture": "candidate-unadmitted"})

    valid = copy.deepcopy(load(old_root / artifact["validation_contract"]["positive_witness"]))
    negatives = {path.name: copy.deepcopy(load(path)) for path in sorted((old_root / "fixtures/invalid").glob("*.json"))}
    if name == "artifact-type-request":
        proposed = {"path": "/schema_version", "value": "cyberalchemy-lab-ontology-product-runtime-binding/v1"}
        schema["required"].append("proposed_discriminator")
        schema["properties"]["proposed_discriminator"] = {
            "type": "object", "additionalProperties": False, "required": ["path", "value"],
            "properties": {"path": {"const": "/schema_version"}, "value": {"type": "string", "minLength": 1}},
        }
        valid["proposed_discriminator"] = proposed
        for subject in negatives.values():
            subject["proposed_discriminator"] = proposed
        existing = copy.deepcopy(valid)
        existing["request_id"] = "CAL-ATR-FIXTURE-EXISTING-DISCRIMINATOR"
        existing["proposed_discriminator"] = {"path": "/schema_version", "value": "cyberalchemy-lab-product-identity/v1"}
        negatives["existing-discriminator.json"] = existing
    elif name == "canonical-package-manifest":
        valid["surface_entries"].insert(0, self_entry())
        for subject in negatives.values():
            subject["surface_entries"].insert(0, self_entry())
        missing = copy.deepcopy(valid)
        missing["surface_entries"] = [entry for entry in missing["surface_entries"] if entry["path"] != "package.json"]
        negatives["missing-self-entry.json"] = missing
        duplicate = copy.deepcopy(valid)
        duplicate["surface_entries"].append(copy.deepcopy(duplicate["surface_entries"][1]))
        negatives["duplicate-surface-path.json"] = duplicate
        schema["properties"]["surface_entries"].update({
            "contains": {
                "type": "object",
                "properties": {
                    "path": {"const": "package.json"},
                    "role": {"const": "canonical-instance"},
                    "artifact_type_ref": {"const": "cal.artifact-type.canonical-package-manifest/v1"},
                    "resolution_count": {"const": 1},
                },
                "required": ["path", "role", "artifact_type_ref", "resolution_count"],
            },
            "minContains": 1,
            "maxContains": 1,
        })
    elif name == "artifact-type-registry":
        duplicate = copy.deepcopy(valid)
        duplicate["registry_id"] = "cal.registry.fixture.duplicate-discriminator"
        duplicate["entries"].append(copy.deepcopy(duplicate["entries"][0]))
        duplicate["entries"][-1]["artifact_type_ref"] = "cal.artifact-type.ambiguous-shadow/v1"
        negatives["duplicate-current-discriminator.json"] = duplicate

    artifact["validation_contract"]["negative_witnesses"] = [f"fixtures/invalid/{filename}" for filename in sorted(negatives)]
    dump(new_root / "schema.json", schema)
    artifact["schema_digest"] = sha(new_root / "schema.json")
    dump(new_root / "artifact.json", artifact)
    dump(new_root / artifact["validation_contract"]["positive_witness"], valid)
    for filename, subject in negatives.items():
        dump(new_root / "fixtures/invalid" / filename, subject)
    generator = import_path("artifact_surface_generator", SHARED_GENERATOR)
    persisted_artifact = load(new_root / "artifact.json")
    persisted_valid = load(new_root / artifact["validation_contract"]["positive_witness"])
    write(new_root / "ARTIFACT.md", generator.render_artifact(persisted_artifact))
    write(new_root / artifact["validation_contract"]["positive_projection"], generator.render_instance(persisted_artifact, persisted_valid))
    write(new_root / "validate.py", f'''#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[5]
cmd=[sys.executable,str(LAB/"tooling/validators/artifact_surface_candidate_2.py"),"validate-package",str(ROOT),"--registry",str(LAB/"authority/artifact-types/candidates/0001-artifact-surface-foundation/registry.json")]
raise SystemExit(subprocess.run(cmd).returncode)
''')


def main() -> None:
    author_definitions()
    for name in TYPE_NAMES:
        author_type(name)
    print("ARTIFACT_SURFACE_SUCCESSOR_AUTHORED=PASS")


if __name__ == "__main__":
    main()

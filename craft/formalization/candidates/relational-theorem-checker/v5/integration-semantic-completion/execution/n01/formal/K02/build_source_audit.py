"""Bind exact K02 branches and expose source-schema semantic boundaries."""
from pathlib import Path
import copy
import hashlib
import importlib.metadata
import json

import jsonschema

HERE = Path(__file__).resolve().parent
SUCCESSOR = HERE.parents[3]
ROOT = SUCCESSOR.parents[5]
NAMES = {"agent-assignment": "agentAssignment", "goal": "goal", "product": "product",
         "product-capability": "productCapability", "project": "project",
         "research-inquiry": "researchInquiry"}


def binding(path):
    return {"path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    declarations = ROOT / "authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds"
    relation_path = declarations / "addresses-intent.json"
    member_path = declarations / "member-of.json"
    relation = json.loads(relation_path.read_text())["payload"]
    pairs = relation["allowed_endpoint_pairs"]
    assert len(pairs) == 6 and {p["source_kind"] for p in pairs} == set(NAMES)
    assert all(p["target_kind"] == "intent" for p in pairs)
    member_pairs = [p for p in json.loads(member_path.read_text())["payload"]["allowed_endpoint_pairs"]
                    if p["source_kind"] in NAMES]
    assert len(member_pairs) == 5
    assert all(p["target_kind"] in {"project", "product"} for p in member_pairs)
    sources = ", ".join("." + NAMES[p["source_kind"]] for p in pairs)
    memberships = ", ".join("(." + NAMES[p["source_kind"]] + ", ." + p["target_kind"] + ")"
                            for p in member_pairs)
    lean = ("-- Generated source data; no source semantic refinement or discharge.\n"
            f"-- K02 source SHA256: {binding(relation_path)['sha256']}\n"
            f"-- member-of source SHA256: {binding(member_path)['sha256']}\n"
            "import IntentAddressingCandidate\nset_option autoImplicit false\n"
            "namespace RelationalSuccessor.CandidateIntentAddressing.SourceSignature\n"
            f"def capturedSources : List SubjectKind := [{sources}]\n"
            f"def capturedMembershipPairs : List (SubjectKind × ContainerKind) := [{memberships}]\n"
            "theorem source_signature_equals_model : capturedSources = allowedSources := rfl\n"
            "theorem membership_signature_equals_model (source : SubjectKind) (target : ContainerKind) :\n"
            "    (source, target) ∈ capturedMembershipPairs ↔ AllowedMembership source target := by\n"
            "  cases source <;> cases target <;> simp [capturedMembershipPairs, AllowedMembership]\n"
            "#print axioms source_signature_equals_model\n"
            "#print axioms membership_signature_equals_model\n"
            "end RelationalSuccessor.CandidateIntentAddressing.SourceSignature\n")
    (HERE / "SourceSignature.lean").write_text(lean)
    package = ROOT / "authority/artifact-types/intent-resolution/v1"
    schema_path, fixture_path = package / "schema.json", package / "fixtures/valid/record.json"
    schema = json.loads(schema_path.read_text())
    fixture = json.loads(fixture_path.read_text())
    validator = jsonschema.Draft202012Validator(schema)
    errors = lambda data: sorted(e.message for e in validator.iter_errors(data))
    assert not errors(fixture)
    probes = []
    for name, operation, expected in [
        ("empty-satisfaction-tests", lambda d: d["payload"].update(satisfaction_test_refs=[]), True),
        ("selected-and-excluded-overlap", lambda d: d["payload"]["excluded_subject_refs"].append(
            d["payload"]["selected_subject_refs"][0]), True),
        ("no-selected-subjects", lambda d: d["payload"].update(selected_subject_refs=[]), True),
        ("duplicate-test", lambda d: d["payload"].update(satisfaction_test_refs=[
            d["payload"]["satisfaction_test_refs"][0]] * 2), False),
        ("missing-owner-decision", lambda d: d["payload"].pop("owner_decision_ref"), False),
    ]:
        altered = copy.deepcopy(fixture)
        operation(altered)
        findings = errors(altered)
        accepted = not findings
        assert accepted == expected, (name, findings)
        probes.append({"case": name, "schema_accepts": accepted, "errors": findings})
    contract = relation["qualifier_contract"]
    qualifier_schema = {"type": "object", "additionalProperties": not contract["closed"],
                        "properties": contract["properties"], "required": contract["required_axes"]}
    raw = {"intent_resolution_ref": "resolution:any", "addressing_role": "all-powerful"}
    assert not list(jsonschema.Draft202012Validator(qualifier_schema).iter_errors(raw))
    report = {"task": "N01", "unit": "K02", "result": "source-boundary-audit-pass",
              "driver": binding(Path(__file__)), "source_relation": binding(relation_path),
              "membership_source": binding(member_path), "resolution_schema": binding(schema_path),
              "resolution_fixture": binding(fixture_path),
              "generated_signature": binding(HERE / "SourceSignature.lean"),
              "declared_pairs": pairs, "filtered_membership_pairs": member_pairs,
              "jsonschema_version": importlib.metadata.version("jsonschema"),
              "schema_probes": probes, "arbitrary_nonempty_role_passes_raw_qualifier_shape": True,
              "semantic_duties": ["exclude subjects even when they are also selected",
                                  "preserve selected test completeness and an explicit empty-test policy",
                                  "resolve roles through the exact kind/pair owner catalog",
                                  "separate selection-list membership from member-of graph semantics"],
              "actual_owner_review": None, "source_semantic_refinement_complete": False,
              "inherited_discharges": 0, "authority_effect": "none"}
    (HERE / "source-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"result": report["result"], "K02_pairs": len(pairs),
                      "membership_pairs": len(member_pairs), "source_probes": len(probes)}))


if __name__ == "__main__":
    run()

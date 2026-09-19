#!/usr/bin/env python3
import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module

SEEDS = ["authority-model", "exact-publication-authorization-invariant", "experiment-design", "experiment-run", "product-thesis"]
TEXT = {"type": "string", "pattern": "\\S"}
DIGEST = {"type": "string", "pattern": "^[a-f0-9]{64}$"}


def obj(properties):
    return {"type": "object", "additionalProperties": False, "required": sorted(properties), "properties": properties}


def build():
    ref = obj({"path": TEXT, "sha256": DIGEST})
    subject = obj({"subject_ref": TEXT, "path": TEXT, "sha256": DIGEST, "material_manifest": ref})
    actor = obj({"principal_ref": TEXT, "role_ref": TEXT})
    date = {"type": "string", "format": "date-time", "pattern": "Z$"}
    provenance = {"enum": ["simulation", "recorded-owner-statement"]}
    common = {"proposal_id": TEXT, "scope_ref": TEXT, "subject": subject, "selected_option_id": TEXT,
              "actor": actor, "recorded_at": date, "provenance_kind": provenance}
    schema = obj({"schema_version": {"const": "cyberalchemy-lab-decision/v1"},
        "artifact_type_ref": {"const": "cal.artifact-type.decision/v1"}, "decision_id": TEXT,
        "status": {"const": "candidate-unadmitted"}, "authority_effect": {"const": "none"},
        **common, "proposal": ref, "statement": ref, "declared_effect": TEXT, "rationale": TEXT,
        "challenge_route": TEXT, "supersession_policy": {"const": "new-record-required-preserve-prior-bytes"},
        "source_direction": obj({"canonical": {"const": "decision.json"}, "human_projection": {"const": "DECISION.md"}, "projection_policy": {"const": "generated-only"}}),
        "claim_ceiling": TEXT})
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "Decision candidate bound to an exact proposal and statement"})
    proposal_schema = obj({"proposal_id": TEXT, "scope_ref": TEXT, "subject": subject, "owner_role_ref": TEXT,
        "authority_effect": {"const": "none"}, "options": {"type": "array", "minItems": 2, "maxItems": 20,
        "items": obj({"option_id": TEXT, "description": TEXT, "declared_effect": TEXT})}})
    statement_schema = obj({**common, "proposal_sha256": DIGEST, "statement_text": TEXT, "authority_effect": {"const": "none"}})
    for name, value in [("schema.json", schema), ("proposal.schema.json", proposal_schema), ("statement.schema.json", statement_schema)]:
        dump(PACKAGE / name, value)
    dump(ROOT / "contracts.json", {"authority_effect": "none", "schemas": [binding(PACKAGE / name) for name in ["schema.json", "proposal.schema.json", "statement.schema.json"]]})
    artifact = load(PREVIOUS / "artifact-types/constitution/v1/artifact.json")
    definitions = [L1 / f"definitions/{name}/v1/definition.json" for name in SEEDS]
    goal = LAB / "authority/definitions/candidates/0006-craft-identity/definitions/goal/v1/definition.json"
    definitions.append(goal)
    binds = [{**binding(path), "definition_ref": load(path)["definition_id"] + "@" + load(path)["version"], "admission_posture": "admitted" if path == goal else "candidate-unadmitted"} for path in definitions]
    artifact.update(artifact_type_id="cal.artifact-type.decision", artifact_type_ref="cal.artifact-type.decision/v1", name="Decision",
        schema_ref="cal.schema.decision/v1", schema_digest=sha(PACKAGE / "schema.json"), semantic_definition_refs=[x["definition_ref"] for x in binds],
        semantic_definition_bindings=binds, distinct_validation_purpose="Records an authorized choice bound to exact candidate bytes and scope.")
    artifact["classification"].update(semantic_kind="decision", lifecycle_posture_ref="candidate:decision-reconstruction/v1")
    artifact["instance_contract"].update(canonical_filename="decision.json", human_filename="DECISION.md", identity_field="decision_id",
        required_semantic_fields=sorted(set(schema["required"]) - {"schema_version", "status", "authority_effect", "source_direction", "claim_ceiling"}))
    artifact["orthogonality_rules"] = [{"rule_id": "DECISION-01", "statement": "The selected choice, exact proposal, subject bytes, role, statement and scope must agree."},
        {"rule_id": "DECISION-02", "statement": "Internal agreement does not authenticate a principal or establish role authority; the checker grants no effect."},
        {"rule_id": "DECISION-03", "statement": "A change to any bound subject, proposal or statement invalidates the old binding; represent a new decision without rewriting prior bytes."}]
    artifact["four_facets"] = {"classification": "Candidate Decision carrier preserving the five selected source lineages.", "schema": "Closed decision, proposal and statement records with explicit provenance.",
        "machine_checkable": "Cross-record agreement, current digest bindings, option uniqueness, scope and actor checks.", "human_continuation": "Generated DECISION.md exposes the exact simulated choice and its limitations."}
    artifact["typed_residue"] = [{"residue_id": "DECISION-R1", "owner_ref": "role:authority-owner", "missing": "Authenticated decision-maker and verified role authority.", "consequence": "A valid record is not authorization; the inspection always reports authority unverified."},
        {"residue_id": "DECISION-R2", "owner_ref": "role:decision-owner", "missing": "Append-only decision storage and verified supersession chains.", "consequence": "This read-only checker detects changed bound bytes but does not prevent filesystem edits or establish a complete decision history."}]
    artifact["claim_ceiling"] = "Candidate decision record and binding-integrity inspection only. No authentication, authority verification, admission, effect execution or immutable storage guarantee."
    exact_subject = {"subject_ref": "candidate:constitution-carrier-0007", **binding(PREVIOUS / "candidate.json"), "material_manifest": binding(PREVIOUS / "manifest.json")}
    proposal = {"proposal_id": "CAL-DECISION-DEMO-PROPOSAL-001", "scope_ref": "scope:constitution-candidate-review", "subject": exact_subject,
        "owner_role_ref": "role:product-review-owner", "authority_effect": "none",
        "options": [{"option_id": "review", "description": "Record intent to review this exact candidate.", "declared_effect": "record-review-intent"},
                    {"option_id": "revise", "description": "Request revisions to this candidate.", "declared_effect": "record-revision-request"},
                    {"option_id": "defer", "description": "Defer the review.", "declared_effect": "record-deferral"},
                    {"option_id": "reject", "description": "Record rejection of this candidate.", "declared_effect": "record-rejection"}]}
    proposal_path = ROOT / "examples/proposal.json"; dump(proposal_path, proposal)
    statement = {"proposal_id": proposal["proposal_id"], "proposal_sha256": sha(proposal_path), "scope_ref": proposal["scope_ref"], "subject": exact_subject,
        "selected_option_id": "review", "actor": {"principal_ref": "simulation:reviewer", "role_ref": proposal["owner_role_ref"]},
        "recorded_at": "2026-09-07T00:00:00Z", "provenance_kind": "simulation", "authority_effect": "none",
        "statement_text": "Simulated choice to review the exact candidate. No human approval is asserted."}
    statement_path = ROOT / "examples/statement.json"; dump(statement_path, statement)
    example = {"schema_version": "cyberalchemy-lab-decision/v1", "artifact_type_ref": "cal.artifact-type.decision/v1", "decision_id": "CAL-DECISION-SIMULATION-001",
        "status": "candidate-unadmitted", "authority_effect": "none", **{key: statement[key] for key in common},
        "proposal": binding(proposal_path), "statement": binding(statement_path), "declared_effect": "record-review-intent",
        "rationale": "Demonstrate exact choice binding without asserting a real owner decision.", "challenge_route": "role:decision-owner",
        "supersession_policy": "new-record-required-preserve-prior-bytes",
        "source_direction": {"canonical": "decision.json", "human_projection": "DECISION.md", "projection_policy": "generated-only"},
        "claim_ceiling": "Simulation fixture only; not the user's approval and not authorization to adopt the Constitution."}
    invalid = {}
    for name, key, value in [("self-admission", "status", "admitted"), ("authority-effect", "authority_effect", "authorize"), ("blank-scope", "scope_ref", " "), ("extra-authority-field", "authority_verified", True), ("invalid-date", "recorded_at", "yesterday"), ("erase-history", "supersession_policy", "overwrite-prior"), ("missing-provenance", "provenance_kind", "unknown")]:
        bad = copy.deepcopy(example); bad[key] = value; invalid[name] = bad
    bad = copy.deepcopy(example); bad["subject"]["sha256"] = "invalid"; invalid["invalid-subject-digest"] = bad
    artifact["validation_contract"].update(positive_witness="fixtures/valid/decision.json", positive_projection="fixtures/valid/DECISION.md",
        negative_witnesses=["fixtures/invalid/" + name + ".json" for name in sorted(invalid)], validator_path=str((ROOT / "validate.py").relative_to(LAB)))
    dump(PACKAGE / "artifact.json", artifact); dump(PACKAGE / "fixtures/valid/decision.json", example)
    for name, bad in invalid.items():
        dump(PACKAGE / ("fixtures/invalid/" + name + ".json"), bad)
    renderer = module(LAB / "tooling/generators/artifact_surface.py", "decision_renderer")
    artifact = load(PACKAGE / "artifact.json")
    (PACKAGE / "ARTIFACT.md").write_text(renderer.render_artifact(artifact))
    (PACKAGE / "fixtures/valid/DECISION.md").write_text(renderer.render_instance(artifact, load(PACKAGE / "fixtures/valid/decision.json")))
    dump(ROOT / "registry.json", {"authority_effect": "none", "entries": [{"target_id": "type.decision", "family": "artifact-type", "status": "candidate-unadmitted", **binding(PACKAGE / "artifact.json")} ]})
    edges = load(L1 / "batches.json")["edges"]; selected = {"semantic." + name for name in SEEDS}
    while True:
        expanded = selected | {x["dependency_target_id"] for x in edges if x["consumer_target_id"] in selected}
        if expanded == selected:
            break
        selected = expanded
    registry = {x["target_id"]: x for x in load(L1 / "registry.json")["entries"]}
    scaffold = ROOT.parent / "0003-review-led-reconstruction/target-candidates/artifact-type/type-decision/v1/artifact.json"
    dump(ROOT / "dependencies.json", {"authority_effect": "none", "seed_targets": ["semantic." + name for name in SEEDS],
        "inputs": [binding(PREVIOUS / "manifest.json"), binding(L1 / "batches.json"), binding(goal), binding(scaffold)],
        "definitions": [{"target_id": target, **binding(LAB / registry[target]["path"])} for target in sorted(selected)],
        "selected_source_sections": load(scaffold)["source_refs"],
        "source_lineage_residue": [x for x in load(L1 / "drift-audit.json")["legacy_reference_residue"] if x["consumer_target_id"] in selected]})


if __name__ == "__main__":
    build()

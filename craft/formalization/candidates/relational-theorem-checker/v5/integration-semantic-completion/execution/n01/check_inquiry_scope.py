"""Source-bound evidence for K01's optionality clarification, not acceptance."""
from pathlib import Path
import copy
import hashlib
import importlib.metadata
import json

import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[7]


def binding(path):
    return {"path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    package = ROOT / "authority/artifact-types/research-inquiry/v1"
    schema_path = package / "schema.json"
    witness_path = package / "fixtures/valid/record.json"
    schema = json.loads(schema_path.read_text())
    witness = json.loads(witness_path.read_text())
    validator = jsonschema.Draft202012Validator(schema)
    errors = lambda data: sorted(error.message for error in validator.iter_errors(data))
    assert not errors(witness)
    assert not any("improvement" in key for key in witness)
    controls = []
    for field in ["question", "project_ref", "goal_refs", "method_ref", "stop_conditions"]:
        altered = copy.deepcopy(witness)
        del altered[field]
        findings = errors(altered)
        assert f"'{field}' is a required property" in findings
        controls.append({"removed": field, "refused": True, "errors": findings})
    declarations = ROOT / "authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds"
    connections = []
    for path in sorted(declarations.glob("*.json")):
        declaration = json.loads(path.read_text())
        payload = declaration["payload"]
        pairs = [pair for pair in payload["allowed_endpoint_pairs"]
                 if "research-inquiry" in (pair["source_kind"], pair["target_kind"])]
        if pairs:
            connections.append({"kind": declaration["node_id"], "source": binding(path),
                                "pairs": pairs, "question": payload["unique_question"]})
    assert len(connections) == 7
    report = {"task": "N01", "unit": "K01", "result": "source-clarification-check-pass",
              "driver": binding(Path(__file__)), "schema": binding(schema_path),
              "witness": binding(witness_path),
              "shared_validator": binding(ROOT / "tooling/validators/artifact_surface.py"),
              "jsonschema_version": importlib.metadata.version("jsonschema"),
              "existing_candidate_inquiry_is_schema_valid_without_improvement_target": True,
              "required_research_boundary_controls": controls,
              "allowed_research_inquiry_relation_families": connections,
              "allowed_family_count": len(connections),
              "ordered_branch_count": sum(len(c["pairs"]) for c in connections),
              "claim_scope": "Current source schema/fixture and declared endpoint compatibility only.",
              "composed_successor_required_obligation_generator_checked": False,
              "actual_K01_owner_assessment": None,
              "inherited_discharges": 0, "authority_effect": "none"}
    (HERE / "clarifications/K01-inquiry-scope-validation.json").write_text(
        json.dumps(report, indent=2) + "\n")
    print(json.dumps({"result": report["result"], "allowed_families": len(connections),
                      "ordered_branches": report["ordered_branch_count"],
                      "required_boundary_refusal_controls": len(controls)}))


if __name__ == "__main__":
    run()

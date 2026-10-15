"""Check K03 source boundaries without accepting a meaning or discharge."""
from pathlib import Path
import copy
import hashlib
import importlib.metadata
import json
import jsonschema

HERE = Path(__file__).resolve().parent
SUCCESSOR = HERE.parents[3]
ROOT = SUCCESSOR.parents[5]


def binding(path):
    return {"path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    context = json.loads((HERE / "context-pack.json").read_text())
    for source in context["selected_sources"]:
        assert binding(ROOT / source["path"])["sha256"] == source["sha256"]
    relation_path = ROOT / "authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/affects.json"
    payload = json.loads(relation_path.read_text())["payload"]
    definition_path = SUCCESSOR / "definitions/K03-affects.json"
    definition = json.loads(definition_path.read_text())
    pairs = payload["allowed_endpoint_pairs"]
    sources = payload["source_kinds"]
    targets = payload["target_kinds"]
    assert len(pairs) == 22 and len(sources) == 2 and len(targets) == 11
    assert pairs == [{"source_kind": s, "target_kind": t} for s in sources for t in targets]
    assert pairs == definition["ordered_pairs"]
    assert len(definition["pending_ids"]) == 7
    contract = payload["qualifier_contract"]
    qualifier_schema = {"type": "object", "additionalProperties": not contract["closed"],
                        "properties": contract["properties"], "required": contract["required_axes"]}
    raw = {"impact_scope": "scope:invented-all-subjects", "evidence_posture": "definitely-observed"}
    assert not list(jsonschema.Draft202012Validator(qualifier_schema).iter_errors(raw))
    probes = []
    bindings = []
    for kind in sources:
        package = ROOT / f"authority/artifact-types/{kind}/v1"
        schema_path, fixture_path = package / "schema.json", package / "fixtures/valid/record.json"
        bindings.extend([binding(schema_path), binding(fixture_path)])
        schema = json.loads(schema_path.read_text())
        fixture = json.loads(fixture_path.read_text())
        validator = jsonschema.Draft202012Validator(schema)
        errors = lambda item: sorted(e.message for e in validator.iter_errors(item))
        assert not errors(fixture)
        operations = [("no-top-level-evidence", lambda d: d.update(evidence_refs=[]), True)]
        if kind == "failure-occurrence":
            operations += [
                ("no-detection-evidence", lambda d: d["payload"].update(detection_evidence_refs=[]), True),
                ("no-observed-manifestations", lambda d: d["payload"].update(observed_manifestations=[]), True),
                ("predicted-occurrence-label", lambda d: d["payload"].update(occurrence_posture="predicted-only"), True),
                ("no-impact-references", lambda d: d["payload"].update(impact_refs=[]), True),
                ("arbitrary-cause-label", lambda d: d["payload"].update(cause_posture="proved-by-label"), True),
                ("missing-subject", lambda d: d["payload"].pop("subject_ref"), False),
            ]
        else:
            operations += [
                ("no-occurrence-references", lambda d: d["payload"].update(occurrence_refs=[]), True),
                ("no-timeline-references", lambda d: d["payload"].update(timeline_refs=[]), True),
                ("arbitrary-impact-summary", lambda d: d["payload"].update(impact_summary="severe because I say so"), True),
                ("no-decision-references", lambda d: d["payload"].update(decision_refs=[]), True),
                ("missing-accountable-principal", lambda d: d["payload"].pop("accountable_principal_ref"), False),
            ]
        for name, operation, expected in operations:
            altered = copy.deepcopy(fixture)
            operation(altered)
            findings = errors(altered)
            assert (not findings) == expected, (kind, name, findings)
            probes.append({"kind": kind, "case": name, "schema_accepts": not findings, "errors": findings})
    report = {"task": "N01", "unit": "K03", "result": "source-boundary-audit-pass",
              "driver": binding(Path(__file__)), "source_relation": binding(relation_path),
              "candidate_definition": binding(definition_path), "context_pack": binding(HERE / "context-pack.json"),
              "source_artifact_bindings": bindings, "declared_pairs": pairs,
              "source_kinds": sources, "target_kinds": targets,
              "jsonschema_version": importlib.metadata.version("jsonschema"), "schema_probes": probes,
              "arbitrary_scope_and_observed_label_pass_raw_qualifier_shape": True,
              "semantic_duties": ["An owned admissible observation must establish exact impact; a label or possibility is insufficient.",
                                  "Resolve scope and posture through the exact independently owned catalog and full frame.",
                                  "An accountable principal is not thereby blamed or made owner of the affected subject.",
                                  "Impact summary/cause posture labels do not constitute causal models or severity assessments."],
              "actual_owner_review": None, "source_semantic_refinement_complete": False,
              "inherited_discharges": 0, "authority_effect": "none"}
    (HERE / "source-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"result": report["result"], "pairs": len(pairs), "source_probes": len(probes)}))


if __name__ == "__main__":
    run()

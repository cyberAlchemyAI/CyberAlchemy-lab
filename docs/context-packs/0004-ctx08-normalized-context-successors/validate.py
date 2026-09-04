#!/usr/bin/env python3
"""Validate CTX08 normalized context and lineage successor candidates."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from render import OUTPUT, SOURCE, render

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    pack = load(SOURCE)
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check(
        "pack-identity",
        pack.get("pack_id") == "CAL-CONTEXT-PACK-CTX08-0001"
        and pack.get("status") == "candidate-unadmitted"
        and pack.get("authority_effect") == "none",
        {"id": pack.get("pack_id"), "status": pack.get("status"), "effect": pack.get("authority_effect")},
    )
    direction = pack["authorship_direction"]
    check(
        "exact-authorship-direction",
        direction.get("instruction") == "author-normalized-governance-and-ontology-lifecycle-successor-context-epochs"
        and direction.get("principal") == "person:<vrondelli>"
        and direction.get("effect") == "candidate-authorship-and-validation-only",
        direction,
    )

    input_results = []
    for item in pack["selected_inputs"]:
        actual = sha(LAB / item["path"])
        input_results.append({"input_id": item["input_id"], "path": item["path"], "expected": item["sha256"], "actual": actual})
    check("selected-input-digest-closure", all(item["expected"] == item["actual"] for item in input_results), input_results)

    decision_ids = {
        "ctx01-lineage-and-language-artifact-type-admission",
        "context-operational-owner-admission",
        "ctx05-successor-admission",
        "ctx07-normalized-artifact-type-admission",
    }
    decision_results = []
    for item in pack["selected_inputs"]:
        if item["input_id"] in decision_ids:
            decision_results.append({"input_id": item["input_id"], "status": load(LAB / item["path"]).get("status")})
    check("prerequisite-decisions-current", len(decision_results) == 4 and all(item["status"] == "owner-admitted" for item in decision_results), decision_results)

    receipt_ids = {"ctx05-successor-admission-validation", "ctx07-normalized-artifact-type-admission-validation"}
    receipt_results = []
    for item in pack["selected_inputs"]:
        if item["input_id"] in receipt_ids:
            record = load(LAB / item["path"])
            receipt_results.append({"input_id": item["input_id"], "result": record.get("result"), "state": record.get("admission_state")})
    check("prerequisite-admission-evidence-pass", len(receipt_results) == 2 and all(item["result"] == "PASS" for item in receipt_results), receipt_results)

    owners = load(LAB / next(item["path"] for item in pack["selected_inputs"] if item["input_id"] == "context-operational-owner-registry"))
    assignments = {item["role_id"]: item for item in owners["role_assignments"]}
    required_roles = set(pack["promotion_gate"]["required_roles"])
    check(
        "owner-roles-current-and-separated",
        required_roles <= set(assignments)
        and all(assignments[role]["principal_id"] == "person:<vrondelli>" and assignments[role]["decision_separation"] == "required" for role in required_roles),
        {role: assignments.get(role) for role in sorted(required_roles)},
    )

    artifacts = {}
    artifact_results = []
    for item in pack["canonical_artifacts"]:
        path = LAB / item["path"]
        projection = LAB / item["projection"]
        artifacts[item["artifact_id"]] = load(path)
        artifact_results.append(
            {
                "artifact_id": item["artifact_id"],
                "machine": sha(path),
                "expected_machine": item["sha256"],
                "projection": sha(projection),
                "expected_projection": item["projection_sha256"],
            }
        )
    check("four-artifact-byte-bindings-current", len(artifact_results) == 4 and all(item["machine"] == item["expected_machine"] and item["projection"] == item["expected_projection"] for item in artifact_results), artifact_results)

    context_schema = load(LAB / "tooling/schemas/ctx07/v2/schema.json")
    lineage_schema = load(LAB / "tooling/schemas/ctx01/v1/schema.json")
    schema_results = []
    for item in pack["canonical_artifacts"]:
        schema_name = "boundedContext" if item["artifact_type_ref"] == "cal.artifact-type.bounded-context/v2" else "contextLineageRecord"
        schema = context_schema if schema_name == "boundedContext" else lineage_schema
        errors = [error.message for error in Draft202012Validator({"$ref": f"#/$defs/{schema_name}", **schema}).iter_errors(artifacts[item["artifact_id"]])]
        schema_results.append({"artifact_id": item["artifact_id"], "errors": errors})
    check("closed-schemas-valid", all(not item["errors"] for item in schema_results), schema_results)
    check("all-candidates-non-effectful", all(item.get("status") == "candidate-unadmitted" and item.get("authority_effect") == "none" for item in artifacts.values()), {key: [value.get("status"), value.get("authority_effect")] for key, value in artifacts.items()})

    gov = artifacts["cal.context.governance/v3"]
    lifecycle = artifacts["cal.context.ontology-lifecycle/v3"]
    contexts = (gov, lifecycle)
    check(
        "normalized-context-identities-and-versions",
        gov["context_id"] == "cal.context.governance"
        and lifecycle["context_id"] == "cal.context.ontology-lifecycle"
        and all(item["version"] == "2.0.0-candidate.1" for item in contexts)
        and all(item["classification"]["artifact_type_ref"] == "cal.artifact-type.bounded-context/v2" for item in contexts),
        {"governance": [gov["context_id"], gov["version"]], "ontology_lifecycle": [lifecycle["context_id"], lifecycle["version"]]},
    )
    forbidden = set(pack["normalization_contract"]["forbidden_endpoint_fields"])
    check(
        "canonical-map-backreferences-absent",
        all(not (forbidden & set(item)) for item in contexts),
        {item["context_id"]: sorted(forbidden & set(item)) for item in contexts},
    )
    required_contracts = {
        "cal.definition.bounded-context@2.0.0-candidate.1",
        "cal.definition.context-map@2.0.0-candidate.1",
        "cal.artifact-type.bounded-context/v2",
        "cal.artifact-type.context-map/v2",
    }
    check("normalized-contract-bindings-current", all(required_contracts <= set(item["contract_refs"]) for item in contexts), {item["context_id"]: item["contract_refs"] for item in contexts})

    predecessors = {
        "cal.context.governance": load(LAB / "contexts/governance/v2/context.json"),
        "cal.context.ontology-lifecycle": load(LAB / "contexts/ontology-lifecycle/v2/context.json"),
    }
    preserved_fields = ("context_id", "domain_model_ref", "semantic_owner_ref", "challenge_route")
    check(
        "semantic-scope-preserved",
        all(
            all(item[field] == predecessors[item["context_id"]][field] for field in preserved_fields)
            and item["scope"]["statement"] == predecessors[item["context_id"]]["scope"]["statement"]
            for item in contexts
        ),
        {item["context_id"]: {field: item[field] for field in preserved_fields} for item in contexts},
    )

    language_results = []
    for item in pack["preserved_languages"]:
        path = LAB / item["path"]
        projection = LAB / item["projection"]
        language = load(path)
        context = gov if item["stable_context_id"] == gov["context_id"] else lifecycle
        language_results.append(
            {
                "language_ref": item["language_ref"],
                "machine": sha(path),
                "expected_machine": item["sha256"],
                "projection": sha(projection),
                "expected_projection": item["projection_sha256"],
                "language_id": language["language_id"],
                "stable_context_from_language": language["bounded_context_ref"].rsplit("/", 1)[0],
                "stable_context_expected": item["stable_context_id"],
                "successor_language_ref": context["ubiquitous_language_ref"],
            }
        )
    check(
        "exact-admitted-languages-preserved",
        all(
            item["machine"] == item["expected_machine"]
            and item["projection"] == item["expected_projection"]
            and item["stable_context_from_language"] == item["stable_context_expected"]
            and item["successor_language_ref"] == item["language_ref"]
            for item in language_results
        ),
        language_results,
    )

    gov_lineage = artifacts["cal.context-lineage.governance.v2-to-v3"]
    lifecycle_lineage = artifacts["cal.context-lineage.ontology-lifecycle.v2-to-v3"]
    lineage_pairs = (
        (gov_lineage, "cal.context.governance/v2", "cal.context.governance/v3"),
        (lifecycle_lineage, "cal.context.ontology-lifecycle/v2", "cal.context.ontology-lifecycle/v3"),
    )
    check(
        "exact-v2-to-v3-lineage-closure",
        all(
            item["predecessor_context_ref"] == predecessor
            and item["successor_context_refs"] == [successor]
            and item["source_version"] == "1.1.0-candidate.1"
            and item["destination_versions"] == ["2.0.0-candidate.1"]
            and item["lineage_kind"] == "successor"
            for item, predecessor, successor in lineage_pairs
        ),
        {item["lineage_record_id"]: [item["predecessor_context_ref"], item["successor_context_refs"]] for item, _, _ in lineage_pairs},
    )
    check(
        "lineage-inference-denied",
        all(item["equivalence_inferred"] is False and item["admission_inferred"] is False and "no successor Context Map" in item["effective_boundary"] for item, _, _ in lineage_pairs),
        {item["lineage_record_id"]: [item["equivalence_inferred"], item["admission_inferred"], item["effective_boundary"]] for item, _, _ in lineage_pairs},
    )

    predecessor_hashes = {
        "contexts/governance/v2/context.json": "5c59ae8dc12807ad8996749a82e1f9b0c1f624b3ef87aaebf4442e957d90d88f",
        "contexts/ontology-lifecycle/v2/context.json": "4a8ef8f3441a055aeed10e368db4bcec7bf6c098e15e2356cfd25d659df3a4b8",
    }
    predecessor_results = [{"path": path, "expected": expected, "actual": sha(LAB / path)} for path, expected in predecessor_hashes.items()]
    check("ctx05-predecessor-contexts-preserved", all(item["expected"] == item["actual"] for item in predecessor_results), predecessor_results)

    context_generator = load_module(LAB / "tooling/generators/ctx07_artifact.py", "ctx08_context_generator")
    lineage_generator = load_module(LAB / "tooling/generators/ctx01_artifact.py", "ctx08_lineage_generator")
    projection_results = []
    for item in pack["canonical_artifacts"]:
        slug = "bounded-context" if item["artifact_type_ref"] == "cal.artifact-type.bounded-context/v2" else "context-lineage-record"
        generator = context_generator if slug == "bounded-context" else lineage_generator
        expected = generator.render_instance(artifacts[item["artifact_id"]], slug)
        projection_results.append({"artifact_id": item["artifact_id"], "parity": (LAB / item["projection"]).read_text(encoding="utf-8") == expected})
    check("deterministic-artifact-projections", all(item["parity"] for item in projection_results), projection_results)
    check("deterministic-pack-projection", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(pack), str(OUTPUT))

    hostile = copy.deepcopy(gov)
    hostile["context_map_refs"] = ["cal.context-map.governance-ontology-lifecycle/v1"]
    hostile_errors = [error.message for error in Draft202012Validator({"$ref": "#/$defs/boundedContext", **context_schema}).iter_errors(hostile)]
    check("hostile-canonical-map-backreference-rejected", bool(hostile_errors), hostile_errors)

    check(
        "no-successor-map-or-migration-material",
        len(pack["canonical_artifacts"]) == 4
        and all(item["artifact_type_ref"] not in {"cal.artifact-type.context-map/v2", "cal.artifact-type.context-migration-manifest/v1"} for item in pack["canonical_artifacts"]),
        [item["artifact_type_ref"] for item in pack["canonical_artifacts"]],
    )
    check(
        "promotion-remains-gated",
        pack["promotion_gate"]["current_state"] == "not_evaluable-until-aggregate-and-conformance-validation-pass-and-owners-select"
        and set(pack["promotion_gate"]["required_roles"]) == required_roles,
        pack["promotion_gate"],
    )
    check(
        "claim-ceiling-preserved",
        all(term in pack["claim_ceiling"] for term in ("does not admit", "Context Map", "migration", "stable-release state")),
        pack["claim_ceiling"],
    )

    failed = [item for item in checks if item["result"] == "FAIL"]
    result = "PASS" if not failed else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-ctx08-normalized-context-successor-validation/v1",
        "subject": pack["pack_id"],
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "current_gate_state": "candidate-ready-for-independent-conformance" if result == "PASS" else "not_evaluable",
        "claim_ceiling": pack["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX08_NORMALIZED_CONTEXT_SUCCESSOR_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"CURRENT_GATE_STATE={receipt['current_gate_state']}")
    for item in failed:
        print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

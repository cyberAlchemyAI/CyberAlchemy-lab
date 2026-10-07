#!/usr/bin/env python3
"""Materialize complete Relation Kind/v2 and Typed Relation/v2 candidates."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
MODEL_PATH = LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json"
EXAMPLES_PATH = LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/examples.json"
RK_V1 = LAB / "authority/artifact-types/relation-kind/v1"
TR_V1 = LAB / "authority/artifact-types/typed-relation/v1"
RK_V2 = LAB / "authority/artifact-types/relation-kind/v2"
TR_V2 = LAB / "authority/artifact-types/typed-relation/v2"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def endpoint_kind(ref: str) -> str:
    if ref.startswith("cal.artifact-type."):
        return "artifact-type"
    if ref.startswith("cal.definition."):
        return "definition"
    if ref.startswith("CA2-PRODUCT-"):
        return "product"
    kind = ref.split(":", 1)[0]
    return "method" if kind == "measurement-method" else kind


def qualifier_value_schema(value: Any) -> dict[str, Any]:
    if isinstance(value, list):
        return {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "string", "minLength": 1}}
    return {"type": "string", "minLength": 1}


def common_properties(schema_version: str, kind: str) -> dict[str, Any]:
    relation_ref = {
        "type": "object",
        "additionalProperties": False,
        "required": ["relation_kind_ref", "direction", "counterpart_kind", "counterpart_ref"],
        "properties": {
            "relation_kind_ref": {"type": "string", "minLength": 1},
            "direction": {"enum": ["source", "target"]},
            "counterpart_kind": {"type": "string", "minLength": 1},
            "counterpart_ref": {"type": "string", "minLength": 1},
        },
    }
    return {
        "schema_version": {"const": schema_version},
        "node_id": {"type": "string", "minLength": 1},
        "kind": {"const": kind},
        "name": {"type": "string", "minLength": 1},
        "lifecycle_state": {"enum": ["candidate", "active", "historical", "retired"]},
        "authority_effect": {"const": "none"},
        "owner_ref": {"type": "string", "minLength": 1},
        "scope_ref": {"type": "string", "minLength": 1},
        "evidence_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
        "challenge_route": {"type": "string", "minLength": 1},
        "successor_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
        "relation_refs": {"type": "array", "items": relation_ref},
        "claim_ceiling": {"type": "string", "minLength": 1},
    }


COMMON_REQUIRED = [
    "schema_version", "node_id", "kind", "name", "lifecycle_state", "authority_effect",
    "owner_ref", "scope_ref", "evidence_refs", "challenge_route", "successor_refs",
    "relation_refs", "payload", "claim_ceiling",
]


def relation_kind_schema() -> dict[str, Any]:
    properties = common_properties("cyberalchemy-lab-relation-kind/v2", "relation-kind")
    properties["payload"] = {
        "type": "object", "additionalProperties": False,
        "required": [
            "relation_kind_id", "axis_id", "predicate", "group", "unique_question",
            "operational_effect", "source_kinds", "target_kinds", "allowed_endpoint_pairs",
            "qualifier_contract", "forbidden_inferences", "absorbed_relation_kinds", "inverse_ref",
        ],
        "properties": {
            "relation_kind_id": {"type": "string", "pattern": "^relation\\.[a-z0-9-]+$"},
            "axis_id": {"type": "string", "pattern": "^axis\\.[a-z0-9-]+$"},
            "predicate": {"type": "string", "pattern": "^[a-z0-9-]+$"},
            "group": {"type": "string", "minLength": 1},
            "unique_question": {"type": "string", "minLength": 1},
            "operational_effect": {"type": "string", "minLength": 1},
            "source_kinds": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "string", "minLength": 1, "not": {"const": "*"}}},
            "target_kinds": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "string", "minLength": 1, "not": {"const": "*"}}},
            "allowed_endpoint_pairs": {
                "type": "array", "minItems": 1, "uniqueItems": True,
                "items": {"type": "object", "additionalProperties": False, "required": ["source_kind", "target_kind"], "properties": {"source_kind": {"type": "string", "minLength": 1, "not": {"const": "*"}}, "target_kind": {"type": "string", "minLength": 1, "not": {"const": "*"}}}},
            },
            "qualifier_contract": {
                "type": "object", "additionalProperties": False,
                "required": ["closed", "required_axes", "properties"],
                "properties": {
                    "closed": {"const": True},
                    "required_axes": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "string", "minLength": 1}},
                    "properties": {"type": "object", "minProperties": 1, "additionalProperties": {"type": "object"}},
                },
            },
            "forbidden_inferences": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "string", "minLength": 1}},
            "absorbed_relation_kinds": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "string", "minLength": 1}},
            "inverse_ref": {"type": ["string", "null"]},
        },
    }
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://cyberalchemy.local/schemas/relation-kind/v2", "type": "object", "additionalProperties": False, "required": COMMON_REQUIRED, "properties": properties}


def typed_relation_schema(entries: list[dict[str, Any]], examples: dict[str, Any]) -> dict[str, Any]:
    relation_ids = [entry["relation_kind_id"] for entry in entries]
    properties = common_properties("cyberalchemy-lab-typed-relation/v2", "typed-relation")
    endpoint = {
        "type": "object", "additionalProperties": False,
        "required": ["kind", "ref", "version_ref"],
        "properties": {"kind": {"type": "string", "minLength": 1, "not": {"const": "*"}}, "ref": {"type": "string", "minLength": 1}, "version_ref": {"type": "string", "minLength": 1}},
    }
    properties["payload"] = {
        "type": "object", "additionalProperties": False,
        "required": ["relation_kind_ref", "source", "target", "qualifiers", "relation_lifecycle_state", "relation_evidence_refs"],
        "properties": {
            "relation_kind_ref": {"enum": relation_ids},
            "source": endpoint,
            "target": endpoint,
            "qualifiers": {"type": "object"},
            "relation_lifecycle_state": {"enum": ["candidate", "active", "historical", "retired"]},
            "relation_evidence_refs": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "string", "minLength": 1}},
        },
    }
    branches = []
    for entry in entries:
        rid = entry["relation_kind_id"]
        value_examples = examples[rid]["qualifiers"]
        qualifier_properties = {axis: qualifier_value_schema(value_examples[axis]) for axis in entry["required_qualifier_axes"]}
        pairs = []
        for pair in entry["allowed_endpoint_pairs"]:
            pairs.append({
                "properties": {
                    "source": {"properties": {"kind": {"const": pair["source_kind"]}}},
                    "target": {"properties": {"kind": {"const": pair["target_kind"]}}},
                }
            })
        branches.append({
            "if": {"properties": {"payload": {"properties": {"relation_kind_ref": {"const": rid}}}}},
            "then": {"properties": {"payload": {"properties": {
                "qualifiers": {"type": "object", "additionalProperties": False, "required": entry["required_qualifier_axes"], "properties": qualifier_properties},
            }, "oneOf": pairs}}},
        })
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://cyberalchemy.local/schemas/typed-relation/v2", "type": "object", "additionalProperties": False, "required": COMMON_REQUIRED, "properties": properties, "allOf": branches}


def artifact_v2(v1_dir: Path, v2_dir: Path, schema: dict[str, Any], semantic_kind: str, purpose: str, checks: list[str]) -> dict[str, Any]:
    v1 = load(v1_dir / "artifact.json")
    item = copy.deepcopy(v1)
    item["artifact_type_ref"] = item["artifact_type_ref"].replace("/v1", "/v2")
    item["version"] = "2.0.0-candidate.1"
    item["schema_ref"] = item["schema_ref"].replace("/v1", "/v2")
    item["status"] = "candidate-unadmitted"
    item["classification"]["lifecycle_posture_ref"] = "candidate:relation-kind-step6-closure/v1"
    item["distinct_validation_purpose"] = purpose
    item["instance_contract"]["instance_discriminator"]["value"] = f"cyberalchemy-lab-{semantic_kind}/v2"
    item["source_direction"] = {"canonical": "artifact.json", "human_projection": "ARTIFACT.md", "projection_policy": "generated-only", "generator_path": str((ROOT / "build.py").relative_to(LAB))}
    item["validation_contract"] = {
        "admission_effect": "none",
        "assessment_scope": "candidate-complete-relation-contract",
        "positive_witness": "fixtures/valid/record.json",
        "negative_witnesses": ["fixtures/invalid/missing-qualifier.json", "fixtures/invalid/extra-qualifier.json", "fixtures/invalid/undeclared-pair.json", "fixtures/invalid/authority.json"],
        "required_checks": checks,
        "validator_path": str((v2_dir / "validate.py").relative_to(LAB)),
    }
    item["candidate_predecessor_contract"] = {"artifact_type_ref": v1["artifact_type_ref"], "path": str((v1_dir / "artifact.json").relative_to(LAB)), "sha256": sha(v1_dir / "artifact.json"), "admission_posture": "candidate-unadmitted-superseded-before-admission"}
    item["claim_ceiling"] = f"This complete candidate {item['name']}/v2 carrier supersedes its unadmitted v1 candidate before admission. PASS proves its exact closed schema and fixtures; it does not admit the type, any {item['name']} instance, consumer, ontology assertion, or runtime."
    item["typed_residue"][0]["missing"] = f"Artifact Type owner admission for this exact {item['name']}/v2 candidate."
    dump(v2_dir / "schema.json", schema)
    item["schema_digest"] = sha(v2_dir / "schema.json")
    dump(v2_dir / "artifact.json", item)
    return item


def wrap(kind: str, node_id: str, name: str, payload: dict[str, Any], evidence: str) -> dict[str, Any]:
    return {
        "schema_version": f"cyberalchemy-lab-{kind}/v2", "node_id": node_id, "kind": kind, "name": name,
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:relation-owner",
        "scope_ref": "scope:integrated-lab-relation-model", "evidence_refs": [evidence],
        "challenge_route": "challenge:relation-governance-review", "successor_refs": [], "relation_refs": [],
        "payload": payload,
        "claim_ceiling": "Candidate example for exact schema and semantic validation only; it creates no admission, authority, connection, inference, or runtime effect.",
    }


def relation_instance(entry: dict[str, Any], example: dict[str, Any]) -> dict[str, Any]:
    qualifier_properties = {axis: qualifier_value_schema(example["qualifiers"][axis]) for axis in entry["required_qualifier_axes"]}
    payload = {
        "relation_kind_id": entry["relation_kind_id"], "axis_id": entry["axis_id"],
        "predicate": entry["relation_kind_id"].removeprefix("relation."), "group": entry["group"],
        "unique_question": entry["unique_question"], "operational_effect": entry["operational_effect"],
        "source_kinds": entry["source_kinds"], "target_kinds": entry["target_kinds"],
        "allowed_endpoint_pairs": entry["allowed_endpoint_pairs"],
        "qualifier_contract": {"closed": True, "required_axes": entry["required_qualifier_axes"], "properties": qualifier_properties},
        "forbidden_inferences": entry["forbidden_inferences"], "absorbed_relation_kinds": entry["absorbed_relation_kinds"],
        "inverse_ref": None,
    }
    return wrap("relation-kind", entry["relation_kind_id"], entry["relation_kind_id"].removeprefix("relation.").replace("-", " ").title(), payload, f"evidence:{entry['relation_kind_id'].removeprefix('relation.')}-model")


def typed_instance(entry: dict[str, Any], example: dict[str, Any]) -> dict[str, Any]:
    source_kind = endpoint_kind(example["source_ref"]); target_kind = endpoint_kind(example["target_ref"])
    payload = {
        "relation_kind_ref": entry["relation_kind_id"],
        "source": {"kind": source_kind, "ref": example["source_ref"], "version_ref": f"{example['source_ref']}@example-revision-1"},
        "target": {"kind": target_kind, "ref": example["target_ref"], "version_ref": f"{example['target_ref']}@example-revision-1"},
        "qualifiers": example["qualifiers"], "relation_lifecycle_state": "candidate",
        "relation_evidence_refs": example["evidence_refs"],
    }
    return wrap("typed-relation", example["relation_id"], f"Example {entry['relation_kind_id']}", payload, example["evidence_refs"][0])


def render_record(record: dict[str, Any]) -> str:
    return "\n".join([
        "<!-- GENERATED FILE: canonical data is record.json. -->", "", f"# {record['name']}", "",
        f"- Identity: `{record['node_id']}`", f"- Kind: `{record['kind']}`", f"- Lifecycle: `{record['lifecycle_state']}`",
        f"- Owner: `{record['owner_ref']}`", f"- Authority effect: `{record['authority_effect']}`", "", "## Payload", "",
        "```json", json.dumps(record["payload"], indent=2, sort_keys=True), "```", "", "## Claim ceiling", "", record["claim_ceiling"], "",
    ])


def write_package_support(package: Path, valid: dict[str, Any], invalids: dict[str, dict[str, Any]]) -> None:
    dump(package / "fixtures/valid/record.json", valid)
    (package / "fixtures/valid/RECORD.md").write_text(render_record(valid), encoding="utf-8")
    for name, value in invalids.items(): dump(package / f"fixtures/invalid/{name}.json", value)
    validate = """#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
TARGET=ROOT.parents[2]/'relation-kinds/candidates/0003-admission-ready-instances/validate.py'
if __name__=='__main__': raise SystemExit(subprocess.run([sys.executable,str(TARGET),'--package',str(ROOT)]).returncode)
"""
    (package / "validate.py").write_text(validate, encoding="utf-8")
    (package / "ARTIFACT.md").write_text("\n".join(["<!-- GENERATED FILE: canonical data is artifact.json. -->", "", f"# {load(package/'artifact.json')['name']}/v2", "", load(package/'artifact.json')["distinct_validation_purpose"], "", "## Claim ceiling", "", load(package/'artifact.json')["claim_ceiling"], ""]), encoding="utf-8")


def main() -> None:
    model = load(MODEL_PATH); examples = load(EXAMPLES_PATH); entries = model["entries"]
    rk_schema = relation_kind_schema(); tr_schema = typed_relation_schema(entries, examples)
    rk_artifact = artifact_v2(RK_V1, RK_V2, rk_schema, "relation-kind", "A Relation Kind/v2 is the complete closed semantic-axis contract: one question, operational effect, exact ordered endpoint pairs, exact qualifier schema, forbidden inferences, and preserved normalization lineage.", ["complete semantic-axis payload", "closed endpoint pairs", "closed qualifier contract", "forbidden inference preservation", "23 instance validation"])
    tr_artifact = artifact_v2(TR_V1, TR_V2, tr_schema, "typed-relation", "A Typed Relation/v2 is one independently identified connection whose selected Relation Kind fixes its exact ordered endpoint-kind pair and its complete, closed qualifier object; both endpoint revisions, evidence, lifecycle, owner, scope, and challenge route remain explicit.", ["known Relation Kind", "exact ordered endpoint pair", "exact qualifier set", "endpoint revision binding", "23 example validation"])

    rk_records = {}; tr_records = {}
    for entry in entries:
        rid = entry["relation_kind_id"]; slug = rid.removeprefix("relation.")
        rk = relation_instance(entry, examples[rid]); tr = typed_instance(entry, examples[rid])
        rk_records[rid] = rk; tr_records[rid] = tr
        dump(ROOT / f"instances/relation-kinds/{slug}.json", rk)
        dump(ROOT / f"instances/typed-relations/{slug}.json", tr)

    rk_valid = rk_records["relation.member-of"]
    tr_valid = tr_records["relation.realizes"]
    rk_missing = copy.deepcopy(rk_valid); del rk_missing["payload"]["unique_question"]
    rk_extra = copy.deepcopy(rk_valid); rk_extra["payload"]["undeclared"] = True
    rk_wild = copy.deepcopy(rk_valid); rk_wild["payload"]["allowed_endpoint_pairs"][0]["source_kind"] = "*"
    rk_authority = copy.deepcopy(rk_valid); rk_authority["authority_effect"] = "admit"
    write_package_support(RK_V2, rk_valid, {"missing-qualifier": rk_missing, "extra-qualifier": rk_extra, "undeclared-pair": rk_wild, "authority": rk_authority})
    tr_missing = copy.deepcopy(tr_valid); del tr_missing["payload"]["qualifiers"]["realization_role"]
    tr_extra = copy.deepcopy(tr_valid); tr_extra["payload"]["qualifiers"]["undeclared_axis"] = "invalid"
    tr_pair = copy.deepcopy(tr_valid); tr_pair["payload"]["source"]["kind"] = "product"
    tr_authority = copy.deepcopy(tr_valid); tr_authority["authority_effect"] = "admit"
    write_package_support(TR_V2, tr_valid, {"missing-qualifier": tr_missing, "extra-qualifier": tr_extra, "undeclared-pair": tr_pair, "authority": tr_authority})

    carrier_postimages = {
        "schema_version": "cyberalchemy-lab-relation-carrier-v2-postimages/v1", "status": "candidate-materialized", "authority_effect": "none",
        "entries": [
            {"artifact_type_id": rk_artifact["artifact_type_id"], "artifact_type_ref": rk_artifact["artifact_type_ref"], "artifact_path": str((RK_V2/"artifact.json").relative_to(LAB)), "artifact_sha256": sha(RK_V2/"artifact.json"), "schema_path": str((RK_V2/"schema.json").relative_to(LAB)), "schema_sha256": sha(RK_V2/"schema.json"), "supersedes_candidate_ref": "cal.artifact-type.relation-kind/v1", "kind": "relation-kind"},
            {"artifact_type_id": tr_artifact["artifact_type_id"], "artifact_type_ref": tr_artifact["artifact_type_ref"], "artifact_path": str((TR_V2/"artifact.json").relative_to(LAB)), "artifact_sha256": sha(TR_V2/"artifact.json"), "schema_path": str((TR_V2/"schema.json").relative_to(LAB)), "schema_sha256": sha(TR_V2/"schema.json"), "supersedes_candidate_ref": "cal.artifact-type.typed-relation/v1", "kind": "typed-relation"},
        ],
    }
    dump(ROOT / "carrier-postimages.json", carrier_postimages)
    dump(ROOT / "relation-kind-instances.json", {"schema_version": "cyberalchemy-lab-relation-kind-instance-set/v2", "status": "candidate-unadmitted", "authority_effect": "none", "count": len(rk_records), "entries": list(rk_records.values())})
    dump(ROOT / "typed-relation-examples.json", {"schema_version": "cyberalchemy-lab-typed-relation-example-set/v2", "status": "candidate-unadmitted", "authority_effect": "none", "count": len(tr_records), "entries": list(tr_records.values())})
    candidate = {
        "schema_version": "cyberalchemy-lab-relation-step6-materialization/v1", "candidate_id": "CAL-RELATION-STEP6-ADMISSION-READY-INSTANCES-0003", "status": "candidate-owner-review-open", "authority_effect": "none",
        "inputs": {"relation_model": str(MODEL_PATH.relative_to(LAB)), "examples": str(EXAMPLES_PATH.relative_to(LAB)), "relation_kind_v1": str((RK_V1/"artifact.json").relative_to(LAB)), "typed_relation_v1": str((TR_V1/"artifact.json").relative_to(LAB))},
        "outputs": {"carrier_postimages": str((ROOT/"carrier-postimages.json").relative_to(LAB)), "relation_kind_instances": str((ROOT/"relation-kind-instances.json").relative_to(LAB)), "typed_relation_examples": str((ROOT/"typed-relation-examples.json").relative_to(LAB))},
        "counts": {"relation_kinds": 23, "typed_relation_examples": 23, "exact_endpoint_pairs": 147, "carrier_v2_candidates": 2},
        "claim_ceiling": "This materializes complete candidate carriers and candidate examples. It admits no Artifact Type, Relation Kind, Typed Relation, endpoint pair, ontology assertion, consumer, or runtime.",
    }
    dump(ROOT / "candidate.json", candidate)
    lines = ["<!-- GENERATED FILE: canonical data is relation-kind-instances.json and typed-relation-examples.json. -->", "", "# Step 6 relation contract materialization", "", "- Relation Kinds: `23`", "- Exact ordered endpoint pairs: `147`", "- Typed Relation examples: `23`", "- Wildcards: `0`", "- Authority effect: `none`", "", "## Complete model", ""]
    for entry in entries:
        rid=entry["relation_kind_id"]; ex=tr_records[rid]["payload"]
        lines += [f"### `{rid}`", "", entry["unique_question"], "", f"Required qualifiers: `{', '.join(entry['required_qualifier_axes'])}`", "", "Example:", "", "```json", json.dumps(ex, indent=2, sort_keys=True), "```", ""]
    lines += ["## Claim ceiling", "", candidate["claim_ceiling"], ""]
    (ROOT / "RELATION-KINDS.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

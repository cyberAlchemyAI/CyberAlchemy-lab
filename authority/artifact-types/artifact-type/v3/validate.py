#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def load(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path: Path, value) -> None: path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    artifact = load(ROOT / "artifact.json"); schema = load(ROOT / "schema.json")
    registry = load(LAB / "authority/artifact-types/candidates/0008-registry-snapshot-0002/registry.json")
    definitions = load(LAB / "authority/definitions/registry.json")
    model = load(LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json")
    checks = []
    def check(cid, ok, detail): checks.append({"check_id": cid, "result": "PASS" if ok else "BLOCK", "detail": detail})
    errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(artifact)]
    check("closed-v3-self-schema", schema.get("additionalProperties") is False and not errors and artifact["schema_digest"] == sha(ROOT / "schema.json"), errors)
    predecessor = artifact["predecessor_contract"]
    admitted = next(row for row in registry["admitted_contracts"] if row["artifact_type_ref"] == predecessor["artifact_type_ref"])
    check("exact-v2-predecessor", admitted["artifact_path"] == predecessor["path"] and admitted["artifact_sha256"] == predecessor["sha256"] == sha(LAB / predecessor["path"]), predecessor)
    binding = artifact["semantic_definition_bindings"][0]; did = binding["definition_ref"].split("@", 1)[0]
    check("current-artifact-type-definition", definitions["current_lookup"].get(did) == binding["definition_ref"] and sha(LAB / binding["path"]) == binding["sha256"], binding)
    expected_roles=[]
    for relation in model["entries"]:
        outgoing=sorted({p["target_kind"] for p in relation["allowed_endpoint_pairs"] if p["source_kind"]=="artifact-type"}); incoming=sorted({p["source_kind"] for p in relation["allowed_endpoint_pairs"] if p["target_kind"]=="artifact-type"})
        if outgoing: expected_roles.append({"relation_kind_ref":relation["relation_kind_id"],"direction":"source","counterpart_kinds":outgoing})
        if incoming: expected_roles.append({"relation_kind_ref":relation["relation_kind_id"],"direction":"target","counterpart_kinds":incoming})
    expected_roles=sorted(expected_roles,key=lambda r:(r["relation_kind_ref"],r["direction"]))
    check("closed-relation-surface", artifact["relation_roles"] == expected_roles and artifact["allowed_relation_kinds"] == sorted({r["relation_kind_ref"] for r in expected_roles}), expected_roles)
    hostile=[]
    for relative in artifact["validation_contract"]["negative_witnesses"]:
        found=[error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(load(ROOT/relative))]; hostile.append({"path":relative,"rejected":bool(found),"errors":found})
    check("four-hostile-rejections", len(hostile)==4 and all(row["rejected"] for row in hostile), hostile)
    check("bounded-self-application", artifact["self_application"]["mode"]=="bounded-successor-self-description" and artifact["registered_types"][0]["artifact_type_ref"]==artifact["artifact_type_ref"] and artifact["registered_types"][0]["schema_sha256"]==artifact["schema_digest"], artifact["self_application"])
    generator = LAB / artifact["source_direction"]["shared_generator_path"]
    spec=importlib.util.spec_from_file_location("successor_generator",generator); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
    check("deterministic-projections", artifact["source_direction"]["shared_generator_sha256"]==sha(generator) and (ROOT/"ARTIFACT.md").read_text()==module.render_artifact(artifact) and (ROOT/artifact["validation_contract"]["positive_projection"]).read_text()==module.render_instance(artifact,artifact), {"artifact":sha(ROOT/"ARTIFACT.md"),"self_witness":sha(ROOT/artifact["validation_contract"]["positive_projection"])})
    check("candidate-no-effect", artifact["status"]=="candidate-unadmitted" and artifact["authority_effect"]=="none", {"status":artifact["status"],"authority_effect":artifact["authority_effect"]})
    result="PASS" if all(row["result"]=="PASS" for row in checks) else "BLOCK"
    receipt={"schema_version":"cyberalchemy-lab-artifact-type-v3-validation/v1","subject":artifact["artifact_type_ref"],"result":result,"authority_effect":"none","checks":checks,"materials":{"artifact_sha256":sha(ROOT/"artifact.json"),"schema_sha256":sha(ROOT/"schema.json")},"claim_ceiling":"PASS proves the exact candidate v3 self-schema, admitted v2 predecessor, Definition, relation surface, hostile cases, bounded self-application, and projections. It does not admit v3 or any other type or instance, transition v2, or activate a consumer."}
    dump(ROOT/"receipts/validation.json",receipt); print(json.dumps({"subject":artifact["artifact_type_ref"],"result":result,"checks":len(checks)},sort_keys=True)); return 0 if result=="PASS" else 1


if __name__ == "__main__": raise SystemExit(main())

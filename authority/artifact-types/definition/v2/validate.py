#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import jsonschema


ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[3]
def load(path:Path): return json.loads(path.read_text(encoding="utf-8"))
def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path:Path,value)->None: path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")


def main()->int:
    artifact=load(ROOT/"artifact.json");schema=load(ROOT/"schema.json");witness=load(ROOT/artifact["validation_contract"]["positive_witness"])
    registry=load(LAB/"authority/artifact-types/candidates/0008-registry-snapshot-0002/registry.json");definitions=load(LAB/"authority/definitions/registry.json");model=load(LAB/"authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json")
    checks=[]
    def check(cid,ok,detail): checks.append({"check_id":cid,"result":"PASS" if ok else "BLOCK","detail":detail})
    predecessor=artifact["predecessor_contract"];admitted=next(row for row in registry["admitted_contracts"] if row["artifact_type_ref"]==predecessor["artifact_type_ref"])
    check("exact-definition-v1-predecessor",admitted["artifact_path"]==predecessor["path"] and admitted["artifact_sha256"]==predecessor["sha256"]==sha(LAB/predecessor["path"]),predecessor)
    binding=artifact["semantic_definition_bindings"][0];did=binding["definition_ref"].split("@",1)[0]
    check("current-definition-definition",definitions["current_lookup"].get(did)==binding["definition_ref"] and sha(LAB/binding["path"])==binding["sha256"],binding)
    errors=[error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(witness)]
    check("closed-v2-schema-positive",schema.get("additionalProperties") is False and not errors and artifact["schema_digest"]==witness["schema_digest"]==sha(ROOT/"schema.json"),errors)
    expected_ids=[row["relation_kind_id"] for row in model["entries"]]
    actual_ids=schema["$defs"]["typedRelation"]["properties"]["relation_kind_ref"]["enum"]
    check("23-kind-closed-vocabulary",actual_ids==expected_ids and len(actual_ids)==23 and all("*" not in item for item in actual_ids),actual_ids)
    hostile=[]
    for relative in artifact["validation_contract"]["negative_witnesses"]:
        found=[error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(load(ROOT/relative))];hostile.append({"path":relative,"rejected":bool(found),"errors":found})
    check("four-hostile-rejections",len(hostile)==4 and all(row["rejected"] for row in hostile),hostile)
    generator=ROOT/"generator.py";spec=importlib.util.spec_from_file_location("definition_generator",generator);module=importlib.util.module_from_spec(spec);assert spec and spec.loader;spec.loader.exec_module(module)
    check("definition-projection-parity",witness["source_direction"]["generator_sha256"]==sha(generator) and (ROOT/artifact["validation_contract"]["positive_projection"]).read_text()==module.render(witness),{"generator":sha(generator),"projection":sha(ROOT/artifact["validation_contract"]["positive_projection"])})
    successor_generator=LAB/artifact["source_direction"]["shared_generator_path"];spec2=importlib.util.spec_from_file_location("successor_generator",successor_generator);module2=importlib.util.module_from_spec(spec2);assert spec2 and spec2.loader;spec2.loader.exec_module(module2)
    check("artifact-projection-parity",artifact["source_direction"]["shared_generator_sha256"]==sha(successor_generator) and (ROOT/"ARTIFACT.md").read_text()==module2.render_artifact(artifact),sha(ROOT/"ARTIFACT.md"))
    check("candidate-no-effect",artifact["status"]=="candidate-unadmitted" and artifact["authority_effect"]=="none",{"status":artifact["status"],"authority_effect":artifact["authority_effect"]})
    result="PASS" if all(row["result"]=="PASS" for row in checks) else "BLOCK"
    receipt={"schema_version":"cyberalchemy-lab-definition-v2-validation/v1","subject":artifact["artifact_type_ref"],"result":result,"authority_effect":"none","checks":checks,"materials":{"artifact_sha256":sha(ROOT/"artifact.json"),"schema_sha256":sha(ROOT/"schema.json"),"positive_witness_sha256":sha(ROOT/artifact["validation_contract"]["positive_witness"])},"claim_ceiling":"PASS proves the exact Definition/v2 candidate successor, v1 predecessor, Definition binding, closed schema, 23-kind relation vocabulary, hostile cases, and projections. It does not admit v2, transition v1, migrate Definitions, admit relations, or activate consumers."}
    dump(ROOT/"receipts/validation.json",receipt);print(json.dumps({"subject":artifact["artifact_type_ref"],"result":result,"checks":len(checks)},sort_keys=True));return 0 if result=="PASS" else 1


if __name__=="__main__":raise SystemExit(main())

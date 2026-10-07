#!/usr/bin/env python3
"""Validate complete v2 relation carriers and all 23 candidate instances."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
RK = LAB / "authority/artifact-types/relation-kind/v2"
TR = LAB / "authority/artifact-types/typed-relation/v2"


def load(path: Path) -> Any: return json.loads(path.read_text(encoding="utf-8"))
def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path: Path, value: Any) -> None: path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_package(package: Path) -> int:
    schema = load(package / "schema.json"); artifact = load(package / "artifact.json"); valid = load(package / "fixtures/valid/record.json")
    validator = jsonschema.Draft202012Validator(schema); checks=[]
    def check(cid: str, ok: bool, detail: Any) -> None: checks.append({"check_id": cid, "result": "PASS" if ok else "BLOCK", "detail": detail})
    valid_errors = [e.message for e in validator.iter_errors(valid)]
    check("valid-fixture-accepted", not valid_errors, valid_errors)
    negative=[]
    for path in sorted((package / "fixtures/invalid").glob("*.json")):
        errors=[e.message for e in validator.iter_errors(load(path))]
        negative.append({"path": str(path.relative_to(package)), "rejected": bool(errors), "errors": errors})
    check("four-hostile-fixtures-rejected", len(negative)==4 and all(x["rejected"] for x in negative), negative)
    check("closed-schema", schema.get("additionalProperties") is False and schema["properties"]["payload"].get("additionalProperties") is False, {"top": schema.get("additionalProperties"), "payload": schema["properties"]["payload"].get("additionalProperties")})
    check("artifact-binds-schema", artifact["schema_digest"]==sha(package/"schema.json") and artifact["status"]=="candidate-unadmitted" and artifact["authority_effect"]=="none", {"artifact_type_ref": artifact["artifact_type_ref"], "schema_digest": artifact["schema_digest"]})
    predecessor=artifact.get("candidate_predecessor_contract",{}); predecessor_path=LAB/predecessor.get("path","")
    check("unadmitted-v1-predecessor-preserved", predecessor.get("admission_posture")=="candidate-unadmitted-superseded-before-admission" and predecessor_path.is_file() and sha(predecessor_path)==predecessor.get("sha256"), predecessor)
    projection=(package/"fixtures/valid/RECORD.md").read_text(encoding="utf-8")
    check("projection-current", json.dumps(valid["payload"],indent=2,sort_keys=True) in projection and valid["node_id"] in projection, {"projection": "fixtures/valid/RECORD.md"})
    result="PASS" if all(x["result"]=="PASS" for x in checks) else "BLOCK"
    receipt={"schema_version":"cyberalchemy-lab-relation-carrier-v2-validation/v1","artifact_type_ref":artifact["artifact_type_ref"],"result":result,"authority_effect":"none","checks":checks,"materials":{"artifact_sha256":sha(package/"artifact.json"),"schema_sha256":sha(package/"schema.json"),"fixture_sha256":sha(package/"fixtures/valid/record.json")},"claim_ceiling":"PASS proves this candidate carrier's exact schema, fixtures, preserved v1 bytes, and projection. It does not admit the carrier or any instance."}
    dump(package/"receipts/validation.json",receipt)
    print(json.dumps({"artifact_type_ref":artifact["artifact_type_ref"],"result":result,"checks":len(checks)},sort_keys=True))
    return 0 if result=="PASS" else 1


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--package",type=Path); args=parser.parse_args()
    if args.package: return validate_package(args.package.resolve())
    subprocess.run([sys.executable,str(ROOT/"build.py")],check=True)
    rk_code=validate_package(RK); tr_code=validate_package(TR)
    model=load(LAB/"authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json")
    examples=load(LAB/"authority/relation-kinds/candidates/0002-axis-orthogonal-model/examples.json")
    rk_set=load(ROOT/"relation-kind-instances.json"); tr_set=load(ROOT/"typed-relation-examples.json")
    rk_schema=load(RK/"schema.json"); tr_schema=load(TR/"schema.json")
    checks=[]
    def check(cid: str, ok: bool, detail: Any) -> None: checks.append({"check_id":cid,"result":"PASS" if ok else "BLOCK","detail":detail})
    rk_errors=[]
    for row in rk_set["entries"]:
        errors=[e.message for e in jsonschema.Draft202012Validator(rk_schema).iter_errors(row)]
        rk_errors.append({"relation_kind":row["payload"]["relation_kind_id"],"errors":errors})
    check("all-23-relation-kind-instances-valid",len(rk_errors)==23 and all(not x["errors"] for x in rk_errors),rk_errors)
    tr_errors=[]
    for row in tr_set["entries"]:
        errors=[e.message for e in jsonschema.Draft202012Validator(tr_schema).iter_errors(row)]
        tr_errors.append({"relation_kind":row["payload"]["relation_kind_ref"],"errors":errors})
    check("all-23-typed-relation-examples-valid",len(tr_errors)==23 and all(not x["errors"] for x in tr_errors),tr_errors)
    by_id={x["payload"]["relation_kind_id"]:x for x in rk_set["entries"]}
    semantic=[]
    for entry in model["entries"]:
        payload=by_id[entry["relation_kind_id"]]["payload"]
        semantic.append({"relation_kind":entry["relation_kind_id"],"question":payload["unique_question"]==entry["unique_question"],"effect":payload["operational_effect"]==entry["operational_effect"],"pairs":payload["allowed_endpoint_pairs"]==entry["allowed_endpoint_pairs"],"qualifiers":payload["qualifier_contract"]["required_axes"]==entry["required_qualifier_axes"],"forbidden":payload["forbidden_inferences"]==entry["forbidden_inferences"],"lineage":payload["absorbed_relation_kinds"]==entry["absorbed_relation_kinds"]})
    check("full-v1-model-semantics-retained",all(all(v for k,v in x.items() if k!="relation_kind") for x in semantic),semantic)
    pair_count=sum(len(x["payload"]["allowed_endpoint_pairs"]) for x in rk_set["entries"])
    check("closed-147-pair-universe",pair_count==147 and all("*" not in (p["source_kind"],p["target_kind"]) for x in rk_set["entries"] for p in x["payload"]["allowed_endpoint_pairs"]),{"pairs":pair_count,"wildcards":0})
    hostile=[]
    base=tr_set["entries"][0]
    for mutation in ["missing-qualifier","extra-qualifier","swapped-pair","unknown-kind","authority"]:
        row=json.loads(json.dumps(base)); payload=row["payload"]
        if mutation=="missing-qualifier": payload["qualifiers"].pop(next(iter(payload["qualifiers"])))
        elif mutation=="extra-qualifier": payload["qualifiers"]["undeclared_axis"]="invalid"
        elif mutation=="swapped-pair": payload["source"],payload["target"]=payload["target"],payload["source"]
        elif mutation=="unknown-kind": payload["relation_kind_ref"]="relation.unknown"
        else: row["authority_effect"]="admit"
        errors=[e.message for e in jsonschema.Draft202012Validator(tr_schema).iter_errors(row)]
        hostile.append({"case":mutation,"rejected":bool(errors),"errors":errors})
    check("typed-vector-hostile-rejections",all(x["rejected"] for x in hostile),hostile)
    no_collapse=load(LAB/"authority/relation-kinds/candidates/0002-axis-orthogonal-model/receipts/no-collapse.json")
    check("ten-no-collapse-cases-preserved",no_collapse["result"]=="PASS" and len(no_collapse["cases"])==10,no_collapse["cases"])
    carrier=load(ROOT/"carrier-postimages.json")
    receipts=[]
    for row in carrier["entries"]:
        package=(LAB/row["artifact_path"]).parent; receipt=load(package/"receipts/validation.json")
        receipts.append({"ref":row["artifact_type_ref"],"artifact":sha(LAB/row["artifact_path"])==row["artifact_sha256"],"schema":sha(LAB/row["schema_path"])==row["schema_sha256"],"receipt_pass":receipt["result"]=="PASS"})
    check("two-v2-carrier-postimages-current",rk_code==tr_code==0 and len(receipts)==2 and all(all(v for k,v in x.items() if k!="ref") for x in receipts),receipts)
    check("candidate-no-authority-effect",rk_set["authority_effect"]==tr_set["authority_effect"]==carrier["authority_effect"]=="none",{"relation_kinds":rk_set["authority_effect"],"typed_relations":tr_set["authority_effect"]})
    before=[(ROOT/x).read_bytes() for x in ["candidate.json","carrier-postimages.json","relation-kind-instances.json","typed-relation-examples.json","RELATION-KINDS.md"]]
    subprocess.run([sys.executable,str(ROOT/"build.py")],check=True)
    after=[(ROOT/x).read_bytes() for x in ["candidate.json","carrier-postimages.json","relation-kind-instances.json","typed-relation-examples.json","RELATION-KINDS.md"]]
    check("deterministic-materialization",before==after,{"relation_kinds_sha256":sha(ROOT/"relation-kind-instances.json"),"typed_relations_sha256":sha(ROOT/"typed-relation-examples.json"),"carrier_postimages_sha256":sha(ROOT/"carrier-postimages.json")})
    result="PASS" if all(x["result"]=="PASS" for x in checks) else "BLOCK"
    receipt={"schema_version":"cyberalchemy-lab-relation-step6-materialization-validation/v1","result":result,"authority_effect":"none","checks":checks,"materials":{"candidate_sha256":sha(ROOT/"candidate.json"),"carrier_postimages_sha256":sha(ROOT/"carrier-postimages.json"),"relation_kind_instances_sha256":sha(ROOT/"relation-kind-instances.json"),"typed_relation_examples_sha256":sha(ROOT/"typed-relation-examples.json"),"review_sha256":sha(ROOT/"RELATION-KINDS.md")},"claim_ceiling":"PASS proves two complete candidate carrier schemas, 23 candidate Relation Kind instances, 23 schema-valid candidate Typed Relation examples, 147 exact ordered pairs, closed qualifiers, and tested hostile rejection. It admits and activates nothing."}
    dump(ROOT/"receipts/validation.json",receipt)
    print(json.dumps({"result":result,"checks":len(checks),**receipt["materials"]},sort_keys=True))
    return 0 if result=="PASS" else 1


if __name__=="__main__": raise SystemExit(main())

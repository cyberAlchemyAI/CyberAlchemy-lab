#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[3]
def load(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def main():
 subprocess.run([sys.executable,str(ROOT/"build.py")],check=True);m=load(ROOT/"admission-manifest.json");schema=load(LAB/"authority/artifact-types/relation-kind/v2/schema.json");checks=[]
 def ck(i,o,d):checks.append({"check_id":i,"result":"PASS" if o else "BLOCK","detail":d})
 ck("exact-counts",m["counts"]=={"relation_kinds_to_admit":23,"exact_endpoint_pairs_to_admit":147,"typed_relations_to_admit":0,"artifact_types_to_admit":0,"ontology_assertions_to_admit":0,"consumer_activations":0,"runtime_activations":0},m["counts"])
 records=[]
 for x in m["entries"]:
  p=LAB/x["record_path"];record=load(p);errors=[e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(record)];records.append({"ref":x["relation_kind_ref"],"digest":sha(p)==x["record_sha256"],"schema_valid":not errors,"identity":record["payload"]["relation_kind_id"]==x["relation_kind_ref"],"qualifiers":record["payload"]["qualifier_contract"]["required_axes"]==x["required_qualifier_axes"],"pairs":len(record["payload"]["allowed_endpoint_pairs"])==x["exact_endpoint_pair_count"],"errors":errors})
 ck("23-exact-schema-valid-records",len(records)==23 and all(all(v for k,v in x.items() if k not in {"ref","errors"}) for x in records),records)
 ck("unique-identities-and-bytes",len({x["relation_kind_ref"] for x in m["entries"]})==len({x["record_sha256"] for x in m["entries"]})==23,{"identities":len({x["relation_kind_ref"] for x in m["entries"]}),"digests":len({x["record_sha256"] for x in m["entries"]})})
 ck("extension-rule-admitted",m["prerequisites"][0]["state"]=="satisfied" and m["prerequisites"][0]["definition_current"] is True,m["prerequisites"][0])
 required={x["artifact_type_ref"] for x in m["prerequisites"][1]["required_carriers"]};ck("v2-carriers-exact-and-pending-0069",required=={"cal.artifact-type.relation-kind/v2","cal.artifact-type.typed-relation/v2"} and m["prerequisites"][1]["state"]=="pending-owner-authorization",m["prerequisites"][1])
 ck("zero-out-of-scope-effects",all(m["counts"][k]==0 for k in ["typed_relations_to_admit","artifact_types_to_admit","ontology_assertions_to_admit","consumer_activations","runtime_activations"]) and m["authority_effect"]=="none",m["counts"])
 before=(ROOT/"ADMISSION-REVIEW.md").read_bytes();subprocess.run([sys.executable,str(ROOT/"build.py")],check=True);ck("deterministic-review",before==(ROOT/"ADMISSION-REVIEW.md").read_bytes(),{"manifest_sha256":sha(ROOT/"admission-manifest.json"),"review_sha256":sha(ROOT/"ADMISSION-REVIEW.md")})
 result="PASS" if all(x["result"]=="PASS" for x in checks) else "BLOCK";receipt={"schema_version":"cyberalchemy-lab-relation-kind-admission-review-validation/v1","result":result,"authority_effect":"none","checks":checks,"materials":{"manifest_sha256":sha(ROOT/"admission-manifest.json"),"review_sha256":sha(ROOT/"ADMISSION-REVIEW.md")},"claim_ceiling":"PASS proves the exact 23-record review set and its dependency gate. It does not authorize or apply admission."};dump(ROOT/"receipts/validation.json",receipt);print(json.dumps({"result":result,"checks":len(checks),**receipt["materials"]},sort_keys=True));return 0 if result=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())

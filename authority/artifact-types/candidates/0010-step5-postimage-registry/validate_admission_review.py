#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[3]
def load(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def main():
 subprocess.run([sys.executable,str(ROOT/"build_admission_review.py")],check=True);m=load(ROOT/"admission-manifest.json");r=load(ROOT/"registry.json");defs=load(LAB/"authority/definitions/registry.json");checks=[]
 def check(i,o,d):checks.append({"check_id":i,"result":"PASS" if o else "BLOCK","detail":d})
 check("exact-group-counts",m["counts"]["artifact_types_to_admit"]==53 and m["counts"]["existing-ready-candidate"]==17 and m["counts"]["repaired-candidate"]==5 and m["counts"]["immutable-successor"]==9 and m["counts"]["new-endpoint-carrier"]==22,m["counts"])
 check("eight-exclusions",len(m["excluded_candidate_records"])==8 and sum(x["reason"]=="candidate-lineage-predecessor-preserved" for x in m["excluded_candidate_records"])==3 and sum(x["reason"]=="superseded-before-admission" for x in m["excluded_candidate_records"])==2,m["excluded_candidate_records"])
 byte_results=[]
 for e in m["entries"]:byte_results.append({"ref":e["artifact_type_ref"],"artifact":sha(LAB/e["artifact_path"])==e["artifact_sha256"],"schema":sha(LAB/e["schema_path"])==e["schema_sha256"],"receipt":sha(LAB/e["receipt_path"])==e["receipt_sha256"] and load(LAB/e["receipt_path"])["result"]=="PASS"})
 check("all-exact-bytes-and-receipts",len(byte_results)==53 and all(all(v for k,v in x.items() if k!="ref") for x in byte_results),byte_results)
 definition_results=[]
 for e in m["entries"]:
  for ref in e["semantic_definition_refs"]:definition_results.append({"ref":e["artifact_type_ref"],"definition":ref,"current":defs["current_lookup"].get(ref.split("@",1)[0])==ref})
 check("all-definitions-current",all(x["current"] for x in definition_results),definition_results)
 successors=[e for e in m["entries"] if e["admission_action"]=="successor-current"]
 check("nine-exact-successors",len(successors)==9 and all(e["predecessor_contract"] and r["current_by_identity"].get(e["artifact_type_id"])==e["predecessor_contract"]["artifact_type_ref"] for e in successors),[(e["artifact_type_ref"],e["predecessor_contract"]["artifact_type_ref"]) for e in successors])
 check("zero-out-of-scope-effects",all(m["counts"][k]==0 for k in ["instance_admissions","relation_kind_admissions","typed_relation_admissions","consumer_activations"]) and m["authority_effect"]=="none",m["counts"])
 before=(ROOT/"ADMISSION-REVIEW.md").read_bytes();subprocess.run([sys.executable,str(ROOT/"build_admission_review.py")],check=True);check("deterministic-review",before==(ROOT/"ADMISSION-REVIEW.md").read_bytes(),{"manifest_sha256":sha(ROOT/"admission-manifest.json"),"projection_sha256":sha(ROOT/"ADMISSION-REVIEW.md")})
 result="PASS" if all(x["result"]=="PASS" for x in checks) else "BLOCK";receipt={"schema_version":"cyberalchemy-lab-collective-artifact-type-admission-review-validation/v1","result":result,"authority_effect":"none","checks":checks,"materials":{"manifest_sha256":sha(ROOT/"admission-manifest.json"),"projection_sha256":sha(ROOT/"ADMISSION-REVIEW.md")},"claim_ceiling":"PASS proves the exact 53-entry review manifest, nine predecessor transitions, eight exclusions, byte bindings, current Definitions, passing receipts, deterministic projection, and zero out-of-scope effects. It does not admit the reviewed bytes."};dump(ROOT/"receipts/admission-review-validation.json",receipt);print(json.dumps({"result":result,"checks":len(checks),**receipt["materials"]},sort_keys=True));return 0 if result=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())

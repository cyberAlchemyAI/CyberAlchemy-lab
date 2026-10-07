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
 subprocess.run([sys.executable,str(ROOT/"build.py")],check=True);p=load(ROOT/"proposal.json");r=load(ROOT/"registry-postimage.json");e=load(ROOT/"endpoint-inventory-postimage.json");m=load(LAB/p["review_manifest"]["path"]);schema=load(LAB/"authority/artifact-types/candidates/0006-effective-state-registry/schema.json");checks=[]
 def check(i,o,d):checks.append({"check_id":i,"result":"PASS" if o else "BLOCK","detail":d})
 errors=[x.message for x in jsonschema.Draft202012Validator(schema).iter_errors(r)];check("registry-v2-schema",not errors,errors)
 expected={"admitted_contract_count":87,"admitted_current_count":73,"admitted_historical_count":14,"descriptor_count":90,"descriptor_declared_ref_count":83,"descriptor_identity_count":68,"descriptor_resolved_ref_count":85,"duplicate_resolution_count":2,"semantic_binding_counts":{"admitted-successor-required":0,"candidate-rebind-required":0,"current-as-declared":90},"state_counts":{"admitted-current":66,"admitted-historical":14,"candidate-unadmitted":8,"resolved-duplicate":2}};check("exact-postimage-cardinality",r["inventory"]==expected,r["inventory"])
 check("53-exact-admissions",sum(x["admission_decision_ref"]==p["decision_id"] for x in r["admitted_contracts"])==53 and m["counts"]["artifact_types_to_admit"]==53,p["proposed_effects"])
 check("nine-historical-transitions",p["proposed_effects"]["predecessors_transitioned_to_historical"]==9 and r["inventory"]["admitted_historical_count"]==14,p["proposed_effects"])
 check("eight-candidates-remain",r["inventory"]["state_counts"]["candidate-unadmitted"]==len(m["excluded_candidate_records"])==8,m["excluded_candidate_records"])
 check("all-50-endpoint-carriers-current",e["counts"]=={"admitted-current":50,"candidate-materialized":0,"declared_endpoint_pairs":147,"named_endpoint_kinds":50,"referenced-no-canonical-carrier":0,"wildcard_tokens":0},e["counts"])
 check("zero-out-of-scope-effects",all(p["proposed_effects"][k]==0 for k in ["ordinary_instances_admitted","relation_kinds_admitted","typed_relations_admitted","consumer_activations","runtime_activations"]) and p["authority_effect"]=="none" and p["authorization_present"] is False,p["proposed_effects"])
 check("exact-material-digests",p["review_manifest"]["sha256"]==sha(LAB/p["review_manifest"]["path"]) and p["proposed_postimages"]["registry"]["sha256"]==sha(ROOT/"registry-postimage.json") and p["proposed_postimages"]["endpoint_inventory"]["sha256"]==sha(ROOT/"endpoint-inventory-postimage.json"),p["proposed_postimages"])
 before=[(ROOT/x).read_bytes() for x in ["proposal.json","registry-postimage.json","endpoint-inventory-postimage.json","PROPOSAL.md"]];subprocess.run([sys.executable,str(ROOT/"build.py")],check=True);after=[(ROOT/x).read_bytes() for x in ["proposal.json","registry-postimage.json","endpoint-inventory-postimage.json","PROPOSAL.md"]];check("deterministic-proposal",before==after,{"proposal_sha256":sha(ROOT/"proposal.json"),"registry_sha256":sha(ROOT/"registry-postimage.json"),"endpoint_sha256":sha(ROOT/"endpoint-inventory-postimage.json")})
 result="PASS" if all(x["result"]=="PASS" for x in checks) else "BLOCK";receipt={"schema_version":"cyberalchemy-lab-complete-artifact-type-model-admission-proposal-validation/v1","result":result,"authority_effect":"none","checks":checks,"materials":{"proposal_sha256":sha(ROOT/"proposal.json"),"registry_postimage_sha256":sha(ROOT/"registry-postimage.json"),"endpoint_postimage_sha256":sha(ROOT/"endpoint-inventory-postimage.json")},"claim_ceiling":"PASS proves the proposed Decision 0069 transaction and deterministic postimages. It does not authorize or apply the decision."};dump(ROOT/"validation.json",receipt);print(json.dumps({"result":result,"checks":len(checks),**receipt["materials"]},sort_keys=True));return 0 if result=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())

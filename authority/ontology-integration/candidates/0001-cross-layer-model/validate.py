#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[3]
def load(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def main():
 subprocess.run([sys.executable,str(ROOT/"build.py")],check=True);m=load(ROOT/"integration-model.json");checks=[]
 def ck(i,o,d):checks.append({"check_id":i,"result":"PASS" if o else "BLOCK","detail":d})
 ck("exact-model-counts",m["counts"]=={"layers":8,"cross_layer_mappings":7,"identity_and_lifecycle_invariants":8,"admission_and_effect_laws":9,"relation_namespaces":3,"global_relation_kinds":23,"business_relationship_terms":21,"business_relationship_entries":24,"domainspec_relationship_terms":25,"domainspec_relationship_signatures":28,"relation_token_collisions":1,"non_collapse_cases":12,"gaps":10,"artifact_type_actions":7},m["counts"])
 evidence=[]
 for key in ["architecture","lifecycle"]:
  x=m["selected_foundations"][key];p=LAB/x["path"];evidence.append({"id":x["decision_id"],"exists":p.is_file(),"digest":p.is_file() and sha(p)==x["sha256"],"selected":x["status"] in {"owner-selected","selected"}})
 for name,x in m["selected_foundations"]["definitions"].items():
  p=LAB/x["path"];evidence.append({"id":x["definition_ref"],"exists":p.is_file(),"digest":p.is_file() and sha(p)==x["sha256"],"selected":x["lifecycle_state"]=="admitted"})
 ck("selected-and-admitted-foundations-current",all(all(v for k,v in x.items() if k!="id") for x in evidence),evidence)
 maps={x["mapping_id"]:x for x in m["cross_layer_mappings"]};ck("representation-cardinalities-explicit",maps["MAP-SUBJECT-NODE"]["cardinality"]==maps["MAP-GLOBAL-RELATION-EDGE"]["cardinality"]=="0..n" and maps["MAP-LOCAL-EDGE"]["cardinality"]=="1..1",maps)
 invariants=" ".join(m["identity_and_lifecycle_invariants"]);ck("typed-relation-edge-non-collapse","Typed Relation identity and Ontology Edge identity remain separate" in invariants and "local edge never becomes global" in invariants,invariants)
 namespaces={x["namespace"]:x for x in m["relation_namespaces"]};ck("three-relation-namespaces-closed",set(namespaces)=={"lab-global","ontology-business-model","domainspec-development"} and [namespaces[x]["count"] for x in sorted(namespaces)]==[25,23,21] and namespaces["domainspec-development"]["entry_count"]==28 and namespaces["ontology-business-model"]["entry_count"]==24,{k:{"terms":v["count"],"entries":v.get("entry_count",v["count"])} for k,v in namespaces.items()})
 ck("text-collision-not-identity",m["relation_token_collisions"]["tokens"]==["derives-from"] and "does not establish identity" in m["relation_token_collisions"]["rule"],m["relation_token_collisions"])
 gaps={x["gap_id"]:x for x in m["gaps"]};ck("seven-carrier-actions-supported",len(m["recommended_artifact_type_actions"])==7 and {x["subject"] for x in m["gaps"] if x["severity"] in {"carrier-missing","admission-blocker"}}=={"Ontology Node/v1","Ontology Edge","Ontology Manifest","Ontology Cut","Ontology View","Semantic Event History","Governance Event History"},m["recommended_artifact_type_actions"])
 absent=[]
 for name in ["ontology-edge","ontology-manifest","ontology-cut","ontology-view","semantic-event-history","governance-event-history"]:absent.append({"kind":name,"carrier_absent":not (LAB/f"authority/artifact-types/{name}").exists()})
 ck("six-carriers-currently-absent",all(x["carrier_absent"] for x in absent),absent)
 runtime=m["runtime_state"];ck("runtime-boundary-evidence-current",runtime["adoption"]["status"]=="adopted" and runtime["activation"]["status"]=="authorized" and runtime["activation"]["execution_result"]=="PASS" and all(sha(LAB/x["path"])==x["sha256"] for x in [runtime["adoption"],runtime["activation"]]),runtime)
 ck("candidate-no-authority-effect",m["authority_effect"]=="none" and m["status"]=="candidate-owner-review-open",{"status":m["status"],"authority_effect":m["authority_effect"]})
 before=[(ROOT/x).read_bytes() for x in ["integration-model.json","INTEGRATION-MODEL.md"]];subprocess.run([sys.executable,str(ROOT/"build.py")],check=True);after=[(ROOT/x).read_bytes() for x in ["integration-model.json","INTEGRATION-MODEL.md"]];ck("deterministic-projection",before==after,{"model_sha256":sha(ROOT/"integration-model.json"),"projection_sha256":sha(ROOT/"INTEGRATION-MODEL.md")})
 result="PASS" if all(x["result"]=="PASS" for x in checks) else "BLOCK";receipt={"schema_version":"cyberalchemy-lab-ontology-cross-layer-model-validation/v1","result":result,"authority_effect":"none","checks":checks,"materials":{"model_sha256":sha(ROOT/"integration-model.json"),"projection_sha256":sha(ROOT/"INTEGRATION-MODEL.md")},"claim_ceiling":"PASS proves the current-evidence bindings, layer distinctions, mapping cardinalities, namespace separation, runtime boundary, and exact gap/action inventory. It does not approve or apply a convention or admission."};dump(ROOT/"receipts/validation.json",receipt);print(json.dumps({"result":result,"checks":len(checks),**receipt["materials"]},sort_keys=True));return 0 if result=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())

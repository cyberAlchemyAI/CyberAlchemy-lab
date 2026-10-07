#!/usr/bin/env python3
"""Validate Step 7 ontology carrier candidates."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from typing import Any
import jsonschema
ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[3]
KINDS=["ontology-node","ontology-edge","ontology-manifest","ontology-cut","ontology-view","semantic-event-history","governance-event-history"]
def load(p:Path)->Any:return json.loads(p.read_text(encoding="utf-8"))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p:Path,v:Any)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def validate_package(package:Path)->int:
 schema=load(package/"schema.json");artifact=load(package/"artifact.json");fixture=load(package/"fixtures/valid/record.json");v=jsonschema.Draft202012Validator(schema);checks=[]
 def ck(i,o,d):checks.append({"check_id":i,"result":"PASS" if o else "BLOCK","detail":d})
 errors=[e.message for e in v.iter_errors(fixture)];ck("valid-fixture",not errors,errors)
 bad=[]
 for p in sorted((package/"fixtures/invalid").glob("*.json")):
  es=[e.message for e in v.iter_errors(load(p))];bad.append({"path":str(p.relative_to(package)),"rejected":bool(es),"errors":es})
 ck("four-hostile-rejections",len(bad)==4 and all(x["rejected"] for x in bad),bad)
 ck("closed-schema",schema.get("additionalProperties") is False and schema["properties"]["payload"].get("additionalProperties") is False,{"top":schema.get("additionalProperties"),"payload":schema["properties"]["payload"].get("additionalProperties")})
 ck("schema-bound",artifact["schema_digest"]==sha(package/"schema.json") and artifact["status"]=="candidate-unadmitted" and artifact["authority_effect"]=="none",{"ref":artifact["artifact_type_ref"],"digest":artifact["schema_digest"]})
 reg=load(LAB/"authority/definitions/registry.json");defs=[]
 for b in artifact["semantic_definition_bindings"]:
  p=LAB/b["path"];defs.append({"ref":b["definition_ref"],"exists":p.is_file(),"digest":p.is_file() and sha(p)==b["sha256"],"current":reg["current_lookup"].get(b["definition_ref"].split('@',1)[0])==b["definition_ref"],"admitted":b["admission_posture"]=="admitted"})
 ck("current-admitted-definition",len(defs)==1 and all(all(v for k,v in x.items() if k!="ref") for x in defs),defs)
 if artifact["classification"]["semantic_kind"]=="ontology-node":
  pred=artifact["candidate_predecessor_contract"];p=LAB/pred["path"];ck("v1-predecessor-preserved",p.is_file() and sha(p)==pred["sha256"] and pred["admission_posture"]=="candidate-unadmitted-superseded-before-admission",pred)
 projection=(package/"fixtures/valid/RECORD.md").read_text(encoding="utf-8");ck("fixture-projection",fixture["node_id"] in projection and json.dumps(fixture["payload"],indent=2,sort_keys=True) in projection,"fixtures/valid/RECORD.md")
 result="PASS" if all(x["result"]=="PASS" for x in checks) else "BLOCK";receipt={"schema_version":"cyberalchemy-lab-ontology-carrier-validation/v1","artifact_type_ref":artifact["artifact_type_ref"],"result":result,"authority_effect":"none","checks":checks,"materials":{"artifact_sha256":sha(package/"artifact.json"),"schema_sha256":sha(package/"schema.json"),"fixture_sha256":sha(package/"fixtures/valid/record.json")},"claim_ceiling":"PASS proves only the candidate carrier's exact schema, current admitted Definition binding, fixtures, hostile rejection, and projection."};dump(package/"receipts/validation.json",receipt);print(json.dumps({"artifact_type_ref":artifact["artifact_type_ref"],"result":result,"checks":len(checks)},sort_keys=True));return 0 if result=="PASS" else 1
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--package",type=Path);a=ap.parse_args()
 if a.package:return validate_package(a.package.resolve())
 subprocess.run([sys.executable,str(ROOT/"build.py")],check=True);codes=[]
 for kind in KINDS:codes.append(validate_package(LAB/f"authority/artifact-types/{kind}/{'v2' if kind=='ontology-node' else 'v1'}"))
 manifest=load(ROOT/"carrier-postimages.json");integration=load(LAB/manifest["inputs"]["integration_model"]);checks=[]
 def ck(i,o,d):checks.append({"check_id":i,"result":"PASS" if o else "BLOCK","detail":d})
 ck("seven-packages-pass",len(codes)==7 and all(x==0 for x in codes),{"results":codes})
 rows=[]
 for x in manifest["entries"]:
  package=(LAB/x["artifact_path"]).parent;receipt=load(package/"receipts/validation.json");rows.append({"ref":x["artifact_type_ref"],"artifact":sha(LAB/x["artifact_path"])==x["artifact_sha256"],"schema":sha(LAB/x["schema_path"])==x["schema_sha256"],"receipt":receipt["result"]=="PASS"})
 ck("seven-exact-postimages",len(rows)==7 and all(all(v for k,v in x.items() if k!="ref") for x in rows),rows)
 ck("one-successor-six-new",manifest["counts"]=={"carrier_postimages":7,"candidate_successors":1,"new_carriers":6} and sum(x["action"]=="supersede-before-admission" for x in manifest["entries"])==1,manifest["counts"])
 recommended={x["artifact_type_ref"] for x in integration["recommended_artifact_type_actions"]};actual={x["artifact_type_ref"] for x in manifest["entries"]};ck("integration-actions-complete",recommended==actual,sorted(actual))
 # Cross-carrier source-direction rules.
 fixtures={x["kind"]:load((LAB/x["artifact_path"]).parent/"fixtures/valid/record.json") for x in manifest["entries"]}
 ck("node-and-edge-not-replay-sources",fixtures["ontology-node"]["payload"]["replay_source"] is False and fixtures["ontology-edge"]["payload"]["replay_source"] is False,True)
 ck("cut-and-view-not-replay-sources",fixtures["ontology-cut"]["payload"]["replay_source"] is False and fixtures["ontology-view"]["payload"]["replay_source"] is False,True)
 ck("history-events-are-replay-sources",all(fixtures[k]["payload"]["event_records_are_replay_source"] is True and fixtures[k]["payload"]["history_manifest_is_event_index"] is True for k in ["semantic-event-history","governance-event-history"]),True)
 edge=fixtures["ontology-edge"]["payload"];ck("projected-edge-binds-global-relation",edge["edge_mode"]=="global-projection" and edge["global_typed_relation_binding"] and edge["local_interpretation"] is None,edge)
 node=fixtures["ontology-node"]["payload"];ck("node-binds-exact-subject-and-event",set(node["represented_subject"])=={"kind","ref","version_ref","digest"} and set(node["governance_binding"]["semantic_event_ref"])=={"semantic_event_id","semantic_event_digest","semantic_cursor"},node)
 before=[(ROOT/x).read_bytes() for x in ["carrier-postimages.json","CARRIERS.md"]];subprocess.run([sys.executable,str(ROOT/"build.py")],check=True);after=[(ROOT/x).read_bytes() for x in ["carrier-postimages.json","CARRIERS.md"]];ck("deterministic-materialization",before==after,{"manifest_sha256":sha(ROOT/"carrier-postimages.json"),"projection_sha256":sha(ROOT/"CARRIERS.md")})
 result="PASS" if all(x["result"]=="PASS" for x in checks) else "BLOCK";receipt={"schema_version":"cyberalchemy-lab-step7-ontology-carrier-set-validation/v1","result":result,"authority_effect":"none","checks":checks,"materials":{"manifest_sha256":sha(ROOT/"carrier-postimages.json"),"projection_sha256":sha(ROOT/"CARRIERS.md")},"claim_ceiling":"PASS proves seven exact candidate carrier postimages, their current admitted Definition bindings, source direction, fixtures, and non-collapse constraints. It does not admit or integrate them."};dump(ROOT/"receipts/validation.json",receipt);print(json.dumps({"result":result,"checks":len(checks),**receipt["materials"]},sort_keys=True));return 0 if result=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())

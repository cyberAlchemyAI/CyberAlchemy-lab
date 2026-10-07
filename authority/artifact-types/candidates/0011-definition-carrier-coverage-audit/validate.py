#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[3]
def load(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def main():
 subprocess.run([sys.executable,str(ROOT/"build.py")],check=True);a=load(ROOT/"audit.json");checks=[]
 def ck(i,o,d):checks.append({"check_id":i,"result":"PASS" if o else "BLOCK","detail":d})
 ck("exact-60-way-partition",a["counts"]=={"integrated_definitions":60,"carrier_backed":20,"carrier_required_missing":34,"no_standalone_carrier":6,"projected_carrier_backed_after_actions":54,"projected_artifact_types_in_decision_0069":93},a["counts"])
 refs=[x["definition_ref"] for x in a["entries"]];ck("unique-definition-coverage",len(refs)==len(set(refs))==60,refs)
 materials=[]
 for x in a["entries"]:
  p=LAB/x["definition_path"];materials.append({"ref":x["definition_ref"],"exists":p.is_file(),"digest":p.is_file() and sha(p)==x["definition_sha256"],"current":x["definition_current"]})
 ck("all-definition-bytes-current-and-admitted",all(all(v for k,v in x.items() if k!="ref") for x in materials),materials)
 non={x["definition_ref"].split('@',1)[0].removeprefix('cal.definition.') for x in a["entries"] if x["posture"]=="no-standalone-carrier"};ck("exact-six-noncarriers",non=={"actor","agent","session-memory","operational-learning-cycle","classification","failure"},sorted(non))
 actions=a["required_actions"];ck("34-unique-actions",len(actions)==len({x["definition_ref"] for x in actions})==len({x["artifact_type_ref"] for x in actions})==34,actions)
 backed=[x for x in a["entries"] if x["posture"]=="carrier-backed"];carrier_files=[]
 for x in backed:
  for path in x["carrier_paths"]:
   p=LAB/path;carrier_files.append({"path":path,"exists":p.is_file()})
 ck("20-backed-definitions-materialized",len(backed)==20 and all(x["exists"] for x in carrier_files),carrier_files)
 ck("no-overlap-between-postures",not ({x["definition_ref"] for x in backed}&{x["definition_ref"] for x in actions}) and all(x["noncarrier_contract"] is None for x in a["entries"] if x["posture"]!="no-standalone-carrier"),True)
 ck("candidate-no-authority-effect",a["authority_effect"]=="none" and a["status"]=="candidate-complete-awaiting-owner-review",{"status":a["status"],"authority_effect":a["authority_effect"]})
 before=[(ROOT/x).read_bytes() for x in ["audit.json","COVERAGE-AUDIT.md"]];subprocess.run([sys.executable,str(ROOT/"build.py")],check=True);after=[(ROOT/x).read_bytes() for x in ["audit.json","COVERAGE-AUDIT.md"]];ck("deterministic-audit",before==after,{"audit_sha256":sha(ROOT/"audit.json"),"projection_sha256":sha(ROOT/"COVERAGE-AUDIT.md")})
 result="PASS" if all(x["result"]=="PASS" for x in checks) else "BLOCK";r={"schema_version":"cyberalchemy-lab-definition-carrier-coverage-validation/v1","result":result,"authority_effect":"none","checks":checks,"materials":{"audit_sha256":sha(ROOT/"audit.json"),"projection_sha256":sha(ROOT/"COVERAGE-AUDIT.md")},"claim_ceiling":"PASS proves an exact exhaustive partition of the 60 integrated Definitions into 20 carrier-backed, 34 carrier-required, and six explicitly realized noncarrier concepts. It does not materialize or admit the missing carriers."};dump(ROOT/"receipts/validation.json",r);print(json.dumps({"result":result,"checks":len(checks),**r["materials"]},sort_keys=True));return 0 if result=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())

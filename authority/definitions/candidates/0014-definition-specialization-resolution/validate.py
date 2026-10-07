#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json,hashlib
ROOT=Path(__file__).resolve().parent; SHARED=ROOT.parent/"_candidate_pack.py"
def hostile(s):
 f=set(); k=s.get("kind")
 if k=="context-profile" and s.get("is_context_instance") is True: f.add("context-profile-must-not-be-context-instance")
 if k=="capability-realization-binding" and s.get("is_capability_or_implementation") is True: f.add("realization-binding-must-not-be-endpoint")
 if k=="measurement-method" and s.get("records_execution_value") is True: f.add("measurement-method-must-not-be-result")
 if k=="measurement-result" and s.get("asserts_conclusion") is True: f.add("measurement-result-must-not-be-finding")
 if k=="model-instance-binding" and s.get("transfers_parent_authority") is True: f.add("model-binding-must-not-transfer-parent-authority")
 if k=="ledger" and s.get("append_only_inferred") is True: f.add("ledger-must-not-imply-append-only")
 if k=="withdrawal-record" and s.get("identifier_reusable") is True: f.add("withdrawal-must-preserve-identifier")
 if k=="workflow-resolution" and s.get("craft_supersedes_generic") is True: f.add("workflow-specialization-must-not-be-succession")
 if k=="project-identity-resolution" and s.get("semantic_change") is False and s.get("requires_v2") is True: f.add("project-v1-must-not-bump-without-semantic-change")
 return f
if __name__=="__main__":
 spec=importlib.util.spec_from_file_location("candidate_pack",SHARED); m=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(m); m.hostile_failures=hostile
 rc=m.validate(ROOT,{'cal.definition.context-profile','cal.definition.capability-realization-binding','cal.definition.measurement-method','cal.definition.measurement-result','cal.definition.model-instance-binding','cal.definition.ledger','cal.definition.withdrawal-record'})
 if rc: raise SystemExit(rc)
 r=json.loads((ROOT/"resolution.json").read_text()); ok=(len(r["positive_definition_bindings"])==5 and len(r["workflow_overlap_resolutions"])==3 and all(x["resolution"]=="craft-specializes-generic" and x["succession"] is False for x in r["workflow_overlap_resolutions"]) and r["project_identity_resolution"]["resolution"]=="retain-v1" and r["project_identity_resolution"]["requires_v2_before_permanent_use"] is False)
 receipt=json.loads((ROOT/"receipts/validation.json").read_text()); receipt["checks"].append({"check_id":"step3-resolution-closure","result":"PASS" if ok else "FAIL","detail":{"positive_bindings":len(r["positive_definition_bindings"]),"workflow_overlaps":len(r["workflow_overlap_resolutions"]),"project_resolution":r["project_identity_resolution"]["resolution"]}}); receipt["summary"]={"passed":20 if ok else 19,"failed":0 if ok else 1,"total":20}; receipt["result"]="PASS" if ok else "FAIL"; receipt["materials"]["resolution_sha256"]=hashlib.sha256((ROOT/"resolution.json").read_bytes()).hexdigest(); (ROOT/"receipts/validation.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n"); print("STEP3_RESOLUTION_VALIDATION="+receipt["result"]); print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}"); raise SystemExit(0 if ok else 1)

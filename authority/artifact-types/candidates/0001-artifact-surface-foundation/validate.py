#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, runpy
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parent; LAB=ROOT.parents[3]
def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
def check(cid,ok,detail): checks.append({"check_id":cid,"result":"PASS" if ok else "BLOCK","detail":detail})

if __name__=="__main__":
 runpy.run_path(str(ROOT/"build.py"),run_name="__main__")
 c=load(ROOT/"candidate.json"); check("candidate-no-authority-effect",c["authority_effect"]=="none" and c["status"]=="test-candidate-unapproved",{"status":c["status"],"authority_effect":c["authority_effect"]})
 dr=load(LAB/"authority/definitions/candidates/0009-artifact-surface-foundation/receipts/validation.json"); check("definitions-pass-without-admission",dr["result"]=="PASS" and dr["promotion_eligibility"]=="blocked-by-declared-dependencies",{"result":dr["result"],"promotion":dr["promotion_eligibility"]})
 type_results=[]
 for name in ["artifact-type-registry","artifact-type-request","canonical-package-manifest"]:
  p=LAB/f"authority/artifact-types/{name}/v1/receipts/validation.json"; r=load(p); type_results.append({"name":name,"result":r["result"],"admission":r["assessment"]["admission_posture"]})
 check("three-artifact-types-pass-candidate-only",all(x["result"]=="PASS" and x["admission"]=="candidate-unadmitted" for x in type_results),type_results)
 reg=load(ROOT/"registry.json"); schema=load(LAB/"authority/artifact-types/artifact-type-registry/v1/schema.json"); errors=sorted(x.message for x in jsonschema.Draft202012Validator(schema).iter_errors(reg)); check("registry-schema-valid",not errors,errors)
 refs=[x["artifact_type_ref"] for x in reg["entries"]]; check("exact-25-admitted-type-versions",len(refs)==25 and len(set(refs))==25,{"count":len(refs),"unique":len(set(refs))})
 check("ontology-package-not-falsely-admitted","cal.artifact-type.ontology-package/v1" not in refs,refs)
 foundation=[x for x in reg["entries"] if x["admission_decision_ref"]=="CAL-DECISION-0013-FOUNDATION-01-ADMISSION"]; selector_based=[x for x in foundation if x["schema_selector"]]
 check("foundation-bootstrap-preserved",len(foundation)==8 and len(selector_based)==7,{"foundation":len(foundation),"selector_based":len(selector_based)})
 digests=[]
 for x in reg["entries"]:
  ap=LAB/x["artifact_path"]; sp=LAB/x["schema_path"]; digests.append({"ref":x["artifact_type_ref"],"artifact_current":ap.is_file() and sha(ap)==x["artifact_sha256"],"schema_current":sp.is_file() and sha(sp)==x["schema_sha256"]})
 check("registry-exact-byte-bindings",all(x["artifact_current"] and x["schema_current"] for x in digests),digests)
 decision_paths={
  "CAL-DECISION-0013-FOUNDATION-01-ADMISSION":"docs/decisions/0013-foundation-01-admission/decision.json",
  "CAL-DECISION-0015-DEFINITION-V1-ADMISSION":"docs/decisions/0015-definition-v1-admission/decision.json",
  "CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION":"docs/decisions/0021-ctx01-artifact-type-promotion/decision.json",
  "CAL-DECISION-0027-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPE-PROMOTION":"docs/decisions/0027-ctx07-normalized-context-artifact-type-promotion/decision.json",
  "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1":"docs/decisions/0029-cml07-semantic-foundation-v1/decision.json",
  "CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1":"docs/decisions/0030-cml07-s2-artifact-types-v1/decision.json",
 }
 decision_results=[]
 for x in reg["entries"]:
  d=load(LAB/decision_paths[x["admission_decision_ref"]]); admitted=d.get("admitted_artifact_types")
  if isinstance(admitted,list) and admitted and isinstance(admitted[0],str): ok=x["artifact_type_ref"] in admitted
  elif isinstance(admitted,list):
   hit=next((y for y in admitted if y["artifact_type_ref"]==x["artifact_type_ref"]),None); ok=bool(hit) and hit["artifact_path"]==x["artifact_path"] and hit["artifact_sha256"]==x["artifact_sha256"] and hit["schema_path"]==x["schema_path"] and hit["schema_sha256"]==x["schema_sha256"]
  elif d.get("admitted_contract",{}).get("artifact_type_ref")==x["artifact_type_ref"]:
   hit=d["accepted_candidate"]; ok=hit["path"]==x["artifact_path"] and hit["sha256"]==x["artifact_sha256"]
  else:
   hit=d.get("admitted_artifact_type",{}); ok=hit.get("artifact_type_ref")==x["artifact_type_ref"] and hit.get("path")==x["artifact_path"] and hit.get("sha256")==x["artifact_sha256"]
  decision_results.append({"ref":x["artifact_type_ref"],"decision":x["admission_decision_ref"],"bound":ok})
 check("registry-decision-overlay-closure",all(x["bound"] for x in decision_results),decision_results)
 current=[x for x in reg["entries"] if x["lifecycle_state"]=="admitted-current"]; discs=[x["instance_discriminator"]["value"] for x in current]; check("current-discriminators-unique",len(discs)==len(set(discs)),{"count":len(discs),"unique":len(set(discs))})
 gen_path=LAB/"tooling/generators/artifact_surface.py"; spec=importlib.util.spec_from_file_location("g",gen_path); g=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(g)
 check("registry-projection-parity",(ROOT/"REGISTRY.md").read_text()==g.render_registry(reg),sha(ROOT/"REGISTRY.md"))
 audit=load(ROOT/"audit.json"); check("audit-complete-with-visible-residue",audit["result"]=="complete-with-visible-residue" and len(audit["findings"])==9,{"result":audit["result"],"findings":len(audit["findings"])})
 check("audit-projection-parity",(ROOT/"AUDIT.md").read_text()==g.render_audit(audit),sha(ROOT/"AUDIT.md"))
 manifest=load(ROOT/"manifest.json"); manifest_results=[]
 for x in manifest["materials"]:
  p=LAB/x["path"]; manifest_results.append({"path":x["path"],"current":p.is_file() and sha(p)==x["sha256"]})
 check("candidate-byte-manifest-closed",len(manifest_results)>=40 and all(x["current"] for x in manifest_results),{"materials":len(manifest_results),"stale":[x["path"] for x in manifest_results if not x["current"]]})
 hostile=load(LAB/"tests/conformance/artifact-surface-foundation/suite.json"); observed=[]
 mapping={x["instance_discriminator"]["value"]:x["artifact_type_ref"] for x in current}
 for case in hostile["cases"]:
  matches=[] if case["schema_version"] not in mapping else [mapping[case["schema_version"]]]
  if case.get("extra_match"): matches.append(case["extra_match"])
  outcome="resolved" if len(matches)==1 else "unresolved" if len(matches)==0 else "ambiguous"
  observed.append({"case_id":case["case_id"],"expected":case["expected"],"actual":outcome,"ok":outcome==case["expected"]})
 check("resolution-hostile-suite",all(x["ok"] for x in observed),observed)
 blocked=[x for x in checks if x["result"]=="BLOCK"]
 receipt={"schema_version":"cyberalchemy-lab-artifact-surface-foundation-validation/v1","subject":c["candidate_id"],"result":"PASS" if not blocked else "BLOCK","authority_effect":"none","assessment":{"product_candidate":"TESTED" if not blocked else "NOT_ESTABLISHED","product_approval":"not_granted","definition_admission":"not_granted","artifact_type_admission":"not_granted","registry_activation":"not_authorized","migration":"not_authorized"},"checks":checks,"summary":{"passed":len(checks)-len(blocked),"blocked":len(blocked),"total":len(checks)},"materials":{"candidate_sha256":sha(ROOT/"candidate.json"),"definition_receipt_sha256":sha(LAB/"authority/definitions/candidates/0009-artifact-surface-foundation/receipts/validation.json"),"registry_sha256":sha(ROOT/"registry.json"),"audit_sha256":sha(ROOT/"audit.json"),"manifest_sha256":sha(ROOT/"manifest.json"),"suite_sha256":sha(LAB/"tests/conformance/artifact-surface-foundation/suite.json")},"claim_ceiling":"PASS establishes exact current test evidence for the unapproved Artifact Surface Foundation candidate only. It does not approve the product, admit definitions or Artifact Types, activate the registry, establish repository-wide conformance, migrate files, or authorize publication."}
 out=ROOT/"receipts/validation.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
 print(f"ARTIFACT_SURFACE_FOUNDATION={receipt['result']}"); print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}"); raise SystemExit(0 if not blocked else 1)

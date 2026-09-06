#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parent; SHARED=ROOT.parent/"_candidate_pack.py"
def hostile(subject):
 failures=set()
 if subject.get("resolution_basis")=="directory": failures.add("directory-must-not-resolve-artifact-type")
 if subject.get("kind")=="canonical-carrier" and not subject.get("declared_by_package_manifest"): failures.add("canonical-carrier-must-be-declared")
 if subject.get("kind")=="artifact-type-resolution" and len(subject.get("matches",[]))!=1: failures.add("artifact-type-resolution-must-be-unique")
 if subject.get("kind")=="artifact-type-request" and subject.get("consumed_as_subject") is True: failures.add("artifact-type-request-must-not-substitute-for-subject")
 if subject.get("independent_lifecycle") is True and not subject.get("package_manifest_ref"): failures.add("independent-lifecycle-must-have-package-manifest")
 return failures
if __name__=="__main__":
 spec=importlib.util.spec_from_file_location("candidate_pack",SHARED); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); module.hostile_failures=hostile
 result=module.validate(ROOT,{"cal.definition.artifact-surface-classification","cal.definition.artifact-type-resolution","cal.definition.artifact-type-request","cal.definition.canonical-package-manifest"})
 receipt=json.loads((ROOT/"receipts/validation.json").read_text()); count=len(json.loads((ROOT/"registry-postimage.json").read_text())["entries"]); ok=count==42
 receipt["checks"].append({"check_id":"successor-registry-count","result":"PASS" if ok else "FAIL","detail":{"expected":42,"actual":count}})
 failed=[x for x in receipt["checks"] if x["result"]=="FAIL"]; receipt["result"]="PASS" if result==0 and not failed else "FAIL"; receipt["summary"]={"passed":len(receipt["checks"])-len(failed),"failed":len(failed),"total":len(receipt["checks"])}; receipt["promotion_eligibility"]="blocked-by-declared-dependencies" if receipt["result"]=="PASS" else "not-eligible"
 (ROOT/"receipts/validation.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n"); print(f"ARTIFACT_SURFACE_DEFINITION_SUCCESSORS={receipt['result']}"); print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}"); raise SystemExit(0 if receipt["result"]=="PASS" else 1)

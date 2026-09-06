#!/usr/bin/env python3
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parent; SHARED=ROOT.parent/"_candidate_pack.py"
def hostile(subject):
 failures=set()
 if subject.get("execution_authority") is not False: failures.add("manifest-must-not-authorize-execution")
 if subject.get("copy_semantics",{}).get("overwrite") is not False: failures.add("manifest-must-not-overwrite")
 if not subject.get("rollback_ref"): failures.add("manifest-must-account-for-rollback")
 return failures
if __name__=="__main__":
 spec=importlib.util.spec_from_file_location("candidate_pack",SHARED); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); module.hostile_failures=hostile
 raise SystemExit(module.validate(ROOT,{"cal.definition.repository-migration-manifest"}))

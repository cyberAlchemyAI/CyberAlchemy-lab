"""Independent constant-pin verification of the separately staged runtime16 draft."""
import json
import fcntl
import os
from pathlib import Path
from jsonschema import Draft202012Validator
import build_runtime as B

def main():
    api=B.BASE/'api-integration-v16';out=B.HERE/'runtime16-draft-0276'
    source_pin='8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7'
    profile_pin='8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c'
    fd=os.open(B.ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-api-regression-0173-0190.execution.lock',os.O_RDWR|os.O_NOFOLLOW)
    try:
        fcntl.flock(fd,fcntl.LOCK_SH);g=B.module('_independent_runtime16_fixed_pin_guard',api/'guard.py');g.verify(source_pin)
        B.exact(api/'contract-profile.json',profile_pin)
        source=B.exact(api/'source-manifest.json',source_pin);profile=B.exact(api/'contract-profile.json',profile_pin)
        env=B.load(out/'environment-contract.json');record=B.load(out/'runtime-implementation.json');member=B.load(out/'review-member.json')
        B.need(env['complete_source_bindings']==source['files'] and env['complete_profile_bindings']==profile['files'],'draft omits source/profile input')
        B.need(env['API_source_binding']==B.bind(api/'source-manifest.json') and env['API_profile_binding']==B.bind(api/'contract-profile.json'),'draft selects another family')
        B.need(env['current_API16_R06_conformance_binding'] is None and env['current_API16_all34_qualification_binding'] is None,'pending evidence silently claimed')
        B.need(member['targets']==[B.bind(out/'runtime-implementation.json')],'member differs from actual record')
        B.need(record['payload']['environment_contract_ref']==str((out/'environment-contract.json').relative_to(B.ROOT)),'environment locator differs')
        for path in record['payload']['conforms_to_schema_refs']:B.need((B.ROOT/path).is_file(),'fake schema locator')
        Draft202012Validator(B.load(B.IMPL/'schema.json')).validate(record)
        g.verify(source_pin);B.exact(api/'contract-profile.json',profile_pin)
        report={'schema_version':'lab-independent-runtime16-draft-verification/v1-candidate','caller_binding':B.bind(Path(__file__)),
            'runtime_body_binding':B.bind(out/'runtime-implementation.json'),'environment_binding':B.bind(out/'environment-contract.json'),
            'member_binding':B.bind(out/'review-member.json'),'full16_constant_pin_entry_exit_verified':True,
            'original_builder_used_current_output_pin_for_exit':True,
            'independent_verifier_corrects_that_proof_limitation_without_changing_original_builder_or_outputs':True,
            'current_R06_conformance_absent':True,'current_all34_and_345_evidence_not_inferred':True,
            'authority_effect':'none','actual_owner_outcome':None,'release_ready':False,'task_complete':False,'goal_complete':False}
        B.emit(out/'independent-verification.json',report);print(json.dumps({'result':'VERIFIED-DRAFT-ONLY','report_binding':B.bind(out/'independent-verification.json')}),flush=True)
    finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)

if __name__=='__main__':main()

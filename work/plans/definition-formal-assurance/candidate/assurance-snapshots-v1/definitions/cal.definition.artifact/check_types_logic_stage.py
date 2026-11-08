"""Independently audit Artifact's frozen types/logic and retained actual failure."""
import json
import build_candidate as b
import close_types_logic_stage as stage
def main():
 context,counts,model,source,fresh,prior=stage.audit();receipt=stage.load('types-logic-receipt.json');b.unchanged(receipt['inputs']+receipt['producer_results']+[x['attempt_ref'] for x in receipt['retained_failed_native_attempts']]);assert receipt['result']=='PASS-for-typed-candidate-stage-only' and receipt['counts']==counts and receipt['full_delivery_sealed'] is False and receipt['working_draft_files_observed']==82 and receipt['last_sealed_partial_drafts']==81 and receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False and receipt['mechanized_proof'] is False and len(receipt['inputs'])==16 and len(receipt['retained_failed_native_attempts'])==1 and receipt['retained_failed_native_attempts'][0]['stage']=='native-build' and receipt['retained_failed_native_attempts'][0]['actual_exit_code']==1
 print(json.dumps({'result':'PASS-for-preserved-Artifact-types-logic-stage','frozen_inputs':16,'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'working_drafts':82,'retained_failed_native_builds':1,'full_delivery_sealed':False,'goal_status':'active'},indent=2))
if __name__=='__main__':main()

"""Independently audit Receipt's frozen typed-stage evidence and partial claim boundary."""
import json
import build_candidate as b
import close_types_logic_stage as stage
def main():
 context,counts,model,source,fresh,prior=stage.audit();receipt=stage.load('types-logic-receipt.json');b.unchanged(receipt['inputs']+receipt['producer_results']+receipt['retained_successful_prior_stage_refs']+[x['attempt_ref'] for x in receipt['retained_failed_native_attempts']]);assert receipt['result']=='PASS-for-typed-candidate-stage-only' and receipt['full_delivery_sealed'] is False and receipt['counts']==counts and receipt['working_draft_files_observed']==81 and receipt['last_sealed_partial_drafts']==80 and receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False and receipt['mechanized_proof'] is False and len(receipt['inputs'])==16 and len(receipt['retained_failed_native_attempts'])==1 and receipt['retained_failed_native_attempts'][0]['stage']=='typed-freeze-audit' and receipt['retained_failed_native_attempts'][0]['actual_exit_code']==1 and len(receipt['retained_successful_prior_stage_refs'])==2
 print(json.dumps({'result':'PASS-for-preserved-Receipt-types-logic-stage','frozen_inputs':16,'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'working_drafts':81,'full_delivery_sealed':False,'goal_status':'active'},indent=2))
if __name__=='__main__':main()

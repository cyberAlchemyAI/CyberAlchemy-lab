"""Read-only audit of frozen Lifetime typed-stage evidence and preserved earlier seals."""
import json
import build_candidate as b
import close_types_logic_stage as stage
def main():
 context,counts,model,source,fresh,prior=stage.audit();receipt=stage.load('types-logic-receipt.json');b.unchanged(receipt['inputs']+receipt['producer_results']+receipt['retained_preparation_failure_refs']);assert len(receipt['inputs'])==16 and receipt['result']=='PASS-for-typed-candidate-stage-only' and receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False and receipt['mechanized_proof'] is False and receipt['full_delivery_sealed'] is False and receipt['last_sealed_partial_drafts']==82 and receipt['working_draft_files_observed']==83 and len(receipt['retained_failed_native_attempts'])==1 and receipt['retained_failed_native_attempts'][0]['actual_exit_code']==1 and receipt['retained_failed_native_attempts'][0]['native_unit_created'] is False
 print(json.dumps({'result':'PASS-for-separate-frozen-types-logic-audit','frozen_inputs':16,'prior_candidate_files_preserved':len(prior['files']),'controls':receipt['controls'],'countermodels':receipt['nonentailment_queries'],'source_checks':receipt['actual_source_checks'],'working_drafts':83,'full_delivery_sealed':False,'goal_status':'active'},indent=2,sort_keys=True))
if __name__=='__main__':main()

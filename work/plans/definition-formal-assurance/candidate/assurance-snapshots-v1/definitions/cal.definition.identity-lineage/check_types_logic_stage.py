"""Separate actual IdentityLineage sixteen-input typed-stage audit."""
import json
import build_candidate as b
import close_types_logic_stage as stage
def main():
 context,counts,model,source,fresh,prior=stage.audit();receipt=stage.load('types-logic-receipt.json');b.unchanged(receipt['inputs']+receipt['producer_results']+receipt['retained_preparation_failure_refs']+receipt['retained_successful_prior_stage_refs']);assert receipt['result']=='PASS-for-typed-candidate-stage-only' and len(receipt['inputs'])==16 and receipt['full_delivery_sealed'] is False and receipt['semantic_ready'] is False and receipt['source_fidelity']=='pending' and len(receipt['retained_preparation_failure_refs'])==len(receipt['retained_successful_prior_stage_refs'])==1 and receipt['retained_failed_native_attempts']==receipt['retained_failed_typed_stage_refs']==[] and receipt['counts']==counts and receipt['controls']==205 and receipt['nonentailment_queries']==34 and receipt['source_conditioned_queries']==10 and receipt['actual_source_checks']==89 and receipt['source_query_obligations']==52
 print(json.dumps({'result':'PASS-separate-IdentityLineage-typed-stage-audit','frozen_inputs':16,'controls':205,'nonentailment_queries':34,'source_conditioned_queries':10,'prior_candidate_files_preserved':9112,'source_files_current':201,'working_drafts':100,'last_full_inventory_partial_drafts':99,'whole_inventory_refresh_complete':False,'whole_definition_proofs':0,'owner_accepted_whole_translations':0,'retained_native_failures':0,'retained_preparation_failures':1,'retained_successful_prior_label_stages':1,'goal_status':'active'},indent=2))
if __name__=='__main__':main()


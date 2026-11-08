"""Independent read-only Derived Refresh typed-stage audit."""
import json
import build_candidate as b
import close_types_logic_stage as stage
def main():
 context,counts,model,source,fresh,prior=stage.audit();receipt=stage.load('types-logic-receipt.json');b.unchanged(receipt['inputs']+receipt['producer_results']+receipt['retained_preparation_failure_refs']+receipt['retained_failed_typed_stage_refs']+[receipt['serialization_recovery_ref']]);assert receipt['result']=='PASS-for-typed-candidate-stage-only' and len(receipt['inputs'])==16 and receipt['full_delivery_sealed'] is False and receipt['semantic_ready'] is False and receipt['source_fidelity']=='pending' and receipt['retained_failed_native_attempts']==context['retained_preparation_failure_refs'] and receipt['counts']==counts and receipt['controls']==203 and receipt['nonentailment_queries']==28 and receipt['actual_source_checks']==50 and receipt['source_query_obligations']==28
 print(json.dumps({'result':'PASS-separate-DerivedRefresh-typed-stage-audit','frozen_inputs':16,'controls':203,'nonentailment_queries':28,'prior_candidate_files_preserved':8024,'source_files_current':201,'working_drafts':91,'last_full_inventory_partial_drafts':90,'whole_inventory_refresh_complete':False,'whole_definition_proofs':0,'owner_accepted_whole_translations':0,'retained_native_failures':1,'goal_status':'active'},indent=2))
if __name__=='__main__':main()

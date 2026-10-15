import json
import build_candidate as b
import close_types_logic_stage as stage
context,counts,model,source,fresh,prior=stage.audit();receipt=stage.load('types-logic-receipt.json')
b.unchanged(receipt['inputs']+receipt['checker_bindings']+receipt['retained_preparation_failure_refs'])
assert receipt['counts']==counts and receipt['controls']==198 and receipt['nonentailment_queries']==32 and receipt['actual_source_checks']==86 and receipt['source_query_obligations']==74
assert receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is receipt['mechanized_proof'] is receipt['full_delivery_sealed'] is receipt['current_whole_inventory_refresh_complete'] is False
assert receipt['source_owner_accepted_whole_translations']==receipt['whole_definition_proofs']==0 and receipt['goal_status']=='active'
assert receipt['working_draft_files_observed']==111 and receipt['remaining_current_identities_without_draft_files_observed']==72 and len(prior['files'])==10389
print(json.dumps({'result':'PASS-separate-CoordinationContext-typed-stage-audit','controls':198,'queries':32,'source_checks':86,'frozen_inputs':len(receipt['inputs']),'frozen_checkers':len(receipt['checker_bindings']),'full_delivery_sealed':False,'semantic_ready':False},indent=2))

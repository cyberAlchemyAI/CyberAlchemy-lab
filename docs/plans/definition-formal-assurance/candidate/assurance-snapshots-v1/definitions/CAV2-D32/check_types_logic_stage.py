"""Separate read-only process audits the frozen typed-stage receipt."""
import json
import build_candidate as b
import close_types_logic_stage as stage
receipt=json.loads((b.UNIT/'types-logic-receipt.json').read_bytes());b.unchanged(receipt['inputs']+receipt['checker_bindings']);context,counts,model,source,fresh,prior=stage.audit()
assert receipt['result']=='PASS-for-typed-candidate-stage-only' and receipt['unit_id']==context['unit_id'] and receipt['counts']==counts and receipt['fresh_checks']==fresh and receipt['controls']==173 and receipt['nonentailment_queries']==39 and receipt['actual_source_checks']==69 and receipt['source_files_current']==201 and receipt['prior_candidate_files_preserved']==9852 and receipt['working_draft_files_observed']==106
assert all(receipt[k] is False for k in ['semantic_ready','mechanized_proof','full_delivery_sealed','current_whole_inventory_refresh_complete']) and receipt['authority_effect']=='none' and receipt['source_fidelity']=='pending' and receipt['goal_status']=='active' and receipt['source_owner_accepted_whole_translations']==receipt['whole_definition_proofs']==0
b.unchanged(receipt['inputs']+receipt['checker_bindings']+prior['files']);print(json.dumps({'result':'PASS-separate-GenericMethod-typed-stage-audit','frozen_input_files':len(receipt['inputs']),'controls':173,'nonentailment_queries':39,'source_checks':69,'prior_candidate_files_preserved':9852,'source_files_current':201,'full_delivery_sealed':False,'next':'GenericMethod carrier/consumer maps before generic Method'},indent=2))

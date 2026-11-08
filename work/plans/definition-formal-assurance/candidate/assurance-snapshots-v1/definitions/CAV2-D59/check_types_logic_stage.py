"""Separate read-only Goal typed-stage audit of the exact frozen receipt."""
import json
import build_candidate as b
import close_types_logic_stage as stage
r=json.loads((b.UNIT/'types-logic-receipt.json').read_bytes());b.unchanged(r['inputs']+r['checker_bindings']);context,counts,model,source,fresh,prior=stage.audit()
assert r['result']=='PASS-for-typed-candidate-stage-only' and r['unit_id']==context['unit_id']=='F08-T.CAV2-D59' and r['counts']==counts and r['fresh_checks']==fresh and r['controls']==181 and r['nonentailment_queries']==24 and r['actual_source_checks']==69 and r['source_files_current']==201 and r['prior_candidate_files_preserved']==9964 and r['working_draft_files_observed']==107
assert all(r[k] is False for k in ['semantic_ready','mechanized_proof','full_delivery_sealed','current_whole_inventory_refresh_complete']) and r['authority_effect']=='none' and r['source_fidelity']=='pending' and r['goal_status']=='active' and r['source_owner_accepted_whole_translations']==r['whole_definition_proofs']==0 and r['next_definition_after_delivery']=='F08-T.CAV2-D60'
b.unchanged(r['inputs']+r['checker_bindings']+prior['files']);print(json.dumps({'result':'PASS-separate-Goal-typed-stage-audit','frozen_input_files':len(r['inputs']),'controls':181,'nonentailment_queries':24,'source_checks':69,'prior_candidate_files_preserved':9964,'source_files_current':201,'full_delivery_sealed':False,'next':'Goal full consumer delivery before CAV2-D60 Project'},indent=2))

"""Separate actual read-only audit of frozen CI typed receipt."""
import json
import build_candidate as b
import close_types_logic_stage as stage
r=json.loads((b.UNIT/'types-logic-receipt.json').read_bytes())
b.unchanged(r['inputs']+r['checker_bindings']+r['retained_review_writer_failure_refs'])
assert r['retained_review_writer_failures']==1 and len(r['retained_review_writer_failure_refs'])==6
context,counts,model,source,fresh,prior=stage.audit()
assert r['unit_id']==context['unit_id']=='F08-T.cal.definition.capability-instance' and r['counts']==counts and r['fresh_checks']==fresh
assert (r['controls'],r['nonentailment_queries'],r['source_conditioned_queries'],r['actual_source_checks'],r['source_query_obligations'])==(186,28,2,93,63)
assert r['prior_candidate_files_preserved']==10188 and r['working_draft_files_observed']==109
assert all(r[k] is False for k in ['semantic_ready','mechanized_proof','full_delivery_sealed','current_whole_inventory_refresh_complete'])
assert r['authority_effect']=='none' and r['source_fidelity']=='pending' and r['goal_status']=='active' and r['source_owner_accepted_whole_translations']==r['whole_definition_proofs']==0
assert r['next_definition_after_delivery']=='F08-T.cal.definition.capability-realization-binding' and r['retained_failed_prepared_syntax']==1 and r['retained_failed_prepared_semantic_controls']==0
b.unchanged(r['inputs']+r['checker_bindings']+prior['files'])
print(json.dumps({'result':'PASS-separate-CapabilityInstance-typed-stage-audit','frozen_input_files':len(r['inputs']),'controls':186,'nonentailment_queries':28,'conditioned_queries':2,'source_checks':93,'prior_candidate_files_preserved':10188,'source_files_current':201,'full_delivery_sealed':False,'next':'Capability Instance full consumer delivery before Capability Realization Binding'},indent=2))


"""Freeze the exact Intent typed stage; full delivery and original scope stay open."""
import json,re
import build_candidate as b
import verify_candidate as a
import verify_source_checks as s
INPUTS=['context.json','t.json','static-ir.json','correspondence.json','correspondence-check.json','denominator.json','clause-analysis.json','query-policy.json','source-query-obligation.json','comparison-selection.json','model-controls.json','source-checks.json','fresh-types-logic-results.json','REVIEW.md','CONTINUATION.md','DELIVERY-CONTEXT.md','continuation-dag.json']
EXPECTED={'source_units':22,'mapped_clauses':22,'encoded_clauses':8,'explanatory_clauses':9,'deferred_clauses':5,'declarations':185,'required_populations':32,'unresolved_populations':127,'direct_semantic_uses':28,'countermodel_queries':42}
def load(name):return json.loads((b.UNIT/name).read_bytes())
def audit():
 context=load('context.json');core=load('t.json')['payload'];packet=load('correspondence.json');counts=load('denominator.json');snapshot=b.snapshot();b.unchanged(context['sources']);b.external_current(context);assert b.r.verify(snapshot,b.ROOT)['files']==201
 prior=json.loads((b.BASE/'definitions/cal.definition.implementation/delivery-manifest.json').read_bytes());b.unchanged(prior['files']);assert len(prior['files'])==10600
 assert context['unit_id']=='F08-T.cal.definition.intent' and core['source']==context['source_selection']==b.source_ref(snapshot,'cal.definition.intent') and core['source']['sha256']=='cce7b46ddc9bf4f7b42038c15da1380573e58d9bb2919d86b94a7c1738325c0b'
 assert context['current_admission_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and context['normalization_context']['decision_status']=='owner-selected'
 assert context['pre_execution_check']['previous_separate_delivery_audit_exit_code']==context['pre_execution_check']['prepared_source_and_model_check_exit_code']==context['pre_execution_check']['prepared_independent_source_check_exit_code']==0
 work=json.loads((b.ROOT/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json').read_bytes());swu=next(row for row in work['units'] if row['id']==context['unit_id']);assert swu['outputs']==[b.ref(b.UNIT/'t.json')['path']] and swu['write_scope']==context['write_scope'] and swu['depends_on_tasks']==['A04','C01','E02'] and len(work['units'])==797
 assert not context['session_scope']['blocking_user_decisions']
 for binding in context['prerequisite_receipts']:
  b.unchanged([binding['receipt_ref']]);assert binding['result'].startswith('PASS') and json.loads((b.ROOT/binding['receipt_ref']['path']).read_bytes())['task_result']==binding['result']
 assert b.c.validate(load('t.json'),'interpretation')['status']=='structurally-valid' and load('static-ir.json')==b.ir.compile_interpretation(core,snapshot) and packet['interpretation']==core
 account=b.co.check(packet,snapshot,required_dependencies=[row['version_ref'] for row in core['depends_on']],required_conflicts=[row['finding_id'] for row in packet['source_precedence']['conflicts']]);assert account==load('correspondence-check.json') and account['character_accounting_complete']
 assert not core['assumptions'] and not packet['assumption_links'] and core['source_fidelity']=='pending'
 assert counts==EXPECTED and (len(b.SORTS),len(b.CONSTANTS),len(b.FUNCTIONS),len(b.SIGNATURE))==(19,5,34,127)
 assert core['interpretation_id']=='interpretation:Intent-seven-coordinates-classification-explained-revision-trace-v1' and len(core['depends_on'])==28 and len(packet['source_precedence']['conflicts'])==23
 assert packet['source_precedence']['review_ref'] is None and packet['review_packet']['review_status']=='pending'
 required=[row for row in core['populations'] if row['requirement']=='required'];assert {row['population_id']:(row['carrier'],row['statement']) for row in required}=={'POP-REQ-'+name:value for name,value in b.required_populations().items()} and len(core['populations'])==159 and all(row['review_ref'] is None for row in core['populations'])
 doc=b.co.source_document(snapshot,core['source']);assert all(row['formal_statement']==spec['formula'] and row['disposition']==spec['disposition'] for row,spec in zip(core['clauses'],b.selected_clauses(doc)))
 analysis=load('clause-analysis.json');assert analysis['known_losses']==b.LOSSES and analysis['primitive_theory_formulas']==8
 assert all(analysis[key] is True for key in ['canonical_classification_conditional','work_scope_not_owner_scope','desired_hypothesis_independent_from_after','multiple_reasons_allowed','no_existing_claim_required','deferred_output_allowed'])
 assert all(analysis[key] is False for key in ['actual_outcome_queries_assumed_in_T','whole_prior_theories_imported','source_precedence_reviewed','mechanized_proof','automatic_fulfillment_or_mutation_permission','universal_successor_identity_policy_added'])
 stack=[row['formal_statement'] for row in core['clauses'] if row['disposition']=='encoded']
 while stack:
  node=stack.pop()
  if isinstance(node,dict):
   assert not(node.get('op')=='pred' and any(node.get('name','').startswith(prefix+'Actual') for prefix in ['Intent','Change','Claim']));stack.extend(node.values())
  elif isinstance(node,list):stack.extend(node)
 assert load('query-policy.json')['queries']==b.query_specs() and len(b.query_specs())==42
 model=a.verify();source=s.verify();assert model['control_count']==len(model['results'])==200 and len(model['nonentailment_countermodels'])==42
 assert (sum(row.get('primary_theory_satisfied') is True for row in model['results']),sum(row.get('primary_theory_satisfied') is False for row in model['results']),sum(row['status']=='rejected-model-structure' for row in model['results']))==(73,119,8)
 cases={row['case_id']:row for row in model['results']}
 for name in ['seven-coordinates-canonical-and-noncanonical-explained-changes-four-trace-kinds','additional-explicit-source-section-permitted','no-output-change-unused-reason-can-be-absent','no-output-change-extra-explanation-permitted']:assert cases[name]['primary_theory_satisfied'] is cases[name]['required_population_satisfied'] is True
 for name in ['no-selected-intents-changes-or-claims','no-selected-changes','no-selected-claims','mixed-orientation-reduced-to-pressure','single-explanation-still-valid']:assert cases[name]['primary_theory_satisfied'] is True and cases[name]['required_population_satisfied'] is False
 assert len(source['checks'])==99 and source['source_query_obligations']==len(load('source-query-obligation.json')['obligations'])==85
 assert source['accepted_source_map'] is source['actual_Intent_fulfilled_or_authorized'] is source['semantic_ready'] is False and source['source_fidelity']=='pending'
 fresh=load('fresh-types-logic-results.json');assert [row['check'] for row in fresh]==['contract','model','source'] and all(row['exit_code']==0 and not(b.UNIT/row['stderr']).read_bytes() for row in fresh)
 assert fresh[0]['argv'][1:]==['-B',str(b.IMPL/'contracts.py'),'validate','--kind','interpretation','--input',str(b.UNIT/'t.json')]
 for row,script in zip(fresh[1:],['verify_candidate.py','verify_source_checks.py']):assert row['argv']==[fresh[0]['argv'][0],'-B',str(b.UNIT/script)] and (b.UNIT/row['stdout']).read_bytes()==(b.UNIT/(row['check']+'-stdout.txt')).read_bytes()
 assert [row['check'] for row in load('native-stage-results.json')]==['author','build','model','source']
 for name in ['author','build','model','source']:
  result=load(name+'-command-result.json');assert result['exit_code']==0 and not(b.UNIT/result['stderr']).read_bytes()
 b.unchanged(context['retained_preparation_failure_refs']+context['retained_successful_preparation_refs']);assert not context['retained_preparation_failure_refs']
 dirty=json.loads((b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261012-project/unrelated-tracked-work.json').read_bytes());assert len(dirty['refs'])==30;b.unchanged(dirty['refs'])
 assert len(list((b.BASE/'definitions').glob('*/t.json')))==113 and len(snapshot['current_entries'])==183
 assert len((b.UNIT/'t.json').read_bytes())<b.c.MAX_BYTES==1000000 and b.c.MAX_NODES==50000 and a.v.MAX_STEPS==100000 and a.v.TIMEOUT==30
 review=(b.UNIT/'REVIEW.md').read_text();assert len(review.split())>2000 and len(re.findall(r'^## [0-9]+\.',review,re.M))==13 and all(row['finding_id'] in review for row in packet['source_precedence']['conflicts'])
 dag=load('continuation-dag.json');pending={row['id'] for row in dag['nodes']};done=set();assert len(pending)==18 and len(dag['edges'])==17 and dag['source']==core['source'] and dag['authority_effect']=='none'
 while pending:
  ready={name for name in pending if all(left in done for left,right in dag['edges'] if right==name)};assert ready;pending-=ready;done|=ready
 b.unchanged(prior['files']+context['sources']+dirty['refs']);return context,counts,model,source,fresh,prior
def main():
 context,counts,model,source,fresh,prior=audit();result={'schema_version':'definition-assurance-types-logic-stage/v1-candidate','result':'PASS-for-Intent-typed-candidate-stage-only','unit_id':context['unit_id'],'authority_effect':'none','goal_status':'active','source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'full_delivery_sealed':False,'counts':counts,'controls':200,'T_true_controls':73,'T_false_controls':119,'malformed_rejections':8,'nonentailment_queries':42,'actual_source_checks':99,'source_query_obligations':85,'fresh_checks':fresh,'source_files_current':201,'prior_candidate_files_preserved':10600,'last_sealed_partial_drafts':112,'working_draft_files_observed':113,'remaining_current_identities_without_draft_files_observed':70,'current_whole_inventory_refresh_complete':False,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'retained_failed_preparation_attempts':0,'retained_preparation_failure_refs':context['retained_preparation_failure_refs'],'inputs':[b.ref(b.UNIT/name) for name in INPUTS],'checker_bindings':[b.ref(b.UNIT/name) for name in ['close_types_logic_stage.py','check_types_logic_stage.py','build_candidate.py','verify_candidate.py','verify_source_checks.py']],'next_definition_after_delivery':context['next_definition_priority'],'pending':['full consumer and profile observations and accepted maps','reachable dependencies and whole113 inventory','six fresh full checks','full review, seal and separate audit','original O/E/R/J and final complete episode review']};b.put('types-logic-receipt.json',result);print(json.dumps({key:result[key] for key in ['result','controls','nonentailment_queries','actual_source_checks','prior_candidate_files_preserved','working_draft_files_observed','full_delivery_sealed','goal_status']},indent=2))
if __name__=='__main__':main()

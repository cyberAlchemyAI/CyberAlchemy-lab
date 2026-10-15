"""Freeze the exact Coordination Context typed stage; full delivery remains required."""
import json,re
import build_candidate as b
import verify_candidate as a
import verify_source_checks as s
INPUTS=['context.json','t.json','static-ir.json','correspondence.json','correspondence-check.json','denominator.json','clause-analysis.json','query-policy.json','source-query-obligation.json','comparison-selection.json','model-controls.json','source-checks.json','fresh-types-logic-results.json','REVIEW.md','CONTINUATION.md','DELIVERY-CONTEXT.md','continuation-dag.json']
EXPECTED={'source_units':20,'mapped_clauses':20,'encoded_clauses':12,'explanatory_clauses':6,'deferred_clauses':2,'declarations':174,'required_populations':23,'unresolved_populations':109,'direct_semantic_uses':28,'countermodel_queries':32}
def load(name):return json.loads((b.UNIT/name).read_bytes())
def audit():
 context=load('context.json');core=load('t.json')['payload'];packet=load('correspondence.json');counts=load('denominator.json');snapshot=b.snapshot();b.unchanged(context['sources']);b.external_current(context);assert b.r.verify(snapshot,b.ROOT)['files']==201
 prior=json.loads((b.BASE/'definitions/cal.definition.capability-realization-binding/delivery-manifest.json').read_bytes());b.unchanged(prior['files']);assert len(prior['files'])==10389
 assert context['unit_id']=='F08-T.cal.definition.coordination-context' and core['source']==context['source_selection']==b.source_ref(snapshot,'cal.definition.coordination-context') and core['source']['sha256']=='547a714a9552f83985de78b2ce228421f5102c40cacf8c1edfb48ef46366a8aa'
 assert context['pre_execution_check']['previous_separate_delivery_audit_exit_code']==context['pre_execution_check']['prepared_source_and_model_check_exit_code']==context['pre_execution_check']['prepared_independent_source_check_exit_code']==0
 work=json.loads((b.ROOT/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json').read_bytes());swu=next(row for row in work['units'] if row['id']==context['unit_id']);assert swu['outputs']==[b.ref(b.UNIT/'t.json')['path']] and swu['write_scope']==context['write_scope'] and swu['depends_on_tasks']==['A04','C01','E02'] and len(work['units'])==797
 assert not context['session_scope']['blocking_user_decisions']
 for binding in context['prerequisite_receipts']:
  b.unchanged([binding['receipt_ref']]);assert binding['result'].startswith('PASS') and json.loads((b.ROOT/binding['receipt_ref']['path']).read_bytes())['task_result']==binding['result']
 assert b.c.validate(load('t.json'),'interpretation')['status']=='structurally-valid'
 assert load('static-ir.json')==b.ir.compile_interpretation(core,snapshot) and packet['interpretation']==core
 assert not core['assumptions'] and not packet['assumption_links'] and core['source_fidelity']=='pending'
 assert counts==EXPECTED and (len(b.SORTS),len(b.CONSTANTS),len(b.FUNCTIONS),len(b.SIGNATURE))==(20,1,44,109)
 assert core['interpretation_id']=='interpretation:CoordinationContext-frame-optional-boundaries-identity-v1' and len(core['depends_on'])==28
 assert len(packet['source_precedence']['conflicts'])==21 and packet['source_precedence']['review_ref'] is None and packet['review_packet']['review_status']=='pending'
 required=[row for row in core['populations'] if row['requirement']=='required'];assert {row['population_id']:(row['carrier'],row['statement']) for row in required}=={'POP-REQ-'+name:value for name,value in b.required_populations().items()}
 assert len(core['populations'])==132 and all(row['review_ref'] is None for row in core['populations'])
 assert next(row['formal_statement'] for row in core['clauses'] if row['source_selector']=='/voices/scientific_formal/normative_statement')==b.both(*b.THEORY.values())
 analysis=load('clause-analysis.json');assert analysis['known_losses']==b.LOSSES and analysis['primitive_theory_formulas']==7 and all(analysis[key] is True for key in ['zero_bounded_context_links_allowed','owner_principals_need_not_differ','materiality_is_not_all_anchor_differences','optional_project_and_goal_independent'])
 assert all(analysis[key] is False for key in ['actual_outcome_queries_assumed_in_T','whole_prior_theories_imported','source_precedence_reviewed','mechanized_proof'])
 stack=[row['formal_statement'] for row in core['clauses'] if row['disposition']=='encoded']
 while stack:
  node=stack.pop()
  if isinstance(node,dict):
   assert not(node.get('op')=='pred' and any(node.get('name','').startswith(prefix+'Actual') for prefix in ['Context','AnchorChange','SourceViewChange']));stack.extend(node.values())
  elif isinstance(node,list):stack.extend(node)
 assert load('query-policy.json')['queries']==b.query_specs() and len(b.query_specs())==32
 model=a.verify();source=s.verify();assert model['control_count']==len(model['results'])==198 and len(model['nonentailment_countermodels'])==32
 assert (sum(row.get('primary_theory_satisfied') is True for row in model['results']),sum(row.get('primary_theory_satisfied') is False for row in model['results']),sum(row['status']=='rejected-model-structure' for row in model['results']))==(57,133,8)
 cases={row['case_id']:row for row in model['results']}
 for name in ['positive-fourteen-coordinates-optional-anchors-boundaries-material-changes-and-views','same-principal-can-own-independent-boundaries','absent-Project-unused-binding-may-be-empty','absent-Goal-unused-binding-may-be-empty','unselected-Project-reference-may-be-undeclared','unselected-Goal-reference-may-be-undeclared']:
  assert cases[name]['primary_theory_satisfied'] is cases[name]['required_population_satisfied'] is True
 for kind in ['aProduct','aProject','aGoal','aPurpose']:
  assert cases['material-inplace-successor-'+kind]['primary_theory_satisfied'] is False
  assert cases['materiality-flag-removed-'+kind]['primary_theory_satisfied'] is True and cases['materiality-flag-removed-'+kind]['required_population_satisfied'] is False
 assert len(source['checks'])==86 and source['source_query_obligations']==len(load('source-query-obligation.json')['obligations'])==74
 assert source['accepted_source_map'] is source['actual_Context_created_owned_or_authorized'] is source['semantic_ready'] is False and source['source_fidelity']=='pending'
 fresh=load('fresh-types-logic-results.json');assert [row['check'] for row in fresh]==['contract','model','source'] and all(row['exit_code']==0 and not(b.UNIT/row['stderr']).read_bytes() for row in fresh)
 assert fresh[0]['argv'][1:]==['-B',str(b.IMPL/'contracts.py'),'validate','--kind','interpretation','--input',str(b.UNIT/'t.json')]
 for row,script in zip(fresh[1:],['verify_candidate.py','verify_source_checks.py']):assert row['argv']==[fresh[0]['argv'][0],'-B',str(b.UNIT/script)] and (b.UNIT/row['stdout']).read_bytes()==(b.UNIT/(row['check']+'-stdout.txt')).read_bytes()
 assert [row['check'] for row in load('native-stage-results.json')]==['author','build','model','source']
 for name in ['author','build','model','source']:
  result=load(name+'-command-result.json');assert result['exit_code']==0 and not(b.UNIT/result['stderr']).read_bytes()
 b.unchanged(context['retained_preparation_failure_refs']+context['retained_successful_preparation_refs']);assert len(context['retained_preparation_failure_refs'])==42
 dirty=json.loads((b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261012-project/unrelated-tracked-work.json').read_bytes());assert len(dirty['refs'])==30;b.unchanged(dirty['refs'])
 assert len(list((b.BASE/'definitions').glob('*/t.json')))==111 and len(snapshot['current_entries'])==183
 assert len((b.UNIT/'t.json').read_bytes())<b.c.MAX_BYTES==1000000 and b.c.MAX_NODES==50000 and a.v.MAX_STEPS==100000 and a.v.TIMEOUT==30
 review=(b.UNIT/'REVIEW.md').read_text();assert len(review.split())>2000 and len(re.findall(r'^## [0-9]+\.',review,re.M))==13 and all(row['finding_id'] in review for row in packet['source_precedence']['conflicts'])
 dag=load('continuation-dag.json');pending={row['id'] for row in dag['nodes']};done=set();assert len(pending)==18 and len(dag['edges'])==17 and dag['source']==core['source'] and dag['authority_effect']=='none'
 while pending:
  ready={name for name in pending if all(left in done for left,right in dag['edges'] if right==name)};assert ready;pending-=ready;done|=ready
 b.unchanged(prior['files']+context['sources']+dirty['refs']);b.external_current(context)
 return context,counts,model,source,fresh,prior
def main():
 context,counts,model,source,fresh,prior=audit()
 result={'schema_version':'definition-assurance-types-logic-stage/v1-candidate','result':'PASS-for-CoordinationContext-typed-candidate-stage-only','unit_id':context['unit_id'],'authority_effect':'none','goal_status':'active','source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'full_delivery_sealed':False,'counts':counts,'controls':198,'T_true_controls':57,'T_false_controls':133,'malformed_rejections':8,'nonentailment_queries':32,'actual_source_checks':86,'source_query_obligations':74,'fresh_checks':fresh,'source_files_current':201,'prior_candidate_files_preserved':10389,'last_sealed_partial_drafts':110,'working_draft_files_observed':111,'remaining_current_identities_without_draft_files_observed':72,'current_whole_inventory_refresh_complete':False,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'retained_failed_preparation_attempts':2,'retained_preparation_failure_refs':context['retained_preparation_failure_refs'],'inputs':[b.ref(b.UNIT/name) for name in INPUTS],'checker_bindings':[b.ref(b.UNIT/name) for name in ['close_types_logic_stage.py','check_types_logic_stage.py','build_candidate.py','verify_candidate.py','verify_source_checks.py']],'next_definition_after_delivery':context['next_definition_priority'],'pending':['full consumer and profile observations and accepted maps','reachable dependencies and whole111 inventory','six fresh full checks','full review, seal and separate audit','original O/E/R/J and final episode review']}
 b.put('types-logic-receipt.json',result);print(json.dumps({key:result[key] for key in ['result','controls','nonentailment_queries','actual_source_checks','prior_candidate_files_preserved','working_draft_files_observed','full_delivery_sealed','goal_status']},indent=2))
if __name__=='__main__':main()

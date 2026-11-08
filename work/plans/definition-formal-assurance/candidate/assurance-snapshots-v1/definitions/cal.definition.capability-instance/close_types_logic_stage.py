"""Freeze CI typed logic only after actual native and fresh checks."""
import json,re
import build_candidate as b
import verify_candidate as a
import verify_source_checks as s
INPUTS=['context.json','t.json','static-ir.json','correspondence.json','correspondence-check.json','denominator.json','clause-analysis.json','query-policy.json','source-query-obligation.json','comparison-selection.json','model-controls.json','source-checks.json','fresh-types-logic-results.json','REVIEW.md','CONTINUATION.md','DELIVERY-CONTEXT.md','continuation-dag.json']
EXPECTED={'source_units':20,'mapped_clauses':20,'encoded_clauses':12,'explanatory_clauses':6,'deferred_clauses':2,'declarations':171,'required_populations':18,'unresolved_populations':100,'direct_semantic_uses':30,'countermodel_queries':28}
def load(name):return json.loads((b.UNIT/name).read_bytes())
def audit():
 context=load('context.json');core=load('t.json')['payload'];packet=load('correspondence.json');counts=load('denominator.json');snap=b.snapshot()
 b.unchanged(context['sources']);b.external_current(context);assert b.r.verify(snap,b.ROOT)['files']==201
 prior=load('../CAV2-D60/delivery-manifest.json');b.unchanged(prior['files'])
 assert len(prior['files'])==10188==context['pre_execution_check']['prior_candidate_files_preserved']
 assert context['unit_id']=='F08-T.cal.definition.capability-instance'
 assert core['source']==context['source_selection']==b.source_ref(snap,'cal.definition.capability-instance')
 assert core['source']['sha256']=='d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5'
 assert context['pre_execution_check']['previous_separate_delivery_audit_exit_code']==context['pre_execution_check']['prepared_source_and_model_check_exit_code']==0
 work=json.loads((b.ROOT/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json').read_bytes())
 swu=next(x for x in work['units'] if x['id']==context['unit_id'])
 assert swu['outputs']==[b.ref(b.UNIT/'t.json')['path']] and swu['write_scope']==context['write_scope'] and swu['depends_on_tasks']==['A04','C01','E02'] and not context['session_scope']['blocking_user_decisions']
 for ref in context['prerequisite_receipts']:
  b.unchanged([ref['receipt_ref']]);assert json.loads((b.ROOT/ref['receipt_ref']['path']).read_bytes())['task_result']==ref['result'] and ref['result'].startswith('PASS')
 assert b.c.validate(load('t.json'),'interpretation')['status']=='structurally-valid'
 assert load('static-ir.json')==b.ir.compile_interpretation(core,snap) and packet['interpretation']==core
 assert not core['assumptions'] and not packet['assumption_links'] and core['source_fidelity']=='pending'
 assert core['interpretation_id']=='interpretation:CapabilityInstance-exact-parent-owner-context-claims-recursion-handoff-v1'
 assert counts==EXPECTED and (len(b.SORTS),len(b.CONSTANTS),len(b.FUNCTIONS),len(b.SIGNATURE))==(23,3,45,100)
 assert len(core['depends_on'])==30 and len(packet['source_precedence']['conflicts'])==26 and packet['source_precedence']['review_ref'] is None
 assert packet['review_packet']['review_status']=='pending'
 req=[x for x in core['populations'] if x['requirement']=='required']
 assert {x['population_id']:(x['carrier'],x['statement']) for x in req}=={'POP-REQ-'+n:z for n,z in b.required_populations().items()}
 assert len({x['population_id'] for x in core['populations']})==118 and all(x['review_ref'] is None for x in core['populations'])
 assert next(x['formal_statement'] for x in core['clauses'] if x['source_selector']=='/voices/scientific_formal/normative_statement')==b.both(*b.THEORY.values())
 analysis=load('clause-analysis.json');assert analysis['known_losses']==b.LOSSES and analysis['primitive_theory_formulas']==7 and analysis['conditioned_authority_queries']==2
 assert all(analysis[n] is False for n in ['actual_outcome_queries_assumed_in_T','whole_prior_theories_imported','source_precedence_reviewed','mechanized_proof'])
 stack=[x['formal_statement'] for x in core['clauses'] if x['disposition']=='encoded']
 while stack:
  x=stack.pop()
  if isinstance(x,dict):
   assert not(x.get('op')=='pred' and (x.get('name','').startswith('InstanceActual') or x.get('name')=='ParentCapabilityActualAuthority'))
   stack.extend(x.values())
  elif isinstance(x,list):stack.extend(x)
 policy=load('query-policy.json')
 assert policy['queries']==b.query_specs() and len(policy['queries'])==28 and sum('does-not-imply-Authority' in x['query_id'] for x in policy['queries'])==2
 assert policy['targets_not_assumptions'] is True and policy['whole_definition_proof_claimed'] is False
 model=a.verify();source=s.verify()
 assert model['control_count']==len(model['results'])==186 and len(model['nonentailment_countermodels'])==28
 assert model['semantic_ready'] is source['semantic_ready'] is False and model['source_fidelity']==source['source_fidelity']=='pending'
 assert (sum(x.get('primary_theory_satisfied') is True for x in model['results']),sum(x.get('primary_theory_satisfied') is False for x in model['results']),sum(x['status']=='rejected-model-structure' for x in model['results']),len(source['checks']))==(57,121,8,93)
 cases={x['case_id']:x for x in model['results']}
 for name in ['selected-instance-neither-realization-nor-specialization','missing-InstanceOwnerLocalDeclared','owner-does-not-have-nominated-local-context-relation','nonempty-context-collection-handle-with-no-semantic-context','semantic-context-member-not-in-nominated-collection','instance-identity-collapses-into-parent','instance-local-lane-collapses-into-parent-lane','missing-parent-claim-lane-binding','extra-parent-claim-at-wrong-lane','selected-recursion-has-neither-budget-nor-stop','selected-excluded-ConformanceInterpretedAsAuthorityDeclared','selected-excluded-ParentClaimGrantsInstanceAuthorityDeclared']:
  assert cases[name]['primary_theory_satisfied'] is False
 for name in ['realization-specialization-owner-context-claims-budget-stop-and-handoff','independent-second-parent-actual-authority','unused-parent-version-binding-absent','budget-only-unused-stop-binding-absent','stop-only-unused-budget-binding-absent','unused-version-handle-empty','unused-parent-handle-empty','unused-recursion-handle-empty','budget-only-unused-stop-handle-empty','stop-only-unused-budget-handle-empty']:
  assert cases[name]['primary_theory_satisfied'] is cases[name]['required_population_satisfied'] is True
 for name in ['no-selected-instance','no-independent-actual-authority','no-actual-conformance-population','no-parent-actual-authority-population','realization-specialization-overlap-removed-but-genus-preserved','single-semantic-context-remains-sufficient','recursion-overlap-removed-budget-remains-sufficient']:
  assert cases[name]['primary_theory_satisfied'] is True and cases[name]['required_population_satisfied'] is False
 assert source['source']==core['source'] and source['projection_bytes']==4095 and source['accepted_source_map'] is False
 assert source['actual_CapabilityInstance_instantiated_adopted_bound_or_conformant'] is False
 assert len(source['source_body_upstreams'])==len(source['external_file_refs'])==2
 assert {x['declared_selector']:x['selected_sha256'] for x in source['external_file_refs']}=={'CAV2-D64':'891c6b66c578bc0b8f763ad15e250fea255aed36274b9799436f6ab9544dd080','CAV2-D67':'bf8f3cb9b7d22aaa3c54b7c1eb177b85100be9bc421142bb3ead7e2456431d13'}
 assert len(load('source-query-obligation.json')['obligations'])==63
 fresh=load('fresh-types-logic-results.json')
 assert [x['check'] for x in fresh]==['contract','model','source'] and all(x['exit_code']==0 and not(b.UNIT/x['stderr']).read_bytes() for x in fresh)
 assert fresh[0]['argv'][1:]==['-B',str(b.IMPL/'contracts.py'),'validate','--kind','interpretation','--input',str(b.UNIT/'t.json')]
 for x,script in zip(fresh[1:],['verify_candidate.py','verify_source_checks.py']):
  assert x['argv']==[fresh[0]['argv'][0],'-B',str(b.UNIT/script)] and (b.UNIT/x['stdout']).read_bytes()==(b.UNIT/(x['check']+'-stdout.txt')).read_bytes()
 for name in ['author','build','model','source']:
  cmd=load(name+'-command-result.json');assert cmd['exit_code']==0 and not(b.UNIT/cmd['stderr']).read_bytes()
 b.unchanged(context['retained_preparation_failure_refs']+context['retained_successful_preparation_refs'])
 assert len(context['retained_preparation_failure_refs'])==5 and len(context['retained_successful_preparation_refs'])==9 and not context['retained_successful_native_stage_refs']
 assert len(list((b.BASE/'definitions').glob('*/t.json')))==109 and not(b.BASE/'definitions/cal.definition.capability-realization-binding').exists()
 assert len((b.UNIT/'t.json').read_bytes())<b.c.MAX_BYTES==1000000 and b.c.MAX_NODES==50000 and a.v.MAX_STEPS==100000 and a.v.TIMEOUT==30
 review=(b.UNIT/'REVIEW.md').read_text()
 assert len(review.split())>2000 and len(re.findall(r'^## [0-9]+\.',review,re.M))==13 and all(x['finding_id'] in review for x in packet['source_precedence']['conflicts'])
 dag=load('continuation-dag.json');nodes={x['id'] for x in dag['nodes']};edges=[tuple(x) for x in dag['edges']]
 assert len(nodes)==len(edges)==18 and all(x in nodes and y in nodes for x,y in edges) and dag['authority_effect']=='none'
 pending=set(nodes);done=set()
 while pending:
  ready={n for n in pending if all(x in done for x,y in edges if y==n)};assert ready;done|=ready;pending-=ready
 b.unchanged(prior['files']+context['sources']);b.external_current(context)
 return context,counts,model,source,fresh,prior
def main():
 context,counts,model,source,fresh,prior=audit()
 review_failure=b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261012-capability-instance/retained-review-heading-pattern-1'
 review_failure_refs=[b.ref(q) for q in sorted(review_failure.rglob('*')) if q.is_file()]
 assert len(review_failure_refs)==6 and json.loads((review_failure/'command-result.json').read_bytes())['exit_code']==1
 report={'schema_version':'definition-assurance-types-logic-stage/v1-candidate','result':'PASS-for-typed-candidate-stage-only','unit_id':context['unit_id'],'authority_effect':'none','goal_status':'active','source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'full_delivery_sealed':False,'counts':counts,'controls':186,'T_true_controls':57,'T_false_controls':121,'malformed_rejections':8,'nonentailment_queries':28,'source_conditioned_queries':2,'actual_source_checks':93,'source_query_obligations':63,'fresh_checks':fresh,'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),'last_sealed_partial_drafts':108,'working_draft_files_observed':109,'current_whole_inventory_refresh_complete':False,'remaining_current_identities_without_draft_files_observed':74,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'pending':['currentinstance/parent/context/authority/construction/recursion/handoffconsumer maps','profilesandreachable dependencies','whole109draftinventory refresh','sixfreshfullchecks','fullreview/seal/separateaudit'],'next_definition_after_delivery':'F08-T.cal.definition.capability-realization-binding','retained_preparation_failure_refs':context['retained_preparation_failure_refs'],'retained_failed_prepared_syntax':1,'retained_failed_prepared_semantic_controls':0,'retained_failed_native_attempts':[],'retained_review_writer_failure_refs':review_failure_refs,'retained_review_writer_failures':1,'inputs':[b.ref(b.UNIT/name) for name in INPUTS],'checker_bindings':[b.ref(b.UNIT/name) for name in ['close_types_logic_stage.py','check_types_logic_stage.py','build_candidate.py','verify_candidate.py','verify_source_checks.py']]}
 b.put('types-logic-receipt.json',report)
 print(json.dumps({k:report[k] for k in ['result','controls','nonentailment_queries','source_conditioned_queries','actual_source_checks','prior_candidate_files_preserved','working_draft_files_observed','full_delivery_sealed','goal_status']},indent=2))
if __name__=='__main__':main()


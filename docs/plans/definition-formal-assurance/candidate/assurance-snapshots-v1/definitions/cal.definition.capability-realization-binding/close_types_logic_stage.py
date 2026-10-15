"""Freeze exact CRB typed inputs after actual native and fresh checks, preserving full scope."""
import json,re
import build_candidate as b
import verify_candidate as a
import verify_source_checks as s
INPUTS=['context.json','t.json','static-ir.json','correspondence.json','correspondence-check.json','denominator.json','clause-analysis.json','query-policy.json','source-query-obligation.json','comparison-selection.json','model-controls.json','source-checks.json','fresh-types-logic-results.json','REVIEW.md','CONTINUATION.md','DELIVERY-CONTEXT.md','continuation-dag.json']
EXPECTED={'source_units':23,'mapped_clauses':23,'encoded_clauses':14,'explanatory_clauses':6,'deferred_clauses':3,'declarations':176,'required_populations':19,'unresolved_populations':105,'direct_semantic_uses':27,'countermodel_queries':33}
def load(name):return json.loads((b.UNIT/name).read_bytes())
def audit():
 context=load('context.json');core=load('t.json')['payload'];packet=load('correspondence.json');counts=load('denominator.json');snapshot=b.snapshot()
 b.unchanged(context['sources']);b.external_current(context);assert b.r.verify(snapshot,b.ROOT)['files']==201
 prior=load('../cal.definition.capability-instance/delivery-manifest.json');b.unchanged(prior['files']);assert len(prior['files'])==10287
 assert context['unit_id']=='F08-T.cal.definition.capability-realization-binding' and core['source']==context['source_selection']==b.source_ref(snapshot,'cal.definition.capability-realization-binding')
 assert core['source']['sha256']=='8a0f907bb854371b8946e071c9d01702de3f35799405cb8b0ee66e546990b1bd'
 assert context['pre_execution_check']['previous_separate_delivery_audit_exit_code']==context['pre_execution_check']['prepared_source_and_model_check_exit_code']==0
 work=load('../../../../foundations-first-v1/swu-manifest.json') if False else json.loads((b.ROOT/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json').read_bytes())
 swu=next(x for x in work['units'] if x['id']==context['unit_id']);assert swu['outputs']==[b.ref(b.UNIT/'t.json')['path']] and swu['write_scope']==context['write_scope'] and swu['depends_on_tasks']==['A04','C01','E02']
 assert len(work['units'])==797 and not context['session_scope']['blocking_user_decisions']
 for ref in context['prerequisite_receipts']:
  b.unchanged([ref['receipt_ref']]);assert load_relative(ref['receipt_ref']['path'])['task_result']==ref['result'] and ref['result'].startswith('PASS')
 assert b.c.validate(load('t.json'),'interpretation')['status']=='structurally-valid'
 assert load('static-ir.json')==b.ir.compile_interpretation(core,snapshot) and packet['interpretation']==core
 assert not core['assumptions'] and not packet['assumption_links'] and core['source_fidelity']=='pending'
 assert counts==EXPECTED and (len(b.SORTS),len(b.CONSTANTS),len(b.FUNCTIONS),len(b.SIGNATURE))==(20,5,46,105)
 assert core['interpretation_id']=='interpretation:CapabilityRealizationBinding-exact-association-projection-succession-v1'
 assert len(core['depends_on'])==27 and len(packet['source_precedence']['conflicts'])==22 and packet['source_precedence']['review_ref'] is None and packet['review_packet']['review_status']=='pending'
 required=[x for x in core['populations'] if x['requirement']=='required'];assert {x['population_id']:(x['carrier'],x['statement']) for x in required}=={'POP-REQ-'+n:z for n,z in b.required_populations().items()}
 assert len(core['populations'])==124 and all(x['review_ref'] is None for x in core['populations'])
 assert next(x['formal_statement'] for x in core['clauses'] if x['source_selector']=='/voices/scientific_formal/normative_statement')==b.both(*b.THEORY.values())
 analysis=load('clause-analysis.json');assert analysis['known_losses']==b.LOSSES and analysis['primitive_theory_formulas']==8 and analysis['implementation_member_change_is_extensional'] is analysis['evidence_roles_share_common_collection_carrier'] is analysis['projection_optional'] is analysis['successor_distinct_only_when_required_change'] is True
 assert all(analysis[n] is False for n in ['actual_outcome_queries_assumed_in_T','whole_prior_theories_imported','source_precedence_reviewed','mechanized_proof','actual_digest_authenticity_proved'])
 stack=[x['formal_statement'] for x in core['clauses'] if x['disposition']=='encoded']
 while stack:
  node=stack.pop()
  if isinstance(node,dict):
   assert not(node.get('op')=='pred' and any(node.get('name','').startswith(x+'Actual') for x in ['Binding','Projection','Change']));stack.extend(node.values())
  elif isinstance(node,list):stack.extend(node)
 assert load('query-policy.json')['queries']==b.query_specs() and len(b.query_specs())==33
 model=a.verify();source=s.verify()
 assert model['control_count']==len(model['results'])==201 and len(model['nonentailment_countermodels'])==33
 assert (sum(x.get('primary_theory_satisfied') is True for x in model['results']),sum(x.get('primary_theory_satisfied') is False for x in model['results']),sum(x['status']=='rejected-model-structure' for x in model['results']))==(57,136,8)
 cases={x['case_id']:x for x in model['results']}
 for name in ['exact-association-members-authority-evidence-projection-and-changes','no-change-successor-reference-may-be-original','no-change-unused-successor-binding-absent','without-projection-unused-projection-binding-absent','without-projection-unused-digest-binding-absent','unused-digest-handle-empty','unused-projection-handle-empty']:
  assert cases[name]['primary_theory_satisfied'] is cases[name]['required_population_satisfied'] is True
 for name in ['no-selected-bindings-projections-or-changes','optional-projections-all-absent','no-selected-changes','all-endpoint-collections-singleton','separate-evidence-contents-permitted','Implementation-member-change-removed-no-successor-required']:
  assert cases[name]['primary_theory_satisfied'] is True and cases[name]['required_population_satisfied'] is False
 for name in ['nonempty-collection-handle-with-no-endpoints','second-canonical-authority-for-association','evidence-purpose-role-collapsed','projection-second-writable-authority','projection-digest-differs','changed-state-inplace-successor-cCap','changed-state-inplace-successor-cImpl','changed-state-inplace-successor-cPosture']:
  assert cases[name]['primary_theory_satisfied'] is False
 assert len(source['checks'])==85 and source['source_query_obligations']==len(load('source-query-obligation.json')['obligations'])==73 and source['projection_bytes']==5106
 assert source['accepted_source_map'] is source['actual_Binding_adopted_deployed_conformant_or_authorized'] is source['semantic_ready'] is False and source['source_fidelity']=='pending'
 fresh=load('fresh-types-logic-results.json');assert [x['check'] for x in fresh]==['contract','model','source'] and all(x['exit_code']==0 and not(b.UNIT/x['stderr']).read_bytes() for x in fresh)
 assert fresh[0]['argv'][1:]==['-B',str(b.IMPL/'contracts.py'),'validate','--kind','interpretation','--input',str(b.UNIT/'t.json')]
 for row,script in zip(fresh[1:],['verify_candidate.py','verify_source_checks.py']):assert row['argv']==[fresh[0]['argv'][0],'-B',str(b.UNIT/script)] and (b.UNIT/row['stdout']).read_bytes()==(b.UNIT/(row['check']+'-stdout.txt')).read_bytes()
 for name in ['author','build','model','source']:
  result=load(name+'-command-result.json');assert result['exit_code']==0 and not(b.UNIT/result['stderr']).read_bytes()
 b.unchanged(context['retained_preparation_failure_refs']+context['retained_successful_preparation_refs']);assert len(context['retained_preparation_failure_refs'])==26
 source_failure=b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261012-capability-realization-binding/retained-native-source-check-1';assert json.loads((source_failure/'observation.json').read_bytes())['actual_exit_code']==1
 assert len(list((b.BASE/'definitions').glob('*/t.json')))==110 and not(b.BASE/'definitions/cal.definition.coordination-context').exists()
 assert len((b.UNIT/'t.json').read_bytes())<b.c.MAX_BYTES==1000000 and b.c.MAX_NODES==50000 and a.v.MAX_STEPS==100000 and a.v.TIMEOUT==30
 review=(b.UNIT/'REVIEW.md').read_text();assert len(review.split())>2000 and len(re.findall(r'^## [0-9]+\.',review,re.M))==13 and all(x['finding_id'] in review for x in packet['source_precedence']['conflicts'])
 dag=load('continuation-dag.json');pending={x['id'] for x in dag['nodes']};done=set();assert len(pending)==len(dag['edges'])==18 and dag['source']==core['source'] and dag['authority_effect']=='none'
 while pending:
  ready={n for n in pending if all(left in done for left,right in dag['edges'] if right==n)};assert ready;pending-=ready;done|=ready
 b.unchanged(prior['files']+context['sources']);b.external_current(context)
 return context,counts,model,source,fresh,prior
def load_relative(path):return json.loads((b.ROOT/path).read_bytes())
def main():
 context,counts,model,source,fresh,prior=audit();p=b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261012-capability-realization-binding';failed=[b.ref(q) for q in sorted((p/'retained-native-source-check-1').rglob('*')) if q.is_file()]
 assert len(failed)==8
 result={'schema_version':'definition-assurance-types-logic-stage/v1-candidate','result':'PASS-for-CRB-typed-candidate-stage-only','unit_id':context['unit_id'],'authority_effect':'none','goal_status':'active','source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'full_delivery_sealed':False,'counts':counts,'controls':201,'T_true_controls':57,'T_false_controls':136,'malformed_rejections':8,'nonentailment_queries':33,'actual_source_checks':85,'source_query_obligations':73,'fresh_checks':fresh,'source_files_current':201,'prior_candidate_files_preserved':10287,'last_sealed_partial_drafts':109,'working_draft_files_observed':110,'remaining_current_identities_without_draft_files_observed':73,'current_whole_inventory_refresh_complete':False,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'retained_prepared_model_construction_failures':1,'retained_native_source_check_failures':1,'retained_preparation_failure_refs':context['retained_preparation_failure_refs'],'retained_source_check_failure_refs':failed,'inputs':[b.ref(b.UNIT/name) for name in INPUTS],'checker_bindings':[b.ref(b.UNIT/name) for name in ['close_types_logic_stage.py','check_types_logic_stage.py','build_candidate.py','verify_candidate.py','verify_source_checks.py']],'next_definition_after_delivery':'F08-T.cal.definition.coordination-context','pending':['fullconsumer/profile observations andaccepted maps','reachabledependencies andwhole110 inventory','sixfreshfullchecks','fullreview/seal/separateaudit','originalO/E/R/J andfinal episode review']}
 b.put('types-logic-receipt.json',result);print(json.dumps({k:result[k] for k in ['result','controls','nonentailment_queries','actual_source_checks','prior_candidate_files_preserved','working_draft_files_observed','full_delivery_sealed','goal_status']},indent=2))
if __name__=='__main__':main()

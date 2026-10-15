"""Exact RR typed freeze and separate independent audit;full delivery remains pending."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.representation-revision')
freeze='''"""Exact current C28 Representation Revision typed candidate stage."""
import json,re
import build_candidate as b
import verify_candidate as a
import verify_source_checks as s
INPUTS=['context.json','t.json','static-ir.json','correspondence.json','correspondence-check.json','denominator.json','clause-analysis.json','query-policy.json','source-query-obligation.json','comparison-selection.json','model-controls.json','source-checks.json','fresh-types-logic-results.json','REVIEW.md','CONTINUATION.md','DELIVERY-CONTEXT.md']
EXPECTED={'source_units':30,'mapped_clauses':30,'encoded_clauses':17,'explanatory_clauses':11,'deferred_clauses':2,'declarations':217,'required_populations':11,'unresolved_populations':130,'direct_semantic_uses':23,'countermodel_queries':36}
def load(n):return json.loads((b.UNIT/n).read_bytes())
def audit():
 context=load('context.json');core=load('t.json')['payload'];packet=load('correspondence.json');counts=load('denominator.json');snap=b.snapshot();b.unchanged(context['sources']);b.external_current(context);assert b.r.verify(snap,b.ROOT)['files']==201
 prior=load('../cal.definition.projection-specification/delivery-manifest.json');b.unchanged(prior['files']);assert len(prior['files'])==8509==context['pre_execution_check']['prior_candidate_files_preserved'] and context['pre_execution_check']['previous_separate_delivery_audit_exit_code']==0
 assert context['unit_id']=='F04-T.cal.definition.representation-revision' and core['source']==context['source_selection']==b.source_ref(snap,'cal.definition.representation-revision') and core['source']['sha256']=='5bb818e70b0281dc14edcd4dade418335f50df93bc30c607823ecce5b3349850'
 work=json.loads((b.ROOT/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json').read_bytes());swu=next(x for x in work['units'] if x['id']==context['unit_id']);assert swu['outputs']==[b.ref(b.UNIT/'t.json')['path']] and swu['write_scope']==context['write_scope'] and swu['depends_on_tasks']==['A04','C01','E02'] and not context['session_scope']['blocking_user_decisions']
 for x in context['prerequisite_receipts']:
  b.unchanged([x['receipt_ref']]);assert json.loads((b.ROOT/x['receipt_ref']['path']).read_bytes())['task_result']==x['result'] and x['result'].startswith('PASS')
 b.c.validate(load('t.json'),'interpretation');assert load('static-ir.json')==b.ir.compile_interpretation(core,snap) and packet['interpretation']==core and packet['source_selection']=='current' and not core['assumptions'] and not packet['assumption_links'] and core['source_fidelity']=='pending'
 assert counts==EXPECTED and (len(b.SORTS),len(b.CONSTANTS),len(b.FUNCTIONS),len(b.SIGNATURE),len(core['declarations']))==(22,1,64,130,217) and len(core['depends_on'])==23 and len(packet['source_precedence']['conflicts'])==22 and packet['source_precedence']['review_ref'] is None and packet['review_packet']['review_status']=='pending'
 required=[x for x in core['populations'] if x['requirement']=='required'];assert {x['population_id']:x['statement'] for x in required}=={'POP-'+n:z for n,z in b.required_populations().items()} and all(x['carrier']=='RevisionReference' and x['review_ref'] is None for x in required) and all(x['review_ref'] is None for x in core['populations'])
 assert b.FUNCTIONS['revisionBefore']==(['RevisionReference'],'RepresentationReference') and b.FUNCTIONS['stateDigest']==(['ByteStateReference'],'DigestReference') and b.SIGNATURE['ExactPrePostDeclared']==['RevisionReference','RepresentationReference','RepresentationReference'] and b.FUNCTIONS['selectionEvidence']==(['OwnerSelectionReference'],'EquivalenceEvidenceReference')
 analysis=load('clause-analysis.json');assert analysis['known_losses']==b.LOSSES and analysis['primitive_theory_formulas']==12 and analysis['unique_encoded_source_formula_values']==10 and analysis['normative_formal_support_composition']=='necessary-guards-source-precedence-owner-pending' and analysis['state_and_digest_equality']=='distinct-declared-guards-not-hash-computation-or-injectivity' and analysis['representation_change_dimensions']=='inclusive-OR-of-four-exact-selector-differences' and analysis['validation']=='recorded-explicit-reference-not-invented-PASS-or-actual-execution' and all(analysis[n] is False for n in ['actual_outcome_queries_assumed_in_T','whole_prior_theories_imported','source_precedence_reviewed','mechanized_proof'])
 stack=[x['formal_statement'] for x in core['clauses'] if x['disposition']=='encoded']
 while stack:
  x=stack.pop()
  if isinstance(x,dict):assert not (x.get('op')=='pred' and x.get('name','').startswith('RevisionActual'));stack.extend(x.values())
  elif isinstance(x,list):stack.extend(x)
 model=a.verify();source=s.verify();assert model['control_count']==len(model['results'])==266 and len(model['nonentailment_countermodels'])==36 and model['semantic_ready'] is False and source['semantic_ready'] is False and model['source_fidelity']==source['source_fidelity']=='pending'
 assert (sum(x.get('primary_theory_satisfied') is True for x in model['results']),sum(x.get('primary_theory_satisfied') is False for x in model['results']),sum(x['status']=='rejected-model-structure' for x in model['results']),len(source['checks']))==(59,199,8,58)
 cases={x['case_id']:x for x in model['results']}
 for n in ['changed-meaning-with-same-label','hidden-conflicting-prepost','missing-exact-prepost','different-states-with-equal-declared-digest','different-digest-for-one-declared-state','changed-bytes-with-no-declared-dimension','support-endpoint-mismatch-selectionEvidence','support-endpoint-mismatch-rollbackAfter','selected-excluded-CreatesSemanticSuccessorLineageDeclared','selected-excluded-CreatesContextLineageDeclared','selected-excluded-InPlaceDecisionBoundMutationDeclared','missing-posture-RepresentationHistoricalDeclared-a0','missing-posture-OwnerSelectionRecordedDeclared-selection0']:assert cases[n]['primary_theory_satisfied'] is False
 for n in ['exact-representation-revisions','duplicate-declared-revision-identity-not-forced-injective','all-four-change-dimensions-permitted','outside-prepost-unconstrained','outside-excluded-CreatesSemanticSuccessorLineageDeclared','independently-supported-actual-MeaningEquivalence','independently-supported-actual-RollbackSuccess','independently-supported-actual-Authority']:assert cases[n]['primary_theory_satisfied'] is True and cases[n]['required_population_satisfied'] is True
 for n in ['no-selected-revisions','only-first-revision-selected','schema-only-witness-not-source-wide-policy','independent-authority-not-supplied','all-actual-outcomes-independently-supplied']:assert cases[n]['primary_theory_satisfied'] is True and cases[n]['required_population_satisfied'] is False
 assert source['current_registry_admission_ref']=='CAL-DECISION-0028-CRAFT-FOUNDATION-V1' and source['all_local_upstream_source_bytes_verified'] is True and len(source['recorded_local_source_observations'])==2 and source['external_source_observations']==source['external_file_refs']==[] and source['projection_bytes']==4652 and source['first_render_sha256']==source['second_render_sha256']==b.r.digest((b.UNIT/'source-render-1.md').read_bytes())==b.r.digest((b.UNIT/'source-render-2.md').read_bytes())=='07e6cf51fd762e32866970e16fa92ddeff357a96e4f188d4ebe026be17969cd5'
 assert len(load('source-query-obligation.json')['obligations'])==33 and len(load('query-policy.json')['queries'])==36 and all(x['selected_in_T'] is False for x in load('query-policy.json')['queries'])
 fresh=load('fresh-types-logic-results.json');assert [x['check'] for x in fresh]==['contract','model','source'] and all(x['exit_code']==0 and not (b.UNIT/x['stderr']).read_bytes() for x in fresh)
 assert fresh[0]['argv'][1:]==[str(b.IMPL/'contracts.py'),'validate','--kind','interpretation','--input',str(b.UNIT/'t.json')]
 for x,script in zip(fresh[1:],['verify_candidate.py','verify_source_checks.py']):assert x['argv']==[fresh[0]['argv'][0],str(b.UNIT/script)] and (b.UNIT/x['stdout']).read_bytes()==(b.UNIT/(x['check']+'-stdout.txt')).read_bytes()
 for stem in ['author','build','model','source']:
  cmd=load(stem+'-command-result.json');assert cmd['exit_code']==0 and not (b.UNIT/cmd['stderr']).read_bytes()
 assert context['retained_preparation_failure_refs']==[] and len(list((b.BASE/'definitions').glob('*/t.json')))==95 and not (b.BASE/'definitions/cal.definition.schema-evolution-invariant').exists()
 assert len((b.UNIT/'t.json').read_bytes())==286979<b.c.MAX_BYTES==1000000 and b.c.MAX_NODES==50000 and a.v.MAX_STEPS==100000 and a.v.TIMEOUT==30
 review=(b.UNIT/'REVIEW.md').read_text();assert len(review.split())>2500 and len(re.findall(r'^## [0-9]+\\.',review,re.M))==13 and all('RR-FINDING-'+str(i).zfill(3) in review for i in range(1,23))
 diagram=review.split('```mermaid\\n')[1].split('```')[0];edges=re.findall(r'^ ([A-Z]+)(?:\\[.*?\\])? --> ([A-Z]+)',diagram,re.M);nodes={n for pair in edges for n in pair};assert nodes==set('S A T B I C R F V H P D J E Q N X'.split()) and len(edges)==17;pending=set(nodes);done=set()
 while pending:
  ready={n for n in pending if all(x in done for x,y in edges if y==n)};assert ready;done|=ready;pending-=ready
 b.unchanged(prior['files']+context['sources']);b.external_current(context);return context,counts,model,source,fresh,prior
def main():
 context,counts,model,source,fresh,prior=audit();report={'schema_version':'definition-assurance-types-logic-stage/v1-candidate','result':'PASS-for-typed-candidate-stage-only','unit_id':context['unit_id'],'authority_effect':'none','goal_status':'active','source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'full_delivery_sealed':False,'counts':counts,'controls':266,'T_true_controls':59,'T_false_controls':199,'malformed_rejections':8,'nonentailment_queries':36,'actual_source_checks':58,'source_query_obligations':33,'fresh_checks':fresh,'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),'last_sealed_partial_drafts':94,'working_draft_files_observed':95,'current_whole_inventory_refresh_complete':False,'remaining_current_identities_without_draft_files_observed':88,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'pending':['current carrier and consumer mapping','reachable dependencies and current whole inventory','six fresh delivery checks','full delivery review,seal and separate audit'],'next_definition_after_delivery':'F04-T.cal.definition.schema-evolution-invariant','retained_preparation_failure_refs':context['retained_preparation_failure_refs'],'retained_failed_native_attempts':[],'retained_successful_prior_stage_refs':[],'retained_failed_typed_stage_refs':[],'producer_results':[b.ref(b.UNIT/(stem+'-command-result.json')) for stem in ['author','build','model','source']],'inputs':[b.ref(b.UNIT/n) for n in INPUTS]};b.put('types-logic-receipt.json',report);print(json.dumps({k:report[k] for k in ['result','controls','nonentailment_queries','source_files_current','prior_candidate_files_preserved','working_draft_files_observed','full_delivery_sealed','goal_status']},indent=2))
if __name__=='__main__':main()
'''
check='''"""Separate exact RR types-and-logic audit; no full delivery or accepted semantics."""
import json
import build_candidate as b
import close_types_logic_stage as stage
def main():
 context,counts,model,source,fresh,prior=stage.audit();receipt=stage.load('types-logic-receipt.json');b.unchanged(receipt['inputs']+receipt['producer_results']+receipt['retained_preparation_failure_refs']);assert receipt['result']=='PASS-for-typed-candidate-stage-only' and len(receipt['inputs'])==16 and receipt['full_delivery_sealed'] is False and receipt['semantic_ready'] is False and receipt['source_fidelity']=='pending' and receipt['retained_failed_native_attempts']==receipt['retained_failed_typed_stage_refs']==receipt['retained_preparation_failure_refs']==receipt['retained_successful_prior_stage_refs']==[] and receipt['counts']==counts and receipt['controls']==266 and receipt['nonentailment_queries']==36 and receipt['actual_source_checks']==58 and receipt['source_query_obligations']==33
 print(json.dumps({'result':'PASS-separate-RepresentationRevision-typed-stage-audit','frozen_inputs':16,'controls':266,'nonentailment_queries':36,'prior_candidate_files_preserved':8509,'source_files_current':201,'working_drafts':95,'last_full_inventory_partial_drafts':94,'whole_inventory_refresh_complete':False,'whole_definition_proofs':0,'owner_accepted_whole_translations':0,'retained_native_failures':0,'goal_status':'active'},indent=2))
if __name__=='__main__':main()
'''
for n,s in [('close_types_logic_stage.py',freeze),('check_types_logic_stage.py',check)]:
 ast.parse(s)
 with (u/n).open('x') as f:f.write(s)
s=Path('docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261011-projection-specification/capture_typed_stage.py').read_text().replace('cal.definition.projection-specification','cal.definition.representation-revision')
with (p/'capture_typed_stage.py').open('x') as f:f.write(s)
print('Prepared sixteen-input RR types-logic freeze and separate actual audit.')

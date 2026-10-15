"""Prepare exact sixteen-input Withdrawal Record typed freeze and separate audit."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.withdrawal-record')
s='''"""Exact C66 Withdrawal Record typed-stage audit,conditional queries and retained evidence."""
import json,re
import build_candidate as b
import verify_candidate as a
import verify_source_checks as s
INPUTS=['context.json','t.json','static-ir.json','correspondence.json','correspondence-check.json','denominator.json','clause-analysis.json','query-policy.json','source-query-obligation.json','comparison-selection.json','model-controls.json','source-checks.json','fresh-types-logic-results.json','REVIEW.md','CONTINUATION.md','DELIVERY-CONTEXT.md']
EXPECTED={'source_units':24,'mapped_clauses':24,'encoded_clauses':16,'explanatory_clauses':6,'deferred_clauses':2,'declarations':173,'required_populations':17,'unresolved_populations':121,'direct_semantic_uses':21,'countermodel_queries':34}
def load(n):return json.loads((b.UNIT/n).read_bytes())
def retained_successes():
 refs=[]
 for p in (b.UNIT/'attempts').glob('*/stage.json'):
  d=json.loads(p.read_bytes());b.unchanged(d['files']);assert d['status']=='retained-successful-prior-query-stage' and d['producer_exit_code']==0 and d['primary_theory_changed'] is False and d['scope_or_population_denominator_changed'] is False;refs.append(b.ref(p))
 assert len(refs)==2;return refs
def queries():
 expected=[]
 for n in b.ACTUAL:
  condition=None;label='all-selected-records'
  if n in ['DigestAvailability','DigestFidelity']:condition=b.pred('RecordDigestAvailableDeclared',b.R);label='declared-digest-available'
  elif n in ['SuccessorExistence','SuccessorResolution','SuccessorIdentity','SuccessorAdmission']:condition=b.pred('RecordSuccessorClaimedDeclared',b.R);label='claimed-successor'
  elif n in ['RecoveryRuleAuthority','Restoration']:condition=b.pred('RecordExplicitRecoverySelectedDeclared',b.R);label='explicit-higher-order-recovery-selected'
  elif n=='NoIdentifierReuse':condition=b.pred('RecordEffectiveDeclared',b.R);label='declared-effective-record'
  elif n=='HistoricalAvailability':condition=b.pred('SubjectInactiveDeclared',b.SUBJECT);label='declared-inactive-subject'
  scope=b.APP if condition is None else b.both(b.APP,condition);expected.append({'query_id':'Record-not-Actual'+n,'target':b.allof([('WithdrawalRecordReference','r')],b.implies(scope,b.pred('RecordActual'+n,b.R))),'witness_condition':b.exists([('WithdrawalRecordReference','r')],b.both(scope,b.neg(b.pred('RecordActual'+n,b.R)))),'source_condition':label,'selected_in_T':False,'source_fidelity':'pending'})
 return expected
def audit():
 context=load('context.json');core=load('t.json')['payload'];packet=load('correspondence.json');counts=load('denominator.json');snap=b.snapshot();b.unchanged(context['sources']);b.external_current(context);assert b.r.verify(snap,b.ROOT)['files']==201
 prior=load('../cal.definition.semantic-epoch/delivery-manifest.json');b.unchanged(prior['files']);assert len(prior['files'])==8847==context['pre_execution_check']['prior_candidate_files_preserved'] and context['pre_execution_check']['previous_separate_delivery_audit_exit_code']==0
 assert context['unit_id']=='F04-T.cal.definition.withdrawal-record' and core['source']==context['source_selection']==b.source_ref(snap,'cal.definition.withdrawal-record') and core['source']['sha256']=='f929f75cda1bf96791c2756b481ae55cb58559fdc98d105871c5b6d8b3906571'
 work=json.loads((b.ROOT/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json').read_bytes());swu=next(x for x in work['units'] if x['id']==context['unit_id']);assert swu['outputs']==[b.ref(b.UNIT/'t.json')['path']] and swu['write_scope']==context['write_scope'] and swu['depends_on_tasks']==['A04','C01','E02'] and not context['session_scope']['blocking_user_decisions']
 for x in context['prerequisite_receipts']:
  b.unchanged([x['receipt_ref']]);assert json.loads((b.ROOT/x['receipt_ref']['path']).read_bytes())['task_result']==x['result'] and x['result'].startswith('PASS')
 assert b.c.validate(load('t.json'),'interpretation')['status']=='structurally-valid' and load('static-ir.json')==b.ir.compile_interpretation(core,snap) and packet['interpretation']==core and packet['source_selection']=='current' and not core['assumptions'] and not packet['assumption_links'] and core['source_fidelity']=='pending'
 assert counts==EXPECTED and (len(b.SORTS),len(b.CONSTANTS),len(b.FUNCTIONS),len(b.SIGNATURE),len(core['declarations']))==(16,1,35,121,173) and len(core['depends_on'])==21 and len(packet['source_precedence']['conflicts'])==22 and packet['source_precedence']['review_ref'] is None and packet['review_packet']['review_status']=='pending'
 required=[x for x in core['populations'] if x['requirement']=='required'];unresolved=[x for x in core['populations'] if x['requirement']=='unresolved'];assert {x['population_id']:(x['carrier'],x['statement']) for x in required}=={'POP-REQ-'+n:z for n,z in b.required_populations().items()} and all(x['review_ref'] is None for x in core['populations']) and {x['carrier'] for x in required}=={'WithdrawalRecordReference'} and len(unresolved)==121 and len({x['population_id'] for x in core['populations']})==138 and all(x['population_id'].startswith('POP-UNRESOLVED-') for x in unresolved)
 assert b.FUNCTIONS['recordIdentifier']==(['WithdrawalRecordReference'],'IdentifierReference') and b.FUNCTIONS['recordSubject']==(['WithdrawalRecordReference'],'SubjectReference') and b.FUNCTIONS['subjectLastKnownDigest']==(['SubjectReference'],'DigestReference') and b.FUNCTIONS['successorAdmissionState']==(['SuccessorReference'],'AdmissionStateReference') and b.SIGNATURE['RecoveryRuleAppliesToIdentifierDeclared']==['RecoveryRuleReference','IdentifierReference'] and b.FUNCTIONS['historyRecord']==(['HistoricalResolutionReference'],'WithdrawalRecordReference')
 assert next(x['formal_statement'] for x in core['clauses'] if x['source_selector']=='/voices/scientific_formal/normative_statement')==b.both(*b.THEORY.values()) and len(b.THEORY)==9 and isinstance(b.BASE,b.Path)
 analysis=load('clause-analysis.json');assert analysis['known_losses']==b.LOSSES and analysis['primitive_theory_formulas']==9 and analysis['digest']=='conditional-declared-availability-and-exact-subject-last-known-reference' and analysis['successor']=='optional-with-independent-declared-resolution-own-identity-admission' and analysis['reservation']=='declared-permanent-unless-explicit-higher-order-recovery-selected' and analysis['reuse']=='rejected-while-effective-even-if-restoration-exception-selected' and analysis['history']=='declared-resolution-without-subject-load-and-after-subject-inactivity' and all(analysis[n] is False for n in ['actual_outcome_queries_assumed_in_T','whole_prior_theories_imported','source_precedence_reviewed','mechanized_proof'])
 stack=[x['formal_statement'] for x in core['clauses'] if x['disposition']=='encoded']
 while stack:
  x=stack.pop()
  if isinstance(x,dict):assert not (x.get('op')=='pred' and x.get('name','').startswith('RecordActual'));stack.extend(x.values())
  elif isinstance(x,list):stack.extend(x)
 policy=load('query-policy.json');assert policy['queries']==queries() and len(policy['queries'])==34 and sum(x['source_condition']!='all-selected-records' for x in policy['queries'])==10 and policy['targets_not_assumptions'] is True and policy['whole_definition_proof_claimed'] is False
 model=a.verify();source=s.verify();assert model['control_count']==len(model['results'])==209 and len(model['nonentailment_countermodels'])==34 and model['semantic_ready'] is False and source['semantic_ready'] is False and model['source_fidelity']==source['source_fidelity']=='pending'
 assert (sum(x.get('primary_theory_satisfied') is True for x in model['results']),sum(x.get('primary_theory_satisfied') is False for x in model['results']),sum(x['status']=='rejected-model-structure' for x in model['results']),len(source['checks']))==(72,129,8,63)
 cases={x['case_id']:x for x in model['results']}
 for n in ['governed-missing','bounded-missing','permanent-missing','no-retired-or-rejected-identifier','subject-identifier-mismatch','available-digest-subject-mismatch','no-recovery-but-identifier-not-reserved','effective-record-reuse-not-rejected','effective-recovery-still-needs-reuse-rejection','recovery-not-applicable-to-record-identifier','history-inexact-historyRecord','missing-selected-posture-HistoryResolvableDeclared','missing-selected-posture-SuccessorIndependentlyResolvedDeclared']:assert cases[n]['primary_theory_satisfied'] is False
 for n in ['exact-reservation-optional-digest-successor-recovery-and-history-records','unused-unavailable-digest-handle-empty','unused-successor-handle-empty','unused-recovery-handle-empty','unavailable-digest-binding-absent-allowed','unclaimed-successor-binding-absent-allowed','unused-recovery-binding-absent-allowed','same-successor-identity-label-not-automatically-merge','retired-and-rejected-inclusive','independently-supported-actual-Authority','independently-supported-actual-Restoration']:assert cases[n]['primary_theory_satisfied'] is True and cases[n]['required_population_satisfied'] is True
 for n in ['no-selected-records','only-first-record-selected','no-independent-authority','all-actual-outcomes-independently-supplied']:assert cases[n]['primary_theory_satisfied'] is True and cases[n]['required_population_satisfied'] is False
 assert source['current_registry_admission_ref']=='CAL-DECISION-0066-DEFINITION-SPECIALIZATION-RESOLUTION-ADMISSION' and source['all_local_upstream_source_bytes_verified'] is True and len(source['recorded_local_source_observations'])==1 and source['external_file_refs']==[] and source['projection_bytes']==5042 and source['identifier_actually_withdrawn'] is False and source['first_render_sha256']==source['second_render_sha256']==b.r.digest((b.UNIT/'source-render-1.md').read_bytes())==b.r.digest((b.UNIT/'source-render-2.md').read_bytes())=='89162de7c65af480d3159ada490858ee105661f677883995cdb4dbe1a8ce68f6'
 assert len(load('source-query-obligation.json')['obligations'])==38
 fresh=load('fresh-types-logic-results.json');assert [x['check'] for x in fresh]==['contract','model','source'] and all(x['exit_code']==0 and not (b.UNIT/x['stderr']).read_bytes() for x in fresh)
 assert fresh[0]['argv'][1:]==[str(b.IMPL/'contracts.py'),'validate','--kind','interpretation','--input',str(b.UNIT/'t.json')]
 for x,script in zip(fresh[1:],['verify_candidate.py','verify_source_checks.py']):assert x['argv']==[fresh[0]['argv'][0],str(b.UNIT/script)] and (b.UNIT/x['stdout']).read_bytes()==(b.UNIT/(x['check']+'-stdout.txt')).read_bytes()
 for stem in ['author','build','model','source']:
  cmd=load(stem+'-command-result.json');assert cmd['exit_code']==0 and not (b.UNIT/cmd['stderr']).read_bytes()
 assert len(context['retained_preparation_failure_refs'])==1
 for ref in context['retained_preparation_failure_refs']:
  b.unchanged([ref]);attempt=b.ROOT/ref['path'];data=json.loads(attempt.read_bytes());assert data['status']=='retained-actual-prepared-contract-failure' and data['exit_code']==1 and data['checker_limits_changed'] is False and data['semantic_theory_change']=='none'
  for x in data['files']:assert b.r.digest((attempt.parent/x['path']).read_bytes())==x['sha256']
 successes=retained_successes();refinement=load('query-scope-refinement.json');b.unchanged([refinement['retained_successful_stage_ref']]);assert refinement['primary_theory_changed'] is False and refinement['source_units_changed'] is False and refinement['required_populations_changed'] is False and refinement['query_count']==34 and refinement['source_conditioned_queries']==10
 assert len(list((b.BASE/'definitions').glob('*/t.json')))==98 and not (b.BASE/'definitions/cal.definition.actor').exists() and len((b.UNIT/'t.json').read_bytes())==202871<b.c.MAX_BYTES==1000000 and b.c.MAX_NODES==50000 and a.v.MAX_STEPS==100000 and a.v.TIMEOUT==30
 review=(b.UNIT/'REVIEW.md').read_text();assert len(review.split())>3000 and len(re.findall(r'^## [0-9]+\\.',review,re.M))==13 and all('WR-FINDING-'+str(i).zfill(3) in review for i in range(1,23)) and 'S[Exact C66 source and Semantic Epoch full8847 audit]' in review and 'X[Next Actor native definition]' in review and 'Ten targets and witnesses are conditioned' in review
 diagram=review.split('```mermaid\\n')[1].split('```')[0];edges=re.findall(r'^ ([A-Z]+)(?:\\[.*?\\])? --> ([A-Z]+)',diagram,re.M);nodes={n for pair in edges for n in pair};assert nodes==set('S A T B I C R F V H P D J E Q N X'.split()) and len(edges)==17;pending=set(nodes);done=set()
 while pending:
  ready={n for n in pending if all(x in done for x,y in edges if y==n)};assert ready;done|=ready;pending-=ready
 b.unchanged(prior['files']+context['sources']);b.external_current(context);return context,counts,model,source,fresh,prior
def main():
 context,counts,model,source,fresh,prior=audit();report={'schema_version':'definition-assurance-types-logic-stage/v1-candidate','result':'PASS-for-typed-candidate-stage-only','unit_id':context['unit_id'],'authority_effect':'none','goal_status':'active','source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'full_delivery_sealed':False,'counts':counts,'controls':209,'T_true_controls':72,'T_false_controls':129,'malformed_rejections':8,'nonentailment_queries':34,'source_conditioned_queries':10,'actual_source_checks':63,'source_query_obligations':38,'fresh_checks':fresh,'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),'last_sealed_partial_drafts':97,'working_draft_files_observed':98,'current_whole_inventory_refresh_complete':False,'remaining_current_identities_without_draft_files_observed':85,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'pending':['current carrier and consumer mapping','reachable dependencies and current whole inventory','six fresh delivery checks','full delivery review,seal and separate audit'],'next_definition_after_delivery':'F05-T.cal.definition.actor','retained_preparation_failure_refs':context['retained_preparation_failure_refs'],'retained_failed_native_attempts':[],'retained_successful_prior_stage_refs':retained_successes(),'retained_failed_typed_stage_refs':[],'producer_results':[b.ref(b.UNIT/(stem+'-command-result.json')) for stem in ['author','build','model','source']],'inputs':[b.ref(b.UNIT/n) for n in INPUTS]};b.put('types-logic-receipt.json',report);print(json.dumps({k:report[k] for k in ['result','controls','nonentailment_queries','source_conditioned_queries','source_files_current','prior_candidate_files_preserved','working_draft_files_observed','full_delivery_sealed','goal_status']},indent=2))
if __name__=='__main__':main()
'''
ast.parse(s)
with (u/'close_types_logic_stage.py').open('x') as f:f.write(s)
s='''"""Separate actual Withdrawal Record sixteen-input typed-stage audit."""
import json
import build_candidate as b
import close_types_logic_stage as stage
def main():
 context,counts,model,source,fresh,prior=stage.audit();receipt=stage.load('types-logic-receipt.json');b.unchanged(receipt['inputs']+receipt['producer_results']+receipt['retained_preparation_failure_refs']+receipt['retained_successful_prior_stage_refs']);assert receipt['result']=='PASS-for-typed-candidate-stage-only' and len(receipt['inputs'])==16 and receipt['full_delivery_sealed'] is False and receipt['semantic_ready'] is False and receipt['source_fidelity']=='pending' and len(receipt['retained_preparation_failure_refs'])==1 and len(receipt['retained_successful_prior_stage_refs'])==2 and receipt['retained_failed_native_attempts']==receipt['retained_failed_typed_stage_refs']==[] and receipt['counts']==counts and receipt['controls']==209 and receipt['nonentailment_queries']==34 and receipt['source_conditioned_queries']==10 and receipt['actual_source_checks']==63 and receipt['source_query_obligations']==38
 print(json.dumps({'result':'PASS-separate-WithdrawalRecord-typed-stage-audit','frozen_inputs':16,'controls':209,'nonentailment_queries':34,'source_conditioned_queries':10,'prior_candidate_files_preserved':8847,'source_files_current':201,'working_drafts':98,'last_full_inventory_partial_drafts':97,'whole_inventory_refresh_complete':False,'whole_definition_proofs':0,'owner_accepted_whole_translations':0,'retained_native_failures':0,'retained_preparation_failures':1,'retained_successful_prior_query_stages':2,'goal_status':'active'},indent=2))
if __name__=='__main__':main()
'''
ast.parse(s)
with (u/'check_types_logic_stage.py').open('x') as f:f.write(s)
old=(p.with_name('20261011-semantic-epoch')/'capture_typed_stage.py').read_text().replace('cal.definition.semantic-epoch','cal.definition.withdrawal-record')
with (p/'capture_typed_stage.py').open('x') as f:f.write(old)
print('Prepared exact sixteen-input Withdrawal Record typed freeze and separate audit.')

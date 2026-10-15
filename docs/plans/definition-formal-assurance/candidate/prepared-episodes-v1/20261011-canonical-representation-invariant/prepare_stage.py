"""Prepare exact candidate typed-stage freeze and independent read-only audit."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.canonical-representation-invariant');prev=u.with_name('cal.definition.canonical-package-manifest')
freeze='''"""Exact CPRI types/logic stage only;full delivery remains pending."""
import json,re
import build_candidate as b
import verify_candidate as a
import verify_source_checks as s
INPUTS=['context.json','t.json','static-ir.json','correspondence.json','correspondence-check.json','denominator.json','clause-analysis.json','query-policy.json','source-query-obligation.json','comparison-selection.json','model-controls.json','source-checks.json','fresh-types-logic-results.json','REVIEW.md','CONTINUATION.md','DELIVERY-CONTEXT.md']
EXPECTED={'source_units':24,'mapped_clauses':24,'encoded_clauses':5,'explanatory_clauses':9,'deferred_clauses':10,'declarations':235,'required_populations':14,'unresolved_populations':128,'direct_semantic_uses':16,'countermodel_queries':34}
def load(n):return json.loads((b.UNIT/n).read_bytes())
def audit():
 context=load('context.json');core=load('t.json')['payload'];packet=load('correspondence.json');counts=load('denominator.json');snap=b.snapshot();b.unchanged(context['sources']);b.external_current(context);assert b.r.verify(snap,b.ROOT)['files']==201
 prior=load('../cal.definition.canonical-package-manifest/delivery-manifest.json');b.unchanged(prior['files']);assert len(prior['files'])==7919==context['pre_execution_check']['prior_candidate_files_preserved'] and context['pre_execution_check']['previous_separate_delivery_audit_exit_code']==0
 assert context['unit_id']=='F04-T.cal.definition.canonical-representation-invariant' and core['source']==context['source_selection']==b.source_ref(snap,'cal.definition.canonical-representation-invariant') and core['source']['sha256']=='36d484e269e9aeb79e2e4653874062157a07cc6a04d5edacfaa3502b441bbe76'
 manifest=json.loads((b.ROOT/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json').read_bytes());swu=next(x for x in manifest['units'] if x['id']==context['unit_id']);assert swu['outputs']==[b.ref(b.UNIT/'t.json')['path']] and swu['write_scope']==context['write_scope'] and swu['depends_on_tasks']==['A04','C01','E02'] and not context['session_scope']['blocking_user_decisions']
 for x in context['prerequisite_receipts']:
  b.unchanged([x['receipt_ref']]);assert json.loads((b.ROOT/x['receipt_ref']['path']).read_bytes())['task_result']==x['result'] and x['result'].startswith('PASS')
 b.c.validate(load('t.json'),'interpretation');assert load('static-ir.json')==b.ir.compile_interpretation(core,snap) and packet['interpretation']==core and packet['source_selection']=='current' and not core['assumptions'] and not packet['assumption_links'] and core['source_fidelity']=='pending'
 assert counts==EXPECTED and (len(b.SORTS),len(b.CONSTANTS),len(b.FUNCTIONS),len(b.SIGNATURE),len(core['declarations']))==(25,11,71,128,235) and len(core['depends_on'])==16 and len(packet['source_precedence']['conflicts'])==23 and packet['source_precedence']['review_ref'] is None and packet['review_packet']['review_status']=='pending'
 assert {x['population_id']:x['statement'] for x in core['populations'] if x['requirement']=='required'}=={'POP-'+n:z for n,z in b.required_populations().items()} and all(x['review_ref'] is None for x in core['populations'])
 assert b.FUNCTIONS['artifactMachine']==(['ArtifactReference'],'RepresentationReference') and b.FUNCTIONS['originProducer']==(['OriginRecordReference'],'ProducerReference') and b.SIGNATURE['MachineCanonicalDeclared']==['ArtifactReference','RepresentationReference'] and b.SIGNATURE['AllowedTupleDeclared']==['CanonicalKind','ProducerReference','ProcessReference','ProcessVersionReference','SourceReference'] and b.SIGNATURE['GeneratedProjectionDeclared']==['ProjectionReference','ArtifactReference','RepresentationReference']
 analysis=load('clause-analysis.json');assert analysis['known_losses']==b.LOSSES and analysis['primitive_theory_formulas']==9 and analysis['unique_encoded_source_formula_values']==5 and analysis['representation_origin_composition']=='source-precedence-owner-pending' and analysis['kind_authority_correspondence']=='explicit-declared-map-owner-pending' and analysis['L2_present_posture']=='future-level-only-not-currently-available' and all(analysis[n] is False for n in ['actual_outcome_queries_assumed_in_T','whole_prior_theories_imported','source_precedence_reviewed','mechanized_proof'])
 model=a.verify();source=s.verify();assert model['control_count']==len(model['results'])==160 and len(model['nonentailment_countermodels'])==34 and model['semantic_ready'] is False and source['semantic_ready'] is False and model['source_fidelity']==source['source_fidelity']=='pending'
 assert (sum(x.get('primary_theory_satisfied') is True for x in model['results']),sum(x.get('primary_theory_satisfied') is False for x in model['results']),sum(x['status']=='rejected-model-structure' for x in model['results']),len(source['checks']))==(42,110,8,57)
 cases={x['case_id']:x for x in model['results']}
 for n in ['hidden-second-representation','hidden-second-origin-record','candidate-producer-claimed-allowed','source-candidate-still-claimed-allowed','artifact-free-choice-artifactAuthorityKind','unsupported-owner-declared-statement','invalid-L1-receipt-declaration','future-L2-presently-unavailable','signature-mismatch-signatureState','projection-claims-canonical','prohibited-CanonicalGrantsAuthorityDeclared','prohibited-SharedD51LineageMergesSiblingDeclared']:assert cases[n]['primary_theory_satisfied'] is False
 for n in ['exact-representation-origin-assurance-and-independent-authority','single-allowed-alternative','outside-path-inference-not-scoped','independently-supported-actual-Authority','independently-supported-actual-ProcessExecution']:assert cases[n]['primary_theory_satisfied'] is True
 assert cases['single-allowed-alternative']['required_population_satisfied'] is False and cases['no-human-view-witness']['primary_theory_satisfied'] is True and cases['no-human-view-witness']['required_population_satisfied'] is False
 assert source['current_registry_admission_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and source['all_local_upstream_source_bytes_verified'] is True and len(source['recorded_local_source_observations'])==1 and len(source['external_source_observations'])==1 and source['projection_bytes']==11637 and source['first_render_sha256']==source['second_render_sha256']==b.r.digest((b.UNIT/'source-render-1.md').read_bytes())==b.r.digest((b.UNIT/'source-render-2.md').read_bytes())=='64310c3aa8032faddd71166d08ba5aa0b789d3461b506e7f8e44baf861b5ef1e'
 external=source['external_source_observations'][0];assert external['current_selection_bytes']==10383 and external['current_selection_sha256']=='3e9d50b1154b58b938c164725ac8fabed16914538dda579cf89c671c13c5becc' and external['admitted_for_use_selection']['status']=='admitted-for-definition-use' and external['coordinate_equivalence_accepted'] is False and external['prior_Artifact_observations_not_rewritten'] is True
 assert len(load('source-query-obligation.json')['obligations'])==27 and len(load('query-policy.json')['queries'])==34 and all(x['selected_in_T'] is False for x in load('query-policy.json')['queries'])
 fresh=load('fresh-types-logic-results.json');assert [x['check'] for x in fresh]==['contract','model','source'] and all(x['exit_code']==0 and not (b.UNIT/x['stderr']).read_bytes() for x in fresh)
 assert fresh[0]['argv'][1:]==[str(b.IMPL/'contracts.py'),'validate','--kind','interpretation','--input',str(b.UNIT/'t.json')]
 for x,script in zip(fresh[1:],['verify_candidate.py','verify_source_checks.py']):assert x['argv']==[fresh[0]['argv'][0],str(b.UNIT/script)] and (b.UNIT/x['stdout']).read_bytes()==(b.UNIT/(x['check']+'-stdout.txt')).read_bytes()
 for stem in ['author','build','model','source']:
  cmd=load(stem+'-command-result.json');assert cmd['exit_code']==0 and not (b.UNIT/cmd['stderr']).read_bytes()
 assert not context['retained_preparation_failure_refs'] and len(list((b.BASE/'definitions').glob('*/t.json')))==90
 review=(b.UNIT/'REVIEW.md').read_text();assert len(review.split())>2500 and len(re.findall(r'^## [0-9]+\\.',review,re.M))==13 and all('CPRI-FINDING-'+str(i).zfill(3) in review for i in range(1,24))
 diagram=review.split('```mermaid\\n')[1].split('```')[0];edges=re.findall(r'^ ([A-Z]+)(?:\\[.*?\\])? --> ([A-Z]+)',diagram,re.M);nodes={n for pair in edges for n in pair};assert nodes==set('S A T B I C R F V H P D J E Q N X'.split()) and len(edges)==17;pending=set(nodes);done=set()
 while pending:
  ready={n for n in pending if all(x in done for x,y in edges if y==n)};assert ready;done|=ready;pending-=ready
 b.unchanged(prior['files']+context['sources']);b.external_current(context);return context,counts,model,source,fresh,prior
def main():
 context,counts,model,source,fresh,prior=audit();report={'schema_version':'definition-assurance-types-logic-stage/v1-candidate','result':'PASS-for-typed-candidate-stage-only','unit_id':context['unit_id'],'authority_effect':'none','goal_status':'active','source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'full_delivery_sealed':False,'counts':counts,'controls':160,'T_true_controls':42,'T_false_controls':110,'malformed_rejections':8,'nonentailment_queries':34,'actual_source_checks':57,'source_query_obligations':27,'fresh_checks':fresh,'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),'last_sealed_partial_drafts':89,'working_draft_files_observed':90,'current_whole_inventory_refresh_complete':False,'remaining_current_identities_without_draft_files_observed':93,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'pending':['current carrier and consumer mapping','reachable dependencies and current whole inventory','six fresh delivery checks','full delivery review,seal and separate audit'],'next_definition_after_delivery':'F04-T.cal.definition.derived-refresh','retained_preparation_failure_refs':context['retained_preparation_failure_refs'],'retained_failed_native_attempts':[],'retained_successful_prior_stage_refs':[],'producer_results':[b.ref(b.UNIT/(stem+'-command-result.json')) for stem in ['author','build','model','source']],'inputs':[b.ref(b.UNIT/n) for n in INPUTS]};b.put('types-logic-receipt.json',report);print(json.dumps({k:report[k] for k in ['result','controls','nonentailment_queries','source_files_current','prior_candidate_files_preserved','working_draft_files_observed','full_delivery_sealed','goal_status']},indent=2))
if __name__=='__main__':main()
'''
check='''"""Independent read-only typed-stage audit;not a full delivery audit."""
import json
import build_candidate as b
import close_types_logic_stage as stage
def main():
 context,counts,model,source,fresh,prior=stage.audit();receipt=stage.load('types-logic-receipt.json');b.unchanged(receipt['inputs']+receipt['producer_results']+receipt['retained_preparation_failure_refs']);assert receipt['result']=='PASS-for-typed-candidate-stage-only' and len(receipt['inputs'])==16 and receipt['full_delivery_sealed'] is False and receipt['semantic_ready'] is False and receipt['source_fidelity']=='pending' and receipt['retained_failed_native_attempts']==[] and receipt['counts']==counts and receipt['controls']==160 and receipt['nonentailment_queries']==34 and receipt['actual_source_checks']==57 and receipt['source_query_obligations']==27
 print(json.dumps({'result':'PASS-separate-CanonicalRepresentationInvariant-typed-stage-audit','frozen_inputs':16,'controls':160,'nonentailment_queries':34,'prior_candidate_files_preserved':7919,'source_files_current':201,'working_drafts':90,'last_full_inventory_partial_drafts':89,'whole_inventory_refresh_complete':False,'whole_definition_proofs':0,'owner_accepted_whole_translations':0,'goal_status':'active'},indent=2))
if __name__=='__main__':main()
'''
replay=(prev/'replay_types_logic.py').read_text().replace('Canonical Package Manifest','Canonical Representation Invariant')
for name,text in [('close_types_logic_stage.py',freeze),('check_types_logic_stage.py',check),('replay_types_logic.py',replay)]:
 ast.parse(text)
 with (u/name).open('x') as f:f.write(text)
capture=(p.with_name('20261011-canonical-package-manifest')/'capture_typed_stage.py').read_text().replace('cal.definition.canonical-package-manifest','cal.definition.canonical-representation-invariant')
with (p/'capture_typed_stage.py').open('x') as f:f.write(capture)
print('Prepared CPRI typed-stage freeze,independent audit and three-check fresh replay.')

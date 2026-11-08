"""Record only the verified typed-candidate stage; full delivery remains pending."""
import json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def main():
 context=load('context.json');core=load('t.json')['payload'];packet=load('correspondence.json');counts=load('denominator.json');model=load('model-controls.json');source=load('source-checks.json');fresh=load('fresh-types-logic-results.json');b.unchanged(context['sources']);snap=b.snapshot();selected=b.r.verify(snap,b.ROOT);prior=json.loads((b.BASE/'definitions/cal.definition.evaluation/delivery-manifest.json').read_bytes());b.unchanged(prior['files']);assert len(prior['files'])==context['pre_execution_check']['prior_candidate_files_preserved'] and selected['files']==201
 b.c.validate(load('t.json'),'interpretation');assert b.r.same_json(b.ir.compile_interpretation(core,snap),load('static-ir.json'));assert packet['interpretation']==core;assert load('correspondence-check.json')['character_accounting_complete'];assert not core['assumptions'] and not packet['assumption_links'] and core['source_fidelity']=='pending';assert len(model['results'])==88 and len(model['nonentailment_countermodels'])==21
 assert (sum(x.get('primary_theory_satisfied') is True for x in model['results']),sum(x.get('primary_theory_satisfied') is False for x in model['results']),sum(x['status']=='rejected-model-structure' for x in model['results']))==(33,48,7)
 b.unchanged(model['checker_bindings']+model['input_refs']+list(source['selected_inputs'].values()));assert model['runtime_bindings']==v.f.current_bindings();assert len(source['checks'])==38 and all(x['result'] for x in source['checks']);assert source['projection_bytes']>0 and source['whole_recorded_legacy_file_recovered'] is False and source['unrecovered_legacy_sections']==['D65'] and len(source['legacy_recovery_observations'])==2 and source['actual_evidence_proof_truth_adequacy_provenance_currentness_or_authority_verified'] is False;assert [x['check'] for x in fresh]==['contract','model','source'];assert all(x['exit_code']==0 and not (b.UNIT/x['stderr']).read_bytes() for x in fresh)
 for x in fresh[1:]:assert (b.UNIT/x['stdout']).read_bytes()==(b.UNIT/(x['check']+'-stdout.txt')).read_bytes()
 assert len(list((b.BASE/'definitions').glob('*/t.json')))==70
 report={'schema_version':'definition-assurance-types-logic-stage/v1-candidate','result':'PASS-for-typed-candidate-stage-only','unit_id':context['unit_id'],'authority_effect':'none','goal_status':'active','source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'full_delivery_sealed':False,'counts':counts,'controls':88,'T_true_controls':33,'T_false_controls':48,'malformed_rejections':7,'nonentailment_queries':21,'actual_source_checks':38,'fresh_checks':fresh,'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),'last_sealed_partial_drafts':69,'working_draft_files_observed':70,'current_whole_inventory_refresh_complete':False,'remaining_current_identities_without_draft_files_observed':113,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'pending':['authority-profile/schema probes','reachable dependency and current joint inventory refresh','six-check full-delivery replay','finalization and separate delivery audit'],'next_definition_after_delivery':'F03-T.cal.definition.evidence-set','inputs':[b.ref(b.UNIT/n) for n in ['context.json','t.json','static-ir.json','correspondence.json','correspondence-check.json','model-controls.json','source-checks.json','fresh-types-logic-results.json','REVIEW.md','CONTINUATION.md']]}

 for stem in ['author','build','model','source']:
  cmd=load(stem+'-command-result.json');assert cmd['exit_code']==0 and not (b.UNIT/cmd['stderr']).read_bytes()

 attempts=[]
 for folder,stem,code in [('001-wrong-SWU-binding','author',1),('002-invoked-before-author-success','build',2)]:
  d=b.UNIT/'attempts'/folder;attempt=json.loads((d/'attempt.json').read_bytes());cmd=json.loads((d/(stem+'-command-result.json')).read_bytes());assert attempt['actual_exit_code']==cmd['exit_code']==code and attempt['actual_Evidence_unit_created'] is False
  for x in attempt['files']:assert b.r.digest((d/x['name']).read_bytes())==x['sha256']
  assert (d/(stem+'-stderr.txt')).read_bytes();attempts.append({'directory':folder,'producer':stem,'actual_exit_code':code,'successful_producer':False,'attempt_ref':b.ref(d/'attempt.json')})
 report['retained_failed_attempts']=attempts;report['successful_corrected_author_result_ref']=b.ref(b.UNIT/'author-command-result.json')
 b.put('types-logic-receipt.json',report);print(json.dumps({k:report[k] for k in ['result','controls','nonentailment_queries','source_files_current','prior_candidate_files_preserved','full_delivery_sealed','goal_status']},indent=2))
if __name__=='__main__':main()

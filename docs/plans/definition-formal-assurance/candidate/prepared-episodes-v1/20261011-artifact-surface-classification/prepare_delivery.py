from pathlib import Path
import ast
root=Path.cwd();unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact-surface-classification';old=(unit.with_name('cal.definition.artifact-lifetime')/'finalize.py').read_text()
head='''"""Seal exact Surface candidate delivery only after all actual fresh checks."""
import json,re
import build_candidate as b
import close_types_logic_stage as stage
import verify_authority_profile as p
import verifier as v
NEXT='F04-T.cal.definition.artifact-type-registry'
def load(n):return json.loads((b.UNIT/n).read_bytes())
def require(ok,message):
 if not ok:raise ValueError(message)
def audit():
 context,counts,model,source,typed_fresh,prior=stage.audit();core=load('t.json')['payload'];packet=load('correspondence.json');typed=load('types-logic-receipt.json');b.unchanged(typed['inputs']+typed['producer_results']);require(typed['result']=='PASS-for-typed-candidate-stage-only' and typed['full_delivery_sealed'] is False and len(typed['inputs'])==16 and typed['retained_failed_native_attempts']==[] and typed['retained_preparation_failure_refs']==[],'Frozen typed stage changed')
 profile=p.verify();require((len(profile['profiles']),sum(x['expected_rejection'] for x in profile['profiles']),len(profile['finite_comparison_frames']),sum(x['expected_rejection'] for x in profile['finite_comparison_frames']))==(32,30,77,72),'Qualified counts changed')
 require(profile['actual_check_count']==len(profile['actual_checks'])==46 and all(x['result'] for x in profile['actual_checks']) and (profile['current_type_registry_rows'],profile['admitted_current_type_rows'])==(143,121),'Catalog or consumer observations changed')
 require(profile['direct_current_definition_binding_types']==['cal.artifact-type.canonical-package-manifest/v1'] and profile['C13_profile_is_Surface_consistency_detector'] is False,'Carrier admission or generic profile collapsed')
 require((len(profile['Definition_schema_probes']),sum(x['schema_accepted'] for x in profile['Definition_schema_probes']),len(profile['C13_profile_schema_probes']),sum(x['schema_accepted'] for x in profile['C13_profile_schema_probes']),len(profile['manifest_schema_and_pure_guard_probes']))==(38,5,30,10,10),'Schema/pure function probes changed')
 require(profile['source_map_obligations']==p.MAP_FIELDS and len(p.MAP_FIELDS)==26 and profile['accepted_source_to_carrier_or_consumer_map_refs']==[] and all(profile[n] is False for n in ['bound_package_validator_executed','canonical_or_candidate_carrier_writer_executed','native_or_live_consumer_executed','actual_role_resolution_admission_or_authority_created','direct_carrier_or_consumer_alignment_accepted']) and profile['current_manifest_semantic_function_evaluated_on_in_memory_fixtures'] is True and profile['new_authorities_or_relations_created']==0,'Mappings or effects invented')
 observations=profile['consumer_observations'];cross=profile['cross_definition_review_findings'];require(len(observations)==2 and [x['variant'] for x in observations]==['historical','current'] and all(x['accepted_consumer_map_refs']==[] and x['native_or_live_consumer_executed'] is False for x in observations),'Consumer set or accepted maps changed')
 require(observations[0]['Surface_binding']['definition_ref']=='cal.definition.artifact-surface-classification@1.0.0-candidate.1' and observations[1]['Surface_binding']['definition_ref']==core['source']['version_ref'] and observations[1]['Surface_binding']['sha256']==core['source']['sha256'] and len(cross)==1 and cross[0]['finding_id']=='SURF-CONSUMER-FINDING-001' and cross[0]['status']=='unresolved' and cross[0]['accepted_consumer_map_refs']==[] and cross[0]['common_meaning_consistency_verified'] is False,'Historical/current consumer routing silently accepted')
 for n in ['current_C70_carrier_binds_current_Surface','historical_manifest_binds_predecessor','historical_positive_fixture_missing_self_entry','current_positive_fixture_has_exact_self_entry','current_schema_rejects_missing_duplicate_wrong_type_and_wrong_role_self_entry','current_pure_manifest_guard_rejects_these','duplicate_surface_path_fixture_needs_pure_semantic_guard']:require(cross[0][n] is True,'Consumer distinction changed '+n)
'''
common=old[old.index(" local=load('dependency-graph.json')"):old.index(" require(not (b.BASE/'definitions/cal.definition.artifact-surface-classification').exists()")]
common=common.replace("../cal.definition.artifact/","../cal.definition.artifact-lifetime/").replace("+33","+26").replace("==83","==84").replace("==100","==99").replace("'LIFE-FINDING-'","'SURF-FINDING-'").replace("'LIFE-CONSUMER-FINDING-001'","'SURF-CONSUMER-FINDING-001'")
next_checks=''' require(not (b.BASE/'definitions/cal.definition.artifact-type-registry').exists(),'Next native unit created before full delivery audit')
 prep=load('next-unit-preparation/source-inspection.json');command=load('next-unit-preparation/source-inspection-command-result.json');planned=load('next-unit-preparation/manifest.json')
 require(command['exit_code']==0 and not (b.UNIT/'next-unit-preparation'/command['stderr']).read_bytes() and len(prep['checks'])==16 and all(x['result'] for x in prep['checks']) and prep['source']==b.source_ref(b.snapshot(),'cal.definition.artifact-type-registry') and prep['source']['sha256']=='e554069c42d0ee17d4df65a0de2b0bba998933622aa9aba296671a01dd273e81' and prep['requires_Surface_full_delivery_audit_first'] is True and all(prep[n] is False for n in ['actual_next_unit_created','interpretation_or_models_created','native_or_live_consumer_executed','semantic_ready','mechanized_proof']),'Next Registry source preparation promoted')
 b.unchanged(list(prep['selected_inputs'].values()));require(planned['source']==prep['source'] and planned['next_definition_priority']==NEXT and len(planned['files'])==6 and planned['owner_acceptance_ref'] is None and all(planned[n] is False for n in ['actual_next_unit_created','typed_interpretation_or_models_created','semantic_ready','mechanized_proof']),'Next proposal promoted');b.unchanged(planned['files'])
 for i in [1,2]:
  folder=b.UNIT/('preparation-history/profile-00'+str(i));attempt=json.loads((folder/'attempt.json').read_bytes());cmd=json.loads((folder/'profile-command-result.json').read_bytes());require(attempt['actual_exit_code']==cmd['exit_code']==1 and attempt['frozen_inputs_modified'] is False and attempt['profile_report_created'] is False and (folder/'profile-stderr.txt').read_bytes(),'Failed profile history changed')
 b.unchanged(prior['files']+context['sources']);b.external_current(context)
 return context,core,packet,counts,inventory,graph,profile,source,prior
'''
main=old[old.index('def main():'):]
start=main.index(" validation={");end=main.index(" b.put('episode-status.json'",start)
validation=""" validation={**counts,'sorts':8,'unique_encoded_formulas':5,'primitive_theory_templates':4,'model_controls':95,'T_true_controls':31,'T_false_controls':56,'malformed_rejections':8,'nonentailment_queries':22,'qualification_profiles':32,'rejected_profiles':30,'finite_source_map_frames':77,'rejected_frames':72,'catalog_and_consumer_checks':46,'Definition_shape_probes':38,'Definition_acceptances':5,'C13_profile_shape_probes':30,'C13_profile_acceptances':10,'manifest_schema_and_pure_guard_probes':10,'source_map_obligations':26,'historical_and_current_consumer_variants_observed':2,'unresolved_cross_definition_findings':1,'accepted_Surface_carrier_or_consumer_maps':0,'actual_source_checks':55,'source_query_obligations':33,'static_reuse_adversarial_differential_checks':15,'all_per_definition_T_I_models_freshly_evaluated':True,'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'fresh_replays':'PASS for six actual terminal checks','retained_failed_native_definition_producers':0,'retained_failed_native_profile_producers':2,'retained_failed_typed_freeze_audits':0,'retained_failed_next_source_inspections':0,'retained_preparation_failures':0,'retained_failed_delivery_seal_audits':0,'retained_failed_separate_delivery_audits':0}
"""
main=main[:start]+validation+main[end:]
main=main.replace("'per_definition_T_candidate_drafts':83","'per_definition_T_candidate_drafts':84").replace("'remaining_current_identities_without_per_definition_T_draft':100","'remaining_current_identities_without_per_definition_T_draft':99").replace('partial-typed-Lifetime-default-override-and-scoped-assertion-record-guards','partial-typed-Surface-package-roles-self-entry-and-unique-declared-resolution-guards').replace('actual_lifespan_truth_chronology_override_authority_and_consumer_maps','actual_enumeration_role_correctness_resolution_admission_and_consumer_maps').replace('Lifetime_owner_translation_acceptance','Surface_owner_translation_acceptance').replace("'retained_next_source_inspection_failure_refs':[b.ref(b.UNIT/'preparation-history/next-Surface-source-inspection-001/attempt.json')]","'retained_next_source_inspection_failure_refs':[],'retained_failed_native_profile_attempt_refs':[b.ref(b.UNIT/('preparation-history/profile-00'+str(i)+'/attempt.json')) for i in [1,2]]").replace('Current inventory83partial/100missing','Current inventory84partial/99missing').replace("'partial_drafts':83","'partial_drafts':84").replace("'missing_current_drafts':100","'missing_current_drafts':99")
code=head+common+next_checks+main;ast.parse(code)
with (unit/'finalize.py').open('x') as f:f.write(code)
audit='''"""Read-only audit of exact Surface delivery before native Registry creation."""
import json
import build_candidate as b
import finalize

def main():
 context,core,packet,counts,inventory,graph,profile,source,prior=finalize.audit();receipt=finalize.load('receipt.json');manifest=finalize.load('delivery-manifest.json');b.unchanged(receipt['inputs']+receipt['outputs']+manifest['files']);assert receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False and receipt['mechanized_proof'] is False and receipt['whole_definition_translation']=='pending' and len(list((b.BASE/'definitions').glob('*/t.json')))==84 and any(x['path']==b.ref(b.UNIT/'t.json')['path'] for x in receipt['outputs']) and receipt['retained_failed_native_attempt_refs']==[] and receipt['retained_prior_preparation_failure_refs']==[] and receipt['retained_next_source_inspection_failure_refs']==[] and len(receipt['retained_failed_native_profile_attempt_refs'])==2
 current=sorted([b.ref(q) for folder in [b.BASE,b.IMPL] for q in folder.rglob('*') if q.is_file() and '__pycache__' not in q.parts and q.suffix!='.pyc' and q!=b.UNIT/'delivery-manifest.json'],key=lambda x:x['path'])
 if current!=manifest['files']:raise ValueError('Current file set differs from seal')
 print(json.dumps({'result':'PASS-for-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'partial_drafts':84,'missing_current_drafts':99,'retained_failed_native_profile_attempts':2,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'semantic_ready':False,'goal_status':'active','next_definition_priority':finalize.NEXT},indent=2,sort_keys=True))
if __name__=='__main__':main()
'''
ast.parse(audit)
with (unit/'check_delivery.py').open('x') as f:f.write(audit)
print('Surface full delivery helpers prepared; frozen16 inputs unchanged.')

"""Read-only bounded CRB consumer/profile/reuse audit; whole episode remains active."""
from pathlib import Path
import collections,json,sys
root=Path.cwd();prepared=Path(__file__).resolve().parent;unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding';sys.path.insert(0,str(unit))
import build_candidate as b
import inspect_carrier_consumers as consumer
import verify_authority_profile as profile
checks=[]
def load(path):return json.loads(path.read_bytes())
def ck(name,ok):assert ok,name;checks.append({'check_id':name,'result':True})
observation=consumer.inspect();qualification=profile.verify()
ck('fresh-consumer-and-profile-reports-match',observation==load(unit/'carrier-consumer-inspection.json') and qualification==load(unit/'authority-profile-checks.json'))
ck('400actual-checks',observation['check_count']==len(observation['checks'])==400 and all(x['result'] for x in observation['checks']))
matrix=observation['source_coordinate_correspondence'];expected={n:(carrier,sort) for fields,carrier in b.GROUPS for n,sort in fields.items()}
ck('27exact-descriptor-fields-and-types',len(matrix)==27 and {x['candidate_symbol']:(x['candidate_argument_sort'],x['candidate_result_sort']) for x in matrix}==expected)
ck('all-maps-pending-not-accepted',all(x['status']=='pending-owner-correspondence' and not x['accepted_map_refs'] and x['meaning_obligation'] for x in matrix) and observation['accepted_semantic_correspondence_complete'] is False and not observation['accepted_semantic_map_refs'])
ck('current-and-historical-primary-meanings-separate',observation['complete_current_definition_binding_types']==['cal.artifact-type.capability-realization-binding/v2'] and observation['historical_primary_meanings']==['cal.definition.product-capability@1.0.0-candidate.1'] and observation['current_primary_meanings']==['cal.definition.capability-realization-binding@1.0.0-candidate.1'])
ck('positive-C60-type-no-instance',observation['positive_C60_result']['artifact_types_admitted']==1 and observation['positive_C60_result']['instances_admitted']==observation['positive_C60_result']['consumer_activations']==0)
ck('28meaning-observations-no-whole-import',len(observation['meaning_observations'])==28 and all(x['whole_theory_imported'] is False and not x['accepted_map_refs'] for x in observation['meaning_observations']))
ck('30Definition71carrier-probes',len(observation['definition_shape_probes'])==30 and len(observation['carrier_shape_probes'])==71 and observation['definition_shape_acceptances']==6 and observation['carrier_shape_acceptances']==28)
probes={x['case_id']:x for x in observation['carrier_shape_probes'] if x['version']=='v2'}
for name in ['Binding-ID-is-Capability','Binding-ID-is-Capability-version','realization-is-node_id','realization-is-capability_ref','realization-is-capability_version_ref']:
 ck('schema-vs-current-expression-'+name,probes[name]['schema_accepted'] is True and probes[name]['isolated_current_expression']['result'] is False)
for name in ['superseded-with-self-successor','changed-endpoint-same-node-version','changed-posture-same-node-version','adopted-with-opaque-evidence','duplicate-realization-records']:
 ck('carrier-correspondence-gap-'+name,probes[name]['schema_accepted'] is True and probes[name]['isolated_current_expression']['result'] is True)
for name in ['unreviewed-direct-canonical_relation_authority_ref','unreviewed-direct-typed_relation_projection','unreviewed-direct-binding_digest','direct-Implementation-version-field']:
 ck('closed-schema-no-injected-map-'+name,probes[name]['schema_accepted'] is False)
comparisons=observation['typed_comparison_models'];ck('42models23isolatedguards',len(comparisons)==42 and sum(x['semantic_guard_isolated'] for x in comparisons)==23)
ck('T-I-independent-distribution',collections.Counter((x['T'],x['I']) for x in comparisons)=={(True,True):7,(True,False):10,(False,True):24,(False,False):1})
for case in comparisons:
 ck('model-digest-'+case['case_id'],b.ir.digest(case['model'])==case['model_sha256'])
 if case['semantic_guard_isolated']:ck('isolated-primitive-'+case['case_id'],[n for n,truth in case['primitive_results'].items() if not truth]==case['expected_only_failed_primitives'] and len(case['expected_only_failed_primitives'])==1)
ck('unchanged-step-limits',max(x['T_I_steps'] for x in comparisons)==40628 and max(x['primitive_steps'] for x in comparisons)==11536)
ck('38profiles37reject157frames156reject50obligations',len(qualification['profiles'])==38 and sum(x['expected_rejection'] for x in qualification['profiles'])==37 and len(qualification['finite_comparison_frames'])==157 and sum(x['expected_rejection'] for x in qualification['finite_comparison_frames'])==156 and len(qualification['source_map_obligations'])==50)
ck('13explicit-unresolved-findings',len(observation['unresolved_consumer_findings'])==13 and all(x['status']=='unresolved' and not x['accepted_map_refs'] for x in observation['unresolved_consumer_findings']))
ck('no-owner-acceptance-or-actual-effects',not qualification['accepted_source_to_carrier_or_consumer_map_refs'] and qualification['actual_instance_effects_created'] is False and observation['actual_Binding_adoption_deployment_conformance_operation_value_or_authority_created'] is False and observation['semantic_ready'] is qualification['semantic_ready'] is False)
ck('only-exact-current-expression-no-whole-package',observation['current_package_expression_extracted_read_only'] is True and observation['bound_package_validator_executed'] is observation['canonical_or_candidate_carrier_writer_executed'] is observation['native_or_live_consumer_executed'] is False)
bindings=[]
for stem in ['carrier-inspection','carrier-inspection-replay','profile','profile-replay','reuse']:
 result=load(prepared/(stem+'-command-result.json'));ck('actual-terminal0-'+stem,result['exit_code']==0 and not(prepared/result['stderr']).read_bytes());bindings.extend([b.ref(prepared/(stem+'-command-result.json')),b.ref(prepared/result['stdout']),b.ref(prepared/result['stderr'])])
for stem in ['carrier-inspection','profile']:ck('stdout-parity-'+stem,(prepared/(stem+'-stdout.txt')).read_bytes()==(prepared/(stem+'-replay-stdout.txt')).read_bytes())
reuse=load(unit/'static-snapshot-reuse-checks.json');ck('15strict-reuse-checks',len(reuse['checks'])==15 and all(x['result'] for x in reuse['checks']) and reuse['shared_sealed_validator_files_modified'] is reuse['live_currentness_reused'] is reuse['model_evaluation_or_correspondence_checks_skipped'] is False)
for name in ['static_snapshot_reuse.py','verify_static_snapshot_reuse.py']:ck('exact-predecessor-reuse-code-'+name,(unit/name).read_bytes()==(b.BASE/'definitions/cal.definition.capability-instance'/name).read_bytes())
frozen=load(unit/'types-logic-receipt.json');prior=load(b.BASE/'definitions/cal.definition.capability-instance/delivery-manifest.json')['files'];b.unchanged(frozen['inputs']+frozen['checker_bindings']+prior+bindings+list(observation['selected_inputs'].values())+list(qualification['selected_inputs'].values())+reuse['selected_inputs'])
ck('17inputs5checkers10287prior201sources-preserved',len(frozen['inputs'])==17 and len(frozen['checker_bindings'])==5 and len(prior)==10287 and b.r.verify(b.snapshot(),root)['files']==201)
unrelated=load(root/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261012-project/unrelated-tracked-work.json');b.unchanged(unrelated['refs']);ck('30unrelated-dirty-files-preserved',len(unrelated['refs'])==unrelated['tracked_dirty_count']==30)
state=load(prepared/'current-state.json');ck('original-scope-and-goal-active',state['original_scope']=={'identities':183,'versions':189,'source_files':201,'tasks':121,'edges':511,'work_units':797,'frontiers':36} and state['goal_status']=='active' and state['full_delivery_sealed'] is False)
ck('110working-theories-no-new-coordination-unit',len(list((b.BASE/'definitions').glob('*/t.json')))==110 and not(b.BASE/'definitions/cal.definition.coordination-context').exists())
report={'schema_version':'CRB-consumer-profile-reuse-stage-audit/v1-candidate','result':'PASS-for-bounded-CRB-consumer-profile-reuse-stage','checks':checks,'check_count':len(checks),'actual_terminal_records':bindings,'selected_inputs':[b.ref(unit/n) for n in ['carrier-consumer-inspection.json','authority-profile-checks.json','CONSUMER-REVIEW.md','static-snapshot-reuse-checks.json']]+[b.ref(Path(__file__).resolve())],'frozen_inputs_preserved':17,'frozen_checker_bindings_preserved':5,'prior_candidate_files_preserved':10287,'source_files_current':201,'full_delivery_sealed':False,'source_fidelity':'pending','semantic_ready':False,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'goal_status':'active','authority_effect':'none'}
with (prepared/'consumer-stage-audit.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'result':report['result'],'checks':len(checks),'full_delivery_sealed':False,'semantic_ready':False},indent=2))

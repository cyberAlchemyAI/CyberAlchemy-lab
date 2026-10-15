"""Record Project full closure only after actual terminal seal and separate audit."""
from pathlib import Path
import hashlib,json,sys
p=Path(__file__).resolve().parent;root=Path.cwd()
u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/CAV2-D60'
sys.path.insert(0,str(u))
import build_candidate as b
def load(path):return json.loads(path.read_bytes())
for stem in ['full-delivery-seal','full-delivery-audit','fresh-delivery']:
 cmd=load(p/(stem+'-command-result.json'))
 assert cmd['exit_code']==0,stem
 stderr=Path(cmd['stderr']);stderr=stderr if stderr.is_absolute() else p/stderr
 assert not stderr.read_bytes(),stem
fresh=load(u/'fresh-command-results.json')
assert [x['check'] for x in fresh]==['contract','model','source','profile','dependency','inventory']
assert all(x['exit_code']==0 and not(u/x['stderr']).read_bytes() for x in fresh)
manifest=load(u/'delivery-manifest.json');receipt=load(u/'receipt.json')
b.unchanged(manifest['files'])
current=sorted([b.ref(q) for folder in [b.BASE,b.IMPL] for q in folder.rglob('*') if q.is_file() and '__pycache__' not in q.parts and q.suffix!='.pyc' and q!=u/'delivery-manifest.json'],key=lambda x:x['path'])
assert current==manifest['files']
assert manifest['prior_seal_files']==10076 and receipt['task_result']=='PARTIAL-DRAFT-VERIFIED'
assert receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False and receipt['whole_definition_proof'] is None
unrelated=load(p/'unrelated-tracked-work.json')
b.unchanged(unrelated['refs']);assert unrelated['tracked_dirty_count']==30
continuation=load(p/'ARE-full-continuation.json')
assert continuation['response']['ok'] is True and continuation['response']['kind']=='gate' and continuation['response']['authority_effect']=='none'
iv=load(u/'current-inventory.json');g=load(u/'current-dependency-graph.json');local=load(u/'dependency-graph.json')
c=load(u/'carrier-consumer-inspection.json');profile=load(u/'authority-profile-checks.json');selection=load(u/'dependency-selection.json')
prep=load(u/'next-unit-preparation/source-inspection.json')
assert iv['partial_drafts']==108 and len(iv['missing_current_drafts'])==75
assert iv['source_owner_accepted_whole_translations']==iv['whole_definition_proofs']==0
assert c['accepted_semantic_map_refs']==profile['accepted_source_to_carrier_or_consumer_map_refs']==[]
assert not(b.BASE/'definitions/cal.definition.capability-instance').exists()
assert len(prep['checks'])==27 and all(x['result'] for x in prep['checks']) and prep['requires_Project_full_delivery_audit_first'] is True
old=(p/'current-state.json').read_bytes();state=json.loads(old)
with (p/'current-state-before-full-delivery.json').open('xb') as f:f.write(old)
combinations=[(x['T'],x['I']) for x in c['typed_comparison_models']]
sealed=len(manifest['files']);words=len((u/'DELIVERY-REVIEW.md').read_text().split())
state.update(
 completed_boundary=f'Project full{sealed}-file candidate seal and separate actual audit0',
 full_delivery_sealed=True,sealed_candidate_files=sealed,full_seal_exit_code=0,
 full_separate_audit_exit_code=0,active_jobs=[],
 consumer_inspection={'actual_exit_code':0,'identical_fresh_replay_exit_code':0,
  'full_consumer_inspection_complete':True,'checks':c['check_count'],
  'meanings':len(c['meaning_observations']),'contracts':len(c['separately_bound_comparison_contracts']),
  'Definition_probes':c['definition_shape_probe_count'],'Definition_acceptances':c['definition_shape_acceptances'],
  'carrier_probes':c['carrier_shape_probe_count'],'carrier_acceptances':c['carrier_shape_acceptances'],
  'typed_comparisons':c['typed_comparison_count'],
  'TT':combinations.count((True,True)),'TF':combinations.count((True,False)),
  'FT':combinations.count((False,True)),'FF':combinations.count((False,False)),
  'isolated_semantic_guards':sum(x['semantic_guard_isolated'] for x in c['typed_comparison_models']),
  'consumer_findings':len(profile['cross_definition_review_findings']),'accepted_maps':0,
  'actual_Project_activation_established':False},
 authority_profiles=len(profile['profiles']),
 rejected_profiles=sum(x['expected_rejection'] for x in profile['profiles']),
 finite_map_frames=len(profile['finite_comparison_frames']),
 rejected_frames=sum(x['expected_rejection'] for x in profile['finite_comparison_frames']),
 pending_source_maps=len(profile['source_map_obligations']),static_reuse_checks=15,
 whole_inventory_refresh_complete=True,working_native_drafts=108,
 working_identities_without_native_T=75,current_inventory_counts=iv['counts'],
 joint_graph={'nodes':len(g['nodes']),'edges':len(g['edges']),
  'missing_counterparts':len(g['missing_or_quarantined_interpretations']),'unclassified_cycles':len(g['cycle_reviews'])},
 reachable_graph={'nodes':len(local['nodes']),'edges':len(local['edges']),
  'selected_packets':len(selection['packet_refs']),
  'missing_packets':len(local['missing_or_quarantined_interpretations']),
  'unclassified_cycles':len(local['cycle_reviews'])},
 six_fresh_delivery_checks=fresh,typed_review_words=state['review_words'],
 full_review_words=words,full_review_aspects=13,
 next_CapabilityInstance_source_preparation={'actual_exit_code':0,
  'checks':len(prep['checks']),'source_units':prep['source_units'],
  'projection_bytes':prep['projection_bytes'],'external_scopes':len(prep['external_file_refs']),
  'actual_native_CapabilityInstance_created':False,'requires_Project_full_audit0':True},
 next_action='Formalize exact C18 Capability Instance definitions/types/logic after Project full separateaudit0;16tuplecoordinates,ownerlocality,oneexactProductCapabilityversion,separateparent/instanceauthorityclaims,inheritedcontract,extensionscope,adoption,construction,conformance,lifecycle,drift/recomposition,recursionbudgetorstop,terminalhandoff;conformancedoesnotimplyauthority.',
 goal_status='active')
state['refs'] += [b.ref(q) for q in [u/'receipt.json',u/'delivery-manifest.json',u/'DELIVERY-REVIEW.md',u/'work-delivery-dag.json',u/'current-inventory.json',u/'current-dependency-graph.json',u/'next-unit-preparation/manifest.json',p/'full-delivery-seal-command-result.json',p/'full-delivery-audit-command-result.json',p/'ARE-full-continuation.json']]
with (p/'current-state.json').open('w') as f:json.dump(state,f,indent=2,sort_keys=True);f.write('\n')
with (p/'FULL-DELIVERY-CONTEXT.md').open('a') as f:
 f.write('\n\n## Actual full Project delivery close\n\n')
 f.write(f'Project full{sealed}-file seal and separate actual read-only audit both exit0. All10076ancestor bytes and201sources preserved. Six fresh delivery checks exit0 with empty stderr and identical outputs. Full review{words}words/13aspects and18node18edge work DAG. Project actual activation unestablished;24source and12consumer findings unresolved;acceptedmaps0/wholetranslations0/wholeproofs0/sourcefidelitypending/semanticreadyfalse. No active delivery jobs.\n\n')
 f.write('Consumer191checks,27meanings,6contracts,30Definitionprobes6acceptances,321carrierprobes76acceptances,29T/I(12TT5TF6FT6FF),9isolatedguards. ProjectIDcollapse retains changecontinuity.35profiles34reject,121frames120reject,38pendingmaps,15staticreusechecks. DirectProjectIdentity andcompleteProjectIdentity+IdentityGraphbindings observed;goal_refs/owner_routes/evidence_index/purpose_refs/lifecycle_state absentfromcurrentProjectschema;Goalbodyalsolacksstate. Pursuit/membership/ownershipmap pending. C30/C31positive scoped effects intact,implementation/runtimenot_evaluable,Goalachievementnot_proven. No livevalidator,writer,adoption,activation oractualauthority effect.\n\n')
 f.write('Current108partial drafts75withoutT;all108selected T/Iwitnesses freshly evaluated. Joint150nodes2700edges42missing1unclassifiedcycle;reachable146nodes2620edges105packets41missing1cycle. Edgecompletenessrequiresindependentreview. Original183identities189versions201sources121tasks511edges797SWUs36frontiers intact. Prior138SWUoutputpresence isnotacceptance. OriginalT/O/E/R/J requirements,ownerfidelity,acceptedsharedinterpretation,wholeproofs andfinaloriginalscope aspectreview remain outstanding.\n\n')
 f.write('CapabilityInstance next source27checks20units4095projectionbytes2externalH2scopes exit0. ExactC18source d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5;C17sourceusesD64/D67 exact891c6b66.../bf8f3cb9...selectorspreserved.16tuplecoordinatesplusowner-localcondition,exactparentProductCapabilityversion,separateclaims,inheritedcontract,extension/adoption/construction/conformance/lifecycle/drift/recomposition/recursionstop/terminalhandoff. No nextnative existedatthefullaudited boundary. Conformanceisnotauthority. AREcontinuation gate/oktrue/none records nextnativework.\n\n')
 f.write('Retained9failedpreparedassemblyfiles13successfulpreparationrefs;no failednative/consumer/fresh/seal/audit producer orweakenedcheckerlimit. Preserve unrelated30trackedfiles4833insertions518deletionsandprivate/live/rollbackstate. Candidate-only;no canonical/private/live/publication/commit/push/memory changes. Originalgoalactive.\n')
print(json.dumps({'result':'Project full closure recorded','sealed_files':sealed,'prior_files_preserved':10076,'partial_drafts':108,'without_native_T':75,'full_review_words':words,'next':'Capability Instance types/logic','active_jobs':[],'goal_status':'active','semantic_ready':False},indent=2))


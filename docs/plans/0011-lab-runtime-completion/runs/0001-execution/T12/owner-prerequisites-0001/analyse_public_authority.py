"""Public authority metadata analysis only; no native/runtime/private-body access."""
import collections,hashlib,json,os,stat
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');OUT=Path(__file__).absolute().parent
S02='product/lab/release-candidates/v1/release-validation/0001/'
sources={};checks=[]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
def stamp(st):return st.st_dev,st.st_ino,st.st_uid,st.st_mode,st.st_size,st.st_mtime_ns,st.st_ctime_ns
def directory(st):return st.st_dev,st.st_ino,st.st_uid,st.st_mode
def capture(relative,pin=None):
 path=ROOT/relative;assert path.is_relative_to(ROOT) and '..' not in path.parts
 handles=[];links=[]
 try:
  parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);handles.append(parent)
  for part in path.parts[1:-1]:
   child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);handles.append(child)
   links.append((parent,part,directory(os.fstat(child))));parent=child
  fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent);handles.append(fd)
  before=os.fstat(fd);assert stat.S_ISREG(before.st_mode) and before.st_size<=32*1024*1024
  pieces=[];size=0
  while True:
   block=os.read(fd,min(1024*1024,32*1024*1024+1-size))
   if not block:break
   pieces.append(block);size+=len(block);assert size<=32*1024*1024
  raw=b''.join(pieces)
  assert stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False))
  assert all(directory(os.stat(name,dir_fd=parent,follow_symlinks=False))==identity for parent,name,identity in links)
  assert pin is None or sha(raw)==pin,relative
  row={'path':relative,'sha256':sha(raw),'size_bytes':len(raw),'public_metadata_only':True}
  assert sources.get(relative,row)==row
  sources[relative]=row;return raw
 finally:
  for fd in reversed(handles):os.close(fd)
def pairs(items):
 out={}
 for k,v in items:assert k not in out;out[k]=v
 return out
def load(relative,pin=None):return json.loads(capture(relative,pin),object_pairs_hook=pairs)
def bound(binding):return load(binding['path'],binding['sha256'])
def save(name,value):
 body=(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
 with (OUT/name).open('xb') as handle:handle.write(body)
 return {'path':str((OUT/name).relative_to(ROOT)),'sha256':sha(body),'size_bytes':len(body)}

task='docs/plans/0011-lab-runtime-completion/work-pack/tasks/T12.md'
for path in [task,'docs/plans/0010-lab-one-shot-execution/work-pack/tasks/R08.md','docs/plans/0009-lab-integrated-roadmap/work-pack/tasks/R08.md',S02+'S02-package-specific-gaps-0276.md','docs/plans/0011-lab-runtime-completion/SOURCE-BASELINE.json']:
 capture(path)
matrix=load(S02+'S02-owner-effect-matrix-0276.json','022ee74995b073b39dfbe0f28a529958f9c8f33c7059b2ebdf4614211b086ae1')
materializer=load(S02+'final-materializer-selection-0276.json','c5f290c5f5bebbbf3b8572a9b3457d265e9ab632a35e6b4cc5a4a78dd2f99465')
base=load(S02+'base-state-registry-history-0276.json','c4dc354eb83de8f24620abd9bbaf248c117b3f2cf247822432953e03dfe998c2')
assert len(matrix['members'])==len(materializer['members'])==363
by_member={m['member_ref']:m for m in materializer['members']};assert len(by_member)==363
assert set(by_member)=={m['member_ref']for m in matrix['members']}
assert all(not m['declared_role_objects'] and not m['matching_retained_assignment_objects'] and not m['current_owner_authority_verified']for m in matrix['members'])
assert not [r for r in base['original_role_Principal_objects'] if r['kind'] in ['role','role-assignment']]
checks.append('363 exact metadata members matched and zero required native Role/RoleAssignment objects in selected public candidate-base inspection')

D13=load('docs/decisions/0013-foundation-01-admission/decision.json','2aec4fc4cee04804047dbdfecdf521837b0bd1b006fc6b7ea55f46c9a15b4f52')
owner13=next(r for r in D13['admitted_records']if r['record_id']=='CAL-OWNERS-FOUNDATION-01');O13=bound(owner13)
assert D13['status']=='owner-admitted' and D13['bootstrap_owner_identity']['principal_id']=='person:<vrondelli>'
assert owner13['admission_effect']=='principal-and-five-separated-role-assignments-admitted'
foundation=bound({'path':D13['accepted_candidate']['manifest_path'],'sha256':D13['accepted_candidate']['manifest_sha256']})
bound({'path':D13['accepted_candidate']['validation_receipt_path'],'sha256':D13['accepted_candidate']['validation_receipt_sha256']})
D22=load('docs/decisions/0022-context-operational-owner-promotion/decision.json','4066222836d20e53c1b7a3eedff00690de0032e504d9369071aba87d2cc533ec')
assert D22['authority_basis']['foundation_decision_sha256']==sources['docs/decisions/0013-foundation-01-admission/decision.json']['sha256']
assert {'definition-owner','artifact-type-owner'}<=set(D22['preserved_foundation_role_ids'])
O22=bound(D22['accepted_successor_registry']);assert D22['accepted_successor_registry']['predecessor_sha256']==owner13['sha256']
D28=load('docs/decisions/0028-craft-foundation-v1/decision.json','920d2f82d22e30af51daaebbb8ec7dfbed336524920920a6669d8f6bb5234764')
bind28=D28['admitted_owner_binding'];O28=bound({'path':bind28['registry_postimage_path'],'sha256':bind28['registry_postimage_sha256']})
assert bind28['decision_overlay_status']=='admitted-active'
D29=load('docs/decisions/0029-cml07-semantic-foundation-v1/decision.json','5d197e1fbd5dd2fe9ebf46b1af72dd8dc4c705bc9438c6d964a99ca0f3662a82')
auth29=bound({'path':D29['authority_basis']['authorization_path'],'sha256':D29['authority_basis']['authorization_sha256']})
assert auth29['status']=='exact-owner-authorized' and auth29['principal_id']=='person:<vrondelli>'
manifest29=bound(auth29['manifest']);bound(auth29['validation_receipt'])
binding29=next(r for r in manifest29['candidate_inputs']if r['path'].endswith('/owner-bindings.json'));OB29=bound(binding29)
O29=bound(next(r for r in D29['canonical_postimages']if r['path'].endswith('/owners.json')))
assert O29['predecessor']['sha256']==bind28['registry_postimage_sha256']
assert D29['admission_result']['owner_bindings_admitted']==4
assert any(r['request_id']=='CML07-DR-03-OWNER-BINDINGS' for r in D29['admitted_decision_requests'])
assert any(r['role_id']=='identity-graph-owner' and r['principal_id']=='person:<vrondelli>'for r in OB29['assignments'])
checks.append('Exact admitted bootstrap-owner chain 0013→0022→0028→0029 and bound owner registries/authorization/manifest bytes verified, distinct from unchanged candidate-source status')

lookup=load('authority/project-state-transitions/current.json');state=bound(lookup['current_project_state']);bundle=bound(lookup['admission_bundle'])
assert state['node_id']==lookup['identity_ref'] and bundle['current_project_state_sha256']==lookup['current_project_state']['sha256']
canon={k:load('authority/admissions/lab-operational-runtime/v1/instances/'+k+'.json')for k in ['project-semantic-event-history','project-governance-event-history']}
history_results=[];unverified_runtime_authorization_refs=[];unverified_runtime_material_refs=[]
for label,histories in [('repository-current-public-lookup',canon),('selected-candidate-base-public-inspection',base['original_histories'])]:
 sem=histories['project-semantic-event-history']['payload']['events'];gov=histories['project-governance-event-history']['payload']['events']
 assert len(sem)==len(gov)
 for kind,h in histories.items():
  events=h['payload']['events'];prior=None
  for event in events:
   assert event['previous_event_digest']==prior
   assert digest({k:v for k,v in event.items()if k!='event_digest'})==event['event_digest']
   prior=event['event_digest']
   for row in event.get('material_refs',[]):
    if row['path'].split('/')[0] not in {'docs','authority','product','implementation','evidence','tooling','tools'}:
     unverified_runtime_material_refs.append({'binding':row,'scope':label,'body_opened':False,'reason':'Native artifact identifier, not a public repository file locator. Its exact native body remains unverified in this metadata-only analysis.'})
    else:capture(row['path'],row['sha256'])
   if 'authorization_ref' in event:
    if event['authorization_ref'].startswith('runtime-approval:'):
     unverified_runtime_authorization_refs.append({'reference':event['authorization_ref'],'expected_sha256':event['authorization_sha256'],'scope':label,'body_opened':False,'reason':'Local runtime identifier is not a public repository authority file; native/private approval bytes were not opened or verified in this analysis.'})
    else:capture(event['authorization_ref'],event['authorization_sha256'])
  assert digest([e['event_digest']for e in events])==h['payload']['chain_digest']
  history_results.append({'scope':label,'history_kind':kind,'events':len(events),'chain_digest':h['payload']['chain_digest'],'pure_digest_and_attachment_checks':'PASS','native_replay_or_current_owner_authority_claimed':False})
 for event,semantic in zip(gov,sem):
  pairing=event['semantic_event_ref'];assert pairing['semantic_event_digest']==semantic['event_digest'] and pairing['semantic_event_id']==semantic['event_id']
checks.append('Canonical five-event and selected candidate ten-event paired public histories have exact event/chain digests and available public authorization/material bytes; opaque local runtime approval identifiers remain explicitly unverified, with no native replay or authority transfer')
D75=load('docs/decisions/0075-lab-operational-runtime-v1-admission/decision.json');A75=bound(D75['authorization'])
assert A75['principal_ref']=='principal:lab-owner' and 'external-publication' in A75['excluded_effects']
checks.append('Historical Lab owner admission is exact implementation-only authorization, not new RoleAssignment or current R08 release authorization')

endpoint=load('authority/admissions/definition-complete-lab-model/v1/endpoint-inventory.json')
role_schema=load('authority/artifact-types/role-assignment/v1/schema.json')
for kind in ['role','role-assignment']:
 assert any(r.get('endpoint_kind')==kind and r.get('lifecycle_state')=='admitted-current'for r in endpoint['entries'])
assert {'role_ref','assignee_ref','assignment_basis_ref','assignment_state','period','scope_ref','owner_route','authority_claim_refs'}<=set(role_schema['required'])
checks.append('Role and RoleAssignment carrier admission verified separately from instance/assignment authority; required native interval, scope and basis fields recorded')

assignments={r['role_id']:r for r in O29['role_assignments']}
roles=[]
counts=collections.Counter(r for m in matrix['members']for r in m['required_roles'])
for role in ['repository-owner','definition-owner','artifact-type-owner','identity-graph-owner']:
 row=assignments.get(role);historical=row is not None
 roles.append({'required_role_ref':'role:'+role,'original_member_count':counts['role:'+role],
  'verified_historical_bootstrap_principal_ref':row['principal_id']if historical else None,
  'verified_historical_assignment_id':row['assignment_id']if historical else None,
  'historical_scope':row['scope']if historical else None,
  'historical_binding_admitted':historical,
  'historical_admission_decisions':['CAL-DECISION-0013-FOUNDATION-01-ADMISSION','CAL-DECISION-0022-CONTEXT-OPERATIONAL-OWNER-PROMOTION']if role in ['definition-owner','artifact-type-owner']else ['CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1']if historical else [],
  'native_assignment_interval':None,'native_assignment_scope_verified':False,'current_exact_member_effect_authority_verified':False,
  'actual_answering_principal_ref':None,'actual_owner_outcome':None,'authentication_to_historical_owner_link_verified':False,
  'status':'historical-admitted-bootstrap-route-found-current-native-prerequisites-unresolved'if historical else 'repository-owner-bootstrap-route-required',
  'reason':'Historical semantic-role admission is real but supplies no currently selected native Role/RoleAssignment instance, explicit interval, exact final-member scope, authenticated operator link or current release outcome.'})
members=[]
for m in matrix['members']:
 exact=by_member[m['member_ref']];a=exact['axes'];r={'member_ref':m['member_ref'],'required_roles':m['required_roles'],'member_class':exact['member_class'],
  'original_target_bindings_declared_in_pinned_public_metadata':exact['original_target_bindings'],'target_bodies_opened':False,
  'effect_selection':{k:a.get(k)for k in ['category','operation','carrier_ref','identity_ref','version_ref','original_body_scope_ref','body_binding','body_byte_sha256','decision_ref','semantic_tuple','predecessor_governance_tuple']if k in a},
  'currently_eligible_accountable_owner':None,'current_owner_authority_verified':False,'authenticated_operator_ref':None,'actual_answering_principal_ref':None,'actual_owner_outcome':None,
  'status':'BLOCKED-owner-bootstrap-or-current-assignment-prerequisite','final_successor_package_scope_frozen':False}
 members.append(r)
prerequisites=[
 {'id':'T12-P01','requirement':'Select the exact final successor base, source/profile/cut, complete member inventory and per-member effect/core bytes. Preserve the original363 rows; add all actual successor members. Old0276 metadata is historical scope, not new release authority.','owner_route':'Root assembles exact candidate package; no semantic or authority grant inferred.'},
 {'id':'T12-P02','requirement':'Resolve actual answering human/team identity and its authenticated operator/PrincipalReference link. Keep person:<vrondelli>, principal:lab-owner, principal:repository-owner and candidate development principals distinct until an explicit admitted identity/recognition route binds them.','owner_route':'Actual recognized bootstrap owner, with independently bound public identity evidence.'},
 {'id':'T12-P03','requirement':'Locate a current admitted repository-owner Role and RoleAssignment with actual assignee, interval, scope, assignment basis, permitted effects and challenge route; otherwise prepare a separate exact owner-approved bootstrap route. Historical implementation-only authorizations and principal names cannot supply this missing assignment.','owner_route':'Actual repository bootstrap owner; no role self-grant.'},
 {'id':'T12-P04','requirement':'For definition-owner, artifact-type-owner and identity-graph-owner, carry the verified historical bootstrap bindings through an explicit owner-approved current native Role/RoleAssignment route, or independently prove an eligible admitted alternative source. Verify interval, revocation/successor state, scope and per-effect exclusions fresh. Do not rewrite immutable admitted inputs or treat candidate status alone as absence of historical admission.','owner_route':'Historical bootstrap principal person:<vrondelli> under separately admitted role scopes, subject to current identity and authority verification.'},
 {'id':'T12-P05','requirement':'Expand each role only through an explicit applicable owner route when current members/effects fall outside its admitted scope. Resolve exact native governance-event materialization, definitions, artifact-type changes and identity-graph relationships separately. Shared principal identity merges none of these grants.','owner_route':'Accountable owner for each exact effect and scope.'},
 {'id':'T12-P06','requirement':'After technical and human prerequisites, obtain the actual R08 admit/reject/revise outcome for exact package bytes and stable Decision cores; no outcome may be generated, reused from historical authorization or implied by complete-plan implementation permission. Publication/deployment require separately declared approval.','owner_route':'Actual currently eligible owners through the final exact owner checkpoint.'}
]
report={'schema_version':'lab-T12-public-owner-prerequisites/v1-candidate','observed_at':datetime.now(timezone.utc).isoformat(),'task_id':'T12','SWU':'SWU-T12-01',
 'analysis_result':'PASS-public-metadata-analysis','governing_prerequisite_result':'BLOCKED-current-authority-not-verified','candidate_owner_effect_matrix':roles,'members':members,
 'original_member_count':363,'verified_current_native_required_assignments':0,'historical_bootstrap_roles_located':3,
 'selected_candidate_base':{'inspection_binding':sources[S02+'base-state-registry-history-0276.json'],'state_ref':base['original_state']['node_id'],'head_sequence':base['original_head']['sequence'],'head_transaction_digest':base['original_head']['transaction_digest'],'source_archive_binding_metadata_only':base['source_selection']['archive_binding'],'native_replay_performed_in_this_analysis':False,'canonical_global_State_claimed':False},
 'repository_public_current_lookup':{'lookup_binding':sources['authority/project-state-transitions/current.json'],'state_ref':state['node_id'],'state_binding':lookup['current_project_state'],'scope':'Immutable historical admitted runtime State lookup; distinct from the signed candidate execution branch.'},
 'operator_identity_separation':{'historical_bootstrap_owner':'person:<vrondelli>','historical_implementation_authorization_principal':'principal:lab-owner','selected_candidate_config_operator_ref':base['original_config']['owner_ref'],'candidate_base_repository_owner_principal':'principal:repository-owner','current_authenticated_operator_ref':None,'identity_alias_inferred':False},
 'history_metadata_checks':history_results,'unverified_local_runtime_authorization_references':unverified_runtime_authorization_refs,'unverified_local_runtime_material_bindings':unverified_runtime_material_refs,'unresolved_prerequisites':prerequisites,'public_metadata_checks':checks,
 'current_signed_native_replay_or_role_admission_executed':False,'private_artifact_bodies_or_keys_opened':False,'actual_Lab_Source_Service_Session_or_native_constructed':False,'runtime_lock_acquired':False,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
report_binding=save('candidate-owner-effect-matrix.json',report)
for path,row in list(sources.items()):capture(path,row['sha256'])
evidence=save('evidence.json',{'schema_version':'lab-T12-public-authority-evidence/v1-candidate','sources':list(sources.values()),'independent_fresh_source_captures_at_entry_exit':True,'checks':checks,'matrix_binding':report_binding,'no_private_body_or_native_runtime_access':True,'task_complete':False,'authority_effect':'none'})
print(json.dumps({'result':'PASS-analysis; governing prerequisites BLOCKED','original_members':363,'historical_roles':3,'verified_current_native_assignments':0,'matrix':report_binding,'evidence':evidence,'sources':len(sources)}),flush=True)

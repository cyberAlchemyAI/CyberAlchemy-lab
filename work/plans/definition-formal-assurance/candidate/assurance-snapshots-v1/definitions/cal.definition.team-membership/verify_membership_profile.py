"""Explicit hypothetical interval/currentness/history policies and actual carrier shape checks."""
import copy,json,types
from datetime import datetime
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def baseline():
 record=json.loads((b.ROOT/'authority/artifact-types/team-membership/v1/fixtures/valid/record.json').read_bytes())
 return {'record':record,'Person_hypothesis':'Human:hyp1','Team_hypothesis':'Team:hyp1','reference_resolution':{'ref':record['person_reference_ref'],'Person_hypothesis':'Human:hyp1','justification_marker':'hypothetical-reference-review:1'},'team_resolution':{'ref':record['team_ref'],'Team_hypothesis':'Team:hyp1'},'time_interpretation':'effective-period','endpoint_policy':'half-open','query_time':'2026-10-06T00:00:00Z','reference_only_conclusions':[],'independent_outcomes':[],'owner_policy_reviewed':False,'actual_Human_denotation_established':False}
def timestamp(value):return datetime.strptime(value,'%Y-%m-%dT%H:%M:%SZ')
def errors(p):
 es=[];rec=p['record'];start=end=now=None
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected candidate profile')
 ck(rec['status']=='candidate-unadmitted' and rec['authority_effect']=='none','candidate posture and non-effect retained')
 ck(p['Person_hypothesis']!=rec['node_id'] and p['Team_hypothesis']!=rec['node_id'] and p['Person_hypothesis']!=p['Team_hypothesis'],'hypothetical membership Person and Team entities distinct')
 rr=p['reference_resolution'];tr=p['team_resolution'];ck(rr['ref']==rec['person_reference_ref'] and rr['Person_hypothesis']==p['Person_hypothesis'] and bool(rr['justification_marker']),'exact hypothetical Reference-to-Person mapping explicit')
 ck(tr['ref']==rec['team_ref'] and tr['Team_hypothesis']==p['Team_hypothesis'],'exact hypothetical Team mapping explicit')
 ck(p['time_interpretation'] in ['finite-ended','effective-period'],'time-bound interpretation selected explicitly')
 ck(p['endpoint_policy'] in ['half-open','closed'],'endpoint convention selected explicitly')
 for value,key in [(rec['period']['start'],'start'),(rec['period']['end'],'end'),(p['query_time'],'query')]:
  if value is None and key=='end':continue
  try:
   dt=timestamp(value)
   if key=='start':start=dt
   elif key=='end':end=dt
   else:now=dt
  except (ValueError,TypeError):es.append('invalid selected UTC calendar '+key)
 if start is not None and end is not None:ck(start<end,'selected nonempty period has strictly ordered endpoints')
 if p['time_interpretation']=='finite-ended':ck(end is not None,'finite-ended interpretation requires explicit finite upper bound')
 ck(rec['membership_state'] in ['proposed','active','inactive','revoked'],'explicit selected lifecycle vocabulary')
 ck(all(isinstance(rec[k],str) and bool(rec[k].strip()) for k in ['basis_ref','owner_ref','owner_route','challenge_route','scope_ref']),'basis owner challenge scope explicitly recorded; authenticity not established')
 ck(rec['node_id'] not in rec['successor_refs'],'selected stronger policy rejects self-successor')
 ck(not p['reference_only_conclusions'],'membership/reference/status alone no world conclusion')
 ck(set(p['independent_outcomes'])<=set(b.OUTCOMES),'independent outcomes remain separate')
 ck(p['owner_policy_reviewed'] is False and p['actual_Human_denotation_established'] is False,'hypothetical profile never authenticates Human or owner review')
 within=None if start is None or now is None or (rec['period']['end'] is not None and end is None) or p['endpoint_policy'] not in ['half-open','closed'] else start<=now and (end is None or now<end if p['endpoint_policy']=='half-open' else end is None or now<=end)
 current=None if es or within is None else rec['membership_state']=='active' and within
 return es,{'current_under_selected_hypothetical_policy':current,'within_selected_interval':within,'time_interpretation':p['time_interpretation'],'endpoint_policy':p['endpoint_policy'],'actual_currentness_verified':False}
def controls():
 rows=[]
 def add(id,change,bad=False,current=True):
  p=baseline();change(p);es,temporal=errors(p)
  if bool(es)!=bad or temporal['current_under_selected_hypothetical_policy']!=(None if bad else current):raise ValueError('Unexpected interval profile '+id+' '+str((es,temporal)))
  if id in ['invalid-calendar-start','invalid-calendar-end','invalid-query-calendar','unselected-endpoint-policy'] and temporal['within_selected_interval'] is not None:raise ValueError('Unknown/malformed bound or convention treated as open/false interval')
  rows.append({'case_id':id,'profile':p,'errors':es,'temporal_check':temporal,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_Human_denotation_established':False,'actual_runtime_execution':False})
 add('open-ended-active-effective-period-policy',lambda p:None)
 add('open-ended-does-not-satisfy-finite-ended-interpretation',lambda p:p.update(time_interpretation='finite-ended'),True)
 add('finite-period-under-finite-ended-policy',lambda p:p.update(time_interpretation='finite-ended') or p['record']['period'].update(end='2026-10-07T00:00:00Z'))
 add('finite-period-under-effective-period-policy',lambda p:p['record']['period'].update(end='2026-10-07T00:00:00Z'))
 add('active-label-before-start-is-not-current',lambda p:p.update(query_time='2026-10-04T00:00:00Z'),current=False)
 add('at-start-inclusive-current',lambda p:p.update(query_time=p['record']['period']['start']))
 add('half-open-at-end-not-current',lambda p:p['record']['period'].update(end=p['query_time']),current=False)
 add('closed-at-end-current',lambda p:p.update(endpoint_policy='closed') or p['record']['period'].update(end=p['query_time']))
 add('after-end-not-current-despite-active-label',lambda p:p['record']['period'].update(end='2026-10-05T12:00:00Z'),current=False)
 for state in ['proposed','inactive','revoked']:add(state+'-is-not-current-even-within-period',lambda p,state=state:p['record'].update(membership_state=state),current=False)
 add('independent-outcomes-can-coexist',lambda p:p.update(independent_outcomes=b.OUTCOMES))
 add('reversed-period',lambda p:p['record']['period'].update(end='2026-10-04T00:00:00Z'),True)
 add('empty-period-selected-nonempty-policy',lambda p:p['record']['period'].update(end=p['record']['period']['start']),True)
 add('invalid-calendar-start',lambda p:p['record']['period'].update(start='2026-99-99T00:00:00Z'),True)
 add('invalid-calendar-end',lambda p:p['record']['period'].update(end='2026-99-99T00:00:00Z'),True)
 add('invalid-query-calendar',lambda p:p.update(query_time='2026-99-99T00:00:00Z'),True)
 add('unselected-endpoint-policy',lambda p:p.update(endpoint_policy='unknown'),True)
 add('unselected-time-bound-interpretation',lambda p:p.update(time_interpretation='unknown'),True)
 add('reference-mapping-wrong-Person',lambda p:p['reference_resolution'].update(Person_hypothesis='other'),True)
 add('reference-mapping-wrong-token',lambda p:p['reference_resolution'].update(ref='other'),True)
 add('reference-mapping-missing-justification-marker',lambda p:p['reference_resolution'].update(justification_marker=''),True)
 add('Team-mapping-wrong-token',lambda p:p['team_resolution'].update(ref='other'),True)
 add('Team-mapping-wrong-entity',lambda p:p['team_resolution'].update(Team_hypothesis='other'),True)
 add('membership-collapsed-with-Person',lambda p:p.update(Person_hypothesis=p['record']['node_id']),True)
 add('membership-collapsed-with-Team',lambda p:p.update(Team_hypothesis=p['record']['node_id']),True)
 add('self-successor-not-selected-policy',lambda p:p['record']['successor_refs'].append(p['record']['node_id']),True)
 for key in ['basis_ref','owner_ref','owner_route','challenge_route','scope_ref']:add('empty-'+key,lambda p,key=key:p['record'].__setitem__(key,' '),True)
 for n in b.OUTCOMES:add('membership-alone-not-'+n,lambda p,n=n:p.update(reference_only_conclusions=[n]),True)
 add('authority-effect-not-membership',lambda p:p['record'].update(authority_effect='grant'),True)
 add('owner-review-not-invented',lambda p:p.update(owner_policy_reviewed=True),True)
 add('actual-Human-verification-not-invented',lambda p:p.update(actual_Human_denotation_established=True),True)
 return rows
def frames():
 rows=[]
 def baseline_frame():
  record=baseline()['record'];record['membership_state']='proposed'
  return {'operation':'activate','before':record,'after':{**copy.deepcopy(record),'membership_state':'active'},'decision_marker':'Decision:hyp-activate','old_record_retained':True,'before_Team_identity':'Team:hyp1','after_Team_identity':'Team:hyp1','before_Person_identity':'Human:hyp1','after_Person_identity':'Human:hyp1','before_authority':[],'after_authority':[],'separate_authority_decision_ref':None,'successor':None}
 def check(f):
  es=[];a=f['before'];z=f['after']
  if f['operation'] not in ['activate','deactivate','revoke','supersede']:es.append('operation outside selected policy')
  for key in ['node_id','person_reference_ref','team_ref','scope_ref','basis_ref','owner_route']:
   if a[key]!=z[key]:es.append('selected same membership preserves '+key)
  if a['period']['start']!=z['period']['start']:es.append('selected history retains start')
  if f['before_Team_identity']!=f['after_Team_identity'] or f['before_Person_identity']!=f['after_Person_identity']:es.append('membership step does not retarget endpoints or Team identity')
  if not f['old_record_retained'] or not f['decision_marker']:es.append('retained prior record and hypothetical decision required')
  if f['operation']=='activate' and (a['membership_state']!='proposed' or z['membership_state']!='active' or z['period']['end'] is not None):es.append('selected proposed-to-active open-ended frame')
  if f['operation'] in ['deactivate','revoke']:
   if a['membership_state']!='active' or z['membership_state']!=('inactive' if f['operation']=='deactivate' else 'revoked') or z['period']['end'] is None:es.append('selected terminating step requires explicit closing end and exact state')
   elif timestamp(z['period']['end'])<=timestamp(z['period']['start']):es.append('closing time strictly follows start')
  if f['operation']=='supersede':
   successor=f['successor']
   if successor is None or successor['node_id']==a['node_id'] or successor['node_id'] not in z['successor_refs'] or successor['person_reference_ref']!=a['person_reference_ref'] or successor['team_ref']!=a['team_ref'] or successor['scope_ref']!=a['scope_ref']:es.append('explicit fresh scoped successor with same endpoints')
  if f['before_authority']!=f['after_authority'] and f['separate_authority_decision_ref'] is None:es.append('membership lifecycle alone does not change authority')
  return es
 def add(id,change,bad=False):
  f=baseline_frame();change(f);es=check(f)
  if bool(es)!=bad:raise ValueError('Unexpected membership frame '+id+' '+str(es))
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('proposed-to-active-same-membership-and-endpoints',lambda f:None)
 def terminate(f,operation='deactivate'):f.update(operation=operation);f['before']['membership_state']='active';f['after'].update(membership_state='inactive' if operation=='deactivate' else 'revoked');f['after']['period']['end']='2026-10-07T00:00:00Z'
 add('deactivate-with-history-and-explicit-close',terminate)
 add('revoke-with-history-and-explicit-close',lambda f:terminate(f,'revoke'))
 def successor(f):f.update(operation='supersede',successor={**copy.deepcopy(f['before']),'node_id':'Membership:hyp-successor'});f['after']['successor_refs']=['Membership:hyp-successor']
 add('explicit-fresh-same-endpoint-successor',successor)
 add('independent-authority-decision-can-coexist',lambda f:f.update(after_authority=['Permission:hyp1'],separate_authority_decision_ref='Decision:hyp-permission'))
 for key in ['node_id','person_reference_ref','team_ref','scope_ref','basis_ref','owner_route']:add('activation-changes-'+key,lambda f,key=key:f['after'].__setitem__(key,'other'),True)
 add('activation-rewrites-start',lambda f:f['after']['period'].update(start='2026-10-06T00:00:00Z'),True)
 add('activation-retargets-Person',lambda f:f.update(after_Person_identity='other'),True)
 add('membership-step-changes-Team-identity',lambda f:f.update(after_Team_identity='other'),True)
 add('history-discarded',lambda f:f.update(old_record_retained=False),True)
 add('missing-hypothetical-decision',lambda f:f.update(decision_marker=''),True)
 add('membership-grants-authority',lambda f:f.update(after_authority=['Permission:hyp1']),True)
 add('membership-revokes-authority',lambda f:f.update(before_authority=['Permission:hyp1']),True)
 add('termination-without-close',lambda f:terminate(f) or f['after']['period'].update(end=None),True)
 add('termination-close-before-start',lambda f:terminate(f) or f['after']['period'].update(end='2026-10-04T00:00:00Z'),True)
 add('supersede-without-successor',lambda f:f.update(operation='supersede'),True)
 add('supersede-with-self',lambda f:successor(f) or f['successor'].update(node_id=f['before']['node_id']),True)
 add('unselected-operation',lambda f:f.update(operation='grant-role'),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();root=b.ROOT/'authority/artifact-types/team-membership/v1'
 paths={'descriptor':root/'artifact.json','schema':root/'schema.json','fixture':root/'fixtures/valid/record.json','artifact_projection':root/'ARTIFACT.md','fixture_projection':root/'fixtures/valid/RECORD.md','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','generator':b.ROOT/'tooling/generators/artifact_surface.py','shared_validator':b.ROOT/'tooling/validators/artifact_surface.py','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json','refinement':b.ROOT/'authority/artifact-types/candidates/0004-remaining-26-materialization/refinements/type.team-membership.json'}
 for p in sorted((root/'fixtures/invalid').glob('*.json')):paths['negative_'+p.stem]=p
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());tr=next(x for x in reg['admitted_contracts'] if x['semantic_kind']=='typed-relation' and x['lifecycle_state']=='admitted-current');paths['TR_schema']=b.ROOT/tr['schema_path'];paths['TR_fixture']=(b.ROOT/tr['artifact_path']).parent/'fixtures/valid/record.json'
 for semantic in ['person-reference','team']:
  row=next(x for x in reg['admitted_contracts'] if x['semantic_kind']==semantic and x['lifecycle_state']=='admitted-current');paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=(b.ROOT/row['artifact_path']).parent/'fixtures/valid/record.json'
 kinds={}
 for id in ['relation.member-of','relation.successor-of','relation.challenges']:
  row=next(x for x in kr['entries'] if x['relation_kind_ref']==id);kinds[id]=row;paths[id]=b.ROOT/row['instance_path']
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};artifact=docs['descriptor'];fixture=docs['fixture'];schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 entry=next(x for x in reg['admitted_contracts'] if x['artifact_type_ref']==artifact['artifact_type_ref']);source=load('t.json')['payload']['source'];binding=artifact['semantic_definition_bindings'][0]
 ck('exact-current-Type-overlay-0070',entry['lifecycle_state']=='admitted-current' and entry['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and entry['artifact_sha256']==refs['descriptor']['sha256'] and entry['schema_sha256']==refs['schema']['sha256'])
 ck('historical-candidate-wording-retained',artifact['status']==fixture['status']=='candidate-unadmitted' and artifact['authority_effect']==fixture['authority_effect']=='none')
 ck('exact-admitted-Definition-0053-binding',binding['definition_ref']==source['version_ref'] and binding['path']==source['path'] and binding['sha256']==source['sha256'] and binding['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION')
 ck('root-descriptor-and-closed-schema-bound',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'] and artifact['schema_digest']==refs['schema']['sha256'] and schema['additionalProperties'] is False)
 ck('shared-renderer-validator-digests',artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['shared_validator']['sha256'])
 ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 negative=[{'path':refs[n]['path'],'schema_rejected':bool(list(validator.iter_errors(docs[n])))} for n in sorted(refs) if n.startswith('negative_')];ck('four-hostiles-rejected',len(negative)==4 and all(x['schema_rejected'] for x in negative))
 mod=types.ModuleType('_bound_artifact_renderer');mod.__file__=str(paths['generator']);exec(compile(raws['generator'],str(paths['generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture])
 ck('two-artifact-renders-exact-projection',mod.render_artifact(artifact).encode()==mod.render_artifact(artifact).encode()==raws['artifact_projection']);ck('two-fixture-renders-exact-projection',mod.render_instance(artifact,fixture).encode()==mod.render_instance(artifact,fixture).encode()==raws['fixture_projection']);ck('renderers-preserve-inputs',before==[artifact,fixture]);ck('refinement-separate-lifecycle-basis-period-not-admission',docs['refinement']['target_id']=='type.team-membership' and docs['refinement']['admission_effect']=='none')
 for semantic in ['person-reference','team']:ck(semantic+'-fixture-shape-valid',not list(b.c.Draft202012Validator(docs[semantic+'_schema']).iter_errors(docs[semantic+'_fixture'])))
 joins={'PersonReference_literal_node_matches':fixture['person_reference_ref']==docs['person-reference_fixture']['node_id'],'Team_literal_node_matches':fixture['team_ref']==docs['team_fixture']['node_id'],'Team_literal_membership_reverse_link_matches':fixture['node_id'] in docs['team_fixture']['membership_refs'],'literal_scopes_match':fixture['scope_ref']==docs['person-reference_fixture']['scope_ref']==docs['team_fixture']['scope_ref'],'actual_Human_denotation_verified':False,'actual_currentness_basis_attribution_verified':False}
 ck('literal-fixture-joins-do-not-authenticate-Human-or-membership',joins=={'PersonReference_literal_node_matches':True,'Team_literal_node_matches':True,'Team_literal_membership_reverse_link_matches':True,'literal_scopes_match':True,'actual_Human_denotation_verified':False,'actual_currentness_basis_attribution_verified':False})
 probes=[]
 def probe(id,change,expected):
  rec=copy.deepcopy(fixture);change(rec);es=list(validator.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected membership schema '+id+' '+str([x.message for x in es]))
  probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_Human_denotation_established':False,'actual_currentness_or_interval_enforced':False,'actual_runtime_execution':False,'whole_source_conformance_established':False})
 probe('unresolved-PersonReference-token-accepted',lambda r:r.update(person_reference_ref='absent:Reference'),True)
 probe('unresolved-Team-token-accepted',lambda r:r.update(team_ref='absent:Team'),True)
 probe('unreviewed-basis-token-accepted',lambda r:r.update(basis_ref='absent:Decision'),True)
 probe('invalid-calendar-shape-accepted',lambda r:r['period'].update(start='2026-99-99T99:99:99Z'),True)
 probe('future-start-active-label-shape-accepted',lambda r:r['period'].update(start='2099-01-01T00:00:00Z'),True)
 probe('inactive-reversed-period-shape-accepted',lambda r:r.update(membership_state='inactive') or r['period'].update(end='2026-10-04T00:00:00Z'),True)
 probe('revoked-open-end-shape-accepted',lambda r:r.update(membership_state='revoked'),True)
 probe('self-successor-token-shape-accepted',lambda r:r['successor_refs'].append(r['node_id']),True)
 probe('membership-node-equals-reference-token-shape-accepted',lambda r:r.update(node_id=r['person_reference_ref']),True)
 probe('proposed-past-period-shape-accepted',lambda r:r.update(membership_state='proposed') or r['period'].update(end='2026-10-06T00:00:00Z'),True)
 probe('authority-effect-rejected',lambda r:r.update(authority_effect='grant'),False)
 probe('extra-derived-role-field-rejected',lambda r:r.update(role_ref='Role:hyp1'),False)
 probe('active-finite-end-rejected-by-current-schema',lambda r:r['period'].update(end='2026-10-07T00:00:00Z'),False)
 probe('duplicate-successor-tokens-rejected',lambda r:r.update(successor_refs=['same','same']),False)
 probe('blank-basis-rejected',lambda r:r.update(basis_ref=' '),False)
 probe('extra-period-field-rejected',lambda r:r['period'].update(timezone='UTC'),False)
 probe('timestamp-format-rejected',lambda r:r['period'].update(start='not-a-time'),False)
 probe('missing-owner-route-rejected',lambda r:r.pop('owner_route'),False)
 for id,row in kinds.items():
  payload=docs[id]['payload'];ck('current-exact-Kind-'+id,row['lifecycle_state']=='admitted-current' and row['instance_sha256']==refs[id]['sha256'] and row['exact_endpoint_pair_count']==len(payload['allowed_endpoint_pairs']) and row['required_qualifier_axes']==payload['qualifier_contract']['required_axes'])
 kp=docs['relation.member-of']['payload'];ck('current-24-member-of-pairs-include-Reference-Team-with-exact-qualifier',len(kp['allowed_endpoint_pairs'])==24 and {'source_kind':'person-reference','target_kind':'team'} in kp['allowed_endpoint_pairs'] and not any(x['target_kind']=='team' and x['source_kind'] in ['person','team-membership'] for x in kp['allowed_endpoint_pairs']) and kp['qualifier_contract']['required_axes']==['membership_role'] and kinds['relation.member-of']['admission_decision_ref']=='CAL-DECISION-0074C-GOVERNANCE-RELATION-SURFACE-ADMISSION');ck('member-of-forbids-assignment-authority-identity-equivalence',kp['forbidden_inferences']==['contribution','assignment','authority','identity-equivalence']);ck('current-TR-v3-schema-bound',tr['artifact_type_ref']=='cal.artifact-type.typed-relation/v3' and tr['schema_sha256']==refs['TR_schema']['sha256'])
 def matching_condition(x):
  if isinstance(x,dict):return x.get('const')=='relation.member-of' or any(matching_condition(z) for z in x.values())
  if isinstance(x,list):return any(matching_condition(z) for z in x)
  return False
 def conditions(x):
  rows=[]
  if isinstance(x,dict):
   if 'if' in x and matching_condition(x['if']):rows.append(x)
   for value in x.values():rows+=conditions(value)
  elif isinstance(x,list):
   for value in x:rows+=conditions(value)
  return rows
 bound_conditions=conditions(docs['TR_schema'])
 if len(bound_conditions)!=1:raise ValueError('Ambiguous exact member-of schema condition')
 arms=bound_conditions[0]['then']['properties']['payload']['oneOf'];schema_pairs=[{'source_kind':x['properties']['source']['properties']['kind']['const'],'target_kind':x['properties']['target']['properties']['kind']['const']} for x in arms]
 pair_key=lambda x:(x['source_kind'],x['target_kind'])
 missing_pairs=sorted([x for x in kp['allowed_endpoint_pairs'] if x not in schema_pairs],key=pair_key);extra_pairs=sorted([x for x in schema_pairs if x not in kp['allowed_endpoint_pairs']],key=pair_key)
 ck('current-Kind24-versus-TR23-exact-DecisionBundle-gap-retained',len(schema_pairs)==23 and missing_pairs==[{'source_kind':'decision','target_kind':'decision-bundle'}] and extra_pairs==[])
 relation=copy.deepcopy(docs['TR_fixture']);relation['payload'].update(relation_kind_ref='relation.member-of',source={'kind':'person-reference','ref':fixture['person_reference_ref'],'version_ref':'Reference@hyp'},target={'kind':'team','ref':fixture['team_ref'],'version_ref':'Team@hyp'},qualifiers={'membership_role':'member'});tv=b.c.Draft202012Validator(docs['TR_schema']);relation_probes=[]
 def rp(id,change,expected):
  rec=copy.deepcopy(relation);change(rec);es=list(tv.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected member-of shape '+id+' '+str([x.message for x in es]))
  relation_probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_Human_denotation_established':False,'actual_relation_created':False,'whole_source_conformance_established':False})
 rp('Reference-to-Team-member-of-shape-valid-no-Membership-artifact-binding',lambda r:None,True)
 rp('membership-role-owner-label-does-not-create-RoleAssignment',lambda r:r['payload']['qualifiers'].update(membership_role='owner'),True)
 rp('unresolved-reference-token-shape-accepted',lambda r:r['payload']['source'].update(ref='absent:Reference'),True)
 rp('unresolved-Team-token-shape-accepted',lambda r:r['payload']['target'].update(ref='absent:Team'),True)
 rp('Person-endpoint-not-member-of-pair',lambda r:r['payload']['source'].update(kind='person'),False)
 rp('Membership-endpoint-not-member-of-pair',lambda r:r['payload']['source'].update(kind='team-membership'),False)
 rp('missing-required-membership-role-rejected',lambda r:r['payload'].update(qualifiers={}),False)
 rp('extra-Membership-artifact-binding-qualifier-rejected',lambda r:r['payload']['qualifiers'].update(membership_ref=fixture['node_id']),False)
 rp('Reference-to-Project-cross-product-pair-rejected',lambda r:r['payload']['target'].update(kind='project'),False)
 rp('current-Kind-Decision-to-DecisionBundle-pair-rejected-by-TR23-schema',lambda r:r['payload'].update(source={'kind':'decision','ref':'Decision:hyp','version_ref':'Decision@hyp'},target={'kind':'decision-bundle','ref':'Bundle:hyp','version_ref':'Bundle@hyp'}),False)
 pair_observations=[]
 for pair in kp['allowed_endpoint_pairs']:
  rec=copy.deepcopy(relation);rec['payload']['source'].update(kind=pair['source_kind']);rec['payload']['target'].update(kind=pair['target_kind']);es=list(tv.iter_errors(rec));accepted=not es
  if accepted!=(pair in schema_pairs):raise ValueError('Actual schema differs from extracted exact pair condition')
  pair_observations.append({'pair':pair,'schema_accepted':accepted,'errors':[x.message for x in es],'model_record':rec,'actual_relation_created':False,'whole_catalog_alignment_established':False})
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();history=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_membership_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=json.loads((b.BASE/'definitions/cal.definition.person/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-membership-profile/v1-candidate','status':'PASS-for-explicit-hypothetical-period-currentness-history-and-current-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_history_frame_count':len(history),'rejected_history_frames':sum(x['expected_rejection'] for x in history),'finite_history_frames':history,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'actual_relation_schema_probes':relation_probes,'negative_fixture_checks':negative,'actual_join_observations':joins,'actual_relation_endpoint_pairs':kp['allowed_endpoint_pairs'],'TR_member_of_schema_pairs':schema_pairs,'current_Kind_TR_pair_observations':pair_observations,'current_Kind_TR_schema_gap':{'current_Kind_pairs':24,'current_TR_schema_pairs':23,'missing_TR_pairs':missing_pairs,'extra_TR_pairs':extra_pairs,'alignment_reviewed':False},'period_source_carrier_gap':'time-bounded target versus active carrier requiring null end; finite-ended/effective-period and endpoint/currentness meanings need review','relation_membership_mapping_gap':'member-of binds Reference to Team with membership_role string; no independent Membership artifact or period/basis/currentness binding in this exact closed qualifier contract','source_mapping_gaps':{'actual_PersonReference_Human_Team_and_membership_denotation_reviewed':False,'period_clock_endpoint_currentness_semantics_reviewed':False,'basis_owner_attribution_and_authority_authenticated':False,'lifecycle_history_Team_frame_and_succession_policy_reviewed':False,'source_precedence_and_relation_mapping_reviewed':False,'whole_source_conformance_established':False},'new_Person_Team_memberships_or_relations_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Hypothetical finite/effective interval comparison with explicit UTC and endpoint policy, stronger lifecycle/history frames and exact current schema/fixture/projection/Kind observations. Literal fixture joins and synthetic decision/resolver markers do not authenticate Person/Team/membership/currentness/authority. Current Kind24 versus TR23 gap retained; no whole catalog closure. No selected final source time interpretation, actual operational/history proof, real membership/relation/admission/world effect or whole-definition acceptance.'}
 if write:b.put('membership-profile-checks.json',report)
 elif not b.r.same_json(report,load('membership-profile-checks.json')):raise ValueError('Fresh membership profile differs')
 return report
def main():
 report=verify('--write' in b.sys.argv);print(json.dumps({k:report[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

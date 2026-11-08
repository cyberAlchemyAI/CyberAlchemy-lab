"""Hypothetical current-member/owner profiles, Team frames and actual carrier observations."""
import copy,json,types
from datetime import datetime
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def baseline():
 root=b.ROOT/'authority/artifact-types';rec=json.loads((root/'team/v1/fixtures/valid/record.json').read_bytes());m=json.loads((root/'team-membership/v1/fixtures/valid/record.json').read_bytes())
 return {'record':rec,'Team_entity':'Team:hyp1','carrier_entity':'Record:Team:hyp1','owner_qualification':{'team_ref':rec['node_id'],'scope_ref':rec['scope_ref'],'owner_route':rec['owner_route'],'justification_marker':'hypothetical-owner-qualification:1'},'membership_resolution':{m['node_id']:{'record':m,'membership_entity':'Membership:hyp1','reference_token':m['person_reference_ref'],'Person_entity':'Human:hyp1','reference_resolution_marker':'hypothetical-Person-reference-resolution:1'}},'query_time':'2026-10-06T00:00:00Z','reference_only_conclusions':[],'independent_outcomes':[],'owner_policy_reviewed':False,'actual_collective_Human_and_owner_verified':False}
def stamp(value):return datetime.strptime(value,'%Y-%m-%dT%H:%M:%SZ')
def errors(p):
 es=[];rec=p['record'];resolved=[];now=None
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected profile')
 ck(rec['status']=='candidate-unadmitted' and rec['authority_effect']=='none','candidate posture/non-effect retained')
 ck(p['Team_entity']!=p['carrier_entity'],'hypothetical collective entity distinct from machine carrier')
 ck(all(isinstance(rec[k],str) and bool(rec[k].strip()) for k in ['node_id','name','purpose','scope_ref','identity_boundary','owner_ref','owner_route','challenge_route']),'explicit nonempty selected metadata; values not authenticated')
 q=p['owner_qualification'];ck(q['team_ref']==rec['node_id'] and q['scope_ref']==rec['scope_ref'] and q['owner_route']==rec['owner_route'] and bool(q['justification_marker']),'exact hypothetical owner qualification, scope and route')
 ck(rec['lifecycle_state'] in ['proposed','active','suspended','retired','superseded'],'selected Team lifecycle vocabulary')
 ck(rec['node_id'] not in rec['successor_refs'],'selected stronger policy rejects self-successor')
 if rec['lifecycle_state']=='superseded':ck(bool(rec['successor_refs']),'selected stronger superseded-Team policy requires explicit successor')
 try:now=stamp(p['query_time'])
 except (ValueError,TypeError):es.append('invalid selected UTC query calendar')
 for token in rec['membership_refs']:
  row=p['membership_resolution'].get(token)
  if row is None:resolved.append({'token':token,'status':'unresolved-record','current_under_hypothesis':None});continue
  m=row['record'];status='resolved-hypothetical-record';within=current=None;issues=[]
  if m['node_id']!=token:issues.append('resolved-node-token-mismatch')
  if m['team_ref']!=rec['node_id']:issues.append('different-Team')
  if m['scope_ref']!=rec['scope_ref']:issues.append('different-selected-scope')
  if row['reference_token']!=m['person_reference_ref']:issues.append('different-PersonReference-token')
  if not row['reference_resolution_marker'] or not row['Person_entity']:issues.append('unresolved-Person-denotation')
  if row['membership_entity'] in [p['Team_entity'],row['Person_entity']] or row['Person_entity']==p['Team_entity']:issues.append('collapsed-membership-or-Person-entity')
  start=end=None;end_known=m['period']['end'] is None
  try:start=stamp(m['period']['start'])
  except (ValueError,TypeError):issues.append('invalid-start-calendar')
  if m['period']['end'] is not None:
   try:end=stamp(m['period']['end']);end_known=True
   except (ValueError,TypeError):issues.append('invalid-end-calendar')
  if start is not None and end is not None and end<=start:issues.append('nonordered-selected-period')
  if start is not None and now is not None and end_known:within=start<=now and (end is None or now<end)
  if not issues and within is not None:current=m['membership_state']=='active' and within
  if issues:status='unresolved-or-invalid-selected-binding'
  resolved.append({'token':token,'status':status,'issues':issues,'within_selected_half_open_effective_period':within,'current_under_hypothesis':current,'Person_entity':row['Person_entity'],'actual_currentness_or_Human_verified':False})
 current=[x for x in resolved if x['current_under_hypothesis'] is True]
 if rec['lifecycle_state']=='active':ck(bool(current),'active Team needs at least one exact resolved hypothetical current membership/Person')
 ck(not p['reference_only_conclusions'],'Team/membership/owner labels alone no selected world conclusion')
 ck(set(p['independent_outcomes'])<=set(b.OUTCOMES),'independent world outcomes separate')
 ck(p['owner_policy_reviewed'] is False and p['actual_collective_Human_and_owner_verified'] is False,'hypothetical profile never creates owner or actual entity verification')
 return es,{'listed_refs':len(rec['membership_refs']),'current_hypothetical_witnesses':len(current),'resolved_rows':resolved,'actual_currentness_verified':False,'complete_actual_membership_catalog_verified':False,'period_policy':'hypothetical-effective-period-half-open-UTC; source time-bound interpretation remains unreviewed'}
def controls():
 rows=[]
 def add(id,change,bad=False,current=1):
  p=baseline();change(p);es,detail=errors(p)
  if bool(es)!=bad or detail['current_hypothetical_witnesses']!=current:raise ValueError('Unexpected Team profile '+id+' '+str((es,detail)))
  if id=='invalid-nonnull-end-is-unknown-not-open' and detail['resolved_rows'][0]['within_selected_half_open_effective_period'] is not None:raise ValueError('Invalid end became open/false interval')
  rows.append({'case_id':id,'profile':p,'errors':es,'membership_check':detail,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_collective_Human_owner_denotation_established':False,'actual_runtime_execution':False})
 add('active-Team-one-hypothetical-resolved-current-witness',lambda p:None)
 def extra(p,state='inactive'):
  token='Membership:hyp2';r=copy.deepcopy(next(iter(p['membership_resolution'].values())));r['record'].update(node_id=token,membership_state=state);r['membership_entity']='Membership:hyp2';p['record']['membership_refs'].append(token);p['membership_resolution'][token]=r
 add('one-current-plus-one-inactive-ref-permitted',extra)
 add('one-current-plus-one-unresolved-ref-permitted-not-whole-catalog-closure',lambda p:p['record']['membership_refs'].append('absent:Membership'))
 add('two-current-witnesses-permitted',lambda p:extra(p,'active'),current=2)
 add('proposed-Team-with-no-members-permitted',lambda p:p['record'].update(lifecycle_state='proposed',membership_refs=[]),current=0)
 add('retired-Team-with-no-members-permitted',lambda p:p['record'].update(lifecycle_state='retired',membership_refs=[]),current=0)
 add('independent-world-facts-allowed',lambda p:p.update(independent_outcomes=b.OUTCOMES))
 add('display-name-change-preserves-selected-boundary',lambda p:p['record'].update(name='Other functional label'))
 add('active-Team-empty-ref-list',lambda p:p['record'].update(membership_refs=[]),True,0)
 add('active-Team-only-unresolved-token',lambda p:p['record'].update(membership_refs=['absent:Membership']),True,0)
 def member(p):return next(iter(p['membership_resolution'].values()))
 add('active-Team-before-membership-start',lambda p:p.update(query_time='2026-10-04T00:00:00Z'),True,0)
 add('active-Team-after-membership-end',lambda p:member(p)['record']['period'].update(end='2026-10-05T12:00:00Z'),True,0)
 add('active-Team-half-open-exact-end',lambda p:member(p)['record']['period'].update(end=p['query_time']),True,0)
 for state in ['proposed','inactive','revoked']:add('active-Team-only-'+state+'-membership',lambda p,state=state:member(p)['record'].update(membership_state=state),True,0)
 add('resolved-membership-wrong-Team',lambda p:member(p)['record'].update(team_ref='other:Team'),True,0)
 add('resolved-membership-wrong-selected-scope',lambda p:member(p)['record'].update(scope_ref='other:Scope'),True,0)
 add('resolved-record-token-mismatch',lambda p:member(p)['record'].update(node_id='other:Membership'),True,0)
 add('resolved-PersonReference-token-mismatch',lambda p:member(p).update(reference_token='other:Reference'),True,0)
 add('unresolved-Person-denotation-marker',lambda p:member(p).update(reference_resolution_marker=''),True,0)
 add('membership-entity-collapsed-with-Team',lambda p:member(p).update(membership_entity=p['Team_entity']),True,0)
 add('Person-entity-collapsed-with-Team',lambda p:member(p).update(Person_entity=p['Team_entity']),True,0)
 add('invalid-start-calendar',lambda p:member(p)['record']['period'].update(start='2026-99-99T00:00:00Z'),True,0)
 add('invalid-nonnull-end-is-unknown-not-open',lambda p:member(p)['record']['period'].update(end='2026-99-99T00:00:00Z'),True,0)
 add('invalid-query-calendar',lambda p:p.update(query_time='2026-99-99T00:00:00Z'),True,0)
 add('Team-collapsed-with-machine-carrier',lambda p:p.update(carrier_entity=p['Team_entity']),True)
 for key in ['purpose','scope_ref','owner_route','identity_boundary','challenge_route']:add('empty-'+key,lambda p,key=key:p['record'].__setitem__(key,' '),True,current=0 if key=='scope_ref' else 1)
 add('owner-qualification-wrong-Team',lambda p:p['owner_qualification'].update(team_ref='other'),True)
 add('owner-qualification-wrong-scope',lambda p:p['owner_qualification'].update(scope_ref='other'),True)
 add('owner-qualification-wrong-route',lambda p:p['owner_qualification'].update(owner_route='other'),True)
 add('owner-qualification-marker-missing',lambda p:p['owner_qualification'].update(justification_marker=''),True)
 add('self-successor-not-selected-policy',lambda p:p['record']['successor_refs'].append(p['record']['node_id']),True)
 add('superseded-without-successor-not-selected-policy',lambda p:p['record'].update(lifecycle_state='superseded'),True)
 for n in b.OUTCOMES:add('Team-alone-not-'+n,lambda p,n=n:p.update(reference_only_conclusions=[n]),True)
 add('authority-effect-not-Team-metadata',lambda p:p['record'].update(authority_effect='grant'),True)
 add('owner-review-not-invented',lambda p:p.update(owner_policy_reviewed=True),True)
 add('actual-collective-owner-Human-verification-not-invented',lambda p:p.update(actual_collective_Human_and_owner_verified=True),True)
 return rows
def frames():
 rows=[]
 def baseline_frame():
  rec=baseline()['record'];z=copy.deepcopy(rec);z['membership_refs']=['Membership:hyp-successor']
  return {'operation':'change-members','before':rec,'after':z,'before_Team_entity':'Team:hyp1','after_Team_entity':'Team:hyp1','before_current_People':['Human:hyp1'],'after_current_People':['Human:hyp2'],'old_record_retained':True,'membership_decision_marker':'Decision:hyp-membership','separate_assignment_decision_marker':None,'before_authority':[],'after_authority':[],'separate_authority_decision_marker':None,'successor':None,'succession_effect':None}
 def check(f):
  es=[];a=f['before'];z=f['after']
  if f['operation'] not in ['change-members','change-label','retire','supersede']:es.append('operation outside selected Team frame')
  for key in ['node_id','purpose','scope_ref','owner_route','owner_ref','identity_boundary']:
   if a[key]!=z[key]:es.append('selected stable-boundary Team frame preserves '+key)
  if f['before_Team_entity']!=f['after_Team_entity']:es.append('selected continuing Team Entity unchanged')
  if not f['old_record_retained']:es.append('prior Team/member projection retained')
  if f['operation']=='change-members' and not f['membership_decision_marker']:es.append('hypothetical independently governed membership change marker required')
  if (a['role_assignment_refs']!=z['role_assignment_refs'] or a['responsibility_refs']!=z['responsibility_refs']) and f['separate_assignment_decision_marker'] is None:es.append('membership change alone does not alter independent assignments')
  if f['before_authority']!=f['after_authority'] and f['separate_authority_decision_marker'] is None:es.append('Team/member metadata alone does not change independent authority')
  if f['operation']=='change-label' and (a['membership_refs']!=z['membership_refs'] or a['lifecycle_state']!=z['lifecycle_state']):es.append('selected label edit preserves members and lifecycle')
  if f['operation']=='retire' and z['lifecycle_state']!='retired':es.append('retirement exact state')
  if f['operation']=='supersede':
   s=f['successor']
   if z['lifecycle_state']!='superseded' or s is None or s['node_id']==a['node_id'] or s['node_id'] not in z['successor_refs'] or f['succession_effect']!='supersedes':es.append('explicit fresh successor and replacement effect required by selected stronger policy')
  return es
 def add(id,change,bad=False):
  f=baseline_frame();change(f);es=check(f)
  if bool(es)!=bad:raise ValueError('Unexpected Team frame '+id+' '+str(es))
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('actual-hypothetical-Person-set-changes-same-Team-boundary',lambda f:None)
 add('fresh-membership-record-same-Person-set-also-preserves-Team',lambda f:f.update(after_current_People=f['before_current_People']))
 add('separate-assignment-decision-can-coexist',lambda f:f['after']['role_assignment_refs'].append('Assignment:hyp2') or f.update(separate_assignment_decision_marker='Decision:hyp-assignment'))
 add('separate-authority-decision-can-coexist',lambda f:f.update(after_authority=['Permission:hyp'],separate_authority_decision_marker='Decision:hyp-authority'))
 add('retirement-does-not-automatically-revoke-independent-authority',lambda f:f.update(operation='retire') or f['after'].update(lifecycle_state='retired'))
 add('functional-label-edit-same-boundary-and-members',lambda f:f.update(operation='change-label') or f['after'].update(name='Other functional label',membership_refs=f['before']['membership_refs']))
 def successor(f):f.update(operation='supersede',successor={**copy.deepcopy(f['before']),'node_id':'Team:hyp-successor'},succession_effect='supersedes');f['after'].update(lifecycle_state='superseded',successor_refs=['Team:hyp-successor'])
 add('explicit-fresh-successor-replacement-not-identity-equality',successor)
 for key in ['node_id','purpose','scope_ref','owner_route','owner_ref','identity_boundary']:add('membership-step-changes-'+key,lambda f,key=key:f['after'].__setitem__(key,'other'),True)
 add('membership-step-changes-Team-Entity',lambda f:f.update(after_Team_entity='other'),True)
 add('prior-history-discarded',lambda f:f.update(old_record_retained=False),True)
 add('membership-change-marker-missing',lambda f:f.update(membership_decision_marker=''),True)
 add('membership-alone-adds-role-assignment',lambda f:f['after']['role_assignment_refs'].append('Assignment:hyp2'),True)
 add('membership-alone-adds-responsibility',lambda f:f['after']['responsibility_refs'].append('Responsibility:hyp2'),True)
 add('membership-alone-grants-authority',lambda f:f.update(after_authority=['Permission:hyp']),True)
 add('membership-alone-revokes-authority',lambda f:f.update(before_authority=['Permission:hyp']),True)
 add('label-edit-changes-members',lambda f:f.update(operation='change-label'),True)
 add('retirement-wrong-state',lambda f:f.update(operation='retire'),True)
 add('superseded-without-successor',lambda f:f.update(operation='supersede') or f['after'].update(lifecycle_state='superseded'),True)
 add('succession-without-replacement-effect',lambda f:successor(f) or f.update(succession_effect='continues'),True)
 add('succession-self-reference',lambda f:successor(f) or f['successor'].update(node_id=f['before']['node_id']),True)
 add('unselected-operation',lambda f:f.update(operation='grant-authority'),True)
 return rows

def relation_conditions(schema,kind):
 def mentions(x):
  if isinstance(x,dict):return x.get('const')==kind or any(mentions(y) for y in x.values())
  if isinstance(x,list):return any(mentions(y) for y in x)
  return False
 def visit(x):
  result=[]
  if isinstance(x,dict):
   if 'if' in x and mentions(x['if']):result.append(x)
   for y in x.values():result+=visit(y)
  elif isinstance(x,list):
   for y in x:result+=visit(y)
  return result
 found=visit(schema)
 if len(found)!=1:raise ValueError('Ambiguous exact relation schema condition '+kind)
 return [{'source_kind':arm['properties']['source']['properties']['kind']['const'],'target_kind':arm['properties']['target']['properties']['kind']['const']} for arm in found[0]['then']['properties']['payload']['oneOf']]

def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();root=b.ROOT/'authority/artifact-types/team/v1'
 paths={'descriptor':root/'artifact.json','schema':root/'schema.json','fixture':root/'fixtures/valid/record.json','artifact_projection':root/'ARTIFACT.md','fixture_projection':root/'fixtures/valid/RECORD.md','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','generator':b.ROOT/'tooling/generators/artifact_surface.py','shared_validator':b.ROOT/'tooling/validators/artifact_surface.py','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'}
 for p in sorted((root/'fixtures/invalid').glob('*.json')):paths['negative_'+p.stem]=p
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());tr=next(x for x in reg['admitted_contracts'] if x['semantic_kind']=='typed-relation' and x['lifecycle_state']=='admitted-current')
 paths['TR_schema']=b.ROOT/tr['schema_path'];paths['TR_fixture']=(b.ROOT/tr['artifact_path']).parent/'fixtures/valid/record.json'
 for semantic in ['team-membership','person-reference','role-assignment','responsibility']:
  row=next(x for x in reg['admitted_contracts'] if x['semantic_kind']==semantic and x['lifecycle_state']=='admitted-current');paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=(b.ROOT/row['artifact_path']).parent/'fixtures/valid/record.json'
 kinds={x['relation_kind_ref']:x for x in kr['entries']}
 for id,row in kinds.items():paths[id]=b.ROOT/row['instance_path']
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'}
 artifact=docs['descriptor'];fixture=docs['fixture'];schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);checks=[]
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
 ck('two-artifact-renders-exact-projection',mod.render_artifact(artifact).encode()==mod.render_artifact(artifact).encode()==raws['artifact_projection']);ck('two-fixture-renders-exact-projection',mod.render_instance(artifact,fixture).encode()==mod.render_instance(artifact,fixture).encode()==raws['fixture_projection']);ck('renderers-preserve-inputs',before==[artifact,fixture])
 for semantic in ['team-membership','person-reference','role-assignment','responsibility']:ck(semantic+'-fixture-shape-valid',not list(b.c.Draft202012Validator(docs[semantic+'_schema']).iter_errors(docs[semantic+'_fixture'])))
 membership=docs['team-membership_fixture'];assignment=docs['role-assignment_fixture'];responsibility=docs['responsibility_fixture'];reference=docs['person-reference_fixture']
 joins={'listed_membership_literal_node_matches':membership['node_id'] in fixture['membership_refs'],'membership_literal_Team_matches':membership['team_ref']==fixture['node_id'],'membership_literal_Reference_matches':membership['person_reference_ref']==reference['node_id'],'Team_membership_Reference_literal_scopes_match':fixture['scope_ref']==membership['scope_ref']==reference['scope_ref'],'listed_role_assignment_literal_node_matches':assignment['node_id'] in fixture['role_assignment_refs'],'listed_assignment_is_PersonReference_assignee':assignment['assignee_kind']=='person-reference' and assignment['assignee_ref']==reference['node_id'],'listed_assignment_is_Team_assignee':assignment['assignee_kind']=='team' and assignment['assignee_ref']==fixture['node_id'],'listed_responsibility_literal_node_matches':responsibility['node_id'] in fixture['responsibility_refs'],'selected_responsibility_literal_scope_matches':responsibility['scope_ref']==fixture['scope_ref'],'actual_Team_Person_owner_currentness_or_role_assignment_verified':False}
 ck('literal-fixture-joins-retain-member-assignment-and-missing-responsibility-gaps',joins=={'listed_membership_literal_node_matches':True,'membership_literal_Team_matches':True,'membership_literal_Reference_matches':True,'Team_membership_Reference_literal_scopes_match':True,'listed_role_assignment_literal_node_matches':True,'listed_assignment_is_PersonReference_assignee':True,'listed_assignment_is_Team_assignee':False,'listed_responsibility_literal_node_matches':False,'selected_responsibility_literal_scope_matches':False,'actual_Team_Person_owner_currentness_or_role_assignment_verified':False})
 probes=[]
 def probe(id,change,expected):
  rec=copy.deepcopy(fixture);change(rec);es=list(validator.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected Team schema '+id+' '+str([x.message for x in es]))
  probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_collective_Person_owner_denotation_established':False,'actual_currentness_or_reference_resolution_enforced':False,'actual_runtime_execution':False,'whole_source_conformance_established':False})
 probe('proposed-empty-members-accepted',lambda r:r.update(lifecycle_state='proposed',membership_refs=[]),True)
 probe('active-unresolved-membership-token-accepted',lambda r:r.update(membership_refs=['absent:Membership']),True)
 probe('active-own-node-as-member-token-accepted',lambda r:r.update(membership_refs=[r['node_id']]),True)
 probe('superseded-without-successor-accepted',lambda r:r.update(lifecycle_state='superseded'),True)
 probe('self-successor-token-accepted',lambda r:r['successor_refs'].append(r['node_id']),True)
 probe('unresolved-owner-route-accepted',lambda r:r.update(owner_ref='absent:Owner',owner_route='absent:Route'),True)
 probe('arbitrary-nonblank-boundary-metadata-accepted',lambda r:r.update(identity_boundary='Other unreviewed narrative'),True)
 probe('empty-role-responsibility-and-claim-lists-accepted',lambda r:r.update(role_assignment_refs=[],responsibility_refs=[],authority_claim_refs=[]),True)
 probe('unresolved-assignment-responsibility-authority-tokens-accepted',lambda r:r.update(role_assignment_refs=['absent:Assignment'],responsibility_refs=['absent:Responsibility'],authority_claim_refs=['absent:Claim']),True)
 probe('retired-with-no-members-accepted',lambda r:r.update(lifecycle_state='retired',membership_refs=[]),True)
 probe('active-empty-members-rejected',lambda r:r.update(membership_refs=[]),False)
 probe('duplicate-member-tokens-rejected',lambda r:r.update(membership_refs=['same','same']),False)
 probe('extra-Person-field-rejected',lambda r:r.update(Person_entity='Human:hyp'),False)
 probe('extra-grant-field-rejected',lambda r:r.update(permission_granted=True),False)
 probe('effect-grant-rejected',lambda r:r.update(authority_effect='grant'),False)
 probe('missing-purpose-rejected',lambda r:r.pop('purpose'),False)
 probe('blank-purpose-rejected',lambda r:r.update(purpose=' '),False)
 probe('unknown-lifecycle-rejected',lambda r:r.update(lifecycle_state='running'),False)
 roles=[]
 for id,row in sorted(kinds.items()):
  payload=docs[id]['payload']
  if row['lifecycle_state']!='admitted-current' or row['instance_sha256']!=refs[id]['sha256'] or row['exact_endpoint_pair_count']!=len(payload['allowed_endpoint_pairs']) or row['required_qualifier_axes']!=payload['qualifier_contract']['required_axes']:raise ValueError('Current Kind catalog binding changed '+id)
  for direction,key,peer in [('source','source_kind','target_kind'),('target','target_kind','source_kind')]:
   peers=sorted({x[peer] for x in payload['allowed_endpoint_pairs'] if x[key]=='team'})
   if peers:roles.append({'relation_kind_ref':id,'direction':direction,'counterpart_kinds':peers,'required_qualifier_axes':payload['qualifier_contract']['required_axes']})
 expected_roles=[{'relation_kind_ref':'relation.assigned-to','direction':'source','counterpart_kinds':['responsibility','role'],'required_qualifier_axes':['assignment_kind','relation_record_ref']},{'relation_kind_ref':'relation.challenges','direction':'target','counterpart_kinds':['challenge-event'],'required_qualifier_axes':['challenge_contract_ref','challenge_mode','challenged_version_ref']},{'relation_kind_ref':'relation.member-of','direction':'target','counterpart_kinds':['person-reference'],'required_qualifier_axes':['membership_role']},{'relation_kind_ref':'relation.successor-of','direction':'source','counterpart_kinds':['team'],'required_qualifier_axes':['succession_effect']},{'relation_kind_ref':'relation.successor-of','direction':'target','counterpart_kinds':['team'],'required_qualifier_axes':['succession_effect']}]
 ck('all41-current-Kinds-exact-five-Team-roles',len(kinds)==41 and roles==expected_roles)
 kp=docs['relation.member-of']['payload'];ap=docs['relation.assigned-to']['payload']
 ck('member-of-exact-Reference-Team-qualifier-and-forbidden-inferences',len(kp['allowed_endpoint_pairs'])==24 and {'source_kind':'person-reference','target_kind':'team'} in kp['allowed_endpoint_pairs'] and kp['qualifier_contract']['required_axes']==['membership_role'] and kp['forbidden_inferences']==['contribution','assignment','authority','identity-equivalence'])
 ck('assignment-exact-Team-role-responsibility-directions-and-independent-effects',{'source_kind':'team','target_kind':'role'} in ap['allowed_endpoint_pairs'] and {'source_kind':'team','target_kind':'responsibility'} in ap['allowed_endpoint_pairs'] and ap['qualifier_contract']['required_axes']==['assignment_kind','relation_record_ref'] and ap['forbidden_inferences']==['team-membership','authority','permission','identity'])
 ck('current-TR-v3-schema-bound',tr['artifact_type_ref']=='cal.artifact-type.typed-relation/v3' and tr['schema_sha256']==refs['TR_schema']['sha256'])
 schema_pairs=relation_conditions(docs['TR_schema'],'relation.member-of');assignment_pairs=relation_conditions(docs['TR_schema'],'relation.assigned-to');pair_key=lambda x:(x['source_kind'],x['target_kind'])
 missing_pairs=sorted([x for x in kp['allowed_endpoint_pairs'] if x not in schema_pairs],key=pair_key);extra_pairs=sorted([x for x in schema_pairs if x not in kp['allowed_endpoint_pairs']],key=pair_key)
 ck('current-Kind24-versus-TR23-DecisionBundle-gap-retained',len(schema_pairs)==23 and missing_pairs==[{'source_kind':'decision','target_kind':'decision-bundle'}] and extra_pairs==[])
 ck('assigned-to-six-exact-TR-pairs',sorted(assignment_pairs,key=pair_key)==sorted(ap['allowed_endpoint_pairs'],key=pair_key) and len(assignment_pairs)==6)
 relation=copy.deepcopy(docs['TR_fixture']);relation['payload'].update(relation_kind_ref='relation.member-of',source={'kind':'person-reference','ref':membership['person_reference_ref'],'version_ref':'Reference@hyp'},target={'kind':'team','ref':fixture['node_id'],'version_ref':'Team@hyp'},qualifiers={'membership_role':'member'});tv=b.c.Draft202012Validator(docs['TR_schema']);relation_probes=[]
 def rp(id,change,expected):
  rec=copy.deepcopy(relation);change(rec);es=list(tv.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected Team relation shape '+id+' '+str([x.message for x in es]))
  relation_probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_collective_Person_owner_denotation_established':False,'actual_relation_created':False,'whole_source_conformance_established':False})
 rp('Reference-to-Team-member-of-no-independent-Membership-binding',lambda r:None,True)
 rp('membership-owner-label-not-RoleAssignment-or-grant',lambda r:r['payload']['qualifiers'].update(membership_role='owner'),True)
 rp('unresolved-Reference-and-Team-tokens-accepted',lambda r:r['payload']['source'].update(ref='absent:Reference') or r['payload']['target'].update(ref='absent:Team'),True)
 def assigned(r,kind='role',record='absent:Assignment'):
  r['payload'].update(relation_kind_ref='relation.assigned-to',source={'kind':'team','ref':fixture['node_id'],'version_ref':'Team@hyp'},target={'kind':kind,'ref':'absent:'+kind,'version_ref':kind+'@hyp'},qualifiers={'assignment_kind':kind,'relation_record_ref':record})
 rp('Team-to-Role-assigned-to-unresolved-record-accepted',assigned,True)
 rp('Team-to-Responsibility-assigned-to-unresolved-record-accepted',lambda r:assigned(r,'responsibility'),True)
 rp('Team-assignment-qualifier-can-name-Person-assignment-without-assignee-join',lambda r:assigned(r,'role',assignment['node_id']),True)
 rp('member-of-Person-source-rejected',lambda r:r['payload']['source'].update(kind='person'),False)
 rp('member-of-Membership-source-rejected',lambda r:r['payload']['source'].update(kind='team-membership'),False)
 rp('member-of-missing-role-rejected',lambda r:r['payload'].update(qualifiers={}),False)
 rp('member-of-extra-Membership-binding-rejected',lambda r:r['payload']['qualifiers'].update(membership_ref=membership['node_id']),False)
 rp('member-of-Reference-to-Project-cross-product-rejected',lambda r:r['payload']['target'].update(kind='project'),False)
 rp('Kind-DecisionBundle-pair-rejected-by-current-TR23',lambda r:r['payload'].update(source={'kind':'decision','ref':'Decision:hyp','version_ref':'Decision@hyp'},target={'kind':'decision-bundle','ref':'Bundle:hyp','version_ref':'Bundle@hyp'}),False)
 rp('assignment-reversed-Role-to-Team-rejected',lambda r:assigned(r) or r['payload'].update(source={'kind':'role','ref':'Role:hyp','version_ref':'Role@hyp'},target={'kind':'team','ref':fixture['node_id'],'version_ref':'Team@hyp'}),False)
 rp('assignment-missing-lifecycle-record-ref-rejected',lambda r:assigned(r) or r['payload']['qualifiers'].pop('relation_record_ref'),False)
 rp('assignment-missing-kind-rejected',lambda r:assigned(r) or r['payload']['qualifiers'].pop('assignment_kind'),False)
 rp('assignment-extra-grant-qualifier-rejected',lambda r:assigned(r) or r['payload']['qualifiers'].update(authority_granted=True),False)
 pair_observations=[]
 for pair in kp['allowed_endpoint_pairs']:
  rec=copy.deepcopy(relation);rec['payload']['source'].update(kind=pair['source_kind']);rec['payload']['target'].update(kind=pair['target_kind']);es=list(tv.iter_errors(rec));accepted=not es
  if accepted!=(pair in schema_pairs):raise ValueError('Actual schema differs from extracted exact pair condition')
  pair_observations.append({'pair':pair,'schema_accepted':accepted,'errors':[x.message for x in es],'model_record':rec,'actual_relation_created':False,'whole_catalog_alignment_established':False})
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();history=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_team_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=json.loads((b.BASE/'definitions/cal.definition.team-membership/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-Team-profile/v1-candidate','status':'PASS-for-hypothetical-Team-current-member-owner-and-stable-frame-with-current-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_history_frame_count':len(history),'rejected_history_frames':sum(x['expected_rejection'] for x in history),'finite_history_frames':history,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'actual_relation_schema_probes':relation_probes,'negative_fixture_checks':negative,'actual_join_observations':joins,'Team_roles_from_all_current_Kinds':roles,'TR_member_of_schema_pairs':schema_pairs,'TR_assignment_schema_pairs':assignment_pairs,'current_Kind_TR_pair_observations':pair_observations,'current_Kind_TR_schema_gap':{'current_Kind_pairs':24,'current_TR_schema_pairs':23,'missing_TR_pairs':missing_pairs,'extra_TR_pairs':extra_pairs,'alignment_reviewed':False},'source_mapping_gaps':{'actual_Team_Person_Reference_membership_owner_denotation_reviewed':False,'period_clock_endpoint_currentness_semantics_reviewed':False,'owner_qualification_attribution_and_authority_authenticated':False,'lifecycle_history_Team_frame_succession_policy_reviewed':False,'source_precedence_and_relation_mapping_reviewed':False,'whole_source_conformance_established':False},'new_Person_Team_memberships_or_relations_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Exact supplied hypothetical resolver/owner/current-member profiles and stable-boundary history frames, and current carrier/schema/fixture/rendered projection/41 Kind observations. Member assignment fixture is not a Team assignment; selected responsibility does not match Team token/scope. Kind24/TR23 gap retained. String shape and literal joins do not authenticate collective/Human/owner/currentness/basis/assignment/grants. No actual operation, history/liveness proof, relation/admission/world effect, full catalog closure or whole-definition acceptance.'}
 if write:b.put('team-profile-checks.json',report)
 elif not b.r.same_json(report,load('team-profile-checks.json')):raise ValueError('Fresh Team profile differs')
 return report
def main():
 report=verify('--write' in b.sys.argv);print(json.dumps({k:report[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

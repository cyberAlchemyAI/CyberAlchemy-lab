"""Role descriptions, explicit historical-kind mapping and independent assignment/authority profiles."""
import copy,json,types
from datetime import datetime
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def record(kind):return json.loads((b.ROOT/'authority/artifact-types'/kind/'v1/fixtures/valid/record.json').read_bytes())
def baseline():
 role=record('role');assignment=record('role-assignment')
 return {'record':role,'Role_entity':'Role:hyp1','carrier_entity':'Record:Role:hyp1','eligible_kind_mapping':{'relation.claims-authority-over':{'selected_current_kind':'relation.scopes-authority-over','selection_marker':'hyp:explicit-absorbed-kind-selection','mapping_reviewed':False}},'assignments':[{'record':assignment,'assignee_token':assignment['assignee_ref'],'assignee_kind':assignment['assignee_kind'],'assignee_entity':'Human:hyp1','resolution_marker':'hyp:assignee-resolution'}],'query_time':'2026-10-06T00:00:00Z','description_derived_grants':[],'independently_supported_grants':[],'source_owner_reviewed':False,'actual_Role_assignee_owner_and_grant_verified':False}
def catalog():
 reg=json.loads((b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json').read_bytes())
 return {r['relation_kind_ref']:json.loads((b.ROOT/r['instance_path']).read_bytes())['payload'] for r in reg['entries']}
def stamp(x):return datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')
def errors(p):
 es=[];r=p['record'];observations=[];now=None;kinds=catalog()
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected Role profile')
 schema=json.loads((b.ROOT/'authority/artifact-types/role/v1/schema.json').read_bytes());ck(not list(b.c.Draft202012Validator(schema).iter_errors(r)),'exact selected Role record shape')
 ck(p['Role_entity']!=p['carrier_entity'],'Role intension Entity distinct from its carrier')
 ck(r['node_id'] not in r['successor_refs'],'selected stronger policy excludes self successor')
 if r['lifecycle_state']=='superseded':ck(bool(r['successor_refs']),'selected stronger supersession needs successor')
 for literal in r['eligible_authority_relation_kinds']:
  mapping=p['eligible_kind_mapping'].get(literal)
  if mapping is None:es.append('unresolved eligible kind selection');continue
  current=mapping['selected_current_kind'];payload=kinds.get(current)
  ck(payload is not None and (literal==current or literal in payload['absorbed_relation_kinds']),'exact current or explicitly selected absorbed kind')
  ck(bool(mapping['selection_marker']) and mapping['mapping_reviewed'] is False,'hypothetical mapping selection never creates owner approval')
 try:now=stamp(p['query_time'])
 except (ValueError,TypeError):es.append('unresolved selected query calendar')
 for row in p['assignments']:
  a=row['record'];issues=[];within=current=None;start=end=None;end_known=a['period']['end'] is None
  if a['role_ref']!=r['node_id']:issues.append('different selected Role')
  if a['scope_ref']!=r['scope_ref']:issues.append('different selected scope')
  if row['assignee_token']!=a['assignee_ref'] or row['assignee_kind']!=a['assignee_kind']:issues.append('unresolved exact assignee token/kind')
  if not row['resolution_marker'] or not row['assignee_entity']:issues.append('missing hypothetical assignee denotation')
  if row['assignee_entity']==p['Role_entity']:issues.append('selected assignee/Role Entity collapsed')
  if {'source_kind':row['assignee_kind'],'target_kind':'role'} not in kinds['relation.assigned-to']['allowed_endpoint_pairs']:issues.append('unselected assignee kind')
  try:start=stamp(a['period']['start'])
  except (ValueError,TypeError):issues.append('unresolved start calendar')
  if a['period']['end'] is not None:
   try:end=stamp(a['period']['end']);end_known=True
   except (ValueError,TypeError):issues.append('unresolved nonnull end calendar')
  ordered=start is not None and (end is None or end>start)
  if start is not None and end is not None and not ordered:issues.append('nonordered selected period')
  if ordered and now is not None and end_known:within=start<=now and (end is None or now<end)
  if not issues and within is not None:current=a['assignment_state']=='active' and within
  es.extend(issues);observations.append({'assignment_token':a['node_id'],'issues':issues,'within_selected_half_open_period':within,'current_under_hypothesis':current,'assignee_entity':row['assignee_entity'],'actual_assignment_or_grant_verified':False})
 ck(not p['description_derived_grants'],'expected functions/eligible kinds alone do not generate grants')
 ck(p['source_owner_reviewed'] is False and p['actual_Role_assignee_owner_and_grant_verified'] is False,'candidate markers do not create source review or actual verification')
 return es,{'selected_assignment_rows':len(observations),'current_hypothetical_assignees':sum(x['current_under_hypothesis'] is True for x in observations),'rows':observations,'complete_actual_assignment_catalog_verified':False,'actual_role_grants_verified':False,'period_semantics':'selected hypothetical UTC effective period with half-open endpoint; unreviewed source correspondence'}
def controls():
 rows=[]
 def add(id,change,bad=False,current=1):
  p=baseline();change(p);es,detail=errors(p)
  if bool(es)!=bad or detail['current_hypothetical_assignees']!=current:raise ValueError('Unexpected Role profile '+id+' '+str((es,detail)))
  rows.append({'case_id':id,'profile':p,'errors':es,'assignment_check':detail,'expected_rejection':bad,'source_owner_reviewed':False,'actual_Role_assignee_or_grant_verified':False,'actual_runtime_execution':False})
 add('historical-eligible-kind-explicit-hypothetical-mapping-not-grant',lambda p:None)
 add('Role-valid-with-no-selected-assignment',lambda p:p.update(assignments=[]),current=0)
 add('independent-grant-can-coexist-with-description',lambda p:p.update(independently_supported_grants=['Grant:hyp-independent']))
 def extra(p,kind='person-reference'):
  row=copy.deepcopy(p['assignments'][0]);row['record'].update(node_id='Assignment:hyp2',assignee_kind=kind,assignee_ref='Assignee:hyp2');row.update(assignee_kind=kind,assignee_token='Assignee:hyp2',assignee_entity='Entity:hyp2');p['assignments'].append(row)
 add('same-Role-two-PersonReference-assignees',extra,current=2)
 add('same-Role-Team-assignee-supported',lambda p:extra(p,'team'),current=2)
 add('same-Role-AgentInstance-assignee-supported',lambda p:extra(p,'agent-instance'),current=2)
 add('inactive-assignment-label-does-not-invalidate-Role',lambda p:p['assignments'][0]['record'].update(assignment_state='inactive'),current=0)
 add('before-assignment-start-not-current-still-valid-Role',lambda p:p.update(query_time='2026-10-04T00:00:00Z'),current=0)
 add('after-selected-finite-end-not-current-still-valid-Role',lambda p:p['assignments'][0]['record']['period'].update(end='2026-10-05T12:00:00Z'),current=0)
 add('selected-half-open-exact-end-not-current',lambda p:p['assignments'][0]['record']['period'].update(end=p['query_time']),current=0)
 def current_label(p):p['record']['eligible_authority_relation_kinds']=['relation.scopes-authority-over'];p['eligible_kind_mapping']={'relation.scopes-authority-over':{'selected_current_kind':'relation.scopes-authority-over','selection_marker':'hyp:direct-current-kind','mapping_reviewed':False}}
 add('current-eligible-kind-label-also-not-grant',current_label)
 add('eligible-list-can-be-empty-no-actual-grant-follows',lambda p:p['record'].update(eligible_authority_relation_kinds=[]))
 add('Role-label-Team-does-not-merge-semantic-identity',lambda p:p['record'].update(name='Team'))
 add('no-selected-mapping-for-legacy-eligible-kind',lambda p:p.update(eligible_kind_mapping={}),True)
 add('unknown-eligible-kind',lambda p:p['record'].update(eligible_authority_relation_kinds=['absent:Kind']),True)
 add('wrong-current-kind-for-absorbed-label',lambda p:p['eligible_kind_mapping']['relation.claims-authority-over'].update(selected_current_kind='relation.assigned-to'),True)
 add('missing-explicit-kind-selection-marker',lambda p:p['eligible_kind_mapping']['relation.claims-authority-over'].update(selection_marker=''),True)
 add('kind-mapping-owner-approval-not-created',lambda p:p['eligible_kind_mapping']['relation.claims-authority-over'].update(mapping_reviewed=True),True)
 add('Role-collapsed-with-carrier',lambda p:p.update(carrier_entity=p['Role_entity']),True)
 add('selected-assignee-collapsed-with-Role',lambda p:p['assignments'][0].update(assignee_entity=p['Role_entity']),True,0)
 add('assignment-wrong-Role-reference',lambda p:p['assignments'][0]['record'].update(role_ref='other:Role'),True,0)
 add('assignment-wrong-selected-scope',lambda p:p['assignments'][0]['record'].update(scope_ref='other:Scope'),True,0)
 add('assignment-unresolved-assignee-token',lambda p:p['assignments'][0].update(assignee_token='other:Reference'),True,0)
 add('assignment-unresolved-assignee-kind',lambda p:p['assignments'][0].update(assignee_kind='team'),True,0)
 add('assignment-missing-denotation-marker',lambda p:p['assignments'][0].update(resolution_marker=''),True,0)
 add('invalid-calendar-start-not-false-currentness',lambda p:p['assignments'][0]['record']['period'].update(start='2026-99-99T00:00:00Z'),True,0)
 add('invalid-nonnull-end-not-open-ended',lambda p:p['assignments'][0]['record']['period'].update(end='2026-99-99T00:00:00Z'),True,0)
 add('invalid-query-calendar-not-world-falsehood',lambda p:p.update(query_time='2026-99-99T00:00:00Z'),True,0)
 add('empty-functions-selected-shape-fails',lambda p:p['record'].update(functions=[]),True)
 add('empty-exclusions-selected-shape-fails',lambda p:p['record'].update(exclusions=[]),True)
 add('description-alone-generates-grant',lambda p:p.update(description_derived_grants=['Grant:hyp']),True)
 add('self-successor-rejected-by-selected-stronger-policy',lambda p:p['record']['successor_refs'].append(p['record']['node_id']),True)
 add('superseded-without-successor-selected-policy',lambda p:p['record'].update(lifecycle_state='superseded'),True)
 add('source-owner-approval-not-created',lambda p:p.update(source_owner_reviewed=True),True)
 add('actual-Role-assignee-grant-verification-not-created',lambda p:p.update(actual_Role_assignee_owner_and_grant_verified=True),True)
 for x in rows:
  if x['case_id'] in ['invalid-calendar-start-not-false-currentness','invalid-nonnull-end-not-open-ended','invalid-query-calendar-not-world-falsehood']:
   if any(z['within_selected_half_open_period'] is not None or z['current_under_hypothesis'] is not None for z in x['assignment_check']['rows']):raise ValueError('Unresolved interval became known or open')
 return rows
def frames():
 rows=[]
 def base():
  r=record('role');return {'operation':'change-holders','before':r,'after':copy.deepcopy(r),'Role_entity_before':'Role:hyp1','Role_entity_after':'Role:hyp1','holders_before':['Human:hyp1'],'holders_after':['Human:hyp2'],'prior_assignment_history_retained':True,'assignment_decision_marker':'Decision:hyp-assignment','separate_role_revision_marker':None,'authority_before':['Grant:hyp-independent'],'authority_after':['Grant:hyp-independent'],'separate_authority_decision_marker':None,'successor':None}
 def errors(f):
  es=[];a=f['before'];z=f['after']
  if f['operation'] not in ['change-holders','edit-label','revise-description','retire','supersede']:es.append('unselected operation')
  if a['node_id']!=z['node_id'] or f['Role_entity_before']!=f['Role_entity_after']:es.append('selected continuing Role identity preserved')
  description_fields=['purpose','scope_ref','functions','responsibility_refs','eligible_authority_relation_kinds','authority_boundary','exclusions','owner_ref','owner_route','challenge_route']
  if any(a[k]!=z[k] for k in description_fields) and f['separate_role_revision_marker'] is None:es.append('holder change alone does not revise Role intension')
  if not f['prior_assignment_history_retained']:es.append('selected assignment history retained')
  if f['operation']=='change-holders' and not f['assignment_decision_marker']:es.append('separate assignment decision marker')
  if f['authority_before']!=f['authority_after'] and f['separate_authority_decision_marker'] is None:es.append('independent authority change needs separate marker')
  if f['operation']=='edit-label' and f['holders_before']!=f['holders_after']:es.append('label-only change preserves holders')
  if f['operation']=='retire' and z['lifecycle_state']!='retired':es.append('retirement exact state')
  if f['operation']=='supersede':
   s=f['successor']
   if z['lifecycle_state']!='superseded' or s is None or s['node_id']==a['node_id'] or s['node_id'] not in z['successor_refs']:es.append('fresh explicit successor required')
  return es
 def add(id,change,bad=False):
  f=base();change(f);es=errors(f)
  if bool(es)!=bad:raise ValueError('Unexpected Role frame '+id+' '+str(es))
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'source_owner_reviewed':False,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('different-holders-same-Role-intension-and-identity',lambda f:None)
 add('fresh-assignment-records-same-holders-also-valid',lambda f:f.update(holders_after=f['holders_before']))
 add('independent-authority-change-can-coexist',lambda f:f.update(authority_after=['Grant:hyp2'],separate_authority_decision_marker='Decision:hyp-authority'))
 add('separate-Role-description-revision-can-coexist',lambda f:f.update(operation='revise-description',separate_role_revision_marker='Decision:hyp-revision') or f['after'].update(functions=['New independent expectation']))
 add('retirement-does-not-automatically-revoke-grants',lambda f:f.update(operation='retire') or f['after'].update(lifecycle_state='retired'))
 add('label-edit-preserves-role-and-holders',lambda f:f.update(operation='edit-label',holders_after=f['holders_before']) or f['after'].update(name='Other label'))
 def successor(f):f.update(operation='supersede',successor={**f['before'],'node_id':'Role:hyp-successor'});f['after'].update(lifecycle_state='superseded',successor_refs=['Role:hyp-successor'])
 add('fresh-explicit-Role-successor',successor)
 for k in ['purpose','scope_ref','functions','eligible_authority_relation_kinds','authority_boundary','exclusions']:
  add('holder-change-alone-mutates-'+k,lambda f,k=k:f['after'].__setitem__(k,['Other'] if isinstance(f['after'][k],list) else 'Other'),True)
 add('holder-change-replaces-Role-entity',lambda f:f.update(Role_entity_after='Role:hyp2'),True)
 add('assignment-history-discarded',lambda f:f.update(prior_assignment_history_retained=False),True)
 add('assignment-decision-marker-missing',lambda f:f.update(assignment_decision_marker=''),True)
 add('Role-or-holder-metadata-automatically-grants',lambda f:f.update(authority_after=['Grant:hyp2']),True)
 add('Role-retirement-automatically-revokes',lambda f:f.update(operation='retire',authority_after=[]) or f['after'].update(lifecycle_state='retired'),True)
 add('label-change-alone-alters-holders',lambda f:f.update(operation='edit-label'),True)
 add('superseded-without-successor',lambda f:f.update(operation='supersede') or f['after'].update(lifecycle_state='superseded'),True)
 add('self-successor',lambda f:successor(f) or f['successor'].update(node_id=f['before']['node_id']),True)
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
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();root=b.ROOT/'authority/artifact-types/role/v1'
 paths={'descriptor':root/'artifact.json','schema':root/'schema.json','fixture':root/'fixtures/valid/record.json','artifact_projection':root/'ARTIFACT.md','fixture_projection':root/'fixtures/valid/RECORD.md','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','generator':b.ROOT/'tooling/generators/artifact_surface.py','shared_validator':b.ROOT/'tooling/validators/artifact_surface.py','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json','refinement':b.ROOT/'authority/artifact-types/candidates/0004-remaining-26-materialization/refinements/type.role.json'}
 for p in sorted((root/'fixtures/invalid').glob('*.json')):paths['negative_'+p.stem]=p
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());tr=next(x for x in reg['admitted_contracts'] if x['semantic_kind']=='typed-relation' and x['lifecycle_state']=='admitted-current')
 paths['TR_schema']=b.ROOT/tr['schema_path'];paths['TR_fixture']=(b.ROOT/tr['artifact_path']).parent/'fixtures/valid/record.json'
 for semantic in ['person-reference','role-assignment','responsibility','team']:
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
 ck('Role-refinement-description-lifecycle-no-admission',docs['refinement']['target_id']=='type.role' and docs['refinement']['admission_effect']=='none')
 for semantic in ['person-reference','role-assignment','responsibility','team']:ck(semantic+'-fixture-shape-valid',not list(b.c.Draft202012Validator(docs[semantic+'_schema']).iter_errors(docs[semantic+'_fixture'])))
 assignment=docs['role-assignment_fixture'];reference=docs['person-reference_fixture'];responsibility=docs['responsibility_fixture'];team=docs['team_fixture']
 joins={'assignment_Role_literal_matches':assignment['role_ref']==fixture['node_id'],'assignment_PersonReference_literal_matches':assignment['assignee_kind']=='person-reference' and assignment['assignee_ref']==reference['node_id'],'Role_assignment_Reference_literal_scopes_match':fixture['scope_ref']==assignment['scope_ref']==reference['scope_ref'],'Team_lists_the_Person_assignment':assignment['node_id'] in team['role_assignment_refs'],'assignment_is_Team_assignee':assignment['assignee_kind']=='team' and assignment['assignee_ref']==team['node_id'],'Role_listed_responsibility_literal_matches':responsibility['node_id'] in fixture['responsibility_refs'],'Role_selected_responsibility_literal_scope_matches':responsibility['scope_ref']==fixture['scope_ref'],'actual_Role_Person_assignment_or_grant_verified':False}
 ck('literal-Role-Person-assignment-and-responsibility-gaps-retained',joins=={'assignment_Role_literal_matches':True,'assignment_PersonReference_literal_matches':True,'Role_assignment_Reference_literal_scopes_match':True,'Team_lists_the_Person_assignment':True,'assignment_is_Team_assignee':False,'Role_listed_responsibility_literal_matches':False,'Role_selected_responsibility_literal_scope_matches':False,'actual_Role_Person_assignment_or_grant_verified':False})
 probes=[]
 def probe(id,change,expected):
  rec=copy.deepcopy(fixture);change(rec);es=list(validator.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected Role schema '+id+' '+str([x.message for x in es]))
  probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_Role_or_eligible_authority_verified':False,'actual_current_assignment_or_grant_enforced':False,'actual_runtime_execution':False,'whole_source_conformance_established':False})
 probe('Role-label-Team-shape-accepted',lambda r:r.update(name='Team'),True)
 probe('active-Role-empty-responsibility-and-eligibility-lists-accepted',lambda r:r.update(responsibility_refs=[],eligible_authority_relation_kinds=[]),True)
 probe('legacy-eligible-kind-label-accepted',lambda r:None,True)
 probe('current-absorbing-kind-label-accepted',lambda r:r.update(eligible_authority_relation_kinds=['relation.scopes-authority-over']),True)
 probe('unknown-eligible-kind-token-accepted',lambda r:r.update(eligible_authority_relation_kinds=['absent:Kind']),True)
 probe('superseded-without-successor-accepted',lambda r:r.update(lifecycle_state='superseded'),True)
 probe('self-successor-token-accepted',lambda r:r['successor_refs'].append(r['node_id']),True)
 probe('unresolved-owner-and-responsibility-refs-accepted',lambda r:r.update(owner_ref='absent:Owner',owner_route='absent:Route',responsibility_refs=['absent:Responsibility']),True)
 probe('arbitrary-nonblank-authority-boundary-accepted',lambda r:r.update(authority_boundary='Unreviewed narrative'),True)
 probe('node-equals-PersonReference-token-accepted',lambda r:r.update(node_id=reference['node_id']),True)
 probe('empty-functions-rejected',lambda r:r.update(functions=[]),False)
 probe('empty-exclusions-rejected',lambda r:r.update(exclusions=[]),False)
 probe('blank-purpose-rejected',lambda r:r.update(purpose=' '),False)
 probe('extra-current-holder-field-rejected',lambda r:r.update(current_holder_ref=reference['node_id']),False)
 probe('duplicate-eligible-kind-labels-rejected',lambda r:r.update(eligible_authority_relation_kinds=['same','same']),False)
 probe('effect-grant-rejected',lambda r:r.update(authority_effect='grant'),False)
 probe('unknown-lifecycle-rejected',lambda r:r.update(lifecycle_state='running'),False)
 probe('missing-authority-boundary-rejected',lambda r:r.pop('authority_boundary'),False)
 roles=[]
 for id,row in sorted(kinds.items()):
  payload=docs[id]['payload']
  if row['lifecycle_state']!='admitted-current' or row['instance_sha256']!=refs[id]['sha256'] or row['exact_endpoint_pair_count']!=len(payload['allowed_endpoint_pairs']) or row['required_qualifier_axes']!=payload['qualifier_contract']['required_axes']:raise ValueError('Current Kind binding drift '+id)
  for direction,key,peer in [('source','source_kind','target_kind'),('target','target_kind','source_kind')]:
   peers=sorted({x[peer] for x in payload['allowed_endpoint_pairs'] if x[key]=='role'})
   if peers:roles.append({'relation_kind_ref':id,'direction':direction,'counterpart_kinds':peers,'required_qualifier_axes':payload['qualifier_contract']['required_axes']})
 expected=[{'relation_kind_ref':'relation.assigned-to','direction':'target','counterpart_kinds':['agent-instance','person-reference','team'],'required_qualifier_axes':['assignment_kind','relation_record_ref']},{'relation_kind_ref':'relation.challenges','direction':'target','counterpart_kinds':['challenge-event'],'required_qualifier_axes':['challenge_contract_ref','challenge_mode','challenged_version_ref']},{'relation_kind_ref':'relation.member-of','direction':'target','counterpart_kinds':['responsibility'],'required_qualifier_axes':['membership_role']},{'relation_kind_ref':'relation.successor-of','direction':'source','counterpart_kinds':['role'],'required_qualifier_axes':['succession_effect']},{'relation_kind_ref':'relation.successor-of','direction':'target','counterpart_kinds':['role'],'required_qualifier_axes':['succession_effect']}]
 ck('all41-current-Kinds-exact-five-Role-roles',len(kinds)==41 and roles==expected)
 absorption=[]
 for literal in fixture['eligible_authority_relation_kinds']:
  absorption.append({'literal_eligible_kind':literal,'is_current_kind_ref':literal in kinds,'current_absorbing_kind_refs':sorted(id for id in kinds if literal in docs[id]['payload']['absorbed_relation_kinds']),'mapping_reviewed':False,'actual_eligibility_or_grant_verified':False})
 ck('legacy-eligible-kind-not-current-explicitly-absorbed-by-authority-scope',absorption==[{'literal_eligible_kind':'relation.claims-authority-over','is_current_kind_ref':False,'current_absorbing_kind_refs':['relation.scopes-authority-over'],'mapping_reviewed':False,'actual_eligibility_or_grant_verified':False}])
 authority=docs['relation.scopes-authority-over']['payload'];ck('current-authority-scope-kind-does-not-use-Role-endpoint-or-grant',not any('role' in [p['source_kind'],p['target_kind']] for p in authority['allowed_endpoint_pairs']) and authority['forbidden_inferences']==['permission-grant','claim-authentication','effect-execution'])
 ck('current-TR-v3-schema-bound',tr['artifact_type_ref']=='cal.artifact-type.typed-relation/v3' and tr['schema_sha256']==refs['TR_schema']['sha256'])
 ap=docs['relation.assigned-to']['payload'];mp=docs['relation.member-of']['payload'];assignment_pairs=relation_conditions(docs['TR_schema'],'relation.assigned-to');member_pairs=relation_conditions(docs['TR_schema'],'relation.member-of');authority_pairs=relation_conditions(docs['TR_schema'],'relation.scopes-authority-over');key=lambda x:(x['source_kind'],x['target_kind'])
 ck('assigned-to-six-exact-Kind-TR-pairs',len(assignment_pairs)==6 and sorted(assignment_pairs,key=key)==sorted(ap['allowed_endpoint_pairs'],key=key))
 ck('member-of-Responsibility-to-Role-pair-current',{'source_kind':'responsibility','target_kind':'role'} in mp['allowed_endpoint_pairs'] and {'source_kind':'responsibility','target_kind':'role'} in member_pairs and not any(p['target_kind']=='role' and p['source_kind']=='person-reference' for p in mp['allowed_endpoint_pairs']))
 ck('authority-scope-three-exact-Kind-TR-pairs',len(authority_pairs)==3 and sorted(authority_pairs,key=key)==sorted(authority['allowed_endpoint_pairs'],key=key))
 relation=copy.deepcopy(docs['TR_fixture']);relation['payload'].update(relation_kind_ref='relation.assigned-to',source={'kind':'person-reference','ref':assignment['assignee_ref'],'version_ref':'Reference@hyp'},target={'kind':'role','ref':fixture['node_id'],'version_ref':'Role@hyp'},qualifiers={'assignment_kind':'role','relation_record_ref':assignment['node_id']});tv=b.c.Draft202012Validator(docs['TR_schema']);relation_probes=[]
 def rp(id,change,expected):
  rec=copy.deepcopy(relation);change(rec);es=list(tv.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected Role relation schema '+id+' '+str([x.message for x in es]))
  relation_probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_assignment_eligibility_or_grant_verified':False,'actual_relation_created':False,'whole_source_conformance_established':False})
 rp('Reference-to-Role-actual-literal-links-shape-only',lambda r:None,True)
 rp('unresolved-assignment-record-token-accepted',lambda r:r['payload']['qualifiers'].update(relation_record_ref='absent:Assignment'),True)
 rp('Team-to-Role-with-Person-assignment-token-no-assignee-join',lambda r:r['payload']['source'].update(kind='team',ref=team['node_id']),True)
 rp('AgentInstance-to-Role-shape-valid',lambda r:r['payload']['source'].update(kind='agent-instance',ref='Agent:hyp'),True)
 rp('unresolved-Role-token-accepted',lambda r:r['payload']['target'].update(ref='absent:Role'),True)
 rp('arbitrary-assignment-kind-label-accepted-without-record-conformance',lambda r:r['payload']['qualifiers'].update(assignment_kind='other-unreviewed-label'),True)
 def member(r):r['payload'].update(relation_kind_ref='relation.member-of',source={'kind':'responsibility','ref':responsibility['node_id'],'version_ref':'Responsibility@hyp'},target={'kind':'role','ref':fixture['node_id'],'version_ref':'Role@hyp'},qualifiers={'membership_role':'expected-responsibility'})
 rp('Responsibility-to-Role-member-of-shape-not-TeamMembership',member,True)
 def scope(r):r['payload'].update(relation_kind_ref='relation.scopes-authority-over',source={'kind':'authority-claim','ref':'Claim:hyp','version_ref':'Claim@hyp'},target={'kind':'role-assignment','ref':assignment['node_id'],'version_ref':'Assignment@hyp'},qualifiers={'authority_role':'recommendation','scope_ref':fixture['scope_ref']})
 rp('current-authority-Claim-to-RoleAssignment-scope-shape-not-grant',scope,True)
 rp('assignment-missing-record-qualifier-rejected',lambda r:r['payload']['qualifiers'].pop('relation_record_ref'),False)
 rp('assignment-extra-grant-qualifier-rejected',lambda r:r['payload']['qualifiers'].update(permission_granted=True),False)
 rp('assignment-reversed-Role-to-Reference-rejected',lambda r:r['payload'].update(source={'kind':'role','ref':fixture['node_id'],'version_ref':'Role@hyp'},target={'kind':'person-reference','ref':reference['node_id'],'version_ref':'Reference@hyp'}),False)
 rp('member-of-Reference-to-Role-not-pair',lambda r:member(r) or r['payload']['source'].update(kind='person-reference'),False)
 rp('legacy-eligible-kind-not-direct-current-TR-kind',lambda r:scope(r) or r['payload'].update(relation_kind_ref='relation.claims-authority-over'),False)
 rp('authority-scope-Role-source-not-pair',lambda r:scope(r) or r['payload']['source'].update(kind='role',ref=fixture['node_id']),False)
 rp('authority-scope-Role-target-not-pair',lambda r:scope(r) or r['payload']['target'].update(kind='role',ref=fixture['node_id']),False)
 rp('authority-scope-missing-role-qualifier-rejected',lambda r:scope(r) or r['payload']['qualifiers'].pop('authority_role'),False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();history=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_role_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=json.loads((b.BASE/'definitions/cal.definition.team/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-Role-profile/v1-candidate','status':'PASS-for-explicit-Role-description-independent-assignment-and-authority-profiles-with-current-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_history_frame_count':len(history),'rejected_history_frames':sum(x['expected_rejection'] for x in history),'finite_history_frames':history,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'actual_relation_schema_probes':relation_probes,'negative_fixture_checks':negative,'actual_join_observations':joins,'Role_roles_from_all_current_Kinds':roles,'eligible_kind_currentness_observations':absorption,'TR_assignment_schema_pairs':assignment_pairs,'TR_authority_scope_schema_pairs':authority_pairs,'source_mapping_gaps':{'actual_Role_intension_entity_and_record_denotation_reviewed':False,'expected_responsibility_and_eligible_authority_kind_mapping_reviewed':False,'Role_assignee_principal_reference_currentness_and_grant_maps_authenticated':False,'lifecycle_history_succession_and_independence_policy_reviewed':False,'source_precedence_and_relation_mapping_reviewed':False,'whole_source_conformance_established':False},'new_Roles_assignments_or_relations_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Supplied hypothetical reusable Role/explicit absorbed-kind mapping/current assignment/independent authority profiles and finite history frames, with actual current carrier/schema/rendered fixture/41 Kind observations. Historical eligible kind is absorbed, not directly current; current authority scope has no Role endpoint and grants no permission. Literal Role/PersonReference/assignment links do not authenticate entities, currentness or grants. No approved mapping, actual operation, relation/admission/world effect, global catalog closure or whole-definition acceptance.'}
 if write:b.put('role-profile-checks.json',report)
 elif not b.r.same_json(report,load('role-profile-checks.json')):raise ValueError('Fresh Role profile differs')
 return report
def main():
 report=verify('--write' in b.sys.argv);print(json.dumps({k:report[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()


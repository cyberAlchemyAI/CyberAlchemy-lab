"""Selected temporal/epoch/history hypotheses and exact current carriers; no actual admission or effect."""
import copy,json,types
from datetime import datetime
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def record():return json.loads((b.ROOT/'authority/artifact-types/role-assignment/v1/fixtures/valid/record.json').read_bytes())
def baseline():
 r=record();return {'record':r,'assignment_entity':'Assignment:hyp1','carrier_entity':'Record:hyp1','assignee_token':r['assignee_ref'],'assignee_kind':r['assignee_kind'],'assignee_entity':'Human:hyp1','Role_token':r['role_ref'],'Role_entity':'Role:hyp1','scope_token':r['scope_ref'],'epoch_token':'Epoch:hyp1','query_epoch':'Epoch:hyp1','selection_markers':{'assignee':'hyp:Reference-to-Human','Role':'hyp:Role-denotation','owner':'hyp:owner-qualification','basis':'hyp:basis-decision','epoch':'hyp:lifecycle-epoch'},'interval_policy':'effective-period','query_time':'2026-10-06T00:00:00Z','implicit_memberships':[],'assignment_derived_grants':[],'independent_grants':[],'source_owner_reviewed':False,'actual_assignment_owner_epoch_and_grant_verified':False}
def stamp(x):return datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')
def errors(p):
 es=[];r=p['record'];start=end=now=None;end_known=r['period']['end'] is None
 def ck(ok,msg):
  if not ok:es.append(msg)
 schema=json.loads((b.ROOT/'authority/artifact-types/role-assignment/v1/schema.json').read_bytes());ck(set(p)==set(baseline()),'closed selected profile');ck(not list(b.c.Draft202012Validator(schema).iter_errors(r)),'exact selected carrier shape')
 ck(p['assignment_entity']!=p['carrier_entity'],'selected Assignment Entity differs from record');ck(p['assignee_entity']!=p['Role_entity'],'selected assignee and Role denotations distinct')
 ck(p['assignee_token']==r['assignee_ref'] and p['assignee_kind']==r['assignee_kind'],'exact assignee token/kind');ck(p['Role_token']==r['role_ref'],'exact Role token');ck(p['scope_token']==r['scope_ref'],'exact scope token')
 ck(all(p['selection_markers'].get(n) for n in ['assignee','Role','owner','basis','epoch']) and bool(p['epoch_token']),'hypothetical endpoint owner basis and epoch selections required')
 ck(p['interval_policy'] in ['finite-ended','effective-period'],'selected interval interpretation')
 if p['interval_policy']=='finite-ended':ck(r['period']['end'] is not None,'finite-ended hypothesis requires explicit end; active carrier requires null')
 try:start=stamp(r['period']['start'])
 except (ValueError,TypeError):es.append('unresolved start calendar')
 if r['period']['end'] is not None:
  try:end=stamp(r['period']['end']);end_known=True
  except (ValueError,TypeError):es.append('unresolved nonnull end calendar')
 try:now=stamp(p['query_time'])
 except (ValueError,TypeError):es.append('unresolved query calendar')
 ordered=start is not None and (end is None or end>start)
 if start is not None and end is not None:ck(ordered,'strictly ordered selected period')
 within=start<=now and (end is None or now<end) if start is not None and now is not None and end_known and ordered else None
 current=(r['assignment_state']=='active' and within and p['epoch_token']==p['query_epoch']) if not es and within is not None else None
 ck(not p['implicit_memberships'],'Assignment alone does not create Membership');ck(not p['assignment_derived_grants'],'Assignment/claim labels alone do not generate grant')
 ck(p['source_owner_reviewed'] is False and p['actual_assignment_owner_epoch_and_grant_verified'] is False,'no source review or actual authentication created')
 for grant in p['independent_grants']:
  ck(set(grant)=={'claim_token','assignee_entity','scope_token','epoch_token','action_token','support_marker','admission_selection_marker','actual_verified'} and grant['claim_token'] in r['authority_claim_refs'] and grant['assignee_entity']==p['assignee_entity'] and grant['scope_token']==p['scope_token'] and grant['epoch_token']==p['epoch_token'] and bool(grant['action_token']) and bool(grant['support_marker']) and bool(grant['admission_selection_marker']) and grant['actual_verified'] is False,'separate exact hypothetical supported/admitted-claim grant selection')
 if es:current=None
 return es,{'within_selected_half_open_period':within,'current_under_hypothesis':current,'selected_epoch_matches':p['epoch_token']==p['query_epoch'],'hypothetical_independent_grants':len(p['independent_grants']),'actual_currentness_or_grant_verified':False,'temporal_source_correspondence_reviewed':False}
def controls():
 rows=[]
 def add(id,change,bad=False,current=True):
  p=baseline();change(p);es,detail=errors(p)
  if bool(es)!=bad or detail['current_under_hypothesis']!=(None if bad else current):raise ValueError('Unexpected assignment profile '+id+' '+str((es,detail)))
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'temporal_observation':detail,'source_owner_reviewed':False,'actual_runtime_execution':False})
 add('effective-open-period-explicit-hypothetical-epoch',lambda p:None)
 add('Team-assignee-selected',lambda p:p['record'].update(assignee_kind='team',assignee_ref='Team:hyp') or p.update(assignee_kind='team',assignee_token='Team:hyp',assignee_entity='TeamEntity:hyp'))
 add('active-label-before-start-not-current',lambda p:p.update(query_time='2026-10-04T00:00:00Z'),current=False)
 add('exact-start-is-included-under-hypothesis',lambda p:p.update(query_time=p['record']['period']['start']))
 add('different-query-epoch-not-current',lambda p:p.update(query_epoch='Epoch:hyp2'),current=False)
 for state in ['proposed','suspended','ended','revoked']:add(state+'-label-not-active',lambda p,state=state:p['record'].update(assignment_state=state),current=False)
 def finite(p):p['record'].update(assignment_state='ended');p['record']['period'].update(end=p['query_time']);p.update(interval_policy='finite-ended')
 add('finite-ended-ended-record-exact-end-excluded',finite,current=False)
 def grant(p):p['independent_grants']=[{'claim_token':p['record']['authority_claim_refs'][0],'assignee_entity':p['assignee_entity'],'scope_token':p['scope_token'],'epoch_token':p['epoch_token'],'action_token':'Action:hyp','support_marker':'hyp:independent-support','admission_selection_marker':'hyp:separate-claim-selection','actual_verified':False}]
 add('separate-exact-supported-grant-hypothesis-permitted',grant)
 add('empty-claim-list-does-not-invalidate-assignment',lambda p:p['record'].update(authority_claim_refs=[]))
 add('active-open-period-fails-finite-ended-hypothesis',lambda p:p.update(interval_policy='finite-ended'),True)
 add('active-finite-end-fails-current-carrier',lambda p:p['record']['period'].update(end='2026-10-07T00:00:00Z'),True)
 add('AgentInstance-generic-kind-not-this-carrier',lambda p:p['record'].update(assignee_kind='agent-instance') or p.update(assignee_kind='agent-instance'),True)
 for k in ['assignee_token','Role_token','scope_token']:add('unresolved-exact-'+k,lambda p,k=k:p.update({k:'other:token'}),True)
 for k in ['assignee','Role','owner','basis','epoch']:add('missing-hypothetical-'+k+'-selection',lambda p,k=k:p['selection_markers'].update({k:''}),True)
 add('Assignment-collapsed-with-carrier',lambda p:p.update(carrier_entity=p['assignment_entity']),True)
 add('selected-assignee-collapsed-with-Role',lambda p:p.update(assignee_entity=p['Role_entity']),True)
 add('empty-epoch-not-inferred-from-start',lambda p:p.update(epoch_token=''),True)
 for key in ['start','end']:add('invalid-'+key+'-calendar-unknown',lambda p,key=key:p['record']['period'].update({key:'2026-99-99T00:00:00Z'}),True)
 add('invalid-query-calendar-unknown',lambda p:p.update(query_time='2026-99-99T00:00:00Z'),True)
 add('reversed-finite-period',lambda p:finite(p) or p['record']['period'].update(end='2026-10-04T00:00:00Z'),True)
 add('unselected-period-policy',lambda p:p.update(interval_policy='unknown'),True)
 add('implicit-Team-membership-rejected',lambda p:p.update(implicit_memberships=['Membership:hyp']),True)
 add('claim-label-implies-grant-rejected',lambda p:p.update(assignment_derived_grants=['Grant:hyp']),True)
 add('independent-grant-missing-support',lambda p:grant(p) or p['independent_grants'][0].update(support_marker=''),True)
 add('independent-grant-wrong-epoch',lambda p:grant(p) or p['independent_grants'][0].update(epoch_token='Epoch:hyp2'),True)
 add('source-owner-review-not-created',lambda p:p.update(source_owner_reviewed=True),True)
 add('actual-authentication-not-created',lambda p:p.update(actual_assignment_owner_epoch_and_grant_verified=True),True)
 return rows

def frames():
 rows=[];schema=json.loads((b.ROOT/'authority/artifact-types/role-assignment/v1/schema.json').read_bytes());validator=b.c.Draft202012Validator(schema)
 def baseline_frame():
  a=record();z=copy.deepcopy(a);z.update(assignment_state='ended');z['period'].update(end='2026-10-06T00:00:00Z');return {'operation':'end','before':a,'after':z,'epoch_before':'Epoch:hyp1','epoch_after':'Epoch:hyp1','entity_before':'Assignment:hyp1','entity_after':'Assignment:hyp1','prior_history_retained':True,'decision_marker':'hyp:assignment-decision','successor':None,'Role_before':'Role:hyp1','Role_after':'Role:hyp1','membership_before':['Membership:hyp-independent'],'membership_after':['Membership:hyp-independent'],'grant_before':['Grant:hyp-independent'],'grant_after':['Grant:hyp-independent'],'separate_membership_decision_marker':None,'separate_grant_decision_marker':None}
 def errors(f):
  es=[];a=f['before'];z=f['after'];op=f['operation']
  def ck(ok,msg):
   if not ok:es.append(msg)
  ck(op in ['end','suspend','revoke','correct-successor','epoch-successor'],'selected finite operation');ck(not list(validator.iter_errors(a)) and not list(validator.iter_errors(z)),'exact carrier shapes');ck(bool(f['decision_marker']) and f['prior_history_retained'],'separate selected decision/history')
  ck(a['node_id']==z['node_id'] and f['entity_before']==f['entity_after'],'predecessor assignment identity preserved')
  ck(f['Role_before']==f['Role_after'],'assignment operation alone does not replace Role')
  ck(all(a[k]==z[k] for k in ['assignee_kind','assignee_ref','role_ref','scope_ref','owner_ref','assignment_basis_ref']),'continuing predecessor endpoints/basis/scope fixed')
  ck(f['epoch_before']==f['epoch_after'],'predecessor epoch retained')
  if op=='end':ck(z['assignment_state']=='ended' and z['period']['end'] is not None,'selected ending closes interval')
  if op=='suspend':ck(z['assignment_state']=='suspended','selected suspension state')
  if op=='revoke':ck(z['assignment_state']=='revoked','selected revocation state')
  if op in ['correct-successor','epoch-successor']:
   s=f['successor'];ck(s is not None and s['record']['node_id']!=a['node_id'] and s['entity']!=f['entity_before'] and s['record']['node_id'] in z['successor_refs'],'fresh explicit successor/history edge')
   if s is not None:
    ck(not list(validator.iter_errors(s['record'])),'successor selected shape');ck(op!='epoch-successor' or s['epoch']!=f['epoch_before'],'selected new epoch')
  ck(f['membership_before']==f['membership_after'] or bool(f['separate_membership_decision_marker']),'independent membership change needs separate marker');ck(f['grant_before']==f['grant_after'] or bool(f['separate_grant_decision_marker']),'assignment end/revoke alone does not change independent grants')
  return es
 def add(id,change,bad=False):
  f=baseline_frame();change(f);es=errors(f)
  if bool(es)!=bad:raise ValueError('Unexpected assignment frame '+id+' '+str(es))
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('ending-preserves-Role-independent-membership-and-grant',lambda f:None)
 add('suspension-preserves-independent-grants',lambda f:f['after'].update(assignment_state='suspended')) if False else None
 add('suspension-preserves-independent-grants',lambda f:f.update(operation='suspend') or f['after'].update(assignment_state='suspended'))
 add('revocation-preserves-independently-supported-grant',lambda f:f.update(operation='revoke') or f['after'].update(assignment_state='revoked'))
 add('separate-membership-change-can-coexist',lambda f:f.update(membership_after=[],separate_membership_decision_marker='hyp:membership-decision'))
 add('separate-grant-change-can-coexist',lambda f:f.update(grant_after=[],separate_grant_decision_marker='hyp:grant-decision'))
 def successor(f,epoch=False):
  s=record();s.update(node_id='Assignment:hyp-successor');f.update(operation='epoch-successor' if epoch else 'correct-successor',successor={'record':s,'entity':'Assignment:hyp2','epoch':'Epoch:hyp2' if epoch else 'Epoch:hyp1'});f['after'].update(successor_refs=[s['node_id']])
 add('fresh-correction-successor',successor)
 add('new-epoch-explicit-fresh-successor',lambda f:successor(f,True))
 for k in ['assignee_ref','role_ref','scope_ref','owner_ref','assignment_basis_ref']:add('ending-alone-mutates-'+k,lambda f,k=k:f['after'].update({k:'other:token'}),True)
 add('in-place-epoch-rewrite-rejected',lambda f:f.update(epoch_after='Epoch:hyp2'),True)
 add('ending-discards-prior-history',lambda f:f.update(prior_history_retained=False),True)
 add('ending-lacks-decision-marker',lambda f:f.update(decision_marker=''),True)
 add('ending-replaces-Role',lambda f:f.update(Role_after='Role:hyp2'),True)
 add('ending-creates-membership',lambda f:f.update(membership_after=['Membership:hyp-new']),True)
 add('ending-automatically-revokes-independent-grant',lambda f:f.update(grant_after=[]),True)
 add('self-successor-rejected',lambda f:successor(f) or f['successor']['record'].update(node_id=f['before']['node_id']),True)
 add('same-epoch-as-new-epoch-rejected',lambda f:successor(f,True) or f['successor'].update(epoch=f['epoch_before']),True)
 return rows

def relation_conditions(schema,kind):
 def mentions(x):return isinstance(x,dict) and (x.get('const')==kind or any(mentions(v) for v in x.values())) or isinstance(x,list) and any(mentions(v) for v in x)
 def visit(x):
  if isinstance(x,dict):return ([x] if 'if' in x and mentions(x['if']) else [])+sum([visit(v) for v in x.values()],[])
  if isinstance(x,list):return sum([visit(v) for v in x],[])
  return []
 found=visit(schema)
 if len(found)!=1:raise ValueError('Ambiguous relation condition '+kind)
 return [{'source_kind':x['properties']['source']['properties']['kind']['const'],'target_kind':x['properties']['target']['properties']['kind']['const']} for x in found[0]['then']['properties']['payload']['oneOf']]

def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();root=b.ROOT/'authority/artifact-types/role-assignment/v1'
 paths={'descriptor':root/'artifact.json','schema':root/'schema.json','fixture':root/'fixtures/valid/record.json','artifact_projection':root/'ARTIFACT.md','fixture_projection':root/'fixtures/valid/RECORD.md','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','generator':b.ROOT/'tooling/generators/artifact_surface.py','shared_validator':b.ROOT/'tooling/validators/artifact_surface.py','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'}
 for p in sorted((root/'fixtures/invalid').glob('*.json')):paths['negative_'+p.stem]=p
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());tr=next(x for x in reg['admitted_contracts'] if x['semantic_kind']=='typed-relation' and x['lifecycle_state']=='admitted-current')
 paths['TR_schema']=b.ROOT/tr['schema_path'];paths['TR_fixture']=(b.ROOT/tr['artifact_path']).parent/'fixtures/valid/record.json'
 for semantic in ['person-reference','role','team','responsibility','authority-claim','decision']:
  row=next(x for x in reg['admitted_contracts'] if x['semantic_kind']==semantic and x['lifecycle_state']=='admitted-current');paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=(b.ROOT/row['artifact_path']).parent/'fixtures/valid/record.json'
 for row in kr['entries']:paths[row['relation_kind_ref']]=b.ROOT/row['instance_path']
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};artifact=docs['descriptor'];fixture=docs['fixture'];schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 entry=next(x for x in reg['admitted_contracts'] if x['artifact_type_ref']==artifact['artifact_type_ref']);source=load('t.json')['payload']['source'];binding=artifact['semantic_definition_bindings'][0]
 ck('exact-current-Type-overlay0070',entry['lifecycle_state']=='admitted-current' and entry['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and entry['artifact_sha256']==refs['descriptor']['sha256'] and entry['schema_sha256']==refs['schema']['sha256'])
 ck('exact-admitted-source0053-binding',binding['definition_ref']==source['version_ref'] and binding['path']==source['path'] and binding['sha256']==source['sha256'] and binding['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION')
 ck('historical-candidate-wording-authority-none',artifact['status']==fixture['status']=='candidate-unadmitted' and artifact['authority_effect']==fixture['authority_effect']=='none')
 ck('root-schema-renderer-validator-bound',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'] and artifact['schema_digest']==refs['schema']['sha256'] and artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['shared_validator']['sha256'] and schema['additionalProperties'] is False)
 ck('valid-fixture-exact-shape',not list(validator.iter_errors(fixture)));negative=[{'path':refs[n]['path'],'schema_rejected':bool(list(validator.iter_errors(docs[n])))} for n in sorted(refs) if n.startswith('negative_')];ck('all-selected-hostiles-rejected',bool(negative) and all(x['schema_rejected'] for x in negative))
 mod=types.ModuleType('_bound_artifact_renderer');mod.__file__=str(paths['generator']);exec(compile(raws['generator'],str(paths['generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture]);ck('two-descriptor-renders-exact',mod.render_artifact(artifact).encode()==mod.render_artifact(artifact).encode()==raws['artifact_projection']);ck('two-fixture-renders-exact',mod.render_instance(artifact,fixture).encode()==mod.render_instance(artifact,fixture).encode()==raws['fixture_projection']);ck('renderers-preserve-inputs',before==[artifact,fixture])
 for semantic in ['person-reference','role','team','responsibility','authority-claim','decision']:ck(semantic+'-selected-fixture-shape',not list(b.c.Draft202012Validator(docs[semantic+'_schema']).iter_errors(docs[semantic+'_fixture'])))
 ck('no-explicit-epoch-field',not any('epoch' in x for x in schema['properties']) and schema['additionalProperties'] is False)
 role=docs['role_fixture'];reference=docs['person-reference_fixture'];team=docs['team_fixture'];responsibility=docs['responsibility_fixture'];claim=docs['authority-claim_fixture'];decision=docs['decision_fixture']
 joins={'Role_literal_matches':fixture['role_ref']==role['node_id'],'Reference_literal_matches':fixture['assignee_ref']==reference['node_id'] and fixture['assignee_kind']=='person-reference','Role_Reference_assignment_literal_scopes_match':fixture['scope_ref']==role['scope_ref']==reference['scope_ref'],'Team_lists_Person_assignment':fixture['node_id'] in team['role_assignment_refs'],'is_Team_assignee':fixture['assignee_kind']=='team' and fixture['assignee_ref']==team['node_id'],'responsibility_literal_matches':responsibility['node_id'] in fixture['responsibility_refs'],'responsibility_literal_scope_matches':responsibility['scope_ref']==fixture['scope_ref'],'claim_literal_matches':claim['node_id'] in fixture['authority_claim_refs'],'claim_literal_scope_matches':claim['scope_ref']==fixture['scope_ref'],'basis_Decision_literal_matches':decision['node_id']==fixture['assignment_basis_ref'],'basis_Decision_literal_scope_matches':decision['scope_ref']==fixture['scope_ref'],'actual_Reference_owner_basis_claim_or_epoch_verified':False}
 ck('exact-literal-joins-and-unresolved-neighbors-retained',joins=={'Role_literal_matches':True,'Reference_literal_matches':True,'Role_Reference_assignment_literal_scopes_match':True,'Team_lists_Person_assignment':True,'is_Team_assignee':False,'responsibility_literal_matches':False,'responsibility_literal_scope_matches':False,'claim_literal_matches':False,'claim_literal_scope_matches':False,'basis_Decision_literal_matches':False,'basis_Decision_literal_scope_matches':False,'actual_Reference_owner_basis_claim_or_epoch_verified':False})
 probes=[]
 def probe(id,change,expected):
  r=copy.deepcopy(fixture);change(r);es=list(validator.iter_errors(r));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected carrier probe '+id+' '+str([x.message for x in es]))
  probes.append({'case_id':id,'record':r,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_currentness_owner_basis_claim_or_epoch_verified':False,'whole_source_conformance_established':False})
 probe('active-open-ended-accepted',lambda r:None,True)
 probe('Team-assignee-shape-accepted',lambda r:r.update(assignee_kind='team',assignee_ref=team['node_id']),True)
 probe('ended-with-null-end-accepted',lambda r:r.update(assignment_state='ended'),True)
 probe('revoked-with-null-end-accepted',lambda r:r.update(assignment_state='revoked'),True)
 probe('invalid-calendar-regex-accepted',lambda r:r['period'].update(start='2026-99-99T00:00:00Z'),True)
 probe('reversed-ended-period-shape-accepted',lambda r:r.update(assignment_state='ended') or r['period'].update(end='2026-10-04T00:00:00Z'),True)
 probe('unresolved-owner-basis-Role-Reference-claim-accepted',lambda r:r.update(owner_ref='absent:Owner',assignment_basis_ref='absent:Decision',role_ref='absent:Role',assignee_ref='absent:Reference',authority_claim_refs=['absent:Claim']),True)
 probe('empty-claim-and-responsibility-lists-accepted',lambda r:r.update(authority_claim_refs=[],responsibility_refs=[]),True)
 probe('self-successor-token-accepted',lambda r:r.update(successor_refs=[r['node_id']]),True)
 probe('assignment-node-equals-Role-token-accepted',lambda r:r.update(node_id=r['role_ref']),True)
 probe('AgentInstance-assignee-rejected',lambda r:r.update(assignee_kind='agent-instance'),False)
 probe('Human-Person-kind-rejected',lambda r:r.update(assignee_kind='person'),False)
 probe('active-finite-end-rejected',lambda r:r['period'].update(end='2026-10-07T00:00:00Z'),False)
 probe('explicit-extra-epoch-field-rejected',lambda r:r.update(epoch_ref='Epoch:hyp'),False)
 probe('blank-basis-rejected',lambda r:r.update(assignment_basis_ref=' '),False)
 probe('unknown-lifecycle-state-rejected',lambda r:r.update(assignment_state='superseded'),False)
 probe('implicit-grant-effect-rejected',lambda r:r.update(authority_effect='grant'),False)
 probe('duplicate-claim-refs-rejected',lambda r:r.update(authority_claim_refs=['Claim:same','Claim:same']),False)
 kinds={x['relation_kind_ref']:x for x in kr['entries']};roles=[]
 for id,row in sorted(kinds.items()):
  p=docs[id]['payload'];ck('current-Kind-binding-'+id,row['lifecycle_state']=='admitted-current' and row['instance_sha256']==refs[id]['sha256'] and row['exact_endpoint_pair_count']==len(p['allowed_endpoint_pairs']) and row['required_qualifier_axes']==p['qualifier_contract']['required_axes'])
  for direction,key,peer in [('source','source_kind','target_kind'),('target','target_kind','source_kind')]:
   peers=sorted({x[peer] for x in p['allowed_endpoint_pairs'] if x[key]=='role-assignment'})
   if peers:roles.append({'relation_kind_ref':id,'direction':direction,'counterpart_kinds':peers,'required_qualifier_axes':p['qualifier_contract']['required_axes']})
 ck('all41-Kinds-four-assignment-directions',len(kinds)==41 and [(x['relation_kind_ref'],x['direction']) for x in roles]==[('relation.challenges','target'),('relation.scopes-authority-over','target'),('relation.successor-of','source'),('relation.successor-of','target')])
 assignment_pairs=relation_conditions(docs['TR_schema'],'relation.assigned-to');ap=docs['relation.assigned-to']['payload'];authority_pairs=relation_conditions(docs['TR_schema'],'relation.scopes-authority-over');authority=docs['relation.scopes-authority-over']['payload'];key=lambda x:(x['source_kind'],x['target_kind'])
 ck('current-TRv3-exact-six-assigned-to-pairs',tr['artifact_type_ref']=='cal.artifact-type.typed-relation/v3' and tr['schema_sha256']==refs['TR_schema']['sha256'] and len(assignment_pairs)==6 and sorted(assignment_pairs,key=key)==sorted(ap['allowed_endpoint_pairs'],key=key))
 ck('assigned-to-record-token-not-assignment-endpoint',not any('role-assignment' in p.values() for p in assignment_pairs) and ap['qualifier_contract']['required_axes']==['assignment_kind','relation_record_ref'])
 missing=[p for p in authority['allowed_endpoint_pairs'] if p not in authority_pairs];ck('authority-Kind3-TR2-AuthorityBoundary-gap',len(authority['allowed_endpoint_pairs'])==3 and len(authority_pairs)==2 and missing==[{'source_kind':'authority-boundary','target_kind':'decision-scope'}] and not [p for p in authority_pairs if p not in authority['allowed_endpoint_pairs']])
 relation=copy.deepcopy(docs['TR_fixture']);relation['payload'].update(relation_kind_ref='relation.assigned-to',source={'kind':'person-reference','ref':fixture['assignee_ref'],'version_ref':'Reference@hyp'},target={'kind':'role','ref':fixture['role_ref'],'version_ref':'Role@hyp'},qualifiers={'assignment_kind':'role','relation_record_ref':fixture['node_id']});tv=b.c.Draft202012Validator(docs['TR_schema']);rp=[]
 def relation_probe(id,change,expected):
  r=copy.deepcopy(relation);change(r);es=list(tv.iter_errors(r));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected relation probe '+id+' '+str([x.message for x in es]))
  rp.append({'case_id':id,'record':r,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_relation_created':False,'actual_epoch_assignment_join_or_grant_verified':False})
 for p in assignment_pairs:relation_probe('current-assigned-to-'+p['source_kind']+'-to-'+p['target_kind'],lambda r,p=p:r['payload']['source'].update(kind=p['source_kind']) or r['payload']['target'].update(kind=p['target_kind']),True)
 relation_probe('unresolved-assignment-record-qualifier-accepted',lambda r:r['payload']['qualifiers'].update(relation_record_ref='absent:Assignment'),True)
 relation_probe('Team-endpoint-with-Person-assignment-token-accepted',lambda r:r['payload']['source'].update(kind='team',ref=team['node_id']),True)
 relation_probe('unreviewed-assignment-kind-label-accepted',lambda r:r['payload']['qualifiers'].update(assignment_kind='unreviewed-label'),True)
 relation_probe('RoleAssignment-as-endpoint-not-current-assigned-pair',lambda r:r['payload']['target'].update(kind='role-assignment'),False)
 relation_probe('missing-assignment-record-qualifier-rejected',lambda r:r['payload']['qualifiers'].pop('relation_record_ref'),False)
 relation_probe('extra-epoch-qualifier-rejected',lambda r:r['payload']['qualifiers'].update(epoch_ref='Epoch:hyp'),False)
 relation_probe('extra-permission-qualifier-rejected',lambda r:r['payload']['qualifiers'].update(permission_granted=True),False)
 authority_observations=[]
 for p in authority['allowed_endpoint_pairs']:
  r=copy.deepcopy(relation);r['payload'].update(relation_kind_ref='relation.scopes-authority-over',source={'kind':p['source_kind'],'ref':'Source:hyp','version_ref':'Source@hyp'},target={'kind':p['target_kind'],'ref':'Target:hyp','version_ref':'Target@hyp'},qualifiers={'authority_role':'recommendation','scope_ref':fixture['scope_ref']});es=list(tv.iter_errors(r));accepted=not es
  if accepted!=(p in authority_pairs):raise ValueError('Authority pair observation differs')
  authority_observations.append({'pair':p,'record':r,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_relation_or_grant_created':False})
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();history=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_assignment_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=json.loads((b.BASE/'definitions/cal.definition.role/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-RoleAssignment-profile/v1-candidate','status':'PASS-for-selected-temporal-epoch-history-profiles-and-exact-current-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_history_frame_count':len(history),'rejected_history_frames':sum(x['expected_rejection'] for x in history),'finite_history_frames':history,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'actual_relation_schema_probes':rp,'negative_fixture_checks':negative,'actual_join_observations':joins,'assignment_roles_from_all_current_Kinds':roles,'TR_assignment_schema_pairs':assignment_pairs,'TR_authority_scope_schema_pairs':authority_pairs,'current_authority_Kind_TR_pair_observations':authority_observations,'authority_scope_schema_gap':{'current_Kind_pairs':3,'current_TR_schema_pairs':2,'missing_TR_pairs':missing,'alignment_reviewed':False},'source_mapping_gaps':{'source_precedence_reviewed':False,'actual_Reference_Person_Team_Role_owner_basis_claim_denotations_authenticated':False,'temporal_and_epoch_source_correspondence_reviewed':False,'lifecycle_history_correction_and_grant_policy_reviewed':False,'whole_source_conformance_established':False},'new_assignments_or_relations_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Selected UTC effective/finite interval, explicit hypothetical epoch and separate grant/history profiles; exact carrier shape and current catalog observations. Active requires open end, schema has no epoch; AgentInstance generic pair exceeds carrier. Actual decision/responsibility/claim fixtures do not match assignment literals/scopes. No owner/basis/claim authentication, actual currentness, admission/grant/operation, universal proof, common-meaning alignment or whole source acceptance.'}
 if write:b.put('assignment-profile-checks.json',report)
 elif not b.r.same_json(report,load('assignment-profile-checks.json')):raise ValueError('Fresh assignment profile differs')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({k:r[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

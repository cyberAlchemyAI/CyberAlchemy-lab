"""Explicit outcome/scope/completion hypotheses and current-versus-historical carrier relation surfaces."""
import ast,copy,itertools,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def record():return json.loads((b.ROOT/'authority/artifact-types/responsibility/v1/fixtures/valid/record.json').read_bytes())
def current_roles():
 reg=json.loads((b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json').read_bytes());roles=[]
 for row in sorted(reg['entries'],key=lambda x:x['relation_kind_ref']):
  p=json.loads((b.ROOT/row['instance_path']).read_bytes())['payload']
  for direction,key,peer in [('source','source_kind','target_kind'),('target','target_kind','source_kind')]:
   peers=sorted({x[peer] for x in p['allowed_endpoint_pairs'] if x[key]=='responsibility'})
   if peers:roles.append({'relation_kind_ref':row['relation_kind_ref'],'direction':direction,'counterpart_kinds':peers,'required_qualifier_axes':p['qualifier_contract']['required_axes']})
 return roles

def baseline():
 r=record();return {'record':r,'responsibility_entity':'Responsibility:hyp1','carrier_entity':'Record:hyp1','outcome_token':'Outcome:hyp1','modes':['perform','answer-for'],'scope_mapping':{'policy':'separate-mapped','outer':r['scope_ref'],'payload':r['payload']['scope_ref'],'selection_marker':'hyp:explicit-scope-map'},'owner_selection_marker':'hyp:owner-qualification','accountable_selections':[{'token':x,'entity':'Role:hyp'+str(i),'selection_marker':'hyp:role-denotation'} for i,x in enumerate(r['payload']['accountable_role_refs'])],'completion_selections':[{'token':x,'selection_marker':'hyp:evidence-selection'} for x in r['payload']['completion_evidence_refs']],'outcome_observed':False,'completion_accepted':False,'completion_review_marker':None,'independent_grants':[],'obligation_derived_grants':[],'source_owner_reviewed':False,'actual_duty_owner_outcome_and_grant_verified':False}
def errors(p):
 es=[];r=p['record'];schema=json.loads((b.ROOT/'authority/artifact-types/responsibility/v1/schema.json').read_bytes())
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected profile');ck(not list(b.c.Draft202012Validator(schema).iter_errors(r)),'exact selected carrier shape');ck(p['responsibility_entity']!=p['carrier_entity'],'selected obligation Entity differs from record');ck(bool(p['outcome_token'].strip()) and bool(p['modes']) and set(p['modes'])<={'perform','maintain','answer-for','route'} and len(set(p['modes']))==len(p['modes']),'declared outcome and inclusive exact selected modes')
 sm=p['scope_mapping'];ck(set(sm)=={'policy','outer','payload','selection_marker'} and sm['outer']==r['scope_ref'] and sm['payload']==r['payload']['scope_ref'] and bool(sm['selection_marker']) and bool(sm['outer'].strip()) and bool(sm['payload'].strip()),'explicit outer/payload scope map')
 ck(sm['policy'] in ['exact-equal','separate-mapped'],'selected scope policy')
 if sm['policy']=='exact-equal':ck(sm['outer']==sm['payload'],'selected exact-equal scope policy')
 ck(bool(p['owner_selection_marker']),'hypothetical owner qualification required')
 selections=p['accountable_selections'];ck(sorted(x['token'] for x in selections)==sorted(r['payload']['accountable_role_refs']) and all(x['entity']!=p['responsibility_entity'] and bool(x['selection_marker']) for x in selections),'exact accountable Role denotations')
 ck(sorted(x['token'] for x in p['completion_selections'])==sorted(r['payload']['completion_evidence_refs']) and all(x['selection_marker'] for x in p['completion_selections']),'exact completion evidence selections')
 ck(not p['obligation_derived_grants'],'obligation alone does not generate grant');ck(p['source_owner_reviewed'] is False and p['actual_duty_owner_outcome_and_grant_verified'] is False,'no owner review or actual verification created')
 if p['completion_accepted']:ck(p['outcome_observed'] and bool(p['completion_review_marker']),'selected completion acceptance needs separate hypothetical observation/review')
 allowed={(x['relation_kind_ref'],x['direction'],peer) for x in current_roles() for peer in x['counterpart_kinds']}
 ck(all((x['relation_kind_ref'],x['direction'],x['counterpart_kind']) in allowed for x in r['relation_refs']),'exact current relation direction/peer surface')
 for g in p['independent_grants']:ck(set(g)=={'outcome','scope','action','claim_selection_marker','basis_marker','actual_verified'} and g['outcome']==p['outcome_token'] and g['scope']==sm['payload'] and bool(g['action']) and bool(g['claim_selection_marker']) and bool(g['basis_marker']) and g['actual_verified'] is False,'separate exact hypothetical outcome/scope/action/claim/basis grant')
 return es,{'outcome_observed_under_hypothesis':p['outcome_observed'],'completion_accepted_under_hypothesis':p['completion_accepted'] if not es else None,'declared_completion_tokens':len(r['payload']['completion_evidence_refs']),'hypothetical_grants':len(p['independent_grants']),'actual_outcome_completion_or_authority_verified':False}
def controls():
 rows=[]
 def add(id,change,bad=False):
  p=baseline();change(p);es,detail=errors(p)
  if bool(es)!=bad:raise ValueError('Unexpected Responsibility profile '+id+' '+str(es))
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'completion_observation':detail,'source_owner_reviewed':False,'actual_runtime_execution':False})
 add('declared-evidence-and-modes-with-unobserved-unaccepted-outcome',lambda p:None)
 add('several-modes-allowed-no-exclusive-mode-assumption',lambda p:p.update(modes=['perform','maintain','answer-for','route']))
 for mode in ['perform','maintain','answer-for','route']:add('only-'+mode+'-mode-permitted',lambda p,mode=mode:p.update(modes=[mode]))
 add('active-label-still-unfulfilled',lambda p:p['record'].update(lifecycle_state='active'))
 add('retired-label-does-not-make-outcome-true',lambda p:p['record'].update(lifecycle_state='retired'))
 add('independent-observation-without-acceptance',lambda p:p.update(outcome_observed=True))
 add('separate-hypothetical-observation-and-completion-review',lambda p:p.update(outcome_observed=True,completion_accepted=True,completion_review_marker='hyp:separate-completion-review'))
 def grant(p):p['independent_grants']=[{'outcome':p['outcome_token'],'scope':p['scope_mapping']['payload'],'action':'Action:hyp','claim_selection_marker':'hyp:claim-selection','basis_marker':'hyp:independent-basis','actual_verified':False}]
 add('independently-supported-grant-can-coexist',grant)
 def equal(p):p['record']['payload'].update(scope_ref=p['record']['scope_ref']);p['scope_mapping'].update(policy='exact-equal',payload=p['record']['scope_ref'])
 add('explicit-equal-scope-selection-permitted',equal)
 add('historical-current-member-Role-surface-permitted',lambda p:p['record']['relation_refs'][0].update(relation_kind_ref='relation.member-of',direction='source',counterpart_kind='role',counterpart_ref='Role:hyp'))
 for k in ['owner_selection_marker','outcome_token']:add('missing-'+k,lambda p,k=k:p.update({k:''}),True)
 add('empty-mode-list',lambda p:p.update(modes=[]),True)
 add('unselected-obligation-mode',lambda p:p.update(modes=['authorize']),True)
 add('duplicate-mode-label',lambda p:p.update(modes=['perform','perform']),True)
 add('unequal-scopes-misrepresented-as-equal',lambda p:p['scope_mapping'].update(policy='exact-equal'),True)
 add('missing-explicit-scope-map-marker',lambda p:p['scope_mapping'].update(selection_marker=''),True)
 add('wrong-payload-scope-map',lambda p:p['scope_mapping'].update(payload='other:Scope'),True)
 add('missing-accountable-denotation-selection',lambda p:p['accountable_selections'][0].update(selection_marker=''),True)
 add('accountable-Role-collapsed-with-duty',lambda p:p['accountable_selections'][0].update(entity=p['responsibility_entity']),True)
 add('completion-token-mismatch',lambda p:p['completion_selections'][0].update(token='other:Evidence'),True)
 add('completion-evidence-selection-missing',lambda p:p['completion_selections'][0].update(selection_marker=''),True)
 add('evidence-label-accepts-unobserved-outcome',lambda p:p.update(completion_accepted=True,completion_review_marker='hyp:review'),True)
 add('completion-without-separate-review',lambda p:p.update(outcome_observed=True,completion_accepted=True),True)
 add('carrier-collapsed-with-obligation',lambda p:p.update(carrier_entity=p['responsibility_entity']),True)
 add('mode-alone-grants-permission',lambda p:p.update(obligation_derived_grants=['Grant:hyp']),True)
 add('independent-grant-wrong-scope',lambda p:grant(p) or p['independent_grants'][0].update(scope='other:Scope'),True)
 add('independent-grant-missing-basis',lambda p:grant(p) or p['independent_grants'][0].update(basis_marker=''),True)
 add('source-review-not-created',lambda p:p.update(source_owner_reviewed=True),True)
 add('actual-authentication-not-created',lambda p:p.update(actual_duty_owner_outcome_and_grant_verified=True),True)
 add('wrong-assigned-to-direction-schema-accepts-profile-rejects',lambda p:p['record']['relation_refs'][0].update(direction='source'),True)
 add('member-of-Team-not-current-role-schema-accepts-profile-rejects',lambda p:p['record']['relation_refs'][0].update(relation_kind_ref='relation.member-of',direction='target',counterpart_kind='team'),True)
 add('AgentInstance-current-Kind-old-carrier-rejects',lambda p:p['record']['relation_refs'][0].update(counterpart_kind='agent-instance'),True)
 return rows

def frames():
 schema=json.loads((b.ROOT/'authority/artifact-types/responsibility/v1/schema.json').read_bytes());validator=b.c.Draft202012Validator(schema);rows=[]
 def base():
  a=record();return {'operation':'edit-label','before':a,'after':copy.deepcopy(a),'entity_before':'Responsibility:hyp1','entity_after':'Responsibility:hyp1','decision_marker':'hyp:obligation-decision','history_retained':True,'duty_before':'Duty:hyp1','duty_after':'Duty:hyp1','duty_change_marker':None,'outcome_observed':False,'completion_accepted':False,'completion_review_marker':None,'discharged':False,'discharge_marker':None,'successor':None,'grants_before':['Grant:hyp-independent'],'grants_after':['Grant:hyp-independent'],'separate_grant_decision_marker':None}
 def errors(f):
  es=[];a=f['before'];z=f['after'];op=f['operation']
  def ck(ok,msg):
   if not ok:es.append(msg)
  ck(op in ['edit-label','reassign-accountability','revise-duty','record-completion','discharge','retire','successor'],'selected finite operation');ck(not list(validator.iter_errors(a)) and not list(validator.iter_errors(z)),'exact selected carrier shapes');ck(a['node_id']==z['node_id'] and f['entity_before']==f['entity_after'],'continuing predecessor identity');ck(f['history_retained'] and bool(f['decision_marker']),'history and separate operation marker')
  if f['duty_before']!=f['duty_after'] or any(a['payload'][k]!=z['payload'][k] for k in ['responsibility_statement','scope_ref']):ck(bool(f['duty_change_marker']),'separate duty revision marker')
  if op=='edit-label':ck(a['payload']==z['payload'] and a['owner_ref']==z['owner_ref'] and a['scope_ref']==z['scope_ref'],'label change preserves selected obligation/accountability/owner/scope')
  if f['completion_accepted']:ck(f['outcome_observed'] and bool(f['completion_review_marker']),'completion needs selected observation and separate review')
  if f['discharged']:ck(f['completion_accepted'] and bool(f['discharge_marker']),'discharge requires separate accepted completion selection')
  if op=='discharge':ck(f['discharged'],'exact selected discharge outcome')
  if op=='retire':ck(z['lifecycle_state']=='retired','exact retirement label')
  if op=='successor':
   s=f['successor'];ck(s is not None and s['node_id']!=a['node_id'] and s['node_id'] in z['successor_refs'] and not list(validator.iter_errors(s)),'fresh explicit successor')
  ck(f['grants_before']==f['grants_after'] or bool(f['separate_grant_decision_marker']),'obligation/accountability/discharge alone does not change independent grants')
  return es
 def add(id,change,bad=False):
  f=base();change(f);es=errors(f)
  if bool(es)!=bad:raise ValueError('Unexpected Responsibility frame '+id+' '+str(es))
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('label-edit-preserves-unfulfilled-obligation',lambda f:f['after'].update(name='Other label'))
 add('reassign-accountability-independent-of-grant',lambda f:f.update(operation='reassign-accountability') or f['after']['payload'].update(accountable_role_refs=['Role:hyp-new']))
 add('separate-duty-revision',lambda f:f.update(operation='revise-duty',duty_after='Duty:hyp2',duty_change_marker='hyp:duty-revision') or f['after']['payload'].update(responsibility_statement='Maintain exact postimages'))
 def complete(f):f.update(operation='record-completion',outcome_observed=True,completion_accepted=True,completion_review_marker='hyp:completion-review')
 add('separate-selected-completion-review',complete)
 add('separate-selected-discharge-does-not-grant',lambda f:complete(f) or f.update(operation='discharge',discharged=True,discharge_marker='hyp:discharge'))
 add('retirement-can-retain-unfulfilled-duty-residue',lambda f:f.update(operation='retire') or f['after'].update(lifecycle_state='retired'))
 add('separate-grant-change-can-coexist',lambda f:f.update(grants_after=[],separate_grant_decision_marker='hyp:grant-decision'))
 def successor(f):s=copy.deepcopy(f['before']);s.update(node_id='Responsibility:hyp-successor');f.update(operation='successor',successor=s);f['after'].update(lifecycle_state='historical',successor_refs=[s['node_id']])
 add('fresh-historical-predecessor-and-successor',successor)
 add('silent-duty-revision',lambda f:f.update(duty_after='Duty:hyp2'),True)
 add('label-alone-mutates-accountability',lambda f:f['after']['payload'].update(accountable_role_refs=['Role:other']),True)
 add('evidence-label-alone-accepts-completion',lambda f:f.update(completion_accepted=True,completion_review_marker='hyp:review'),True)
 add('outcome-observed-without-completion-review',lambda f:f.update(completion_accepted=True,outcome_observed=True),True)
 add('retirement-auto-discharges-unfulfilled-duty',lambda f:f.update(operation='retire',discharged=True) or f['after'].update(lifecycle_state='retired'),True)
 add('discharge-without-separate-selection',lambda f:complete(f) or f.update(operation='discharge',discharged=True),True)
 add('accountability-change-auto-grants',lambda f:f.update(operation='reassign-accountability',grants_after=['Grant:hyp-new']),True)
 add('discharge-auto-revokes-independent-grant',lambda f:complete(f) or f.update(operation='discharge',discharged=True,discharge_marker='hyp:discharge',grants_after=[]),True)
 add('history-discarded',lambda f:f.update(history_retained=False),True)
 add('missing-operation-marker',lambda f:f.update(decision_marker=''),True)
 add('continuing-Entity-replaced',lambda f:f.update(entity_after='Responsibility:hyp2'),True)
 add('self-successor',lambda f:successor(f) or f['successor'].update(node_id=f['before']['node_id']),True)
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
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();root=b.ROOT/'authority/artifact-types/responsibility/v1'
 paths={'descriptor':root/'artifact.json','schema':root/'schema.json','fixture':root/'fixtures/valid/record.json','artifact_projection':root/'ARTIFACT.md','fixture_projection':root/'fixtures/valid/RECORD.md','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','generator':b.ROOT/'tooling/generators/endpoint_carrier.py','shared_validator':b.ROOT/'tooling/validators/endpoint_carrier.py','historical_relation_model':b.ROOT/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'}
 for p in sorted((root/'fixtures/invalid').glob('*.json')):paths['negative_'+p.stem]=p
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());tr=next(x for x in reg['admitted_contracts'] if x['semantic_kind']=='typed-relation' and x['lifecycle_state']=='admitted-current');paths['TR_schema']=b.ROOT/tr['schema_path'];paths['TR_fixture']=(b.ROOT/tr['artifact_path']).parent/'fixtures/valid/record.json'
 for semantic in ['person-reference','role','team','role-assignment','decision']:
  row=next(x for x in reg['admitted_contracts'] if x['semantic_kind']==semantic and x['lifecycle_state']=='admitted-current');paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=(b.ROOT/row['artifact_path']).parent/'fixtures/valid/record.json'
 for row in kr['entries']:paths[row['relation_kind_ref']]=b.ROOT/row['instance_path']
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};artifact=docs['descriptor'];fixture=docs['fixture'];schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 entry=next(x for x in reg['admitted_contracts'] if x['artifact_type_ref']==artifact['artifact_type_ref']);source=load('t.json')['payload']['source'];binding=artifact['semantic_definition_bindings'][0]
 ck('exact-current-Type0070',entry['lifecycle_state']=='admitted-current' and entry['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and entry['artifact_sha256']==refs['descriptor']['sha256'] and entry['schema_sha256']==refs['schema']['sha256']);ck('exact-Definition0053-binding',binding['definition_ref']==source['version_ref'] and binding['path']==source['path'] and binding['sha256']==source['sha256']);ck('historical-candidate-wording-authority-none',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']==fixture['authority_effect']=='none')
 ck('exact-root-schema-generator-validator',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'] and artifact['schema_digest']==refs['schema']['sha256'] and artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['shared_validator']['sha256']);ck('valid-fixture-shape',not list(validator.iter_errors(fixture)))
 negative=[{'path':refs[n]['path'],'schema_rejected':bool(list(validator.iter_errors(docs[n])))} for n in sorted(refs) if n.startswith('negative_')];ck('five-hostiles-rejected',len(negative)==5 and all(x['schema_rejected'] for x in negative))
 mod=types.ModuleType('_bound_endpoint_renderer');mod.__file__=str(paths['generator']);exec(compile(raws['generator'],str(paths['generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture]);ck('two-descriptor-renders-exact',mod.render_artifact(artifact).encode()==mod.render_artifact(artifact).encode()==raws['artifact_projection']);ck('two-fixture-renders-exact',mod.render_instance(artifact,fixture).encode()==mod.render_instance(artifact,fixture).encode()==raws['fixture_projection']);ck('renderers-preserve-inputs',before==[artifact,fixture])
 tree=ast.parse(raws['shared_validator']);functions=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='expected_roles'];ck('one-pure-historical-role-function',len(functions)==1);namespace={};exec(compile(ast.Module(body=functions,type_ignores=[]),str(paths['shared_validator']),'exec'),namespace);historical=namespace['expected_roles']('responsibility',docs['historical_relation_model']);ck('descriptor-two-roles-match-exact-historical-model',len(historical)==2 and historical==artifact['relation_roles'])
 for semantic in ['person-reference','role','team','role-assignment','decision']:ck(semantic+'-selected-fixture-shape',not list(b.c.Draft202012Validator(docs[semantic+'_schema']).iter_errors(docs[semantic+'_fixture'])))
 roles=current_roles();kinds={x['relation_kind_ref']:x for x in kr['entries']}
 for id,row in kinds.items():
  p=docs[id]['payload'];ck('current-Kind-binding-'+id,row['lifecycle_state']=='admitted-current' and row['instance_sha256']==refs[id]['sha256'] and row['exact_endpoint_pair_count']==len(p['allowed_endpoint_pairs']) and row['required_qualifier_axes']==p['qualifier_contract']['required_axes'])
 ck('all41-current-Kinds-five-Responsibility-directions',len(kinds)==41 and [(x['relation_kind_ref'],x['direction']) for x in roles]==[('relation.assigned-to','target'),('relation.challenges','target'),('relation.member-of','source'),('relation.successor-of','source'),('relation.successor-of','target')])
 historical_set={(x['relation_kind_ref'],x['direction'],peer) for x in historical for peer in x['counterpart_kinds']};current_set={(x['relation_kind_ref'],x['direction'],peer) for x in roles for peer in x['counterpart_kinds']};missing=sorted(current_set-historical_set);ck('historical-three-versus-current-seven-triplets',len(historical_set)==3 and len(current_set)==7 and len(missing)==4 and historical_set<=current_set)
 joins={'outer_scope_equals_payload_scope':fixture['scope_ref']==fixture['payload']['scope_ref'],'accountable_Role_literal_matches':docs['role_fixture']['node_id'] in fixture['payload']['accountable_role_refs'],'completion_Decision_literal_matches':docs['decision_fixture']['node_id'] in fixture['payload']['completion_evidence_refs'],'assigned_Reference_literal_matches':fixture['relation_refs'][0]['counterpart_ref']==docs['person-reference_fixture']['node_id'],'listed_by_Role':fixture['node_id'] in docs['role_fixture']['responsibility_refs'],'listed_by_Team':fixture['node_id'] in docs['team_fixture']['responsibility_refs'],'listed_by_RoleAssignment':fixture['node_id'] in docs['role-assignment_fixture']['responsibility_refs'],'actual_duty_owner_outcome_completion_or_grant_verified':False};ck('all-literal-neighbor-and-scope-gaps-retained',not any(joins.values()))
 probes=[]
 def probe(id,change,expected):
  r=copy.deepcopy(fixture);change(r);es=list(validator.iter_errors(r));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected Responsibility carrier '+id+' '+str([x.message for x in es]))
  probes.append({'case_id':id,'record':r,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_duty_outcome_completion_or_grant_verified':False,'whole_source_conformance_established':False})
 probe('active-with-unresolved-completion-token-accepted',lambda r:r.update(lifecycle_state='active'),True)
 probe('outer-and-payload-scopes-differ-accepted',lambda r:None,True)
 probe('unresolved-owner-accountable-Role-evidence-accepted',lambda r:r.update(owner_ref='absent:Owner') or r['payload'].update(accountable_role_refs=['absent:Role'],completion_evidence_refs=['absent:Evidence']),True)
 probe('whitespace-scope-statement-owner-accepted-by-minLength',lambda r:r.update(scope_ref=' ',owner_ref=' ') or r['payload'].update(scope_ref=' ',responsibility_statement=' '),True)
 probe('retired-without-proven-fulfillment-accepted',lambda r:r.update(lifecycle_state='retired'),True)
 probe('self-successor-shape-accepted',lambda r:r.update(successor_refs=[r['node_id']]),True)
 probe('node-equals-accountable-Role-token-accepted',lambda r:r.update(node_id=r['payload']['accountable_role_refs'][0]),True)
 probe('no-general-evidence-ref-required',lambda r:r.update(evidence_refs=[]),True)
 probe('empty-completion-evidence-list-rejected',lambda r:r['payload'].update(completion_evidence_refs=[]),False)
 probe('empty-accountable-Role-list-rejected',lambda r:r['payload'].update(accountable_role_refs=[]),False)
 probe('extra-actual-completion-field-rejected',lambda r:r.update(completed=True),False)
 probe('permission-grant-effect-rejected',lambda r:r.update(authority_effect='grant'),False)
 probe('unknown-completed-lifecycle-label-rejected',lambda r:r.update(lifecycle_state='completed'),False)
 probe('AgentInstance-metadata-peer-not-old-schema',lambda r:r['relation_refs'][0].update(counterpart_kind='agent-instance'),False)
 cross=[]
 for kind,direction,peer in itertools.product(schema['properties']['relation_refs']['items']['properties']['relation_kind_ref']['enum'],['source','target'],schema['properties']['relation_refs']['items']['properties']['counterpart_kind']['enum']):
  r=copy.deepcopy(fixture);r['relation_refs'][0].update(relation_kind_ref=kind,direction=direction,counterpart_kind=peer);es=list(validator.iter_errors(r));accepted=not es
  if not accepted:raise ValueError('Unexpected schema coupling added')
  cross.append({'relation_kind_ref':kind,'direction':direction,'counterpart_kind':peer,'schema_accepted':accepted,'descriptor_declared':(kind,direction,peer) in historical_set,'current_Kind_declared':(kind,direction,peer) in current_set,'record':r,'actual_relation_created':False})
 metadata=[]
 for kind,direction,peer in sorted(current_set):
  r=copy.deepcopy(fixture);r['relation_refs'][0].update(relation_kind_ref=kind,direction=direction,counterpart_kind=peer);es=list(validator.iter_errors(r));accepted=not es
  if accepted!=((kind,direction,peer) in historical_set):raise ValueError('Current-role metadata boundary differs')
  metadata.append({'relation_kind_ref':kind,'direction':direction,'counterpart_kind':peer,'schema_accepted':accepted,'errors':[x.message for x in es],'record':r,'actual_relation_created':False})
 tv=b.c.Draft202012Validator(docs['TR_schema']);pair_tests=[]
 for id in sorted({x['relation_kind_ref'] for x in roles}):
  p=docs[id]['payload'];schema_pairs=relation_conditions(docs['TR_schema'],id)
  for pair in [x for x in p['allowed_endpoint_pairs'] if 'responsibility' in x.values()]:
   r=copy.deepcopy(docs['TR_fixture']);r['payload'].update(relation_kind_ref=id,source={'kind':pair['source_kind'],'ref':'Source:hyp','version_ref':'Source@hyp'},target={'kind':pair['target_kind'],'ref':'Target:hyp','version_ref':'Target@hyp'},qualifiers={x:'hyp:qualifier' for x in p['qualifier_contract']['required_axes']});es=list(tv.iter_errors(r));accepted=not es
   if accepted!=(pair in schema_pairs):raise ValueError('Current Responsibility Kind/TR pair differs')
   pair_tests.append({'relation_kind_ref':id,'pair':pair,'schema_accepted':accepted,'errors':[x.message for x in es],'record':r,'actual_obligation_owner_assignment_or_grant_verified':False,'actual_relation_created':False})
 ck('current-TRv3-bound-and-six-Responsibility-pairs-accepted',tr['artifact_type_ref']=='cal.artifact-type.typed-relation/v3' and tr['schema_sha256']==refs['TR_schema']['sha256'] and len(pair_tests)==6 and all(x['schema_accepted'] for x in pair_tests))
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();history=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_responsibility_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=json.loads((b.BASE/'definitions/cal.definition.role-assignment/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-Responsibility-profile/v1-candidate','status':'PASS-for-selected-outcome-scope-completion-history-and-current-carrier-boundaries','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_history_frame_count':len(history),'rejected_history_frames':sum(x['expected_rejection'] for x in history),'finite_history_frames':history,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'negative_fixture_checks':negative,'actual_join_observations':joins,'Responsibility_roles_from_all_current_Kinds':roles,'historical_descriptor_roles':historical,'historical_current_role_gap':{'historical_triplets':len(historical_set),'current_triplets':len(current_set),'missing_descriptor_triplets':[{'relation_kind_ref':k,'direction':d,'counterpart_kind':peer} for k,d,peer in missing],'alignment_reviewed':False},'carrier_cross_product_observations':cross,'current_role_carrier_schema_observations':metadata,'current_Kind_TR_pair_observations':pair_tests,'source_mapping_gaps':{'source_precedence_reviewed':False,'actual_owner_obligation_Role_Reference_outcome_completion_denotations_authenticated':False,'outer_payload_scope_and_current_relation_alignment_reviewed':False,'deontic_temporal_history_delegation_and_discharge_policy_reviewed':False,'whole_source_conformance_established':False},'new_responsibilities_or_relations_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Selected hypothetical outcome/scope/completion/grant/history rules and exact current/historical carrier observations. Completion tokens and lifecycle do not prove fulfillment; root/payload scopes and all selected Role/Reference/Decision/Team/Assignment links differ. Historical descriptor3 versus current7 triplets; schema cross12 accepts9 undeclared, current4additional metadata directions/peers rejected though6current TR pairs pass. No actual deontic/owner/fulfillment/permission/operation/admission, approved alignment or whole-definition proof.'}
 if write:b.put('responsibility-profile-checks.json',report)
 elif not b.r.same_json(report,load('responsibility-profile-checks.json')):raise ValueError('Fresh Responsibility profile differs')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({k:r[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

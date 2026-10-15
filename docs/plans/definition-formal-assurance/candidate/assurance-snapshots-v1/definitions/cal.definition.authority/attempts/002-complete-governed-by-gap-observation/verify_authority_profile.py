"""Explicit hypothetical governing/context/transfer policy; exact side carriers do not replace Authority."""
import copy,itertools,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def rec(kind):return json.loads((b.ROOT/'authority/artifact-types'/kind/'v1/fixtures/valid/record.json').read_bytes())
def baseline():
 c=rec('authority-claim');boundary=rec('authority-boundary');values={'scope':c['payload']['decision_scope_ref'],'owner':c['payload']['claimant_ref'],'surface':'Surface:hyp','object':'Object:hyp','operation':c['payload']['claimed_permissions'][0],'basis':c['payload']['authority_basis_refs'][0],'effect':'artifact-type-admission','challenge':c['challenge_route']};context={k:values[k] for k in ['scope','owner','surface','object','operation','effect']};context.update(purpose='Purpose:hyp',mirror='Mirror:hyp-canonical',source_space='SourceSpace:hyp-lab')
 return {'claim_record':c,'boundary_record':boundary,'authority_entity':'Authority:hyp1','claim_entity':'Claim:hyp1','boundary_entity':'Boundary:hyp1','tuple_fields':{n:{'value':values[n],'selection_marker':'hyp:'+n+'-denotation'} for n in values},'context':context,'query':copy.deepcopy(context),'scope_mapping_marker':'hyp:explicit-claim-scope-to-boundary-scope','operation_effect_mapping_marker':'hyp:permission-to-effect-selection','effectivity_selection_marker':'hyp:effective-at-query','effective_at_query':True,'governing_selected':False,'independent_support':{'owner_authentication':None,'claim_fidelity':None,'basis_decision':None,'admission_disposition':None},'implicit_grants':[],'source_owner_reviewed':False,'actual_authority_or_governing_effect_verified':False}
def errors(p):
 es=[]
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected profile')
 for kind,key in [('authority-claim','claim_record'),('authority-boundary','boundary_record')]:ck(not list(b.c.Draft202012Validator(json.loads((b.ROOT/'authority/artifact-types'/kind/'v1/schema.json').read_bytes())).iter_errors(p[key])),'exact selected '+kind+' shape')
 ck(len({p['authority_entity'],p['claim_entity'],p['boundary_entity']})==3,'selected Authority Claim Boundary Entities distinct')
 fields=p['tuple_fields'];ck(set(fields)=={n.lower() for n in b.FIELDS} and all(bool(x['value'].strip()) and bool(x['selection_marker']) for x in fields.values()),'eight explicit hypothetical tuple field values/maps')
 ck(fields['scope']['value']==p['claim_record']['payload']['decision_scope_ref'] and fields['owner']['value']==p['claim_record']['payload']['claimant_ref'] and fields['operation']['value'] in p['claim_record']['payload']['claimed_permissions'] and fields['basis']['value'] in p['claim_record']['payload']['authority_basis_refs'] and fields['challenge']['value']==p['claim_record']['challenge_route'],'exact selected claim literal fields; no actual authentication')
 ck(set(p['context'])==set(p['query'])=={'scope','owner','surface','object','operation','effect','purpose','mirror','source_space'} and all(bool(x.strip()) for x in p['context'].values()) and all(bool(x.strip()) for x in p['query'].values()),'explicit nine-axis context/query')
 ck(all(p['context'][n]==fields[n]['value'] for n in ['scope','owner','surface','object','operation','effect']),'context exact selected tuple values')
 ck(bool(p['scope_mapping_marker']) and bool(p['operation_effect_mapping_marker']) and bool(p['effectivity_selection_marker']),'scope/effect/time mappings are explicit hypotheses')
 ck(p['effective_at_query'] in [True,False,None],'known or unresolved selected effectivity')
 ck(not p['implicit_grants'],'field names/evidence/source truth/shape do not create grants');ck(p['source_owner_reviewed'] is False and p['actual_authority_or_governing_effect_verified'] is False,'no source review or actual governing verification created')
 if p['governing_selected']:ck(all(p['independent_support'].get(n) for n in ['owner_authentication','claim_fidelity','basis_decision','admission_disposition']),'separate hypothetical owner/fidelity/basis/admission support')
 match=p['context']==p['query'];effect=fields['effect']['value'];boundary=p['boundary_record']['payload'];effect_allowed=effect in boundary['allowed_effect_kinds'] and effect not in boundary['excluded_effect_kinds'];not_revoked=boundary['revocation_state']=='not-revoked'
 eligible=None if es or p['effective_at_query'] is None else match and effect_allowed and not_revoked and p['effective_at_query'];permitted=None if eligible is None else bool(eligible and p['governing_selected'])
 return es,{'context_matches_under_hypothesis':match,'effect_allowed_under_hypothesis':effect_allowed,'not_revoked_label':not_revoked,'eligible_under_hypothesis':eligible,'counting_operation_permitted_under_hypothesis':permitted,'field_completeness_implies_actual_validity':False,'actual_authentication_or_effect_verified':False}
def controls():
 rows=[]
 def add(id,change,bad=False,permitted=False):
  p=baseline();change(p);es,detail=errors(p)
  if bool(es)!=bad or detail['counting_operation_permitted_under_hypothesis']!=(None if bad else permitted):raise ValueError('Unexpected Authority profile '+id+' '+str((es,detail)))
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'governing_observation':detail,'source_owner_reviewed':False,'actual_runtime_execution':False})
 add('complete-hypothetical-fields-still-no-selected-governing-permission',lambda p:None)
 add('active-claim-label-still-no-governing-permission',lambda p:p['claim_record'].update(lifecycle_state='active'))
 add('allowed-boundary-effect-label-still-no-governing-permission',lambda p:None)
 def supported(p):p.update(governing_selected=True,independent_support={n:'hyp:separate-'+n for n in p['independent_support']})
 add('separate-owner-fidelity-basis-admission-hypotheses',supported,permitted=True)
 for axis in ['scope','owner','surface','object','operation','effect','purpose','mirror','source_space']:add('supported-right-not-automatically-transferred-'+axis,lambda p,axis=axis:supported(p) or p['query'].update({axis:'other:'+axis}))
 for state in ['revoked','expired']:add(state+'-boundary-label-prevents-selected-permission',lambda p,state=state:supported(p) or p['boundary_record']['payload'].update(revocation_state=state))
 add('not-effective-at-query-prevents-selected-permission',lambda p:supported(p) or p.update(effective_at_query=False))
 add('unresolved-effectivity-retains-unknown',lambda p:supported(p) or p.update(effective_at_query=None),permitted=None)
 add('excluded-effect-prevents-selected-permission',lambda p:supported(p) or p['boundary_record']['payload']['excluded_effect_kinds'].append(p['tuple_fields']['effect']['value']))
 add('unallowed-effect-prevents-selected-permission',lambda p:supported(p) or p['boundary_record']['payload'].update(allowed_effect_kinds=['other-effect']))
 for n in ['owner_authentication','claim_fidelity','basis_decision','admission_disposition']:add('governing-selected-missing-'+n,lambda p,n=n:supported(p) or p['independent_support'].update({n:None}),True)
 for n in [x.lower() for x in b.FIELDS]:add('missing-hypothetical-'+n+'-field-map',lambda p,n=n:p['tuple_fields'][n].update(selection_marker=''),True)
 add('empty-hypothetical-object-field',lambda p:p['tuple_fields']['object'].update(value=' '),True)
 add('missing-context-purpose',lambda p:p['context'].update(purpose=''),True)
 add('wrong-literal-claim-basis',lambda p:p['tuple_fields']['basis'].update(value='other:Decision'),True)
 for marker in ['scope_mapping_marker','operation_effect_mapping_marker','effectivity_selection_marker']:add('missing-'+marker,lambda p,marker=marker:p.update({marker:''}),True)
 add('Authority-collapsed-with-Claim',lambda p:p.update(authority_entity=p['claim_entity']),True)
 add('Authority-collapsed-with-Boundary',lambda p:p.update(authority_entity=p['boundary_entity']),True)
 add('field-completeness-generates-grant',lambda p:p.update(implicit_grants=['Grant:hyp']),True)
 add('source-owner-approval-not-created',lambda p:p.update(source_owner_reviewed=True),True)
 add('actual-governing-authentication-not-created',lambda p:p.update(actual_authority_or_governing_effect_verified=True),True)
 return rows

def frames():
 rows=[]
 def baseline_frame():
  p=baseline();return {'operation':'copy-mirror','authority_entity_before':'Authority:hyp1','authority_entity_after':'Authority:hyp1','context_before':p['context'],'context_after':{**p['context'],'mirror':'Mirror:hyp-generated'},'history_retained':True,'decision_marker':'hyp:operation-decision','requalification_marker':None,'governing_before':False,'governing_after':False,'governing_admission_marker':None,'revocation_marker':None,'successor_entity':None,'successor_edge_marker':None,'independent_grants_before':['Grant:hyp-independent'],'independent_grants_after':['Grant:hyp-independent'],'separate_grant_decision_marker':None}
 def errors(f):
  es=[];op=f['operation'];changed=f['context_before']!=f['context_after']
  def ck(ok,msg):
   if not ok:es.append(msg)
  ck(op in ['copy-mirror','move-scope','change-owner','change-surface','revise-operation','admit-governing','revoke','successor'],'selected finite operation');ck(f['history_retained'] and bool(f['decision_marker']),'history and separate operation marker');ck(f['authority_entity_before']==f['authority_entity_after'],'continuing predecessor Authority identity')
  if f['governing_after'] and (changed or not f['governing_before']):ck(bool(f['requalification_marker']) and bool(f['governing_admission_marker']),'changed context or new governing posture needs separate requalification/admission selection')
  if op=='revoke':ck(not f['governing_after'] and bool(f['revocation_marker']),'selected revocation needs separate marker')
  if op=='successor':ck(f['successor_entity'] is not None and f['successor_entity']!=f['authority_entity_before'] and bool(f['successor_edge_marker']),'fresh explicit successor, no automatic right transfer')
  ck(f['independent_grants_before']==f['independent_grants_after'] or bool(f['separate_grant_decision_marker']),'right/claim operation alone does not alter other grants')
  return es
 def add(id,change,bad=False):
  f=baseline_frame();change(f);es=errors(f)
  if bool(es)!=bad:raise ValueError('Unexpected Authority frame '+id+' '+str(es))
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('generated-mirror-copy-does-not-govern',lambda f:None)
 for op,axis in [('move-scope','scope'),('change-owner','owner'),('change-surface','surface'),('revise-operation','operation')]:add(op+'-retains-unqualified-posture',lambda f,op=op,axis=axis:f.update(operation=op) or f['context_after'].update({axis:'other:'+axis}))
 def admit(f):f.update(operation='admit-governing',governing_after=True,requalification_marker='hyp:owner-context-requalification',governing_admission_marker='hyp:separate-governing-admission')
 add('explicit-selected-requalification-and-governing-admission',admit)
 add('separate-revocation-preserves-independent-grants',lambda f:f.update(operation='revoke',governing_before=True,revocation_marker='hyp:revocation'))
 add('fresh-successor-does-not-auto-transfer',lambda f:f.update(operation='successor',successor_entity='Authority:hyp2',successor_edge_marker='hyp:successor-edge'))
 add('separate-independent-grant-change-can-coexist',lambda f:f.update(independent_grants_after=[],separate_grant_decision_marker='hyp:grant-decision'))
 add('mirror-copy-auto-governs',lambda f:f.update(governing_after=True),True)
 add('context-change-preserves-governing-without-requalification',lambda f:f.update(governing_before=True,governing_after=True),True)
 add('new-governing-posture-missing-admission-selection',lambda f:admit(f) or f.update(governing_admission_marker=None),True)
 add('missing-history',lambda f:f.update(history_retained=False),True)
 add('missing-operation-decision',lambda f:f.update(decision_marker=''),True)
 add('revocation-missing-marker',lambda f:f.update(operation='revoke',governing_before=True),True)
 add('revocation-remains-governing',lambda f:admit(f) or f.update(operation='revoke',governing_before=True,revocation_marker='hyp:revocation'),True)
 add('self-successor',lambda f:f.update(operation='successor',successor_entity=f['authority_entity_before'],successor_edge_marker='hyp:edge'),True)
 add('predecessor-Entity-replaced',lambda f:f.update(authority_entity_after='Authority:hyp2'),True)
 add('right-revocation-auto-revokes-independent-grant',lambda f:f.update(operation='revoke',revocation_marker='hyp:revocation',independent_grants_after=[]),True)
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
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();paths={'type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','generator':b.ROOT/'tooling/generators/endpoint_carrier.py','shared_validator':b.ROOT/'tooling/validators/endpoint_carrier.py'};reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes())
 selected={}
 for semantic in ['authority-claim','authority-boundary','decision-scope','role-assignment','role','principal','evidence-set','decision','typed-relation']:
  row=next(x for x in reg['admitted_contracts'] if x['semantic_kind']==semantic and x['lifecycle_state']=='admitted-current');selected[semantic]=row;root=(b.ROOT/row['artifact_path']).parent;paths[semantic+'_descriptor']=root/'artifact.json';paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=root/'fixtures/valid/record.json'
  if semantic in ['authority-claim','authority-boundary']:
   paths[semantic+'_artifact_projection']=root/'ARTIFACT.md';paths[semantic+'_fixture_projection']=root/'fixtures/valid/RECORD.md';paths[semantic+'_declared_validator']=b.ROOT/json.loads((root/'artifact.json').read_bytes())['validation_contract']['shared_validator_path']
   for p in sorted((root/'fixtures/invalid').glob('*.json')):paths[semantic+'_negative_'+p.stem]=p
 for row in kr['entries']:paths[row['relation_kind_ref']]=b.ROOT/row['instance_path']
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 authority_rows=[x for x in reg['admitted_contracts'] if x['semantic_kind']=='authority' and x['lifecycle_state']=='admitted-current'];direct_bindings=[x['artifact_type_ref'] for x in reg['admitted_contracts'] if load('t.json')['payload']['source']['version_ref'] in x['semantic_definition_refs'] and x['lifecycle_state']=='admitted-current'];ck('no-dedicated-current-Authority-type-or-direct-definition-binding',not authority_rows and not direct_bindings)
 mod=types.ModuleType('_bound_endpoint_renderer');mod.__file__=str(paths['generator']);exec(compile(raws['generator'],str(paths['generator']),'exec'),mod.__dict__)
 for semantic,row in selected.items():
  artifact=docs[semantic+'_descriptor'];schema=docs[semantic+'_schema'];fixture=docs[semantic+'_fixture'];b.c.Draft202012Validator.check_schema(schema);ck(semantic+'-exact-current-descriptor-schema-binding',row['artifact_sha256']==refs[semantic+'_descriptor']['sha256'] and row['schema_sha256']==refs[semantic+'_schema']['sha256']);ck(semantic+'-fixture-shape',not list(b.c.Draft202012Validator(schema).iter_errors(fixture)))
  if semantic in ['authority-claim','authority-boundary']:
   before=copy.deepcopy([artifact,fixture]);ck(semantic+'-root-schema-renderer-validator-digests',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'] and artifact['schema_digest']==refs[semantic+'_schema']['sha256'] and artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs[semantic+'_declared_validator']['sha256']);ck(semantic+'-two-descriptor-renders-exact',mod.render_artifact(artifact).encode()==mod.render_artifact(artifact).encode()==raws[semantic+'_artifact_projection']);ck(semantic+'-two-fixture-renders-exact',mod.render_instance(artifact,fixture).encode()==mod.render_instance(artifact,fixture).encode()==raws[semantic+'_fixture_projection']);ck(semantic+'-inputs-preserved',before==[artifact,fixture]);ck(semantic+'-historical-authority-none-posture',artifact['authority_effect']==fixture['authority_effect']=='none' and artifact['status']=='candidate-unadmitted')
 negatives=[]
 for n in sorted(refs):
  if '_negative_' in n:
   semantic=n.split('_negative_',1)[0];es=list(b.c.Draft202012Validator(docs[semantic+'_schema']).iter_errors(docs[n]));negatives.append({'path':refs[n]['path'],'schema_rejected':bool(es)})
 ck('ten-side-carrier-hostiles-rejected',len(negatives)==10 and all(x['schema_rejected'] for x in negatives))
 joins={'claim_DecisionScope_literal_matches':docs['authority-claim_fixture']['payload']['decision_scope_ref']==docs['decision-scope_fixture']['node_id'],'boundary_authority_scope_DecisionScope_literal_matches':docs['authority-boundary_fixture']['payload']['authority_scope_ref']==docs['decision-scope_fixture']['node_id'],'boundary_relation_DecisionScope_literal_matches':docs['authority-boundary_fixture']['relation_refs'][0]['counterpart_ref']==docs['decision-scope_fixture']['node_id'],'claim_EvidenceSet_literal_matches':docs['authority-claim_fixture']['relation_refs'][0]['counterpart_ref']==docs['evidence-set_fixture']['node_id'],'boundary_Principal_literal_matches':docs['authority-boundary_fixture']['payload']['accountable_principal_ref']==docs['principal_fixture']['node_id'],'claim_claimant_Role_literal_matches':docs['authority-claim_fixture']['payload']['claimant_ref']==docs['role_fixture']['node_id'],'claim_basis_Decision_literal_matches':docs['decision_fixture']['node_id'] in docs['authority-claim_fixture']['payload']['authority_basis_refs'],'boundary_owner_Role_literal_matches':docs['authority-boundary_fixture']['payload']['owner_role_ref']==docs['role_fixture']['node_id'],'Claim_Boundary_root_scopes_equal':docs['authority-claim_fixture']['scope_ref']==docs['authority-boundary_fixture']['scope_ref'],'actual_right_owner_basis_scope_or_permission_verified':False};ck('exact-side-carrier-literal-joins-and-gaps',joins=={'claim_DecisionScope_literal_matches':False,'boundary_authority_scope_DecisionScope_literal_matches':False,'boundary_relation_DecisionScope_literal_matches':True,'claim_EvidenceSet_literal_matches':True,'boundary_Principal_literal_matches':False,'claim_claimant_Role_literal_matches':False,'claim_basis_Decision_literal_matches':False,'boundary_owner_Role_literal_matches':False,'Claim_Boundary_root_scopes_equal':False,'actual_right_owner_basis_scope_or_permission_verified':False})
 kinds={x['relation_kind_ref']:x for x in kr['entries']};authority_endpoints=[];side_roles=[]
 for id,row in sorted(kinds.items()):
  p=docs[id]['payload'];ck('current-Kind-binding-'+id,row['lifecycle_state']=='admitted-current' and row['instance_sha256']==refs[id]['sha256'] and row['exact_endpoint_pair_count']==len(p['allowed_endpoint_pairs']) and row['required_qualifier_axes']==p['qualifier_contract']['required_axes'])
  authority_endpoints += [{'relation_kind_ref':id,'pair':pair} for pair in p['allowed_endpoint_pairs'] if 'authority' in pair.values()]
  for semantic in ['authority-claim','authority-boundary']:
   for direction,key,peer in [('source','source_kind','target_kind'),('target','target_kind','source_kind')]:
    peers=sorted({x[peer] for x in p['allowed_endpoint_pairs'] if x[key]==semantic})
    if peers:side_roles.append({'semantic_kind':semantic,'relation_kind_ref':id,'direction':direction,'counterpart_kinds':peers,'required_qualifier_axes':p['qualifier_contract']['required_axes']})
 ck('no-Authority-endpoint-in-all41currentKinds',len(kinds)==41 and not authority_endpoints);ck('five-Claim-two-Boundary-current-directions',sum(x['semantic_kind']=='authority-claim' for x in side_roles)==5 and sum(x['semantic_kind']=='authority-boundary' for x in side_roles)==2)
 probes=[]
 def probe(semantic,id,change,expected):
  r=copy.deepcopy(docs[semantic+'_fixture']);change(r);es=list(b.c.Draft202012Validator(docs[semantic+'_schema']).iter_errors(r));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected side carrier probe '+id+' '+str([x.message for x in es]))
  probes.append({'semantic_kind':semantic,'case_id':id,'record':r,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_Authority_claim_authentication_or_effect_verified':False,'Authority_primitive_carrier_established':False})
 for semantic in ['authority-claim','authority-boundary']:
  probe(semantic,'active-label-does-not-enforce-governing-authentication',lambda r:r.update(lifecycle_state='active'),True)
  probe(semantic,'unresolved-owner-scope-reference-accepted',lambda r:r.update(owner_ref='absent:Owner',scope_ref='absent:Scope'),True)
  probe(semantic,'self-successor-token-accepted',lambda r:r.update(successor_refs=[r['node_id']]),True)
  probe(semantic,'whitespace-owner-scope-accepted-minLength',lambda r:r.update(owner_ref=' ',scope_ref=' '),True)
  probe(semantic,'actual-grant-effect-rejected',lambda r:r.update(authority_effect='grant'),False)
  probe(semantic,'Authority-primitive-kind-rejected',lambda r:r.update(kind='authority'),False)
  probe(semantic,'extra-source-tuple-surface-field-rejected',lambda r:r['payload'].update(authority_surface_ref='Surface:hyp'),False)
 probe('authority-claim','unresolved-basis-and-permission-label-accepted',lambda r:r['payload'].update(authority_basis_refs=['absent:Decision'],claimed_permissions=['unreviewed:Permission']),True)
 probe('authority-claim','empty-basis-list-rejected',lambda r:r['payload'].update(authority_basis_refs=[]),False)
 probe('authority-boundary','allowed-and-excluded-effect-overlap-shape-accepted',lambda r:r['payload']['excluded_effect_kinds'].append(r['payload']['allowed_effect_kinds'][0]),True)
 probe('authority-boundary','arbitrary-effective-period-text-shape-accepted',lambda r:r['payload'].update(effective_period='unreviewed:Time'),True)
 cross=[];metadata=[]
 for semantic in ['authority-claim','authority-boundary']:
  schema=docs[semantic+'_schema'];enum=schema['properties']['relation_refs']['items']['properties'];legacy={(x['relation_kind_ref'],x['direction'],peer) for x in docs[semantic+'_descriptor']['relation_roles'] for peer in x['counterpart_kinds']};current={(x['relation_kind_ref'],x['direction'],peer) for x in side_roles if x['semantic_kind']==semantic for peer in x['counterpart_kinds']}
  for k,d,peer in itertools.product(enum['relation_kind_ref']['enum'],enum['direction']['enum'],enum['counterpart_kind']['enum']):
   r=copy.deepcopy(docs[semantic+'_fixture']);r['relation_refs'][0].update(relation_kind_ref=k,direction=d,counterpart_kind=peer);accepted=not list(b.c.Draft202012Validator(schema).iter_errors(r));ck('schema-independent-enums-'+semantic+'-'+k+'-'+d+'-'+peer,accepted);cross.append({'semantic_kind':semantic,'relation_kind_ref':k,'direction':d,'counterpart_kind':peer,'schema_accepted':accepted,'descriptor_declared':(k,d,peer) in legacy,'current_Kind_declared':(k,d,peer) in current,'record':r,'actual_relation_created':False})
  for k,d,peer in sorted(current):
   r=copy.deepcopy(docs[semantic+'_fixture']);r['relation_refs'][0].update(relation_kind_ref=k,direction=d,counterpart_kind=peer);es=list(b.c.Draft202012Validator(schema).iter_errors(r));metadata.append({'semantic_kind':semantic,'relation_kind_ref':k,'direction':d,'counterpart_kind':peer,'schema_accepted':not es,'errors':[x.message for x in es],'record':r,'actual_relation_created':False})
 tv=b.c.Draft202012Validator(docs['typed-relation_schema']);pair_tests=[]
 for id in sorted({x['relation_kind_ref'] for x in side_roles}):
  p=docs[id]['payload'];schema_pairs=relation_conditions(docs['typed-relation_schema'],id)
  for pair in [x for x in p['allowed_endpoint_pairs'] if any(x[k] in ['authority-claim','authority-boundary'] for k in x)]:
   r=copy.deepcopy(docs['typed-relation_fixture']);r['payload'].update(relation_kind_ref=id,source={'kind':pair['source_kind'],'ref':'Source:hyp','version_ref':'Source@hyp'},target={'kind':pair['target_kind'],'ref':'Target:hyp','version_ref':'Target@hyp'},qualifiers={x:'hyp:qualifier' for x in p['qualifier_contract']['required_axes']});es=list(tv.iter_errors(r));accepted=not es
   if accepted!=(pair in schema_pairs):raise ValueError('Side Kind/TR pair observation differs')
   pair_tests.append({'relation_kind_ref':id,'pair':pair,'schema_accepted':accepted,'errors':[x.message for x in es],'record':r,'actual_relation_or_authentication_or_grant_created':False})
 authority=docs['relation.scopes-authority-over']['payload'];schema_pairs=relation_conditions(docs['typed-relation_schema'],'relation.scopes-authority-over');gap={'current_Kind_pairs':len(authority['allowed_endpoint_pairs']),'current_TR_schema_pairs':len(schema_pairs),'missing_TR_pairs':[x for x in authority['allowed_endpoint_pairs'] if x not in schema_pairs],'alignment_reviewed':False};ck('exact-authority-Kind3-TR2-Boundary-to-DecisionScope-gap',gap=={'current_Kind_pairs':3,'current_TR_schema_pairs':2,'missing_TR_pairs':[{'source_kind':'authority-boundary','target_kind':'decision-scope'}],'alignment_reviewed':False})
 ck('scope-kind-forbids-permission-authentication-execution',authority['forbidden_inferences']==['permission-grant','claim-authentication','effect-execution']);ck('evidence-kind-forbids-claim-acceptance-decision-admission-truth',docs['relation.evidence-bears-on']['payload']['forbidden_inferences']==['claim-acceptance','decision','admission','truth']);ck('succession-forbids-automatic-supersession-equality-authority-transfer',docs['relation.successor-of']['payload']['forbidden_inferences']==['automatic-supersession','identity-equality','authority-transfer'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();history=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=json.loads((b.BASE/'definitions/cal.definition.responsibility/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-Authority-profile/v1-candidate','status':'PASS-for-explicit-hypothetical-context-governing-transfer-and-exact-side-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_history_frame_count':len(history),'rejected_history_frames':sum(x['expected_rejection'] for x in history),'finite_history_frames':history,'actual_check_count':len(checks),'actual_checks':checks,'actual_side_carrier_schema_probes':probes,'negative_fixture_checks':negatives,'actual_join_observations':joins,'current_Authority_carrier_selection':{'semantic_kind_rows':authority_rows,'direct_definition_binding_types':direct_bindings,'dedicated_Authority_carrier_established':False,'scope':'selected admitted-current Type registry only'},'Authority_endpoint_roles_from_all_current_Kinds':authority_endpoints,'current_side_carrier_roles':side_roles,'carrier_cross_product_observations':cross,'current_side_role_carrier_schema_observations':metadata,'current_Kind_TR_pair_observations':pair_tests,'authority_scope_schema_gap':gap,'source_mapping_gaps':{'source_precedence_tuple_valid_admissible_equivalence_reviewed':False,'actual_owner_right_counting_duty_purpose_surface_object_claim_basis_authenticated':False,'dedicated_Authority_carrier_mapping_reviewed':False,'cross_context_transfer_revocation_history_and_temporal_rules_reviewed':False,'side_carrier_relation_alignment_and_whole_source_conformance_established':False},'new_authorities_claims_or_relations_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Hypothetical nine-axis context/independent governing support/effectivity/revocation/transfer/history rules and exact related carriers. No dedicated current Authority carrier/endpoint; Claim and Boundary separate. Field/shape completeness not validity sufficiency, authenticated governing effect or permission. Current side metadata gaps and Boundary-to-DecisionScope Kind3/TR2 gap retained. No actual source fidelity, right/duty/authentication/admission/world effect or universal proof.'}
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh Authority profile differs')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({k:r[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

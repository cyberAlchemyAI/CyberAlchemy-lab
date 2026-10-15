"""Bounded explicit-edge/removal profile and selected legacy graph strengths/gaps."""
import copy,json,types
import build_candidate as b
import verifier as v
def text(x):return isinstance(x,str) and bool(x.strip())
def closed(x,keys):return isinstance(x,dict) and set(x)==set(keys)
PAIRS={'synthetic.coordination@1':('product','project'),'synthetic.same-kind@1':('product','product')}
def inspect(state):
 if not closed(state,['endpoints','edges','labels']) or not isinstance(state['endpoints'],dict) or not state['endpoints'] or not isinstance(state['edges'],list) or not isinstance(state['labels'],dict):return False
 for id,row in state['endpoints'].items():
  if not closed(row,['identity_id','identity_kind','authority','owner_ref']) or not text(id) or any(not text(x) for x in row.values()) or row['identity_id']!=id:return False
 seen=set()
 for edge in state['edges']:
  if not closed(edge,['edge_id','kind_ref','source_ref','target_ref','owner_ref','evidence_refs','lifecycle_ref']):return False
  if any(not text(edge[x]) for x in ['edge_id','kind_ref','source_ref','target_ref','owner_ref','lifecycle_ref']):return False
  if edge['edge_id'] in seen or edge['edge_id'] in state['endpoints'] or edge['kind_ref'] not in PAIRS or edge['source_ref'] not in state['endpoints'] or edge['target_ref'] not in state['endpoints']:return False
  seen.add(edge['edge_id']);pair=tuple(state['endpoints'][edge[x]]['identity_kind'] for x in ['source_ref','target_ref'])
  if pair!=PAIRS[edge['kind_ref']]:return False
  refs=edge['evidence_refs']
  if not isinstance(refs,list) or not refs or any(not text(x) for x in refs) or len(set(refs))!=len(refs):return False
 for label in state['labels'].values():
  if not closed(label,['value','generated','canonical_axis']) or not text(label['value']) or label['generated'] is not True or label['canonical_axis'] is not False:return False
 return True
def initial():
 return {'endpoints':{id:{'identity_id':id,'identity_kind':kind,'authority':authority,'owner_ref':'synthetic:shared-owner'} for id,kind,authority in [('a','product','synthetic:authority-a'),('z','project','synthetic:authority-z')]},'edges':[{'edge_id':'edge-r','kind_ref':'synthetic.coordination@1','source_ref':'a','target_ref':'z','owner_ref':'synthetic:edge-owner','evidence_refs':['synthetic:evidence@1'],'lifecycle_ref':'synthetic:lifecycle@1'}],'labels':{'reverse-display':{'value':'generated reverse description','generated':True,'canonical_axis':False}}}
def verify(write=False):
 context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.r.verify(b.snapshot(),b.ROOT)
 runtime=v.f.current_bindings();bindings=[b.ref(p) for p in [b.UNIT/'verify_relation_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'resolver.py']]
 controls=[]
 def add(name,change,expected):
  state=initial();change(state);actual=inspect(state)
  if actual!=expected:raise ValueError('Wrong bounded edge control: '+name)
  controls.append({'case_id':name,'state':state,'accepted_shape':actual,'actual_admission':False})
 add('explicit-directional-edge-independent-authorities',lambda x:None,True)
 for field in ['edge_id','kind_ref','source_ref','target_ref','owner_ref','evidence_refs','lifecycle_ref']:add('missing-'+field,lambda x,field=field:x['edges'][0].pop(field),False)
 add('empty-edge-evidence',lambda x:x['edges'][0].update(evidence_refs=[]),False)
 add('unversioned-kind-is-not-selected-contract',lambda x:x['edges'][0].update(kind_ref='coordination'),False)
 add('reverse-endpoint-pair-is-not-declared-direction',lambda x:x['edges'][0].update(source_ref='z',target_ref='a'),False)
 add('unresolved-endpoint-is-not-synthesized',lambda x:x['edges'][0].update(target_ref='unknown-subject'),False)
 add('edge-identity-cannot-be-endpoint-identity-in-selected-common-namespace',lambda x:x['edges'][0].update(edge_id='a'),False)
 add('bool-is-not-endpoint-ref',lambda x:x['edges'][0].update(source_ref=True),False)
 add('duplicate-edge-id',lambda x:x['edges'].append(copy.deepcopy(x['edges'][0])),False)
 add('implicit-authority-extra-field',lambda x:x['edges'][0].update(authority_grant='synthetic:grant'),False)
 add('shared-context-without-edge-is-permitted-not-an-inferred-edge',lambda x:x.update(edges=[]),True)
 add('same-endpoint-self-edge-when-selected-kind-pair-permits',lambda x:x['edges'][0].update(kind_ref='synthetic.same-kind@1',target_ref='a'),True)
 def second(x):edge=copy.deepcopy(x['edges'][0]);edge['edge_id']='edge-second';x['edges'].append(edge)
 add('different-edge-identities-same-pair-permitted',second,True)
 add('derived-label-not-canonical-axis',lambda x:x['labels']['reverse-display'].update(canonical_axis=True),False)
 traces=[]
 def trace(name,change,expected):
  before=initial();after=copy.deepcopy(before);change(after);preserved=inspect(after) and before['endpoints']==after['endpoints']
  if preserved!=expected:raise ValueError('Wrong removal/frame trace '+name)
  traces.append({'case_id':name,'states':[before,after],'endpoints_preserved':preserved,'expected':expected,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 trace('remove-edge-retains-both-endpoints',lambda x:x.update(edges=[]),True)
 trace('remove-derived-label-retains-edge-endpoints',lambda x:x.update(labels={}),True)
 trace('add-different-edge-identity-does-not-copy-authority',second,True)
 trace('generated-reverse-description-does-not-create-reverse-edge',lambda x:x['labels']['reverse-display'].update(value='another reverse description'),True)
 def erase(x):x['edges']=[];x['endpoints'].pop('z')
 trace('edge-removal-erases-endpoint-is-rejected',erase,False)
 trace('edge-action-transfers-authority-is-rejected',lambda x:x['endpoints']['z'].update(authority=x['endpoints']['a']['authority']),False)
 trace('endpoint-identity-collapse-is-rejected',lambda x:x['endpoints']['z'].update(identity_id='a'),False)
 trace('label-becomes-canonical-axis-is-rejected',lambda x:x['labels']['reverse-display'].update(canonical_axis=True),False)
 selected={};actual=[];hostiles=[];probes=[]
 def capture(name,path):
  ref=b.ref(b.ROOT/path);raw=b.r.read_bytes(b.ROOT,path)
  if b.r.digest(raw)!=ref['sha256']:raise ValueError('Capture race')
  selected[name]=ref;return raw
 def check(id,ok,detail=None):
  if not ok:raise ValueError('Selected actual graph check failed '+id)
  actual.append({'check_id':id,'result':True,'detail':detail})
 folder='authority/artifact-types/identity-graph/v1';artifact=b.r.parse(capture('artifact',folder+'/artifact.json'),'graph-type');schema=b.r.parse(capture('schema',folder+'/schema.json'),'graph-schema');b.c.Draft202012Validator.check_schema(schema)
 registry=b.r.parse(capture('registry','authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'),'type-registry');entry=next(x for x in registry['admitted_contracts'] if x['artifact_type_ref']==artifact['artifact_type_ref'])
 check('selected-exact-admitted-current-graph-contract',entry['artifact_sha256']==selected['artifact']['sha256'] and entry['schema_sha256']==selected['schema']['sha256']==artifact['schema_digest'] and registry['current_by_identity'][artifact['artifact_type_id']]==artifact['artifact_type_ref'] and entry['lifecycle_state']=='admitted-current',{'embedded_status':artifact['status'],'overlay_lifecycle':entry['lifecycle_state'],'decision_ref':entry['admission_decision_ref']})
 check('closed-graph-and-edge-shapes',schema.get('additionalProperties') is False and schema['$defs']['relation']['additionalProperties'] is False)
 definitions=b.r.parse(capture('definition_registry','authority/definitions/registry.json'),'definition-registry')
 for index,binding in enumerate(artifact['semantic_definition_bindings']):
  doc=b.r.parse(capture('meaning_'+str(index),binding['path']),'bound-meaning');version=doc['definition_id']+'@'+doc['version'];row=next(x for x in definitions['entries'] if x['definition_id']==doc['definition_id'] and x['version']==doc['version'])
  check('exact-current-admitted-meaning-'+str(index),version==binding['definition_ref'] and binding['sha256']==selected['meaning_'+str(index)]['sha256']==row['sha256'] and definitions['current_lookup'][doc['definition_id']]==version and row['lifecycle_state']=='admitted')
 check('IdentityRelation-and-IdentityCarrier-bindings',all(any(x['definition_ref']==id+'@1.0.0-candidate.1' for x in artifact['semantic_definition_bindings']) for id in ['cal.definition.identity-relation','cal.definition.identity-carrier']))
 modules={}
 for name,path in [('validator','tooling/validators/cml07_identity_artifact_type.py'),('generator','tooling/generators/cml07_identity_artifact.py')]:
  raw=capture(name,path);module=types.ModuleType('_bound_graph_'+name);module.__file__=str(b.ROOT/path);exec(compile(raw,str(b.ROOT/path),'exec'),module.__dict__);modules[name]=module
 check('bound-validator-generator-digests',artifact['validation_contract']['shared_validator_sha256']==selected['validator']['sha256'] and artifact['source_direction']['shared_generator_sha256']==selected['generator']['sha256'])
 fixture_path=folder+'/'+artifact['validation_contract']['positive_witness'];fixture=b.r.parse(capture('positive_fixture',fixture_path),'positive-graph');original=copy.deepcopy(fixture);validator=modules['validator'];generator=modules['generator']
 errors=list(b.c.Draft202012Validator(schema).iter_errors(fixture));sem=validator.semantic_errors('identity-graph',fixture)
 check('positive-fixture-schema-and-local-semantic-valid',not errors and not sem and fixture==original)
 check('five-explicit-unique-nodes-and-five-directional-edge-identities',len(fixture['nodes'])==len({x['identity_ref'] for x in fixture['nodes']})==5 and len(fixture['relations'])==len({x['relation_id'] for x in fixture['relations']})==5)
 projections=[]
 for name,render,expected_path in [('descriptor',lambda:generator.render_artifact(artifact),folder+'/ARTIFACT.md'),('fixture',lambda:generator.render_instance(artifact,fixture),folder+'/'+artifact['validation_contract']['positive_projection'])]:
  before_artifact=copy.deepcopy(artifact);before_fixture=copy.deepcopy(fixture);first=render().encode();second=render().encode();expected=capture(name+'_projection',expected_path)
  check(name+'-two-render-parity-and-unmodified-input',first==second==expected and artifact==before_artifact and fixture==before_fixture);projections.append({'name':name,'bytes':len(first),'sha256':b.r.digest(first)})
 for index,path in enumerate(artifact['validation_contract']['negative_witnesses']):
  raw=b.r.parse(capture('hostile_'+str(index),folder+'/'+path),'hostile-graph')
  if raw.get('fixture_kind')=='mutation-v1':capture('hostile_base_'+str(index),folder+'/'+raw['base_path'])
  hostile,mode=validator.materialize_hostile_fixture(b.ROOT/folder,raw);schema_errors=[x.message for x in b.c.Draft202012Validator(schema).iter_errors(hostile)];semantic_errors=validator.semantic_errors('identity-graph',hostile)
  rejected=bool(semantic_errors) if mode=='semantic' else bool(schema_errors) if mode=='schema' else bool(schema_errors or semantic_errors)
  check('actual-hostile-'+str(index)+'-rejected-at-declared-layer',rejected);hostiles.append({'path':folder+'/'+path,'mode':mode,'schema_errors':schema_errors,'semantic_errors':semantic_errors,'rejected':True})
 def probe(name,change,expect_schema,expect_semantic):
  data=copy.deepcopy(fixture);change(data);schema_ok=not list(b.c.Draft202012Validator(schema).iter_errors(data));sem_errors=validator.semantic_errors('identity-graph',data);semantic_ok=not sem_errors
  if (schema_ok,semantic_ok)!=(expect_schema,expect_semantic):raise ValueError('Actual checker boundary changed '+name)
  probes.append({'case_id':name,'schema_accepted':schema_ok,'local_semantics_accepted':semantic_ok,'data':data,'semantic_errors':sem_errors,'whole_source_conformance':False})
 probe('legacy-checker-accepts-edge-id-equal-to-endpoint-ref',lambda x:x['relations'][0].update(relation_id=x['relations'][0]['source_ref']),True,True)
 probe('legacy-same-kind-signature-permits-self-edge',lambda x:x['relations'][0].update(target_ref=x['relations'][0]['source_ref']),True,True)
 def reverse(x):edge=x['relations'][1];edge['source_ref'],edge['target_ref']=edge['target_ref'],edge['source_ref']
 probe('legacy-reverse-coordination-rejected-by-semantic-signature',reverse,True,False)
 probe('legacy-duplicate-edge-id-rejected-only-by-semantic-check',lambda x:x['relations'][1].update(relation_id=x['relations'][0]['relation_id']),True,False)
 probe('literal-per-edge-owner-field-not-in-closed-legacy-shape',lambda x:x['relations'][0].update(owner_ref=x['graph_owner_ref']),False,True)
 probe('one-edge-removal-keeps-five-node-records',lambda x:x['relations'].pop(),True,True)
 probe('last-edge-removal-hits-graph-minimum-not-endpoint-erasure',lambda x:x.update(relations=[]),False,True)
 gaps={'literal_edge_fields':schema['$defs']['relation']['required'],'per_edge_generic_fields_absent':['owner_ref','evidence_refs','lifecycle'],'graph_aggregate_owner_field':'graph_owner_ref','graph_aggregate_evidence_field':'evidence_refs','mapping_reviewed':False,'edge_endpoint_identity_collision_rejected_by_legacy_checker':False,'minimum_graph_edges':schema['properties']['relations']['minItems'],'canonical_axis_or_live_authority_embedding':'pending'}
 b.unchanged(list(selected.values())+context['sources']+bindings);b.r.verify(b.snapshot(),b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-identity-relation-profile/v1-candidate','authority_effect':'none','status':'PASS-for-bounded-edges-removal-and-selected-legacy-checker-boundaries','checker_bindings':bindings,'runtime_bindings':runtime,'selected_inputs':selected,'profile_controls':controls,'profile_control_count':len(controls),'rejected_profile_controls':sum(not x['accepted_shape'] for x in controls),'finite_frame_traces':traces,'finite_frame_trace_count':len(traces),'rejected_frame_traces':sum(not x['endpoints_preserved'] for x in traces),'actual_checks':actual,'actual_check_count':len(actual),'actual_hostile_fixtures':hostiles,'actual_hostile_fixture_count':len(hostiles),'actual_boundary_probes':probes,'actual_boundary_probe_count':len(probes),'selected_graph_contracts':1,'projections':projections,'source_carrier_mapping_gaps':gaps,'source_profile_embedding_reviewed':False,'unbounded_preservation_proof':False,'actual_admission_created':False,'new_relations_created':0,'actual_runtime_activated':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Synthetic explicit-edge/frame controls and exact legacy schema/local-semantic/projection evidence, including retained acceptance gaps. No current modern Kind mapping, actual edge/admission/grant, principal authentication, per-edge metadata embedding, unbounded preservation, legacy-checker repair or jointly aligned whole theory.'}
 if write:b.put('relation-profile-checks.json',report)
 elif not b.r.same_json(report,json.loads((b.UNIT/'relation-profile-checks.json').read_bytes())):raise ValueError('Fresh relation profile differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({k:x[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_frame_trace_count','rejected_frame_traces','actual_check_count','actual_hostile_fixture_count','actual_boundary_probe_count','selected_graph_contracts','source_profile_embedding_reviewed','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

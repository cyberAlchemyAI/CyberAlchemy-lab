"""Hypothetical edge qualification and source-authority frames with actual schema/captured pure-function observations."""
import ast,copy,hashlib,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['edge','ontology','source_node','target_node','represented_source_version','represented_target_version','global_relation_version','relation_digest','local_scope','source_epoch','registry_epoch']
SUPPORT=['independent_identity','exact_node_resolution','subject_endpoint_map','exclusive_mode','global_digest_authentication','closed_relation_kind_qualifiers','explicit_local_scope','local_signature','separate_source_authority','scope_use']
def profiles():
 context={n:'hyp:'+n for n in AXES};base={'context':context,'query':dict(context),'supports':{n:True for n in SUPPORT},'is_global_source':False,'overrides_global_relation':False,'second_writable_authority':False,'local_is_global':False,'infers_authority':False,'infers_admission':False,'actual_claim':False,'edge_current':True,'bindings_current':True};rows=[]
 def add(id,change,reject=False,use=True):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['context']!=x['query']:errors.append('exact-edge-context-mismatch')
  if not all(x['supports'].values()):errors.append('missing-qualified-support')
  if any(x[n] for n in ['is_global_source','overrides_global_relation','second_writable_authority','local_is_global','infers_authority','infers_admission','actual_claim']):errors.append('unverified-role-or-outcome')
  allowed=not errors and x['edge_current'] and x['bindings_current'];assert bool(errors)==reject and allowed==use,(id,errors)
  rows.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':use,'actual_runtime_execution':False,'actual_endpoint_version_digest_local_scope_or_authority_verified':False,'source_fidelity_accepted':False,'use_allowed_under_hypotheses':allowed})
 add('qualified-projection-or-explicit-local-edge-under-separate-authority',lambda x:None)
 for n in AXES:add('mismatched-'+n,lambda x,n=n:x['query'].update({n:'hyp:other'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 for n in ['is_global_source','overrides_global_relation','second_writable_authority','local_is_global','infers_authority','infers_admission','actual_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True,False)
 add('stale-edge-no-reuse',lambda x:x.update(edge_current=False),False,False);add('changed-bindings-no-reuse',lambda x:x.update(bindings_current=False),False,False)
 return rows

def frames():
 source={'id':'hyp:relation','source':'hyp:s1','target':'hyp:s2','kind':'hyp:kind','digest':'hyp:d','meaning':'hyp:meaning'};base={'source_before':source,'source_after':copy.deepcopy(source),'edge':{'mode':'global-projection','relation_ref':'hyp:relation','relation_digest':'hyp:d','local_scope':None,'label':'hyp:display'},'edge_writes_source':False,'second_writable_authority':False,'local_is_global':False,'actual_claim':False};rows=[]
 def add(id,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['source_before']!=x['source_after']:errors.append('projection-overrides-source-record')
  if x['edge']['mode']=='global-projection' and (x['edge']['relation_ref']!=x['source_before']['id'] or x['edge']['relation_digest']!=x['source_before']['digest']):errors.append('projected-binding-mismatch')
  if x['edge']['mode']=='local-interpretation' and (x['edge']['local_scope'] is None or x['edge']['relation_ref'] is not None):errors.append('local-scope-or-source-role-mismatch')
  if x['edge_writes_source'] or x['second_writable_authority'] or x['local_is_global']:errors.append('forbidden-source-authority-or-local-collapse')
  if x['actual_claim']:errors.append('actual-behavior-proof-unverified')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'universal_source_write_confinement_proof':False,'actual_runtime_execution':False})
 add('projected-edge-retains-global-source',lambda x:None)
 add('independent-edge-display-update',lambda x:x['edge'].update(label='hyp:new-display'))
 for n in ['id','source','target','kind','digest','meaning']:add('projection-changes-source-'+n,lambda x,n=n:x['source_after'].update({n:'hyp:changed'}),True)
 for n in ['relation_ref','relation_digest']:add('projection-binding-changes-'+n,lambda x,n=n:x['edge'].update({n:'hyp:other'}),True)
 add('explicit-local-edge-separate-from-global-source',lambda x:x['edge'].update(mode='local-interpretation',relation_ref=None,relation_digest=None,local_scope='hyp:o'))
 add('local-edge-without-scope',lambda x:x['edge'].update(mode='local-interpretation',relation_ref=None,relation_digest=None),True)
 add('local-edge-retains-global-source-binding',lambda x:x['edge'].update(mode='local-interpretation',local_scope='hyp:o'),True)
 for n in ['edge_writes_source','second_writable_authority','local_is_global','actual_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 return rows

def extracted(raw,path,names,namespace):
 tree=ast.parse(raw,filename=str(path));selected=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in names]
 if {x.name for x in selected}!=set(names):raise ValueError('Missing selected pure functions')
 exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace);return namespace

def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert [x['artifact_type_ref'] for x in direct]==['cal.artifact-type.ontology-edge/v1'];row=direct[0];pkg=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((pkg/'artifact.json').read_bytes());ep=b.ROOT/'authority/admissions/first-governed-agent-work-episode/v1/instances';rkp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json';rkr=json.loads(rkp.read_bytes());rkrow=next(x for x in rkr['entries'] if x['relation_kind_id']=='relation.member-of' and x['lifecycle_state']=='admitted-current')
 paths={'registry':rp,'descriptor':pkg/'artifact.json','schema':b.ROOT/row['schema_path'],'fixture':pkg/'fixtures/valid/record.json','artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/'fixtures/valid/RECORD.md','generator':b.ROOT/artifact['source_direction']['generator_path'],'wrapper':pkg/'validate.py','validator':b.ROOT/'authority/ontology-integration/candidates/0002-carrier-materialization/validate.py','root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','native_runtime':b.ROOT/'ontology-lifecycle/runtime/src/lib.rs','domainspec_relation':b.ROOT/'ontology-lifecycle/domainspec/specs/ontology-lifecycle/nodes/ontology-relation-semantic-state.json','domainspec_integrity':b.ROOT/'ontology-lifecycle/domainspec/specs/ontology-lifecycle/nodes/relation-endpoint-integrity.json','project_session':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/session.py','project_graph':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/graph.py','project_operations':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/operations.py','project_sources':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/sources.py','project_common':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/common.py','episode_edge':ep/'artifacts/ontology-edge.json','episode_relation':ep/'typed-relations/state-project.json','episode_source_node':ep/'artifacts/ontology-node-state.json','episode_target_node':ep/'artifacts/ontology-node-project.json','relation_kind_registry':rkp,'relation_kind':b.ROOT/rkrow['instance_path']}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-edge-binding',len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]) and binding[0]['admission_decision_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION')
 ck('current-registry-records-C70-type-admission',row['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and row['lifecycle_state']=='admitted-current')
 ck('retained-descriptor-and-fixture-candidate-posture',artifact['status']=='candidate-unadmitted' and fixture['record_state']=='candidate' and artifact['authority_effect']==fixture['authority_effect']=='none')
 ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256']);ck('root-descriptor-binding',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 renderer=extracted(raw['generator'],paths['generator'],['render_record'],{'json':json})['render_record'];before=copy.deepcopy(fixture);ck('two-pure-fixture-renders-exact',renderer(fixture).encode()==renderer(fixture).encode()==raw['fixture_projection']);ck('render-input-preserved',fixture==before)
 expected='\n'.join(['<!-- GENERATED FILE: canonical data is artifact.json. -->','',f"# {artifact['name']}/v1",'',artifact['distinct_validation_purpose'],'','## Claim ceiling','',artifact['claim_ceiling'],'']).encode();ck('generator-artifact-template-projection-exact',expected==raw['artifact_projection'] and 'item["distinct_validation_purpose"]' in raw['generator'].decode())
 payload=schema['properties']['payload'];ck('closed-top-payload-event-and-mode-objects',schema['additionalProperties'] is payload['additionalProperties'] is payload['properties']['semantic_event_ref']['additionalProperties'] is False and all(x['then']['properties']['payload']['properties'][n]['additionalProperties'] is False for x,n in zip(schema['allOf'],['global_typed_relation_binding','local_interpretation'])))
 ck('qualifier-object-without-specific-closed-properties',payload['properties']['closed_qualifiers']=={'type':'object'})
 ck('two-mode-conditional-shapes-inspected',[x['if']['properties']['payload']['properties']['edge_mode']['const'] for x in schema['allOf']]==['global-projection','local-interpretation'])
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('four-hostiles-rejected',len(hostiles)==4 and all(x['schema_rejected'] for x in hostiles))
 tree=ast.parse(raw['validator']);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='validate_package');code=ast.get_source_segment(raw['validator'].decode(),fn);ck('generic-validator-not-edge-reference-hash-resolution',all(n not in code for n in ['global_typed_relation_binding','typed_relation_digest','source_node_ref','target_node_ref','local_interpretation']) and 'dump(package/' in code)
 native=raw['native_runtime'].decode();relstruct=native.split('pub struct OntologyRelationSemanticState {',1)[1].split('\n}',1)[0];endpointfn=native.split('fn validate_relation_endpoints(',1)[1].split('fn validate_projected_relation_endpoints(',1)[0]
 ck('native-relation-fields-without-explicit-mode-binding-inspected','pub source_node_id: String' in relstruct and 'pub target_node_id: String' in relstruct and 'pub direction: RelationDirection' in relstruct and all(x not in relstruct for x in ['edge_mode','global_typed_relation_binding','local_interpretation']))
 ck('native-active-same-ontology-endpoint-integrity-inspected','Lifecycle::Active' in endpointfn and 'identity.ontology_id.as_str()' in endpointfn and 'RELATION_ENDPOINT_INTEGRITY' in endpointfn)
 ck('DomainSpec-complete-state-and-active-endpoint-intent-inspected',docs['domainspec_integrity']['intent']=='Require both endpoints of every active relation to be active node subjects in the same ontology cut.' and 'canonical serialization' in docs['domainspec_relation']['body']['equality'])
 graphtree=ast.parse(raw['project_graph']);graphfn=next(x for x in graphtree.body if isinstance(x,ast.FunctionDef) and x.name=='build');graphcode=ast.get_source_segment(raw['project_graph'].decode(),graphfn)
 ck('Project-global-effective-admission-and-relation-validator-inspected','entry["effective_state"] in ("admitted-current", "local-admitted-current")' in graphcode and 'validate_relation(entry["record"], projection)' in graphcode and 'global-typed-relation-projection' in graphcode and 'excluded_from_confirmed_paths' in graphcode)
 ck('Project-local-signatures-and-endpoint-kinds-inspected','local_edge_signatures' in graphcode and 'undeclared ontology-local endpoint signature' in graphcode and 'undeclared ontology-local edge predicate' in graphcode)
 sessiontree=ast.parse(raw['project_session']);cls=next(x for x in sessiontree.body if isinstance(x,ast.ClassDef) and x.name=='Session');method=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='_build');session=ast.get_source_segment(raw['project_session'].decode(),method)
 ck('Project-session-global-versus-local-copy-fields-inspected',all(x in session for x in ['edge_mode="global-projection", local_interpretation=None','edge_mode="local-interpretation", global_typed_relation_binding=None','entry["source"]["sha256"]','local_scope": config["scope_ref"]']))
 episode=docs['episode_edge'];rel=docs['episode_relation'];nsrc=docs['episode_source_node'];ntgt=docs['episode_target_node'];eb=episode['payload'];rb=rel['payload'];versions={side:{'relation_endpoint':rb[side]['version_ref'],'node_represented_subject':node['payload']['represented_subject']['version_ref'],'equal':rb[side]['version_ref']==node['payload']['represented_subject']['version_ref']} for side,node in [('source',nsrc),('target',ntgt)]}
 ck('captured-episode-edge-schema-valid',not list(validator.iter_errors(episode)))
 ck('captured-episode-edge-digest-exact-selected-relation-bytes',eb['global_typed_relation_binding']['typed_relation_digest']==refs['episode_relation']['sha256']=='70be6198f3866c330db68a09a8e90e675e18ae16a86067b6e0c0d5daf83c0378' and eb['global_typed_relation_binding']['typed_relation_ref']==rel['node_id'])
 ck('captured-episode-edge-node-refs-and-represented-identities',eb['source_node_ref']==nsrc['node_id'] and eb['target_node_ref']==ntgt['node_id'] and all(rb[side]['ref']==node['payload']['represented_subject']['ref'] for side,node in [('source',nsrc),('target',ntgt)]))
 ck('captured-source-version-match-and-target-version-gap-observed',versions['source']['equal'] is True and versions['target']['equal'] is False)
 ck('captured-edge-kind-and-qualifiers-match-relation',eb['relation_type_ref']==rb['relation_kind_ref'] and eb['closed_qualifiers']==rb['qualifiers'])
 ck('current-member-of-Relation-Kind-exact-bytes',rkrow['instance_sha256']==refs['relation_kind']['sha256'] and rkrow['admission_decision_ref']=='CAL-DECISION-0074C-GOVERNANCE-RELATION-SURFACE-ADMISSION')
 derr=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(b.co.source_document(snap,source)));shape={'current_schema_accepted':not derr,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in derr],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-Definition-v1-current-v2-four-errors',{x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 probes=[]
 def local(x):x['payload'].update(edge_mode='local-interpretation',global_typed_relation_binding=None,local_interpretation={'interpretation':'hyp:represents','local_scope':'hyp:o','owner_ref':'hyp:owner','evidence_refs':['hyp:evidence']})
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in validator.iter_errors(x)];assert (not errors)==accept,(id,errors);probes.append({'case_id':id,'record':x,'schema_accepted':not errors,'expected_schema_acceptance':accept,'errors':errors,'actual_endpoint_version_digest_local_scope_qualifier_or_authority_verified':False})
 probe('unresolved-ontology-and-endpoint-refs-accepted',lambda x:x['payload'].update(ontology_ref='absent:o',source_node_ref='absent:n1',target_node_ref='absent:n2'),True)
 probe('unresolved-global-relation-and-version-accepted',lambda x:x['payload']['global_typed_relation_binding'].update(typed_relation_ref='absent:r',typed_relation_version_ref='absent:v'),True)
 probe('wrong-plausible-global-and-event-digests-accepted',lambda x:(x['payload']['global_typed_relation_binding'].update(typed_relation_digest='0'*64),x['payload']['semantic_event_ref'].update(semantic_event_digest='0'*64)),True)
 probe('same-node-endpoints-accepted',lambda x:x['payload'].update(target_node_ref=x['payload']['source_node_ref']),True)
 probe('symmetric-direction-without-Relation-Kind-check-accepted',lambda x:x['payload'].update(direction='symmetric'),True)
 probe('arbitrary-qualifier-keys-and-nested-values-accepted',lambda x:x['payload'].update(closed_qualifiers={'grants_all_authority':True,'nested':{'unreviewed':[1,2]}}),True)
 probe('empty-qualifier-object-accepted',lambda x:x['payload'].update(closed_qualifiers={}),True)
 probe('weak-collapse-label-accepted',lambda x:x['payload'].update(forbidden_collapse=['anything']),True)
 probe('same-edge-id-changed-global-binding-accepted',lambda x:x['payload']['global_typed_relation_binding'].update(typed_relation_ref='other:r',typed_relation_digest='f'*64),True)
 probe('explicit-local-interpretation-shape-accepted',local,True)
 probe('local-scope-differs-from-ontology-and-top-scope-accepted',lambda x:(local(x),x['payload']['local_interpretation'].update(local_scope='other:scope')),True)
 probe('local-owner-differs-from-top-owner-accepted',lambda x:(local(x),x['payload']['local_interpretation'].update(owner_ref='other:owner')),True)
 probe('local-unresolved-evidence-and-meaning-accepted',lambda x:(local(x),x['payload']['local_interpretation'].update(interpretation='unreviewed:meaning',evidence_refs=['absent:evidence'])),True)
 probe('whitespace-local-and-global-refs-accepted',lambda x:(local(x),x['payload']['local_interpretation'].update(interpretation=' ',local_scope=' ',owner_ref=' ',evidence_refs=[' '])),True)
 for state in ['retired','removed']:probe('nonactive-edge-lifecycle-'+state+'-accepted',lambda x,state=state:x['payload'].update(lifecycle=state),True)
 probe('admitted-record-state-with-no-effect-accepted',lambda x:x.update(record_state='admitted'),True)
 probe('permission-sounding-claim-accepted',lambda x:x.update(claim_ceiling='This edge writes the global relation and authorizes all effects.'),True)
 probe('huge-positive-semantic-cursor-accepted',lambda x:x['payload']['semantic_event_ref'].update(semantic_cursor=10**100),True)
 probe('global-projection-null-binding-rejected',lambda x:x['payload'].update(global_typed_relation_binding=None),False)
 probe('global-projection-local-object-rejected',lambda x:x['payload'].update(local_interpretation={'interpretation':'x','local_scope':'o','owner_ref':'p','evidence_refs':['e']}),False)
 probe('local-interpretation-global-binding-rejected',lambda x:x['payload'].update(edge_mode='local-interpretation',local_interpretation={'interpretation':'x','local_scope':'o','owner_ref':'p','evidence_refs':['e']}),False)
 probe('local-interpretation-null-object-rejected',lambda x:x['payload'].update(edge_mode='local-interpretation',global_typed_relation_binding=None),False)
 for n in ['ontology_ref','edge_mode','relation_type_ref','source_node_ref','target_node_ref','direction','closed_qualifiers','global_typed_relation_binding','local_interpretation','lifecycle','forbidden_collapse','semantic_event_ref','replay_source']:probe('missing-'+n+'-rejected',lambda x,n=n:x['payload'].pop(n),False)
 for n in ['interpretation','local_scope','owner_ref','evidence_refs']:probe('missing-local-'+n+'-rejected',lambda x,n=n:(local(x),x['payload']['local_interpretation'].pop(n)),False)
 probe('empty-local-evidence-rejected',lambda x:(local(x),x['payload']['local_interpretation'].update(evidence_refs=[])),False)
 probe('extra-local-authority-field-rejected',lambda x:(local(x),x['payload']['local_interpretation'].update(authority=True)),False)
 probe('extra-global-authority-field-rejected',lambda x:x['payload']['global_typed_relation_binding'].update(authority=True),False)
 probe('empty-collapse-list-rejected',lambda x:x['payload'].update(forbidden_collapse=[]),False)
 probe('qualifier-array-rejected',lambda x:x['payload'].update(closed_qualifiers=[]),False)
 probe('invalid-edge-mode-rejected',lambda x:x['payload'].update(edge_mode='global-source'),False)
 probe('invalid-direction-rejected',lambda x:x['payload'].update(direction='undirected'),False)
 probe('short-relation-digest-rejected',lambda x:x['payload']['global_typed_relation_binding'].update(typed_relation_digest='a'),False)
 probe('replay-source-true-rejected',lambda x:x['payload'].update(replay_source=True),False)
 probe('authority-effect-admitted-rejected',lambda x:x.update(authority_effect='admitted'),False)
 # Execute exact existing pure validators only on explicit captured/authored in-memory frames.
 ns=extracted(raw['project_common'],paths['project_common'],['RuntimeFault','require'],{});extracted(raw['project_sources'],paths['project_sources'],['resolve'],ns);extracted(raw['project_operations'],paths['project_operations'],['protocol_check','validate_relation'],ns)
 subjects={node['payload']['represented_subject']['version_ref']:{'identity':node['payload']['represented_subject']['ref'],'version_ref':node['payload']['represented_subject']['version_ref'],'kind':node['payload']['represented_subject']['kind'],'effective_state':node['record_state']} for node in [nsrc,ntgt]}
 projection={'subjects':subjects,'relation_contracts':{'relation.member-of':docs['relation_kind']}};pure=[]
 def repaired(x):x['record']['payload']['target']['version_ref']=ntgt['payload']['represented_subject']['version_ref']
 def subject(x,side):return x['projection']['subjects'][x['record']['payload'][side]['version_ref']]
 def purecase(id,change,accept):
  x={'record':copy.deepcopy(rel),'projection':copy.deepcopy(projection)};change(x);before=copy.deepcopy(x);error=None
  try:ns['validate_relation'](x['record'],x['projection'])
  except ns['RuntimeFault'] as err:error=str(err)
  assert (error is None)==accept and x==before,(id,error)
  pure.append({'case_id':id,'frame':x,'pure_checker_accepted':error is None,'expected_acceptance':accept,'error':error,'input_preserved':True,'actual_runtime_execution':False,'actual_global_admission_or_whole_edge_fidelity_verified':False})
 purecase('captured-Node-version-frame-exposes-unresolved-target-version',lambda x:None,False)
 purecase('authored-target-version-alignment-with-candidate-endpoints-accepted',repaired,True)
 purecase('unknown-Relation-Kind-rejected',lambda x:(repaired(x),x['record']['payload'].update(relation_kind_ref='absent:kind')),False)
 purecase('unknown-target-version-rejected',lambda x:x['record']['payload']['target'].update(version_ref='absent:v'),False)
 purecase('endpoint-identity-mismatch-rejected',lambda x:(repaired(x),x['record']['payload']['target'].update(ref='other:id')),False)
 purecase('exact-endpoint-pair-mismatch-rejected',lambda x:(repaired(x),x['record']['payload']['target'].update(kind='ontology-node')),False)
 purecase('withdrawn-target-rejected',lambda x:(repaired(x),subject(x,'target').update(effective_state='withdrawn')),False)
 purecase('local-withdrawn-source-rejected',lambda x:(repaired(x),subject(x,'source').update(effective_state='local-withdrawn')),False)
 purecase('required-membership-qualifier-missing-rejected',lambda x:(repaired(x),x['record']['payload'].update(qualifiers={})),False)
 purecase('extra-global-qualifier-rejected',lambda x:(repaired(x),x['record']['payload']['qualifiers'].update(authority=True)),False)
 purecase('wrong-qualifier-type-rejected',lambda x:(repaired(x),x['record']['payload']['qualifiers'].update(membership_role=1)),False)
 purecase('historical-endpoint-direct-version-key-not-rejected',lambda x:(repaired(x),subject(x,'target').update(effective_state='historical')),True)
 purecase('unrecognized-endpoint-status-direct-key-not-rejected',lambda x:(repaired(x),subject(x,'target').update(effective_state='unrecognized')),True)
 purecase('source-version-label-under-direct-key-not-crosschecked',lambda x:(repaired(x),subject(x,'source').update(version_ref='other:version')),True)
 purecase('top-record-authority-effect-not-checked-by-relation-function',lambda x:(repaired(x),x['record'].update(authority_effect='admitted')),True)
 purecase('candidate-Relation-Kind-lifecycle-not-checked-by-this-function',lambda x:(repaired(x),x['projection']['relation_contracts']['relation.member-of'].update(lifecycle_state='candidate')),True)
 ck('pure-captured-frame-version-gap-and-authored-alignment-observed',pure[0]['pure_checker_accepted'] is False and pure[1]['pure_checker_accepted'] is True and all(x['input_preserved'] for x in pure))
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-OntologyEdge-profile/v1-candidate','status':'PASS-for-qualified-edge-hypotheses-and-selected-carrier-native-project-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'exact_definition_binding':binding[0],'current_registry_selection':row,'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'descriptor_version':artifact['version'],'fixture_status':fixture['record_state'],'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_edge_frames':frames(),'project_pure_relation_controls':pure,'captured_episode_endpoint_versions':versions,'captured_episode_relation_digest_verified':True,'captured_episode_complete_endpoint_version_map_accepted':False,'normalized_captured_Node_version_frame_is_runtime_projection':False,'native_relation_struct_source':relstruct,'native_runtime_source_inspected':True,'native_runtime_executed':False,'project_graph_session_source_inspected':True,'project_graph_session_executed':False,'existing_pure_relation_function_executed_on_in_memory_frames':True,'bound_package_validator_executed':False,'bound_package_validator_static_source_inspected':True,'generator_module_or_materialization_writer_executed':False,'historical_source_current_definition_shape':shape,'generic_native_project_common_edge_map_accepted':False,'actual_global_connection_or_source_authority_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Actual carrier mode/schema/pure projection checks;captured episode edge digest and endpoint version gap;pure relation validator on captured/authored Node-version frames;static native/DomainSpec/Project code. No actual global admission,write authority,live graph/session,closed local denotation,accepted common map,source-owner fidelity or joint closure.'}
 b.unchanged(list(refs.values())+context['sources']+report['checker_bindings']+report['input_refs']);assert runtime==v.f.current_bindings()
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh edge observations differ')
 return report

def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'frames':len(x['finite_edge_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_edge_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(z['schema_accepted'] for z in x['schema_probes']),'catalog_checks':x['actual_check_count'],'pure_relation_controls':len(x['project_pure_relation_controls']),'pure_relation_acceptances':sum(z['pure_checker_accepted'] for z in x['project_pure_relation_controls'])},indent=2))
if __name__=='__main__':main()

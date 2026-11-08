"""View hypotheses with exact schema/captured builder digests and isolated Session method frames."""
import ast,copy,hashlib,json,time
from datetime import datetime,timezone
from typing import Any
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['view','ontology','cut','semantic_cursor','governance_cursor','event_set_digest','selection_contract','consumer','exclusions','freshness','expiry','claim_ceiling','source_epoch','authority_envelope']
SUPPORT=['cut_consistency','coordinate_resolution','event_digest_authentication','selected_item_resolution','selection_contract','immutable_record','equivalent_recomputation','clock_expiry_contract','consumer_scope','canonical_identity_preservation','authority_separation']
FORBIDDEN=['canonical_replay','canonical_subject','canonical_relation','governance_Decision','authority_grant','authorizes_Action','widens_Assignment','widens_Policy','widens_Delegation','actual_claim']
def profiles():
 ctx={n:'hyp:'+n for n in AXES};base={'context':ctx,'query':dict(ctx),'supports':{n:True for n in SUPPORT},**{n:False for n in FORBIDDEN},'view_current':True,'bindings_current':True};rows=[]
 def add(id,change,reject=False,use=True):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['context']!=x['query']:errors.append('exact-cut-selection-consumer-clock-context-mismatch')
  if not all(x['supports'].values()):errors.append('missing-hypothetical-support')
  if any(x[n] for n in FORBIDDEN):errors.append('forbidden-canonical-or-authority-role')
  allowed=not errors and x['view_current'] and x['bindings_current'];assert bool(errors)==reject and allowed==use,(id,errors)
  rows.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':use,'use_allowed_under_hypotheses':allowed,'actual_runtime_execution':False,'actual_cut_selection_expiry_or_authority_verified':False,'source_fidelity_accepted':False})
 add('qualified-immutable-exact-cut-view-under-hypotheses',lambda x:None)
 for n in AXES:add('mismatched-'+n,lambda x,n=n:x['query'].update({n:'hyp:other'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 for n in FORBIDDEN:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True,False)
 add('stale-view-no-current-use',lambda x:x.update(view_current=False),False,False);add('changed-binding-no-reuse',lambda x:x.update(bindings_current=False),False,False)
 return rows

def frames():
 source={'ontology':'hyp:o','semantic_cursor':'hyp:sc','governance_cursor':'hyp:gc','event_set_digest':'hyp:es','canonical_identity':'hyp:s','authority':'hyp:source-envelope'};view={'cut':'hyp:cut','selector':'hyp:sel','consumer':'hyp:c','content':'hyp:content','expiry':'hyp:e'};base={'source_before':source,'source_after':copy.deepcopy(source),'view_before':view,'view_after':copy.deepcopy(view),'recomputed':dict(view),'consumer_before':{'Assignment':'hyp:a','Policy':'hyp:p','Delegation':'hyp:d'},'consumer_after':{'Assignment':'hyp:a','Policy':'hyp:p','Delegation':'hyp:d'},'expired':False,'stale':False,'requires_current':True,'view_usable':True,'authorizes_Action':False,'canonical_replay':False,'actual_claim':False};rows=[]
 def add(id,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['source_before']!=x['source_after']:errors.append('View-changes-source-cut-or-identity-authority')
  if x['view_before']!=x['view_after']:errors.append('retained-immutable-View-mutated')
  if x['recomputed']['cut']==x['view_before']['cut'] and x['recomputed']['selector']==x['view_before']['selector'] and x['recomputed']['content']!=x['view_before']['content']:errors.append('same-cut-contract-non-equivalent-content')
  if x['consumer_before']!=x['consumer_after']:errors.append('View-widens-consumer-envelope')
  if x['requires_current'] and (x['expired'] or x['stale']) and x['view_usable']:errors.append('expired-or-stale-current-state-use')
  if x['authorizes_Action'] or x['canonical_replay'] or x['actual_claim']:errors.append('unverified-canonical-authority-or-actual-role')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'universal_recomputation_clock_write_or_authority_proof':False,'actual_runtime_execution':False})
 add('same-cut-contract-equivalent-View-retains-source-envelope',lambda x:None)
 add('expired-current-use-rejected-under-hypothesis',lambda x:x.update(expired=True,view_usable=False))
 add('stale-current-use-rejected-under-hypothesis',lambda x:x.update(stale=True,view_usable=False))
 add('expired-noncurrent-use-allowed-under-separate-hypothesis',lambda x:x.update(expired=True,requires_current=False))
 add('new-cut-or-selection-may-change-content',lambda x:x['recomputed'].update(cut='hyp:new-cut',content='hyp:new-content'))
 for n in source:add('View-changes-source-'+n,lambda x,n=n:x['source_after'].update({n:'hyp:new'}),True)
 for n in view:add('mutates-retained-View-'+n,lambda x,n=n:x['view_after'].update({n:'hyp:new'}),True)
 add('same-cut-contract-non-equivalent-content',lambda x:x['recomputed'].update(content='hyp:new'),True)
 for n in ['Assignment','Policy','Delegation']:add('View-widens-'+n,lambda x,n=n:x['consumer_after'].update({n:'hyp:new'}),True)
 add('expired-current-state-use',lambda x:x.update(expired=True),True);add('stale-current-state-use',lambda x:x.update(stale=True),True)
 for n in ['authorizes_Action','canonical_replay','actual_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 return rows

def extracted(raw,path,names,namespace):
 tree=ast.parse(raw,filename=str(path));selected=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in names];assert {x.name for x in selected}==set(names)
 exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace);return namespace

def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert [x['artifact_type_ref'] for x in direct]==['cal.artifact-type.ontology-view/v1'];row=direct[0];pkg=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((pkg/'artifact.json').read_bytes());ep=b.ROOT/'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts'
 paths={'registry':rp,'descriptor':pkg/'artifact.json','schema':b.ROOT/row['schema_path'],'fixture':pkg/'fixtures/valid/record.json','artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/'fixtures/valid/RECORD.md','generator':b.ROOT/artifact['source_direction']['generator_path'],'wrapper':pkg/'validate.py','validator':b.ROOT/'authority/ontology-integration/candidates/0002-carrier-materialization/validate.py','root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','generic_cut':b.ROOT/'authority/artifact-types/ontology-cut/v1/fixtures/valid/record.json','native_runtime':b.ROOT/'ontology-lifecycle/runtime/src/lib.rs','domainspec_selector':b.ROOT/'ontology-lifecycle/domainspec/specs/ontology-lifecycle/nodes/context-selector.json','domainspec_projection':b.ROOT/'ontology-lifecycle/domainspec/specs/ontology-lifecycle/nodes/context-projection.json','project_session':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/session.py','project_graph':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/graph.py','project_common':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/common.py','episode_builder':b.ROOT/'authority/agent-work-episodes/candidates/0001-first-governed-agent-context/build.py','episode_view':ep/'ontology-view.json','episode_cut':ep/'ontology-cut.json','episode_state_node':ep/'ontology-node-state.json','episode_project_node':ep/'ontology-node-project.json','episode_edge':ep/'ontology-edge.json','episode_consumer':ep/'agent-session.json','episode_semantic_history':ep/'project-semantic-event-history.json','episode_governance_history':ep/'project-governance-event-history.json'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-View-binding',len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]) and binding[0]['admission_decision_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION')
 ck('current-registry-records-C70-type-admission',row['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and row['lifecycle_state']=='admitted-current')
 ck('retained-descriptor-and-fixture-candidate-posture',artifact['status']=='candidate-unadmitted' and fixture['record_state']=='candidate' and artifact['authority_effect']==fixture['authority_effect']=='none')
 ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256'])
 ck('root-descriptor-binding',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 renderer=extracted(raw['generator'],paths['generator'],['render_record'],{'json':json})['render_record'];before=copy.deepcopy(fixture);ck('two-pure-fixture-renders-exact',renderer(fixture).encode()==renderer(fixture).encode()==raw['fixture_projection']);ck('render-input-preserved',fixture==before)
 expected='\n'.join(['<!-- GENERATED FILE: canonical data is artifact.json. -->','',f"# {artifact['name']}/v1",'',artifact['distinct_validation_purpose'],'','## Claim ceiling','',artifact['claim_ceiling'],'']).encode();ck('generator-artifact-template-projection-exact',expected==raw['artifact_projection'] and 'item["distinct_validation_purpose"]' in raw['generator'].decode())
 payload=schema['properties']['payload'];pp=payload['properties'];ck('closed-top-and-payload',schema['additionalProperties'] is payload['additionalProperties'] is False)
 ck('fifteen-required-payload-fields',len(payload['required'])==15 and set(payload['required'])==set(pp));ck('semantic-coordinate-without-governance-cursor','semantic_cursor' in pp and 'governance_cursor' not in pp)
 ck('date-fields-without-format-or-order-contract',all(pp[n]=={'type':'string','minLength':1} for n in ['freshness_at','expires_at']))
 ck('empty-selection-exclusions-permitted-and-replay-false',all('minItems' not in pp[n] for n in ['selected_node_refs','selected_edge_refs','exclusions']) and pp['replay_source']=={'const':False})
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('four-hostiles-rejected',len(hostiles)==4 and all(x['schema_rejected'] for x in hostiles))
 tree=ast.parse(raw['validator']);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='validate_package');code=ast.get_source_segment(raw['validator'].decode(),fn);ck('package-validator-not-View-cut-time-selection-resolution',all(n not in code for n in ['cut_digest','expires_at','selected_node_refs','source_event_set_digest']) and 'dump(package/' in code)
 native=raw['native_runtime'].decode();selector=native.split('pub struct ContextSelector {',1)[1].split('\n}',1)[0];projection=native.split('pub struct ContextProjection {',1)[1].split('\n}',1)[0];projectfn=native.split('pub fn context_projection(',1)[1].split('\n    pub fn ',1)[0]
 ck('native-selector-exact-semantic-cursor-required-subjects-policy-profile',all(n in selector for n in ['semantic_cursor: u64','required_subject_set: Vec<OntologySubjectIdentity>','governance_join_policy: GovernanceJoinPolicy','intended_use: String','projection_profile: ProjectionProfile']))
 ck('native-projection-lacks-generic-consumer-expiry-governance-cursor',all(n in projection for n in ['source_event_set_digest: String','selected_node_ids: Vec<String>','selected_relation_ids: Vec<String>','forbidden_authority_moves: Vec<String>']) and all(n not in projection for n in ['consumer_ref','expires_at','governance_cursor','cut_digest']))
 ck('native-required-set-active-subject-exact-governance-checks-inspected',all(n in projectfn for n in ['CONTEXT_REQUIRED_SET_EMPTY','CONTEXT_REQUIRED_SUBJECT_DUPLICATE','REQUIRED_SUBJECT_NOT_ACTIVE','EXACT_GOVERNANCE_STATE_MISSING','exact_reference_matches','digest_value(&references)']))
 ck('native-explicit-forbidden-authority-moves-inspected',all(n in projectfn for n in ['admission-from-projection','acceptance-from-projection','publication-from-projection']))
 ck('DomainSpec-bounded-noncanonical-source-traceable-projection',all(n in docs['domainspec_selector']['intent'] for n in ['exact semantic cursor','intended use','closed projection profile']) and 'non-canonical context slice' in docs['domainspec_projection']['intent'])
 cls=next(x for x in ast.parse(raw['project_session']).body if isinstance(x,ast.ClassDef) and x.name=='Session');methods={x.name:ast.get_source_segment(raw['project_session'].decode(),x) for x in cls.body if isinstance(x,ast.FunctionDef)};build=methods['_build'];ck('Project-whole-history-and-record-body-digest-schemes-inspected','event_set_digest = digest(p["histories"])' in build and 'cut_digest = digest({"nodes": node_records, "edges": edge_records})' in build)
 ck('Project-view-consumer-ttl-selected-query-and-exclusions-inspected',all(n in build for n in ['consumer_ref=self.session_id','freshness_at=started, expires_at=expires','selected_node_refs=ontology["node_refs"]','selected_edge_refs=ontology["relation_refs"]','Sources outside the query envelope']))
 ck('Project-context-clock-HEAD-and-close-separation-inspected',all(n in methods['context'] for n in ['self.clock() >= self.deadline','self.close()','self.store.replay(require_current=True)','transaction_digest','copy.deepcopy(self.pack)']) and all(n in methods['close'] for n in ['self.memory.clear()','self.pack = None','self.closed = True']))
 graph=raw['project_graph'].decode();ck('Project-stale-query-suppresses-confirmed-edges-inspected','stale-source-envelope' in graph and 'graph["edges"] = []' in graph and 'outside selected source envelope' in graph)
 sourceDigest=extracted(raw['episode_builder'],paths['episode_builder'],['digest'],{'json':json,'hashlib':hashlib,'Any':Any})['digest'];common=extracted(raw['project_common'],paths['project_common'],['RuntimeFault','require','digest'],{'json':json,'hashlib':hashlib});projectDigest=common['digest'];ev=docs['episode_view'];cut=docs['episode_cut'];consumer=docs['episode_consumer'];vp=ev['payload'];cp=cut['payload'];sem=docs['episode_semantic_history'];gov=docs['episode_governance_history'];nodes=[docs['episode_state_node'],docs['episode_project_node']];edge=docs['episode_edge'];eventInput={'semantic_chain':sem['payload']['chain_digest'],'governance_chain':gov['payload']['chain_digest']};eventDigest=sourceDigest(eventInput);body={'ontology_ref':vp['ontology_ref'],'semantic_cursor':vp['semantic_cursor'],'source_event_set_digest':eventDigest,'nodes':[{'ref':x['node_id'],'sha256':refs[n]['sha256']} for x,n in zip(nodes,['episode_state_node','episode_project_node'])],'edges':[{'ref':edge['node_id'],'sha256':refs['episode_edge']['sha256']}]};bodyDigest=sourceDigest(body)
 ck('captured-View-schema-valid-and-cut-field-binding',not list(validator.iter_errors(ev)) and vp['ontology_ref']==cp['ontology_ref'] and vp['cut_ref']==cut['node_id'] and vp['semantic_cursor']==cp['semantic_cursor'] and vp['cut_digest']==cp['calculated_digest'] and vp['source_event_set_digest']==cp['source_event_set_digest'])
 ck('captured-selection-and-consumer-exact-IDs',vp['selected_node_refs']==cp['node_refs']==[x['node_id'] for x in nodes] and vp['selected_edge_refs']==cp['edge_refs']==[edge['node_id']] and vp['consumer_ref']==consumer['node_id'] and consumer['payload']['ontology_view_ref']==ev['node_id'])
 ck('captured-builder-chain-event-set-and-ref-hash-body-recomputed',eventDigest==vp['source_event_set_digest'] and bodyDigest==vp['cut_digest'] and 'projection_set = {"ontology_ref": ONTOLOGY' in raw['episode_builder'].decode())
 projectEventDigest=projectDigest({'project-semantic-event-history':sem,'project-governance-event-history':gov});projectBodyDigest=projectDigest({'nodes':nodes,'edges':[edge]});ck('captured-native-Project-digest-schemes-not-conflated',projectEventDigest!=eventDigest and projectBodyDigest!=bodyDigest and refs['episode_cut']['sha256']!=bodyDigest)
 asof=datetime.fromisoformat(context['as_of_utc'].replace('Z','+00:00'));times=[]
 for id,record in [('generic',fixture),('captured',ev)]:
  p=record['payload'];fresh=datetime.fromisoformat(p['freshness_at'].replace('Z','+00:00'));expiry=datetime.fromisoformat(p['expires_at'].replace('Z','+00:00'));times.append({'case_id':id,'freshness_at':p['freshness_at'],'expires_at':p['expires_at'],'as_of_utc':context['as_of_utc'],'freshness_before_expiry':fresh<expiry,'expired_at_pinned_instant':asof>=expiry,'actual_live_consumer_rejection_verified':False})
 ck('generic-and-captured-fixtures-expired-at-pinned-analysis-instant',all(x['freshness_before_expiry'] and x['expired_at_pinned_instant'] for x in times));ck('captured-selector-label-not-contract-proof',vp['selector_ref']=='ontology-selector:first-agent-episode-empty' and len(vp['selected_node_refs'])==2 and len(vp['selected_edge_refs'])==1)
 derr=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(b.co.source_document(snap,source)));shape={'current_schema_accepted':not derr,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in derr],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-Definition-v1-current-v2-four-errors',{x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in validator.iter_errors(x)];assert (not errors)==accept,(id,errors);probes.append({'case_id':id,'record':x,'schema_accepted':not errors,'expected_schema_acceptance':accept,'errors':errors,'actual_cut_digest_selection_expiry_or_authority_verified':False})
 for n in ['selected_node_refs','selected_edge_refs','exclusions']:probe('empty-'+n+'-accepted',lambda x,n=n:x['payload'].update({n:[]}),True)
 for n in ['ontology_ref','cut_ref','selector_ref','consumer_ref','governance_join_policy_ref']:probe('unresolved-'+n+'-accepted',lambda x,n=n:x['payload'].update({n:'absent:ref'}),True)
 for n in ['cut_digest','source_event_set_digest']:probe('wrong-plausible-'+n+'-accepted',lambda x,n=n:x['payload'].update({n:'0'*64}),True)
 probe('invalid-date-text-accepted',lambda x:x['payload'].update(freshness_at='not-a-date',expires_at='also-not-a-date'),True)
 probe('expiry-before-freshness-accepted',lambda x:x['payload'].update(freshness_at='2030-01-01',expires_at='2000-01-01'),True)
 probe('unresolved-selected-items-accepted',lambda x:x['payload'].update(selected_node_refs=['absent:n'],selected_edge_refs=['absent:e']),True)
 probe('same-ID-different-cut-selection-consumer-accepted',lambda x:x['payload'].update(cut_ref='other:cut',selector_ref='other:selector',consumer_ref='other:consumer'),True)
 probe('View-ID-equals-cut-ref-accepted',lambda x:x.update(node_id=x['payload']['cut_ref']),True)
 probe('huge-semantic-cursor-accepted',lambda x:x['payload'].update(semantic_cursor=10**100),True)
 probe('whitespace-selection-ref-accepted',lambda x:x['payload'].update(selector_ref=' '),True)
 probe('admitted-state-with-effect-none-accepted',lambda x:x.update(record_state='admitted'),True)
 probe('permission-sounding-intended-use-accepted',lambda x:x['payload'].update(intended_use='Authorize every Action and widen the consumer Delegation.'),True)
 for n in payload['required']:probe('missing-'+n+'-rejected',lambda x,n=n:x['payload'].pop(n),False)
 for n in ['selected_node_refs','selected_edge_refs','exclusions']:
  probe('duplicate-'+n+'-rejected',lambda x,n=n:x['payload'].update({n:['hyp:x','hyp:x']}),False)
  probe('wrong-type-'+n+'-rejected',lambda x,n=n:x['payload'].update({n:'hyp:x'}),False)
  probe('empty-item-'+n+'-rejected',lambda x,n=n:x['payload'].update({n:['']}),False)
 for n in ['cut_digest','source_event_set_digest']:probe('malformed-'+n+'-rejected',lambda x,n=n:x['payload'].update({n:'G'*64}),False)
 probe('zero-semantic-cursor-rejected',lambda x:x['payload'].update(semantic_cursor=0),False)
 probe('governance-cursor-extra-field-rejected',lambda x:x['payload'].update(governance_cursor=1),False)
 probe('replay-source-true-rejected',lambda x:x['payload'].update(replay_source=True),False)
 probe('authority-effect-inflation-rejected',lambda x:x.update(authority_effect='admitted'),False)
 probe('expiry-enforcement-extra-field-rejected',lambda x:x['payload'].update(expiry_enforced=True),False)
 stubbed=extracted(raw['project_session'],paths['project_session'],['Session'],{'copy':copy,'time':time,'require':common['require']})['Session'];methodCases=[]
 class ReplayStub:
  def __init__(self,head,failed):self.head=head;self.failed=failed;self.calls=[]
  def replay(self,require_current=False):
   self.calls.append({'require_current':require_current});common['require'](not self.failed,'declared replay stub source drift');return {'head':{'transaction_digest':self.head}}
 def methodcase(id,now=1,closed=False,head='hyp:head',failed=False,operation='context',accept=True,erased=False,mutate_return=False):
  obj=object.__new__(stubbed);obj.clock=lambda:now;obj.deadline=10;obj.closed=closed;obj.head='hyp:head';obj.session_id='hyp:session';obj.instance_id='hyp:instance';obj.memory=['hyp:memory'];obj.pack={'content':['hyp:immutable']};obj.store=ReplayStub(head,failed);before=copy.deepcopy(obj.pack);error=None;result=None
  try:result=getattr(obj,operation)();ok=True
  except common['RuntimeFault'] as e:ok=False;error=str(e)
  if mutate_return and ok:result['content'].append('hyp:changed-return')
  assert ok==accept and (obj.pack is None and obj.memory==[] and obj.closed)==erased,(id,error)
  if mutate_return:assert obj.pack==before
  methodCases.append({'case_id':id,'arguments':{'clock_now':now,'deadline':10,'closed':closed,'stub_head':head,'stub_failed':failed,'operation':operation,'return_mutated':mutate_return},'method_accepted':ok,'expected_acceptance':accept,'error':error,'result':result,'after':{'pack':obj.pack,'memory':obj.memory,'closed':obj.closed,'replay_calls':obj.store.calls},'memory_and_pack_erased':erased,'actual_store_replay_executed':False,'actual_Session_constructed_or_live_runtime_executed':False,'actual_view_projection_or_authority_verified':False})
 methodcase('before-deadline-same-HEAD-read',accept=True);methodcase('returned-copy-isolation',mutate_return=True)
 methodcase('closed-context-rejected',closed=True,accept=False);methodcase('exact-deadline-rejects-and-erases',now=10,accept=False,erased=True);methodcase('after-deadline-rejects-and-erases',now=11,accept=False,erased=True)
 methodcase('changed-HEAD-rejected-retains-memory-until-close',head='hyp:changed',accept=False);methodcase('declared-replay-staleness-rejected-retains-memory',failed=True,accept=False);methodcase('explicit-close-erases',operation='close',erased=True)
 pureInputs=copy.deepcopy(body);pureBefore=copy.deepcopy(pureInputs);render1=sourceDigest(pureInputs);render2=sourceDigest(pureInputs);ck('two-pure-captured-body-recomputations-identical-and-preserved',render1==render2==bodyDigest and pureInputs==pureBefore)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-OntologyView-profile/v1-candidate','status':'PASS-for-qualified-View-hypotheses-and-selected-carrier-captured-digests-isolated-method-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'exact_definition_binding':binding[0],'current_registry_selection':row,'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'fixture_status':fixture['record_state'],'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_view_frames':frames(),'captured_digest_observations':{'chain_digest_input':eventInput,'projection_set':body,'recomputed_event_set_digest':eventDigest,'recomputed_cut_digest':bodyDigest,'two_recomputations':{'first':render1,'second':render2,'input_preserved':pureInputs==pureBefore},'captured_cut_record_byte_sha256':refs['episode_cut']['sha256'],'current_Project_whole_history_digest':projectEventDigest,'current_Project_node_edge_record_digest':projectBodyDigest,'common_digest_contract_accepted':False},'pinned_expiry_observations':times,'isolated_Session_method_controls':methodCases,'native_runtime_executed':False,'live_Project_Session_or_store_executed':False,'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'selected_pure_render_and_digest_functions_executed':True,'selected_Session_methods_executed_only_on_stub_frames':True,'generic_native_Project_common_View_map_accepted':False,'actual_source_write_action_authority_or_consumer_widening_created':False,'new_authorities_or_relations_created':0,'historical_source_current_definition_shape':shape,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Actual schema/catalog/pure projections,captured builder-specific digests and pinned expiry observations,isolated existing Session.context/close behavior with declared read-only replay stub,static native/DomainSpec/Project code. No universal cut/selection/hash/clock/recompute/immutability/authority enforcement,live session/store,accepted common maps,source-owner fidelity or joint closure.'}
 b.unchanged(list(refs.values())+context['sources']+report['checker_bindings']+report['input_refs']);assert runtime==v.f.current_bindings()
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh View observations differ')
 return report

def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'frames':len(x['finite_view_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_view_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(z['schema_accepted'] for z in x['schema_probes']),'catalog_checks':x['actual_check_count'],'isolated_method_controls':len(x['isolated_Session_method_controls']),'method_acceptances':sum(z['method_accepted'] for z in x['isolated_Session_method_controls'])},indent=2))
if __name__=='__main__':main()

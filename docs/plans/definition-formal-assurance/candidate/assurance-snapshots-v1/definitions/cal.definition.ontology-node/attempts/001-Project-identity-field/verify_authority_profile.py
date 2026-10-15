"""Qualified Node hypotheses and exact schema/subject/history/pure-function/static observations."""
import ast,copy,hashlib,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['node','ontology','manifest','subject','revision','subject_digest','Definition_version','source_epoch','semantic_event_tuple','governance_epoch','confidence_scheme','branch_profile','challenge_route','facet_contract']
SUPPORT=['independent_identity','exact_revision_resolution','digest_authentication','manifest_closure','provenance_authentication','confidence_calibration','lifecycle_contract','branch_contract','contestability_contract','semantic_governance_join','scope_use','separate_subject_truth_authority']
FORBIDDEN=['node_is_subject','node_is_identity_carrier','node_is_Definition','is_replay_source','node_writes_subject','global_truth_proof','infers_authority','infers_admission','actual_claim']
def profiles():
 ctx={n:'hyp:'+n for n in AXES};base={'context':ctx,'query':dict(ctx),'supports':{n:True for n in SUPPORT},**{n:False for n in FORBIDDEN},'node_current':True,'bindings_current':True};rows=[]
 def add(id,change,reject=False,use=True):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['context']!=x['query']:errors.append('exact-Node-revision-context-mismatch')
  if not all(x['supports'].values()):errors.append('missing-hypothetical-support')
  if any(x[n] for n in FORBIDDEN):errors.append('forbidden-collapse-truth-or-authority-role')
  allowed=not errors and x['node_current'] and x['bindings_current'];assert bool(errors)==reject and allowed==use,(id,errors)
  rows.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':use,'use_allowed_under_hypotheses':allowed,'actual_runtime_execution':False,'actual_revision_facet_truth_or_authority_verified':False,'source_fidelity_accepted':False})
 add('qualified-independent-exact-revision-under-hypotheses',lambda x:None)
 for n in AXES:add('mismatched-'+n,lambda x,n=n:x['query'].update({n:'hyp:other'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 for n in FORBIDDEN:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True,False)
 add('stale-node-no-reuse',lambda x:x.update(node_current=False),False,False);add('changed-binding-no-reuse',lambda x:x.update(bindings_current=False),False,False)
 return rows

def frames():
 source={'subject':'hyp:s','version':'hyp:v','bytes':'hyp:source','digest':'hyp:d'};node={'identity':'hyp:n','ontology':'hyp:o','subject':'hyp:s','version':'hyp:v','digest':'hyp:d','provenance':'hyp:p','confidence':'hyp:c'};base={'source_before':source,'source_after':copy.deepcopy(source),'node_before':node,'node_after':copy.deepcopy(node),'successor':dict(node),'identity_carrier':'hyp:ic','Definition':'hyp:def','exact_revision_support_hypothesis':True,**{n:False for n in FORBIDDEN}};rows=[]
 def add(id,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['source_before']!=x['source_after']:errors.append('representation-modifies-source')
  if x['node_before']!=x['node_after']:errors.append('retained-immutable-Node-mutated')
  if x['successor']['identity'] in [x['successor']['subject'],x['identity_carrier'],x['Definition']]:errors.append('Node-identity-collapse')
  changed=any(x['successor'][n]!=x['node_before'][n] for n in ['subject','version','digest','provenance','confidence'])
  if changed and x['successor']['identity']==x['node_before']['identity']:errors.append('changed-representation-reuses-immutable-record-identity')
  if not x['exact_revision_support_hypothesis']:errors.append('unqualified-revision-binding')
  if any(x[n] for n in FORBIDDEN):errors.append('forbidden-collapse-truth-authority-or-replay')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'universal_temporal_source_write_or_truth_proof':False,'actual_runtime_execution':False,'immutable_revision_rule_is_primary_T_axiom':False})
 add('retained-Node-with-unchanged-source',lambda x:None)
 add('new-Node-for-same-revision-in-another-ontology',lambda x:x['successor'].update(identity='hyp:new',ontology='hyp:o2'))
 for n in ['version','digest','provenance','confidence']:add('new-Node-for-hypothetically-supported-'+n,lambda x,n=n:x['successor'].update(identity='hyp:new',**{n:'hyp:new'}))
 for n in source:add('Node-changes-source-'+n,lambda x,n=n:x['source_after'].update({n:'hyp:new'}),True)
 for n in ['identity','subject','version','digest','confidence']:add('mutates-retained-Node-'+n,lambda x,n=n:x['node_after'].update({n:'hyp:new'}),True)
 for n in ['version','digest','provenance','confidence']:add('same-Node-identity-changes-'+n,lambda x,n=n:x['successor'].update({n:'hyp:new'}),True)
 for n in ['subject','identity_carrier','Definition']:add('Node-equals-'+n,lambda x,n=n:x['successor'].update(identity=x['successor']['subject'] if n=='subject' else x[n]),True)
 add('missing-hypothetical-revision-support',lambda x:x.update(exact_revision_support_hypothesis=False),True)
 for n in FORBIDDEN:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 return rows

def extracted(raw,path,names,namespace):
 tree=ast.parse(raw,filename=str(path));selected=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in names];assert {x.name for x in selected}==set(names)
 exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace);return namespace

def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert [x['artifact_type_ref'] for x in direct]==['cal.artifact-type.ontology-node/v2'];row=direct[0];pkg=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((pkg/'artifact.json').read_bytes());ep=b.ROOT/'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts'
 paths={'registry':rp,'descriptor':pkg/'artifact.json','schema':b.ROOT/row['schema_path'],'fixture':pkg/'fixtures/valid/record.json','artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/'fixtures/valid/RECORD.md','generator':b.ROOT/artifact['source_direction']['generator_path'],'wrapper':pkg/'validate.py','validator':b.ROOT/'authority/ontology-integration/candidates/0002-carrier-materialization/validate.py','root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','predecessor_descriptor':b.ROOT/artifact['candidate_predecessor_contract']['path'],'represented_type_descriptor':b.ROOT/'authority/artifact-types/definition/v2/artifact.json','manifest_fixture':b.ROOT/'authority/artifact-types/ontology-manifest/v1/fixtures/valid/record.json','native_runtime':b.ROOT/'ontology-lifecycle/runtime/src/lib.rs','domainspec_node':b.ROOT/'ontology-lifecycle/domainspec/specs/ontology-lifecycle/nodes/ontology-node-semantic-state.json','domainspec_governance':b.ROOT/'ontology-lifecycle/domainspec/specs/ontology-lifecycle/nodes/ontology-governance-state.json','project_session':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/session.py','project_sources':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/sources.py','project_common':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/common.py','episode_state_node':ep/'ontology-node-state.json','episode_project_node':ep/'ontology-node-project.json','episode_state_subject':ep/'project-state.json','episode_project_subject':b.ROOT/'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/project.json','episode_semantic_history':ep/'project-semantic-event-history.json','episode_governance_history':ep/'project-governance-event-history.json'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-Node-binding',len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]) and binding[0]['admission_decision_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION')
 ck('current-registry-records-C70-v2-type-admission',row['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and row['lifecycle_state']=='admitted-current')
 ck('retained-descriptor-and-fixture-candidate-posture',artifact['status']=='candidate-unadmitted' and fixture['record_state']=='candidate' and artifact['authority_effect']==fixture['authority_effect']=='none')
 ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256'])
 ck('root-descriptor-binding',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'])
 ck('preserved-v1-predecessor-exact',artifact['candidate_predecessor_contract']['sha256']==refs['predecessor_descriptor']['sha256'] and artifact['candidate_predecessor_contract']['admission_posture']=='candidate-unadmitted-superseded-before-admission')
 ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 renderer=extracted(raw['generator'],paths['generator'],['render_record'],{'json':json})['render_record'];before=copy.deepcopy(fixture);ck('two-pure-fixture-renders-exact',renderer(fixture).encode()==renderer(fixture).encode()==raw['fixture_projection']);ck('render-input-preserved',fixture==before)
 expected='\n'.join(['<!-- GENERATED FILE: canonical data is artifact.json. -->','',f"# {artifact['name']}/v2",'',artifact['distinct_validation_purpose'],'','## Claim ceiling','',artifact['claim_ceiling'],'']).encode();ck('generator-artifact-template-projection-exact',expected==raw['artifact_projection'] and 'item["distinct_validation_purpose"]' in raw['generator'].decode())
 payload=schema['properties']['payload'];pp=payload['properties'];sem=pp['semantic_state'];gov=pp['governance_binding'];rs=pp['represented_subject']
 ck('closed-top-payload-subject-semantic-governance-event',all(x['additionalProperties'] is False for x in [schema,payload,rs,sem,gov,gov['properties']['semantic_event_ref']]))
 ck('ten-required-payload-fields',len(payload['required'])==10 and set(payload['required'])==set(pp))
 ck('nonempty-provenance-but-empty-Definition-governance-lists-permitted',pp['provenance_refs']['minItems']==1 and 'minItems' not in sem['properties']['semantic_definition_refs'] and 'minItems' not in gov['properties']['governance_event_refs'])
 ck('open-typed-properties-and-nonreplay-constant',sem['properties']['typed_properties']=={'type':'object'} and pp['replay_source']=={'const':False})
 ck('separate-confidence-fields-and-effect-none',{'evidence_confidence_ref','commitment_confidence_ref'}<=set(gov['required']) and gov['properties']['authority_effect']=={'const':'none'})
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('four-hostiles-rejected',len(hostiles)==4 and all(x['schema_rejected'] for x in hostiles))
 tree=ast.parse(raw['validator']);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='validate_package');code=ast.get_source_segment(raw['validator'].decode(),fn)
 ck('generic-package-validator-does-not-resolve-Node-subject-or-events',all(n not in code for n in ['represented_subject','semantic_event_ref','ontology_manifest_ref','governance_event_refs']) and 'dump(package/' in code)
 native=raw['native_runtime'].decode();node_struct=native.split('pub struct OntologyNodeSemanticState {',1)[1].split('\n}',1)[0];gov_struct=native.split('pub struct OntologyGovernanceState {',1)[1].split('\n}',1)[0];view=native.split('pub struct GovernedOntologyNodeView {',1)[1].split('\n}',1)[0];nodeval=native.split('fn validate_semantic_state(',1)[1].split('fn validate_typed_properties(',1)[0];propval=native.split('fn validate_typed_properties(',1)[1].split('\nfn ',1)[0];join=native.split('fn exact_reference_matches(',1)[1].split('\nfn ',1)[0]
 ck('native-Node-semantic-fields-without-generic-subject-branch-manifest',all(n in node_struct for n in ['identity: OntologySubjectIdentity','lifecycle: Lifecycle','definition_or_claim: String','semantic_definition_refs: Vec<DefinitionReference>']) and all(n not in node_struct for n in ['represented_subject','ontology_manifest_ref','branch','evidence_confidence']))
 ck('native-governance-facet-separate-provenance-confidence-challenge',all(n in gov_struct for n in ['provenance: Vec<ProvenanceEntry>','evidence_confidence: ConfidenceReference','commitment_confidence: ConfidenceReference','challenge_contract: ChallengeContract','semantic_ref: ExactSemanticEventReference']))
 ck('native-governed-view-joins-two-facets-and-exact-tuple',all(n in view for n in ['semantic_state: OntologyNodeSemanticState','governance_state: OntologyGovernanceState','semantic_event_id: String','semantic_event_digest: String','semantic_cursor: u64']))
 ck('native-nonempty-Definition-refs-and-restricted-profile-properties',all(n in nodeval for n in ['SEMANTIC_DEFINITION_REFS_EMPTY','test-empty-profile/v1']) and 'test-empty-profile/v1' in propval and '!properties.values.is_empty()' in propval)
 ck('native-event-join-compares-exact-three-fields',all(n in join for n in ['reference.semantic_event_id == event.event_id','reference.semantic_event_digest == event.event_digest','reference.semantic_cursor == event.semantic_cursor']))
 ck('DomainSpec-semantic-governance-separation-intent',docs['domainspec_node']['intent']=='Carry the complete meaning-bearing state of one ontology node after one canonical semantic event, excluding every governance field.' and 'one exact semantic event' in docs['domainspec_governance']['intent'])
 sessiontree=ast.parse(raw['project_session']);cls=next(x for x in sessiontree.body if isinstance(x,ast.ClassDef) and x.name=='Session');method=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='_build');session=ast.get_source_segment(raw['project_session'].decode(),method)
 ck('Project-session-node-digest-source-or-derived-fallback-inspected','digest(view)' in session and 'source_digest and len(source_digest) == 64' in session and 'semantic_definition_refs=[]' in session)
 ck('Project-session-shared-tuple-and-runtime-head-inspected','ontology_manifest_ref="runtime-head:" + self.head' in session and 'semantic_event_ref=tuple_ref' in session and 'confidence:not-evaluated' in session)
 fp=fixture['payload'];subject_gap={'fixture_subject':fp['represented_subject'],'selected_descriptor_ref':refs['represented_type_descriptor'],'selected_descriptor_identity':docs['represented_type_descriptor']['artifact_type_ref'],'selected_descriptor_version':docs['represented_type_descriptor']['version'],'digest_matches':fp['represented_subject']['digest']==refs['represented_type_descriptor']['sha256'],'fixture_manifest_ref':fp['ontology_manifest_ref'],'selected_manifest_id':docs['manifest_fixture']['node_id'],'version_alias_map_accepted':False,'whole_subject_revision_map_accepted':False}
 ck('generic-subject-identity-version-but-placeholder-byte-digest',fp['represented_subject']['ref']==docs['represented_type_descriptor']['artifact_type_ref'] and fp['represented_subject']['version_ref']==docs['represented_type_descriptor']['artifact_type_ref']+'@'+docs['represented_type_descriptor']['version'] and subject_gap['digest_matches'] is False)
 ck('generic-Manifest-version-suffix-map-unresolved',subject_gap['fixture_manifest_ref']==subject_gap['selected_manifest_id']+'/v1')
 histories={'project-semantic-event-history':docs['episode_semantic_history'],'project-governance-event-history':docs['episode_governance_history']};episode=[]
 for stem in ['state','project']:
  n=docs['episode_'+stem+'_node'];s=docs['episode_'+stem+'_subject'];np=n['payload'];r=np['represented_subject'];tuple_ref=np['governance_binding']['semantic_event_ref'];event=histories['project-semantic-event-history']['payload']['events'][tuple_ref['semantic_cursor']-1];gov_event=next(x for x in histories['project-governance-event-history']['payload']['events'] if x['event_id'] in np['governance_binding']['governance_event_refs'])
  obs={'node_ref':refs['episode_'+stem+'_node'],'subject_ref':refs['episode_'+stem+'_subject'],'schema_valid':not list(validator.iter_errors(n)),'subject_identity_matches':r['ref']==s['node_id'],'subject_digest_matches':r['digest']==refs['episode_'+stem+'_subject']['sha256'],'semantic_tuple_matches_selected_event':tuple_ref=={'semantic_event_id':event['event_id'],'semantic_event_digest':event['event_digest'],'semantic_cursor':event['cursor']},'governance_tuple_matches':gov_event['semantic_event_ref']==tuple_ref,'represented_subject_ref':r['ref'],'represented_subject_version':r['version_ref'],'represented_subject_version_map_accepted':False,'semantic_tuple':tuple_ref,'semantic_resulting_state_ref':event['resulting_state_ref'],'represented_subject_is_project_event_resulting_state':r['ref']==event['resulting_state_ref'],'empty_semantic_Definition_refs':np['semantic_state']['semantic_definition_refs']==[]}
  episode.append(obs)
 ck('two-captured-Nodes-schema-valid-exact-subject-bytes-and-event-tuples',all(all(x[n] for n in ['schema_valid','subject_identity_matches','subject_digest_matches','semantic_tuple_matches_selected_event','governance_tuple_matches']) for x in episode))
 ck('different-captured-subjects-share-one-Project-event',episode[0]['represented_subject_ref']!=episode[1]['represented_subject_ref'] and episode[0]['semantic_tuple']==episode[1]['semantic_tuple'] and episode[0]['represented_subject_is_project_event_resulting_state'] is True and episode[1]['represented_subject_is_project_event_resulting_state'] is False)
 ck('captured-Nodes-empty-Definition-list-contrasts-native-rule',all(x['empty_semantic_Definition_refs'] for x in episode))
 derr=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(b.co.source_document(snap,source)));shape={'current_schema_accepted':not derr,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in derr],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-Definition-v1-current-v2-four-errors',{x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in validator.iter_errors(x)];assert (not errors)==accept,(id,errors);probes.append({'case_id':id,'record':x,'schema_accepted':not errors,'expected_schema_acceptance':accept,'errors':errors,'actual_revision_facet_truth_or_authority_verified':False})
 probe('Node-id-equals-subject-ref-accepted',lambda x:x.update(node_id=x['payload']['represented_subject']['ref']),True)
 for n in ['ontology_ref','ontology_manifest_ref','node_type_ref','profile_ref']:probe('unresolved-'+n+'-accepted',lambda x,n=n:x['payload'].update({n:'absent:ref'}),True)
 for n in ['kind','ref','version_ref']:probe('unresolved-subject-'+n+'-accepted',lambda x,n=n:x['payload']['represented_subject'].update({n:'absent:wrong-kind'}),True)
 probe('wrong-plausible-subject-and-semantic-digests-accepted',lambda x:(x['payload']['represented_subject'].update(digest='0'*64),x['payload']['governance_binding']['semantic_event_ref'].update(semantic_event_digest='0'*64)),True)
 probe('same-ID-changed-subject-revision-accepted',lambda x:x['payload']['represented_subject'].update(version_ref='other:version',digest='f'*64),True)
 probe('empty-semantic-Definition-refs-accepted',lambda x:x['payload']['semantic_state'].update(semantic_definition_refs=[]),True)
 probe('empty-governance-events-accepted',lambda x:x['payload']['governance_binding'].update(governance_event_refs=[]),True)
 probe('unresolved-provenance-accepted',lambda x:x['payload'].update(provenance_refs=['absent:source']),True)
 probe('whitespace-subject-version-accepted',lambda x:x['payload']['represented_subject'].update(version_ref=' '),True)
 probe('arbitrary-nested-authority-typed-property-accepted',lambda x:x['payload']['semantic_state'].update(typed_properties={'grants_all_authority':True,'nested':{'unreviewed':[1,2]}}),True)
 probe('same-evidence-commitment-confidence-accepted',lambda x:x['payload']['governance_binding'].update(evidence_confidence_ref='hyp:same',commitment_confidence_ref='hyp:same'),True)
 probe('unresolved-confidence-and-challenge-accepted',lambda x:x['payload']['governance_binding'].update(evidence_confidence_ref='absent:confidence',challenge_contract_ref='absent:challenge'),True)
 probe('huge-positive-semantic-cursor-accepted',lambda x:x['payload']['governance_binding']['semantic_event_ref'].update(semantic_cursor=10**100),True)
 probe('weak-forbidden-collapse-text-accepted',lambda x:x['payload']['semantic_state'].update(forbidden_collapse=['anything']),True)
 probe('admitted-record-state-effect-none-accepted',lambda x:x.update(record_state='admitted'),True)
 probe('permission-sounding-claim-accepted',lambda x:x.update(claim_ceiling='This Node proves global truth and admits its subject.'),True)
 for value in pp['branch']['enum']:probe('branch-'+value+'-accepted',lambda x,value=value:x['payload'].update(branch=value),True)
 for value in sem['properties']['lifecycle']['enum']:probe('lifecycle-'+value+'-accepted',lambda x,value=value:x['payload']['semantic_state'].update(lifecycle=value),True)
 for n in payload['required']:probe('missing-payload-'+n+'-rejected',lambda x,n=n:x['payload'].pop(n),False)
 for n in rs['required']:probe('missing-subject-'+n+'-rejected',lambda x,n=n:x['payload']['represented_subject'].pop(n),False)
 for n in gov['required']:probe('missing-governance-'+n+'-rejected',lambda x,n=n:x['payload']['governance_binding'].pop(n),False)
 for n in sem['required']:probe('missing-semantic-'+n+'-rejected',lambda x,n=n:x['payload']['semantic_state'].pop(n),False)
 probe('empty-provenance-rejected',lambda x:x['payload'].update(provenance_refs=[]),False)
 probe('duplicate-provenance-rejected',lambda x:x['payload'].update(provenance_refs=['hyp:p','hyp:p']),False)
 probe('malformed-subject-digest-rejected',lambda x:x['payload']['represented_subject'].update(digest='G'*64),False)
 probe('zero-semantic-cursor-rejected',lambda x:x['payload']['governance_binding']['semantic_event_ref'].update(semantic_cursor=0),False)
 probe('replay-source-true-rejected',lambda x:x['payload'].update(replay_source=True),False)
 probe('semantic-facet-confidence-field-rejected',lambda x:x['payload']['semantic_state'].update(evidence_confidence_ref='hyp:c'),False)
 probe('governance-facet-proposition-field-rejected',lambda x:x['payload']['governance_binding'].update(proposition='hyp:claim'),False)
 probe('top-authority-effect-inflation-rejected',lambda x:x.update(authority_effect='admitted'),False)
 probe('governance-authority-effect-inflation-rejected',lambda x:x['payload']['governance_binding'].update(authority_effect='admitted'),False)
 probe('unlisted-branch-rejected',lambda x:x['payload'].update(branch='other'),False)
 probe('unlisted-lifecycle-rejected',lambda x:x['payload']['semantic_state'].update(lifecycle='other'),False)
 common=extracted(raw['project_common'],paths['project_common'],['RuntimeFault','require','digest'],{'json':json,'hashlib':hashlib});purefn=extracted(raw['project_sources'],paths['project_sources'],['validate_histories'],common)['validate_histories'];pure=[];frame={'histories':histories,'nodes':[docs['episode_state_node'],docs['episode_project_node']]}
 def rechain(x):
  h=x['histories']['project-governance-event-history']['payload'];previous=None
  for e in h['events']:
   e['previous_event_digest']=previous;e['event_digest']=common['digest']({k:z for k,z in e.items() if k!='event_digest'});previous=e['event_digest']
  h['chain_digest']=common['digest']([e['event_digest'] for e in h['events']])
 def purecase(id,change,accept):
  x=copy.deepcopy(frame);change(x);before=copy.deepcopy(x);error=None
  try:purefn(x['histories']);ok=True
  except common['RuntimeFault'] as e:ok=False;error=str(e)
  assert ok==accept,(id,error)
  pure.append({'case_id':id,'input':x,'pure_checker_accepted':ok,'expected_acceptance':accept,'error':error,'input_preserved':x==before,'actual_runtime_execution':False,'actual_Node_binding_or_confidence_truth_authority_verified':False})
 purecase('captured-Project-event-chains-and-joins',lambda x:None,True)
 purecase('changed-Node-semantic-tuple-not-checked',lambda x:x['nodes'][0]['payload']['governance_binding']['semantic_event_ref'].update(semantic_cursor=999),True)
 purecase('changed-Node-subject-digest-not-checked',lambda x:x['nodes'][0]['payload']['represented_subject'].update(digest='0'*64),True)
 purecase('Node-confidence-authority-not-checked',lambda x:x['nodes'][0]['payload']['governance_binding'].update(evidence_confidence_ref='confidence:global-truth',authority_effect='admitted'),True)
 def semevent(x):return x['histories']['project-semantic-event-history']['payload']['events'][-1]
 def govevent(x):return x['histories']['project-governance-event-history']['payload']['events'][-1]
 purecase('wrong-semantic-cursor-rejected',lambda x:semevent(x).update(cursor=999),False)
 purecase('wrong-semantic-digest-rejected',lambda x:semevent(x).update(event_digest='0'*64),False)
 purecase('broken-semantic-previous-digest-rejected',lambda x:semevent(x).update(previous_event_digest='0'*64),False)
 purecase('deleted-semantic-tail-rejected',lambda x:x['histories']['project-semantic-event-history']['payload']['events'].pop(),False)
 purecase('wrong-semantic-watermark-rejected',lambda x:x['histories']['project-semantic-event-history']['payload'].update(latest_cursor=999),False)
 purecase('wrong-semantic-chain-digest-rejected',lambda x:x['histories']['project-semantic-event-history']['payload'].update(chain_digest='0'*64),False)
 purecase('wrong-governance-cursor-rejected',lambda x:govevent(x).update(governance_cursor=999),False)
 purecase('wrong-governance-digest-rejected',lambda x:govevent(x).update(event_digest='0'*64),False)
 purecase('rehashed-governance-wrong-semantic-id-rejected',lambda x:(govevent(x)['semantic_event_ref'].update(semantic_event_id='absent:event'),rechain(x)),False)
 purecase('rehashed-governance-out-of-range-semantic-cursor-rejected',lambda x:(govevent(x)['semantic_event_ref'].update(semantic_cursor=999),rechain(x)),False)
 purecase('rehashed-governance-wrong-semantic-digest-rejected',lambda x:(govevent(x)['semantic_event_ref'].update(semantic_event_digest='0'*64),rechain(x)),False)
 purecase('missing-Node-Manifest-ref-not-checked',lambda x:x['nodes'][0]['payload'].update(ontology_manifest_ref='absent:manifest'),True)
 purecase('Node-replay-source-true-not-checked',lambda x:x['nodes'][0]['payload'].update(replay_source=True),True)
 purecase('empty-Node-provenance-not-checked',lambda x:x['nodes'][0]['payload'].update(provenance_refs=[]),True)
 ck('pure-captured-history-and-bounded-Node-nonchecks',pure[0]['pure_checker_accepted'] is True and pure[1]['pure_checker_accepted'] is True and all(x['input_preserved'] for x in pure))
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-OntologyNode-profile/v1-candidate','status':'PASS-for-qualified-Node-hypotheses-and-selected-carrier-subject-history-static-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'exact_definition_binding':binding[0],'current_registry_selection':row,'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'fixture_status':fixture['record_state'],'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_representation_frames':frames(),'generic_fixture_subject_and_manifest_gap':subject_gap,'captured_episode_Node_observations':episode,'project_pure_history_controls':pure,'historical_source_current_definition_shape':shape,'native_runtime_executed':False,'project_session_executed':False,'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'existing_pure_projection_and_history_functions_executed':True,'generic_native_project_common_Node_map_accepted':False,'actual_subject_revision_confidence_truth_or_authority_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Actual selected schema/catalog/pure projection checks,generic subject placeholder digest gap,captured Node exact subject byte/event tuple observations,pure Project history controls and static native/DomainSpec/Project source. No whole revision-version/identity/facet/claim-truth/authority map,actual session or native execution,source-owner fidelity,accepted common adapters or joint closure.'}
 b.unchanged(list(refs.values())+context['sources']+report['checker_bindings']+report['input_refs']);assert runtime==v.f.current_bindings()
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh Node observations differ')
 return report

def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'frames':len(x['finite_representation_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_representation_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(z['schema_accepted'] for z in x['schema_probes']),'catalog_checks':x['actual_check_count'],'pure_history_controls':len(x['project_pure_history_controls']),'pure_history_acceptances':sum(z['pure_checker_accepted'] for z in x['project_pure_history_controls'])},indent=2))
if __name__=='__main__':main()

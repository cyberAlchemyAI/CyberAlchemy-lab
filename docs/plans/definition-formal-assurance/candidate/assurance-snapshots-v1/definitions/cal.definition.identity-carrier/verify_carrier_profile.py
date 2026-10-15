"""Bounded identity-record/context traces and exact specialized carrier fixtures."""
import copy,json,types
import build_candidate as b
import verifier as v
def text(x):return isinstance(x,str) and bool(x.strip())
def closed(x,keys):return isinstance(x,dict) and set(x)==set(keys)
def inspect(state):
 if not closed(state,['carriers','views','links','placements','labels','authority']):return False
 if not isinstance(state['carriers'],dict) or not state['carriers']:return False
 identities={}
 for key,row in state['carriers'].items():
  if not closed(row,['carrier_id','subject_id','kind_definition_ref','owner_route','lifecycle_ref','provenance_refs']):return False
  if any(not text(row[x]) for x in ['carrier_id','subject_id','kind_definition_ref','owner_route','lifecycle_ref']) or row['carrier_id']!=key:return False
  if row['kind_definition_ref'] not in ['synthetic.product@1','synthetic.project@1']:return False
  refs=row['provenance_refs']
  if not isinstance(refs,list) or not refs or any(not text(x) for x in refs) or len(set(refs))!=len(refs):return False
  if row['subject_id'] in identities and identities[row['subject_id']]!=row['kind_definition_ref']:return False
  identities[row['subject_id']]=row['kind_definition_ref']
 if not isinstance(state['links'],list):return False
 seen=set()
 for link in state['links']:
  if not closed(link,['link_id','kind_ref','source_ref','target_ref']) or any(not text(x) for x in link.values()):return False
  if link['link_id'] in seen or link['kind_ref']!='synthetic.related@1' or link['source_ref'] not in identities or link['target_ref'] not in identities:return False
  seen.add(link['link_id'])
 if not isinstance(state['authority'],dict) or set(state['authority'])!=set(identities) or any(not text(x) for x in state['authority'].values()):return False
 return all(isinstance(state[x],dict) for x in ['views','placements','labels'])
def initial():
 def carrier(id,subject,kind):return {'carrier_id':id,'subject_id':subject,'kind_definition_ref':kind,'owner_route':'synthetic:shared-owner','lifecycle_ref':'synthetic:lifecycle@1','provenance_refs':['synthetic:source@1']}
 return {'carriers':{'k':carrier('k','subject-a','synthetic.product@1'),'j':carrier('j','subject-b','synthetic.project@1')},'views':{'graph':'synthetic:graph-view','human':'synthetic:human-view'},'links':[],'placements':{'k':'shared-dir','j':'shared-dir'},'labels':{'k':'same-name','j':'same-name'},'authority':{'subject-a':'synthetic:authority-a','subject-b':'synthetic:authority-b'}}
def frame(before,after):return before['carriers']==after['carriers'] and before['authority']==after['authority']
def verify(write=False):
 context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.r.verify(b.snapshot(),b.ROOT)
 runtime=v.f.current_bindings();bindings=[b.ref(p) for p in [b.UNIT/'verify_carrier_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'resolver.py']]
 controls=[]
 def control(name,change,expected):
  state=initial();change(state);actual=inspect(state)
  if actual!=expected:raise ValueError('Wrong record control: '+name)
  controls.append({'case_id':name,'state':state,'accepted_shape':actual,'actual_admission':False})
 control('explicit-identities-share-owner-path-label-without-merging',lambda x:None,True)
 for field in ['subject_id','kind_definition_ref','owner_route','lifecycle_ref','provenance_refs']:
  control('missing-'+field,lambda x,field=field:x['carriers']['k'].pop(field),False)
 control('bare-subject-kind-does-not-resolve',lambda x:x['carriers']['k'].update(kind_definition_ref='product'),False)
 control('bool-is-not-subject-identifier',lambda x:x['carriers']['k'].update(subject_id=True),False)
 control('directory-cannot-substitute-subject-field',lambda x:x['carriers']['k'].update(directory_identity='shared-dir'),False)
 control('embedded-related-identity-is-not-carrier-field',lambda x:x['carriers']['k'].update(related_project={'project_id':'subject-b'}),False)
 control('empty-provenance-is-not-filled-from-directory',lambda x:x['carriers']['k'].update(provenance_refs=[]),False)
 def link(x,source='subject-a',target='subject-b'):x['links']=[{'link_id':'l','kind_ref':'synthetic.related@1','source_ref':source,'target_ref':target}]
 control('typed-external-identity-link',link,True)
 control('self-link-is-not-unconditionally-forbidden',lambda x:link(x,'subject-a','subject-a'),True)
 control('unresolved-target-is-not-synthesized',lambda x:link(x,'subject-a','unresolved-subject'),False)
 def badkind(x):link(x);x['links'][0]['kind_ref']='related'
 control('unversioned-link-kind-rejected',badkind,False)
 def duplicate(x):link(x);x['links'].append(copy.deepcopy(x['links'][0]))
 control('duplicate-link-id-rejected',duplicate,False)
 def transfer(x):link(x);x['links'][0]['authority_grant']='synthetic:grant'
 control('relation-does-not-carry-implicit-authority-grant',transfer,False)
 control('empty-views-are-permitted',lambda x:x.update(views={}),True)
 traces=[]
 def trace(name,steps,expected):
  before=initial();states=[copy.deepcopy(before)];preserved=True
  for change in steps:
   after=copy.deepcopy(states[-1]);change(after);preserved=preserved and inspect(after) and frame(states[-1],after);states.append(after)
  if preserved!=expected:raise ValueError('Wrong finite frame trace: '+name)
  traces.append({'case_id':name,'states':states,'frame_preserved':preserved,'expected_frame_preserved':expected,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 trace('move-and-relabel-with-related-link', [lambda x:x['placements'].update(k='new-dir'),lambda x:x['labels'].update(k='renamed'),link],True)
 trace('graph-and-human-view-removal-preserves-canonical-record',[lambda x:x['views'].pop('graph'),lambda x:x['views'].pop('human')],True)
 trace('relation-membership-add-remove-preserves-identities',[link,lambda x:x.update(links=[])],True)
 trace('shared-owner-path-label-remain-context',[lambda x:x['labels'].update(k=x['labels']['j'])],True)
 trace('path-derived-subject-replacement-is-rejected',[lambda x:x['carriers']['k'].update(subject_id='path-derived-id')],False)
 def erase(x):x['carriers'].pop('k');x['authority'].pop('subject-a');x['views']={}
 trace('view-removal-erases-canonical-record-is-rejected',[erase],False)
 def merge(x):x['carriers']['j'].update(subject_id='subject-a',kind_definition_ref='synthetic.product@1');x['authority'].pop('subject-b')
 trace('related-membership-merges-subject-is-rejected',[merge],False)
 trace('relation-context-transfers-authority-is-rejected',[lambda x:x['authority'].update({'subject-b':x['authority']['subject-a']})],False)
 selected={};actual=[];projections=[];mapping_gaps=[]
 def capture(name,path):
  ref=b.ref(b.ROOT/path);raw=b.r.read_bytes(b.ROOT,path)
  if b.r.digest(raw)!=ref['sha256']:raise ValueError('Capture race')
  selected[name]=ref;return raw
 def check(id,ok,detail=None):
  if not ok:raise ValueError('Actual specialized carrier check failed: '+id)
  actual.append({'check_id':id,'result':True,'detail':detail})
 registry=b.r.parse(capture('registry','authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'),'artifact-type-registry')
 definitions=b.r.parse(capture('definition_registry','authority/definitions/registry.json'),'definition-registry')
 generator_path='tooling/generators/cml07_identity_artifact.py';raw=capture('shared_generator',generator_path);module=types.ModuleType('_bound_identity_generator');module.__file__=str(b.ROOT/generator_path);exec(compile(raw,str(b.ROOT/generator_path),'exec'),module.__dict__)
 fixtures=[]
 for name,version in [('product-identity','v2'),('project-identity','v1'),('goal','v1')]:
  folder='authority/artifact-types/'+name+'/'+version;artifact=b.r.parse(capture(name+'_artifact',folder+'/artifact.json'),'carrier-type');schema=b.r.parse(capture(name+'_schema',folder+'/schema.json'),'carrier-schema');b.c.Draft202012Validator.check_schema(schema)
  ref=artifact['artifact_type_ref'];entry=next(x for x in registry['admitted_contracts'] if x['artifact_type_ref']==ref)
  check(name+'-exact-descriptor-and-schema-overlay',entry['artifact_path']==selected[name+'_artifact']['path'] and entry['artifact_sha256']==selected[name+'_artifact']['sha256'] and entry['schema_sha256']==selected[name+'_schema']['sha256']==artifact['schema_digest'],{'embedded_status':artifact['status'],'registry_lifecycle':entry['lifecycle_state'],'decision_ref':entry['admission_decision_ref']})
  check(name+'-selected-current-contract',registry['current_by_identity'][artifact['artifact_type_id']]==ref)
  check(name+'-closed-specialized-identity-shape',schema.get('additionalProperties') is False and artifact['instance_contract']['identity_field'] in schema['required'])
  for index,binding in enumerate(artifact['semantic_definition_bindings']):
   doc=b.r.parse(capture(name+'_meaning_'+str(index),binding['path']),'bound-meaning');did=doc['definition_id'];version_ref=did+'@'+doc['version'];row=next(x for x in definitions['entries'] if x['definition_id']==did and x['version']==doc['version'])
   check(name+'-meaning-'+str(index)+'-exact-current-admitted-source',version_ref==binding['definition_ref'] and binding['sha256']==selected[name+'_meaning_'+str(index)]['sha256']==row['sha256'] and definitions['current_lookup'][did]==version_ref and row['lifecycle_state']=='admitted')
  check(name+'-IdentityCarrier-semantic-binding-present',any(x['definition_ref']=='cal.definition.identity-carrier@1.0.0-candidate.1' for x in artifact['semantic_definition_bindings']))
  fixture=b.r.parse(capture(name+'_fixture',folder+'/'+artifact['validation_contract']['positive_witness']),'positive-carrier-fixture');check(name+'-positive-specialized-fixture-valid',not list(b.c.Draft202012Validator(schema).iter_errors(fixture)))
  field=artifact['instance_contract']['identity_field'];check(name+'-explicit-fixture-identity-and-non-effect',text(fixture[field]) and fixture['authority_effect']=='none' and 'directory_identity' not in fixture and field in schema['required'],{'identity_field':field,'fixture_identity':fixture[field],'fixture_status':fixture['status']})
  original_artifact=copy.deepcopy(artifact);original_fixture=copy.deepcopy(fixture);first=module.render_artifact(artifact).encode();second=module.render_artifact(artifact).encode();human=capture(name+'_artifact_human',folder+'/ARTIFACT.md')
  check(name+'-two-descriptor-render-parity',first==second==human and artifact['source_direction']['shared_generator_sha256']==selected['shared_generator']['sha256']);projections.append({'carrier':name,'projection':'descriptor','bytes':len(first),'sha256':b.r.digest(first)})
  first=module.render_instance(artifact,fixture).encode();second=module.render_instance(artifact,fixture).encode();human=capture(name+'_fixture_human',folder+'/'+artifact['validation_contract']['positive_projection'])
  check(name+'-two-instance-render-parity',first==second==human and artifact==original_artifact and fixture==original_fixture);projections.append({'carrier':name,'projection':'fixture','bytes':len(first),'sha256':b.r.digest(first)})
  for index,relative in enumerate(artifact['validation_contract']['negative_witnesses']):
   hostile=b.r.parse(capture(name+'_hostile_'+str(index),folder+'/'+relative),'hostile-carrier-fixture');errors=[x.message for x in b.c.Draft202012Validator(schema).iter_errors(hostile)];check(name+'-hostile-'+str(index)+'-rejected',bool(errors));fixtures.append({'path':folder+'/'+relative,'rejected':True,'schema_errors':errors})
  mapping_gaps.append({'carrier':name,'identity_field':field,'literal_generic_fields_absent':[x for x in ['carrier_id','subject_id','subject_kind_definition_ref','lifecycle_ref','provenance_refs'] if x not in fixture],'mapping_reviewed':False,'note':'Specialized identity/kind/owner/evidence/lineage fields may implement generic roles through reviewed maps; literal absence is not a conformance verdict.'})
 b.unchanged(list(selected.values())+context['sources']+bindings);b.r.verify(b.snapshot(),b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-identity-carrier-profile/v1-candidate','authority_effect':'none','status':'PASS-for-bounded-carrier-context-and-selected-specialized-fixtures','checker_bindings':bindings,'runtime_bindings':runtime,'selected_inputs':selected,'profile_controls':controls,'profile_control_count':len(controls),'rejected_profile_controls':sum(not x['accepted_shape'] for x in controls),'finite_frame_traces':traces,'finite_frame_trace_count':len(traces),'rejected_frame_traces':sum(not x['frame_preserved'] for x in traces),'actual_checks':actual,'actual_check_count':len(actual),'actual_hostile_fixtures':fixtures,'actual_hostile_fixture_count':len(fixtures),'selected_specialized_carriers':3,'projections':projections,'source_carrier_mapping_gaps':mapping_gaps,'source_profile_embedding_reviewed':False,'unbounded_preservation_proof':False,'actual_admission_created':False,'new_carriers_created':0,'actual_runtime_activated':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Finite synthetic shape/frame controls and exact read-only current specialized contracts, fixtures, semantic-source bindings and projections. No actual subject creation, canonical deletion, typed relation/admission act, authenticated principal, reviewed generic/specialized embedding, unbounded preservation or meaning-aligned whole theory.'}
 if write:b.put('carrier-profile-checks.json',report)
 elif not b.r.same_json(report,json.loads((b.UNIT/'carrier-profile-checks.json').read_bytes())):raise ValueError('Fresh carrier profile differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({k:x[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_frame_trace_count','rejected_frame_traces','actual_check_count','actual_hostile_fixture_count','selected_specialized_carriers','source_profile_embedding_reviewed','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

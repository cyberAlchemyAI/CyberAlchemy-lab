"""Read-only actual carrier probes and hypothetical parent/local ownership/succession guards."""
import ast,copy,json,typing
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['exact_parent','exact_instance','owner_routes','authority_scopes','clause_coverage','parent_provenance','bounded_extensions','override_authority','override_evidence','claim_separation','read_only_projection','successor_guard']
def qualification(x):
 return ['missing-'+n for n in AXES if x['hypotheses'].get(n) is not True]+(['stale-source-selection'] if x['selected_source_current'] is not True else [])+(['actual-or-authority-claim'] if x['actual_claim'] else [])
def profiles():
 rows=[];base={'hypotheses':{n:True for n in AXES},'selected_source_current':True,'actual_claim':False}
 def add(name,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=qualification(x);assert bool(errors)==reject;rows.append({'profile_name':name,'input':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_authority_or_endpoint_verification':False,'source_fidelity_accepted':False})
 add('allowed-only-under-all-explicit-hypotheses',lambda x:None)
 for n in AXES:add('missing-'+n,lambda x,n=n:x['hypotheses'].update({n:False}),True)
 add('source-selection-stale',lambda x:x.update(selected_source_current=False),True)
 add('actual-authority-or-resolution-claim',lambda x:x.update(actual_claim=True),True)
 return rows
FRAME_KEYS=['parent','parent_version','instance','instance_version','parent_scope','instance_scope']
def frame_errors(x):
 before=x['before'];after=x['after'];errors=[];changed=any(before[n]!=after[n] for n in FRAME_KEYS)
 if changed and (before['id']==after['id'] or x['successor_of']!=before['id']):errors.append('changed-endpoint-or-scope-requires-successor')
 if any(c['provenance']!=after['parent_version'] or c['silently_weakened'] for c in after['inherited']):errors.append('parent-provenance-or-weakening')
 for c in after['overrides']:
  if c['key'] not in after['extension_scope']:errors.append('override-outside-extension')
  if not c['authority_ref'] or not c['evidence_ref']:errors.append('missing-override-citations')
 if x['generic_projection_writable']:errors.append('writable-generic-projection')
 if x['parent_ownership_transferred'] or x['unrestricted_authority_transferred'] or x['actual_claim']:errors.append('transfer-or-actual-claim')
 return errors
def frames():
 doc={'id':'hyp:b1','parent':'hyp:p','parent_version':'hyp:pv1','instance':'hyp:i','instance_version':'hyp:iv1','parent_scope':'hyp:ps','instance_scope':'hyp:is','parent_owner':'hyp:o1','instance_owner':'hyp:o2','inherited':[{'key':'stop','provenance':'hyp:pv1','silently_weakened':False}],'extension_scope':['budget'],'overrides':[{'key':'budget','authority_ref':'hyp:a','evidence_ref':'hyp:e'}]}
 base={'before':doc,'after':copy.deepcopy(doc),'successor_of':None,'generic_projection_writable':False,'parent_ownership_transferred':False,'unrestricted_authority_transferred':False,'actual_claim':False};rows=[]
 def add(name,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=frame_errors(x);assert bool(errors)==reject,(name,errors);rows.append({'frame_name':name,'input':x,'errors':errors,'expected_rejection':reject,'universal_temporal_proof':False,'actual_runtime_execution':False})
 add('unchanged-binding',lambda x:None)
 for n in FRAME_KEYS:
  def good(x,n=n):
   x['after'].update({n:'hyp:changed','id':'hyp:b2'});x['successor_of']='hyp:b1'
   if n=='parent_version':x['after']['inherited'][0]['provenance']='hyp:changed'
  add('explicit-successor-for-changed-'+n,good)
  add('in-place-change-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 add('changed-revision-new-id-without-successor-link',lambda x:x['after'].update(id='hyp:b2',instance_version='hyp:iv2'),True)
 add('silent-weakening',lambda x:x['after']['inherited'][0].update(silently_weakened=True),True)
 add('inherited-provenance-replaced',lambda x:x['after']['inherited'][0].update(provenance='hyp:other'),True)
 add('override-outside-budget-scope',lambda x:x['after']['overrides'][0].update(key='admission'),True)
 for n in ['authority_ref','evidence_ref']:add('override-missing-'+n,lambda x,n=n:x['after']['overrides'][0].update({n:''}),True)
 for n in ['generic_projection_writable','parent_ownership_transferred','unrestricted_authority_transferred','actual_claim']:add(n,lambda x,n=n:x.update({n:True}),True)
 add('same-owner-may-hold-both-routes',lambda x:x['after'].update(instance_owner='hyp:o1'))
 add('owner-route-only-change-not-a-source-successor-trigger',lambda x:x['after'].update(instance_owner='hyp:o3'))
 return rows
def extract(raw,path,names,ns):
 tree=ast.parse(raw,filename=str(path));functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert {n.name for n in functions}==set(names);exec(compile(ast.Module(body=functions,type_ignores=[]),str(path),'exec'),ns);return ns

def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];row=next(x for x in current if x['semantic_kind']=='model-instance-binding');pkg=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((pkg/'artifact.json').read_bytes())
 paths={'registry':rp,'descriptor':pkg/'artifact.json','schema':b.ROOT/row['schema_path'],'fixture':pkg/'fixtures/valid/record.json','artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/'fixtures/valid/RECORD.md','generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'wrapper':pkg/'validate.py','validator':b.ROOT/artifact['validation_contract']['shared_validator_path'],'root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','historical_complete_model':b.ROOT/'authority/artifact-types/candidates/0005-remaining-18-complete-model/model.json','ctx01_validator':b.ROOT/'tooling/validators/ctx01_artifact_type.py'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-positive-Definition-carrier',[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']]==['cal.artifact-type.model-instance-binding/v1'] and len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]))
 ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256']);ck('root-bound',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 ck('shared-generator-and-validator-current',artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['validator']['sha256'])
 renderer=extract(raw['generator'],paths['generator'],['render_artifact','render_instance'],{'json':json,'Any':typing.Any});before=copy.deepcopy(fixture);ck('two-fixture-projections-exact',renderer['render_instance'](artifact,fixture).encode()==renderer['render_instance'](artifact,fixture).encode()==raw['fixture_projection']);ck('artifact-projection-exact',renderer['render_artifact'](artifact).encode()==raw['artifact_projection']);ck('render-input-preserved',fixture==before)
 ck('closed-candidate-with-all-required-fields',schema['additionalProperties'] is False and set(schema['required'])==set(schema['properties']) and schema['properties']['authority_effect']['const']=='none' and schema['properties']['status']['const']=='candidate-unadmitted')
 ck('no-instance-version-or-override-citation-structures','instance_version_ref' not in schema['properties'] and schema['properties']['local_override_refs']['items']['type']=='string' and all(n not in schema['properties'] for n in ['prohibited_clause_refs','unresolved_clause_refs','adoption_refs','realization_refs','identity_claim_refs']))
 code=raw['validator'].decode();tree=ast.parse(code);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='validate_package');selected=ast.get_source_segment(code,fn)
 ck('shared-package-validator-source-inspected-generic',all(n not in selected for n in ['parent_model_version_ref','instance_ref','local_override_refs','extension_scope','successor_refs']) and 'dump(root/"receipts/validation.json",receipt)' in selected)
 ctx=raw['ctx01_validator'].decode();ck('distinct-capability-instance-checks-not-Binding-checks','if slug == "capability-instance"' in ctx and 'parent-instance-authority-distinct' in ctx and '"model-instance-binding"' not in ctx)
 historical=next(x for x in docs['historical_complete_model']['entries'] if x['slug']=='model-instance-binding');ck('historical-model-source-matches-but-carrier-binding-differs',refs['historical_complete_model']['sha256']==b.co.source_document(snap,source)['source_refs'][0]['content_sha256'] and historical['artifact_version']=='1.0.0-candidate.2' and artifact['version']=='1.0.0-candidate.3' and historical['artifact_sha256']!=refs['descriptor']['sha256'] and historical['semantic_definition_refs']==['cal.definition.parent-instance-authority-separation-invariant@1.0.0-candidate.1'] and artifact['semantic_definition_refs']==[source['version_ref']])
 errors=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(b.co.source_document(snap,source)));shape={'current_schema_accepted':not errors,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in errors],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('selected-Definition-v1-current-v2-four-shape-errors',{x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   es=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(es),'errors':es})
 ck('four-hostile-fixtures-rejected',len(hostiles)==4 and all(x['schema_rejected'] for x in hostiles));probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);es=[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in validator.iter_errors(x)];assert (not es)==accept,(id,es);probes.append({'case_id':id,'record':x,'schema_accepted':not es,'expected_schema_acceptance':accept,'errors':es,'actual_endpoint_resolution_authorization_conformance_or_succession_verified':False})
 probe('opaque-parent-version',lambda x:x.update(parent_model_version_ref='unresolved'),True)
 probe('instance-reference-without-version',lambda x:x.update(instance_ref='absent:unversioned'),True)
 probe('binding-parent-instance-identity-collapse',lambda x:x.update(parent_model_ref=x['node_id'],instance_ref=x['node_id']),True)
 probe('same-parent-local-owner-route',lambda x:x.update(instance_owner_route=x['parent_owner_route']),True)
 probe('same-authority-scope',lambda x:x.update(instance_authority_scope=x['parent_authority_scope']),True)
 for n in ['extension_scope','local_override_refs','conformance_refs','successor_refs']:probe('empty-'+n,lambda x,n=n:x.update({n:[]}),True)
 probe('out-of-scope-override-no-citations',lambda x:x.update(extension_scope=[],local_override_refs=['override:admission-without-authority']),True)
 probe('unresolved-inherited-contract-and-conformance',lambda x:x.update(inherited_contract_refs=['absent:contract'],conformance_refs=['absent:proof']),True)
 probe('changed-parent-under-same-binding-id-without-successor',lambda x:x.update(parent_model_version_ref='other:parent@v2',successor_refs=[]),True)
 probe('permission-sounding-claim-ceiling',lambda x:x.update(claim_ceiling='This active Binding grants all parent authority.'),True)
 probe('active-state-with-candidate-status',lambda x:None,True)
 for n in ['proposed','suspended','superseded','retired']:probe('valid-state-'+n,lambda x,n=n:x.update(binding_state=n),True)
 probe('all-five-dispositions-not-required',lambda x:x.update(local_override_refs=[],conformance_refs=[]),True)
 probe('same-owner-and-authority-scopes-not-transfer-proof',lambda x:x.update(parent_owner_route='same:owner',instance_owner_route='same:owner',parent_authority_scope='same:scope',instance_authority_scope='same:scope'),True)
 for n in ['parent_model_ref','parent_model_version_ref','instance_ref','instance_authority_scope','challenge_route']:probe('missing-'+n,lambda x,n=n:x.pop(n),False)
 for val in ['', '   ']:probe('blank-parent-version-'+repr(val),lambda x,val=val:x.update(parent_model_version_ref=val),False)
 probe('empty-inherited-contracts',lambda x:x.update(inherited_contract_refs=[]),False)
 probe('duplicate-inherited-contracts',lambda x:x['inherited_contract_refs'].append(x['inherited_contract_refs'][0]),False)
 probe('too-many-overrides',lambda x:x.update(local_override_refs=[str(i) for i in range(101)]),False)
 probe('structured-override-extra-type',lambda x:x.update(local_override_refs=[{'clause':'budget','authority':'a','evidence':'e'}]),False)
 for n in ['instance_version_ref','adoption_refs','prohibited_clause_refs','unresolved_clause_refs','derived_authority','implicit_admission']:probe('unsupported-extra-'+n,lambda x,n=n:x.update({n:'hyp:claim'}),False)
 probe('authority-effect-admitted',lambda x:x.update(authority_effect='admitted'),False)
 probe('instance-status-admitted',lambda x:x.update(status='admitted'),False)
 probe('binding-state-unknown',lambda x:x.update(binding_state='authorized'),False)
 probe('wrong-kind',lambda x:x.update(kind='capability-realization-binding'),False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-ModelInstanceBinding-profile-checks/v1-candidate','status':'PASS-for-read-only-carrier-probes-and-hypothetical-binding-guards','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py')],'runtime_bindings':runtime,'selected_inputs':refs,'actual_checks':checks,'actual_check_count':len(checks),'profiles':profiles(),'finite_binding_frames':frames(),'schema_probes':probes,'negative_fixture_checks':hostiles,'historical_source_current_definition_shape':shape,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'current_registry_selection':row,'exact_definition_binding':binding[0],'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'descriptor_version':artifact['version'],'carrier_schema_ref':artifact['schema_ref'],'fixture_kind':fixture['kind'],'fixture_status':fixture['status'],'fixture_binding_state':fixture['binding_state'],'historical_complete_model_row':historical,'bound_package_validator_executed':False,'bound_package_validator_static_source_inspected':True,'only_pure_generator_functions_executed':True,'generator_module_or_materialization_writer_executed':False,'actual_runtime_execution':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Actual exact current carrier/schema and deterministic projections with selected fixture/hostile/schema observations. Hypothetical twelve-axis qualification and finite succession/provenance/override frames do not authenticate real identities,grants/evidence or prove universal temporal behavior. Current C70 carrier admission and retained candidate descriptor/active fixture are separate; historic invariant carrier not silently equated.'}
 b.unchanged(context['sources']+list(refs.values()));b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile checks differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'actual_checks':len(x['actual_checks']),'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_binding_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_binding_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(y['schema_accepted'] for y in x['schema_probes']),'actual_runtime_execution':False},indent=2))
if __name__=='__main__':main()

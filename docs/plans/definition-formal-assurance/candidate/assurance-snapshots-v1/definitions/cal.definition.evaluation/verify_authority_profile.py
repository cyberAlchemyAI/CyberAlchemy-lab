"""Qualified Evaluation hypotheses and read-only carrier/schema/role/projection observations."""
import ast,copy,itertools,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['identity','kind','carrier','source','profile','subject','input','profile_digest','subject_digest','input_digest','check_set','coverage_set','dependency_set','evidence_set','outcome_set','relation_roles']
FORBIDDEN=['PASS_is_conformance','PASS_is_admission','PASS_is_authority','status_label_is_execution','digest_label_is_currentness','evidence_ref_is_adequate_support','blocker_ref_is_actual_cause','nonempty_outcomes_is_collect_all','schema_is_status_enum_or_unique_checks','carrier_admission_is_instance_admission','source_admission_is_translation_fidelity','profile_effect_inclusion_is_authority','PASS_cycle_is_valid_execution','nonentailment_denies_independently_supported_outcomes']
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['binding-changed:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_evaluation_correctness_causal_adequacy_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-collect-all-record',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('all-statuses-without-actual-outcome-inference',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 def outcome(c,result,blockers):return {'check':c,'result':result,'run_binding':True,'handle':'hyp:outcome','check_handle':'hyp:check','evidence_set_declared':True,'evidence_set_handle':'hyp:set','evidence_handles':[],'blockers':blockers}
 def blocker(up=None):return {'declared':True,'handle':'hyp:blocker','cause':'hyp:cause','dependency_qualified':up is not None,'upstream':up}
 checks=['pass','fail','ne','blocked'];base={'before':envelope(),'after':envelope(),'selected':True,'record_declared':True,'application_declared':True,'profile_declared':True,'current_declarations':{n:True for n in ['profile','subject','input']},'exact_digest_maps':{n:True for n in ['profile','subject','input']},'handles':{n:'hyp:'+n for n in ['run','profile','subject','input','outcome_set','profile_digest','subject_digest','input_digest']},'outcome_set_declared':True,'profile_checks':checks,'profile_coverage':checks,'dependencies':[['blocked','fail']],'outcomes':[outcome('pass','PASS',[]),outcome('fail','FAIL',[]),outcome('ne','NOT_EVALUABLE',[blocker()]),outcome('blocked','NOT_EVALUABLE',[blocker('fail')])],'validation_role':False,'validation_profile':False,'conformance_role':False,'authority_decision_role':False,'effect_declared':False,'explicit_profile_effect':False,'actual_outcome_claim':False};rows=[]
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('qualified-binding-change-needs-independent-review')
  if x['selected']:
   for n in ['record_declared','application_declared','profile_declared','outcome_set_declared']:
    if not x[n]:errors.append('missing-'+n)
   for n,value in x['current_declarations'].items():
    if not value:errors.append('not-current-declared:'+n)
   for n,value in x['exact_digest_maps'].items():
    if not value:errors.append('digest-map-mismatch:'+n)
   for n,value in x['handles'].items():
    if not value:errors.append('empty-handle:'+n)
   for c in x['profile_checks']:
    if sum(o['check']==c for o in x['outcomes'])!=1:errors.append('not-exactly-one-outcome:'+c)
   for o in x['outcomes']:
    if o['check'] not in x['profile_checks'] or o['check'] not in x['profile_coverage']:errors.append('undeclared-or-uncovered-outcome')
    for n in ['run_binding','handle','check_handle','evidence_set_declared','evidence_set_handle']:
     if not o[n]:errors.append('outcome-missing-or-wrong-'+n)
    if o['result'] not in ['PASS','FAIL','NOT_EVALUABLE']:errors.append('unknown-status')
    if not all(o['evidence_handles']):errors.append('empty-evidence-member-handle')
    if o['result']=='NOT_EVALUABLE' and not o['blockers']:errors.append('NE-without-blocker')
    for bb in o['blockers']:
     if not all(bb[n] for n in ['declared','handle','cause']):errors.append('missing-blocker-declaration-handle-or-cause')
   for down,up in x['dependencies']:
    if down not in x['profile_checks'] or up not in x['profile_checks']:errors.append('dependency-endpoint-undeclared')
    for uo in [o for o in x['outcomes'] if o['check']==up and o['result']!='PASS']:
     for do in [o for o in x['outcomes'] if o['check']==down]:
      if do['result']!='NOT_EVALUABLE' or not any(bb['dependency_qualified'] and bb['upstream']==up for bb in do['blockers']):errors.append('failed-prerequisite-not-preserved')
   if x['validation_role'] and not x['validation_profile']:errors.append('validation-without-profile')
   if x['conformance_role'] or x['authority_decision_role']:errors.append('excluded-determination-role')
   if x['effect_declared'] and not x['explicit_profile_effect']:errors.append('effect-outside-profile')
  if x['actual_outcome_claim']:errors.append('record-does-not-establish-actual-execution-correctness-or-authority')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_evaluation_correctness_causal_adequacy_or_authority_verified':False,'universal_dependency_or_causal_proof':False})
 add('collect-all-three-statuses-causal-blockers',lambda x:None,False)
 add('empty-evidence-membership-permitted',lambda x:None,False)
 add('declared-member-handles',lambda x:x['outcomes'][0].update(evidence_handles=['hyp:evidence']),False)
 add('qualified-validation-role',lambda x:x.update(validation_role=True,validation_profile=True),False)
 add('explicit-profile-effects',lambda x:x.update(effect_declared=True,explicit_profile_effect=True),False)
 add('validation-profile-does-not-force-role',lambda x:x.update(validation_profile=True),False)
 add('successful-prerequisite-does-not-force-PASS',lambda x:x['dependencies'].append(['fail','pass']),False)
 add('declared-PASS-self-cycle-not-a-valid-execution-claim',lambda x:x['dependencies'].append(['pass','pass']),False)
 add('empty-profile-check-set-not-universally-forbidden',lambda x:x.update(profile_checks=[],profile_coverage=[],dependencies=[],outcomes=[]),False)
 add('outside-selected-record',lambda x:x.update(selected=False,outcomes=[],record_declared=False),False)
 for n in AXES:add('changed-binding-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in ['record_declared','application_declared','profile_declared','outcome_set_declared']:add('missing-'+n,lambda x,n=n:x.update({n:False}),True)
 for n in ['profile','subject','input']:
  add('missing-current-'+n,lambda x,n=n:x['current_declarations'].update({n:False}),True)
  add('wrong-digest-'+n,lambda x,n=n:x['exact_digest_maps'].update({n:False}),True)
 for n in base['handles']:add('empty-handle-'+n,lambda x,n=n:x['handles'].update({n:''}),True)
 add('omitted-declared-check',lambda x:x['outcomes'].pop(0),True)
 add('duplicate-check-outcome',lambda x:x['outcomes'].append(copy.deepcopy(x['outcomes'][0])),True)
 add('unknown-status',lambda x:x['outcomes'][0].update(result='UNKNOWN'),True)
 add('outcome-check-outside-profile',lambda x:x['outcomes'][0].update(check='other'),True)
 add('profile-coverage-gap',lambda x:x.update(profile_coverage=['fail','ne','blocked']),True)
 for n in ['run_binding','handle','check_handle','evidence_set_declared','evidence_set_handle']:add('missing-outcome-'+n,lambda x,n=n:x['outcomes'][0].update({n:False if isinstance(x['outcomes'][0][n],bool) else ''}),True)
 add('empty-evidence-member-handle',lambda x:x['outcomes'][0].update(evidence_handles=['']),True)
 add('NE-without-blocker',lambda x:x['outcomes'][2].update(blockers=[]),True)
 for n in ['declared','handle','cause']:add('missing-causal-'+n,lambda x,n=n:x['outcomes'][2]['blockers'][0].update({n:False if n=='declared' else ''}),True)
 for s in ['PASS','FAIL']:add('blocked-dependent-mislabeled-'+s,lambda x,s=s:x['outcomes'][3].update(result=s),True)
 add('wrong-upstream-cause',lambda x:x['outcomes'][3]['blockers'][0].update(upstream='pass'),True)
 add('unqualified-dependency-blocker',lambda x:x['outcomes'][3]['blockers'][0].update(dependency_qualified=False),True)
 add('undeclared-dependency-endpoint',lambda x:x['dependencies'].append(['pass','outside']),True)
 add('validation-without-profile',lambda x:x.update(validation_role=True),True)
 add('conformance-determination-role',lambda x:x.update(conformance_role=True),True)
 add('authority-decision-role',lambda x:x.update(authority_decision_role=True),True)
 add('effect-without-profile',lambda x:x.update(effect_declared=True),True)
 add('declared-record-as-actual-authority',lambda x:x.update(actual_outcome_claim=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert len(direct)==1;carrier=direct[0];ap=b.ROOT/carrier['artifact_path'];artifact=json.loads(ap.read_bytes())
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','direct_artifact':ap,'direct_schema':b.ROOT/carrier['schema_path'],'direct_fixture':ap.parent/artifact['validation_contract']['positive_witness'],'relation_model':b.ROOT/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json','role_observer_source':b.ROOT/artifact['validation_contract']['shared_validator_path'],'carrier_generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'artifact_projection':ap.with_name('ARTIFACT.md'),'fixture_projection':ap.parent/artifact['validation_contract']['positive_projection'],'checker':b.UNIT/'verify_authority_profile.py'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['hostile_'+str(i)]=ap.parent/n
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];schema=docs['direct_schema'];b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(schema);dv=b.c.Draft202012Validator(ds);cv=b.c.Draft202012Validator(schema);generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121);ck('direct-current-Evaluation-v1-C70',carrier['artifact_type_ref']=='cal.artifact-type.evaluation/v1' and carrier['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION');ck('direct-exact-current-Definition-meaning',carrier['semantic_definition_refs']==artifact['semantic_definition_refs']==[source['version_ref']]);ck('direct-artifact-schema-bytes-current',refs['direct_artifact']['sha256']==carrier['artifact_sha256'] and refs['direct_schema']['sha256']==carrier['schema_sha256']==artifact['schema_digest']);ck('direct-retained-body-candidate-none',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none');ck('direct-exact-C29-Definition-binding',artifact['semantic_definition_bindings'][0]['path']==source['path'] and artifact['semantic_definition_bindings'][0]['sha256']==source['sha256'] and artifact['semantic_definition_bindings'][0]['definition_ref']==source['version_ref'] and artifact['semantic_definition_bindings'][0]['admission_decision_ref']=='CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1');ck('closed14root4payload4outcome-shape',schema['additionalProperties'] is False and len(schema['required'])==14 and schema['properties']['payload']['additionalProperties'] is False and len(schema['properties']['payload']['required'])==4 and len(schema['properties']['payload']['properties']['outcomes']['items']['required'])==4);ck('direct-exact-discriminator',schema['properties']['schema_version']['const']==carrier['instance_discriminator']['value']=='cyberalchemy-lab-evaluation/v1');ck('current-generic-Definition-separate-meaning',len(generic)==1 and generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']]);ck('historical-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows));ck('selected-Definition-v1-shape-valid',not list(dv.iter_errors(docs['source'])));ck('three-source-postures-and-C13-profile-admission-separate',[x['admission_posture'] for x in docs['source']['source_refs']]==['admitted','admitted','candidate-unadmitted'] and load('source-checks.json')['exact_profile_record_admission_ref']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION');ck('pure-role-observer-source-bound',refs['role_observer_source']['sha256']==artifact['validation_contract']['shared_validator_sha256']);ck('pure-carrier-generator-source-bound',refs['carrier_generator']['sha256']==artifact['source_direction']['shared_generator_sha256'])
 model_assign=next(x for x in ast.parse(paths['role_observer_source'].read_bytes()).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RELATION_MODEL' for t in x.targets));assert isinstance(model_assign.value,ast.BinOp) and isinstance(model_assign.value.op,ast.Div) and isinstance(model_assign.value.left,ast.Name) and model_assign.value.left.id=='LAB' and isinstance(model_assign.value.right,ast.Constant);ck('validator-declared-relation-model-location-bound',model_assign.value.right.value==refs['relation_model']['path'])
 nodes=[x for x in ast.parse(paths['role_observer_source'].read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name=='expected_roles'];assert len(nodes)==1;ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['role_observer_source']),'exec'),ns);expected=ns['expected_roles']('evaluation',docs['relation_model']);allowed={(x['relation_kind_ref'],x['direction'],k) for x in expected for k in x['counterpart_kinds']};ck('pure-role-surface-exact',artifact['relation_roles']==expected and artifact['allowed_relation_kinds']==sorted({x['relation_kind_ref'] for x in expected}));ck('four-orthogonality-rules-two-neighbors',len(artifact['orthogonality_rules'])==4 and artifact['hostile_non_collapse']==['measurement-result','review'])
 generator=types.ModuleType('_pure_evaluation_carrier_projection');exec(compile(paths['carrier_generator'].read_bytes(),str(paths['carrier_generator']),'exec'),generator.__dict__);before=copy.deepcopy(docs['direct_fixture']);a1=generator.render_artifact(artifact).encode();a2=generator.render_artifact(artifact).encode();f1=generator.render_instance(artifact,before).encode();f2=generator.render_instance(artifact,before).encode();ck('two-pure-artifact-and-fixture-projections',a1==a2==paths['artifact_projection'].read_bytes() and f1==f2==paths['fixture_projection'].read_bytes() and before==docs['direct_fixture'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];carrier_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored shape probe '+id+' '+str(errors))
  row={'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_evaluation_correctness_causal_adequacy_or_authority_verified':False}
  if bucket is carrier_probes:row['declared_roles_satisfied']=all((x.get('relation_kind_ref'),x.get('direction'),x.get('counterpart_kind')) in allowed for x in doc.get('relation_refs',[]))
  bucket.append(row)
 original=docs['source'];probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-required-root-'+n,x,dv,False)
 for n in ['profile_digest','subject_digest','input_digest','check_outcome']:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'shape-does-not-resolve-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:PASS establishes admission and authority';probe(definition_probes,'shape-valid-overclaimed-text',x,dv,True)
 fixture=docs['direct_fixture'];probe(carrier_probes,'exact-current-direct-fixture',copy.deepcopy(fixture),cv,True)
 for n in schema['required']:
  x=copy.deepcopy(fixture);x.pop(n);probe(carrier_probes,'missing-root-'+n,x,cv,False)
 for n in schema['properties']['payload']['required']:
  x=copy.deepcopy(fixture);x['payload'].pop(n);probe(carrier_probes,'missing-payload-'+n,x,cv,False)
 for n in ['profile_ref','subject_ref','input_state_ref']:
  x=copy.deepcopy(fixture);x['payload'][n]='hyp:unresolved';probe(carrier_probes,'unresolved-'+n+'-shape-valid',x,cv,True)
 for n in schema['properties']['payload']['properties']['outcomes']['items']['required']:
  x=copy.deepcopy(fixture);x['payload']['outcomes'][0].pop(n);probe(carrier_probes,'missing-outcome-'+n,x,cv,False)
 for n in ['check_id','result','blocker_ref']:
  x=copy.deepcopy(fixture);x['payload']['outcomes'][0][n]='';probe(carrier_probes,'empty-outcome-'+n,x,cv,False)
 for n,value in [('result','UNKNOWN'),('result','NOT_EVALUABLE'),('blocker_ref','none'),('check_id','hyp:undeclared'),('blocker_ref','hyp:unresolved-cause')]:
  x=copy.deepcopy(fixture);x['payload']['outcomes'][0][n]=value;probe(carrier_probes,'shape-valid-'+n+'-'+value,x,cv,True)
 x=copy.deepcopy(fixture);x['payload']['outcomes'].append(copy.deepcopy(x['payload']['outcomes'][0]));probe(carrier_probes,'duplicate-check-and-outcome-accepted',x,cv,True)
 x=copy.deepcopy(fixture);extra=copy.deepcopy(x['payload']['outcomes'][0]);extra['result']='FAIL';x['payload']['outcomes'].append(extra);probe(carrier_probes,'contradictory-statuses-for-same-check-accepted',x,cv,True)
 x=copy.deepcopy(fixture);x['payload']['outcomes'][0]['evidence_refs']=[];probe(carrier_probes,'empty-outcome-evidence-rejected',x,cv,False)
 x=copy.deepcopy(fixture);x['payload']['outcomes']=[];probe(carrier_probes,'empty-outcomes-rejected',x,cv,False)
 x=copy.deepcopy(fixture);x['evidence_refs']=[];probe(carrier_probes,'empty-root-evidence-accepted',x,cv,True)
 x=copy.deepcopy(fixture);x['payload']['outcomes'][0]['result']='   ';probe(carrier_probes,'whitespace-result-accepted',x,cv,True)
 x=copy.deepcopy(fixture);x['lifecycle_state']='active';probe(carrier_probes,'active-label-does-not-prove-execution',x,cv,True)
 x=copy.deepcopy(fixture);x['claim_ceiling']='hyp:actual execution conformance and admission verified';probe(carrier_probes,'overclaimed-ceiling-accepted',x,cv,True)
 x=copy.deepcopy(fixture);x['payload']['profile_digest']='hyp:digest';probe(carrier_probes,'extra-digest-field-rejected',x,cv,False)
 for location in ['root','payload']:
  x=copy.deepcopy(fixture);(x if location=='root' else x['payload'])['implicit_authority']='hyp:claimed';probe(carrier_probes,'extra-'+location+'-field-rejected',x,cv,False)
 x=copy.deepcopy(fixture);x['authority_effect']='canonical';probe(carrier_probes,'governing-effect-rejected',x,cv,False)
 x=copy.deepcopy(fixture);x['kind']='measurement-result';probe(carrier_probes,'collapsed-neighbor-kind-rejected',x,cv,False)
 x=copy.deepcopy(fixture);x['relation_refs']=[];probe(carrier_probes,'empty-relations-rejected',x,cv,False)
 for i in range(5):probe(carrier_probes,'retained-hostile-'+str(i),docs['hostile_'+str(i)],cv,False)
 products=[];rp=schema['properties']['relation_refs']['items']['properties']
 for kind,direction,counterpart in itertools.product(rp['relation_kind_ref']['enum'],rp['direction']['enum'],rp['counterpart_kind']['enum']):
  x=copy.deepcopy(fixture);x['relation_refs'][0].update(relation_kind_ref=kind,direction=direction,counterpart_kind=counterpart);assert not list(cv.iter_errors(x));products.append({'relation_kind_ref':kind,'direction':direction,'counterpart_kind':counterpart,'schema_accepted':True,'declared_role_member':(kind,direction,counterpart) in allowed,'actual_evaluation_correctness_causal_adequacy_or_authority_verified':False})
 assert len(products)==3 and len(allowed)==3 and sum(not x['declared_role_member'] for x in products)==0
 current_errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in b.c.Draft202012Validator(docs['current_Definition_schema']).iter_errors(original)];inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(x) for x in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']]
 report={'schema_version':'definition-assurance-Evaluation-profile/v1-candidate','status':'PASS-for-qualified-Evaluation-hypotheses-and-actual-C70-shape-role-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_comparison_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'direct_carrier_admission_ref':carrier['admission_decision_ref'],'direct_carrier_semantic_ref':carrier['semantic_definition_refs'][0],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'Definition_schema_probes':definition_probes,'direct_carrier_schema_probes':carrier_probes,'role_schema_product_probes':products,'role_schema_product_count':3,'declared_role_product_members':3,'schema_accepted_but_role_invalid_products':0,'pure_role_surface_observer_executed':True,'pure_carrier_projection_functions_executed':True,'pure_carrier_projection_observations':{'artifact_bytes':len(a1),'artifact_sha256':b.r.digest(a1),'fixture_bytes':len(f1),'fixture_sha256':b.r.digest(f1)},'historical_source_current_Definition_shape':{'errors':current_errors,'exact_source_admission_invalidated':False},'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_evaluation_correctness_causal_adequacy_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified collect-all/causal/role hypotheses and actual C70 Evaluation carrier/schema,pure roles/projections. All3relation enum products match the declared role surface. Shape accepts unknown result labels,duplicate and contradictory check outcomes,unresolved refs and NOT_EVALUABLE with blocker none;it does not establish exact digests,collect-all coverage,causal adequacy,actual execution,admission or owner fidelity. No package writer,live consumer,accepted alignment or whole proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_comparison_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_comparison_frames']),'catalog_checks':x['actual_check_count'],'Definition_probes':len(x['Definition_schema_probes']),'Definition_acceptances':sum(y['schema_accepted'] for y in x['Definition_schema_probes']),'carrier_probes':len(x['direct_carrier_schema_probes']),'carrier_acceptances':sum(y['schema_accepted'] for y in x['direct_carrier_schema_probes']),'role_schema_products':3,'declared_role_members':3,'schema_accepted_but_role_invalid':0},indent=2))
if __name__=='__main__':main()

"""Qualified comparison hypotheses and actual C70 carrier/schema/pure-role observations; no package writer."""
import ast,copy,itertools,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['identity','kind','carrier','source','subject','scope','time','dimension','declared_value','observed_value','evidence_set','evidence_membership','assessment_owner','relation_roles']
FORBIDDEN=['mismatch_is_cause','mismatch_is_severity','mismatch_is_failure','mismatch_is_correction_authority','mismatch_is_required_remediation','value_handle_is_value_equality','time_label_is_authenticated_epoch','evidence_ref_is_adequate_support','schema_product_is_declared_role','carrier_admission_is_instance_admission','source_admission_is_translation_fidelity','conformance_is_actual_drift','nonentailment_denies_independently_supported_outcomes']
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['binding-changed:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_comparison_cause_severity_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-dimensional-comparison',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('matched-and-mismatched-assessments-without-actual-outcome-inference',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'record_declared':True,'comparison_declared':True,'governed_identity_or_record':True,'subject_declared':True,'scope_declared':True,'time_declared':True,'owner_declared':True,'evidence_set_declared':True,'evidence_set_matches_subject_scope_time':True,'handles':{n:'hyp:'+n for n in ['assessment','subject','scope','time','owner','evidence_set']},'slots':[{'declared':True,'matches_assessment_subject_scope_time':True,'dimension':'Version','values_declared':True,'values_match_dimension':True,'declared_value':'hyp:declared','observed_value':'hyp:observed','handle':'hyp:slot','value_handles':['hyp:declared','hyp:observed'],'mismatch_label':True,'evidence':[{'member':True,'bears_on_slot':True,'matches_subject_scope_time':True,'handle':'hyp:evidence'}]}],'actual_outcome_claim':False};rows=[]
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('qualified-binding-change-needs-independent-review')
  if x['selected']:
   for n in ['record_declared','comparison_declared','governed_identity_or_record','subject_declared','scope_declared','time_declared','owner_declared','evidence_set_declared','evidence_set_matches_subject_scope_time']:
    if not x[n]:errors.append('missing-or-wrong-'+n)
   for n,value in x['handles'].items():
    if not value:errors.append('empty-handle:'+n)
   if not x['slots']:errors.append('no-included-comparison-slot')
   for slot in x['slots']:
    for n in ['declared','matches_assessment_subject_scope_time','values_declared','values_match_dimension']:
     if not slot[n]:errors.append('slot-missing-or-wrong-'+n)
    if slot['dimension'] not in b.DIMENSIONS:errors.append('unmapped-comparison-dimension')
    if not slot['handle'] or not all(slot['value_handles']):errors.append('empty-slot-or-value-handle')
    if slot['mismatch_label']!=(slot['declared_value']!=slot['observed_value']):errors.append('mapped-value-inequality-label-mismatch')
    if not any(e['member'] and e['bears_on_slot'] and e['matches_subject_scope_time'] and e['handle'] for e in slot['evidence']):errors.append('no-included-matching-evidence-witness')
  if x['actual_outcome_claim']:errors.append('declaration-is-not-actual-drift-cause-severity-or-authority')
  assert bool(errors)==reject,(id,errors);rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_comparison_cause_severity_or_authority_verified':False,'universal_temporal_equality_or_causal_proof':False})
 add('declared-mismatch-without-actual-cause-or-authority',lambda x:None,False)
 for n in b.DIMENSIONS:add('independent-dimension-'+n,lambda x,n=n:x['slots'][0].update(dimension=n),False)
 add('matched-comparison-remains-assessment',lambda x:x['slots'][0].update(observed_value='hyp:declared',mismatch_label=False),False)
 add('plural-included-slots',lambda x:x['slots'].append(copy.deepcopy(x['slots'][0])),False)
 add('unrelated-evidence-does-not-replace-matching-witness',lambda x:x['slots'][0]['evidence'].append({'member':True,'bears_on_slot':False,'matches_subject_scope_time':False,'handle':'hyp:unrelated'}),False)
 add('outside-selected-assessment',lambda x:x.update(selected=False,slots=[],time_declared=False),False)
 for n in AXES:add('changed-binding-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in ['record_declared','comparison_declared','governed_identity_or_record','subject_declared','scope_declared','time_declared','owner_declared','evidence_set_declared','evidence_set_matches_subject_scope_time']:add('missing-'+n,lambda x,n=n:x.update({n:False}),True)
 for n in base['handles']:add('empty-'+n,lambda x,n=n:x['handles'].update({n:''}),True)
 add('no-comparison-slots',lambda x:x.update(slots=[]),True)
 for n in ['declared','matches_assessment_subject_scope_time','values_declared','values_match_dimension']:add('missing-slot-'+n,lambda x,n=n:x['slots'][0].update({n:False}),True)
 add('unmapped-dimension',lambda x:x['slots'][0].update(dimension='hyp:unmapped'),True)
 add('empty-slot-handle',lambda x:x['slots'][0].update(handle=''),True)
 add('empty-value-handle',lambda x:x['slots'][0].update(value_handles=['','hyp:observed']),True)
 add('wrong-mismatch-label',lambda x:x['slots'][0].update(mismatch_label=False),True)
 add('included-slot-without-evidence',lambda x:x['slots'][0].update(evidence=[]),True)
 for n in ['member','bears_on_slot','matches_subject_scope_time']:add('evidence-without-'+n,lambda x,n=n:x['slots'][0]['evidence'][0].update({n:False}),True)
 add('evidence-without-handle',lambda x:x['slots'][0]['evidence'][0].update(handle=''),True)
 add('declared-assessment-as-actual-cause-or-authority',lambda x:x.update(actual_outcome_claim=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert len(direct)==1;carrier=direct[0];ap=b.ROOT/carrier['artifact_path'];artifact=json.loads(ap.read_bytes())
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','direct_artifact':ap,'direct_schema':b.ROOT/carrier['schema_path'],'direct_fixture':ap.parent/artifact['validation_contract']['positive_witness'],'relation_model':b.ROOT/artifact['relation_model_binding']['path'],'role_observer_source':b.ROOT/artifact['validation_contract']['shared_validator_path'],'carrier_generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'artifact_projection':ap.with_name('ARTIFACT.md'),'fixture_projection':ap.parent/artifact['validation_contract']['positive_projection'],'checker':b.UNIT/'verify_authority_profile.py'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['hostile_'+str(i)]=ap.parent/n
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];schema=docs['direct_schema'];b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(schema);dv=b.c.Draft202012Validator(ds);cv=b.c.Draft202012Validator(schema);generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121);ck('direct-current-DriftAssessment-v1-C70',carrier['artifact_type_ref']=='cal.artifact-type.drift-assessment/v1' and carrier['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION');ck('direct-exact-current-Definition-meaning',carrier['semantic_definition_refs']==artifact['semantic_definition_refs']==[source['version_ref']]);ck('direct-artifact-schema-bytes-current',refs['direct_artifact']['sha256']==carrier['artifact_sha256'] and refs['direct_schema']['sha256']==carrier['schema_sha256']==artifact['schema_digest']);ck('direct-retained-body-candidate-none',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none');ck('direct-exact-C65-Definition-binding',artifact['semantic_definition_bindings'][0]['path']==source['path'] and artifact['semantic_definition_bindings'][0]['sha256']==source['sha256'] and artifact['semantic_definition_bindings'][0]['definition_ref']==source['version_ref'] and artifact['semantic_definition_bindings'][0]['admission_decision_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION');ck('closed14root9payload-shape',schema['additionalProperties'] is False and len(schema['required'])==14 and schema['properties']['payload']['additionalProperties'] is False and len(schema['properties']['payload']['required'])==9);ck('direct-exact-discriminator',schema['properties']['schema_version']['const']==carrier['instance_discriminator']['value']=='cyberalchemy-lab-drift-assessment/v1');ck('current-generic-Definition-separate-meaning',len(generic)==1 and generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']]);ck('historical-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows));ck('selected-Definition-v1-shape-valid',not list(dv.iter_errors(docs['source'])));ck('historical-source-and-C65-overlay-separate',all(x['admission_posture']=='candidate-unadmitted' for x in docs['source']['source_refs']) and load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION');ck('relation-model-bytes-bound',refs['relation_model']['sha256']==artifact['relation_model_binding']['sha256']);ck('pure-role-observer-source-bound',refs['role_observer_source']['sha256']==artifact['validation_contract']['shared_validator_sha256']);ck('pure-carrier-generator-source-bound',refs['carrier_generator']['sha256']==artifact['source_direction']['shared_generator_sha256'])
 nodes=[x for x in ast.parse(paths['role_observer_source'].read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name=='roles_for'];assert len(nodes)==1;ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['role_observer_source']),'exec'),ns);expected=ns['roles_for']('drift-assessment',docs['relation_model']);allowed={(x['relation_kind_ref'],x['direction'],k) for x in expected for k in x['counterpart_kinds']};ck('pure-role-surface-exact',artifact['relation_roles']==expected and artifact['allowed_relation_kinds']==sorted({x['relation_kind_ref'] for x in expected}));ck('four-orthogonality-rules-two-neighbors',len(artifact['orthogonality_rules'])==4 and artifact['hostile_non_collapse']==['failure-assessment','finding'])
 generator=types.ModuleType('_pure_drift_carrier_projection');exec(compile(paths['carrier_generator'].read_bytes(),str(paths['carrier_generator']),'exec'),generator.__dict__);before=copy.deepcopy(docs['direct_fixture']);a1=generator.render_artifact(artifact).encode();a2=generator.render_artifact(artifact).encode();f1=generator.render_instance(artifact,before).encode();f2=generator.render_instance(artifact,before).encode();ck('two-pure-artifact-and-fixture-projections',a1==a2==paths['artifact_projection'].read_bytes() and f1==f2==paths['fixture_projection'].read_bytes() and before==docs['direct_fixture'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];carrier_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored shape probe '+id+' '+str(errors))
  row={'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_comparison_cause_severity_or_authority_verified':False}
  if bucket is carrier_probes:row['declared_roles_satisfied']=all((x.get('relation_kind_ref'),x.get('direction'),x.get('counterpart_kind')) in allowed for x in doc.get('relation_refs',[]))
  bucket.append(row)
 original=docs['source'];probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-required-root-'+n,x,dv,False)
 for n in ['comparison_time','declared_value','observed_value','remediation_authority_ref']:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'shape-does-not-resolve-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:mismatch establishes critical failure and correction authority';probe(definition_probes,'shape-valid-overclaimed-text',x,dv,True)
 fixture=docs['direct_fixture'];probe(carrier_probes,'exact-current-direct-fixture',copy.deepcopy(fixture),cv,True)
 for n in schema['required']:
  x=copy.deepcopy(fixture);x.pop(n);probe(carrier_probes,'missing-root-'+n,x,cv,False)
 for n in schema['properties']['payload']['required']:
  x=copy.deepcopy(fixture);x['payload'].pop(n);probe(carrier_probes,'missing-payload-'+n,x,cv,False)
 for n in ['subject_ref','expected_version_ref','observed_version_ref','comparison_time','cause_posture','severity_posture','remediation_authority_ref']:
  x=copy.deepcopy(fixture);x['payload'][n]='hyp:unresolved-or-overclaimed';probe(carrier_probes,'shape-does-not-resolve-'+n,x,cv,True)
 for n in ['mismatch_refs','evidence_refs']:
  x=copy.deepcopy(fixture);x['payload'][n]=[];probe(carrier_probes,'empty-payload-'+n+'-accepted',x,cv,True)
 x=copy.deepcopy(fixture);x['evidence_refs']=[];probe(carrier_probes,'empty-root-evidence-accepted',x,cv,True)
 x=copy.deepcopy(fixture);x['payload']['comparison_time']='   ';probe(carrier_probes,'whitespace-time-has-no-authenticated-epoch',x,cv,True)
 x=copy.deepcopy(fixture);x['lifecycle_state']='active';probe(carrier_probes,'active-label-does-not-prove-activation',x,cv,True)
 x=copy.deepcopy(fixture);x['claim_ceiling']='hyp:actual drift cause severity and correction authority verified';probe(carrier_probes,'shape-valid-overclaimed-ceiling',x,cv,True)
 for location in ['root','payload']:
  x=copy.deepcopy(fixture);(x if location=='root' else x['payload'])['implicit_authority']='hyp:claimed';probe(carrier_probes,'extra-'+location+'-field-rejected',x,cv,False)
 x=copy.deepcopy(fixture);x['authority_effect']='canonical';probe(carrier_probes,'governing-effect-rejected',x,cv,False)
 x=copy.deepcopy(fixture);x['kind']='failure-assessment';probe(carrier_probes,'collapsed-neighbor-kind-rejected',x,cv,False)
 x=copy.deepcopy(fixture);x['relation_refs']=[];probe(carrier_probes,'empty-relations-rejected',x,cv,False)
 for i in range(5):probe(carrier_probes,'retained-hostile-'+str(i),docs['hostile_'+str(i)],cv,False)
 products=[];rp=schema['properties']['relation_refs']['items']['properties']
 for kind,direction,counterpart in itertools.product(rp['relation_kind_ref']['enum'],rp['direction']['enum'],rp['counterpart_kind']['enum']):
  x=copy.deepcopy(fixture);x['relation_refs'][0].update(relation_kind_ref=kind,direction=direction,counterpart_kind=counterpart);assert not list(cv.iter_errors(x));products.append({'relation_kind_ref':kind,'direction':direction,'counterpart_kind':counterpart,'schema_accepted':True,'declared_role_member':(kind,direction,counterpart) in allowed,'actual_comparison_cause_severity_or_authority_verified':False})
 assert len(products)==132 and len(allowed)==12 and sum(not x['declared_role_member'] for x in products)==120
 current_errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in b.c.Draft202012Validator(docs['current_Definition_schema']).iter_errors(original)];inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(x) for x in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']]
 report={'schema_version':'definition-assurance-DriftAssessment-profile/v1-candidate','status':'PASS-for-qualified-comparison-hypotheses-and-actual-C70-shape-role-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_comparison_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'direct_carrier_admission_ref':carrier['admission_decision_ref'],'direct_carrier_semantic_ref':carrier['semantic_definition_refs'][0],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'Definition_schema_probes':definition_probes,'direct_carrier_schema_probes':carrier_probes,'role_schema_product_probes':products,'role_schema_product_count':132,'declared_role_product_members':12,'schema_accepted_but_role_invalid_products':120,'pure_role_surface_observer_executed':True,'pure_carrier_projection_functions_executed':True,'pure_carrier_projection_observations':{'artifact_bytes':len(a1),'artifact_sha256':b.r.digest(a1),'fixture_bytes':len(f1),'fixture_sha256':b.r.digest(f1)},'historical_source_current_Definition_shape':{'errors':current_errors,'exact_source_admission_invalidated':False},'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_comparison_cause_severity_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified declared exact-time dimensional comparison hypotheses plus actual C70 direct carrier/Definition shape,pure role and pure projection observations.132schema products include12declared roles and120outside the role surface. Shape does not establish time/values/evidence adequacy,cause,severity,failure,correction authority or actual comparison validity. No package validator,carrier writer,live consumer,new authority,accepted fidelity or whole proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_comparison_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_comparison_frames']),'catalog_checks':x['actual_check_count'],'Definition_probes':len(x['Definition_schema_probes']),'Definition_acceptances':sum(y['schema_accepted'] for y in x['Definition_schema_probes']),'carrier_probes':len(x['direct_carrier_schema_probes']),'carrier_acceptances':sum(y['schema_accepted'] for y in x['direct_carrier_schema_probes']),'role_schema_products':132,'declared_role_members':12,'schema_accepted_but_role_invalid':120},indent=2))
if __name__=='__main__':main()

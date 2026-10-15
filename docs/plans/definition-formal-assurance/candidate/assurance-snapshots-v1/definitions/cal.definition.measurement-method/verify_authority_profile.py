"""Qualified Method hypotheses and actual current C70 residue-entropy carrier observations."""
import copy,itertools,json,types
import build_candidate as b
import verifier as v
AXES=['identity','kind','source','Definition_context','property','procedure','subject_conditions','tools_implementation','calibration','reproducibility','uncertainty','evidence_failure','owner','version']
FORBIDDEN=['Method_is_Result','schema_proves_physical_calibration','criterion_is_actual_reproducibility','specification_forces_execution','specification_forces_result','schema_is_source_owner_fidelity','carrier_admission_is_instance_authority','residue_only_carrier_is_all_Method_meaning','procedure_text_change_proves_revision','distinct_version_proves_admission','latest_live_tool_version_required','opaque_handles_authenticate_subject','theorem_label_is_proof','authority_treatment_is_authority','C66_Definition_admits_carrier','C70_carrier_activates_consumer']
MAP_FIELDS=['one_property','version','procedure','subject_specification','conditions','units','Tool_or_instrument','Implementation','calibration_contract_and_state','sampling','computation','uncertainty','evidence','applicability','owner_route','failure_contract','reproducibility_criterion','execution_bindings','version_change']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['changed-binding:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_Method_truth_adequacy_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-bounded-conclusion-with-separate-Result',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('flat-carrier-with-explicit-unaccepted-source-residue',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','claim_scope_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'sibling_assignment_declared':True,'explicit_sibling_ref':'hyp:separate-target','residue_only_carrier_claimed_complete_general_Method':False,'carrier_labels_prove_version_or_reproducibility':False};rows=[]
 def qualified(x):x.update(full_alignment_claimed=True,accepted_map_refs={n:'hyp:map:'+n for n in MAP_FIELDS},owner_review_ref='hyp:owner',claim_scope_ref='hyp:scope')
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('changed-qualification')
  if x['selected']:
   errors+=['lost-obligation:'+n for n in MAP_FIELDS if not x['map_fields'].get(n)]
   if x['source_role_collapsed']:errors.append('Method-Result-Definition-role-collapse')
   if x['sibling_assignment_declared'] and not x['explicit_sibling_ref']:errors.append('missing-explicit-sibling-ref')
   if x['residue_only_carrier_claimed_complete_general_Method']:errors.append('unaccepted-residue-only-source-map')
   if x['carrier_labels_prove_version_or_reproducibility']:errors.append('shape-does-not-prove-version-reproducibility')
   if x['full_alignment_claimed']:
    errors+=['missing-accepted-map:'+n for n in MAP_FIELDS if not x['accepted_map_refs'].get(n)]
    if not x['owner_review_ref'] or not x['claim_scope_ref']:errors.append('missing-owner-review-or-scope')
  if x['actual_outcome_claimed']:errors.append('hypothesis-or-shape-does-not-prove-truth-adequacy-authority')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_Method_truth_adequacy_or_authority_verified':False,'universal_source_to_carrier_mapping_proof':False})
 add('proposed-full-source-map-without-acceptance',lambda x:None,False)
 add('narrow-carrier-with-explicit-Result-residue',lambda x:x['map_fields'].update({n:'explicit-source-residue' for n in MAP_FIELDS[5:]}),False)
 add('no-sibling-assignment',lambda x:x.update(sibling_assignment_declared=False,explicit_sibling_ref=''),False)
 add('outside-selected-map-scope',lambda x:x.update(selected=False,map_fields={},source_role_collapsed=True),False)
 add('hypothetically-referenced-map-not-actual-review',qualified,False)
 for n in AXES:add('changed-binding-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in MAP_FIELDS:
  add('lost-obligation-'+n,lambda x,n=n:x['map_fields'].pop(n),True)
  def missing(x,n=n):qualified(x);x['accepted_map_refs'][n]=''
  add('missing-accepted-map-'+n,missing,True)
 add('shape-claimed-full-fidelity',lambda x:x.update(full_alignment_claimed=True),True)
 for n in ['owner_review_ref','claim_scope_ref']:
  def missing(x,n=n):qualified(x);x[n]=''
  add('missing-'+n,missing,True)
 for n in ['source_role_collapsed','residue_only_carrier_claimed_complete_general_Method','carrier_labels_prove_version_or_reproducibility','actual_outcome_claimed']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 add('missing-sibling-ref',lambda x:x.update(explicit_sibling_ref=''),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert len(direct)==1;carrier=direct[0];ap=b.ROOT/carrier['artifact_path'];artifact=json.loads(ap.read_bytes())
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','direct_artifact':ap,'direct_schema':b.ROOT/carrier['schema_path'],'direct_fixture':ap.parent/artifact['validation_contract']['positive_witness'],'bound_package_validator_source':b.ROOT/artifact['validation_contract']['shared_validator_path'],'carrier_generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'artifact_projection':ap.with_name('ARTIFACT.md'),'fixture_projection':ap.parent/artifact['validation_contract']['positive_projection'],'checker':b.UNIT/'verify_authority_profile.py'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['hostile_'+str(i)]=ap.parent/n
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];schema=docs['direct_schema'];b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(schema);dv=b.c.Draft202012Validator(ds);cv=b.c.Draft202012Validator(schema);generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('catalog143rows121current',len(rows)==143 and len(current)==121)
 ck('direct-current-Method-v1-C70',carrier['artifact_type_ref']=='cal.artifact-type.measurement-method/v1' and carrier['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('direct-exact-selected-meaning',carrier['semantic_definition_refs']==artifact['semantic_definition_refs']==[source['version_ref']])
 ck('exact-artifact-schema-bytes',refs['direct_artifact']['sha256']==carrier['artifact_sha256']=='96a25b42ea259e7175136b25dd96be2b26208dd5e1d622f76b84827fb5cb87f1' and refs['direct_schema']['sha256']==carrier['schema_sha256']==artifact['schema_digest']=='c7182a5ad0e48bfd417159a7e59eddadfc9ce9203af4976a6bf0765e932c76f0')
 binding=artifact['semantic_definition_bindings'][0];ck('exact-C66-positive-Definition-binding',binding['path']==source['path'] and binding['sha256']==source['sha256'] and binding['definition_ref']==source['version_ref'] and binding['admission_decision_ref']=='CAL-DECISION-0066-DEFINITION-SPECIALIZATION-RESOLUTION-ADMISSION')
 ck('type-retains-candidate-none',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none')
 ck('closed24root23declared-semantic-fields',schema['additionalProperties'] is False and len(schema['required'])==24 and len(artifact['instance_contract']['required_semantic_fields'])==23 and set(schema['required'])==set(artifact['instance_contract']['required_semantic_fields'])|{'status','authority_effect'} and set(schema['properties'])==set(schema['required']))
 ck('exact-kind-discriminator',carrier['instance_discriminator']=={'path':'/kind','value':'measurement-method'} and schema['properties']['kind']['const']=='measurement-method')
 ck('residue-entropy-only-carrier',schema['properties']['property']['const']=='residue entropy' and 'other governed properties' in docs['source']['boundaries'][0])
 absent=['method_version','subject_specification','tools','implementation_ref','calibration','sampling','computation','evidence_refs','applicability','failure_contract','reproducibility_criterion','execution_bindings','version_change'];ck('thirteen-general-Method-obligations-without-direct-fields',all(x not in schema['properties'] for x in absent))
 ck('conditions-nonempty-unique-bounded',schema['properties']['conditions']['minItems']==1 and schema['properties']['conditions']['maxItems']==100 and schema['properties']['conditions']['uniqueItems'] is True)
 ck('claim-and-authority-labels-only',schema['properties']['claim_status']['enum']==['theorem','conjecture','analogy','review'] and schema['properties']['authority_treatment']['enum']==['non-governing','advisory','governed-by-separate-decision'])
 ck('three-observables-five-registers-five-scopes',len(schema['properties']['observable_kind']['enum'])==3 and len(schema['properties']['entropy_register']['enum'])==len(schema['properties']['scope_kind']['enum'])==5)
 ck('four-hostile-witnesses',len(artifact['validation_contract']['negative_witnesses'])==4)
 ck('generator-exact-bound',refs['carrier_generator']['sha256']==artifact['source_direction']['shared_generator_sha256'])
 ck('package-validator-source-bound-not-executed',refs['bound_package_validator_source']['sha256']==artifact['validation_contract']['shared_validator_sha256'])
 ck('current-generic-Definition-separate',len(generic)==1 and generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('historical-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows))
 ck('selected-C66-Definition-source-posture-valid',not list(dv.iter_errors(docs['source'])) and docs['source']['source_refs'][0]['source_admission_ref'] is None and load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0066-DEFINITION-SPECIALIZATION-RESOLUTION-ADMISSION')
 module=types.ModuleType('_pure_Method_carrier_projection');exec(compile(paths['carrier_generator'].read_bytes(),str(paths['carrier_generator']),'exec'),module.__dict__);before=copy.deepcopy(docs['direct_fixture']);a1=module.render_artifact(artifact).encode();a2=module.render_artifact(artifact).encode();f1=module.render_instance(artifact,before).encode();f2=module.render_instance(artifact,before).encode();ck('two-pure-artifact-fixture-projections',a1==a2==paths['artifact_projection'].read_bytes() and f1==f2==paths['fixture_projection'].read_bytes() and before==docs['direct_fixture'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];carrier_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected shape '+id+' '+str(errors))
  bucket.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_calibration_reproducibility_execution_result_or_authority_verified':False})
 original=docs['source'];probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-root-'+n,x,dv,False)
 for n in ['method_version','calibration','sampling','execution_bindings']:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'unresolved-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:Method schema proves actual calibration and results';probe(definition_probes,'overclaimed-text-shape-valid',x,dv,True)
 fixture=docs['direct_fixture'];probe(carrier_probes,'exact-current-fixture',copy.deepcopy(fixture),cv,True)
 def mutate(id,expected,fn):
  x=copy.deepcopy(fixture);fn(x);probe(carrier_probes,id,x,cv,expected)
 for n in schema['required']:mutate('missing-root-'+n,False,lambda x,n=n:x.pop(n))
 for n in ['challenge_route','claim_ceiling','interpretation','mathematical_reading','name','node_id','owner_ref','owner_route','procedure','residue_type_ref','scope_ref','source_operation_ref','uncertainty_rule','unit']:
  for label,value,accept in [('empty','',False),('whitespace','   ',False),('unresolved','hyp:unresolved',True)]:mutate(n+'-'+label,accept,lambda x,n=n,value=value:x.update({n:value}))
 for label,value,accept in [('empty',[],False),('unresolved',['hyp:unresolved'],True),('whitespace',['   '],False),('duplicate',['hyp:ref','hyp:ref'],False),('too-many',['hyp:'+str(i) for i in range(101)],False),('hundred-unresolved',['hyp:'+str(i) for i in range(100)],True)]:mutate('conditions-'+label,accept,lambda x,value=value:x.update(conditions=value))
 for n in ['payload','relation_refs','derived_authority',*absent]:mutate('extra-'+n,False,lambda x,n=n:x.update({n:'hyp:claimed'}))
 for n,value in [('authority_effect','canonical'),('status','admitted'),('kind','measurement-result'),('property','temperature'),('claim_status','proof-complete'),('authority_treatment','governing'),('entropy_register','unbounded'),('observable_kind','raw-number'),('scope_kind','any-subject')]:mutate('changed-'+n,False,lambda x,n=n,value=value:x.update({n:value}))
 mutate('temperature-method-allowed-source-rejected-carrier',False,lambda x:x.update(property='temperature',unit='kelvin'))
 mutate('overclaimed-procedure-and-ceiling-shape-valid',True,lambda x:x.update(procedure='hyp:declared Method guarantees correctly calibrated accepted results',claim_ceiling='hyp:complete fidelity and theorem proof verified'))
 mutate('arbitrary-unit-and-formula-shape-valid',True,lambda x:x.update(unit='hyp:incompatible-unit',mathematical_reading='hyp:unverified incompatible formula'))
 for i in range(4):probe(carrier_probes,'retained-hostile-'+str(i),docs['hostile_'+str(i)],cv,False)
 labels=[]
 for claim,authority in itertools.product(schema['properties']['claim_status']['enum'],schema['properties']['authority_treatment']['enum']):
  x=copy.deepcopy(fixture);x.update(claim_status=claim,authority_treatment=authority);assert not list(cv.iter_errors(x));labels.append({'claim_status':claim,'authority_treatment':authority,'schema_accepted':True,'theorem_or_authority_verified':False})
 observables=[]
 for observable,register,scope in itertools.product(schema['properties']['observable_kind']['enum'],schema['properties']['entropy_register']['enum'],schema['properties']['scope_kind']['enum']):
  x=copy.deepcopy(fixture);x.update(observable_kind=observable,entropy_register=register,scope_kind=scope);assert not list(cv.iter_errors(x));observables.append({'observable_kind':observable,'entropy_register':register,'scope_kind':scope,'schema_accepted':True,'formula_units_register_scope_semantic_consistency_verified':False})
 current_errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in b.c.Draft202012Validator(docs['current_Definition_schema']).iter_errors(original)];inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']]
 report={'schema_version':'definition-assurance-MeasurementMethod-profile/v1-candidate','status':'PASS-for-qualified-Method-hypotheses-and-actual-C70-residue-entropy-shape-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_comparison_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'direct_carrier_admission_ref':carrier['admission_decision_ref'],'direct_carrier_semantic_ref':carrier['semantic_definition_refs'][0],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'Definition_schema_probes':definition_probes,'direct_carrier_schema_probes':carrier_probes,'claim_authority_label_products':labels,'observable_register_scope_products':observables,'source_map_obligations':MAP_FIELDS,'carrier_source_breadth_gap':{'source':'one declared property including residue or other governed properties','carrier':'property fixed to residue entropy;closed flat24root23declared semantic fields','accepted_correspondence_ref':None,'general_obligations_without_direct_fields':absent},'current_Definition_v2_comparison':{'schema_accepted':not current_errors,'errors':current_errors,'selected_Definition_v1_admission_invalidated':False},'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_calibration_reproducibility_execution_result_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified Method hypotheses and actual current C70 residue-entropy-only carrier schema/pure projections. The positive Definition is broader and13general obligations lack direct fields. Twelve claim/authority and75observable/register/scope products are shape-valid without actual proof or compatibility. No accepted source/carrier map,calibration,reproducibility,execution,result,authority,writer,consumer or whole proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh Method profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_comparison_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_comparison_frames']),'catalog_checks':x['actual_check_count'],'Definition_probes':len(x['Definition_schema_probes']),'Definition_acceptances':sum(y['schema_accepted'] for y in x['Definition_schema_probes']),'carrier_probes':len(x['direct_carrier_schema_probes']),'carrier_acceptances':sum(y['schema_accepted'] for y in x['direct_carrier_schema_probes']),'claim_authority_products':len(x['claim_authority_label_products']),'observable_register_scope_products':len(x['observable_register_scope_products'])},indent=2))
if __name__=='__main__':main()

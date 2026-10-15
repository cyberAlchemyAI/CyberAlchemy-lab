"""Qualified Review hypotheses and separate current C70 carrier observations."""
import copy,itertools,json,types
import build_candidate as b
import verifier as v
AXES=['identity','kind','source','Definition_context','exact_subject_versions','questions','criteria','evidence','alternatives','claim_ceiling','attribution','scope','context','use_version','Decision','effect_kind','contract','grant']
FORBIDDEN=['Review_is_Evaluation','Review_is_Finding','Review_is_Decision','assessment_is_approval','assessment_is_admission','assessment_is_validation','Fact_label_is_truth','reviewer_ref_authenticates_person','subject_ref_authenticates_exact_revision','profile_ref_proves_questions_criteria_alternatives','finding_ref_proves_adequacy','nonempty_claim_ceiling_proves_support','Decision_ref_proves_grant','contract_ref_authenticates_admission','shape_is_actual_assessment','carrier_is_full_Source_meaning','C65_Definition_admits_carrier','C70_carrier_activates_consumer']
MAP_FIELDS=['exact_subject_versions','questions','criteria','evidence','alternatives','claim_ceiling','attribution','bounded_scope','context','governed_identity_or_record','exact_or_admitted_successor_use','applicability_and_exclusions','separate_Decision','effect_kind','separate_contract','exact_grant_binding','effect_record','actual_outcome_independence','no_term_only_authority','consumer_correspondence']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['changed-binding:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_Review_assessment_grant_truth_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-bounded-conclusion-with-separate-Review',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('flat-carrier-with-explicit-unaccepted-source-residue',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','claim_scope_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'sibling_assignment_declared':True,'explicit_sibling_ref':'hyp:separate-target','Review_carrier_claimed_full_bounded_source':False,'nonempty_reference_proves_authenticity':False};rows=[]
 def qualified(x):x.update(full_alignment_claimed=True,accepted_map_refs={n:'hyp:map:'+n for n in MAP_FIELDS},owner_review_ref='hyp:owner',claim_scope_ref='hyp:scope')
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('changed-qualification')
  if x['selected']:
   errors+=['lost-obligation:'+n for n in MAP_FIELDS if not x['map_fields'].get(n)]
   if x['source_role_collapsed']:errors.append('Review-Evaluation-Finding-Decision-role-collapse')
   if x['sibling_assignment_declared'] and not x['explicit_sibling_ref']:errors.append('missing-explicit-sibling-ref')
   if x['Review_carrier_claimed_full_bounded_source']:errors.append('unaccepted-residue-only-source-map')
   if x['nonempty_reference_proves_authenticity']:errors.append('nonempty-reference-does-not-prove-authenticity')
   if x['full_alignment_claimed']:
    errors+=['missing-accepted-map:'+n for n in MAP_FIELDS if not x['accepted_map_refs'].get(n)]
    if not x['owner_review_ref'] or not x['claim_scope_ref']:errors.append('missing-owner-review-or-scope')
  if x['actual_outcome_claimed']:errors.append('hypothesis-or-shape-does-not-prove-truth-adequacy-authority')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_Review_assessment_grant_truth_or_authority_verified':False,'universal_source_to_carrier_mapping_proof':False})
 add('proposed-full-source-map-without-acceptance',lambda x:None,False)
 add('narrow-carrier-with-explicit-Review-residue',lambda x:x['map_fields'].update({n:'explicit-source-residue' for n in MAP_FIELDS[5:]}),False)
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
 for n in ['source_role_collapsed','Review_carrier_claimed_full_bounded_source','nonempty_reference_proves_authenticity','actual_outcome_claimed']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 add('missing-sibling-ref',lambda x:x.update(explicit_sibling_ref=''),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);source=load('t.json')['payload']['source'];runtime=v.f.current_bindings();rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert len(direct)==1;carrier=direct[0];ap=b.ROOT/carrier['artifact_path'];artifact=json.loads(ap.read_bytes())
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','direct_artifact':ap,'direct_schema':b.ROOT/carrier['schema_path'],'direct_fixture':ap.parent/artifact['validation_contract']['positive_witness'],'bound_package_validator_source':b.ROOT/artifact['validation_contract']['shared_validator_path'],'carrier_generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'artifact_projection':ap.with_name('ARTIFACT.md'),'fixture_projection':ap.parent/artifact['validation_contract']['positive_projection'],'checker':b.UNIT/'verify_authority_profile.py'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['hostile_'+str(i)]=ap.parent/n
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];schema=docs['direct_schema'];b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(schema);dv=b.c.Draft202012Validator(ds);cv=b.c.Draft202012Validator(schema);generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('catalog143rows121current',len(rows)==143 and len(current)==121)
 ck('direct-current-Review-v1-C70',carrier['artifact_type_ref']=='cal.artifact-type.review/v1' and carrier['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('direct-exact-selected-meaning',carrier['semantic_definition_refs']==artifact['semantic_definition_refs']==[source['version_ref']])
 ck('exact-artifact-schema-bytes',refs['direct_artifact']['sha256']==carrier['artifact_sha256']=='676385f67759798f51eff82e8d8123199565b7077d1a03822b7f5a87ee077d13' and refs['direct_schema']['sha256']==carrier['schema_sha256']==artifact['schema_digest']=='4b11503db405a76bde3e38b54f4f353ac1cebe2c4d9b1d7dd5a047520da97f69')
 binding=artifact['semantic_definition_bindings'][0];ck('exact-C65-positive-Definition-binding',binding['path']==source['path'] and binding['sha256']==source['sha256'] and binding['definition_ref']==source['version_ref'] and binding['admission_decision_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION')
 ck('embedded-candidate-none-versus-current-admission-overlay',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none' and carrier['lifecycle_state']=='admitted-current')
 ck('closed14root-semantic-fields',schema['additionalProperties'] is False and len(schema['required'])==14 and set(schema['required'])==set(schema['properties'])==set(artifact['instance_contract']['required_semantic_fields']))
 ck('exact-schema-discriminator-and-kind',carrier['instance_discriminator']=={'path':'/schema_version','value':'cyberalchemy-lab-review/v1'} and schema['properties']['schema_version']['const']=='cyberalchemy-lab-review/v1' and schema['properties']['kind']['const']=='review')
 payload=schema['properties']['payload'];ck('closed5payload-fields',payload['additionalProperties'] is False and set(payload['required'])==set(payload['properties'])=={'subject_ref','review_profile_ref','reviewer_refs','finding_refs','disposition'})
 absent=['subject_versions','exact_revision','questions','criteria','alternatives','context_ref','definition_version_ref','decision_ref','effect_kind','contract_ref','decision_grant_ref'];ck('eleven-obligations-without-dedicated-root-or-payload-fields',all(n not in schema['properties'] and n not in payload['properties'] for n in absent))
 ck('subject-profile-disposition-opaque-nonempty',all(payload['properties'][n]=={'minLength':1,'type':'string'} for n in ['subject_ref','review_profile_ref','disposition']))
 ck('reviewer-finding-collections-nonempty-unique',all(payload['properties'][n]['minItems']==1 and payload['properties'][n]['uniqueItems'] is True for n in ['reviewer_refs','finding_refs']))
 ck('evidence-and-successor-empty-collections-allowed',all('minItems' not in schema['properties'][n] and schema['properties'][n]['uniqueItems'] is True for n in ['evidence_refs','successor_refs']))
 rel=schema['properties']['relation_refs'];ck('exact-target-context-frames-role',rel['minItems']==1 and rel['items']['additionalProperties'] is False and {n:rel['items']['properties'][n]['enum'] for n in ['direction','counterpart_kind','relation_kind_ref']}=={'direction':['target'],'counterpart_kind':['context'],'relation_kind_ref':['relation.frames']} and artifact['relation_roles']==[{'counterpart_kinds':['context'],'direction':'target','relation_kind_ref':'relation.frames'}])
 ck('relation-array-does-not-require-unique-items','uniqueItems' not in rel)
 ck('authority-none-in-this-carrier-contract',schema['properties']['authority_effect']=={'const':'none'})
 ck('lifecycle-labels-have-no-activation-proof',schema['properties']['lifecycle_state']['enum']==['candidate','active','historical','retired'])
 ck('five-hostile-witnesses',len(artifact['validation_contract']['negative_witnesses'])==5)
 ck('generator-exact-bound',refs['carrier_generator']['sha256']==artifact['source_direction']['shared_generator_sha256'])
 ck('package-validator-source-bound-not-executed',refs['bound_package_validator_source']['sha256']==artifact['validation_contract']['shared_validator_sha256'])
 ck('current-generic-Definition-separate',len(generic)==1 and generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('historical-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows))
 ck('selected-C65-Definition-source-posture-valid',not list(dv.iter_errors(docs['source'])) and docs['source']['source_refs'][0]['source_admission_ref'] is None and load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION')
 module=types.ModuleType('_pure_Review_carrier_projection');exec(compile(paths['carrier_generator'].read_bytes(),str(paths['carrier_generator']),'exec'),module.__dict__);before=copy.deepcopy(docs['direct_fixture']);a1=module.render_artifact(artifact).encode();a2=module.render_artifact(artifact).encode();f1=module.render_instance(artifact,before).encode();f2=module.render_instance(artifact,before).encode();ck('two-pure-artifact-fixture-projections',a1==a2==paths['artifact_projection'].read_bytes() and f1==f2==paths['fixture_projection'].read_bytes() and before==docs['direct_fixture'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];carrier_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected shape '+id+' '+str(errors))
  bucket.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_assessment_adequacy_authentic_grant_truth_validation_execution_or_authority_verified':False})
 original=docs['source'];probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-root-'+n,x,dv,False)
 for n in ['subject_ref','review_profile_ref','reviewer_refs','disposition']:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'unresolved-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:Review schema proves authentic approval and truth';probe(definition_probes,'overclaimed-text-shape-valid',x,dv,True)
 fixture=docs['direct_fixture'];probe(carrier_probes,'exact-current-fixture',copy.deepcopy(fixture),cv,True)
 def mutate(id,expected,fn):
  x=copy.deepcopy(fixture);fn(x);probe(carrier_probes,id,x,cv,expected)
 for k in schema['required']:
  mutate('missing-root-'+k,False,lambda x,k=k:x.pop(k));mutate('null-root-'+k,False,lambda x,k=k:x.update({k:None}))
 for k in payload['required']:
  mutate('missing-payload-'+k,False,lambda x,k=k:x['payload'].pop(k));mutate('null-payload-'+k,False,lambda x,k=k:x['payload'].update({k:None}))
 for k in ['node_id','name','owner_ref','scope_ref','challenge_route','claim_ceiling']:
  mutate('empty-'+k,False,lambda x,k=k:x.update({k:''}));mutate('whitespace-'+k,True,lambda x,k=k:x.update({k:' '}));mutate('unresolved-'+k,True,lambda x,k=k:x.update({k:'hyp:unresolved'}))
 for k in ['subject_ref','review_profile_ref','disposition']:
  mutate('empty-payload-'+k,False,lambda x,k=k:x['payload'].update({k:''}));mutate('whitespace-payload-'+k,True,lambda x,k=k:x['payload'].update({k:' '}));mutate('unresolved-payload-'+k,True,lambda x,k=k:x['payload'].update({k:'hyp:unresolved'}))
 for k in ['reviewer_refs','finding_refs']:
  for label,val,accepted in [('empty',[],False),('empty-item',[''],False),('whitespace',[' '],True),('duplicate',['hyp:x','hyp:x'],False),('unresolved',['hyp:unresolved'],True)]:mutate(label+'-'+k,accepted,lambda x,k=k,val=val:x['payload'].update({k:val}))
 for k in ['evidence_refs','successor_refs']:
  mutate('empty-'+k,True,lambda x,k=k:x.update({k:[]}));mutate('duplicate-'+k,False,lambda x,k=k:x.update({k:['hyp:x','hyp:x']}))
 for k in absent:mutate('unsupported-explicit-payload-'+k,False,lambda x,k=k:x['payload'].update({k:'hyp:claimed'}))
 for k in artifact['instance_contract']['forbidden_canonical_fields']:mutate('forbidden-root-'+k,False,lambda x,k=k:x.update({k:'hyp:claimed'}))
 mutate('empty-relations',False,lambda x:x.update(relation_refs=[]));mutate('duplicate-context-relations',True,lambda x:x['relation_refs'].append(copy.deepcopy(x['relation_refs'][0])))
 for k,val in [('direction','source'),('counterpart_kind','decision'),('relation_kind_ref','relation.admits')]:mutate('undeclared-relation-'+k,False,lambda x,k=k,val=val:x['relation_refs'][0].update({k:val}))
 mutate('unresolved-context-reference',True,lambda x:x['relation_refs'][0].update(counterpart_ref='hyp:unresolved'));mutate('unversioned-subject-reference',True,lambda x:x['payload'].update(subject_ref='hyp:subject-with-no-revision'))
 for value in ['admission','approval','validation','fact','execution','ready-for-decision','all-proofs-complete']:mutate('opaque-disposition-'+value,True,lambda x,value=value:x['payload'].update(disposition=value))
 for value in schema['properties']['lifecycle_state']['enum']:mutate('lifecycle-'+value,True,lambda x,value=value:x.update(lifecycle_state=value))
 for value in ['admitted','approved','valid']:mutate('unsupported-lifecycle-'+value,False,lambda x,value=value:x.update(lifecycle_state=value))
 for value in ['admission','authority','validation','execution']:mutate('carrier-cannot-claim-authority-effect-'+value,False,lambda x,value=value:x.update(authority_effect=value))
 for value in artifact['hostile_non_collapse']:mutate('neighbor-kind-'+value,False,lambda x,value=value:x.update(kind=value))
 mutate('overclaimed-ceiling-is-shape-valid',True,lambda x:x.update(claim_ceiling='hyp:assessment proves approval admission validation truth and execution'))
 for i in range(5):probe(carrier_probes,'canonical-hostile-'+str(i),docs['hostile_'+str(i)],cv,False)
 current_errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in b.c.Draft202012Validator(docs['current_Definition_schema']).iter_errors(original)];inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']]
 report={'schema_version':'definition-assurance-Review-profile/v1-candidate','status':'PASS-for-qualified-Review-hypotheses-and-actual-C70-carrier-shape-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_comparison_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'direct_carrier_admission_ref':carrier['admission_decision_ref'],'direct_carrier_semantic_ref':carrier['semantic_definition_refs'][0],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'Definition_schema_probes':definition_probes,'direct_carrier_schema_probes':carrier_probes,'source_map_obligations':MAP_FIELDS,'carrier_source_record_gap':{'source':'attributable bounded assessment of exact subject versions against questions criteria evidence alternatives and a claim ceiling;conditional separate Decision effects','carrier':'closed14root5payload Review carrier with opaque subject/profile/reviewer/finding/disposition references and target-context frames','accepted_correspondence_ref':None,'obligations_without_dedicated_fields':absent,'fields_in_external_profile_or_other_references_accepted_map':None},'current_Definition_v2_comparison':{'schema_accepted':not current_errors,'errors':current_errors,'selected_Definition_v1_admission_invalidated':False},'accepted_source_to_carrier_or_consumer_map_refs':[],'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_assessment_adequacy_authentic_grants_truth_validation_execution_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified Review hypotheses and exact current C70 carrier schema/pure projections. Eleven obligations have no dedicated root/payload field;external profile/reference maps remain unaccepted. Opaque disposition text and lifecycle labels do not prove actual grants,approval,truth,assessment adequacy,activation or authority. No accepted correspondence,writer,consumer or whole proof.'}
 b.unchanged(list(refs.values())+context['sources']+inputs+bindings);b.r.verify(snap,b.ROOT)
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh Review profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_comparison_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_comparison_frames']),'catalog_checks':x['actual_check_count'],'Definition_probes':len(x['Definition_schema_probes']),'Definition_acceptances':sum(y['schema_accepted'] for y in x['Definition_schema_probes']),'carrier_probes':len(x['direct_carrier_schema_probes']),'carrier_acceptances':sum(y['schema_accepted'] for y in x['direct_carrier_schema_probes'])},indent=2))
if __name__=='__main__':main()

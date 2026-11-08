"""Qualified Evidence Set carrier/source-map hypotheses and exact current C70 shape,role and projection observations."""
import ast,copy,itertools,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['identity','kind','carrier','source','definition_context','topic','question_claim_projection','scope','project','goal_links','sources','observations','method','support_items','counter_items','limitations','freshness','applicability','findings_refs','created_updated','owner_challenge_routes','sibling_references','relation_roles']
FORBIDDEN=['aggregate_is_findings','aggregate_is_decision','classification_is_Definition_authority','promotion_is_authority','handles_are_provenance_authentication','freshness_ref_is_currentness','coverage_text_is_adequacy','aggregate_fields_force_nonempty_all_sets','support_counter_are_disjoint','question_claim_automatically_equal','created_updated_refs_imply_chronological_order','ephemeral_is_deletion_policy','sibling_ref_is_actual_adoption','carrier_admission_is_instance_admission','schema_is_full_Source_semantics','relation_enum_is_role_admission','C12_selection_is_C53_C70_or_owner_fidelity','nonentailment_denies_real_supported_outcomes']
MAP_FIELDS=['question_or_claim','project','goals','sources','observations','method','supporting','counterevidence','limitations','freshness','applicability','findings','created','last_updated','owner_route','challenge_route','scope','definition_context','sibling_references']
RICH_PAYLOAD_FIELDS=['question_ref','claim_ref','project_ref','goal_refs','observation_refs','method_ref','counterevidence_refs','freshness_ref','applicability_ref','findings_refs','created','last_updated','owner_route']
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['binding-changed:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_investigation_finding_truth_adequacy_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-normalized-source-qualified-research-aggregate',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('explicit-carrier-source-residue-without-alignment-claim',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-correspondence-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','claim_scope_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'sibling_assignment_declared':True,'explicit_sibling_ref':'hyp:separate-finding','outside_declared_relation_role':False};rows=[]
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('changed-qualification-needs-independent-review')
  if x['selected']:
   for n in MAP_FIELDS:
    if n not in x['map_fields'] or not x['map_fields'][n]:errors.append('lost-source-obligation:'+n)
   if x['sibling_assignment_declared'] and not x['explicit_sibling_ref']:errors.append('sibling-assignment-without-explicit-reference')
   if x['source_role_collapsed']:errors.append('normalized-context-aggregate-finding-or-sibling-collapse')
   if x['outside_declared_relation_role']:errors.append('schema-enum-membership-does-not-qualify-role')
   if x['full_alignment_claimed']:
    if any(not x['accepted_map_refs'].get(n) for n in MAP_FIELDS):errors.append('full-alignment-without-all-accepted-map-refs')
    if not x['owner_review_ref'] or not x['claim_scope_ref']:errors.append('full-alignment-without-owner-and-claim-scope')
  if x['actual_outcome_claimed']:errors.append('hypothesis-or-shape-does-not-prove-investigation-truth-adequacy-or-authority')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_investigation_finding_truth_adequacy_or_authority_verified':False,'universal_source_to_carrier_mapping_proof':False})
 add('full-source-map-explicitly-proposed-without-acceptance',lambda x:None,False)
 add('narrow-carrier-fields-with-all-source-residue-visible',lambda x:x['map_fields'].update({n:'explicit-residue' for n in MAP_FIELDS if n not in ['sources','limitations','scope','challenge_route']}),False)
 add('no-sibling-assignment-does-not-require-ref',lambda x:x.update(sibling_assignment_declared=False,explicit_sibling_ref=''),False)
 add('outside-selected-alignment-scope',lambda x:x.update(selected=False,map_fields={},source_role_collapsed=True),False)
 def qualified(x):x.update(full_alignment_claimed=True,accepted_map_refs={n:'hyp:reviewed-map:'+n for n in MAP_FIELDS},owner_review_ref='hyp:owner-review',claim_scope_ref='hyp:scope')
 add('hypothetically-referenced-full-map-is-not-actual-owner-evidence',qualified,False)
 for n in AXES:add('changed-qualified-binding-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in MAP_FIELDS:
  add('lost-source-map-obligation-'+n,lambda x,n=n:x['map_fields'].pop(n),True)
  def missing(x,n=n):qualified(x);x['accepted_map_refs'][n]=''
  add('claimed-alignment-missing-accepted-map-'+n,missing,True)
 add('carrier-shape-claimed-full-fidelity',lambda x:x.update(full_alignment_claimed=True),True)
 for n in ['owner_review_ref','claim_scope_ref']:
  def missing(x,n=n):qualified(x);x[n]=''
  add('claimed-alignment-without-'+n,missing,True)
 add('sibling-assignment-without-explicit-ref',lambda x:x.update(explicit_sibling_ref=''),True)
 add('collapsed-finding-or-Definition-instance-role',lambda x:x.update(source_role_collapsed=True),True)
 add('schema-valid-outside-declared-relation-role',lambda x:x.update(outside_declared_relation_role=True),True)
 add('carrier-as-actual-investigation-truth-authority',lambda x:x.update(actual_outcome_claimed=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert len(direct)==1;carrier=direct[0];ap=b.ROOT/carrier['artifact_path'];artifact=json.loads(ap.read_bytes())
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','direct_artifact':ap,'direct_schema':b.ROOT/carrier['schema_path'],'direct_fixture':ap.parent/artifact['validation_contract']['positive_witness'],'relation_model':b.ROOT/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json','role_observer_source':b.ROOT/artifact['validation_contract']['shared_validator_path'],'carrier_generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'artifact_projection':ap.with_name('ARTIFACT.md'),'fixture_projection':ap.parent/artifact['validation_contract']['positive_projection'],'checker':b.UNIT/'verify_authority_profile.py'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['hostile_'+str(i)]=ap.parent/n
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];schema=docs['direct_schema'];b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(schema);dv=b.c.Draft202012Validator(ds);cv=b.c.Draft202012Validator(schema);generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121);ck('direct-current-EvidenceSet-v1-C70',carrier['artifact_type_ref']=='cal.artifact-type.evidence-set/v1' and carrier['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION');ck('direct-exact-current-Definition-meaning',carrier['semantic_definition_refs']==artifact['semantic_definition_refs']==[source['version_ref']]);ck('direct-artifact-schema-bytes-current',refs['direct_artifact']['sha256']==carrier['artifact_sha256'] and refs['direct_schema']['sha256']==carrier['schema_sha256']==artifact['schema_digest']);ck('direct-retained-body-candidate-none',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none');ck('direct-exact-C53-Definition-binding',artifact['semantic_definition_bindings'][0]['path']==source['path'] and artifact['semantic_definition_bindings'][0]['sha256']==source['sha256'] and artifact['semantic_definition_bindings'][0]['definition_ref']==source['version_ref'] and artifact['semantic_definition_bindings'][0]['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION');ck('closed14root4payload-source-item-coverage-limits',schema['additionalProperties'] is False and len(schema['required'])==14 and schema['properties']['payload']['additionalProperties'] is False and schema['properties']['payload']['required']==['source_refs','item_refs','coverage_statement','limitations']);ck('direct-exact-discriminator',schema['properties']['schema_version']['const']==carrier['instance_discriminator']['value']=='cyberalchemy-lab-evidence-set/v1');ck('current-generic-Definition-separate-meaning',len(generic)==1 and generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']]);ck('historical-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows));ck('selected-Definition-v1-shape-valid',not list(dv.iter_errors(docs['source'])));ck('C53-current-source-D61-split-and-retained-historical-posture',docs['source']['source_refs'][0]['admission_posture']=='candidate-unadmitted' and docs['source']['source_refs'][0]['source_admission_ref'] is None and load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and len(load('source-checks.json')['selected_source_sections'][0]['admission']['target_definition_refs'])==4);ck('pure-role-observer-source-bound',refs['role_observer_source']['sha256']==artifact['validation_contract']['shared_validator_sha256']);ck('pure-carrier-generator-source-bound',refs['carrier_generator']['sha256']==artifact['source_direction']['shared_generator_sha256'])
 model_assign=next(x for x in ast.parse(paths['role_observer_source'].read_bytes()).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RELATION_MODEL' for t in x.targets));assert isinstance(model_assign.value,ast.BinOp) and isinstance(model_assign.value.op,ast.Div) and isinstance(model_assign.value.left,ast.Name) and model_assign.value.left.id=='LAB' and isinstance(model_assign.value.right,ast.Constant);ck('validator-declared-relation-model-location-bound',model_assign.value.right.value==refs['relation_model']['path'])
 nodes=[x for x in ast.parse(paths['role_observer_source'].read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name=='expected_roles'];assert len(nodes)==1;ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['role_observer_source']),'exec'),ns);expected=ns['expected_roles']('evidence-set',docs['relation_model']);allowed={(x['relation_kind_ref'],x['direction'],k) for x in expected for k in x['counterpart_kinds']};ck('pure-role-surface-exact',artifact['relation_roles']==expected and artifact['allowed_relation_kinds']==sorted({x['relation_kind_ref'] for x in expected}));ck('four-orthogonality-rules-two-neighbors',len(artifact['orthogonality_rules'])==4 and artifact['hostile_non_collapse']==['finding','observation'])
 generator=types.ModuleType('_pure_evidence_set_carrier_projection');exec(compile(paths['carrier_generator'].read_bytes(),str(paths['carrier_generator']),'exec'),generator.__dict__);before=copy.deepcopy(docs['direct_fixture']);a1=generator.render_artifact(artifact).encode();a2=generator.render_artifact(artifact).encode();f1=generator.render_instance(artifact,before).encode();f2=generator.render_instance(artifact,before).encode();ck('two-pure-artifact-and-fixture-projections',a1==a2==paths['artifact_projection'].read_bytes() and f1==f2==paths['fixture_projection'].read_bytes() and before==docs['direct_fixture'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];carrier_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored shape probe '+id+' '+str(errors))
  row={'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_investigation_finding_truth_adequacy_or_authority_verified':False}
  if bucket is carrier_probes:row['declared_roles_satisfied']=all((x.get('relation_kind_ref'),x.get('direction'),x.get('counterpart_kind')) in allowed for x in doc.get('relation_refs',[]))
  bucket.append(row)
 original=docs['source'];probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-required-root-'+n,x,dv,False)
 for n in ['question_ref','counterevidence_refs','freshness_ref','findings_refs']:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'shape-does-not-resolve-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:PASS establishes admission and authority';probe(definition_probes,'shape-valid-overclaimed-text',x,dv,True)
 fixture=docs['direct_fixture'];probe(carrier_probes,'exact-current-direct-fixture',copy.deepcopy(fixture),cv,True)
 for n in schema['required']:
  x=copy.deepcopy(fixture);x.pop(n);probe(carrier_probes,'missing-root-'+n,x,cv,False)
 for n in schema['properties']['payload']['required']:
  x=copy.deepcopy(fixture);x['payload'].pop(n);probe(carrier_probes,'missing-payload-'+n,x,cv,False)
 for n in ['source_refs','item_refs','limitations']:
  for label,value,accept in [('unresolved',['hyp:unresolved'],True),('empty',[],False),('empty-member',[''],False),('duplicate',['hyp:member','hyp:member'],False),('whitespace-member',['   '],True)]:
   x=copy.deepcopy(fixture);x['payload'][n]=value;probe(carrier_probes,n+'-'+label,x,cv,accept)
 for value,accept,label in [('',False,'empty'),('   ',True,'whitespace'),('hyp:sufficient current findings and decision authority verified',True,'overclaimed')]:
  x=copy.deepcopy(fixture);x['payload']['coverage_statement']=value;probe(carrier_probes,'coverage-'+label,x,cv,accept)
 for n in ['node_id','owner_ref','scope_ref','challenge_route']:
  x=copy.deepcopy(fixture);x[n]='hyp:unresolved';probe(carrier_probes,'unresolved-root-'+n,x,cv,True)
 for n in RICH_PAYLOAD_FIELDS:
  x=copy.deepcopy(fixture);x['payload'][n]=['hyp:ref'] if n.endswith('refs') else 'hyp:ref';probe(carrier_probes,'source-rich-field-not-carrier-payload-'+n,x,cv,False)
 for location in ['root','payload']:
  x=copy.deepcopy(fixture);(x if location=='root' else x['payload'])['implicit_authority']='hyp:claimed';probe(carrier_probes,'extra-'+location+'-field-rejected',x,cv,False)
 x=copy.deepcopy(fixture);x['authority_effect']='canonical';probe(carrier_probes,'governing-effect-rejected',x,cv,False)
 for kind in ['finding','observation','research-inquiry','research-run']:
  x=copy.deepcopy(fixture);x['kind']=kind;probe(carrier_probes,'collapsed-neighbor-'+kind,x,cv,False)
 x=copy.deepcopy(fixture);x['evidence_refs']=[];probe(carrier_probes,'empty-root-evidence-permitted',x,cv,True)
 x=copy.deepcopy(fixture);x['relation_refs']=[];probe(carrier_probes,'empty-relations-rejected',x,cv,False)
 x=copy.deepcopy(fixture);x['lifecycle_state']='active';probe(carrier_probes,'active-label-does-not-authenticate-investigation',x,cv,True)
 x=copy.deepcopy(fixture);x['claim_ceiling']='hyp:actual proof adequacy source fidelity and authority verified';probe(carrier_probes,'overclaimed-ceiling-shape-valid',x,cv,True)
 x=copy.deepcopy(fixture);x['relation_refs'][0]['counterpart_ref']='hyp:unresolved';probe(carrier_probes,'unresolved-counterpart-ref-shape-valid',x,cv,True)
 x=copy.deepcopy(fixture);x['relation_refs'].append(copy.deepcopy(x['relation_refs'][0]));probe(carrier_probes,'duplicate-relations-shape-valid',x,cv,True)
 for i in range(5):probe(carrier_probes,'retained-hostile-'+str(i),docs['hostile_'+str(i)],cv,False)
 products=[];relation_properties=schema['properties']['relation_refs']['items']['properties']
 for kind,direction,counterpart in itertools.product(relation_properties['relation_kind_ref']['enum'],relation_properties['direction']['enum'],relation_properties['counterpart_kind']['enum']):
  x=copy.deepcopy(fixture);x['relation_refs'][0].update(relation_kind_ref=kind,direction=direction,counterpart_kind=counterpart);assert not list(cv.iter_errors(x));products.append({'relation_kind_ref':kind,'direction':direction,'counterpart_kind':counterpart,'schema_accepted':True,'declared_role_member':(kind,direction,counterpart) in allowed,'actual_investigation_finding_truth_adequacy_or_authority_verified':False})
 assert len(products)==42 and len(allowed)==8 and sum(not x['declared_role_member'] for x in products)==34
 current_errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in b.c.Draft202012Validator(docs['current_Definition_schema']).iter_errors(original)];inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(x) for x in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']]
 report={'schema_version':'definition-assurance-EvidenceSet-profile/v1-candidate','status':'PASS-for-qualified-EvidenceSet-hypotheses-and-actual-C70-shape-role-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_comparison_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'direct_carrier_admission_ref':carrier['admission_decision_ref'],'direct_carrier_semantic_ref':carrier['semantic_definition_refs'][0],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'Definition_schema_probes':definition_probes,'direct_carrier_schema_probes':carrier_probes,'role_schema_product_probes':products,'role_schema_product_count':42,'declared_role_product_members':8,'schema_accepted_but_role_invalid_products':34,'pure_role_surface_observer_executed':True,'pure_carrier_projection_functions_executed':True,'pure_carrier_projection_observations':{'artifact_bytes':len(a1),'artifact_sha256':b.r.digest(a1),'fixture_bytes':len(f1),'fixture_sha256':b.r.digest(f1)},'rich_source_to_narrow_carrier_mapping':{'source_map_obligations':MAP_FIELDS,'absent_or_rejected_explicit_payload_fields':RICH_PAYLOAD_FIELDS,'accepted_correspondence_ref':None,'status':'pending-owner-and-consumer-map'},'historical_source_current_Definition_shape':{'errors':current_errors,'exact_source_admission_invalidated':False},'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_investigation_finding_truth_adequacy_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified rich Research-source-to-narrow-carrier hypotheses and actual C70 Evidence Set carrier/schema,pure role/projection observations. Schema admits42 enum products but34 are outside the8 exact declared roles;it accepts unresolved and whitespace refs,duplicate relations,active labels and overclaimed coverage without proving investigation,Finding truth,adequacy,source fidelity or authority. Thirteen richer source payload fields are absent/rejected,requiring accepted correspondence or explicit residue. No package writer,live consumer,accepted alignment or whole proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_comparison_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_comparison_frames']),'catalog_checks':x['actual_check_count'],'Definition_probes':len(x['Definition_schema_probes']),'Definition_acceptances':sum(y['schema_accepted'] for y in x['Definition_schema_probes']),'carrier_probes':len(x['direct_carrier_schema_probes']),'carrier_acceptances':sum(y['schema_accepted'] for y in x['direct_carrier_schema_probes']),'role_schema_products':42,'declared_role_members':8,'schema_accepted_but_role_invalid':34},indent=2))
if __name__=='__main__':main()

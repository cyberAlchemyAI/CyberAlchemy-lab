"""Finding qualification hypotheses and actual flat C70 carrier observations; no package writer."""
import copy,itertools,json,types
import build_candidate as b
import verifier as v
AXES=['identity','kind','source','definition_context','question','scope','wording','support_bound','derivation_basis','research_context','limitations','owner_challenge','sibling_references','carrier','lifecycle','revision']
FORBIDDEN=['Finding_is_Research_aggregate','Research_not_Finding_erases_Finding_conclusion','classification_is_Definition_authority','promotion_is_authority','wording_pair_is_actual_adequacy','handles_are_authenticated_provenance','Run_or_Set_requires_both','Findings_reference_proves_truth','Research_outcome_field_permitted','carrier_admission_is_instance_admission','schema_is_full_Source_semantics','schema_state_is_truth','revision_ref_is_reviewed_decision','created_updated_imply_order','C12_selection_is_C53_C70_or_owner_fidelity','nonentailment_denies_supported_outcomes']
MAP_FIELDS=['question','scope','wording','support_bound','Run_or_Set_derivation','Research_context','Project','Goals','sources','observations','method','support_items','counter_items','limitations','Finding_references','Research_outcome_absence','created_updated','owner_challenge','sibling_references','Definition_context']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['changed-binding:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_Finding_truth_adequacy_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-bounded-conclusion-with-separate-Research',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('flat-carrier-with-explicit-unaccepted-source-residue',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','claim_scope_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'sibling_assignment_declared':True,'explicit_sibling_ref':'hyp:separate-target','Run_or_Set_collapsed_into_both_required':False,'state_or_revision_imported_into_Source_T':False};rows=[]
 def qualified(x):x.update(full_alignment_claimed=True,accepted_map_refs={n:'hyp:map:'+n for n in MAP_FIELDS},owner_review_ref='hyp:owner',claim_scope_ref='hyp:scope')
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('changed-qualification')
  if x['selected']:
   errors+=['lost-obligation:'+n for n in MAP_FIELDS if not x['map_fields'].get(n)]
   if x['source_role_collapsed']:errors.append('Finding-Research-Definition-role-collapse')
   if x['sibling_assignment_declared'] and not x['explicit_sibling_ref']:errors.append('missing-explicit-sibling-ref')
   if x['Run_or_Set_collapsed_into_both_required']:errors.append('unaccepted-carrier-strengthening-of-source-disjunction')
   if x['state_or_revision_imported_into_Source_T']:errors.append('unaccepted-carrier-lifecycle-import')
   if x['full_alignment_claimed']:
    errors+=['missing-accepted-map:'+n for n in MAP_FIELDS if not x['accepted_map_refs'].get(n)]
    if not x['owner_review_ref'] or not x['claim_scope_ref']:errors.append('missing-owner-review-or-scope')
  if x['actual_outcome_claimed']:errors.append('hypothesis-or-shape-does-not-prove-truth-adequacy-authority')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_Finding_truth_adequacy_or_authority_verified':False,'universal_source_to_carrier_mapping_proof':False})
 add('proposed-full-source-map-without-acceptance',lambda x:None,False)
 add('narrow-carrier-with-explicit-Research-residue',lambda x:x['map_fields'].update({n:'explicit-source-residue' for n in MAP_FIELDS[5:]}),False)
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
 for n in ['source_role_collapsed','Run_or_Set_collapsed_into_both_required','state_or_revision_imported_into_Source_T','actual_outcome_claimed']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 add('missing-sibling-ref',lambda x:x.update(explicit_sibling_ref=''),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source']
 rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert len(direct)==1;carrier=direct[0];ap=b.ROOT/carrier['artifact_path'];artifact=json.loads(ap.read_bytes())
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','direct_artifact':ap,'direct_schema':b.ROOT/carrier['schema_path'],'direct_fixture':ap.parent/artifact['validation_contract']['positive_witness'],'bound_package_validator_source':b.ROOT/artifact['validation_contract']['shared_validator_path'],'carrier_generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'artifact_projection':ap.with_name('ARTIFACT.md'),'fixture_projection':ap.parent/artifact['validation_contract']['positive_projection'],'checker':b.UNIT/'verify_authority_profile.py'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['hostile_'+str(i)]=ap.parent/n
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];schema=docs['direct_schema'];b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(schema);dv=b.c.Draft202012Validator(ds);cv=b.c.Draft202012Validator(schema);generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('catalog143rows121current',len(rows)==143 and len(current)==121)
 ck('direct-current-Finding-v1-C70',carrier['artifact_type_ref']=='cal.artifact-type.finding/v1' and carrier['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('direct-exact-selected-meaning',carrier['semantic_definition_refs']==artifact['semantic_definition_refs']==[source['version_ref']])
 ck('direct-current-artifact-schema-byte-bindings',refs['direct_artifact']['sha256']==carrier['artifact_sha256']=='754ae78686ce548a1d15f53c9431818d4ede004fc21f1d4ef095d7a54b86a6d4' and refs['direct_schema']['sha256']==carrier['schema_sha256']==artifact['schema_digest']=='b0e2d44bee4819881a8e38369dc89646e967297028cd6b28959b9e43ab01d023')
 binding=artifact['semantic_definition_bindings'][0]
 ck('exact-C53-Definition-binding',binding['path']==source['path'] and binding['sha256']==source['sha256'] and binding['definition_ref']==source['version_ref'] and binding['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION')
 ck('retained-type-body-candidate-none',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none')
 ck('flat-closed23root21semantic-fields',schema['additionalProperties'] is False and len(schema['required'])==23 and len(artifact['instance_contract']['required_semantic_fields'])==21 and set(schema['required'])==set(artifact['instance_contract']['required_semantic_fields'])|{'status','authority_effect'} and 'payload' not in schema['properties'] and 'relation_refs' not in schema['properties'] and 'relation_roles' not in artifact)
 ck('exact-kind-discriminator',carrier['instance_discriminator']=={'path':'/kind','value':'finding'} and schema['properties']['kind']['const']=='finding')
 ck('five-by-five-state-labels',len(schema['properties']['finding_state']['enum'])==5 and len(schema['properties']['support_assessment']['properties']['support_state']['enum'])==5)
 ck('Run-and-Set-both-nonempty-carrier-strengthening',schema['properties']['research_run_refs']['minItems']==schema['properties']['evidence_set_refs']['minItems']==1)
 ck('four-hostile-witnesses',len(artifact['validation_contract']['negative_witnesses'])==4)
 ck('generator-exact-bound',refs['carrier_generator']['sha256']==artifact['source_direction']['shared_generator_sha256'])
 ck('package-validator-source-bound-not-executed',refs['bound_package_validator_source']['sha256']==artifact['validation_contract']['shared_validator_sha256'])
 ck('current-generic-Definition-separate-meaning',len(generic)==1 and generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('historical-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows))
 ck('selected-Definition-v1-valid',not list(dv.iter_errors(docs['source'])))
 ck('source-C53-D61-historical-posture-retained',docs['source']['source_refs'][0]['source_admission_ref'] is None and load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and len(load('source-checks.json')['selected_source_sections'][0]['admission']['target_definition_refs'])==4)
 generator=types.ModuleType('_pure_Finding_carrier_projection');exec(compile(paths['carrier_generator'].read_bytes(),str(paths['carrier_generator']),'exec'),generator.__dict__);before=copy.deepcopy(docs['direct_fixture']);a1=generator.render_artifact(artifact).encode();a2=generator.render_artifact(artifact).encode();f1=generator.render_instance(artifact,before).encode();f2=generator.render_instance(artifact,before).encode();ck('two-pure-artifact-fixture-projections',a1==a2==paths['artifact_projection'].read_bytes() and f1==f2==paths['fixture_projection'].read_bytes() and before==docs['direct_fixture'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];carrier_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected shape '+id+' '+str(errors))
  bucket.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_Finding_truth_adequacy_or_authority_verified':False})
 original=docs['source'];probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-root-'+n,x,dv,False)
 for n in ['statement','support_assessment','research_run_refs','revision_history']:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'unresolved-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:Finding schema proves truth and authority';probe(definition_probes,'overclaimed-text-shape-valid',x,dv,True)
 fixture=docs['direct_fixture'];probe(carrier_probes,'exact-current-fixture',copy.deepcopy(fixture),cv,True)
 def mutate(id,expected,fn):
  x=copy.deepcopy(fixture);fn(x);probe(carrier_probes,id,x,cv,expected)
 for n in schema['required']:mutate('missing-root-'+n,False,lambda x,n=n:x.pop(n))
 for n in ['node_id','owner_ref','scope_ref','statement','inquiry_ref','question','owner_route','challenge_route','claim_ceiling']:
  for label,value,accept in [('empty','',False),('whitespace','   ',False),('unresolved','hyp:unresolved',True)]:mutate(n+'-'+label,accept,lambda x,n=n,value=value:x.update({n:value}))
 for n in ['research_run_refs','evidence_set_refs','evidence_refs','limitations','counterevidence_refs','successor_refs']:
  for label,value,accept in [('empty',[],n in ['counterevidence_refs','successor_refs']),('unresolved',['hyp:unresolved'],True),('whitespace',['   '],False),('duplicate',['hyp:ref','hyp:ref'],False),('too-many',['hyp:'+str(i) for i in range(101)],False)]:mutate(n+'-'+label,accept,lambda x,n=n,value=value:x.update({n:value}))
 mutate('Run-only-Source-basis-carrier-rejected',False,lambda x:x.update(evidence_set_refs=[]))
 mutate('Set-only-Source-basis-carrier-rejected',False,lambda x:x.update(research_run_refs=[]))
 for n in ['payload','relation_refs','derived_authority','Research_outcome','project_ref','goal_refs','method_ref']:mutate('extra-'+n,False,lambda x,n=n:x.update({n:'hyp:claimed'}))
 for n,value in [('authority_effect','canonical'),('status','admitted'),('kind','evidence-set')]:mutate('changed-'+n,False,lambda x,n=n,value=value:x.update({n:value}))
 mutate('overclaimed-statement-and-ceiling-shape-valid',True,lambda x:x.update(statement='hyp:actual adequate truthful authoritative conclusion',claim_ceiling='hyp:whole proof and admission verified'))
 for n in ['created_at','last_updated_at']:
  mutate(n+'-impossible-calendar-shape-valid',True,lambda x,n=n:x.update({n:'2026-99-99T99:99:99Z'}))
  mutate(n+'-invalid-syntax-rejected',False,lambda x,n=n:x.update({n:'yesterday'}))
 mutate('reversed-time-order-shape-valid',True,lambda x:x.update(created_at='2026-10-06T00:00:00Z',last_updated_at='2026-10-05T00:00:00Z'))
 for n in ['support_state','rationale']:mutate('missing-support-'+n,False,lambda x,n=n:x['support_assessment'].pop(n))
 mutate('support-extra-field',False,lambda x:x['support_assessment'].update(actual_truth=True))
 mutate('support-invalid-state',False,lambda x:x['support_assessment'].update(support_state='proven'))
 mutate('support-empty-rationale',False,lambda x:x['support_assessment'].update(rationale=' '))
 mutate('superseded-without-successor',False,lambda x:x.update(finding_state='superseded'))
 mutate('current-with-successor-not-revision-reviewed',True,lambda x:x.update(finding_state='current',successor_refs=['hyp:unresolved']))
 revision={'revision_id':'hyp:revision','rationale':'hyp:rationale','decision_ref':'hyp:unresolved','supersedes_finding_ref':None}
 for n in revision:
  def missing(x,n=n):r=copy.deepcopy(revision);r.pop(n);x['revision_history']=[r]
  mutate('missing-revision-'+n,False,missing)
 mutate('revision-null-predecessor-unresolved-decision-valid',True,lambda x:x.update(revision_history=[copy.deepcopy(revision)]))
 mutate('duplicate-revisions-valid',True,lambda x:x.update(revision_history=[copy.deepcopy(revision),copy.deepcopy(revision)]))
 def selfcycle(x):r=copy.deepcopy(revision);r['supersedes_finding_ref']=x['node_id'];x['revision_history']=[r]
 mutate('revision-self-predecessor-valid',True,selfcycle)
 for i in range(4):probe(carrier_probes,'retained-hostile-'+str(i),docs['hostile_'+str(i)],cv,False)
 states=[]
 for state,support in itertools.product(schema['properties']['finding_state']['enum'],schema['properties']['support_assessment']['properties']['support_state']['enum']):
  x=copy.deepcopy(fixture);x['finding_state']=state;x['support_assessment']['support_state']=support
  if state=='superseded':x['successor_refs']=['hyp:successor']
  assert not list(cv.iter_errors(x));states.append({'finding_state':state,'support_state':support,'schema_accepted':True,'actual_Finding_truth_adequacy_revision_or_authority_verified':False})
 current_errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in b.c.Draft202012Validator(docs['current_Definition_schema']).iter_errors(original)];inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']]
 report={'schema_version':'definition-assurance-Finding-profile/v1-candidate','status':'PASS-for-qualified-Finding-hypotheses-and-actual-flat-C70-shape-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_comparison_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'direct_carrier_admission_ref':carrier['admission_decision_ref'],'direct_carrier_semantic_ref':carrier['semantic_definition_refs'][0],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'Definition_schema_probes':definition_probes,'direct_carrier_schema_probes':carrier_probes,'state_schema_product_probes':states,'state_schema_product_count':25,'source_map_obligations':MAP_FIELDS,'carrier_source_disjunction_gap':{'Source':'one-or-more ResearchRuns OR EvidenceSets; nonexclusive','carrier':'both research_run_refs and evidence_set_refs required nonempty','accepted_correspondence_ref':None},'carrier_representation':'flat23required-root21semantic-fields;no-payload-or-declared-relation-role-surface','current_Definition_v2_comparison':{'schema_accepted':not current_errors,'errors':current_errors,'selected_Definition_v1_admission_invalidated':False},'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_Finding_truth_adequacy_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified Finding and separate Research-context hypotheses with actual current C70 flat Finding schema and pure projection observations. Both derivation lists are schema-required despite source Run OR Set; 25 state/support products are shape-valid, including current/contradicted. Unresolved refs,impossible calendar,reversed times,duplicate revision and self-predecessor do not prove truth,support adequacy,review,source fidelity,chronology or authority. No accepted carrier correspondence,package writer,live consumer or whole proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_comparison_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_comparison_frames']),'catalog_checks':x['actual_check_count'],'Definition_probes':len(x['Definition_schema_probes']),'Definition_acceptances':sum(y['schema_accepted'] for y in x['Definition_schema_probes']),'carrier_probes':len(x['direct_carrier_schema_probes']),'carrier_acceptances':sum(y['schema_accepted'] for y in x['direct_carrier_schema_probes']),'state_schema_products':25},indent=2))
if __name__=='__main__':main()

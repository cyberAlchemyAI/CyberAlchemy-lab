"""Qualified Registry hypotheses and historical/current carrier,consumer and schema observations."""
import ast,copy,json
import build_candidate as b
import verifier as v
AXES=['registry_ref', 'entry_ref', 'versioned_type_ref', 'type_key', 'artifact_ref', 'artifact_digest', 'schema_ref', 'schema_digest', 'schema_selector', 'discriminator_path', 'discriminator_value', 'Definition_set_ref', 'Definition_members', 'decision_ref', 'overlay_ref', 'lifecycle_state', 'historical_visibility', 'successor_ref']
FORBIDDEN=['registration_is_admission', 'embedded_status_is_effective_state', 'descriptor_is_admitted_contract', 'resolved_duplicate_scope_silently_discarded', 'entry_scope_is_accepted_without_map', 'digest_declaration_verifies_bytes', 'schema_reference_proves_selector_validity', 'decision_label_authenticates_owner', 'at_most_one_requires_total_resolution', 'zero_results_means_conformance', 'historical_visibility_authenticates_chronology', 'schema_PASS_grants_lifecycle_authority', 'C68_carrier_admission_accepts_translation', 'C13_Definition_profile_proves_Registry_consistency', 'v1_consumer_label_silently_replaced_by_v2', 'candidate_schema_mismatch_silently_ignored', 'historical25_versions_is_current_catalog_count', 'hypothetical_map_is_owner_acceptance']
MAP_FIELDS=['registry_ref', 'entry_ref', 'versioned_type_ref', 'type_key', 'artifact_ref', 'artifact_digest', 'schema_ref', 'schema_digest', 'schema_selector', 'discriminator_path', 'discriminator_value', 'Definition_set_ref', 'Definition_members', 'decision_ref', 'overlay_ref', 'lifecycle_state', 'historical_visibility', 'successor_ref', 'entry_vs_descriptor_scope', 'resolved_duplicate_lineage', 'candidate_admitted_current_historical_mapping', 'whole_null_and_shared_selector_mapping', 'exact_Definition_membership', 'owner_overlay_authority', 'at_most_one_result_relation', 'actual_byte_fidelity', 'historical_and_current_consumer_versions', 'operational_root_envelope_schema', 'consumer_claim_ceiling']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['changed-binding:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_digest_decision_admission_or_resolution_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-Registry-necessary-guard-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('distinct-current-Registry-carrier-and-C13-Definition-profile-with-unaccepted-map',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','claim_scope_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'posture_metadata_as_sufficient_authority':False,'unresolved_entry_scope_ignored':False,'sibling_assignment_declared':True,'explicit_sibling_refs':['hyp:historical-Registry-v1-consumer','hyp:current-Registry-v2-consumer']};rows=[]
 def qualified(x):x.update(full_alignment_claimed=True,accepted_map_refs={n:'hyp:map:'+n for n in MAP_FIELDS},owner_review_ref='hyp:owner',claim_scope_ref='hyp:scope')
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('changed-qualification')
  if x['selected']:
   errors+=['lost-obligation:'+n for n in MAP_FIELDS if not x['map_fields'].get(n)]
   for n in ['source_role_collapsed','posture_metadata_as_sufficient_authority','unresolved_entry_scope_ignored']:
    if x[n]:errors.append('forbidden:'+n)
   if x['sibling_assignment_declared'] and (len(x['explicit_sibling_refs'])!=2 or len(set(x['explicit_sibling_refs']))!=2):errors.append('missing-sibling-ref')
   if x['full_alignment_claimed']:
    errors+=['missing-accepted-map:'+n for n in MAP_FIELDS if not x['accepted_map_refs'].get(n)]
    if not x['owner_review_ref'] or not x['claim_scope_ref']:errors.append('missing-owner-review-or-scope')
  if x['actual_outcome_claimed']:errors.append('hypothesis-shape-or-profile-does-not-prove-actual-outcome')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_digest_decision_admission_or_resolution_verified':False,'universal_source_to_profile_mapping_proof':False})
 add('complete-proposed-source-map-without-acceptance',lambda x:None,False)
 add('separate-Definition-profile-with-explicit-Registry-residue',lambda x:x['map_fields'].update({n:'explicit-source-residue' for n in MAP_FIELDS}),False)
 add('no-sibling-assignment',lambda x:x.update(sibling_assignment_declared=False,explicit_sibling_refs=[]),False)
 add('outside-selected-map-scope',lambda x:x.update(selected=False,map_fields={},source_role_collapsed=True),False)
 add('hypothetical-map-references-not-actual-owner-review',qualified,False)
 for n in AXES:add('changed-binding-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in MAP_FIELDS:
  add('lost-map-'+n,lambda x,n=n:x['map_fields'].pop(n),True)
  def missing(x,n=n):qualified(x);x['accepted_map_refs'][n]=''
  add('missing-accepted-map-'+n,missing,True)
 add('shape-claimed-full-fidelity',lambda x:x.update(full_alignment_claimed=True),True)
 for n in ['owner_review_ref','claim_scope_ref']:
  def missing(x,n=n):qualified(x);x[n]=''
  add('missing-'+n,missing,True)
 for n in ['source_role_collapsed','posture_metadata_as_sufficient_authority','unresolved_entry_scope_ignored','actual_outcome_claimed']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 add('missing-sibling-ref',lambda x:x.update(explicit_sibling_refs=[]),True)
 return rows
def pure_functions(path,names):
 nodes=[x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in nodes}==set(names);ns={'Any':object,'json':json};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns
def sliced_projections(path,artifact,registry):
 tree=ast.parse(path.read_bytes());start=next(i for i,x in enumerate(tree.body) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='artifact_lines' for t in x.targets));nodes=[];removed=0
 for node in tree.body[start:]:
  if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='write_text':removed+=1;continue
  assert isinstance(node,(ast.Assign,ast.AugAssign,ast.For));nodes.append(node)
 assert removed==2 and not any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ['write_text','write_bytes','open','unlink','mkdir'] for node in nodes for x in ast.walk(node))
 a=copy.deepcopy(artifact);r=copy.deepcopy(registry);ns={'a':a,'r':r,'json':json};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);assert a==artifact and r==registry
 return ('\n'.join(ns['artifact_lines']).rstrip()+'\n').encode(),('\n'.join(ns['lines']).rstrip()+'\n').encode()
def verify(write=False):
 context=load('context.json');typed=load('types-logic-receipt.json');b.unchanged(typed['inputs']+typed['producer_results']+context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];carrier=next(x for x in direct if x['artifact_type_ref']=='cal.artifact-type.artifact-type-registry/v2');generic=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2');profile_type=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.evaluation-profile/v1');cp=(b.ROOT/carrier['artifact_path']).parent;hp=b.ROOT/'authority/artifact-types/artifact-type-registry/v1'
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/generic['schema_path'],'C13_foundation_schema':b.ROOT/profile_type['schema_path'],'C13_profile':b.ROOT/'authority/profiles/definition/v1/evaluation.json','C13_decision':b.ROOT/'docs/decisions/0013-foundation-01-admission/decision.json','C13_profile_generator':b.ROOT/'authority/foundation/v1/render.py','C13_profile_projection':b.ROOT/'authority/profiles/definition/v1/EVALUATION.md','current_artifact':b.ROOT/carrier['artifact_path'],'current_schema':b.ROOT/carrier['schema_path'],'initial_registry':cp/'registry.json','initial_registry_projection':cp/'REGISTRY.md','current_artifact_projection':cp/'ARTIFACT-TYPE.md','current_generator':cp/'build.py','current_validator':cp/'validate.py','hostile_matrix':cp/'hostile-cases.json','historical_artifact':hp/'artifact.json','historical_schema':hp/'schema.json','historical_registry':hp/'fixtures/valid/registry.json','checker':b.UNIT/'verify_authority_profile.py'}
 resolution_current=b.source_ref(snap,'cal.definition.artifact-type-resolution');resolution_historical=next(x for x in snap['historical_entries'] if x['version_ref']=='cal.definition.artifact-type-resolution@1.0.0-candidate.1');resolution_sources=[{k:row[k] for k in ['definition_id','version_ref','path','sha256']} for row in [resolution_historical,resolution_current]]
 for label,selected in zip(['historical_resolution','current_resolution'],resolution_sources):paths[label]=b.ROOT/selected['path'];paths[label+'_projection']=(b.ROOT/selected['path']).with_name('DEFINITION.md')
 artifact=json.loads(paths['current_artifact'].read_bytes())
 for binding in artifact['semantic_definition_bindings']:paths['binding_'+binding['definition_ref']]=b.ROOT/binding['path']
 for i,row in enumerate(rows):paths['catalog-artifact-'+str(i)]=b.ROOT/row['artifact_path'];paths['catalog-schema-'+str(i)]=b.ROOT/row['schema_path']
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json' and not k.startswith('catalog-')};checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ds=docs['Definition_schema'];foundation=docs['C13_foundation_schema'];ps={'$schema':foundation['$schema'],'$defs':foundation['$defs'],'$ref':profile_type['schema_selector']};b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(ps);dv=b.c.Draft202012Validator(ds);pv=b.c.Draft202012Validator(ps);record=docs['C13_profile'];decision=docs['C13_decision'];admitted=[x for x in decision['admitted_records'] if x['record_id']==record['record_id']]
 ck('catalog143contracts121current22historical145descriptors',len(rows)==143 and len(current)==121 and len([x for x in rows if x['lifecycle_state']=='admitted-historical'])==22 and len(registry['descriptors'])==145)
 ck('one-current-direct-Registry-v2-carrier',len(direct)==1 and direct[0]==carrier and carrier['admission_decision_ref']=='CAL-DECISION-0068-ARTIFACT-TYPE-REGISTRY-V2-ADMISSION')
 ck('exact-current-carrier-and-schema',refs['current_artifact']=={'path':carrier['artifact_path'],'sha256':carrier['artifact_sha256']} and refs['current_schema']=={'path':carrier['schema_path'],'sha256':carrier['schema_sha256']})
 ck('current-carrier-retained-body-candidate-none',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none')
 ck('generic-current-Definition-separate-meaning',generic['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('C13-profile-schema-selector-exact',profile_type['schema_selector']=='#/$defs/evaluationProfile' and profile_type['semantic_definition_refs']==[] and refs['C13_foundation_schema']['sha256']==profile_type['schema_sha256'])
 ck('C13-exact-Definition-profile-admission',decision['status']=='owner-admitted' and len(admitted)==1 and admitted[0]['path']==refs['C13_profile']['path'] and admitted[0]['sha256']==refs['C13_profile']['sha256']=='8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9' and admitted[0]['admission_effect']=='definition-evaluation-profile-admitted')
 ck('C13-body-and-generic-subject-distinct',record['status']=='candidate-unadmitted' and record['authority_effect']=='none' and record['record_id']=='CAL-EVALUATION-DEFINITION-V1' and record['subject_artifact_type_ref']=='cal.artifact-type.definition/v1' and record['outcomes']==['PASS','FAIL','NOT_EVALUABLE'] and record['evaluation_mode']=='collect-all')
 ck('C13-profile13required7checks',len(foundation['$defs']['evaluationProfile']['allOf'][1]['required'])==13 and len(record['checks'])==7 and not list(pv.iter_errors(record)))
 ck('C13-generator-digest',record['source_direction']['generator_sha256']==refs['C13_profile_generator']['sha256'])
 gen=pure_functions(paths['C13_profile_generator'],['header','evaluation']);before=copy.deepcopy(record);first=(gen['evaluation'](before).rstrip()+'\n').encode();second=(gen['evaluation'](before).rstrip()+'\n').encode();ck('two-pure-C13-projections-preserve-input',first==second==paths['C13_profile_projection'].read_bytes() and before==record)
 ck('source-Definition-valid',not list(dv.iter_errors(docs['source'])))
 ck('declared-consumer-labels-retained',docs['source']['primary_consumer_refs']==['cal.artifact-type.artifact-type-registry/v1','cal.definition.artifact-type-resolution@1.0.0-candidate.1'])
 ck('predecessor-contract-exact',artifact['predecessor_contract']['path']==refs['historical_artifact']['path'] and artifact['predecessor_contract']['sha256']==refs['historical_artifact']['sha256'])
 for binding in artifact['semantic_definition_bindings']:ck('exact-current-semantic-binding-'+binding['definition_ref'],refs['binding_'+binding['definition_ref']]=={'path':binding['path'],'sha256':binding['sha256']} and b.source_ref(snap,binding['definition_ref'].split('@')[0])['version_ref']==binding['definition_ref'])
 ck('schema-digest-and-hostile-matrix-bound',artifact['schema_digest']==refs['current_schema']['sha256'] and artifact['validation_contract']['hostile_matrix']['sha256']==refs['hostile_matrix']['sha256'])
 validator=b.c.Draft202012Validator(docs['current_schema']);hv=b.c.Draft202012Validator(docs['historical_schema']);initial=docs['initial_registry'];historical=docs['historical_registry'];ck('initial-C68-registry-schema-valid',not list(validator.iter_errors(initial)));ck('historical-v1-registry-schema-valid',not list(hv.iter_errors(historical)))
 ck('historical25-v1-and-C68initial56-descriptors-distinct-from-current',len(historical['entries'])==25 and len(initial['descriptors'])==56 and len(initial['admitted_contracts'])==33)
 first=sliced_projections(paths['current_generator'],artifact,initial);second=sliced_projections(paths['current_generator'],artifact,initial);ck('two-sliced-C68-artifact-and-registry-projections',first==second and first[0]==paths['current_artifact_projection'].read_bytes() and first[1]==paths['initial_registry_projection'].read_bytes())
 observations=[];gen=pure_functions(paths['Definition_generator'],['esc','bullets','render'])
 for label,selected in zip(['historical_resolution','current_resolution'],resolution_sources):
  doc=docs[label];before=copy.deepcopy(doc);first=gen['render'](before).encode();second=gen['render'](before).encode();ck(label+'-shape-and-two-pure-projections',not list(dv.iter_errors(doc)) and first==second==paths[label+'_projection'].read_bytes() and before==doc and refs[label]['sha256']==selected['sha256']);observations.append({'observed_source':selected,'effective_state':'admitted-historical' if label.startswith('historical') else 'admitted-current','observed_kind':'Definition meaning;no resolver entrypoint executed','formal_selector':'/voices/scientific_formal/formal_expression','formal_excerpt':doc['voices']['scientific_formal']['formal_expression'],'formal_excerpt_sha256':b.r.digest(doc['voices']['scientific_formal']['formal_expression'].encode()),'accepted_consumer_map_refs':[],'native_or_live_consumer_executed':False})
 current_errors=[{'path':'/'+ '/'.join(str(x) for x in error.absolute_path),'message':error.message} for error in validator.iter_errors(registry)]
 ck('current-operational-root-seven-exact-schema-mismatches-observed',len(current_errors)==7 and {x['path'] for x in current_errors}=={'/authority_effect','/inventory/semantic_binding_counts','/source_direction','/source_direction/canonical','/status'})
 ck('current-four-descriptor-states-and-two-resolved-duplicates-observed',{x['effective_state'] for x in registry['descriptors']}=={'candidate-unadmitted','admitted-current','admitted-historical','resolved-duplicate'} and sum(x['effective_state']=='resolved-duplicate' for x in registry['descriptors'])==2)
 ck('current-shared-and-whole-schema-selectors-observed',any(x['schema_selector'] is None for x in rows) and any(isinstance(x['schema_selector'],str) and x['schema_selector'].startswith('#/') for x in rows))
 catalog_observations=[{'artifact_type_ref':row['artifact_type_ref'],'lifecycle_state':row['lifecycle_state'],'artifact_digest_matches':refs['catalog-artifact-'+str(i)]['sha256']==row['artifact_sha256'],'schema_digest_matches':refs['catalog-schema-'+str(i)]['sha256']==row['schema_sha256'],'schema_selector':row['schema_selector'],'accepted_semantic_map':False} for i,row in enumerate(rows)]
 ck('all-catalog-binding-observations-recorded',len(catalog_observations)==143)
 registry_probes=[];mutate=pure_functions(paths['current_validator'],['mutate_registry']);mutate['mutate_registry'].__globals__['copy']=copy
 for case in docs['hostile_matrix']['cases']:
  hostile=mutate['mutate_registry'](initial,case['mutation']);errors=[e.message for e in validator.iter_errors(hostile)];ck('C68-hostile-'+case['case_id'],bool(errors) and any(case['expected_rejection_fragment'] in e for e in errors));registry_probes.append({'case_id':case['case_id'],'schema_accepted':not bool(errors),'errors':errors,'canonical_writer_executed':False})
 cross=[{'finding_id':'REG-CONSUMER-FINDING-001','status':'unresolved','issue':'Candidate three-tag selected EntryReference scope versus current v2 four-state descriptors including resolved-duplicate.','observed_descriptor_states':sorted({x['effective_state'] for x in registry['descriptors']}),'candidate_entry_state_tags':list(b.STATE_NAMES),'possible_resolution':'Accept exact entry/descriptor/lineage and reference-alias mappings;do not silently discard duplicate-resolution evidence or assert vocabulary completeness.','accepted_consumer_map_refs':[]},{'finding_id':'REG-CONSUMER-FINDING-002','status':'unresolved','issue':'Current admitted operational registry does not conform to the exact C68 candidate-instance schema selected by its current type contract.','current_registry_ref':refs['registry'],'selected_schema_ref':refs['current_schema'],'schema_accepted':False,'schema_errors':current_errors,'possible_resolution':'Review root admission envelope,status/effect,projection metadata and omitted zero-count keys;an admitted-instance schema or accepted envelope mapping may be required. No canonical repair is performed.','accepted_consumer_map_refs':[]},{'finding_id':'REG-CONSUMER-FINDING-003','status':'unresolved','issue':'Source declares Registry/v1 and Resolution candidate.1;observed current carrier is Registry/v2 and current Resolution meaning is candidate.2.','historical_carrier_ref':refs['historical_artifact'],'current_carrier_ref':refs['current_artifact'],'resolution_sources':resolution_sources,'possible_resolution':'Record historical/current consumer routes and accepted semantic correspondence without silently rewriting source labels.','accepted_consumer_map_refs':[]}]
 if not all(x['result'] for x in checks):raise ValueError(json.dumps([x for x in checks if not x['result']]))
 definition_probes=[];profile_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected shape '+id+' '+str(errors))
  bucket.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_digest_decision_admission_or_resolution_verified':False})
 original=docs['source'];probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-root-'+n,x,dv,False)
 for n in AXES:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'unresolved-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:exact Registry entry declarations prove actual digest fidelity,admission and authority';probe(definition_probes,'overclaimed-text-shape-valid',x,dv,True)
 probe(profile_probes,'exact-admitted-C13-Definition-profile-body',copy.deepcopy(record),pv,True)
 for n in foundation['$defs']['evaluationProfile']['allOf'][1]['required']:
  x=copy.deepcopy(record);x.pop(n);probe(profile_probes,'missing-root-'+n,x,pv,False)
 for n in ['check_id','purpose','blocked_by']:
  x=copy.deepcopy(record);x['checks'][0].pop(n);probe(profile_probes,'missing-check-'+n,x,pv,False)
 for n in ['record_id','owner_ref','claim_ceiling','admission_rule']:
  for label,value,expected in [('empty','',False),('whitespace',' ',True),('unresolved','hyp:unresolved',True)]:
   x=copy.deepcopy(record);x[n]=value;probe(profile_probes,n+'-'+label,x,pv,expected)
 x=copy.deepcopy(record);x['claim_ceiling']='hyp:this profile grants Registry classification,admission and authority';probe(profile_probes,'overclaimed-profile-text-shape-valid',x,pv,True)
 reports=profiles();fs=frames();report={'schema_version':'definition-assurance-ArtifactTypeRegistry-authority-profile/v1-candidate','status':'PASS-for-qualified-Registry-hypotheses-and-exact-consumer-observations-with-unresolved-schema-and-entry-scope','authority_effect':'none','source':source,'profiles':reports,'finite_comparison_frames':fs,'actual_checks':checks,'actual_check_count':len(checks),'selected_inputs':refs,'checker_bindings':[refs['checker'],b.ref(b.IMPL/'contracts.py')],'runtime_bindings':runtime,'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'admitted_historical_type_rows':22,'current_descriptor_rows':145,'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic['artifact_type_ref'],'generic_Definition_semantic_ref':generic['semantic_definition_refs'][0],'C13_profile_record_ref':record['record_id'],'C13_profile_is_Registry_consistency_detector':False,'Definition_schema_probes':definition_probes,'C13_profile_schema_probes':profile_probes,'C68_hostile_registry_schema_probes':registry_probes,'catalog_contract_and_schema_observations':catalog_observations,'current_operational_registry_schema_accepted':False,'current_operational_registry_schema_errors':current_errors,'consumer_meaning_observations':observations,'cross_definition_review_findings':cross,'source_map_obligations':MAP_FIELDS,'accepted_source_to_carrier_or_consumer_map_refs':[],'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'current_registry_mutator_evaluated_on_in_memory_initial_fixtures':True,'actual_digest_decision_admission_or_resolution_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Exact historical/current catalog,carrier,Definition consumer,projection and schema observations;current operational root has7 schema mismatches and broader4-state descriptor scope. No accepted entry scope,envelope map,owner fidelity,lifecycle effect,live writer or whole proof.'}
 b.unchanged(list(refs.values())+context['sources']+typed['inputs']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh qualification/catalog/consumer observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'qualification_profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'finite_frames':len(x['finite_comparison_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_comparison_frames']),'actual_checks':x['actual_check_count'],'Definition_schema_probes':len(x['Definition_schema_probes']),'C13_profile_schema_probes':len(x['C13_profile_schema_probes']),'C68_hostile_probes':len(x['C68_hostile_registry_schema_probes']),'catalog_contract_and_schema_observations':len(x['catalog_contract_and_schema_observations']),'catalog_digest_mismatches':sum(not z['artifact_digest_matches'] or not z['schema_digest_matches'] for z in x['catalog_contract_and_schema_observations']),'current_operational_registry_schema_accepted':False,'current_operational_registry_schema_errors':len(x['current_operational_registry_schema_errors']),'unresolved_consumer_findings':len(x['cross_definition_review_findings']),'mapping_obligations':len(x['source_map_obligations']),'direct_current_definition_binding_types':x['direct_current_definition_binding_types'],'semantic_ready':False},indent=2))
if __name__=='__main__':main()

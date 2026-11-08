"""Qualified Interface hypotheses and actual C12 prototype/C13 Definition evaluation profile observations."""
import ast,copy,json
import build_candidate as b
import verifier as v
AXES=['identity','kind','source','normalized_context','claim_class','evidence_kind','proxy_limit','owner_route','residue','context','direct_topics','human_topics','necessary_validity','fixture_approval','weak_response','dense_expert_calibration','role_boundaries','sibling_references']
FORBIDDEN=['C12_prototype_is_selected_UX_profile','C13_Definition_profile_is_UX_profile','generic_type_admission_is_instance_admission','source_admission_is_translation_fidelity','matching_is_sufficient_validity','five_classes_are_universal_exclusive_taxonomy','class_order_is_numeric_UX_score','browser_direct_topic_is_actual_adequacy','browser_preparation_is_human_outcome_proof','fixture_OR_approval_replaces_AND','fixture_approval_declarations_create_authority','response_declarations_execute_remediation','false_positive_handle_proves_calibration','schema_PASS_grants_admission','schema_checks_authenticate_owner','nonempty_proxy_text_is_adequate_disclosure','invariant_and_profile_split_collapsed','nonentailment_denies_supported_outcomes']
MAP_FIELDS=['claim_class','evidence_kind','proxy_limit','owner_route','residue','context','normalized_classification','D47_lineage','five_class_labels','direct_topics','human_topics','necessary_validity','fixtures_calibration','owner_approval','weaker_evidence_response','dense_expert_false_positive_calibration','role_noncollapse','sibling_references']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['changed-binding:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_truth_calibration_approval_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-Interface-necessary-guard-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('distinct-prototype-and-C13-profile-with-unaccepted-map',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','claim_scope_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'necessary_validity_as_iff':False,'fixture_approval_as_OR':False,'sibling_assignment_declared':True,'explicit_sibling_ref':'hyp:separate-UX-profile'};rows=[]
 def qualified(x):x.update(full_alignment_claimed=True,accepted_map_refs={n:'hyp:map:'+n for n in MAP_FIELDS},owner_review_ref='hyp:owner',claim_scope_ref='hyp:scope')
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('changed-qualification')
  if x['selected']:
   errors+=['lost-obligation:'+n for n in MAP_FIELDS if not x['map_fields'].get(n)]
   for n in ['source_role_collapsed','necessary_validity_as_iff','fixture_approval_as_OR']:
    if x[n]:errors.append('forbidden:'+n)
   if x['sibling_assignment_declared'] and not x['explicit_sibling_ref']:errors.append('missing-sibling-ref')
   if x['full_alignment_claimed']:
    errors+=['missing-accepted-map:'+n for n in MAP_FIELDS if not x['accepted_map_refs'].get(n)]
    if not x['owner_review_ref'] or not x['claim_scope_ref']:errors.append('missing-owner-review-or-scope')
  if x['actual_outcome_claimed']:errors.append('hypothesis-shape-or-profile-does-not-prove-actual-outcome')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_truth_calibration_approval_or_authority_verified':False,'universal_source_to_profile_mapping_proof':False})
 add('complete-proposed-source-map-without-acceptance',lambda x:None,False)
 add('separate-Definition-profile-with-explicit-Interface-residue',lambda x:x['map_fields'].update({n:'explicit-source-residue' for n in MAP_FIELDS}),False)
 add('no-sibling-assignment',lambda x:x.update(sibling_assignment_declared=False,explicit_sibling_ref=''),False)
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
 for n in ['source_role_collapsed','necessary_validity_as_iff','fixture_approval_as_OR','actual_outcome_claimed']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 add('missing-sibling-ref',lambda x:x.update(explicit_sibling_ref=''),True)
 return rows
def pure_functions(path,names):
 nodes=[x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in nodes}==set(names);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2');profile_type=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.evaluation-profile/v1')
 prototype=b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/profile/profile-ux-evidence-compatibility/v1/artifact.json'
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/generic['schema_path'],'C13_foundation_schema':b.ROOT/profile_type['schema_path'],'C13_profile':b.ROOT/'authority/profiles/definition/v1/evaluation.json','C13_decision':b.ROOT/'docs/decisions/0013-foundation-01-admission/decision.json','C13_profile_generator':b.ROOT/'authority/foundation/v1/render.py','C13_profile_projection':b.ROOT/'authority/profiles/definition/v1/EVALUATION.md','C12_prototype':prototype,'C12_prototype_projection':prototype.with_name('ARTIFACT.md'),'C12_prototype_renderer':b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/followups.py','C12_normalization':b.ROOT/'docs/normalizations/0001-definition-migration-model/normalization.json','checker':b.UNIT/'verify_authority_profile.py'};refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];foundation=docs['C13_foundation_schema'];ps={'$schema':foundation['$schema'],'$defs':foundation['$defs'],'$ref':profile_type['schema_selector']};b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(ps);dv=b.c.Draft202012Validator(ds);pv=b.c.Draft202012Validator(ps);record=docs['C13_profile'];proto=docs['C12_prototype'];decision=docs['C13_decision'];admitted=[x for x in decision['admitted_records'] if x['record_id']==record['record_id']];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('catalog143rows121current',len(rows)==143 and len(current)==121)
 ck('no-direct-current-Interface-invariant-carrier',not direct)
 ck('generic-current-Definition-separate-meaning',generic['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('generic-C13-EvaluationProfile-selector-exact',profile_type['admission_decision_ref']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION' and profile_type['schema_selector']=='#/$defs/evaluationProfile' and profile_type['semantic_definition_refs']==[] and refs['C13_foundation_schema']['sha256']==profile_type['schema_sha256'])
 ck('C13-decision-and-exact-Definition-profile-admission',decision['status']=='owner-admitted' and decision['decision_id']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION' and len(admitted)==1 and admitted[0]['path']==refs['C13_profile']['path'] and admitted[0]['sha256']==refs['C13_profile']['sha256']=='8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9' and admitted[0]['admission_effect']=='definition-evaluation-profile-admitted')
 ck('C13-retained-profile-body-candidate-none',record['status']=='candidate-unadmitted' and record['authority_effect']=='none')
 ck('C13-profile-subject-Definition-not-UX-claim',record['record_id']=='CAL-EVALUATION-DEFINITION-V1' and record['subject_artifact_type_ref']=='cal.artifact-type.definition/v1' and record['outcomes']==['PASS','FAIL','NOT_EVALUABLE'] and record['evaluation_mode']=='collect-all')
 ck('C13-profile13required7checks',len(foundation['$defs']['evaluationProfile']['allOf'][1]['required'])==13 and len(record['checks'])==7 and not list(pv.iter_errors(record)))
 ck('C13-generator-bytes-bound',record['source_direction']['generator_sha256']==refs['C13_profile_generator']['sha256'])
 ck('C12-profile-exact-normalization-contract',proto['normalized_contract']==next(x for x in docs['C12_normalization']['profiles'] if x['profile_id']=='profile.ux-evidence-compatibility')=={'artifact_type_ref':'type.evaluation','name':'UX/UI Evidence Compatibility Profile','profile_id':'profile.ux-evidence-compatibility'})
 ck('C12-profile-retained-prototype-no-admission',proto['target_id']=='profile.ux-evidence-compatibility' and proto['family']=='profile' and proto['status']=='prototype-scaffold' and proto['authority_effect']=='none' and proto['owner_decision_ref']=='CAL-DECISION-0012-NORMALIZE-01-DEFAULTS')
 ck('C12-prototype-needs-family-specific-schema',proto['four_facets']['schema']['admitted_schema_ref'] is None and proto['four_facets']['schema']['schema_state']=='prototype-only-needs-family-specific-schema' and proto['four_facets']['classification']['carrier_ref'] is None)
 ck('C12-prototype-D47-exact-separate-split',proto['accepted_source_decisions']==[{'decision':'split','legacy_id':'CAV2-D47','legacy_term':'Interface Evidence Boundary'}] and len(proto['source_refs'])==1 and proto['source_refs'][0]['section_sha256']==load('source-checks.json')['selected_source_sections'][0]['sha256']=='f8d187d383d536b6e4271808161e7d103173380b89f3774692faefff76b37e2b')
 ck('selected-Definition-v1-valid',not list(dv.iter_errors(docs['source'])))
 ck('C53-source-meaning-admission-not-replaced',load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and len(load('source-checks.json')['selected_source_sections'][0]['admission']['target_definition_refs'])==1)
 gen=pure_functions(paths['C13_profile_generator'],['header','evaluation']);before=copy.deepcopy(record);p1=(gen['evaluation'](before).rstrip()+'\n').encode();p2=(gen['evaluation'](before).rstrip()+'\n').encode();ck('two-pure-C13-profile-projections-preserve-input',p1==p2==paths['C13_profile_projection'].read_bytes() and before==record)
 gen=pure_functions(paths['C12_prototype_renderer'],['render_target']);before=copy.deepcopy(proto);p1=gen['render_target'](before).encode();p2=gen['render_target'](before).encode();ck('two-pure-C12-prototype-projections-preserve-input',p1==p2==paths['C12_prototype_projection'].read_bytes() and before==proto)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];profile_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected shape '+id+' '+str(errors))
  bucket.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_truth_calibration_approval_or_authority_verified':False})
 original=docs['source'];probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-root-'+n,x,dv,False)
 for n in ['claim_class','evidence_kind','proxy_limit','owner_route']:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'unresolved-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:browser evidence proves human trust and actual authority';probe(definition_probes,'overclaimed-text-shape-valid',x,dv,True)
 probe(profile_probes,'exact-admitted-C13-Definition-profile-body',copy.deepcopy(record),pv,True)
 def mutate(id,expected,fn):
  x=copy.deepcopy(record);fn(x);probe(profile_probes,id,x,pv,expected)
 for n in foundation['$defs']['evaluationProfile']['allOf'][1]['required']:mutate('missing-root-'+n,False,lambda x,n=n:x.pop(n))
 for n in ['record_id','owner_ref','claim_ceiling','admission_rule']:
  for label,value,expected in [('empty','',False),('whitespace',' ',True),('unresolved','hyp:unresolved',True)]:mutate(n+'-'+label,expected,lambda x,n=n,value=value:x.update({n:value}))
 for n in ['check_id','purpose','blocked_by']:mutate('missing-check-'+n,False,lambda x,n=n:x['checks'][0].pop(n))
 mutate('empty-check-list',False,lambda x:x.update(checks=[]))
 mutate('duplicate-check-record-shape-valid',True,lambda x:x['checks'].append(copy.deepcopy(x['checks'][0])))
 mutate('unresolved-blocker-shape-valid',True,lambda x:x['checks'][0].update(blocked_by=['hyp:unresolved']))
 mutate('self-blocked-check-shape-valid',True,lambda x:x['checks'][0].update(blocked_by=[x['checks'][0]['check_id']]))
 mutate('duplicate-blockers-shape-valid',True,lambda x:x['checks'][0].update(blocked_by=['hyp:ref','hyp:ref']))
 mutate('whitespace-check-purpose-shape-valid',True,lambda x:x['checks'][0].update(purpose=' '))
 mutate('overclaimed-check-purpose-shape-valid',True,lambda x:x['checks'][0].update(purpose='hyp:prove comprehension trust approval and deterministic authority'))
 mutate('overclaimed-admission-rule-shape-valid',True,lambda x:x.update(admission_rule='hyp:PASS admits all UI claims and creates authority'))
 mutate('overclaimed-ceiling-shape-valid',True,lambda x:x.update(claim_ceiling='hyp:whole proof and source fidelity verified'))
 mutate('different-UX-subject-rejected',False,lambda x:x.update(subject_artifact_type_ref='hyp:interface-claim'))
 mutate('different-outcome-labels-rejected',False,lambda x:x.update(outcomes=['hard gate','soft flag']))
 mutate('admitted-body-label-rejected',False,lambda x:x.update(status='admitted'))
 mutate('governing-effect-rejected',False,lambda x:x.update(authority_effect='canonical'))
 for n in MAP_FIELDS:mutate('Interface-field-not-C13-Definition-profile-'+n,False,lambda x,n=n:x.update({n:'hyp:ref'}))
 probe(profile_probes,'C12-UX-prototype-not-C13-profile-shape',copy.deepcopy(proto),pv,False)
 current_errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in b.c.Draft202012Validator(docs['current_Definition_schema']).iter_errors(original)];inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']]
 report={'schema_version':'definition-assurance-InterfaceClaimSupport-profile/v1-candidate','status':'PASS-for-qualified-Interface-hypotheses-and-actual-separate-C12-C13-profile-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_comparison_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[],'generic_Definition_current_type_ref':generic['artifact_type_ref'],'generic_Definition_semantic_ref':generic['semantic_definition_refs'][0],'C12_UX_profile':{'target_id':proto['target_id'],'status':proto['status'],'admitted_schema_ref':None,'selected_profile_admission_established':False},'C13_profile':{'record_id':record['record_id'],'admission_decision_ref':decision['decision_id'],'admission_effect':admitted[0]['admission_effect'],'subject_artifact_type_ref':record['subject_artifact_type_ref'],'source_Interface_meaning_bound':False},'Definition_schema_probes':definition_probes,'C13_profile_schema_probes':profile_probes,'source_map_obligations':MAP_FIELDS,'accepted_source_profile_correspondence_ref':None,'current_Definition_v2_comparison':{'schema_accepted':not current_errors,'errors':current_errors,'selected_Definition_v1_admission_invalidated':False},'pure_projection_functions_executed':True,'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_truth_calibration_approval_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified Interface necessary-guard hypotheses and actual separate C12 UX prototype/C13 Definition evaluation profile observations. No current type binds this invariant. C12 prototype lacks a selected family-specific schema;C13 is a collect-all Definition/v1 profile,not an admitted UX claim implementation. Its shape accepts unresolved refs,duplicate/self-blocked checks,whitespace and overclaimed rule/purpose text while rejecting Interface tuple extras. Two exact pure projections each create no writer,consumer,actual truth/calibration/approval/authority,accepted correspondence or whole proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_comparison_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_comparison_frames']),'catalog_checks':x['actual_check_count'],'Definition_probes':len(x['Definition_schema_probes']),'Definition_acceptances':sum(y['schema_accepted'] for y in x['Definition_schema_probes']),'C13_profile_probes':len(x['C13_profile_schema_probes']),'C13_profile_acceptances':sum(y['schema_accepted'] for y in x['C13_profile_schema_probes']),'direct_current_Interface_carriers':0},indent=2))
if __name__=='__main__':main()

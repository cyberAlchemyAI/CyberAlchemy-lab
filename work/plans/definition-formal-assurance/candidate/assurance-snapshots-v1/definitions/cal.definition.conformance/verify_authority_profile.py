"""Qualified conformance hypotheses plus actual Definition/evaluation-profile catalog and shape observations."""
import copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['subject','subject_digest','contract','contract_digest','scope','profile','profile_version','evidence_set','evidence_membership','obligation_map','assessment_owner','currentness_epoch']
FORBIDDEN=['validation_PASS_is_conformance','schema_scope_is_runtime_scope','identity_scope_is_implementation_scope','profile_label_is_completeness','sufficiency_declaration_is_adequacy','currentness_label_is_authentication','owner_handle_is_authority','digest_equal_means_identity_authority','NOT_EVALUABLE_is_PASS','unrecovered_D65_is_verified','recovered_ranges_authenticate_producer','conformance_is_admission','conformance_is_acceptance','conformance_is_authority','conformance_is_publication','conformance_is_deployment']
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];before=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['binding-changed:'+n for n in AXES if before[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':before,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_conformance_authority_adequacy_or_currentness_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-scoped-conformance-hypothesis',copy.deepcopy(before),copy.deepcopy(flags),False)
 add('separate-scopes-with-independent-qualified-evidence',copy.deepcopy(before),copy.deepcopy(flags),False)
 for n in AXES:
  after=copy.deepcopy(before);after[n]='hyp:changed';add('changed-'+n,after,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  f=copy.deepcopy(flags);f[n]=True;add('forbidden-'+n,copy.deepcopy(before),f,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'asserted':True,'tuple_declared':True,'scope_kind':'SchemaScope','profile_applicable':True,'profile_complete_declared':True,'evidence_current_declared':True,'stale_against_subject':False,'stale_against_contract':False,'evidence_subject_matches':True,'evidence_contract_matches':True,'assessment_subject_digest_matches':True,'assessment_contract_digest_matches':True,'assessment_profile_version_matches':True,'handles':{n:'hyp:'+n for n in ['subject','subject_digest','contract','contract_digest','scope','profile','profile_version','evidence_set','owner']},'obligations':[{'applicable':True,'handle':'hyp:obligation','profile_declares_sufficient':True,'evidence':[{'member':True,'maps_obligation':True,'satisfies_declared':True,'handle':'hyp:evidence'}]}],'not_evaluable_declared':False,'cause_reference':'hyp:cause','collapsed_role':None,'actual_outcome_claim':False};rows=[]
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('qualified-binding-change-needs-independent-review')
  if x['asserted']:
   for n in ['tuple_declared','profile_applicable','profile_complete_declared','evidence_current_declared','evidence_subject_matches','evidence_contract_matches','assessment_subject_digest_matches','assessment_contract_digest_matches','assessment_profile_version_matches']:
    if not x[n]:errors.append('missing-or-wrong-'+n)
   for n in ['stale_against_subject','stale_against_contract']:
    if x[n]:errors.append(n)
   for n,value in x['handles'].items():
    if not value:errors.append('missing-handle:'+n)
   for i,obligation in enumerate(x['obligations']):
    if not obligation['applicable']:continue
    if not obligation['handle']:errors.append('empty-obligation:'+str(i))
    if not obligation['profile_declares_sufficient']:errors.append('missing-sufficiency:'+str(i))
    if not any(e['member'] and e['maps_obligation'] and e['satisfies_declared'] and e['handle'] for e in obligation['evidence']):errors.append('missing-included-satisfying-evidence:'+str(i))
   if x['collapsed_role']:errors.append('excluded-conformance-role')
  # This explicit frame observation checks the source's causal NOT_EVALUABLE
  # test condition; it is not imported as a universal primary-T axiom.
  if x['not_evaluable_declared'] and not x['cause_reference']:errors.append('NOT_EVALUABLE-observation-needs-cause-reference')
  if x['actual_outcome_claim']:errors.append('declarations-are-not-accepted-actual-outcomes')
  assert bool(errors)==reject,(id,errors);rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_conformance_authority_adequacy_or_currentness_verified':False,'universal_sufficiency_or_scope_equivalence_proof':False})
 add('exact-current-schema-obligation-tuple',lambda x:None,False)
 for kind in b.SCOPE_KINDS:add('independent-'+kind,lambda x,kind=kind:x.update(scope_kind=kind),False)
 def plural(x):x['obligations'].append(copy.deepcopy(x['obligations'][0]));x['obligations'][0]['evidence'].append({'member':False,'maps_obligation':False,'satisfies_declared':False,'handle':''})
 add('plural-obligations-and-one-satisfying-included-witness',plural,False)
 add('outside-applicable-obligation-not-asserted',lambda x:x['obligations'].append({'applicable':False,'handle':'','profile_declares_sufficient':False,'evidence':[]}),False)
 add('empty-obligation-domain-vacuous-T-not-population-proof',lambda x:x.update(obligations=[]),False)
 add('unasserted-causal-NOT_EVALUABLE',lambda x:x.update(asserted=False,not_evaluable_declared=True,evidence_current_declared=False,obligations=[]),False)
 add('unasserted-outside-scope',lambda x:x.update(asserted=False,tuple_declared=False,profile_complete_declared=False),False)
 for n in AXES:add('changed-binding-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in ['tuple_declared','profile_applicable','profile_complete_declared','evidence_current_declared','evidence_subject_matches','evidence_contract_matches','assessment_subject_digest_matches','assessment_contract_digest_matches','assessment_profile_version_matches']:add('missing-'+n,lambda x,n=n:x.update({n:False}),True)
 for n in ['stale_against_subject','stale_against_contract']:add('stale-'+n,lambda x,n=n:x.update({n:True}),True)
 for n in base['handles']:add('empty-'+n,lambda x,n=n:x['handles'].update({n:''}),True)
 add('empty-obligation-handle',lambda x:x['obligations'][0].update(handle=''),True)
 add('profile-without-per-obligation-sufficiency',lambda x:x['obligations'][0].update(profile_declares_sufficient=False),True)
 add('applicable-obligation-without-evidence',lambda x:x['obligations'][0].update(evidence=[]),True)
 for n in ['member','maps_obligation','satisfies_declared']:add('evidence-without-'+n,lambda x,n=n:x['obligations'][0]['evidence'][0].update({n:False}),True)
 add('evidence-without-handle',lambda x:x['obligations'][0]['evidence'][0].update(handle=''),True)
 add('new-applicable-obligation-without-evidence',lambda x:x['obligations'].append({'applicable':True,'handle':'hyp:new','profile_declares_sufficient':True,'evidence':[]}),True)
 for role in b.ROLES:add('collapsed-'+role,lambda x,role=role:x.update(collapsed_role=role),True)
 add('unasserted-NOT_EVALUABLE-without-causal-reference',lambda x:x.update(asserted=False,not_evaluable_declared=True,cause_reference=''),True)
 add('claimed-actual-scope-authority-or-adequacy',lambda x:x.update(actual_outcome_claim=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source']
 paths={'registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','foundation_schema':b.ROOT/'authority/foundation/v1/schema.json','evaluation_profile':b.ROOT/'authority/profiles/definition/v1/evaluation.json','candidate':b.ROOT/'authority/definitions/candidates/0007-cml07-semantic-closure/candidate.json','source':b.ROOT/source['path'],'checker':b.UNIT/'verify_authority_profile.py'};refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};rows=docs['registry']['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];ep=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.evaluation-profile/v1'];schema=docs['Definition_schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);current_validator=b.c.Draft202012Validator(docs['current_Definition_schema']);foundation=docs['foundation_schema'];b.c.Draft202012Validator.check_schema(foundation);ep_schema={'$ref':'#/$defs/evaluationProfile','$defs':foundation['$defs']};ep_validator=b.c.Draft202012Validator(ep_schema);checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121)
 ck('no-admitted-direct-Conformance-type',not direct)
 ck('current-generic-Definition-v2',len(generic)==1 and generic[0]['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('generic-Definition-separate-current-meaning',generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('historical-generic-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows))
 ck('current-evaluation-profile-contract-C13',len(ep)==1 and ep[0]['admission_decision_ref']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION')
 ck('evaluation-profile-exact-foundation-schema-selector',ep[0]['schema_path']==refs['foundation_schema']['path'] and ep[0]['schema_sha256']==refs['foundation_schema']['sha256'] and ep[0]['schema_selector']=='#/$defs/evaluationProfile')
 ck('evaluation-profile-contract-has-no-Conformance-semantic-binding',ep[0]['semantic_definition_refs']==[])
 ck('CML07-exact-selected-evaluation-profile-binding',any(x['source_ref']=='cal.evaluation.definition/v1' and x['path']==refs['evaluation_profile']['path'] and x['sha256']==refs['evaluation_profile']['sha256'] and x['admission_posture']=='admitted' for x in docs['candidate']['source_bindings']))
 original_ep=docs['evaluation_profile'];ck('evaluation-profile-shape-valid',not list(ep_validator.iter_errors(original_ep)))
 ck('evaluation-profile-historical-candidate-none',original_ep['status']=='candidate-unadmitted' and original_ep['authority_effect']=='none')
 ck('evaluation-profile-exact-Definition-v1-subject',original_ep['subject_artifact_type_ref']=='cal.artifact-type.definition/v1')
 ck('evaluation-profile-collect-all-three-outcomes',original_ep['evaluation_mode']=='collect-all' and original_ep['outcomes']==['PASS','FAIL','NOT_EVALUABLE'])
 ck('seven-recorded-evaluation-checks',len(original_ep['checks'])==7 and len({x['check_id'] for x in original_ep['checks']})==7)
 ck('evaluation-profile-PASS-is-evidence-not-admission','PASS remains evidence and cannot perform the admission' in original_ep['admission_rule'])
 ck('selected-Definition-v1-shape-valid',not list(validator.iter_errors(docs['source'])) and docs['source']['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1')
 ck('retained-body-postures-separate-from-C29-overlay',load('source-checks.json')['historical_embedded_source_postures']==['admitted','candidate-unadmitted','candidate-unadmitted','candidate-unadmitted'] and load('source-checks.json')['current_registry_entry_lifecycle']=='admitted')
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 probes=[]
 def probe(surface,id,doc,expected,selected_validator):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in selected_validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored shape probe '+id+' '+str(errors))
  probes.append({'case_id':id,'surface':surface,'schema_accepted':accepted,'errors':errors,'actual_conformance_authority_adequacy_or_currentness_verified':False})
 original=docs['source'];probe('Definition/v1','selected-exact-Definition-shape',copy.deepcopy(original),True,validator)
 for n in schema['required']:
  d=copy.deepcopy(original);d.pop(n);probe('Definition/v1','missing-required-root-'+n,d,False,validator)
 for n in ['subject_digest','contract_digest','evidence_set','conformance_scope']:
  d=copy.deepcopy(original);d[n]='hyp:claimed';probe('Definition/v1','tuple-field-not-Definition-schema-'+n,d,False,validator)
 for n in ['definition_id','term','semantic_owner_ref']:
  d=copy.deepcopy(original);d[n]='hyp:unresolved';probe('Definition/v1','shape-does-not-resolve-'+n,d,True,validator)
 d=copy.deepcopy(original);d['voices']['scientific_formal']['normative_statement']='hyp:schema PASS proves runtime conformance and authorizes publication';probe('Definition/v1','shape-valid-overclaimed-normative-text',d,True,validator)
 probe('foundation/evaluationProfile','selected-exact-evaluation-profile-shape',copy.deepcopy(original_ep),True,ep_validator)
 for n in foundation['$defs']['evaluationProfile']['allOf'][1]['required']:
  d=copy.deepcopy(original_ep);d.pop(n);probe('foundation/evaluationProfile','missing-profile-root-'+n,d,False,ep_validator)
 for n in ['scope','subject_digest','contract_digest','evidence_set','profile_complete']:
  d=copy.deepcopy(original_ep);d[n]='hyp:claimed';probe('foundation/evaluationProfile','conformance-tuple-not-evaluation-profile-field-'+n,d,False,ep_validator)
 for n in ['owner_ref','claim_ceiling','admission_rule']:
  d=copy.deepcopy(original_ep);d[n]='hyp:unresolved-or-overclaimed';probe('foundation/evaluationProfile','profile-shape-does-not-resolve-'+n,d,True,ep_validator)
 d=copy.deepcopy(original_ep);d['checks'][0]['purpose']='hyp:one schema check proves every scope obligation';probe('foundation/evaluationProfile','shape-valid-overclaimed-check-purpose',d,True,ep_validator)
 errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in current_validator.iter_errors(original)]
 inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']]
 report={'schema_version':'definition-assurance-Conformance-profile/v1-candidate','status':'PASS-for-qualified-scoped-conformance-hypotheses-and-actual-catalog-shape-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_conformance_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'evaluation_profile_contract_ref':ep[0],'evaluation_profile_status':original_ep['status'],'evaluation_profile_authority_effect':original_ep['authority_effect'],'admitted_Conformance_tuple_schema_ref':None,'schema_probes':probes,'historical_source_current_definition_shape':{'errors':errors,'exact_source_admission_invalidated':False,'semantic_epoch_mismatch_claimed':False},'causal_NOT_EVALUABLE_frame_guard_is_primary_T_axiom':False,'bound_evaluation_runner_executed':False,'generator_module_or_materialization_writer_executed':False,'native_or_live_consumer_executed':False,'actual_conformance_authority_adequacy_or_currentness_created':False,'generic_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified authored exact scoped conformance hypotheses and actual Definition/evaluation-profile catalog/schema observations. Current evaluation-profile contract has no Conformance semantic binding;selected profile remains historical candidate none. No admitted tuple adapter,actual complete/current/adequate evidence,owner authority,scope conformance,consumer alignment,whole-source fidelity or proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_conformance_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_conformance_frames']),'catalog_checks':x['actual_check_count'],'shape_probes':len(x['schema_probes']),'shape_acceptances':sum(y['schema_accepted'] for y in x['schema_probes']),'direct_current_definition_binding_types':x['direct_current_definition_binding_types']},indent=2))
if __name__=='__main__':main()

"""Qualified Evidence hypotheses and exact catalog/schema comparisons;no carrier writer or actual adequacy."""
import copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['identity','kind','carrier','source','claim','subject','scope','provenance','origin_ref','observed_time','currentness_condition','content','evidence_collection','force_relation','assessment','relation_roles']
FORBIDDEN=['existence_is_proof','volume_is_sufficiency','declared_force_is_actual_support','reference_is_authenticated_provenance','time_label_is_currentness','stale_record_is_never_evidence','shared_handle_merges_claim_and_evidence','force_partition_is_exhaustive','support_projection_is_accepted','assessment_label_is_authority','schema_PASS_is_runtime_proof','C13_profile_is_Evidence_contract','other_carrier_admission_is_Evidence_admission','recovered_D38_authenticates_producer','unrecovered_D65_is_verified','nonentailment_denies_supported_real_outcomes']
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];before=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['binding-changed:'+n for n in AXES if before[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':before,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_evidence_proof_truth_adequacy_provenance_currentness_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-bounded-record',copy.deepcopy(before),copy.deepcopy(flags),False)
 add('historical-and-current-records-without-automatic-outcomes',copy.deepcopy(before),copy.deepcopy(flags),False)
 for n in AXES:
  after=copy.deepcopy(before);after[n]='hyp:changed';add('changed-'+n,after,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  f=copy.deepcopy(flags);f[n]=True;add('forbidden-'+n,copy.deepcopy(before),f,True)
 return rows
def frames():
 declarations=['record_declared','provenance_bound','inspectable','claim_explicit','subject_declared','scope_declared','provenance_inspectable','time_declared','currentness_declared','content_inspectable','claim_subject_matches','claim_scope_matches'];handles=['record','claim','subject','scope','provenance','origin','time','currentness','content'];base={'before':envelope(),'after':envelope(),'selected':True,**{n:True for n in declarations},'handles':{n:'hyp:'+n for n in handles},'forces':[{'kind':'support','claim_matches':True,'subject_matches':True,'scope_matches':True}],'silent_current_support':False,'current_claim_declared':True,'currentness_matches':True,'stale':False,'mismatch':False,'claim_itself_role':False,'proof_by_existence_role':False,'governing_roles':[],'assessments':[],'actual_outcome_claim':False};rows=[]
 def assessment():return {'applicable':True,'evidence_matches':True,'claim_matches':True,'subject_matches':True,'scope_matches':True,'handle':'hyp:assessment'}
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('qualified-binding-change-needs-independent-review')
  if x['selected']:
   for n in declarations:
    if not x[n]:errors.append('missing-or-wrong-'+n)
   for n,value in x['handles'].items():
    if not value:errors.append('empty-handle:'+n)
   for force in x['forces']:
    if force['kind'] not in ['support','weakening','unevaluable']:errors.append('unknown-proposed-force')
    for n in ['claim_matches','subject_matches','scope_matches']:
     if not force[n]:errors.append('force-outside-'+n)
   if x['silent_current_support']:
    if not x['current_claim_declared'] or not x['currentness_matches'] or x['stale'] or x['mismatch'] or not any(f['kind']=='support' for f in x['forces']):errors.append('unqualified-silent-current-support')
   if x['claim_itself_role'] or x['proof_by_existence_role']:errors.append('excluded-evidence-role')
   if x['governing_roles'] and not x['assessments']:errors.append('role-without-applicable-assessment')
   for a in x['assessments']:
    if not all(a.values()):errors.append('assessment-not-applicable-exact-or-nonempty')
  if x['actual_outcome_claim']:errors.append('record-force-or-volume-is-not-actual-proof-adequacy-or-authority')
  assert bool(errors)==reject,(id,errors);rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_evidence_proof_truth_adequacy_provenance_currentness_or_authority_verified':False,'universal_scope_currentness_or_evidential_force_proof':False})
 add('bounded-record-with-optional-support',lambda x:None,False)
 for force in ['support','weakening','unevaluable']:add('independent-scoped-'+force,lambda x,force=force:x['forces'][0].update(kind=force),False)
 add('no-force-declaration-required',lambda x:x.update(forces=[]),False)
 add('overlapping-force-declarations',lambda x:x['forces'].append({**x['forces'][0],'kind':'weakening'}),False)
 add('qualified-silent-current-support',lambda x:x.update(silent_current_support=True),False)
 add('stale-record-retains-historical-support',lambda x:x.update(stale=True,currentness_matches=False),False)
 add('mismatched-record-remains-evidence',lambda x:x.update(mismatch=True),False)
 for role in ['decision','authority','admission','conformance']:add('assessment-qualified-'+role,lambda x,role=role:x.update(governing_roles=[role],assessments=[assessment()]),False)
 add('outside-selected-record',lambda x:x.update(selected=False,record_declared=False,forces=[]),False)
 for n in AXES:add('changed-binding-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in declarations:add('missing-'+n,lambda x,n=n:x.update({n:False}),True)
 for n in handles:add('empty-'+n,lambda x,n=n:x['handles'].update({n:''}),True)
 for force in ['support','weakening','unevaluable']:
  for n in ['claim_matches','subject_matches','scope_matches']:add('out-of-bound-'+force+'-'+n,lambda x,force=force,n=n:x['forces'][0].update(kind=force,**{n:False}),True)
 for n in ['current_claim_declared','currentness_matches']:add('silent-current-support-without-'+n,lambda x,n=n:x.update(silent_current_support=True,**{n:False}),True)
 for n in ['stale','mismatch']:add('silent-current-support-with-'+n,lambda x,n=n:x.update(silent_current_support=True,**{n:True}),True)
 add('silent-current-support-without-support-declaration',lambda x:x.update(silent_current_support=True,forces=[]),True)
 for n in ['claim_itself_role','proof_by_existence_role']:add('collapsed-'+n,lambda x,n=n:x.update(**{n:True}),True)
 for role in ['decision','authority','admission','conformance']:add('unqualified-'+role,lambda x,role=role:x.update(governing_roles=[role]),True)
 for n in ['applicable','evidence_matches','claim_matches','subject_matches','scope_matches','handle']:
  def wrong(x,n=n):a=assessment();a[n]='' if n=='handle' else False;x.update(governing_roles=['conformance'],assessments=[a])
  add('assessment-without-'+n,wrong,True)
 add('declared-force-as-actual-authority',lambda x:x.update(actual_outcome_claim=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source']
 paths={'registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','foundation_schema':b.ROOT/'authority/foundation/v1/schema.json','evaluation_profile':b.ROOT/'authority/profiles/definition/v1/evaluation.json','candidate':b.ROOT/'authority/definitions/candidates/0007-cml07-semantic-closure/candidate.json','source':b.ROOT/source['path'],'checker':b.UNIT/'verify_authority_profile.py','C13':b.ROOT/'docs/decisions/0013-foundation-01-admission/decision.json','C13_manifest':b.ROOT/'authority/foundation/v1/manifest.json','C13_receipt':b.ROOT/'authority/foundation/v1/receipts/validation.json'};refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};rows=docs['registry']['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];ep=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.evaluation-profile/v1'];schema=docs['Definition_schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);current_validator=b.c.Draft202012Validator(docs['current_Definition_schema']);foundation=docs['foundation_schema'];b.c.Draft202012Validator.check_schema(foundation);ep_schema={'$ref':'#/$defs/evaluationProfile','$defs':foundation['$defs']};ep_validator=b.c.Draft202012Validator(ep_schema);checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121)
 ck('no-admitted-direct-Evidence-type',not direct)
 ck('current-generic-Definition-v2',len(generic)==1 and generic[0]['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('generic-Definition-separate-current-meaning',generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('historical-generic-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows))
 ck('current-evaluation-profile-contract-C13',len(ep)==1 and ep[0]['admission_decision_ref']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION')
 ck('evaluation-profile-exact-foundation-schema-selector',ep[0]['schema_path']==refs['foundation_schema']['path'] and ep[0]['schema_sha256']==refs['foundation_schema']['sha256'] and ep[0]['schema_selector']=='#/$defs/evaluationProfile')
 ck('evaluation-profile-contract-has-no-Evidence-semantic-binding',ep[0]['semantic_definition_refs']==[])
 ck('CML07-exact-selected-evaluation-profile-binding',any(x['source_ref']=='cal.evaluation.definition/v1' and x['path']==refs['evaluation_profile']['path'] and x['sha256']==refs['evaluation_profile']['sha256'] and x['admission_posture']=='admitted' for x in docs['candidate']['source_bindings']))
 original_ep=docs['evaluation_profile'];ck('evaluation-profile-shape-valid',not list(ep_validator.iter_errors(original_ep)))
 ck('evaluation-profile-historical-candidate-none',original_ep['status']=='candidate-unadmitted' and original_ep['authority_effect']=='none')
 ck('evaluation-profile-exact-Definition-v1-subject',original_ep['subject_artifact_type_ref']=='cal.artifact-type.definition/v1')
 ck('evaluation-profile-collect-all-three-outcomes',original_ep['evaluation_mode']=='collect-all' and original_ep['outcomes']==['PASS','FAIL','NOT_EVALUABLE'])
 ck('seven-recorded-evaluation-checks',len(original_ep['checks'])==7 and len({x['check_id'] for x in original_ep['checks']})==7)
 ck('evaluation-profile-PASS-is-evidence-not-admission','PASS remains evidence and cannot perform the admission' in original_ep['admission_rule'])
 ck('selected-Definition-v1-shape-valid',not list(validator.iter_errors(docs['source'])) and docs['source']['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1')
 ck('retained-body-postures-separate-from-C29-overlay',load('source-checks.json')['historical_embedded_source_postures']==['admitted','candidate-unadmitted','candidate-unadmitted'] and load('source-checks.json')['current_registry_entry_lifecycle']=='admitted')
 c13=docs['C13'];rec=next(x for x in c13['admitted_records'] if x['record_id']=='CAL-EVALUATION-DEFINITION-V1')
 ck('C13-exact-current-decision-bytes',refs['C13']['sha256']=='2aec4fc4cee04804047dbdfecdf521837b0bd1b006fc6b7ea55f46c9a15b4f52' and c13['status']=='owner-admitted')
 ck('C13-exact-profile-record-admission-separate-from-body',rec['path']==refs['evaluation_profile']['path'] and rec['sha256']==refs['evaluation_profile']['sha256']=='8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9' and rec['admission_effect']=='definition-evaluation-profile-admitted')
 for name,key in [('C13_manifest','manifest'),('C13_receipt','validation_receipt')]:ck('C13-exact-'+key,refs[name]['path']==c13['accepted_candidate'][key+'_path'] and refs[name]['sha256']==c13['accepted_candidate'][key+'_sha256'])
 ck('C13-profile-admission-no-semantic-truth-or-authority',any(x['role_id']=='evidence-conformance-owner' and 'Admit the Definition evaluation profile' in x['effect'] and 'neither performs admission' in x['non_effect'] for x in c13['role_scoped_determinations']))
 evaluation=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.evaluation/v1'];ck('Evaluation-v1-carrier-binds-its-own-meaning-not-Evidence',len(evaluation)==1 and evaluation[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.evaluation')['version_ref']] and source['version_ref'] not in evaluation[0]['semantic_definition_refs'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 probes=[]
 def probe(surface,id,doc,expected,selected_validator):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in selected_validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored shape probe '+id+' '+str(errors))
  probes.append({'case_id':id,'surface':surface,'schema_accepted':accepted,'errors':errors,'actual_evidence_proof_truth_adequacy_provenance_currentness_or_authority_verified':False})
 original=docs['source'];probe('Definition/v1','selected-exact-Definition-shape',copy.deepcopy(original),True,validator)
 for n in schema['required']:
  d=copy.deepcopy(original);d.pop(n);probe('Definition/v1','missing-required-root-'+n,d,False,validator)
 for n in ['claim_ref','provenance','observed_at','currentness']:
  d=copy.deepcopy(original);d[n]='hyp:claimed';probe('Definition/v1','tuple-field-not-Definition-schema-'+n,d,False,validator)
 for n in ['definition_id','term','semantic_owner_ref']:
  d=copy.deepcopy(original);d[n]='hyp:unresolved';probe('Definition/v1','shape-does-not-resolve-'+n,d,True,validator)
 d=copy.deepcopy(original);d['voices']['scientific_formal']['normative_statement']='hyp:evidence volume proves truth and authorizes publication';probe('Definition/v1','shape-valid-overclaimed-normative-text',d,True,validator)
 probe('foundation/evaluationProfile','selected-exact-evaluation-profile-shape',copy.deepcopy(original_ep),True,ep_validator)
 for n in foundation['$defs']['evaluationProfile']['allOf'][1]['required']:
  d=copy.deepcopy(original_ep);d.pop(n);probe('foundation/evaluationProfile','missing-profile-root-'+n,d,False,ep_validator)
 for n in ['claim_ref','provenance','content','evidence_scope','currentness']:
  d=copy.deepcopy(original_ep);d[n]='hyp:claimed';probe('foundation/evaluationProfile','evidence-record-not-evaluation-profile-field-'+n,d,False,ep_validator)
 for n in ['owner_ref','claim_ceiling','admission_rule']:
  d=copy.deepcopy(original_ep);d[n]='hyp:unresolved-or-overclaimed';probe('foundation/evaluationProfile','profile-shape-does-not-resolve-'+n,d,True,ep_validator)
 d=copy.deepcopy(original_ep);d['checks'][0]['purpose']='hyp:one schema check proves actual evidence adequacy and truth';probe('foundation/evaluationProfile','shape-valid-overclaimed-check-purpose',d,True,ep_validator)
 errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in current_validator.iter_errors(original)]
 inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']]
 report={'schema_version':'definition-assurance-Evidence-profile/v1-candidate','status':'PASS-for-qualified-bounded-Evidence-hypotheses-and-actual-catalog-shape-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_evidence_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'evaluation_profile_contract_ref':ep[0],'evaluation_profile_status':original_ep['status'],'evaluation_profile_authority_effect':original_ep['authority_effect'],'admitted_Evidence_tuple_schema_ref':None,'schema_probes':probes,'historical_source_current_definition_shape':{'errors':errors,'exact_source_admission_invalidated':False,'semantic_epoch_mismatch_claimed':False},'actual_evidential_force_or_authority_queries_assumed_in_T':False,'selected_evaluation_profile_is_Evidence_source':False,'exact_evaluation_profile_record_admission_ref':c13['decision_id'],'exact_evaluation_profile_record_admission_effect':rec['admission_effect'],'bound_evaluation_runner_executed':False,'generator_module_or_materialization_writer_executed':False,'native_or_live_consumer_executed':False,'actual_evidence_proof_truth_adequacy_provenance_currentness_or_authority_created':False,'generic_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified bounded Evidence hypotheses and actual Definition/evaluation-profile catalog/schema observations. No direct Evidence carrier. C13 separately admits the exact profile record despite its historical candidate body;neither it nor Evaluation/v1 binds Evidence meaning. No package or live runner,writer,actual proof/truth/sufficiency/provenance/currentness/authority,accepted carrier/consumer correspondence,source fidelity or whole proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_evidence_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_evidence_frames']),'catalog_checks':x['actual_check_count'],'shape_probes':len(x['schema_probes']),'shape_acceptances':sum(y['schema_accepted'] for y in x['schema_probes']),'direct_current_definition_binding_types':x['direct_current_definition_binding_types']},indent=2))
if __name__=='__main__':main()

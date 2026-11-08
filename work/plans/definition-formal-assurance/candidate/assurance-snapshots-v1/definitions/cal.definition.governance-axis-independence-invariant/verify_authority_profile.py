"""Qualified Governance-Axis lifecycle/record hypotheses and actual catalog/prototype/Definition-shape observations."""
import copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['identity','kind','carrier','owner_scope','sources','subject','scope','before','after','intended_axis','value_map','information_map','source_map','change_record']
FORBIDDEN=['maturity_proves_evidence','evidence_proves_commitment','commitment_proves_authority','kind_proves_status','provenance_proves_canonicality','owner_proves_permission','utility_proves_promotion','tuple_proves_complete_schema','unknown_means_false','source_local_means_authenticated','validity_proves_actual_transition']
def envelope():return {n:'hyp:'+n for n in AXES}
def qualify(before,after,flags):return ['binding-changed:'+n for n in AXES if before[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if flags[n]]
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,expected):
  errors=qualify(base,after,f);assert bool(errors)==expected;rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'actual_governance_record_authority_or_transition_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False);add('declared-move-with-independent-no-actual-authority-or-transition-claim',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:a=copy.deepcopy(base);a[n]='hyp:changed';add('changed-'+n,a,copy.deepcopy(flags),True)
 for n in FORBIDDEN:f=copy.deepcopy(flags);f[n]=True;add('forbidden-'+n,copy.deepcopy(base),f,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'intended_axis':'status','changed_axes':['status'],'declared_axes':['kind','status','evidence','commitment','provenance','owner','residue'],'recorded_other_axes':[],'record_subject_matches':True,'record_scope_matches':True,'validity_claim':True,'unknown_as_false':False,'source_local':False,'source_reference_present':True,'actual_authority_or_transition_claim':False};rows=[]
 def add(id,mutate,expected):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('qualified-binding-change-needs-independent-review')
  if x['validity_claim']:
   if x['intended_axis'] not in x['changed_axes']:errors.append('intended-axis-not-changed')
   if any(a not in x['declared_axes'] for a in x['changed_axes']):errors.append('undeclared-extra-axis')
   extras=[a for a in x['changed_axes'] if a!=x['intended_axis']]
   if any(a not in x['recorded_other_axes'] for a in extras):errors.append('unrecorded-other-axis-change')
   if extras and (not x['record_subject_matches'] or not x['record_scope_matches']):errors.append('additional-record-binding-mismatch')
  if x['unknown_as_false']:errors.append('information-state-not-truth-value')
  if x['source_local'] and not x['source_reference_present']:errors.append('source-local-needs-reference')
  if x['actual_authority_or_transition_claim']:errors.append('declared-validity-not-actual-authority-or-execution')
  assert bool(errors)==expected;rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'universal_frame_record_authority_or_independence_proof':False})
 add('intended-only-without-additional-record',lambda x:None,False)
 add('explicit-recorded-status-and-evidence',lambda x:x.update(changed_axes=['status','evidence'],recorded_other_axes=['evidence']),False)
 add('information-only-intended-change',lambda x:None,False)
 add('source-local-intended-binding-change',lambda x:x.update(intended_axis='provenance',changed_axes=['provenance'],source_local=True),False)
 add('idempotent-reaffirmation-without-validity-claim',lambda x:x.update(changed_axes=[],validity_claim=False),False)
 add('explicit-declared-extra-axis-change',lambda x:x.update(changed_axes=['status','custom'],declared_axes=x['declared_axes']+['custom'],recorded_other_axes=['custom']),False)
 for n in ['sources','subject','scope','before','after','intended_axis','value_map','information_map','source_map','change_record']:add('changed-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 add('validity-without-intended-change',lambda x:x.update(changed_axes=[]),True)
 add('unrecorded-other-axis-change',lambda x:x.update(changed_axes=['status','evidence']),True)
 add('wrong-additional-record-subject',lambda x:x.update(changed_axes=['status','evidence'],recorded_other_axes=['evidence'],record_subject_matches=False),True)
 add('wrong-additional-record-scope',lambda x:x.update(changed_axes=['status','evidence'],recorded_other_axes=['evidence'],record_scope_matches=False),True)
 add('unknown-as-false',lambda x:x.update(unknown_as_false=True),True)
 add('source-local-without-reference',lambda x:x.update(source_local=True,source_reference_present=False),True)
 add('undeclared-extra-axis',lambda x:x.update(changed_axes=['status','custom'],recorded_other_axes=['custom']),True)
 add('declared-validity-as-actual-authority',lambda x:x.update(actual_authority_or_transition_claim=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];paths={'registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','prototype':b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-governance-axis-independence-invariant/v1/artifact.json','Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','source':b.ROOT/source['path'],'checker':b.UNIT/'verify_authority_profile.py'};refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};rows=docs['registry']['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];proto=docs['prototype'];schema=docs['Definition_schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);current_validator=b.c.Draft202012Validator(docs['current_Definition_schema']);checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121)
 ck('no-admitted-direct-Governance-Axis-invariant-type',not direct)
 ck('no-current-generic-invariant-carrier',not any(x['semantic_kind']=='invariant' for x in current))
 ck('current-generic-Definition-v2',len(generic)==1 and generic[0]['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('generic-Definition-binds-current-Definition-meaning',generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('historical-generic-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows))
 ck('prototype-remains-prototype-scaffold',proto['status']=='prototype-scaffold')
 ck('prototype-authority-effect-none',proto['authority_effect']=='none')
 ck('prototype-exact-normalized-identity',proto['normalized_contract']['concept_id']==proto['target_id']=='semantic.governance-axis-independence-invariant')
 ck('prototype-independent-kind-carrier-owner-axes',proto['normalized_contract']['semantic_kind']=='invariant' and proto['normalized_contract']['carrier_ref']=='type.invariant' and proto['normalized_contract']['owner_scope']=='scope.shared-authority')
 ck('prototype-no-admitted-lifecycle-transition-schema',proto['four_facets']['schema']['admitted_schema_ref'] is None and proto['four_facets']['schema']['schema_state']=='definition-voice-shape-prototyped')
 observed=load('source-checks.json')['selected_source_sections']
 for label,sr,section in zip(['D23'],proto['source_refs'],observed):
  ck('prototype-'+label+'-selector-and-digest',sr['selector']==section['source_ref']['selector'] and sr['section_sha256']==section['sha256'])
 ck('prototype-D23-reclassify-disposition',[(x['legacy_id'],x['decision']) for x in proto['accepted_source_decisions']]==[('CAV2-D23','reclassify')])
 ck('prototype-normalization-owner-decision-not-governance-execution',proto['owner_decision_ref']=='CAL-DECISION-0012-NORMALIZE-01-DEFAULTS' and proto['normalization_ref']=='CAL-NORMALIZE-01')
 ck('family-specific-admitted-type-gap-preserved',any('family-specific admitted Artifact Type' in x for x in proto['gaps']))
 ck('selected-Definition-v1-shape-valid',not list(validator.iter_errors(docs['source'])) and docs['source']['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1')
 ck('historical-body-and-C53-overlay-separate',all(x['admission_posture']=='candidate-unadmitted' for x in docs['source']['source_refs']) and load('source-checks.json')['current_registry_entry_lifecycle']=='admitted')
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 probes=[]
 def probe(id,doc,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored Definition-shape probe '+id+' '+str(errors))
  probes.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_governance_record_authority_or_transition_verified':False,'scope':'Definition/v1 shape only;no executable lifecycle or transition carrier'})
 original=docs['source'];probe('selected-exact-Definition-shape',copy.deepcopy(original),True)
 for n in schema['required']:
  d=copy.deepcopy(original);d.pop(n);probe('missing-required-root-'+n,d,False)
 for n in ['lifecycle_posture','governance_move','component_information','additional_change_record']:
  d=copy.deepcopy(original);d[n]='hyp:claimed';probe('governance-field-not-in-Definition-schema-'+n,d,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  d=copy.deepcopy(original);d[n]='hyp:unresolved';probe('shape-does-not-resolve-'+n,d,True)
 d=copy.deepcopy(original);d['voices']['scientific_formal']['normative_statement']='hyp:governance move grants canonical authority';probe('shape-valid-overclaimed-normative-text',d,True)
 errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in current_validator.iter_errors(original)]
 inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']];report={'schema_version':'definition-assurance-GAI-profile/v1-candidate','status':'PASS-for-qualified-governance-hypotheses-and-actual-catalog-prototype-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_governance_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'prototype_status':proto['status'],'prototype_authority_effect':proto['authority_effect'],'admitted_lifecycle_transition_schema_ref':None,'schema_probe_surface':'selected Definition/v1 shape;generic Definition/v2 is not an executable lifecycle or transition adapter','schema_probes':probes,'historical_source_current_definition_shape':{'errors':errors,'exact_source_admission_invalidated':False,'semantic_epoch_mismatch_claimed':False},'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'native_or_live_consumer_executed':False,'actual_governance_record_authority_or_transition_created':False,'generic_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified authored lifecycle/frame hypotheses plus actual registry,prototype,D23 source-reference and Definition-shape observations. Generic Definition/v2 binds current Definition@1 meaning. No direct admitted invariant/type.invariant lifecycle or transition schema,actual record write,authority,semantic independence,transition execution,owner acceptance or consumer proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({'status':r['status'],'profiles':len(r['profiles']),'rejected_profiles':sum(x['expected_rejection'] for x in r['profiles']),'frames':len(r['finite_governance_frames']),'rejected_frames':sum(x['expected_rejection'] for x in r['finite_governance_frames']),'catalog_checks':r['actual_check_count'],'Definition_schema_probes':len(r['schema_probes']),'schema_acceptances':sum(x['schema_accepted'] for x in r['schema_probes']),'direct_current_definition_binding_types':r['direct_current_definition_binding_types']},indent=2))
if __name__=='__main__':main()

"""Qualified Gate record hypotheses and actual catalog/prototype/Definition-shape observations."""
import copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['identity','kind','carrier','owner_scope','sources','owner_route','scope','inputs','criteria','verdicts','required_evidence','residue','record_location','downstream_effect']
FORBIDDEN=['shape_proves_decision','record_proves_authority','evidence_presence_proves_adequacy','criteria_presence_proves_correctness','pass_proves_execution','flag_is_silent_pass','block_proves_enforcement','defer_proves_handoff','normalization_proves_identity_equivalence','validator_proves_owner_acceptance','generic_carrier_proves_Gate_consumer']
def envelope():return {n:'hyp:'+n for n in AXES}
def qualify(before,after,flags):return ['binding-changed:'+n for n in AXES if before[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if flags[n]]
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,expected):
  errors=qualify(base,after,f);assert bool(errors)==expected;rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'actual_Gate_record_authority_or_effect_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False);add('declared-verdict-with-independent-no-actual-effect-claim',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:a=copy.deepcopy(base);a[n]='hyp:changed';add('changed-'+n,a,copy.deepcopy(flags),True)
 for n in FORBIDDEN:f=copy.deepcopy(flags);f[n]=True;add('forbidden-'+n,copy.deepcopy(base),f,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'verdict':'pass','record_seen':True,'owner_recorded':True,'evidence_recorded':True,'effect_recorded':True,'risk_named':False,'follow_up_named':False,'silent_pass':False,'deferred_route':'same','admissibility_claim':True,'actual_effect_claim':False};rows=[]
 def add(id,mutate,expected):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('qualified-binding-change-needs-independent-review')
  if x['admissibility_claim'] and not all(x[n] for n in ['record_seen','owner_recorded','evidence_recorded','effect_recorded']):errors.append('missing-necessary-record')
  if x['admissibility_claim'] and x['verdict']=='flag' and (not x['risk_named'] or not x['follow_up_named'] or x['silent_pass']):errors.append('flag-needs-named-risk-follow-up-and-not-silent-pass')
  if x['admissibility_claim'] and x['verdict']=='defer' and x['deferred_route']=='same':errors.append('defer-needs-another-owner-route')
  if x['actual_effect_claim']:errors.append('declared-verdict-is-not-actual-effect-evidence')
  assert bool(errors)==expected;rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'universal_record_authority_correctness_or_effect_proof':False})
 add('recorded-default-pass',lambda x:None,False)
 add('recorded-flag-named-risk-follow-up',lambda x:x.update(verdict='flag',risk_named=True,follow_up_named=True),False)
 add('recorded-block-stop-policy',lambda x:x.update(verdict='block'),False)
 add('recorded-defer-another-route',lambda x:x.update(verdict='defer',deferred_route='another'),False)
 add('unrecorded-invocation-without-admissibility-claim',lambda x:x.update(record_seen=False,admissibility_claim=False),False)
 for n in ['sources','owner_route','scope','inputs','criteria','verdicts','required_evidence','residue','record_location','downstream_effect']:add('changed-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in ['owner_recorded','evidence_recorded','effect_recorded']:add('missing-'+n,lambda x,n=n:x.update({n:False}),True)
 add('flag-missing-follow-up',lambda x:x.update(verdict='flag',risk_named=True),True)
 add('flag-as-silent-pass',lambda x:x.update(verdict='flag',risk_named=True,follow_up_named=True,silent_pass=True),True)
 add('defer-same-route',lambda x:x.update(verdict='defer'),True)
 add('declared-verdict-as-actual-effect',lambda x:x.update(actual_effect_claim=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];paths={'registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','prototype':b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-gate/v1/artifact.json','Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','source':b.ROOT/source['path'],'checker':b.UNIT/'verify_authority_profile.py'};refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};rows=docs['registry']['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];proto=docs['prototype'];schema=docs['Definition_schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);current_validator=b.c.Draft202012Validator(docs['current_Definition_schema']);checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121)
 ck('no-admitted-direct-Gate-type',not direct)
 ck('current-generic-Definition-v2',len(generic)==1 and generic[0]['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('generic-Definition-binds-current-Definition-meaning',generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('historical-generic-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows))
 ck('prototype-remains-prototype-scaffold',proto['status']=='prototype-scaffold')
 ck('prototype-authority-effect-none',proto['authority_effect']=='none')
 ck('prototype-exact-normalized-identity',proto['normalized_contract']['concept_id']==proto['target_id']=='semantic.gate')
 ck('prototype-independent-kind-carrier-owner-axes',proto['normalized_contract']['semantic_kind']=='definition' and proto['normalized_contract']['carrier_ref']=='type.definition' and proto['normalized_contract']['owner_scope']=='scope.shared-authority')
 ck('prototype-no-admitted-Gate-schema',proto['four_facets']['schema']['admitted_schema_ref'] is None and proto['four_facets']['schema']['schema_state']=='definition-voice-shape-prototyped')
 observed=load('source-checks.json')['selected_source_sections']
 for label,sr,section in zip(['D5','D37'],proto['source_refs'],observed):
  ck('prototype-'+label+'-selector-and-digest',sr['selector']==section['source_ref']['selector'] and sr['section_sha256']==section['sha256'])
 ck('prototype-D5-collapse-D37-split-dispositions',[(x['legacy_id'],x['decision']) for x in proto['accepted_source_decisions']]==[('CAV2-D5','collapse'),('CAV2-D37','split')])
 ck('prototype-normalization-owner-decision-not-Gate-execution',proto['owner_decision_ref']=='CAL-DECISION-0012-NORMALIZE-01-DEFAULTS' and proto['normalization_ref']=='CAL-NORMALIZE-01')
 ck('family-specific-admitted-type-gap-preserved',any('family-specific admitted Artifact Type' in x for x in proto['gaps']))
 ck('selected-Definition-v1-shape-valid',not list(validator.iter_errors(docs['source'])) and docs['source']['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1')
 ck('historical-body-and-C53-overlay-separate',all(x['admission_posture']=='candidate-unadmitted' for x in docs['source']['source_refs']) and load('source-checks.json')['current_registry_entry_lifecycle']=='admitted')
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 probes=[]
 def probe(id,doc,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored Definition-shape probe '+id+' '+str(errors))
  probes.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_Gate_record_authority_or_effect_verified':False,'scope':'Definition/v1 shape only;no executable Gate decision or record carrier'})
 original=docs['source'];probe('selected-exact-Definition-shape',copy.deepcopy(original),True)
 for n in schema['required']:
  d=copy.deepcopy(original);d.pop(n);probe('missing-required-root-'+n,d,False)
 for n in ['gate_configuration','decision_function','admissible_verdict','gate_record']:
  d=copy.deepcopy(original);d[n]='hyp:claimed';probe('Gate-field-not-in-Definition-schema-'+n,d,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  d=copy.deepcopy(original);d[n]='hyp:unresolved';probe('shape-does-not-resolve-'+n,d,True)
 d=copy.deepcopy(original);d['voices']['scientific_formal']['normative_statement']='hyp:gate proves correctness';probe('shape-valid-overclaimed-normative-text',d,True)
 errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in current_validator.iter_errors(original)]
 inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']];report={'schema_version':'definition-assurance-Gate-profile/v1-candidate','status':'PASS-for-qualified-Gate-hypotheses-and-actual-catalog-prototype-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_Gate_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'prototype_status':proto['status'],'prototype_authority_effect':proto['authority_effect'],'admitted_Gate_schema_ref':None,'schema_probe_surface':'selected Definition/v1 shape;generic Definition/v2 is not an executable Gate adapter','schema_probes':probes,'historical_source_current_definition_shape':{'errors':errors,'exact_source_admission_invalidated':False,'semantic_epoch_mismatch_claimed':False},'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'native_or_live_consumer_executed':False,'actual_Gate_record_authority_or_effect_created':False,'generic_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified authored hypotheses and finite record frames plus actual registry,prototype,source-reference and Definition-shape observations. Generic Definition/v2 binds current Definition@1 meaning. No direct admitted Gate type,executed decision function,actual record write,authority,correctness,downstream effect,owner acceptance or consumer proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({'status':r['status'],'profiles':len(r['profiles']),'rejected_profiles':sum(x['expected_rejection'] for x in r['profiles']),'frames':len(r['finite_Gate_frames']),'rejected_frames':sum(x['expected_rejection'] for x in r['finite_Gate_frames']),'catalog_checks':r['actual_check_count'],'Definition_schema_probes':len(r['schema_probes']),'schema_acceptances':sum(x['schema_accepted'] for x in r['schema_probes']),'direct_current_definition_binding_types':r['direct_current_definition_binding_types']},indent=2))
if __name__=='__main__':main()

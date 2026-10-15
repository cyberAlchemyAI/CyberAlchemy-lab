"""Qualified claim/support/treatment hypotheses and actual catalog/prototype/schema observations."""
import copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['identity','kind','carrier','owner_scope','sources','claim','claim_type','context','interpreter','asserted_strength','authority_effect_strength','validation_status_strength','publication_posture_strength','support_package','support_items','treatment']
FORBIDDEN=['citation_proves_truth','schema_proves_semantic_alignment','validation_proves_publication','owner_decision_support_proves_authority','accepted_premise_kind_is_assumption','private_support_means_no_possible_honest_claim','compatible_label_proves_evidence_adequacy','gate_route_proves_clearance','downgrade_declaration_proves_execution','strength_must_be_numeric_total_order','only_formal_proof_counts','source_local_means_authenticated']
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,expected):
  errors=['binding-changed:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==expected
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'actual_truth_authority_or_remediation_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-support-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('bounded-honest-claim-without-actual-authority',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  a=copy.deepcopy(base);a[n]='hyp:changed';add('changed-'+n,a,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  f=copy.deepcopy(flags);f[n]=True;add('forbidden-'+n,copy.deepcopy(base),f,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'applicable':True,'context_declared':True,'interpreter_declared':True,'interpreter_matches_type_context':True,'interpreter_handle':'hyp:interpreter','interpreter_kinds':['DomainInterpreter'],'claim_handle':'hyp:claim','has_support':True,'cites_package':True,'package_declared':True,'package_matches_type_context_interpreter':True,'package_handle':'hyp:package','items':[{'matches_type_context':True,'handle':'hyp:item','kinds':['SourceCitationSupport']}],'dimension_comparisons':{n:True for n in b.DIMENSIONS},'within_bound':True,'honest_wording':True,'compatible_label':True,'postures':[],'risky_label':False,'treatments':[],'treatment_reference':'hyp:treatment','formal_proof_only_role':False,'maximal_certainty_required_role':False,'actual_outcome_claim':False};rows=[]
 def add(id,mutate,expected):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('qualified-binding-change-needs-independent-review')
  if x['applicable']:
   for n in ['context_declared','interpreter_declared','interpreter_matches_type_context']:
    if not x[n]:errors.append('missing-or-wrong-'+n)
   for n in ['interpreter_handle','claim_handle']:
    if not x[n]:errors.append('missing-'+n)
   if not any(k in b.INTERPRETER_KINDS for k in x['interpreter_kinds']):errors.append('no-eligible-interpreter-kind')
   if x['has_support']!=(x['cites_package'] and x['package_declared']):errors.append('support-presence-not-cited-declared-package')
   if x['has_support']:
    if not x['package_matches_type_context_interpreter']:errors.append('package-binding-mismatch')
    if not x['package_handle']:errors.append('package-handle-missing')
    if not x['items']:errors.append('no-included-support-item')
    for item in x['items']:
     if not item['matches_type_context']:errors.append('item-binding-mismatch')
     if not item['handle']:errors.append('item-handle-missing')
     if not any(k in b.ITEM_KINDS for k in item['kinds']):errors.append('no-eligible-support-kind')
   bound=x['has_support'] and all(x['dimension_comparisons'].values())
   if x['within_bound']!=bound:errors.append('four-dimension-bound-label-mismatch')
   if x['compatible_label']!=(x['has_support'] and bound and x['honest_wording']):errors.append('compatible-honest-bound-label-mismatch')
   risk=not x['has_support'] or any(p in b.POSTURES for p in x['postures']) or (x['has_support'] and not bound)
   if x['risky_label']!=risk:errors.append('risk-label-mismatch')
   if risk and (not any(t in b.TREATMENTS for t in x['treatments']) or not x['treatment_reference']):errors.append('risk-needs-explicit-treatment-reference')
   if not x['has_support'] and not any(t in x['treatments'] for t in ['CandidateWordingDeclared','HypothesisWordingDeclared']):errors.append('absent-support-needs-default-wording')
  if x['formal_proof_only_role'] or x['maximal_certainty_required_role']:errors.append('excluded-epistemic-role')
  if x['actual_outcome_claim']:errors.append('declaration-not-actual-truth-authority-or-execution')
  assert bool(errors)==expected,(id,errors);rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'actual_truth_authority_or_remediation_verified':False,'universal_epistemic_or_strength_order_proof':False})
 def risky(x,posture,treatment):x.update(postures=[posture],risky_label=True,treatments=[treatment])
 def absent(x,treatment):x.update(has_support=False,cites_package=False,package_declared=False,items=[],dimension_comparisons={n:False for n in b.DIMENSIONS},within_bound=False,compatible_label=False,risky_label=True,treatments=[treatment])
 def weak(x,dimension):x['dimension_comparisons'][dimension]=False;x.update(within_bound=False,compatible_label=False,risky_label=True,treatments=['ResidueFlagDeclared'])
 add('cited-package-with-honest-modest-bound',lambda x:None,False)
 for kind in b.ITEM_KINDS:add('plural-support-'+kind,lambda x,kind=kind:x['items'][0].update(kinds=[kind]),False)
 for kind in b.INTERPRETER_KINDS:add('domain-specific-interpreter-'+kind,lambda x,kind=kind:x.update(interpreter_kinds=[kind]),False)
 for posture,treatment in zip(b.POSTURES,['DowngradeDeclared','ResidueFlagDeclared','GateRouteDeclared','GoverningBlockDeclared','CandidateWordingDeclared']):add('bounded-but-treated-'+posture,lambda x,posture=posture,treatment=treatment:risky(x,posture,treatment),False)
 for n in b.DIMENSIONS:add('over-bound-with-explicit-treatment-'+n,lambda x,n=n:weak(x,n),False)
 for t in ['CandidateWordingDeclared','HypothesisWordingDeclared']:add('absent-support-'+t,lambda x,t=t:absent(x,t),False)
 def overlaps(x):risky(x,'PrivateSupport','ResidueFlagDeclared');x['treatments'].append('GateRouteDeclared');x['items'][0]['kinds'].append('AcceptedPremiseSupport');x['interpreter_kinds'].append('ConstitutionInterpreter')
 add('support-interpreter-treatment-overlap',overlaps,False)
 add('outside-applicable-scope',lambda x:x.update(applicable=False,has_support=False,within_bound=False),False)
 for n in AXES:add('changed-binding-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in ['context_declared','interpreter_declared','interpreter_matches_type_context','package_matches_type_context_interpreter']:add('missing-'+n,lambda x,n=n:x.update({n:False}),True)
 for n in ['interpreter_handle','claim_handle','package_handle']:add('empty-'+n,lambda x,n=n:x.update({n:''}),True)
 add('missing-interpreter-kind',lambda x:x.update(interpreter_kinds=[]),True)
 for n in ['cites_package','package_declared','has_support']:add('support-presence-mismatch-'+n,lambda x,n=n:x.update({n:False}),True)
 add('cited-package-without-items',lambda x:x.update(items=[]),True)
 add('item-context-type-mismatch',lambda x:x['items'][0].update(matches_type_context=False),True)
 add('item-without-handle',lambda x:x['items'][0].update(handle=''),True)
 add('item-with-no-support-kind',lambda x:x['items'][0].update(kinds=[]),True)
 for n in b.DIMENSIONS:add('untreated-or-mislabelled-overclaim-'+n,lambda x,n=n:x['dimension_comparisons'].update({n:False}),True)
 add('compatible-without-honest-wording',lambda x:x.update(honest_wording=False),True)
 add('spurious-risk-label',lambda x:x.update(risky_label=True),True)
 for p in b.POSTURES:add('missing-treatment-'+p,lambda x,p=p:x.update(postures=[p],risky_label=True),True)
 def missing_reference(x):risky(x,'PrivateSupport','ResidueFlagDeclared');x['treatment_reference']=''
 add('treatment-without-reference',missing_reference,True)
 add('absent-support-gate-does-not-replace-default-wording',lambda x:absent(x,'GateRouteDeclared'),True)
 for n in ['formal_proof_only_role','maximal_certainty_required_role','actual_outcome_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];paths={'registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','prototype':b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-claim-support-compatibility-invariant/v1/artifact.json','Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','source':b.ROOT/source['path'],'checker':b.UNIT/'verify_authority_profile.py'};refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};rows=docs['registry']['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];proto=docs['prototype'];schema=docs['Definition_schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);current_validator=b.c.Draft202012Validator(docs['current_Definition_schema']);checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121)
 ck('no-admitted-direct-Claim-Support-invariant-type',not direct)
 ck('no-current-generic-invariant-carrier',not any(x['semantic_kind']=='invariant' for x in current))
 ck('current-generic-Definition-v2',len(generic)==1 and generic[0]['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('generic-Definition-binds-current-Definition-meaning',generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('historical-generic-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows))
 ck('prototype-remains-prototype-scaffold',proto['status']=='prototype-scaffold')
 ck('prototype-authority-effect-none',proto['authority_effect']=='none')
 ck('prototype-exact-normalized-identity',proto['normalized_contract']['concept_id']==proto['target_id']=='semantic.claim-support-compatibility-invariant')
 ck('prototype-independent-kind-carrier-owner-axes',proto['normalized_contract']['semantic_kind']=='invariant' and proto['normalized_contract']['carrier_ref']=='type.invariant' and proto['normalized_contract']['owner_scope']=='scope.shared-authority')
 ck('prototype-no-admitted-claim-support-schema',proto['four_facets']['schema']['admitted_schema_ref'] is None and proto['four_facets']['schema']['schema_state']=='definition-voice-shape-prototyped')
 observed=load('source-checks.json')['selected_source_sections']
 for label,sr,section in zip(['D38'],proto['source_refs'],observed):
  ck('prototype-'+label+'-selector-and-digest',sr['selector']==section['source_ref']['selector'] and sr['section_sha256']==section['sha256'])
 ck('prototype-D38-reclassify-disposition',[(x['legacy_id'],x['decision']) for x in proto['accepted_source_decisions']]==[('CAV2-D38','reclassify')])
 ck('prototype-normalization-owner-decision-not-bridge-execution',proto['owner_decision_ref']=='CAL-DECISION-0012-NORMALIZE-01-DEFAULTS' and proto['normalization_ref']=='CAL-NORMALIZE-01')
 ck('family-specific-admitted-type-gap-preserved',any('family-specific admitted Artifact Type' in x for x in proto['gaps']))
 ck('selected-Definition-v1-shape-valid',not list(validator.iter_errors(docs['source'])) and docs['source']['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1')
 ck('historical-body-and-C53-overlay-separate',all(x['admission_posture']=='candidate-unadmitted' for x in docs['source']['source_refs']) and load('source-checks.json')['current_registry_entry_lifecycle']=='admitted')
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 probes=[]
 def probe(id,doc,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored Definition-shape probe '+id+' '+str(errors))
  probes.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_truth_authority_or_remediation_verified':False,'scope':'Definition/v1 shape only;no executable claim or support carrier'})
 original=docs['source'];probe('selected-exact-Definition-shape',copy.deepcopy(original),True)
 for n in schema['required']:
  d=copy.deepcopy(original);d.pop(n);probe('missing-required-root-'+n,d,False)
 for n in ['asserted_strength','support_package','support_items','remediation']:
  d=copy.deepcopy(original);d[n]='hyp:claimed';probe('governance-field-not-in-Definition-schema-'+n,d,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  d=copy.deepcopy(original);d[n]='hyp:unresolved';probe('shape-does-not-resolve-'+n,d,True)
 d=copy.deepcopy(original);d['voices']['scientific_formal']['normative_statement']='hyp:cited support proves truth and authorizes publication';probe('shape-valid-overclaimed-normative-text',d,True)
 errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in current_validator.iter_errors(original)]
 inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']];report={'schema_version':'definition-assurance-ClaimSupport-profile/v1-candidate','status':'PASS-for-qualified-claim-support-hypotheses-and-actual-catalog-prototype-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_claim_support_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'prototype_status':proto['status'],'prototype_authority_effect':proto['authority_effect'],'admitted_claim_support_execution_schema_ref':None,'schema_probe_surface':'selected Definition/v1 shape;generic Definition/v2 is not an executable claim or support adapter','schema_probes':probes,'historical_source_current_definition_shape':{'errors':errors,'exact_source_admission_invalidated':False,'semantic_epoch_mismatch_claimed':False},'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'native_or_live_consumer_executed':False,'actual_truth_authority_or_remediation_created':False,'generic_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified authored claim/support hypotheses plus actual registry,prototype,D38 source-reference and Definition-shape observations. Generic Definition/v2 binds current Definition@1 meaning. No direct admitted invariant/type.invariant claim or support schema,actual truth,authority,support adequacy,publication,gate clearance or remediation execution,owner acceptance or consumer proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({'status':r['status'],'profiles':len(r['profiles']),'rejected_profiles':sum(x['expected_rejection'] for x in r['profiles']),'frames':len(r['finite_claim_support_frames']),'rejected_frames':sum(x['expected_rejection'] for x in r['finite_claim_support_frames']),'catalog_checks':r['actual_check_count'],'Definition_schema_probes':len(r['schema_probes']),'schema_acceptances':sum(x['schema_accepted'] for x in r['schema_probes']),'direct_current_definition_binding_types':r['direct_current_definition_binding_types']},indent=2))
if __name__=='__main__':main()

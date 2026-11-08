"""Qualified Root-Axis binding/frame hypotheses and actual catalog/prototype/Definition-shape observations."""
import copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['identity','kind','carrier','owner_scope','sources','context','decision','scope','source_axis','target_axis','first_move','second_move','bridge','direction','evidence','effect']
FORBIDDEN=['axis_label_proves_semantic_identity','independent_moves_require_bridge','declared_bridge_proves_admission','reference_proves_evidence_adequacy','gate_is_typed_coupling','direction_label_proves_execution','source_local_means_authenticated','orthogonality_proves_statistical_independence','orthogonality_proves_consistency','valid_move_proves_target_authority']
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,expected):
  errors=['binding-changed:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==expected
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'actual_bridge_authority_or_cross_axis_execution_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('two-independent-moves-without-implied-cochange',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  a=copy.deepcopy(base);a[n]='hyp:changed';add('changed-'+n,a,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  f=copy.deepcopy(flags);f[n]=True;add('forbidden-'+n,copy.deepcopy(base),f,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'applicable':True,'source_axis':'left','target_axis':'right','context_matches':True,'decision_matches':True,'axis_move_bindings_match':True,'both_axes_declared_relevant':True,'has_bridge':False,'bridge_declared':False,'bridge_endpoints_match':True,'bridge_context_decision_match':True,'kinds':[],'direction_named':False,'symmetry_named':False,'direction_reference':'hyp:direction','effect_reference':'hyp:effect','evidence_reference':'hyp:evidence','independent_variation_declared':True,'claimed_cross_inference':False,'not_silent':False,'first_move_valid':True,'second_move_valid':True,'decision_depends_on_cochange':False,'typed_coupling_represented':False,'typed_coupling_reference':'','classification_question':False,'classification_reference_declared':False,'classification_reference':'','lifecycle_question':False,'lifecycle_reference_declared':False,'lifecycle_reference':'','nonindependent_question':False,'actual_authority_execution_or_scientific_claim':False}
 rows=[]
 def add(id,mutate,expected):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('qualified-binding-change-needs-independent-review')
  if x['applicable']:
   if x['source_axis']==x['target_axis']:errors.append('axis-identities-not-distinct')
   for n in ['context_matches','decision_matches','axis_move_bindings_match','both_axes_declared_relevant']:
    if not x[n]:errors.append('missing-or-wrong-'+n)
   if x['has_bridge']!=x['bridge_declared']:errors.append('bridge-presence-not-declaration')
   if x['has_bridge']:
    for n in ['bridge_endpoints_match','bridge_context_decision_match']:
     if not x[n]:errors.append('wrong-'+n)
    if not any(k in b.KINDS for k in x['kinds']):errors.append('no-eligible-bridge-kind')
    if not (x['direction_named'] or x['symmetry_named']):errors.append('no-named-direction-or-symmetry')
    for n in ['direction_reference','effect_reference','evidence_reference']:
     if not x[n]:errors.append('missing-'+n)
   else:
    if not x['independent_variation_declared']:errors.append('undeclared-independent-variation')
    if x['claimed_cross_inference']:errors.append('silent-inference-without-bridge')
   if x['claimed_cross_inference'] and (not x['has_bridge'] or not x['not_silent'] or not x['first_move_valid']):errors.append('cross-inference-necessary-guard-fails')
   if x['decision_depends_on_cochange'] and (not x['claimed_cross_inference'] or not x['typed_coupling_represented'] or not x['typed_coupling_reference']):errors.append('dependent-decision-needs-explicit-typed-coupling-reference')
   for q in ['classification','lifecycle']:
    if x[q+'_question'] and (not x[q+'_reference_declared'] or not x[q+'_reference']):errors.append('unrouted-'+q+'-question')
   if x['nonindependent_question'] and (not x['typed_coupling_represented'] or not x['typed_coupling_reference']):errors.append('unrouted-nonindependent-axes-question')
  if x['actual_authority_execution_or_scientific_claim']:errors.append('qualified-declaration-not-actual-authority-execution-or-science')
  assert bool(errors)==expected,(id,errors);rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'universal_independence_or_frame_proof':False})
 def bridge(x,kind='GateBridge'):
  x.update(has_bridge=True,bridge_declared=True,kinds=[kind],direction_named=True,claimed_cross_inference=True,not_silent=True)
 add('two-valid-independent-moves-without-bridge',lambda x:None,False)
 add('no-second-move-validity-inferred',lambda x:x.update(second_move_valid=False),False)
 for kind in b.KINDS:add('explicit-'+kind,lambda x,kind=kind:bridge(x,kind),False)
 def coupled(x):bridge(x);x.update(decision_depends_on_cochange=True,typed_coupling_represented=True,typed_coupling_reference='hyp:separate-coupling')
 add('Gate-with-separate-typed-coupling-reference',coupled,False)
 def symmetric(x):bridge(x);x.update(direction_named=False,symmetry_named=True)
 add('symmetry-named-without-operational-proof',symmetric,False)
 def overlapping(x):bridge(x);x.update(kinds=['GateBridge','SchemaRuleBridge'],symmetry_named=True)
 add('kind-overlap-and-both-direction-modes-allowed',overlapping,False)
 add('outside-governed-scope',lambda x:x.update(applicable=False,source_axis='right',bridge_declared=True),False)
 add('classification-routed',lambda x:x.update(classification_question=True,classification_reference_declared=True,classification_reference='hyp:classification'),False)
 add('lifecycle-routed',lambda x:x.update(lifecycle_question=True,lifecycle_reference_declared=True,lifecycle_reference='hyp:lifecycle'),False)
 for n in ['context','decision','source_axis','target_axis','bridge','direction','evidence','effect']:add('changed-binding-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 add('identical-axis-identities',lambda x:x.update(source_axis='right'),True)
 for n in ['context_matches','decision_matches','axis_move_bindings_match','both_axes_declared_relevant']:add('missing-'+n,lambda x,n=n:x.update({n:False}),True)
 add('bridge-declared-but-presence-denied',lambda x:x.update(bridge_declared=True),True)
 add('undeclared-independent-variation',lambda x:x.update(independent_variation_declared=False),True)
 add('claimed-cochange-without-bridge',lambda x:x.update(claimed_cross_inference=True),True)
 def broken_bridge(x,n,value):bridge(x);x[n]=value
 for n,value in [('bridge_declared',False),('bridge_endpoints_match',False),('bridge_context_decision_match',False),('kinds',[]),('direction_named',False),('direction_reference',''),('effect_reference',''),('evidence_reference',''),('not_silent',False),('first_move_valid',False)]:add('bridge-missing-or-wrong-'+n,lambda x,n=n,value=value:broken_bridge(x,n,value),True)
 def missing_coupling(x):bridge(x);x.update(decision_depends_on_cochange=True)
 add('dependent-Gate-without-typed-coupling-reference',missing_coupling,True)
 add('dependent-decision-without-inference',lambda x:x.update(decision_depends_on_cochange=True,typed_coupling_represented=True,typed_coupling_reference='hyp:coupling'),True)
 for q in ['classification','lifecycle']:add('unrouted-'+q,lambda x,q=q:x.update({q+'_question':True}),True)
 add('unrouted-nonindependent-axes',lambda x:x.update(nonindependent_question=True),True)
 add('actual-authority-execution-or-science-claimed',lambda x:x.update(actual_authority_execution_or_scientific_claim=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];paths={'registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','prototype':b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-root-axis-independence-invariant/v1/artifact.json','Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','source':b.ROOT/source['path'],'checker':b.UNIT/'verify_authority_profile.py'};refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};rows=docs['registry']['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];proto=docs['prototype'];schema=docs['Definition_schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);current_validator=b.c.Draft202012Validator(docs['current_Definition_schema']);checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121)
 ck('no-admitted-direct-Root-Axis-invariant-type',not direct)
 ck('no-current-generic-invariant-carrier',not any(x['semantic_kind']=='invariant' for x in current))
 ck('current-generic-Definition-v2',len(generic)==1 and generic[0]['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('generic-Definition-binds-current-Definition-meaning',generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('historical-generic-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows))
 ck('prototype-remains-prototype-scaffold',proto['status']=='prototype-scaffold')
 ck('prototype-authority-effect-none',proto['authority_effect']=='none')
 ck('prototype-exact-normalized-identity',proto['normalized_contract']['concept_id']==proto['target_id']=='semantic.root-axis-independence-invariant')
 ck('prototype-independent-kind-carrier-owner-axes',proto['normalized_contract']['semantic_kind']=='invariant' and proto['normalized_contract']['carrier_ref']=='type.invariant' and proto['normalized_contract']['owner_scope']=='scope.shared-authority')
 ck('prototype-no-admitted-axis-bridge-schema',proto['four_facets']['schema']['admitted_schema_ref'] is None and proto['four_facets']['schema']['schema_state']=='definition-voice-shape-prototyped')
 observed=load('source-checks.json')['selected_source_sections']
 for label,sr,section in zip(['D29'],proto['source_refs'],observed):
  ck('prototype-'+label+'-selector-and-digest',sr['selector']==section['source_ref']['selector'] and sr['section_sha256']==section['sha256'])
 ck('prototype-D29-reclassify-disposition',[(x['legacy_id'],x['decision']) for x in proto['accepted_source_decisions']]==[('CAV2-D29','reclassify')])
 ck('prototype-normalization-owner-decision-not-bridge-execution',proto['owner_decision_ref']=='CAL-DECISION-0012-NORMALIZE-01-DEFAULTS' and proto['normalization_ref']=='CAL-NORMALIZE-01')
 ck('family-specific-admitted-type-gap-preserved',any('family-specific admitted Artifact Type' in x for x in proto['gaps']))
 ck('selected-Definition-v1-shape-valid',not list(validator.iter_errors(docs['source'])) and docs['source']['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1')
 ck('historical-body-and-C53-overlay-separate',all(x['admission_posture']=='candidate-unadmitted' for x in docs['source']['source_refs']) and load('source-checks.json')['current_registry_entry_lifecycle']=='admitted')
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 probes=[]
 def probe(id,doc,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored Definition-shape probe '+id+' '+str(errors))
  probes.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_bridge_authority_or_cross_axis_execution_verified':False,'scope':'Definition/v1 shape only;no executable axis or bridge carrier'})
 original=docs['source'];probe('selected-exact-Definition-shape',copy.deepcopy(original),True)
 for n in schema['required']:
  d=copy.deepcopy(original);d.pop(n);probe('missing-required-root-'+n,d,False)
 for n in ['governance_pair','axis_move','explicit_bridge','typed_coupling_reference']:
  d=copy.deepcopy(original);d[n]='hyp:claimed';probe('governance-field-not-in-Definition-schema-'+n,d,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  d=copy.deepcopy(original);d[n]='hyp:unresolved';probe('shape-does-not-resolve-'+n,d,True)
 d=copy.deepcopy(original);d['voices']['scientific_formal']['normative_statement']='hyp:axis declaration proves statistical independence and authorizes cross-axis execution';probe('shape-valid-overclaimed-normative-text',d,True)
 errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in current_validator.iter_errors(original)]
 inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']];report={'schema_version':'definition-assurance-RootAxis-profile/v1-candidate','status':'PASS-for-qualified-axis-bridge-hypotheses-and-actual-catalog-prototype-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_axis_bridge_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'prototype_status':proto['status'],'prototype_authority_effect':proto['authority_effect'],'admitted_axis_bridge_execution_schema_ref':None,'schema_probe_surface':'selected Definition/v1 shape;generic Definition/v2 is not an executable axis or bridge adapter','schema_probes':probes,'historical_source_current_definition_shape':{'errors':errors,'exact_source_admission_invalidated':False,'semantic_epoch_mismatch_claimed':False},'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'native_or_live_consumer_executed':False,'actual_bridge_authority_or_cross_axis_execution_created':False,'generic_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified authored axis/bridge hypotheses plus actual registry,prototype,D29 source-reference and Definition-shape observations. Generic Definition/v2 binds current Definition@1 meaning. No direct admitted invariant/type.invariant axis or bridge schema,actual bridge write,authority,statistical independence,scientific theorem or cross-axis execution,owner acceptance or consumer proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({'status':r['status'],'profiles':len(r['profiles']),'rejected_profiles':sum(x['expected_rejection'] for x in r['profiles']),'frames':len(r['finite_axis_bridge_frames']),'rejected_frames':sum(x['expected_rejection'] for x in r['finite_axis_bridge_frames']),'catalog_checks':r['actual_check_count'],'Definition_schema_probes':len(r['schema_probes']),'schema_acceptances':sum(x['schema_accepted'] for x in r['schema_probes']),'direct_current_definition_binding_types':r['direct_current_definition_binding_types']},indent=2))
if __name__=='__main__':main()

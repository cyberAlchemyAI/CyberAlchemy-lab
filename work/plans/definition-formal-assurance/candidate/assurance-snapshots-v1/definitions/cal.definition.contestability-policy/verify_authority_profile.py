"""Hypothetical review/retention contexts and bounded current generic carrier observations."""
import copy,json,types
import build_candidate as b
import verifier as v
AXES=['policy','version','scope','subject_revision','owner_route','response_mode','resolution_gate','residue_route','challenge_context']
SUPPORT=['identity_source','field_map','object_revision','owner_authorization','gate','challenge_modes','confidence_split','residue_trace']
HYPOTHETICAL_MODES=['question','contradiction','validation','owner-review']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def raw_profile():
 context={n:'hyp:'+n for n in AXES};context['response_mode']='question'
 return {'qualified':False,'context':context,'query':copy.deepcopy(context),'support':{n:None for n in SUPPORT},'unresolved':True,'owner_resolution':None,'owner_authorized':False,'gate_passed':False,'contains_own_confidence':False,'contains_own_residue':False,'third_confidence_axis':False,'link_present':False,'link_value':None,'actual_review_verified':False,'actual_residue_handled_verified':False,'actual_authority_or_runtime_verified':False}
def assess(p):
 errors=[]
 if any(p[n] for n in ['actual_review_verified','actual_residue_handled_verified','actual_authority_or_runtime_verified']):errors.append('actual-world-claim-not-supported-by-hypotheses')
 if any(p[n] for n in ['contains_own_confidence','contains_own_residue','third_confidence_axis']):errors.append('contract-content-or-confidence-axis-collapse')
 if p['context']['response_mode'] not in HYPOTHETICAL_MODES:errors.append('outside-selected-illustrative-mode-hypotheses')
 if p['link_present'] and not p['link_value']:errors.append('present-link-value-missing')
 if p['qualified']:
  for n in SUPPORT:
   if not p['support'][n]:errors.append('missing-support:'+n)
 if p['owner_resolution'] is not None and (p['owner_resolution'] not in ['close','waive','demote'] or not p['qualified'] or not p['owner_authorized'] or not p['gate_passed'] or p['context']!=p['query']):errors.append('unqualified-owner-resolution')
 qualified=p['qualified'] and all(p['support'].values()) and p['context']==p['query'] and not errors
 resolved=qualified and p['owner_resolution'] in ['close','waive','demote'] and p['owner_authorized'] and p['gate_passed']
 return errors,{'review_under_hypotheses':bool(qualified),'retention_required_under_hypotheses':bool(p['unresolved'] and not resolved),'actual_review_or_resolution_verified':False,'source_fidelity_accepted':False}
def profiles():
 rows=[]
 def add(id,change,reject=False,review=False,retain=True):
  p=raw_profile();change(p);errors,observations=assess(p)
  if bool(errors)!=reject or observations['review_under_hypotheses']!=review or observations['retention_required_under_hypotheses']!=retain:raise ValueError('Wrong authored profile '+id)
  rows.append({'case_id':id,'profile':p,'errors':errors,'observations':observations,'expected_rejection':reject,'expected_review':review,'expected_retention_required':retain,'actual_runtime_execution':False})
 def qualify(p):p.update(qualified=True,owner_authorized=True,gate_passed=True,support={n:'hyp:support:'+n for n in SUPPORT})
 add('raw-field-completeness-not-qualified-review',lambda p:None)
 add('qualified-context-review-still-retains-unresolved-residue',qualify,review=True)
 for n in SUPPORT:
  def missing(p,n=n):qualify(p);p['support'][n]=None
  add('missing-'+n,missing,reject=True)
 for n in AXES:
  def mismatch(p,n=n):qualify(p);p['query'][n]='hyp:other'
  add('context-mismatch-'+n,mismatch)
 for mode in HYPOTHETICAL_MODES:
  def selected(p,mode=mode):qualify(p);p['context']['response_mode']=p['query']['response_mode']=mode
  add('illustrative-mode-'+mode,selected,review=True)
 for outcome in ['close','waive','demote']:
  def resolve(p,outcome=outcome):qualify(p);p['owner_resolution']=outcome
  add('qualified-owner-'+outcome,resolve,review=True,retain=False)
  add('raw-owner-'+outcome,lambda p,outcome=outcome:p.update(owner_resolution=outcome),reject=True)
 add('unknown-resolution',lambda p:p.update(owner_resolution='auto-promote'),reject=True)
 add('present-link-without-value',lambda p:p.update(link_present=True),reject=True)
 add('present-link-with-unresolved-reference-is-only-a-hypothesis',lambda p:p.update(link_present=True,link_value='hyp:unresolved'))
 for n in ['contains_own_confidence','contains_own_residue','third_confidence_axis','actual_review_verified','actual_residue_handled_verified','actual_authority_or_runtime_verified']:add('forbidden-'+n,lambda p,n=n:p.update(**{n:True}),reject=True)
 add('unselected-mode-not-a-source-enumeration-claim',lambda p:p['context'].update(response_mode='other'),reject=True)
 return rows
def frames():
 rows=[]
 def add(id,operation,change=lambda f:None,reject=False):
  f={'operation':operation,'policy_before':'hyp:p@v1','policy_after':'hyp:p@v1','scope_before':'hyp:scope','scope_after':'hyp:scope','subject_before':'hyp:s@v1','subject_after':'hyp:s@v1','evidence_confidence_before':'hyp:ec','evidence_confidence_after':'hyp:ec','commitment_confidence_before':'hyp:cc','commitment_confidence_after':'hyp:cc','object_residue_before':'hyp:or','object_residue_after':'hyp:or','unresolved':True,'challenge_residue_retained':True,'qualified_owner_resolution':False,'original_history_retained':True,'actual_transition_verified':False};change(f);errors=[]
  for n in ['policy','scope','subject','evidence_confidence','commitment_confidence','object_residue']:
   if f[n+'_before']!=f[n+'_after']:errors.append('unqualified-frame-change:'+n)
  resolution=operation in ['close','waive','demote'] and f['qualified_owner_resolution']
  if operation in ['close','waive','demote'] and not resolution:errors.append('owner-resolution-not-qualified')
  if f['unresolved'] and not resolution and not f['challenge_residue_retained']:errors.append('unresolved-residue-dropped')
  if not f['original_history_retained'] or f['actual_transition_verified']:errors.append('history-or-actual-claim')
  if bool(errors)!=reject:raise ValueError('Wrong authored frame '+id)
  rows.append({'case_id':id,'frame':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'universal_temporal_proof':False})
 for op in ['file','question','contradict','validate']:add(op+'-preserves-sibling-state',op)
 for n in ['policy','scope','subject','evidence_confidence','commitment_confidence','object_residue']:add('silent-change-'+n,'file',lambda f,n=n:f.update(**{n+'_after':'hyp:other'}),True)
 add('drop-unresolved-residue','file',lambda f:f.update(challenge_residue_retained=False),True)
 add('erase-original-history','file',lambda f:f.update(original_history_retained=False),True)
 for op in ['close','waive','demote']:
  add('qualified-'+op,op,lambda f:f.update(qualified_owner_resolution=True,challenge_residue_retained=False))
  add('unqualified-'+op,op,reject=True)
 add('actual-runtime-claim','file',lambda f:f.update(actual_transition_verified=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings()
 registry_path=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(registry_path.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];source=load('t.json')['payload']['source'];direct=[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']];selected={};paths={'registry':registry_path};checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('no-current-exact-ContestabilityPolicy-carrier-binding-in-selected-registry',direct==[])
 for n in ['policy','challenge-contract','challenge-event','ontology-node','definition']:
  rows=[x for x in current if x['semantic_kind']==n]
  if len(rows)!=1:raise ValueError('Ambiguous related carrier '+n)
  row=rows[0];selected[n]=row;folder=(b.ROOT/row['artifact_path']).parent;descriptor=json.loads((folder/'artifact.json').read_bytes());paths[n+'_descriptor']=folder/'artifact.json';paths[n+'_schema']=b.ROOT/row['schema_path'];paths[n+'_fixture']=folder/descriptor['validation_contract']['positive_witness']
  if n=='policy':
   paths['policy_generator']=b.ROOT/descriptor['source_direction']['shared_generator_path'];paths['policy_validator']=b.ROOT/descriptor['validation_contract']['shared_validator_path'];paths['policy_artifact_projection']=folder/'ARTIFACT.md';paths['policy_fixture_projection']=folder/descriptor['validation_contract']['positive_projection'];paths['root_descriptor']=b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json'
   for rel in descriptor['validation_contract']['negative_witnesses']:paths['policy_negative_'+b.Path(rel).stem]=folder/rel
 refs={n:b.ref(q) for n,q in paths.items()};raws={n:q.read_bytes() for n,q in paths.items()};docs={n:json.loads(raws[n]) for n,q in paths.items() if q.suffix=='.json'};observations=[];probes=[];life=[];hostiles=[]
 for n,row in selected.items():
  schema=docs[n+'_schema'];fixture=docs[n+'_fixture'];validator=b.c.Draft202012Validator(schema);b.c.Draft202012Validator.check_schema(schema);ck(n+'-exact-descriptor-schema',refs[n+'_descriptor']['sha256']==row['artifact_sha256'] and refs[n+'_schema']['sha256']==row['schema_sha256']);ck(n+'-positive-fixture-shape',not list(validator.iter_errors(fixture)));observations.append({'semantic_kind':n,'artifact_type_ref':row['artifact_type_ref'],'fixture_shape_valid':True,'whole_ContestabilityPolicy_alignment_verified':False,'declared_validator_executed':False})
  x=copy.deepcopy(fixture);x.update(owner_ref='absent:owner',scope_ref='absent:scope');errors=list(validator.iter_errors(x));probes.append({'semantic_kind':n,'case_id':'unresolved-owner-scope','record':x,'schema_accepted':not errors,'errors':[e.message for e in errors],'reference_resolution_or_review_verified':False})
  for state in ['candidate','active','historical','retired']:
   x=copy.deepcopy(fixture);x['lifecycle_state']=state;errors=list(validator.iter_errors(x));life.append({'semantic_kind':n,'lifecycle_state':state,'schema_accepted':not errors,'actual_lifecycle_or_runtime_verified':False})
 policy=docs['policy_descriptor'];ps=docs['policy_schema'];fixture=docs['policy_fixture'];validator=b.c.Draft202012Validator(ps);binding=policy['semantic_definition_bindings'];ck('generic-policy-is-bound-to-independent-Policy-definition',len(binding)==1 and binding[0]['definition_ref']==b.source_ref(snap,'cal.definition.policy')['version_ref'] and binding[0]['sha256']==b.source_ref(snap,'cal.definition.policy')['sha256'])
 for n in paths:
  if n.startswith('policy_negative_'):
   errors=list(validator.iter_errors(docs[n]));hostiles.append({'path':refs[n]['path'],'schema_rejected':bool(errors),'errors':[e.message for e in errors]})
 ck('five-policy-hostiles-reject',len(hostiles)==5 and all(x['schema_rejected'] for x in hostiles))
 module=types.ModuleType('_pure_policy_generator');exec(compile(raws['policy_generator'],str(paths['policy_generator']),'exec'),module.__dict__);before=copy.deepcopy([policy,fixture]);ck('pure-policy-generator-validator-root-digests',policy['source_direction']['shared_generator_sha256']==refs['policy_generator']['sha256'] and policy['validation_contract']['shared_validator_sha256']==refs['policy_validator']['sha256'] and policy['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('two-exact-policy-artifact-renders',module.render_artifact(policy).encode()==module.render_artifact(policy).encode()==raws['policy_artifact_projection']);ck('two-exact-policy-fixture-renders',module.render_instance(policy,fixture).encode()==module.render_instance(policy,fixture).encode()==raws['policy_fixture_projection']);ck('render-inputs-preserved',before==[policy,fixture])
 special=[]
 for field in b.FIELDS:
  x=copy.deepcopy(fixture);x['payload'][field]='hyp:field';errors=list(validator.iter_errors(x));special.append({'case_id':'extra-source-review-field-'+field,'record':x,'schema_accepted':not errors,'errors':[e.message for e in errors],'source_field_mapping_or_review_verified':False})
 for id,change in [('unresolved-issuer',lambda x:x['payload'].update(issuer_ref='absent:issuer')),('unresolved-rules',lambda x:x['payload'].update(rule_refs=['absent:rule'])),('unresolved-exception-route',lambda x:x['payload'].update(exception_route='absent:route')),('no-review-tuple-or-confidence-frame-required',lambda x:None)]:
  x=copy.deepcopy(fixture);change(x);errors=list(validator.iter_errors(x));special.append({'case_id':id,'record':x,'schema_accepted':not errors,'errors':[e.message for e in errors],'source_field_mapping_or_review_verified':False})
 ck('eight-extra-review-fields-reject-four-unresolved-shapes-accept',len(special)==12 and sum(x['schema_accepted'] for x in special)==4)
 current_definition=b.c.Draft202012Validator(docs['definition_schema']);source_doc=json.loads((b.ROOT/source['path']).read_bytes());errors=list(current_definition.iter_errors(source_doc));shape={'source_schema_version':source_doc['schema_version'],'selected_current_definition_type':selected['definition']['artifact_type_ref'],'current_schema_accepted':not errors,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in errors],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-Definition-v1-current-v2-four-binding-errors',bool(errors) and {x['path'] for x in shape['errors']}=={'/schema_version','/classification/artifact_type_ref','/schema_ref','/source_direction/generator_ref'})
 comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs']);ck('independent-ChallengeContract-identity-not-imported-alias',any(x['definition_id']=='cal.definition.challenge-contract' and x['version_ref']!=source['version_ref'] for x in comparison['separate_qualified_sources']) and comparison['comparison_assembled_into_primary_T'] is False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles_result=profiles();frames_result=frames();bindings=[b.ref(q) for q in [b.UNIT/'verify_authority_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=load('../cal.definition.constitution/delivery-manifest.json');b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-ContestabilityPolicy-profile/v1-candidate','status':'PASS-for-explicit-review-retention-hypotheses-and-selected-generic-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json','legacy-source-section.md','legacy-confidence-context.md']],'selected_inputs':refs,'profile_control_count':len(profiles_result),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles_result),'profiles':profiles_result,'finite_history_frame_count':len(frames_result),'rejected_history_frames':sum(x['expected_rejection'] for x in frames_result),'finite_history_frames':frames_result,'actual_check_count':len(checks),'actual_checks':checks,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'dedicated_current_carrier_selection':{'direct_definition_binding_types':direct,'dedicated_current_carrier_established':False},'generic_Policy_selection':{'artifact_type_ref':selected['policy']['artifact_type_ref'],'exact_definition_bindings':binding,'required_payload_fields':ps['properties']['payload']['required'],'possible_owner_route_locator':'/owner_ref','accepted_ContestabilityPolicy_tuple_or_type_policy_mapping':False},'related_carrier_observations':observations,'negative_fixture_checks':hostiles,'related_schema_probes':probes,'lifecycle_shape_probes':life,'generic_Policy_source_field_probes':special,'historical_source_current_definition_shape':shape,'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'illustrative_challenge_modes':HYPOTHETICAL_MODES,'mode_enumeration_is_source_owner_accepted':False,'actual_review_confidence_change_residue_handling_or_authority_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Explicit hypothetical review/retention profiles and finite sibling-state frames; exact generic Policy/current carrier shapes and independent identity bindings. No dedicated exact current carrier,accepted Policy/ChallengeContract alias/field/owner/confidence/residue map,actual review/closure or universal trace proof.'}
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({k:x[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

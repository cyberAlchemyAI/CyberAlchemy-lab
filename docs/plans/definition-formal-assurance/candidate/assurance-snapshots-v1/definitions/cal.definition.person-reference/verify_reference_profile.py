"""Finite full-subset minimization/use/history profiles and actual reference carrier observations."""
import copy,itertools,json,types
import build_candidate as b
import verifier as v
FIELDS=['identifier','identity_scope','functional_label','private_attribute']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def subsets(fields):return [set(xs) for size in range(len(fields)+1) for xs in itertools.combinations(fields,size)]
def baseline():
 rec=json.loads((b.ROOT/'authority/artifact-types/person-reference/v1/fixtures/valid/record.json').read_bytes())
 return {'record':rec,'hypothetical_Person':'Person:hyp1','field_universe':FIELDS,'exposed_fields':['identifier','identity_scope'],'purpose_policy':{'purpose':rec['purpose'],'identity_scope':rec['identity_scope'],'sufficient_bases':[['identifier','identity_scope']],'forbidden_fields':['private_attribute'],'review_marker':'hypothetical-purpose-review:1'},'requested_use':rec['permitted_uses'][0],'reference_only_conclusions':[],'independently_supported_outcomes':[]}
def errors(p):
 es=[];r=p['record'];policy=p['purpose_policy'];universe=set(p['field_universe']);selected=set(p['exposed_fields']);bases=[set(x) for x in policy['sufficient_bases']]
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected candidate reference profile')
 ck(r['authority_effect']=='none' and r['status']=='candidate-unadmitted','candidate reference non-effect retained')
 ck(bool(p['hypothetical_Person']) and p['hypothetical_Person']!=r['node_id'],'selected hypothetical referent never reference itself')
 ck(policy['purpose']==r['purpose'] and policy['identity_scope']==r['identity_scope'] and bool(policy['review_marker']),'purpose/scope-specific symbolic sufficiency policy exact')
 ck(len(universe)==len(p['field_universe']) and universe<=set(FIELDS),'selected finite field universe exact and distinct')
 ck(len(selected)==len(p['exposed_fields']) and selected<=universe,'selected exposed fields declared and distinct')
 ck(bool(bases) and all(x<=universe for x in bases),'sufficiency bases explicitly enumerated within candidate universe')
 sufficient=lambda selection:any(basis<=selection for basis in bases)
 ck(sufficient(selected),'selected field set sufficient for declared purpose')
 ck(not any(sufficient(s) for s in subsets(sorted(universe)) if s<selected),'no sufficient proper subset; explicit full powerset checked')
 ck(not selected.intersection(policy['forbidden_fields']),'selected purpose policy forbids exposed private attributes')
 ck(p['requested_use'] in r['permitted_uses'] and p['requested_use'] not in r['prohibited_uses'],'selected use permitted and not prohibited under candidate declarations')
 ck(not set(r['permitted_uses']).intersection(r['prohibited_uses']),'selected permitted/prohibited declarations not contradictory')
 ck(r['lifecycle_state']=='active','candidate use requires active reference')
 ck(r['node_id'] not in r['successor_refs'],'candidate reference cannot be its own successor')
 ck(not p['reference_only_conclusions'],'reference alone establishes no selected world conclusion')
 ck(set(p['independently_supported_outcomes'])<=set(b.OUTCOMES),'independent outcomes within selected profile vocabulary')
 ck(bool(r['minimization_basis']) and bool(r['owner_route']) and bool(r['challenge_route']),'minimization/owner/challenge metadata recorded')
 all_sets=subsets(sorted(universe));minimum=[s for s in all_sets if sufficient(s) and not any(sufficient(t) for t in all_sets if t<s)]
 details={'enumerated_selections':len(all_sets),'inclusion_minima':[sorted(x) for x in minimum],'selected_inclusion_minimum':sufficient(selected) and not any(sufficient(t) for t in all_sets if t<selected),'selected_global_cardinality_minimum':sufficient(selected) and all(len(selected)<=len(t) for t in all_sets if sufficient(t))}
 return es,details
def controls():
 rows=[]
 def add(id,change,bad=False):
  p=baseline();change(p);es,details=errors(p)
  if bool(es)!=bad:raise ValueError('Unexpected candidate reference profile '+id+' '+str(es))
  rows.append({'case_id':id,'profile':p,'errors':es,'minimum_check':details,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_reference_denotation_established':False,'actual_runtime_execution':False})
 add('two-required-purpose-fields-explicit-full-subset-check',lambda p:None)
 add('independent-world-facts-allowed',lambda p:p.update(independently_supported_outcomes=b.OUTCOMES))
 def single(p):p['purpose_policy']['sufficient_bases']=[['identifier']];p['exposed_fields']=['identifier']
 add('different-purpose-policy-can-need-one-field',single)
 add('inclusion-minimum-need-not-be-global-cardinality-minimum',lambda p:p['purpose_policy'].update(sufficient_bases=[['identifier','identity_scope'],['functional_label']]))
 add('redundant-functional-label-rejected',lambda p:p['exposed_fields'].append('functional_label'),True)
 add('private-field-exposure-rejected',lambda p:p['exposed_fields'].append('private_attribute'),True)
 add('insufficient-one-field',lambda p:p.update(exposed_fields=['identifier']),True)
 add('empty-selection-insufficient-for-selected-policy',lambda p:p.update(exposed_fields=[]),True)
 add('missing-sufficiency-policy',lambda p:p['purpose_policy'].update(sufficient_bases=[]),True)
 add('omitted-required-field-from-universe',lambda p:p.update(field_universe=['identifier','functional_label','private_attribute']),True)
 add('unknown-sufficiency-field',lambda p:p['purpose_policy']['sufficient_bases'][0].append('unknown'),True)
 add('unknown-exposed-field',lambda p:p['exposed_fields'].append('unknown'),True)
 add('duplicate-exposed-field',lambda p:p['exposed_fields'].append('identifier'),True)
 add('purpose-mismatch',lambda p:p['purpose_policy'].update(purpose='other-purpose'),True)
 add('scope-mismatch',lambda p:p['purpose_policy'].update(identity_scope='other-scope'),True)
 add('missing-separate-policy-review-marker',lambda p:p['purpose_policy'].update(review_marker=''),True)
 add('reference-collapsed-with-selected-Person',lambda p:p.update(hypothetical_Person=p['record']['node_id']),True)
 add('undeclared-use',lambda p:p.update(requested_use='undeclared-use'),True)
 add('prohibited-use',lambda p:p.update(requested_use=p['record']['prohibited_uses'][0]),True)
 add('permitted-and-prohibited-overlap',lambda p:p['record']['prohibited_uses'].append(p['record']['permitted_uses'][0]),True)
 add('retired-reference-not-active-use',lambda p:p['record'].update(lifecycle_state='retired'),True)
 add('superseded-reference-not-active-use',lambda p:p['record'].update(lifecycle_state='superseded'),True)
 add('self-successor-not-selected-policy',lambda p:p['record']['successor_refs'].append(p['record']['node_id']),True)
 add('empty-minimization-basis',lambda p:p['record'].update(minimization_basis=''),True)
 add('empty-challenge-route',lambda p:p['record'].update(challenge_route=''),True)
 for n in b.OUTCOMES:add('reference-alone-cannot-establish-'+n,lambda p,n=n:p.update(reference_only_conclusions=[n]),True)
 add('world-authority-effect-forbidden',lambda p:p['record'].update(authority_effect='grant'),True)
 add('runtime-field-not-in-selected-profile',lambda p:p.update(runtime=True),True)
 return rows
def frames():
 rows=[]
 def frame():return {'operation':'update-label','before':{'node_id':'reference:hyp1','reference_value':'opaque:hyp1','purpose':'attribution','identity_scope':'lab','local_label':'reviewer','lifecycle_state':'active','successor_refs':[]},'after':{'node_id':'reference:hyp1','reference_value':'opaque:hyp1','purpose':'attribution','identity_scope':'lab','local_label':'new-functional-label','lifecycle_state':'active','successor_refs':[]},'before_Person_hypothesis':'Person:hyp1','after_Person_hypothesis':'Person:hyp1','successor':None,'old_record_retained':True,'before_authority':['permission:hyp-independent'],'after_authority':['permission:hyp-independent'],'separate_authority_decision_ref':None}
 def check(f):
  es=[];before=f['before'];after=f['after']
  if f['operation'] not in ['update-label','retire','supersede']:es.append('operation not in candidate policy')
  for key in ['node_id','reference_value','purpose','identity_scope']:
   if before[key]!=after[key]:es.append('same selected reference preserves '+key)
  if f['before_Person_hypothesis']!=f['after_Person_hypothesis']:es.append('no silently retargeted Person hypothesis')
  if not f['old_record_retained']:es.append('candidate history retains prior record')
  if f['operation']=='update-label' and before['lifecycle_state']!=after['lifecycle_state']:es.append('label edit does not change lifecycle')
  if f['operation']=='retire' and after['lifecycle_state']!='retired':es.append('retirement state exact')
  if f['operation']=='supersede':
   s=f['successor']
   if after['lifecycle_state']!='superseded' or s is None or s['node_id']==before['node_id'] or s['node_id'] not in after['successor_refs'] or s['identity_scope']!=before['identity_scope']:es.append('candidate fresh scoped successor explicit')
  if f['before_authority']!=f['after_authority'] and f['separate_authority_decision_ref'] is None:es.append('reference lifecycle alone does not grant/revoke independent authority')
  return es
 def add(id,change,bad=False):
  f=frame();change(f);es=check(f)
  if bool(es)!=bad:raise ValueError('Unexpected selected reference history '+id+' '+str(es))
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('functional-label-edit-preserves-reference-and-Person-hypothesis',lambda f:None)
 add('retirement-preserves-identity-and-independent-authority',lambda f:f['after'].update(lifecycle_state='retired') or f.update(operation='retire'))
 def successor(f):f.update(operation='supersede',successor={'node_id':'reference:hyp2','identity_scope':'lab'});f['after'].update(lifecycle_state='superseded',successor_refs=['reference:hyp2'])
 add('explicit-fresh-scoped-successor-old-history-retained',successor)
 add('separate-authority-decision-can-coexist',lambda f:f.update(after_authority=[],separate_authority_decision_ref='hypothetical-independent-decision:1'))
 for key in ['node_id','reference_value','purpose','identity_scope']:add('label-edit-changes-'+key,lambda f,key=key:f['after'].__setitem__(key,'other'),True)
 add('label-edit-retargets-Person',lambda f:f.update(after_Person_hypothesis='other'),True)
 add('old-history-dropped',lambda f:f.update(old_record_retained=False),True)
 add('label-edit-changes-lifecycle',lambda f:f['after'].update(lifecycle_state='retired'),True)
 add('superseded-without-successor',lambda f:f.update(operation='supersede') or f['after'].update(lifecycle_state='superseded'),True)
 add('reference-lifecycle-revokes-permission',lambda f:f.update(after_authority=[]),True)
 add('reference-lifecycle-grants-permission',lambda f:f.update(after_authority=['permission:new']),True)
 add('unselected-operation',lambda f:f.update(operation='authenticate-Person'),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();root=b.ROOT/'authority/artifact-types/person-reference/v1'
 paths={'descriptor':root/'artifact.json','schema':root/'schema.json','fixture':root/'fixtures/valid/record.json','artifact_projection':root/'ARTIFACT.md','fixture_projection':root/'fixtures/valid/RECORD.md','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','generator':b.ROOT/'tooling/generators/artifact_surface.py','shared_validator':b.ROOT/'tooling/validators/artifact_surface.py','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json','refinement':b.ROOT/'authority/artifact-types/candidates/0004-remaining-26-materialization/refinements/type.person-reference.json'}
 for p in sorted((root/'fixtures/invalid').glob('*.json')):paths['negative_'+p.stem]=p
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());tr=next(x for x in reg['admitted_contracts'] if x['semantic_kind']=='typed-relation' and x['lifecycle_state']=='admitted-current');kind=next(x for x in kr['entries'] if x['relation_kind_ref']=='relation.asserts-identity-of');paths['Kind']=b.ROOT/kind['instance_path'];paths['TR_schema']=b.ROOT/tr['schema_path'];paths['TR_fixture']=(b.ROOT/tr['artifact_path']).parent/'fixtures/valid/record.json'
 for semantic in ['identity-claim','person']:
  row=next(x for x in reg['admitted_contracts'] if x['semantic_kind']==semantic and x['lifecycle_state']=='admitted-current');paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=(b.ROOT/row['artifact_path']).parent/'fixtures/valid/record.json'
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};artifact=docs['descriptor'];fixture=docs['fixture'];schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 entry=next(x for x in reg['admitted_contracts'] if x['artifact_type_ref']==artifact['artifact_type_ref']);source=load('t.json')['payload']['source'];binding=artifact['semantic_definition_bindings'][0]
 ck('exact-current-Type-overlay-0070',entry['lifecycle_state']=='admitted-current' and entry['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and entry['artifact_sha256']==refs['descriptor']['sha256'] and entry['schema_sha256']==refs['schema']['sha256'])
 ck('historical-candidate-descriptor-fixture-wording-retained',artifact['status']==fixture['status']=='candidate-unadmitted' and artifact['authority_effect']==fixture['authority_effect']=='none')
 ck('exact-admitted-Definition-0053-binding',binding['definition_ref']==source['version_ref'] and binding['path']==source['path'] and binding['sha256']==source['sha256'] and binding['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION')
 ck('root-descriptor-and-closed-schema-bound',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'] and artifact['schema_digest']==refs['schema']['sha256'] and schema['additionalProperties'] is False)
 ck('shared-renderer-validator-digests',artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['shared_validator']['sha256'])
 ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 negative=[{'path':refs[n]['path'],'schema_rejected':bool(list(validator.iter_errors(docs[n])))} for n in sorted(refs) if n.startswith('negative_')];ck('four-hostiles-rejected',len(negative)==4 and all(x['schema_rejected'] for x in negative))
 mod=types.ModuleType('_bound_artifact_surface_renderer');mod.__file__=str(paths['generator']);exec(compile(raws['generator'],str(paths['generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture]);renderA=mod.render_artifact(artifact).encode();renderB=mod.render_instance(artifact,fixture).encode()
 ck('two-artifact-renders-exact-projection',renderA==mod.render_artifact(artifact).encode()==raws['artifact_projection']);ck('two-fixture-renders-exact-projection',renderB==mod.render_instance(artifact,fixture).encode()==raws['fixture_projection']);ck('renderers-preserve-inputs',before==[artifact,fixture])
 ck('refinement-explicit-minimization-policy-not-admission',docs['refinement']['target_id']=='type.person-reference' and docs['refinement']['admission_effect']=='none' and docs['refinement']['review_state']=='revision-authorized-before-admission')
 for semantic in ['identity-claim','person']:ck(semantic+'-selected-fixture-shape-valid',not list(b.c.Draft202012Validator(docs[semantic+'_schema']).iter_errors(docs[semantic+'_fixture'])))
 joins={'Claim_literal_reference_matches_selected_node':docs['identity-claim_fixture']['person_reference_ref']==fixture['node_id'],'Claim_identifier_matches_reference_value':docs['identity-claim_fixture']['asserted_identifier']==fixture['reference_value'],'direct_Person_field_present':'person_ref' in fixture,'selected_Person_relation_points_to_this_reference':any(x['counterpart_ref']==fixture['node_id'] for x in docs['person_fixture']['relation_refs']),'actual_Person_mapping_verified':False,'purpose_sufficiency_minimization_policy_reviewed':False}
 ck('actual-literal-join-is-not-Person-denotation',joins=={'Claim_literal_reference_matches_selected_node':True,'Claim_identifier_matches_reference_value':False,'direct_Person_field_present':False,'selected_Person_relation_points_to_this_reference':False,'actual_Person_mapping_verified':False,'purpose_sufficiency_minimization_policy_reviewed':False})
 probes=[]
 def probe(id,change,expected):
  rec=copy.deepcopy(fixture);change(rec);es=list(validator.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected actual Reference schema probe '+id+' '+str([x.message for x in es]))
  probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_reference_denotation_established':False,'actual_privacy_or_minimization_enforced':False,'actual_runtime_execution':False,'whole_source_conformance_established':False})
 probe('opaque-type-with-synthetic-identifiable-value-accepted',lambda r:r.update(reference_value='synthetic-identifiable-value'),True)
 probe('unsupported-minimization-sentence-accepted',lambda r:r.update(minimization_basis='Arbitrary unreviewed assertion of minimum'),True)
 probe('different-identity-scope-string-accepted',lambda r:r.update(identity_scope='other-scope'),True)
 probe('permitted-prohibited-overlap-accepted',lambda r:r['prohibited_uses'].append(r['permitted_uses'][0]),True)
 probe('self-successor-shape-accepted',lambda r:r['successor_refs'].append(r['node_id']),True)
 probe('superseded-without-successor-shape-accepted',lambda r:r.update(lifecycle_state='superseded'),True)
 probe('retired-with-permitted-use-labels-retained',lambda r:r.update(lifecycle_state='retired'),True)
 probe('nonexistent-successor-token-accepted',lambda r:r['successor_refs'].append('absent:successor'),True)
 probe('extra-private-attribute-field-rejected',lambda r:r.update(private_attribute='synthetic-private-attribute'),False)
 probe('extra-direct-Person-field-rejected',lambda r:r.update(person_ref='Person:hyp1'),False)
 probe('empty-permitted-uses-rejected',lambda r:r.update(permitted_uses=[]),False)
 probe('duplicate-successor-refs-rejected',lambda r:r.update(successor_refs=['same','same']),False)
 probe('authority-effect-rejected',lambda r:r.update(authority_effect='grant'),False)
 kp=docs['Kind']['payload'];ck('current-Kind-four-pairs-and-two-qualifiers-bound',kind['lifecycle_state']=='admitted-current' and kind['instance_sha256']==refs['Kind']['sha256'] and kind['exact_endpoint_pair_count']==len(kp['allowed_endpoint_pairs'])==4 and kind['required_qualifier_axes']==kp['qualifier_contract']['required_axes']==['assertion_kind','claim_scope']);ck('Kind-excludes-merge-authority-private-inference',kp['forbidden_inferences']==['identity-merge','authority-transfer','private-attribute-inference']);ck('current-TR-v3-schema-bound',tr['artifact_type_ref']=='cal.artifact-type.typed-relation/v3' and tr['schema_sha256']==refs['TR_schema']['sha256'])
 relation=copy.deepcopy(docs['TR_fixture']);relation['payload'].update(relation_kind_ref='relation.asserts-identity-of',source={'kind':'person-reference','ref':fixture['node_id'],'version_ref':fixture['node_id']+'@example-revision'},target={'kind':'person','ref':docs['person_fixture']['node_id'],'version_ref':docs['person_fixture']['node_id']+'@example-revision'},qualifiers={'assertion_kind':'person-reference','claim_scope':fixture['identity_scope']});trvalidator=b.c.Draft202012Validator(docs['TR_schema']);relation_probes=[]
 def rp(id,change,expected):
  rec=copy.deepcopy(relation);change(rec);es=list(trvalidator.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected relation shape probe '+id)
  relation_probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_reference_denotation_established':False,'actual_relation_created':False,'whole_source_conformance_established':False})
 rp('Reference-to-Person-shape-valid',lambda r:None,True)
 rp('Reference-to-same-Reference-shape-valid-no-identity-merge',lambda r:r['payload'].update(target=copy.deepcopy(r['payload']['source'])),True)
 rp('different-scope-string-shape-accepted',lambda r:r['payload']['qualifiers'].update(claim_scope='other'),True)
 rp('unresolved-target-string-shape-accepted',lambda r:r['payload']['target'].update(ref='absent:Person'),True)
 rp('Reference-to-Claim-not-admitted-pair',lambda r:r['payload']['target'].update(kind='identity-claim'),False)
 rp('missing-required-scope-rejected',lambda r:r['payload']['qualifiers'].pop('claim_scope'),False)
 rp('extra-private-inference-qualifier-rejected',lambda r:r['payload']['qualifiers'].update(private_attributes=True),False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();history=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_reference_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=json.loads((b.BASE/'definitions/cal.definition.identity-claim/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-person-reference-profile/v1-candidate','status':'PASS-for-bounded-purpose-minimization-use-history-and-current-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_history_frame_count':len(history),'rejected_history_frames':sum(x['expected_rejection'] for x in history),'finite_history_frames':history,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'actual_relation_schema_probes':relation_probes,'negative_fixture_checks':negative,'actual_join_observations':joins,'actual_relation_endpoint_pairs':kp['allowed_endpoint_pairs'],'source_mapping_gaps':{'mapping_reviewed':False,'Claim_fixture_literal_reference_join_established':True,'identifier_to_Person_denotation_established':False,'purpose_fields_sufficiency_minimization_and_privacy_enforcement_reviewed':False,'selected_use_and_successor_history_policy_reviewed':False,'source_precedence_and_inherited_Person_semantics_reviewed':False,'whole_source_conformance_established':False},'new_Person_data_references_or_relations_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Bounded full-subset inclusion-minimum/use/exposure and history profiles, plus exact current schemas/fixtures/projections. Symbolic purpose/sufficiency/review markers do not establish actual data minimization, privacy, reference/Person identity mapping or authorization. Inclusion minimal is not necessarily minimum cardinality/cost/bytes. No real reference, operational/history proof, actual relation/admission/world effect or whole-definition acceptance.'}
 if write:b.put('reference-profile-checks.json',report)
 elif not b.r.same_json(report,load('reference-profile-checks.json')):raise ValueError('Fresh reference profile differs')
 return report
def main():
 report=verify('--write' in b.sys.argv);print(json.dumps({k:report[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

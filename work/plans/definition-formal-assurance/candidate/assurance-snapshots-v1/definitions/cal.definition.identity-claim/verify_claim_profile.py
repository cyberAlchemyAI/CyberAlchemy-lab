"""Candidate assurance/time/history policy profiles; actual source carriers stay separate."""
import copy,datetime,json,types
import build_candidate as b
import verifier as v
LEVELS={'self-asserted':0,'corroborated':1,'verified':2}
STATES={'proposed':{'current','contested','withdrawn'},'current':{'contested','expired','withdrawn'},'contested':{'current','expired','withdrawn'},'expired':set(),'withdrawn':set()}
def load(n):return json.loads((b.UNIT/n).read_bytes())
def baseline():
 rec=json.loads((b.ROOT/'authority/artifact-types/identity-claim/v1/fixtures/valid/record.json').read_bytes())
 return {'record':rec,'reference_binding':{'reference_ref':rec['person_reference_ref'],'person_hypothesis':'hypothetical-person:1','identifier':rec['asserted_identifier'],'scope':rec['claim_scope']},'policy_binding':{'policy_ref':rec['assurance_policy_ref'],'scope':rec['claim_scope'],'allowed_levels':list(LEVELS)},'evidence_bindings':[{'evidence_ref':ref,'policy_ref':rec['assurance_policy_ref'],'reference_ref':rec['person_reference_ref'],'identifier':rec['asserted_identifier'],'scope':rec['claim_scope'],'supported_level':'self-asserted','support_record_ref':'hypothetical-support:1'} for ref in rec['evidence_refs']],'assessment_time':'2026-10-05T16:00:00Z','claim_only_conclusions':[],'independently_supported_outcomes':[]}
def date(s):return datetime.datetime.strptime(s,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
def errors(p):
 es=[];rec=p['record'];ref=p['reference_binding'];policy=p['policy_binding'];evidence={x['evidence_ref']:x for x in p['evidence_bindings']}
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected candidate profile')
 ck(rec['authority_effect']=='none' and rec['status']=='candidate-unadmitted','candidate record non-effect retained')
 ck(ref['reference_ref']==rec['person_reference_ref'] and ref['identifier']==rec['asserted_identifier'] and ref['scope']==rec['claim_scope'] and bool(ref['person_hypothesis']),'candidate asserted reference/identifier/Person-hypothesis/scope binding exact')
 ck(policy['policy_ref']==rec['assurance_policy_ref'] and policy['scope']==rec['claim_scope'],'declared assurance policy scope exact')
 ck(rec['assurance_level'] in LEVELS and rec['assurance_level'] in policy['allowed_levels'],'assurance label within selected policy')
 ck(bool(rec['evidence_refs']) and len(set(rec['evidence_refs']))==len(rec['evidence_refs']),'nonempty distinct candidate evidence references')
 ck(len(evidence)==len(p['evidence_bindings']),'support binding identities not duplicated')
 for id in rec['evidence_refs']:
  support=evidence.get(id)
  if support is None:es.append('selected candidate evidence reference unresolved');continue
  ck(support['policy_ref']==rec['assurance_policy_ref'] and support['reference_ref']==rec['person_reference_ref'] and support['identifier']==rec['asserted_identifier'] and support['scope']==rec['claim_scope'],'support declared exact assertion/policy/scope')
  ck(bool(support['support_record_ref']),'separate symbolic support record retained')
 ck(any(LEVELS.get(x['supported_level'],-1)>=LEVELS.get(rec['assurance_level'],99) for x in p['evidence_bindings'] if x['evidence_ref'] in rec['evidence_refs']),'label alone cannot exceed selected symbolic support assessment')
 try:
  asserted=date(rec['asserted_at']);now=date(p['assessment_time']);ck(asserted<=now,'assertion not in future at candidate assessment time')
  if rec['expires_at'] is not None:
   expires=date(rec['expires_at']);ck(asserted<expires,'expiry strictly after assertion')
   if rec['claim_state']=='current':ck(now<expires,'current label not allowed after candidate expiry')
 except (ValueError,TypeError):es.append('valid parsed UTC calendar dates required by candidate policy')
 ck(rec['claim_state'] in STATES,'selected state vocabulary')
 ck(bool(rec['owner_ref']) and bool(rec['owner_route']) and bool(rec['challenge_route']) and bool(rec['limitations']),'attribution/challenge/limitations recorded')
 ck(not p['claim_only_conclusions'],'no claim-only conclusion in selected profile')
 ck(set(p['independently_supported_outcomes'])<=set(b.OUTCOMES),'independent world-outcome labels within selected bounded profile')
 return es
def controls():
 rows=[]
 def add(id,change,bad=False):
  p=baseline();change(p);es=errors(p)
  if bool(es)!=bad:raise ValueError('Unexpected selected assurance profile '+id+' '+str(es))
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_identity_verified':False,'actual_runtime_execution':False})
 add('self-asserted-bounded-reference-and-hypothetical-support',lambda p:None)
 add('independent-world-facts-allowed',lambda p:p.update(independently_supported_outcomes=b.OUTCOMES))
 def supported(p):p['record']['assurance_level']='verified';p['evidence_bindings'][0]['supported_level']='verified';p['evidence_bindings'][0]['support_record_ref']='hypothetical-separate-verification:1'
 add('verified-symbolic-label-with-separate-symbolic-support-not-real-verification',supported)
 add('contested-assertion-retained-as-claim-content',lambda p:p['record'].update(claim_state='contested'))
 add('expired-content-retained-with-expired-state',lambda p:p['record'].update(claim_state='expired',expires_at='2026-10-05T15:30:00Z'))
 add('verified-label-without-support-promotion',lambda p:p['record'].update(assurance_level='verified'),True)
 add('unresolved-evidence',lambda p:p.update(evidence_bindings=[]),True)
 add('empty-evidence-set',lambda p:p['record'].update(evidence_refs=[]),True)
 add('duplicate-evidence-reference',lambda p:p['record']['evidence_refs'].append(p['record']['evidence_refs'][0]),True)
 add('wrong-reference-token',lambda p:p['reference_binding'].update(reference_ref='other'),True)
 add('wrong-asserted-identifier',lambda p:p['reference_binding'].update(identifier='other'),True)
 add('missing-Person-hypothesis',lambda p:p['reference_binding'].update(person_hypothesis=''),True)
 add('wrong-claim-scope',lambda p:p['record'].update(claim_scope='other'),True)
 add('wrong-policy-version',lambda p:p['policy_binding'].update(policy_ref='other@2'),True)
 add('policy-does-not-allow-assurance-level',lambda p:p['policy_binding'].update(allowed_levels=['verified']),True)
 for key in ['policy_ref','reference_ref','identifier','scope']:add('support-'+key+'-mismatch',lambda p,key=key:p['evidence_bindings'][0].__setitem__(key,'other'),True)
 add('missing-separate-support-record',lambda p:p['evidence_bindings'][0].update(support_record_ref=''),True)
 add('invalid-calendar-date',lambda p:p['record'].update(asserted_at='2026-99-99T99:99:99Z'),True)
 add('future-assertion',lambda p:p['record'].update(asserted_at='2026-10-06T15:10:00Z'),True)
 add('expiry-before-assertion',lambda p:p['record'].update(expires_at='2026-10-04T15:10:00Z'),True)
 add('current-claim-after-expiry',lambda p:p['record'].update(expires_at='2026-10-05T15:30:00Z'),True)
 add('unsupported-state',lambda p:p['record'].update(claim_state='admitted'),True)
 add('owner-attribution-empty',lambda p:p['record'].update(owner_ref=''),True)
 add('challenge-route-empty',lambda p:p['record'].update(challenge_route=''),True)
 add('limitations-empty',lambda p:p['record'].update(limitations=[]),True)
 for n in b.OUTCOMES:add('claim-alone-does-not-establish-'+n,lambda p,n=n:p.update(claim_only_conclusions=[n]),True)
 add('actual-authority-field-forbidden',lambda p:p['record'].update(authority_effect='granted'),True)
 add('candidate-profile-runtime-field-forbidden',lambda p:p.update(runtime=True),True)
 return rows
def frames():
 rows=[]
 def baseframe():return {'before_state':'current','after_state':'contested','before_reference':'reference:1','after_reference':'reference:1','before_person_hypothesis':'Person:hyp1','after_person_hypothesis':'Person:hyp1','before_assurance':'self-asserted','after_assurance':'self-asserted','separate_review_ref':None,'before_authority':['permission:hyp-independent'],'after_authority':['permission:hyp-independent'],'separate_authority_decision_ref':None}
 def check(f):
  es=[]
  if f['after_state'] not in STATES.get(f['before_state'],set()):es.append('selected candidate state transition not permitted')
  if f['before_reference']!=f['after_reference'] or f['before_person_hypothesis']!=f['after_person_hypothesis']:es.append('same selected assertion history step must retain declared subject pair')
  if (f['after_state']=='current' or LEVELS[f['after_assurance']]>LEVELS[f['before_assurance']]) and f['separate_review_ref'] is None:es.append('selected symbolic confirmation/promotion requires separate review marker')
  if f['before_authority']!=f['after_authority'] and f['separate_authority_decision_ref'] is None:es.append('claim lifecycle alone does not change independent authority facts')
  return es
 def add(id,change,bad=False):
  f=baseframe();change(f);es=check(f)
  if bool(es)!=bad:raise ValueError('Unexpected history profile '+id+' '+str(es))
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('challenge-retains-assertion-and-independent-authority',lambda f:None)
 add('withdrawal-retains-assertion-history',lambda f:f.update(after_state='withdrawn'))
 add('expiry-retains-assertion-history',lambda f:f.update(after_state='expired'))
 add('separate-symbolic-confirmation-of-contested-claim',lambda f:f.update(before_state='contested',after_state='current',separate_review_ref='hypothetical-review:1'))
 add('separate-symbolic-authority-decision-not-claim-only',lambda f:f.update(after_authority=[],separate_authority_decision_ref='hypothetical-independent-decision:1'))
 add('withdrawn-is-terminal-in-selected-policy',lambda f:f.update(before_state='withdrawn',after_state='current',separate_review_ref='hypothetical-review:1'),True)
 add('expired-is-terminal-in-selected-policy',lambda f:f.update(before_state='expired',after_state='current',separate_review_ref='hypothetical-review:1'),True)
 add('unreviewed-confirmation',lambda f:f.update(before_state='proposed',after_state='current'),True)
 add('unreviewed-assurance-promotion',lambda f:f.update(after_assurance='verified'),True)
 add('history-retargets-reference',lambda f:f.update(after_reference='other'),True)
 add('history-retargets-Person-hypothesis',lambda f:f.update(after_person_hypothesis='other'),True)
 add('challenge-revokes-permission-without-separate-decision',lambda f:f.update(after_authority=[]),True)
 add('claim-state-grants-permission-without-separate-decision',lambda f:f.update(after_authority=['permission:new']),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();root=b.ROOT/'authority/artifact-types/identity-claim/v1'
 paths={'descriptor':root/'artifact.json','schema':root/'schema.json','fixture':root/'fixtures/valid/record.json','artifact_projection':root/'ARTIFACT.md','fixture_projection':root/'fixtures/valid/RECORD.md','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','generator':b.ROOT/'tooling/generators/artifact_surface.py','shared_validator':b.ROOT/'tooling/validators/artifact_surface.py','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json','refinement':b.ROOT/'authority/artifact-types/candidates/0004-remaining-26-materialization/refinements/type.identity-claim.json'}
 for p in sorted((root/'fixtures/invalid').glob('*.json')):paths['negative_'+p.stem]=p
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());tr=next(x for x in reg['admitted_contracts'] if x['semantic_kind']=='typed-relation' and x['lifecycle_state']=='admitted-current');kind=next(x for x in kr['entries'] if x['relation_kind_ref']=='relation.asserts-identity-of');paths['Kind']=b.ROOT/kind['instance_path'];paths['TR_schema']=b.ROOT/tr['schema_path'];paths['TR_fixture']=(b.ROOT/tr['artifact_path']).parent/'fixtures/valid/record.json'
 for semantic in ['person-reference','person']:
  row=next(x for x in reg['admitted_contracts'] if x['semantic_kind']==semantic and x['lifecycle_state']=='admitted-current');paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=(b.ROOT/row['artifact_path']).parent/'fixtures/valid/record.json'
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};artifact=docs['descriptor'];fixture=docs['fixture'];schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 entry=next(x for x in reg['admitted_contracts'] if x['artifact_type_ref']==artifact['artifact_type_ref']);source=load('t.json')['payload']['source'];binding=artifact['semantic_definition_bindings'][0]
 ck('exact-current-Type-overlay-0070',entry['lifecycle_state']=='admitted-current' and entry['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and entry['artifact_sha256']==refs['descriptor']['sha256'] and entry['schema_sha256']==refs['schema']['sha256'])
 ck('historical-candidate-descriptor-and-fixture-wording-retained',artifact['status']==fixture['status']=='candidate-unadmitted' and artifact['authority_effect']==fixture['authority_effect']=='none')
 ck('exact-admitted-Definition-0053-binding',binding['definition_ref']==source['version_ref'] and binding['path']==source['path'] and binding['sha256']==source['sha256'] and binding['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION')
 ck('root-descriptor-and-closed-schema-bound',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'] and artifact['schema_digest']==refs['schema']['sha256'] and schema['additionalProperties'] is False)
 ck('shared-generator-and-validator-digests',artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['shared_validator']['sha256'])
 ck('positive-fixture-shape-valid',not list(validator.iter_errors(fixture)))
 negatives=[{'path':refs[n]['path'],'schema_rejected':bool(list(validator.iter_errors(docs[n])))} for n in sorted(refs) if n.startswith('negative_')];ck('four-hostile-fixtures-rejected',len(negatives)==4 and all(x['schema_rejected'] for x in negatives))
 mod=types.ModuleType('_bound_artifact_surface_renderer');mod.__file__=str(paths['generator']);exec(compile(raws['generator'],str(paths['generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture]);renderA=mod.render_artifact(artifact).encode();renderB=mod.render_instance(artifact,fixture).encode()
 ck('two-artifact-renders-exact-projection',renderA==mod.render_artifact(artifact).encode()==raws['artifact_projection'])
 ck('two-fixture-renders-exact-projection',renderB==mod.render_instance(artifact,fixture).encode()==raws['fixture_projection'])
 ck('renderers-preserve-inputs',before==[artifact,fixture])
 ck('refinement-declares-policy-not-identity-proof',docs['refinement']['target_id']=='type.identity-claim' and docs['refinement']['admission_effect']=='none' and docs['refinement']['review_state']=='revision-authorized-before-admission')
 joins={'claim_ref_equals_selected_PersonReference_node':fixture['person_reference_ref']==docs['person-reference_fixture']['node_id'],'asserted_identifier_equals_reference_value':fixture['asserted_identifier']==docs['person-reference_fixture']['reference_value'],'direct_Person_referent_field_present':'person_ref' in fixture or 'person_ref' in docs['person-reference_fixture'],'claim_id_listed_in_selected_Person_identity_evidence':fixture['node_id'] in docs['person_fixture']['payload']['identity_evidence_refs'],'assurance_policy_resolved':False,'evidence_attestation_authenticated':False}
 for semantic in ['person-reference','person']:ck(semantic+'-selected-fixture-shape-valid',not list(b.c.Draft202012Validator(docs[semantic+'_schema']).iter_errors(docs[semantic+'_fixture'])))
 ck('bounded-join-gap-not-assumed-denotation',joins=={'claim_ref_equals_selected_PersonReference_node':True,'asserted_identifier_equals_reference_value':False,'direct_Person_referent_field_present':False,'claim_id_listed_in_selected_Person_identity_evidence':False,'assurance_policy_resolved':False,'evidence_attestation_authenticated':False})
 probes=[]
 def probe(id,change,expected):
  rec=copy.deepcopy(fixture);change(rec);es=list(validator.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected actual Claim schema boundary '+id+' '+str([x.message for x in es]))
  probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_identity_verified':False,'actual_runtime_execution':False,'whole_source_conformance_established':False})
 probe('verified-label-without-new-evidence-accepted',lambda r:r.update(assurance_level='verified'),True)
 probe('nonexistent-reference-policy-and-evidence-accepted',lambda r:r.update(person_reference_ref='absent:ref',assurance_policy_ref='absent:policy',evidence_refs=['absent:evidence']),True)
 probe('invalid-calendar-digits-match-pattern',lambda r:r.update(asserted_at='2026-99-99T99:99:99Z'),True)
 probe('expiry-before-assertion-accepted',lambda r:r.update(expires_at='2026-10-04T15:10:00Z'),True)
 probe('current-label-past-expiry-accepted',lambda r:r.update(expires_at='2026-10-05T15:30:00Z'),True)
 probe('claim-owner-route-different-from-owner-ref-accepted',lambda r:r.update(owner_route='role:different-owner'),True)
 probe('empty-evidence-rejected',lambda r:r.update(evidence_refs=[]),False)
 probe('duplicate-evidence-rejected',lambda r:r['evidence_refs'].append(r['evidence_refs'][0]),False)
 probe('direct-Person-field-extra-rejected',lambda r:r.update(person_ref='person:hyp1'),False)
 probe('permission-field-extra-rejected',lambda r:r.update(permission='grant'),False)
 probe('unsupported-assurance-label-rejected',lambda r:r.update(assurance_level='admitted'),False)
 kp=docs['Kind']['payload'];ck('asserts-identity-Kind-exact-four-ordered-pairs',kind['lifecycle_state']=='admitted-current' and kind['instance_sha256']==refs['Kind']['sha256'] and kind['exact_endpoint_pair_count']==len(kp['allowed_endpoint_pairs'])==4 and kind['required_qualifier_axes']==kp['qualifier_contract']['required_axes']==['assertion_kind','claim_scope'])
 ck('Kind-forbids-merge-authority-transfer-private-inference',kp['forbidden_inferences']==['identity-merge','authority-transfer','private-attribute-inference'])
 ck('current-TR-v3-schema-bound',tr['artifact_type_ref']=='cal.artifact-type.typed-relation/v3' and tr['schema_sha256']==refs['TR_schema']['sha256'])
 relation=copy.deepcopy(docs['TR_fixture']);relation['payload'].update(relation_kind_ref='relation.asserts-identity-of',source={'kind':'identity-claim','ref':fixture['node_id'],'version_ref':fixture['node_id']+'@example-revision'},target={'kind':'person-reference','ref':fixture['person_reference_ref'],'version_ref':fixture['person_reference_ref']+'@example-revision'},qualifiers={'assertion_kind':'identifier-claim','claim_scope':fixture['claim_scope']});trvalidator=b.c.Draft202012Validator(docs['TR_schema']);relation_probes=[]
 def relation_probe(id,change,expected):
  rec=copy.deepcopy(relation);change(rec);es=list(trvalidator.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected ordered-pair/qualifier probe '+id)
  relation_probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_reference_denotation_established':False,'actual_relation_created':False,'whole_source_conformance_established':False})
 relation_probe('Claim-to-Reference-current-shape',lambda r:None,True)
 relation_probe('unresolved-target-reference-shape-accepted',lambda r:r['payload']['target'].update(ref='absent:ref'),True)
 relation_probe('different-claim-scope-string-shape-accepted',lambda r:r['payload']['qualifiers'].update(claim_scope='other-scope'),True)
 relation_probe('Claim-direct-to-Person-not-admitted-pair',lambda r:r['payload']['target'].update(kind='person'),False)
 relation_probe('Reference-to-Person-separately-admitted-pair',lambda r:r['payload'].update(source={'kind':'person-reference','ref':'hyp-ref','version_ref':'hyp-ref@1'},target={'kind':'person','ref':'hyp-person','version_ref':'hyp-person@1'}),True)
 relation_probe('extra-actual-identity-proof-qualifier-rejected',lambda r:r['payload']['qualifiers'].update(identity_verified=True),False)
 relation_probe('missing-scope-qualifier-rejected',lambda r:r['payload']['qualifiers'].pop('claim_scope'),False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();history=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_claim_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=json.loads((b.BASE/'definitions/cal.definition.classification/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-identity-claim-profile/v1-candidate','status':'PASS-for-bounded-claim-assurance-history-and-current-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_history_frame_count':len(history),'rejected_history_frames':sum(x['expected_rejection'] for x in history),'finite_history_frames':history,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'actual_relation_schema_probes':relation_probes,'negative_fixture_checks':negatives,'actual_join_observations':joins,'actual_relation_endpoint_pairs':kp['allowed_endpoint_pairs'],'source_mapping_gaps':{'mapping_reviewed':False,'PersonReference_fixture_literal_join_established':True,'identifier_to_Person_denotation_established':False,'real_attributor_evidence_policy_assurance_authenticated':False,'selected_state_time_history_and_privacy_policy_reviewed':False,'source_precedence_and_inherited_Person_semantics_reviewed':False,'whole_source_conformance_established':False},'new_claims_Person_data_assertions_or_relations_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Candidate bounded assertion/support-assessment/time/state profiles and finite history frames, plus exact current source-carrier schemas/fixtures/projections. Hypothetical support/review markers do not establish authentic evidence, verified Person denotation or a real decision. No owner-approved assurance or transition policy, actual processing/inference compliance, admission, world identity truth or whole-definition acceptance.'}
 if write:b.put('claim-profile-checks.json',report)
 elif not b.r.same_json(report,load('claim-profile-checks.json')):raise ValueError('Fresh claim profile differs')
 return report
def main():
 report=verify('--write' in b.sys.argv);print(json.dumps({k:report[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

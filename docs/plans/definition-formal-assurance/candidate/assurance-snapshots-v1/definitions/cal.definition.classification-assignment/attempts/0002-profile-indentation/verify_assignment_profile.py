"""Candidate binding/attribution/correction records and read-only carrier observations."""
import ast,copy,itertools,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
CATALOG={'subjects':{'subject@1':'subject','subject@2':'subject','other@1':'other'},'axes':{('result','sv1'),('result','sv2')},'values':{'v1':('result','sv1'),'v2':('result','sv2')},'actions':{'action1','action2'},'methods':{'method1'},'implementations':{'implementation1'},'evidence':{'e1','e2','counter1'},'decisions':{'decision1'}}
BASIS=['explicit','measured','inferred','imported','owner-declared'];STATUSES=['proposed','confirmed','disputed','rejected','superseded','expired']
def record():
 return {'assignment_id':'old','assignment_revision':'old@1','subject_id':'subject','subject_revision':'subject@1','scheme_version':'sv1','axis_id':'result','value_id':'v1','basis':'owner-declared','action_ref':'action1','method_used':True,'method_ref':'method1','implementation_used':True,'implementation_ref':'implementation1','evidence_refs':['e1'],'counterevidence_refs':[],'effective_period':{'from':0,'until':10},'status':'proposed','decision_ref':None,'owner_ref':'owner','challenge_ref':'route','authority_effect':'none'}
def profile_errors(rec):
 errors=[]
 if set(rec)!=set(record()):return ['closed-assignment-profile-fields']
 if any(not isinstance(rec[n],str) or not rec[n] for n in ['assignment_id','assignment_revision','subject_id','subject_revision','scheme_version','axis_id','value_id','action_ref','owner_ref','challenge_ref']):errors.append('missing-exact-required-field')
 if CATALOG['subjects'].get(rec['subject_revision'])!=rec['subject_id']:errors.append('subject-revision-owner-mismatch-or-unresolved')
 if (rec['axis_id'],rec['scheme_version']) not in CATALOG['axes']:errors.append('unresolved-exact-axis-version')
 if CATALOG['values'].get(rec['value_id'])!=(rec['axis_id'],rec['scheme_version']):errors.append('value-not-allowed-in-exact-axis-version')
 if rec['basis'] not in BASIS:errors.append('unsupported-basis-in-selected-profile')
 if rec['action_ref'] not in CATALOG['actions']:errors.append('unresolved-attributing-action')
 for prefix,key in [('method','methods'),('implementation','implementations')]:
  if type(rec[prefix+'_used']) is not bool:errors.append('invalid-used-marker');continue
  if rec[prefix+'_used'] and rec[prefix+'_ref'] not in CATALOG[key]:errors.append('unresolved-'+prefix+'-when-used')
  if not rec[prefix+'_used'] and rec[prefix+'_ref'] is not None:errors.append('unused-'+prefix+'-not-null-in-selected-profile')
 for key in ['evidence_refs','counterevidence_refs']:
  if len(set(rec[key]))!=len(rec[key]) or any(e not in CATALOG['evidence'] for e in rec[key]):errors.append('unresolved-or-duplicate-'+key)
 if rec['basis'] in ['measured','inferred'] and not rec['evidence_refs']:errors.append('selected-measurement-inference-evidence-required')
 period=rec['effective_period']
 if set(period)!={'from','until'} or any(type(period[n]) is not int for n in ['from','until']) or period['from']>period['until']:errors.append('invalid-selected-finite-effective-period')
 if rec['status'] not in STATUSES:errors.append('unsupported-status-in-selected-profile')
 if rec['decision_ref'] is not None and rec['decision_ref'] not in CATALOG['decisions']:errors.append('unresolved-decision-reference')
 if rec['status']=='confirmed' and rec['decision_ref'] not in CATALOG['decisions']:errors.append('selected-confirmation-decision-required')
 if rec['authority_effect']!='none':errors.append('assignment-is-not-authority-grant')
 return sorted(set(errors))
def controls():
 rows=[]
 def add(id,change,rejected=False):
  rec=record();change(rec);errors=profile_errors(rec)
  if bool(errors)!=rejected:raise ValueError('Profile expectation mismatch '+id+str(errors))
  rows.append({'case_id':id,'record':rec,'errors':errors,'expected_rejection':rejected,'actual_runtime_execution':False,'owner_policy_reviewed':False,'world_truth_established':False})
 add('exact-proposed-attributable-binding',lambda r:None)
 add('measured-basis-with-selected-evidence',lambda r:r.update(basis='measured'))
 add('counterevidence-retained-without-truth-promotion',lambda r:r.update(counterevidence_refs=['counter1']))
 add('confirmed-record-with-separate-decision-no-authority',lambda r:r.update(status='confirmed',decision_ref='decision1'))
 add('method-implementation-unused-have-no-invented-execution',lambda r:r.update(method_used=False,method_ref=None,implementation_used=False,implementation_ref=None))
 add('owner-declared-empty-evidence-is-explicit-selected-policy',lambda r:r.update(evidence_refs=[]))
 add('same-subject-different-exact-revision',lambda r:r.update(subject_revision='subject@2'))
 add('unresolved-subject-revision',lambda r:r.update(subject_revision='subject@unknown'),True)
 add('subject-ref-does-not-own-exact-revision',lambda r:r.update(subject_revision='other@1'),True)
 add('unresolved-scheme-version',lambda r:r.update(scheme_version='sv0'),True)
 add('unresolved-axis',lambda r:r.update(axis_id='other'),True)
 add('value-from-other-version',lambda r:r.update(value_id='v2'),True)
 add('unresolved-value',lambda r:r.update(value_id='missing'),True)
 add('basis-not-from-selected-vocabulary',lambda r:r.update(basis='automatic-truth'),True)
 add('unresolved-action',lambda r:r.update(action_ref='missing'),True)
 add('method-used-but-unresolved',lambda r:r.update(method_ref='missing'),True)
 add('implementation-used-but-unresolved',lambda r:r.update(implementation_ref='missing'),True)
 add('unused-method-does-not-invent-reference',lambda r:r.update(method_used=False),True)
 add('unused-implementation-does-not-invent-reference',lambda r:r.update(implementation_used=False),True)
 add('used-marker-bool-not-integer',lambda r:r.update(method_used=1),True)
 add('unresolved-evidence',lambda r:r.update(evidence_refs=['missing']),True)
 add('duplicate-evidence',lambda r:r.update(evidence_refs=['e1','e1']),True)
 add('unresolved-counterevidence',lambda r:r.update(counterevidence_refs=['missing']),True)
 add('measured-without-selected-evidence',lambda r:r.update(basis='measured',evidence_refs=[]),True)
 add('inferred-without-selected-evidence',lambda r:r.update(basis='inferred',evidence_refs=[]),True)
 add('invalid-period-order',lambda r:r.update(effective_period={'from':10,'until':0}),True)
 add('bool-not-period-integer',lambda r:r.update(effective_period={'from':False,'until':10}),True)
 add('period-extra-field',lambda r:r.update(effective_period={'from':0,'until':10,'authority':True}),True)
 add('unsupported-lifecycle-vocabulary',lambda r:r.update(status='active-grants-authority'),True)
 add('confirmed-without-decision',lambda r:r.update(status='confirmed'),True)
 add('decision-unresolved',lambda r:r.update(decision_ref='missing'),True)
 add('assignment-identity-missing',lambda r:r.update(assignment_id=''),True)
 add('owner-missing',lambda r:r.update(owner_ref=''),True)
 add('challenge-route-missing',lambda r:r.update(challenge_ref=''),True)
 add('authority-effect-not-assignment',lambda r:r.update(authority_effect='granted'),True)
 add('hidden-runtime-field',lambda r:r.update(runtime=True),True)
 return rows
def frame():
 old=record();new=copy.deepcopy(old);new.update(assignment_id='new',assignment_revision='new@1',subject_revision='subject@2',scheme_version='sv2',value_id='v2',action_ref='action2',evidence_refs=['e2'])
 return {'operation':'correct-assignment','old_id':'old','new_id':'new','before':[old],'after':[copy.deepcopy(old),new],'subject_identity_before':{'subject':'subject-id'},'subject_identity_after':{'subject':'subject-id'},'successor_links':[['new','old']],'assignment_only_other_axis_inferences':[]}
def frame_errors(rec):
 errors=[]
 if rec['operation']!='correct-assignment':return ['unsupported-operation-no-selected-frame']
 for key in ['before','after']:
  ids=[x['assignment_id'] for x in rec[key]]
  if len(ids)!=len(set(ids)):errors.append('duplicate-assignment-identity')
  for x in rec[key]:
   if profile_errors(x):errors.append('invalid-'+key+'-binding-profile')
 before={x['assignment_id']:x for x in rec['before']};after={x['assignment_id']:x for x in rec['after']}
 for id,old in before.items():
  if after.get(id)!=old:errors.append('old-record-deleted-or-overwritten')
  if rec['subject_identity_before'].get(old['subject_id'])!=rec['subject_identity_after'].get(old['subject_id']):errors.append('subject-identity-changed')
 old=before.get(rec['old_id']);new=after.get(rec['new_id'])
 if old is None or new is None:errors.append('missing-correction-endpoint')
 if rec['new_id'] in before or rec['new_id']==rec['old_id']:errors.append('successor-not-fresh')
 if [rec['new_id'],rec['old_id']] not in rec['successor_links']:errors.append('missing-exact-successor-direction')
 if old is not None and new is not None and old['subject_id']!=new['subject_id']:errors.append('selected-same-subject-correction-retargeted')
 if rec['assignment_only_other_axis_inferences']:errors.append('assignment-alone-other-axis-inference')
 return sorted(set(errors))
def frames():
 rows=[]
 def add(id,change,rejected=False):
  rec=frame();change(rec);errors=frame_errors(rec)
  if bool(errors)!=rejected:raise ValueError('Frame expectation mismatch '+id+str(errors))
  rows.append({'case_id':id,'frame':rec,'errors':errors,'expected_rejection':rejected,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('fresh-successor-retains-entire-prior-evidence-lifecycle-record',lambda r:None)
 def metadata(r):r['after'][1].update(subject_revision='subject@1',scheme_version='sv1',value_id='v1')
 add('metadata-only-successor-permitted-separately',metadata)
 for key,value in [('assignment_revision','old@2'),('subject_revision','subject@2'),('scheme_version','sv2'),('value_id','v2'),('basis','measured'),('action_ref','action2'),('method_ref',None),('implementation_ref',None),('evidence_refs',['e2']),('counterevidence_refs',['counter1']),('effective_period',{'from':1,'until':9}),('status','expired'),('decision_ref','decision1'),('owner_ref','other-owner'),('challenge_ref','other-route')]:add('overwritten-prior-'+key,lambda r,key=key,value=value:r['after'][0].update({key:value}),True)
 add('predecessor-deleted',lambda r:r['after'].pop(0),True)
 add('subject-identity-changed',lambda r:r.update(subject_identity_after={'subject':'different-id'}),True)
 add('already-recorded-successor-not-fresh',lambda r:r['before'].append(copy.deepcopy(r['after'][1])),True)
 add('duplicate-successor-identity',lambda r:r['after'].append(copy.deepcopy(r['after'][1])),True)
 add('reversed-successor-link',lambda r:r.update(successor_links=[['old','new']]),True)
 add('missing-successor-link',lambda r:r.update(successor_links=[]),True)
 add('other-axis-inference-without-independent-support',lambda r:r.update(assignment_only_other_axis_inferences=['evidence-posture=confirmed']),True)
 add('retargeted-subject-is-not-selected-correction',lambda r:r['after'][1].update(subject_id='other',subject_revision='other@1'),True)
 add('successor-missing',lambda r:r['after'].pop(1),True)
 add('unselected-retirement-operation',lambda r:r.update(operation='retire-subject'),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings()
 root=b.ROOT/'authority/artifact-types/classification-assignment/v1'
 paths={'descriptor':root/'artifact.json','schema':root/'schema.json','fixture':root/'fixtures/valid/record.json','artifact_projection':root/'ARTIFACT.md','fixture_projection':root/'fixtures/valid/RECORD.md','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','relation_model':b.ROOT/'authority/relation-kinds/candidates/0005-definition-complete-extension/model.json','generator':b.ROOT/'tooling/generators/endpoint_carrier.py','validator':b.ROOT/'tooling/validators/definition_complete_carrier.py','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','definition_registry':b.ROOT/'authority/definitions/registry.json','review':b.ROOT/'.arcanum/ontology-vault/2026-10-05-classification-model-review.md'}
 for p in sorted((root/'fixtures/invalid').glob('*.json')):paths['negative_'+p.stem]=p
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:b.r.read_bytes(b.ROOT,x['path']) for n,x in refs.items()};artifact=json.loads(raw['descriptor']);schema=json.loads(raw['schema']);fixture=json.loads(raw['fixture']);model=json.loads(raw['relation_model']);reg=json.loads(raw['type_registry']);definitionreg=json.loads(raw['definition_registry']);source=load('t.json')['payload']['source'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema)
 # Execute only the pure roles_for AST; canonical validate_package writes receipts and is never called.
 tree=ast.parse(raw['validator']);role_function=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='roles_for');env={};exec(compile(ast.Module(body=[role_function],type_ignores=[]),str(paths['validator']),'exec'),env);roles=env['roles_for']('classification-assignment',model);allowed={(x['relation_kind_ref'],x['direction'],kind) for x in roles for kind in x['counterpart_kinds']}
 mod=types.ModuleType('_bound_endpoint_renderer');mod.__file__=str(paths['generator']);exec(compile(raw['generator'],str(paths['generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture]);renderA=mod.render_artifact(artifact).encode();renderB=mod.render_instance(artifact,fixture).encode()
 negative=[{'path':refs[n]['path'],'schema_rejected':bool(list(validator.iter_errors(json.loads(raw[n]))))} for n in sorted(refs) if n.startswith('negative_')]
 entries=[x for x in reg['admitted_contracts'] if x['artifact_type_ref']==artifact['artifact_type_ref']];binding=artifact['semantic_definition_bindings'][0];checks=[]
 def ck(id,value):checks.append({'check_id':id,'result':bool(value)})
 ck('current-overlay-exact-0070',len(entries)==1 and entries[0]['artifact_sha256']==refs['descriptor']['sha256'] and entries[0]['schema_sha256']==refs['schema']['sha256'] and entries[0]['lifecycle_state']=='admitted-current' and entries[0]['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('historical-descriptor-candidate-ceiling-retained',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none')
 ck('current-source-definition-65',binding['definition_ref']==source['version_ref'] and binding['sha256']==source['sha256'] and binding['path']==source['path'] and binding['admission_decision_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION' and definitionreg['current_lookup'][source['definition_id']]==source['version_ref'])
 ck('root-descriptor-binding-exact',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'])
 ck('schema-digest-exact-closed',artifact['schema_digest']==refs['schema']['sha256'] and schema['additionalProperties'] is False)
 ck('candidate-relation-model-bound',artifact['relation_model_binding']['sha256']==refs['relation_model']['sha256'] and model['status']=='candidate-complete-awaiting-owner-review')
 ck('exact-relation-role-triples',artifact['relation_roles']==roles and artifact['allowed_relation_kinds']==sorted({x['relation_kind_ref'] for x in roles}))
 ck('fixture-relation-triples-in-exact-role-surface',{(x['relation_kind_ref'],x['direction'],x['counterpart_kind']) for x in fixture['relation_refs']}<=allowed)
 ck('fixture-schema-valid',not list(validator.iter_errors(fixture)))
 ck('five-schema-hostiles-rejected',len(negative)==5 and all(x['schema_rejected'] for x in negative))
 ck('generator-digest-exact',artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'])
 ck('validator-digest-exact',artifact['validation_contract']['shared_validator_sha256']==refs['validator']['sha256'])
 ck('renderers-do-not-mutate-selected-inputs',before==[artifact,fixture])
 ck('two-artifact-renders-and-projection-equal',renderA==mod.render_artifact(artifact).encode()==raw['artifact_projection'])
 ck('two-fixture-renders-and-projection-equal',renderB==mod.render_instance(artifact,fixture).encode()==raw['fixture_projection'])
 ck('four-explicit-noncollapse-contracts',len(artifact['orthogonality_rules'])==4 and set(artifact['hostile_non_collapse'])=={'typed-relation','identity-claim'})
 ck('whole-file-review-source-sha-exact',refs['review']['sha256']=='2f8147089d6b245d5696d132c3bf49f757bdd43cebe03ff032d92202946c7439')
 probes=[]
 def probe(id,change,accept=True):
  rec=copy.deepcopy(fixture);change(rec);errors=list(validator.iter_errors(rec));accepted=not errors
  if accepted!=accept:raise ValueError('Unexpected actual schema boundary '+id)
  probes.append({'case_id':id,'schema_accepted':accepted,'record':rec,'errors':[x.message for x in errors],'whole_source_conformance_established':False,'actual_runtime_execution':False})
 probe('subject-ref-and-version-identity-mismatch',lambda r:r['payload'].update(subject_version_ref='other-subject@7'))
 probe('unresolved-exact-binding-and-attribution-strings',lambda r:r['payload'].update(subject_ref='unknown-subject',subject_version_ref='unknown-revision',scheme_version_ref='unversioned-scheme',axis_ref='unknown-axis',value_ref='unknown-value',action_ref='unknown-action',method_ref='unknown-method',implementation_ref='unknown-implementation'))
 probe('unsupported-assignment-basis-string',lambda r:r['payload'].update(basis='automatic-world-truth'))
 probe('status-string-does-not-enforce-confirmation-policy',lambda r:r['payload'].update(status='confirmed-grants-authority'))
 probe('empty-evidence-lists-shape-accepted',lambda r:r.update(evidence_refs=[],payload={**r['payload'],'evidence_refs':[]}))
 probe('unparsed-effective-period-string',lambda r:r['payload'].update(effective_period='not-a-defined-period'))
 probe('self-successor-reference-shape-accepted',lambda r:r.update(successor_refs=[r['node_id']]))
 probe('relation-role-cross-product-outside-exact-triples',lambda r:r.update(relation_refs=[{'relation_kind_ref':'relation.successor-of','direction':'target','counterpart_kind':'decision','counterpart_ref':'decision:x'}]))
 probe('top-lifecycle-and-payload-status-unmapped',lambda r:r.update(lifecycle_state='historical',payload={**r['payload'],'status':'active'}))
 probe('counterevidence-extra-payload-field-closed',lambda r:r['payload'].update(counterevidence_refs=['evidence:counter']),False)
 probe('method-implementation-omission-shape-rejected',lambda r:(r['payload'].pop('method_ref'),r['payload'].pop('implementation_ref')),False)
 probe('authority-effect-shape-rejected',lambda r:r.update(authority_effect='granted'),False)
 bad=probes[7]['record']['relation_refs'][0];ck('role-cross-product-probe-outside-exact-role-surface',(bad['relation_kind_ref'],bad['direction'],bad['counterpart_kind']) not in allowed)
 ck('format-and-required-version-field-do-not-resolve-subject-scheme',schema['properties']['schema_version']['const']=='cyberalchemy-lab-classification-assignment/v1' and schema['properties']['payload']['properties']['scheme_version_ref']=={'minLength':1,'type':'string'})
 sibling_kinds=['classification-scheme','classification-value','agent-instance','agent-action','implementation','measurement-method']
 sibling_paths={kind+'_fixture':b.ROOT/('authority/artifact-types/'+kind+'/v1/fixtures/valid/record.json') for kind in sibling_kinds}
 for kind in sibling_kinds:sibling_paths[kind+'_schema']=b.ROOT/('authority/artifact-types/'+kind+'/v1/schema.json')
 siblings={n:b.ref(p) for n,p in sibling_paths.items()};sibling_docs={kind:json.loads(sibling_paths[kind+'_fixture'].read_bytes()) for kind in sibling_kinds}
 sibling_validity=[]
 for kind in sibling_kinds:
  selected_schema=json.loads(sibling_paths[kind+'_schema'].read_bytes());b.c.Draft202012Validator.check_schema(selected_schema);errors=list(b.c.Draft202012Validator(selected_schema).iter_errors(sibling_docs[kind]));sibling_validity.append({'kind':kind,'shape_valid':not errors})
 ck('six-selected-sibling-fixtures-individually-shape-valid',len(sibling_validity)==6 and all(x['shape_valid'] for x in sibling_validity))
 scheme=sibling_docs['classification-scheme'];value=sibling_docs['classification-value'];subject=sibling_docs['agent-instance'];action=sibling_docs['agent-action'];implementation=sibling_docs['implementation'];method=sibling_docs['measurement-method'];p=fixture['payload']
 join={'assignment-scheme-is-selected-scheme-node':p['scheme_version_ref']==scheme['node_id'],'assignment-value-is-selected-value-node':p['value_ref']==value['node_id'],'assignment-value-listed-by-selected-scheme':p['value_ref'] in scheme['payload']['value_refs'],'assignment-axis-listed-by-selected-scheme':p['axis_ref'] in scheme['payload']['axis_refs'],'assignment-axis-agrees-with-selected-value':p['axis_ref']==value['payload']['axis_ref'],'assignment-scheme-literal-agrees-with-selected-value':p['scheme_version_ref']==value['payload']['scheme_ref'],'assignment-subject-is-selected-agent-instance':p['subject_ref']==subject['node_id'],'assignment-action-is-selected-agent-action':p['action_ref']==action['node_id'],'assignment-implementation-is-selected-implementation':p['implementation_ref']==implementation['node_id'],'assignment-method-is-selected-measurement-method':p['method_ref']==method['node_id'],'assignment-subject-version-is-literal-subject-plus-revision':p['subject_version_ref']==p['subject_ref']+'@1','assignment-implementation-literal-agrees-with-agent-instance':p['implementation_ref']==subject['payload']['implementation_ref'],'assignment-subject-literal-agrees-with-action-actor':p['subject_ref']==action['payload']['agent_instance_ref']}
 ck('selected-fixture-literal-join-limits-retained',join=={'assignment-scheme-is-selected-scheme-node':False,'assignment-value-is-selected-value-node':False,'assignment-value-listed-by-selected-scheme':True,'assignment-axis-listed-by-selected-scheme':True,'assignment-axis-agrees-with-selected-value':True,'assignment-scheme-literal-agrees-with-selected-value':True,'assignment-subject-is-selected-agent-instance':False,'assignment-action-is-selected-agent-action':False,'assignment-implementation-is-selected-implementation':False,'assignment-method-is-selected-measurement-method':False,'assignment-subject-version-is-literal-subject-plus-revision':True,'assignment-implementation-literal-agrees-with-agent-instance':True,'assignment-subject-literal-agrees-with-action-actor':True})
 ck('two-recorded-status-loci-kept-distinct',fixture['lifecycle_state']=='candidate' and p['status']=='active')
  if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();correction_frames=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_assignment_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'verifier.py',b.IMPL/'contracts.py']]
 b.unchanged(context['sources']+list(refs.values())+list(siblings.values())+bindings);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-classification-assignment-profile/v1-candidate','status':'PASS-for-exact-candidate-assignment-binding-correction-frames-and-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'sibling_source_inputs':siblings,'actual_join_observations':join,'sibling_fixture_validity':sibling_validity,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_correction_frame_count':len(correction_frames),'rejected_correction_frames':sum(x['expected_rejection'] for x in correction_frames),'finite_correction_frames':correction_frames,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'negative_fixture_checks':negative,'actual_roles':roles,'source_mapping_gaps':{'mapping_reviewed':False,'exact_subject_revision_value_axis_scheme_resolution_established':False,'immutable_record_and_governance_projection_mapping_pending':True,'attribution_reference_is_not_execution_or_authority':True,'evidence_status_period_and_confirmation_policy_pending':True,'generic_MethodRef_has_no_fabricated_current_Definition':True,'correction_permission_and_runtime_proof_established':False,'whole_source_conformance_established':False},'new_assignments_corrections_or_actions_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Candidate bounded assignment/attribution records/correction frames and selected current carrier bytes/fixtures/renderers. No reviewed policy denotation, whole source conformity, immutable-assignment/runtime preservation implementation, exact subject/axis/value/version resolver, owner fidelity, actual correction, world truth or unbounded trace proof.'}
 if write:b.put('assignment-profile-checks.json',report)
 elif not b.r.same_json(report,load('assignment-profile-checks.json')):raise ValueError('Fresh profile report differs')
 return report
def main():
 report=verify('--write' in b.sys.argv);print(json.dumps({k:report[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_correction_frame_count','rejected_correction_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

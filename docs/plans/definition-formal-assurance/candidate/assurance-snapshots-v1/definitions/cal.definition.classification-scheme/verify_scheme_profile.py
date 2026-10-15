"""Read-only candidate policy/upgrade examples and exact carrier boundary observations."""
import ast,copy,itertools,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def policy_record():
 return {'scheme_version':'sv1','axes':[{'axis_id':'kind','min':1,'max':1,'values':['human','machine']},{'axis_id':'posture','min':0,'max':2,'values':['supported','disputed']}],'assignments':[{'subject_revision':'subject@1','scheme_version':'sv1','axis_id':'kind','values':['machine']},{'subject_revision':'subject@1','scheme_version':'sv1','axis_id':'posture','values':['supported']}],'compatibility':[{'if_axis':'kind','if_value':'machine','then_axis':'posture','then_value':'supported'}]}
def profile_errors(rec):
 errors=[]
 if set(rec)!={'scheme_version','axes','assignments','compatibility'}:return ['closed-profile-fields']
 if not isinstance(rec['scheme_version'],str) or not rec['scheme_version']:return ['exact-scheme-version']
 axes={}
 for axis in rec['axes']:
  if set(axis)!={'axis_id','min','max','values'} or any(type(axis.get(n)) is not int for n in ['min','max']) or axis['min']<0 or axis['max']<axis['min']:errors.append('invalid-cardinality');continue
  if axis['axis_id'] in axes:errors.append('duplicate-axis')
  if not axis['values'] or len(set(axis['values']))!=len(axis['values']):errors.append('invalid-allowed-values')
  axes[axis['axis_id']]=axis
 subjects=set();selected={}
 for assignment in rec['assignments']:
  if set(assignment)!={'subject_revision','scheme_version','axis_id','values'}:errors.append('closed-assignment-fields');continue
  if not assignment['subject_revision']:errors.append('subject-revision-required')
  subject=assignment['subject_revision'];subjects.add(subject);axis=assignment['axis_id'];key=(subject,axis)
  if key in selected:errors.append('duplicate-subject-axis-record')
  selected[key]=assignment['values']
  if assignment['scheme_version']!=rec['scheme_version']:errors.append('wrong-scheme-version')
  if axis not in axes:errors.append('undeclared-axis');continue
  if len(set(assignment['values']))!=len(assignment['values']):errors.append('duplicate-selected-value')
  if any(val not in axes[axis]['values'] for val in assignment['values']):errors.append('unallowed-value')
 for subject,axis in itertools.product(sorted(subjects),sorted(axes)):
  n=len(selected.get((subject,axis),[]));bound=axes[axis]
  if not bound['min']<=n<=bound['max']:errors.append('cardinality-violation')
 for rule in rec['compatibility']:
  if set(rule)!={'if_axis','if_value','then_axis','then_value'}:errors.append('closed-compatibility-fields');continue
  if any(rule[end+'_axis'] not in axes or rule[end+'_value'] not in axes[rule[end+'_axis']]['values'] for end in ['if','then']):errors.append('unresolved-compatibility-reference');continue
  for subject in sorted(subjects):
   if rule['if_value'] in selected.get((subject,rule['if_axis']),[]) and rule['then_value'] not in selected.get((subject,rule['then_axis']),[]):errors.append('compatibility-violation')
 return sorted(set(errors))
def controls():
 out=[]
 def add(id,change,rejected=False):
  rec=policy_record();change(rec);errors=profile_errors(rec)
  if bool(errors)!=rejected:raise ValueError('Profile expectation mismatch '+id+str(errors))
  out.append({'case_id':id,'record':rec,'errors':errors,'expected_rejection':rejected,'actual_runtime_execution':False,'owner_policy_reviewed':False})
 add('required-single-and-optional-multiple-cardinality',lambda r:None)
 add('two-posture-values-allowed-by-local-cardinality',lambda r:r['assignments'][1]['values'].append('disputed'))
 def empty_optional(r):r['assignments'][0]['values']=['human'];r['assignments'][1]['values']=[]
 add('optional-axis-may-be-empty-with-no-triggered-rule',empty_optional)
 add('no-subjects-vacuous-profile-retains-existence-obligation',lambda r:r.update(assignments=[]))
 add('wrong-exact-scheme-version',lambda r:r['assignments'][0].update(scheme_version='sv2'),True)
 add('unresolved-axis-reference',lambda r:r['assignments'][0].update(axis_id='other'),True)
 add('value-not-allowed-under-axis',lambda r:r['assignments'][0].update(values=['supported']),True)
 add('required-axis-empty',lambda r:r['assignments'][0].update(values=[]),True)
 add('required-axis-absent',lambda r:r['assignments'].pop(0),True)
 add('single-axis-two-values',lambda r:r['assignments'][0].update(values=['human','machine']),True)
 add('duplicate-selected-value',lambda r:r['assignments'][1].update(values=['supported','supported']),True)
 add('trigger-without-compatible-value',lambda r:r['assignments'][1].update(values=['disputed']),True)
 add('unknown-compatibility-axis',lambda r:r['compatibility'][0].update(then_axis='other'),True)
 add('unknown-compatibility-value',lambda r:r['compatibility'][0].update(then_value='other'),True)
 add('bool-is-not-cardinality-integer',lambda r:r['axes'][0].update(min=True),True)
 add('negative-cardinality',lambda r:r['axes'][0].update(min=-1),True)
 add('inverted-cardinality',lambda r:r['axes'][0].update(min=2,max=1),True)
 add('duplicate-axis',lambda r:r['axes'].append(copy.deepcopy(r['axes'][0])),True)
 add('duplicate-allowed-value',lambda r:r['axes'][0]['values'].append('human'),True)
 add('no-allowed-values',lambda r:r['axes'][0].update(values=[]),True)
 add('subject-revision-missing',lambda r:r['assignments'][0].update(subject_revision=''),True)
 add('duplicate-subject-axis-record',lambda r:r['assignments'].append(copy.deepcopy(r['assignments'][0])),True)
 add('profile-authority-field-rejected',lambda r:r.update(authority=True),True)
 add('assignment-hidden-effect-rejected',lambda r:r['assignments'][0].update(runtime=True),True)
 add('compatibility-hidden-effect-rejected',lambda r:r['compatibility'][0].update(grant=True),True)
 return out
def trace():
 old={'assignment_id':'a-old','scheme_version':'sv1','axis_id':'kind','value_id':'machine','subject_revision':'subject@1','meaning_token':'machine@sv1'}
 return {'action':'introduce-version','new_version':'sv2','versions_before':['sv1'],'versions_after':['sv1','sv2'],'assignments_before':[old],'assignments_after':[copy.deepcopy(old)]}
def frame_errors(t):
 errors=[]
 if t['action']!='introduce-version':return ['unsupported-action-no-selected-frame']
 if t['new_version'] in t['versions_before'] or t['new_version'] not in t['versions_after']:errors.append('version-not-freshly-introduced')
 if not set(t['versions_before'])<=set(t['versions_after']):errors.append('older-version-deleted')
 ids=[x['assignment_id'] for x in t['assignments_after']]
 if len(ids)!=len(set(ids)):errors.append('duplicate-assignment-identity')
 after={x['assignment_id']:x for x in t['assignments_after']}
 for old in t['assignments_before']:
  if old['scheme_version'] not in t['versions_before']:errors.append('before-assignment-version-unresolved')
  if after.get(old['assignment_id'])!=old:errors.append('old-assignment-deleted-or-reinterpreted')
 return sorted(set(errors))
def traces():
 rows=[]
 def add(id,change,rejected=False):
  t=trace();change(t);errors=frame_errors(t)
  if bool(errors)!=rejected:raise ValueError('Trace expectation mismatch '+id)
  rows.append({'case_id':id,'trace':t,'errors':errors,'expected_rejection':rejected,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('fresh-version-retains-old-record',lambda t:None)
 def migrate(t):
  successor=copy.deepcopy(t['assignments_before'][0]);successor.update(assignment_id='a-successor',scheme_version='sv2',subject_revision='subject@2',meaning_token='machine@sv2');t['assignments_after'].append(successor)
 add('separate-successor-migration-retains-old-record',migrate)
 for key,value in [('scheme_version','sv2'),('axis_id','effect'),('value_id','human'),('subject_revision','subject@2'),('meaning_token','changed')]:add('silently-changed-'+key,lambda t,key=key,value=value:t['assignments_after'][0].update({key:value}),True)
 add('old-record-deleted',lambda t:t.update(assignments_after=[]),True)
 add('old-version-deleted',lambda t:t.update(versions_after=['sv2']),True)
 add('same-version-not-new',lambda t:t.update(new_version='sv1'),True)
 add('new-version-not-present-after',lambda t:t.update(versions_after=['sv1']),True)
 add('duplicate-assignment-identity',lambda t:t['assignments_after'].append(copy.deepcopy(t['assignments_after'][0])),True)
 add('correction-is-separately-scoped-action',lambda t:t.update(action='correct-assignment'),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings()
 root=b.ROOT/'authority/artifact-types/classification-scheme/v1'
 paths={'descriptor':root/'artifact.json','schema':root/'schema.json','fixture':root/'fixtures/valid/record.json','artifact_projection':root/'ARTIFACT.md','fixture_projection':root/'fixtures/valid/RECORD.md','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','relation_model':b.ROOT/'authority/relation-kinds/candidates/0005-definition-complete-extension/model.json','generator':b.ROOT/'tooling/generators/endpoint_carrier.py','validator':b.ROOT/'tooling/validators/definition_complete_carrier.py','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','definition_registry':b.ROOT/'authority/definitions/registry.json','review':b.ROOT/'.arcanum/ontology-vault/2026-10-05-classification-model-review.md'}
 for p in sorted((root/'fixtures/invalid').glob('*.json')):paths['negative_'+p.stem]=p
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:b.r.read_bytes(b.ROOT,x['path']) for n,x in refs.items()};artifact=json.loads(raw['descriptor']);schema=json.loads(raw['schema']);fixture=json.loads(raw['fixture']);model=json.loads(raw['relation_model']);reg=json.loads(raw['type_registry']);definitionreg=json.loads(raw['definition_registry']);source=load('t.json')['payload']['source'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema)
 # Execute only the pure roles_for AST; canonical validate_package writes receipts and is never called.
 tree=ast.parse(raw['validator']);role_function=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='roles_for');env={};exec(compile(ast.Module(body=[role_function],type_ignores=[]),str(paths['validator']),'exec'),env);roles=env['roles_for']('classification-scheme',model);allowed={(x['relation_kind_ref'],x['direction'],kind) for x in roles for kind in x['counterpart_kinds']}
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
 ck('four-explicit-noncollapse-contracts',len(artifact['orthogonality_rules'])==4 and set(artifact['hostile_non_collapse'])=={'schema','classification-assignment'})
 ck('whole-file-review-source-sha-exact',refs['review']['sha256']=='2f8147089d6b245d5696d132c3bf49f757bdd43cebe03ff032d92202946c7439')
 probes=[]
 def probe(id,change,accept=True):
  rec=copy.deepcopy(fixture);change(rec);errors=list(validator.iter_errors(rec));accepted=not errors
  if accepted!=accept:raise ValueError('Unexpected actual schema boundary '+id)
  probes.append({'case_id':id,'schema_accepted':accepted,'record':rec,'errors':[x.message for x in errors],'whole_source_conformance_established':False,'actual_runtime_execution':False})
 probe('empty-axis-value-cardinality-compatibility-lists',lambda r:r['payload'].update(axis_refs=[],value_refs=[],cardinality_rules=[],compatibility_rules=[]))
 probe('unresolved-axis-and-value-references',lambda r:r['payload'].update(axis_refs=['axis:unresolved'],value_refs=['value:unresolved']))
 probe('arbitrary-cardinality-rule-string',lambda r:r['payload'].update(cardinality_rules=['this-is-not-an-interpreted-cardinality-rule']))
 probe('arbitrary-compatibility-rule-string',lambda r:r['payload'].update(compatibility_rules=['grant-authority']))
 probe('cross-product-role-combination-schema-accepts',lambda r:r.update(relation_refs=[{'relation_kind_ref':'relation.challenges','direction':'source','counterpart_kind':'classification-value','counterpart_ref':'value:example'}]))
 probe('duplicate-mapping-references-schema-accepts',lambda r:r['payload'].update(mapping_refs=['map:x','map:x']))
 probe('instance-version-extra-payload-field-closed',lambda r:r['payload'].update(scheme_version_ref='scheme:x@2'),False)
 probe('authority-effect-field-rejected',lambda r:r.update(authority_effect='granted'),False)
 bad=probes[4]['record']['relation_refs'][0];ck('cross-product-schema-probe-outside-exact-role-surface',(bad['relation_kind_ref'],bad['direction'],bad['counterpart_kind']) not in allowed)
 ck('format-discriminator-not-instance-version',schema['properties']['schema_version']['const']=='cyberalchemy-lab-classification-scheme/v1' and 'scheme_version_ref' not in schema['properties']['payload']['properties'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();frames=traces();bindings=[b.ref(p) for p in [b.UNIT/'verify_scheme_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'verifier.py',b.IMPL/'contracts.py']]
 b.unchanged(context['sources']+list(refs.values())+bindings);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-classification-scheme-profile/v1-candidate','status':'PASS-for-exact-candidate-policy-frames-and-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_introduction_count':len(frames),'rejected_introductions':sum(x['expected_rejection'] for x in frames),'finite_introductions':frames,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'negative_fixture_checks':negative,'actual_roles':roles,'source_mapping_gaps':{'mapping_reviewed':False,'exact_instance_version_resolution_established':False,'policy_strings_are_not_executable_rules':True,'old_assignment_meaning_frame_is_not_runtime_proof':True,'whole_file_review_precedence_pending':True,'schema_cross_product_is_not_exact_roles':True,'world_truth_and_consumer_no_inference_compliance_established':False},'new_scheme_versions_or_assignments_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Candidate bounded policy records/introduction frames and selected current carrier bytes/fixtures/renderers. No reviewed policy denotation, whole source conformity, immutable assignment implementation, exact instance-version resolver, owner fidelity, actual upgrade, world truth or unbounded trace proof.'}
 if write:b.put('scheme-profile-checks.json',report)
 elif not b.r.same_json(report,load('scheme-profile-checks.json')):raise ValueError('Fresh profile report differs')
 return report
def main():
 report=verify('--write' in b.sys.argv);print(json.dumps({k:report[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_introduction_count','rejected_introductions','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

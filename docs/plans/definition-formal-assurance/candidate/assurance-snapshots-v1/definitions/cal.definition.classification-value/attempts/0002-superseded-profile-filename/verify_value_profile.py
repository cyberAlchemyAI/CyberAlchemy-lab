"""Candidate scoped-value/mapping/label frames plus selected actual carrier observations."""
import ast,copy,itertools,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def record():
 return {'versions':['sv1','sv2'],'axes':[{'axis_id':'result','scheme_version':'sv1'},{'axis_id':'evidence','scheme_version':'sv1'},{'axis_id':'result','scheme_version':'sv2'}],'definitions':['def:result@1','def:evidence@1'],'values':[{'value_id':'v1','axis_id':'result','scheme_version':'sv1','label':'failed','meaning_token':'result-failed@1','definition_ref':'def:result@1','parent_refs':[]},{'value_id':'v2','axis_id':'evidence','scheme_version':'sv1','label':'failed','meaning_token':'evidence-failed@1','definition_ref':'def:evidence@1','parent_refs':[]},{'value_id':'v3','axis_id':'result','scheme_version':'sv2','label':'failed','meaning_token':'result-failed@2','definition_ref':'def:result@1','parent_refs':[]}],'mappings':[{'source':'v1','target':'v3','kind':'compatible','claim':'candidate-scoped-compatibility','effect':'none'}],'label_only_merges':[],'hierarchy_policy':'acyclic-selected-profile'}
def profile_errors(rec):
 errors=[]
 if set(rec)!={'versions','axes','definitions','values','mappings','label_only_merges','hierarchy_policy'}:return ['closed-profile-fields']
 if len(set(rec['versions']))!=len(rec['versions']):errors.append('duplicate-version-identity')
 axes=[]
 for a in rec['axes']:
  if set(a)!={'axis_id','scheme_version'}:errors.append('closed-axis-fields');continue
  if a['scheme_version'] not in rec['versions']:errors.append('axis-version-unresolved')
  axes.append((a['axis_id'],a['scheme_version']))
 if len(set(axes))!=len(axes):errors.append('duplicate-exact-axis-binding')
 values={}
 for val in rec['values']:
  if set(val)!={'value_id','axis_id','scheme_version','label','meaning_token','definition_ref','parent_refs'}:errors.append('closed-value-fields');continue
  if any(not isinstance(val[n],str) or not val[n] for n in ['value_id','axis_id','scheme_version','label','meaning_token','definition_ref']):errors.append('missing-exact-value-field')
  if val['value_id'] in values:errors.append('duplicate-value-identity')
  values[val['value_id']]=val
  if (val['axis_id'],val['scheme_version']) not in axes:errors.append('unresolved-exact-axis-version')
  if val['definition_ref'] not in rec['definitions']:errors.append('unresolved-exact-definition')
  if len(set(val['parent_refs']))!=len(val['parent_refs']):errors.append('duplicate-parent-reference')
 for val in values.values():
  for parent in val['parent_refs']:
   if parent not in values:errors.append('unresolved-parent');continue
   target=values[parent]
   if (val['axis_id'],val['scheme_version'])!=(target['axis_id'],target['scheme_version']):errors.append('parent-outside-selected-axis-version')
 if rec['hierarchy_policy']=='acyclic-selected-profile':
  def cyclic(id,stack):
   if id in stack:return True
   return any(cyclic(p,stack|{id}) for p in values[id]['parent_refs'] if p in values)
  if any(cyclic(id,set()) for id in sorted(values)):errors.append('selected-hierarchy-cycle')
 else:errors.append('unsupported-hierarchy-policy')
 for mapping in rec['mappings']:
  if set(mapping)!={'source','target','kind','claim','effect'}:errors.append('closed-mapping-fields');continue
  if mapping['source'] not in values or mapping['target'] not in values:errors.append('mapping-endpoint-unresolved')
  if mapping['kind'] not in ['compatible','equivalent','broader','narrower'] or not mapping['claim']:errors.append('mapping-claim-required')
  if mapping['effect']!='none':errors.append('mapping-is-not-authority')
 for pair in rec['label_only_merges']:
  if set(pair)!={'source','target'} or pair['source'] not in values or pair['target'] not in values:errors.append('label-merge-endpoint-unresolved');continue
  left=values[pair['source']];right=values[pair['target']]
  if left['label']==right['label'] and any(left[n]!=right[n] for n in ['value_id','axis_id','scheme_version','meaning_token']):errors.append('label-alone-cannot-coalesce-scoped-meaning')
 return sorted(set(errors))
def controls():
 out=[]
 def add(id,change,rejected=False):
  rec=record();change(rec);errors=profile_errors(rec)
  if bool(errors)!=rejected:raise ValueError('Profile expectation mismatch '+id+str(errors))
  out.append({'case_id':id,'record':rec,'errors':errors,'expected_rejection':rejected,'actual_runtime_execution':False,'owner_mapping_reviewed':False})
 add('equal-labels-distinct-axes-versions-identities-and-meanings',lambda r:None)
 add('display-text-can-change-with-stable-scoped-identity',lambda r:r['values'][0].update(label='failure'))
 add('identity-may-lexically-match-label-without-collapse-rule',lambda r:r['values'][0].update(label='v1'))
 add('no-parents-or-mappings-required-for-flat-values',lambda r:r.update(mappings=[]))
 add('explicit-reverse-mapping-is-separate-directed-record',lambda r:r['mappings'].append({'source':'v3','target':'v1','kind':'compatible','claim':'candidate-reverse','effect':'none'}))
 def hierarchy(r):
  other=copy.deepcopy(r['values'][0]);other.update(value_id='broader',label='negative-outcome',meaning_token='negative@1');r['values'].append(other);r['values'][0]['parent_refs']=['broader']
 add('optional-same-version-hierarchy-with-exact-parent',hierarchy)
 add('different-version-label-only-coalescence-rejected',lambda r:r['label_only_merges'].append({'source':'v1','target':'v3'}),True)
 add('different-axis-label-only-coalescence-rejected',lambda r:r['label_only_merges'].append({'source':'v1','target':'v2'}),True)
 add('unresolved-axis',lambda r:r['values'][0].update(axis_id='unresolved'),True)
 add('unresolved-version',lambda r:r['values'][0].update(scheme_version='sv0'),True)
 add('axis-known-in-other-version-not-exact-match',lambda r:r['values'][1].update(scheme_version='sv2'),True)
 add('unresolved-definition',lambda r:r['values'][0].update(definition_ref='def:unknown@1'),True)
 add('missing-stable-value-identity',lambda r:r['values'][0].update(value_id=''),True)
 add('missing-meaning-token',lambda r:r['values'][0].update(meaning_token=''),True)
 add('missing-display-label',lambda r:r['values'][0].update(label=''),True)
 add('duplicate-value-identity',lambda r:r['values'].append(copy.deepcopy(r['values'][0])),True)
 add('duplicate-version-identity',lambda r:r['versions'].append('sv1'),True)
 add('duplicate-exact-axis-binding',lambda r:r['axes'].append(copy.deepcopy(r['axes'][0])),True)
 add('axis-version-not-resolved',lambda r:r['axes'][0].update(scheme_version='sv0'),True)
 add('unknown-parent',lambda r:r['values'][0].update(parent_refs=['missing']),True)
 add('cross-axis-parent-not-selected-hierarchy',lambda r:r['values'][0].update(parent_refs=['v2']),True)
 add('cross-version-parent-requires-separate-mapping',lambda r:r['values'][0].update(parent_refs=['v3']),True)
 add('self-parent-cycle-rejected-in-selected-profile',lambda r:r['values'][0].update(parent_refs=['v1']),True)
 add('duplicate-parent-reference',lambda r:r['values'][0].update(parent_refs=['v1','v1']),True)
 add('unknown-mapping-source',lambda r:r['mappings'][0].update(source='missing'),True)
 add('unknown-mapping-target',lambda r:r['mappings'][0].update(target='missing'),True)
 add('mapping-authority-not-allowed',lambda r:r['mappings'][0].update(effect='granted'),True)
 add('mapping-with-no-specific-claim',lambda r:r['mappings'][0].update(claim=''),True)
 add('unsupported-mapping-kind',lambda r:r['mappings'][0].update(kind='membership'),True)
 add('hidden-value-authority-field',lambda r:r['values'][0].update(authority=True),True)
 add('hidden-mapping-runtime-field',lambda r:r['mappings'][0].update(runtime=True),True)
 add('hidden-profile-effect',lambda r:r.update(effect='granted'),True)
 return out
def frame():
 old={'value_id':'v1','axis_id':'result','scheme_version':'sv1','identity_token':'id1','label':'failed','meaning_token':'result-failed@1','definition_ref':'def:result@1'};new=copy.deepcopy(old);new['label']='failure'
 return {'action':'label-only-change','before':old,'after':new}
def frame_errors(rec):
 if rec['action']!='label-only-change':return ['unsupported-action-no-selected-frame']
 errors=[]
 if rec['before'] is None or rec['after'] is None:return ['value-absent']
 for n in ['value_id','axis_id','scheme_version','identity_token','meaning_token','definition_ref']:
  if rec['before'][n]!=rec['after'][n]:errors.append('changed-'+n)
 return errors
def frames():
 rows=[]
 def add(id,change,rejected=False):
  rec=frame();change(rec);errors=frame_errors(rec)
  if bool(errors)!=rejected:raise ValueError('Frame expectation mismatch '+id)
  rows.append({'case_id':id,'frame':rec,'errors':errors,'expected_rejection':rejected,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('pure-label-change-preserves-exact-identity-binding-meaning',lambda r:None)
 add('display-noop-permitted-but-not-a-variation-witness',lambda r:r['after'].update(label='failed'))
 for n,value in [('value_id','v2'),('axis_id','evidence'),('scheme_version','sv2'),('identity_token','id2'),('meaning_token','changed'),('definition_ref','def:result@2')]:add('claimed-label-update-changes-'+n,lambda r,n=n,value=value:r['after'].update({n:value}),True)
 add('deleted-output-value',lambda r:r.update(after=None),True)
 add('absent-input-value',lambda r:r.update(before=None),True)
 add('successor-redefinition-is-a-separate-operation',lambda r:r.update(action='successor-redefinition'),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings()
 root=b.ROOT/'authority/artifact-types/classification-value/v1'
 paths={'descriptor':root/'artifact.json','schema':root/'schema.json','fixture':root/'fixtures/valid/record.json','artifact_projection':root/'ARTIFACT.md','fixture_projection':root/'fixtures/valid/RECORD.md','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','relation_model':b.ROOT/'authority/relation-kinds/candidates/0005-definition-complete-extension/model.json','generator':b.ROOT/'tooling/generators/endpoint_carrier.py','validator':b.ROOT/'tooling/validators/definition_complete_carrier.py','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','definition_registry':b.ROOT/'authority/definitions/registry.json','review':b.ROOT/'.arcanum/ontology-vault/2026-10-05-classification-model-review.md'}
 for p in sorted((root/'fixtures/invalid').glob('*.json')):paths['negative_'+p.stem]=p
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:b.r.read_bytes(b.ROOT,x['path']) for n,x in refs.items()};artifact=json.loads(raw['descriptor']);schema=json.loads(raw['schema']);fixture=json.loads(raw['fixture']);model=json.loads(raw['relation_model']);reg=json.loads(raw['type_registry']);definitionreg=json.loads(raw['definition_registry']);source=load('t.json')['payload']['source'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema)
 # Execute only the pure roles_for AST; canonical validate_package writes receipts and is never called.
 tree=ast.parse(raw['validator']);role_function=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='roles_for');env={};exec(compile(ast.Module(body=[role_function],type_ignores=[]),str(paths['validator']),'exec'),env);roles=env['roles_for']('classification-value',model);allowed={(x['relation_kind_ref'],x['direction'],kind) for x in roles for kind in x['counterpart_kinds']}
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
 ck('four-explicit-noncollapse-contracts',len(artifact['orthogonality_rules'])==4 and set(artifact['hostile_non_collapse'])=={'definition','classification-assignment'})
 ck('whole-file-review-source-sha-exact',refs['review']['sha256']=='2f8147089d6b245d5696d132c3bf49f757bdd43cebe03ff032d92202946c7439')
 probes=[]
 def probe(id,change,accept=True):
  rec=copy.deepcopy(fixture);change(rec);errors=list(validator.iter_errors(rec));accepted=not errors
  if accepted!=accept:raise ValueError('Unexpected actual schema boundary '+id)
  probes.append({'case_id':id,'schema_accepted':accepted,'record':rec,'errors':[x.message for x in errors],'whole_source_conformance_established':False,'actual_runtime_execution':False})
 probe('unresolved-axis-reference',lambda r:r['payload'].update(axis_ref='axis:unresolved'))
 probe('unversioned-scheme-name-string',lambda r:r['payload'].update(scheme_ref='scheme-name'))
 probe('unresolved-answer-definition',lambda r:r['payload'].update(definition_ref='cal.definition.missing@0'))
 probe('self-parent-shape-accepted',lambda r:r['payload'].update(parent_value_refs=[r['node_id']]))
 probe('duplicate-parent-references-shape-accepted',lambda r:r['payload'].update(parent_value_refs=['value:x','value:x']))
 probe('unresolved-compatibility-rule-reference',lambda r:r['payload'].update(compatibility_refs=['rule:unresolved']))
 probe('role-cross-product-shape-accepts-invalid-tuple',lambda r:r.update(relation_refs=[{'relation_kind_ref':'relation.member-of','direction':'target','counterpart_kind':'challenge-event','counterpart_ref':'event:x'}]))
 probe('meaning-token-extra-payload-field-closed',lambda r:r['payload'].update(meaning_token='meaning:x'),False)
 probe('empty-axis-reference-rejected',lambda r:r['payload'].update(axis_ref=''),False)
 probe('authority-effect-rejected',lambda r:r.update(authority_effect='granted'),False)
 bad=probes[6]['record']['relation_refs'][0];ck('role-cross-product-probe-outside-exact-role-surface',(bad['relation_kind_ref'],bad['direction'],bad['counterpart_kind']) not in allowed)
 ck('format-discriminator-not-instance-scheme-version',schema['properties']['schema_version']['const']=='cyberalchemy-lab-classification-value/v1' and 'scheme_version_ref' not in schema['properties']['payload']['properties'])
 sibling_paths={'scheme_fixture':b.ROOT/'authority/artifact-types/classification-scheme/v1/fixtures/valid/record.json','assignment_fixture':b.ROOT/'authority/artifact-types/classification-assignment/v1/fixtures/valid/record.json'}
 siblings={n:b.ref(p) for n,p in sibling_paths.items()};scheme=json.loads(sibling_paths['scheme_fixture'].read_bytes());assignment=json.loads(sibling_paths['assignment_fixture'].read_bytes())
 join={'value-axis-in-selected-scheme-axes':fixture['payload']['axis_ref'] in scheme['payload']['axis_refs'],'value-exact-scheme-literal-is-selected-scheme-identity':fixture['payload']['scheme_ref']==scheme['node_id'],'value-identity-in-selected-scheme-value-list':fixture['node_id'] in scheme['payload']['value_refs'],'assignment-value-literal-is-selected-value-identity':assignment['payload']['value_ref']==fixture['node_id'],'assignment-value-literal-in-selected-scheme-value-list':assignment['payload']['value_ref'] in scheme['payload']['value_refs'],'assignment-axis-agrees-with-selected-value-axis':assignment['payload']['axis_ref']==fixture['payload']['axis_ref'],'assignment-scheme-literal-agrees-with-selected-value-scheme':assignment['payload']['scheme_version_ref']==fixture['payload']['scheme_ref']}
 answer_ref=fixture['payload']['definition_ref'];answer_rows=[x for x in definitionreg['entries'] if x['definition_id']+'@'+x['version']==answer_ref]
 ck('fixture-answer-definition-reference-current-admitted',len(answer_rows)==1 and answer_rows[0]['lifecycle_state']=='admitted' and definitionreg['current_lookup'][answer_rows[0]['definition_id']]==answer_ref)
 if len(answer_rows)==1:
  answer=answer_rows[0];selected_answer={k:answer[k] for k in ['definition_id','path','sha256']};refs['fixture_answer_definition']={k:answer[k] for k in ['path','sha256']};b.unchanged([refs['fixture_answer_definition']])
 ck('selected-fixtures-literal-join-observations-retained',join=={'value-axis-in-selected-scheme-axes':True,'value-exact-scheme-literal-is-selected-scheme-identity':False,'value-identity-in-selected-scheme-value-list':False,'assignment-value-literal-is-selected-value-identity':False,'assignment-value-literal-in-selected-scheme-value-list':True,'assignment-axis-agrees-with-selected-value-axis':True,'assignment-scheme-literal-agrees-with-selected-value-scheme':True})
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();display_frames=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_value_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'verifier.py',b.IMPL/'contracts.py']]
 b.unchanged(context['sources']+list(refs.values())+list(siblings.values())+bindings);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-classification-value-profile/v1-candidate','status':'PASS-for-exact-candidate-value-bindings-maps-display-frames-and-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'sibling_source_inputs':siblings,'actual_join_observations':join,'selected_answer_definition':selected_answer,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_display_frame_count':len(display_frames),'rejected_display_frames':sum(x['expected_rejection'] for x in display_frames),'finite_display_frames':display_frames,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'negative_fixture_checks':negative,'actual_roles':roles,'source_mapping_gaps':{'mapping_reviewed':False,'exact_axis_and_scheme_version_resolution_established':False,'label_is_not_identity_key':True,'answer_definition_admission_is_not_value_meaning_approval':True,'display_frame_is_not_runtime_proof':True,'hierarchy_mapping_and_review_precedence_pending':True,'whole_source_conformance_established':False},'new_values_mappings_or_assignments_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Candidate bounded value/mapping records/display frames and selected current carrier bytes/fixtures/renderers. No reviewed policy denotation, whole source conformity, stable value/runtime preservation implementation, exact axis/version resolver, owner fidelity, actual upgrade, world truth or unbounded trace proof.'}
 if write:b.put('scheme-profile-checks.json',report)
 elif not b.r.same_json(report,load('scheme-profile-checks.json')):raise ValueError('Fresh profile report differs')
 return report
def main():
 report=verify('--write' in b.sys.argv);print(json.dumps({k:report[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_display_frame_count','rejected_display_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

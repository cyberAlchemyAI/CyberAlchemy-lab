"""Bounded candidate composition/projection profiles and actual current/historical carriers."""
import copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base():
 return {'episode_id':'episode:1','subject_revision':'subject@1','scheme_version':'sv1','act':{'id':'act:1','subject_revision':'subject@1','scheme_version':'sv1','producer_action':'action:1','result_ref':'result:1'},'result':{'id':'result:1','subject_revision':'subject@1','scheme_version':'sv1','assignment_refs':['a1','a2','a3']},'axes':[{'id':'kind','question_ref':'question:kind'},{'id':'posture','question_ref':'question:posture'}],'values':[{'id':'v1','version_ref':'v1@1','axis':'kind','scheme_version':'sv1','semantic_class':True},{'id':'v2','version_ref':'v2@1','axis':'posture','scheme_version':'sv1','semantic_class':False},{'id':'v3','version_ref':'v3@1','axis':'kind','scheme_version':'sv1','semantic_class':True}],'assignments':[{'id':'a1','subject_revision':'subject@1','scheme_version':'sv1','axis':'kind','value':'v1'},{'id':'a2','subject_revision':'subject@1','scheme_version':'sv1','axis':'posture','value':'v2'},{'id':'a3','subject_revision':'subject@1','scheme_version':'sv1','axis':'kind','value':'v3'}],'cardinality':{'kind':{'min':1,'max':2},'posture':{'min':0,'max':1}},'classification_only_conclusions':[],'independently_supported_outcomes':[],'projections':[{'assignment_ref':'a1','kind':'relation.instance-of','source_revision':'subject@1','target_version':'v1@1','qualifiers':{'classification_assignment_ref':'a1','scheme_version_ref':'sv1','axis_ref':'kind','class_or_parent_version_ref':'v1@1'}}]}
def errors(r):
 out=[]
 def check(ok,msg):
  if not ok:out.append(msg)
 fields=set(base())
 check(set(r)==fields,'candidate composition fields closed')
 check(bool(r['episode_id']) and bool(r['subject_revision']) and bool(r['scheme_version']),'exact episode/subject/Scheme tokens required')
 act=r['act'];result=r['result'];check(bool(act['id']) and bool(result['id']) and bool(act['producer_action']),'recorded act/result/producer required')
 for rec in [act,result]:check(rec['subject_revision']==r['subject_revision'] and rec['scheme_version']==r['scheme_version'],'act/result exact subject revision and Scheme agree')
 check(act['result_ref']==result['id'],'recorded producer/result link exact')
 axes={x['id']:x for x in r['axes']};values={x['id']:x for x in r['values']};assignments={x['id']:x for x in r['assignments']}
 check(len(axes)==len(r['axes']) and len(values)==len(r['values']) and len(assignments)==len(r['assignments']),'candidate identity keys unique within selected role')
 check(all(x['id'] and x['question_ref'] for x in r['axes']) and len({x['question_ref'] for x in r['axes']})==len(axes),'independent named questions need distinct candidate IDs')
 check(bool(result['assignment_refs']) and len(set(result['assignment_refs']))==len(result['assignment_refs']),'nonempty nonduplicated result assignment references')
 counts={axis:0 for axis in axes}
 for id in result['assignment_refs']:
  a=assignments.get(id)
  if a is None:out.append('unresolved result assignment');continue
  check(a['subject_revision']==r['subject_revision'] and a['scheme_version']==r['scheme_version'],'result assignments one exact subject revision/Scheme')
  check(a['axis'] in axes,'declared axis required');value=values.get(a['value'])
  check(value is not None,'declared value required')
  if value:check(value['axis']==a['axis'] and value['scheme_version']==r['scheme_version'],'value exact axis/Scheme agreement')
  if a['axis'] in counts:counts[a['axis']]+=1
 check(set(r['cardinality'])==set(axes),'selected cardinality policies bind all candidate axes')
 for axis,p in r['cardinality'].items():
  check(type(p['min']) is int and type(p['max']) is int and 0<=p['min']<=p['max'],'finite selected cardinality policy well formed')
  check(p['min']<=counts.get(axis,0)<=p['max'],'assignment count follows selected Scheme policy')
 check(not r['classification_only_conclusions'],'classification alone authorizes no selected boundary conclusion')
 check(set(r['independently_supported_outcomes'])<=set(b.OUTCOMES),'independent outcome labels within selected bounded profile')
 for p in r['projections']:
  a=assignments.get(p['assignment_ref']);check(a is not None and p['assignment_ref'] in result['assignment_refs'],'projection bound to included canonical Assignment')
  if a is None:continue
  value=values.get(a['value'])
  if value is None:continue
  check(value['semantic_class'] is True,'only selected semantic class values projected; no general enum-edge rule')
  check(p['kind']=='relation.instance-of' and p['source_revision']==a['subject_revision'] and p['target_version']==value['version_ref'],'projection kind and direction exact')
  check(p['qualifiers']=={'classification_assignment_ref':a['id'],'scheme_version_ref':a['scheme_version'],'axis_ref':a['axis'],'class_or_parent_version_ref':value['version_ref']},'candidate proposed four qualifiers exact; not current Kind admission')
 return out
def controls():
 rows=[]
 def add(id,change,bad=False):
  r=base();change(r);es=errors(r)
  if bool(es)!=bad:raise ValueError('Wrong selected composition profile '+id+' '+str(es))
  rows.append({'case_id':id,'record':r,'errors':es,'expected_rejection':bad,'actual_runtime_execution':False,'owner_policy_reviewed':False})
 add('two-questions-multi-value-axis-semantic-class-projection',lambda r:None)
 add('no-graph-projection-required-for-local-classification',lambda r:r.update(projections=[]))
 add('independent-world-outcomes-not-forbidden',lambda r:r.update(independently_supported_outcomes=b.OUTCOMES))
 def single(r):r['result']['assignment_refs']=['a1'];r['cardinality']['kind']['max']=1
 add('one-answer-optional-second-axis-no-universal-two-axis-rule',single)
 add('mixed-assignment-subject-revision',lambda r:r['assignments'][1].update(subject_revision='subject@2'),True)
 add('mixed-assignment-scheme',lambda r:r['assignments'][1].update(scheme_version='sv2'),True)
 add('wrong-act-subject',lambda r:r['act'].update(subject_revision='other@1'),True)
 add('wrong-result-scheme',lambda r:r['result'].update(scheme_version='sv2'),True)
 add('unlinked-result',lambda r:r['act'].update(result_ref='result:other'),True)
 add('missing-recorded-producer',lambda r:r['act'].update(producer_action=''),True)
 add('empty-result',lambda r:r['result'].update(assignment_refs=[]),True)
 add('unresolved-assignment',lambda r:r['result']['assignment_refs'].append('absent'),True)
 add('duplicate-result-assignment',lambda r:r['result']['assignment_refs'].append('a1'),True)
 add('undeclared-axis',lambda r:r['assignments'][0].update(axis='absent'),True)
 add('wrong-value-axis',lambda r:r['values'][1].update(axis='kind'),True)
 add('wrong-value-scheme',lambda r:r['values'][1].update(scheme_version='sv2'),True)
 add('undeclared-value',lambda r:r['assignments'][0].update(value='absent'),True)
 add('collapsed-question-identities',lambda r:r['axes'][1].update(question_ref='question:kind'),True)
 add('missing-question-identity',lambda r:r['axes'][1].update(question_ref=''),True)
 add('multi-value-exceeds-selected-single-cardinality',lambda r:r['cardinality']['kind'].update(max=1),True)
 add('optional-axis-made-required-without-answer',lambda r:(r['result'].update(assignment_refs=['a1','a3']),r['cardinality']['posture'].update(min=1)),True)
 add('malformed-cardinality-interval',lambda r:r['cardinality']['kind'].update(min=3),True)
 for outcome in b.SOURCE_OUTCOMES:add('classification-only-'+outcome,lambda r,outcome=outcome:r.update(classification_only_conclusions=[outcome]),True)
 add('enum-posture-is-not-semantic-class-projection',lambda r:r['values'][0].update(semantic_class=False),True)
 add('unbound-projection',lambda r:r['projections'][0].update(assignment_ref='absent'),True)
 add('projection-wrong-source-revision',lambda r:r['projections'][0].update(source_revision='subject@2'),True)
 add('projection-wrong-target-version',lambda r:r['projections'][0].update(target_version='v1@2'),True)
 add('projection-not-selected-kind',lambda r:r['projections'][0].update(kind='relation.realizes'),True)
 for key in ['classification_assignment_ref','scheme_version_ref','axis_ref','class_or_parent_version_ref']:add('proposal-qualifier-'+key+'-mismatch',lambda r,key=key:r['projections'][0]['qualifiers'].__setitem__(key,'other'),True)
 add('projection-has-extra-qualifier',lambda r:r['projections'][0]['qualifiers'].update(extra='other'),True)
 add('runtime-field-not-in-candidate-composition',lambda r:r.update(runtime=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings()
 paths={'type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json','review':b.ROOT/'.arcanum/ontology-vault/2026-10-05-classification-model-review.md'}
 type_reg=json.loads(paths['type_registry'].read_bytes());kind_reg=json.loads(paths['kind_registry'].read_bytes())
 kinds=['classification-scheme','classification-value','classification-assignment','typed-relation'];entries={kind:next(x for x in type_reg['admitted_contracts'] if x['semantic_kind']==kind and x['lifecycle_state']=='admitted-current') for kind in kinds}
 for kind,row in entries.items():
  paths[kind+'_descriptor']=b.ROOT/row['artifact_path'];paths[kind+'_schema']=b.ROOT/row['schema_path'];paths[kind+'_fixture']=paths[kind+'_descriptor'].parent/'fixtures/valid/record.json'
 historical=next(x for x in type_reg['admitted_contracts'] if x['artifact_type_ref']=='cal.artifact-type.typed-relation/v2');paths['historical_schema']=b.ROOT/historical['schema_path'];paths['historical_descriptor']=b.ROOT/historical['artifact_path'];paths['historical_fixture']=paths['historical_descriptor'].parent/'fixtures/valid/record.json'
 selected_kind=next(x for x in kind_reg['entries'] if x['relation_kind_ref']=='relation.instance-of');paths['instance_of']=b.ROOT/selected_kind['instance_path']
 for p in sorted(paths['typed-relation_descriptor'].parent.glob('fixtures/invalid/*.json')):paths['negative_'+p.stem]=p
 refs={n:b.ref(p) for n,p in paths.items()};docs={n:json.loads(p.read_bytes()) for n,p in paths.items() if p.suffix=='.json'};checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 ck('143-selected-contracts-no-dedicated-Classification-carrier',len(type_reg['admitted_contracts'])==143 and not any(x['semantic_kind']=='classification' for x in type_reg['admitted_contracts']) and not (b.ROOT/'authority/artifact-types/classification/v1').exists())
 validators={}
 for kind,row in entries.items():
  a=docs[kind+'_descriptor'];s=docs[kind+'_schema'];b.c.Draft202012Validator.check_schema(s);validators[kind]=b.c.Draft202012Validator(s)
  ck(kind+'-current-overlay-exact',row['artifact_sha256']==refs[kind+'_descriptor']['sha256'] and row['schema_sha256']==refs[kind+'_schema']['sha256'] and a['schema_digest']==refs[kind+'_schema']['sha256'])
  ck(kind+'-selected-fixture-shape-valid',not list(validators[kind].iter_errors(docs[kind+'_fixture'])))
 ck('current-Typed-Relation-v3-separate-historical-v2',entries['typed-relation']['artifact_type_ref']=='cal.artifact-type.typed-relation/v3' and entries['typed-relation']['admission_decision_ref']=='CAL-DECISION-0074A-GOVERNANCE-CARRIER-ADMISSION' and historical['lifecycle_state']=='admitted-historical' and historical['schema_sha256']==refs['historical_schema']['sha256'] and historical['artifact_sha256']==refs['historical_descriptor']['sha256'])
 historical_validator=b.c.Draft202012Validator(docs['historical_schema']);ck('historical-v2-selected-fixture-valid',not list(historical_validator.iter_errors(docs['historical_fixture'])))
 kp=docs['instance_of']['payload'];pairs=kp['allowed_endpoint_pairs'];qual=kp['qualifier_contract'];proposed=['classification_assignment_ref','scheme_version_ref','axis_ref','class_or_parent_version_ref']
 ck('current-instance-of-exact-12-ordered-pairs',selected_kind['instance_sha256']==refs['instance_of']['sha256'] and selected_kind['lifecycle_state']=='admitted-current' and selected_kind['exact_endpoint_pair_count']==len(pairs)==12 and selected_kind['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('current-two-qualifiers-not-four-proposed-qualifiers',selected_kind['required_qualifier_axes']==qual['required_axes']==['parent_version_ref','binding_ref'] and qual['closed'] is True and set(qual['properties'])==set(qual['required_axes']) and all(x in paths['review'].read_text() for x in proposed))
 ck('whole-file-review-bound-at-candidate-ceiling',refs['review']['sha256']=='2f8147089d6b245d5696d132c3bf49f757bdd43cebe03ff032d92202946c7439')
 ck('Kind-excludes-conformance-realization-ownership-transfer',kp['forbidden_inferences']==['conformance','realization','ownership-transfer'])
 assignment=docs['classification-assignment_fixture'];ap=assignment['payload'];value=docs['classification-value_fixture'];scheme=docs['classification-scheme_fixture']
 joins={'scheme_ref_matches_selected_node':ap['scheme_version_ref']==scheme['node_id'],'value_ref_matches_selected_node':ap['value_ref']==value['node_id'],'value_ref_in_selected_scheme_list':ap['value_ref'] in scheme['payload']['value_refs'],'axis_literal_agrees':ap['axis_ref']==value['payload']['axis_ref'],'scheme_literal_agrees_with_value':ap['scheme_version_ref']==value['payload']['scheme_ref'],'subject_revision_resolved':False,'value_version_resolved':False}
 ck('literal-join-agreement-is-not-exact-record-resolution',joins=={'scheme_ref_matches_selected_node':False,'value_ref_matches_selected_node':False,'value_ref_in_selected_scheme_list':True,'axis_literal_agrees':True,'scheme_literal_agrees_with_value':True,'subject_revision_resolved':False,'value_version_resolved':False})
 relation=copy.deepcopy(docs['typed-relation_fixture']);relation['payload'].update(relation_kind_ref='relation.instance-of',source={'kind':'agent-instance','ref':ap['subject_ref'],'version_ref':ap['subject_version_ref']},target={'kind':'classification-value','ref':ap['value_ref'],'version_ref':ap['value_ref']+'@example-revision'},qualifiers={'binding_ref':assignment['node_id'],'parent_version_ref':ap['value_ref']+'@example-revision'})
 probes=[]
 def probe(id,change,expected):
  rec=copy.deepcopy(relation);change(rec);es=list(validators['typed-relation'].iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected observed current schema boundary '+id+' '+str([x.message for x in es]))
  probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'exact_reference_resolution_established':False,'semantic_class_established':False,'actual_relation_created':False,'whole_source_conformance_established':False})
 proposal={'classification_assignment_ref':assignment['node_id'],'scheme_version_ref':ap['scheme_version_ref'],'axis_ref':ap['axis_ref'],'class_or_parent_version_ref':relation['payload']['target']['version_ref']}
 probe('current-two-qualifier-instance-of-shape',lambda r:None,True)
 probe('proposal-four-alone-not-current-contract',lambda r:r['payload'].update(qualifiers=proposal),False)
 probe('adding-proposed-four-to-current-two-not-admitted-extension',lambda r:r['payload']['qualifiers'].update(proposal),False)
 probe('unresolved-binding-string-shape-accepted',lambda r:r['payload']['qualifiers'].update(binding_ref='absent:binding'),True)
 probe('different-subject-reference-shape-accepted',lambda r:r['payload']['source'].update(ref='other:subject',version_ref='other:subject@2'),True)
 probe('parent-qualifier-target-version-mismatch-shape-accepted',lambda r:r['payload']['qualifiers'].update(parent_version_ref='different-parent@2'),True)
 probe('unadmitted-ordered-pair-rejected',lambda r:r['payload']['source'].update(kind='agent-profile'),False)
 probe('reversed-classification-endpoint-pair-rejected',lambda r:r['payload'].update(source=copy.deepcopy(r['payload']['target']),target=copy.deepcopy(r['payload']['source'])),False)
 probe('runtime-authority-effect-rejected',lambda r:r.update(authority_effect='runtime-authority'),False)
 old=copy.deepcopy(relation);old['schema_version']='cyberalchemy-lab-typed-relation/v2';ck('same-selected-instance-of-two-qualifier-shape-valid-under-historical-v2',not list(historical_validator.iter_errors(old)))
 negative=[{'path':refs[n]['path'],'schema_rejected':bool(list(validators['typed-relation'].iter_errors(docs[n])))} for n in sorted(refs) if n.startswith('negative_')];ck('four-current-Typed-Relation-hostiles-rejected',len(negative)==4 and all(x['schema_rejected'] for x in negative))
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();bindings=[b.ref(p) for p in [b.UNIT/'verify_classification_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=json.loads((b.BASE/'definitions/cal.definition.classification-assignment/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-classification-profile/v1-candidate','status':'PASS-for-bounded-composition-profiles-and-current-historical-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'negative_fixture_checks':negative,'actual_join_observations':joins,'current_qualifier_axes':qual['required_axes'],'candidate_proposed_qualifier_axes':proposed,'current_endpoint_pairs':pairs,'actual_projection_reference_mapping_reviewed':False,'source_mapping_gaps':{'mapping_reviewed':False,'composed_act_result_assignment_carrier_embedding_pending':True,'question_identity_and_world_answer_correctness_reviewed':False,'semantic_class_only_projection_and_history_policy_reviewed':False,'two_vs_four_qualifier_extension_admitted':False,'whole_source_conformance_established':False},'new_classifications_assignments_actions_or_relations_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Bounded candidate composition/cardinality/semantic-class-only proposal profiles and selected actual current v3/historical v2 schema observations. Closed string references do not resolve actual subjects/values/bindings, establish class meaning or prove no-inference compliance. No carrier created, ontology relation, admission, execution, aligned meaning, world truth or whole-definition acceptance.'}
 if write:b.put('classification-profile-checks.json',report)
 elif not b.r.same_json(report,load('classification-profile-checks.json')):raise ValueError('Fresh profile differs')
 return report
def main():
 report=verify('--write' in b.sys.argv);print(json.dumps({k:report[k] for k in ['status','profile_control_count','rejected_profile_controls','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()

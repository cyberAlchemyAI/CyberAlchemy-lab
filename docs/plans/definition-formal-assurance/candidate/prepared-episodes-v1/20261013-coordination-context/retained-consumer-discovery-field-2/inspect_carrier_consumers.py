"""Exact carrier observations and fresh hypothetical comparisons; no accepted decoding map."""
from pathlib import Path
import ast,copy,json,sys
import build_candidate as b
import verify_candidate as a
import verifier as v
def load(path):return json.loads(path.read_bytes())
def pure(path,names,constants=()):
 tree=ast.parse(path.read_bytes());namespace={'json':json,'Any':object}
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id in constants for target in node.targets):
   for target in node.targets:
    if isinstance(target,ast.Name) and target.id in constants:namespace[target.id]=ast.literal_eval(node.value)
 nodes=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names];assert {node.name for node in nodes}==set(names);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace);return namespace
SELECTORS={
 'contextIdentity':('coordination_context_id / version','Stable identity and record revision need separate accepted maps.'),
 'contextProduct':('product_ref','Resolve exactly one Product; a scalar is a nomination.'),
 'contextPurpose':('purpose','Map purpose and stability; nonempty text is insufficient.'),
 'contextConsumers':('consumer_refs','Resolve consumers; schema minimum one is a carrier policy.'),
 'contextIntendedUses':('intended_uses','Interpret uses and suitability; schema minimum one is a carrier policy.'),
 'contextSubjectScope':('subject_scope','Map statement and exclusions to the governed scope.'),
 'contextSourcePolicies':('source_policy_refs','Resolve policies and distinguish nomination from enforcement.'),
 'contextBoundedContexts':('bounded_context_refs','Resolve explicit separately owned versions; an empty list is allowed.'),
 'contextOwner':('owner_ref / owner_route','Resolve nominated principal, role and bounded authority.'),
 'contextLifecycle':('v1 classification.lifecycle_posture_ref / v2 lifecycle_state','Historical posture and current lifecycle state are distinct proposed maps.'),
 'contextRevisionHistory':('revision_history','Authenticate history; an empty list is not proof of persistence.'),
 'contextChallengeRoute':('challenge_route','Resolve accountable handler and process.'),
 'contextProject':('project_ref','v1 permits omission; v2 requires explicit null for absence.'),
 'contextGoal':('goal_ref','Independent optional anchor with the same representation distinction.'),
 'boundedContextVersionOwner':('contexts/*/context.json owner_ref','Resolve exact referenced boundary versions before mapping their separate owners.'),
 'changeOriginalContext':('lifecycle fixture base','Select authentic before state; fixtures are examples.'),
 'changeDesiredProduct':('lifecycle fixture after.product_ref','Desired state must remain independent of successor nomination.'),
 'changeDesiredPurpose':('lifecycle fixture after.purpose','Materiality is not every unequal purpose string.'),
 'changeDesiredProject':('lifecycle fixture after.project_ref','Retain presence and reference identity separately.'),
 'changeDesiredGoal':('lifecycle fixture after.goal_ref','Retain presence and reference identity separately.'),
 'changeSuccessorContext':('after.coordination_context_id / predecessor_ref','Resolve distinct matching successor; the package compares anchors without a materiality parameter.'),
 'viewBeforeContext':(None,'Select an authenticated source-view before record without importing anchor-change meaning.'),
 'viewAfterContext':(None,'Select after record and retain durable identity independently of real view suitability.'),
 'viewBeforeSource':(None,'No direct source-view snapshot coordinate is selected from these carriers.'),
 'viewAfterSource':(None,'Policy-list changes and view changes require an explicit correspondence.')}
ISSUES=[
 'C18 Definition admission, C21 historical type admission and C67 current successor admission have separate effects; none accepts this translation or creates a context.',
 'C17 D66 and ContextPackage selections are scoped evidence uses, not imported hierarchy, package authority or predecessor equivalence.',
 'V1 optional Project and Goal fields may be absent; v2 requires explicit null. Both permit all four presence combinations. Presence and resolution remain separate.',
 'Consumer and intended-use arrays have carrier minimums; the source supplies no universal minimum. Empty collection adequacy needs an owner policy.',
 'Boundary references can be empty, but opaque nonempty strings do not prove exact version resolution or independently bound ownership.',
 'V1 non-collapse checks forbidden boundary fields; v2 additionally rejects printed identity and owner endpoint equality. Nominal sorted separation alone does not establish accepted common identity maps.',
 'A shared principal may own independent boundaries. The source does not require different owner identifiers, while v2 rejects an owner identifier equal to a framed endpoint identifier.',
 'Lifecycle strings, history arrays and nonempty owner or challenge references do not prove actual durability, operational ownership, history authenticity or accountable handling.',
 'The v2 lifecycle function treats every changed anchor as requiring succession and has no materiality parameter. The candidate preserves materiality as a separately interpreted source condition.',
 'Predecessor strings and a new identity do not authenticate original or desired state, create a successor, prove unique global lineage or establish reference equivalence.',
 'Source-policy revision fixtures are not a complete source-view model. Source-view snapshots and preservation need accepted maps and real evidence.',
 'Read-only extracted schema, projection, relation and lifecycle functions are subsets of package behavior; fixture and receipt writers are not executed.',
 'The Ontology Product coordination record is a v1 candidate with exact nominated boundary references and a generated projection; it supplies no operational admission or ownership proof.',
 'Proposed relation.frames and successor-of projections retain endpoint-extension residue and confer no Relation or Typed Relation admission.',
 'Finite T/I comparisons, schema acceptance and printed reference equality cannot accept denotations, source fidelity, shared interpretation or whole-definition proof.'
]
def inspect(write=False):
 root,unit=b.ROOT,b.UNIT;p=root/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261013-coordination-context';context=load(unit/'context.json');typed=load(unit/'types-logic-receipt.json');prior=load(b.BASE/'definitions/cal.definition.capability-realization-binding/delivery-manifest.json');runtime=v.f.current_bindings();frozen=typed['inputs']+typed['checker_bindings'];b.unchanged(frozen+context['sources']+prior['files']);b.external_current(context)
 terminal=load(p/'typed-stage-audit-command-result.json');assert terminal['exit_code']==0 and not(p/terminal['stderr']).read_bytes();selected={};checks=[]
 def select(path,label=None):
  value=b.ref(path);selected[label or value['path']]=value;return value
 def check(name,condition):
  if not condition:raise ValueError('Consumer check failed: '+name)
  checks.append({'check_id':name,'result':True})
 select(Path(__file__).resolve());select(p/'current-consumer-discovery.json');discovery=load(p/'current-consumer-discovery.json');discovery_refs=[{key:row[key] for key in ['path','sha256']} for row in discovery['matching_file_bindings']];b.unchanged(discovery_refs);check('discovery-79-files45-bindings',discovery['files_read']==79 and len(discovery_refs)==45 and not discovery['accepted_maps']);check('discovery-byte-counts',all(len((root/row['path']).read_bytes())==row['bytes'] for row in discovery['matching_file_bindings']))
 registry_path=root/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=load(registry_path);select(registry_path);current=[row for row in registry['admitted_contracts'] if row['artifact_type_ref'] in registry['current_by_identity'].values()];check('catalog-143-contracts121-current',len(registry['admitted_contracts'])==143 and len(current)==121)
 core=load(unit/'t.json')['payload'];complete=[];meanings=[]
 for row in current:
  ap,sp=root/row['artifact_path'],root/row['schema_path'];artifact=load(ap);ar,sr=select(ap),select(sp);check('current-catalog-'+row['artifact_type_ref'],ar['sha256']==row['artifact_sha256'] and sr['sha256']==row['schema_sha256'])
  versions=artifact.get('semantic_definition_refs',[]);old=artifact.get('definition_binding',{})
  if old.get('definition_id'):versions=versions+[old['definition_id']+'@'+old.get('version','')]
  if core['source']['version_ref'] in versions:complete.append(row['artifact_type_ref'])
 check('current-exact-CoordinationContext-binding',complete==['cal.artifact-type.coordination-context/v2'])
 shared_schema_path=root/'tooling/schemas/ctx01/v1/schema.json';shared=load(shared_schema_path);select(shared_schema_path);schema1=copy.deepcopy(shared);schema1['$ref']='#/$defs/coordinationContext'
 shared_generator_path=root/'tooling/generators/ctx01_artifact.py';select(shared_generator_path);g1=pure(shared_generator_path,['label','render_value','render_instance','render_artifact_type'],['CONFIG','COMMON_FIELDS']);select(root/'tooling/validators/ctx01_artifact_type.py');s1=pure(root/'tooling/validators/ctx01_artifact_type.py',['semantic_invariants'])
 versions={};fixtures={};validators={};semantic={};projections=[]
 for ver in ['v1','v2']:
  folder=root/'authority/artifact-types/coordination-context'/ver;artifact=load(folder/'artifact.json');schema=load(folder/'schema.json');select(folder/'artifact.json');select(folder/'schema.json');select(folder/'generator.py');select(folder/'validate.py');fixture_path=folder/artifact['validation_contract']['positive_witness'];fixture=load(fixture_path);select(fixture_path);b.c.Draft202012Validator.check_schema(schema1 if ver=='v1' else schema);validator=b.c.Draft202012Validator(schema1 if ver=='v1' else schema)
  row=next(row for row in registry['admitted_contracts'] if row['artifact_type_ref']==artifact['artifact_type_ref']);check(ver+'-historical-current-overlay',row['lifecycle_state']==('admitted-historical' if ver=='v1' else 'admitted-current') and artifact['status']==fixture['status']=='candidate-unadmitted')
  binding=artifact['definition_binding'] if ver=='v1' else artifact['semantic_definition_bindings'][0];check(ver+'-exact-Definition-binding',binding['sha256']==core['source']['sha256'] and binding['path']==core['source']['path'])
  if ver=='v1':
   check('v1-wrapper-exact-local-ref',schema['$ref']=='../../../../tooling/schemas/ctx01/v1/schema.json#/$defs/coordinationContext');render=lambda data:g1['render_instance'](data,'coordination-context');render_type=g1['render_artifact_type'];failure=lambda data:[name for name,ok,detail in s1['semantic_invariants']('coordination-context',data) if not ok]
   for label,binding in artifact['shared_mechanics'].items():check('v1-exact-shared-'+label,select(root/binding['path'])['sha256']==binding['sha256'])
  else:
   g2=pure(folder/'generator.py',['render_instance','render_artifact']);render=g2['render_instance'];render_type=g2['render_artifact'];s2=pure(folder/'validate.py',['semantic_failures','lifecycle_result','relation_projections']);failure=s2['semantic_failures']
  check(ver+'-positive-shape',not list(validator.iter_errors(fixture)));check(ver+'-positive-semantic-subset',not failure(fixture));before=copy.deepcopy(fixture)
  pp=folder/artifact['validation_contract']['positive_projection'];select(pp);select(folder/'ARTIFACT.md');check(ver+'-exact-two-projections',render(fixture)==render(fixture)==pp.read_text() and fixture==before);check(ver+'-exact-artifact-projection',render_type(artifact)==(folder/'ARTIFACT.md').read_text());check(ver+'-schema-generator-digests',artifact['schema_digest']==b.ref(folder/'schema.json')['sha256'] and artifact['source_direction']['generator_sha256']==b.ref(folder/'generator.py')['sha256'])
  for name in artifact['validation_contract'].get('positive_matrix',[artifact['validation_contract']['positive_witness']]):
   path=folder/name;data=load(path);select(path);check(ver+'-positive-matrix-'+path.stem,not list(validator.iter_errors(data)) and not failure(data))
  for name in artifact['validation_contract']['negative_witnesses']:
   path=folder/name;data=load(path);select(path);check(ver+'-hostile-'+path.stem,bool(list(validator.iter_errors(data))) or bool(failure(data)))
  versions[ver],fixtures[ver],validators[ver],semantic[ver]=artifact,fixture,validator,failure;projections.append({'version':ver,'projection':b.ref(pp),'pure_functions_only':True})
 for folder in ['0021-ctx01-artifact-type-promotion','0067-coordination-context-v2-successor-admission','0070-definition-complete-lab-model-admission']:
  path=root/'docs/decisions'/folder/'decision.json';decision=load(path);select(path);check(folder+'-positive-status',decision['status']=='owner-admitted')
  if 'authorization' in decision:auth=decision['authorization'];check(folder+'-exact-authorization',select(root/auth['path'])['sha256']==auth['sha256'])
  effects=decision.get('effects',decision.get('admission_result',{}));meanings.append({'decision_id':decision['decision_id'],'effects':effects,'excluded_effects':decision['excluded_effects']})
  if folder.startswith('0021'):check('C21-zero-context-instances-owners',effects['artifact_types_admitted']==7 and effects['context_instances_created']==effects['operational_owner_bindings_created']==0)
  if folder.startswith('0067'):check('C67-one-successor-zero-instances-endpoint-effects',effects['artifact_types_admitted']==effects['predecessors_transitioned_to_historical']==1 and effects['instances_admitted']==effects['relation_endpoint_pairs_admitted']==effects['consumer_activations']==0)
  if folder.startswith('0070'):check('C70-only-integrated-GovernedModel-instance',effects['governed_model_instances_admitted']==effects['ordinary_artifact_instances_admitted']==1 and 'No ordinary Artifact Type instance other than the exact integrated Governed Model instance is admitted.' in decision['excluded_effects'])
 probes=[]
 def probe(name,mutation,expected):
  for ver in ['v1','v2']:
   data=copy.deepcopy(fixtures[ver]);mutation(data);errors=list(validators[ver].iter_errors(data));failures=semantic[ver](data);accepted=not errors;check(ver+'-shape-probe-'+name,accepted==expected[0 if ver=='v1' else 1]);probes.append({'case_id':ver+'-'+name,'version':ver,'schema_accepted':accepted,'semantic_subset_failures':failures,'instance':data,'instance_sha256':b.ir.digest(data),'whole_package_executed':False,'accepted_map':False})
 probe('missing-Product',lambda x:x.pop('product_ref'),[False,False]);probe('multiple-Products',lambda x:x.update(product_ref=['a','b']),[False,False]);probe('zero-boundary-references',lambda x:x.update(bounded_context_refs=[]),[True,True])
 for field in ['project_ref','goal_ref']:
  probe('absent-'+field,lambda x,field=field:x.pop(field),[True,False]);probe('null-'+field,lambda x,field=field:x.update({field:None}),[True,True]);probe('multiple-'+field,lambda x,field=field:x.update({field:['a','b']}),[False,False]);probe('empty-'+field,lambda x,field=field:x.update({field:''}),[False,False])
 for field in ['consumer_refs','intended_uses']:probe('empty-'+field,lambda x,field=field:x.update({field:[]}),[False,False])
 for field in ['coordination_context_id','product_ref','purpose','owner_ref','challenge_route']:probe('empty-'+field,lambda x,field=field:x.update({field:''}),[False,False])
 for field in ['domain_model_ref','ubiquitous_language_ref','context_map_refs','accepted_semantic_map_ref','execution_permission_ref']:probe('unreviewed-field-'+field,lambda x,field=field:x.update({field:'invented'}),[False,False])
 for field in ['product_ref','project_ref','goal_ref']:
  probe('identity-equals-'+field,lambda x,field=field:x.update(coordination_context_id=x[field] if x[field] is not None else x['product_ref']),[True,True])
 probe('identity-equals-boundary',lambda x:x.update(coordination_context_id=x['bounded_context_refs'][0]),[True,True]);probe('owner-equals-Product',lambda x:x.update(owner_ref=x['product_ref']),[True,True])
 lifecycle_path=root/'authority/artifact-types/coordination-context/v2/fixtures/lifecycle/cases.json';lifecycle=load(lifecycle_path);select(lifecycle_path);lifecycle_results=[]
 for row in lifecycle['cases']:
  result=s2['lifecycle_result'](lifecycle['base'],row['after']);check('lifecycle-'+row['case_id'],result==row['expected']);lifecycle_results.append({'case_id':row['case_id'],'actual_result':result,'expected':row['expected'],'whole_package_executed':False})
 same=copy.deepcopy(lifecycle['base']);same['product_ref']='product:changed/v1';check('shape-alone-permits-inplace-anchor-change',not list(validators['v2'].iter_errors(same)));check('isolated-lifecycle-requires-successor',s2['lifecycle_result'](lifecycle['base'],same)=='successor-required')
 relations=s2['relation_projections'](fixtures['v2']);check('pure-relations-explicit-anchors-and-boundaries',len(relations)==1+int(fixtures['v2']['project_ref'] is not None)+int(fixtures['v2']['goal_ref'] is not None)+len(fixtures['v2']['bounded_context_refs']));check('relation-projections-do-not-mutate-input',fixtures['v2']==load(root/'authority/artifact-types/coordination-context/v2/fixtures/valid/product-project-goal.json'))
 ontology_path=root/'coordination/contexts/ontology-product/v1/coordination-context.json';ontology=load(ontology_path);select(ontology_path);select(ontology_path.with_name('generator.py'));select(ontology_path.with_name('validate.py'));select(ontology_path.with_name('COORDINATION-CONTEXT.md'));check('OntologyProduct-v1-candidate-shape',not list(validators['v1'].iter_errors(ontology)) and ontology['status']=='candidate-unadmitted' and ontology['authority_effect']=='none');check('OntologyProduct-generated-projection',g1['render_instance'](ontology,'coordination-context')==ontology_path.with_name('COORDINATION-CONTEXT.md').read_text())
 endpoints=[]
 for folder in ['contexts/governance/v3','contexts/ontology-lifecycle/v3']:
  path=root/folder/'context.json';data=load(path);select(path);endpoints.append({'path':b.ref(path),'context_id':data['context_id'],'version':data['version'],'owner_ref':data['owner_ref'],'accepted_reference_resolution':False})
 check('OntologyProduct-two-explicit-boundary-nominations',ontology['bounded_context_refs']==['cal.context.governance/v2','cal.context.ontology-lifecycle/v2'])
 definition=load(root/core['source']['path']);definition_schema=load(root/'authority/artifact-types/definition/v1/schema.json');definition_validator=b.c.Draft202012Validator(definition_schema);definition_probes=[]
 for field in ['definition_id','version','term','scope','voices','boundaries','source_refs','classification','claim_ceiling']:
  data=copy.deepcopy(definition);data.pop(field);accepted=not list(definition_validator.iter_errors(data));check('Definition-missing-'+field,accepted is False);definition_probes.append({'case_id':'missing-'+field,'schema_accepted':accepted})
 for selector in ['normative_statement','formal_expression']:
  data=copy.deepcopy(definition);data['voices']['scientific_formal'][selector]='Altered meaning with well-formed text.';accepted=not list(definition_validator.iter_errors(data));check('Definition-shape-does-not-enforce-'+selector,accepted is True);definition_probes.append({'case_id':'altered-'+selector,'schema_accepted':accepted})
 typed_ir=load(unit/'static-ir.json');ids={row['symbol_id']:b.ir.qualified(core['source'],core['scope'],row['symbol_id']) for row in core['declarations']};comparisons=[]
 names=['positive-fourteen-coordinates-optional-anchors-boundaries-material-changes-and-views','same-principal-can-own-independent-boundaries','second-Product-link','second-Project-link','second-Goal-link','missing-explicit-boundary-link','extra-boundary-link-outside-collection','missing-independent-boundary-ownership','source-view-change-mutates-coordination-identity','material-change-wrong-desired-successor','material-change-successor-collapses-identity','material-change-missing-successor-identity','material-flag-without-anchor-delta']+['material-inplace-successor-'+kind for kind in ['aProduct','aProject','aGoal','aPurpose']]+['materiality-flag-removed-'+kind for kind in ['aProduct','aProject','aGoal','aPurpose']]+['unselected-'+kind+'-reference-may-be-undeclared' for kind in ['Project','Goal']]+['missing-exact-binding-'+name for name in ['contextIdentity','contextOwner','contextLifecycle','contextRevisionHistory','contextPurpose','viewBeforeSource','viewAfterSource']]
 controls={row['case_id']:row for row in a.controls()}
 for name in names:
  row=controls[name];model=a.qualify(row['model'],ids);e=v.Denotation(typed_ir['declarations'],model);ts=[{'clause_id':clause['clause_id'],'truth':e.truth(clause['formal_statement'])} for clause in typed_ir['clauses'] if clause['disposition']=='encoded'];ps=[{'population_id':pop['population_id'],'truth':e.truth(pop['statement'])} for pop in typed_ir['populations'] if pop['requirement']=='required'];t,i=all(x['truth'] for x in ts),all(x['truth'] for x in ps);check('fresh-hypothetical-T-I-'+name,t==row['expected_T'] and (row['expected_I'] is None or i==row['expected_I']));comparisons.append({'case_id':name,'model':model,'model_sha256':b.ir.digest(model),'T':t,'I':i,'steps':e.steps,'clause_results':ts,'population_results':ps,'actual_carrier_decoded':False,'accepted_correspondence':False})
 expected={name for fields,carrier in b.GROUPS for name in fields};check('all25-source-coordinate-maps-accounted',set(SELECTORS)==expected and len(expected)==25);matrix=[{'symbol':name,'carrier_selector':selector,'rationale':reason,'status':'proposed-map' if selector else 'explicit-unresolved','accepted_map_ref':None} for name,(selector,reason) in SELECTORS.items()]
 findings=[{'finding_id':'COORD-CONSUMER-FINDING-'+str(i).zfill(3),'issue':issue,'status':'unresolved','accepted_map_refs':[],'owner_route':'role:definition-owner with coordination, boundary, identity, lifecycle, source-policy and relation owners'} for i,issue in enumerate(ISSUES,1)]
 b.unchanged(frozen+context['sources']+prior['files']+list(selected.values())+discovery_refs);b.external_current(context);check('201-current-sources',b.r.verify(b.snapshot(),root)['files']==201);check('runtime-unchanged',runtime==v.f.current_bindings())
 report={'schema_version':'CoordinationContext-consumer-inspection/v1-candidate','result':'PASS-exact-carrier-observations-and-hypothetical-T-I-comparisons','authority_effect':'none','source':core['source'],'selected_inputs':selected,'checks':checks,'check_count':len(checks),'complete_current_definition_binding_types':complete,'meaning_observations':meanings,'source_coordinate_correspondence':matrix,'source_coordinate_account_complete':True,'accepted_semantic_correspondence_complete':False,'definition_shape_probes':definition_probes,'carrier_shape_probes':probes,'lifecycle_results':lifecycle_results,'relation_projections':relations,'boundary_endpoint_observations':endpoints,'projection_observations':projections,'typed_comparison_models':comparisons,'unresolved_consumer_findings':findings,'accepted_semantic_map_refs':[],'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_Context_instance_effects_established':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'frozen_inputs_preserved':17,'frozen_checker_bindings_preserved':5,'prior_candidate_files_preserved':10389,'source_files_current':201,'runtime_bindings':runtime,'claim_ceiling':'Exact declared carrier and scoped-function behavior plus supplied finite hypothetical models; no accepted decoding map, actual context, operational ownership, permission, fidelity or whole proof.'}
 if write:b.put('carrier-consumer-inspection.json',report)
 else:assert b.r.same_json(report,load(unit/'carrier-consumer-inspection.json')),'Fresh consumer observations differ'
 return report
if __name__=='__main__':
 report=inspect('--write' in sys.argv);print(json.dumps({'result':report['result'],'checks':report['check_count'],'coordinate_maps':len(report['source_coordinate_correspondence']),'carrier_probes':len(report['carrier_shape_probes']),'typed_comparisons':len(report['typed_comparison_models']),'source_fidelity':'pending','semantic_ready':False},indent=2))

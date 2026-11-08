"""Bounded read-only CI carrier discovery, pure functions, and fixture probes."""
from pathlib import Path
import ast,copy,hashlib,json,subprocess,sys
root=Path.cwd();p=Path(__file__).resolve().parent
u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-instance'
sys.path.insert(0,str(u));import build_candidate as b
def load(path):return json.loads(path.read_bytes())
def ref(path):return {'path':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
checks=[]
def ck(name,ok):assert ok,name;checks.append({'check_id':name,'result':True})
registry_path=root/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
registry=load(registry_path);ck('143catalog121current',len(registry['admitted_contracts'])==143 and len(registry['current_by_identity'])==121)
for row in registry['admitted_contracts']:
 if row['artifact_type_ref'] not in registry['current_by_identity'].values():continue
 ck('current-contract-bytes-'+row['artifact_type_ref'],ref(root/row['artifact_path'])['sha256']==row['artifact_sha256'] and ref(root/row['schema_path'])['sha256']==row['schema_sha256'])
version='cal.definition.capability-instance@1.0.0-candidate.1'
summary=[row for row in registry['admitted_contracts'] if row['artifact_type_ref'] in registry['current_by_identity'].values() and version in row.get('semantic_definition_refs',[])]
complete=[]
for row in registry['admitted_contracts']:
 if row['artifact_type_ref'] not in registry['current_by_identity'].values():continue
 art=load(root/row['artifact_path'])
 ids=art.get('semantic_definition_refs',[])
 old=art.get('definition_binding',{})
 if old.get('definition_id'):ids=ids+[old['definition_id']+'@'+old.get('version','')]
 if version in ids:complete.append(row['artifact_type_ref'])
ck('one-currentCIv2-summary-and-complete-binding',len(summary)==1 and summary[0]['artifact_type_ref']=='cal.artifact-type.capability-instance/v2' and complete==['cal.artifact-type.capability-instance/v2'])
v1=root/'authority/artifact-types/capability-instance/v1'
v2=root/'authority/artifact-types/capability-instance/v2'
a1=load(v1/'artifact.json');a2=load(v2/'artifact.json');schema=load(v2/'schema.json');fixture=load(v2/'fixtures/valid/instance.json')
paths={'registry':registry_path,'historical_artifact':v1/'artifact.json','historical_schema':v1/'schema.json','current_artifact':v2/'artifact.json','current_schema':v2/'schema.json','current_artifact_projection':v2/'ARTIFACT.md','fixture':v2/'fixtures/valid/instance.json','fixture_projection':v2/'fixtures/valid/INSTANCE.md','source':root/b.source_ref(b.snapshot(),'cal.definition.capability-instance')['path'],'C70_decision':root/'docs/decisions/0070-definition-complete-lab-model-admission/decision.json','successor_generator':root/'tooling/generators/artifact_type_successor.py','ctx_generator':root/'tooling/generators/ctx01_artifact.py','successor_validator':root/'tooling/validators/artifact_type_successor.py','legacy_validator':root/'tooling/validators/ctx01_artifact_type.py','relation_model':root/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json','checker':Path(__file__).resolve()}
d70=load(paths['C70_decision']);paths['C70_authorization']=root/d70['authorization']['path']
refs={k:ref(v) for k,v in paths.items()}
ck('exact-C70-authorization',refs['C70_authorization']['sha256']==d70['authorization']['sha256'])
ck('C70positive-scoped-effects',d70['status']=='owner-admitted' and d70['effects']['artifact_types_admitted']==93 and d70['effects']['artifact_type_predecessors_to_historical']==9 and d70['effects']['typed_relation_instances_admitted']==d70['effects']['consumer_activations']==d70['effects']['runtime_activations']==0)
ck('candidate-body-versus-positive-overlay-preserved',a2['status']=='candidate-unadmitted' and a2['authority_effect']=='none' and summary[0]['lifecycle_state']=='admitted-current' and a1['status']=='candidate-unadmitted')
ck('exact-source-and-predecessor',a2['semantic_definition_bindings'][0]['sha256']==refs['source']['sha256']=='d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5' and a2['predecessor_contract']['sha256']==refs['historical_artifact']['sha256'])
b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema)
ck('closed-fixture-shape',not list(validator.iter_errors(fixture)))
def pure(path,names,constants=()):
 tree=ast.parse(path.read_bytes());nodes=[]
 for n in tree.body:
  if isinstance(n,ast.FunctionDef) and n.name in names:nodes.append(n)
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in constants for t in n.targets):nodes.append(n)
 namespace={'json':json,'Any':object};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace)
 return namespace
generator=pure(paths['successor_generator'],['render_artifact','render_instance'])
before=copy.deepcopy(fixture);one=generator['render_instance'](a2,fixture);two=generator['render_instance'](a2,fixture)
ck('two-exact-successor-projections',one==two==(v2/'fixtures/valid/INSTANCE.md').read_text() and before==fixture)
ck('exact-successor-artifact-projection',generator['render_artifact'](a2)==(v2/'ARTIFACT.md').read_text())
ctx=pure(paths['ctx_generator'],['label','render_value','render_instance'],['CONFIG','COMMON_FIELDS'])
oldfixture=load(v1/'fixtures/valid/instance.json')
ck('exact-historical-ctx-projection',ctx['render_instance'](oldfixture,'capability-instance')==(v1/'fixtures/valid/INSTANCE.md').read_text())
helper=pure(paths['legacy_validator'],['semantic_invariants'])['semantic_invariants']
rolehelper=pure(paths['successor_validator'],['roles_for','schema_is_closed'])
ck('exact-current-relation-surface',rolehelper['schema_is_closed'](schema) and rolehelper['roles_for']('capability-instance',load(paths['relation_model']))==a2['relation_roles'])
probes=[]
def probe(name,mutate,expected_schema,expected_legacy):
 doc=copy.deepcopy(fixture);mutate(doc);shape=not list(validator.iter_errors(doc));semantic=helper('capability-instance',doc);legacy=all(x[1] for x in semantic)
 ck('probe-'+name,shape==expected_schema and legacy==expected_legacy)
 probes.append({'case_id':name,'base':'immutable-current-fixture-copy','schema_accepted':shape,'legacy_helper_accepted':legacy,'legacy_helper_results':[{'check':x[0],'result':x[1]} for x in semantic],'current_bound_package_executed':False,'model':doc,'model_sha256':b.r.digest(doc)})
probe('same-parent-and-instance-claim-reference',lambda d:d.update(instance_authority_claim_ref=d['parent_authority_claim_ref']),True,False)
probe('instanceID-equals-parent-version-reference',lambda d:d.update(capability_instance_id=d['capability_version_ref']),True,False)
probe('opaque-unresolved-parent-owner-and-decision',lambda d:d.update(capability_version_ref='unresolved:parent',owner_ref='unresolved:owner',adoption_decision_ref='unresolved:decision'),True,True)
probe('budget-kind-without-budget',lambda d:d['recursion_stop'].pop('budget'),True,True)
probe('budget-kind-null-budget',lambda d:d['recursion_stop'].update(budget=None),True,True)
probe('budget-zero-rejected',lambda d:d['recursion_stop'].update(budget=0),False,True)
probe('budget-negative-rejected',lambda d:d['recursion_stop'].update(budget=-1),False,True)
probe('empty-stop-condition-rejected',lambda d:d['recursion_stop'].update(condition=''),False,True)
probe('owner-stop-without-budget',lambda d:d.update(recursion_stop={'kind':'owner-stop','condition':'owner may stop'}),True,True)
probe('terminal-condition-without-budget',lambda d:d.update(recursion_stop={'kind':'terminal-condition','condition':'terminal handoff'}),True,True)
probe('budget-and-stop-condition-coexist',lambda d:None,True,True)
probe('empty-semantic-context-collection-rejected',lambda d:d.update(bounded_context_refs=[]),False,True)
probe('empty-conformance-evidence-list-permitted',lambda d:d.update(conformance_refs=[]),True,True)
probe('direct-lifecycle-field-rejected',lambda d:d.update(lifecycle='active'),False,True)
probe('status-active-rejected',lambda d:d.update(status='active'),False,True)
probe('opaque-claim-ceiling-activation-overclaim-shape-valid',lambda d:d.update(claim_ceiling='Already adopted,activated andauthorized.'),True,True)
probe('classification-v2-instead-of-inherited-v1-rejected',lambda d:d['classification'].update(artifact_type_ref='cal.artifact-type.capability-instance/v2'),False,True)
roots=[x for x in ['coordination','product','contexts','craft/impl','implementation','evidence'] if (root/x).is_dir()]
scan=subprocess.run(['rg','-l','cyberalchemy-lab-capability-instance/v[12]',*roots,'--glob','*.json','--glob','!**/node_modules/**','--glob','!**/target/**'],cwd=root,capture_output=True,text=True)
ck('bounded-operational-tree-scan',scan.returncode in [0,1] and not scan.stderr)
matching=scan.stdout.splitlines();owned=[]
for name in matching:
 doc=load(root/name)
 if isinstance(doc,dict) and doc.get('schema_version') in ['cyberalchemy-lab-capability-instance/v1','cyberalchemy-lab-capability-instance/v2']:owned.append(ref(root/name))
ck('no-top-level-CI-record-in-selected-trees',not owned)
observed_props=schema['$defs']['capabilityInstance']['allOf'][1]['properties']
ck('lifecycle-source-coordinate-not-direct-carrier-field','lifecycle' not in observed_props and 'owner_ref' in observed_props)
report={'schema_version':'CapabilityInstance-consumer-discovery/v1-candidate','checks':checks,'actual_check_count':len(checks),'selected_inputs':refs,'source':b.source_ref(b.snapshot(),'cal.definition.capability-instance'),'direct_summary_bindings':[row['artifact_type_ref'] for row in summary],'complete_artifact_bindings':complete,'positive_C70_effects':d70['effects'],'historical_v1_binding_preserved':True,'body_candidate_posture_preserved':True,'carrier_fixture_probes':probes,'current_schema_top_level_property_names':list(observed_props),'source_lifecycle_direct_field_present':False,'classification_type_ref_in_fixture':fixture['classification']['artifact_type_ref'],'legacy_helper_is_current_bound_package':False,'successor_bound_package_validator_executed':False,'pure_renderers_and_legacy_helper_only':True,'live_or_native_consumer_executed':False,'schema_shape_is_semantic_fidelity':False,'scan':{'selected_roots':roots,'matching_documents_including_nested_refs_or_schemas':len(matching),'top_level_CI_records':owned,'complete_repo_or_private_scan':False},'accepted_map_refs':[],'actual_instance_adoption_conformance_or_authority_established':False,'full_consumer_mapping_complete':False,'source_fidelity':'pending','semantic_ready':False,'authority_effect':'none','goal_status':'active','claim_ceiling':'Bounded catalog/shape/projection/source/helper observations. No package validator/writer orliveinstance;legacyhelper distinct fromcurrent successorvalidator;frozen theory andacceptedsource/carriermaps remainseparate.'}
b.unchanged(list(refs.values()))
with (p/'consumer-discovery.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'result':'PASS-bounded-CI-carrier-discovery','checks':len(checks),'fixture_probes':len(probes),'current_binding':complete,'selected_operational_top_level_records':len(owned),'source_lifecycle_direct_field_present':False,'full_consumer_mapping_complete':False,'semantic_ready':False},indent=2))


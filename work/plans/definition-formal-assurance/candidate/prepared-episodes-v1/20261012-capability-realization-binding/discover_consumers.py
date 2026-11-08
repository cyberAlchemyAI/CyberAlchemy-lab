"""Bounded CRB carrier discovery and exact pure current non-collapse expression probes."""
from pathlib import Path
import ast,copy,json,sys
root=Path.cwd();prepared=Path(__file__).resolve().parent;unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding';sys.path.insert(0,str(unit));import build_candidate as b
def load(path):return json.loads(path.read_bytes())
checks=[]
def ck(name,ok):assert ok,name;checks.append({'check_id':name,'result':True})
receipt=load(unit/'types-logic-receipt.json');b.unchanged(receipt['inputs']+receipt['checker_bindings']);audit=load(prepared/'typed-stage-audit-command-result.json');ck('actual-typed-audit0',audit['exit_code']==0 and not(prepared/audit['stderr']).read_bytes())
registry_path=root/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=load(registry_path);current=registry['current_by_identity'].values();version='cal.definition.capability-realization-binding@1.0.0-candidate.1';complete=[]
ck('143contracts121current',len(registry['admitted_contracts'])==143 and len(current)==121)
for row in registry['admitted_contracts']:
 if row['artifact_type_ref'] not in current:continue
 ck('current-bytes-'+row['artifact_type_ref'],b.ref(root/row['artifact_path'])['sha256']==row['artifact_sha256'] and b.ref(root/row['schema_path'])['sha256']==row['schema_sha256'])
 artifact=load(root/row['artifact_path']);old=artifact.get('definition_binding',{});versions=artifact.get('semantic_definition_refs',[])
 if old.get('definition_id'):versions=versions+[old['definition_id']+'@'+old.get('version','')]
 if version in versions:complete.append(row['artifact_type_ref'])
ck('one-complete-current-v2-binding',complete==['cal.artifact-type.capability-realization-binding/v2'])
v1=root/'authority/artifact-types/capability-realization-binding/v1';v2=root/'authority/artifact-types/capability-realization-binding/v2';a1=load(v1/'artifact.json');a2=load(v2/'artifact.json');schema=load(v2/'schema.json');fixture=load(v2/a2['validation_contract']['positive_witness']);validator=b.c.Draft202012Validator(schema);b.c.Draft202012Validator.check_schema(schema)
paths={'registry':registry_path,'historical_artifact':v1/'artifact.json','historical_schema':v1/'schema.json','current_artifact':v2/'artifact.json','current_schema':v2/'schema.json','fixture':v2/a2['validation_contract']['positive_witness'],'artifact_projection':v2/'ARTIFACT.md','fixture_projection':v2/a2['validation_contract']['positive_projection'],'current_generator':v2/'generator.py','current_validator':v2/'validate.py','C70_decision':root/'docs/decisions/0070-definition-complete-lab-model-admission/decision.json','C60_decision':root/'docs/decisions/0060-capability-realization-binding-v1-admission/decision.json','checker':Path(__file__).resolve()}
refs={k:b.ref(path) for k,path in paths.items()}
ck('closed-positive-fixture',schema['additionalProperties'] is False and not list(validator.iter_errors(fixture)))
ck('exact-source-predecessor',a2['semantic_definition_bindings'][0]['sha256']==b.source_ref(b.snapshot(),'cal.definition.capability-realization-binding')['sha256'] and a2['predecessor_contract']['sha256']==refs['historical_artifact']['sha256'])
rows={r['artifact_type_ref']:r for r in registry['admitted_contracts']}
ck('C60historical-v1-C70current-v2',rows[a1['artifact_type_ref']]['lifecycle_state']=='admitted-historical' and rows[a2['artifact_type_ref']]['lifecycle_state']=='admitted-current' and rows[a1['artifact_type_ref']]['admission_decision_ref']=='CAL-DECISION-0060-CAPABILITY-REALIZATION-BINDING-V1-ADMISSION')
ck('historical-v1-broader-ProductCapability-binding',a1['semantic_definition_refs']==['cal.definition.product-capability@1.0.0-candidate.1'] and a2['semantic_definition_refs']==[version])
ck('candidate-body-fixture-no-effect',a1['status']==a2['status']==fixture['status']=='candidate-unadmitted' and a2['authority_effect']==fixture['authority_effect']=='none')
d70=load(paths['C70_decision']);auth=root/d70['authorization']['path'];refs['C70_authorization']=b.ref(auth)
ck('C70exact-scope-auth',d70['status']=='owner-admitted' and refs['C70_authorization']['sha256']==d70['authorization']['sha256'] and d70['effects']['artifact_types_admitted']==93 and d70['effects']['consumer_activations']==d70['effects']['runtime_activations']==0 and 'No ordinary Artifact Type instance other than the exact integrated Governed Model instance is admitted.' in d70['excluded_effects'])
nodes=[n for n in ast.parse(paths['current_generator'].read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name in ['render_artifact','render_instance']];ns={'json':json};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['current_generator']),'exec'),ns)
before=copy.deepcopy(fixture);render1=ns['render_instance'](a2,fixture);render2=ns['render_instance'](a2,fixture);ck('two-pure-fixture-projections',render1==render2==paths['fixture_projection'].read_text() and before==fixture);ck('exact-pure-artifact-projection',ns['render_artifact'](a2)==paths['artifact_projection'].read_text());ck('exact-bound-schema-and-generator',a2['schema_digest']==refs['current_schema']['sha256'] and a2['source_direction']['generator_sha256']==refs['current_generator']['sha256'])
# Extract exactly the current package's endpoint expression and check, excluding writers/main.
main=next(n for n in ast.parse(paths['current_validator'].read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='main');selected=[]
for n in main.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='endpoint_results' for t in n.targets):selected.append(n)
 if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and n.value.args and isinstance(n.value.args[0],ast.Constant) and n.value.args[0].value=='binding-capability-realization-non-collapse':selected.append(n)
ck('exact-current-noncollapse-expression-selected',len(selected)==2)
expression=compile(ast.Module(body=selected,type_ignores=[]),str(paths['current_validator']),'exec')
def helper(doc):
 observed=[];namespace={'artifact':a2,'witness':doc,'check':lambda name,ok,detail:observed.append({'check_id':name,'result':ok,'detail':detail})};exec(expression,namespace);assert len(observed)==1;return observed[0]
probes=[]
def probe(name,mutation,expected_shape,expected_guard=True):
 doc=copy.deepcopy(fixture);mutation(doc);before=copy.deepcopy(doc);errors=sorted(e.message for e in validator.iter_errors(doc));guard=helper(doc);ck('probe-'+name,(not errors)==expected_shape and guard['result']==expected_guard and doc==before)
 probes.append({'case_id':name,'schema_accepted':not errors,'schema_errors':errors,'current_extracted_noncollapse_guard':guard,'current_whole_package_executed':False,'model':doc,'model_sha256':b.ir.digest(doc),'accepted_semantic_map':False})
probe('exact-workflow-fixture',lambda x:None,True)
probe('bindingID-equals-Capability-reference',lambda x:x.update(node_id=x['capability_ref']),True,False)
probe('bindingID-equals-Capability-version-reference',lambda x:x.update(node_id=x['capability_version_ref']),True,False)
probe('realization-reference-equals-Binding',lambda x:x['realization_refs'][0].update(realization_ref=x['node_id']),True,False)
probe('realization-reference-equals-Capability-version',lambda x:x['realization_refs'][0].update(realization_ref=x['capability_version_ref']),True,False)
probe('empty-realization-collection',lambda x:x.update(realization_refs=[]),False)
probe('duplicate-realization-records',lambda x:x['realization_refs'].append(copy.deepcopy(x['realization_refs'][0])),True)
for kind in ['capability-instance','agent-capability','implementation','service','workflow']:probe('realization-kind-'+kind,lambda x,kind=kind:x['realization_refs'][0].update(realization_kind=kind),True)
probe('no-explicit-Implementation-revision',lambda x:x['realization_refs'][0].update(realization_ref='opaque:workflow',realization_kind='workflow'),True)
probe('unknown-direct-Implementation-version-field',lambda x:x['realization_refs'][0].update(implementation_version_ref='hyp:implementation@1'),False)
probe('opaque-unresolved-owner-and-endpoints',lambda x:x.update(owner_ref='unresolved:owner',capability_version_ref='unresolved:capability@revision'),True)
probe('candidate-null-adoption-empty-conformance',lambda x:x.update(adoption_decision_ref=None,conformance_refs=[]),True)
probe('adopted-without-decision-or-conformance',lambda x:x.update(binding_state='adopted'),False)
probe('adopted-with-opaque-decision-and-conformance',lambda x:x.update(binding_state='adopted',adoption_decision_ref='unresolved:decision',conformance_refs=['unresolved:conformance']),True)
probe('superseded-without-successor',lambda x:x.update(binding_state='superseded'),False)
probe('superseded-with-self-successor',lambda x:x.update(binding_state='superseded',successor_refs=[x['node_id']]),True)
probe('endpoint-change-same-node-and-version',lambda x:x['realization_refs'][0].update(realization_ref='hyp:changed-realization'),True)
probe('posture-change-same-node-and-version',lambda x:x.update(binding_state='retired'),True)
probe('unknown-canonical-authority-field',lambda x:x.update(canonical_relation_authority_ref='hyp:authority'),False)
probe('unknown-readonly-digest-projection-field',lambda x:x.update(typed_relation_projection={'digest':'hyp:digest','readonly':True}),False)
probe('direct-four-purpose-evidence-fields-rejected',lambda x:x.update(adoption_evidence_refs=[],deployment_evidence_refs=[],outcome_evidence_refs=[]),False)
probe('self-granted-authority-effect',lambda x:x.update(authority_effect='activate'),False)
for rel in a2['validation_contract']['negative_witnesses']:
 path=v2/rel;refs['negative-'+rel]=b.ref(path);ck('negative-fixture-'+rel,bool(list(validator.iter_errors(load(path)))))
ck('carrier-lacks-explicit-authority-projection-and-purpose-fields',all(name not in schema['properties'] for name in ['canonical_relation_authority_ref','typed_relation_projection','adoption_evidence_refs','deployment_evidence_refs','outcome_evidence_refs']))
b.unchanged(receipt['inputs']+receipt['checker_bindings']+list(refs.values()))
report={'schema_version':'CRB-bounded-consumer-discovery/v1-candidate','checks':checks,'actual_check_count':len(checks),'selected_inputs':refs,'complete_current_binding_types':complete,'historical_v1_primary_meaning':a1['semantic_definition_refs'],'current_v2_primary_meaning':a2['semantic_definition_refs'],'positive_C70_effects':d70['effects'],'source_endpoint_requirement':'one exact Capability revision andone-or-more exact Implementation revisions','fixture_endpoint_kinds':[x['realization_kind'] for x in fixture['realization_refs']],'current_schema_realization_kinds':schema['properties']['realization_refs']['items']['properties']['realization_kind']['enum'],'schema_probes':probes,'schema_probe_count':len(probes),'schema_acceptances':sum(x['schema_accepted'] for x in probes),'current_package_expression_extracted_read_only':True,'current_whole_package_validator_executed':False,'projection_or_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_Binding_adoption_deployment_conformance_operation_or_authority_created':False,'accepted_map_refs':[],'full_consumer_mapping_complete':False,'source_fidelity':'pending','semantic_ready':False,'authority_effect':'none','goal_status':'active','claim_ceiling':'Exact catalog/schema/fixture/projection and isolated current package expression observations only. Broad realization kinds need explicit Implementation-revision maps; no accepted authority,projection,evidence-purpose orsuccession correspondence.'}
with (prepared/'consumer-discovery.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'result':'PASS-bounded-CRB-consumer-discovery','checks':len(checks),'probes':len(probes),'schema_acceptances':report['schema_acceptances'],'full_consumer_mapping_complete':False,'semantic_ready':False},indent=2))

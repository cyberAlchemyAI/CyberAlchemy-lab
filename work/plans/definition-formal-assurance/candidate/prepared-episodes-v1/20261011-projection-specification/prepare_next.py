"""Prepare only exact Representation Revision source; no next theory before PS audit."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.projection-specification');d=u/'next-unit-preparation';d.mkdir()
s='''from pathlib import Path
import sys,json,ast,copy
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent));import build_candidate as b
snap=b.snapshot();assert b.r.verify(snap,b.ROOT)['files']==201;source=b.source_ref(snap,'cal.definition.representation-revision');doc=b.co.source_document(snap,source)
decision_path=b.ROOT/'docs/decisions/0028-craft-foundation-v1/decision.json';decision=json.loads(decision_path.read_bytes());auth_path=decision_path.with_name('authorization.json');auth=json.loads(auth_path.read_bytes());manifest_path=b.ROOT/auth['manifest']['path'];manifest=json.loads(manifest_path.read_bytes())
paths={'source':b.ROOT/source['path'],'projection':(b.ROOT/source['path']).with_name('DEFINITION.md'),'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','current_snapshot':b.BASE/'current-snapshot.json','checker':P/'inspect_source.py','C28_decision':decision_path,'C28_authorization':auth_path,'C28_manifest':manifest_path,'C28_validation':b.ROOT/auth['validation_receipt']['path']}
refs={k:b.ref(q) for k,q in paths.items()};checks=[]
def ck(n,ok):
 assert ok,n;checks.append({'check_id':n,'result':True})
row=next(x for x in snap['current_entries'] if x['definition_id']==source['definition_id']);ck('exact-current-source',source['version_ref']=='cal.definition.representation-revision@1.0.0-candidate.1' and source['sha256']==refs['source']['sha256']=='5bb818e70b0281dc14edcd4dade418335f50df93bc30c607823ecce5b3349850')
ck('C28-current-overlay',row['effective_state']=='admitted-current' and row['admission_decision_ref']==decision['decision_id']=='CAL-DECISION-0028-CRAFT-FOUNDATION-V1' and decision['status']=='owner-admitted')
ck('original-scope',len(snap['current_entries'])==183 and len(snap['current_entries'])+len(snap['historical_entries'])==189 and len(snap['captured_files'])==201)
ck('C28-exact-selected-definition',any(x['definition_id']==source['definition_id'] and x['path']==source['path'] and x['sha256']==source['sha256'] for x in decision['admitted_definitions']))
ck('C28-exact-manifest',refs['C28_manifest']['sha256']==auth['manifest']['sha256']==decision['selection']['manifest_sha256'])
ck('C28-exact-validation-bytes',refs['C28_validation']['sha256']==auth['validation_receipt']['sha256']==decision['selection']['validation_receipt_sha256'])
ck('C28-authorization-token',auth['status']=='exact-owner-authorized' and auth['selection_token']==decision['selection']['selection_token'])
ck('C28-no-implementation-binding',decision['admission_result']['implementation_bindings_accepted']==0)
schema=json.loads(paths['Definition_schema'].read_bytes());ck('Definition-schema-binding',doc['schema_digest']==refs['Definition_schema']['sha256']);ck('Definition-generator-binding',doc['source_direction']['generator_sha256']==refs['Definition_generator']['sha256']);ck('Definition-shape',not list(b.c.Draft202012Validator(schema).iter_errors(doc)))
nodes=[x for x in ast.parse(paths['Definition_generator'].read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in ['esc','bullets','render']];ck('pure-functions-only',len(nodes)==3);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['Definition_generator']),'exec'),ns);before=copy.deepcopy(doc);one=ns['render'](doc).encode();two=ns['render'](doc).encode();ck('two-exact-projections-and-no-mutation',one==two==paths['projection'].read_bytes() and before==doc)
f=doc['voices']['scientific_formal'];expr=f['formal_expression'];norm=f['normative_statement'];ck('immutable-preserved-meaning-genus',all(x in norm for x in ['new immutable machine-canonical encoding','existing Semantic Epoch','normative meaning and semantic identity are preserved']))
ck('representation-change-dimensions',all(x in norm for x in ['schema binding','artifact-type representation contract','canonical field layout','encoding changes']))
ck('exact-record-binding-components',all(x in norm for x in ['predecessor and postimage digests','representation revision identity','representation delta','equivalence evidence','validation','owner selection','rollback']))
ck('formal-equal-identity-epoch-meaning',all(x in expr for x in ['SemanticIdentity(a0)=SemanticIdentity(a1)','SemanticEpoch(a0)=SemanticEpoch(a1)','NormativeMeaning(a0)=NormativeMeaning(a1)']))
ck('formal-unequal-bytes-exact-endpoints',all(x in expr for x in ['CanonicalBytes(a0)!=CanonicalBytes(a1)','ExactPrePost(r,a0,a1)']))
ck('no-semantic-successor-or-context-lineage', 'does not create semantic-successor lineage' in norm and 'Context lineage is not created for representation-only change.' in f['boundary_conditions'])
ck('explicit-evidence-owner-and-immutable-predecessor',all(x in f['boundary_conditions'] for x in ['Meaning preservation requires explicit evidence and owner selection.','The predecessor remains immutable historical evidence.','A representation revision cannot be used when semantic meaning changed.']))
ck('three-notations-four-boundaries-four-tests',len(f['notation'])==3 and len(f['boundary_conditions'])==4 and len(f['testable_conditions'])==4)
ck('nonexecuting-body-ceiling','does not reclassify, replace, mutate, or admit any CTX08 artifact' in doc['claim_ceiling'])
observations=[]
for i,x in enumerate(doc['source_refs']):
 row=next(z for z in snap['current_entries']+snap['historical_entries'] if z['version_ref']==x['source_ref']);r={k:row[k] for k in ['definition_id','version_ref','path','sha256']};q=b.ROOT/r['path'];paths['upstream-'+str(i)]=q;refs['upstream-'+str(i)]=b.ref(q);observations.append({'embedded_source_ref':x,'current_or_historical_exact_ref':r,'accepted_semantic_map':False});assert r['sha256']==x['content_sha256']==refs['upstream-'+str(i)]['sha256']
ck('two-exact-local-upstream-sources',len(observations)==2 and {x['embedded_source_ref']['source_ref'] for x in observations}=={'cal.definition.definition@1.0.0-candidate.1','cal.definition.bounded-context@2.0.0-candidate.1'})
ck('next-native-absent',not (b.BASE/'definitions/cal.definition.representation-revision').exists());b.unchanged(list(refs.values()));ck('all-source-inputs-still-current',b.r.verify(snap,b.ROOT)['files']==201)
assert len(checks)==25
report={'schema_version':'definition-assurance-next-source-inspection/v1-candidate','authority_effect':'none','source':source,'source_units':len(b.co.inventory(doc)),'checks':checks,'selected_inputs':refs,'upstream_observations':observations,'projection_bytes':len(one),'projection_sha256':b.r.digest(one),'external_file_refs':[],'requires_ProjectionSpecification_full_delivery_audit_first':True,'actual_next_unit_created':False,'interpretation_or_models_created':False,'native_or_live_consumer_executed':False,'semantic_ready':False,'mechanized_proof':False}
with (P/'source-inspection.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\\n')
print(json.dumps({'result':'PASS-next-RepresentationRevision-source-only','checks':len(checks),'source_units':report['source_units'],'projection_bytes':len(one),'local_upstreams':len(observations),'source_sha256':source['sha256'],'actual_next_unit_created':False},indent=2))
'''
ast.parse(s)
with (d/'inspect_source.py').open('x') as f:f.write(s)
s=(p.with_name('20261011-generated-output')/'capture_next_source.py').read_text().replace('cal.definition.generated-output','cal.definition.projection-specification')
with (p/'capture_next_source.py').open('x') as f:f.write(s)
print('Prepared exact C28 Representation Revision source-only producer.')

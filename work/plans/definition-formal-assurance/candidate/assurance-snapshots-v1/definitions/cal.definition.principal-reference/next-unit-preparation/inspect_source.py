"""Exact C53 Constraint Cycle Safety source-only preparation; no next T or edge effect."""
from pathlib import Path
import sys,json,ast,copy
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent));import build_candidate as b
snap=b.snapshot();source=b.source_ref(snap,'cal.definition.constraint-cycle-safety-invariant');doc=b.co.source_document(snap,source);row=next(x for x in snap['current_entries'] if x['definition_id']==source['definition_id'])
paths={'source':b.ROOT/source['path'],'projection':(b.ROOT/source['path']).with_name('DEFINITION.md'),'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','current_snapshot':b.BASE/'current-snapshot.json','checker':P/'inspect_source.py'}
refs={k:b.ref(v) for k,v in paths.items()};checks=[]
def ck(n,ok):assert ok,n;checks.append({'check_id':n,'result':True})
ck('exact-current-C53-source',source['sha256']==refs['source']['sha256']=='bf829b78c06764c34db536edd838cce4683716935ca0ec5bd9742f8d66e573fb' and row['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and row['effective_state']=='admitted-current')
ck('original183189201scope',len(snap['current_entries'])==183 and len(snap['historical_entries'])==6 and b.r.verify(snap,b.ROOT)['files']==201)
ck('Definition-schema-binding',doc['schema_digest']==refs['Definition_schema']['sha256'])
ck('Definition-generator-binding',doc['source_direction']['generator_sha256']==refs['Definition_generator']['sha256'])
ck('Definition-shape',not list(b.c.Draft202012Validator(json.loads(paths['Definition_schema'].read_bytes())).iter_errors(doc)))
nodes=[x for x in ast.parse(paths['Definition_generator'].read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in ['esc','bullets','render']];ck('three-pure-functions-only',len(nodes)==3)
ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['Definition_generator']),'exec'),ns);before=copy.deepcopy(doc);one=ns['render'](doc).encode();two=ns['render'](doc).encode();ck('two-exact-projections-no-mutation',one==two==paths['projection'].read_bytes() and before==doc)
f=doc['voices']['scientific_formal'];norm=f['normative_statement'];formal=f['formal_expression']
ck('stable-normalized-identity-classification-preservation',all(x in norm for x in ['semantic.constraint-cycle-safety-invariant','scope.shared-authority','type.invariant','CAV2-D28','without silently merging']))
ck('value-and-cycle-watch-guard',all(x in norm for x in ['constrain the value, label, authority state, schema field','participate in a cycle','explicit acyclicity','stop at schema governance','contextuality-obstruction review']))
ck('explicit-exception-evidence-witness-residue',all(x in formal for x in ['value_constraining(E)','cycle_permitted(E)','unless a schema owner','source evidence','constraint semantics','satisfiability or obstruction review','validator or review','typed residue','watch condition, not a theorem']))
ck('non-value-cycles-and-acyclic-constraints-not-banned',all(x in f['boundary_conditions'][0] for x in ['not a contextuality theorem','not a spectral-presheaf','not a ban on cyclic non-value relations','not a ban on acyclic','does not promote any live vault edge family']))
ck('retained-scaffold-and-upstream-metadata-not-accepted-model',len(doc['source_refs'])==1 and doc['source_refs'][0]['source_ref']=='cyberalchemy-v2:CAV2-D28' and doc['source_refs'][0]['admission_posture']=='candidate-unadmitted' and doc['source_refs'][0]['source_admission_ref'] is None and doc['primary_consumer_refs']==[])
ck('scope-obstruction-witness-owner-review',all(x in doc['scope']['applicability'] for x in ['force a value or state','form cycles','block the promotion','constraints could fail to glue','validator or reviewer','owner accepts']))
ck('test-and-notation-source-retained',len(f['testable_conditions'])==4 and len(f['notation'])==2)
ck('retained-body-no-effect-ceiling','grants no implementation, migration, registry, publication, release, deployment, or external-effect authority' in doc['claim_ceiling'])
ck('next-native-absent',not (b.BASE/'definitions/cal.definition.constraint-cycle-safety-invariant').exists())
b.unchanged(list(refs.values()));ck('all-inputs-current',b.r.verify(snap,b.ROOT)['files']==201)
report={'schema_version':'definition-assurance-next-source-inspection/v1-candidate','authority_effect':'none','source':source,'source_units':len(b.co.inventory(doc)),'checks':checks,'selected_inputs':refs,'upstream_observations':[{'embedded_source_ref':doc['source_refs'][0],'upstream_bytes_read':False,'upstream_currentness':'pending-next-source-owner-evidence','source_admission_or_model_inferred':False}],'consumer_observations':[],'projection_bytes':len(one),'projection_sha256':b.r.digest(one),'external_file_refs':[],'requires_PrincipalReference_full_delivery_audit_first':True,'actual_next_unit_created':False,'interpretation_or_models_created':False,'native_or_live_consumer_executed':False,'actual_edge_promotion_or_authority_created':False,'semantic_ready':False,'mechanized_proof':False}
if '--write' in sys.argv:
 with (P/'source-inspection.json').open('x') as out:json.dump(report,out,indent=2,sort_keys=True);out.write('\n')
else:assert b.r.same_json(report,json.loads((P/'source-inspection.json').read_bytes()))
print(json.dumps({'result':'PASS-next-ConstraintCycleSafety-source-only','checks':len(checks),'source_units':report['source_units'],'projection_bytes':len(one),'upstream_byte_currentness':'pending','actual_next_unit_created':False},indent=2))

